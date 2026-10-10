"""图割子模函数 (Graph Cut).

作者: 晨星

f(S) = Σ_{i ∈ S, j ∉ S} w(i, j)

对称子模函数 (f(S) = f(V\\S)), 一般非单调。
是子模函数最小化 (SFM) 的标准测试函数 (Queyranne 算法即针对对称子模函数)。
"""
from core.types import SubmodularFunction
from core.errors import E100InvalidInput


class GraphCut(SubmodularFunction):
    def __init__(self, weights):
        """
        weights: dict {(i, j): w} 或 list[((i,j), w)]; 自动对称化, 非负。
        """
        self._w = {}
        try:
            items = weights.items() if hasattr(weights, "items") else iter(weights)
        except TypeError:
            raise E100InvalidInput("weights 必须是 dict 或可迭代序列")
        ground = set()
        for (i, j), w in items:
            w = float(w)
            if w < 0:
                raise E100InvalidInput("边权重必须非负")
            self._w[(i, j)] = w
            self._w[(j, i)] = w
            ground.add(i)
            ground.add(j)
        super().__init__(sorted(ground, key=str))

    def _value(self, S):
        S = set(S)
        total = 0.0
        for (i, j), w in self._w.items():
            if (i in S) != (j in S):  # 恰好一端在 S 内
                total += w
        # 每条边被 (i,j) 和 (j,i) 各计一次 -> 除以 2
        return total / 2.0
