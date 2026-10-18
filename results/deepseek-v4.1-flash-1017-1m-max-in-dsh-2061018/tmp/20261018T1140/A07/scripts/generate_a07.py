"""A07 · 三线换乘图与路线核验 — 1600×1000 map + 720×1280 travel card."""
from __future__ import annotations

import heapq
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A07"
TMP = ROOT / "tmp" / RUN / TASK
VERSION = sys.argv[1] if len(sys.argv) > 1 else "v001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))

from dsl import C, Col, Gap, HGap, Label, Pos, Row, SizedBox, Stack, T, polygon, _ribbon_points  # noqa: E402

BG = "#070D19"
PANEL = "#0D1728"
NODE_BG = "#0B1220"
LINE = "#22314B"
TEXT = "#EAF2FB"
MUTED = "#93A6C2"
FAINT = "#5F7290"
R = "#F87171"
B = "#60A5FA"
G = "#34D399"
AMBER = "#F59E0B"
GREEN = "#34D399"
RED = "#F87171"

W, H = 1600, 1000
COLORS = {"R": R, "B": B, "G": G}
LINE_NAMES = {"R": "红线", "B": "蓝线", "G": "绿线"}

XY = {
    "S01": (120, 320), "S02": (260, 320), "S03": (400, 320), "S04": (520, 320),
    "S05": (860, 320), "S06": (1000, 320), "S12": (1140, 320),
    "S07": (120, 620), "S08": (400, 620), "S09": (620, 420), "S10": (720, 420), "S11": (820, 420),
    "S13": (120, 860), "S14": (300, 860), "S15": (620, 620), "S16": (1040, 200),
}
POLY = {
    "R": [(120, 320), (1140, 320)],
    "B": [(120, 620), (400, 620), (520, 500), (520, 320), (620, 420), (820, 420)],
    "G": [(120, 860), (300, 860), (400, 760), (400, 620), (620, 620), (740, 500), (860, 500),
          (860, 320), (980, 200), (1040, 200)],
}
LABEL_SIDE = {"S01": "above", "S02": "above", "S03": "above", "S04": "above", "S05": "above",
              "S06": "above", "S12": "above", "S07": "below", "S08": "below", "S09": "above",
              "S10": "below", "S11": "above", "S13": "below", "S14": "below", "S15": "below",
              "S16": "below"}
STATIONS = [
    ("S01", "松林", True, ["R"]), ("S02", "北门", True, ["R"]), ("S03", "书院", False, ["R"]),
    ("S04", "中心", True, ["R", "B"]), ("S05", "东桥", False, ["R", "G"]), ("S06", "江湾", True, ["R"]),
    ("S12", "机场", True, ["R"]), ("S07", "西港", True, ["B"]), ("S08", "工坊", True, ["B", "G"]),
    ("S09", "花园", False, ["B"]), ("S10", "南门", True, ["B"]), ("S11", "会展", True, ["B"]),
    ("S13", "石溪", True, ["G"]), ("S14", "公园", False, ["G"]), ("S15", "剧院", True, ["G"]),
    ("S16", "研究所", True, ["G"]),
]
IDX = {s[0]: s for s in STATIONS}
LINES = {"R": ["S01", "S02", "S03", "S04", "S05", "S06", "S12"],
         "B": ["S07", "S08", "S04", "S09", "S10", "S11"],
         "G": ["S13", "S14", "S08", "S15", "S05", "S16"]}
QUERIES = [("S01", "S11"), ("S13", "S12"), ("S07", "S16")]


def solve(a, b, accessible_mode=False):
    shared = {}
    for lid, ss in LINES.items():
        for s in ss:
            shared.setdefault(s, set()).add(lid)
    pq = [(0, 0, 0, a, "")]
    best = {}
    prev = {}
    visited = set()
    counter = 0
    while pq:
        e, t, _, s, ln = heapq.heappop(pq)
        key = (s, ln)
        if key in visited:
            continue
        visited.add(key)
        best[key] = (e, t)
        if s == b:
            path = []
            k = key
            while k in prev:
                path.append(k)
                k = prev[k]
            path.append(k)
            path.reverse()
            stations = []
            for st, _ in path:
                if not stations or stations[-1] != st:
                    stations.append(st)
            return {"intervals": e, "transfers": t, "stations": stations,
                    "states": [(st, l) for st, l in path]}
        if ln:
            ss = LINES[ln]
            i = ss.index(s)
            for j in (i - 1, i + 1):
                if 0 <= j < len(ss):
                    ns = ss[j]
                    nk = (ns, ln)
                    nv = (e + 1, t)
                    if nk not in visited and (nk not in best or nv < best[nk]):
                        best[nk] = nv
                        prev[nk] = key
                        counter += 1
                        heapq.heappush(pq, (nv[0], nv[1], counter, ns, ln))
        for l2 in shared.get(s, []):
            if l2 == ln:
                continue
            if accessible_mode and not IDX[s][2]:
                continue
            nv = (e, t + (0 if not ln else 1))
            nk = (s, l2)
            if nk not in visited and (nk not in best or nv < best[nk]):
                best[nk] = nv
                prev[nk] = key
                counter += 1
                heapq.heappush(pq, (nv[0], nv[1], counter, s, l2))
    return None


def segments_of(states):
    out = []
    for (s1, l1), (s2, l2) in zip(states, states[1:]):
        if s1 == s2:
            continue
        if not out or out[-1]["line"] != l1:
            out.append({"line": l1, "stations": [s1]})
        out[-1]["stations"].append(s2)
    return out


def route_info(a, b, mode):
    r = solve(a, b, accessible_mode=(mode == "accessible"))
    segs = segments_of(r["states"])
    transfer_stations = [segs[i]["stations"][-1] for i in range(len(segs) - 1)]
    return {
        "stations": r["stations"],
        "edge_lines": [l for seg in segs for _ in zip(seg["stations"], seg["stations"][1:]) for l in [seg["line"]]],
        "segments": segs,
        "intervals": r["intervals"],
        "transfers": r["transfers"],
        "transfer_stations": transfer_stations,
    }


def line_polygon(lid):
    pts = POLY[lid]
    return polygon(W, H, _ribbon_points(pts, 7), COLORS[lid])


def joint(lid, x, y):
    return Pos(x - 4, y - 4, C(width=8, height=8, color=COLORS[lid], borderRadius=4))


def marker(sid):
    x, y = XY[sid]
    _, name, acc, lines = IDX[sid]
    color = COLORS[lines[0]] if len(lines) == 1 else "#E2E8F0"
    if len(lines) > 1:
        return [Pos(x - 10, y - 10, C(width=20, height=20, color="#F8FAFC", borderRadius=10)),
                Pos(x - 7, y - 7, C(width=14, height=14, color="#0B1220", borderRadius=7)),
                Pos(x - 3, y - 3, C(width=6, height=6, color=AMBER, borderRadius=3))]
    return [Pos(x - 7, y - 7, C(width=14, height=14, color=NODE_BG, borderRadius=7,
                                border=f"3 SOLID {color}"))]


LABEL_DX = {"S05": -42}


def station_label(sid):
    x, y = XY[sid]
    _, name, acc, lines = IDX[sid]
    above = LABEL_SIDE[sid] == "above"
    label_y = y - 50 if above else y + 26
    badge = C(width=16, height=16, color=(GREEN + "22" if acc else RED + "22"), borderRadius=4,
              alignment="CENTER", child=T("A" if acc else "N", size=11, color=(GREEN if acc else RED), weight="BOLD", family="Inter"))
    parts = [T(sid, size=13, color=FAINT, family="Inter"), HGap(4), T(name, size=20, color=TEXT, weight="BOLD"), HGap(5), badge]
    if len(lines) > 1:
        parts += [HGap(4), T("⇄", size=14, color=AMBER, weight="BOLD")]
    return Pos(x - 62 + LABEL_DX.get(sid, 0), label_y, Row(parts, crossAxisAlignment="CENTER"))


def build_map():
    layers = [SizedBox(W, H)]
    # line ribbons
    for lid in ["R", "B", "G"]:
        layers.append(line_polygon(lid))
        for x, y in POLY[lid]:
            layers.append(joint(lid, x, y))
    # line letter chips at the left ends
    for lid, y in [("R", 320), ("B", 620), ("G", 860)]:
        layers.append(Pos(64, y - 12, C(width=30, height=24, color=COLORS[lid], borderRadius=6,
                                        alignment="CENTER", child=T(lid, size=16, color="#07101E", weight="BOLD", family="Inter"))))
    # markers and labels
    for sid, *_ in STATIONS:
        layers += marker(sid)
        layers.append(station_label(sid))

    header = Row([
        C(width=46, height=46, gradientType="LINEAR", gradientColors="#F87171,#60A5FA,#34D399",
          gradientBegin="TOP_LEFT", gradientEnd="BOTTOM_RIGHT", borderRadius=12,
          child=C(alignment="CENTER", child=T("M", size=20, color="#07101E", weight="BOLD", family="Inter"))),
        HGap(12),
        Col([
            T("三线换乘示意图", size=40, color=TEXT, weight="BOLD", family="Noto Serif CJK SC,Inter"),
            Gap(2),
            T("非地理示意图 · 16 站 · 3 条线路 · 相邻站耗时相同", size=20, color=MUTED),
        ], crossAxisAlignment="START"),
        '<Spacer />',
        Col([
            T("SCHEMATIC · NOT TO SCALE", size=15, color=R, weight="BOLD", family="Inter", spacing=1),
            Gap(3),
            T("折线转角 45° / 90°", size=17, color=MUTED),
        ], crossAxisAlignment="END"),
    ], crossAxisAlignment="CENTER")

    legend = Row([
        T("线路", size=15, color=FAINT),
        HGap(8),
        C(width=22, height=6, color=R), HGap(4), T("R 红线", size=18, color=MUTED),
        HGap(12), C(width=22, height=6, color=B), HGap(4), T("B 蓝线", size=18, color=MUTED),
        HGap(12), C(width=22, height=6, color=G), HGap(4), T("G 绿线", size=18, color=MUTED),
        HGap(20),
        T("A", size=12, color=GREEN, weight="BOLD"), T(" 无障碍可用", size=18, color=MUTED),
        HGap(12), T("N", size=12, color=RED, weight="BOLD"), T(" 无设施", size=18, color=MUTED),
        '<Spacer />',
        T("仅双圈站可换乘；线条交叉不换乘", size=17, color=FAINT),
    ], crossAxisAlignment="CENTER")

    side = C(width=328, height=700, color=PANEL, borderRadius=14, border=f"1 SOLID {LINE}",
             padding="(16,20)", child=Col([
                 T("换乘站 / INTERCHANGE", size=20, color=TEXT, weight="BOLD"),
                 Gap(8),
                 Row([C(width=16, height=16, color="#F8FAFC", borderRadius=8), HGap(8),
                      Col([T("S04 中心", size=20, color=TEXT, weight="BOLD"),
                           T("R ↔ B · 无障碍可用", size=15, color=MUTED)], crossAxisAlignment="START")]),
                 Gap(8),
                 Row([C(width=16, height=16, color="#F8FAFC", borderRadius=8), HGap(8),
                      Col([T("S08 工坊", size=20, color=TEXT, weight="BOLD"),
                           T("B ↔ G · 无障碍可用", size=15, color=MUTED)], crossAxisAlignment="START")]),
                 Gap(8),
                 Row([C(width=16, height=16, color="#F8FAFC", borderRadius=8), HGap(8),
                      Col([T("S05 东桥", size=20, color=TEXT, weight="BOLD"),
                           T("R ↔ G · N 无设施", size=15, color=RED)], crossAxisAlignment="START")]),
                 Gap(16),
                 C(width=280, height=1, color=LINE),
                 Gap(12),
                 T("无障碍规则", size=18, color=TEXT, weight="BOLD"),
                 Gap(4),
                 T("A 站可作起点/终点/换乘；N 站可乘车通过，但不可上下车或换乘。", size=15, color=MUTED, height="1.45"),
                 Gap(12),
                 T("读图规则", size=18, color=TEXT, weight="BOLD"),
                 Gap(4),
                 T("站距不代表实际距离；相邻站耗时相同；区间数 = 边数，不是站数。", size=15, color=MUTED, height="1.45"),
                 Gap(12),
                 C(width=280, height=1, color=LINE),
                 Gap(12),
                 T("16 站 / 3 线", size=20, color=TEXT, weight="BOLD"),
                 T("R 7 · B 6 · G 6 站", size=16, color=MUTED),
             ], crossAxisAlignment="START"))

    content = Stack([
        SizedBox(W, H),
        Pos(0, 0, C(width=W, height=5, gradientType="LINEAR",
                    gradientColors="#F8717100,#F87171E6,#60A5FAE6,#34D39900",
                    gradientBegin="CENTER_LEFT", gradientEnd="CENTER_RIGHT"), w=W, h=5),
        Pos(32, 26, header, w=W - 64, h=76),
        Pos(32, 112, legend, w=W - 64, h=28),
        *layers[1:],
        Pos(1240, 180, side, w=328, h=700),
        Pos(32, 958, Row([
            T("非地理示意图 · 所有相邻站耗时相同 · 仅用于拓扑关系", size=15, color=FAINT),
            '<Spacer />',
            T("NETWORK MAP · THREE LINES", size=14, color=FAINT, family="Inter", spacing=1),
        ], crossAxisAlignment="CENTER"), w=W - 64, h=20),
    ], width=W, height=H)
    return f'<Snapshot type="png" background="{BG}">\n{content}\n</Snapshot>\n'


def route_spans(stations, segs):
    """Nested Text spans: station names + coloured line letters."""
    parts = []
    if segs:
        parts.append(f'<Text color="{COLORS[segs[0]["line"]]}" fontStyle="BOLD">{segs[0]["line"]} </Text>')
    for i, seg in enumerate(segs):
        st = seg["stations"]
        for j, sid in enumerate(st):
            if i > 0 and j == 0:
                continue
            if parts:
                parts.append('<Text color="#93A6C2"> → </Text>')
            parts.append(f'<Text color="#EAF2FB">{sid} {IDX[sid][1]}</Text>')
        if i < len(segs) - 1:
            nxt = segs[i + 1]["line"]
            col = COLORS[nxt]
            parts.append('<Text color="#93A6C2">  </Text>')
            parts.append(f'<Text color="{col}" fontStyle="BOLD">⇄ {nxt} </Text>')
    return '<Text fontSize="20" color="#EAF2FB" height="1.45">' + "".join(parts) + "</Text>"


def passed_n(sid_list, transfer_stations):
    return [sid for sid in sid_list if not IDX[sid][2] and sid not in transfer_stations]


def card(y, h, q, normal, accessible, alt=None):
    a, b = q
    title = Row([
        C(width=40, height=28, color=COLORS[normal["segments"][0]["line"]] + "22", borderRadius=8,
          alignment="CENTER", child=T("Q", size=15, color=COLORS[normal["segments"][0]["line"]], weight="BOLD", family="Inter")),
        HGap(8),
        T(f"{a} {IDX[a][1]} → {b} {IDX[b][1]}", size=24, color=TEXT, weight="BOLD"),
        '<Spacer />',
        T(f'{normal["intervals"]} 区间 · {normal["transfers"]} 换乘', size=18, color=MUTED, family="Inter"),
    ], crossAxisAlignment="CENTER")
    ok = normal["transfers"] == accessible["transfers"] and normal["intervals"] == accessible["intervals"]
    meta = T(f'普通最短：{normal["intervals"]} 个区间 · {normal["transfers"]} 次换乘 · 换乘站 '
             + (("、".join(normal["transfer_stations"])) if normal["transfer_stations"] else "无"),
             size=20, color=MUTED)
    seg_txt = " · ".join(f'{seg["line"]}×{len(seg["stations"]) - 1}' for seg in normal["segments"])
    body = [title, Gap(4), meta, Gap(8), route_spans(normal["stations"], normal["segments"]), Gap(4),
            T(f'站数 {len(normal["stations"])} · 区间 {normal["intervals"]} · 分段 {seg_txt}', size=16, color=FAINT), Gap(6)]
    passed = passed_n(normal["stations"], normal["transfer_stations"])
    if ok:
        body += [Row([T("✓", size=20, color=GREEN, weight="BOLD"), HGap(5),
                      T("可作为无障碍旅程", size=20, color=GREEN, weight="BOLD")], crossAxisAlignment="CENTER")]
        if passed:
            body += [Gap(2), T("途经 N 站 " + "、".join(passed) + "（可乘车通过，不可上下车）", size=15, color=FAINT)]
    else:
        body += [Row([T("✗", size=20, color=RED, weight="BOLD"), HGap(5),
                      T(f'不可作为无障碍旅程：换乘站 {", ".join(normal["transfer_stations"])} 无设施', size=20, color=RED, weight="BOLD")], crossAxisAlignment="CENTER")]
        if alt:
            alt_passed = passed_n(alt["stations"], alt["transfer_stations"])
            body += [Gap(8), C(width=624, height=1, color=LINE), Gap(6),
                     T(f'无障碍替代：{alt["intervals"]} 个区间 · {alt["transfers"]} 次换乘', size=20, color=GREEN, weight="BOLD"),
                     Gap(4), route_spans(alt["stations"], alt["segments"]),
                     T("站数 " + str(len(alt["stations"])) + " · 区间 " + str(alt["intervals"]) + " · 分段 " + " · ".join(f'{seg["line"]}×{len(seg["stations"]) - 1}' for seg in alt["segments"]), size=16, color=FAINT)]
            if alt_passed:
                body += [Gap(2), T("途经 N 站 " + "、".join(alt_passed) + "（可乘车通过，不可上下车）", size=15, color=FAINT)]
    return Pos(28, y, C(width=664, height=h, color=PANEL, borderRadius=16, border=f"1 SOLID {LINE}",
                        padding="(16,20)", child=Col(body, crossAxisAlignment="START")), w=664, h=h)


def build_card(normal, accessible):
    header = Row([
        C(width=42, height=42, gradientType="LINEAR", gradientColors="#F87171,#60A5FA,#34D399",
          gradientBegin="TOP_LEFT", gradientEnd="BOTTOM_RIGHT", borderRadius=10,
          child=C(alignment="CENTER", child=T("3", size=22, color="#07101E", weight="BOLD", family="Inter"))),
        HGap(10),
        Col([
            T("三线旅行卡", size=34, color=TEXT, weight="BOLD", family="Noto Serif CJK SC,Inter"),
            Gap(2),
            T("3 条查询 · 普通最短路线 + 无障碍判定", size=20, color=MUTED),
        ], crossAxisAlignment="START"),
    ], crossAxisAlignment="CENTER")
    note = T("非地理示意 · 相邻站耗时相同 · 换乘 = 改变线路（第一次上车不算）", size=20, color=FAINT)
    q1, q2, q3 = QUERIES
    cards = [
        card(170, 250, q1, normal[q1], accessible[q1]),
        card(436, 366, q2, normal[q2], accessible[q2], alt=accessible[q2] if normal[q2]["transfers"] != accessible[q2]["transfers"] or normal[q2]["intervals"] != accessible[q2]["intervals"] else None),
        card(818, 250, q3, normal[q3], accessible[q3]),
    ]
    notes = C(width=664, height=132, color="#0F1C30", borderRadius=12, border=f"1 SOLID {LINE}",
              padding="(10,16)", child=Col([
                  T("读卡说明", size=18, color=TEXT, weight="BOLD"),
                  Gap(2),
                  T("• 普通路线按（区间数，换乘数）字典序最优；无障碍替代只在普通最短不满足时给出。", size=16, color=MUTED),
                  T("• N 站可乘车通过，不能作为无障碍旅程的起点、终点或换乘站。", size=16, color=MUTED),
                  T("• 区间数 = 边数，不是站数；所有区间等耗时，故最短区间数 = 最短时间。", size=16, color=MUTED),
              ], crossAxisAlignment="START"))
    content = Stack([
        SizedBox(720, 1280),
        Pos(0, 0, C(width=720, height=5, gradientType="LINEAR",
                    gradientColors="#F8717100,#F87171E6,#60A5FAE6,#34D39900",
                    gradientBegin="CENTER_LEFT", gradientEnd="CENTER_RIGHT"), w=720, h=5),
        Pos(28, 24, header, w=664, h=76),
        Pos(28, 110, note, w=664, h=24),
        *cards,
        Pos(28, 1084, notes, w=664, h=132),
        Pos(28, 1226, Row([
            T("NETWORK MAP · TRAVEL CARD", size=13, color=FAINT, family="Inter", spacing=1),
            '<Spacer />',
            T("2026 · SCHEMATIC", size=13, color=FAINT, family="Inter", spacing=1),
        ], crossAxisAlignment="CENTER"), w=664, h=18),
    ], width=720, height=1280)
    return f'<Snapshot type="png" background="{BG}">\n{content}\n</Snapshot>\n'


def routes_json(normal, accessible):
    acc = [{"id": sid, "name": name, "accessible": a, "lines": lines} for sid, name, a, lines in STATIONS]
    queries = []
    for i, (a, b) in enumerate(QUERIES, 1):
        n, ac = normal[(a, b)], accessible[(a, b)]
        same = n["intervals"] == ac["intervals"] and n["transfers"] == ac["transfers"]
        queries.append({
            "id": f"Q{i}", "from": a, "to": b,
            "normal": {**n, "accessible": same},
            "accessible": {**ac, "same_as_normal": same},
            "accessible_status": "available_same" if same else "available_alternative",
            "note": ("普通最短路线本身满足无障碍约束。" if same else
                     "普通最短路线的换乘站含 N 站，不能作为无障碍旅程；另给满足约束的替代路线。"),
        })
    return {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
        "source": "tasks/A07-transit-topology/inputs/network.json",
        "definitions": {
            "intervals": "相邻站之间的边数；与站数不同（站数 = 区间数 + 1）。",
            "transfers": "改变乘坐线路的次数；第一次上车不计。",
            "accessible": "起点、终点、换乘站均须 accessible=true；accessible=false 站可乘车通过。",
        },
        "accessibility": acc,
        "queries": queries,
        "optimality": [{
            "query": f"Q{i}", "modes": ["normal", "accessible"],
            "method": "状态为 (station, line) 的字典序 Dijkstra：乘车边权 (1,0)，换乘边权 (0,1)；先比区间数，再比换乘数；accessible 模式禁止在 accessible=false 站换乘。",
            "normal_cost": [normal[q]["intervals"], normal[q]["transfers"]],
            "accessible_cost": [accessible[q]["intervals"], accessible[q]["transfers"]],
            "tie_break": "字典序 (intervals, transfers) 最小；实现中同代价按首次发现顺序稳定。",
        } for i, q in enumerate(QUERIES, 1)],
        "map_geometry": {
            "canvas": [1600, 1000],
            "lines": {lid: [list(p) for p in POLY[lid]] for lid in POLY},
            "stations": {sid: {"x": xy[0], "y": xy[1]} for sid, xy in XY.items()},
            "label_side": LABEL_SIDE,
            "angles": "线路折点仅使用 0°/45°/90°/135° 方向，转角为 45° 或 90°。",
        },
        "content_map": [
            {"query": "Q1", "map": "network-map.png", "map_box": [120, 280, 1200, 700],
             "card": "travel-card.png", "card_box": [28, 170, 692, 420],
             "check": "S01→S11 普通与无障碍均为 6 区间/1 换乘（S04）。"},
            {"query": "Q2", "map": "network-map.png", "map_box": [120, 200, 1200, 900],
             "card": "travel-card.png", "card_box": [28, 436, 692, 766],
             "check": "S13→S12 普通 6/1（S05，N）；无障碍替代 6/2（S08、S04）。"},
            {"query": "Q3", "map": "network-map.png", "map_box": [120, 200, 1200, 700],
             "card": "travel-card.png", "card_box": [28, 782, 692, 1032],
             "check": "S07→S16 普通与无障碍均为 4 区间/1 换乘（S08）。"},
        ],
    }


def main() -> int:
    normal = {q: route_info(q[0], q[1], "normal") for q in QUERIES}
    accessible = {q: route_info(q[0], q[1], "accessible") for q in QUERIES}
    d = TMP / "dsl"
    (d / "map").mkdir(parents=True, exist_ok=True)
    (d / "card").mkdir(parents=True, exist_ok=True)
    (d / "map" / f"{VERSION}.snapshot").write_text(build_map(), encoding="utf-8")
    (d / "card" / f"{VERSION}.snapshot").write_text(build_card(normal, accessible), encoding="utf-8")
    (TMP / "routes.json").write_text(json.dumps(routes_json(normal, accessible), ensure_ascii=False, indent=2), encoding="utf-8")
    for q in QUERIES:
        print(q, "normal", normal[q]["intervals"], normal[q]["transfers"], normal[q]["stations"])
        print(q, "accessible", accessible[q]["intervals"], accessible[q]["transfers"], accessible[q]["stations"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
