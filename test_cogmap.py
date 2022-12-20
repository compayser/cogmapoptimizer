from unittest import TestCase
import itertools as it

import utils
from cogmap import CogMap, Vertex, Edge, Impulses
import numpy as np


class TestVertex(TestCase):
    pass


class TestEdge(TestCase):
    pass


class TestCogMap(TestCase):
    def setUp(self) -> None:
        v = []
        e = []
        v.append(Vertex(27, 8, -1, 2, 15, "charlie"))
        v.append(Vertex(42, 7, -3, 4, 12, "donnie"))
        v.append(Vertex(38, 2, -0.5, 2.4, 11, "gillian"))
        e.append(Edge(452, 27, 42, 0.1, "A"))
        e.append(Edge(455, 42, 38, 0.3, "B"))
        e.append(Edge(458, 27, 38, -0.2, "C"))
        self.c = CogMap(v, e)

    def test_vertex_idx_by_id(self):
        self.assertEqual(self.c.vertex_idx_by_id(27), 0)
        self.assertEqual(self.c.vertex_idx_by_id(42), 1)
        self.assertEqual(self.c.vertex_idx_by_id(38), 2)

    def test_rebuild_matrix(self):
        m1 = self.c.matrix
        m2 = np.array([[0, 0.1, -0.2], [0, 0, 0.3], [0, 0, 0]])
        self.assertTrue((m1 == m2).all())
        self.c.vertices.append(Vertex(21, 6, -1.5, 6.4, 17, "dorothy"))
        self.c.edges.append(Edge(113, 38, 21, 0.6, "A"))
        self.c.edges.append(Edge(112, 21, 27, 0.8, "B"))
        self.c.edges.append(Edge(111, 38, 27, 0.1, "C"))
        self.c.rebuild_matrix()
        m2 = np.array([[0, 0.1, -0.2, 0], [0, 0, 0.3, 0], [0.1, 0, 0, 0.6], [0.8, 0, 0, 0]])
        self.assertTrue((self.c.matrix == m2).all())

    def test_add_vertex(self):
        n = len(self.c.vertices)
        self.c.add_vertex(Vertex(878, 101, 0, 0, 2, "bone"))
        self.assertEqual(len(self.c.vertices), n + 1)
        m1 = self.c.matrix
        m2 = np.array([[0, 0.1, -0.2, 0], [0, 0, 0.3, 0], [0, 0, 0, 0], [0, 0, 0, 0]])
        self.assertTrue((m1 == m2).all())

    def test_add_edge(self):
        n = len(self.c.edges)
        self.c.add_edge(Edge(8111, 38, 27, 2, "A"))
        self.assertEqual(len(self.c.edges), n + 1)
        m1 = self.c.matrix
        m2 = np.array([[0, 0.1, -0.2], [0, 0, 0.3], [2, 0, 0]])
        self.assertTrue((m1 == m2).all())

    def test_rem_vertex(self):
        n = len(self.c.vertices)
        self.c.rem_vertex(27)
        self.assertEqual(len(self.c.vertices), n - 1)
        m1 = self.c.matrix
        m2 = np.array([[0, 0.3], [0, 0]])
        self.assertTrue((m1 == m2).all())

    def test_rem_edge(self):
        n = len(self.c.edges)
        self.c.rem_edge(452)
        self.assertEqual(len(self.c.edges), n - 1)
        m1 = self.c.matrix
        m2 = np.array([[0, 0, -0.2], [0, 0, 0.3], [0, 0, 0]])
        self.assertTrue((m1 == m2).all())

    def test_pulse_calc(self):
        # cycles count
        steps = 1
        # put start impulses to V0 with val = 1.1 and to V2 with val = -1.2
        vq = [0, 2]
        q = [1.1, -1.2]
        res = self.c.pulse_calc(q, vq, steps)
        self.assertEqual(res, [1.1, 0.0, -1.2])


        # cycles count
        steps = 2
        # put start impulses to V0 with val = 1.1 and to V2 with val = -1.2
        vq = [0, 2]
        q = [1.1, -1.2]
        res = self.c.pulse_calc(q, vq, steps)
        self.assertEqual(res, [1.1, 1.1 * 0.1, -1.42])


        # cycles count
        steps = 5

        # put start impulses to V0 with val = 1.1 and to V2 with val = -1.2
        vq = [0, 2]
        q = [1.1, -1.2]

        res = self.c.pulse_calc(q, vq, steps)
        self.assertEqual(res, [1.1, 0.11000000000000001, -1.387])

        # TODO проверить на других примерах

    def test_eig_vals_calc(self):
        ar = [[-1, -6], [2, 6]]
        f, m = self.c.eig_vals_calc(ar)
        self.assertEqual(f, False)
        self.assertEqual(m, 3)

    def test_simplex_calc(self):
        self.assertEqual(self.c.simplex_calc(0), [])
        self.assertEqual(self.c.simplex_calc(1), [0])
        self.assertEqual(self.c.simplex_calc(2), [0, 1])

    def test_cycles_calc(self):
        ar = [[0, -1, 1, 1],
              [1, 0, -1, 1],
              [1, 1, 0, -1],
              [-1, 1, 1, 0]]

        # ar = np.random.randint(-1, 1, (13, 13))
        # for i in range(13):
        #    ar[i,i] = 0
        # print(ar)
        # матрица 50х50 - 13 минут и не дождался
        # 10x10 - 6 с
        # 11x11 - 10 с
        # 12x12 - 10 с
        # 13x13 - 111 с
        count, neg = self.c.cycles_calc(ar)
        self.assertEqual(count, 20)
        self.assertEqual(neg, 8)
        # TODO проверить на других примерах

    def test_rem_edge_by_vertices(self):
        n = len(self.c.edges)
        self.c.rem_edge_by_vertices(27, 42)
        self.assertEqual(len(self.c.edges), n - 1)
        m1 = self.c.matrix
        m2 = np.array([[0, 0, -0.2], [0, 0, 0.3], [0, 0, 0]])
        self.assertTrue((m1 == m2).all())

    def test_sy1(self):
        ar = [[0, -1, 1, 1], [1, 0, -1, 1], [1, 1, 0, -1], [-1, 1, 1, 0]]
        self.assertEqual(self.c.sy1(ar, 0), [1, 2, 3])
        self.assertEqual(self.c.sy1(ar, 1), [0, 2, 3])
        self.assertEqual(self.c.sy1(ar, 2), [0, 1, 3])
        self.assertEqual(self.c.sy1(ar, 3), [0, 1, 2])

    def test_sy(self):
        ar = [[0, -1, 1, 1], [1, 0, -1, 1], [1, 1, 0, -1], [-1, 1, 1, 0]]
        self.assertEqual(self.c.sy(ar), [[[0], [1], [2], [3]], [[0, 1, 2, 3]]])

    def test_combo_v(self):
        ar = [[0, -1, -1, -1, -1],
               [-1, 0, -1, -1, -1],
               [-1, -1, 0, -1, -1],
               [-1, -1, -1, 0, -1],
               [-1, -1, -1, -1, 0]]
        sim2 = [[0, 12],
                [21, 0]]
        sim4 = [[0, 12, 13, 14],
                [21, 0, 23, 24],
                [31, 32, 0, 34],
                [41, 42, 43, 0]]
        k1 = np.array(ar)
        s1 = np.array(sim2)
        # Example 1 - merge graph with 2D by 1 vertex
        res1 = [[ 0., -1., -1., -1., -1.,  0.],
                [-1.,  0., -1., -1., -1.,  0.],
                [-1., -1.,  0., -1., -1.,  21.],
                [-1., -1., -1.,  0., -1.,  0.],
                [-1., -1., -1., -1.,  0.,  0.],
                [ 0., 0.,  12.,  0.,  0.,  0.]]

        r = self.c.comboV(k1, s1, [2], [1], 0)
        self.assertTrue((r == np.array(res1)).all())

        # Example 2 - merge graph with 2D by 2 vertex
        k1 = np.array(ar)
        s1 = np.array(sim2)
        res2 = [[ 0., -1., -1., -1., -1.],
                [-1.,  0., -1., 12., -1.],
                [-1., -1.,  0., -1., -1.],
                [-1., 21., -1.,  0., -1.],
                [-1., -1., -1., -1.,  0.]]
        r = self.c.comboV(k1, s1, [1,3], [0,1], 0)
        self.assertTrue((r == np.array(res2)).all())

        # Example 3 - merge graph with 4D by 3 vertex
        k1 = np.array(ar)
        s1 = np.array(sim4)
        res3 = [[ 0., 13., -1., 14., -1., 12.],
                [31.,  0., -1., 34., -1., 32.],
                [-1., -1.,  0., -1., -1.,  0.],
                [41., 43., -1.,  0., -1., 42.],
                [-1., -1., -1., -1.,  0.,  0.],
                [21., 23., 0., 24.,  0.,  0.]]
        r = self.c.comboV(k1, s1, [0,1,3], [0,2,3], 0)
        self.assertTrue((r == np.array(res3)).all())

    def test_get_composition(self):
        s1 = np.array([[0, 0, 1],
                       [-1, 0, 0],
                       [0, 1, 0]])
        res1 = [[0., 0.1, -0.2, 0., 1.],
                [0., 0.,   0.3, 0., 0.],
                [0., 0.,   0.,  0., 0.],
                [-1., 0.,  0.,  0., 0.],
                [0., 0.,   0.,  1., 0.]]
        new_cm = self.c.get_composition(s1, [0], [0], 0)
        self.assertTrue((new_cm.matrix == np.array(res1)).all())

        res2 = [[0., 1., -0.2, 0.],
                [0., 0.,   0.3, 1.],
                [0., 0.,   0.,  0.],
                [-1., 0.,  0.,  0.]]
        new_cm = self.c.get_composition(s1, [0, 1], [0, 2], 0)
#        print(new_cm.matrix)
        self.assertTrue((new_cm.matrix == np.array(res2)).all())

        # cogmap_json_path = "Контрольный пример 1.cmj"
        # cogmap_xyz_json_path = "Контрольный пример 1.cmj_xyz"
        # with open(cogmap_json_path, "r") as config_file:
        #     cogmap_json = config_file.read()
        # with open(cogmap_xyz_json_path, "r") as config_xyz_file:
        #     cogmap_xyz_json = config_xyz_file.read()
        # base_cogmap = CogMap()
        # base_cogmap.fill_from_json(cogmap_json, cogmap_xyz_json)
        # for v in base_cogmap.Y:
        #     for s in utils.get_simple_structs():
        #         base_cogmap.get_composition(s, [v.idx], [0], 0)

    def test_pulse_model(self):
        imp = Impulses([1.1, -1.2], [self.c.vertices[0], self.c.vertices[2]])
        v_bad, max_y_er = self.c.pulse_model(5, imp)
        self.assertEqual(v_bad, [])
        self.assertEqual(max_y_er, 0.0)
        self.c.Y.append(self.c.vertices[2])
        v_bad, max_y_er = self.c.pulse_model(5, imp)
        self.assertEqual(v_bad, [self.c.vertices[2]])
        self.assertEqual(max_y_er, abs(((2.4 - 0.5) / 2) + 1.387) / (2.4 + 0.5))
