# -*- coding: utf-8 -*-
"""A10 probe: scan cell 3 card interior for blur evidence."""
from PIL import Image

im = Image.open("tmp/run-20261013-174209/A10/base.png").convert("RGB")
# 实验3 origin (912,120); card local (40,40) 240x160 -> canvas (952,160)-(1192,320)
print("cell3 card row y=240 (x transitions):")
prev = None
for x in range(952, 1193):
    p = im.getpixel((x, 240))
    if p != prev:
        print("  x", x, p)
        prev = p
print()
print("cell3 card row y=200:")
prev = None
for x in range(952, 1193):
    p = im.getpixel((x, 200))
    if p != prev:
        print("  x", x, p)
        prev = p
print()
# 对照：实验4 origin (208,392); card local (40,40) -> canvas (248,432)-(488,592)
print("cell4 card row y=512:")
prev = None
for x in range(248, 489):
    p = im.getpixel((x, 512))
    if p != prev:
        print("  x", x, p)
        prev = p
