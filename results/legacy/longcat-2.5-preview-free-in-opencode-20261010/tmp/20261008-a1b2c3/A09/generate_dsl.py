#!/usr/bin/env python3
"""A09 - 十二个非对称图形变换标本 DSL 生成器"""
import json
import math
from pathlib import Path

# 数据
stamp = {
    "size": [120, 120],
    "pivot": [60, 60],
    "rectangles": [
        {"xywh": [8, 8, 28, 92], "color": "#E54B4B"},
        {"xywh": [36, 72, 68, 28], "color": "#2364DB"},
        {"xywh": [64, 8, 40, 28], "color": "#EAB53B"}
    ],
    "dot": {"center": [91, 49], "radius": 8, "color": "#111111"}
}

transforms = [
    {"id": "T01", "operations": [["rotate_clockwise_deg", 0]]},
    {"id": "T02", "operations": [["rotate_clockwise_deg", 90]]},
    {"id": "T03", "operations": [["rotate_clockwise_deg", 180]]},
    {"id": "T04", "operations": [["rotate_clockwise_deg", 270]]},
    {"id": "T05", "operations": [["mirror_horizontal", True]]},
    {"id": "T06", "operations": [["mirror_vertical", True]]},
    {"id": "T07", "operations": [["mirror_horizontal", True], ["rotate_clockwise_deg", 90]]},
    {"id": "T08", "operations": [["rotate_clockwise_deg", 90], ["mirror_horizontal", True]]},
    {"id": "T09", "operations": [["scale_uniform", 0.75]]},
    {"id": "T10", "operations": [["scale_xy", [1.25, 0.75]]]},
    {"id": "T11", "operations": [["rotate_clockwise_deg", 30]]},
    {"id": "T12", "operations": [["mirror_vertical", True], ["rotate_clockwise_deg", 30]]}
]

# 矩阵运算
def mat_mul(a, b):
    """4x4矩阵乘法"""
    result = [0] * 16
    for i in range(4):
        for j in range(4):
            for k in range(4):
                result[i*4+j] += a[i*4+k] * b[k*4+j]
    return result

def translate(tx, ty):
    return [1,0,0,0, 0,1,0,0, 0,0,1,0, tx,ty,0,1]

def rotate(deg):
    rad = math.radians(deg)
    c = math.cos(rad)
    s = math.sin(rad)
    return [c,s,0,0, -s,c,0,0, 0,0,1,0, 0,0,0,1]

def scale(sx, sy):
    return [sx,0,0,0, 0,sy,0,0, 0,0,1,0, 0,0,0,1]

def mirror_h():
    return [-1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1]

def mirror_v():
    return [1,0,0,0, 0,-1,0,0, 0,0,1,0, 0,0,0,1]

def compute_matrix(operations, pivot):
    """计算组合变换矩阵"""
    px, py = pivot
    # 初始矩阵
    result = [1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1]
    
    for op, value in operations:
        if op == "rotate_clockwise_deg":
            # 围绕pivot旋转
            t1 = translate(-px, -py)
            r = rotate(value)
            t2 = translate(px, py)
            step = mat_mul(t2, mat_mul(r, t1))
        elif op == "mirror_horizontal":
            # 围绕pivot水平镜像
            t1 = translate(-px, -py)
            m = mirror_h()
            t2 = translate(px, py)
            step = mat_mul(t2, mat_mul(m, t1))
        elif op == "mirror_vertical":
            # 围绕pivot垂直镜像
            t1 = translate(-px, -py)
            m = mirror_v()
            t2 = translate(px, py)
            step = mat_mul(t2, mat_mul(m, t1))
        elif op == "scale_uniform":
            # 围绕pivot均匀缩放
            t1 = translate(-px, -py)
            s = scale(value, value)
            t2 = translate(px, py)
            step = mat_mul(t2, mat_mul(s, t1))
        elif op == "scale_xy":
            # 围绕pivot非均匀缩放
            t1 = translate(-px, -py)
            s = scale(value[0], value[1])
            t2 = translate(px, py)
            step = mat_mul(t2, mat_mul(s, t1))
        else:
            continue
        
        result = mat_mul(step, result)
    
    return result

# 计算所有变换的矩阵
matrices = {}
for t in transforms:
    matrices[t["id"]] = compute_matrix(t["operations"], stamp["pivot"])

# 保存geometry-audit.json
audit = {
    "stamp": stamp,
    "matrices": matrices,
    "transforms": transforms
}

output_dir = Path("outputs/20261008-a1b2c3/A09")
output_dir.mkdir(parents=True, exist_ok=True)
with open(output_dir / "geometry-audit.json", "w", encoding="utf-8") as f:
    json.dump(audit, f, ensure_ascii=False, indent=2)

# 颜色定义
BG = "#0F172A"
CARD_BG = "#1E293B"
CARD_BORDER = "#334155"
TEXT_PRIMARY = "#F1F5F9"
TEXT_SECONDARY = "#94A3B8"

# 网格参数
cols = 4
rows = 3
cell_w = 300
cell_h = 250
gap = 32
grid_w = cols * cell_w + (cols - 1) * gap
grid_h = rows * cell_h + (rows - 1) * gap
offset_x = (1600 - grid_w) // 2
offset_y = 100

# 构建DSL
lines = []
lines.append(f'<Snapshot background="{BG}" type="png">')
lines.append(f'  <Container width="1600" height="1200" padding="(20,24)">')
lines.append(f'    <Column crossAxisAlignment="START">')
lines.append(f'')
lines.append(f'      <!-- 标题 -->')
lines.append(f'      <Container width="1552" height="40" color="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}" padding="(10,14)">')
lines.append(f'        <Text color="{TEXT_PRIMARY}" fontSize="20" fontStyle="BOLD">十二个非对称图形变换标本</Text>')
lines.append(f'      </Container>')
lines.append(f'')
lines.append(f'      <SizedBox height="10"/>')
lines.append(f'')
lines.append(f'      <!-- 变换图谱 -->')
lines.append(f'      <Container width="{grid_w}" height="{grid_h}" color="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}">')
lines.append(f'        <Stack>')

# 绘制每个变换
for idx, t in enumerate(transforms):
    row = idx // cols
    col = idx % cols
    x = offset_x + col * (cell_w + gap)
    y = offset_y + row * (cell_h + gap)
    
    # 背景
    lines.append(f'          <Positioned left="{x}" top="{y}" width="{cell_w}" height="{cell_h}">')
    lines.append(f'            <Container width="{cell_w}" height="{cell_h}" color="{CARD_BG}" borderRadius="6" border="1 SOLID {CARD_BORDER}"/>')
    lines.append(f'          </Positioned>')
    
    # 编号
    lines.append(f'          <Positioned left="{x + 10}" top="{y + 10}" width="60" height="24">')
    lines.append(f'            <Text color="{TEXT_PRIMARY}" fontSize="16" fontStyle="BOLD">{t["id"]}</Text>')
    lines.append(f'          </Positioned>')
    
    # 操作说明
    op_names = []
    for op, val in t["operations"]:
        if op == "rotate_clockwise_deg":
            op_names.append(f"旋转{val}°")
        elif op == "mirror_horizontal":
            op_names.append("水平镜像")
        elif op == "mirror_vertical":
            op_names.append("垂直镜像")
        elif op == "scale_uniform":
            op_names.append(f"缩放{val}")
        elif op == "scale_xy":
            op_names.append(f"缩放({val[0]},{val[1]})")
    op_text = " → ".join(op_names)
    lines.append(f'          <Positioned left="{x + 10}" top="{y + 34}" width="{cell_w - 20}" height="20">')
    lines.append(f'            <Text color="{TEXT_SECONDARY}" fontSize="12">{op_text}</Text>')
    lines.append(f'          </Positioned>')
    
    # 变换后的图形
    matrix = matrices[t["id"]]
    matrix_str = ",".join(f"{v:.6f}" for v in matrix)
    
    # 计算图形在格子中的位置
    cell_center_x = x + cell_w // 2
    cell_center_y = y + cell_h // 2 + 20
    
    lines.append(f'          <Positioned left="{cell_center_x - 60}" top="{cell_center_y - 60}" width="120" height="120">')
    lines.append(f'            <Transform matrix="({matrix_str})" alignment="CENTER">')
    lines.append(f'              <Stack width="120" height="120">')
    
    # 绘制矩形
    for rect in stamp["rectangles"]:
        rx, ry, rw, rh = rect["xywh"]
        lines.append(f'                <Positioned left="{rx}" top="{ry}" width="{rw}" height="{rh}">')
        lines.append(f'                  <Container width="{rw}" height="{rh}" color="{rect["color"]}"/>')
        lines.append(f'                </Positioned>')
    
    # 绘制圆点
    dot = stamp["dot"]
    dx, dy = dot["center"]
    r = dot["radius"]
    lines.append(f'                <Positioned left="{dx - r}" top="{dy - r}" width="{r*2}" height="{r*2}">')
    lines.append(f'                  <Container width="{r*2}" height="{r*2}" color="{dot["color"]}" borderRadius="{r}"/>')
    lines.append(f'                </Positioned>')
    
    lines.append(f'              </Stack>')
    lines.append(f'            </Transform>')
    lines.append(f'          </Positioned>')

lines.append(f'        </Stack>')
lines.append(f'      </Container>')
lines.append(f'')
lines.append(f'      <!-- 图例 -->')
lines.append(f'      <Container width="1552" height="40" color="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}" padding="(10,14)">')
lines.append(f'        <Row crossAxisAlignment="CENTER">')
lines.append(f'          <Text color="{TEXT_SECONDARY}" fontSize="12">图例：</Text>')
lines.append(f'          <SizedBox width="10"/>')
lines.append(f'          <Container width="16" height="16" color="#E54B4B"/>')
lines.append(f'          <SizedBox width="4"/>')
lines.append(f'          <Text color="{TEXT_SECONDARY}" fontSize="12">矩形1</Text>')
lines.append(f'          <SizedBox width="10"/>')
lines.append(f'          <Container width="16" height="16" color="#2364DB"/>')
lines.append(f'          <SizedBox width="4"/>')
lines.append(f'          <Text color="{TEXT_SECONDARY}" fontSize="12">矩形2</Text>')
lines.append(f'          <SizedBox width="10"/>')
lines.append(f'          <Container width="16" height="16" color="#EAB53B"/>')
lines.append(f'          <SizedBox width="4"/>')
lines.append(f'          <Text color="{TEXT_SECONDARY}" fontSize="12">矩形3</Text>')
lines.append(f'          <SizedBox width="10"/>')
lines.append(f'          <Container width="16" height="16" color="#111111" borderRadius="8"/>')
lines.append(f'          <SizedBox width="4"/>')
lines.append(f'          <Text color="{TEXT_SECONDARY}" fontSize="12">圆点</Text>')
lines.append(f'        </Row>')
lines.append(f'      </Container>')
lines.append(f'')
lines.append(f'    </Column>')
lines.append(f'  </Container>')
lines.append(f'</Snapshot>')

dsl = "\n".join(lines)
with open(output_dir / "transform-atlas.snapshot", "w", encoding="utf-8") as f:
    f.write(dsl)

print(f"DSL generated: {len(dsl)} chars")
for t in transforms:
    print(f"{t['id']}: {matrices[t['id']][:4]}...")
