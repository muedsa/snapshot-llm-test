"""B03 case-04: 极坐标玫瑰（Polar Rose）- 分类数据可视化
用极坐标扇形展示分类数据，每个扇形代表一个类别。
场景：企业年度业务分析，展示不同业务线的占比。
技术：极坐标几何计算，扇形填充，标签定位。
"""
import sys, os, json, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b03_kit as K

W, H = 1400, 1400
doc = K.Doc(W, H, "#0a0e1a")

# ============================================================ 数据
categories = [
    ("云计算", 28, "#FF6B6B"),
    ("人工智能", 22, "#FFA94D"),
    ("大数据", 18, "#69DB7C"),
    ("物联网", 12, "#4DABF7"),
    ("区块链", 8, "#9775FA"),
    ("量子计算", 6, "#63E6BE"),
    ("其他", 6, "#FFD93D"),
]

# ============================================================ 中心点
cx, cy = W // 2, H // 2 - 50
max_r = 450
start_angle = -math.pi / 2  # 从顶部开始

# ============================================================ 背景装饰
for i in range(6, 0, -1):
    doc.rect(cx - i * 80, cy - i * 80, i * 160, i * 160,
             "#1a237e", radius=i * 80, opacity=0.02 * i)

# ============================================================ 绘制玫瑰图
total = sum(v for _, v, _ in categories)
current_angle = start_angle

for name, value, color in categories:
    angle_span = (value / total) * 2 * math.pi
    r = max_r * (0.3 + 0.7 * (value / max(categories[1][1] for _ in [0])))

    # 计算扇形顶点
    x1 = cx + r * math.cos(current_angle)
    y1 = cy + r * math.sin(current_angle)
    x2 = cx + r * math.cos(current_angle + angle_span)
    y2 = cy + r * math.sin(current_angle + angle_span)

    # 构建扇形多边形
    polygon = [(cx, cy), (x1, y1)]
    # 添加弧线点
    arc_steps = max(10, int(angle_span * 50))
    for i in range(1, arc_steps):
        angle = current_angle + angle_span * (i / arc_steps)
        polygon.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    polygon.append((x2, y2))

    # 填充扇形
    doc.fill(polygon, color, step=3)

    # 绘制分隔线
    doc.stroke([(cx, cy), (x2, y2)], "#0a0e1a", width=2, step=2)

    # 标签
    label_angle = current_angle + angle_span / 2
    label_r = r + 40
    lx = cx + label_r * math.cos(label_angle)
    ly = cy + label_r * math.sin(label_angle)

    # 百分比
    pct = f"{value}%"
    doc.text_c(lx, ly - 10, pct, 20, color, bold=True, owner="pct")
    # 名称
    doc.text_c(lx, ly + 14, name, 14, "#CCCCCC", owner="name")

    current_angle += angle_span

# ============================================================ 中心圆
doc.rect(cx - 60, cy - 60, 120, 120, "#1a1a3a", radius=60)
doc.text_c(cx, cy - 12, "业务", 24, "#FFFFFF", bold=True, owner="center_label")
doc.text_c(cx, cy + 22, "占比", 20, "#8888aa", owner="center_sub")

# ============================================================ 标题
doc.text(80, 40, "极坐标玫瑰 · POLAR ROSE", 42, "#FFFFFF", bold=True, owner="title")
doc.text(80, 94, "企业年度业务结构分析 · Annual Business Structure", 16, "#8888aa", owner="subtitle")

# ============================================================ 图例
legend_x, legend_y = 80, H - 280
doc.text(legend_x, legend_y, "业务线", 18, "#FFFFFF", bold=True, owner="legend_title")
for i, (name, value, color) in enumerate(categories):
    ly = legend_y + 35 + i * 28
    doc.rect(legend_x, ly, 16, 16, color, radius=4)
    doc.text(legend_x + 24, ly, f"{name} ({value}%)", 14, "#CCCCCC", owner="leg_item")

# ============================================================ 底部信息
doc.line_h(80, W - 80, H - 40, "#333355", 1)
doc.text(80, H - 30, "数据来源：自拟演示数据", 12, "#666688", owner="data_note")
doc.text_r(W - 80, H - 30, "© 2026 企业分析项目", 12, "#666688", owner="footer")

# ============================================================ 干跑门禁
gates = K.dry_run(doc, "case-04", 12, [], max_parts=9000)
K.save_gates("case-04", gates, "初始版本")
K.assert_gates(gates, "case-04")

stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")
print("Gates passed:", len([g for g in gates if g['passed']]), "/", len(gates))

result = K.render_case("case-04", doc, "极坐标玫瑰", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))
