# CogMap #
Библиотека содержит набор классов, обеспечивающих выполнение адаптивной оптимизации с использованием 
когнитивного моделирования. 

# Пример использования #

Ниже приведен пример подключения и использования библиотеки CogMap Optimizer. 

```python
import sys
from pathlib import Path
import cogmap as cm
import impact_generator as ig
import report
from optimizer import Optimizer


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
```


# Файл cogmap.py #
## Класс Impulses ##
    Описывает серию импульсов (воздействий) на когнитивную карту

## Класс Vertex ##
    Описывает вершину когнитивной карты

## Класс Edge ##
    Оисывает ребро когнитивной карты

## Класс CogMap ##
    Описывает когнитивную карту
    __init__(self, vertices=[], edges=[]):
        Конструктор
        vertices - массив вершин
        edged - массив ребер

    is_stable(self)
        Возвращает True, если когнитивная карта стабильна (объединяет проверку структурной устройчивости и
        устойчивости к возмущениям)

    fill_from_json(self, data, data_xyz)
        Заполняет данные когнитивной карты из данных в формате JSON
        data - описание когнитивной карты
        data_xyz - описание групп вершин когнитивной карты

    vertex_idx_by_id(self, id)
        Возвращает индекс вершины по ее идентификатору
        id - идентификатор вершины

    rebuild_indexes(self)
        Перестраивает таблицы индексов вершины и ребер когнитивной карты 

    rebuild_matrix(self)
        Перестраивает матрицу смежности согласно массивам вершин и ребер        

    add_vertex(self, v)
        Добавляет вершину
        v - вершина

    add_edge(self, e)
        Добавляет ребро
        e - ребро

    rem_vertex(self, id)
        Удаляет вершину
        id - идентификатор вершины

    rem_edge(self, id)
        Удаляет ребро
        id - идентификатор ребра

    rem_edge_by_vertices(self, v1_id, v2_id)
        Удаляет ребро
        v1_id - идентификатор вершины 1
        v2_id - идентификатор вершины 2
    
    pulse_calc(self, qq, vvq, st)
        Анализ тенденций развития ситуаций на когнитивной модели - импульсное. моделирование
        qq - величины импульсов
        vvq - индексы вершин импульсов
        st - число шагов моделирования

    eig_vals_calc(self, ar)
        Определения устойчивости системы к возмущениям
        ar - матрица смежности

    def simplex_calc(self, v):

    def cycles_calc(self, ar)
        Определения структурной устойчивости
        ar - матрица смежности

    sy1(self, ar, vc)
        расчет симплекса для одной вершины
        ar - матрица смежности
        vc - индекс вершины

    sy(self, ar)
        выдает симплициальные комплексы соответствующего порядка и q- связность между ними, размерность 
        q-связности = количество вершин с которыми она связана минус 1 т.к. наличие всего 1й связи говорит о нулевом порядке связности

    get_composition(self, s1, vk, vs, use)
        Определение композиции выбранной простой структуры
        s1 - матрица кусочка который мы добавляем в систему, отрезок, треугольник, квадрат, часы и тп
        vk - это список вершин исходной матрицы k1 на котрые присоединяется дополнение
        vs - это список вершин исходной  матрица кусочка   s1 котрые для присоединения
        use - флаг метода дополнения исходной матрицы, 0 или 1 - регулирует поведение объединения ребер при их наличии
        Возвращает экземпляр CogMap с обновленными списками вершин и ребер

    comboV(self, k1, s1, vk, vs, use)
        Определение композиции выбранной простой структуры
        k1 - это исходная матрица графа, текущее состояние системы,
        s1 - матрица кусочка который мы добавляем в систему, отрезок, треугольник, квадрат, часы и тп
        vk - это список вершин исходной матрицы k1 на котрые присоединяется дополнение
        vs - это список вершин исходной  матрица кусочка   s1 котрые для присоединения
        use - флаг метода дополнения исходной матрицы, 0 или 1 - регулирует поведение объединения ребер при их наличии
        Возвращает матрицу смежности

    pulse_model(self, N, impulses=None)
        Анализ тенденций развития ситуаций на когнитивной модели - импульсное. моделирование
        N - число шагов моделирования
        impulses - импульсы (если не указаны - заполняются исходя из данных когнитивной карты, полученных их файла при загрузке)
        Возвращает значения вершин

    get_neighbors(self, vertex_idx: int, deep: int)
        Возвращает список соседних вершин в пределах заданной глубины поиска
        vertex_idx - индекс исходной вершины
        deep - глубина поиска

    get_compositions(self, s, vertex: Vertex)
        Возвращает список всех композиций заданной вершины и ее окружения с простой структурой
        vertex - исходная вершина
        s - матрица смежности простой структуры


# Файл optimizer.py #
## Класс SolutionData ##
    Данные решения

## Класс Optimizer ##
    get_simple_structs(self)
        Возвращает список доступных простых структур

    find_impact(self, cogmap: cm.CogMap, V: list[cm.Vertex], N: int, impactgen: ig.ImpactGenerator, initial_impulses: list[float]=None)
        Подбирает воздействие для исправления состояния
        cogmap - когнитивная карта
        V - список вершин для воздействия
        N - число шагов импульсного моделирования
        impactgen - генератор воздействий
        initial_impulses - начальные воздействия (для поиска)

    mix_solutions(self, base_cogmap: cm.CogMap, solutions: list[SolutionData])
        Формирует композицию решений
        base_cogmap - базовая когнитивная карта
        solutions - список решений

    build_compositions(self, base_cogmap: cm.CogMap, partial_solutions: list[SolutionData])
        Формирует список композиций решений
        base_cogmap - базовая когнитивная карта
        partial_solutions - список частных решений

    process_simple_structs(self, cogmap: cm.CogMap, s, vertex: cm.Vertex, impactgen: ig.ImpactGenerator, old_v_bad, old_max_y_er)
        Формирует решения на основе композиций с заданной простой структурой
        cogmap - когнитивная карта
        s - простая структура
        vertex - целевая вершина
        impactgen - генератор воздействий
        old_v_bad - начальный список "плохих" вершин
        old_max_y_er - начальной значение отклонения "плохох" вершин

    find_optimal_changes(self, base_cogmap: cm.CogMap, N: int, simple_structs: list[list[float]], impactgen: ig.ImpactGenerator)
        base_cogmap - базовая когнитивная карта
        N - число шагов импульсного моделирования
        simple_structs - список простых структур
        impactgen - генератор воздействий

# Файл impact_generator.py #
## Класс ImpactData ##
    Данные воздейсвия

## Класс ImpactGenerator ##
    add_impact(self, impact: ImpactData)
        Добавляет воздействие в рестроспективу воздействий
        impact - данные о воздействии

    get_impact(self, cogmap, V: list[cm.Vertex])
        Возвращает воздействие для заданной КК и вершин
        cogmap - когнитивная карта
        V - список вершин

# Файл report.py #
## Класс Report ##
    Генератор отчетов
    __init__(self, data)
        Конструктор
        data - данные для отчета

    build_report(self)
        Формирует отчет в формате JSON

    save_to_file(self, filename)
        Записывает отчет в файл
        filename - имя файла   