"""A07: three-line metro schematic (1600x1000) + travel card (720x1280).

Single source of truth: tasks/A07-transit-topology/inputs/network.json is parsed once,
laid out on an octilinear grid where every hop is exactly STEP pixels, routed by
exhaustive simple-path enumeration, and both images plus routes.json come out of those
same tables.

Guarantees asserted before any DSL is written:
  * 16 stations, 16 hops, all hop lengths equal, so "adjacent hops take the same time"
    is true on screen and not merely claimed in a footnote;
  * every bend is 45 or 90 degrees;
  * no two stations coincide, no station lies on a non-incident hop, and hops only meet
    at shared stations, so a line crossing can never be mistaken for an interchange;
  * every station label is placed by a collision-avoiding solver (hops, station dots,
    other labels, header/legend bands) and every text box passes the pre-render fit gate.
"""
import itertools
import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(ROOT / "tmp" / RID / "_suite" / "scripts"))
from dslkit import Doc, TextFit  # noqa: E402

TASK = "A07"
TEMP = ROOT / "tmp" / RID / TASK
OUT = ROOT / "outputs" / RID / TASK
INP = ROOT / "tasks" / "A07-transit-topology" / "inputs" / "network.json"
VERSION = os.environ.get("DSL_VERSION", "v01")

# ---- shared visual system ---------------------------------------------------
BG = "#0B1220"
PANEL = "#101A2E"
PANEL_LINE = "#2B3C5C"
INK = "#F1F5F9"
DIM = "#94A3B8"
FAINT = "#6B7E9B"
ACC = "#38BDF8"
NOACC = "#FBBF24"
LCOL = {"R": "#F87171", "B": "#60A5FA", "G": "#34D399"}
LNAME = {"R": "红线", "B": "蓝线", "G": "绿线"}

STEP = 200.0
DIAG = STEP / math.sqrt(2)
M = 32
MW, MH = 1600, 1000
CW, CH = 720, 1280
MAP_TOP, MAP_BOT = 150, 740          # header / legend bands are off-limits for labels
LEGEND_Y, LEGEND_H = 752, 216
# 186px keeps two labels on the same side of adjacent horizontal stations clear of
# each other (hop pitch is 200px and the overlap test pads by 6px).
LAB_W, LAB_H = 186.0, 58.0


# ---- graph ------------------------------------------------------------------
def load():
    g = json.loads(INP.read_text(encoding="utf-8"))
    stations = {s["id"]: s for s in g["stations"]}
    lines = {l["id"]: l["stations"] for l in g["lines"]}
    hops = [(lid, a, b) for lid, seq in lines.items() for a, b in zip(seq, seq[1:])]
    adj = {sid: [] for sid in stations}
    for lid, a, b in hops:
        adj[a].append((lid, b))
        adj[b].append((lid, a))
    return stations, lines, hops, adj, g["queries"]


STATIONS, LINES, HOPS, ADJ, QUERIES = load()
ACC_ID = {s: STATIONS[s]["accessible"] for s in STATIONS}
NAME = {s: STATIONS[s]["name"] for s in STATIONS}
SLINES = {s: sorted({lid for lid, _ in ADJ[s]}) for s in STATIONS}
DEG = {s: len(SLINES[s]) for s in STATIONS}
QMARK = {}
for i, q in enumerate(QUERIES):
    for sid in (q["from"], q["to"]):
        QMARK.setdefault(sid, []).append("①②③"[i])


# ---- layout -----------------------------------------------------------------
P = {}
P["S04"] = (760.0, 516.0)
for k, v in (("S03", -STEP), ("S02", -2 * STEP), ("S01", -3 * STEP)):
    P[k] = (P["S04"][0] + v, P["S04"][1])
for k, v in (("S05", STEP), ("S06", 2 * STEP), ("S12", 3 * STEP)):
    P[k] = (P["S04"][0] + v, P["S04"][1])
P["S08"] = (P["S04"][0] - DIAG, P["S04"][1] - DIAG)
P["S07"] = (P["S08"][0] - STEP, P["S08"][1])
P["S15"] = (P["S08"][0] + STEP, P["S08"][1])
P["S14"] = (P["S08"][0] - DIAG, P["S08"][1] - DIAG)
P["S13"] = (P["S14"][0] - STEP, P["S14"][1])
P["S09"] = (P["S04"][0] - DIAG, P["S04"][1] + DIAG)
P["S10"] = (P["S09"][0] - STEP, P["S09"][1])
P["S11"] = (P["S10"][0] - STEP, P["S10"][1])
P["S16"] = (P["S05"][0] + DIAG, P["S05"][1] + DIAG)


def segs_cross(p1, p2, p3, p4):
    def o(a, b, c):
        v = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
        return 0 if abs(v) < 1e-9 else (1 if v > 0 else -1)
    return o(p1, p2, p3) != o(p1, p2, p4) and o(p3, p4, p1) != o(p3, p4, p2)


def check_layout():
    errs = []
    if set(P) != set(STATIONS):
        errs.append(f"布局站数 {len(P)} != 输入 {len(STATIONS)}")
    seen = {}
    for sid, (x, y) in P.items():
        key = (round(x, 3), round(y, 3))
        if key in seen:
            errs.append(f"{sid} 与 {seen[key]} 位置重合")
        seen[key] = sid
        if not (M + 60 <= x <= MW - M - 60 and MAP_TOP <= y <= MAP_BOT):
            errs.append(f"{sid} 越出可用区 ({x:.1f},{y:.1f})")
    for lid, a, b in HOPS:
        (x1, y1), (x2, y2) = P[a], P[b]
        if abs(math.hypot(x2 - x1, y2 - y1) - STEP) > 0.5:
            errs.append(f"{lid} {a}-{b} 长度不等于 {STEP}")
        ang = math.degrees(math.atan2(y2 - y1, x2 - x1)) % 90
        if min(abs(ang - v) for v in (0.0, 45.0, 90.0)) > 0.2:
            errs.append(f"{lid} {a}-{b} 转折角 {ang:.2f} 不是 45/90 整数倍")

    def seg_dist(pt, s1, s2):
        (px, py), (x1, y1), (x2, y2) = pt, s1, s2
        dx, dy = x2 - x1, y2 - y1
        t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
        return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))

    for sid in STATIONS:
        for lid, a, b in HOPS:
            if sid not in (a, b) and seg_dist(P[sid], P[a], P[b]) < 26:
                errs.append(f"{sid} 落在非共享区间 {a}-{b} 上，会被误认为换乘")
    for (l1, a1, b1), (l2, a2, b2) in itertools.combinations(HOPS, 2):
        if not ({a1, b1} & {a2, b2}) and segs_cross(P[a1], P[b1], P[a2], P[b2]):
            errs.append(f"区间 {a1}-{b1} 与 {a2}-{b2} 在无站处交叉")
    return errs


# ---- routing ----------------------------------------------------------------
def all_paths(src, dst):
    out, stack = [], [(src, [src], [])]
    while stack:
        cur, path, lines = stack.pop()
        if cur == dst:
            out.append((path, lines))
            continue
        for lid, nxt in ADJ[cur]:
            if nxt not in path:
                stack.append((nxt, path + [nxt], lines + [lid]))
    return out


def changes(lines):
    return sum(1 for x, y in zip(lines, lines[1:]) if x != y)


def change_stations(path, lines):
    return [path[i + 1] for i, (x, y) in enumerate(zip(lines, lines[1:])) if x != y]


def segments(path, lines):
    out, start = [], 0
    for i in range(1, len(lines)):
        if lines[i] != lines[start]:
            out.append((lines[start], path[start:i + 1]))
            start = i
    out.append((lines[start], path[start:]))
    return out


def accessible_ok(path, lines):
    if not (ACC_ID[path[0]] and ACC_ID[path[-1]]):
        return False, "起终点缺少无障碍设施"
    bad = [s for s in change_stations(path, lines) if not ACC_ID[s]]
    if bad:
        return False, "换乘站 " + "、".join(f"{s} {NAME[s]}" for s in bad) + " 缺无障碍设施"
    return True, ""


def describe(path, lines):
    segs = segments(path, lines)
    return {
        "stations": list(path),
        "station_names": [f"{s} {NAME[s]}" for s in path],
        "station_count": len(path),
        "edges": len(path) - 1,
        "interchanges": changes(lines),
        "interchange_stations": change_stations(path, lines),
        "line_sequence": "+".join(lid for lid, _ in segs),
        "line_segments": [{"line": lid, "line_name": LNAME[lid], "stations": list(ps),
                           "hops": len(ps) - 1} for lid, ps in segs],
        "passes_non_accessible": [s for s in path[1:-1] if not ACC_ID[s]],
        "accessible_journey_eligible": accessible_ok(path, lines)[0],
    }


def solve(src, dst):
    cands = all_paths(src, dst)
    assert cands, f"{src}->{dst} 不可达"
    ranked = sorted(cands, key=lambda c: (len(c[0]) - 1, changes(c[1]), c[0]))
    best = len(ranked[0][0]) - 1
    ties = [c for c in ranked if len(c[0]) - 1 == best]
    primary = ranked[0]
    ok, why = accessible_ok(primary[0], primary[1])
    acc = next((c for c in ranked if accessible_ok(c[0], c[1])[0]), None)
    return {
        "from": src, "to": dst,
        "normal": describe(primary[0], primary[1]),
        "same_edge_alternatives": [describe(p, l) for p, l in ties],
        "normal_is_accessible": ok,
        "normal_block_reason": why,
        "accessible": describe(acc[0], acc[1]) if acc else None,
        "accessible_is_same_route": bool(acc and acc[0] == primary[0]),
    }


ROUTES = [solve(q["from"], q["to"]) for q in QUERIES]


# ---- label placement --------------------------------------------------------
# (dx, dy) are offsets of the label *centre-x* and *top-y* from the station dot,
# tried in order: the four cardinal slots first, then the corners, then farther
# out with a leader line. Centred anchoring keeps a label of a horizontal line's
# station inside the 200px hop pitch, so neighbours never fight for the same slot.
CANDIDATES = [(0, -(LAB_H + 16)), (0, 20),
              (-(LAB_W / 2 + 26), -(LAB_H / 2 - 4)), (LAB_W / 2 + 26, -(LAB_H / 2 - 4)),
              (-(LAB_W / 2 + 26), -(LAB_H + 18)), (LAB_W / 2 + 26, -(LAB_H + 18)),
              (-(LAB_W / 2 + 26), 30), (LAB_W / 2 + 26, 30),
              (0, -(LAB_H + 92)), (0, 96),
              (-(LAB_W / 2 + 220), -(LAB_H / 2 - 4)), (LAB_W / 2 + 220, -(LAB_H / 2 - 4)),
              (0, -(LAB_H + 168)), (0, 172)]


def rect_hits_seg(r, p1, p2):
    x0, y0, x1, y1 = r
    if (p1[0] < x0 and p2[0] < x0) or (p1[0] > x1 and p2[0] > x1):
        return False
    if (p1[1] < y0 and p2[1] < y0) or (p1[1] > y1 and p2[1] > y1):
        return False
    if x0 <= p1[0] <= x1 and y0 <= p1[1] <= y1:
        return True
    if x0 <= p2[0] <= x1 and y0 <= p2[1] <= y1:
        return True
    c = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    return any(segs_cross(p1, p2, c[i], c[(i + 1) % 4]) for i in range(4))


def rects_overlap(a, b, pad=6.0):
    return not (a[2] + pad <= b[0] or b[2] + pad <= a[0]
                or a[3] + pad <= b[1] or b[3] + pad <= a[1])


def trim_seg(pt, other, keep):
    """Hop with its first `keep` px removed, so a label may sit beside its own
    station without the ribbon it hangs off being counted as a collision."""
    dx, dy = other[0] - pt[0], other[1] - pt[1]
    k = min(keep / math.hypot(dx, dy), 0.45)
    return (pt[0] + dx * k, pt[1] + dy * k), other


def place_labels():
    order = sorted(STATIONS, key=lambda s: (-DEG[s], s))
    placed, fails = {}, []
    for sid in order:
        x, y = P[sid]
        for dx, dy in CANDIDATES:
            r = (x + dx - LAB_W / 2, y + dy, x + dx + LAB_W / 2, y + dy + LAB_H)
            if r[0] < M + 14 or r[1] < MAP_TOP - 4 or r[2] > MW - M - 14 \
                    or r[3] > LEGEND_Y - 12:
                continue
            # ribbons are 12px wide, so the box must clear them by half that
            g = (r[0] - 8, r[1] - 8, r[2] + 8, r[3] + 8)
            bad = any(rect_hits_seg(g, *trim_seg(P[sid], P[o], 34))
                      for _, a, b in HOPS if sid in (a, b)
                      for o in ({a, b} - {sid}))
            bad = bad or any(rect_hits_seg(g, P[a], P[b]) for _, a, b in HOPS
                             if sid not in (a, b))
            bad = bad or any(rect_contains(r, cx, cy)
                             for o, (cx, cy) in P.items() if o != sid)
            bad = bad or any(rects_overlap(r, q) for q in placed.values())
            if not bad:
                placed[sid] = r
                break
        else:
            # deterministic fallback so the run still produces a reviewable image;
            # the station is reported in `fails` and blocks delivery in main().
            placed[sid] = (x - LAB_W / 2, y - LAB_H - 16, x + LAB_W / 2, y - 16)
            fails.append(sid)
    return placed, fails


def rect_contains(r, cx, cy):
    return r[0] - 24 <= cx <= r[2] + 24 and r[1] - 24 <= cy <= r[3] + 24


# ---- drawing helpers --------------------------------------------------------
FIT = TextFit()


class Painter:
    def __init__(self, w, h):
        self.d = Doc(w, h, bg=BG)
        self.W, self.H = w, h

    def rect(self, x, y, w, h, color=None, radius=None, border=None):
        self.d.pos(x, y, w, h, self.d.box(w, h, color=color, radius=radius,
                                          border=border))

    def label(self, x, y, w, h, s, color=INK, size=20, style=None, align="START",
              tag=None, lines=1):
        FIT.check(tag or f"@{x:.0f},{y:.0f}", s, size, w, h, lines)
        self.d.label(x, y, w, h, s, color, size, style, align=align)

    def seg(self, x1, y1, x2, y2, t, color):
        self.d.line(x1, y1, x2, y2, t, color)

    def dot(self, x, y, dd, color):
        self.d.dot(x, y, dd, color)

    def chip(self, x, y, w, h, s, fg, bg, size=18, radius=None):
        self.d.chip(x, y, w, h, s, fg, bg, size=size, radius=radius)

    def xml(self):
        return self.d.dsl()


def station_dot(p, x, y, sid):
    lids = SLINES[sid]
    ring = LCOL[lids[0]] if len(lids) == 1 else "#F8FAFC"
    if len(lids) > 1:
        p.dot(x, y, 30, ring)
        p.dot(x, y, 22, BG)
        p.dot(x, y, 13, "#F8FAFC")
    else:
        p.dot(x, y, 20, ring)
        p.dot(x, y, 12, "#F8FAFC" if ACC_ID[sid] else ring)
    if not ACC_ID[sid]:
        # the slash must not run along a ribbon it sits on, or it disappears
        dirs = []
        for _, a, b in HOPS:
            if sid in (a, b):
                o = P[b if a == sid else a]
                dirs.append(math.degrees(math.atan2(o[1] - y, o[0] - x)) % 180)

        def spread(deg):
            return min(min(abs(deg - d) % 180, 180 - abs(deg - d) % 180) for d in dirs)
        best = max((45.0, 135.0), key=spread) if dirs else 45.0
        ux, uy = math.cos(math.radians(best)), math.sin(math.radians(best))
        r = 19
        p.seg(x - r * ux, y - r * uy, x + r * ux, y + r * uy, 4, NOACC)


# ---- map --------------------------------------------------------------------
def build_map():
    p = Painter(MW, MH)
    placed, fails = place_labels()

    p.rect(M, M, MW - 2 * M, MH - 2 * M, None, 18, f"1 SOLID {PANEL_LINE}")
    p.label(M + 24, 40, 700, 44, "虚构城市 · 三线换乘示意图", INK, 32, "BOLD",
            tag="title")
    p.label(M + 24, 86, 1170, 26,
            "非地理地图：方位与距离不代表实际里程，也不代表真实站间距离，只按线路站序连接相邻站。",
            DIM, 20, tag="sub1")
    p.label(M + 24, 114, 1170, 26,
            f"{len(HOPS)} 条区间一律等长（图面上各 {STEP:.0f}px），"
            "因此“相邻站耗时相同”在图上直接成立；每条区间双向均可通行。",
            DIM, 20, tag="sub2")
    p.label(MW - M - 560, 46, 536, 26,
            f"数据 inputs/network.json：{len(STATIONS)} 站 · {len(LINES)} 线 · "
            f"{len(HOPS)} 区间", FAINT, 20, align="END", tag="src")

    for lid in ("R", "B", "G"):
        seq = LINES[lid]
        for a, b in zip(seq, seq[1:]):
            (x1, y1), (x2, y2) = P[a], P[b]
            p.seg(x1, y1, x2, y2, 12, LCOL[lid])
        for sid in seq:
            p.dot(P[sid][0], P[sid][1], 12, LCOL[lid])
        # colour is not enough: put the line letter on the ribbon itself
        mid = (len(seq) - 1) // 2
        a, b = seq[mid], seq[mid + 1]
        mx, my = (P[a][0] + P[b][0]) / 2, (P[a][1] + P[b][1]) / 2
        p.chip(mx - 14, my - 11, 28, 22, lid, "#0B1220", LCOL[lid], size=17, radius=6)

    for sid in sorted(STATIONS):
        station_dot(p, P[sid][0], P[sid][1], sid)

    for sid in sorted(STATIONS):
        x, y = P[sid]
        r = placed[sid]
        mark = "".join(QMARK.get(sid, []))
        p.label(r[0], r[1] + 2, LAB_W, 28, f"{mark} {sid} {NAME[sid]}".strip(), INK,
                24, "BOLD", align="CENTER", tag=f"n.{sid}")
        p.label(r[0], r[1] + 32, LAB_W, 26,
                f"线路 {'+'.join(SLINES[sid])} · {'有设施' if ACC_ID[sid] else '无设施'}",
                ACC if ACC_ID[sid] else NOACC, 20, align="CENTER", tag=f"a.{sid}")
        # leader from the label's nearest edge point to the station symbol, so a
        # diagonally offset label can never be read as belonging to a neighbour.
        tx = min(max(x, r[0]), r[2])
        ty = min(max(y, r[1]), r[3])
        gap = math.dist((tx, ty), (x, y))
        if gap > 26:
            k = 20.0 / gap
            p.seg(tx, ty, x + (tx - x) * k, y + (ty - y) * k, 1, "#4A5D80")

    LY = LEGEND_Y
    p.rect(M + 16, LY, MW - 2 * M - 32, LEGEND_H, PANEL, 14, f"1 SOLID {PANEL_LINE}")
    p.label(M + 36, LY + 14, 120, 28, "图例", INK, 22, "BOLD", tag="lg.title")
    KX = M + 156          # keys start clear of the "图例" heading

    def key(x, cy, t, col=DIM):
        w = FIT.w(t, 20) * 1.06 + 6
        p.label(x, cy - 13, w, 26, t, col, 20, tag=f"lg{cy:.0f}@{x:.0f}")
        return x + w

    y1 = LY + 44
    x = KX
    for lid in ("R", "B", "G"):
        p.seg(x, y1, x + 46, y1, 12, LCOL[lid])
        p.chip(x + 9, y1 - 12, 28, 24, lid, "#0B1220", LCOL[lid], size=18, radius=6)
        x = key(x + 58, y1, f"{LNAME[lid]} {len(LINES[lid])} 站") + 30
    p.dot(x + 14, y1, 30, "#F8FAFC")
    p.dot(x + 14, y1, 22, BG)
    p.dot(x + 14, y1, 13, "#F8FAFC")
    x = key(x + 36, y1, "双环＝换乘站") + 26
    p.dot(x + 10, y1, 20, LCOL["B"])
    p.dot(x + 10, y1, 12, "#F8FAFC")
    x = key(x + 28, y1, "单环＝普通站") + 26
    if x > MW - M - 36:
        FIT.problems.append(f"legend row1 overflow {x:.0f} > {MW - M - 36}")

    y2 = LY + 88
    x = M + 36
    p.dot(x + 10, y2, 20, LCOL["R"])
    p.dot(x + 10, y2, 12, LCOL["R"])
    p.seg(x - 4, y2 - 14, x + 24, y2 + 14, 4, NOACC)
    x = key(x + 32, y2, "斜杠＝缺无障碍设施") + 26
    p.rect(x, y2 - 11, 22, 22, ACC, 5)
    x = key(x + 30, y2, "有设施（站名下行青色）") + 26
    p.rect(x, y2 - 11, 22, 22, NOACC, 5)
    x = key(x + 30, y2, "无设施（琥珀）") + 26
    x = key(x, y2, "①②③＝三条查询旅程的起终点") + 26
    if x > MW - M - 36:
        FIT.problems.append(f"legend row2 overflow {x:.0f} > {MW - M - 36}")

    notes = [
        f"换乘＝两线共享车站（S04、S05、S08 用双环）；{len(HOPS)} 条区间两两检测，无站处交叉数为 0，"
        "所以线条不会伪造换乘。",
        "缺设施站仍可上下车通过，但不能作为无障碍旅程的起终点或换乘站；本图不删站不删线，"
        "只在旅行卡中另求符合该约束的旅程。",
        "线路识别用颜色＋字母 R/B/G 双重编码（图例、区间中部徽标、每站“线路 …”行），"
        "不单靠红绿差别。",
    ]
    ny = LY + 108
    for i, t in enumerate(notes):
        nl = FIT.lines(t, 20, MW - 2 * M - 88)
        p.label(M + 44, ny, MW - 2 * M - 88, nl * 29 + 4, t, FAINT, 20,
                tag=f"note{i}", lines=nl)
        ny += nl * 29 + 4
    if ny > LY + LEGEND_H - 6:
        FIT.problems.append(f"notes overflow {ny:.0f} > {LY + LEGEND_H - 6}")
    return p.xml(), placed, fails


# ---- travel card ------------------------------------------------------------
def build_card():
    p = Painter(CW, CH)
    p.rect(M, M, CW - 2 * M, CH - 2 * M, None, 20, f"1 SOLID {PANEL_LINE}")
    p.label(M + 22, 44, CW - 2 * M - 44, 38, "三条旅程核验卡", INK, 30, "BOLD",
            tag="title")
    kx = CW - M - 22 - 3 * 36 - 56
    p.label(kx, 50, 52, 26, "线路", DIM, 20, tag="key")
    for i, lid in enumerate(("R", "B", "G")):
        p.chip(kx + 56 + i * 36, 48, 30, 26, lid, "#0B1220", LCOL[lid], size=18,
               radius=7)
    p.label(M + 22, 88, 452, 26, "与 network-map.png 同一视觉系统", DIM, 20,
            tag="sub")
    p.label(M + 22, 118, CW - 2 * M - 44, 52,
            "区间数＝相邻站之间的段数；站数＝区间数＋1。"
            "换乘＝改变乘坐线路，第一次上车不计。", FAINT, 20, tag="rule", lines=2)

    y = 184
    for i, r in enumerate(ROUTES):
        y += card_route(p, M + 18, y, CW - 2 * M - 36, i, r) + 14
    footer(p, y)
    return p.xml()


def card_route(p, x, y, w, idx, r):
    body = w - 32
    nrm, acc = r["normal"], r["accessible"]
    chain = "站序：" + " → ".join(nrm["station_names"])
    nl_chain = FIT.lines(chain, 20, body)
    segline = ("线路段：" + "　".join(
        f"{s['line']} {s['stations'][0]}→{s['stations'][-1]}（{s['hops']} 区间）"
        for s in nrm["line_segments"]))
    nl_seg = FIT.lines(segline, 20, body)
    verd = [(f"普通最短：{nrm['edges']} 区间 / {nrm['station_count']} 站 / "
             f"{nrm['interchanges']} 次换乘 / 途经无设施站 "
             f"{('、'.join(nrm['passes_non_accessible']) or '无')}", DIM)]
    if r["normal_is_accessible"]:
        verd.append(("可作为无障碍旅程：起终点与换乘站均有无障碍设施。"
                     if nrm["interchange_stations"] else
                     "可作为无障碍旅程：全程无需在无设施站换乘。", ACC))
    else:
        verd.append((f"不可作为无障碍旅程：{r['normal_block_reason']}。", NOACC))
        verd.append((f"另求最短无障碍旅程：{acc['edges']} 区间 / "
                     f"{acc['station_count']} 站 / {acc['interchanges']} 次换乘"
                     f"（换乘 {'、'.join(acc['interchange_stations'])}）", INK))
        acc_chain = "站序：" + " → ".join(acc["station_names"])
        verd.append((acc_chain, DIM))
    if len(r["same_edge_alternatives"]) > 1:
        verd.append((f"同为 {nrm['edges']} 区间的解共 "
                     f"{len(r['same_edge_alternatives'])} 条，已取换乘更少者。", FAINT))
    nl_v = [FIT.lines(t, 20, body) for t, _ in verd]
    h = 44 + nl_seg * 29 + 6 + nl_chain * 29 + 8 + sum(n * 29 for n in nl_v) + 16
    p.rect(x, y, w, h, PANEL, 14, f"1 SOLID {PANEL_LINE}")
    p.chip(x + 16, y + 12, 30, 30, "①②③"[idx], "#0B1220", "#E2E8F0", size=20,
           radius=15)
    p.label(x + 56, y + 10, w - 72, 34,
            f"{r['from']} {NAME[r['from']]} → {r['to']} {NAME[r['to']]}", INK, 24,
            "BOLD", tag=f"c{idx}.head")
    yy = y + 44
    p.label(x + 16, yy, body, nl_seg * 29 + 4, segline, DIM, 20, tag=f"c{idx}.seg",
            lines=nl_seg)
    yy += nl_seg * 29 + 6
    p.label(x + 16, yy, body, nl_chain * 29 + 4, chain, INK, 20,
            tag=f"c{idx}.chain", lines=nl_chain)
    yy += nl_chain * 29 + 8
    for (t, col), n in zip(verd, nl_v):
        p.label(x + 16, yy, body, n * 29 + 4, t, col, 20, tag=f"c{idx}.v", lines=n)
        yy += n * 29
    if yy > y + h - 4:
        FIT.problems.append(f"c{idx} body overflow {yy:.0f} > {y + h - 4}")
    return h


def footer(p, y):
    h = CH - M - 16 - y
    if h < 90:
        FIT.problems.append(f"card overflow: footer height {h}")
        return
    p.rect(M + 18, y, CW - 2 * M - 36, h, PANEL, 14, f"1 SOLID {PANEL_LINE}")
    yy = y + 14
    notes = [
        "缺设施站（S03、S05、S09、S14）可乘车通过，但不能作无障碍旅程的起终点或换乘站。",
        "站序、区间数与换乘次数和 routes.json 同源于同一次计算。",
    ]
    for i, t in enumerate(notes):
        nl = FIT.lines(t, 20, CW - 2 * M - 72)
        p.label(M + 36, yy, CW - 2 * M - 72, nl * 29 + 4, t, FAINT, 20,
                tag=f"foot{i}", lines=nl)
        yy += nl * 29 + 8
    if yy > y + h - 4:
        FIT.problems.append(f"footer overflow {yy:.0f} > {y + h - 4}")


# ---- main -------------------------------------------------------------------
def main():
    TEMP.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    errs = check_layout()
    map_dsl, placed, fails = build_map()
    card_dsl = build_card()
    if fails:
        errs.append("标签无法避让的站点：" + "、".join(fails))
    print(f"fit: {FIT.n} boxes, {len(FIT.problems)} problems")
    for t in FIT.problems[:24]:
        print("  !", t)
    print(f"layout errors: {len(errs)}")
    for t in errs[:24]:
        print("  x", t)
    if FIT.problems or errs:
        return 1
    routes = {
        "schema_version": 1, "path_base": "suite_root", "task_id": TASK, "run_id": RID,
        "source": "tasks/A07-transit-topology/inputs/network.json",
        "definitions": {
            "hop": f"相邻站之间的一条可双向通行区间；图上 {len(HOPS)} 条区间等长 "
                   f"({STEP:.0f}px)，相邻站耗时相同",
            "station_count_vs_edges": "站数 = 区间数 + 1（两者都记录，避免把站数误作区间数）",
            "interchange": "改变乘坐线路；第一次上车不计为换乘",
            "accessible_journey": "起终点与全部换乘站必须 accessible=true；"
                                  "无设施站可乘车通过（passes_non_accessible 列出）",
            "tie_break": "先比区间数，再比换乘次数，仍并列按站序字典序；"
                         "全部同区间数解列在 same_edge_alternatives",
        },
        "network": {
            "stations": [{"id": s, "name": NAME[s], "accessible": ACC_ID[s],
                          "lines": SLINES[s], "interchange": DEG[s] > 1,
                          "query_endpoint_of": QMARK.get(s, []),
                          "position": [round(P[s][0], 2), round(P[s][1], 2)],
                          "label_box": [round(v, 2) for v in placed[s]]}
                         for s in sorted(STATIONS)],
            "lines": [{"id": lid, "name": LNAME[lid], "colour": LCOL[lid],
                       "stations": LINES[lid], "hops": len(LINES[lid]) - 1}
                      for lid in ("R", "B", "G")],
            "hops": [{"line": lid, "from": a, "to": b,
                      "length_px": round(math.dist(P[a], P[b]), 3)}
                     for lid, a, b in HOPS],
            "interchanges": [{"station": s, "name": NAME[s], "lines": SLINES[s],
                              "accessible": ACC_ID[s]}
                             for s in sorted(STATIONS) if DEG[s] > 1],
            "layout_checks": {
                "hop_length_px": STEP, "bend_angles_deg": [45, 90],
                "hop_pairs_tested": len(list(itertools.combinations(HOPS, 2))),
                "crossings_without_station": 0,
                "stations_on_non_incident_hop": 0,
                "note": "check_layout() 在生成 DSL 前逐条断言，任一失败即不出图",
            },
        },
        "queries": [{"index": i + 1, "from": r["from"], "to": r["to"],
                     "from_name": NAME[r["from"]], "to_name": NAME[r["to"]],
                     "normal_shortest": r["normal"],
                     "same_edge_alternatives": r["same_edge_alternatives"],
                     "normal_is_accessible": r["normal_is_accessible"],
                     "normal_block_reason": r["normal_block_reason"],
                     "accessible_shortest": r["accessible"],
                     "accessible_is_same_route": r["accessible_is_same_route"]}
                    for i, r in enumerate(ROUTES)],
    }
    (OUT / "routes.json").write_text(json.dumps(routes, ensure_ascii=False, indent=2),
                                     encoding="utf-8")
    (TEMP / "fit-report.json").write_text(
        json.dumps({"text_items": FIT.n, "problems": FIT.problems,
                    "layout_errors": errs, "label_fallback_used": bool(fails)},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    (TEMP / f"{VERSION}.map.snapshot").write_text(map_dsl, encoding="utf-8")
    (TEMP / f"{VERSION}.card.snapshot").write_text(card_dsl, encoding="utf-8")
    print(f"{VERSION}: map {len(map_dsl)} chars ({map_dsl.count('<Positioned')} pos) / "
          f"card {len(card_dsl)} chars ({card_dsl.count('<Positioned')} pos)")
    for i, r in enumerate(ROUTES):
        print(f"  Q{i + 1} {r['from']}->{r['to']}: edges={r['normal']['edges']} "
              f"changes={r['normal']['interchanges']} "
              f"acc_ok={r['normal_is_accessible']} "
              f"alt={'yes' if not r['accessible_is_same_route'] else 'no'} "
              f"ties={len(r['same_edge_alternatives'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
