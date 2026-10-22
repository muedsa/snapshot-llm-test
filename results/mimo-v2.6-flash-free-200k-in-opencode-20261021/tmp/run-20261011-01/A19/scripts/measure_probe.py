# -*- coding: utf-8 -*-
"""Measure the ring/shadow probe: inner diameter, shadow/text extents."""
import pathlib

from PIL import Image

PNG = pathlib.Path("tmp/run-20261011-01/A19/scripts/probe-ring.png")
im = Image.open(PNG).convert("RGB")
px = im.load()
W, H = im.size
print("size:", (W, H))


def bbox_of(pred, x0, y0, x1, y1):
    minx, miny, maxx, maxy, n = W, H, -1, -1, 0
    for y in range(y0, y1):
        for x in range(x0, x1):
            if pred(px[x, y]):
                n += 1
                minx, miny = min(minx, x), min(miny, y)
                maxx, maxy = max(maxx, x), max(maxy, y)
    return (minx, miny, maxx, maxy, n)


def near(c, t):
    return abs(c[0] - t[0]) < 45 and abs(c[1] - t[1]) < 45 and abs(c[2] - t[2]) < 45


BLUE = (37, 99, 235)
ORANGE = (245, 158, 11)
GREEN = (22, 163, 74)
PURPLE = (124, 58, 237)

print()
print("ring80 blue  bbox:", bbox_of(lambda c: near(c, BLUE), 0, 0, 125, 125))
print("ring64 orange bbox:", bbox_of(lambda c: near(c, ORANGE), 125, 0, 215, 100))
print("ring48 green  bbox:", bbox_of(lambda c: near(c, GREEN), 215, 0, 290, 90))
print("sq80 purple   bbox:", bbox_of(lambda c: near(c, PURPLE), 300, 0, 420, 120))

print()
print("row scan y=60 (ring80 centre) blue x-runs:")
xs = [x for x in range(0, 130) if near(px[x, 60], BLUE)]
runs = []
if xs:
    s = xs[0]
    for i in range(1, len(xs)):
        if xs[i] != xs[i - 1] + 1:
            runs.append((s, xs[i - 1]))
            s = xs[i]
    runs.append((s, xs[-1]))
print("  ", runs, " => outer:", runs[0][0], "..", runs[-1][1],
      "inner hole:", runs[0][1], "..", runs[1][0] if len(runs) > 1 else None,
      "=> inner width:", (runs[1][0] - runs[0][1]) if len(runs) > 1 else None)

print("row scan y=52 (ring64 centre) orange x-runs:")
xs = [x for x in range(125, 215) if near(px[x, 52], ORANGE)]
runs = []
if xs:
    s = xs[0]
    for i in range(1, len(xs)):
        if xs[i] != xs[i - 1] + 1:
            runs.append((s, xs[i - 1]))
            s = xs[i]
    runs.append((s, xs[-1]))
print("  ", runs, "=> outer:", runs[0][0], "..", runs[-1][1],
      "inner width:", (runs[1][0] - runs[0][1]) if len(runs) > 1 else None)

print("row scan y=44 (ring48 centre) green x-runs:")
xs = [x for x in range(215, 295) if near(px[x, 44], GREEN)]
runs = []
if xs:
    s = xs[0]
    for i in range(1, len(xs)):
        if xs[i] != xs[i - 1] + 1:
            runs.append((s, xs[i - 1]))
            s = xs[i]
    runs.append((s, xs[-1]))
print("  ", runs, "=> outer:", runs[0][0], "..", runs[-1][1],
      "inner width:", (runs[1][0] - runs[0][1]) if len(runs) > 1 else None)

print()
# shadow extent: any non-white pixel around the shadow box (130,130)-(230,230)
def dark(c):
    return min(c) < 250 and not near(c, BLUE) or near(c, (0, 0, 0))


def nonwhite(c):
    return not (c[0] > 250 and c[1] > 250 and c[2] > 250)


bb = bbox_of(lambda c: nonwhite(c), 105, 105, 265, 265)
print("shadow-box region non-white bbox (box is 130,130-230,230):", bb)
print("  => left margin:", 130 - bb[0], "top:", 130 - bb[1],
      "right:", bb[2] - 230, "bottom:", bb[3] - 230)

bb2 = bbox_of(lambda c: nonwhite(c), 250, 130, 395, 235)
print("text '7' region non-white bbox:", bb2)
