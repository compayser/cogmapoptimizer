# pylint: disable=too-many-locals, too-few-public-methods
"""
:file: Модуль с описанием класса для генерации воздействий
"""
from typing import List
import numpy as np
from keras.models import load_model  # pylint: disable=E0401
import proba
import cogmap as cm


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
        for i, delta in enumerate(value_deltas):
            compact_matrix[i, i] = delta
        m = np.array(compact_matrix).ravel()

        growths = [v.growth for v in cogmap.vertices]
        growths.extend(np.zeros(32 - len(growths)))

        data = []
        data.extend(m)
        data.extend(np.zeros((32 ** 2) - len(m)))

        data_ = []
        for _, item in enumerate(data):
            if isinstance(item, proba.ProbA):
                data_.append(item.build_scalar())
            else:
                data_.append(item)
        data = data_

        all_impulses_sum = self.model.predict([data], verbose=0)
        growths_ = []
        for _, item in enumerate(growths):
            if isinstance(item, proba.ProbA):
                growths_.append(item.build_scalar())
            else:
                growths_.append(item)
        growths = growths_
        all_impulses = np.array(all_impulses_sum[0]) - np.array(growths)
        res_impulses = []
        for v in v_lst:
            res_impulses.append(all_impulses[cogmap.vertex_idx_by_id(v.id_)])
        return res_impulses
