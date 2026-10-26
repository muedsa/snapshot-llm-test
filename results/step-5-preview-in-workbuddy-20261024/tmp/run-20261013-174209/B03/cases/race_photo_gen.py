#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-04 用灰度赛照底图生成器（PIL）：鹭洲湿地半程马拉松清晨赛道。
输出 L 模式灰度图， tonal 范围 20–250，供 ColorFiltered 双色调映射。"""
from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw

W, H = 640, 360
OUT = Path(__file__).resolve().parent / "race-photo.png"


def main() -> None:
    im = Image.new("L", (W, H), 200)
    dr = ImageDraw.Draw(im)
    # 天空：上深下浅（黎明前）
    for y in range(210):
        t = y / 210
        dr.line([(0, y), (W, y)], fill=int(70 + 150 * t))
    # 太阳与光晕
    for r, v in ((64, 215), (46, 232), (30, 248)):
        dr.ellipse([470 - r, 96 - r, 470 + r, 96 + r], fill=v)
    # 远岸线 + 芦苇剪影
    dr.rectangle([0, 205, W, 212], fill=120)
    rnd = random.Random(7)
    for i in range(90):
        x = rnd.uniform(0, W)
        h = rnd.uniform(14, 42)
        dr.line([(x, 208), (x + rnd.uniform(-6, 6), 208 - h)],
                fill=rnd.randint(70, 100), width=2)
    # 水面
    for y in range(212, 268):
        t = (y - 212) / 56
        dr.line([(0, y), (W, y)], fill=int(150 - 30 * t))
    for i in range(40):  # 波光
        y = rnd.uniform(216, 264)
        x = rnd.uniform(0, W - 60)
        dr.line([(x, y), (x + rnd.uniform(20, 60), y)],
                fill=rnd.randint(180, 225), width=1)
    # 太阳倒影
    for i in range(10):
        y = 216 + i * 5
        wdt = 26 - i * 1.6
        dr.line([(470 - wdt, y), (470 + wdt, y)], fill=235, width=2)
    # 近岸跑道
    dr.polygon([(0, 268), (W, 268), (W, 360), (0, 360)], fill=105)
    for i in range(7):  # 跑道纹理
        y = 278 + i * 13
        dr.line([(0, y), (W, y)], fill=92, width=2)
    # 选手剪影 ×3（不同步态）
    def runner(cx, base, s, tone):
        # 头
        dr.ellipse([cx - 7 * s, base - 66 * s, cx + 7 * s, base - 52 * s],
                   fill=tone)
        # 躯干
        dr.line([(cx, base - 52 * s), (cx + 4 * s, base - 26 * s)],
                fill=tone, width=int(9 * s))
        # 前腿（跨步）
        dr.line([(cx + 4 * s, base - 26 * s), (cx + 20 * s, base - 2 * s)],
                fill=tone, width=int(7 * s))
        # 后腿
        dr.line([(cx + 4 * s, base - 26 * s), (cx - 16 * s, base - 8 * s)],
                fill=tone, width=int(7 * s))
        # 前臂
        dr.line([(cx + 2 * s, base - 46 * s), (cx + 18 * s, base - 34 * s)],
                fill=tone, width=int(6 * s))
        # 后臂
        dr.line([(cx + 2 * s, base - 46 * s), (cx - 14 * s, base - 38 * s)],
                fill=tone, width=int(6 * s))

    runner(180, 300, 1.35, 34)
    runner(300, 322, 1.6, 28)
    runner(415, 296, 1.15, 40)
    # 前景芦苇丛（左右下角，深色）
    for i in range(26):
        x = rnd.uniform(-10, 90)
        h = rnd.uniform(60, 150)
        dr.line([(x, 360), (x + rnd.uniform(-24, 10), 360 - h)],
                fill=rnd.randint(16, 30), width=3)
    for i in range(26):
        x = rnd.uniform(550, 650)
        h = rnd.uniform(60, 150)
        dr.line([(x, 360), (x + rnd.uniform(-10, 24), 360 - h)],
                fill=rnd.randint(16, 30), width=3)
    im.save(OUT, "PNG")
    print("wrote", OUT, im.size)


if __name__ == "__main__":
    main()
