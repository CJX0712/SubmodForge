FROM python:3.11-slim

WORKDIR /app

COPY . /app

# SubmodForge 零运行时依赖, 仅安装测试依赖用于 CI 冒烟
RUN python -m pip install --no-cache-dir pytest==8.3.3

# 端到端演示 (一键复现基准, 落盘 benchmark.json)
CMD ["python", "examples/run_demo.py"]
