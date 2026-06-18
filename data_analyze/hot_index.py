"""
PEEHI 考研综合热度指数 — 熵权法构建（修正版 v2）
================================================
修正内容：
  1. X2_报录比：原错误使用 year.csv 中的"报录比(X:1)"列（实为国考报录比），
               现改为 报名人数 / 硕士实际录取人数（正确口径）。
  2. X3_统考竞争度：分子不再减去推免人数（考研报名人数通常不含推免生）。
  3. X4_升学率：已从 PEEHI 中移除。升学率衡量的是供给端响应（"退烧药"），
               不适合作为热度指数（"体温计"）的构成指标。
  4. 路径统一为 data_show/year.csv。
"""

import pandas as pd
import numpy as np
import os, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)


def calculate_peehi(df):
    res = df.copy()

    # ----------------------------------------------------------
    # 1. 子指标（PEEHI 仅含 X1/X2/X3，X4 升学历计但不纳入）
    # ----------------------------------------------------------
    res["X1_参与率"] = res["报名人数(万)"] / res["普通本科毕业生数(万)"]

    res["X2_报录比"] = res["报名人数(万)"] / res["硕士实际录取人数(万)"]

    res["X3_统考竞争度"] = res["报名人数(万)"] / (
        res["硕士总招生(万)"] - res["推免保研人数(万,估算)"])

    # X4 仅保留原始值供参考，不参与 PEEHI 合成
    res["X4_升学率_参考"] = res["硕士实际录取人数(万)"] / res["普通本科毕业生数(万)"]

    indicator_names = ["X1_参与率", "X2_报录比", "X3_统考竞争度"]
    label_names = ["参与率(X1)", "报录比(X2)", "统考竞争度(X3)"]
    X = res[indicator_names].values

    # ----------------------------------------------------------
    # 2. 熵权法
    # ----------------------------------------------------------
    n = X.shape[0]

    X_min = X.min(axis=0)
    X_max = X.max(axis=0)
    Z = (X - X_min) / (X_max - X_min)

    P = Z / (Z.sum(axis=0) + 1e-12)

    e = -1.0 / np.log(n) * np.sum(P * np.log(P + 1e-12), axis=0)

    d = 1.0 - e
    weights = d / d.sum()

    res["PEEHI_原始"] = np.dot(Z, weights)
    s_min = res["PEEHI_原始"].min()
    s_max = res["PEEHI_原始"].max()
    res["PEEHI_归一化"] = (res["PEEHI_原始"] - s_min) / (s_max - s_min) * 100.0

    for j, name in enumerate(indicator_names):
        res[f"{name}_归一化"] = Z[:, j]
        res[f"{name}_权重"] = weights[j]

    weight_dict = dict(zip(label_names, np.round(weights, 4)))
    return res, weight_dict


# ================================================================
if __name__ == "__main__":
    df = pd.read_csv(os.path.join(project_dir, "data_show", "year.csv"))
    res_df, weights = calculate_peehi(df)

    out_cols = ["年份",
                "X1_参与率", "X2_报录比", "X3_统考竞争度", "X4_升学率_参考",
                "PEEHI_原始", "PEEHI_归一化",
                "X1_参与率_归一化", "X2_报录比_归一化", "X3_统考竞争度_归一化",
                "X1_参与率_权重", "X2_报录比_权重", "X3_统考竞争度_权重"]
    peehi_csv = os.path.join(script_dir, "PEEHI_热度指数.csv")
    res_df[out_cols].to_csv(peehi_csv, index=False, encoding="utf-8-sig")
    print(f"[OK] 已保存: {peehi_csv}")

    weight_csv = os.path.join(script_dir, "PEEHI_权重.csv")
    pd.DataFrame({"指标": list(weights.keys()), "权重": list(weights.values())}) \
        .to_csv(weight_csv, index=False, encoding="utf-8-sig")
    print(f"[OK] 已保存: {weight_csv}")

    print("\n" + "=" * 60)
    print("PEEHI 熵权法权重（三指标，已移除 X4 升学率）")
    print("=" * 60)
    for k, v in weights.items():
        bar = "█" * int(v * 200)
        print(f"  {k:<18}  {v:.4f}  {bar}")

    print(f"\nPEEHI 归一化值（0–100）：")
    for _, row in res_df.iterrows():
        yr = int(row["年份"])
        val = row["PEEHI_归一化"]
        bar = "█" * int(val / 2)
        print(f"  {yr}: {val:6.1f}  {bar}")

    print(f"\n最低: {res_df['PEEHI_归一化'].min():.1f}（{res_df.loc[res_df['PEEHI_归一化'].idxmin(), '年份']:.0f}年）")
    print(f"最高: {res_df['PEEHI_归一化'].max():.1f}（{res_df.loc[res_df['PEEHI_归一化'].idxmax(), '年份']:.0f}年）")
    print(f"2024: {res_df[res_df['年份']==2024]['PEEHI_归一化'].values[0]:.1f}")

