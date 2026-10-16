# gen_a22_round3.py - 生成 A22 Round 03 经营驾驶舱 (7个月)
import json, os, csv

SUITE_ROOT = os.environ.get("SNAPSHOT_TASK_ROOT", ".")
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "run-20261016")
OUTPUT_ROOT = os.path.join(SUITE_ROOT, "outputs", RUN_ID, "A22")
TEMP_DIR = os.path.join(SUITE_ROOT, "tmp", RUN_ID, "A22")
SERVICE_URL = "https://open-snapshot.muedsa.com/snapshot"
FONT = "Noto Sans CJK SC,Inter"

# 读取原始 CSV
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

# Round 02 更正（继续有效）
corrections_r2 = [
    {"month": "2026-08", "field": "refund_amount", "old": 15048, "new": 25048},
    {"month": "2026-09", "field": "operating_cost", "old": 138000, "new": 208000},
]
for c in corrections_r2:
    for r in rows:
        if r["month"] == c["month"]:
            r[c["field"]] = c["new"]

# Round 03 新增 2026-10
new_row = {
    "month": "2026-10",
    "orders": 640,
    "gross_revenue": 224000,
    "refund_amount": 11200,
    "operating_cost": 142000,
    "sessions": 5900,
}
rows.append(new_row)

# 重新计算所有月份
for r in rows:
    r["net_revenue"] = r["gross_revenue"] - r["refund_amount"]
    r["profit"] = r["net_revenue"] - r["operating_cost"]
    r["refund_rate"] = r["refund_amount"] / r["gross_revenue"] if r["gross_revenue"] > 0 else 0
    r["conv_rate"] = r["orders"] / r["sessions"] if r["sessions"] > 0 else 0

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

DESIGN_TOKENS = {
    "primary": "#2563EB",
    "bg": "#FFFFFF",
    "title": "#111827",
    "body": "#64748B",
    "kpi_bg": "#F8FAFC",
    "kpi_border": "#E2E8F0",
    "net_color": "#2563EB",
    "profit_color": "#10B981",
    "loss_color": "#DC2626",
    "table_header_bg": "#F1F5F9",
    "table_row_bg": "#FFFFFF",
    "table_border": "#CBD5E1"
}

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def gen_dashboard(W, H, rows, totals, tokens, round_id):
    lines = []
    lines.append('<Snapshot type="png">')
    lines.append('  <SizedBox width="' + str(W) + '" height="' + str(H) + '">')
    lines.append('    <Stack alignment="TOP_LEFT">')
    lines.append('      <Container color="' + tokens["bg"] + '" width="' + str(W) + '" height="' + str(H) + '"/>')

    # 标题
    lines.append('      <Text left="40" top="30" fontSize="24" fontStyle="BOLD" fill="' + tokens["title"] + '" fontFamily="' + FONT + '">经营驾驶舱 — 2026-04 至 2026-10 (R3新增)</Text>')
    lines.append('      <Text left="40" top="60" fontSize="18" fill="' + tokens["body"] + '" fontFamily="' + FONT + '">四KPI · 净收入/利润柱图(允许负值) · 月度明细表 (7个月)</Text>')

    # 四KPI卡片 (7个月汇总)
    kpi_y = 100
    kpi_h = 70
    kpi_w = 360
    gap = 20
    profit_color = tokens["loss_color"] if totals["profit"] < 0 else tokens["profit_color"]
    kpis = [
        ("总净收入", fmt_amount(totals["net"]), tokens["net_color"]),
        ("总经营利润", fmt_amount(totals["profit"]), profit_color),
        ("总订单", str(totals["orders"]) + " 笔", tokens["primary"]),
        ("总体转化率", fmt_pct(totals["conv"]), tokens["primary"]),
    ]
    for i, (label, value, color) in enumerate(kpis):
        kx = 40 + i * (kpi_w + gap)
        lines.append('      <Container color="' + tokens["kpi_bg"] + '" border="1 SOLID ' + tokens["kpi_border"] + '" borderRadius="8" left="' + str(kx) + '" top="' + str(kpi_y) + '" width="' + str(kpi_w) + '" height="' + str(kpi_h) + '"/>')
        lines.append('      <Text left="' + str(kx+16) + '" top="' + str(kpi_y+14) + '" fontSize="16" fill="' + tokens["body"] + '" fontFamily="' + FONT + '">' + esc(label) + '</Text>')
        lines.append('      <Text left="' + str(kx+16) + '" top="' + str(kpi_y+36) + '" fontSize="22" fontStyle="BOLD" fill="' + color + '" fontFamily="' + FONT + '">' + esc(value) + '</Text>')

    # 柱图区域 (支持负值，7个月)
    chart_x = 40
    chart_y = 200
    chart_w = 700
    chart_h = 420
    lines.append('      <Container color="#FFFFFF" border="1 SOLID ' + tokens["table_border"] + '" borderRadius="6" left="' + str(chart_x) + '" top="' + str(chart_y) + '" width="' + str(chart_w) + '" height="' + str(chart_h) + '"/>')
    lines.append('      <Text left="' + str(chart_x+16) + '" top="' + str(chart_y+14) + '" fontSize="18" fontStyle="BOLD" fill="' + tokens["title"] + '" fontFamily="' + FONT + '">净收入 / 经营利润 (元)</Text>')

    max_pos = max(max(r["net_revenue"], max(r["profit"], 0)) for r in rows)
    max_neg = abs(min(min(r["profit"], 0) for r in rows))
    chart_bottom = chart_y + chart_h - 60
    chart_top = chart_y + 50
    zero_y = chart_bottom - int((max_pos / (max_pos + max_neg)) * (chart_bottom - chart_top)) if max_neg > 0 else chart_bottom

    lines.append('      <Container color="#94A3B8" left="' + str(chart_x+16) + '" top="' + str(zero_y-0.5) + '" width="' + str(chart_w-32) + '" height="1"/>')

    bar_w = 50
    bar_gap = 35
    total_bar_w = len(rows) * bar_w + (len(rows)-1) * bar_gap
    start_x = chart_x + (chart_w - total_bar_w) // 2

    scale = (chart_bottom - chart_top) / (max_pos + max_neg) if (max_pos + max_neg) > 0 else 1

    for i, r in enumerate(rows):
        bx = start_x + i * (bar_w + bar_gap)
        net_h = int(r["net_revenue"] * scale)
        lines.append('      <Container color="' + tokens["net_color"] + '" left="' + str(bx) + '" top="' + str(zero_y - net_h) + '" width="' + str(bar_w//2 - 2) + '" height="' + str(net_h) + '"/>')
        prof_h = int(abs(r["profit"]) * scale)
        prof_color = tokens["profit_color"] if r["profit"] >= 0 else tokens["loss_color"]
        prof_top = zero_y if r["profit"] >= 0 else zero_y
        lines.append('      <Container color="' + prof_color + '" left="' + str(bx + bar_w//2 + 2) + '" top="' + str(prof_top) + '" width="' + str(bar_w//2 - 2) + '" height="' + str(prof_h) + '"/>')
        if r["profit"] < 0:
            lines[-1] = '      <Container color="' + prof_color + '" left="' + str(bx + bar_w//2 + 2) + '" top="' + str(zero_y) + '" width="' + str(bar_w//2 - 2) + '" height="' + str(prof_h) + '"/>'
        lines.append('      <Text left="' + str(bx-8) + '" top="' + str(chart_bottom+8) + '" fontSize="12" fill="' + tokens["body"] + '" fontFamily="' + FONT + '">' + esc(r["month"][5:]) + '</Text>')

    # 表格区域 (7行)
    table_x = 780
    table_y = 200
    table_w = 780
    table_h = 420
    lines.append('      <Container color="#FFFFFF" border="1 SOLID ' + tokens["table_border"] + '" borderRadius="6" left="' + str(table_x) + '" top="' + str(table_y) + '" width="' + str(table_w) + '" height="' + str(table_h) + '"/>')
    lines.append('      <Text left="' + str(table_x+16) + '" top="' + str(table_y+14) + '" fontSize="18" fontStyle="BOLD" fill="' + tokens["title"] + '" fontFamily="' + FONT + '">月度明细表 (7个月)</Text>')

    th_y = table_y + 50
    col_w = table_w - 32
    col1_w = 100
    col2_w = (col_w - col1_w) // 4
    lines.append('      <Container color="' + tokens["table_header_bg"] + '" left="' + str(table_x+16) + '" top="' + str(th_y) + '" width="' + str(col_w) + '" height="30"/>')
    headers = ["月份", "净收入", "利润", "退款率", "转化率"]
    hx = table_x + 16
    widths = [col1_w, col2_w, col2_w, col2_w, col2_w]
    for j, h in enumerate(headers):
        lines.append('      <Text left="' + str(hx+8) + '" top="' + str(th_y+6) + '" fontSize="16" fontStyle="BOLD" fill="' + tokens["title"] + '" fontFamily="' + FONT + '">' + esc(h) + '</Text>')
        hx += widths[j]

    ty = th_y + 34
    row_h = 32
    for i, r in enumerate(rows):
        bg_color = tokens["table_row_bg"] if i % 2 == 0 else "#F8FAFC"
        lines.append('      <Container color="' + bg_color + '" left="' + str(table_x+16) + '" top="' + str(ty) + '" width="' + str(col_w) + '" height="' + str(row_h) + '"/>')
        tx = table_x + 16
        vals = [r["month"], fmt_amount(r["net_revenue"]), fmt_amount(r["profit"]), fmt_pct(r["refund_rate"]), fmt_pct(r["conv_rate"])]
        for j, v in enumerate(vals):
            lines.append('      <Text left="' + str(tx+8) + '" top="' + str(ty+6) + '" fontSize="16" fill="' + tokens["body"] + '" fontFamily="' + FONT + '">' + esc(v) + '</Text>')
            tx += widths[j]
        ty += row_h

    # 主结论
    conc_y = chart_y + chart_h + 20
    loss_months = sum(1 for r in rows if r["profit"] < 0)
    conclusion = "7个月净收入" + fmt_amount(totals["net"]) + "，经营利润" + fmt_amount(totals["profit"]) + "，" + str(loss_months) + "个月亏损，最后月份2026-10恢复盈利。"
    lines.append('      <Text left="40" top="' + str(conc_y) + '" fontSize="20" fontStyle="BOLD" fill="' + tokens["title"] + '" fontFamily="' + FONT + '">主结论:</Text>')
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

os.makedirs(os.path.join(OUTPUT_ROOT, "round-03"), exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

totals = {"net": total_net, "profit": total_profit, "orders": total_orders, "conv": total_conv}

dsl = gen_dashboard(1600, 1000, rows, totals, DESIGN_TOKENS, "round-03")
dsl_path = os.path.join(TEMP_DIR, "round-03-dashboard.v1.snapshot")
with open(dsl_path, "w", encoding="utf-8") as f:
    f.write(dsl)
render(dsl, os.path.join(OUTPUT_ROOT, "round-03", "dashboard.png"))
with open(dsl_path, "r", encoding="utf-8") as f:
    with open(os.path.join(OUTPUT_ROOT, "round-03", "dashboard.snapshot"), "w", encoding="utf-8") as fo:
        fo.write(f.read())
print("Dashboard DSL written")

# computed-data.json
computed = {
    "round": 3,
    "currency": "CNY",
    "corrections_r2": corrections_r2,
    "new_row_r3": new_row,
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
    },
    "last_month": "2026-10"
}
with open(os.path.join(OUTPUT_ROOT, "round-03", "computed-data.json"), "w", encoding="utf-8") as f:
    json.dump(computed, f, ensure_ascii=False, indent=2)
print("computed-data.json written")

# layout-map.json
layout_map = {
    "canvas": [1600, 1000],
    "title": [40, 30, 550, 60],
    "chart": [40, 200, 740, 620],
    "table": [780, 200, 1560, 620],
    "conclusion": [40, 640, 750, 700],
    "months": 7,
    "zero_baseline_supported": True
}
with open(os.path.join(OUTPUT_ROOT, "round-03", "layout-map.json"), "w", encoding="utf-8") as f:
    json.dump(layout_map, f, ensure_ascii=False, indent=2)
print("layout-map.json written")

# change-audit.json
change_audit = {
    "round": 3,
    "changes_from_round2": [
        "新增2026-10一行: orders=640, gross_revenue=224000, refund_amount=11200, operating_cost=142000, sessions=5900",
        "Round 02 两项更正继续有效",
        "KPI改成7个月期间汇总",
        "图与表包括全部7个月",
        "最后月份指2026-10",
        "主区域边界维持上一轮±2px"
    ],
    "old_totals_r2": {
        "net_revenue": 908624,
        "profit": 182124,
        "orders": 3045,
        "sessions": 27300
    },
    "new_totals_r3": {
        "net_revenue": total_net,
        "profit": total_profit,
        "orders": total_orders,
        "sessions": total_sessions
    },
    "visual_regression": {
        "canvas_size": [1600, 1000],
        "chart_area_unchanged": [40, 200, 740, 620],
        "table_area_unchanged": [780, 200, 1560, 620],
        "negative_axis_retained": True,
        "bar_count": 7,
        "table_rows": 7
    },
    "notes": "7个月汇总，2026-10恢复盈利 (利润70,800元)，负轴范围保留以显示2026-09亏损。"
}
with open(os.path.join(OUTPUT_ROOT, "round-03", "change-audit.json"), "w", encoding="utf-8") as f:
    json.dump(change_audit, f, ensure_ascii=False, indent=2)
print("change-audit.json written")

print("Round 03 complete!")
