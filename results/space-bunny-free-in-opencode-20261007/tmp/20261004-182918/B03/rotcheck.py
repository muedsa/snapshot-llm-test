"""Review helper: crop a region and rotate it so rotated DSL labels become readable."""
import os
import sys

from PIL import Image

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"

src, task, box, scale, tag = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]), sys.argv[5]
deg = int(sys.argv[6]) if len(sys.argv) > 6 else 270
outdir = os.path.join(ROOT, "tmp", RUN, task, "crops")
os.makedirs(outdir, exist_ok=True)
im = Image.open(src).convert("RGB").crop(tuple(int(v) for v in box.split(",")))
if deg:
    im = im.transpose(Image.ROTATE_270 if deg == 270 else Image.ROTATE_90)
if scale != 1.0:
    im = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
out = os.path.join(outdir, "%s-%s.png" % (os.path.splitext(os.path.basename(src))[0], tag))
im.save(out)
print(out, im.size)
