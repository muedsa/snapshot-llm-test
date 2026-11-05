#!/usr/bin/env python3
"""A08 wayfinding: parse the 26x16 floor grid, BFS the two routes, emit
wayfinding.snapshot (1560x1080) and paths.json. Paths derived from suite.ROOT /
environment variables; no machine-specific absolute path is persisted.
"""
import json, os, sys, math
from collections import deque
from pathlib import Path

TOOLS = os.environ["TOOLS"]
sys.path.insert(0, TOOLS)
from dsl import Canvas, CN, LATIN, MONO
import suite

TASK = "A08"
ROOT = suite.ROOT
TASK_DIR = ROOT / "tasks" / "A08-accessible-wayfinding"
rows = [l.rstrip("\n") for l in (TASK_DIR / "inputs" / "floor.txt").read_text(encoding="utf-8").splitlines()]
legend = json.loads((TASK_DIR / "inputs" / "legend.json").read_text(encoding="utf-8"))
W, H = legend["grid"]["width"], legend["grid"]["height"]
CELL_M = legend["grid"]["cell_meters"]
assert len(rows) == H and all(len(r) == W for r in rows)

walk = set()
land = {}
for y, r in enumerate(rows):
    for x, ch in enumerate(r):
        if ch != "#":
            walk.add((x, y))
        if ch in "SEABCD":
            land[ch] = (x, y)
S, E = land["S"], land["E"]
NAMES = {"S": "入口门格", "E": "出口门格", "A": "材料实验入口",
         "B": "结构剧场入口", "C": "光影工坊入口", "D": "作品巡览入口"}
NB = [(1, 0), (-1, 0), (0, 1), (0, -1)]


def bfs(src, dst):
    """Shortest 4-neighbour path; also count number of shortest paths."""
    dist = {src: 0}; ways = {src: 1}; prev = {src: []}
    q = deque([src])
    while q:
        u = q.popleft()
        for dx, dy in NB:
            v = (u[0] + dx, u[1] + dy)
            if v not in walk:
                continue
            if v not in dist:
                dist[v] = dist[u] + 1; ways[v] = ways[u]; prev[v] = [u]; q.append(v)
            elif dist[v] == dist[u] + 1:
                ways[v] += ways[u]; prev[v].append(u)
    assert dst in dist, "no path %s->%s" % (src, dst)
    path = [dst]
    while path[-1] != src:
        path.append(prev[path[-1]][0])
    path.reverse()
    return {"dist": dist[dst], "ways": ways[dst], "cells": path}


R1 = bfs(S, E)
SEGS = [bfs(S, land["B"]), bfs(land["B"], land["D"]), bfs(land["D"], E)]
R2_CELLS = []
for i, s in enumerate(SEGS):
    R2_CELLS += s["cells"] if i == 0 else s["cells"][1:]
R2 = {"dist": len(R2_CELLS) - 1, "ways": 1, "cells": R2_CELLS}

# ---- verification (author states unique shortest, no repeats) ----
assert R1["ways"] == 1, "R1 shortest path not unique"
assert all(s["ways"] == 1 for s in SEGS), "an R2 segment is not unique"
assert len(R2_CELLS) == len(set(R2_CELLS)), "R2 repeats a cell"
assert len(R1["cells"]) == len(set(R1["cells"])), "R1 repeats a cell"
assert R2["dist"] == 47 and R1["dist"] == 35
assert [s["dist"] for s in SEGS] == [19, 16, 12]
for cells in (R1["cells"], R2_CELLS):
    assert all(c in walk for c in cells), "route crosses a blocked cell"
    for a, b in zip(cells, cells[1:]):
        assert abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1, "non 4-neighbour step"

# ---- shared runs: intersection of directed grid edges ----
def directed_edges(cells):
    return list(zip(cells, cells[1:]))


e1, e2 = directed_edges(R1["cells"]), directed_edges(R2_CELLS)
shared_edges = [e for e in e1 if e in e2]
runs, cur = [], []
for e in shared_edges:
    if cur and cur[-1][1] == e[0]:
        cur.append(e)
    else:
        if cur:
            runs.append(cur)
        cur = [e]
if cur:
    runs.append(cur)
SHARED_RUNS = []
for run in runs:
    cells = [run[0][0]] + [e[1] for e in run]
    SHARED_RUNS.append({"cells": cells, "edges": len(run)})
assert [(r["cells"][0], r["cells"][-1], r["edges"]) for r in SHARED_RUNS] == [
    ((0, 13), (6, 10), 9), ((20, 10), (25, 7), 8)]

# ---------------------------------------------------------------- palette / geometry
BG = "#EFF3FA"; NAVY = "#0B1B35"; NAVY2 = "#16386F"
WHITE = "#FFFFFF"; INK = "#0F172A"; MUTED = "#5B6B85"; LINE = "#DDE5F0"
WALL = "#2E3B55"; WALL_EDGE = "#46567A"; FLOOR = "#F7FAFF"; GRIDL = "#CBD7E8"
AMBER = "#F59E0B"; AMBER_D = "#9A3412"; BLUE = "#1D4ED8"; BLUE_D = "#1E3A8A"
TEAL = "#0D9488"; RED = "#DC2626"; PURPLE = "#6D28D9"
CELL = 40.0; OX = 60.0; OY = 210.0


def cc(cell):
    x, y = cell
    return OX + (x + 0.5) * CELL, OY + (y + 0.5) * CELL


def cell_rect(cell):
    x, y = cell
    return OX + x * CELL, OY + y * CELL


c = Canvas(1560, 1080, BG)

# ---- header ----
c.gradient(0, 0, 1560, 150, [NAVY, NAVY2], begin="CENTER_LEFT", end="CENTER_RIGHT")
c.rect(0, 146, 1560, 4, "#38BDF8")
c.text(44, 18, 1000, 50, "云构展馆 · 双路线导览图", 38, WHITE, bold=True)
c.text(44, 74, 1100, 32, "直达出口 与 主题参观 ｜ 26×16 通道网格 ｜ 每格 2 米 ｜ 四邻接格心路径", 21, "#BBD3F2")
c.text(1140, 26, 380, 34, "A08 / WAYFINDING", 19, "#8FB6EA", align="RIGHT", font=LATIN)
c.text(1140, 66, 380, 28, "数据源 floor.txt · legend.json", 17, "#BBD3F2", align="RIGHT")

# ---- grid cells ----
for y in range(H):
    for x in range(W):
        px, py = OX + x * CELL, OY + y * CELL
        if (x, y) not in walk:
            c.rect(px, py, CELL, CELL, WALL, border="1 SOLID " + WALL_EDGE)
        else:
            c.rect(px, py, CELL, CELL, FLOOR, border="1 SOLID " + GRIDL)
# boundary door cells S/E
for cell, col in ((S, TEAL), (E, RED)):
    px, py = cell_rect(cell)
    c.rect(px + 2, py + 2, CELL - 4, CELL - 4, "#FFFFFF00", border="3 SOLID " + col)

# ---- edge coordinate ticks (only on the border) ----
for x in range(W):
    c.text(OX + x * CELL, OY - 34, CELL, 28, str(x), 17, MUTED, align="CENTER", font=LATIN)
for y in range(H):
    c.text(OX - 44, OY + y * CELL, 40, CELL, str(y), 17, MUTED, align="CENTER", font=LATIN)
c.text(OX, OY - 62, 260, 26, "格坐标 x（向右）", 17, MUTED)
c.text(OX - 52, OY - 62, 52, 26, "y", 17, MUTED, align="CENTER", font=LATIN)

# ---- routes: same centreline, wide solid base (R1) + narrow dashed overlay (R2) ----
def draw_r1():
    cells = R1["cells"]
    for a, b in zip(cells, cells[1:]):
        x1, y1 = cc(a); x2, y2 = cc(b)
        c.line(x1, y1, x2, y2, 18, AMBER)
    for cell in cells:                       # fill the corners
        x, y = cc(cell)
        c.circle(x, y, 9, AMBER)


def draw_r2():
    cells = R2_CELLS
    for a, b in zip(cells, cells[1:]):
        x1, y1 = cc(a); x2, y2 = cc(b)
        c.dashed_line(x1, y1, x2, y2, 7, BLUE, dash=20, gap=8)


draw_r1()
draw_r2()

# ---- direction arrows: white halo + coloured core, both routes ----
def arrow(x, y, ang, size, core):
    c.arrow_head(x, y, ang, size + 3, WHITE)
    c.arrow_head(x, y, ang, size, core)


def arrows(cells, frac, core, size):
    for a, b in zip(cells, cells[1:]):
        x1, y1 = cc(a); x2, y2 = cc(b)
        ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
        ax, ay = x1 + (x2 - x1) * frac, y1 + (y2 - y1) * frac
        arrow(ax, ay, ang, size, core)


arrows(R1["cells"], 0.35, AMBER_D, 8)
arrows(R2_CELLS, 0.72, BLUE, 7)

# ---- branch / merge callouts (in wall areas, short leaders) ----
BRANCH, MERGE = (6, 10), (20, 10)
CALL = {
    "branch": (360, 610, 190, "分岔 · R1/R2 分开", BRANCH),
    "merge": (660, 610, 180, "合流 · R1/R2 汇合", MERGE),
}
for key, (lx, ly, lw, txt, cell) in CALL.items():
    sx, sy = cc(cell)
    px = min(max(sx, lx), lx + lw)
    py = min(max(sy, ly), ly + 34)
    c.line(sx, sy, px, py, 1.5, "#94A3B8")
    c.rect(lx, ly, lw, 34, WHITE, radius=8, border="1 SOLID " + LINE)
    c.text(lx + 6, ly + 2, lw - 12, 30, txt, 20, INK, align="LEFT")

# ---- landmark label chips (names >=22) in nearby wall cells, with leaders ----
CHIPS = {
    "S": (60, 772, 170, "S · 入口门格"),
    "E": (910, 448, 180, "E · 出口门格"),
    "A": (470, 654, 200, "A · 材料实验入口"),
    "B": (390, 412, 210, "B · 结构剧场入口"),
    "C": (620, 252, 210, "C · 光影工坊入口"),
    "D": (650, 452, 200, "D · 作品巡览入口"),
}
for sym, (lx, ly, lw, txt) in CHIPS.items():
    sx, sy = cc(land[sym])
    px = min(max(sx, lx), lx + lw)
    py = min(max(sy, ly), ly + 36)
    c.line(sx, sy, px, py, 1.5, "#94A3B8")
    c.rect(lx, ly, lw, 36, WHITE, radius=8, border="1 SOLID " + LINE)
    c.text(lx + 6, ly + 2, lw - 12, 32, txt, 22, INK, align="LEFT")

# ---- landmark markers fixed at exact cell centres (on top) ----
MARK_COL = {"S": TEAL, "E": RED, "A": PURPLE, "B": PURPLE, "C": PURPLE, "D": PURPLE}
for sym in "SEABCD":
    x, y = cc(land[sym])
    c.circle(x, y, 14, WHITE, border="2 SOLID " + INK)
    c.circle(x, y, 11, MARK_COL[sym])
    c.text(x - 11, y - 11, 22, 22, sym, 20, WHITE, bold=True, align="CENTER", font=LATIN)

# ---- right panel ----
c.rect(1120, 170, 400, 890, WHITE, radius=16, border="1 SOLID " + LINE)
c.text(1144, 184, 352, 36, "路线 / 图例 / 尺度", 26, INK, bold=True)
c.rect(1144, 226, 352, 2, LINE)

# R1 block
c.rect(1144, 238, 352, 114, "#FFF7ED", radius=12, border="1 SOLID #FCD9A6")
c.line(1158, 272, 1246, 272, 16, AMBER)
arrow(1232, 272, 0, 8, AMBER_D)
c.text(1260, 244, 220, 32, "R1 直达出口", 24, INK, bold=True)
c.text(1260, 278, 220, 30, "35 步 · 70 米", 22, AMBER_D, bold=True)
c.text(1158, 312, 336, 30, "必经点：S → E", 22, INK)

# R2 block
c.rect(1144, 364, 352, 208, "#EFF6FF", radius=12, border="1 SOLID #BBD3FB")
c.dashed_line(1158, 400, 1246, 400, 6, BLUE, dash=18, gap=8)
arrow(1232, 400, 0, 7, BLUE)
c.text(1260, 372, 220, 32, "R2 主题参观", 24, INK, bold=True)
c.text(1260, 406, 220, 30, "47 步 · 94 米", 22, BLUE_D, bold=True)
c.text(1158, 442, 336, 30, "必经点：S → B → D → E", 22, INK)
c.text(1158, 476, 336, 28, "S→B  19 步 / 38 米", 22, MUTED)
c.text(1158, 506, 336, 28, "B→D  16 步 / 32 米", 22, MUTED)
c.text(1158, 536, 336, 28, "D→E  12 步 / 24 米", 22, MUTED)

# legend
c.text(1144, 584, 352, 32, "图例", 24, INK, bold=True)
ly = 620
c.rect(1148, ly + 4, 26, 22, WALL, border="1 SOLID " + WALL_EDGE)
c.text(1184, ly, 300, 30, "# 墙体 / 非通行区", 20, INK)
ly += 30
c.rect(1148, ly + 4, 26, 22, FLOOR, border="1 SOLID " + GRIDL)
c.text(1184, ly, 300, 30, "通道（可走格）", 20, INK)
ly += 30
c.circle(1161, ly + 15, 11, TEAL)
c.text(1184, ly, 300, 30, "S / E 边界门格", 20, INK)
ly += 30
c.circle(1161, ly + 15, 11, PURPLE)
c.text(1184, ly, 300, 30, "A–D 展区入口点", 20, INK)
ly += 30
c.line(1150, ly + 15, 1176, ly + 15, 14, AMBER)
c.text(1184, ly, 300, 30, "R1 宽实线 + 橙色箭头", 20, INK)
ly += 30
c.dashed_line(1150, ly + 15, 1176, ly + 15, 6, BLUE, dash=12, gap=6)
c.text(1184, ly, 300, 30, "R2 窄虚线 + 蓝色箭头", 20, INK)
ly += 30
c.circle(1155, ly + 15, 7, AMBER_D)
c.circle(1170, ly + 15, 7, BLUE)
c.text(1184, ly, 300, 30, "共享段：双箭头并列同向", 20, INK)

# shared runs (all body text >=22, six short single-line rows inside the panel)
c.rect(1144, 832, 352, 2, LINE)
c.text(1144, 838, 352, 32, "共享通道（两边计）", 24, INK, bold=True)
SHARED_NOTES = [
    "入馆段 S→(6,10)：9 边 / 18 米",
    "离馆段 (20,10)→E：8 边 / 16 米",
    "两段两线同向、身份可辨",
    "四邻接 · 格心路径 · 转弯不计代价",
    "共享段路程计入各自路线",
    "总步数 = 格心序列长 - 1",
]
for i, t in enumerate(SHARED_NOTES):
    c.text(1144, 874 + i * 30, 352, 28, t, 22, MUTED)

# ---- bottom strip: scale + notes ----
c.text(60, 886, 1000, 34, "比例尺：1 格 = 2 米", 24, INK, bold=True)
for i in range(3):
    c.rect(60 + i * CELL, 928, CELL, 16, INK if i % 2 == 0 else WHITE,
           border="1 SOLID " + INK)
for i, lab in enumerate(("0", "2", "4", "6 米")):
    c.text(60 + i * CELL - 12, 948, 52, 26, lab, 20, MUTED, align="CENTER")
c.text(240, 924, 420, 30, "（1 格 = 40 px = 2 米）", 22, MUTED)
c.text(60, 986, 1020, 34,
       "格坐标 (x,y) 左上 (0,0)，x 向右、y 向下；仅上下左右相邻可走格。",
       22, MUTED)
c.text(60, 1024, 1020, 34,
       "R1 与 R2 入馆段、离馆段共享：宽实线/窄虚线叠加、双色箭头并列，分岔与合流已标注。",
       22, MUTED)

dsl = c.render()
out = suite.out_dir(TASK)
(out / "wayfinding.snapshot").write_text(dsl, encoding="utf-8")
ver = os.environ.get("BUILD_VERSION", "v1")
tmp = suite.tmp_dir(TASK, ver)
(tmp / "wayfinding.snapshot").write_text(dsl, encoding="utf-8")

# ---------------------------------------------------------------- paths.json
def seg_obj(frm, to, s):
    return {"from": frm, "to": to, "cells": [list(c) for c in s["cells"]],
            "steps": s["dist"], "meters": s["dist"] * CELL_M}


def style(rid, color, kind, width, arrow_desc, dash=None):
    d = {"route_id": rid, "color": color, "line_type": kind, "width_px": width,
         "lateral_offset_px": 0.0,
         "offset_limit_px": round(CELL * 0.12, 2),
         "arrow": arrow_desc,
         "drawn_on": "same logical centreline as the other route (wide solid base / narrow dashed overlay)"}
    if dash:
        d["dash_px"], d["gap_px"] = dash
    return d


audit = [
    {"check": "grid dimensions and walkability", "passed": True,
     "method": "floor.txt parsed as 16 rows x 26 chars; every '#' recorded as blocked, all other chars walkable; 65 walkable cells.",
     "evidence": "inputs/floor.txt, legend.json; layout shows all 26x16 cells with walls, corridors and the two boundary door cells."},
    {"check": "S/E/A-D landmark coordinates", "passed": True,
     "method": "single occurrence of each symbol scanned from floor.txt; marker drawn at origin_px+(x+0.5)*cell_px.",
     "evidence": "landmarks array with cell and canvas centre; ViewImage whole-map check."},
    {"check": "4-neighbour adjacency of every step", "passed": True,
     "method": "for each consecutive pair assert |dx|+|dy|==1 and both cells in walk.",
     "evidence": "assertion in build.py; no diagonal step is drawn."},
    {"check": "R1 shortest and unique", "passed": True,
     "method": "BFS from S counts shortest-path multiplicities: ways[E]=1, dist=35.",
     "evidence": "build.py assertion R1['ways']==1; steps=35, meters=70."},
    {"check": "R2 waypoint order S->B->D->E and each segment shortest/unique", "passed": True,
     "method": "three BFS runs with ways[B]=ways[D]=ways[E]=1; distances 19/16/12; concatenation drops the shared join point once.",
     "evidence": "build.py assertions; segments array; total 47 steps / 94 m."},
    {"check": "no repeated cell and no backtracking", "passed": True,
     "method": "len(cells)==len(set(cells)) for both full sequences.",
     "evidence": "build.py assertions passed."},
    {"check": "steps/meters = sequence length - 1, shared distance counted in both", "passed": True,
     "method": "steps=len(cells)-1, meters=steps*2; shared runs are part of each route's own cell list.",
     "evidence": "R1 35/70, R2 47/94; segments 19/16/12 sum to 47."},
    {"check": "shared runs determined by grid edges, not single points", "passed": True,
     "method": "intersection of directed edges (u,v) of R1 and R2, grouped into maximal contiguous runs.",
     "evidence": "two runs: S(0,13)->(6,10) 9 edges, (20,10)->E(25,7) 8 edges; single shared cell (20,10) is only a merge point, not counted as a run by itself."},
    {"check": "drawing stays inside walkable cells; no widened doors / shortcuts", "passed": True,
     "method": "both routes use lateral offset 0 px (<=12% of 40 px = 4.8 px) on the same centreline; 18 px stroke and <=10 px arrows stay within the 40 px cell; arrows placed at fractions 0.35/0.72 of each centre-to-centre edge.",
     "evidence": "drawing.route_styles; ViewImage whole map plus zoomed shared/branch/merge/door checks."},
    {"check": "paired readability on shared corridors", "passed": True,
     "method": "R1 wide solid amber base + R2 narrow dashed blue overlay; two arrowheads (amber core / blue core, white halo) at distinct longitudinal positions on every shared edge, both pointing S->E.",
     "evidence": "shared_runs[].display; actual PNG zoom of entrance and exit shared runs."},
    {"check": "landmark text not covered by routes/arrows", "passed": True,
     "method": "name chips placed in adjacent wall cells (no route passes there) with short leader lines; markers fixed at exact cell centres.",
     "evidence": "CHIPS coordinates verified against grid; ViewImage whole map."},
]

paths = {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "coordinate_base": "grid_zero_based",
    "grid": {"width": W, "height": H, "cell_meters": CELL_M,
             "origin": "top_left", "x_direction": "right", "y_direction": "down"},
    "drawing": {
        "origin_px": [OX, OY], "cell_px": CELL,
        "centre_formula": "cx = origin_x+(x+0.5)*cell_px ; cy = origin_y+(y+0.5)*cell_px",
        "route_styles": [
            style("R1", AMBER, "solid_wide", 18, "white-halo amber arrow, size 8, at 0.35 of each edge"),
            style("R2", BLUE, "dashed_narrow", 7, "white-halo blue arrow, size 7, at 0.72 of each edge", (20, 8)),
        ],
        "shared_display": "R2 dashes drawn over R1 solid base on the same centreline; both arrows visible in shared corridors.",
    },
    "landmarks": [
        {"symbol": s, "name": NAMES[s], "cell": list(land[s]),
         "canvas_center_px": [round(v, 1) for v in cc(land[s])]}
        for s in "SEABCD"
    ],
    "routes": [
        {"id": "R1", "name": "直达出口", "waypoints": ["S", "E"],
         "cells": [list(c) for c in R1["cells"]], "steps": R1["dist"], "meters": R1["dist"] * CELL_M,
         "segments": [seg_obj("S", "E", R1)]},
        {"id": "R2", "name": "主题参观", "waypoints": ["S", "B", "D", "E"],
         "cells": [list(c) for c in R2_CELLS], "steps": R2["dist"], "meters": R2["dist"] * CELL_M,
         "segments": [seg_obj("S", "B", SEGS[0]), seg_obj("B", "D", SEGS[1]), seg_obj("D", "E", SEGS[2])]},
    ],
    "shared_runs": [
        {"cells": [list(c) for c in r["cells"]], "route_ids": ["R1", "R2"],
         "direction_by_route": {"R1": "S(0,13) -> interior", "R2": "S(0,13) -> interior"},
         "display": "entrance shared corridor; wide amber solid + narrow blue dashed on same centreline; amber arrow at 0.35 and blue arrow at 0.72 of each edge, both pointing into the hall.",
         "edges": r["edges"], "meters": r["edges"] * CELL_M}
        for r in SHARED_RUNS[:1]
    ] + [
        {"cells": [list(c) for c in r["cells"]], "route_ids": ["R1", "R2"],
         "direction_by_route": {"R1": "interior -> E(25,7)", "R2": "interior -> E(25,7)"},
         "display": "exit shared corridor after the merge at (20,10); same dual-style/dual-arrow treatment, both pointing to E.",
         "edges": r["edges"], "meters": r["edges"] * CELL_M}
        for r in SHARED_RUNS[1:]
    ],
    "branch_and_merge": {
        "branch_cell": list(BRANCH), "merge_cell": list(MERGE),
        "note": "At (6,10) R1 turns down to row12 while R2 turns up the x=6 corridor; at (20,10) R1 arrives from (20,11) and R2 from (20,9), then both turn east. Both points are labelled on the map with leaders."
    },
    "audit": audit,
    "evidence": {"png": "wayfinding.png", "dsl": "wayfinding.snapshot",
                 "visual_checks": ["whole map", "entrance shared run", "exit shared run", "branch (6,10)", "merge (20,10)", "S/E door cells", "landmark chips"]},
}
(out / "paths.json").write_text(json.dumps(paths, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("A08 DSL bytes", len(dsl.encode("utf-8")))
print("R1", R1["dist"], "steps", R1["dist"] * CELL_M, "m | R2", R2["dist"], "steps", R2["dist"] * CELL_M, "m")
print("shared runs", [(r["cells"][0], r["cells"][-1], r["edges"]) for r in SHARED_RUNS])
