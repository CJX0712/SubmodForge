"""暴力枚举 (仅用于小规模测试 / 基线对照).

作者: 晨星
"""
import itertools


def _all_sets(V):
    V = list(V)
    for r in range(len(V) + 1):
        for combo in itertools.combinations(V, r):
            yield frozenset(combo)


def brute_force_min(func, V=None):
    """返回 (argmin_set, min_value). 仅适用于 n <= ~20."""
    if V is None:
        V = func.V
    best_S, best_v = frozenset(), func.value(frozenset())
    for S in _all_sets(V):
        v = func.value(S)
        if v < best_v - 1e-12:
            best_v = v
            best_S = S
    return best_S, best_v


def brute_force_max(func, k, V=None):
    """返回基数约束 k 下 (argmax_set, max_value). 仅适用于 n <= ~22."""
    if V is None:
        V = func.V
    best_S, best_v = None, -float("inf")
    for S in _all_sets(V):
        if len(S) != k:
            continue
        v = func.value(S)
        if v > best_v:
            best_v = v
            best_S = S
    return best_S, best_v
