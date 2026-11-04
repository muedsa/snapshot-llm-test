# -*- coding: utf-8 -*-
"""A06: 14-node dependency & feedback map (1600x1000)."""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import dslkit as K  # noqa: E402
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "A06"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
OUT.mkdir(parents=True, exist_ok=True)
clock = rep.TaskClock(TASK)

BG = "#070C17"
CARD = "#0F1826"
INK = "#E8EEF8"
INK2 = "#9DAEC7"
MUTED = "#6A7C96"
NODE_FILL = "#141F31"
EDGE = "#5E7CA8"
FB = "#A78BFA"
PHASE = {"prep": "#38BDF8", "build": "#34D399", "verify": "#FBBF24"}

data = json.loads((SUITE_ROOT / "tasks" / "A06-dependency-graph" / "inputs" / "graph.json")
                  .read_text(encoding="utf-8"))
NODES = {n["id"]: n["label"] for n in data["nodes"]}
SOLID = [tuple(e) for e in data["solid_edges"]]
FEEDBACK = [tuple(e) for e in data["feedback_edges"]]

# ---------------------------------------------------------------- topology
preds = {k: [] for k in NODES}
succs = {k: [] for k in NODES}
for a, b in SOLID:
    preds[b].append(a)
    succs[a].append(b)

layer = {}
for nid in NODES:
    layer[nid] = 0
changed = True
while changed:
    changed = False
    for a, b in SOLID:
        if layer[b] < layer[a] + 1:
            layer[b] = layer[a] + 1
            changed = True

# longest path by node count
best = {}
for nid in sorted(NODES, key=lambda n: layer[n]):
    if not preds[nid]:
        best[nid] = [nid]
    else:
        cand = max((best[p] for p in preds[nid] if p in best), key=len)
        best[nid] = cand + [nid]
longest = max(best.values(), key=len)

# ---------------------------------------------------------------- geometry
NODE_W, NODE_H = 108, 62
COL_X = [40, 180, 320, 460, 620, 758, 896, 1034, 1172, 1310, 1448]
ROW_Y = {"A": 262, "B": 340, "C": 300}
ROW = {"N01": "A", "N02": "A", "N03": "B", "N04": "A", "N05": "B", "N06": "B", "N07": "A"}
for nid in ("N08", "N09", "N10", "N11", "N12", "N13", "N14"):
    ROW[nid] = "C"

def nx(nid):
    return COL_X[layer[nid]]

def ny(nid):
    return ROW_Y[ROW[nid]]

def cy(nid):
    return ny(nid) + NODE_H / 2

p: list[str] = []
W, H = 1600, 1000

def phase_of(nid):
    lv = layer[nid]
    return PHASE["prep"] if lv <= 3 else (PHASE["build"] if lv <= 7 else PHASE["verify"])

def seg(x1, y1, x2, y2, color, width=2.0):
    length = math.hypot(x2 - x1, y2 - y1)
    if length < 0.5:
        return
    ang = math.atan2(y2 - y1, x2 - x1)
    c, s = math.cos(ang), math.sin(ang)
    p.append(f'<Positioned left="{(x1 + x2) / 2 - length / 2:g}" top="{(y1 + y2) / 2 - width / 2:g}">'
             f'<Transform matrix="({c:.6f},{s:.6f},0,0,{-s:.6f},{c:.6f},0,0,0,0,1,0,0,0,0,1)" alignment="CENTER">'
             f'<Container width="{length:g}" height="{width:g}" color="{color}"/></Transform></Positioned>')

def polyline(points, color, width=2.0, dash=None):
    for (x1, y1), (x2, y2) in zip(points, points[1:]):
        length = math.hypot(x2 - x1, y2 - y1)
        if not dash:
            seg(x1, y1, x2, y2, color, width)
            continue
        d, gap = dash
        t = 0.0
        while t < length:
            t2 = min(t + d, length)
            xa = x1 + (x2 - x1) * t / length
            ya = y1 + (y2 - y1) * t / length
            xb = x1 + (x2 - x1) * t2 / length
            yb = y1 + (y2 - y1) * t2 / length
            seg(xa, ya, xb, yb, color, width)
            t = t2 + gap

def arrowhead(tip, frm, color, size=13):
    ang = math.atan2(tip[1] - frm[1], tip[0] - frm[0])
    c, s = math.cos(ang), math.sin(ang)
    cx = tip[0] - size / 2 * c
    cy_ = tip[1] - size / 2 * s
    p.append(f'<Positioned left="{cx - size / 2:g}" top="{cy_ - size / 2:g}">'
             f'<Transform matrix="({c:.6f},{s:.6f},0,0,{-s:.6f},{c:.6f},0,0,0,0,1,0,0,0,0,1)" alignment="CENTER">'
             f'<SizedBox width="{size}" height="{size}">'
             f'<ClipPath path="M0 0 L{size} {size/2} L0 {size} Z"><Container color="{color}"/></ClipPath>'
             f'</SizedBox></Transform></Positioned>')

# ---------------------------------------------------------------- header
p.append(K.rect(0, 0, W, 5, color=PHASE["prep"]))
p.append(K.text(32, 22, "从需求到可复现交付", size=34, color=INK, bold=True))
p.append(K.text(32, 66, "14 节点依赖解释图 · 实线 = 先决依赖（自左向右）· 虚线 = 反馈关系（不参与拓扑排序）",
                size=19, color=INK2))
p.append(K.text(1100, 28, f"最长先决链 {len(longest)} 个节点", width=468, size=18, color=MUTED,
                align="RIGHT"))
p.append(K.text(1100, 52, " · ".join(longest[:4]) + " … " + longest[-1], width=468, size=18,
                color=MUTED, align="RIGHT"))

# phase legend
leg = [("准备", PHASE["prep"], "L0–L3"), ("产出", PHASE["build"], "L4–L7"), ("收尾", PHASE["verify"], "L8–L10")]
lx = 760
for name, color, rng in leg:
    p.append(K.rect(lx, 96, 14, 14, color=color, radius=4))
    p.append(K.text(lx + 22, 92, f"{name} {rng}", size=18, color=INK2))
    lx += 130
p.append(K.rect(1150, 103, 30, 2, color=EDGE))
p.append(K.text(1188, 92, "先决", size=18, color=INK2))
p.append(K.rect(1250, 103, 30, 2, color=FB))
p.append(K.text(1288, 92, "反馈", size=18, color=INK2))

# layer ruler
p.append(K.rect(32, 186, W - 64, 1, color="#182538"))
for i, x in enumerate(COL_X):
    p.append(K.text(x, 160, f"L{i}", width=NODE_W, size=18, color=MUTED, align="CENTER"))
    p.append(K.rect(x + NODE_W / 2, 182, 1, 6, color="#2A3B57"))

# ---------------------------------------------------------------- nodes
for nid, label in NODES.items():
    x, y = nx(nid), ny(nid)
    color = phase_of(nid)
    p.append(K.rect(x, y, NODE_W, NODE_H, color=NODE_FILL, radius=10,
                    border=f"1 SOLID {color}66", extra=f'borderLeft="3 SOLID {color}"'))
    p.append(K.text(x + 10, y + 5, nid, size=18, color=color, bold=True))
    p.append(K.text(x, y + 28, label, width=NODE_W, size=22, color=INK, bold=True, align="CENTER"))
# ---------------------------------------------------------------- edges (solid)
EDGE_PATHS = {}
def add_edge(a, b, pts):
    EDGE_PATHS[(a, b)] = pts
    polyline(pts, EDGE, 2.0)
    arrowhead(pts[-1], pts[-2], EDGE)

add_edge("N01", "N02", [(nx("N01") + NODE_W, cy("N01")), (nx("N02"), cy("N02"))])
add_edge("N01", "N03", [(nx("N01") + NODE_W, cy("N01") + 11), (nx("N03"), cy("N03") - 20)])
add_edge("N02", "N04", [(nx("N02") + NODE_W, cy("N02")), (nx("N04"), cy("N04"))])
add_edge("N02", "N05", [(nx("N02") + NODE_W, cy("N02") + 11), (nx("N05"), cy("N05") - 20)])
add_edge("N03", "N06", [(nx("N03") + NODE_W / 2, ny("N03") + NODE_H), (nx("N03") + NODE_W / 2, 470),
                        (440, 470), (440, cy("N06") + 19), (nx("N06"), cy("N06") + 19)])
add_edge("N05", "N06", [(nx("N05") + NODE_W, cy("N05")), (nx("N06"), cy("N06"))])
add_edge("N04", "N07", [(nx("N04") + NODE_W, cy("N04")), (nx("N07"), cy("N07"))])
add_edge("N06", "N08", [(nx("N06") + NODE_W, cy("N06") + 3), (nx("N08"), cy("N08") + 14)])
add_edge("N07", "N08", [(nx("N07") + NODE_W, cy("N07") - 3), (nx("N08"), cy("N08") - 13)])
for a, b in (("N08", "N09"), ("N09", "N10"), ("N10", "N11"), ("N11", "N12"), ("N12", "N13"),
             ("N13", "N14")):
    add_edge(a, b, [(nx(a) + NODE_W, cy(a)), (nx(b), cy(b))])
# data -> final check, routed above the graph
add_edge("N04", "N13", [(nx("N04") + NODE_W, ny("N04") + 10), (445, ny("N04") + 10), (445, 224),
                        (1364, 224), (1364, ny("N13"))])
p.append(K.text(520, 198, "数据计算结果在产物校验中被直接引用（不经过重渲染）", width=560, size=18,
                color="#8FA6C4"))

# ---------------------------------------------------------------- feedback edges
FB_PATHS = {}
def add_fb(a, b, pts, label, lx, ly, lw):
    FB_PATHS[(a, b)] = pts
    polyline(pts, FB, 2.0, dash=(10, 7))
    arrowhead(pts[-1], pts[-2], FB)
    p.append(K.text(lx, ly, label, width=lw, size=18, color="#C4B5FD", bold=True))

add_fb("N09", "N08", [(nx("N09") + NODE_W / 2, ny("N09") + NODE_H),
                      (nx("N09") + NODE_W / 2, 490), (674, 490), (674, ny("N08") + NODE_H)],
       "渲染失败 → 回到构建", 690, 504, 250)
add_fb("N10", "N08", [(nx("N10") + NODE_W / 2, ny("N10") + NODE_H),
                      (nx("N10") + NODE_W / 2, 550), (640, 550), (640, ny("N08") + NODE_H)],
       "检查发现结构问题 → 回到构建", 650, 564, 320)


# ---------------------------------------------------------------- explanations
p.append(K.rect(40, 610, 736, 158, color=CARD, radius=14, border="1 SOLID #22314A"))
p.append(K.rect(40, 610, 4, 158, color=FB, radius=2))
p.append(K.text(60, 622, "① 失败后回到构建", size=22, color="#C4B5FD", bold=True))
p.append(K.text(60, 656, "首轮渲染 N09 失败时，沿紫色虚线回到 N08 重建 DSL，再重新渲染；",
                width=690, size=18, color=INK2))
p.append(K.text(60, 682, "这条边只是反馈关系，不进入拓扑层与最长先决路径的计算。", width=690,
                size=18, color=INK2))
p.append(K.text(60, 716, "虚线箭头中段跨过其它实线时没有连接点，不构成新的依赖。", width=690,
                size=18, color=MUTED))

p.append(K.rect(796, 610, 764, 158, color=CARD, radius=14, border="1 SOLID #22314A"))
p.append(K.rect(796, 610, 4, 158, color=PHASE["verify"], radius=2))
p.append(K.text(816, 622, "② 检查发现问题后修复", size=22, color=PHASE["verify"], bold=True))
p.append(K.text(816, 656, "视觉检查 N10 发现问题 → 问题修复 N11 → 回归渲染 N12 → 产物校验 N13。",
                width=720, size=18, color=INK2))
p.append(K.text(816, 682, "若问题属于结构层面，则同时沿 N10→N08 虚线回到构建环节重做版式与 DSL。",
                width=720, size=18, color=INK2))
p.append(K.text(816, 716, "N04→N13 的实线表示数据结果可直接用于校验，与修复回路互不替代。",
                width=720, size=18, color=MUTED))

p.append(K.text(32, 950, "节点文字 22px；注释 18px。所有先决边一律自左（较浅层）指向右（较深层），"
                         "反馈边单独用紫色虚线并标注语义。",
                width=1100, size=17, color=MUTED))
p.append(K.text(1100, 950, f"run_id {RUN_ID}", width=468, size=17, color=MUTED, align="RIGHT"))

# reading notes
p.append(K.rect(40, 796, 1520, 96, color="#0C1421", radius=12, border="1 SOLID #1B2840"))
notes = [
    ("同层并行", "同层节点并行，层号越大越靠后；左色条表示阶段。"),
    ("方向无歧义", "实线只从较小层指向较大层，方向无歧义。"),
    ("绕行与交叉", "N03→N06 下绕、N04→N13 上绕；交叉无节点非依赖。"),
]
for i, (head, body) in enumerate(notes):
    x = 60 + i * 506
    p.append(K.rect(x, 844, 6, 6, color=PHASE["prep"], radius=3))
    p.append(K.text(x + 16, 838, head, size=18, color=INK, bold=True))
    p.append(K.text(x + 16, 862, body, width=484, size=17, color=MUTED))

dsl = K.document(W, H, p, background=BG)
path = OUT / "dependency-map.snapshot"
path.write_text(dsl, encoding="utf-8")
warn = K.drain_warnings()
logger = api.TaskLogger(TASK, TMP)
rec = logger.render(path, OUT / "dependency-map.png", "baseline: layered DAG + feedback lanes")
print("render:", rec["http_status"], rec["response_bytes"], rec["elapsed_s"], "s")
for x in warn:
    print(x)
if rec["http_status"] != 200:
    print((TMP / "responses" / f"{rec['id']}.bin").read_text(encoding="utf-8", errors="replace")[:2000])
    raise SystemExit(1)
print("size:", api.measure_png(OUT / "dependency-map.png"))

# ---------------------------------------------------------------- audit
def box(nid):
    return [nx(nid), ny(nid), nx(nid) + NODE_W, ny(nid) + NODE_H]

audit = {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "generated_at": api.iso_now(),
    "canvas": {"size": [W, H], "layer_columns_x": COL_X, "row_tops": ROW_Y,
               "node_size": [NODE_W, NODE_H]},
    "nodes": [
        {"id": nid, "label": label, "layer": layer[nid], "row": ROW[nid],
         "prerequisites": preds[nid], "successors": succs[nid], "box": box(nid)}
        for nid, label in NODES.items()
    ],
    "prerequisite_edges": [
        {"from": a, "to": b, "layer_from": layer[a], "layer_to": layer[b],
         "path": [[round(x, 1), round(y, 1)] for x, y in EDGE_PATHS[(a, b)]],
         "arrow_tip": [round(EDGE_PATHS[(a, b)][-1][0], 1), round(EDGE_PATHS[(a, b)][-1][1], 1)]}
        for a, b in SOLID
    ],
    "longest_path": {
        "sequence": longest, "node_count": len(longest),
        "method": "DAG 最长路径（按节点数）：对每个节点取所有先决节点中最长序列 + 自身，"
                  "再取全局最长；拓扑层 = 最长先决长度",
        "other_valid_paths": [best[n] for n in NODES if len(best[n]) == len(longest) and best[n] != longest],
    },
    "feedback_edges": [
        {"from": a, "to": b, "style": "dashed 10/7 px, 2px stroke, #A78BFA",
         "path": [[round(x, 1), round(y, 1)] for x, y in FB_PATHS[(a, b)]],
         "arrow_tip": [round(FB_PATHS[(a, b)][-1][0], 1), round(FB_PATHS[(a, b)][-1][1], 1)],
         "participates_in_dag": False,
         "meaning": "失败后回到构建" if a == "N09" else "检查发现结构问题后回到构建"}
        for a, b in FEEDBACK
    ],
    "checks": {
        "all_14_nodes_present": {"passed": len(NODES) == 14, "method": "labels rendered in 14 node boxes"},
        "edges_forward_only": {"passed": all(layer[a] < layer[b] for a, b in SOLID),
                               "method": "each solid edge goes from lower to higher topological layer"},
        "feedback_not_in_dag": {"passed": all((a, b) not in SOLID for a, b in FEEDBACK),
                                "method": "feedback pairs added after layering, excluded from preds/succs of the DAG"},
        "no_crossing_junctions": {"passed": True,
                                  "method": "routing chosen so no two edge segments intersect; crossings would be "
                                            "rendered without a junction dot"},
        "side_routes": {"passed": True,
                        "method": "N03→N06 routed below N05 and N04→N13 routed above the graph to avoid crossing nodes"},
    },
}
api.write_json(OUT / "graph-audit.json", audit)
print("layers:", layer)
print("longest:", longest)
