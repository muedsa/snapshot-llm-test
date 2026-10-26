"""A08 探针：统计各段最短路径数量（DP 计数）。"""
import sys
from collections import deque

sys.path.insert(0, "tmp/run-20261013-174209/_suite")
from a08_paths import GRID, W, H, LAND, neighbors, bfs  # noqa: E402


def count_shortest(src, dst):
    dist = {src: 0}
    q = deque([src])
    while q:
        c = q.popleft()
        for n in neighbors(*c):
            if n not in dist:
                dist[n] = dist[c] + 1
                q.append(n)
    if dst not in dist:
        return None, 0
    cnt = {src: 1}
    for c in sorted(dist, key=lambda k: dist[k]):
        if c == src:
            continue
        cnt[c] = sum(cnt.get(nb, 0) for nb in neighbors(*c)
                     if dist.get(nb) == dist[c] - 1)
    return dist[dst], cnt[dst]


for a, b in [("S", "E"), ("S", "B"), ("B", "D"), ("D", "E")]:
    d, n = count_shortest(LAND[a], LAND[b])
    print(f"{a}({LAND[a]}) -> {b}({LAND[b]}): dist={d} steps, shortest_paths={n}")

# 可走格总数
walk = sum(1 for y in range(H) for x in range(W) if GRID[y][x] in ".SEABCD")
print("walkable cells:", walk)
