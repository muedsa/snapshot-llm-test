#!/usr/bin/env python3
"""Second-pass detail measurement of reference.png (observation only)."""
import os, struct
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
SRC = ROOT / "tasks" / "A15-reference-reconstruction" / "inputs" / "reference.png"
RAW = ROOT / "tmp" / RID / "A15" / "ref.rgb"
d = SRC.read_bytes()[:33]
W, H = struct.unpack(">II", d[16:24])
r = RAW.read_bytes()


def px(x, y):
    i = (y * W + x) * 3
    return (r[i], r[i + 1], r[i + 2])


def near(c, t, tol):
    return all(abs(c[i] - t[i]) <= tol for i in range(3))


BLUE = (36, 92, 228)
WHT = (255, 255, 255)
SIDEBG = (20, 35, 60)

# ---- 1. exact bar tops / bottoms ------------------------------------
print("== BARS (blue runs on each bar center column) ==")
centers = [383, 484, 585, 686, 787, 888]
for cx in centers:
    ys = [y for y in range(300, 620) if near(px(cx, y), BLUE, 40)]
    if ys:
        print("center x=%d  blue y %d..%d  height=%d  top=%d" % (cx, min(ys), max(ys), max(ys) - min(ys) + 1, min(ys)))

# ---- 2. horizontal grid lines (sample a column in the plot, left of bars)
print("\n== GRID LINES: non-white colored rows at x=320 (chart y 320..580) ==")
for y in range(320, 585):
    c = px(320, y)
    if not near(c, WHT, 6):
        print("  y=%d color=%s" % (y, c))

print("\n== GRID LINES: non-white colored rows at x=950 (right side of plot) ==")
for y in range(320, 585):
    c = px(950, y)
    if not near(c, WHT, 6):
        print("  y=%d color=%s" % (y, c))

# ---- 3. status pill colors & boxes ----------------------------------
print("\n== STATUS PILL samples ==")
for y in [735, 745, 755, 765, 775, 785, 795, 805, 815, 825]:
    print("y=%d " % y, " ".join("%d:%s" % (x, px(x, y)) for x in [1035, 1050, 1100, 1160, 1170, 1176]))

print("\n== STATUS PILL horizontal colored runs (x 1000..1200) ==")
for y in [730, 735, 740, 745, 750, 760, 765, 770, 775, 780, 790, 795, 800, 805, 810, 815, 820, 825, 830]:
    segs = []
    for x in range(1000, 1210):
        c = px(x, y)
        if not near(c, WHT, 6):
            segs.append(x)
    if segs:
        print("  y=%d  colored x %d..%d  n=%d  sample=%s" % (y, min(segs), max(segs), len(segs), px((min(segs)+max(segs))//2, y)))

# ---- 4. dark-text bounding boxes ------------------------------------
def dark(c):
    return sum(c) < 330


def bbox(x0, y0, x1, y1):
    xs, ys = [], []
    for y in range(y0, y1):
        for x in range(x0, x1):
            if dark(px(x, y)):
                xs.append(x); ys.append(y)
    if not xs:
        return None
    return (min(xs), min(ys), max(xs), max(ys))


print("\n== TITLE dark glyph bbox (main area, y 20..90) ==")
print(" ", bbox(250, 20, 900, 90))
print("== TITLE dark glyph bbox left half (find W top-left) ==")
print(" ", bbox(250, 20, 420, 90))
print("== SUBTITLE bbox ==")
print(" ", bbox(250, 90, 700, 125))
print("== KPI label bbox card1 ==")
print(" ", bbox(270, 145, 610, 190))
print("== KPI value bbox card1 ==")
print(" ", bbox(270, 195, 610, 245))
print("== chart title bbox ==")
print(" ", bbox(275, 320, 520, 360))
print("== chart month labels bbox ==")
print(" ", bbox(330, 545, 950, 590))
print("== activity card title bbox ==")
print(" ", bbox(1045, 320, 1300, 360))
print("== table title bbox ==")
print(" ", bbox(275, 635, 560, 675))
print("== table header row bbox ==")
print(" ", bbox(275, 685, 1380, 715))
print("== table last row status bbox ==")
print(" ", bbox(1020, 795, 1190, 830))
print("== footer bbox ==")
print(" ", bbox(240, 855, 700, 890))

# ---- 5. navigation item text rows -----------------------------------
print("\n== SIDEBAR: non-background pixels by row (x 20..205, y 90..420) ==")
for y in range(90, 420, 4):
    n = sum(1 for x in range(20, 205) if not near(px(x, y), SIDEBG, 12))
    if n > 3:
        print("  y=%d n=%d" % (y, n))

# ---- 6. workspace box rows ------------------------------------------
print("\n== SIDEBAR bottom box: non-bg rows (x 22..197, y 740..880) ==")
for y in range(740, 880, 4):
    n = sum(1 for x in range(22, 197) if not near(px(x, y), SIDEBG, 12))
    if n > 3:
        print("  y=%d n=%d" % (y, n))
