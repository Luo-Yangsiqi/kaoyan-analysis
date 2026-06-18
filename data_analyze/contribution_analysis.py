"""
四类机制贡献度分析 + 堆叠面积图
===============================
贡献度 C_i_t = S_i_t / (S1+S2+S3+S4)_t × 100%
展示考研热度驱动力的结构变迁
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys, io, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# ================================================================
# 1. 读取 & 计算 S1~S4（与其他脚本完全一致）
# ================================================================
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)

peehi_df = pd.read_csv(os.path.join(script_dir, "PEEHI_热度指数.csv"))
df = pd.read_csv(os.path.join(project_dir, "data_show", "year.csv"))

years = df["年份"].values
PEEHI = peehi_df["PEEHI_归一化"].values


def norm(v):
    return (v - np.nanmin(v)) / (np.nanmax(v) - np.nanmin(v)) * 100


def norm_rev(v):
    return (np.nanmax(v) - v) / (np.nanmax(v) - np.nanmin(v)) * 100


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
      + df["政策哑变量(2020后=1)"].values * 100) / 3
S4 = (norm(df["报名过审人数(万)"].values) + norm(df["报录比(X:1)"].values)) / 2

# ================================================================
# 2. 贡献度计算
# ================================================================
Total = S1 + S2 + S3 + S4
C1 = S1 / Total * 100
C2 = S2 / Total * 100
C3 = S3 / Total * 100
C4 = S4 / Total * 100

# ================================================================
# 3. 输出
# ================================================================
labels = ["S1 升学基数", "S2 就业市场", "S3 政策供给", "S4 考公替代"]
print(f"{'年份':<6} {'S1':<8} {'S2':<8} {'S3':<8} {'S4':<8} | {'C1%':<8} {'C2%':<8} {'C3%':<8} {'C4%':<8} | PEEHI")
print("-" * 85)
for t, year in enumerate(years):
    print(f"{year:<6} {S1[t]:<8.1f} {S2[t]:<8.1f} {S3[t]:<8.1f} {S4[t]:<8.1f} | "
          f"{C1[t]:<8.1f} {C2[t]:<8.1f} {C3[t]:<8.1f} {C4[t]:<8.1f} | {PEEHI[t]:.0f}")

# 全时段平均贡献度
print(f"\n{'─' * 55}")
print("全时段平均贡献度（2010–2024）：")
for i, lb in enumerate(labels):
    c = [C1, C2, C3, C4][i]
    print(f"  {lb}: {c.mean():.1f}%")

# 分阶段
stages = {"2010–2016 下行期": (0, 7), "2017–2019 回升期": (7, 10), "2020–2024 高位期": (10, 15)}
print(f"\n分阶段平均贡献度：")
print(f"{'阶段':<20} {'C1%':<8} {'C2%':<8} {'C3%':<8} {'C4%':<8}")
for name, (a, b) in stages.items():
    print(f"{name:<20} {C1[a:b].mean():<8.1f} {C2[a:b].mean():<8.1f} "
          f"{C3[a:b].mean():<8.1f} {C4[a:b].mean():<8.1f}")

# ================================================================
# 4. 堆叠面积图
# ================================================================
fig, ax = plt.subplots(figsize=(14, 7), facecolor="white")

colors_stack = ["#3498DB", "#E67E22", "#27AE60", "#9B59B6"]
ax.stackplot(years, C1, C2, C3, C4, labels=labels, colors=colors_stack, alpha=0.85)

# PEEHI 叠加为参考虚线
ax2 = ax.twinx()
ax2.plot(years, PEEHI, "o-", color="#1a5276", linewidth=2.8, markersize=7,
         markerfacecolor="white", markeredgewidth=2, zorder=5, label="PEEHI")
ax2.set_ylabel("PEEHI 热度指数", fontsize=12, fontweight="bold", color="#1a5276")
ax2.set_ylim(-5, 110)
ax2.tick_params(axis="y", labelcolor="#1a5276")

# 标注
for i, yr in enumerate(years):
    if i % 2 == 0:
        ax2.annotate(f"{PEEHI[i]:.0f}", (yr, PEEHI[i]), textcoords="offset points",
                     xytext=(0, 8), ha="center", fontsize=7.5, color="#1a5276", fontweight="bold")

# 2020 参考线
ax.axvline(x=2020, color="#333333", linestyle=":", linewidth=1.2, alpha=0.5)
ax.text(2020.1, 98, "← 2020", fontsize=10, color="#333333", va="top")

ax.set_xlim(2009.5, 2024.5)
ax.set_ylim(0, 100)
ax.set_ylabel("贡献度占比（%）", fontsize=12, fontweight="bold")
ax.set_title("考研热度四类驱动机制的贡献度结构变迁（2010–2024）", fontsize=16,
             fontweight="bold", color="#1a5276", pad=16)

# 合并图例
lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=9.5,
          framealpha=0.9, ncol=3)

ax.grid(axis="y", alpha=0.15, linestyle="--")
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)
    ax2.spines[spine].set_visible(False)

fig.text(0.5, 0.01, "注：堆叠面积 = 四类机制贡献度占比（总和恒为 100%）；"
         "虚线 = PEEHI 热度指数（右轴）。", ha="center", fontsize=9, color="#7F8C8D")

plt.tight_layout(rect=[0, 0.04, 1, 1])
out = os.path.join(script_dir, "贡献度堆叠面积图.png")
plt.savefig(out, dpi=200, bbox_inches="tight")
plt.close()
print(f"\n已保存: {out}")

# ---- 保存数据 ----
result = pd.DataFrame({
    "年份": years, "PEEHI": np.round(PEEHI, 1),
    "S1_升学基数": np.round(S1, 1), "S2_就业市场": np.round(S2, 1),
    "S3_政策供给": np.round(S3, 1), "S4_考公替代": np.round(S4, 1),
    "C1%": np.round(C1, 1), "C2%": np.round(C2, 1),
    "C3%": np.round(C3, 1), "C4%": np.round(C4, 1),
})
result.to_csv(os.path.join(script_dir, "贡献度分析.csv"), index=False, encoding="utf-8-sig")
print(f"已保存: 贡献度分析.csv")
