# gen_a22_round1.py - 生成 A22 Round 01 经营驾驶舱
import json, os, csv

SUITE_ROOT = os.environ.get("SNAPSHOT_TASK_ROOT", ".")
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "run-20261016")
OUTPUT_ROOT = os.path.join(SUITE_ROOT, "outputs", RUN_ID, "A22")
TEMP_DIR = os.path.join(SUITE_ROOT, "tmp", RUN_ID, "A22")
SERVICE_URL = "https://open-snapshot.muedsa.com/snapshot"
FONT = "Noto Sans CJK SC,Inter"

# 读取 CSV
csv_path = os.path.join(SUITE_ROOT, "tasks", "A22-staged-data-correction", "inputs", "monthly.csv")
rows = []
with open(csv_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append({
            "month": r["month"],
            "orders": int(r["orders"]),
            "gross_revenue": int(r["gross_revenue"]),
            "refund_amount": int(r["refund_amount"]),
            "operating_cost": int(r["operating_cost"]),
            "sessions": int(r["sessions"]),
        })

# 计算每月指标
for r in rows:
    r["net_revenue"] = r["gross_revenue"] - r["refund_amount"]
    r["profit"] = r["net_revenue"] - r["operating_cost"]
    r["refund_rate"] = r["refund_amount"] / r["gross_revenue"] if r["gross_revenue"] > 0 else 0
    r["conv_rate"] = r["orders"] / r["sessions"] if r["sessions"] > 0 else 0

# 汇总
total_net = sum(r["net_revenue"] for r in rows)
total_profit = sum(r["profit"] for r in rows)
total_orders = sum(r["orders"] for r in rows)
total_sessions = sum(r["sessions"] for r in rows)
total_conv = total_orders / total_sessions if total_sessions > 0 else 0

def fmt_amount(v):
    if v >= 10000:
        return str(round(v/10000, 2)) + "万元"
    return str(round(v)) + "元"

def fmt_pct(v):
    return str(round(v*100, 2)) + "%"

# 设计令牌
DESIGN_TOKENS = {
    "primary": "#2563EB",
    "bg": "#FFFFFF",
    "title": "#111827",
    "body": "#64748B",
    "kpi_bg": "#F8FAFC",
    "kpi_border": "#E2E8F0",
    "net_color": "#2563EB",
    "profit_color": "#10B981",
    "table_header_bg": "#F1F5F9",
    "table_row_bg": "#FFFFFF",
    "table_border": "#CBD5E1"
}

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def gen_dashboard(W, H, rows, totals, tokens):
    lines = []
    lines.append('<Snapshot type="png">')
    lines.append('  <SizedBox width="' + str(W) + '" height="' + str(H) + '">')
    lines.append('    <Stack alignment="TOP_LEFT">')
    lines.append('      <Container color="' + tokens["bg"] + '" width="' + str(W) + '" height="' + str(H) + '"/>')

    # 标题
    lines.append('      <Text left="40" top="30" fontSize="24" fontStyle="BOLD" fill="' + tokens["title"] + '" fontFamily="' + FONT + '">经营驾驶舱 — 2026-04 至 2026-09</Text>')
    lines.append('      <Text left="40" top="60" fontSize="18" fill="' + tokens["body"] + '" fontFamily="' + FONT + '">四KPI · 净收入/利润柱图 · 月度明细表</Text>')

    # 四KPI卡片 (y=100, 4个卡片)
    kpi_y = 100
    kpi_h = 70
    kpi_w = 360
    gap = 20
    kpis = [
        ("总净收入", fmt_amount(totals["net"]), tokens["net_color"]),
        ("总经营利润", fmt_amount(totals["profit"]), tokens["profit_color"]),
        ("总订单", str(totals["orders"]) + " 笔", tokens["primary"]),
        ("总体转化率", fmt_pct(totals["conv"]), tokens["primary"]),
    ]
    for i, (label, value, color) in enumerate(kpis):
        kx = 40 + i * (kpi_w + gap)
        lines.append('      <Container color="' + tokens["kpi_bg"] + '" border="1 SOLID ' + tokens["kpi_border"] + '" borderRadius="8" left="' + str(kx) + '" top="' + str(kpi_y) + '" width="' + str(kpi_w) + '" height="' + str(kpi_h) + '"/>')
        lines.append('      <Text left="' + str(kx+16) + '" top="' + str(kpi_y+14) + '" fontSize="16" fill="' + tokens["body"] + '" fontFamily="' + FONT + '">' + esc(label) + '</Text>')
        lines.append('      <Text left="' + str(kx+16) + '" top="' + str(kpi_y+36) + '" fontSize="22" fontStyle="BOLD" fill="' + color + '" fontFamily="' + FONT + '">' + esc(value) + '</Text>')

    # 柱图区域 (y=200, 左侧)
    chart_x = 40
    chart_y = 200
    chart_w = 700
    chart_h = 420
    lines.append('      <Container color="#FFFFFF" border="1 SOLID ' + tokens["table_border"] + '" borderRadius="6" left="' + str(chart_x) + '" top="' + str(chart_y) + '" width="' + str(chart_w) + '" height="' + str(chart_h) + '"/>')
    lines.append('      <Text left="' + str(chart_x+16) + '" top="' + str(chart_y+14) + '" fontSize="18" fontStyle="BOLD" fill="' + tokens["title"] + '" fontFamily="' + FONT + '">净收入 / 经营利润 (元)</Text>')

    # 计算柱图数据
    max_val = max(max(r["net_revenue"], r["profit"]) for r in rows)
    chart_bottom = chart_y + chart_h - 60  # 留空间给X轴标签
    chart_top = chart_y + 50

    bar_w = 60
    bar_gap = 40
    total_bar_w = len(rows) * bar_w + (len(rows)-1) * bar_gap
    start_x = chart_x + (chart_w - total_bar_w) // 2

    for i, r in enumerate(rows):
        bx = start_x + i * (bar_w + bar_gap)
        # 净收入柱 (蓝色)
        net_h = int((r["net_revenue"] / max_val) * (chart_bottom - chart_top))
        lines.append('      <Container color="' + tokens["net_color"] + '" left="' + str(bx) + '" top="' + str(chart_bottom - net_h) + '" width="' + str(bar_w//2 - 2) + '" height="' + str(net_h) + '"/>')
        # 利润柱 (绿色)
        prof_h = int((r["profit"] / max_val) * (chart_bottom - chart_top))
        lines.append('      <Container color="' + tokens["profit_color"] + '" left="' + str(bx + bar_w//2 + 2) + '" top="' + str(chart_bottom - prof_h) + '" width="' + str(bar_w//2 - 2) + '" height="' + str(prof_h) + '"/>')
        # 月份标签
        lines.append('      <Text left="' + str(bx-10) + '" top="' + str(chart_bottom+8) + '" fontSize="14" fill="' + tokens["body"] + '" fontFamily="' + FONT + '">' + esc(r["month"][5:]) + '</Text>')

    # 表格区域 (右侧)
    table_x = 780
    table_y = 200
    table_w = 780
    table_h = 420
    lines.append('      <Container color="#FFFFFF" border="1 SOLID ' + tokens["table_border"] + '" borderRadius="6" left="' + str(table_x) + '" top="' + str(table_y) + '" width="' + str(table_w) + '" height="' + str(table_h) + '"/>')
    lines.append('      <Text left="' + str(table_x+16) + '" top="' + str(table_y+14) + '" fontSize="18" fontStyle="BOLD" fill="' + tokens["title"] + '" fontFamily="' + FONT + '">月度明细表</Text>')

    # 表头
    th_y = table_y + 50
    col_w = table_w - 32
    col1_w = 120
    col2_w = (col_w - col1_w) // 4
    lines.append('      <Container color="' + tokens["table_header_bg"] + '" left="' + str(table_x+16) + '" top="' + str(th_y) + '" width="' + str(col_w) + '" height="30"/>')
    headers = ["月份", "净收入", "利润", "退款率", "转化率"]
    hx = table_x + 16
    widths = [col1_w, col2_w, col2_w, col2_w, col2_w]
    for j, h in enumerate(headers):
        lines.append('      <Text left="' + str(hx+8) + '" top="' + str(th_y+6) + '" fontSize="16" fontStyle="BOLD" fill="' + tokens["title"] + '" fontFamily="' + FONT + '">' + esc(h) + '</Text>')
        hx += widths[j]

    # 表格行
    ty = th_y + 34
    row_h = 34
    for i, r in enumerate(rows):
        bg_color = tokens["table_row_bg"] if i % 2 == 0 else "#F8FAFC"
        lines.append('      <Container color="' + bg_color + '" left="' + str(table_x+16) + '" top="' + str(ty) + '" width="' + str(col_w) + '" height="' + str(row_h) + '"/>')
        tx = table_x + 16
        vals = [r["month"], fmt_amount(r["net_revenue"]), fmt_amount(r["profit"]), fmt_pct(r["refund_rate"]), fmt_pct(r["conv_rate"])]
        for j, v in enumerate(vals):
            lines.append('      <Text left="' + str(tx+8) + '" top="' + str(ty+6) + '" fontSize="16" fill="' + tokens["body"] + '" fontFamily="' + FONT + '">' + esc(v) + '</Text>')
            tx += widths[j]
        ty += row_h

    # 主结论 (底部)
    conc_y = chart_y + chart_h + 20
    lines.append('      <Text left="40" top="' + str(conc_y) + '" fontSize="20" fontStyle="BOLD" fill="' + tokens["title"] + '" fontFamily="' + FONT + '">主结论:</Text>')
    # 基于实际数据的结论
    profit_months = sum(1 for r in rows if r["profit"] > 0)
    conclusion = "6个月净收入" + fmt_amount(totals["net"]) + "，经营利润" + fmt_amount(totals["profit"]) + "，" + str(profit_months) + "个月盈利，整体盈利运营。"
    lines.append('      <Text left="40" top="' + str(conc_y+30) + '" fontSize="18" fill="' + tokens["body"] + '" fontFamily="' + FONT + '">' + esc(conclusion) + '</Text>')

    lines.append('    </Stack>')
    lines.append('  </SizedBox>')
    lines.append('</Snapshot>')
    return "\n".join(lines)

def render(dsl_content, out_path):
    import urllib.request
    req = urllib.request.Request(
        SERVICE_URL,
        data=dsl_content.encode("utf-8"),
        headers={"Content-Type": "text/plain; charset=utf-8", "User-Agent": "Mozilla/5.0"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = resp.read()
    with open(out_path, "wb") as f:
        f.write(data)
    print("Rendered", out_path, len(data), "bytes")

os.makedirs(os.path.join(OUTPUT_ROOT, "round-01"), exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

totals = {"net": total_net, "profit": total_profit, "orders": total_orders, "conv": total_conv}

dsl = gen_dashboard(1600, 1000, rows, totals, DESIGN_TOKENS)
dsl_path = os.path.join(TEMP_DIR, "round-01-dashboard.v1.snapshot")
with open(dsl_path, "w", encoding="utf-8") as f:
    f.write(dsl)
render(dsl, os.path.join(OUTPUT_ROOT, "round-01", "dashboard.png"))
with open(dsl_path, "r", encoding="utf-8") as f:
    with open(os.path.join(OUTPUT_ROOT, "round-01", "dashboard.snapshot"), "w", encoding="utf-8") as fo:
        fo.write(f.read())
print("Dashboard DSL written")

# computed-data.json
computed = {
    "round": 1,
    "currency": "CNY",
    "formulas": {
        "net_revenue": "gross_revenue - refund_amount",
        "profit": "net_revenue - operating_cost",
        "refund_rate": "refund_amount / gross_revenue",
        "conv_rate": "orders / sessions",
        "overall_conv": "total_orders / total_sessions"
    },
    "monthly": rows,
    "totals": {
        "gross_revenue": sum(r["gross_revenue"] for r in rows),
        "refund_amount": sum(r["refund_amount"] for r in rows),
        "operating_cost": sum(r["operating_cost"] for r in rows),
        "net_revenue": total_net,
        "profit": total_profit,
        "orders": total_orders,
        "sessions": total_sessions,
        "refund_rate": sum(r["refund_amount"] for r in rows) / sum(r["gross_revenue"] for r in rows),
        "conv_rate": total_conv
    },
    "kpi": {
        "total_net_revenue": total_net,
        "total_profit": total_profit,
        "total_orders": total_orders,
        "overall_conversion_rate": total_conv
    }
}
with open(os.path.join(OUTPUT_ROOT, "round-01", "computed-data.json"), "w", encoding="utf-8") as f:
    json.dump(computed, f, ensure_ascii=False, indent=2)
print("computed-data.json written")

# layout-map.json
layout_map = {
    "canvas": [1600, 1000],
    "title": [40, 30, 400, 60],
    "subtitle": [40, 60, 400, 85],
    "kpi_cards": [{"label": k[0], "x": 40 + i*(360+20), "y": 100, "w": 360, "h": 70} for i, k in enumerate([
        ("总净收入", None, None), ("总经营利润", None, None), ("总订单", None, None), ("总体转化率", None, None)
    ])],
    "chart": [40, 200, 740, 620],
    "table": [780, 200, 1560, 620],
    "conclusion": [40, 640, 600, 700]
}
with open(os.path.join(OUTPUT_ROOT, "round-01", "layout-map.json"), "w", encoding="utf-8") as f:
    json.dump(layout_map, f, ensure_ascii=False, indent=2)
print("layout-map.json written")

print("Round 01 complete!")
