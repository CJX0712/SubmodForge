"""SubmodForge 错误码定义 (E100~E500).

作者: 晨星
"""


class SubmodError(Exception):
    """所有 SubmodForge 异常的基类."""


class E100InvalidInput(SubmodError):
    """E100: 非法输入 (如空全集、负预算、非数值相似度)."""


class E110NotSubmodular(SubmodError):
    """E110: 函数不满足子模性 (diminishing returns 被破坏)."""


class E200SubmodularViolation(SubmodError):
    """E200: 运行时子模性不一致 (数值/契约违反)."""


class E300ConstraintInfeasible(SubmodError):
    """E300: 约束不可行 (如 k > |V| 且不允许超额)."""


class E400AlgorithmError(SubmodError):
    """E400: 算法内部错误 (如 min-norm-point 步长求解失败)."""


class E500DeterminismError(SubmodError):
    """E500: 确定性校验失败 (同 seed 两次运行结果不一致)."""
