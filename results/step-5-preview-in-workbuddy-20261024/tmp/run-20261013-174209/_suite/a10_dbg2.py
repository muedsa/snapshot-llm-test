# -*- coding: utf-8 -*-
"""A10 probe: sample cells 1/2 and compute expected values."""
from PIL import Image

im = Image.open("tmp/run-20261013-174209/A10/base.png").convert("RGBA")
for name, ox, oy in [("E1", 208, 120), ("E2", 560, 120)]:
    p = im.getpixel((ox + 180, oy + 100))
    print(name, "sample(180,100) =", p)


def over(fg, fa, bg):
    return [f * fa + b * (1 - fa) for f, b in zip(fg, bg)]


def rnd(v):
    return int(v + 0.5)


a = 128 / 255
red = [255, 0, 0]
blue = [0, 0, 255]
white = [255, 255, 255]

r1 = over(red, a, white)
b1 = over(blue, a, r1)
print("E1 theoretical:", [rnd(v) for v in b1], "float:", [round(v, 4) for v in b1])

g_red = over(red, 1.0, white)
g_blue = over(blue, 1.0, g_red)
g2 = over(g_blue, 0.5, white)
print("E2 theoretical:", [rnd(v) for v in g2], "float:", [round(v, 4) for v in g2])
