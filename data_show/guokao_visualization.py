"""
考公替代效应可视化（自变量3）
============================
输入：国考数据.csv、考研报名数据.csv
输出：
  1. 考研vs国考分阶段增速对比.png
  2. 国考报录比变化趋势.png
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ============================================================
# 中文字体设置
# ============================================================
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC"]
plt.rcParams["axes.unicode_minus"] = False

# ============================================================
# 读取数据
# ============================================================
df_gk = pd.read_csv("国考数据.csv")           # 年份, 招录计划人数(万), 报名过审人数(万), 报录比(X:1)
df_ky = pd.read_csv("考研报名数据.csv")        # 年份, 报名人数(万)

df = pd.merge(df_ky, df_gk, on="年份", how="inner")
df = df[df["年份"].between(2010, 2024)].copy()

years = df["年份"].values
x = np.arange(len(years))
ky_apply = df["报名人数(万)"].values
gk_apply = df["报名过审人数(万)"].values
gk_ratio = df["报录比(X:1)"].values

# 计算增长率
ky_growth = np.insert(np.diff(ky_apply) / ky_apply[:-1] * 100, 0, np.nan)
gk_growth = np.insert(np.diff(gk_apply) / gk_apply[:-1] * 100, 0, np.nan)

# ---- 配色 ----
C_RED    = "#E74C3C"
C_BLUE   = "#2980B9"
C_DARK   = "#2C3E50"
C_GREY   = "#7F8C8D"
C_ORANGE = "#E67E22"
C_GREEN  = "#27AE60"
C_PURPLE = "#8E44AD"

# ============================================================
# 图1：分阶段年均增速对比
# ============================================================
fig1, ax1 = plt.subplots(figsize=(14, 7))

# 阶段划分
stages = [
    ("2010–2015\n（存量博弈期）", 0, 5),
    ("2016–2019\n（考研升温期）", 5, 9),
    ("2020–2022\n（疫情冲击期）", 10, 12),
    ("2023–2024\n（替代效应期）", 13, 14),
]

stage_names = []
ky_avg_list = []
gk_avg_list = []

for name, start, end in stages:
    stage_names.append(name)
    ky_avg = np.nanmean(ky_growth[start+1:end+1])
    gk_avg = np.nanmean(gk_growth[start+1:end+1])
    ky_avg_list.append(ky_avg)
    gk_avg_list.append(gk_avg)

x1 = np.arange(len(stages))
width = 0.3

bars_ky = ax1.bar(x1 - width/2, ky_avg_list, width, color=C_RED, alpha=0.85,
                   edgecolor="#C0392B", linewidth=0.8, label="考研报名年均增速")
bars_gk = ax1.bar(x1 + width/2, gk_avg_list, width, color=C_BLUE, alpha=0.85,
                   edgecolor="#1A5276", linewidth=0.8, label="国考过审年均增速")

# 数据标签
for xi, kv, gv in zip(x1, ky_avg_list, gk_avg_list):
    ax1.text(xi - width/2, kv + 1.0 if kv >= 0 else kv - 3.0,
             f"{kv:+.1f}%", ha="center", fontsize=11, color=C_RED, fontweight="bold")
    ax1.text(xi + width/2, gv + 1.0 if gv >= 0 else gv - 3.0,
             f"{gv:+.1f}%", ha="center", fontsize=11, color=C_BLUE, fontweight="bold")

# 第一阶段标注
ax1.annotate("国考热度低\n考研温和增长",
             xy=(x1[0], ky_avg_list[0]),
             xytext=(x1[0] + 0.6, ky_avg_list[0] + 4),
             ha="center", fontsize=9, color=C_DARK,
             arrowprops=dict(arrowstyle="->", color=C_DARK, lw=1.2),
             bbox=dict(boxstyle="round,pad=0.3", facecolor="#F8F9F9", edgecolor=C_GREY, alpha=0.8))

ax1.axhline(y=0, color=C_DARK, linewidth=1.2)

# 动态设置 Y 轴范围，确保标签不溢出
y_bottom = min(min(ky_avg_list), min(gk_avg_list)) - 8
y_top = max(max(ky_avg_list), max(gk_avg_list)) + 8
ax1.set_ylim(y_bottom, y_top)

ax1.set_xticks(x1)
ax1.set_xticklabels(stage_names, fontsize=11)
ax1.set_ylabel("年均增长率（%）", fontsize=13, fontweight="bold")
ax1.set_title("考研 vs 国考：分阶段年均增长率对比（2010–2024）", fontsize=16, fontweight="bold", pad=15)
ax1.legend(loc="upper right", fontsize=11, framealpha=0.9)
ax1.grid(axis="y", alpha=0.3, linestyle="--")

fig1.text(0.5, 0.01,
          "数据来源：教育部历年统计公报（考研报名）、国家公务员局公告 + 华图教育汇总（国考数据）| "
          "注：增长率为各阶段内逐年增长率的算术平均，第一阶段因2010年基期增长率不可计算而少1个观测",
          ha="center", fontsize=9, color=C_GREY, style="italic")

plt.tight_layout(rect=[0, 0.04, 1, 1])
plt.savefig("考研vs国考分阶段增速对比.png", dpi=200, bbox_inches="tight")
plt.close()
print("[OK] 考研vs国考分阶段增速对比.png 已保存")

# ============================================================
# 图2：国考报录比变化趋势
# ============================================================
fig2, ax2 = plt.subplots(figsize=(14, 7))

# 分段配色
bar_colors = []
for v in gk_ratio:
    if v < 60:
        bar_colors.append("#ABEBC6")      # 浅绿 — 温和
    elif v < 80:
        bar_colors.append("#F9E79F")      # 浅黄 — 加剧
    else:
        bar_colors.append("#F1948A")      # 浅红 — 高度竞争

ax2.bar(x, gk_ratio, color=bar_colors, edgecolor=C_DARK, linewidth=0.8, width=0.65, zorder=3)
ax2.plot(x, gk_ratio, "o-", color=C_DARK, linewidth=2.8, markersize=9,
         markerfacecolor="white", markeredgewidth=2, zorder=5)

# 数据标签
for xi, v in zip(x, gk_ratio):
    ax2.text(xi, v + 1.8, f"{v:.0f}:1", ha="center", fontsize=9, color=C_DARK, fontweight="bold")

# 均值线
mean_ratio = gk_ratio.mean()
ax2.axhline(y=mean_ratio, color=C_ORANGE, linestyle="--", linewidth=1.5, alpha=0.7,
            label=f"均值: {mean_ratio:.1f}:1")

# 2019异常标注
idx_2019 = list(years).index(2019)
ax2.annotate("2019年\n国家机构改革\n（国地税合并）\n招录骤降至1.45万\n报录比异常飙升",
             xy=(idx_2019, gk_ratio[idx_2019]),
             xytext=(idx_2019 + 3, gk_ratio[idx_2019] - 25),
             ha="center", fontsize=10, color=C_RED, fontweight="bold",
             arrowprops=dict(arrowstyle="->", color=C_RED, lw=1.8, connectionstyle="arc3,rad=0.3"),
             bbox=dict(boxstyle="round,pad=0.4", facecolor="#FDEDEC", edgecolor=C_RED, alpha=0.9))

# 三区间图例色块
from matplotlib.patches import Patch
legend_patches = [
    Patch(facecolor="#ABEBC6", edgecolor=C_DARK, label="竞争温和（<60:1）"),
    Patch(facecolor="#F9E79F", edgecolor=C_DARK, label="竞争加剧（60-80:1）"),
    Patch(facecolor="#F1948A", edgecolor=C_DARK, label="高度竞争（>80:1）"),
]
handles, labels = ax2.get_legend_handles_labels()
ax2.legend(handles=handles + legend_patches, loc="upper left", fontsize=10, framealpha=0.9)

ax2.set_xticks(x)
ax2.set_xticklabels(years, rotation=0, fontsize=10)
ax2.set_ylabel("报录比（X : 1）", fontsize=13, fontweight="bold")
ax2.set_title("国考报录比变化趋势（过审人数 / 招录人数）", fontsize=16, fontweight="bold", pad=15)
ax2.grid(axis="y", alpha=0.3, linestyle="--")

fig2.text(0.5, 0.01,
          "数据来源：国家公务员局历年招录公告 → 华图教育、杭州本地宝新闻汇总 | "
          "注：报录比 = 报名过审人数 / 招录计划人数，2019年因机构改革招录骤降导致数值异常",
          ha="center", fontsize=9, color=C_GREY, style="italic")

plt.tight_layout(rect=[0, 0.04, 1, 1])
plt.savefig("国考报录比变化趋势.png", dpi=200, bbox_inches="tight")
plt.close()
print("[OK] 国考报录比变化趋势.png 已保存")

print("\n全部完成！共生成 2 张图表。")
