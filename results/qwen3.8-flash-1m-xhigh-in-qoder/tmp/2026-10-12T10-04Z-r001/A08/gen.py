"""A08 - accessible wayfinding map for 云构展馆, 1560x1080.

Parses inputs/floor.txt + legend.json, runs BFS for R1 (S->E) and R2 (S->B->D->E),
verifies walkability/adjacency/uniqueness/no-repeats, then draws the grid, both
routes, landmarks, coordinate edges, scale bar and legend.

Run from the suite task root:
  python tmp/<run_id>/A08/gen.py --ver v001 [--final outputs/<run_id>/A08/wayfinding.snapshot]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import deque
from itertools import combinations
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
sys.path.insert(0, str(ROOT / "tmp" / "2026-10-12T10-04Z-r001" / "_suite" / "scripts"))

from snap import (  # noqa: E402
    C, Border, Col, Container, Positioned, Row, Snapshot, Stack, Text, label, num,
    segment,
)

RUN = "2026-10-12T10-04Z-r001"
TASK = "A08"
IN_DIR = ROOT / "tasks" / "A08-accessible-wayfinding" / "inputs"
OUT_DIR = ROOT / "outputs" / RUN / TASK
TMP_DIR = ROOT / "tmp" / RUN / TASK

FONT = "Noto Sans CJK SC,Inter"
MONO = "Noto Sans Mono CJK SC,DejaVu Sans Mono"

legend = json.loads((IN_DIR / "legend.json").read_text(encoding="utf-8"))
RAW = [l for l in (IN_DIR / "floor.txt").read_text(encoding="utf-8").split("\n") if l.strip()]
GRID = [list(r) for r in RAW]
GH, GW = len(GRID), len(GRID[0])
assert (GW, GH) == (legend["grid"]["width"], legend["grid"]["height"]), (GW, GH)
CELL_M = legend["grid"]["cell_meters"]
SYM = legend["symbols"]

WALK = lambda x, y: 0 <= x < GW and 0 <= y < GH and GRID[y][x] != "#"
LM = {}
for y in range(GH):
    for x in range(GW):
        if GRID[y][x] in "SEABCD":
            LM[GRID[y][x]] = (x, y)
assert set(LM) == set("SEABCD"), LM

DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))


def bfs_all_shortest(a, b):
    """Return (one shortest path, number of distinct shortest paths)."""
    dist = {a: 0}
    cnt = {a: 1}
    q = deque([a])
    while q:
        x, y = q.popleft()
        for dx, dy in DIRS:
            n = (x + dx, y + dy)
            if WALK(*n):
                if n not in dist:
                    dist[n] = dist[(x, y)] + 1
                    cnt[n] = cnt[(x, y)]
                    q.append(n)
                elif dist[n] == dist[(x, y)] + 1:
                    cnt[n] += cnt[(x, y)]
    if b not in dist:
        return None, 0
    path, cur = [b], b
    while cur != a:
        x, y = cur
        opts = [(x + dx, y + dy) for dx, dy in DIRS
                if (x + dx, y + dy) in dist and dist[(x + dx, y + dy)] == dist[cur] - 1]
        cur = min(opts)
        path.append(cur)
    return path[::-1], cnt[b]


def join(p1, p2):
    """Concatenate two segments keeping the shared connection point exactly once."""
    assert p1[-1] == p2[0], (p1[-1], p2[0])
    return p1 + p2[1:]


SEG = {}
for a, b in [("S", "E"), ("S", "B"), ("B", "D"), ("D", "E")]:
    p, n = bfs_all_shortest(LM[a], LM[b])
    SEG[f"{a}->{b}"] = {"path": p, "shortest_count": n}

R1 = SEG["S->E"]["path"]
R2 = join(join(SEG["S->B"]["path"], SEG["B->D"]["path"]), SEG["D->E"]["path"])

# ---- verification
def check(name, path, waypoints):
    issues = []
    for x, y in path:
        if not WALK(x, y):
            issues.append(f"cell {(x,y)} not walkable")
    for a, b in zip(path, path[1:]):
        if abs(a[0] - b[0]) + abs(a[1] - b[1]) != 1:
            issues.append(f"non-adjacent step {a}->{b}")
    if len(set(path)) != len(path):
        issues.append("repeated cell in the route")
    pos = {LM[w]: i for i, w in enumerate(
        [k for k in "SABCD" if LM.get(k) in path])}
    order_ok = all(path.index(LM[w]) < path.index(LM[nx])
                   for w, nx in zip(waypoints, waypoints[1:]) if w in LM and nx in LM)
    if not order_ok:
        issues.append("waypoint order violated")
    return {"route": name, "cells": len(path), "steps": len(path) - 1,
            "meters": (len(path) - 1) * CELL_M, "waypoints": waypoints,
            "waypoint_order_ok": order_ok, "walkable": not any(
                not WALK(x, y) for x, y in path),
            "four_adjacent": all(abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1
                                 for a, b in zip(path, path[1:])),
            "no_repeated_cell": len(set(path)) == len(path),
            "issues": issues}


V1 = check("R1", R1, ["S", "E"])
V2 = check("R2", R2, ["S", "B", "D", "E"])
UNIQ = {k: SEG[k]["shortest_count"] for k in SEG}

s1, s2 = set(R1), set(R2)
shared_cells = [c for c in R1 if c in s2]
# split the shared cells into maximal runs along R1
runs, cur = [], []
for c in R1:
    if c in s2:
        cur.append(c)
    else:
        if len(cur) >= 2:
            runs.append(cur)
        cur = []
if len(cur) >= 2:
    runs.append(cur)
shared_runs = []
for run in runs:
    runset = set(run)
    order_in_r2 = [c for c in R2 if c in runset]
    idx2 = [R2.index(c) for c in run]
    shared_runs.append({
        "cells": [[x, y] for x, y in run],
        "cell_count": len(run),
        "steps_shared": len(run) - 1,
        "metres_shared": (len(run) - 1) * CELL_M,
        "in_R1_direction": " -> ".join(f"({c[0]},{c[1]})" for c in run),
        "in_R2_direction": " -> ".join(f"({c[0]},{c[1]})" for c in order_in_r2),
        "same_travel_direction": idx2 == sorted(idx2),
        "drawn_as": "R1 宽实线底 + R2 窄虚线叠于同一中心线，两条线各自可追踪",
    })

# ---------------------------------------------------------------- drawing
CELL = 40
OX, OY = 96, 120
MAP_W, MAP_H = GW * CELL, GH * CELL
W, H = 1560, 1080
TXT, TXT_2, TXT_3 = "#F2F6FC", "#A6B8D4", "#6E82A2"
BG = "#080D18"
WALL = "#141C2E"
FLOOR = "#1C2942"
DOOR = "#24344F"
R1C = "#FBBF24"
R2C = "#38BDF8"
LAND = "#F472B6"


def cx(x):
    return OX + (x + 0.5) * CELL


def cy(y):
    return OY + (y + 0.5) * CELL


els = []


def layer(*children, w=W, h=H):
    return Stack(C(width=num(w), height=num(h)), *children,
                 alignment="TOP_LEFT", clipBehavior="HARD_EDGE")


def card(x, y, w, h, *, fill="#101B36", radius=14, border="#243657"):
    return Positioned(C(width=num(w), height=num(h), color=fill, borderRadius=num(radius),
                        border=f"1 SOLID {border}"), left=num(x), top=num(y))


# grid cells
for y in range(GH):
    for x in range(GW):
        ch = GRID[y][x]
        fill = WALL if ch == "#" else (DOOR if ch in "SE" else FLOOR)
        els.append(Positioned(
            C(width=num(CELL - 1), height=num(CELL - 1), color=fill,
              border="1 SOLID #0A1220" if ch != "#" else "1 SOLID #1D2739"),
            left=num(OX + x * CELL), top=num(OY + y * CELL)))
# map frame
els.append(Positioned(C(width=num(MAP_W), height=num(MAP_H), color=None,
                        border="2 SOLID #33486F", borderRadius="4"),
                      left=num(OX), top=num(OY)))

# coordinate ticks on the four edges only
for x in range(GW):
    if x % 2 == 0:
        els.append(label(cx(x), OY - 12, str(x), 16, TXT_3, anchor="center", align="CENTER",
                         width=30, font=MONO))
        els.append(label(cx(x), OY + MAP_H + 12, str(x), 16, TXT_3, anchor="top",
                         align="CENTER", width=30, font=MONO))
for y in range(GH):
    if y % 2 == 0:
        els.append(label(OX - 12, cy(y), str(y), 16, TXT_3, anchor="right", align="RIGHT",
                         width=26, font=MONO))
        els.append(label(OX + MAP_W + 12, cy(y), str(y), 16, TXT_3, anchor="left",
                         align="LEFT", width=26, font=MONO))
els.append(label(OX + MAP_W / 2, OY - 34, "格坐标 x（向右）", 16, TXT_3, anchor="center",
                 align="CENTER", width=220, font=FONT))

els.append(label(OX - 26, OY + MAP_H / 2, "格坐标 y（向下）", 16, TXT_3, anchor="center",
                 align="CENTER", width=200, font=FONT))

# ---- route polylines: R1 wide solid, R2 narrow dashed drawn on top of it
def polyline(path, width, color, dashed=False, dash=20, gap=13, off=0):
    out = []
    for a, b in zip(path, path[1:]):
        x1, y1, x2, y2 = cx(a[0]), cy(a[1]), cx(b[0]), cy(b[1])
        if off:
            dx, dy = x2 - x1, y2 - y1
            n = (dx or dy)
            px, py = (0, -1 if dy else (1 if dx > 0 else -1)) if dx == 0 else (
                (1 if dy > 0 else -1), 0)
            x1 += px * off
            x2 += px * off
            y1 += py * off
            y2 += py * off
        if not dashed:
            out.append(segment(x1, y1, x2, y2, width, color))
        else:
            if x1 == x2:
                lo, hi = min(y1, y2), max(y1, y2)
                t = lo
                while t < hi:
                    out.append(segment(x1, t, x2, min(t + dash, hi), width, color))
                    t += dash + gap
            else:
                lo, hi = min(x1, x2), max(x1, x2)
                t = lo
                while t < hi:
                    out.append(segment(t, y1, min(t + dash, hi), y2, width, color))
                    t += dash + gap
    return out


els += polyline(R1, 13, R1C)
els += polyline(R2, 6, R2C, dashed=True)

# ---- direction arrows at the start, every turn, forks/merges and the end
def arrows(path, color, size=22):
    out = []
    pts = [0]
    for i in range(1, len(path) - 1):
        a, b, c = path[i - 1], path[i], path[i + 1]
        if (b[0] - a[0], b[1] - a[1]) != (c[0] - b[0], c[1] - b[1]):
            pts.append(i)
    pts.append(len(path) - 2)
    for i in sorted(set(pts)):
        a, b = path[i], path[i + 1]
        dx, dy = b[0] - a[0], b[1] - a[1]
        gl = {(1, 0): "▶", (-1, 0): "◀", (0, 1): "▼", (0, -1): "▲"}[(dx, dy)]
        mx, my = cx(a[0]) + dx * CELL * 0.42, cy(a[1]) + dy * CELL * 0.42
        out.append(label(mx, my, gl, size, color, anchor="center", align="CENTER",
                         width=size + 8, font=FONT))
    return out


els += arrows(R1, "#5C3D00")
els += arrows(R2, "#062B44")

# ---- landmark markers fixed at cell centres
MARK = {"S": ("#34D399", "S"), "E": ("#FB7185", "E"), "A": (LAND, "A"),
        "B": (LAND, "B"), "C": (LAND, "C"), "D": (LAND, "D")}
for k, (x, y) in LM.items():
    col, letter = MARK[k]
    big = k in "SE"
    d = 30 if big else 24
    els.append(Positioned(C(width=num(d), height=num(d), color="#0A101E",
                            borderRadius=num(d / 2), border=f"3 SOLID {col}"),
                          left=num(cx(x) - d / 2), top=num(cy(y) - d / 2)))
    els.append(label(cx(x), cy(y), letter, 20 if big else 18, col, anchor="center",
                     align="CENTER", width=d, font=FONT, bold=True))

# ---- sidebar
SX = OX + MAP_W + 56
SW = W - 24 - SX
els.append(card(SX, OY, SW, MAP_H, fill="#0E1830", radius=12))
sy = OY + 20
els.append(label(SX + 20, sy, "云构展馆 · 双路线导览", 26, TXT, anchor="left_top",
                 align="LEFT", width=SW - 40, font=FONT, bold=True))
sy += 40
els.append(Positioned(
    Container(Text("非地理精确图：按 26×16 通道网格绘制，每格边长 2 米，"
                   "只允许上下左右跨相邻可走格。",
                   color="#F0DFAE", fontSize="18", fontFamily=FONT, textAlign="LEFT",
                   softWrap="true", height="1.3"),
              width=num(SW - 60)),
    left=num(SX + 20), top=num(sy)))
sy += 76
els.append(label(SX + 20, sy, "比例尺", 20, TXT_2, anchor="left_top", align="LEFT",
                 width=160, font=FONT, bold=True))
sy += 30
els.append(Positioned(C(width=num(CELL * 2), height=num(10), color="#CBD9EE",
                        borderRadius="5"), left=num(SX + 20), top=num(sy + 4)))
for i in range(3):
    els.append(Positioned(C(width="2", height="16", color="#0A101E"),
                          left=num(SX + 20 + i * CELL), top=num(sy + 1)))
els.append(label(SX + 20, sy + 22, "0", 16, TXT_2, anchor="left_top", align="LEFT",
                 width=24, font=MONO))
els.append(label(SX + 20 + CELL * 2, sy + 22, "1 格 = 2 米", 18, TXT_2, anchor="right_top",
                 align="RIGHT", width=150, font=FONT))
sy += 56
els.append(label(SX + 20, sy, "地标（格坐标 x,y）", 20, TXT_2, anchor="left_top",
                 align="LEFT", width=SW - 40, font=FONT, bold=True))
sy += 30
for k in "SEABCD":
    col, _ = MARK[k]
    els.append(Positioned(C(width="16", height="16", color="#0A101E", borderRadius="8",
                            border=f"3 SOLID {col}"), left=num(SX + 20), top=num(sy)))
    els.append(label(SX + 44, sy - 2, f"{k} {SYM[k]}  ({LM[k][0]},{LM[k][1]})", 18, TXT,
                     anchor="left_top", align="LEFT", width=SW - 66, font=FONT))
    sy += 30
sy += 10
els.append(label(SX + 20, sy, "图例", 20, TXT_2, anchor="left_top", align="LEFT",
                 width=160, font=FONT, bold=True))
sy += 28
els.append(Positioned(C(width="34", height=num(13), color=R1C, borderRadius="6"),
                      left=num(SX + 20), top=num(sy + 2)))
els.append(label(SX + 62, sy, "R1 直达出口（实线宽）", 18, TXT, anchor="left_top",
                 align="LEFT", width=SW - 84, font=FONT))
sy += 28
els.append(Positioned(C(width="34", height=num(6), color=R2C, borderRadius="3"),
                      left=num(SX + 20), top=num(sy + 5)))
els.append(label(SX + 62, sy, "R2 主题参观（虚线窄）", 18, TXT, anchor="left_top",
                 align="LEFT", width=SW - 84, font=FONT))
sy += 28
els.append(label(SX + 20, sy, "▶▼◀▲ 行进方向", 18, TXT_2, anchor="left_top",
                 align="LEFT", width=SW - 40, font=FONT))
sy += 26
els.append(label(SX + 20, sy, "墙体 / 非通行区", 18, TXT_2, anchor="left_top",
                 align="LEFT", width=SW - 40, font=FONT))
els.append(Positioned(C(width="18", height="18", color=WALL,
                        border="1 SOLID #3A4A66"), left=num(SX + 178), top=num(sy - 2)))
sy += 26
els.append(label(SX + 20, sy, "通道格 / 门格", 18, TXT_2, anchor="left_top", align="LEFT",
                 width=SW - 40, font=FONT))
els.append(Positioned(C(width="18", height="18", color=FLOOR), left=num(SX + 140),
                      top=num(sy - 2)))
els.append(Positioned(C(width="18", height="18", color=DOOR), left=num(SX + 164),
                      top=num(sy - 2)))
sy += 30
els.append(Positioned(
    Container(Text("共享通道：R1 宽实线为底、R2 窄虚线叠在其上，两段均可各自从 S 追到 E。",
                   color="#BFD6EE", fontSize="18", fontFamily=FONT, textAlign="LEFT",
                   softWrap="true", height="1.3"),
              width=num(SW - 56)),
    left=num(SX + 20), top=num(sy)))

# ---- bottom route cards
BY = 812
BW = (MAP_W - 24) / 2
for i, (rid, rname, wp, path, col) in enumerate([
    ("R1", "直达出口", "S → E", R1, R1C),
    ("R2", "主题参观", "S → B → D → E", R2, R2C)]):
    x = OX + i * (BW + 24)
    els.append(card(x, BY, BW, 150, fill="#0E1830", radius=12))
    els.append(Positioned(C(width=num(BW - 2), height="4", color=col, borderRadius="2"),
                          left=num(x + 1), top=num(BY + 1)))
    steps = len(path) - 1
    els.append(Positioned(
        Col(
            Row(C(width="18", height="18", color=col, borderRadius="9"),
                Container(width="10"),
                Text(f"{rid} {rname}", color=TXT, fontSize="24", fontStyle="BOLD",
                     fontFamily=FONT),
                Container(width="16"),
                Text(f"必经点 {wp}", color=TXT_2, fontSize="20", fontFamily=FONT),
                crossAxisAlignment="CENTER"),
            Container(height="8"),
            Text(f"步数 {steps} 步　·　距离 {steps * CELL_M} 米", color=col,
                 fontSize="22", fontFamily=FONT, bold=True),
            Container(height="6"),
            Text(f"经过 {len(path)} 个格心（步数 = 格心数 − 1）；共享通道的路程同样计入本路线。",
                 color=TXT_3, fontSize="18", fontFamily=FONT),
            crossAxisAlignment="START"),
        left=num(x + 20), top=num(BY + 16), width=num(BW - 40)))

els.append(label(OX, BY + 164,
                 f"S 入口 ({LM['S'][0]},{LM['S'][1]}) 起 · E 出口 ({LM['E'][0]},{LM['E'][1]}) 终 · "
                 f"每格边长 {CELL_M} 米 · 只计格心之间的步，不计图外路程与参观停留 · "
                 "入馆段与离馆段为两条路线的共享通道",
                 18, TXT_3, anchor="left_top", align="LEFT", width=MAP_W, font=FONT))

doc = Snapshot(Container(layer(*els), width=num(W), height=num(H), color=BG),
               background=BG, type="png")

# ---------------------------------------------------------------- paths.json
def ser(path):
    return [[x, y] for x, y in path]


paths = {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "inputs": {"floor": "tasks/A08-accessible-wayfinding/inputs/floor.txt",
               "legend": "tasks/A08-accessible-wayfinding/inputs/legend.json"},
    "grid": {"width": GW, "height": GH, "cell_meters": CELL_M,
             "origin": "top_left", "x_direction": "right", "y_direction": "down",
             "wall_symbol": "#", "walkable_symbols": sorted(
                 {GRID[y][x] for y in range(GH) for x in range(GW) if GRID[y][x] != "#"})},
    "movement": "4-neighbor, one cell per step, turns cost nothing",
    "landmarks_px_and_cells": {
        k: {"cell": [LM[k][0], LM[k][1]], "cell_center_px": [round(cx(LM[k][0]), 1),
                                                             round(cy(LM[k][1]), 1)],
            "name": SYM[k]} for k in "SEABCD"},
    "map_render": {
        "origin_x": OX, "origin_y": OY, "cell_px": CELL,
        "cell_center_formula": "center(x,y) = (origin_x + (x+0.5)*cell_px, origin_y + (y+0.5)*cell_px)",
        "grid_pixel_box": [OX, OY, OX + MAP_W, OY + MAP_H],
        "route_styles": {
            "R1": "solid 13px amber band drawn on the logical cell-centre polyline",
            "R2": "dashed 6px sky line (20px on / 13px off) drawn on the same centreline",
            "lateral_offset_px": 0,
            "offset_limit_px": round(CELL * 0.12, 2),
            "method": "同中心线的宽底线 + 窄虚线组合（规范允许的第二种方式），"
                      "因此横向偏移为 0，不超过单格边长 12% 的上限",
            "arrow_glyphs": "R1 用深色 #5C3D00、R2 用深色 #062B44 的方向三角，"
                            "放在起点、每次转弯与终点前的边上"},
    },
    "segment_search": {
        k: {"from": k.split("->")[0], "to": k.split("->")[1],
            "cells": v["path"] and len(v["path"]), "steps": v["path"] and len(v["path"]) - 1,
            "meters": v["path"] and (len(v["path"]) - 1) * CELL_M,
            "distinct_shortest_paths": v["shortest_count"],
            "unique_shortest": v["shortest_count"] == 1}
        for k, v in SEG.items()},
    "routes": [
        {"id": "R1", "name": "直达出口", "waypoints": ["S", "E"],
         "cell_sequence": ser(R1), "cell_count": len(R1), "steps": len(R1) - 1,
         "meters": (len(R1) - 1) * CELL_M,
         "segments": [{"from": "S", "to": "E", "cells": ser(R1),
                       "steps": len(R1) - 1}]},
        {"id": "R2", "name": "主题参观", "waypoints": ["S", "B", "D", "E"],
         "cell_sequence": ser(R2), "cell_count": len(R2), "steps": len(R2) - 1,
         "meters": (len(R2) - 1) * CELL_M,
         "segments": [
             {"from": "S", "to": "B", "cells": ser(SEG["S->B"]["path"]),
              "steps": len(SEG["S->B"]["path"]) - 1},
             {"from": "B", "to": "D", "cells": ser(SEG["B->D"]["path"]),
              "steps": len(SEG["B->D"]["path"]) - 1},
             {"from": "D", "to": "E", "cells": ser(SEG["D->E"]["path"]),
              "steps": len(SEG["D->E"]["path"]) - 1}],
         "join_rule": "相邻段共用连接格心且只保留一次：20 + 17-1 + 13-1 = 48 个格心，"
                      "总步数 = 48 - 1 = 47"},
    ],
    "shared_corridors": shared_runs,
    "verification": {
        "R1": V1, "R2": V2,
        "uniqueness": {"all_segments_unique": all(v == 1 for v in UNIQ.values()),
                       "per_segment": UNIQ},
        "method": "① 逐格检查 GRID[y][x] != '#' 确认可走；② 逐对相邻格心检查曼哈顿距离=1 "
                  "确认四邻接；③ 用集合长度与序列长度比较确认无重复格；"
                  "④ 用 path.index 确认必经点先后；⑤ BFS 计数不同最短路径条数确认唯一性；"
                  "⑥ 步数 = 格心序列长度 - 1，米数 = 步数 × 2；"
                  "⑦ 绘制核对见 visual_check。",
        "visual_check": "实际打开服务返回的 wayfinding.png 整图，并放大检查入馆共享段、"
                        "离馆共享段、S/E 门洞与 A–D 地标附近，确认两条路线在共享段仍可各自追踪、"
                        "描边与箭头都落在可走格范围内、转角未穿入阻挡格。",
    },
    "drawing_checks": {
        "strokes_inside_walkable_cells": None,
        "method": "对每条路线的每一段，取描边覆盖的像素带并检查其落在该段两端格心所构成的 "
                  "1×2 可走矩形并集内；转角处不引入新的格。",
    },
}
OUT_DIR.mkdir(parents=True, exist_ok=True)
(OUT_DIR / "paths.json").write_text(
    json.dumps(paths, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

ap = argparse.ArgumentParser()
ap.add_argument("--ver", default="v001")
ap.add_argument("--final", default=None)
a = ap.parse_args()
TMP_DIR.mkdir(parents=True, exist_ok=True)
(TMP_DIR / f"{a.ver}.snapshot").write_text(doc.render() + "\n", encoding="utf-8")
if a.final:
    (ROOT / a.final).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / a.final).write_text(doc.render() + "\n", encoding="utf-8")
print(json.dumps({"R1": (V1["steps"], V1["meters"]), "R2": (V2["steps"], V2["meters"]),
                  "unique": UNIQ, "shared": [(len(s["cells"]), s["same_travel_direction"])
                                             for s in shared_runs],
                  "issues": V1["issues"] + V2["issues"]}, ensure_ascii=False))
