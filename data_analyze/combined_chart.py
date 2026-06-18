import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys, io, os
from matplotlib.lines import Line2D

# 保持环境设置
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# ---- 读取数据 (保持原逻辑) ----
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)

# 假设数据已存在，此处仅保留逻辑
peehi_df = pd.read_csv(os.path.join(script_dir, "PEEHI_热度指数.csv"))
df = pd.read_csv(os.path.join(project_dir, "data_show", "year.csv"))

years = df["年份"].values
x = np.arange(len(years))
PEEHI = peehi_df["PEEHI_归一化"].values

# ---- 计算四类子指数 (保持原逻辑) ----
def norm(v): return (v - np.nanmin(v)) / (np.nanmax(v) - np.nanmin(v)) * 100
def norm_rev(v): return (np.nanmax(v) - v) / (np.nanmax(v) - np.nanmin(v)) * 100

S1 = (norm(df["普通本科毕业生数(万)"].values) + norm(df["读研比例(%)"].values)) / 2
rs = df["实际月薪(2010年不变价,元)"].values
g = np.array([rs[1]/rs[0]-1] + [rs[i]/rs[i-1]-1 for i in range(1, len(rs))]) * 100
emp_rev = norm_rev(df["受雇工作比例(%)"].values)
wage_stag = norm_rev(g)

# S2: 青年失业率缺失年份仅用两个可得指标
unemp_raw = df["16-24岁青年失业率(%)"].values
has_unemp = ~np.isnan(unemp_raw)
unemp_norm = np.full(len(unemp_raw), np.nan)
unemp_norm[has_unemp] = norm(unemp_raw[has_unemp])  # 仅对有效值标准化

S2 = np.zeros(len(years))
for i in range(len(years)):
    if has_unemp[i]:
        S2[i] = (unemp_norm[i] + emp_rev[i] + wage_stag[i]) / 3
    else:
        S2[i] = (emp_rev[i] + wage_stag[i]) / 2
S3 = (norm(df["硕士实际录取人数(万)"].values) + norm(df["专硕占比(%)"].values) + df["政策哑变量(2020后=1)"].values * 100) / 3
S4 = (norm(df["报名过审人数(万)"].values) + norm(df["报录比(X:1)"].values)) / 2

# ================================================================
# 绘图优化版
# ================================================================
fig, ax = plt.subplots(figsize=(16, 8.5), facecolor='white')

# 设置背景网格
ax.grid(axis="y", color="#EAEDED", linestyle="-", linewidth=1, zorder=0)
ax.set_facecolor("#FDFDFD")

# ---- 1. 子指数：增加线宽和透明度，添加微小标记 ----
sub_lines_config = [
    (S1, "#3498DB", "升学基数压力", "o"), # 蓝色
    (S2, "#E67E22", "就业市场压力", "s"), # 橙红色
    (S3, "#27AE60", "招生政策供给", "^"), # 绿色
    (S4, "#9B59B6", "考公替代压力", "d"), # 紫色
]

for data, color, label, marker in sub_lines_config:
    # 绘制带轻微阴影效果的线条
    ax.plot(x, data, "-", color=color, linewidth=1.8, alpha=0.75, 
            marker=marker, markersize=4, markerfacecolor='white', markeredgewidth=1,
            label=label, zorder=2)

# ---- 2. PEEHI：核心主体（增加白色描边以突出） ----
# 填充背景
ax.fill_between(x, PEEHI, color="#1a5276", alpha=0.12, zorder=3)

# 绘制主线描边（白色底层，产生呼吸感）
ax.plot(x, PEEHI, "-", color="white", linewidth=5, alpha=0.8, zorder=4)

# 绘制主线
ax.plot(x, PEEHI, "o-", color="#1a5276", linewidth=3.8, markersize=11,
        markerfacecolor="white", markeredgewidth=3, markeredgecolor="#1a5276",
        zorder=5, label="★ PEEHI 考研热度指数")

# ---- 3. PEEHI 数据标签优化 ----
for xi, yi in zip(x, PEEHI):
    # 根据趋势动态调整标签高度
    va = "bottom" if yi < 40 else "top"
    offset = 6 if yi < 40 else -7
    ax.text(xi, yi + offset, f"{yi:.0f}", ha="center", va=va,
            fontsize=9, color="#1a5276", fontweight="bold",
            bbox=dict(facecolor='white', alpha=0.6, edgecolor='none', pad=1))

# ---- 4. 2020 政策拐点装饰 ----
ax.axvline(x=10, color="#7F8C8D", linestyle="--", linewidth=1.2, alpha=0.6, zorder=1)
ax.annotate("2020 政策拐点", xy=(10, 102), xytext=(10.2, 102),
            arrowprops=dict(arrowstyle="->", color="#5D6D7E"),
            fontsize=10, color="#2C3E50", fontweight="bold")

# ---- 5. 图例优化 ----
legend_elements = [
    Line2D([0], [0], color="#1a5276", linewidth=3.5, marker="o", markersize=9,
           markerfacecolor="white", markeredgecolor="#1a5276", label="★ PEEHI 考研热度指数"),
    Line2D([0], [0], color="#3498DB", linewidth=2, alpha=0.8, marker="o", markersize=5, label="升学基数压力"),
    Line2D([0], [0], color="#E67E22", linewidth=2, alpha=0.8, marker="s", markersize=5, label="就业市场压力"),
    Line2D([0], [0], color="#27AE60", linewidth=2, alpha=0.8, marker="^", markersize=5, label="招生政策供给"),
    Line2D([0], [0], color="#9B59B6", linewidth=2, alpha=0.8, marker="d", markersize=5, label="考公替代压力"),
]
ax.legend(handles=legend_elements, loc="upper left", fontsize=10, 
          frameon=True, facecolor="white", edgecolor="#D5DBDB",
          ncol=2, columnspacing=1.2, handletextpad=0.5)

# ---- 6. 坐标轴与标题 ----
ax.set_xticks(x)
ax.set_xticklabels(years, fontsize=11, color="#2C3E50")
ax.set_xlim(-0.6, 14.6)
ax.set_ylim(-2, 115) # 稍微调高上限给标签留空间
ax.set_ylabel("标准化指数值 (0–100)", fontsize=13, fontweight="bold", color="#1a5276")
ax.set_title("考研热度指数 PEEHI 与四类驱动机制（2010–2024）", 
             fontsize=20, fontweight="bold", pad=25, color="#1a5276")

# 移除多余边框
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color('#BDC3C7')
ax.spines['bottom'].set_color('#BDC3C7')

# 底注
fig.text(0.5, 0.02,
         "注：粗线为 PEEHI (综合热度指数)；细线为四类核心驱动因子 (经 Min-Max 标准化处理，反映相对变动强度)。",
         ha="center", fontsize=10, color="#7F8C8D", style='italic')

plt.tight_layout(rect=[0, 0.05, 1, 1])
out = os.path.join(script_dir, "PEEHI与四类机制合并图_优化版.png")
plt.savefig(out, dpi=300, bbox_inches="tight")
plt.close()