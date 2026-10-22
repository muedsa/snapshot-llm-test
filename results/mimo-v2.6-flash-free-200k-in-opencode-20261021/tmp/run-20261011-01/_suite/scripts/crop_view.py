#!/usr/bin/env python3
"""Crop a PNG region for close visual inspection.

Usage: python crop_view.py <src.png> <out.png> <l> <t> <r> <b> [scale]
"""
import sys
from PIL import Image

src, dst = sys.argv[1], sys.argv[2]
l, t, r, b = (int(x) for x in sys.argv[3:7])
scale = float(sys.argv[7]) if len(sys.argv) > 7 else 1.0
im = Image.open(src).convert("RGB").crop((l, t, r, b))
if scale != 1.0:
    im = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
im.save(dst)
print(dst, im.size)
