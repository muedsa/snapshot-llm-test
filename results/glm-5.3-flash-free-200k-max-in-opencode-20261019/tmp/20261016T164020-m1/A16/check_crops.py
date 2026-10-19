# -*- coding: utf-8 -*-
"""A16 终检裁剪：图表上层/柱区/明细卡/关注卡。"""
import io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from PIL import Image
STEPS = "tmp/20261016T164020-m1/A16/steps"
im = Image.open("outputs/20261016T164020-m1/A16/corrected-report.png").convert("RGB")
for nm, box, k in [("top", (56, 140, 780, 320), 1.6), ("bars34", (660, 240, 1240, 520), 1.6),
                   ("detail", (56, 616, 790, 850), 1.6), ("focus", (810, 616, 1240, 850), 2.0)]:
    c = im.crop(box)
    c = c.resize((int(c.width * k), int(c.height * k)), Image.LANCZOS)
    c.save(os.path.join(STEPS, f"chk-{nm}.png"))
print("ok")
