# -*- coding: utf-8 -*-
"""Diff exp2/exp3/exp5 against exp1 (identical scene, no filter) -> exact
region touched by BackdropFilter."""
import pathlib
from PIL import Image, ImageChops

EXP = pathlib.Path("tmp/run-20261011-01/A17/experiments")
base = Image.open(EXP / "exp1.png").convert("RGB")

for name in ("exp2", "exp3", "exp4", "exp5"):
    other = Image.open(EXP / f"{name}.png").convert("RGB")
    diff = ImageChops.difference(base, other)
    bbox = diff.getbbox()
    print(f"{name}: diff bbox = {bbox}")
    if bbox:
        # sample some diff values
        px = diff.load()
        x0, y0, x1, y1 = bbox
        samples = []
        for y in (y0, (y0 + y1) // 2, y1 - 1):
            for x in (x0, (x0 + x1) // 2, x1 - 1):
                samples.append((x, y, px[x, y]))
        print("   samples:", samples[:9])

# Also locate T2 text extent in exp1 vs exp2 (R channel) at y=244
b1 = base.load()
im2 = Image.open(EXP / "exp2.png").convert("RGB")
p2 = im2.load()
print("\nR values along y=244 exp1 vs exp2 (every 20px):")
for x in range(0, 400, 20):
    print(f"  x={x}: exp1={b1[x, 244]} exp2={p2[x, 244]}")
print("\nR values along y=24 exp1 vs exp2 (every 20px):")
for x in range(0, 400, 20):
    print(f"  x={x}: exp1={b1[x, 24]} exp2={p2[x, 24]}")
print("\ncolumn x=350, exp1 vs exp2 (every 20px):")
for y in range(0, 300, 20):
    print(f"  y={y}: exp1={b1[350, y]} exp2={p2[350, y]}")
