import requests, csv, sys, time, re, io
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# 修复 Windows GBK 终端的编码问题
# ---------------------------------------------------------------------------
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# 请求头
# ---------------------------------------------------------------------------
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

# ---------------------------------------------------------------------------
# 数据来源 — 已知包含历年考研报名人数表格的页面
# ---------------------------------------------------------------------------
SOURCES = [
    {
        "url": "https://news.koolearn.com/20240809/1262886.html",
        "name": "新东方在线",
    },
    {
        "url": "https://mtoutiao.xdf.cn/kaoyan/202511/15001248.html",
        "name": "新东方网",
    },
    {
        "url": "https://m.educity.cn/mba/5355480.html",
        "name": "教育网",
    },
]

# 目标年份
TARGET_YEARS = set(range(2010, 2026))
res_data = []

session = requests.Session()


def parse_table_for_data(soup, source_name):
    """
    从 BeautifulSoup 对象中找到所有 <table>，
    解析包含"年份"和"报名人数"的行，返回 {year: num} 字典。
    """
    found = {}
    tables = soup.find_all("table")
    print(f"  找到 {len(tables)} 个表格")

    for ti, table in enumerate(tables):
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all(["td", "th"])
            if len(cells) < 2:
                continue

            # 提取所有单元格的纯文本
            texts = [cell.get_text(strip=True) for cell in cells]

            # 遍历每对相邻单元格，尝试匹配「年份 + 人数」
            for i in range(len(texts) - 1):
                year_str = texts[i].replace("年", "").strip()
                num_str = texts[i + 1].replace("万", "").strip()

                # 也尝试从纯数字字符串中提取（有些表格年份和人数不在相邻列）
                year_match = re.search(r"(20\d{2})", texts[i])
                num_match = re.search(r"(\d+\.?\d*)\s*万?", texts[i])
                # 如果当前格同时有年份和人数（合并格式）
                if year_match and num_match:
                    y = int(year_match.group(1))
                    n = float(num_match.group(1))
                    if y in TARGET_YEARS and 50 < n < 600:
                        found[y] = n
                        continue

                # 标准格式：年份在前，人数在后
                try:
                    year = int(year_str)
                    if year < 2000 or year > 2030:
                        continue
                except ValueError:
                    continue

                try:
                    num = float(num_str)
                except ValueError:
                    continue

                # 合理范围过滤
                if 50 < num < 600 and year in TARGET_YEARS:
                    found[year] = num

    return found


# ===================================================================
# 主流程
# ===================================================================
print("=" * 60)
print("考研报名人数数据采集（2010–2024）")
print("策略：直接解析已知数据页面的 HTML 表格")
print("=" * 60)

for source in SOURCES:
    missing = TARGET_YEARS - {row[0] for row in res_data}
    if not missing:
        break

    print(f"\n尝试数据源：{source['name']}")
    print(f"  URL: {source['url']}")

    try:
        resp = session.get(source["url"], headers=headers, timeout=15)
        print(f"  响应状态: {resp.status_code} | 大小: {len(resp.text)} 字节")

        if resp.status_code != 200:
            print(f"  跳过（状态码 {resp.status_code}）")
            continue

        soup = BeautifulSoup(resp.text, "html.parser")
        found = parse_table_for_data(soup, source["name"])

        for year in sorted(missing & set(found.keys())):
            res_data.append([year, found[year]])
            print(f"  ✓ {year}年 → {found[year]}万")
            missing.discard(year)

        if missing:
            print(f"  该数据源未覆盖的年份: {sorted(missing)}")

    except requests.exceptions.RequestException as e:
        print(f"  ✗ 请求异常: {e}")
        continue
    except Exception as e:
        print(f"  ✗ 解析异常: {e}")
        continue

    # 请求间隔
    time.sleep(2)

# ===================================================================
# 结果汇总与保存
# ===================================================================
res_data.sort(key=lambda x: x[0])

out_file = "考研报名数据.csv"
with open(out_file, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["年份", "报名人数(万)"])
    w.writerows(res_data)

print(f"\n{'=' * 60}")
missing_final = TARGET_YEARS - {row[0] for row in res_data}
print(f"成功获取: {len(res_data)}/{len(TARGET_YEARS)} 条记录")
if missing_final:
    print(f"缺失年份: {sorted(missing_final)}")
print(f"数据文件: {out_file}")

if res_data:
    print("\n数据预览：")
    print("-" * 30)
    print(f"{'年份':<8}{'报名人数(万)':<15}")
    print("-" * 30)
    for year, num in res_data:
        print(f"{year:<8}{num:<15}")
    print("-" * 30)
