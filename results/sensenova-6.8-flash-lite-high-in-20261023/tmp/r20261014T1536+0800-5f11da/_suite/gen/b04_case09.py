"""B04 case-09: 行星表面重力（Surface Gravity Comparison）
展示八大行星的表面重力加速度，对比地球重力。
数据源：NASA Planetary Fact Sheet (2025-03-18)
"""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b04_kit as K

W, H = 1400, 1400
doc = K.Doc(W, H, "#0a0e1a")

# ============================================================ 行星数据（重力加速度：m/s²）
planets = [
    ("Mercury", "水星", 3.7, "#B8860B", "38%"),
    ("Venus", "金星", 8.9, "#FF8C00", "91%"),
    ("Earth", "地球", 9.8, "#4169E1", "100%"),
    ("Mars", "火星", 3.7, "#CD5C5C", "38%"),
    ("Jupiter", "木星", 23.1, "#DEB887", "236%"),
    ("Saturn", "土星", 9.0, "#F4A460", "92%"),
    ("Uranus", "天王星", 8.7, "#87CEEB", "89%"),
    ("Neptune", "海王星", 11.0, "#4169E1", "112%"),
]

# ============================================================ 标题
doc.text(80, 40, "行星表面重力 · SURFACE GRAVITY COMPARISON", 42, "#FFFFFF", bold=True, owner="title")
doc.text(80, 94, "八大行星表面重力可视化 · Surface Gravity of Eight Planets", 16, "#8888aa", owner="subtitle")

# ============================================================ 绘制重力条
chart_x = 200
chart_y = 180
chart_w = 900
chart_h = 1000
max_gravity = 25
num_bars = len(planets)
bar_spacing = chart_h / num_bars
bar_width = 80

# 地球重力线
earth_gravity = 9.8
earth_y = chart_y + chart_h - (earth_gravity / max_gravity) * chart_h

for i, (name, name_cn, gravity, color, pct) in enumerate(planets):
    y = chart_y + i * bar_spacing + bar_spacing / 2

    # 行星名称
    doc.text_r(chart_x - 20, y - 15, f"{name_cn}", 16, color, bold=True, owner="name")

    # 重力条（水平）
    bar_w = (gravity / max_gravity) * chart_w
    doc.rect(chart_x, y - 20, bar_w, 40, color, radius=4, opacity=0.8)

    # 重力值
    doc.text(chart_x + bar_w + 10, y - 15, f"{gravity} m/s²", 16, color, bold=True, owner="gravity")

    # 地球百分比
    doc.text(chart_x + bar_w + 10, y + 10, f"({pct} 地球)", 12, "#8888aa", owner="pct")

# ============================================================ 地球重力参考线
doc.line_v(chart_x + (earth_gravity / max_gravity) * chart_w, chart_y, chart_y + chart_h, "#4DABF7", 1)
doc.text_r(chart_x + (earth_gravity / max_gravity) * chart_w, chart_y - 15, "地球重力 9.8 m/s²", 12, "#4DABF7", owner="earth_ref")

# ============================================================ 右侧信息
info_x = 1180
info_y = 200
doc.text(info_x, info_y, "重力排名", 16, "#FFFFFF", bold=True, owner="info_title")

sorted_planets = sorted(planets, key=lambda x: x[2], reverse=True)
for i, (name, name_cn, gravity, color, pct) in enumerate(sorted_planets[:5]):
    ly = info_y + 40 + i * 35
    doc.text(info_x, ly, f"{i+1}.", 14, color, bold=True, owner="rank")
    doc.text(info_x + 25, ly, f"{name_cn}", 14, "#FFFFFF", owner="rank_name")
    doc.text(info_x + 80, ly, f"{gravity}", 14, "#CCCCCC", owner="rank_gravity")

# ============================================================ 底部说明
doc.line_h(80, W - 80, H - 100, "#333355", 1)
doc.text(80, H - 80, "木星表面重力是地球的2.36倍，是重力最大的行星", 14, "#CCCCCC", owner="fact1")
doc.text(80, H - 55, "水星和火星表面重力仅约地球的38%", 14, "#CCCCCC", owner="fact2")
doc.text_r(W - 80, H - 55, "数据来源：NASA Planetary Fact Sheet", 12, "#666688", owner="source")
doc.text_r(W - 80, H - 30, "© 2026 太阳系行星特辑", 12, "#666688", owner="footer")

# ============================================================ 门禁
gates = K.dry_run(doc, "case-09", 12, [], max_parts=9000)
K.save_gates("case-09", gates, "初始版本")
K.assert_gates(gates, "case-09")

stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")
print("Gates passed:", len([g for g in gates if g['passed']]), "/", len(gates))

result = K.render_case("case-09", doc, "行星表面重力", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))
