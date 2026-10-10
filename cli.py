"""SubmodForge 命令行入口.

作者: 晨星

子命令:
    maximize   对给定函数运行最大化算法 (greedy/lazy/stochastic/continuous)
    minimize   运行 SFM (最小范数点算法)
    benchmark  运行完整基准并落盘 benchmark.json
    demo       运行端到端演示 (examples/run_demo.py)

示例:
    python cli.py maximize --type facility --n 30 --k 6 --algo lazy
    python cli.py minimize --type graphcut --n 12
    python cli.py benchmark --seed 0
"""
import argparse
import json
import sys

sys.path.insert(0, ".")

from core.seed import set_all, RNG
from core.config import Config
from submod import (
    FacilityLocation, SetCover, SaturationCoverage,
    LogDetFeatureSelection, InfluenceIC, GraphCut, ConcaveOverModular,
)
from maximize import greedy, lazy_greedy, stochastic_greedy, continuous_greedy
from minimize import min_norm_point, min_norm_point_value
from data import (
    make_facility_location, make_set_cover, make_saturation,
    make_logdet, make_influence, make_graph_cut, make_concave,
)
from pipeline.pipeline import SubmodPipeline

BUILDERS = {
    "facility": lambda n, s: FacilityLocation(make_facility_location(n=n, seed=s)),
    "setcover": lambda n, s: SetCover(make_set_cover(n=n, seed=s)),
    "saturation": lambda n, s: SaturationCoverage(make_saturation(n_topics=6, per_topic=3, seed=s)),
    "logdet": lambda n, s: LogDetFeatureSelection(make_logdet(n=n, d=6, seed=s)),
    "influence": lambda n, s: InfluenceIC(make_influence(n=n, seed=s), samples=60, seed=s),
    "graphcut": lambda n, s: GraphCut(make_graph_cut(n=n, seed=s)),
    "concave": lambda n, s: ConcaveOverModular(make_concave(n=n, seed=s)),
}


def _build(ftype, n, seed):
    if ftype not in BUILDERS:
        raise SystemExit(f"未知函数类型: {ftype}; 可选: {list(BUILDERS)}")
    return BUILDERS[ftype](n, seed)


def cmd_maximize(args):
    set_all(args.seed)
    func = _build(args.type, args.n, args.seed)
    rng = RNG(args.seed + 1)
    if args.algo == "greedy":
        sel, val = greedy(func, args.k)
    elif args.algo == "lazy":
        sel, val = lazy_greedy(func, args.k)
    elif args.algo == "stochastic":
        sel, val = stochastic_greedy(func, args.k, eps=args.eps, rng=rng)
    elif args.algo == "continuous":
        sel, val = continuous_greedy(func, args.k, T=args.T)
    else:
        raise SystemExit("algo 必须 ∈ {greedy,lazy,stochastic,continuous}")
    print(json.dumps({"algorithm": args.algo, "k": args.k,
                      "selected": sel, "value": val}, ensure_ascii=False))


def cmd_minimize(args):
    set_all(args.seed)
    func = _build(args.type, args.n, args.seed)
    S = min_norm_point(func)
    print(json.dumps({"minimizer": sorted(S, key=str),
                      "min_value": func.value(S)}, ensure_ascii=False))


def cmd_benchmark(args):
    cfg = Config.from_env()
    cfg.seed = args.seed
    pipe = SubmodPipeline(cfg)
    report = pipe.run(seed=args.seed, out_path=args.out, n_seeds=args.seeds,
                      eps=args.eps, T=args.T, ic_samples=args.ic)
    print(f"等级={report['grade']} 确定性={report['determinism']['deterministic']} -> {args.out}")


def cmd_demo(args):
    from examples.run_demo import main
    main()


def main():
    p = argparse.ArgumentParser(prog="SubmodForge", description="世界顶级子模优化库 (作者: 晨星)")
    sub = p.add_subparsers(dest="cmd", required=True)

    pm = sub.add_parser("maximize")
    pm.add_argument("--type", required=True)
    pm.add_argument("--n", type=int, default=30)
    pm.add_argument("--k", type=int, default=6)
    pm.add_argument("--algo", default="greedy")
    pm.add_argument("--eps", type=float, default=0.1)
    pm.add_argument("--T", type=int, default=120)
    pm.add_argument("--seed", type=int, default=0)
    pm.set_defaults(func=cmd_maximize)

    pn = sub.add_parser("minimize")
    pn.add_argument("--type", required=True)
    pn.add_argument("--n", type=int, default=12)
    pn.add_argument("--seed", type=int, default=0)
    pn.set_defaults(func=cmd_minimize)

    pb = sub.add_parser("benchmark")
    pb.add_argument("--seed", type=int, default=0)
    pb.add_argument("--seeds", type=int, default=3)
    pb.add_argument("--eps", type=float, default=0.1)
    pb.add_argument("--T", type=int, default=120)
    pb.add_argument("--ic", type=int, default=60)
    pb.add_argument("--out", default="benchmark.json")
    pb.set_defaults(func=cmd_benchmark)

    pd = sub.add_parser("demo")
    pd.set_defaults(func=cmd_demo)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
