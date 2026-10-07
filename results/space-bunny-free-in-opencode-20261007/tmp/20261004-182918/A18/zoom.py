"""Zoom crops for A18 visual verification (avoids shell arg quoting issues)."""
import os
import sys

from PIL import Image

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
OUT = os.path.join(ROOT, "tmp", RUN, "A18", "crops")


def main():
    src = sys.argv[1]
    tag = sys.argv[2]
    jobs = []
    for spec in sys.argv[3:]:
        x, y, w, h, sc = spec.split(":")
        jobs.append((int(x), int(y), int(w), int(h), float(sc)))
    os.makedirs(OUT, exist_ok=True)
    im = Image.open(src).convert("RGB")
    for (x, y, w, h, sc) in jobs:
        sub = im.crop((x, y, x + w, y + h))
        if sc != 1.0:
            sub = sub.resize((int(sub.width * sc), int(sub.height * sc)), Image.LANCZOS)
        p = os.path.join(OUT, "%s-%s.png" % (os.path.splitext(os.path.basename(src))[0], tag))
        sub.save(p)
        print(p, sub.size)


if __name__ == "__main__":
    main()