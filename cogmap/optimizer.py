import cogmap as cm
import numpy as np
import itertools as it
import scipy.optimize as opt
import impact_generator as ig


class SolutionData:
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
        # каждая простая структура - матрица смежности (матрицы разных размеров)
        simple_structs = []
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

    def find_impact(self, cogmap: cm.CogMap, V: list[cm.Vertex], N: int, impactgen: ig.ImpactGenerator, initial_impulses: list[float]=None):
        #  V - вершины для воздействия
        #  целевая функция - макисмальное отклонение в вершинах от оптимума
        def opt_func(Vpulse):
            # список вершин с воздействиями
            impulses = cm.Impulses(Vpulse, V)
            v_bad, y_max_er = cogmap.pulse_model(N, impulses)
            return y_max_er

        def build_simplex(n):
            return [i*[0]+[n]+(n+~i)*[0]for i in range(n)]+[n*[1+(n+1)**.5]]

        initial_simplex = build_simplex(len(V))
        if initial_impulses is not None:
            x0 = initial_impulses
        else:
            x0 = impactgen.get_impact(cogmap, V)
        xtol = 1.0e-5 # Точность поиска экстремума
        res = opt.minimize(opt_func, x0, method='Nelder-Mead',
                           options={'xtol': xtol, 'disp': False, 'initial_simplex': initial_simplex})
        if res.success:
            impulses = cm.Impulses(res.x, V)
            v_bad, y_max_er = cogmap.pulse_model(N, impulses)
            return impulses, v_bad, y_max_er
        else:
            return None, None, None

    def mix_solutions(self, base_cogmap: cm.CogMap, solutions: list[SolutionData]):
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
        # На основе списка частных решений формирование композиций решений. Каждая композиция включает по
        # одному частному решению для всех проблемных вершин. Композиции формируются для всех сочетаний

        # группируем в списки по идентификатору целевой вершины (у частных решений список target_vertices содержит удинственную вершину)
        values = set(map(lambda x: x.target_vertices[0].id, partial_solutions))
        grouped_solutions = [[ps for ps in partial_solutions if ps.target_vertices[0].id == x] for x in values]
        # формируем списки композиций на основе декартова произведения списков частных решений для каждой вершины
        # композиция включает частные решения для ВСЕХ вершин, для которых они доступны
        # (например, если для вершины есть только одно частное решение, то оно войдет в КАЖДУЮ композицию)
        compositions = []
        for prod in it.product(*grouped_solutions):
            composition = []
            for solution in prod:
                composition.append(solution)
            cogmap, impulses, target_vertices = self.mix_solutions(base_cogmap, composition)
            compositions.append([cogmap, impulses, target_vertices])
        return compositions

    def process_simple_structs(self, cogmap: cm.CogMap, s, vertex: cm.Vertex, N: int, impactgen: ig.ImpactGenerator, old_v_bad, old_max_y_er):
        def is_valid_solution(v_bad, y_max_er):
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
        # 0 - no solution found
        # 1 - found solution with new vertices
        # 2 - found solution with impact

        # Анализ тенденций развития ситуаций на когнитивной модели по результатам первой серии импульсного моделирования.
        v_bad, max_y_er = base_cogmap.pulse_model(N)
        if len(v_bad) == 0:  # нет проблемных вершин
            return -1, None
        print("Found %d problem vertice(s)" % len(v_bad))

        partial_solutions = []
        for v in v_bad:
            # p2
            # Определение симплексов sigma вершин v_bad

            sim = base_cogmap.simplex_calc(v.idx)
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
        composed_solutions = []
        for c in compositions:
            V = []
            initial_impulses = []
            for i in range(len(c[1].imp)):
                V.append(c[1].v_imp[i])
                initial_impulses.append(c[1].imp[i])
            impulses, bad_vertices, y_max_er = self.find_impact(c[0], V, N, impactgen, initial_impulses)
            composed_solutions.append(SolutionData(1 if len(c[0].matrix) > len(base_cogmap.matrix) else 0, c[0], c[2], impulses, bad_vertices, y_max_er))
        composed_solutions.sort(key=lambda x: (len(x.bad_vertices), x.y_max_er, len(x.cogmap.matrix)))
        # возвращаем статус и данные для отчета
        return 1 if len(compositions) > 0 else 0, composed_solutions
