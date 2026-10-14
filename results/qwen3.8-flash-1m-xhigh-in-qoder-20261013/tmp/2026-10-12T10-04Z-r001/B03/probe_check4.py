"""Readout for B03 probe round 4 - decides the six open capability questions.

Run: python tmp/<run_id>/B03/probe_check4.py
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from PIL import Image

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
TMP = ROOT / "tmp" / "2026-10-12T10-04Z-r001" / "B03"
EV: dict = {}


def load(name):
    return Image.open(TMP / f"p4-{name}.png").convert("RGB")


def px(im, x, y):
    return im.getpixel((int(x), int(y)))


def lum(c):
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def ink_rows(im, y0, y1, x0, x1, thresh=170, step=2):
    return [y for y in range(y0, y1)
            if any(lum(px(im, x, y)) < thresh for x in range(x0, x1, step))]


def bands(rows):
    out = []
    for y in rows:
        if out and y == out[-1][-1] + 1:
            out[-1].append(y)
        else:
            out.append([y])
    return [(g[0], g[-1]) for g in out]


def ink_extent(im, y0, y1, x0, x1, thresh=170):
    cols = [x for x in range(x0, x1)
            if any(lum(px(im, x, y)) < thresh for y in range(y0, y1))]
    return None if not cols else (cols[0], cols[-1], cols[-1] - cols[0] + 1)


# 1 Opacity
im = load("opacity")
EV["opacity"] = {"plain": list(px(im, 110, 60)), "at_035": list(px(im, 310, 60)),
                 "sheet": list(px(im, 210, 110))}

# 2 line height on wrapped copy
im = load("lineheight")
lb = bands(ink_rows(im, 16, 250, 24, 236))
rb = bands(ink_rows(im, 16, 250, 284, 496))
EV["lineheight"] = {"left_bands": lb[:6], "right_bands": rb[:6],
                    "left_pitch": (lb[1][0] - lb[0][0]) if len(lb) > 1 else None,
                    "right_pitch": (rb[1][0] - rb[0][0]) if len(rb) > 1 else None,
                    "left_lines": len(lb), "right_lines": len(rb)}

# 3 Raw vs trimmed Text
im = load("rawspan")
EV["rawspan"] = {"text_row": ink_extent(im, 20, 54, 16, 500),
                 "raw_row": ink_extent(im, 70, 104, 16, 500)}

# 4 custom boxShadow scan: vertical ramp under the card, no text in the column
im = load("shadowscan")
custom = [list(px(im, 160, y)) for y in (112, 118, 124, 130)]
elev = [list(px(im, 160, y)) for y in (262, 268, 274, 280)]
EV["shadowscan"] = {"custom_below": custom, "elevation6_below": elev,
                    "sheet": list(px(im, 20, 20)),
                    "custom_right": [list(px(im, x, 75)) for x in (264, 270, 276)]}

# 5 radial tile modes: count dark rings along the horizontal centre line
EV["radialtile"] = {}
for mode in ("CLAMP", "REPEAT", "MIRROR", "DECAL"):
    im = load(f"radialtile{mode}")
    row = [lum(px(im, x, 100)) for x in range(10, 190)]
    dark = sum(1 for v in row if v < 60)
    mid = sum(1 for a, b in zip(row, row[1:]) if a < 60 <= b)
    EV["radialtile"][mode] = {"dark_px": dark, "dark_to_light_edges": mid,
                              "centre": list(px(im, 100, 100)),
                              "at_45px": list(px(im, 55, 100)),
                              "corner": list(px(im, 15, 15))}

# 6 dotted vs dashed horizontal runs, and WidgetSpan BASELINE placement
im = load("decorun")
def red_runs(y0, y1):
    on = [any(px(im, x, y)[0] - px(im, x, y)[1] > 60 for y in range(y0, y1))
          for x in range(20, 500)]
    runs = sum(1 for a, b in zip(on, on[1:]) if b and not a)
    return {"on_px": sum(on), "runs": runs + (1 if on and on[0] else 0)}
EV["decorun"] = {"dotted": red_runs(46, 60), "dashed": red_runs(86, 100)}
box = [(x, y) for y in range(100, 150) for x in range(120, 400)
       if px(im, x, y)[0] > 180 and px(im, x, y)[1] < 110]
EV["decorun"]["widgetspan_box"] = (min(p[0] for p in box), max(p[0] for p in box),
                                   min(p[1] for p in box), max(p[1] for p in box),
                                   len(box)) if box else None

# 7 small caps pixel diff between the two rows
im = load("smallcaps")
diff = sum(1 for y in range(18, 60) for x in range(18, 400)
           if abs(lum(px(im, x, y)) - lum(px(im, x, y + 50))) > 60)
EV["smallcaps"] = {"row1": ink_extent(im, 18, 58, 16, 410),
                   "row2": ink_extent(im, 68, 108, 16, 410), "changed_px": diff}

(TMP / "probe-evidence4.json").write_text(json.dumps(EV, indent=2), encoding="utf-8")
print(json.dumps(EV, indent=2, ensure_ascii=False))
