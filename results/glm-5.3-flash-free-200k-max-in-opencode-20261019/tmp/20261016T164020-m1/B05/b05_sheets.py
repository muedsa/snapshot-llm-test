# -*- coding: utf-8 -*-
"""B05 接触表：每张两屏成对拼图，输出 tmp/<run>/B05/steps/sheet-N.png。"""
import os
from pathlib import Path
from PIL import Image

TASK_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ.get("SNAPSHOT_RUN_ID", "20261016T164020-m1")
OUT = TASK_ROOT / "outputs" / RUN / "B05"
STEPS = TASK_ROOT / "tmp" / RUN / "B05" / "steps"
STEPS.mkdir(exist_ok=True)

pairs = [[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]]
SCALE = 0.55
PAD = 16
CAP = 30

from PIL import ImageDraw  # noqa: E402

for pi, pr in enumerate(pairs, start=1):
    imgs = []
    for k in pr:
        p = OUT / ("case-%02d" % k) / "final.png"
        im = Image.open(p)
        tw = int(im.width * SCALE)
        th = int(im.height * SCALE)
        imgs.append((im.resize((tw, th), Image.LANCZOS), k))
    W = sum(im.width for im, _k in imgs) + PAD * (len(imgs) + 1)
    H = max(im.height for im, _k in imgs) + PAD * 2 + CAP
    sheet = Image.new("RGB", (W, H), "#E7E2D5")
    d = ImageDraw.Draw(sheet)
    x = PAD
    for im, k in imgs:
        sheet.paste(im, (x, PAD + CAP))
        d.text((x, 8), "case-%02d" % k, fill="#333")
        x += im.width + PAD
    out = STEPS / ("sheet-%d.png" % pi)
    sheet.save(out)
    print(out, sheet.size)
