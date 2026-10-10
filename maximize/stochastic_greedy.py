"""随机贪心最大化 (Mirzasoleiman et al., 2015).

作者: 晨星

每步从随机采样的 min(n, k/eps) 个候选中选边际增益最大者。
理论保证: E[value] >= (1 - 1/e - eps) * OPT, 复杂度 O(n log k)。
"""
import random
from core.types import SubmodularFunction
from core.seed import RNG
from core.errors import E300ConstraintInfeasible

_TOL = 1e-12


def stochastic_greedy(func: SubmodularFunction, k: int, eps: float = 0.1, rng=None):
    """随机贪心。返回 (selected_list, objective_value)。"""
    if k < 0:
        raise E300ConstraintInfeasible("k 必须 >= 0")
    if not (0.0 < eps < 1.0):
        raise ValueError("eps 必须位于 (0, 1)")
    rng = rng or RNG()
    V = func.V
    n = len(V)
    selected = []
    selected_set = set()
    m = max(1, int(k / eps))
    while len(selected) < k:
        cand = rng.sample(V, min(m, n - len(selected)))
        cand = [e for e in cand if e not in selected_set]
        if not cand:
            break
        best_e, best_g = None, -float("inf")
        for e in cand:
            g = func.marginal(selected_set, e)
            if g > best_g:
                best_g = g
                best_e = e
        if best_e is None or best_g <= _TOL:
            break
        selected.append(best_e)
        selected_set.add(best_e)
    return selected, func.value(selected_set)


class StochasticGreedy:
    name = "StochasticGreedy"

    def run(self, func, k, eps=0.1, rng=None, **kw):
        return stochastic_greedy(func, k, eps=eps, rng=rng)
