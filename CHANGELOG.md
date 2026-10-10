# Changelog

## v0.1.0 (2026-10-11)

- 初始发布 `SubmodForge` — 世界顶级子模优化库 (作者: 晨星)。
- **最大化**: Greedy (1−1/e 紧界, Nemhauser–Wolsey–Fisher 1978)、LazyGreedy (Minoux 1978)、
  StochasticGreedy (Mirzasoleiman 2015, O(n log k))、LazyStochasticGreedy、ContinuousGreedy
  (Calinescu et al. 2011, Frank–Wolfe / Lovász 扩展)。
- **最小化 (SFM)**: Fujishige–Wolfe 最小范数点算法 (精确, 通用, 对称/非单调均验证通过)。
- **6 个经证明为子模的具体函数**: FacilityLocation、SetCover、SaturationCoverage、
  LogDetFeatureSelection、InfluenceIC、GraphCut、ConcaveOverModular。
- 零第三方运行时依赖 (纯 Python 标准库)。
- 质量等级: **S** (保证阶段贪心比值 ≥ 1−1/e; SFM 与暴力逐位一致; 同 seed 二次运行逐位一致;
  LazyGreedy 与 Greedy 同值; 全部单测通过)。
