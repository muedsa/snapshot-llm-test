"""A08 solver probe: parse floor.txt, BFS shortest paths, report geometry."""
from __future__ import annotations

import json
import os
from collections import deque

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
BASE = os.path.join(ROOT, "tasks", "A08-accessible-wayfinding", "inputs")

raw = open(os.path.join(BASE, "floor.txt"), encoding="utf-8").read().splitlines()
GRID = [ln for ln in raw if ln.strip() != ""]
H, W = len(GRID), max(len(g) for g in GRID)
print("rows", H, "cols", W)
for i, g in enumerate(GRID):
    assert len(g) == W, (i, len(g), g)

LEG = json.load(open(os.path.join(BASE, "legend.json"), encoding="utf-8"))
MET = LEG["cell_meters"]

anchors = {}
for y, row in enumerate(GRID):
    for x, ch in enumerate(row):
        if ch != "." and ch != "#":
            anchors[ch] = (x, y)
print("anchors", anchors, {k: LEG[k] for k in anchors})

walkable = set()
for y, row in enumerate(GRID):
    for x, ch in enumerate(row):
        if ch != "#":
            walkable.add((x, y))
print("walkable cells", len(walkable), "total", W * H)


def bfs(src, dst):
    prev = {src: None}
    q = deque([src])
    while q:
        u = q.popleft()
        if u == dst:
            break
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            v = (u[0] + dx, u[1] + dy)
            if v in walkable and v not in prev:
                prev[v] = u
                q.append(v)
    if dst not in prev:
        return None
    path, u = [], dst
    while u is not None:
        path.append(u)
        u = prev[u]
    path.reverse()
    return path


S, E = anchors["S"], anchors["E"]
B, D = anchors["B"], anchors["D"]
A, C = anchors["A"], anchors["C"]

r1 = bfs(S, E)
print("\nroute1 steps", len(r1) - 1, "meters", (len(r1) - 1) * MET)
print(r1)

sb, bd, de = bfs(S, B), bfs(B, D), bfs(D, E)
print("\nroute2 segs", len(sb) - 1, len(bd) - 1, len(de) - 1,
      "total", len(sb) + len(bd) + len(de) - 3,
      "meters", (len(sb) + len(bd) + len(de) - 3) * MET)
print("S->B", sb)
print("B->D", bd)
print("D->E", de)

# doorways: a wall cell that is horizontally/vertically between two walkable cells
doors = set()
for y in range(H):
    for x in range(W):
        if (x, y) in walkable:
            continue
        for dx, dy in ((1, 0), (0, 1)):
            a = (x - dx, y - dy)
            b = (x + dx, y + dy)
            if a in walkable and b in walkable:
                doors.add((x, y))
print("\ndoor cells", sorted(doors))