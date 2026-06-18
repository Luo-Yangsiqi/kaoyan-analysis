"""
本科毕业生人数 & 读研比例 —— 年度变化可视化
==============================================
输入：本科毕业生数据.csv、读研比例.csv
输出：毕业生人数变化图.png、读研比例变化图.png
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import sys, io

# 修复 Windows GBK 终端的编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ============================================================
# 中文字体设置（与 admission_rate.py 保持一致）
# ============================================================
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC"]
plt.rcParams["axes.unicode_minus"] = False

# ============================================================
# 读取数据
# ============================================================
df_grad = pd.read_csv("本科毕业生数据.csv")   # 年份, 普通本科毕业生数(万)
df_ratio = pd.read_csv("读研比例.csv")         # 年份, 普通本科毕业生数(万), 硕士实际录取人数(万), 读研比例(%)

years = df_grad["年份"].values
grad_num = df_grad["普通本科毕业生数(万)"].values
ratio_pct = df_ratio["读研比例(%)"].values

x = np.arange(len(years))

# ============================================================
# 图1：本科毕业生人数年度变化图
# ============================================================
fig1, ax1 = plt.subplots(figsize=(14, 7))

# 渐变色柱状图（从浅蓝到深蓝，反映规模递增）
norm = plt.Normalize(grad_num.min(), grad_num.max())
colors_bar = plt.cm.Blues(0.3 + 0.7 * norm(grad_num))

bars = ax1.bar(x, grad_num, color=colors_bar, edgecolor="#2C3E50", linewidth=0.8, width=0.65)

# 折线叠在柱状图上
ax1.plot(x, grad_num, "o-", color="#C0392B", linewidth=2.5, markersize=7,
         markerfacecolor="white", markeredgewidth=1.8, zorder=5)

# 数据标签（隔年标注，避免拥挤）
for i, (xi, v) in enumerate(zip(x, grad_num)):
    if i % 2 == 0:
        ax1.text(xi, v + 8, f"{v:.1f}", ha="center", fontsize=8.5, color="#2C3E50", fontweight="bold")

# 标注关键节点
annotations = {
    0: "2010\n259万",                          # 起点
    9: "2019\n395万",                          # 疫情前
    14: "2024\n512万",                         # 最新
}
for i, txt in annotations.items():
    ax1.annotate(txt, (x[i], grad_num[i]),
                textcoords="offset points", xytext=(0, 25),
                ha="center", fontsize=9, color="#C0392B",
                arrowprops=dict(arrowstyle="->", color="#7F8C8D", lw=1.2),
                bbox=dict(boxstyle="round,pad=0.3", facecolor="#FEF9E7", edgecolor="#F39C12", alpha=0.85))

ax1.set_xticks(x)
ax1.set_xticklabels(years, rotation=45, fontsize=10)
ax1.set_ylabel("本科毕业生数（万人）", fontsize=13, fontweight="bold")
ax1.set_title("全国普通本科应届毕业生总数年度变化（2010–2024）", fontsize=16, fontweight="bold", pad=15)
ax1.set_ylim(200, 570)

# 副标题：增长率信息
growth_total = (grad_num[-1] - grad_num[0]) / grad_num[0] * 100
ax1.text(0.99, 0.05, f"2010 → 2024 累计增长 {growth_total:.1f}%（接近翻倍）",
         transform=ax1.transAxes, ha="right", fontsize=11, color="#7F8C8D",
         bbox=dict(boxstyle="round,pad=0.4", facecolor="#F8F9F9", edgecolor="#BDC3C7", alpha=0.8))

ax1.grid(axis="y", alpha=0.3, linestyle="--")
ax1.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f"{v:.0f}万"))

plt.tight_layout()
plt.savefig("毕业生人数变化图.png", dpi=200, bbox_inches="tight")
plt.close()
print("✅ 毕业生人数变化图.png 已保存")


# ============================================================
# 图2：读研比例年度变化图
# ============================================================
fig2, ax2 = plt.subplots(figsize=(14, 7))

# 面积填充：低于均值 vs 高于均值
mean_ratio = ratio_pct.mean()
ax2.fill_between(x, ratio_pct, mean_ratio,
                 where=(ratio_pct >= mean_ratio),
                 color="#27AE60", alpha=0.25, label=f"高于均值 ({mean_ratio:.1f}%)")
ax2.fill_between(x, ratio_pct, mean_ratio,
                 where=(ratio_pct < mean_ratio),
                 color="#E74C3C", alpha=0.15, label=f"低于均值 ({mean_ratio:.1f}%)")

# 主折线
ax2.plot(x, ratio_pct, "o-", color="#2980B9", linewidth=3, markersize=9,
         markerfacecolor="white", markeredgewidth=2, markeredgecolor="#2980B9", zorder=5)

# 均值参考线
ax2.axhline(y=mean_ratio, color="#E74C3C", linestyle="--", linewidth=1.5, alpha=0.7,
            label=f"均值: {mean_ratio:.2f}%")

# 数据标签
for i, (xi, v) in enumerate(zip(x, ratio_pct)):
    offset = 0.6 if v >= mean_ratio else -1.0
    ax2.text(xi, v + offset, f"{v:.1f}%", ha="center", fontsize=8, color="#2C3E50")

# 标注关键拐点
key_points = {
    5: ("2016\n最低点 15.2%", 60, -30),        # 2016 最低
    10: ("2020\n疫情+扩招\n19.3%", 30, 35),    # 2020 政策拐点
    13: ("2023\n峰值 23.4%", -70, -20),        # 2023 峰值
}
for i, (label, x_offset, y_offset) in key_points.items():
    ax2.annotate(label, (x[i], ratio_pct[i]),
                textcoords="offset points", xytext=(x_offset, y_offset),
                ha="center", fontsize=9, color="#8E44AD",
                arrowprops=dict(arrowstyle="->", color="#8E44AD", lw=1.5,
                              connectionstyle="arc3,rad=0.2"),
                bbox=dict(boxstyle="round,pad=0.3", facecolor="#F4ECF7", edgecolor="#8E44AD", alpha=0.85))

# 政策分区标注（2020起专硕扩招）
ax2.axvspan(10, 14, alpha=0.08, color="#F39C12")
ax2.text(12, ax2.get_ylim()[1] * 0.96, "专硕扩招政策期\n(2020–2024)",
         ha="center", fontsize=10, color="#E67E22", fontweight="bold",
         bbox=dict(boxstyle="round,pad=0.3", facecolor="#FEF9E7", edgecolor="#F39C12", alpha=0.85))

ax2.set_xticks(x)
ax2.set_xticklabels(years, rotation=45, fontsize=10)
ax2.set_ylabel("读研比例（%）", fontsize=13, fontweight="bold")
ax2.set_title("本科生国内读研比例年度变化（2010–2024）", fontsize=16, fontweight="bold", pad=15)
ax2.legend(loc="upper left", fontsize=10, framealpha=0.9)
ax2.grid(axis="y", alpha=0.3, linestyle="--")

plt.tight_layout()
plt.savefig("读研比例变化图.png", dpi=200, bbox_inches="tight")
plt.close()
print("✅ 读研比例变化图.png 已保存")


# ============================================================
# 图3（附加）：双轴组合图 —— 毕业生基数 vs 读研比例
# ============================================================
fig3, ax3_left = plt.subplots(figsize=(14, 7))

# 左轴：本科毕业生人数（柱状图）
bars3 = ax3_left.bar(x, grad_num, color="#5DADE2", alpha=0.7, width=0.6, label="本科毕业生数（万人）")
ax3_left.set_ylabel("本科毕业生数（万人）", fontsize=13, fontweight="bold", color="#2471A3")
ax3_left.tick_params(axis="y", labelcolor="#2471A3")
ax3_left.set_ylim(200, 580)

# 右轴：读研比例（折线）
ax3_right = ax3_left.twinx()
ax3_right.plot(x, ratio_pct, "s-", color="#E74C3C", linewidth=2.5, markersize=8,
               markerfacecolor="white", markeredgewidth=2, zorder=5, label="读研比例（%）")
ax3_right.set_ylabel("读研比例（%）", fontsize=13, fontweight="bold", color="#C0392B")
ax3_right.tick_params(axis="y", labelcolor="#C0392B")
ax3_right.set_ylim(10, 28)

# 标注
for i in [0, 5, 10, 14]:
    ax3_left.text(x[i], grad_num[i] + 10, f"{grad_num[i]:.0f}万", ha="center", fontsize=8.5, color="#2471A3")
    ax3_right.text(x[i], ratio_pct[i] + 0.5, f"{ratio_pct[i]:.1f}%", ha="center", fontsize=8.5, color="#C0392B")

ax3_left.set_xticks(x)
ax3_left.set_xticklabels(years, rotation=45, fontsize=10)
ax3_left.set_title("本科毕业生基数与读研比例联动趋势（2010–2024）", fontsize=16, fontweight="bold", pad=15)

# 合并图例
lines1, labels1 = ax3_left.get_legend_handles_labels()
lines2, labels2 = ax3_right.get_legend_handles_labels()
ax3_left.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=10, framealpha=0.9)

ax3_left.grid(axis="y", alpha=0.3, linestyle="--")

plt.tight_layout()
plt.savefig("毕业生与读研比例联动图.png", dpi=200, bbox_inches="tight")
plt.close()
print("✅ 毕业生与读研比例联动图.png 已保存")

print("\n全部图表生成完毕！")
