"""临时冒烟测试: 校验 SFM / 子模性 / 贪心保证 / 惰性==贪心.

作者: 晨星 (开发期自检)
"""
import random
import sys
sys.path.insert(0, ".")

from core.seed import set_all
from submod import (FacilityLocation, SetCover, SaturationCoverage,
                    LogDetFeatureSelection, InfluenceIC, GraphCut, ConcaveOverModular)
from maximize import greedy, lazy_greedy, stochastic_greedy, continuous_greedy
from minimize import min_norm_point_value, brute_force_min, brute_force_max

set_all(42)
rng = random.Random(42)
fails = 0

# ---- 1. 子模性校验 ----
print("== 子模性校验 ==")
n = 12
# FacilityLocation
sim = {}
for i in range(n):
    for j in range(i + 1, n):
        w = rng.random()
        sim[(i, j)] = w
fl = FacilityLocation(sim)
ok, ce = fl.is_submodular(samples=300)
print(f"  FacilityLocation submodular={ok}")
if not ok:
    fails += 1
    print("   CE:", ce)

# GraphCut
w = {}
for i in range(n):
    for j in range(i + 1, n):
        w[(i, j)] = rng.random()
gc = GraphCut(w)
ok, ce = gc.is_submodular(samples=300)
print(f"  GraphCut submodular={ok}")
if not ok:
    fails += 1

# ConcaveOverModular
WW = {i: [rng.random() for _ in range(4)] for i in range(n)}
cm = ConcaveOverModular(WW)
ok, ce = cm.is_submodular(samples=300)
print(f"  ConcaveOverModular submodular={ok}")
if not ok:
    fails += 1

# SetCover
cover = {i: set(rng.sample(range(20), rng.randint(1, 5))) for i in range(n)}
sc = SetCover(cover)
ok, ce = sc.is_submodular(samples=300)
print(f"  SetCover submodular={ok}")
if not ok:
    fails += 1

# SaturationCoverage
topic = {i: rng.randint(0, 5) for i in range(n)}
sat = SaturationCoverage(topic)
ok, ce = sat.is_submodular(samples=300)
print(f"  SaturationCoverage submodular={ok}")
if not ok:
    fails += 1

# LogDet
feats = {i: [rng.gauss(0, 1) for _ in range(6)] for i in range(n)}
ld = LogDetFeatureSelection(feats)
ok, ce = ld.is_submodular(samples=300)
print(f"  LogDetFeatureSelection submodular={ok}")
if not ok:
    fails += 1

# InfluenceIC
graph = {i: [(j, rng.random() * 0.5) for j in rng.sample(range(n), rng.randint(1, 3))] for i in range(n)}
ic = InfluenceIC(graph, samples=50, seed=1)
ok, ce = ic.is_submodular(samples=200)
print(f"  InfluenceIC submodular={ok} (MC 估计, 可能噪声)")
if not ok:
    print("    CE:", ce)

# ---- 2. SFM: min_norm_point vs brute_force_min ----
print("\n== SFM 校验 (min_norm_point vs brute force) ==")
for name, fn in [("FacilityLocation", fl), ("GraphCut", gc), ("ConcaveOverModular", cm)]:
    S_sfm = min_norm_point_value(fn)
    _, v_bf = brute_force_min(fn)
    diff = abs(S_sfm - v_bf)
    ok = diff < 1e-6
    print(f"  {name}: SFM={S_sfm:.6f}  BF={v_bf:.6f}  diff={diff:.2e}  {'OK' if ok else 'FAIL'}")
    if not ok:
        fails += 1

# ---- 3. 贪心 (1-1/e) 保证 vs brute force OPT ----
print("\n== 贪心 (1-1/e) 保证 ==")
k = 4
sel, vg = greedy(fl, k)
_, vopt = brute_force_max(fl, k)
ratio = vg / vopt
print(f"  FacilityLocation Greedy/OPT={ratio:.4f} (>= {1-1/2.718281828:.4f}-tol 应成立)")
if ratio < (1 - 1 / 2.718281828) - 1e-6:
    fails += 1
    print("    FAIL: 低于 1-1/e")

# ---- 4. 惰性贪心 == 贪心 (同值) ----
print("\n== 惰性贪心 == 贪心 ==")
sel_l, vl = lazy_greedy(fl, k)
print(f"  Greedy={vg:.6f}  LazyGreedy={vl:.6f}  equal={abs(vg-vl)<1e-9}")
if abs(vg - vl) > 1e-9:
    fails += 1

# ---- 5. 随机贪心 / 连续贪心 不显著低于 OPT ----
print("\n== 变体算法 ==")
sel_s, vs = stochastic_greedy(fl, k, eps=0.1, rng=random.Random(7))
sel_c, vc = continuous_greedy(fl, k, T=200)
print(f"  StochasticGreedy/OPT={vs/vopt:.4f}")
print(f"  ContinuousGreedy/OPT={vc/vopt:.4f}")
if vs / vopt < (1 - 1 / 2.718281828) - 0.15:
    fails += 1
    print("    FAIL: 随机贪心过低")
if vc / vopt < (1 - 1 / 2.718281828) - 0.15:
    fails += 1
    print("    FAIL: 连续贪心过低")

print("\n==== 失败数:", fails, "====")
sys.exit(1 if fails else 0)
