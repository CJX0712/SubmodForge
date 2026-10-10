"""集合覆盖子模函数 (Set Cover).

作者: 晨星

给定每个元素 e 覆盖的元素集合 cover[e], 权重 w[item]:
    f(S) = Σ_{item ∈ ∪_{e∈S} cover[e]} w[item]

单调子模函数。
"""
from core.types import SubmodularFunction
from core.errors import E100InvalidInput


class SetCover(SubmodularFunction):
    def __init__(self, cover, weights=None):
        """
        cover: dict e -> iterable of covered items
        weights: dict item -> weight (默认 1.0)
        """
        if not hasattr(cover, "items"):
            raise E100InvalidInput("cover 必须是 dict (e -> covered items)")
        self.cover = {e: set(c) for e, c in cover.items()}
        all_items = set()
        for c in self.cover.values():
            all_items |= c
        if weights is None:
            self.weights = {it: 1.0 for it in all_items}
        else:
            self.weights = {it: float(weights.get(it, 1.0)) for it in all_items}
        super().__init__(sorted(self.cover.keys(), key=str))

    def _value(self, S):
        covered = set()
        for e in S:
            covered |= self.cover[e]
        return sum(self.weights[it] for it in covered)
