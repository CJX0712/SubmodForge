"""SubmodForge 子模最大化算法.

作者: 晨星

    Greedy            标准贪心 (1 - 1/e) 近似保证 (Nemhauser, Wolsey & Fisher, 1978)
    LazyGreedy        Minoux 惰性贪心, 同值更快
    StochasticGreedy  Mirzasoleiman 随机贪心, O(n log k) 复杂度
    LazyStochastic    惰性 + 随机组合
    ContinuousGreedy  Calinescu 连续贪心 (Frank-Wolfe), 分数解 (1 - 1/e)
"""
from .greedy import greedy, Greedy
from .lazy_greedy import lazy_greedy, LazyGreedy
from .stochastic_greedy import stochastic_greedy, StochasticGreedy
from .lazy_stochastic import lazy_stochastic_greedy, LazyStochasticGreedy
from .continuous_greedy import continuous_greedy, ContinuousGreedy
from .registry import ALL_MAXIMIZERS, run_all_maximizers

__all__ = [
    "greedy", "Greedy",
    "lazy_greedy", "LazyGreedy",
    "stochastic_greedy", "StochasticGreedy",
    "lazy_stochastic_greedy", "LazyStochasticGreedy",
    "continuous_greedy", "ContinuousGreedy",
    "ALL_MAXIMIZERS", "run_all_maximizers",
]
