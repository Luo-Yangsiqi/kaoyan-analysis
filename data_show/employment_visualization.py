"""
就业市场压力可视化（自变量2）
============================
输入：year.csv（统一大表，含名义/实际月薪）
输出：
  1. 本科毕业月薪名义vs实际.png
  2. 受雇工作比例变化趋势.png
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
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
df = pd.read_csv("year.csv")
years = df["年份"].values
x = np.arange(len(years))

salary_nominal = df["本科毕业半年月薪(元)"].values
salary_real   = df["实际月薪(2010年不变价,元)"].values
employ_rate   = df["受雇工作比例(%)"].values

# ---- 配色 ----
C_RED    = "#E74C3C"
C_BLUE   = "#2980B9"
C_DARK   = "#2C3E50"
C_GREY   = "#7F8C8D"
C_GREEN  = "#27AE60"

# ============================================================
# 图1：本科毕业半年月薪 — 名义 vs 实际
# ============================================================
fig1, ax1 = plt.subplots(figsize=(14, 7))

# 名义月薪（浅色柱状）
ax1.bar(x - 0.12, salary_nominal, width=0.24, color="#AED6F1", edgecolor=C_BLUE, linewidth=0.5,
        alpha=0.85, label="名义月薪（元）")
# 实际月薪（深色柱状）
ax1.bar(x + 0.12, salary_real, width=0.24, color=C_BLUE, edgecolor="#1A5276", linewidth=0.5,
        alpha=0.9, label="实际月薪（2010年不变价，元）")

# 折线叠在柱状图上
ax1.plot(x, salary_nominal, "o-", color="#5DADE2", linewidth=2, markersize=5, markerfacecolor="white")
ax1.plot(x, salary_real, "s-", color="#1A5276", linewidth=2, markersize=5, markerfacecolor="white")

# 通胀侵蚀箭头（首尾两年）
for i in [0, 14]:
    gap = salary_nominal[i] - salary_real[i]
    ax1.annotate("", xy=(x[i], salary_nominal[i]), xytext=(x[i], salary_real[i]),
                arrowprops=dict(arrowstyle="<->", color=C_RED, lw=1.5))

ax1.text(7, 2700, f"累计通胀侵蚀\n≈ {salary_nominal[-1] - salary_real[-1]:.0f} 元（2024年）",
         ha="center", fontsize=11, color=C_RED, fontweight="bold",
         bbox=dict(boxstyle="round,pad=0.4", facecolor="#FDEDEC", edgecolor=C_RED, alpha=0.85))

# 首尾数据标签
for i in [0, 14]:
    ax1.text(x[i] - 0.12, salary_nominal[i] + 150, f"{salary_nominal[i]:.0f}",
             ha="center", fontsize=9, color="#5DADE2", fontweight="bold")
    ax1.text(x[i] + 0.12, salary_real[i] - 180, f"{salary_real[i]:.0f}",
             ha="center", fontsize=9, color="#1A5276", fontweight="bold")

ax1.set_xticks(x)
ax1.set_xticklabels(years, rotation=0, fontsize=10)
ax1.set_ylabel("月薪（元）", fontsize=13, fontweight="bold")
ax1.set_title("本科毕业半年月薪：名义 vs 实际（以2010年为基期平减）", fontsize=16, fontweight="bold", pad=15)
ax1.legend(loc="upper left", fontsize=11, framealpha=0.9)
ax1.grid(axis="y", alpha=0.3, linestyle="--")

# 底部注释
fig1.text(0.5, 0.01,
          "数据来源：麦可思研究院《中国大学生就业报告》（就业蓝皮书）2011–2025各版 | "
          "注：实际月薪以2010年CPI为基期平减，剔除通货膨胀影响",
          ha="center", fontsize=9, color=C_GREY, style="italic")

plt.tight_layout(rect=[0, 0.04, 1, 1])
plt.savefig("本科毕业月薪名义vs实际.png", dpi=200, bbox_inches="tight")
plt.close()
print("[OK] 本科毕业月薪名义vs实际.png 已保存")

# ============================================================
# 图2：受雇工作比例下滑趋势
# ============================================================
fig2, ax2 = plt.subplots(figsize=(14, 7))

# 渐变色柱状图（越近越深，反映持续恶化）
gradient = np.linspace(0.3, 1.0, len(years))
colors_employ = [plt.cm.OrRd(0.25 + 0.55 * g) for g in gradient]
ax2.bar(x, employ_rate, color=colors_employ, edgecolor=C_DARK, linewidth=0.6, width=0.65)

# 趋势线
ax2.plot(x, employ_rate, "o-", color=C_DARK, linewidth=2.8, markersize=8,
         markerfacecolor="white", markeredgewidth=1.8, zorder=5)

# 数据标签（隔年）
for i, (xi, v) in enumerate(zip(x, employ_rate)):
    if i % 2 == 0:
        ax2.text(xi, v + 1.2, f"{v:.1f}%", ha="center", fontsize=9, color=C_DARK, fontweight="bold")

# 均值线
mean_emp = employ_rate.mean()
ax2.axhline(y=mean_emp, color=C_RED, linestyle="--", linewidth=1.5, alpha=0.7,
            label=f"均值: {mean_emp:.1f}%")

# 下降幅度标注
decline = employ_rate[0] - employ_rate[-1]
ax2.annotate(f"2010 -> 2024\n累计下降 {decline:.1f} 个百分点\n（年均 -{decline/14:.1f}pp）",
             xy=(x[-1], employ_rate[-1]), xytext=(x[-6], employ_rate[-1] - 10),
             ha="center", fontsize=11, color=C_RED, fontweight="bold",
             arrowprops=dict(arrowstyle="->", color=C_RED, lw=1.8, connectionstyle="arc3,rad=0.2"),
             bbox=dict(boxstyle="round,pad=0.4", facecolor="#FDEDEC", edgecolor=C_RED, alpha=0.9))

# 2020疫情冲击
idx_2020 = list(years).index(2020)
ax2.annotate("2020\n疫情冲击\n就业率骤降",
             xy=(idx_2020, employ_rate[idx_2020]),
             xytext=(idx_2020 - 2.5, employ_rate[idx_2020] + 8),
             ha="center", fontsize=9, color=C_DARK,
             arrowprops=dict(arrowstyle="->", color=C_DARK, lw=1.3),
             bbox=dict(boxstyle="round,pad=0.3", facecolor="#FEF9E7", edgecolor="#F39C12", alpha=0.85))

ax2.set_xticks(x)
ax2.set_xticklabels(years, rotation=0, fontsize=10)
ax2.set_ylabel("比例（%）", fontsize=13, fontweight="bold")
ax2.set_title("本科毕业生受雇工作比例变化趋势（2010–2024）", fontsize=16, fontweight="bold", pad=15)
ax2.set_ylim(50, 90)
ax2.legend(loc="upper right", fontsize=11, framealpha=0.9)
ax2.grid(axis="y", alpha=0.3, linestyle="--")

# 底部注释
fig2.text(0.5, 0.01,
          "数据来源：麦可思研究院《中国大学生就业报告》历年「毕业半年后去向分布」| "
          "注：2010–2015为受雇全职工作比例，2016年后含半职工作",
          ha="center", fontsize=9, color=C_GREY, style="italic")

plt.tight_layout(rect=[0, 0.04, 1, 1])
plt.savefig("受雇工作比例变化趋势.png", dpi=200, bbox_inches="tight")
plt.close()
print("[OK] 受雇工作比例变化趋势.png 已保存")

print("\n全部完成！共生成 2 张图表。")
