"""SubmodForge 全局配置 (环境变量覆盖 + schema 校验).

作者: 晨星
"""
import os
from dataclasses import dataclass, field


@dataclass
class Config:
    """系统级配置. 支持环境变量覆盖 ``SUBMOD_*``.

    字段:
        seed: 全局确定性种子.
        ic_samples: InfluenceIC 蒙特卡洛采样数 (影响期望传播估计精度).
        eps: 随机贪心 / 连续贪心 容差参数.
        tol: 子模性 / 数值比较容差.
        rng_impl: 随机源实现 (固定为 stdlib random.Random).
    """

    seed: int = 0
    ic_samples: int = 200
    eps: float = 0.1
    tol: float = 1e-9

    @classmethod
    def from_env(cls) -> "Config":
        """从环境变量 ``SUBMOD_SEED`` 等读取覆盖值."""
        kw: dict = {}
        if os.environ.get("SUBMOD_SEED") is not None:
            kw["seed"] = int(os.environ["SUBMOD_SEED"])
        if os.environ.get("SUBMOD_IC_SAMPLES") is not None:
            kw["ic_samples"] = int(os.environ["SUBMOD_IC_SAMPLES"])
        if os.environ.get("SUBMOD_EPS") is not None:
            kw["eps"] = float(os.environ["SUBMOD_EPS"])
        if os.environ.get("SUBMOD_TOL") is not None:
            kw["tol"] = float(os.environ["SUBMOD_TOL"])
        return cls(**kw)

    def validate(self) -> None:
        if self.seed < 0:
            raise ValueError("seed 必须 >= 0")
        if self.ic_samples < 1:
            raise ValueError("ic_samples 必须 >= 1")
        if not (0.0 < self.eps < 1.0):
            raise ValueError("eps 必须位于 (0, 1)")
        if self.tol <= 0:
            raise ValueError("tol 必须 > 0")
