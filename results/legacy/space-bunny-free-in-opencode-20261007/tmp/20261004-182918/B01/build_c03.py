# -*- coding: utf-8 -*-
"""case-03 · STORMRUN · 台风登陆前的港口撤离调度令 (1600x1100).

Brief: the duty officer at a small commercial port has to send five vessels out
of the harbour before the eye arrives. The sheet is an ORDER, not a weather
map: the officer needs the wind circles to know how much room is left, the
vessel list to know who is still inside, and a clock. Storm blues carry the
picture; red is reserved for the two instructions that must happen before 19:10.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run  # noqa: E402
import atelier as A  # noqa: E402
import dsllib as D  # noqa: E402

run.fresh()
CASE = "case-03"
W, H = 1600, 1100

# ------------------------------------------------------------------ palette
BG = "#060D18FF"
PANEL = "#0B1524FF"
SEA = "#091829FF"
LAND = "#18293DFF"
COASTC = "#33526FFF"
LINE = "#1D3350FF"
GRID = "#12243AFF"
INK = "#EAF2FFFF"
MUTED = "#8AA2C0FF"
FAINT = "#5D7694FF"
CYAN = "#4FD6FFFF"
AMBER = "#FFC24DFF"
RED = "#FF5A68FF"
RED_D = "#48161FFF"
GREEN = "#59E0A8FF"
VIOLET = "#A99BFFFF"

M = 40
HEAD_H = 100
MAP_X, MAP_Y, MAP_W, MAP_H = M, HEAD_H + 24, 928, 700
IX0, IY0 = MAP_X + 40, MAP_Y + 20          # inner map origin
IW, IH = MAP_W - 80, MAP_H - 60
SIDE_X = MAP_X + MAP_W + 24
SIDE_W = W - M - SIDE_X
TIME_Y = MAP_Y + MAP_H + 24
TIME_H = H - TIME_Y - 52

K = []

# ------------------------------------------------------------------- header
K.append(D.box(0, 0, W, HEAD_H, color=PANEL))
K.append(D.box(0, 0, 8, HEAD_H, color=RED))
K.append(D.hline(0, W, HEAD_H - 1, LINE, 1.4))
K.append(A.label(M + 26, 20, "PORT EMERGENCY ORDER · 自拟演练", size=13,
                 color=RED, ls=3.2))
K.append(A.one_line(M + 26, 42, "台风「海燕」· 港区船舶撤离调度令", size=27,
                    color=INK, font=A.SEMI, pad=20))
K.append(A.one_line(W - M, 26, "签发 17:20 · 编号 东港-2026-0917-07", size=14,
                    color=MUTED, pad=10, anchor="RIGHT", ls=0.4))
K.append(D.box(W - M - 208, 52, 208, 32, color=RED_D, radius=16))
K.append(A.ctr(W - M - 104, 60, "橙色警戒 · 预计 22:40 登陆", w=208,
               size=14, color=RED))

# --------------------------------------------------------------------- map
K.append(A.plate(MAP_X, MAP_Y, MAP_W, MAP_H, fill=SEA, radius=14, line=LINE))
for g in range(1, 6):
    K.append(D.vline(IX0 + g * IW / 6.0, IY0, IY0 + IH, GRID, 1))
for g in range(1, 5):
    K.append(D.hline(IX0, IX0 + IW, IY0 + g * IH / 5.0, GRID, 1))

# --- land west of a schematic coast, one abutting 4px column at a time.
# The coast is deliberately low-amplitude: a big zig-zag makes the stroked
# polyline read as a set of long diagonal lines instead of a shoreline.
COAST = [(330, 0), (322, 80), (338, 160), (316, 240), (330, 320), (314, 400),
         (328, 480), (312, 560), (322, 640)]


def coast_x(y):
    if y <= 0:
        return COAST[0][0]
    if y >= COAST[-1][1]:
        return COAST[-1][0]
    for i in range(len(COAST) - 1):
        y0, y1 = COAST[i][1], COAST[i + 1][1]
        if y0 <= y <= y1:
            t = (y - y0) / (y1 - y0)
            return COAST[i][0] + (COAST[i + 1][0] - COAST[i][0]) * t
    return COAST[-1][0]


yy = IY0
while yy < IY0 + IH:
    cx = IX0 + coast_x(yy - IY0)
    K.append(D.box(IX0, int(yy), cx - IX0, 4, color=LAND))
    # the shoreline is taken from the same fill edge, so the two can never
    # disagree; stroking the control polyline instead drew a visible zigzag
    K.append(D.box(cx - 2, int(yy), 2, 4, color=COASTC))
    yy += 4

# --- inland: low ridges, the coast road and three settlements, so the west
# half of the sheet carries information instead of being a flat slab.
INLAND = [[(58, 150), (148, 118), (232, 138)],
          [(50, 340), (138, 302), (226, 332)],
          [(92, 560), (174, 526), (252, 558)]]
for ridge in INLAND:
    # soft body under the crest line, so a ridge reads as terrain rather than
    # as a stray scratch across the land
    pts = [(IX0 + px, IY0 + py) for px, py in ridge]
    K += A.band(pts, [(px, py + 34) for px, py in pts], "#1E3149", 4)
    K += A.polyline(pts, "#33495F", 1.6)
ROAD = [(252, 34), (240, 180), (252, 330), (242, 470), (254, 622)]
K += A.polyline([(IX0 + px, IY0 + py) for px, py in ROAD], "#40607C", 2.2)
TOWNS = [("西堤镇", 206, 296, 6.5), ("南屏", 122, 172, 5.0),
         ("北塘", 114, 482, 5.0)]
for name, tx, ty, r in TOWNS:
    K.append(A.dot(IX0 + tx, IY0 + ty, r, "#8AA2C0"))
    K.append(A.one_line(IX0 + tx + 11, IY0 + ty - 8, name, size=12,
                        color="#7C97B6", pad=8))
K.append(A.one_line(IX0 + 18, IY0 + 40, "西 陲 半 岛", size=15,
                    color="#6A8AACFF", pad=10, ls=4.0))
K.append(A.one_line(IX0 + 264, IY0 + 26, "S203", size=11, color="#5C7898FF",
                    font=A.MONO, pad=6, anchor="RIGHT"))

# --- the eye: nested wind circles, dotted isobars, forecast cone to the NE
EX, EY = IX0 + 600, IY0 + 300
RINGS = [(236, "#4FD6FF0D", "7 级风圈", "280km", A.A(CYAN, 0.9)),
         (162, "#4FD6FF17", "10 级风圈", "170km", "#9FE8FFFF"),
         (100, "#FF5A6824", "12 级风圈", "80km", "#FFA0A8FF")]
for r, col, _n, _k, _c in RINGS:
    K.append(D.box(EX - r, EY - r, 2 * r, 2 * r, color=col, radius=r))
    n = max(26, int(2 * math.pi * r / 21))
    for i in range(n):
        a = 2 * math.pi * i / n
        K.append(A.dot(EX + r * math.cos(a), EY + r * math.sin(a), 2.0,
                       A.A(CYAN, 0.5)))
K.append(A.dot(EX, EY, 13, RED))
K.append(A.dot(EX, EY, 6, "#FFE9EBFF"))
# the name sits WEST of the eye: the east side is where the forecast cone and
# the vessel call-outs live, and text there was being crossed by both
K.append(A.one_line(EX - 22, EY - 10, "海燕", size=22, color=INK, font=A.SEMI,
                    pad=8, anchor="RIGHT"))
K.append(A.one_line(EX - 22, EY + 18, "925hPa · 近中心 42m/s", size=12,
                    color=MUTED, pad=8, anchor="RIGHT"))

# forecast cone: upper/lower edges sampled from the eye out to +18h, so the
# ribbon keeps a constant width instead of the hard vertical cut a single
# endpoint pair would leave at the far end.
CX1, CY1 = IX0 + 820, IY0 + 170
K += A.band([(EX, EY), (CX1, IY0 + 100)], [(EX, EY), (CX1, IY0 + 240)],
            "#FFC24D1C", 4)
TRACK = [(EX + (CX1 - EX) * t / 3.0, EY + (CY1 - EY) * t / 3.0)
         for t in range(4)]
K += A.polyline(TRACK, "#FFC24D99", 2.0)
for i, (px, py) in enumerate(TRACK):
    K.append(A.dot(px, py, 7.5, SEA if i == 0 else "#FFC24D33"))
    K.append(A.dot(px, py, 4.5, AMBER))
for lbl, (px, py) in (("+06h", TRACK[1]), ("+12h", TRACK[2]), ("+18h", TRACK[3])):
    K.append(A.one_line(px + 12, py - 9, lbl, size=11, color=A.A(AMBER, 0.85),
                        font=A.MONO, pad=6))
K.append(A.one_line(EX + 96, EY - 74, "预报路径 · 未来 18h", size=13,
                    color=A.A(AMBER, 0.95), pad=10))

# wind-circle legend: a compact strip along the top of the sea, above the
# outmost isobar so it never cuts the 7-level circle in half
LGX, LGY, LGW = IX0 + 300, IY0 + 6, 548
K.append(A.plate(LGX, LGY, LGW, 86, fill=SEA, radius=10, line=LINE))
K.append(A.label(LGX + 18, LGY + 12, "风圈半径", size=11, color=FAINT, ls=2.2))
for i, (_r, _c, nm, km, cc) in enumerate(RINGS):
    lx = LGX + 118 + i * 142
    K.append(A.dot(lx, LGY + 50, 5.5, cc))
    K.append(A.one_line(lx + 16, LGY + 42, nm, size=13, color=INK, pad=8))
    K.append(A.one_line(lx + 124, LGY + 42, km, size=13, color=MUTED,
                        font=A.MONO, pad=8, anchor="RIGHT"))

# --- ports on the coast. Their names sit WEST of the dot, on the land, so the
# vessel labels (all east of x=IX0+460) can never collide with them.
PORTS = [("东港 · 主码头", 170, "泊位 3 / 4 号"),
         ("南汊 · 锚地", 400, "锚位 A–C"),
         ("西堤 · 渔港", 600, "泊位 1 / 2 号")]
for name, cy, berth in PORTS:
    px, py = IX0 + coast_x(cy), IY0 + cy
    K.append(A.dot(px, py, 5.5, CYAN))
    K.append(A.dot(px, py, 10, None, line=CYAN, lw=1.6))
    K.append(A.one_line(px - 16, py - 9, name, size=13, color=INK, pad=8,
                        anchor="RIGHT"))
    K.append(A.one_line(px - 16, py + 8, berth, size=10, color=FAINT, pad=6,
                        anchor="RIGHT"))

# --- the five vessels still inside the harbour. Every marker is placed EAST
# of the coastline (coast_x never exceeds 338, so vx >= 460) - the first cut of
# this sheet put all five on the land.
VESSELS = [
    ("东盛 3 号", "工程", 744, 120, "L", GREEN, "南汊", "双锚到位后报"),
    ("琼海轮渡", "客滚", 472, 200, "R", AMBER, "东港", "载客 412 人 · 提前解缆"),
    ("海丰 12 号", "油轮", 486, 372, "R", RED, "南汊", "禁锚 · 须拖轮伴航"),
    ("长风 8 号", "散货", 486, 500, "R", AMBER, "东港", "风速 >20m/s 即返"),
    ("渔政 061", "公务", 486, 600, "R", GREEN, "西堤", "风暴潮每 30min 测报"),
]
for name, kind, vx, vy, side, col, dest, note in VESSELS:
    px, py = IX0 + vx, IY0 + vy
    K.append(A.rot_box(px - 7, py - 7, 14, 14, 45, col, radius=2))
    tx = px - 14 if side == "L" else px + 14
    anc = "RIGHT" if side == "L" else "LEFT"
    K.append(A.one_line(tx, py - 22, "%s · %s" % (name, kind), size=12,
                        color=INK, pad=8, anchor=anc))
    K.append(A.one_line(tx, py - 6, "→%s · %s" % (dest, note), size=10,
                        color=col, pad=8, anchor=anc))
    r = math.hypot(px - EX, py - EY)
    ring = None
    for r0, _c, nm, _k, _cc in RINGS:
        if r < r0:
            ring = nm.split()[0]
            break
    if ring:
        K.append(A.one_line(tx, py + 10, "位于 %s 风圈内 · 距心 %.0fkm"
                            % (ring, r / 236.0 * 280.0), size=10,
                            color=A.A(CYAN, 0.8), pad=8, anchor=anc))
    else:
        K.append(A.one_line(tx, py + 10, "位于各风圈之外 · 距心 %.0fkm"
                            % (r / 236.0 * 280.0), size=10, color=FAINT,
                            pad=8, anchor=anc))

# scale bar + north mark, on the empty southern land rather than in the sea
# where the vessel call-outs live
SBX, SBY = IX0 + 24, IY0 + 566
K.append(A.one_line(SBX, SBY - 24, "比例尺", size=11, color=FAINT, ls=2.0))
K.append(D.box(SBX, SBY, 108, 5, color="#6E8CA8"))
K.append(D.box(SBX + 54, SBY, 54, 5, color="#0B1524"))
for i in range(3):
    K.append(D.vline(SBX + i * 54, SBY - 4, SBY + 10, "#6E8CA8", 1.2))
K.append(A.one_line(SBX, SBY + 14, "0", size=10, color=FAINT, font=A.MONO,
                    pad=4))
K.append(A.one_line(SBX + 108, SBY + 14, "280 km", size=10, color=FAINT,
                    font=A.MONO, pad=4, anchor="RIGHT"))
K.append(A.arrow(SBX + 176, SBY + 24, SBX + 176, SBY - 18, "#6E8CA8", 1.6, 8))
K.append(A.ctr(SBX + 176, SBY + 26, "N", w=20, size=12, color="#8AA2C0",
               font=A.SEMI))

K.append(A.one_line(MAP_X + 24, MAP_Y + MAP_H - 28,
                    "近 18 小时路径 · 登陆点未定，登陆前 6h 更新", size=12,
                    color=FAINT, pad=8))
K.append(A.one_line(MAP_X + MAP_W - 24, MAP_Y + MAP_H - 28,
                    "陆岸线与经纬网为示意，非真实地理坐标", size=11,
                    color="#42607CFF", pad=8, anchor="RIGHT"))

# ------------------------------------------------------------ order column
K.append(A.plate(SIDE_X, MAP_Y, SIDE_W, MAP_H, fill=PANEL, radius=14, line=LINE))
K.append(A.label(SIDE_X + 24, MAP_Y + 22, "撤离指令 · 逐船", size=13,
                 color=FAINT, ls=2.4))
K.append(A.one_line(SIDE_X + 24, MAP_Y + 42, "5 艘在港 · 2 条红色指令",
                    size=21, color=INK, font=A.SEMI, pad=20))
colx = [SIDE_X + 24, SIDE_X + 176, SIDE_X + 252, SIDE_X + SIDE_W - 24]
K.append(D.hline(SIDE_X + 24, SIDE_X + SIDE_W - 24, MAP_Y + 88, LINE, 1))
for i, h in enumerate(["船名", "船型", "指令", "时限"]):
    K.append(A.one_line(colx[i], MAP_Y + 98, h, size=12, color=FAINT,
                        font=A.SEMI, pad=8, ls=1.6,
                        anchor="RIGHT" if i == 3 else "LEFT"))
ORDER = [
    ("海丰 12 号", "油轮", "立即离泊", "18:30", RED, "禁锚，须拖轮伴航"),
    ("琼海轮渡", "客滚", "提前解缆", "19:10", RED, "载客 412 人，须优先"),
    ("长风 8 号", "散货", "航道待命", "20:00", AMBER, "风速 >20m/s 即返"),
    ("东盛 3 号", "工程", "原地锚泊", "20:00", GREEN, "双锚到位后报"),
    ("渔政 061", "公务", "值守待命", "全程", GREEN, "风暴潮测报每 30min"),
]
oy = MAP_Y + 128
for name, kind, act, dl, col, note in ORDER:
    K.append(D.box(SIDE_X + 24, oy - 4, 3, 66, color=col))
    K.append(A.one_line(SIDE_X + 36, oy, name, size=15, color=INK, pad=8))
    K.append(A.one_line(colx[1], oy, kind, size=13, color=MUTED, pad=8))
    K.append(A.one_line(colx[2], oy, act, size=15, color=col, font=A.SEMI, pad=8))
    K.append(A.one_line(colx[3], oy, dl, size=14, color=col, font=A.MONO,
                        pad=8, anchor="RIGHT"))
    K.append(A.one_line(SIDE_X + 36, oy + 24, note, size=12, color=MUTED,
                        pad=8))
    K.append(D.hline(SIDE_X + 36, SIDE_X + SIDE_W - 24, oy + 58, LINE, 1))
    oy += 76
K.append(A.plate(SIDE_X + 24, oy + 6, SIDE_W - 48, 104, fill=RED_D, radius=10))
K.append(A.one_line(SIDE_X + 44, oy + 24, "港口统一停工时间 21:00", size=16,
                    color=RED, font=A.SEMI, pad=10))
K.append(A.one_line(SIDE_X + 44, oy + 50,
                    "21:00 后所有移动设备撤离泊位，人员进防波堤内侧避险点",
                    size=13, color="#FFCBD1FF", pad=10))
K.append(A.one_line(SIDE_X + 44, oy + 74, "应急集合点：西堤仓储 2 号库", size=13,
                    color="#FFCBD1FF", pad=10))

# ------------------------------------------------------------- action clock
K.append(A.plate(M, TIME_Y, W - 2 * M, TIME_H, fill=PANEL, radius=14, line=LINE))
K.append(A.label(M + 24, TIME_Y + 18, "行动时序", size=12, color=FAINT,
                 ls=2.2))
AX0, AXW = M + 132, W - 2 * M - 132 - 60
K.append(D.hline(AX0, AX0 + AXW, TIME_Y + 58, LINE, 2))
STEPS = [
    (0.00, "17:20", "签发撤离令", MUTED),
    (0.17, "18:30", "海丰 12 号离泊", RED),
    (0.37, "19:10", "琼海轮渡解缆", RED),
    (0.63, "20:00", "长风/东盛到位", AMBER),
    (0.79, "21:00", "全港停工撤离", AMBER),
    (1.00, "22:40", "预计登陆", VIOLET),
]
for t, hh, txt, col in STEPS:
    px = AX0 + AXW * t
    K.append(A.dot(px, TIME_Y + 58, 7, PANEL))
    K.append(A.dot(px, TIME_Y + 58, 4.5, col))
    last = t > 0.9
    K.append(A.one_line(px - (A.tw(hh, 14, mono=True) + 8) if last else px,
                        TIME_Y + 26, hh, size=14, color=col, font=A.MONO, pad=8))
    K.append(A.one_line(px - (A.tw(txt, 13) + 8) if last else px, TIME_Y + 74,
                        txt, size=13, color=MUTED if col == MUTED else INK,
                        pad=8))
K.append(D.hline(M + 24, W - M - 24, TIME_Y + 110, LINE, 1))
K.append(A.label(M + 24, TIME_Y + 124, "港口气象 · 逐时预报", size=12,
                 color=FAINT, ls=2.2))
FC = [("18:00", "9 级", "阵风 11 级", "2.1 m", "4.8 °C", AMBER),
      ("21:00", "11 级", "阵风 13 级", "3.4 m", "4.9 °C", RED),
      ("00:00", "12 级", "阵风 14 级", "4.6 m", "5.1 °C", RED)]
fw = (W - 2 * M - 48) / 3.0
for i, (t, w, g, tide, temp, col) in enumerate(FC):
    x = M + 24 + i * fw
    K.append(A.one_line(x, TIME_Y + 150, t, size=15, color=col, font=A.MONO,
                        pad=8))
    K.append(A.one_line(x + 62, TIME_Y + 150, "持续风 " + w, size=14, color=INK,
                        pad=8))
    K.append(A.one_line(x + 152, TIME_Y + 150, g, size=14, color=MUTED, pad=8))
    K.append(A.one_line(x + 266, TIME_Y + 150, "潮位 " + tide, size=14,
                        color=INK, pad=8))
    K.append(A.one_line(x + 372, TIME_Y + 150, "气温 " + temp, size=14,
                        color=MUTED, pad=8))
K.append(A.one_line(W - M - 24, TIME_Y + TIME_H - 14,
                    "台风路径、风圈、船舶与地名均为本次演示自拟，不代表任何真实台风或港航记录",
                    size=11, color=FAINT, pad=8, anchor="RIGHT"))

# ------------------------------------------------------------------ footer
K.append(A.one_line(M, H - 42, "CASE 03 / 10", size=12, color=FAINT,
                    font=A.MONO, pad=8))
K.append(A.one_line(W - M, H - 42, "东港 · 值班调度台", size=12, color=FAINT,
                    pad=8, anchor="RIGHT"))

dsl = A.root(K, W, H, BG)
if __name__ == "__main__":
    import json
    final = "--final" in sys.argv
    r = run.emit(CASE, dsl, final=final, label=CASE)
    print(json.dumps({k: v for k, v in r.items() if k != "dsl"},
                     ensure_ascii=False))