# -*- coding: utf-8 -*-
"""A10 交付前几何自检：从最终 PNG 逐项复核 TASK.md 的硬指标。"""
from __future__ import annotations

import io
import json
import os

from PIL import Image

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
OUT = os.path.join(ROOT, "outputs", "20261004-182918", "A10")
TMP = os.path.join(ROOT, "tmp", "20261004-182918", "A10")
PNG = os.path.join(OUT, "compositing-lab.png")
SNAP = os.path.join(OUT, "compositing-lab.snapshot")

im = Image.open(PNG)
rgb = im.convert("RGB")
print("PNG size:", im.size, "mode:", im.mode, "format:", im.format)
print("PNG bytes:", os.path.getsize(PNG), " signature:", open(PNG, "rb").read(8))

a = io.open(SNAP, encoding="utf-8").read()
b = io.open(os.path.join(TMP, "drafts", "v02.snapshot"), encoding="utf-8").read()
print("snapshot == last sent DSL:", a == b, "len:", len(a))

COLS = [48, 560, 1072]
ROWS = [186, 572]
WHITE = (255, 255, 255)


def is_white(p, tol=2):
    return all(abs(p[i] - 255) <= tol for i in range(3))


def is_board(p, tol=2):
    return all(abs(p[i] - (241, 245, 249)[i]) <= tol for i in range(3))


# --- 每个实验区必须是 320x240 白底
for i in range(6):
    cx, cy = COLS[i % 3], ROWS[i // 3]
    corners = [rgb.getpixel((cx + 1, cy + 1)), rgb.getpixel((cx + 318, cy + 1)),
               rgb.getpixel((cx + 1, cy + 238)), rgb.getpixel((cx + 318, cy + 238))]
    edge = rgb.getpixel((cx - 2, cy + 120))
    print("cell %d panel origin=(%d,%d) corner-px=%s board-px-outside=%s"
          % (i + 1, cx, cy, corners, edge))

# --- 区与区间距
for row in (0, 1):
    pass
gaps_x = [COLS[1] - (COLS[0] + 320), COLS[2] - (COLS[1] + 320)]
gaps_y = ROWS[1] - (ROWS[0] + 240)
print("horizontal gaps:", gaps_x, "vertical gap:", gaps_y)

# --- ①② 矩形几何：从像素反推
def scan_edges(i, y):
    """在格内第 y 行找颜色分段边界。"""
    cx = COLS[i % 3]
    row = [rgb.getpixel((cx + x, y)) for x in range(320)]
    edges = [x for x in range(1, 320) if row[x] != row[x - 1]]
    return edges


def scan_vedges(i, x):
    cx = COLS[i % 3]
    col = [rgb.getpixel((cx + x, y)) for y in range(240)]
    return [y for y in range(1, 240) if col[y] != col[y - 1]]


print("cell1 h-edges@y=60 :", scan_edges(0, 60))
print("cell1 h-edges@y=190:", scan_edges(0, 190))
print("cell1 v-edges@x=70 :", scan_vedges(0, 70))
print("cell1 v-edges@x=250:", scan_vedges(0, 250))
print("cell2 h-edges@y=60 :", scan_edges(1, 60))
print("cell2 h-edges@y=190:", scan_edges(1, 190))

# --- ③④ 卡片边界与条纹
for i, name in ((2, "cell3"), (3, "cell4")):
    cx = COLS[i % 3]
    cy = ROWS[i // 3]
    print(name, "card row y=120 h-edges:", [x for x in range(1, 320)
                                            if rgb.getpixel((cx + x, cy + 120))
                                            != rgb.getpixel((cx + x - 1, cy + 120))][:8])
    print(name, "card col x=160 v-edges:", [y for y in range(1, 240)
                                           if rgb.getpixel((cx + 160, cy + y))
                                           != rgb.getpixel((cx + 160, cy + y - 1))][:8])

# --- ⑤⑥ 滤色区域
TINT = (246, 185, 74)


def is_tint(p):
    return (abs(p[0] - TINT[0]) <= 3 and abs(p[1] - TINT[1]) <= 3
            and abs(p[2] - TINT[2]) <= 6)


for i in (4, 5):
    cx = COLS[i % 3]
    cy = ROWS[i // 3]
    xs, ys = [], []
    for y in range(240):
        for x in range(320):
            if is_tint(rgb.getpixel((cx + x, cy + y))):
                xs.append(x)
                ys.append(y)
    print("cell%d tint bbox x[%d,%d] y[%d,%d] count=%d"
          % (i + 1, min(xs), max(xs), min(ys), max(ys), len(xs)))

# --- 文字 "SHARP / BLUR" 是否存在（③④ 同位置）
for i in (2, 3):
    cx = COLS[i % 3]
    cy = ROWS[i // 3]
    reg = [rgb.getpixel((cx + x, cy + y)) for y in range(66, 106)
           for x in range(56, 264)]
    dark = sum(1 for p in reg if sum(p) < 300)
    print("cell%d text-region dark px(<300 sum)=%d  darkest=%s"
          % (i + 1, dark, min(reg, key=sum)))

# --- 结论区文字存在性（抽样）
print("title px:", rgb.getpixel((60, 50)), rgb.getpixel((100, 60)))