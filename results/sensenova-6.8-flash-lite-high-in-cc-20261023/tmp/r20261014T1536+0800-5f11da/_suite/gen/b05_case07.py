"""B05 case-07: FlowDay Stats & Insights
Productivity metrics, weekly trends, and achievements
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b05_kit as K
from b05_kit import *

W, H = 400, 800
doc = Doc(W, H, BG_LIGHT)

doc.status_bar(0, BG_WHITE, TEXT_PRIMARY)
doc.nav_bar(40, "统计与洞察", False, "⚙️")

# Time period selector
doc.chip(20, 108, "本周", BG_MUTED, TEXT_SECONDARY, selected=True)
doc.chip(88, 108, "本月", BG_WHITE, TEXT_SECONDARY)
doc.chip(156, 108, "全部", BG_WHITE, TEXT_SECONDARY)

# Overview stats
doc.text(20, 160, "本周概览", 16, TEXT_PRIMARY, bold=True)

stats_row = [
    ("🎯", "87", "任务完成", PRIMARY),
    ("⏱️", "42h", "专注时长", ACCENT_GREEN),
    ("🔥", "12", "连续天数", ACCENT_ORANGE),
    ("⚡", "94%", "效率评分", ACCENT_PURPLE),
]

for i, (icon, value, label, color) in enumerate(stats_row):
    x = 20 + i * 92
    doc.rect_shadow(x, 188, 80, 72, BG_WHITE, RADIUS_MD)
    doc.text_c(x+40, 200, icon, 18, TEXT_MUTED)
    doc.text_c(x+40, 224, value, 20, color, bold=True)
    doc.text_c(x+40, 248, label, 12, TEXT_MUTED)

# Weekly chart
doc.text(20, 290, "专注时长趋势", 15, TEXT_PRIMARY, bold=True)
doc.rect_shadow(20, 312, 360, 140, BG_WHITE, RADIUS_MD)

# Bar chart data
days = ["一", "二", "三", "四", "五", "六", "日"]
hours = [6, 8, 5, 7, 4, 3, 9]
max_h = 10
chart_x, chart_y, chart_w, chart_h = 40, 328, 320, 100

for i, (d, h) in enumerate(zip(days, hours)):
    x = chart_x + i * 44
    bar_h = int(h / max_h * chart_h)
    color = PRIMARY if h == max_h else PRIMARY_LIGHT
    # Bar
    doc.rect(x+8, chart_y + chart_h - bar_h, 24, bar_h, color, radius=4)
    # Day label
    doc.text_c(x+20, chart_y + chart_h + 8, d, 12, TEXT_MUTED)

# Achievements section
doc.text(20, 480, "成就徽章", 15, TEXT_PRIMARY, bold=True)
doc.text_r(360, 480, "全部 ›", 12, PRIMARY)

achievements = [
    ("🎯", "专注大师", "累计专注100小时", True),
    ("🔥", "坚持不懈", "连续30天打卡", True),
    ("💎", "完美一周", "7天全勤", False),
    ("🚀", "效率达人", "效率评分>90%", True),
]

for i, (icon, title, desc, unlocked) in enumerate(achievements):
    x = 20 + i * 92
    y = 510
    bg = BG_WHITE if unlocked else BG_MUTED
    doc.rect_shadow(x, y, 80, 80, bg, RADIUS_MD)
    doc.circle(x+40, y+30, 24, PRIMARY if unlocked else BORDER_MED)
    doc.text_c(x+40, y+22, icon, 18, TEXT_WHITE if unlocked else TEXT_MUTED)
    doc.text_c(x+40, y+60, title, 12, TEXT_PRIMARY if unlocked else TEXT_MUTED)

# Activity feed
doc.text(20, 620, "近期活动", 15, TEXT_PRIMARY, bold=True)

activities = [
    ("完成", "项目报告第三章", "1小时前", ACCENT_GREEN),
    ("开始", "深度工作模式", "3小时前", PRIMARY),
    ("完成", "客户邮件处理", "5小时前", ACCENT_GREEN),
]

for i, (action, title, time, color) in enumerate(activities):
    y = 648 + i * 36
    doc.circle(32, y+8, 8, color)
    doc.text_c(32, y+4, "✓" if "完成" in action else "▶", 12, TEXT_WHITE)
    doc.text(48, y, f"{action}：{title}", 13, TEXT_PRIMARY)
    doc.text_r(370, y+2, time, 12, TEXT_MUTED)

# Bottom nav
doc.bottom_tab_bar(720, active_idx=3)

# Gates
gates = K.dry_run(doc, "case-07", 12, [], max_parts=9000)
K.save_gates("case-07", gates, "初始版本")
K.assert_gates(gates, "case-07")

stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")

result = K.render_case("case-07", doc, "FlowDay统计洞察", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))
