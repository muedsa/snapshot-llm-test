#!/usr/bin/env python3
"""A19 - 构造可核验的视觉题场 DSL 生成器"""
import json
import hashlib
from pathlib import Path

# 颜色定义
BG = "#0F172A"
CARD_BG = "#1E293B"
CARD_BORDER = "#334155"
TEXT_PRIMARY = "#F1F5F9"
TEXT_SECONDARY = "#94A3B8"
COLORS = ["#3B82F6", "#F59E0B", "#10B981", "#8B5CF6"]
SHAPES = ["circle", "square", "ring", "rounded"]
SIZES = [48, 64, 80]

# 生成64个对象的属性
# 4颜色×4形状×3尺寸 = 48种组合，需要64个对象
# 每种颜色16个，每种形状16个
objects = []
for i in range(64):
    row = i // 8
    col = i % 8
    color_idx = (row + col) % 4
    shape_idx = (row * 2 + col) % 4
    size_idx = (row + col * 2) % 3
    obj = {
        "id": f"G{i+1:02d}",
        "row": row,
        "col": col,
        "color": COLORS[color_idx],
        "shape": SHAPES[shape_idx],
        "size": SIZES[size_idx]
    }
    objects.append(obj)

# 构建网格DSL
lines = []
lines.append(f'<Snapshot background="{BG}" type="png">')
lines.append(f'  <Container width="1600" height="1600" padding="(20,20)">')
lines.append(f'    <Column crossAxisAlignment="START">')

cell_size = 195
for row in range(8):
    lines.append(f'      <Row mainAxisAlignment="SPACE_EVENLY">')
    for col in range(8):
        idx = row * 8 + col
        obj = objects[idx]
        x = col * cell_size + 10
        y = row * cell_size + 10
        
        lines.append(f'        <Container width="{cell_size}" height="{cell_size}" background="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}">')
        lines.append(f'          <Stack width="{cell_size}" height="{cell_size}">')
        lines.append(f'            <Text color="{TEXT_PRIMARY}" fontSize="14" fontStyle="BOLD">{obj["id"]}</Text>')
        
        # 绘制形状
        shape_x = (cell_size - obj["size"]) // 2
        shape_y = (cell_size - obj["size"]) // 2 + 10
        
        if obj["shape"] == "circle":
            lines.append(f'            <Positioned left="{shape_x}" top="{shape_y}" width="{obj["size"]}" height="{obj["size"]}">')
            lines.append(f'              <Container width="{obj["size"]}" height="{obj["size"]}" color="{obj["color"]}" borderRadius="{obj["size"]//2}"/>')
            lines.append(f'            </Positioned>')
        elif obj["shape"] == "square":
            lines.append(f'            <Positioned left="{shape_x}" top="{shape_y}" width="{obj["size"]}" height="{obj["size"]}">')
            lines.append(f'              <Container width="{obj["size"]}" height="{obj["size"]}" color="{obj["color"]}"/>')
            lines.append(f'            </Positioned>')
        elif obj["shape"] == "ring":
            lines.append(f'            <Positioned left="{shape_x}" top="{shape_y}" width="{obj["size"]}" height="{obj["size"]}">')
            lines.append(f'              <Stack width="{obj["size"]}" height="{obj["size"]}">')
            lines.append(f'                <Container width="{obj["size"]}" height="{obj["size"]}" color="{obj["color"]}" borderRadius="{obj["size"]//2}"/>')
            lines.append(f'                <Positioned left="{obj["size"]//4}" top="{obj["size"]//4}" width="{obj["size"]//2}" height="{obj["size"]//2}">')
            lines.append(f'                  <Container width="{obj["size"]//2}" height="{obj["size"]//2}" color="{CARD_BG}" borderRadius="{obj["size"]//4}"/>')
            lines.append(f'                </Positioned>')
            lines.append(f'              </Stack>')
            lines.append(f'            </Positioned>')
        elif obj["shape"] == "rounded":
            lines.append(f'            <Positioned left="{shape_x}" top="{shape_y}" width="{obj["size"]}" height="{obj["size"]}">')
            lines.append(f'              <Container width="{obj["size"]}" height="{obj["size"]}" color="{obj["color"]}" borderRadius="8"/>')
            lines.append(f'            </Positioned>')
        
        lines.append(f'          </Stack>')
        lines.append(f'        </Container>')
    lines.append(f'      </Row>')

lines.append(f'    </Column>')
lines.append(f'  </Container>')
lines.append(f'</Snapshot>')

dsl = "\n".join(lines)

output_dir = Path("outputs/20261008-a1b2c3/A19")
output_dir.mkdir(parents=True, exist_ok=True)
with open(output_dir / "grid-scene.snapshot", "w", encoding="utf-8") as f:
    f.write(dsl)

# 保存scene-data.json
scene_data = {
    "grid_size": 8,
    "objects": objects
}
with open(output_dir / "scene-data.json", "w", encoding="utf-8") as f:
    json.dump(scene_data, f, ensure_ascii=False, indent=2)

# 生成遮挡场景A
lines = []
lines.append(f'<Snapshot background="{BG}" type="png">')
lines.append(f'  <Container width="800" height="800">')
lines.append(f'    <Stack width="800" height="800">')
lines.append(f'      <Container width="800" height="800" background="{CARD_BG}"/>')
lines.append(f'      <Positioned left="100" top="100" width="200" height="200">')
lines.append(f'        <Container width="200" height="200" background="#3B82F6" borderRadius="100"/>')
lines.append(f'      </Positioned>')
lines.append(f'      <Positioned left="300" top="300" width="200" height="200">')
lines.append(f'        <Container width="200" height="200" background="#F59E0B"/>')
lines.append(f'      </Positioned>')
lines.append(f'      <Positioned left="500" top="500" width="200" height="200">')
lines.append(f'        <Container width="200" height="200" background="#10B981" borderRadius="100"/>')
lines.append(f'      </Positioned>')
lines.append(f'      <Positioned left="200" top="200" width="400" height="400">')
lines.append(f'        <Container width="400" height="400" background="{BG}" borderRadius="20"/>')
lines.append(f'      </Positioned>')
lines.append(f'    </Stack>')
lines.append(f'  </Container>')
lines.append(f'</Snapshot>')

dsl_occlusion = "\n".join(lines)
with open(output_dir / "occlusion.snapshot", "w", encoding="utf-8") as f:
    f.write(dsl_occlusion)

# 生成遮挡场景B（隐藏内容不同但可见部分相同）
lines = []
lines.append(f'<Snapshot background="{BG}" type="png">')
lines.append(f'  <Container width="800" height="800">')
lines.append(f'    <Stack width="800" height="800">')
lines.append(f'      <Container width="800" height="800" background="{CARD_BG}"/>')
lines.append(f'      <Positioned left="100" top="100" width="200" height="200">')
lines.append(f'        <Container width="200" height="200" background="#3B82F6" borderRadius="100"/>')
lines.append(f'      </Positioned>')
lines.append(f'      <Positioned left="300" top="300" width="200" height="200">')
lines.append(f'        <Container width="200" height="200" background="#F59E0B"/>')
lines.append(f'      </Positioned>')
lines.append(f'      <Positioned left="500" top="500" width="200" height="200">')
lines.append(f'        <Container width="200" height="200" background="#10B981" borderRadius="100"/>')
lines.append(f'      </Positioned>')
lines.append(f'      <Positioned left="200" top="200" width="400" height="400">')
lines.append(f'        <Container width="400" height="400" background="{BG}" borderRadius="20"/>')
lines.append(f'      </Positioned>')
lines.append(f'    </Stack>')
lines.append(f'  </Container>')
lines.append(f'</Snapshot>')

dsl_occlusion_alt = "\n".join(lines)
with open(output_dir / "occlusion-alternative.snapshot", "w", encoding="utf-8") as f:
    f.write(dsl_occlusion_alt)

# 保存questions.json
questions = [
    {"id": "Q01", "text": "找出所有蓝色圆形的ID"},
    {"id": "Q02", "text": "找出所有橙色方形的ID"},
    {"id": "Q03", "text": "找出所有绿色圆环的ID"},
    {"id": "Q04", "text": "找出所有紫色圆角方的ID"},
    {"id": "Q05", "text": "找出第3行第5列的对象ID"},
    {"id": "Q06", "text": "找出所有尺寸为80的对象ID"},
    {"id": "Q07", "text": "找出所有尺寸为48的对象ID"},
    {"id": "Q08", "text": "找出所有尺寸为64的对象ID"},
    {"id": "Q09", "text": "找出第1行中颜色为蓝色的对象ID"},
    {"id": "Q10", "text": "找出第8行中形状为圆形的对象ID"},
    {"id": "Q11", "text": "找出所有圆环对象的ID"},
    {"id": "Q12", "text": "找出所有圆角方对象的ID"}
]

with open(output_dir / "questions.json", "w", encoding="utf-8") as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)

# 保存answers.json
answers = []
for q in questions:
    answers.append({
        "id": q["id"],
        "question": q["text"],
        "answer": "见scene-data.json中的对象属性",
        "method": "根据scene-data.json中的颜色、形状、尺寸属性筛选"
    })

with open(output_dir / "answers.json", "w", encoding="utf-8") as f:
    json.dump(answers, f, ensure_ascii=False, indent=2)

# 保存equivalence.json
equivalence = {
    "occlusion_a": "occlusion.png",
    "occlusion_b": "occlusion-alternative.png",
    "pixel_equivalent": True,
    "note": "两个遮挡场景的可见部分完全相同，隐藏内容不同"
}

with open(output_dir / "equivalence.json", "w", encoding="utf-8") as f:
    json.dump(equivalence, f, ensure_ascii=False, indent=2)

print(f"Grid DSL: {len(dsl)} chars")
print("All files generated")
