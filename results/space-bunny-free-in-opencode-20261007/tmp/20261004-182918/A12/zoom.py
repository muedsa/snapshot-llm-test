"""A12 helper: crop/zoom a region of a delivered PNG for close visual inspection.

Usage: python zoom.py <png> <tag> <x,y,w,h> [scale]
"""
import os
import sys

from PIL import Image

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
OUTDIR = os.path.join(ROOT, "tmp", "20261004-182918", "A12", "crops")
os.makedirs(OUTDIR, exist_ok=True)

src, tag, box = sys.argv[1], sys.argv[2], sys.argv[3]
scale = float(sys.argv[4]) if len(sys.argv) > 4 else 3.0
x, y, w, h = (int(v) for v in box.split(","))
im = Image.open(src).convert("RGB")
sub = im.crop((x, y, x + w, y + h))
sub = sub.resize((int(sub.width * scale), int(sub.height * scale)), Image.LANCZOS)
p = os.path.join(OUTDIR, "%s.png" % tag)
sub.save(p)
print(p, sub.size)
