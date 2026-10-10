"""对数行列式特征选择子模函数 (Log-Det Feature Selection).

作者: 晨星

f(S) = log det( I + Σ_{i ∈ S} v_i v_iᵀ )

经典单调子模函数, 用于贪心式最优特征选择 (Krause & Golovin, 2014)。
纯 Python 实现的 Cholesky 对数行列式 (零依赖, 维度 d 建议 <= 32)。
"""
import math
from core.types import SubmodularFunction
from core.errors import E100InvalidInput


def _logdet_cholesky(M):
    """对正定矩阵 M 计算 log det 的 Cholesky 法 (数值稳定, 避免 det 溢出)."""
    n = len(M)
    L = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            s = M[i][j]
            for k in range(j):
                s -= L[i][k] * L[j][k]
            if i == j:
                if s <= 0:
                    # I + Σ vvᵀ 必为正定; 仅防御浮点负零
                    s = max(s, 1e-15)
                L[i][j] = math.sqrt(s)
            else:
                L[i][j] = s / L[j][j]
    return 2.0 * sum(math.log(L[i][i]) for i in range(n))


class LogDetFeatureSelection(SubmodularFunction):
    def __init__(self, features):
        """
        features: dict e -> d 维向量 (list[float])。
        每个元素 e 是一个 d 维样本/特征向量。
        """
        if not hasattr(features, "items"):
            raise E100InvalidInput("features 必须是 dict (e -> vector)")
        self.X = {e: list(map(float, v)) for e, v in features.items()}
        dims = {len(v) for v in self.X.values()}
        if len(dims) != 1:
            raise E100InvalidInput("所有向量必须同维")
        self.d = dims.pop()
        super().__init__(sorted(self.X.keys(), key=str))

    def _value(self, S):
        # M = I + Σ_{e∈S} v_e v_eᵀ
        M = [[1.0 if i == j else 0.0 for j in range(self.d)] for i in range(self.d)]
        for e in S:
            v = self.X[e]
            for i in range(self.d):
                vi = v[i]
                if vi == 0.0:
                    continue
                row = M[i]
                for j in range(self.d):
                    row[j] += vi * v[j]
        return _logdet_cholesky(M)
