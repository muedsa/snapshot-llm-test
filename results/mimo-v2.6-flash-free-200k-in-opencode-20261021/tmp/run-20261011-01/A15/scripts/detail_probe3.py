# -*- coding: utf-8 -*-
"""A15 detail probe v3: '0' y-label, nav dots, card corner radii."""
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

# 1) '0' label: wide window, and dark-only (exclude gridline lum236)
R["zero_label_glyph"] = bbox(265, 535, 345, 560, lambda p: lum(p) < 160)
# also profile of dark pixels per row there
prof = {}
for y in range(535, 561):
    xs = [x for x in range(265, 346) if lum(px[x, y]) < 160]
    if xs:
        prof[str(y)] = [min(xs), max(xs), len(xs)]
R["zero_label_profile"] = prof

# 2) nav green selected dot
R["nav_dot_selected"] = bbox(20, 118, 62, 162,
                             lambda p: p[1] - p[0] > 60 and p[1] > 120)
# unsel dot rows: slate (119,145,179) on (20,35,60)
R["nav_dot_projects"] = bbox(20, 182, 62, 226,
                             lambda p: p[2] - p[0] > 80 and p[0] > 70)

# 3) card corner radii: first non-bg x per row near top-left corner
BG = (243, 246, 251)


def corner(left, top, rows=8, span=40):
    out = {}
    for dy in range(1, rows + 1):
        y = top + dy
        for x in range(left - 4, left - 4 + span):
            p = px[x, y]
            if abs(p[0] - BG[0]) + abs(p[1] - BG[1]) + abs(p[2] - BG[2]) > 8:
                out[str(dy)] = x - left
                break
    return out


R["kpi1_corner"] = corner(260, 138)
R["chart_corner"] = corner(260, 310)
R["table_corner"] = corner(260, 624)
R["activity_corner"] = corner(1030, 310)
# sidebar workspace card corner vs sidebar bg
SB = (20, 35, 60)
ws = {}
for dy in range(1, 9):
    y = 752 + dy
    for x in range(18, 60):
        p = px[x, y]
        if abs(p[0] - SB[0]) + abs(p[1] - SB[1]) + abs(p[2] - SB[2]) > 8:
            ws[str(dy)] = x - 22
            break
R["workspace_corner"] = ws
# nav pill corner (pill starts x18 y116, bg 41,68,103 on 20,35,60)
pill = {}
for dy in range(1, 9):
    y = 116 + dy
    for x in range(14, 60):
        p = px[x, y]
        if abs(p[0] - SB[0]) + abs(p[1] - SB[1]) + abs(p[2] - SB[2]) > 10:
            pill[str(dy)] = x - 18
            break
R["navpill_corner"] = pill
# export button corner (1184,43 blue on bg)
btn = {}
for dy in range(1, 9):
    y = 43 + dy
    for x in range(1180, 1230):
        p = px[x, y]
        if abs(p[0] - BG[0]) + abs(p[1] - BG[1]) + abs(p[2] - BG[2]) > 8:
            btn[str(dy)] = x - 1184
            break
R["button_corner"] = btn
# status pill corner: pill 1028,729 fill 231,239,255 on white
sp = {}
for dy in range(1, 9):
    y = 729 + dy
    for x in range(1024, 1070):
        p = px[x, y]
        if abs(p[0] - 255) + abs(p[1] - 255) + abs(p[2] - 255) > 8:
            sp[str(dy)] = x - 1028
            break
R["statuspill_corner"] = sp

# 4) month label core color + selected dot core color
R["month_core"] = list(min(
    ((px[x, y], lum(px[x, y])) for y in range(561, 574)
     for x in range(373, 395)), key=lambda t: t[1])[0])
R["navdotsel_core"] = list(max(
    ((px[x, y], px[x, y][1] - px[x, y][0]) for y in range(128, 146)
     for x in range(32, 52)), key=lambda t: t[1])[0])

# 5) KPI card bottom edge exact (column x400)
ys = []
for y in range(275, 292):
    p = px[400, y]
    if abs(p[0] - BG[0]) + abs(p[1] - BG[1]) + abs(p[2] - BG[2]) > 8:
        ys.append(y)
R["kpi1_bottom_rows"] = ys

(OUT / "detail-measured-v3.json").write_text(
    json.dumps(R, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(R, ensure_ascii=False, indent=1))
