#!/usr/bin/env python3
"""A06 - 十四节点依赖图与反馈回路 DSL 生成器"""
import json
import math
from pathlib import Path

# 数据
nodes = [
    {"id": "N01", "label": "需求冻结"},
    {"id": "N02", "label": "输入检查"},
    {"id": "N03", "label": "字体查询"},
    {"id": "N04", "label": "数据计算"},
    {"id": "N05", "label": "内容规划"},
    {"id": "N06", "label": "版式系统"},
    {"id": "N07", "label": "图表生成"},
    {"id": "N08", "label": "DSL构建"},
    {"id": "N09", "label": "首轮渲染"},
    {"id": "N10", "label": "视觉检查"},
    {"id": "N11", "label": "问题修复"},
    {"id": "N12", "label": "回归渲染"},
    {"id": "N13", "label": "产物校验"},
    {"id": "N14", "label": "交付归档"},
]

solid_edges = [
    ["N01", "N02"], ["N01", "N03"], ["N02", "N04"], ["N02", "N05"],
    ["N03", "N06"], ["N05", "N06"], ["N04", "N07"], ["N06", "N08"],
    ["N07", "N08"], ["N08", "N09"], ["N09", "N10"], ["N10", "N11"],
    ["N11", "N12"], ["N12", "N13"], ["N13", "N14"], ["N04", "N13"]
]

feedback_edges = [
    ["N09", "N08"], ["N10", "N08"]
]

# 计算拓扑层
def compute_layers(nodes, solid_edges):
    node_map = {n["id"]: n for n in nodes}
    in_degree = {n["id"]: 0 for n in nodes}
    for e in solid_edges:
        in_degree[e[1]] += 1
    
    layers = []
    remaining = set(n["id"] for n in nodes)
    
    while remaining:
        layer = [nid for nid in remaining if in_degree[nid] == 0]
        if not layer:
            break
        layers.append(layer)
        for nid in layer:
            remaining.remove(nid)
            for e in solid_edges:
                if e[0] == nid:
                    in_degree[e[1]] -= 1
    
    return layers

layers = compute_layers(nodes, solid_edges)

# 计算入/出邻居
def compute_neighbors(nodes, solid_edges):
    in_neighbors = {n["id"]: [] for n in nodes}
    out_neighbors = {n["id"]: [] for n in nodes}
    for e in solid_edges:
        out_neighbors[e[0]].append(e[1])
        in_neighbors[e[1]].append(e[0])
    return in_neighbors, out_neighbors

in_neighbors, out_neighbors = compute_neighbors(nodes, solid_edges)

# 计算最长路径
def longest_path(nodes, solid_edges):
    node_map = {n["id"]: n for n in nodes}
    dist = {n["id"]: 1 for n in nodes}
    prev = {n["id"]: None for n in nodes}
    
    # 按拓扑顺序处理
    layers = compute_layers(nodes, solid_edges)
    for layer in layers:
        for nid in layer:
            for e in solid_edges:
                if e[0] == nid:
                    if dist[e[1]] < dist[nid] + 1:
                        dist[e[1]] = dist[nid] + 1
                        prev[e[1]] = nid
    
    # 找到最长路径的终点
    max_dist = max(dist.values())
    end_node = max(dist, key=dist.get)
    
    # 回溯路径
    path = []
    current = end_node
    while current:
        path.append(current)
        current = prev[current]
    path.reverse()
    
    return path, max_dist

max_path, max_len = longest_path(nodes, solid_edges)

# 保存graph-audit.json
audit = {
    "nodes": nodes,
    "layers": layers,
    "in_neighbors": in_neighbors,
    "out_neighbors": out_neighbors,
    "longest_path": max_path,
    "longest_path_length": max_len,
    "feedback_edges": feedback_edges
}

output_dir = Path("outputs/20261008-a1b2c3/A06")
output_dir.mkdir(parents=True, exist_ok=True)
with open(output_dir / "graph-audit.json", "w", encoding="utf-8") as f:
    json.dump(audit, f, ensure_ascii=False, indent=2)

# 颜色定义
BG = "#0F172A"
CARD_BG = "#1E293B"
CARD_BORDER = "#334155"
TEXT_PRIMARY = "#F1F5F9"
TEXT_SECONDARY = "#94A3B8"
COLOR_EDGE = "#64748B"
COLOR_FEEDBACK = "#F59E0B"
COLOR_NODE = "#3B82F6"

# 节点位置（按拓扑层排列）
# 层0: N01
# 层1: N02, N03
# 层2: N04, N05, N06
# 层3: N07, N08
# 层4: N09
# 层5: N10
# 层6: N11
# 层7: N12
# 层8: N13
# 层9: N14

node_positions = {
    "N01": (100, 450),
    "N02": (300, 300),
    "N03": (300, 600),
    "N04": (500, 200),
    "N05": (500, 400),
    "N06": (500, 600),
    "N07": (700, 200),
    "N08": (700, 500),
    "N09": (900, 400),
    "N10": (1100, 400),
    "N11": (1300, 400),
    "N12": (1300, 600),
    "N13": (1100, 600),
    "N14": (1300, 750),
}

# 构建DSL
lines = []
lines.append(f'<Snapshot background="{BG}" type="png">')
lines.append(f'  <Container width="1600" height="1000" padding="(20,24)">')
lines.append(f'    <Column crossAxisAlignment="START">')
lines.append(f'')
lines.append(f'      <!-- 标题 -->')
lines.append(f'      <Container width="1552" height="40" color="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}" padding="(10,14)">')
lines.append(f'        <Text color="{TEXT_PRIMARY}" fontSize="20" fontStyle="BOLD">从需求到可复现交付 · 依赖解释图</Text>')
lines.append(f'      </Container>')
lines.append(f'')
lines.append(f'      <SizedBox height="10"/>')
lines.append(f'')
lines.append(f'      <!-- 依赖图 -->')
lines.append(f'      <Container width="1552" height="700" color="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}">')
lines.append(f'        <Stack>')

# 先决边（实线）
for e in solid_edges:
    n1, n2 = e
    x1, y1 = node_positions[n1]
    x2, y2 = node_positions[n2]
    # 计算线段
    dx = x2 - x1
    dy = y2 - y1
    length = (dx*dx + dy*dy) ** 0.5
    angle = math.degrees(math.atan2(dy, dx))
    lines.append(f'          <Positioned left="{x1}" top="{y1}" width="{length}" height="2">')
    lines.append(f'            <Transform matrix="(1,0,0,0,1,0,0,0,0,0,1,0,0,0,0,1)" alignment="CENTER">')
    lines.append(f'              <Container width="{length}" height="2" color="{COLOR_EDGE}"/>')
    lines.append(f'            </Transform>')
    lines.append(f'          </Positioned>')

# 反馈边（虚线效果：用多个小段表示）
for e in feedback_edges:
    n1, n2 = e
    x1, y1 = node_positions[n1]
    x2, y2 = node_positions[n2]
    dx = x2 - x1
    dy = y2 - y1
    length = (dx*dx + dy*dy) ** 0.5
    # 用多个小段表示虚线
    dash_length = 10
    gap_length = 5
    num_dashes = int(length / (dash_length + gap_length))
    for i in range(num_dashes):
        start = i * (dash_length + gap_length)
        lines.append(f'          <Positioned left="{x1 + start}" top="{y1}" width="{dash_length}" height="2">')
        lines.append(f'            <Container width="{dash_length}" height="2" color="{COLOR_FEEDBACK}"/>')
        lines.append(f'          </Positioned>')

# 节点
for n in nodes:
    x, y = node_positions[n["id"]]
    lines.append(f'          <Positioned left="{x}" top="{y}" width="80" height="50">')
    lines.append(f'            <Container width="80" height="50" color="{COLOR_NODE}" borderRadius="8" border="1 SOLID {CARD_BORDER}">')
    lines.append(f'              <Column crossAxisAlignment="CENTER" mainAxisAlignment="CENTER">')
    lines.append(f'                <Text color="{TEXT_PRIMARY}" fontSize="12" fontStyle="BOLD">{n["id"]}</Text>')
    lines.append(f'                <Text color="{TEXT_PRIMARY}" fontSize="11">{n["label"]}</Text>')
    lines.append(f'              </Column>')
    lines.append(f'            </Container>')
    lines.append(f'          </Positioned>')

lines.append(f'        </Stack>')
lines.append(f'      </Container>')
lines.append(f'')
lines.append(f'      <!-- 图例和说明 -->')
lines.append(f'      <Container width="1552" height="80" color="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}" padding="(10,14)">')
lines.append(f'        <Row crossAxisAlignment="CENTER">')
lines.append(f'          <Container width="30" height="2" color="{COLOR_EDGE}"/>')
lines.append(f'          <SizedBox width="6"/>')
lines.append(f'          <Text color="{TEXT_SECONDARY}" fontSize="12">先决依赖</Text>')
lines.append(f'          <SizedBox width="20"/>')
lines.append(f'          <Container width="30" height="2" color="{COLOR_FEEDBACK}"/>')
lines.append(f'          <SizedBox width="6"/>')
lines.append(f'          <Text color="{TEXT_SECONDARY}" fontSize="12">反馈关系</Text>')
lines.append(f'          <SizedBox width="20"/>')
lines.append(f'          <Text color="{TEXT_SECONDARY}" fontSize="12">失败后回到构建：N09→N08</Text>')
lines.append(f'          <SizedBox width="20"/>')
lines.append(f'          <Text color="{TEXT_SECONDARY}" fontSize="12">检查发现问题后修复：N10→N08</Text>')
lines.append(f'        </Row>')
lines.append(f'      </Container>')
lines.append(f'')
lines.append(f'    </Column>')
lines.append(f'  </Container>')
lines.append(f'</Snapshot>')

dsl = "\n".join(lines)
with open(output_dir / "dependency-map.snapshot", "w", encoding="utf-8") as f:
    f.write(dsl)

print(f"DSL generated: {len(dsl)} chars")
print(f"Layers: {len(layers)}")
print(f"Longest path: {max_path} (length: {max_len})")
