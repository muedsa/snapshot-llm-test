"""B02 case-08: 月度健康检查卡 (Monthly Health Check Card)
540x1600, dark theme, health data card with charts.
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
GREEN     = "#10B981"
GREEN_L   = "#34D399"
CYAN      = "#06B6D4"
CYAN_L    = "#67E8F9"
ROSE      = "#FB7185"
ROSE_L    = "#FDA4AF"
RED       = "#EF4444"

W, H = 540, 1600
doc = K.Doc(W, H, NIGHT)

# ============================================================ 顶部品牌区
doc.text(32, 24, "夜光驿站", 24, WHITE, bold=True, owner="brand")
doc.text(32 + K.tw("夜光驿站", 24) + 16, 32, "月度健康检查", 18, AMBER, bold=True, owner="title")

# 日期
doc.text_r(W - 32, 28, "2026-10", 16, SLATE, owner="date")

# 分割线
doc.line_h(32, W - 32, 58, NIGHT_LGT, 1)

# ============================================================ 用户信息
user_y = 76
doc.text(32, user_y, "李建国", 28, WHITE, bold=True, owner="user_name")
doc.text(32, user_y + 36, "夜班护士 · 工号 0847", 14, SLATE, owner="user_info")

# ============================================================ 月度概览
overview_y = user_y + 76
doc.text(32, overview_y, "月度概览", 20, WHITE, bold=True, owner="overview_title")

# 睡眠时长
doc.rect(32, overview_y + 32, 120, 64, CYAN, radius=8, opacity=0.15)
doc.text(44, overview_y + 40, "5.2h", 28, CYAN_L, bold=True, owner="sleep_val")
doc.text(44, overview_y + 76, "平均睡眠", 12, CYAN_L, owner="sleep_label")

# 体检次数
doc.rect(164, overview_y + 32, 120, 64, GREEN, radius=8, opacity=0.15)
doc.text(176, overview_y + 40, "3", 28, GREEN_L, bold=True, owner="check_val")
doc.text(176, overview_y + 76, "健康检查", 12, GREEN_L, owner="check_label")

# 热食次数
doc.rect(296, overview_y + 32, 120, 64, AMBER, radius=8, opacity=0.15)
doc.text(308, overview_y + 40, "28", 28, AMBER_L, bold=True, owner="meal_val")
doc.text(308, overview_y + 76, "次热食", 12, AMBER_L, owner="meal_label")

# 志愿者时长
doc.rect(428, overview_y + 32, 80, 64, ROSE, radius=8, opacity=0.15)
doc.text(440, overview_y + 40, "6h", 28, ROSE_L, bold=True, owner="vol_val")
doc.text(440, overview_y + 76, "志愿时长", 12, ROSE_L, owner="vol_label")

# ============================================================ 分割线
doc.line_h(32, W - 32, overview_y + 110, NIGHT_LGT, 1)

# ============================================================ 睡眠趋势
sleep_y = overview_y + 130
doc.text(32, sleep_y, "睡眠趋势", 20, WHITE, bold=True, owner="sleep_title")

# 7 天睡眠数据
sleep_data = [5.2, 4.8, 5.5, 4.2, 5.0, 5.8, 5.2]  # 小时
chart_x, chart_y = 32, sleep_y + 36
chart_w, chart_h = W - 64, 120
max_val = 8.0
bar_w = (chart_w - 6 * 8) / 7

# 背景网格线
for i in range(0, 5):
    gy = chart_y + chart_h - (i * chart_h / 4)
    doc.line_h(chart_x, chart_x + chart_w, gy, NIGHT_MID, 1)

# 柱状图
for i, val in enumerate(sleep_data):
    bx = chart_x + i * (bar_w + 8)
    bh = (val / max_val) * chart_h
    by = chart_y + chart_h - bh
    # 柱状图
    doc.rect(bx, by, bar_w, bh, CYAN, radius=4)
    # 数值标签
    doc.text_c(bx + bar_w / 2, by - 20, "%.1f" % val, 12, CYAN_L, bold=True, owner="sleep_bar_val")

# X 轴标签
days = ["一", "二", "三", "四", "五", "六", "日"]
for i, day in enumerate(days):
    dx = chart_x + i * (bar_w + 8) + bar_w / 2
    doc.text_c(dx, chart_y + chart_h + 8, day, 12, SLATE, owner="day_label")

# 目标线
target_y = chart_y + chart_h - (6.5 / max_val) * chart_h
doc.line_h(chart_x, chart_x + chart_w, target_y, GREEN, 1)
doc.text(chart_x + 4, target_y - 16, "目标 6.5h", 12, GREEN, bold=True, owner="target_label")

# ============================================================ 分割线
doc.line_h(32, W - 32, chart_y + chart_h + 40, NIGHT_LGT, 1)

# ============================================================ 压力水平
stress_y = chart_y + chart_h + 60
doc.text(32, stress_y, "压力水平", 20, WHITE, bold=True, owner="stress_title")

# 压力评分
stress_score = 6.2  # / 10
stress_y_pos = stress_y + 36

# 进度条背景
doc.rect(32, stress_y_pos, W - 64, 24, NIGHT_MID, radius=12)
# 进度条前景
stress_w = (stress_score / 10) * (W - 64)
doc.rect(32, stress_y_pos, stress_w, 24, AMBER, radius=12)

# 评分文字
doc.text(32, stress_y_pos + 32, "%.1f / 10" % stress_score, 28, WHITE, bold=True, owner="stress_val")

# 压力建议
doc.text(32, stress_y_pos + 72, "建议：增加运动 · 减少咖啡因 · 保证午休", 14, SLATE, owner="stress_advice")

# ============================================================ 分割线
doc.line_h(32, W - 32, stress_y_pos + 100, NIGHT_LGT, 1)

# ============================================================ 健康检查记录
record_y = stress_y_pos + 120
doc.text(32, record_y, "健康检查记录", 20, WHITE, bold=True, owner="record_title")

records = [
    ("10-28", "血压 118/76", "正常", GREEN),
    ("10-21", "血压 122/80", "正常", GREEN),
    ("10-14", "血压 128/84", "偏高", AMBER),
    ("10-07", "血压 115/72", "正常", GREEN),
]

for i, (date, data, status, color) in enumerate(records):
    ry = record_y + 32 + i * 52
    # 日期
    doc.text(32, ry, date, 16, SLATE, owner="rec_date")
    # 数据
    doc.text(100, ry, data, 16, WHITE, bold=True, owner="rec_data")
    # 状态标签
    tag_w = K.tw(status, 12) + 16
    doc.rect(W - 32 - tag_w, ry - 4, tag_w, 22, color, radius=11, opacity=0.2)
    doc.text_c(W - 32 - tag_w / 2, ry - 1, status, 12, color, bold=True, owner="rec_status")

# ============================================================ 分割线
doc.line_h(32, W - 32, record_y + 32 + 4 * 52, NIGHT_LGT, 1)

# ============================================================ 建议
advice_y = record_y + 32 + 4 * 52 + 20
doc.text(32, advice_y, "健康建议", 20, WHITE, bold=True, owner="advice_title")

advices = [
    "本周睡眠不足，建议增加午休 30 分钟",
    "血压偏高，请减少盐分摄入",
    "保持每周 3 次运动习惯",
    "下月体检提醒：11-15 血检",
]

for i, advice in enumerate(advices):
    ay = advice_y + 32 + i * 32
    # 建议点
    doc.rect(36, ay + 8, 8, 8, AMBER, radius=4)
    doc.text(56, ay, advice, 14, SLATE, owner="advice_item")

# ============================================================ 底部品牌
doc.rect(0, H - 60, W, 60, AMBER, radius=0, opacity=0.1)
doc.text_c(W // 2, H - 44, "夜光驿站 · 夜里有光", 18, AMBER, bold=True, owner="footer_brand")
doc.text_c(W // 2, H - 20, "健康是夜班最好的礼物", 12, AMBER_L, owner="footer_slogan")

# ============================================================ 干跑门禁
gates = K.dry_run(doc, "case-08", 12, [], max_parts=9000)
K.save_gates("case-08", gates, "初始版本")
K.assert_gates(gates, "case-08")

stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")
print("Gates passed:", len([g for g in gates if g['passed']]), "/", len(gates))

result = K.render_case("case-08", doc, "月度健康检查卡", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))