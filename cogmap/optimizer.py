# pylint: disable=too-many-arguments, too-few-public-methods, too-many-locals, unnecessary-pass
""":file: Модуль с описанием класса когнитивного оптимизатора"""

import itertools as it
import time  # !!!
from typing import List
import numpy as np
import scipy.optimize as opt
import proba
import cogmap as cm
import impact_generator as ig


def debug_print(content, file_path="info.txt"):
    """
    Создает файл и записывает в него строку.
    :param file_path: Путь к файлу, который нужно создать.
    :param content: Строка, которую нужно записать в файл.
    """
    try:
        with open(file_path, "a", encoding="utf-8") as file:
            file.write(f"{content}\n")
    except (FileNotFoundError, PermissionError, OSError) as e:
        print(f"Ошибка при создании файла {file_path}: {e}")


class SolutionData:
    """ Описывает решение """
    __slots__ = ("added_new_vertices", "cogmap", "target_vertices",
                 "impulses", "bad_vertices", "y_max_er")

    def __init__(self, added_new_vertices, cogmap, target_vertices: List[cm.Vertex],
                 impulses: cm.Impulses, bad_vertices, y_max_er):
        """
        Конструктор
        :param added_new_vertices: добавляемые вершины
        :param cogmap: когнитивная карта
        :param target_vertices: целевые вершины
        :param impulses: воздействия
        :param bad_vertices: «плохие» вершины
        :param y_max_er: максимальная ошибка
        """
        self.added_new_vertices = added_new_vertices
        self.cogmap = cogmap
        self.target_vertices = target_vertices
        self.impulses = impulses
        self.bad_vertices = bad_vertices
        self.y_max_er = y_max_er


class Optimizer:
    """ Класс оптимизатора """
    def __init__(self):
        pass

    # noinspection PyMethodMayBeStatic
    def get_simple_structs(self):
        """
        Возвращает список простых структур
        :return: список простых структур (матриц смежности)
        """
        plus = proba.ProbA()
        plus.append_value(1.0, 1.0)
        minus = proba.ProbA()
        minus.append_value(-1.0, 1.0)
        zero = proba.ProbA()
        zero.append_value(0.0, 1.0)
        # Каждая простая структура - матрица смежности (матрицы разных размеров)
        simple_structs = []
        pass  # Отключает оптимизацию со стороны PyCharm при создании simple_structs
        # Отрезок
        simple_structs.append([[zero, plus],
                               [zero, zero]])
        # Треугольник - устойчивый цикл
        simple_structs.append([[zero, zero, plus],
                               [minus, zero, zero],
                               [zero, plus, zero]])
        # Треугольник - неустойчивый цикл
        simple_structs.append([[zero, zero, plus],
                               [plus, zero, zero],
                               [zero, plus, zero]])
        # Песочные часы - устойчивый цикл
        simple_structs.append([[zero, minus, zero, zero, zero],
                               [zero, zero, zero, zero, plus],
                               [zero, zero, zero, plus, zero],
                               [zero, zero, zero, zero, plus],
                               [plus, zero, plus, zero, zero]])
        # Песочные часы - неустойчивый цикл
        simple_structs.append([[zero, minus, zero, zero, zero],
                               [zero, zero, zero, zero, plus],
                               [zero, zero, zero, minus, zero],
                               [zero, zero, zero, zero, plus],
                               [plus, zero, plus, zero, zero]])
        # Два треугольника - неустойчивый цикл
        simple_structs.append([[zero, plus, zero, zero],
                               [zero, zero, zero, plus],
                               [zero, plus, zero, zero],
                               [plus, zero, plus, zero]])
        # Конверт - неустойчивый цикл
        simple_structs.append([[zero, plus, zero, zero, zero],
                               [zero, zero, plus, zero, plus],
                               [zero, zero, zero, plus, plus],
                               [plus, zero, zero, zero, plus],
                               [plus, zero, zero, zero, zero]])
        return simple_structs

    # noinspection PyMethodMayBeStatic
    def find_impact(self, cogmap: cm.CogMap, v_lst: List[cm.Vertex], n: int,
                    impactgen: ig.ImpactGenerator, initial_impulses: List[float] = None,
                    log_values: bool = False):
        """
        Подбирает воздействия для корректировки значений проблемных вершин когнитивной карты
        :param cogmap: когнитивная карта
        :param v_lst: список вершин для воздействия
        :param n: число шагов импульсного моделирования
        :param impactgen: генератор воздействий
        :param initial_impulses: начальные воздействия
        :param log_values: если True, то при импульсном моделировании будет
                           формироваться лог со значениями вершин на каждом шаге
        :return: данные воздействий, список оставшихся проблемных вершин, отклонение
                 проблемных вершин
        """
        #  V - вершины для воздействия
        #  Целевая функция - макисмальное отклонение в вершинах от оптимума

        # Заполняем список индексов вершин
        v_idx = []
        for imp_vertex in v_lst:
            v_idx.append(cogmap.vertex_idx_by_id(imp_vertex.id_))

        def opt_func(v_pulse):
            return cogmap.pulse_model_opt(n, v_pulse, v_idx)

        if initial_impulses is not None:
            x0 = initial_impulses
        else:
            x0 = impactgen.get_impact(cogmap, v_lst, n)
        tol = 1.0e-4  # Точность поиска экстремума
        res = opt.minimize(opt_func, x0, method="Nelder-Mead",
                           options={"xatol": tol, "disp": False, "maxiter": 200})

        res_ = []
        for _, x_val in enumerate(res.x):
            temp = proba.ProbA()
            temp.append_value(x_val, 1.0)
            res_.append(temp)

        if res.success:
            impulses = cm.Impulses(res_, v_lst)
            v_bad, y_max_er = cogmap.pulse_model(n, impulses, log_values)
            return impulses, v_bad, y_max_er
        return None, [], 0.0

    # noinspection PyMethodMayBeStatic
    def mix_solutions(self, base_cogmap: cm.CogMap, solutions: List[SolutionData]):
        """
        Совмещает частные решения
        :param base_cogmap: базовая когнитивная карта
        :param solutions: список частных решений
        :return: когнитивная карта (совмещенное решение), данные воздействия для совмещенного
                 решения, список вершин на корректировку которых нацелено совмещенное решение
        """
        v_list = np.arange(start=0, stop=len(base_cogmap.matrix), dtype=int)
        cogmap = base_cogmap
        limit = len(base_cogmap.matrix) - 1
        imp = []
        imp_v_idx = []
        target_vertices = []
        for solution in solutions:
            for i, impulse in enumerate(solution.impulses.imp):
                imp.append(impulse)
                idx = solution.cogmap.vertex_idx_by_id(solution.impulses.v_imp[i].id_)
                if idx > limit:  # Новые вершины относительно базовой КК
                    idx += len(cogmap.matrix) - len(base_cogmap.matrix)
                imp_v_idx.append(idx)
            cogmap = cogmap.get_composition(solution.cogmap.matrix, v_list, v_list, 2)
            target_vertices.append(solution.target_vertices[0])
        counts = np.zeros(len(cogmap.matrix))
        impulses = np.zeros(len(cogmap.matrix))
        for i, impulse in enumerate(imp):
            impulses[imp_v_idx[i]] += impulse.build_scalar()
            counts[imp_v_idx[i]] += 1
        res_imp = []
        res_imp_v = []
        for i, impulse in enumerate(impulses):
            if counts[i]:
                impulses[i] /= counts[i]
                res_imp.append(impulses[i])
                res_imp_v.append(cogmap.vertices[i])
        return cogmap, cm.Impulses(res_imp, res_imp_v), target_vertices

    def build_compositions(self, base_cogmap: cm.CogMap, partial_solutions: List[SolutionData]):
        """
        Формирует композиции частных решений
        :param base_cogmap: базовая когнитивная карта
        :param partial_solutions: список частных решений
        :return: список композиций частных решений
        """
        # На основе списка частных решений формирование композиций решений. Каждая композиция
        # включает по одному частному решению для всех проблемных вершин. Композиции формируются
        # для всех сочетаний

        # Группируем в списки по идентификатору целевой вершины
        # (у частных решений список target_vertices содержит удинственную вершину)
        values = set(map(lambda x: x.target_vertices[0].id_, partial_solutions))
        grouped_solutions = [[ps for ps in partial_solutions if ps.target_vertices[0].id_ == x]
                             for x in values]
        # Формируем списки композиций на основе декартова произведения списков частных решений
        # для каждой вершины композиция включает частные решения для ВСЕХ вершин, для которых они
        # доступны (например, если для вершины есть только одно частное решение, то оно войдет в
        # КАЖДУЮ композицию)
        compositions = []
        i = 0
        for prod in it.product(*grouped_solutions):
            composition = []
            for solution in prod:
                composition.append(solution)
            cogmap, impulses, target_vertices = self.mix_solutions(base_cogmap, composition)
            i += 1
            if i % 50 == 0:
                print(f"Mixed {i}+ compositions")
                # debug_print(f"Mixed {i}+ compositions")
            compositions.append([cogmap, impulses, target_vertices])

        return compositions

    def process_simple_structs(self, cogmap: cm.CogMap, s, vertex: cm.Vertex, n: int,
                               impactgen: ig.ImpactGenerator, old_v_bad, old_max_y_er):
        """
        Сопоставляет простую структуру с проблемной вершиной
        :param cogmap: когнитивная карта
        :param s: простая структура
        :param vertex: проблемная вершина
        :param n: число шагов импульсного моделирования
        :param impactgen: генератор воздействий
        :param old_v_bad: предыдущий список проблемных вершин
        :param old_max_y_er: предыдущее значение отклонения
        :return: список частных решений
        """
        def is_valid_solution(v_bads_lst, y_max_er_lst):
            """
            Проверяет пригодность решения
            :param v_bads_lst: список проблемных вершин
            :param y_max_er_lst: отклонение проблемных вершин
            :return: True, если решение уменьшает отклонение при тех же проблемных вершинах или
            уменьшает число проблемных вершин не увеличивая отклонение
            """
            new_bad_idxs = []
            old_bad_idxs = []
            for v in v_bads_lst:
                new_bad_idxs.append(v.idx)
            for v in old_v_bad:
                old_bad_idxs.append(v.idx)
            return (y_max_er_lst < old_max_y_er and set(new_bad_idxs) == set(old_bad_idxs)) or \
                   (y_max_er_lst <= old_max_y_er and set(new_bad_idxs) < set(old_bad_idxs))

        solutions = []
        compositions = cogmap.get_compositions(np.array(s), vertex)
        print(f"Found {len(compositions)} composition(s)")
        # debug_print(f"Found {len(compositions)} composition(s)")
        comp_num = 0
        comp_len = len(compositions)

        if compositions:
            for comp in compositions:

                comp_num += 1
                print(f"Processing composition #{comp_num}/{comp_len} ...")
                # debug_print(f"Processing composition #{comp_num}/{comp_len} ...")
                if comp[0] == 1:
                    if comp[1].is_stable():
                        # Новая КК создается в get_compositions
                        imp, v_bads, y_max_er__ = self.find_impact(comp[1], comp[1].x,
                                                                   n, impactgen)
                        if imp is not None:
                            solutions.append(SolutionData(1, comp[1], [vertex],
                                                          imp, v_bads, y_max_er__))
                            impactgen.add_impact(ig.ImpactData(comp[1], imp, y_max_er__))
                else:
                    imp, v_bads, y_max_er__ = self.find_impact(comp[1], cogmap.x, n, impactgen)
                    if imp is not None:
                        if is_valid_solution(v_bads, y_max_er__):
                            solutions.append(SolutionData(0, comp[1], [vertex], imp,
                                                          v_bads, y_max_er__))
                            impactgen.add_impact(ig.ImpactData(comp[1], imp, y_max_er__))
        else:
            imp, v_bads, y_max_er__ = self.find_impact(cogmap, cogmap.x, n, impactgen)
            if imp is not None:
                # Отсутствие перехода вершин из числа благополучных в проблемные, а также
                # ухудшения состояния проблемных
                if is_valid_solution(v_bads, y_max_er__):
                    # Добавление варианта решения в список частных решений
                    solutions.append(SolutionData(0, cogmap, [vertex], imp, v_bads, y_max_er__))
                    # Пополнение обучающей выборки нейросети
                    impactgen.add_impact(ig.ImpactData(cogmap, imp, y_max_er__))

        # debug_print(f"return solutions")
        return solutions

    def find_optimal_changes(self, base_cogmap: cm.CogMap, n: int,
                             simple_structs: List[List[float]],
                             impactgen: ig.ImpactGenerator, figures_range: List[int]):
        """
        Ищет оптимальное изменение когнитивной карты для приведения значений целевых вершин
        в заданные пределы
        :param base_cogmap: базовая когнитивная карта
        :param n: число шагов импульсного моделирования
        :param simple_structs: список простых структур
        :param impactgen: генератор воздействий
        :param figures_range: список простых фигур для обработки
        :return: 0 - решений не найдено, -1 - решений не требуется,
                +1 - решения найдены; список композиций решений
        """

        # Анализ тенденций развития ситуаций на когнитивной модели по результатам первой
        # серии импульсного моделирования
        v_bad, max_y_er = base_cogmap.pulse_model(n)
        if len(v_bad) == 0:  # Нет проблемных вершин
            return -1, None
        print(f"Found {len(v_bad)} problem vertices")
        # debug_print(f"Found {len(v_bad)} problem vertices")

        partial_solutions = []
        for v in v_bad:
            for i, simple_struct in enumerate(simple_structs):
                # Пропуск структур, не указанных в списке figures_range
                if i not in figures_range:
                    continue
                print(f"Processing simple structure {i} for vertex id {v.id_}")
                # debug_print(f"Processing simple structure {i} for vertex id {v.id_}")
                # Обработка простых структур
                solutions = self.process_simple_structs(base_cogmap, simple_struct, v, n,
                                                        impactgen, v_bad, max_y_er)
                if solutions:
                    partial_solutions.extend(solutions)

        print(f"Found {len(partial_solutions)} solution(s)")
        # debug_print(f"Found {len(partial_solutions)} solution(s)")
        if len(partial_solutions) == 0:
            return None, None

        print("Building compositions", end="")
        # debug_print("Building compositions")
        # Формирование композиций решений
        compositions = self.build_compositions(base_cogmap, partial_solutions)
        print(" - OK")

        # Выполнение когнитивного моделирования для всех композиций.
        # Формирование списка композиций на основе результатов моделирования
        print("Modeling compositions...")
        # debug_print("Modeling compositions...")
        composed_solutions = []
        c_num = 1
        for c in compositions:
            print(f"Composition {c_num}/{len(compositions)}")
            # debug_print(f"Composition {c_num}/{len(compositions)}")
            c_num += 1
            v = []
            initial_impulses = []
            for i, impulse in enumerate(c[1].imp):
                v.append(c[1].v_imp[i])
                initial_impulses.append(impulse)
            impulses, bad_vertices, y_max_er = self.find_impact(c[0], v, n, impactgen,
                                                                initial_impulses, True)
            composed_solutions.append(SolutionData(len(c[0].matrix) - len(base_cogmap.matrix),
                                                   c[0], c[2], impulses, bad_vertices, y_max_er))
        composed_solutions.sort(key=lambda x: (len(x.bad_vertices), x.y_max_er,
                                               len(x.cogmap.matrix)))

        # Возвращаем статус и данные для отчета
        print("Modeling compositions complete")
        # debug_print("Modeling compositions complete")
        return 1 if len(compositions) > 0 else 0, composed_solutions
