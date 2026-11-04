# -*- coding: utf-8 -*-
"""A08: dual-route accessible wayfinding map (1560x1080)."""
from __future__ import annotations

import json
import math
import os
import sys
from collections import deque
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import dslkit as K  # noqa: E402
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "A08"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
OUT.mkdir(parents=True, exist_ok=True)
clock = rep.TaskClock(TASK)

base = SUITE_ROOT / "tasks" / "A08-accessible-wayfinding" / "inputs"
legend = json.loads((base / "legend.json").read_text(encoding="utf-8"))
rows = [ln.rstrip("\n") for ln in (base / "floor.txt").read_text(encoding="utf-8").splitlines() if ln.strip()]
GW, GH = len(rows[0]), len(rows)
assert GW == 26 and GH == 16, (GW, GH)

WALK = set(".SEABCD")
def walkable(x, y):
    return 0 <= x < GW and 0 <= y < GH and rows[y][x] in WALK

def find(sym):
    for y in range(GH):
        for x in range(GW):
            if rows[y][x] == sym:
                return (x, y)
    raise KeyError(sym)

POS = {sym: find(sym) for sym in "SEABCD"}

def neighbours(x, y):
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, ny = x + dx, y + dy
        if walkable(nx, ny):
            yield (nx, ny)

def bfs(src, dst):
    dist = {src: 0}
    q = deque([src])
    while q:
        cur = q.popleft()
        for n in neighbours(*cur):
            if n not in dist:
                dist[n] = dist[cur] + 1
                q.append(n)
    if dst not in dist:
        return None
    # count shortest paths (cap 2) to detect multi-solution
    order = sorted(dist, key=lambda c: dist[c])
    cnt = {src: 1}
    for c in order:
        if c == src:
            continue
        cnt[c] = min(2, sum(cnt.get(n, 0) for n in neighbours(*c) if dist.get(n) == dist[c] - 1))
    path = [dst]
    cur = dst
    while cur != src:
        prev = [n for n in neighbours(*cur) if dist.get(n) == dist[cur] - 1]
        cur = prev[0]
        path.append(cur)
    path.reverse()
    return {"cells": path, "steps": dist[dst], "solutions": cnt.get(dst, 1)}

SEGS = {"R1": [("S", "E")], "R2": [("S", "B"), ("B", "D"), ("D", "E")]}
ROUTE = {}
for rid, pairs in SEGS.items():
    segs = []
    for a, b in pairs:
        r = bfs(POS[a], POS[b])
        segs.append({"from": a, "to": b, **r})
    cells = list(segs[0]["cells"])
    for s in segs[1:]:
        cells += s["cells"][1:]
    ROUTE[rid] = {
        "segs": segs, "cells": cells,
        "steps": len(cells) - 1, "meters": (len(cells) - 1) * 2,
        "unique": all(s["solutions"] == 1 for s in segs),
        "dup_cells": len(cells) != len(set(cells)),
    }

# shared runs on cell-to-cell edges
def edge_set(cells):
    return {(cells[i], cells[i + 1]) for i in range(len(cells) - 1)}
E1, E2 = edge_set(ROUTE["R1"]["cells"]), edge_set(ROUTE["R2"]["cells"])
SHARED_EDGES = E1 & E2
# group consecutive shared edges into runs (along R1 order)
runs, cur = [], []
c1 = ROUTE["R1"]["cells"]
for i in range(len(c1) - 1):
    e = (c1[i], c1[i + 1])
    if e in SHARED_EDGES:
        if cur and cur[-1] == c1[i]:
            cur.append(c1[i + 1])
        else:
            if cur:
                runs.append(cur)
            cur = [c1[i], c1[i + 1]]
    else:
        if cur:
            runs.append(cur)
            cur = []
if cur:
    runs.append(cur)

# ---------------------------------------------------------------- drawing
BG = "#F3F6FB"
WALL = "#1E2B3D"
FLOOR = "#FFFFFF"
GRIDC = "#DCE4EF"
INK = "#101B2B"
INK2 = "#4A5A72"
MUTED = "#7C8CA3"
R1C = "#1D4ED8"
R2C = "#D97706"
HILITE = "#FDE68A"

W, H = 1560, 1080
OX, OY, CELL = 36, 140, 42

def cx(x):
    return OX + (x + 0.5) * CELL

def cy(y):
    return OY + (y + 0.5) * CELL

p: list[str] = []
p.append(K.rect(0, 0, W, 6, color=R1C))
p.append(K.text(32, 18, "云构展馆 · 双路线导览", size=34, color=INK, bold=True))
p.append(K.text(32, 62, "直达出口 R1 与主题参观 R2 画在同一张 26×16 通道网格上；格心坐标为 (x,y)，"
                         "左上为 (0,0)，1 格 = 2 米。", size=19, color=INK2))

# map background + floor cells
p.append(K.rect(OX, OY, GW * CELL, GH * CELL, color=WALL, radius=6))
for y in range(GH):
    for x in range(GW):
        if rows[y][x] in WALK:
            p.append(K.rect(OX + x * CELL + 1, OY + y * CELL + 1, CELL - 2, CELL - 2, color=FLOOR,
                            radius=3))

# landmark cells
for sym, color, name in (("A", "#7C3AED", "材料实验"), ("B", "#0F766E", "结构剧场"),
                         ("C", "#BE185D", "光影工坊"), ("D", "#B45309", "作品巡览")):
    x, y = POS[sym]
    p.append(K.rect(OX + x * CELL + 3, OY + y * CELL + 3, CELL - 6, CELL - 6, color=color + "22",
                    radius=4, border=f"2 SOLID {color}"))
for sym, color in (("S", "#0F766E"), ("E", "#B91C1C")):
    x, y = POS[sym]
    p.append(K.rect(OX + x * CELL + 2, OY + y * CELL + 2, CELL - 4, CELL - 4, color=color + "33",
                    radius=4, border=f"3 SOLID {color}"))

# coordinate ticks
for x in range(0, GW, 2):
    p.append(K.text(OX + x * CELL, OY - 24, str(x), width=CELL * 1.6, size=16, color=MUTED,
                    align="LEFT"))
for y in range(0, GH, 2):
    p.append(K.text(OX - 34, OY + y * CELL + CELL / 2 - 9, str(y), width=26, size=16, color=MUTED,
                    align="RIGHT"))
p.append(K.text(OX - 34, OY - 24, "y\\x", width=30, size=15, color=MUTED, align="RIGHT"))

# ---------------------------------------------------------------- route drawing
def centers(cells):
    return [(cx(x), cy(y)) for x, y in cells]

def merge_polyline(pts):
    """collapse collinear runs -> list of (start, end) segments"""
    segs = []
    i = 0
    while i < len(pts) - 1:
        j = i + 1
        dx = pts[j][0] - pts[i][0]
        dy = pts[j][1] - pts[i][1]
        while j < len(pts) - 1:
            ndx = pts[j + 1][0] - pts[j][0]
            ndy = pts[j + 1][1] - pts[j][1]
            if (ndx == 0 and dx == 0 and (ndy > 0) == (dy > 0)) or (ndy == 0 and dy == 0 and (ndx > 0) == (dx > 0)):
                j += 1
                dx, dy = pts[j][0] - pts[i][0], pts[j][1] - pts[i][1]
            else:
                break
        segs.append((pts[i], pts[j]))
        i = j
    return segs

def thick_seg(a, b, width, color, radius=None):
    (x1, y1), (x2, y2) = a, b
    if abs(y1 - y2) < 0.01:
        p.append(K.rect(min(x1, x2) - width / 2, y1 - width / 2, abs(x2 - x1) + width, width,
                        color=color, radius=(radius if radius is not None else width / 2)))
    elif abs(x1 - x2) < 0.01:
        p.append(K.rect(x1 - width / 2, min(y1, y2) - width / 2, width, abs(y2 - y1) + width,
                        color=color, radius=(radius if radius is not None else width / 2)))
    else:  # 45 deg fallback
        length = math.hypot(x2 - x1, y2 - y1)
        ang = math.atan2(y2 - y1, x2 - x1)
        c, s = math.cos(ang), math.sin(ang)
        p.append(f'<Positioned left="{(x1 + x2) / 2 - length / 2:g}" top="{(y1 + y2) / 2 - width / 2:g}">'
                 f'<Transform matrix="({c:.6f},{s:.6f},0,0,{-s:.6f},{c:.6f},0,0,0,0,1,0,0,0,0,1)" alignment="CENTER">'
                 f'<Container width="{length + width:g}" height="{width:g}" color="{color}" borderRadius="{width/2:g}"/>'
                 f'</Transform></Positioned>')

def arrow(tip, frm, color, size=14):
    ang = math.atan2(tip[1] - frm[1], tip[0] - frm[0])
    c, s = math.cos(ang), math.sin(ang)
    px, py = tip[0] - size / 2 * c, tip[1] - size / 2 * s
    p.append(f'<Positioned left="{px - size / 2:g}" top="{py - size / 2:g}">'
             f'<Transform matrix="({c:.6f},{s:.6f},0,0,{-s:.6f},{c:.6f},0,0,0,0,1,0,0,0,0,1)" alignment="CENTER">'
             f'<SizedBox width="{size}" height="{size}">'
             f'<ClipPath path="M0 0 L{size} {size/2} L0 {size} Z"><Container color="{color}"/></ClipPath>'
             f'</SizedBox></Transform></Positioned>')

def dashed_polyline(pts, width, color, dash=9, gap=7):
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        seglen = math.hypot(x2 - x1, y2 - y1)
        t = 0.0
        while t < seglen:
            t2 = min(t + dash, seglen)
            ax = x1 + (x2 - x1) * t / seglen
            ay = y1 + (y2 - y1) * t / seglen
            bx = x1 + (x2 - x1) * t2 / seglen
            by = y1 + (y2 - y1) * t2 / seglen
            thick_seg((ax, ay), (bx, by), width, color)
            t = t2 + gap

def dir_arrows(pts, color, every=150, phase=0.0, size=14):
    """place arrowheads at arc-length intervals along the polyline"""
    acc = phase
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        seglen = math.hypot(x2 - x1, y2 - y1)
        if seglen < 1:
            continue
        d = every - acc
        while d < seglen:
            t = d / seglen
            tip = (x1 + (x2 - x1) * t, y1 + (y2 - y1) * t)
            frm = (tip[0] - (x2 - x1) / seglen * 8, tip[1] - (y2 - y1) / seglen * 8)
            arrow(tip, frm, color, size)
            d += every
        acc = (acc + seglen) % every

R1P = centers(ROUTE["R1"]["cells"])
R2P = centers(ROUTE["R2"]["cells"])

for a, b in merge_polyline(R1P):
    thick_seg(a, b, 16, R1C)
for a, b in merge_polyline(R2P):
    dashed_polyline([a, b], 8, R2C)

dir_arrows(R1P, "#FFFFFF", every=170, phase=40, size=15)
dir_arrows(R2P, "#FFFFFF", every=170, phase=120, size=18)
dir_arrows(R2P, R2C, every=170, phase=120, size=12)

# start / end markers
for pts, color in ((R1P, R1C), (R2P, R2C)):
    p.append(K.rect(pts[0][0] - 7, pts[0][1] - 7, 14, 14, color="#FFFFFF", radius=7))
    p.append(K.rect(pts[-1][0] - 8, pts[-1][1] - 8, 16, 16, color="#FFFFFF", radius=3))

# landmark symbols
for sym, color in (("A", "#7C3AED"), ("B", "#0F766E"), ("C", "#BE185D"), ("D", "#B45309"),
                   ("S", "#0F766E"), ("E", "#B91C1C")):
    x, y = POS[sym]
    mx, my = OX + (x + 0.5) * CELL, OY + (y + 0.5) * CELL
    p.append(K.rect(mx - 12, my - 12, 24, 24, color="#FFFFFF", radius=12,
                    border=f"2 SOLID {color}"))
    p.append(K.text(mx - 12, my - 10, sym, width=24, size=18, color=color, bold=True, align="CENTER"))

# landmark labels
p.append(K.text(OX + 4, OY + 13 * CELL + CELL + 6, "S 入口", width=140, size=22, color="#0F766E",
                bold=True))
p.append(K.text(OX + 25 * CELL - 106, OY + 8 * CELL + 8, "E 出口", width=98, size=22,
                color="#B91C1C", bold=True, align="RIGHT"))
p.append(K.text(OX + 12 * CELL - 40, OY + 12 * CELL + CELL + 6, "A 材料实验入口", width=200, size=22,
                color="#7C3AED", bold=True))
p.append(K.text(OX + 10 * CELL - 32, OY + 4 * CELL - 36, "B 结构剧场入口", width=210, size=22,
                color="#0F766E", bold=True))
p.append(K.text(OX + 16 * CELL - 32, OY + 2 * CELL - 36, "C 光影工坊入口", width=210, size=22,
                color="#BE185D", bold=True))
p.append(K.text(OX + 20 * CELL - 152, OY + 6 * CELL + 10, "D 作品巡览入口", width=142, size=22,
                color="#B45309", bold=True, align="RIGHT"))

dsl = K.document(W, H, p, background=BG)
path = OUT / "wayfinding.snapshot"
path.write_text(dsl, encoding="utf-8")
print("routes:", {k: (v["steps"], v["unique"], v["dup_cells"]) for k, v in ROUTE.items()})
print("shared runs:", [len(r) - 1 for r in runs])
api.write_json(TMP / "routes-calc.json", {"routes": ROUTE, "shared": runs, "pos": POS})
