"""A15 measurement pass 5: radii, pill rects + text ink, core text colours, band corners."""
import json
import os
from collections import Counter

from PIL import Image

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
TMP = os.path.join(ROOT, "tmp", RUN, "A15")
REF = os.path.join(ROOT, "tasks", "A15-reference-reconstruction", "inputs", "reference.png")
OUT = os.path.join(TMP, "reference-measurements5.json")

im = Image.open(REF).convert("RGB")
W, H = im.size
px = im.load()
res = {}


def hx(c):
    return "#%02X%02X%02X" % c


def rgb(s):
    return tuple(int(s[i:i + 2], 16) for i in (1, 3, 5))


def core(x0, x1, y0, y1, bg, tol=30, darkest=True):
    """Most saturated / darkest pixel colour inside a text region (glyph core colour)."""
    bgc = rgb(bg)
    cnt = Counter()
    for y in range(y0, y1):
        for x in range(x0, x1):
            c = px[x, y]
            if sum(abs(c[i] - bgc[i]) for i in range(3)) > tol:
                cnt[c] += 1
    if not cnt:
        return None
    return hx(min(cnt, key=lambda c: sum(c)))


def ink(x0, x1, y0, y1, bg, tol=30):
    bgc = rgb(bg)
    minx = miny = maxx = maxy = None
    for y in range(y0, y1):
        for x in range(x0, x1):
            if sum(abs(px[x, y][i] - bgc[i]) for i in range(3)) > tol:
                minx = x if minx is None else min(minx, x)
                maxx = x if maxx is None else max(maxx, x)
                miny = y if miny is None else min(miny, y)
                maxy = y if maxy is None else max(maxy, y)
    if minx is None:
        return None
    return {"bbox": [minx, miny, maxx, maxy], "w": maxx - minx + 1, "h": maxy - miny + 1}


def profile_v(x, y0, y1, bg):
    """Non-bg y-extent for a column (corner profile helper)."""
    bgc = rgb(bg)
    ys = [y for y in range(y0, y1)
          if sum(abs(px[x, y][i] - bgc[i]) for i in range(3)) > 6]
    return [min(ys), max(ys)] if ys else None


# --------------------------------------------------------------- core colours
res["colors"] = {
    "title": core(260, 600, 36, 72, "#F3F6FB"),
    "subtitle": core(260, 510, 83, 104, "#F3F6FB"),
    "button_text": core(1230, 1350, 52, 74, "#245CE4"),
    "brand": core(70, 195, 36, 56, "#14233C"),
    "nav_selected_label": core(60, 152, 124, 144, "#294467"),
    "nav_other_label": core(60, 138, 188, 210, "#14233C"),
    "nav_selected_dot": core(32, 48, 126, 142, "#294467"),
    "nav_other_dot": core(32, 48, 190, 206, "#14233C"),
    "side_label": core(36, 152, 768, 782, "#233954"),
    "side_member": core(36, 175, 802, 818, "#233954"),
    "side_manage": core(37, 162, 833, 850, "#233954"),
    "kpi_label": core(282, 350, 158, 173, "#FFFFFF"),
    "kpi_value": core(282, 435, 197, 230, "#FFFFFF"),
    "kpi_change": core(283, 343, 244, 260, "#FFFFFF"),
    "chart_title": core(283, 416, 334, 354, "#FFFFFF"),
    "chart_period": core(894, 976, 335, 355, "#FFFFFF"),
    "chart_unit": core(285, 358, 373, 387, "#FFFFFF"),
    "ytick": core(297, 322, 396, 409, "#FFFFFF"),
    "month": core(371, 397, 558, 575, "#FFFFFF"),
    "act_title": core(1052, 1202, 333, 358, "#FFFFFF"),
    "act_item": core(1076, 1220, 393, 413, "#FFFFFF"),
    "act_time": core(1075, 1118, 420, 435, "#FFFFFF"),
    "table_title": core(283, 456, 643, 668, "#FFFFFF"),
    "colhead": core(296, 356, 697, 710, "#F3F6FB"),
    "row_proj": core(296, 462, 732, 752, "#FFFFFF"),
    "row_owner": core(781, 858, 733, 749, "#FFFFFF"),
    "row_due": core(1229, 1286, 733, 749, "#FFFFFF"),
    "pill_inprogress": core(1040, 1168, 736, 750, "#E7EFFF"),
    "pill_review": core(1040, 1168, 770, 784, "#FFF3D7"),
    "pill_done": core(1040, 1168, 804, 818, "#DCF5EC"),
    "footer": core(258, 520, 865, 881, "#F3F6FB"),
}

# --------------------------------------------------------------- radii
# KPI card top-left corner at (260,138).  Scan the first non-bg pixel per column.
def corner_r(x_top_left, y_top_left, bg, direction=1, span=30):
    """Estimate border radius: for each column offset d, the y where content starts."""
    bgc = rgb(bg)
    out = {}
    for d in range(span):
        x = x_top_left + direction * d
        ys = [y for y in range(y_top_left, y_top_left + span)
              if sum(abs(px[x, y][i] - bgc[i]) for i in range(3)) > 6]
        out[d] = (min(ys) - y_top_left) if ys else None
    return out


res["corner_kpi_topleft"] = corner_r(260, 138, "#F3F6FB", 1, 26)
res["corner_chart_topleft"] = corner_r(260, 310, "#F3F6FB", 1, 26)
res["corner_table_topleft"] = corner_r(260, 624, "#F3F6FB", 1, 26)
res["corner_navpill_topleft"] = corner_r(18, 116, "#14233C", 1, 26)
res["corner_sidecard_topleft"] = corner_r(22, 752, "#14233C", 1, 26)
res["corner_button_topleft"] = corner_r(1184, 43, "#F3F6FB", 1, 26)
res["corner_pill_topleft"] = corner_r(1028, 729, "#FFFFFF", 1, 26)
res["corner_bar_topleft"] = corner_r(357, 485, "#FFFFFF", 1, 26)
res["corner_logo_topleft"] = corner_r(30, 33, "#14233C", 1, 26)

# --------------------------------------------------------------- pills
pills = {}
for nm, y in (("in_progress", 743), ("review", 777), ("done", 811)):
    bgc = {"in_progress": "#E7EFFF", "review": "#FFF3D7", "done": "#DCF5EC"}[nm]
    c = rgb(bgc)
    ys = [yy for yy in range(720, 845) if px[1100, yy] == c]
    xs = [xx for xx in range(1000, 1210) if px[xx, y] == c]
    pills[nm] = {"bg": bgc, "x0": min(xs), "x1": max(xs), "y0": min(ys), "y1": max(ys),
                 "w": max(xs) - min(xs) + 1, "h": max(ys) - min(ys) + 1}
    pills[nm]["text_ink"] = ink(pills[nm]["x0"] + 6, pills[nm]["x1"] - 6,
                                pills[nm]["y0"] + 4, pills[nm]["y1"] - 3, bgc, 25)
res["pills"] = pills

# --------------------------------------------------------------- thead band
band_c = rgb("#F3F6FB")
ys = [y for y in range(675, 735) if px[300, y] == band_c]
xs = [x for x in range(255, 1420) if px[x, 700] == band_c]
res["thead_band"] = {"x0": min(xs), "x1": max(xs), "y0": min(ys), "y1": max(ys),
                     "w": max(xs) - min(xs) + 1, "h": max(ys) - min(ys) + 1}
res["thead_corner"] = corner_r(min(xs), min(ys), "#FFFFFF", 1, 22)

# --------------------------------------------------------------- month labels ink
res["month_ink"] = {}
for nm, cx in (("Apr", 383), ("May", 484), ("Jun", 585), ("Jul", 686),
               ("Aug", 787), ("Sep", 888)):
    res["month_ink"][nm] = ink(cx - 40, cx + 40, 556, 580, "#FFFFFF", 26)

# --------------------------------------------------------------- row separators
res["rowseps"] = {}
for y in (760, 795):
    c = rgb("#EBEFF5")
    xs = [x for x in range(255, 1420) if px[x, y] == c]
    res["rowseps"][str(y)] = [min(xs), max(xs)] if xs else None

# --------------------------------------------------------------- logo geometry
res["logo"] = {
    "ring_color": hx(px[33, 46]),
    "outer": [30, 33, 57, 60],
    "hole_probe": {("%d,%d" % (x, y)): hx(px[x, y]) for x, y in
                   [(38, 41), (43, 45), (49, 52), (38, 41), (30, 46), (57, 46), (33, 33), (54, 60)]},
}
res["logo_corner"] = corner_r(30, 33, "#14233C", 1, 26)

# --------------------------------------------------------------- bars exact
BLUE = rgb("#245CE4")
bars = []
x = 330
run = None
while x < 980:
    ys = [y for y in range(400, 560) if px[x, y] == BLUE]
    if ys:
        if run and x == run[-1][0] + 1:
            run.append((x, min(ys), max(ys)))
        else:
            if run:
                bars.append(run)
            run = [(x, min(ys), max(ys))]
    else:
        if run:
            bars.append(run)
            run = None
    x += 1
if run:
    bars.append(run)
res["bars"] = [{"x0": b[0][0], "x1": b[-1][0], "w": b[-1][0] - b[0][0] + 1,
                "top": min(p[1] for p in b), "bot": max(p[2] for p in b),
                "h": max(p[2] for p in b) - min(p[1] for p in b) + 1}
               for b in bars if b[-1][0] - b[0][0] >= 20]

# --------------------------------------------------------------- gridlines
res["gridlines"] = {}
c = rgb("#E7EDF5")
for gy in (405, 441, 477, 513, 549):
    xs = [x for x in range(280, 1000) if px[x, gy] == c]
    res["gridlines"][str(gy)] = [min(xs), max(xs)] if xs else None

# --------------------------------------------------------------- y tick ink rights
res["ytick_ink"] = {}
for gy, lbl in ((405, "120"), (441, "90"), (477, "60"), (513, "30"), (549, "0")):
    res["ytick_ink"][lbl] = ink(285, 330, gy - 12, gy + 12, "#FFFFFF", 26)

# --------------------------------------------------------------- nav geometry
res["nav"] = {}
for nm, y in (("overview", 134), ("projects", 198), ("analytics", 262), ("settings", 326)):
    c = rgb("#64DBB6" if nm == "overview" else "#7791B3")
    ys = [yy for yy in range(y - 20, y + 20) if px[39, yy] == c]
    xs = [xx for xx in range(20, 55) if px[xx, y] == c]
    res["nav"][nm] = {"dot": [min(xs), min(ys), max(xs) - min(xs) + 1,
                              max(ys) - min(ys) + 1] if xs else None}
    res["nav"][nm]["label_ink"] = ink(56, 198, y - 14, y + 14,
                                      "#294467" if nm == "overview" else "#14233C", 26)

# --------------------------------------------------------------- button + brand
res["button"] = {"x0": 1184, "x1": 1399, "y0": 43, "y1": 90, "w": 216, "h": 48,
                 "fill": hx(px[1200, 62]), "text_ink": ink(1210, 1390, 45, 90, "#245CE4", 30)}

json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("wrote", OUT)
for k in ("colors", "pills", "thead_band", "bars", "gridlines", "rowseps",
          "button", "month_ink", "ytick_ink", "logo"):
    print("--", k, json.dumps(res[k], ensure_ascii=False)[:700])
print("-- corner_kpi", json.dumps(res["corner_kpi_topleft"]))
print("-- corner_chart", json.dumps(res["corner_chart_topleft"]))
print("-- corner_navpill", json.dumps(res["corner_navpill_topleft"]))
print("-- corner_sidecard", json.dumps(res["corner_sidecard_topleft"]))
print("-- corner_button", json.dumps(res["corner_button_topleft"]))
print("-- corner_pill", json.dumps(res["corner_pill_topleft"]))
print("-- corner_bar", json.dumps(res["corner_bar_topleft"]))
print("-- corner_logo", json.dumps(res["corner_logo_topleft"]))
print("-- thead_corner", json.dumps(res["thead_corner"]))
print("-- nav", json.dumps(res["nav"], ensure_ascii=False)[:900])
