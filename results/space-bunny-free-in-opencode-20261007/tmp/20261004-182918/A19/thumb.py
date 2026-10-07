"""A19 readability thumbnails: confirm the delivered figures survive being scaled down
(a diagnostic grid must still be legible in a contact sheet / gallery thumbnail)."""
import os
import sys

from PIL import Image

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
OUT = os.path.join(ROOT, "outputs", RUN, "A19")
TMP = os.path.join(ROOT, "tmp", RUN, "A19", "thumbs")
os.makedirs(TMP, exist_ok=True)

for name, w in (("grid-scene", 800), ("occlusion", 400),
                ("occlusion-alternative", 400)):
    im = Image.open(os.path.join(OUT, name + ".png")).convert("RGB")
    h = int(im.height * w / im.width)
    p = os.path.join(TMP, "%s-%dpx.png" % (name, w))
    im.resize((w, h), Image.LANCZOS).save(p)
    print(p, (w, h))
