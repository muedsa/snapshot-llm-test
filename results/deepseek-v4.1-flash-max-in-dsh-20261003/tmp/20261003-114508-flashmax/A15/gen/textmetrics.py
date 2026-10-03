"""A15 · per-text-block ink box comparison (reference vs reconstruction)."""
from __future__ import annotations

import os
import sys

from PIL import Image

REF = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tasks\A15-reference-reconstruction\inputs\reference.png"
NEW = sys.argv[1] if len(sys.argv) > 1 else \
    r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A15\png\reconstructed.v2.png"

REGIONS = {
    "title": (255, 25, 900, 80, "dark"),
    "subtitle": (255, 82, 900, 108, "dark"),
    "brand": (68, 30, 210, 60, "light"),
    "nav_selected": (60, 122, 200, 158, "light"),
    "nav_idle2": (58, 185, 210, 215, "light"),
    "ws_label": (34, 764, 190, 784, "light"),
    "ws_text": (34, 790, 190, 816, "light"),
    "ws_link": (34, 822, 190, 848, "light"),
    "kpi1_label": (280, 155, 460, 178, "dark"),
    "kpi1_value": (276, 190, 560, 240, "dark"),
    "kpi1_change": (280, 240, 400, 266, "dark"),
    "chart_title": (280, 328, 470, 362, "dark"),
    "chart_period": (860, 328, 985, 358, "dark"),
    "chart_unit": (280, 360, 380, 388, "dark"),
    "act_title": (1050, 328, 1250, 362, "dark"),
    "act_item1": (1072, 388, 1300, 416, "dark"),
    "tbl_title": (280, 636, 500, 672, "dark"),
    "tbl_head_project": (290, 692, 420, 716, "dark"),
    "btn_text": (1200, 50, 1390, 86, "light"),
    "act_time1": (1072, 420, 1220, 444, "dark"),
    "month_apr": (355, 553, 415, 580, "dark"),
    "tick_120": (286, 396, 322, 414, "dark"),
    "tick_0": (286, 540, 322, 558, "dark"),
    "cell_project1": (290, 730, 560, 756, "dark"),
    "cell_owner1": (780, 730, 940, 756, "dark"),
    "cell_due1": (1235, 730, 1360, 756, "dark"),
    "pill1_text": (1040, 730, 1170, 756, "dark"),
    "tbl_head_owner": (780, 692, 900, 716, "dark"),
    "tbl_head_status": (1020, 692, 1140, 716, "dark"),
    "tbl_head_due": (1235, 692, 1340, 716, "dark"),
    "footer": (255, 860, 560, 886, "dark"),
}


def ink_box(im, box, mode):
    px = im.crop(box).load()
    w, h = box[2] - box[0], box[3] - box[1]
    l = t = r = b = None
    for y in range(h):
        for x in range(w):
            c = px[x, y]
            hit = (max(c) < 205) if mode == "dark" else (min(c) > 150)
            if hit:
                l = x if l is None or x < l else l
                r = x if r is None or x > r else r
                t = y if t is None else t
                b = y if b is None or y > b else b
    if l is None:
        return None
    return [box[0] + l, box[1] + t, box[0] + r, box[1] + b]


ref = Image.open(REF).convert("RGB")
new = Image.open(NEW).convert("RGB")
print(f"{'block':18s} {'ref x0,x1,y0,y1 (w x h)':34s} {'new x0,x1,y0,y1 (w x h)':34s} dw dh dx dy")
for name, (x0, y0, x1, y1, mode) in REGIONS.items():
    a = ink_box(ref, (x0, y0, x1, y1), mode)
    b = ink_box(new, (x0, y0, x1, y1), mode)
    if not a or not b:
        print(f"{name:18s} {str(a):34s} {str(b):34s} MISSING")
        continue
    f = lambda v: (v[2] - v[0] + 1, v[3] - v[1] + 1)
    aw, ah = f(a)
    bw, bh = f(b)
    print(f"{name:18s} {str(a):34s} {str(b):34s} {bw-aw:+4d} {bh-ah:+4d} "
          f"{b[0]-a[0]:+4d} {b[1]-a[1]:+4d}")
