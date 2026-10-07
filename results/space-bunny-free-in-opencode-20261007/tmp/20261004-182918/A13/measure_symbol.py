# -*- coding: utf-8 -*-
"""A13: measure the rendered symbol - find alpha dips (box seams), the ink bbox,
the void bbox, and whether colour and mono masks are identical."""
import os
import sys

from PIL import Image

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import state as S  # noqa: E402
import layerlight as L  # noqa: E402

mark = L.build_mark(plate=300, radius=60, offset=150, origin=6)
CLEAR = 512.0 / 9.0
ox, oy, k = L.fitted(mark, 256, 256, 512 - 2 * CLEAR)
print("ink", L.ink_box(mark, ox, oy, k))


def analyse(path, label):
    im = Image.open(path).convert("RGBA")
    a = im.split()[3]
    w, h = im.size
    # ink bbox (alpha > 8)
    mask = a.point(lambda v: 255 if v > 8 else 0)
    bb = mask.getbbox()
    print("%-12s size=%s ink_bbox=%s" % (label, im.size, bb))
    # the void: alpha==0 pixels inside the ink bbox, largest empty square run
    px = im.load()
    # scanline through the middle of the mark horizontally
    ymid = int(bb[1] + (bb[3] - bb[1]) / 2)
    row = [a.getpixel((x, ymid)) for x in range(bb[0], bb[2])]
    dips = [(bb[0] + i, v) for i, v in enumerate(row) if 0 < v < 250]
    print("   alpha dips on row y=%d: %s" % (ymid, dips[:24]))
    # scanline through the top leg (to expose the vertical seam)
    yleg = int(oy + 40 * k)
    row2 = [a.getpixel((x, yleg)) for x in range(bb[0], bb[2])]
    dips2 = [(bb[0] + i, v) for i, v in enumerate(row2) if 0 < v < 250]
    print("   alpha dips on row y=%d: %s" % (yleg, dips2[:24]))
    # scanline through the bottom leg (exposes the cyan leg junction at x = o3)
    ybot = 400
    row3 = [(x, a.getpixel((x, ybot))) for x in range(bb[0], bb[2])]
    dips4 = [(x, v) for x, v in row3 if 0 < v < 250]
    print("   alpha dips on row y=%d: %s" % (ybot, dips4[:24]))
    # vertical scanline through the middle
    xmid = int(bb[0] + (bb[2] - bb[0]) / 2)
    col = [a.getpixel((xmid, y)) for y in range(bb[1], bb[3])]
    dips3 = [(bb[1] + i, v) for i, v in enumerate(col) if 0 < v < 250]
    print("   alpha dips on col x=%d: %s" % (xmid, dips3[:24]))
    # void extent on the middle row
    zero_runs = []
    start = None
    for i, v in enumerate(row):
        if v == 0 and start is None:
            start = i
        elif v != 0 and start is not None:
            zero_runs.append((bb[0] + start, bb[0] + i - 1))
            start = None
    if start is not None:
        zero_runs.append((bb[0] + start, bb[0] + len(row) - 1))
    print("   transparent runs on the middle row: %s" % zero_runs)
    # distinct colours
    cols = {}
    for y in range(0, h, 3):
        for x in range(0, w, 3):
            r, g, b, al = px[x, y]
            if al > 250:
                cols[(r, g, b)] = cols.get((r, g, b), 0) + 1
    top = sorted(cols.items(), key=lambda t: -t[1])[:6]
    print("   top opaque colours:", top)
    return im, a


base = sys.argv[1]
imc, ac = analyse(os.path.join(base, "symbol-color.png"), "colour")
imb, ab = analyse(os.path.join(base, "symbol-black.png"), "mono")
diff = 0
maxdiff = 0
for y in range(512):
    for x in range(512):
        av, bv = ac.getpixel((x, y)), ab.getpixel((x, y))
        if av != bv:
            diff += 1
            maxdiff = max(maxdiff, abs(av - bv))
print("alpha channel differing pixels colour vs mono: %d (max delta %d)" % (diff, maxdiff))
pxb = imb.load()
bad = sum(1 for y in range(512) for x in range(512)
          if pxb[x, y][3] > 0 and (pxb[x, y][0] or pxb[x, y][1] or pxb[x, y][2]))
print("mono pixels with alpha>0 and non-zero RGB:", bad)