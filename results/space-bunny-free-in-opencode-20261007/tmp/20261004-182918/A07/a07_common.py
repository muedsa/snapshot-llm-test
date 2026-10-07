# -*- coding: utf-8 -*-
"""A07 shared data: network graph, least-edge route solver, schematic layout geometry.

Everything here is pure computation (no rendering).  build_map_a07.py / build_card_a07.py
import from it so both deliverables are driven by exactly the same numbers.
"""
from __future__ import annotations

import json
import math
import os

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
NET_PATH = os.path.join(ROOT, "tasks", "A07-transit-topology", "inputs", "network.json")

with open(NET_PATH, encoding="utf-8") as _fh:
    NET = json.load(_fh)

STATIONS = [s["id"] for s in NET["stations"]]
NAME = {s["id"]: s["name"] for s in NET["stations"]}
ACC = {s["id"]: bool(s["accessible"]) for s in NET["stations"]}
LINES = {l["id"]: l for l in NET["lines"]}
LORDER = [l["id"] for l in NET["lines"]]
LNAME = {l["id"]: l["name"] for l in NET["lines"]}
LSEQ = {l["id"]: list(l["stations"]) for l in NET["lines"]}
QUERIES = [dict(q) for q in NET["queries"]]

# ------------------------------------------------------------------ graph
ADJ = {sid: [] for sid in STATIONS}
EDGES = []          # (a, b, line)
for _lid in LORDER:
    _seq = LSEQ[_lid]
    for _a, _b in zip(_seq, _seq[1:]):
        ADJ[_a].append((_b, _lid))
        ADJ[_b].append((_a, _lid))
        EDGES.append((_a, _b, _lid))

INTERCHANGE = sorted(sid for sid in STATIONS if len(set(l for _, l in ADJ[sid])) > 1)
LINES_AT = {}
for _sid in STATIONS:
    _seen = []
    for _nb, _l in ADJ[_sid]:
        if _l not in _seen:
            _seen.append(_l)
    LINES_AT[_sid] = _seen


def enumerate_paths(src, dst, require_accessible=False, max_edges=12):
    """All simple (state = station x boarded-line) paths src->dst.

    A transfer away from station `s` is forbidden when require_accessible and `s`
    is not accessible -- that is exactly the task's rule that a non-accessible
    station may be ridden through but may not be a transfer point of an
    accessible journey.
    """
    out = []

    def dfs(node, cur, edges, transfers, path, seen):
        if node == dst and edges > 0:
            out.append((edges, transfers, list(path)))
            return
        if edges >= max_edges:
            return
        for nb, lid in ADJ[node]:
            if require_accessible and cur is not None and cur != lid and not ACC[node]:
                continue
            state = (nb, lid)
            if state in seen:
                continue
            ntr = transfers if (cur is None or cur == lid) else transfers + 1
            seen.add(state)
            path.append(nb)
            dfs(nb, lid, edges + 1, ntr, path, seen)
            path.pop()
            seen.discard(state)

    dfs(src, None, 0, 0, [src], {(src, None)})
    return out


def solve(src, dst, require_accessible=False):
    cands = enumerate_paths(src, dst, require_accessible)
    if not cands:
        return None
    best = min((e, t, tuple(p)) for e, t, p in cands)
    out = {
        "from": src,
        "to": dst,
        "edges": best[0],
        "transfers": best[1],
        "stations": list(best[2]),
        "station_count": len(best[2]),
        "legs": legs_of(list(best[2])),
        "optimal_path_count": sum(1 for e, t, p in cands if (e, t) == (best[0], best[1])),
        "all_candidate_counts": sorted({(e, t) for e, t, _ in cands}),
    }
    out.update(accessibility_report(out))
    return out


def legs_of(seq):
    """Split a station sequence into (line, [stations...]) riding legs."""
    legs = []
    for a, b in zip(seq, seq[1:]):
        shared = [l for l in LINES_AT[a] if b in LSEQ[l]]
        assert len(shared) == 1, "edge %s-%s is not on exactly one line: %s" % (a, b, shared)
        lid = shared[0]
        if legs and legs[-1][0] == lid:
            legs[-1][1].append(b)
        else:
            legs.append([lid, [a, b]])
    return [{"line": lid, "line_name": LNAME[lid], "stations": st,
             "board": st[0], "alight": st[-1], "edges": len(st) - 1}
            for lid, st in legs]


def accessibility_report(route):
    seq = route["stations"]
    legs = route["legs"]
    transfer_at = [legs[i + 1]["board"] for i in range(len(legs) - 1)]
    passed = [s for s in seq if not ACC[s]]
    blockers = []
    if not ACC[seq[0]]:
        blockers.append("起点 %s %s 非无障碍站" % (seq[0], NAME[seq[0]]))
    if not ACC[seq[-1]]:
        blockers.append("终点 %s %s 非无障碍站" % (seq[-1], NAME[seq[-1]]))
    for t in transfer_at:
        if not ACC[t]:
            blockers.append("换乘站 %s %s 非无障碍站" % (t, NAME[t]))
    return {
        "transfer_stations": transfer_at,
        "non_accessible_stations_on_route": passed,
        "non_accessible_passed_through": [s for s in passed if s not in transfer_at],
        "accessibility_feasible": not blockers,
        "accessibility_blockers": blockers,
    }


def solve_query(q):
    src, dst = q["from"], q["to"]
    normal = solve(src, dst)
    entry = {
        "query_index": None,
        "from": src, "from_name": NAME[src], "from_accessible": ACC[src],
        "to": dst, "to_name": NAME[dst], "to_accessible": ACC[dst],
        "normal_route": normal,
        "needs_accessible_alternative": not normal["accessibility_feasible"],
        "accessible_route": None,
    }
    if not normal["accessibility_feasible"]:
        alt = solve(src, dst, require_accessible=True)
        if alt is not None:
            entry["accessible_route"] = alt
            entry["accessible_route_extra_edges"] = alt["edges"] - normal["edges"]
            entry["accessible_route_extra_transfers"] = alt["transfers"] - normal["transfers"]
    return entry


def solve_all():
    res = []
    for i, q in enumerate(QUERIES, 1):
        e = solve_query(q)
        e["query_index"] = i
        res.append(e)
    return res


# ------------------------------------------------------------------ layout
# Schematic (non-geographic) station coordinates.  Every consecutive pair of
# points in a line polyline is checked to be horizontal, vertical or exactly 45.
POS = {
    "S01": (130.0, 270.0),
    "S02": (300.0, 270.0),
    "S03": (460.0, 270.0),
    "S04": (580.0, 270.0),
    "S05": (820.0, 270.0),
    "S06": (970.0, 120.0),
    "S07": (180.0, 670.0),
    "S08": (380.0, 470.0),
    "S09": (780.0, 470.0),
    "S10": (920.0, 610.0),
    "S11": (1140.0, 610.0),
    "S12": (1150.0, 120.0),
    "S13": (120.0, 470.0),
    "S14": (260.0, 470.0),
    "S15": (500.0, 470.0),
    "S16": (1000.0, 450.0),
}
# polyline point lists per line: stations in network order + intermediate corners
# + one 46px stub past each terminus that carries the route bullet.
PATH = {
    "R": ["@R-w", "S01", "S02", "S03", "S04", "S05", "S06", "S12", "@R-e"],
    "B": ["@B-w", "S07", "S08", "S04", "S09", "S10", "S11", "@B-e"],
    "G": ["@G-w", "S13", "S14", "S08", "S15", "@G-c", "S05", "S16", "@G-e"],
}
STUB = 46.0
# bends that are not stations; still must obey the 45/90 rule
CORNER = {"@G-c": (620.0, 470.0)}


def _pt(token, toks):
    if not token.startswith("@"):
        return POS[token]
    if token in CORNER:
        return CORNER[token]
    kind = token[1:].split("-")[1]
    i = toks.index(token)
    st, anchor = (toks[i + 1], toks[i + 2]) if kind == "w" else (toks[i - 1], toks[i - 2])
    a, b = POS[st], POS[anchor]
    dx, dy = a[0] - b[0], a[1] - b[1]
    n = math.hypot(dx, dy)
    return (a[0] + dx / n * STUB, a[1] + dy / n * STUB)


def runs_of(lid):
    toks = PATH[lid]
    pts = [_pt(t, toks) for t in toks]
    return list(zip(pts, pts[1:])), pts


def is_octilinear(p, q, tol=0.5):
    dx, dy = q[0] - p[0], q[1] - p[1]
    return (abs(dy) <= tol or abs(dx) <= tol or abs(abs(dx) - abs(dy)) <= tol)


def seg_point_param(p, q, r):
    """Parameter t in [0,1] of point r projected on segment pq, or None."""
    vx, vy = q[0] - p[0], q[1] - p[1]
    L2 = vx * vx + vy * vy
    if L2 == 0:
        return None
    t = ((r[0] - p[0]) * vx + (r[1] - p[1]) * vy) / L2
    return t


def seg_dist(p, q, r):
    t = seg_point_param(p, q, r)
    if t is None:
        return math.hypot(r[0] - p[0], r[1] - p[1])
    t = max(0.0, min(1.0, t))
    return math.hypot(p[0] + t * (q[0] - p[0]) - r[0], p[1] + t * (q[1] - p[1]) - r[1])


def find_crossings():
    """Proper crossings between different lines, excluding shared stations."""
    out = []
    for la in LORDER:
        ra, _ = runs_of(la)
        for lb in LORDER:
            if lb <= la:
                continue
            rb, _ = runs_of(lb)
            for pa, qa in ra:
                for pb, qb in rb:
                    # skip if the two segments share an endpoint (a shared station)
                    if any(math.hypot(pa[0] - x, pa[1] - y) < 1 for x, y in (pb, qb)) or \
                       any(math.hypot(qa[0] - x, qa[1] - y) < 1 for x, y in (pb, qb)):
                        continue
                    den = (qa[0] - pa[0]) * (qb[1] - pb[1]) - (qa[1] - pa[1]) * (qb[0] - pb[0])
                    if abs(den) < 1e-9:
                        continue
                    t = ((pb[0] - pa[0]) * (qb[1] - pb[1]) - (pb[1] - pa[1]) * (qb[0] - pb[0])) / den
                    u = ((pb[0] - pa[0]) * (qa[1] - pa[1]) - (pb[1] - pa[1]) * (qa[0] - pa[0])) / den
                    if 0.02 < t < 0.98 and 0.02 < u < 0.98:
                        out.append({
                            "lines": (la, lb), "point": (pa[0] + t * (qa[0] - pa[0]),
                                                        pa[1] + t * (qa[1] - pa[1])),
                            "t": t, "u": u})
    return out


def validate():
    """Geometry invariants that the task demands; raises on violation."""
    problems = []
    for lid in LORDER:
        seq = LSEQ[lid]
        toks = PATH[lid]
        # station order inside the polyline must match network.json exactly
        got = [t for t in toks if not t.startswith("@")]
        if got != seq:
            problems.append("%s polyline station order %s != network order %s" % (lid, got, seq))
        for a, b in zip(seq, seq[1:]):
            if toks.index(b) - toks.index(a) not in (1, 2):
                problems.append("%s: %s->%s is not a connected run" % (lid, a, b))
        pts = [_pt(t, toks) for t in toks]
        for p, q in zip(pts, pts[1:]):
            if not is_octilinear(p, q):
                problems.append("%s run %s->%s is not 0/45/90 deg" % (lid, p, q))
    xs = [x for _, x in POS.values()]
    ys = [y for _, y in POS.values()]
    if min(xs) < 40 or max(xs) > 1220 or min(ys) < 100 or max(ys) > 740:
        problems.append("station bbox out of the map panel: x[%s,%s] y[%s,%s]"
                        % (min(xs), max(xs), min(ys), max(ys)))
    for sid in STATIONS:
        on = [l for l in LORDER if sid in LSEQ[l]]
        for l in LORDER:
            if l in on:
                continue
            for p, q in runs_of(l)[0]:
                if seg_dist(p, q, POS[sid]) < 16.0:
                    problems.append("station %s sits on line %s run %s-%s" % (sid, l, p, q))
    cr = find_crossings()
    for c in cr:
        for sid in STATIONS:
            if math.hypot(POS[sid][0] - c["point"][0], POS[sid][1] - c["point"][1]) < 60:
                problems.append("crossing %s too close to station %s"
                                % ([str(round(v, 1)) for v in c["point"]], sid))
    return problems, cr


if __name__ == "__main__":
    probs, crossings = validate()
    print("validation problems:", len(probs))
    for p in probs:
        print("  !", p)
    print("crossings:", [(c["lines"], tuple(round(v, 1) for v in c["point"])) for c in crossings])
    print("interchanges:", [(s, NAME[s], LINES_AT[s]) for s in INTERCHANGE])
    print("edges:", len(EDGES))
    res = solve_all()
    with open(os.path.join(ROOT, "routes-preview.json"), "w", encoding="utf-8") as fh:
        json.dump({"queries": res}, fh, ensure_ascii=False, indent=2)
    for e in res:
        n = e["normal_route"]
        print("Q%d %s->%s edges=%d transfers=%d stations=%d feasible=%s" % (
            e["query_index"], e["from_name"], e["to_name"], n["edges"], n["transfers"],
            n["station_count"], n["accessibility_feasible"]))
        print("   seq:", " ".join(NAME[s] for s in n["stations"]))
        print("   legs:", " -> ".join("%s(%d区间)" % (LNAME[l["line"]], l["edges"]) for l in n["legs"]))
        print("   blockers:", n["accessibility_blockers"],
              "passed:", [NAME[s] for s in n["non_accessible_passed_through"]],
              "optimal_count:", n["optimal_path_count"])
        if e["accessible_route"]:
            a = e["accessible_route"]
            print("   ALT edges=%d transfers=%d" % (a["edges"], a["transfers"]))
            print("   seq:", " ".join(NAME[s] for s in a["stations"]))
            print("   legs:", " -> ".join("%s(%d区间)" % (LNAME[l["line"]], l["edges"]) for l in a["legs"]))
