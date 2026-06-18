"""
四类机制子指数折线图（2010–2024）
================================
① 升学基数压力 = 本科毕业生数标准化 + 读研比例标准化
② 就业市场压力 = 青年失业率标准化 + 受雇工作比例反向标准化 + 薪资增长放缓指标
③ 招生政策供给 = 硕士录取人数标准化 + 专硕占比标准化 + 政策哑变量
④ 考公替代压力 = 国考过审人数标准化 + 国考报录比标准化
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import sys, io, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# ---- 辅助函数 ----
def norm(x):
    """Min-Max 标准化到 0–100"""
    return (x - np.nanmin(x)) / (np.nanmax(x) - np.nanmin(x)) * 100

def norm_reverse(x):
    """反向标准化：原始值越小 → 标准化值越大"""
    return (np.nanmax(x) - x) / (np.nanmax(x) - np.nanmin(x)) * 100

# ---- 读取 ----
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
df = pd.read_csv(os.path.join(project_dir, "data_show", "year.csv"))
years = df["年份"].values
x = np.arange(len(years))

# ================================================================
# ① 升学基数压力
# ================================================================
s1a = norm(df["普通本科毕业生数(万)"].values)
s1b = norm(df["读研比例(%)"].values)
S1 = (s1a + s1b) / 2

# ================================================================
# ② 就业市场压力
# ================================================================
# 2a: 青年失业率 — 仅对有效值标准化，缺失年份不参与
unemp_raw = df["16-24岁青年失业率(%)"].values
has_unemp = ~np.isnan(unemp_raw)
s2a = np.full(len(unemp_raw), np.nan)
s2a[has_unemp] = norm(unemp_raw[has_unemp])

# 2b: 受雇工作比例 → 反向（就业率越低，压力越大）
s2b = norm_reverse(df["受雇工作比例(%)"].values)

# 2c: 实际月薪同比增长率 → 反向（增速越低，压力越大）
real_salary = df["实际月薪(2010年不变价,元)"].values
growth = np.array([np.nan] + [real_salary[i] / real_salary[i-1] - 1 for i in range(1, len(real_salary))])
growth_pct = growth * 100
growth_pct[0] = growth_pct[1]
s2c = norm_reverse(growth_pct)

S2 = np.zeros(len(years))
for i in range(len(years)):
    if has_unemp[i]:
        S2[i] = (s2a[i] + s2b[i] + s2c[i]) / 3
    else:
        S2[i] = (s2b[i] + s2c[i]) / 2

# ================================================================
# ③ 招生政策供给
# ================================================================
s3a = norm(df["硕士实际录取人数(万)"].values)
s3b = norm(df["专硕占比(%)"].values)
s3c = df["政策哑变量(2020后=1)"].values * 100  # 0→0, 1→100
S3 = (s3a + s3b + s3c) / 3

# ================================================================
# ④ 考公替代压力
# ================================================================
s4a = norm(df["报名过审人数(万)"].values)
s4b = norm(df["报录比(X:1)"].values)
S4 = (s4a + s4b) / 2

# ================================================================
# 绘图
# ================================================================
fig, ax = plt.subplots(figsize=(15, 8))

COLORS = {
    "S1": ("#2980B9", "升学基数压力\n(毕业生+读研比)"),
    "S2": ("#E74C3C", "就业市场压力\n(失业率+就业率↓+薪资放缓)"),
    "S3": ("#27AE60", "招生政策供给\n(硕士扩招+专硕占比+政策)"),
    "S4": ("#8E44AD", "考公替代压力\n(国考过审+报录比)"),
}

for key, (color, label) in COLORS.items():
    data = {"S1": S1, "S2": S2, "S3": S3, "S4": S4}[key]
    ax.plot(x, data, "o-", color=color, linewidth=2.2, markersize=6,
            markerfacecolor="white", markeredgewidth=1.8, label=label, zorder=4)

# ---- 标注关键拐点 ----
# 标注 2020 政策线
ax.axvline(x=10, color="#333333", linestyle=":", linewidth=1.2, alpha=0.6)
ax.text(10.15, 98, "← 2020\n专硕扩招方案发布", fontsize=9, color="#333333", va="top")

# ---- 坐标 ----
ax.set_xticks(x)
ax.set_xticklabels(years, fontsize=9.5)
ax.set_xlim(-0.5, 14.5)
ax.set_ylim(-5, 105)
ax.set_ylabel("子指数（标准化 0–100）", fontsize=13, fontweight="bold")
ax.set_title("考研热度四类驱动机制子指数变化（2010–2024）", fontsize=16,
             fontweight="bold", pad=16)

ax.legend(loc="upper left", fontsize=9.5, framealpha=0.9,
          ncol=2, columnspacing=0.8)

ax.grid(axis="y", alpha=0.2, linestyle="--")

# 注释
fig.text(0.5, 0.01,
         "注：各子指数为对应类别内指标的 Min-Max 标准化均值（0–100）。"
         "就业市场压力中，2010–2017 年青年失业率数据缺失，以 0 替代。",
         ha="center", fontsize=8.5, color="#7F8C8D")

plt.tight_layout(rect=[0, 0.04, 1, 1])
out = os.path.join(script_dir, "四类机制子指数趋势图.png")
plt.savefig(out, dpi=200, bbox_inches="tight")
plt.close()
print(f"已保存: {out}")

# ---- 打印数据 ----
print(f"\n{'年份':<6} {'升学基数':<10} {'就业市场':<10} {'政策供给':<10} {'考公替代':<10}")
print("-" * 50)
for i, year in enumerate(years):
    print(f"{year:<6} {S1[i]:<10.1f} {S2[i]:<10.1f} {S3[i]:<10.1f} {S4[i]:<10.1f}")
