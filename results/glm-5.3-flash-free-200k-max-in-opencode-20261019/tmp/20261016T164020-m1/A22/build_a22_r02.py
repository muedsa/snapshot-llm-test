# -*- coding: utf-8 -*-
"""A22 round-02 · 财务更正后重算（2026-08 refund=25048；2026-09 cost=208000）。

在 r1 版式上重算：柱图加负轴范围（−4..24 万）表达 2026-09 经营利润 −5,632 元；
主区域边界 ±2px、主字体与视觉系统不变；表格红色高亮负利润/峰值退款率。
不修改原始 CSV。
"""
import csv
import json
import os
from pathlib import Path

TASK_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ["SNAPSHOT_RUN_ID"]
IT = TASK_ROOT / "outputs" / RUN_ID / "A22" / "round-02"
IT.mkdir(parents=True, exist_ok=True)

FONT = "Noto Sans CJK SC"
FONT_NUM = "Inter"
FAM_NUM = "Inter," + FONT
sep = lambda v: f"{v:,}"
pct2 = lambda v: f"{v * 100:.2f}%"

# ---------- 数据（r1 CSV + 轮次更正；不改写原 CSV） ----------
DIFFS = {
    ("2026-08", "refund_amount"): (15048, 25048),
    ("2026-09", "operating_cost"): (138000, 208000),
}
rows = list(csv.DictReader((TASK_ROOT / "tasks" / "A22-staged-data-correction"
                            / "inputs" / "monthly.csv").open(encoding="utf-8")))
months = []
for r in rows:
    o = int(r["orders"]); gr = int(r["gross_revenue"]); rf = int(r["refund_amount"])
    oc = int(r["operating_cost"]); se = int(r["sessions"])
    for (m0, key), (old, new) in DIFFS.items():
        if r["month"] == m0:
            if key == "refund_amount":
                rf = new
            else:
                oc = new
    months.append({"month": r["month"], "orders": o, "gross_revenue": gr,
                   "refund_amount": rf, "operating_cost": oc, "sessions": se,
                   "net_revenue": gr - rf, "profit": gr - rf - oc,
                   "refund_rate": rf / gr, "conversion": o / se})
assert months[4]["refund_amount"] == 25048 and months[5]["operating_cost"] == 208000
T = {k: sum(m[k] for m in months)
     for k in ("gross_revenue", "refund_amount", "operating_cost", "orders", "sessions")}
T["net_revenue"] = T["gross_revenue"] - T["refund_amount"]
T["profit"] = T["net_revenue"] - T["operating_cost"]
T["overall_conversion"] = T["orders"] / T["sessions"]
T["profit_margin"] = T["profit"] / T["net_revenue"]
net_delta = months[-1]["net_revenue"] / months[-2]["net_revenue"] - 1
RR_MAX = max(m["refund_rate"] for m in months)
RR_MAX_MS = "、".join(m["month"] for m in months if abs(m["refund_rate"] - RR_MAX) < 1e-9)
NEG_MS = [m["month"] for m in months if m["profit"] < 0]

r1c = json.load(open(TASK_ROOT / "outputs" / RUN_ID / "A22" / "round-01"
                     / "computed-data.json", encoding="utf-8"))
r1_profit = r1c["totals"]["profit"]
profit_drop = T["profit"] / r1_profit - 1

# ---------- DSL 发射器（同 r1 视觉系统） ----------
CYAN = "#4CC2FF"; AMBER = "#FFC154"; GREEN = "#3FD9A4"; RED = "#FF8A80"
TXT = "#EAF3FF"; SUB = "#A9BFDF"; MUT = "#8FA8CE"
PANEL = "#12203A"; PBORDER = "#23375C"; GRID = "#27395F"; AXLINE = "#33507F"
BG = "#0B1526"
ORIGIN = [0, 0]


def fnum(v):
    s = f"{float(v):.2f}".rstrip("0").rstrip(".")
    return s if s else "0"


def p(x, y):
    return x - ORIGIN[0], y - ORIGIN[1]


def content_of(ox, oy, children):
    prev = tuple(ORIGIN)
    ORIGIN[0], ORIGIN[1] = ox, oy
    try:
        return children()
    finally:
        ORIGIN[0], ORIGIN[1] = prev


def rect(x, y, w, h, color=None, radius=None, border="1 SOLID #23375C"):
    lx, ly = p(x, y)
    a = f'<Container width="{fnum(w)}" height="{fnum(h)}"'
    if color:
        a += f' color="{color}"'
    if radius is not None and radius > 0:
        a += f' borderRadius="{fnum(radius)}"'
    if radius is not None and radius > 0 and border:
        a += f' border="{border}"'
    return (f'<Positioned left="{fnum(lx)}" top="{fnum(ly)}" width="{fnum(w)}"'
            f' height="{fnum(h)}">' + a + " /></Positioned>")


def text(x, y, content, size, color, family=FONT, bold=False, align="START", box_w=None):
    lx, ly = p(x, y)
    sty = f'<Text fontSize="{fnum(size)}" color="{color}" fontFamily="{family}"'
    if bold:
        sty += ' fontStyle="BOLD"'
    sty += ' maxLines="1" overflow="CLIP"'
    if align != "START":
        sty += f' textAlign="{align}"'
    sty += f'>{content}</Text>'
    if box_w is None:
        return f'<Positioned left="{fnum(lx)}" top="{fnum(ly)}">{sty}</Positioned>'
    return (f'<Positioned left="{fnum(lx)}" top="{fnum(ly)}" width="{fnum(box_w)}">'
            + sty + "</Positioned>")


def circle(x, y, d, color):
    lx, ly = p(x, y)
    return (f'<Positioned left="{fnum(lx)}" top="{fnum(ly)}" width="{fnum(d)}" '
            f'height="{fnum(d)}"><Container width="{fnum(d)}" height="{fnum(d)}" '
            f'shape="CIRCLE" color="{color}" /></Positioned>')


def panel(x, y, w, h, children):
    inner = f'<SizedBox width="{fnum(w)}" height="{fnum(h)}" />' + "".join(children)
    return (f'<Positioned left="{fnum(x)}" top="{fnum(y)}" width="{fnum(w)}" '
            f'height="{fnum(h)}"><Container width="{fnum(w)}" height="{fnum(h)}" '
            f'color="{PANEL}" border="1 SOLID {PBORDER}" borderRadius="14">'
            f'<Stack>{inner}</Stack></Container></Positioned>')


S = ['<SizedBox width="1600" height="1000" />']
REGIONS = []

# ---- 头部（同 r1 边界） ----
S.append(rect(28, 28, 44, 44, "#4CC2FF", 10))
S.append('<Positioned left="28" top="28" width="44" height="44">'
         '<Text fontSize="26" color="#0B1526" fontFamily="Inter" fontStyle="BOLD"'
         '>L</Text></Positioned>')
S.append(text(88, 32, "叠光 Layerlight 经营驾驶舱 · 2026-04 至 2026-09（更正）", 36, TXT,
              bold=True))
S.append(text(1070, 44, "单位：金额 元 / 万元 · 比率 %（两位小数）", 22, SUB,
              align="END", box_w=502))
REGIONS.append({"id": "R-title", "box": [28, 28, 1572, 90],
                "style": {"font_px": 36, "color": TXT, "bg": BG, "bold": True,
                          "title_suffix": "（更正）"}})

# ---- KPI 卡（边界同 r1） ----
kpis = [
    ("总净收入", f"{sep(T['net_revenue'])} 元", f"总退款 {sep(T['refund_amount'])} 元", CYAN),
    ("总经营利润", f"{sep(T['profit'])} 元", f"经营成本 {sep(T['operating_cost'])} 元", AMBER),
    ("总订单", f"{sep(T['orders'])} 单", f"总访问 {sep(T['sessions'])} 次", GREEN),
    ("总体转化率", pct2(T["overall_conversion"]),
     f"{sep(T['orders'])} ÷ {sep(T['sessions'])}（非月均）", "#B98CFF"),
]
KPI_Y, KPI_H, KPI_W = 108, 118, 371
for i, (label, value, sub, accent) in enumerate(kpis):
    x = 28 + i * 391
    S.append(rect(x, KPI_Y, KPI_W, KPI_H, PANEL, 14))
    S.append(rect(x, KPI_Y, 4, KPI_H, accent, None))
    S.append(text(x + 20, KPI_Y + 12, label, 22, SUB, bold=True))
    S.append(text(x + 20, KPI_Y + 44, value, 34, TXT, family=FAM_NUM, bold=True))
    S.append(text(x + 20, KPI_Y + 88, sub, 22, MUT))
REGIONS.append({"id": "R-kpi", "box": [28, 108, 1572, 226],
                "style": {"card": [391.0, 20.0], "label_px": 22, "value_px": 34,
                          "sub_px": 22, "value_color": TXT,
                          "accents": [CYAN, AMBER, GREEN, "#B98CFF"]}})

# ---- 主柱图（负轴 −4..24 万；零线在内部） ----
PX, PY, PW, PH = 28, 240, 1544, 420
plot_x0 = PX + 84
plot_w = PW - 84 - 24
plot_top = PY + 58
plot_h = 300
plot_bot = plot_top + plot_h
AXIS_MAX = 24.0
AXIS_MIN = -4.0
SPAN = AXIS_MAX - AXIS_MIN
ymap = lambda v: plot_bot - (v - AXIS_MIN) / SPAN * plot_h
zero_y = ymap(0)
GROUP = plot_w / 6.0
BAR_W, PAIR_GAP = 58, 10


def build_chart():
    ch = []
    ch.append(text(PX + 24, PY + 14, "净收入与经营利润（万元，共轴；含负利润月份）",
                   24, TXT, bold=True))
    lx = PX + PW - 24 - 340
    ch.append(circle(lx, PY + 22, 14, CYAN))
    ch.append(text(lx + 20, PY + 19, "净收入", 22, SUB))
    ch.append(circle(lx + 130, PY + 22, 14, AMBER))
    ch.append(text(lx + 150, PY + 19, "经营利润", 22, SUB))
    for g in (-4, 0, 4, 8, 12, 16, 20, 24):
        ch.append(text(PX + 14, ymap(g) - 13, str(g), 22, MUT,
                       align="END", box_w=(plot_x0 - PX - 20)))
        if g != 0:
            ch.append(rect(plot_x0, ymap(g), plot_w, 1, GRID))
    ch.append(rect(plot_x0, plot_bot, plot_w, 2, AXLINE))
    ch.append(rect(plot_x0, zero_y - 1, plot_w, 2, AXLINE))     # 零线强调
    ch.append(text(30, PY + 59, "万元", 22, MUT))
    for i, m in enumerate(months):
        cx = plot_x0 + (i + 0.5) * GROUP
        xv = m["net_revenue"] / 10000
        pv = m["profit"] / 10000
        x_net = cx - (BAR_W * 2 + PAIR_GAP) / 2
        x_pro = x_net + BAR_W + PAIR_GAP
        # 双系列：正柱零线向上、负柱零线向下（真实高度=|v|/SPAN×plot_h）
        for (x0, v, cpos, lpos) in ((x_net, xv, CYAN, "#BFE7FF"),
                                    (x_pro, pv, AMBER, "#FFD98F")):
            if v >= 0:
                bh = v / SPAN * plot_h
                top = zero_y - bh
                txt_y, txt_c = top - 32, lpos
                extra = ' borderRadiusTopLeft="6" borderRadiusTopRight="6"'
            else:
                bh = (0 - v) / SPAN * plot_h
                top = zero_y
                txt_y, txt_c = top + 6, RED
                extra = ""
            col = cpos if v >= 0 else RED
            ch.append(f'<Positioned left="{fnum(p(x0, 0)[0])}" top="{fnum(p(0, top)[1])}"'
                      f' width="{BAR_W}" height="{fnum(bh)}">'
                      f'<Container width="{BAR_W}" height="{fnum(bh)}" color="{col}"'
                      f'{extra} /></Positioned>')
            ch.append(text(x0 + BAR_W / 2 - 55, txt_y, f"{v:.2f}", 22, txt_c,
                           family=FAM_NUM, bold=True, align="CENTER", box_w=110))
        ch.append(text(cx - 70, plot_bot + 10, m["month"], 22, SUB,
                       align="CENTER", box_w=140))
    return ch


S.append(panel(PX, PY, PW, PH, content_of(PX, PY, build_chart)))
REGIONS.append({"id": "R-chart", "box": [PX, PY, PX + PW, PY + PH],
                "style": {"title_px": 24, "label_px": 22, "axis_px": 22,
                          "plot": [plot_x0, plot_top, plot_x0 + plot_w, plot_bot],
                          "axis_unit": "万元", "axis_min": AXIS_MIN, "axis_max": AXIS_MAX,
                          "gridlines_wan": [-4, 0, 4, 8, 12, 16, 20, 24],
                          "zero_line_y_px": round(zero_y, 3),
                          "mapping": f"y_px = {plot_bot} - ((v - ({AXIS_MIN}f))/{SPAN:f})*{plot_h}",
                          "series": {"net": CYAN, "profit_positive": AMBER,
                                     "profit_negative": RED},
                          "bar": {"width": BAR_W, "pair_gap": PAIR_GAP}}})

# ---- 表格（同 r1 边界） ----
TB_Y, TB_H = 676, 210
cols = [("月份", 220, "START"), ("净收入（元）", 400, "END"),
        ("经营利润（元）", 400, "END"), ("退款率", 260, "END"), ("转化率", 264, "END")]
S.append(rect(28, TB_Y, 1544, TB_H, "#0F1C35", 10))
S.append(rect(28, TB_Y, 1544, 34, "#16284A", 10))
S.append(rect(28, TB_Y, 4, TB_H, CYAN, 10))
hdr_h = 34
row_h = (TB_H - hdr_h) / 6.0
for ci, (label, wc, al) in enumerate(cols):
    cx0 = 28 + sum(c[1] for c in cols[:ci])
    S.append(text(cx0 + 16, TB_Y + 4, label, 22, "#8FA8CE", bold=True, align=al,
                  box_w=(wc - 32)))
S.append(rect(32, TB_Y + hdr_h - 2, 1536, 2, "#2A3E63"))
for ri, m in enumerate(months):
    ry = TB_Y + hdr_h + ri * row_h
    if ri % 2 == 1:
        S.append(rect(32, ry, 1536, row_h, "#152744", None))
    rr = m["refund_rate"]
    ref_c = RED if rr >= 0.075 else (GREEN if rr <= 0.045 else TXT)
    cells = [(0, m["month"], TXT, False), (1, sep(m["net_revenue"]), TXT, False),
             (2, sep(m["profit"]), RED if m["profit"] < 0 else TXT, m["profit"] < 0),
             (3, pct2(rr), ref_c, rr >= 0.075),
             (4, pct2(m["conversion"]), TXT, False)]
    for ci, content, col, bold in cells:
        wc, al = cols[ci][1], cols[ci][2]
        cx0 = 28 + sum(c[1] for c in cols[:ci])
        S.append(text(cx0 + 16, ry + (row_h - 32) / 2, content, 22, col,
                      family=(FAM_NUM if ci == 0 else FONT), bold=bold,
                      align=al, box_w=(wc - 32)))
    if ri:
        S.append(rect(32, ry, 1536, 1, "#1D2E52"))
REGIONS.append({"id": "R-table", "box": [28, TB_Y, 1572, TB_Y + TB_H],
                "style": {"font_px": 22, "header_px": 22, "header_bg": "#16284A",
                          "zebra": "#152744", "accent": CYAN,
                          "columns": [[c[0], c[1], c[2]] for c in cols],
                          "row_h": f"{row_h:.3f}（未舍入），hdr 34"}})

# ---- 结论 + 口径 ----
CC_Y = 900
S.append(rect(28, CC_Y, 1544, 64, "#142446", 12))
S.append(rect(28, CC_Y, 6, 64, "#FFB454", 12))
S.append(text(52, CC_Y + 8,
              f"管理结论：2026-09 经营利润 {sep(months[-1]['profit'])} 元为期间唯一负值；"
              f"最高净收入 {sep(months[-1]['net_revenue'])} 元（环比 +{net_delta * 100:.2f}%）；"
              f"总体转化率 {pct2(T['overall_conversion'])}。", 22, TXT))
S.append(text(52, CC_Y + 36,
              f"校正影响：8 月退款 25,048 元 → 净收入 163,052、退款率 {pct2(RR_MAX)}（峰值）；"
              f"9 月经营成本 208,000 → 利润 −5,632；期间利润 {sep(r1_profit)} → "
              f"{sep(T['profit'])}（{profit_drop * 100:.2f}%）。", 22, "#FFD9A8"))
S.append(text(28, 972,
              "口径：同 r1；本轮仅更正 2026-08 退款与 2026-09 经营成本，"
              "monthly.csv 原样未改，负利润以负轴真实画出。", 22, "#7E94BC"))
REGIONS.append({"id": "R-conclusion", "box": [28, 900, 1572, 964],
                "style": {"font_px": 22, "accent": "#FFB454"}})
REGIONS.append({"id": "R-footnote", "box": [28, 968, 1572, 996],
                "style": {"font_px": 22, "color": "#7E94BC"}})

DSL = ('<Snapshot background="' + BG + '" type="png">\n'
       + "<Stack>\n" + "\n".join(S) + "\n</Stack>\n</Snapshot>\n")
(IT / "dashboard.snapshot").write_text(DSL, encoding="utf-8")
print("r2 dashboard.snapshot written:", len(DSL))

# ---------- computed-data.json ----------
applied = []
for (month, key), (old, new) in DIFFS.items():
    col = {"refund_amount": "refund_amount", "operating_cost": "operating_cost"}[key]
    applied.append({"field": f"{month}.{col}", "old": old, "new": new,
                    "source": "rounds/round-02.md（r2 预置更正）"})
monthly_json = []
for i, m in enumerate(months):
    d = {"month": m["month"],
         "raw": {"orders": m["orders"], "gross_revenue": m["gross_revenue"],
                 "refund_amount": m["refund_amount"], "operating_cost": m["operating_cost"],
                 "sessions": m["sessions"]},
         "net_revenue": m["net_revenue"], "profit": m["profit"],
         "refund_rate": m["refund_rate"], "refund_rate_display": pct2(m["refund_rate"]),
         "conversion": m["conversion"], "conversion_display": pct2(m["conversion"]),
         "net_revenue_wan": round(m["net_revenue"] / 10000, 4),
         "profit_wan": round(m["profit"] / 10000, 4)}
    monthly_json.append(d)
computed = {
    "schema_version": 1, "task_id": "A22", "path_base": "output_dir", "round": 2,
    "source": {"path_base": "suite_root",
               "path": "tasks/A22-staged-data-correction/inputs/monthly.csv",
               "rows_used": len(months)},
    "applied_changes": applied,
    "formulas": r1c["formulas"],
    "months": monthly_json,
    "totals": {
        "period": ["2026-04", "2026-09"], "months_count": 6,
        "gross_revenue": T["gross_revenue"], "refund_amount": T["refund_amount"],
        "operating_cost": T["operating_cost"], "net_revenue": T["net_revenue"],
        "profit": T["profit"], "orders": T["orders"], "sessions": T["sessions"],
        "overall_conversion": T["overall_conversion"],
        "overall_conversion_display": pct2(T["overall_conversion"]),
        "overall_conversion_formula": "总订单/总访问（非月均）",
        "profit_margin": T["profit_margin"],
        "profit_margin_display": pct2(T["profit_margin"]),
        "profit_change_vs_r1_display": pct2(profit_drop) + "（相对 r1）",
    },
    "axes": {
        "chart": "grouped-bars/revenue-profit", "unit": "万元",
        "min": AXIS_MIN, "max": AXIS_MAX,
        "zero_line_y_px": round(zero_y, 3),
        "pixel_range_y": [plot_top, plot_bot],
        "mapping": f"y_px = {plot_bot} - ((v + 4)/28.0)*{plot_h}；"
                   f"组中心 x_px = {plot_x0} + (i+0.5)*{GROUP:.3f}",
        "gridlines_wan": [-4, 0, 4, 8, 12, 16, 20, 24], "negative_axis": True,
        "negative_reason": f"{NEG_MS[0]} 经营利润 −5,632 元（−0.5632 万元）为真实负值",
        "rounding": "展示前用未舍入值定柱高/位置；柱标签四舍五入两位小数"
    },
    "conclusion": {
        "text_lines": [
            f"管理结论：2026-09 经营利润 {sep(months[-1]['profit'])} 元为期间唯一负值；"
            f"最高净收入 {sep(months[-1]['net_revenue'])} 元（环比 +{net_delta * 100:.2f}%）；"
            f"总体转化率 {pct2(T['overall_conversion'])}。",
            f"校正影响：8 月退款 25,048 元 → 净收入 163,052、退款率 {pct2(RR_MAX)}（峰值）；"
            f"9 月经营成本 208,000 → 利润 −5,632；期间利润 {sep(r1_profit)} → "
            f"{sep(T['profit'])}（{profit_drop * 100:.2f}%）。"],
        "refs": {"negative_profit_month": NEG_MS[0],
                 "negative_profit": months[-1]["profit"],
                 "aug_refund_rate": months[4]["refund_rate"],
                 "profit_after": T["profit"], "profit_before": r1_profit,
                 "profit_change": profit_drop},
        "supported_only_by_actual_values": True,
    },
}
with (IT / "computed-data.json").open("w", encoding="utf-8", newline="\n") as f:
    json.dump(computed, f, ensure_ascii=False, indent=1)

layout = {
    "schema_version": 1, "task_id": "A22", "path_base": "output_dir", "round": 2,
    "canvas": [1600, 1000],
    "regions": REGIONS,
    "comparison": [],   # finalize_r2 填：与 r1 layout-map 逐区域分量差
    "notes": "边界同 r1 ±2px；柱图内部刻度改为 −4..24（含零线强调），属允许重排。",
}
with (IT / "layout-map.json").open("w", encoding="utf-8", newline="\n") as f:
    json.dump(layout, f, ensure_ascii=False, indent=1)
print("KPI r2:", T["net_revenue"], T["profit"], T["orders"], pct2(T["overall_conversion"]))
print("negative months:", NEG_MS, "| zero_y:", round(zero_y, 3))
