#import cProfile
import os
import sys
from pathlib import Path
import cogmap as cm
import impact_generator as ig
import report
from optimizer import Optimizer


#def main():
if __name__ == '__main__':
    # входные данные - файл когнитивная карта, файл групп вершин, число шагов импульсного моделирования
    if len(sys.argv) < 4:
        print("usage %s <input.cmj> <input.xyz_cmj> <pulse model steps>", sys.argv[0])
        exit(-1)

    cogmap_json_path = sys.argv[1]
    cogmap_xyz_json_path = sys.argv[2]
    N = int(sys.argv[3])

    optimizer = Optimizer()
    simple_structs = optimizer.get_simple_structs()
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
    res, data = optimizer.find_optimal_changes(base_cogmap, N, simple_structs, impactgen)
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
    print("Done")


#if __name__ == '__main__':
#    cProfile.run('main()')
