"""独立级联影响力传播子模函数 (Influence Maximization, IC model).

作者: 晨星

f(S) = E[ 在独立级联模型下从种子集 S 激活的节点数 ]

单调子模函数 (Kempe, Kleinberg & Tardos, 2003)。
期望通过蒙特卡洛模拟估计; 使用固定种子的 Random 保证可复现。
"""
import random
from core.types import SubmodularFunction
from core.errors import E100InvalidInput


class InfluenceIC(SubmodularFunction):
    def __init__(self, graph, samples=200, seed=0):
        """
        graph: dict node -> list of (neighbor, prob)
        samples: 蒙特卡洛采样数 (影响 f 估计精度与运行时间)
        seed: 固定的随机种子 (保证确定性)
        """
        if not hasattr(graph, "items"):
            raise E100InvalidInput("graph 必须是 dict (node -> [(neighbor, prob), ...])")
        self.graph = {u: [(v, float(p)) for v, p in nbrs] for u, nbrs in graph.items()}
        self.samples = int(samples)
        if self.samples < 1:
            raise E100InvalidInput("samples 必须 >= 1")
        self.rng = random.Random(int(seed))
        ground = set(self.graph.keys())
        for nbrs in self.graph.values():
            for v, _ in nbrs:
                ground.add(v)
        super().__init__(sorted(ground, key=str))

    def _spread_once(self, S):
        active = set(S)
        frontier = set(S)
        while frontier:
            nxt = set()
            for u in frontier:
                for v, p in self.graph.get(u, []):
                    if v not in active and self.rng.random() < p:
                        active.add(v)
                        nxt.add(v)
            frontier = nxt
        return len(active)

    def _value(self, S):
        S = set(S)
        if not S:
            return 0.0
        total = 0
        for _ in range(self.samples):
            total += self._spread_once(S)
        return total / self.samples
