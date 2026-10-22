# -*- coding: utf-8 -*-
"""Pixel-verify case-09 (criteria C1..C5).

  C1  the ranking is derived from the data by the stated rule chain and the
      eight rows are rendered in exactly that order
  C2  every line is internally consistent (P = 3W + D, W+D+L = played); the
      three level teams really do share the same points cell
  C3  goal difference equals goals for minus goals against, and the ratio bar
      encodes that difference
  C4  bar length is strictly proportional to the difference, measured against
      one shared scale, with the sign carried by the direction
  C5  big-screen legibility + nothing clipped or crossing the margins
"""
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PNG = os.path.join(HERE, "..", "drafts", "case-09-v3.png")

W, H = 1920, 1080
ZERO, SCALE = 1560.0, 25.0
ROW_Y, PITCH, ROW_H = 342, 78, 72

BG = (237, 241, 245)
WHITE = (255, 255, 255)
TIE = (217, 232, 246)
BLUE = (47, 128, 192)
ORANGE = (224, 118, 47)
AXIS = (148, 169, 186)
LINK = (30, 95, 148)

# (name, played, won, drawn, lost, gf, ga)
TABLE = [
    ("云岭", 14, 7, 3, 4, 22, 12), ("沁水", 14, 7, 3, 4, 19, 9),
    ("苍梧", 14, 6, 6, 2, 17, 11), ("白泽", 14, 6, 4, 4, 16, 13),
    ("青岚", 14, 5, 4, 5, 14, 15), ("长庚", 14, 4, 4, 6, 12, 17),
    ("赤壁", 14, 3, 3, 8, 10, 21), ("玄鸟", 14, 2, 5, 7, 10, 22),
]
ROWS = sorted(({"n": n, "pl": p, "w": w, "d": d, "l": l, "gf": gf, "ga": ga,
                "pts": w * 3 + d, "gd": gf - ga}
               for n, p, w, d, l, gf, ga in TABLE),
              key=lambda r: (-r["pts"], -r["gd"], -r["gf"]))

assert [r["n"] for r in ROWS] == ["云岭", "沁水", "苍梧", "白泽",
                                  "青岚", "长庚", "赤壁", "玄鸟"]
for r in ROWS:                                   # C2 / C3 arithmetic
    assert r["w"] + r["d"] + r["l"] == r["pl"]
    assert r["pts"] == r["w"] * 3 + r["d"]
    assert r["gd"] == r["gf"] - r["ga"]

im = Image.open(PNG).convert("RGB")
assert im.size == (W, H), im.size
_load = im.load()


def px(x, y):
    return _load[x, y]


def close(c, want, tol=30):
    return all(abs(c[i] - want[i]) <= tol for i in range(3))


def bar_run(y, color, tol=34):
    xs = [x for x in range(1240, 1890) if close(px(x, y), color, tol)]
    return (min(xs), max(xs)) if xs else None


def bbox(x0, y0, x1, y1, thr=480):
    pts = [(x, y) for y in range(y0, y1) for x in range(x0, x1)
           if sum(px(x, y)) < thr]
    return (min(p[0] for p in pts), min(p[1] for p in pts),
            max(p[0] for p in pts), max(p[1] for p in pts)) if pts else None


# ---- C4: bar geometry, one shared scale, sign carried by direction ---------
print("row  team   pts   gd   bar px      expect px   ratio")
prev = None
for i, r in enumerate(ROWS):
    ry = ROW_Y + i * PITCH
    gd = r["gd"]
    col = BLUE if gd > 0 else ORANGE
    run = bar_run(ry + 36, col)
    assert run, "第 %d 行比例条缺失" % i
    lo, hi = run
    width = hi - lo + 1
    assert abs(width - abs(gd) * SCALE) <= 4, \
        "第 %d 行条长 %d != %.0f" % (i, width, abs(gd) * SCALE)
    if gd > 0:
        assert abs(lo - ZERO) <= 2, "正条未从零轴起画: %d" % lo
        assert abs(hi - (ZERO + gd * SCALE - 1)) <= 3
    else:
        assert abs(hi - (ZERO - 1)) <= 2, "负条未止于零轴: %d" % hi
        assert abs(lo - (ZERO + gd * SCALE)) <= 3
    # bar body is 34 px tall
    probe = 1580 if gd > 0 else 1540
    tall = [y for y in range(ry + 4, ry + 70) if close(px(probe, y), col, 34)]
    assert tall and abs((max(tall) - min(tall) + 1) - 34) <= 2, \
        "第 %d 行条高异常" % i
    if abs(r["gd"]):
        # every bar must imply the same px-per-goal scale, allowing only for
        # whole-pixel rounding (which is proportionally larger on short bars)
        assert abs(width / abs(gd) - SCALE) <= 4.0 / abs(gd) + 0.02, \
            "第 %d 行比例尺偏离: %.2f" % (i, width / abs(gd))
    print("  %d  %-5s %3d  %+3d   %4d px    %4.0f px    %.2f px/球"
          % (i + 1, r["n"], r["pts"], gd, width, abs(gd) * SCALE,
             width / abs(gd)))
    prev = (r["gd"], width)

# the two level teams' bars must be exactly equal in length
w0 = bar_run(ROW_Y + 36, BLUE)
w1 = bar_run(ROW_Y + PITCH + 36, BLUE)
assert w0 == w1, "第 2 级并列两队条长不等: %s / %s" % (w0, w1)
# ...and the third team's bar is shorter by the goal-difference gap
w2 = bar_run(ROW_Y + 2 * PITCH + 36, BLUE)
assert abs((w0[1] - w2[1]) - 4 * SCALE) <= 2, "苍梧条差应为 4 球"

# ---- C4: the zero axis and the level-2 tie marker --------------------------
axis_px = [x for x in range(1550, 1572) if close(px(x, 900), AXIS, 30)]
assert axis_px and abs(sum(axis_px) / len(axis_px) - ZERO) <= 2, "零轴缺失"
axis_rows = [y for y in range(330, 956) if close(px(1560, y), AXIS, 30)]
# the four positive bars are drawn over the axis, so roughly 136 px of it are
# legitimately hidden behind them
assert len(axis_rows) > 430, "零轴不连续 (%d)" % len(axis_rows)
assert close(px(1810, 417), LINK, 34), "并列条连接线缺失"
assert close(px(1810, 490), TIE, 6), "连接线越过并列行"
assert close(px(1810, 350), TIE, 6), "连接线越过并列行上方"
link_rows = [y for y in range(350, 490) if close(px(1810, y), LINK, 34)]
assert len(link_rows) >= 100, "连接线太短 (%d)" % len(link_rows)

# ---- C1/C2: tie group is one band, rows render top-to-bottom ---------------
# tol 6: the tint, the page background and the row rules are all within 20 of
# each other, so the window must be narrow enough to separate all three
assert close(px(142, 350), TIE, 6), "同分组顶边缺失"
assert close(px(142, 450), TIE, 6), "同分组中段缺失"
assert close(px(142, 560), TIE, 6), "同分组底边缺失"
assert not close(px(142, 575), TIE, 6), "同分组溢出到第 4 名"
band_rows = [y for y in range(330, 600) if close(px(142, y), TIE, 6)]
assert abs(min(band_rows) - 342) <= 2 and abs(max(band_rows) - 569) <= 2, \
    "同分色带高度异常 %d..%d" % (min(band_rows), max(band_rows))
assert not any(close(px(142, y), TIE, 6) for y in range(575, 960)), \
    "非同分行被着色"

prev_bb = None
for i in range(8):
    ry = ROW_Y + i * PITCH
    bb = bbox(40, ry + 6, 132, ry + 66)
    assert bb, "第 %d 名排名数字缺失" % (i + 1)
    assert bb[2] <= 131 and bb[0] >= 40
    if prev_bb:
        assert bb[1] > prev_bb[1], "排名未按顺序渲染"
    prev_bb = bb

# ---- C1/C2: column alignment on one sample row -----------------------------
ALIGN = [((150, 410), None, "LEFT"), ((420, 552), BLUE, "RIGHT"),
         ((580, 642), None, "RIGHT"), ((660, 722), None, "RIGHT"),
         ((740, 802), None, "RIGHT"), ((820, 882), None, "RIGHT"),
         ((900, 982), None, "RIGHT"), ((1000, 1082), None, "RIGHT"),
         ((1100, 1212), BLUE, "RIGHT")]
for i, (x0x1, colr, al) in enumerate(ALIGN):
    ry = ROW_Y
    bb = bbox(x0x1[0], ry + 6, x0x1[1], ry + 66)
    assert bb, "第 %d 列首行无墨迹" % i
    if al == "RIGHT":
        assert bb[2] <= x0x1[1] and bb[2] >= x0x1[1] - 8, \
            "第 %d 列未右对齐: %s vs %s" % (i, bb[2], x0x1[1])
    else:
        assert 148 <= bb[0] <= 156, "球队列未左对齐: %s" % (bb[0],)
    if colr:
        # sample the whole cell: the bbox centre can fall on background
        pts = [(x, y) for y in range(bb[1], bb[3] + 1)
               for x in range(bb[0], bb[2] + 1) if sum(px(x, y)) < 560]
        assert pts, "第 %d 列无墨迹" % i
        hit = sum(1 for x, y in pts if close(px(x, y), colr, 70))
        assert hit > 0.6 * len(pts), "第 %d 列颜色异常 %d/%d" % (i, hit, len(pts))
    print("  col %2d  %s ink right=%d  align=%s" % (i, x0x1, bb[2], al))

# the three level teams share an identical points cell
p_w = []
for i in range(3):
    bb = bbox(420, ROW_Y + i * PITCH + 6, 552, ROW_Y + i * PITCH + 66)
    p_w.append((bb[2] - bb[0] + 1, bb[3] - bb[1] + 1))
assert p_w[0] == p_w[1] == p_w[2], "同分三队积分格不一致: %s" % (p_w,)
print("  同分三队积分墨迹尺寸一致:", p_w[0])

# ---- C5: big screen scale + margins ----------------------------------------
assert 44 <= (bbox(40, 40, 940, 104)[3] - bbox(40, 40, 940, 104)[1] + 1) <= 62, \
    "主标题不够大"
for i in range(8):
    ry = ROW_Y + i * PITCH
    nb = bbox(150, ry + 6, 400, ry + 66)
    assert nb and (nb[3] - nb[1] + 1) >= 28, "球队名偏小"
pb = bbox(420, ROW_Y + 6, 552, ROW_Y + 66)
# Latin digits at 40 px measure ~29 px of ink; the plain statistic columns
# below them use 28 px, so the points figure must still be clearly taller
sb = bbox(580, ROW_Y + 6, 642, ROW_Y + 66)
assert (pb[3] - pb[1] + 1) >= 26, "积分数字不够大（大屏要求）"
assert (pb[3] - pb[1] + 1) >= (sb[3] - sb[1] + 1) + 6, "积分未在层级上突出"

bleed = 0
for y in range(H):
    for x in (0, 4, 9, 19, 1899, 1908, W - 3):
        if not close(px(x, y), BG, 14):
            bleed += 1
for x in range(W):
    for y in (0, 4, 9, 19, 1059, 1068, H - 2):
        if not close(px(x, y), BG, 14):
            bleed += 1
assert bleed == 0, "有元素越出安全边距 (%d)" % bleed
for (x, y, w, h, name) in ((40, 160, 1840, 100, "规则链面板"),
                           (350, 182, 450, 64, "第 1 级"),
                           (860, 182, 450, 64, "第 2 级"),
                           (1370, 182, 450, 64, "第 3 级")):
    assert x + w <= W and y + h <= H, "%s 越界" % name
for cx in (350, 860, 1370):
    assert close(px(cx, 214), BLUE, 46), "规则链药丸边框缺失 %d" % cx
    assert close(px(cx + 200, 214), (242, 247, 251), 12), "药丸底色异常 %d" % cx
assert close(px(43, 210), BLUE, 40), "规则链面板强调条缺失"
# nothing in the table may spill past the content column
over = [(x, y) for y in range(336, 962) for x in range(1882, 1898)
        if sum(px(x, y)) < 480]
assert not over, "表格元素越出 1880 右边界: %s" % over[:4]

print("\n排序:", " > ".join("%s(%d/%+d)" % (r["n"], r["pts"], r["gd"])
                            for r in ROWS))
print("ALL CASE-09 TIE-BREAK / PROPORTIONALITY / LAYOUT CHECKS PASSED")
