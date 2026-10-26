"""A08 · 展馆双路线导览 — 路径计算。

规则：
- 26×16 网格，# 与非通行；. S E A B C D 可走
- 4 邻接，每步 1 格 = 2 米；路径从 S 格心到 E 格心
- R1: S→E 最短；R2: S→B→D→E 各段最短后拼接（连接点只保留一次）
"""
from __future__ import annotations

import json
import os
from collections import deque
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
TASK_DIR = ROOT / "tasks" / "A08-accessible-wayfinding"

lines = (TASK_DIR / "inputs" / "floor.txt").read_text(encoding="utf-8").splitlines()
GRID = [list(l) for l in lines]
H = len(GRID)
W = len(GRID[0])
LEG = json.loads((TASK_DIR / "inputs" / "legend.json").read_text(encoding="utf-8"))
CELL_M = LEG["grid"]["cell_meters"]

assert W == LEG["grid"]["width"] and H == LEG["grid"]["height"], (W, H)

WALKABLE = set(".SEABCD")   # '#' 是墙体/非通行区，不可走
LAND = {}
for y in range(H):
    for x in range(W):
        c = GRID[y][x]
        if c in WALKABLE:
            if c in "SEABCD":
                LAND[c] = (x, y)


def neighbors(x, y):
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, ny = x + dx, y + dy
        if 0 <= nx < W and 0 <= ny < H and GRID[ny][nx] in WALKABLE:
            yield nx, ny


def bfs(src, dst):
    """返回 (dist, path)；path 为含首尾的格序列。"""
    if src == dst:
        return 0, [src]
    dist = {src: 0}
    prev = {src: None}
    q = deque([src])
    while q:
        c = q.popleft()
        for n in neighbors(*c):
            if n not in dist:
                dist[n] = dist[c] + 1
                prev[n] = c
                if n == dst:
                    p = [n]
                    while prev[p[-1]] is not None:
                        p.append(prev[p[-1]])
                    return dist[n], p[::-1]
                q.append(n)
    return None, None


def seg_steps(cells):
    return len(cells) - 1


def concat(segs):
    """拼接多段，相邻段共用端点只保留一次。"""
    out = list(segs[0])
    for s in segs[1:]:
        out.extend(s[1:])
    return out


R1_cells = concat([bfs(LAND["S"], LAND["E"])[1]])
R2_segs = []
for a, b in zip(["S", "B", "D"], ["B", "D", "E"]):
    d, p = bfs(LAND[a], LAND[b])
    assert d is not None, (a, b)
    R2_segs.append({"from": a, "to": b, "cells": p, "steps": d, "meters": d * CELL_M})
R2_cells = concat([s["cells"] for s in R2_segs])

for name, cells in (("R1", R1_cells), ("R2", R2_cells)):
    assert len(set(cells)) == len(cells), f"{name} 有重复格"
    for i in range(len(cells) - 1):
        a, b = cells[i], cells[i + 1]
        assert abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1, f"{name} 非邻接 {a}->{b}"

# 共享通道：按「格间边」判定（两路线都经过的同一条边）
def edges_of(cells):
    return {(cells[i], cells[i + 1]) for i in range(len(cells) - 1)}


def undirected(e):
    return frozenset(e)


e1 = edges_of(R1_cells)
e2 = edges_of(R2_cells)
shared = set()
for a, b in e1 & e2:
    shared.add((a, b))
# 也可能方向相反
for a, b in e1:
    if (b, a) in e2:
        shared.add((a, b))

# 提取共享通道的连续格序列
def runs_from_edges(edges):
    """把边集合合并成连续格序列（保留原始方向）。"""
    adjm = {}
    for a, b in edges:
        adjm.setdefault(a, []).append(b)
        adjm.setdefault(b, []).append(a)
    used_nodes = set()
    runs = []
    # 端点为度数 1 的节点
    endpoints = [c for c, nb in adjm.items() if len(nb) == 1]
    for s in endpoints:
        if s in used_nodes:
            continue
        run = [s]
        used_nodes.add(s)
        cur = s
        while True:
            nxt = [n for n in adjm[cur] if n not in used_nodes]
            if not nxt:
                break
            cur = nxt[0]
            used_nodes.add(cur)
            run.append(cur)
        runs.append(run)
    # 孤立节点（度为 0）不构成通道段，忽略
    return [r for r in runs if len(r) >= 2]


shared_runs = runs_from_edges(shared)

if __name__ == "__main__":
    print("grid", W, "x", H, "cell_m", CELL_M)
    print("landmarks:", {k: v for k, v in LAND.items()})
    print("R1 steps", len(R1_cells) - 1, "meters", (len(R1_cells) - 1) * CELL_M)
    print("R1 cells", R1_cells)
    print("R2 steps", len(R2_cells) - 1, "meters", (len(R2_cells) - 1) * CELL_M)
    print("R2 cells", R2_cells)
    print("R2 segments:", [(s["from"], s["to"], s["steps"]) for s in R2_segs])
    print("shared runs:", shared_runs)
