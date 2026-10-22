# -*- coding: utf-8 -*-
"""Crop per-card detail PNGs from a rendered wall using its layout JSON.

Usage: crop_cards.py <wall.png> <layout.json> <out_dir> <tag>
Writes <tag>-card-K01.png ... for every card (declared box +- 16px margin).
"""
import json
import pathlib
import sys

from PIL import Image

wall = Image.open(pathlib.Path(sys.argv[1]))
layout = json.loads(pathlib.Path(sys.argv[2]).read_text(encoding="utf-8"))
out = pathlib.Path(sys.argv[3])
tag = sys.argv[4]
out.mkdir(parents=True, exist_ok=True)

W, H = wall.size
for rec in layout["cards"]:
    x1, y1, x2, y2 = rec["declared_box"]
    pad = 16
    box = (max(0, x1 - pad), max(0, y1 - pad),
           min(W, x2 + pad), min(H, y2 + pad))
    wall.crop(box).save(out / f"{tag}-card-{rec['id']}.png")
print(f"cropped {len(layout['cards'])} cards -> {out}/{tag}-card-*.png")
