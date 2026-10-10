"""SubmodForge 端到端流水线.

作者: 晨星

SubmodPipeline.run():
    1. 固定全局种子 (确定性).
    2. 运行完整基准 (保证阶段 / 规模阶段 / SFM 阶段 / 消融).
    3. 二次运行校验确定性 (同 seed 核心指标逐位一致).
    4. 计算质量等级 (S/A/B/C).
    5. 落盘 benchmark.json.

CLI / demo 均复用本流水线, 保证"一键复现".
"""
import json
import time
from core.seed import set_all
from core.config import Config
from eval.benchmark import run_benchmark, GUARANTEE


def grade_report(report):
    """依据 DoD 计算本地质量等级 (S/A/B/C)."""
    g_ok = all(e["passes_guarantee"] for e in report["guarantee_phase"])
    sfm_ok = all(e["match"] for e in report["sfm_phase"])
    scale_ok = all(e["lazy_eq_greedy"] for e in report["scale_phase"])
    det_ok = report.get("determinism", {}).get("deterministic", False)
    stoch_ok = all(abs(e["stochastic_delta"]) < max(0.05 * abs(e["greedy_value"]), 0.05)
                   for e in report["scale_phase"])
    if g_ok and sfm_ok and det_ok and scale_ok and stoch_ok:
        return "S"
    if g_ok and sfm_ok and det_ok:
        return "A"
    if g_ok:
        return "B"
    return "C"


class SubmodPipeline:
    def __init__(self, config: Config = None):
        self.config = config or Config.from_env()

    def run(self, seed=None, out_path=None, n_seeds=3, eps=0.1, T=120, ic_samples=60):
        if seed is not None:
            self.config.seed = seed
        set_all(self.config.seed)
        t0 = time.perf_counter()
        report = run_benchmark(
            seed=self.config.seed, n_seeds=n_seeds, eps=eps, T=T,
            ic_samples=ic_samples, verbose=True,
        )
        report["meta"]["elapsed_sec"] = round(time.perf_counter() - t0, 3)
        # 二次运行校验确定性
        report["determinism"] = self._check_determinism(n_seeds, eps, T, ic_samples)
        report["grade"] = grade_report(report)
        if out_path:
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
        self._report = report
        return report

    def _check_determinism(self, n_seeds, eps, T, ic_samples):
        """二次运行 (同 seed) 比对核心指标 (排除时间). 返回 {max_abs_diff, deterministic}."""
        r1 = run_benchmark(seed=self.config.seed, n_seeds=n_seeds, eps=eps, T=T,
                           ic_samples=ic_samples, verbose=False)
        r2 = run_benchmark(seed=self.config.seed, n_seeds=n_seeds, eps=eps, T=T,
                           ic_samples=ic_samples, verbose=False)
        diffs = []
        for a, b in zip(r1["guarantee_phase"], r2["guarantee_phase"]):
            diffs.append(abs(a["greedy"]["mean"] - b["greedy"]["mean"]))
            diffs.append(abs(a["lazy_greedy"]["mean"] - b["lazy_greedy"]["mean"]))
        for a, b in zip(r1["sfm_phase"], r2["sfm_phase"]):
            diffs.append(abs(a["sfm_value"] - b["sfm_value"]))
        for a, b in zip(r1["scale_phase"], r2["scale_phase"]):
            diffs.append(abs(a["greedy_value"] - b["greedy_value"]))
        maxd = max(diffs) if diffs else 0.0
        return {"max_abs_diff_excl_time": maxd, "deterministic": maxd < 1e-9}
