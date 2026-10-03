"""A06 graph audit: topological layers, neighbours, longest prerequisite path, feedback placement.

Feedback edges are deliberately NOT part of the DAG ordering, so the layer computation runs
on solid_edges only.
"""
from __future__ import annotations

import json
import os

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN_ID = "20261003-114508-flashmax"
TASK = "A06"
SRC = os.path.join(ROOT, "tasks", "A06-dependency-graph", "inputs", "graph.json")
OUT = os.path.join(ROOT, "outputs", RUN_ID, TASK)
TMP = os.path.join(ROOT, "tmp", RUN_ID, TASK)
os.makedirs(OUT, exist_ok=True)
os.makedirs(TMP, exist_ok=True)

G = json.load(open(SRC, encoding="utf-8"))
NODES = [n["id"] for n in G["nodes"]]
LABEL = {n["id"]: n["label"] for n in G["nodes"]}
SOLID = [tuple(e) for e in G["solid_edges"]]
FEEDBACK = [tuple(e) for e in G["feedback_edges"]]

out_nei = {n: [] for n in NODES}
in_nei = {n: [] for n in NODES}
for a, b in SOLID:
    out_nei[a].append(b)
    in_nei[b].append(a)

# ---- Kahn topological order + longest path by node count (DAG over solid edges only) ----
indeg = {n: len(in_nei[n]) for n in NODES}
queue = sorted([n for n in NODES if indeg[n] == 0])
order, layers = [], {n: 0 for n in NODES}
while queue:
    n = queue.pop(0)
    order.append(n)
    for m in sorted(out_nei[n]):
        layers[m] = max(layers[m], layers[n] + 1)
        indeg[m] -= 1
        if indeg[m] == 0:
            queue.append(m)
assert len(order) == len(NODES), "solid_edges 必须是无环的（反馈边不参与排序）"

# longest prerequisite chain by node count; ties are allowed, one witness is reported
dist = {n: 1 for n in NODES}
pred = {n: None for n in NODES}
for n in order:
    for m in sorted(out_nei[n]):
        if dist[n] + 1 > dist[m]:
            dist[m] = dist[n] + 1
            pred[m] = n

end = max(NODES, key=lambda n: dist[n])
chain, cur = [], end
while cur is not None:
    chain.append(cur)
    cur = pred[cur]
chain.reverse()

layer_groups = {}
for n in NODES:
    layer_groups.setdefault(layers[n], []).append(n)
for k in layer_groups:
    layer_groups[k].sort()

# ---- feedback edge character ----
fb = []
for a, b in FEEDBACK:
    fb.append({
        "from": a, "to": b,
        "from_label": LABEL[a], "to_label": LABEL[b],
        "excluded_from_topological_order": True,
        "is_dag_edge": False,
        "same_venue_note": f"{LABEL[a]} 回流到 {LABEL[b]}，构成回路，故不参与拓扑分层",
    })

doc = {
    "schema": "a06-graph-audit/1",
    "run_id": RUN_ID,
    "title": "从需求到可复现交付",
    "source_file": "tasks/A06-dependency-graph/inputs/graph.json",
    "counts": {"nodes": len(NODES), "solid_edges": len(SOLID), "feedback_edges": len(FEEDBACK)},
    "labels": LABEL,
    "topological_layers": {str(k): v for k, v in sorted(layer_groups.items())},
    "layer_index": layers,
    "topological_order": order,
    "acyclic_check": {
        "method": "Kahn 算法只在 solid_edges 上运行",
        "result": "14 个节点全部出队，先决关系无环",
        "feedback_edges_excluded": [[a, b] for a, b in FEEDBACK],
    },
    "neighbours": {n: {"in": sorted(in_nei[n]), "out": sorted(out_nei[n]),
                       "in_degree": len(in_nei[n]), "out_degree": len(out_nei[n])} for n in NODES},
    "longest_prerequisite_path": {
        "measured_by": "节点数",
        "node_count": len(chain),
        "edge_count": len(chain) - 1,
        "path": chain,
        "path_labels": [f"{n} {LABEL[n]}" for n in chain],
        "tie_note": "按节点数计算的最长先决路径可能多解；此处给出至少一条（N01→N02→N04→N07→N08→N09→N10→N11→N12→N13→N14）。",
        "all_distances": dist,
    },
    "feedback_edges": fb,
    "layout_contract": {
        "node_columns": "列 = 拓扑层，层号从左到右递增",
        "edge_direction_rule": "每条先决边的箭头都由较小层指向较大层，图中不存在指向过去层的先决边",
        "parallelism": "同一列内的节点互为并行分支（层内没有先决关系）",
        "feedback_rendering": "反馈边用虚线 + 专用图例，沿图底部与左侧专用通道绕行，不画成普通先决依赖",
        "crossing_rule": "交叉线在没有连接点时不构成新的依赖——图中所有线段只在端点相连",
    },
}

with open(os.path.join(OUT, "graph-audit.json"), "w", encoding="utf-8") as fh:
    json.dump(doc, fh, ensure_ascii=False, indent=2)
with open(os.path.join(TMP, "graph-audit.check.json"), "w", encoding="utf-8") as fh:
    json.dump({"layers": doc["topological_layers"], "order": order,
               "longest": chain, "feedback": fb}, fh, ensure_ascii=False, indent=2)

print("layers:", {k: v for k, v in sorted(layer_groups.items())})
print("topological order:", order)
print("longest path (%d nodes):" % len(chain), " -> ".join(chain))
print("feedback:", [(a, b) for a, b in FEEDBACK])
