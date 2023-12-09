import numpy as np
import copy
import json
import itertools as it
import proba


class Impulses:
    """Описывает серию импульсов (воздействий) на когнитивную карту"""
    __slots__ = ("imp", "v_imp")

    def __init__(self, imp, v_imp):
        """

        :param imp:
        :param v_imp:
        """
        self.imp = imp
        self.v_imp = v_imp


class Vertex:
    """Описывает вершину когнитивной карты"""
    __slots__ = ("id", "value", "min", "max", "impulse", "name", "idx", "short_name", "color", "show", "growth", "x", "y")

    def __init__(self, id: int, value: proba.ProbA, min: float, max: float, impulse: proba.ProbA, name: str):
        """

        :param id:
        :param value:
        :param min:
        :param max:
        :param impulse:
        :param name:
        """
        self.id = id
        self.value = value
        self.min = min
        self.max = max
        # old self.impulse = impulse
        self.impulse = proba.ProbA()
        self.impulse = impulse
        self.name = name
        self.idx = -1  # используется в работе
        self.short_name = ""
        self.color = "0x808080ff"
        self.show = "false"
        # old self.growth = 0.0
        self.growth = proba.ProbA()
        self.growth.append_value(0.0, 1.0)
        self.x = 0.0
        self.y = 0.0


class Edge:
    """Оисывает ребро когнитивной карты"""
    __slots__ = ("id", "v1_id", "v2_id", "value", "name", "formula", "md", "color")

    def __init__(self, id: int, v1_id: int, v2_id: int, value: proba.ProbA, name: str):
        self.id = id
        self.v1_id = v1_id
        self.v2_id = v2_id
        self.value = value
        self.name = name
        self.formula = ""
        self.md = ""
        self.color = "0x808080ff"


class CogMap:
    """Описывает когнитивную карту"""
    __slots__ = ("X", "Y", "Z", "vertices", "edges", "matrix", "edge_ids", "vertex_ids", "cognimod_settings", "cognimod_map_title", "pulse_calc_log")

    def __init__(self, vertices=[], edges=[]):
        """

        :param vertices:
        :param edges:
        """
        """
        Конструктор.
        ``vertices`` - массив вершин
        ``edged`` - массив ребер
        """
        # X - множество входных, управляющих воздействий, автономно задаваемых СППР или ЛПР, или во взаимодействии с ЛПР
        self.X = []
        # Y - множество оптимизируемых выходных показателей
        self.Y = []
        # Z - множество контролируемых, но неуправляемых возмущающих воздействий внешней и внутренней среды
        self.Z = []
        self.vertices = vertices
        # self.vertices = np.empty((0,), dtype=proba.ProbA)
        self.edges = edges
        self.matrix = None
        self.edge_ids = []
        self.vertex_ids = []
        self.cognimod_settings = None
        self.cognimod_map_title = None
        self.pulse_calc_log = None
        if len(vertices) and len(edges):
            self.rebuild_matrix()

    def is_stable(self):
        """
        Проверяет стабильность когнитивной карты
        :return: True, если когнитивная карта стабильна (объединяет проверку структурной устройчивости и
        устойчивости к возмущениям)
        """
        count, nOfNeg = CogMap.cycles_calc(self.matrix)
        f, m = self.eig_vals_calc(self.matrix)
        return f & (nOfNeg % 2 == 1)

    def fill_from_json(self, data, data_xyz):
        """
        Заполняет данные когнитивной карты из данных в формате JSON.
        :param data: описание когнитивной карты
        :param data_xyz: описание групп вершин когнитивной карты
        :return:
        """
        V, E = [], []
        json_content = json.loads(data)
        json_xyz_content = json.loads(data_xyz)
        self.cognimod_settings = json_content["Settings"]
        self.cognimod_map_title = json_content["MapTitle"]
        json_vertices = json_content["Vertices"]
        for v in json_vertices:
            v_id = 0
            v_value = proba.ProbA()
            v_min = 0.0
            v_max = 0.0
            # old v_impulse = 0.0
            v_impulse = proba.ProbA()
            v_impulse.append_value(0.0, 1.0)
            v_name = ""

            v_short_name = ""
            v_color = ""
            v_show = ""
            # old v_growth = 0.0
            v_growth = proba.ProbA()
            v_growth.append_value(0.0, 1.0)
            v_x = 0.0
            v_y = 0.0

            rnd_val = -1
            rnd_prob = -1
            for item in v.items():
                item_split = item[0].split('-')
                if item_split[0] == "id":
                    v_id = item[1]
                elif item_split[0] == "value":
                    rnd_val = float(item[1])
                    if rnd_val != -1 and rnd_prob != -1:
                        v_value.append_value(rnd_val, rnd_prob)
                        rnd_val = -1
                        rnd_prob = -1
                elif item_split[0] == "prob":
                    rnd_prob = float(item[1])
                    if rnd_val != -1 and rnd_prob != -1:
                        v_value.append_value(rnd_val, rnd_prob)
                        rnd_val = -1
                        rnd_prob = -1
                elif item_split[0] == "min":
                    v_min = float(item[1])
                elif item_split[0] == "max":
                    v_max = float(item[1])
                elif item_split[0] == "impulse":
                    # old v_impulse = float(item[1])
                    v_impulse = proba.ProbA()
                    v_impulse.append_value(float(item[1]), 1.0)
                elif item_split[0] == "fullName":
                    v_name = item[1]
                elif item_split[0] == "shortName":
                    v_short_name = item[1]
                elif item_split[0] == "color":
                    v_color = item[1]
                elif item_split[0] == "show":
                    v_show = item[1]
                elif item_split[0] == "growth":
                    # old v_growth = float(item[1])
                    v_growth = proba.ProbA()
                    v_growth.append_value(float(item[1]), 1.0)
                elif item_split[0] == "x":
                    v_x = item[1]
                elif item_split[0] == "y":
                    v_y = item[1]
            vertex = Vertex(v_id, v_value, v_min, v_max, v_impulse, v_name)
            vertex.short_name = v_short_name
            vertex.color = v_color
            vertex.show = v_show
            vertex.growth = v_growth
            vertex.x = v_x
            vertex.y = v_y
            V.append(vertex)

        json_edges = json_content["Edges"]
        for e in json_edges:
            e_id = 0
            e_weight = proba.ProbA()
            e_shortName = ""
            e_v1 = 0
            e_v2 = 0

            e_formula = ""
            e_md = ""
            e_color = ""
            rnd_val = -1
            rnd_prob = -1
            for item in e.items():
                item_split = item[0].split('-')
                if item_split[0] == "id":
                    e_id = item[1]
                elif item_split[0] == "weight":
                    rnd_val = float(item[1])
                    if rnd_val != -1 and rnd_prob != -1:
                        e_weight.append_value(rnd_val, rnd_prob)
                        rnd_val = -1
                        rnd_prob = -1
                elif item_split[0] == "prob":
                    rnd_prob = float(item[1])
                    if rnd_val != -1 and rnd_prob != -1:
                        e_weight.append_value(rnd_val, rnd_prob)
                        rnd_val = -1
                        rnd_prob = -1
                elif item_split[0] == "v1":
                    e_v1 = item[1]
                elif item_split[0] == "v2":
                    e_v2 = item[1]
                elif item_split[0] == "shortName":
                    e_shortName = item[1]
                elif item_split[0] == "formula":
                    e_formula = item[1]
                elif item_split[0] == "md":
                    e_md = item[1]
                elif item_split[0] == "color":
                    e_color = item[1]
            edge = Edge(e_id, e_v1, e_v2, e_weight, e_shortName)
            edge.formula = e_formula
            edge.md = e_md
            edge.color = e_color
            E.append(edge)

        json_scenarios = json_content["Scenarios"]
        if len(json_scenarios):
            s = json_scenarios[0]
            json_impulses = s["impulses"]
            for impulse in json_impulses:
                imp_val = 0.0
                imp_v = 0
                for item in impulse.items():
                    if item[0] == "val":
                        imp_val = item[1]
                    elif item[0] == "v":
                        imp_v = item[1]
                for v in V:
                    if v.id == imp_v:
                        # old v.impulse = imp_val
                        v.impulse = proba.ProbA()
                        v.impulse.append_value(imp_val, 1.0)
                        break
        json_xyz = json_xyz_content["Groups"]
        for xyz_item in json_xyz:
            vertex_id = xyz_item["id"]
            vertex_group = xyz_item["type"]
            for v in V:
                if v.id == vertex_id:
                    if vertex_group == "X":
                        self.X.append(v)
                    elif vertex_group == "Y":
                        self.Y.append(v)
                        v.min = xyz_item["min"]
                        v.max = xyz_item["max"]
                    elif vertex_group == "Z":
                        self.Z.append(v)
                    break
        self.vertices = V
        self.edges = E
        self.matrix = None
        self.edge_ids = []
        self.vertex_ids = []
        if len(self.vertices) and len(self.edges):
            self.rebuild_matrix()

    def vertex_idx_by_id(self, id):
        """
        Возвращает индекс вершины по ее идентификатору
        :param id: идентификатор вершины
        :return: индекс вершины
        """
        for i in range(len(self.vertex_ids)):
            if self.vertex_ids[i] == id:
                return i
        return None

    def rebuild_indexes(self):
        """
        Перестраивает таблицы индексов вершины и ребер когнитивной карты
        :return:
        """
        self.edge_ids = []
        self.vertex_ids = []
        for v in self.vertices:
            self.vertex_ids.append(v.id)
        for e in self.edges:
            self.edge_ids.append(e.id)

    def rebuild_matrix(self):
        """
        Перестраивает матрицу смежности согласно массивам вершин и ребер
        :return:
        """
        self.rebuild_indexes()

        # old self.matrix = np.zeros((len(self.vertices), len(self.vertices)))
        tmp_prob = proba.ProbA()
        tmp_prob.append_value(0.0, 1.0)
        self.matrix = np.full((len(self.vertices), len(self.vertices)), tmp_prob)

        col, row = 0, 0
        for i in range(len(self.vertices)):
            vid = self.vertex_ids[i]
            for e in self.edges:
                if e.v1_id == vid:
                    v2_idx = self.vertex_idx_by_id(e.v2_id)
                    if v2_idx is None:
                        raise Exception("Invalid vertex id")
                    self.matrix[i][v2_idx] = e.value

    def add_vertex(self, v):
        """
        Добавляет вершину
        :param v: вершина
        :return:
        """
        for ex_v in self.vertices:
            if ex_v.id == v.id:
                raise Exception("Duplicated vertex id")
        self.vertices.append(v)
        self.rebuild_matrix()

    def add_edge(self, e):
        """
        Добавляет ребро
        :param e: ребро
        :return:
        """
        for ex_e in self.edges:
            if ex_e.id == e.id:
                raise Exception("Duplicated edge id")
        v1_found, v2_found = False, False
        for v in self.vertices:
            if v.id == e.v1_id:
                v1_found = True
            if v.id == e.v2_id:
                v2_found = True
            if v1_found and v2_found:
                self.edges.append(e)
                self.rebuild_matrix()
                return
        raise Exception("Invalid vertex id")

    def rem_vertex(self, id):
        """
        Удаляет вершину
        :param id: идентификатор вершины
        :return:
        """
        for i in range(len(self.vertices)):
            if self.vertices[i].id == id:
                self.vertices.pop(i)
                for e in self.edges:
                    if (e.v1_id == id) or (e.v2_id == id):
                        self.edges.remove(e)
                self.rebuild_matrix()
                return
        raise Exception("Invalid vertex id")

    def rem_edge(self, id):
        """
        Удаляет ребро
        :param id: идентификатор ребра
        :return:
        """
        for i in range(len(self.edges)):
            if self.edges[i].id == id:
                self.edges.pop(i)
                self.rebuild_matrix()
                return
        raise Exception("Invalid edge id")

    def rem_edge_by_vertices(self, v1_id, v2_id):
        """
        Удаляет ребро
        :param v1_id: идентификатор вершины 1
        :param v2_id: идентификатор вершины 2
        :return:
        """
        for i in range(len(self.edges)):
            if (self.edges[i].v1_id == v1_id) and (self.edges[i].v2_id == v2_id):
                self.edges.pop(i)
                self.rebuild_matrix()
                return
        raise Exception("Invalid vertex id")

    def init_pulse_calc_log(self, vals):
        """
        Инициализирует лог импульсного моделирования
        :param vals: массив значений вершин
        :return:
        """
        self.pulse_calc_log = [vals]

    def append_pulse_calc_log(self, vals):
        """
        Добавляет запись в лог импульсного моделирования
        :param vals: массив значений вершин
        :return:
        """
        self.pulse_calc_log.append(vals)

    def pulse_calc(self, qq, vvq, st, log_values: bool = False):
        """
        Выполняет импульсное моделирование
        :param qq: величины импульсов
        :param vvq: индексы вершин импульсов
        :param st: число шагов моделирования
        :param log_values: если равно True, включает логирование значений вершин на каждом шаге моделирования
        :return: массив новых значений вершин
        """
        n = len(self.matrix)
        # v0 = [self.vertices[i].value for i in range(n)]
        # p0 = [self.vertices[i].growth for i in range(n)]
        v0 = []
        p0 = []
        #v0 = [self.vertices[i].value for i in range(n)]
        #p0 = [self.vertices[i].growth for i in range(n)]
        for i in range(n):
            if isinstance(self.vertices[i].value, float):
                temp = proba.ProbA()
                temp.append_value(self.vertices[i].value, 1.0)
                v0.append(temp)
            else:
                v0.append(self.vertices[i].value)
            p0.append(self.vertices[i].growth)
        for i in range(len(vvq)):
            temp = proba.ProbA()
            temp.append_value(qq[i], 1.0)
            p0[vvq[i]] = p0[vvq[i]] + qq[i]
        if log_values:
            self.init_pulse_calc_log(p0)
            self.append_pulse_calc_log(v0)
        for s in range(st):
            # old v1 = [0.0 for i in range(n)]
            # old p1 = [0.0 for i in range(n)]
            tmp_prob = proba.ProbA()
            tmp_prob.append_value(0.0, 1.0) # ???
            v1 = [tmp_prob for i in range(n)]
            p1 = [tmp_prob for i in range(n)]
            for v in range(n):
                # old v1[v] = v0[v] + p0[v]
                v1[v] = v0[v]+p0[v]
                # old if p0[v] == 0:
                if len(p0[v].vals) == 0 or p0[v].vals[0].value == 0:
                    continue
                for e in range(n):
                    if v == e:
                        continue
                    p1[e] = p1[e] + p0[v] * self.matrix[v][e]
            v0 = v1
            p0 = p1
            if log_values:
                self.append_pulse_calc_log(v1)
        return v1

    @staticmethod
    #@numba.njit(fastmath=True)
    #def pulse_calc_opt(matrix: list[list[float]], vertices_value: list[float], vertices_growth: list[float], qq: list[float], vvq: list[int], st: int):
    def pulse_calc_opt(matrix,
                       vertices_value, # : list[proba.ProbA]
                       vertices_growth, # : list[proba.ProbA]
                       qq, vvq, st):
        """
        Выполняет импульсное моделирование (ускоренная и сокращенная версия метода)
        :param matrix: матрица смежности
        :param vertices_value: текущие значения вершин
        :param vertices_growth: текущие значения предустановленных импульсов
        :param qq: величины импульсов
        :param vvq: индексы вершин импульсов
        :param st: число шагов моделирования
        :return: массив новых значений вершин
        """
        n = len(matrix)
        v0 = vertices_value[:]
        for i in range(n):
            if isinstance(v0[i], float):
                temp = proba.ProbA()
                temp.append_value(v0[i], 1.0)
                v0[i] = temp
        p0 = vertices_growth[:]
        for i in range(len(vvq)):
            tmp = proba.ProbA()
            tmp.append_value(qq[i], 1.0)
            p0[vvq[i]] = p0[vvq[i]] + tmp
        tmp = proba.ProbA()
        tmp.append_value(0.0, 1.0)
        for s in range(st):
            v1 = [tmp for i in range(n)]
            p1 = [tmp for i in range(n)]
            for v in range(n):
                v1[v] = v0[v] + p0[v]
                if p0[v] == 0:
                    continue
                for e in range(n):
                    if v == e:
                        continue
                    p1[e] = p1[e] + p0[v] * matrix[v][e]
            v0 = v1
            p0 = p1
        return v1

    def eig_vals_calc(self, ar):
        """
        Рассчитывает собственное число матрицы смежности (оределение устойчивости системы к возмущениям)
        :param ar: матрица смежности
        :return: собственное число
        """
        rows = min(len(self.vertices), len(ar))
        cols = min(len(self.vertices), len(ar[0]))
        ar_ = np.full((rows, cols), 0.0)
        for i in range(rows):
            for j in range(cols):
                ar_[i][j] = ar[i][j].build_scalar()

        w, v = np.linalg.eig(np.array(ar_))
        re = w.real
        im = w.imag
        m = 0
        size = len(ar)
        for i in range(size):
            m = max(abs(m), max(abs(re[i]), abs(im[i])))
        return (m < 1), m

    def simplex_calc(self, v):
        """
        Рассчитывает симплекс для одной вершины
        :param v: индекс вершины
        :return: список вершин симплициального комплекса
        """
        return self.sy1(self.matrix, v)

    @staticmethod
    def cycles_calc(ar):
        """
        Рассчитывает число циклов в когнитивной карте (определение структурной устойчивости)
        :param ar: матрица смежности
        :return: число циклов, число отрицательных циклов
        """

        def dfs(gr: list[list[float]], start: int, v: int, depth: int, stack: np.ndarray, visited: list[bool],
                cycles: list[np.ndarray], count: int) -> tuple[np.ndarray, list[bool], list[list[int]], int]:
            """

            :param gr:
            :param start:
            :param v:
            :param depth:
            :param stack:
            :param visited:
            :param cycles:
            :param count:
            :return:
            """
            stack = np.append(stack, v)
            if visited[v]:
                if start == v:  # found a path
                    cycle = np.array(stack)
                    cycles.append(cycle)
                    count = count + 1

                stack = np.delete(stack, len(stack) - 1)
            else:
                visited[v] = True
                links = np.array(gr[v])
                for l in range(len(gr)):
                    if links[l] != 0:
                        stack, visited, cycles, count = dfs(gr, start, l, depth + 1, stack, visited, cycles, count)
                visited[v] = False
                stack = np.delete(stack, len(stack) - 1)
            return stack, visited, cycles, count

        def markSign(ar, cycles):
            """

            :param ar:
            :param cycles:
            :return:
            """
            n = len(cycles)
            nOfNeg = 0
            signs = np.array([1 for i in range(n)])
            for j in range(n):
                cycle = cycles[j]
                v0 = cycle[0]
                for i in range(len(cycle) - 1):
                    v = cycle[i + 1]
                    if ar[v0][v] < 0:
                        signs[j] = signs[j] * -1
                    v0 = v
                if signs[j] < 0:
                    nOfNeg = nOfNeg + 1
            return nOfNeg, signs

        def allCyclesDirectedmain(ar: list[list[float]]) -> tuple[list[np.ndarray], int]:
            """

            :param ar:
            :return:
            """
            n = len(ar)
            stack = np.array([], dtype='i4')
            cycles = []
            visited = [False for i in range(n)]
            count = 0
            depth = 1

            for v in range(n):
                stack, visited, cycles, count = dfs(ar, v, v, depth, stack, visited, cycles, count)
                visited[v] = True

            return cycles, count

        cycles, count = allCyclesDirectedmain(ar)
        nOfNeg, signs = markSign(ar, cycles)

        return count, nOfNeg

    def sy1(self, ar, vc):
        """
        Рассчитывает симплекс для одной вершины
        :param ar: матрица смежности
        :param vc: индекс вершины
        :return: список вершин симплициального комплекса
        """
        n = len(ar)  # total # of V
        Vx = [[] for i in range(n)]  # V connected with other V
        qmaxEm = -1
        for j in range(n):
            for v in range(n):
                if j != v:
                    if ar[v][j] != 0.0:
                        Vx[j].append(v)
                        qmaxEm = max(qmaxEm, len(Vx[j]) - 1)
        return Vx[vc]

    def sy(self, ar):
        """
        Рассчитывает все симплициальные комплексы
        :param ar: матрица смежности
        :return: симплициальные комплексы
        """
        n = len(ar) # total # of V
        Vx = [[] for i in range(n)] # V connected with other V
        qmaxEm = -1
        for l in range(n):
            for v in range(n):
                if l != v:
                    if ar[v][l] != 0.0:
                        Vx[l].append(v)
                        qmaxEm = max(qmaxEm, len(Vx[l]) -1 )

        # if Vx has same dots as for Vy - combine it per #of same dots: 3same -> Q2

        Qxx = [[] for i in range(qmaxEm)] # num of V for each Q
        for q in range(qmaxEm, 0, -1):
            for v in range(n):
                if len(Vx[v]) -1 >= q:
                    Qxx[qmaxEm-q].append(v)

        nQ = len(Qxx)
        Qx = [[] for i in range(qmaxEm)]
        for qn in range(nQ): # all ranges
            Qcur = Qxx[qn]
            for vc in range(len(Qcur)):    # all V in cur range
                Vcur = Qcur[vc]
                if Vcur != -1: #skip if already proceed
                    Qx[qn].append([Vcur])
                for v in range(len(Qcur)): # other V in cur range
                    if vc != v:
                        Vint = Qcur[v]
                        intersect = list(set(Vx[Vcur]) & set(Vx[Vint]))
                        q = len(intersect) -1   # has same siplexes
                        if Vint > Vcur and q >= nQ-qn: # and same or higher Q
                            # merge in same part
                            Qx[qn][len(Qx[qn])-1].append(Vint)

        for qn in range(nQ):  # all ranges
            for i in range(len(Qx[qn])):
                for j in range(len(Qx[qn])):
                    if i == j:
                        continue
                    intersect = list(set(Qx[qn][i]) & set(Qx[qn][j])) # cur with each in line
                    ii = len(intersect)
                    if ii > 0:
                        Qx[qn][i] = list(set(Qx[qn][i] + Qx[qn][j]))
                        Qx[qn][j] = []
            Qx[qn] = [item for item in Qx[qn] if item != []]

        return Qx

    def pulse_model_nn(self, N):
        """
        Выполняет импульсное моделирование
        :param N: число шагов импульсного моделирования
        :return: массив отклонений значений контролируемых вершин
        """
        v_values = self.pulse_calc([], [], N)
        res_deltas = []
        for v in self.vertices:
            temp = proba.ProbA()
            if v.id in [y.id for y in self.Y]:
                temp.append_value((v.max + v.min) / 2, 1.0)
                res_deltas.append(temp - v_values[v.idx])
            else:
                temp.append_value(0.0, 1.0)
                res_deltas.append(temp)
        return res_deltas

    def get_composition(self, s1, vk, vs, use):
        """
        Формирует композицию выбранной простой структуры
        :param s1: матрица смежности простой структуры
        :param vk: список вершин исходной матрицы на которые присоединяется дополнение
        :param vs: список вершин простой структуры s1 для присоединения
        :param use: флаг метода дополнения исходной матрицы, 0 или 1 - регулирует поведение объединения ребер при их наличии
        :return: новая когнитивная карта с наложенной простой структурой
        """
        gr = self.comboV(self.matrix, s1, vk, vs, use)
        new_cogmap = copy.deepcopy(self)

        max_v_id = self.vertices[0].id
        max_e_id = self.edges[0].id
        for v in self.vertices:
            max_v_id = max(v.id, max_v_id)
        for e in self.edges:
            max_e_id = max(e.id, max_e_id)

        # обновляем существующие ребра согласно новой матрице
        for i in range(len(self.matrix)):
            for j in range(len(self.matrix)):
                v1_id = self.vertices[i].id
                v2_id = self.vertices[j].id
                f = False
                for e in new_cogmap.edges:
                    if e.v1_id == v1_id and e.v2_id == v2_id:
                        f = True
                        if e.value != gr[i][j]:
                            e.value = gr[i][j]
                            e.color = "0xff8080ff"
                        break
                if not f:
                    if gr[i][j] != 0.0:
                        max_e_id = max_e_id + 1
                        e = Edge(max_e_id, v1_id, v2_id, gr[i][j], "New %d" % max_e_id)
                        e.color = "0x80ff80ff"
                        xm = (new_cogmap.vertices[i].x + new_cogmap.vertices[j].x) / 2
                        ym = (new_cogmap.vertices[i].y + new_cogmap.vertices[j].y) / 2
                        e.md = f"({xm},{ym})"
                        new_cogmap.edges.append(e)

        max_x = new_cogmap.vertices[0].x
        max_y = new_cogmap.vertices[0].y
        for i in range(len(new_cogmap.vertices)):
            max_x = max(max_x, new_cogmap.vertices[i].x)
            max_y = max(max_y, new_cogmap.vertices[i].y)

        if len(gr) > len(self.matrix):
            for i in range((len(gr) - len(self.matrix))):
                max_v_id = max_v_id + 1
                v = Vertex(max_v_id, 0.0, 0.0, 0.0, 0.0, "New %d" % max_v_id)
                v.color = "0x80ff80ff"
                v.short_name = "V"
                v.x = max_x + 30
                v.y = max_y + 30
                max_x = max_x + 30
                max_y = max_y + 30
                new_cogmap.X.append(v)
                new_cogmap.vertices.append(v)

            for i in range(len(gr)):
                for j in range(len(gr)):
                    if i < len(self.matrix) and j < len(self.matrix):
                        continue
                    # ребро от i к j
                    v1_id = new_cogmap.vertices[i].id
                    v2_id = new_cogmap.vertices[j].id
                    edge_value = gr[i][j]
                    if edge_value != 0.0:
                        max_e_id = max_e_id + 1
                        e = Edge(max_e_id, v1_id, v2_id, edge_value, "New %d" % max_e_id)
                        e.color = "0x80ff80ff"
                        xm = (new_cogmap.vertices[i].x + new_cogmap.vertices[j].x) / 2
                        ym = (new_cogmap.vertices[i].y + new_cogmap.vertices[j].y) / 2
                        e.md = f"({xm},{ym})"
                        new_cogmap.edges.append(e)
            new_cogmap.rebuild_indexes()
        new_cogmap.matrix = gr
        return new_cogmap

    def comboV(self, k1, s1, vk, vs, use):
        """
        Формирует композицию выбранной простой структуры
        :param k1: матрица смежности когнитивной карты
        :param s1: матрица смежности простой структуры
        :param vk: список вершин исходной матрицы на которые присоединяется дополнение
        :param vs: список вершин простой структуры s1 для присоединения
        :param use: флаг метода дополнения исходной матрицы, 0 или 1 - регулирует поведение объединения ребер при их наличии
        :return: новая матрица смежности с наложенной простой структурой
        """
        assert (len(vk) == len(vs)), "Merging vertices should be same dimension"

        gr = np.array(k1)
        si = np.array(s1)

        # expand matrix
        tmp = proba.ProbA()
        tmp.append_value(0.0, 1.0)
        for l in range(len(si) - len(vs)):
            # old gr = np.append(gr, [[0.0 for i in range(len(k1))]], 0)
            gr = np.append(gr, [[tmp for i in range(len(k1))]], 0)
        for l in range(len(si) - len(vs)):
            # old gr = np.append(gr, [[0.0] for i in range(len(gr))], 1)
            gr = np.append(gr, [[tmp] for i in range(len(gr))], 1)

        # fill with new edges
        for i in range(len(vk)):
            for j in range(len(vk)):
                if i == j:
                    continue

#todo Где-то int...
                tmp = si[vs[i]][vs[j]]
                if use == 0:    # заменяем исходный вес связи
                    gr[vk[i]][vk[j]] = si[vs[i]][vs[j]]
                elif use == 1:  # добаляем вес новой связи
                    gr[vk[i]][vk[j]] = gr[vk[i]][vk[j]] + si[vs[i]][vs[j]]
                elif use == 2:  # усредняем вес старой и новой связи
                    gr[vk[i]][vk[j]] = (gr[vk[i]][vk[j]] + si[vs[i]][vs[j]]) / 2

        # fill row and col for merged vertices
        d = 0
        for i in range(len(si)):
            if i in vs:
                d = d + 1
                continue
            aa = len(k1) + i - d
            for k in range(len(vs)):
                gr[vk[k]][aa] = si[vs[k]][i]
                gr[aa][vk[k]] = si[i][vs[k]]

        # remove rows and cols
        si = np.delete(si, vs, 0)
        si = np.delete(si, vs, 1)

        # fill remaining rows and cols
        for i in range(len(si)):
            for j in range(len(si)):
                gr[len(k1) + i][len(k1) + j] = si[i][j]

        return gr

    def pulse_model(self, N, impulses=None, log_values: bool = False):
        """
        Выполняет импульсное моделирование
        :param N: число шагов импульсного моделирования
        :param impulses: импульсы
        :param log_values: если True, то при импульсном моделировании будет формироваться лог со значениями вершин на каждом шаге
        :return: массив проблемных вершин, отклонение значений проблемных вершин
        """
        imp = []
        v_imp = []
        # Введение возмущений в вершины, соответствующие сигналам изменения данных (X,Y,Z) на основе текущего среза данных.
        if impulses is None:
            for v in self.vertices:
                # old if v.impulse != 0.0:
                if v.impulse.vals[0].value != 0.0:
                    imp.append(v.impulse)
                    v_imp.append(self.vertex_idx_by_id(v.id))
        else:
            imp = impulses.imp
            for imp_vertex in impulses.v_imp:
                v_imp.append(self.vertex_idx_by_id(imp_vertex.id))
        v_values = self.pulse_calc(imp, v_imp, N, log_values)
        v_bad = []
        Y_er = []
        # Определение вершин Vi в которых  нарушается условие Yi_min < Yi < Yi_max и в которых необходимо улучшать процесс. Ситуация отмечается как «плохая» (bad) - Vi bad, i =1,2,…k.
        for y in self.Y:
            y.idx = self.vertex_idx_by_id(y.id)
            temp_max = proba.ProbA()
            temp_max.append_value(y.max, 1.0)
            temp_min = proba.ProbA()
            temp_min.append_value(y.min, 1.0)
            if v_values[y.idx] > temp_max or v_values[y.idx] < temp_min:
                v_bad.append(y)
            y_diff = proba.ProbA()
            y_diff.append_value(y.max - y.min, 1.0)
            y_avg = proba.ProbA()
            y_avg.append_value((y.max + y.min) / 2, 1.0)
            tmp_y = y_avg - v_values[y.idx]
            tmp_y.abs()
            Y_er.append(tmp_y / y_diff)

        temp_t = proba.ProbA()
        temp_t = temp_t.max(Y_er)
        temp_f = proba.ProbA()
        temp_f.append_value(0.0, 1.0)
        return v_bad, temp_t if len(v_bad) else temp_f

    def pulse_model_opt(self, N, Vpulse, Vidx):
        """
        Выполняет импульсное моделирование (сокращенная версия)
        :param N: число шагов импульсного моделирования
        :param Vpulse: знаечния импульсов
        :param Vidx: индексы вершин для импульсов
        :return: отклонение значений проблемных вершин
        """
        # Введение возмущений в вершины, соответствующие сигналам изменения данных (X,Y,Z) на основе текущего среза данных.

        vertices_value = [v.value for v in self.vertices]
        vertices_growth = [v.growth for v in self.vertices]
        v_values = self.pulse_calc_opt(self.matrix, vertices_value, vertices_growth, Vpulse, Vidx, N)
        flag = False
        Y_er = []
        # Определение вершин Vi в которых  нарушается условие Yi_min < Yi < Yi_max и в которых необходимо улучшать процесс. Ситуация отмечается как «плохая» (bad) - Vi bad, i =1,2,…k.
        for y in self.Y:
            y.idx = self.vertex_idx_by_id(y.id)
            temp_max = proba.ProbA()
            temp_max.append_value(y.max, 1.0)
            temp_min = proba.ProbA()
            temp_min.append_value(y.min, 1.0)
            if v_values[y.idx] > temp_max or v_values[y.idx] < temp_min:
                flag = True
            two = proba.ProbA()
            two.append_value(2.0, 1.0)
            temp = proba.ProbA()
            temp = ((temp_max + temp_min) / two) - v_values[y.idx]
            temp.abs()
            Y_er.append(temp / (temp_max - temp_min))
        temp_t = proba.ProbA()
        temp_t = temp_t.max(Y_er)
        temp_f = proba.ProbA()
        temp_f.append_value(0.0, 1.0)
        return temp_t.build_scalar() if flag else temp_f.build_scalar()

    def get_compositions(self, s, vertex: Vertex):
        """
        Возвращает список всех композиций заданной вершины с простой структурой
        :param s: матрица смежности простой структуры
        :param vertex: вершина
        :return: список композиций
        """
        # Определение симплексов sigma вершин v_bad
        sim = self.simplex_calc(self.vertex_idx_by_id(vertex.id))

        compositions = []

        # выбор всех ближайшик вершин
        # определение множества всех верщин КК с заданной глубиной
        vertex_idx = self.vertex_idx_by_id(vertex.id)
        ss_vertices = np.arange(0, len(s))
        for l in range(1, min(len(s), len(sim) + 1) + 1):
            cogmap_vertices = set(sim)
            cogmap_vertices.add(vertex_idx)
            # список вершин ПС заданной длины
            ss_vertices_list = list(it.permutations(ss_vertices, l))
            cogmap_vertices_list = list(it.permutations(cogmap_vertices, l))
            for prod in it.product(*[cogmap_vertices_list, ss_vertices_list]):
                compositions.append([1 if len(prod[0]) < len(s) else 0, self.get_composition(s, prod[0], prod[1], 0)])
        return compositions
