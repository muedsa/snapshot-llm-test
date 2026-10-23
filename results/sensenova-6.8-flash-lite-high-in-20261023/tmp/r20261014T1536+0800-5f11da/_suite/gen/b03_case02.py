"""B03 case-02: 数据马赛克（Data Mosaic）- 数据热力图
用彩色方块组成数据热力图，展示不同区域的数据密度。
场景：城市规划数据可视化，展示城市人口密度分布。
技术：程序化网格生成，颜色编码密度，数据叠加。
"""
import sys, os, json, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b03_kit as K

W, H = 1600, 1200
doc = K.Doc(W, H, "#0a0e1a")

# ============================================================ 数据马赛克
random.seed(123)

# 网格参数
grid_cols = 40
grid_rows = 30
cell_w = 30
cell_h = 30
grid_x = 80
grid_y = 120

# 生成密度数据（模拟城市人口分布）
data = []
for row in range(grid_rows):
    for col in range(grid_cols):
        # 高斯分布模拟多个中心
        density = 0
        # 中心1：市中心
        cx1, cy1 = 20, 15
        density += 1.0 * math.exp(-((col-cx1)**2 + (row-cy1)**2) / 80)
        # 中心2：商业区
        cx2, cy2 = 12, 10
        density += 0.7 * math.exp(-((col-cx2)**2 + (row-cy2)**2) / 60)
        # 中心3：居住区
        cx3, cy3 = 28, 20
        density += 0.8 * math.exp(-((col-cx3)**2 + (row-cy3)**2) / 70)
        # 添加噪声
        density += random.random() * 0.1
        data.append(density)

# 绘制马赛克
for row in range(grid_rows):
    for col in range(grid_cols):
        density = data[row * grid_cols + col]
        x = grid_x + col * cell_w
        y = grid_y + row * cell_h

        # 颜色映射：低密度蓝色 -> 高密度红色
        if density < 0.1:
            color = "#1a237e"
        elif density < 0.3:
            color = "#1565c0"
        elif density < 0.5:
            color = "#2e7d32"
        elif density < 0.7:
            color = "#f9a825"
        elif density < 0.9:
            color = "#ef6c00"
        else:
            color = "#c62828"

        # 绘制方块，密度越高亮度越高（clamp opacity to [0,1]）
        opacity = min(1.0, 0.3 + density * 0.7)
        doc.rect(x + 1, y + 1, cell_w - 2, cell_h - 2, color,
                 radius=2, opacity=opacity)

# ============================================================ 标题区
doc.text(80, 40, "数据马赛克 · DATA MOSAIC", 42, "#FFFFFF", bold=True, owner="title")
doc.text(80, 94, "城市人口密度分布可视化 · Urban Population Density", 16, "#8888aa", owner="subtitle")

# ============================================================ 图例
legend_x, legend_y = 1300, 140
doc.text(legend_x, legend_y - 30, "密度", 16, "#FFFFFF", bold=True, owner="legend_title")

colors_legend = [
    ("#c62828", "极高"),
    ("#ef6c00", "高"),
    ("#f9a825", "中高"),
    ("#2e7d32", "中"),
    ("#1565c0", "低"),
    ("#1a237e", "极低"),
]
for i, (color, label) in enumerate(colors_legend):
    ly = legend_y + i * 35
    doc.rect(legend_x, ly, 24, 24, color, radius=4)
    doc.text(legend_x + 32, ly + 4, label, 14, "#CCCCCC", owner="legend_label")

# ============================================================ 统计数据
stats_y = H - 160
doc.line_h(80, W - 80, H - 200, "#333355", 1)

stats = [
    ("总人口", "8.7M", "#FFD700"),
    ("面积", "480km²", "#81D4FA"),
    ("平均密度", "18,125/km²", "#81C784"),
    ("最高密度", "42,000/km²", "#FFB74D"),
]
for i, (label, value, color) in enumerate(stats):
    sx = 80 + i * 360
    doc.text(sx, stats_y, label, 14, "#8888aa", owner="stat_label")
    doc.text(sx, stats_y + 25, value, 32, color, bold=True, owner="stat_value")

# ============================================================ 底部
doc.text(80, H - 60, "数据来源：自拟演示数据", 12, "#666688", owner="data_note")
doc.text_r(W - 80, H - 60, "© 2026 城市规划项目", 12, "#666688", owner="footer")

# ============================================================ 干跑门禁
gates = K.dry_run(doc, "case-02", 12, [], max_parts=9000)
K.save_gates("case-02", gates, "初始版本")
K.assert_gates(gates, "case-02")

stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")
print("Gates passed:", len([g for g in gates if g['passed']]), "/", len(gates))

result = K.render_case("case-02", doc, "数据马赛克", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))
