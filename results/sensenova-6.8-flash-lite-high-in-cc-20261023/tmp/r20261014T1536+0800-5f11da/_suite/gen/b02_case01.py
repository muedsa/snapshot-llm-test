"""B02 case-01: 驿站品牌标识海报 (Station Brand Identity Poster)
2400x3000, dark theme, low density, large warm glow circle.
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b02_kit as K

# ============================================================ 颜色
NIGHT     = "#0F172A"
NIGHT_MID = "#1E293B"
NIGHT_LGT = "#334155"
WHITE     = "#F1F5F9"
SLATE     = "#94A3B8"
MUTED     = "#64748B"
AMBER     = "#F59E0B"
AMBER_L   = "#FCD34D"
AMBER_D   = "#D97706"
GREEN     = "#10B981"
RED       = "#EF4444"

W, H = 2400, 3000
doc = K.Doc(W, H, NIGHT)

# ============================================================ 背景光晕（径向渐变效果）
# 从中心向外，12 个同心圆模拟萤火虫/驿站灯光光晕
# 外圈用低透明度，内圈用高透明度
glow_center = (W // 2, H * 3 // 7)  # 光晕中心偏上
glow_max_r  = 1100

for i in range(12, 0, -1):
    r = glow_max_r * i / 12
    # 内圈更亮，外圈更暗
    brightness = (13 - i) / 12
    # 用暖琥珀色
    if i <= 2:
        color = AMBER_L
        opacity = 0.35 * (3 - i) / 2
    elif i <= 4:
        color = AMBER
        opacity = 0.25 * (5 - i) / 2
    else:
        color = AMBER_D
        opacity = 0.15 * (13 - i) / 12
    doc.rect(
        glow_center[0] - r, glow_center[1] - r, r * 2, r * 2,
        color, radius=r, opacity=opacity
    )

# ============================================================ 顶部品牌区
# 顶部横条：品牌名称和口号
top_y = 120
# 品牌名
doc.text_c(W // 2, top_y, "夜光驿站", 72, WHITE, bold=True, owner="brand")
doc.text_c(W // 2, top_y + 100, "NIGHT GLOW STATION", 28, AMBER, bold=True, owner="brand_en")

# 细分割线
doc.line_h(W // 2 - 400, W // 2 + 400, top_y + 140, NIGHT_LGT, 1)

# ============================================================ 中心光晕区域
# 光晕中心放一个圆形驿站图标
icon_cx, icon_cy = glow_center
icon_r = 140

# 外圈发光
doc.rect(icon_cx - icon_r - 20, icon_cy - icon_r - 20,
         (icon_r + 20) * 2, (icon_r + 20) * 2,
         AMBER, radius=icon_r + 20, opacity=0.15)

# 图标底色
doc.rect(icon_cx - icon_r, icon_cy - icon_r,
         icon_r * 2, icon_r * 2,
         AMBER, radius=icon_r, opacity=0.3)

# 驿站图标：圆形内有十字（+ 形）
# 横线
doc.rect(icon_cx - 60, icon_cy - 8, 120, 16, WHITE, radius=8)
# 竖线
doc.rect(icon_cx - 8, icon_cy - 60, 16, 120, WHITE, radius=8)

# ============================================================ 核心信息区
info_y = icon_cy + 240

# 大标题：驿站名称
doc.text_c(W // 2, info_y, "城市24小时开放驿站", 56, WHITE, bold=True, owner="title")

# 副标题：开放时间
doc.text_c(W // 2, info_y + 80, "24小时 · 全年无休", 36, AMBER, bold=True, owner="hours")

# 分割线
doc.line_h(W // 2 - 300, W // 2 + 300, info_y + 145, NIGHT_LGT, 1)

# 服务列表
services = [
    ("休息区", "有沙发，有热水，有充电插座"),
    ("免费热食", "夜宵和早餐，由志愿烹饪者提供"),
    ("健康站", "血压仪，急救包，心理咨询热线"),
    ("社区公告", "活动招募，互助信息，工人故事"),
]
svc_y = info_y + 180
for i, (title, desc) in enumerate(services):
    row_y = svc_y + i * 85
    # 圆点
    doc.rect(W // 2 - 520, row_y + 18, 12, 12, AMBER, radius=6)
    # 服务名
    doc.text(W // 2 - 490, row_y + 8, title, 28, WHITE, bold=True, owner="svc")
    # 描述
    doc.text(W // 2 - 490, row_y + 45, desc, 20, SLATE, owner="svc_desc")

# ============================================================ 底部信息区
bottom_y = H - 200

# 分割线
doc.line_h(W // 2 - 600, W // 2 + 600, bottom_y - 60, NIGHT_LGT, 1)

# 口号
doc.text_c(W // 2, bottom_y - 30, "夜里有光，路有驿站", 32, AMBER, bold=True, owner="slogan")

# 底部辅助信息
doc.text_c(W // 2, bottom_y + 30, "12个驿站 · 覆盖全市夜班通勤路线 · 欢迎进入", 20, SLATE, owner="footer")

doc.text_c(W // 2, bottom_y + 65, "www.yeguang-yizhan.com", 18, MUTED, owner="url")

# ============================================================ 侧边装饰光斑
# 左侧散布几个小光斑
left_spots = [
    (200, 400, 20, 0.3),
    (300, 700, 14, 0.2),
    (180, 1100, 18, 0.25),
    (350, 1500, 12, 0.15),
    (220, 2000, 16, 0.2),
    (400, 2500, 14, 0.15),
]
for (x, y, r, op) in left_spots:
    doc.rect(x - r, y - r, r * 2, r * 2, AMBER, radius=r, opacity=op)

# 右侧散布几个小光斑
right_spots = [
    (2200, 300, 16, 0.25),
    (2100, 600, 12, 0.15),
    (2200, 900, 20, 0.3),
    (2050, 1300, 14, 0.2),
    (2250, 1700, 16, 0.2),
    (2100, 2200, 18, 0.25),
    (2200, 2700, 12, 0.15),
]
for (x, y, r, op) in right_spots:
    doc.rect(x - r, y - r, r * 2, r * 2, AMBER, radius=r, opacity=op)

# ============================================================ 左上角和右上角装饰
# 左上角：小月亮图标
moon_cx, moon_cy = 150, 150
# 月亮外圈
doc.rect(moon_cx - 40, moon_cy - 40, 80, 80, AMBER, radius=40, opacity=0.15)
# 月亮本体（用一个圆和一个偏移的深色圆叠加）
doc.rect(moon_cx - 30, moon_cy - 30, 60, 60, AMBER_L, radius=30)
# 月牙效果：用一个稍偏移的深色圆遮住一部分
doc.rect(moon_cx - 30 + 12, moon_cy - 30 + 5, 60, 60, NIGHT, radius=30)

# 右上角：小星星
star_positions = [(2250, 150), (2180, 120), (2220, 200)]
for (sx, sy) in star_positions:
    doc.rect(sx - 3, sy - 3, 6, 6, AMBER_L, radius=3, opacity=0.6)

# ============================================================ 底部光晕
# 底部有一条柔和的光晕带
for i in range(8, 0, -1):
    doc.rect(
        0, H - i * 30, W, 30,
        AMBER, radius=15, opacity=0.03 * i
    )

# ============================================================ 干跑门禁
gates = K.dry_run(doc, "case-01", 16, [], max_parts=9000)
K.save_gates("case-01", gates, "初始版本")
K.assert_gates(gates, "case-01")

# ============================================================ 渲染
stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")
print(f"Canvas: {W}x{H}")
print("Gates passed:", len([g for g in gates if g['passed']]), "/", len(gates))

result = K.render_case("case-01", doc, "驿站品牌标识海报", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))