# -*- coding: utf-8 -*-
"""A01 generator v3: six-month operations diagnostic cockpit (1600x1000).

Run from the suite root:
    python tmp/<run_id>/A01/scripts/generate.py
"""
from __future__ import annotations

import csv
import os
import sys
import time
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))

import dslkit as K  # noqa: E402
import snapshot_api as api  # noqa: E402

TASK = "A01"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
OUT.mkdir(parents=True, exist_ok=True)
(TMP / "scripts").mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- palette
BG = "#070C16"
CARD = "#0D1524"
BORDER = "#1D2B44"
HAIR = "#17243A"
GRID = "#192640"
TEXT = "#E9EFF9"
TEXT2 = "#9DAEC7"
MUTED = "#6B7C93"
CYAN = "#22D3EE"
AMBER = "#FBBF24"
GREEN = "#34D399"
RED = "#FB7185"
VIOLET = "#A78BFA"

# ---------------------------------------------------------------- data
csv_path = SUITE_ROOT / "tasks" / "A01-operations-dashboard" / "inputs" / "monthly.csv"
rows = []
with csv_path.open(encoding="utf-8", newline="") as fh:
    for rec in csv.DictReader(fh):
        rows.append({k: (rec[k] if k == "month" else int(rec[k]))
                     for k in ("month", "orders", "gross_revenue", "refund_amount",
                               "operating_cost", "sessions")})

months = []
for r in rows:
    net = r["gross_revenue"] - r["refund_amount"]
    profit = net - r["operating_cost"]
    months.append({
        **r,
        "net_revenue": net,
        "operating_profit": profit,
        "refund_rate": r["refund_amount"] / r["gross_revenue"] * 100,
        "conversion_rate": r["orders"] / r["sessions"] * 100,
        "profit_margin": profit / net * 100,
        "profit_per_order": profit / r["orders"],
    })

tot = {k: sum(m[k] for m in months) for k in
       ("gross_revenue", "refund_amount", "operating_cost", "net_revenue",
        "operating_profit", "orders", "sessions")}
tot["refund_rate"] = tot["refund_amount"] / tot["gross_revenue"] * 100
tot["conversion_rate"] = tot["orders"] / tot["sessions"] * 100
tot["profit_margin"] = tot["operating_profit"] / tot["net_revenue"] * 100

last, prev = months[-1], months[-2]
mom = {
    "net_revenue": (last["net_revenue"] / prev["net_revenue"] - 1) * 100,
    "operating_profit": (last["operating_profit"] / prev["operating_profit"] - 1) * 100,
    "orders": (last["orders"] / prev["orders"] - 1) * 100,
    "conversion_pp": last["conversion_rate"] - prev["conversion_rate"],
}

recovery = 0.0
for m in months:
    if round(m["refund_rate"], 2) == 8.00:
        recovery += m["refund_amount"] - m["gross_revenue"] * 0.05
recovery_share = recovery / last["operating_profit"] * 100

# ---------------------------------------------------------------- geometry
W, H = 1600, 1000
KPI_Y, KPI_H, KPI_W, KPI_GAP = 130, 142, 365, 20

BX0, BX1 = 140.0, 896.0
BY0, BY1 = 372.0, 592.0
BAR_MAX = 210000.0
BAR_TICKS = [0, 50000, 100000, 150000, 200000]
GROUP_W = (BX1 - BX0) / 6
BAR_W, BAR_GAP = 34.0, 10.0

SX0, SX1 = 1040.0, 1520.0
SESS_TOP, SESS_BASE, SESS_MAX = 390.0, 458.0, 6000.0
CONV_TOP, CONV_BASE, CONV_MAX = 520.0, 592.0, 14.0
SGROUP = (SX1 - SX0) / 6


def y_of(v: float, top: float, base: float, vmax: float) -> float:
    return base - v / vmax * (base - top)


parts: list[str] = []

# ---------------------------------------------------------------- atmosphere
parts.append(K.rect(-200, -300, 700, 560, radius=280,
                    gradient='gradientType="RADIAL" gradientColors="#0891B266,#0891B200" '
                             'gradientCenter="CENTER" gradientRadius="0.5"'))
parts.append(K.rect(1180, 700, 620, 500, radius=250,
                    gradient='gradientType="RADIAL" gradientColors="#1D4ED84D,#1D4ED800" '
                             'gradientCenter="CENTER" gradientRadius="0.5"'))

# ---------------------------------------------------------------- header
parts.append(K.rect(36, 36, 44, 44, radius=12,
                    gradient='gradientType="LINEAR" gradientColors="#22D3EE,#2563EB" '
                             'gradientBegin="TOP_LEFT" gradientEnd="BOTTOM_RIGHT"'))
parts.append(K.text(36, 46, "N", width=44, size=24, color="#04121B", bold=True, align="CENTER"))
parts.append(K.text(94, 30, "NORTHSTAR / OPS REVIEW", size=17, color=CYAN, bold=True, spacing=2.6))
parts.append(K.text(94, 54, "经营诊断驾驶舱", size=32, color=TEXT, bold=True))
parts.append(K.text(840, 40, "净收入 = 收入 − 退款　经营利润 = 净收入 − 成本", width=724,
                    size=16, color=TEXT2, align="RIGHT"))
parts.append(K.text(840, 64, "口径：金额 元 · 订单 笔 · 访问 次 · 数据源 inputs/monthly.csv", width=724,
                    size=16, color=MUTED, align="RIGHT"))
parts.append(K.rect(36, 110, 1528, 1, color=HAIR))

# ---------------------------------------------------------------- KPI
kpis = [
    ("总净收入", f"{K.wan(tot['net_revenue'])} 万元", "元",
     f"9 月 {K.wan(last['net_revenue'])} 万", f"+{mom['net_revenue']:.1f}%", CYAN,
     [m["net_revenue"] for m in months]),
    ("总经营利润", f"{K.wan(tot['operating_profit'])} 万元", "元",
     f"9 月 {K.wan(last['operating_profit'])} 万", f"+{mom['operating_profit']:.1f}%", AMBER,
     [m["operating_profit"] for m in months]),
    ("总订单", K.fmt_int(tot["orders"]), "笔",
     f"9 月 {K.fmt_int(last['orders'])} 笔", f"+{mom['orders']:.1f}%", VIOLET,
     [m["orders"] for m in months]),
    ("期间总体转化率", K.fmt_pct(tot["conversion_rate"]), "总订单 ÷ 总访问", None, None, GREEN, None),
]

for i, (label, value, unit, sub, delta, accent, series) in enumerate(kpis):
    x = 36 + i * (KPI_W + KPI_GAP)
    parts.append(K.rect(x, KPI_Y, KPI_W, KPI_H, color=CARD, radius=16, border=f"1 SOLID {BORDER}"))
    parts.append(K.rect(x, KPI_Y + 18, 4, KPI_H - 36, color=accent, radius=2))
    parts.append(K.text(x + 24, KPI_Y + 17, label, size=19, color=TEXT2))
    parts.append(K.text(x + KPI_W - 170, KPI_Y + 18, unit, width=146, size=16, color=MUTED, align="RIGHT"))
    parts.append(K.text(x + 22, KPI_Y + 43, value, size=40, color=TEXT, bold=True, spacing=-0.8))
    if series is not None:
        parts.append(K.text(x + 24, KPI_Y + 99, sub, width=140, size=16, color=TEXT2))
        parts.append(K.text(x + 176, KPI_Y + 99, delta, width=100, size=16, color=GREEN, bold=True))
        mx = max(series)
        for j, v in enumerate(series):
            bh = max(5.0, v / mx * 30)
            bx = x + KPI_W - 24 - (6 - j) * 12 + 4
            alpha = "" if j == 5 else "9A"
            parts.append(K.rect(bx, KPI_Y + 127 - bh, 8, bh, color=accent + alpha, radius=2))
    else:
        parts.append(K.text(x + 24, KPI_Y + 96, f"9 月 {K.fmt_pct(last['conversion_rate'])} · "
                                               f"+{mom['conversion_pp']:.2f}pp", width=320, size=16, color=TEXT2))
        parts.append(K.text(x + 24, KPI_Y + 118, "峰值 12.00% · 谷值 10.60%", width=320, size=16, color=MUTED))

# ---------------------------------------------------------------- main bar chart
parts.append(K.rect(36, 286, 900, 360, color=CARD, radius=16, border=f"1 SOLID {BORDER}"))
parts.append(K.text(58, 298, "六个月净收入与经营利润", size=21, color=TEXT, bold=True))
parts.append(K.text(58, 326, "同一零起点 · 同一线性比例 · 单位 万元", size=16, color=MUTED))
parts.append(K.rect(700, 306, 12, 12, color=CYAN, radius=3))
parts.append(K.text(718, 300, "净收入", size=16, color=TEXT2))
parts.append(K.rect(796, 306, 12, 12, color=AMBER, radius=3))
parts.append(K.text(814, 300, "经营利润", size=16, color=TEXT2))
parts.append(K.text(60, 347, "万元", width=64, size=16, color=MUTED, align="RIGHT"))

for t in BAR_TICKS:
    y = y_of(t, BY0, BY1, BAR_MAX)
    parts.append(K.rect(BX0 - 8, y, BX1 - BX0 + 8, 1, color=GRID))
    parts.append(K.text(60, y - 12, str(t // 10000), width=64, size=16, color=MUTED, align="RIGHT"))
parts.append(K.rect(BX0, BY1, BX1 - BX0, 2, color="#33445F"))

for i, m in enumerate(months):
    cx = BX0 + (i + 0.5) * GROUP_W
    for value, left, color in ((m["net_revenue"], cx - BAR_GAP / 2 - BAR_W, CYAN),
                               (m["operating_profit"], cx + BAR_GAP / 2, AMBER)):
        y = y_of(value, BY0, BY1, BAR_MAX)
        parts.append(K.rect(left, y, BAR_W, BY1 - y, radius=3,
                            gradient=f'gradientType="LINEAR" gradientColors="{color}CC,{color}44" '
                                     f'gradientBegin="TOP_CENTER" gradientEnd="BOTTOM_CENTER"'))
    parts.append(K.text(cx - 53, 600, m["month"], width=106, size=17, color=TEXT2, align="CENTER"))
    parts.append(K.text(cx - BAR_GAP / 2 - BAR_W - 13, y_of(m["net_revenue"], BY0, BY1, BAR_MAX) - 22,
                        K.wan(m["net_revenue"]), width=60, size=16, color=CYAN, align="CENTER"))
    parts.append(K.text(cx + BAR_GAP / 2 - 13, y_of(m["operating_profit"], BY0, BY1, BAR_MAX) - 22,
                        K.wan(m["operating_profit"]), width=60, size=16, color=AMBER, align="CENTER"))

# ---------------------------------------------------------------- side card
parts.append(K.rect(956, 286, 600, 360, color=CARD, radius=16, border=f"1 SOLID {BORDER}"))
parts.append(K.text(980, 298, "访问量与转化率", size=21, color=TEXT, bold=True))
parts.append(K.text(980, 326, "两个小图共用同一组月份位置", size=16, color=MUTED))
parts.append(K.text(980, 350, "访问量 · 次", size=16, color=TEXT2))
parts.append(K.text(1370, 350, f"合计 {K.fmt_int(tot['sessions'])} 次", width=150, size=16,
                    color=MUTED, align="RIGHT"))
for t in (0, 3000, 6000):
    y = y_of(t, SESS_TOP, SESS_BASE, SESS_MAX)
    if t:
        parts.append(K.rect(SX0, y, SX1 - SX0, 1, color=GRID))
    parts.append(K.text(980, y - 12, K.fmt_int(t), width=54, size=16, color=MUTED, align="RIGHT"))
parts.append(K.rect(SX0, SESS_BASE, SX1 - SX0, 2, color="#33445F"))
for i, m in enumerate(months):
    cx = SX0 + (i + 0.5) * SGROUP
    y = y_of(m["sessions"], SESS_TOP, SESS_BASE, SESS_MAX)
    parts.append(K.rect(cx - 23, y, 46, SESS_BASE - y, radius=3,
                        gradient='gradientType="LINEAR" gradientColors="#22D3EECC,#0EA5E944" '
                                 'gradientBegin="TOP_CENTER" gradientEnd="BOTTOM_CENTER"'))
    parts.append(K.text(cx - 31, y - 22, K.fmt_int(m["sessions"]), width=62, size=16,
                        color="#7DD3FC", align="CENTER"))

parts.append(K.text(980, 486, "转化率 · %", size=16, color=TEXT2))
parts.append(K.text(1230, 486, "峰值 12.00% · 谷值 10.60%", width=290, size=16,
                    color=MUTED, align="RIGHT"))
for t in (0, 7, 14):
    y = y_of(t, CONV_TOP, CONV_BASE, CONV_MAX)
    if t:
        parts.append(K.rect(SX0, y, SX1 - SX0, 1, color=GRID))
    parts.append(K.text(980, y - 12, str(t), width=54, size=16, color=MUTED, align="RIGHT"))
parts.append(K.rect(SX0, CONV_BASE, SX1 - SX0, 2, color="#33445F"))
for i, m in enumerate(months):
    cx = SX0 + (i + 0.5) * SGROUP
    y = y_of(m["conversion_rate"], CONV_TOP, CONV_BASE, CONV_MAX)
    color = AMBER if round(m["conversion_rate"], 2) >= 12.0 else "#7DD3FC"
    parts.append(K.rect(cx - 20, y, 40, CONV_BASE - y, radius=3,
                        gradient=f'gradientType="LINEAR" gradientColors="{color}CC,{color}44" '
                                 f'gradientBegin="TOP_CENTER" gradientEnd="BOTTOM_CENTER"'))
    parts.append(K.text(cx - 31, y - 22, K.fmt_pct(m["conversion_rate"]), width=62, size=16,
                        color=color, align="CENTER"))
for i, m in enumerate(months):
    cx = SX0 + (i + 0.5) * SGROUP
    parts.append(K.text(cx - 30, 600, m["month"][5:] + "月", width=60, size=16, color=MUTED, align="CENTER"))

# ---------------------------------------------------------------- table
parts.append(K.rect(36, 660, 1520, 224, color=CARD, radius=16, border=f"1 SOLID {BORDER}"))
for i in range(6):
    top = 724 + i * 26
    if i % 2 == 0:
        parts.append(K.rect(56, top, 1480, 26, color="#0A1221"))
parts.append(K.text(58, 670, "月度明细", size=19, color=TEXT, bold=True))
parts.append(K.text(1100, 672, "金额单位：元 · 比例保留两位小数", width=436, size=16, color=MUTED, align="RIGHT"))
parts.append(K.rect(56, 720, 1480, 1, color=HAIR))

COLS = [("月份", 58, "START"), ("净收入", 496, "RIGHT"), ("退款率", 716, "RIGHT"),
        ("经营利润", 1016, "RIGHT"), ("利润率", 1236, "RIGHT"), ("转化率", 1516, "RIGHT")]
for label, edge, align in COLS:
    if align == "START":
        parts.append(K.text(edge, 696, label, size=16, color=MUTED))
    else:
        parts.append(K.text(edge - 160, 696, label, width=160, size=16, color=MUTED, align="RIGHT"))

for i, m in enumerate(months):
    top = 724 + i * 26
    ty = top + 2
    parts.append(K.text(58, ty, "2026-" + m["month"][5:], size=20, color=TEXT2, extra='fontFeatures="tnum"'))
    parts.append(K.text(296, ty, K.fmt_int(m["net_revenue"]), width=200, size=20, color=TEXT,
                        align="RIGHT", extra='fontFeatures="tnum"'))
    rr_color = RED if round(m["refund_rate"], 2) >= 8.0 else AMBER
    parts.append(K.text(516, ty, K.fmt_pct(m["refund_rate"]), width=200, size=20, color=rr_color,
                        align="RIGHT", extra='fontFeatures="tnum"'))
    parts.append(K.text(816, ty, K.fmt_int(m["operating_profit"]), width=200, size=20, color=TEXT,
                        align="RIGHT", extra='fontFeatures="tnum"'))
    bar_w = max(2.0, m["profit_margin"] / 40.0 * 92)
    parts.append(K.rect(1044, top + 9, bar_w, 8, color="#22D3EE47", radius=4))
    parts.append(K.text(1156, ty, K.fmt_pct(m["profit_margin"]), width=80, size=20, color=TEXT2,
                        align="RIGHT", extra='fontFeatures="tnum"'))
    parts.append(K.text(1316, ty, K.fmt_pct(m["conversion_rate"]), width=200, size=20, color=TEXT2,
                        align="RIGHT", extra='fontFeatures="tnum"'))

# ---------------------------------------------------------------- conclusion
parts.append(K.rect(36, 898, 1520, 66, color="#111B2D", radius=14, border="1 SOLID #2C3D59"))
parts.append(K.rect(36, 898, 5, 66, color=AMBER, radius=2))
parts.append(K.text(58, 908, "管理结论", size=17, color=AMBER, bold=True, spacing=1.2))
parts.append(K.text(58, 932, "证据链", size=16, color="#A98A3E"))
parts.append(K.text(190, 904,
                    "退款率是本期利润的最强解释项：6、8 月升至 8.00%，单均经营利润随之跌至 62.7 / 72.0 元。",
                    width=1345, size=20, color="#E4EDFA"))
parts.append(K.text(190, 934,
                    f"反事实测算：两月退款率回到 5.00% 可多留 {K.fmt_int(recovery)} 元，"
                    f"≈ 9 月经营利润 64,368 元的 {recovery_share:.1f}%。",
                    width=1345, size=17, color="#9FB4CE"))

# ---------------------------------------------------------------- footnote
parts.append(K.text(36, 972, "数据源 inputs/monthly.csv · 图轴均为线性零起点；期间转化率 = 总订单 ÷ 总访问，"
                             "未对月度比例取平均。", width=1130, size=16, color=MUTED))
parts.append(K.text(1150, 972, f"run_id {RUN_ID} · A01", width=386, size=16, color=MUTED, align="RIGHT"))

warnings = K.drain_warnings()
dsl = K.document(W, H, parts, background=BG)
dsl_path = OUT / "operations.snapshot"
dsl_path.write_text(dsl, encoding="utf-8")

logger = api.TaskLogger(TASK, TMP)
rec = logger.render(dsl_path, OUT / "operations.png", "visual v3: fit-checked typography and 2-line conclusion")
print("render:", rec["http_status"], rec["content_type"], rec["response_bytes"], "in", rec["elapsed_s"], "s")
for w_ in warnings:
    print(w_)
if rec["http_status"] != 200:
    print((TMP / "responses" / f"{rec['id']}.bin").read_text(encoding="utf-8", errors="replace")[:2000])
    raise SystemExit(1)
w, h = api.measure_png(OUT / "operations.png")
print("png:", w, "x", h)

# ---------------------------------------------------------------- audit json
axes = [
    {"chart": "main_grouped_bars", "unit": "万元", "value_domain": [0, 210000], "zero_line": True,
     "pixel_mapping": {"plot_box": [BX0, BY0, BX1, BY1], "formula": "y = 592 - value / 210000 * 220",
                       "ticks": [{"value": t, "label": str(t // 10000),
                                  "y": round(y_of(t, BY0, BY1, BAR_MAX), 2)} for t in BAR_TICKS]},
     "series": ["net_revenue", "operating_profit"]},
    {"chart": "sessions_mini_bars", "unit": "次", "value_domain": [0, 6000], "zero_line": True,
     "pixel_mapping": {"plot_box": [SX0, SESS_TOP, SX1, SESS_BASE],
                       "formula": "y = 458 - value / 6000 * 68",
                       "ticks": [{"value": t, "y": round(y_of(t, SESS_TOP, SESS_BASE, SESS_MAX), 2)}
                                 for t in (0, 3000, 6000)]}},
    {"chart": "conversion_mini_bars", "unit": "%", "value_domain": [0, 14], "zero_line": True,
     "pixel_mapping": {"plot_box": [SX0, CONV_TOP, SX1, CONV_BASE],
                       "formula": "y = 592 - value / 14 * 72",
                       "ticks": [{"value": t, "y": round(y_of(t, CONV_TOP, CONV_BASE, CONV_MAX), 2)}
                                 for t in (0, 7, 14)]}},
]

conclusion_text = ("退款率是本期利润的最强解释项：6、8 月升至 8.00%，单均经营利润随之跌至 62.7 / 72.0 元。"
                   f"反事实测算：两月退款率回到 5.00% 可多留 {K.fmt_int(recovery)} 元，"
                   f"≈ 9 月经营利润 64,368 元的 {recovery_share:.1f}%。")

payload = {
    "schema_version": 1,
    "task_id": TASK,
    "path_base": "output_dir",
    "generated_at": api.iso_now(),
    "source": "tasks/A01-operations-dashboard/inputs/monthly.csv",
    "months": [
        {
            "month": m["month"], "orders": m["orders"], "gross_revenue": m["gross_revenue"],
            "refund_amount": m["refund_amount"], "operating_cost": m["operating_cost"],
            "sessions": m["sessions"], "net_revenue": m["net_revenue"],
            "operating_profit": m["operating_profit"],
            "refund_rate_pct": round(m["refund_rate"], 4),
            "conversion_rate_pct": round(m["conversion_rate"], 4),
            "profit_margin_pct": round(m["profit_margin"], 4),
            "profit_per_order": round(m["profit_per_order"], 2),
        }
        for m in months
    ],
    "totals": {**tot, "refund_rate_pct": round(tot["refund_rate"], 4),
               "conversion_rate_pct": round(tot["conversion_rate"], 4),
               "profit_margin_pct": round(tot["profit_margin"], 4),
               "conversion_formula": "sum(orders) / sum(sessions)",
               "refund_formula": "sum(refund_amount) / sum(gross_revenue)"},
    "axes": axes,
    "conclusion": {
        "text": conclusion_text,
        "referenced_fields": ["months[2].refund_rate_pct", "months[4].refund_rate_pct",
                              "months[2].profit_per_order", "months[4].profit_per_order",
                              "recovery_cny", "months[5].operating_profit",
                              "recovery_share_of_sep_profit_pct"],
        "values": {"refund_rate_jun_pct": 8.0, "refund_rate_aug_pct": 8.0,
                   "profit_per_order_jun": 62.72, "profit_per_order_aug": 72.02,
                   "recovery_cny": round(recovery, 2),
                   "sep_operating_profit": last["operating_profit"],
                   "recovery_share_of_sep_profit_pct": round(recovery_share, 2)},
        "method": "for each month at 8.00% refund rate: refund_amount - gross_revenue * 0.05",
    },
    "mom_last_month": {"net_revenue_pct": round(mom["net_revenue"], 4),
                       "operating_profit_pct": round(mom["operating_profit"], 4),
                       "orders_pct": round(mom["orders"], 4),
                       "conversion_pp": round(mom["conversion_pp"], 4)},
    "geometry_checks": {
        "bar_scale_shared": True,
        "negative_values_present": False,
        "min_operating_profit": min(m["operating_profit"] for m in months),
        "percent_and_money_axes_separated": True,
    },
    "deliverables": {"png": {"path": "operations.png", "width": w, "height": h},
                     "dsl": "operations.snapshot"},
}
api.write_json(OUT / "computed-data.json", payload)
print("ok. recovery=", round(recovery, 2), "share=", round(recovery_share, 2))
