"""子模优化基准测试.

作者: 晨星

三大阶段:
    A. 保证阶段 (小 n, 可暴力 OPT): 验证 贪心值/OPT >= 1 - 1/e (理论紧界).
    B. 规模/速度阶段 (大 n): 验证 LazyGreedy == Greedy (同值), 随机贪心近贪心, 报告加速比.
    C. SFM 阶段: 最小范数点算法 vs 暴力最小化 (逐位一致).
并含消融: 贪心 vs 随机基线 (margin).
"""
import math
import time
import statistics
from core.seed import RNG
from submod import (
    FacilityLocation, SetCover, SaturationCoverage,
    LogDetFeatureSelection, InfluenceIC, GraphCut, ConcaveOverModular,
)
from maximize import (
    greedy, lazy_greedy, stochastic_greedy, lazy_stochastic_greedy, continuous_greedy,
)
from minimize import min_norm_point_value, brute_force_min, brute_force_max
from data import (
    make_facility_location, make_set_cover, make_saturation,
    make_logdet, make_influence, make_graph_cut, make_concave,
)

GUARANTEE = 1.0 - 1.0 / math.e  # ≈ 0.6321


def _random_baseline(func, k, rng):
    sel = rng.sample(func.V, min(k, len(func.V)))
    return func.value(set(sel))


def _agg(vals):
    return {
        "mean": statistics.mean(vals) if vals else None,
        "std": statistics.pstdev(vals) if len(vals) > 1 else 0.0,
        "n": len(vals),
    }


def run_benchmark(seed=0, n_seeds=3, eps=0.1, T=120, ic_samples=60, verbose=True):
    """运行完整基准, 返回结构化报告 dict. 所有数字均来自真实运行."""
    rng_cfg = RNG(seed)
    seeds = [seed + i * 7 for i in range(n_seeds)]
    report = {
        "meta": {
            "seed": seed,
            "n_seeds": n_seeds,
            "eps": eps,
            "guarantee_1_minus_1oe": GUARANTEE,
            "python": __import__("sys").version.split()[0],
        },
        "guarantee_phase": [],
        "scale_phase": [],
        "sfm_phase": [],
        "ablation": [],
    }

    # ---------------- A. 保证阶段 (小 n, 可暴力 OPT) ----------------
    # (func_factory, name, n, k, kind)
    g_specs = [
        (lambda n: FacilityLocation(make_facility_location(n=n, seed=seed)), "FacilityLocation", 14, 5),
        (lambda n: SetCover(make_set_cover(n=n, seed=seed)), "SetCover", 14, 5),
        (lambda n: SaturationCoverage(make_saturation(n_topics=6, per_topic=3, seed=seed)), "SaturationCoverage", 18, 6),
        (lambda n: LogDetFeatureSelection(make_logdet(n=n, d=6, seed=seed)), "LogDetFeatureSelection", 12, 4),
        (lambda n: InfluenceIC(make_influence(n=n, p=0.3, seed=seed), samples=ic_samples, seed=seed), "InfluenceIC", 14, 4),
    ]
    for factory, name, n, k in g_specs:
        func = factory(n)
        # 暴力 OPT (仅 k 大小集合)
        _, opt = brute_force_max(func, k)
        g_vals, l_vals, s_vals, ls_vals, c_vals, r_vals = [], [], [], [], [], []
        for sd in seeds:
            _, vg = greedy(func, k)
            _, vl = lazy_greedy(func, k)
            _, vs = stochastic_greedy(func, k, eps=eps, rng=RNG(sd + 101))
            _, vls = lazy_stochastic_greedy(func, k, eps=eps, rng=RNG(sd + 202))
            _, vc = continuous_greedy(func, k, T=min(T, max(40, k * 8)))
            vr = _random_baseline(func, k, RNG(sd + 303))
            g_vals.append(vg); l_vals.append(vl); s_vals.append(vs)
            ls_vals.append(vls); c_vals.append(vc); r_vals.append(vr)
        ratio_opt = statistics.mean(g_vals) / opt
        passes = ratio_opt >= GUARANTEE - 1e-6
        entry = {
            "function": name, "n": n, "k": k, "opt": opt,
            "greedy": _agg(g_vals), "lazy_greedy": _agg(l_vals),
            "stochastic_greedy": _agg(s_vals), "lazy_stochastic": _agg(ls_vals),
            "continuous_greedy": _agg(c_vals), "random_baseline": _agg(r_vals),
            "ratio_to_opt": ratio_opt,
            "ratio_to_guarantee": ratio_opt / GUARANTEE,
            "passes_guarantee": bool(passes),
        }
        report["guarantee_phase"].append(entry)
        if verbose:
            print(f"[保证] {name:22s} n={n} k={k} OPT={opt:.3f} "
                  f"Greedy={entry['greedy']['mean']:.3f} ratio/OPT={ratio_opt:.4f} "
                  f"(>=1-1/e={GUARANTEE:.4f}) {'✅' if passes else '❌'}", flush=True)

    # ---------------- B. 规模/速度阶段 (大 n) ----------------
    s_specs = [
        (lambda: FacilityLocation(make_facility_location(n=80, seed=seed)), "FacilityLocation", 80, 10),
        (lambda: SetCover(make_set_cover(n=60, seed=seed)), "SetCover", 60, 10),
        (lambda: SaturationCoverage(make_saturation(n_topics=8, per_topic=10, seed=seed)), "SaturationCoverage", 80, 12),
    ]
    for factory, name, n, k in s_specs:
        func = factory()
        t0 = time.perf_counter(); sel_g, vg = greedy(func, k); tg = time.perf_counter() - t0
        t0 = time.perf_counter(); sel_l, vl = lazy_greedy(func, k); tl = time.perf_counter() - t0
        t0 = time.perf_counter(); sel_s, vs = stochastic_greedy(func, k, eps=eps, rng=RNG(seed + 7)); ts = time.perf_counter() - t0
        lazy_eq = abs(vg - vl) < 1e-9
        entry = {
            "function": name, "n": n, "k": k,
            "greedy_value": vg, "lazy_value": vl, "lazy_eq_greedy": bool(lazy_eq),
            "stochastic_value": vs, "stochastic_delta": vs - vg,
            "greedy_time": tg, "lazy_time": tl, "stochastic_time": ts,
            "speedup_lazy": tg / tl if tl > 0 else None,
            "speedup_stochastic": tg / ts if ts > 0 else None,
        }
        report["scale_phase"].append(entry)
        if verbose:
            print(f"[规模] {name:22s} n={n} k={k} Greedy={vg:.3f} Lazy==Greedy={lazy_eq} "
                  f"tG={tg:.3f}s tL={tl:.3f}s tS={ts:.3f}s", flush=True)

    # ---------------- C. SFM 阶段 ----------------
    c_specs = [
        (lambda: GraphCut(make_graph_cut(n=12, seed=seed)), "GraphCut", 12),
        (lambda: ConcaveOverModular(make_concave(n=12, m=4, seed=seed),
                                    concave_fn=lambda x: 1.0 - (x - 1.0) ** 2), "ConcaveOverModular(NM)", 12),
    ]
    for factory, name, n in c_specs:
        func = factory()
        v_sfm = min_norm_point_value(func)
        _, v_bf = brute_force_min(func)
        match = abs(v_sfm - v_bf) < 1e-4
        report["sfm_phase"].append({
            "function": name, "n": n, "sfm_value": v_sfm, "brute_value": v_bf, "match": bool(match),
        })
        if verbose:
            print(f"[SFM ] {name:22s} n={n} SFM={v_sfm:.4f} BF={v_bf:.4f} {'✅' if match else '❌'}", flush=True)

    # ---------------- 消融: 贪心 vs 随机基线 ----------------
    a_specs = [
        (lambda: FacilityLocation(make_facility_location(n=20, seed=seed)), "FacilityLocation", 6),
        (lambda: SaturationCoverage(make_saturation(n_topics=6, per_topic=3, seed=seed)), "SaturationCoverage", 6),
    ]
    for factory, name, k in a_specs:
        func = factory()
        gv = statistics.mean([greedy(func, k)[1] for _ in seeds])
        rv = statistics.mean([_random_baseline(func, k, RNG(sd + 909)) for sd in seeds])
        report["ablation"].append({
            "function": name, "k": k, "greedy_mean": gv, "random_mean": rv, "margin": gv - rv,
        })
        if verbose:
            print(f"[消融] {name:22s} k={k} Greedy={gv:.3f} Random={rv:.3f} margin={gv-rv:.3f}", flush=True)

    return report
