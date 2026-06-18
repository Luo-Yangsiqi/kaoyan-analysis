"""
考研热度情景模拟（2025–2030）
=============================
改进版：
- 2024 年 PEEHI 锚定校准
- 安全版 norm / norm_rev（兼容 NaN）
- S2 用 np.nanmean 自动处理缺失
- 考公分流：先算机制路径，再减分流折减
- 薪资增长率 2010 年留空而非替代
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import sys, io, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# ================================================================
# 1. 读取 & 安全版标准化函数
# ================================================================
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)

peehi_df = pd.read_csv(os.path.join(project_dir, "data_analyze", "PEEHI_热度指数.csv"))
df = pd.read_csv(os.path.join(project_dir, "data_show", "year.csv"))

years_hist = df["年份"].values
PEEHI_hist = peehi_df["PEEHI_归一化"].values


def norm(v):
    v = np.asarray(v, dtype=float)
    vmin, vmax = np.nanmin(v), np.nanmax(v)
    if vmax == vmin:
        return np.zeros_like(v)
    return (v - vmin) / (vmax - vmin) * 100


def norm_rev(v):
    v = np.asarray(v, dtype=float)
    vmin, vmax = np.nanmin(v), np.nanmax(v)
    if vmax == vmin:
        return np.zeros_like(v)
    return (vmax - v) / (vmax - vmin) * 100


# ================================================================
# 2. 计算四类子指数
# ================================================================
S1 = (norm(df["普通本科毕业生数(万)"].values) + norm(df["读研比例(%)"].values)) / 2

# S2：实际薪资增长率 2010 年留 NaN，np.nanmean 自动忽略
rs = df["实际月薪(2010年不变价,元)"].values
g = np.full(len(rs), np.nan)
g[1:] = (rs[1:] / rs[:-1] - 1) * 100
unemp_norm = norm(df["16-24岁青年失业率(%)"].values)
emp_rev = norm_rev(df["受雇工作比例(%)"].values)
wage_stag = norm_rev(g)
S2 = np.nanmean(np.vstack([unemp_norm, emp_rev, wage_stag]), axis=0)

S3 = (norm(df["硕士实际录取人数(万)"].values) + norm(df["专硕占比(%)"].values)
      + df["政策哑变量(2020后=1)"].values * 100) / 3
S4 = (norm(df["报名过审人数(万)"].values) + norm(df["报录比(X:1)"].values)) / 2

S_hist = pd.DataFrame({"年份": years_hist, "S1": S1, "S2": S2, "S3": S3, "S4": S4})
X_hist = np.column_stack([S1, S2, S3, S4])

# ================================================================
# 3. 灰色关联度 → 机制权重
# ================================================================
Y_norm = (PEEHI_hist - PEEHI_hist.min()) / (PEEHI_hist.max() - PEEHI_hist.min())
X_norm = (X_hist - X_hist.min(axis=0)) / (X_hist.max(axis=0) - X_hist.min(axis=0))
diff = np.abs(X_norm - Y_norm.reshape(-1, 1))
rho = 0.5
coef = (diff.min() + rho * diff.max()) / (diff + rho * diff.max())
grey_grades = coef.mean(axis=0)
weights = grey_grades / grey_grades.sum()
w = dict(zip(["S1", "S2", "S3", "S4"], weights))
w_vec = np.array([w["S1"], w["S2"], w["S3"], w["S4"]])

print("灰色关联度归一化权重：")
for k, v in w.items():
    print(f"  {k}: {v:.4f}")

# ================================================================
# 4. 近五年（2020–2024）年均变化量
# ================================================================
recent = S_hist[S_hist["年份"].between(2020, 2024)]
dS_avg = recent[["S1", "S2", "S3", "S4"]].diff().mean()
print(f"\n2020–2024 年均变化量：")
for k in ["S1", "S2", "S3", "S4"]:
    print(f"  Δ{k} = {dS_avg[k]:+.2f}/年")

# ================================================================
# 5. 未来 S 外推
# ================================================================
future_years = np.arange(2025, 2031)
last_S = S_hist.loc[S_hist["年份"] == 2024, ["S1", "S2", "S3", "S4"]].values[0]


def simulate(dS, last, n=6):
    trace, cur = [], last.copy()
    for _ in range(n):
        cur = cur + dS
        cur = np.clip(cur, 0, 100)
        trace.append(cur.copy())
    return np.array(trace)


# ================================================================
# 6. 锚定校准：从 2024 年真实 PEEHI 自然延伸
# ================================================================
score_hist = np.dot(X_hist, w_vec)
score_2024 = score_hist[-1]
peehi_2024 = PEEHI_hist[-1]

print(f"\n2024 锚定：真实 PEEHI={peehi_2024:.1f}，机制得分={score_2024:.1f}")


def calibrated_peehi(S_mat):
    score = np.dot(S_mat, w_vec)
    return np.clip(peehi_2024 + (score - score_2024), 0, 100)


def make_scenario(multipliers=None, diversion_elasticity=None):
    """
    multipliers 用于调整 S1-S4 的年均变化量。
    diversion_elasticity 表示考公/其他路径对考研热的额外分流强度。
    """
    multipliers = multipliers or {}
    dS = dS_avg.copy()

    for key, value in multipliers.items():
        dS[key] *= value

    S_future = simulate(dS.values, last_S)
    peehi_future = calibrated_peehi(S_future)

    if diversion_elasticity is not None:
        # lam 先抵消 S4 的机制正向权重，再加入额外分流弹性，避免 0.2 这类经验拍值。
        lam = w_vec[3] + diversion_elasticity
        S4_2024 = S_hist.loc[S_hist["年份"] == 2024, "S4"].values[0]
        peehi_future = peehi_future - lam * (S_future[:, 3] - S4_2024)
        peehi_future = np.clip(peehi_future, 0, 100)

    return S_future, peehi_future


# 1. 基准延续：沿用 2020-2024 年均变化趋势
S_base, PEEHI_base = make_scenario()

# 2. 就业压力加剧：就业压力指标 S2 上升更快
S_emp, PEEHI_emp = make_scenario({"S2": 1.5})

# 3. 考公分流：考公竞争增强，同时对考研形成额外分流
S_split, PEEHI_split = make_scenario({"S4": 1.3}, diversion_elasticity=0.10)

# 4. 综合治理降温：改善就业、优化招生、拓宽多元发展路径，使非理性升学压力主动回落
S_policy, PEEHI_policy = make_scenario({
    "S1": 0.2,    # 参与冲动明显放缓
    "S2": -0.4,   # 就业压力逐步回落
    "S3": 0.0,    # 招生扩张刺激趋于稳定
    "S4": -0.2,   # 外部竞争压力缓和
})

# ================================================================
# 7. 输出
# ================================================================
print(f"\n{'年份':<6} {'S1':<8} {'S2':<8} {'S3':<8} {'S4':<8} | "
      f"{'基准':<8} {'就业加剧':<10} {'考公分流':<10} {'综合治理':<10}")
print("-" * 90)
for i, yr in enumerate(future_years):
    print(f"{yr:<6} {S_base[i,0]:<8.1f} {S_base[i,1]:<8.1f} "
          f"{S_base[i,2]:<8.1f} {S_base[i,3]:<8.1f} | "
          f"{PEEHI_base[i]:<8.1f} {PEEHI_emp[i]:<10.1f} "
          f"{PEEHI_split[i]:<10.1f} {PEEHI_policy[i]:<10.1f}")

# 历史 vs 机制得分一致性
print(f"\n历史 PEEHI 与机制得分相关性：r = {np.corrcoef(PEEHI_hist, score_hist)[0,1]:.4f}")

# ================================================================
# 8. 可视化
# ================================================================
fig, ax = plt.subplots(figsize=(14, 7.5), facecolor="white")

ax.plot(years_hist, PEEHI_hist, "o-", color="#1a5276", linewidth=3.2, markersize=8,
        markerfacecolor="white", markeredgewidth=2.5, zorder=6, label="历史 PEEHI")

ax.axvline(x=2024.4, color="#7F8C8D", linestyle="--", linewidth=1.2, alpha=0.7)
ax.text(2024.6, 108, "← 模拟期", fontsize=10, color="#7F8C8D", va="top")

scenarios = [
    (PEEHI_base, "#27AE60", "基准延续情景"),
    (PEEHI_emp,  "#E74C3C", "就业压力加剧"),
    (PEEHI_split, "#8E44AD", "考公分流情景"),
    (PEEHI_policy, "#F39C12", "综合治理降温"),
]
for peehi_sim, color, label in scenarios:
    ax.plot(future_years, peehi_sim, "s--", color=color, linewidth=2.2, markersize=7,
            markerfacecolor="white", markeredgewidth=1.8, zorder=5, label=label)

# 标签
for yr, py in zip(years_hist, PEEHI_hist):
    if yr in [2010, 2016, 2019, 2020, 2023, 2024]:
        ax.annotate(f"{py:.0f}", (yr, py), textcoords="offset points",
                    xytext=(0, 10), ha="center", fontsize=8.5, color="#1a5276", fontweight="bold")

for yr, pb, pe, ps, pp in zip(future_years, PEEHI_base, PEEHI_emp, PEEHI_split, PEEHI_policy):
    ax.annotate(f"{pb:.0f}", (yr, pb), textcoords="offset points",
                xytext=(-14, -14), ha="center", fontsize=7.5, color="#27AE60")
    ax.annotate(f"{pe:.0f}", (yr, pe), textcoords="offset points",
                xytext=(14, -14), ha="center", fontsize=7.5, color="#E74C3C")
    ax.annotate(f"{ps:.0f}", (yr, ps), textcoords="offset points",
                xytext=(0, 10), ha="center", fontsize=7.5, color="#8E44AD")
    ax.annotate(f"{pp:.0f}", (yr, pp), textcoords="offset points",
                xytext=(0, -26), ha="center", fontsize=7.5, color="#F39C12")

legend_elements = [
    Line2D([0], [0], color="#1a5276", linewidth=3, marker="o", markersize=7,
           markerfacecolor="white", markeredgecolor="#1a5276", label="历史 PEEHI"),
    Line2D([0], [0], color="#27AE60", linewidth=2.2, linestyle="--", marker="s", markersize=6,
           markerfacecolor="white", markeredgecolor="#27AE60", label="基准延续情景"),
    Line2D([0], [0], color="#E74C3C", linewidth=2.2, linestyle="--", marker="s", markersize=6,
           markerfacecolor="white", markeredgecolor="#E74C3C", label="就业压力加剧"),
    Line2D([0], [0], color="#8E44AD", linewidth=2.2, linestyle="--", marker="s", markersize=6,
           markerfacecolor="white", markeredgecolor="#8E44AD", label="考公分流情景"),
    Line2D([0], [0], color="#F39C12", linewidth=2.2, linestyle="--", marker="s", markersize=6,
           markerfacecolor="white", markeredgecolor="#F39C12", label="综合治理降温"),
]
ax.legend(handles=legend_elements, loc="upper left", fontsize=9.5, framealpha=0.92, ncol=2)

ax.set_xticks(np.arange(2010, 2031, 2))
ax.set_xticklabels(np.arange(2010, 2031, 2), fontsize=10)
ax.set_xlim(2009.3, 2030.7)
ax.set_ylim(-5, 115)
ax.set_ylabel("PEEHI 考研热度指数", fontsize=13, fontweight="bold")
ax.set_title("2025–2030 年考研热度情景模拟", fontsize=17, fontweight="bold",
             color="#1a5276", pad=16)
ax.grid(axis="y", alpha=0.15, linestyle="--")
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)

fig.text(0.5, 0.01,
         "注：以 2024 年真实 PEEHI 为锚定点，基于灰色关联度权重与 2020–2024 年年均变化量外推；"
         "四条曲线反映不同外部条件与政策干预下的可能路径，非精确预测。",
         ha="center", fontsize=9, color="#7F8C8D")

plt.tight_layout(rect=[0, 0.04, 1, 1])
out = os.path.join(script_dir, "情景模拟.png")
plt.savefig(out, dpi=200, bbox_inches="tight")
plt.close()
print(f"\n已保存: {out}")

# ================================================================
# 9. 保存数据
# ================================================================
sim_result = pd.DataFrame({
    "年份": future_years,
    "S1_基准": np.round(S_base[:, 0], 1),
    "S2_基准": np.round(S_base[:, 1], 1),
    "S3_基准": np.round(S_base[:, 2], 1),
    "S4_基准": np.round(S_base[:, 3], 1),
    "PEEHI_基准延续情景": np.round(PEEHI_base, 1),
    "PEEHI_就业压力加剧情景": np.round(PEEHI_emp, 1),
    "PEEHI_考公分流情景": np.round(PEEHI_split, 1),
    "PEEHI_综合治理降温情景": np.round(PEEHI_policy, 1),
})
sim_result.to_csv(os.path.join(script_dir, "情景模拟结果.csv"), index=False, encoding="utf-8-sig")
print(f"已保存: 情景模拟结果.csv")
