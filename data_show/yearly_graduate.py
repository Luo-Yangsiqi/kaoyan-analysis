"""
全国普通本科应届毕业生总数（万人）数据采集 + 本科生国内读研比例计算
=====================================================================
数据来源：国家统计局年度数据 → 各教育数据聚合网站
目标年份：2010-2024
输出文件：本科毕业生数据.csv、读研比例.csv
"""

import requests, csv, sys, time, re, io, os
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# 修复 Windows GBK 终端的编码问题
# ---------------------------------------------------------------------------
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# 请求头
# ---------------------------------------------------------------------------
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

# 目标年份
TARGET_YEARS = set(range(2010, 2025))
res_data = {}  # {year: num_wan}

session = requests.Session()


# ===================================================================
# 工具函数
# ===================================================================

def fetch(url, name="", force_utf8=False):
    """请求页面，返回 (status_code, html_text)"""
    try:
        resp = session.get(url, headers=HEADERS, timeout=15)
        if force_utf8 or resp.apparent_encoding == "utf-8":
            resp.encoding = "utf-8"
        print(f"  响应: {resp.status_code} | {len(resp.text)} 字节 | 编码: {resp.encoding}")
        return resp.status_code, resp.text
    except Exception as e:
        print(f"  [失败] {e}")
        return 0, ""


def extract_num_from_text(text, year):
    """
    从文本中用正则提取「年份 + 普通本科毕业生数」。
    文本已去除换行符，用 .{m,n}? 跨句匹配。
    注意区分：普通本科毕业生 ≠ 普通高校毕业生（含专科）≠ 研究生毕业生
    """
    patterns = [
        # 最优：年份 + "普通本科" + "毕业生" + 数字 + 万
        # 例："2024年普通本科毕业生511.96万人"
        rf"{year}\s*年.{{0,150}}?普通本科.{{0,40}}?毕业生?.{{0,20}}?(\d+\.?\d*)\s*万",
        # 年份 + "本科" + "毕业" + 数字 + 万（更宽泛）
        rf"{year}\s*年.{{0,120}}?本科.{{0,20}}?毕业\s*生?.{{0,15}}?(\d+\.?\d*)\s*万",
        # "本科毕业生" + 数字 + 万 + 年份（倒序）
        rf"本科\s*毕业\s*生?.{{0,15}}?(\d+\.?\d*)\s*万.{{0,150}}?{year}\s*年",
        # 年份 + … + "本科" + 数字万（紧凑格式）
        rf"{year}\s*年.{{0,200}}?本科\s*(\d+\.?\d*)\s*万",
    ]

    for pat in patterns:
        m = re.search(pat, text)
        if m:
            val = float(m.group(1))
            # 普通本科毕业生合理范围：200–600万（2010 ≈ 259万 → 2024 ≈ 512万）
            if 200 < val < 600:
                ctx = m.group(0)
                # 校验：必须含"本科"，不能混入"研究生"毕业生数
                if "本科" not in ctx:
                    continue
                # 排除「研究生」毕业生统计
                if "研究生" in ctx:
                    continue
                return val, f"regex({ctx[:80]}...)"

    return None, ""


def parse_ticker_items(html, source_name):
    """
    从 HTML 中的 <span class="ticker-item"> 提取「年份 → 数值」。
    格式：<span class="ticker-item">2015年 2015 <strong>358.594</strong></span>
    常见于 macrodatas.cn 等数据面板站点。
    """
    found = {}
    pattern = re.compile(
        r'<span[^>]*ticker-item[^>]*?>.*?(\d{4})\D.*?<strong>(\d+\.?\d*)</strong>',
        re.DOTALL,
    )
    matches = pattern.findall(html)
    print(f"  ticker-item 匹配数: {len(matches)}")

    for year_str, val_str in matches:
        year = int(year_str)
        if year in TARGET_YEARS and year not in found:
            val = float(val_str)
            if 200 < val < 600:
                found[year] = val
    return found


def parse_timeline_divs(html, source_name):
    """
    从 HTML 中 <div class="tl-year"> / <div class="tl-val"> 提取数据。
    格式：<div class="tl-year">2015</div> <div class="tl-val">358.594</div>
    """
    found = {}
    soup = BeautifulSoup(html, "html.parser")
    year_els = soup.find_all("div", class_="tl-year")
    for el in year_els:
        year_text = el.get_text(strip=True)
        ym = re.search(r"(\d{4})", year_text)
        if not ym:
            continue
        year = int(ym.group(1))
        if year not in TARGET_YEARS or year in found:
            continue
        # 下一个兄弟元素应该是 tl-val
        val_el = el.find_next_sibling("div", class_="tl-val")
        if val_el:
            vm = re.search(r"(\d+\.?\d*)", val_el.get_text(strip=True))
            if vm:
                val = float(vm.group(1))
                if 200 < val < 600:
                    found[year] = val
    return found


def parse_html_table(html, source_name):
    """
    从 HTML 中找到 <table>，解析「年份 → 本科毕业生数」。
    识别包含"本科"和"毕业生"关键词的列。
    """
    found = {}
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table")
    print(f"  表格数: {len(tables)}")

    for table in tables:
        rows = table.find_all("tr")
        year_col = None
        grad_col = None

        for row in rows:
            cells = row.find_all(["td", "th"])
            texts = [c.get_text(strip=True) for c in cells]

            # 第一步：识别表头 → 确定「年份」列和「毕业生数」列的位置
            has_year_header = any("年份" in t or "年度" in t for t in texts)
            GRAD_KW = ["本科毕业生", "本科毕业", "毕业生数", "普通本科", "毕业人数", "毕业生"]
            has_grad_header = any(
                any(kw in t for kw in GRAD_KW) for t in texts
            )
            # 确保不是「研究生」列
            has_postgrad = any("研究生" in t for t in texts)

            if has_year_header and has_grad_header and not has_postgrad:
                for i, t in enumerate(texts):
                    if "年份" in t or "年度" in t:
                        year_col = i
                    elif any(kw in t for kw in GRAD_KW):
                        grad_col = i
                continue  # 表头行，跳过

            # 数据行：使用已识别的列位置
            if year_col is not None and grad_col is not None:
                if len(texts) > max(year_col, grad_col):
                    yt = texts[year_col]
                    gt = texts[grad_col]
                    ym = re.search(r"(20\d{2})", yt)
                    if ym:
                        year = int(ym.group(1))
                        if year in TARGET_YEARS and year not in found:
                            nm = re.search(
                                r"(\d+\.?\d*)", gt.replace("万", "").replace(",", "")
                            )
                            if nm:
                                val = float(nm.group(1))
                                # 合理范围：200–600万（纯本科）
                                if 200 < val < 600:
                                    found[year] = val
                continue

            # 回退策略：启发式扫描每对相邻单元格
            for i in range(len(texts)):
                ym = re.search(r"(20\d{2})", texts[i])
                if not ym:
                    continue
                year = int(ym.group(1))
                if year not in TARGET_YEARS or year in found:
                    continue

                # 在当前格及后续格中找毕业生人数
                for j in range(i, min(i + 4, len(texts))):
                    t = texts[j]
                    # 跳过增长率、百分比等
                    if t.endswith("%") or re.match(r"^[+\-－]\d", t):
                        continue
                    if t in ("—", "—", "-", "待公布", "", "--", "/"):
                        continue
                    nm = re.search(
                        r"(\d+\.?\d*)", t.replace("万", "").replace(",", "")
                    )
                    if nm:
                        val = float(nm.group(1))
                        # 纯本科毕业生范围 200-600万
                        if 200 < val < 600:
                            found[year] = val
                            break

    return found


# ===================================================================
# 数据源定义
# ===================================================================

TABLE_SOURCES = [
    {
        "url": "https://www.gotohui.com/edu/show-9717",
        "name": "gotohui-普通本科毕业生数 (1949-2022)",
        "note": "含 2010-2014 数据，2015+ 可能为空",
    },
    {
        "url": "https://s.macrodatas.cn/article/indicator/hg-eae13c2db84c275fb8c6d9d62f4f-putongbenkebiyeshengshu-a56c0a",
        "name": "macrodatas-普通本科毕业生面板数据 (1998-2024)",
        "note": "完整面板数据，整理自国家统计局",
    },
]

TEXT_SOURCES = [
    {
        "url": "https://s.macrodatas.cn/article/indicator/hg-eae13c2db84c275fb8c6d9d62f4f-putongbenkebiyeshengshu-a56c0a",
        "name": "macrodatas-文本提取",
        "force_utf8": True,
    },
]


# ===================================================================
# 主流程
# ===================================================================
print("=" * 70)
print("全国普通本科应届毕业生总数数据采集（2010–2024）")
print("数据来源：国家统计局年度数据 → 教育数据聚合网站")
print("=" * 70)

# ---- 阶段一：多方法解析（ticker-item → timeline-div → HTML table → text regex） ----
for src in TABLE_SOURCES:
    missing = TARGET_YEARS - set(res_data.keys())
    if not missing:
        break

    print(f"\n[数据源] {src['name']}")
    print(f"  URL: {src['url']}")
    print(f"  备注: {src.get('note', '')}")
    status, html = fetch(src["url"], force_utf8=src.get("force_utf8", False))
    if status != 200:
        continue

    # 方法1：ticker-item 格式（macrodatas.cn 等数据面板站点）
    found_ticker = parse_ticker_items(html, src["name"])
    new_years = missing & set(found_ticker.keys())
    for year in sorted(new_years):
        res_data[year] = found_ticker[year]
        print(f"  [OK-ticker] {year}年 -> {found_ticker[year]}万")

    # 方法2：timeline div 格式
    still_missing = TARGET_YEARS - set(res_data.keys())
    if still_missing:
        found_timeline = parse_timeline_divs(html, src["name"])
        new_years = still_missing & set(found_timeline.keys())
        for year in sorted(new_years):
            res_data[year] = found_timeline[year]
            print(f"  [OK-timeline] {year}年 -> {found_timeline[year]}万")

    # 方法3：标准 HTML 表格
    still_missing = TARGET_YEARS - set(res_data.keys())
    if still_missing:
        found_table = parse_html_table(html, src["name"])
        new_years = still_missing & set(found_table.keys())
        for year in sorted(new_years):
            res_data[year] = found_table[year]
            print(f"  [OK-table] {year}年 -> {found_table[year]}万")

    still_missing = TARGET_YEARS - set(res_data.keys())
    if still_missing:
        print(f"  该源未覆盖: {sorted(still_missing)}")

    time.sleep(2)

# ---- 阶段二：文本正则提取（补充缺失年份） ----
for src in TEXT_SOURCES:
    missing = TARGET_YEARS - set(res_data.keys())
    if not missing:
        break

    print(f"\n[文本源] {src['name']}")
    print(f"  URL: {src['url']}")
    status, html = fetch(src["url"], force_utf8=src.get("force_utf8", False))
    if status != 200:
        continue

    # 用 BeautifulSoup 提取正文（去掉 script/style/nav/footer）
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    text = soup.get_text()
    # 合并空白字符，保留中文语境
    text = re.sub(r"\s+", "", text)
    print(f"  正文长度: {len(text)} 字符")

    for year in sorted(missing):
        if str(year) not in text and f"{year}年" not in text:
            continue

        num, desc = extract_num_from_text(text, year)
        if num:
            res_data[year] = num
            print(f"  [OK] {year}年 -> {num}万  [{desc}]")

    still_missing = TARGET_YEARS - set(res_data.keys())
    if still_missing:
        print(f"  该源未覆盖: {sorted(still_missing)}")

    time.sleep(2)


# ===================================================================
# 结果汇总与保存 — 本科毕业生数据
# ===================================================================
sorted_data = sorted(res_data.items(), key=lambda x: x[0])

out_file = "本科毕业生数据.csv"
with open(out_file, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["年份", "普通本科毕业生数(万)"])
    w.writerows(sorted_data)

print(f"\n{'=' * 70}")
missing_final = TARGET_YEARS - set(res_data.keys())
print(f"本科毕业生数据采集结果: {len(sorted_data)}/{len(TARGET_YEARS)} 条记录")
if missing_final:
    print(f"⚠ 缺失年份: {sorted(missing_final)}")
print(f"数据文件: {out_file}")

if sorted_data:
    print("\n数据预览：")
    print("-" * 50)
    print(f"{'年份':<8}{'普通本科毕业生数(万)':<22}")
    print("-" * 50)
    for year, num in sorted_data:
        print(f"{year:<8}{num:<22.4f}")
    print("-" * 50)


# ===================================================================
# 计算本科生国内读研比例
# ===================================================================
print(f"\n{'=' * 70}")
print("计算本科生国内读研比例")
print("公式: 读研比例(%) = 硕士实际录取人数 / 普通本科毕业生数 × 100%")
print("=" * 70)

# 读取硕士录取数据
master_file = "硕士录取数据.csv"
if not os.path.exists(master_file):
    print(f"⚠ 找不到 {master_file}，跳过读研比例计算")
    print("  请先运行 sucess.py 获取硕士录取数据")
else:
    master_data = {}
    with open(master_file, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            year = int(row["年份"])
            if year in TARGET_YEARS:
                master_data[year] = float(row["硕士实际录取人数(万)"])

    # 合并计算
    ratio_data = []
    common_years = sorted(set(res_data.keys()) & set(master_data.keys()))

    print(f"\n{'年份':<6} {'本科毕业生(万)':<16} {'硕士录取(万)':<14} {'读研比例(%)':<12}")
    print("-" * 60)

    for year in common_years:
        grad = res_data[year]
        master = master_data[year]
        ratio = (master / grad) * 100
        ratio_data.append([year, grad, master, round(ratio, 2)])
        print(f"{year:<6} {grad:<16.4f} {master:<14.2f} {ratio:<12.2f}%")

    print("-" * 60)

    if ratio_data:
        ratios = [r[3] for r in ratio_data]
        print(f"\n读研比例统计：")
        print(f"  均值: {sum(ratios)/len(ratios):.2f}%")
        print(f"  最低: {min(ratios):.2f}% ({common_years[ratios.index(min(ratios))]}年)")
        print(f"  最高: {max(ratios):.2f}% ({common_years[ratios.index(max(ratios))]}年)")
        print(f"  2024年: {ratios[-1]:.2f}%")

    # 保存读研比例数据
    ratio_file = "读研比例.csv"
    with open(ratio_file, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["年份", "普通本科毕业生数(万)", "硕士实际录取人数(万)", "读研比例(%)"])
        w.writerows(ratio_data)
    print(f"\n读研比例数据已保存至: {ratio_file}")

    # 展示哪些年份缺毕业生数据
    missing_for_ratio = set(master_data.keys()) - set(res_data.keys())
    if missing_for_ratio:
        print(f"⚠ 以下年份有硕士录取数据但缺本科毕业生数据: {sorted(missing_for_ratio)}")

print(f"\n{'=' * 70}")
print("全部任务完成！")
print(f"  1. {out_file}      — 普通本科毕业生数")
if os.path.exists(master_file):
    print(f"  2. 读研比例.csv       — 本科生国内读研比例")
print("=" * 70)
