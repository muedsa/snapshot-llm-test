# -*- coding: utf-8 -*-
"""A15 v04 终检视觉件：compare-02（7 区域 ref/mine 对照）+ 4 个 2x 放大对照对。"""
import io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from PIL import Image, ImageDraw
REF = "tasks/A15-reference-reconstruction/inputs/reference.png"
MINE = "outputs/20261016T164020-m1/A15/reconstructed.png"
STEPS = "tmp/20261016T164020-m1/A15/steps"
a = Image.open(REF).convert("RGB")
b = Image.open(MINE).convert("RGB")
zones = [("sidebar", (0, 0, 240, 900)), ("header", (240, 0, 1440, 115)),
         ("kpi", (250, 130, 1440, 290)), ("chart", (250, 300, 1010, 605)),
         ("activity", (1020, 300, 1410, 605)), ("table", (250, 615, 1410, 850)),
         ("footer", (250, 845, 900, 895))]
rows = []
for name, box in zones:
    rows.append((name, a.crop(box), b.crop(box)))
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
sheet.save(os.path.join(STEPS, "compare-02.png"))
for nm, box, k in (("nav", (10, 100, 220, 360), 1.6),
                   ("panel", (10, 740, 220, 885), 1.6),
                   ("thead", (270, 675, 760, 760), 2.0),
                   ("chartaxis", (280, 320, 620, 600), 1.4)):
    ca, cb = a.crop(box), b.crop(box)
    w3, h3 = int(ca.width * k), int(ca.height * k)
    ca = ca.resize((w3, h3), Image.LANCZOS); cb = cb.resize((w3, h3), Image.LANCZOS)
    im = Image.new("RGB", (w3 * 2 + 12, h3), (18, 24, 42))
    im.paste(ca, (0, 0)); im.paste(cb, (w3 + 12, 0))
    im.save(os.path.join(STEPS, f"zoomv4_{nm}.png"))
print("ok", sheet.size)
