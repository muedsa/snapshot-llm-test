"""Produce the required 400px-wide thumbnail for legibility checking (preview only)."""
import os
import sys

from PIL import Image

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
OUT = os.path.join(ROOT, "tmp", RUN, "A18", "thumbs")
os.makedirs(OUT, exist_ok=True)
src = sys.argv[1]
tag = sys.argv[2]
im = Image.open(src).convert("RGB")
w = int(sys.argv[3]) if len(sys.argv) > 3 else 400
h = int(round(im.height * w / im.width))
p = os.path.join(OUT, "%s-%dw.png" % (os.path.splitext(os.path.basename(src))[0], w))
im.resize((w, h), Image.LANCZOS).save(p)
print(p, (w, h))