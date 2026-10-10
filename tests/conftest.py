"""Pytest 配置: 确保仓库根目录在 sys.path 中 (CI 矩阵 3.12/3.13 一致)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
