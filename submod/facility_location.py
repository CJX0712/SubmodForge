"""设施选址子模函数 (Facility Location).

作者: 晨星

f(S) = Σ_{v ∈ V} max_{s ∈ S} sim(v, s)

经典单调子模函数 (Krause & Golovin, 2014)。
相似度矩阵必须对称非负, 缺省为 0。
"""
from core.types import SubmodularFunction
from core.errors import E100InvalidInput


class FacilityLocation(SubmodularFunction):
    def __init__(self, sim):
        """sim: 可迭代的 ((i, j), weight) 或 dict {(i,j): w}。自动对称化."""
        self._sim = {}
        try:
            items = sim.items() if hasattr(sim, "items") else iter(sim)
        except TypeError:
            raise E100InvalidInput("sim 必须是 dict 或可迭代的 (pair, weight) 序列")
        ground = set()
        for pair, w in items:
            i, j = pair
            w = float(w)
            if w < 0:
                raise E100InvalidInput("相似度必须非负")
            self._sim[(i, j)] = w
            self._sim[(j, i)] = w
            ground.add(i)
            ground.add(j)
        super().__init__(sorted(ground, key=str))

    def _sim_lookup(self, i, j):
        if i == j:
            return 1.0
        return self._sim.get((i, j), 0.0)

    def _value(self, S):
        if not S:
            return 0.0
        total = 0.0
        for v in self.V:
            best = 0.0
            for s in S:
                sv = self._sim_lookup(v, s)
                if sv > best:
                    best = sv
            total += best
        return total
