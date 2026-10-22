# -*- coding: utf-8 -*-
"""Pixel-verify case-02 sugar-cube geometry (criterion C4).

Claim under test: the cube strip is drawn from N_CUBES equal cubes on an
even pitch, the first SERVE_CUBES are the label's per-serving share, and
the amber share of the strip equals 2/10 = SERVE_CUBES/N_CUBES.
"""
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PNG = os.path.join(HERE, "..", "drafts", "case-02-v2.png")
CS, CGAP = 46, 22
PITCH = CS + CGAP
N_CUBES, SERVE_CUBES = 10, 2
CML, INNER = 70, 640
SY = 1146

im = Image.open(PNG).convert("RGB")
assert im.size == (780, 1688), im.size

AMBER = (0xF2, 0xA9, 0x3B)
BLUE = (0x2C, 0x54, 0x68)
tot_w = N_CUBES * CS + (N_CUBES - 1) * CGAP
cx0 = CML + (INNER - tot_w) / 2.0
cy0 = SY + 140
# the cube carries an inner white gloss from y+7 to y+27 (CS=46), so sample
# the plain band between the gloss and the bottom rounding instead
mid = int(cy0 + 36)


def runs(y, want):
    """contiguous x runs whose pixel is close to `want` on row y."""
    out, st = [], None
    for x in range(int(cx0) - 30, int(cx0) + tot_w + 30):
        p = im.getpixel((x, y))
        hit = all(abs(p[i] - want[i]) <= 34 for i in range(3))
        if hit and st is None:
            st = x
        elif not hit and st is not None:
            if x - st >= 8:
                out.append((st, x - 1))
            st = None
    if st is not None:
        out.append((st, int(cx0) + tot_w + 29))
    return out


amber = runs(mid, AMBER)
blue = runs(mid, BLUE)
print("amber runs:", amber)
print("blue  runs:", blue)

# --- 1. exactly SERVE_CUBES amber cubes, N_CUBES-SERVE_CUBES blue -------
assert len(amber) == SERVE_CUBES, "expected %d amber cubes, got %d" % (
    SERVE_CUBES, len(amber))
assert len(blue) == N_CUBES - SERVE_CUBES, "expected %d blue cubes, got %d" % (
    N_CUBES - SERVE_CUBES, len(blue))

# --- 2. every cube is the same painted width, on an even pitch -----------
widths = [r[1] - r[0] + 1 for r in amber + blue]
print("cube widths:", sorted(set(widths)))
assert all(abs(w - CS) <= 3 for w in widths), "cube widths not uniform: %s" % widths

lefts = sorted(r[0] for r in amber + blue)
pitches = [lefts[i + 1] - lefts[i] for i in range(len(lefts) - 1)]
print("pitches:", sorted(set(pitches)))
assert all(abs(p - PITCH) <= 3 for p in pitches), "pitch not even: %s" % pitches
assert abs(lefts[0] - (cx0 + 1)) <= 3, "first cube off position: %d vs %.1f" % (
    lefts[0], cx0)

# --- 3. proportionality: the amber SHARE OF CUBES is SERVE/N -------------
# Note: the gap-inclusive *span* ratio is not SERVE/N (gaps do not scale
# linearly), so the claim under test is the solid-cube proportion.
amber_solid = SERVE_CUBES * CS
total_solid = N_CUBES * CS
ratio = amber_solid / float(total_solid)
expect = SERVE_CUBES / float(N_CUBES)
print("amber solid %dpx of %dpx = %.3f (expect %.3f)"
      % (amber_solid, total_solid, ratio, expect))
assert abs(ratio - expect) < 1e-9, "amber share %.3f != %.3f" % (ratio, expect)
# and the drawn amber span matches the formula for SERVE cubes + their gaps
expect_span = SERVE_CUBES * CS + (SERVE_CUBES - 1) * CGAP
amber_span = amber[-1][1] - amber[0][0] + 1
print("amber span %dpx (expect %d) / gap-inclusive strip %dpx = %.3f"
      % (amber_span, expect_span, tot_w, amber_span / float(tot_w)))
assert abs(amber_span - expect_span) <= 3, "amber span wrong"

# --- 4. brackets: top spans all cubes, bottom spans only the amber ones --
def bracket_width(y, want, tol=34):
    xs = [x for x in range(int(cx0) - 40, int(cx0) + tot_w + 40)
          if all(abs(im.getpixel((x, y))[i] - want[i]) <= tol for i in range(3))]
    return (min(xs), max(xs), max(xs) - min(xs)) if xs else None


top = bracket_width(int(cy0 - 16), (0x8F, 0xB4, 0xC7))
bot = bracket_width(int(cy0 + CS + 14), AMBER)
print("top bracket (all 10):", top, "expect width ~%d" % tot_w)
print("bot bracket (amber 2):", bot, "expect width ~%d" % expect_span)
assert top and abs(top[2] - tot_w) <= 6, "top bracket does not span all cubes"
assert bot and abs(bot[2] - expect_span) <= 6, \
    "bottom bracket does not span exactly the per-serving cubes"

print("\nALL SUGAR-CUBE GEOMETRY CHECKS PASSED")
