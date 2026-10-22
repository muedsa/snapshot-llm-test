# -*- coding: utf-8 -*-
"""B06 case-10 · 再停 20 分钟会多多少钱 — 停车计费分段曲线 (1440x900 web)

Problem: 车库出口只告诉车主"已停 88 分钟，10 元"，车主想知道再停一会儿到底
多花钱还是不多花钱——而分段计费下，答案在绝大多数时间里不是"按比例多付"。
Redesign: 把费率规则摊开成一条阶梯曲线，标出当前点、下一次跳价的临界时刻，
并直接给出"再停 20 分钟"的结论：不是按比例，而是跨没跨档。

数据边界: 费率与场所均为自拟演示数据，不指向任何真实停车场或收费政策。
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from b06_common import box, circle, dash_line, dashed_v, emit, seg, text, tw_slot

W, H = 1440, 900
BG = "#EEF3F8"
WHITE = "#FFFFFF"
BORD = "#D2DEE9"
INK = "#14283B"
MUT = "#5C7488"
FAINT = "#8397A6"
NAVY = "#16324A"
BLUE = "#1F6FB2"
ORANGE = "#E0762F"
DELAY = "#C8452F"
GRID = "#E1EAF1"
AXIS = "#9FB2C2"

M = 40
CW = W - 2 * M

# ---------------- rate card (self-authored demo) ----------------------------
R1_MIN, R1_PRICE = 60, 6.0        # 首 60 分钟一口价
R2_MIN, R2_PRICE = 30, 4.0        # 之后每 30 分钟，不足按 30 分钟计
NOW = 88                          # 当前已停分钟数（演示）
ASK = 20                          # 车主问的是"再停 20 分钟"


def cost_of(t):
    """分段累加：首小时一口价，之后按整 30 分钟档累加。"""
    if t <= R1_MIN:
        return R1_PRICE
    return R1_PRICE + math.ceil((t - R1_MIN) / float(R2_MIN)) * R2_PRICE


# ---------------- C2: the total really is the sum of its segments ----------
tier1 = R1_PRICE
tier2_n = int(math.ceil((NOW - R1_MIN) / float(R2_MIN)))
tier2 = tier2_n * R2_PRICE
CUR = cost_of(NOW)
assert tier1 + tier2 == CUR == 10.0, (tier1, tier2, CUR)
# second, independent formulation of the same rule
assert CUR == R1_PRICE + max(0, -(-(NOW - R1_MIN) // R2_MIN)) * R2_PRICE


def next_jump(t):
    """第一次费用高于 cost_of(t) 的时刻。"""
    c = cost_of(t)
    k = t + 1
    while cost_of(k) <= c:
        k += 1
    return k


JUMP1 = next_jump(NOW)
JUMP2 = next_jump(JUMP1)
ANS20 = cost_of(NOW + ASK)
assert JUMP1 == 91 and JUMP2 == 121, (JUMP1, JUMP2)
assert JUMP1 - NOW == 3
assert ANS20 == 14.0 and ANS20 - CUR == 4.0
assert cost_of(JUMP2) == 18.0 and JUMP2 - NOW == 33

# ---------------- plot geometry --------------------------------------------
PX0, PX1 = 540.0, 1360.0
PY0, PY1 = 640.0, 240.0          # y for ¥0 and for ¥20
TMAX, CMAX = 150, 20
PX_PER_MIN = (PX1 - PX0) / TMAX
PX_PER_YUAN = (PY0 - PY1) / CMAX
assert abs(PX_PER_MIN - 5.4666667) < 1e-6 and PX_PER_YUAN == 20.0


def X(t):
    return PX0 + t * PX_PER_MIN


def Y(c):
    return PY0 - c * PX_PER_YUAN


BOUNDS = [0, R1_MIN + 1, R1_MIN + R2_MIN + 1, R1_MIN + 2 * R2_MIN + 1, TMAX]
# cost that applies on each run: evaluated just after each step, right-continuous
COSTS = [cost_of(b) for b in BOUNDS[:-1]]
assert COSTS == [6.0, 10.0, 14.0, 18.0] and BOUNDS[-1] == 150
assert BOUNDS[1] == next_jump(0), "首个跳价时刻不一致"
assert BOUNDS[2] == JUMP1 and BOUNDS[3] == JUMP2, "阶梯边界与推导的跳价时刻不一致"

TEXTS = []


def T(x, y, w, h, s, size, color, *a, **k):
    assert tw_slot(s, size) <= w, "过宽 (%d>%d): %s" % (tw_slot(s, size), w, s)
    TEXTS.append(s)
    return text(x, y, w, h, s, size, color, *a, **k)


B = [box(0, 0, W, H, BG)]

# ---------------- header ----------------------------------------------------
B.append(T(M, 28, 720, 50, "再停 %d 分钟会多多少钱" % ASK, 36, INK, bold=True))
B.append(T(M, 82, 860, 30, "停车分段计费：现在多少钱，再停多久会跨档", 18, MUT))
B.append(box(1180, 34, 220, 44, WHITE, radius=22, border=DELAY, border_w=2))
B.append(T(1180, 43, 220, 28, "演示费率 · 非真实车场", 16, DELAY, align="CENTER"))

# ---------------- C1: rate card --------------------------------------------
B.append(box(M, 128, 390, 232, WHITE, radius=16, border=BORD, border_w=2))
B.append(box(M, 128, 6, 232, NAVY, radius=3))
B.append(T(60, 144, 320, 30, "费率规则（演示）", 19, INK, bold=True))
B.append(T(60, 182, 340, 26, "首 %d 分钟（含）" % R1_MIN, 16, MUT))
B.append(T(60, 206, 340, 44, "¥%d 一口价" % int(R1_PRICE), 30, NAVY, bold=True))
B.append(T(60, 256, 340, 26, "之后每 %d 分钟" % R2_MIN, 16, MUT))
B.append(T(60, 280, 340, 44, "¥%d / %d 分钟" % (int(R2_PRICE), R2_MIN), 30,
           NAVY, bold=True))
B.append(T(60, 328, 350, 24, "不足 %d 分钟按 %d 分钟计" % (R2_MIN, R2_MIN), 15,
           FAINT))

# ---------------- current state, with the segment breakdown -----------------
B.append(box(M, 376, 390, 200, WHITE, radius=16, border=BORD, border_w=2))
B.append(T(60, 392, 320, 26, "当前状态（演示）", 16, MUT))
ROWS2 = [("已停时长", "%d 分钟" % NOW, 26, INK),
         ("首 %d 分钟" % R1_MIN, "¥%d" % int(tier1), 26, NAVY),
         ("之后 %d 分钟 → %d 个 %d 分钟" % (NOW - R1_MIN, tier2_n, R2_MIN),
          "¥%d" % int(tier2), 26, NAVY)]
for i, (lab, val, sz, colr) in enumerate(ROWS2):
    ry = 424 + i * 34
    B.append(T(60, ry, 220, 28, lab, 15 if i == 2 else 16, MUT))
    B.append(T(280, ry - 4, 130, 36, val, sz, colr, align="RIGHT",
               font="Inter" if val.startswith("¥") else None, bold=True))
B.append(seg(60, 530, 410, 530, 2, BORD))
B.append(T(60, 538, 160, 28, "当前费用", 17, INK, bold=True))
B.append(T(250, 530, 160, 46, "¥%d" % int(CUR), 38, NAVY, bold=True,
           align="RIGHT", font="Inter"))

# ---------------- C4: next critical moment ---------------------------------
B.append(box(M, 592, 390, 140, "#FDF0EA", radius=16, border="#EECDBC",
             border_w=2))
B.append(T(60, 606, 320, 26, "下一次跳价（临界时刻）", 16, MUT))
B.append(T(60, 632, 340, 46, "%d 分钟" % JUMP1, 32, ORANGE, bold=True))
B.append(T(60, 680, 350, 30, "再停 %d 分钟就多花 ¥%d"
           % (JUMP1 - NOW, int(cost_of(JUMP1) - CUR)), 17, DELAY, bold=True))

# ---------------- chart panel -----------------------------------------------
B.append(box(460, 128, 940, 604, WHITE, radius=16, border=BORD, border_w=2))
B.append(T(480, 144, 420, 30, "费用-时间曲线（分段计费）", 20, INK, bold=True))
B.append(T(480, 178, 520, 26, "横轴：停车时长（分钟） · 纵轴：累计费用（元）",
           15, MUT))
B.append(T(486, 204, 140, 24, "费用（元）", 15, MUT))
B.append(T(1210, 692, 150, 24, "时长（分钟）", 15, MUT, align="RIGHT"))

# grid + axes
for c in (0, 5, 10, 15, 20):
    if c:
        B.append(seg(PX0, Y(c), PX1, Y(c), 2, GRID))
    B.append(T(486, Y(c) - 13, 48, 26, str(c), 15, MUT, align="RIGHT",
               font="Inter"))
for t in (0, 30, 60, 90, 120, 150):
    if t:
        B.append(seg(X(t), PY1, X(t), PY0, 2, GRID))
    B.append(T(X(t) - 40, 646, 80, 26, str(t), 15, MUT, align="CENTER",
               font="Inter"))
B.append(seg(PX0, PY0, PX1, PY0, 3, AXIS))
B.append(seg(PX0, PY1, PX0, PY0, 3, AXIS))

# the staircase itself: right-continuous, one flat run per price tier
for i in range(4):
    xl, xr = X(BOUNDS[i]), X(BOUNDS[i + 1])
    yv = Y(COSTS[i])
    B.append(seg(xl, yv, xr, yv, 5, BLUE))
    circle_ = circle(xl, yv, 7, BLUE, border=WHITE, border_w=3)
    B.append(circle_)

# each jump, drawn as the vertical climb between tiers
JUMP_LABEL = ["首 %d 分钟 ¥%d" % (R1_MIN, int(R1_PRICE)),
              "每 %d 分钟 ¥%d" % (R2_MIN, int(R2_PRICE)),
              "每 %d 分钟 ¥%d" % (R2_MIN, int(R2_PRICE)),
              "每 %d 分钟 ¥%d" % (R2_MIN, int(R2_PRICE))]
for i in (1, 2, 3):
    xj = X(BOUNDS[i])
    # C4: the curve must show the exact moments the price moves, so the climb
    # between tiers is drawn as its own connector rather than left implied
    B.append(dashed_v(xj, Y(COSTS[i]), Y(COSTS[i - 1]), ORANGE, dash=6, gap=5,
                      thick=3))
    B.append(circle(xj, Y(COSTS[i]), 7, BLUE, border=WHITE, border_w=3))

# per-tier rate labels, each sitting above the run it prices.  Boxes are built
# from the measured ink width so the collision audit below sees real extents.
TIER_AT = [(560, 486, 17, NAVY), (885, 400, 17, NAVY),
           (1045, 326, 15, MUT), (1210, 246, 15, MUT)]
TIER_BOXES = []
for i, (lx, ly, sz, colr) in enumerate(TIER_AT):
    w = tw_slot(JUMP_LABEL[i], sz)
    TIER_BOXES.append((lx, ly, w, 26))
    B.append(T(lx, ly, w, 26, JUMP_LABEL[i], sz, colr, bold=True))

# C4: the current position, and the very next moment the price moves
CX, CY = X(NOW), Y(CUR)
B.append(dashed_v(CX, CY, PY0, DELAY, dash=6, gap=5, thick=2))
B.append(circle(CX, CY, 9, DELAY, border=WHITE, border_w=3))
S_NOW = "现在 %d 分钟 · ¥%d" % (NOW, int(CUR))
S_J0 = "%d 分钟起 +¥%d" % (BOUNDS[1], int(COSTS[1] - COSTS[0]))
S_J1 = "%d 分钟起 +¥%d" % (JUMP1, int(cost_of(JUMP1) - CUR))
S_J2 = "%d 分钟起 +¥%d" % (JUMP2, int(cost_of(JUMP2) - cost_of(JUMP1)))
# anchored right of its own marker line: to the left it lands squarely on the
# t=61 climb connector and the two annotations fight for the same pixels
NOW_BOX = (CX + 14, 470, tw_slot(S_NOW, 16), 26)
# the earliest climb is labelled left of its own connector, in the step's inner
# corner, so all three critical moments carry a time and not just two of them
J0_BOX = (X(BOUNDS[1]) - 12 - tw_slot(S_J0, 15), 444, tw_slot(S_J0, 15), 26)
J1_BOX = (X(JUMP1) + 12, 384, tw_slot(S_J1, 16), 26)
J2_BOX = (X(JUMP2) + 12, 304, tw_slot(S_J2, 15), 26)
B.append(T(NOW_BOX[0], NOW_BOX[1], NOW_BOX[2], 26, S_NOW, 16, DELAY,
           bold=True))
B.append(T(J0_BOX[0], J0_BOX[1], J0_BOX[2], 26, S_J0, 15, FAINT))
B.append(T(J1_BOX[0], J1_BOX[1], J1_BOX[2], 26, S_J1, 16, ORANGE, bold=True))
B.append(T(J2_BOX[0], J2_BOX[1], J2_BOX[2], 26, S_J2, 15, FAINT))

# ---------------- answer band -----------------------------------------------
B.append(box(M, 748, CW, 96, "#FCEDE8", radius=16, border="#EECDBC",
             border_w=2))
B.append(box(M, 748, 6, 96, DELAY, radius=3))
L1 = "再停 %d 分钟：¥%d → ¥%d，多花 ¥%d" % (
    ASK, int(CUR), int(ANS20), int(ANS20 - CUR))
L2 = ("下一次跳价在 %d 分钟（再停 %d 分钟），到 %d 分钟已跨过这一档；"
      "若停到 %d 分钟才会再跳到 ¥%d"
      % (JUMP1, JUMP1 - NOW, NOW + ASK, JUMP2, int(cost_of(JUMP2))))
assert tw_slot(L1, 32) <= 1300 and tw_slot(L2, 17) <= 1320
B.append(T(64, 760, 1300, 42, L1, 32, DELAY, bold=True))
B.append(T(64, 806, 1320, 30, L2, 17, MUT))

# ---------------- footer ----------------------------------------------------
BOUNDARY = "费率与场所均为自拟演示数据，不指向任何真实停车场或收费政策"
B.append(T(M, 858, 1360, 30, BOUNDARY, 16, FAINT))

# ---------------- C5 audit --------------------------------------------------
for need in ("首 %d 分钟（含）" % R1_MIN, "之后每 %d 分钟" % R2_MIN,
             "¥%d 一口价" % int(R1_PRICE), "¥%d / %d 分钟" % (int(R2_PRICE),
                                                             R2_MIN),
             BOUNDARY, L1, L2):
    assert any(need == t or need in t for t in TEXTS), "缺失: %s" % need
assert sum(1 for t in TEXTS if "¥%d" % int(R2_PRICE) in t) >= 3, "后续单价标注不足"
assert 858 + 30 <= H and 748 + 96 <= H
assert all(0 <= X(t) <= W and 0 <= Y(c) <= H for t in (0, TMAX)
           for c in (0, CMAX)), "曲线越出画布"


def _hit(a, b):
    """Axis-aligned overlap using each label's measured ink extent."""
    return not (a[0] + a[2] <= b[0] or b[0] + b[2] <= a[0] or
                a[1] + a[3] <= b[1] or b[1] + b[3] <= a[1])


# v1 lesson: an annotation can quietly land on top of a climb connector, so the
# seven chart callouts are audited against each other and against all three
# connectors before the DSL is emitted
CHART_LABELS = TIER_BOXES + [J0_BOX, NOW_BOX, J1_BOX, J2_BOX]
CLIMBS = [(X(BOUNDS[i]) - 4, Y(COSTS[i]), 8,
           Y(COSTS[i - 1]) - Y(COSTS[i])) for i in (1, 2, 3)]
for i, a in enumerate(CHART_LABELS):
    for j, c in enumerate(CLIMBS):
        assert not _hit(a, c), "图表标注 %d 压住 %d 号攀升线" % (i, j)
    for k in range(i + 1, len(CHART_LABELS)):
        assert not _hit(a, CHART_LABELS[k]), "图表标注 %d 与 %d 重叠" % (i, k)
    assert PX0 - 8 <= a[0] and a[0] + a[2] <= PX1 + 8 \
        and PY1 - 12 <= a[1] and a[1] + a[3] <= PY0 + 8, \
        "图表标注 %d 越出绘图区: %s" % (i, a)
print("图表 8 条标注与 3 条攀升线两两无重叠，均在绘图区内")

print("当前 %d 分钟 = ¥%d（首段 ¥%d + %d 个 ¥%d）"
      % (NOW, int(CUR), int(tier1), tier2_n, int(R2_PRICE)))
print("下次跳价 %d 分钟（+%d 分钟）；+20 分钟到 %d 分钟 = ¥%d（+%d）"
      % (JUMP1, JUMP1 - NOW, NOW + ASK, int(ANS20), int(ANS20 - CUR)))
print("阶梯 %s，横轴 %.4f px/分钟，纵轴 %.0f px/元"
      % ([int(c) for c in COSTS], PX_PER_MIN, PX_PER_YUAN))
print("layout ends at 888 / %d  (%d px spare)" % (H, H - 888))
print("%d 条文本全部通过宽度断言" % len(TEXTS))

VER = sys.argv[1] if len(sys.argv) > 1 else "v1"
emit(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "drafts", "case-10-%s.snapshot" % VER),
     "\n".join(B), W, H, bg=BG)
print("case-10 %s written" % VER)
