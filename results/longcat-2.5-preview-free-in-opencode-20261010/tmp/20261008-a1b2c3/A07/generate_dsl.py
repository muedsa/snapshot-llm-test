#!/usr/bin/env python3
"""A07 - 三线换乘图与路线核验 DSL 生成器"""
import json
from pathlib import Path
from collections import deque

# 数据
stations = [
    {"id": "S01", "name": "松林", "accessible": True},
    {"id": "S02", "name": "北门", "accessible": True},
    {"id": "S03", "name": "书院", "accessible": False},
    {"id": "S04", "name": "中心", "accessible": True},
    {"id": "S05", "name": "东桥", "accessible": False},
    {"id": "S06", "name": "江湾", "accessible": True},
    {"id": "S07", "name": "西港", "accessible": True},
    {"id": "S08", "name": "工坊", "accessible": True},
    {"id": "S09", "name": "花园", "accessible": False},
    {"id": "S10", "name": "南门", "accessible": True},
    {"id": "S11", "name": "会展", "accessible": True},
    {"id": "S12", "name": "机场", "accessible": True},
    {"id": "S13", "name": "石溪", "accessible": True},
    {"id": "S14", "name": "公园", "accessible": False},
    {"id": "S15", "name": "剧院", "accessible": True},
    {"id": "S16", "name": "研究所", "accessible": True},
]

lines = [
    {"id": "R", "name": "红线", "stations": ["S01", "S02", "S03", "S04", "S05", "S06", "S12"]},
    {"id": "B", "name": "蓝线", "stations": ["S07", "S08", "S04", "S09", "S10", "S11"]},
    {"id": "G", "name": "绿线", "stations": ["S13", "S14", "S08", "S15", "S05", "S16"]},
]

queries = [
    {"from": "S01", "to": "S11"},
    {"from": "S13", "to": "S12"},
    {"from": "S07", "to": "S16"},
]

# 站点映射
station_map = {s["id"]: s for s in stations}

# 计算换乘站
transfer_stations = {}
for line in lines:
    for sid in line["stations"]:
        if sid not in transfer_stations:
            transfer_stations[sid] = []
        transfer_stations[sid].append(line["id"])

# 构建图
graph = {s["id"]: [] for s in stations}
for line in lines:
    for i in range(len(line["stations"]) - 1):
        s1, s2 = line["stations"][i], line["stations"][i + 1]
        graph[s1].append((s2, line["id"]))
        graph[s2].append((s1, line["id"]))

# BFS求最短路径
def bfs_shortest_path(start, end):
    queue = deque([(start, [], None)])
    visited = set()
    
    while queue:
        current, path, current_line = queue.popleft()
        if current == end:
            return path + [current]
        if current in visited:
            continue
        visited.add(current)
        
        for neighbor, line_id in graph[current]:
            if neighbor not in visited:
                queue.append((neighbor, path + [current], line_id))
    
    return None

# 计算路径详情
def get_path_details(path):
    if not path:
        return None
    
    segments = []
    current_line = None
    segment_start = path[0]
    
    for i in range(len(path) - 1):
        s1, s2 = path[i], path[i + 1]
        # 找到连接s1和s2的线路
        for line in lines:
            if s1 in line["stations"] and s2 in line["stations"]:
                idx1 = line["stations"].index(s1)
                idx2 = line["stations"].index(s2)
                if abs(idx1 - idx2) == 1:
                    line_id = line["id"]
                    break
        
        if current_line is None:
            current_line = line_id
            segment_start = s1
        elif line_id != current_line:
            segments.append({"line": current_line, "from": segment_start, "to": path[i]})
            current_line = line_id
            segment_start = s1
    
    segments.append({"line": current_line, "from": segment_start, "to": path[-1]})
    
    return {
        "path": path,
        "edges": len(path) - 1,
        "segments": segments,
        "transfers": len(segments) - 1
    }

# 计算所有查询的路径
routes = []
for q in queries:
    path = bfs_shortest_path(q["from"], q["to"])
    details = get_path_details(path)
    routes.append({
        "from": q["from"],
        "to": q["to"],
        "from_name": station_map[q["from"]]["name"],
        "to_name": station_map[q["to"]]["name"],
        **details
    })

# 保存routes.json
routes_data = {
    "routes": routes,
    "transfer_stations": {k: v for k, v in transfer_stations.items() if len(v) > 1}
}

output_dir = Path("outputs/20261008-a1b2c3/A07")
output_dir.mkdir(parents=True, exist_ok=True)
with open(output_dir / "routes.json", "w", encoding="utf-8") as f:
    json.dump(routes_data, f, ensure_ascii=False, indent=2)

# 颜色定义
BG = "#0F172A"
CARD_BG = "#1E293B"
CARD_BORDER = "#334155"
TEXT_PRIMARY = "#F1F5F9"
TEXT_SECONDARY = "#94A3B8"
COLOR_R = "#EF4444"
COLOR_B = "#3B82F6"
COLOR_G = "#10B981"

# 站点位置（按线路布局）
station_positions = {
    "S01": (100, 200),
    "S02": (250, 200),
    "S03": (400, 200),
    "S04": (550, 200),
    "S05": (700, 200),
    "S06": (850, 200),
    "S12": (1000, 200),
    "S07": (100, 500),
    "S08": (250, 500),
    "S09": (700, 500),
    "S10": (850, 500),
    "S11": (1000, 500),
    "S13": (100, 800),
    "S14": (250, 800),
    "S15": (550, 800),
    "S16": (1000, 800),
}

# ==================== 大图 DSL (1600x1000) ====================
lines_dsl = []
lines_dsl.append(f'<Snapshot background="{BG}" type="png">')
lines_dsl.append(f'  <Container width="1600" height="1000" padding="(20,24)">')
lines_dsl.append(f'    <Column crossAxisAlignment="START">')
lines_dsl.append(f'')
lines_dsl.append(f'      <!-- 标题 -->')
lines_dsl.append(f'      <Container width="1552" height="40" color="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}" padding="(10,14)">')
lines_dsl.append(f'        <Text color="{TEXT_PRIMARY}" fontSize="20" fontStyle="BOLD">虚构城市地铁示意图 · 三线换乘</Text>')
lines_dsl.append(f'      </Container>')
lines_dsl.append(f'')
lines_dsl.append(f'      <SizedBox height="10"/>')
lines_dsl.append(f'')
lines_dsl.append(f'      <!-- 地铁图 -->')
lines_dsl.append(f'      <Container width="1552" height="700" color="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}">')
lines_dsl.append(f'        <Stack>')

# 线路
for line in lines:
    color = COLOR_R if line["id"] == "R" else (COLOR_B if line["id"] == "B" else COLOR_G)
    for i in range(len(line["stations"]) - 1):
        s1, s2 = line["stations"][i], line["stations"][i + 1]
        x1, y1 = station_positions[s1]
        x2, y2 = station_positions[s2]
        lines_dsl.append(f'          <Positioned left="{x1}" top="{y1}" width="{x2-x1}" height="4">')
        lines_dsl.append(f'            <Container width="{x2-x1}" height="4" color="{color}"/>')
        lines_dsl.append(f'          </Positioned>')

# 站点
for s in stations:
    x, y = station_positions[s["id"]]
    is_transfer = len(transfer_stations.get(s["id"], [])) > 1
    border_color = "#F59E0B" if is_transfer else CARD_BORDER
    lines_dsl.append(f'          <Positioned left="{x}" top="{y}" width="60" height="40">')
    lines_dsl.append(f'            <Container width="60" height="40" color="{CARD_BG}" borderRadius="6" border="2 SOLID {border_color}">')
    lines_dsl.append(f'              <Column crossAxisAlignment="CENTER" mainAxisAlignment="CENTER">')
    lines_dsl.append(f'                <Text color="{TEXT_PRIMARY}" fontSize="12" fontStyle="BOLD">{s["id"]}</Text>')
    lines_dsl.append(f'                <Text color="{TEXT_PRIMARY}" fontSize="11">{s["name"]}</Text>')
    lines_dsl.append(f'              </Column>')
    lines_dsl.append(f'            </Container>')
    lines_dsl.append(f'          </Positioned>')

lines_dsl.append(f'        </Stack>')
lines_dsl.append(f'      </Container>')
lines_dsl.append(f'')
lines_dsl.append(f'      <!-- 图例 -->')
lines_dsl.append(f'      <Container width="1552" height="60" color="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}" padding="(10,14)">')
lines_dsl.append(f'        <Row crossAxisAlignment="CENTER">')
lines_dsl.append(f'          <Container width="30" height="4" color="{COLOR_R}"/>')
lines_dsl.append(f'          <SizedBox width="6"/>')
lines_dsl.append(f'          <Text color="{TEXT_SECONDARY}" fontSize="12">R 红线</Text>')
lines_dsl.append(f'          <SizedBox width="20"/>')
lines_dsl.append(f'          <Container width="30" height="4" color="{COLOR_B}"/>')
lines_dsl.append(f'          <SizedBox width="6"/>')
lines_dsl.append(f'          <Text color="{TEXT_SECONDARY}" fontSize="12">B 蓝线</Text>')
lines_dsl.append(f'          <SizedBox width="20"/>')
lines_dsl.append(f'          <Container width="30" height="4" color="{COLOR_G}"/>')
lines_dsl.append(f'          <SizedBox width="6"/>')
lines_dsl.append(f'          <Text color="{TEXT_SECONDARY}" fontSize="12">G 绿线</Text>')
lines_dsl.append(f'          <SizedBox width="20"/>')
lines_dsl.append(f'          <Container width="20" height="20" color="{CARD_BG}" borderRadius="4" border="2 SOLID #F59E0B"/>')
lines_dsl.append(f'          <SizedBox width="6"/>')
lines_dsl.append(f'          <Text color="{TEXT_SECONDARY}" fontSize="12">换乘站</Text>')
lines_dsl.append(f'          <SizedBox width="20"/>')
lines_dsl.append(f'          <Text color="{TEXT_SECONDARY}" fontSize="12">无障碍站：● 可乘车通过</Text>')
lines_dsl.append(f'        </Row>')
lines_dsl.append(f'      </Container>')
lines_dsl.append(f'')
lines_dsl.append(f'    </Column>')
lines_dsl.append(f'  </Container>')
lines_dsl.append(f'</Snapshot>')

dsl_map = "\n".join(lines_dsl)
with open(output_dir / "network-map.snapshot", "w", encoding="utf-8") as f:
    f.write(dsl_map)

# ==================== 小图 DSL (720x1280) ====================
lines_dsl = []
lines_dsl.append(f'<Snapshot background="{BG}" type="png">')
lines_dsl.append(f'  <Container width="720" height="1280" padding="(16,20)">')
lines_dsl.append(f'    <Column crossAxisAlignment="START">')
lines_dsl.append(f'')
lines_dsl.append(f'      <!-- 标题 -->')
lines_dsl.append(f'      <Container width="680" height="50" color="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}" padding="(10,14)">')
lines_dsl.append(f'        <Text color="{TEXT_PRIMARY}" fontSize="18" fontStyle="BOLD">旅行卡 · 三条路线</Text>')
lines_dsl.append(f'      </Container>')
lines_dsl.append(f'')
lines_dsl.append(f'      <SizedBox height="10"/>')
lines_dsl.append(f'')

for i, route in enumerate(routes):
    lines_dsl.append(f'      <!-- 路线{i+1} -->')
    lines_dsl.append(f'      <Container width="680" height="200" color="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}" padding="(12,14)">')
    lines_dsl.append(f'        <Column crossAxisAlignment="START">')
    lines_dsl.append(f'          <Row crossAxisAlignment="CENTER">')
    lines_dsl.append(f'            <Text color="{TEXT_PRIMARY}" fontSize="16" fontStyle="BOLD">路线{i+1}</Text>')
    lines_dsl.append(f'            <SizedBox width="10"/>')
    lines_dsl.append(f'            <Text color="{TEXT_SECONDARY}" fontSize="14">{route["from_name"]} → {route["to_name"]}</Text>')
    lines_dsl.append(f'          </Row>')
    lines_dsl.append(f'          <SizedBox height="8"/>')
    lines_dsl.append(f'          <Text color="{TEXT_SECONDARY}" fontSize="12">边数：{route["edges"]} · 换乘：{route["transfers"]}次</Text>')
    lines_dsl.append(f'          <SizedBox height="6"/>')
    lines_dsl.append(f'          <Text color="{TEXT_SECONDARY}" fontSize="12">路径：{" → ".join(route["path"])}</Text>')
    lines_dsl.append(f'          <SizedBox height="6"/>')
    for seg in route["segments"]:
        color = COLOR_R if seg["line"] == "R" else (COLOR_B if seg["line"] == "B" else COLOR_G)
        lines_dsl.append(f'          <Text color="{color}" fontSize="12">{seg["line"]}线：{seg["from"]} → {seg["to"]}</Text>')
    lines_dsl.append(f'        </Column>')
    lines_dsl.append(f'      </Container>')
    lines_dsl.append(f'      <SizedBox height="8"/>')
    lines_dsl.append(f'')

lines_dsl.append(f'    </Column>')
lines_dsl.append(f'  </Container>')
lines_dsl.append(f'</Snapshot>')

dsl_card = "\n".join(lines_dsl)
with open(output_dir / "travel-card.snapshot", "w", encoding="utf-8") as f:
    f.write(dsl_card)

print(f"Map DSL: {len(dsl_map)} chars")
print(f"Card DSL: {len(dsl_card)} chars")
for i, r in enumerate(routes):
    print(f"Route {i+1}: {r['from_name']} -> {r['to_name']}, edges={r['edges']}, transfers={r['transfers']}")
