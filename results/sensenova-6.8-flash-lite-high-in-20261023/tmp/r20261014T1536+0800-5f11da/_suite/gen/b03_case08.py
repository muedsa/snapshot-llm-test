"""B03 case-08: 时间螺旋（Time Spiral）- 时间序列可视化
用螺旋线展示时间序列数据，不同圈代表不同时间段。
场景：项目管理时间线、生命周期可视化、年度回顾。
技术：极坐标参数化螺旋，时间轴映射，事件标记。
"""
import sys, os, json, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b03_kit as K

W, H = 1400, 1400
doc = K.Doc(W, H, "#0a0e1a")

# ============================================================ 参数
cx, cy = W // 2, H // 2
num_turns = 8  # 螺旋圈数
points_per_turn = 40

# ============================================================ 背景光晕
for i in range(6, 0, -1):
    doc.rect(cx - i * 80, cy - i * 80, i * 160, i * 160,
             "#1a1a3a", radius=i * 80, opacity=0.02 * i)

# ============================================================ 生成螺旋路径
spiral_points = []
for i in range(num_turns * points_per_turn + 1):
    t = i / (num_turns * points_per_turn)
    angle = t * num_turns * 2 * math.pi
    r = 80 + t * 450  # 从内到外
    x = cx + r * math.cos(angle)
    y = cy + r * math.sin(angle)
    spiral_points.append((x, y, angle, r))

# ============================================================ 绘制螺旋
# 按段颜色渐变
colors = [
    (0, 0.125, "#FF6B6B"),
    (0.125, 0.25, "#FFA94D"),
    (0.25, 0.375, "#FFD93D"),
    (0.375, 0.5, "#69DB7C"),
    (0.5, 0.625, "#4DABF7"),
    (0.625, 0.75, "#9775FA"),
    (0.75, 0.875, "#F06595"),
    (0.875, 1.0, "#63E6BE"),
]

for ci, (start, end, color) in enumerate(colors):
    segment_points = []
    for i in range(len(spiral_points)):
        t = i / (len(spiral_points) - 1)
        if start <= t <= end:
            segment_points.append((spiral_points[i][0], spiral_points[i][1]))
    if len(segment_points) > 1:
        doc.stroke(segment_points, color, width=3, step=2)

# ============================================================ 季度标记
quarters = [
    ("Q1", 0.125, "#FF6B6B"),
    ("Q2", 0.375, "#FFD93D"),
    ("Q3", 0.625, "#4DABF7"),
    ("Q4", 0.875, "#63E6BE"),
]

for label, t_val, color in quarters:
    idx = int(t_val * (len(spiral_points) - 1))
    x, y, angle, r = spiral_points[idx]
    # 标记点
    doc.rect(x - 8, y - 8, 16, 16, color, radius=8, opacity=0.9)
    # 标签
    label_r = r + 30
    lx = cx + label_r * math.cos(angle)
    ly = cy + label_r * math.sin(angle)
    doc.text_c(lx, ly - 8, label, 18, color, bold=True, owner="quarter")

# ============================================================ 事件标记
events = [
    (0.1, "需求确认", "#FFFFFF"),
    (0.25, "原型设计", "#FFFFFF"),
    (0.4, "开发启动", "#FFFFFF"),
    (0.55, "Alpha版", "#FFFFFF"),
    (0.7, "Beta测试", "#FFFFFF"),
    (0.85, "正式发布", "#FFD700"),
]

for t_val, label, color in events:
    idx = int(t_val * (len(spiral_points) - 1))
    x, y, angle, r = spiral_points[idx]
    # 事件点
    doc.rect(x - 6, y - 6, 12, 12, color, radius=6, opacity=0.9)
    # 连接线到标签
    label_r = r - 40
    lx = cx + label_r * math.cos(angle + 0.3)
    ly = cy + label_r * math.sin(angle + 0.3)
    doc.stroke([(x, y), (lx, ly)], "#66668888", width=1, step=2)
    doc.text_c(lx, ly - 8, label, 12, "#CCCCCC", owner="event")

# ============================================================ 中心圆
doc.rect(cx - 40, cy - 40, 80, 80, "#1a1a3a", radius=40)
doc.text_c(cx, cy - 10, "2026", 16, "#FFFFFF", bold=True, owner="year")
doc.text_c(cx, cy + 14, "年度规划", 12, "#8888aa", owner="year_label")

# ============================================================ 标题
doc.text(80, 40, "时间螺旋 · TIME SPIRAL", 42, "#FFFFFF", bold=True, owner="title")
doc.text(80, 94, "项目生命周期可视化 · Project Lifecycle Visualization", 16, "#8888aa", owner="subtitle")

# ============================================================ 图例
legend_x, legend_y = 1150, 40
doc.text(legend_x, legend_y, "阶段", 14, "#FFFFFF", bold=True, owner="legend_title")
for i, (start, end, color) in enumerate(colors[:4]):
    ly = legend_y + 25 + i * 24
    doc.rect(legend_x, ly, 12, 12, color, radius=3)
    doc.text(legend_x + 18, ly - 1, ["Q1 规划", "Q2 设计", "Q3 开发", "Q4 发布"][i], 12, "#CCCCCC", owner="leg_item")

# ============================================================ 底部
doc.line_h(80, W - 80, H - 40, "#333355", 1)
doc.text(80, H - 30, "8圈螺旋 · 6个关键节点 · 4个季度", 12, "#666688", owner="info")
doc.text_r(W - 80, H - 30, "© 2026 项目管理办公室", 12, "#666688", owner="footer")

# ============================================================ 门禁
gates = K.dry_run(doc, "case-08", 12, [], max_parts=9000)
K.save_gates("case-08", gates, "初始版本")
K.assert_gates(gates, "case-08")

stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")
print("Gates passed:", len([g for g in gates if g['passed']]), "/", len(gates))

result = K.render_case("case-08", doc, "时间螺旋", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))
