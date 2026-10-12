"""A08 · grid wayfinding: parse floor.txt, BFS shortest paths, connectivity audit.

Run from suite root:
  python tmp/<run_id>/A08/plan_a08.py
Writes tmp/<run_id>/A08/plan.json (geometry-independent facts the painter consumes).
"""
import json
import os
from collections import deque
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
RID = os.environ["SNAPSHOT_RUN_ID"]
FLOOR = ROOT / "tasks/A08-accessible-wayfinding/inputs/floor.txt"
TEMP = ROOT / "tmp" / RID / "A08"

raw = [l for l in FLOOR.read_text(encoding="utf-8").split("\n") if l != ""]
GRID = [list(r) for r in raw]
H, W = len(GRID), len(GRID[0])
assert all(len(r) == W for r in GRID), "ragged floor"

WALK = set(".SAABCDE")


def walkable(x, y):
    return 0 <= x < W and 0 <= y < H and GRID[y][x] in WALK


def cell(x, y):
    return GRID[y][x]


MARKS = {}
for y in range(H):
    for x in range(W):
        c = GRID[y][x]
        if c in "SAABCDE":
            assert c not in MARKS, f"duplicate marker {c}"
            MARKS[c] = (x, y)

CELLS = [(x, y) for y in range(H) for x in range(W) if walkable(x, y)]
DIRS = [(1, 0), (-1, 0), (0, 1), (0, -1)]
NAME = {(1, 0): "E", (-1, 0): "W", (0, 1): "S", (0, -1): "N"}


def neighbours(p):
    x, y = p
    out = []
    for dx, dy in DIRS:
        q = (x + dx, y + dy)
        if walkable(*q):
            out.append(q)
    return out


def bfs_dist(src):
    d = {src: 0}
    dq = deque([src])
    while dq:
        p = dq.popleft()
        for q in neighbours(p):
            if q not in d:
                d[q] = d[p] + 1
                dq.append(q)
    return d


def bfs_path(src, dst, order=("S", "E", "N", "W")):
    """One deterministic shortest path: BFS layered, greedy back-walk."""
    d = bfs_dist(src)
    if dst not in d:
        return None
    # dist-to-target field drives the greedy forward walk
    dt = bfs_dist(dst)
    path = [src]
    cur = src
    while cur != dst:
        cands = []
        for q in neighbours(cur):
            if dt.get(q, 10 ** 9) == dt[cur] - 1:
                cands.append(q)
        cands.sort(key=lambda q: order.index(NAME[(q[0] - cur[0], q[1] - cur[1])]))
        assert cands, f"dead end at {cur}"
        cur = cands[0]
        path.append(cur)
    assert len(path) - 1 == d[dst]
    return path


def count_shortest(src, dst):
    d = bfs_dist(src)
    if dst not in d:
        return 0
    ways = {src: 1}
    for p in sorted(d, key=lambda k: d[k]):
        if p == src:
            continue
        ways[p] = sum(ways[q] for q in neighbours(p) if d.get(q) == d[p] - 1)
    return ways[dst]


def edges_of(path):
    return [(path[i], path[i + 1]) for i in range(len(path) - 1)]


S, E = MARKS["S"], MARKS["E"]
B, D, A, C = MARKS["B"], MARKS["D"], MARKS["A"], MARKS["C"]

r1 = bfs_path(S, E)
r1_n = count_shortest(S, E)
sb, bd, de = bfs_path(S, B), bfs_path(B, D), bfs_path(D, E)
assert sb and bd and de
r2 = sb + bd[1:] + de[1:]
assert len(r2) - 1 == (len(sb) - 1) + (len(bd) - 1) + (len(de) - 1)

# --- validation of both routes -------------------------------------------------
def validate(path, label, allow_revisit=False):
    problems = []
    for (x, y) in path:
        if not walkable(x, y):
            problems.append(f"{label}: 路径落到非可走格 {(x, y)}")
    for (p, q) in edges_of(path):
        if abs(p[0] - q[0]) + abs(p[1] - q[1]) != 1:
            problems.append(f"{label}: 非 4-邻接步 {p}->{q}")
    if len(set(path)) != len(path) and not allow_revisit:
        problems.append(f"{label}: 单段最短路内重复经过同一格")
    return problems


v1 = validate(r1, "路线一")
# 路线二是三段最短路的首尾拼接，去 B 取货必然原路折返，因此整体允许重复格，
# 但每一段单独必须是简单路径。
v2 = (validate(r2, "路线二（拼接整体）", allow_revisit=True)
      + validate(sb, "路线二 S→B 段") + validate(bd, "路线二 B→D 段")
      + validate(de, "路线二 D→E 段"))
revisits = sorted({c for c in r2 if r2.count(c) > 1})
# edges_of() is directed, so the round trip ((12,4)->(12,3) and back) never shows up
# as a repeated *directed* edge: canonicalise first, then look for duplicates.
und_r2 = [(min(a, b), max(a, b)) for a, b in edges_of(r2)]
backtrack = sorted({k for k in und_r2 if und_r2.count(k) > 1})

# --- connectivity audit --------------------------------------------------------
dS = bfs_dist(S)
unreached = [p for p in CELLS if p not in dS]
wall_count = W * H - len(CELLS)
mark_dist = {k: dS.get(v) for k, v in MARKS.items()}

# doorways: walkable cells whose removal would split the two halves / that sit in
# a wall run — reported as walkable cells flanked by wall on two opposite sides
doors = []
for (x, y) in CELLS:
    if y in (0, H - 1) or x in (0, W - 1):
        continue
    hor = (not walkable(x - 1, y)) and (not walkable(x + 1, y)) and (walkable(x, y - 1) and walkable(x, y + 1))
    ver = (not walkable(x, y - 1)) and (not walkable(x, y + 1)) and (walkable(x - 1, y) and walkable(x + 1, y))
    if hor or ver:
        doors.append({"cell": [x, y], "axis": "水平墙上的门洞" if hor else "垂直墙上的门洞"})

# --- overlap between the two routes -------------------------------------------
e1, e2 = set(map(lambda e: tuple(map(tuple, e)), edges_of(r1))), edges_of(r2)
shared = [e for e in e2 if tuple(map(tuple, e)) in e1 or tuple(map(tuple, (e[1], e[0]))) in e1]
shared_nodes = [p for p in r2 if p in set(r1)]

out = {
    "schema_version": 1,
    "path_base": "suite_root",
    "grid": {"cols": W, "rows": H, "cell_meters": 2, "movement": "4-neighbor",
             "coordinates": "zero-based (x,y), origin top-left",
             "wall_cells": wall_count, "walkable_cells": len(CELLS),
             "markers": {k: list(v) for k, v in MARKS.items()}},
    "route_1": {"purpose": "S→E 最短", "cells": [list(p) for p in r1],
                "steps": len(r1) - 1, "meters": (len(r1) - 1) * 2,
                "shortest_path_count": r1_n},
    "route_2": {"purpose": "S→B→D→E，必须先到 B 再到 D，每段取最短路",
                "cells": [list(p) for p in r2],
                "steps": len(r2) - 1, "meters": (len(r2) - 1) * 2,
                "segments": [
                    {"from": "S", "to": "B", "cells": [list(p) for p in sb],
                     "steps": len(sb) - 1, "meters": (len(sb) - 1) * 2,
                     "shortest_path_count": count_shortest(S, B)},
                    {"from": "B", "to": "D", "cells": [list(p) for p in bd],
                     "steps": len(bd) - 1, "meters": (len(bd) - 1) * 2,
                     "shortest_path_count": count_shortest(B, D)},
                    {"from": "D", "to": "E", "cells": [list(p) for p in de],
                     "steps": len(de) - 1, "meters": (len(de) - 1) * 2,
                     "shortest_path_count": count_shortest(D, E)},
                ]},
    "comparison": {"route_2_minus_route_1_steps": (len(r2) - 1) - (len(r1) - 1),
                   "shared_step_count": len(shared),
                   "shared_cells": [list(p) for p in shared_nodes],
                   "route_2_revisited_cells": [list(p) for p in revisits],
                   "route_2_out_and_back_edges": [[list(a), list(b)] for a, b in backtrack]},
    "connectivity": {"bfs_from_S_reached": len(dS), "walkable_total": len(CELLS),
                     "unreached_walkable": [list(p) for p in unreached],
                     "all_walkable_connected": not unreached,
                     "marker_distance_from_S": {k: v for k, v in mark_dist.items()},
                     "doorways": doors,
                     "doorway_count": len(doors)},
    "validation": {"problems": v1 + v2, "route_1_ok": not v1, "route_2_ok": not v2},
}
TEMP.mkdir(parents=True, exist_ok=True)
(TEMP / "plan.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"r1_steps": out["route_1"]["steps"], "r1_alternatives": r1_n,
                  "r2_steps": out["route_2"]["steps"],
                  "segments": [s["steps"] for s in out["route_2"]["segments"]],
                  "shared_steps": len(shared), "shared_nodes": len(shared_nodes),
                  "doors": len(doors), "unreached": len(unreached),
                  "problems": v1 + v2}, ensure_ascii=False))
print("R1", r1)
print("R2", r2)
