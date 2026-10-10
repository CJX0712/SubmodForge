"""惰性随机贪心 (Lazy + Stochastic 组合).

作者: 晨星

在随机采样候选集内做惰性评估: 用堆维护采样候选的边际上界, 仅在堆顶重算。
兼顾 O(n log k) 复杂度与惰性求值加速。
"""
import heapq
import random
from core.types import SubmodularFunction
from core.seed import RNG
from core.errors import E300ConstraintInfeasible

_TOL = 1e-12


def lazy_stochastic_greedy(func: SubmodularFunction, k: int, eps: float = 0.1, rng=None):
    rng = rng or RNG()
    if k < 0:
        raise E300ConstraintInfeasible("k 必须 >= 0")
    V = func.V
    n = len(V)
    m = max(1, int(k / eps))
    selected = []
    selected_set = set()
    while len(selected) < k:
        cand = rng.sample(V, min(m, n - len(selected)))
        cand = [e for e in cand if e not in selected_set]
        if not cand:
            break
        gain = {}
        pq = []
        for e in cand:
            g = func.marginal(selected_set, e)
            gain[e] = g
            heapq.heappush(pq, (-g, e))
        while pq:
            neg_g, e = heapq.heappop(pq)
            stored = -neg_g
            if stored != gain[e]:
                continue
            true_g = func.marginal(selected_set, e)
            if true_g < stored - _TOL:
                gain[e] = true_g
                heapq.heappush(pq, (-true_g, e))
                continue
            if true_g <= _TOL:
                break
            selected.append(e)
            selected_set.add(e)
            break
        else:
            break
    return selected, func.value(selected_set)


class LazyStochasticGreedy:
    name = "LazyStochasticGreedy"

    def run(self, func, k, eps=0.1, rng=None, **kw):
        return lazy_stochastic_greedy(func, k, eps=eps, rng=rng)
