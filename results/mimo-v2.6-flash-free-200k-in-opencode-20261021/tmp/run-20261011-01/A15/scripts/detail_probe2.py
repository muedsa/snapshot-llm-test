# -*- coding: utf-8 -*-
"""A15 detail probe v2: locate missing elements, fix light-on-dark colors."""
import json
import pathlib
from PIL import Image

ROOT = pathlib.Path(".")
REF = ROOT / "tasks" / "A15-reference-reconstruction" / "inputs" / "reference.png"
OUT = ROOT / "tmp" / "run-20261011-01" / "A15"
img = Image.open(REF).convert("RGB")
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


R = {}

# 1) month labels: row profile y550..605, x330..960 (dark pixel counts)
prof = {}
for y in range(550, 606):
    n = sum(1 for x in range(330, 961) if lum(px[x, y]) < 195)
    if n > 2:
        prof[str(y)] = n
R["month_rows_profile"] = prof
R["month_glyph_apr"] = bbox(330, 550, 440, 605, lambda p: lum(p) < 195)

# 2) zero '0' label: profile x270..315, y530..568
R["zero_label_glyph"] = bbox(265, 530, 316, 568, lambda p: lum(p) < 195)

# 3) DUE column full window
R["th_due_glyph2"] = bbox(1150, 692, 1400, 718, lambda p: lum(p) < 195)
R["row1_due_glyph2"] = bbox(1150, 724, 1400, 758, lambda p: lum(p) < 195)

# 4) owner color (darkest core)
R["row_owner_core"] = list(min(
    ((px[x, y], lum(px[x, y])) for y in range(735, 747)
     for x in range(783, 856)), key=lambda t: t[1])[0])

# 5) band exact edges at y695: find bg-run inside card (white outside)
runs, s = [], None
for x in range(262, 1398):
    p = px[x, 695]
    is_bg = abs(p[0] - 243) + abs(p[1] - 246) + abs(p[2] - 251) <= 4
    if is_bg and s is None:
        s = x
    elif not is_bg and s is not None:
        runs.append((s, x - 1))
        s = None
if s is not None:
    runs.append((s, 1397))
R["band_runs_y695"] = [r for r in runs if r[1] - r[0] > 5]
# band vertical exact at x900
vs, s = [], None
for y in range(680, 730):
    p = px[900, y]
    is_bg = abs(p[0] - 243) + abs(p[1] - 246) + abs(p[2] - 251) <= 4
    if is_bg and s is None:
        s = y
    elif not is_bg and s is not None:
        vs.append((s, y - 1))
        s = None
R["band_vext_x900"] = vs

# 6) separators scan y756..835
seps = []
for y in range(756, 836):
    p = px[500, y]
    if abs(p[0] - 255) + abs(p[1] - 255) + abs(p[2] - 255) > 5:
        left = right = None
        for x in range(262, 1398):
            q = px[x, y]
            if abs(q[0] - 255) + abs(q[1] - 255) + abs(q[2] - 255) > 5:
                if left is None:
                    left = x
                right = x
        seps.append({"y": y, "rgb": list(p), "x": [left, right]})
R["separator_rows"] = seps

# 7) light-on-dark text cores (BRIGHTEST)
def bright_core(x1, y1, x2, y2):
    return list(max(((px[x, y], lum(px[x, y])) for y in range(y1, y2 + 1)
                     for x in range(x1, x2 + 1)), key=lambda t: t[1])[0])


R["nav_unsel_text_core"] = bright_core(64, 191, 134, 209)
R["ws_line1_core"] = bright_core(39, 770, 151, 780)      # PRO WORKSPACE (green)
R["ws_line2_core"] = bright_core(39, 804, 173, 816)
R["ws_line3_core"] = bright_core(39, 836, 161, 849)
# green: max g-r within line1
R["ws_line1_green"] = list(max(
    ((px[x, y], px[x, y][1] - px[x, y][0]) for y in range(768, 782)
     for x in range(37, 153)), key=lambda t: t[1])[0])

# 8) logo green core (max g-r in logo box)
R["logo_green_core"] = list(max(
    ((px[x, y], px[x, y][1] - px[x, y][0]) for y in range(33, 61)
     for x in range(30, 58)), key=lambda t: t[1])[0])

# 9) unit + period + misc cores (darkest)
def dark_core(x1, y1, x2, y2):
    return list(min(((px[x, y], lum(px[x, y])) for y in range(y1, y2 + 1)
                     for x in range(x1, x2 + 1)), key=lambda t: t[1])[0])


R["unit_core"] = dark_core(288, 376, 356, 388)
R["chart_period_core"] = dark_core(897, 337, 974, 353)
R["subtitle_core"] = dark_core(261, 86, 507, 103)
R["button_core_bg"] = list(px[1200, 66])
R["ws_card_radius_probe"] = [list(px[23, 753]), list(px[30, 760]),
                             list(px[196, 753]), list(px[110, 866])]
R["pill_radius_probe"] = [list(px[1029, 742]), list(px[1035, 731]),
                          list(px[1174, 742])]

(OUT / "detail-measured-v2.json").write_text(
    json.dumps(R, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(R, ensure_ascii=False, indent=1))
