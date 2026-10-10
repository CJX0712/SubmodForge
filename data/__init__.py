"""SubmodForge 合成数据生成器.

作者: 晨星

所有生成器接受固定 seed, 使用独立 random.Random 实例, 保证可复现.
"""
from .synthetic import (
    make_facility_location,
    make_set_cover,
    make_saturation,
    make_logdet,
    make_influence,
    make_graph_cut,
    make_concave,
)

__all__ = [
    "make_facility_location",
    "make_set_cover",
    "make_saturation",
    "make_logdet",
    "make_influence",
    "make_graph_cut",
    "make_concave",
]
