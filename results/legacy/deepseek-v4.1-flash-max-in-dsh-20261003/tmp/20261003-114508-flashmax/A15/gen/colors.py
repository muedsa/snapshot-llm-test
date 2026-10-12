"""A15 · compare the actual ink colours of each text block in reference vs rebuild.

For every text region the darkest pixel is the least antialiased sample of the glyph
colour, which is what a reconstruction has to match.
"""
from __future__ import annotations

import sys

from PIL import Image

REF = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tasks\A15-reference-reconstruction\inputs\reference.png"
NEW = sys.argv[1] if len(sys.argv) > 1 else \
    r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A15\png\reconstructed.v1.png"

REGIONS = {
    "title": (261, 36, 600, 72), "subtitle": (261, 84, 520, 104),
    "kpi_label": (286, 158, 420, 174), "kpi_value": (280, 194, 460, 236),
    "kpi_change1": (286, 242, 360, 262), "kpi_change3": (1054, 242, 1140, 262),
    "card_title_chart": (286, 332, 420, 360), "chart_period": (890, 332, 980, 356),
    "chart_unit": (286, 364, 360, 384), "axis_tick": (290, 396, 320, 416),
    "month_label": (365, 556, 405, 578),
    "act_title": (1078, 392, 1200, 414), "act_time": (1078, 422, 1130, 440),
    "tbl_title": (286, 640, 460, 670), "tbl_header": (300, 694, 350, 712),
    "cell_project": (300, 732, 460, 754), "cell_owner": (790, 732, 880, 754),
    "footer": (261, 864, 520, 884),
    "nav_sel_text": (64, 126, 160, 154), "nav_idle_text": (64, 188, 140, 212),
    "brand_text": (73, 34, 190, 56), "ws_label": (38, 766, 160, 784),
    "ws_text": (38, 792, 160, 814), "ws_link": (38, 824, 160, 848),
    "btn_text": (1220, 54, 1370, 82),
}
ims = {k: Image.open(p).convert("RGB") for k, p in (("ref", REF), ("new", NEW))}
print(f"{'region':18s} {'reference':10s} {'rebuilt':10s} delta")
for name, box in REGIONS.items():
    out = {}
    for k, im in ims.items():
        px = im.crop(box).load()
        w, h = box[2] - box[0], box[3] - box[1]
        best, bc = 10 ** 9, None
        for y in range(h):
            for x in range(w):
                c = px[x, y]
                s = sum(c)
                if s < best:
                    best, bc = s, c
        out[k] = bc
    dr = max(abs(a - b) for a, b in zip(out["ref"], out["new"]))
    print(f"{name:18s} #{out['ref'][0]:02X}{out['ref'][1]:02X}{out['ref'][2]:02X}   "
          f"#{out['new'][0]:02X}{out['new'][1]:02X}{out['new'][2]:02X}   {dr}")
