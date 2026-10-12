"""A16 — build corrected-data.json and the corrected report DSL.

Every number comes from inputs/source.csv; every bar height is value * SCALE from
the axis definition written into corrected-data.json, so geometry and labels cannot
drift apart the way they did in the flawed report.
"""
import csv
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")) / "tmp" /
                       os.environ["SNAPSHOT_RUN_ID"] / "_suite" / "scripts"))
from dslkit import Doc  # noqa: E402

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
TEMP = ROOT / "tmp" / RID / "A16"
SRC = ROOT / "tasks/A16-visual-data-forensics/inputs/source.csv"

rows = list(csv.DictReader(SRC.open(encoding="utf-8")))
D = [{"quarter": r["quarter"], "revenue": int(r["revenue_wan"]), "cost": int(r["cost_wan"])}
     for r in rows]
for d in D:
    d["profit"] = d["revenue"] - d["cost"]
    d["margin_pct"] = round(d["profit"] / d["revenue"] * 100, 1)
TOT = {"revenue": sum(d["revenue"] for d in D), "cost": sum(d["cost"] for d in D)}
TOT["profit"] = TOT["revenue"] - TOT["cost"]
TOT["margin_pct"] = round(TOT["profit"] / TOT["revenue"] * 100, 1)
for i, d in enumerate(D):
    d["revenue_qoq_pct"] = None if i == 0 else round(
        (d["revenue"] - D[i - 1]["revenue"]) / D[i - 1]["revenue"] * 100, 1)
    d["profit_share_pct"] = round(d["profit"] / TOT["profit"] * 100, 1)
best = max(D, key=lambda d: d["profit"])
worst_margin = min(D, key=lambda d: d["margin_pct"])

# ---------- axis definition (shared by the picture and corrected-data.json) ----------
SCALE = 1.4                      # px per 万元
BASE_Y = 508.0                   # y of the zero line
TOP_Y = BASE_Y - 200 * SCALE     # 220 -> axis maximum 200 万元
AXIS_MAX = 200
TICKS = [0, 50, 100, 150, 200]
PLOT_X0, PLOT_X1 = 150, 1196
SLOT = (PLOT_X1 - PLOT_X0) / 4
BAR_W, BAR_GAP = 76, 18
PAGE, CARD, EDGE = "#F4F6FA", "#FFFFFF", "#E3E8F0"
INK, MUTED, SOFT = "#18283F", "#5C6B85", "#8A97AC"
REV, COST = "#245CE4", "#E88E35"
GRID, AXIS = "#E7ECF3", "#C6CFDC"
BAND, PROF_BG, PROF_EDGE = "#EEF3FE", "#FFF7E8", "#F0DDBB"
GOOD, WARN = "#168267", "#B4740E"

corrected = {
    "source_of_truth": "tasks/A16-visual-data-forensics/inputs/source.csv",
    "unit": "万元",
    "rows": D,
    "totals": TOT,
    "derived": {
        "profit_formula": "profit = revenue_wan - cost_wan",
        "margin_formula": "margin_pct = profit / revenue * 100",
        "qoq_formula": "revenue_qoq_pct = (rev[q] - rev[q-1]) / rev[q-1] * 100",
        "profit_share_formula": "profit_share_pct = profit[q] / total_profit * 100",
        "highest_profit_quarter": best["quarter"],
        "highest_profit": best["profit"],
        "highest_profit_share_pct": best["profit_share_pct"],
        "lowest_margin_quarter": worst_margin["quarter"],
        "lowest_margin_pct": worst_margin["margin_pct"],
        "revenue_is_monotonic": all(D[i]["revenue"] >= D[i - 1]["revenue"]
                                    for i in range(1, len(D))),
        "revenue_dip": {"from": D[1]["quarter"], "to": D[2]["quarter"],
                        "delta": D[2]["revenue"] - D[1]["revenue"]},
        "mean_revenue_wan": round(TOT["revenue"] / len(D), 2),
        "mean_revenue_line_y_px": BASE_Y - (TOT["revenue"] / len(D)) * SCALE,
        "q4_above_mean_pct": round((D[3]["revenue"] / (TOT["revenue"] / len(D)) - 1) * 100, 1),
        "profit_share_sum_pct": round(sum(d["profit_share_pct"] for d in D), 1),
    },
    "axis": {
        "kind": "shared zero baseline for both series",
        "zero_y_px": BASE_Y, "top_y_px": TOP_Y, "px_per_wan": SCALE,
        "axis_min": 0, "axis_max": AXIS_MAX, "ticks": TICKS,
        "tick_y_px": {str(t): BASE_Y - t * SCALE for t in TICKS},
        "plot_x": [PLOT_X0, PLOT_X1], "slot_width_px": SLOT,
        "bar_width_px": BAR_W, "bar_gap_px": BAR_GAP,
        "group_centres_px": [PLOT_X0 + SLOT * (i + 0.5) for i in range(4)],
    },
    "bar_geometry_px": {
        d["quarter"]: {
            "revenue": {"value": d["revenue"], "height": round(d["revenue"] * SCALE, 1),
                        "top_y": round(BASE_Y - d["revenue"] * SCALE, 1)},
            "cost": {"value": d["cost"], "height": round(d["cost"] * SCALE, 1),
                     "top_y": round(BASE_Y - d["cost"] * SCALE, 1)},
        } for d in D},
    "headline": {
        "text": f"季度复盘：Q4 收入与利润双高，全年利润 {TOT['profit']} 万元",
        "why": (f"Q4 revenue {best['revenue']} and profit {best['profit']} are both the "
                f"annual maxima; profit share {best['profit_share_pct']}% and margin "
                f"{best['margin_pct']}% are the highest of the four quarters"),
    },
}
(TEMP / "corrected-data.json").write_text(json.dumps(corrected, ensure_ascii=False, indent=1),
                                          encoding="utf-8")

# ------------------------------- the picture -------------------------------
doc = Doc(1280, 900, bg=PAGE, palette={"ink": INK})
FAM = {"reg": "Inter,Noto Sans CJK SC", "med": "Inter Medium,Noto Sans CJK SC",
       "sem": "Inter Semi Bold,Noto Sans CJK SC"}


def txt(x, y, w, h, s, size, color=INK, fam="reg", align="START", spacing=None,
        maxlines=1):
    old = doc.font
    doc.font = FAM["reg"] if fam == "bol" else FAM[fam]
    doc.label(x, y, w, h, s, color=color, size=size, align=align,
              style="BOLD" if fam == "bol" else None, spacing=spacing, maxlines=maxlines)
    doc.font = old


def rect(x, y, w, h, color, radius=None, edge=None):
    doc.pos(x, y, w, h, doc.box(w, h, color=color, radius=radius,
                                border=f"1 SOLID {edge}" if edge else None))


def card(x, y, w, h, color=CARD, radius=14):
    rect(x, y, w, h, color, radius=radius, edge=EDGE if color == CARD else PROF_EDGE)


# header
txt(56, 32, 1000, 44, corrected["headline"]["text"], 34, INK, "bol")
txt(56, 86, 900, 28,
    f"收入 {TOT['revenue']} · 成本 {TOT['cost']} · 利润 {TOT['profit']} 万元；"
    f"Q3 收入环比回落 {abs(D[2]['revenue'] - D[1]['revenue'])} 万元，Q4 冲至 {D[3]['revenue']} 万元",
    22, MUTED, "med")
rect(980, 40, 244, 40, "#E7EFFF", radius=10)
txt(980, 40, 244, 40, "修正版 · 数据源 source.csv", 18, "#1E40AF", "bol", align="CENTER")

# chart card
card(56, 132, 1168, 452)
txt(84, 154, 520, 30, "季度收入与成本对比（共同零起点）", 24, INK, "bol")
txt(84, 188, 700, 24, f"单位：万元 · 柱高 = 数值 × {SCALE} px · 纵轴自 0 起 · "
    f"细横线 = 四季平均 {TOT['revenue'] / len(D):.1f} 万元", 18, SOFT, "reg")
for i, (lab, col) in enumerate((("收入", REV), ("成本", COST))):
    sx = 968 + i * 122
    rect(sx, 160, 16, 16, col, radius=4)
    txt(sx + 24, 156, 80, 24, lab, 18, INK, "med")

# highlight band behind Q4
cx3 = PLOT_X0 + SLOT * 3.5
rect(cx3 - SLOT / 2 + 6, 224, SLOT - 12, BASE_Y - 224, BAND, radius=10)

# reference line: the four-quarter mean revenue, derived from source.csv
AVG = TOT["revenue"] / len(D)
AVG_Y = int(round(BASE_Y - AVG * SCALE))

# gridlines + tick labels
for t in TICKS:
    y = BASE_Y - t * SCALE
    doc.rect(PLOT_X0, int(y), PLOT_X1 - PLOT_X0, 1 if t else 2, AXIS if t == 0 else GRID)
    txt(96, y - 11, 46, 22, str(t), 18, MUTED, "reg", align="END")

doc.rect(PLOT_X0, AVG_Y, PLOT_X1 - PLOT_X0, 2, "#AEBDCE")

for i, d in enumerate(D):
    c = PLOT_X0 + SLOT * (i + 0.5)
    hi = d["quarter"] == best["quarter"]
    for k, (val, col) in enumerate(((d["revenue"], REV), (d["cost"], COST))):
        x = c - BAR_W - BAR_GAP / 2 + k * (BAR_W + BAR_GAP)
        h = round(val * SCALE)
        top = int(BASE_Y) - h
        doc.pos(x, top, BAR_W, h, doc.box(BAR_W, h, color=col, radius=6))
        doc.rect(x, int(BASE_Y) - 6, BAR_W, 6, col)
        txt(x - 12, top - 28, BAR_W + 24, 22, str(val), 18,
            "#1E40AF" if (k == 0 and hi) else INK, "bol" if hi else "med", align="CENTER")
    txt(c - 60, 512, 120, 28, d["quarter"], 22, INK, "bol", align="CENTER")
    txt(c - 78, 538, 156, 24, f"利润 {d['profit']} · {d['margin_pct']}%", 20,
        SOFT if not hi else "#1E40AF", "med", align="CENTER")

# profit detail card
card(56, 600, 700, 248)
txt(84, 620, 300, 30, "利润明细", 24, INK, "bol")
COLS = [("季度", 100, 96, "START"), ("收入", 224, 100, "END"), ("成本", 340, 100, "END"),
        ("利润", 456, 100, "END"), ("利润率", 572, 110, "END"), ("占全年利润", 700, 104, "END")]
rect(84, 664, 644, 30, PAGE, radius=8)
for name, x, w, al in COLS:
    txt(x - (0 if al == "START" else w), 664, w, 30, name, 18, MUTED, "bol", align=al,
        spacing=0.6)
y = 694
for d in D:
    hi = d["quarter"] == best["quarter"]
    if y > 694:
        doc.rect(84, y - 1, 644, 1, "#EDF1F7")
    txt(100, y, 90, 28, d["quarter"], 22, INK, "bol")
    for (name, x, w, al), val, col in zip(
            COLS[1:], (d["revenue"], d["cost"], f"{d['profit']} 万元",
                       f"{d['margin_pct']}%", f"{d['profit_share_pct']}%"),
            (INK, INK, "#1E40AF", GOOD if d["margin_pct"] >= 25 else WARN, SOFT)):
        txt(x - w, y, w, 28, str(val), 22, col, "med", align=al)
    y += 30
doc.rect(84, y, 644, 2, AXIS)
txt(100, y + 4, 90, 28, "全年", 22, INK, "bol")
for (name, x, w, al), val in zip(COLS[1:], (TOT["revenue"], TOT["cost"],
                                            f"{TOT['profit']} 万元",
                                            f"{TOT['margin_pct']}%", "100.0%")):
    txt(x - w, y + 4, w, 28, str(val), 22, INK, "bol", align=al)

# focus card
card(780, 600, 444, 248, color=PROF_BG)
rect(781, 601, 5, 246, "#E0A93B", radius=3)
txt(808, 620, 390, 30, f"重点观察 · {best['quarter']}", 24, INK, "bol")
lines = [(f"收入 {best['revenue']} 万元，环比 +{best['revenue_qoq_pct']}%", INK),
         (f"利润 {best['profit']} 万元，占全年 {best['profit_share_pct']}%", INK),
         (f"利润率 {best['margin_pct']}%，四季度最高", GOOD),
         (f"提示：{worst_margin['quarter']} 利润率 {worst_margin['margin_pct']}% 最低", WARN)]
yy = 662
for s, col in lines:
    doc.dot(812, yy + 11, 8, col)
    txt(828, yy, 372, 26, s, 22, col if col != INK else INK, "med")
    yy += 34
txt(808, yy + 4, 390, 22, "结论由 source.csv 计算得出，非沿用旧稿", 18, SOFT, "reg")

txt(56, 852, 1168, 24,
    "修正自 flawed-report.png：零起点 · 柱高 = 数值 × 1.4px · 图例与柱色一致 · "
    "Q3 利润 42 → 32 · 重点季度 Q3 → Q4", 18, SOFT, "reg")

(TEMP / "corrected-v01.snapshot").write_text(doc.dsl(), encoding="utf-8")
print("dsl bytes", len(doc.dsl()))
print(json.dumps(corrected["derived"], ensure_ascii=False))
