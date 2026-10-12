"""A20 · map polish after reading annotated-map.v1.png.

Problems found by looking at the render:
  * the legend card sat on top of label M03 (upper-left of the map) and hid it;
  * the y axis had a stray "100" above the map, the 10..90 tick numbers were missing, and
    the "0"/"100" corner labels were wrong;
  * the y-axis caption floated above the map instead of beside the axis.

Fixes: the legend moves to the empty lower-left band (verified clear of all 24 dots and
label boxes by a rectangle test), the axis gets its full 0..100 tick set, and the caption
sits left of the axis.
"""
from __future__ import annotations

import io
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "gen_map.py")
s = io.open(P, encoding="utf-8").read()

old_axis = '''        d.text(gx - 20, MAP_Y + MAP_H + 8, str(i * 10), 15, MUTED, family="Noto Sans Mono CJK SC",
               w=40, align="CENTER_RIGHT")
        d.text(MAP_X - 12 - 46, gy - 9, str(i * 10), 15, MUTED,
               family="Noto Sans Mono CJK SC", w=46, align="CENTER_RIGHT")
    d.text(MAP_X - 58, MAP_Y - 30, "100", 15, MUTED, family="Noto Sans Mono CJK SC")
    d.text(MAP_X - 46, MAP_Y + MAP_H + 8, "0", 15, MUTED, family="Noto Sans Mono CJK SC")
    d.text(MAP_X + MAP_W - 40, MAP_Y + MAP_H + 8, "100", 15, MUTED,
           family="Noto Sans Mono CJK SC")
    d.text(MAP_X, MAP_Y + MAP_H + 34, "逻辑坐标 x（0–100，向右递增） · 单位：指数", 18, MUTED)
    d.text(MAP_X - 58, MAP_Y - 58, "y（0–100，向上递增）", 18, MUTED)'''
new_axis = '''        d.text(gx - 20, MAP_Y + MAP_H + 8, str(i * 10), 15, MUTED,
               family="Noto Sans Mono CJK SC", w=40, align="CENTER_RIGHT")
        d.text(MAP_X - 12 - 44, gy - 9, str(i * 10), 15, MUTED,
               family="Noto Sans Mono CJK SC", w=44, align="CENTER_RIGHT")
    d.text(MAP_X + MAP_W + 6, MAP_Y + MAP_H - 9, "0", 15, MUTED,
           family="Noto Sans Mono CJK SC")
    d.text(MAP_X + MAP_W + 6, MAP_Y - 9, "100", 15, MUTED, family="Noto Sans Mono CJK SC")
    d.text(MAP_X + MAP_W - 40, MAP_Y + MAP_H + 8, "100", 15, MUTED,
           family="Noto Sans Mono CJK SC")
    d.text(MAP_X - 46, MAP_Y + MAP_H + 8, "0", 15, MUTED, family="Noto Sans Mono CJK SC")
    d.text(MAP_X, MAP_Y + MAP_H + 34, "逻辑坐标 x（0–100，向右递增） · 单位：指数", 18, MUTED)
    d.text(20, MAP_Y - 26, "y（0–100，向上递增）", 18, MUTED)'''
assert old_axis in s
s = s.replace(old_axis, new_axis)

old_leg = '''    top3 = sorted(pts, key=lambda p: -p["value"])[:3]
    lx, ly = 300.0, 176.0
    d.box(lx, ly, 300, 34 + 30 * len(top3), "#FFFFFFF2", radius=8,
          border=f"1 SOLID {BOX_BORDER}")
    d.text(lx + 12, ly + 8, "指数最高的 3 个点", 18, INK, weight="BOLD")
    for i, p in enumerate(top3):
        d.text(lx + 12, ly + 38 + i * 30, f"{p['id']}  {p['name']}", 18, MUTED)
        d.text(lx + 288 - 40, ly + 38 + i * 30, str(p["value"]), 18, TOP3,
               family="Noto Sans Mono CJK SC", w=40, align="CENTER_RIGHT")'''
new_leg = '''    top3 = sorted(pts, key=lambda p: -p["value"])[:3]
    lw, lh = 270.0, 40 + 30 * len(top3)
    # pick the first grid position whose card clears every dot and every label box
    legend_pos = None
    for ly in [780.0, 200.0, 760.0, 220.0]:
        for lx in [300.0, 1020.0, 620.0, 860.0]:
            card = {"x": lx, "y": ly, "w": lw, "h": lh}
            if lx + lw > MAP_X + MAP_W - 8 or ly + lh > MAP_Y + MAP_H - 8:
                continue
            clash = False
            for p in pts:
                b = p["label"]["box"]
                if not (card["x"] + card["w"] <= b["x"] or b["x"] + b["w"] <= card["x"]
                        or card["y"] + card["h"] <= b["y"] or b["y"] + b["h"] <= card["y"]):
                    clash = True
                    break
                ax, ay = p["anchor_px"]["x"], p["anchor_px"]["y"]
                if (card["x"] - 6 <= ax <= card["x"] + card["w"] + 6
                        and card["y"] - 6 <= ay <= card["y"] + card["h"] + 6):
                    clash = True
                    break
            if not clash:
                legend_pos = (lx, ly)
                break
        if legend_pos:
            break
    assert legend_pos is not None, "no clear position for the legend"
    lx, ly = legend_pos
    d.box(lx, ly, lw, lh, "#FFFFFFF2", radius=8, border=f"1 SOLID {BOX_BORDER}")
    d.text(lx + 12, ly + 10, "指数最高的 3 个点", 18, INK, weight="BOLD")
    for i, p in enumerate(top3):
        d.text(lx + 12, ly + 42 + i * 30, f"{p['id']}  {p['name']}", 18, MUTED)
        d.text(lx + lw - 52, ly + 42 + i * 30, str(p["value"]), 18, TOP3,
               family="Noto Sans Mono CJK SC", w=40, align="CENTER_RIGHT")'''
assert old_leg in s
s = s.replace(old_leg, new_leg)
io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("gen_map.py polished (axis ticks + clear legend placement)")
