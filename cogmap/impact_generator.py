import numpy as np
import cogmap as cm


class ImpactData:
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
    def __init__(self):
        """
        Конструктор
        """
        self.impacts = []

    def add_impact(self, impact: ImpactData):
        """
        Добавляет воздействие в рестроспективу воздействий
        :param impact: данные о воздействии
        :return:
        """
        self.impacts.append(impact)

    def get_impact(self, cogmap, V: list[cm.Vertex]):
        """
        Возвращает воздействие для заданной КК и вершин
        cogmap - когнитивная карта
        :param cogmap: когнитивная карта
        :param V: список вершин для формирования воздействия
        :return: список значений для воздействия
        """
        return np.zeros(len(V), dtype = float)
