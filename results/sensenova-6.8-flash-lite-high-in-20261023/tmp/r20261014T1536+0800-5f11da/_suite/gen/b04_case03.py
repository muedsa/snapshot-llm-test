"""B04 case-03: 行星密度对比（Planetary Density Comparison）
用柱状图展示八大行星的平均密度，区分岩石行星和气态巨行星。
数据源：NASA Planary Fact Sheet (2025-03-18)
"""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b04_kit as K

W, H = 1600, 900
doc = K.Doc(W, H, "#0a0e1a")

# ============================================================ 行星数据（密度单位：kg/m³）
planets = [
    ("Mercury", "水星", 5427, "#B8860B", "岩石"),
    ("Venus", "金星", 5243, "#FF8C00", "岩石"),
    ("Earth", "地球", 5513, "#4169E1", "岩石"),
    ("Mars", "火星", 3934, "#CD5C5C", "岩石"),
    ("Jupiter", "木星", 1326, "#DEB887", "气态"),
    ("Saturn", "土星", 687, "#F4A460", "气态"),
    ("Uranus", "天王星", 1271, "#87CEEB", "冰巨"),
    ("Neptune", "海王星", 1638, "#4169E1", "冰巨"),
]

# ============================================================ 标题
doc.text(80, 40, "行星密度对比 · PLANETARY DENSITY COMPARISON", 42, "#FFFFFF", bold=True, owner="title")
doc.text(80, 94, "八大行星平均密度可视化 · Average Density of Eight Planets", 16, "#8888aa", owner="subtitle")

# ============================================================ 柱状图参数
chart_x = 150
chart_y = 200
chart_w = 1300
chart_h = 550
max_density = 6000
num_bars = len(planets)
bar_spacing = chart_w / num_bars
bar_width = bar_spacing * 0.6

# ============================================================ 绘制网格线
for i in range(5):
    y = chart_y + chart_h - (i / 4) * chart_h
    doc.line_h(chart_x, chart_x + chart_w, y, "#333355", 1)
    density_val = int((i / 4) * max_density)
    doc.text_r(chart_x - 10, y - 8, f"{density_val:,}", 12, "#8888aa", owner="grid_label")

# ============================================================ Y轴标签
doc.text(80, chart_y + chart_h / 2 - 30, "密度 (kg/m³)", 14, "#FFFFFF", bold=True, owner="y_label")

# ============================================================ 绘制柱子
for i, (name, name_cn, density, color, ptype) in enumerate(planets):
    x = chart_x + i * bar_spacing + bar_spacing / 2 - bar_width / 2
    bar_h = (density / max_density) * chart_h
    y = chart_y + chart_h - bar_h

    # 柱子
    doc.rect(x, y, bar_width, bar_h, color, radius=4, opacity=0.8)

    # 密度值
    doc.text_c(x + bar_width / 2, y - 25, f"{density:,}", 14, color, bold=True, owner="density")

    # 行星名称
    doc.text_c(x + bar_width / 2, chart_y + chart_h + 15, name_cn, 14, "#FFFFFF", owner="name")

    # 类型标签
    doc.text_c(x + bar_width / 2, chart_y + chart_h + 35, ptype, 12, "#8888aa", owner="type")

# ============================================================ 基准线
water_density = 1000
water_y = chart_y + chart_h - (water_density / max_density) * chart_h
doc.line_h(chart_x, chart_x + chart_w, water_y, "#4DABF7", 1)
doc.text_r(chart_x + chart_w, water_y - 10, "水密度 1,000 kg/m³", 12, "#4DABF7", owner="water_line")

# ============================================================ 图例
legend_x = 1400
legend_y = 200
doc.text(legend_x, legend_y, "行星类型", 14, "#FFFFFF", bold=True, owner="legend_title")
types = [("岩石行星", "#CD5C5C"), ("气态巨行星", "#DEB887"), ("冰巨行星", "#87CEEB")]
for i, (tname, color) in enumerate(types):
    doc.rect(legend_x, legend_y + 25 + i * 28, 14, 14, color, radius=3)
    doc.text(legend_x + 22, legend_y + 24 + i * 28, tname, 12, "#CCCCCC", owner="leg_item")

# ============================================================ 底部信息
doc.line_h(80, W - 80, H - 60, "#333355", 1)
doc.text(80, H - 45, "土星密度0.687 g/cm³，比水轻，可浮于水面", 14, "#CCCCCC", owner="fact")
doc.text_r(W - 80, H - 45, "数据来源：NASA Planetary Fact Sheet", 12, "#666688", owner="source")
doc.text_r(W - 80, H - 25, "© 2026 太阳系行星特辑", 12, "#666688", owner="footer")

# ============================================================ 门禁
gates = K.dry_run(doc, "case-03", 12, [], max_parts=9000)
K.save_gates("case-03", gates, "初始版本")
K.assert_gates(gates, "case-03")

stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")
print("Gates passed:", len([g for g in gates if g['passed']]), "/", len(gates))

result = K.render_case("case-03", doc, "行星密度对比", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))
