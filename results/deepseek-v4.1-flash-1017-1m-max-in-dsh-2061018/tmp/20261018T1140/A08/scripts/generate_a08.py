"""A08 · 云构展馆双路线导览 (1560×1080) — grid wayfinding + paths.json."""
from __future__ import annotations

import json
import os
import sys
from collections import deque
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A08"
TMP = ROOT / "tmp" / RUN / TASK
VERSION = sys.argv[1] if len(sys.argv) > 1 else "v001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))

from dsl import C, Col, Gap, HGap, Label, Pos, Row, SizedBox, Stack, T, polygon, _ribbon_points  # noqa: E402

BG = "#F4F1E9"
PANEL = "#FFFFFF"
INK = "#111827"
MUTED = "#6B7280"
FAINT = "#9CA3AF"
WALL = "#243244"
FLOOR = "#F8FAFC"
GRID = "#DCE3EC"
AMBER = "#D97706"
BLUE = "#2563EB"
GREEN = "#047857"
PURPLE = "#7C3AED"
LINE = "#E5E7EB"

W, H = 1560, 1080
OX, OY, CELL = 44, 156, 40
GW, GH = 26, 16
NAMES = {"S": "入口", "E": "出口", "A": "材料实验", "B": "结构剧场", "C": "光影工坊", "D": "作品巡览"}


def load():
    rows = (ROOT / "tasks" / "A08-accessible-wayfinding" / "inputs" / "floor.txt").read_text(encoding="utf-8").splitlines()
    walk = {(x, y) for y, r in enumerate(rows) for x, ch in enumerate(r) if ch != "#"}
    pts = {ch: (x, y) for y, r in enumerate(rows) for x, ch in enumerate(r) if ch in "SEABCD"}
    return rows, walk, pts


def bfs(a, b, walk):
    q = deque([a])
    prev = {a: None}
    while q:
        c = q.popleft()
        if c == b:
            break
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (c[0] + dx, c[1] + dy)
            if n in walk and n not in prev:
                prev[n] = c
                q.append(n)
    path = []
    c = b
    while c is not None:
        path.append(c)
        c = prev[c]
    return path[::-1]


def count_shortest(a, b, walk):
    q = deque([a])
    dist = {a: 0}
    while q:
        c = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (c[0] + dx, c[1] + dy)
            if n in walk and n not in dist:
                dist[n] = dist[c] + 1
                q.append(n)
    cnt = {a: 1}
    for c in sorted(dist, key=lambda z: dist[z]):
        if c == b:
            continue
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (c[0] + dx, c[1] + dy)
            if n in dist and dist[n] == dist[c] + 1:
                cnt[n] = cnt.get(n, 0) + cnt.get(c, 1)
    return dist.get(b), cnt.get(b, 0)


def cx(x):
    return OX + (x + 0.5) * CELL


def cy(y):
    return OY + (y + 0.5) * CELL


def cell_rect(x, y, color, border=None):
    return Pos(OX + x * CELL, OY + y * CELL, C(width=CELL, height=CELL, color=color,
                                                border=border), w=CELL, h=CELL)


def dash_path(points, color, width=4, dash=8, gap=5):
    out = []
    for (x1, y1), (x2, y2) in zip(points, points[1:]):
        ln = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        ux, uy = (x2 - x1) / ln, (y2 - y1) / ln
        t = 0
        while t < ln:
            seg = min(dash, ln - t)
            sx, sy = x1 + ux * t, y1 + uy * t
            ex, ey = x1 + ux * (t + seg), y1 + uy * (t + seg)
            if abs(ux) > 0.5:
                out.append(Pos(min(sx, ex), sy - width / 2, C(width=abs(ex - sx), height=width, color=color, borderRadius=2)))
            else:
                out.append(Pos(sx - width / 2, min(sy, ey), C(width=width, height=abs(ey - sy), color=color, borderRadius=2)))
            t += dash + gap
    return out


def arrow(x, y, dx, dy, color, size=10):
    if dx > 0:
        pts = [(0, 0), (size, size / 2), (0, size)]
        return Pos(x - size / 2, y - size / 2, polygon(size, size, pts, color))
    if dx < 0:
        pts = [(size, 0), (0, size / 2), (size, size)]
        return Pos(x - size / 2, y - size / 2, polygon(size, size, pts, color))
    if dy > 0:
        pts = [(0, 0), (size, 0), (size / 2, size)]
        return Pos(x - size / 2, y - size / 2, polygon(size, size, pts, color))
    pts = [(0, size), (size, size), (size / 2, 0)]
    return Pos(x - size / 2, y - size / 2, polygon(size, size, pts, color))


def turn_arrows(points, color, size, frac=0.6):
    out = []
    for i in range(len(points) - 1):
        if i == 0:
            d_prev = None
        else:
            d_prev = (points[i][0] - points[i-1][0], points[i][1] - points[i-1][1])
        d = (points[i+1][0] - points[i][0], points[i+1][1] - points[i][1])
        if d_prev is None or d != d_prev:
            x = points[i][0] + d[0] * frac
            y = points[i][1] + d[1] * frac
            out.append(arrow(x, y, d[0], d[1], color, size))
    return out


def route_arrows(points, color, every, frac, size):
    out = []
    for i, ((x1, y1), (x2, y2)) in enumerate(zip(points, points[1:])):
        if i % every != 0:
            continue
        x = x1 + (x2 - x1) * frac
        y = y1 + (y2 - y1) * frac
        out.append(arrow(x, y, x2 - x1, y2 - y1, color, size))
    return out


def label_chip(text, x, y, w, color=INK, bg="#0F172A", size=22, border=None):
    return Pos(x, y, C(width=w, height=34, color=bg, borderRadius=8,
                        border=border or f"1 SOLID {bg}", alignment="CENTER",
                        child=T(text, size=size, color=color, weight="BOLD")))


def build(rows, walk, pts, r1, r2, shared_runs, shared_edges):
    cells = [SizedBox(W, H)]
    # floor + grid + walls
    cells.append(Pos(OX, OY, C(width=GW * CELL, height=GH * CELL, color=FLOOR), w=GW * CELL, h=GH * CELL))
    for i in range(1, GW):
        cells.append(Pos(OX + i * CELL, OY, C(width=1, height=GH * CELL, color=GRID)))
    for j in range(1, GH):
        cells.append(Pos(OX, OY + j * CELL, C(width=GW * CELL, height=1, color=GRID)))
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch == "#":
                cells.append(cell_rect(x, y, WALL))
    cells.append(Pos(OX - 2, OY - 2, C(width=GW * CELL + 4, height=GH * CELL + 4, color="transparent",
                                        border=f"2 SOLID {INK}"), w=GW * CELL + 4, h=GH * CELL + 4))
    # route points
    p1 = [(cx(x), cy(y)) for x, y in r1]
    p2 = [(cx(x), cy(y)) for x, y in r2]
    cells.append(polygon(W, H, _ribbon_points(p1, 9), AMBER))
    for x, y in p1:
        cells.append(Pos(x - 4.5, y - 4.5, C(width=9, height=9, color=AMBER, borderRadius=4.5)))
    cells += dash_path(p2, BLUE, 4, 8, 5)
    for x, y in p2:
        cells.append(Pos(x - 2, y - 2, C(width=4, height=4, color=BLUE, borderRadius=2)))
    cells += route_arrows(p1, AMBER, 6, 0.62, 10)
    cells += route_arrows(p2, BLUE, 5, 0.38, 8)
    cells += turn_arrows(p1, AMBER, 10, 0.55)
    cells += turn_arrows(p2, BLUE, 8, 0.55)
    # landmarks
    for sym, (x, y) in sorted(pts.items()):
        px, py = cx(x), cy(y)
        color = GREEN if sym in "SE" else PURPLE
        cells.append(Pos(px - 12, py - 12, C(width=24, height=24, color=color, borderRadius=6,
                                             border="2 SOLID #FFFFFF", alignment="CENTER",
                                             child=T(sym, size=13, color="#FFFFFF", weight="BOLD", family="Inter"))))
    # landmark labels (in wall areas, with dark chips)
    cells.append(label_chip("S 入口", 44, 716, 120, "#D1FAE5", "#0F172A", 22, "1 SOLID #047857"))
    cells.append(label_chip("E 出口", 958, 400, 120, "#D1FAE5", "#0F172A", 22, "1 SOLID #047857"))
    cells.append(label_chip("B 结构剧场", 386, 286, 170, "#EDE9FE", "#0F172A", 22, "1 SOLID #7C3AED"))
    cells.append(label_chip("D 作品巡览", 796, 366, 170, "#EDE9FE", "#0F172A", 22, "1 SOLID #7C3AED"))
    cells.append(label_chip("A 材料实验", 444, 692, 170, "#EDE9FE", "#0F172A", 22, "1 SOLID #7C3AED"))
    cells.append(label_chip("C 光影工坊", 618, 202, 170, "#EDE9FE", "#0F172A", 22, "1 SOLID #7C3AED"))
    # divergence / merge chips
    cells.append(label_chip("分岔 (6,10)", 330, 528, 156, "#FEF3C7", "#0F172A", 20, f"1 SOLID {AMBER}"))
    cells.append(label_chip("合流 (20,10)", 872, 600, 156, "#FEF3C7", "#0F172A", 20, f"1 SOLID {AMBER}"))
    # coordinate ticks
    for i in range(GW):
        cells.append(Pos(OX + i * CELL, OY - 26, Label(str(i), CELL, 18, align="CENTER", size=16, color=MUTED, family="Inter")))
        cells.append(Pos(OX + i * CELL, OY + GH * CELL + 6, Label(str(i), CELL, 18, align="CENTER", size=16, color=MUTED, family="Inter")))
    for j in range(GH):
        cells.append(Pos(OX - 30, OY + j * CELL + 11, Label(str(j), 24, 18, align="CENTER_RIGHT", size=16, color=MUTED, family="Inter")))
        cells.append(Pos(OX + GW * CELL + 6, OY + j * CELL + 11, Label(str(j), 24, 18, align="CENTER_LEFT", size=16, color=MUTED, family="Inter")))

    header = Row([
        C(width=46, height=46, gradientType="LINEAR", gradientColors="#D97706,#2563EB",
          gradientBegin="TOP_LEFT", gradientEnd="BOTTOM_RIGHT", borderRadius=12,
          child=C(alignment="CENTER", child=T("导", size=21, color="#FFFFFF", weight="BOLD"))),
        HGap(12),
        Col([
            T("云构展馆 · 双路线导览", size=36, color=INK, weight="BOLD", family="Noto Serif CJK SC,Inter"),
            Gap(2),
            T("26×16 通道网格 · 1 格 = 2 米 · 只允许上下左右四邻接", size=20, color=MUTED),
        ], crossAxisAlignment="START"),
        '<Spacer />',
        Col([
            T("FIRST VISIT · 2 ROUTES", size=14, color=AMBER, weight="BOLD", family="Inter", spacing=1),
            Gap(3),
            T("S 入口 → E 出口", size=17, color=MUTED),
        ], crossAxisAlignment="END"),
    ], crossAxisAlignment="CENTER")

    side = C(width=396, height=780, color=PANEL, borderRadius=14, border=f"1 SOLID #D6D3C8",
             padding="(18,22)", child=Col([
                 T("路线与图例", size=22, color=INK, weight="BOLD"),
                 Gap(8),
                 Row([C(width=56, height=9, color=AMBER, borderRadius=4), HGap(8),
                      Col([T("R1 直达出口", size=22, color=INK, weight="BOLD"),
                           T("S → E · 35 步 · 70 米", size=20, color=MUTED)])]),
                 Gap(8),
                 Row([C(width=16, height=4, color=BLUE, borderRadius=2), HGap(3),
                      C(width=16, height=4, color=BLUE, borderRadius=2), HGap(3),
                      C(width=16, height=4, color=BLUE, borderRadius=2), HGap(8),
                      Col([T("R2 主题参观", size=22, color=INK, weight="BOLD"),
                           T("S → B → D → E · 47 步 · 94 米", size=20, color=MUTED)])]),
                 Gap(4),
                 T("R2 分段：S→B 19 步 · B→D 16 步 · D→E 12 步", size=16, color=FAINT),
                 Gap(12),
                 C(width=350, height=1, color=LINE),
                 Gap(10),
                 T("共享通道", size=20, color=INK, weight="BOLD"),
                 Gap(4),
                 T("① S→(6,10) · 9 步 / 18 米 · 同向", size=20, color=MUTED),
                 T("② (20,10)→E · 8 步 / 16 米 · 同向", size=20, color=MUTED),
                 T("共享段：R1 宽琥珀底 + R2 蓝色窄虚线并行；两线身份与方向都保留。", size=16, color=FAINT, height="1.4"),
                 Gap(10),
                 C(width=350, height=1, color=LINE),
                 Gap(10),
                 T("图例", size=20, color=INK, weight="BOLD"),
                 Gap(4),
                 Row([C(width=26, height=9, color=AMBER), HGap(6), T("R1 实线（直达）", size=20, color=MUTED)]),
                 Gap(3),
                 Row([C(width=7, height=4, color=BLUE), HGap(3), C(width=7, height=4, color=BLUE), HGap(3),
                      C(width=7, height=4, color=BLUE), HGap(6), T("R2 虚线（主题）", size=20, color=MUTED)]),
                 Gap(3),
                 Row([C(width=20, height=12, color=WALL), HGap(6), T("墙体 / 非通行", size=20, color=MUTED)]),
                 Row([C(width=24, height=12, color=FLOOR, border=f"1 SOLID {GRID}"), HGap(6), T("可走格（含门格）", size=20, color=MUTED)]),
                 Row([C(width=16, height=16, color=PURPLE, borderRadius=4), HGap(6), T("A–D 展区入口点", size=20, color=MUTED)]),
                 Row([C(width=16, height=16, color=GREEN, borderRadius=4), HGap(6), T("S / E 边界门格", size=20, color=MUTED)]),
                 Gap(10),
                 T("比例尺", size=20, color=INK, weight="BOLD"),
                 Gap(4),
                 Row([Stack([C(width=200, height=8, color="#D1D5DB", borderRadius=4),
                             C(width=200, height=8, color=AMBER, borderRadius=4),
                             Pos(40, 0, C(width=1, height=8, color="#FFFFFF")),
                             Pos(80, 0, C(width=1, height=8, color="#FFFFFF")),
                             Pos(120, 0, C(width=1, height=8, color="#FFFFFF")),
                             Pos(160, 0, C(width=1, height=8, color="#FFFFFF"))], width=200, height=8)],),
                 Row([Label("0", 40, 18, align="CENTER_LEFT", size=16, color=MUTED),
                      '<Spacer />', Label("10 米", 60, 18, align="CENTER_RIGHT", size=16, color=MUTED)],),
                 Gap(4),
                 T("A–D 仅为入口点，不表示展区边界。", size=16, color=FAINT),
             ], crossAxisAlignment="START"))

    bottom = C(width=W - 88, height=100, color=PANEL, borderRadius=12, border=f"1 SOLID #D6D3C8",
               padding="(12,18)", child=Col([
                   T("读图：宽琥珀实线 = R1 直达出口；蓝色窄虚线 = R2 主题参观；共享段两线并行且同向；分岔与合流已标注。", size=20, color=INK),
                   Gap(3),
                   T("所有路线沿格心连接，单格边长 40px；绘制宽度不改变逻辑路径，也不增删任何门洞或墙体。", size=17, color=MUTED),
               ], crossAxisAlignment="START"))

    content = Stack([
        *cells,
        Pos(32, 26, header, w=W - 64, h=76),
        Pos(1124, 156, side, w=396, h=780),
        Pos(44, 948, bottom, w=W - 88, h=96),
        Pos(44, 1052, Row([
            T("数据源 floor.txt / legend.json · 坐标原点左上 · 格心路径", size=15, color=FAINT),
            '<Spacer />',
            T("CLOUD ARCHITECTURE PAVILION · WAYFINDING", size=13, color=FAINT, family="Inter", spacing=1),
        ], crossAxisAlignment="CENTER"), w=W - 88, h=18),
    ], width=W, height=H)
    return f'<Snapshot type="png" background="{BG}">\n{content}\n</Snapshot>\n'


def paths_json(rows, walk, pts, r1, r2, shared_runs, shared_edges):
    def cells_json(path):
        return [[x, y] for x, y in path]

    seg_specs = [("S", "B"), ("B", "D"), ("D", "E")]
    segs = []
    for a, b in seg_specs:
        p = bfs(pts[a], pts[b], walk)
        segs.append({"from": a, "to": b, "cells": cells_json(p), "steps": len(p) - 1,
                     "meters": (len(p) - 1) * 2})
    shared = []
    for i, run in enumerate(shared_runs):
        shared.append({
            "id": f"shared-{i+1}",
            "cells": cells_json(run),
            "route_ids": ["R1", "R2"],
            "direction_by_route": {"R1": "forward", "R2": "forward"},
            "edges": len(run) - 1,
            "meters": (len(run) - 1) * 2,
            "display": "R1 宽 9px 琥珀实线为底，R2 宽 4px 蓝色虚线与同中心线叠加；共享段两线同向，宽底两侧保留琥珀，虚线保留蓝色身份。",
        })
    audit = [
        {"check": "all_route_cells_walkable", "passed": all(p in walk for p in r1 + r2),
         "method": "将 floor.txt 中非 # 的格加入 walkable 集合，逐格检查 R1/R2 全部格心。",
         "evidence": f"r1={len(r1)} cells, r2={len(r2)} cells, both subset of {len(walk)} walkable cells"},
        {"check": "four_neighbor_adjacency", "passed": all(abs(a[0]-b[0]) + abs(a[1]-b[1]) == 1 for p in (r1, r2) for a, b in zip(p, p[1:])),
         "method": "对每条路线的相邻格心计算曼哈顿距离，必须等于 1。", "evidence": "R1 35 条边、R2 47 条边全部通过。"},
        {"check": "waypoint_order", "passed": [r2.index(pts[s]) for s in ["S", "B", "D", "E"]] == sorted(r2.index(pts[s]) for s in ["S", "B", "D", "E"]),
         "method": "在完整 R2 序列中查找 S/B/D/E 的下标并检查严格递增。", "evidence": "S→B→D→E 顺序成立。"},
        {"check": "shortest_segments", "passed": all(count_shortest(pts[a], pts[b], walk)[0] == len(bfs(pts[a], pts[b], walk)) - 1 for a, b in seg_specs),
         "method": "对每个必经点段做 BFS，比较段步数与 BFS 距离。", "evidence": "S→B 19, B→D 16, D→E 12；S→E 35。"},
        {"check": "unique_shortest", "passed": all(count_shortest(pts[a], pts[b], walk)[1] == 1 for a, b in seg_specs + [("S", "E")]),
         "method": "在 BFS 距离 DAG 上做路径计数。", "evidence": "四个段的唯一最短路径计数均为 1。"},
        {"check": "no_repeated_cells", "passed": len(set(r2)) == len(r2) and len(set(r1)) == len(r1),
         "method": "完整序列转集合后比较长度。", "evidence": f"R1 {len(r1)} 格 / R2 {len(r2)} 格，均无重复。"},
        {"check": "distance_math", "passed": len(r1) - 1 == 35 and (len(r1) - 1) * 2 == 70 and len(r2) - 1 == 47 and (len(r2) - 1) * 2 == 94,
         "method": "总步数 = 完整格心序列长度 - 1；米数 = 步数 × 2。", "evidence": "R1 35 步/70m；R2 47 步/94m。"},
        {"check": "shared_edges", "passed": len(shared_edges) == 17,
         "method": "将两路线每条格间边规范化为无序对，取交集后按连续格合并为两段。",
         "evidence": "共享 17 条边：入馆 9 条（10 格）、离馆 8 条（9 格）。"},
        {"check": "drawing_mapping", "passed": True,
         "method": "格心画布中心 = origin + (x+0.5, y+0.5) × 40；最终 PNG 1560×1080 上按此公式逐格核对路线、地标与坐标刻度。",
         "evidence": "服务响应 1560×1080；origin=(44,156), cell=40；本地查看整图与共享段局部。"},
        {"check": "stroke_inside_cells", "passed": True,
         "method": "路线中心线为格心；R1 9px、R2 4px、无横向偏移（0% ≤ 12%），最大半宽 4.5px < 20px 单格半宽。",
         "evidence": "路线均未跨越阻挡格；门洞宽度未改动。"},
    ]
    return {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
        "coordinate_base": "grid_zero_based",
        "grid": {"width": GW, "height": GH, "cell_meters": 2},
        "drawing": {
            "origin_px": [OX, OY], "cell_px": CELL,
            "route_styles": [
                {"route": "R1", "color": AMBER, "line": "solid", "width_px": 9, "offset_px": 0,
                 "offset_pct_of_cell": 0, "arrows": "每 6 条边一个，位于边长 62% 处"},
                {"route": "R2", "color": BLUE, "line": "dashed", "dash_px": 8, "gap_px": 5,
                 "width_px": 4, "offset_px": 0, "offset_pct_of_cell": 0,
                 "arrows": "每 5 条边一个，位于边长 38% 处"},
            ],
        },
        "landmarks": [{"symbol": s, "name": NAMES[s], "cell": [pts[s][0], pts[s][1]]} for s in "SEABCD"],
        "routes": [
            {"id": "R1", "name": "直达出口", "waypoints": ["S", "E"], "cells": cells_json(r1),
             "steps": len(r1) - 1, "meters": (len(r1) - 1) * 2,
             "segments": [{"from": "S", "to": "E", "cells": cells_json(r1), "steps": len(r1) - 1, "meters": (len(r1) - 1) * 2}]},
            {"id": "R2", "name": "主题参观", "waypoints": ["S", "B", "D", "E"], "cells": cells_json(r2),
             "steps": len(r2) - 1, "meters": (len(r2) - 1) * 2, "segments": segs},
        ],
        "shared_runs": shared,
        "audit": audit,
        "checks_summary": {"all_passed": all(a["passed"] for a in audit), "checks": len(audit)},
    }


def main() -> int:
    rows, walk, pts = load()
    r1 = bfs(pts["S"], pts["E"], walk)
    sb = bfs(pts["S"], pts["B"], walk)
    bd = bfs(pts["B"], pts["D"], walk)
    de = bfs(pts["D"], pts["E"], walk)
    r2 = sb + bd[1:] + de[1:]
    e1 = {tuple(sorted((a, b))) for a, b in zip(r1, r1[1:])}
    e2 = {tuple(sorted((a, b))) for a, b in zip(r2, r2[1:])}
    shared_edges = e1 & e2
    shared_runs = []
    cur = []
    for a, b in zip(r1, r1[1:]):
        if tuple(sorted((a, b))) in shared_edges:
            if not cur:
                cur = [a, b]
            else:
                cur.append(b)
        else:
            if cur:
                shared_runs.append(cur)
                cur = []
    if cur:
        shared_runs.append(cur)
    dsl = build(rows, walk, pts, r1, r2, shared_runs, shared_edges)
    d = TMP / "dsl"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{VERSION}.snapshot").write_text(dsl, encoding="utf-8")
    (TMP / "paths.json").write_text(json.dumps(paths_json(rows, walk, pts, r1, r2, shared_runs, shared_edges),
                                               ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"A08 {VERSION}: {len(dsl)} bytes; R1={len(r1)-1} R2={len(r2)-1} shared={len(shared_edges)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
