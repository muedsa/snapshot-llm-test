#!/usr/bin/env python3
"""A01 operations dashboard: computes figures from inputs/monthly.csv and emits DSL + audit JSON."""
import csv, json, os, sys
from pathlib import Path

TOOLS = os.environ["TOOLS"]
sys.path.insert(0, TOOLS)
from dsl import Canvas, CN, LATIN
import suite

TASK = "A01"
ROOT = suite.ROOT
SRC = ROOT / "tasks" / "A01-operations-dashboard" / "inputs" / "monthly.csv"
rows = list(csv.DictReader(SRC.read_text(encoding="utf-8").splitlines()))
data = []
for r in rows:
    gross = int(r["gross_revenue"]); refund = int(r["refund_amount"])
    cost = int(r["operating_cost"]); orders = int(r["orders"]); sessions = int(r["sessions"])
    net = gross - refund; profit = net - cost
    data.append({
        "month": r["month"], "orders": orders, "sessions": sessions,
        "gross_revenue": gross, "refund_amount": refund, "operating_cost": cost,
        "net_revenue": net, "operating_profit": profit,
        "refund_rate": refund / gross, "conversion_rate": orders / sessions,
    })

tot = {
    "gross_revenue": sum(d["gross_revenue"] for d in data),
    "refund_amount": sum(d["refund_amount"] for d in data),
    "operating_cost": sum(d["operating_cost"] for d in data),
    "net_revenue": sum(d["net_revenue"] for d in data),
    "operating_profit": sum(d["operating_profit"] for d in data),
    "orders": sum(d["orders"] for d in data),
    "sessions": sum(d["sessions"] for d in data),
}
tot["overall_conversion_rate"] = tot["orders"] / tot["sessions"]
assert tot["net_revenue"] == tot["gross_revenue"] - tot["refund_amount"]
assert tot["operating_profit"] == tot["net_revenue"] - tot["operating_cost"]

# ------------------------------------------------------------------ palette
BG = "#F4F7FC"; NAVY = "#0B1B35"; NAVY2 = "#16386F"
WHITE = "#FFFFFF"; INK = "#0F172A"; MUTED = "#5B6B85"; LINE = "#DDE5F0"
BLUE = "#2563EB"; TEAL = "#0D9488"; AMBER = "#F59E0B"; RED = "#DC2626"; GREEN = "#16A34A"

c = Canvas(1600, 1000, BG)

# header
c.gradient(0, 0, 1600, 112, [NAVY, NAVY2], begin="CENTER_LEFT", end="CENTER_RIGHT")
c.rect(0, 108, 1600, 4, "#38BDF8")
c.text(48, 18, 900, 48, "NORTHSTAR  ·  六个月经营诊断驾驶舱", 36, WHITE, bold=True)
c.text(48, 70, 900, 30, "2026-04 — 2026-09   |   金额单位：元（CNY）", 20, "#BBD3F2")
c.text(1130, 26, 420, 34, "MANAGEMENT  VIEW  /  H1", 20, "#8FB6EA", align="RIGHT")
c.text(1130, 66, 420, 30, "数据源：monthly.csv · 6 个月", 18, "#BBD3F2", align="RIGHT")

# ------------------------------------------------------------------ KPI cards
kpis = [
    ("总净收入", "¥ " + format(tot["net_revenue"], ","), "gross − refund", BLUE, "NET"),
    ("总经营利润", "¥ " + format(tot["operating_profit"], ","), "净收入 − 经营成本", TEAL, "PROFIT"),
    ("总订单", format(tot["orders"], ",") + " 笔", "6 个月累计", AMBER, "ORDERS"),
    ("期间总体转化率", "%.2f%%" % (tot["overall_conversion_rate"] * 100), "总订单 ÷ 总访问量", "#7C3AED", "CVR"),
]
for i, (label, val, sub, col, en) in enumerate(kpis):
    x = 48 + i * 380
    c.rect(x, 136, 364, 128, WHITE, radius=16, border="1 SOLID " + LINE)
    c.rect(x, 136, 6, 128, col, radius=3)
    c.text(x + 24, 148, 320, 28, label, 20, MUTED)
    c.text(x + 24, 178, 330, 52, val, 36, INK, bold=True, font=LATIN if i in (0, 1, 2, 3) else None)
    c.text(x + 24, 230, 330, 26, sub, 17, MUTED)
    c.text(x + 250, 150, 90, 24, en, 14, "#9AAAC2", align="RIGHT", font=LATIN)

# ------------------------------------------------------------------ left grouped bar chart
LX, LY, LW, LH = 48, 282, 940, 378
c.rect(LX, LY, LW, LH, WHITE, radius=16, border="1 SOLID " + LINE)
c.text(70, 294, 560, 32, "净收入 与 经营利润 · 分月对比", 24, INK, bold=True)
c.text(70, 328, 600, 24, "金额 / 元 · 同一零起点、同一刻度，两组柱共用比例", 17, MUTED)
# legend
c.rect(668, 302, 18, 18, BLUE, radius=4)
c.text(692, 296, 110, 30, "净收入", 18, INK)
c.rect(806, 302, 18, 18, TEAL, radius=4)
c.text(830, 296, 130, 30, "经营利润", 18, INK)

PLOT_L, PLOT_R = 116, 958
BASE_Y, TOP_Y = 620, 356
VMAX = 220000
SCALE = (BASE_Y - TOP_Y) / VMAX
for v in (0, 50000, 100000, 150000, 200000):
    y = BASE_Y - v * SCALE
    c.hline(PLOT_L, y, PLOT_R - PLOT_L, 1 if v else 2, LINE if v else "#94A3B8")
    c.text(58, y - 12, 54, 24, "%dk" % (v // 1000), 17, MUTED, align="RIGHT", font=LATIN)
GROUP = (PLOT_R - PLOT_L) / 6
for i, d in enumerate(data):
    gx = PLOT_L + GROUP * i + GROUP / 2
    hn = d["net_revenue"] * SCALE
    hp = d["operating_profit"] * SCALE
    c.bar(gx - 41, BASE_Y - hn, 38, hn, BLUE, radius=5)
    c.bar(gx + 3, BASE_Y - hp, 38, hp, TEAL, radius=5)
    c.text(gx - 52, BASE_Y - hn - 26, 104, 24, format(d["net_revenue"], ","), 16, BLUE, align="CENTER", font=LATIN)
    c.text(gx - 48, 626, 96, 28, d["month"][-2:] + "月", 20, INK, bold=True, align="CENTER")

# ------------------------------------------------------------------ right mini charts
RX, RW = 1004, 548
# sessions
c.rect(RX, 282, RW, 182, WHITE, radius=16, border="1 SOLID " + LINE)
c.text(1026, 292, 360, 28, "访问量 Sessions", 20, INK, bold=True)
c.text(1360, 294, 170, 26, "0 → 6,000", 17, MUTED, align="RIGHT", font=LATIN)
SX0, SGAP, SBARW = 1062, 80, 42
for i, d in enumerate(data):
    h = d["sessions"] / 6000 * 76
    x = SX0 + SGAP * i
    c.bar(x, 418 - h, SBARW, h, "#93C5FD", radius=5)
    c.text(x - 9, 396 - h, 60, 22, format(d["sessions"], ","), 16, BLUE, align="CENTER", font=LATIN)
    c.text(x - 6, 424, 54, 24, d["month"][-2:] + "月", 16, MUTED, align="CENTER")
# conversion rate
c.rect(RX, 478, RW, 182, WHITE, radius=16, border="1 SOLID " + LINE)
c.text(1026, 488, 360, 28, "转化率 CVR", 20, INK, bold=True)
c.text(1360, 490, 170, 26, "8% → 13%", 17, MUTED, align="RIGHT", font=LATIN)
CY0, CY1, CMIN, CMAX = 536, 610, 0.08, 0.13
def cy(v):
    return CY1 - (v - CMIN) / (CMAX - CMIN) * (CY1 - CY0)
for v in (0.09, 0.11, 0.13):
    y = cy(v)
    c.hline(1062, y, 452, 1, LINE)
    c.text(1024, y - 11, 36, 22, "%d%%" % (v * 100), 16, MUTED, align="RIGHT", font=LATIN)
pts = []
for i, d in enumerate(data):
    pts.append((SX0 + SGAP * i + SBARW / 2, cy(d["conversion_rate"])))
for p1, p2 in zip(pts, pts[1:]):
    c.line(p1[0], p1[1], p2[0], p2[1], 4, "#7C3AED")
for p in pts:
    c.circle(p[0], p[1], 6, "#7C3AED")
    c.circle(p[0], p[1], 3, WHITE)
ov = cy(tot["overall_conversion_rate"])
c.dashed_hline(1062, ov, 452, 2, "#F59E0B", dash=9, gap=6)
c.rect(1382, ov - 36, 154, 26, "#FFF7ED", radius=6, border="1 SOLID #FDE68A")
c.text(1388, ov - 35, 142, 24, "总体 11.15%", 16, "#B45309", bold=True, align="CENTER")
for i, d in enumerate(data):
    x = SX0 + SGAP * i
    c.text(x - 6, 616, 54, 24, d["month"][-2:] + "月", 16, MUTED, align="CENTER")

# ------------------------------------------------------------------ detail table
TX, TY, TW, TH = 48, 676, 1000, 276
c.rect(TX, TY, TW, TH, WHITE, radius=16, border="1 SOLID " + LINE)
c.text(70, 686, 500, 30, "分月明细", 22, INK, bold=True)
c.text(830, 688, 196, 26, "退款率 = 退款 ÷ 收入", 16, MUTED, align="RIGHT")
cols = [(70, 150, "月份", "LEFT"), (220, 200, "净收入 / 元", "RIGHT"),
        (420, 170, "退款率", "RIGHT"), (590, 210, "经营利润 / 元", "RIGHT"),
        (800, 226, "转化率", "RIGHT")]
c.rect(64, 722, 968, 38, "#EEF3FB", radius=6)
for x, w, h, al in cols:
    c.text(x, 724, w, 32, h, 18, "#31456B", bold=True, align=al)
for i, d in enumerate(data):
    y = 762 + i * 31
    if i % 2 == 1:
        c.rect(64, y - 3, 968, 31, "#F8FAFE")
    vals = [d["month"], format(d["net_revenue"], ","), "%.2f%%" % (d["refund_rate"] * 100),
            format(d["operating_profit"], ","), "%.2f%%" % (d["conversion_rate"] * 100)]
    for j, ((x, w, h, al), v) in enumerate(zip(cols, vals)):
        col = RED if (j == 2 and d["refund_rate"] >= 0.08) else INK
        c.text(x, y, w, 28, v, 20, col, align=al, font=LATIN if j in (1, 2, 3, 4) else None)
c.hline(64, 948, 968, 1, LINE)

# ------------------------------------------------------------------ conclusion
QX, QY, QW, QH = 1064, 676, 488, 276
c.rect(QX, QY, QW, QH, NAVY, radius=16)
c.text(1088, 688, 420, 30, "管理结论  /  EVIDENCE-BASED", 20, "#7DD3FC", bold=True)
c.text(1088, 718, 436, 132,
       "增长来自规模而非效率：净收入由 119,700 升至 202,368 元（+69.1%），"
       "但期间总体转化率 11.15% 低于 4 月 12.00%。6 月与 8 月退款率达 8.00%，"
       "优先治理退款与转化再扩大投放。", 20, "#E8F0FC", align="LEFT")
c.rect(1088, 858, 200, 56, "#163A6B", radius=10)
c.text(1100, 862, 180, 22, "净收入 +69.1%", 18, "#7DD3FC", bold=True, font=LATIN)
c.text(1100, 884, 180, 22, "119,700 → 202,368", 16, "#C6DCF7", font=LATIN)
c.rect(1300, 858, 228, 56, "#163A6B", radius=10)
c.text(1312, 862, 206, 22, "总体转化率 11.15%", 18, "#FCD34D", bold=True)
c.text(1312, 884, 206, 22, "≠ 月均 11.19%", 16, "#C6DCF7")

c.text(48, 962, 1000, 26, "口径：净收入 = 收入 − 退款；经营利润 = 净收入 − 经营成本；总体转化率 = 总订单 ÷ 总访问量（不平均月比例）。", 16, MUTED)
c.text(1064, 962, 488, 26, "© NORTHSTAR ANALYTICS  ·  SNAPSHOT DSL", 16, MUTED, align="RIGHT", font=LATIN)

# ------------------------------------------------------------------ outputs
dsl = c.render()
out = suite.out_dir(TASK)
(out / "operations.snapshot").write_text(dsl, encoding="utf-8")
ver = os.environ.get("BUILD_VERSION", "v1")
tmp = suite.tmp_dir(TASK, ver)
(tmp / "operations.snapshot").write_text(dsl, encoding="utf-8")

audit = {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "units": {"amount": "CNY 元", "orders": "笔", "sessions": "次", "rate": "小数比例（0-1）"},
    "months": [
        {
            "month": d["month"], "orders": d["orders"], "sessions": d["sessions"],
            "gross_revenue": d["gross_revenue"], "refund_amount": d["refund_amount"],
            "operating_cost": d["operating_cost"],
            "net_revenue": d["net_revenue"], "operating_profit": d["operating_profit"],
            "refund_rate": round(d["refund_rate"], 6),
            "conversion_rate": round(d["conversion_rate"], 6),
        } for d in data
    ],
    "totals": {**tot, "overall_conversion_rate": round(tot["overall_conversion_rate"], 6)},
    "axes": [
        {"chart": "grouped_bars", "unit": "CNY 元", "min": 0, "max": VMAX,
         "zero_line_px": BASE_Y, "tick_values": [0, 50000, 100000, 150000, 200000],
         "pixel_mapping": "y = 620 - value * (620-356)/220000", "shared_by": ["net_revenue", "operating_profit"]},
        {"chart": "sessions_mini", "unit": "次", "min": 0, "max": 6000,
         "zero_line_px": 418, "pixel_mapping": "h = sessions/6000*76", "shared_month_x": True},
        {"chart": "cvr_mini", "unit": "比例", "min": CMIN, "max": CMAX,
         "zero_line_px": None, "pixel_mapping": "y = 610 - (v-0.08)/(0.13-0.08)*(610-536)",
         "shared_month_x": True},
    ],
    "conclusion": {
        "text": "增长来自规模而非效率：净收入由 119,700 升至 202,368 元（+69.1%），但期间总体转化率 11.15% 低于 4 月 12.00%。6 月与 8 月退款率达 8.00%，优先治理退款与转化再扩大投放。",
        "referenced_fields": ["months[0].net_revenue", "months[5].net_revenue",
                              "totals.overall_conversion_rate", "months[0].conversion_rate",
                              "months[2].refund_rate", "months[4].refund_rate"],
        "values": {"net_growth_pct": round((data[-1]["net_revenue"] / data[0]["net_revenue"] - 1) * 100, 2),
                   "overall_cvr_pct": round(tot["overall_conversion_rate"] * 100, 2),
                   "apr_cvr_pct": round(data[0]["conversion_rate"] * 100, 2),
                   "mean_monthly_cvr_pct": round(sum(d["conversion_rate"] for d in data) / 6 * 100, 2)},
    },
    "evidence": {"png": "operations.png", "dsl": "operations.snapshot",
                  "checks": ["net = gross - refund", "profit = net - cost",
                             "overall_cvr = total orders / total sessions"]},
}
(out / "computed-data.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("A01 DSL bytes", len(dsl.encode("utf-8")), "| totals", tot)
