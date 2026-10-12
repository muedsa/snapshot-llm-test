"""A01 generator: compute metrics from inputs/monthly.csv and emit the dashboard DSL.

Run from the suite root. Requires SNAPSHOT_RUN_ID (and optional DSL_VERSION).
Layout uses absolute canvas coordinates; pos()/rect() add the current card origin
stored in CUR so chart internals can be written relative to their own card.
"""
import csv
import json
import math
import os
from pathlib import Path

root = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
rid = os.environ["SNAPSHOT_RUN_ID"]
task = "A01"
inp = root / "tasks" / "A01-operations-dashboard" / "inputs" / "monthly.csv"
temp = root / "tmp" / rid / task
out = root / "outputs" / rid / task
temp.mkdir(parents=True, exist_ok=True)
out.mkdir(parents=True, exist_ok=True)

rows = list(csv.DictReader(inp.open(encoding="utf-8")))
months = []
for r in rows:
    gross = int(r["gross_revenue"]); ref = int(r["refund_amount"])
    cost = int(r["operating_cost"]); orders = int(r["orders"]); sess = int(r["sessions"])
    net = gross - ref
    profit = net - cost
    months.append({
        "month": r["month"], "orders": orders, "gross_revenue": gross,
        "refund_amount": ref, "operating_cost": cost, "sessions": sess,
        "net_revenue": net, "operating_profit": profit,
        "refund_rate": round(ref / gross, 6),
        "conversion_rate": round(orders / sess, 6),
        "profit_margin": round(profit / net, 6),
        "cost_ratio": round(cost / net, 6),
    })

T = {k: sum(m[k] for m in months) for k in
     ("orders", "gross_revenue", "refund_amount", "operating_cost", "sessions",
      "net_revenue", "operating_profit")}
T["overall_conversion_rate"] = round(T["orders"] / T["sessions"], 6)
T["overall_refund_rate"] = round(T["refund_amount"] / T["gross_revenue"], 6)
T["overall_profit_margin"] = round(T["operating_profit"] / T["net_revenue"], 6)
T["mean_of_monthly_conversion"] = round(
    sum(m["conversion_rate"] for m in months) / len(months), 6)

growth_net = months[-1]["net_revenue"] / months[0]["net_revenue"] - 1
growth_sess = months[-1]["sessions"] / months[0]["sessions"] - 1
growth_orders = months[-1]["orders"] / months[0]["orders"] - 1
conv_pp = (months[-1]["conversion_rate"] - months[0]["conversion_rate"]) * 100

BAR_MAX = 240000
BAR_TICKS = [0, 60000, 120000, 180000, 240000]
SESS_MAX = 6000
SESS_TICKS = [0, 2000, 4000, 6000]
CONV_LO, CONV_HI = 0.09, 0.13
CONV_TICKS = [0.09, 0.11, 0.13]

C = {"card": "#121E38", "border": "#1E2E4F", "grid": "#1E2E4F", "axis": "#3A4C70",
     "t0": "#F1F5F9", "t1": "#A9B8D0", "t2": "#7A8AA6",
     "cyan": "#38BDF8", "amber": "#FBBF24", "green": "#34D399",
     "red": "#F87171", "violet": "#A78BFA", "teal": "#2DD4BF", "row": "#0F1A31"}
FONT = "Inter,Noto Sans CJK SC"

P = []
CUR = [0.0, 0.0]


def n(v):
    return f"{round(float(v), 1):g}"


def pos(x, y, w, h, inner):
    P.append(f'<Positioned left="{n(CUR[0] + x)}" top="{n(CUR[1] + y)}" '
             f'width="{n(w)}" height="{n(h)}">{inner}</Positioned>')


def rect(x, y, w, h, color, radius=None):
    pos(x, y, w, h, f'<Container width="{n(w)}" height="{n(h)}" color="{color}"'
        + (f' borderRadius="{radius}"' if radius is not None else "") + "/>")


def txt(s, color=None, size=20, style=None, align=None, maxlines=None, height=None):
    color = color or C["t0"]
    a = f'color="{color}" fontSize="{size}" fontFamily="{FONT}"'
    if style:
        a += f' fontStyle="{style}"'
    if align:
        a += f' textAlign="{align}"'
    if maxlines:
        a += f' maxLines="{maxlines}"'
    if height:
        a += f' height="{height}"'
    return f"<Text {a}>{s}</Text>"


def spacer(w, h):
    return f'<Container width="{n(w)}" height="{n(h)}"/>'


def box(w, h, color=None, radius=None, border=None, align=None, pad=None, inner=None,
        shadow=None):
    a = f'width="{n(w)}" height="{n(h)}"'
    if color:
        a += f' color="{color}"'
    if radius is not None:
        a += f' borderRadius="{radius}"'
    if border:
        a += f' border="{border}"'
    if align:
        a += f' alignment="{align}"'
    if pad:
        a += f' padding="{pad}"'
    if shadow:
        a += f' boxShadow="{shadow}"'
    return f"<Container {a}>{inner}</Container>" if inner else f"<Container {a}/>"


def card(w, h, inner=None, pad=None, align=None):
    return box(w, h, color=C["card"], radius=14, border=f"1 SOLID {C['border']}",
               inner=inner, pad=pad, align=align)


def label(x, y, w, h, s, color=None, size=20, style=None, align="START", valign=None):
    """text block anchored in the current card; valign 'TOP' pins to the top edge"""
    inner = txt(s, color, size, style, align=align if align != "START" else None)
    if valign == "TOP":
        va = {"START": "TOP_LEFT", "END": "TOP_RIGHT", "CENTER": "TOP_CENTER"}[align]
    else:
        va = {"START": "CENTER_LEFT", "END": "CENTER_RIGHT", "CENTER": "CENTER"}[align]
    pos(x, y, w, h, box(w, h, inner=inner, align=va))


# ============ background ============
P.append('<Container width="1600" height="1000" gradientType="LINEAR"'
         ' gradientColors="#060B18,#0C1730,#060B18" gradientBegin="TOP_LEFT"'
         ' gradientEnd="BOTTOM_RIGHT"/>')

# ============ header ============
CUR[:] = [0, 0]
hdr = ('<Row mainAxisAlignment="SPACE_BETWEEN" crossAxisAlignment="START">'
       '<Column crossAxisAlignment="START">'
       + txt("NORTHSTAR · 经营诊断驾驶舱", C["t0"], 34, "BOLD")
       + spacer(4, 8)
       + txt("统计期间 2026-04 至 2026-09　·　金额单位：元　·　数据源：inputs/monthly.csv",
             C["t1"], 20)
       + '</Column>'
       '<Column crossAxisAlignment="END">'
       + txt("净收入 = 退款前收入 − 退款　·　经营利润 = 净收入 − 经营成本", C["t1"], 20)
       + spacer(4, 8)
       + txt("总体转化率 = 总订单 ÷ 总访问次数（加权，不平均月比例）", C["t2"], 18)
       + '</Column></Row>')
pos(48, 28, 1504, 78, hdr)

# ============ KPI row ============
kpis = [
    ("总净收入", f'{T["net_revenue"]:,} 元', f'{T["net_revenue"]/10000:.2f} 万元',
     f'9 月单月较 4 月 +{growth_net*100:.1f}%', C["cyan"]),
    ("总经营利润", f'{T["operating_profit"]:,} 元', f'{T["operating_profit"]/10000:.2f} 万元',
     f'整体利润率 {T["overall_profit_margin"]*100:.2f}%', C["amber"]),
    ("总订单", f'{T["orders"]:,} 笔', f'同期访问 {T["sessions"]:,} 次',
     f'订单量较 4 月 +{growth_orders*100:.1f}%', C["violet"]),
    ("期间总体转化率", f'{T["overall_conversion_rate"]*100:.2f}%',
     f'月度简单均值 {T["mean_of_monthly_conversion"]*100:.2f}%（仅对照）',
     f'4 月 12.00% → 9 月 {months[-1]["conversion_rate"]*100:.2f}%', C["teal"]),
]
KW, GAP = 352, 32
for i, (lab, v1, v2, note, col) in enumerate(kpis):
    x = 48 + i * (KW + GAP)
    inner = ('<Column crossAxisAlignment="START">'
             + txt(lab, C["t1"], 20, "BOLD") + spacer(4, 4)
             + txt(v1, col, 30, "BOLD") + spacer(4, 2)
             + txt(v2, C["t1"], 20) + spacer(4, 4)
             + txt(note, C["t2"], 16) + '</Column>')
    body = ('<Row crossAxisAlignment="CENTER">'
            + box(6, 116, color=col, radius=3) + spacer(16, 1)
            + '<Expanded><Container alignment="CENTER_LEFT">' + inner
            + '</Container></Expanded></Row>')
    pos(x, 114, KW, 156, card(KW, 156, inner=body, pad="(0,14,0,14)"))

# ============ grouped bar chart ============
CX, CY, CW, CH = 48, 278, 900, 390
PL, PT, PW, PH = 96, 94, 776, 222
BASE = PT + PH
sc = PH / BAR_MAX
CUR[:] = [CX, CY]
pos(0, 0, CW, CH, card(CW, CH))
label(24, 16, 560, 30, "净收入与经营利润（元）", C["t0"], 24, "BOLD", "START")
label(24, 50, 620, 24, "两组柱共用零起点与同一比例，刻度以 6 万元递进", C["t2"], 18,
      None, "START")
leg = ('<Row crossAxisAlignment="CENTER">'
       + box(16, 16, color=C["cyan"], radius=4) + spacer(8, 1) + txt("净收入", C["t1"], 20)
       + spacer(22, 1) + box(16, 16, color=C["amber"], radius=4) + spacer(8, 1)
       + txt("经营利润", C["t1"], 20) + '</Row>')
pos(664, 18, 212, 28, leg)
for tv in BAR_TICKS:
    y = BASE - tv * sc
    rect(PL, y, PW, 1, C["grid"])
    lbl = "0" if tv == 0 else f"{tv//10000}万"
    label(14, y - 12, 68, 24, lbl, C["t2"], 20, None, "END")
gw = PW / 6
bw, bgap = 44, 10
pair = bw * 2 + bgap
for i, m in enumerate(months):
    gx = PL + gw * i + (gw - pair) / 2
    for key, col, off in (("net_revenue", C["cyan"], 0),
                          ("operating_profit", C["amber"], bw + bgap)):
        h = m[key] * sc
        rect(gx + off, BASE - h, bw, h, col, 4)
        val = m[key] / 10000
        label(gx + off - 14, BASE - h - 26, bw + 28, 22, f"{val:.1f}", col, 18,
              "BOLD", "CENTER")
    label(PL + gw * i, BASE + 10, gw, 26, m["month"], C["t1"], 18, None, "CENTER")
rect(PL, BASE, PW, 2, C["axis"])
label(PL, BASE + 42, PW, 22, "柱高按“元”线性映射；柱顶数值标签单位为万元", C["t2"],
      16, None, "CENTER")

# ============ small chart A: sessions ============
SX, SY, SW, SH = 976, 278, 528, 190
SPL, SPT, SPW, SPH = 66, 62, 438, 76
SBASE = SPT + SPH
CUR[:] = [SX, SY]
pos(0, 0, SW, SH, card(SW, SH))
label(20, 12, 260, 26, "访问量（次）", C["t0"], 22, "BOLD", "START")
label(280, 14, 228, 24, f'总访问 {T["sessions"]:,} 次', C["t2"], 18, None, "END")
for tv in SESS_TICKS:
    y = SBASE - tv / SESS_MAX * SPH
    rect(SPL, y, SPW, 1, C["grid"])
    label(0, y - 12, 58, 24, f"{tv:,}", C["t2"], 20, None, "END")
gw2 = SPW / 6
bw2 = 34
for i, m in enumerate(months):
    h = m["sessions"] / SESS_MAX * SPH
    x = SPL + gw2 * i + (gw2 - bw2) / 2
    rect(x, SBASE - h, bw2, h, C["violet"], 3)
    label(x - 16, SBASE - h - 20, bw2 + 32, 18, f'{m["sessions"]:,}', C["t1"], 16,
          None, "CENTER")
    label(SPL + gw2 * i, SBASE + 6, gw2, 22, m["month"][5:7] + "月", C["t2"], 16,
          None, "CENTER")
rect(SPL, SBASE, SPW, 2, C["axis"])

# ============ small chart B: conversion ============
TX, TY = 976, 478
CUR[:] = [SX, TY]
pos(0, 0, SW, SH, card(SW, SH))
base2 = SPT + SPH
label(20, 12, 300, 26, "月度转化率（%）", C["t0"], 22, "BOLD", "START")
label(280, 14, 228, 24, f'总体 {T["overall_conversion_rate"]*100:.2f}%（加权）',
      C["green"], 18, None, "END")
for tv in CONV_TICKS:
    y = base2 - (tv - CONV_LO) / (CONV_HI - CONV_LO) * SPH
    rect(SPL, y, SPW, 1, C["grid"])
    label(0, y - 12, 58, 24, f"{tv*100:.0f}%", C["t2"], 20, None, "END")
pts = []
for i, m in enumerate(months):
    px = SPL + gw2 * i + gw2 / 2
    py = base2 - (m["conversion_rate"] - CONV_LO) / (CONV_HI - CONV_LO) * SPH
    pts.append((px, py, m))
for (x1, y1, _), (x2, y2, _) in zip(pts, pts[1:]):
    ln = math.hypot(x2 - x1, y2 - y1)
    co, si = (x2 - x1) / ln, (y2 - y1) / ln
    seg = (f'<Transform matrix="({co:.6f},{si:.6f},0,0,{-si:.6f},{co:.6f},0,0,'
           f'0,0,1,0,0,0,0,1)">' + box(ln, 3, color=C["green"], radius=2)
           + '</Transform>')
    pos(x1, y1 - 1.5, ln, 3, seg)
for px, py, m in pts:
    pos(px - 6, py - 6, 12, 12, box(12, 12, color=C["green"], radius=6))
    label(px - 32, py - 30, 64, 20, f'{m["conversion_rate"]*100:.2f}', C["t1"], 16,
          None, "CENTER")
for i, m in enumerate(months):
    label(SPL + gw2 * i, base2 + 6, gw2, 22, m["month"][5:7] + "月", C["t2"], 16, None,
          "CENTER")
rect(SPL, base2, SPW, 2, C["axis"])
label(SPL, base2 + 32, SPW, 20, "纵轴自 9% 起（截断轴），仅用于显示趋势", C["t2"], 16,
      None, "START")

# ============ table ============
RX, RY, RW, RH = 48, 680, 900, 288
CUR[:] = [RX, RY]
pos(0, 0, RW, RH, card(RW, RH))
cols = [("月份", 128, "START"), ("净收入(元)", 150, "END"), ("退款率", 112, "END"),
        ("经营利润(元)", 160, "END"), ("利润率", 112, "END"), ("转化率", 112, "END")]
col_x, ccx = [], 24
for name, w, al in cols:
    col_x.append((ccx, w, al))
    ccx += w + 9
label(24, 14, 520, 28, "六个月明细（金额取整数，比例保留两位小数）", C["t0"], 22, "BOLD",
      "START")
label(560, 18, 316, 24, "合计行为期间加权值", C["t2"], 18, None, "END")
rh = 28
y = 52
for (name, w, al), (x0, w2, _) in zip(cols, col_x):
    label(x0, y, w2, rh, name, C["t1"], 20, "BOLD", al)
rect(24, y + rh, RW - 48, 2, "#2B3E63")
y += rh + 2
for i, m in enumerate(months):
    if i % 2 == 1:
        rect(16, y, RW - 32, rh, C["row"])
    vals = [m["month"], f'{m["net_revenue"]:,}', f'{m["refund_rate"]*100:.2f}%',
            f'{m["operating_profit"]:,}', f'{m["profit_margin"]*100:.2f}%',
            f'{m["conversion_rate"]*100:.2f}%']
    for (v, (x0, w2, al), ci) in zip(vals, col_x, range(6)):
        col = C["t0"]
        if ci == 2:
            col = C["red"] if m["refund_rate"] >= 0.07 else (
                C["green"] if m["refund_rate"] <= 0.045 else C["t0"])
        if ci == 4 and m["profit_margin"] < 0.25:
            col = C["red"]
        label(x0, y, w2, rh, v, col, 20, None, al)
    y += rh
rect(24, y, RW - 48, 2, "#2B3E63")
y += 2
tot = ["合计", f'{T["net_revenue"]:,}', f'{T["overall_refund_rate"]*100:.2f}%',
       f'{T["operating_profit"]:,}', f'{T["overall_profit_margin"]*100:.2f}%',
       f'{T["overall_conversion_rate"]*100:.2f}%']
for (v, (x0, w2, al)) in zip(tot, col_x):
    label(x0, y, w2, rh, v, C["cyan"], 20, "BOLD", al)

# ============ conclusion ============
BX, BY, BW, BH = 976, 680, 528, 288
CUR[:] = [BX, BY]
pos(0, 0, BW, BH, card(BW, BH))
label(24, 14, 300, 28, "管理结论", C["t0"], 24, "BOLD", "START")
rect(24, 48, BW - 48, 1, "#2B3E63")
label(24, 54, BW - 48, 56,
      "① 增长由流量驱动：访问量 +60.0%、订单 +47.6%，"
      "而月度转化率从 12.00% 降至 11.07%。",
      C["t1"], 20, None, "START", "TOP")
label(24, 116, BW - 48, 84,
      "② 退款主导利润波动：6 月与 8 月退款率升至 8.00%，经营利润率同步跌到 "
      "21.99% 与 23.72%；9 月退款率回到 4.00%，利润率恢复至 31.81%。",
      C["t1"], 20, None, "START", "TOP")
rect(24, 204, BW - 48, 1, "#2B3E63")
label(24, 212, BW - 48, 64,
      "→ 建议：复核 6/8 月退款动因，把退款率稳定在 5% 以内；停止单纯加投流量，"
      "把预算转向转化路径优化。", C["green"], 20, "BOLD", "START", "TOP")

# ============ footer ============
CUR[:] = [0, 0]
pos(48, 972, 1504, 22,
    box(1504, 22, align="CENTER_LEFT",
        inner=txt("口径：净收入 = gross_revenue − refund_amount；经营利润 = 净收入 − "
                  "operating_cost；退款率 = refund_amount ÷ gross_revenue；"
                  "转化率 = orders ÷ sessions。合计与 KPI 比例按期间汇总值加权计算。",
                  C["t2"], 16)))

dsl = ('<Snapshot background="#060B18" type="png"><Container width="1600" height="1000">'
       '<Stack alignment="TOP_LEFT" clipBehavior="NONE">' + "".join(P)
       + '</Stack></Container></Snapshot>')

ver = os.environ.get("DSL_VERSION", "v01")
(temp / f"{ver}.snapshot").write_text(dsl, encoding="utf-8")

computed = {
    "task_id": "A01", "run_id": rid, "path_base": "suite_root",
    "source": "tasks/A01-operations-dashboard/inputs/monthly.csv",
    "definitions": {
        "net_revenue": "gross_revenue - refund_amount",
        "operating_profit": "net_revenue - operating_cost",
        "refund_rate": "refund_amount / gross_revenue",
        "conversion_rate": "orders / sessions",
        "profit_margin": "operating_profit / net_revenue",
        "overall_conversion_rate": "sum(orders) / sum(sessions)",
    },
    "monthly": months, "totals": T,
    "derived": {
        "net_revenue_growth_apr_to_sep": round(growth_net, 6),
        "sessions_growth_apr_to_sep": round(growth_sess, 6),
        "orders_growth_apr_to_sep": round(growth_orders, 6),
        "conversion_change_percentage_points": round(conv_pp, 4),
        "conclusion_cited_values": {
            "apr_conversion": months[0]["conversion_rate"],
            "sep_conversion": months[-1]["conversion_rate"],
            "apr_profit_margin": months[0]["profit_margin"],
            "jun_refund_rate": months[2]["refund_rate"],
            "aug_refund_rate": months[4]["refund_rate"],
            "sep_refund_rate": months[5]["refund_rate"],
            "jun_profit_margin": months[2]["profit_margin"],
            "aug_profit_margin": months[4]["profit_margin"],
            "sep_profit_margin": months[5]["profit_margin"],
            "sessions_growth": round(growth_sess, 6),
            "orders_growth": round(growth_orders, 6),
        },
    },
    "axes": {
        "grouped_bar": {"unit": "元", "kind": "linear", "zero_based": True,
                        "min": 0, "max": BAR_MAX, "ticks": BAR_TICKS,
                        "series": ["net_revenue", "operating_profit"],
                        "shared_scale": True,
                        "plot_rect_canvas": [CX + PL, CY + PT, PW, PH]},
        "sessions": {"unit": "次", "kind": "linear", "zero_based": True,
                     "min": 0, "max": SESS_MAX, "ticks": SESS_TICKS,
                     "plot_rect_canvas": [SX + SPL, SY + SPT, SPW, SPH]},
        "conversion": {"unit": "%", "kind": "linear", "zero_based": False,
                       "min": CONV_LO, "max": CONV_HI, "ticks": CONV_TICKS,
                       "truncated_axis_annotated": True,
                       "plot_rect_canvas": [SX + SPL, base2 - SPH, SPW, SPH]},
        "month_alignment_shared": {"left_edge": SPL, "width": SPW,
                                   "note": "sessions 与 conversion 使用同一 x 分组宽度"},
    },
}
(out / "computed-data.json").write_text(
    json.dumps(computed, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"wrote {ver} -> tmp/{rid}/A01/{ver}.snapshot ({len(dsl)} chars)")
