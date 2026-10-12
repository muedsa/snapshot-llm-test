# -*- coding: utf-8 -*-
"""Debug: dump the colour mask clusters that pollute the geometry verification."""
import sys

from PIL import Image

p = r'D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004\tmp\20261004-182918\A09\preview\transform-atlas.png'
im = Image.open(p).convert("RGB")
px = im.load()


def near(c, t, d=60):
    return ((c[0] - t[0]) ** 2 + (c[1] - t[1]) ** 2 + (c[2] - t[2]) ** 2) ** 0.5 <= d


target = (0xE5, 0x4B, 0x4B)
pts = []
for y in range(490 - 30, 740 + 30):
    for x in range(152 - 30, 452 + 30):
        if near(px[x, y], target):
            pts.append((x, y))
print("red-ish pixels in T05 window:", len(pts))
xs = [p[0] for p in pts]
ys = [p[1] for p in pts]
print("bbox", min(xs), min(ys), max(xs), max(ys))
# histogram by 10px rows
from collections import Counter
c = Counter(y // 10 * 10 for x, y in pts)
for k in sorted(c):
    print("row band", k, c[k])
print("sample colours near the top-left:")
seen = {}
for x, y in pts:
    if y < 600 and x < 310:
        seen[px[x, y]] = seen.get(px[x, y], 0) + 1
for col, n in sorted(seen.items(), key=lambda kv: -kv[1])[:12]:
    print("   ", col, n, "dist", round(sum((col[i] - target[i]) ** 2 for i in range(3)) ** 0.5, 1))