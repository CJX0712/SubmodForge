"""SubmodForge 确定性种子管理.

作者: 晨星

集中式随机源: 所有需要随机性的模块都通过本模块获取 ``random.Random`` 实例,
保证同 seed 下两次运行结果逐位一致 (elapsed_sec 除外).
"""
import random
from typing import Optional

_SEED: int = 0
_GLOBAL_RNG: Optional[random.Random] = None


def set_all(seed: int = 0) -> int:
    """设置全局种子, 返回生效 seed.

    同时重置标准库 ``random`` 模块 (部分旧代码可能直接用 random),
    以及缓存本模块的全局 RNG.
    """
    global _SEED, _GLOBAL_RNG
    _SEED = int(seed)
    random.seed(_SEED)
    _GLOBAL_RNG = random.Random(_SEED)
    return _SEED


def get_seed() -> int:
    return _SEED


def RNG(seed: Optional[int] = None) -> random.Random:
    """返回一个独立的可复现随机源.

    若 ``seed`` 为 None 则基于全局 seed 派生 (避免多个模块互相污染全局状态).
    """
    if seed is None:
        return random.Random(_SEED)
    return random.Random(int(seed))
