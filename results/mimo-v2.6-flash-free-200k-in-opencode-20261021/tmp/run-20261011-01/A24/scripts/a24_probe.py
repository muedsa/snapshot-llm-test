# -*- coding: utf-8 -*-
"""Pixel probe: list color runs on scanlines of A24 renders (locate objects)."""
import sys
from PIL import Image


def runs(im, y, x0, x1):
    out, prev, start = [], None, x0
    for x in range(x0, x1):
        c = im.getpixel((x, y))
        if c != prev:
            if prev is not None and x - start >= 2:
                out.append((start, x - 1, prev))
            prev, start = c, x
    out.append((start, x1 - 1, prev))
    return out


def main():
    src = sys.argv[1]
    im = Image.open(src).convert("RGB")
    for spec in sys.argv[2:]:
        y, x0, x1 = (int(v) for v in spec.split(","))
        print("scan y=%d x=%d..%d" % (y, x0, x1))
        for a, b, c in runs(im, y, x0, x1):
            print("   %4d..%4d  #%02X%02X%02X" % (a, b, c[0], c[1], c[2]))


if __name__ == "__main__":
    main()
