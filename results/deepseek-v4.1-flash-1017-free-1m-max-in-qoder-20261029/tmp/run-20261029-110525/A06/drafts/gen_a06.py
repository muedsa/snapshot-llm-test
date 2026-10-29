#!/usr/bin/env python3
"""A06 dependency map: 14 nodes, layered DAG, dashed feedback edges, audit json."""
import json, os, math, html
from pathlib import Path

SCRIPT = Path(__file__).resolve()
SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", SCRIPT.parents[4]))
RUN_ID = SCRIPT.parents[2].name
OUT = SUITE_ROOT / "outputs" / RUN_ID / "A06"
OUT.mkdir(parents=True, exist_ok=True)

def esc(s): return html.escape(str(s), quote=False)
def T(txt, size, color="#0B1220", bold=False, extra=""):
    st = ' fontStyle="BOLD"' if bold else ""
    return f'<Text fontFamily="Noto Sans CJK SC" fontSize="{size}" color="{color}"{st}{extra}>{esc(txt)}</Text>'

graph = json.loads((SUITE_ROOT / "tasks/A06-dependency-graph/inputs/graph.json").read_text(encoding="utf-8"))
nodes = graph["nodes"]
labels = {n["id"]: n["label"] for n in nodes}
solid = [tuple(e) for e in graph["solid_edges"]]
feedback = [tuple(e) for e in graph["feedback_edges"]]

# topological layers (longest path from sources)
preds = {n["id"]: [] for n in nodes}
for a, b in solid:
    preds[b].append(a)
layer = {}
def lay(nid):
    if nid in layer: return layer[nid]
    layer[nid] = 0 if not preds[nid] else max(lay(p) + 1 for p in preds[nid])
    return layer[nid]
for n in nodes: lay(n["id"])
max_layer = max(layer.values())

# longest path by node count
path = {}
def longest(nid):
    if nid in path: return path[nid]
    best = [nid]
    for a in preds[nid]:
        cand = longest(a) + [nid]
        if len(cand) > len(best): best = cand
    path[nid] = best
    return best
lp = max((longest(n["id"]) for n in nodes), key=len)

# positions
W, H = 1600, 1000
cy = 380
layer_x = [95 + i * 145 for i in range(max_layer + 1)]
pos = {}
for n in nodes:
    nid = n["id"]; L = layer[nid]
    same = [m["id"] for m in nodes if layer[m["id"]] == L]
    idx = same.index(nid)
    y = cy if len(same) == 1 else (cy - 75 if idx == 0 else cy + 75)
    pos[nid] = (layer_x[L], y)
NW, NH = 104, 62

def seg(x1, y1, x2, y2, color, w=2):
    length = math.hypot(x2 - x1, y2 - y1)
    if length < 0.5: return ""
    ang = math.atan2(y2 - y1, x2 - x1)
    c, s = math.cos(ang), math.sin(ang)
    mat = f"({c:.6f},{s:.6f},0,0,{-s:.6f},{c:.6f},0,0,0,0,1,0,0,0,0,1)"
    return f'<Positioned left="{x1:.1f}" top="{y1-w/2:.1f}"><Transform matrix="{mat}" origin="(0,0)"><Container width="{length:.1f}" height="{w}" color="{color}"/></Transform></Positioned>'

def arrow(x, y, ang, color):
    out = []
    for d in (28, -28):
        a = ang + math.radians(d)
        out.append(seg(x - 11 * math.cos(a), y - 11 * math.sin(a), x, y, color, 2))
    return "".join(out)

def edge_pts(a, b):
    ax, ay = pos[a]; bx, by = pos[b]
    # start at right edge for forward edges, else nearest side
    sx, sy = ax + NW / 2, ay
    ex, ey = bx - NW / 2, by
    return sx, sy, ex, ey

def dash_line(x1, y1, x2, y2, color="#DB2777"):
    out = []
    length = math.hypot(x2 - x1, y2 - y1)
    ang = math.atan2(y2 - y1, x2 - x1)
    ux, uy = math.cos(ang), math.sin(ang)
    t = 0
    while t < length:
        e = min(t + 9, length)
        out.append(seg(x1 + ux * t, y1 + uy * t, x1 + ux * e, y1 + uy * e, color, 2))
        t = e + 7
    return "".join(out)

def route(points, color="#DB2777", arrow_end=True):
    out = []
    for i in range(len(points) - 1):
        x1, y1 = points[i]; x2, y2 = points[i + 1]
        out.append(dash_line(x1, y1, x2, y2, color))
        if i == len(points) - 2 and arrow_end:
            out.append(arrow(x2, y2, math.atan2(y2 - y1, x2 - x1), color))
    return "".join(out)

parts = ['<Snapshot background="#F7F8FC" type="png">', '<Container width="1600" height="1000"><Stack alignment="TOP_LEFT" clipBehavior="NONE"><Container width="1600" height="1000" color="#F7F8FC"/>']
# header
parts.append('<Positioned left="40" top="30"><Column crossAxisAlignment="START" mainAxisSize="MIN">' + T("DELIVERY PIPELINE / DEPENDENCY MAP", 14, "#2563EB", True, ' letterSpacing="2"') + T("从需求到可复现交付", 40, "#0B1220", True) + T("14 节点 · 16 条先决边 · 2 条反馈边 · 横向位置 = 拓扑层", 20, "#56637A") + '</Column></Positioned>')
parts.append('<Positioned right="40" top="34"><Column crossAxisAlignment="END" mainAxisSize="MIN"><Row crossAxisAlignment="CENTER"><Container width="38" height="2" color="#64748B"/><SizedBox width="8"/>' + T("先决依赖", 18, "#475569") + '</Row><SizedBox height="4"/><Row crossAxisAlignment="CENTER">' + ''.join('<Container width="8" height="2" color="#DB2777"/><SizedBox width="4"/>' for _ in range(3)) + '<SizedBox width="2"/>' + T("反馈关系", 18, "#BE185D") + '</Row>' + T("无端点交点不表示连接", 16, "#8896AB") + '</Column></Positioned>')
# stage labels + bands
stages = [(0, 2, "准备", "#2563EB"), (3, 4, "设计", "#7C3AED"), (5, 7, "构建", "#0D9488"), (8, 10, "交付", "#D97706")]
for lo, hi, name, color in stages:
    x1 = layer_x[lo] - NW / 2 - 22
    x2 = layer_x[hi] + NW / 2 + 22
    parts.append(f'<Positioned left="{x1:.1f}" top="238" width="{x2-x1:.1f}" height="284"><Container width="{x2-x1:.1f}" height="284" color="{color}0D" borderRadius="14"/></Positioned>')
    parts.append(f'<Positioned left="{x1:.1f}" top="126" width="{x2-x1:.1f}"><Container width="{x2-x1:.1f}" alignment="CENTER">' + T(name, 20, color, True, ' letterSpacing="2"') + '</Container></Positioned>')
# layer labels
for n in nodes:
    x = pos[n["id"]][0]
    parts.append(f'<Positioned left="{x-30}" top="246" width="60"><Container width="60" alignment="CENTER">' + T(f"L{layer[n['id']]}", 15, "#94A3B8", True) + '</Container></Positioned>')
# skip edge N04 -> N13 (routed above)
parts.append(route([(pos["N04"][0], pos["N04"][1] - NH / 2), (pos["N04"][0], 220), (pos["N13"][0], 220), (pos["N13"][0], pos["N13"][1] - NH / 2)], color="#94A3B8"))
parts.append('<Positioned left="690" top="196"><Container padding="(2,6)" color="#F7F8FC">' + T("N04 → N13 跨层先决（顶部绕行）", 16, "#64748B") + '</Container></Positioned>')
# feedback edges (dashed)
parts.append(route([(pos["N09"][0], pos["N09"][1] - NH / 2), (pos["N09"][0], 176), (pos["N08"][0], 176), (pos["N08"][0], pos["N08"][1] - NH / 2)]))
parts.append('<Positioned left="600" top="152"><Container padding="(2,6)" color="#F7F8FC">' + T("N09 首轮渲染失败 → 回到 N08 构建", 17, "#BE185D", True) + '</Container></Positioned>')
parts.append(route([(pos["N10"][0], pos["N10"][1] + NH / 2), (pos["N10"][0], 566), (pos["N08"][0], 566), (pos["N08"][0], pos["N08"][1] + NH / 2)]))
parts.append('<Positioned left="700" top="574"><Container padding="(2,6)" color="#F7F8FC">' + T("N10 检查发现问题 → 回 N08 修正后重建", 17, "#BE185D", True) + '</Container></Positioned>')
# solid edges
for a, b in solid:
    if (a, b) == ("N04", "N13"):
        continue
    sx, sy, ex, ey = edge_pts(a, b)
    parts.append(seg(sx, sy, ex, ey, "#64748B", 2))
    parts.append(arrow(ex, ey, math.atan2(ey - sy, ex - sx), "#64748B"))
# nodes
for n in nodes:
    nid = n["id"]; x, y = pos[nid]
    l = layer[nid]
    accent = "#2563EB" if l <= 2 else ("#7C3AED" if l <= 4 else ("#0D9488" if l <= 7 else "#D97706"))
    left = x - NW / 2; top = y - NH / 2
    parts.append(f'<Positioned left="{left:.1f}" top="{top:.1f}" width="{NW}" height="{NH}"><Container width="{NW}" height="{NH}" color="#FFFFFF" borderRadius="12" border="1 SOLID #CBD5E1" padding="(4,6)"><Column crossAxisAlignment="CENTER" mainAxisAlignment="CENTER" mainAxisSize="MIN">')
    parts.append(f'<Container padding="(0,6)" color="{accent}18" borderRadius="5">' + T(nid, 13, accent, True) + '</Container>')
    parts.append('<SizedBox height="2"/>')
    parts.append(T(labels[nid], 22, "#0B1220", True, ' maxLines="1"'))
    parts.append('</Column></Container></Positioned>')

# bottom cards
cards = [
    ("先决关系 / SOLID", "16 条 solid_edges 都指向更高层；N04→N13 是跨层数据先决，用顶部绕行线表达，不改变拓扑层。", "#2563EB"),
    ("反馈不是先决 / FEEDBACK", "2 条粉色虚线：N09→N08（渲染失败回到构建）、N10→N08（检查发现问题回到构建修正）；不参与 DAG 排序。N10 的常规修复仍走 N11→N12。", "#BE185D"),
    ("并行与最长路径 / LAYERS", "L1–L3 允许并行（如 N02/N03、N04/N05、N06/N07）。最长先决路径 11 节点：N01→N02→N04→N07→N08→N09→N10→N11→N12→N13→N14。", "#0D9488"),
]
stat_sets = [
    [("16 条先决边", "#2563EB"), ("11 个拓扑层", "#2563EB"), ("0 条反向先决", "#2563EB")],
    [("2 条反馈边", "#BE185D"), ("N09 → N08", "#BE185D"), ("N10 → N08", "#BE185D")],
    [("11 节点最长路径", "#0D9488"), ("3 组并行", "#0D9488"), ("L0 → L10", "#0D9488")],
]
for i, (title, body, color) in enumerate(cards):
    x = 40 + i * 520
    parts.append(f'<Positioned left="{x}" top="620"><Container width="500" height="290" color="#FFFFFF" borderRadius="18" border="1 SOLID #E3E9F2" padding="22"><Column crossAxisAlignment="START" mainAxisSize="MIN">')
    parts.append(f'<Row crossAxisAlignment="CENTER"><Container width="8" height="8" color="{color}" shape="CIRCLE"/><SizedBox width="7"/>' + T(title, 20, color, True, ' letterSpacing="1"') + '</Row>')
    parts.append('<SizedBox height="10"/>')
    parts.append(T(body, 20, "#334155"))
    parts.append('<Spacer/>')
    parts.append('<Row crossAxisAlignment="CENTER">' + '<SizedBox width="8"/>'.join([f'<Container padding="(4,9)" color="{color}12" borderRadius="6">' + T(x[0], 16, x[1], True) + '</Container>' for x in stat_sets[i]]) + '</Row>')
    parts.append('</Column></Container></Positioned>')
parts.append('<Positioned left="40" top="936"><Row crossAxisAlignment="CENTER">' + T("读图：横向层 = 先决顺序；同层堆叠 = 并行；粉色虚线 = 反馈；灰色交点若没有端点圆点，不构成依赖。", 18, "#64748B") + '</Row></Positioned>')
parts.append('</Stack></Container></Snapshot>')
dsl = "\n".join(parts)
(OUT / "dependency-map.snapshot").write_text(dsl, encoding="utf-8")

neighbors = {n["id"]: {"in": [a for a, b in solid if b == n["id"]], "out": [b for a, b in solid if a == n["id"]]} for n in nodes}
audit = {
    "schema_version": 1, "task_id": "A06", "path_base": "output_dir",
    "nodes": [{"id": n["id"], "label": n["label"], "layer": layer[n["id"]],
               "position_center_px": list(pos[n["id"]])} for n in nodes],
    "solid_edges": [{"from": a, "to": b, "from_layer": layer[a], "to_layer": layer[b],
                     "forward": layer[b] > layer[a]} for a, b in solid],
    "feedback_edges": [{"from": a, "to": b,
                        "route": "top" if (a, b) == ("N09", "N08") else "bottom",
                        "label_position_px": [600, 152] if (a, b) == ("N09", "N08") else [700, 574],
                        "endpoints_px": [list(pos[a]), list(pos[b])],
                        "not_in_topological_sort": True} for a, b in feedback],
    "neighbors": neighbors,
    "longest_path": lp, "longest_path_node_count": len(lp),
    "layers": {str(i): [n["id"] for n in nodes if layer[n["id"]] == i] for i in range(max_layer + 1)},
    "checks": {
        "all_nodes_14": len(nodes) == 14,
        "solid_edges_16": len(solid) == 16,
        "feedback_edges_2": len(feedback) == 2,
        "all_solid_forward": all(layer[b] > layer[a] for a, b in solid),
        "crossings_without_dot_are_not_edges": "图例与页脚明确说明",
    }
}
(OUT / "graph-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
print("wrote A06", len(dsl), "layers", max_layer + 1, "longest", len(lp))
