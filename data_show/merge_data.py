"""
合并所有 CSV 文件为一张大表
============================
输入：7 个 CSV 文件（年份 2010–2024）
附加：用 CPI 对名义月薪平减，计算实际月薪
输出：year.csv（统一大表，按年份对齐）
"""

import pandas as pd
import numpy as np
import sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ============================================================
# 1. 逐个读取，只保留 2010–2024
# ============================================================

# --- (A) 考研报名人数 ---
df_a = pd.read_csv("考研报名数据.csv")
df_a = df_a[df_a["年份"].between(2010, 2024)].copy()

# --- (B) 硕士录取人数 ---
df_b = pd.read_csv("硕士录取数据.csv")

# --- (C) 本科毕业生数 ---
df_c = pd.read_csv("本科毕业生数据.csv")

# --- (D) 读研比例（只取 读研比例(%) 列，其余与 C/B 重复）---
df_d = pd.read_csv("读研比例.csv")
df_d = df_d[["年份", "读研比例(%)"]]

# --- (E) 就业市场指标 ---
df_e = pd.read_csv("就业市场指标.csv")

# --- (F) 国考数据 ---
df_f = pd.read_csv("国考数据.csv")

# --- (G) 招生政策与保研数据 ---
df_g = pd.read_csv("招生政策与保研数据.csv")

# ============================================================
# 2. 依次合并
# ============================================================
dfs = [df_a, df_b, df_c, df_d, df_e, df_f, df_g]

merged = dfs[0]
for i, df in enumerate(dfs[1:], start=2):
    merged = pd.merge(merged, df, on="年份", how="outer")

# ============================================================
# 3. CPI 平减：名义月薪 → 实际月薪（以 2010 年为基期）
# ============================================================
CPI = {  # 居民消费价格指数（上年=100），来源：国家统计局
    2010: 103.3, 2011: 105.4, 2012: 102.6, 2013: 102.6, 2014: 102.0,
    2015: 101.4, 2016: 102.0, 2017: 101.6, 2018: 102.1, 2019: 102.9,
    2020: 102.5, 2021: 100.9, 2022: 102.0, 2023: 100.2, 2024: 100.2,
}

# 构建累计平减指数（2010 = 1.0000）
deflator = {}
chain = 1.0
for year in range(2010, 2025):
    if year == 2010:
        deflator[year] = 1.0
    else:
        chain *= CPI[year] / 100.0
        deflator[year] = chain

merged["CPI(上年=100)"] = merged["年份"].map(CPI)
merged["累计平减指数(2010=1)"] = merged["年份"].map(deflator)
merged["实际月薪(2010年不变价,元)"] = np.round(
    merged["本科毕业半年月薪(元)"] / merged["累计平减指数(2010=1)"], 0
)

# ============================================================
# 4. 保存
# ============================================================
merged = merged.sort_values("年份").reset_index(drop=True)
merged.to_csv("year.csv", index=False, encoding="utf-8-sig")

# ============================================================
# 5. 打印预览
# ============================================================
print("=" * 100)
print("合并完成！共 {} 行 × {} 列".format(*merged.shape))
print("输出文件：year.csv")
print("=" * 100)

print(f"\n全部列名（{len(merged.columns)} 列）：")
for i, col in enumerate(merged.columns, 1):
    print(f"  {i:2d}. {col}")

# 关键列预览
print(f"\n{'年份':<6} {'名义月薪':<10} {'CPI':<8} {'平减指数':<10} {'实际月薪':<10}")
print("-" * 50)
for _, row in merged.iterrows():
    print(f"{int(row['年份']):<6} {row['本科毕业半年月薪(元)']:<10.0f} "
          f"{row['CPI(上年=100)']:<8.1f} {row['累计平减指数(2010=1)']:<10.4f} "
          f"{row['实际月薪(2010年不变价,元)']:<10.0f}")

# 缺失检查
print(f"\n各列缺失值统计：")
missing = merged.isnull().sum()
for col in merged.columns:
    if missing[col] > 0:
        print(f"  {col}: {int(missing[col])} 个缺失")

print(f"\n年份范围：{int(merged['年份'].min())} – {int(merged['年份'].max())}")
print(f"总行数：{len(merged)}")
