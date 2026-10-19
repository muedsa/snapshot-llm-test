# -*- coding: utf-8 -*-
"""A07 路径核验（独立先算）：三条查询 普通/无障碍 最优旅程。
按 (区间数, 换乘数) 字典序最优；状态图 (站点,正在乘坐的线路)；
换乘=改乘线路（首次乘车不计），无障碍搜索仅允许在 accessible=true 的站改乘，
且起点/终点须 accessible（途经未设站允许通过）。"""
import json, heapq, sys
from pathlib import Path

ROOT = Path("tasks/A07-transit-topology")
net = json.loads((ROOT / "inputs/network.json").read_text(encoding="utf-8"))
ST = {s["id"]: s for s in net["stations"]}
ACC = {k: ST[k]["accessible"] for k in ST}
LINES = {l["id"]: l for l in net["lines"]}

EDGES = []          # (u, v, line) 双向
for lid, l in LINES.items():
    seq = l["stations"]
    for a, b in zip(seq, seq[1:]):
        EDGES.append((a, b, lid))
        EDGES.append((b, a, lid))

INCIDENT = {k: set() for k in ST}
for u, v, lid in EDGES:
    INCIDENT[u].add(lid)
    INCIDENT[v].add(lid)

def dijkstra(src, dst, accessible_only=False):
    """返回 (stations, edge_lines)；无可行返回 None。"""
    if accessible_only and not ACC[src]:
        return None
    INF = (10**9, 0)
    start = [(src, None)]
    dist = {}
    pq = []
    # 状态: (station, boarded_line or None)
    key0 = (src, None)
    dist[key0] = (0, 0)          # (intervals, transfers)
    parent = {}
    pq.append(((0, 0), key0))
    while pq:
        cost, cur = heapq.heappop(pq)
        if dist.get(cur, INF) < cost:
            continue
        st, line = cur
        if st == dst:
            break
        for u, v, lid in EDGES:
            if u != st:
                continue
            if accessible_only and line is not None and lid != line and not ACC[st]:
                continue     # 非无障碍站不得改乘
            nc = (cost[0] + 1, cost[1] + (1 if (line is not None and lid != line) else 0))
            nk = (v, lid)
            if nk not in dist or nc < dist[nk]:
                dist[nk] = nc
                parent[nk] = cur
                heapq.heappush(pq, (nc, nk))
    # 取终点最优状态
    finals = [(dist[k], k) for k in dist if k[0] == dst]
    if not finals:
        return None
    finals.sort()
    cost, k = finals[0]
    els_rev, stations_rev, cur = [], [], k
    while cur != key0:
        els_rev.append(cur[1])
        cur = parent[cur]
        stations_rev.append(cur[0])
    stations = [stations_rev[-1]] + list(reversed(stations_rev[:-1])) + [dst]
    els = list(reversed(els_rev))
    if accessible_only and not ACC[dst]:
        return None
    return stations, els

def describe(r):
    if not r:
        return None
    stations, els = r
    segs, i = [], 0
    while i < len(els):
        j = i
        while j < len(els) and els[j] == els[i]:
            j += 1
        segs.append((els[i], stations[i], stations[j]))
        i = j
    return {
        "stations": stations,
        "edge_lines": els,
        "intervals": len(els),
        "line_segments": [{"line": a, "from": b, "to": c} for a, b, c in segs],
        "transfers": len(segs) - 1,
        "transfer_stations": [s[2] for s in segs[:-1]],
    }

for q in net["queries"]:
    n = describe(dijkstra(q["from"], q["to"]))
    ac = describe(dijkstra(q["from"], q["to"], accessible_only=True))
    if ac is not None and not ST[q["to"]]["accessible"]:
        ac = None
    print("==", q["from"], ST[q["from"]]["name"], "->", q["to"], ST[q["to"]]["name"])
    print("  normal    :", n["stations"], n["edge_lines"], "区间", n["intervals"], "换乘", n["transfers"], n["transfer_stations"])
    if ac:
        print("  accessible:", ac["stations"], ac["edge_lines"], "区间", ac["intervals"], "换乘", ac["transfers"], ac["transfer_stations"])
    else:
        print("  accessible: 无可行（约束后）")

# 与手算断言
exp = {
 "S01->S11": (["S01","S02","S03","S04","S09","S10","S11"], ["R","R","R","B","B","B"]),
 "S13->S12n": (["S13","S14","S08","S15","S05","S06","S12"], ["G","G","G","G","R","R"]),
 "S13->S12a": (["S13","S14","S08","S04","S05","S06","S12"], ["G","G","B","R","R","R"]),
 "S07->S16": (["S07","S08","S15","S05","S16"], ["B","G","G","G"]),
}
def chk(qi, mode, exps):
    r = describe(dijkstra(qi["from"], qi["to"], mode == "a"))
    if mode == "a" and not ST[qi["to"]]["accessible"]:
        assert r is None
        return
    assert [r["stations"], r["edge_lines"]] == [e[0] for e in exps] and True, (r, exps)
for qi in net["queries"]:
    kk = qi["from"] + "->" + qi["to"]
    n = describe(dijkstra(qi["from"], qi["to"]))
    ac = describe(dijkstra(qi["from"], qi["to"], True))
    if ac is not None and not ST[qi["to"]]["accessible"]:
        ac = None
    if kk == "S01-S11" or True:
        pass
E = {
 ("S01","S11","n"): exp["S01->S11"],
 ("S13","S12","n"): exp["S13->S12n"],
 ("S13","S12","a"): exp["S13->S12a"],
 ("S07","S16","n"): exp["S07->S16"],
}
for (f, t, m), (ss, ll) in E.items():
    r = describe(dijkstra(f, t, m == "a"))
    assert [r["stations"], r["edge_lines"]] == [ss, ll], (f, t, m, r)
print("断言全部通过 ✓")
