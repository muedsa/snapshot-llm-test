"""B02 case-07: 工人故事特写 (Worker Story Feature)
1200x1200, dark theme, social media story feature.
"""
import sys, os, json, math
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
ROSE      = "#FB7185"
ROSE_L    = "#FDA4AF"
PURPLE    = "#8B5CF6"
PURPLE_L  = "#A78BFA"

W, H = 1200, 1200
doc = K.Doc(W, H, NIGHT)

# ============================================================ 背景装饰
# 左上角光晕
for i in range(8, 0, -1):
    doc.rect(-i * 60, -i * 60, i * 180, i * 180,
             ROSE, radius=i * 90, opacity=0.03 * i)

# 右下角光晕
for i in range(8, 0, -1):
    doc.rect(W - i * 60 - 120, H - i * 60 - 120, i * 180, i * 180,
             AMBER, radius=i * 90, opacity=0.03 * i)

# ============================================================ 顶部品牌区
doc.text(60, 40, "夜光驿站", 28, WHITE, bold=True, owner="brand")
doc.text(60 + K.tw("夜光驿站", 28) + 16, 48, "工人故事 · 第 47 期", 20, AMBER, bold=True, owner="series")

# 右上角：日期
doc.text_r(W - 60, 44, "2026年10月", 18, SLATE, owner="date")

# 分割线
doc.line_h(60, W - 60, 88, NIGHT_LGT, 1)

# ============================================================ 故事人物区
# 人物头像
avatar_cx, avatar_cy = 180, 240
avatar_r = 100

# 外圈光晕
for i in range(5, 0, -1):
    doc.rect(avatar_cx - avatar_r - i * 20, avatar_cy - avatar_r - i * 20,
             (avatar_r + i * 20) * 2, (avatar_r + i * 20) * 2,
             ROSE, radius=avatar_r + i * 20, opacity=0.06 * i)

# 头像圆底
doc.rect(avatar_cx - avatar_r, avatar_cy - avatar_r,
         avatar_r * 2, avatar_r * 2, ROSE, radius=avatar_r, opacity=0.25)

# 头像： initials
doc.text_c(avatar_cx, avatar_cy - 30, "王", 56, ROSE_L, bold=True, owner="avatar_char")

# 职业标签
doc.rect(avatar_cx - 80, avatar_cy + 50, 160, 32, ROSE, radius=16, opacity=0.3)
doc.text_c(avatar_cx, avatar_cy + 54, "夜班司机", 16, ROSE_L, bold=True, owner="job_label")

# ============================================================ 人物信息
info_x = 320
info_y = 140

# 姓名
doc.text(info_x, info_y, "王建国", 48, WHITE, bold=True, owner="name")

# 年龄和工作年限
doc.text(info_x, info_y + 60, "45 岁 · 夜班 15 年", 24, SLATE, owner="age")

# 所属驿站
doc.text(info_x, info_y + 100, "所属驿站：物流园站", 20, MUTED, owner="station")

# 分割线
doc.line_h(info_x, W - 60, info_y + 140, NIGHT_LGT, 1)

# ============================================================ 引语区
quote_y = 340

# 引号装饰
doc.text(60, quote_y - 80, "「", 60, AMBER, bold=True, owner="quote_open")

# 引语正文
quote_text = "凌晨的高速路，只有路灯陪着我。"
quote_sub = "但我从不觉得孤独，因为我知道，"
quote_sub2 = "在我休息的驿站里，有一杯热粥等我。"

doc.text(100, quote_y + 20, quote_text, 36, WHITE, bold=True, owner="quote_main")
doc.text(100, quote_y + 80, quote_sub, 24, SLATE, owner="quote_sub1")
doc.text(100, quote_y + 120, quote_sub2, 24, SLATE, owner="quote_sub2")

# 引语结束
doc.text(100, quote_y + 180, "」", 40, AMBER, bold=True, owner="quote_close")

# 分割线
doc.line_h(60, W - 60, quote_y + 220, NIGHT_LGT, 1)

# ============================================================ 故事时间线
timeline_y = quote_y + 250

# 时间线标题
doc.text(60, timeline_y, "他的夜班故事", 24, WHITE, bold=True, owner="timeline_title")

# 时间线事件
events = [
    ("2011", "开始跑夜班", "当时 30 岁，为了孩子上学"),
    ("2016", "第一次听说驿站", "一个司机朋友推荐的"),
    ("2018", "成为常驻用户", "每周至少去 4 次"),
    ("2024", "成为志愿烹饪者", "每月轮值 2 次，做夜宵"),
]

for i, (year, title, desc) in enumerate(events):
    ey = timeline_y + 40 + i * 80
    # 年份
    doc.rect(60, ey, 80, 30, AMBER, radius=6, opacity=0.2)
    doc.text_c(60 + 40, ey + 5, year, 16, AMBER, bold=True, owner="event_year")

    # 事件标题
    doc.text(160, ey, title, 18, WHITE, bold=True, owner="event_title")

    # 描述
    doc.text(160, ey + 26, desc, 16, SLATE, owner="event_desc")

# ============================================================ 底部统计
stats_y = timeline_y + 380

# 分割线
doc.line_h(60, W - 60, stats_y, NIGHT_LGT, 1)

# 统计数据
stats = [
    ("15", "年夜班", AMBER),
    ("2,400+", "次休息", GREEN),
    ("48", "次志愿", ROSE),
    ("12", "个朋友", PURPLE),
]

for i, (num, label, color) in enumerate(stats):
    sx = 60 + i * 280
    # 数字
    doc.text_c(sx + 60, stats_y + 24, num, 36, color, bold=True, owner="stat_num")
    # 标签
    doc.text_c(sx + 60, stats_y + 72, label, 16, SLATE, owner="stat_label")

# ============================================================ 底部品牌条
doc.rect(0, H - 60, W, 60, AMBER, radius=0, opacity=0.1)
doc.text_c(W // 2, H - 44, "夜光驿站 · 夜里有光，路有驿站", 20, AMBER, bold=True, owner="footer")

# ============================================================ 装饰光斑
for i in range(6, 0, -1):
    doc.rect(W - 120, H // 2 + i * 30, 6, 6, AMBER_L, radius=3, opacity=0.2 * i / 6)

# ============================================================ 干跑门禁
gates = K.dry_run(doc, "case-07", 16, [], max_parts=9000)
K.save_gates("case-07", gates, "初始版本")
K.assert_gates(gates, "case-07")

stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")
print("Gates passed:", len([g for g in gates if g['passed']]), "/", len(gates))

result = K.render_case("case-07", doc, "工人故事特写", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))