"""
考研热度分析系统 — 交互式可视化看板
====================================
基于 Streamlit + Plotly，提供 2010-2024 年考研热度及其驱动因素的全景式交互分析。
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os

# ============================================================
# 页面配置
# ============================================================
st.set_page_config(
    page_title="考研热度分析系统",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# 配色方案（全局统一）
# ============================================================
C = {
    "red": "#E74C3C", "blue": "#2980B9", "green": "#27AE60",
    "orange": "#E67E22", "purple": "#8E44AD", "teal": "#1ABC9C",
    "gold": "#F39C12", "dark": "#2C3E50", "grey": "#95A5A6",
    "cyan": "#3498DB", "pink": "#E91E63", "bg": "#F8F9FA",
}

# ============================================================
# 数据加载（缓存）
# ============================================================
@st.cache_data
def load_data():
    base = os.path.dirname(os.path.abspath(__file__))
    df = pd.read_csv(os.path.join(base, "data_show", "year.csv"))
    peehi = pd.read_csv(os.path.join(base, "data_analyze", "PEEHI_热度指数.csv"))
    grey = pd.read_csv(os.path.join(base, "data_analyze", "灰色关联度_排序.csv"))
    contrib = pd.read_csv(os.path.join(base, "data_analyze", "贡献度分析.csv"))
    sim = pd.read_csv(os.path.join(base, "data_trend_simulate", "情景模拟结果.csv"))
    return df, peehi, grey, contrib, sim


df, peehi, grey, contrib, sim = load_data()
years = df["年份"].values
PEEHI = peehi["PEEHI_归一化"].values

# ============================================================
# 侧边栏
# ============================================================
with st.sidebar:
    st.markdown("## 📊 考研热度分析系统")
    st.markdown("---")

    # 年份范围
    year_range = st.slider(
        "📅 选择年份范围",
        min_value=2010, max_value=2024, value=(2010, 2024),
    )
    yr_start, yr_end = year_range
    mask = (years >= yr_start) & (years <= yr_end)

    st.markdown("---")

    # 导航
    st.markdown("### 🧭 分析模块")
    tab = st.radio(
        "选择模块",
        ["🏠 总览看板", "💼 就业市场", "🏛️ 考公替代",
         "🎓 招生结构", "📈 综合对比", "🔮 情景模拟"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown(
        "<small>数据来源：教育部、国家统计局、麦可思研究院<br>"
        "时间跨度：2010—2024 年<br>"
        "工具：Streamlit + Plotly</small>",
        unsafe_allow_html=True,
    )

# ============================================================
# 辅助函数
# ============================================================
def make_layout(title, height=450):
    """统一的 Plotly 布局模板"""
    return dict(
        title=dict(text=title, font=dict(size=16, color=C["dark"]), x=0.02),
        height=height,
        margin=dict(l=40, r=40, t=55, b=40),
        plot_bgcolor=C["bg"],
        paper_bgcolor="white",
        hovermode="x unified",
        legend=dict(orientation="h", y=1.10, x=0, font=dict(size=11)),
        font=dict(family="Microsoft YaHei, SimHei, sans-serif"),
    )


def metric_card(label, value, delta=None, color=C["blue"]):
    """自定义指标卡片"""
    delta_str = f'<span style="color:{C["green"] if delta and delta > 0 else C["red"]};font-size:0.9em;">{"↑" if delta and delta > 0 else "↓" if delta else ""}{abs(delta):.1f}%</span>' if delta else ""
    st.markdown(
        f'<div style="background:white;border-radius:10px;padding:16px;'
        f'border-left:4px solid {color};margin:4px 0;">'
        f'<div style="font-size:0.85em;color:#7F8C8D;">{label}</div>'
        f'<div style="font-size:1.8em;font-weight:bold;color:{color};">{value}</div>'
        f'{delta_str}</div>',
        unsafe_allow_html=True,
    )

# ============================================================
# 总览看板
# ============================================================
if tab == "🏠 总览看板":
    st.markdown("## 🏠 考研热度总览看板")
    st.markdown("综合展示 PEEHI 热度指数、关键指标卡片与年度趋势。")

    # 指标卡片行
    idx_start = max(0, yr_start - 2010)
    idx_end = min(15, yr_end - 2010 + 1)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        pe_now = PEEHI[mask][-1] if mask.any() else 0
        pe_prev = PEEHI[mask][-2] if mask.sum() > 1 else pe_now
        metric_card("PEEHI 热度指数", f"{pe_now:.1f}", delta=pe_now - pe_prev, color=C["red"])
    with col2:
        ky_now = df["报名人数(万)"].values[mask][-1] if mask.any() else 0
        ky_max = df["报名人数(万)"].values[mask].max() if mask.any() else 0
        metric_card("考研报名人数(万)", f"{ky_now:.0f}", color=C["blue"])
    with col3:
        ratio_now = df["受雇工作比例(%)"].values[mask][-1] if mask.any() else 0
        metric_card("受雇工作比例(%)", f"{ratio_now:.1f}", color=C["orange"])
    with col4:
        gk_now = df["报名过审人数(万)"].values[mask][-1] if mask.any() else 0
        metric_card("国考过审人数(万)", f"{gk_now:.0f}", color=C["purple"])

    st.markdown("---")

    # PEEHI 趋势图
    fig = go.Figure()
    ym = years[mask]
    pm = PEEHI[mask]

    fig.add_trace(go.Scatter(
        x=ym, y=pm, mode="lines+markers",
        line=dict(color=C["red"], width=3),
        marker=dict(size=8, color="white", line=dict(width=2, color=C["red"])),
        name="PEEHI 热度指数",
        hovertemplate="<b>%{x}年</b><br>PEEHI: %{y:.1f}<extra></extra>",
    ))
    # 低/中/高分区
    fig.add_hrect(y0=0, y1=33, fillcolor="green", opacity=0.04, line_width=0, name="低温区")
    fig.add_hrect(y0=33, y1=66, fillcolor="orange", opacity=0.04, line_width=0, name="中温区")
    fig.add_hrect(y0=66, y1=100, fillcolor="red", opacity=0.06, line_width=0, name="高温区")
    fig.update_layout(**make_layout(f"PEEHI 考研综合热度指数（{yr_start}—{yr_end}）", 420))
    fig.update_yaxes(title="PEEHI (0-100)", range=[-5, 110])
    st.plotly_chart(fig, use_container_width=True)

    # 提示
    with st.expander("💡 怎么看这张图？"):
        st.markdown("""
        - **绿色区域（0-33）**：考研热度较低，市场供需相对均衡
        - **黄色区域（33-66）**：热度上升中，竞争开始加剧
        - **红色区域（66-100）**：高位运行，录取竞争激烈
        - 将鼠标悬停在数据点上可查看精确年份与数值
        - 使用左侧年份滑块可缩放到感兴趣的时间段
        """)

# ============================================================
# 就业市场
# ============================================================
elif tab == "💼 就业市场":
    st.markdown("## 💼 就业市场压力分析")
    st.markdown("考察本科毕业生的薪资水平与就业吸纳能力如何影响考研热度。")

    # 指标选择
    metric_choice = st.radio(
        "选择查看指标：",
        ["📊 名义 vs 实际月薪", "📉 受雇工作比例", "📈 青年失业率（2018+）"],
        horizontal=True,
    )

    ym = years[mask]

    if "月薪" in metric_choice:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=ym, y=df["本科毕业半年月薪(元)"].values[mask],
            name="名义月薪", marker=dict(color=C["cyan"], opacity=0.6),
            hovertemplate="名义: %{y:.0f}元<extra></extra>",
        ))
        fig.add_trace(go.Bar(
            x=ym, y=df["实际月薪(2010年不变价,元)"].values[mask],
            name="实际月薪(2010不变价)", marker=dict(color=C["blue"], opacity=0.85),
            hovertemplate="实际: %{y:.0f}元<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=ym, y=df["本科毕业半年月薪(元)"].values[mask],
            mode="lines+markers", name="名义趋势",
            line=dict(color=C["cyan"], width=2, dash="dot"),
            marker=dict(size=4), showlegend=False,
        ))
        fig.update_layout(**make_layout(f"本科毕业半年月薪：名义 vs 实际（{yr_start}—{yr_end}）"))
        fig.update_yaxes(title="月薪（元）")
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("💡 解读"):
            st.markdown("浅色柱为名义月薪，深色柱为剔除通胀后的实际购买力。两者差距越大，通胀侵蚀越严重。")

    elif "受雇" in metric_choice:
        fig = go.Figure()
        emp = df["受雇工作比例(%)"].values[mask]
        fig.add_trace(go.Scatter(
            x=ym, y=emp, mode="lines+markers",
            line=dict(color=C["orange"], width=3),
            marker=dict(size=10, color="white", line=dict(width=2.5, color=C["orange"])),
            fill="tozeroy", fillcolor="rgba(230,126,34,0.1)",
            name="受雇工作比例",
            hovertemplate="<b>%{x}年</b><br>受雇比例: %{y:.1f}%<extra></extra>",
        ))
        # 均值线
        fig.add_hline(y=emp.mean(), line_dash="dash", line_color=C["grey"],
                      annotation_text=f"均值 {emp.mean():.1f}%")
        fig.update_layout(**make_layout(f"本科毕业生受雇工作比例（{yr_start}—{yr_end}）"))
        fig.update_yaxes(title="比例 (%)")
        st.plotly_chart(fig, use_container_width=True)

    else:
        # 青年失业率——仅有效年份
        unemp = df["16-24岁青年失业率(%)"].values[mask]
        valid = ~np.isnan(unemp)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=ym[valid], y=unemp[valid], mode="lines+markers",
            line=dict(color=C["red"], width=3, dash="dot"),
            marker=dict(size=12, color="white", line=dict(width=2.5, color=C["red"])),
            name="青年失业率",
        ))
        fig.update_layout(**make_layout(f"16-24岁青年失业率（仅有效年份）"))
        fig.update_yaxes(title="失业率 (%)")
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("⚠️ 注意"):
            st.markdown("2010—2017 无数据（统计制度未建立），2023 年口径断裂（暂停→不含在校生新口径）。")

# ============================================================
# 考公替代
# ============================================================
elif tab == "🏛️ 考公替代":
    st.markdown("## 🏛️ 考公与考研替代效应")
    st.markdown("检验国考热度对考研热度的分流作用。")

    ym = years[mask]
    ky = df["报名人数(万)"].values[mask]
    gk = df["报名过审人数(万)"].values[mask]

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    # 考研报名（左轴，柱状）
    fig.add_trace(go.Bar(
        x=ym, y=ky, name="考研报名人数",
        marker=dict(color=C["red"], opacity=0.65),
        hovertemplate="考研: %{y:.0f}万<extra></extra>",
    ), secondary_y=False)
    # 国考过审（右轴，折线）
    fig.add_trace(go.Scatter(
        x=ym, y=gk, name="国考过审人数",
        mode="lines+markers",
        line=dict(color=C["blue"], width=3),
        marker=dict(size=9, color="white", line=dict(width=2, color=C["blue"])),
        hovertemplate="国考: %{y:.1f}万<extra></extra>",
    ), secondary_y=True)

    fig.update_layout(**make_layout(f"考研 vs 国考：双轴对比（{yr_start}—{yr_end}）"))
    fig.update_yaxes(title_text="考研报名（万人）", secondary_y=False, gridcolor="#E5E7E9")
    fig.update_yaxes(title_text="国考过审（万人）", secondary_y=True, gridcolor="#E5E7E9")
    st.plotly_chart(fig, use_container_width=True)

    # 报录比趋势
    st.markdown("---")
    fig2 = go.Figure()
    gk_ratio = df["报录比(X:1)"].values[mask]
    colors_bar = ["#ABEBC6" if v < 60 else "#F9E79F" if v < 80 else "#F1948A" for v in gk_ratio]
    fig2.add_trace(go.Bar(
        x=ym, y=gk_ratio, name="国考报录比",
        marker=dict(color=colors_bar),
        hovertemplate="报录比: %{y:.0f}:1<extra></extra>",
    ))
    fig2.add_hline(y=gk_ratio.mean(), line_dash="dash", line_color=C["grey"],
                   annotation_text=f"均值 {gk_ratio.mean():.0f}:1")
    fig2.update_layout(**make_layout("国考报录比变化（过审/招录）"))
    fig2.update_yaxes(title="报录比 (X:1)")
    st.plotly_chart(fig2, use_container_width=True)

    with st.expander("💡 替代效应怎么看？"):
        st.markdown("""
        观察 2023—2024 年：考研报名人数向下转折的同时，国考过审人数继续攀升——
        这是"此消彼长"的最直接信号。两条线在近年的背离程度越大，替代效应越明显。
        """)

# ============================================================
# 招生结构
# ============================================================
elif tab == "🎓 招生结构":
    st.markdown("## 🎓 硕士招生结构变迁")
    st.markdown("展示学硕与专硕的此消彼长，以及推免对统考名额的挤压。")

    ym = years[mask]
    xs = df["学术硕士招生(万)"].values[mask]
    zs = df["专业硕士招生(万)"].values[mask]
    total = xs + zs
    baoyan = df["推免保研人数(万,估算)"].values[mask]
    tongkao = total - baoyan

    view = st.radio("选择视图：", ["📊 学硕 vs 专硕（堆叠面积）", "🔍 推免 vs 统考（名额分配）"], horizontal=True)

    if "学硕" in view:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=ym, y=xs, mode="lines", name="学术硕士",
            line=dict(color=C["blue"], width=1),
            stackgroup="one", fillcolor="rgba(41,128,185,0.5)",
            hovertemplate="学硕: %{y:.1f}万<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=ym, y=zs, mode="lines", name="专业硕士",
            line=dict(color=C["orange"], width=1),
            stackgroup="one", fillcolor="rgba(230,126,34,0.55)",
            hovertemplate="专硕: %{y:.1f}万<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=ym, y=total, mode="lines+markers", name="总招生",
            line=dict(color=C["dark"], width=2.5), marker=dict(size=6, color="white",
            line=dict(width=2, color=C["dark"])),
        ))
        # 2020 政策线
        if 2020 >= yr_start and 2020 <= yr_end:
            fig.add_vline(x=2020, line_dash="dash", line_color=C["red"], line_width=2,
                          annotation_text="2020扩招政策")
        fig.update_layout(**make_layout("硕士招生结构：学硕 vs 专硕"))
        fig.update_yaxes(title="招生人数（万人）")
        st.plotly_chart(fig, use_container_width=True)

    else:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=ym, y=tongkao, mode="lines", name="统考名额",
            line=dict(color=C["green"], width=1),
            stackgroup="one", fillcolor="rgba(39,174,96,0.5)",
            hovertemplate="统考: %{y:.1f}万<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=ym, y=baoyan, mode="lines", name="推免保研",
            line=dict(color=C["purple"], width=1),
            stackgroup="one", fillcolor="rgba(142,68,173,0.4)",
            hovertemplate="推免: %{y:.1f}万<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=ym, y=total, mode="lines+markers", name="总招生",
            line=dict(color=C["dark"], width=2.5), marker=dict(size=6, color="white",
            line=dict(width=2, color=C["dark"])),
        ))
        fig.update_layout(**make_layout("推免保研 vs 统考录取名额"))
        fig.update_yaxes(title="人数（万人）")
        st.plotly_chart(fig, use_container_width=True)

# ============================================================
# 综合对比
# ============================================================
elif tab == "📈 综合对比":
    st.markdown("## 📈 多变量综合对比")
    st.markdown("将所有核心变量标准化后叠合在同一坐标系，观察变量间联动关系。")

    ym = years[mask]

    # 选择要展示的变量
    var_options = {
        "报名人数(万)": ("考研报名人数", C["red"]),
        "读研比例(%)": ("读研比例", C["blue"]),
        "实际月薪增长率": ("实际月薪增长率", C["green"]),
        "受雇工作比例(%)": ("受雇工作比例", C["orange"]),
        "报名过审人数(万)": ("国考过审人数", C["cyan"]),
        "专硕占比(%)": ("专硕占比", C["gold"]),
    }

    selected = st.multiselect(
        "选择要对比的变量（建议 3-5 个，避免线条重叠）",
        options=list(var_options.keys()),
        default=["报名人数(万)", "受雇工作比例(%)", "专硕占比(%)"],
    )

    if selected:
        fig = go.Figure()

        # 计算月薪增长率
        rs = df["实际月薪(2010年不变价,元)"].values
        g = np.insert(np.diff(rs) / rs[:-1] * 100, 0, np.nan)

        for var in selected:
            label, color = var_options[var]
            if var == "实际月薪增长率":
                data = g[mask]
            else:
                data = df[var].values[mask]
            # Min-Max 归一化
            valid = ~np.isnan(data)
            d_min, d_max = data[valid].min(), data[valid].max()
            z = (data - d_min) / (d_max - d_min) if d_max > d_min else np.zeros_like(data)

            fig.add_trace(go.Scatter(
                x=ym, y=z, mode="lines+markers", name=label,
                line=dict(color=color, width=2.2),
                marker=dict(size=5, color="white", line=dict(width=1.5, color=color)),
                hovertemplate=f"<b>%{{x}}年</b><br>{label}: %{{y:.3f}} (归一化)<extra></extra>",
            ))

        # 2020 参考线
        if 2020 >= yr_start and 2020 <= yr_end:
            fig.add_vline(x=2020, line_dash="dot", line_color=C["grey"], line_width=1.5,
                          opacity=0.5, annotation_text="2020")

        fig.update_layout(**make_layout(f"标准化多变量叠合（{yr_start}—{yr_end}）", 500))
        fig.update_yaxes(title="Min-Max 归一化值", range=[-0.05, 1.08])
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("💡 怎么看叠合图？"):
            st.markdown("""
            - 所有变量被缩放到 [0, 1] 区间，消除量纲差异
            - **同向变动**：曲线一起上升或下降 → 正关联
            - **反向变动**：一升一降 → 负关联（如受雇工作比例 vs 报名人数）
            - 取消勾选某个变量可以排除干扰，聚焦感兴趣的变量对
            """)
    else:
        st.info("👆 请至少选择一个变量。")

# ============================================================
# 情景模拟
# ============================================================
elif tab == "🔮 情景模拟":
    st.markdown("## 🔮 2025—2030 年考研热度情景模拟")
    st.markdown("基于四类驱动机制的历史变化趋势与灰色关联权重，外推四种情景下的 PEEHI 演化路径。")

    # 情景选择
    scenario_choice = st.radio(
        "选择情景对比：",
        ["全部四条路径", "仅基准 vs 综合治理", "仅基准 vs 就业加剧 vs 考公分流"],
        horizontal=True,
    )

    fig = go.Figure()

    # 历史线
    fig.add_trace(go.Scatter(
        x=years, y=PEEHI, mode="lines+markers", name="历史 PEEHI",
        line=dict(color=C["dark"], width=3.5),
        marker=dict(size=8, color="white", line=dict(width=2.5, color=C["dark"])),
        hovertemplate="<b>%{x}年</b><br>历史PEEHI: %{y:.1f}<extra></extra>",
    ))

    # 分界线
    fig.add_vline(x=2024.4, line_dash="dash", line_color=C["grey"], line_width=1.5)
    fig.add_annotation(x=2024.8, y=105, text="← 模拟期", showarrow=False,
                       font=dict(size=10, color=C["grey"]))

    # 情景路径
    scenarios = {
        "PEEHI_基准延续情景": ("基准延续", C["green"]),
        "PEEHI_就业压力加剧情景": ("就业加剧", C["red"]),
        "PEEHI_考公分流情景": ("考公分流", C["purple"]),
        "PEEHI_综合治理降温情景": ("综合治理", C["gold"]),
    }

    for col, (name, color) in scenarios.items():
        if "全部" in scenario_choice:
            show = True
        elif "综合治理" in scenario_choice:
            show = name in ("基准延续", "综合治理")
        else:
            show = name != "综合治理"

        if show:
            fig.add_trace(go.Scatter(
                x=sim["年份"], y=sim[col], mode="lines+markers", name=name,
                line=dict(color=color, width=2.5, dash="dash"),
                marker=dict(size=7, color="white", line=dict(width=2, color=color)),
                hovertemplate=f"<b>%{{x}}年</b><br>{name}: %{{y:.1f}}<extra></extra>",
            ))

    fig.update_layout(**make_layout("2025—2030 PEEHI 情景模拟", 480))
    fig.update_yaxes(title="PEEHI", range=[0, 115])
    fig.update_xaxes(range=[2009.5, 2030.5], dtick=2)
    st.plotly_chart(fig, use_container_width=True)

    # 结果表格
    st.markdown("---")
    st.markdown("### 📋 模拟结果数据")
    cols_show = ["年份", "PEEHI_基准延续情景", "PEEHI_就业压力加剧情景",
                 "PEEHI_考公分流情景", "PEEHI_综合治理降温情景"]
    st.dataframe(
        sim[cols_show].set_index("年份").style
        .format("{:.1f}")
        .background_gradient(cmap="RdYlGn_r", axis=0),
        use_container_width=True,
    )

    with st.expander("⚠️ 方法论说明"):
        st.markdown("""
        **这不是预测，而是探索性推演。** 模拟基于以下假设：
        1. 以 2024 年真实 PEEHI 为锚定点，不偏离历史轨迹
        2. 四类机制按近五年（2020-2024）年均变化量线性外推
        3. 灰色关联权重反映历史上 S→PEEHI 的映射关系，假设该关系在未来保持稳定
        4. S₁ 和 S₃ 已接近 [0,100] 上限，未来上升空间受结构性制约

        **使用建议**：关注不同情景间的**相对差异**和**方向性变化**，而非绝对数值。
        """)
