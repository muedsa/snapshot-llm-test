from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import suitekit as s

RUN_ID = "20261124T113838+0800-aac601"
TASK = "A06"
NODE_W, NODE_H = 116, 76
CENTERS = {
    "N01": (100, 500),
    "N02": (240, 400), "N03": (240, 600),
    "N04": (380, 300), "N05": (380, 500),
    "N06": (520, 400), "N07": (520, 650),
    "N08": (660, 500), "N09": (800, 500), "N10": (940, 500),
    "N11": (1080, 500), "N12": (1220, 500), "N13": (1360, 500),
    "N14": (1500, 500),
}
LAYER_NAMES = ["需求", "并行准备", "计算/规划", "版式/图表", "构建", "渲染", "检查", "修复", "回归", "校验", "归档"]
SOLID_ROUTES = {
    ("N01", "N02"): [(158, 500), (170, 500), (170, 400), (182, 400)],
    ("N01", "N03"): [(158, 500), (176, 500), (176, 600), (182, 600)],
    ("N02", "N04"): [(298, 390), (310, 390), (310, 300), (322, 300)],
    ("N02", "N05"): [(298, 410), (304, 410), (304, 500), (322, 500)],
    ("N03", "N06"): [(298, 600), (454, 600), (454, 390), (462, 390)],
    ("N05", "N06"): [(438, 490), (446, 490), (446, 410), (462, 410)],
    ("N04", "N07"): [(438, 310), (442, 310), (442, 650), (462, 650)],
    ("N06", "N08"): [(578, 390), (590, 390), (590, 440), (660, 440), (660, 462)],
    ("N07", "N08"): [(578, 660), (598, 660), (598, 500), (602, 500)],
    ("N08", "N09"): [(718, 500), (742, 500)],
    ("N09", "N10"): [(858, 500), (882, 500)],
    ("N10", "N11"): [(998, 500), (1022, 500)],
    ("N11", "N12"): [(1138, 500), (1162, 500)],
    ("N12", "N13"): [(1278, 500), (1302, 500)],
    ("N13", "N14"): [(1418, 500), (1442, 500)],
    ("N04", "N13"): [(438, 290), (1400, 290), (1400, 462)],
}
FEEDBACK_ROUTES = {
    ("N09", "N08"): [(800, 538), (800, 590), (640, 590), (640, 538)],
    ("N10", "N08"): [(940, 538), (940, 730), (690, 730), (690, 538)],
}
FEEDBACK_LABELS = {
    ("N09", "N08"): "失败后回到构建",
    ("N10", "N08"): "检查发现问题后修复",
}


def load_graph():
    graph = json.loads((s.ROOT / "tasks/A06-dependency-graph/inputs/graph.json").read_text(encoding="utf-8"))
    assert len(graph["nodes"]) == 14
    assert len(graph["solid_edges"]) == 16 and len(graph["feedback_edges"]) == 2
    assert set(SOLID_ROUTES) == {tuple(edge) for edge in graph["solid_edges"]}
    assert set(FEEDBACK_ROUTES) == {tuple(edge) for edge in graph["feedback_edges"]}
    return graph


def topology(graph):
    ids = [node["id"] for node in graph["nodes"]]
    incoming = {node_id: [] for node_id in ids}
    outgoing = {node_id: [] for node_id in ids}
    for source, target in graph["solid_edges"]:
        outgoing[source].append(target)
        incoming[target].append(source)
    indegree = {node_id: len(incoming[node_id]) for node_id in ids}
    ready = [node_id for node_id in ids if indegree[node_id] == 0]
    order = []
    while ready:
        node_id = ready.pop(0)
        order.append(node_id)
        for target in outgoing[node_id]:
            indegree[target] -= 1
            if indegree[target] == 0:
                ready.append(target)
    assert len(order) == len(ids), "solid_edges must be a DAG"
    layer = {}
    longest_to = {}
    for node_id in order:
        layer[node_id] = 0 if not incoming[node_id] else max(layer[parent] + 1 for parent in incoming[node_id])
        candidates = [longest_to[parent] + [node_id] for parent in incoming[node_id]]
        longest_to[node_id] = max(candidates, key=len) if candidates else [node_id]
    longest = max(longest_to.values(), key=len)
    expected_layers = {
        "N01": 0, "N02": 1, "N03": 1, "N04": 2, "N05": 2, "N06": 3,
        "N07": 3, "N08": 4, "N09": 5, "N10": 6, "N11": 7, "N12": 8,
        "N13": 9, "N14": 10,
    }
    assert layer == expected_layers
    assert len(longest) == 11
    return ids, incoming, outgoing, layer, order, longest


def node_box(node_id):
    x, y = CENTERS[node_id]
    return [x - NODE_W / 2, y - NODE_H / 2, x + NODE_W / 2, y + NODE_H / 2]


def direction(path):
    x1, y1 = path[-2]
    x2, y2 = path[-1]
    if x2 > x1:
        return "RIGHT"
    if x2 < x1:
        return "LEFT"
    if y2 > y1:
        return "DOWN"
    return "UP"


def arrow(tip, heading, color, size=9):
    x, y = tip
    if heading == "RIGHT":
        a, b = (x - size, y - 5), (x - size, y + 5)
    elif heading == "LEFT":
        a, b = (x + size, y - 5), (x + size, y + 5)
    elif heading == "DOWN":
        a, b = (x - 5, y - size), (x + 5, y - size)
    else:
        a, b = (x - 5, y + size), (x + 5, y + size)
    return [s.line(a[0], a[1], x, y, color, 2), s.line(b[0], b[1], x, y, color, 2)]


def dashed_segment(x1, y1, x2, y2, color, thickness=2, dash=10, gap=7):
    length = math.hypot(x2 - x1, y2 - y1)
    if not length:
        return []
    ux, uy = (x2 - x1) / length, (y2 - y1) / length
    result = []
    distance = 0.0
    while distance < length:
        end = min(distance + dash, length)
        result.append(s.line(x1 + ux * distance, y1 + uy * distance, x1 + ux * end, y1 + uy * end, color, thickness))
        distance += dash + gap
    return result


def dashed_path(path, color="#BE123C"):
    result = []
    for a, b in zip(path, path[1:]):
        result.extend(dashed_segment(a[0], a[1], b[0], b[1], color))
    return result


def point_segment_distance(point, a, b):
    px, py = point
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    if dx == dy == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def segment_intersection(a, b, c, d):
    # All routes are orthogonal. Return a point only for a proper interior crossing.
    def horizontal(p, q):
        return p[1] == q[1]
    if horizontal(a, b) and not horizontal(c, d):
        h1, h2, v1, v2 = a, b, c, d
    elif horizontal(c, d) and not horizontal(a, b):
        h1, h2, v1, v2 = c, d, a, b
    else:
        return None
    hx1, hx2 = sorted([h1[0], h2[0]])
    vy1, vy2 = sorted([v1[1], v2[1]])
    x, y = v1[0], h1[1]
    if hx1 < x < hx2 and vy1 < y < vy2:
        return [x, y]
    return None


def audit(graph):
    ids, incoming, outgoing, layer, order, longest = topology(graph)
    nodes = []
    labels = {node["id"]: node["label"] for node in graph["nodes"]}
    for node_id in ids:
        nodes.append({
            "id": node_id, "label": labels[node_id], "topological_layer": layer[node_id],
            "in_neighbors": incoming[node_id], "out_neighbors": outgoing[node_id],
            "pixel_box": node_box(node_id), "pixel_center": list(CENTERS[node_id]),
        })
    prerequisite_edges = []
    for index, (source, target) in enumerate(graph["solid_edges"], 1):
        path = SOLID_ROUTES[(source, target)]
        prerequisite_edges.append({
            "edge_id": f"S{index:02d}", "from": source, "to": target, "style": "SOLID", "path": path,
            "arrow_position": path[-1], "arrow_direction": direction(path),
            "layout_rule": "target topological layer > source topological layer",
        })
    feedback_edges = []
    for index, (source, target) in enumerate(graph["feedback_edges"], 1):
        item = {
            "edge_id": f"F{index:02d}", "from": source, "to": target, "style": "DASHED", "path": FEEDBACK_ROUTES[(source, target)],
            "arrow_position": FEEDBACK_ROUTES[(source, target)][-1],
            "arrow_direction": direction(FEEDBACK_ROUTES[(source, target)]),
            "participates_in_dag": False, "annotation": FEEDBACK_LABELS[(source, target)],
        }
        if source == "N09":
            item["crossing_gap"] = {"at": [690, 590], "gap_x": [682, 698], "reason": "与 F02 交叉但无连接点"}
        feedback_edges.append(item)
    crossings = []
    all_routes = [(f"S{i:02d}", a, b, path) for i, ((a, b), path) in enumerate(SOLID_ROUTES.items(), 1)]
    all_routes += [(f"F{i:02d}", a, b, path) for i, ((a, b), path) in enumerate(FEEDBACK_ROUTES.items(), 1)]
    for i, (id1, src1, dst1, path1) in enumerate(all_routes):
        for id2, src2, dst2, path2 in all_routes[i + 1:]:
            for a, b in zip(path1, path1[1:]):
                for c, d in zip(path2, path2[1:]):
                    point = segment_intersection(a, b, c, d)
                    if point and not any(item["position"] == point for item in crossings):
                        crossings.append({"edges": [id1, id2], "position": point, "junction": False})
    # Verify no routed segment passes through the interior of an unrelated node.
    for source, target in graph["solid_edges"] + graph["feedback_edges"]:
        path = SOLID_ROUTES.get((source, target), FEEDBACK_ROUTES.get((source, target)))
        for a, b in zip(path, path[1:]):
            for node_id in ids:
                if node_id in (source, target):
                    continue
                left, top, right, bottom = node_box(node_id)
                if a[1] == b[1] and top < a[1] < bottom and max(min(a[0], b[0]), left) < min(max(a[0], b[0]), right):
                    raise AssertionError(f"{source}->{target} crosses node {node_id}")
                if a[0] == b[0] and left < a[0] < right and max(min(a[1], b[1]), top) < min(max(a[1], b[1]), bottom):
                    raise AssertionError(f"{source}->{target} crosses node {node_id}")
    result = s.audit_identity(TASK)
    result.update({
        "source": "inputs/graph.json",
        "nodes": nodes,
        "prerequisite_edges": prerequisite_edges,
        "longest_path": {
            "path": longest, "length_nodes": len(longest),
            "method": "Kahn topological order followed by dynamic programming: L[v]=1+max(L[u]) over solid predecessors; feedback excluded",
        },
        "feedback_edges": feedback_edges,
        "topological_order": order,
        "topological_layers": [sorted([node_id for node_id in ids if layer[node_id] == index]) for index in range(max(layer.values()) + 1)],
        "crossings": crossings,
        "crossing_rule": "Only arrow endpoints on node boxes are connections; line crossings have no junction dot",
        "coordinate_system": "canvas top-left origin; x right, y down; pixels; boxes [left,top,right,bottom]",
        "counts": {"nodes": 14, "solid_edges": 16, "feedback_edges": 2, "topological_layers": 11},
    })
    return result


def build_dsl(graph):
    c = []
    c.append(s.label("DEPENDENCY / REPRODUCIBLE DELIVERY", 32, 20, 800, 26, 18, "#52627A", True))
    c.append(s.label("从需求到可复现交付", 32, 50, 900, 56, 44, "#13233A", True))
    c.append(s.label("14 个节点  ·  16 条有向先决  ·  2 条独立反馈  ·  左到右不指向过去层", 32, 116, 1050, 32, 22, "#52627A"))
    # Header legend.
    c.append(s.line(1160, 60, 1210, 60, "#334155", 3))
    c.extend(arrow((1210, 60), "RIGHT", "#334155", 8))
    c.append(s.label("先决依赖", 1222, 47, 160, 28, 18, "#334155", True))
    c.extend(dashed_path([(1160, 96), (1210, 96)], "#BE123C"))
    c.extend(arrow((1210, 96), "RIGHT", "#BE123C", 8))
    c.append(s.label("反馈（不参与 DAG）", 1222, 83, 300, 28, 18, "#BE123C", True))
    # Layer guides.
    for index, name in enumerate(LAYER_NAMES):
        x = 100 + 140 * index
        c.append(s.label(f"L{index}", x - 60, 174, 120, 26, 18, "#64748B", True, "CENTER"))
        c.append(s.label(name, x - 66, 202, 132, 28, 18, "#334155", True, "CENTER"))
        c.append(s.line(x, 238, x, 758, "#E2E8F0", 1))
    # Solid prerequisite routes below nodes.
    for (source, target), path in SOLID_ROUTES.items():
        for a, b in zip(path, path[1:]):
            c.append(s.line(a[0], a[1], b[0], b[1], "#475569", 2))
        c.extend(arrow(path[-1], direction(path), "#334155"))
    # Feedback routes. F01 has a deliberate gap where it crosses F02.
    f1 = FEEDBACK_ROUTES[("N09", "N08")]
    for path in ([f1[0], f1[1], (700, 590)], [(680, 590), f1[2], f1[3]]):
        c.extend(dashed_path(path))
    c.extend(arrow(f1[-1], "UP", "#BE123C"))
    f2 = FEEDBACK_ROUTES[("N10", "N08")]
    c.extend(dashed_path(f2))
    c.extend(arrow(f2[-1], "UP", "#BE123C"))
    # Edge annotations.
    c.append(s.label("N04 数据计算也是产物校验的先决", 820, 254, 500, 26, 18, "#52627A", False, "CENTER"))
    c.append(s.label("失败后回到构建", 724, 552, 190, 26, 18, "#BE123C", True))
    c.append(s.label("检查发现问题后修复", 956, 686, 240, 26, 18, "#BE123C", True))
    # Nodes.
    labels = {node["id"]: node["label"] for node in graph["nodes"]}
    _, _, _, layer, _, _ = topology(graph)
    for node in graph["nodes"]:
        node_id = node["id"]
        x, y = CENTERS[node_id]
        left, top = x - NODE_W / 2, y - NODE_H / 2
        if node_id == "N14":
            fill, border, text_color = "#13233A", "#13233A", "#FFFFFF"
        elif layer[node_id] <= 3:
            fill, border, text_color = "#EAF2FF", "#4F46E5", "#172033"
        elif layer[node_id] <= 7:
            fill, border, text_color = "#E8F7F5", "#0F766E", "#172033"
        else:
            fill, border, text_color = "#F3EEFF", "#7C3AED", "#172033"
        c.append(s.box(left + 3, top + 4, NODE_W, NODE_H, "#DDE5EF", 10))
        c.append(s.box(left, top, NODE_W, NODE_H, fill, 10, border))
        c.append(s.label(node_id, left + 8, top + 7, NODE_W - 16, 28, 22, border if node_id != "N14" else "#FFFFFF", True, "CENTER"))
        c.append(s.label(labels[node_id], left + 5, top + 39, NODE_W - 10, 28, 22, text_color, True, "CENTER"))
    # Bottom explanation cards.
    c.append(s.box(32, 800, 760, 164, "#FFFFFF", 14, "#DCE4ED"))
    c.append(s.label("先决路径与反馈语义", 52, 818, 700, 30, 22, "#13233A", True))
    c.append(s.line(54, 872, 104, 872, "#475569", 3))
    c.extend(arrow((104, 872), "RIGHT", "#334155", 7))
    c.append(s.label("实线：有向先决", 116, 859, 210, 28, 18, "#475569"))
    c.extend(dashed_path([(330, 872), (380, 872)], "#BE123C"))
    c.extend(arrow((380, 872), "RIGHT", "#BE123C", 7))
    c.append(s.label("虚线：反馈，不参与拓扑排序", 392, 859, 360, 28, 18, "#BE123C"))
    c.append(s.label("最长先决路径（11 节点）", 52, 900, 300, 28, 18, "#13233A", True))
    c.append(s.label("N01→N02→N05→N06→N08→N09→N10→N11→N12→N13→N14", 52, 932, 720, 26, 18, "#334155"))
    c.append(s.box(816, 800, 752, 164, "#FFFFFF", 14, "#DCE4ED"))
    c.append(s.label("并行与跨层依赖", 836, 818, 700, 30, 22, "#13233A", True))
    c.append(s.label("N02 / N03 并行；N04 / N05 并行；N06 等待 N03 与 N05。", 836, 862, 700, 30, 18, "#334155"))
    c.append(s.label("N04→N13 为跨层先决；N06 与 N07 在 N08 构建前汇合。", 836, 902, 700, 30, 18, "#334155"))
    c.append(s.label("交叉线无连接点；F01/F02 不改变节点拓扑层。", 836, 934, 700, 26, 18, "#52627A"))
    return s.snapshot(1600, 1000, c, "#F5F7FB")


def main():
    s.begin_task(RUN_ID, TASK)
    graph = load_graph()
    out, tmp = s.task_dirs(RUN_ID, TASK)
    result = audit(graph)
    s.write_json(out / "graph-audit.json", result)
    s.write_json(tmp / "computed-graph.json", result)
    image, record = s.render(RUN_ID, TASK, build_dsl(graph), "dependency-map", sys.argv[1] if len(sys.argv) > 1 else "v001", kind="baseline")
    version = record["version_id"]
    s.write_json(tmp / f"{version}-response.json", record)
    print(image)


if __name__ == "__main__":
    main()
