# pylint: disable=too-many-locals
"""
:file: Модуль с описанием класса отчетов
"""
import json
import pandas as pd  # pylint: disable=E0401


class Report:
    """
    Класс с описанием отчета
    """
    def __init__(self, data):
        """
        Конструктор
        :param data: данные для отчета
        """
        self.data = data

    def build_report(self):
        # pylint: disable=too-many-branches
        """
        Формирует отчет
        :return: Отчет (когнитивная карта + сценарий моделирования) в формате JSON, 
        Pandas.DataFrame с данными по импульсному моделированию когнитивной карты из отчета
        """
        scenarios = []
        impulses = []
        if self.data.impulses is not None:
            for i, impulse in enumerate(self.data.impulses.imp):
                if isinstance(impulse, (float, int)):
                    val = impulse
                else:
                    val = impulse.build_scalar()
                impulses.append({"val": val, "v": self.data.impulses.v_imp[i].id_, "step": 1})
        scenario = {"impulses": impulses, "name": "scenario1", "id": 1670668256870,
                    "indicators": [self.data.cogmap.y[i].id_ \
                                   for i in range(len(self.data.cogmap.y))]}
        scenarios.append(scenario)
        edges = []
        for e in self.data.cogmap.edges:
            if isinstance(e.value, (float, int)):
                edges.append({"id": e.id_, "weight": e.value, "v1": e.v1_id,
                              "v2": e.v2_id, "shortName": e.name,
                              "formula": e.formula, "md": e.md, "color": e.color})
            else:
                weight = e.value.build_scalar()
                edges.append({"id": e.id_, "weight": weight, "v1": e.v1_id,
                              "v2": e.v2_id, "shortName": e.name,
                              "formula": e.formula, "md": e.md, "color": e.color})
        vertices = []
        for v in self.data.cogmap.vertices:
            if isinstance(v.value, (float, int)):
                val = v.value
            else:
                val = v.value.build_scalar()
            if isinstance(v.growth, (float, int)):
                grow = v.growth
            else:
                grow = v.growth.build_scalar()
            vertices.append({"id": v.id_, "value": val,
                             "fullName": v.name, "shortName": v.short_name,
                             "color": v.color, "show": v.show, "growth": grow, 
                             "x": v.x, "y": v.y})

        target_vertices = []
        for v in self.data.target_vertices:
            target_vertices.append({"id": v.id_, "fullName": v.name})

        bad_vertices = []
        for v in self.data.bad_vertices:
            bad_vertices.append({"id": v.id_, "fullName": v.name})

        modeling_results = {
            "added_new_vertices": self.data.added_new_vertices,
            "target_vertices": target_vertices,
            "bad_vertices": bad_vertices,
            "y_max_er": self.data.y_max_er.build_scalar()
        }

        j = {
            "MapTitle": self.data.cogmap.cognimod_map_title,
            "ModelingResults": modeling_results,
            "Settings": self.data.cogmap.cognimod_settings,
            "Scenarios": scenarios,
            "Vertices": vertices,
            "Edges": edges
        }

        for ii, row in enumerate(self.data.cogmap.pulse_calc_log):
            for jj, item in enumerate(row):
                self.data.cogmap.pulse_calc_log[ii][jj] = item.build_scalar()

        c = pd.DataFrame(data=self.data.cogmap.pulse_calc_log,
                         columns=[v.id_ for v in self.data.cogmap.vertices])
        return j, c

    def save_to_file(self, filename):
        """
        Записывает отчет в файлы
        :param filename: имя файла для когнитивной карты (JSON)
        :return:
        """
        r, c = self.build_report()
        with open(filename, "w", encoding="cp1251") as f:
            json.dump(r, f, indent=4, ensure_ascii=False)
        c.to_csv(filename+".csv")
