"""
四类驱动机制年均变化量可视化（2020–2024）
===========================================
棒棒糖图（lollipop chart）展示情景模拟所用的 ΔS 参数。
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys, io, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)

# ================================================================
# 1. 计算 S1-S4
# ================================================================
peehi_df = pd.read_csv(os.path.join(project_dir, "data_analyze", "PEEHI_热度指数.csv"))
df = pd.read_csv(os.path.join(project_dir, "data_show", "year.csv"))
years_hist = df["年份"].values


def norm(v):
    v = np.asarray(v, dtype=float)
    vmin, vmax = np.nanmin(v), np.nanmax(v)
    return np.zeros_like(v) if vmax == vmin else (v - vmin) / (vmax - vmin) * 100


def norm_rev(v):
    v = np.asarray(v, dtype=float)
    vmin, vmax = np.nanmin(v), np.nanmax(v)
    return np.zeros_like(v) if vmax == vmin else (vmax - v) / (vmax - vmin) * 100


S1 = (norm(df["普通本科毕业生数(万)"].values) + norm(df["读研比例(%)"].values)) / 2
rs = df["实际月薪(2010年不变价,元)"].values
g = np.full(len(rs), np.nan)
g[1:] = (rs[1:] / rs[:-1] - 1) * 100
S2 = np.nanmean(np.vstack([
    norm(df["16-24岁青年失业率(%)"].values),
    norm_rev(df["受雇工作比例(%)"].values),
    norm_rev(g)
]), axis=0)
S3 = (norm(df["硕士实际录取人数(万)"].values) + norm(df["专硕占比(%)"].values)
      + df["政策哑变量(2020后=1)"].values * 100) / 3
S4 = (norm(df["报名过审人数(万)"].values) + norm(df["报录比(X:1)"].values)) / 2

S_all = {"S1": S1, "S2": S2, "S3": S3, "S4": S4}

# 2020–2024 年均变化量（与 scenario_simulation.py 完全一致）
S_recent = {key: S_all[key][(years_hist >= 2020) & (years_hist <= 2024)]
            for key in ["S1", "S2", "S3", "S4"]}
dS_avg = {key: np.diff(S_recent[key]).mean() for key in ["S1", "S2", "S3", "S4"]}

# ================================================================
# 2. 配色 & 标签
# ================================================================
# 全新配色：深青 / 珊瑚 / 橄榄金 / 靛紫
COLORS = {
    "S1": "#2C6975",   # 深青
    "S2": "#E07B58",   # 珊瑚
    "S3": "#C9A12E",   # 橄榄金
    "S4": "#6C5F99",   # 靛紫
}
LABELS = {
    "S1": "升学基数压力\n(S1)",
    "S2": "就业市场压力\n(S2)",
    "S3": "招生政策供给\n(S3)",
    "S4": "考公替代压力\n(S4)",
}
C_DARK = "#2C3E50"
C_GREY = "#95A5A6"
BG = "#FCFCFC"

# ================================================================
# 3. 棒棒糖图
# ================================================================
fig, ax = plt.subplots(figsize=(10, 7))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

keys = ["S1", "S2", "S3", "S4"]
vals = [dS_avg[k] for k in keys]
y_pos = [3, 2, 1, 0]  # 自上而下

for y, key, v in zip(y_pos, keys, vals):
    color = COLORS[key]
    # 茎线
    ax.plot([0, v], [y, y], "-", color=color, linewidth=3.5, alpha=0.7, solid_capstyle="round")
    # 端点圆圈
    ax.scatter(v, y, s=280, color="white", edgecolor=color, linewidth=3, zorder=5)
    # 端点数值
    ax.text(v, y, f"  {v:+.1f}", ha="left" if v >= 0 else "right", va="center",
            fontsize=14, color=color, fontweight="bold")

# 零线
ax.axvline(x=0, color=C_GREY, linewidth=1.5, alpha=0.5, zorder=1)

# 均值虚线
avg_dS = np.mean(vals)
ax.axvline(x=avg_dS, color=C_GREY, linestyle=(0, (5, 3)), linewidth=1.2, alpha=0.6)
ax.text(avg_dS, 3.55, f"均值\n{avg_dS:+.1f}", ha="center", fontsize=8.5, color=C_GREY)

# Y 轴
ax.set_yticks(y_pos)
ax.set_yticklabels([LABELS[k] for k in keys], fontsize=11)
ax.set_ylim(-0.8, 3.8)

# X 轴
x_abs_max = max(abs(min(vals)), abs(max(vals))) * 1.25
ax.set_xlim(-2, x_abs_max)
ax.set_xlabel("年均变化量（标准化单位 / 年）", fontsize=12, fontweight="bold", color=C_DARK)

# 网格
ax.xaxis.grid(True, alpha=0.2, linestyle="--")
ax.yaxis.grid(False)

# 标题
ax.set_title("四类驱动机制年均变化量（2020–2024）", fontsize=16, fontweight="bold",
             color=C_DARK, pad=20)

# 解读文本
max_key = max(dS_avg, key=dS_avg.get)
min_key = min(dS_avg, key=dS_avg.get)
ax.text(0.98, 0.08,
        f"增长最快：{LABELS[max_key].split(chr(10))[0]}（{dS_avg[max_key]:+.1f}/年）\n"
        f"增长最慢：{LABELS[min_key].split(chr(10))[0]}（{dS_avg[min_key]:+.1f}/年）",
        transform=ax.transAxes, ha="right", fontsize=9.5, color=C_DARK,
        bbox=dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor="#E0E0E0", alpha=0.9))

# 边框
for spine in ["top", "right", "left"]:
    ax.spines[spine].set_visible(False)
ax.spines["bottom"].set_color("#E0E0E0")

fig.text(0.5, 0.01,
         "注：变化量基于标准化后 S 指数（0–100）计算，反映近五年各类压力的平均变动速率；"
         "该参数直接用于情景模拟的外推设定。",
         ha="center", fontsize=8.5, color=C_GREY, style="italic")

plt.tight_layout(rect=[0, 0.04, 1, 1])
out = os.path.join(script_dir, "年均变化量棒棒糖图.png")
plt.savefig(out, dpi=200, bbox_inches="tight")
plt.close()
print(f"[OK] 已保存: {out}")

# ================================================================
print("\n" + "=" * 55)
print("2020–2024 年均变化量")
print("=" * 55)
for key in ["S1", "S2", "S3", "S4"]:
    direction = "↑" if dS_avg[key] > 0 else "↓"
    bar = "█" * int(abs(dS_avg[key]) * 2)
    print(f"  {key} {LABELS[key].split(chr(10))[0]:<8}  {direction} {dS_avg[key]:+.2f}/年  {bar}")
