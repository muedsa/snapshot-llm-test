"""B04 case-06: 行星卫星数量（Moon Count Comparison）
展示八大行星的卫星数量，揭示土星卫星最多的事实。
数据源：NASA Planetary Fact Sheet (2025-03-18)
"""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b04_kit as K

W, H = 1600, 900
doc = K.Doc(W, H, "#0a0e1a")

# ============================================================ 行星数据（卫星数量）
planets = [
    ("Mercury", "水星", 0, "#B8860B"),
    ("Venus", "金星", 0, "#FF8C00"),
    ("Earth", "地球", 1, "#4169E1"),
    ("Mars", "火星", 2, "#CD5C5C"),
    ("Jupiter", "木星", 95, "#DEB887"),
    ("Saturn", "土星", 274, "#F4A460"),
    ("Uranus", "天王星", 28, "#87CEEB"),
    ("Neptune", "海王星", 16, "#4169E1"),
]

# ============================================================ 标题
doc.text(80, 40, "行星卫星数量 · MOON COUNT COMPARISON", 42, "#FFFFFF", bold=True, owner="title")
doc.text(80, 94, "八大行星卫星数量可视化 · Number of Moons of Eight Planets", 16, "#8888aa", owner="subtitle")

# ============================================================ 绘制气泡图
# 卫星数量用气泡大小表示（对数尺度）
chart_x = 150
chart_y = 200
chart_w = 1200
chart_h = 500
max_moons = 274
num_bubbles = len(planets)
spacing = chart_w / num_bubbles

for i, (name, name_cn, moons, color) in enumerate(planets):
    x = chart_x + i * spacing + spacing / 2
    y = chart_y + chart_h / 2

    # 气泡半径（对数尺度）
    if moons == 0:
        r = 5
    else:
        r = 15 + 25 * math.log10(moons + 1)
        r = min(60, r)

    # 光晕
    doc.rect(x - r - 3, y - r - 3, (r + 3) * 2, (r + 3) * 2, color, radius=r + 3, opacity=0.2)

    # 主气泡
    doc.rect(x - r, y - r, r * 2, r * 2, color, radius=r, opacity=0.7)

    # 卫星数量（气泡内）
    doc.text_c(x, y - 5, f"{moons}颗", 18, "#FFFFFF", bold=True, owner="count")

    # 行星名称（气泡下）
    doc.text_c(x, y + r + 20, name_cn, 16, color, bold=True, owner="name")

# ============================================================ 说明
doc.line_h(80, W - 80, H - 150, "#333355", 1)
doc.text(80, H - 130, "土星拥有274颗卫星，是卫星最多的行星", 14, "#CCCCCC", owner="fact1")
doc.text(80, H - 105, "木星拥有95颗卫星，其中伽利略卫星最著名", 14, "#CCCCCC", owner="fact2")
doc.text(80, H - 80, "水星和金星没有卫星", 14, "#CCCCCC", owner="fact3")
doc.text_r(W - 80, H - 80, "数据来源：NASA Planetary Fact Sheet", 12, "#666688", owner="source")
doc.text_r(W - 80, H - 55, "© 2026 太阳系行星特辑", 12, "#666688", owner="footer")

# ============================================================ 图例
legend_x = 1350
legend_y = 200
doc.text(legend_x, legend_y, "气泡大小", 14, "#FFFFFF", bold=True, owner="legend_title")
doc.text(legend_x, legend_y + 25, "代表卫星数量", 12, "#8888aa", owner="legend_note")
doc.text(legend_x, legend_y + 50, "（对数尺度）", 12, "#8888aa", owner="legend_note2")

# 示例气泡
for i, (count, size) in enumerate([(0, 8), (1, 20), (10, 35), (100, 50), (274, 60)]):
    cy = legend_y + 90 + i * 55
    doc.rect(legend_x + 25 - size/2, cy - size/2, size, size, "#666688", radius=size/2, opacity=0.5)
    doc.text(legend_x + 50, cy - 8, f"{count}颗", 12, "#CCCCCC", owner="leg_item")

# ============================================================ 门禁
gates = K.dry_run(doc, "case-06", 12, [], max_parts=9000)
K.save_gates("case-06", gates, "初始版本")
K.assert_gates(gates, "case-06")

stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")
print("Gates passed:", len([g for g in gates if g['passed']]), "/", len(gates))

result = K.render_case("case-06", doc, "行星卫星数量", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))
