# -*- coding: utf-8 -*-
"""Compare v1 (leaky) vs v2 (paint-order fixed) page renders.

Pages 1-3 must stay pixel-identical (their cores contain no BackdropFilter;
only emission order changed).  Page 4 must differ exactly in the region that
used to be blurred by the BackdropFilter leak, and its preamble text must be
sharp again (gradient energy check).
"""
import pathlib

from PIL import Image, ImageFilter

GEN = pathlib.Path(__file__).resolve().parents[1] / "gen"


def load(name):
    return Image.open(GEN / name).convert("RGB")


def diff_stats(a, b):
    pa, pb = a.load(), b.load()
    w, h = a.size
    n = 0
    minx, miny, maxx, maxy = w, h, -1, -1
    for y in range(h):
        for x in range(w):
            ra, ga, ba = pa[x, y]
            rb, gb, bb = pb[x, y]
            if abs(ra - rb) + abs(ga - gb) + abs(ba - bb) > 12:
                n += 1
                if x < minx:
                    minx = x
                if x > maxx:
                    maxx = x
                if y < miny:
                    miny = y
                if y > maxy:
                    maxy = y
    return n, (minx, miny, maxx, maxy) if n else None


def sharpness(img, box):
    """Mean gradient magnitude inside box -- high = crisp text/edges."""
    crop = img.crop(box).convert("L")
    edge = crop.filter(ImageFilter.FIND_EDGES)
    data = list(edge.getdata())
    return sum(data) / len(data)


REGIONS = {
    "title": (48, 96, 1104, 176),
    "intro": (48, 168, 1104, 300),
    "rightcol": (540, 320, 1152, 640),
    "frame_border": (48, 326, 508, 684),
}


def main():
    for n in (1, 2, 3, 4):
        old = load(f"handbook-{n:02d}.png")
        new = load(f"handbook-{n:02d}-v2.png")
        count, bbox = diff_stats(old, new)
        print(f"handbook-{n:02d}: changed px = {count}, bbox = {bbox}")
        if n == 4:
            for label, box in REGIONS.items():
                so = sharpness(old, box)
                sn = sharpness(new, box)
                print(f"  sharpness {label}: v1 {so:.2f} -> v2 {sn:.2f}")


if __name__ == "__main__":
    main()
