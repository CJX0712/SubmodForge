"""惰性贪心最大化 (Minoux, 1978).

作者: 晨星

维护每个元素边际增益的上界 (priority queue), 仅当元素位于堆顶时才重新计算,
从而将求值次数从 O(nk) 降到接近 O(n log k), 且与标准贪心返回**相同目标值**。
"""
import heapq
from core.types import SubmodularFunction

_TOL = 1e-12


def lazy_greedy(func: SubmodularFunction, k: int):
    """惰性贪心。返回 (selected_list, objective_value), 目标值等于 greedy()。"""
    if k < 0:
        raise ValueError("k 必须 >= 0")
    selected = []
    selected_set = set()
    gain = {}
    idx_of = {e: i for i, e in enumerate(func.V)}  # 与 greedy 一致的平局打破 (首个索引优先)
    pq = []
    for e in func.V:
        g = func.marginal(selected_set, e)  # 初始上界 = 相对空集的边际
        gain[e] = g
        heapq.heappush(pq, (-g, idx_of[e], e))
    while len(selected) < k and pq:
        neg_g, _, e = heapq.heappop(pq)
        stored = -neg_g
        if stored != gain[e]:
            # 过期条目 (已有更新的 gain 入堆), 跳过
            continue
        true_g = func.marginal(selected_set, e)
        if true_g < stored - _TOL:
            # 上界过期, 用真实值更新后重新入堆
            gain[e] = true_g
            heapq.heappush(pq, (-true_g, idx_of[e], e))
            continue
        if true_g <= _TOL:
            break
        selected.append(e)
        selected_set.add(e)
    return selected, func.value(selected_set)


class LazyGreedy:
    name = "LazyGreedy"

    def run(self, func, k, **kw):
        return lazy_greedy(func, k)
