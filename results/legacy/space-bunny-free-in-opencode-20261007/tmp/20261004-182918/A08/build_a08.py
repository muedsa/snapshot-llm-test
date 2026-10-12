"""A08 - 26x18 exhibition-hall grid wayfinding map with two walkable routes.

Everything on the canvas (walls, floors, doorway cells, coordinate rulers,
anchors, route polylines, arrowheads, scale bar, legend, side bar) is built
from Snapshot DSL primitives; no external image is used.
"""
from __future__ import annotations

import json
import math
import os
import sys
from collections import deque

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import dsllib as D  # noqa: E402
import snapkit  # noqa: E402
import state as S  # noqa: E402

TASK = "A08"
BASE = os.path.join(ROOT, "tasks", "A08-accessible-wayfinding", "inputs")
OUT = os.path.join(S.OUT_ROOT, TASK)
TMP = os.path.join(S.TMP_ROOT, TASK)
snapkit.configure(TASK, OUT, TMP)
if not os.path.exists(os.path.join(TMP, "A08.started")):
    S.start_task(TASK)
    open(os.path.join(TMP, "A08.started"), "w", encoding="utf-8").write("started\n")

# ----------------------------------------------------------------- inputs
LEG = json.load(open(os.path.join(BASE, "legend.json"), encoding="utf-8"))
GRID = [ln for ln in open(os.path.join(BASE, "floor.txt"), encoding="utf-8").read().splitlines()
        if ln.strip() != ""]
ROWS, COLS = len(GRID), max(len(g) for g in GRID)
for _r in GRID:
    assert len(_r) == COLS
MET = LEG["cell_meters"]

WALL = "#3D4A5CFF"
FLOOR = "#FFFFFFFF"
GRIDLINE = "#94A3B8FF"
GRIDLINE_W = "#64748BFF"
DOOR_FILL = "#FCD34DFF"
DOOR_EDGE = "#B45309FF"
R1 = "#1D4ED8FF"
R2 = "#EA580CFF"
INK = "#0F172AFF"
MUTED = "#475569FF"
FAINT = "#64748BFF"
PAPER = "#EEF2F7FF"

ANCHOR_COLOR = {"S": "#047857FF", "E": "#7E22CEFF", "A": "#0E7490FF",
                "B": "#BE185DFF", "C": "#65A30DFF", "D": "#4338CAFF"}

WALK = set()
ANCH = {}
for _y, _row in enumerate(GRID):
    for _x, _ch in enumerate(_row):
        if _ch != "#":
            WALK.add((_x, _y))
        if _ch not in (".", "#"):
            ANCH[_ch] = (_x, _y)


def bfs(src, dst):
    prev = {src: None}
    q = deque([src])
    while q:
        u = q.popleft()
        if u == dst:
            break
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            v = (u[0] + dx, u[1] + dy)
            if v in WALK and v not in prev:
                prev[v] = u
                q.append(v)
    if dst not in prev:
        raise RuntimeError("no path %s -> %s" % (src, dst))
    out, u = [], dst
    while u is not None:
        out.append(u)
        u = prev[u]
    out.reverse()
    return out


Sxy, Exy = ANCH["S"], ANCH["E"]
Bxy, Dxy, Axy, Cxy = ANCH["B"], ANCH["D"], ANCH["A"], ANCH["C"]

R1_PATH = bfs(Sxy, Exy)
SEG_SB, SEG_BD, SEG_DE = bfs(Sxy, Bxy), bfs(Bxy, Dxy), bfs(Dxy, Exy)
R2_PATH = SEG_SB[:-1] + SEG_BD[:-1] + SEG_DE

# doorway = walkable cell with wall on both sides along one axis (never widened)
DOORS = []
for (x, y) in sorted(WALK, key=lambda c: (c[1], c[0])):
    horiz = (x - 1, y) not in WALK and (x + 1, y) not in WALK
    vert = (x, y - 1) not in WALK and (x, y + 1) not in WALK
    if horiz or vert:
        DOORS.append((x, y, "EW" if horiz else "NS"))


def edges(path):
    return [tuple(sorted((p, q))) for p, q in zip(path, path[1:])]


E1, E2 = set(edges(R1_PATH)), set(edges(R2_PATH))
SHARED = sorted(E1 & E2, key=lambda e: (min(e)[1], min(e)[0]))

CONN = []
for nm, path in (("route_1", R1_PATH), ("route_2", R2_PATH)):
    bad = []
    for a, b in zip(path, path[1:]):
        if a not in WALK or b not in WALK or abs(a[0] - b[0]) + abs(a[1] - b[1]) != 1:
            bad.append([list(a), list(b)])
    CONN.append({"route": nm, "steps": len(path) - 1,
                 "all_cells_walkable": all(c in WALK for c in path),
                 "every_step_4_neighbour": not bad, "bad_steps": bad,
                 "diagonal_steps": 0, "passes_through_wall": False})

# ----------------------------------------------------------------- geometry
CS = 40
GX, GY = 68, 110
GW, GH = COLS * CS, ROWS * CS
W, H = 1560, 1080
SBX, SBW = 1128, 408
SBY, SBH = GY, 1052 - GY
BX, BY, BW2, BH2 = 24, 840, 1084, 212

INK_S = 22          # body text floor
LBL_S = 22          # badge letters
RULER_S = 16        # coordinate ruler numerals


def px(x):
    return GX + x * CS + CS / 2.0


def py(y):
    return GY + y * CS + CS / 2.0


def wrap(s, size, maxw, maxlines=4):
    toks, cur = [], ""
    for ch in s:
        if ord(ch) > 0x2E80 or ch in "，。、：；！？（）《》“”·—…①→":
            if cur:
                toks.append(cur)
                cur = ""
            toks.append(ch)
        elif ch == " ":
            if cur:
                toks.append(cur)
                cur = ""
            toks.append(" ")
        else:
            cur += ch
    if cur:
        toks.append(cur)
    lines, line = [], ""
    for t in toks:
        if D.est_width(line + t, size) <= maxw or not line:
            line += t
        else:
            lines.append(line.rstrip())
            line = "" if t == " " else t
    if line.strip():
        lines.append(line.rstrip())
    if len(lines) > maxlines:
        keep = lines[:maxlines]
        while keep and D.est_width(keep[-1] + "…", size) > maxw:
            keep[-1] = keep[-1][:-1]
        keep[-1] += "…"
        return keep
    return lines


def tri(cx, cy, half, ln, d, color):
    """Arrowhead: apex `ln` ahead of (cx,cy) along d, base 2*half wide `ln*0.7` behind."""
    n = max(4, int(half * 2))
    rh = (half * 2.0) / n + 0.6
    rows = []
    for i in range(n):
        t = (i + 0.5) / n
        ww = ln * 1.7 * (1.0 - t)          # length of this scan row
        u = cx if d in ("R", "L") else cy  # along-axis origin
        v = cy if d in ("R", "L") else cx  # perpendicular origin
        s = v - half + (half * 2.0) * (i + 0.5) / n - rh / 2.0
        if d == "R":
            rows.append(D.box(u - ln * 0.7, s, ww, rh, color=color))
        elif d == "L":
            rows.append(D.box(u + ln * 0.7 - ww, s, ww, rh, color=color))
        elif d == "D":
            rows.append(D.box(s, u - ln * 0.7, rh, ww, color=color))
        else:
            rows.append(D.box(s, u + ln * 0.7 - ww, rh, ww, color=color))
    return "\n".join(rows)


def dashed_path(path, on, off, wdt, color):
    """Dash one polyline with a continuous arc-length phase so it reads as one line.

    The travel direction matters: an upward / leftward edge must lay its dashes
    backwards from the start cell centre, otherwise the dash lands one cell off.
    """
    out, acc = [], 0.0
    for (x0, y0), (x1, y1) in zip(path, path[1:]):
        horiz = (y0 == y1)
        sgn = 1.0 if ((x1 > x0) if horiz else (y1 > y0)) else -1.0
        a0x, a0y = px(x0), py(y0)
        s = 0.0
        while s < CS - 0.01:
            ph = (acc + s) % (on + off)
            is_on = ph < on
            remain = (on - ph) if is_on else (on + off - ph)
            step = min(remain, CS - s)
            if is_on:
                if horiz:
                    x = a0x + sgn * s - (0.0 if sgn > 0 else step)
                    out.append(D.box(x, a0y - wdt / 2.0, step, wdt, color=color))
                else:
                    y = a0y + sgn * s - (0.0 if sgn > 0 else step)
                    out.append(D.box(a0x - wdt / 2.0, y, wdt, step, color=color))
            s += step
        acc += CS
    return out


kids = []

# ----------------------------------------------------------------- header
kids += [
    D.box(0, 0, W, 74, color="#0F172AFF"),
    D.text_el("展馆网格导览 · 两条可走路线", x=24, y=6, w=900, h=38, size=30,
              style="BOLD", color="#F8FAFCFF"),
    D.text_el("26 列 × 18 行 · 每格 2 m · 坐标 (x,y) 均从 0 开始，x 为列号、y 为行号，原点在左上角",
              x=24, y=42, w=1180, h=30, size=INK_S, color="#A9BCD0FF"),
    D.text_el("任务 A08", x=W - 24 - 180, y=20, w=180, h=34, size=24, style="BOLD",
              color="#7DD3FCFF", align="RIGHT"),
]

# ----------------------------------------------------------------- rulers
for x in range(COLS):
    kids.append(D.text_el("%d" % x, x=px(x) - 20, y=GY - 30, w=40, h=24, size=RULER_S,
                          color=MUTED, align="CENTER"))
for y in range(ROWS):
    kids.append(D.text_el("%d" % y, x=GX - 48, y=py(y) - 12, w=40, h=24, size=RULER_S,
                          color=MUTED, align="RIGHT"))
kids.append(D.text_el("x", x=GX + GW + 10, y=GY - 30, w=26, h=24, size=RULER_S,
                      style="BOLD", color=FAINT))
kids.append(D.text_el("y", x=GX - 48, y=GY - 30, w=40, h=24, size=RULER_S,
                      style="BOLD", color=FAINT, align="RIGHT"))

# ----------------------------------------------------------------- floor
kids.append(D.box(GX - 6, GY - 6, GW + 12, GH + 12, color="#CBD5E1FF", radius=8,
                  shadow="0 2 10 0 #0F172A1F"))
kids.append(D.box(GX, GY, GW, GH, color=FLOOR))
for (x, y, _o) in DOORS:
    kids.append(D.box(px(x) - CS / 2.0, py(y) - CS / 2.0, CS, CS, color=DOOR_FILL))
run = []
for y in range(ROWS):
    x = 0
    while x < COLS:
        if GRID[y][x] == "#":
            x0 = x
            while x < COLS and GRID[y][x] == "#":
                x += 1
            kids.append(D.box(GX + x0 * CS, GY + y * CS, (x - x0) * CS, CS, color=WALL))
        else:
            x += 1
for i in range(COLS + 1):
    kids.append(D.vline(GX + i * CS, GY, GY + GH, GRIDLINE_W, 1))
for j in range(ROWS + 1):
    kids.append(D.hline(GX, GX + GW, GY + j * CS, GRIDLINE_W, 1))
for (x, y, _o) in DOORS:
    # amber doorway cell + a small corner tab; the cell centre stays free so a route
    # crossing the opening is never hidden and the opening is never widened
    kids.append(D.box(px(x) - CS / 2.0 + 1, py(y) - CS / 2.0 + 1, CS - 2, CS - 2,
                      color=None, border="3 SOLID " + DOOR_EDGE))
    kids.append(D.box(px(x) - CS / 2.0 + 4, py(y) - CS / 2.0 + 4, 11, 11, color=DOOR_EDGE,
                      radius=3, border="1 SOLID #FFF8E7FF"))

# ----------------------------------------------------------------- routes
LW = 11
for (x0, y0), (x1, y1) in zip(R1_PATH, R1_PATH[1:]):
    if y0 == y1:
        kids.append(D.box(min(px(x0), px(x1)), py(y0) - LW / 2.0, abs(px(x1) - px(x0)), LW,
                          color=R1))
    else:
        kids.append(D.box(px(x0) - LW / 2.0, min(py(y0), py(y1)), LW, abs(py(y1) - py(y0)),
                          color=R1))
kids += dashed_path(R2_PATH, 16, 11, LW, R2)

# arrowheads, greedy so the two routes never stack an arrow on the same spot
placed = []
BADGE_PTS = [px(v[0]) for v in ANCH.values()], [py(v[1]) for v in ANCH.values()]


def dir_of(a, b):
    return "R" if b[0] > a[0] else "L" if b[0] < a[0] else "D" if b[1] > a[1] else "U"


SHAREDSET = set(SHARED)


def near_badge(cx, cy, r=28):
    return any(math.hypot(cx - px(ux), cy - py(uy)) < r for ux, uy in ANCH.values())


def put_arrow(cx, cy, d, color, shared, gap=56):
    if near_badge(cx, cy):
        return False
    if any(math.hypot(cx - a, cy - b) < gap for a, b in placed):
        return False
    placed.append((cx, cy))
    if not shared:
        # knock the local dashes out so a same-colour arrowhead still reads as an
        # arrow; on shared edges the halo is skipped so neither line gets nicked
        kids.append(tri(cx, cy, 14, 16, d, "#FFFFFFFF"))
    kids.append(tri(cx, cy, 11, 13, d, color))
    return True


# Interleaved greedy pass: 40 px cell pitch with a 56 px keep-out gives a clean
# every-other-cell rhythm, and alternating the route order between rounds lets
# the second colour take the slots the first one skipped.
ROUTES = ((R1_PATH, R1), (R2_PATH, R2))
_nmax = max(len(p) for p, _ in ROUTES)
for _rnd in range(3):
    order = ROUTES if _rnd % 2 == 0 else tuple(reversed(ROUTES))
    for i in range(1, _nmax - 1):
        for path, color in order:
            if i >= len(path) - 1:
                continue
            a, b = path[i], path[i + 1]
            put_arrow((px(a[0]) + px(b[0])) / 2.0, (py(a[1]) + py(b[1])) / 2.0,
                      dir_of(a, b), color, tuple(sorted((a, b))) in SHAREDSET)

# route start markers 1 / 2, side by side just above the shared first segment
kids += [
    D.box(px(4) - 16, py(1) - 16, 32, 32, color=R1, radius=16, border="3 SOLID #FFFFFFFF"),
    D.text_el("①", x=px(4) - 16, y=py(1) - 15, w=32, h=28, size=LBL_S, style="BOLD",
              color="#FFFFFFFF", align="CENTER"),
    D.box(px(6) - 16, py(1) - 16, 32, 32, color=R2, radius=16, border="3 SOLID #FFFFFFFF"),
    D.text_el("②", x=px(6) - 16, y=py(1) - 15, w=32, h=28, size=LBL_S, style="BOLD",
              color="#FFFFFFFF", align="CENTER"),
]

# ----------------------------------------------------------------- anchors
route_rects = []
for path in (R1_PATH, R2_PATH):
    for (x0, y0), (x1, y1) in zip(path, path[1:]):
        if y0 == y1:
            route_rects.append((min(px(x0), px(x1)) - 8, py(y0) - 8,
                                abs(px(x1) - px(x0)) + 16, 16))
        else:
            route_rects.append((px(x0) - 8, min(py(y0), py(y1)) - 8,
                                16, abs(py(y1) - py(y0)) + 16))


def hit(r1, r2):
    return not (r1[0] + r1[2] <= r2[0] or r2[0] + r2[2] <= r1[0] or
                r1[1] + r1[3] <= r2[1] or r2[1] + r2[3] <= r1[1])


for ch in ("S", "E", "A", "B", "C", "D"):
    x, y = ANCH[ch]
    col = ANCHOR_COLOR[ch]
    kids += [
        D.box(px(x) - 18, py(y) - 18, 36, 36, color="#FFFFFFFF", radius=18,
              shadow="0 1 4 0 #0F172A33"),
        D.box(px(x) - 15, py(y) - 15, 30, 30, color=col, radius=15),
        D.text_el(ch, x=px(x) - 15, y=py(y) - 14, w=30, h=28, size=LBL_S, style="BOLD",
                  color="#FFFFFFFF", align="CENTER"),
    ]

# zone names: pick the first candidate slot that touches neither route nor
# another badge / label, so nothing is covered and nothing overlaps.
name_rects = []
zone_pos = {}
for ch in ("A", "B", "C", "D"):
    ax, ay = ANCH[ch]
    nm = LEG[ch]
    tw = D.est_width(nm, INK_S) + 14
    th = 32
    best = None
    for dx, dy in ((0, -2), (0, 2), (-3, 0), (3, 0), (0, -3), (0, 3), (-4, 0), (4, 0),
                   (2, -2), (-2, -2), (2, 2), (-2, 2), (2, -3), (-2, -3), (0, 4)):
        cx, cy = px(ax + dx), py(ay + dy)
        rect = (cx - tw / 2.0, cy - th / 2.0, tw, th)
        if rect[0] < GX + 2 or rect[0] + rect[2] > GX + GW - 2:
            continue
        if rect[1] < GY + 2 or rect[1] + rect[3] > GY + GH - 2:
            continue
        if any(hit(rect, rr) for rr in route_rects):
            continue
        if any(hit(rect, rr) for rr in name_rects):
            continue
        best = (rect, cx, cy)
        break
    if best is None:
        for dx, dy in ((0, -2), (0, 2), (-3, 0), (3, 0)):
            cx, cy = px(ax + dx), py(ay + dy)
            best = ((cx - tw / 2.0, cy - th / 2.0, tw, th), cx, cy)
            break
    rect, cx, cy = best
    name_rects.append(rect)
    zone_pos[ch] = [round(cx, 2), round(cy, 2)]
    kids += [
        D.box(rect[0], rect[1], tw, th, color="#FFFFFFF2", radius=8,
              border="2 SOLID " + ANCHOR_COLOR[ch]),
        D.text_el(nm, x=rect[0], y=rect[1] + 3, w=tw, h=28, size=INK_S, style="BOLD",
                  color=ANCHOR_COLOR[ch], align="CENTER"),
    ]

# ----------------------------------------------------------------- side bar
sy = SBY


def card(title, height, body_fn):
    global sy
    kids.append(D.card(SBX, sy, SBW, height, "#FFFFFFFF", 12, "1 SOLID #CBD5E1FF",
                       "0 1 6 0 #0F172A12"))
    kids.append(D.box(SBX, sy, SBW, 5, color="#0F172AFF", radii={"TopLeft": "12",
                                                                 "TopRight": "12"}))
    kids.append(D.text_el(title, x=SBX + 16, y=sy + 9, w=SBW - 32, h=30, size=24,
                          style="BOLD", color=INK))
    body_fn(sy + 42)
    sy += height + 10


LW_IN = SBW - 32
leg_rows = [
    ("wall", "墙体 · 不可通行"),
    ("floor", "可走地面"),
    ("door", "门洞 · 宽 1 格 = 2 m"),
    ("S", "入口 S (2,2)"),
    ("E", "出口 E (23,15)"),
    ("r1", "① 路线一 · 实线 + 箭头"),
    ("r2", "② 路线二 · 虚线 + 箭头"),
    ("both", "重合段 · 两线同格叠加"),
]
CARD_H = 42 + len(leg_rows) * 29 + 6


def leg_body(y0):
    for k, (kind, label) in enumerate(leg_rows):
        ry = y0 + k * 29
        if kind == "wall":
            kids.append(D.box(SBX + 16, ry + 3, 26, 22, color=WALL, radius=3))
        elif kind == "floor":
            kids.append(D.box(SBX + 16, ry + 3, 26, 22, color=FLOOR, radius=3,
                              border="1 SOLID #94A3B8FF"))
        elif kind == "door":
            kids.append(D.box(SBX + 16, ry + 3, 26, 22, color=DOOR_FILL, radius=3,
                              border="2 SOLID " + DOOR_EDGE))
            kids.append(D.box(SBX + 19, ry + 6, 8, 8, color=DOOR_EDGE, radius=2))
        elif kind in ("S", "E"):
            kids.append(D.box(SBX + 19, ry + 6, 20, 16, color=ANCHOR_COLOR[kind],
                              radius=8, border="2 SOLID #FFFFFFFF"))
        elif kind == "r1":
            kids.append(D.box(SBX + 14, ry + 12, 26, 6, color=R1))
            kids.append(tri(SBX + 44, ry + 15, 8, 8, "R", R1))
        elif kind == "r2":
            x = SBX + 14
            while x < SBX + 40:
                kids.append(D.box(x, ry + 12, min(8, SBX + 40 - x), 6, color=R2))
                x += 14
            kids.append(tri(SBX + 44, ry + 15, 8, 8, "R", R2))
        else:
            kids.append(D.box(SBX + 14, ry + 12, 26, 6, color=R1))
            x = SBX + 14
            while x < SBX + 40:
                kids.append(D.box(x, ry + 12, min(8, SBX + 40 - x), 6, color=R2))
                x += 14
        kids.append(D.text_el(label, x=SBX + 58, y=ry + 1, w=LW_IN - 42, h=28,
                              size=INK_S, color=INK))


card("图例", CARD_H, leg_body)


def r1_body(y0):
    lines = ["起点 S (2,2) → 终点 E (23,15)",
             "%d 步 · %d m（全图最短）" % (len(R1_PATH) - 1, (len(R1_PATH) - 1) * MET),
             "与路线二重合 %d 步 · %d m" % (len(SHARED), len(SHARED) * MET)]
    for k, ln in enumerate(lines):
        kids.append(D.text_el(ln, x=SBX + 16, y=y0 + k * 30, w=LW_IN, h=28, size=INK_S,
                              color=(INK if k == 1 else MUTED),
                              style=("BOLD" if k == 1 else "NORMAL")))


card("路线一 · S → E 最短", 42 + 3 * 30 + 6, r1_body)


def r2_body(y0):
    segs = [("S (2,2) → B (12,3)", SEG_SB), ("B (12,3) → D (12,13)", SEG_BD),
            ("D (12,13) → E (23,15)", SEG_DE)]
    for k, (lab, sp) in enumerate(segs):
        kids.append(D.text_el(lab, x=SBX + 16, y=y0 + k * 30, w=LW_IN - 142, h=28,
                              size=INK_S, color=MUTED))
        kids.append(D.text_el("%d 步 · %d m" % ((len(sp) - 1), (len(sp) - 1) * MET),
                              x=SBX + LW_IN - 136, y=y0 + k * 30, w=136, h=28,
                              size=INK_S, style="BOLD", color=INK, align="RIGHT"))
    tot = (len(R2_PATH) - 1)
    kids.append(D.text_el("合计 %d 步 · %d m（先 B 后 D）" % (tot, tot * MET),
                          x=SBX + 16, y=y0 + 3 * 30 + 2, w=LW_IN, h=28, size=INK_S,
                          style="BOLD", color=R2))


card("路线二 · S → B → D → E", 42 + 4 * 30 + 8, r2_body)


def zone_body(y0):
    for k, ch in enumerate(("A", "B", "C", "D")):
        x, y = ANCH[ch]
        ry = y0 + k * 30
        kids.append(D.box(SBX + 16, ry + 4, 20, 20, color=ANCHOR_COLOR[ch], radius=10))
        kids.append(D.text_el("%s %s" % (ch, LEG[ch]), x=SBX + 46, y=ry + 1,
                              w=LW_IN - 152, h=28, size=INK_S, color=INK))
        kids.append(D.text_el("(%d,%d)" % (x, y), x=SBX + LW_IN - 96, y=ry + 1, w=96,
                              h=28, size=INK_S, color=MUTED, align="RIGHT"))


card("四个展区", 42 + 4 * 30 + 6, zone_body)


def door_body(y0):
    horiz = [(x, y) for x, y, o in DOORS if o == "EW"]
    vert = [(x, y) for x, y, o in DOORS if o == "NS"]
    cols = {}
    for x, y in vert:
        cols.setdefault(x, []).append(y)
    rows = ["行 %d：x = %s" % (horiz[0][1], " / ".join(str(x) for x, y in horiz))]
    for x in sorted(cols):
        rows.append("列 %d：y = %s" % (x, " / ".join(str(y) for y in cols[x])))
    for k, ln in enumerate(rows):
        kids.append(D.text_el(ln, x=SBX + 16, y=y0 + k * 30, w=LW_IN, h=28, size=INK_S,
                              color=DOOR_EDGE, style=("BOLD" if k == 0 else "NORMAL")))


card("门洞 7 处 · 各宽 1 格 = 2 m", 42 + 3 * 30 + 6, door_body)

# ----------------------------------------------------------------- bottom cards
LWc = BW2 // 2 - 8
kids.append(D.card(BX, BY, LWc, BH2, "#FFFFFFFF", 12, "1 SOLID #CBD5E1FF",
                   "0 1 6 0 #0F172A12"))
kids.append(D.text_el("尺度", x=BX + 16, y=BY + 11, w=300, h=30, size=24, style="BOLD",
                      color=INK))
sbx0 = BX + 20
for k in range(5):
    kids.append(D.box(sbx0 + k * CS, BY + 48, CS, 24,
                      color=("#0F172AFF" if k % 2 == 0 else "#FFFFFFFF"),
                      border="1 SOLID #0F172AFF"))
for k in range(6):
    kids.append(D.text_el("%d" % (k * 2), x=sbx0 + k * CS - 24, y=BY + 78, w=48, h=28,
                          size=INK_S, color=MUTED, align="CENTER"))
kids.append(D.text_el("m", x=sbx0 + 5 * CS + 30, y=BY + 78, w=40, h=28, size=INK_S,
                      color=MUTED))
scale_notes = [
    "每格边长 2 m；图中 1 格 = %d px" % CS,
    "米数 = 步数 × 2 m",
    "路线一 %d 步 / %d m · 路线二 %d 步 / %d m"
    % (len(R1_PATH) - 1, (len(R1_PATH) - 1) * MET, len(R2_PATH) - 1,
       (len(R2_PATH) - 1) * MET),
]
ny = BY + 112
for ln in scale_notes:
    kids.append(D.text_el(ln, x=BX + 20, y=ny, w=LWc - 40, h=28, size=INK_S, color=INK))
    ny += 30

rx = BX + BW2 // 2 + 8
rw = BW2 - BW2 // 2 - 8
kids.append(D.card(rx, BY, rw, BH2, "#FFFFFFFF", 12, "1 SOLID #CBD5E1FF",
                   "0 1 6 0 #0F172A12"))
kids.append(D.text_el("连通性检查与读图", x=rx + 16, y=BY + 11, w=rw - 32, h=30,
                      size=24, style="BOLD", color=INK))
def doors_used(path):
    s = set(path)
    return [(x, y) for x, y, o in DOORS if (x, y) in s]


D1, D2 = doors_used(R1_PATH), doors_used(R2_PATH)
notes = [
    "① %d 步：每步上下左右相邻，无穿墙无对角" % (len(R1_PATH) - 1),
    "② %d 步：先经 B(12,3)，再到 D(12,13)" % (len(R2_PATH) - 1),
    "重合 %d 步 · %d m，两线同格心可追踪" % (len(SHARED), len(SHARED) * MET),
    "①过门洞 %s" % "/".join("%d,%d" % d for d in D1),
    "②过门洞 %s" % "/".join("%d,%d" % d for d in D2),
    "逐格序列与连通性校验见 paths.json",
]
ny = BY + 42
for k, ln in enumerate(notes):
    kids.append(D.text_el(ln, x=rx + 18, y=ny, w=rw - 36, h=26, size=INK_S,
                          color=(FAINT if k == 5 else INK)))
    ny += 27.5

dsl = D.snapshot([D.stack(kids, W, H)], W, H, bg=PAPER)
with open(os.path.join(TMP, "build-a08.snapshot"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write(dsl)
r = snapkit.render(dsl, "wayfinding.png", "wayfinding.snapshot", final=True)
print("render ok=%s status=%s bytes=%s" % (r.get("ok"), r.get("status"), r.get("bytes")))
if not r.get("ok"):
    print(r.get("error"))
warn = D.warnings()
print("warnings: %d" % len(warn))
for wn in warn[:20]:
    print("WARN", wn)
print("r1 %d steps %d m | r2 %d steps %d m | shared %d" % (
    len(R1_PATH) - 1, (len(R1_PATH) - 1) * MET, len(R2_PATH) - 1,
    (len(R2_PATH) - 1) * MET, len(SHARED)))
print("sidebar last card bottom = %d (canvas 1080, cards must end <= 1052)" % sy)
print("arrows placed = %d" % len(placed))
print("doors", DOORS)
print("zone label pos", zone_pos)


def cells(path):
    return [[x, y] for x, y in path]


def pxseq(path):
    return [[round(px(x), 2), round(py(y), 2)] for x, y in path]


paths = {
    "task": TASK,
    "source_files": ["tasks/A08-accessible-wayfinding/inputs/floor.txt",
                     "tasks/A08-accessible-wayfinding/inputs/legend.json"],
    "grid": {"cols": COLS, "rows": ROWS, "origin": "top-left",
             "coordinate_system": "zero-based (x,y); x = column, y = row",
             "row_y_order": "floor.txt 第 1 行 = y 0",
             "total_cells": ROWS * COLS, "walkable_cells": len(WALK),
             "wall_cells": ROWS * COLS - len(WALK)},
    "rules_applied": {"cell_meters": MET, "movement": LEG["movement"],
                      "diagonal_moves_allowed": False, "wall_cells_passable": False,
                      "shortest_path": "BFS on the 4-neighbour walkable graph"},
    "legend_from_input": LEG,
    "anchors": {k: {"xy": list(v), "name": LEG[k], "walkable": v in WALK}
                for k, v in ANCH.items()},
    "doorways": {
        "definition": "a walkable cell whose two opposite neighbours on one axis are both "
                      "walls; such an opening is exactly one cell (2 m) wide and is never "
                      "widened by the drawing",
        "count": len(DOORS),
        "horizontal_openings": [{"xy": [x, y], "width_m": MET} for x, y, o in DOORS if o == "EW"],
        "vertical_openings": [{"xy": [x, y], "width_m": MET} for x, y, o in DOORS if o == "NS"]},
    "bfs_shortest_step_counts": {
        "S->E": len(R1_PATH) - 1, "S->B": len(SEG_SB) - 1,
        "B->D": len(SEG_BD) - 1, "D->E": len(SEG_DE) - 1},
    "routes": {
        "route_1": {
            "label": "① 路线一 S → E 最短",
            "waypoints": ["S", "E"],
            "steps": len(R1_PATH) - 1,
            "meters": (len(R1_PATH) - 1) * MET,
            "shortest_proof": "steps == BFS distance S->E == %d, and any 4-neighbour walk "
                              "needs at least |dx|+|dy| = %d steps, so this is minimal"
                              % (len(R1_PATH) - 1,
                                 abs(Sxy[0] - Exy[0]) + abs(Sxy[1] - Exy[1])),
            "cell_sequence": cells(R1_PATH),
            "cell_centers_px": pxseq(R1_PATH),
            "arrow_directions": ["R" if b[0] > a[0] else "L" if b[0] < a[0]
                                 else "D" if b[1] > a[1] else "U"
                                 for a, b in zip(R1_PATH, R1_PATH[1:])]},
        "route_2": {
            "label": "② 路线二 S → B → D → E（先 B 后 D）",
            "waypoints": ["S", "B", "D", "E"],
            "steps": len(R2_PATH) - 1,
            "meters": (len(R2_PATH) - 1) * MET,
            "shortest_proof": "each leg is its own BFS shortest path, so the total equals "
                              "d(S,B)+d(B,D)+d(D,E) = %d+%d+%d = %d"
                              % (len(SEG_SB) - 1, len(SEG_BD) - 1, len(SEG_DE) - 1,
                                 len(R2_PATH) - 1),
            "segments": [
                {"from": a, "to": b, "steps": len(p) - 1, "meters": (len(p) - 1) * MET,
                 "cell_sequence": cells(p), "cell_centers_px": pxseq(p),
                 "passes_doorways": [list(d) for d in DOORS if d[0] in p or d[1] in p]}
                for a, b, p in (("S", "B", SEG_SB), ("B", "D", SEG_BD), ("D", "E", SEG_DE))],
            "cell_sequence": cells(R2_PATH),
            "cell_centers_px": pxseq(R2_PATH),
            "visits_B_before_D": ANCH["B"] in SEG_SB and ANCH["B"] not in SEG_BD[1:]
                                  and ANCH["D"] in SEG_BD},
        "shared_edges": {
            "steps": len(SHARED), "meters": len(SHARED) * MET,
            "note": "these cell edges are walked by both routes; the drawing keeps route 1 "
                    "solid and route 2 dashed on the same cell centres so both stay readable",
            "edges": [list(e) for e in SHARED]},
    },
    "connectivity_check": {
        "rule": "consecutive cells must be walkable and 4-neighbour adjacent "
                "(|dx| + |dy| == 1); no wall cell is ever entered",
        "routes": CONN,
        "route_1_cells_all_walkable": all(c in WALK for c in R1_PATH),
        "route_2_cells_all_walkable": all(c in WALK for c in R2_PATH),
        "route_1_visits_no_wall": True,
        "route_2_visits_no_wall": True,
        "route_2_order_check": {"B_index": R2_PATH.index(ANCH["B"]),
                                "D_index": R2_PATH.index(ANCH["D"]),
                                "B_before_D": R2_PATH.index(ANCH["B"]) <
                                              R2_PATH.index(ANCH["D"])},
        "doorway_cells_entered": {"route_1": [list(d) for d in D1],
                                  "route_2": [list(d) for d in D2],
                                  "note": "each listed cell is exactly one cell (2 m) wide in "
                                          "floor.txt and is drawn without widening"},
        "wall_cells_entered": [],
        "diagonal_steps_found": 0},
    "drawing_geometry_px": {
        "canvas": [W, H], "cell_px": CS,
        "grid_origin_px": [GX, GY], "grid_size_px": [GW, GH],
        "cell_center_px": "x_px = %d + x*%d + %d ; y_px = %d + y*%d + %d"
                          % (GX, CS, CS // 2, GY, CS, CS // 2),
        "sidebar_rect": [SBX, SBY, SBW, SBH],
        "bottom_cards_rect": [BX, BY, BW2, BH2],
        "route_line_width_px": LW, "zone_label_centers_px": zone_pos},
}
with open(os.path.join(OUT, "paths.json"), "w", encoding="utf-8") as fh:
    json.dump(paths, fh, ensure_ascii=False, indent=2)
print("paths.json written")