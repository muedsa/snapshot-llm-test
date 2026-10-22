#!/usr/bin/env python3
"""A05 geometry probe: verify shared x reference lines, marker y positions, zero line."""
import sys
from PIL import Image

png = sys.argv[1] if len(sys.argv) > 1 else "tmp/run-20261011-01/A05/drafts/sensor-report-v2.png"
im = Image.open(png).convert("RGB")
PX = lambda m: 150 + m * 1250 / 270


def near(p, c, tol):
    return all(abs(p[i] - c[i]) < tol for i in range(3))


def find_line(y, x0, x1, target=(27, 41, 66), tol=14):
    return [x for x in range(int(x0), int(x1)) if near(im.getpixel((x, y)), target, tol)]


for name, y in [("temp", 240), ("hum", 440), ("pre", 640)]:
    hits = find_line(y, int(PX(75)) - 8, int(PX(75)) + 8)
    print(name, "ref-line x near 09:15:", hits, "expected", round(PX(75), 1))

col = [y for y in range(620, 760) if near(im.getpixel((200, y)), (226, 232, 240), 30)]
print("pressure zero-line y at x=200:", col, "expected", round(756 - 53.6, 1))

cx = int(PX(60))
ys = [y for y in range(200, 360) if near(im.getpixel((cx, y)), (245, 158, 11), 40)]
print("temp 09:00 marker ys:", ys, "expected ~302")

cx = int(PX(130))
ys = [y for y in range(620, 756) if near(im.getpixel((cx, y)), (248, 113, 113), 40)]
print("pressure 10:10 marker ys:", ys, "expected ~745")

y = int(756 - (0.2 / 2.5) * 134)
xs = [x for x in range(560, 660) if near(im.getpixel((x, y)), (248, 113, 113), 40)]
print("09:40 marker xs:", xs, "expected", round(PX(100), 1))

cx = int(PX(250))
ys = [y for y in range(400, 560) if near(im.getpixel((cx, y)), (56, 189, 248), 40)]
print("humidity 12:10 marker ys:", ys, "expected", round(556 - (37 - 30) / 15 * 134, 1))

print("size", im.size)
