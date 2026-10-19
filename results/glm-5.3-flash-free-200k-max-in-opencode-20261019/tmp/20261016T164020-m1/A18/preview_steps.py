# -*- coding: utf-8 -*-
from PIL import Image
for s, k in (("alpha", 1), ("beta", 1)):
    p = f"tmp/20261016T164020-m1/A18/steps/preview-{s}.png"
    im = Image.open(p)
    w, h = im.size
    im.resize((int(w * 0.625), int(h * 0.625)), Image.LANCZOS).save(
        f"tmp/20261016T164020-m1/A18/steps/preview-{s}-1000.png")
print("ok", w, h)
