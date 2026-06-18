"""
多变量综合看板可视化
====================
输入：year.csv（统一大表）
输出：
  1. 标准化多变量趋势叠合图.png
  2. Pearson相关系数矩阵.png
  3. 各变量年度相对强度热力图.png

注：已去除"16-24岁青年失业率"指标（缺失过多，不参与综合看板）
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
# 读取主数据表
# ============================================================
df = pd.read_csv("year.csv")
years = df["年份"].values
x = np.arange(len(years))

# ============================================================
# 选取核心变量（已去除青年失业率）
# ============================================================
VAR_CONFIG = {
    "报名人数(万)":               {"label": "考研报名人数",          "role": "被解释变量", "color": "#E74C3C", "ls": "-",  "lw": 3.0},
    "读研比例(%)":                {"label": "读研比例",              "role": "供给面",     "color": "#2980B9", "ls": "-",  "lw": 2.0},
    "实际月薪增长率(%)":           {"label": "实际月薪增长率",          "role": "就业吸引力", "color": "#27AE60", "ls": "-",  "lw": 2.0},
    "受雇工作比例(%)":            {"label": "受雇工作比例",          "role": "就业吸纳",   "color": "#8E44AD", "ls": "--", "lw": 2.0},
    "报名过审人数(万)":           {"label": "国考过审人数",          "role": "替代选择",   "color": "#3498DB", "ls": "-",  "lw": 2.0},
    "专硕占比(%)":                {"label": "专硕占比",              "role": "政策变量",   "color": "#F39C12", "ls": "-",  "lw": 2.5},
    "推免保研人数(万,估算)":      {"label": "推免保研人数(估算)",     "role": "招生结构",   "color": "#1ABC9C", "ls": "--", "lw": 1.8},
}

var_names = list(VAR_CONFIG.keys())

# ---- 配色 ----
C_RED    = "#E74C3C"
C_BLUE   = "#2980B9"
C_DARK   = "#2C3E50"
C_GREY   = "#7F8C8D"
C_GREEN  = "#27AE60"
C_PURPLE = "#8E44AD"
C_ORANGE = "#E67E22"

# ---- 计算实际月薪增长率（替代绝对月薪，避免热力图单调递增） ----
real_salary = df["实际月薪(2010年不变价,元)"].values
salary_growth_pct = np.insert(np.diff(real_salary) / real_salary[:-1] * 100, 0, np.nan)
df["实际月薪增长率(%)"] = salary_growth_pct

# ============================================================
# 构建标准化数据（Min-Max 归一化到 [0, 1]）
# ============================================================
def normalize_minmax(series):
    valid = series.dropna()
    if len(valid) < 2:
        return pd.Series([np.nan] * len(series), index=series.index)
    s_min, s_max = valid.min(), valid.max()
    if s_max == s_min:
        return pd.Series([0.5] * len(series), index=series.index)
    return (series - s_min) / (s_max - s_min)

df_norm = pd.DataFrame({"年份": years})
for vn in var_names:
    df_norm[vn] = normalize_minmax(df[vn])

# ============================================================
# 图1：标准化多变量趋势叠合图
# ============================================================
fig1, ax1 = plt.subplots(figsize=(16, 8))

for vn, cfg in VAR_CONFIG.items():
    ax1.plot(x, df_norm[vn], linestyle=cfg["ls"], color=cfg["color"], linewidth=cfg["lw"],
             marker="o", markersize=5, markerfacecolor="white", markeredgewidth=1.2,
             label=cfg["label"], alpha=0.9, zorder=3)

# 2020政策分界线
idx_2020 = list(years).index(2020)
ax1.axvline(x=idx_2020, color=C_GREY, linestyle=":", linewidth=2.5, alpha=0.5)
ax1.text(idx_2020 + 0.15, 0.94, "2020年\n扩招政策节点",
         ha="left", fontsize=10, color=C_GREY, fontweight="bold")

# 2023拐点
idx_2023 = list(years).index(2023)
ax1.axvline(x=idx_2023, color=C_RED, linestyle=":", linewidth=1.5, alpha=0.35)
ax1.text(idx_2023 - 0.15, 0.07, "2023\n报名峰值",
         ha="right", fontsize=9, color=C_RED, fontweight="bold")

# 正/负相关标注
ax1.annotate("与报名人数同向变化（正相关）：\n专硕占比、国考过审、推免人数、实际月薪、读研比例",
             xy=(0.01, 0.78), xycoords="axes fraction", fontsize=10, color=C_DARK,
             bbox=dict(boxstyle="round,pad=0.4", facecolor="#D5F5E3", edgecolor=C_GREY, alpha=0.85))
ax1.annotate("与报名人数反向变化（负相关）：\n受雇工作比例",
             xy=(0.01, 0.66), xycoords="axes fraction", fontsize=10, color=C_DARK,
             bbox=dict(boxstyle="round,pad=0.4", facecolor="#FDEDEC", edgecolor=C_GREY, alpha=0.85))

ax1.set_xticks(x)
ax1.set_xticklabels(years, rotation=0, fontsize=10)
ax1.set_ylabel("Min-Max 归一化值", fontsize=13, fontweight="bold")
ax1.set_title("标准化多变量趋势叠合图（所有变量归一化至 [0, 1] 区间）", fontsize=17, fontweight="bold", pad=15)
ax1.set_ylim(-0.06, 1.10)
ax1.grid(axis="y", alpha=0.2, linestyle="--")

# 图例分两列
ax1.legend(loc="lower left", fontsize=10, ncol=4, framealpha=0.9,
           columnspacing=0.8, handlelength=1.5)

fig1.text(0.5, 0.01,
          "数据来源：year.csv 统一主数据表 | "
          "注：为便于跨变量比较，各指标均已做 Min-Max 归一化处理；已排除青年失业率（缺失过半）",
          ha="center", fontsize=9, color=C_GREY, style="italic")

plt.tight_layout(rect=[0, 0.04, 1, 1])
plt.savefig("标准化多变量趋势叠合图.png", dpi=200, bbox_inches="tight")
plt.close()
print("[OK] 标准化多变量趋势叠合图.png 已保存")

# ============================================================
# 图2：Pearson 相关系数矩阵
# ============================================================
fig2, ax2 = plt.subplots(figsize=(12, 10))

# 构建相关性矩阵
corr_df = df[var_names].copy()
# 对缺失值用均值填充（仅用于相关性计算）
for col in corr_df.columns:
    if corr_df[col].isna().sum() > 0:
        corr_df[col] = corr_df[col].fillna(corr_df[col].mean())

corr_matrix = corr_df.corr()
short_labels = [VAR_CONFIG[v]["label"] for v in var_names]

im = ax2.imshow(corr_matrix.values, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")

# 标注相关系数值
n_vars = len(var_names)
for i in range(n_vars):
    for j in range(n_vars):
        val = corr_matrix.values[i, j]
        text_color = "white" if abs(val) > 0.6 else C_DARK
        ax2.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=10,
                 color=text_color, fontweight="bold" if abs(val) > 0.8 else "normal")

# 高亮与报名人数的相关行
for j in range(n_vars):
    val = corr_matrix.values[0, j]
    if abs(val) > 0.7 and j > 0:
        ax2.add_patch(plt.Rectangle((j - 0.5, 0 - 0.5), 1, 1, fill=False,
                                     edgecolor=C_DARK, linewidth=3, linestyle="--"))

ax2.set_xticks(range(n_vars))
ax2.set_xticklabels(short_labels, rotation=45, ha="right", fontsize=10)
ax2.set_yticks(range(n_vars))
ax2.set_yticklabels(short_labels, fontsize=10)
ax2.set_title("Pearson 相关系数矩阵", fontsize=16, fontweight="bold", pad=15)

# 色条
cbar = plt.colorbar(im, ax=ax2, shrink=0.82, pad=0.02)
cbar.set_label("Pearson r", fontsize=12)

fig2.text(0.5, 0.01,
          "注：虚线框标记与考研报名人数 |r| > 0.7 的变量；缺失值以列均值填充后计算",
          ha="center", fontsize=9, color=C_GREY, style="italic")

plt.tight_layout(rect=[0, 0.03, 1, 1])
plt.savefig("Pearson相关系数矩阵.png", dpi=200, bbox_inches="tight")
plt.close()
print("[OK] Pearson相关系数矩阵.png 已保存")

# ============================================================
# 图3：各变量年度相对强度热力图
# ============================================================
fig3, ax3 = plt.subplots(figsize=(14, 10))

heatmap_data = df_norm[var_names].T.values  # 行=变量，列=年份

im3 = ax3.imshow(heatmap_data, cmap="YlOrRd", aspect="auto", vmin=0, vmax=1)

# Y轴：变量标签（使用 set_yticks + set_yticklabels 避免文本重叠）
y_labels = [f"{VAR_CONFIG[vn]['label']}  [{VAR_CONFIG[vn]['role']}]" for vn in var_names]
ax3.set_yticks(range(len(var_names)))
ax3.set_yticklabels(y_labels, fontsize=9.5)

# X轴：年份标签（全部显示）
ax3.set_xticks(range(len(years)))
ax3.set_xticklabels(years, rotation=45, ha="right", fontsize=8.5)

ax3.set_title("各变量年度相对强度热力图（Min-Max 归一化）", fontsize=16, fontweight="bold", pad=20)

# 色条
cbar3 = plt.colorbar(im3, ax=ax3, shrink=0.85, pad=0.02)
cbar3.set_label("归一化强度（0 = 该变量年度最低值，1 = 年度最高值）", fontsize=10)

# 解读标注（放在 title 下方 subtitle 位置）
ax3.set_xlabel(
    "颜色越深 → 该变量在该年度越接近其历史最高水平 | "
    "横向观察可看同一变量15年间的高峰低谷；纵向对比可看同一年度各变量的相对强弱  "
    "[注] 已排除青年失业率（缺失过半）；实际月薪已替换为同比增长率",
    fontsize=8, color=C_GREY, style="italic", labelpad=8
)

plt.tight_layout(rect=[0, 0.02, 1, 0.98])
plt.savefig("各变量年度相对强度热力图.png", dpi=200, bbox_inches="tight")
plt.close()
print("[OK] 各变量年度相对强度热力图.png 已保存")

# ============================================================
# 关键统计摘要
# ============================================================
print("\n" + "=" * 70)
print("关键统计摘要（供论文引用）")
print("=" * 70)

print(f"\n[1] 考研报名人数：")
print(f"    2010年: {df['报名人数(万)'].iloc[0]:.1f}万 -> 2024年: {df['报名人数(万)'].iloc[-1]:.1f}万")
print(f"    峰值: {df['报名人数(万)'].max():.1f}万（{df.loc[df['报名人数(万)'].idxmax(), '年份']:.0f}年）")
print(f"    累计: +{(df['报名人数(万)'].iloc[-1] - df['报名人数(万)'].iloc[0]) / df['报名人数(万)'].iloc[0] * 100:.1f}%")

print(f"\n[2] 读研比例：")
print(f"    最低: {df['读研比例(%)'].min():.1f}%（{df.loc[df['读研比例(%)'].idxmin(), '年份']:.0f}年）")
print(f"    最高: {df['读研比例(%)'].max():.1f}%（{df.loc[df['读研比例(%)'].idxmax(), '年份']:.0f}年）")

print(f"\n[3] 实际月薪（2010年不变价）：")
print(f"    2010年: {df['实际月薪(2010年不变价,元)'].iloc[0]:.0f}元 -> 2024年: {df['实际月薪(2010年不变价,元)'].iloc[-1]:.0f}元")
real_growth = (df['实际月薪(2010年不变价,元)'].iloc[-1] - df['实际月薪(2010年不变价,元)'].iloc[0]) / df['实际月薪(2010年不变价,元)'].iloc[0] * 100
print(f"    实际增幅: {real_growth:.1f}%")

print(f"\n[4] 受雇工作比例：")
print(f"    2010年: {df['受雇工作比例(%)'].iloc[0]:.1f}% -> 2024年: {df['受雇工作比例(%)'].iloc[-1]:.1f}%")
print(f"    累计下降: {df['受雇工作比例(%)'].iloc[0] - df['受雇工作比例(%)'].iloc[-1]:.1f}pp")

print(f"\n[5] 国考过审人数：")
print(f"    2010年: {df['报名过审人数(万)'].iloc[0]:.1f}万 -> 2024年: {df['报名过审人数(万)'].iloc[-1]:.1f}万")
print(f"    峰值: {df['报名过审人数(万)'].max():.1f}万（2024年）")

print(f"\n[6] 专硕占比：")
print(f"    2010年: {df['专硕占比(%)'].iloc[0]:.1f}% -> 2024年: {df['专硕占比(%)'].iloc[-1]:.1f}%")

print(f"\n[7] Pearson 相关系数（与考研报名人数）：")
corr_with_ky = corr_matrix.iloc[0, 1:].sort_values(ascending=False)
for i, (vn, r) in enumerate(corr_with_ky.items()):
    label = VAR_CONFIG[vn]["label"]
    direction = "正" if r > 0 else "负"
    print(f"    {i+1}. {label}: r = {r:+.3f}（{direction}相关）")

print("\n全部完成！共生成 3 张图表。")
