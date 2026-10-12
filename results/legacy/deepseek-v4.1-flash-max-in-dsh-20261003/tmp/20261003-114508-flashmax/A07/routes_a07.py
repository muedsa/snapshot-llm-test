"""A07: shortest journeys (fewest inter-station edges, then fewest transfers) + accessible variants.

Accessibility semantics used here (as stated in the task):
  * accessibility is a STATION facility attribute
  * a train may PASS THROUGH a non-accessible station
  * an accessible journey may not START, END or TRANSFER at a non-accessible station

That distinction is load-bearing: on this network no accessible station is shared between
line R and line B, so an accessible journey from an R-only station to a B-only station has
no solution at all - the report says so explicitly instead of quietly relaxing the rule.
"""
from __future__ import annotations

import json
import os
from collections import deque
from datetime import datetime, timedelta, timezone

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN_ID = "20261003-114508-flashmax"
TASK = "A07"
SRC = os.path.join(ROOT, "tasks", "A07-transit-topology", "inputs", "network.json")
OUT = os.path.join(ROOT, "outputs", RUN_ID, TASK)
TMP = os.path.join(ROOT, "tmp", RUN_ID, TASK)
TZ = timezone(timedelta(hours=8))
os.makedirs(OUT, exist_ok=True)
os.makedirs(TMP, exist_ok=True)

NET = json.load(open(SRC, encoding="utf-8"))
ST = {s["id"]: s for s in NET["stations"]}
LINE_OF = {l["id"]: l for l in NET["lines"]}
ADJ: dict[str, list[tuple[str, str]]] = {s: [] for s in ST}
for l in NET["lines"]:
    seq = l["stations"]
    for a, b in zip(seq, seq[1:]):
        ADJ[a].append((b, l["id"]))
        ADJ[b].append((a, l["id"]))
for k in ADJ:
    ADJ[k].sort()
SHARED = sorted([s for s in ST if len({lid for _, lid in ADJ[s]}) > 1])
INACC = [s for s in sorted(ST) if not ST[s]["accessible"]]


def find_route(src: str, dst: str, accessible_only: bool = False):
    """Lexicographic BFS over (station, line) with cost = (edges, transfers).

    In accessible mode a transition is rejected when it requires the rider to be at a
    non-accessible station for a reason other than riding through:
      * the origin must be accessible,
      * the destination must be accessible,
      * a line change must happen AT an accessible station,
      * the first boarding must happen at the accessible origin.
    """
    def can_board(s: str) -> bool:
        return ST[s]["accessible"] or not accessible_only

    if not (can_board(src) and can_board(dst)):
        return None

    start = (src, None)
    q = deque([start])
    best = {start: (0, 0)}
    parent = {start: None}
    while q:
        node = q.popleft()
        here, line = node
        edges, transfers = best[node]
        for nb, nl in ADJ[here]:
            changing = (line is not None and nl != line)
            if changing and not can_board(here):
                continue                     # cannot transfer at a non-accessible station
            nxt = (nb, nl)
            cand = (edges + 1, transfers + (1 if changing else 0))
            if nxt not in best or cand < best[nxt]:
                best[nxt] = cand
                parent[nxt] = node
                q.append(nxt)

    # the BFS above relaxes every state, so `parent` now holds a shortest-path tree and the
    # destination state with the smallest cost is the true optimum. Rebuild the path from
    # the FINAL parent pointers - reading it earlier walks a stale tree (that was the bug
    # that made the first attempt report one extra transfer and a wrong detour).
    cands = [k for k in best if k[0] == dst]
    if not cands:
        return None
    target = min(cands, key=lambda k: best[k])
    path, cur = [], target
    while cur is not None:
        path.append(cur)
        cur = parent[cur]
    path.reverse()
    stations = [p[0] for p in path]
    lines = [p[1] for p in path]

    legs = []
    for i in range(len(stations) - 1):
        leg_line = lines[i + 1]
        if legs and legs[-1]["line"] == leg_line:
            legs[-1]["stations"].append(stations[i + 1])
        else:
            legs.append({"line": leg_line, "line_name": LINE_OF[leg_line]["name"],
                         "stations": [stations[i], stations[i + 1]]})
    transfers = sum(1 for i in range(1, len(lines) - 1) if lines[i + 1] != lines[i])
    # a rider alights at station i only when the leg leaving it (lines[i+1]) differs from the
    # leg that arrived (lines[i]); the origin boards without a transfer.
    transfer_stations = [stations[i] for i in range(1, len(stations) - 1)
                         if lines[i + 1] != lines[i]]
    # stations actually boarded / alighted / transferred at (these must be accessible)
    contact = sorted({stations[0], stations[-1], *transfer_stations})
    return {
        "station_sequence": stations,
        "station_names": [ST[s]["name"] for s in stations],
        "legs": legs,
        "edge_count": len(stations) - 1,
        "station_count": len(stations),
        "transfer_count": transfers,
        "transfer_stations": transfer_stations,
        "transfer_station_names": [ST[s]["name"] for s in transfer_stations],
        "contact_stations": contact,
        "ridden_through_inaccessible": [s for s in stations if not ST[s]["accessible"]],
        "accessible_ok": all(ST[s]["accessible"] for s in contact),
    }


def diagnosis(src: str, dst: str) -> str:
    """Why an accessible journey may be impossible, in plain words."""
    if not (ST[src]["accessible"] and ST[dst]["accessible"]):
        bad = [s for s in (src, dst) if not ST[s]["accessible"]]
        return "起点或终点本身不是无障碍站：" + "、".join(f"{s} {ST[s]['name']}" for s in bad)
    lines_src = sorted({lid for _, lid in ADJ[src]})
    lines_dst = sorted({lid for _, lid in ADJ[dst]})
    reachable = set(lines_src)
    changed = True
    while changed:
        changed = False
        for s in SHARED:
            if not ST[s]["accessible"]:
                continue
            ls = {lid for _, lid in ADJ[s]}
            if ls & reachable and not ls <= reachable:
                reachable |= ls
                changed = True
    blocked = [l for l in lines_dst if l not in reachable]
    acc_shared_names = "、".join(f"{s} {ST[s]['name']}" for s in SHARED if ST[s]["accessible"])
    return (f"起点在 {'/'.join(lines_src)} 线、终点在 {'/'.join(lines_dst)} 线；"
            f"无障碍换乘站只有 {acc_shared_names}，经它无法换到 {'/'.join(blocked)} 线，"
            f"因此不存在满足约束的无障碍旅程。")


routes = []
for q in NET["queries"]:
    plain = find_route(q["from"], q["to"], accessible_only=False)
    acc = find_route(q["from"], q["to"], accessible_only=True)
    plain["accessibility"] = {
        "usable_as_accessible_journey": plain["accessible_ok"],
        "contact_stations": plain["contact_stations"],
        "reason": ("起点、终点与换乘站全部为无障碍站" if plain["accessible_ok"]
                   else "起点、终点或换乘站包含非无障碍站：" +
                        "、".join(f"{s} {ST[s]['name']}" for s in plain["contact_stations"]
                                  if not ST[s]["accessible"])),
    }
    routes.append({
        "from": q["from"], "to": q["to"],
        "from_name": ST[q["from"]]["name"], "to_name": ST[q["to"]]["name"],
        "plain_shortest": plain,
        "accessible_shortest": acc,
        "needs_accessible_alternative": not plain["accessible_ok"],
        "accessible_endpoints_ok": ST[q["from"]]["accessible"] and ST[q["to"]]["accessible"],
        "accessible_impossible_reason": None if acc else diagnosis(q["from"], q["to"]),
    })

# which accessible lines are mutually reachable through accessible interchanges only
acc_shared = [s for s in SHARED if ST[s]["accessible"]]
groups: list[set] = []
for s in acc_shared:
    ls = {lid for _, lid in ADJ[s]}
    merged = [g for g in groups if g & ls]
    for g in merged:
        groups.remove(g)
        ls |= g
    groups.append(ls)

doc = {
    "schema": "a07-routes/1",
    "generated_at": datetime.now(TZ).isoformat(),
    "timezone": "+08:00",
    "source_file": "tasks/A07-transit-topology/inputs/network.json",
    "rules": {
        "transfer_definition": "换乘 = 改变乘坐线路；第一次上车不计入换乘。",
        "selection_order": "先比站间边数最少，边数相同时再比换乘次数最少。",
        "edges_not_stations": "边数 = 相邻站之间的段数 = 站序长度 − 1；两者都给出，避免把站数当区间数。",
        "accessibility": ("accessibility 是站设施属性：列车可以驶过非无障碍站，"
                          "但无障碍旅程不能在非无障碍站上车、下车或换乘。未据此删除任何线路或车站。"),
        "accessibility_scope": "本网络的无障碍换乘站只有 " + "、".join(
            f"{s} {ST[s]['name']}" for s in acc_shared) + "；"
            "无障碍线路连通组：" + "；".join("/".join(sorted(g)) for g in groups) + "。",
    },
    "network": {
        "station_count": len(ST),
        "stations": [{"id": s, "name": ST[s]["name"], "accessible": ST[s]["accessible"],
                      "lines": sorted({lid for _, lid in ADJ[s]}),
                      "is_interchange": s in SHARED} for s in sorted(ST)],
        "lines": [{"id": l["id"], "name": l["name"], "station_count": len(l["stations"]),
                   "stations": l["stations"]} for l in NET["lines"]],
        "interchanges": SHARED,
        "interchange_names": [ST[s]["name"] for s in SHARED],
        "accessible_interchanges": acc_shared,
        "inaccessible_stations": INACC,
        "accessible_count": sum(1 for s in ST if ST[s]["accessible"]),
    },
    "routes": routes,
    "map_contract": {
        "projection": "非地理示意图：站间折线只用 45° 与 90°，不代表真实距离与方位。",
        "crossing_rule": "普通线条交叉处没有站点标记，不构成换乘；换乘只发生在共享站（图中有环状标记）。",
        "line_colour_and_letter": "每条线路同时用颜色与字母标识（R/B/G），不依赖红绿差异。",
    },
}

with open(os.path.join(OUT, "routes.json"), "w", encoding="utf-8") as fh:
    json.dump(doc, fh, ensure_ascii=False, indent=2)
with open(os.path.join(TMP, "routes.check.json"), "w", encoding="utf-8") as fh:
    json.dump({"interchanges": SHARED, "accessible_interchanges": acc_shared,
               "inaccessible": INACC, "accessible_line_groups": [sorted(g) for g in groups],
               "summary": [{"q": f"{r['from']}->{r['to']}",
                            "plain": [r["plain_shortest"]["edge_count"], r["plain_shortest"]["transfer_count"]],
                            "acc": None if r["accessible_shortest"] is None else
                                   [r["accessible_shortest"]["edge_count"], r["accessible_shortest"]["transfer_count"]],
                            "plain_acc_ok": r["plain_shortest"]["accessible_ok"]} for r in routes]},
              fh, ensure_ascii=False, indent=2)

print("换乘站:", SHARED, "| 无障碍换乘站:", acc_shared)
print("无障碍线路连通组:", [sorted(g) for g in groups])
print("非无障碍站:", INACC)
for r in routes:
    p, a = r["plain_shortest"], r["accessible_shortest"]
    print(f"{r['from']}→{r['to']}: 普通 {p['edge_count']} 边({p['station_count']} 站)/{p['transfer_count']} 换乘 "
          f"| {'、'.join(p['station_names'])} | 可作无障碍={p['accessible_ok']}")
    print("        无障碍: " + ("无 —— " + (r["accessible_impossible_reason"] or "") if a is None else
          f"{a['edge_count']} 边/ {a['transfer_count']} 换乘 | {'、'.join(a['station_names'])}"))
