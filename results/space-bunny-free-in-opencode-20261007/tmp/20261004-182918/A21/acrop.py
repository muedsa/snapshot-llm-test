# -*- coding: utf-8 -*-
"""A21 local crop helper: python acrop.py <png> <x,y,w,h> <scale> <tag>"""
import os
import sys

from PIL import Image

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
OUTDIR = os.path.join(ROOT, "tmp", "20261004-182918", "A21", "crops")
os.makedirs(OUTDIR, exist_ok=True)
src = sys.argv[1]
x, y, w, h = [int(v) for v in sys.argv[2].split(",")]
scale = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
tag = sys.argv[4] if len(sys.argv) > 4 else "crop"
im = Image.open(src).convert("RGB")
sub = im.crop((x, y, x + w, y + h))
if scale != 1.0:
    sub = sub.resize((int(sub.width * scale), int(sub.height * scale)), Image.LANCZOS)
out = os.path.join(OUTDIR, "%s-%s.png" % (os.path.splitext(os.path.basename(src))[0], tag))
sub.save(out)
print(out, sub.size)