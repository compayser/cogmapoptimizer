"""
:file: Основная программа
Описание: Демонстратор возможностей библиотеки алгоритмов сильного ИИ в части 
оптимизации реальных сценариев производств и расширений имитационных моделей
"""
import os
import sys
import time
import shutil
from typing import List
from pathlib import Path
import uid
import zip as zip_module
import report
import cogmap as cm
import impact_generator as ig
from optimizer import Optimizer


def get_range_from_args(args):
    """
    Парсинг параметра командной строки со списком простых фигур для обработки и извлечение их 
    номеров в список
    :param args: аргумент коммандной строки со списком простых фигур (строка)
    :return: список с номерами фигур
    """
    res1 = args.split(",")
    res2 = []
    for _, item in enumerate(res1):
        range_in = item.split("-")
        if len(range_in) == 1:
            res2.append(int(range_in[0]))
        else:
            for idx2 in range(int(range_in[0]), int(range_in[1]) + 1):
                res2.append(idx2)
    return res2


# Точка входа main
if __name__ == "__main__":
    # Проверка версии Python
    version = sys.version_info[0:2]
    if version < (3, 8):
        print("Error: requires python version 3.8 or higher (instead of "
              f"{version[0]}.{version[1]})")
        sys.exit(-1)

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
              f"<cognitive_map.cmj> <vertices_group_file.xyz_cmj> "
              f"<pulse_model_steps> [simple_figures_list [-remote]]")
        print(f"Example: {sys.argv[0]} test_map.cmj test_map.xyz_cmj 10 0-2,4,6 -remote")
        sys.exit(-1)

    start_time = time.time()  # Начало работы программы

    # Аргументы командной строки (первые три)
    cogmap_json_path = sys.argv[1]
    cogmap_xyz_json_path = sys.argv[2]
    N = int(sys.argv[3])

    optimizer = Optimizer()
    simple_structs = optimizer.get_simple_structs()

    #  Аргументы командной строки (какие из простых фигур надо обработать)
    if len(sys.argv) >= 5:
        Range = get_range_from_args(sys.argv[4])
        Range = sorted(Range)
        if Range[0] < 0 or Range[len(Range)-1] > len(simple_structs)-1:
            Range: List[int] = []
            for ii in range(0, len(simple_structs)):
                Range.append(ii)
    else:
        Range: List[int] = []
        for ii in range(0, len(simple_structs)):
            Range.append(ii)

    remote_execution = False  # pylint: disable=C0103
    if len(sys.argv) == 6 and sys.argv[5].upper() == "-REMOTE":
        remote_execution = True  # pylint: disable=C0103

    impactgen = ig.ImpactGenerator()

    # Чтение конфигурации когнитивной карты и входных данных
    print("Loading config", end="")
    with open(cogmap_json_path, "r", encoding="cp1251") as config_file:
        cogmap_json = config_file.read()
    with open(cogmap_xyz_json_path, "r", encoding="cp1251") as config_xyz_file:
        cogmap_xyz_json = config_xyz_file.read()
    print(" - OK")
    base_cogmap = cm.CogMap()
    base_cogmap.fill_from_json(cogmap_json, cogmap_xyz_json)
    print("Analyzing", end="")
    res, data = optimizer.find_optimal_changes(base_cogmap, N, simple_structs, impactgen, Range)
    if res == -1:
        print("Problems not found")
        res = None  # pylint: disable=C0103
        data = None  # pylint: disable=C0103
    if res == 0:
        print("Solutions not found")
        res = None  # pylint: disable=C0103
        data = None  # pylint: disable=C0103

    local_uid = uid.get_uid()
    if not(res is None and data is None):
        i = 0
        print(f"Built {len(data)} composition(s)")
        print("Building reports", end="")
        p = Path(cogmap_json_path)
        for d in data:
            r = report.Report(d)
            # Папка для результатов
            result_dir = str(p.parent) + "\\Results"  # pylint: disable=C0103
            rd = Path(result_dir)
            if not rd.exists():
                rd.mkdir()
            # Сами результаты
            result_dir = f"{p.parent}\\Results\\added_{d.added_new_vertices}"  # pylint: disable=C0103
            rd = Path(result_dir)
            if not rd.exists():
                rd.mkdir()
            result_filename = f"{str(result_dir)}\\{p.name}.out{i}_{local_uid}.cmj"
            i = i + 1
            r.save_to_file(result_filename)
        print(" - OK")

    if remote_execution:
        arch_name = "archive-" + local_uid + ".zip"
        if not(res is None and data is None):
            # Есть результаты
            print("Compressing data", end="")
            zip_module.archive("Results", arch_name)  # Заархивировать результаты
            shutil.rmtree("Results", ignore_errors=True)  # Удалить папку с оригиналами результатов
            print(" - OK")
        else:
            # Нет результатов
            zip_module.create_empty(arch_name)  # Создать пустой архив
        with open("done.txt", "a", encoding="cp1251") as file:  # Выставить флаг "Работу завершил"
            file.write(f"{arch_name}")

    print(f"Job done (in {(time.time() - start_time):.1f} second(s))")  # Конец работы программы
