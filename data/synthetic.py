"""合成数据生成器 (确定性, 可复现).

作者: 晨星

每个生成器返回可直接喂给 submod 模块的构造参数.
"""
import random
import math


def make_facility_location(n=60, dim=4, seed=0, sigma=1.0):
    """生成设施选址相似度矩阵. 返回 {(i,j): sim} (对称, 非负)."""
    rng = random.Random(seed)
    pts = [[rng.gauss(0, 1) for _ in range(dim)] for _ in range(n)]
    sim = {}
    for i in range(n):
        for j in range(i + 1, n):
            d2 = sum((pts[i][k] - pts[j][k]) ** 2 for k in range(dim))
            w = math.exp(-d2 / (2 * sigma * sigma))
            sim[(i, j)] = w
    return sim


def make_set_cover(n=40, m=8, vocab=60, seed=0):
    """生成集合覆盖. 每个元素覆盖 vocab 中的 m 个随机项. 返回 {e: set(items)}."""
    rng = random.Random(seed)
    cover = {}
    for e in range(n):
        cover[e] = set(rng.sample(range(vocab), m))
    return cover


def make_saturation(n_topics=6, per_topic=10, seed=0):
    """生成饱和覆盖数据. 返回 {e: topic}."""
    rng = random.Random(seed)
    topic_of = {}
    for t in range(n_topics):
        for _ in range(per_topic):
            e = rng.randint(0, 10 ** 9)
            topic_of[e] = t
    return topic_of


def make_logdet(n=30, d=8, seed=0):
    """生成对数行列式特征选择数据. 返回 {e: d 维向量}."""
    rng = random.Random(seed)
    return {e: [rng.gauss(0, 1) for _ in range(d)] for e in range(n)}


def make_influence(n=40, p=0.3, max_out=3, seed=0):
    """生成独立级联影响力网络. 返回 {node: [(neighbor, prob), ...]}."""
    rng = random.Random(seed)
    graph = {}
    for u in range(n):
        outs = rng.sample(range(n), min(max_out, n - 1))
        graph[u] = [(v, rng.random() * p) for v in outs if v != u]
    return graph


def make_graph_cut(n=12, p=0.5, seed=0):
    """生成图割权重. 返回 {(i,j): w} (对称, 非负)."""
    rng = random.Random(seed)
    w = {}
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < p:
                w[(i, j)] = rng.random()
    return w


def make_concave(n=20, m=4, seed=0):
    """生成凹-模函数数据. 返回 {e: list[float]} (每个特征权重)."""
    rng = random.Random(seed)
    return {e: [rng.random() for _ in range(m)] for e in range(n)}
