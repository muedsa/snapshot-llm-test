"""A04 pixel self-check: ink outside panel boxes + safe-margin ring.

Usage: python tmp/<run_id>/A04/check_overflow.py <png>
Panels are the boxes declared in generate_a04.py; any pixel whose brightest channel
exceeds INK_MIN inside the checked bands is treated as text/graphics ink
(panel fill #131D31 maxes at 49, so the threshold separates ink from background).
"""
import json
import sys
from pathlib import Path

from PIL import Image

INK_MIN = 90
path = Path(sys.argv[1])
im = Image.open(path).convert("RGB")
W, H = im.size
px = im.load()

PANELS = {
    "p1": (32, 128, 636, 584),
    "p2": (656, 128, 1086, 584),
    "p3": (1106, 128, 1568, 584),
    "p4": (32, 600, 758, 968),
    "p5": (782, 600, 1568, 968),
}


def ink(x0, y0, x1, y1):
    hits = []
    for y in range(max(0, y0), min(H, y1)):
        run = None
        for x in range(max(0, x0), min(W, x1)):
            r, g, b = px[x, y]
            on = max(r, g, b) >= INK_MIN
            if on and run is None:
                run = x
            elif not on and run is not None:
                hits.append((y, run, x - 1))
                run = None
        if run is not None:
            hits.append((y, run, min(W, x1) - 1))
    return hits


out = {"image": str(path), "size": [W, H], "panels": {}}
for name, (x0, y0, x1, y1) in PANELS.items():
    # band straddling the bottom border: inside 6px and outside 12px
    inside = ink(x0 + 2, y1 - 6, x1 - 2, y1)
    outside = ink(x0 + 2, y1, x1 - 2, y1 + 12)
    right = ink(x1, y0 + 2, x1 + 12, y1 - 2)
    out["panels"][name] = {
        "box": [x0, y0, x1, y1],
        "ink_rows_inside_bottom": sorted({y for y, _, _ in inside}),
        "ink_outside_bottom": len(outside),
        "ink_outside_bottom_runs": outside[:8],
        "ink_outside_right": len(right),
        "ink_outside_right_runs": right[:8],
    }

ring = []
for y in range(H):
    for x in range(W):
        if x < 32 or x >= W - 32 or y < 32 or y >= H - 32:
            r, g, b = px[x, y]
            if max(r, g, b) >= INK_MIN:
                ring.append((x, y))
out["safe_margin_32_violations"] = len(ring)
out["safe_margin_first"] = ring[:10]
print(json.dumps(out, ensure_ascii=False, indent=1))
