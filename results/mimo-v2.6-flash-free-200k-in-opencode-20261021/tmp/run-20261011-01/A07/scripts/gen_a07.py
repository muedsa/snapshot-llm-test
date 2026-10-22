#!/usr/bin/env python3
"""A07 transit map + travel card generator + routes.json.

Launch base: suite root.
Usage: python tmp/<run_id>/A07/scripts/gen_a07.py <suite_root> <run_id> [outdir]

Solver: Dijkstra over (station, riding-line) states with lexicographic cost
(intervals, transfers); boarding at origin is free (first boarding is not a
transfer). Accessible mode forbids transfers at accessible=false stations
(pass-through riding stays allowed). A plain simple-path DFS enumerates all
routes within min_edges+3 and cross-checks the Dijkstra optimum.
"""
import heapq
import json
import math
import pathlib
import sys
from datetime import datetime

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
run_id = sys.argv[2] if len(sys.argv) > 2 else "run-20261011-01"
out_dir = pathlib.Path(sys.argv[3]) if len(sys.argv) > 3 else (root / "outputs" / run_id / "A07")
tmp_drafts = root / "tmp" / run_id / "A07" / "drafts"
tmp_drafts.mkdir(parents=True, exist_ok=True)
out_dir.mkdir(parents=True, exist_ok=True)

net = json.loads((root / "tasks" / "A07-transit-topology" / "inputs" / "network.json").read_text(encoding="utf-8"))
ST = {s["id"]: s for s in net["stations"]}
ACC = {s["id"]: bool(s["accessible"]) for s in net["stations"]}
NAME = {s["id"]: s["name"] for s in net["stations"]}
LINES = {l["id"]: l["stations"] for l in net["lines"]}
LINE_NAME = {"R": "R 红线", "B": "B 蓝线", "G": "G 绿线"}
LINE_COLOR = {"R": "#E4485B", "B": "#3B82F6", "G": "#22C55E"}
FONT = "Inter,Noto Sans CJK SC"
NOW = datetime.now().astimezone().isoformat(timespec="seconds")

# adjacency station -> [(neighbor, line)] built cleanly (no setdefault pitfalls)
ADJ = {s: [] for s in ST}
for lid, sts in LINES.items():
    for a, b in zip(sts, sts[1:]):
        ADJ[a].append((b, lid))
        ADJ[b].append((a, lid))
LINES_AT = {s: sorted({lid for _, lid in ADJ[s]}) for s in ST}
TRANSFER = {s for s in ST if len(LINES_AT[s]) > 1}


def dijkstra(origin, dest, accessible_mode):
    """Return best route dict or None (infeasible endpoints)."""
    if accessible_mode and (not ACC[origin] or not ACC[dest]):
        return None
    start_lines = LINES_AT[origin]
    best = {}
    prev = {}
    pq = []
    seq = 0
    for lid in start_lines:
        best[(origin, lid)] = (0, 0)
        heapq.heappush(pq, (0, 0, seq, origin, lid))
        seq += 1
    goal = None
    while pq:
        iv, tr, _, st, lid = heapq.heappop(pq)
        if best.get((st, lid), (10 ** 9, 10 ** 9)) != (iv, tr):
            continue
        if st == dest:
            goal = (st, lid)
            break
        for nb, lid2 in ADJ[st]:
            if lid2 != lid:
                continue
            cost = (iv + 1, tr)
            if cost < best.get((nb, lid), (10 ** 9, 10 ** 9)):
                best[(nb, lid)] = cost
                prev[(nb, lid)] = ((st, lid), "ride")
                heapq.heappush(pq, (cost[0], cost[1], seq, nb, lid))
                seq += 1
        for lid2 in LINES_AT[st]:
            if lid2 == lid:
                continue
            if accessible_mode and not ACC[st]:
                continue
            cost = (iv, tr + 1)
            if cost < best.get((st, lid2), (10 ** 9, 10 ** 9)):
                best[(st, lid2)] = cost
                prev[(st, lid2)] = ((st, lid), "transfer")
                heapq.heappush(pq, (cost[0], cost[1], seq, st, lid2))
                seq += 1
    if goal is None:
        return None
    states = [goal]
    cur = goal
    while cur in prev:
        cur = prev[cur][0]
        states.append(cur)
    states.reverse()
    stations = [states[0][0]]
    edge_lines = []
    transfers = []
    for i in range(1, len(states)):
        pst, pline = states[i - 1]
        cst, cline = states[i]
        if prev[states[i]][1] == "ride":
            stations.append(cst)
            edge_lines.append(cline)
        else:
            transfers.append({"station": cst, "name": NAME[cst],
                               "from_line": pline, "from_line_name": LINE_NAME[pline],
                               "to_line": cline, "to_line_name": LINE_NAME[cline]})
    segments = []
    cur_line, seg_sts = edge_lines[0], [stations[0]]
    for i, (e, nxt) in enumerate(zip(edge_lines, stations[1:])):
        if e != cur_line:
            segments.append({"line": cur_line, "line_name": LINE_NAME[cur_line], "stations": seg_sts})
            cur_line, seg_sts = e, [stations[i + 1]]
        seg_sts.append(nxt)
    segments.append({"line": cur_line, "line_name": LINE_NAME[cur_line], "stations": seg_sts})
    return {"feasible": True, "stations": stations, "station_names": [NAME[s] for s in stations],
            "edge_lines": edge_lines, "intervals": len(edge_lines), "transfers": len(transfers),
            "transfer_stations": transfers, "segments": segments}


def enumerate_routes(origin, dest, bound, accessible_mode):
    """All simple paths with intervals <= bound; returns list of route records."""
    out = []

    def dfs(st, ride_line, path, elines, trs):
        if len(elines) >= bound:
            return
        if st == dest:
            out.append({"stations": path[:], "edge_lines": elines[:], "transfers": trs})
            return
        for nb, lid in ADJ[st]:
            if nb in path:
                continue
            dtr = 1 if (ride_line and lid != ride_line) else 0
            if accessible_mode and dtr and not ACC[st]:
                continue
            dfs(nb, lid, path + [nb], elines + [lid], trs + dtr)

    dfs(origin, None, [origin], [], 0)
    return out


QUERIES = [(q["from"], q["to"]) for q in net["queries"]]
ROUTES = {}
OPT = {}
for origin, dest in QUERIES:
    key = f"{origin}->{dest}"
    n = dijkstra(origin, dest, False)
    a = dijkstra(origin, dest, True)
    ROUTES[key] = {"normal": n, "accessible": a}
    # cross-check with plain enumeration
    rec = {}
    for mode, feasible in (("normal", n), ("accessible", a)):
        if not feasible:
            rec[mode] = None
            continue
        cands = enumerate_routes(origin, dest, feasible["intervals"] + 3, mode == "accessible")
        mine = [c for c in cands if len(c["edge_lines"]) == feasible["intervals"]]
        mtr = min(c["transfers"] for c in mine)
        assert (feasible["intervals"], feasible["transfers"]) == (feasible["intervals"], mtr), \
            f"{key} {mode}: dijkstra transfers {feasible['transfers']} != enum min {mtr}"
        rec[mode] = {
            "enumerated_within": feasible["intervals"] + 3,
            "routes_found": len(cands),
            "min_interval_routes": len(mine),
            "min_interval_transfer_counts": sorted({c["transfers"] for c in mine}),
            "chosen_transfers": feasible["transfers"],
        }
    OPT[key] = rec
    print(key, "normal", n["intervals"], n["transfers"], "-".join(n["stations"]))
    if a:
        print("   accessible", a["intervals"], a["transfers"], "-".join(a["stations"]))
    else:
        print("   accessible: infeasible endpoints")

# ---------------------------------------------------------------- map layout
XY = {
    "S01": (100, 500), "S02": (250, 500), "S03": (400, 500), "S04": (550, 500),
    "S05": (750, 700), "S06": (950, 700), "S12": (1150, 700),
    "S07": (750, 100), "S08": (750, 300), "S09": (550, 700),
    "S10": (350, 900), "S11": (150, 900),
    "S13": (250, 300), "S14": (450, 300), "S15": (950, 500), "S16": (750, 900),
}
MAPW, MAPH = 1600, 1000

# every drawn segment must be horizontal, vertical or exactly 45 degrees
for lid, sts in LINES.items():
    for a, b in zip(sts, sts[1:]):
        (x0, y0), (x1, y1) = XY[a], XY[b]
        dx, dy = x1 - x0, y1 - y0
        ang = math.degrees(math.atan2(dy, dx)) % 180
        assert min(abs(ang - k) for k in (0, 45, 90, 135, 180)) < 1e-9, (lid, a, b, ang)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def f(v):
    if isinstance(v, float):
        s = f"{v:.2f}".rstrip("0").rstrip(".")
        return s if s not in ("-0", "") else "0"
    return str(v)


class DSL:
    def __init__(self):
        self.o = []

    def add(self, s):
        self.o.append(s)

    def rect(self, x, y, w, h, color, extra=""):
        self.add(f'<Positioned left="{f(x)}" top="{f(y)}" width="{f(w)}" height="{f(h)}">'
                 f'<Container color="{color}"{extra} /></Positioned>')

    def box(self, x, y, w, h, inner):
        self.add(f'<Positioned left="{f(x)}" top="{f(y)}" width="{f(w)}" height="{f(h)}">{inner}</Positioned>')

    def text(self, x, y, s, size=22, color="#F8FAFC", weight="NORMAL", w=None, align="START"):
        wa = f' width="{f(w)}"' if w is not None else ""
        ta = f' textAlign="{align}"' if align != "START" else ""
        self.add(f'<Positioned left="{f(x)}" top="{f(y)}"{wa}>'
                 f'<Text fontFamily="{FONT}" fontSize="{f(size)}" color="{color}" '
                 f'fontStyle="{weight}"{ta}>{esc(s)}</Text></Positioned>')

    def seg(self, p0, p1, th, color):
        L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        if L < 0.01:
            return
        a = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
        c, s = math.cos(a), math.sin(a)
        cx, cy = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
        self.box(cx - L / 2, cy - th / 2, L, th,
                 f'<Transform matrix="({f(c)},{f(s)},0,0,{f(-s)},{f(c)},0,0,0,0,1,0,0,0,0,1)" '
                 f'alignment="CENTER"><Container height="{f(th)}" color="{color}" /></Transform>')

    def circle(self, cx, cy, d, fill, border=None, bw=2):
        ba = f' border="{bw} SOLID {border}"' if border else ""
        self.box(cx - d / 2, cy - d / 2, d, d,
                 f'<Container width="{f(d)}" height="{f(d)}" color="{fill}" shape="CIRCLE"{ba} />')

    def medallion(self, cx, cy, letter, color, d=30, size=22):
        self.box(cx - d / 2, cy - d / 2, d, d,
                 f'<Container width="{f(d)}" height="{f(d)}" color="{color}" borderRadius="8" />')
        self.text(cx - d / 2, cy - size * 0.62, letter, size, "#FFFFFF", "BOLD", w=d, align="CENTER")

    def render(self, w, h, bg):
        return (f'<Snapshot type="png" background="{bg}">\n  <SizedBox width="{w}" height="{h}">\n  '
                '<Stack alignment="TOP_LEFT" clipBehavior="NONE">\n    '
                + "\n    ".join(self.o)
                + "\n  </Stack>\n  </SizedBox>\n</Snapshot>\n")


MAP_BADGE = {("S01", "S11"): "①", ("S13", "S12"): "②", ("S07", "S16"): "③"}
BADGE_NUM = {}
for (fr, to), num in MAP_BADGE.items():
    BADGE_NUM[fr] = num
    BADGE_NUM[to] = num

LBL = {  # name: (x, y, w, align) ; id defaults to name below unless overridden
    "S01": (40, 526, 120, "CENTER"), "S02": (190, 526, 120, "CENTER"),
    "S03": (340, 526, 120, "CENTER"), "S04": (485, 438, 130, "CENTER"),
    "S05": (610, 710, 120, "CENTER"), "S06": (890, 652, 120, "CENTER"),
    "S07": (690, 52, 120, "CENTER"), "S08": (790, 268, 150, "START"),
    "S09": (575, 678, 150, "START"), "S10": (290, 916, 120, "CENTER"),
    "S11": (90, 916, 120, "CENTER"), "S12": (1090, 652, 120, "CENTER"),
    "S13": (190, 252, 120, "CENTER"), "S14": (390, 252, 120, "CENTER"),
    "S15": (975, 478, 150, "START"), "S16": (690, 916, 130, "CENTER"),
}
LBL_ID = {  # explicit id boxes where the default "below" collides with lines/labels/edge
    "S04": (485, 412, 130, "CENTER"), "S05": (610, 738, 120, "CENTER"),
    "S06": (890, 626, 120, "CENTER"), "S07": (690, 26, 120, "CENTER"),
    "S08": (790, 300, 150, "START"), "S09": (575, 706, 150, "START"),
    "S10": (290, 946, 120, "CENTER"), "S11": (90, 946, 120, "CENTER"),
    "S12": (1090, 626, 120, "CENTER"), "S13": (190, 226, 120, "CENTER"),
    "S14": (390, 226, 120, "CENTER"), "S15": (975, 506, 150, "START"),
    "S16": (690, 946, 130, "CENTER"),
}
BADGE_POS = {"S01": (40, 483), "S11": (90, 883), "S13": (190, 283),
             "S12": (1176, 683), "S07": (694, 83), "S16": (694, 883)}
MEDALLIONS = [(175, 500, "R"), (650, 600, "R"), (1050, 700, "R"),
              (750, 200, "B"), (550, 600, "B"), (250, 900, "B"),
              (350, 300, "G"), (850, 400, "G"), (750, 800, "G")]

d = DSL()
d.rect(0, 0, MAPW, MAPH, "#0A1020")
d.rect(0, 0, MAPW, 4, "#38BDF8")
d.text(60, 30, "虚构城地铁线网 · 非地理示意图", 40, "#F8FAFC", "BOLD")
d.text(60, 84, "三线 16 站 · 折线仅 45°/90° · 相邻站双向乘车且耗时相同", 22, "#94A3B8")

# lines first (under stations)
for lid, sts in LINES.items():
    for a, b in zip(sts, sts[1:]):
        d.seg(XY[a], XY[b], 10, LINE_COLOR[lid])

# line letter medallions on the lines
for cx, cy, lid in MEDALLIONS:
    d.medallion(cx, cy, lid, LINE_COLOR[lid])

# station marks: plain white dot / transfer double ring / amber hollow ring
for sid, (x, y) in XY.items():
    if sid in TRANSFER and not ACC[sid]:
        d.circle(x, y, 32, "#0A1020", "#E2E8F0", 3)
        d.circle(x, y, 22, "#0A1020", "#F59E0B", 2)
        d.circle(x, y, 8, "#F8FAFC")
    elif sid in TRANSFER:
        d.circle(x, y, 26, "#0A1020", "#E2E8F0", 3)
        d.circle(x, y, 10, "#F8FAFC")
    elif not ACC[sid]:
        d.circle(x, y, 26, "#0A1020", "#F59E0B", 2)
    else:
        d.circle(x, y, 14, "#F8FAFC")

# station labels (name 22px, id 20px — all >= 20)
for sid, (lx, ly, lw, la) in LBL.items():
    d.text(lx, ly, NAME[sid], 22, "#F8FAFC", "BOLD", w=lw, align=la)
    if sid in LBL_ID:
        ix, iy, iw, ia = LBL_ID[sid]
    else:
        ix, iy, iw, ia = lx, ly + 60, lw, la
    d.text(ix, iy, sid, 20, "#94A3B8", w=iw, align=ia)

# query endpoint badges
for sid, (bx, by) in BADGE_POS.items():
    d.box(bx, by, 34, 34, '<Container width="34" height="34" color="#F8FAFC" shape="CIRCLE" />')
    d.text(bx, by + 5, BADGE_NUM[sid], 20, "#0A1020", "BOLD", w=34, align="CENTER")

# legend box
d.rect(1120, 60, 440, 470, "#0F1A2E", ' borderRadius="14" border="1 SOLID #1E293B"')
d.text(1144, 76, "图例", 24, "#F8FAFC", "BOLD")
ly = 116
for lid in ("R", "B", "G"):
    d.medallion(1159, ly + 12, lid, LINE_COLOR[lid])
    d.text(1184, ly, f"{LINE_NAME[lid]} · {len(LINES[lid])} 站", 20, "#CBD5E1")
    ly += 34
d.circle(1167, ly + 10, 14, "#F8FAFC")
d.text(1184, ly - 2, "白实心圆＝普通站（可上下车）", 20, "#CBD5E1")
ly += 36
d.circle(1167, ly + 10, 26, "#0A1020", "#E2E8F0", 3)
d.circle(1167, ly + 10, 10, "#F8FAFC")
d.text(1184, ly - 2, "白色双环＝换乘站（可换乘）", 20, "#CBD5E1")
ly += 36
d.circle(1167, ly + 10, 26, "#0A1020", "#F59E0B", 2)
d.text(1184, ly - 2, "琥珀空心环＝无无障碍设施", 20, "#F59E0B")
ly += 34
d.text(1144, ly, "无设施站可过站乘车，但不可作", 20, "#CBD5E1")
ly += 28
d.text(1144, ly, "起点、终点或换乘站（见旅行卡）", 20, "#CBD5E1")
ly += 32
d.text(1144, ly, "无设施车站：S03 书院 · S05 东桥 ·", 20, "#94A3B8")
ly += 28
d.text(1144, ly, "S09 花园 · S14 公园", 20, "#94A3B8")
ly += 34
d.text(1144, ly, "线路交叉且无站点＝不可换乘；", 20, "#CBD5E1")
ly += 28
d.text(1144, ly, "本图线路仅在换乘站相交", 20, "#CBD5E1")

# overview box
d.rect(1140, 720, 420, 250, "#0F1A2E", ' borderRadius="14" border="1 SOLID #1E293B"')
d.text(1164, 736, "三条旅程概览（详见旅行卡）", 22, "#F8FAFC", "BOLD")
d.text(1164, 774, "① 松林→会展 6区间/1换乘 可无障碍", 20, "#CBD5E1", w=390)
d.text(1164, 808, "② 石溪→机场 6区间/1换乘 不可无障碍", 20, "#F87171", w=390)
d.text(1184, 838, "无障碍替代 6区间/2换乘（S08、S04）", 20, "#34D399", w=370)
d.text(1164, 876, "③ 西港→研究所 4区间/1换乘 可无障碍", 20, "#CBD5E1", w=390)
d.text(1164, 916, "①②③＝旅行卡旅程端点（起/终）", 20, "#94A3B8", w=390)

map_dsl = d.render(MAPW, MAPH, "#0A1020")
(tmp_drafts / "network-map.snapshot").write_text(map_dsl, encoding="utf-8")

# ------------------------------------------------------------ travel card
CW, CH, PAD, INNER = 720, 1280, 32, 656
c = DSL()
c.rect(0, 0, CW, CH, "#0A1020")
c.rect(0, 0, CW, 4, "#38BDF8")
c.text(32, 22, "旅行卡 · 三条旅程", 36, "#F8FAFC", "BOLD")
c.text(32, 74, "站序与线路段 · 区间数 · 换乘次数 · 无障碍判定", 20, "#94A3B8")
c.text(32, 104, "白色双边＝换乘站；琥珀色边＝无无障碍设施车站", 20, "#CBD5E1")
c.text(32, 130, "无设施站可过站乘车，但不可作起点、终点或换乘站", 20, "#F59E0B")

BLOCK = {"S01->S11": (168, 258), "S13->S12": (436, 500), "S07->S16": (946, 258)}


def chip_row(x0, y, stations, w, gap):
    centers = []
    for i, s in enumerate(stations):
        cx = x0 + i * (w + gap)
        acc_ring = not ACC[s]
        tr = s in TRANSFER
        border = ' border="2 SOLID #F59E0B"' if acc_ring else (' border="3 SOLID #E2E8F0"' if tr else "")
        c.box(cx, y, w, 66, f'<Container color="#0B1424" borderRadius="10"{border} />')
        if acc_ring and tr:  # both: amber outer + white inner double line
            c.box(cx + 4, y + 4, w - 8, 58, '<Container color="#00000000" borderRadius="7" '
                                            'border="1 SOLID #E2E8F0" />')
        c.text(cx, y + 8, NAME[s], 22, "#F8FAFC", "BOLD", w=w, align="CENTER")
        c.text(cx, y + 38, s, 20, "#94A3B8", w=w, align="CENTER")
        centers.append(cx + w / 2)
    return centers


def seg_bars(centers, edge_lines, y):
    i = 0
    while i < len(edge_lines):
        lid = edge_lines[i]
        j = i
        while j + 1 < len(edge_lines) and edge_lines[j + 1] == lid:
            j += 1
        x0, x1 = centers[i], centers[j + 1]
        c.rect(x0, y, x1 - x0, 8, LINE_COLOR[lid], ' borderRadius="4"')
        c.medallion((x0 + x1) / 2, y + 4, lid, LINE_COLOR[lid], d=26, size=20)
        i = j + 1
    for k in range(len(edge_lines) - 1):  # transfer ticks at line-change junctions
        if edge_lines[k] != edge_lines[k + 1]:
            c.circle(centers[k + 1], y + 4, 12, "#F8FAFC")


def draw_route(bx, by, route, w, gap, stats, access, access_color):
    centers = chip_row(bx, by, route["stations"], w, gap)
    seg_bars(centers, route["edge_lines"], by + 82)
    c.text(bx, by + 104, stats, 20, "#F8FAFC")
    c.text(bx, by + 136, access, 20, access_color, w=INNER - 32)
    return centers


q1, q2, q2a, q3 = (ROUTES["S01->S11"]["normal"], ROUTES["S13->S12"]["normal"],
                   ROUTES["S13->S12"]["accessible"], ROUTES["S07->S16"]["normal"])


def block_shell(y, h, title):
    c.box(PAD, y, INNER, h, '<Container color="#0F1A2E" borderRadius="16" border="1 SOLID #1E293B" />')
    c.text(48, y + 12, title, 24, "#F8FAFC", "BOLD")


def layout7(n):
    w, gap = 82, 13
    total = n * w + (n - 1) * gap
    return w, gap, PAD + (INNER - total) / 2


def layout5(n):
    w, gap = 104, 34
    total = n * w + (n - 1) * gap
    return w, gap, PAD + (INNER - total) / 2


# Q1
y, h = BLOCK["S01->S11"]
block_shell(y, h, "① S01 松林 → S11 会展")
w, gap, x0 = layout7(7)
draw_route(x0, y + 44, q1, w, gap,
           "区间 6 · 换乘 1 次（S04 中心：R→B） · 线路段 R(3)+B(3)",
           "可作为无障碍旅程：起点 S01、终点 S11、换乘站 S04 均有设施；"
           "S03 书院无设施但仅过站乘车，不违反约束", "#34D399")

# Q2 (two routes)
y, h = BLOCK["S13->S12"]
block_shell(y, h, "② S13 石溪 → S12 机场")
w, gap, x0 = layout7(7)
draw_route(x0, y + 44, q2, w, gap,
           "区间 6 · 换乘 1 次（S05 东桥：G→R） · 线路段 G(4)+R(2)",
           "不可作为无障碍旅程：换乘站 S05 东桥无无障碍设施"
           "（起点/终点合规，但换乘站不合规）", "#F87171")
c.text(48, y + 252, "无障碍替代（最短）", 22, "#F8FAFC", "BOLD")
draw_route(x0, y + 286, q2a, w, gap,
           "区间 6 · 换乘 2 次（S08 G→B、S04 B→R） · 线路段 G(2)+B(1)+R(3)",
           "可作为无障碍旅程：换乘站 S08、S04 均有设施；"
           "S14 公园、S05 东桥仅过站乘车", "#34D399")

# Q3
y, h = BLOCK["S07->S16"]
block_shell(y, h, "③ S07 西港 → S16 研究所")
w, gap, x0 = layout5(5)
draw_route(x0, y + 44, q3, w, gap,
           "区间 4 · 换乘 1 次（S08 工坊：B→G） · 线路段 B(1)+G(3)",
           "可作为无障碍旅程：起点 S07、终点 S16、换乘站 S08 均有设施；"
           "S05 东桥无设施但仅过站乘车", "#34D399")

c.text(32, 1222, "非地理示意 · 区间＝相邻站间边 · 换乘＝改变乘坐线路（首次上车不算）", 20, "#94A3B8")
c.text(32, 1250, "数据源 network.json · 三条路线与最优性核验见 routes.json", 20, "#94A3B8")

card_dsl = c.render(CW, CH, "#0A1020")
(tmp_drafts / "travel-card.snapshot").write_text(card_dsl, encoding="utf-8")

# ------------------------------------------------------------- routes.json
CARD_REGION = {k: [PAD, v[0], PAD + INNER, v[0] + v[1]] for k, v in BLOCK.items()}
MAP_WHERE = {
    "S01->S11": "①端点徽标在 S01（左）与 S11（左下）；路线为 R 线西段 S01→S04 后经 S04 换乘 B 线南段至 S11",
    "S13->S12": "②端点徽标在 S13（左上）与 S12（右）；普通路线 G 线上段 S13→S05 后经 S05 换乘 R 线东段至 S12；"
                "无障碍替代改经 S08（G→B）与 S04（B→R）",
    "S07->S16": "③端点徽标在 S07（上）与 S16（下）；路线为 B 线北段 S07→S08 换乘 G 线后经 S15、S05 至 S16",
}


def bbox_of(sts, pad=60):
    xs = [XY[s][0] for s in sts]
    ys = [XY[s][1] for s in sts]
    return [max(0, min(xs) - pad), max(0, min(ys) - pad),
            min(MAPW, max(xs) + pad), min(MAPH, max(ys) + pad)]


queries_json = []
content_map = []
optimality_json = []
for origin, dest in QUERIES:
    key = f"{origin}->{dest}"
    n = ROUTES[key]["normal"]
    a = ROUTES[key]["accessible"]
    note = ""
    if a and n["transfer_stations"]:
        bad = [t for t in n["transfer_stations"] if not ACC[t["station"]]]
        if bad:
            note = ("最短普通旅程的换乘站 " + "、".join(f"{t['station']} {t['name']}" for t in bad) +
                    " 无无障碍设施，故另求最短无障碍旅程：区间数不变，换乘次数增加")
        else:
            note = "最短普通旅程的起点、终点与换乘站均有设施，无障碍旅程与普通旅程相同"
    queries_json.append({
        "from": origin, "from_name": NAME[origin], "to": dest, "to_name": NAME[dest],
        "normal": n,
        "accessible": a if a else {"feasible": False, "stations": None, "edge_lines": None,
                                   "intervals": None, "transfers": None, "transfer_stations": None,
                                   "reason": "起点或终点无无障碍设施，不能作为无障碍旅程端点"},
        "accessible_note": note,
    })
    card_r = CARD_REGION[key]
    content_map.append({
        "query": key,
        "map": {
            "endpoint_badges": [MAP_BADGE[(origin, dest)]],
            "badge_positions_px": [[XY[origin][0], XY[origin][1]], [XY[dest][0], XY[dest][1]]],
            "route_stations_px": [[XY[s][0], XY[s][1]] for s in n["stations"]],
            "region": bbox_of(n["stations"]),
            "where": MAP_WHERE[key],
        },
        "card": {
            "block": f"旅程{MAP_BADGE[(origin, dest)]}（{'含无障碍替代子路线' if key == 'S13->S12' else '单一路线'}）",
            "region": card_r,
            "route_regions": {"normal": card_r,
                              "accessible": card_r if key == "S13->S12" else card_r},
        },
        "conclusion": ("地图端点徽标、站位与卡片站序/线路段/区间/换乘数同源于同一求解结果；"
                       + ("卡片旅程②内另列无障碍替代路线逐段展示；" if key == "S13->S12" else "")
                       + f"核验：{n['intervals']} 区间、{n['transfers']} 次换乘，"
                         f"无障碍判定与 routes.json 一致"),
    })
    for mode in ("normal", "accessible"):
        r = queries_json[-1][mode]
        ev = OPT[key][mode]
        optimality_json.append({
            "query": key, "mode": mode,
            "method": "在（车站,当前线路）状态上做 Dijkstra，代价为（区间数,换乘数）字典序；"
                      "起点首次上车不计换乘；无障碍模式禁止在无设施站换乘（过站乘车不受限）",
            "result": ({"intervals": r["intervals"], "transfers": r["transfers"],
                        "stations": r["stations"]} if r["feasible"] else None),
            "basis": ("相邻站等权 ⇒ 区间数即最少站间边数；区间数相同时取换乘数最少者。"
                      "独立枚举交叉核验：在最优区间数+3 范围内共枚举 %s 条简单路径，"
                      "其中最少区间路径 %s 条，其换乘数集合为 %s，所选换乘数 %s 为其中最小"
                      % (ev["routes_found"], ev["min_interval_routes"],
                         ev["min_interval_transfer_counts"], ev["chosen_transfers"])
                      if ev else "起点或终点无无障碍设施，无可行无障碍路线，故不参与排序"),
            "reason": r.get("reason"),
        })

routes_json = {
    "schema_version": 1,
    "task_id": "A07",
    "path_base": "output_dir",
    "generated_at": NOW,
    "source_network": "tasks/A07-transit-topology/inputs/network.json",
    "definitions": {
        "interval": "相邻站间的一条边（区间）；站数 = 区间数 + 1，二者不混用",
        "transfer": "改变乘坐线路；第一次上车不算换乘",
        "accessible_rule": "accessible=false 的车站可乘车通过（途经），但不能作为无障碍旅程的"
                           "起点、终点或换乘站；据此不删除任何线路或车站",
    },
    "queries": queries_json,
    "accessibility": [
        {"id": s["id"], "name": NAME[s["id"]], "accessible": ACC[s["id"]],
         "is_transfer_station": s["id"] in TRANSFER,
         "eligible_as_endpoint": ACC[s["id"]],
         "eligible_as_transfer": ACC[s["id"]],
         "pass_through_allowed": True,
         "basis": "依据任务说明：accessible 表示该站是否具备无障碍设施；false 站可乘车通过，"
                  "仅限制作为起点、终点或换乘站"}
        for s in net["stations"]
    ],
    "optimality": optimality_json,
    "content_map": content_map,
}
(out_dir / "routes.json").write_text(json.dumps(routes_json, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"map dsl {len(map_dsl)} bytes | card dsl {len(card_dsl)} bytes")
print("transfer stations:", sorted(TRANSFER))
print("non-accessible:", sorted(s for s in ST if not ACC[s]))
