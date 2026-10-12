#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A22 round builder.  Usage: python build_a22.py <1|2|3>

Emits outputs/20261004-182918/A22/<round-subdir>/{dashboard.png, dashboard.snapshot,
computed-data.json, layout-map.json} (+ change-audit.json for rounds 2 and 3).
The .snapshot next to the PNG is byte-identical to the text that was POSTed.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))

import snapkit  # noqa: E402
import dsllib as D  # noqa: E402
import a22lib as L  # noqa: E402

ROUND = int(sys.argv[1])
SUB = L.ROUND_META[ROUND]["subdir"]
TASK = "A22"
OUT = os.path.join(ROOT, "outputs", "20261004-182918", TASK, SUB)
TMP = os.path.join(ROOT, "tmp", "20261004-182918", TASK)
os.makedirs(OUT, exist_ok=True)
snapkit.configure(TASK, os.path.join(ROOT, "outputs", "20261004-182918", TASK), TMP)

rows, corrections, added_rows = L.rows_for_round(ROUND)
d = L.derive(rows)
ms, tot, axis = d["months"], d["total"], d["axis"]
conc = L.conclusion_for(ROUND, d)
period = "%s ~ %s" % (ms[0]["month"], ms[-1]["month"])
E = L.Emitter()
R = L.REGIONS


def f(v):
    return "{:,.0f}".format(v)


# ============================================================ header
h = R["header"]
E.tb("header.title", "%s 经营驾驶舱 · 财务口径更正版" % "2026 财年",
     h["x"], h["y"] + 2, w=900, h=46, size=L.TITLE_SIZE, color=L.INK, font=D.UI,
     style="BOLD")
badge = "ROUND-%02d" % ROUND
bw_px = L.str_w(badge, L.BODY_SIZE) + 44
E.bb("header.badge", h["x"] + h["w"] - bw_px, h["y"] + 6, bw_px, 40,
     color="#1D4ED8FF", radius=20)
E.tb("header.badge.text", badge, h["x"] + h["w"] - bw_px, h["y"] + 15, w=bw_px, h=26,
     size=L.BODY_SIZE, color="#FFFFFFFF", font=D.UI, style="BOLD", align="CENTER")
sub = "数据源 inputs/monthly.csv ｜ 期间 %s（%d 个月） ｜ 净收入=收入−退款" % (period, len(ms))
E.tb("header.subtitle", sub, h["x"], h["y"] + 56, w=L.SUBTITLE_W, h=32,
     size=L.BODY_SIZE, color=L.MUTED, font=D.UI)
verdict = ("第 1 轮 · 按原值渲染，未做任何更正" if ROUND == 1 else
           ("第 2 轮 · 08 退款=25,048，09 成本=208,000" if ROUND == 2 else
            "第 3 轮 · 新增 2026-10，第 2 轮更正仍有效"))
vx = h["x"] + h["w"] - L.VERDICT_W
E.tb("header.verdict", verdict, vx, h["y"] + 58, w=L.VERDICT_W, h=30,
     size=L.BODY_SIZE, color="#B45309FF", font=D.UI, align="RIGHT")

# ============================================================ KPI row
k = R["kpi_row"]
kpi_defs = [
    ("总净收入", "net_revenue", f(tot["net_revenue"]), L.NET_C, "元",
     "占毛收入 %.2f%%" % (tot["net_revenue"] / tot["gross_revenue"] * 100)),
    ("总经营利润", "operating_profit", f(tot["operating_profit"]),
     L.LOSS_C if tot["operating_profit"] < 0 else L.PROF_C, "元",
     "利润率 %.2f%%" % (tot["margin"] * 100)),
    ("总订单", "orders", f(tot["orders"]), L.NET_C, "单",
     "总 sessions %s" % f(tot["sessions"])),
    ("总体转化率", "overall_conversion_rate",
     "%.2f%%" % (tot["overall_conversion_rate"] * 100), L.PROF_C, "",
     "总订单 ÷ 总 sessions"),
]
kpi_boxes = []
for i, (name, key, val, col, unit, sub2) in enumerate(kpi_defs):
    kx, ky = k["x"] + i * (L.KPI_W + L.KPI_GAP), k["y"]
    E.bb("kpi[%d].card" % i, kx, ky, L.KPI_W, k["h"], color=L.CARD, radius=16,
         border="1 SOLID %s" % L.LINE)
    E.bb("kpi[%d].accent" % i, kx, ky, 6, k["h"], color=col, radius=3)
    E.tb("kpi[%d].label" % i, name, kx + 24, ky + 22, w=L.KPI_W - 44, h=30,
         size=L.KPI_LABEL_SIZE, color=L.MUTED, font=D.UI)
    vtext = val + ((" " + unit) if unit else "")
    E.tb("kpi[%d].value" % i, vtext, kx + 24, ky + 58, w=L.KPI_W - 44, h=54,
         size=L.KPI_VALUE_SIZE, color=L.INK, font=D.UI, style="BOLD")
    E.tb("kpi[%d].sub" % i, sub2, kx + 24, ky + 114, w=L.KPI_W - 44, h=30,
         size=L.KPI_LABEL_SIZE, color=col, font=D.UI)
    kpi_boxes.append({"index": i, "name": name, "key": key, "value_text": vtext,
                      "sub_text": sub2, "accent": col,
                      "rect": {"x": kx, "y": ky, "w": L.KPI_W, "h": k["h"]}})

# ============================================================ chart panel
c = R["chart"]
E.bb("chart.panel", c["x"], c["y"], c["w"], c["h"], color=L.CARD, radius=16,
     border="1 SOLID %s" % L.LINE)
E.tb("chart.title", "净收入与经营利润（共用零基线性轴，单位：元）", c["x"] + 24,
     c["y"] + 14, w=700, h=34, size=L.SECT_SIZE, color=L.INK, font=D.UI, style="BOLD")
sx = c["x"] + L.CH_SIDE_X_OFF
lg_x = sx - 24
for lab, col in (("经营利润", L.PROF_C), ("净收入", L.NET_C))[::-1]:
    lg_x -= L.str_w(lab, L.BODY_SIZE) + 8
    E.tb("chart.legend.%s" % lab, lab, lg_x, c["y"] + 18, w=L.str_w(lab, L.BODY_SIZE) + 8,
         h=28, size=L.BODY_SIZE, color=L.MUTED, font=D.UI)
    lg_x -= 22 + 10
    E.bb("chart.legend.swatch.%s" % lab, lg_x, c["y"] + 24, 22, 16, color=col, radius=3)
    lg_x -= 26

PLOT_X0 = c["x"] + L.CH_PLOT_X0_OFF
PLOT_X1 = c["x"] + L.CH_PLOT_X1_OFF
PLOT_Y0 = c["y"] + L.CH_PLOT_Y0_OFF
PLOT_Y1 = c["y"] + L.CH_PLOT_Y1_OFF
plot_w, plot_h = PLOT_X1 - PLOT_X0, PLOT_Y1 - PLOT_Y0
lo, hi = axis["domain"]
span = float(hi - lo)


def ypx(v):
    return PLOT_Y1 - (v - lo) / span * plot_h


zero_y = ypx(0.0)
neg_bottom = ypx(min(m["operating_profit"] for m in ms))
axis_bottom = ypx(lo)
if lo < 0:
    # shade the entire negative band (0 down to the axis minimum), so the small
    # -5,632 bar is visibly tiny *because* it sits in a real -20,000..0 region
    E.bb("chart.neghint", PLOT_X0, zero_y, plot_w, axis_bottom - zero_y,
         color="#FEF2F2FF")
    E.ln("chart.negband.rule", PLOT_X0, axis_bottom, plot_w, "#FCA5A5FF")
for v, lab in zip(axis["ticks"], axis["tick_labels"]):
    ty = ypx(v)
    is_zero = (v == 0)
    E.bb("chart.grid.%s" % lab, PLOT_X0, ty - (1 if is_zero else 0.5), plot_w,
         2 if is_zero else 1, color="#64748BFF" if is_zero else "#E2E8F0FF")
    E.tb("chart.tick.%s" % lab, lab, PLOT_X0 - 96, ty - 13, w=86, h=26,
         size=L.BODY_SIZE, color=L.LOSS_C if is_zero and lo < 0 else L.MUTED,
         font=D.UI, align="RIGHT", style="BOLD" if is_zero else None)
if lo < 0:
    # inside the shaded negative band, left-aligned to the plot, clear of every
    # bar, value label and tick
    E.tb("chart.zeroaxis.note", "← 零基线", PLOT_X0 + 6, axis_bottom + 4, w=120, h=26,
         size=L.BODY_SIZE, color=L.LOSS_C, font=D.UI, style="BOLD")

gw = plot_w / len(ms)
BAR_W = L.BAR_W
PAIR_W = BAR_W * 2 + L.BAR_GAP
month_label_y = max(PLOT_Y1, neg_bottom) + L.CH_MONTH_LABEL_GAP
bar_rects = []
for i, m in enumerate(ms):
    cx = PLOT_X0 + gw * i + gw / 2.0
    if i:
        E.bb("chart.gridline.%d" % i, PLOT_X0 + gw * i, PLOT_Y0, 1, plot_h,
             color="#F1F5F9FF")
    for j, key in enumerate(("net_revenue", "operating_profit")):
        v = m[key]
        col = L.NET_C if key == "net_revenue" else (L.LOSS_C if v < 0 else L.PROF_C)
        bx = cx - PAIR_W / 2.0 + j * (BAR_W + L.BAR_GAP)
        by_top, by_bot = ypx(max(v, 0.0)), ypx(min(v, 0.0))
        if abs(by_bot - by_top) < 3:
            by_bot = by_top + 3 if v >= 0 else by_top - 3
        E.bb("chart.bar.%s.%s" % (m["month"], key), bx, by_top, BAR_W,
             by_bot - by_top, color=col, radius=4)
        bar_rects.append({"month": m["month"], "series": key, "value": v,
                          "rect": {"x": round(bx, 2), "y": round(by_top, 2),
                                   "w": BAR_W, "h": round(by_bot - by_top, 2)}})
        lab = f(v) if v >= 0 else "-%s（亏损）" % f(abs(v))
        lw_ = L.str_w(lab, L.BARS_LABEL_SIZE)
        ly = by_top - 30 if v >= 0 else by_bot + 8
        E.tb("chart.vlabel.%s.%s" % (m["month"], key), lab,
             bx + (BAR_W - lw_) / 2.0, ly, w=max(lw_ + 10, 40), h=28,
             size=L.BARS_LABEL_SIZE, color=col, font=D.UI, align="CENTER",
             style="BOLD")
    has_neg = m["operating_profit"] < 0
    my = month_label_y
    E.tb("chart.month.%s" % m["month"], m["month"], cx - gw / 2.0, my, w=gw, h=30,
         size=L.BODY_SIZE, color=L.INK, font=D.UI, align="CENTER")

# side summary
E.bb("chart.side.divider", sx - 18, c["y"] + 56, 1, c["h"] - 80, color=L.LINE)
E.tb("chart.side.hdr", "净收入 / 经营利润（元）", sx, c["y"] + 14, w=L.CH_SIDE_W - 8,
     h=28, size=L.BODY_SIZE, color=L.MUTED, font=D.UI, style="BOLD")
items = [(m["month"], f(m["net_revenue"]), f(m["operating_profit"]),
          m["operating_profit"] < 0) for m in ms][::-1]
iy = c["y"] + 58
for i, (mo, nv, pv, neg) in enumerate(items):
    E.tb("chart.side.month.%d" % i, mo, sx, iy, w=94, h=28, size=L.BODY_SIZE,
         color=L.INK, font=D.UI)
    E.tb("chart.side.net.%d" % i, nv, sx + 92, iy, w=96, h=28, size=L.BODY_SIZE,
         color=L.NET_C, font=D.UI, align="RIGHT")
    E.tb("chart.side.prof.%d" % i, pv, sx + 186, iy, w=L.CH_SIDE_W - 194, h=28,
         size=L.BODY_SIZE, color=L.LOSS_C if neg else L.PROF_C, font=D.UI,
         align="RIGHT")
    iy += 30
    if i < len(items) - 1:
        E.ln("chart.side.rule.%d" % i, sx, iy - 5, L.CH_SIDE_W - 8, L.LINE)

# ============================================================ table panel
t = R["table"]
E.bb("table.panel", t["x"], t["y"], t["w"], t["h"], color=L.CARD, radius=16,
     border="1 SOLID %s" % L.LINE)
t_title = "月度明细（%d 个月）" % len(ms)
E.tb("table.title", t_title, t["x"] + 24, t["y"] + L.TABLE_TITLE_TOP,
     w=L.str_w(t_title, L.SECT_SIZE) + 20, h=34, size=L.SECT_SIZE, color=L.INK,
     font=D.UI, style="BOLD")
t_formula = "退款率=退款÷收入；转化率=订单÷sessions"
t_fw = L.str_w(t_formula, L.BODY_SIZE) + 16
E.tb("table.formula", t_formula, t["x"] + t["w"] - 24 - t_fw,
     t["y"] + L.TABLE_TITLE_TOP + 4, w=t_fw, h=30, size=L.BODY_SIZE, color=L.MUTED,
     font=D.UI, align="RIGHT")
E.ln("table.hdr.rule", t["x"] + 24, t["y"] + L.TABLE_HDR_RULE, t["w"] - 48, L.LINE)
for key, al, off, bw_, zh in L.TABLE_COLS:
    col = {"month": L.INK, "net_revenue": L.NET_C, "operating_profit": L.PROF_C,
           "refund_rate": "#B45309FF", "conversion_rate": "#7C3AEDFF"}[key]
    tx = t["x"] + off if al == "LEFT" else t["x"] + off - bw_
    E.tb("table.hdr.%s" % key, zh, tx, t["y"] + L.TABLE_HDR_TOP, w=bw_, h=28,
         size=L.TBL_HDR_SIZE, color=col, font=D.UI, style="BOLD",
         align=None if al == "LEFT" else "RIGHT")
rows_top = t["y"] + L.TABLE_ROWS_TOP
rows_h = t["h"] - L.TABLE_ROWS_TOP - L.TABLE_BOTTOM_PAD
pitch = rows_h / len(ms)
cell_dy = max(0.0, (pitch - L.TABLE_CELL_H) / 2.0)
for i, m in enumerate(ms):
    ry = rows_top + i * pitch
    if i % 2 == 0:
        E.bb("table.zebra.%d" % i, t["x"] + 16, ry, t["w"] - 32, pitch, color="#F8FAFCFF")
    E.tb("table.cell.%s.month" % m["month"], m["month"], t["x"] + 24, ry + cell_dy,
         w=130, h=L.TABLE_CELL_H, size=L.BODY_SIZE, color=L.INK, font=D.UI)
    vals = [("net_revenue", f(m["net_revenue"]), L.NET_C),
            ("operating_profit", f(m["operating_profit"]),
             L.LOSS_C if m["operating_profit"] < 0 else L.PROF_C),
            ("refund_rate", "%.2f%%" % (m["refund_rate"] * 100), "#B45309FF"),
            ("conversion_rate", "%.2f%%" % (m["conversion_rate"] * 100), "#7C3AEDFF")]
    for key, v, col in vals:
        anchor = next(cc for cc in L.TABLE_COLS if cc[0] == key)
        E.tb("table.cell.%s.%s" % (m["month"], key), v, t["x"] + anchor[2] - anchor[3],
             ry + cell_dy, w=anchor[3], h=L.TABLE_CELL_H, size=L.BODY_SIZE,
             color=col, font=D.UI, align="RIGHT")
    if m["operating_profit"] < 0:
        # chip sits right after the month label, clear of every numeric column
        E.bb("table.lossmark.%s" % m["month"], t["x"] + 118, ry + cell_dy + 2, 78, 22,
             color="#FEE2E2FF", radius=11)
        E.tb("table.lossmark.text.%s" % m["month"], "亏损", t["x"] + 118,
             ry + cell_dy + 6, w=78, h=22, size=L.BODY_SIZE, color=L.LOSS_C,
             font=D.UI, align="CENTER", style="BOLD")
    E.ln("table.rule.%d" % i, t["x"] + 24, ry + pitch - 1, t["w"] - 48,
         L.LINE if i < len(ms) - 1 else "#CBD5E1FF")

# ============================================================ conclusion panel
cc = R["conclusion"]
E.bb("conclusion.panel", cc["x"], cc["y"], cc["w"], cc["h"], color=L.CARD, radius=16,
     border="1 SOLID %s" % L.LINE)
E.tb("conclusion.title", "主结论（只依据上表实际数值）", cc["x"] + 24,
     cc["y"] + L.CONC_TITLE_TOP, w=cc["w"] - 48, h=32, size=L.SECT_SIZE,
     color=L.INK, font=D.UI, style="BOLD")
inner_w = cc["w"] - 48
head_lines = conc["headline_lines"]
for i, ln_ in enumerate(head_lines):
    E.tb("conclusion.head.%d" % i, ln_, cc["x"] + 24,
         cc["y"] + L.CONC_HEAD_TOP + i * L.CONC_HEAD_STEP, w=inner_w,
         h=L.SECT_SIZE + 8, size=L.SECT_SIZE, color=L.INK, font=D.UI, style="BOLD")
E.ln("conclusion.head.rule", cc["x"] + 24,
     cc["y"] + L.CONC_HEAD_TOP + len(head_lines) * L.CONC_HEAD_STEP + 4,
     cc["w"] - 48, L.LINE)
by = cc["y"] + L.CONC_HEAD_TOP + len(head_lines) * L.CONC_HEAD_STEP + 22
body_top = by - cc["y"]
li = 0
for b, txt in enumerate(conc["bullets"]):
    if b:
        li += L.CONC_BULLET_GAP_LINES
    lines = L.wrap_cjk(txt, L.BODY_SIZE, inner_w - 22)
    for j, ln_ in enumerate(lines):
        if j == 0:
            E.bb("conclusion.bullet.dot.%d" % b, cc["x"] + 24,
                 by + li * L.CONC_BODY_STEP + 9, 8, 8, color=L.NET_C, radius=4)
        E.tb("conclusion.bullet.%d.%d" % (b, j), ln_, cc["x"] + 42,
             by + li * L.CONC_BODY_STEP, w=inner_w - 22, h=L.BODY_SIZE + 8,
             size=L.BODY_SIZE, color=L.MUTED, font=D.UI)
        li += 1
li_total = li
conc_body_bottom = by + (li - 1) * L.CONC_BODY_STEP + L.BODY_SIZE + 8
E.ln("conclusion.rule", cc["x"] + 24, cc["y"] + L.CONC_RULE_Y_OFF, cc["w"] - 48, L.LINE)
E.tb("conclusion.foot", "口径：净收入=收入−退款；利润=净收入−经营成本",
     cc["x"] + 24, cc["y"] + L.CONC_FOOT_Y_OFF, w=inner_w, h=28,
     size=L.BODY_SIZE, color="#94A3B8FF", font=D.UI)

# ============================================================ footnote
fn = R["footnote"]
axis_txt = "柱图纵轴 %s~%s 元（刻度 %s），零基线%s" % (
    f(lo), f(hi), "/".join(axis["tick_labels"]),
    "在图内负值区" if lo < 0 else "位于轴底")
E.tb("footnote.text", "%s ｜ 本轮累计更正 %d 项 ｜ 回归证据见 layout-map.json"
     % (axis_txt, len(corrections)),
     fn["x"], fn["y"], w=fn["w"], h=fn["h"], size=L.BODY_SIZE, color="#94A3B8FF",
     font=D.UI)

# ============================================================ assemble
if not E.kids:
    raise SystemExit("no elements emitted")
assert len(E.kids) == len(E.reg), (len(E.kids), len(E.reg))
dsl_text = D.snapshot([D.stack(E.kids, L.W, L.H)], L.W, L.H, bg=L.BG)

os.makedirs(os.path.join(TMP, "drafts"), exist_ok=True)
draft = os.path.join(TMP, "drafts", "r%02d-final.snapshot" % ROUND)
with open(draft, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(dsl_text)

res = snapkit.render(dsl_text, "dashboard.png", "dashboard.snapshot",
                     final=True, out_dir=OUT)
print("RENDER ok=%s status=%s bytes=%s attempts=%s" % (
    res.get("ok"), res.get("status"), res.get("bytes"), res.get("attempts")))
if not res.get("ok"):
    print("RENDER_ERROR", res.get("error"))

warn = D.warnings()
if warn:
    for w_ in warn:
        print("WARN", w_)
else:
    print("WARN none")

if res.get("ok"):
    conc_cap = int((L.CONC_RULE_Y_OFF - body_top - L.BODY_SIZE - 8) / L.CONC_BODY_STEP)
    rule_y = cc["y"] + L.CONC_RULE_Y_OFF
    if conc_body_bottom > rule_y - 6:
        print("WARN conclusion overflow: body bottom %.1f > rule %.1f (over by %.1fpx)"
              % (conc_body_bottom, rule_y, conc_body_bottom - (rule_y - 6)))

layout = {
    "schema_version": 1,
    "round": ROUND,
    "round_requirements_file": L.ROUND_META[ROUND]["req"],
    "canvas": {"width": L.W, "height": L.H, "background": L.BG},
    "period": period,
    "months_shown": [m["month"] for m in ms],
    "regions": R,
    "region_rects_note": "主区域边界，三轮之间保持一致（要求 ±2px）",
    "kpi": kpi_boxes,
    "chart": {
        "panel_rect": c,
        "plot_rect": {"x": PLOT_X0, "y": PLOT_Y0, "w": plot_w, "h": plot_h},
        "zero_baseline_y_px": round(zero_y, 2),
        "negative_extent_bottom_px": round(neg_bottom, 2),
        "axis_bottom_y_px": round(axis_bottom, 2),
        "negative_band_shaded": bool(lo < 0),
        "axis": axis, "bar_width_px": BAR_W, "group_width_px": round(gw, 2),
        "bars": bar_rects,
    },
    "table": {
        "panel_rect": t,
        "columns": [{"key": k2, "align": a2, "x_anchor": o2, "box_w": bw2,
                     "header_label": z2} for k2, a2, o2, bw2, z2 in L.TABLE_COLS],
        "header_top": t["y"] + L.TABLE_HDR_TOP, "rows_top": rows_top,
        "row_pitch_px": round(pitch, 2), "row_count": len(ms),
        "rows": [{"month": m["month"], "net_revenue": m["net_revenue"],
                  "operating_profit": m["operating_profit"],
                  "refund_rate": round(m["refund_rate"], 6),
                  "conversion_rate": round(m["conversion_rate"], 6),
                  "row_top_px": round(rows_top + i * pitch, 2)}
                 for i, m in enumerate(ms)],
    },
    "conclusion": {
        "panel_rect": cc, "headline": conc["headline"],
        "headline_lines": head_lines, "bullets": conc["bullets"],
        "bullet_line_count": li_total,
        "bullet_body_top_px": body_top,
        "bullet_body_bottom_px": round(conc_body_bottom, 2),
        "bullet_line_capacity": int((L.CONC_RULE_Y_OFF - 6 - body_top - L.BODY_SIZE - 8)
                                    / L.CONC_BODY_STEP),
        "claims": conc["claims"],
    },
    "styles": {
        "fonts": {"body": D.UI,
                  "availability_source": "GET https://open-snapshot.muedsa.com/fonts"},
        "body_font_size_floor": L.BODY_SIZE,
        "colors": {"bg": L.BG, "ink": L.INK, "muted": L.MUTED, "line": L.LINE,
                   "net": L.NET_C, "profit": L.PROF_C, "loss": L.LOSS_C,
                   "card": L.CARD},
        "card_style": {"radius": 16, "border": "1 SOLID #E2E8F0FF"},
    },
    "element_registry": E.reg,
    "element_count": len(E.reg),
}
with open(os.path.join(OUT, "layout-map.json"), "w", encoding="utf-8") as fh:
    json.dump(layout, fh, ensure_ascii=False, indent=2)

computed = {
    "schema_version": 1,
    "round": ROUND,
    "round_requirements_file": L.ROUND_META[ROUND]["req"],
    "input_file": "tasks/A22-staged-data-correction/inputs/monthly.csv",
    "formulas": {
        "net_revenue": "gross_revenue - refund_amount",
        "operating_profit": "net_revenue - operating_cost",
        "refund_rate": "refund_amount / gross_revenue",
        "conversion_rate": "orders / sessions",
        "overall_conversion_rate": "sum(orders) / sum(sessions)",
    },
    "raw_rows": rows,
    "corrections_applied_through_this_round": corrections,
    "months_added_this_round": added_rows,
    "months": ms,
    "totals": {k2: (round(v, 8) if isinstance(v, float) else v) for k2, v in tot.items()},
    "axis": axis,
    "conclusion": conc,
    "geometry": {"canvas": [L.W, L.H],
                 "plot_rect": [PLOT_X0, PLOT_Y0, plot_w, plot_h],
                 "zero_baseline_y_px": round(zero_y, 2),
                 "bar_width_px": BAR_W, "table_row_pitch_px": round(pitch, 2),
                 "element_count": len(E.reg)},
}
with open(os.path.join(OUT, "computed-data.json"), "w", encoding="utf-8") as fh:
    json.dump(computed, fh, ensure_ascii=False, indent=2)

print("months=%d net=%s profit=%s conv=%.4f%% axis=%s zero_y=%.1f pitch=%.2f els=%d lines=%d" % (
    len(ms), f(tot["net_revenue"]), f(tot["operating_profit"]),
    tot["overall_conversion_rate"] * 100, axis["domain"], zero_y, pitch,
    len(E.reg), li_total))