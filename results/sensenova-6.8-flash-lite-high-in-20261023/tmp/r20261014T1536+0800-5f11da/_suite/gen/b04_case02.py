"""B04 case-02: 行星距离螺旋（Orbital Distance Spiral）
用螺旋线展示八大行星与太阳的距离，直观感受太阳系的巨大尺度。
数据源：NASA Planetary Fact Sheet (2025-03-18)
"""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b04_kit as K

W, H = 1400, 1400
doc = K.Doc(W, H, "#0a0e1a")

# ============================================================ 行星数据（距离单位：10^6 km）
planets = [
    ("Mercury", "水星", 57.9, "#B8860B"),
    ("Venus", "金星", 108.2, "#FF8C00"),
    ("Earth", "地球", 149.6, "#4169E1"),
    ("Mars", "火星", 228.0, "#CD5C5C"),
    ("Jupiter", "木星", 778.5, "#DEB887"),
    ("Saturn", "土星", 1432.0, "#F4A460"),
    ("Uranus", "天王星", 2867.0, "#87CEEB"),
    ("Neptune", "海王星", 4515.0, "#4169E1"),
]

# ============================================================ 参数
cx, cy = W // 2, H // 2
max_r = 550
num_turns = 4

# ============================================================ 背景光晕
for i in range(6, 0, -1):
    doc.rect(cx - i * 80, cy - i * 80, i * 160, i * 160,
             "#1a1a3a", radius=i * 80, opacity=0.02 * i)

# ============================================================ 绘制轨道环
for i, (_, _, dist, color) in enumerate(planets):
    r = (dist / 4515.0) * max_r
    r = max(20, r)
    doc.circle(cx, cy, r, color + "33", step=3, segs=max(20, int(r / 5)))

# ============================================================ 绘制行星
# 使用螺旋布局，行星在螺旋线上，标签在右侧固定位置
spiral_r = 550
spiral_turns = 0.5  # 半圈

for i, (name, name_cn, dist, color) in enumerate(planets):
    # 螺旋半径（均匀分布）
    t = i / (len(planets) - 1)
    r = t * spiral_r + 80  # 从80到630
    angle = -math.pi/2 + t * math.pi * spiral_turns * 2  # 半圈从顶部到底部

    x = cx + r * math.cos(angle)
    y = cy + r * math.sin(angle)

    # 行星圆点
    planet_r = 8
    doc.rect(x - planet_r, y - planet_r, planet_r * 2, planet_r * 2, color, radius=planet_r)

    # 标签：放在行星右侧，固定偏移
    label_x = x + 20
    label_y = y - 8

    doc.text(label_x, label_y, f"{name_cn}", 14, color, bold=True, owner="name")
    doc.text(label_x, label_y + 18, f"{dist} × 10⁶ km", 12, "#8888aa", owner="dist")

# ============================================================ 中心太阳
doc.rect(cx - 25, cy - 25, 50, 50, "#FFD700", radius=25, opacity=0.8)
doc.rect(cx - 15, cy - 15, 30, 30, "#FFA500", radius=15, opacity=0.6)
doc.text_c(cx, cy - 5, "太阳", 12, "#000000", bold=True, owner="sun")

# ============================================================ 标题
doc.text(80, 40, "行星距离螺旋 · ORBITAL DISTANCE SPIRAL", 42, "#FFFFFF", bold=True, owner="title")
doc.text(80, 94, "八大行星与太阳的距离 · Distance from Sun to Eight Planets", 16, "#8888aa", owner="subtitle")

# ============================================================ 距离信息
doc.text(80, H - 100, "水星距离太阳约5800万公里，海王星约45亿公里", 14, "#CCCCCC", owner="fact")
doc.text(80, H - 75, "太阳系直径约为92亿公里", 14, "#CCCCCC", owner="fact2")
doc.text_r(W - 80, H - 75, "数据来源：NASA Planetary Fact Sheet", 12, "#666688", owner="source")
doc.text_r(W - 80, H - 50, "© 2026 太阳系行星特辑", 12, "#666688", owner="footer")

# ============================================================ 门禁
gates = K.dry_run(doc, "case-02", 12, [], max_parts=9000)
K.save_gates("case-02", gates, "初始版本")
K.assert_gates(gates, "case-02")

stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")
print("Gates passed:", len([g for g in gates if g['passed']]), "/", len(gates))

result = K.render_case("case-02", doc, "行星距离螺旋", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))
