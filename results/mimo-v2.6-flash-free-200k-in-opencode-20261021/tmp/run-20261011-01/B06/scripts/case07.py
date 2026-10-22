# -*- coding: utf-8 -*-
"""B06 case-07 · 换乘 500 米是几分钟 — 地铁换乘时间轴 (1688x780 landscape)

Problem: 换乘站只告诉你"步行 300 米"，没人告诉你这要几分钟、其中多少是
爬楼，无障碍路线又差多少，以及末班车还来不来得及。
Redesign: 把换乘摊成两条与分钟数严格成正比的时间轴（常规楼梯 / 无障碍电梯），
每段标出耗时与算法；末班车余量直接扣掉换乘耗时给出"还剩多少"。

数据边界: 站点、线路、距离、时刻均为自拟演示数据；步速 1.2 m/s 是图上
明确标注的演示假设，不是实测。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from b06_common import box, emit, seg, text, tw_slot

W, H = 1688, 780
BG = "#101820"
PANEL = "#17222C"
BORD = "#24333F"
GRID = "#24333F"
INK = "#EAF2F8"
MUT = "#7E97A8"
FAINT = "#6E8798"
BLUE = "#3C86C8"      # 步行
AMBER = "#E0A02B"     # 楼梯（竖向）
GREEN = "#35A06E"     # 电梯
YELL = "#FFCB47"      # 总计 / 末班
WALK, UP, LIFT = "walk", "up", "lift"

V = 1.2                                  # 演示步速 m/s
MARGIN_L = 40
BAR_X, BAR_MAX_S = 380.0, 480.0          # 0..8 分钟
BAR_W = 1648.0 - BAR_X                   # 1268 px
PX_S = BAR_W / BAR_MAX_S                 # px per second -> C2

# ---------------- demo data -------------------------------------------------
PATH_A = [                               # 楼梯路径
    {"n": "站台", "k": WALK, "d": 72},
    {"n": "上行楼梯", "k": UP, "s": 75, "sub": "楼梯 · 竖向 1 层"},
    {"n": "换乘通道", "k": WALK, "d": 180},
    {"n": "下行楼梯", "k": UP, "s": 70, "sub": "楼梯 · 竖向 1 层"},
    {"n": "站台", "k": WALK, "d": 48},
]
PATH_B = [                               # 无障碍路径
    {"n": "站台", "k": WALK, "d": 72},
    {"n": "电梯上行", "k": LIFT, "s": 85, "sub": "等候 40 + 运行 45"},
    {"n": "无障碍通道", "k": WALK, "d": 216},
    {"n": "电梯下行", "k": LIFT, "s": 75, "sub": "等候 35 + 运行 40"},
    {"n": "站台", "k": WALK, "d": 48},
]
CUR, LAST = "23:12", "23:40"             # 演示时刻


def hhmm_min(a, b):
    ha, ma = int(a[:2]), int(a[3:])
    hb, mb = int(b[:2]), int(b[3:])
    return (hb * 60 + mb) - (ha * 60 + ma)


def mmss(s):
    s = int(round(s))
    return "%d 分 %02d 秒" % (s // 60, s % 60)


def clock(s):
    s = int(round(s))
    return "%d:%02d" % (s // 60, s % 60)


def prepare(path):
    """C1: every walking segment's time is distance / pace, and the pace is
    a stated assumption; vertical segments carry an explicit duration."""
    for sg in path:
        if sg["k"] == WALK:
            sg["t"] = sg["d"] / V
            sg["sub"] = "%g÷%g=%ds" % (sg["d"], V, int(round(sg["t"])))
            assert abs(sg["t"] * V - sg["d"]) < 1e-9, "步行时间 ≠ 距离÷步速"
        else:
            assert "s" in sg and sg["s"] > 0, "竖向段缺耗时"
            sg["t"] = float(sg["s"])
        sg["txt"] = clock(sg["t"])
    return path


prepare(PATH_A)
prepare(PATH_B)

TA, TB = sum(s["t"] for s in PATH_A), sum(s["t"] for s in PATH_B)
WALK_A = sum(s["t"] for s in PATH_A if s["k"] == WALK)
VERT_A = TA - WALK_A
WD_A = sum(s["d"] for s in PATH_A if s["k"] == WALK)
WALK_B = sum(s["t"] for s in PATH_B if s["k"] == WALK)
VERT_B = TB - WALK_B
WD_B = sum(s["d"] for s in PATH_B if s["k"] == WALK)
LIFT_T = sum(s["t"] for s in PATH_B if s["k"] == LIFT)

MARGIN = hhmm_min(CUR, LAST) * 60.0
LEFT = MARGIN - TA

# ---------------- assertions -------------------------------------------------
assert abs(TA - 395) < 1e-9, TA
assert abs(TB - 440) < 1e-9, TB
assert abs(WD_A - 300) < 1e-9 and abs(WALK_A - 250) < 1e-9
assert abs(VERT_A - 145) < 1e-9
assert abs(WD_B - 336) < 1e-9 and abs(WALK_B - 280) < 1e-9
assert abs(LIFT_T - 160) < 1e-9
# C3 both routes complete, elevator path present with its own duration
assert any(s["k"] == LIFT for s in PATH_B), "缺电梯/无障碍段"
assert VERT_B > 0 and LIFT_T > 0
assert len(PATH_A) == len(PATH_B) == 5
# C4 last-train margin is explained: current -> last, minus the transfer
assert abs(MARGIN - 28 * 60) < 1e-9
assert abs(LEFT - 1285) < 1e-9 and LEFT > 0
assert abs(LEFT - (MARGIN - TA)) < 1e-9
# C2 geometry: every segment width is proportional to its minutes
for path, total in ((PATH_A, TA), (PATH_B, TB)):
    c = 0.0
    for sg in path:
        sg["x0"] = BAR_X + c * PX_S
        c += sg["t"]
        sg["x1"] = BAR_X + c * PX_S
        sg["w"] = sg["x1"] - sg["x0"]
        assert abs(sg["w"] - sg["t"] * PX_S) < 1e-9, "段宽不正比于分钟"
        assert sg["w"] >= 40, "段过窄: %.1f" % sg["w"]
    assert abs(c - total) < 1e-9
    assert abs((BAR_X + c * PX_S) - (BAR_X + total * PX_S)) < 1e-9

TEXTS = []


def T(x, y, w, h, s, size, color, *a, **k):
    """emit text after asserting it actually fits its slot (C5)."""
    assert tw_slot(s, size) <= w, "过宽 (%d>%d): %s" % (tw_slot(s, size), w, s)
    TEXTS.append(s)
    return text(x, y, w, h, s, size, color, *a, **k)


B = [box(0, 0, W, H, BG)]

# ---------------- header ----------------------------------------------------
B.append(T(MARGIN_L, 24, 780, 48, "换乘时间轴 · 星河路站 1→6 号线", 32, INK,
           bold=True))
B.append(T(MARGIN_L, 78, 820, 30,
           "演示站点/线路/距离/时刻 · 段内数字为 分:秒", 19, MUT))
B.append(box(1130, 24, 518, 92, PANEL, radius=14, border=YELL, border_w=2))
B.append(T(1150, 36, 478, 28, "步速假设（演示，非实测）· 楼梯/电梯按段计时", 16, MUT))
B.append(T(1150, 68, 478, 36, "步行时间 = 距离 ÷ 步速 · 1.2 m/s", 21, YELL,
           bold=True))

# ---------------- axis ------------------------------------------------------
AX_Y0, AX_Y1 = 186.0, 428.0
for i in range(9):
    s = i * 60
    x = BAR_X + s * PX_S
    lab = "0" if i == 0 else "%d 分" % i
    if x + 40 <= 1648:
        B.append(T(x - 40, 132, 80, 28, lab, 15, FAINT, align="CENTER",
                   font="Inter"))
    else:
        B.append(T(x - 80, 132, 80, 28, lab, 15, FAINT, align="RIGHT",
                   font="Inter"))
    B.append(seg(x, 164, x, 176, 2, "#3A4C5A"))
    if i:
        B.append(seg(x, AX_Y0, x, AX_Y0 + 78, 2, GRID))       # track A band
        B.append(seg(x, AX_Y1 - 78, x, AX_Y1, 2, GRID))       # track B band
B.append(seg(BAR_X, 178, 1648, 178, 2, "#3A4C5A"))

# ---------------- tracks ----------------------------------------------------
COLS = {WALK: BLUE, UP: AMBER, LIFT: GREEN}
for path, ty, name, total in ((PATH_A, 186.0, "楼梯路径（常规）", TA),
                              (PATH_B, 350.0, "无障碍路径（电梯）", TB)):
    B.append(box(BAR_X - 4, ty, (total * PX_S) + 8, 78, "#1B2833", radius=10))
    B.append(T(MARGIN_L, ty + 4, 316, 30, name, 18, MUT))
    B.append(T(MARGIN_L, ty + 34, 316, 44, mmss(total), 34, YELL, bold=True,
               font="Inter"))
    for sg in path:
        x0, w = int(round(sg["x0"])), sg["w"]
        B.append(box(x0, ty, int(round(w)), 78, COLS[sg["k"]], radius=6))
        B.append(T(x0 + 2, ty + 26, int(round(w)) - 4, 30, sg["txt"], 17,
                   "#FFFFFF", bold=True, align="CENTER", font="Inter"))
        B.append(T(x0 + 2, ty + 86, int(round(w)) - 4, 26, sg["n"], 15, INK,
                   align="CENTER"))
        B.append(T(x0 + 2, ty + 110, int(round(w)) - 4, 24, sg["sub"], 13,
                   MUT, align="CENTER"))

# ---------------- summary cards --------------------------------------------
CARDS = [
    (MARGIN_L, 512, 520, "楼梯路径 · 总耗时", mmss(TA),
     "%d s = 步行 %d s + 竖向 %d s" % (int(TA), int(WALK_A), int(VERT_A)),
     "步行 %d m ÷ 1.2 m/s（演示假设）" % int(WD_A)),
    (584, 512, 520, "无障碍路径 · 总耗时", mmss(TB),
     "%d s = 步行 %d s + 电梯 %d s" % (int(TB), int(WALK_B), int(LIFT_T)),
     "电梯等候 75 s + 运行 85 s"),
    (1128, 512, 520, "末班车余量", mmss(LEFT),
     "%s 出发 → %s 末班 = %d 分钟" % (CUR, LAST, int(MARGIN // 60)),
     "已扣除换乘 %s" % mmss(TA)),
]
for cx, cy, cwid, lab, big, d1, d2 in CARDS:
    assert cx + cwid <= 1648
    B.append(box(cx, cy, cwid, 206, PANEL, radius=14, border=BORD, border_w=2))
    B.append(box(cx, cy, 6, 206, YELL, radius=3))
    iw = cwid - 52
    B.append(T(cx + 26, cy + 16, iw, 30, lab, 19, MUT))
    B.append(T(cx + 26, cy + 50, iw, 58, big, 46, YELL, bold=True, font="Inter"))
    B.append(T(cx + 26, cy + 116, iw, 28, d1, 16, INK, font="Inter"))
    B.append(T(cx + 26, cy + 148, iw, 28, d2, 16, MUT))

footer = ("演示数据：站点/线路/距离/时刻均自拟 · 步速为图上标明的演示假设 "
          "· 出行请以车站现场指引为准")
B.append(T(MARGIN_L, 734, 1608, 36, footer, 15, FAINT))

assert 734 + 36 <= H, "内容超出画布"
print("t0..: 楼梯 %s (walk %ds + vert %ds) | 无障碍 %s (walk %ds + lift %ds)"
      % (mmss(TA), WALK_A, VERT_A, mmss(TB), WALK_B, LIFT_T))
print("末班余量 %s 分钟，换乘后剩 %s" % (int(MARGIN // 60), mmss(LEFT)))
print("layout ends at 770 / %d  (%d px spare)" % (H, H - 770))
print("%d 条文本全部通过宽度断言" % len(TEXTS))

VER = sys.argv[1] if len(sys.argv) > 1 else "v1"
emit(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "drafts", "case-07-%s.snapshot" % VER),
     "\n".join(B), W, H, bg=BG)
print("case-07 %s written" % VER)
