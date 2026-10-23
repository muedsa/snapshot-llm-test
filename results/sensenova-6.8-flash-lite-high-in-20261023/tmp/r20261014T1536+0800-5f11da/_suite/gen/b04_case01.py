"""B04 case-01: 行星尺度比较（Planetary Scale Comparison）
用实际比例展示八大行星的直径大小，帮助理解行星间的巨大尺度差异。
数据源：NASA Planetary Fact Sheet (2025-03-18)
"""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b04_kit as K

W, H = 1600, 900
doc = K.Doc(W, H, "#0a0e1a")

# ============================================================ 行星数据
planets = [
    ("Mercury", "水星", 4879, "#B8860B"),
    ("Venus", "金星", 12104, "#FF8C00"),
    ("Earth", "地球", 12756, "#4169E1"),
    ("Mars", "火星", 6792, "#CD5C5C"),
    ("Jupiter", "木星", 142984, "#DEB887"),
    ("Saturn", "土星", 120536, "#F4A460"),
    ("Uranus", "天王星", 51118, "#87CEEB"),
    ("Neptune", "海王星", 49528, "#4169E1"),
]

# ============================================================ 缩放因子
# 木星直径142984km -> 显示为100px半径
scale = 100.0 / 142984.0  # 半径比例

# ============================================================ 标题
doc.text(80, 40, "行星尺度比较 · PLANETARY SCALE COMPARISON", 42, "#FFFFFF", bold=True, owner="title")
doc.text(80, 94, "八大行星直径可视化 · Diameter Comparison of Eight Planets", 16, "#8888aa", owner="subtitle")

# ============================================================ 绘制行星
# 内行星（岩石）
inner_y = 250
doc.text(80, inner_y - 30, "内行星（岩石行星）", 18, "#FFFFFF", bold=True, owner="inner_label")

x = 200
for name, name_cn, diameter, color in planets[:4]:
    r = diameter * scale
    r = max(4, r)  # 最小半径4px
    doc.rect(x - r, inner_y + 40 - r, r * 2, r * 2, color, radius=r, opacity=0.8)
    doc.text_c(x, inner_y + 40 + r + 10, f"{name_cn}", 14, color, bold=True, owner="name")
    doc.text_c(x, inner_y + 40 + r + 32, f"{diameter:,} km", 12, "#8888aa", owner="diameter")
    x += 180

# ============================================================ 外行星（气态/冰巨行星）
outer_y = 500
doc.text(80, outer_y - 30, "外行星（气态巨行星 / 冰巨行星）", 18, "#FFFFFF", bold=True, owner="outer_label")

x = 250
for name, name_cn, diameter, color in planets[4:]:
    r = diameter * scale
    r = max(4, r)
    doc.rect(x - r, outer_y + 40 - r, r * 2, r * 2, color, radius=r, opacity=0.8)
    doc.text_c(x, outer_y + 40 + r + 10, f"{name_cn}", 14, color, bold=True, owner="name")
    doc.text_c(x, outer_y + 40 + r + 32, f"{diameter:,} km", 12, "#8888aa", owner="diameter")
    x += 250

# ============================================================ 比例尺
ruler_x = 1400
doc.text(ruler_x, 40, "比例尺", 14, "#FFFFFF", bold=True, owner="ruler_title")
doc.text(ruler_x, 65, "实际比例", 12, "#8888aa", owner="ruler_note")
doc.text(ruler_x, 85, "1px = 1,430 km", 12, "#666688", owner="scale")

# ============================================================ 对比说明
doc.line_h(80, W - 80, H - 120, "#333355", 1)
doc.text(80, H - 100, "木星直径是地球的11.2倍，是月球的3.5倍", 14, "#CCCCCC", owner="fact1")
doc.text(80, H - 75, "土星是密度最低的行星（0.687 g/cm³），比水还轻", 14, "#CCCCCC", owner="fact2")
doc.text_r(W - 80, H - 75, "数据来源：NASA Planetary Fact Sheet", 12, "#666688", owner="source")
doc.text_r(W - 80, H - 50, "© 2026 太阳系行星特辑", 12, "#666688", owner="footer")

# ============================================================ 门禁
gates = K.dry_run(doc, "case-01", 12, [], max_parts=9000)
K.save_gates("case-01", gates, "初始版本")
K.assert_gates(gates, "case-01")

stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")
print("Gates passed:", len([g for g in gates if g['passed']]), "/", len(gates))

result = K.render_case("case-01", doc, "行星尺度比较", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))
