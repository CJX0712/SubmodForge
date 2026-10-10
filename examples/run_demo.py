"""SubmodForge 端到端演示.

作者: 晨星

运行: python examples/run_demo.py
产出: benchmark.json (核心指标) + 失败案例归因 + 质量等级.
"""
import json
import sys

sys.path.insert(0, ".")

from core.seed import set_all, RNG
from core.config import Config
from pipeline.pipeline import SubmodPipeline
from eval.benchmark import GUARANTEE
from submod import FacilityLocation
from maximize import greedy, stochastic_greedy
from data import make_facility_location


def build_failure_cases(report, seed):
    """生成 >=3 条典型误例 (含原因归因), 全部由真实运行派生."""
    fc = []
    for e in report["guarantee_phase"]:
        gap = e["opt"] - e["greedy"]["mean"]
        rel = gap / e["opt"] if e["opt"] else 0.0
        fc.append({
            "function": e["function"], "k": e["k"],
            "greedy": round(e["greedy"]["mean"], 4), "opt": round(e["opt"], 4),
            "abs_gap": round(gap, 4), "relative_gap": round(rel, 4),
            "cause": "diminishing returns 使贪心至多达到 (1-1/e)·OPT, 该界为紧界 "
                     "(Nemhauser, Wolsey & Fisher, 1978), 非算法缺陷.",
        })
    # 随机贪心 eps 权衡
    fl = FacilityLocation(make_facility_location(n=14, seed=seed))
    _, vg = greedy(fl, 5)
    _, vs = stochastic_greedy(fl, 5, eps=0.5, rng=RNG(seed + 1))
    fc.append({
        "function": "FacilityLocation", "k": 5,
        "greedy": round(vg, 4), "stochastic_eps0.5": round(vs, 4),
        "abs_gap": round(vg - vs, 4),
        "cause": "随机贪心 eps=0.5 牺牲精度换 O(n log k) 速度, 理论界降至 (1-1/e-eps)·OPT.",
    })
    return fc


def main():
    cfg = Config.from_env()
    pipe = SubmodPipeline(cfg)
    report = pipe.run(
        seed=cfg.seed, out_path="benchmark.json",
        n_seeds=3, eps=0.1, T=120, ic_samples=60,
    )
    report["failure_cases"] = build_failure_cases(report, cfg.seed)
    with open("benchmark.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("\n================ SubmodForge 基准摘要 ================")
    print(f" 质量等级        : {report['grade']}")
    print(f" 理论保证 1-1/e   : {GUARANTEE:.4f}")
    for e in report["guarantee_phase"]:
        flag = "✅" if e["passes_guarantee"] else "❌"
        print(f"   [保证] {e['function']:22s} ratio/OPT={e['ratio_to_opt']:.4f} "
              f"(>={GUARANTEE:.4f}) {flag}")
    for e in report["scale_phase"]:
        print(f"   [规模] {e['function']:22s} Lazy==Greedy={e['lazy_eq_greedy']} "
              f"speedupL={e['speedup_lazy']:.2f}x speedupS={e['speedup_stochastic']:.2f}x")
    for e in report["sfm_phase"]:
        print(f"   [SFM ] {e['function']:22s} SFM={e['sfm_value']:.4f} BF={e['brute_value']:.4f} "
              f"{'✅' if e['match'] else '❌'}")
    d = report["determinism"]
    print(f" 确定性          : max_diff={d['max_abs_diff_excl_time']:.2e} "
          f"deterministic={d['deterministic']}")
    print(f" 失败案例        : {len(report['failure_cases'])} 条")
    print(f" 耗时            : {report['meta']['elapsed_sec']}s -> benchmark.json")
    print("=====================================================")
    return report


if __name__ == "__main__":
    main()
