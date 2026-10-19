# -*- coding: utf-8 -*-
"""A01 · 六个月经营诊断驾驶舱 数据计算与 DSL 生成（v2：面板内坐标基准自动换算）。
启动基准：总任务根（或 SNAPSHOT_TASK_ROOT）；需 SNAPSHOT_RUN_ID。
产出：
  outputs/<run_id>/A01/computed-data.json
  outputs/<run_id>/A01/operations.snapshot
"""
import csv
import json
import math
import os
from pathlib import Path

TASK_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ["SNAPSHOT_RUN_ID"]
OUT = TASK_ROOT / "outputs" / RUN_ID / "A01"
OUT.mkdir(parents=True, exist_ok=True)

FONT = "Noto Sans CJK SC"
FONT_NUM = "Inter"
sep = lambda v: f"{v:,}"
pct2 = lambda v: f"{v*100:.2f}%"
pct1_delta = lambda v: f"+{v*100:.1f}%"

# ---------- 1) 数据 ----------
rows = list(csv.DictReader((TASK_ROOT / "tasks" / "A01-operations-dashboard" / "inputs" / "monthly.csv").open(encoding="utf-8")))
months = []
for r in rows:
    o = int(r["orders"]); gr = int(r["gross_revenue"]); rf = int(r["refund_amount"])
    oc = int(r["operating_cost"]); se = int(r["sessions"])
    months.append({
        "month": r["month"], "orders": o, "gross_revenue": gr, "refund_amount": rf,
        "operating_cost": oc, "sessions": se,
        "net_revenue": gr - rf, "profit": gr - rf - oc,
        "refund_rate": rf / gr, "conversion": o / se,
    })
T = {k: sum(m[k] for m in months) for k in
     ("gross_revenue", "refund_amount", "operating_cost", "orders", "sessions")}
T["net_revenue"] = T["gross_revenue"] - T["refund_amount"]
T["profit"] = T["net_revenue"] - T["operating_cost"]
T["overall_conversion"] = T["orders"] / T["sessions"]
T["profit_margin"] = T["profit"] / T["net_revenue"]
net_delta = months[-1]["net_revenue"] / months[-2]["net_revenue"] - 1
orders_delta = months[-1]["orders"] / months[-2]["orders"] - 1

# ---------- 2) 位置感知 DSL 发射器 ----------
CYAN = "#4CC2FF"; AMBER = "#FFC154"; GREEN = "#3FD9A4"; RED = "#FF8A80"
TXT = "#EAF3FF"; SUB = "#A9BFDF"; MUT = "#8FA8CE"
PANEL = "#12203A"; PBORDER = "#23375C"
GRID = "#27395F"; AXLINE = "#33507F"
BGL = "#0B1526"

ORIGIN = [0, 0]

def fnum(v):
    s = f"{float(v):.2f}".rstrip("0").rstrip(".")
    return s if s else "0"

def p(x, y):
    """把目标点按当前 ORIGIN 换算成相对坐标。"""
    return x - ORIGIN[0], y - ORIGIN[1]

def content_of(ox, oy, children):
    """以 (ox,oy) 为基准构建子元素列表后恢复原基准。"""
    prev = tuple(ORIGIN)
    ORIGIN[0], ORIGIN[1] = ox, oy
    try:
        return children()
    finally:
        ORIGIN[0], ORIGIN[1] = prev

def rect(x, y, w, h, color=None, radius=None, border=None, shape=None):
    lx, ly = p(x, y)
    a = f'<Container width="{fnum(w)}" height="{fnum(h)}"'
    if color: a += f' color="{color}"'
    if radius is not None and radius > 0: a += f' borderRadius="{fnum(radius)}"'
    if border: a += f' border="{border}"'
    if shape: a += f' shape="{shape}"'
    return f'<Positioned left="{fnum(lx)}" top="{fnum(ly)}" width="{fnum(w)}" height="{fnum(h)}">' + a + " /></Positioned>"

def rrect(x, y, w, h, color=None, radius=None):
    return rect(x, y, w, h, color, radius)

def hline(x, y, w, th, color):
    return rect(x, y, w, th, color)

def text(x, y, content, size, color, family=FONT, bold=False, align="START", box_w=None):
    lx, ly = p(x, y)
    sty = f'<Text fontSize="{fnum(size)}" color="{color}" fontFamily="{family}"'
    if bold: sty += ' fontStyle="BOLD"'
    sty += ' maxLines="1" overflow="CLIP"'
    if align != "START":
        sty += f' textAlign="{align}"'
    sty += f'>{content}</Text>'
    if align == "START" and box_w is None:
        return f'<Positioned left="{fnum(lx)}" top="{fnum(ly)}">{sty}</Positioned>'
    bw = box_w if box_w is not None else 90
    return f'<Positioned left="{fnum(lx)}" top="{fnum(ly)}" width="{fnum(bw)}">{sty}</Positioned>'

def circle(x, y, d, color, border=None):
    return rect(x, y, d, d, color, shape="CIRCLE", border=border)

def panel(x, y, w, h, children):
    inner = f'<SizedBox width="{fnum(w)}" height="{fnum(h)}" />' + "".join(children)
    return (f'<Positioned left="{fnum(x)}" top="{fnum(y)}" width="{fnum(w)}" height="{fnum(h)}">'
            f'<Container width="{fnum(w)}" height="{fnum(h)}" color="{PANEL}" border="{PBORDER and "1 SOLID #23375C"}" borderRadius="14">'
            f'<Stack>{inner}</Stack></Container></Positioned>')

# ---------- 3) 组装 ----------
S = ['<SizedBox width="1600" height="1000" />']

# ===== 头部 =====
S.append(rect(28, 32, 40, 40, "#4CC2FF", 10))
S.append('<Positioned left="28" top="32" width="40" height="40"><Text fontSize="24" color="#0B1526" fontFamily="Inter" fontStyle="BOLD" maxLines="1">N</Text></Positioned>')
S.append(text(84, 34, "Northstar 经营诊断驾驶舱", 36, TXT, bold=True))
S.append(text(1150, 40, "2026-04 至 2026-09 · 指标单位：元 / 万元 / %", 20, SUB, align="END", box_w=422))

# ===== KPI 卡 =====
kpis = [
    ("总净收入", "918,624 元", "9 月单月 20.24 万（环比 +17.0%）", CYAN),
    ("总经营利润", "262,124 元", "期间利润率 28.53%（利润 / 净收入）", AMBER),
    ("总订单", "3,045 笔", "9 月 620 单（环比 +8.8%）", GREEN),
    ("期间总体转化率", "11.15%", "总订单 3,045 ÷ 总访问 27,300", "#B98CFF"),
]
KPI_Y, KPI_H, KPI_W = 108, 120, 371
for i, (label, value, sub, accent) in enumerate(kpis):
    x = 28 + i * 391
    S.append(rect(x, KPI_Y, KPI_W, KPI_H, PANEL, 14, "1 SOLID #23375C"))
    S.append(rect(x, KPI_Y, 4, KPI_H, accent, None))
    S.append(text(x + 20, KPI_Y + 12, label, 20, SUB, bold=True))
    S.append(text(x + 20, KPI_Y + 44, value, 38, TXT, family="Inter," + FONT, bold=True))
    S.append(text(x + 20, KPI_Y + 94, sub, 16, MUT))

# ===== 主柱图面板（基于画布绝对坐标构建后换算） =====
PX, PY, PW, PH = 28, 248, 1020, 400
plot_x0 = PX + 84
plot_w = PW - 84 - 24
plot_top = PY + 58
plot_h = 280
plot_bot = plot_top + plot_h
AXIS_MAX_MAP = 24.0
ymap = lambda v: plot_bot - (v / AXIS_MAX_MAP) * plot_h

def build_main():
    ch = []
    ch.append(text(PX + 24, PY + 16, "净收入与经营利润（万元）", 20, TXT, bold=True))
    legend_x = PX + PW - 24 - 320
    ch.append(circle(legend_x, PY + 24, 12, CYAN))
    ch.append(text(legend_x + 17, PY + 19, "净收入", 18, SUB))
    ch.append(circle(legend_x + 110, PY + 24, 12, AMBER))
    ch.append(text(legend_x + 127, PY + 19, "经营利润", 18, SUB))
    gvals = [0, 6, 12, 18, 24]
    ch.append(text(34, 294, "万元", 16, MUT))
    for g in gvals:
        ch.append(text(PX + 16, ymap(g) - 12, str(g), 18, MUT, align="END", box_w=(plot_x0 - PX - 22)))
        if g > 0:
            ch.append(rect(plot_x0, ymap(g), plot_w, 1, GRID))
    ch.append(rect(plot_x0, plot_bot, plot_w, 2, AXLINE))
    BAR_W, PAIR_GAP = 58, 10
    GROUP = plot_w / 6.0
    for i, m in enumerate(months):
        cx = plot_x0 + (i + 0.5) * GROUP
        total = BAR_W * 2 + PAIR_GAP
        x_net = cx - total / 2
        x_pro = x_net + BAR_W + PAIR_GAP
        for (x0, v, c, lbl_c) in ((x_net, m["net_revenue"] / 10000, CYAN, "#BFE7FF"),
                                  (x_pro, m["profit"] / 10000, AMBER, "#FFD98F")):
            bh = (v / AXIS_MAX_MAP) * plot_h
            top = plot_bot - bh
            ch.append(f'<Positioned left="{fnum(p(x0, 0)[0])}" top="{fnum(p(0, top)[1])}" width="{fnum(BAR_W)}" height="{fnum(bh)}">'
                      f'<Container width="{fnum(BAR_W)}" height="{fnum(bh)}" color="{c}"'
                      f' borderRadiusTopLeft="{fnum(min(6, bh / 2))}" borderRadiusTopRight="{fnum(min(6, bh / 2))}" /></Positioned>')
            ch.append(text(x0 + BAR_W / 2 - 45, top - 28, f"{v:.2f}", 18, lbl_c, family=FONT_NUM, bold=True, align="CENTER", box_w=90))
        ch.append(text(cx - 60, plot_bot + 8, m["month"], 18, SUB, align="CENTER", box_w=120))
    return ch

S.append(panel(PX, PY, PW, PH, content_of(PX, PY, build_main)))

# ===== 右上：访问量 =====
RX, RW = 1068, 504
c1y, c1h = 248, 192
p1_top, p1_bot = c1y + 52, c1y + 150
AX1_MAX = 6000.0
a1x0, a1x1 = RX + 84, RX + RW - 20
d1w = a1x1 - a1x0
ymap1 = lambda v: p1_bot - (v / AX1_MAX) * (p1_bot - p1_top)

def build_sessions():
    card = []
    card.append(text(RX + 20, c1y + 10, "访问量（次数）", 20, TXT, bold=True))
    for g in [0, 3000, 6000]:
        card.append(text(RX + 12, ymap1(g) - 11, sep(g), 18, MUT, family=FONT_NUM, align="END", box_w=(a1x0 - RX - 18)))
        if g > 0:
            card.append(rect(a1x0, ymap1(g), d1w, 1, GRID))
    card.append(rect(a1x0, p1_bot, d1w, 2, AXLINE))
    GW1 = d1w / 6.0
    for i, m in enumerate(months):
        cx = a1x0 + (i + 0.5) * GW1
        bw = 30
        x0 = cx - bw / 2
        h1 = (m["sessions"] / AX1_MAX) * (p1_bot - p1_top)
        card.append(f'<Positioned left="{fnum(p(x0, 0)[0])}" top="{fnum(p(0, p1_bot - h1)[1])}" width="{fnum(bw)}" height="{fnum(h1)}">'
                    f'<Container width="{fnum(bw)}" height="{fnum(h1)}" color="{GREEN}" borderRadiusTopLeft="4" borderRadiusTopRight="4" /></Positioned>')
        card.append(text(cx - 34, p1_bot - h1 - 26, sep(m["sessions"]), 18, "#C8F5E4", family=FONT_NUM, align="CENTER", box_w=68, bold=True))
        card.append(text(cx - 22, p1_bot + 8, m["month"][5:7] + "月", 18, MUT, family=FONT_NUM + "," + FONT, align="CENTER", box_w=44))
    return card

S.append(panel(RX, c1y, RW, c1h, content_of(RX, c1y, build_sessions)))

# ===== 右下：转化率 =====
c2y, c2h = 458, 200
p2_top, p2_bot = c2y + 62, c2y + 170
AX2_MAX = 12.5
a2x0, a2x1 = RX + 84, RX + RW - 20
d2w = a2x1 - a2x0
ymap2 = lambda v: p2_bot - (v / AX2_MAX) * (p2_bot - p2_top)

def build_conv():
    card = []
    card.append(text(RX + 20, c2y + 6, "转化率（订单/访问，%）", 20, TXT, bold=True))
    for g in [0, 5, 10]:
        card.append(text(RX + 12, ymap2(g) - 11, f"{g}%", 18, MUT, family=FONT_NUM, align="END", box_w=(a2x0 - RX - 18)))
        if g > 0:
            card.append(rect(a2x0, ymap2(g), d2w, 1, GRID))
    card.append(rect(a2x0, p2_bot, d2w, 2, AXLINE))
    GW2 = d2w / 6.0
    pts = [(a2x0 + (i + 0.5) * GW2, ymap2(m["conversion"] * 100)) for i, m in enumerate(months)]
    for i in range(5):
        x1, y1 = pts[i]; x2, y2 = pts[i + 1]
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy)
        th = math.atan2(dy, dx)
        c_, s_ = math.cos(th), math.sin(th)
        matrix = f"({fnum(c_)},{fnum(s_)},0,0,{fnum(-s_)},{fnum(c_)},0,0,0,0,1,0,0,0,0,1)"
        card.append(f'<Positioned left="{fnum(p(x1, 0)[0])}" top="{fnum(p(0, y1 - 1.5)[1])}" width="{fnum(L)}" height="3">'
                    f'<Transform matrix="{matrix}" alignment="CENTER_LEFT">'
                    f'<Container width="{fnum(L)}" height="3" color="{GREEN}" /></Transform></Positioned>')
    for i, (px, py) in enumerate(pts):
        m = months[i]
        card.append(circle(px - 5.5, py - 5.5, 11, GREEN, "2 SOLID #0B1526"))
        card.append(text(px - 40, py - 33, f"{m['conversion'] * 100:.2f}%", 18, "#C8F5E4", family=FONT_NUM, bold=True, align="CENTER", box_w=80))
        card.append(text(px - 22, p2_bot + 4, m["month"][5:7] + "月", 18, MUT, family=FONT_NUM + "," + FONT, align="CENTER", box_w=44))
    return card

S.append(panel(RX, c2y, RW, c2h, content_of(RX, c2y, build_conv)))

# ===== 明细表 =====
TB_Y, TB_H = 668, 208
cols = [("月份", 168, "START"), ("净收入（元）", 362, "END"),
        ("退款率", 362, "END"), ("经营利润（元）", 362, "END"), ("转化率", 290, "END")]
S.append(rect(28, TB_Y, 1544, TB_H, "#0F1C35", 10))
S.append(rect(28, TB_Y, 1544, 28, "#16284A", 10))
S.append(rect(28, TB_Y, 4, TB_H, CYAN, 10))
for ci, (label, wc, al) in enumerate(cols):
    cx0 = 28 + sum(c[1] for c in cols[:ci])
    S.append(text(cx0 + (16 if ci == 0 else 0), TB_Y + 2, label, 18, "#8FA8CE", bold=True,
                  align="END" if al == "END" else "START", box_w=(wc - 36) if al == "END" else (wc - 16)))
S.append(rect(32, TB_Y + 28, 1544 - 8, 2, "#2A3E63"))
hdr_h, row_h = 28, 30
for ri, m in enumerate(months):
    ry = TB_Y + hdr_h + ri * row_h
    if ri % 2 == 1:
        S.append(rect(32, ry, 1544 - 8, row_h, "#152744", None))
    ref_r = m["refund_rate"]
    ref_c = RED if ref_r >= 0.075 else (GREEN if ref_r <= 0.045 else TXT)
    cells = [
        (0, m["month"], TXT, False),
        (1, sep(m["net_revenue"]), TXT, False),
        (2, pct2(ref_r), ref_c, ref_r >= 0.075),
        (3, sep(m["profit"]), TXT, False),
        (4, pct2(m["conversion"]), TXT, False),
    ]
    for ci, content, col, bold in cells:
        wc, al = cols[ci][1], cols[ci][2]
        cx0 = 28 + sum(c[1] for c in cols[:ci])
        if ci == 0:
            S.append(text(cx0 + 16, ry + 1, content, 20, col, family=FONT_NUM, box_w=wc - 32))
        else:
            S.append(text(cx0 + 8, ry + 1, content, 20, col, family=FONT, bold=bold, align="END", box_w=wc - 16))
    if ri > 0:
        S.append(rect(32, ry, 1544 - 8, 1, "#1D2E52"))

# ===== 管理结论 =====
CC_Y = 890
S.append(rect(28, CC_Y, 1544, 64, "#142446", 12))
S.append(rect(28, CC_Y, 6, 64, "#FFB454", 12))
S.append(text(52, CC_Y + 8, "管理结论：9 月净收入 20.24 万元、经营利润 6.44 万元为期间最高（净收入环比 +17.0%）；期间总体转化率 11.15%（3,045 单 ÷ 27,300 访问）。", 20, TXT))
S.append(text(52, CC_Y + 36, "风险：6 月与 8 月退款率升至 8.00%（其余月份 4.00%–5.00%），8 月退款 1.50 万元；建议优先排查 8 月售后链路，并验证 9 月回落至 4.00% 是否持续。", 20, "#FFD9A8"))

# ===== 脚注 =====
S.append(text(28, 964, "口径：净收入 = 收入 − 退款金额；经营利润 = 净收入 − 经营成本；退款率 = 退款金额 ÷ 退款前收入；总体转化率 = 总订单 ÷ 总访问次数（非月度平均）。数据来源：monthly.csv。", 16, "#7E94BC"))

DSL = ('<Snapshot background="#0B1526" type="png">\n'
       + "<Stack>\n" + "\n".join(S) + "\n</Stack>\n</Snapshot>\n")

(OUT / "operations.snapshot").write_text(DSL, encoding="utf-8")

# ---------- 4) computed-data.json ----------
axes = [
    {"chart": "grouped-bars/revenue-profit", "unit": "万元", "min": 0, "max": 24.0,
     "zero_line_y_px": 586, "pixel_range_y": [306, 586],
     "mapping": "y_px = 586 - (value_wan / 24.0) * 280；第 i 月组中心 x_px = 112.0 + (i + 0.5) * 152.0",
     "gridlines_wan": [0, 6, 12, 18, 24]},
    {"chart": "bars/sessions", "unit": "次数", "min": 0, "max": 6000,
     "zero_line_y_px": 398, "pixel_range_y": [300, 398],
     "mapping": "y_px = 398 - (v / 6000) * 98；第 i 月中心 x_px = 1152.0 + (i + 0.5) * 66.667",
     "gridlines_count": [0, 3000, 6000]},
    {"chart": "line/conversion", "unit": "%", "min": 0, "max": 12.5,
     "zero_line_y_px": 628, "pixel_range_y": [520, 628],
     "mapping": "y_px = 628 - (v / 12.5) * 108；第 i 月中心 x_px = 1152.0 + (i + 0.5) * 66.667",
     "gridlines_pct": [0, 5, 10]},
]
computed = {
    "schema_version": 1,
    "task_id": "A01",
    "path_base": "output_dir",
    "source": {"path_base": "suite_root",
               "path": "tasks/A01-operations-dashboard/inputs/monthly.csv",
               "rows_used": len(months)},
    "formulas": {
        "net_revenue": "gross_revenue - refund_amount",
        "profit": "net_revenue - operating_cost",
        "refund_rate": "refund_amount / gross_revenue",
        "conversion": "orders / sessions（月）；总体 = sum(orders) / sum(sessions)",
    },
    "months": [
        {
            "month": m["month"],
            "raw": {"orders": m["orders"], "gross_revenue": m["gross_revenue"],
                    "refund_amount": m["refund_amount"], "operating_cost": m["operating_cost"],
                    "sessions": m["sessions"]},
            "net_revenue": m["net_revenue"],
            "profit": m["profit"],
            "refund_rate": round(m["refund_rate"], 6),
            "refund_rate_display": pct2(m["refund_rate"]),
            "conversion": round(m["conversion"], 6),
            "conversion_display": pct2(m["conversion"]),
            "net_revenue_wan": round(m["net_revenue"] / 10000, 4),
            "profit_wan": round(m["profit"] / 10000, 4),
        } for m in months],
    "totals": {
        "gross_revenue": T["gross_revenue"], "refund_amount": T["refund_amount"],
        "operating_cost": T["operating_cost"], "net_revenue": T["net_revenue"],
        "profit": T["profit"], "orders": T["orders"], "sessions": T["sessions"],
        "overall_conversion": round(T["overall_conversion"], 6),
        "overall_conversion_display": pct2(T["overall_conversion"]),
        "overall_conversion_formula": "total_orders / total_sessions（非月度平均）",
        "profit_margin_display": pct2(T["profit_margin"]),
        "sept_net_revenue_mom_display": pct1_delta(net_delta),
        "sept_orders_mom_display": pct1_delta(orders_delta),
    },
    "axes": axes,
    "conclusion": {
        "text_lines": [
            "管理结论：9 月净收入 20.24 万元、经营利润 6.44 万元为期间最高（净收入环比 +17.0%）；期间总体转化率 11.15%（3,045 单 ÷ 27,300 访问）。",
            "风险：6 月与 8 月退款率升至 8.00%（其余月份 4.00%–5.00%），8 月退款 1.50 万元；建议优先排查 8 月售后链路，并验证 9 月回落至 4.00% 是否持续。",
        ],
        "refs": {
            "sept_net_revenue": months[-1]["net_revenue"], "sept_profit": months[-1]["profit"],
            "sept_net_mom": round(net_delta, 6), "overall_conversion": round(T["overall_conversion"], 6),
            "overall_orders": T["orders"], "overall_sessions": T["sessions"],
            "high_refund_months": [m["month"] for m in months if m["refund_rate"] >= 0.075],
            "high_refund_rate": 0.08, "other_refund_rates": [0.04, 0.05],
            "aug_refund_amount": months[4]["refund_amount"], "sept_refund_rate": round(months[-1]["refund_rate"], 6),
        },
    },
}
(OUT / "computed-data.json").write_text(json.dumps(computed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("DSL bytes:", len(DSL.encode("utf-8")))
print("total net:", T["net_revenue"], "profit:", T["profit"], "conv:", pct2(T["overall_conversion"]))
