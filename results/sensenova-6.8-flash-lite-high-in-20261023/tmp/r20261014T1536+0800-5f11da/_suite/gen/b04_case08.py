"""B04 case-08: 行星大气成分（Atmospheric Composition）
展示八大行星的大气成分，对比岩石行星和气态巨行星的大气差异。
数据源：NASA Planetary Fact Sheet (2025-03-18)
"""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b04_kit as K

W, H = 1400, 1400
doc = K.Doc(W, H, "#0a0e1a")

# ============================================================ 行星大气数据
planets = [
    ("Mercury", "水星", "无大气", [], "#B8860B", "trace"),
    ("Venus", "金星", "CO₂ 96.5%", [("CO₂", 96.5, "#FF6B6B"), ("N₂", 3.5, "#4DABF7")], "#FF8C00", "thick"),
    ("Earth", "地球", "N₂ 78%", [("N₂", 78.08, "#4DABF7"), ("O₂", 20.95, "#69DB7C"), ("其他", 0.97, "#8888aa")], "#4169E1", "normal"),
    ("Mars", "火星", "CO₂ 95%", [("CO₂", 95.32, "#FF6B6B"), ("N₂", 2.7, "#4DABF7"), ("Ar", 1.6, "#FFD93D")], "#CD5C5C", "thin"),
    ("Jupiter", "木星", "H₂ 90%", [("H₂", 89.8, "#4DABF7"), ("He", 10.2, "#FFA94D")], "#DEB887", "gas"),
    ("Saturn", "土星", "H₂ 96%", [("H₂", 96.3, "#4DABF7"), ("He", 3.25, "#FFA94D"), ("其他", 0.45, "#8888aa")], "#F4A460", "gas"),
    ("Uranus", "天王星", "H₂ 83%", [("H₂", 82.99, "#4DABF7"), ("He", 15.1, "#FFA94D"), ("CH₄", 1.91, "#9775FA")], "#87CEEB", "ice"),
    ("Neptune", "海王星", "H₂ 80%", [("H₂", 80.2, "#4DABF7"), ("He", 19.0, "#FFA94D"), ("CH₄", 0.8, "#9775FA")], "#4169E1", "ice"),
]

# ============================================================ 标题
doc.text(80, 40, "行星大气成分 · ATMOSPHERIC COMPOSITION", 42, "#FFFFFF", bold=True, owner="title")
doc.text(80, 94, "八大行星大气组成可视化 · Atmospheric Breakdown of Eight Planets", 16, "#8888aa", owner="subtitle")

# ============================================================ 绘制大气成分柱
chart_x = 150
chart_y = 180
chart_w = 1100
chart_h = 1050
num_bars = len(planets)
bar_spacing = chart_h / num_bars
bar_width = 60

for i, (name, name_cn, summary, components, color, atype) in enumerate(planets):
    y = chart_y + i * bar_spacing + bar_spacing / 2

    # 行星名称
    doc.text_r(chart_x - 20, y - 15, f"{name_cn}", 16, color, bold=True, owner="name")

    # 大气类型标签
    doc.text_r(chart_x - 20, y + 8, f"({atype})", 12, "#8888aa", owner="atype")

    # 绘制成分堆叠条
    x_start = chart_x
    total_width = chart_w

    if len(components) == 0:
        # 无大气
        doc.rect(x_start, y - 15, total_width, 30, "#333355", radius=4)
        doc.text_c(x_start + total_width / 2, y - 8, "无大气", 14, "#8888aa", owner="no_atm")
    else:
        x_current = x_start
        for gas, pct, gas_color in components:
            w = (pct / 100) * total_width
            if w > 2:  # 只绘制足够宽的条
                doc.rect(x_current, y - 15, w, 30, gas_color, radius=2, opacity=0.8)
                # 标签（如果足够宽）
                if w > 40:
                    doc.text_c(x_current + w / 2, y - 6, f"{gas}", 12, "#FFFFFF", bold=True, owner="gas")
                    doc.text_c(x_current + w / 2, y + 10, f"{pct}%", 12, "#FFFFFF", owner="pct")
            x_current += w

# ============================================================ 图例
legend_x = 1300
legend_y = 200
doc.text(legend_x, legend_y, "气体成分", 14, "#FFFFFF", bold=True, owner="legend_title")
gases = [
    ("N₂", "氮气", "#4DABF7"),
    ("O₂", "氧气", "#69DB7C"),
    ("CO₂", "二氧化碳", "#FF6B6B"),
    ("H₂", "氢气", "#4DABF7"),
    ("He", "氦气", "#FFA94D"),
    ("CH₄", "甲烷", "#9775FA"),
    ("Ar", "氩气", "#FFD93D"),
]
for i, (gas, name, color) in enumerate(gases):
    ly = legend_y + 30 + i * 28
    doc.rect(legend_x, ly, 14, 14, color, radius=3)
    doc.text(legend_x + 22, ly - 1, f"{gas} {name}", 12, "#CCCCCC", owner="leg_item")

# ============================================================ 底部说明
doc.line_h(80, W - 80, H - 80, "#333355", 1)
doc.text(80, H - 60, "金星大气主要是CO₂（96.5%），造成强烈温室效应", 12, "#CCCCCC", owner="fact1")
doc.text_r(W - 80, H - 60, "数据来源：NASA Planetary Fact Sheet", 12, "#666688", owner="source")
doc.text_r(W - 80, H - 40, "© 2026 太阳系行星特辑", 12, "#666688", owner="footer")

# ============================================================ 门禁
gates = K.dry_run(doc, "case-08", 12, [], max_parts=9000)
K.save_gates("case-08", gates, "初始版本")
K.assert_gates(gates, "case-08")

stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")
print("Gates passed:", len([g for g in gates if g['passed']]), "/", len(gates))

result = K.render_case("case-08", doc, "行星大气成分", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))
