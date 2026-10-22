# -*- coding: utf-8 -*-
"""Locate the blur region in handbook-04.png by edge-sharpness probes."""
import pathlib
from PIL import Image

p = pathlib.Path("tmp/run-20261011-01/A17/gen/handbook-04.png")
im = Image.open(p).convert("RGB")
px = im.load()
W, H = im.size
print("size", W, H)


def vprofile(x, y0, y1, label):
    vals = [px[x, y][0] for y in range(y0, y1)]
    print(f"{label} x={x} y{y0}..{y1}: {vals}")


def hprofile(y, x0, x1, label, step=1):
    vals = [px[x, y][0] for x in range(x0, x1, step)]
    print(f"{label} y={y} x{x0}..{x1}: {vals}")


def edge_width(vals):
    """Count pixels within 10%..90% transition -> blur width."""
    lo, hi = min(vals), max(vals)
    if hi - lo < 30:
        return None
    t0 = lo + 0.1 * (hi - lo)
    t1 = lo + 0.9 * (hi - lo)
    inside = [i for i, v in enumerate(vals) if t0 <= v <= t1]
    return (min(inside), max(inside), max(inside) - min(inside) + 1) if inside else None


# 1) accent bar top edge (y=48) -- painted first
vprofile(600, 40, 62, "accent bar")
# 2) title stroke: scan a horizontal slice across title text ~y=118
hprofile(118, 48, 140, "title slice")
# 3) intro text slice ~y=186
hprofile(186, 48, 140, "intro slice")
# 4) heading 4.1 slice y~290
hprofile(290, 48, 140, "h41 slice")
# 5) frame card top border at y=322 (color #F8FAFC -> border #E2E8F0)
vprofile(300, 314, 330, "frame top border")
# 6) white card border y=378
vprofile(200, 370, 388, "white card border")
# 7) stripe left edge: page x = 76+24 = 100, y ~420
hprofile(420, 92, 112, "stripe left edge")
# 8) solid purple left edge: page x = 76+24 = 100, y = 378+88+30 = 496
hprofile(496, 92, 112, "solid purple left edge")
# 9) opacity bar left edge: y = 378+168+26 = 572
hprofile(572, 92, 112, "opacity bar left edge")
# 10) right column text slice y~330
hprofile(330, 540, 620, "right col text slice")
# 11) heading 4.2 slice y~706 (painted after core)
hprofile(706, 48, 140, "h42 slice")
# 12) footer rule y=1508
vprofile(600, 1500, 1516, "footer rule")
