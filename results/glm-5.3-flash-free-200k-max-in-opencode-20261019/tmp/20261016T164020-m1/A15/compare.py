# -*- coding: utf-8 -*-
"""A15 参考vs重建并排对比条（7 区域，ref 上 / mine 下），存 steps/compare-01.png。"""
import io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from PIL import Image, ImageDraw
REF = "tasks/A15-reference-reconstruction/inputs/reference.png"
MINE = "outputs/20261016T164020-m1/A15/reconstructed.png"
a = Image.open(REF).convert("RGB")
b = Image.open(MINE).convert("RGB")
zones = [("sidebar", (0, 0, 240, 900)), ("header", (240, 0, 1440, 115)),
         ("kpi", (250, 130, 1440, 290)), ("chart", (250, 300, 1010, 605)),
         ("activity", (1020, 300, 1410, 605)), ("table", (250, 615, 1410, 850)),
         ("footer", (250, 845, 900, 895))]
rows = []
for name, box in zones:
    ca, cb = a.crop(box), b.crop(box)
    rows.append((name, ca, cb))
gap, label_h = 8, 22
W2 = max(max(ca.width for _, ca, _ in rows), max(cb.width for _, _, cb in rows)) + gap * 2
H2 = sum(ca.height + cb.height + label_h + gap for name, ca, cb in rows) + gap
sheet = Image.new("RGB", (W2, H2), (18, 24, 42))
d = ImageDraw.Draw(sheet)
y = gap
for name, ca, cb in rows:
    d.text((gap, y + 3), f"[{name}] REF(top) vs MINE(bottom)", fill=(255, 220, 120))
    y += label_h
    sheet.paste(ca, (gap, y)); y += ca.height
    sheet.paste(cb, (gap, y)); y += cb.height + gap
sheet.save("tmp/20261016T164020-m1/A15/steps/compare-01.png")
print("compare-01", sheet.size)
