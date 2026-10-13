"""A07 - fictional metro: 1600x1000 schematic map + 720x1280 travel card.

Reads tasks/A07-transit-topology/inputs/network.json. Routes are computed with a
BFS over (station, line) states minimising (edges, transfers); a second search adds
the accessibility constraint. Nothing about the routes is hand-written.

Run from the suite task root:
  python tmp/<run_id>/A07/gen.py --ver v001
"""
from __future__ import annotations

import argparse
import heapq
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
sys.path.insert(0, str(ROOT / "tmp" / "2026-10-12T10-04Z-r001" / "_suite" / "scripts"))

from snap import (  # noqa: E402
    C, Border, Col, Container, Positioned, Row, Snapshot, Stack, Text, label, num,
    segment,
)

RUN = "2026-10-12T10-04Z-r001"
TASK = "A07"
IN_JSON = ROOT / "tasks" / "A07-transit-topology" / "inputs" / "network.json"
OUT_DIR = ROOT / "outputs" / RUN / TASK
TMP_DIR = ROOT / "tmp" / RUN / TASK

FONT = "Noto Sans CJK SC,Inter"
MONO = "Noto Sans Mono CJK SC,DejaVu Sans Mono"
net = json.loads(IN_JSON.read_text(encoding="utf-8"))
ST = {s["id"]: s for s in net["stations"]}
LINES = {l["id"]: l for l in net["lines"]}
QUERIES = [(q["from"], q["to"]) for q in net["queries"]]
NAME = {sid: ST[sid]["name"] for sid in ST}
ACC = {sid: ST[sid]["accessible"] for sid in ST}

LINE_COLOR = {"R": "#E24C4C", "B": "#38BDF8", "G": "#34D399"}
LINE_NAME = {lid: LINES[lid]["name"] for lid in LINES}

# adjacency: station -> list of (neighbour, line)
ADJ = defaultdict(set)
for lid, ln in LINES.items():
    for a, b in zip(ln["stations"], ln["stations"][1:]):
        ADJ[a].add((b, lid))
        ADJ[b].add((a, lid))
    ADJ  # each adjacent pair is bidirectional
LINES_AT = defaultdict(set)
for lid, ln in LINES.items():
    for s in ln["stations"]:
        LINES_AT[s].add(lid)

INTERCHANGE = {s for s in ST if len(LINES_AT[s]) > 1}


def search(src, dst, accessible_only=False):
    """Dijkstra on (station, line) with cost (edges, transfers). Returns the route."""
    start_states = [(src, lid) for lid in sorted(LINES_AT[src])]
    if accessible_only and not ACC[src]:
        return None
    best = {}
    pq = []
    for stt in start_states:
        best[stt] = (0, 0)
        heapq.heappush(pq, (0, 0, [stt]))
    while pq:
        e, t, path = heapq.heappop(pq)
        s, lid = path[-1]
        if (e, t) > best.get((s, lid), (9, 9)):
            continue
        if s == dst:
            return decode(path)
        for (n, nl) in sorted(ADJ[s]):
            nt = t + (1 if nl != lid else 0)
            if accessible_only and nl != lid and not ACC[s]:
                continue          # transfers only at accessible stations
            if accessible_only and n == dst and not ACC[dst]:
                continue
            ne = e + 1
            key = (n, nl)
            if best.get(key, (9, 9)) > (ne, nt):
                best[key] = (ne, nt)
                heapq.heappush(pq, (ne, nt, path + [(n, nl)]))
    return None


def decode(states):
    stations = [s for s, _ in states]
    segs = []
    for i, (s, l) in enumerate(states):
        if segs and segs[-1]["line"] == l:
            segs[-1]["stations"].append(s)
        elif segs:
            # a line change happens at the previous station, so that station belongs
            # to both segments and the per-segment edge counts sum to the route total
            segs.append({"line": l, "stations": [states[i - 1][0], s]})
        else:
            segs.append({"line": l, "stations": [s]})
    for g in segs:
        g["from"] = g["stations"][0]
        g["to"] = g["stations"][-1]
    return {
        "stations": stations,
        "station_count": len(stations),
        "edges": len(states) - 1,
        "transfers": sum(1 for i in range(1, len(states))
                         if states[i][1] != states[i - 1][1]),
        # a line change happens where you get off, i.e. the station of the previous state
        "transfer_stations": [states[i - 1][0] for i in range(1, len(states))
                              if states[i][1] != states[i - 1][1]],
        "segments": [{"line": g["line"], "line_name": LINE_NAME[g["line"]],
                      "from": g["from"], "to": g["to"],
                      "stations": g["stations"],
                      "edges": len(g["stations"]) - 1} for g in segs],
    }


ROUTES = {}
for src, dst in QUERIES:
    normal = search(src, dst)
    acc = search(src, dst, accessible_only=True)
    ok = normal is not None and all(ACC[s] for s in normal["transfer_stations"]) \
        and ACC[src] and ACC[dst]
    ROUTES[(src, dst)] = {"normal": normal, "normal_is_accessible": bool(ok),
                          "accessible": acc}

# ---------------------------------------------------------------- map layout
U = 180
POS = {
    "S01": (150, 530), "S02": (330, 530), "S03": (510, 530), "S04": (690, 530),
    "S05": (870, 530), "S06": (1050, 530), "S12": (1230, 530),
    "S07": (330, 170), "S08": (510, 350), "S09": (870, 710), "S10": (870, 890),
    "S11": (1050, 890),
    "S13": (150, 170), "S14": (330, 350), "S15": (690, 350), "S16": (1050, 710),
}
# (dx, dy, anchor): every offset keeps the label off the polylines and off its
# neighbours; the accessibility mark is appended to the same line.
LBL = {
    "S01": (-18, 0, "right"), "S02": (0, -26, "above"), "S03": (0, -26, "above"),
    "S04": (0, -26, "above"), "S05": (0, -26, "above"), "S06": (0, -26, "above"),
    "S12": (0, -26, "above"), "S07": (0, -26, "above"), "S08": (0, 30, "below"),
    "S09": (-18, 0, "right"), "S10": (-18, 0, "right"), "S11": (18, 0, "left"),
    "S13": (0, -26, "above"), "S14": (0, -26, "above"), "S15": (0, -26, "above"),
    "S16": (0, 30, "below"),
}

W, H = 1600, 1000
TXT, TXT_2, TXT_3 = "#F2F6FC", "#9FB2D0", "#6A7E9E"
BG, BG2 = "#070C1A", "#0D1730"
CARD, EDGE = "#101B36", "#243657"
AMBER, ROSE = "#FBBF24", "#FB7185"


def layer(*children, w=W, h=H):
    return Stack(C(width=num(w), height=num(h)), *children,
                 alignment="TOP_LEFT", clipBehavior="HARD_EDGE")


def card(x, y, w, h, *, fill=CARD, radius=14, border=EDGE):
    return Positioned(C(width=num(w), height=num(h), color=fill, borderRadius=num(radius),
                        border=f"1 SOLID {border}"), left=num(x), top=num(y))


mapels = []
mapels.append(Positioned(
    Row(C(width="6", height="54", color=LINE_COLOR["B"], borderRadius="3"),
        Container(width="16"),
        Col(Text("云构市地铁 · 线路示意图", color=TXT, fontSize="34", fontStyle="BOLD",
                 fontFamily=FONT),
            Container(height="6"),
            Text("非地理示意图：只表达乘车拓扑与换乘关系，不代表真实距离、方向或比例",
                 color=AMBER, fontSize="20", fontFamily=FONT),
            crossAxisAlignment="START"),
        crossAxisAlignment="CENTER"),
    left=num(28), top=num(22)))

# line polylines (45 / 90 degree bends only)
for lid in ("R", "B", "G"):
    pts = [POS[s] for s in LINES[lid]["stations"]]
    for a, b in zip(pts, pts[1:]):
        mapels.append(segment(a[0], a[1], b[0], b[1], 13, LINE_COLOR[lid]))

# stations
for sid, (x, y) in POS.items():
    inter = sid in INTERCHANGE
    lines_here = sorted(LINES_AT[sid])
    if inter:
        mapels.append(Positioned(C(width="30", height="30", color="#FFFFFF",
                                   borderRadius="15", border="4 SOLID #0B1220"),
                                 left=num(x - 15), top=num(y - 15)))
        mapels.append(Positioned(C(width="12", height="12", color="#0B1220",
                                   shape="CIRCLE"), left=num(x - 6), top=num(y - 6)))
    else:
        col = LINE_COLOR[lines_here[0]]
        mapels.append(Positioned(C(width="22", height="22", color=col, borderRadius="11",
                                   border="3 SOLID #FFFFFF"),
                                 left=num(x - 11), top=num(y - 11)))

    dx, dy, anchor = LBL[sid]
    lx, ly = x + dx, y + dy
    txt = f"{sid} {NAME[sid]}" + ("" if ACC[sid] else "  ×")
    if anchor in ("above", "below"):
        mapels.append(label(lx, ly, txt, 20, TXT,
                            anchor="center_bottom" if anchor == "above" else "center_top",
                            align="CENTER", width=170, font=FONT, bold=True))
    elif anchor == "left":
        mapels.append(label(lx, ly, txt, 20, TXT, anchor="left", align="LEFT",
                            width=170, font=FONT, bold=True))
    else:
        mapels.append(label(lx, ly, txt, 20, TXT, anchor="right", align="RIGHT",
                            width=170, font=FONT, bold=True))

# legend card on the right
LEG_X, LEG_Y, LEG_W, LEG_H = 1300, 150, 272, 520
mapels.append(card(LEG_X, LEG_Y, LEG_W, LEG_H, fill="#0E1830", radius=12))
ly = LEG_Y + 18
mapels.append(label(LEG_X + 18, ly, "图例", 22, TXT, anchor="left_top", align="LEFT",
                    width=120, font=FONT, bold=True))
ly += 36
for lid in ("R", "B", "G"):
    mapels.append(Positioned(C(width="26", height="13", color=LINE_COLOR[lid],
                               borderRadius="6"), left=num(LEG_X + 18), top=num(ly + 3)))
    mapels.append(label(LEG_X + 54, ly, f"{LINE_NAME[lid]}（{lid}）", 20, TXT,
                        anchor="left_top", align="LEFT", width=200, font=FONT))
    ly += 34
ly += 12
mapels.append(Positioned(C(width="26", height="26", color="#FFFFFF", borderRadius="13",
                           border="4 SOLID #0B1220"), left=num(LEG_X + 18), top=num(ly)))
mapels.append(label(LEG_X + 54, ly + 2, "换乘站（两线共享）", 20, TXT, anchor="left_top",
                    align="LEFT", width=210, font=FONT))
ly += 38
mapels.append(Positioned(C(width="20", height="20", color=LINE_COLOR["R"], borderRadius="10",
                           border="3 SOLID #FFFFFF"), left=num(LEG_X + 21), top=num(ly)))
mapels.append(label(LEG_X + 54, ly, "普通站（单线）", 20, TXT, anchor="left_top",
                    align="LEFT", width=210, font=FONT))
ly += 34
mapels.append(label(LEG_X + 18, ly, "× 不具备无障碍设施", 20, AMBER, anchor="left_top",
                    align="LEFT", width=250, font=FONT, bold=True))
ly += 34
mapels.append(Positioned(
    Container(
        Container(Text("不具备无障碍设施的站可以乘车通过，但不能作为无障碍旅程的"
                       "起点、终点或换乘站。",
                       color="#F0DFAE", fontSize="18", fontFamily=FONT, textAlign="LEFT",
                       softWrap="true", height="1.3"),
                  width=num(LEG_W - 64)),
        padding="(8,10)", color="#2A2410", borderRadius="10"),
    left=num(LEG_X + 18), top=num(ly)))
ly += 128
mapels.append(Positioned(
    Container(Text("两条线若在某点相交而没有白色换乘圆环，只是跨越，不是换乘；"
                   "本图布局已让线路只在共享站相遇。",
                   color=TXT_2, fontSize="18", fontFamily=FONT, textAlign="LEFT",
                   softWrap="true", height="1.3"),
              width=num(LEG_W - 40)),
    left=num(LEG_X + 18), top=num(ly)))

# route summary strip along the bottom-left
mapels.append(card(28, 926, W - 56, 58, fill="#0E1830", radius=10))
qs = []
for (src, dst), r in ROUTES.items():
    n = r["normal"]
    qs.append(f"{NAME[src]}→{NAME[dst]} {n['edges']}区间·{n['transfers']}换乘"
              f"{'·可无障碍' if r['normal_is_accessible'] else '·需绕行'}")
mapels.append(label(44, 944, "　·　".join(qs), 20, TXT_2, anchor="left_top", align="LEFT",
                    width=1150, font=FONT))
mapels.append(label(W - 44, 946, f"run {RUN}", 18, "#42536E", anchor="right_top",
                    align="RIGHT", width=340, font=FONT))
mapels.append(label(W - 44, 946, f"run {RUN}", 18, "#42536E", anchor="right_top",
                    align="RIGHT", width=220, font=FONT))

map_doc = Snapshot(
    Container(layer(*mapels), width=num(W), height=num(H),
              gradientType="LINEAR", gradientColors=f"{BG},{BG2}", gradientStops="0,1",
              gradientBegin="TOP_CENTER", gradientEnd="BOTTOM_CENTER"),
    background=BG, type="png")

# ---------------------------------------------------------------- travel card
MW, MH = 720, 1280
CTXT, CTXT2, CTXT3 = "#F2F6FC", "#A6B8D4", "#6E82A2"
CCARD, CEDGE = "#111C38", "#26385C"


def mlayer(*children):
    return Stack(C(width=num(MW), height=num(MH)), *children,
                 alignment="TOP_LEFT", clipBehavior="HARD_EDGE")


def mcard(x, y, w, h, *, fill=CCARD, border=CEDGE):
    return Positioned(C(width=num(w), height=num(h), color=fill, borderRadius="14",
                        border=f"1 SOLID {border}"), left=num(x), top=num(y))


mel = []
mel.append(Positioned(
    Col(Text("云构市地铁 · 出行卡", color=CTXT, fontSize="30", fontStyle="BOLD",
             fontFamily=FONT),
        Container(height="6"),
        Text("非地理示意图配套卡片 · 共 16 站 3 条线路", color=CTXT2, fontSize="20",
             fontFamily=FONT),
        Container(height="4"),
        Text("区间数 = 相邻站之间的边数；换乘 = 改变乘坐线路（首次上车不计）",
             color=CTXT3, fontSize="20", fontFamily=FONT),
        crossAxisAlignment="START"),
    left=num(24), top=num(20)))

JH = 322
y = 176
for qi, (src, dst) in enumerate(QUERIES):
    r = ROUTES[(src, dst)]
    n = r["normal"]
    a = r["accessible"]
    mel.append(mcard(24, y, MW - 48, JH))
    mel.append(Positioned(C(width=num(MW - 50), height="4",
                            color=LINE_COLOR[n["segments"][0]["line"]], borderRadius="2"),
                          left=num(25), top=num(y + 1)))
    mel.append(label(40, y + 14, f"{qi+1}  {NAME[src]} {src} → {NAME[dst]} {dst}",
                     22, CTXT, anchor="left_top", align="LEFT", width=620, font=FONT,
                     bold=True))
    # station chain
    chain = " → ".join(f"{s}" for s in n["stations"])
    mel.append(label(40, y + 46, chain, 20, CTXT2, anchor="left_top", align="LEFT",
                     width=MW - 90, font=MONO))
    names = " → ".join(f"{NAME[s]}" for s in n["stations"])
    mel.append(label(40, y + 70, names, 20, CTXT, anchor="left_top", align="LEFT",
                     width=MW - 90, font=FONT))
    # line segments
    sy = y + 100
    for seg in n["segments"]:
        mel.append(Positioned(C(width="16", height="16",
                                color=LINE_COLOR[seg["line"]], borderRadius="8"),
                              left=num(40), top=num(sy + 4)))
        mel.append(label(64, sy,
                         f"{LINE_NAME[seg['line']]} {seg['from']}→{seg['to']}"
                         f"（{seg['edges']} 区间）", 20, CTXT2, anchor="left_top",
                         align="LEFT", width=560, font=FONT))
        sy += 30
    tr = "、".join(f"{s} {NAME[s]}" for s in n["transfer_stations"]) or "无"
    mel.append(label(40, sy, f"合计：{n['edges']} 个区间 · {n['station_count']} 站 · "
                             f"换乘 {n['transfers']} 次（在 {tr}）",
                     20, CTXT, anchor="left_top", align="LEFT", width=MW - 90, font=FONT,
                     bold=True))
    sy += 32
    verdict = "可作为无障碍旅程" if r["normal_is_accessible"] else "最短路线不满足无障碍约束"
    vcol = "#34D399" if r["normal_is_accessible"] else AMBER
    body = (f"无障碍：{verdict}。" + (
        "" if r["normal_is_accessible"] else
        f" 改用 {a['edges']} 区间 / {a['transfers']} 次换乘的无障碍路线："
        + " → ".join(a["stations"]) + "。") +
        " 途中经过的非无障碍站仅作通过，不作起终点或换乘。")
    mel.append(Positioned(
        Container(
            Container(Text(body, color="#EAF2FF", fontSize="20", fontFamily=FONT,
                           textAlign="LEFT", softWrap="true", height="1.28"),
                      width=num(MW - 100)),
            padding="(8,12)", color="#16263F", borderRadius="10"),
        left=num(36), top=num(sy)))
    y += JH + 12

mel.append(label(24, MH - 56,
                 "× 的站（书院/东桥/花园/公园）不具备无障碍设施，只可乘车通过。",
                 20, AMBER, anchor="left_top", align="LEFT", width=MW - 48, font=FONT))

mob_doc = Snapshot(
    Container(mlayer(*mel), width=num(MW), height=num(MH), color="#0A1122"),
    background="#0A1122", type="png")

# ---------------------------------------------------------------- routes.json
routes = {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "source_input": "tasks/A07-transit-topology/inputs/network.json",
    "definitions": {
        "edge": "同一条线路上相邻两站之间的可双向乘车区间；所有相邻站耗时相同",
        "interval_count": "区间数 = 站点序列长度 - 1，不把站数误作区间数",
        "transfer": "在途中改变乘坐线路；第一次上车不计入换乘",
        "interchange_station": "同时属于两条线路的共享站",
        "accessibility": "accessible=false 的站可以乘车通过，但不能作为无障碍旅程的"
                         "起点、终点或换乘站；线路不因该属性删除",
        "route_objective": "先最小化区间数（边数），并列时最小化换乘次数",
    },
    "stations": {sid: {"name": NAME[sid], "accessible": ACC[sid],
                       "lines": sorted(LINES_AT[sid]),
                       "interchange": sid in INTERCHANGE,
                       "map_position_px": list(POS[sid]),
                       "label_offset": list(LBL[sid][:2]) + [LBL[sid][2]]}
                 for sid in sorted(ST)},
    "lines": {lid: {"name": LINE_NAME[lid], "color": LINE_COLOR[lid],
                    "stations": LINES[lid]["stations"],
                    "edges": len(LINES[lid]["stations"]) - 1} for lid in LINES},
    "interchange_stations": sorted(INTERCHANGE),
    "non_accessible_stations": sorted(s for s in ST if not ACC[s]),
    "queries": [],
    "map_note": "示意图中线路折线的每一段都是水平、垂直或 45 度；角度约束只针对图上绘制，"
                "不代表地理方位。图内已标注“非地理示意图”。",
    "bare_crossings": "布局经过设计使任意两条线路只在共享站上相遇，图中不存在可能被误读为"
                      "换乘的裸交叉；图例仍写明“无白色换乘圆环的相交只是跨越”。",
}
for src, dst in QUERIES:
    r = ROUTES[(src, dst)]
    n, a = r["normal"], r["accessible"]

    def pack(x):
        return {"station_sequence": x["stations"],
                "station_names": [NAME[s] for s in x["stations"]],
                "station_count": x["station_count"], "edges": x["edges"],
                "transfers": x["transfers"], "transfer_stations": x["transfer_stations"],
                "segments": x["segments"]}
    routes["queries"].append({
        "from": src, "to": dst,
        "from_name": NAME[src], "to_name": NAME[dst],
        "shortest_normal": pack(n),
        "shortest_normal_is_valid_accessible_journey": r["normal_is_accessible"],
        "reason": (None if r["normal_is_accessible"] else
                   f"最短路线在 {'、'.join(n['transfer_stations'])} 换乘，"
                   f"该站 accessible=false，不能作为无障碍旅程的换乘站"),
        "shortest_accessible": (pack(a) if a else None),
        "accessible_extra_transfers": (a["transfers"] - n["transfers"])
        if (a and not r["normal_is_accessible"]) else 0,
        "passed_through_non_accessible": [s for s in n["stations"] if not ACC[s]],
    })

OUT_DIR.mkdir(parents=True, exist_ok=True)
(OUT_DIR / "routes.json").write_text(
    json.dumps(routes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

ap = argparse.ArgumentParser()
ap.add_argument("--ver", default="v001")
a = ap.parse_args()
TMP_DIR.mkdir(parents=True, exist_ok=True)
(TMP_DIR / f"{a.ver}-map.snapshot").write_text(map_doc.render() + "\n", encoding="utf-8")
(TMP_DIR / f"{a.ver}-card.snapshot").write_text(mob_doc.render() + "\n", encoding="utf-8")
print(json.dumps({f"{s}-{d}": {"edges": v["normal"]["edges"], "transfers": v["normal"]["transfers"],
                      "acc_ok": v["normal_is_accessible"],
                      "acc_edges": v["accessible"]["edges"] if v["accessible"] else None,
                      "acc_transfers": v["accessible"]["transfers"] if v["accessible"] else None,
                      "seq": v["normal"]["stations"]}
                  for (s, d), v in ROUTES.items()}, ensure_ascii=False))
