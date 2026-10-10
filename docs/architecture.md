# SubmodForge 架构文档

> 作者：晨星 · 世界顶级子模优化系统 · 纯标准库 / 零依赖 / 逐位可复现

## 1. 总览

SubmodForge 解决两类组合优化问题：

- **最大化**：在基数约束 `|S| ≤ k` 下最大化单调子模函数 `f(S)`，提供 `(1−1/e)` 紧界保证的贪心族算法。
- **最小化（SFM）**：精确最小化任意子模函数 `f`，通过 Fujishige–Wolfe 最小范数点算法，与暴力枚举逐位一致。

设计原则（源自本仓库的"零依赖零构建"哲学）：

1. 仅用 Python 标准库（`heapq`、`random`、`itertools`、`math`、`json`），无第三方依赖。
2. 全局确定性：所有随机性经 `core.seed` 统一播种，同 seed 逐位可复现。
3. 每个数学结果均有**可验证不变量**（见 README 数学内核），由测试与基准交叉验证。

## 2. 分层结构

```
cli.py ──> pipeline/pipeline.py ──> eval/benchmark.py
                                      │
              ┌───────────┬───────────┼───────────┬────────────┐
              ▼           ▼           ▼           ▼            ▼
          data/      maximize/    minimize/    submod/      core/
      (合成数据)   (6 算法)   (SFM 精确)  (7 函数)   (类型/错误/配置/种子)
```

调用单向无环：`cli → pipeline → {data, maximize, minimize, submod, eval} → core`。

## 3. 核心抽象（core/types.py）

- `SubmodularFunction`：接口 `V`（全集）、`value(S)`、`marginal(A, e)`、`ground_union`（并集上界）。
  - 约定：`f(∅)=0`，单调函数 `f(A) ≤ f(B)`（当 `A⊆B`），子模性 `marginal` 随集合增大不增。
- `Maximizer` / `Minimizer`：返回 `(selected, value)` 的算法签名，便于注册表统一调度。

## 4. 子模函数（submod/）

| 模块 | 函数 | 性质 | 应用 |
|------|------|------|------|
| `facility_location.py` | FacilityLocation | 单调、子模 | 数据摘要 / 选址 |
| `set_cover.py` | SetCover | 单调、子模 | 集合覆盖 |
| `saturation.py` | SaturationCoverage | 单调、子模 | 多样性覆盖 |
| `logdet.py` | LogDetFeatureSelection | 单调、子模 | 特征选择 |
| `influence.py` | InfluenceIC | 经验子模（MC） | 影响力最大化 |
| `graph_cut.py` | GraphCut | 对称、非单调 | 图割（SFM 对象） |
| `concave.py` | ConcaveOverModular | 非单调（凹包模） | 一般 SFM 测试 |

子模性由 `tests/test_submodularity.py` 的随机化链检验（Dr
以 `marginal` 单调性 + 定义式双重校验）。

## 5. 最大化算法（maximize/）

- `greedy.py`：惰性贪心原型，逐元素选最大边际增益，复杂度 `O(kn)` 次求值。
- `lazy_greedy.py`：Minoux (1978) 惰性评估，`heapq` 维护候选上界，仅对过期项重算，返回值与 Greedy 逐位相同。
- `stochastic_greedy.py`：Mirzasoleiman et al. (2015)，每步随机采样 `⌈n/k·log(1/ε)⌉` 个元素，复杂度降至 `O(k·log(1/ε)·log k)`。
- `lazy_stochastic.py`：惰性 + 随机的组合。
- `continuous_greedy.py`：Calinescu et al. (2011) 分数域 Frank–Wolfe，输出分数解后取整为 top-k。
- `registry.py`：`ALGORITHMS` 字典，CLI 与 benchmark 统一按名调用。

## 6. 最小化（SFM，minimize/）

- `min_norm_point.py`：**Fujishige–Wolfe 最小范数点算法**。核心步骤：
  1. 以"超模曲面对偶"梯度 `g = [f({i}) − f(∅)]` 初始化。
  2. 在由极点构成的面 `P` 上求最小范数点：用 **Edmonds 排序**（按 `x` 升序接管）构造当前面的极点；内部用**仿射极小点**（权重和=1，可为负）做 major/minor 循环收敛。
  3. 当最小范数点落在某个面内时，输出 `S* = {i : x*_i < 0}` 即为 SFM 解。
- `brute_force.py`：枚举 `2^n` 子集，仅用于小规模验证/基线，不进入生产路径。

正确性由 `tests/test_sfm.py` 对照 `n≤12` 的暴力解，对称与非单调函数均逐位一致。

## 7. 评估与确定性（eval/ + pipeline/）

`benchmark.py` 分四阶段产出 `benchmark.json`：

1. **保证阶段**：小 n 暴力算 OPT，验证各算法 `ratio ≥ 1−1/e`。
2. **规模阶段**：大 n 测 LazyGreedy/Stochastic 加速比与 `Lazy==Greedy`。
3. **SFM 阶段**：对照暴力最小化。
4. **消融 / 确定性**：贪心 vs 随机基线 margin；同 seed 二次运行 max diff。

`pipeline.py` 编排四阶段并给出质量等级（S/A/B/C）。

## 8. CLI（cli.py）

子命令：`maximize`、`minimize`、`benchmark`、`demo`。参数经 `core/config` 校验，输出 JSON 便于管道。

## 9. 已知工程权衡

- SFM 每步枚举 `2^n` 子集，适用 `n ≲ 20`；超大对称图割建议 Queyranne 近似。
- InfluenceIC 子模性依赖蒙特卡洛采样，增大 `samples` 降方差。
- ContinuousGreedy 分数取整引入整数化偏差，理论界在期望意义成立。
