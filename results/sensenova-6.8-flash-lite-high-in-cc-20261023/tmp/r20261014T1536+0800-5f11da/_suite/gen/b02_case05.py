"""B02 case-05: 社区公告栏 (Community Bulletin Board)
1600x1200, dark theme, high density multi-card layout.
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
GREEN     = "#10B981"
GREEN_L   = "#34D399"
CYAN      = "#06B6D4"
CYAN_L    = "#67E8F9"
ROSE      = "#FB7185"
ROSE_L    = "#FDA4AF"
RED       = "#EF4444"
PURPLE    = "#8B5CF6"
PURPLE_L  = "#A78BFA"

W, H = 1600, 1200
doc = K.Doc(W, H, NIGHT)

# ============================================================ 顶部页头
doc.text(48, 28, "夜光驿站", 36, WHITE, bold=True, owner="brand")
doc.text(48 + K.tw("夜光驿站", 36) + 20, 36, "社区公告栏", 28, AMBER, bold=True, owner="title")

# 日期
doc.text_r(W - 48, 32, "2026-10-23 · 星期四", 20, SLATE, owner="date")
doc.text_r(W - 48, 60, "人民南站", 16, MUTED, owner="station")

# 分割线
doc.line_h(48, W - 48, 92, NIGHT_LGT, 1)

# ============================================================ 公告栏卡片
CARD_W = 470
CARD_H = 360
CARD_GAP = 30
ROW_Y = 115

cards = [
    {
        "x": 48, "y": ROW_Y,
        "color": AMBER, "color_l": AMBER_L,
        "icon": "event",
        "title": "今日活动",
        "badge": "进行中",
        "items": [
            ("19:00-21:00", "夜跑俱乐部", "医院北门集合，3 公里轻松跑"),
            ("20:00-21:00", "夜班故事会", "3 位工人的深夜故事分享"),
            ("22:00-00:00", "志愿烹饪", "今晚夜宵由张师傅主厨"),
        ]
    },
    {
        "x": 48 + CARD_W + CARD_GAP, "y": ROW_Y,
        "color": GREEN, "color_l": GREEN_L,
        "icon": "health",
        "title": "健康提示",
        "badge": "每日更新",
        "items": [
            ("凌晨 3 点", "拉伸提醒", "请每 2 小时起身活动 10 分钟"),
            ("全天", "补水计划", "夜班期间至少喝 2 升水"),
            ("今晚", "免费血压测量", "站点健康站 20:00-22:00"),
        ]
    },
    {
        "x": 48 + 2 * (CARD_W + CARD_GAP), "y": ROW_Y,
        "color": ROSE, "color_l": ROSE_L,
        "icon": "community",
        "title": "互助信息",
        "badge": "急需",
        "items": [
            ("换班请求", "周三夜班", "找一位护士换周三夜班，可带班"),
            ("失物招领", "黑色保温杯", "在休息区找到，请与工作人员联系"),
            ("代班求助", "周五白班", "临时有事，急需周五白班代班"),
        ]
    },
    {
        "x": 48, "y": ROW_Y + CARD_H + CARD_GAP,
        "color": CYAN, "color_l": CYAN_L,
        "icon": "volunteer",
        "title": "志愿者招募",
        "badge": "进行中",
        "items": [
            ("每月轮值", "烹饪志愿者", "每周日 19:00-21:00 准备夜宵"),
            ("周末值班", "接待志愿者", "周六周日 20:00-02:00 接待和清洁"),
            ("线上支持", "故事编辑", "整理工人故事，无需线下参与"),
        ]
    },
    {
        "x": 48 + CARD_W + CARD_GAP, "y": ROW_Y + CARD_H + CARD_GAP,
        "color": PURPLE, "color_l": PURPLE_L,
        "icon": "story",
        "title": "工人故事",
        "badge": "新一期",
        "items": [
            ("王师傅", "物流司机 15 年", "「凌晨的高速路，只有路灯陪着我」"),
            ("小李", "便利店店员 2 年", "「凌晨 4 点的早餐，是给夜班人最暖的礼物」"),
            ("张护士", "ICU 10 年", "「每一个夜班，都是一次与时间的赛跑」"),
        ]
    },
    {
        "x": 48 + 2 * (CARD_W + CARD_GAP), "y": ROW_Y + CARD_H + CARD_GAP,
        "color": RED, "color_l": "#FCA5A5",
        "icon": "emergency",
        "title": "紧急通知",
        "badge": "重要",
        "items": [
            ("明日维护", "中央商场站", "10-24 全天维护，明日 09:00 恢复"),
            ("天气预警", "寒潮来袭", "今夜气温降至 5°C，注意保暖"),
            ("站点活动", "新站开业", "金融街站 10-25 上午 10:00 开业"),
        ]
    },
]

for card in cards:
    cx, cy = card["x"], card["y"]
    color = card["color"]
    color_l = card["color_l"]

    # 卡片背景
    doc.rect(cx, cy, CARD_W, CARD_H, NIGHT_MID, radius=12)

    # 左侧色条
    doc.rect(cx, cy, 6, CARD_H, color, radius=0)

    # 卡片标题
    doc.text(cx + 24, cy + 18, card["title"], 22, WHITE, bold=True, owner="card_title")

    # 标签
    badge_text = card["badge"]
    badge_w = K.tw(badge_text, 12) + 16
    doc.rect(cx + CARD_W - 24 - badge_w, cy + 16, badge_w, 22, color, radius=11, opacity=0.2)
    doc.text_c(cx + CARD_W - 24 - badge_w / 2, cy + 18, badge_text, 12, color_l, bold=True, owner="card_badge")

    # 分割线
    doc.line_h(cx + 24, cx + CARD_W - 24, cy + 56, NIGHT_LGT, 1)

    # 项目列表
    for i, (time, title, desc) in enumerate(card["items"]):
        iy = cy + 70 + i * 92
        # 时间标签
        doc.rect(cx + 24, iy, 90, 26, color, radius=6, opacity=0.2)
        doc.text_c(cx + 24 + 45, iy + 4, time, 12, color_l, bold=True, owner="item_time")
        # 项目标题
        doc.text(cx + 124, iy, title, 16, WHITE, bold=True, owner="item_title")
        # 项目描述
        doc.text(cx + 124, iy + 24, desc, 14, SLATE, owner="item_desc")

# ============================================================ 底部页脚
doc.line_h(48, W - 48, H - 50, NIGHT_LGT, 1)
doc.text(48, H - 36, "夜光驿站 · 人民南站", 16, MUTED, owner="footer_brand")
doc.text_c(W // 2, H - 36, "夜里有光 · 路有驿站", 16, AMBER, bold=True, owner="footer_slogan")
doc.text_r(W - 48, H - 36, "400-888-0000", 16, AMBER, bold=True, owner="footer_phone")

# ============================================================ 干跑门禁
gates = K.dry_run(doc, "case-05", 12, [], max_parts=9000)
K.save_gates("case-05", gates, "初始版本")
K.assert_gates(gates, "case-05")

stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")
print("Gates passed:", len([g for g in gates if g['passed']]), "/", len(gates))

result = K.render_case("case-05", doc, "社区公告栏", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))