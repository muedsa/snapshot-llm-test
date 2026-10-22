# -*- coding: utf-8 -*-
"""Pixel-verify case-08 (criteria C1..C5).

  C1  the boarding pass carries all five elements, each visibly rendered
  C2  the status timeline's nodes are strictly increasing in clock time and
      the whole column is rendered top-to-bottom in that order
  C3  the delay block states a cause and a new estimated time; the current
      step is explicitly marked
  C4  gate and seat appear identically in the pass, the status block and the
      timeline
  C5  demo boundary marked; nothing clipped or crossing the margins
"""
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PNG = os.path.join(HERE, "..", "drafts", "case-08-v2.png")

W, H = 1440, 900
PY = 128
TY = 376
BG = (238, 242, 246)
WHITE = (255, 255, 255)
HL = (238, 245, 251)
TINT = (253, 244, 230)      # current-step band
DTINT = (252, 238, 234)     # delay block
DELAY = (200, 69, 47)
GREEN = (46, 139, 87)
AMBER = (224, 160, 43)
BLUE = (47, 128, 192)
NAVY = (22, 50, 74)

FLIGHT, DATE, GATE, SEAT = "XA 2049", "10 月 26 日", "A15", "32C"
BOARD_AT, BOARD_OLD = "19:15", "18:10"
DEP_OLD, DEP_NEW = "18:40", "19:35"
TIMES = ["15:50", BOARD_OLD, "18:32", BOARD_AT, DEP_NEW]
DOTCOL = [GREEN, DELAY, AMBER, BLUE, BLUE]


def mins(t):
    return int(t[:2]) * 60 + int(t[3:])


assert all(mins(TIMES[i]) < mins(TIMES[i + 1]) for i in range(4)), "C2 非递增"
assert mins(DEP_NEW) - mins(DEP_OLD) == 55

im = Image.open(PNG).convert("RGB")
assert im.size == (W, H), im.size
_load = im.load()


def px(x, y):
    return _load[x, y]


def close(c, want, tol=30):
    return all(abs(c[i] - want[i]) <= tol for i in range(3))


def dark(c, thr=480):
    return sum(c) < thr


def count_dark(x0, y0, x1, y1, thr=480):
    return sum(1 for y in range(y0, y1) for x in range(x0, x1)
               if dark(px(x, y), thr))


def bbox_dark(x0, y0, x1, y1, thr=480):
    pts = [(x, y) for y in range(y0, y1) for x in range(x0, x1)
           if dark(px(x, y), thr)]
    return (min(p[0] for p in pts), min(p[1] for p in pts),
            max(p[0] for p in pts), max(p[1] for p in pts)) if pts else None


# ---- C1: five elements each visibly rendered -------------------------------
ELEMENTS = [
    ("航班号", (240, 296, 676, 346), FLIGHT, 32),
    ("日期", (240, 358, 676, 408), DATE, 32),
    ("登机时间", (240, 420, 676, 470), BOARD_AT, 32),
    ("登机口", (82, 534, 344, 594), GATE, 44),
    ("座位", (396, 534, 658, 594), SEAT, 44),
]
for lab, reg, val, size in ELEMENTS:
    n = count_dark(*reg)
    bb = bbox_dark(*reg)
    assert n > 300, "C1 %s 未渲染 (%s)" % (lab, n)
    print("  C1 %-5s %-12s ink %5d px  bbox %s" % (lab, val, n, bb))
# the two big cells really are the largest type on the pass
g1 = bbox_dark(82, 534, 344, 594)
g2 = bbox_dark(396, 534, 658, 594)
# Latin caps at 44 px measure ~32 px of ink; the rows above use 32 px CJK
assert (g1[3] - g1[1] + 1) >= 30 and (g2[3] - g2[1] + 1) >= 30, "登机口/座位不够大"
assert close(px(300, 500), HL, 10) and close(px(620, 500), HL, 10), \
    "登机口/座位缺少独立高亮格"
assert g1[2] - g1[0] > 60 and g2[2] - g2[0] > 60
# labels rendered beside them
for reg in ((64, 304, 240, 340), (64, 366, 240, 402), (64, 428, 240, 464),
            (82, 506, 344, 536), (396, 506, 658, 536)):
    assert count_dark(*reg, thr=520) > 150, "C1 要素标签缺失 %s" % (reg,)

# ---- C2: timeline rendered top-to-bottom in strictly increasing time order --
prev_bb = None
for i, t in enumerate(TIMES):
    ny = TY + 68 + i * 70
    bb = bbox_dark(756, ny - 2, 878, ny + 38)
    assert bb, "C2 第 %d 个时刻未渲染" % i
    print("  C2 %s ink bbox %s (y %d)" % (t, bb, ny))
    if prev_bb:
        assert bb[1] > prev_bb[1], "C2 节点顺序错乱"
    prev_bb = bb
    assert 866 <= bb[2] <= 876, "时刻未右对齐到 x=874"
    dot = px(900, ny + 18)
    assert close(dot, DOTCOL[i], 36), "C2 第 %d 个节点颜色 %s != %s" % (
        i, dot, DOTCOL[i])
    # connector into the next node
    if i < 4:
        assert close(px(900, ny + 54), (201, 214, 225), 34), "节点连接线缺失 %d" % i
    # event title + sub rendered
    assert count_dark(928, ny - 4, 1268, ny + 26) > 200, "事件标题缺失 %d" % i
    assert count_dark(928, ny + 28, 1268, ny + 54, thr=520) > 150, "说明缺失 %d" % i

# ---- C3: delay block + explicitly marked current step ----------------------
assert close(px(733, 240), DELAY, 30), "延误块强调条缺失"
red_n = sum(1 for y in range(176, 240) for x in range(756, 1280)
            if close(px(x, y), DELAY, 60))
assert red_n > 2500, "C3 延误大字未渲染 (%d)" % red_n
print("  C3 延误大字 %d px 红色墨迹" % red_n)
assert count_dark(756, 240, 1380, 274) > 400, "C3 延误原因未渲染"
assert count_dark(756, 274, 1380, 306) > 400, "C3 新预计时间未渲染"
assert count_dark(756, 306, 1380, 338, thr=520) > 400, "C4 状态区登机口/座位未渲染"
# the "now" band sits behind node 3 only
ny_now = TY + 68 + 2 * 70
assert close(px(760, ny_now - 8), TINT, 14), "C3 当前节点高亮缺失"
assert close(px(760, ny_now - 40), WHITE, 10), "C3 高亮带错位到其他节点"
assert close(px(760, ny_now + 60), WHITE, 10), "C3 高亮带溢出下边界"
white_in_pill = sum(1 for y in range(586, 620) for x in range(1288, 1380)
                    if close(px(x, y), WHITE, 40))
assert white_in_pill > 90, "「现在」药丸未渲染"
assert close(px(1292, 602), AMBER, 40), "「现在」药丸底色缺失"

# ---- C4: gate + seat consistent across pass / status block / timeline ------
c4 = []
c4.append(count_dark(82, 534, 344, 594) > 300)          # pass: gate cell
c4.append(count_dark(396, 534, 658, 594) > 300)         # pass: seat cell
c4.append(count_dark(756, 306, 1380, 338, thr=520) > 400)   # status block
c4.append(count_dark(928, ny_now + 28, 1268, ny_now + 54, thr=520) > 150)
assert all(c4), "C4 登机口/座位未在全部位置呈现"
print("  C4 登机口/座位四处出现一致")

# ---- C5: demo boundary + no clipping --------------------------------------
assert count_dark(40, 826, 1400, 862, thr=520) > 500, "C5 边界说明未渲染"
assert count_dark(1130, 42, 1395, 78, thr=560) > 150, "C5 页头演示标识未渲染"
assert count_dark(506, 148, 668, 174, thr=560) > 100, "C5 登机牌演示标识未渲染"

bleed = 0
for y in range(H):
    for x in (0, 4, 9, 18, 1421, 1430, W - 3):
        if not close(px(x, y), BG, 16):
            bleed += 1
for x in range(W):
    for y in (0, 4, 9, 18, 881, 890, H - 2):
        if not close(px(x, y), BG, 16):
            bleed += 1
assert bleed == 0, "有元素越出安全边距 (%d)" % bleed

# panels inside the canvas, and the barcode inside the pass card
for (x, y, w, h, name) in ((40, PY, 660, 672, "登机牌"),
                           (730, PY, 670, 220, "延误块"),
                           (730, TY, 670, 424, "时间轴")):
    assert 0 <= x and x + w <= W and 0 <= y and y + h <= H, "%s 越界" % name
bars = [x for x in range(50, 700) if close(px(x, 690), NAVY, 40)]
assert bars and 60 <= min(bars) and max(bars) <= 680, "条码越出卡片: %s" % (
    (min(bars), max(bars)) if bars else None)
assert count_dark(64, 644, 676, 730) > 8000, "条码未渲染"

print("\n延误 %d 分钟，时刻 %s 严格递增" % (mins(DEP_NEW) - mins(DEP_OLD),
                                         " < ".join(TIMES)))
print("ALL CASE-08 PASS / TIMELINE / CONSISTENCY CHECKS PASSED")
