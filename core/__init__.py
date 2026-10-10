"""SubmodForge — 子模优化核心层 (Core).

作者: 晨星
零依赖: 仅使用 Python 标准库 (>=3.10)。
"""
from .errors import (
    SubmodError,
    E100InvalidInput,
    E110NotSubmodular,
    E200SubmodularViolation,
    E300ConstraintInfeasible,
    E400AlgorithmError,
    E500DeterminismError,
)
from .config import Config
from .seed import set_all, get_seed, RNG
from .types import SubmodularFunction, Maximizer

__all__ = [
    "SubmodError",
    "E100InvalidInput",
    "E110NotSubmodular",
    "E200SubmodularViolation",
    "E300ConstraintInfeasible",
    "E400AlgorithmError",
    "E500DeterminismError",
    "Config",
    "set_all",
    "get_seed",
    "RNG",
    "SubmodularFunction",
    "Maximizer",
    "__version__",
]

__version__ = "0.1.0"
