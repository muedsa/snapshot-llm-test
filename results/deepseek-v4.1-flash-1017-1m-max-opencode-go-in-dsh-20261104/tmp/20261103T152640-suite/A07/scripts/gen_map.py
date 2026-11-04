# -*- coding: utf-8 -*-
"""A07 full: network map + travel card + routes.json."""
from __future__ import annotations

import heapq
import json
import math
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import dslkit as K  # noqa: E402
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "A07"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
OUT.mkdir(parents=True, exist_ok=True)
clock = rep.TaskClock(TASK)

net = json.loads((SUITE_ROOT / "tasks" / "A07-transit-topology" / "inputs" / "network.json")
                 .read_text(encoding="utf-8"))
ST = {s["id"]: s for s in net["stations"]}
LINES = {l["id"]: l for l in net["lines"]}
QUERIES = net["queries"]
LC = {"R": "#F43F5E", "B": "#3B82F6", "G": "#10B981"}
LN = {"R": "红线", "B": "蓝线", "G": "绿线"}

line_of, adj = {}, {}
for lid, line in LINES.items():
    for sid in line["stations"]:
        line_of.setdefault(sid, []).append(lid)
    for a, b in zip(line["stations"], line["stations"][1:]):
        adj.setdefault(a, []).append((b, lid))
        adj.setdefault(b, []).append((a, lid))
INTER = [s for s in ST if len(line_of[s]) > 1]

def solve(src, dst, accessible_only=False):
    if accessible_only and (not ST[src]["accessible"] or not ST[dst]["accessible"]):
        return None
    best, heap, parent = {}, [], {}
    for lid in line_of[src]:
        heapq.heappush(heap, (0, 0, (src, lid), None))
    while heap:
        e, tr, state, par = heapq.heappop(heap)
        if state in best:
            continue
        best[state] = (e, tr)
        parent[state] = par
        sid, lid = state
        if sid == dst:
            chain, cur = [], state
            while cur is not None:
                chain.append(cur)
                cur = parent[cur]
            chain.reverse()
            return {"edges": e, "transfers": tr, "chain": chain}
        for nxt, lid2 in adj[sid]:
            if lid2 == lid and (nxt, lid) not in best:
                heapq.heappush(heap, (e + 1, tr, (nxt, lid), state))
        for lid2 in line_of[sid]:
            if lid2 != lid:
                if accessible_only and not ST[sid]["accessible"]:
                    continue
                if (sid, lid2) not in best:
                    heapq.heappush(heap, (e, tr + 1, (sid, lid2), state))
    return None

def describe(res):
    chain = res["chain"]
    stations, segs = [chain[0][0]], []
    for (sid, lid), (nid, _l2) in zip(chain, chain[1:]):
        if sid != nid:
            segs.append(lid)
            stations.append(nid)
    runs = []
    for i, lid in enumerate(segs):
        if runs and runs[-1]["line"] == lid:
            runs[-1]["end_index"] = i + 1
        else:
            runs.append({"line": lid, "start_index": i, "end_index": i + 1})
    return {
        "station_ids": stations,
        "stations": [ST[s]["name"] for s in stations],
        "segments": [{"line": r["line"], "line_name": LN[r["line"]],
                      "from": ST[stations[r["start_index"]]]["name"],
                      "to": ST[stations[r["end_index"]]]["name"],
                      "stops": r["end_index"] - r["start_index"]} for r in runs],
        "edges": res["edges"], "transfers": res["transfers"],
        "transfer_station_ids": [stations[r["end_index"]] for r in runs[:-1]],
        "transfer_stations": [ST[stations[r["end_index"]]]["name"] for r in runs[:-1]],
    }

ROUTES = []
for q in QUERIES:
    a, b = q["from"], q["to"]
    plain = describe(solve(a, b, False))
    ok = (ST[a]["accessible"] and ST[b]["accessible"]
          and all(ST[s]["accessible"] for s in plain["transfer_station_ids"]))
    plain["accessible_ok"] = ok
    plain["blocking_stations"] = [] if ok else [
        ST[s]["name"] for s in plain["transfer_station_ids"] if not ST[s]["accessible"]]
    alt = None
    if not ok:
        r = solve(a, b, True)
        if r:
            alt = describe(r)
            alt["accessible_ok"] = True
    ROUTES.append({"from": a, "to": b, "from_name": ST[a]["name"], "to_name": ST[b]["name"],
                   "plain": plain, "alternative": alt})

# ---------------------------------------------------------------- MAP
BG = "#0B1220"
INK = "#EAF1FB"
INK2 = "#A7B6CC"
MUTED = "#6E8098"

POS = {
    "S01": (120, 600), "S02": (300, 600), "S03": (480, 600), "S04": (580, 600),
    "S05": (1060, 600), "S06": (1280, 600), "S12": (1440, 600),
    "S07": (400, 240), "S08": (580, 240), "S09": (580, 820), "S10": (760, 820),
    "S11": (940, 820),
    "S13": (240, 420), "S14": (400, 420), "S15": (900, 240), "S16": (1060, 740),
}
BENDS = {("S15", "S05"): [(1060, 240)]}

def seg(x1, y1, x2, y2, color, width):
    if abs(y1 - y2) < 0.01:
        p.append(K.rect(min(x1, x2) - width / 2, y1 - width / 2, abs(x2 - x1) + width, width,
                        color=color, radius=width / 2))
        return
    if abs(x1 - x2) < 0.01:
        p.append(K.rect(x1 - width / 2, min(y1, y2) - width / 2, width, abs(y2 - y1) + width,
                        color=color, radius=width / 2))
        return
    length = math.hypot(x2 - x1, y2 - y1)
    ang = math.atan2(y2 - y1, x2 - x1)
    c, s = math.cos(ang), math.sin(ang)
    p.append(f'<Positioned left="{(x1 + x2) / 2 - length / 2:g}" top="{(y1 + y2) / 2 - width / 2:g}">'
             f'<Transform matrix="({c:.6f},{s:.6f},0,0,{-s:.6f},{c:.6f},0,0,0,0,1,0,0,0,0,1)" alignment="CENTER">'
             f'<Container width="{length + width:g}" height="{width:g}" color="{color}" borderRadius="{width/2:g}"/>'
             f'</Transform></Positioned>')

p: list[str] = []
W, H = 1600, 1000
p.append(K.rect(0, 0, W, 5, color="#F43F5E"))
p.append(K.text(32, 20, "三线换乘 · 网络示意图", size=34, color=INK, bold=True))
p.append(K.text(32, 64, "非地理示意图：只表达相邻关系与换乘，拓扑距离不代表实际距离；相邻站间耗时相同、可双向乘车。",
                size=19, color=INK2))
p.append(K.text(980, 22, "图例", size=18, color=MUTED, bold=True))
lx = 980
for lid in ("R", "B", "G"):
    p.append(K.rect(lx, 52, 34, 8, color=LC[lid], radius=4))
    p.append(K.text(lx + 42, 42, f"{lid} {LN[lid]}", size=18, color=INK2))
    lx += 116
p.append(K.text(980, 74, "线路用颜色 + 字母双重编码，不依赖红绿色差", size=17, color=MUTED))
p.append(K.text(980, 98, "○ 有设施　⊘ 无设施（可乘车通过，不可作起终点或换乘站）", size=17, color=MUTED))
p.append(K.text(980, 122, "◎ 换乘站（两线共用）　线段交叉无站点处不构成换乘", size=17, color=MUTED))
p.append(K.rect(32, 152, W - 64, 1, color="#1B2840"))

def route_pts(a, b):
    return [POS[a]] + BENDS.get((a, b), []) + [POS[b]]

for lid in ("R", "B", "G"):
    seq = LINES[lid]["stations"]
    for a, b in zip(seq, seq[1:]):
        pts = route_pts(a, b)
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            seg(x1, y1, x2, y2, LC[lid], 11)

def tag(lid, x, y):
    p.append(K.rect(x - 14, y - 14, 28, 28, color=LC[lid], radius=9))
    p.append(K.text(x - 14, y - 10, lid, width=28, size=18, color="#08101C", bold=True, align="CENTER"))

tag("R", 76, 600)
tag("B", 356, 240)
tag("G", 196, 420)

LABEL = {
    "S01": (0, 30, "C"), "S02": (0, 30, "C"), "S03": (0, 30, "C"),
    "S04": (16, -74, "START"), "S05": (16, -74, "START"), "S06": (0, 30, "C"),
    "S12": (0, 30, "C"),
    "S07": (0, -74, "C"), "S08": (18, -74, "START"), "S15": (0, -74, "C"),
    "S09": (0, 30, "C"), "S10": (0, 30, "C"), "S11": (0, 30, "C"),
    "S13": (0, 30, "C"), "S14": (0, 30, "C"), "S16": (24, -12, "START"),
}
for sid, (px, py) in POS.items():
    st = ST[sid]
    inter = sid in INTER
    r = 16 if inter else 12
    p.append(K.rect(px - r - 2, py - r - 2, 2 * r + 4, 2 * r + 4, color=BG, radius=(8 if inter else r + 2)))
    p.append(K.rect(px - r, py - r, 2 * r, 2 * r, color="#FFFFFF", radius=(8 if inter else r)))
    p.append(K.rect(px - r + 4, py - r + 4, 2 * r - 8, 2 * r - 8, color=BG, radius=(6 if inter else r - 4)))
    if not st["accessible"]:
        d = r * 0.62
        seg(px - d, py + d, px + d, py - d, "#EF4444", 3)
    dx, dy, align = LABEL[sid]
    lw = 120
    lx = px + dx - (lw / 2 if align == "C" else 0)
    p.append(K.text(lx, py + dy, st["name"], width=lw, size=22, color=INK, bold=True,
                    align=("CENTER" if align == "C" else align)))
    p.append(K.text(lx, py + dy + 26, sid, width=lw, size=18, color=MUTED,
                    align=("CENTER" if align == "C" else align)))

p.append(K.rect(32, 878, W - 64, 1, color="#1B2840"))
p.append(K.text(32, 894, "换乘站：中心（R↔B）、东桥（R↔G）、工坊（B↔G）。书院、东桥、花园、公园无无障碍设施——"
                         "可乘车通过，但不能作为旅程起终点或换乘站。", width=1520, size=19, color=INK2))
p.append(K.text(32, 926, "16 站、17 段相邻关系；三条线路的交汇点都是真实车站，图中不存在“纯线条交叉”造成的换乘歧义。",
                width=1520, size=19, color=MUTED))

dsl = K.document(W, H, p, background=BG)
path = OUT / "network-map.snapshot"
path.write_text(dsl, encoding="utf-8")
warn = K.drain_warnings()
logger = api.TaskLogger(TASK, TMP)
rec = logger.render(path, OUT / "network-map.png", "map v2")
print("map:", rec["http_status"], rec["response_bytes"], rec["elapsed_s"], "s")
for x in warn:
    print(x)
if rec["http_status"] != 200:
    print((TMP / "responses" / f"{rec['id']}.bin").read_text(encoding="utf-8", errors="replace")[:1500])
    raise SystemExit(1)
print("map size:", api.measure_png(OUT / "network-map.png"))

api.write_json(OUT / "routes.json", {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "generated_at": api.iso_now(),
    "graph": {"stations": 16, "edges": sum(len(l["stations"]) - 1 for l in LINES.values()),
              "lines": {k: v["stations"] for k, v in LINES.items()},
              "interchanges": [{"id": s, "name": ST[s]["name"], "lines": line_of[s],
                                "accessible": ST[s]["accessible"]} for s in INTER],
              "inaccessible": [{"id": s, "name": ST[s]["name"]} for s in ST if not ST[s]["accessible"]]},
    "definitions": {"edge": "相邻两站之间的一段乘车区间", "transfer": "改变乘坐线路；首次上车不计为换乘",
                    "objective": "先最少站间边数，再最少换乘次数",
                    "accessible_rule": "起终点必须有设施；换乘站必须有设施；可乘车通过无设施车站"},
    "queries": ROUTES,
    "map_positions": {k: list(v) for k, v in POS.items()},
})
print("routes:", [(r["from_name"], r["to_name"], r["plain"]["edges"], r["plain"]["transfers"],
                   r["plain"]["accessible_ok"]) for r in ROUTES])
