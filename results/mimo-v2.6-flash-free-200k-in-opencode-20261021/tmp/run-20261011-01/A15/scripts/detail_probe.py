# -*- coding: utf-8 -*-
"""A15 detail probe: text/dot bounding boxes + remaining colors from reference.

Feeds gen_a15.py layout constants (these are *observations*, the 12 required
audit anchors come from reference-measured.json). Output: detail-measured.json
"""
import json
import pathlib
from PIL import Image

ROOT = pathlib.Path(".")
REF = ROOT / "tasks" / "A15-reference-reconstruction" / "inputs" / "reference.png"
OUT = ROOT / "tmp" / "run-20261011-01" / "A15"

img = Image.open(REF).convert("RGB")
W, H = img.size
px = img.load()


def lum(p):
    return (p[0] * 299 + p[1] * 587 + p[2] * 114) // 1000


def bbox(x1, y1, x2, y2, pred):
    xs, ys = [], []
    for y in range(y1, y2 + 1):
        for x in range(x1, x2 + 1):
            if pred(px[x, y]):
                xs.append(x)
                ys.append(y)
    return [min(xs), min(ys), max(xs), max(ys)] if xs else None


dark = lambda p: lum(p) < 170
gray = lambda p: lum(p) < 195
bright = lambda p: lum(p) > 150

R = {}

# --- sidebar texts
R["northstar_glyph"] = bbox(62, 25, 215, 72, bright)
R["nav_sel_text_glyph"] = bbox(58, 118, 200, 162, bright)
R["ws_line1_glyph"] = bbox(30, 762, 196, 792, lambda p: lum(p) > 135)
R["ws_line2_glyph"] = bbox(30, 794, 196, 826, bright)
R["ws_line3_glyph"] = bbox(30, 828, 196, 860, lambda p: lum(p) > 135)
R["logo_probe"] = {
    "green_tl": list(px[33, 36]),
    "center": list(px[44, 46]),
    "inner_edge": list(px[42, 44]),
}
R["nav_unsel_dot"] = {"xy": [41, 198], "rgb": list(px[41, 198])}
R["nav_unsel_text"] = {"rgb": list(bbox and min(
    (px[x, y] for y in range(191, 209) for x in range(64, 134)),
    key=lum))}

# --- header
R["button_text_glyph"] = bbox(1200, 50, 1396, 84, bright)

# --- KPI1/2/3 internals (per-card windows from card boxes)
kpis = {"kpi1": (260, 615), "kpi2": (644, 999), "kpi3": (1028, 1383)}
for name, (l, r) in kpis.items():
    R[f"{name}_label_glyph"] = bbox(l + 18, 150, r - 10, 182, gray)
    R[f"{name}_value_glyph"] = bbox(l + 18, 184, r - 10, 234, dark)
    R[f"{name}_change_glyph"] = bbox(l + 18, 236, r - 10, 270, gray)

# --- chart internals
R["chart_title_glyph"] = bbox(275, 328, 560, 368, dark)
R["chart_period_glyph"] = bbox(840, 328, 998, 368, gray)
R["unit_glyph"] = bbox(275, 372, 460, 400, gray)
ylabs = {}
for v, gy in ((120, 405), (90, 441), (60, 477), (30, 513), (0, 549)):
    ylabs[str(v)] = bbox(270, gy - 14, 313, gy + 14, gray)
R["y_label_glyphs"] = ylabs
months = {}
for i, m in enumerate(("Apr", "May", "Jun", "Jul", "Aug", "Sep")):
    cx = (357 + 410) // 2 + i * 101
    months[m] = bbox(cx - 55, 572, cx + 55, 600, gray)
R["month_label_glyphs"] = months

# --- activity internals
R["activity_title_glyph"] = bbox(1045, 330, 1320, 372, dark)
R["act_item1_title_glyph"] = bbox(1070, 388, 1360, 420, dark)
R["act_item1_time_glyph"] = bbox(1070, 418, 1360, 448, gray)
R["act_item2_title_glyph"] = bbox(1070, 448, 1360, 482, dark)
R["act_item2_time_glyph"] = bbox(1070, 480, 1360, 510, gray)
R["act_item3_title_glyph"] = bbox(1070, 508, 1360, 542, dark)
R["act_item3_time_glyph"] = bbox(1070, 538, 1360, 568, gray)
R["act_dot1"] = bbox(1044, 388, 1070, 418,
                    lambda p: p[0] > 200 and p[1] > 130 and p[2] < 130)
R["act_dot2"] = bbox(1044, 448, 1070, 478,
                    lambda p: p[2] - p[0] > 60 and p[2] > 180)
R["act_dot3"] = bbox(1044, 508, 1070, 538,
                    lambda p: p[1] - p[0] > 40 and p[1] > 120 and p[0] < 150)
R["act_dot_colors"] = {
    "amber": list(px[(R["act_dot1"][0] + R["act_dot1"][2]) // 2,
                     (R["act_dot1"][1] + R["act_dot1"][3]) // 2]),
    "blue": list(px[(R["act_dot2"][0] + R["act_dot2"][2]) // 2,
                    (R["act_dot2"][1] + R["act_dot2"][3]) // 2]),
    "green": list(px[(R["act_dot3"][0] + R["act_dot3"][2]) // 2,
                     (R["act_dot3"][1] + R["act_dot3"][3]) // 2]),
}

# --- table internals
R["table_title_glyph"] = bbox(275, 632, 640, 680, dark)
R["th_project_glyph"] = bbox(280, 692, 460, 718, gray)
R["th_owner_glyph"] = bbox(660, 692, 800, 718, gray)
R["th_status_glyph"] = bbox(1020, 692, 1140, 718, gray)
R["th_due_glyph"] = bbox(1240, 692, 1340, 718, gray)
R["row1_project_glyph"] = bbox(280, 724, 640, 758, dark)
R["row1_owner_glyph"] = bbox(660, 724, 860, 758, gray)
R["row1_due_glyph"] = bbox(1240, 724, 1360, 758, gray)
R["row2_project_glyph"] = bbox(280, 760, 640, 793, dark)
R["row3_project_glyph"] = bbox(280, 795, 640, 830, dark)

# --- header band + separators: raw structure probe
R["band_probe_rows"] = {}
for y in (686, 690, 700, 710, 720, 723):
    row = [px[x, y] for x in (265, 275, 285, 300, 340, 360, 500, 900, 1380, 1396)]
    R["band_probe_rows"][str(y)] = row
R["band_probe_cols"] = {}
for x in (300, 900):
    col = {str(y): list(px[x, y]) for y in range(684, 726, 3)}
    R["band_probe_cols"][str(x)] = col
sep = {}
for y in (755, 757, 758, 759, 760, 791, 793, 825, 827, 829):
    p = px[500, y]
    xs = None
    if abs(p[0] - 255) + abs(p[1] - 255) + abs(p[2] - 255) > 6:
        left = right = None
        for x in range(262, 1398):
            q = px[x, y]
            if abs(q[0] - 255) + abs(q[1] - 255) + abs(q[2] - 255) > 6:
                if left is None:
                    left = x
                right = x
        xs = [left, right]
    sep[str(y)] = {"rgb": list(p), "x_extent": xs}
R["separators"] = sep

# --- remaining colors
def stroke(x1, y1, x2, y2, key=lum, lo=True):
    vals = [(px[x, y], key(px[x, y])) for y in range(y1, y2 + 1)
            for x in range(x1, x2 + 1)]
    return list(min(vals, key=lambda t: t[1])[0] if lo
                else max(vals, key=lambda t: t[1])[0])


R["colors"] = {
    "gridline": list(px[500, 405]),
    "zero_line": list(px[500, 549]),
    "kpi_card_top_border": list(px[400, 138]),
    "kpi_card_left_border": list(px[260, 200]),
    "kpi_value_stroke": stroke(283, 190, 480, 230),
    "chart_title_stroke": stroke(285, 336, 460, 362),
    "month_stroke": stroke(360, 574, 410, 596),
    "y_label_stroke": stroke(285, 432, 312, 552),
    "activity_title_stroke": stroke(1056, 340, 1260, 364),
    "act_item_title_stroke": stroke(1078, 396, 1240, 416),
    "act_time_stroke": stroke(1078, 420, 1140, 440),
    "table_title_stroke": stroke(284, 642, 460, 668),
    "th_stroke": stroke(289, 697, 350, 714),
    "row_project_stroke": stroke(287, 730, 470, 752),
    "row_owner_stroke": stroke(674, 730, 760, 752),
    "row_due_stroke": stroke(1259, 730, 1330, 752),
    "footer_stroke": stroke(261, 866, 515, 880),
    "northstar_stroke": stroke(73, 38, 200, 56, lo=True) if False else None,
    "nav_unsel_text_stroke": stroke(64, 191, 133, 208),
    "ws_green_stroke": stroke(38, 768, 170, 784),
    "ws_members_stroke": stroke(38, 802, 175, 822),
    "ws_manage_stroke": stroke(38, 836, 150, 852),
    "subtitle_stroke2": stroke(261, 86, 506, 102),
}
R["colors"]["northstar_stroke"] = stroke(73, 38, 200, 56)
R["colors"]["northstar_stroke"] = min(
    (px[x, y] for y in range(38, 57) for x in range(73, 201)), key=lum) if False else None
# NORTHSTAR is white on dark: take brightest
R["colors"]["northstar_stroke"] = max(
    ((px[x, y], lum(px[x, y])) for y in range(38, 57) for x in range(73, 201)),
    key=lambda t: t[1])[0]
R["colors"]["northstar_stroke"] = list(R["colors"]["northstar_stroke"])
R["colors"]["kpi_label_stroke"] = list(min(
    ((px[x, y], lum(px[x, y])) for y in range(158, 176) for x in range(283, 400)),
    key=lambda t: t[1])[0])
R["colors"]["export_text_white"] = list(max(
    ((px[x, y], lum(px[x, y])) for y in range(56, 78) for x in range(1230, 1360)),
    key=lambda t: t[1])[0])

(OUT / "detail-measured.json").write_text(
    json.dumps(R, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(R, ensure_ascii=False, indent=1))
