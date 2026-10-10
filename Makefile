# SubmodForge Makefile (作者: 晨星)
PY ?= python

.PHONY: demo benchmark test ci clean

demo:
	$(PY) examples/run_demo.py

benchmark:
	$(PY) cli.py benchmark --seed 0

test:
	$(PY) -m pytest -q -W ignore::UserWarning

ci: test demo

clean:
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
	rm -f benchmark.json cli_bench.json
