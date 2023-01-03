import json
import cogmap as cm


class Report:
    def __init__(self, data):
        self.data = data

    def build_report(self):
        scenarios = []
        impulses = []
        for i in range(len(self.data.impulses.imp)):
            impulses.append({"val": self.data.impulses.imp[i], "v": self.data.impulses.v_imp[i].id})
        scenario = {"impulses": impulses}
        scenarios.append(scenario)
        edges = []
        for e in self.data.cogmap.edges:
            edges.append({"id": e.id, "weight": e.value, "v1": e.v1_id, "v2": e.v2_id, "shortName": e.name})
        vertices = []
        for v in self.data.cogmap.vertices:
            vertices.append({"id": v.id, "value": v.value, "fullName": v.name})

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
            "y_max_er": self.data.y_max_er
        }

        j = {
            "ModelingResults": modeling_results,
            "Scenarios": scenarios,
            "Vertices": vertices,
            "Edges": edges
        }
        return j

    def save_to_file(self, filename):
        r = self.build_report()
        with open(filename, 'w') as f:
            json.dump(r, f, indent=4)
