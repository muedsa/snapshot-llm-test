#!/usr/bin/env python3
"""A04: Simpson-style conversion paradox infographic, 1600x1000."""
import csv, json, os, sys
from pathlib import Path
TOOLS = os.environ["TOOLS"]; sys.path.insert(0, TOOLS)
from dsl import Canvas, LATIN
import suite

T = "A04"
SRC = suite.ROOT / "tasks/A04-conversion-paradox/inputs/conversion.csv"
rows = list(csv.DictReader(SRC.read_text(encoding="utf-8").splitlines()))
D = {}
for r in rows:
    D[(r["period"], r["channel"])] = (int(r["visits"]), int(r["conversions"]))
CH = ["直接访问", "推广访问"]; P = ["前期", "后期"]
CC = {"直接访问": "#2563EB", "推广访问": "#F59E0B"}
INK, MUTED, LINE, WHITE, BG = "#0F172A", "#5B6B85", "#DDE5F0", "#FFFFFF", "#F4F7FC"

groups = []
for p in P:
    for ch in CH:
        v, cv = D[(p, ch)]
        groups.append({"period": p, "channel": ch, "visits": v, "conversions": cv,
                        "fraction": "%d/%d" % (cv, v), "rate": cv / v})
periods = []
for p in P:
    tv = sum(D[(p, ch)][0] for ch in CH); tc = sum(D[(p, ch)][1] for ch in CH)
    periods.append({"period": p, "visits": tv, "conversions": tc,
                     "fraction": "%d/%d" % (tc, tv), "rate": tc / tv,
                     "composition": {ch: D[(p, ch)][0] / tv for ch in CH},
                     "weighted": " + ".join("%.4f×%.4f" % (D[(p, ch)][0] / tv, D[(p, ch)][1] / D[(p, ch)][0]) for ch in CH)})
mean_rates = [sum(g["rate"] for g in groups if g["period"] == p) / 2 for p in P]

c = Canvas(1600, 1000, BG)
c.gradient(0, 0, 1600, 106, ["#0B1B35", "#16386F"], begin="CENTER_LEFT", end="CENTER_RIGHT")
c.text(48, 16, 1200, 48, "转化变化，为什么不能只看平均？", 36, WHITE, bold=True)
c.text(48, 68, 1400, 28, "两期 × 两渠道 · 单位：访问数（次）、成交数（笔）、转化率（%） · 数据来自 conversion.csv", 20, "#BBD3F2")
c.text(1200, 22, 352, 32, "STRUCTURE / VISION 2026", 18, "#8FB6EA", align="RIGHT", font=LATIN)

# ---- panel 1: grouped rate chart, shared 0-100% scale
X1, Y1, W1, H1 = 48, 126, 500, 520
c.rect(X1, Y1, W1, H1, WHITE, radius=16, border="1 SOLID " + LINE)
c.text(70, 140, 460, 32, "① 渠道分组转化率", 24, INK, bold=True)
c.text(70, 174, 460, 26, "同一 0–100% 纵轴；四根柱来自四个原始分数", 18, MUTED)
PL, PR, PB, PT = 110, 520, 560, 230
for v in (0, .25, .5, .75, 1.0):
    yy = PB - v * (PB - PT)
    c.hline(PL, yy, PR - PL, 1 if v else 2, LINE if v else "#94A3B8")
    c.text(60, yy - 12, 46, 24, "%d%%" % (v * 100), 18, MUTED, align="RIGHT", font=LATIN)
BW = 62
for i, g in enumerate(groups):
    bx = 150 + i * 95
    h = g["rate"] * (PB - PT)
    c.bar(bx, PB - h, BW, h, CC[g["channel"]], radius=6)
    c.text(bx - 12, PB - h - 30, BW + 24, 26, "%.2f%%" % (g["rate"] * 100), 18, CC[g["channel"]], bold=True, align="CENTER", font=LATIN)
    c.text(bx - 20, 570, BW + 40, 26, g["period"] + g["channel"][:2], 18, INK, align="CENTER")
    c.text(bx - 20, 596, BW + 40, 24, g["fraction"], 18, MUTED, align="CENTER", font=LATIN)
c.rect(70, 626, 18, 14, CC["直接访问"], radius=3)
c.text(94, 620, 130, 26, "直接访问", 18, INK)
c.rect(240, 626, 18, 14, CC["推广访问"], radius=3)
c.text(264, 620, 130, 26, "推广访问", 18, INK)

# ---- panel 2: equal-length stacked composition
X2, W2 = 572, 470
c.rect(X2, Y1, W2, H1, WHITE, radius=16, border="1 SOLID " + LINE)
c.text(594, 140, 430, 32, "② 访问构成（每期等长）", 24, INK, bold=True)
c.text(594, 174, 430, 26, "分段按真实占比；两期总访问量均为 10,000 次", 18, MUTED)
SX, SW, SH = 612, 390, 72
for i, pd in enumerate(periods):
    y = 250 + i * 170
    c.text(SX, y - 34, 200, 28, pd["period"], 22, INK, bold=True)
    c.text(SX + 200, y - 32, 190, 26, "10,000 次", 18, MUTED, align="RIGHT", font=LATIN)
    x = SX
    for ch in CH:
        w = SW * pd["composition"][ch]
        c.rect(x, y, w, SH, CC[ch])
        lab = ("%s %d%%" % (ch, round(pd["composition"][ch] * 100))) if w >= 150 else ("%d%%" % round(pd["composition"][ch] * 100))
        c.text(x + 4, y + 12, w - 8, 26, lab, 18, WHITE, bold=True, align="CENTER")
        c.text(x + 4, y + 40, w - 8, 24, format(D[(pd["period"], ch)][0], ","), 18, WHITE, align="CENTER", font=LATIN)
        x += w
    c.rect(SX, y, SW, SH, "transparent", radius=0, border="1 SOLID #FFFFFF")
c.text(594, 594, 430, 26, "前期 直接 80% → 后期 直接 20%", 18, INK)
c.text(594, 620, 430, 24, "蓝=直接访问，橙=推广访问；权重被大幅转移", 18, MUTED)

# ---- panel 3: overall comparison
X3, W3 = 1066, 486
c.rect(X3, Y1, W3, H1, WHITE, radius=16, border="1 SOLID " + LINE)
c.text(1088, 140, 440, 32, "③ 总体转化率对照", 24, INK, bold=True)
c.text(1088, 174, 440, 26, "总成交 ÷ 总访问，不平均渠道比例", 18, MUTED)
for i, pd in enumerate(periods):
    y = 220 + i * 152
    c.rect(1088, y, 442, 140, "#F1F6FF" if i == 0 else "#FFF3E8", radius=12)
    c.text(1106, y + 8, 250, 28, pd["period"] + "总体", 22, INK, bold=True)
    c.text(1106, y + 40, 410, 62, "%.2f%%" % (pd["rate"] * 100), 46, "#1D4ED8" if i == 0 else "#C2410C", bold=True, font=LATIN)
    c.text(1106, y + 106, 410, 26, "%s = %s" % (pd["fraction"], "%.4f" % pd["rate"]), 18, MUTED, font=LATIN)
c.text(1088, 528, 442, 30, "总体 ↓ 9.40 个百分点", 22, "#DC2626", bold=True)
c.text(1088, 562, 442, 52, "加权：Σ(渠道访问占比 × 渠道转化率)；\n平均渠道比例会得到相反方向。", 18, MUTED)
c.text(1088, 618, 442, 24, "错误口径均值：%.2f%% → %.2f%%" % (mean_rates[0] * 100, mean_rates[1] * 100), 18, "#B45309", font=LATIN)

# ---- bottom: raw table + conclusion
c.rect(48, 664, 760, 296, WHITE, radius=16, border="1 SOLID " + LINE)
c.text(70, 676, 700, 30, "原始分子 / 分母核对表", 24, INK, bold=True)
cols = [(70, 130, "期 / 渠道", "LEFT"), (210, 120, "访问数", "RIGHT"),
        (340, 120, "成交数", "RIGHT"), (470, 130, "精确分数", "RIGHT"), (610, 180, "转化率", "RIGHT")]
c.rect(64, 712, 728, 36, "#EEF3FB", radius=6)
for x, w, h, al in cols:
    c.text(x, 714, w, 30, h, 18, "#31456B", bold=True, align=al)
for i, g in enumerate(groups):
    y = 750 + i * 32
    if i % 2: c.rect(64, y - 4, 728, 32, "#F8FAFE")
    vals = [g["period"] + " " + g["channel"][:2], format(g["visits"], ","),
            format(g["conversions"], ","), g["fraction"], "%.2f%%" % (g["rate"] * 100)]
    for j, ((x, w, h, al), v) in enumerate(zip(cols, vals)):
        c.text(x, y, w, 30, v, 20, CC[g["channel"]] if j == 4 else INK, align=al,
               font=LATIN if j in (1, 2, 3, 4) else None)
for i, pd in enumerate(periods):
    y = 750 + (4 + i) * 32
    c.rect(64, y - 5, 728, 32, "#E8EEF9")
    for j, ((x, w, h, al), v) in enumerate(zip(cols, [pd["period"] + " 合计", format(pd["visits"], ","),
                                                       format(pd["conversions"], ","), pd["fraction"], "%.2f%%" % (pd["rate"] * 100)])):
        c.text(x, y - 2, w, 30, v, 20, INK, bold=True, align=al, font=LATIN if j else None)

c.rect(832, 664, 720, 296, "#0B1B35", radius=16)
c.text(856, 678, 670, 32, "主结论 · 由数据支持", 24, "#7DD3FC", bold=True)
c.text(856, 716, 672, 118,
       "两渠道转化率都上升（直接 30.00%→35.00%，推广 10.00%→12.00%），总体却从 26.00% 降到 16.60%。"
       "高转化的直接访问占比由 80% 降至 20%，权重转移压过组内改善。", 22, "#E8F0FC")
c.rect(856, 840, 672, 96, "#163A6B", radius=10)
c.text(870, 848, 644, 30, "限制：不能由该数据证明因果", 22, "#FCD34D", bold=True)
c.text(870, 880, 644, 48, "数据只显示构成与结果的相关变化，无法判断渠道调整、流量质量或其他因素是否导致下降；也不能把同期不同渠道的绝对成交量当作转化率。", 18, "#C6DCF7")
c.text(48, 970, 1504, 24, "单位：前期/后期为期名；访问数=次、成交数=笔、转化率=%。率图 0–100% 共用尺度；构成图每期等长 390px 并按真实占比分段。", 16, MUTED)

dsl = c.render()
out = suite.out_dir(T)
(out / "conversion-story.snapshot").write_text(dsl, encoding="utf-8")
v = suite.tmp_dir(T, os.environ.get("BUILD_VERSION", "v1"))
(v / "conversion-story.snapshot").write_text(dsl, encoding="utf-8")

audit = {
    "schema_version": 1, "task_id": T, "path_base": "output_dir",
    "groups": [{"period": g["period"], "channel": g["channel"], "numerator": g["conversions"],
                "denominator": g["visits"], "exact_fraction": g["fraction"],
                "rate": round(g["rate"], 6), "display_percent": "%.2f%%" % (g["rate"] * 100)} for g in groups],
    "periods": [{"period": p["period"], "numerator": p["conversions"], "denominator": p["visits"],
                 "exact_fraction": p["fraction"], "rate": round(p["rate"], 6),
                 "display_percent": "%.2f%%" % (p["rate"] * 100),
                 "weighted_formula": p["weighted"],
                 "composition": {k: round(v, 6) for k, v in p["composition"].items()}} for p in periods],
    "axes": [
        {"chart": "group_rate", "unit": "比例 / %", "min": 0, "max": 1.0,
         "ticks": [0, .25, .5, .75, 1.0], "zero_line_px": PB,
         "pixel_mapping": "y = 560 - rate*(560-230)"},
        {"chart": "composition", "unit": "访问数占比", "equal_length_px": SW,
         "segments": "width = 390 * visits/10000", "note": "两期总长相等"},
        {"chart": "overall", "unit": "比例 / %", "values": [round(p["rate"], 6) for p in periods]}
    ],
    "conclusions": [
        {"claim": "两渠道各自转化率均上升但总体下降，源于访问构成从高转化的直接访问（80%）转向推广访问（80%）",
         "referenced_values": ["30.00%→35.00%", "10.00%→12.00%", "26.00%→16.60%", "80%→20%"],
         "method": "总体=总成交/总访问；加权式 Σ(占比×组率)"},
        {"claim": "不能由该数据证明因果",
         "type": "limitation",
         "detail": "仅显示构成与结果的相关变化；无法识别渠道调整、流量质量或其他混杂因素；不得把绝对成交量当作转化率"},
    ],
    "wrong_methods": {"mean_of_channel_rates": ["%.2f%%" % (mean_rates[0] * 100), "%.2f%%" % (mean_rates[1] * 100)],
                      "note": "平均渠道比例会给出与总体相反的方向，仅作反例展示，不作为结论"},
    "evidence": {"png": "conversion-story.png", "dsl": "conversion-story.snapshot"},
}
(out / "analysis.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("A04 groups=%d periods=%d overall=%s" % (len(groups), len(periods), [round(p["rate"] * 100, 2) for p in periods]))
