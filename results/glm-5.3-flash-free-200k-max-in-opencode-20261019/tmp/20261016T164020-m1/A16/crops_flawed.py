# -*- coding: utf-8 -*-
"""A16 证据裁剪：图例/明细卡/标题副标/关注卡 三倍放大 + 关键色采样。"""
import io, sys, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from PIL import Image
STEPS = "tmp/20261016T164020-m1/A16/steps"
im = Image.open("tasks/A16-visual-data-forensics/inputs/flawed-report.png").convert("RGB")
px = im.load()
print("focus_card_sample", "#%02X%02X%02X" % px[1000, 700], "#%02X%02X%02X" % px[1100, 760])
print("legend_zone", "#%02X%02X%02X" % px[940, 298], "#%02X%02X%02X" % px[960, 298], "#%02X%02X%02X" % px[1040, 298], "#%02X%02X%02X" % px[1060, 298])
print("detail_num_row", "#%02X%02X%02X" % px[110, 770])
for nm, box in [("legend", (700, 175, 1270, 450)), ("head", (40, 30, 900, 130)),
                ("detail", (56, 640, 830, 830)), ("focus", (840, 640, 1270, 850)),
                ("foot", (40, 845, 400, 885)), ("qtr", (200, 570, 700, 650))]:
    c = im.crop(box)
    c = c.resize((c.width * 3, c.height * 3), Image.LANCZOS)
    c.save(os.path.join(STEPS, f"flaw-{nm}.png"))
print("crops ok")
