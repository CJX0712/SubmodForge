"""本地测试运行器 (零依赖, 模拟 pytest 发现 test_* 函数).

仅用于无网络环境下本地验证; 正式 CI 使用 pytest.
作者: 晨星
"""
import importlib
import pkgutil
import traceback
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "tests"))

import tests as tests_pkg

passed = 0
failed = 0
failures = []

for modname in ["test_submodularity", "test_maximizers", "test_sfm",
                "test_determinism", "test_cli"]:
    mod = importlib.import_module("tests." + modname)
    funcs = [f for f in dir(mod) if f.startswith("test_") and callable(getattr(mod, f))]
    for fn in funcs:
        try:
            getattr(mod, fn)()
            print(f"  PASS  {modname}.{fn}")
            passed += 1
        except Exception as e:
            print(f"  FAIL  {modname}.{fn}: {e}")
            failures.append((modname, fn, traceback.format_exc()))
            failed += 1

print(f"\n==== 本地测试: {passed} passed, {failed} failed ====")
if failures:
    for m, f, tb in failures:
        print(f"\n--- {m}.{f} ---\n{tb}")
    sys.exit(1)
sys.exit(0)
