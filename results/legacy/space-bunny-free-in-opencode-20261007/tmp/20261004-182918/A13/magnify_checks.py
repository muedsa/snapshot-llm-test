# -*- coding: utf-8 -*-
"""A13 inspection tool: magnify the service-rendered 32x32/64x64 checks so they
can actually be looked at, and cross-check the PIL downscale of the 512 symbol.
Everything written here is a check preview and lives in the temp dir."""
import os
import sys

from PIL import Image

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import state as S  # noqa: E402

TMP = os.path.join(S.TMP_ROOT, "A13")
tag = sys.argv[1]
src_dir = os.path.join(TMP, "preview", tag)
out_dir = os.path.join(TMP, "preview", tag, "magnified")
os.makedirs(out_dir, exist_ok=True)

SHEET_BG = (255, 255, 255)


def checker(n, sq=1):
    """A faint chequer so transparency is visible when magnified."""
    im = Image.new("RGB", (n * sq, n * sq), SHEET_BG)
    px = im.load()
    for y in range(n * sq):
        for x in range(n * sq):
            if ((x // sq) + (y // sq)) % 2 == 0:
                px[x, y] = (233, 236, 243)
    return im


def magnify(path, scale, tagname):
    im = Image.open(path).convert("RGBA")
    n = im.size[0]
    base = checker(n)
    base.paste(im, (0, 0), im)
    big = base.resize((n * scale, n * scale), Image.NEAREST)
    out = os.path.join(out_dir, "%s-%s.png" % (tagname, os.path.basename(path)[:-4]))
    big.save(out)
    print(out, big.size)


for nm, sc in (("checksize/check-color-32x32.png", 12),
               ("checksize/check-black-32x32.png", 12),
               ("checksize/check-color-64x64.png", 7),
               ("checksize/check-black-64x64.png", 7)):
    p = os.path.join(src_dir, nm)
    if os.path.exists(p):
        magnify(p, sc, "svc")

# cross-check: PIL downscale of the delivered 512 render, then magnified
for nm, sc in (("symbol-color.png", 12), ("symbol-black.png", 12)):
    p = os.path.join(src_dir, nm)
    if not os.path.exists(p):
        continue
    im = Image.open(p).convert("RGBA")
    small = im.resize((32, 32), Image.LANCZOS)
    base = checker(32)
    base.paste(small, (0, 0), small)
    out = os.path.join(out_dir, "pil32-%s.png" % os.path.basename(p)[:-4])
    base.resize((32 * sc, 32 * sc), Image.NEAREST).save(out)
    print(out)
    # and a 64px resample for the mid-size range
    small64 = im.resize((64, 64), Image.LANCZOS)
    base64 = checker(64)
    base64.paste(small64, (0, 0), small64)
    out64 = os.path.join(out_dir, "pil64-%s.png" % os.path.basename(p)[:-4])
    base64.resize((64 * 6, 64 * 6), Image.NEAREST).save(out64)
    print(out64)