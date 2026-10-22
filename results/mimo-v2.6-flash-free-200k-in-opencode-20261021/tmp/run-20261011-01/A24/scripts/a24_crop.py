# -*- coding: utf-8 -*-
"""Crop/zoom regions of A24 renders for close visual inspection.

Usage: python a24_crop.py <png_in> <x> <y> <w> <h> <scale> <png_out>
"""
import sys
from PIL import Image


def main():
    src, x, y, w, h, scale, dst = (sys.argv[1], int(sys.argv[2]), int(sys.argv[3]),
                                   int(sys.argv[4]), int(sys.argv[5]),
                                   float(sys.argv[6]), sys.argv[7])
    im = Image.open(src).convert("RGB")
    box = im.crop((x, y, x + w, y + h))
    nw, nh = int(w * scale), int(h * scale)
    box = box.resize((nw, nh), Image.LANCZOS)
    box.save(dst)
    print("cropped %s (%d,%d,%d,%d) x%g -> %s (%dx%d)"
          % (src, x, y, w, h, scale, dst, nw, nh))


if __name__ == "__main__":
    main()
