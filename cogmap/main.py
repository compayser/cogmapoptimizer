import sys
from pathlib import Path
import cogmap as cm
import impact_generator as ig
import report
from optimizer import Optimizer
import time
import proba
# from typing import List


def GetRangeFromArgs(args):
    res1 = args.split(",")
    res2 = []
    for ii in range(len(res1)):
        rangeIn = res1[ii].split("-")
        if len(rangeIn) == 1:
            res2.append(int(rangeIn[0]))
        else:
            for jj in range(int(rangeIn[0]), int(rangeIn[1])+1):
                res2.append(jj)
    print(f"{args} => {res2}")
    return res2


if __name__ == '__main__':
    # входные данные - файл когнитивная карта, файл групп вершин,
    #                  число шагов импульсного моделирования, [диапазон для простых фигур]
    if len(sys.argv) < 4:
        print("usage %s <input.cmj> <input.xyz_cmj> <pulse_model_steps> [simple_figures_range]", sys.argv[0])
        exit(-1)

    start_time = time.time()

    cogmap_json_path = sys.argv[1]
    cogmap_xyz_json_path = sys.argv[2]
    N = int(sys.argv[3])

    optimizer = Optimizer()
    simple_structs = optimizer.get_simple_structs()

    # диапазон обработки (какие из простых фигур надо обработать)
    if len(sys.argv) == 5:
        Range = GetRangeFromArgs(sys.argv[4])
        Range = sorted(Range)
        if Range[0] < 0 or Range[len(Range)-1] > len(simple_structs)-1:
            Range: list[int] = []
            for ii in range(0, len(simple_structs)):
                Range.append(ii)
    else:
        Range: list[int] = []
        for ii in range(0, len(simple_structs)):
            Range.append(ii)

    impactgen = ig.ImpactGenerator()

    # чтение конфигурации когнитивной карты и входных данных
    print("Loading config...")
    with open(cogmap_json_path, "r") as config_file:
        cogmap_json = config_file.read()
    with open(cogmap_xyz_json_path, "r") as config_xyz_file:
        cogmap_xyz_json = config_xyz_file.read()
    base_cogmap = cm.CogMap()
    base_cogmap.fill_from_json(cogmap_json, cogmap_xyz_json)
    print("Analyzing...")
    res, data = optimizer.find_optimal_changes(base_cogmap, N, simple_structs, impactgen, Range)
    if res == -1:
        print("Problems not found")
        exit(0)
    if res == 0:
        print("Solutions not found")
        exit(0)

    i = 0
    print("Built %d composition(s)" % len(data))
    print("Building reports...")
    p = Path(cogmap_json_path)

    for d in data:
        r = report.Report(d)
        result_dir = str(p.parent) + "\\added_%d" % d.added_new_vertices
        rd = Path(result_dir)
        if not rd.exists():
            rd.mkdir()
        result_filename = str(result_dir) + "\\" + p.name + ".out%d.cmj" % i
        i = i + 1
        r.save_to_file(result_filename)
    print(f"Done (in {(time.time() - start_time):.1f} second(s))")
