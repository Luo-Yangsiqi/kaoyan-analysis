"""
灰色关联度雷达图
=================
以雷达图展示四类驱动机制（S1~S4）对 PEEHI 的灰色关联度，
替代原横向条形图，增强视觉表现力与维度对比感。
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import sys, io, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# ================================================================
# 1. 计算灰色关联度（与 grey_relational.py 完全一致）
# ================================================================
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)

peehi_df = pd.read_csv(os.path.join(script_dir, "PEEHI_热度指数.csv"))
df = pd.read_csv(os.path.join(project_dir, "data_show", "year.csv"))

years = df["年份"].values
Y = peehi_df["PEEHI_归一化"].values


def norm(v):
    return (v - np.nanmin(v)) / (np.nanmax(v) - np.nanmin(v))


def norm_rev(v):
    return (np.nanmax(v) - v) / (np.nanmax(v) - np.nanmin(v))


S1 = (norm(df["普通本科毕业生数(万)"].values) + norm(df["读研比例(%)"].values)) / 2

rs = df["实际月薪(2010年不变价,元)"].values
g = np.array([rs[1] / rs[0] - 1] + [rs[i] / rs[i - 1] - 1 for i in range(1, len(rs))]) * 100
emp_rev = norm_rev(df["受雇工作比例(%)"].values)
wage_stag = norm_rev(g)

unemp_raw = df["16-24岁青年失业率(%)"].values
has_unemp = ~np.isnan(unemp_raw)
unemp_norm = np.full(len(unemp_raw), np.nan)
unemp_norm[has_unemp] = norm(unemp_raw[has_unemp])

S2 = np.zeros(len(years))
for i in range(len(years)):
    if has_unemp[i]:
        S2[i] = (unemp_norm[i] + emp_rev[i] + wage_stag[i]) / 3
    else:
        S2[i] = (emp_rev[i] + wage_stag[i]) / 2

S3 = (norm(df["硕士实际录取人数(万)"].values) + norm(df["专硕占比(%)"].values)
      + df["政策哑变量(2020后=1)"].values) / 3
S4 = (norm(df["报名过审人数(万)"].values) + norm(df["报录比(X:1)"].values)) / 2

X = np.column_stack([S1, S2, S3, S4])

Y_norm = (Y - Y.min()) / (Y.max() - Y.min())
X_norm = (X - X.min(axis=0)) / (X.max(axis=0) - X.min(axis=0))

diff = np.abs(X_norm - Y_norm.reshape(-1, 1))
rho = 0.5
coef = (diff.min() + rho * diff.max()) / (diff + rho * diff.max())
grades = coef.mean(axis=0)

labels = ["S1 升学基数压力", "S2 就业市场压力", "S3 招生政策供给", "S4 考公替代压力"]
colors = ["#3498DB", "#E67E22", "#27AE60", "#9B59B6"]

# ================================================================
# 2. 雷达图绘制
# ================================================================
N = len(labels)
angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
angles += angles[:1]                 # 闭合

values = grades.tolist()
values += values[:1]                 # 闭合

fig, ax = plt.subplots(figsize=(9, 9), subplot_kw=dict(polar=True))
fig.patch.set_facecolor("white")

# ---- 2a. 网格与刻度 ----
ax.set_theta_offset(np.pi / 2)       # 让第一个轴从正上方开始
ax.set_theta_direction(-1)           # 顺时针

# 极轴刻度：从 0 到关联度最大值略多一点
r_max = np.ceil(max(grades) * 10) / 10 + 0.05
ax.set_ylim(0, r_max)
ax.set_yticks(np.linspace(0, r_max, 5))
ax.set_yticklabels([f"{t:.2f}" for t in np.linspace(0, r_max, 5)],
                   fontsize=8, color="#7F8C8D")
ax.set_rlabel_position(30)           # 刻度标签位置

# 浅色网格
ax.yaxis.grid(True, color="#E5E7E9", linewidth=1)
ax.xaxis.grid(True, color="#E5E7E9", linewidth=1)

# ---- 2b. 多边形填充 ----
ax.fill(angles, values, color="#3498DB", alpha=0.18, zorder=2)
ax.plot(angles, values, "o-", color="#2980B9", linewidth=2.5, markersize=10,
        markerfacecolor="white", markeredgewidth=2.5, markeredgecolor="#2980B9", zorder=3)

# ---- 2c. 顶点数据标签 ----
for a, v, lb, c in zip(angles[:-1], values[:-1], labels, colors):
    # 标签向外偏移
    ax.text(a, r_max + 0.03, lb, ha="center", va="center",
            fontsize=11, color=c, fontweight="bold")
    # 数值在顶点内侧
    ax.text(a, v - 0.04, f"{v:.4f}", ha="center", va="top",
            fontsize=12, color="#2C3E50", fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                      edgecolor=c, alpha=0.85))

# ---- 2d. 隐藏极轴边框 ----
ax.spines["polar"].set_visible(False)
ax.set_xticklabels([])

# ---- 2e. 解读标注 ----
# 在雷达图内部加入关联度排名
rank_order = np.argsort(-grades)
rank_text_lines = []
for rank, idx in enumerate(rank_order, 1):
    rank_text_lines.append(f"#{rank}  {labels[idx][3:]}  —  {grades[idx]:.4f}")
rank_text = "\n".join(rank_text_lines)

ax.text(0, 0, rank_text, ha="center", va="center",
        fontsize=10, color="#2C3E50",
        bbox=dict(boxstyle="round,pad=0.6", facecolor="#F8F9F9",
                  edgecolor="#BDC3C7", alpha=0.92))

# ---- 2f. 标题 ----
ax.set_title("灰色关联度雷达图：四类驱动机制对 PEEHI 的影响强度",
             fontsize=15, fontweight="bold", color="#1a5276", pad=28)

# 底部注释
fig.text(0.5, 0.02,
         f"分辨系数 ρ = 0.5  |  关联系数越接近 1，该机制与考研热度（PEEHI）的时序联动越紧密",
         ha="center", fontsize=9, color="#7F8C8D", style="italic")

plt.tight_layout(rect=[0, 0.05, 1, 0.95])
out = os.path.join(script_dir, "灰色关联度雷达图.png")
plt.savefig(out, dpi=200, bbox_inches="tight")
plt.close()
print(f"[OK] 已保存: {out}")

# ================================================================
# 3. 打印结果
# ================================================================
print("\n" + "=" * 55)
print("灰色关联度排序（ρ = 0.5）")
print("=" * 55)
for i in rank_order:
    bar = "█" * int(grades[i] * 60)
    print(f"  #{list(rank_order).index(i)+1}  {labels[i]:<16}  关联度 = {grades[i]:.4f}  {bar}")
