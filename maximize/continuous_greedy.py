"""连续贪心最大化 (Calinescu, Chekuri, Pál & Vondrák, 2011) — Frank-Wolfe 视角.

作者: 晨星

对单调子模函数在基数约束 (matroid) 下, 在分数域做连续贪心:
    x ← 0; 重复 T 步: x ← x + (1/T)·e*,  e* = argmax_i [F(x + (1/T)e_i) - F(x)]
其中 F 为 Lovász 扩展。最终取整选 top-k。

理论保证: E[value] >= (1 - 1/e - O(1/T)) · OPT。
"""
from core.types import SubmodularFunction
from core.errors import E300ConstraintInfeasible


def continuous_greedy(func: SubmodularFunction, k: int, T: int = None):
    """连续贪心 (Frank-Wolfe)。返回 (selected_list, objective_value)。"""
    if k < 0:
        raise E300ConstraintInfeasible("k 必须 >= 0")
    n = len(func.V)
    if k == 0:
        return [], 0.0
    T = T if T is not None else max(50, k * 10)
    idx = {e: i for i, e in enumerate(func.V)}
    x = [0.0] * n

    def lovasz(x):
        # F(x) = Σ_i x_{π_i} (f(prefix_{≤i}) - f(prefix_{<i})), π 按 x 降序
        order = sorted(range(n), key=lambda i: x[i], reverse=True)
        prev = 0.0
        total = 0.0
        S = set()
        for i in order:
            S.add(func.V[i])
            cur = func.value(S)
            total += x[i] * (cur - prev)
            prev = cur
        return total

    Fx = lovasz(x)
    step = 1.0 / T
    for _ in range(T):
        best_i, best_gain = 0, -1e18
        for i in range(n):
            xi = x[i]
            x[i] = xi + step
            gain = lovasz(x) - Fx
            x[i] = xi
            if gain > best_gain:
                best_gain = gain
                best_i = i
        x[best_i] += step
        Fx = lovasz(x)
    order = sorted(range(n), key=lambda i: x[i], reverse=True)
    selected = [func.V[i] for i in order[:k]]
    return selected, func.value(set(selected))


class ContinuousGreedy:
    name = "ContinuousGreedy"

    def run(self, func, k, T=None, **kw):
        return continuous_greedy(func, k, T=T)
