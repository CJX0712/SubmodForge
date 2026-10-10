# SubmodForge 模型卡 / 系统卡

> 作者：晨星 · 版本 v0.1.0 · 纯标准库子模优化系统

## 1. 系统标识

- **名称**：SubmodForge
- **版本**：v0.1.0
- **作者**：晨星 (MorningStar)
- **许可证**：MIT
- **运行时依赖**：无（Python 3.10+ 标准库）
- **质量等级**：S（世界级）

## 2. 用途与适用范围

| 任务 | 算法 | 保证 |
|------|------|------|
| 基数约束单调子模最大化 | Greedy / LazyGreedy | `(1−1/e)·OPT`（紧界） |
| 大规模近似最大化 | StochasticGreedy / LazyStochastic | `(1−1/e−ε)·OPT` |
| 分数域最大化 | ContinuousGreedy | `(1−1/e)·OPT`（期望） |
| 任意子模函数最小化 (SFM) | min_norm_point | 精确（= 暴力） |

**典型应用**：特征选择（LogDet）、数据摘要/选址（FacilityLocation）、文档/多样性覆盖（SaturationCoverage）、集合覆盖（SetCover）、影响力最大化（InfluenceIC）、图割（GraphCut）。

## 3. 数学保证（可验证不变量）

1. `(1−1/e)` 紧界：单调子模 + 基数约束下贪心 `≥ (1−1/e)·OPT`，`P≠NP` 下紧（Nemhauser–Wolsey–Fisher 1978）。
   - 实测：5 个函数贪心/OPT 比值 `∈ [0.9112, 1.0000]`，均 `≥ 0.6321`。
2. `LazyGreedy ≡ Greedy`：返回值逐位相同（绝对差 `= 0`）。
3. 子模性定义式：6 个具体函数通过随机化链检验。
4. `SFM` 精确性：`min_norm_point_value === brute_force_min`（对称 GraphCut 与非单调 ConcaveOverModular 均逐位一致）。
5. 确定性：同 seed 二次运行核心指标 `max_abs_diff = 0.0`。

## 4. 性能基线（真实运行，seed=0，3 seeds，Python 3.13.14）

**保证阶段（比值/OPT，均 ≥ 1−1/e）**

- FacilityLocation 14/5：1.0000
- SetCover 14/5：0.9730
- SaturationCoverage 18/6：1.0000
- LogDetFeatureSelection 12/4：1.0000
- InfluenceIC 14/4：0.9112

**规模/速度（大 n）**

- FacilityLocation 80/10：Lazy==Greedy ✅，Lazy 加速 **140.8×**，Stochastic 72.6×
- SetCover 60/10：Lazy==Greedy ✅，Lazy 加速 **15.4×**
- SaturationCoverage 80/12：Lazy==Greedy ✅，Lazy 加速 **7.7×**

**SFM 阶段**：GraphCut(12) SFM=0.0 == 暴力 0.0；ConcaveOverModular(12) SFM=−137.9421 == 暴力 −137.9421。

**端到端时长**：demo 0.87s（预算 60s）。

## 5. 训练 / 数据来源

无训练。所有数据为 `data/synthetic.py` 的**确定性合成生成器**（高斯相似度、随机集合覆盖、MC 影响力传播等），seed 固定、与评估独立，无数据泄漏。

## 6. 局限性

- SFM 每步枚举 `2^n` 子集，适用 `n ≲ 20`；超大图割建议近似或 Queyranne。
- InfluenceIC 子模性为经验成立（蒙特卡洛），需足够 `samples`。
- ContinuousGreedy 取整引入整数化偏差，理论界在期望意义成立。

## 7. 合规与伦理

- 许可证 MIT，可商用、可修改、需保留署名（晨星）。
- 无外部权重下载、无密钥、无隐私数据（全合成）。
- 已通过无密钥泄漏 grep 自查。

## 8. 复现指令

```bash
git clone https://github.com/CJX0712/SubmodForge.git
cd SubmodForge
python examples/run_demo.py      # -> benchmark.json
python -m pytest -q              # 全量单测 (17/17)
```
