import os
import sys
import uid
import zip
import time
import report
import shutil
import cogmap as cm
import impact_generator as ig
from typing import List
from pathlib import Path
from optimizer import Optimizer


def GetRangeFromArgs(args):
    """
    Парсинг параметра командной строки со списком простых фигур для обработки и извлечение их номеров в список
    :param args: аргумент коммандной строки со списком простых фигур (строка)
    :return: список с номерами фигур
    """
    res1 = args.split(",")
    res2 = []
    for idx1 in range(len(res1)):
        rangeIn = res1[idx1].split("-")
        if len(rangeIn) == 1:
            res2.append(int(rangeIn[0]))
        else:
            for idx2 in range(int(rangeIn[0]), int(rangeIn[1])+1):
                res2.append(idx2)
    return res2


# Точка входа main
if __name__ == '__main__':
    # Проверка версии Python
    version = sys.version_info[0:2]
    if version < (3, 8):
        print(f"Error: requires python version 3.8 or higher (instead of {version[0]}.{version[1]})")
        exit(-1)

    # Удалить файла-флага завершения работы от прошлого запуска
    if os.path.isfile("done.txt") or os.path.islink("done.txt"):
        os.remove("done.txt")

    # Входные данные - файл когнитивной карты,
    #                  файл групп вершин,
    #                  число шагов импульсного моделирования,
    #                  список простых фигур для обработки,
    #                  признак запуска на удаленной машине
    if len(sys.argv) < 4:
        print(f"Usage: {sys.argv[0]} "
              f"<cognitive_map.cmj> <vertices_group_file.xyz_cmj> <pulse_model_steps> [simple_figures_list [-remote]]")
        print(f"Example: {sys.argv[0]} test_map.cmj test_map.xyz_cmj 10 0-2,4,6 -remote")
        exit(-1)

    start_time = time.time()  # Начало работы программы

    # Аргументы командной строки (первые три)
    cogmap_json_path = sys.argv[1]
    cogmap_xyz_json_path = sys.argv[2]
    N = int(sys.argv[3])

    optimizer = Optimizer()
    simple_structs = optimizer.get_simple_structs()

    #  Аргументы командной строки (какие из простых фигур надо обработать)
    if len(sys.argv) >= 5:
        Range = GetRangeFromArgs(sys.argv[4])
        Range = sorted(Range)
        if Range[0] < 0 or Range[len(Range)-1] > len(simple_structs)-1:
            Range: List[int] = []
            for ii in range(0, len(simple_structs)):
                Range.append(ii)
    else:
        Range: List[int] = []
        for ii in range(0, len(simple_structs)):
            Range.append(ii)

    remote_execution = False
    if len(sys.argv) == 6 and sys.argv[5].upper() == "-REMOTE":
        remote_execution = True

    impactgen = ig.ImpactGenerator()

    # Чтение конфигурации когнитивной карты и входных данных
    print(f"Loading config", end="")
    with open(cogmap_json_path, "r") as config_file:
        cogmap_json = config_file.read()
    with open(cogmap_xyz_json_path, "r") as config_xyz_file:
        cogmap_xyz_json = config_xyz_file.read()
    print(f" - OK")
    base_cogmap = cm.CogMap()
    base_cogmap.fill_from_json(cogmap_json, cogmap_xyz_json)
    print(f"Analyzing", end="")
    res, data = optimizer.find_optimal_changes(base_cogmap, N, simple_structs, impactgen, Range)
    if res == -1:
        print(f"Problems not found")
        res = None
        data = None
    if res == 0:
        print(f"Solutions not found")
        res = None
        data = None

    local_uid = uid.get_uid()
    if not(res is None and data is None):
        i = 0
        print(f"Built {len(data)} composition(s)")
        print(f"Building reports", end="")
        p = Path(cogmap_json_path)
        for d in data:
            r = report.Report(d)
            # Папка для результатов
            result_dir = str(p.parent) + "\\Results"
            rd = Path(result_dir)
            if not rd.exists():
                rd.mkdir()
            # Сами результаты
            result_dir = str(p.parent) + "\\Results\\added_%d" % d.added_new_vertices
            rd = Path(result_dir)
            if not rd.exists():
                rd.mkdir()
            result_filename = f"{str(result_dir)}\\{p.name}.out{i}_{local_uid}.cmj"
            i = i + 1
            r.save_to_file(result_filename)
        print(f" - OK")

    if remote_execution:
        arch_name = "archive-" + local_uid + ".zip"
        if not(res is None and data is None):
            # Есть результаты
            print(f"Compressing data", end="")
            # Заархивировать результаты
            zip.archive("Results", arch_name)
            # Удалить папку с оригиналами результатов
            shutil.rmtree("Results", ignore_errors=True)
            print(f" - OK")
        else:
            # Нет результатов
            zip.create_empty(arch_name)  # Создать пустой архив
        # Выставить флаг "Работу завершил"
        open("done.txt", "a").close()

    print(f"Job done (in {(time.time() - start_time):.1f} second(s))")  # Конец работы программы
