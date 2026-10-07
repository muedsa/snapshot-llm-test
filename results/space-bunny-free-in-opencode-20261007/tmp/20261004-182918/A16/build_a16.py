# -*- coding: utf-8 -*-
"""A16 · rebuild the quarterly-review report from inputs/source.csv.

The flawed colleague PNG was measured first (analyze_flawed*.py, measure_regions.py);
this script encodes the corrected geometry only -- every bar height comes from the CSV.

  python build_a16.py preview   -> render into tmp/<run>/A16/preview/
  python build_a16.py final     -> render into outputs/<run>/A16/ (service bytes, no post-processing)
"""
import csv, json, os, shutil, sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import snapkit, dsllib as D, state as S

TASK = "A16"
OUT = os.path.join(S.OUT_ROOT, TASK)
TMP = os.path.join(S.TMP_ROOT, TASK)
CSV = os.path.join(ROOT, "tasks", "A16-visual-data-forensics", "inputs", "source.csv")
snapkit.configure(TASK, OUT, TMP)

MODE = sys.argv[1] if len(sys.argv) > 1 else "preview"
TAG = sys.argv[2] if len(sys.argv) > 2 else "v01"

# ---------------------------------------------------------------- data
rows = list(csv.DictReader(open(CSV, encoding="utf-8")))
data = [{"quarter": r["quarter"], "revenue": int(r["revenue_wan"]),
         "cost": int(r["cost_wan"])} for r in rows]
for d in data:
    d["profit"] = d["revenue"] - d["cost"]
    d["margin"] = d["profit"] / d["revenue"]
    d["cost_ratio"] = d["cost"] / d["revenue"]
    d["qoq_revenue"] = None
for i in range(1, len(data)):
    data[i]["qoq_revenue"] = data[i]["revenue"] / data[i - 1]["revenue"] - 1.0
tot_rev = sum(d["revenue"] for d in data)
tot_cost = sum(d["cost"] for d in data)
tot_profit = sum(d["profit"] for d in data)
tot_margin = tot_profit / tot_rev
best = max(data, key=lambda d: d["profit"])

# ---------------------------------------------------------------- style
W, H = 1280, 900
BG = "#F4F6FAFF"
CARD = "#FFFFFFFF"
CARD_LINE = "1 SOLID #E3E8EF"
CARD_SHADOW = "0 4 18 0 #0F172A12"
INK = "#0F172AFF"
MUTED = "#64748BFF"
LABEL = "#334155FF"
GRID = "#E6EAF2FF"
AXIS = "#94A3B8FF"
REV = "#2563EBFF"
COST = "#F97316FF"
GAIN = "#059669FF"
CALLOUT_BG = "#F0FDF6FF"
CALLOUT_LINE = "1 SOLID #BBF0D6"

# ---------------------------------------------------------------- geometry
CH_X, CH_Y, CH_W, CH_H = 56, 158, 1168, 424          # chart card 158..582
PL, PR = 162.0, 1200.0                                # plot x range
BASE_Y, TOP_V, TOP_Y = 530.0, 200.0, 246.0            # zero baseline at y=530
SCALE = (BASE_Y - TOP_Y) / TOP_V                      # 1.42 px per 万元
TICKS = [0, 50, 100, 150, 200]
BAR_W, BAR_GAP = 68.0, 16.0

PF_X, PF_Y, PF_W, PF_H = 56, 602, 756, 246             # profit card 602..848
CO_X, CO_Y, CO_W, CO_H = 836, 602, 388, 246           # callout card

kids = []


def panel(x, y, w, h, content, fill=CARD, radius=18, border=CARD_LINE,
          shadow=CARD_SHADOW):
    """Card background + full-canvas Stack for its absolutely positioned children.

    A <Container> may only hold ONE child, so the children go into a Stack.
    The Stack is laid out at (0,0) with the full canvas size, which keeps every
    child's coordinates in page space (a Stack nested inside the card box would
    re-base the coordinates onto the card's top-left corner).
    """
    return "\n".join([
        D.box(x, y, w, h, color=fill, radius=radius, border=border, shadow=shadow),
        D.box(0, 0, W, H, children=[D.stack(content, W, H)]),
    ])


# ---------------------------------------------------------------- header
kids.append(D.text_el("季度复盘 · 依据 inputs/source.csv 全量四个季度重制",
                      x=56, y=30, w=900, h=26, size=18, color=REV, ls=1.2))
kids.append(D.text_el("季度复盘：Q4 利润 %d 万元居首，占全年利润的 %.1f%%"
                      % (best["profit"], best["profit"] / tot_profit * 100),
                      x=56, y=54, w=1170, h=56, size=40, style="BOLD", color=INK))
kids.append(D.text_el(
    "全年收入 %d 万元、成本 %d 万元、利润 %d 万元；Q3 收入环比回落 %.1f%%，Q4 收入与利润创全年新高"
    % (tot_rev, tot_cost, tot_profit, abs(data[2]["qoq_revenue"]) * 100),
    x=56, y=114, w=1170, h=32, size=22, color=MUTED))

# ---------------------------------------------------------------- chart card
chart = []
chart.append(D.text_el("收入与成本对比（单位：万元）", x=88, y=180, w=560, h=36,
                       size=26, style="BOLD", color=INK))
# legend (right aligned inside the card header)
for i, (lab, col) in enumerate((("收入", REV), ("成本", COST))):
    x = 1032 + i * 94
    chart.append(D.box(x, 192, 18, 18, color=col, radius=4))
    chart.append(D.text_el(lab, x=x + 26, y=187, w=60, h=28, size=20, color=INK))

for v in TICKS:
    y = BASE_Y - v * SCALE
    if v == 0:
        chart.append(D.hline(PL, PR, y, AXIS, 2))
    else:
        chart.append(D.hline(PL, PR, y, GRID, 1))
    chart.append(D.text_el(str(v), x=84, y=y - 13, w=66, h=26, size=18,
                           color=MUTED, align="RIGHT"))

gw = (PR - PL) / len(data)
pair_w = BAR_W * 2 + BAR_GAP
bar_geom = []
for i, d in enumerate(data):
    gx = PL + gw * i + (gw - pair_w) / 2.0
    gc = PL + gw * i + gw / 2.0
    for j, (key, col) in enumerate((("revenue", REV), ("cost", COST))):
        v = d[key]
        bx = gx + j * (BAR_W + BAR_GAP)
        by = BASE_Y - v * SCALE
        chart.append(D.box(bx, by, BAR_W, BASE_Y - by, color=col,
                           radii={"TopLeft": 8, "TopRight": 8}))
        chart.append(D.text_el(str(v), x=bx - 14, y=by - 27, w=BAR_W + 28, h=26,
                               size=18, color=LABEL, align="CENTER",
                               extra={"fontFeatures": "tnum=2"}))
        bar_geom.append({"quarter": d["quarter"], "series": key, "value": v,
                         "x_left": round(bx, 2), "x_right": round(bx + BAR_W - 1, 2),
                         "y_top": round(by, 2), "y_bottom": round(BASE_Y - 1, 2),
                         "height_px": round(BASE_Y - by, 2)})
    chart.append(D.text_el("%s · 利润 %d" % (d["quarter"], d["profit"]),
                           x=gc - 100, y=540, w=200, h=30, size=20, color=INK,
                           align="CENTER"))
kids.append(panel(CH_X, CH_Y, CH_W, CH_H, chart))

# ---------------------------------------------------------------- profit table
rows_def = [("收入", "revenue", "{:,.0f}", False, 1),
            ("成本", "cost", "{:,.0f}", False, 1),
            ("利润", "profit", "{:,.0f}", True, 1),
            ("利润率", "margin", "{:.1f}%", False, 100)]
col_edges = [324.0, 440.0, 556.0, 672.0, 788.0]
COL_W = 116.0
pt = []
pt.append(D.text_el("利润明细（单位：万元）", x=88, y=624, w=400, h=32,
                    size=24, style="BOLD", color=INK))
hdr = ["指标"] + [d["quarter"] for d in data] + ["全年"]
pt.append(D.text_el(hdr[0], x=88, y=672, w=200, h=26, size=18, color=MUTED))
for i, lab in enumerate(hdr[1:]):
    pt.append(D.text_el(lab, x=col_edges[i] - COL_W, y=672, w=COL_W, h=26, size=18,
                        color=MUTED, align="RIGHT",
                        extra={"fontFeatures": "tnum=2"}))
pt.append(D.hline(88, 788, 702, "#CBD5E1FF", 1))
pt.append(D.vline(676, 702, 832, GRID, 1))
totals = {"revenue": tot_rev, "cost": tot_cost, "profit": tot_profit,
          "margin": tot_margin}
for r, (name, key, fmt, emph, scale) in enumerate(rows_def):
    y = 712 + r * 34
    col = GAIN if emph else INK
    pt.append(D.text_el(name, x=88, y=y, w=200, h=28, size=22,
                        style="BOLD" if emph else None, color=col))
    for i, d in enumerate(data):
        pt.append(D.text_el(fmt.format(d[key] * scale), x=col_edges[i] - COL_W, y=y,
                            w=COL_W, h=28, size=22, style="BOLD" if emph else None,
                            color=col, align="RIGHT",
                            extra={"fontFeatures": "tnum=2"}))
    pt.append(D.text_el(fmt.format(totals[key] * scale), x=col_edges[4] - COL_W,
                        y=y, w=COL_W, h=28, size=22,
                        style="BOLD" if emph else None, color=col, align="RIGHT",
                        extra={"fontFeatures": "tnum=2"}))
    if r < len(rows_def) - 1:
        pt.append(D.hline(88, 788, y + 30, "#EEF2F7FF", 1))
kids.append(panel(PF_X, PF_Y, PF_W, PF_H, pt))

# ---------------------------------------------------------------- callout
bullets = [
    "收入 %d 万元 · 全年最高" % best["revenue"],
    "成本 %d 万元 · 同步走高" % best["cost"],
    "利润 %d 万元 · 四季居首" % best["profit"],
    "利润率 %.1f%% · 全年最高" % (best["margin"] * 100),
    "占全年利润 %.1f%%" % (best["profit"] / tot_profit * 100),
]
cal = [D.text_el("重点观察 · %s" % best["quarter"], x=868, y=624, w=340, h=32,
                 size=24, style="BOLD", color=GAIN)]
for i, line in enumerate(bullets):
    y = 670 + i * 30
    cal.append(D.box(868, y + 9, 10, 10, color=GAIN, radius=5))
    cal.append(D.text_el(line, x=888, y=y, w=316, h=28, size=22, color=INK))
cal.append(D.text_el("四个季度全部由同一比例尺绘制", x=868, y=820, w=340, h=24,
                     size=18, color=MUTED))
kids.append(panel(CO_X, CO_Y, CO_W, CO_H, cal, fill=CALLOUT_BG, border=CALLOUT_LINE,
                   shadow=None))

# ---------------------------------------------------------------- footer
kids.append(D.text_el(
    "数据源：inputs/source.csv · 利润 = 收入 − 成本 · 利润率 = 利润 ÷ 收入 · "
    "纵轴 0–200 万元，刻度 50 万元，八根柱共用零起点与同一比例尺",
    x=56, y=864, w=1170, h=26, size=18, color=MUTED))

dsl = D.snapshot([D.stack(kids, W, H)], W, H, bg=BG)

draft_dir = os.path.join(TMP, "drafts")
os.makedirs(draft_dir, exist_ok=True)
n = len([f for f in os.listdir(draft_dir) if f.startswith("v")]) + 1
draft = os.path.join(draft_dir, "v%02d.snapshot" % n)
with open(draft, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(dsl)

if MODE == "final":
    r = snapkit.render(dsl, "corrected-report.png", "corrected-report.snapshot",
                       final=True)
else:
    r = snapkit.render(dsl, "a16-%s.png" % TAG, "a16-%s.snapshot" % TAG,
                       final=False, out_dir=os.path.join(TMP, "preview"))
print("render ok=%s status=%s bytes=%s" % (r.get("ok"), r.get("status"), r.get("bytes")))
print("draft:", draft)

# ---------------------------------------------------------------- side data
axis = {
    "chart_card_bbox_px": [CH_X, CH_Y, CH_X + CH_W - 1, CH_Y + CH_H - 1],
    "plot_x_range_px": [PL, PR],
    "baseline_y_px": BASE_Y,
    "value_200_y_px": TOP_Y,
    "domain_wan": [0, TOP_V],
    "ticks_wan": TICKS,
    "tick_y_px": {str(v): round(BASE_Y - v * SCALE, 2) for v in TICKS},
    "pixels_per_wan": round(SCALE, 4),
    "common_zero_baseline": True,
    "truncated_axis": False,
    "bar_width_px": BAR_W,
    "group_gap_px": BAR_GAP,
    "group_centers_px": [round(PL + gw * i + gw / 2.0, 2) for i in range(len(data))],
    "series_order_left_to_right": ["revenue", "cost"],
    "colors": {"revenue": REV, "cost": COST},
}
corrected = {
    "task": TASK,
    "source_file": "inputs/source.csv",
    "unit": "万元",
    "source_rows": data,
    "totals": {"revenue_wan": tot_rev, "cost_wan": tot_cost, "profit_wan": tot_profit,
               "margin": round(tot_margin, 6),
               "cost_ratio": round(tot_cost / tot_rev, 6)},
    "derived_fields": {
        "profit": "profit_wan = revenue_wan - cost_wan（逐季度，先减后合计）",
        "margin": "margin = profit_wan / revenue_wan，四舍五入到 0.1% 显示",
        "cost_ratio": "cost_ratio = cost_wan / revenue_wan",
        "qoq_revenue": "qoq_revenue = revenue_wan[i] / revenue_wan[i-1] - 1（Q1 无环比）",
        "annual_margin": "全年利润率 = 全年利润 / 全年收入，不等于四个季度利润率的平均",
    },
    "key_quarter_argument": {
        "quarter": best["quarter"],
        "why": ["利润 %d 万元为四个季度最高（Q1 %d / Q2 %d / Q3 %d / Q4 %d）"
                % (data[0]["profit"], data[1]["profit"], data[2]["profit"],
                   data[3]["profit"], best["profit"]),
                "收入 %d 万元为全年最高" % best["revenue"],
                "利润率 %.1f%% 为全年最高" % (best["margin"] * 100),
                "占全年利润 %d 万元的 %.1f%%" % (tot_profit, best["profit"] / tot_profit * 100),
                "对照：Q3 收入环比 %.1f%%，是唯一环比回落的季度" % (data[2]["qoq_revenue"] * 100)],
    },
    "axis": axis,
    "bar_geometry": bar_geom,
    "corrected_from_flaws": {
        "title": "由 “Q3利润最高” 改为 “Q4 利润 %d 万元居首，占全年利润的 %.1f%%”"
                 % (best["profit"], best["profit"] / tot_profit * 100),
        "subtitle": "由 “收入持续上升，全年保持增长” 改为全年合计 + Q3 环比回落 %.1f%% 的事实描述"
                    % (abs(data[2]["qoq_revenue"]) * 100),
        "legend": "蓝=收入、橙=成本，与 source.csv 的 revenue_wan / cost_wan 对应（原稿图例左右互换）",
        "y_axis": "由 100–200 截断轴改为 0–200 零起点轴，刻度 50 万元",
        "bars": "每根柱高 = (BASE_Y - value * 1.42 px/万元)，8 根柱共用同一比例尺与同一零基线",
        "profit_table": "Q3 利润由 42 更正为 32 万元（128 − 96），并补全年合计列与利润率行",
    },
}
cd_path = os.path.join(OUT, "corrected-data.json")
with open(cd_path, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(corrected, fh, ensure_ascii=False, indent=1)
shutil.copyfile(cd_path, os.path.join(TMP, "corrected-data.json"))
print("corrected-data.json ->", cd_path)

for w in D.warnings():
    print("WARN", w)
print("warnings:", len(D.warnings()))