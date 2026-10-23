"""B05 case-01: FlowDay Home Dashboard
Today's schedule overview with time blocks, focus timer, and quick stats
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b05_kit as K
from b05_kit import *

W, H = 400, 800
doc = Doc(W, H, BG_WHITE)

# Status bar
doc.status_bar()

# Header
doc.bg_section(0, 40, W, 80, PRIMARY)
doc.text(20, 52, "早上好，小明 👋", 20, TEXT_WHITE, bold=True)
doc.text(20, 80, "10月23日 星期四", 14, "#C7D2FE")

# Focus timer card
doc.rect_shadow(20, 136, 360, 100, BG_WHITE, RADIUS_LG)
doc.text(36, 148, "🎯 今日专注", 14, TEXT_SECONDARY)
# Timer display
doc.circle(100, 200, 36, PRIMARY_LIGHT, 0.2)
doc.circle(100, 200, 28, PRIMARY)
doc.text_c(100, 192, "45:00", 20, TEXT_WHITE, bold=True)
# Timer controls
doc.text(180, 178, "专注中", 16, TEXT_PRIMARY, bold=True)
doc.text(180, 202, "深度工作", 13, TEXT_SECONDARY)
doc.pill(320, 178, 40, 24, PRIMARY)
doc.text_c(340, 182, "▶", 12, TEXT_WHITE)

# Today's stats row
doc.text(20, 252, "今日概览", 16, TEXT_PRIMARY, bold=True)

# Stat tiles
doc.rect_shadow(20, 280, 108, 70, BG_WHITE, RADIUS_MD)
doc.text_c(74, 292, "8/10", 20, PRIMARY, bold=True)
doc.text_c(74, 318, "任务完成", 12, TEXT_MUTED)

doc.rect_shadow(146, 280, 108, 70, BG_WHITE, RADIUS_MD)
doc.text_c(200, 292, "6.5h", 20, ACCENT_GREEN, bold=True)
doc.text_c(200, 318, "专注时长", 12, TEXT_MUTED)

doc.rect_shadow(272, 280, 108, 70, BG_WHITE, RADIUS_MD)
doc.text_c(326, 292, "🔥 5", 20, ACCENT_ORANGE, bold=True)
doc.text_c(326, 318, "连续天数", 12, TEXT_MUTED)

# Today's schedule
doc.text(20, 370, "今日日程", 16, TEXT_PRIMARY, bold=True)
doc.text_r(360, 372, "查看全部 ›", 12, PRIMARY)

schedule = [
    ("09:00 - 10:30", "团队晨会", CAT_WORK, "已完成"),
    ("10:45 - 12:00", "深度工作：项目报告", CAT_WORK, "专注中"),
    ("12:00 - 13:00", "午餐休息", CAT_BREAK, "—"),
    ("13:00 - 14:00", "客户邮件处理", CAT_WORK, "待开始"),
    ("15:00 - 15:30", "健身", CAT_HEALTH, "待开始"),
    ("16:00 - 17:00", "学习：新框架", CAT_LEARNING, "待开始"),
]

for i, (time, title, color, status) in enumerate(schedule):
    y = 400 + i * 52
    doc.time_block(20, y, 360, 44, time, title, color)
    if status == "专注中":
        doc.pill(320, y+10, 48, 22, PRIMARY)
        doc.text_c(344, y+13, "专注", 12, TEXT_WHITE, bold=True)

# Bottom navigation
doc.bottom_tab_bar(720, active_idx=0)

# Gates
gates = K.dry_run(doc, "case-01", 12, [], max_parts=9000)
K.save_gates("case-01", gates, "初始版本")
K.assert_gates(gates, "case-01")

stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")
print("Gates passed:", len([g for g in gates if g['passed']]), "/", len(gates))

result = K.render_case("case-01", doc, "FlowDay首页", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))
