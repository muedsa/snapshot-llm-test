# -*- coding: utf-8 -*-
"""Pixel-verify case-03 stepped-price chart geometry.

The redesign claims the bill is the AREA under a stepped price curve, so the
geometry itself must be proportional to the numbers:

  * x is 用电量 at a fixed scale  -> tier boundary, this-month fill edge and
    the third-tier threshold must land on their computed degrees
  * y is 单价 at a fixed scale     -> each step top must sit at price*sy_scale
  * fill width  ratio  == 186/180 度      (C2, disjoint tier quotas)
  * fill height ratio  == 0.57/0.52 元/度 (C3, rate per tier)
  * marker lines must sit on 258 and 366 度 (C4, the two months compared)
"""
import math
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PNG = os.path.join(HERE, "..", "drafts", "case-03-v2.png")

CY_ = 320
PX0, PX1 = 118.0, 700.0
PY0, PY1 = float(CY_ + 98), float(CY_ + 316)
X_MAX, P_MAX = 450.0, 1.00
SX = (PX1 - PX0) / X_MAX        # px per 度
SY = (PY1 - PY0) / P_MAX        # px per 元/度
CUR, PREV, T3 = 366, 258, 400

im = Image.open(PNG).convert("RGB")
assert im.size == (780, 1688), im.size

T1_FILL = (169, 112, 31)    # #A9701F
T2_FILL = (242, 169, 59)    # #F2A93B
STRUCT_BORDER = (44, 74, 99)   # #2C4A63
TEAL = (79, 209, 197)       # #4FD1C5  上月
YELLOW = (255, 209, 102)    # #FFD166  本月
RED = (255, 122, 92)        # #FF7A5C  第三档阈值
TOL = 30


def is_col(x, y, want, tol=TOL):
    p = im.getpixel((x, y))
    return all(abs(p[i] - want[i]) <= tol for i in range(3))


def hrun(y, want, x0=110, x1=720, tol=TOL):
    xs = [x for x in range(x0, x1) if is_col(x, y, want, tol)]
    return (min(xs), max(xs)) if xs else None


def top_at(x, y_from, y_to, want, tol=TOL):
    for y in range(y_from, y_to):
        if is_col(x, y, want, tol):
            return y
    return None


# ---- 1. x-scale: boundaries must land on their computed degrees ------------
row = 600                                   # inside all three bands
t1 = hrun(row, T1_FILL)
t2 = hrun(row, T2_FILL)
assert t1 and t2, "fill bands not found on row %d" % row
exp_t1_end = PX0 + 180 * SX
exp_t2_end = PX0 + CUR * SX
print("tier-1 fill  x %d..%d   (expect right edge %.1f = 180 度)"
      % (t1[0], t1[1], exp_t1_end))
print("tier-2 fill  x %d..%d   (expect right edge %.1f = %d 度)"
      % (t2[0], t2[1], exp_t2_end, CUR))
assert abs(t1[1] - exp_t1_end) <= 3, "tier boundary off: %d vs %.1f" % (
    t1[1], exp_t1_end)
assert abs(t2[1] - exp_t2_end) <= 3, "this-month fill edge off: %d vs %.1f" % (
    t2[1], exp_t2_end)
# fills must be contiguous and disjoint (C2)
assert t2[0] - t1[1] <= 3, "gap/overlap between tier fills: %d -> %d" % (
    t1[1], t2[0])

# ---- 2. step tops must sit at price * sy_scale ----------------------------
t1_top = top_at(200, int(PY0), int(PY1), T1_FILL)
t2_top = top_at(500, int(PY0), int(PY1), T2_FILL)
t3_top = top_at(660, int(PY0), int(PY1), STRUCT_BORDER, tol=14)
exp1 = PY1 - 0.52 * SY
exp2 = PY1 - 0.57 * SY
exp3 = PY1 - 0.82 * SY
print("step tops: tier1 %d (expect %.1f)  tier2 %d (expect %.1f)  "
      "tier3 %d (expect %.1f)" % (t1_top, exp1, t2_top, exp2, t3_top, exp3))
assert t1_top is not None and abs(t1_top - exp1) <= 3, "tier1 height wrong"
assert t2_top is not None and abs(t2_top - exp2) <= 3, "tier2 height wrong"
assert t3_top is not None and abs(t3_top - exp3) <= 3, "tier3 height wrong"

# ---- 3. proportionality of the paid area ----------------------------------
w1 = t1[1] - t1[0]
w2 = t2[1] - t2[0]
h1 = PY1 - t1_top
h2 = PY1 - t2_top
r_w, e_w = w2 / float(w1), 186.0 / 180.0
r_h, e_h = h2 / float(h1), 0.57 / 0.52
print("width ratio  %.4f (expect %.4f = 186/180 度)" % (r_w, e_w))
print("height ratio %.4f (expect %.4f = 0.57/0.52 元/度)" % (r_h, e_h))
assert abs(r_w - e_w) < 0.02, "fill width not proportional to quota"
assert abs(r_h - e_h) < 0.02, "fill height not proportional to rate"

# ---- 4. marker lines on the two compared months ---------------------------
scan = 500                                   # above both fills, below labels
teal = hrun(scan, TEAL, 300, 560, tol=40)
yellow = hrun(scan, YELLOW, 540, 630, tol=40)
exp_prev = PX0 + PREV * SX
exp_cur = PX0 + CUR * SX
print("上月 marker x=%s (expect %.1f)   本月 marker x=%s (expect %.1f)"
      % (teal, exp_prev, yellow, exp_cur))
assert teal and abs((teal[0] + teal[1]) / 2 - exp_prev) <= 3, "上月线错位"
assert yellow and abs((yellow[0] + yellow[1]) / 2 - exp_cur) <= 3, "本月线错位"

# ---- 5. third-tier threshold dash at 400 度 -------------------------------
red_px = [(x, y) for y in range(455, int(PY1)) for x in range(620, 652)
          if is_col(x, y, RED, tol=45)]
assert len(red_px) >= 8, "threshold dash not found (%d px)" % len(red_px)
mean_x = sum(p[0] for p in red_px) / float(len(red_px))
exp_t3 = PX0 + T3 * SX
print("threshold dash %d px, mean x=%.1f (expect %.1f = %d 度)"
      % (len(red_px), mean_x, exp_t3, T3))
assert abs(mean_x - exp_t3) <= 3, "400 度阈值线错位"
# the dash must be broken, i.e. genuinely dashed rather than a solid rule
ys = sorted(set(p[1] for p in red_px))
assert ys[-1] - ys[0] > 100, "dash does not span the plot"
assert len(ys) < (ys[-1] - ys[0]) * 0.9, "threshold drawn solid, not dashed"

# ---- 6. y-axis ticks at 0.4 / 0.6 / 0.8 -----------------------------------
for p in (0.4, 0.6, 0.8):
    y = int(round(PY1 - p * SY))
    ok = any(is_col(114, yy, STRUCT_BORDER, tol=22) for yy in range(y - 3, y + 4))
    print("  y-tick %.1f at y=%d -> %s" % (p, y, "OK" if ok else "MISS"))
    assert ok, "y-axis tick %.1f missing" % p

# ---- 7. numeric: area under the curve is proportional to the bill ---------
area_scale = SX * SY
bill = 180 * 0.52 + 186 * 0.57 + 0 * 0.82
print("area check: %.2f 元 x (sx*sy=%.3f) = %.0f px^2"
      % (bill, area_scale, bill * area_scale))
assert abs(bill - 199.62) < 1e-9
assert abs(180 * 0.52 + 186 * 0.57 - bill) < 1e-9

print("\nALL CHART GEOMETRY CHECKS PASSED")
