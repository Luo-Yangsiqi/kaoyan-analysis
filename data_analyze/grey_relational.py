"""
灰色关联度分析：四类驱动机制 ↔ PEEHI
=====================================
参考序列 Y = PEEHI
比较序列 X = [S1 升学基数, S2 就业市场, S3 政策供给, S4 考公替代]
输出: 灰色关联度排序 + 可视化 + 逐年关联系数表
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys, io, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# ================================================================
# 1. 读取 & 计算四类子指数
# ================================================================
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)

peehi_df = pd.read_csv(os.path.join(script_dir, "PEEHI_热度指数.csv"))
df = pd.read_csv(os.path.join(project_dir, "data_show", "year.csv"))

years = df["年份"].values
Y = peehi_df["PEEHI_归一化"].values  # (15,)


def norm(v):
    return (v - np.nanmin(v)) / (np.nanmax(v) - np.nanmin(v))


def norm_rev(v):
    return (np.nanmax(v) - v) / (np.nanmax(v) - np.nanmin(v))


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
      + df["政策哑变量(2020后=1)"].values) / 3
S4 = (norm(df["报名过审人数(万)"].values) + norm(df["报录比(X:1)"].values)) / 2

X = np.column_stack([S1, S2, S3, S4])
labels = ["S1 升学基数压力", "S2 就业市场压力", "S3 招生政策供给", "S4 考公替代压力"]
colors = ["#3498DB", "#E67E22", "#27AE60", "#9B59B6"]

# ================================================================
# 2. Min-Max 标准化
# ================================================================
Y_norm = (Y - Y.min()) / (Y.max() - Y.min())
X_norm = (X - X.min(axis=0)) / (X.max(axis=0) - X.min(axis=0))

# ================================================================
# 3~5. 差序列 → 关联系数
# ================================================================
diff = np.abs(X_norm - Y_norm.reshape(-1, 1))  # (15, 4)
d_min = diff.min()
d_max = diff.max()
rho = 0.5
coef = (d_min + rho * d_max) / (diff + rho * d_max)  # (15, 4)

# ================================================================
# 6. 灰色关联度 = 各年关联系数均值
# ================================================================
grades = coef.mean(axis=0)
rank = np.argsort(-grades)  # 降序

# ================================================================
# 7. 输出
# ================================================================
print("=" * 55)
print("灰色关联度分析：PEEHI ← 四类驱动机制")
print(f"分辨系数 ρ = {rho}")
print("=" * 55)
for i in rank:
    bar = "█" * int(grades[i] * 60)
    print(f"  #{i+1} {labels[i]:<16} 关联度 = {grades[i]:.4f}  {bar}")

print(f"\n逐年关联系数：")
print(f"{'年份':<6}", end="")
for lb in labels:
    print(f"{lb:<14}", end="")
print(f"\n{'-' * 62}")
for t, year in enumerate(years):
    print(f"{year:<6}", end="")
    for j in range(4):
        marker = " ★" if j == rank[0] else ""
        print(f"{coef[t, j]:.4f}{marker:<12}", end="")
    print()

# ================================================================
# 8. 可视化
# ================================================================
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
fig.suptitle("灰色关联度分析：PEEHI 与四类驱动机制", fontsize=17,
             fontweight="bold", color="#1a5276", y=1.03)

# ---- (a) 关联度条形图 ----
ax = axes[0]
sorted_labels = [labels[i] for i in rank]
sorted_grades = [grades[i] for i in rank]
sorted_colors = [colors[i] for i in rank]

bars = ax.barh(range(4), sorted_grades, color=sorted_colors, edgecolor="white",
               linewidth=1.5, height=0.55)
for i, (bar_obj, grade) in enumerate(zip(bars, sorted_grades)):
    ax.text(grade + 0.005, bar_obj.get_y() + bar_obj.get_height() / 2,
            f"{grade:.4f}", va="center", fontsize=12, fontweight="bold", color="#2C3E50")
ax.set_yticks(range(4))
ax.set_yticklabels(sorted_labels, fontsize=11)
ax.set_xlim(0, 1.05)
ax.set_title("灰色关联度排序", fontsize=13, fontweight="bold", color="#2C3E50")
ax.invert_yaxis()
ax.grid(axis="x", alpha=0.2)
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)

# ---- (b) 逐年关联系数雷达/折线 ----
ax = axes[1]
for j in range(4):
    ax.plot(years, coef[:, j], "o-", color=colors[j], linewidth=1.8, markersize=5,
            markerfacecolor="white", markeredgewidth=1.5, label=labels[j])
ax.axhline(y=grades.mean(), color="#E74C3C", linestyle="--", linewidth=1, alpha=0.5,
           label=f"总均值={grades.mean():.3f}")
ax.set_xticks(years)
ax.set_xticklabels(years, rotation=45, fontsize=8.5)
ax.set_ylabel("灰色关联系数", fontsize=11, fontweight="bold")
ax.set_title("逐年关联系数变化", fontsize=13, fontweight="bold", color="#2C3E50")
ax.legend(fontsize=8.5, ncol=2)
ax.grid(alpha=0.2)
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)

plt.tight_layout()
out = os.path.join(script_dir, "灰色关联度分析.png")
plt.savefig(out, dpi=200, bbox_inches="tight")
plt.close()
print(f"\n已保存: {out}")

# ---- 保存数据 ----
result_df = pd.DataFrame({
    "年份": years,
    "PEEHI": np.round(Y, 1),
    "S1关联系数": np.round(coef[:, 0], 4),
    "S2关联系数": np.round(coef[:, 1], 4),
    "S3关联系数": np.round(coef[:, 2], 4),
    "S4关联系数": np.round(coef[:, 3], 4),
})
result_df.to_csv(os.path.join(script_dir, "灰色关联度_结果.csv"), index=False, encoding="utf-8-sig")

grade_df = pd.DataFrame({
    "变量": labels,
    "灰色关联度": np.round(grades, 4),
    "排序": [list(rank).index(i) + 1 for i in range(4)],
})
grade_df.to_csv(os.path.join(script_dir, "灰色关联度_排序.csv"), index=False, encoding="utf-8-sig")

print(f"已保存: 灰色关联度_结果.csv")
print(f"已保存: 灰色关联度_排序.csv")
