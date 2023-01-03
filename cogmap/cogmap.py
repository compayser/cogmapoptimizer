import numpy as np
import copy
import json
import itertools as it


class Impulses:
    def __init__(self, imp, v_imp):
        self.imp = imp
        self.v_imp = v_imp


class Vertex:
    def __init__(self, id, value, min, max, impulse, name):
        self.id = id
        self.value = value
        self.min = min
        self.max = max
        self.impulse = impulse
        self.name = name
        self.idx = -1  # используется в работе


class Edge:
    def __init__(self, id, v1_id, v2_id, value, name):
        self.id = id
        self.v1_id = v1_id
        self.v2_id = v2_id
        self.value = value
        self.name = name


class CogMap:
    def __init__(self, vertices=[], edges=[]):
        # X - множество входных, управляющих воздействий, автономно задаваемых СППР или ЛПР, или во взаимодействии с ЛПР
        self.X = []
        # Y - множество оптимизируемых выходных показателей
        self.Y = []
        # Z - множество контролируемых, но неуправляемых возмущающих воздействий внешней и внутренней среды
        self.Z = []
        self.vertices = vertices
        self.edges = edges
        self.matrix = None
        self.edge_ids = []
        self.vertex_ids = []
        if len(vertices) and len(edges):
            self.rebuild_matrix()

    def is_stable(self):
        count, nOfNeg = self.cycles_calc(self.matrix)
        f, m = self.eig_vals_calc(self.matrix)
        return f & (nOfNeg % 2 == 1)

    def fill_from_json(self, data, data_xyz):
        V, E = [], []
        json_content = json.loads(data)
        json_xyz_content = json.loads(data_xyz)
        json_vertices = json_content["Vertices"]
        for v in json_vertices:
            v_id = 0
            v_value = 0.0
            v_min = 0.0
            v_max = 0.0
            v_impulse = 0.0
            v_name = ""
            for item in v.items():
                if item[0] == "id":
                    v_id = item[1]
                elif item[0] == "value":
                    v_value = item[1]
                elif item[0] == "min":
                    v_min = item[1]
                elif item[0] == "max":
                    v_max = item[1]
                elif item[0] == "impulse":
                    v_impulse = item[1]
                elif item[0] == "fullName":
                    v_name = item[1]
            vertex = Vertex(v_id, v_value, v_min, v_max, v_impulse, v_name)
            V.append(vertex)

        json_edges = json_content["Edges"]
        for e in json_edges:
            e_id = 0
            e_weight = 0.0
            e_shortName = ""
            e_v1 = 0
            e_v2 = 0
            for item in e.items():
                if item[0] == "id":
                    e_id = item[1]
                elif item[0] == "weight":
                    e_weight = item[1]
                elif item[0] == "v1":
                    e_v1 = item[1]
                elif item[0] == "v2":
                    e_v2 = item[1]
                elif item[0] == "shortName":
                    e_shortName = item[1]
            edge = Edge(e_id, e_v1, e_v2, e_weight, e_shortName)
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
                        v.impulse = imp_val
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
        for i in range(len(self.vertex_ids)):
            if self.vertex_ids[i] == id:
                return i
        return None

    def rebuild_indexes(self):
        self.edge_ids = []
        self.vertex_ids = []
        for v in self.vertices:
            self.vertex_ids.append(v.id)
        for e in self.edges:
            self.edge_ids.append(e.id)

    def rebuild_matrix(self):
        self.rebuild_indexes()
        self.matrix = np.zeros((len(self.vertices), len(self.vertices)))
        col,row = 0,0
        for i in range(0,len(self.vertices)):
            vid = self.vertex_ids[i]
            for e in self.edges:
                if e.v1_id == vid:
                    v2_idx = self.vertex_idx_by_id(e.v2_id)
                    if v2_idx is None:
                        raise Exception("Invalid vertex id")
                    self.matrix[i][v2_idx] = e.value

    def add_vertex(self, v):
        for ex_v in self.vertices:
            if ex_v.id == v.id:
                raise Exception("Duplicated vertex id")
        self.vertices.append(v)
        self.rebuild_matrix()

    def add_edge(self, e):
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
        for i in range(len(self.edges)):
            if self.edges[i].id == id:
                self.edges.pop(i)
                self.rebuild_matrix()
                return
        raise Exception("Invalid edge id")

    def rem_edge_by_vertices(self, v1_id, v2_id):
        for i in range(len(self.edges)):
            if (self.edges[i].v1_id == v1_id) and (self.edges[i].v2_id == v2_id):
                self.edges.pop(i)
                self.rebuild_matrix()
                return
        raise Exception("Invalid vertex id")

    def pulse_calc(self, qq, vvq, st):
        n = len(self.matrix)
        v0 = [0.0 for i in range(n)]
        p0 = [0.0 for i in range(n)]
        for i in range(len(vvq)):
            p0[vvq[i]] = qq[i]
        for s in range(st):
            v1 = [0.0 for i in range(n)]
            p1 = [0.0 for i in range(n)]
            for v in range(n):
                v1[v] = v0[v] + p0[v]
                if p0[v] == 0:
                    continue
                for e in range(n):
                    if v == e:
                        continue
                    p1[e] = p1[e] + p0[v] * self.matrix[v][e]
            v0 = v1
            p0 = p1
        return v1

    def eig_vals_calc(self, ar):
        w, v = np.linalg.eig(np.array(ar))
        re = w.real
        im = w.imag
        m = 0
        size = len(ar)
        for i in range(size):
            m = max(abs(m), max(abs(re[i]), abs(im[i])))
        return (m < 1), m

    def simplex_calc(self, v):
        return self.sy1(self.matrix, v)

    def cycles_calc(self, ar):
        def allCyclesDirectedmain(ar):
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

        def dfs(gr, start, v, depth, stack, visited, cycles, count):
            stack = np.append(stack, v)
            if visited[v]:
                if start == v:  # found a path
                    cycle = np.array(stack)
                    cycles.append(cycle)
                    count = count + 1;

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
            n = len(cycles)
            nOfNeg = 0
            signs = np.array([1 for i in range(n)])
            for j in range(n):
                cycle = cycles[j]
                v0 = cycle[0]
                for i in range(len(cycle) - 1):
                    v = cycle[i + 1]
                    if (ar[v0][v] < 0):
                        signs[j] = signs[j] * -1
                    v0 = v
                if signs[j] < 0:
                    nOfNeg = nOfNeg + 1
            return nOfNeg, signs

        cycles, count = allCyclesDirectedmain(ar)
        nOfNeg, signs = markSign(ar, cycles)

        return count, nOfNeg

    def sy1(self, ar, vc):
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

    def get_composition(self, s1, vk, vs, use):
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
                        e.value = gr[i][j]
                        break;
                if not f:
                    max_e_id = max_e_id + 1
                    new_cogmap.edges.append(Edge(max_e_id, v1_id, v2_id, gr[i][j], "New %d" % max_e_id))

        if len(gr) > len(self.matrix):
            for i in range((len(gr) - len(self.matrix))):
                max_v_id = max_v_id + 1
                v = Vertex(max_v_id, 0, 0, 0, 0, "New %d" % max_v_id)
                new_cogmap.X.append(v)
                new_cogmap.vertices.append(v)

            for i in range(len(self.matrix), len(gr)):
                for j in range(len(self.matrix), len(gr)):
                    # ребро от i к j
                    v1_id = new_cogmap.vertices[i].id
                    v2_id = new_cogmap.vertices[j].id
                    edge_value = gr[i][j]
                    if edge_value != 0.0:
                        max_e_id = max_e_id + 1
                        new_cogmap.edges.append(Edge(max_e_id, v1_id, v2_id, edge_value, "New %d" % max_e_id))
            new_cogmap.rebuild_indexes()
        new_cogmap.matrix = gr
        return new_cogmap

    def comboV(self, k1, s1, vk, vs, use):
        assert (len(vk) == len(vs)), "Merging vertices should be same dimension"

        gr = np.array(k1)
        si = np.array(s1)

        # expand matrix
        for l in range(len(si) - len(vs)):
            gr = np.append(gr, [[0 for i in range(len(k1))]], 0)
        for l in range(len(si) - len(vs)):
            gr = np.append(gr, [[0] for i in range(len(gr))], 1)

        # fill with new edges
        for i in range(len(vk)):
            for j in range(len(vk)):
                if i == j:
                    continue
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

    def pulse_model(self, N, impulses=None):
        imp = []
        v_imp = []
        # Введение возмущений в вершины, соответствующие сигналам изменения данных (X,Y,Z) на основе текущего среза данных.
        if impulses is None:
            for v in self.vertices:
                if v.impulse != 0.0:
                    imp.append(v.impulse)
                    v_imp.append(self.vertex_idx_by_id(v.id))
        else:
            imp = impulses.imp
            for imp_vertex in impulses.v_imp:
                v_imp.append(self.vertex_idx_by_id(imp_vertex.id))
        v_values = self.pulse_calc(imp, v_imp, N)
        v_bad = []
        Y_er = []
        # Определение вершин Vi в которых  нарушается условие Yi_min < Yi < Yi_max и в которых необходимо улучшать процесс. Ситуация отмечается как «плохая» (bad) - Vi bad, i =1,2,…k.
        for y in self.Y:
            y.idx = self.vertex_idx_by_id(y.id)
            if v_values[y.idx] > y.max or v_values[y.idx] < y.min:
                v_bad.append(y)
            Y_er.append(abs(((y.max + y.min) / 2) - v_values[y.idx]) / (y.max - y.min))
        return v_bad, max(Y_er) if len(v_bad) else 0.0

    def get_neighbors(self, vertex_idx: int, deep: int):
        assert (deep > 0)
        neighbors = []
        local_neighbors = []    # ближайшие соседи вершины
        for i in range(len(self.matrix)):
            if self.matrix[i][vertex_idx] != 0.0 or self.matrix[vertex_idx][i] != 0.0:
                local_neighbors.append(i)
        if deep == 1:
            return local_neighbors
        else:
            neighbors.extend(local_neighbors)
            for v in local_neighbors:
                neighbors.extend(self.get_neighbors(v, deep - 1))
            return neighbors

    def get_compositions(self, s, vertex: Vertex):
        v = vertex.idx
        compositions = []

        # выбор всех ближайшик вершин
        # определение множества всех верщин КК с заданной глубиной
        vertex_idx = self.vertex_idx_by_id(vertex.id)
        ss_vertices = np.arange(0, len(s))
        for l in range(1, len(s) + 1):
            if l == 1:
                cogmap_vertices = set([vertex_idx])
            elif l == 2:
                cogmap_vertices = set(self.get_neighbors(vertex_idx, l))
                cogmap_vertices.add(vertex_idx)
            else:
                cogmap_vertices = set(self.get_neighbors(vertex_idx, l))
            # список вершин ПС заданной длины
            ss_vertices_list = list(it.permutations(ss_vertices, l))
            cogmap_vertices_list = list(it.permutations(cogmap_vertices, l))
            for prod in it.product(*[cogmap_vertices_list, ss_vertices_list]):
                compositions.append([1 if len(prod[0]) < len(s) else 0, self.get_composition(s, prod[0], prod[1], 0)])
        return compositions
