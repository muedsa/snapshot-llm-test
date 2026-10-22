# -*- coding: utf-8 -*-
"""Inspect F3: where is the red LED (U05)? What does the DSL say?"""
import re
from PIL import Image

P = "tmp/run-20261011-01/A23/frames/frame-03b.png"
im = Image.open(P).convert("RGBA")
px = im.load()
red = [(x, y) for y in range(600) for x in range(600)
       if px[x, y][3] > 200 and abs(px[x, y][0] - 239) < 12
       and abs(px[x, y][1] - 68) < 12 and abs(px[x, y][2] - 68) < 12]
print("red pixels:", len(red), red[:5])
print("at (143,258):", px[143, 258], "| at (135,250):", px[135, 250])
seen = {}
for y in range(235, 285):
    for x in range(115, 175):
        p = px[x, y]
        if p[3] > 200:
            seen[p[:3]] = seen.get(p[:3], 0) + 1
print("colors near U05 F3 spot:",
      sorted(seen.items(), key=lambda kv: -kv[1])[:8])

t = open("tmp/run-20261011-01/A23/frames/frame-03.snapshot",
         encoding="utf-8").read()
for m in re.finditer(r'<Positioned left="([^"]+)" top="([^"]+)"'
                     r' width="18" height="18">(.{0,60})', t):
    print("F3 U05 elem: left=%s top=%s %s" % (m.group(1), m.group(2),
                                              m.group(3)[:60]))
