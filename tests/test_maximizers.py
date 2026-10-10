"""最大化算法正确性: (1-1/e) 保证 / Lazy==Greedy / 随机贪心 / 连续贪心."""
import math
from core.seed import set_all, RNG
from submod import FacilityLocation, GraphCut, ConcaveOverModular
from maximize import (greedy, lazy_greedy, stochastic_greedy, continuous_greedy)
from minimize import brute_force_max
from data import make_facility_location, make_graph_cut, make_concave

GUARANTEE = 1.0 - 1.0 / math.e


def test_greedy_1_minus_1oe_guarantee():
    set_all(0)
    fl = FacilityLocation(make_facility_location(n=12, seed=2))
    k = 5
    _, opt = brute_force_max(fl, k)
    _, vg = greedy(fl, k)
    ratio = vg / opt
    assert ratio >= GUARANTEE - 1e-6, f"贪心未达 (1-1/e): ratio={ratio}"


def test_lazy_equals_greedy():
    set_all(0)
    for seed in range(3):
        fl = FacilityLocation(make_facility_location(n=20, seed=seed))
        _, vg = greedy(fl, 6)
        _, vl = lazy_greedy(fl, 6)
        assert abs(vg - vl) < 1e-9, f"LazyGreedy 与 Greedy 值不一致 (seed={seed})"


def test_stochastic_near_optimal():
    set_all(0)
    fl = FacilityLocation(make_facility_location(n=14, seed=3))
    k = 5
    _, opt = brute_force_max(fl, k)
    _, vs = stochastic_greedy(fl, k, eps=0.1, rng=RNG(5))
    # 随机贪心理论界 (1-1/e-eps); 实测应 >= (1-1/e-0.15)·OPT (含统计余量)
    assert vs / opt >= GUARANTEE - 0.15, f"随机贪心过低: {vs/opt}"


def test_continuous_near_optimal():
    set_all(0)
    fl = FacilityLocation(make_facility_location(n=14, seed=4))
    k = 5
    _, opt = brute_force_max(fl, k)
    _, vc = continuous_greedy(fl, k, T=200)
    assert vc / opt >= GUARANTEE - 0.15, f"连续贪心过低: {vc/opt}"


def test_constraint_infeasible_raises():
    fl = FacilityLocation(make_facility_location(n=4, seed=0))
    raised = False
    try:
        greedy(fl, -1)
    except Exception:
        raised = True
    assert raised, "k<0 应抛出异常"
