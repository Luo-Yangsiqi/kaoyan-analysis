"""
PEEHI 考研热度指数 — 时间趋势图（2010–2024）
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import sys, io, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ---- 字体 ----
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# ---- 读取 ----
script_dir = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(script_dir, "PEEHI_热度指数.csv"))

years = df["年份"].values
peehi = df["PEEHI_归一化"].values
x = np.arange(len(years))

# ---- 配色 ----
DARK_BLUE = "#1a5276"
MID_BLUE = "#2980B9"
LIGHT_BLUE = "#85C1E9"
RED = "#C0392B"
ORANGE = "#E67E22"
GRAY = "#7F8C8D"

# ---- 绘图 ----
fig, ax = plt.subplots(figsize=(14, 7))

# 面积填充
ax.fill_between(x, peehi, color=LIGHT_BLUE, alpha=0.35)

# 主折线
ax.plot(x, peehi, "o-", color=MID_BLUE, linewidth=2.8, markersize=9,
        markerfacecolor="white", markeredgewidth=2, markeredgecolor=DARK_BLUE, zorder=5)

# ---- 数据标签 ----
for xi, yi in zip(x, peehi):
    offset = 4 if yi < 50 else -5
    ax.text(xi, yi + offset, f"{yi:.0f}", ha="center", fontsize=8.5,
            color=DARK_BLUE, fontweight="bold")

# ---- 标注关键节点（数据驱动，自动对齐） ----
# 找到最低点和最高点的年份
idx_min = np.argmin(peehi)
idx_max = np.argmax(peehi)

# 最低点
ax.annotate(f"{int(years[idx_min])}\n冰点 {peehi[idx_min]:.0f}",
            xy=(x[idx_min], peehi[idx_min]),
            textcoords="offset points", xytext=(0, -22),
            ha="center", fontsize=8.5, color=RED,
            arrowprops=dict(arrowstyle="->", color=GRAY, lw=1.2,
                          connectionstyle="arc3,rad=0.15"),
            bbox=dict(boxstyle="round,pad=0.25", facecolor="#FEF9E7",
                      edgecolor=ORANGE, alpha=0.85))

# 最高点
ax.annotate(f"{int(years[idx_max])}\n峰值 {peehi[idx_max]:.0f}",
            xy=(x[idx_max], peehi[idx_max]),
            textcoords="offset points", xytext=(-65, -18),
            ha="center", fontsize=8.5, color=RED,
            arrowprops=dict(arrowstyle="->", color=GRAY, lw=1.2,
                          connectionstyle="arc3,rad=0.15"),
            bbox=dict(boxstyle="round,pad=0.25", facecolor="#FEF9E7",
                      edgecolor=ORANGE, alpha=0.85))

# 2020 政策节点
idx_2020 = list(years).index(2020)
ax.annotate(f"2020\n跳升 {peehi[idx_2020]:.0f}",
            xy=(x[idx_2020], peehi[idx_2020]),
            textcoords="offset points", xytext=(-55, 22),
            ha="center", fontsize=8.5, color=RED,
            arrowprops=dict(arrowstyle="->", color=GRAY, lw=1.2,
                          connectionstyle="arc3,rad=0.15"),
            bbox=dict(boxstyle="round,pad=0.25", facecolor="#FEF9E7",
                      edgecolor=ORANGE, alpha=0.85))

# 2024 最新值
idx_2024 = list(years).index(2024)
ax.annotate(f"2024\n回落 {peehi[idx_2024]:.0f}",
            xy=(x[idx_2024], peehi[idx_2024]),
            textcoords="offset points", xytext=(30, -20),
            ha="center", fontsize=8.5, color=RED,
            arrowprops=dict(arrowstyle="->", color=GRAY, lw=1.2,
                          connectionstyle="arc3,rad=0.15"),
            bbox=dict(boxstyle="round,pad=0.25", facecolor="#FEF9E7",
                      edgecolor=ORANGE, alpha=0.85))

# 2019 跳升前基准
idx_2019 = list(years).index(2019)
ax.annotate(f"2019\n{peehi[idx_2019]:.0f}",
            xy=(x[idx_2019], peehi[idx_2019]),
            textcoords="offset points", xytext=(40, 10),
            ha="center", fontsize=8.5, color=RED,
            arrowprops=dict(arrowstyle="->", color=GRAY, lw=1.2,
                          connectionstyle="arc3,rad=0.15"),
            bbox=dict(boxstyle="round,pad=0.25", facecolor="#FEF9E7",
                      edgecolor=ORANGE, alpha=0.85))

# ---- 阶段分区 ----
# 2010–2016 热度下行期
ax.axvspan(-0.5, 6.5, alpha=0.06, color=GRAY)
ax.text(3, 105, "热度下行期", ha="center", fontsize=11, color=GRAY, fontweight="bold")

# 2017–2019 快速回升
ax.axvspan(6.5, 9.5, alpha=0.06, color=ORANGE)
ax.text(8, 105, "快速回升期", ha="center", fontsize=11, color=ORANGE, fontweight="bold")

# 2020–2024 政策驱动高位
ax.axvspan(9.5, 14.5, alpha=0.08, color="#F39C12")
ax.text(12, 105, "政策驱动高位期\n(专硕扩招+疫情影响)", ha="center", fontsize=10,
        color="#D35400", fontweight="bold")

# ---- 参考线 ----
ax.axhline(y=50, color=GRAY, linestyle="--", linewidth=0.8, alpha=0.5)

# ---- 坐标轴 ----
ax.set_xticks(x)
ax.set_xticklabels(years, fontsize=10)
ax.set_xlim(-0.8, 14.8)
ax.set_ylim(-5, 115)
ax.set_ylabel("PEEHI 考研热度指数", fontsize=14, fontweight="bold", color=DARK_BLUE)
ax.set_title("中国考研综合热度指数（PEEHI）时间趋势\n2010 — 2024", fontsize=17,
             fontweight="bold", color=DARK_BLUE, pad=18)

# 底部注释
fig.text(0.5, 0.01,
         f"注：PEEHI 基于参与率(X1)、报录比(X2)、统考竞争度(X3) 3 项指标，"
         f"采用熵权法赋权并归一化至 0–100。"
         f"{int(years[idx_min])}={peehi[idx_min]:.0f}（最低点），{int(years[idx_max])}={peehi[idx_max]:.0f}（最高点）。",
         ha="center", fontsize=9, color=GRAY)

ax.grid(axis="y", alpha=0.25, linestyle="--")
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f"{v:.0f}"))

plt.tight_layout(rect=[0, 0.04, 1, 1])
plt.savefig(os.path.join(script_dir, "PEEHI_趋势图.png"), dpi=200, bbox_inches="tight")
plt.close()
print("已保存: PEEHI_趋势图.png")
