"""模函数上的凹函数 (Concave over Modular).

作者: 晨星

f(S) = Σ_{j=1..m} g( Σ_{i ∈ S} w_{ij} )

其中 g 为凹函数。凹函数复合模函数得到子模函数 (Bach, 2010)。
g 递增凹 -> 单调子模; g 非单调 -> 非单调子模 (适合 SFM 演示)。
默认 g(x) = sqrt(x) (单调)。
"""
import math
from core.types import SubmodularFunction
from core.errors import E100InvalidInput


def _default_concave(x):
    return math.sqrt(max(x, 0.0))


class ConcaveOverModular(SubmodularFunction):
    def __init__(self, modular_weights, concave_fn=None):
        """
        modular_weights: dict e -> list[float] (每个特征 j 的权重 w_{ej})
        concave_fn: 凹函数 g (默认 sqrt)
        """
        if not hasattr(modular_weights, "items"):
            raise E100InvalidInput("modular_weights 必须是 dict (e -> [w_j, ...])")
        self.W = {e: list(map(float, w)) for e, w in modular_weights.items()}
        dims = {len(w) for w in self.W.values()}
        if len(dims) != 1:
            raise E100InvalidInput("所有权重向量必须同维")
        self.m = dims.pop()
        self.g = concave_fn if concave_fn is not None else _default_concave
        super().__init__(sorted(self.W.keys(), key=str))

    def _value(self, S):
        s = [0.0] * self.m
        for e in S:
            w = self.W[e]
            for j in range(self.m):
                s[j] += w[j]
        return sum(self.g(sj) for sj in s)
