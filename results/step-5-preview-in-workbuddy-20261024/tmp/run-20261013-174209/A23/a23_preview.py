#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A23 · 生成可查看的合成预览（透明 PNG 叠到浅灰底 + 棋盘格）与分区放大图。"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = "run-20261013-174209"
OUT = ROOT / "outputs" / RUN_ID / "A23"
TMP = ROOT / "tmp" / RUN_ID / "A23"
PREV = TMP / "preview"
PREV.mkdir(parents=True, exist_ok=True)


def composite(arr, bg=(244, 246, 251), checker=False):
    h, w = arr.shape[:2]
    if checker:
        base = np.zeros((h, w, 3), dtype=np.uint8)
        s = 16
        for y in range(0, h, s):
            for x in range(0, w, s):
                c = 226 if ((x // s) + (y // s)) % 2 == 0 else 246
                base[y:y + s, x:x + s] = (c, c, c)
    else:
        base = np.zeros((h, w, 3), dtype=np.uint8)
        base[:, :] = bg
    a = arr[:, :, 3:4].astype(float) / 255.0
    rgb = arr[:, :, :3].astype(float)
    out = rgb * a + base.astype(float) * (1 - a)
    return Image.fromarray(out.astype(np.uint8))


def zoom(arr, box, scale=2):
    x0, y0, x1, y1 = box
    crop = arr[y0:y1, x0:x1]
    im = composite(crop)
    return im.resize((im.width * scale, im.height * scale), Image.NEAREST)


def main():
    names = [f"frame-{k:02d}" for k in range(1, 7)] + ["cover"]
    for n in names:
        arr = np.asarray(Image.open(OUT / f"{n}.png").convert("RGBA"))
        composite(arr).save(PREV / f"{n}-flat.png")
        composite(arr, checker=True).save(PREV / f"{n}-checker.png")
    # 接触表：6 帧横向排列，浅灰底
    frames = [np.asarray(Image.open(OUT / f"frame-{k:02d}.png").convert("RGBA"))
              for k in range(1, 7)]
    ims = [composite(f) for f in frames]
    pad, lab = 18, 30
    W = sum(i.width for i in ims) + pad * (len(ims) + 1)
    H = max(i.height for i in ims) + pad * 2 + lab
    sheet = Image.new("RGB", (W, H), (255, 255, 255))
    x = pad
    from PIL import ImageDraw
    dr = ImageDraw.Draw(sheet)
    for i, im in enumerate(ims):
        sheet.paste(im, (x, pad + lab))
        dr.text((x + 2, pad), f"frame-{i+1:02d}  t={[0,250,500,750,1000,1250][i]}ms",
                fill=(20, 20, 30))
        x += im.width + pad
    sheet.save(PREV / "contact-sheet.png")
    print("previews ->", PREV)


if __name__ == "__main__":
    main()
