"""A15 · sample the exact colours A15 needs, plus a few text-position scans."""
from __future__ import annotations

import sys

from PIL import Image

P = sys.argv[1] if len(sys.argv) > 1 else \
    r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tasks\A15-reference-reconstruction\inputs\reference.png"
im = Image.open(P).convert("RGB")
px = im.load()
hx = lambda c: "#%02X%02X%02X" % c[:3]

PTS = {
    "title_ink": (300, 55), "subtitle_ink": (300, 93), "kpi_label": (300, 170),
    "kpi_value": (300, 210), "kpi_change_1": (295, 251), "kpi_change_3": (1060, 251),
    "card_border": (260, 200), "gridline": (340, 441), "row_sep": (600, 760),
    "tbl_header_bg": (600, 700), "tbl_header_text": (300, 702),
    "cell_project": (300, 741), "cell_owner": (800, 741), "cell_due": (1260, 741),
    "pill_blue_bg": (1060, 732), "pill_amber_bg": (1060, 767), "pill_green_bg": (1060, 802),
    "act_dot1": (1058, 401), "act_dot2": (1058, 461), "act_dot3": (1058, 521),
    "act_item_text": (1100, 400), "act_time_text": (1100, 428),
    "sidebar": (110, 500), "nav_sel_bg": (25, 140), "nav_sel_text": (70, 139),
    "nav_idle_text": (70, 199), "nav_idle_dot": (39, 199),
    "workspace_panel": (110, 760), "ws_label": (35, 775), "ws_text": (35, 807),
    "btn_text": (1290, 66), "brand_text": (80, 45), "logo_teal": (35, 37),
    "footer_text": (280, 873), "bar": (380, 500),
}
for k, (x, y) in PTS.items():
    print(f"{k:18s} ({x:4d},{y:3d}) {hx(px[x, y])}")

print()
for label, (x, y0, y1) in {
    "KPI1 col x=286": (286, 150, 280),
    "title col x=270": (270, 30, 110),
    "nav text x=70": (70, 110, 350),
    "table col x=300": (300, 630, 850),
    "activity col x=1100": (1100, 380, 600),
}.items():
    print(f"--- {label}")
    prev = None
    for y in range(y0, y1):
        dark = max(px[x, y][:3]) < 200
        if dark != prev:
            print(f"   y={y:4d} {'ink' if dark else 'bg '} {hx(px[x, y])}")
            prev = dark

print()
for label, (y, x0, x1) in {
    "kpi1 row y=210": (210, 270, 640),
    "table header row y=702": (702, 280, 1400),
    "table row1 y=741": (741, 280, 1400),
    "title row y=55": (55, 255, 700),
    "btn row y=66": (66, 1170, 1410),
    "footer row y=873": (873, 255, 700),
    "act item1 y=400": (400, 1040, 1400),
}.items():
    print(f"--- {label}")
    prev = None
    for x in range(x0, x1):
        c = px[x, y]
        kind = "ink" if sum(c[:3]) < 600 else "bg"
        if kind != prev:
            print(f"   x={x:4d} {kind} {hx(c)}")
            prev = kind
