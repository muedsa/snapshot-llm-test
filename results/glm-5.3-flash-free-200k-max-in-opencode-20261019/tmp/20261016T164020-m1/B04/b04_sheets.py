# -*- coding: utf-8 -*-
"""B04 看图接触表。"""
from pathlib import Path
from PIL import Image
import os, sys

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "..\\..\\..")).resolve()
RUN = os.environ.get("SNAPSHOT_RUN_ID", "20261016T164020-m1")
OUT = ROOT / "outputs" / RUN / "B04"
STEPS = ROOT / "tmp" / RUN / "B04" / "steps"
STEPS.mkdir(parents=True, exist_ok=True)

CELL_H = 1250
PAD = 30

pairs = [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10)]
for si, (a, b) in enumerate(pairs, start=1):
    imgs = []
    for n in (a, b):
        p = OUT / f"case-{n:02d}" / "final.png"
        im = Image.open(p).convert("RGB")
        k = CELL_H / im.height
        tw = max(1, int(im.width * k))
        imgs.append(im.resize((tw, CELL_H), Image.LANCZOS))
    W = sum(i.width for i in imgs) + PAD * 3
    sheet = Image.new("RGB", (W, CELL_H + PAD * 2), "#333333")
    x = PAD
    for im in imgs:
        sheet.paste(im, (x, PAD))
        x += im.width + PAD
    q = STEPS / f"sheet-{si}.png"
    sheet.save(q)
    print(q, sheet.size)
