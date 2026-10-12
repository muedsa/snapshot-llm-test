"""A15 · build the viewing aids: a thumbnail, a side-by-side sheet and four local zooms.

These live in the temp directory only - they are how the reconstruction gets inspected
at thumbnail size and at 2x in local regions. The deliverable stays the single
service-rendered PNG.
"""
from __future__ import annotations

import os
import sys

from PIL import Image, ImageDraw

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
TMP = os.path.join(ROOT, "tmp", "20261003-114508-flashmax", "A15")
REF = os.path.join(ROOT, "tasks", "A15-reference-reconstruction", "inputs", "reference.png")
NEW = sys.argv[1] if len(sys.argv) > 1 else os.path.join(TMP, "png", "reconstructed.v2.png")
TAG = sys.argv[2] if len(sys.argv) > 2 else "v2"
OUT = os.path.join(TMP, "review")
os.makedirs(OUT, exist_ok=True)

ref = Image.open(REF).convert("RGB")
new = Image.open(NEW).convert("RGB")

# ---------------------------------------------------------------- thumbnail
th = new.resize((360, 225), Image.LANCZOS)
th.save(os.path.join(OUT, f"reconstructed.{TAG}.thumb-360x225.png"))

# ---------------------------------------------------------------- side by side
sheet = Image.new("RGB", (1440 + 24, 900 + 900 + 60), (255, 255, 255))
dr = ImageDraw.Draw(sheet)
dr.rectangle([0, 0, sheet.width, 28], fill=(15, 23, 42))
dr.text((12, 8), "A15 side-by-side: reference (top) / reconstruction (bottom), 1:1",
        fill=(248, 250, 252))
sheet.paste(ref, (12, 40))
sheet.paste(new, (12, 40 + 900 + 12))
sheet.save(os.path.join(OUT, f"side-by-side.{TAG}.png"))

# ---------------------------------------------------------------- local zooms
ZOOMS = {
    "sidebar-header": (0, 0, 520, 200),
    "kpi-row": (250, 130, 1010, 290),
    "chart": (260, 300, 1010, 600),
    "table-status": (260, 620, 1410, 850),
    "activity": (1020, 300, 1410, 600),
}
for name, box in ZOOMS.items():
    w, h = box[2] - box[0], box[3] - box[1]
    scale = 2 if w <= 760 else 1.4
    cw, ch = int(w * scale), int(h * scale)
    c = Image.new("RGB", (cw, ch * 2 + 46), (255, 255, 255))
    d2 = ImageDraw.Draw(c)
    d2.rectangle([0, 0, cw, 22], fill=(15, 23, 42))
    d2.text((8, 6), f"{name}  x{scale}  top=reference  bottom=reconstruction",
            fill=(248, 250, 252))
    c.paste(ref.crop(box).resize((cw, ch), Image.NEAREST), (0, 22))
    c.paste(new.crop(box).resize((cw, ch), Image.NEAREST), (0, 22 + ch + 24))
    c.save(os.path.join(OUT, f"zoom-{name}.{TAG}.png"))
    print("zoom", name, c.size)
print("thumbnail + side-by-side + zooms written to", OUT)
