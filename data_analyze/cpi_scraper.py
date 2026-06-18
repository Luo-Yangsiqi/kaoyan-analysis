"""
CPI 居民消费价格指数采集 + 实际工资平减
========================================
爬取 2010-2024 年全国年度 CPI（上年=100），
并用 CPI 对本科毕业半年月薪（名义工资）进行平减，得到实际工资。

数据来源：国家统计局 → 数据聚合网站
"""

import requests, csv, sys, time, re, io, os
from bs4 import BeautifulSoup

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

TARGET_YEARS = set(range(2010, 2025))
session = requests.Session()
cpi_data = {}


def fetch(url):
    try:
        resp = session.get(url, headers=HEADERS, timeout=15)
        if resp.apparent_encoding == "utf-8":
            resp.encoding = "utf-8"
        print(f"  响应: {resp.status_code} | {len(resp.text)} 字节")
        return resp.status_code, resp.text
    except Exception as e:
        print(f"  [失败] {e}")
        return 0, ""


# ================================================================
# 阶段一：爬取 CPI 数据
# ================================================================
print("=" * 60)
print("CPI 居民消费价格指数采集（2010-2024）")
print("=" * 60)

SOURCES = [
    {
        "url": "https://m.gotohui.com/ndata/show-1396757",
        "name": "gotohui-CPI年度数据",
    },
    {
        "url": "https://s.macrodatas.cn/article/indicator/hg-eae13c2bb3ce101a3b1a7-juminxiaofeijiagezhishu1978100-5243f3",
        "name": "macrodatas-CPI面板数据",
    },
]

for src in SOURCES:
    missing = TARGET_YEARS - set(cpi_data.keys())
    if not missing:
        break

    print(f"\n[数据源] {src['name']}")
    print(f"  URL: {src['url']}")
    status, html = fetch(src["url"])
    if status != 200:
        continue

    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()
    text = soup.get_text()
    text = re.sub(r"\s+", "", text)

    for year in sorted(missing):
        patterns = [
            rf"{year}\s*年?[^0-9]*?CPI[^0-9]*?(\d{{3}}\.?\d*)",
            rf"{year}\s*年?[^0-9]*?居民消费价格[^0-9]*?(\d{{3}}\.?\d*)",
            rf"{year}\s*年?[^0-9]*?(\d{{3}}\.?\d*)[^0-9]*?CPI",
            rf"(\d{{3}}\.?\d*)[^0-9]*?{year}\s*年?[^0-9]*?CPI",
            rf"{year}\s*年?[^0-9]*?(\d{{3}}\.?\d*)",  # 模糊匹配
        ]
        for pat in patterns:
            m = re.search(pat, text)
            if m:
                val = float(m.group(1))
                # CPI 上年=100，合理范围 98-108
                if 98 < val < 108:
                    cpi_data[year] = val
                    print(f"  [OK] {year}年 CPI -> {val}")
                    break

        # 也试试 ticker-item 格式（macrodatas.cn）
        if year not in cpi_data:
            ticker_pat = re.compile(
                rf'<span[^>]*ticker-item[^>]*?>.*?{year}.*?<strong>(\d+\.?\d*)</strong>',
                re.DOTALL,
            )
            tm = ticker_pat.search(html)
            if tm:
                val = float(tm.group(1))
                if 98 < val < 108:
                    cpi_data[year] = val
                    print(f"  [OK-ticker] {year}年 CPI -> {val}")

    time.sleep(1.5)


# ---- 兜底：国家统计局官方数据 ----
VERIFIED_CPI = {
    2010: 103.3,
    2011: 105.4,
    2012: 102.6,
    2013: 102.6,
    2014: 102.0,
    2015: 101.4,
    2016: 102.0,
    2017: 101.6,
    2018: 102.1,
    2019: 102.9,
    2020: 102.5,
    2021: 100.9,
    2022: 102.0,
    2023: 100.2,
    2024: 100.2,
}

for year, val in VERIFIED_CPI.items():
    if year in cpi_data:
        # 校验：CPI 上年=100，值域 99-108；整100 通常为定基指数错配
        if cpi_data[year] == 100.0 or abs(cpi_data[year] - val) > 3:
            print(f"  [校验拒绝] {year}年 爬取值{cpi_data[year]} 不合理，改用验证值{val}")
            cpi_data[year] = val
    else:
        cpi_data[year] = val
        print(f"  [兜底] {year}年 CPI -> {val}（国家统计局）")


# ================================================================
# 阶段二：计算平减指数 & 实际工资
# ================================================================
print(f"\n{'=' * 60}")
print("工资平减：名义工资 → 实际工资（以 2010 年为基期）")
print("=" * 60)

# 以 2010 年为基期，构建累计 CPI 平减指数
cpi_sorted = sorted(cpi_data.items())

# 定基 CPI：2010 = 1.00
cum_cpi = {}
base_idx = 1.0
for year, _ in cpi_sorted:
    cum_cpi[year] = base_idx
    if year + 1 <= 2024:  # 下一年的累计 CPI = 当前累计 × 下一年 CPI / 100
        base_idx *= cpi_data.get(year + 1, 100) / 100

# 注：更准确的方式是 forward chaining
# 2010 = 1.00
# 2011 = 1.00 * (CPI_2011/100)
# 2012 = cum_2011 * (CPI_2012/100) ...
cum = {}
chain = 1.0
for year in range(2010, 2025):
    if year == 2010:
        cum[year] = 1.0
    else:
        chain *= cpi_data[year] / 100
        cum[year] = chain

# 读取名义工资 — 从上级目录的 data_collect_visual/ 读取
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)

salary_nominal = {}
possible_paths = [
    os.path.join(project_dir, "data_collect_visual", "就业市场指标.csv"),
    os.path.join(project_dir, "就业市场指标.csv"),
    "就业市场指标.csv",
]
salary_file = None
for p in possible_paths:
    if os.path.exists(p):
        salary_file = p
        break

if salary_file:
    with open(salary_file, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            year = int(row["年份"])
            if year in TARGET_YEARS and row["本科毕业半年月薪(元)"]:
                salary_nominal[year] = float(row["本科毕业半年月薪(元)"])
    print(f"已加载名义工资: {salary_file}")
else:
    print(f"[WARN] 找不到 就业市场指标.csv")

# 合并输出
print(f"\n{'年份':<6} {'CPI(上年=100)':<15} {'累计平减指数':<12} {'名义月薪(元)':<14} {'实际月薪(元)':<14}")
print("-" * 65)
results = []
for year in sorted(TARGET_YEARS):
    cpi = cpi_data.get(year)
    deflator = cum.get(year, 1.0)
    nominal = salary_nominal.get(year)
    real = round(nominal / deflator, 0) if nominal else None

    results.append([year, cpi, round(deflator, 4), nominal, real])

    cpi_str = f"{cpi:.1f}" if cpi else "—"
    deflator_str = f"{deflator:.4f}" if deflator else "—"
    nom_str = f"{nominal:.0f}" if nominal else "—"
    real_str = f"{real:.0f}" if real else "—"
    print(f"{year:<6} {cpi_str:<15} {deflator_str:<12} {nom_str:<14} {real_str:<14}")


# ================================================================
# 保存
# ================================================================
out_file = os.path.join(script_dir, "CPI及实际工资.csv")
with open(out_file, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["年份", "CPI(上年=100)", "累计平减指数(2010=1)", "名义月薪(元)", "实际月薪(2010年不变价,元)"])
    w.writerows(results)

print(f"\n已保存: {out_file}")
print("""
说明：
  - CPI 以上年=100 表示，如 103.3 表示同比上涨 3.3%
  - 累计平减指数以 2010 年为基期（2010=1.0000）
  - 实际月薪 = 名义月薪 / 累计平减指数
  - 即：剔除了通货膨胀影响后的真实购买力
""")
