"""A01 - Northstar six-month operations dashboard (1600x1000).

Reads tasks/A01-operations-dashboard/inputs/monthly.csv, derives every figure
from it, writes computed-data.json and emits the Snapshot DSL.

Run from the suite task root:
  python tmp/<run_id>/A01/gen.py --ver v004 [--final outputs/<run_id>/A01/operations.snapshot]
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
sys.path.insert(0, str(ROOT / "tmp" / "2026-10-12T10-04Z-r001" / "_suite" / "scripts"))

from snap import (  # noqa: E402
    C, Border, Col, Container, Opacity, Positioned, Row, Snapshot, Stack, Text,
    hline, label, num, vline,
)

RUN = "2026-10-12T10-04Z-r001"
TASK = "A01"
IN_CSV = ROOT / "tasks" / "A01-operations-dashboard" / "inputs" / "monthly.csv"
OUT_DIR = ROOT / "outputs" / RUN / TASK
TMP_DIR = ROOT / "tmp" / RUN / TASK

FONT = "Noto Sans CJK SC,Inter"
FONT_MONO = "Noto Sans Mono CJK SC,DejaVu Sans Mono"

BG_TOP, BG_BOT = "#070C1C", "#0D1730"
CARD, CARD_2 = "#111C38", "#0E1830"
LINE, LINE_SOFT = "#223257", "#1A2745"
TXT, TXT_2, TXT_3 = "#F1F5FB", "#9AACC9", "#6B7E9E"
SKY, EMERALD, AMBER, ROSE, VIOLET = "#38BDF8", "#34D399", "#FBBF24", "#FB7185", "#A78BFA"


def r2(x: float) -> float:
    return round(x + 1e-12, 2)


# ---------------------------------------------------------------- data
rows = []
with IN_CSV.open(encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        o = {k: (r[k]) for k in ("month",)}
        for k in ("orders", "gross_revenue", "refund_amount", "operating_cost", "sessions"):
            o[k] = int(r[k])
        o["net_revenue"] = o["gross_revenue"] - o["refund_amount"]
        o["operating_profit"] = o["net_revenue"] - o["operating_cost"]
        o["refund_rate"] = r2(o["refund_amount"] / o["gross_revenue"] * 100)
        o["conversion_rate"] = r2(o["orders"] / o["sessions"] * 100)
        o["profit_margin"] = r2(o["operating_profit"] / o["net_revenue"] * 100)
        rows.append(o)

T = {k: sum(r[k] for r in rows) for k in
     ("orders", "gross_revenue", "refund_amount", "operating_cost", "sessions",
      "net_revenue", "operating_profit")}
T["refund_rate"] = r2(T["refund_amount"] / T["gross_revenue"] * 100)
T["conversion_rate"] = r2(T["orders"] / T["sessions"] * 100)
T["profit_margin"] = r2(T["operating_profit"] / T["net_revenue"] * 100)
T["avg_orders_per_month"] = r2(T["orders"] / len(rows))
assert sum(r["operating_profit"] for r in rows) == T["operating_profit"]

first, last = rows[0], rows[-1]
ses_g = r2((last["sessions"] - first["sessions"]) / first["sessions"] * 100)
net_g = r2((last["net_revenue"] - first["net_revenue"]) / first["net_revenue"] * 100)
min_profit_m = min(rows, key=lambda r: r["operating_profit"])
min_conv_m = min(rows, key=lambda r: r["conversion_rate"])
max_conv_m = max(rows, key=lambda r: r["conversion_rate"])
high_refund = [r for r in rows if r["refund_rate"] >= max(x["refund_rate"] for x in rows) - 1e-9]
low_refund = [r for r in rows if r not in high_refund]
HR = "、".join(r["month"] for r in high_refund)
LR_RANGE = (min(r["refund_rate"] for r in low_refund), max(r["refund_rate"] for r in low_refund))
# strongest month-over-month profit decline while net revenue still rose
drops = [
    (a, b) for a, b in zip(rows, rows[1:])
    if b["net_revenue"] > a["net_revenue"] and b["operating_profit"] < a["operating_profit"]
]
drop_prev, drop_cur = max(drops, key=lambda p: p[0]["operating_profit"] - p[1]["operating_profit"])

conclusion = {
    "headline": "增长由流量驱动，而非转化效率",
    "claim": (
        f"访问量 +{ses_g:.1f}%（{first['sessions']:,}→{last['sessions']:,} 次）带动净收入 "
        f"+{net_g:.1f}%，但期间总体转化率仅 {T['conversion_rate']:.2f}%。"
    ),
    "evidence": [
        f"总体转化率 = {T['orders']:,} 笔 ÷ {T['sessions']:,} 次 = {T['conversion_rate']:.2f}%，"
        f"低于 {first['month']} 的 {first['conversion_rate']:.2f}%。",
        f"{HR} 退款率 {high_refund[0]['refund_rate']:.2f}%，其余月份仅 "
        f"{LR_RANGE[0]:.2f}%–{LR_RANGE[1]:.2f}%（期间 {T['refund_rate']:.2f}%）。",
        f"{drop_cur['month']} 净收入 {drop_cur['net_revenue']:,} 元高于 {drop_prev['month']} 的 "
        f"{drop_prev['net_revenue']:,} 元，经营利润却由 {drop_prev['operating_profit']:,} 元降至 "
        f"{drop_cur['operating_profit']:,} 元。",
    ],
    "recommendation": (
        f"优先治理 {HR.replace('2026-', '')} 的退款成因并复核成本投放，"
        f"把目标从扩大访问转向守住 {T['conversion_rate']:.2f}% 转化与 {T['profit_margin']:.2f}% 利润率。"
    ),
    "cited_values": {
        "sessions_first": first["sessions"], "sessions_last": last["sessions"],
        "sessions_growth_pct": ses_g, "net_revenue_growth_pct": net_g,
        "period_conversion_rate_pct": T["conversion_rate"],
        "total_orders": T["orders"], "total_sessions": T["sessions"],
        "conversion_first_month_pct": first["conversion_rate"],
        "conversion_last_month_pct": last["conversion_rate"],
        "conversion_min": {"month": min_conv_m["month"], "value_pct": min_conv_m["conversion_rate"]},
        "conversion_max": {"month": max_conv_m["month"], "value_pct": max_conv_m["conversion_rate"]},
        "high_refund_months": [{"month": r["month"], "refund_rate_pct": r["refund_rate"]} for r in high_refund],
        "other_refund_rate_range_pct": [LR_RANGE[0], LR_RANGE[1]],
        "period_refund_rate_pct": T["refund_rate"],
        "profit_decline_with_revenue_growth": {
            "earlier_month": drop_prev["month"], "later_month": drop_cur["month"],
            "earlier_net_revenue": drop_prev["net_revenue"], "later_net_revenue": drop_cur["net_revenue"],
            "earlier_operating_profit": drop_prev["operating_profit"],
            "later_operating_profit": drop_cur["operating_profit"],
        },
        "lowest_profit_month": {
            "month": min_profit_m["month"], "operating_profit": min_profit_m["operating_profit"],
            "profit_margin_pct": min_profit_m["profit_margin"],
        },
        "period_profit_margin_pct": T["profit_margin"],
    },
}

# ---------------------------------------------------------------- axes
BAR_MAX, BAR_STEP = 210000, 30000
SES_MAX, SES_STEP = 7000, 2000
CONV_MAX, CONV_STEP = 15.0, 3.0

computed = {
    "task_id": TASK,
    "path_base": "output_dir",
    "source_input": "tasks/A01-operations-dashboard/inputs/monthly.csv",
    "definitions": {
        "net_revenue": "gross_revenue - refund_amount",
        "operating_profit": "net_revenue - operating_cost",
        "refund_rate_pct": "refund_amount / gross_revenue * 100",
        "conversion_rate_pct": "orders / sessions * 100",
        "profit_margin_pct": "operating_profit / net_revenue * 100",
        "period_conversion_rate_pct": "total orders / total sessions * 100 (weighted, not mean of monthly)",
        "period_refund_rate_pct": "total refund / total gross revenue * 100",
        "rounding": "rates rounded to 2 decimals for display; amounts kept as exact integers in 元",
    },
    "units": {"amount": "元", "chart_amount_axis": "万元", "orders": "笔", "sessions": "次", "rates": "%"},
    "monthly": rows,
    "totals": T,
    "axes": {
        "grouped_bar_amount": {
            "unit": "万元", "min": 0, "max": BAR_MAX, "step": BAR_STEP, "zero_baseline": True,
            "shared_by": ["net_revenue", "operating_profit"],
            "ticks": list(range(0, BAR_MAX + 1, BAR_STEP)),
            "note": "净收入与经营利润共用同一零起点与同一比例；两列均为正值，无负值区间。",
        },
        "sessions_bar": {
            "unit": "次", "min": 0, "max": SES_MAX, "step": SES_STEP, "zero_baseline": True,
            "ticks": list(range(0, SES_MAX + 1, SES_STEP)),
            "labelled_ticks": list(range(0, SES_MAX + 1, SES_STEP)),
        },
        "conversion_bar": {
            "unit": "%", "min": 0, "max": CONV_MAX, "step": CONV_STEP, "zero_baseline": True,
            "ticks": [round(CONV_STEP * i, 2) for i in range(int(CONV_MAX / CONV_STEP) + 1)],
            "labelled_ticks": [0, 6, 12],
            "reference_line_pct": T["conversion_rate"],
            "note": "百分比使用独立数轴，不与金额共用；参考线为期间总体转化率。",
        },
        "month_axis_alignment": "两个小图使用完全相同的左右内边距与等分月份槽位，逐月垂直对齐。",
    },
    "conclusion": conclusion,
}
OUT_DIR.mkdir(parents=True, exist_ok=True)
(OUT_DIR / "computed-data.json").write_text(
    json.dumps(computed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# ---------------------------------------------------------------- geometry
W, H = 1600, 1000
PAD = 32
CW = W - 2 * PAD                      # 1536
HDR_Y, HDR_H = 32, 76
KPI_Y, KPI_H = 122, 132
CHT_Y, CHT_H = 268, 302
BOT_Y, BOT_H = 584, 384
GAP = 20

MAIN_W = 972
SIDE_W = CW - MAIN_W - GAP            # 544
TABLE_W = 828
CONC_W = CW - TABLE_W - GAP           # 688


def card(x, y, w, h, *, fill=CARD, radius=18, border=LINE):
    return Positioned(
        C(width=num(w), height=num(h), color=fill, borderRadius=num(radius),
          border=f"1 SOLID {border}"),
        left=num(x), top=num(y),
    )


def top_accent(x, y, w, color):
    return Positioned(C(width=num(w - 2), height="4", color=color, borderRadius="2"),
                      left=num(x + 1), top=num(y + 1))


def layer_stack(*children, w=W, h=H, clip="HARD_EDGE"):
    return Stack(C(width=num(w), height=num(h)), *children,
                 alignment="TOP_LEFT", clipBehavior=clip)


# ---------------------------------------------------------------- header
parts = []
parts.append(
    Positioned(
        Row(
            C(width="6", height="56", color=SKY, borderRadius="3"),
            C(width="18"),
            Col(
                Text("Northstar 经营诊断驾驶舱", color=TXT, fontSize="36", fontStyle="BOLD",
                     fontFamily=FONT),
                C(height="8"),
                Text(f"{first['month']} 至 {last['month']} · 唯一业务数据 inputs/monthly.csv · 金额单位 元",
                     color=TXT_2, fontSize="20", fontFamily=FONT),
                crossAxisAlignment="START",
            ),
            crossAxisAlignment="CENTER",
        ),
        left=num(PAD), top=num(HDR_Y + 4),
    )
)
parts.append(
    Positioned(
        Row(
            C(width="12", height="12", color=SKY, shape="CIRCLE"),
            C(width="10"),
            Text(f"净收入 {T['net_revenue'] / 10000:.2f} 万元", color=TXT, fontSize="20",
                 fontFamily=FONT),
            C(width="28"),
            Text("利润率", color=TXT_3, fontSize="20", fontFamily=FONT),
            C(width="8"),
            Text(f"{T['profit_margin']:.2f}%", color=EMERALD, fontSize="22", fontStyle="BOLD",
                 fontFamily=FONT),
            crossAxisAlignment="CENTER",
        ),
        right=num(PAD), top=num(HDR_Y + 28),
    )
)

# ---------------------------------------------------------------- KPI
KPIS = [
    ("总净收入", f"{T['net_revenue'] / 10000:.2f}", "万元",
     f"{T['net_revenue']:,} 元 = {T['gross_revenue']:,} − {T['refund_amount']:,}", SKY),
    ("总经营利润", f"{T['operating_profit'] / 10000:.2f}", "万元",
     f"{T['operating_profit']:,} 元 · 利润率 {T['profit_margin']:.2f}%", EMERALD),
    ("总订单", f"{T['orders']:,}", "笔",
     f"月均 {T['avg_orders_per_month']:.1f} 笔 · 访问 {T['sessions']:,} 次", VIOLET),
    ("期间总体转化率", f"{T['conversion_rate']:.2f}", "%",
     f"{T['orders']:,} ÷ {T['sessions']:,}（加权，非月均）", AMBER),
]
KPI_W = (CW - 3 * GAP) / 4
for i, (lab, val, unit, sub, acc) in enumerate(KPIS):
    x = PAD + i * (KPI_W + GAP)
    parts.append(card(x, KPI_Y, KPI_W, KPI_H, fill=CARD_2))
    parts.append(top_accent(x, KPI_Y, KPI_W, acc))
    parts.append(
        Positioned(
            Col(
                Text(lab, color=TXT_2, fontSize="20", fontFamily=FONT),
                C(height="6"),
                Row(
                    Text(val, color=acc, fontSize="40", fontStyle="BOLD", fontFamily=FONT),
                    C(width="8"),
                    Text(unit, color=TXT_2, fontSize="20", fontFamily=FONT),
                    crossAxisAlignment="END",
                ),
                C(height="6"),
                Text(sub, color=TXT_3, fontSize="16", fontFamily=FONT),
                crossAxisAlignment="START",
            ),
            left=num(x + 22), top=num(KPI_Y + 16), width=num(KPI_W - 44),
        )
    )

# ---------------------------------------------------------------- main chart
mx, my = PAD, CHT_Y
plot_l, plot_r = mx + 82, mx + MAIN_W - 26
plot_t, plot_b = my + 80, my + 252
plot_w, plot_h = plot_r - plot_l, plot_b - plot_t
scale = plot_h / BAR_MAX
group_w = plot_w / len(rows)
BAR_W, BAR_GAP = 40, 14

mc = [card(mx, my, MAIN_W, CHT_H)]
mc.append(
    Positioned(
        Row(
            Text("净收入与经营利润 · 逐月对比", color=TXT, fontSize="24", fontStyle="BOLD",
                 fontFamily=FONT),
            C(width="16"),
            Text("纵轴单位 万元 · 两列共用零起点与同一比例", color=TXT_3, fontSize="16",
                 fontFamily=FONT),
            crossAxisAlignment="END",
        ),
        left=num(mx + 26), top=num(my + 20),
    )
)
mc.append(
    Positioned(
        Row(
            C(width="16", height="16", color=SKY, borderRadius="4"),
            C(width="8"),
            Text("净收入", color=TXT_2, fontSize="18", fontFamily=FONT),
            C(width="24"),
            C(width="16", height="16", color=EMERALD, borderRadius="4"),
            C(width="8"),
            Text("经营利润", color=TXT_2, fontSize="18", fontFamily=FONT),
            crossAxisAlignment="CENTER",
        ),
        right=num(W - (mx + MAIN_W - 26)), top=num(my + 22),
    )
)
for v in range(0, BAR_MAX + 1, BAR_STEP):
    y = plot_b - v * scale
    mc.append(hline(plot_l, plot_r, y, 1 if v else 2, LINE if v else "#3A4C73"))
    mc.append(label(plot_l - 14, y, f"{v / 10000:g}", 18, TXT_3, anchor="right",
                    align="RIGHT", width=52, font=FONT))
mc.append(vline(plot_l, plot_t - 4, plot_b, 2, "#3A4C73"))

for i, r in enumerate(rows):
    cx = plot_l + group_w * (i + 0.5)
    x0 = cx - (BAR_W * 2 + BAR_GAP) / 2
    for j, (key, colr, lab_col) in enumerate(
        (("net_revenue", SKY, "#C7E9FF"), ("operating_profit", EMERALD, "#B6F0D6"))
    ):
        v = r[key]
        h = v * scale
        bx = x0 + j * (BAR_W + BAR_GAP)
        mc.append(
            Positioned(
                C(width=num(BAR_W), height=num(h), color=colr,
                  gradientType="LINEAR", gradientColors=f"{colr},{colr}99",
                  gradientStops="0,1", gradientBegin="TOP_CENTER", gradientEnd="BOTTOM_CENTER"),
                left=num(bx), top=num(plot_b - h),
            )
        )
        mc.append(label(bx + BAR_W / 2, plot_b - h - 6, f"{v / 10000:.2f}", 18, lab_col,
                        anchor="bottom", align="CENTER", width=BAR_W + 14, font=FONT))
    mc.append(label(cx, plot_b + 10, r["month"], 20, TXT_2, anchor="top", align="CENTER",
                    width=group_w - 4, font=FONT))

# ---------------------------------------------------------------- side charts
sx = PAD + MAIN_W + GAP
SC_H = (CHT_H - 16) // 2
SC_GAP = CHT_H - 2 * SC_H
si_l, si_r = sx + 58, sx + SIDE_W - 20
si_t_off, si_b_off = 40, 114
si_w = si_r - si_l
si_h = si_b_off - si_t_off
si_gw = si_w / len(rows)


def side_chart(y, title, unit, values, vmax, vstep, labelled, color, fmt, *, ref=None,
               ref_text=None):
    inner_b = y + si_b_off
    inner_t = y + si_t_off
    sc = si_h / vmax
    gw = si_gw
    out = [card(sx, y, SIDE_W, SC_H, fill=CARD_2)]
    out.append(
        Positioned(
            Row(
                Text(title, color=TXT, fontSize="18", fontStyle="BOLD", fontFamily=FONT),
                C(width="10"),
                Text(unit, color=TXT_3, fontSize="16", fontFamily=FONT),
                crossAxisAlignment="END",
            ),
            left=num(sx + 20), top=num(y + 4),
        )
    )
    if ref is not None:
        out.append(
            Positioned(
                Row(
                    C(width="18", height="3", color=AMBER),
                    C(width="8"),
                    Text(ref_text, color="#FFE1A8", fontSize="16", fontFamily=FONT),
                    crossAxisAlignment="CENTER",
                ),
                right=num(W - (sx + SIDE_W - 20)), top=num(y + 8),
            )
        )
    n = int(round(vmax / vstep))
    for i in range(n + 1):
        v = vstep * i
        yy = inner_b - v * sc
        if yy < inner_t - 1:
            continue
        out.append(hline(si_l, si_r, yy, 1, LINE_SOFT))
        if any(abs(v - t) < 1e-9 for t in labelled):
            out.append(label(si_l - 10, yy, fmt(v), 16, TXT_3, anchor="right",
                             align="RIGHT", width=46, font=FONT))
    out.append(vline(si_l, inner_t - 4, inner_b, 2, "#3A4C73"))
    for i, v in enumerate(values):
        cx = si_l + gw * (i + 0.5)
        h = v * sc
        bw = 30
        out.append(
            Positioned(
                C(width=num(bw), height=num(h), color=color,
                  borderRadiusTopLeft="5", borderRadiusTopRight="5"),
                left=num(cx - bw / 2), top=num(inner_b - h),
            )
        )
        out.append(label(cx, inner_b - h - 4, fmt(v, True), 16, "#DCEBFF", anchor="bottom",
                         align="CENTER", width=gw - 2, font=FONT))
        out.append(label(cx, inner_b + 6, rows[i]["month"][5:], 16, TXT_3, anchor="top",
                         align="CENTER", width=gw - 2, font=FONT))
    if ref is not None:
        ry = inner_b - ref * sc
        out.append(hline(si_l, si_r, ry, 2, AMBER))
    return out


def f_ses(v, top=False):
    return f"{int(round(v)):,}"


def f_conv(v, top=False):
    return f"{v:.2f}" if top else f"{v:g}"


side = []
side += side_chart(CHT_Y, "访问量", "单位 次", [r["sessions"] for r in rows], SES_MAX,
                   SES_STEP, [0, 2000, 4000, 6000], "#60A5FA", f_ses)
side += side_chart(CHT_Y + SC_H + SC_GAP, "转化率", "单位 %",
                   [r["conversion_rate"] for r in rows], CONV_MAX, CONV_STEP,
                   [0, 6, 12], "#FBBF24", f_conv, ref=T["conversion_rate"],
                   ref_text=f"期间总体 {T['conversion_rate']:.2f}%")

# ---------------------------------------------------------------- table
tx, ty = PAD, BOT_Y
tbl_l, tbl_r = tx + 24, tx + TABLE_W - 24
tbl_inner = tbl_r - tbl_l
COLS = [("月份", 128, "LEFT"), ("净收入（元）", 196, "RIGHT"), ("退款率", 116, "RIGHT"),
        ("经营利润（元）", 196, "RIGHT"), ("转化率", 144, "RIGHT")]
assert sum(c[1] for c in COLS) == tbl_inner, (sum(c[1] for c in COLS), tbl_inner)

HEAD_Y = ty + 58
HEAD_H = 32
ROW_TOP = HEAD_Y + HEAD_H + 2
ROW_H = 34
DIV_Y = ROW_TOP + len(rows) * ROW_H + 4
TOT_H = 34
assert DIV_Y + TOT_H + 14 <= ty + BOT_H, (DIV_Y + TOT_H, ty + BOT_H)

xs, acc = [], tbl_l
for name, wdt, al in COLS:
    xs.append((acc, wdt, al))
    acc += wdt

tb = [card(tx, ty, TABLE_W, BOT_H)]
tb.append(
    Positioned(
        Row(
            Text("逐月明细", color=TXT, fontSize="24", fontStyle="BOLD", fontFamily=FONT),
            C(width="16"),
            Text("金额取整数元 · 比例保留两位小数", color=TXT_3, fontSize="16", fontFamily=FONT),
            crossAxisAlignment="END",
        ),
        left=num(tbl_l), top=num(ty + 16),
    )
)
tb.append(Positioned(C(width=num(tbl_inner), height="2", color="#33486F"),
                     left=num(tbl_l), top=num(HEAD_Y + HEAD_H)))
for (cx0, cw0, al), (name, _w, _a) in zip(xs, COLS):
    px = cx0 + 10 if al == "LEFT" else cx0 + cw0 - 10
    tb.append(label(px, HEAD_Y + HEAD_H / 2, name, 20, TXT_2,
                    anchor="left" if al == "LEFT" else "right", align=al, width=cw0 - 20,
                    font=FONT))

for i, r in enumerate(rows):
    ry = ROW_TOP + i * ROW_H
    if i % 2 == 0:
        tb.append(Positioned(C(width=num(tbl_inner), height=num(ROW_H), color="#141F3D",
                               borderRadius="6"), left=num(tbl_l), top=num(ry)))
    cells = [
        (r["month"], TXT, FONT),
        (f"{r['net_revenue']:,}", TXT, FONT_MONO),
        (f"{r['refund_rate']:.2f}%", ROSE if r["refund_rate"] >= 8 else TXT_2, FONT_MONO),
        (f"{r['operating_profit']:,}", TXT, FONT_MONO),
        (f"{r['conversion_rate']:.2f}%", SKY, FONT_MONO),
    ]
    for (cx0, cw0, al), (val, colr, fnt) in zip(xs, cells):
        px = cx0 + 10 if al == "LEFT" else cx0 + cw0 - 10
        tb.append(label(px, ry + ROW_H / 2, val, 20, colr,
                        anchor="left" if al == "LEFT" else "right", align=al, width=cw0 - 20,
                        font=fnt))

tb.append(Positioned(C(width=num(tbl_inner), height="2", color="#33486F"),
                     left=num(tbl_l), top=num(DIV_Y)))
tot_cells = [
    ("合计 / 期间", TXT, FONT),
    (f"{T['net_revenue']:,}", TXT, FONT_MONO),
    (f"{T['refund_rate']:.2f}%", ROSE, FONT_MONO),
    (f"{T['operating_profit']:,}", TXT, FONT_MONO),
    (f"{T['conversion_rate']:.2f}%", AMBER, FONT_MONO),
]
for (cx0, cw0, al), (val, colr, fnt) in zip(xs, tot_cells):
    px = cx0 + 10 if al == "LEFT" else cx0 + cw0 - 10
    tb.append(label(px, DIV_Y + TOT_H / 2 + 2, val, 20, colr,
                    anchor="left" if al == "LEFT" else "right", align=al, width=cw0 - 20,
                    font=fnt, bold=True))

# ---------------------------------------------------------------- conclusion
cx0, cy0 = PAD + TABLE_W + GAP, BOT_Y
CI = cx0 + 26
CWD = CONC_W - 52
cc = [card(cx0, cy0, CONC_W, BOT_H, fill="#121D3A", border="#2C4670")]
cc.append(top_accent(cx0, cy0, CONC_W, AMBER))
cc.append(
    Positioned(
        Col(
            Text("管理结论", color=AMBER, fontSize="18", fontStyle="BOLD", fontFamily=FONT),
            C(height="6"),
            Container(Text(conclusion["headline"], color=TXT, fontSize="26", fontStyle="BOLD",
                           fontFamily=FONT, textAlign="LEFT"), width=num(CWD)),
            C(height="8"),
            Container(Text(conclusion["claim"], color="#CBD9EE", fontSize="20", fontFamily=FONT,
                           textAlign="LEFT", softWrap="true", height="1.3"), width=num(CWD)),
            crossAxisAlignment="START",
        ),
        left=num(CI), top=num(cy0 + 14), width=num(CWD),
    )
)
EV_TOP = cy0 + 163
EV_STEP = 48
cc.append(Positioned(C(width=num(CWD), height="1", color="#2C4670"), left=num(CI),
                     top=num(EV_TOP - 12)))
for i, ev in enumerate(conclusion["evidence"]):
    yy = EV_TOP + i * EV_STEP
    cc.append(Positioned(C(width="8", height="8", color=AMBER, shape="CIRCLE"),
                         left=num(CI), top=num(yy + 9)))
    cc.append(label(CI + 18, yy, ev, 18, TXT_2, anchor="left_top", align="LEFT",
                    width=CWD - 20, max_lines=2, line_height=1.3, font=FONT))
REC_Y = EV_TOP + len(conclusion["evidence"]) * EV_STEP + 6
cc.append(
    Positioned(
        Border(
            Container(
                Container(
                    Text(conclusion["recommendation"], color="#FFF2CC", fontSize="18",
                         fontFamily=FONT, textAlign="LEFT", softWrap="true", height="1.3"),
                    width=num(CWD - 32),
                ),
                padding="(8,14)", color="#1B2747", borderRadius="12",
            ),
            border="1 SOLID #4A628C", borderRadius="12",
        ),
        left=num(CI), top=num(REC_Y), width=num(CWD),
    )
)
assert REC_Y + 70 <= cy0 + BOT_H, (REC_Y + 70, cy0 + BOT_H)
# ---------------------------------------------------------------- footer
foot = [
    label(PAD, 974,
          "净收入 = 退款前收入 − 退款；经营利润 = 净收入 − 经营成本（成本不含退款）；"
          "总体转化率 = 总订单 ÷ 总访问，不平均月度比例。",
          16, TXT_3, anchor="left_top", align="LEFT", width=1000, font=FONT),
    label(W - PAD, 974,
          "柱顶数值以万元显示并四舍五入到两位小数，精确值见明细表",
          16, "#55668A", anchor="right_top", align="RIGHT", width=480, font=FONT),
]

glow = layer_stack(
    Positioned(Opacity(C(width="720", height="340", color="#1B4470", shape="CIRCLE"),
                       opacity="0.5"), left="-130", top="-150"),
    Positioned(Opacity(C(width="520", height="280", color="#252A60", shape="CIRCLE"),
                       opacity="0.45"), right="-110", top="40"),
)
root = Container(
    layer_stack(glow, *parts, *mc, *side, *tb, *cc, *foot),
    width=num(W), height=num(H),
    gradientType="LINEAR", gradientColors=f"{BG_TOP},{BG_BOT}", gradientStops="0,1",
    gradientBegin="TOP_CENTER", gradientEnd="BOTTOM_CENTER",
)
doc = Snapshot(root, background=BG_TOP, type="png")

ap = argparse.ArgumentParser()
ap.add_argument("--ver", default="v004")
ap.add_argument("--final", default=None)
a = ap.parse_args()
TMP_DIR.mkdir(parents=True, exist_ok=True)
out_file = TMP_DIR / f"{a.ver}.snapshot"
out_file.write_text(doc.render() + "\n", encoding="utf-8")
if a.final:
    dst = ROOT / a.final
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(doc.render() + "\n", encoding="utf-8")
print(json.dumps({"dsl": out_file.relative_to(ROOT).as_posix(),
                  "bytes": out_file.stat().st_size,
                  "totals": T, "final": a.final}, ensure_ascii=False))
