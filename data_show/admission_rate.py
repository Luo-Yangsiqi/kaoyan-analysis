import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

# ============================================================
# 1. 读取数据 & 合并
# ============================================================
df_apply = pd.read_csv("考研报名数据.csv")      # 年份, 报名人数(万)
df_admit = pd.read_csv("硕士录取数据.csv")      # 年份, 硕士实际录取人数(万)

df = pd.merge(df_apply, df_admit, on="年份", how="inner")  # 取交集 (2010-2024)

# ============================================================
# 2. 计算衍生指标
# ============================================================
df["录取率"] = df["硕士实际录取人数(万)"] / df["报名人数(万)"]        # ① 考研录取率
df["竞争指数"] = df["报名人数(万)"] / df["硕士实际录取人数(万)"]      # ② 考研竞争指数
df["落榜人数(万)"] = df["报名人数(万)"] - df["硕士实际录取人数(万)"]

print("=" * 70)
print("考研数据汇总 (2010-2024)")
print("=" * 70)
print(f"{'年份':<6} {'报名(万)':<10} {'录取(万)':<10} {'录取率':<10} {'竞争指数':<10}")
print("-" * 70)
for _, row in df.iterrows():
    print(f"{int(row['年份']):<6} {row['报名人数(万)']:<10.2f} {row['硕士实际录取人数(万)']:<10.2f} "
          f"{row['录取率']:<10.4f} {row['竞争指数']:<10.2f}")
print("=" * 70)
print(f"平均录取率: {df['录取率'].mean():.4f}  ({df['录取率'].mean()*100:.2f}%)")
print(f"平均竞争指数: {df['竞争指数'].mean():.2f}  (约 {df['竞争指数'].mean():.0f} 人抢 1 个名额)")

# ============================================================
# 3. 中文字体设置
# ============================================================
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC"]
plt.rcParams["axes.unicode_minus"] = False

# ============================================================
# 4. 可视化 — 四合一仪表盘
# ============================================================
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle("中国考研数据可视化 (2010–2024)", fontsize=20, fontweight="bold", y=0.98)

years = df["年份"].values
x = np.arange(len(years))

# ---- 子图1: 报名人数 vs 录取人数 ----
ax1 = axes[0, 0]
ax1.bar(x - 0.15, df["报名人数(万)"], width=0.3, color="#E74C3C", alpha=0.85, label="报名人数")
ax1.bar(x + 0.15, df["硕士实际录取人数(万)"], width=0.3, color="#2ECC71", alpha=0.85, label="录取人数")
ax1.plot(x, df["报名人数(万)"], "o-", color="#C0392B", linewidth=2, markersize=5)
ax1.plot(x, df["硕士实际录取人数(万)"], "o-", color="#27AE60", linewidth=2, markersize=5)
ax1.set_xticks(x)
ax1.set_xticklabels(years, rotation=45)
ax1.set_title("报名人数 vs 录取人数", fontsize=14, fontweight="bold")
ax1.set_ylabel("人数 (万人)")
ax1.legend(fontsize=10)
ax1.grid(axis="y", alpha=0.3)

# 数据标签
for i, (a, b) in enumerate(zip(df["报名人数(万)"], df["硕士实际录取人数(万)"])):
    if i % 3 == 0:
        ax1.text(x[i] - 0.15, a + 3, f"{a:.0f}", ha="center", fontsize=7, color="#C0392B")
        ax1.text(x[i] + 0.15, b + 3, f"{b:.0f}", ha="center", fontsize=7, color="#27AE60")

# ---- 子图2: 落榜人数 (报名-录取) ----
ax2 = axes[0, 1]
gap = df["落榜人数(万)"].values
colors_gap = ["#F1948A" if v > 200 else "#FADBD8" for v in gap]
ax2.bar(x, gap, color=colors_gap, edgecolor="#E74C3C", linewidth=0.8)
ax2.plot(x, gap, "o-", color="#C0392B", linewidth=2, markersize=6)
ax2.set_xticks(x)
ax2.set_xticklabels(years, rotation=45)
ax2.set_title("落榜人数 (报名 — 录取)", fontsize=14, fontweight="bold")
ax2.set_ylabel("人数 (万人)")
ax2.grid(axis="y", alpha=0.3)

for i, v in enumerate(gap):
    ax2.text(x[i], v + 2, f"{v:.0f}", ha="center", fontsize=8, color="#C0392B")

# ---- 子图3: 录取率趋势 ----
ax3 = axes[1, 0]
rate_pct = df["录取率"] * 100
ax3.fill_between(x, rate_pct, alpha=0.3, color="#3498DB")
ax3.plot(x, rate_pct, "o-", color="#2980B9", linewidth=2.5, markersize=8, markerfacecolor="white")
ax3.set_xticks(x)
ax3.set_xticklabels(years, rotation=45)
ax3.set_title("考研录取率趋势", fontsize=14, fontweight="bold")
ax3.set_ylabel("录取率 (%)")
ax3.grid(axis="y", alpha=0.3)
ax3.axhline(y=rate_pct.mean(), color="#E74C3C", linestyle="--", linewidth=1, alpha=0.7,
            label=f"均值: {rate_pct.mean():.1f}%")
ax3.legend(fontsize=10)

for i, v in enumerate(rate_pct):
    ax3.text(x[i], v + 0.5, f"{v:.1f}%", ha="center", fontsize=8, color="#2980B9")

# ---- 子图4: 竞争指数趋势 ----
ax4 = axes[1, 1]
comp = df["竞争指数"]
ax4.fill_between(x, comp, alpha=0.3, color="#E67E22")
ax4.plot(x, comp, "s-", color="#D35400", linewidth=2.5, markersize=8, markerfacecolor="white")
ax4.set_xticks(x)
ax4.set_xticklabels(years, rotation=45)
ax4.set_title("考研竞争指数 (报名/录取)", fontsize=14, fontweight="bold")
ax4.set_ylabel("竞争指数 (X:1)")
ax4.grid(axis="y", alpha=0.3)
ax4.axhline(y=comp.mean(), color="#2ECC71", linestyle="--", linewidth=1, alpha=0.7,
            label=f"均值: {comp.mean():.1f}")
ax4.legend(fontsize=10)

for i, v in enumerate(comp):
    ax4.text(x[i], v + 0.1, f"{v:.1f}", ha="center", fontsize=8, color="#D35400")

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig("考研数据仪表盘.png", dpi=200, bbox_inches="tight")
plt.show()

# ============================================================
# 5. 补充: 历年增长率图
# ============================================================
fig2, axes2 = plt.subplots(1, 2, figsize=(16, 6))
fig2.suptitle("考研报名 & 录取 同比增长率", fontsize=18, fontweight="bold")

for idx, (col, title, color, ax) in enumerate([
    ("报名人数(万)", "报名人数同比增长率", "#E74C3C", axes2[0]),
    ("硕士实际录取人数(万)", "录取人数同比增长率", "#2ECC71", axes2[1]),
]):
    growth = df[col].pct_change() * 100
    bars = ax.bar(x[1:], growth.iloc[1:], color=color, alpha=0.8, edgecolor="black", linewidth=0.5)
    ax.axhline(y=0, color="black", linewidth=0.8)
    ax.set_xticks(x[1:])
    ax.set_xticklabels(years[1:], rotation=45)
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_ylabel("同比增长率 (%)")
    ax.grid(axis="y", alpha=0.3)

    for i, (xi, v) in enumerate(zip(x[1:], growth.iloc[1:])):
        color_tag = "#27AE60" if v >= 0 else "#C0392B"
        ax.text(xi, v + (1 if v >= 0 else -2.5), f"{v:+.1f}%", ha="center", fontsize=8, color=color_tag)

plt.tight_layout(rect=[0, 0, 1, 0.94])
plt.savefig("考研增长率.png", dpi=200, bbox_inches="tight")
plt.show()

print("\n图表已保存:")
print("  1. 考研数据仪表盘.png  — 四合一综合视图")
print("  2. 考研增长率.png      — 报名/录取同比增长率")
