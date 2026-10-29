#!/usr/bin/env python3
"""A07 transit topology: compute routes, draw 1600x1000 map + 720x1280 travel card."""
import json, os, math, heapq, html
from pathlib import Path

SCRIPT = Path(__file__).resolve()
SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", SCRIPT.parents[4]))
RUN_ID = SCRIPT.parents[2].name
OUT = SUITE_ROOT / "outputs" / RUN_ID / "A07"
OUT.mkdir(parents=True, exist_ok=True)

def esc(s): return html.escape(str(s), quote=False)
def T(txt, size, color="#0B1220", bold=False, extra=""):
    st = ' fontStyle="BOLD"' if bold else ""
    return f'<Text fontFamily="Noto Sans CJK SC" fontSize="{size}" color="{color}"{st}{extra}>{esc(txt)}</Text>'

data = json.loads((SUITE_ROOT / "tasks/A07-transit-topology/inputs/network.json").read_text(encoding="utf-8"))
stations = {s["id"]: s for s in data["stations"]}
lines = {l["id"]: l for l in data["lines"]}
line_color = {"R": "#E11D48", "B": "#2563EB", "G": "#059669"}
line_name = {k: v["name"] for k, v in lines.items()}
access = {k: v["accessible"] for k, v in stations.items()}

# station -> [(neighbor, line)]
adj = {s: [] for s in stations}
for lid, l in lines.items():
    ss = l["stations"]
    for a, b in zip(ss, ss[1:]):
        adj[a].append((b, lid)); adj[b].append((a, lid))
lines_at = {s: sorted({lid for _, lid in adj[s]}) for s in stations}

def shortest(start, end, accessible=False):
    if accessible and (not access[start] or not access[end]):
        return None
    pq = []
    best = {}
    for lid in lines_at[start]:
        best[(start, lid)] = (0, 0, None, None)
        heapq.heappush(pq, (0, 0, start, lid))
    while pq:
        e, t, s0, lid = heapq.heappop(pq)
        if best.get((s0, lid), (99, 99))[:2] < (e, t):
            continue
        if s0 == end:
            states = []
            cur = (s0, lid)
            while cur is not None:
                _, _, prev, typ = best[cur]
                states.append((cur, typ))
                cur = prev
            states.reverse()
            edge_list = []
            transfers = []
            for i in range(1, len(states)):
                (ps, pl), (cs, cl) = states[i - 1][0], states[i][0]
                typ = states[i][1]
                if typ == "ride":
                    edge_list.append((ps, cs, cl))
                elif typ == "transfer":
                    transfers.append(cs)
            sts = [edge_list[0][0]] + [x[1] for x in edge_list]
            return {"stations": sts, "edge_list": edge_list, "edges": e,
                    "transfers": t, "transfers_at": transfers}
        for nx, nlid in adj[s0]:
            if nlid != lid:
                continue
            key = (nx, lid)
            cand = (e + 1, t)
            if key not in best or cand < best[key][:2]:
                best[key] = (e + 1, t, (s0, lid), "ride")
                heapq.heappush(pq, (e + 1, t, nx, lid))
        for l2 in lines_at[s0]:
            if l2 == lid: continue
            if accessible and not access[s0]:
                continue
            key = (s0, l2)
            cand = (e, t + 1)
            if key not in best or cand < best[key][:2]:
                best[key] = (e, t + 1, (s0, lid), "transfer")
                heapq.heappush(pq, (e, t + 1, s0, l2))
    return None

def segments(route):
    segs = []
    for a, b, lid in route["edge_list"]:
        if segs and segs[-1]["line"] == lid and segs[-1]["stations"][-1] == a:
            segs[-1]["stations"].append(b)
        else:
            segs.append({"line": lid, "stations": [a, b]})
    for x in segs:
        x["edges"] = len(x["stations"]) - 1
        x["route"] = " → ".join(x["stations"])
    return segs

routes = []
for q in data["queries"]:
    r = shortest(q["from"], q["to"], False)
    r["from"] = q["from"]; r["to"] = q["to"]
    r["segments"] = segments(r)
    r["accessible_ok"] = access[q["from"]] and access[q["to"]] and all(access[s] for s in r["transfers_at"])
    r["from_name"] = stations[q["from"]]["name"]; r["to_name"] = stations[q["to"]]["name"]
    if not r["accessible_ok"]:
        ar = shortest(q["from"], q["to"], True)
        ar["from"] = q["from"]; ar["to"] = q["to"]
        ar["segments"] = segments(ar)
        ar["from_name"] = r["from_name"]; ar["to_name"] = r["to_name"]
        ar["accessible_ok"] = True
    else:
        ar = None
    r["accessible_alt"] = ar
    routes.append(r)

# map geometry
POS = {
    "S01": (120, 560), "S02": (280, 560), "S03": (420, 560), "S04": (620, 560),
    "S05": (900, 560), "S06": (1040, 560), "S12": (1180, 700),
    "S07": (620, 220), "S08": (620, 420), "S09": (780, 700), "S10": (940, 700), "S11": (1080, 820),
    "S13": (300, 240), "S14": (440, 240), "S15": (760, 420), "S16": (1040, 700),
}
W, H = 1600, 1000

def seg(x1, y1, x2, y2, color, w=10):
    length = math.hypot(x2 - x1, y2 - y1)
    ang = math.atan2(y2 - y1, x2 - x1)
    c, s = math.cos(ang), math.sin(ang)
    mat = f"({c:.6f},{s:.6f},0,0,{-s:.6f},{c:.6f},0,0,0,0,1,0,0,0,0,1)"
    return f'<Positioned left="{x1:.1f}" top="{y1-w/2:.1f}"><Transform matrix="{mat}" origin="(0,0)"><Container width="{length:.1f}" height="{w}" color="{color}" borderRadius="{w//2}"/></Transform></Positioned>'

parts = ['<Snapshot background="#F7F8FC" type="png">', '<Container width="1600" height="1000"><Stack alignment="TOP_LEFT"><Container width="1600" height="1000" color="#F7F8FC"/>']
parts.append('<Positioned left="40" top="28"><Column crossAxisAlignment="START" mainAxisSize="MIN">' + T("CITY TRANSIT / SCHEMATIC", 14, "#2563EB", True, ' letterSpacing="2"') + T("三线换乘图", 40, "#0B1220", True) + T("非地理示意图 · 相邻站耗时相同 · 站间边为双向乘车", 20, "#56637A") + '</Column></Positioned>')
# legend
parts.append('<Positioned right="40" top="34"><Column crossAxisAlignment="END" mainAxisSize="MIN">')
parts.append('<Row crossAxisAlignment="CENTER">' + ''.join(f'<Container width="10" height="10" color="{line_color[lid]}" shape="CIRCLE"/><SizedBox width="4"/>' + T(f"{lid} {line_name[lid]}", 18, "#334155") + '<SizedBox width="12"/>' for lid in "RBG") + '</Row>')
parts.append('<SizedBox height="4"/>')
parts.append('<Row crossAxisAlignment="CENTER"><Container width="10" height="10" color="#FFFFFF" shape="CIRCLE" border="3 SOLID #0B1220"/><SizedBox width="4"/>' + T("换乘站", 17, "#475569") + '<SizedBox width="12"/><Container width="8" height="8" color="#059669" shape="CIRCLE"/><SizedBox width="4"/>' + T("无障碍可用", 17, "#475569") + '<SizedBox width="12"/><Container width="8" height="8" color="#94A3B8" shape="CIRCLE"/><SizedBox width="4"/>' + T("无设施（仅可乘车通过）", 17, "#475569") + '</Row>')
parts.append('</Column></Positioned>')
# lines
for lid, l in lines.items():
    ss = l["stations"]
    for a, b in zip(ss, ss[1:]):
        x1, y1 = POS[a]; x2, y2 = POS[b]
        parts.append(seg(x1, y1, x2, y2, line_color[lid], 10))
# line badges near first station
for lid, l in lines.items():
    x, y = POS[l["stations"][0]]
    parts.append(f'<Positioned left="{x-54}" top="{y-20}" width="40" height="40"><Container width="40" height="40" color="{line_color[lid]}" shape="CIRCLE" alignment="CENTER">' + T(lid, 20, "#FFFFFF", True) + '</Container></Positioned>')
# station markers
inter = [s for s in stations if len(lines_at[s]) > 1]
for sid, s in stations.items():
    x, y = POS[sid]
    if sid in inter:
        parts.append(f'<Positioned left="{x-17}" top="{y-17}" width="34" height="34"><Container width="34" height="34" color="#FFFFFF" shape="CIRCLE" border="5 SOLID #0B1220"/></Positioned>')
    else:
        parts.append(f'<Positioned left="{x-13}" top="{y-13}" width="26" height="26"><Container width="26" height="26" color="#FFFFFF" shape="CIRCLE" border="5 SOLID #0B1220"/></Positioned>')
# labels
label_pos = {
    "S01": (120, 596, "CENTER"), "S02": (280, 596, "CENTER"), "S03": (420, 596, "CENTER"),
    "S04": (620, 516, "CENTER"), "S05": (900, 596, "CENTER"), "S06": (1040, 516, "CENTER"),
    "S12": (1210, 700, "LEFT"), "S07": (620, 168, "CENTER"), "S08": (620, 368, "CENTER"),
    "S09": (780, 736, "CENTER"), "S10": (940, 736, "CENTER"), "S11": (1150, 820, "LEFT"),
    "S13": (300, 186, "CENTER"), "S14": (440, 186, "CENTER"), "S15": (760, 368, "CENTER"),
    "S16": (1060, 744, "LEFT"),
}
for sid, (lx, ly, al) in label_pos.items():
    x = lx - (60 if al == "CENTER" else 0)
    w = 150 if al == "LEFT" else 120
    align_value = "CENTER" if al == "CENTER" else "CENTER_LEFT"
    parts.append(f'<Positioned left="{x}" top="{ly}" width="{w}"><Container width="{w}" color="#F7F8FCEB" borderRadius="5" padding="(1,4)"><Container width="{w-8}" alignment="{align_value}"><Row crossAxisAlignment="CENTER">' + T(f"{sid} {stations[sid]['name']}", 20, "#0B1220", sid in inter) + '<SizedBox width="4"/>' + (f'<Container width="8" height="8" color="#059669" shape="CIRCLE"/>' if access[sid] else f'<Container width="8" height="8" color="#FFFFFF" shape="CIRCLE" border="2 SOLID #94A3B8"/>') + '</Row></Container></Container></Positioned>')
# query strip
parts.append('<Positioned left="40" top="888"><Row crossAxisAlignment="CENTER">')
for i, r in enumerate(routes):
    acc = "✓ 无障碍" if r["accessible_ok"] else "✗ 需替代路线"
    color = "#166534" if r["accessible_ok"] else "#B45309"
    parts.append(f'<Container padding="(8,14)" color="#FFFFFF" borderRadius="10" border="1 SOLID #E3E9F2" margin="(0,0,10,0)"><Row crossAxisAlignment="CENTER">' + T(f"查询 {i+1}", 14, "#8896AB", True) + '<SizedBox width="6"/>' + T(f"{r['from']} → {r['to']}", 19, "#0B1220", True) + '<SizedBox width="8"/>' + T(f"{r['edges']} 边 · {r['transfers']} 换乘", 18, "#475569") + '<SizedBox width="8"/>' + T(acc, 17, color, True) + '</Row></Container>')
parts.append('</Row></Positioned>')
parts.append('<Positioned left="40" top="950">' + T("线路只按站序绘制，转折为 45°/90°；交叉处没有站点圆环则不构成换乘。", 17, "#64748B") + '</Positioned>')
parts.append('</Stack></Container></Snapshot>')
map_dsl = "\n".join(parts)
(OUT / "network-map.snapshot").write_text(map_dsl, encoding="utf-8")

# ---------------- travel card ----------------
TW, TH = 720, 1280
t = ['<Snapshot background="#F3F5FA" type="png">', f'<Container width="{TW}" height="{TH}"><Stack alignment="TOP_LEFT"><Container width="{TW}" height="{TH}" color="#F3F5FA"/>']
t.append('<Positioned left="36" top="28"><Column crossAxisAlignment="START" mainAxisSize="MIN">' + T("TRANSIT CARD / VERIFIED ROUTES", 14, "#2563EB", True, ' letterSpacing="2"') + T("三条旅程，逐个核对", 32, "#0B1220", True) + T("最少站间边 → 换乘最少 → 无障碍约束", 18, "#56637A") + '</Column></Positioned>')

def route_chips(route, x, y, small=False):
    out = []
    sts = route["stations"]
    seg_color = {}
    for s in route["segments"]:
        for a, b in zip(s["stations"], s["stations"][1:]):
            seg_color[(a, b)] = s["line"]; seg_color[(b, a)] = s["line"]
    chip_w = 64 if small else 74
    gap = 14
    fs = 16 if small else 20
    out.append(f'<Positioned left="{x}" top="{y}"><Row crossAxisAlignment="CENTER">')
    for i, sid in enumerate(sts):
        out.append(f'<Container width="{chip_w}" height="{54 if small else 62}" color="#FFFFFF" borderRadius="8" border="1 SOLID #DDE4EF" alignment="CENTER"><Column crossAxisAlignment="CENTER" mainAxisSize="MIN">' + T(stations[sid]["name"], fs, "#0B1220", True) + T(sid, 11 if small else 13, "#8896AB") + '</Column></Container>')
        if i < len(sts) - 1:
            lc = line_color[seg_color.get((sid, sts[i + 1]), "B")]
            out.append(f'<Container width="{gap}" height="6" color="{lc}"/>')
    out.append('</Row></Positioned>')
    return "".join(out)

card_y = [150, 486, 932]
card_h = [320, 430, 320]
for i, r in enumerate(routes):
    y = card_y[i]; h = card_h[i]
    t.append(f'<Positioned left="28" top="{y}"><Container width="664" height="{h}" color="#FFFFFF" borderRadius="18" border="1 SOLID #E3E9F2" padding="20"><Stack alignment="TOP_LEFT"><Container width="624" height="{h-40}" color="#FFFFFF"/>')
    t.append('<Positioned left="0" top="0">' + T(f"0{i+1}  {r['from']} {r['from_name']} → {r['to']} {r['to_name']}", 21, "#0B1220", True) + '</Positioned>')
    acc_ok = r["accessible_ok"]
    badge = "✓ 无障碍可行" if acc_ok else "✗ 普通最短不可无障碍"
    bcol = "#166534" if acc_ok else "#B91C1C"
    bgacc = "#DCFCE7" if acc_ok else "#FEE2E2"
    t.append(f'<Positioned left="0" top="30"><Row crossAxisAlignment="CENTER"><Container padding="(3,9)" color="#E0E7FF" borderRadius="6">' + T(f"{r['edges']} 站间边", 18, "#3730A3", True) + '</Container><SizedBox width="8"/><Container padding="(3,9)" color="#FEF3C7" borderRadius="6">' + T(f"{r['transfers']} 次换乘", 18, "#92400E", True) + f'</Container><SizedBox width="8"/><Container padding="(3,9)" color="{bgacc}" borderRadius="6">' + T(badge, 18, bcol, True) + '</Container></Row></Positioned>')
    t.append(route_chips(r, 0, 70))
    seg_text = " · ".join([f"{s['line']} {line_name[s['line']]}：{s['route']}（{s['edges']} 边）" for s in r["segments"]])
    t.append(f'<Positioned left="0" top="138" width="624">' + T(seg_text, 20, "#475569") + '</Positioned>')
    if r["transfers_at"]:
        tt = "、".join(f"{x} {stations[x]['name']}" for x in r["transfers_at"])
        t.append(f'<Positioned left="0" top="216" width="624">' + T(f"换乘点：{tt}；首次上车不计换乘。", 20, "#64748B") + '</Positioned>')
    if acc_ok:
        t.append(f'<Positioned left="0" top="248" width="624">' + T("起点、终点与换乘站均具备无障碍设施。", 20, "#166534") + '</Positioned>')
    else:
        t.append(f'<Positioned left="0" top="248" width="624">' + T(f"普通最短需在 {r['transfers_at'][0]} {stations[r['transfers_at'][0]]['name']} 换乘，该站无设施；可乘车通过但不能换乘。", 20, "#B91C1C") + '</Positioned>')
        ar = r["accessible_alt"]
        t.append(f'<Positioned left="0" top="304" width="624"><Row crossAxisAlignment="CENTER">' + T("无障碍替代", 20, "#166534", True) + '<SizedBox width="10"/>' + T(f"{ar['edges']} 边 · {ar['transfers']} 换乘", 18, "#475569") + T("  起点/终点/换乘站均可用", 16, "#64748B") + '</Row></Positioned>')
        # small alternative sequence below (inside card, may extend if needed)
        t.append(route_chips(ar, 0, 332, small=True))
    t.append('</Stack></Container></Positioned>')
t.append('</Stack></Container></Snapshot>')
travel_dsl = "\n".join(t)
(OUT / "travel-card.snapshot").write_text(travel_dsl, encoding="utf-8")

# routes json
def export(r):
    if r is None: return None
    return {"from": r["from"], "to": r["to"], "from_name": r["from_name"], "to_name": r["to_name"],
            "stations": r["stations"], "station_names": [stations[s]["name"] for s in r["stations"]],
            "edges": r["edges"], "transfers": r["transfers"], "transfers_at": r["transfers_at"],
            "segments": [{"line": s["line"], "line_name": line_name[s["line"]], "stations": s["stations"],
                          "edges": s["edges"], "route": s["route"]} for s in r["segments"]],
            "accessible_ok": r["accessible_ok"]}
out = {
    "schema_version": 1, "task_id": "A07", "path_base": "output_dir",
    "map_note": "非地理示意图；线路按站序绘制，转折为45°/90°",
    "accessibility_rule": "accessible=false 可乘车通过，不可作为起点/终点/换乘站",
    "routes": [export(r) for r in routes],
    "accessible_alternatives": [export(r["accessible_alt"]) for r in routes if r["accessible_alt"]],
    "station_table": [{"id": s["id"], "name": s["name"], "accessible": s["accessible"],
                       "lines": lines_at[s["id"]]} for s in data["stations"]],
    "checks": {
        "all_queries": len(routes) == 3,
        "first_boarding_not_transfer": True,
        "edge_cost_unit": 1, "transfer_tiebreak": "min edges then min transfers",
    }
}
(OUT / "routes.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
for r in routes:
    print(r["from"], r["to"], r["edges"], r["transfers"], r["stations"], r["accessible_ok"], bool(r["accessible_alt"]))
print("wrote A07", len(map_dsl), len(travel_dsl))
