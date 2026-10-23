"""B02 case-06: 每日早餐提醒 (Morning Breakfast Reminder)
1080x1920, dark theme, push notification style.
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b02_kit as K

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
GREEN_L   = "#34D399"
CYAN      = "#06B6D4"
ROSE      = "#FB7185"

W, H = 1080, 1920
doc = K.Doc(W, H, NIGHT)

# ============================================================ 背景光晕
# 底部柔和光晕
for i in range(15, 0, -1):
    doc.rect(W // 2 - i * 120, H - 300, i * 240, 300,
             AMBER, radius=i * 120, opacity=0.02 * i)

# ============================================================ 通知卡片区
# 模拟手机锁屏通知
notif_y = 120

# 状态栏（模拟手机顶部）
doc.rect(0, 0, W, 40, NIGHT_MID, radius=0)
doc.text(40, 8, "05:28", 18, WHITE, bold=True, owner="status_time")
doc.text_r(W - 40, 8, "100%", 18, WHITE, bold=True, owner="status_battery")
# 信号图标
doc.rect(W - 100, 14, 4, 12, WHITE, radius=2)
doc.rect(W - 94, 12, 4, 14, WHITE, radius=2)
doc.rect(W - 88, 10, 4, 16, WHITE, radius=2)

# 日期栏
doc.text_c(W // 2, 65, "2026年10月23日 星期五", 24, WHITE, bold=True, owner="date")

# 分割线
doc.line_h(40, W - 40, 110, NIGHT_LGT, 1)

# ============================================================ 通知卡片
card_x = 60
card_y = notif_y + 80
card_w = W - 120
card_h = 780

# 通知卡片背景
doc.rect(card_x, card_y, card_w, card_h, NIGHT_MID, radius=24)

# 顶部图标区
icon_y = card_y + 40
# 应用图标：暖色圆形
icon_r = 40
doc.rect(card_x + 40 - icon_r, icon_y, icon_r * 2, icon_r * 2, AMBER, radius=icon_r)
doc.rect(card_x + 40 - 20, icon_y + 20, 40, 40, WHITE, radius=20)
doc.rect(card_x + 32, icon_y + 30, 16, 20, AMBER, radius=2)
doc.rect(card_x + 28, icon_y + 36, 24, 8, AMBER, radius=2)

# 应用名称
doc.text(card_x + 100, icon_y + 20, "夜光驿站", 28, WHITE, bold=True, owner="app_name")
doc.text_r(W - 60 - 40, icon_y + 28, "现在", 20, SLATE, owner="notif_time")

# 分割线
doc.line_h(card_x + 40, card_x + card_w - 40, icon_y + 110, NIGHT_LGT, 1)

# 通知标题
title_y = icon_y + 140
doc.text(card_x + 40, title_y, "早餐已备好", 48, AMBER, bold=True, owner="notif_title")

# 通知副标题
doc.text(card_x + 40, title_y + 72, "人民南站 · 距离 500 米", 28, WHITE, owner="notif_subtitle")

# 早餐菜单
menu_y = title_y + 130
doc.text(card_x + 40, menu_y, "今日菜单", 24, WHITE, bold=True, owner="menu_title")

menu_items = [
    ("白粥", "热粥 · 姜丝 · 葱花", GREEN),
    ("馒头", "刚出炉 · 3 个/人", AMBER),
    ("小菜", "腌黄瓜 · 豆腐乳", CYAN),
    ("热豆浆", "无糖 · 热饮", ROSE),
]

for i, (item, desc, color) in enumerate(menu_items):
    my = menu_y + 38 + i * 64
    # 项目点
    doc.rect(card_x + 44, my + 12, 12, 12, color, radius=6)
    # 项目名
    doc.text(card_x + 68, my, item, 22, WHITE, bold=True, owner="menu_item")
    # 描述
    doc.text(card_x + 180, my + 4, desc, 18, SLATE, owner="menu_desc")

# 分割线
doc.line_h(card_x + 40, card_x + card_w - 40, menu_y + 260, NIGHT_LGT, 1)

# 按钮区
btn_y = menu_y + 290
# 主按钮
btn_w = card_w - 80
btn_h = 64
doc.rect(card_x + 40, btn_y, btn_w, btn_h, AMBER, radius=32)
doc.text_c(card_x + card_w / 2, btn_y + 16, "查看路线 · 1 公里", 24, NIGHT, bold=True, owner="btn_primary")

# 次按钮
doc.rect(card_x + 40, btn_y + 80, btn_w, 56, NIGHT_LGT, radius=28)
doc.text_c(card_x + card_w / 2, btn_y + 94, "明天再说", 20, SLATE, bold=True, owner="btn_secondary")

# ============================================================ 快捷信息卡
quick_y = card_y + card_h + 40

# 天气卡
doc.rect(card_x, quick_y, card_w, 120, NIGHT_MID, radius=20)
doc.text(card_x + 40, quick_y + 20, "天气", 20, WHITE, bold=True, owner="weather_title")
doc.text(card_x + 40, quick_y + 52, "阴 · 12°C", 32, WHITE, bold=True, owner="weather_temp")
doc.text_r(W - 60 - 40, quick_y + 60, "北风 3 级", 18, SLATE, owner="weather_wind")

# 站点状态卡
doc.rect(card_x, quick_y + 140, card_w, 120, NIGHT_MID, radius=20)
doc.text(card_x + 40, quick_y + 160, "人民南站", 20, WHITE, bold=True, owner="station_title")
doc.text(card_x + 40, quick_y + 192, "营业中 · 当前空闲", 24, GREEN, bold=True, owner="station_status")
# 状态圆点
doc.rect(W - 60 - 40 - 16, quick_y + 200, 16, 16, GREEN, radius=8)

# ============================================================ 底部品牌
doc.text_c(W // 2, H - 100, "夜光驿站", 28, AMBER, bold=True, owner="brand_footer")
doc.text_c(W // 2, H - 64, "夜里有光 · 路有驿站", 18, AMBER_L, owner="slogan_footer")

# ============================================================ 干跑门禁
gates = K.dry_run(doc, "case-06", 16, [], max_parts=9000)
K.save_gates("case-06", gates, "初始版本")
K.assert_gates(gates, "case-06")

stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")
print("Gates passed:", len([g for g in gates if g['passed']]), "/", len(gates))

result = K.render_case("case-06", doc, "每日早餐提醒", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))