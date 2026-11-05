#!/usr/bin/env python3
"""A06: 14-node layered dependency DAG with two explicit feedback loops."""
import json, os, sys
TOOLS = os.environ["TOOLS"]; sys.path.insert(0, TOOLS)
from dsl import Canvas, LATIN
import suite

T = "A06"
G = json.loads((suite.ROOT / "tasks/A06-dependency-graph/inputs/graph.json").read_text(encoding="utf-8"))
nodes = {n["id"]: n["label"] for n in G["nodes"]}
solid = [tuple(e) for e in G["solid_edges"]]
feedback = [tuple(e) for e in G["feedback_edges"]]
ins = {k: [] for k in nodes}; outs = {k: [] for k in nodes}
for a, b in solid: outs[a].append(b); ins[b].append(a)
# longest-path topological layers (feedback edges excluded)
layer = {}
for _ in range(len(nodes)):
    changed = False
    for k in nodes:
        v = 0 if not ins[k] else 1 + max(layer[p] for p in ins[k] if p in layer) if all(p in layer for p in ins[k]) else -1
        if v >= 0 and (k not in layer or v > layer[k]):
            layer[k] = v; changed = True
    if not changed: break
for k in nodes: layer.setdefault(k, 0)
# longest prerequisite path by node count
best = []
def dfs(path):
    global best
    if len(path) > len(best): best = list(path)
    for nxt in outs[path[-1]]:
        dfs(path + [nxt])
for k in nodes:
    if not ins[k]: dfs([k])

NW, NH = 118, 58
LX = lambda l: 48 + l * 138
CENTER = {0: 485, 1: 330, 2: 640}
pos = {}
by_layer = {}
for k, l in layer.items(): by_layer.setdefault(l, []).append(k)
for l, ks in by_layer.items():
    ks.sort()
    for i, k in enumerate(ks):
        cy = CENTER[i] if len(ks) > 1 else 485
        pos[k] = (LX(l), cy - NH / 2, cy)

INK, MUTED, LINE, WHITE, BG = "#0F172A", "#5B6B85", "#DDE5F0", "#FFFFFF", "#F4F7FC"
SOLID = "#2563EB"; FEED = "#DB2777"; NODE = "#FFFFFF"

c = Canvas(1600, 1000, BG)
c.gradient(0, 0, 1600, 100, ["#0B1B35", "#16386F"], begin="CENTER_LEFT", end="CENTER_RIGHT")
c.text(48, 14, 1000, 44, "从需求到可复现交付 · 依赖解释图", 34, WHITE, bold=True)
c.text(48, 62, 1050, 28, "14 节点 · 16 条先决依赖 · 2 条反馈关系（虚线，不参与 DAG 排序）", 20, "#BBD3F2")
# legend
c.line(1100, 44, 1150, 44, 3, SOLID); c.arrow_head(1150, 44, 0, 10, SOLID)
c.text(1158, 32, 200, 26, "先决依赖", 18, "#E8F0FC")
c.dashed_line(1100, 76, 1150, 76, 3, "#F9A8D4", dash=8, gap=5)
c.text(1158, 64, 240, 26, "反馈边（洋红虚线）", 18, "#F9A8D4")
# layer captions
for l in sorted(by_layer):
    c.text(LX(l), 122, NW, 26, "L%d" % l, 18, MUTED, align="CENTER", font=LATIN)
c.text(48, 150, 700, 26, "左 → 右为先后；同层上下为可并行的节点", 18, MUTED)

edge_records = []
for a, b in solid:
    ax, ay, acy = pos[a]; bx, by, bcy = pos[b]
    if a == "N04" and b == "N13":
        # long-range prerequisite bypasses every intermediate node along the bottom
        x0 = ax + NW / 2; y0 = ay + NH
        x1 = bx + NW / 2; y1 = by + NH
        byp = 806
        pts = [(x0, y0), (x0, byp), (x1, byp), (x1, y1)]
        for p, q in zip(pts, pts[1:]):
            c.line(p[0], p[1], q[0], q[1], 3, SOLID)
        c.arrow_head(x1, y1, -90, 11, SOLID)
        c.text((x0 + x1) / 2 - 160, byp - 26, 320, 24, "N04 → N13 长距先决（底部绕行）", 18, SOLID)
        path = [[round(v, 1) for v in p] for p in pts]
    else:
        p0, p1 = (ax + NW, acy), (bx, bcy)
        c.line(p0[0], p0[1], p1[0], p1[1], 3, SOLID)
        import math
        ang = math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
        c.arrow_head(p1[0], p1[1], ang, 11, SOLID)
        path = [[round(v, 1) for v in p0], [round(v, 1) for v in p1]]
    edge_records.append({"from": a, "to": b, "path_px": path,
                         "arrow_px": [round(path[-1][0], 1), round(path[-1][1], 1)]})

# feedback edges: dashed magenta, routed along the top with separate lanes
fb_records = []
for i, (a, b) in enumerate(feedback):
    ax, ay, acy = pos[a]; bx, by, bcy = pos[b]
    lane = 200 if i == 0 else 160
    x0 = ax + NW / 2; y0 = ay
    x1 = bx + (20 if i == 0 else 90); y1 = by - 8
    pts = [(x0, y0), (x0, lane), (x1, lane), (x1, y1)]
    for p, q in zip(pts, pts[1:]):
        c.dashed_line(p[0], p[1], q[0], q[1], 3, FEED, dash=9, gap=6)
    c.arrow_head(x1, y1, 90, 11, FEED)
    fb_records.append({"from": a, "to": b, "dashed": True,
                       "polyline_px": [[round(v, 1) for v in p] for p in pts],
                       "arrow_px": [round(x1, 1), round(y1, 1)],
                       "participates_in_dag": False})
c.rect(1000, 158, 350, 30, WHITE, radius=8, border="1 SOLID #F9A8D4")
c.text(1006, 160, 338, 26, "检查发现问题后修复  N10 → N08", 18, FEED, bold=True)
c.rect(1000, 198, 330, 30, WHITE, radius=8, border="1 SOLID #F9A8D4")
c.text(1006, 200, 318, 26, "失败后回到构建  N09 → N08", 18, FEED, bold=True)

# nodes (drawn last so no line crosses the labels)
for k, (x, y, cy) in pos.items():
    c.rect(x, y, NW, NH, NODE, radius=10, border="2 SOLID #CBD5E1")
    c.rect(x, y, 5, NH, SOLID, radius=2)
    c.text(x + 8, y + 3, NW - 14, 20, k + " · L%d" % layer[k], 18, SOLID, bold=True, font=LATIN)
    c.text(x + 8, y + 25, NW - 14, 30, nodes[k], 22, INK, bold=True)

# explanation cards
c.rect(48, 850, 740, 118, WHITE, radius=14, border="1 SOLID " + LINE)
c.text(70, 860, 700, 30, "图内解释 · 两条反馈回路", 24, INK, bold=True)
c.text(70, 894, 700, 30, "① 失败后回到构建：首轮渲染 N09 → DSL 构建 N08（重新出图）", 20, FEED)
c.text(70, 926, 700, 30, "② 检查发现问题后修复：视觉检查 N10 → DSL 构建 N08（改完再渲染）", 20, FEED)
c.rect(812, 850, 740, 118, "#0B1B35", radius=14)
c.text(834, 860, 700, 30, "读图规则与拓扑核对", 24, "#7DD3FC", bold=True)
c.text(834, 894, 700, 58,
       "实线蓝色箭头为有向先决依赖，一律由左层指向右层；洋红虚线是反馈，不参与 DAG 排序。"
       "交叉处没有连接点，不构成新的依赖。最长先决路径共 %d 个节点。" % len(best), 20, "#E8F0FC")
c.text(48, 978, 1504, 20, "拓扑层由 solid_edges 的最长前驱链计算；反馈边单独标注，未纳入层计算。节点字号 22px，注释 18px。", 16, MUTED)

dsl = c.render()
out = suite.out_dir(T)
(out / "dependency-map.snapshot").write_text(dsl, encoding="utf-8")
v = suite.tmp_dir(T, os.environ.get("BUILD_VERSION", "v1"))
(v / "dependency-map.snapshot").write_text(dsl, encoding="utf-8")

audit = {
    "schema_version": 1, "task_id": T, "path_base": "output_dir",
    "layers": {str(l): sorted(ks) for l, ks in sorted(by_layer.items())},
    "nodes": [{"id": k, "label": nodes[k], "topological_layer": layer[k],
               "prerequisite_in": sorted(ins[k]), "prerequisite_out": sorted(outs[k]),
               "pixel_box": [round(pos[k][0], 1), round(pos[k][1], 1),
                            round(pos[k][0] + NW, 1), round(pos[k][1] + NH, 1)]} for k in sorted(nodes)],
    "prerequisite_edges": edge_records,
    "longest_path": {"sequence": best, "length_nodes": len(best),
                     "method": "对 solid_edges 构成的有向无环图做最长前驱层数计算后从所有源点 DFS 取节点数最大路径；允许多解，此处给出一条",
                     "feedback_edges_excluded": True},
    "feedback_edges": fb_records,
    "rules": {"crossings_have_no_junction": True, "all_prerequisite_edges_left_to_right": True,
              "feedback_not_in_dag": True},
    "evidence": {"png": "dependency-map.png", "dsl": "dependency-map.snapshot"},
}
(out / "graph-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("A06 nodes=%d solid=%d feedback=%d layers=%d longest=%d" %
      (len(nodes), len(solid), len(feedback), len(by_layer), len(best)))
