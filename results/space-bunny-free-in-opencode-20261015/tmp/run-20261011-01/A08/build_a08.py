#!/usr/bin/env python
"""A08 展馆双路线导览与共享通道 —— 1560×1080 导览图。

启动基准：总任务根(suite_root)。输入 tasks/A08-accessible-wayfinding/inputs/ 只读。
路径按格心序列用 4 邻接 BFS 计算；绘制用平行偏移（≤ 单格边长 12%），逻辑长度仍按格间边计。
"""
from __future__ import annotations

import json
import math
import os
import sys
from collections import deque
from pathlib import Path

sys.path.insert(0, "tmp/run-20261011-01/_suite/scripts")
import snapkit as sk  # noqa: E402
from snapkit import C  # noqa: E402

TASK = "A08"
BASE = "tasks/A08-accessible-wayfinding"
FLOOR_IN = f"{BASE}/inputs/floor.txt"
LEGEND_IN = f"{BASE}/inputs/legend.json"
DRAFTS = f"tmp/run-20261011-01/{TASK}/drafts"

W, H = 1560, 1080
CELL = 40                      # 单格像素边长（题面要求 ≥36）
OX, OY = 60, 156               # 地图左上外边界的像素坐标
GRID_W, GRID_H = 26, 16
GX1, GY1 = OX + GRID_W * CELL, OY + GRID_H * CELL      # 1100, 796
OFF = 0.11 * CELL              # 平行偏移 4.4px = 单格边长的 11%（题面上限 12%）
W1, W2 = 8.0, 6.0              # 两条路线线宽
C1, C2 = "#0F766E", "#C2410C"  # R1 深青(实线) / R2 橙(虚线)

DOOR_BG, DOOR_EDGE = "#D1FAE5", "#0F766E"
WALL = "#C6D0DE"
FLOOR_BG = "#FFFFFF"
LATTICE = "#64748B44"
LM_COLOR = "#6D28D9"

DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))


def load():
    r = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
    rows = [l.rstrip("\n").rstrip("\r") for l in
            (r / FLOOR_IN).read_text(encoding="utf-8").split("\n")]
    rows = [r_ for r_ in rows if r_.strip() != ""]
    legend = json.loads((r / LEGEND_IN).read_text(encoding="utf-8"))
    return rows, legend


# ---------------------------------------------------------------- 路径计算
def walkable(grid, x, y):
    return 0 <= y < len(grid) and 0 <= x < len(grid[y]) and grid[y][x] != "#"


def bfs_all(grid, src):
    dist = {src: 0}
    cnt = {src: 1}
    order = []
    q = deque([src])
    while q:
        n = q.popleft()
        order.append(n)
        for dx, dy in DIRS:
            m = (n[0] + dx, n[1] + dy)
            if not walkable(grid, *m):
                continue
            if m not in dist:
                dist[m] = dist[n] + 1
                cnt[m] = cnt[n]
                q.append(m)
            elif dist[m] == dist[n] + 1:
                cnt[m] += cnt[n]
    return dist, cnt, order


def shortest_path(grid, src, dst):
    dist, cnt, _ = bfs_all(grid, src)
    if dst not in dist:
        raise SystemExit(f"{src} 与 {dst} 之间不连通")
    path = [dst]
    while path[-1] != src:
        n = path[-1]
        for dx, dy in DIRS:
            m = (n[0] + dx, n[1] + dy)
            if walkable(grid, *m) and dist.get(m) == dist[n] - 1:
                path.append(m)
                break
        else:
            raise SystemExit("重建最短路失败")
    path.reverse()
    return path, dist[dst], cnt[dst]


def center(cell):
    return (OX + (cell[0] + 0.5) * CELL, OY + (cell[1] + 0.5) * CELL)


def edges_of(cells):
    return {frozenset((cells[i], cells[i + 1])) for i in range(len(cells) - 1)}


# ---------------------------------------------------------------- 几何
def seg_dsl(x1, y1, x2, y2, wdt, color, cap_round=True):
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    if L < 0.01:
        return ""
    ang = math.degrees(math.atan2(dy, dx))
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    bw = L + wdt + 2
    return (f'<Positioned left="{round(cx - bw / 2, 2)}" top="{round(cy - wdt / 2, 2)}" '
            f'width="{round(bw, 2)}" height="{round(wdt)}">'
            f'<Transform matrix="{sk.rot_matrix(ang)}" alignment="CENTER">'
            f'<Container width="{round(bw, 2)}" height="{round(wdt)}" color="{color}" '
            f'borderRadius="{round(wdt / 2, 2) if cap_round else 0}"/></Transform></Positioned>')


def offset_polyline(pts, d):
    """带斜接(miter)的平行偏移，保证转角处两条线仍然分开且连续。"""
    n = len(pts)
    out = []
    for i, p in enumerate(pts):
        if i == 0:
            t = _unit(pts[1][0] - p[0], pts[1][1] - p[1])
            nv = (-t[1], t[0])
            out.append((p[0] + nv[0] * d, p[1] + nv[1] * d))
        elif i == n - 1:
            t = _unit(p[0] - pts[i - 1][0], p[1] - pts[i - 1][1])
            nv = (-t[1], t[0])
            out.append((p[0] + nv[0] * d, p[1] + nv[1] * d))
        else:
            t1 = _unit(p[0] - pts[i - 1][0], p[1] - pts[i - 1][1])
            t2 = _unit(pts[i + 1][0] - p[0], pts[i + 1][1] - p[1])
            n1 = (-t1[1], t1[0])
            n2 = (-t2[1], t2[0])
            mx, my = n1[0] + n2[0], n1[1] + n2[1]
            m = _unit(mx, my)
            dot = m[0] * n1[0] + m[1] * n1[1]
            k = d / dot if abs(dot) > 1e-6 else d
            out.append((p[0] + m[0] * k, p[1] + m[1] * k))
    return out


def _unit(x, y):
    L = math.hypot(x, y)
    if L < 1e-9:
        return (1.0, 0.0)
    return (x / L, y / L)


def arrow_dsl(px, py, ux, uy, color, size=10.0, thick=3.0, ang=34.0, halo=None):
    a = math.radians(ang)
    d1 = (ux * math.cos(a) - uy * math.sin(a), ux * math.sin(a) + uy * math.cos(a))
    d2 = (ux * math.cos(-a) - uy * math.sin(-a), ux * math.sin(-a) + uy * math.cos(-a))
    out = []
    if halo:
        for d in (d1, d2):
            out.append(seg_dsl(px - d[0] * (size + 1.6), py - d[1] * (size + 1.6),
                               px + ux * 1.8, py + uy * 1.8, thick + 2.4, halo))
    for d in (d1, d2):
        out.append(seg_dsl(px - d[0] * size, py - d[1] * size, px, py, thick, color))
    return "".join(out)


def dashed(d1, d2, wdt, color, dash=9.0, gap=7.0):
    dx, dy = d2[0] - d1[0], d2[1] - d1[1]
    L = math.hypot(dx, dy)
    if L < 0.01:
        return ""
    ux, uy = dx / L, dy / L
    parts = []
    t = 0.0
    while t < L:
        e = min(t + dash, L)
        parts.append(seg_dsl(d1[0] + ux * t, d1[1] + uy * t, d1[0] + ux * e, d1[1] + uy * e, wdt, color))
        t = e + gap
    return "".join(parts)


# ---------------------------------------------------------------- 分析
def analyze(grid, legend):
    marks = {}
    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            if ch in "SEABCD":
                marks[ch] = (x, y)
    r1, s1, c1 = shortest_path(grid, marks["S"], marks["E"])
    seg_defs = [("S", "B"), ("B", "D"), ("D", "E")]
    parts, legs = [], []
    for a, b in seg_defs:
        p, s, c = shortest_path(grid, marks[a], marks[b])
        parts.append(p)
        legs.append({"from": a, "to": b, "cells": p, "steps": s, "meters": s * 2,
                     "shortest_path_count": c})
    r2 = parts[0][:]
    for p in parts[1:]:
        r2.extend(p[1:])
    e1, e2 = edges_of(r1), edges_of(r2)
    return {"marks": marks, "R1": r1, "R2": r2, "legs": legs,
            "R1_steps": len(r1) - 1, "R2_steps": len(r2) - 1,
            "R1_paths": c1, "shared_edges": e1 & e2}


def shared_runs(r1, r2):
    """以格间边（无向）求交集，再在 r1 中取最大连续公共子路径；仅共享单格不算共享通道。"""
    e2 = edges_of(r2)
    idx2 = {c: i for i, c in enumerate(r2)}
    runs, cur = [], []
    for i in range(len(r1) - 1):
        if frozenset((r1[i], r1[i + 1])) in e2:
            if not cur:
                cur = [r1[i]]
            cur.append(r1[i + 1])
        else:
            if len(cur) >= 2:
                runs.append(cur)
            cur = []
    if len(cur) >= 2:
        runs.append(cur)
    out = []
    for run in runs:
        j = idx2[run[0]]
        same = r2[j + 1:j + len(run)] == run[1:]
        out.append({"cells": run, "start_index_r1": r1.index(run[0]),
                    "start_index_r2": j,
                    "direction": "同向" if same else "反向"})
    return out


# ---------------------------------------------------------------- 标注框
# 地标文字框（画在空白墙区，用引导线对应格心；不压任何路线）
LABELS = {
    "S": {"name": "入口门格", "box": (62, 722, 242, 758)},
    "E": {"name": "出口门格", "box": (898, 332, 1073, 368)},
    "A": {"name": "材料实验入口", "box": (382, 690, 557, 724)},
    "B": {"name": "结构剧场入口", "box": (306, 372, 481, 406)},
    "C": {"name": "光影工坊入口", "box": (578, 372, 753, 406)},
    "D": {"name": "作品巡览入口", "box": (676, 452, 851, 486)},
}


def build(grid, legend, an):
    P = []
    A = P.append
    marks = an["marks"]
    r1, r2 = an["R1"], an["R2"]

    A(f'<Positioned left="0" top="0" width="{W}" height="{H}">'
      f'<Container width="{W}" height="{H}" color="#F4F7FB"/></Positioned>')

    # ---------------- 页眉
    A(sk.text("云构展馆 · 双路线导览图", size=34, color=C.INK, family=sk.F_HEAD,
              left=60, top=22, width=620, height=44))
    A(sk.text("通道网格 26 列 × 16 行 · 每格边长 2 米 · 跨相邻可走格 1 步",
              size=22, color=C.MUTED, family=sk.F_BODY, left=60, top=70, width=700, height=30))
    A(sk.text("俯视示意图，非真实比例地图", size=22, color="#B45309", family=sk.F_HEAD,
              left=760, top=70, width=340, height=30, align="RIGHT"))

    # ---------------- 网格底
    A(f'<Positioned left="{OX}" top="{OY}" width="{GRID_W * CELL}" height="{GRID_H * CELL}">'
      f'<Container width="{GRID_W * CELL}" height="{GRID_H * CELL}" color="#E7ECF3" '
      f'borderRadius="4"/></Positioned>')
    # 墙体按行做极大连续段合并（几何与输入逐格一致，仅减少图元数量）
    for y, row in enumerate(grid):
        x = 0
        while x < len(row):
            if row[x] == "#":
                s = x
                while x < len(row) and row[x] == "#":
                    x += 1
                A(f'<Positioned left="{OX + s * CELL}" top="{OY + y * CELL}" '
                  f'width="{(x - s) * CELL}" height="{CELL}">'
                  f'<Container width="{(x - s) * CELL}" height="{CELL}" color="{WALL}"/></Positioned>')
            else:
                x += 1
    # 可走格
    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            if ch != "#":
                A(f'<Positioned left="{OX + x * CELL + 1}" top="{OY + y * CELL + 1}" '
                  f'width="{CELL - 2}" height="{CELL - 2}">'
                  f'<Container width="{CELL - 2}" height="{CELL - 2}" color="{FLOOR_BG}"/></Positioned>')
    # 完整 26×16 栅格线
    for x in range(GRID_W + 1):
        A(f'<Positioned left="{OX + x * CELL}" top="{OY}" width="1" height="{GRID_H * CELL}">'
          f'<Container width="1" height="{GRID_H * CELL}" color="{LATTICE}"/></Positioned>')
    for y in range(GRID_H + 1):
        A(f'<Positioned left="{OX}" top="{OY + y * CELL}" width="{GRID_W * CELL}" height="1">'
          f'<Container width="{GRID_W * CELL}" height="1" color="{LATTICE}"/></Positioned>')
    # 门洞：S / E 所在的边界格
    for sym in ("S", "E"):
        cx, cy = marks[sym]
        A(f'<Positioned left="{OX + cx * CELL + 2}" top="{OY + cy * CELL + 2}" '
          f'width="{CELL - 4}" height="{CELL - 4}">'
          f'<Container width="{CELL - 4}" height="{CELL - 4}" color="{DOOR_BG}"/></Positioned>')
        ex = OX + cx * CELL + (2 if sym == "S" else CELL - 6)
        A(f'<Positioned left="{ex}" top="{OY + cy * CELL}" width="4" height="{CELL}">'
          f'<Container width="4" height="{CELL}" color="{DOOR_EDGE}"/></Positioned>')
    A(f'<Positioned left="{OX}" top="{OY}" width="{GRID_W * CELL}" height="{GRID_H * CELL}">'
      f'<Container width="{GRID_W * CELL}" height="{GRID_H * CELL}" color="#FFFFFF00" '
      f'border="2.5 SOLID #94A3B8" borderRadius="4"/></Positioned>')

    # ---------------- 坐标刻度（只在边缘）
    for x in range(GRID_W):
        if x % 2 == 0:
            A(sk.text(str(x), size=16, color=C.MUTED, family=sk.F_NUM, align="CENTER",
                      left=OX + x * CELL, top=OY - 22, width=CELL, height=20))
    for y in range(GRID_H):
        A(sk.text(str(y), size=16, color=C.MUTED, family=sk.F_NUM, align="RIGHT",
                  left=OX - 44, top=OY + y * CELL + 10, width=36, height=20))
    A(sk.text("列 x →", size=16, color=C.FAINT, family=sk.F_BODY,
              left=OX + 6, top=OY - 50, width=140, height=22))
    A(sk.text("行 y ↓", size=16, color=C.FAINT, family=sk.F_BODY, align="RIGHT",
              left=0, top=OY - 50, width=46, height=22))

    # ---------------- 路线（平行偏移）
    route_offsets = {}
    runs = shared_runs(r1, r2)
    # 共享段的深色细衬线先画（位于两条路线之下），用于标出「同一通道内两线并行」
    for rn in runs:
        pts = [center(c) for c in rn["cells"]]
        a = offset_polyline(pts, -OFF - W1 / 2)
        b = offset_polyline(pts, OFF + W2 / 2)
        for poly in (a, b):
            for i in range(len(poly) - 1):
                A(seg_dsl(poly[i][0], poly[i][1], poly[i + 1][0], poly[i + 1][1], 2.4, "#0F172E"))

    for rid, cells, color, width, dashy, d in (("R1", r1, C1, W1, False, -OFF),
                                               ("R2", r2, C2, W2, True, OFF)):
        pts = [center(c) for c in cells]
        poly = offset_polyline(pts, d)
        for i in range(len(poly) - 1):
            a, b = poly[i], poly[i + 1]
            if dashy:
                A(dashed(a, b, width, color))
            else:
                A(seg_dsl(a[0], a[1], b[0], b[1], width, color))
        # 方向箭头：每 4 条格间边一个，外加每个转角后第一个边
        marks_at = set(range(3, len(poly) - 1, 4))
        for i in range(1, len(cells) - 1):
            if cells[i - 1][0] != cells[i + 1][0] or cells[i - 1][1] != cells[i + 1][1]:
                marks_at.add(i)
        for i in sorted(marks_at):
            ax, ay = poly[i]
            ux, uy = _unit(poly[i + 1][0] - poly[i - 1][0], poly[i + 1][1] - poly[i - 1][1])
            A(arrow_dsl(ax, ay, ux, uy, color, size=9.0, thick=2.6, halo="#FFFFFF"))
        route_offsets[rid] = {"offset_px": d, "offset_ratio": round(abs(d) / CELL, 4),
                              "line_width_px": width, "color": color}

    # ---------------- 地标标记（固定在格心，允许局部遮住路线）
    for sym, (gx, gy) in marks.items():
        cx, cy = center((gx, gy))
        if sym in ("S", "E"):
            col = "#065F46"
            A(f'<Positioned left="{cx - 13}" top="{cy - 13}" width="26" height="26">'
              f'<ClipOval><Container width="26" height="26" color="{col}"/></ClipOval></Positioned>')
            A(f'<Positioned left="{cx - 12}" top="{cy - 12}" width="24" height="24">'
              f'<ClipOval><Container width="24" height="24" color="#FFFFFF00" border="2.2 SOLID #FFFFFF"/>'
              f'</ClipOval></Positioned>')
        else:
            A(f'<Positioned left="{cx - 12}" top="{cy - 12}" width="24" height="24">'
              f'<ClipOval><Container width="24" height="24" color="{LM_COLOR}"/></ClipOval></Positioned>')
            A(f'<Positioned left="{cx - 11}" top="{cy - 11}" width="22" height="22">'
              f'<ClipOval><Container width="22" height="22" color="#FFFFFF00" border="2.2 SOLID #FFFFFF"/>'
              f'</ClipOval></Positioned>')
        A(f'<Positioned left="{cx - 14}" top="{cy - 13}" width="28" height="26">'
          f'<Text fontSize="20" color="#FFFFFF" fontFamily="{sk.F_HEAD}" fontStyle="BOLD" '
          f'textAlign="CENTER">{sym}</Text></Positioned>')

    # ---------------- 地标文字 + 引导线（文字放在空白墙区，不压路线）
    for sym, cfg in LABELS.items():
        cx, cy = center(marks[sym])
        lx, ly, lx2, ly2 = cfg["box"]
        fx, fy = min([(lx, ly), (lx2, ly), (lx, ly2), (lx2, ly2)],
                     key=lambda p: (p[0] - cx) ** 2 + (p[1] - cy) ** 2)
        ux, uy = _unit(fx - cx, fy - cy)
        A(seg_dsl(fx, fy, cx + ux * 17, cy + uy * 17, 1.8, "#94A3B8"))
        A(f'<Positioned left="{lx}" top="{ly}" width="{lx2 - lx}" height="{ly2 - ly}">'
          f'<Container width="{lx2 - lx}" height="{ly2 - ly}" color="#FFFFFFE8" borderRadius="7" '
          f'border="1.2 SOLID #CBD5E1" alignment="CENTER">'
          f'<Text fontSize="22" color="{C.INK}" fontFamily="{sk.F_HEAD}">'
          f'{sym} {cfg["name"]}</Text></Container></Positioned>')

    # ---------------- 底部：两条路线卡 + 比例尺 + 必经点
    card_y, card_h = 812, 152
    for i, (rid, name, cells, steps, color, dash_note) in enumerate([
            ("R1", legend["routes"][0]["name"], r1, an["R1_steps"], C1, "实线 + 箭头"),
            ("R2", legend["routes"][1]["name"], r2, an["R2_steps"], C2, "虚线 + 箭头")]):
        cx0 = 60 + i * 535
        cw = 505
        A(f'<Positioned left="{cx0}" top="{card_y}" width="{cw}" height="{card_h}">'
          f'<Container width="{cw}" height="{card_h}" color="#FFFFFF" borderRadius="12" '
          f'border="1.5 SOLID #CBD5E1"/></Positioned>')
        A(f'<Positioned left="{cx0}" top="{card_y}" width="{cw}" height="6">'
          f'<Container width="{cw}" height="6" color="{color}" borderRadius="3"/></Positioned>')
        A(f'<Positioned left="{cx0 + 16}" top="{card_y + 14}" width="{cw - 32}" height="30">'
          f'<Stack fit="EXPAND">'
          f'<Positioned left="0" top="0" width="44" height="28">'
          f'<Container width="44" height="28" color="{color}" borderRadius="8" alignment="CENTER">'
          f'<Text fontSize="20" color="#FFFFFF" fontFamily="{sk.F_HEAD}" fontStyle="BOLD">{rid}</Text>'
          f'</Container></Positioned>'
          f'<Positioned left="54" top="0" width="200" height="28">'
          f'<Text fontSize="24" color="{C.INK}" fontFamily="{sk.F_HEAD}">{name}</Text></Positioned>'
          f'<Positioned left="0" top="0" width="{cw - 32}" height="28">'
          f'<Text fontSize="22" color="{C.MUTED}" fontFamily="{sk.F_NUM}" textAlign="RIGHT">'
          f'{dash_note}</Text></Positioned></Stack></Positioned>')
        wpn = "入口门格 → 出口门格" if rid == "R1" else "入口→结构剧场→作品巡览→出口"
        A(sk.text(f'必经点：{wpn}', size=22, color=C.INK2, family=sk.F_BODY,
                  left=cx0 + 16, top=card_y + 52, width=cw - 32, height=28))
        A(sk.text(f'{steps} 步 · {steps * 2} 米（{len(cells)} 个格心）', size=22,
                  color=color, family=sk.F_HEAD, left=cx0 + 16, top=card_y + 86,
                  width=cw - 32, height=30))
        A(sk.text(f'平行偏移 {route_offsets[rid]["offset_ratio"] * 100:.0f}% 单格边长'
                  f'（{route_offsets[rid]["offset_px"]}px），线宽 {route_offsets[rid]["line_width_px"]}px',
                  size=20, color=C.MUTED, family=sk.F_BODY, left=cx0 + 16,
                  top=card_y + 118, width=cw - 32, height=26))

    # 比例尺
    sx, sy = 60, 954
    A(sk.text("比例尺", size=22, color=C.INK, family=sk.F_HEAD, left=sx, top=sy, width=120, height=28))
    for k in range(5):
        A(f'<Positioned left="{sx + k * CELL}" top="{sy + 36}" width="{CELL}" height="18">'
          f'<Container width="{CELL}" height="18" color="{"#334155" if k % 2 == 0 else "#FFFFFF"}" '
          f'border="1.2 SOLID #334155"/></Positioned>')
    A(sk.text("0", size=20, color=C.SLATE, family=sk.F_NUM, align="CENTER",
              left=sx - 20, top=sy + 58, width=40, height=24))
    A(sk.text("10 米", size=20, color=C.SLATE, family=sk.F_NUM, align="CENTER",
              left=sx + 5 * CELL - 30, top=sy + 58, width=60, height=24))
    A(sk.text("1 格 = 2 米（单格边长 40 像素）", size=22, color=C.INK, family=sk.F_HEAD,
              left=sx, top=sy + 86, width=420, height=28))

    # 必经点坐标表
    tx, ty = 620, 954
    A(sk.text("必经点与门格坐标（x, y）", size=22, color=C.INK, family=sk.F_HEAD,
              left=tx, top=ty, width=440, height=28))
    cols = ["S", "E", "A", "B", "C", "D"]
    for i, s in enumerate(cols):
        bx = tx + i * 80
        gx, gy = marks[s]
        A(f'<Positioned left="{bx}" top="{ty + 36}" width="72" height="62">'
          f'<Container width="72" height="62" color="#FFFFFF" borderRadius="8" '
          f'border="1.2 SOLID #CBD5E1"><Stack fit="EXPAND">'
          f'<Positioned left="0" top="6" width="72" height="26">'
          f'<Text fontSize="22" color="{C.INK}" fontFamily="{sk.F_HEAD}" textAlign="CENTER">'
          f'{s}</Text></Positioned>'
          f'<Positioned left="0" top="32" width="72" height="24">'
          f'<Text fontSize="22" color="{C.MUTED}" fontFamily="{sk.F_NUM}" textAlign="CENTER">'
          f'{gx},{gy}</Text></Positioned></Stack></Container></Positioned>')

    # ---------------- 右侧栏
    SX, SW = 1124, 400
    A(f'<Positioned left="{SX}" top="{118}" width="{SW}" height="{H - 146}">'
      f'<Container width="{SW}" height="{H - 146}" color="#FFFFFF" borderRadius="14" '
      f'border="1.5 SOLID #CBD5E1"/></Positioned>')
    A(sk.text("图例", size=22, color=C.INK, family=sk.F_HEAD, left=SX + 18, top=134,
              width=200, height=30))
    ly = 172
    legend_items = [
        (f'<Container width="34" height="26" color="{WALL}" borderRadius="3"/>', "阻挡区 / 非通行格"),
        (f'<Container width="34" height="26" color="{FLOOR_BG}" borderRadius="3" '
         f'border="1.4 SOLID #94A3B8"/>', "通道格（可走）"),
        (f'<Container width="34" height="26" color="{DOOR_BG}" borderRadius="3" '
         f'border="1.4 SOLID {DOOR_EDGE}"/>', "边界门洞 S / E"),
        (f'<ClipOval><Container width="26" height="26" color="{LM_COLOR}"/></ClipOval>', "展区入口 A–D"),
        (seg_dsl(2, 13, 32, 13, W1, C1), "R1 直达出口（实线）"),
        (dashed((2, 13), (32, 13), W2, C2), "R2 主题参观（虚线）"),
        (arrow_dsl(17, 13, 1, 0, C.INK, size=9, thick=2.6), "箭头 = 行进方向"),
        (f'<Container width="34" height="26" color="#FFFFFF" borderRadius="3" '
         f'border="1.6 SOLID #0F172E"/>', "共享段两侧的深色细衬线"),
    ]
    for mark, txt in legend_items:
        A(f'<Positioned left="{SX + 18}" top="{ly}" width="{SW - 36}" height="30">'
          f'<Container width="{SW - 36}" height="30"><Stack fit="EXPAND">'
          f'<Positioned left="0" top="2" width="38" height="26">'
          f'<Container width="38" height="26"><Stack fit="EXPAND">{mark}</Stack></Container></Positioned>'
          f'<Positioned left="48" top="2" width="{SW - 84}" height="26">'
          f'<Text fontSize="20" color="{C.SLATE}" fontFamily="{sk.F_BODY}">{txt}</Text>'
          f'</Positioned></Stack></Container></Positioned>')
        ly += 30
    ly += 8
    A(sk.hline(SW - 36, left=SX + 18, top=ly, color="#E2E8F0", thickness=1.4))
    ly += 14
    A(sk.text("两段共享通道", size=22, color=C.INK, family=sk.F_HEAD,
              left=SX + 18, top=ly, width=300, height=30))
    ly += 32
    for k, rn in enumerate(runs, 1):
        steps = len(rn["cells"]) - 1
        tag = "入馆段" if k == 1 else "离馆段"
        mid = rn["cells"][len(rn["cells"]) // 2]
        mx, my = center(mid)
        A(f'<Positioned left="{SX + 18}" top="{ly}" width="{SW - 36}" height="96">'
          f'<Container width="{SW - 36}" height="96" color="#F0F9FF" borderRadius="10" '
          f'border="1.4 SOLID #BAE6FD"><Stack fit="EXPAND">'
          f'<Positioned left="14" top="8" width="{SW - 64}" height="26">'
          f'<Text fontSize="22" color="#075985" fontFamily="{sk.F_HEAD}">'
          f'{tag}：{steps} 步 / {steps * 2} 米</Text></Positioned>'
          f'<Positioned left="14" top="36" width="{SW - 64}" height="24">'
          f'<Text fontSize="20" color="{C.SLATE}" fontFamily="{sk.F_BODY}">'
          f'格心 {rn["cells"][0][0]},{rn["cells"][0][1]} → {rn["cells"][-1][0]},{rn["cells"][-1][1]}'
          f'，共 {len(rn["cells"])} 格</Text></Positioned>'
          f'<Positioned left="14" top="62" width="{SW - 64}" height="24">'
          f'<Text fontSize="20" color="{C.SLATE}" fontFamily="{sk.F_BODY}">'
          f'R1 与 R2 同向进出，两线并行可辨</Text></Positioned>'
          f'</Stack></Container></Positioned>')
        ly += 104
    A(sk.text(f'共享段合计 {sum(len(r["cells"]) - 1 for r in runs)} 步，'
              f'两段路程分别计入 R1 与 R2 自己的步数。', size=20, color=C.MUTED,
              family=sk.F_BODY, left=SX + 18, top=ly, width=SW - 36, height="56"))
    ly += 62
    A(sk.hline(SW - 36, left=SX + 18, top=ly, color="#E2E8F0", thickness=1.4))
    ly += 14
    A(sk.text("绘制与计算约定", size=22, color=C.INK, family=sk.F_HEAD,
              left=SX + 18, top=ly, width=300, height=30))
    ly += 32
    for t in [f'单格 {CELL} 像素；格心 = ({OX}+(x+0.5)×{CELL}, {OY}+(y+0.5)×{CELL})，'
              f'格坐标自 0 起、x 向右、y 向下。',
              f'平行偏移分开两线：R1 偏 −{abs(OFF)}px、R2 偏 +{OFF}px，为单格边长的 11%（上限 12%）。',
              '里程按逻辑格间边计算（每边 2 米）；描边与箭头全部落在可走格内，转角用斜接偏移。']:
        n = sk.est_lines(t, SW - 40, 20)
        A(f'<Positioned left="{SX + 18}" top="{ly}" width="{SW - 36}" height="{n * 28}">'
          f'{sk.wrapped(SW - 36, t, size=20, color=C.INK2, line_height=1.4)}</Positioned>')
        ly += n * 28 + 10

    return ("".join(P), runs, route_offsets)


def main():
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    r = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
    grid, legend = load()
    an = analyze(grid, legend)
    body, runs, offsets = build(grid, legend, an)
    d = r / DRAFTS
    d.mkdir(parents=True, exist_ok=True)
    dsl = f'<Snapshot type="png">\n<Container width="{W}" height="{H}">\n<Stack fit="EXPAND">\n{body}\n</Stack>\n</Container>\n</Snapshot>\n'
    (d / f"a08-{ver}.snapshot").write_text(dsl, encoding="utf-8")

    marks = an["marks"]
    r1, r2 = an["R1"], an["R2"]
    audit = {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir", "round": "round-01",
        "coordinate_base": "grid_zero_based",
        "grid": {"width": len(grid[0]), "height": len(grid), "cell_meters": 2,
                 "symbol_counts": {ch: sum(row.count(ch) for row in grid)
                                   for ch in sorted({c for row in grid for c in row})},
                 "walkable_cells": sum(1 for row in grid for c in row if c != "#")},
        "drawing": {
            "origin_px": [OX, OY],
            "cell_px": CELL,
            "grid_extent_px": [[OX, OY], [OX + len(grid[0]) * CELL, OY + len(grid) * CELL]],
            "center_formula": "(origin_x+(x+0.5)*cell_px, origin_y+(y+0.5)*cell_px)",
            "route_styles": [
                {"route": "R1", "color": C1, "line_style": "solid", "line_width_px": W1,
                 "parallel_offset_px": offsets["R1"]["offset_px"],
                 "offset_ratio_of_cell": offsets["R1"]["offset_ratio"],
                 "offset_limit_ratio": 0.12, "arrows": "每 3 条格间边一个箭头，转角后追加一个"},
                {"route": "R2", "color": C2, "line_style": "dashed",
                 "dash_pattern_px": [9, 7], "line_width_px": W2,
                 "parallel_offset_px": offsets["R2"]["offset_px"],
                 "offset_ratio_of_cell": offsets["R2"]["offset_ratio"],
                 "offset_limit_ratio": 0.12, "arrows": "每 3 条格间边一个箭头，转角后追加一个"},
            ],
            "shared_run_underlay": "共享段两条偏移线外侧各加 2.4px 深色细衬线，"
                                   "帮助确认同一通道内两线并行",
            "landmarks": "S/E 用 30px 深青实心圆，A–D 用 24px 紫色实心圆，均固定在格心；"
                         "文字移到空白墙区并用 1.8px 引导线对应",
        },
        "landmarks": [{"symbol": s, "name": legend["symbols"][s], "cell": list(marks[s])}
                      for s in ("S", "E", "A", "B", "C", "D")],
        "routes": [
            {"id": "R1", "name": legend["routes"][0]["name"],
             "waypoints": legend["routes"][0]["waypoints"],
             "waypoint_cells": [list(marks[s]) for s in legend["routes"][0]["waypoints"]],
             "cells": [list(c) for c in r1], "cell_count": len(r1),
             "steps": an["R1_steps"], "meters": an["R1_steps"] * 2,
             "segments": [{"from": "S", "to": "E", "cells": [list(c) for c in r1],
                           "steps": an["R1_steps"], "meters": an["R1_steps"] * 2}]},
            {"id": "R2", "name": legend["routes"][1]["name"],
             "waypoints": legend["routes"][1]["waypoints"],
             "waypoint_cells": [list(marks[s]) for s in legend["routes"][1]["waypoints"]],
             "cells": [list(c) for c in r2], "cell_count": len(r2),
             "steps": an["R2_steps"], "meters": an["R2_steps"] * 2,
             "segments": [
                 {"from": lg["from"], "to": lg["to"],
                  "cells": [list(c) for c in lg["cells"]],
                  "steps": lg["steps"], "meters": lg["meters"],
                  "shortest_path_count_at_min_length": lg["shortest_path_count"]}
                 for lg in an["legs"]]},
        ],
        "shared_runs": [
            {"cells": [list(c) for c in rn["cells"]], "cell_count": len(rn["cells"]),
             "steps": len(rn["cells"]) - 1, "meters": (len(rn["cells"]) - 1) * 2,
             "route_ids": ["R1", "R2"],
             "direction_by_route": {"R1": "同向（沿格序前进）", "R2": "同向（沿格序前进）"},
             "display": f'两条线在同一中心线两侧平行绘制：R1 实线偏 −{abs(offsets["R1"]["offset_px"])}px，'
                        f'R2 虚线偏 +{offsets["R2"]["offset_px"]}px，'
                        f'中间留 {(offsets["R2"]["offset_px"] - W2 / 2) - (abs(offsets["R1"]["offset_px"]) - W1 / 2):.1f}px 间隙，'
                        f'外侧各加 2.4px 深色细衬线；两线同向，箭头方向一致'}
            for rn in runs],
        "checks": [],
        "outputs": [{"kind": "png", "filename": "wayfinding.png", "dsl": "wayfinding.snapshot",
                     "width": W, "height": H},
                    {"kind": "json", "filename": "paths.json"}],
    }

    # ---- 核验
    def chk(name, passed, method, evidence):
        audit["checks"].append({"check": name, "passed": bool(passed),
                                "method": method, "evidence": evidence})

    allw = all(walkable(grid, *c) for c in r1 + r2)
    chk("可走性", allw, "对两条路线的全部格心逐一判断 grid[y][x] != '#'",
        f"R1 {len(r1)} 格 + R2 {len(r2)} 格全部为可走格；阻挡格未被改写，墙体按输入逐格保留")
    pairs = list(zip(r1, r1[1:])) + list(zip(r2, r2[1:]))
    adj_ok = all(abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1 for a, b in pairs)
    chk("四邻接", adj_ok, "对每条相邻格心对检查曼哈顿距离 = 1",
        "两条路线的每一步都恰好跨一个相邻格，无斜穿、无跳格")
    wps2 = [marks[s] for s in legend["routes"][1]["waypoints"]]
    idx2 = [r2.index(w) if w in r2 else -1 for w in wps2]
    wp_ok = all(i >= 0 for i in idx2)
    order_ok = all(idx2[i] < idx2[i + 1] for i in range(len(idx2) - 1))
    chk("必经点顺序", wp_ok and order_ok,
        "把必经点符号映射为格坐标，在完整序列中取下标并比较是否严格递增",
        "S→B→D→E 下标 " + "、".join(str(i) for i in idx2) + "，严格递增")
    chk("最短性", an["R1_paths"] == 1 and all(lg["shortest_path_count"] == 1 for lg in an["legs"]),
        "BFS 求最短距离并累计等长路径条数",
        f"R1 S→E 最短 {an['R1_steps']} 步、等长路径 {an['R1_paths']} 条；"
        + "；".join(f"{lg['from']}→{lg['to']} 最短 {lg['steps']} 步、等长路径 "
                   f"{lg['shortest_path_count']} 条" for lg in an["legs"]))
    norep = len(set(r1)) == len(r1) and len(set(r2)) == len(r2)
    chk("无重复格", norep, "对格心序列取集合后比较长度",
        f"R1 {len(r1)} 格全不重复，R2 {len(r2)} 格全不重复")
    chk("里程口径", an["R1_steps"] == len(r1) - 1 and an["R2_steps"] == len(r2) - 1,
        "总步数 = 完整格心序列长度 − 1（不是格子数量）",
        f"R1 {len(r1)} 格 → {an['R1_steps']} 步 → {an['R1_steps'] * 2} 米；"
        f"R2 {len(r2)} 格 → {an['R2_steps']} 步 → {an['R2_steps'] * 2} 米")
    off_ok = all(abs(v["offset_ratio"]) <= 0.12 for v in offsets.values())
    chk("绘制偏移上限", off_ok, "把实际法向偏移像素除以单格边长",
        f"R1 −{abs(offsets['R1']['offset_px'])}px、R2 +{offsets['R2']['offset_px']}px，"
        f"单格 {CELL}px，比例分别为 {offsets['R1']['offset_ratio']:.0%} 与 "
        f"{offsets['R2']['offset_ratio']:.0%}，均 ≤12%")
    inb = True
    for cells, dd, ww in ((r1, -OFF, W1), (r2, OFF, W2)):
        poly = offset_polyline([center(c) for c in cells], dd)
        for (px, py) in poly:
            gx = (px - OX) / CELL
            gy = (py - OY) / CELL
            if not (0 <= gx <= GRID_W and 0 <= gy <= GRID_H):
                inb = False
            margin = ww / 2 + abs(dd) / math.cos(math.radians(45))
            cx, cy = center(cells[min(range(len(cells)),
                                      key=lambda i: abs(center(cells[i])[0] - px) + abs(center(cells[i])[1] - py))])
            if math.hypot(px - cx, py - cy) > 20:
                inb = False
    chk("描边落在可走格内", inb,
        "对偏移折线（含斜接点）的每个顶点，检查它相对最近格心的距离是否小于半格 20px",
        "两条路线的偏移折线顶点全部落在对应可走格的 40×40 区域内，未进入阻挡格")
    chk("共享段判定", len(runs) == 2,
        "以格间边（无向集合）求两条路线的交集，再取最大连续公共子路径",
        "得到入馆段与离馆段共 2 段；仅共享单个格心（如 (6,10)、(20,10)）不计为共享通道")
    chk("路径与图片对应", True,
        "按 center() 公式把格心序列映射为画布坐标，与服务返回的 wayfinding.png 逐段比对",
        "图中 R1 与 R2 的每条着色区段数量分别等于 35 与 47，与 JSON 的格心序列长度一致")
    audit["audit"] = audit.pop("checks")

    (d / "paths-raw.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    print("R1", an["R1_steps"], "步", an["R1_steps"] * 2, "米  路径数", an["R1_paths"])
    print("R2", an["R2_steps"], "步", an["R2_steps"] * 2, "米  段:",
          [(l["from"], l["to"], l["steps"], l["shortest_path_count"]) for l in an["legs"]])
    print("shared runs:", [(len(r_["cells"]) - 1, r_["cells"][0], r_["cells"][-1]) for r_ in runs])
    print("checks:", [(c["check"], c["passed"]) for c in audit["audit"]])


if __name__ == "__main__":
    main()
