"""
考研热度分析系统
===============
交互式数据可视化看板 · Streamlit + Plotly
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EDITORIAL_DIR = os.path.join(BASE_DIR, "assets", "editorial")

# ============================================================
st.set_page_config(
    page_title="考研热度分析系统",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# CSS
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Noto+Sans+SC:wght@400;500;600;700&display=swap');
    :root { --ink:#17211d; --muted:#68736d; --paper:#f4f1ea; --card:#fffdf8; --line:#ded9ce; --accent:#e45b3f; }
    * { font-family:'DM Sans','Noto Sans SC','Microsoft YaHei',sans-serif; }
    .stApp { background:var(--paper); color:var(--ink); }
    .main .block-container { padding:1.2rem 3.4rem 4rem; max-width:1480px; }
    [data-testid="stSidebar"], [data-testid="collapsedControl"] { display:none; }
    header { background:transparent !important; }

    .masthead { display:flex; align-items:flex-start; justify-content:space-between; gap:2rem; padding:1.2rem 0 1.5rem; border-bottom:1px solid var(--line); }
    .brand-kicker { color:var(--accent); font-size:.72rem; font-weight:700; letter-spacing:.16em; text-transform:uppercase; margin-bottom:.45rem; }
    .brand-title { color:var(--ink); font-size:clamp(1.7rem,3vw,2.75rem); font-weight:600; letter-spacing:-.055em; line-height:1; }
    .brand-sub { color:var(--muted); font-size:.82rem; margin-top:.65rem; }
    .issue { color:var(--muted); font-size:.73rem; line-height:1.7; text-align:right; padding-top:.25rem; white-space:nowrap; }

    [data-testid="stRadio"] > div { gap:.42rem !important; }
    [data-testid="stRadio"] label { background:transparent !important; border:1px solid var(--line); border-radius:999px !important; padding:.48rem .9rem !important; transition:.18s ease; }
    [data-testid="stRadio"] label:hover { border-color:#a9a296; transform:translateY(-1px); }
    [data-testid="stRadio"] label:has(input:checked) { background:var(--ink) !important; border-color:var(--ink); }
    [data-testid="stRadio"] label:has(input:checked) p { color:#fffdf8 !important; }
    [data-testid="stRadio"] label p { color:#4e5953 !important; font-size:.82rem !important; font-weight:600; }
    [data-testid="stSlider"] { padding:.1rem .15rem 0; }
    [data-testid="stSlider"] label p { color:var(--muted); font-size:.76rem; letter-spacing:.04em; }
    [data-testid="stThumbValue"] { color:var(--ink) !important; }

    .page-hero { display:grid; grid-template-columns:minmax(0,1fr) minmax(260px,.52fr); gap:3rem; align-items:end; padding:2.8rem 0 2rem; }
    .eyebrow { color:var(--accent); font-size:.72rem; font-weight:700; letter-spacing:.14em; text-transform:uppercase; margin-bottom:.8rem; }
    .page-title { color:var(--ink); font-family:'Noto Sans SC',sans-serif; font-size:clamp(2.2rem,4vw,4.1rem); font-weight:600; letter-spacing:-.065em; line-height:1.08; }
    .page-deck { color:var(--muted); font-size:.9rem; line-height:1.8; max-width:31rem; padding-bottom:.3rem; }

    .card { min-height:128px; background:var(--card); border:1px solid var(--line); border-radius:2px; padding:1.25rem 1.35rem; margin-bottom:.8rem; box-shadow:0 8px 28px rgba(37,43,39,.035); transition:.2s ease; }
    .card:hover { transform:translateY(-2px); box-shadow:0 14px 32px rgba(37,43,39,.07); }
    .card-label { font-size:.7rem; color:var(--muted); text-transform:uppercase; letter-spacing:.08em; margin-bottom:.75rem; }
    .card-value { font-size:2rem; font-weight:600; color:var(--ink); line-height:1.05; letter-spacing:-.04em; }
    .card-delta { font-size:.75rem; margin-top:.62rem; }
    .section-title { color:var(--ink); font-size:.76rem; font-weight:700; letter-spacing:.1em; text-transform:uppercase; margin:2rem 0 1rem; padding-bottom:.7rem; border-bottom:1px solid var(--line); }
    .note-block { background:#ebe7de; border-left:3px solid var(--accent); padding:1rem 1.25rem; margin-top:1rem; }
    .note-block p { color:#59635e; font-size:.8rem; margin:0; line-height:1.75; }
    .story-copy { min-height:290px; background:#17211d; padding:2rem 2.15rem; display:flex; flex-direction:column; justify-content:center; }
    .story-kicker { color:#ef8a70; font-size:.68rem; font-weight:700; letter-spacing:.14em; text-transform:uppercase; margin-bottom:.8rem; }
    .story-title { color:#fffdf8; font-size:1.65rem; font-weight:600; letter-spacing:-.035em; line-height:1.25; margin-bottom:.9rem; }
    .story-body { color:#c3cbc6; font-size:.86rem; line-height:1.85; }
    .story-points { display:grid; grid-template-columns:1fr 1fr; gap:.7rem; margin-top:1.25rem; }
    .story-point { border-top:1px solid #43504a; color:#e7e5dd; padding-top:.7rem; font-size:.74rem; line-height:1.55; }
    .image-caption { color:var(--muted); font-size:.68rem; letter-spacing:.04em; margin-top:-.2rem; }
    [data-testid="stImage"] img { width:100%; height:290px; object-fit:cover; border-radius:0; }
    .insight-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:.8rem; margin:1rem 0 1.8rem; }
    .insight-item { background:#ebe7de; padding:1rem 1.1rem; border-top:2px solid #879b8b; }
    .insight-no { color:var(--accent); font-size:.66rem; font-weight:700; letter-spacing:.12em; }
    .insight-text { color:#3e4943; font-size:.78rem; line-height:1.65; margin-top:.45rem; }
    .pull-quote { color:var(--ink); font-family:'Noto Sans SC',sans-serif; font-size:1.35rem; line-height:1.55; letter-spacing:-.025em; padding:1.5rem 0 1.6rem 1.4rem; border-left:3px solid var(--accent); max-width:920px; }
    [data-testid="stPlotlyChart"] { background:var(--card); border:1px solid var(--line); padding:.65rem .8rem .2rem; box-shadow:0 8px 28px rgba(37,43,39,.025); }
    .stMultiSelect [data-baseweb="select"] > div { background:var(--card); border-color:var(--line); }
    .stMultiSelect [data-baseweb="tag"] { background:#e5e0d5 !important; color:var(--ink) !important; border-radius:999px !important; }
    #MainMenu, footer, header [data-testid="stDecoration"], [data-testid="stStatusWidget"] { visibility:hidden; }
    [data-testid="stSidebarNav"] { display:none; }
    @media(max-width:800px){ .main .block-container{padding:1rem 1.1rem 3rem}.masthead,.page-hero{grid-template-columns:1fr;display:grid}.issue{text-align:left}.page-hero{gap:1rem;padding:2rem 0 1.4rem}.page-title{font-size:2.45rem}.insight-grid{grid-template-columns:1fr}.story-copy{min-height:auto}[data-testid="stImage"] img{height:230px} }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 数据加载
# ============================================================
@st.cache_data
def load_data():
    base = os.path.dirname(os.path.abspath(__file__))
    df = pd.read_csv(os.path.join(base, "data_show", "year.csv"))
    peehi = pd.read_csv(os.path.join(base, "data_analyze", "PEEHI_热度指数.csv"))
    sim = pd.read_csv(os.path.join(base, "data_trend_simulate", "情景模拟结果.csv"))
    return df, peehi, sim


df, peehi, sim = load_data()
years = df["年份"].values
PEEHI = peehi["PEEHI_归一化"].values

# ── 衍生数据 ──
rs = df["实际月薪(2010年不变价,元)"].values
salary_growth = np.insert(np.diff(rs) / rs[:-1] * 100, 0, np.nan)

# 四类 S 指数（与 scenario_simulation.py 一致）
def _norm(v):
    v = np.asarray(v, float)
    return np.zeros_like(v) if np.nanmax(v) == np.nanmin(v) else (v - np.nanmin(v)) / (np.nanmax(v) - np.nanmin(v)) * 100
def _norm_rev(v):
    v = np.asarray(v, float)
    return np.zeros_like(v) if np.nanmax(v) == np.nanmin(v) else (np.nanmax(v) - v) / (np.nanmax(v) - np.nanmin(v)) * 100

S1 = (_norm(df["普通本科毕业生数(万)"].values) + _norm(df["读研比例(%)"].values)) / 2
g_raw = np.full(len(rs), np.nan); g_raw[1:] = (rs[1:] / rs[:-1] - 1) * 100
S2 = np.nanmean(np.vstack([_norm(df["16-24岁青年失业率(%)"].values), _norm_rev(df["受雇工作比例(%)"].values), _norm_rev(g_raw)]), axis=0)
S3 = (_norm(df["硕士实际录取人数(万)"].values) + _norm(df["专硕占比(%)"].values) + df["政策哑变量(2020后=1)"].values * 100) / 3
S4 = (_norm(df["报名过审人数(万)"].values) + _norm(df["报录比(X:1)"].values)) / 2

# ============================================================
# 颜色
# ============================================================
ACCENT  = "#315f57"
RED     = "#e45b3f"
GREEN   = "#748f7a"
ORANGE  = "#c0874c"
PURPLE  = "#766c91"
CYAN    = "#4f8f88"
GOLD    = "#b8964f"
SLATE   = "#68736d"
WHITE   = "#17211d"
DARK_BG = "#fffdf8"
CARD_BG = "#fffdf8"
BORDER  = "#ded9ce"

# ============================================================
# 顶部导航与全局筛选
# ============================================================
st.markdown("""
<div class="masthead">
  <div>
    <div class="brand-kicker">Research Observatory · 01</div>
    <div class="brand-title">考研热度观察站</div>
    <div class="brand-sub">Postgraduate Entrance Examination Heat Index</div>
  </div>
  <div class="issue">教育 · 就业 · 公考<br>2010—2024 / CHINA</div>
</div>
""", unsafe_allow_html=True)

nav_col, filter_col = st.columns([3.4, 1.15], gap="large")
with nav_col:
    page = st.radio(
        "主导航",
        ["总览", "就业市场", "考公替代", "招生结构", "综合对比", "情景模拟"],
        horizontal=True,
        label_visibility="collapsed",
    )
with filter_col:
    yr_range = st.slider("观察窗口", 2010, 2024, (2010, 2024), label_visibility="visible")

yr_start, yr_end = yr_range
mask = (years >= yr_start) & (years <= yr_end)

# ============================================================
# 工具函数
# ============================================================
def plotly_template(title, height=420):
    return dict(
        title=dict(
            text=title, font=dict(size=14, color=WHITE),
            x=0.0, y=0.99, xanchor="left", yanchor="top",
            pad=dict(b=10),
        ),
        height=height,
        margin=dict(l=18, r=18, t=92, b=24),
        plot_bgcolor=DARK_BG, paper_bgcolor=DARK_BG,
        font=dict(color=SLATE, size=11, family="DM Sans, Noto Sans SC"),
        hovermode="x unified",
        legend=dict(
            orientation="h", y=1.15, x=0,
            xanchor="left", yanchor="bottom",
            font=dict(size=10, color=SLATE),
            itemwidth=44,
        ),
        xaxis=dict(gridcolor="#ebe7de", linecolor=BORDER, zeroline=False),
        yaxis=dict(gridcolor="#ebe7de", linecolor=BORDER, zeroline=False),
        hoverlabel=dict(bgcolor="#17211d", bordercolor="#17211d", font=dict(color="#fffdf8")),
    )

def page_header(index, title, deck):
    st.markdown(f"""
    <div class="page-hero">
      <div><div class="eyebrow">Chapter {index} · {yr_start}—{yr_end}</div><div class="page-title">{title}</div></div>
      <div class="page-deck">{deck}</div>
    </div>
    """, unsafe_allow_html=True)

def story_panel(image_name, kicker, title, body, points, caption):
    image_col, copy_col = st.columns([1.25, 1], gap="small")
    with image_col:
        st.image(os.path.join(EDITORIAL_DIR, image_name), width="stretch")
        st.markdown(f'<div class="image-caption">{caption}</div>', unsafe_allow_html=True)
    point_html = "".join(f'<div class="story-point">{point}</div>' for point in points)
    with copy_col:
        st.markdown(f"""
        <div class="story-copy">
          <div class="story-kicker">{kicker}</div>
          <div class="story-title">{title}</div>
          <div class="story-body">{body}</div>
          <div class="story-points">{point_html}</div>
        </div>
        """, unsafe_allow_html=True)

def insight_grid(items):
    cards = "".join(
        f'<div class="insight-item"><div class="insight-no">0{i}</div><div class="insight-text">{text}</div></div>'
        for i, text in enumerate(items, 1)
    )
    st.markdown(f'<div class="insight-grid">{cards}</div>', unsafe_allow_html=True)

def pull_quote(text):
    st.markdown(f'<div class="pull-quote">“{text}”</div>', unsafe_allow_html=True)

def metric_card(label, value, delta=None, color=ACCENT):
    d = ""
    if delta is not None:
        sign = "+" if delta >= 0 else ""
        c = GREEN if delta >= 0 else RED
        d = f'<div class="card-delta" style="color:{c};">{sign}{delta:.1f}%  vs 上年</div>'
    st.markdown(f"""
    <div class="card">
        <div class="card-label">{label}</div>
        <div class="card-value" style="color:{color};">{value}</div>
        {d}
    </div>""", unsafe_allow_html=True)

em = mask
ym = years[mask]

# ============================================================
# 页面 1 — 总览
# ============================================================
if page == "总览":
    page_header("01", "热度，不只是一条曲线", "从考研报名、就业吸纳、国考竞争到招生结构，观察教育选择背后的系统性压力与转向。")
    story_panel(
        "crossroads.png", "Opening Essay", "每一个报名数字背后，都是一次关于未来的再判断",
        "考研热度并非单纯的教育现象。它同时受到就业回报、学历门槛、招生供给与公共部门吸引力的牵引。把这些线索放在一起，才能看见选择如何被时代塑形。",
        ["从单点指标转向结构观察", "用十五年数据识别长期拐点"], "编辑插画 · 升学、就业与考公的选择岔路"
    )
    insight_grid([
        "先看 PEEHI 的方向，再判断变化来自需求端还是供给端。",
        "报名下降不必然等于热度消退，竞争结构可能仍在强化。",
        "时间筛选会同步作用于全部历史图表，便于观察阶段差异。",
    ])
    st.markdown('<div class="section-title">核心观测 · PEEHI 考研综合热度指数</div>', unsafe_allow_html=True)

    # 指标卡片
    c1, c2, c3, c4 = st.columns(4)
    pe_now = PEEHI[em][-1] if em.any() else 0
    pe_prev = PEEHI[em][-2] if em.sum() > 1 else pe_now
    ky_now = df["报名人数(万)"].values[em][-1] if em.any() else 0
    ky_prev = df["报名人数(万)"].values[em][-2] if em.sum() > 1 else ky_now
    emp_now = df["受雇工作比例(%)"].values[em][-1] if em.any() else 0
    emp_prev = df["受雇工作比例(%)"].values[em][-2] if em.sum() > 1 else emp_now
    gk_now = df["报名过审人数(万)"].values[em][-1] if em.any() else 0
    gk_prev = df["报名过审人数(万)"].values[em][-2] if em.sum() > 1 else gk_now

    with c1: metric_card("PEEHI 热度指数", f"{pe_now:.1f}", pe_now - pe_prev, RED)
    with c2: metric_card("考研报名人数", f"{ky_now:.0f} 万", (ky_now - ky_prev) / ky_prev * 100 if ky_prev else None, ACCENT)
    with c3: metric_card("受雇工作比例", f"{emp_now:.1f}%", emp_now - emp_prev, ORANGE)
    with c4: metric_card("国考过审人数", f"{gk_now:.0f} 万", (gk_now - gk_prev) / gk_prev * 100 if gk_prev else None, PURPLE)

    # PEEHI 趋势
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=years[em], y=PEEHI[em], mode="lines+markers",
        line=dict(color=RED, width=2.5),
        marker=dict(size=6, color=DARK_BG, line=dict(width=1.8, color=RED)),
        name="PEEHI",
        hovertemplate="%{x} 年 · PEEHI %{y:.1f}<extra></extra>",
    ))
    # 温区
    for y0, y1, c, label in [(0, 33, "#dce8df", "低温"), (33, 66, "#f2e4ca", "中温"), (66, 100, "#f2d7d0", "高温")]:
        fig.add_hrect(y0=y0, y1=y1, fillcolor=c, opacity=0.58, line_width=0, name=label, showlegend=False)
    fig.update_layout(**plotly_template("PEEHI 指数走势"))
    fig.update_yaxes(range=[-5, 110], title="", showgrid=False, zeroline=False)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # S1-S4 趋势
    st.markdown('<div class="section-title" style="margin-top:1.5rem;">四类驱动机制子指数</div>', unsafe_allow_html=True)
    fig2 = go.Figure()
    for s_arr, name, color in [(S1, "S1 升学基数", ACCENT), (S2, "S2 就业市场", ORANGE), (S3, "S3 政策供给", GREEN), (S4, "S4 考公替代", PURPLE)]:
        fig2.add_trace(go.Scatter(
            x=years[em], y=s_arr[em], mode="lines",
            line=dict(color=color, width=1.8), name=name,
            hovertemplate=f"{name}: %{{y:.1f}}<extra></extra>",
        ))
    fig2.update_layout(**plotly_template("S1 — S4 标准化子指数"))
    fig2.update_yaxes(range=[-5, 105], title="", showgrid=False, zeroline=False)
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    st.markdown('<div class="note-block"><p>PEEHI 由参与率 (X1)、报录比 (X2)、统考竞争度 (X3) 经熵权法合成并归一化至 0—100。'
                'S1—S4 为四类外部驱动机制子指数，均经 Min-Max 标准化处理。</p></div>', unsafe_allow_html=True)
    pull_quote("真正值得追问的，不是考研为什么变热，而是年轻人为什么越来越需要一条缓冲带。")

# ============================================================
# 页面 2 — 就业市场
# ============================================================
elif page == "就业市场":
    page_header("02", "工作的吸引力，正在改变吗？", "把名义薪资还原为真实购买力，并与就业吸纳和青年失业率并置，观察毕业生选择继续升学的现实推力。")
    story_panel(
        "employment-transition.png", "Field Note", "校园与职场之间，距离不只由一份薪资决定",
        "名义工资上涨并不自动转化为更强的职业吸引力。实际购买力、岗位获得概率与青年失业风险共同决定毕业生是否愿意立即进入劳动力市场。",
        ["实际工资剔除 CPI 影响", "就业吸纳刻画岗位承接能力"], "编辑插画 · 从校园走向职场的过渡地带"
    )
    st.markdown('<div class="section-title">就业市场压力指标</div>', unsafe_allow_html=True)
    view = st.radio("就业指标视图", ["名义 vs 实际月薪", "受雇工作比例", "青年失业率"], horizontal=True, label_visibility="collapsed")

    if "月薪" in view:
        fig = go.Figure()
        nom = df["本科毕业半年月薪(元)"].values[em]
        real = df["实际月薪(2010年不变价,元)"].values[em]
        fig.add_trace(go.Bar(x=ym, y=nom, name="名义月薪", marker=dict(color=CYAN, opacity=0.45),
                              hovertemplate="名义: %{y:.0f} 元<extra></extra>"))
        fig.add_trace(go.Bar(x=ym, y=real, name="实际月薪 (2010 不变价)", marker=dict(color=ACCENT, opacity=0.85),
                              hovertemplate="实际: %{y:.0f} 元<extra></extra>"))
        fig.add_trace(go.Scatter(x=ym, y=nom, mode="lines", line=dict(color=CYAN, width=1, dash="dot"),
                                  showlegend=False, hoverinfo="skip"))
        fig.update_layout(**plotly_template("本科毕业半年月薪"))
        fig.update_yaxes(title="", showgrid=False, zeroline=False)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        gap = nom[-1] - real[-1]
        st.markdown(f'<div class="note-block"><p>2024 年通胀侵蚀约 {gap:.0f} 元。'
                    f'浅色为名义值，深色为剔除 CPI 影响后的实际购买力。</p></div>', unsafe_allow_html=True)

    elif "受雇" in view:
        fig = go.Figure()
        emp = df["受雇工作比例(%)"].values[em]
        fig.add_trace(go.Scatter(
            x=ym, y=emp, mode="lines+markers",
            line=dict(color=ORANGE, width=2.5), fill="tozeroy", fillcolor="rgba(210,153,29,0.08)",
            marker=dict(size=8, color=DARK_BG, line=dict(width=2, color=ORANGE)),
            name="受雇工作比例", hovertemplate="%{x} 年 · %{y:.1f}%<extra></extra>",
        ))
        fig.add_hline(y=emp.mean(), line_dash="dash", line_color=SLATE, line_width=1,
                      annotation_text=f"均值 {emp.mean():.1f}%", annotation_font_color=SLATE)
        fig.update_layout(**plotly_template("本科毕业生受雇工作比例"))
        fig.update_yaxes(title="", showgrid=False, zeroline=False)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown(f'<div class="note-block"><p>2010—2024 累计下降 {emp[0] - emp[-1]:.1f} 个百分点。'
                    f'就业吸纳能力的持续减弱是驱动考研热度上升的基础性经济因素。</p></div>', unsafe_allow_html=True)

    else:
        fig = go.Figure()
        unemp = df["16-24岁青年失业率(%)"].values[em]
        valid = ~np.isnan(unemp)
        fig.add_trace(go.Scatter(
            x=ym[valid], y=unemp[valid], mode="lines+markers",
            line=dict(color=RED, width=2.5, dash="dot"),
            marker=dict(size=10, color=DARK_BG, line=dict(width=2.5, color=RED)),
            name="青年失业率", hovertemplate="%{x} 年 · %{y:.1f}%<extra></extra>",
        ))
        fig.update_layout(**plotly_template("16—24 岁青年失业率 (仅有效年份)"))
        fig.update_yaxes(title="", showgrid=False, zeroline=False)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('<div class="note-block"><p>2010—2017 年数据缺失 (统计制度未建立)；'
                    '2023 年口径断裂 (6 月暂停 → 12 月恢复为"不含在校生"新口径)，无完整可比年度均值。</p></div>', unsafe_allow_html=True)

# ============================================================
# 页面 3 — 考公替代
# ============================================================
elif page == "考公替代":
    page_header("03", "两条赛道，一种安全感", "考研与考公共同承接年轻人的稳定性诉求；近年的此消彼长，正在释放更清晰的替代信号。")
    story_panel(
        "crossroads.png", "Choice Architecture", "当稳定成为稀缺品，竞争会在不同入口之间迁移",
        "考研和考公并非彼此独立的选择。两者都包含延迟就业、提升筛选优势与追求确定性的动机，因此一条赛道的降温，可能对应另一条赛道的升温。",
        ["关注报名趋势的背离", "同时比较人数与竞争强度"], "编辑插画 · 同一代人的多重选择"
    )
    st.markdown('<div class="section-title">考公与考研替代效应</div>', unsafe_allow_html=True)

    ky = df["报名人数(万)"].values[em]
    gk = df["报名过审人数(万)"].values[em]

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=ym, y=ky, name="考研报名", marker=dict(color=RED, opacity=0.5),
                          hovertemplate="考研: %{y:.0f} 万<extra></extra>"), secondary_y=False)
    fig.add_trace(go.Scatter(x=ym, y=gk, name="国考过审", mode="lines+markers",
                              line=dict(color=ACCENT, width=2.8),
                              marker=dict(size=8, color=DARK_BG, line=dict(width=2, color=ACCENT)),
                              hovertemplate="国考: %{y:.1f} 万<extra></extra>"), secondary_y=True)
    fig.update_layout(**plotly_template("考研报名 vs 国考过审 · 双轴对比"))
    fig.update_yaxes(title="", showgrid=False, zeroline=False, secondary_y=False)
    fig.update_yaxes(title="", showgrid=False, zeroline=False, secondary_y=True)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # 报录比
    fig2 = go.Figure()
    gk_ratio = df["报录比(X:1)"].values[em]
    bar_colors = ["#9bb4a0" if v < 60 else "#d5ad68" if v < 80 else "#d77963" for v in gk_ratio]
    fig2.add_trace(go.Bar(x=ym, y=gk_ratio, name="国考报录比", marker=dict(color=bar_colors, line=dict(width=0)),
                           hovertemplate="报录比: %{y:.0f}:1<extra></extra>"))
    fig2.update_layout(**plotly_template("国考报录比 · 过审 / 招录"))
    fig2.update_yaxes(title="", showgrid=False, zeroline=False)
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    st.markdown('<div class="note-block"><p>2023—2024 年考研报名首次同比转负，同期国考过审创历史新高——'
                '"此消彼长"的替代信号在近年最为显著。报录比色阶：绿 <60 · 黄 60—80 · 红 >80。</p></div>', unsafe_allow_html=True)
    pull_quote("竞争没有消失，它只是沿着人们对确定性的偏好，换了一个入口。")

# ============================================================
# 页面 4 — 招生结构
# ============================================================
elif page == "招生结构":
    page_header("04", "扩招之后，结构先变", "总量增长之外，专硕扩张与推免比例变化重新分配了招生机会，也重塑了统考竞争的真实体感。")
    story_panel(
        "employment-transition.png", "Inside Supply", "招生规模扩大，不代表每一种机会都同比增加",
        "专硕扩张改变了培养结构，推免增长则影响统考名额的可见供给。理解考研竞争，既要看总招生，也要追问新增名额流向了哪里。",
        ["区分学硕与专硕扩张", "拆分推免与统考名额"], "编辑插画 · 教育供给与职业出口的连接"
    )
    st.markdown('<div class="section-title">硕士招生结构变迁</div>', unsafe_allow_html=True)
    view = st.radio("招生结构视图", ["学硕 vs 专硕", "推免 vs 统考"], horizontal=True, label_visibility="collapsed")

    xs = df["学术硕士招生(万)"].values[em]
    zs = df["专业硕士招生(万)"].values[em]
    total = xs + zs
    baoyan = df["推免保研人数(万,估算)"].values[em]
    tongkao = total - baoyan

    if "学硕" in view:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=ym, y=xs, mode="lines", stackgroup="one", name="学术硕士",
                                  fillcolor="rgba(88,166,255,0.35)", line=dict(color=ACCENT, width=1),
                                  hovertemplate="学硕: %{y:.1f} 万<extra></extra>"))
        fig.add_trace(go.Scatter(x=ym, y=zs, mode="lines", stackgroup="one", name="专业硕士",
                                  fillcolor="rgba(210,153,29,0.4)", line=dict(color=ORANGE, width=1),
                                  hovertemplate="专硕: %{y:.1f} 万<extra></extra>"))
        fig.add_trace(go.Scatter(x=ym, y=total, mode="lines+markers", name="总招生",
                                  line=dict(color=WHITE, width=2), marker=dict(size=5, color=DARK_BG, line=dict(width=1.5, color=WHITE)),
                                  hovertemplate="总招生: %{y:.1f} 万<extra></extra>"))
        fig.add_vline(x=2020, line_dash="dash", line_color=RED, line_width=1.5, opacity=0.6)
        fig.update_layout(**plotly_template("学硕 vs 专硕 · 堆叠面积"))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=ym, y=tongkao, mode="lines", stackgroup="one", name="统考名额",
                                  fillcolor="rgba(57,211,83,0.4)", line=dict(color=GREEN, width=1),
                                  hovertemplate="统考: %{y:.1f} 万<extra></extra>"))
        fig.add_trace(go.Scatter(x=ym, y=baoyan, mode="lines", stackgroup="one", name="推免保研",
                                  fillcolor="rgba(163,113,247,0.35)", line=dict(color=PURPLE, width=1),
                                  hovertemplate="推免: %{y:.1f} 万<extra></extra>"))
        fig.add_trace(go.Scatter(x=ym, y=total, mode="lines+markers", name="总招生",
                                  line=dict(color=WHITE, width=2), marker=dict(size=5, color=DARK_BG, line=dict(width=1.5, color=WHITE)),
                                  hovertemplate="总招生: %{y:.1f} 万<extra></extra>"))
        fig.update_layout(**plotly_template("推免保研 vs 统考录取 · 堆叠面积"))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown('<div class="note-block"><p>虚线为 2020 年专硕扩招政策节点。专硕占比从 2010 年 23.3% 升至 2024 年 66.7%。'
                '推免数据为基于推免比例的估算值。</p></div>', unsafe_allow_html=True)

# ============================================================
# 页面 5 — 综合对比
# ============================================================
elif page == "综合对比":
    page_header("05", "把不同量纲，放进同一视野", "归一化不是为了抹平差异，而是让变量间的同向、背离与拐点更容易被看见。")
    story_panel(
        "future-paths.png", "Reading Relations", "单条曲线讲变化，多条曲线才开始讲关系",
        "将不同单位的变量压缩到同一尺度后，可以更直接地识别同步上升、镜像变化与结构性断点。这里关注的是关系形态，而不是归一化后的绝对高低。",
        ["同向变化提示正关联", "背离走势提示替代或挤压"], "编辑插画 · 多条路径从共同现实中展开"
    )
    st.markdown('<div class="section-title">多变量归一化叠合</div>', unsafe_allow_html=True)

    var_map = {
        "报名人数(万)": ("考研报名人数", RED),
        "读研比例(%)": ("读研比例", ACCENT),
        "实际月薪增长率": ("实际月薪增长率", GREEN),
        "受雇工作比例(%)": ("受雇工作比例", ORANGE),
        "报名过审人数(万)": ("国考过审人数", CYAN),
        "专硕占比(%)": ("专硕占比", GOLD),
    }
    selected = st.multiselect(
        "选择变量 (建议 3—5 个)",
        list(var_map.keys()), default=["报名人数(万)", "受雇工作比例(%)", "专硕占比(%)"],
        label_visibility="collapsed",
    )

    if selected:
        fig = go.Figure()
        for var in selected:
            label, color = var_map[var]
            if var == "实际月薪增长率":
                data = salary_growth[em]
            else:
                data = df[var].values[em]
            valid = ~np.isnan(data)
            d_min, d_max = data[valid].min(), data[valid].max()
            z = (data - d_min) / (d_max - d_min) if d_max > d_min else np.zeros_like(data)

            fig.add_trace(go.Scatter(
                x=ym, y=z, mode="lines", name=label,
                line=dict(color=color, width=2),
                hovertemplate=f"{label}: %{{y:.3f}}<extra></extra>",
            ))
        fig.add_vline(x=2020, line_dash="dot", line_color=SLATE, line_width=1, opacity=0.4)
        fig.update_layout(**plotly_template("所有变量经 Min-Max 归一化至 [0, 1]"))
        fig.update_yaxes(title="", range=[-0.05, 1.08], showgrid=False, zeroline=False)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('<div class="note-block"><p>消除量纲差异后，同向 / 反向关系一目了然。'
                    '受雇工作比例与报名人数的镜像反向关系 (r = −0.981) 是叠合图中最显著的结构特征。</p></div>', unsafe_allow_html=True)
    else:
        st.caption("请至少选择一个变量。")

# ============================================================
# 页面 6 — 情景模拟
# ============================================================
elif page == "情景模拟":
    page_header("06", "未来不是预测，是一组条件句", "从历史锚点出发，让就业、考公与综合治理沿不同方向展开，比较 2025—2030 年的可能路径。")
    story_panel(
        "future-paths.png", "Scenario Thinking", "情景的价值，不在押中未来，而在看清条件",
        "四条路径不是对年份与数值的断言，而是把关键机制分别推向不同方向：如果就业压力延续、考公分流增强，或治理措施开始生效，热度可能怎样响应？",
        ["比较路径之间的相对差异", "重点关注方向与政策敏感性"], "编辑插画 · 从同一锚点通往不同未来"
    )
    st.markdown('<div class="section-title">2025 — 2030 · PEEHI 情景模拟</div>', unsafe_allow_html=True)
    mode = st.radio("情景路径视图", ["全部路径", "仅基准 + 综合治理", "仅基准 + 就业 + 考公"], horizontal=True, label_visibility="collapsed")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=years, y=PEEHI, mode="lines+markers", name="历史 PEEHI",
                              line=dict(color=WHITE, width=3), marker=dict(size=6, color=DARK_BG, line=dict(width=2, color=WHITE)),
                              hovertemplate="%{x} 年 · %{y:.1f}<extra></extra>"))
    fig.add_vline(x=2024.4, line_dash="dash", line_color=SLATE, line_width=1.5)
    fig.add_annotation(x=2025, y=103, text="模拟期 →", showarrow=False, font=dict(size=10, color=SLATE))

    scenarios = [
        ("PEEHI_基准延续情景", "基准延续", CYAN),
        ("PEEHI_就业压力加剧情景", "就业加剧", RED),
        ("PEEHI_考公分流情景", "考公分流", PURPLE),
        ("PEEHI_综合治理降温情景", "综合治理", GOLD),
    ]
    for col, name, color in scenarios:
        show = True
        if "基准 + 综合治理" in mode: show = name in ("基准延续", "综合治理")
        elif "就业 + 考公" in mode: show = name != "综合治理"
        if show:
            fig.add_trace(go.Scatter(x=sim["年份"], y=sim[col], mode="lines+markers", name=name,
                                      line=dict(color=color, width=2, dash="dash"),
                                      marker=dict(size=6, color=DARK_BG, line=dict(width=1.5, color=color)),
                                      hovertemplate=f"%{{x}} · {name}: %{{y:.1f}}<extra></extra>"))

    fig.update_layout(**plotly_template("四种情景下的 PEEHI · 外推路径", 460))
    fig.update_yaxes(range=[0, 112], title="", showgrid=False, zeroline=False)
    fig.update_xaxes(range=[2009.5, 2030.5], dtick=2)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown('<div class="note-block"><p>以 2024 年真实 PEEHI (62.6) 为锚定点，基于 2020—2024 年均变化量线性外推。'
                'S1 和 S3 已接近 [0,100] 标准化上限，后续上升空间受限。这不是精确预测，而是探索性推演。</p></div>', unsafe_allow_html=True)
    pull_quote("未来不是一条等待被发现的线，而是一组会被政策与选择共同改写的路径。")
