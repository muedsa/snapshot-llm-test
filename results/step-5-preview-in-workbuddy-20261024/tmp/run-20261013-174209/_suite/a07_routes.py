"""A07 · 路线计算（普通 + 无障碍）。

约束语义（依题面）：
- accessible=false 的站「可乘车通过」，因此可以出现在路径中间
- 但不能作为无障碍旅程的「起点」「终点」或「换乘站」
- 换乘 = 改变乘坐线路；第一次上车不算换乘

算法：状态 (station, line)，代价字典序 (edges, transfers)，Dijkstra。
无障碍模式额外要求：起点/终点 accessible，且每次换乘所在站 accessible。
"""
from __future__ import annotations

import heapq
import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
TASK_DIR = ROOT / "tasks" / "A07-transit-topology"

NET = json.loads((TASK_DIR / "inputs" / "network.json").read_text(encoding="utf-8"))
stations = {s["id"]: s for s in NET["stations"]}
SIDS = [s["id"] for s in NET["stations"]]
lines = {l["id"]: l for l in NET["lines"]}

adj = {s: [] for s in SIDS}
for lid, l in lines.items():
    for a, b in zip(l["stations"], l["stations"][1:]):
        adj[a].append((b, lid))
        adj[b].append((a, lid))

INACCESSIBLE = {s for s in SIDS if not stations[s]["accessible"]}


def route(src, dst, *, accessible_only=False):
    """返回 {edges, path, segments, transfers} 或 None。"""
    if src == dst:
        return {"edges": 0, "path": [src], "segments": [], "transfers": 0}
    if accessible_only and (src in INACCESSIBLE or dst in INACCESSIBLE):
        return None

    dist = {}
    prev = {}
    pq = []
    # 初始：从 src 上车（第一次上车不算换乘），沿任一邻边
    for nb, lid in adj[src]:
        # 换乘站约束只在「改变线路」时生效；首发到 nb 不换乘，
        # 但若之后在 nb 换乘则 nb 必须 accessible —— 由扩展时判断
        st = (nb, lid)
        if st not in dist or (1, 0) < dist[st]:
            dist[st] = (1, 0)
            prev[st] = (src, None)
            heapq.heappush(pq, ((1, 0), st))
    while pq:
        d, st = heapq.heappop(pq)
        if dist.get(st) != d:
            continue
        cur, cur_line = st
        for nb, lid in adj[cur]:
            is_transfer = (lid != cur_line)
            if accessible_only and is_transfer and cur in INACCESSIBLE:
                continue      # 不能在无障碍缺失站换乘
            nd = (d[0] + 1, d[1] + (1 if is_transfer else 0))
            nst = (nb, lid)
            if nst not in dist or nd < dist[nst]:
                dist[nst] = nd
                prev[nst] = (cur, cur_line)
                heapq.heappush(pq, (nd, nst))

    cands = [(dist[st], st) for st in dist if st[0] == dst]
    if not cands:
        return None
    d, st = min(cands, key=lambda x: x[0])

    chain = [st]
    while True:
        p = prev[chain[-1]]
        if p[1] is None:
            break
        chain.append((p[0], p[1]))
    chain.reverse()
    path = [src] + [c[0] for c in chain]
    seq = [(c[0], c[1]) for c in chain]

    segs = []
    cur_line, seg_start, seg_st = None, None, []
    for i, (stn, lid) in enumerate(seq):
        if lid != cur_line:
            if cur_line is not None:
                segs.append({"line": cur_line, "from": seg_start, "to": seg_st[-1],
                             "stations": seg_st})
            cur_line, seg_start, seg_st = lid, path[i], [path[i]]
        seg_st.append(stn)
    if cur_line is not None:
        segs.append({"line": cur_line, "from": seg_start, "to": seg_st[-1],
                     "stations": seg_st})
    return {"edges": d[0], "path": path, "segments": segs,
            "transfers": len(segs) - 1}


if __name__ == "__main__":
    out = []
    for q in NET["queries"]:
        src, dst = q["from"], q["to"]
        n = route(src, dst)
        a = route(src, dst, accessible_only=True)
        out.append({
            "from": src, "to": dst,
            "from_name": stations[src]["name"], "to_name": stations[dst]["name"],
            "normal": n, "accessible": a,
        })
    print(json.dumps(out, ensure_ascii=False, indent=2))
