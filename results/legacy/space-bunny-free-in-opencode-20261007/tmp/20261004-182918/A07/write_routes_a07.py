# -*- coding: utf-8 -*-
"""A07 - emit outputs/20261004-182918/A07/routes.json with the solved routes and
self-checks (edges == stations-1, leg edges sum, transfer counts, accessibility)."""
from __future__ import annotations

import json
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "A07"))
import state as S  # noqa: E402
import a07_common as C  # noqa: E402

TASK = "A07"
OUT = os.path.join(S.OUT_ROOT, TASK)
TMP = os.path.join(S.TMP_ROOT, TASK)

routes = C.solve_all()
checks = []


def note(ok, msg):
    checks.append({"check": msg, "passed": bool(ok)})
    assert ok, msg


def dump(route):
    seq = route["stations"]
    out = {
        "station_ids": list(seq),
        "station_names": [C.NAME[s] for s in seq],
        "station_sequence_with_flags": [
            {"id": s, "name": C.NAME[s], "accessible": C.ACC[s],
             "role": ("起点" if i == 0 else "终点" if i == len(seq) - 1 else
                      "换乘站" if s in route["transfer_stations"] else "经过站")}
            for i, s in enumerate(seq)],
        "station_count": len(seq),
        "edges_between_stations": route["edges"],
        "edges_equal_station_count_minus_one": len(seq) - 1 == route["edges"],
        "transfers": route["transfers"],
        "transfer_stations": [
            {"id": s, "name": C.NAME[s], "accessible": C.ACC[s],
             "lines": [C.LNAME[l] for l in C.LINES_AT[s]]}
            for s in route["transfer_stations"]],
        "legs": [
            {"sequence_index": i + 1, "line_id": leg["line"], "line_name": leg["line_name"],
             "board": leg["board"], "board_name": C.NAME[leg["board"]],
             "alight": leg["alight"], "alight_name": C.NAME[leg["alight"]],
             "station_ids": leg["stations"],
             "station_names": [C.NAME[s] for s in leg["stations"]],
             "edges": leg["edges"]}
            for i, leg in enumerate(route["legs"])],
        "leg_edges_sum": sum(l["edges"] for l in route["legs"]),
        "leg_count": len(route["legs"]),
        "transfers_equal_leg_count_minus_one": len(route["legs"]) - 1 == route["transfers"],
        "accessibility": {
            "origin_accessible": C.ACC[seq[0]],
            "destination_accessible": C.ACC[seq[-1]],
            "all_transfer_stations_accessible": all(C.ACC[s] for s in route["transfer_stations"]),
            "feasible_as_accessible_journey": route["accessibility_feasible"],
            "blockers": route["accessibility_blockers"],
            "non_accessible_passed_through": [
                {"id": s, "name": C.NAME[s]} for s in route["non_accessible_passed_through"]],
            "note": "非无障碍站仍完整保留在线路上，可乘车经过；只是不能作为无障碍旅程的"
                    "起点、终点或换乘站。",
        },
        "optimal_route_count_at_same_cost": route["optimal_path_count"],
        "all_distinct_edge_transfer_costs_for_this_pair": [
            {"edges": e, "transfers": t} for e, t in route["all_candidate_counts"]],
    }
    return out


queries = []
for e in routes:
    n = e["normal_route"]
    item = {
        "query_index": e["query_index"],
        "from": e["from"], "from_name": e["from_name"],
        "to": e["to"], "to_name": e["to_name"],
        "objective": "先最少站间区间数（边数），边数相同时取换乘次数更少者；"
                     "仍相同时按站序字典序取定，过程可复现。",
        "shortest_ordinary_route": dump(n),
        "can_be_used_as_accessible_journey": n["accessibility_feasible"],
        "accessible_alternative_required": e["needs_accessible_alternative"],
        "accessible_alternative_route": dump(e["accessible_route"]) if e["accessible_route"] else None,
    }
    if e["accessible_route"]:
        item["accessible_alternative_delta"] = {
            "extra_edges": e["accessible_route_extra_edges"],
            "extra_transfers": e["accessible_route_extra_transfers"],
            "explanation": "普通最短路线的换乘站 %s 非无障碍；改在 %s 换乘后区间数不变，"
                           "换乘次数由 %d 增为 %d，是满足无障碍约束的最短路线。"
                           % ("、".join(C.NAME[s] for s in n["transfer_stations"]
                                     if not C.ACC[s]),
                              "、".join(C.NAME[s] for s in e["accessible_route"]["transfer_stations"]),
                              n["transfers"], e["accessible_route"]["transfers"]),
        }
    queries.append(item)
    note(n["edges"] == n["station_count"] - 1,
         "Q%d edges(%d) == stations(%d) - 1" % (e["query_index"], n["edges"], n["station_count"]))
    note(sum(l["edges"] for l in n["legs"]) == n["edges"],
         "Q%d leg edges sum == total edges" % e["query_index"])
    note(len(n["legs"]) - 1 == n["transfers"],
         "Q%d transfers == legs - 1" % e["query_index"])
    if e["accessible_route"]:
        a = e["accessible_route"]
        note(a["edges"] == a["station_count"] - 1, "Q%d alt edges == stations - 1" % e["query_index"])
        note(C.ACC[a["stations"][0]] and C.ACC[a["stations"][-1]]
             and all(C.ACC[s] for s in a["transfer_stations"]),
             "Q%d alt route satisfies the accessibility constraint" % e["query_index"])
        note(a["edges"] >= n["edges"], "Q%d alt route is not shorter than the ordinary one" % e["query_index"])

# every line must be connected exactly as network.json orders it
for lid in C.LORDER:
    seq = C.LSEQ[lid]
    note(len(seq) == len(set(seq)), "line %s has no repeated station" % lid)
    for a, b in zip(seq, seq[1:]):
        pair = (b, lid) in C.ADJ[a] and (a, lid) in C.ADJ[b]
        note(pair, "line %s connects %s-%s in both directions" % (lid, a, b))
note(sum(len(C.LSEQ[l]) - 1 for l in C.LORDER) == len(C.EDGES),
     "sum of per-line consecutive pairs == edge count (%d)" % len(C.EDGES))

doc = {
    "task": "A07",
    "title": "三线换乘图与路线核验",
    "generated_by": "tmp/20261004-182918/A07/a07_common.py (solve_all) + "
                    "tmp/20261004-182918/A07/build_map_a07.py + build_card_a07.py",
    "input": "tasks/A07-transit-topology/inputs/network.json",
    "definitions": {
        "edge": "一条边 = 同一线路站序中两个相邻站之间的一段，双向可走，所有边耗时相同。",
        "station_count_vs_edges": "区间数（边数）= 经过的站数 − 1；两者不可混用。",
        "transfer": "换乘 = 改变所乘坐的线路；第一次上车不计为换乘。因此换乘次数 = 乘车段数 − 1。",
        "accessibility": "accessibility 是车站设施属性。非无障碍站仍在该线路上、可以乘车经过，"
                         "但不能作为无障碍旅程的起点、终点或换乘站；无障碍约束不删除任何线路或车站。",
        "tie_breaking": "先最小化边数；边数相同再最小化换乘次数；两者都相同则按站序字典序，"
                        "保证结果唯一可复现。",
    },
    "network_summary": {
        "station_count": len(C.STATIONS),
        "stations": [{"id": s, "name": C.NAME[s], "accessible": C.ACC[s]} for s in C.STATIONS],
        "accessible_station_count": sum(1 for s in C.STATIONS if C.ACC[s]),
        "non_accessible_station_ids": [s for s in C.STATIONS if not C.ACC[s]],
        "lines": [{"id": l, "name": C.LNAME[l], "station_ids": C.LSEQ[l],
                   "station_count": len(C.LSEQ[l]), "edge_count": len(C.LSEQ[l]) - 1}
                  for l in C.LORDER],
        "interchange_stations": [{"id": s, "name": C.NAME[s],
                                  "lines": [C.LNAME[l] for l in C.LINES_AT[s]],
                                  "accessible": C.ACC[s]} for s in C.INTERCHANGE],
        "total_edges": len(C.EDGES),
        "edges": [{"a": a, "b": b, "line_id": l, "line_name": C.LNAME[l]} for a, b, l in C.EDGES],
        "topology_notes": "三条线路在图上共 1 处纯线条交叉（绿线 × 蓝线），该处没有任何车站，"
                          "因此不可换乘；全网只有 3 个换乘站（S04/S05/S08），均为两条线共站。",
    },
    "queries": queries,
    "self_checks": {"total": len(checks), "all_passed": all(c["passed"] for c in checks),
                    "checks": checks},
}

path = os.path.join(OUT, "routes.json")
with open(path, "w", encoding="utf-8") as fh:
    json.dump(doc, fh, ensure_ascii=False, indent=2)
print("wrote", path, os.path.getsize(path), "bytes")
print("checks:", len(checks), "all passed:", doc["self_checks"]["all_passed"])
for q in queries:
    n = q["shortest_ordinary_route"]
    print("Q%d %s->%s  %s | edges=%d transfers=%d stations=%d acc_ok=%s" % (
        q["query_index"], q["from_name"], q["to_name"], " → ".join(n["station_names"]),
        n["edges_between_stations"], n["transfers"], n["station_count"],
        q["can_be_used_as_accessible_journey"]))
    if q["accessible_alternative_route"]:
        a = q["accessible_alternative_route"]
        print("   alt %s | edges=%d transfers=%d" % (
            " → ".join(a["station_names"]), a["edges_between_stations"], a["transfers"]))
