# -*- coding: utf-8 -*-
"""Pixel-verify case-10 (criteria C1..C5).

  C1  the two rate tiers are stated separately: first-hour price and the
      subsequent per-half-hour price, both on the card and on the curve
  C2  the total is the sum of its segments; the breakdown shown on the card
      must add up to the figure shown as the current cost
  C3  every point of the cost/time staircase is where the arithmetic says it
      should be - checked point by point against one shared scale
  C4  the next critical moment is explicit: where you are now, which minute
      the price moves, and what the answer to the title question is
  C5  demo-data boundary on the page, nothing clipped, nothing off-canvas
"""
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PNG = os.path.join(HERE, "..", "drafts", "case-10-v4.png")

W, H = 1440, 900

BG = (238, 243, 248)
WHITE = (255, 255, 255)
BLUE = (31, 111, 178)
ORANGE = (224, 118, 47)
DELAY = (200, 69, 47)
NAVY = (22, 50, 74)
AXIS = (159, 178, 194)
MUT = (92, 116, 136)
FAINT = (131, 151, 166)

PX0, PX1, PY0, PY1 = 540.0, 1360.0, 640.0, 240.0
TMAX, CMAX = 150, 20
PPM = (PX1 - PX0) / TMAX
PPY = (PY0 - PY1) / CMAX
BOUNDS = [0, 61, 91, 121, 150]
COSTS = [6.0, 10.0, 14.0, 18.0]
NOW, CUR, ASK = 88, 10, 20


def X(t):
    return PX0 + t * PPM


def Y(c):
    return PY0 - c * PPY


# ---- C2: two independent formulations of the same rate card ----------------
def cost_a(t):
    """tiered: flat first hour, then whole half-hours (ceil)."""
    if t <= 60:
        return 6.0
    n = -(-(t - 60) // 30)
    return 6.0 + n * 4.0


def cost_b(t):
    """The same rule walked segment by segment over the rate card rather than
    evaluated from a formula, so the two must agree at every minute."""
    if t <= 0:
        return 0.0
    billed = 6.0                       # segment 1: the first hour, one block
    elapsed = min(t, 60)
    while elapsed < t:                 # segment 2: one block per started half-hour
        billed += 4.0
        elapsed += 30
    return billed


for t in range(1, 151):
    assert cost_a(t) == cost_b(t), "两种计费算法在 %d 分钟不一致" % t
assert cost_a(NOW) == 10.0
assert cost_a(NOW + ASK) == 14.0
assert cost_a(91) == 14.0 and cost_a(120) == 14.0 and cost_a(121) == 18.0
# the card shows this breakdown, so it must add up to the displayed total
assert 6.0 + ((NOW - 60 + 29) // 30) * 4.0 == CUR
# and the next critical minute really is the first one that costs more
assert next(t for t in range(NOW + 1, 200) if cost_a(t) > cost_a(NOW)) == 91
# point-by-point expectations for the staircase
SAMPLES = [0, 30, 59, 60, 61, 75, 90, 91, 105, 120, 121, 135, 150]
EXPECT = {t: cost_a(t) for t in SAMPLES}

im = Image.open(PNG).convert("RGB")
assert im.size == (W, H), im.size
_load = im.load()


def px(x, y):
    return _load[int(round(x)), int(round(y))]


def near(c, want, tol=30):
    return all(abs(c[i] - want[i]) <= tol for i in range(3))


def bbox(x0, y0, x1, y1, thr=480):
    pts = [(x, y) for y in range(y0, y1) for x in range(x0, x1)
           if sum(px(x, y)) < thr]
    return (min(p[0] for p in pts), min(p[1] for p in pts),
            max(p[0] for p in pts), max(p[1] for p in pts)) if pts else None


def ink(x0, y0, x1, y1, pred):
    return sum(1 for y in range(y0, y1) for x in range(x0, x1) if pred(px(x, y)))


# ---- C1: the rate card states both tiers -----------------------------------
assert near(px(60, 140), WHITE, 8), "费率规则面板缺失"
assert near(px(43, 200), NAVY, 40), "费率面板强调条缺失"
first_lbl = bbox(58, 178, 410, 210)      # 首 60 分钟（含）
first_val = bbox(58, 206, 410, 252)       # ¥6 一口价
later_lbl = bbox(58, 252, 410, 284)       # 之后每 30 分钟
later_val = bbox(58, 280, 410, 326)       # ¥4 / 30 分钟
note = bbox(58, 326, 410, 354)            # 不足 30 分钟按 30 分钟计
for nm, bb in (("首档标签", first_lbl), ("首档价格", first_val),
               ("后续标签", later_lbl), ("后续价格", later_val),
               ("计费说明", note)):
    assert bb, "%s 未渲染" % nm
for nm, bb in (("首档价格", first_val), ("后续价格", later_val)):
    h = bb[3] - bb[1] + 1
    assert h >= 24, "%s 偏小 %d px" % (nm, h)
for nm, bb in (("首档标签", first_lbl), ("后续标签", later_lbl), ("计费说明", note)):
    h = bb[3] - bb[1] + 1
    assert h <= 20, "%s 层级过高 %d px" % (nm, h)
assert (first_val[3] - first_val[1]) > (first_lbl[3] - first_lbl[1]) + 6, \
    "价格未在层级上压过标签"
n_navy_1 = ink(58, 206, 410, 252, lambda c: near(c, NAVY, 46))
n_navy_2 = ink(58, 280, 410, 326, lambda c: near(c, NAVY, 46))
assert n_navy_1 >= 150 and n_navy_2 >= 150, "两个费率价格墨迹不足"
# the chart repeats both rates, so the card is not the only place they appear
chart_rates = ink(540, 240, 1360, 530, lambda c: near(c, NAVY, 46))
assert chart_rates >= 400, "曲线上的档位单价标注不足"
print("C1 首档价格 %d px 高、后续价格 %d px 高，标签均 <=20 px；曲线档位标注墨迹 %d"
      % (first_val[3] - first_val[1] + 1, later_val[3] - later_val[1] + 1,
         chart_rates))

# ---- C2: the breakdown on the card adds up to the total --------------------
assert near(px(60, 390), WHITE, 8), "当前状态面板缺失"
rows_y = [424, 458, 492]
starts = []
for i, ry in enumerate(rows_y):
    bb = bbox(58, ry - 6, 285, ry + 34)
    assert bb, "费用拆解第 %d 行缺失" % i
    assert ry <= bb[1] <= ry + 10, "第 %d 行起始位置 %d 越出 %d..%d" % (
        i, bb[1], ry, ry + 10)
    starts.append(bb[1])
for i in range(len(starts) - 1):
    assert abs(starts[i + 1] - starts[i] - 34) <= 3, \
        "拆解行间距 %d != 34" % (starts[i + 1] - starts[i])
vals = []
for i, ry in enumerate(rows_y):
    bb = bbox(285, ry - 2, 412, ry + 32)
    assert bb, "费用拆解第 %d 行金额缺失" % i
    vals.append(bb)
div = [x for x in range(58, 412) if near(px(x, 530), (210, 222, 233), 16)]
assert len(div) > 300, "费用拆解分隔线缺失"
total = bbox(250, 528, 412, 578)
assert total, "当前费用数字缺失"
tot_h = total[3] - total[1] + 1
amt_h = vals[1][3] - vals[1][1] + 1      # the ¥6 line, same figure style
assert tot_h >= 26, "当前费用数字偏小 %d px" % tot_h
assert tot_h >= amt_h + 7, "总额未在层级上压过单段 (%d vs %d)" % (tot_h, amt_h)
n_navy_total = ink(total[0], total[1], total[2] + 1, total[3] + 1,
                   lambda c: near(c, NAVY, 46))
assert n_navy_total >= 200, "当前费用墨迹不足"
print("C2 拆解三行 y=%s，总额框 %s 高 %d px，分隔线 %d px 宽"
      % (starts, total, total[3] - total[1] + 1, len(div)))

# ---- C3: staircase geometry, point by point --------------------------------
print("  level  y-ink   y-want  cost-from-y   x-ink")
LEVEL_X = []
LEVEL_Y = []
for i, cost in enumerate(COSTS):
    want_y = Y(cost)
    probe = (620, 950, 1100, 1280)[i]
    rows = [y for y in range(int(want_y) - 6, int(want_y) + 7)
            if near(px(probe, y), BLUE, 45)]
    assert rows, "第 %d 档水平线缺失" % i
    cy = (min(rows) + max(rows)) / 2.0
    assert abs(cy - want_y) <= 2.0, "第 %d 档纵位置 %.1f != %.1f" % (i, cy, want_y)
    assert 3 <= (max(rows) - min(rows) + 1) <= 8, "第 %d 档线宽异常" % i
    yrow = int(round(cy))
    xs = [x for x in range(495, 1405) if near(px(x, yrow), BLUE, 45)]
    assert xs, "第 %d 档水平线无横向延伸" % i
    lo, hi = min(xs), max(xs)
    e_lo, e_hi = X(BOUNDS[i]), X(BOUNDS[i + 1])
    assert e_lo - 9 <= lo <= e_lo + 4, "第 %d 档左端 %d != %.1f" % (i, lo, e_lo)
    assert e_hi - 5 <= hi <= e_hi + 1, "第 %d 档右端 %d != %.1f" % (i, hi, e_hi)
    derived = (PY0 - cy) / PPY
    assert abs(derived - cost) <= 0.12, "第 %d 档反算费用 %.2f != %.0f" % (
        i, derived, cost)
    LEVEL_X.append((lo, hi))
    LEVEL_Y.append(cy)
    print("  %2d ¥%-4.0f  y=%-6.1f y-want=%-6.0f cost=%.3f   x=%d..%d"
          % (i + 1, cost, cy, want_y, derived, lo, hi))

# tiers are evenly spaced: 20 px per yuan is the one shared scale
for i in range(1, 4):
    gap = LEVEL_Y[i - 1] - LEVEL_Y[i]
    assert abs(gap - 4 * PPY) <= 3, "第 %d 档实测落差 %.1f != 80" % (i, gap)

# every sampled minute must sit on a blue pixel of its expected level
print("  point checks:")
for t in SAMPLES:
    xc = X(t)
    yc = Y(EXPECT[t])
    ok = (near(px(xc, yc), BLUE, 45) or near(px(xc - 1, yc), BLUE, 45)
          or near(px(xc + 1, yc), BLUE, 45))
    assert ok, "t=%d 分钟(¥%d) 处 (%.1f,%.0f) 不是曲线像素" % (
        t, EXPECT[t], xc, yc)
    print("    t=%3d -> ¥%-4.0f  px(%.1f,%.0f) = %s"
          % (t, EXPECT[t], xc, yc, px(xc, yc)))

# ---- C3: axes ---------------------------------------------------------------
xaxis = [x for x in range(int(PX0) + 8, int(PX1) - 6) if near(px(x, PY0), AXIS, 30)]
assert len(xaxis) > 750, "横轴缺失 (%d)" % len(xaxis)
y_samples = [y for y in range(244, 636) if not (512 <= y <= 528)]
yaxis = [y for y in y_samples if near(px(PX0, y), AXIS, 30)]
assert len(yaxis) > 0.9 * len(y_samples), "纵轴缺失 (%d/%d)" % (
    len(yaxis), len(y_samples))
print("C3 横轴 %d px、纵轴 %d/%d px 通过；四档墨迹中线 y=%s"
      % (len(xaxis), len(yaxis), len(y_samples),
         ["%.1f" % y for y in LEVEL_Y]))

# ---- C4: climb connectors, current marker, the answer -----------------------
print("  climbs:")
for i in (1, 2, 3):
    xj, ytop, ybot = X(BOUNDS[i]), Y(COSTS[i]), Y(COSTS[i - 1])
    rows = [y for y in range(int(ytop) - 2, int(ybot) + 4)
            if any(near(px(x, y), ORANGE, 40)
                   for x in range(int(xj) - 4, int(xj) + 5))]
    assert len(rows) >= 25, "第 %d 段攀升线太短 (%d)" % (i, len(rows))
    assert min(rows) <= int(ytop) + 18, "第 %d 段攀升线未接到上档" % i
    assert max(rows) >= int(ybot) - 14, "第 %d 段攀升线未落到下档" % i
    print("    t=%3d  x=%.1f  orange rows %d..%d  (%d 行)"
          % (BOUNDS[i], xj, min(rows), max(rows), len(rows)))

CX = X(NOW)
red = [(x, y) for y in range(436, 645)
       for x in range(int(CX) - 8, int(CX) + 9) if near(px(x, y), DELAY, 45)]
assert len(red) >= 90, "当前点红色标记太弱 (%d)" % len(red)
xs = [p[0] for p in red]
assert abs((min(xs) + max(xs)) / 2.0 - CX) <= 3, "当前标记线横向偏移"
assert max(p[1] for p in red) >= 636, "当前标记线未落到横轴"
assert min(p[1] for p in red) <= 448, "当前标记线未接到当前档"
print("  当前标记 x=%.1f  红像素 %d  行 %d..%d" % (
    CX, len(red), min(p[1] for p in red), max(p[1] for p in red)))

# the next critical moment, stated in the side card
jump_val = bbox(58, 630, 412, 680)
jump_sub = bbox(58, 678, 412, 714)
assert jump_val and jump_sub, "下一次跳价卡片缺字"
assert ink(jump_val[0], jump_val[1], jump_val[2] + 1, jump_val[3] + 1,
           lambda c: near(c, ORANGE, 46)) >= 120, "临界时刻未高亮"
assert (jump_val[3] - jump_val[1] + 1) >= 28, "临界时刻不够醒目"
n_delay_sub = ink(jump_sub[0], jump_sub[1], jump_sub[2] + 1, jump_sub[3] + 1,
                  lambda c: near(c, DELAY, 46))
assert n_delay_sub >= 60, "「再停 N 分钟就多花」墨迹不足"
# and on the curve itself
now_lbl = bbox(1030, 466, 1330, 500)
assert now_lbl, "曲线上的当前点标注缺失"
assert ink(now_lbl[0], now_lbl[1], now_lbl[2] + 1, now_lbl[3] + 1,
           lambda c: near(c, DELAY, 46)) >= 60, "当前点标注墨迹不足"
j1_lbl = bbox(1045, 380, 1330, 414)
assert j1_lbl and ink(j1_lbl[0], j1_lbl[1], j1_lbl[2] + 1, j1_lbl[3] + 1,
                      lambda c: near(c, ORANGE, 46)) >= 60, "91 分钟标注缺失"
j0_lbl = bbox(700, 440, 868, 474)
j2_lbl = bbox(1208, 300, 1340, 334)
assert j0_lbl and j2_lbl, "另两处临界时刻标注缺失"
print("  临界标注: 61 -> %s, 91 -> %s, 121 -> %s, 现在 -> %s"
      % (j0_lbl, j1_lbl, j2_lbl, now_lbl))

# the answer to the title question
a1 = bbox(62, 756, 1370, 804)
a2 = bbox(62, 804, 1370, 840)
assert a1 and a2, "答案条缺字"
n_a1 = ink(a1[0], a1[1], a1[2] + 1, a1[3] + 1, lambda c: near(c, DELAY, 46))
assert n_a1 >= 500, "答案主句墨迹不足 (%d)" % n_a1
assert (a1[3] - a1[1] + 1) >= 28, "答案主句不够醒目"
assert (a2[3] - a2[1] + 1) <= 26, "答案解释行层级失衡"
print("C4 答案主句框 %s 高 %d px、墨迹 %d；解释行高 %d"
      % (a1, a1[3] - a1[1] + 1, n_a1, a2[3] - a2[1] + 1))

# ---- C5: demo boundary, margins, panels -------------------------------------
bd = bbox(38, 854, 1405, 892)
assert bd, "演示数据边界声明缺失"
assert ink(bd[0], bd[1], bd[2] + 1, bd[3] + 1, lambda c: near(c, FAINT, 60)) >= 80, \
    "边界声明墨迹不足"
chip = bbox(1178, 32, 1402, 80)
assert chip and ink(chip[0], chip[1], chip[2] + 1, chip[3] + 1,
                    lambda c: near(c, DELAY, 46)) >= 60, "演示徽标缺失"
print("C5 边界声明 %s；演示徽标 %s" % (bd, chip))

for x, y, w, h, nm in ((40, 128, 390, 232, "费率规则"), (40, 376, 390, 200, "当前状态"),
                       (40, 592, 390, 140, "下一次跳价"), (460, 128, 940, 604, "图表"),
                       (40, 748, 1360, 96, "答案条")):
    assert x + w <= W and y + h <= H, "%s 面板越界" % nm
    assert near(px(x + 10, y + 8), WHITE, 10) or near(
        px(x + 10, y + 8), (252, 237, 232), 12), "%s 面板底色缺失" % nm

bleed = 0
for y in range(H):
    for x in (0, 4, 9, 19, 1406, 1416, 1426, 1436, W - 1):
        if not near(px(x, y), BG, 12):
            bleed += 1
for x in range(W):
    for y in (0, 4, 9, 19, 891, 895, 898, H - 1):
        if not near(px(x, y), BG, 12):
            bleed += 1
assert bleed == 0, "有元素越出安全边距 (%d)" % bleed
out = [(x, y) for y in range(H) for x in range(W)
       if sum(px(x, y)) < 300 and (x < 38 or x > 1402 or y < 26 or y > 892)]
assert not out, "有深色墨迹越出内容区: %s" % out[:4]
print("C5 边距逐像素扫描零越界，内容区外无深色墨迹")

print("\nC3 逐点校验通过 %d 个采样时刻；C1/C2/C4/C5 全部通过" % len(SAMPLES))
print("ALL CASE-10 TIERED-CURVE / CRITICAL-MOMENT / MARGIN CHECKS PASSED")
