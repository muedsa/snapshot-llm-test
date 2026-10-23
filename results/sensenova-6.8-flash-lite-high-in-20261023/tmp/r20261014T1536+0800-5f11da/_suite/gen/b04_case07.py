"""B04 case-07: 行星温度范围（Temperature Range Comparison）
展示八大行星的平均温度，突出金星的高温和海王星的极寒。
数据源：NASA Planetary Fact Sheet (2025-03-18)
"""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b04_kit as K

W, H = 1600, 900
doc = K.Doc(W, H, "#0a0e1a")

# ============================================================ 行星数据（平均温度：°C）
planets = [
    ("Mercury", "水星", 167, "#B8860B"),
    ("Venus", "金星", 464, "#FF8C00"),
    ("Earth", "地球", 15, "#4169E1"),
    ("Mars", "火星", -65, "#CD5C5C"),
    ("Jupiter", "木星", -110, "#DEB887"),
    ("Saturn", "土星", -140, "#F4A460"),
    ("Uranus", "天王星", -195, "#87CEEB"),
    ("Neptune", "海王星", -200, "#4169E1"),
]

# ============================================================ 标题
doc.text(80, 40, "行星温度范围 · TEMPERATURE RANGE COMPARISON", 42, "#FFFFFF", bold=True, owner="title")
doc.text(80, 94, "八大行星平均温度可视化 · Average Temperature of Eight Planets", 16, "#8888aa", owner="subtitle")

# ============================================================ 图表参数
chart_x = 150
chart_y = 180
chart_w = 1200
chart_h = 550
min_temp = -250
max_temp = 500
temp_range = max_temp - min_temp
zero_y = chart_y + (max_temp / temp_range) * chart_h

# ============================================================ 绘制温度轴
doc.line_v(chart_x, chart_y, chart_y + chart_h, "#333355", 1)
for t in [-200, -100, 0, 100, 200, 300, 400]:
    y = chart_y + ((max_temp - t) / temp_range) * chart_h
    doc.line_h(chart_x, chart_x + 20, y, "#333355", 1)
    doc.text_r(chart_x - 10, y - 8, f"{t}°", 12, "#8888aa", owner="temp_label")

# 零度线
doc.line_h(chart_x, chart_x + chart_w, zero_y, "#4DABF7", 1)
doc.text_r(chart_x + chart_w, zero_y - 10, "0°C 冰点", 12, "#4DABF7", owner="zero_line")

# 水的沸点线
boil_y = chart_y + ((max_temp - 100) / temp_range) * chart_h
doc.line_h(chart_x, chart_x + chart_w, boil_y, "#FF6B6B", 1)
doc.text_r(chart_x + chart_w, boil_y - 10, "100°C 沸点", 12, "#FF6B6B", owner="boil_line")

# ============================================================ 绘制温度条
num_bars = len(planets)
bar_spacing = chart_w / num_bars
bar_width = bar_spacing * 0.6

for i, (name, name_cn, temp, color) in enumerate(planets):
    x = chart_x + i * bar_spacing + bar_spacing / 2 - bar_width / 2

    # 温度条（从0度线开始）
    bar_y = chart_y + ((max_temp - temp) / temp_range) * chart_h

    if temp >= 0:
        # 正温度：向上
        bar_top = chart_y + ((max_temp - temp) / temp_range) * chart_h
        bar_bottom = zero_y
        bar_height = bar_bottom - bar_top
    else:
        # 负温度：向下
        bar_top = zero_y
        bar_bottom = chart_y + ((max_temp - temp) / temp_range) * chart_h
        bar_height = bar_bottom - bar_top

    # 绘制温度条
    doc.rect(x, bar_top, bar_width, bar_height, color, radius=4, opacity=0.8)

    # 温度值
    if temp >= 0:
        doc.text_c(x + bar_width / 2, bar_top - 25, f"{temp}°C", 14, color, bold=True, owner="temp")
    else:
        doc.text_c(x + bar_width / 2, bar_bottom + 10, f"{temp}°C", 14, color, bold=True, owner="temp")

    # 行星名称
    doc.text_c(x + bar_width / 2, chart_y + chart_h + 15, name_cn, 14, "#FFFFFF", owner="name")

# ============================================================ 说明
doc.line_h(80, W - 80, H - 100, "#333355", 1)
doc.text(80, H - 80, "金星表面温度464°C，是太阳系最热行星", 14, "#CCCCCC", owner="fact1")
doc.text(80, H - 55, "海王星平均温度-200°C，是最冷行星", 14, "#CCCCCC", owner="fact2")
doc.text_r(W - 80, H - 55, "数据来源：NASA Planetary Fact Sheet", 12, "#666688", owner="source")
doc.text_r(W - 80, H - 30, "© 2026 太阳系行星特辑", 12, "#666688", owner="footer")

# ============================================================ 门禁
gates = K.dry_run(doc, "case-07", 12, [], max_parts=9000)
K.save_gates("case-07", gates, "初始版本")
K.assert_gates(gates, "case-07")

stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")
print("Gates passed:", len([g for g in gates if g['passed']]), "/", len(gates))

result = K.render_case("case-07", doc, "行星温度范围", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))
