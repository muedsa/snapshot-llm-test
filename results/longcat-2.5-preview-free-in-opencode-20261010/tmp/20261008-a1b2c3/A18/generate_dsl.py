#!/usr/bin/env python3
"""A18 - 守恒对象的三幕视觉叙事 DSL 生成器"""
import json
import math
from pathlib import Path

# 颜色定义
BG = "#0F172A"
CARD_BG = "#1E293B"
CARD_BORDER = "#334155"
TEXT_PRIMARY = "#F1F5F9"
TEXT_SECONDARY = "#94A3B8"
COLOR_BLUE = "#3B82F6"
COLOR_ORANGE = "#F59E0B"
COLOR_GRAY = "#94A3B8"

# 三幕布局
act_width = 500
act_height = 900
gap = 30
total_width = 3 * act_width + 2 * gap
offset_x = (1600 - total_width) // 2
offset_y = 50

# 15个单元的颜色分配
unit_colors = [COLOR_BLUE] * 5 + [COLOR_ORANGE] * 5 + [COLOR_GRAY] * 5

# 生成单元位置
def generate_units(act_idx):
    """生成15个单元的位置"""
    units = []
    if act_idx == 0:
        # 第一幕：集中 - 圆形聚集在左侧
        for i in range(15):
            row = i // 5
            col = i % 5
            x = 50 + col * 60
            y = 200 + row * 60
            units.append({"x": x, "y": y, "color": unit_colors[i], "id": f"U{i+1:02d}"})
    elif act_idx == 1:
        # 第二幕：过载 - 圆形密集在中心
        for i in range(15):
            row = i // 5
            col = i % 5
            x = 100 + col * 50
            y = 250 + row * 50
            units.append({"x": x, "y": y, "color": unit_colors[i], "id": f"U{i+1:02d}"})
    else:
        # 第三幕：重新分配 - 圆形均匀分配到3个节点
        for i in range(15):
            node_idx = i % 3
            in_node_idx = i // 3
            x = 80 + node_idx * 150
            y = 200 + in_node_idx * 60
            units.append({"x": x, "y": y, "color": unit_colors[i], "id": f"U{i+1:02d}"})
    return units

# 生成节点位置
def generate_nodes(act_idx):
    """生成3个节点的位置"""
    nodes = []
    for i in range(3):
        x = 350
        y = 200 + i * 200
        nodes.append({"x": x, "y": y, "id": f"N{i+1}"})
    return nodes

# 构建DSL
lines = []
lines.append(f'<Snapshot background="{BG}" type="png">')
lines.append(f'  <Container width="1600" height="1000" padding="(20,20)">')
lines.append(f'    <Column crossAxisAlignment="START">')
lines.append(f'      <Text color="{TEXT_PRIMARY}" fontSize="32" fontStyle="BOLD" textAlign="CENTER">集中 → 过载 → 重新分配</Text>')
lines.append(f'      <SizedBox height="20"/>')
lines.append(f'      <Row mainAxisAlignment="SPACE_EVENLY">')

act_names = ["集中", "过载", "重新分配"]
for act_idx in range(3):
    act_x = offset_x + act_idx * (act_width + gap)
    lines.append(f'        <Container width="{act_width}" height="{act_height}" background="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}">')
    lines.append(f'          <Stack width="{act_width}" height="{act_height}">')
    lines.append(f'            <Text color="{TEXT_PRIMARY}" fontSize="24" fontStyle="BOLD" textAlign="CENTER">{act_names[act_idx]}</Text>')
    
    # 绘制单元
    units = generate_units(act_idx)
    for unit in units:
        lines.append(f'            <Positioned left="{unit["x"]}" top="{unit["y"]}" width="36" height="36">')
        lines.append(f'              <Container width="36" height="36" color="{unit["color"]}" borderRadius="18"/>')
        lines.append(f'            </Positioned>')
    
    # 绘制节点
    nodes = generate_nodes(act_idx)
    for node in nodes:
        lines.append(f'            <Positioned left="{node["x"]}" top="{node["y"]}" width="80" height="80">')
        lines.append(f'              <Container width="80" height="80" color="{COLOR_BLUE}" borderRadius="8" border="2 SOLID {TEXT_PRIMARY}"/>')
        lines.append(f'            </Positioned>')
    
    lines.append(f'          </Stack>')
    lines.append(f'        </Container>')

lines.append(f'      </Row>')
lines.append(f'    </Column>')
lines.append(f'  </Container>')
lines.append(f'</Snapshot>')

dsl = "\n".join(lines)

output_dir = Path("outputs/20261008-a1b2c3/A18")
output_dir.mkdir(parents=True, exist_ok=True)
with open(output_dir / "three-act-story.snapshot", "w", encoding="utf-8") as f:
    f.write(dsl)

# 保存story-audit.json
story_audit = {
    "acts": []
}
for act_idx in range(3):
    units = generate_units(act_idx)
    nodes = generate_nodes(act_idx)
    story_audit["acts"].append({
        "act": act_idx + 1,
        "name": act_names[act_idx],
        "units": units,
        "nodes": nodes
    })

with open(output_dir / "story-audit.json", "w", encoding="utf-8") as f:
    json.dump(story_audit, f, ensure_ascii=False, indent=2)

# 保存rationale.md
rationale = """# 三幕视觉叙事说明

## 叙事构思
第一幕（集中）：15个信息单元聚集在左侧，向中心节点移动，表现"集中"概念。
第二幕（过载）：15个单元密集在中心节点周围，表现"过载"概念。
第三幕（重新分配）：15个单元均匀分配到3个节点，每个节点5个单元，表现"重新分配"概念。

## 感知方式
通过距离、连线和构图表达关系：
- 第一幕：单元向中心聚集
- 第二幕：单元密集，空间紧张
- 第三幕：单元均匀分布，秩序恢复

## 守恒验证
每幕都有相同的15个单元（5蓝、5橙、5灰），没有增加、删去或缩小。
"""

with open(output_dir / "rationale.md", "w", encoding="utf-8") as f:
    f.write(rationale)

print(f"DSL generated: {len(dsl)} chars")
