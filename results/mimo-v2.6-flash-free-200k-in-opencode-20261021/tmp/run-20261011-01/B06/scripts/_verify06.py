# -*- coding: utf-8 -*-
"""Pixel-verify case-06 (criteria C2 / C5).

  C2  the 100-cell array must have exactly `POP` coloured cells, and the
      colouring must be countable (rows complete left-to-right)
  C5  every panel must sit inside the canvas, the definition line must not
      cross the right margin, chip values must stay inside their chips, and
      the bottom of the composition must not be clipped
"""
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PNG = os.path.join(HERE, "..", "drafts", "case-06-v2.png")

W, H = 780, 1688
POP = 70
CELL, GAP, N = 46, 8, 10
GX0, GY0 = 124, 546
CHIPW, CHIP_GAP = 205, 12
CML, CMR, L, CW = 70, 710, 46, 688
PY1, PH1 = 212, 216

FILLED = (47, 128, 192)      # #2F80C0
EMPTY = (244, 248, 252)      # #F4F8FC
BLUE = (47, 128, 192)
DEEP = (27, 94, 143)         # #1B5E8F chip values
BORD = (203, 220, 234)
BG = (233, 241, 249)

im = Image.open(PNG).convert("RGB")
assert im.size == (W, H), im.size


def px(x, y):
    return im.getpixel((int(x), int(y)))


def close(c, want, tol=26):
    return all(abs(c[i] - want[i]) <= tol for i in range(3))


# ---- C2: exactly POP coloured cells ---------------------------------------
filled = 0
row_counts = []
for r in range(N):
    rc = 0
    for c in range(N):
        x = GX0 + c * (CELL + GAP) + CELL // 2
        y = GY0 + r * (CELL + GAP) + CELL // 2
        p = px(x, y)
        if close(p, FILLED):
            filled += 1
            rc += 1
        else:
            assert close(p, EMPTY) or close(p, BORD), \
                "cell (%d,%d) unexpected colour %s" % (c, r, p)
    row_counts.append(rc)
print("  row counts:", row_counts, " total filled =", filled)
assert filled == POP, "着色格数 %d != %d" % (filled, POP)
# countable: complete rows first, then empty rows
full = POP // N
assert row_counts[:full] == [N] * full, "着色行不完整"
assert row_counts[full:] == [0] * (N - full), "空白行被着色"

# ---- C5: grid geometry -----------------------------------------------------
span = N * CELL + (N - 1) * GAP
assert GX0 == CML + (CMR - CML - span) // 2, "网格未水平居中"
assert GX0 + span == 656 and GX0 - CML == CMR - 656, "网格左右留白不等"
assert GY0 + span == 1078
# cell edges: first cell must start/end where computed
assert close(px(GX0 + 2, GY0 + CELL // 2), FILLED, 40)
assert close(px(GX0 + CELL - 3, GY0 + CELL // 2), FILLED, 40)
assert close(px(GX0 + CELL + GAP // 2, GY0 + CELL // 2), (255, 255, 255), 20), \
    "格间空隙未留白"

# ---- C5: nothing crosses the right margin ---------------------------------
# definition quote (blue, y 268..302), inside the panel but past x=46 accent
blue_xs = [x for x in range(60, 730) for y in range(272, 300)
           if close(px(x, y), BLUE, 40)]
assert blue_xs, "定义引文未渲染"
print("  definition line x %d..%d (margin %d)" % (min(blue_xs), max(blue_xs), CMR))
assert max(blue_xs) <= CMR, "定义引文越过右margin"

# ---- C5: every panel inside the canvas ------------------------------------
ACCENTS = ((47, 128, 192), (199, 68, 46))       # side accent bars
PANEL_IN = ((255, 255, 255), (242, 248, 252))
for (py, ph, name) in ((PY1, PH1, "P1"), (444, 698, "P2"), (1158, 344, "P3"),
                       (1518, 148, "P4")):
    assert 0 <= py and py + ph <= H, "%s 越出画布" % name
    assert 0 <= L and L + CW <= W, "%s 横向越界" % name
    mid = py + ph // 2
    left = px(L, mid)
    right = px(L + CW - 1, mid)
    assert close(left, BORD, 40) or any(close(left, a, 40) for a in ACCENTS), \
        "%s 左边缘缺失: %s" % (name, left)
    assert close(right, BORD, 40), "%s 右边缘缺失: %s" % (name, right)
    assert any(close(px(x, mid), c, 14) for x in (54, 729) for c in PANEL_IN), \
        "%s 面板内芯缺失" % name

# ---- C5: chip values stay inside their chips ------------------------------
for i, val_max in enumerate((0.62, 0.62, 0.62)):
    cx = CML + i * (CHIPW + CHIP_GAP)
    xs = [x for x in range(cx, cx + CHIPW) for y in range(354, 390)
          if close(px(x, y), DEEP, 44)]
    assert xs, "chip %d value missing" % i
    right = max(xs)
    print("  chip %d value x %d..%d  right edge %d" % (i, min(xs), right,
                                                       cx + CHIPW))
    assert right <= cx + CHIPW - 8, "chip %d 数值溢出边框" % i

# ---- C5: bottom not clipped -----------------------------------------------
assert all(close(px(x, H - 2), BG, 30) for x in range(0, W, 7)), "底部被裁剪"
assert all(close(px(x, 0), BG, 30) for x in range(0, W, 7)), "顶部被裁剪"

print("\nALL CASE-06 ARRAY / LAYOUT CHECKS PASSED")
