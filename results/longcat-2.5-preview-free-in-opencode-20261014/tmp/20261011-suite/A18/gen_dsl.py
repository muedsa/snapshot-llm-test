import json, math
from pathlib import Path

W, H = 1600, 1000
FONT = "Noto Sans CJK SC"
BG = "#0F172A"
BLUE = "#3B82F6"
ORANGE = "#F59E0B"
GRAY = "#94A3B8"
NODE_COLOR = "#10B981"

# 15 units: 5 blue, 5 orange, 5 gray
units = []
for i in range(15):
    color = BLUE if i < 5 else (ORANGE if i < 10 else GRAY)
    units.append({"id": f"U{i+1:02d}", "color": color})

# 3 nodes
nodes = [{"id": "N01"}, {"id": "N02"}, {"id": "N03"}]

# Act 1: all units clustered around N01 (left-center)
# Act 2: all units spread out but still around N01, overlapping connections
# Act 3: units distributed among N01, N02, N03

dsl_parts = []
dsl_parts.append(f'<Snapshot type="png" background="{BG}">')
dsl_parts.append(f'  <Column mainAxisSize="MAX" height="{H}" width="{W}">')

# Title
dsl_parts.append(f'    <Container height="60" padding="(0,24)">')
dsl_parts.append(f'      <Text text="集中 → 过载 → 重新分配" color="#FFFFFF" fontSize="28" fontStyle="BOLD"/>')
dsl_parts.append(f'    </Container>')

# Three acts side by side
act_w = 500
for act_idx, act_name in enumerate(["集中", "过载", "重新分配"]):
    x_offset = 20 + act_idx * (act_w + 20)
    
    # Act label
    dsl_parts.append(f'    <Container height="40" width="{act_w}" padding="({x_offset},0)">')
    dsl_parts.append(f'      <Text text="第{act_idx+1}幕：{act_name}" color="#FFFFFF" fontSize="20" fontStyle="BOLD"/>')
    dsl_parts.append(f'    </Container>')
    
    # Nodes and units
    if act_idx == 0:
        # Act 1: all units around N01 at (250, 250)
        node_x, node_y = 200, 250
        for i, u in enumerate(units):
            angle = i * 2 * math.pi / 15
            ux = node_x + 120 * math.cos(angle)
            uy = node_y + 120 * math.sin(angle)
            u['x'] = round(ux)
            u['y'] = round(uy)
            u['node'] = 'N01'
        dsl_parts.append(f'    <Container width="{act_w}" height="800">')
        dsl_parts.append(f'      <Stack>')
        dsl_parts.append(f'        <Positioned left="{node_x}" top="{node_y}" width="60" height="60">')
        dsl_parts.append(f'          <Container color="{NODE_COLOR}" borderRadius="8"/>')
        dsl_parts.append(f'        </Positioned>')
        for u in units:
            dsl_parts.append(f'        <Positioned left="{u["x"]}" top="{u["y"]}" width="36" height="36">')
            dsl_parts.append(f'          <Container color="{u["color"]}" borderRadius="18"/>')
            dsl_parts.append(f'        </Positioned>')
        dsl_parts.append(f'      </Stack>')
        dsl_parts.append(f'    </Container>')
    
    elif act_idx == 1:
        # Act 2: units spread out, still around N01 but more dispersed
        node_x, node_y = 200, 400
        for i, u in enumerate(units):
            angle = i * 2 * math.pi / 15
            ux = node_x + 180 * math.cos(angle)
            uy = node_y + 180 * math.sin(angle)
            u['x'] = round(ux)
            u['y'] = round(uy)
            u['node'] = 'N01'
        dsl_parts.append(f'    <Container width="{act_w}" height="800">')
        dsl_parts.append(f'      <Stack>')
        dsl_parts.append(f'        <Positioned left="{node_x}" top="{node_y}" width="60" height="60">')
        dsl_parts.append(f'          <Container color="{NODE_COLOR}" borderRadius="8"/>')
        dsl_parts.append(f'        </Positioned>')
        for u in units:
            dsl_parts.append(f'        <Positioned left="{u["x"]}" top="{u["y"]}" width="36" height="36">')
            dsl_parts.append(f'          <Container color="{u["color"]}" borderRadius="18"/>')
            dsl_parts.append(f'        </Positioned>')
        dsl_parts.append(f'      </Stack>')
        dsl_parts.append(f'    </Container>')
    
    else:
        # Act 3: units distributed among 3 nodes
        node_positions = [(100, 200), (400, 200), (250, 500)]
        for i, u in enumerate(units):
            node_idx = i % 3
            angle = (i // 3) * 2 * math.pi / 5
            nx, ny = node_positions[node_idx]
            ux = nx + 80 * math.cos(angle)
            uy = ny + 80 * math.sin(angle)
            u['x'] = round(ux)
            u['y'] = round(uy)
            u['node'] = f'N{node_idx+1:02d}'
        
        dsl_parts.append(f'    <Container width="{act_w}" height="800">')
        dsl_parts.append(f'      <Stack>')
        for nx, ny in node_positions:
            dsl_parts.append(f'        <Positioned left="{nx}" top="{ny}" width="60" height="60">')
            dsl_parts.append(f'          <Container color="{NODE_COLOR}" borderRadius="8"/>')
            dsl_parts.append(f'        </Positioned>')
        for u in units:
            dsl_parts.append(f'        <Positioned left="{u["x"]}" top="{u["y"]}" width="36" height="36">')
            dsl_parts.append(f'          <Container color="{u["color"]}" borderRadius="18"/>')
            dsl_parts.append(f'        </Positioned>')
        dsl_parts.append(f'      </Stack>')
        dsl_parts.append(f'    </Container>')

dsl_parts.append('  </Column>')
dsl_parts.append('</Snapshot>')

dsl = '\n'.join(dsl_parts)
with open('tmp/20261011-suite/A18/three-act-story.snapshot', 'w', encoding='utf-8') as f:
    f.write(dsl)
print(f'Generated DSL: {len(dsl)} chars')

# Save story-audit.json
audit = {
    "schema_version": 1,
    "task_id": "A18",
    "path_base": "output_dir",
    "units": [{"id": u["id"], "color": u["color"], "diameter": 36} for u in units],
    "nodes": [{"id": n["id"], "shape": "rounded_square", "size": 60} for n in nodes],
    "acts": [
        {"act": 1, "name": "集中", "description": "所有单元围绕单一节点"},
        {"act": 2, "name": "过载", "description": "单元分散但仍指向单一节点"},
        {"act": 3, "name": "重新分配", "description": "单元分配到3个节点"}
    ]
}

output_dir = Path('outputs/20261011-suite/A18')
output_dir.mkdir(parents=True, exist_ok=True)
with open(output_dir / 'story-audit.json', 'w', encoding='utf-8') as f:
    json.dump(audit, f, ensure_ascii=False, indent=2)
print('Saved story-audit.json')
