"""A01 - Six-month operations diagnostic cockpit. Generates computed-data.json + DSL.

Every chart geometry constant below is the single source of truth used for both
the DSL and computed-data.json, so the rendered picture and the reported axis
definitions cannot drift apart.
"""
from __future__ import annotations

import csv
import json
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402
import state as S  # noqa: E402

TASK = "A01"
CSV_PATH = os.path.join(ROOT, "tasks", "A01-operations-dashboard", "inputs", "monthly.csv")
OUT = os.path.join(S.OUT_ROOT, TASK)
TMP = os.path.join(S.TMP_ROOT, TASK)
snapkit.configure(TASK, OUT, TMP)
S.start_task(TASK)

# ---------------------------------------------------------------- compute
rows = []
with open(CSV_PATH, newline="", encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        rows.append({k: (r[k] if k == "month" else int(r[k])) for k in
                     ("month", "orders", "gross_revenue", "refund_amount",
                      "operating_cost", "sessions")})

months = []
for r in rows:
    net = r["gross_revenue"] - r["refund_amount"]
    profit = net - r["operating_cost"]
    months.append({
        "month": r["month"], "orders": r["orders"], "sessions": r["sessions"],
        "gross_revenue": r["gross_revenue"], "refund_amount": r["refund_amount"],
        "operating_cost": r["operating_cost"], "net_revenue": net,
        "operating_profit": profit,
        "refund_rate": r["refund_amount"] / r["gross_revenue"],
        "conversion_rate": r["orders"] / r["sessions"],
        "margin": profit / net,
    })

tot = {k: sum(m[k] for m in months) for k in
       ("orders", "sessions", "gross_revenue", "refund_amount", "operating_cost",
        "net_revenue", "operating_profit")}
tot["overall_conversion_rate"] = tot["orders"] / tot["sessions"]
tot["overall_refund_rate"] = tot["refund_amount"] / tot["gross_revenue"]
tot["margin"] = tot["operating_profit"] / tot["net_revenue"]

# ---------------------------------------------------------------- geometry constants
W, H = 1600, 1000
M = 40
HDR_H = 84
KPI_Y, KPI_H, KPI_GAP = 108, 128, 16
KW = (W - 2 * M - 3 * KPI_GAP) / 4.0
CH_Y, CH_H = 252, 420
CX, CW = M, 900
SX, SW = 964, 552
SH = (CH_H - 16) / 2.0
BY, BH = 688, 296

BAR_MAX = 240000.0
SESS_MAX = 8000.0
CONV_MAX = 0.20
BAR_TICKS = [0, 60000, 120000, 180000, 240000]
BAR_TICK_LABELS = ["0", "6万", "12万", "18万", "24万"]
SESS_TICKS = [0, 4000, 8000]
SESS_TICK_LABELS = ["0", "4,000", "8,000"]
CONV_TICKS = [0.0, 0.10, 0.20]
CONV_TICK_LABELS = ["0%", "10%", "20%"]

AXIS = {
    "bar_chart": {
        "measure": "CNY 元", "domain": [0, BAR_MAX], "zero_baseline": True,
        "ticks": BAR_TICKS, "tick_labels": BAR_TICK_LABELS,
        "plot_rect_px": {"left": CX + 24 + 74, "top": CH_Y + 84,
                         "right": CX + CW - 24, "bottom": CH_Y + CH_H - 76},
        "shared_linear_scale_for": ["net_revenue", "operating_profit"],
        "negative_values_present": any(m["net_revenue"] < 0 or m["operating_profit"] < 0
                                       for m in months),
        "negative_handling": "zero baseline at the bottom; if a value were negative the "
                             "bar would be drawn below the baseline, but no month is negative",
    },
    "sessions_chart": {
        "measure": "sessions 访问次数", "domain": [0, SESS_MAX], "zero_baseline": True,
        "ticks": SESS_TICKS, "tick_labels": SESS_TICK_LABELS,
        "independent_from_currency_axis": True,
    },
    "conversion_chart": {
        "measure": "percent %", "domain": [0.0, CONV_MAX], "zero_baseline": True,
        "ticks": CONV_TICKS, "tick_labels": CONV_TICK_LABELS,
        "independent_from_currency_axis": True,
    },
    "month_alignment": "all three charts and the detail table use the same six month "
                       "labels 2026-04 .. 2026-09 in the same left-to-right order",
}

hi_rev = max(months, key=lambda m: m["net_revenue"])
peak_refund = max(months, key=lambda m: m["refund_rate"])
worst = min(months, key=lambda m: m["margin"])
first, last = months[0], months[-1]
apr, may, jun, jul, aug, sep = months

aug_excess_refund = aug["refund_amount"] - round(aug["gross_revenue"] * jul["refund_rate"])

conclusion = {
    "headline": "收入靠流量撑起来，利润被退款和成本吃掉",
    "evidence": [
        "净收入 6 个月 +%.2f%%：%s → %s 元" % (
            (sep["net_revenue"] / apr["net_revenue"] - 1) * 100,
            D.fmt_int(apr["net_revenue"]), D.fmt_int(sep["net_revenue"])),
        "访问量 +%.2f%%，月度转化率 %s → %s" % (
            (sep["sessions"] / apr["sessions"] - 1) * 100,
            D.pct(apr["conversion_rate"]), D.pct(sep["conversion_rate"])),
        "8 月利润比 7 月少 %s 元，退款率 %s 最高" % (
            D.fmt_int(jul["operating_profit"] - aug["operating_profit"]),
            D.pct(aug["refund_rate"])),
    ],
    "evidence_numbers": {
        "apr_net_revenue": apr["net_revenue"], "sep_net_revenue": sep["net_revenue"],
        "net_revenue_growth_pct": round((sep["net_revenue"] / apr["net_revenue"] - 1) * 100, 2),
        "apr_sessions": apr["sessions"], "sep_sessions": sep["sessions"],
        "session_growth_pct": round((sep["sessions"] / apr["sessions"] - 1) * 100, 2),
        "apr_conversion": round(apr["conversion_rate"], 6),
        "sep_conversion": round(sep["conversion_rate"], 6),
        "period_overall_conversion": round(tot["overall_conversion_rate"], 6),
        "aug_net_revenue": aug["net_revenue"], "aug_operating_profit": aug["operating_profit"],
        "jul_operating_profit": jul["operating_profit"],
        "profit_gap_jul_minus_aug": jul["operating_profit"] - aug["operating_profit"],
        "aug_refund_rate": round(aug["refund_rate"], 6),
        "jun_refund_rate": round(jun["refund_rate"], 6),
        "period_refund_rate": round(tot["overall_refund_rate"], 6),
        "aug_excess_refund_vs_jul_rate": aug_excess_refund,
        "worst_margin_month": worst["month"], "worst_margin": round(worst["margin"], 6),
        "period_margin": round(tot["margin"], 6),
        "period_operating_cost": tot["operating_cost"],
        "sep_operating_cost": sep["operating_cost"],
        "jul_operating_cost": jul["operating_cost"],
    },
    "actions": [
        "复盘 6 月与 8 月退款（退款率均 %s，期间 %s）：8 月按 7 月退款率可少退 %s 元" % (
            D.pct(aug["refund_rate"]), D.pct(tot["overall_refund_rate"]),
            D.fmt_int(aug_excess_refund)),
        "把月度转化率从 %s 拉回 4 月的 %s：流量已涨 %.2f%%，效率在稀释增量" % (
            D.pct(sep["conversion_rate"]), D.pct(apr["conversion_rate"]),
            (sep["sessions"] / apr["sessions"] - 1) * 100),
        "成本按 7 月 %s 利润率设红线：成本从 %s 涨到 %s 元，而利润率由 %s 降到 %s" % (
            D.pct(jul["margin"]), D.fmt_int(jul["operating_cost"]),
            D.fmt_int(sep["operating_cost"]), D.pct(jul["margin"]), D.pct(sep["margin"])),
    ],
}

computed = {
    "task": TASK, "title": "六个月经营诊断驾驶舱",
    "source": "tasks/A01-operations-dashboard/inputs/monthly.csv (sole business data source)",
    "units": {"money": "元 (CNY)", "orders": "笔", "sessions": "访问次数"},
    "formulas": {
        "net_revenue": "gross_revenue - refund_amount",
        "operating_profit": "net_revenue - operating_cost",
        "refund_rate": "refund_amount / gross_revenue",
        "conversion_rate_monthly": "orders / sessions",
        "overall_conversion_rate": "total_orders / total_sessions (NOT the mean of monthly ratios)",
        "overall_refund_rate": "total_refund / total_gross_revenue",
        "margin": "operating_profit / net_revenue",
    },
    "months": months, "totals": tot,
    "axis_definitions": AXIS, "conclusion": conclusion,
    "display_rules": {
        "kpi_money": "raw yuan with thousands separators, no lossy rescaling",
        "table_money": "integer yuan with thousands separators",
        "table_ratios": "two decimals with percent sign",
        "body_min_font_px": 20, "footnote_min_font_px": 16,
    },
}
with open(os.path.join(OUT, "computed-data.json"), "w", encoding="utf-8") as fh:
    json.dump(computed, fh, ensure_ascii=False, indent=2)

# ---------------------------------------------------------------- palette
BG, INK, MUTED, FAINT, LINE, CARD = ("#EEF2F6FF", "#0F172AFF", "#475569FF",
                                     "#7C8CA0FF", "#E2E8F0FF", "#FFFFFFFF")
NAVY = "#0F172AFF"
C_NET, C_PROFIT, C_SESS, C_CONV = "#2563EBFF", "#0D9488FF", "#7C3AEDFF", "#EA580CFF"
GOOD, BAD = "#15803DFF", "#B91C1CFF"

kids = []

# ---------------------------------------------------------------- header
kids += [
    D.box(0, 0, W, HDR_H, color=NAVY),
    D.box(0, HDR_H, W, 3, gradient={"gradientType": "LINEAR",
                                     "gradientColors": "%s,%s,%s" % (C_NET, C_CONV, C_PROFIT),
                                     "gradientStops": "0,0.55,1",
                                     "gradientBegin": "CENTER_LEFT",
                                     "gradientEnd": "CENTER_RIGHT"}),
    D.text_el("Northstar 经营诊断驾驶舱", x=M, y=17, w=760, h=40, size=30,
              style="BOLD", color="#F8FAFCFF"),
    D.text_el("2026-04 – 2026-09 · 金额单位：元 · 订单单位：笔 · 访问单位：次 · "
              "口径：净收入 = 收入 − 退款，经营利润 = 净收入 − 经营成本",
              x=M, y=52, w=1080, h=24, size=17, color="#9FB0C4FF"),
]
bw = 286
kids += [
    D.box(W - M - bw, 21, bw, 42, color="#1E293BFF", radius=21, border="1 SOLID #334155FF"),
    D.text_el("期间总体转化率 = 总订单 ÷ 总访问次数", x=W - M - bw, y=33, w=bw, h=24,
              size=16, color="#CBD5E1FF", align="CENTER"),
]

# ---------------------------------------------------------------- KPI cards
kpis = [
    ("总净收入", D.fmt_int(tot["net_revenue"]), "元",
     "六个月累计 · 占退款前收入 %s" % D.pct(tot["net_revenue"] / tot["gross_revenue"]),
     C_NET),
    ("总经营利润", D.fmt_int(tot["operating_profit"]), "元",
     "利润率 %s · 成本合计 %s 元" % (D.pct(tot["margin"]), D.fmt_int(tot["operating_cost"])),
     C_PROFIT),
    ("总订单", D.fmt_int(tot["orders"]), "笔",
     "月均 %s 笔 · 单月峰值 %s 笔" % (D.fmt_int(round(tot["orders"] / 6.0)),
                                     D.fmt_int(max(m["orders"] for m in months))),
     "#0E7490FF"),
    ("期间总体转化率", D.pct(tot["overall_conversion_rate"]), "",
     "%s 笔 ÷ %s 次访问（总÷总）" % (D.fmt_int(tot["orders"]),
                                          D.fmt_int(tot["sessions"])),
     C_CONV),
]
for i, (label, value, unit, sub, accent) in enumerate(kpis):
    x = M + i * (KW + KPI_GAP)
    kids += [
        D.card(x, KPI_Y, KW, KPI_H, CARD, 16, "1 SOLID #E2E8F0FF", "0 2 10 0 #0F172A0F"),
        D.box(x, KPI_Y + 14, 5, KPI_H - 28, color=accent, radius=3),
        D.text_el(label, x=x + 22, y=KPI_Y + 15, w=KW - 44, h=24, size=20, color=MUTED),
    ]
    vw = KW - 44 - (len(unit) * 16 if unit else 0)
    kids += [
        D.text_el(value, x=x + 22, y=KPI_Y + 42, w=vw, h=44, size=34, style="BOLD", color=INK),
        D.text_el(sub, x=x + 22, y=KPI_Y + 92, w=KW - 40, h=22, size=16, color=FAINT,
                  max_lines=1),
    ]
    if unit:
        kids.append(D.text_el(unit, x=x + 22 + vw + 6, y=KPI_Y + 62, w=60, h=24,
                              size=17, color=FAINT))

# ---------------------------------------------------------------- left: grouped bars
kids += [
    D.card(CX, CH_Y, CW, CH_H, CARD, 16),
    D.text_el("净收入与经营利润", x=CX + 24, y=CH_Y + 18, w=440, h=28, size=21,
              style="BOLD", color=INK),
    D.text_el("六个月分组柱图 · 两系列共用同一零起点线性刻度（单位：元）",
              x=CX + 24, y=CH_Y + 46, w=560, h=22, size=16, color=FAINT),
]
lgx = CX + CW - 24
for name, colr in (("经营利润", C_PROFIT), ("净收入", C_NET)):
    tw = 22 + len(name) * 17
    kids += [
        D.text_el(name, x=lgx - tw, y=CH_Y + 24, w=tw, h=22, size=17, color=MUTED, align="RIGHT"),
        D.box(lgx - tw - 18, CH_Y + 29, 14, 14, color=colr, radius=4),
    ]
    lgx -= tw + 32

PX0, PX1 = CX + 24 + 74, CX + CW - 24
PY0, PY1 = CH_Y + 84, CH_Y + CH_H - 76
PH, PW = PY1 - PY0, PX1 - PX0
for tv, tl in zip(BAR_TICKS, BAR_TICK_LABELS):
    ty = PY1 - tv / BAR_MAX * PH
    kids += [
        D.hline(PX0, PX1, ty, "#CBD5E1FF" if tv == 0 else LINE, 1.5 if tv == 0 else 1),
        D.text_el(tl, x=PX0 - 72, y=ty - 11, w=62, h=22, size=16, color=MUTED, align="RIGHT"),
    ]
slot = PW / 6.0
BW = 44.0
for i, m in enumerate(months):
    cx = PX0 + slot * (i + 0.5)
    nbh = m["net_revenue"] / BAR_MAX * PH
    pbh = m["operating_profit"] / BAR_MAX * PH
    kids.append(D.box(cx - BW - 4, PY1 - nbh, BW, nbh, color=C_NET, radius=5,
                      radii={"BottomLeft": "0", "BottomRight": "0"}))
    kids.append(D.box(cx + 4, PY1 - pbh, BW, pbh, color=C_PROFIT, radius=5,
                      radii={"BottomLeft": "0", "BottomRight": "0"}))
    kids += [
        D.text_el(D.fmt_int(m["net_revenue"]), x=cx - BW - 4 - 26, y=PY1 - nbh - 26,
                  w=BW + 52, h=22, size=16, style="BOLD", color="#1D4ED8FF", align="CENTER"),
        D.text_el(m["month"], x=cx - 44, y=PY1 + 10, w=88, h=24, size=17, color=INK,
                  align="CENTER"),
    ]
kids.append(D.text_el("柱图两系列共用零起点与比例；净收入柱上方标注净收入原值，经营利润逐月值见下方明细表。",
                      x=CX + 24, y=CH_Y + CH_H - 30, w=CW - 48, h=22, size=16, color=FAINT))

# ---------------------------------------------------------------- right: two aligned small charts


def small_chart(y, title, unit_note, values, ticks, tick_labels, color, ymax, fmt, area=True):
    kids.append(D.card(SX, y, SW, SH, CARD, 16))
    kids.extend([
        D.text_el(title, x=SX + 20, y=y + 13, w=320, h=26, size=20, style="BOLD", color=INK),
        D.text_el(unit_note, x=SX + SW - 20 - 250, y=y + 15, w=250, h=22,
                  size=16, color=FAINT, align="RIGHT"),
    ])
    qx0, qx1 = SX + 20 + 64, SX + SW - 20
    qy0, qy1 = y + 74, y + SH - 42
    qh, qw = qy1 - qy0, qx1 - qx0
    sl = qw / 6.0
    pts = [(qx0 + sl * (i + 0.5), qy1 - v / ymax * qh) for i, v in enumerate(values)]
    for tv, tl in zip(ticks, tick_labels):
        ty = qy1 - tv / ymax * qh
        kids.extend([
            D.hline(qx0, qx1, ty, "#CBD5E1FF" if tv == 0 else LINE, 1.5 if tv == 0 else 1),
            D.text_el(tl, x=qx0 - 62, y=ty - 10, w=56, h=20, size=16, color=MUTED, align="RIGHT"),
        ])
    if area:
        kids.append(D.polygon([(p[0], qy1) for p in pts] + pts[::-1], color, 0.13))
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        n = 26
        for k in range(n):
            t = k / n
            kids.append(D.box(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t - 1.3,
                              (x1 - x0) / n + 1.0, 2.6, color=color))
    for (px, py) in pts:
        kids.append(D.box(px - 5, py - 5, 10, 10, color="#FFFFFFFF", radius=5,
                          border="3 SOLID " + color))
    for i, ((px, py), v) in enumerate(zip(pts, values)):
        kids.extend([
            D.text_el(fmt(v), x=px - 52, y=y + 42, w=104, h=22, size=16, style="BOLD",
                      color=color, align="CENTER"),
            D.text_el(months[i]["month"], x=px - 42, y=qy1 + 8, w=84, h=22, size=16,
                      color=MUTED, align="CENTER"),
        ])


small_chart(CH_Y, "访问量 sessions", "独立数轴 0–8,000 次（非金额）",
            [m["sessions"] for m in months], SESS_TICKS, SESS_TICK_LABELS,
            C_SESS, SESS_MAX, lambda v: D.fmt_int(v), area=True)
small_chart(CH_Y + SH + 16, "月度转化率", "独立数轴 0–20%（非金额）",
            [m["conversion_rate"] for m in months], CONV_TICKS, CONV_TICK_LABELS,
            C_CONV, CONV_MAX, lambda v: D.pct(v), area=False)

# ---------------------------------------------------------------- bottom: detail table
kids += [
    D.card(CX, BY, CW, BH, CARD, 16),
    D.text_el("月度明细", x=CX + 24, y=BY + 16, w=320, h=26, size=20, style="BOLD", color=INK),
    D.text_el("金额单位：元（整数） · 比例两位小数", x=CX + CW - 24 - 330, y=BY + 20,
              w=330, h=22, size=16, color=FAINT, align="RIGHT"),
]
cols = [("月份", CX + 24, "START", 200), ("净收入", CX + 210, "RIGHT", 210),
        ("退款率", CX + 390, "RIGHT", 160), ("经营利润", CX + 520, "RIGHT", 200),
        ("转化率", CX + 700, "RIGHT", 176)]
HY = BY + 50
kids.append(D.hline(CX + 24, CX + CW - 24, HY + 28, "#CBD5E1FF", 1.5))
for name, cxx, al, cwid in cols:
    kids.append(D.text_el(name, x=cxx, y=HY, w=cwid, h=24, size=18, style="BOLD",
                          color=MUTED, align=al))
RY, ROW = HY + 40, 29
for i, m in enumerate(months):
    ry = RY + i * ROW
    if i % 2 == 1:
        kids.append(D.box(CX + 16, ry - 5, CW - 32, ROW, color="#F8FAFCFF"))
    weak = m["margin"] < tot["margin"]
    kids += [
        D.text_el(m["month"], x=cols[0][1], y=ry, w=200, h=24, size=20, color=INK),
        D.text_el(D.fmt_int(m["net_revenue"]), x=cols[1][1], y=ry, w=210, h=24, size=20,
                  style="BOLD", color=INK, align="RIGHT"),
        D.text_el(D.pct(m["refund_rate"]), x=cols[2][1], y=ry, w=160, h=24, size=20,
                  color=(BAD if m["refund_rate"] >= 0.08 else INK), align="RIGHT"),
        D.text_el(D.fmt_int(m["operating_profit"]), x=cols[3][1], y=ry, w=200, h=24,
                  size=20, style="BOLD", color=(BAD if weak else GOOD), align="RIGHT"),
        D.text_el(D.pct(m["conversion_rate"]), x=cols[4][1], y=ry, w=176, h=24, size=20,
                  color=INK, align="RIGHT"),
    ]
kids += [
    D.hline(CX + 24, CX + CW - 24, RY + 6 * ROW - 7, LINE, 1),
    D.text_el("退款率 = 退款 ÷ 退款前收入；月度转化率 = 订单 ÷ 访问次数；期间总体转化率 = 总订单 ÷ 总访问次数。",
              x=CX + 24, y=RY + 6 * ROW + 1, w=CW - 48, h=22, size=16, color=FAINT),
]

# ---------------------------------------------------------------- bottom: conclusion
QX, QW2 = 964, 552
kids += [
    D.card(QX, BY, QW2, BH, NAVY, 16, None, "0 2 10 0 #0F172A1F"),
    D.box(QX, BY, 6, BH, color=C_CONV, radius=3),
    D.text_el("管理结论", x=QX + 24, y=BY + 14, w=300, h=26, size=19, style="BOLD",
              color="#F8FAFCFF"),
    D.text_el(conclusion["headline"], x=QX + 24, y=BY + 40, w=QW2 - 48, h=30, size=21,
              style="BOLD", color="#FDBA74FF"),
]
ey = BY + 80
for ev in conclusion["evidence"]:
    kids.extend([
        D.box(QX + 26, ey + 9, 7, 7, color=C_CONV, radius=4),
        D.text_el(ev, x=QX + 42, y=ey, w=QW2 - 66, h=28, size=20, color="#E2E8F0FF"),
    ])
    ey += 40
kids.extend([
    D.box(QX + 24, ey + 6, QW2 - 48, 1, color="#334155FF"),
    D.text_el("下一步 · 完整建议见 computed-data.json", x=QX + 24,
              y=ey + 16, w=QW2 - 48, h=22, size=17, style="BOLD", color="#7DD3FCFF"),
    D.text_el(conclusion["actions"][0], x=QX + 24, y=ey + 38, w=QW2 - 48, h=48,
              size=18, color="#BAE6FDFF"),
])

dsl = D.snapshot([D.stack(kids, W, H)], W, H, bg=BG)
with open(os.path.join(TMP, "build-a01.snapshot"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write(dsl)

r = snapkit.render(dsl, "operations.png", "operations.snapshot", final=True)
snapkit.new_version("baseline", None, r.get("dsl"), r.get("image"),
                    changes="v1 generated from monthly.csv with computed axis definitions",
                    observed=None, complete=False, note="first render")
print("render ok=%s status=%s bytes=%s" % (r.get("ok"), r.get("status"), r.get("bytes")))
if not r.get("ok"):
    print(r.get("error"))