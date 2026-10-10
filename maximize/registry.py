"""最大化算法注册表.

作者: 晨星
"""
from core.types import SubmodularFunction
from .greedy import greedy, Greedy
from .lazy_greedy import lazy_greedy, LazyGreedy
from .stochastic_greedy import stochastic_greedy, StochasticGreedy
from .lazy_stochastic import lazy_stochastic_greedy, LazyStochasticGreedy
from .continuous_greedy import continuous_greedy, ContinuousGreedy

ALL_MAXIMIZERS = {
    "Greedy": (greedy, {"k": "k"}),
    "LazyGreedy": (lazy_greedy, {"k": "k"}),
    "StochasticGreedy": (stochastic_greedy, {"k": "k", "eps": "eps", "rng": "rng"}),
    "LazyStochasticGreedy": (lazy_stochastic_greedy, {"k": "k", "eps": "eps", "rng": "rng"}),
    "ContinuousGreedy": (continuous_greedy, {"k": "k", "T": "T"}),
}

CLASSES = {
    "Greedy": Greedy,
    "LazyGreedy": LazyGreedy,
    "StochasticGreedy": StochasticGreedy,
    "LazyStochasticGreedy": LazyStochasticGreedy,
    "ContinuousGreedy": ContinuousGreedy,
}


def run_all_maximizers(func: SubmodularFunction, k: int, eps=0.1, rng=None, T=None):
    """对给定函数运行全部最大化算法, 返回 {name: (selected, value)}。"""
    out = {}
    for name, (fn, _mapping) in ALL_MAXIMIZERS.items():
        if name == "StochasticGreedy" or name == "LazyStochasticGreedy":
            sel, val = fn(func, k, eps=eps, rng=rng)
        elif name == "ContinuousGreedy":
            sel, val = fn(func, k, T=T)
        else:
            sel, val = fn(func, k)
        out[name] = (sel, val)
    return out
