# -*- coding: utf-8 -*-
import io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from PIL import Image
OUT = "outputs/20261016T164020-m1/A11"
STEPS = "tmp/20261016T164020-m1/A11/steps"
p1 = Image.open(os.path.join(OUT, "invoice-page-01.png"))
p2 = Image.open(os.path.join(OUT, "invoice-page-02.png"))
def cr(im, box, name, k):
    c = im.crop(box)
    c = c.resize((int(c.width * k), int(c.height * k)), Image.NEAREST)
    c.save(os.path.join(STEPS, name + ".png"))
cr(p1, (40, 460, 1170, 950), "v5_p1_sku24", 1.35)  # 全部四行（SKU 24px 后）
cr(p2, (40, 1180, 1170, 1400), "v5_p2_checks", 1.35)
cr(p1, (40, 40, 1170, 200), "v5_p1_head", 1.35)    # 页1 页眉（v04 边距后未再看）
print("ok")
