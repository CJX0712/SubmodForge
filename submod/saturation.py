"""饱和覆盖子模函数 (Saturation / Disparate Coverage).

作者: 晨星

用于数据摘要与公平摘要 (Ahmed et al., 2017)。每个元素属于一个主题 topic[e]。
    f(S) = Σ_{topic t} min(1, count_t(S))

单调子模函数; 当某主题已达饱和 (>=1) 后边际增益递减为 0。
"""
from core.types import SubmodularFunction
from core.errors import E100InvalidInput


class SaturationCoverage(SubmodularFunction):
    def __init__(self, topic_of, cap=1.0):
        """
        topic_of: dict e -> topic (任意可哈希)
        cap: 每个主题的饱和上限 (默认 1.0)
        """
        if not hasattr(topic_of, "items"):
            raise E100InvalidInput("topic_of 必须是 dict (e -> topic)")
        self.topic_of = dict(topic_of)
        self.cap = float(cap)
        if self.cap <= 0:
            raise E100InvalidInput("cap 必须 > 0")
        super().__init__(sorted(self.topic_of.keys(), key=str))

    def _value(self, S):
        counts = {}
        for e in S:
            t = self.topic_of[e]
            counts[t] = counts.get(t, 0) + 1
        return sum(min(self.cap, c) for c in counts.values())
