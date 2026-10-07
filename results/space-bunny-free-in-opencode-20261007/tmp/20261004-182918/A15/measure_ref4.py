"""Measurement pass 4 for A15: exact card rects, text ink boxes, nav, pills, colors.

Produces reference-measurements4.json which build_a15.py consumes directly.
"""
import json
import os

from PIL import Image

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
REF = os.path.join(ROOT, "tasks", "A15-reference-reconstruction", "inputs", "reference.png")
OUT = os.path.join(ROOT, "tmp", RUN, "A15", "reference-measurements4.json")

im = Image.open(REF).convert("RGB")
W, H = im.size
px = im.load()
res = {"width": W, "height": H, "ref": REF}


def hx(c):
    return "#%02X%02X%02X" % c


def rgb(s):
    return tuple(int(s[i:i + 2], 16) for i in (1, 3, 5))


def ink(x0, x1, y0, y1, bghex, tol=18):
    """Tight ink bbox of non-bg pixels + per-row ink extents."""
    bg = rgb(bghex)
    minx = miny = maxx = maxy = None
    rows = {}
    cols = {}
    for y in range(y0, y1):
        xs = [x for x in range(x0, x1)
              if sum(abs(px[x, y][i] - bg[i]) for i in range(3)) > tol]
        if xs:
            rows[y] = [min(xs), max(xs)]
            miny = y if miny is None else min(miny, y)
            maxy = y
            minx = min(xs) if minx is None else min(minx, min(xs))
            maxx = max(xs) if maxx is None else max(maxx, max(xs))
    for x in range(x0, x1):
        ys = [y for y in range(y0, y1)
              if sum(abs(px[x, y][i] - bg[i]) for i in range(3)) > tol]
        if ys:
            cols[x] = [min(ys), max(ys)]
    return {"bbox": [minx, miny, maxx, maxy],
            "h": (maxy - miny + 1) if miny is not None else 0,
            "w": (maxx - minx + 1) if minx is not None else 0,
            "rows": rows}


def exact_run_h(y, color, x0=0, x1=None):
    x1 = W if x1 is None else x1
    c = rgb(color)
    out, start = [], None
    for x in range(x0, x1):
        if px[x, y] == c:
            if start is None:
                start = x
        elif start is not None:
            out.append([start, x - 1])
            start = None
    if start is not None:
        out.append([start, x1 - 1])
    return out


def exact_run_v(x, color, y0=0, y1=None):
    y1 = H if y1 is None else y1
    c = rgb(color)
    out, start = [], None
    for y in range(y0, y1):
        if px[x, y] == c:
            if start is None:
                start = y
        elif start is not None:
            out.append([start, y - 1])
            start = None
    if start is not None:
        out.append([start, y1 - 1])
    return out


# ======================================================= card rectangles
res["kpi_border_row250"] = exact_run_h(250, "#E2E8F1", 230, 1440)
res["chart_border_row450"] = exact_run_h(450, "#E2E8F1", 230, 1440)
res["table_border_row700"] = exact_run_h(700, "#E2E8F1", 230, 1440)
res["kpi_border_col700_v"] = exact_run_v(700, "#E2E8F1", 120, 300)
res["chart_border_col500_v"] = exact_run_v(500, "#E2E8F1", 295, 610)
res["table_border_col500_v"] = exact_run_v(500, "#E2E8F1", 610, 860)
res["kpi_top_row139_white"] = exact_run_h(139, "#FFFFFF", 230, 1440)

# ======================================================= header
res["title"] = ink(250, 700, 22, 78, "#F3F6FB", 30)
res["title_color"] = hx(px[270, 52])
res["subtitle"] = ink(250, 600, 80, 112, "#F3F6FB", 30)
res["subtitle_color"] = hx(px[270, 93])
res["button_rect_v"] = exact_run_v(1290, "#245CE4", 20, 110)
res["button_rect_h"] = exact_run_h(62, "#245CE4", 1100, 1440)
res["button_text"] = ink(1190, 1395, 45, 90, "#245CE4", 30)
res["button_text_color"] = hx(px[1245, 62])

# ======================================================= sidebar
res["logo_outer"] = ink(20, 68, 24, 72, "#14233C", 22)
res["logo_ring_h"] = exact_run_h(46, "#64DBB6", 20, 70)
res["logo_ring_v"] = exact_run_v(33, "#64DBB6", 24, 72)
res["logo_hole"] = ink(36, 52, 38, 58, "#14233C", 22)
res["brand_text"] = ink(68, 215, 24, 72, "#14233C", 25)
res["brand_color"] = hx(px[80, 46])
res["nav_pill_v"] = exact_run_v(100, "#294467", 100, 180)
res["nav_pill_h"] = exact_run_h(134, "#294467", 0, 220)
res["nav_pill_color"] = hx(px[100, 134])
for nm, y in (("overview", 134), ("projects", 198), ("analytics", 262), ("settings", 326)):
    res["nav_%s_dot" % nm] = ink(28, 52, y - 14, y + 14, "#294467" if nm == "overview" else "#14233C", 25)
    bg = "#294467" if nm == "overview" else "#14233C"
    res["nav_%s_label" % nm] = ink(58, 200, y - 14, y + 14, bg, 25)
    res["nav_%s_dot_color" % nm] = hx(px[38, y])
    # label color = darkest pixel in label box
    best = min(((px[x, yy], (x, yy)) for x in range(58, 200) for yy in range(y - 14, y + 14)),
               key=lambda t: sum(t[0]))
    res["nav_%s_label_color" % nm] = hx(best[0])
res["sidecard_rect_v"] = exact_run_v(100, "#233954", 720, 890)
res["sidecard_rect_h"] = exact_run_h(800, "#233954", 0, 220)
res["sidecard_label"] = ink(28, 200, 762, 786, "#233954", 25)
res["sidecard_member"] = ink(28, 200, 793, 820, "#233954", 25)
res["sidecard_manage"] = ink(28, 200, 826, 858, "#233954", 25)
res["sidecard_colors"] = {
    "label": hx(px[40, 774]),
    "member": hx(px[35, 807]),
    "manage": hx(px[40, 841]),
}

# ======================================================= KPI
res["kpi1_label"] = ink(280, 600, 152, 180, "#FFFFFF", 30)
res["kpi1_label_c"] = hx(px[290, 165])
res["kpi1_value"] = ink(280, 600, 190, 242, "#FFFFFF", 30)
res["kpi1_value_c"] = hx(px[292, 212])
res["kpi1_change"] = ink(280, 600, 244, 270, "#FFFFFF", 30)
res["kpi1_change_c"] = hx(px[288, 252])
res["kpi2_value"] = ink(660, 780, 190, 242, "#FFFFFF", 30)
res["kpi3_value"] = ink(1050, 1210, 190, 242, "#FFFFFF", 30)
res["kpi_rects"] = {"row_y": 250}

# ======================================================= chart
res["chart_title"] = ink(280, 700, 324, 362, "#FFFFFF", 30)
res["chart_title_c"] = hx(px[288, 345])
res["chart_period"] = ink(820, 998, 324, 362, "#FFFFFF", 30)
res["chart_period_c"] = hx(px[902, 345])
res["chart_unit"] = ink(280, 430, 366, 396, "#FFFFFF", 30)
res["chart_unit_c"] = hx(px[292, 380])
res["gridlines"] = {
    str(gy): exact_run_h(gy, "#E7EDF5", 290, 1000) for gy in (405, 441, 477, 513, 549)
}
res["ytick"] = {
    str(gy): ink(283, 332, gy - 14, gy + 14, "#FFFFFF", 26) for gy in (405, 441, 477, 513, 549)
}
res["months"] = {
    nm: ink(cx - 34, cx + 34, 556, 580, "#FFFFFF", 26)
    for nm, cx in (("Apr", 383), ("May", 484), ("Jun", 585), ("Jul", 686), ("Aug", 787), ("Sep", 888))
}
res["bars"] = [
    {"x0": 357, "x1": 410, "top": 485, "w": 54},
    {"x0": 458, "x1": 511, "top": 463, "w": 54},
    {"x0": 559, "x1": 612, "top": 474, "w": 54},
    {"x0": 660, "x1": 713, "top": 441, "w": 54},
    {"x0": 761, "x1": 814, "top": 452, "w": 54},
    {"x0": 862, "x1": 915, "top": 420, "w": 54},
]
res["bar_radius_probe"] = {("%d,%d" % (x, y)): hx(px[x, y]) for x, y in
                           [(357, 490), (358, 487), (360, 486), (365, 484), (375, 483),
                            (383, 484), (383, 485), (356, 500), (410, 500), (411, 500)]}

# ======================================================= activity
res["act_title"] = ink(1050, 1300, 324, 362, "#FFFFFF", 30)
res["act_title_c"] = hx(px[1062, 345])
for i, y in enumerate((401, 461, 521)):
    res["act%d_dot" % (i + 1)] = ink(1046, 1070, y - 10, y + 10, "#FFFFFF", 25)
    res["act%d_dot_c" % (i + 1)] = hx(px[1058, y])
    res["act%d_title" % (i + 1)] = ink(1074, 1300, y - 14, y + 14, "#FFFFFF", 26)
for i, y in enumerate((429, 489, 549)):
    res["act%d_time" % (i + 1)] = ink(1074, 1300, y - 12, y + 12, "#FFFFFF", 26)

# ======================================================= table
res["table_title"] = ink(280, 700, 632, 678, "#FFFFFF", 30)
res["table_title_c"] = hx(px[288, 655])
res["thead_band_h"] = exact_run_h(700, "#F3F6FB", 255, 1420)
res["thead_band_v"] = exact_run_v(300, "#F3F6FB", 675, 730)
res["thead_band_c"] = hx(px[700, 700])
res["thead_bot"] = exact_run_v(700, "#FFFFFF", 675, 730)
res["colheads"] = {
    "PROJECT": ink(288, 420, 692, 718, "#F3F6FB", 25),
    "OWNER": ink(775, 900, 692, 718, "#F3F6FB", 25),
    "STATUS": ink(1025, 1140, 692, 718, "#F3F6FB", 25),
    "DUE": ink(1220, 1340, 692, 718, "#F3F6FB", 25),
}
res["colhead_c"] = hx(px[300, 705])
res["rowseps"] = {
    str(y): exact_run_h(y, "#EBEFF5", 255, 1420) for y in (760, 795)
}
res["rows"] = {}
for i, (y0, y1) in enumerate(((722, 760), (761, 795), (796, 841))):
    res["rows"]["r%d" % (i + 1)] = {
        "proj": ink(288, 520, y0, y1, "#FFFFFF", 25),
        "owner": ink(775, 920, y0, y1, "#FFFFFF", 25),
        "due": ink(1220, 1350, y0, y1, "#FFFFFF", 25),
        "status_text": ink(1040, 1180, y0, y1, "#FFFFFF", 25),
    }
res["row_text_c"] = hx(px[300, 743])
res["row_sub_c"] = hx(px[800, 743])
res["row_due_c"] = hx(px[1240, 743])
res["pills"] = {}
for nm, y in (("in_progress", 743), ("review", 777), ("done", 811)):
    bgc = {"in_progress": "#E7EFFF", "review": "#FFF3D7", "done": "#DCF5EC"}[nm]
    res["pills"][nm] = {
        "rect_h": exact_run_h(y, bgc, 1010, 1200),
        "rect_v": exact_run_v(1100, bgc, 720, 845),
        "bg": bgc,
    }
for nm, y, bgc in (("in_progress", 743, "#E7EFFF"), ("review", 777, "#FFF3D7"),
                   ("done", 811, "#DCF5EC")):
    res["pills"][nm]["text"] = ink(1040, 1180, y - 14, y + 14, bgc, 25)
    dark = min(((px[x, yy], (x, yy)) for x in range(1040, 1180) for yy in range(y - 14, y + 14)),
               key=lambda t: sum(t[0]))
    res["pills"][nm]["text_c"] = hx(dark[0])

# ======================================================= footer
res["footer"] = ink(250, 700, 858, 890, "#F3F6FB", 30)
res["footer_c"] = hx(px[266, 872])

# ======================================================= palette of distinctive colors
res["distinct"] = {}
from collections import Counter
cnt = Counter()
for y in range(0, H, 2):
    for x in range(0, W, 2):
        cnt[px[x, y]] += 1
res["distinct"]["top30"] = [{"hex": hx(c), "n": n} for c, n in cnt.most_common(30)]

with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(res, fh, ensure_ascii=False, indent=1)
print("wrote", OUT)
for k in ("kpi_border_row250", "chart_border_row450", "table_border_row700",
          "kpi_border_col700_v", "chart_border_col500_v", "table_border_col500_v",
          "button_rect_v", "button_rect_h", "gridlines", "bar_radius_probe",
          "pills", "thead_band_h", "thead_band_v", "logo_ring_h", "logo_ring_v",
          "logo_hole", "nav_pill_v", "nav_pill_h", "sidecard_rect_v", "sidecard_rect_h"):
    print("--", k, json.dumps(res.get(k), ensure_ascii=False)[:360])
