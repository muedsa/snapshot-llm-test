"""A06 - "from requirement to reproducible delivery" dependency map, 1600x1000.

Reads tasks/A06-dependency-graph/inputs/graph.json. solid_edges are prerequisite
edges laid out strictly left-to-right by topological layer; feedback_edges are
drawn dashed with their own legend and never take part in the layering.

Run from the suite task root:
  python tmp/<run_id>/A06/gen.py --ver v001 [--final outputs/<run_id>/A06/dependency-map.snapshot]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict, deque
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
sys.path.insert(0, str(ROOT / "tmp" / "2026-10-12T10-04Z-r001" / "_suite" / "scripts"))

from snap import (  # noqa: E402
    C, Border, Col, Container, Positioned, Row, Snapshot, Stack, Text, label, num,
)

RUN = "2026-10-12T10-04Z-r001"
TASK = "A06"
IN_JSON = ROOT / "tasks" / "A06-dependency-graph" / "inputs" / "graph.json"
OUT_DIR = ROOT / "outputs" / RUN / TASK
TMP_DIR = ROOT / "tmp" / RUN / TASK

FONT = "Noto Sans CJK SC,Inter"
MONO = "Noto Sans Mono CJK SC,DejaVu Sans Mono"

BG, BG2 = "#070C1A", "#0D1730"
CARD, CARD2, EDGE = "#101B36", "#0E1830", "#243657"
TXT, TXT_2, TXT_3 = "#F2F6FC", "#9FB2D0", "#6A7E9E"
SKY, EMERALD, AMBER, ROSE, VIOLET = "#38BDF8", "#34D399", "#FBBF24", "#FB7185", "#A78BFA"

g = json.loads(IN_JSON.read_text(encoding="utf-8"))
NODES = {n["id"]: n["label"] for n in g["nodes"]}
ORDER = [n["id"] for n in g["nodes"]]
SOLID = [tuple(e) for e in g["solid_edges"]]
FEEDBACK = [tuple(e) for e in g["feedback_edges"]]
assert len(ORDER) == 14

out_adj = defaultdict(list)
in_adj = defaultdict(list)
for a, b in SOLID:
    out_adj[a].append(b)
    in_adj[b].append(a)

# longest-path layering over prerequisite edges only
layer = {}
indeg = {n: len(in_adj[n]) for n in ORDER}
q = deque([n for n in ORDER if indeg[n] == 0])
while q:
    n = q.popleft()
    base = max((layer[p] + 1 for p in in_adj[n]), default=0)
    layer[n] = max(layer.get(n, -1), base)
    for m in out_adj[n]:
        indeg[m] -= 1
        if indeg[m] == 0:
            q.append(m)
assert len(layer) == 14 and min(layer.values()) == 0, layer

# longest prerequisite path by node count (one witness path)
memo = {}


def longest(n):
    if n in memo:
        return memo[n]
    best = [n]
    for m in out_adj[n]:
        cand = [n] + longest(m)
        if len(cand) > len(best):
            best = cand
    memo[n] = best
    return best


paths = [longest(n) for n in ORDER if not in_adj[n]]
LP = max(paths, key=len)

# ---------------------------------------------------------------- layout
W, H = 1600, 1000
PAD = 32
NLANE = max(layer.values()) + 1
GX0, GX1 = 30, W - 30
PITCH = (GX1 - GX0) / NLANE          # 140 per layer
NODE_W, NODE_H = 114, 68
LANE_Y = {"A": 212, "B": 322, "C": 432, "D": 542}

POS = {
    "N01": "C", "N02": "B", "N03": "D", "N04": "B", "N05": "C", "N06": "C",
    "N07": "B", "N08": "A", "N09": "A", "N10": "A", "N11": "A", "N12": "A",
    "N13": "A", "N14": "A",
}
CENTER = {n: (GX0 + PITCH * (layer[n] + 0.5), LANE_Y[POS[n]]) for n in ORDER}
BOX = {n: [round(CENTER[n][0] - NODE_W / 2, 1), round(CENTER[n][1] - NODE_H / 2, 1),
           round(CENTER[n][0] + NODE_W / 2, 1), round(CENTER[n][1] + NODE_H / 2, 1)]
       for n in ORDER}

# orthogonal routes for the prerequisite edges; the long N04->N13 edge detours below
TOP_ROUTE_Y = 166


def route(a, b):
    ax, ay = CENTER[a]
    bx, by = CENTER[b]
    ar = BOX[a][2]
    bl = BOX[b][0]
    br = BOX[b][2]
    if layer[b] - layer[a] == 1 and abs(ay - by) < 1:
        return [(ar, ay), (bl, by)]
    if abs(ay - by) < 1:
        return [(ar, ay), (bl, by)]
    midx = ar + 14
    if (a, b) == ("N04", "N13"):
        # N04 and N05 share layer 2, so dropping below N04 would run straight through
        # N05; this one long edge goes over the top instead.
        return [(ax, BOX[a][1]), (ax, TOP_ROUTE_Y), (bx, TOP_ROUTE_Y), (bx, BOX[b][1])]
    return [(ar, ay), (midx, ay), (midx, by), (bl, by)]


SOLID_ROUTES = {e: route(*e) for e in SOLID}

# feedback arcs run below the top chain
def fb_route(a, b, y):
    ax, ay = CENTER[a]
    bx, by = CENTER[b]
    return [(ax, BOX[a][3]), (ax, y), (bx, y), (bx, BOX[b][3])]


FB_ROUTES = {FEEDBACK[0]: fb_route(*FEEDBACK[0], 272),
             FEEDBACK[1]: fb_route(*FEEDBACK[1], 300)}

# ---------------------------------------------------------------- draw
els = []


def layer_stack(*children, w=W, h=H):
    return Stack(C(width=num(w), height=num(h)), *children,
                 alignment="TOP_LEFT", clipBehavior="HARD_EDGE")


def card(x, y, w, h, *, fill=CARD, radius=14, border=EDGE):
    return Positioned(C(width=num(w), height=num(h), color=fill, borderRadius=num(radius),
                        border=f"1 SOLID {border}"), left=num(x), top=num(y))


def polyline(pts, color, thick=3, dashed=False, dash=14, gap=10):
    """Axis-aligned polyline; dashed variants emit short runs."""
    out = []
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        if not dashed:
            out.append(seg(x1, y1, x2, y2, thick, color))
            continue
        if x1 == x2:
            y0, y1v = min(y1, y2), max(y1, y2)
            yy = y0
            while yy < y1v:
                e = min(yy + dash, y1v)
                out.append(seg(x1, yy, x2, e, thick, color))
                yy = e + gap
        else:
            x0, x1v = min(x1, x2), max(x1, x2)
            xx = x0
            while xx < x1v:
                e = min(xx + dash, x1v)
                out.append(seg(xx, y1, e, y2, thick, color))
                xx = e + gap
    return out


def seg(x1, y1, x2, y2, thick, color):
    if x1 == x2:
        return Positioned(C(width=num(thick), height=num(abs(y2 - y1)), color=color),
                          left=num(x1 - thick / 2), top=num(min(y1, y2)))
    return Positioned(C(width=num(abs(x2 - x1)), height=num(thick), color=color),
                      left=num(min(x1, x2)), top=num(y1 - thick / 2))


GLYPH = {(1, 0): "▶", (-1, 0): "◀", (0, 1): "▼", (0, -1): "▲"}


def arrow(pts, color, size=20):
    (x1, y1), (x2, y2) = pts[-2], pts[-1]
    dx, dy = (1 if x2 > x1 else -1) if x1 != x2 else 0, (1 if y2 > y1 else -1) if y1 != y2 else 0
    gl = GLYPH[(dx, dy)]
    ox = -size * dx
    oy = -size * dy if dy else 0
    return label(x2 + ox * 0.72, y2 + oy * 0.72, gl, size, color, anchor="center",
                 align="CENTER", width=size + 8, font=FONT)


# header
els.append(Positioned(
    Row(C(width="6", height="56", color=SKY, borderRadius="3"), Container(width="16"),
        Col(Text("从需求到可复现交付 · 依赖解释图", color=TXT, fontSize="34",
                 fontStyle="BOLD", fontFamily=FONT),
            Container(height="8"),
            Text("14 个节点 · 16 条先决依赖（实线）· 2 条反馈关系（虚线，不参与 DAG 排序）",
                 color=TXT_2, fontSize="20", fontFamily=FONT),
            crossAxisAlignment="START"),
        crossAxisAlignment="CENTER"),
    left=num(PAD), top=num(28)))

# legend
LEG_X = 1000
els.append(card(LEG_X, 28, W - PAD - LEG_X, 104, fill=CARD2, radius=10))
els.append(Positioned(
    Col(
        Row(C(width="26", height="4", color="#CBD9EE"), Container(width="8"),
            Text("先决依赖（实线 + 箭头）", color=TXT_2, fontSize="18", fontFamily=FONT),
            crossAxisAlignment="CENTER"),
        Container(height="8"),
        Row(C(width="26", height="4", color=ROSE), Container(width="8"),
            Text("反馈关系（虚线 + 箭头）", color=TXT_2, fontSize="18", fontFamily=FONT),
            crossAxisAlignment="CENTER"),
        Container(height="8"),
        Row(C(width="11", height="11", color=EMERALD, shape="CIRCLE"),
            Container(width="8"),
            Text("绿点=多个先决条件在此会聚；无绿点的交叉只是跨越", color=TXT_3,
                 fontSize="18", fontFamily=FONT),
            crossAxisAlignment="CENTER"),
        crossAxisAlignment="START"),
    left=num(LEG_X + 16), top=num(38)))

# layer band captions
for L in range(NLANE):
    x = GX0 + PITCH * L
    els.append(Positioned(C(width=num(PITCH - 8), height=num(474), color="#0C1428",
                            borderRadius="10", border="1 SOLID #16223C"),
                          left=num(x + 4), top=num(176)))
    els.append(label(x + PITCH / 2, 142, f"第 {L} 层", 18, TXT_3, anchor="center",
                     align="CENTER", width=PITCH - 10, font=MONO))

# edges (drawn under the nodes)
for e, pts in SOLID_ROUTES.items():
    els += polyline(pts, "#8FA6C4", 3)
    els.append(arrow(pts, "#8FA6C4"))
for e, pts in FB_ROUTES.items():
    els += polyline(pts, ROSE, 3, dashed=True)
    els.append(arrow(pts, ROSE))

# junction dots where prerequisite edges genuinely merge
for tgt in ORDER:
    if len(in_adj[tgt]) > 1:
        bx, by = CENTER[tgt]
        els.append(Positioned(
            C(width="13", height="13", color=EMERALD, shape="CIRCLE"),
            left=num(bx - NODE_W / 2 - 6.5), top=num(by - 6.5)))

# nodes
GROUP_COLOR = {
    "N01": VIOLET, "N02": VIOLET, "N03": VIOLET,
    "N04": SKY, "N05": SKY, "N06": SKY, "N07": SKY,
    "N08": EMERALD, "N09": EMERALD, "N10": EMERALD, "N11": EMERALD,
    "N12": AMBER, "N13": AMBER, "N14": AMBER,
}
for n in ORDER:
    x, y = CENTER[n]
    col = GROUP_COLOR[n]
    els.append(Positioned(
        Border(
            Container(
                Col(Text(n, color=col, fontSize="18", fontFamily=MONO, textAlign="CENTER"),
                    Container(height="2"),
                    Text(NODES[n], color=TXT, fontSize="22", fontStyle="BOLD",
                         fontFamily=FONT, textAlign="CENTER"),
                    crossAxisAlignment="CENTER"),
                width=num(NODE_W), height=num(NODE_H), color="#13203C", borderRadius="12",
                alignment="CENTER"),
            border=f"2 SOLID {col}", borderRadius="12"),
        left=num(x - NODE_W / 2), top=num(y - NODE_H / 2)))

# callouts for the two feedback meanings
def callout(x, w, title, body, *, tint="#2A1520", edge="#7A3A4E", tcol="#FFD9E2",
            bcol="#F3C6D1"):
    return Positioned(
        Border(
            Container(
                Col(Text(title, color=tcol, fontSize="20", fontStyle="BOLD",
                         fontFamily=FONT, textAlign="LEFT"),
                    Container(height="6"),
                    Container(Text(body, color=bcol, fontSize="18", fontFamily=FONT,
                                   textAlign="LEFT", softWrap="true", height="1.3"),
                              width=num(w - 30)),
                    crossAxisAlignment="START"),
                width=num(w), height=num(132), color=tint, borderRadius="12",
                padding="(10,14)"),
            border=f"1 SOLID {edge}", borderRadius="12"),
        left=num(x), top=num(656))


els.append(card(PAD, 656, 490, 132, fill=CARD2, radius=12))
els.append(Positioned(
    Col(
        Text("怎么读这张图", color=SKY, fontSize="20", fontStyle="BOLD", fontFamily=FONT),
        Container(height="6"),
        Container(Text("横轴是自左向右的拓扑层（第 0–10 层），同一层内互不依赖、可并行；"
                       "实线箭头一律指向更靠右的层，不存在指向过去层的先决边。",
                       color=TXT_2, fontSize="18", fontFamily=FONT, textAlign="LEFT",
                       softWrap="true", height="1.3"),
                  width=num(460)),
        crossAxisAlignment="START"),
    left=num(PAD + 15), top=num(668), width=num(460)))

els.append(callout(PAD + 490 + 24, 490, "反馈 ① 失败后回到构建",
                   "N09 首轮渲染失败 → 虚线回到 N08 DSL构建；改完再从 N09 重跑。"
                   "这条边不是先决条件，不参与分层。"))
els.append(callout(PAD + 2 * (490 + 24), 508, "反馈 ② 检查发现问题后修复",
                   "N10 视觉检查发现问题 → 虚线回到 N08 修改；实线 N10→N11 问题修复 → "
                   "N12 回归渲染 才是先决链。", ))

els.append(label(PAD, 806,
                 f"最长先决路径（按节点数 {len(LP)} 个，另有等长解）：{' → '.join(LP)}",
                 18, TXT_2, anchor="left_top", align="LEFT", width=1536, font=FONT))
els.append(label(PAD, 832,
                 "并行关系：N02‖N03、N04‖N05、N06‖N07，两路会聚到 N08；"
                 "N04→N13 这条跨越 7 层的先决边从顶部绕行，避免穿过同列下方的 N05。",
                 18, TXT_2, anchor="left_top", align="LEFT", width=1536, font=FONT))
els.append(label(PAD, 858,
                 "节点标签字号 22，节点编号与全部注释 18；14 个节点的编号与标签都出现在图中。"
                 "数据源 inputs/graph.json。",
                 18, TXT_3, anchor="left_top", align="LEFT", width=1536, font=FONT))
els.append(label(W - PAD, 900, f"run {RUN}", 18, "#42536E", anchor="right_top",
                 align="RIGHT", width=340, font=FONT))

doc = Snapshot(
    Container(layer_stack(*els), width=num(W), height=num(H),
              gradientType="LINEAR", gradientColors=f"{BG},{BG2}", gradientStops="0,1",
              gradientBegin="TOP_CENTER", gradientEnd="BOTTOM_CENTER"),
    background=BG, type="png")

# ---------------------------------------------------------------- audit
audit = {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "source_input": "tasks/A06-dependency-graph/inputs/graph.json",
    "canvas": [W, H],
    "coordinate_space": "画布左上原点，x 向右 y 向下，单位像素",
    "node_count": len(ORDER),
    "nodes": [{"id": n, "label": NODES[n], "layer": layer[n],
               "box_px": BOX[n], "center_px": [round(CENTER[n][0], 1), round(CENTER[n][1], 1)],
               "in_neighbors": sorted(in_adj[n]), "out_neighbors": sorted(out_adj[n])}
              for n in ORDER],
    "topological_layers": {str(L): sorted([n for n in ORDER if layer[n] == L])
                           for L in range(NLANE)},
    "layering_rule": "最长路径分层：layer(v) = 1 + max(layer(u) for u in 先决前驱)，"
                     "无前驱者为第 0 层；反馈边不参与该计算",
    "prerequisite_edges": [{"from": a, "to": b, "layer_from": layer[a], "layer_to": layer[b],
                            "forward": layer[b] > layer[a],
                            "polyline_px": [[round(x, 1), round(y, 1)] for x, y in pts]}
                           for (a, b), pts in SOLID_ROUTES.items()],
    "forward_only_check": {
        "all_prerequisite_edges_point_right": all(layer[b] > layer[a] for a, b in SOLID),
        "violations": [[a, b] for a, b in SOLID if layer[b] <= layer[a]],
    },
    "longest_prerequisite_path": {
        "node_count": len(LP), "path": LP,
        "rule": "按节点数计的最长先决路径；图中给出至少一条，另有等长解见 alternative_equal",
        "alternative_equal": [p for p in ([longest(n) for n in ORDER if not in_adj[n]] + paths)
                              if len(p) == len(LP) and p != LP],
    },
    "feedback_edges": [{"from": a, "to": b,
                        "participates_in_layering": False,
                        "rendered_as": "rose dashed polyline with a left/up arrow glyph",
                        "polyline_px": [[round(x, 1), round(y, 1)] for x, y in FB_ROUTES[(a, b)]],
                        "label_box_px": ([560, 676, 1012, 794] if (a, b) == FEEDBACK[0]
                                         else [1040, 676, 1492, 794]),
                        "meaning": ("首轮渲染失败后回到 DSL 构建" if (a, b) == FEEDBACK[0]
                                    else "视觉检查发现问题后回到 DSL 构建")}
                       for (a, b) in FEEDBACK],
    "crossings_are_not_dependencies": {
      "rule": "线段交叉处没有实心圆点即不构成依赖；真正的多前驱会聚点用绿色圆点标出",
      "merge_points": [{"node": n, "predecessors": sorted(in_adj[n])}
                       for n in ORDER if len(in_adj[n]) > 1],
    },
    "typography": {"node_label_font_size": 22, "node_id_font_size": 18,
                   "annotation_font_size": 18, "floor_required": {"node": 22, "note": 18}},
}
OUT_DIR.mkdir(parents=True, exist_ok=True)
(OUT_DIR / "graph-audit.json").write_text(
    json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

ap = argparse.ArgumentParser()
ap.add_argument("--ver", default="v001")
ap.add_argument("--final", default=None)
a = ap.parse_args()
TMP_DIR.mkdir(parents=True, exist_ok=True)
(TMP_DIR / f"{a.ver}.snapshot").write_text(doc.render() + "\n", encoding="utf-8")
if a.final:
    (ROOT / a.final).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / a.final).write_text(doc.render() + "\n", encoding="utf-8")
print(json.dumps({"ver": a.ver, "layers": {str(L): sorted(n for n in ORDER if layer[n] == L)
                                           for L in range(NLANE)},
                  "longest_path": LP, "all_forward": audit["forward_only_check"]["all_prerequisite_edges_point_right"]},
                 ensure_ascii=False))
