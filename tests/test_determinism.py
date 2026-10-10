"""确定性: 同 seed 两次运行核心指标逐位一致 (排除时间)."""
from core.seed import set_all
from eval.benchmark import run_benchmark


def test_determinism():
    set_all(0)
    r1 = run_benchmark(seed=0, n_seeds=3, verbose=False)
    r2 = run_benchmark(seed=0, n_seeds=3, verbose=False)
    diffs = []
    for a, b in zip(r1["guarantee_phase"], r2["guarantee_phase"]):
        diffs.append(abs(a["greedy"]["mean"] - b["greedy"]["mean"]))
    for a, b in zip(r1["sfm_phase"], r2["sfm_phase"]):
        diffs.append(abs(a["sfm_value"] - b["sfm_value"]))
    maxd = max(diffs)
    assert maxd < 1e-9, f"确定性被破坏: max_diff={maxd}"
