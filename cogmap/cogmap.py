# pylint: disable=too-many-locals, too-many-arguments
# pylint: disable=too-few-public-methods, too-many-instance-attributes
""":file: Содержит классы, описывающие части когнитивной карты"""
import copy
import json
import itertools as it
from typing import List, Tuple
import numpy as np
import proba


class Impulses:
    """Описывает серию импульсов (воздействий) на когнитивную карту"""
    __slots__ = ("imp", "v_imp")

    def __init__(self, imp, v_imp):
        """
        Конструктор
        :param imp: воздействия
        :param v_imp: вершины для воздействий
        """
        self.imp = imp
        self.v_imp = v_imp


class Vertex:
    """Описывает вершину когнитивной карты"""
    __slots__ = ("id_", "value", "min", "max", "impulse", "name", "idx",
                 "short_name", "color", "show", "growth", "x", "y")

    def __init__(self, id_: int, value: proba.ProbA, min_: float, max_: float,
                 impulse: proba.ProbA, name: str):
        """
        Конструктор
        :param id_: идентификатор вершины
        :param value: вес вершины
        :param min_: минимальное значение веса
        :param max_: максимальное значение веса
        :param impulse: воздействие
        :param name: название вершины
        """
        self.id_ = id_
        self.value = value
        self.min = min_
        self.max = max_
        self.impulse = proba.ProbA()
        self.impulse = impulse
        self.name = name
        self.idx = -1  # Используется в работе
        self.short_name = ""
        self.color = "0x808080ff"
        self.show = "false"
        self.growth = proba.ProbA()
        self.growth.append_value(0.0, 1.0)
        self.x = 0.0
        self.y = 0.0


class Edge:
    """Оисывает ребро когнитивной карты"""
    __slots__ = ("id_", "v1_id", "v2_id", "value", "name", "formula", "md", "color")

    def __init__(self, id_: int, v1_id: int, v2_id: int, value: proba.ProbA, name: str):
        """
        Конструктор
        :param id_: идентификатор ребра
        :param v1_id: идентификатор вершины 1
        :param v2_id: идентификатор вершины 2
        :param value: вес ребра
        :param name: название ребра
        """
        self.id_ = id_
        self.v1_id = v1_id
        self.v2_id = v2_id
        self.value = value
        self.name = name
        self.formula = ""
        self.md = ""
        self.color = "0x808080ff"


class CogMap:
    """Описывает когнитивную карту"""
    __slots__ = ("x", "y", "z", "vertices", "edges", "matrix", "edge_ids",
                 "vertex_ids", "cognimod_settings", "cognimod_map_title", "pulse_calc_log")

    def __init__(self, vertices=None, edges=None):
        """
        Конструктор
        :param vertices: массив вершин
        :param edges: массив ребер
        """
        if edges is None:
            edges = []
        if vertices is None:
            vertices = []
        # X - Множество входных, управляющих воздействий, автономно задаваемых
        # СППР или ЛПР, или во взаимодействии с ЛПР
        self.x = []
        # Y - Множество оптимизируемых выходных показателей
        self.y = []
        # Z - Множество контролируемых, но неуправляемых возмущающих воздействий
        # внешней и внутренней среды
        self.z = []
        self.vertices = vertices
        self.edges = edges
        self.matrix = None
        self.edge_ids = []
        self.vertex_ids = []
        self.cognimod_settings = None
        self.cognimod_map_title = None
        self.pulse_calc_log = None
        if len(vertices) and len(edges):
            self._rebuild_matrix()

    def is_stable(self):
        """
        Проверяет стабильность когнитивной карты
        :return: True, если когнитивная карта стабильна (объединяет проверку структурной
        устройчивости и устойчивости к возмущениям)
        """
        _, n_of_neg = CogMap._cycles_calc(self.matrix)
        f, _ = self._eig_vals_calc(self.matrix)
        return f & (n_of_neg % 2 == 1)

    def fill_from_json(self, data, data_xyz):
        # pylint: disable=too-many-branches, too-many-statements
        """
        Заполняет данные когнитивной карты из данных в формате JSON
        :param data: Описание когнитивной карты
        :param data_xyz: Описание групп вершин когнитивной карты
        :return:
        """
        v_, e_ = [], []
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
            v_impulse = proba.ProbA()
            v_impulse.append_value(0.0, 1.0)
            v_name = ""

            v_short_name = ""
            v_color = ""
            v_show = ""
            v_growth = proba.ProbA()
            v_growth.append_value(0.0, 1.0)
            v_x = 0.0
            v_y = 0.0

            rnd_val = -1
            rnd_prob = -1
            for item in v.items():
                item_split = item[0].split("-")
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
            v_.append(vertex)

        json_edges = json_content["Edges"]
        for e in json_edges:
            e_id = 0
            e_weight = proba.ProbA()
            e_short_name = ""
            e_v1 = 0
            e_v2 = 0

            e_formula = ""
            e_md = ""
            e_color = ""
            rnd_val = -1
            rnd_prob = -1
            for item in e.items():
                item_split = item[0].split("-")
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
                    e_short_name = item[1]
                elif item_split[0] == "formula":
                    e_formula = item[1]
                elif item_split[0] == "md":
                    e_md = item[1]
                elif item_split[0] == "color":
                    e_color = item[1]
            edge = Edge(e_id, e_v1, e_v2, e_weight, e_short_name)
            edge.formula = e_formula
            edge.md = e_md
            edge.color = e_color
            e_.append(edge)

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
                for v in v_:
                    if v.id_ == imp_v:
                        v.impulse = proba.ProbA()
                        v.impulse.append_value(imp_val, 1.0)
                        break
        json_xyz = json_xyz_content["Groups"]
        for xyz_item in json_xyz:
            vertex_id = xyz_item["id"]
            vertex_group = xyz_item["type"]
            for v in v_:
                if v.id_ == vertex_id:
                    if vertex_group == "X":
                        self.x.append(v)
                    elif vertex_group == "Y":
                        self.y.append(v)
                        v.min = xyz_item["min"]
                        v.max = xyz_item["max"]
                    elif vertex_group == "Z":
                        self.z.append(v)
                    break
        self.vertices = v_
        self.edges = e_
        self.matrix = None
        self.edge_ids = []
        self.vertex_ids = []
        if len(self.vertices) and len(self.edges):
            self._rebuild_matrix()

    def vertex_idx_by_id(self, id_):
        """
        Возвращает индекс вершины по ее идентификатору
        :param id_: идентификатор вершины
        :return: индекс вершины
        """
        for i, vertex_id in enumerate(self.vertex_ids):
            if vertex_id == id_:
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
            self.vertex_ids.append(v.id_)
        for e in self.edges:
            self.edge_ids.append(e.id_)

    def _rebuild_matrix(self):
        """
        Перестраивает матрицу смежности согласно массивам вершин и ребер
        :return:
        """
        self.rebuild_indexes()

        self.matrix = np.empty((len(self.vertices), len(self.vertices)), dtype=object)
        for i in range(len(self.vertices)):
            for j in range(len(self.vertices)):
                self.matrix[i, j] = proba.ProbA()
                self.matrix[i, j].append_value(0.0, 1.0)

        for i in range(len(self.vertices)):
            vid = self.vertex_ids[i]
            for e in self.edges:
                if e.v1_id == vid:
                    v2_idx = self.vertex_idx_by_id(e.v2_id)
                    if v2_idx is None:
                        raise ValueError("Invalid vertex id")
                    self.matrix[i][v2_idx] = e.value

    def _add_vertex(self, v):
        """
        Добавляет вершину
        :param v: вершина
        :return:
        """
        for ex_v in self.vertices:
            if ex_v.id_ == v.id_:
                raise ValueError("Duplicated vertex id")
        self.vertices.append(v)
        self._rebuild_matrix()

    def _add_edge(self, e):
        """
        Добавляет ребро
        :param e: ребро
        :return:
        """
        for ex_e in self.edges:
            if ex_e.id_ == e.id_:
                raise ValueError("Duplicated edge id")
        v1_found, v2_found = False, False
        for v in self.vertices:
            if v.id_ == e.v1_id:
                v1_found = True
            if v.id_ == e.v2_id:
                v2_found = True
            if v1_found and v2_found:
                self.edges.append(e)
                self._rebuild_matrix()
                return
        raise ValueError("Invalid vertex id")

    def _rem_vertex(self, id_):
        """
        Удаляет вершину
        :param id_: идентификатор вершины
        :return:
        """
        for i, vertex in enumerate(self.vertices):
            if vertex.id_ == id_:
                self.vertices.pop(i)
                for e in self.edges[:]:  # Копия списка для безопасного удаления
                    if id_ in (e.v1_id, e.v2_id):
                        self.edges.remove(e)
                self._rebuild_matrix()
                return

        raise ValueError("Invalid vertex id")

    def _rem_edge(self, id_):
        """
        Удаляет ребро по его идентификатору
        :param id_: идентификатор ребра
        :return:
        """
        for i, edge in enumerate(self.edges):
            if edge.id_ == id_:
                self.edges.pop(i)
                self._rebuild_matrix()
                return
        raise ValueError("Invalid edge id")

    def _rem_edge_by_vertices(self, v1_id, v2_id):
        """
        Удаляет ребро по его вершинам
        :param v1_id: идентификатор вершины 1
        :param v2_id: идентификатор вершины 2
        :return:
        """
        for i, edge in enumerate(self.edges):
            if edge.v1_id == v1_id and edge.v2_id == v2_id:
                self.edges.pop(i)
                self._rebuild_matrix()
                return
        raise ValueError("Invalid vertex id")

    def _init_pulse_calc_log(self, vals):
        """
        Инициализирует лог импульсного моделирования
        :param vals: массив значений вершин
        :return:
        """
        self.pulse_calc_log = [vals]

    def _append_pulse_calc_log(self, vals):
        """
        Добавляет запись в лог импульсного моделирования
        :param vals: массив значений вершин
        :return:
        """
        self.pulse_calc_log.append(vals)

    def _pulse_calc(self, qq, vvq, st, log_values: bool = False):
        """
        Выполняет импульсное моделирование
        :param qq: величины импульсов
        :param vvq: индексы вершин импульсов
        :param st: число шагов моделирования
        :param log_values: если равно True, включает логирование значений вершин на каждом
                           шаге моделирования
        :return: массив новых значений вершин
        """
        n = len(self.matrix)
        v0 = []
        p0 = []
        v1 = []
        for i in range(n):
            if isinstance(self.vertices[i].value, float):
                temp = proba.ProbA()
                temp.append_value(self.vertices[i].value, 1.0)
                v0.append(temp)
            else:
                v0.append(self.vertices[i].value)
            p0.append(self.vertices[i].growth)
        for i, v in enumerate(vvq):
            temp = proba.ProbA()
            temp.append_value(qq[i], 1.0)
            p0[v] += qq[i]
        if log_values:
            self._init_pulse_calc_log(p0)
            self._append_pulse_calc_log(v0)
        for _ in range(st):
            tmp_prob = proba.ProbA()
            tmp_prob.append_value(0.0, 1.0)
            v1 = [tmp_prob for _ in range(n)]
            p1 = [tmp_prob for _ in range(n)]
            for v in range(n):
                v1[v] = v0[v]+p0[v]
                if len(p0[v].vals) == 0 or p0[v].vals[0].value == 0:
                    continue
                for e in range(n):
                    if v == e:
                        continue
                    p1[e] = p1[e] + p0[v] * self.matrix[v][e]
            v0 = v1
            p0 = p1
            if log_values:
                self._append_pulse_calc_log(v1)
        return v1

    @staticmethod
    def _pulse_calc_opt(matrix,
                        vertices_value: List[proba.ProbA],
                        vertices_growth: List[proba.ProbA],
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
        v1 = []
        for i in range(n):
            if isinstance(v0[i], float):
                temp = proba.ProbA()
                temp.append_value(v0[i], 1.0)
                v0[i] = temp
        p0 = vertices_growth[:]
        for i, v in enumerate(vvq):
            tmp = proba.ProbA()
            tmp.append_value(qq[i], 1.0)
            p0[v] += tmp
        tmp = proba.ProbA()
        tmp.append_value(0.0, 1.0)
        for _ in range(st):
            v1 = [tmp for _ in range(n)]
            p1 = [tmp for _ in range(n)]
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

    def _eig_vals_calc(self, ar):
        """
        Рассчитывает собственное число матрицы смежности (определение устойчивости системы к
        возмущениям)
        :param ar: матрица смежности
        :return: собственное число
        """
        rows = min(len(self.vertices), len(ar))
        cols = min(len(self.vertices), len(ar[0]))
        ar_ = np.full((rows, cols), 0.0)
        for i in range(rows):
            for j in range(cols):
                ar_[i][j] = ar[i][j].build_scalar()

        w, _ = np.linalg.eig(np.array(ar_))
        re = w.real
        im = w.imag
        m = 0
        size = len(ar)
        for i in range(size):
            m = max(abs(m), abs(re[i]), abs(im[i]))
        return (m < 1), m

    def _simplex_calc(self, v):
        """
        Рассчитывает симплекс для одной вершины
        :param v: индекс вершины
        :return: список вершин симплициального комплекса
        """
        return self._sy1(self.matrix, v)

    @staticmethod
    def _cycles_calc(ar):
        """
        Рассчитывает число циклов в когнитивной карте (определение структурной устойчивости)
        :param ar: матрица смежности
        :return: число циклов, число отрицательных циклов
        """
        def dfs(gr: List[List[float]],
                start: int,
                v: int,
                depth: int,
                stack: np.ndarray,
                visited: List[bool],
                cycles_lst: List[np.ndarray], counter: int) -> \
                Tuple[np.ndarray, List[bool], List[List[int]], int]:
            """
            :param gr:
            :param start:
            :param v:
            :param depth:
            :param stack:
            :param visited:
            :param cycles_lst:
            :param counter:
            :return:
            """
            stack = np.append(stack, v)
            if visited[v]:
                if start == v:  # Путь найден
                    cycle = np.array(stack)
                    cycles_lst.append(cycle)
                    counter += 1
                stack = np.delete(stack, len(stack) - 1)
            else:
                visited[v] = True
                links = np.array(gr[v])
                for l in range(len(gr)):
                    if links[l] != 0:
                        stack, visited, cycles_lst, counter = dfs(gr, start, l, depth + 1,
                                                                  stack, visited,
                                                                  cycles_lst, counter)
                visited[v] = False
                stack = np.delete(stack, len(stack) - 1)
            return stack, visited, cycles_lst, counter

        def mark_sign(arr, cycles_lst):
            """
            :param arr:
            :param cycles_lst:
            :return:
            """
            n = len(cycles)
            n_of_neg_ = 0
            signs_ = np.array([1 for _ in range(n)])
            for j in range(n):
                cycle = cycles_lst[j]
                v0 = cycle[0]
                for i in range(len(cycle) - 1):
                    v = cycle[i + 1]
                    if arr[v0][v] < 0:
                        signs_[j] = signs_[j] * -1
                    v0 = v
                if signs_[j] < 0:
                    n_of_neg_ += 1
            return n_of_neg_, signs_

        def all_cycles_directed_main(arr: List[List[float]]) -> Tuple[List[np.ndarray], int]:
            """
            :param arr:
            :return:
            """
            n = len(arr)
            stack = np.array([], dtype="i4")
            cycles_lst = []
            visited = [False for _ in range(n)]
            counter = 0
            depth = 1
            for v in range(n):
                stack, visited, cycles_lst, counter = dfs(ar, v, v, depth, stack,
                                                          visited, cycles_lst, counter)
                visited[v] = True
            return cycles_lst, counter

        cycles, count = all_cycles_directed_main(ar)
        n_of_neg, _ = mark_sign(ar, cycles)
        return count, n_of_neg

    @staticmethod
    def _sy1(ar, vc):
        """
        Рассчитывает симплекс для одной вершины
        :param ar: матрица смежности
        :param vc: индекс вершины
        :return: список вершин симплициального комплекса
        """
        n = len(ar)
        vx = [[] for _ in range(n)]
        qmax_em = -1
        for j in range(n):
            for v in range(n):
                if j != v:
                    if ar[v][j] != 0.0:
                        vx[j].append(v)
                        qmax_em = max(qmax_em, len(vx[j]) - 1)
        return vx[vc]

    @staticmethod
    def _sy(ar):
        # pylint: disable=too-many-branches
        """
        Рассчитывает все симплициальные комплексы
        :param ar: матрица смежности
        :return: симплициальные комплексы
        """
        n = len(ar)
        vx = [[] for _ in range(n)]
        qmax_em = -1
        for l in range(n):
            for v in range(n):
                if l != v:
                    if ar[v][l] != 0.0:
                        vx[l].append(v)
                        qmax_em = max(qmax_em, len(vx[l]) - 1)

        qxx: List[List[int]] = [[] for _ in range(qmax_em)]
        for q in range(qmax_em, 0, -1):
            for v in range(n):
                if len(vx[v]) - 1 >= q:
                    qxx[qmax_em-q].append(v)

        n_q = len(qxx)
        qx = [[] for _ in range(qmax_em)]
        for qn in range(n_q):
            q_cur = qxx[qn]
            for vc, v_cur in enumerate(q_cur):
                if v_cur != -1:
                    qx[qn].append([v_cur])
                for v, vint in enumerate(q_cur):
                    if vc != v:
                        intersect: List = list(set(vx[v_cur]) & set(vx[vint]))
                        q = len(intersect) - 1
                        if vint > v_cur and q >= n_q - qn:
                            qx[qn][-1].append(vint)

        for qn in range(n_q):
            for i in range(len(qx[qn])):
                for j in range(len(qx[qn])):
                    if i == j:
                        continue
                    intersect: List = list(set(qx[qn][i]) & set(qx[qn][j]))
                    ii = len(intersect)
                    if ii > 0:
                        qx[qn][i]: List = list(set(qx[qn][i] + qx[qn][j]))
                        qx[qn][j] = []
            qx[qn] = [item for item in qx[qn] if item != []]

        return qx

    def pulse_model_nn(self, n):
        """
        Выполняет импульсное моделирование
        :param n: число шагов импульсного моделирования
        :return: массив отклонений значений контролируемых вершин
        """
        v_values = self._pulse_calc([], [], n)
        res_deltas = []
        for v in self.vertices:
            temp = proba.ProbA()
            if v.id_ in [y.id_ for y in self.y]:
                temp.append_value((v.max + v.min) / 2, 1.0)
                res_deltas.append(temp - v_values[v.idx])
            else:
                temp.append_value(0.0, 1.0)
                res_deltas.append(temp)
        return res_deltas

    def get_composition(self, s1, vk, vs, use):
        # pylint: disable=too-many-branches, too-many-statements
        """
        Формирует композицию выбранной простой структуры
        :param s1: матрица смежности простой структуры
        :param vk: список вершин исходной матрицы на которые присоединяется дополнение
        :param vs: список вершин простой структуры s1 для присоединения
        :param use: флаг метода дополнения исходной матрицы, 0 или 1 - регулирует поведение
                    объединения ребер при их наличии
        :return: новая когнитивная карта с наложенной простой структурой
        """
        gr = self._combo_v(self.matrix, s1, vk, vs, use)
        new_cogmap = copy.deepcopy(self)

        max_v_id = self.vertices[0].id_
        max_e_id = self.edges[0].id_
        for v in self.vertices:
            max_v_id = max(v.id_, max_v_id)
        for e in self.edges:
            max_e_id = max(e.id_, max_e_id)

        # Обновляем существующие ребра согласно новой матрице
        for i in range(len(self.matrix)):
            for j in range(len(self.matrix)):
                v1_id = self.vertices[i].id_
                v2_id = self.vertices[j].id_
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
                        e = Edge(max_e_id, v1_id, v2_id, gr[i][j], f"New {max_e_id}")
                        e.color = "0x80ff80ff"
                        xm = (new_cogmap.vertices[i].x + new_cogmap.vertices[j].x) / 2
                        ym = (new_cogmap.vertices[i].y + new_cogmap.vertices[j].y) / 2
                        e.md = f"({xm},{ym})"
                        new_cogmap.edges.append(e)

        max_x = new_cogmap.vertices[0].x
        max_y = new_cogmap.vertices[0].y
        for vertex in new_cogmap.vertices:
            max_x = max(max_x, vertex.x)
            max_y = max(max_y, vertex.y)

        zero = proba.ProbA()
        zero.append_value(0.0, 1.0)
        if len(gr) > len(self.matrix):
            for i in range((len(gr) - len(self.matrix))):
                max_v_id = max_v_id + 1
                v = Vertex(max_v_id, zero, 0.0, 0.0, zero, f"New {max_v_id}")
                v.color = "0x80ff80ff"
                v.short_name = "V"
                v.x = max_x + 30
                v.y = max_y + 30
                max_x = max_x + 30
                max_y = max_y + 30
                new_cogmap.x.append(v)
                new_cogmap.vertices.append(v)

            for i, row in enumerate(gr):
                for j, edge_value in enumerate(row):
                    if i < len(self.matrix) and j < len(self.matrix):
                        continue
                    # Ребро от i к j
                    v1_id = new_cogmap.vertices[i].id_
                    v2_id = new_cogmap.vertices[j].id_
                    if edge_value != 0.0:
                        max_e_id += 1
                        e = Edge(max_e_id, v1_id, v2_id, edge_value, f"New {max_e_id}")
                        e.color = "0x80ff80ff"
                        xm = (new_cogmap.vertices[i].x + new_cogmap.vertices[j].x) / 2
                        ym = (new_cogmap.vertices[i].y + new_cogmap.vertices[j].y) / 2
                        e.md = f"({xm},{ym})"
                        new_cogmap.edges.append(e)
            new_cogmap.rebuild_indexes()
        new_cogmap.matrix = gr
        return new_cogmap

    @staticmethod
    def _combo_v(k1, s1, vk, vs, use):
        # pylint: disable=too-many-branches
        """
        Формирует композицию выбранной простой структуры
        :param k1: матрица смежности когнитивной карты
        :param s1: матрица смежности простой структуры
        :param vk: список вершин исходной матрицы на которые присоединяется дополнение
        :param vs: список вершин простой структуры s1 для присоединения
        :param use: флаг метода дополнения исходной матрицы, 0 или 1 - регулирует поведение
                    объединения ребер при их наличии
        :return: новая матрица смежности с наложенной простой структурой
        """
        assert (len(vk) == len(vs)), "Merging vertices should be same dimension"

        gr = np.array(k1)
        si = np.array(s1)

        # Расширяем матрицу
        tmp = proba.ProbA()
        tmp.append_value(0.0, 1.0)
        for _ in range(len(si) - len(vs)):
            gr = np.append(gr, [[tmp for _ in range(len(k1))]], 0)
        for _ in range(len(si) - len(vs)):
            gr = np.append(gr, [[tmp] for _ in range(len(gr))], 1)

        # Заполняем новыми ребрами
        for i, vi in enumerate(vk):
            for j, vj in enumerate(vk):
                if i == j:
                    continue
                if use == 0:  # Заменяем исходный вес связи
                    gr[vi][vj] = si[vs[i]][vs[j]]
                elif use == 1:  # Добавляем вес новой связи
                    gr[vi][vj] += si[vs[i]][vs[j]]
                elif use == 2:  # Усредняем вес старой и новой связи
                    gr[vi][vj] = (gr[vi][vj] + si[vs[i]][vs[j]]) / 2
        # Заполняем строку и столбец для объединенных вершин
        d = 0
        for i, _ in enumerate(si):
            if i in vs:
                d += 1
                continue
            aa = len(k1) + i - d
            for k, v in enumerate(vs):
                gr[vk[k]][aa] = si[v][i]
                gr[aa][vk[k]] = si[i][v]
        # Удаляем строку и столбец
        si = np.delete(si, vs, 0)
        si = np.delete(si, vs, 1)
        # Заполняем оставшиеся столбцы и строки
        for i, row in enumerate(si):
            for j, value in enumerate(row):
                gr[len(k1) + i][len(k1) + j] = value
        return gr

    def pulse_model(self, n, impulses=None, log_values: bool = False):
        """
        Выполняет импульсное моделирование
        :param n: число шагов импульсного моделирования
        :param impulses: импульсы
        :param log_values: если True, то при импульсном моделировании будет формироваться
        лог со значениями вершин на каждом шаге
        :return: массив проблемных вершин, отклонение значений проблемных вершин
        """
        imp = []
        v_imp = []
        # Введение возмущений в вершины, соответствующие сигналам
        # изменения данных (X,Y,Z) на основе текущего среза данных
        if impulses is None:
            for v in self.vertices:
                if v.impulse.vals[0].value != 0.0:
                    imp.append(v.impulse)
                    v_imp.append(self.vertex_idx_by_id(v.id_))
        else:
            imp = impulses.imp
            for imp_vertex in impulses.v_imp:
                v_imp.append(self.vertex_idx_by_id(imp_vertex.id_))
        v_values = self._pulse_calc(imp, v_imp, n, log_values)
        v_bad = []
        y_er = []
        # Определение вершин Vi в которых  нарушается условие Yi_min < Yi < Yi_max и в которых
        # необходимо улучшать процесс. Ситуация отмечается как «плохая» (bad) - Vi bad, i =1,2,…,k.
        for y in self.y:
            y.idx = self.vertex_idx_by_id(y.id_)
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
            y_er.append(tmp_y / y_diff)
        temp_t = proba.ProbA()
        temp_t = temp_t.max(y_er)
        temp_f = proba.ProbA()
        temp_f.append_value(0.0, 1.0)
        return v_bad, temp_t if len(v_bad) > 0 else temp_f

    def pulse_model_opt(self, n, v_pulse, v_idx):
        """
        Выполняет импульсное моделирование (сокращенная версия)
        :param n: число шагов импульсного моделирования
        :param v_pulse: значения импульсов
        :param v_idx: индексы вершин для импульсов
        :return: отклонение значений проблемных вершин
        """
        # Введение возмущений в вершины, соответствующие сигналам изменения данных (X,Y,Z)
        # на основе текущего среза данных.

        vertices_value = [v.value for v in self.vertices]
        vertices_growth = [v.growth for v in self.vertices]
        v_values = self._pulse_calc_opt(self.matrix, vertices_value, vertices_growth,
                                        v_pulse, v_idx, n)
        flag = False
        y_er = []
        # Определение вершин Vi в которых  нарушается условие Yi_min < Yi < Yi_max и в которых
        # необходимо улучшать процесс. Ситуация отмечается как «плохая» (bad) - Vi bad, i =1,2,…k.
        for y in self.y:
            y.idx = self.vertex_idx_by_id(y.id_)
            temp_max = proba.ProbA()
            temp_max.append_value(y.max, 1.0)
            temp_min = proba.ProbA()
            temp_min.append_value(y.min, 1.0)
            if v_values[y.idx] > temp_max or v_values[y.idx] < temp_min:
                flag = True
            two = proba.ProbA()
            two.append_value(2.0, 1.0)
            temp = ((temp_max + temp_min) / two) - v_values[y.idx]
            temp.abs()
            y_er.append(temp / (temp_max - temp_min))
        temp_t = proba.ProbA()
        temp_t = temp_t.max(y_er)
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
        sim = self._simplex_calc(self.vertex_idx_by_id(vertex.id_))

        compositions = []

        # Выбор всех ближайших вершин
        # Определение множества всех вершин КК с заданной глубиной
        vertex_idx = self.vertex_idx_by_id(vertex.id_)
        ss_vertices = np.arange(0, len(s))
        for l in range(1, min(len(s), len(sim) + 1) + 1):
            cogmap_vertices = set(sim)
            cogmap_vertices.add(vertex_idx)
            # Список вершин ПС заданной длины
            ss_vertices_list: List = list(it.permutations(ss_vertices, l))
            cogmap_vertices_list: List = list(it.permutations(cogmap_vertices, l))
            for prod in it.product(*[cogmap_vertices_list, ss_vertices_list]):
                compositions.append([1 if len(prod[0]) < len(s) else 0,
                                     self.get_composition(s, prod[0], prod[1], 0)])
        return compositions
