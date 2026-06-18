"""
政策与招生结构变迁可视化（自变量4）
==================================
输入：招生政策与保研数据.csv、考研报名数据.csv
输出：
  1. 硕士招生结构变迁.png
  2. 推免保研vs统考录取.png
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
df_policy = pd.read_csv("招生政策与保研数据.csv")
df_ky = pd.read_csv("考研报名数据.csv")

df = pd.merge(df_policy, df_ky, on="年份", how="inner")
df = df[df["年份"].between(2010, 2024)].copy()

years = df["年份"].values
x = np.arange(len(years))

total_enroll = df["硕士总招生(万)"].values
xs_enroll   = df["学术硕士招生(万)"].values
zs_enroll   = df["专业硕士招生(万)"].values
baoyan      = df["推免保研人数(万,估算)"].values
ky_apply    = df["报名人数(万)"].values

tongkao_quota = total_enroll - baoyan      # 统考剩余名额
zs_ratio = df["专硕占比(%)"].values

# ---- 配色 ----
C_RED    = "#E74C3C"
C_BLUE   = "#2980B9"
C_DARK   = "#2C3E50"
C_GREY   = "#7F8C8D"
C_ORANGE = "#E67E22"
C_GREEN  = "#27AE60"
C_PURPLE = "#8E44AD"
C_ZS     = "#E67E22"    # 专硕暖色
C_XS     = "#5DADE2"    # 学硕冷色

# ============================================================
# 图1：学硕 vs 专硕招生堆叠面积图
# ============================================================
fig1, ax1 = plt.subplots(figsize=(14, 7))

# 堆叠面积图
ax1.fill_between(x, 0, xs_enroll, color=C_XS, alpha=0.6, label="学术硕士招生")
ax1.fill_between(x, xs_enroll, total_enroll, color=C_ZS, alpha=0.65, label="专业硕士招生")

# 边界线
ax1.plot(x, xs_enroll, "-", color="#2471A3", linewidth=2, label="学硕/专硕分界线")
ax1.plot(x, total_enroll, "o-", color=C_DARK, linewidth=2.8, markersize=7,
         markerfacecolor="white", markeredgewidth=2, zorder=5, label="硕士总招生")

# 2020 政策分界线
idx_2020 = list(years).index(2020)
ax1.axvline(x=idx_2020, color=C_RED, linestyle="--", linewidth=2.8, alpha=0.7)
ax1.text(idx_2020 + 0.2, total_enroll[-1] * 0.93,
         "<-- 2020年9月\n《专业学位研究生教育\n发展方案(2020-2025)》",
         ha="left", fontsize=10, color=C_RED, fontweight="bold",
         bbox=dict(boxstyle="round,pad=0.4", facecolor="#FDEDEC", edgecolor=C_RED, alpha=0.9))

# 关键节点比例标注
for idx, label in [(0, "2010"), (7, "2017"), (10, "2020"), (14, "2024")]:
    mid_xs = xs_enroll[idx] / 2
    mid_zs = xs_enroll[idx] + zs_enroll[idx] / 2
    ax1.text(x[idx], mid_xs, f"学硕\n{xs_enroll[idx]/total_enroll[idx]*100:.0f}%",
             ha="center", fontsize=8.5, color="#1A5276", fontweight="bold")
    ax1.text(x[idx], mid_zs, f"专硕\n{zs_enroll[idx]/total_enroll[idx]*100:.0f}%",
             ha="center", fontsize=8.5, color="#A04000", fontweight="bold")

# 2017年专硕首次超过学硕
idx_2017 = list(years).index(2017)
ax1.annotate("2017年\n专硕首次超过学硕\n（突破50%）",
             xy=(idx_2017, xs_enroll[idx_2017]),
             xytext=(idx_2017 + 3, xs_enroll[idx_2017] - 20),
             ha="center", fontsize=10, color=C_DARK, fontweight="bold",
             arrowprops=dict(arrowstyle="->", color=C_DARK, lw=1.8, connectionstyle="arc3,rad=0.3"),
             bbox=dict(boxstyle="round,pad=0.4", facecolor="#FEF9E7", edgecolor=C_ORANGE, alpha=0.9))

# 2022达标标注
idx_2022 = list(years).index(2022)
ax1.annotate("2022年\n基本达到 2/3 目标\n（专硕占比66.0%）",
             xy=(idx_2022, total_enroll[idx_2022]),
             xytext=(idx_2022 - 2.5, total_enroll[idx_2022] - 18),
             ha="center", fontsize=9.5, color=C_GREEN, fontweight="bold",
             arrowprops=dict(arrowstyle="->", color=C_GREEN, lw=1.5, connectionstyle="arc3,rad=-0.2"),
             bbox=dict(boxstyle="round,pad=0.3", facecolor="#D5F5E3", edgecolor=C_GREEN, alpha=0.85))

ax1.set_xticks(x)
ax1.set_xticklabels(years, rotation=0, fontsize=10)
ax1.set_ylabel("招生人数（万人）", fontsize=13, fontweight="bold")
ax1.set_title("硕士招生结构变迁：学硕 vs 专硕（2010–2024）", fontsize=16, fontweight="bold", pad=25)
ax1.legend(loc="upper left", fontsize=11, framealpha=0.9)
ax1.grid(axis="y", alpha=0.3, linestyle="--")

# 扩展 Y 轴上限，给上方标注留出空间
ax1.set_ylim(0, total_enroll.max() + 30)

fig1.text(0.5, 0.01,
          "数据来源：教育部历年统计公报、教发〔2010〕1号文件、中国教育在线《全国研究生招生调查报告》 | "
          "注：2011–2014、2016、2018等中间年份的学硕/专硕拆分为线性插值估算",
          ha="center", fontsize=9, color=C_GREY, style="italic")

plt.tight_layout(rect=[0, 0.04, 1, 1])
plt.savefig("硕士招生结构变迁.png", dpi=200, bbox_inches="tight")
plt.close()
print("[OK] 硕士招生结构变迁.png 已保存")

# ============================================================
# 图2：推免保研 vs 统考录取名额分配
# ============================================================
fig2, ax2 = plt.subplots(figsize=(14, 7))

# 堆叠面积
ax2.fill_between(x, 0, tongkao_quota, color="#ABEBC6", alpha=0.7, label="统考录取名额")
ax2.fill_between(x, tongkao_quota, total_enroll, color="#D2B4DE", alpha=0.7, label="推免保研名额（估算）")

# 边界线
ax2.plot(x, tongkao_quota, "-", color=C_GREEN, linewidth=2.5)
ax2.plot(x, total_enroll, "o-", color=C_DARK, linewidth=2.5, markersize=6,
         markerfacecolor="white", markeredgewidth=1.5, zorder=5, label="硕士总招生")

# 数据标注
for i in [0, 4, 9, 14]:
    ax2.text(x[i], tongkao_quota[i] + baoyan[i] / 2, f"推免\n{baoyan[i]:.1f}万",
             ha="center", fontsize=8.5, color="#7D3C98", fontweight="bold")

# 统考比例变化
tongkao_start = tongkao_quota[0] / total_enroll[0] * 100
tongkao_end   = tongkao_quota[-1] / total_enroll[-1] * 100

# 2017推免扩容
ax2.annotate("2017年\n推免高校扩容\n（新增54所）\n推免比例跳升",
             xy=(idx_2017, baoyan[idx_2017]),
             xytext=(idx_2017 + 3.5, baoyan[idx_2017] + 5),
             ha="center", fontsize=9.5, color=C_PURPLE, fontweight="bold",
             arrowprops=dict(arrowstyle="->", color=C_PURPLE, lw=1.8, connectionstyle="arc3,rad=0.35"),
             bbox=dict(boxstyle="round,pad=0.4", facecolor="#F4ECF7", edgecolor=C_PURPLE, alpha=0.9))

# 统考空间被挤压
ax2.text(7, total_enroll[-1] * 0.25,
         f"统考名额占比：\n2010年 {tongkao_start:.1f}% → 2024年 {tongkao_end:.1f}%\n推免持续挤压统考空间",
         ha="center", fontsize=11, color=C_DARK, fontweight="bold",
         bbox=dict(boxstyle="round,pad=0.5", facecolor="#F8F9F9", edgecolor=C_GREY, alpha=0.9))

ax2.set_xticks(x)
ax2.set_xticklabels(years, rotation=0, fontsize=10)
ax2.set_ylabel("人数（万人）", fontsize=13, fontweight="bold")
ax2.set_title("推免保研 vs 统考录取：硕士招生名额分配变化", fontsize=16, fontweight="bold", pad=15)
ax2.legend(loc="upper left", fontsize=11, framealpha=0.9)
ax2.grid(axis="y", alpha=0.3, linestyle="--")

fig2.text(0.5, 0.01,
          "数据来源：教育部统计公报、中国教育在线研招报告、教育部阳光高考信息平台 | "
          "注：推免保研人数为基于推免比例的估算值（约10%→14%），非官方直接公布数据，仅供参考",
          ha="center", fontsize=9, color=C_GREY, style="italic")

plt.tight_layout(rect=[0, 0.04, 1, 1])
plt.savefig("推免保研vs统考录取.png", dpi=200, bbox_inches="tight")
plt.close()
print("[OK] 推免保研vs统考录取.png 已保存")

print("\n全部完成！共生成 2 张图表。")
