"""SFM 正确性: 最小范数点算法 == 暴力最小化 (对称 / 非单调)."""
import random
from core.seed import set_all
from submod import GraphCut, ConcaveOverModular
from minimize import min_norm_point_value, brute_force_min
from data import make_graph_cut, make_concave


def test_sfm_graphcut_symmetric():
    set_all(0)
    rng = random.Random(0)
    for trial in range(4):
        n = 10
        gc = GraphCut({(i, j): rng.random()
                       for i in range(n) for j in range(i + 1, n)})
        v = min_norm_point_value(gc)
        _, b = brute_force_min(gc)
        assert abs(v - b) < 1e-6, f"GraphCut SFM 不一致: {v} vs {b}"


def test_sfm_concave_nonmonotone():
    set_all(0)
    rng = random.Random(1)
    g = lambda x: 1.0 - (x - 1.0) ** 2  # 凹且非单调
    for trial in range(4):
        n = 10
        cm = ConcaveOverModular({i: [rng.random() * 2 for _ in range(3)]
                                 for i in range(n)}, concave_fn=g)
        v = min_norm_point_value(cm)
        _, b = brute_force_min(cm)
        assert abs(v - b) < 1e-3, f"ConcaveNM SFM 不一致: {v} vs {b}"
