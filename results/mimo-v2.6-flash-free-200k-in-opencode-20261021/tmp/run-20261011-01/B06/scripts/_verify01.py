# -*- coding: utf-8 -*-
"""Pixel-verify case-01 ring geometry, accounting for two known overlaps.

Two effects are expected and are measured here rather than hidden:
  * seam overshoot -- arc() draws tangent rects whose length includes
    thick*0.6 of overlap, so the band bleeds a few degrees past each end
    point. Measured and bounded below.
  * dot coverage  -- a med dot (r=25) painted on the ring hides the band
    beneath it, so angles within +/-8 deg of a dot are skipped on BOTH
    the elapsed band and its mirror range (the mirror check must not
    require dark where a coloured dot is painted).
Everything else must read as the elapsed colour inside [0, 116.25] and as
the dark track outside it.
"""
import math
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PNG = os.path.join(HERE, "..", "drafts", "case-01-v3.png")
CX, CY, R = 390.0, 452.0, 196.0
NOW_DEG = 7.75 / 24.0 * 360.0            # 116.25

im = Image.open(PNG).convert("RGB")
assert im.size == (780, 1688), im.size


def at_xy(deg, r):
    a = math.radians(deg)
    return CX + r * math.sin(a), CY - r * math.cos(a)


def at(deg, r):
    x, y = at_xy(deg, r)
    return im.getpixel((int(round(x)), int(round(y))))


def near(px, hexcol, tol=26):
    t = tuple(int(hexcol[i:i + 2], 16) for i in (1, 3, 5))
    return all(abs(px[i] - t[i]) <= tol for i in range(3))


ELAPSED, TRACK = "#2A6E8F", "#173549"
DOT_ANGLES = [7.5 / 24 * 360, 8.0 / 24 * 360, 18.0 / 24 * 360, 21.5 / 24 * 360]


def covered_by_dot(deg):
    return any(min(abs(deg - d), 360 - abs(deg - d)) <= 8 for d in DOT_ANGLES)


# ---- 1. measure the painted band first (its ends bound the seam bleed) ----
start = 0
while start > -30 and near(at(start % 360, R), ELAPSED):
    start -= 2
end = int(NOW_DEG)
while end < int(NOW_DEG) + 30 and near(at(end, R), ELAPSED):
    end += 2
bleed_lo, bleed_hi = -start, end - NOW_DEG
print("painted band: %d deg .. %d deg (nominal 0 .. %.2f)" % (start, end, NOW_DEG))
print("  seam overshoot: -%.0f deg at 00:00, +%.0f deg at 07:45"
      % (bleed_lo, bleed_hi))
# arc() builds the band from tangent rects whose length carries thick*0.6 of
# overlap, so a few degrees of bleed past each end point is inherent.
assert bleed_lo <= 8 and bleed_hi <= 8, "seam overshoot beyond tangent-rect bound"

# ---- 2. elapsed band, excluding dot coverage AND the measured seam bleed ---
SEAM = max(bleed_lo, bleed_hi) + 2


def in_seam(deg):
    """inside the measured overshoot window at either end point."""
    return (deg % 360) >= (360 - SEAM) or abs(deg - NOW_DEG) <= SEAM


inside = [d for d in range(0, 360, 2)
          if not covered_by_dot(d) and not in_seam(d) and near(at(d, R), ELAPSED)]
bad = [d for d in inside if not (0 <= d <= NOW_DEG + 1)]
missing = [d for d in range(0, int(NOW_DEG) - 2, 6) if not covered_by_dot(d)
           and not in_seam(d) and d not in inside]
print("elapsed band angles sampled OK: %d" % len(inside))
print("  leaked outside [0,%.2f] excluding seam: %s" % (NOW_DEG, bad))
print("  missing inside  [0,%.2f]: %s" % (NOW_DEG, missing))
assert not bad, "elapsed arc leaked outside its range"
assert not missing, "elapsed arc has gaps"

# ---- 3. mirror range must stay dark track (skipping dot-covered angles) ----
mirror_samples = [d for d in range(130, 350, 5) if not covered_by_dot(d)]
mirror = [d for d in mirror_samples if near(at(d, R), TRACK)]
missed = [d for d in mirror_samples if d not in mirror]
print("mirror range reads as dark track: %d/%d samples"
      % (len(mirror), len(mirror_samples)))
if missed:
    print("  non-track samples in mirror:", missed)
assert not missed, "elapsed arc drawn in the wrong direction"
assert len(mirror_samples) >= 35, "too few usable mirror samples"
assert not [d for d in inside if d > NOW_DEG + 1], "elapsed colour past seam"

# ---- 4. med dots at true angles -------------------------------------------
# The dot centre is painted with its index glyph and (when taken) a white
# tick badge, so sampling the exact centre is meaningless. Instead: collect
# every pixel of the dot's colour in a window around the expected point and
# check the colour centroid sits on the true angle.
for label, h, colr in [("07:30", 7.5, "#2FBF71"), ("08:00", 8.0, "#2E86DE"),
                       ("18:00", 18.0, "#E4572E"), ("21:30", 21.5, "#F2A93B")]:
    deg = h / 24.0 * 360.0
    ex, ey = at_xy(deg, R)
    exp = tuple(int(colr[i:i + 2], 16) for i in (1, 3, 5))
    px = []
    for iy in range(int(ey) - 34, int(ey) + 35):
        for ix in range(int(ex) - 34, int(ex) + 35):
            p = im.getpixel((ix, iy))
            if all(abs(p[i] - exp[i]) <= 45 for i in range(3)):
                px.append((ix, iy))
    assert len(px) > 200, "dot %s colour not found (%d px)" % (label, len(px))
    cxp = sum(p[0] for p in px) / len(px)
    cyp = sum(p[1] for p in px) / len(px)
    off = math.hypot(cxp - ex, cyp - ey)
    # how far the centroid's implied angle drifts from the true one
    ca = math.degrees(math.atan2(cxp - CX, CY - cyp)) % 360
    dang = min(abs(ca - deg), 360 - abs(ca - deg))
    print("  dot %-6s expect=(%.1f,%.1f) centroid=(%.1f,%.1f) "
          "offset=%.1fpx angle_drift=%.2fdeg -> %s"
          % (label, ex, ey, cxp, cyp, off, dang,
             "OK" if off <= 10 and dang <= 4 else "MISS"))
    assert off <= 10 and dang <= 4, "dot %s off its true angle" % label

# ---- 5. major ticks -------------------------------------------------------
n = 0
for h in (0, 6, 12, 18):
    deg = h / 24.0 * 360.0
    found = any(near(at(deg, r), "#5C7C99", tol=30) for r in range(118, 176, 4))
    print("  major tick %02d:00 -> %s" % (h, "OK" if found else "MISS"))
    n += found
assert n == 4, "only %d/4 major ticks" % n

print("\nALL GEOMETRY CHECKS PASSED")
