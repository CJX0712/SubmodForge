"""Fujishige-Wolfe 最小范数点算法 — 精确子模函数最小化 (SFM).

作者: 晨星

对任意子模函数 f (f(∅)=0), 其基多胞形 (base polytope) B(f) 的最小范数点 x*
给出最小化集合 S* = {i : x*_i < 0}。本实现严格遵循 Fujishige-Wolfe 算法
(Wolfe 1976 最小范数点 + Edmonds 排序预言机 + 主/次循环 corral 维护):

  主循环: 用 Edmonds 排序 (按当前点 x 升序排列指标) 构造使 <x, g> 最小的极基 g;
          若 <x, g> >= ||x||^2 则终止 (x 即 B(f) 最小范数点);
          否则扩充面 S' = S ∪ {g}, 求 S' 的仿射极小点 y (仿射组合, 权重可负)。
  次循环: 若 y 不在 conv(S') 相对内部 (存在负权重), 沿线段 [y, x] 收缩到与
          conv(S') 边界的交点, 缩减面 S 后重复, 直至得到 corral。

复杂度: 每次迭代枚举 O(n) 子集求最大步长, 适用于中小规模 (n <= ~20)。
"""
import itertools
import random
from core.errors import E400AlgorithmError

_TOL = 1e-9
_RIDGE = 1e-10


# ---------------- 小型线性代数 (零依赖) ----------------

def _solve_square(A, b):
    """解方阵线性方程组 A x = b (高斯消元 + 部分主元)."""
    n = len(A)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(M[r][col]))
        if abs(M[piv][col]) < 1e-15:
            raise E400AlgorithmError("SFM: 奇异矩阵")
        M[col], M[piv] = M[piv], M[col]
        pv = M[col][col]
        for j in range(col, n + 1):
            M[col][j] /= pv
        for r in range(n):
            if r != col and M[r][col] != 0.0:
                f = M[r][col]
                for j in range(col, n + 1):
                    M[r][j] -= f * M[col][j]
    return [M[i][n] for i in range(n)]


def _lstsq(A, b):
    """最小二乘: min ||A x - b||^2 (A: k×p). 法方程 + 微正则化."""
    p = len(A[0])
    AtA = [[sum(A[r][i] * A[r][j] for r in range(len(A))) for j in range(p)] for i in range(p)]
    Atb = [sum(A[r][i] * b[r] for r in range(len(A))) for i in range(p)]
    for i in range(p):
        AtA[i][i] += _RIDGE
    return _solve_square(AtA, Atb)


# ---------------- 基多胞形工具 ----------------

def _all_subsets(n):
    for r in range(n + 1):
        for combo in itertools.combinations(range(n), r):
            yield frozenset(combo)


def _extreme_base(order, fval):
    """按给定指标顺序 order 构造极基 g: g[e] = f(prefix) - f(prefix前)."""
    x = [0.0] * len(order)
    prev = 0.0
    for idx, e in enumerate(order):
        cur = fval(set(order[: idx + 1]))
        x[e] = cur - prev
        prev = cur
    return x


def _max_step(fval, n, x, d, tol=_TOL):
    """最大步长 t∈(0,1] 使 x + t·d 仍在 B(f) 内."""
    t = 1.0
    for S in _all_subsets(n):
        xs = sum(x[i] for i in S)
        ds = sum(d[i] for i in S)
        if ds > tol:
            bound = (fval(S) - xs) / ds
            if bound < t:
                t = bound
    return t


def _affine_minimizer(S):
    """S 的仿射极小点 y (min ||Σμ_i S_i||^2 s.t. Σμ_i=1) 及权重 μ."""
    m = len(S)
    n = len(S[0])
    P = [[S[j][i] for j in range(m)] for i in range(n)]  # n×m
    M = [[sum(P[i][a] * P[i][b] for i in range(n)) for b in range(m)] for a in range(m)]
    ones = [1.0] * m
    for i in range(m):
        M[i][i] += _RIDGE
    mu = _solve_square(M, ones)
    s = sum(mu)
    mu = [x / s for x in mu]
    y = [sum(mu[j] * S[j][i] for j in range(m)) for i in range(n)]
    return y, mu


def _affine_coeffs(S, xhat):
    """求 λ (Σλ=1) 使 Σλ_i S_i = xhat. 返回 λ (len=m)."""
    m = len(S)
    if m == 1:
        return [1.0]
    base = S[m - 1]
    B = [[S[j][i] - base[i] for j in range(m - 1)] for i in range(len(S[0]))]
    tgt = [xhat[i] - base[i] for i in range(len(S[0]))]
    lam = _lstsq(B, tgt)
    s = sum(lam)
    lam = list(lam) + [1.0 - s]
    return lam


# ---------------- 主算法 ----------------

def min_norm_point(func, V=None, max_iter=2000, tol=_TOL, rng=None):
    """返回使 f 最小化的集合 (frozenset of ground elements)."""
    if V is None:
        V = func.V
    n = len(V)
    rng = rng or random.Random(12345)

    cache = {}

    def fval(S_idx):
        key = frozenset(S_idx)
        if key not in cache:
            cache[key] = func.value({V[i] for i in key})
        return cache[key]

    S = [_extreme_base(list(range(n)), fval)]
    xhat = list(S[0])

    for _ in range(max_iter):
        # Step 2: GreedyMin — Edmonds 排序 (按 xhat 升序) 得极基 g 使 <xhat,g> 最小
        order = sorted(range(n), key=lambda i: xhat[i])
        g = _extreme_base(order, fval)
        dot = sum(xhat[i] * g[i] for i in range(n))
        xnorm2 = sum(xhat[i] * xhat[i] for i in range(n))
        if dot >= xnorm2 - tol:
            break
        # 主循环: S' = S ∪ {g}
        S = S + [g]
        y, mu = _affine_minimizer(S)
        if all(m > tol for m in mu):
            xhat = y
            continue
        # 次循环
        while True:
            lam = _affine_coeffs(S, xhat)
            # z = (1-β)xhat + β y, 选最大 β∈[0,1] 使所有系数 >= 0
            beta = 1.0
            for i in range(len(S)):
                if mu[i] - lam[i] < -tol:
                    b = lam[i] / (lam[i] - mu[i])
                    if b < beta:
                        beta = b
            new_coeff = [(1 - beta) * lam[i] + beta * mu[i] for i in range(len(S))]
            S = [S[i] for i in range(len(S)) if new_coeff[i] > tol]
            xhat = [(1 - beta) * xhat[i] + beta * y[i] for i in range(n)]
            y, mu = _affine_minimizer(S)
            if all(m > tol for m in mu):
                xhat = y
                break
    return frozenset(V[i] for i in range(n) if xhat[i] < -tol)


def min_norm_point_value(func, V=None, **kw):
    """返回最小化目标值."""
    S = min_norm_point(func, V=V, **kw)
    return func.value(S)
