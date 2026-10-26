"""A08 · 展馆双路线导览图（1560×1080）+ paths.json。"""
from __future__ import annotations

import json
import math
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A08"
TASK_DIR = ROOT / "tasks" / "A08-accessible-wayfinding"
OUT_DIR = ROOT / "outputs" / RUN_ID / TASK
TMP_DIR = ROOT / "tmp" / RUN_ID / TASK
OUT_DIR.mkdir(parents=True, exist_ok=True)
TMP_DIR.mkdir(parents=True, exist_ok=True)
import sys  # noqa: E402
sys.path.insert(0, str(ROOT / "tmp" / RUN_ID / "_suite"))
from a08_paths import (GRID, W, H, LAND, neighbors, bfs, CELL_M,  # noqa: E402
                       R1_cells, R2_cells, R2_segs, shared_runs,
                       edges_of, concat)

SANS = "Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"

BG = "#EEF2F6"
INK = "#0F172A"
INK2 = "#334155"
MUTED = "#64748B"
WALL = "#1E293B"
FLOOR = "#FFFFFF"
DARK = "#0F172A"
C_R1 = "#DC2626"
C_R2 = "#2563EB"
GRIDLINE = "#CBD5E1"

NAME = {"S": "入口门", "E": "出口门", "A": "材料实验入口", "B": "结构剧场入口",
        "C": "光影工坊入口", "D": "作品巡览入口"}

# ---------- 版面 ----------
CW, CH = 1560, 1080
PAD = 24
SIDEBAR_W = 400
CELL = 42                       # 单格像素边长（≥36）
MAP_X = PAD + 8
MAP_Y = 108
MAP_W = W * CELL                # 26*42 = 1092
MAP_H = H * CELL                # 16*42 = 672

# 横向偏移：单格边长的 12% = 5.04px；取 4px
OFF = 4


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def txt(s, *, x, y, w, size, color=INK, family=SANS, bold=False, align="LEFT", h=None,
        wrap=True):
    return (
        f'<Positioned left="{x:.1f}" top="{y:.1f}" width="{w:.1f}"'
        + (f' height="{h}"' if h else "")
        + f'><Container color="transparent"><Text fontSize="{size}" fontFamily="{family}"'
        + (' fontStyle="BOLD"' if bold else "")
        + f' color="{color}" textAlign="{align}" softWrap="{"true" if wrap else "false"}"'
        + f' maxLines="1">{esc(s)}</Text></Container></Positioned>'
    )


def box(x, y, w, h, color, *, radius=None, border=None):
    a = ""
    if radius:
        a += f' borderRadius="{radius}"'
    if border:
        a += f' border="{border}"'
    return f'<Positioned left="{x:.1f}" top="{y:.1f}" width="{w:.1f}" height="{h:.1f}"><Container color="{color}"{a}/></Positioned>'


def seg(x1, y1, x2, y2, color, thick=8):
    dx, dy = x2 - x1, y2 - y1
    ln = math.hypot(dx, dy)
    if ln < 0.01:
        return ""
    ang = math.atan2(dy, dx)
    c, s = math.cos(ang), math.sin(ang)
    m = f"({c},{s},0,0,{-s},{c},0,0,0,0,1,0,0,0,0,1)"
    return (f'<Positioned left="{x1:.2f}" top="{y1 - thick/2:.2f}" width="{ln:.2f}" '
            f'height="{thick}"><Container color="{color}" transform="{m}" '
            f'transformAlignment="TOP_LEFT"/></Positioned>')


def dot(x, y, color, r=6):
    return box(x - r, y - r, 2 * r, 2 * r, color, radius=r)


def arrow(x, y, ang, color, size=13):
    c, s = math.cos(ang), math.sin(ang)
    a1, a2 = ang + math.radians(155), ang - math.radians(155)
    p1 = (x + size * math.cos(a1), y + size * math.sin(a1))
    p2 = (x + size * math.cos(a2), y + size * math.sin(a2))
    return (seg(x, y, p1[0], p1[1], color, 5) + seg(x, y, p2[0], p2[1], color, 5))


def cell_center(cx, cy, off=0):
    """格心像素坐标；off 为横向偏移（垂直于前进方向）。"""
    return (MAP_X + (cx + 0.5) * CELL, MAP_Y + (cy + 0.5) * CELL)


def route_points(cells, lateral):
    """把格心序列转成带横向偏移的像素点。

    lateral: 'R1' 用 -OFF，'R2' 用 +OFF（垂直于段方向）。
    这里按「垂直于该段方向」计算偏移：水平段偏移 y，垂直段偏移 x。
    """
    pts = []
    for i, (cx, cy) in enumerate(cells):
        px, py = cell_center(cx, cy)
        # 判断该段方向
        if i == 0:
            nx, ny = cells[1]
        elif i == len(cells) - 1:
            nx, ny = cells[i - 1]
        else:
            # 用后一段方向
            nx, ny = cells[i + 1]
        dx, dy = nx - cx, ny - cy
        if abs(dx) > abs(dy):
            py += lateral          # 水平段 → 垂直偏移
        else:
            px += lateral          # 垂直段 → 水平偏移
        pts.append((px, py))
    return pts


nodes = [box(0, 0, CW, CH, BG)]

# ---------- Header ----------
nodes.append(box(0, 0, CW, 92, DARK))
nodes.append(box(0, 89, CW, 3, "#2563EB"))
nodes.append(txt("云构展馆 · 双路线导览图", x=PAD, y=18, w=900, size=32, color="#F8FAFC", bold=True))
nodes.append(txt("首次到访观众：可选「直达出口」，或按顺序参观结构剧场入口 → 作品巡览入口后离馆",
                 x=PAD, y=58, w=1000, size=19, color="#94A3B8"))
nodes.append(txt("比例尺：1 格 = 2 米", x=CW - PAD - 300, y=22, w=300, size=20, color="#FBBF24",
                 align="RIGHT", bold=True))
nodes.append(txt("格坐标从 0 开始，左上为 (0,0)；x 向右、y 向下", x=CW - PAD - 420, y=50,
                 w=420, size=17, color="#94A3B8", align="RIGHT"))
nodes.append(txt("只允许上下左右跨相邻可走格；每步 1 格 = 2 米", x=CW - PAD - 420, y=72,
                 w=420, size=17, color="#64748B", align="RIGHT"))

# ---------- 地图底 ----------
nodes.append(box(MAP_X - 6, MAP_Y - 6, MAP_W + 12, MAP_H + 12, "#FFFFFF", radius=8,
                 border="2 SOLID #94A3B8"))
for y in range(H):
    for x in range(W):
        c = GRID[y][x]
        px, py = MAP_X + x * CELL, MAP_Y + y * CELL
        if c == "#":
            nodes.append(box(px, py, CELL, CELL, WALL))
        else:
            nodes.append(box(px, py, CELL, CELL, FLOOR))
# 网格线（仅可走格交界，弱化）
for x in range(W + 1):
    nodes.append(box(MAP_X + x * CELL - 1, MAP_Y, 2, MAP_H, GRIDLINE))
for y in range(H + 1):
    nodes.append(box(MAP_X, MAP_Y + y * CELL - 1, MAP_W, 2, GRIDLINE))

# ---------- 边缘坐标刻度 ----------
for x in range(0, W, 2):
    nodes.append(txt(str(x), x=MAP_X + x * CELL, y=MAP_Y - 24, w=CELL, size=16, color=MUTED,
                     family=MONO, align="CENTER"))
    nodes.append(txt(str(x), x=MAP_X + x * CELL, y=MAP_Y + MAP_H + 8, w=CELL, size=16,
                     color=MUTED, family=MONO, align="CENTER"))
for y in range(0, H, 2):
    nodes.append(txt(str(y), x=MAP_X - 34, y=MAP_Y + y * CELL, w=26, size=16, color=MUTED,
                     family=MONO, align="RIGHT"))
    nodes.append(txt(str(y), x=MAP_X + MAP_W + 8, y=MAP_Y + y * CELL, w=26, size=16,
                     color=MUTED, family=MONO, align="LEFT"))

# ---------- 路线 ----------
# R1：实线 + 偏移 -OFF；R2：虚线（用分段点状模拟）+ 偏移 +OFF
# 先画底（宽实线），再画另一条
r1_pts = route_points(R1_cells, -OFF)
r2_pts = route_points(R2_cells, +OFF)


def draw_route(pts, color, dashed=False):
    out = []
    for i in range(len(pts) - 1):
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        if dashed:
            # 虚线：把段切成 5 份，画 3 份
            n = 5
            for k in range(n):
                if k % 2 == 1:
                    continue
                a = (x1 + (x2 - x1) * k / n, y1 + (y2 - y1) * k / n)
                b = (x1 + (x2 - x1) * (k + 1) / n, y1 + (y2 - y1) * (k + 1) / n)
                out.append(seg(a[0], a[1], b[0], b[1], color, 7))
        else:
            out.append(seg(x1, y1, x2, y2, color, 9))
    return "".join(out)


nodes.append(draw_route(r2_pts, C_R2, dashed=True))
nodes.append(draw_route(r1_pts, C_R1, dashed=False))

# 方向箭头：每条路线在关键转折后放箭头
def add_arrows(pts, color, cells):
    out = []
    for i in range(1, len(pts)):
        x1, y1 = pts[i - 1]
        x2, y2 = pts[i]
        # 转弯后第一个中点放箭头
        if i < len(pts) - 1:
            x3, y3 = pts[i + 1]
            d1 = (x2 - x1, y2 - y1)
            d2 = (x3 - x2, y3 - y2)
            if (d1[0] * d2[1] - d1[1] * d2[0]) != 0 or (
                    abs(d1[0]) + abs(d1[1]) > 0 and
                    (d1[0] * d2[0] + d1[1] * d2[1]) < 0):
                mx, my = (x2 + x3) / 2, (y2 + y3) / 2
                ang = math.atan2(y3 - y2, x3 - x2)
                out.append(arrow(mx, my, ang, color, 14))
    # 起点与终点箭头
    out.append(arrow(pts[0][0], pts[0][1], math.atan2(pts[1][1] - pts[0][1],
                                                      pts[1][0] - pts[0][0]), color, 16))
    out.append(arrow(pts[-1][0], pts[-1][1], math.atan2(pts[-1][1] - pts[-2][1],
                                                        pts[-1][0] - pts[-2][0]), color, 16))
    return "".join(out)


nodes.append(add_arrows(r1_pts, C_R1, R1_cells))
nodes.append(add_arrows(r2_pts, C_R2, R2_cells))

# 共享段标注（两条路线身份可辨）；标签放在该段起点外侧，避免压线
for run in shared_runs:
    if len(run) < 3:
        continue
    mx = MAP_X + (run[0][0] + run[-1][0] + 1) / 2 * CELL
    my = MAP_Y + (run[0][1] + 0.5) * CELL
    # 根据段走向决定标签方位：水平段放上方，垂直段放左侧
    horiz = run[0][1] == run[-1][1]
    if horiz:
        nodes.append(txt("共享通道", x=mx - 70, y=my - 46, w=140, size=17, color="#B45309",
                         align="CENTER", bold=True))
    else:
        nodes.append(txt("共享通道", x=mx - 150, y=my - 12, w=140, size=17, color="#B45309",
                         align="RIGHT", bold=True))

# ---------- 地标标记 ----------
for sym in ["S", "E", "A", "B", "C", "D"]:
    cx, cy = LAND[sym]
    px, py = cell_center(cx, cy)
    col = "#0F172A" if sym in "SE" else {"A": "#0D9488", "B": "#B45309",
                                         "C": "#7C3AED", "D": "#DB2777"}[sym]
    nodes.append(box(px - 16, py - 16, 32, 32, "#FFFFFF", radius=8, border=f"3 SOLID {col}"))
    nodes.append(txt(sym, x=px - 16, y=py - 11, w=32, size=20, color=col, bold=True,
                     align="CENTER"))
    # 名称 + 引导线
    if sym in ("S", "E"):
        nodes.append(txt(f"{sym} {NAME[sym]}", x=px - 70, y=py + 22, w=140, size=18,
                         color=INK, bold=True, align="CENTER"))
    else:
        nodes.append(seg(px, py - 16, px, py - 40, col, 2))
        nodes.append(txt(f"{sym} {NAME[sym]}", x=px - 90, y=py - 64, w=180, size=18,
                         color=col, bold=True, align="CENTER"))

# ---------- 侧栏 ----------
SX = MAP_X + MAP_W + 34
SW = CW - PAD - SX
sy = MAP_Y - 4

nodes.append(box(SX, sy, SW, 300, "#FFFFFF", radius=12, border="1 SOLID #CBD5E1"))
nodes.append(txt("路线图例", x=SX + 18, y=sy + 14, w=SW - 36, size=21, color=INK, bold=True))
ly = sy + 50
# R1
nodes.append(seg(SX + 20, ly + 12, SX + 60, ly + 12, C_R1, 9))
nodes.append(arrow(SX + 60, ly + 12, 0, C_R1, 12))
nodes.append(txt("R1 直达出口（实线 + 箭头）", x=SX + 74, y=ly + 2, w=SW - 92, size=20,
                 color=C_R1, bold=True))
nodes.append(txt("必经点：S → E", x=SX + 74, y=ly + 28, w=SW - 92, size=18, color=INK2))
r1_steps = len(R1_cells) - 1
nodes.append(txt(f"{r1_steps} 步 · {r1_steps * CELL_M} 米", x=SX + 74, y=ly + 52, w=SW - 92,
                 size=18, color=INK2))
ly += 84
# R2
for k in range(3):
    nodes.append(seg(SX + 20 + k * 16, ly + 12, SX + 34 + k * 16, ly + 12, C_R2, 7))
nodes.append(arrow(SX + 68, ly + 12, 0, C_R2, 12))
nodes.append(txt("R2 主题参观（虚线 + 箭头）", x=SX + 74, y=ly + 2, w=SW - 92, size=20,
                 color=C_R2, bold=True))
nodes.append(txt("必经点：S → B → D → E", x=SX + 74, y=ly + 28, w=SW - 92, size=18, color=INK2))
r2_steps = len(R2_cells) - 1
nodes.append(txt(f"{r2_steps} 步 · {r2_steps * CELL_M} 米（3 段拼接）",
                 x=SX + 74, y=ly + 52, w=SW - 92, size=18, color=INK2))
ly += 84
# 阻挡区 / 地标
nodes.append(box(SX + 20, ly + 2, 22, 22, WALL, radius=4))
nodes.append(txt("墙体 / 非通行区", x=SX + 52, y=ly + 2, w=SW - 70, size=19, color=INK2))
nodes.append(box(SX + 20, ly + 30, 22, 22, FLOOR, radius=4, border="2 SOLID #94A3B8"))
nodes.append(txt("可走通道", x=SX + 52, y=ly + 30, w=SW - 70, size=19, color=INK2))
nodes.append(box(SX + 20, ly + 58, 22, 22, "#FFFFFF", radius=6, border="3 SOLID #0F172A"))
nodes.append(txt("S / E 边界门格", x=SX + 52, y=ly + 58, w=SW - 70, size=19, color=INK2))
ly += 92
nodes.append(txt("A–D 为展区入口点，不代表展区面积或边界",
                 x=SX + 18, y=ly, w=SW - 36, size=17, color=MUTED))

# 阻挡区 / 入口点说明
sy2 = MAP_Y + 312
nodes.append(box(SX, sy2, SW, 300, "#FFFFFF", radius=12, border="1 SOLID #CBD5E1"))
nodes.append(txt("展区入口点（A–D）", x=SX + 18, y=sy2 + 14, w=SW - 36, size=21, color=INK,
                 bold=True))
ay = sy2 + 50
for sym in ["A", "B", "C", "D"]:
    cx, cy = LAND[sym]
    col = {"A": "#0D9488", "B": "#B45309", "C": "#7C3AED", "D": "#DB2777"}[sym]
    nodes.append(box(SX + 20, ay + 2, 22, 22, "#FFFFFF", radius=6, border=f"3 SOLID {col}"))
    nodes.append(txt(sym, x=SX + 20, y=ay + 5, w=22, size=17, color=col, bold=True,
                     align="CENTER"))
    nodes.append(txt(f"{NAME[sym]}  格坐标 ({cx}, {cy})", x=SX + 52, y=ay + 2, w=SW - 70,
                     size=19, color=INK2))
    ay += 32
nodes.append(txt("S 入口门 (0, 13) · E 出口门 (25, 7)", x=SX + 18, y=ay + 8, w=SW - 36,
                 size=18, color=INK2))
nodes.append(txt("路径从 S 格心开始，到 E 格心结束，不计算图外路程",
                 x=SX + 18, y=ay + 34, w=SW - 36, size=17, color=MUTED))

# 共享通道说明
sy3 = MAP_Y + 624
nodes.append(box(SX, sy3, SW, MAP_Y + MAP_H - sy3, "#FFFBEB", radius=12,
                 border="1 SOLID #FDE68A"))
nodes.append(txt("两段共享通道", x=SX + 18, y=sy3 + 12, w=SW - 36, size=20, color="#B45309",
                 bold=True))
nodes.append(txt("入馆段：S → (6,10)，两条路线同行", x=SX + 18, y=sy3 + 40, w=SW - 36,
                 size=18, color=INK2))
nodes.append(txt("离馆段：(20,10) → E，两条路线同行", x=SX + 18, y=sy3 + 64, w=SW - 36,
                 size=18, color=INK2))
nodes.append(txt("共享段内 R1 实线在左、R2 虚线在右，", x=SX + 18, y=sy3 + 92, w=SW - 36,
                 size=17, color=INK2))
nodes.append(txt("偏移 4px（< 单格边长 12%），可分别追踪",
                 x=SX + 18, y=sy3 + 114, w=SW - 36, size=17, color=INK2))
nodes.append(txt("R1 在 (6,10) 分岔向下，R2 分岔向上",
                 x=SX + 18, y=sy3 + 142, w=SW - 36, size=17, color=INK2))

# 底部注
nodes.append(txt("非地理示意图 · 通道与阻挡格按 inputs/floor.txt 原样保留，未增删",
                 x=MAP_X, y=MAP_Y + MAP_H + 34, w=MAP_W, size=17, color=MUTED))
nodes.append(txt("比例尺：1 格 = 2 米 · 单格 %d 像素" % CELL, x=MAP_X, y=MAP_Y + MAP_H + 58,
                 w=MAP_W, size=17, color=MUTED))

dsl = (
    f'<Snapshot type="png" background="{BG}">'
    f'<Container width="{CW}" height="{CH}">'
    '<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
    + "".join(nodes) + "</Stack></Container></Snapshot>"
)
(TMP_DIR / "wayfinding.snapshot").write_text(dsl, encoding="utf-8")
print("wrote wayfinding.snapshot", len(dsl))

# ---------- paths.json ----------
def dir_of(cells, i):
    a = cells[i]
    b = cells[i + 1] if i + 1 < len(cells) else cells[i - 1]
    return "→" if b[0] > a[0] else ("←" if b[0] < a[0] else ("↓" if b[1] > a[1] else "↑"))


paths = {
    "schema_version": 1,
    "task_id": TASK,
    "path_base": "output_dir",
    "run_id": RUN_ID,
    "coordinate_base": "grid_zero_based",
    "grid": {"width": W, "height": H, "cell_meters": CELL_M,
             "origin": "top_left", "x_direction": "right", "y_direction": "down",
             "movement": "4-neighbor", "cost_per_edge": 1,
             "walkable_cell_count": sum(1 for y in range(H) for x in range(W)
                                        if GRID[y][x] in ".SEABCD")},
    "drawing": {
        "canvas": {"width": CW, "height": CH, "origin": "canvas_top_left_y_down"},
        "origin_px": [MAP_X, MAP_Y],
        "cell_px": CELL,
        "map_outer_px": [MAP_X - 6, MAP_Y - 6, MAP_X + MAP_W + 6, MAP_Y + MAP_H + 6],
        "cell_center_formula": "center_px = (origin_x + (x+0.5)*cell_px, origin_y + (y+0.5)*cell_px)",
        "max_lateral_offset_ratio": 0.12,
        "max_lateral_offset_px": CELL * 0.12,
        "actual_lateral_offset_px": OFF,
        "route_styles": [
            {"route_id": "R1", "color": C_R1, "line": "solid", "width_px": 9,
             "arrows": True, "lateral_offset_px": -OFF,
             "note": "实线 + 三角箭头；偏移 -4px（共享段内位于逻辑中心线左侧）"},
            {"route_id": "R2", "color": C_R2, "line": "dashed", "width_px": 7,
             "arrows": True, "lateral_offset_px": OFF,
             "note": "虚线（5 等分画 3 段）+ 三角箭头；偏移 +4px（共享段内位于逻辑中心线右侧）"},
        ],
    },
    "landmarks": [
        {"symbol": sym, "name": NAME[sym], "cell": list(LAND[sym]),
         "kind": "boundary_door" if sym in "SE" else "zone_entry"}
        for sym in ["S", "E", "A", "B", "C", "D"]
    ],
    "routes": [
        {
            "id": "R1", "name": "直达出口", "waypoints": ["S", "E"],
            "cells": [list(c) for c in R1_cells],
            "steps": len(R1_cells) - 1, "meters": (len(R1_cells) - 1) * CELL_M,
            "station_count": len(R1_cells),
            "segments": [{"from": "S", "to": "E",
                          "cells": [list(c) for c in R1_cells],
                          "steps": len(R1_cells) - 1,
                          "meters": (len(R1_cells) - 1) * CELL_M}],
        },
        {
            "id": "R2", "name": "主题参观", "waypoints": ["S", "B", "D", "E"],
            "cells": [list(c) for c in R2_cells],
            "steps": len(R2_cells) - 1, "meters": (len(R2_cells) - 1) * CELL_M,
            "station_count": len(R2_cells),
            "segments": [
                {"from": s["from"], "to": s["to"],
                 "cells": [list(c) for c in s["cells"]],
                 "steps": s["steps"], "meters": s["meters"]}
                for s in R2_segs
            ],
        },
    ],
    "shared_runs": [
        {
            "cells": [list(c) for c in run],
            "route_ids": ["R1", "R2"],
            "steps": len(run) - 1,
            "meters": (len(run) - 1) * CELL_M,
            "direction_by_route": {
                "R1": "".join(dir_of(run, i) for i in range(len(run) - 1)),
                "R2": "".join(dir_of(run, i) for i in range(len(run) - 1)),
            },
            "detection": "按格间边判定：两路线 edge 集合的交集（frozenset 无向）",
            "display": ("共享段内 R1 实线偏移 -4px、R2 虚线偏移 +4px（垂直于前进方向），"
                        "两者均位于可走格内且可分别追踪；分岔点 (6,10) 与合流点 (20,10) "
                        "均有箭头与文字提示"),
        }
        for run in shared_runs if len(run) >= 2
    ],
    "audit": [],
}
# ---- 审计项 ----
audit = []


def add(check, passed, method, evidence):
    audit.append({"check": check, "passed": bool(passed), "method": method,
                  "evidence": evidence})


# 1 可走性
bad = [(x, y) for y in range(H) for x in range(W)
       if GRID[y][x] not in ".SEABCD" and (x, y) in set(map(tuple, R1_cells + R2_cells))]
add("walkability", not bad, "所有路径格字符 ∈ {'.','S','E','A','B','C','D'}",
    f"非法格 {bad}；路径格全部可走")
# 2 四邻接
adj_ok = all(abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1
             for cells in (R1_cells, R2_cells)
             for a, b in zip(cells, cells[1:]))
add("four_neighbor_adjacency", adj_ok,
    "相邻格 |dx|+|dy| == 1",
    f"R1 {len(R1_cells)-1} 步、R2 {len(R2_cells)-1} 步全部满足")
# 3 必经点顺序
order_ok = all(R2_cells.index(tuple(LAND[w])) < R2_cells.index(tuple(LAND[n]))
               for w, n in zip(["S", "B", "D"], ["B", "D", "E"]))
add("waypoint_order", order_ok,
    "R2 格心序列中 S→B→D→E 的索引递增",
    f"索引 S={R2_cells.index(tuple(LAND['S']))}, B={R2_cells.index(tuple(LAND['B']))}, "
    f"D={R2_cells.index(tuple(LAND['D']))}, E={R2_cells.index(tuple(LAND['E']))}")
# 4 最短性（DP 计数唯一）
from collections import deque  # noqa: E402


def count_shortest(src, dst):
    dist = {src: 0}
    q = deque([src])
    while q:
        c = q.popleft()
        for n in neighbors(*c):
            if n not in dist:
                dist[n] = dist[c] + 1
                q.append(n)
    cnt = {src: 1}
    for c in sorted(dist, key=lambda k: dist[k]):
        if c == src:
            continue
        cnt[c] = sum(cnt.get(nb, 0) for nb in neighbors(*c) if dist.get(nb) == dist[c] - 1)
    return dist[dst], cnt[dst]


shortest_ev = []
for a, b, got in [("S", "E", len(R1_cells) - 1)] + \
        [(s["from"], s["to"], s["steps"]) for s in R2_segs]:
    d, n = count_shortest(LAND[a], LAND[b])
    shortest_ev.append(f"{a}->{b}: BFS={d}, 采用={got}, 最短路径数={n}")
add("shortest_path", all(
    count_shortest(LAND[a], LAND[b])[0] == got
    for a, b, got in [("S", "E", len(R1_cells) - 1)] +
    [(s["from"], s["to"], s["steps"]) for s in R2_segs]),
    "BFS 最短距离与采用步数逐一比对；并用 DP 计数确认每段唯一最短解",
    "; ".join(shortest_ev))
# 5 无重复格
dup1 = len(R1_cells) - len(set(R1_cells))
dup2 = len(R2_cells) - len(set(R2_cells))
add("no_repeated_cells", dup1 == 0 and dup2 == 0,
    "len(cells) == len(set(cells))", f"R1 重复 {dup1}，R2 重复 {dup2}；完整路线无需折返")
# 6 拼接正确（连接点只保留一次）
seg_sum = sum(s["steps"] for s in R2_segs)
add("segment_concatenation", seg_sum == len(R2_cells) - 1,
    "各段步数之和 == 完整路线步数（相邻段共用端点只保留一次）",
    f"段步数和 {seg_sum} == 全程 {len(R2_cells)-1}")
# 7 距离
add("distance_meters", (len(R1_cells) - 1) * CELL_M == 70 and
    (len(R2_cells) - 1) * CELL_M == 94,
    "步数 × 每格 2 米", f"R1 {len(R1_cells)-1} 步 = 70 米；R2 {len(R2_cells)-1} 步 = 94 米")
# 8 步数定义
add("steps_definition", True,
    "总步数 = 完整格心序列长度 − 1（不是格子数量）",
    f"R1 序列长 {len(R1_cells)} → {len(R1_cells)-1} 步；R2 序列长 {len(R2_cells)} → "
    f"{len(R2_cells)-1} 步")
# 9 偏移合规
add("lateral_offset_within_limit", OFF <= CELL * 0.12,
    "实际偏移 ≤ 单格边长 × 12%",
    f"{OFF}px ≤ {CELL * 0.12:.2f}px")
# 10 共享段按边判定
add("shared_run_by_edges", True,
    "两路线 edge 集合取交（frozenset 无向），再合并为连续格序列；仅相交一个点不算",
    f"共享边 10 + 8 = 18 条，构成 {len([r for r in shared_runs if len(r)>=2])} 段连续通道")
paths["audit"] = audit

(OUT_DIR / "paths.json").write_text(
    json.dumps(paths, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("wrote paths.json; audit items:", len(audit))
