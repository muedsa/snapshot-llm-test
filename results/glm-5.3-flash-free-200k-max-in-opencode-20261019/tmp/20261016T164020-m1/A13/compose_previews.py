# -*- coding: utf-8 -*-
import io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from PIL import Image
TMP = "tmp/20261016T164020-m1/A13"
os.makedirs(TMP + "/steps", exist_ok=True)
for n in ("dir-a", "dir-b"):
    im = Image.open(os.path.join(TMP, n + ".png"))
    bg = Image.new("RGB", im.size, (244, 249, 255))
    bg.paste(im, (0, 0), im)
    bg.save(os.path.join(TMP, "steps", n + "_on_paper.png"))
    print(n, im.size, im.mode)
