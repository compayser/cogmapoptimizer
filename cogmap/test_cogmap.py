# pylint: disable=protected-access, too-many-statements, too-many-locals
# pylint: disable=too-many-branches
""":file: Модуль тестирования"""
from unittest import TestCase
import numpy as np
import proba
from cogmap import CogMap, Vertex, Edge, Impulses


class TestVertex(TestCase):
    """
    Тест вершины
    """
    pass  # pylint: disable=unnecessary-pass


class TestEdge(TestCase):
    """
    Тест ребра
    """
    pass  # pylint: disable=unnecessary-pass


class TestCogMap(TestCase):
    """
    Тест когнитивной карты
    """
    def setUp(self) -> None:
        v = []
        e = []
        # Вершины
        rnd1 = proba.ProbA()
        rnd2 = proba.ProbA()
        rnd1.append_value(8, 1)
        rnd2.append_value(15, 1)
        v.append(Vertex(27, rnd1, -1, 2, rnd2, "charlie"))
        rnd3 = proba.ProbA()
        rnd4 = proba.ProbA()
        rnd3.append_value(7, 1)
        rnd4.append_value(12, 1)
        v.append(Vertex(42, rnd3, -3, 4, rnd4, "donnie"))
        rnd5 = proba.ProbA()
        rnd6 = proba.ProbA()
        rnd5.append_value(2, 1)
        rnd6.append_value(11, 1)
        v.append(Vertex(38, rnd5, -0.5, 2.4, rnd6, "gillian"))
        # Ребра
        rnd7 = proba.ProbA()
        rnd7.append_value(0.1, 1)
        e.append(Edge(452, 27, 42, rnd7, "A"))
        rnd8 = proba.ProbA()
        rnd8.append_value(0.3, 1)
        e.append(Edge(455, 42, 38, rnd8, "B"))
        rnd9 = proba.ProbA()
        rnd9.append_value(-0.2, 1)
        e.append(Edge(458, 27, 38, rnd9, "C"))
        # Когнитивная карта
        self.c = CogMap(v, e)
        self.vertices = []

    def test_vertex_idx_by_id(self):
        """
        Тест вершин
        """
        self.assertEqual(self.c.vertex_idx_by_id(27), 0)
        self.assertEqual(self.c.vertex_idx_by_id(42), 1)
        self.assertEqual(self.c.vertex_idx_by_id(38), 2)

    def test_rebuild_matrix(self):
        """
        Тест перестроения матрицы
        """
        m1 = self.c.matrix
        rnd0 = proba.ProbA()
        rnd0.append_value(0, 1)
        rnd01 = proba.ProbA()
        rnd01.append_value(0.1, 1)
        rnd02_ = proba.ProbA()
        rnd02_.append_value(-0.2, 1)
        rnd03 = proba.ProbA()
        rnd03.append_value(0.3, 1)
        m2 = np.array([[rnd0, rnd01, rnd02_], [rnd0, rnd0, rnd03], [rnd0, rnd0, rnd0]])
        count = 0
        for i, row in enumerate(m2):
            for j, val in enumerate(row):
                count += 1
                if not m1[i, j] != val:
                    count -= 1
        self.assertTrue(count == 0)
        rnd6 = proba.ProbA()
        rnd6.append_value(6, 1)
        rnd17 = proba.ProbA()
        rnd17.append_value(17, 1)
        self.c.vertices.append(Vertex(21, rnd6, -1.5, 6.4, rnd17, "dorothy"))
        rnd06 = proba.ProbA()
        rnd06.append_value(0.6, 1)
        rnd08 = proba.ProbA()
        rnd08.append_value(0.8, 1)
        self.c.edges.append(Edge(113, 38, 21, rnd06, "A"))
        self.c.edges.append(Edge(112, 21, 27, rnd08, "B"))
        self.c.edges.append(Edge(111, 38, 27, rnd01, "C"))
        self.c._rebuild_matrix()
        m2 = np.array([[rnd0, rnd01, rnd02_, rnd0],
                       [rnd0, rnd0, rnd03, rnd0],
                       [rnd01, rnd0, rnd0, rnd06],
                       [rnd08, rnd0, rnd0, rnd0]])
        count = 0
        for i, row in enumerate(m2):
            for j, val in enumerate(row):
                count += 1
                if not self.c.matrix[i, j] != val:
                    count -= 1
        self.assertTrue(count == 0)

    def test_add_vertex(self):
        """
        Тест добавления вершин
        """
        n = len(self.c.vertices)
        rnd101 = proba.ProbA()
        rnd101.append_value(101, 1)
        rnd2 = proba.ProbA()
        rnd2.append_value(2, 1)
        self.c._add_vertex(Vertex(878, rnd101, 0, 0, rnd2, "bone"))
        self.assertEqual(len(self.c.vertices), n + 1)
        m1 = self.c.matrix
        rnd0 = proba.ProbA()
        rnd0.append_value(0, 1)
        rnd01 = proba.ProbA()
        rnd01.append_value(0.1, 1)
        rnd02 = proba.ProbA()
        rnd02.append_value(-0.2, 1)
        rnd03 = proba.ProbA()
        rnd03.append_value(0.3, 1)
        m2 = np.array([[rnd0, rnd01, rnd02, rnd0],
                       [rnd0, rnd0, rnd03, rnd0],
                       [rnd0, rnd0, rnd0, rnd0],
                       [rnd0, rnd0, rnd0, rnd0]])
        count = 0
        for i, row in enumerate(m2):
            for j, val in enumerate(row):
                count += 1
                if not m1[i, j] != val:
                    count -= 1
        self.assertTrue(count == 0)

    def test_add_edge(self):
        """
        Тест добавления ребер
        """
        n = len(self.c.edges)
        rnd = proba.ProbA()
        rnd.append_value(2, 1)
        self.c._add_edge(Edge(8111, 38, 27, rnd, "A"))
        self.assertEqual(len(self.c.edges), n + 1)
        m1 = self.c.matrix
        rnd0 = proba.ProbA()
        rnd0.append_value(0.0, 1)
        rnd01 = proba.ProbA()
        rnd01.append_value(0.1, 1)
        rnd02_ = proba.ProbA()
        rnd02_.append_value(-0.2, 1)
        rnd03 = proba.ProbA()
        rnd03.append_value(0.3, 1)
        rnd2 = proba.ProbA()
        rnd2.append_value(2, 1)
        m2 = np.array([[rnd0, rnd01, rnd02_], [rnd0, rnd0, rnd03], [rnd2, rnd0, rnd0]])
        count = 0
        for i, row in enumerate(m2):
            for j, val in enumerate(row):
                count += 1
                if not m1[i, j] != val:
                    count -= 1
        self.assertTrue(count == 0)

    def test_rem_vertex(self):
        """
        Тест удаления вершин
        """
        n = len(self.c.vertices)
        self.c._rem_vertex(27)
        self.assertEqual(len(self.c.vertices), n - 1)
        m1 = self.c.matrix
        rnd0 = proba.ProbA()
        rnd0.append_value(0, 1)
        rnd03 = proba.ProbA()
        rnd03.append_value(0.3, 1)
        m2 = np.array([[rnd0, rnd03], [rnd0, rnd0]])
        count = 0
        for i, row in enumerate(m2):
            for j, val in enumerate(row):
                count += 1
                if not m1[i, j] != val:
                    count -= 1
        self.assertTrue(count == 0)

    def test_rem_edge(self):
        """
        Тест удаления ребер
        """
        n = len(self.c.edges)
        self.c._rem_edge(452)
        self.assertEqual(len(self.c.edges), n - 1)
        m1 = self.c.matrix
        rnd0 = proba.ProbA()
        rnd0.append_value(0, 1)
        rnd02_ = proba.ProbA()
        rnd02_.append_value(-0.2, 1)
        rnd03 = proba.ProbA()
        rnd03.append_value(0.3, 1)
        m2 = np.array([[rnd0, rnd0, rnd02_], [rnd0, rnd0, rnd03], [rnd0, rnd0, rnd0]])
        count = 0
        for i, row in enumerate(m2):
            for j, val in enumerate(row):
                count += 1
                if not m1[i, j] != val:
                    count -= 1
        self.assertTrue(count == 0)

    def test_pulse_calc(self):
        """
        Тест вычисления воздействия
        """
        # Число циклов
        steps = 1
        # Ставим стартовые импульсы на V0 с val=1,1 и на V2 с val=-1,2
        rnd11 = proba.ProbA()
        rnd11.append_value(1.1, 1)
        rnd12_ = proba.ProbA()
        rnd12_.append_value(-1.2, 1)
        q = [rnd11, rnd12_]
        vq = [0, 2]
        res = self.c._pulse_calc(q, vq, steps)
        rnd91 = proba.ProbA()
        rnd91.append_value(9.1, 1)
        rnd70 = proba.ProbA()
        rnd70.append_value(7.0, 1)
        rnd08 = proba.ProbA()
        rnd08.append_value(0.8, 1)
        good = [rnd91, rnd70, rnd08]
        count = 0
        for i, val in enumerate(res):
            count += 1
            if not val != good[i]:
                count -= 1
        self.assertEqual(count, 0)
        # Число циклов
        steps = 2
        # Ставим стартовые импульсы на V0 с val=1,1 и на V2 с val=-1,2
        q = [rnd11, rnd12_]
        vq = [0, 2]
        res = self.c._pulse_calc(q, vq, steps)
        rnd91 = proba.ProbA()
        rnd91.append_value(9.1, 1)
        rnd711 = proba.ProbA()
        rnd711.append_value(7.11, 1)
        rnd058 = proba.ProbA()
        rnd058.append_value(0.5800000000000001, 1)
        good = [rnd91, rnd711, rnd058]
        count = 0
        for i, val in enumerate(res):
            count += 1
            if not val != good[i]:
                count -= 1
        self.assertEqual(count, 0)

        # Число циклов
        steps = 5
        # Ставим стартовые импульсы на V0 с val=1,1 и на V2 с val=-1,2
        q = [rnd11, rnd12_]
        vq = [0, 2]
        res = self.c._pulse_calc(q, vq, steps)
        rnd91 = proba.ProbA()
        rnd91.append_value(9.1, 1)
        rnd711 = proba.ProbA()
        rnd711.append_value(7.11, 1)
        rnd061 = proba.ProbA()
        rnd061.append_value(0.6130000000000001, 1)
        good = [rnd91, rnd711, rnd061]
        count = 0
        for i, val in enumerate(res):
            count += 1
            if not val != good[i]:
                count -= 1
        self.assertEqual(count, 0)

    def test_eig_vals_calc(self):
        """
        Тест вычисления собственных значений
        """
        self.vertices = (1, 2)
        rnd1 = proba.ProbA()
        rnd1.append_value(-1, 1.0)
        rnd2 = proba.ProbA()
        rnd2.append_value(-6, 1.0)
        rnd3 = proba.ProbA()
        rnd3.append_value(+2, 1.0)
        rnd4 = proba.ProbA()
        rnd4.append_value(+6, 1.0)
        ar = [[rnd1, rnd2], [rnd3, rnd4]]
        f, m = self.c._eig_vals_calc(ar)
        self.assertEqual(f, False)
        self.assertEqual(m, 3)

    def test_simplex_calc(self):
        """
        Тест вычисления симплексов
        """
        self.assertEqual(self.c._simplex_calc(0), [])
        self.assertEqual(self.c._simplex_calc(1), [0])
        self.assertEqual(self.c._simplex_calc(2), [0, 1])

    def test_cycles_calc(self):
        """
        Тест вычисления циклов
        """
        ar = [[0, -1, 1, 1],
              [1, 0, -1, 1],
              [1, 1, 0, -1],
              [-1, 1, 1, 0]]
        count, neg = self.c._cycles_calc(ar)
        self.assertEqual(count, 20)
        self.assertEqual(neg, 8)

    def test_rem_edge_by_vertices(self):
        """
        Тест удаления ребра по вершинам
        """
        n = len(self.c.edges)
        self.c._rem_edge_by_vertices(27, 42)
        self.assertEqual(len(self.c.edges), n - 1)
        m1 = self.c.matrix
        rnd0 = proba.ProbA()
        rnd0.append_value(0, 1)
        rnd02_ = proba.ProbA()
        rnd02_.append_value(-0.2, 1)
        rnd03 = proba.ProbA()
        rnd03.append_value(0.3, 1)
        m2 = np.array([[rnd0, rnd0, rnd02_], [rnd0, rnd0, rnd03], [rnd0, rnd0, rnd0]])
        count = 0
        for i, row in enumerate(m2):
            for j, val in enumerate(row):
                count += 1
                if not m1[i, j] != val:
                    count -= 1
        self.assertTrue(count == 0)

    def test_sy1(self):
        """
        Тест вычисления симплекса для одной вершины
        """
        ar = [[0, -1, 1, 1], [1, 0, -1, 1], [1, 1, 0, -1], [-1, 1, 1, 0]]
        self.assertEqual(self.c._sy1(ar, 0), [1, 2, 3])
        self.assertEqual(self.c._sy1(ar, 1), [0, 2, 3])
        self.assertEqual(self.c._sy1(ar, 2), [0, 1, 3])
        self.assertEqual(self.c._sy1(ar, 3), [0, 1, 2])

    def test_sy(self):
        """
        Тест вычисления всех симплициальных комплексов
        """
        ar = [[0, -1, 1, 1], [1, 0, -1, 1], [1, 1, 0, -1], [-1, 1, 1, 0]]
        self.assertEqual(self.c._sy(ar), [[[0], [1], [2], [3]], [[0, 1, 2, 3]]])

    def test_combo_v(self):
        """
        Тест вычисления композиции выбранной простой структуры
        """
        rnd1 = proba.ProbA()
        rnd1.append_value(-1, 1)
        rnd0 = proba.ProbA()
        rnd0.append_value(0, 1)
        ar = [[rnd0, rnd1, rnd1, rnd1, rnd1],
              [rnd1, rnd0, rnd1, rnd1, rnd1],
              [rnd1, rnd1, rnd0, rnd1, rnd1],
              [rnd1, rnd1, rnd1, rnd0, rnd1],
              [rnd1, rnd1, rnd1, rnd1, rnd0]]
        rnd12 = proba.ProbA()
        rnd12.append_value(12, 1)
        rnd21 = proba.ProbA()
        rnd21.append_value(21, 1)
        sim2 = [[rnd0, rnd12],
                [rnd21, rnd0]]
        rnd13 = proba.ProbA()
        rnd13.append_value(13, 1)
        rnd14 = proba.ProbA()
        rnd14.append_value(14, 1)
        rnd23 = proba.ProbA()
        rnd23.append_value(23, 1)
        rnd24 = proba.ProbA()
        rnd24.append_value(24, 1)
        rnd31 = proba.ProbA()
        rnd31.append_value(31, 1)
        rnd32 = proba.ProbA()
        rnd32.append_value(32, 1)
        rnd34 = proba.ProbA()
        rnd34.append_value(34, 1)
        rnd41 = proba.ProbA()
        rnd41.append_value(41, 1)
        rnd42 = proba.ProbA()
        rnd42.append_value(42, 1)
        rnd43 = proba.ProbA()
        rnd43.append_value(43, 1)
        sim4 = [[rnd0, rnd12, rnd13, rnd14],
                [rnd21, rnd0, rnd23, rnd24],
                [rnd31, rnd32, rnd0, rnd34],
                [rnd41, rnd42, rnd43, rnd0]]
        k1 = np.array(ar)
        s1 = np.array(sim2)
        # Пример 1 - объединить граф с 2D по 1 вершине
        res1 = [[rnd0, rnd1, rnd1, rnd1, rnd1, rnd0],
                [rnd1, rnd0, rnd1, rnd1, rnd1, rnd0],
                [rnd1, rnd1, rnd0, rnd1, rnd1, rnd21],
                [rnd1, rnd1, rnd1, rnd0, rnd1, rnd0],
                [rnd1, rnd1, rnd1, rnd1, rnd0, rnd0],
                [rnd0, rnd0, rnd12, rnd0, rnd0, rnd0]]

        r = self.c._combo_v(k1, s1, [2], [1], 0)
        count = 0
        for i, row in enumerate(r):
            for j, val in enumerate(row):
                count += 1
                if not val != res1[i][j]:
                    count -= 1
        self.assertTrue(count == 0)

        # Пример 2 - объединить граф с 2D по 2 вершинам
        k1 = np.array(ar)
        s1 = np.array(sim2)
        res2 = [[rnd0, rnd1, rnd1, rnd1, rnd1],
                [rnd1, rnd0, rnd1, rnd12, rnd1],
                [rnd1, rnd1, rnd0, rnd1, rnd1],
                [rnd1, rnd21, rnd1, rnd0, rnd1],
                [rnd1, rnd1, rnd1, rnd1, rnd0]]
        r = self.c._combo_v(k1, s1, [1, 3], [0, 1], 0)
        count = 0
        for i, row in enumerate(r):
            for j, val in enumerate(row):
                count += 1
                if not val != res2[i][j]:
                    count -= 1
        self.assertTrue(count == 0)

        # Пример 3 - # Пример 3 - объединить граф с 4D по 3 вершине
        k1 = np.array(ar)
        s1 = np.array(sim4)
        res3 = [[rnd0, rnd13, rnd1, rnd14, rnd1, rnd12],
                [rnd31, rnd0, rnd1, rnd34, rnd1, rnd32],
                [rnd1, rnd1, rnd0, rnd1, rnd1, rnd0],
                [rnd41, rnd43, rnd1, rnd0, rnd1, rnd42],
                [rnd1, rnd1, rnd1, rnd1, rnd0, rnd0],
                [rnd21, rnd23, rnd0, rnd24, rnd0, rnd0]]
        r = self.c._combo_v(k1, s1, [0, 1, 3], [0, 2, 3], 0)
        count = 0
        for i, row in enumerate(r):
            for j, val in enumerate(row):
                count += 1
                if not val != res3[i][j]:
                    count -= 1
        self.assertTrue(count == 0)

    def test_get_composition(self):
        """
        Тест формирования композиции выбранной простой структуры
        """
        rnd0 = proba.ProbA()
        rnd0.append_value(0, 1)
        rnd1 = proba.ProbA()
        rnd1.append_value(1, 1)
        rnd1_ = proba.ProbA()
        rnd1_.append_value(-1, 1)
        s1 = np.array([[rnd0, rnd0, rnd1],
                       [rnd1_, rnd0, rnd0],
                       [rnd0, rnd1, rnd0]])
        rnd01 = proba.ProbA()
        rnd01.append_value(0.1, 1)
        rnd02_ = proba.ProbA()
        rnd02_.append_value(-0.2, 1)
        rnd03 = proba.ProbA()
        rnd03.append_value(0.3, 1)
        res1 = [[rnd0, rnd01, rnd02_, rnd0, rnd1],
                [rnd0, rnd0, rnd03, rnd0, rnd0],
                [rnd0, rnd0, rnd0, rnd0, rnd0],
                [rnd1_, rnd0, rnd0, rnd0, rnd0],
                [rnd0, rnd0, rnd0, rnd1, rnd0]]
        new_cm = self.c.get_composition(s1, [0], [0], 0)
        count = 0
        for i, row in enumerate(new_cm.matrix):
            for j, val in enumerate(row):
                count += 1
                if not val != res1[i][j]:
                    count -= 1
        self.assertTrue(count == 0)

        res2 = [[rnd0, rnd1, rnd02_, rnd0],
                [rnd0, rnd0, rnd03, rnd1],
                [rnd0, rnd0, rnd0, rnd0],
                [rnd1_, rnd0, rnd0, rnd0]]
        new_cm = self.c.get_composition(s1, [0, 1], [0, 2], 0)
        count = 0
        for i, row in enumerate(new_cm.matrix):
            for j, val in enumerate(row):
                count += 1
                if not val != res2[i][j]:
                    count -= 1
        self.assertTrue(count == 0)

    def test_pulse_model(self):
        """
        Тест импульсного моделирования
        """
        rnd11 = proba.ProbA()
        rnd11.append_value(1.1, 1)
        rnd12_ = proba.ProbA()
        rnd12_.append_value(-1.2, 1)
        imp = Impulses([rnd11, rnd12_], [self.c.vertices[0], self.c.vertices[2]])
        v_bad, max_y_er = self.c.pulse_model(5, imp)
        self.assertEqual(v_bad, [])
        rnd0 = proba.ProbA()
        rnd0.append_value(0.0, 1.0)
        self.assertFalse(max_y_er != rnd0)
        self.c.y.append(self.c.vertices[2])
        v_bad, max_y_er = self.c.pulse_model(5, imp)
        self.assertEqual(v_bad, [])
        self.assertFalse(max_y_er != rnd0)


class TestProbVal(TestCase):
    """
    Тест вероятностного числа
    """
    pass  # pylint: disable=unnecessary-pass


class TestProbA(TestCase):
    """
    Тесты ДСВ-арифметики
    """
    @classmethod
    def setUpClass(cls) -> None:
        """
        Инициализация экземпляра класса
        """
        cls.rnd = proba.ProbA()

    def test_proba_append_value(self):
        """
        Тест добавления описаний "величина/вероятность" в ДСВ-величину
        """
        self.rnd.vals.clear()
        for i in range(4):
            val = (i + 1) / 10
            prob = (4 - i) / 10
            self.rnd.append_value(val, prob)
        count = 0
        for i in range(4):
            check = self.rnd.vals[i]
            if i == 0 and check.value == 0.1 and check.prob == 0.4:
                count += 1
            if i == 1 and check.value == 0.2 and check.prob == 0.3:
                count += 1
            if i == 2 and check.value == 0.3 and check.prob == 0.2:
                count += 1
            if i == 3 and check.value == 0.4 and check.prob == 0.1:
                count += 1
        self.assertEqual(count, 4)

    def test_proba_check_probs(self):
        """
        Тест проверки ДСВ-величины
        """
        # Подтест 1
        res = self.rnd.check_probs()
        self.assertEqual(res, 0)

        # Подтест 2
        val = 0.0
        prob = 0.2
        self.rnd.append_value(val, prob)
        res = self.rnd.check_probs()
        self.assertEqual(res > 0, True)

        # Подтест 3
        self.rnd.vals.clear()
        val = 0.0
        prob = 0.2
        self.rnd.append_value(val, prob)
        res = self.rnd.check_probs()
        self.assertEqual(res < 0, True)

    def test_proba_check_reduce(self):
        """
        Тест проверки редукции ДСВ-величины
        """
        self.rnd.vals.clear()
        for i in range(100):
            val = i
            prob = 0.01
            self.rnd.append_value(val, prob)
        self.rnd.reduce(10)
        count = 0
        if self.rnd.vals[0].value == 5.000000000000001 and \
                self.rnd.vals[0].prob == 0.10999999999999999:
            count += 1
        if self.rnd.vals[1].value == 16.000000000000004 and \
                self.rnd.vals[1].prob == 0.10999999999999999:
            count += 1
        if self.rnd.vals[2].value == 27.000000000000004 and \
                self.rnd.vals[2].prob == 0.10999999999999999:
            count += 1
        if self.rnd.vals[3].value == 38.000000000000000 and \
                self.rnd.vals[3].prob == 0.10999999999999999:
            count += 1
        if self.rnd.vals[4].value == 49.000000000000014 and \
                self.rnd.vals[4].prob == 0.10999999999999999:
            count += 1
        if self.rnd.vals[5].value == 60.000000000000014 and \
                self.rnd.vals[5].prob == 0.10999999999999999:
            count += 1
        if self.rnd.vals[6].value == 71.000000000000000 and \
                self.rnd.vals[6].prob == 0.10999999999999999:
            count += 1
        if self.rnd.vals[7].value == 82.000000000000000 and \
                self.rnd.vals[7].prob == 0.10999999999999999:
            count += 1
        if self.rnd.vals[8].value == 93.000000000000030 and \
                self.rnd.vals[8].prob == 0.10999999999999999:
            count += 1
        if self.rnd.vals[9].value == 99.000000000000000 and \
                self.rnd.vals[9].prob == 0.01000000000000000:
            count += 1
        self.assertEqual(count, 10)

    def test_proba_check_maths(self):
        """
        Тест проверки ДСВ-арифметики
        """
        rnd1 = proba.ProbA()
        rnd1.append_value(1.0, 0.5)
        rnd1.append_value(2.0, 0.5)
        rnd2 = proba.ProbA()
        rnd2.append_value(1.0, 0.1)
        rnd2.append_value(2.0, 0.2)
        rnd2.append_value(3.0, 0.3)
        rnd2.append_value(4.0, 0.4)

        # Подтест 1 - сложение
        rnd_res = rnd1 + rnd2
        count = 0
        if rnd_res.vals[0].value == 2.0 and rnd_res.vals[0].prob == 0.05:
            count += 1
        if rnd_res.vals[1].value == 3.0 and rnd_res.vals[1].prob == 0.15000000000000002:
            count += 1
        if rnd_res.vals[2].value == 4.0 and rnd_res.vals[2].prob == 0.25:
            count += 1
        if rnd_res.vals[3].value == 5.0 and rnd_res.vals[3].prob == 0.35:
            count += 1
        if rnd_res.vals[4].value == 6.0 and rnd_res.vals[4].prob == 0.2:
            count += 1
        self.assertEqual(count, 5)

        # Подтест 2 - вычитание
        rnd_res = rnd1 - rnd2
        count = 0
        if rnd_res.vals[0].value == -3.0 and rnd_res.vals[0].prob == 0.2:
            count += 1
        if rnd_res.vals[1].value == -2.0 and rnd_res.vals[1].prob == 0.35:
            count += 1
        if rnd_res.vals[2].value == -1.0 and rnd_res.vals[2].prob == 0.25:
            count += 1
        if rnd_res.vals[3].value == 0.0 and rnd_res.vals[3].prob == 0.15000000000000002:
            count += 1
        if rnd_res.vals[4].value == 1.0 and rnd_res.vals[4].prob == 0.05:
            count += 1
        self.assertEqual(count, 5)

        # Подтест 3 - умножение
        rnd_res = rnd1 * rnd2
        count = 0
        if rnd_res.vals[0].value == 1.0 and rnd_res.vals[0].prob == 0.05:
            count += 1
        if rnd_res.vals[1].value == 2.0 and rnd_res.vals[1].prob == 0.15000000000000002:
            count += 1
        if rnd_res.vals[2].value == 3.0 and rnd_res.vals[2].prob == 0.15:
            count += 1
        if rnd_res.vals[3].value == 4.0 and rnd_res.vals[3].prob == 0.30000000000000004:
            count += 1
        if rnd_res.vals[4].value == 6.0 and rnd_res.vals[4].prob == 0.15:
            count += 1
        if rnd_res.vals[5].value == 8.0 and rnd_res.vals[5].prob == 0.2:
            count += 1
        self.assertEqual(count, 6)

        # Подтест 4 - деление
        rnd_res = rnd1 / rnd2
        count = 0
        if rnd_res.vals[0].value == 0.25 and rnd_res.vals[0].prob == 0.2:
            count += 1
        if rnd_res.vals[1].value == 0.3333333333333333 and rnd_res.vals[1].prob == 0.15:
            count += 1
        if rnd_res.vals[2].value == 0.5 and rnd_res.vals[2].prob == 0.30000000000000004:
            count += 1
        if rnd_res.vals[3].value == 0.6666666666666666 and rnd_res.vals[3].prob == 0.15:
            count += 1
        if rnd_res.vals[4].value == 1.0 and rnd_res.vals[4].prob == 0.15000000000000002:
            count += 1
        if rnd_res.vals[5].value == 2.0 and rnd_res.vals[5].prob == 0.05:
            count += 1
        self.assertEqual(count, 6)

    def test_proba_check_compares(self):
        """
        Тесты сравнения ДСВ-величин
        """
        rnd1 = proba.ProbA()
        rnd1.append_value(1.0, 0.5)
        rnd1.append_value(2.0, 0.5)
        rnd2 = proba.ProbA()
        rnd2.append_value(1.0, 0.1)
        rnd2.append_value(2.0, 0.2)
        rnd2.append_value(3.0, 0.3)
        rnd2.append_value(4.0, 0.4)
        rnd3 = proba.ProbA()
        rnd3.append_value(1.0, 0.5)
        rnd3.append_value(2.0, 0.5)

        # Подтест 1 - больше
        self.assertEqual(rnd1 > rnd2, False)
        # Подтест 2 - больше или равно
        self.assertEqual(rnd1 >= rnd3, False)
        # Подтест 3 - меньше
        self.assertEqual(rnd1 < rnd2, True)
        # Подтест 4 - меьше или равно
        self.assertEqual(rnd1 <= rnd3, False)
        # Подтест 5 - не равно
        self.assertEqual(rnd1 != rnd2, True)
        self.assertEqual(rnd1 != rnd3, False)

    def test_proba_check_addons(self):
        """
        Тест дополнительного функционала
        """
        rnd1 = proba.ProbA()
        rnd1.append_value(1.0, 0.5)
        rnd1.append_value(2.0, 0.5)
        rnd2 = proba.ProbA()
        rnd2.append_value(1.0, 0.1)
        rnd2.append_value(2.0, 0.2)
        rnd2.append_value(3.0, 0.3)
        rnd2.append_value(4.0, 0.4)
        rnd3 = proba.ProbA()
        rnd3.append_value(-1.0, 0.5)
        rnd3.append_value(-2.0, 0.5)
        rnd4 = proba.ProbA()
        rnd4.append_value(10.0, 1.0)
        rnd5 = proba.ProbA()

        # Подтест 1 - среднее
        self.assertEqual(rnd1.avg(), +1.5)
        self.assertEqual(rnd2.avg(), +3.0)
        self.assertEqual(rnd3.avg(), -1.5)

        # Подтест 2 - минимум
        arr = [rnd1, rnd2, rnd3]
        min_rnd = min(arr)
        self.assertEqual(min_rnd.avg(), -1.5)

        # Подтест 3 - максимум
        arr = [rnd1, rnd2, rnd3]
        min_rnd = max(arr)
        self.assertEqual(min_rnd.avg(), +3.0)

        # Подтест 4 - модуль
        self.assertEqual(not (rnd1.abs() != rnd1), True)
        rnd3.abs()
        self.assertEqual(rnd3.avg(), +1.5)

        # Подтест 5 - максимальная вероятность
        self.assertEqual(rnd2.max_prob(), 4.0)
        self.assertEqual(rnd4.max_prob(), 10.0)
        self.assertEqual(rnd5.max_prob(), None)

        # Подтест 6 - минимальная вероятность
        self.assertEqual(rnd2.min_prob(), 1.0)
        self.assertEqual(rnd4.min_prob(), 10.0)
        self.assertEqual(rnd5.min_prob(), None)

        # Подтест 7 - вторая по величине максимальная вероятность
        self.assertEqual(rnd2.max2_prob(), 3.0)
        self.assertEqual(rnd4.max2_prob(), 10.0)
        self.assertEqual(rnd5.max2_prob(), None)

        # Подтест 8 - вторая по величине минимальная вероятность
        self.assertEqual(rnd2.min2_prob(), 2.0)
        self.assertEqual(rnd4.min2_prob(), 10.0)
        self.assertEqual(rnd5.min2_prob(), None)

    def test_proba_build_scalar(self):
        """
        Тест конвертации ДСВ-величины в скаляр
        """
        rnd = proba.ProbA()
        rnd.append_value(1.0, 0.1)
        rnd.append_value(2.0, 0.2)
        rnd.append_value(3.0, 0.3)
        rnd.append_value(4.0, 0.4)

        # Подтест 1 - ошибка
        # rnd.build_scalar_mode = "trash"
        # self.assertEqual(rnd.build_scalar(), None)

        # Подтест 2 - среднее
        rnd.build_scalar_mode = "avg"
        self.assertEqual(rnd.build_scalar(), 3.0)

        # Подтест 3 - максимум
        rnd.build_scalar_mode = "max"
        self.assertEqual(rnd.build_scalar(), 4.0)

        # Подтест 4 - минимум
        rnd.build_scalar_mode = "min"
        self.assertEqual(rnd.build_scalar(), 1.0)

        # Подтест 5 - средний максимум
        rnd.build_scalar_mode = "max_avg"
        self.assertEqual(rnd.build_scalar(), 3.5)

        # Подтест 6 - средний минимум
        rnd.build_scalar_mode = "min_avg"
        self.assertEqual(rnd.build_scalar(), 1.5)
