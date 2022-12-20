import numpy as np
import cogmap as cm


class ImpactData:
    def __init__(self, cogmap, impulses, y_max_er):
        self.cogmap = cogmap
        self.impulses = impulses
        self.y_max_er = y_max_er


class ImpactGenerator:
    def __init__(self):
        self.impacts = []

    def add_impact(self, impact: ImpactData):
        self.impacts.append(impact)

    def get_impact(self, cogmap, V: list[cm.Vertex]):
        return np.zeros(len(V), dtype = float)
