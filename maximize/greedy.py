"""标准贪心最大化 (cardinality constraint k).

作者: 晨星

单调子模函数在基数约束 k 下, 贪心达到 (1 - 1/e) ≈ 0.632 的最优近似 (紧界)。
"""
from core.types import SubmodularFunction
from core.errors import E300ConstraintInfeasible

_TOL = 1e-12


def greedy(func: SubmodularFunction, k: int, S_init=None):
    """贪心选择 k 个元素。返回 (selected_list, objective_value)。

    S_init: 可选已选集合 (计入 k 额度)。
    """
    if k < 0:
        raise E300ConstraintInfeasible("k 必须 >= 0")
    selected = list(S_init) if S_init else []
    if len(selected) > k:
        raise E300ConstraintInfeasible("S_init 已超出 k")
    selected_set = set(selected)
    while len(selected) < k:
        best_e, best_gain = None, -float("inf")
        for e in func.V:
            if e in selected_set:
                continue
            g = func.marginal(selected_set, e)
            if g > best_gain:
                best_gain = g
                best_e = e
        if best_e is None or best_gain <= _TOL:
            break
        selected.append(best_e)
        selected_set.add(best_e)
    return selected, func.value(selected_set)


class Greedy:
    name = "Greedy"

    def run(self, func, k, **kw):
        return greedy(func, k)
