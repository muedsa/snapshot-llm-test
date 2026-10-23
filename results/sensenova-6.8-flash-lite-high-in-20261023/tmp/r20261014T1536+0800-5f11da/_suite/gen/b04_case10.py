"""B04 case-10: 行星发现历史（Discovery Timeline）
展示八大行星的发现历史，从古代到现代的天文学进步。
数据源：NASA Planetary Fact Sheet (2025-03-18)
"""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b04_kit as K

W, H = 1400, 1400
doc = K.Doc(W, H, "#0a0e1a")

# ============================================================ 行星发现数据
planets = [
    ("Mercury", "水星", "古代", "人类最早发现的行星之一", "#B8860B", -3000),
    ("Venus", "金星", "古代", "人类最早发现的行星之一", "#FF8C00", -3000),
    ("Earth", "地球", "古代", "我们的家园", "#4169E1", -10000),
    ("Mars", "火星", "古代", "人类最早发现的行星之一", "#CD5C5C", -3000),
    ("Jupiter", "木星", "古代", "太阳系最大行星", "#DEB887", -3000),
    ("Saturn", "土星", "古代", "拥有壮观光环系统", "#F4A460", -3000),
    ("Uranus", "天王星", "1781", "威廉·赫歇尔发现", "#87CEEB", 1781),
    ("Neptune", "海王星", "1846", "勒维耶预测位置后发现", "#4169E1", 1846),
]

# ============================================================ 标题
doc.text(80, 40, "行星发现历史 · DISCOVERY TIMELINE", 42, "#FFFFFF", bold=True, owner="title")
doc.text(80, 94, "八大行星的发现历程 · Discovery History of Eight Planets", 16, "#8888aa", owner="subtitle")

# ============================================================ 时间线参数
timeline_y = 350
timeline_x_start = 150
timeline_x_end = 1250
timeline_width = timeline_x_end - timeline_x_start

# 绘制时间线主轴
doc.line_h(timeline_x_start, timeline_x_end, timeline_y, "#333355", 2)

# 时间刻度
# 古代标记
ancient_x = timeline_x_start + 50
doc.circle(ancient_x, timeline_y, 8, "#8888aa", step=1)
doc.text_c(ancient_x, timeline_y + 20, "古代", 14, "#8888aa", owner="ancient")
doc.text_c(ancient_x, timeline_y - 25, "BC 3000+", 12, "#666688", owner="ancient_year")

# 1781年标记
uranus_x = timeline_x_start + timeline_width * 0.75
doc.circle(uranus_x, timeline_y, 8, "#87CEEB", step=1)
doc.text_c(uranus_x, timeline_y + 20, "1781", 14, "#87CEEB", owner="uranus_year")
doc.text_c(uranus_x, timeline_y - 25, "望远镜发现", 12, "#666688", owner="uranus_note")

# 1846年标记
neptune_x = timeline_x_start + timeline_width * 0.9
doc.circle(neptune_x, timeline_y, 8, "#4169E1", step=1)
doc.text_c(neptune_x, timeline_y + 20, "1846", 14, "#4169E1", owner="neptune_year")
doc.text_c(neptune_x, timeline_y - 25, "数学预测", 12, "#666688", owner="neptune_note")

# ============================================================ 行星卡片
# 内行星（古代发现）
inner_x = 200
inner_y = 550
doc.text(inner_x - 50, inner_y - 30, "古代发现的行星", 18, "#FFFFFF", bold=True, owner="inner_title")

for i, (name, name_cn, year, note, color, y_coord) in enumerate(planets[:6]):
    x = inner_x + i * 180
    # 卡片背景
    doc.rect(x - 70, inner_y - 15, 140, 180, "#1a1a2e", radius=10)
    # 行星圆
    doc.rect(x - 25, inner_y + 15, 50, 50, color, radius=25, opacity=0.8)
    # 名称
    doc.text_c(x, inner_y + 85, name_cn, 16, color, bold=True, owner="name")
    # 年份
    doc.text_c(x, inner_y + 115, "古代", 14, "#8888aa", owner="year")
    # 注释
    doc.text_c(x, inner_y + 145, note[:10] + "...", 12, "#666688", owner="note")

# ============================================================ 外行星（望远镜发现）
outer_x = 200
outer_y = 850
doc.text(outer_x - 50, outer_y - 30, "望远镜发现的行星", 18, "#FFFFFF", bold=True, owner="outer_title")

for i, (name, name_cn, year, note, color, y_coord) in enumerate(planets[6:]):
    x = outer_x + i * 300
    # 卡片背景
    doc.rect(x - 120, outer_y - 15, 240, 200, "#1a1a2e", radius=10)
    # 行星圆
    doc.rect(x - 30, outer_y + 15, 60, 60, color, radius=30, opacity=0.8)
    # 名称
    doc.text_c(x, outer_y + 95, name_cn, 18, color, bold=True, owner="name")
    # 年份
    doc.text_c(x, outer_y + 125, year, 16, "#FFFFFF", owner="year")
    # 注释
    doc.text_c(x, outer_y + 160, note[:15] + "...", 12, "#8888aa", owner="note")

# ============================================================ 发现者信息
info_x = 1050
info_y = 900
doc.text(info_x, info_y, "发现者", 16, "#FFFFFF", bold=True, owner="discovery_title")
doc.text(info_x, info_y + 30, "天王星", 14, "#87CEEB", bold=True, owner="uranus_name")
doc.text(info_x, info_y + 55, "威廉·赫歇尔", 13, "#CCCCCC", owner="herшель")
doc.text(info_x, info_y + 100, "海王星", 14, "#4169E1", bold=True, owner="neptune_name")
doc.text(info_x, info_y + 125, "勒维耶 / 伽勒", 13, "#CCCCCC", owner="leverrier")

# ============================================================ 底部说明
doc.line_h(80, W - 80, H - 100, "#333355", 1)
doc.text(80, H - 80, "六颗行星在古代用肉眼即可发现", 14, "#CCCCCC", owner="fact1")
doc.text(80, H - 55, "天王星和海王星需要望远镜才能观测", 14, "#CCCCCC", owner="fact2")
doc.text_r(W - 80, H - 55, "数据来源：NASA Planetary Fact Sheet", 12, "#666688", owner="source")
doc.text_r(W - 80, H - 30, "© 2026 太阳系行星特辑", 12, "#666688", owner="footer")

# ============================================================ 门禁
gates = K.dry_run(doc, "case-10", 12, [], max_parts=9000)
K.save_gates("case-10", gates, "初始版本")
K.assert_gates(gates, "case-10")

stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")
print("Gates passed:", len([g for g in gates if g['passed']]), "/", len(gates))

result = K.render_case("case-10", doc, "行星发现历史", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))
