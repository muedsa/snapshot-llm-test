# -*- coding: utf-8 -*-
"""A10 几何/语义复核（第二轮，针对性检查）。"""
from __future__ import annotations

import os

from PIL import Image

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
PNG = os.path.join(ROOT, "outputs", "20261004-182918", "A10", "compositing-lab.png")
im = Image.open(PNG).convert("RGB")
COLS = [48, 560, 1072]
ROWS = [186, 572]


def px(i, x, y):
    cx = COLS[i % 3]
    cy = ROWS[i // 3]
    return im.getpixel((cx + x, cy + y))


def runs(i, y, x0=0, x1=320):
    out = []
    prev = px(i, x0, y)
    start = x0
    for x in range(x0 + 1, x1):
        p = px(i, x, y)
        if p != prev:
            out.append((start, x - 1, prev))
            prev, start = p, x
    out.append((start, x1 - 1, prev))
    return out


def vruns(i, x, y0=0, y1=240):
    out = []
    prev = px(i, x, y0)
    start = y0
    for y in range(y0 + 1, y1):
        p = px(i, x, y)
        if p != prev:
            out.append((start, y - 1, prev))
            prev, start = p, y
    out.append((start, y1 - 1, prev))
    return out


print("== ① rect runs y=150:", runs(0, 150))
print("== ① col x=190:", vruns(0, 190))
print("== ② rect runs y=150:", runs(1, 150))
print("== ② col x=190:", vruns(1, 190))


def edge_width(i, x0, y, x1):
    """返回 x0..x1 之间颜色过渡的像素数。"""
    return sum(1 for x in range(x0, x1) if px(i, x, y) != px(i, x - 1, y))


print("== ③ 条纹边过渡：卡外 x=10..11 宽", edge_width(2, 11, 60, 12),
      " 卡内 x=50..62 宽", edge_width(2, 50, 60, 62))
print("== ④ 条纹边过渡：卡外 x=10..11 宽", edge_width(3, 11, 60, 12),
      " 卡内 x=50..62 宽", edge_width(3, 50, 60, 62))
print("== ③ 卡上边 y=40 过渡宽度（x=160 列）:",
      [y for y in range(30, 55) if px(2, 160, y) != px(2, 160, y - 1)])
print("== ④ 卡上边 y=40 过渡宽度（x=160 列）:",
      [y for y in range(30, 55) if px(3, 160, y) != px(3, 160, y - 1)])
print("== ③ 卡左边缘 x=40 过渡（y=60 行）:",
      [x for x in range(30, 55) if px(2, x, 60) != px(2, x - 1, 60)])
print("== ④ 卡左边缘 x=40 过渡（y=60 行）:",
      [x for x in range(30, 55) if px(3, x, 60) != px(3, x - 1, 60)])

TINT = (246, 185, 74)


def is_tint(p):
    return (abs(p[0] - TINT[0]) <= 3 and abs(p[1] - TINT[1]) <= 3
            and abs(p[2] - TINT[2]) <= 6)


def tint_span(i, fixed, axis):
    vals = []
    rng = range(320) if axis == "x" else range(240)
    for v in rng:
        p = px(i, v, fixed) if axis == "x" else px(i, fixed, v)
        if is_tint(p):
            vals.append(v)
    return (min(vals), max(vals)) if vals else None


print("== ⑤ 滤色 span y=120 :", tint_span(4, 120, "x"),
      " x=160 :", tint_span(4, 160, "y"))
print("== ⑥ 滤色 span y=120 :", tint_span(5, 120, "x"),
      " x=160 :", tint_span(5, 160, "y"))
print("== ⑥ 圆心行 y=120 runs:", runs(5, 120, 40, 290))
print("== ⑥ 圆心列 x=160 runs:", vruns(5, 160, 10, 235))