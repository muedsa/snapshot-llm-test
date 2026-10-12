"""A15 step 1 — measure the reference UI from pixels, not from eyeballing.

Emits tmp/<rid>/A15/measure.json: sidebar edge, every white card, the selected nav pill,
chart gridlines/bars, table header + rows + status pills, and the bounding boxes and
colours of the dark text runs. Segmentation is projection-based (numpy only, no scipy):
rows first, then columns inside each row band, so two side-by-side cards never merge into
one rectangle.
"""
import json
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
TEMP = ROOT / "tmp" / RID / "A15"
REF = ROOT / "tasks" / "A15-reference-reconstruction" / "inputs" / "reference.png"
TEMP.mkdir(parents=True, exist_ok=True)
# Same measurement code runs on the reference and on every reconstruction, so the audit
# compares like with like: argv = [image, out_json].
IMG = Path(sys.argv[1]) if len(sys.argv) > 1 else REF
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else (TEMP / "measure.json")
a = np.asarray(Image.open(IMG).convert("RGB")).astype(int)
H, W = a.shape[:2]


def rgb(hexs):
    return np.asarray([int(hexs[i:i + 2], 16) for i in (1, 3, 5)])


def runs(mask, min_len=3, gap=2):
    idx = np.flatnonzero(mask)
    if not len(idx):
        return []
    out, s, p = [], idx[0], idx[0]
    for i in idx[1:]:
        if i - p > gap:
            if p - s + 1 >= min_len:
                out.append((int(s), int(p)))
            s = i
        p = i
    if p - s + 1 >= min_len:
        out.append((int(s), int(p)))
    return out


def colour_at(x, y):
    return "#%02X%02X%02X" % tuple(a[y, x])


def dominant(box, quant=8):
    x0, y0, x1, y1 = [int(v) for v in box]
    sub = a[y0:y1 + 1, x0:x1 + 1].reshape(-1, 3) // quant
    keys, counts = np.unique(sub, axis=0, return_counts=True)
    c = keys[counts.argmax()] * quant + quant // 2
    return "#%02X%02X%02X" % tuple(int(v) for v in c)


def darkest(box, frac=0.05):
    """Text colour = dominant colour among the darkest frac of a box. A single sample inside
    a glyph usually lands on an antialiased edge or on the card behind the stroke."""
    x0, y0, x1, y1 = [int(v) for v in box]
    sub = a[y0:y1 + 1, x0:x1 + 1].reshape(-1, 3)
    lum = sub.sum(axis=1)
    keep = sub[lum <= np.quantile(lum, min(max(frac, 0.01), 1.0))]
    if not len(keep):
        keep = sub
    keys, counts = np.unique(keep // 16, axis=0, return_counts=True)
    c = keys[counts.argmax()] * 16 + 8
    return "#%02X%02X%02X" % tuple(int(v) for v in c)


def text_box(x0, y0, x1, y1, thr=380):
    seg = a[int(y0):int(y1) + 1, int(x0):int(x1) + 1]
    m = seg.sum(axis=2) < thr
    if not m.any():
        return None
    ys, xs = np.flatnonzero(m.any(axis=1)), np.flatnonzero(m.any(axis=0))
    return [int(x0) + int(xs[0]), int(y0) + int(ys[0]),
            int(x0) + int(xs[-1]), int(y0) + int(ys[-1])]


out = {"canvas": [W, H], "colours": {}, "regions": {}, "text": {}}
PAGE_BG = colour_at(1400, 880)
notbg = (np.abs(a - rgb(PAGE_BG)).max(axis=2) > 6)

# ---- flat colours at unambiguous spots -------------------------------------------------
out["colours"] = {"page_bg": PAGE_BG, "sidebar": colour_at(10, 400),
                  "card": colour_at(450, 200),
                  "nav_selected_pill": dominant((60, 120, 120, 150)),
                  "export_button": dominant((1290, 55, 1350, 75)),
                  "gridline": dominant((700, 405, 760, 406)),
                  "workspace_card": dominant((60, 780, 120, 800))}

# ---- sidebar right edge ----------------------------------------------------------------
row = a[H // 2]
edge = [x for x in range(1, 400) if np.abs(row[x] - row[0]).max() > 10]
out["regions"]["sidebar"] = [0, 0, (edge[0] - 1) if edge else 219, H - 1]

# ---- cards: detect against the PAGE background, not against white ----------------------
# Thresholding "white" splits a card wherever a bar or a pill covers most of a column, which
# cut the chart card into three pieces and made the status pills undetectable.
cards = []
for y0, y1 in runs(notbg[:, 240:1410].mean(axis=1) > 0.55, min_len=24):
    band = notbg[y0:y1 + 1, 240:1410]
    for x0, x1 in runs(band.mean(axis=0) > 0.55, min_len=30, gap=6):
        sub = band[:, x0:x1 + 1]
        ry = np.flatnonzero(sub.any(axis=1))
        cards.append([240 + int(x0), int(y0) + int(ry[0]), 240 + int(x1),
                      int(y0) + int(ry[-1])])
out["regions"]["cards"] = cards

# ---- chart internals -------------------------------------------------------------------
out["colours"]["bar"] = dominant((385, 470, 400, 520))
bar_c = rgb(out["colours"]["bar"])
blue = (np.abs(a - bar_c).max(axis=2) <= 46) & (np.arange(3) @ [1, 1, 1] > 0)
bars = []
for x0, x1 in runs(blue[:, 261:1000].any(axis=0), min_len=10):
    col = np.flatnonzero(blue[:, x0 + 261:x1 + 262].any(axis=1))
    rows = [r for r in col if r > 300 and r < 620]
    if rows:
        bars.append([int(x0 + 261), int(min(rows)), int(x1 + 261), int(max(rows))])
out["regions"]["bars"] = bars
gl_c = rgb(out["colours"]["gridline"])
gl = (np.abs(a - gl_c).max(axis=2) <= 6)
out["regions"]["gridlines"] = [380 + int(y0) for y0, y1 in
                               runs(gl[380:560, 925:985].mean(axis=1) > 0.5, min_len=1)]
out["regions"]["axis_x_line"] = [int(x0) for x0, x1 in
                                 runs((a[:, 545:555] < 300).any(axis=1), min_len=1)]

# ---- table rows / header band / pills ---------------------------------------------------
# The table card is split by its own header band, which is only 3-5 levels away from the page
# background, so the two detected pieces are unioned back into one rectangle.
parts = [c for c in cards if c[1] > 600]
tb = [[min(p[0] for p in parts), min(p[1] for p in parts),
       max(p[2] for p in parts), max(p[3] for p in parts)]] if parts else []
out["regions"]["table_card"] = tb[0] if tb else None
if tb:
    tx0, ty0, tx1, ty1 = tb[0]
    seg = a[ty0:ty1 + 1, tx0:tx1 + 1]
    hue = seg.max(axis=2) - seg.min(axis=2)
    pill = (hue > 14) & (seg.min(axis=2) > 165)
    # status pills are ~26 px tall blocks; the 1 px row separators are the same tint family
    # and would otherwise merge into one full-width run.
    out["regions"]["pills"] = []
    for x0, x1 in runs(pill.sum(axis=0) > 12, min_len=30):
        if x0 + tx0 < 1000 or x1 + tx0 > 1200:
            continue
        for y0, y1 in runs(pill[:, x0:x1 + 1].sum(axis=1) > 12, min_len=8, gap=4):
            r = [tx0 + int(x0), ty0 + int(y0), tx0 + int(x1), ty0 + int(y1)]
            out["regions"]["pills"].append({"rect": r, "bg": dominant(r),
                                            "text": darkest(r, 0.04)})
    sep = (seg.sum(axis=2) < 720) & (seg.sum(axis=2) > 600)
    out["regions"]["row_separators"] = [int(ty0 + y) for y in
                                        np.flatnonzero(sep.mean(axis=1) > 0.7)]
    out["colours"]["table_header_band"] = dominant((tx0 + 600, ty0 + 66,
                                                    tx0 + 700, ty0 + 72))

# ---- text anchors -----------------------------------------------------------------------
BANDS = {
    "brand": (30, 25, 210, 70, 520), "title": (255, 25, 900, 80, 380),
    "subtitle": (255, 80, 900, 112, 640), "export_text": (1200, 40, 1400, 95, 640),
    "nav_overview": (55, 112, 210, 160, 640), "nav_projects": (55, 175, 210, 220, 640),
    "nav_analytics": (55, 240, 210, 285, 640), "nav_settings": (55, 305, 210, 350, 640),
    "kpi1_label": (270, 148, 620, 180, 620), "kpi1_value": (270, 185, 620, 240, 380),
    "kpi1_delta": (270, 240, 620, 268, 620),
    "kpi2_value": (650, 185, 1000, 240, 380), "kpi3_value": (1040, 185, 1390, 240, 380),
    "chart_title": (270, 325, 700, 362, 380), "chart_period": (850, 330, 1010, 360, 620),
    "chart_unit": (270, 368, 400, 390, 640),
    "tick120": (270, 393, 330, 415, 640), "tick0": (270, 530, 330, 555, 640),
    "month_apr": (350, 550, 430, 575, 640), "month_sep": (850, 550, 940, 575, 640),
    "activity_title": (1040, 328, 1390, 362, 380),
    "activity_1": (1060, 388, 1390, 415, 380), "activity_1_time": (1060, 418, 1390, 442, 640),
    "table_title": (270, 632, 700, 672, 380),
    "th_project": (285, 688, 500, 712, 620), "th_due": (1200, 688, 1390, 712, 620),
    "row1_project": (285, 725, 780, 752, 380), "row1_owner": (760, 725, 1000, 752, 620),
    "row2_project": (285, 760, 780, 788, 380), "row3_project": (285, 795, 780, 822, 380),
    "row3_due": (1200, 795, 1390, 825, 620),
    "ws_label": (30, 758, 200, 782, 620), "ws_members": (30, 790, 200, 818, 640),
    "ws_manage": (30, 822, 200, 852, 640), "footer": (255, 855, 700, 885, 620),
}
for k, (x0, y0, x1, y1, thr) in BANDS.items():
    b = text_box(x0, y0, x1, y1, thr)
    out["text"][k] = {"box": b, "colour": darkest(b) if b else None,
                      "height": (b[3] - b[1] + 1) if b else None,
                      "width": (b[2] - b[0] + 1) if b else None}
# ---- solid-shape anchors: bbox of a colour inside a window ------------------------------
def colour_rect(colour, x0, y0, x1, y1, tol=14, min_pix=20):
    """x1/y1 are INCLUSIVE pixel indices (the caller's window edge, not a slice bound)."""
    x1, y1 = min(int(x1), W - 1), min(int(y1), H - 1)
    c = rgb(colour) if isinstance(colour, str) else np.asarray(colour)
    m = (np.abs(a[y0:y1 + 1, x0:x1 + 1] - c).max(axis=2) <= tol)
    if m.sum() < min_pix:
        return None
    ys, xs = np.flatnonzero(m.any(axis=1)), np.flatnonzero(m.any(axis=0))
    return [x0 + int(xs[0]), y0 + int(ys[0]), x0 + int(xs[-1]), y0 + int(ys[-1])]


LOGO_WIN = (20, 25, 62, 68)
_seg = a[LOGO_WIN[1]:LOGO_WIN[3] + 1, LOGO_WIN[0]:LOGO_WIN[2] + 1].reshape(-1, 3)
_hue = _seg.max(axis=1) - _seg.min(axis=1)
LOGO = "#%02X%02X%02X" % tuple(int(v) for v in _seg[_hue.argmax()])
out["colours"]["logo"] = LOGO
out["regions"]["logo"] = colour_rect(LOGO, *LOGO_WIN, tol=26)
def contrast_rect(base, x0, y0, x1, y1, tol=12):
    """Bbox of everything that differs from a flat local background — robust where the shape
    carries text of another colour inside it (a colour match would stop at the glyphs)."""
    c = rgb(base) if isinstance(base, str) else np.asarray(base)
    x1, y1 = min(int(x1), W - 1), min(int(y1), H - 1)
    m = (np.abs(a[y0:y1 + 1, x0:x1 + 1] - c).max(axis=2) > tol)
    if not m.any():
        return None
    ys, xs = np.flatnonzero(m.any(axis=1)), np.flatnonzero(m.any(axis=0))
    return [x0 + int(xs[0]), y0 + int(ys[0]), x0 + int(xs[-1]), y0 + int(ys[-1])]


out["regions"]["nav_pill"] = contrast_rect(out["colours"]["sidebar"], 4, 100, 219, 175)
out["regions"]["export_btn"] = contrast_rect(PAGE_BG, 1100, 20, 1439, 120)
out["regions"]["workspace_card"] = colour_rect(out["colours"]["workspace_card"],
                                               0, 700, 220, 890)
out["regions"]["table_header_band"] = colour_rect(out["colours"]["table_header_band"],
                                                  260, 686, 1399, 720)
# nav bullets: the inactive ones are a dim slate, the active one is the brand green
out["regions"]["nav_dots"] = []
for y0, y1 in [(115, 160), (180, 225), (245, 290), (310, 355)]:
    win = a[y0:y1 + 1, 28:56].reshape(-1, 3)
    keys, counts = np.unique(win // 8, axis=0, return_counts=True)
    order = counts.argsort()[::-1]
    col = None
    for j in order:
        c = keys[j] * 8 + 4
        if abs(int(c[0]) - 20) + abs(int(c[1]) - 35) + abs(int(c[2]) - 60) > 40:
            col = "#%02X%02X%02X" % tuple(int(v) for v in c)
            break
    out["regions"]["nav_dots"].append({"band": [28, y0, 55, y1], "colour": col,
                                       "rect": colour_rect(col, 28, y0, 55, y1, 14)
                                       if col else None})
out["regions"]["activity_dots"] = []
for y0, y1 in [(390, 415), (450, 475), (510, 535)]:
    r = None
    for x0 in range(1040, 1075):
        for yy in range(y0, y1):
            px = a[yy, x0]
            if px.max() - px.min() > 40:
                r = colour_rect("#%02X%02X%02X" % tuple(px), x0 - 2, y0, x0 + 14, y1)
                break
        if r:
            break
    out["regions"]["activity_dots"].append(r)
def anchor(b):
    return {"box": b, "colour": darkest(b) if b else None,
            "height": (b[3] - b[1] + 1) if b else None,
            "width": (b[2] - b[0] + 1) if b else None}


# gridline x-extent / bar pitch: derived from the image so both reference and rebuild agree
gl_rows = out["regions"]["gridlines"]
if gl_rows:
    ys, xs = gl_rows[0], np.flatnonzero(
        (np.abs(a[gl_rows[0], 260:1001] - gl_c).max(axis=1) <= 12))
    out["regions"]["grid_extent"] = ([260 + int(xs[0]), min(gl_rows),
                                      260 + int(xs[-1]), max(gl_rows)]
                                     if len(xs) else None)
bs = out["regions"]["bars"]
if bs:
    out["regions"]["bar_geom"] = {"width": bs[0][2] - bs[0][0] + 1,
                                  "pitch": bs[1][0] - bs[0][0] if len(bs) > 1 else None,
                                  "zero_y": max(b[3] for b in bs)}


for k in (2, 3):
    x0 = {2: 660, 3: 1045}[k]
    out["text"][f"kpi{k}_label"] = anchor(text_box(x0, 148, x0 + 340, 180, 620))
    out["text"][f"kpi{k}_delta"] = anchor(text_box(x0, 240, x0 + 340, 268, 620))

OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print("measured", IMG.name, "->", OUT.name)
print("cards:", out["regions"]["cards"])
print("bars:", out["regions"]["bars"])
print("gridlines:", out["regions"]["gridlines"])
print("pills:", json.dumps(out["regions"].get("pills"), ensure_ascii=False))
print("colours:", json.dumps(out["colours"], ensure_ascii=False))
for k, v in out["text"].items():
    print(f"{k:16s} {v['box']} h={v['height']} {v['colour']}")
