# -*- coding: utf-8 -*-
"""A15 reference measurement v2 - fixed detectors.

Fixes vs v1:
  * card outer contours via not-background runs (bg=#F3F6FB measured), chosen
    at text-free rows; columns combine runs broken by same-colored header row
  * KPI cards measured on row y=150 (above labels)
  * status pill predicates tightened (separator lines #E2E8F0 excluded by
    blue/amber/green saturation)
  * samples moved to solid interiors / text-stroke centers
  * workspace card bbox = non-sidebar region
Output: tmp/run-20261011-01/A15/reference-measured.json (overwrites v1)
"""
import json
import pathlib
from PIL import Image

ROOT = pathlib.Path(".")
REF = ROOT / "tasks" / "A15-reference-reconstruction" / "inputs" / "reference.png"
OUT = ROOT / "tmp" / "run-20261011-01" / "A15"
OUT.mkdir(parents=True, exist_ok=True)

img = Image.open(REF).convert("RGB")
W, H = img.size
px = img.load()

BG = (243, 246, 251)          # main background (measured)
SIDEBAR = (20, 35, 60)        # sidebar background (measured)
WHITE = (255, 255, 255)


def lum(p):
    return (p[0] * 299 + p[1] * 587 + p[2] * 114) // 1000


def not_bg(p, tol=4):
    return abs(p[0] - BG[0]) + abs(p[1] - BG[1]) + abs(p[2] - BG[2]) > tol


def not_sidebar(p, tol=14):
    return abs(p[0] - SIDEBAR[0]) + abs(p[1] - SIDEBAR[1]) + abs(p[2] - SIDEBAR[2]) > tol


def runs_row(y, pred, x1, x2):
    out, s = [], None
    for x in range(x1, x2 + 1):
        if pred(px[x, y]):
            if s is None:
                s = x
        elif s is not None:
            out.append((s, x - 1))
            s = None
    if s is not None:
        out.append((s, x2))
    return out


def runs_col(x, pred, y1, y2):
    out, s = [], None
    for y in range(y1, y2 + 1):
        if pred(px[x, y]):
            if s is None:
                s = y
        elif s is not None:
            out.append((s, y - 1))
            s = None
    if s is not None:
        out.append((s, y2))
    return out


def col_extent(x, pred, y1, y2):
    """outer extent of a column, tolerating interior runs of bg-colored rows
    (e.g. table header row that shares the page background colour)."""
    rs = runs_col(x, pred, y1, y2)
    if not rs:
        return None
    return (rs[0][0], rs[-1][1])


def bbox_of(pred, x1, y1, x2, y2):
    xs, ys = [], []
    for y in range(y1, y2 + 1):
        for x in range(x1, x2 + 1):
            if pred(px[x, y]):
                xs.append(x)
                ys.append(y)
    return [min(xs), min(ys), max(xs), max(ys)] if xs else None


R = {"canvas": [W, H], "background_sampled": px[1420, 115]}

# sidebar right edge
for x in range(0, W):
    if lum(px[x, 450]) > 150:
        R["sidebar_right_x"] = x
        break

# nav selected pill (region != sidebar inside x 4..214, y 100..175)
R["nav_selected_box"] = bbox_of(not_sidebar, 4, 100, 214, 178)
# workspace card (non-sidebar region bottom)
R["workspace_card_box"] = bbox_of(not_sidebar, 4, 725, 214, 890)
# logo icon
R["logo_icon_box"] = bbox_of(
    lambda p: p[1] > 120 and p[1] > p[0] + 40 and p[1] > p[2] + 20, 8, 18, 80, 78)

# title glyph bbox (dark text in header)
R["title_glyph_box"] = bbox_of(lambda p: lum(p) < 110, 250, 18, 950, 82)
# subtitle glyph box
R["subtitle_glyph_box"] = bbox_of(lambda p: lum(p) < 170, 250, 82, 950, 110)

# export button
blue_btn = lambda p: p[2] >= 180 and p[2] - p[0] > 60 and p[1] < 160
R["export_button_box"] = bbox_of(blue_btn, 1100, 20, 1439, 115)

# KPI cards on text-free row y=150
kpis = [r for r in runs_row(150, not_bg, 230, 1439) if r[1] - r[0] > 150]
R["kpi_boxes_row150"] = kpis
for i, (a, b) in enumerate(kpis):
    ext = col_extent((a + b) // 2, not_bg, 120, 300)
    R[f"kpi{i+1}_box"] = [a, ext[0], b, ext[1]] if ext else None

# middle row: chart + activity on row y=320 (below card top, above title text)
mid = [r for r in runs_row(320, not_bg, 230, 1439) if r[1] - r[0] > 150]
R["mid_row_runs_y320"] = mid
if mid:
    a, b = mid[0]
    rs = runs_col(a + 9, not_bg, 295, 625)
    R["chart_card_box"] = [a, rs[0][0], b, rs[0][1]] if rs else None
if len(mid) > 1:
    a, b = mid[1]
    rs = runs_col(a + 9, not_bg, 295, 625)
    R["activity_card_box"] = [a, rs[0][0], b, rs[0][1]] if rs else None

# table card: row y=680 for sides, column x=1350 for top/bottom
tab = [r for r in runs_row(680, not_bg, 230, 1439) if r[1] - r[0] > 300]
if tab:
    a, b = tab[0]
    ext = col_extent(1350, not_bg, 610, 880)
    R["table_card_box"] = [a, ext[0], b, ext[1]] if ext else None

# table header row extent (bg-colored band inside card)
if R.get("table_card_box"):
    t = R["table_card_box"]
    hdr = [r for r in runs_row(703, lambda p: not not_bg(p), t[0], t[2])
           if r[1] - r[0] > 200]
    if hdr:
        # header row vertical extent via column inside header band
        vext = col_extent((hdr[0][0] + hdr[0][1]) // 2,
                          lambda p: not not_bg(p), t[1], t[3])
        R["table_header_band_box"] = [hdr[0][0], vext[0], hdr[0][1], vext[1]]

# gridlines inside chart card
cc = R.get("chart_card_box")
grid_rows = []
if cc:
    x1, x2 = cc[0] + 60, cc[2] - 30
    for y in range(cc[1] + 75, cc[3] - 35):
        cnt = 0
        for x in range(x1, x2):
            p = px[x, y]
            if (not (p[0] > 250 and p[1] > 250 and p[2] > 250)) and \
               not (p[2] > 170 and p[2] - p[0] > 50):
                if 190 <= lum(p) <= 244:
                    cnt += 1
        if cnt > 250:
            grid_rows.append((y, cnt))
R["gridline_rows"] = grid_rows

if grid_rows:
    zy = grid_rows[-1][0]
    R["zero_line_y"] = zy
    xs = []
    for x in range(cc[0] + 10, cc[2] - 10):
        p = px[x, zy]
        if not (p[0] > 250 and p[1] > 250 and p[2] > 250) and \
           not (p[2] > 170 and p[2] - p[0] > 50) and lum(p) <= 244:
            xs.append(x)
    if xs:
        R["zero_line_left_x"] = xs[0]
        R["zero_line_right_x"] = xs[-1]

    # bars on row just above zero line
    ybar = zy - 6
    bars = [r for r in runs_row(
        ybar, lambda p: p[2] > 170 and p[2] - p[0] > 50, cc[0], cc[2])
        if r[1] - r[0] > 15]
    R["bar_cols"] = bars
    if bars:
        a, b = bars[-1]
        cx = (a + b) // 2
        top = None
        for y in range(cc[1] + 70, zy):
            p = px[cx, y]
            if p[2] > 170 and p[2] - p[0] > 50:
                top = y
                break
        R["last_bar_top_center"] = [cx, top]
        R["last_bar_box"] = [a, top, b, zy]

# footer glyphs
R["footer_glyph_box"] = bbox_of(lambda p: lum(p) < 170, 250, 855, 700, 895)

# status pills - bg-fill predicates (separator #E2E8F0 and text excluded)
R["status_progress_pill_box"] = bbox_of(
    lambda p: p[2] > 240 and p[2] - p[0] > 15 and p[0] > 220,
    1000, 722, 1230, 762)
R["status_review_pill_box"] = bbox_of(
    lambda p: p[0] > 250 and p[0] - p[2] > 30 and p[1] > 230,
    1000, 758, 1230, 795)
R["status_done_pill_box"] = bbox_of(
    lambda p: p[1] - p[0] > 15 and p[1] - p[2] > 8 and p[1] > 235,
    1000, 793, 1230, 832)

# color samples (solid interiors; text colors = densest stroke pixel in window)
def stroke_sample(x1, y1, x2, y2, mode):
    best, bv = None, (10**9 if mode == "dark" else -10**9)
    for y in range(y1, y2 + 1):
        for x in range(x1, x2 + 1):
            p = px[x, y]
            v = lum(p)
            if mode == "dark" and v < bv:
                best, bv = p, v
            if mode == "green" and p[1] - p[0] > bv:
                best, bv = p, p[1] - p[0]
            if mode == "bright" and v > bv:
                best, bv = p, v
    return best


R["color_samples"] = {
    "main_bg": {"xy": [1420, 115], "rgb": list(px[1420, 115])},
    "sidebar_bg": {"xy": [110, 470], "rgb": list(px[110, 470])},
    "card_white": {"xy": [430, 147], "rgb": list(px[430, 147])},
    "export_blue": {"xy": [1292, 66], "rgb": list(px[1292, 66])},
    "bar_blue": {"xy": [887, 500], "rgb": list(px[887, 500])},
    "selected_nav_bg": {"xy": [185, 135], "rgb": list(px[185, 135])},
    "nav_unselected_bg": {"xy": [185, 201], "rgb": list(px[185, 201])},
    "workspace_card_bg": {"xy": [110, 762], "rgb": list(px[110, 762])},
    "table_header_bg": {"xy": [400, 703], "rgb": list(px[400, 703])},
    "status_progress_bg": {"xy": [1040, 742], "rgb": list(px[1040, 742])},
    "status_progress_text": {"xy": [1090, 742], "rgb": list(px[1090, 742]),
                             "note": "stroke pixel sample of 'In progress'"},
    "status_review_bg": {"xy": [1040, 777], "rgb": list(px[1040, 777])},
    "status_done_bg": {"xy": [1040, 811], "rgb": list(px[1040, 811])},
    "kpi_label_stroke": {"xy": [285, 166], "rgb": list(px[285, 166])},
    "subtitle_stroke": {"xy": [300, 93], "rgb": list(px[300, 93])},
    "title_stroke": {"rgb": list(stroke_sample(261, 39, 593, 68, "dark"))},
    "progress_text_stroke": {"rgb": list(stroke_sample(
        1067, 736, 1136, 748, "dark"))},
    "review_text_stroke": {"rgb": list(stroke_sample(
        1060, 770, 1150, 785, "dark"))},
    "green_change": {"rgb": list(stroke_sample(270, 243, 350, 262, "green"))},
    "nav_selected_text": {"rgb": list(stroke_sample(60, 126, 150, 141, "bright"))},
}

# nav glyph boxes
R["nav_rows"] = []
for name, y0, y1 in (("Overview", 116, 163), ("Projects", 180, 224),
                     ("Analytics", 244, 288), ("Settings", 308, 352)):
    bb = bbox_of(lambda p: lum(p) > 150, 44, y0, 214, y1)
    R["nav_rows"].append({"item": name, "glyph_box": bb})

(OUT / "reference-measured.json").write_text(
    json.dumps(R, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(R, ensure_ascii=False, indent=1))
