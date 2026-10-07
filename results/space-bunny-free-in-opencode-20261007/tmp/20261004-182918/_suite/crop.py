"""Crop / zoom a rendered PNG into the task temp dir for close visual inspection."""
import os
import sys

from PIL import Image

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"


def main():
    src = sys.argv[1]
    task = sys.argv[2]
    box = tuple(int(v) for v in sys.argv[3].split(","))
    scale = float(sys.argv[4]) if len(sys.argv) > 4 else 2.0
    tag = sys.argv[5] if len(sys.argv) > 5 else "crop"
    outdir = os.path.join(ROOT, "tmp", RUN, task, "crops")
    os.makedirs(outdir, exist_ok=True)
    im = Image.open(src).convert("RGB")
    sub = im.crop(box)
    if scale != 1.0:
        sub = sub.resize((int(sub.width * scale), int(sub.height * scale)), Image.LANCZOS)
    out = os.path.join(outdir, "%s-%s.png" % (os.path.splitext(os.path.basename(src))[0], tag))
    sub.save(out)
    print(out, sub.size)


if __name__ == "__main__":
    main()