"""CLI 冒烟测试 (subprocess 调用, 验证端到端可用)."""
import json
import subprocess
import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable


def _run(args):
    return subprocess.run([PY, "cli.py"] + args, cwd=ROOT,
                          capture_output=True, text=True, timeout=120)


def test_cli_maximize():
    r = _run(["maximize", "--type", "facility", "--n", "12", "--k", "4",
              "--algo", "lazy", "--seed", "0"])
    assert r.returncode == 0, r.stderr
    obj = json.loads(r.stdout)
    assert "value" in obj and "selected" in obj
    assert len(obj["selected"]) == 4


def test_cli_minimize():
    r = _run(["minimize", "--type", "graphcut", "--n", "8", "--seed", "0"])
    assert r.returncode == 0, r.stderr
    obj = json.loads(r.stdout)
    assert "min_value" in obj


def test_cli_benchmark():
    r = _run(["benchmark", "--seed", "0", "--seeds", "2", "--out", "cli_bench.json"])
    assert r.returncode == 0, r.stderr
    assert os.path.exists(os.path.join(ROOT, "cli_bench.json"))
