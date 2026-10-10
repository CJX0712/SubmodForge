"""SubmodForge 类型契约 (Protocol / ABC).

作者: 晨星
"""
from abc import ABC, abstractmethod
from typing import Collection, List, Tuple, Protocol, runtime_checkable


class SubmodularFunction(ABC):
    """子模函数值预言机 (value oracle) 基类.

    约定:
        - ``value(S)`` 返回集合 S 的函数值, 带缓存.
        - 子类必须实现 ``_value(S: set) -> float``.
        - 边际增益 ``marginal(S, e) = value(S ∪ {e}) - value(S)``.
        - ``is_submodular()`` 提供随机化 diminishing-returns 校验.
    """

    def __init__(self, ground_set):
        self.V = list(ground_set)
        self._cache: dict = {}

    def value(self, S: Collection) -> float:
        key = frozenset(S)
        if key not in self._cache:
            self._cache[key] = float(self._value(set(key)))
        return self._cache[key]

    @abstractmethod
    def _value(self, S: set) -> float:
        ...

    def marginal(self, S: Collection, e) -> float:
        S = set(S)
        if e in S:
            return 0.0
        return self.value(S | {e}) - self.value(S)

    def is_submodular(self, samples: int = 200, tol: float = 1e-9, rng=None) -> Tuple[bool, object]:
        """随机化子模性校验.

        子模性 (diminishing returns): 对任意 A ⊆ B ⊆ V, e ∉ B:
            f(A ∪ {e}) - f(A) ≥ f(B ∪ {e}) - f(B)

        返回 (is_submodular, counterexample_or_None).
        """
        import random as _r

        rng = rng or _r
        V = self.V
        n = len(V)
        for _ in range(samples):
            sa = rng.randint(0, n)
            A = set(rng.sample(V, sa))
            remain = [x for x in V if x not in A]
            sb = rng.randint(0, len(remain))
            B = A | set(rng.sample(remain, sb))
            cand = [x for x in V if x not in B]
            if not cand:
                continue
            e = rng.choice(cand)
            da = self.marginal(A, e)
            db = self.marginal(B, e)
            if da < db - tol:
                return False, (sorted(A), sorted(B), e, da, db)
        return True, None


@runtime_checkable
class Maximizer(Protocol):
    """最大化算法契约."""

    name: str

    def run(self, func: SubmodularFunction, k: int, **kw) -> Tuple[List, float]:
        """返回 (selected_list, objective_value)."""
        ...
