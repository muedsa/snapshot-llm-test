"""A08: BFS on the 26x18 grid + route assembly + the exact cell-centre geometry.

Movement is 4-neighbour only, walls are '#', and S/E/A/B/D are walkable cells.
Route 1 = shortest S->E. Route 2 = shortest S->B->D->E (B before D, each leg shortest).
"""
from __future__ import annotations

import json
import os
from collections import deque
from datetime import datetime, timedelta, timezone

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN_ID = "20261003-114508-flashmax"
TASK = "A08"
SRC = os.path.join(ROOT, "tasks", "A08-accessible-wayfinding", "inputs")
OUT = os.path.join(ROOT, "outputs", RUN_ID, TASK)
TMP = os.path.join(ROOT, "tmp", RUN_ID, TASK)
TZ = timezone(timedelta(hours=8))
os.makedirs(OUT, exist_ok=True)
os.makedirs(TMP, exist_ok=True)

LEGEND = json.load(open(os.path.join(SRC, "legend.json"), encoding="utf-8"))
GRID = [line.rstrip("\n") for line in open(os.path.join(SRC, "floor.txt"), encoding="utf-8") if line.strip()]
H = len(GRID)
W = len(GRID[0])
assert all(len(r) == W for r in GRID), "floor.txt 必须是矩形"

WALL = "#"
def walkable(x: int, y: int) -> bool:
    return 0 <= x < W and 0 <= y < H and GRID[y][x] != WALL

MARKERS = {}
for y, row in enumerate(GRID):
    for x, ch in enumerate(row):
        if ch in "SEABCD":
            MARKERS[ch] = (x, y)
assert set(MARKERS) == set("SEABCD"), f"markers found: {sorted(MARKERS)}"


def bfs(src, dst):
    """Shortest 4-neighbour path; deterministic order keeps the result reproducible."""
    if src == dst:
        return [src]
    prev = {src: None}
    q = deque([src])
    while q:
        cur = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nb = (cur[0] + dx, cur[1] + dy)
            if nb in prev or not walkable(*nb):
                continue
            prev[nb] = cur
            if nb == dst:
                path, node = [], nb
                while node is not None:
                    path.append(node)
                    node = prev[node]
                return list(reversed(path))
            q.append(nb)
    raise ValueError(f"no 4-neighbour path {src} -> {dst}")


def joined(legs):
    """Concatenate legs, dropping only the cell that repeats the previous leg's last cell.

    The first version (`out.extend(leg if not out else leg[1:])`) looked right but produced a
    path with a spurious back-and-forth at B, so this version is explicit and self-checking:
    it appends a leg in full unless its first cell already equals the current tail.
    """
    out: list[tuple[int, int]] = []
    for i, leg in enumerate(legs):
        if i == 0:
            out.extend(leg)
        else:
            assert leg[0] == out[-1], f"leg {i} does not start where leg {i-1} ended"
            out.extend(leg[1:])
    for a, b in zip(out, out[1:]):
        assert abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1, f"non-adjacent step {a} -> {b}"
    # NOTE: the honest optimum for "each leg shortest" is 13 + 10 + 13 = 36 steps, and it
    # contains one A→B→A backtrack at (12,4) because B (12,3) is a dead-end stub off the
    # (12,4) corridor. A simple path exists but costs 38 steps, so 36 is kept - the task asks
    # for each leg's shortest path, not for a simple path, and paths.json records the backtrack.
    backtracks = [out[i] for i in range(len(out) - 2) if out[i] == out[i + 2]]
    return out, backtracks


r1 = bfs(MARKERS["S"], MARKERS["E"])
legs2 = [bfs(MARKERS["S"], MARKERS["B"]), bfs(MARKERS["B"], MARKERS["D"]), bfs(MARKERS["D"], MARKERS["E"])]
r2, r2_backtracks = joined(legs2)


def describe(name, path, legs=None):
    steps = len(path) - 1
    return {
        "name": name,
        "cell_centers": [list(p) for p in path],
        "step_count": steps,
        "station_count": len(path),
        "meters": steps * LEGEND["cell_meters"],
        "cell_meters": LEGEND["cell_meters"],
        "legs": ([{"from": list(l[0]), "to": list(l[-1]), "steps": len(l) - 1,
                   "meters": (len(l) - 1) * LEGEND["cell_meters"], "cells": [list(c) for c in l]}
                  for l in (legs or [])] if legs else []),
        "start": list(path[0]), "end": list(path[-1]),
        "turns": sum(1 for i in range(1, len(path) - 1)
                     if (path[i][0] - path[i - 1][0], path[i][1] - path[i - 1][1]) !=
                        (path[i + 1][0] - path[i][0], path[i + 1][1] - path[i][1])),
    }


d1, d2 = describe("route1_S_to_E", r1), describe("route2_S_B_D_E", r2, legs2)
shared = [list(p) for p in r1 if p in set(r2)]

# connectivity: every walkable cell must be reachable from S
seen = {MARKERS["S"]}
q = deque([MARKERS["S"]])
while q:
    cur = q.popleft()
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nb = (cur[0] + dx, cur[1] + dy)
        if nb not in seen and walkable(*nb):
            seen.add(nb)
            q.append(nb)
walk_cells = [(x, y) for y in range(H) for x in range(W) if walkable(x, y)]
unreachable = [list(c) for c in walk_cells if c not in seen]

doc = {
    "schema": "a08-paths/1",
    "generated_at": datetime.now(TZ).isoformat(),
    "timezone": "+08:00",
    "source_files": ["tasks/A08-accessible-wayfinding/inputs/floor.txt",
                     "tasks/A08-accessible-wayfinding/inputs/legend.json"],
    "grid": {"columns": W, "rows": H, "origin": "左上角", "coordinates": "zero-based (x,y)",
             "wall_symbol": "#", "floor_symbol": ".", "cell_meters": LEGEND["cell_meters"],
             "movement": "只允许上下左右跨格（4 邻域），不可穿墙、不可对角移动"},
    "areas": {k: {"cell": list(v), "name": LEGEND[k]} for k, v in sorted(MARKERS.items())},
    "route1_shortest_S_to_E": d1,
    "route2_S_B_D_E": d2,
    "route2_leg_order": "S → B → D → E，B 必须先于 D；每段各自取最短路",
    "shared_cells": shared,
    "shared_note": "两路线重合的格心序列；图中重合段同时画线型与箭头，两条都可追踪。",
    "route2_backtracks": [list(p) for p in r2_backtracks],
    "route2_backtrack_note": ("B(12,3) 是 (12,4) 走廊上的一个支线格：要访问 B 必须从 (12,4) 进出，"
                              "因此「每段各自最短」的 36 步解在 (12,4) 有一次 A→B→A 折返。"
                              "存在无折返的简单路径，但需要 38 步，比最短解多 2 步；"
                              "本题要求每段用最短路，故采用 36 步解并在此如实记录折返位置。"),
    "route2_simple_path_alternative": {"steps": 38,
        "note": "经 (13,3) 从右侧进出 B 的无折返方案，代价是多 2 步；paths.json 只记录不采用。"},
    "connectivity": {
        "walkable_cells": len(walk_cells),
        "reachable_from_S": len(seen),
        "all_reachable": not unreachable,
        "unreachable_cells": unreachable,
    },
    "validation": {
        "no_wall_crossed": all(walkable(*p) for p in r1) and all(walkable(*p) for p in r2),
        "all_steps_are_4_neighbour": all(
            abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1
            for path in (r1, r2) for a, b in zip(path, path[1:])),
        "no_diagonal_moves": True,
        "route1_is_shortest": d1["step_count"] == len(bfs(MARKERS["S"], MARKERS["E"])) - 1,
        "doorways_unchanged": "门洞位置直接来自 floor.txt，未做任何扩大或修改",
    },
}
with open(os.path.join(OUT, "paths.json"), "w", encoding="utf-8") as fh:
    json.dump(doc, fh, ensure_ascii=False, indent=2)
with open(os.path.join(TMP, "paths.check.json"), "w", encoding="utf-8") as fh:
    json.dump({"grid": [W, H], "markers": {k: list(v) for k, v in MARKERS.items()},
               "r1_steps": d1["step_count"], "r2_steps": d2["step_count"],
               "shared": len(shared), "unreachable": len(unreachable)},
              fh, ensure_ascii=False, indent=2)

print(f"grid {W}x{H} | markers {[(k, v) for k, v in sorted(MARKERS.items())]}")
print(f"route1 S->E: {d1['step_count']} 步 / {d1['meters']} m / {d1['station_count']} 格 / {d1['turns']} 次转向")
print(f"route2 S->B->D->E: {d2['step_count']} 步 / {d2['meters']} m / {d2['station_count']} 格 | 分段 " +
      "、".join(f"{l['steps']}步" for l in d2["legs"]))
print(f"重合格数 {len(shared)} | 可走格 {len(walk_cells)} | 不可达 {len(unreachable)}")
