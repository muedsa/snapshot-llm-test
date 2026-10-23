"""B03 case-05: 分形树（Fractal Tree）- 自然形态可视化
用递归算法生成树状分形结构，展示自然界中的分形模式。
场景：自然博物馆教育海报，展示树木生长的数学规律。
技术：递归线段生成，角度衰减，颜色渐变。
"""
import sys, os, json, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b03_kit as K

W, H = 1400, 1800
doc = K.Doc(W, H, "#0a0e1a")

# ============================================================ 分形树生成
def fractal_tree(x, y, length, angle, depth, max_depth, branches):
    """递归生成分形树"""
    if depth > max_depth or length < 2:
        return

    # 计算终点
    x2 = x + length * math.cos(angle)
    y2 = y + length * math.sin(angle)

    # 根据深度选择颜色（从棕色到绿色）
    if depth < 2:
        color = "#8D6E63"  # 深棕
    elif depth < 4:
        color = "#6D4C41"  # 棕
    elif depth < 6:
        color = "#4CAF50"  # 绿
    else:
        color = "#81C784"  # 浅绿

    # 线段宽度随深度递减
    width = max(1, (max_depth - depth) * 0.8)

    # 绘制线段，step=3减少parts
    doc.stroke([(x, y), (x2, y2)], color, width=width, step=5)

    # 递归分支
    branch_angle = branches["angle"] + (depth * 0.05)
    new_length = length * branches["ratio"]

    # 左分支
    fractal_tree(x2, y2, new_length, angle - branch_angle, depth + 1, max_depth, branches)
    # 右分支
    fractal_tree(x2, y2, new_length, angle + branch_angle, depth + 1, max_depth, branches)
    # 中间分支（仅前2层）
    if depth < 2:
        fractal_tree(x2, y2, new_length * 0.8, angle, depth + 1, max_depth, branches)

# ============================================================ 绘制多棵分形树
# 主树
fractal_tree(700, 1600, 180, -math.pi/2, 0, 7, {"angle": 0.4, "ratio": 0.72})

# 小树1
fractal_tree(250, 1500, 80, -math.pi/2, 0, 7, {"angle": 0.5, "ratio": 0.7})

# 小树2
fractal_tree(1150, 1550, 90, -math.pi/2, 0, 7, {"angle": 0.35, "ratio": 0.75})

# ============================================================ 背景装饰
# 地面
doc.rect(0, 1600, W, 200, "#1a237e", radius=0, opacity=0.3)
for i in range(10, 0, -1):
    doc.rect(0, 1600 + i * 2, W, 2, "#283593", opacity=min(0.3, 0.03 * i))

# 月亮
moon_x, moon_y = 1100, 200
doc.rect(moon_x - 60, moon_y - 60, 120, 120, "#FFF9C4", radius=60, opacity=0.2)
doc.rect(moon_x - 45, moon_y - 45, 90, 90, "#FFF9C4", radius=45, opacity=0.4)
doc.rect(moon_x - 30, moon_y - 30, 60, 60, "#FFFDE7", radius=30, opacity=0.8)

# 星星
random.seed(77)
for _ in range(50):
    sx = random.randint(0, W)
    sy = random.randint(0, 400)
    doc.circle(sx, sy, random.choice([1, 1.5, 2]), "#FFFFFF", step=1)

# ============================================================ 标题
doc.text(80, 40, "分形树 · FRACTAL TREE", 42, "#FFFFFF", bold=True, owner="title")
doc.text(80, 94, "自然界中的数学之美 · Mathematics in Nature", 16, "#8888aa", owner="subtitle")

# ============================================================ 分形说明
info_x, info_y = 80, H - 200
doc.text(info_x, info_y, "分形参数", 20, "#FFFFFF", bold=True, owner="param_title")
params = [
    ("初始长度", "180px"),
    ("分叉角度", "23°"),
    ("衰减比例", "0.72"),
    ("最大深度", "7"),
    ("分支数", "2-3"),
]
for i, (label, value) in enumerate(params):
    doc.text(info_x + 20, info_y + 30 + i * 28, f"{label}: {value}", 14, "#CCCCCC", owner="param")

# ============================================================ 底部信息
doc.line_h(80, W - 80, H - 40, "#333355", 1)
doc.text(80, H - 30, "自然形态可视化", 12, "#666688", owner="note")
doc.text_r(W - 80, H - 30, "© 2026 自然博物馆", 12, "#666688", owner="footer")

# ============================================================ 干跑门禁
gates = K.dry_run(doc, "case-05", 12, [], max_parts=9000)
K.save_gates("case-05", gates, "初始版本")
K.assert_gates(gates, "case-05")

stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")
print("Gates passed:", len([g for g in gates if g['passed']]), "/", len(gates))

result = K.render_case("case-05", doc, "分形树", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))
