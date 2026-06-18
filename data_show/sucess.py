import requests, csv, sys, time, re, io
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
res_data = {}

session = requests.Session()


# ===================================================================
# 工具函数
# ===================================================================

def fetch(url, name="", force_utf8=False):
    """请求页面，返回 (status, text) 或 (0, '')"""
    try:
        resp = session.get(url, headers=HEADERS, timeout=15)
        # 修复部分网站返回 ISO-8859-1 但实际是 UTF-8 的编码问题
        if force_utf8 or resp.apparent_encoding == "utf-8":
            resp.encoding = "utf-8"
        print(f"  响应: {resp.status_code} | {len(resp.text)} 字节 | 编码: {resp.encoding}")
        return resp.status_code, resp.text
    except Exception as e:
        print(f"  [失败] {e}")
        return 0, ""


def extract_num_from_text(text, year, label_hint=""):
    """
    从文本中用正则提取「年份 + 硕士录取/招生人数」。
    注意区分：研究生总招生数（含博士） vs 纯硕士招生数。
    文本已去除换行符，用 .{m,n}? 跨句匹配（允许穿越 。）。
    """
    patterns = [
        # 最优：年份 + … + "硕士生" + 数字 + 万
        # 例："2024年…硕士生118.57万人"
        rf"{year}\s*年.{{0,250}}?硕士生\s*(\d+\.?\d*)\s*万",
        # 次优：年份 + … + "招收硕士" + 数字 + 万
        rf"{year}\s*年.{{0,200}}?招收硕士.{{0,30}}?(\d+\.?\d*)\s*万",
        # 数字 + "万" + … + "硕士" + … + 年份（倒序匹配）
        rf"硕士生?\s*(\d+\.?\d*)\s*万.{{0,250}}?{year}\s*年",
        # 录取/招生 数字 万 … 年份
        rf"(?:录取|招生)\s*(\d+\.?\d*)\s*万.{{0,200}}?{year}\s*年",
    ]

    for pat in patterns:
        m = re.search(pat, text)
        if m:
            val = float(m.group(1))
            # 硕士录取人数合理范围：20–130万（135+ 通常是研究生总数含博士）
            if 20 < val < 130:
                # 校验：匹配上下文必须含 "硕士"，不能仅有 "研究生"（总数）
                ctx = m.group(0)
                if "研究生" in ctx and "硕士" not in ctx:
                    continue
                return val, f"regex({m.group(0)[:80]}...)"

    return None, ""


def parse_html_table(html, source_name, col_label):
    """
    从 HTML 中找到 <table>，解析「年份 → 录取人数」。
    col_label: 列名关键字，如 '录取人数' 或 '录取'.
    """
    found = {}
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table")
    print(f"  表格数: {len(tables)}")

    for table in tables:
        rows = table.find_all("tr")

        # 第一步：识别表头 → 确定「年份」列和「录取人数」列的位置
        year_col = None
        enroll_col = None
        header_texts = []

        for row in rows:
            cells = row.find_all(["td", "th"])
            texts = [c.get_text(strip=True) for c in cells]

            # 检查是否表头行
            has_year_header = any("年份" in t for t in texts)
            has_enroll_header = any(
                col_label in t or "录取" in t or "招生" in t for t in texts
            )
            has_reg_header = any("报名" in t for t in texts)

            if has_year_header:
                for i, t in enumerate(texts):
                    if "年份" in t:
                        year_col = i
                    elif col_label in t or "录取" in t or ("招生" in t and "报名" not in t):
                        enroll_col = i
                header_texts = texts
                continue  # 跳过表头行本身

            # 数据行
            if year_col is not None and enroll_col is not None:
                # 按列位置提取
                if len(texts) > max(year_col, enroll_col):
                    yt = texts[year_col]
                    et = texts[enroll_col]
                    ym = re.search(r"(20\d{2})", yt)
                    if ym:
                        year = int(ym.group(1))
                        if year in TARGET_YEARS:
                            nm = re.search(r"(\d+\.?\d*)", et.replace("万", ""))
                            if nm:
                                val = float(nm.group(1))
                                if 20 < val < 150:
                                    found[year] = val
                continue

            # 未识别表头时，按内容启发式解析
            # （回退策略：遍历每对相邻单元格）
            for i in range(len(texts)):
                ym = re.search(r"(20\d{2})", texts[i])
                if not ym:
                    continue
                year = int(ym.group(1))
                if year not in TARGET_YEARS:
                    continue

                # 在当前格及后续格中找录取人数
                for j in range(i, min(i + 4, len(texts))):
                    t = texts[j]
                    # 跳过增长率、录取率等
                    if t.endswith("%") or re.match(r"^[+\-－]\d", t):
                        continue
                    pct_m = re.match(r"^(\d+\.?\d*)\s*%$", t)
                    if pct_m and float(pct_m.group(1)) < 50:
                        continue
                    # 跳过 "—" "待公布" 等
                    if t in ("—", "—", "-", "待公布", "", "--", "/"):
                        continue
                    nm = re.search(r"(\d+\.?\d*)", t.replace("万", "").replace("（拟招生）", ""))
                    if nm:
                        val = float(nm.group(1))
                        if 20 < val < 150:
                            found[year] = val
                            break

    return found


# ===================================================================
# 数据源定义
# ===================================================================
TABLE_SOURCES = [
    {
        # 来源 1：中国考研网 2011-2023（录取人数到 2022，2023 空缺）
        "url": "https://www.chinakaoyan.com/info/article/id/378907.shtml",
        "name": "中国考研网 (2011-2023)",
        "type": "table",
        "col_label": "录取人数",
    },
    {
        # 来源 2：中国考研网 2005-2022（含 2010，作为来源 1 的补充）
        "url": "http://www.chinakaoyan.com/info/article/id/102013.shtml",
        "name": "中国考研网 (2005-2022)",
        "type": "table",
        "col_label": "录取人数",
    },
]

TEXT_SOURCES = [
    {
        # 来源 3：红网转载教育部 2023 年数据
        "url": "https://edu.rednet.cn/content/646847/83/13587048.html",
        "name": "红网 (2023年教育部数据)",
        "force_utf8": False,
    },
    {
        # 来源 4：中国教育在线 2024 年统计公报（编码需强制 UTF-8）
        "url": "https://www.eol.cn/news/yaowen/202506/t20250611_2674061.shtml",
        "name": "中国教育在线 (2024年统计公报)",
        "force_utf8": True,
    },
]


# ===================================================================
# 主流程
# ===================================================================
print("=" * 60)
print("硕士实际录取人数数据采集（2010–2024）")
print("=" * 60)

# ---- 阶段一：HTML 表格解析 ----
for src in TABLE_SOURCES:
    missing = TARGET_YEARS - set(res_data.keys())
    if not missing:
        break

    print(f"\n[表格源] {src['name']}")
    print(f"  URL: {src['url']}")
    status, html = fetch(src["url"])
    if status != 200:
        continue

    found = parse_html_table(html, src["name"], src["col_label"])

    new_years = missing & set(found.keys())
    for year in sorted(new_years):
        res_data[year] = found[year]
        print(f"  [OK] {year}年 -> {found[year]}万")

    still_missing = TARGET_YEARS - set(res_data.keys())
    if still_missing:
        print(f"  未覆盖: {sorted(still_missing)}")

    time.sleep(2)

# ---- 阶段二：文本正则提取（2023、2024） ----
for src in TEXT_SOURCES:
    missing = TARGET_YEARS - set(res_data.keys())
    if not missing:
        break

    print(f"\n[文本源] {src['name']}")
    print(f"  URL: {src['url']}")
    status, html = fetch(src["url"], force_utf8=src.get("force_utf8", False))
    if status != 200:
        continue

    # 用 BeautifulSoup 提取正文（去掉 script/style）
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    text = soup.get_text()
    # 合并空白
    text = re.sub(r"\s+", "", text)

    for year in sorted(missing):
        # 先检查该年份是否在页面中提到
        if str(year) not in text and f"{year}年" not in text:
            continue

        num, desc = extract_num_from_text(text, year)
        if num:
            res_data[year] = num
            print(f"  [OK] {year}年 -> {num}万  [{desc}]")

    still_missing = TARGET_YEARS - set(res_data.keys())
    if still_missing:
        print(f"  未覆盖: {sorted(still_missing)}")

    time.sleep(2)

# ===================================================================
# 结果汇总与保存
# ===================================================================
sorted_data = sorted(res_data.items(), key=lambda x: x[0])

out_file = "硕士录取数据.csv"
with open(out_file, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["年份", "硕士实际录取人数(万)"])
    w.writerows(sorted_data)

print(f"\n{'=' * 60}")
missing_final = TARGET_YEARS - set(res_data.keys())
print(f"成功获取: {len(sorted_data)}/{len(TARGET_YEARS)} 条记录")
if missing_final:
    print(f"缺失年份: {sorted(missing_final)}")
print(f"数据文件: {out_file}")

if sorted_data:
    print("\n数据预览：")
    print("-" * 40)
    print(f"{'年份':<8}{'硕士录取人数(万)':<18}")
    print("-" * 40)
    for year, num in sorted_data:
        print(f"{year:<8}{num:<18}")
    print("-" * 40)
