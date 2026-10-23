"""A07 数据模型：拓扑、双层最优路线、无障碍约束路线、示意图几何。

规则（题面原文约束）：
  * 按线路站序连接相邻站，相邻站间双向可乘，所有相邻站耗时相同
    → 图是无向图，每条边代价 1；最短时间 = 最少站间边数（区间数）。
  * 边数相同时再选换乘最少；换乘 = 改变乘坐线路，第一次上车不算。
    → 目标函数按字典序 (区间数, 换乘数)，用 (station, 当前在线路) 状态做
      字典序 Dijkstra。
  * accessible=false 的站可乘车通过，但不能作为无障碍旅程的起点、终点或换乘站。
    → 约束变体：起点/终点必须 accessible，且换线发生的那一站必须 accessible；
      中间单纯途经的站不做限制。
  * 不把站数当区间数：stations 有 n 个 → intervals = n-1。

示意图几何：站坐标在模型里写死为一张满足「全部段为水平/竖直/45°」的布局，
脚本会逐段断言角度，并逐段两两判定「除共享站以外的交叉 = 0」。
几何不满足就 raise，不产出 model.json。

路径：全部相对总任务根（path_base = suite_root）。
用法：python -I tmp/<rid>/A07/gen/a07_model.py
"""

from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a07_io as IO

NET = (IO.ROOT / "tasks" / "A07-transit-topology" / "inputs" / "network.json")

# 线路视觉属性（颜色 + 字母双编码，不只靠色相）
LINES = {
    "R": {"color": "#DC2626", "letter": "R", "name_cn": "红线"},
    "B": {"color": "#2563EB", "letter": "B", "name_cn": "蓝线"},
    "G": {"color": "#16A34A", "letter": "G", "name_cn": "绿线"},
}

# ---- 站坐标（示意图，非地理）。网格步长 120，四个走廊 y=200/400/520/640/760 ----
COORD = {
    "S01": (120, 400), "S02": (240, 400), "S03": (360, 400), "S04": (480, 400),
    "S05": (720, 400), "S06": (840, 400), "S12": (960, 280),
    "S07": (360, 640), "S08": (480, 520), "S09": (1080, 520),
    "S10": (1080, 640), "S11": (1080, 760),
    "S13": (120, 520), "S14": (240, 520), "S15": (600, 520), "S16": (720, 280),
}

# 相邻两站之间的绕行拐点（只在必要时使用，见 segments_of_line 的说明）
WAYPOINTS: dict[tuple[str, str, str], list[tuple[int, int]]] = {
    ("B", "S04", "S09"): [(480, 200), (1080, 200)],
}


# --------------------------------------------------------------------------
# 图与路由
# --------------------------------------------------------------------------

def build_graph(net: dict):
    """返回 (edges, adj)。edges 是每条边一条记录（有向展开，双向都算）。"""
    adj: dict[str, list[dict]] = defaultdict(list)
    undirected: list[dict] = []
    for line in net["lines"]:
        ids = line["stations"]
        for a, b in zip(ids, ids[1:]):
            rec = {"a": a, "b": b, "line": line["id"], "name": line["name"]}
            undirected.append(rec)
            adj[a].append({"to": b, "line": line["id"]})
            adj[b].append({"to": a, "line": line["id"]})
    return undirected, adj


def line_of_station(net: dict) -> dict[str, list[str]]:
    out: dict[str, list[str]] = defaultdict(list)
    for line in net["lines"]:
        for s in line["stations"]:
            out[s].append(line["id"])
    return dict(out)


def dijkstra(net: dict, adj, src: str, dst: str,
             accessible: dict[str, bool] | None = None) -> dict:
    """字典序 (区间数, 换乘数) 最短路。

    accessible 非 None 时启用无障碍约束：起点/终点必须 accessible，换线站必须
    accessible；中间单纯途经不限。
    返回 {stations, intervals, transfers, transfer_stations, segments, lines}
    或 None（不可达 / 起点终点不满足约束）。
    """
    if accessible is not None:
        if not accessible.get(src, False) or not accessible.get(dst, False):
            return None

    best: dict[tuple[str, str], tuple[int, int]] = {}
    prev: dict[tuple[str, str], tuple[tuple[str, str], str, bool]] = {}
    seed: list[tuple[int, int, tuple[str, str]]] = []
    for ln in line_of_station(net).get(src, []):
        best[(src, ln)] = (0, 0)
        prev[(src, ln)] = None
        seed.append((0, 0, (src, ln)))

    # 简单优先队列（图很小，16 站 3 线，够用且完全可核对）
    pq = sorted(seed)
    while pq:
        e, t, st = pq.pop(0)
        if (e, t) != best[st]:
            continue
        u, cur = st
        for nb in adj.get(u, []):
            v, ln = nb["to"], nb["line"]
            tr = 1 if ln != cur else 0
            if accessible is not None and tr and not accessible.get(u, False):
                continue            # 换乘站必须无障碍
            cand = (e + 1, t + tr)
            key = (v, ln)
            if key not in best or cand < best[key]:
                best[key] = cand
                prev[key] = (st, ln, tr == 1)
                pq.append(cand + (key,))
                pq.sort()

    cands = [(v, ln) for (v, ln), (e, t) in best.items() if v == dst]
    if not cands:
        return None
    end = min(cands, key=lambda k: (best[k][0], best[k][1]))
    e, t = best[end]

    # 回溯
    chain: list[tuple[str, str, bool]] = []   # (station, line, 是否在该站换乘到达)
    st = end
    while prev.get(st) is not None:
        p, ln, tr = prev[st]
        chain.append((st[0], ln, tr))
        st = p
    chain.reverse()
    stations = [src] + [c[0] for c in chain]

    # chain[k] 描述的是边 (stations[k] → stations[k+1])：
    #   ln = 这条边所在线路；tr = 在 stations[k] 发生了换乘
    edge_line: dict[tuple[str, str], str] = {}
    for k, (s, ln, _tr) in enumerate(chain):
        edge_line[(stations[k], s)] = ln

    # 线段：连续同线的站合并。换乘站同时是前后两段的端点（图上就是换乘标记处）。
    segments: list[dict] = []
    i = 0
    while i < len(stations):
        ln = edge_line[(stations[i], stations[i + 1])]
        j = i
        while j + 1 < len(stations) and \
                edge_line[(stations[j], stations[j + 1])] == ln:
            j += 1
        segments.append({"line": ln, "name": LINES[ln]["name_cn"],
                         "stations": stations[i:j + 1],
                         "intervals": j - i})
        i = j if j + 1 < len(stations) else j + 1

    assert sum(s["intervals"] for s in segments) == len(stations) - 1
    # 每条线段上的相邻站必须确实是该线路上真实存在的一条边
    for s in segments:
        for a, b in zip(s["stations"], s["stations"][1:]):
            assert adj_has(a, b, s["line"], adj), (a, b, s["line"])
            assert adj_has(b, a, s["line"], adj), (b, a, s["line"])
    transfer_stations = [stations[k] for k, c in enumerate(chain) if c[2]]
    assert len(transfer_stations) == t, (transfer_stations, t)
    return {
        "stations": stations,
        "intervals": len(stations) - 1,
        "transfers": t,
        "transfer_stations": transfer_stations,
        "segments": segments,
        "lines_used": sorted({s["line"] for s in segments}),
    }


def adj_has(a: str, b: str, ln: str, adj) -> bool:
    """邻接表里是否存在 a-b 且属于线路 ln（用于校验线段切分不造假）。"""
    return any(n["to"] == b and n["line"] == ln for n in adj.get(a, []))


# --------------------------------------------------------------------------
# 几何校验
# --------------------------------------------------------------------------

def segments_of_line(net: dict, line_id: str) -> list[dict]:
    """一条线路的绘制折线：站序 + 必要拐点，返回逐段 (p1,p2,from_st,to_st)。

    WAYPOINTS 记录「相邻两站之间为了避开其它线路而绕行的拐点」。只有 B 的
    S04→S09 一条边需要绕行：B 从 S04 向北出、沿 y=200 走廊东行、再在 x=1080
    南下，从而既不穿过 G 的走廊，也不与 R 共用轨道。
    """
    line = next(l for l in net["lines"] if l["id"] == line_id)
    ids = line["stations"]
    out: list[dict] = []
    for a, b in zip(ids, ids[1:]):
        path = [COORD[a]] + list(WAYPOINTS.get((line_id, a, b), [])) + [COORD[b]]
        for p1, p2 in zip(path, path[1:]):
            out.append({"p1": p1, "p2": p2, "from": a, "to": b})
    return out


def angle_of(p1, p2) -> float:
    """段与水平轴的夹角（度）；返回 0 / 45 / 90 / 135 之一才算合格。"""
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    if dx == 0:
        return 90.0
    if dy == 0:
        return 0.0
    return round(abs(math.degrees(math.atan2(abs(dy), abs(dx)))), 6)


def strict_interior_cross(s1, s2) -> tuple[float, float] | None:
    """两段是否严格内部相交。端点相接（共享站）不算交叉。"""
    a, b, c, d = s1["p1"], s1["p2"], s2["p1"], s2["p2"]

    def ccw(p, q, r):
        return (r[0] - p[0]) * (q[1] - p[1]) - (q[0] - p[0]) * (r[1] - p[1])

    def seg_int(p1, p2, p3, p4):
        d1, d2 = ccw(p3, p4, p1), ccw(p3, p4, p2)
        d3, d4 = ccw(p1, p2, p3), ccw(p1, p2, p4)
        if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and \
           ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
            t = ((p3[0] - p1[0]) * (p4[1] - p3[1]) -
                 (p3[1] - p1[1]) * (p4[0] - p3[0])) / \
                ((p4[0] - p3[0]) * (p1[1] - p2[1]) -
                 (p4[1] - p3[1]) * (p1[0] - p2[0]))
            return (p1[0] + t * (p2[0] - p1[0]), p1[1] + t * (p2[1] - p1[1]))
        return None

    pt = seg_int(a, b, c, d)
    if pt is None:
        return None
    # 交点在任一段的端点上 → 属于合法连接，不算交叉
    eps = 1e-6
    for e in (a, b, c, d):
        if abs(pt[0] - e[0]) < eps and abs(pt[1] - e[1]) < eps:
            return None
    return pt


def shared_station(s1, s2) -> str | None:
    for sid in COORD:
        p = COORD[sid]
        if p in (s1["p1"], s1["p2"], s2["p1"], s2["p2"]):
            return sid
    return None


def point_on_seg(p, p1, p2, eps=1e-6) -> bool:
    """点 p 是否落在段 p1-p2 上（含端点）。"""
    (x1, y1), (x2, y2), (x, y) = p1, p2, p
    cross = (x2 - x1) * (y - y1) - (y2 - y1) * (x - x1)
    if abs(cross) > eps:
        return False
    return (min(x1, x2) - eps <= x <= max(x1, x2) + eps) and \
           (min(y1, y2) - eps <= y <= max(y1, y2) + eps)


def check_geometry(net: dict) -> dict:
    allseg: list[dict] = []
    per_line: dict[str, list[dict]] = {}
    for lid in ("R", "B", "G"):
        segs = segments_of_line(net, lid)
        per_line[lid] = segs
        for s in segs:
            s2 = dict(s)
            s2["line"] = lid
            allseg.append(s2)

    bad_angles = [(s["line"], s["from"], s["to"], angle_of(s["p1"], s["p2"]))
                  for s in allseg if angle_of(s["p1"], s["p2"]) not in (0, 45, 90)]
    if bad_angles:
        raise AssertionError(f"存在非 45°/90° 的段: {bad_angles}")

    # 1) 不同线路的段之间严格内部相交 = 会被误读成换乘，必须为 0
    crossings = []
    for s1, s2 in combinations(allseg, 2):
        if s1["line"] == s2["line"]:
            continue
        pt = strict_interior_cross(s1, s2)
        if pt is None:
            continue
        crossings.append({"line_a": s1["line"], "line_b": s2["line"],
                          "seg_a": f"{s1['from']}-{s1['to']}",
                          "seg_b": f"{s2['from']}-{s2['to']}",
                          "point": [round(pt[0], 3), round(pt[1], 3)]})
    if crossings:
        raise AssertionError(f"存在会被误读成换乘的线路交叉: {crossings}")

    # 2) 同一线路的段之间也不该真正交叉（同线共线相接不算）
    same_line_cross = []
    for s1, s2 in combinations(allseg, 2):
        if s1["line"] != s2["line"]:
            continue
        pt = strict_interior_cross(s1, s2)
        if pt is not None:
            same_line_cross.append({"line": s1["line"],
                                    "seg_a": f"{s1['from']}-{s1['to']}",
                                    "seg_b": f"{s2['from']}-{s2['to']}",
                                    "point": [round(pt[0], 3), round(pt[1], 3)]})
    if same_line_cross:
        raise AssertionError(f"同一条线路自身交叉: {same_line_cross}")

    # 3) 每条线路的绘制折线必须经过它自己的每个站（顶点级）
    line_ids = line_of_station(net)
    vertex_missing = []
    for lid, segs in per_line.items():
        verts = {(s["p1"][0], s["p1"][1]) for s in segs} | \
                {(s["p2"][0], s["p2"][1]) for s in segs}
        for s_ in net["stations"]:
            sid = s_["id"]
            if lid in line_ids.get(sid, []) and COORD[sid] not in verts:
                vertex_missing.append({"line": lid, "station": sid})
    if vertex_missing:
        raise AssertionError(f"线路折线没有经过它自己的站: {vertex_missing}")

    # 4) 任何线路的段不得穿过它自己不含的站（否则会被误读成换乘）
    pass_through = []
    for s in allseg:
        for sid, p in COORD.items():
            if s["line"] in line_ids.get(sid, []):
                continue
            if s["from"] == sid or s["to"] == sid:
                continue
            if point_on_seg(p, s["p1"], s["p2"]):
                pass_through.append({"line": s["line"], "station": sid,
                                     "segment": f"{s['from']}-{s['to']}"})
    if pass_through:
        raise AssertionError(f"有线路穿过它不属于的站: {pass_through}")

    # 5) 换乘站：两条及以上线路的折线在同一个站点相遇
    touch: dict[str, dict] = {}
    for sid, p in COORD.items():
        lns = sorted(line_ids.get(sid, []))
        if len(lns) < 2:
            continue
        hit = []
        for lid in lns:
            on_some = any(point_on_seg(p, s["p1"], s["p2"])
                          for s in per_line[lid])
            hit.append({"line": lid, "polyline_passes": on_some})
        assert all(h["polyline_passes"] for h in hit), (sid, hit)
        touch[sid] = {"station": sid, "name": net_stations(net)[sid],
                      "lines": lns, "point": list(p),
                      "lines_on_their_polylines": hit}

    return {"angles_ok": True, "allowed_angles_deg": [0, 45, 90],
            "total_segments": len(allseg),
            "segments_per_line": {k: len(v) for k, v in per_line.items()},
            "false_crossings": [], "false_crossing_count": 0,
            "same_line_crossings": [], "same_line_crossing_count": 0,
            "line_covers_own_stations": True,
            "line_passes_foreign_station_count": 0,
            "transfer_stations_drawn": [touch[k] for k in sorted(touch)]}


def net_stations(net: dict) -> dict[str, str]:
    return {s["id"]: s["name"] for s in net["stations"]}


def seg_records(net: dict) -> list[dict]:
    """全部绘制段（按 R/B/G 顺序），带角度与像素长。"""
    out = []
    for lid in ("R", "B", "G"):
        for s in segments_of_line(net, lid):
            out.append({"line": lid, "name": LINES[lid]["name_cn"],
                        "from": s["from"], "to": s["to"],
                        "p1": list(s["p1"]), "p2": list(s["p2"]),
                        "angle_deg": angle_of(s["p1"], s["p2"]),
                        "length_px": round(math.hypot(
                            s["p2"][0] - s["p1"][0], s["p2"][1] - s["p1"][1]), 3)})
    return out


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    net = json.loads(NET.read_text(encoding="utf-8"))
    acc = {s["id"]: bool(s["accessible"]) for s in net["stations"]}
    undirected, adj = build_graph(net)
    lines_of = line_of_station(net)

    print("站数", len(net["stations"]), "边数", len(undirected),
          "（R/B/G =", [len(l['stations']) - 1 for l in net['lines']], "）")
    print("换乘站（共享站）",
          {k: v for k, v in lines_of.items() if len(v) > 1})
    print("非无障碍站", sorted(k for k, v in acc.items() if not v))

    geomo = check_geometry(net)
    print("几何：段数", geomo["total_segments"],
          "每线", geomo["segments_per_line"],
          "误读交叉", geomo["false_crossing_count"],
          "同线自交叉", geomo["same_line_crossing_count"],
          "线路穿过非本线站", geomo["line_passes_foreign_station_count"],
          "换乘站已绘制", [t["station"] for t in geomo["transfer_stations_drawn"]])

    print("\n---- 路线（字典序：区间数 → 换乘数）----")
    queries = []
    for qi, q in enumerate(net["queries"], 1):
        normal = dijkstra(net, adj, q["from"], q["to"], None)
        accessible_route = dijkstra(net, adj, q["from"], q["to"], acc)
        norm_ok = accessible_route is not None and \
            (accessible_route["intervals"], accessible_route["transfers"]) == \
            (normal["intervals"], normal["transfers"]) and \
            accessible_route["stations"] == normal["stations"]
        rec = {
            "query_id": f"Q{qi}", "from": q["from"], "to": q["to"],
            "normal": normal, "accessible": accessible_route,
        }
        queries.append(rec)
        print(f"Q{qi} {q['from']}→{q['to']}: 普通 {normal['intervals']} 区间 "
              f"{normal['transfers']} 换乘 | 无障碍 "
              f"{(accessible_route or {}).get('intervals')} 区间 "
              f"{(accessible_route or {}).get('transfers')} 换乘"
              f" | 普通即无障碍={norm_ok}")
        for tag, r in (("普通", normal), ("无障碍", accessible_route)):
            if r is None:
                continue
            for seg in r["segments"]:
                print(f"    [{tag}] {seg['line']} {seg['name']}: "
                      f"{'-'.join(seg['stations'])}  {seg['intervals']} 区间")

    model = {
        "schema_version": 1,
        "task_id": "A07",
        "path_base": "suite_root",
        "input": {"path_base": "suite_root",
                   "path": "tasks/A07-transit-topology/inputs/network.json",
                   "stations": len(net["stations"]),
                   "lines": len(net["lines"]),
                   "queries": len(net["queries"]),
                   "undirected_edges": len(undirected),
                   "edge_cost": "每条相邻站边代价 1（题面：所有相邻站耗时相同）"},
        "lines": LINES,
        "stations": {
            s["id"]: {"id": s["id"], "name": s["name"],
                      "accessible": acc[s["id"]],
                      "lines": lines_of.get(s["id"], []),
                      "is_transfer": len(lines_of.get(s["id"], [])) > 1,
                      "x": COORD[s["id"]][0], "y": COORD[s["id"]][1]}
            for s in net["stations"]},
        "geometry": {
            "is_geographic": False,
            "note": "非地理示意图：站间距离与方位不代表真实空间关系",
            "grid_step_px": 120,
            "corridor_rows_y": [200, 280, 400, 520, 640, 760],
            "segments": seg_records(net),
            "checks": geomo,
        },
        "routing": {
            "objective": "(intervals ASC, transfers ASC) 字典序；"
                         "intervals = 站间边数，transfers = 换线路次数（首次上车不计）",
            "method": "状态 (station, 当前线路) 的字典序 Dijkstra；"
                      "无障碍变体额外要求起点/终点与每个换线站 accessible=true",
            "bidirectional": True, "edge_cost_uniform": 1,
        },
        "queries": queries,
    }

    mp = IO.dirs()[1] / "model.json"
    mp.write_text(json.dumps(model, ensure_ascii=False, indent=2) + "\n",
                  encoding="utf-8")
    print("\nmodel.json →", mp.relative_to(IO.ROOT))


if __name__ == "__main__":
    main()
