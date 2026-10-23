"""B04 case-05: 行星自转周期（Rotation Period Comparison）
展示八大行星的自转周期，揭示金星和木星的独特自转特征。
数据源：NASA Planetary Fact Sheet (2025-03-18)
"""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b04_kit as K

W, H = 1600, 900
doc = K.Doc(W, H, "#0a0e1a")

# ============================================================ 行星数据（自转周期：小时）
planets = [
    ("Mercury", "水星", 1407.6, "#B8860B", "58.6天"),
    ("Venus", "金星", 5832.5, "#FF8C00", "243天（逆向）"),
    ("Earth", "地球", 23.9, "#4169E1", "23.9小时"),
    ("Mars", "火星", 24.6, "#CD5C5C", "24.6小时"),
    ("Jupiter", "木星", 9.9, "#DEB887", "9.9小时"),
    ("Saturn", "土星", 10.7, "#F4A460", "10.7小时"),
    ("Uranus", "天王星", 17.2, "#87CEEB", "17.2小时（侧向）"),
    ("Neptune", "海王星", 16.1, "#4169E1", "16.1小时"),
]

# ============================================================ 标题
doc.text(80, 40, "行星自转周期 · ROTATION PERIOD COMPARISON", 42, "#FFFFFF", bold=True, owner="title")
doc.text(80, 94, "八大行星自转速度可视化 · Rotation Speed of Eight Planets", 16, "#8888aa", owner="subtitle")

# ============================================================ 图表参数
chart_x = 150
chart_y = 180
chart_w = 1200
chart_h = 550
max_hours = 6000  # 最大值约6000小时
num_bars = len(planets)
bar_spacing = chart_w / num_bars
bar_width = bar_spacing * 0.5

# ============================================================ 绘制网格线
for i in range(7):
    y = chart_y + chart_h - (i / 6) * chart_h
    doc.line_h(chart_x, chart_x + chart_w, y, "#333355", 1)
    hours_val = int((i / 6) * max_hours)
    if i == 0:
        doc.text_r(chart_x - 10, y - 8, "0", 12, "#8888aa", owner="grid_label")
    else:
        doc.text_r(chart_x - 10, y - 8, f"{hours_val:,}", 12, "#8888aa", owner="grid_label")

# ============================================================ 地球自转线
earth_y = chart_y + chart_h - (24 / max_hours) * chart_h
doc.line_h(chart_x, chart_x + chart_w, earth_y, "#4DABF7", 1)
doc.text_r(chart_x + chart_w, earth_y + 5, "地球 24h", 12, "#4DABF7", owner="earth_line")

# ============================================================ 绘制柱子
for i, (name, name_cn, hours, color, note) in enumerate(planets):
    x = chart_x + i * bar_spacing + bar_spacing / 2 - bar_width / 2
    bar_h = (hours / max_hours) * chart_h
    y = chart_y + chart_h - bar_h

    # 柱子（使用对数可视化效果）
    doc.rect(x, y, bar_width, bar_h, color, radius=4, opacity=0.8)

    # 小时数
    if hours < 100:
        label = f"{hours}h"
    else:
        label = f"{hours/24:.1f}天"
    doc.text_c(x + bar_width / 2, y - 25, label, 14, color, bold=True, owner="hours")

    # 行星名称
    doc.text_c(x + bar_width / 2, chart_y + chart_h + 15, name_cn, 14, "#FFFFFF", owner="name")

    # 注释
    doc.text_c(x + bar_width / 2, chart_y + chart_h + 35, note, 12, "#8888aa", owner="note")

# ============================================================ 说明
doc.line_h(80, W - 80, H - 100, "#333355", 1)
doc.text(80, H - 80, "金星自转最慢：一天比一年还长（243天 vs 225天）", 14, "#CCCCCC", owner="fact1")
doc.text(80, H - 55, "木星自转最快：9.9小时一天，赤道风速超音速", 14, "#CCCCCC", owner="fact2")
doc.text_r(W - 80, H - 55, "数据来源：NASA Planetary Fact Sheet", 12, "#666688", owner="source")
doc.text_r(W - 80, H - 30, "© 2026 太阳系行星特辑", 12, "#666688", owner="footer")

# ============================================================ 门禁
gates = K.dry_run(doc, "case-05", 12, [], max_parts=9000)
K.save_gates("case-05", gates, "初始版本")
K.assert_gates(gates, "case-05")

stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")
print("Gates passed:", len([g for g in gates if g['passed']]), "/", len(gates))

result = K.render_case("case-05", doc, "行星自转周期", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))
