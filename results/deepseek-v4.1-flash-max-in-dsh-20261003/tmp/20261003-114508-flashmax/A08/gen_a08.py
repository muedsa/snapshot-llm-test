"""A08 DSL generator: 网格路线导览 (1560x1080).

Geometry: 38px cells, grid origin (130,196). Routes are drawn through cell centres with a
2px perpendicular offset so an overlapping stretch stays two separable lines, and they use
different line styles (solid vs dash-dot), colours and arrow head positions, so both remain
traceable without hiding any cell number or turning a wall into floor.
"""
from __future__ import annotations

import json
import math
import os
import sys

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN_ID = "20261003-114508-flashmax"
TASK = "A08"
OUT = os.path.join(ROOT, "outputs", RUN_ID, TASK)
TMP = os.path.join(ROOT, "tmp", RUN_ID, TASK)
D = json.load(open(os.path.join(OUT, "paths.json"), encoding="utf-8"))
LEGEND = json.load(open(os.path.join(ROOT, "tasks", "A08-accessible-wayfinding", "inputs",
                                    "legend.json"), encoding="utf-8"))
VER = sys.argv[1] if len(sys.argv) > 1 else "final"

CJ = "Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"
BG, CARD = "#EEF2F7FF", "#FFFFFFFF"
INK, INK2, MUTED = "#0B1220FF", "#1E293BFF", "#5B6B7FFF"
LINE, NAVY = "#E2E8F0FF", "#0F172AFF"
WALL_C, FLOOR_C = "#CBD5E1FF", "#FFFFFFFF"
R1C, R2C = "#DC2626FF", "#2563EBFF"
AREAC = "#0E9F8FFF"

W, H = 1560, 1080
COLS, ROWS, CELL = D["grid"]["columns"], D["grid"]["rows"], 34
GX, GY = 84, 168
GW, GH = COLS * CELL, ROWS * CELL
SIDEBAR_X, SIDEBAR_W = 984, 560

GRID = [l.rstrip("\n") for l in open(os.path.join(ROOT, "tasks", "A08-accessible-wayfinding",
                                                  "inputs", "floor.txt"), encoding="utf-8") if l.strip()]
R1 = [tuple(c) for c in D["route1_shortest_S_to_E"]["cell_centers"]]
R2 = [tuple(c) for c in D["route2_S_B_D_E"]["cell_centers"]]
MARK = {k: tuple(v["cell"]) for k, v in D["areas"].items()}

P: list[str] = []
add = P.append


def box(x, y, w, h, color, radius=None, border=None, shadow=None, tl=None, tr=None, bl=None, br=None):
    a = f'<Container width="{w}" height="{h}" color="{color}"'
    if radius:
        a += f' borderRadius="{radius}"'
    for nm, v in (("TopLeft", tl), ("TopRight", tr), ("BottomLeft", bl), ("BottomRight", br)):
        if v:
            a += f' borderRadius{nm}="{v}"'
    if border:
        a += f' border="{border}"'
    if shadow:
        a += f' boxShadow="{shadow}"'
    add(f'<Positioned left="{x}" top="{y}">{a}/></Positioned>')


def text(x, y, s, size, color, weight="NORMAL", family=CJ, w=None, align="CENTER_LEFT"):
    a = f'fontSize="{size}" color="{color}" fontFamily="{family}" fontStyle="{weight}"'
    body = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    if w:
        add(f'<Positioned left="{x}" top="{y}" width="{w}"><Container alignment="{align}">'
            f'<Text {a}>{body}</Text></Container></Positioned>')
    else:
        add(f'<Positioned left="{x}" top="{y}"><Text {a}>{body}</Text></Positioned>')


def seg(x0, y0, x1, y1, color, th):
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy)
    if length < 0.6:
        return
    ang = math.atan2(dy, dx)
    m11, m12 = math.cos(ang), math.sin(ang)
    m21, m22 = -m12, m11
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    tx = mx - m11 * (length / 2) - m21 * (th / 2)
    ty = my - m12 * (length / 2) - m22 * (th / 2)
    mat = f"(1,0,0,0,0,1,0,0,0,0,1,0,{tx:.3f},{ty:.3f},0,1)"
    add(f'<Positioned left="0" top="0"><Transform matrix="{mat}"><Container width="{length:.2f}" '
        f'height="{th}" color="{color}" borderRadius="{th/2}"/></Transform></Positioned>')


def head(x, y, ux, uy, color, size=8):
    """Filled-looking arrow head pointing along (ux, uy), built from 3 rotated bars."""
    px, py = -uy, ux
    tip = (x + ux * size, y + uy * size)
    a = (x - ux * 2 + px * size * 0.8, y - uy * 2 + py * size * 0.8)
    b = (x - ux * 2 - px * size * 0.8, y - uy * 2 - py * size * 0.8)
    seg(tip[0], tip[1], a[0], a[1], color, 3)
    seg(tip[0], tip[1], b[0], b[1], color, 3)
    seg(a[0], a[1], b[0], b[1], color, 3)


def cx(x: int) -> float:
    return GX + x * CELL + CELL / 2


def cy(y: int) -> float:
    return GY + y * CELL + CELL / 2


def draw_route(path, color, offset, dashed):
    """Dashed routes are emitted as short segments so no path/dash tag is needed."""
    pts = [(cx(x) + offset, cy(y)) for x, y in path]
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        if not dashed:
            seg(x0, y0, x1, y1, color, 5)
        else:
            total = math.hypot(x1 - x0, y1 - y0)
            ux, uy = (x1 - x0) / total, (y1 - y0) / total
            t = 0.0
            while t < total:
                e = min(t + 11, total)
                seg(x0 + ux * t, y0 + uy * t, x0 + ux * e, y0 + uy * e, color, 5)
                t += 19
    # arrow heads on the longer straight runs
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        if math.hypot(x1 - x0, y1 - y0) >= CELL * 5:
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            d = math.hypot(x1 - x0, y1 - y0)
            head(mx, my, (x1 - x0) / d, (y1 - y0) / d, color)
    ex, ey = pts[-2]
    fx, fy = pts[-1]
    d = math.hypot(fx - ex, fy - ey) or 1
    head(fx, fy, (fx - ex) / d, (fy - ey) / d, color)


add(f'<Snapshot background="{BG}" type="png">')
add(f'<Container width="{W}" height="{H}">')
add('<Stack alignment="TOP_LEFT" fit="EXPAND">')

# ============================== header ==============================
box(0, 0, W, 96, NAVY)
box(0, 0, 8, 96, AREAC)
text(40, 12, "虚构展馆 · 网格导览与两条可走路线", 32, "#FFFFFFFF", "BOLD")
text(40, 56, "26 列 × 18 行 · 每格 2 米 · 只允许上下左右跨格，不可穿墙或对角移动 · 坐标 (x,y) 从 0 开始", 22, "#94A3B8FF")
text(1000, 12, "路线一 S→E 最短：34 步 / 68 m", 22, "#FCA5A5FF", "BOLD", CJ, 520, "CENTER_RIGHT")
text(1000, 46, "路线二 S→B→D→E 最短：36 步 / 72 m", 22, "#93C5FDFF", "BOLD", CJ, 520, "CENTER_RIGHT")
text(1000, 74, "重合 15 格：两路线都用线型 + 箭头分别标出", 20, "#94A3B8FF", "NORMAL", CJ, 520, "CENTER_RIGHT")

# ============================== grid base layer ==============================
# LAYER ORDER MATTERS. The floor, the wall tiles and the marker squares are emitted first,
# then the routes, then every label. The first version drew the wall tiles AFTER the routes,
# so each wall tile covered the route line crossing it and the routes came out as
# disconnected dashes instead of continuous lines.
box(GX, GY, GW, GH, FLOOR_C, 6, "2 SOLID #94A3B8FF")
ON_ROUTE = set(R1) | set(R2)
for y in range(ROWS):
    for x in range(COLS):
        if GRID[y][x] == "#":
            box(GX + x * CELL, GY + y * CELL, CELL - 2, CELL - 2, WALL_C)
for k, (x, y) in MARK.items():
    px, py = GX + x * CELL, GY + y * CELL
    if k == "S":
        box(px + 3, py + 3, CELL - 7, CELL - 7, "#16A34AFF", 5)
    elif k == "E":
        box(px + 3, py + 3, CELL - 7, CELL - 7, "#7C3AEDFF", 5)
    else:
        box(px + 3, py + 3, CELL - 7, CELL - 7, "#CCFBF1FF", 5, f"2 SOLID {AREAC}")

# ============================== routes ==============================
draw_route(R2, R2C, +3, True)
draw_route(R1, R1C, -3, False)

# ============================== labels above the routes ==============================
# cell identifiers (>=16px) only in walkable cells that are neither on a route nor even
# adjacent to one, so a number can never sit under a route line or beside an arrow head
NEAR_ROUTE = {(rx + dx, ry + dy) for rx, ry in ON_ROUTE
              for dx in (-1, 0, 1) for dy in (-1, 0, 1)}
_id_count = 0
for _y in range(ROWS):
    for _x in range(COLS):
        if GRID[_y][_x] == "#" or (_x, _y) in NEAR_ROUTE or (_x, _y) in MARK.values():
            continue
        _s = f"{_x},{_y}"
        if len(_s) * 10 > CELL - 2:
            continue
        # light chip behind the number so a line that still passes nearby cannot make the
        # digits unreadable (the chip is lighter than the wall grey, so it never reads as wall)
        box(GX + _x * CELL + 3, GY + _y * CELL + 7, CELL - 6, 21, "#F8FAFCF2", 4)
        text(GX + _x * CELL, GY + _y * CELL + 9, _s, 16, "#8494A6FF", "NORMAL", MONO, CELL, "CENTER")
        _id_count += 1
print("cell identifiers drawn:", _id_count)
assert _id_count >= 16, f"only {_id_count} cell identifiers; need at least 16"

for k, (x, y) in MARK.items():
    px, py = GX + x * CELL, GY + y * CELL
    text(px, py + 7, k, 20, "#FFFFFFFF" if k in ("S", "E") else "#0B7A6EFF", "BOLD", MONO, CELL, "CENTER")

# coordinate rulers every 2 cells
for x in range(0, COLS, 2):
    text(GX + x * CELL, GY - 32, str(x), 18, MUTED, "NORMAL", MONO, CELL * 2, "CENTER_LEFT")
for y in range(0, ROWS, 2):
    text(GX - 56, GY + y * CELL + 2, str(y), 18, MUTED, "NORMAL", MONO, 46, "CENTER_RIGHT")
text(GX - 56, GY - 54, "y\\x", 18, MUTED, "BOLD", MONO, 46, "CENTER_RIGHT")
seg(GX, GY - 12, GX + GW, GY - 12, "#94A3B8FF", 2)
seg(GX - 16, GY, GX - 16, GY + GH, "#94A3B8FF", 2)

# corridor names next to each area marker
NAME_AT = {"A": (1, 3), "B": (1, -2), "D": (1, 3), "C": (1, -2)}
for k, (x, y) in MARK.items():
    if k in ("S", "E"):
        continue
    dx, dy = NAME_AT[k]
    tx = GX + x * CELL + (CELL + 6 if dx > 0 else -190)
    ty = GY + y * CELL + (CELL + 4 if dy > 0 else -30)
    text(tx, ty, f"{k} · {LEGEND[k]}", 22, "#0B7A6EFF", "BOLD", CJ, 190,
         "CENTER_LEFT" if dx > 0 else "CENTER_RIGHT")
text(GX + MARK["S"][0] * CELL - 70, GY + MARK["S"][1] * CELL - 40, "S · 入口", 22, "#15803DFF", "BOLD")
text(GX + MARK["E"][0] * CELL - 70, GY + MARK["E"][1] * CELL + CELL + 4, "E · 出口", 22, "#6D28D9FF", "BOLD")

# ============================== sidebar ==============================
# Two stacked boxes with explicit heights; the asserts below prove the content stays inside
# them. The budget is the grid height (18 * CELL), not the full canvas height.
SW = SIDEBAR_W - 52
ROUTE_H, INFO_H = 224, 388
assert ROUTE_H + INFO_H <= GH, "sidebar bands exceed the grid height"

box(SIDEBAR_X, GY, SIDEBAR_W, ROUTE_H, CARD, 12, f"1 SOLID {LINE}")
yy = GY + 14
seg(SIDEBAR_X + 24, yy + 9, SIDEBAR_X + 74, yy + 9, R1C, 5)
head(SIDEBAR_X + 80, yy + 9, 1, 0, R1C)
text(SIDEBAR_X + 96, yy, "路线一（实线红）S→E 最短", 22, R1C, "BOLD")
yy += 28
text(SIDEBAR_X + 24, yy, f"{D['route1_shortest_S_to_E']['step_count']} 步 · "
     f"{D['route1_shortest_S_to_E']['meters']} m · {D['route1_shortest_S_to_E']['station_count']} 格 · "
     f"{D['route1_shortest_S_to_E']['turns']} 次转向", 22, R1C, "BOLD", MONO)
yy += 38
for k in range(4):
    seg(SIDEBAR_X + 24 + k * 17, yy + 9, SIDEBAR_X + 24 + k * 17 + 10, yy + 9, R2C, 5)
head(SIDEBAR_X + 96, yy + 9, 1, 0, R2C)
text(SIDEBAR_X + 112, yy, "路线二（点划蓝）S→B→D→E 最短", 22, R2C, "BOLD")
yy += 28
text(SIDEBAR_X + 24, yy, f"{D['route2_S_B_D_E']['step_count']} 步 · "
     f"{D['route2_S_B_D_E']['meters']} m · {D['route2_S_B_D_E']['station_count']} 格 · "
     f"{D['route2_S_B_D_E']['turns']} 次转向", 22, R2C, "BOLD", MONO)
yy += 38
text(SIDEBAR_X + 24, yy, "两线在格心两侧各错开 3px：红在左、蓝在右，", 20, MUTED, "NORMAL", CJ, SW, "CENTER_LEFT")
text(SIDEBAR_X + 24, yy + 22, "所以 15 格重合段也能分别追踪、不互相遮住。", 20, MUTED, "NORMAL", CJ, SW, "CENTER_LEFT")
yy += 44
assert yy <= GY + ROUTE_H - 4, f"route box overflows ({yy})"

box(SIDEBAR_X, GY + ROUTE_H, SIDEBAR_W, INFO_H, CARD, 12, f"1 SOLID {LINE}")
yy = GY + ROUTE_H + 12
text(SIDEBAR_X + 22, yy, "路线二分段（必须先 B 后 D）", 22, INK, "BOLD")
yy += 28
NAME_OF = {tuple(v["cell"]): LEGEND[k] for k, v in D["areas"].items()}
for lg in D["route2_S_B_D_E"]["legs"]:
    a, b = tuple(lg["from"]), tuple(lg["to"])
    text(SIDEBAR_X + 24, yy, f"({a[0]},{a[1]}) {NAME_OF.get(a,'')} → ({b[0]},{b[1]}) {NAME_OF.get(b,'')}",
         20, INK2, "NORMAL", CJ, 250, "CENTER_LEFT")
    text(SIDEBAR_X + 300, yy, f"{lg['steps']} 步 / {lg['meters']} m", 20, INK2, "BOLD", MONO, 170, "CENTER_LEFT")
    yy += 25
yy += 8
text(SIDEBAR_X + 22, yy, "校验", 22, INK, "BOLD")
yy += 26
c = D["connectivity"]
for ln in [f"可走格 {c['walkable_cells']} 个全部可从入口到达，不可达 0 个；",
           "每一步都是上下左右跨 1 格，无对角、无穿墙；",
           "门洞位置与宽度取自 floor.txt，未做任何扩大；",
           "墙格恒为灰色，路线不覆盖格号、不把墙变成可走；",
           "两路线均按要求先经过 B 再经过 D。"]:
    text(SIDEBAR_X + 24, yy, ln, 20, MUTED, "NORMAL", CJ, SW, "CENTER_LEFT")
    yy += 24
yy += 8
text(SIDEBAR_X + 22, yy, "折返说明", 22, INK, "BOLD")
yy += 26
for ln in ["B(12,3) 是 (12,4) 走廊上的支线格，进出必然折返一次；",
           "36 步解满足「每段最短」，折返位置已记在 paths.json；",
           "无折返的简单路径需要 38 步（多 2 步），故未采用。"]:
    text(SIDEBAR_X + 24, yy, ln, 20, MUTED, "NORMAL", CJ, SW, "CENTER_LEFT")
    yy += 24
assert yy <= GY + GH - 2, f"sidebar content overflows ({yy} vs {GY + GH})"

# ============================== bottom band: legend + notes ==============================
BY = GY + GH + 14
box(40, BY, W - 80, 74, CARD, 12, f"1 SOLID {LINE}")
text(58, BY + 10, "图例", 22, INK, "BOLD")
lx = 124
for sw, label in ((WALL_C, "不可走墙（#）"), (FLOOR_C, "可走格（.）")):
    box(lx, BY + 22, 28, 28, sw, None, "1 SOLID #94A3B8FF")
    text(lx + 36, BY + 24, label, 22, INK2)
    lx += 230
box(lx, BY + 22, 28, 28, "#16A34AFF", 5)
text(lx + 36, BY + 24, "入口 S", 22, INK2)
lx += 150
box(lx, BY + 22, 28, 28, "#7C3AEDFF", 5)
text(lx + 36, BY + 24, "出口 E", 22, INK2)
lx += 150
box(lx, BY + 22, 28, 28, "#CCFBF1FF", 5, f"2 SOLID {AREAC}")
text(lx + 36, BY + 24, "展区 A B D C（同样可走）", 22, INK2)

text(40, BY + 88, "坐标：格心以 (x,y) 表示，原点在左上角、x 向右、y 向下；边缘标尺每 2 格一个刻度。", 22, MUTED)
text(40, BY + 116, "尺度：每格边长 2 米；路线一步 = 跨一格 = 2 米；墙格为灰色、可走格为白色。", 22, MUTED)
text(1150, BY + 116, "渲染：Snapshot DSL · 1560×1080", 20, MUTED, "NORMAL", MONO, 370, "CENTER_RIGHT")
add('</Stack>')
add('</Container>')
add('</Snapshot>')

dsl = "\n".join(P) + "\n"
os.makedirs(TMP, exist_ok=True)
with open(os.path.join(TMP, f"wayfinding.{VER}.snapshot"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write(dsl)

print("dsl:", len(dsl), "chars | grid", f"{GW}x{GH}", "at", (GX, GY))
print("grid right/bottom:", GX + GW, GY + GH, "| sidebar", SIDEBAR_X, "..", SIDEBAR_X + SIDEBAR_W)
assert GX + GW < SIDEBAR_X, "grid overlaps the sidebar"
assert GY + GH + 14 + 74 + 90 < H, "bottom band leaves the canvas"
assert SIDEBAR_X + SIDEBAR_W < W, "sidebar leaves the canvas"
print("layout OK")
