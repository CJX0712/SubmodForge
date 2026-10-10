"""子模性校验: 每个具体函数 (除 IC 的 MC 估计外) 均满足 diminishing returns."""
import random
from core.seed import set_all
from submod import (FacilityLocation, SetCover, SaturationCoverage,
                    LogDetFeatureSelection, GraphCut, ConcaveOverModular)
from data import (make_facility_location, make_set_cover, make_saturation,
                  make_logdet, make_graph_cut, make_concave)


def _check(func):
    ok, ce = func.is_submodular(samples=300, tol=1e-9)
    assert ok, f"{type(func).__name__} 不满足子模性: {ce}"


def test_facility_location_submodular():
    set_all(0)
    _check(FacilityLocation(make_facility_location(n=10, seed=1)))


def test_set_cover_submodular():
    set_all(0)
    _check(SetCover(make_set_cover(n=10, seed=1)))


def test_saturation_submodular():
    set_all(0)
    _check(SaturationCoverage(make_saturation(n_topics=5, per_topic=3, seed=1)))


def test_logdet_submodular():
    set_all(0)
    _check(LogDetFeatureSelection(make_logdet(n=10, d=5, seed=1)))


def test_graph_cut_submodular():
    set_all(0)
    _check(GraphCut(make_graph_cut(n=10, seed=1)))


def test_concave_submodular():
    set_all(0)
    _check(ConcaveOverModular(make_concave(n=10, m=3, seed=1)))
