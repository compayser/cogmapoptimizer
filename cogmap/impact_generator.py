import proba
import numpy as np
import cogmap as cm
from typing import List
from keras.models import load_model


class ImpactData:
    """ Описывает данные воздействий """
    def __init__(self, cogmap, impulses, y_max_er):
        """
        Конструктор
        :param cogmap: когнитивная карта
        :param impulses: данные о воздействии
        :param y_max_er: ошибка в целевых вершинах при воздействии на когнитивную карту
        """
        self.cogmap = cogmap
        self.impulses = impulses
        self.y_max_er = y_max_er


class ImpactGenerator:
    """ Генератор воздействий """
    def __init__(self, filename="model.h5"):
        """
        Конструктор
        :param filename: имя файла нейросети
        """
        self.impacts = []
        self.model = load_model(filename)

    def add_impact(self, impact: ImpactData):
        """
        Добавляет воздействие в рестроспективу воздействий
        :param impact: данные о воздействии
        :return:
        """
        self.impacts.append(impact)

    def get_impact(self, cogmap, v_lst: List[cm.Vertex], n: int):
        """
        Возвращает воздействие для заданной КК и вершин
        cogmap - когнитивная карта
        :param cogmap: когнитивная карта
        :param v_lst: список вершин для формирования воздействия
        :param n: число шагов когнитивного моделирования
        :return: список значений для воздействия
        """
        value_deltas = cogmap.pulse_model_nn(n)
        compact_matrix = cogmap.matrix[:, :]
        for i in range(len(value_deltas)):
            compact_matrix[i, i] = value_deltas[i]
        m = np.array(compact_matrix).ravel()

        growths = [v.growth for v in cogmap.vertices]
        growths.extend(np.zeros(32 - len(growths)))

        data = []
        data.extend(m)
        data.extend(np.zeros((32 ** 2) - len(m)))

        data_ = []
        for i in range(len(data)):
            if isinstance(data[i], proba.ProbA):
                data_.append(data[i].build_scalar())
            else:
                data_.append(data[i])
        data = data_

        all_impulses_sum = self.model.predict([data])
        growths_ = []
        for i in range(len(growths)):
            if isinstance(growths[i], proba.ProbA):
                growths_.append(growths[i].build_scalar())
            else:
                growths_.append(growths[i])
        growths = growths_
        all_impulses = np.array(all_impulses_sum[0]) - np.array(growths)
        res_impulses = []
        for v in v_lst:
            res_impulses.append(all_impulses[cogmap.vertex_idx_by_id(v.id)])
        return res_impulses
