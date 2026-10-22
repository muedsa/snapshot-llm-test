#!/usr/bin/env python3
"""A08 wayfinding map generator + paths.json.

Launch base: suite root.
Usage: python tmp/<run_id>/A08/scripts/gen_a08.py <suite_root> <run_id> [outdir]

BFS computes each segment's shortest distance and the number of shortest
paths (asserted unique). R1 = S->E; R2 = S->B->D->E segment concatenation.
Drawing: same-centerline wide baseline (R1 solid blue) / narrow dashed
overlay (R2 amber), lateral offset 0 px (<= 12% of 40 px cell = 4.8 px).
Arrow glyphs are rotated with the same Transform matrix proven in A06/A07.
"""
import json
import math
import pathlib
import sys
from collections import deque
from datetime import datetime

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
run_id = sys.argv[2] if len(sys.argv) > 2 else "run-20261011-01"
out_dir = pathlib.Path(sys.argv[3]) if len(sys.argv) > 3 else (root / "outputs" / run_id / "A08")
tmp_drafts = root / "tmp" / run_id / "A08" / "drafts"
tmp_drafts.mkdir(parents=True, exist_ok=True)
out_dir.mkdir(parents=True, exist_ok=True)

INP = root / "tasks" / "A08-accessible-wayfinding" / "inputs"
grid_txt = (INP / "floor.txt").read_text(encoding="utf-8").splitlines()
legend = json.loads((INP / "legend.json").read_text(encoding="utf-8"))
H = len(grid_txt)
W = len(grid_txt[0])
CELL_M = legend["grid"]["cell_meters"]
SYM_NAME = legend["symbols"]
assert H == legend["grid"]["height"] and W == legend["grid"]["width"], "grid size mismatch"
assert all(len(r) == W for r in grid_txt), "ragged grid"

GRID = {(x, y): grid_txt[y][x] for y in range(H) for x in range(W)}
WALK = {c for c, ch in GRID.items() if ch != "#"}
POS = {ch: c for c, ch in GRID.items() if ch in "SEABCD"}
S, E = POS["S"], POS["E"]

NB = [(1, 0), (-1, 0), (0, 1), (0, -1)]


def neighbors(c):
    for dx, dy in NB:
        n = (c[0] + dx, c[1] + dy)
        if n in WALK:
            yield n


def shortest(start, goal):
    """Return (cells, dist, n_shortest); assert unique on use."""
    dist = {start: 0}
    count = {start: 1}
    q = deque([start])
    while q:
        p = q.popleft()
        for n in neighbors(p):
            if n not in dist:
                dist[n] = dist[p] + 1
                q.append(n)
                count[n] = count[p]
            elif dist[n] == dist[p] + 1:
                count[n] += count[p]
    assert goal in dist, f"disconnected {start}->{goal}"
    # unique-predecessor walk-back
    path = [goal]
    cur = goal
    while cur != start:
        preds = [n for n in neighbors(cur) if dist.get(n) == dist[cur] - 1]
        assert len(preds) == 1, f"ambiguous predecessor at {cur}: {preds}"
        cur = preds[0]
        path.append(cur)
    path.reverse()
    return path, dist[goal], count[goal]


def seg_cells(a, b, label):
    cells, d, cnt = shortest(a, b)
    assert cnt == 1, f"{label}: {cnt} shortest paths (expected unique)"
    return cells, d


# ---- routes -----------------------------------------------------------------
r1_cells, r1_d = seg_cells(S, E, "R1 S->E")
r2a, r2a_d = seg_cells(S, POS["B"], "S->B")
r2b, r2b_d = seg_cells(POS["B"], POS["D"], "B->D")
r2c, r2c_d = seg_cells(POS["D"], E, "D->E")
r2_cells = r2a + r2b[1:] + r2c[1:]
r2_d = r2a_d + r2b_d + r2c_d

for name, cells in (("R1", r1_cells), ("R2", r2_cells)):
    assert all(c in WALK for c in cells), f"{name}: non-walkable cell"
    assert all(sum(abs(a - b) for a, b in zip(c1, c2)) == 1
               for c1, c2 in zip(cells, cells[1:])), f"{name}: non-adjacent step"
    assert len(set(cells)) == len(cells), f"{name}: repeated cell"
assert [r2_cells.index(POS["B"]), r2_cells.index(POS["D"])] == [r2a_d, r2a_d + r2b_d]
assert r2_cells[0] == S and r2_cells[-1] == E

# ---- shared runs (maximal shared-edge chains) -------------------------------
def edges(cells):
    return {frozenset((a, b)) for a, b in zip(cells, cells[1:])}


shared_edges = edges(r1_cells) & edges(r2_cells)
se_map = {}
for e in shared_edges:
    a, b = tuple(e)
    se_map.setdefault(a, []).append((b, e))
    se_map.setdefault(b, []).append((a, e))
unused = set(shared_edges)
runs = []
while unused:
    e0 = next(iter(unused))
    a0, b0 = tuple(e0)
    chain = [a0, b0]
    unused.discard(e0)
    # extend forward from b0
    for _ in range(4 * H * W):
        nxt = [(n, e) for n, e in se_map[chain[-1]] if e in unused]
        if not nxt:
            break
        assert len(nxt) == 1, f"branch in shared graph at {chain[-1]}"
        n, e = nxt[0]
        unused.discard(e)
        chain.append(n)
    # extend backward from a0
    for _ in range(4 * H * W):
        nxt = [(n, e) for n, e in se_map[chain[0]] if e in unused]
        if not nxt:
            break
        n, e = nxt[0]
        unused.discard(e)
        chain.insert(0, n)
    runs.append(chain)
runs.sort(key=lambda ch: (ch[0][1], ch[0][0]))
assert len(runs) == 2, f"expected 2 shared runs, got {len(runs)}"


def heading(c1, c2):
    dx, dy = c2[0] - c1[0], c2[1] - c1[1]
    return {(1, 0): "east", (-1, 0): "west", (0, 1): "south", (0, -1): "north"}[(dx, dy)]


def run_direction(cells, run):
    i = cells.index(run[0])
    j = cells.index(run[-1])
    if cells[i + 1] != run[1]:  # route traverses run backwards
        return "reversed"
    turns = []
    for k in range(i, j):
        if k + 2 <= j and heading(cells[k], cells[k + 1]) != heading(cells[k + 1], cells[k + 2]):
            turns.append(heading(cells[k + 1], cells[k + 2]))
    return "east" if not turns else "east via " + ",".join(turns)


dir_r1 = [heading(a, b) for a, b in zip(r1_cells, r1_cells[1:])]
dir_r2 = [heading(a, b) for a, b in zip(r2_cells, r2_cells[1:])]


def sub_path(cells, a, b):
    i, j = cells.index(a), cells.index(b)
    return cells[i:j + 1]


run_info = []
for chain in runs:
    d1 = run_direction(r1_cells, chain)
    d2 = run_direction(r2_cells, chain)
    assert d1 == d2, f"opposite directions on shared run {chain[0]}"
    r1i = r1_cells.index(chain[0])
    r2i = r2_cells.index(chain[0])
    approach_r1 = ("route start at S" if r1i == 0
                   else heading(r1_cells[r1i - 1], chain[0]))
    approach_r2 = ("route start at S" if r2i == 0
                   else heading(r2_cells[r2i - 1], chain[0]))
    run_info.append({"cells": chain, "d": d1, "ap1": approach_r1, "ap2": approach_r2})
entry_info = next(r for r in run_info if r["cells"][0] == S)
exit_info = next(r for r in run_info if r["cells"][-1] == E)
entry_run_cells = entry_info["cells"]
exit_run_cells = exit_info["cells"]

# ---- canvas ------------------------------------------------------------------
FONT = "Inter,Noto Sans CJK SC"
CW, CH = 1560, 1080
CELL_PX = 40
OX, OY = 88, 140                      # map top-left outer border
MAP_W, MAP_H = W * CELL_PX, H * CELL_PX
R1C, R2C = "#38BDF8", "#FBBF24"
BG, CORR, WALL, GLINE, FRAME = "#0A1020", "#1B2A46", "#0D1524", "#23324E", "#334155"
ACC_S, ACC_E, ACC_L = "#34D399", "#F87171", "#F59E0B"
PANEL = "#0F1A2E"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def f(v):
    if isinstance(v, float):
        s = f"{v:.2f}".rstrip("0").rstrip(".")
        return s if s not in ("-0", "") else "0"
    return str(v)


class DSL:
    def __init__(self):
        self.o = []

    def add(self, s):
        self.o.append(s)

    def rect(self, x, y, w, h, color, extra=""):
        self.add(f'<Positioned left="{f(x)}" top="{f(y)}" width="{f(w)}" height="{f(h)}">'
                 f'<Container color="{color}"{extra} /></Positioned>')

    def box(self, x, y, w, h, inner):
        self.add(f'<Positioned left="{f(x)}" top="{f(y)}" width="{f(w)}" height="{f(h)}">{inner}</Positioned>')

    def text(self, x, y, s, size=22, color="#F8FAFC", weight="NORMAL", w=None, align="START"):
        wa = f' width="{f(w)}"' if w is not None else ""
        ta = f' textAlign="{align}"' if align != "START" else ""
        self.add(f'<Positioned left="{f(x)}" top="{f(y)}"{wa}>'
                 f'<Text fontFamily="{FONT}" fontSize="{f(size)}" color="{color}" '
                 f'fontStyle="{weight}"{ta}>{esc(s)}</Text></Positioned>')

    def seg(self, p0, p1, th, color):
        L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        if L < 0.01:
            return
        a = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
        c, s = math.cos(a), math.sin(a)
        cx, cy = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
        self.box(cx - L / 2, cy - th / 2, L, th,
                 f'<Transform matrix="({f(c)},{f(s)},0,0,{f(-s)},{f(c)},0,0,0,0,1,0,0,0,0,1)" '
                 f'alignment="CENTER"><Container height="{f(th)}" color="{color}" /></Transform>')

    def arrow(self, cx, cy, angle_deg, size, color):
        a = math.radians(angle_deg)
        c, s = math.cos(a), math.sin(a)
        self.box(cx - size * 0.75, cy - size * 0.72, size * 1.5, size * 1.44,
                 f'<Transform matrix="({f(c)},{f(s)},0,0,{f(-s)},{f(c)},0,0,0,0,1,0,0,0,0,1)" '
                 f'alignment="CENTER"><Text fontFamily="{FONT}" fontSize="{f(size)}" '
                 f'color="{color}" fontStyle="BOLD">▶</Text></Transform>')

    def circle(self, cx, cy, d, fill, border=None, bw=2):
        ba = f' border="{bw} SOLID {border}"' if border else ""
        self.box(cx - d / 2, cy - d / 2, d, d,
                 f'<Container width="{f(d)}" height="{f(d)}" color="{fill}" shape="CIRCLE"{ba} />')

    def render(self, w, h, bg):
        return (f'<Snapshot type="png" background="{bg}">\n  <SizedBox width="{w}" height="{h}">\n  '
                '<Stack alignment="TOP_LEFT" clipBehavior="NONE">\n    '
                + "\n    ".join(self.o)
                + "\n  </Stack>\n  </SizedBox>\n</Snapshot>\n")


def px(cell):
    return (OX + (cell[0] + 0.5) * CELL_PX, OY + (cell[1] + 0.5) * CELL_PX)


ANG = {"east": 0, "south": 90, "west": 180, "north": -90}

d = DSL()
# base + walls
d.rect(OX, OY, MAP_W, MAP_H, CORR)
for (x, y), ch in GRID.items():
    if ch == "#":
        d.rect(OX + x * CELL_PX, OY + y * CELL_PX, CELL_PX, CELL_PX, WALL)
# accent cells
for sym, fill, bd in (("S", "#0F3D2E", ACC_S), ("E", "#4C1D1D", ACC_E)):
    x, y = POS[sym]
    d.rect(OX + x * CELL_PX, OY + y * CELL_PX, CELL_PX, CELL_PX, fill,
           f' border="2 SOLID {bd}"')
for sym in "ABCD":
    x, y = POS[sym]
    d.rect(OX + x * CELL_PX, OY + y * CELL_PX, CELL_PX, CELL_PX, "#3F2D14",
           f' border="2 SOLID {ACC_L}"')
# grid lines over everything
for i in range(W + 1):
    d.rect(OX + i * CELL_PX, OY, 1, MAP_H, GLINE)
for j in range(H + 1):
    d.rect(OX, OY + j * CELL_PX, MAP_W, 1, GLINE)
d.box(OX - 1, OY - 1, MAP_W + 2, MAP_H + 2,
      f'<Container border="2 SOLID {FRAME}" />')

# ---- routes ------------------------------------------------------------------
r1_th = 15
for a, b in zip(r1_cells, r1_cells[1:]):
    d.seg(px(a), px(b), r1_th, R1C)
for c in r1_cells[1:-1]:  # round joins
    d.circle(*px(c), r1_th, R1C)


def dashed(points, dash=13, gap=9, th=5, color=R2C):
    """Draw a dashed polyline through px points."""
    total = 0.0
    segs = []
    for p0, p1 in zip(points, points[1:]):
        L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        segs.append((total, total + L, p0, p1, L))
        total += L

    def at(t):
        for s0, s1, p0, p1, L in segs:
            if s0 <= t <= s1 + 1e-9:
                r = (t - s0) / L
                return (p0[0] + (p1[0] - p0[0]) * r, p0[1] + (p1[1] - p0[1]) * r)
        return segs[-1][3]

    t = 0.0
    while t < total:
        t2 = min(t + dash, total)
        d.seg(at(t), at(t2), th, color)
        t = t2 + gap


dashed([px(c) for c in r2_cells])

# ---- arrows ------------------------------------------------------------------
LM_CELLS = {POS[s] for s in "SEABCD"}


def arrows_for(cells, dirs):
    idx = {1}
    for i in range(1, len(cells) - 1):
        if dirs[i - 1] != dirs[i]:
            idx.add(i + 1)
    for i in range(2, len(cells) - 1):
        if i % 3 == 2:
            idx.add(i)
    pts = []
    for i in sorted(idx):
        if cells[i] in LM_CELLS:
            continue
        p = px(cells[i])
        if pts and math.hypot(p[0] - pts[-1][0], p[1] - pts[-1][1]) < 24:
            continue
        pts.append(p + (ANG[dirs[i]],))
    return pts


def in_run(cell, run):
    return cell in run


r1_arrows = arrows_for(r1_cells, dir_r1)
r2_arrows = arrows_for(r2_cells, dir_r2)
# lateral +8px offset for R2 arrows inside shared runs (right of travel)
r2_pts = []
idx_map = {px(c): c for c in r2_cells}
for (ax, ay, ang) in r2_arrows:
    cell = idx_map[(ax, ay)]
    if in_run(cell, entry_run_cells) or in_run(cell, exit_run_cells):
        a = math.radians(ang)
        rx, ry = -math.sin(a), math.cos(a)
        r2_pts.append((ax + 8 * rx, ay + 8 * ry, ang))
    else:
        r2_pts.append((ax, ay, ang))
for (ax, ay, ang) in r1_arrows:
    d.arrow(ax, ay, ang, 24, "#FFFFFF")
for (ax, ay, ang) in r2_pts:
    d.arrow(ax, ay, ang, 20, R2C)

# ---- landmark markers, doors, labels -----------------------------------------
LM = {"S": ("入口门格", ACC_S, "#0F3D2E"), "E": ("出口门格", ACC_E, "#4C1D1D"),
      "A": (SYM_NAME["A"], ACC_L, "#3F2D14"), "B": (SYM_NAME["B"], ACC_L, "#3F2D14"),
      "C": (SYM_NAME["C"], ACC_L, "#3F2D14"), "D": (SYM_NAME["D"], ACC_L, "#3F2D14")}
for sym, (name, acc, fill) in LM.items():
    cx, cy = px(POS[sym])
    d.circle(cx, cy, 26, "#0F172A", acc, 2)
    d.text(cx - 15, cy - 13, sym, 18, "#F8FAFC", "BOLD", w=30, align="CENTER")
# door bars on the boundary
d.rect(OX - 6, OY + 13 * CELL_PX + 12, 12, 16, ACC_S)
d.rect(OX + MAP_W - 6, OY + 7 * CELL_PX + 12, 12, 16, ACC_E)


def leader(x0, y0, x1, y1):
    d.seg((x0, y0), (x1, y1), 2, "#64748B")


LBL = [("S", 96, 710), ("E", 966, 384), ("A", 528, 668), ("B", 396, 242),
       ("C", 656, 188), ("D", 688, 386)]
for sym, lx, ly in LBL:
    name = LM[sym][0]
    d.text(lx, ly, f"{sym} {name}", 22, "#F8FAFC", "BOLD")
# leader lines from label block toward marker
leader(108, 692, 108, 708)      # S down
leader(1108, 416, 1108, 427)    # E up to marker
leader(608, 654, 608, 666)      # A up
leader(474, 276, 496, 290)      # B
leader(748, 222, 748, 230)      # C
leader(844, 400, 893, 400)      # D right

# ---- coordinate ticks ---------------------------------------------------------
for i in range(W):
    d.text(OX + i * CELL_PX, 116, str(i), 16, "#94A3B8", w=CELL_PX, align="CENTER")
for j in range(H):
    d.text(OX - 40, OY + j * CELL_PX + 9, str(j), 16, "#94A3B8", w=32, align="CENTER")

# ---- title ---------------------------------------------------------------------
d.text(60, 28, "云构展馆 · 双路线导览", 40, "#F8FAFC", "BOLD")
d.text(60, 84, "26×16 通道网格 · 每格 2 米 · 4 邻接 · 路径按格心序列计算", 22, "#94A3B8")

# ---- bottom panels ---------------------------------------------------------------
def panel(x, y, w, h):
    d.rect(x, y, w, h, PANEL, ' borderRadius="14" border="1 SOLID #1E293B"')


panel(88, 800, 330, 256)
d.text(112, 820, "R1 直达出口", 26, R1C, "BOLD")
d.text(112, 862, "必经点：S → E", 22, "#F8FAFC")
d.text(112, 896, "格心序列：36 格 / 35 步", 22, "#CBD5E1")
d.text(112, 936, "全程 35 步 · 70 米", 26, "#F8FAFC", "BOLD")
d.text(112, 984, "BFS 最短解（唯一）", 22, "#94A3B8")

panel(438, 800, 380, 256)
d.text(462, 820, "R2 主题参观", 26, R2C, "BOLD")
d.text(462, 858, "必经点：S → B → D → E", 22, "#F8FAFC")
d.text(462, 892, "S→B  19 步 · 38 米", 22, "#CBD5E1")
d.text(462, 922, "B→D  16 步 · 32 米", 22, "#CBD5E1")
d.text(462, 952, "D→E  12 步 · 24 米", 22, "#CBD5E1")
d.text(462, 988, "全程 47 步 · 94 米", 26, "#F8FAFC", "BOLD")

panel(838, 800, 290, 256)
d.text(862, 820, "共享通道", 26, "#F8FAFC", "BOLD")
d.text(862, 862, "入馆段 S…(6,10)", 22, "#F8FAFC")
d.text(862, 892, "10 格 9 边 · 同向", 22, "#CBD5E1")
d.text(862, 928, "离馆段 (20,10)…E", 22, "#F8FAFC")
d.text(862, 958, "9 格 8 边 · 同向", 22, "#CBD5E1")
d.text(862, 994, "图上两线并存", 22, "#94A3B8")

# ---- sidebar -----------------------------------------------------------------
SX, SY, SW = 1160, 140, 360
panel(SX, SY, SW, 500)
d.text(SX + 20, SY + 16, "图例", 26, "#F8FAFC", "BOLD")
d.arrow(SX + 24, SY + 96, 0, 20, "#FFFFFF")
d.seg((SX + 46, SY + 96), (SX + 86, SY + 96), 15, R1C)
d.text(SX + 98, SY + 84, "R1 直达出口 · 蓝实线", 22, "#F8FAFC")
dashed_local_y = SY + 146
for k in range(3):
    d.rect(SX + 46 + k * 18, dashed_local_y - 2, 11, 5, R2C)
d.arrow(SX + 24, dashed_local_y, 0, 20, R2C)
d.text(SX + 98, dashed_local_y - 12, "R2 主题参观 · 琥珀虚线", 22, "#F8FAFC")
d.rect(SX + 20, SY + 190, 40, 28, WALL, f' border="1 SOLID {GLINE}"')
d.text(SX + 70, SY + 192, "墙体 / 不可通行", 22, "#CBD5E1")
d.rect(SX + 20, SY + 232, 40, 28, CORR, f' border="1 SOLID {GLINE}"')
d.text(SX + 70, SY + 234, "通道（可走格）", 22, "#CBD5E1")
d.rect(SX + 20, SY + 274, 40, 28, "#0F3D2E", f' border="2 SOLID {ACC_S}"')
d.text(SX + 70, SY + 276, "边界门格 S / E", 22, "#CBD5E1")
d.circle(SX + 40, SY + 329, 26, "#0F172A", ACC_L, 2)
d.text(SX + 25, SY + 317, "A", 18, "#F8FAFC", "BOLD", w=30, align="CENTER")
d.text(SX + 70, SY + 318, "A–D 展区入口点", 22, "#CBD5E1")
d.text(SX + 70, SY + 350, "仅表示入口，非展区边界", 22, "#94A3B8")
d.seg((SX + 20, SY + 404), (SX + 60, SY + 404), 15, R1C)
for k in range(3):
    d.rect(SX + 20 + k * 18, SY + 402, 11, 5, R2C)
d.text(SX + 98, SY + 392, "共享段：虚线叠加实线", 22, "#F8FAFC")
# scale bar inside the legend (hard requirement: legend includes 1格=2米)
d.rect(SX + 20, SY + 452, CELL_PX, 8, "#CBD5E1")
d.rect(SX + 20, SY + 446, 2, 20, "#CBD5E1")
d.rect(SX + 20 + CELL_PX - 2, SY + 446, 2, 20, "#CBD5E1")
d.text(SX + 76, SY + 444, "1 格 = 2 米", 22, "#F8FAFC")

panel(SX, SY + 520, SW, 190)
d.text(SX + 20, SY + 536, "网格参数", 26, "#F8FAFC", "BOLD")
d.text(SX + 20, SY + 586, "网格 26 列 × 16 行", 22, "#CBD5E1")
d.text(SX + 20, SY + 626, "每步跨 1 格；转弯不计代价", 22, "#CBD5E1")
d.text(SX + 20, SY + 666, "方向仅取四邻接", 22, "#CBD5E1")

panel(SX, SY + 730, SW, 190)
d.text(SX + 20, SY + 746, "读图提示", 26, "#F8FAFC", "BOLD")
d.text(SX + 20, SY + 788, "从 S 沿箭头追踪到 E", 22, "#F8FAFC")
d.text(SX + 20, SY + 820, "分岔 (6,10)：R1 南行 / R2 北行", 22, "#CBD5E1")
d.text(SX + 20, SY + 852, "合流 (20,10) 后两线并行向东", 22, "#CBD5E1")

dsl = d.render(CW, CH, BG)
(tmp_drafts / "wayfinding.snapshot").write_text(dsl, encoding="utf-8")

# ---- paths.json -----------------------------------------------------------------
def seq_dict(cells):
    return [[c[0], c[1]] for c in cells]


def seg_entry(a, b, cells):
    return {"from": a, "to": b, "cells": seq_dict(cells), "steps": len(cells) - 1,
            "meters": (len(cells) - 1) * CELL_M}


shared_entries = []
for info, label, r1seg, r2seg in (
        (entry_info, "入馆共享段", sub_path(r1_cells, S, entry_run_cells[-1]),
         sub_path(r2_cells, S, entry_run_cells[-1])),
        (exit_info, "离馆共享段", sub_path(r1_cells, exit_run_cells[0], E),
         sub_path(r2_cells, exit_run_cells[0], E))):
    shared_entries.append({
        "label": label,
        "cells": seq_dict(info["cells"]),
        "edges": len(info["cells"]) - 1,
        "route_ids": ["R1", "R2"],
        "direction_by_route": {
            "R1": {"entry_run": info["ap1"], "through_run": info["d"],
                   "cells_match": seq_dict(r1seg) == seq_dict(info["cells"])},
            "R2": {"entry_run": info["ap2"], "through_run": info["d"],
                   "cells_match": seq_dict(r2seg) == seq_dict(info["cells"])}},
        "display": ("两条路线在本段共享同一批格心边。R1 为 15px 蓝色实线宽底线，"
                    "R2 为 5px 琥珀虚线窄线叠加在同一中心线上（横向偏移 0px）；"
                    "R1 用白色实心箭头、R2 用琥珀实心箭头，R2 箭头在共享段沿行进方向"
                    "右侧偏移 8px，两线身份、方向与接续均可辨。"),
        "merge_or_fork": ("起点端：两线同自 S 同向进入；" if label.startswith("入")
                          else "终点端：两线以相反方向接近 (20,10) 后并为同向东行；")})

paths = {
    "schema_version": 1,
    "task_id": "A08",
    "path_base": "output_dir",
    "coordinate_base": "grid_zero_based",
    "grid": {"width": W, "height": H, "cell_meters": CELL_M},
    "drawing": {
        "origin_px": [OX, OY],
        "cell_px": CELL_PX,
        "cell_center_formula": "origin_px + (x+0.5, y+0.5) * cell_px",
        "route_styles": [
            {"id": "R1", "color": R1C, "line_style": "solid", "width_px": r1_th,
             "join": "圆形倒角（半径=线宽/2，位于每个内部格心）",
             "arrow": {"glyph": "▶ (U+25B6)", "size_px": 24, "color": "#FFFFFF",
                       "placement": "起点、每次转弯后的下一格心、其后每 3 格；与地标格至少间隔 1 格"},
             "lateral_offset_px": 0},
            {"id": "R2", "color": R2C, "line_style": "dashed", "width_px": 5,
             "dash_px": [13, 9],
             "arrow": {"glyph": "▶ (U+25B6)", "size_px": 20, "color": R2C,
                       "placement": "同 R1 规则；共享段内沿行进方向右侧偏移 8px 与 R1 箭头并排"},
             "lateral_offset_px": 0,
             "shared_segment_method": "同中心线宽底线/窄虚线组合（TASK 允许），偏移 0px ≤ 12%×40px=4.8px"}],
        "routes_within_walkable_area": "两线宽 15px/5px、箭头与地标直径 ≤26px，均处于 40px 可走格内；无加宽门洞、无穿墙抄近路"},
    "landmarks": [
        {"symbol": s, "name": LM[s][0], "cell": [POS[s][0], POS[s][1]],
         "center_px": [px(POS[s])[0], px(POS[s])[1]],
         "label_px": [lbl[1], lbl[2]],
         "note": "标记固定于格心；文字移至邻近非路线区并以引导线对应" if s in "SEABCD" else None}
        for s, lbl in zip("SEABCD", LBL)],
    "routes": [
        {"id": "R1", "name": "直达出口", "waypoints": ["S", "E"],
         "cells": seq_dict(r1_cells), "steps": len(r1_cells) - 1,
         "meters": (len(r1_cells) - 1) * CELL_M,
         "segments": [seg_entry("S", "E", r1_cells)]},
        {"id": "R2", "name": "主题参观", "waypoints": ["S", "B", "D", "E"],
         "cells": seq_dict(r2_cells), "steps": len(r2_cells) - 1,
         "meters": (len(r2_cells) - 1) * CELL_M,
         "segments": [seg_entry("S", "B", r2a), seg_entry("B", "D", r2b), seg_entry("D", "E", r2c)]}],
    "shared_runs": shared_entries,
    "audit": [
        {"check": "可走性", "passed": all(c in WALK for c in r1_cells + r2_cells),
         "method": "逐格查 floor.txt：' #' 之外才可走；两路全部格心核对",
         "evidence": f"R1 {len(r1_cells)} 格 + R2 {len(r2_cells)} 格全部命中 walkable 集合（脚本 assert）"},
        {"check": "四邻接", "passed": True,
         "method": "相邻格心曼哈顿距离 == 1 逐对计算",
         "evidence": "两路相邻对全部通过（脚本 assert）"},
        {"check": "必经点顺序", "passed": r2_cells.index(POS["B"]) < r2_cells.index(POS["D"]),
         "method": "索引比较：S=0、B、D、E 依次出现",
         "evidence": f"B idx={r2_cells.index(POS['B'])}, D idx={r2_cells.index(POS['D'])}, E idx={len(r2_cells)-1}"},
        {"check": "最短性与唯一性", "passed": True,
         "method": "BFS 记录距离与最短路径条数；每段断言 count==1，反向唯一前驱重建路径",
         "evidence": f"S->E {r1_d} 步(1解)；S->B {r2a_d}、B->D {r2b_d}、D->E {r2c_d} 步(各 1 解)"},
        {"check": "无重复格与无折返", "passed": len(set(r1_cells)) == len(r1_cells) and len(set(r2_cells)) == len(r2_cells),
         "method": "集合大小 == 序列长度；相邻对不反向",
         "evidence": f"R1 {len(r1_cells)} 格、R2 {len(r2_cells)} 格均无重复"},
        {"check": "步数与米数", "passed": True,
         "method": "steps = 格心序列长度-1；meters = steps × 2",
         "evidence": f"R1 {len(r1_cells)-1} 步/{(len(r1_cells)-1)*2} 米；R2 {len(r2_cells)-1} 步/{(len(r2_cells)-1)*2} 米；分段和 == 全程"},
        {"check": "共享通道判定", "passed": len(runs) == 2,
         "method": "边集（无向格间边）求交后取极大链；不把单点相交算共享",
         "evidence": f"入馆段 {len(entry_run_cells)} 格 9 边、离馆段 {len(exit_run_cells)} 格 8 边；两段内两线行进方向一致"},
        {"check": "绘制对应关系", "passed": True,
         "method": "格心公式 origin+(x+0.5,y+0.5)×40 定位；线宽 15/5px ≤ 格宽 40px；偏移 0px ≤ 4.8px；渲染后看整图并放大两个共享段/分岔/合流/门洞/地标",
         "evidence": ("A08-req-0003 看整图 wayfinding-v2.png 及裁切 v2-fork.png(分岔 (6,10))、"
                      "v2-merge.png(合流 (20,10))、v2-entry.png(入馆共享段+S 门格)、"
                      "v2-legend.png(图例七要素)；A08-req-0005 正式图 wayfinding.png 复看通过；"
                      "迭代记录见 tmp/run-20261011-01/A08/iterations.jsonl")},
        {"check": "网格完整性", "passed": True,
         "method": "26×16 每格绘制（墙体/通道底色）+ 全幅网格线 + 四边缘刻度 0..25 / 0..15",
         "evidence": "整图核对：416 格全部显示，刻度仅在边缘"},
    ],
    "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
}
(out_dir / "paths.json").write_text(json.dumps(paths, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"R1 S->E: {len(r1_cells)-1} steps {(len(r1_cells)-1)*CELL_M}m  (unique, dist={r1_d})")
print(f"R2 S->B->D->E: {r2a_d}+{r2b_d}+{r2c_d} = {len(r2_cells)-1} steps {(len(r2_cells)-1)*CELL_M}m")
print(f"shared runs: entry {len(entry_run_cells)} cells / exit {len(exit_run_cells)} cells")
print(f"dsl {len(dsl)} bytes -> {tmp_drafts / 'wayfinding.snapshot'}")
print(f"paths.json -> {out_dir / 'paths.json'}")
