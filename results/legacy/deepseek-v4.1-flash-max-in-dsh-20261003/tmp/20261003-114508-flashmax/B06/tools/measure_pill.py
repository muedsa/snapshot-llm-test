"""Measure the actual rendered width of a dose pill label in B06 case-01 v1.

The pill looked as if a character was missing, so rather than guess I read the ink extent
of the label rows straight out of the PNG and compare it with the width the layout assumed.
"""
from PIL import Image
import sys

p = sys.argv[1]
im = Image.open(p).convert("RGB")
px = im.load()
W, H = im.size
print("size", W, H)

# the 12:00 ferrous pill is drawn as a filled #B45309 rect around y=402-26..402
target = (180, 83, 9)          # #B45309
rows = {}
for y in range(200, 470):
    run = []
    for x in range(600, 1000):
        r, g, b = px[x, y]
        if abs(r - target[0]) < 26 and abs(g - target[1]) < 26 and abs(b - target[2]) < 26:
            run.append(x)
    if len(run) > 40:
        rows[y] = (run[0], run[-1], len(run))
ys = sorted(rows)
if ys:
    print("pill rows", ys[0], "..", ys[-1], "width", rows[ys[0]][1] - rows[ys[0]][0] + 1)
    # white text inside the pill
    top, bot = ys[0], ys[-1]
    cols = []
    for x in range(rows[top][0], rows[top][1] + 1):
        white = False
        for y in range(top, bot + 1):
            r, g, b = px[x, y]
            if r > 225 and g > 225 and b > 225:
                white = True
                break
        if white:
            cols.append(x)
    if cols:
        print("label ink", cols[0], "..", cols[-1], "width", cols[-1] - cols[0] + 1)
