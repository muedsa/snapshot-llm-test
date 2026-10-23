"""B03 case-09: 等高线地图（Contour Map）- 地形数据可视化
用等高线展示地形高度分布，类似地图等高线。
场景：地理信息系统、地形分析、城市规划。
技术：网格高度场生成，等值线追踪，颜色编码海拔。
"""
import sys, os, json, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b03_kit as K

W, H = 1600, 1200
doc = K.Doc(W, H, "#0a0e1a")

# ============================================================ 生成高度场
random.seed(99)

grid_cols = 40
grid_rows = 30
cell_w = (W - 160) / grid_cols
cell_h = (H - 200) / grid_rows
grid_x = 80
grid_y = 120

def height_at(col, row):
    """模拟地形高度"""
    x = col / grid_cols
    y = row / grid_rows
    # 多个山峰
    h = 0.5 * math.exp(-((x-0.3)**2 + (y-0.4)**2) / 0.04)
    h += 0.7 * math.exp(-((x-0.7)**2 + (y-0.6)**2) / 0.03)
    h += 0.4 * math.exp(-((x-0.5)**2 + (y-0.2)**2) / 0.02)
    h += 0.3 * math.exp(-((x-0.2)**2 + (y-0.8)**2) / 0.03)
    # 平缓区域
    h += 0.1 * (1 - abs(x - 0.5) * 2)
    return h

# ============================================================ 绘制背景
for i in range(6, 0, -1):
    doc.rect(W // 2 - i * 100, H // 2 - i * 100, i * 200, i * 200,
             "#1a1a3a", radius=i * 100, opacity=0.02 * i)

# ============================================================ 绘制等高线
# 使用不同阈值的等高线
contour_levels = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
contour_colors = [
    "#1a237e", "#1565c0", "#1976d2", "#1e88e5", "#2196f3",
    "#42a5f5", "#64b5f6", "#90caf9", "#bbdefb", "#e3f2fd"
]

for level, color in zip(contour_levels, contour_colors):
    # 找到所有接近该高度的点，连接成线
    points = []
    for row in range(grid_rows):
        for col in range(grid_cols):
            h = height_at(col, row)
            if abs(h - level) < 0.08:
                x = grid_x + col * cell_w + cell_w / 2
                y = grid_y + row * cell_h + cell_h / 2
                points.append((x, y, col, row))

    # 简化：按列分组，每列取最高点附近
    if len(points) > 10:
        # 绘制等高线为填充多边形
        # 找边界点
        sorted_by_col = sorted(points, key=lambda p: p[2])
        col_groups = {}
        for p in sorted_by_col:
            col = p[2]
            if col not in col_groups:
                col_groups[col] = []
            col_groups[col].append(p)

        # 绘制每个高度水平的色块
        for col, col_points in col_groups.items():
            for p in col_points:
                x = grid_x + col * cell_w
                y = grid_y + (p[3]) * cell_h
                doc.rect(x, y, cell_w, cell_h, color, radius=2, opacity=0.6)

# ============================================================ 山峰标记
peaks = [
    (0.3, 0.4, "山峰A", "1200m", "#FFD700"),
    (0.7, 0.6, "山峰B", "1500m", "#FFD700"),
    (0.5, 0.2, "山峰C", "800m", "#FFA726"),
]

for px, py, name, elevation, color in peaks:
    x = grid_x + px * (grid_cols * cell_w)
    y = grid_y + py * (grid_rows * cell_h)
    doc.rect(x - 10, y - 10, 20, 20, color, radius=10, opacity=0.9)
    doc.text_c(x, y - 25, name, 14, color, bold=True, owner="peak_name")
    doc.text_c(x, y + 22, elevation, 12, "#CCCCCC", owner="elevation")

# ============================================================ 标题
doc.text(80, 40, "等高线地图 · CONTOUR MAP", 42, "#FFFFFF", bold=True, owner="title")
doc.text(80, 94, "地形高程可视化 · Topographic Elevation Visualization", 16, "#8888aa", owner="subtitle")

# ============================================================ 海拔图例
legend_x, legend_y = 1350, 40
doc.text(legend_x, legend_y, "海拔", 14, "#FFFFFF", bold=True, owner="legend_title")
for i, (level, color) in enumerate(zip(contour_levels[:5], contour_colors[:5])):
    ly = legend_y + 25 + i * 28
    doc.rect(legend_x, ly, 16, 16, color, radius=3, opacity=0.7)
    doc.text(legend_x + 22, ly - 1, f"{int(level * 100)}%", 12, "#CCCCCC", owner="leg_item")

# ============================================================ 坐标信息
doc.text(80, H - 50, "比例尺: 1:50,000 · 分辨率: 40×30 · 海拔范围: 0-1500m", 12, "#666688", owner="map_info")
doc.text_r(W - 80, H - 50, "© 2026 地理信息系统项目", 12, "#666688", owner="footer")

# ============================================================ 门禁
gates = K.dry_run(doc, "case-09", 12, [], max_parts=9000)
K.save_gates("case-09", gates, "初始版本")
K.assert_gates(gates, "case-09")

stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")
print("Gates passed:", len([g for g in gates if g['passed']]), "/", len(gates))

result = K.render_case("case-09", doc, "等高线地图", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))
