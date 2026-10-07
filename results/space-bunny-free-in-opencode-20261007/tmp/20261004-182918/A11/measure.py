"""Column-profile analyser: measures ink runs / inter-glyph gaps inside a band.

Used as rendered-pixel evidence for whitespace fidelity and decimal alignment.
Usage: python measure.py <png> <label> <y0,y1> [x0,x1] [threshold]
"""
import sys

from PIL import Image

p, label = sys.argv[1], sys.argv[2]
y0, y1 = (int(v) for v in sys.argv[3].split(","))
x0, x1 = (0, None)
if len(sys.argv) > 4 and sys.argv[4]:
    x0, x1 = (int(v) for v in sys.argv[4].split(","))
    if x1 is None:
        x1 = None
thresh = int(sys.argv[5]) if len(sys.argv) > 5 else 200

im = Image.open(p).convert("L")
W, H = im.size
x1 = x1 if x1 is not None else W
px = im.load()

runs = []          # (x_start, x_end) inclusive runs of inked columns
cur = None
for x in range(x0, x1):
    inked = False
    for yy in range(y0, min(y1, H)):
        if px[x, yy] < thresh:
            inked = True
            break
    if inked and cur is None:
        cur = x
    elif not inked and cur is not None:
        runs.append((cur, x - 1))
        cur = None
if cur is not None:
    runs.append((cur, x1 - 1))

gaps = []
for i in range(len(runs) - 1):
    g0, g1 = runs[i][1] + 1, runs[i + 1][0] - 1
    gaps.append((g0, g1, g1 - g0 + 1))

print("== %s ==  image=%dx%d band y=%d..%d thresh<%d" % (label, W, H, y0, y1, thresh))
print("ink runs: %d" % len(runs))
for i, r in enumerate(runs):
    print("  run[%2d] x=%4d..%4d  w=%3d" % (i, r[0], r[1], r[1] - r[0] + 1))
print("gaps: %d" % len(gaps))
for i, g in enumerate(gaps):
    print("  gap[%2d] x=%4d..%4d  w=%3d" % (i, g[0], g[1], g[2]))