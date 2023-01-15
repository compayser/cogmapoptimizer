import cogmap as cm
import numpy as np
import itertools as it
import scipy.optimize as opt
import impact_generator as ig


class SolutionData:
    __slots__ = ("added_new_vertices", "cogmap", "target_vertices", "impulses", "bad_vertices", "y_max_er")

    def __init__(self, added_new_vertices, cogmap, target_vertices: list[cm.Vertex], impulses: cm.Impulses, bad_vertices, y_max_er):
        self.added_new_vertices = added_new_vertices
        self.cogmap = cogmap
        self.target_vertices = target_vertices
        self.impulses = impulses
        self.bad_vertices = bad_vertices
        self.y_max_er = y_max_er


class Optimizer:
    def __init__(self):
        pass

    def get_simple_structs(self):
        """
        Возвращает список простых структур
        :return: список простых структур (матриц смежности)
        """
        # каждая простая структура - матрица смежности (матрицы разных размеров)
        simple_structs = []
        # отрезок
        simple_structs.append([[0, 1],
                               [0, 0]])
        # треугольник - устойчивый цикл
        simple_structs.append([[0, 0, 1],
                               [-1, 0, 0],
                               [0, 1, 0]])
        # треугольник - неустойчивый цикл
        simple_structs.append([[0, 0, 1],
                               [1, 0, 0],
                               [0, 1, 0]])
        # песочные часы - устойчивый цикл
        simple_structs.append([[0, -1, 0, 0, 0],
                               [0, 0, 0, 0, 1],
                               [0, 0, 0, 1, 0],
                               [0, 0, 0, 0, 1],
                               [1, 0, 1, 0, 0]])
        # песочные часы - неустойчивый цикл
        simple_structs.append([[0, -1, 0, 0, 0],
                               [0, 0, 0, 0, 1],
                               [0, 0, 0, -1, 0],
                               [0, 0, 0, 0, 1],
                               [1, 0, 1, 0, 0]])
        # два треугольника - неустойчивый цикл
        simple_structs.append([[0, 1, 0, 0],
                               [0, 0, 0, 1],
                               [0, 1, 0, 0],
                               [1, 0, 1, 0]])
        # конверт - неустойчивый цикл
        simple_structs.append([[0, 1, 0, 0, 0],
                               [0, 0, 1, 0, 1],
                               [0, 0, 0, 1, 1],
                               [1, 0, 0, 0, 1],
                               [1, 0, 0, 0, 0]])
        return simple_structs

    def find_impact(self, cogmap: cm.CogMap, V: list[cm.Vertex], N: int, impactgen: ig.ImpactGenerator,
                    initial_impulses: list[float] = None, log_values: bool = False):
        """
        Подбирает воздействия для корректировки значений проблемных вершин когнитивной карты
        :param cogmap: когнитивная карта
        :param V: список вершин для воздействия
        :param N: число шагов импульсного моделирования
        :param impactgen: генератор воздействий
        :param initial_impulses: начальные воздействия
        :param log_values: если True, то при импульсном моделировании будет формироваться лог со значениями вершин на каждом шаге
        :return: данные воздействий, список оставшихся проблемных вершин, отклонение проблемных вершин
        """
        #  V - вершины для воздействия
        #  целевая функция - макисмальное отклонение в вершинах от оптимума

        # заполняем список индексов вершин
        Vidx = []
        for imp_vertex in V:
            Vidx.append(cogmap.vertex_idx_by_id(imp_vertex.id))

        def opt_func(Vpulse):
            return cogmap.pulse_model_opt(N, Vpulse, Vidx)

        if initial_impulses is not None:
            x0 = initial_impulses
        else:
            x0 = impactgen.get_impact(cogmap, V, N)
        xtol = 1.0e-4 # Точность поиска экстремума
        res = opt.minimize(opt_func, x0, method='Nelder-Mead',
                           options={'xtol': xtol, 'disp': False, 'maxiter': 200})
        if res.success:
            impulses = cm.Impulses(res.x, V)
            v_bad, y_max_er = cogmap.pulse_model(N, impulses, log_values)
            return impulses, v_bad, y_max_er
        else:
            return None, [], 0.0

    def mix_solutions(self, base_cogmap: cm.CogMap, solutions: list[SolutionData]):
        """
        Совмещает частные решения
        :param base_cogmap: базовая когнитивная карта
        :param solutions: список частных решений
        :return: когнитивная карта (совмещенное решение), данные воздействия для совмещенного решения,
        список вершин на корректировку которых нацелено совмещенное решение
        """
        v_list = np.arange(start=0, stop=len(base_cogmap.matrix), dtype=int)
        cogmap = base_cogmap
        limit = len(base_cogmap.matrix) - 1
        imp = []
        imp_v_idx = []
        target_vertices = []
        for solution in solutions:
            for i in range(len(solution.impulses.imp)):
                imp.append(solution.impulses.imp[i])
                idx = solution.cogmap.vertex_idx_by_id(solution.impulses.v_imp[i].id)
                if idx > limit:   # новые вершины относительно базовой КК
                    idx = idx + (len(cogmap.matrix) - len(base_cogmap.matrix))
                imp_v_idx.append(idx)
            cogmap = cogmap.get_composition(solution.cogmap.matrix, v_list, v_list, 2)
            target_vertices.append(solution.target_vertices[0])
        counts = np.zeros(len(cogmap.matrix))
        impulses = np.zeros(len(cogmap.matrix))
        for i in range(len(imp)):
            impulses[imp_v_idx[i]] = impulses[imp_v_idx[i]] + imp[i]
            counts[imp_v_idx[i]] = counts[imp_v_idx[i]] + 1
        res_imp = []
        res_imp_v = []
        for i in range(len(impulses)):
            if counts[i]:
                impulses[i] = impulses[i] / counts[i]
                res_imp.append(impulses[i])
                res_imp_v.append(cogmap.vertices[i])
        return cogmap, cm.Impulses(res_imp, res_imp_v), target_vertices

    def build_compositions(self, base_cogmap: cm.CogMap, partial_solutions: list[SolutionData]):
        """
        Формирует композиции частных решений
        :param base_cogmap: базовая когнитивная карта
        :param partial_solutions: список частных решений
        :return: список композиций частных решений
        """
        # На основе списка частных решений формирование композиций решений. Каждая композиция включает по
        # одному частному решению для всех проблемных вершин. Композиции формируются для всех сочетаний

        # группируем в списки по идентификатору целевой вершины (у частных решений список target_vertices содержит удинственную вершину)
        values = set(map(lambda x: x.target_vertices[0].id, partial_solutions))
        grouped_solutions = [[ps for ps in partial_solutions if ps.target_vertices[0].id == x] for x in values]
        # формируем списки композиций на основе декартова произведения списков частных решений для каждой вершины
        # композиция включает частные решения для ВСЕХ вершин, для которых они доступны
        # (например, если для вершины есть только одно частное решение, то оно войдет в КАЖДУЮ композицию)
        compositions = []
        i = 0
        for prod in it.product(*grouped_solutions):
            composition = []
            for solution in prod:
                composition.append(solution)
            cogmap, impulses, target_vertices = self.mix_solutions(base_cogmap, composition)
            i = i+1
            if i % 50 == 0:
                print("Mixed %d+ compositions" % i)
            compositions.append([cogmap, impulses, target_vertices])

        return compositions

    def process_simple_structs(self, cogmap: cm.CogMap, s, vertex: cm.Vertex, N: int, impactgen: ig.ImpactGenerator, old_v_bad, old_max_y_er):
        """
        Сопоставляет простую структуру с проблемной вершиной
        :param cogmap: когнитивная карта
        :param s: простая структура
        :param vertex: проблемная вершина
        :param N: число шагов импульсного моделирования
        :param impactgen: генератор воздействий
        :param old_v_bad: предыдущий список проблемных вершин
        :param old_max_y_er: предыдущее значение отклонения
        :return: список частных решений
        """
        def is_valid_solution(v_bad, y_max_er):
            """
            Проверяет пригодность решения
            :param v_bad: список проблемных вершин
            :param y_max_er: отклонение проблемных вершин
            :return: True, если решение уменьшает отклонение при тех же проблемных вершинах или уменьшает число проблемных вершин не увеличивая отклонение
            """
            new_bad_idxs = []
            old_bad_idxs = []
            for v in v_bad:
                new_bad_idxs.append(v.idx)
            for v in old_v_bad:
                old_bad_idxs.append(v.idx)
            return (y_max_er < old_max_y_er and set(new_bad_idxs) == set(old_bad_idxs)) or (y_max_er <= old_max_y_er and set(new_bad_idxs) < set(old_bad_idxs))

        f = False
        solutions = []
        compositions = cogmap.get_compositions(np.array(s), vertex)
        print("Found %d composition(s)" % len(compositions))
        if len(compositions):
            for comp in compositions:
                if comp[0] == 1:
                    if comp[1].is_stable():
                        # Новая КК создается в get_compositions
                        imp, v_bad, y_max_er = self.find_impact(comp[1], comp[1].X, N, impactgen)
                        if imp is not None:
                            solutions.append(SolutionData(1, comp[1], [vertex], imp, v_bad, y_max_er))
                            impactgen.add_impact(ig.ImpactData(comp[1], imp, y_max_er))
                else:
                    imp, v_bad, y_max_er = self.find_impact(comp[1], cogmap.X, N, impactgen)
                    if imp is not None:
                        if is_valid_solution(v_bad, y_max_er):
                            solutions.append(SolutionData(0, comp[1], [vertex], imp, v_bad, y_max_er))
                            impactgen.add_impact(ig.ImpactData(comp[1], imp, y_max_er))
        else:
            imp, v_bad, y_max_er = self.find_impact(cogmap, cogmap.X, N, impactgen)
            if imp is not None:
                # ...отсутствие перехода вершин из числа благополучных в проблемные, а также ухудшения состояния проблемных
                if is_valid_solution(v_bad, y_max_er):
                    # добавление варианта решения в список частных рещений
                    solutions.append(SolutionData(0, cogmap, [vertex], imp, v_bad, y_max_er))
                    # пополнение обучающей выборки нейросети
                    impactgen.add_impact(ig.ImpactData(cogmap, imp, y_max_er))

        return solutions

    def find_optimal_changes(self, base_cogmap: cm.CogMap, N: int, simple_structs: list[list[float]], impactgen: ig.ImpactGenerator):
        """
        Ищет оптимальное изменение когнитивной карты для приведения значений целевых вершин в заданные пределы
        :param base_cogmap: базовая когнитивная карта
        :param N: число шагов импульсного моделирования
        :param simple_structs: список простых структур
        :param impactgen: генератор воздействий
        :return: 0 - решений не найдено, -1 - решений не требуется, 1 - решения найдены; список композиций решений
        """

        # Анализ тенденций развития ситуаций на когнитивной модели по результатам первой серии импульсного моделирования.
        v_bad, max_y_er = base_cogmap.pulse_model(N)
        if len(v_bad) == 0:  # нет проблемных вершин
            return -1, None
        print("Found %d problem vertice(s)" % len(v_bad))

        partial_solutions = []
        for v in v_bad:
            for i in range(len(simple_structs)):
                print("Processing simple structure %d for vertex id %d" % (i, v.id))
                # Обработка простых структур
                solutions = self.process_simple_structs(base_cogmap, simple_structs[i], v, N, impactgen, v_bad, max_y_er)
                if len(solutions):
                    partial_solutions.extend(solutions)

        print("Found %d solution(s)" % len(partial_solutions))
        print("Building compositions...")
        # Формирование композиций решений
        compositions = self.build_compositions(base_cogmap, partial_solutions)

        # Выполнение когнитивного моделирования для всех композиций. Формирование списка копозиций на основе результатов моделирования
        print("Modeling compositions...")
        composed_solutions = []
        for c in compositions:
            V = []
            initial_impulses = []
            for i in range(len(c[1].imp)):
                V.append(c[1].v_imp[i])
                initial_impulses.append(c[1].imp[i])
            impulses, bad_vertices, y_max_er = self.find_impact(c[0], V, N, impactgen, initial_impulses, True)
            composed_solutions.append(SolutionData(len(c[0].matrix) - len(base_cogmap.matrix), c[0], c[2], impulses, bad_vertices, y_max_er))
        composed_solutions.sort(key=lambda x: (len(x.bad_vertices), x.y_max_er, len(x.cogmap.matrix)))
        # возвращаем статус и данные для отчета
        return 1 if len(compositions) > 0 else 0, composed_solutions
