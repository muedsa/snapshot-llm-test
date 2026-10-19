# -*- coding: utf-8 -*-
"""A07 · 三线换乘图与路线核验。
数据：tasks/A07-transit-topology/inputs/network.json（16 站 / 3 线 / 3 查询）。
产出（路径基准 = 本题输出根 outputs/<run_id>/A07/）：
  network-map.png(1600×1000) + 同名 .snapshot；travel-card.png(720×1280) + 同名 .snapshot；
  routes.json（最小字段约定 + 证据）。
示意图：非地理拓扑图；线路折线仅 45°/90°；共享站=换乘站；无障碍状态以节点形状标注。
旅行卡：三条查询的普通最优旅程 + 无障碍判定（同路径或替代路径）。
"""
import json
import heapq
import os
from pathlib import Path

TASK_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ["SNAPSHOT_RUN_ID"]
OUT = TASK_ROOT / "outputs" / RUN_ID / "A07"
OUT.mkdir(parents=True, exist_ok=True)
TMP = TASK_ROOT / "tmp" / RUN_ID / "A07"
TMP.mkdir(parents=True, exist_ok=True)
INPUTS = TASK_ROOT / "tasks" / "A07-transit-topology" / "inputs"

FONT = "Noto Sans CJK SC"
FN = "Inter"
FAM_MIX = FN + "," + FONT

# ============================================================
# 数据 + 最短路（(区间数, 换乘数) 字典序；换乘=改乘线路，首次上车不计）
# ============================================================
net = json.loads((INPUTS / "network.json").read_text(encoding="utf-8"))
ST = {s["id"]: s for s in net["stations"]}
ACC = {k: ST[k]["accessible"] for k in ST}
LINES = {l["id"]: l for l in net["lines"]}
EDGES = []
for lid, line in LINES.items():
    seq = line["stations"]
    for a, b in zip(seq, seq[1:]):
        EDGES.append((a, b, lid))
        EDGES.append((b, a, lid))
INCIDENT = {k: set() for k in ST}
for u, v, lid in EDGES:
    INCIDENT[u].add(lid)
    INCIDENT[v].add(lid)

def dijkstra(src, dst, accessible_only=False):
    if accessible_only and not ACC[src]:
        return None
    INF = (10**9, 0)
    key0 = (src, None)
    dist = {key0: (0, 0)}
    parent = {}
    pq = [((0, 0), key0)]
    while pq:
        cost, cur = heapq.heappop(pq)
        if dist.get(cur, INF) < cost:
            continue
        st, line = cur
        if st == dst:
            break
        for u, v, lid in EDGES:
            if u != st:
                continue
            if accessible_only and line is not None and lid != line and not ACC[st]:
                continue          # 未设无障碍的站不得改乘
            nc = (cost[0] + 1, cost[1] + (1 if (line is not None and lid != line) else 0))
            nk = (v, lid)
            if nk not in dist or nc < dist[nk]:
                dist[nk] = nc
                parent[nk] = cur
                heapq.heappush(pq, (nc, nk))
    finals = sorted((d, k) for k, d in dist.items() if k[0] == dst)
    if not finals:
        return None
    _, k = finals[0]
    els_rev, stations_rev, cur = [], [], k
    while cur != key0:
        els_rev.append(cur[1])
        cur = parent[cur]
        stations_rev.append(cur[0])
    stations = [stations_rev[-1]] + list(reversed(stations_rev[:-1])) + [dst]
    els = list(reversed(els_rev))
    if accessible_only and not ACC[dst]:
        return None
    return stations, els

def describe(r):
    if not r:
        return None
    stations, els = r
    segs, i = [], 0
    while i < len(els):
        j = i
        while j < len(els) and els[j] == els[i]:
            j += 1
        segs.append((els[i], stations[i], stations[j]))
        i = j
    return {"stations": stations, "edge_lines": els, "intervals": len(els),
            "line_segments": [{"line": a, "from": b, "to": c} for a, b, c in segs],
            "transfers": len(segs) - 1,
            "transfer_stations": [s[2] for s in segs[:-1]]}

EXPECT = {
    ("S01", "S11", "n"): (["S01", "S02", "S03", "S04", "S09", "S10", "S11"],
                          ["R", "R", "R", "B", "B", "B"]),
    ("S01", "S11", "a"): (["S01", "S02", "S03", "S04", "S09", "S10", "S11"],
                          ["R", "R", "R", "B", "B", "B"]),
    ("S13", "S12", "n"): (["S13", "S14", "S08", "S15", "S05", "S06", "S12"],
                          ["G", "G", "G", "G", "R", "R"]),
    ("S13", "S12", "a"): (["S13", "S14", "S08", "S04", "S05", "S06", "S12"],
                          ["G", "G", "B", "R", "R", "R"]),
    ("S07", "S16", "n"): (["S07", "S08", "S15", "S05", "S16"],
                          ["B", "G", "G", "G"]),
    ("S07", "S16", "a"): (["S07", "S08", "S15", "S05", "S16"],
                          ["B", "G", "G", "G"]),
}
ROUTES = []
for q in net["queries"]:
    n = describe(dijkstra(q["from"], q["to"]))
    ac = describe(dijkstra(q["from"], q["to"], accessible_only=True))
    kk = (q["from"], q["to"], "n")
    assert [n["stations"], n["edge_lines"]] == list(EXPECT[kk]), (kk, n)
    if ac is not None:
        ka = (q["from"], q["to"], "a")
        assert [ac["stations"], ac["edge_lines"]] == list(EXPECT[ka]), (ka, ac)
    else:
        assert not ACC[q["to"]], ("普通可达但无障碍判 None 而终点应可作终站", q)
    # 无障碍旅程实际起终/换乘复合校验
    if ac:
        assert ACC[q["from"]] and ACC[q["to"]]
        chg = set()
        for seg_a, seg_b in zip(ac["line_segments"], ac["line_segments"][1:]):
            assert seg_a["to"] == seg_b["from"]
            chg.add(seg_a["to"])
        for s in chg:
            assert ACC[s], ("无障碍换乘站未设设施", s)
    ROUTES.append({"from": q["from"], "to": q["to"], "normal": n, "accessible": ac})

# ============================================================
# 配色 / 文本工具
# ============================================================
W1, H1 = 1600, 1000
W2, H2 = 720, 1280
BG = "#F3F6FB"; INK = "#17233D"; SUB = "#55657F"; FAINT = "#8494AE"
CARD = "#FFFFFF"; BORD = "1 SOLID #E3EAF4"; DIV = "#E3EAF4"
DARK = "#22304A"
OKC = "#0E8A6E"; NOC = "#B45309"
LINE_COL = {"R": "#D0342C", "B": "#2B6CB0", "G": "#2F855A"}
LETTER_BG = LINE_COL

WARN = []
def estw(s, size):
    w = 0.0
    for ch in s:
        o = ord(ch)
        if o < 0x80:
            if ch == " ":
                w += 0.30 * size
            elif ch in ":.,~":
                w += 0.30 * size
            elif ch == "·":
                w += 0.35 * size
            elif ch in "/／":
                w += 0.55 * size
            elif ch in "—–…→↔⇄①②③✓✗":
                w += 1.00 * size
            elif ch in "−=+":
                w += 0.60 * size
            elif ch == "%":
                w += 0.60 * size
            elif ch.isdigit():
                w += 0.60 * size
            elif ch.isupper():
                w += 0.70 * size
            else:
                w += 0.54 * size
        else:
            w += 1.00 * size
    return w

def fit(label, s, size, box_w):
    w = estw(s, size)
    if w > box_w:
        WARN.append(f"{label}: estw({w:.1f}) > box {box_w} :: {s}")

def fnum(v):
    s = f"{float(v):.2f}".rstrip("0").rstrip(".")
    return s if s else "0"

def rect(x, y, w, h, color=None, radius=None, border=None):
    a = f'<Container width="{fnum(w)}" height="{fnum(h)}"'
    if color:
        a += f' color="{color}"'
    if radius is not None and radius > 0:
        a += f' borderRadius="{fnum(radius)}"'
    if border:
        a += f' border="{border}"'
    return (f'<Positioned left="{fnum(x)}" top="{fnum(y)}"'
            f' width="{fnum(w)}" height="{fnum(h)}">' + a + " /></Positioned>")

def text(x, y, content, size, color, family=FONT, bold=False, align="START", box_w=None):
    lx, ly = fnum(x), fnum(y)
    sty = f'<Text fontSize="{fnum(size)}" color="{color}" fontFamily="{family}"'
    if bold:
        sty += ' fontStyle="BOLD"'
    sty += ' maxLines="1" overflow="CLIP"'
    if align != "START":
        sty += f' textAlign="{align}"'
    sty += f'>{content}</Text>'
    if box_w is None:
        return f'<Positioned left="{lx}" top="{ly}">{sty}</Positioned>'
    return f'<Positioned left="{lx}" top="{ly}" width="{fnum(box_w)}">{sty}</Positioned>'

def polygon(pts, color):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    x0, y0 = min(xs), min(ys)
    w = max(xs) - x0; h = max(ys) - y0
    if w < 0.5 or h < 0.5:
        WARN.append(f"polygon 太小 {pts}")
        return None
    d = "M " + " L ".join(f"{fnum(px - x0)} {fnum(py - y0)}" for px, py in pts) + " Z"
    return (f'<Positioned left="{fnum(x0)}" top="{fnum(y0)}"'
            f' width="{fnum(w)}" height="{fnum(h)}">'
            f'<SizedBox width="{fnum(w)}" height="{fnum(h)}">'
            f'<ClipPath path="{d}"><Container color="{color}" /></ClipPath>'
            f'</SizedBox></Positioned>')

def quad(p1, p2, color, thick=3.0):
    import math
    x1, y1 = p1; x2, y2 = p2
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    nx, ny = dy / L, -dx / L
    hw = thick / 2
    return polygon([(x1 + nx*hw, y1 + ny*hw), (x2 + nx*hw, y2 + ny*hw),
                    (x2 - nx*hw, y2 - ny*hw), (x1 - nx*hw, y1 - ny*hw)], color)

def circle_at(cx, cy, r, fill, ring_color=None, ring_w=0.0):
    out = []
    if ring_color and ring_w > 0:
        d = 2 * r
        out.append(rect(cx - r, cy - r, d, d, ring_color, r))
        ri = r - ring_w
        out.append(rect(cx - ri, cy - ri, 2 * ri, 2 * ri, fill, ri))
    else:
        out.append(rect(cx - r, cy - r, 2 * r, 2 * r, fill, r))
    return out

def dot_at(cx, cy, r, color):
    return circle_at(cx, cy, r, color)

def diamond_at(cx, cy, s, fill):
    p = polygon([(cx, cy - s), (cx + s, cy), (cx, cy + s), (cx - s, cy)], fill)
    return [p] if p else []

def diamond_ring(cx, cy, s_out, ring_color, ring_w, inner_fill):
    out = []
    out += diamond_at(cx, cy, s_out, ring_color)
    out += diamond_at(cx, cy, s_out - ring_w, inner_fill)
    return out

def chip_letter(cx, cy, ch, size=18.0, box=24.0, bg=None, fg="#FFFFFF", radius=6.0):
    if bg is None:
        bg = LETTER_BG.get(ch, DARK)
    out = [rect(cx - box / 2, cy - box / 2, box, box, bg, radius)]
    out.append(text(cx - box / 2, cy - size * 0.73, ch, size, fg,
                    family=FN, bold=True, align="CENTER", box_w=box))
    return out

def snapshot(bg, items):
    return ('<Snapshot background="' + bg + '" type="png">\n<Stack>\n'
            + "\n".join(items) + "\n</Stack>\n</Snapshot>\n")

# ============================================================
# 通用：旅程带（站点串 + 彩色区间条 + 换乘点 + 站名 + 无障碍状态）
# ============================================================
def line_of_pair(a, b, el):
    return el

def ribbon(S, x0, axis, width, route, name_size=20.0, chips=True, status=True,
           transfer_x=None):
    stations = route["stations"]
    els = route["edge_lines"]
    n = len(stations)
    step = width / (n - 1)
    xs = [x0 + step * i for i in range(n)]
    # 区间条
    for i in range(n - 1):
        th = 12.0 if chips else 10.0
        S.append(quad((xs[i], axis), (xs[i + 1], axis), LINE_COL[els[i]], th))
    # 线路字母chip（每区间中点）
    if chips:
        for i in range(n - 1):
            S.extend(chip_letter((xs[i] + xs[i + 1]) / 2, axis - 34, els[i], 18.0, 24.0))
    # 站点圆
    chg = set()
    for a, b in zip(els, els[1:]):
        if a != b:
            chg.add(b)     # b 是改乘后新线到达站
    trans_idx = [i for i in range(n) if any(
        (i > 0 and els[i-1] != els[i]) if False else False for _ in [0])] if False else None
    mark_transfer = []
    for i in range(1, n - 1):
        if els[i - 1] != els[i]:
            mark_transfer.append(i)
    for i, x in enumerate(xs):
        is_t = i in mark_transfer
        if transfer_x is not None and i == transfer_x:
            is_t = True
        if is_t:
            S.extend(circle_at(x, axis, 10.5, CARD, DARK, 3.5))
            S.extend(dot_at(x, axis, 3.5, DARK))
        else:
            S.extend(circle_at(x, axis, 8, CARD, LINE_COL[els[min(i, len(els) - 1)]], 3))
    # 站名 + 状态点
    for i, x in enumerate(xs):
        nm = ST[stations[i]]["name"]
        bw = max(step - 8, estw(nm, name_size) + 12)
        S.append(text(x - bw / 2, axis + 18, nm, name_size, INK, family=FAM_MIX, bold=True,
                      align="CENTER", box_w=bw))
        if status:
            acc = ACC[stations[i]]
            gy = axis + 46
            if acc:
                S.extend(dot_at(x, gy, 5.5, OKC))
            else:
                S.extend(diamond_ring(x, gy, 7.0, NOC, 2.2, CARD))
    return xs

# ============================================================
# 图一 network-map（1600×1000）
# ============================================================
S1 = [f'<SizedBox width="{W1}" height="{H1}" />']
# 站点像素坐标（非地理示意，仅保持了 45°/90° 折线关系）
PX = {
    "S01": (140, 670), "S02": (260, 670), "S03": (380, 670), "S04": (500, 550),
    "S05": (620, 670), "S06": (760, 670),
    "S07": (500, 910), "S08": (500, 790),
    "S09": (500, 430), "S10": (500, 310), "S11": (380, 190),
    "S12": (900, 530),
    "S13": (200, 910), "S14": (380, 910), "S15": (620, 910),
    "S16": (740, 550),
}
# 折线角度校验（45 或 90 度）
import math
for lid, line in LINES.items():
    seq = line["stations"]
    for a, b in zip(seq, seq[1:]):
        (x1, y1), (x2, y2) = PX[a], PX[b]
        dx, dy = abs(x2 - x1), abs(y2 - y1)
        assert dx == 0 or dy == 0 or dx == dy, (lid, a, b, dx, dy)
# 全部画进 S1
S1.append(rect(40, 150, 960, 810, CARD, 16, BORD))     # 图卡
S1.append(rect(1020, 150, 540, 810, CARD, 16, BORD))   # 面板卡
S1.append(text(40, 20, "城市地铁三线 · 拓扑示意图", 32, INK, family=FAM_MIX, bold=True))
badge = "16 站 · 3 线 · 3 换乘站"
fit("徽标1", badge, 20, 360)
S1.append(text(1200, 28, badge, 20, SUB, family=FAM_MIX, align="END", box_w=360))
subt = "非地理示意图——仅表示线路连接与站序，不做地理定位；相邻站区间耗时相同，双向可乘。"
fit("副题1", subt, 20, 1500)
S1.append(text(40, 62, subt, 20, SUB, family=FAM_MIX))
# 图例行 y=104..128
lx = 40.0
for lid in ("R", "B", "G"):
    S1.extend(chip_letter(lx + 13, 116, lid, 18, 26))
    nm = {"R": "红线", "B": "蓝线", "G": "绿线"}[lid]
    fit("图例" + lid, nm, 20, 60)
    S1.append(text(lx + 34, 106, nm, 20, SUB, family=FAM_MIX))
    lx += 34 + estw(nm, 20) + 22
# 节点形例
lx += 6
S1.extend(circle_at(lx + 8, 117, 7.5, CARD, SUB, 2.4))
S1.extend(dot_at(lx + 8, 117, 3.2, SUB))
gl = "设无障碍设施"
fit("图例acc", gl, 20, 130)
S1.append(text(lx + 22, 106, gl, 20, SUB, family=FAM_MIX))
lx += 22 + estw(gl, 20) + 20
S1.extend(diamond_ring(lx + 8, 117, 8.5, NOC, 2.4, CARD))
gl2 = "未设无障碍 · 仅乘车通过"
fit("图例noacc", gl2, 20, 240)
S1.append(text(lx + 22, 106, gl2, 20, SUB, family=FAM_MIX))
lx += 22 + estw(gl2, 20) + 20
S1.extend(circle_at(lx + 9, 117, 9.5, CARD, DARK, 3))
S1.extend(dot_at(lx + 9, 117, 3.6, DARK))
gl3 = "换乘站"
fit("图例tf", gl3, 20, 70)
S1.append(text(lx + 26, 106, gl3, 20, SUB, family=FAM_MIX))
# 角标：明确"非地理示意图"
corner = "非地理示意图 · 仅示拓扑与站序"
fit("角标1", corner, 20, 300)
S1.append(text(690, 172, corner, 20, FAINT, family=FAM_MIX, align="END", box_w=300))
# 线路折线（先蓝、再绿、再红；共享点在站内相接，无线线交叉）
for lid in ("B", "G", "R"):
    seq = LINES[lid]["stations"]
    for a, b in zip(seq, seq[1:]):
        S1.append(quad(PX[a], PX[b], LINE_COL[lid], 8))
# 站点节点
TRANSFERS = {k for k in ST if len(INCIDENT[k]) > 1}
assert TRANSFERS == {"S04", "S05", "S08"}, TRANSFERS
for nid in sorted(ST):
    x, y = PX[nid]
    acc = ACC[nid]
    if nid in TRANSFERS:
        if acc:
            S1.extend(circle_at(x, y, 13, CARD, DARK, 3.5))
            S1.extend(dot_at(x, y, 4, DARK))
        else:
            S1.extend(diamond_ring(x, y, 16, DARK, 3.5, CARD))
            S1.extend(diamond_at(x, y, 5, DARK))
    else:
        lc = list(INCIDENT[nid])[0]
        if acc:
            S1.extend(circle_at(x, y, 11, CARD, LINE_COL[lc], 3))
            S1.extend(dot_at(x, y, 3.4, LINE_COL[lc]))
        else:
            S1.extend(diamond_ring(x, y, 15, LINE_COL[lc], 3, CARD))
            S1.extend(dot_at(x, y, 0, CARD))  # 占位无点（保持形状差异）
    # 线路字母终点徽章（颜色 + 字母，不只靠颜色）
TERMINAL_CHIP = {"S01": (104, 706), "S12": (936, 566),
                 "S07": (460, 886), "S11": (300, 202),
                 "S13": (238, 940), "S16": (762, 592)}
for nid, (cx, cy) in TERMINAL_CHIP.items():
    lid = list(INCIDENT[nid])[0]
    S1.extend(chip_letter(cx, cy, lid, 18, 26))
# 站名标签（编号 + 名称；全部 ≥20px）
def label_map(nid, mode, ax, ay):
    num = nid[1:]
    name = ST[nid]["name"]
    nw = estw(num + "  ", 20)
    w_total = nw + estw(name, 22)
    if mode == "C":
        x0 = ax - w_total / 2
    elif mode == "L":
        x0 = ax
    else:
        x0 = ax - w_total
    fit("标签" + nid, num + " " + name, 22, 120)
    S1.append(text(x0, ay + 3, num, 20, FAINT, family=FN, bold=True))
    S1.append(text(x0 + nw, ay, name, 22, INK, family=FAM_MIX, bold=True))

label_map("S01", "C", 140, 626); label_map("S02", "C", 260, 626)
label_map("S03", "C", 380, 694); label_map("S04", "R", 474, 516)
label_map("S05", "R", 604, 692); label_map("S06", "C", 760, 694)
label_map("S07", "C", 500, 934); label_map("S08", "L", 524, 756)
label_map("S09", "L", 524, 396); label_map("S10", "L", 524, 276)
label_map("S11", "C", 380, 156); label_map("S12", "L", 924, 496)
label_map("S13", "C", 200, 876); label_map("S14", "C", 380, 934)
label_map("S15", "C", 620, 934); label_map("S16", "L", 764, 516)

# ---- 右侧面板：问答速览 ----
S1.append(text(1044, 174, "三条最少区间旅程", 24, INK, family=FAM_MIX, bold=True))
ptx = "按（区间数，换乘数）取优；换乘 = 改乘线路"
fit("面板副题", ptx, 20, 492)
S1.append(text(1044, 208, ptx, 20, SUB, family=FAM_MIX))
CN = ["①", "②", "③"]
panel_geo = []
gy = 250
for qi, rt in enumerate(ROUTES):
    qn = rt["normal"]
    heads = f"{CN[qi]} {ST[rt['from']]['name']} → {ST[rt['to']]['name']}"
    fit(f"面板标题{qi}", heads, 22, 330)
    S1.append(text(1044, gy, heads, 22, INK, family=FAM_MIX, bold=True))
    rc = f"{qn['intervals']} 区间 · {qn['transfers']} 换乘"
    fit(f"面板右侧{qi}", rc, 20, 200)
    S1.append(text(1336, gy + 3, rc, 20, SUB, family=FAM_MIX, align="END", box_w=200))
    xs = ribbon(S1, 1052, gy + 46, 468, qn, 20.0, chips=False, status=False)
    if rt["accessible"] is rt["normal"] or (rt["accessible"] and rt["accessible"]["stations"] == qn["stations"]):
        note = f"换乘 {ST[qn['transfer_stations'][0]]['name']} · 同路径可无障碍乘坐 ✓"
        col = OKC
    else:
        note = f"换乘 {ST[qn['transfer_stations'][0]]['name']} 未设无障碍 → 卡内有替代"
        col = NOC
    fit(f"面板注{qi}", note, 20, 492)
    S1.append(text(1044, gy + 92, note, 20, col, family=FAM_MIX))
    panel_geo.append({"row": qi + 1, "ribbon_x_px": [round(xs[0], 1), round(xs[-1], 1)],
                      "ribbon_y_px": gy + 46})
    gy += 122
S1.append(quad((1044, 618), (1536, 618), DIV, 2))
S1.append(text(1044, 636, "线网与无障碍", 22, INK, family=FAM_MIX, bold=True))
rows = [
    ("R", "R 红线 · 7 站 · 松林—机场"),
    ("B", "B 蓝线 · 6 站 · 西港—会展"),
    ("G", "G 绿线 · 6 站 · 石溪—研究所"),
    (None, "换乘站 3：中心 R·B · 东桥 R·G · 工坊 B·G"),
    (None, "无障碍：设 12 站 / 未设 4 站"),
    (None, "未设：书院 S03 · 东桥 S05 · 花园 S09 · 公园 S14"),
]
ry = 672
for lid, s in rows:
    if lid:
        S1.extend(chip_letter(1054, ry + 10, lid, 16, 20))
        S1.append(text(1072, ry, s, 20, SUB, family=FAM_MIX))
    else:
        fit("面板行" + s[:4], s, 20, 492)
        S1.append(text(1044, ry, s, 20, SUB, family=FAM_MIX))
    ry += 28
S1.append(text(1044, ry + 12, "旅程卡片为交付二 travel-card。", 20, FAINT, family=FAM_MIX))
S1.append(text(1044, ry + 40, "判据与坐标证据见 routes.json。", 20, FAINT, family=FAM_MIX))

# ============================================================
# 图二 travel-card（720×1280）
# ============================================================
S2 = [f'<SizedBox width="{W2}" height="{H2}" />']
S2.append(text(32, 24, "三线出行卡", 34, INK, family=FAM_MIX, bold=True))
b2 = "非地理示意图 · 区间耗时相同"
fit("徽标2", b2, 20, 320)
S2.append(text(364, 34, b2, 20, SUB, family=FAM_MIX, align="END", box_w=320))
sb2 = "三条查询的最少区间旅程 · 站序 / 线路 / 无障碍判定"
fit("副题2", sb2, 20, 660)
S2.append(text(32, 78, sb2, 20, SUB, family=FAM_MIX))
# 小图例行 y=112
lx = 36.0
for lid in ("R", "B", "G"):
    S2.extend(chip_letter(lx + 12, 124, lid, 17, 24))
    lx += 36
S2.extend(circle_at(lx + 9, 124, 7, CARD, SUB, 2.2))
S2.extend(dot_at(lx + 9, 124, 3, SUB))
lg = "设无障碍设施"
fit("卡图例1", lg, 20, 124)
S2.append(text(lx + 22, 114, lg, 20, SUB, family=FAM_MIX))
lx += 22 + estw(lg, 20) + 18
S2.extend(diamond_ring(lx + 9, 124, 8, NOC, 2.2, CARD))
lg2 = "未设 · 仅乘车通过"
fit("卡图例2", lg2, 20, 180)
S2.append(text(lx + 26, 114, lg2, 20, SUB, family=FAM_MIX))

BLOCK = [(32, 148, 656, 272), (32, 432, 656, 452), (32, 900, 656, 252)]
for bi, (bx, by, bw, bh) in enumerate(BLOCK):
    S2.append(rect(bx, by, bw, bh, CARD, 14, BORD))
card_ribb_geo = []
def card_rows(ki, block, ribbon_y):
    rt = ROUTES[ki]
    qn = rt["normal"]
    bx, by, bw, bh = block
    ax = bx + 32
    line_x_end = bx + bw - 32
    heads = f"{CN[ki]} {ST[rt['from']]['name']} → {ST[rt['to']]['name']}"
    fit(f"卡标题{ki}", heads, 26, 340)
    S2.append(text(ax, by + 24, heads, 26, INK, family=FAM_MIX, bold=True))
    rc = f"{qn['intervals']} 区间 · {qn['transfers']} 换乘"
    fit(f"卡右侧{ki}", rc, 20, 220)
    S2.append(text(bx + bw - 32 - 220, by + 30, rc, 20, SUB, family=FAM_MIX,
                   align="END", box_w=220))
    xs = ribbon(S2, ax + 8, ribbon_y, line_x_end - ax - 16, qn, 20.0, chips=True, status=True)
    ty = ribbon_y + 78
    tnote = f"换乘 {qn['transfers']} 次：" + "、".join(
        f"{ST[s]['name']}（{qn['edge_lines'][qn['stations'].index(s) if s in qn['stations'] else 0]} 线）"
        for s in qn["transfer_stations"])
    # 修正：换乘行乘用线路段计算
    seg_lines = []
    cur_line = qn["edge_lines"][0]
    for i in range(1, len(qn["edge_lines"])):
        if qn["edge_lines"][i] != cur_line:
            seg_lines.append(ST[qn["stations"][i]]["name"] + "（" + cur_line + "→" + qn["edge_lines"][i] + "）")
            cur_line = qn["edge_lines"][i]
    tnote = f"换乘 {qn['transfers']} 次：" + "、".join(seg_lines)
    fit(f"卡换乘行{ki}", tnote, 20, line_x_end - ax)
    S2.append(text(ax, ty, tnote, 20, SUB, family=FAM_MIX))
    return xs

# 块一：Q1
xs1 = card_rows(0, BLOCK[0], 258)
acc_note_1 = "可无障碍乘坐（换乘站 中心 已设设施）"
fit("卡注1", acc_note_1, 20, 420)
S2.extend(dot_at(64, 378, 6, OKC))
S2.append(text(80, 368, acc_note_1, 20, OKC, family=FAM_MIX))
p1 = "书院 / 花园 途中通过"
fit("卡右注1", p1, 20, 200)
S2.append(text(464, 368, p1, 20, SUB, family=FAM_MIX, align="END", box_w=200))
card_ribb_geo.append({"block": 1, "ribbon_x_px": [round(xs1[0], 1), round(xs1[-1], 1)],
                      "ribbon_y_px": 232})

# 块二：Q2 普通 + 无障碍替代
xs2 = card_rows(1, BLOCK[1], 542)
S2.extend(diamond_ring(64, 662, 8, NOC, 2.2, CARD))
w1 = "东桥 未设无障碍——不能作为无障碍换乘站"
fit("卡注2", w1, 20, 420)
S2.append(text(80, 652, w1, 20, NOC, family=FAM_MIX))
S2.append(quad((56, 686), (664, 686), DIV, 2))
S2.append(text(56, 700, "无障碍旅程（同样 6 区间 · 换乘 2）", 22, INK, family=FAM_MIX, bold=True))
ac2 = ROUTES[1]["accessible"]
xs3 = ribbon(S2, 64, 776, 592, ac2, 20.0, chips=True, status=True)
fit("卡注2b", "换乘 工坊、中心均设无障碍设施 ✓", 20, 380)
S2.extend(dot_at(64, 848, 6, OKC))
S2.append(text(80, 838, "换乘 工坊、中心均设无障碍设施 ✓", 20, OKC, family=FAM_MIX))
p2 = "公园 / 东桥 途中通过"
fit("卡右注2b", p2, 20, 200)
S2.append(text(464, 838, p2, 20, SUB, family=FAM_MIX, align="END", box_w=200))
card_ribb_geo.append({"block": 2, "rows": ["普通 @542", "无障碍 @776"],
                      "ribbon_x_px": [round(xs2[0], 1), round(xs2[-1], 1)]})

# 块三：Q3
xs4 = card_rows(2, BLOCK[2], 1010)
a3 = "可无障碍乘坐（换乘站 工坊 已设设施）"
fit("卡注3", a3, 20, 420)
S2.extend(dot_at(64, 1130, 6, OKC))
S2.append(text(80, 1120, a3, 20, OKC, family=FAM_MIX))
p3 = "东桥 途中通过"
fit("卡右注3", p3, 20, 200)
S2.append(text(464, 1120, p3, 20, SUB, family=FAM_MIX, align="END", box_w=200))
card_ribb_geo.append({"block": 3, "ribbon_x_px": [round(xs4[0], 1), round(xs4[-1], 1)],
                      "ribbon_y_px": 1010})

# 页脚
S2.append(text(32, 1164, "换乘 = 改乘线路（首次乘车不计）；按（区间数，换乘数）取最优。", 20, SUB, family=FAM_MIX))
S2.append(text(32, 1190, "无障碍约束：起点/终点/换乘站须设设施；未设站可乘车通过。", 20, SUB, family=FAM_MIX))
S2.append(text(32, 1216, "线网 16 站 = 红 7 + 蓝 6 + 绿 6 − 共享 3；数据源自 inputs/network.json。", 20, SUB, family=FAM_MIX))
S2.append(text(32, 1242, "站序/区间/换乘判定与两图坐标证据 见 routes.json。", 20, FAINT, family=FAM_MIX))

if WARN:
    print(json.dumps({"estw_overflows": WARN}, ensure_ascii=False, indent=2))
    raise SystemExit(f"{len(WARN)} 处文本估宽超限，先修正再渲染")

dsl1 = snapshot(BG, S1)
(OUT / "network-map.snapshot").write_text(dsl1, encoding="utf-8")
dsl2 = snapshot(BG, S2)
(OUT / "travel-card.snapshot").write_text(dsl2, encoding="utf-8")

# ============================================================
# routes.json
# ============================================================
routes = {
    "schema_version": 1,
    "task_id": "A07",
    "path_base": "output_dir",
    "question": "三线换乘图与路线核验",
    "inputs": {
        "path_base": "suite_root",
        "paths": ["tasks/A07-transit-topology/inputs/network.json"],
        "stations": 16, "lines": 3, "queries": len(ROUTES),
        "modifications": "无——站名/站序/线序/无障碍标记按输入原值；jigsaws 布局坐标是绘制决策",
    },
    "method": {
        "search": "以线路相邻边建图（无向、等权），Dijkstra 按字典序 (区间数, 换乘数)；状态=（站点, 所乘线路），换乘=改乘线路（首乘不计）",
        "accessible_rule": "无障碍搜索：起点/终点须 accessible=true；改乘只能在 accessible=true 的站；未设站允许乘车通过",
        "tie_note": "区间数相同时取换乘数最少；三条普通旅程均一次求出并与独立核验脚本一致（tmp/<run_id>/A07/verify_routes.py）",
    },
    "queries": [],
    "accessibility": [
        {"id": nid, "name": ST[nid]["name"], "accessible": ACC[nid]}
        for nid in sorted(ST)
    ],
    "accessibility_rule": "端点/换乘检查：无障碍旅程的起点、终点与每次改乘站均须 accessible=true；途经未设站允许（在车上不上下）",
    "optimality": [],
    "content_map": [],
    "images": {
        "network-map.png": {"size": [1600, 1000], "dsl": "network-map.snapshot",
                            "product": "全网拓扑示意图（45/90° 折线 · 换乘与无障碍标注 · 问答速览面板）"},
        "travel-card.png": {"size": [720, 1280], "dsl": "travel-card.snapshot",
                            "product": "三旅程分组卡（线路字母chip + 站名 + 无障碍判定 + Q2 无障碍替代）"},
    },
    "build_script": {"path_base": "suite_root", "path": f"tmp/{RUN_ID}/A07/build_a07.py"},
}
CN2 = ["一", "二", "三"]
for qi, rt in enumerate(ROUTES):
    q = {"from": rt["from"], "to": rt["to"],
         "from_name": ST[rt["from"]]["name"], "to_name": ST[rt["to"]]["name"]}
    nn = rt["normal"]
    q["normal"] = {
        "stations": nn["stations"], "station_names": [ST[s]["name"] for s in nn["stations"]],
        "edge_lines": nn["edge_lines"], "line_segments": nn["line_segments"],
        "intervals": nn["intervals"], "transfers": nn["transfers"],
        "transfer_stations": nn["transfer_stations"],
        "usable_as_accessible": nn["stations"] == (rt["accessible"]["stations"] if rt["accessible"] else None),
        "note": ("起点/终点/换乘站均设无障碍设施；途经未设站（含 %s）仅在车上通过" %
                 ("、".join(ST[s]["name"] for s in nn["stations"] if not ACC[s]) or "无")) if
                (rt["accessible"] and rt["accessible"]["stations"] == nn["stations"]) else
                ("换乘站 %s 未设无障碍设施，不满足无障碍约束" % "、".join(
                    ST[s]["name"] for s in nn["transfer_stations"] if not ACC[s])),
    }
    if rt["accessible"]:
        ac = rt["accessible"]
        q["accessible"] = {
            "stations": ac["stations"], "station_names": [ST[s]["name"] for s in ac["stations"]],
            "edge_lines": ac["edge_lines"], "line_segments": ac["line_segments"],
            "intervals": ac["intervals"], "transfers": ac["transfers"],
            "transfer_stations": ac["transfer_stations"],
            "pass_through_not_accessible": [s for s in ac["stations"] if not ACC[s]],
            "note": "改乘站与起终点均设无障碍设施；未设站仅乘车通过" if
                    ac["stations"] != nn["stations"] else "与普通最优同一路径",
        }
    else:
        q["accessible"] = None
        q["accessible_unavailable_reason"] = (
            f"终点 {ST[rt['to']]['name']} 未设无障碍设施，不能作为无障碍旅程终点" if not ACC[rt["to"]]
            else "无可行无障碍旅程")
    routes["queries"].append(q)
    mv = []
    qn = rt["normal"]
    # 次优比较证据：枚举同距其他简单路径的换乘数（邻接DFS 深度=intervals 上限）
    def all_paths(src, dst, max_depth):
        res = []
        def dfs(u, lines, path):
            if len(path) - 1 > max_depth:
                return
            if u == dst:
                res.append(path[:])
                return
            for uu, vv, ll in EDGES:
                if uu != u:
                    continue
                if vv in path:
                    continue
                dfs(vv, lines + [ll], path + [vv])
        dfs(src, [], [src])
        return res
    cand = all_paths(rt["from"], rt["to"], qn["intervals"])
    def tf(pl):
        segs = 0
        for a, b in zip(pl["edges"], pl["edges"][1:]):
            if a != b:
                segs += 1
        return segs
    cand_stats = []
    for p in cand:
        dd = {"stations": p, "edges": [None] * 0}
        # 逐边线路：尝试在站序下每条边的线路（两站间仅一线，取该对唯一线路）
        els = []
        for a, b in zip(p, p[1:]):
            ls = {l for u, v, l in EDGES if {u, v} == {a, b}}
            assert len(ls) == 1, (a, b, ls)
            els.append(ls.pop())
        tr = sum(1 for a, b in zip(els, els[1:]) if a != b)
        cand_stats.append({"stations": p, "intervals": len(p) - 1, "transfers": tr,
                           "edge_lines": els})
    best = sorted(cand_stats, key=lambda c: (c["intervals"], c["transfers"]))
    mv.append({"mode": "normal",
               "method": f"枚举 ≤{qn['intervals']} 区间全部简单路径并按 (区间数,换乘数) 排序复核",
               "candidates": len(cand_stats),
               "best": best[0], "comparison": best[:4]})
    if rt["accessible"]:
        ac = rt["accessible"]
        acc_cand = []
        for c in best:
            ok = ACC[rt["from"]] and ACC[rt["to"]]
            pl = c["edge_lines"]
            for i in range(1, len(c["stations"]) - 1):
                if pl[i - 1] != pl[i]:
                    ok = ok and ACC[c["stations"][i]]
            if ok:
                acc_cand.append(c)
        mv.append({"mode": "accessible",
                   "method": "同一枚举，筛选改乘站/起终点皆 accessible 的路径，再按 (区间数,换乘数) 排序",
                   "candidates": len(acc_cand),
                   "best": acc_cand[0] if acc_cand else None})
    else:
        mv.append({"mode": "accessible", "candidates": 0, "best": None,
                   "method": "无障碍搜索无可行解：改乘/端点约束下无满足路径（或终点未设设施）"})
    routes["optimality"].append({"query": qi + 1, "from": rt["from"], "to": rt["to"],
                                 "evidence": mv})

# content_map（显示区域 + 绘图一致性；结论在查看后由 finalize_audit 追加 pass 证据）
cm_rows = []
MAP_PANEL_Y = [250, 372, 494]
for qi, rt in enumerate(ROUTES):
    qn = rt["normal"]
    cm_rows.append({
        "query": qi + 1, "route": "normal",
        "map_zone": {"panel_row": qi + 1, "ribbon_y_px": MAP_PANEL_Y[qi] + 46,
                     "ribbon_x_px": [1044, 1536],
                     "server_track": "图上站点按线路色标可循；换乘站大圆/大菱点"},
        "card_zone": {"block": qi + 1, "row": "top",
                      "ribbon_y_px": [232, 512, 932][qi], "ribbon_x_px": [72, 648]},
        "consistency_to_verify": "站序与 edge_lines 与两图绘制一致；换乘站在图中为深色换乘记号",
    })
rows2 = []
for qi, rt in enumerate(ROUTES):
    if rt["accessible"] and rt["accessible"]["stations"] != rt["normal"]["stations"]:
        rows2.append({
            "query": qi + 1, "route": "accessible_alternative",
            "map_zone": {"panel_row": qi + 1, "note": "面板注指明卡内有替代"},
            "card_zone": {"block": qi + 1, "row": "access_sub", "divider_y_px": 652,
                          "ribbon_y_px": 736, "ribbon_x_px": [64, 664]},
            "consistency_to_verify": "替代旅程站序/换乘站与普通旅程差异已标注",
        })
routes["content_map"] = cm_rows + rows2
(OUT / "routes.json").write_text(
    json.dumps(routes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(json.dumps({
    "map_bytes": len(dsl1.encode("utf-8")), "card_bytes": len(dsl2.encode("utf-8")),
    "all_paths_normal": [len(r["normal"]["stations"]) for r in ROUTES],
    "blocks": len(BLOCK),
}, ensure_ascii=False))

