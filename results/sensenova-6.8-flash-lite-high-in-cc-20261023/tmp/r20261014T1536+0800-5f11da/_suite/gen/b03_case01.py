"""B03 case-01: 星图（Star Atlas）- 天文教育海报
用大量小圆点模拟星空，不同亮度/颜色表示不同星等。
场景：天文馆教育海报，展示不同星座的分布。
技术：程序化星点生成，光晕用rect+opacity，星座连线用stroke。
"""
import sys, os, json, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b03_kit as K

W, H = 1600, 2000
doc = K.Doc(W, H, "#050810")

# ============================================================ 星空背景
random.seed(42)

# 背景微光（用rect+opacity）
for i in range(5, 0, -1):
    doc.rect(W // 2 - i * 200, H // 2 - i * 150, i * 400, i * 300,
             "#1a237e", radius=i * 150, opacity=0.03 * i)

# 大量背景星星（不同亮度用不同大小和颜色）
for _ in range(300):
    x = random.randint(0, W)
    y = random.randint(0, H)
    brightness = random.random()
    if brightness < 0.3:
        doc.circle(x, y, 0.8, "#4a4a6a", step=1)
    elif brightness < 0.7:
        doc.circle(x, y, 1.2, "#8a8ab0", step=1)
    else:
        doc.circle(x, y, 1.8, "#d0d0f0", step=1)

# ============================================================ 星座绘制
# 大熊座（Big Dipper）
dipper = [
    (300, 400), (400, 380), (500, 400), (600, 420),
    (700, 460), (720, 540), (620, 580)
]
for x, y in dipper:
    # 光晕（用rect模拟圆形光晕）
    for r in [10, 7, 4]:
        doc.rect(x - r, y - r, r * 2, r * 2, "#FFD700",
                 radius=r, opacity=0.08)
    # 星点
    doc.circle(x, y, 4, "#FFD700", step=1)

# 大熊座连线
for i in range(len(dipper) - 1):
    x1, y1 = dipper[i]
    x2, y2 = dipper[i + 1]
    doc.stroke([(x1, y1), (x2, y2)], "#FFD70088", width=1, step=1)

# 小熊座
bear = [(900, 300), (1000, 280), (1080, 320), (1060, 400), (960, 420), (880, 380)]
for x, y in bear:
    for r in [8, 5, 3]:
        doc.rect(x - r, y - r, r * 2, r * 2, "#FFB74D",
                 radius=r, opacity=0.06)
    doc.circle(x, y, 3, "#FFB74D", step=1)
for i in range(len(bear)):
    x1, y1 = bear[i]
    x2, y2 = bear[(i + 1) % len(bear)]
    doc.stroke([(x1, y1), (x2, y2)], "#FFB74D88", width=0.8, step=1)

# 猎户座
orion = [
    (1100, 700), (1150, 680), (1200, 700),
    (1080, 600), (1220, 600),
    (1060, 800), (1240, 800)
]
for x, y in orion:
    for r in [10, 6, 4]:
        doc.rect(x - r, y - r, r * 2, r * 2, "#81D4FA",
                 radius=r, opacity=0.07)
    doc.circle(x, y, 3.5, "#81D4FA", step=1)
# 猎户座连线
connections = [(0, 3), (1, 4), (2, 4), (0, 1), (1, 2), (3, 4), (5, 6)]
for a, b in connections:
    x1, y1 = orion[a]
    x2, y2 = orion[b]
    doc.stroke([(x1, y1), (x2, y2)], "#81D4FA88", width=0.8, step=1)

# ============================================================ 星等说明
info_x, info_y = 100, 1000

# 标题
doc.text(info_x, info_y, "星图 · STAR ATLAS", 48, "#FFFFFF", bold=True, owner="title")
doc.text(info_x, info_y + 60, "天文教育海报 · Astronomical Education Poster", 18, "#8888aa", owner="subtitle")
doc.line_h(info_x, info_x + 800, info_y + 90, "#333355", 1)

# 星等说明
mag_y = info_y + 120
magnitudes = [
    (0, "最亮 · Mag 0", "#FFFFFF", 6),
    (1, "明亮 · Mag 1", "#E0E0F0", 5),
    (2, "中等 · Mag 2", "#C0C0E0", 4),
    (3, "较暗 · Mag 3", "#A0A0C0", 3),
    (4, "暗淡 · Mag 4", "#8080A0", 2),
    (5, "微光 · Mag 5", "#606080", 1),
]
for i, (mag, label, color, size) in enumerate(magnitudes):
    my = mag_y + i * 40
    # 光晕
    for r in [size * 2, size * 1.5]:
        doc.rect(info_x + 15 - r, my + 12 - r, r * 2, r * 2, color,
                 radius=r, opacity=0.05)
    doc.circle(info_x + 15, my + 12, size, color, step=1)
    doc.text(info_x + 50, my, label, 16, color, owner="mag_label")

# ============================================================ 星座名称标注
doc.text(350, 340, "大熊座", 24, "#FFD700", bold=True, owner="dipper_name")
doc.text(350, 370, "Big Dipper", 14, "#FFD700", owner="dipper_en")
doc.text(920, 240, "小熊座", 20, "#FFB74D", bold=True, owner="bear_name")
doc.text(920, 265, "Little Bear", 12, "#FFB74D", owner="bear_en")
doc.text(1050, 560, "猎户座", 22, "#81D4FA", bold=True, owner="orion_name")
doc.text(1050, 592, "Orion", 14, "#81D4FA", owner="orion_en")

# ============================================================ 底部信息
doc.line_h(100, W - 100, H - 120, "#333355", 1)
doc.text(100, H - 100, "数据来源：自拟演示数据", 14, "#666688", owner="data_note")
doc.text_c(W // 2, H - 100, "星等越小越亮", 16, "#8888aa", bold=True, owner="mag_note")
doc.text_r(W - 100, H - 100, "© 2026 天文教育项目", 14, "#666688", owner="footer")

# 底部光晕
for i in range(10, 0, -1):
    doc.rect(W // 2 - i * 80, H - i * 10, i * 160, 10,
             "#1a237e", radius=5, opacity=0.03 * i)

# ============================================================ 干跑门禁
gates = K.dry_run(doc, "case-01", 12, [], max_parts=9000)
K.save_gates("case-01", gates, "初始版本")
K.assert_gates(gates, "case-01")

stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")
print("Gates passed:", len([g for g in gates if g['passed']]), "/", len(gates))

result = K.render_case("case-01", doc, "星图", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))
