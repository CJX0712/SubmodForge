"""SubmodForge 子模函数库.

作者: 晨星

提供 6 个经数学证明为子模的具体函数:
    FacilityLocation        设施选址 (monotone)
    SetCover               集合覆盖 (monotone)
    SaturationCoverage     饱和覆盖 / 公平摘要 (monotone)
    LogDetFeatureSelection 对数行列式特征选择 (monotone)
    InfluenceIC            独立级联影响力传播 (monotone)
    GraphCut               图割 (symmetric, 非单调 — 用于 SFM 演示)
    ConcaveOverModular     模函数上的凹函数 (可非单调)
"""
from .facility_location import FacilityLocation
from .set_cover import SetCover
from .saturation import SaturationCoverage
from .logdet import LogDetFeatureSelection
from .influence import InfluenceIC
from .graph_cut import GraphCut
from .concave import ConcaveOverModular

__all__ = [
    "FacilityLocation",
    "SetCover",
    "SaturationCoverage",
    "LogDetFeatureSelection",
    "InfluenceIC",
    "GraphCut",
    "ConcaveOverModular",
]
