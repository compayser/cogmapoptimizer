import json
import pandas as pd


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
        """
        Формирует отчет
        :return: Отчет (когнитивная карта + сценарий моделирования) в формате JSON, Pandas.DataFrame с данными
        по импульсному моделированию когнитивной карты из отчета
        """
        scenarios = []
        impulses = []
        if self.data.impulses is not None:
            for i in range(len(self.data.impulses.imp)):
                if isinstance(self.data.impulses.imp[i], float) or isinstance(self.data.impulses.imp[i], int):
                    val = self.data.impulses.imp[i]
                else:
                    val = self.data.impulses.imp[i].build_scalar()
                impulses.append({"val": val, "v": self.data.impulses.v_imp[i].id, "step": 1})
        scenario = {"impulses": impulses, "name": "scenario1", "id": 1670668256870,
                    "indicators": [self.data.cogmap.Y[i].id for i in range(len(self.data.cogmap.Y))]}
        scenarios.append(scenario)
        edges = []
        for e in self.data.cogmap.edges:
            if isinstance(e.value, float) or isinstance(e.value, int):
                edges.append({"id": e.id, "weight": e.value, "v1": e.v1_id, "v2": e.v2_id, "shortName": e.name,
                              "formula": e.formula, "md": e.md, "color": e.color})
            else:
                weight = e.value.build_scalar()
                edges.append({"id": e.id, "weight": weight, "v1": e.v1_id, "v2": e.v2_id, "shortName": e.name,
                              "formula": e.formula, "md": e.md, "color": e.color})
        vertices = []
        for v in self.data.cogmap.vertices:
            if isinstance(v.value, float) or isinstance(v.value, int):
                val = v.value
            else:
                val = v.value.build_scalar()
            if isinstance(v.growth, float) or isinstance(v.growth, int):
                grow = v.growth
            else:
                grow = v.growth.build_scalar()
            vertices.append({"id": v.id, "value": val, "fullName": v.name, "shortName": v.short_name,
                             "color": v.color, "show": v.show, "growth": grow, "x": v.x, "y": v.y})

        target_vertices = []
        for v in self.data.target_vertices:
            target_vertices.append({"id": v.id, "fullName": v.name})

        bad_vertices = []
        for v in self.data.bad_vertices:
            bad_vertices.append({"id": v.id, "fullName": v.name})

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

        for ii in range(len(self.data.cogmap.pulse_calc_log)):
            for jj in range(len(self.data.cogmap.pulse_calc_log[ii])):
                self.data.cogmap.pulse_calc_log[ii][jj] = self.data.cogmap.pulse_calc_log[ii][jj].build_scalar()

        c = pd.DataFrame(data=self.data.cogmap.pulse_calc_log, columns=[v.id for v in self.data.cogmap.vertices])
        return j, c

    def save_to_file(self, filename):
        """
        Записывает отчет в файлы
        :param filename: имя файла для когнитивной карты (JSON)
        :return:
        """
        r, c = self.build_report()
        with open(filename, 'w') as f:
            json.dump(r, f, indent=4, ensure_ascii=False)
        c.to_csv(filename+".csv")
