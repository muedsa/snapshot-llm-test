#!/usr/bin/env python3
"""A07 transit topology: computes BFS/Dijkstra routes (normal + accessible) and emits
network-map.snapshot (1600x1000), travel-card.snapshot (720x1280) and routes.json.

All local paths are derived from suite.ROOT / environment variables; nothing machine
specific is persisted. Start from the suite root (SNAPSHOT_TASK_ROOT).
"""
import json, os, sys, heapq
from pathlib import Path

TOOLS = os.environ["TOOLS"]
sys.path.insert(0, TOOLS)
from dsl import Canvas, CN, LATIN, MONO
import suite

TASK = "A07"
ROOT = suite.ROOT
NET = json.loads((ROOT / "tasks" / "A07-transit-topology" / "inputs" / "network.json").read_text(encoding="utf-8"))

stations = {s["id"]: s for s in NET["stations"]}
order_ids = [s["id"] for s in NET["stations"]]
lines = {l["id"]: l for l in NET["lines"]}
line_order = [l["id"] for l in NET["lines"]]
line_name = {l["id"]: l["name"] for l in NET["lines"]}

# ---------------------------------------------------------------- graph
edges = {}
serving = {}
for lid, l in lines.items():
    seq = l["stations"]
    for a, b in zip(seq, seq[1:]):
        edges.setdefault(a, []).append((b, lid))
        edges.setdefault(b, []).append((a, lid))
    for s in seq:
        serving.setdefault(s, []).append(lid)
shared = {s: ls for s, ls in serving.items() if len(ls) > 1}

INF = (10 ** 9, 10 ** 9)


def solve(frm, to, accessible):
    """Minimise (intervals, transfers) over (station, current_line) states.
    accessible=True: endpoints must be accessible; transfers only at accessible
    shared stations; accessible=false stations may still be ridden through."""
    if accessible and not (stations[frm]["accessible"] and stations[to]["accessible"]):
        return None
    best = {}
    pq = []
    for lid in serving.get(frm, []):                    # boarding: not a transfer
        st = (frm, lid)
        best[st] = (0, 0, None, None)
        heapq.heappush(pq, (0, 0, st))
    while pq:
        e, t, st = heapq.heappop(pq)
        if best.get(st, (INF[0], INF[1], None, None))[:2] != (e, t):
            continue
        s, lid = st
        for nb, el in edges.get(s, []):                 # ride one interval
            if el != lid:
                continue
            ns = (nb, lid)
            nc = (e + 1, t)
            if nc < best.get(ns, (INF[0], INF[1], None, None))[:2]:
                best[ns] = (nc[0], nc[1], st, el)
                heapq.heappush(pq, (nc[0], nc[1], ns))
        if s in shared:                                 # change line
            for nl in shared[s]:
                if nl == lid:
                    continue
                if accessible and not stations[s]["accessible"]:
                    continue
                ns = (s, nl)
                nc = (e, t + 1)
                if nc < best.get(ns, (INF[0], INF[1], None, None))[:2]:
                    best[ns] = (nc[0], nc[1], st, None)
                    heapq.heappush(pq, (nc[0], nc[1], ns))
    goal = None
    for lid in serving.get(to, []):
        st = (to, lid)
        if st in best and (goal is None or best[st][:2] < goal[0]):
            goal = (best[st][:2], st)
    if goal is None:
        return None
    chain, st = [], goal[1]
    while st is not None:
        chain.append(st)
        st = best[st][2]
    chain.reverse()
    seq = [chain[0][0]]
    edge_lines, transfer_stations = [], []
    for i in range(1, len(chain)):
        prev, cur = chain[i - 1], chain[i]
        if prev[0] == cur[0]:
            transfer_stations.append(prev[0])
        else:
            seq.append(cur[0])
            edge_lines.append(cur[1])
    return {
        "stations": seq, "edge_lines": edge_lines,
        "intervals": goal[0][0], "transfers": goal[0][1],
        "transfer_stations": transfer_stations,
    }


def assess(normal, frm, to):
    """A normal shortest route is a valid accessible journey iff endpoints and
    every transfer station are accessible=true."""
    ok = stations[frm]["accessible"] and stations[to]["accessible"]
    bad = [s for s in normal["transfer_stations"] if not stations[s]["accessible"]]
    return ok and not bad, bad


queries = []
for q in NET["queries"]:
    frm, to = q["from"], q["to"]
    n = solve(frm, to, False)
    valid, bad = assess(n, frm, to)
    a = None
    if valid:
        a = dict(n)
        a["same_as_normal"] = True
        a["note"] = "端点与换乘站均具备无障碍设施，该最短普通路线可直接作为无障碍旅程。"
    else:
        alt = solve(frm, to, True)
        a = dict(alt) if alt else None
        if a:
            a["same_as_normal"] = False
            a["note"] = ("最短普通路线在 %s 换乘（accessible=false），不可作无障碍换乘；"
                         "另求满足约束的最短无障碍路线。" % ",".join(bad))
        else:
            a = None
    queries.append({"from": frm, "to": to, "normal": n,
                    "accessible": a, "normal_accessible_valid": valid,
                    "normal_invalid_transfer_stations": bad})

# sanity checks against the hand-verified topology
assert queries[0]["normal"]["stations"] == ["S01", "S02", "S03", "S04", "S09", "S10", "S11"]
assert queries[0]["normal"]["intervals"] == 6 and queries[0]["normal"]["transfers"] == 1
assert queries[1]["normal"]["stations"] == ["S13", "S14", "S08", "S15", "S05", "S06", "S12"]
assert queries[1]["normal"]["transfer_stations"] == ["S05"]
assert not queries[1]["normal_accessible_valid"]
assert queries[1]["accessible"]["stations"] == ["S13", "S14", "S08", "S04", "S05", "S06", "S12"]
assert queries[1]["accessible"]["transfers"] == 2
assert queries[2]["normal"]["stations"] == ["S07", "S08", "S15", "S05", "S16"]
assert queries[2]["normal"]["intervals"] == 4 and queries[2]["normal"]["transfers"] == 1
for r in queries:
    n = r["normal"]
    assert len(n["stations"]) == n["intervals"] + 1, "站数必须等于区间数+1"
    assert len(n["edge_lines"]) == n["intervals"]

# ---------------------------------------------------------------- shared palette
BG = "#F4F7FC"; NAVY = "#0B1B35"; NAVY2 = "#16386F"
WHITE = "#FFFFFF"; INK = "#0F172A"; MUTED = "#5B6B85"; LINE = "#DDE5F0"
R_COL = "#E11D48"; B_COL = "#2563EB"; G_COL = "#16A34A"
LINE_COL = {"R": R_COL, "B": B_COL, "G": G_COL}
LINE_CASE = {"R": "#9F1239", "B": "#1E3A8A", "G": "#14532D"}
TEAL = "#0D9488"; SLATE = "#94A3B8"; AMBER = "#B45309"

# ---------------------------------------------------------------- grid geometry
U = 62.0; OX = 60.0; OY = 170.0
GRID = {
    "S01": (1, 7), "S02": (3, 7), "S03": (5, 7), "S04": (8, 7),
    "S05": (13, 7), "S06": (16, 7), "S12": (19, 4),
    "S07": (8, 0), "S08": (8, 2), "S09": (8, 10), "S10": (11, 10),
    "S11": (14, 10),
    "S13": (3, 2), "S14": (5, 2), "S15": (10, 4), "S16": (16, 4),
}


def P(sid):
    gx, gy = GRID[sid]
    return OX + gx * U, OY + gy * U


# label chip top-left, two-line "Sxx / 名称".
# Chips are placed off every line (checked against R/B/G segment geometry) and
# connected to their station by a short leader, so no line is visually broken.
CHIP = {
    "S01": (80, 626), "S02": (204, 626), "S03": (328, 626), "S04": (600, 626),
    "S05": (824, 626), "S06": (1010, 626), "S07": (450, 118), "S08": (450, 236),
    "S09": (514, 806), "S10": (700, 806), "S11": (886, 806), "S12": (1150, 330),
    "S13": (204, 310), "S14": (328, 310), "S15": (570, 450), "S16": (1070, 440),
}
CHIP_W, CHIP_H = 84, 50
# line-letter badge at the start of each line (colour + letter), plus legend
BADGE = {
    "S01": (68, 552, "R"), "S07": (588, 132, "B"), "S13": (188, 250, "G"),
}
# S12 sits against the right panel: put its accessibility badge on the left.
BADGE_OFFSET = {"S12": (-19, -16)}


# ================================================================ MAP 1600x1000
def build_map():
    c = Canvas(1600, 1000, BG)
    # header
    c.gradient(0, 0, 1600, 108, [NAVY, NAVY2], begin="CENTER_LEFT", end="CENTER_RIGHT")
    c.rect(0, 104, 1600, 4, "#38BDF8")
    c.text(44, 16, 1000, 46, "云轨 · 三线换乘示意图", 34, WHITE, bold=True)
    c.text(44, 66, 1100, 30, "16 站 · 3 线 · 非地理拓扑示意 ｜ 线路折线转折仅 45° 或 90°", 19, "#BBD3F2")
    c.text(1240, 24, 320, 34, "A07 / NETWORK MAP", 19, "#8FB6EA", align="RIGHT", font=LATIN)
    c.text(1240, 62, 320, 28, "数据源 network.json", 17, "#BBD3F2", align="RIGHT")

    # right info panel
    c.rect(1250, 128, 310, 852, WHITE, radius=16, border="1 SOLID " + LINE)
    c.text(1270, 142, 270, 30, "线路 / 图例 / 核验", 23, INK, bold=True)
    c.rect(1270, 180, 270, 2, LINE)

    # line legend
    ly = 190
    for lid in line_order:
        c.rect(1272, ly + 4, 40, 26, LINE_COL[lid], radius=6)
        c.text(1272, ly + 3, 40, 26, lid, 18, WHITE, bold=True, align="CENTER", font=LATIN)
        c.text(1322, ly, 220, 32, "%s（%s）" % (line_name[lid], lid), 21, INK, bold=True)
        ly += 44

    c.rect(1270, 330, 270, 2, LINE)
    c.text(1270, 338, 270, 26, "换乘站（共享站）", 20, INK, bold=True)
    c.circle(1288, 380, 15, WHITE, border="3 SOLID " + INK)
    c.circle(1288, 380, 9, WHITE, border="2 SOLID " + INK)
    c.text(1314, 366, 240, 30, "双环 = 可换乘", 20, INK)
    c.text(1270, 400, 270, 52, "S04 中心（R×B）\nS05 东桥（R×G）\nS08 工坊（B×G）", 18, MUTED)

    c.rect(1270, 462, 270, 2, LINE)
    c.text(1270, 470, 270, 26, "无障碍设施状态", 20, INK, bold=True)
    c.circle(1288, 512, 8, TEAL)
    c.line(1284, 512, 1287, 515, 2.2, WHITE)
    c.line(1287, 515, 1293, 508, 2.2, WHITE)
    c.text(1306, 498, 250, 28, "具备（每站右上标）", 19, INK)
    c.circle(1288, 548, 8, SLATE)
    c.line(1285, 545, 1291, 551, 2.2, WHITE)
    c.line(1285, 551, 1291, 545, 2.2, WHITE)
    c.text(1306, 534, 250, 28, "不具备", 19, INK)
    c.text(1270, 566, 272, 76,
           "false 站仍可乘车途经，但不能作为无障碍旅程的起点、终点或换乘站；不因此删除线路。",
           18, MUTED)

    c.rect(1270, 650, 270, 2, LINE)
    c.text(1270, 658, 270, 26, "行程核验（详见旅行卡）", 19, INK, bold=True)
    cy = 690
    marks = ["Q1", "Q2", "Q3"]
    for i, r in enumerate(queries):
        n = r["normal"]
        tag = "可无障碍" if r["normal_accessible_valid"] else "需替代"
        c.text(1270, cy, 270, 24, "%s %s→%s" % (marks[i], r["from"], r["to"]), 18, INK)
        c.text(1270, cy + 24, 270, 24, "%d 区间 / 换乘 %d · %s" % (n["intervals"], n["transfers"], tag), 17,
               TEAL if r["normal_accessible_valid"] else AMBER)
        cy += 56

    c.rect(1270, 862, 270, 2, LINE)
    c.text(1270, 870, 272, 20, "单纯线条交叉不等于换乘", 17, INK, bold=True)
    c.text(1270, 890, 272, 88,
           "本图为非地理示意图：站点位置不代表真实地理方位或距离；线路仅以 45°/90° 折线表达连接。所有线路交汇点均为上述共享换乘站。",
           16, MUTED)

    # ---- lines (draw casing then colour)
    for lid in line_order:
        seq = lines[lid]["stations"]
        pts = [P(s) for s in seq]
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            c.line(x1, y1, x2, y2, 14, LINE_CASE[lid])
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            c.line(x1, y1, x2, y2, 9, LINE_COL[lid])

    # ---- line letter badges (colour + letter at each line start)
    for sid, (bx, by, lid) in BADGE.items():
        c.rect(bx, by, 36, 36, LINE_COL[lid], radius=8, border="2 SOLID " + WHITE)
        c.text(bx, by + 2, 36, 32, lid, 22, WHITE, bold=True, align="CENTER", font=LATIN)

    # ---- leaders from station centre to the nearest point on its chip border
    # (drawn before chips/markers so both ends are hidden; keeps lines continuous)
    for sid in order_ids:
        sx, sy = P(sid)
        lx, ly = CHIP[sid]
        px = min(max(sx, lx), lx + CHIP_W)
        py = min(max(sy, ly), ly + CHIP_H)
        c.line(sx, sy, px, py, 1.5, "#9AAAC2")

    # ---- label chips (name + number, >=20px); placed off the lines
    for sid in order_ids:
        lx, ly = CHIP[sid]
        c.rect(lx, ly, CHIP_W, CHIP_H, WHITE, radius=8, border="1 SOLID " + LINE)
        c.text(lx, ly + 1, CHIP_W, 24, sid, 20, INK, bold=True, align="CENTER", font=LATIN)
        c.text(lx, ly + 25, CHIP_W, 24, stations[sid]["name"], 20, INK, align="CENTER")

    # ---- station markers + accessibility badges (on top)
    for sid in order_ids:
        x, y = P(sid)
        ls = serving[sid]
        if len(ls) > 1:
            c.circle(x, y, 17, WHITE, border="3 SOLID " + INK)
            c.circle(x, y, 10, WHITE, border="2 SOLID " + INK)
            c.circle(x, y, 3, INK)
        else:
            c.circle(x, y, 10, WHITE, border="3 SOLID " + LINE_COL[ls[0]])
        dox, doy = BADGE_OFFSET.get(sid, (19, -19))
        bx, by = x + dox, y + doy
        acc = stations[sid]["accessible"]
        if acc:
            c.circle(bx, by, 8, TEAL)
            c.line(bx - 4, by, bx - 1, by + 3.2, 2.2, WHITE)
            c.line(bx - 1, by + 3.2, bx + 5, by - 4, 2.2, WHITE)
        else:
            c.circle(bx, by, 8, SLATE)
            c.line(bx - 3, by - 3, bx + 3, by + 3, 2.2, WHITE)
            c.line(bx - 3, by + 3, bx + 3, by - 3, 2.2, WHITE)

    # ---- footer
    c.text(44, 946, 1180, 26,
           "图例：R 红线 / B 蓝线 / G 绿线（颜色 + 线路字母双重区分）｜ 双环换乘站 ｜ 绿色勾/灰色叉为无障碍状态 ｜ 非地理示意图，区间数 = 站数 - 1。",
           17, MUTED)
    return c.render()


# ================================================================ CARD 720x1280
def short_name(lid):
    return lid


def chain_text(route):
    return "  →  ".join(route["stations"])


def ribbon(c, x, y, w, h, edge_lines):
    n = len(edge_lines)
    bw = w / n
    for i, lid in enumerate(edge_lines):
        c.rect(x + i * bw, y, bw - 2, h, LINE_COL[lid], radius=3)
        c.text(x + i * bw, y, bw - 2, h, lid, 20, WHITE, bold=True, align="CENTER", font=LATIN)


def draw_card(c, x, y, w, h, idx, q, r, tall):
    c.rect(x, y, w, h, WHITE, radius=18, border="1 SOLID " + LINE)
    c.rect(x, y, 6, h, TEAL if r["normal_accessible_valid"] else AMBER, radius=3)
    # index + title
    c.circle(x + 38, y + 34, 22, NAVY)
    c.text(x + 16, y + 12, 44, 44, idx, 24, WHITE, bold=True, align="CENTER", font=LATIN)
    c.text(x + 74, y + 12, w - 96, 44,
           "%s %s  →  %s %s" % (q["from"], stations[q["from"]]["name"],
                              q["to"], stations[q["to"]]["name"]),
           24, INK, bold=True)
    # normal route
    yy = y + 62
    c.text(x + 22, yy, 300, 28, "普通最短旅程", 21, INK, bold=True)
    n = r["normal"]
    c.text(x + w - 300, yy, 278, 28,
           "%d 区间 · 换乘 %d 次" % (n["intervals"], n["transfers"]),
           21, B_COL, bold=True, align="RIGHT")
    yy += 30
    c.text(x + 22, yy, w - 44, 28, chain_text(n), 20, INK)
    yy += 32
    ribbon(c, x + 22, yy, w - 44, 28, n["edge_lines"])
    yy += 32
    tr = n["transfer_stations"]
    c.text(x + 22, yy, w - 44, 26,
           "换乘：%s" % ("、".join("%s（%s→%s）" % (
               s, n["edge_lines"][n["stations"].index(s) - 1],
               n["edge_lines"][n["stations"].index(s)]) for s in tr) if tr else "无（全程一条线）"),
           20, MUTED)
    # accessibility verdict
    yy += 32
    c.rect(x + 22, yy - 2, w - 44, 2, LINE)
    c.text(x + 22, yy + 6, 300, 28, "无障碍判定", 21, INK, bold=True)
    ok = r["normal_accessible_valid"]
    c.circle(x + 300, yy + 20, 15, TEAL if ok else "#DC2626")
    if ok:
        c.line(x + 294, yy + 20, x + 298, yy + 24, 2.5, WHITE)
        c.line(x + 298, yy + 24, x + 306, yy + 14, 2.5, WHITE)
    else:
        c.line(x + 295, yy + 15, x + 305, yy + 25, 2.5, WHITE)
        c.line(x + 295, yy + 25, x + 305, yy + 15, 2.5, WHITE)
    if ok:
        c.text(x + 324, yy + 6, w - 346, 54,
               "起终点与换乘站均有设施 → 该最短路线可直接作为无障碍旅程。", 20, TEAL)
    else:
        c.text(x + 324, yy + 6, w - 346, 54,
               "换乘站 %s 无设施 → 不满足；%s" % (
                   "、".join(r["normal_invalid_transfer_stations"]),
                   "另求最短无障碍路线。" if r["accessible"] else "无可行无障碍路线。"),
               20, AMBER)
    if tall and r["accessible"]:
        a = r["accessible"]
        yy += 66
        c.text(x + 22, yy, w - 44, 28, "替代 · 最短无障碍旅程", 21, INK, bold=True)
        c.text(x + w - 300, yy, 278, 28,
               "%d 区间 · 换乘 %d 次" % (a["intervals"], a["transfers"]),
               21, TEAL, bold=True, align="RIGHT")
        yy += 30
        c.text(x + 22, yy, w - 44, 28, chain_text(a), 20, INK)
        yy += 32
        ribbon(c, x + 22, yy, w - 44, 28, a["edge_lines"])
        yy += 30
        tr2 = a["transfer_stations"]
        c.text(x + 22, yy, w - 44, 26,
               "换乘：%s ｜ S05 仅途经不换乘" % (
                   "、".join("%s（%s→%s）" % (
                       s, a["edge_lines"][a["stations"].index(s) - 1],
                       a["edge_lines"][a["stations"].index(s)]) for s in tr2) if tr2 else "无"),
               20, MUTED)
        yy += 28
        c.text(x + 22, yy, w - 44, 28,
               "false 站仅可途经（S03/S05/S09/S14）",
               20, MUTED)
    return c


def build_card():
    c = Canvas(720, 1280, BG)
    c.gradient(0, 0, 720, 126, [NAVY, NAVY2], begin="CENTER_LEFT", end="CENTER_RIGHT")
    c.rect(0, 122, 720, 4, "#38BDF8")
    c.text(28, 14, 660, 44, "旅行卡 · 路线与无障碍核验", 32, WHITE, bold=True)
    c.text(28, 60, 660, 30, "3 段行程 ｜ 普通最短 与 无障碍最短 ｜ 区间数 = 站数 - 1", 19, "#BBD3F2")
    c.text(28, 94, 660, 26, "云轨 · 非地理示意图（与全网图同一视觉系统）", 17, "#8FB6EA")

    idxs = ["1", "2", "3"]
    cards = [(136, 260), (408, 410), (830, 260)]
    for i, (yy, hh) in enumerate(cards):
        draw_card(c, 24, yy, 672, hh, idxs[i], queries[i], queries[i], tall=(i == 1))

    # footer legend
    fy = 1100
    c.rect(24, fy, 672, 156, WHITE, radius=16, border="1 SOLID " + LINE)
    c.text(44, fy + 10, 620, 28, "图例 / 规则", 22, INK, bold=True)
    lx = 44
    for lid in line_order:
        c.rect(lx, fy + 44, 34, 24, LINE_COL[lid], radius=6)
        c.text(lx, fy + 44, 34, 24, lid, 18, WHITE, bold=True, align="CENTER", font=LATIN)
        c.text(lx + 42, fy + 42, 120, 28, line_name[lid], 20, INK)
        lx += 176
    c.circle(56, fy + 90, 9, TEAL)
    c.text(72, fy + 78, 250, 28, "具备无障碍设施", 20, INK)
    c.circle(360, fy + 90, 9, SLATE)
    c.text(376, fy + 78, 300, 28, "不具备（可作途经站）", 20, INK)
    c.text(44, fy + 108, 630, 30,
           "换乘=改变乘坐线路（首次上车不计）；按(区间数,换乘数)取最优。",
           18, MUTED)
    return c.render()


# ================================================================ outputs
dsl_map = build_map()
dsl_card = build_card()
out = suite.out_dir(TASK)
(out / "network-map.snapshot").write_text(dsl_map, encoding="utf-8")
(out / "travel-card.snapshot").write_text(dsl_card, encoding="utf-8")
ver = os.environ.get("BUILD_VERSION", "v1")
tmp = suite.tmp_dir(TASK, ver)
(tmp / "network-map.snapshot").write_text(dsl_map, encoding="utf-8")
(tmp / "travel-card.snapshot").write_text(dsl_card, encoding="utf-8")

# ---- routes.json --------------------------------------------------
def audit_route(route):
    d = {k: route[k] for k in ("stations", "edge_lines", "intervals", "transfers", "transfer_stations")}
    d["station_count"] = len(route["stations"])
    d["note"] = "区间数 = 站数 − 1 = %d − 1 = %d" % (len(route["stations"]), route["intervals"])
    return d


accessibility = []
for sid in order_ids:
    st = stations[sid]
    used = []
    for i, r in enumerate(queries):
        roles = []
        for mode in ("normal", "accessible"):
            rt = r[mode]
            if not rt:
                continue
            if sid in (r["from"], r["to"]):
                roles.append("%s:端点" % mode)
            if sid in rt["transfer_stations"]:
                roles.append("%s:换乘" % mode)
            if sid in rt["stations"] and sid not in (r["from"], r["to"]) and sid not in rt["transfer_stations"]:
                roles.append("%s:途经" % mode)
        if roles:
            used.append("Q%d:%s" % (i + 1, "/".join(roles)))
    accessibility.append({
        "id": sid, "name": st["name"], "accessible": st["accessible"],
        "shared_transfer_station": sid in shared,
        "lines": serving.get(sid, []),
        "roles_in_queries": used,
    })

optimality = []
for i, r in enumerate(queries):
    for mode in ("normal", "accessible"):
        rt = r[mode]
        if not rt:
            optimality.append({"query": i + 1, "mode": mode, "result": None,
                               "reason": "无可行路线（端点不具备无障碍设施）"})
            continue
        optimality.append({
            "query": i + 1, "mode": mode,
            "objective": "(区间数 intervals, 换乘数 transfers) 字典序最小",
            "method": "以 (站点, 当前线路) 为状态做 Dijkstra/BFS；乘车边权(1,0)，换乘边权(0,1)；换乘仅在共享站；无障碍模式另要求端点 accessible=true 且换乘站 accessible=true。",
            "result": {"intervals": rt["intervals"], "transfers": rt["transfers"],
                       "stations": rt["stations"]},
            "why_optimal": "所有候选按区间数升序、换乘数升序枚举；该状态值最小。区间数按站间边计，站数=区间数+1。",
        })

content_map = []
card_y = {0: (152, 422), 1: (434, 834), 2: (846, 1116)}
for i, r in enumerate(queries):
    for mode in ("normal", "accessible"):
        rt = r[mode]
        if not rt:
            continue
        content_map.append({
            "query": i + 1, "route": mode,
            "network_map_region": "左侧全网示意图：站点 %s；线路段 %s" % (
                "、".join(rt["stations"]), "".join(rt["edge_lines"])),
            "network_map_panel": "右侧『行程核验』第 %d 行" % (i + 1),
            "travel_card_region": "第 %d 张行程卡 y=%d..%d（%s 段）" % (
                i + 1, card_y[i][0], card_y[i][1], "普通" if mode == "normal" else "无障碍判定/替代"),
            "check": "routes.json 站序/线路段/区间数/换乘数与两图文字一致；最短性由 optimality 计算依据支持；无障碍判定依据 accessible 属性（端点与换乘站）。",
        })

routes = {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "units": {"intervals": "站间边数（区间数）", "transfers": "改变乘坐线路次数（首次上车不计）",
              "length": "所有相邻站耗时相同，故只比较区间数与换乘数"},
    "graph": {
        "lines": {lid: {"name": line_name[lid], "stations": lines[lid]["stations"]} for lid in line_order},
        "shared_transfer_stations": {s: {"lines": ls, "accessible": stations[s]["accessible"]}
                                     for s, ls in shared.items()},
        "note": "共享站为换乘站；单纯线条交叉不构成换乘。本图所有线路交汇点均为共享换乘站。",
    },
    "rules": {
        "accessible_true": "可作起点、终点、换乘站及途经站。",
        "accessible_false": "仅可乘车通过（途经），不可作无障碍旅程的起点、终点或换乘站；不删除线路。",
        "transfer_definition": "改变乘坐线路即计 1 次换乘，第一次上车不计。",
        "objective": "先最少站间边数（区间数），相同时再选换乘最少。",
        "interval_vs_station": "区间数 = 站序长度 − 1，不可把站数当作区间数。",
    },
    "queries": [
        {
            "from": r["from"], "to": r["to"],
            "from_name": stations[r["from"]]["name"], "to_name": stations[r["to"]]["name"],
            "normal": audit_route(r["normal"]),
            "accessible": audit_route(r["accessible"]) if r["accessible"] else None,
            "accessible_note": (r["accessible"]["note"] if r["accessible"]
                                else "无可行无障碍路线：端点不具备无障碍设施。"),
            "normal_is_valid_accessible": r["normal_accessible_valid"],
            "normal_invalid_transfer_stations": r["normal_invalid_transfer_stations"],
        } for r in queries
    ],
    "accessibility": accessibility,
    "optimality": optimality,
    "content_map": content_map,
    "evidence": {
        "png": ["network-map.png", "travel-card.png"],
        "dsl": ["network-map.snapshot", "travel-card.snapshot"],
        "checks": ["站数 = 区间数 + 1", "换乘=改变线路且首次上车不计",
                   "无障碍端点/换乘站 accessible=true", "false 站仅途经",
                   "按(区间数,换乘数)取最优"],
    },
}
(out / "routes.json").write_text(json.dumps(routes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("A07 | map bytes", len(dsl_map.encode("utf-8")), "| card bytes", len(dsl_card.encode("utf-8")))
for r in queries:
    print("  ", r["from"], "->", r["to"], "normal", r["normal"]["intervals"], r["normal"]["transfers"],
          "acc_valid", r["normal_accessible_valid"],
          "acc", None if not r["accessible"] else (r["accessible"]["intervals"], r["accessible"]["transfers"]))
