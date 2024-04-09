# -*- coding: latin-1 -*-
import json
import proba

class Edge:
    """???????? ????? ??????????? ?????"""
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

class Vertex:
    """????????? ??????? ??????????? ?????"""
    __slots__ = ("id", "value", "min", "max", "impulse", "name", "idx", "short_name", "color", "show", "growth", "x", "y")

    def __init__(self, id: int, value: proba.ProbA, min: float, max: float, impulse: float, name: str):
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
        self.impulse = impulse
        self.name = name
        self.idx = -1  # ???????????? ? ??????
        self.short_name = ""
        self.color = "0x808080ff"
        self.show = "false"
        self.growth = 0.0
        self.x = 0.0
        self.y = 0.0

def fill_from_json(data, data_xyz):
    """
    ????????? ?????? ??????????? ????? ?? ?????? ? ??????? JSON.
    :param data: ???????? ??????????? ?????
    :param data_xyz: ???????? ????? ?????? ??????????? ?????
    :return:
    """
    X = []
    Y = []
    Z = []

    V, E = [], []
    json_content = json.loads(data)
    json_xyz_content = json.loads(data_xyz)
    cognimod_settings = json_content["Settings"]
    cognimod_map_title = json_content["MapTitle"]
    json_vertices = json_content["Vertices"]
    for v in json_vertices:
        v_id = 0
        v_value = proba.ProbA()
        v_min = 0.0
        v_max = 0.0
        v_impulse = 0.0
        v_name = ""

        v_short_name = ""
        v_color = ""
        v_show = ""
        v_growth = 0.0
        v_x = 0.0
        v_y = 0.0

        rnd_val = -1
        rnd_prob = -1
        for item in v.items():
            item_split = item[0].split('-')
            print(f'item = {item}')
            if item_split[0] == "id":
                v_id = item[1]
            elif item_split[0] == "value":
                print(f'item_split = {item_split}')
                rnd_val = float(item[1])
                print(f'set rnd_val = {rnd_val}')
                if rnd_val != -1 and rnd_prob != -1:
                    v_value.append_value(rnd_val, rnd_prob)
                    print(f'add1 {rnd_val}, {rnd_prob}')
                    rnd_val = -1
                    rnd_prob = -1
            elif item_split[0] == "prob":
                print(f'item_split = {item_split}')
                rnd_prob = float(item[1])
                print(f'set rnd_prob = {rnd_prob}')
                if rnd_val != -1 and rnd_prob != -1:
                    v_value.append_value(rnd_val, rnd_prob)
                    print(f'add2 {rnd_val}, {rnd_prob}')
                    rnd_val = -1
                    rnd_prob = -1
            elif item_split[0] == "min":
                v_min = float(item[1])
            elif item_split[0] == "max":
                v_max = float(item[1])
            elif item_split[0] == "impulse":
                v_impulse = float(item[1])
            elif item_split[0] == "fullName":
                v_name = item[1]
            elif item_split[0] == "shortName":
                v_short_name = item[1]
            elif item_split[0] == "color":
                v_color = item[1]
            elif item_split[0] == "show":
                v_show = item[1]
            elif item_split[0] == "growth":
                v_growth = float(item[1])
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
        for i in range(0, len(v_value.vals)):
            print(f'i={i} v_value.vals[{i}] = {v_value.vals[i].value}, {v_value.vals[i].prob}')
        print("---")

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
            if item[0] == "id":
                e_id = item[1]
            elif item_split[0] == "weight":
                rnd_val = float(item[1])
                if rnd_val != -1 and rnd_prob != -1:
                    e_weight.append_value(rnd_val, rnd_prob)
                    print(f'add3 {rnd_val}, {rnd_prob}')
                    rnd_val = -1
                    rnd_prob = -1
            elif item_split[0] == "prob":
                print(f' >>>  {item}')
                rnd_prob = float(item[1])
                if rnd_val != -1 and rnd_prob != -1:
                    e_weight.append_value(rnd_val, rnd_prob)
                    print(f'add4 {rnd_val}, {rnd_prob}')
                    rnd_val = -1
                    rnd_prob = -1
            elif item[0] == "v1":
                e_v1 = item[1]
            elif item[0] == "v2":
                e_v2 = item[1]
            elif item[0] == "shortName":
                e_shortName = item[1]
            elif item[0] == "formula":
                e_formula = item[1]
            elif item[0] == "md":
                e_md = item[1]
            elif item[0] == "color":
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
                    v.impulse = imp_val
                    break
    json_xyz = json_xyz_content["Groups"]
    for xyz_item in json_xyz:
        vertex_id = xyz_item["id"]
        vertex_group = xyz_item["type"]
        for v in V:
            if v.id == vertex_id:
                if vertex_group == "X":
                    X.append(v)
                elif vertex_group == "Y":
                    Y.append(v)
                    v.min = xyz_item["min"]
                    v.max = xyz_item["max"]
                elif vertex_group == "Z":
                    Z.append(v)
                break
    vertices = V
    edges = E
    matrix = None
    edge_ids = []
    vertex_ids = []

if __name__ == '__main__':
    print("Loading config...")
    with open("test.cmj", "r") as config_file:
        cogmap_json = config_file.read()
    with open("test.cmj_xyz", "r") as config_xyz_file:
        cogmap_xyz_json = config_xyz_file.read()

    fill_from_json(cogmap_json, cogmap_xyz_json)





