"""A06 - 14-node prerequisite graph with two feedback loops (dependency-map.png).

Vertical (top-down) layered layout: every solid prerequisite edge strictly descends,
so no prerequisite edge can visually point back to an earlier topological layer.
The two feedback edges are drawn dashed in red and routed through side channels.
"""
from __future__ import annotations

import json
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402
import state as S  # noqa: E402

TASK = "A06"
GRAPH_PATH = os.path.join(ROOT, "tasks", "A06-dependency-graph", "inputs", "graph.json")
OUT = os.path.join(S.OUT_ROOT, TASK)
TMP = os.path.join(S.TMP_ROOT, TASK)
snapkit.configure(TASK, OUT, TMP)
S.start_task(TASK)

with open(GRAPH_PATH, encoding="utf-8") as fh:
    G = json.load(fh)
NODES = [(n["id"], n["label"]) for n in G["nodes"]]
LAB = dict(NODES)
SOLID = [tuple(e) for e in G["solid_edges"]]
FEEDBACK = [tuple(e) for e in G["feedback_edges"]]
IDS = [n for n, _ in NODES]

# ---------------------------------------------------------------- graph analysis
out_map = {i: [] for i in IDS}
in_map = {i: [] for i in IDS}
for a, b in SOLID:
    out_map[a].append(b)
    in_map[b].append(a)
fb_out = {i: [] for i in IDS}
fb_in = {i: [] for i in IDS}
for a, b in FEEDBACK:
    fb_out[a].append(b)
    fb_in[b].append(a)

# longest-path layering over solid_edges only (feedback edges excluded by design)
layer = {n: 1 for n in IDS}
converged = False
for _ in range(20):
    changed = False
    for a, b in SOLID:
        cand = layer.get(a, 1) + 1
        if layer.get(b, 0) < cand:
            layer[b] = cand
            changed = True
    if not changed:
        converged = True
        break
assert converged, "layering did not converge: solid graph contains a cycle"
assert set(layer) == set(IDS), "solid graph must be a DAG covering all nodes"
MAXL = max(layer.values())
layer_of = {n: layer[n] for n in IDS}
layers = [[n for n in IDS if layer_of[n] == L] for L in range(1, MAXL + 1)]
assert sorted(sum(layers, [])) == sorted(IDS)
for a, b in SOLID:
    assert layer_of[a] < layer_of[b], "solid edge %s->%s points into an earlier layer" % (a, b)

# real BFS reachability over the solid prerequisite graph
_seen, _queue = set(), [n for n in IDS if not in_map[n]]
while _queue:
    _cur = _queue.pop()
    if _cur in _seen:
        continue
    _seen.add(_cur)
    _queue += out_map[_cur]
REACHABLE = (_seen == set(IDS))
assert REACHABLE, "not every node is reachable over solid_edges"

# longest prerequisite path measured in nodes (all optima enumerated)
memo_len = {}
memo_paths = {}


def lp_from(n):
    if n in memo_len:
        return memo_len[n], memo_paths[n]
    best, bests = 1, [[n]]
    if out_map[n]:
        for m in out_map[n]:
            l2, p2 = lp_from(m)
            if l2 + 1 > best:
                best, bests = l2 + 1, [[n] + p for p in p2]
            elif l2 + 1 == best:
                bests += [[n] + p for p in p2]
    memo_len[n], memo_paths[n] = best, bests
    return best, bests


lp_from(IDS[0])
LP_LEN = memo_len[IDS[0]]
LP_PATHS = memo_paths[IDS[0]]

# ---------------------------------------------------------------- canvas geometry
W, H = 1600, 1000
BG = "#EEF2F7FF"
INK, MUTED, FAINT = "#0F172AFF", "#475569FF", "#94A3B8FF"
EDGE = "#334155FF"
FBC = "#DC2626FF"

HEAD_H = 78
GRAPH_TOP = 88
PITCH = 60
NH = 36
ROW = [GRAPH_TOP + PITCH * i for i in range(11)]
GUT_X, GUT_W = 32, 96
BAND_X, BAND_W = 136, 1212
PANEL_X, PANEL_W = 1360, 212
CH_X, CH_W = GUT_X, GUT_W + BAND_W  # gutter + band block

PHASES = [
    (0, 3, "准备与输入", "#0284C7FF", "#F0F9FFFF"),
    (4, 8, "构建与验证", "#4338CAFF", "#EEF2FFFF"),
    (9, 10, "校验与交付", "#047857FF", "#ECFDF5FF"),
]


def phase_of(row):
    for lo, hi, name, c, tint in PHASES:
        if lo <= row <= hi:
            return name, c, tint
    raise AssertionError


# id -> (x_left, width)
NPOS = {
    "N01": (610, 260), "N02": (350, 240), "N03": (940, 180),
    "N04": (330, 200), "N05": (720, 180), "N06": (1130, 200),
    "N07": (330, 200), "N08": (690, 220), "N09": (700, 200),
    "N10": (700, 200), "N11": (700, 200), "N12": (700, 200),
    "N13": (1130, 200), "N14": (1130, 200),
}


def cx(nid):
    x, w = NPOS[nid]
    return x + w / 2.0


def row_of(nid):
    return layer_of[nid] - 1


def top_of(nid):
    return ROW[row_of(nid)]


def bot_of(nid):
    return ROW[row_of(nid)] + NH


# ---------------------------------------------------------------- primitives
def seg(x0, y0, x1, y1, color=EDGE, w=2, step=4.5):
    """Thick line between two points, emitted as a run of small boxes."""
    dx, dy = x1 - x0, y1 - y0
    n = max(2, int(round(max(abs(dx), abs(dy)) / float(step))))
    out = []
    if abs(dx) >= abs(dy):
        bw = abs(dx) / n * 1.45 + 1.6
        hh = w + abs(dy) / n + 1.2
        for k in range(n):
            t = (k + 0.5) / n
            out.append(D.box(x0 + dx * t - bw / 2.0, y0 + dy * t - hh / 2.0, bw, hh,
                             color=color))
    else:
        bh = abs(dy) / n * 1.45 + 1.6
        ww = w + abs(dx) / n + 1.2
        for k in range(n):
            t = (k + 0.5) / n
            out.append(D.box(x0 + dx * t - ww / 2.0, y0 + dy * t - bh / 2.0, ww, bh,
                             color=color))
    return out


def tri_down(xc, y_tip, hl=11, w=15, color=EDGE, rows=10):
    """Arrowhead pointing DOWN: base (widest) at y_tip-hl, tip at y_tip."""
    out = []
    hh = hl / float(rows)
    for i in range(rows):
        t = (i + 0.5) / rows
        ww = w * (1.0 - t)
        out.append(D.box(xc - ww / 2.0, y_tip - hl + hh * i, ww, hh + 0.8, color=color))
    return out


def tri_right(x_tip, yc, hl=11, w=15, color=EDGE, rows=10):
    """Arrowhead pointing RIGHT: base at x_tip-hl, tip at x_tip."""
    out = []
    ww = hl / float(rows)
    for i in range(rows):
        t = (i + 0.5) / rows
        hh = w * (1.0 - t)
        out.append(D.box(x_tip - hl + ww * i, yc - hh / 2.0, ww + 0.8, hh, color=color))
    return out


def tri_left(x_tip, yc, hl=11, w=15, color=EDGE, rows=10):
    """Arrowhead pointing LEFT: base at x_tip+hl, tip at x_tip."""
    out = []
    ww = hl / float(rows)
    for i in range(rows):
        t = (i + 0.5) / rows
        hh = w * (1.0 - t)
        out.append(D.box(x_tip + hl - ww * (i + 1), yc - hh / 2.0, ww + 0.8, hh,
                         color=color))
    return out


def dot(xc, yc, color, r=3.4):
    return [D.box(xc - r, yc - r, 2 * r, 2 * r, color=color, radius=r)]


def dash_h(x0, x1, y, color=FBC, w=3, dash=11, gap=8):
    out, x, end = [], min(x0, x1), max(x0, x1)
    while x < end:
        out.append(D.box(x, y - w / 2.0, min(dash, end - x), w, color=color))
        x += dash + gap
    return out


def dash_v(y0, y1, x, color=FBC, w=3, dash=11, gap=8):
    out, y, end = [], min(y0, y1), max(y0, y1)
    while y < end:
        out.append(D.box(x - w / 2.0, y, w, min(dash, end - y), color=color))
        y += dash + gap
    return out


def path(points, color=EDGE, w=2, step=4.5):
    out = []
    for i in range(len(points) - 1):
        (x0, y0), (x1, y1) = points[i], points[i + 1]
        out += seg(x0, y0, x1, y1, color=color, w=w, step=step)
    return out


def dash_path(points, color=FBC, w=3, dash=11, gap=8):
    out = []
    for i in range(len(points) - 1):
        (x0, y0), (x1, y1) = points[i], points[i + 1]
        if abs(y1 - y0) < 0.01:
            out += dash_h(x0, x1, y0, color, w, dash, gap)
        elif abs(x1 - x0) < 0.01:
            out += dash_v(y0, y1, x0, color, w, dash, gap)
        else:
            out += seg(x0, y0, x1, y1, color=color, w=w, step=4.5)
        out.append(D.box(x1 - w / 2.0, y1 - w / 2.0, w, w, color=color))
    return out


# ---------------------------------------------------------------- edge routes
# solid: (exit point on source border, list of waypoints, arrow target point)
SOLID_ROUTES = {
    ("N01", "N02"): [(660, 124), (470, 137), (470, 148)],
    ("N01", "N03"): [(820, 124), (1030, 137), (1030, 148)],
    ("N02", "N04"): [(430, 184), (430, 208)],
    ("N02", "N05"): [(540, 184), (810, 197), (810, 208)],
    ("N03", "N06"): [(1030, 184), (1260, 257), (1260, 268)],
    ("N05", "N06"): [(810, 244), (1150, 257), (1150, 268)],
    ("N04", "N07"): [(430, 244), (430, 268)],
    ("N06", "N08"): [(1230, 304), (850, 317), (850, 328)],
    ("N07", "N08"): [(430, 304), (750, 317), (750, 328)],
    ("N08", "N09"): [(800, 364), (800, 388)],
    ("N09", "N10"): [(800, 424), (800, 448)],
    ("N10", "N11"): [(800, 484), (800, 508)],
    ("N11", "N12"): [(800, 544), (800, 568)],
    ("N12", "N13"): [(800, 604), (1230, 617), (1230, 628)],
    ("N13", "N14"): [(1230, 664), (1230, 688)],
    ("N04", "N13"): [(330, 226), (160, 226), (160, 646), (1130, 646)],
}
# F1 takes the right-hand channel, F2 the left-hand one, so the two return paths
# never have to cross each other or the solid flow.
FEEDBACK_ROUTES = {
    ("N09", "N08"): [(900, 400), (950, 400), (950, 340), (910, 340)],
    ("N10", "N08"): [(700, 472), (560, 472), (560, 350), (690, 350)],
}
FEEDBACK_META = {
    ("N09", "N08"): dict(
        fid="F1", meaning="失败后回到构建",
        note="首轮渲染失败，路径沿虚线回到 DSL 构建重做",
        badge=(1000, 366), leader=[(996, 379), (946, 379)],
        badge_w=200, badge_txt="F1 · 失败后回到构建"),
    ("N10", "N08"): dict(
        fid="F2", meaning="检查发现问题后修复",
        note="视觉检查判定不合格，回到 DSL 构建重做",
        badge=(214, 428), leader=[(452, 441), (556, 441)],
        badge_w=232, badge_txt="F2 · 检查发现问题后修复"),
}

# ---------------------------------------------------------------- DSL assembly
kids = []

# --- header
kids += [
    D.box(0, 0, W, HEAD_H, color="#0F172AFF"),
    D.text_el("从需求到可复现交付 · 十四节点依赖图与反馈回路",
              x=32, y=12, w=860, h=44, size=30, style="BOLD", color="#F8FAFCFF"),
    D.text_el("数据：inputs/graph.json · 14 节点 / 16 条先决依赖 / 2 条反馈 · 拓扑 11 层 "
              "· 最长先决路径 11 个节点",
              x=32, y=48, w=980, h=26, size=18, color="#93A4BAFF"),
    D.text_el("实线＝有向先决依赖　虚线＝反馈回路　箭头＝依赖方向",
              x=1040, y=48, w=528, h=26, size=18, color="#7DD3FCFF", align="RIGHT"),
]

# --- graph field + layer bands + gutter
kids.append(D.box(0, HEAD_H, W, 654, color="#F8FAFCFF"))
kids.append(D.box(GUT_X, GRAPH_TOP, GUT_W, 636,
                  color="#E2E8F0FF", radius=8))
for i in range(11):
    rt = ROW[i]
    _pname, pc, ptint = phase_of(i)
    kids.append(D.box(BAND_X, rt, BAND_W, NH,
                      color="#FFFFFFFF" if i % 2 == 0 else "#F1F5F9FF", radius=8))
    if i:
        kids.append(D.hline(BAND_X, BAND_X + BAND_W, rt - (PITCH - NH) / 2.0,
                            "#E8EDF3FF", 1))
    kids.append(D.text_el("L%d" % (i + 1), x=48, y=rt + 6, w=64, h=26, size=18,
                          style="BOLD", color=pc))

# --- prerequisite edges (drawn under the nodes)
for (a, b), pts in SOLID_ROUTES.items():
    kids += path(pts, color=EDGE, w=2, step=4.5)
    kids += dot(pts[0][0], pts[0][1], EDGE)
    tx, ty = pts[-1]
    if abs(tx - pts[-2][0]) < 0.01 and abs(ty - pts[-2][1]) > 4:
        kids += tri_down(tx, ty, color=EDGE)
    elif abs(ty - pts[-2][1]) < 0.01:
        kids += tri_right(tx, ty, color=EDGE)

# --- feedback edges (dashed, side channels) drawn under the nodes
for (a, b), pts in FEEDBACK_ROUTES.items():
    kids += dash_path(pts, color=FBC, w=3, dash=11, gap=8)
    kids += dot(pts[0][0], pts[0][1], FBC, r=4)
    tx, ty = pts[-1]
    if tx < pts[-2][0]:
        kids += tri_left(tx, ty, color=FBC, hl=10, w=13)
    else:
        kids += tri_right(tx, ty, color=FBC, hl=10, w=13)

# --- feedback edge labels with leader lines
for key, meta in FEEDBACK_META.items():
    bx, by = meta["badge"]
    kids += seg(meta["leader"][0][0], meta["leader"][0][1],
                meta["leader"][1][0], meta["leader"][1][1], color=FBC, w=1.6, step=5)
    kids.append(D.box(bx, by, meta["badge_w"], 26, color="#FEF2F2FF", radius=13,
                      border="1 SOLID #FECACAFF"))
    kids.append(D.text_el(meta["badge_txt"], x=bx + 12, y=by + 3, w=meta["badge_w"] - 20,
                          h=24, size=18, style="BOLD", color="#B91C1CFF"))
kids.append(D.text_el("直接校验：数据不经过渲染回路", x=234, y=470, w=310, h=26, size=18,
                      style="BOLD", color="#475569FF"))
kids += seg(226, 483, 163, 483, color="#64748BFF", w=1.6, step=5)

# --- nodes on top
for nid, label in NODES:
    nx, nw = NPOS[nid]
    rt = top_of(nid)
    _pname, pc, ptint = phase_of(row_of(nid))
    kids.append(D.box(nx, rt, nw, NH, color=ptint, radius=10,
                      border="2 SOLID " + pc, shadow="0 1 4 0 #0F172A12"))
    kids.append(D.box(nx + 11, rt + 5, 5, NH - 10, color=pc, radius=3))
    kids.append(D.text_el("%s %s" % (nid, label), x=nx + 24, y=rt + 3, w=nw - 34,
                          h=30, size=22, style="BOLD", color=INK))

# --- right-hand topological layer panel
PT, PW = 96, PANEL_W
PT_H = 384
kids.append(D.card(PANEL_X, PT, PW, PT_H, "#FFFFFFFF", 12, "1 SOLID #E2E8F0FF",
                   "0 2 8 0 #0F172A0F"))
kids += [
    D.text_el("拓扑分层", x=PANEL_X + 14, y=PT + 12, w=PW - 28, h=28, size=20,
              style="BOLD", color=INK),
    D.text_el("仅按先决依赖排序", x=PANEL_X + 14, y=PT + 40, w=PW - 28, h=24, size=18,
              color=MUTED),
    D.hline(PANEL_X + 12, PANEL_X + PW - 12, PT + 70, "#E2E8F0FF", 1.5),
]
for L in range(1, MAXL + 1):
    members = layers[L - 1]
    txt = "L%-2d  %s" % (L, " ".join(members))
    ry = PT + 80 + (L - 1) * 21
    _pname, pc, _pt = phase_of(L - 1)
    kids += [
        D.text_el(txt, x=PANEL_X + 14, y=ry, w=PW - 28, h=22, size=18,
                  style=("BOLD" if len(members) > 1 else "NORMAL"), color=INK),
        D.text_el("×%d" % len(members), x=PANEL_X + PW - 46, y=ry, w=34, h=22,
                  size=18, style="BOLD", color=(pc if len(members) > 1 else FAINT),
                  align="RIGHT"),
    ]
kids += [
    D.hline(PANEL_X + 12, PANEL_X + PW - 12, PT + 322, "#E2E8F0FF", 1.5),
    D.text_el("最长先决路径", x=PANEL_X + 14, y=PT + 330, w=PW - 28, h=24, size=18,
              style="BOLD", color=INK),
    D.text_el("%d 节点 / %d 边" % (LP_LEN, LP_LEN - 1), x=PANEL_X + 14, y=PT + 352,
              w=PW - 28, h=24, size=18, color="#B45309FF"),
]

# ---------------------------------------------------------------- footer
LEG_Y1 = 738
LEG_Y2 = 766
kids.append(D.hline(32, W - 32, LEG_Y1 - 12, "#CBD5E1FF", 1.5))
legend_rows = [
    (LEG_Y1, [("solid", "实线＝有向先决依赖（严格向下）"),
              ("dash", "虚线＝反馈回路（不参与 DAG 排序）"),
              ("arrow", "箭头＝依赖方向")]),
    (LEG_Y2, [("dot", "圆点＝边的起点端点"),
              ("cross", "交叉线无连接点，不构成新的依赖"),
              ("par", "同层节点并行、互不依赖")]),
]
LEG_W = 0
for ly, items in legend_rows:
    lx = 32
    for kind, label in items:
        tw = D.est_width(label, 18)
        if kind == "solid":
            kids.append(D.box(lx, ly + 10, 36, 3, color=EDGE))
        elif kind == "dash":
            kids += dash_h(lx, lx + 36, ly + 11.5, color=FBC, w=3, dash=9, gap=6)
        elif kind == "arrow":
            kids += seg(lx, ly + 11, lx + 20, ly + 11, color=EDGE, w=2, step=5)
            kids += tri_down(lx + 30, ly + 18, hl=8, w=11, color=EDGE, rows=8)
        elif kind == "dot":
            kids.append(D.box(lx + 1, ly + 6, 10, 10, color=EDGE, radius=5))
        elif kind == "cross":
            kids.append(D.box(lx, ly + 8, 36, 7, color="#F1F5F9FF"))
            kids.append(D.box(lx, ly + 8, 13, 7, color=EDGE))
            kids.append(D.box(lx + 23, ly + 8, 13, 7, color=EDGE))
        elif kind == "par":
            kids.append(D.box(lx, ly + 8, 14, 7, color="#0284C7FF", radius=3))
            kids.append(D.box(lx + 22, ly + 8, 14, 7, color="#0284C7FF", radius=3))
        kids.append(D.text_el(label, x=lx + 46, y=ly, w=tw + 16, h=24, size=18,
                              color=INK))
        lx += 46 + tw + 30
    LEG_W = max(LEG_W, lx - 32)

CARD_Y, CARD_H = 794, 146
CARDS = [
    (32, 752, "① 失败后回到构建（F1：N09 → N08）", "#B91C1CFF",
     ["首轮渲染 N09 失败时，路径沿虚线回到 DSL 构建 N08 重新出图，不产生新节点。",
      "虚线只表示返工路径，不参与 DAG 拓扑排序，因此先决层号不会因它回退。",
      "图中位置：N09 右侧出线，右折至 x=950，上行，右折箭头从 N08 右侧进入。"]),
    (816, 752, "② 检查发现问题后修复（F2：N10 → N08）", "#B91C1CFF",
     ["视觉检查 N10 判定首轮图不合格，沿虚线回到 N08 重建，再走 N11 问题修复。",
      "N10 → N11 → N12 是实线先决依赖；N10 → N08 是虚线反馈，图中分别绘制。",
      "图中位置：N10 左侧出线，左折至 x=560，上行两级，右折箭头进入 N08 左侧。"]),
]
for cx0, cw0, title, tcol, lines in CARDS:
    kids.append(D.card(cx0, CARD_Y, cw0, CARD_H, "#FFFFFFFF", 12, "1 SOLID #E2E8F0FF",
                       "0 2 8 0 #0F172A0F"))
    kids.append(D.box(cx0, CARD_Y, 5, CARD_H, color=tcol, radius=3))
    kids.append(D.text_el(title, x=cx0 + 20, y=CARD_Y + 10, w=cw0 - 40, h=32, size=22,
                          style="BOLD", color=INK))
    kids.append(D.hline(cx0 + 20, cx0 + cw0 - 20, CARD_Y + 46, "#E2E8F0FF", 1.5))
    for k, ln in enumerate(lines):
        kids.append(D.text_el(ln, x=cx0 + 20, y=CARD_Y + 56 + k * 28, w=cw0 - 40,
                              h=26, size=18, color=(MUTED if k == 2 else INK)))

FOOT = [
    "先决边 16 条全部严格向下，无一条指向更早的拓扑层；反馈边 2 条均向上返回构建，不参与排序。",
    "同源/同汇的边已分端口出线，图中无几何交叉；N04→N13 经左侧边距通道 x=160 绕行，不压节点文字。",
]
for k, ln in enumerate(FOOT):
    kids.append(D.text_el(ln, x=32, y=948 + k * 24, w=W - 64, h=26, size=18,
                          color="#64748BFF"))

dsl = D.snapshot([D.stack(kids, W, H)], W, H, bg=BG)
with open(os.path.join(TMP, "build-a06.snapshot"), "w", encoding="utf-8",
          newline="\n") as fh:
    fh.write(dsl)
r = snapkit.render(dsl, "dependency-map.png", "dependency-map.snapshot", final=True)
print("render ok=%s status=%s bytes=%s dsl_bytes=%s elements=%d" % (
    r.get("ok"), r.get("status"), r.get("bytes"), len(dsl.encode("utf-8")),
    dsl.count("<Positioned")))
if not r.get("ok"):
    print(r.get("error"))
for wn in D.warnings():
    print("WARN", wn)
print("legend width used = %d (avail %d)" % (LEG_W, W - 64))

# ---------------------------------------------------------------- graph-audit.json
audit = {
    "task": TASK,
    "title": "十四节点依赖图与反馈回路",
    "source_input": "tasks/A06-dependency-graph/inputs/graph.json",
    "canvas": {"png": "dependency-map.png", "width": W, "height": H,
               "dsl": "dependency-map.snapshot"},
    "counts": {"nodes": len(NODES), "solid_prerequisite_edges": len(SOLID),
               "feedback_edges": len(FEEDBACK), "topological_layers": MAXL,
               "total_drawn_edges": len(SOLID) + len(FEEDBACK),
               "drawn_arrowheads": len(SOLID) + len(FEEDBACK),
               "edge_source_dots": len(SOLID) + len(FEEDBACK)},
    "node_positions": {
        nid: {"label": LAB[nid], "topological_layer": layer_of[nid],
              "row_index_0based": row_of(nid), "phase": phase_of(row_of(nid))[0],
              "box_left_px": NPOS[nid][0], "box_width_px": NPOS[nid][1],
              "box_top_px": top_of(nid), "box_bottom_px": bot_of(nid),
              "box_center_x_px": round(cx(nid), 1),
              "box_center_y_px": round(top_of(nid) + NH / 2.0, 1)}
        for nid, _ in NODES},
    "topological_layers": {
        "method": "longest-path layering computed over solid_edges only; "
                  "feedback_edges are excluded from the ordering by definition",
        "layer_index_base": 1,
        "layer_count": MAXL,
        "layers": [{"layer": L, "nodes": layers[L - 1],
                    "labels": [LAB[n] for n in layers[L - 1]],
                    "parallel_size": len(layers[L - 1])}
                   for L in range(1, MAXL + 1)],
        "layer_of_node": layer_of,
        "parallel_layers": [{"layer": L, "nodes": layers[L - 1],
                             "note": "nodes in the same layer have no prerequisite "
                                     "relation between them"}
                            for L in range(1, MAXL + 1) if len(layers[L - 1]) > 1],
    },
    "node_neighbors": {
        nid: {
            "prerequisite_in": in_map[nid],
            "prerequisite_out": out_map[nid],
            "feedback_in": fb_in[nid],
            "feedback_out": fb_out[nid],
            "prerequisite_in_degree": len(in_map[nid]),
            "prerequisite_out_degree": len(out_map[nid]),
            "layer": layer_of[nid],
        } for nid, _ in NODES},
    "longest_prerequisite_path": {
        "measured_in": "nodes",
        "node_count": LP_LEN,
        "edge_count": LP_LEN - 1,
        "multiple_solutions_exist": len(LP_PATHS) > 1,
        "solution_count_enumerated": len(LP_PATHS),
        "paths_node_ids": LP_PATHS,
        "paths_labels": [" → ".join("%s %s" % (n, LAB[n]) for n in p)
                         for p in LP_PATHS],
        "note": "至少给出一条即可；此处把全部 %d 条等长最长路径都列出以便核对。" % len(LP_PATHS),
    },
    "feedback_edges": [
        {
            "id": FEEDBACK_META[(a, b)]["fid"],
            "from": a, "from_label": LAB[a], "from_layer": layer_of[a],
            "to": b, "to_label": LAB[b], "to_layer": layer_of[b],
            "style": "dashed",
            "stroke_color": "#DC2626FF",
            "counted_in_dag_sort": False,
            "excluded_from_topological_layers": True,
            "meaning": FEEDBACK_META[(a, b)]["meaning"],
            "explanation": FEEDBACK_META[(a, b)]["note"],
            "image_representation": {
                "canvas": [W, H],
                "polyline_points_px": FEEDBACK_ROUTES[(a, b)],
                "start_point_on_source_border": FEEDBACK_ROUTES[(a, b)][0],
                "arrow_tip_px": FEEDBACK_ROUTES[(a, b)][-1],
                "arrow_direction": (
                    "right-then-up-then-left; tip points left into the right border of %s"
                    % b if FEEDBACK_ROUTES[(a, b)][-1][0]
                    < FEEDBACK_ROUTES[(a, b)][-2][0] else
                    "left-then-up-then-right; tip points right into the left border of %s"
                    % b),
                "side_channel_x_px": FEEDBACK_ROUTES[(a, b)][-2][0],
                "routed_beside_the_main_flow": True,
                "source_dot_px": FEEDBACK_META[(a, b)]["badge"],
                "inline_label_bbox_px": [
                    FEEDBACK_META[(a, b)]["badge"][0],
                    FEEDBACK_META[(a, b)]["badge"][1],
                    FEEDBACK_META[(a, b)]["badge_w"], 26],
                "leader_line_px": FEEDBACK_META[(a, b)]["leader"],
                "explanation_card_in_footer": "left card" if a == "N09" else "right card",
            },
        } for a, b in FEEDBACK],
    "solid_edge_representation": {
        "note": "16 条先决边全部自上而下，箭头落在目标节点上边框；源端画实心圆点标出真实端点。",
        "routes_px": {"%s->%s" % k: v for k, v in SOLID_ROUTES.items()},
        "long_span_edge": {
            "id": "N04->N13",
            "why": "数据计算完成后可以直接做产物校验，不必等渲染回路跑完",
            "detour": "自 N04 左侧出图，绕行左侧边距通道 x=160（整图最左的节点边框在 x=330），"
                      "下行到 L10 行高后右折，从 N13 左侧进入，避免压住任何节点文字",
        },
        "no_backward_layer_edge": all(layer_of[a] < layer_of[b] for a, b in SOLID),
        "geometric_crossings": [],
        "crossing_convention": "本图已把同源/同汇的边分端口出线，几何上无交叉；"
                              "即使出现交叉，交叉处没有连接点即不构成新的依赖。",
    },
    "topology_checks": {
        "solid_graph_is_dag": converged,
        "layering_converged_without_conflict": converged,
        "all_nodes_reachable_from_source": REACHABLE,
        "source_nodes": sorted([n for n in IDS if not in_map[n]]),
        "sink_nodes": sorted([n for n in IDS if not out_map[n]]),
        "nodes_with_no_prerequisite": sorted([n for n in IDS if not in_map[n]]),
        "nodes_with_no_dependent": sorted([n for n in IDS if not out_map[n]]),
        "feedback_targets": sorted({b for _, b in FEEDBACK}),
        "feedback_originates_from": sorted({a for a, _ in FEEDBACK}),
        "every_feedback_edge_goes_back_to_an_earlier_layer": all(
            layer_of[a] > layer_of[b] for a, b in FEEDBACK),
        "feedback_layers_skipped": [{"edge": "%s->%s" % (a, b),
                                     "from_layer": layer_of[a], "to_layer": layer_of[b],
                                     "layers_back": layer_of[a] - layer_of[b]}
                                    for a, b in FEEDBACK],
        "layers_are_consistent_with_every_solid_edge": converged,
        "no_prerequisite_edge_points_into_an_earlier_layer": all(
            layer_of[a] < layer_of[b] for a, b in SOLID),
    },
    "text_rendering_constraints": {
        "min_node_font_size_px": 22,
        "min_annotation_font_size_px": 18,
        "latin_cjk_font_stack": D.UI,
    },
}
with open(os.path.join(OUT, "graph-audit.json"), "w", encoding="utf-8") as fh:
    json.dump(audit, fh, ensure_ascii=False, indent=2)

print("layers:", [" ".join(l) for l in layers])
print("longest path nodes=%d solutions=%d" % (LP_LEN, len(LP_PATHS)))
for p in LP_PATHS:
    print("  ", " -> ".join(p))
print("legend width used = %d" % LEG_W)
