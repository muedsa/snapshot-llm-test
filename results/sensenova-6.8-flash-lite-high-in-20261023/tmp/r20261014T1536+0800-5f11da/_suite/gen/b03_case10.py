"""B03 case-10: 极简信息卡（Minimal Infocard）- 信息设计
用最少的元素传达关键信息，展示极简主义设计美学。
场景：天气预报卡、数据统计卡、通知卡片。
技术：大量留白，精确对齐，有限色彩，字体层级。
"""
import sys, os, json, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b03_kit as K

W, H = 1400, 1400
doc = K.Doc(W, H, "#0a0e1a")

# ============================================================ 极简设计参数
margin = 120
card_x = margin
card_y = margin
card_w = W - margin * 2
card_h = H - margin * 2

# ============================================================ 卡片背景
doc.rect(card_x, card_y, card_w, card_h, "#12121a", radius=20)
doc.rect(card_x, card_y, card_w, card_h, "#1a1a2e", radius=20, opacity=0.3)

# ============================================================ 顶部：天气信息
header_y = card_y + 80
doc.text(card_x + 60, header_y, "天气预报", 24, "#666688", owner="category")
doc.text(card_x + 60, header_y + 40, "上海", 48, "#FFFFFF", bold=True, owner="city")
doc.text_r(card_x + card_w - 60, header_y + 50, "10月23日 周四", 16, "#8888aa", owner="date")

# 温度大字
temp_y = header_y + 130
doc.text_c(W // 2, temp_y, "18°", 120, "#FFFFFF", bold=True, owner="temp")
doc.text_c(W // 2, temp_y + 152, "晴间多云", 28, "#8888aa", owner="condition")

# ============================================================ 分割线
line_y = temp_y + 220
doc.line_h(card_x + 60, card_x + card_w - 60, line_y, "#333355", 1)

# ============================================================ 天气详情
detail_y = line_y + 40
details = [
    ("最低", "14°", "#4DABF7"),
    ("最高", "22°", "#FF6B6B"),
    ("湿度", "65%", "#69DB7C"),
    ("风速", "3级", "#FFD93D"),
]

detail_spacing = card_w / len(details)
for i, (label, value, color) in enumerate(details):
    cx = card_x + 60 + i * detail_spacing + detail_spacing / 2
    doc.text_c(cx, detail_y, label, 14, "#666688", owner="detail_label")
    doc.text_c(cx, detail_y + 25, value, 32, color, bold=True, owner="detail_value")

# ============================================================ 分割线
line_y2 = detail_y + 80
doc.line_h(card_x + 60, card_x + card_w - 60, line_y2, "#333355", 1)

# ============================================================ 一周预报
week_y = line_y2 + 40
doc.text(card_x + 60, week_y, "一周预报", 18, "#FFFFFF", bold=True, owner="week_title")

days = [
    ("周四", "晴", "18°", "#FFD700"),
    ("周五", "多云", "16°", "#FFA94D"),
    ("周六", "雨", "12°", "#4DABF7"),
    ("周日", "雨", "11°", "#4DABF7"),
    ("周一", "阴", "14°", "#8888aa"),
    ("周二", "晴", "17°", "#FFD700"),
    ("周三", "晴", "19°", "#FFD700"),
]

day_spacing = (card_w - 120) / len(days)
for i, (day, weather, temp, color) in enumerate(days):
    x = card_x + 60 + i * day_spacing + day_spacing / 2
    doc.text_c(x, week_y + 50, day, 14, "#8888aa", owner="day")
    doc.text_c(x, week_y + 80, weather, 16, "#CCCCCC", owner="weather")
    doc.text_c(x, week_y + 110, temp, 20, color, bold=True, owner="day_temp")

# ============================================================ 底部信息
footer_y = card_y + card_h - 60
doc.line_h(card_x + 60, card_x + card_w - 60, footer_y - 20, "#333355", 1)
doc.text(card_x + 60, footer_y, "数据来源：中国气象局", 12, "#666688", owner="source")
doc.text_r(card_x + card_w - 60, footer_y, "更新时间：06:00", 12, "#666688", owner="update_time")

# ============================================================ 标题区
doc.text(80, 40, "极简信息卡 · MINIMAL INFOCARD", 42, "#FFFFFF", bold=True, owner="title")
doc.text(80, 94, "信息设计的减法美学 · The Subtractive Aesthetics of Information Design", 16, "#8888aa", owner="subtitle")

# ============================================================ 设计原则
principles_x = W - 80
principles_y = 40
doc.text_r(principles_x, principles_y, "设计原则", 14, "#FFFFFF", bold=True, owner="principles_title")
principles = ["留白", "层级", "对齐", "克制"]
for i, p in enumerate(principles):
    doc.text_r(principles_x, principles_y + 25 + i * 22, p, 12, "#8888aa", owner="principle")

# ============================================================ 底部
doc.text(80, H - 30, "极简主义：用最少的元素传达最多的信息", 12, "#666688", owner="info")
doc.text_r(W - 80, H - 30, "© 2026 信息设计项目", 12, "#666688", owner="footer")

# ============================================================ 门禁
gates = K.dry_run(doc, "case-10", 12, [], max_parts=9000)
K.save_gates("case-10", gates, "初始版本")
K.assert_gates(gates, "case-10")

stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")
print("Gates passed:", len([g for g in gates if g['passed']]), "/", len(gates))

result = K.render_case("case-10", doc, "极简信息卡", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))
