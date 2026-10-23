"""B05 case-02: FlowDay Day Planner
Detailed hourly schedule with draggable time blocks
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b05_kit as K
from b05_kit import *

W, H = 400, 800
doc = Doc(W, H, BG_LIGHT)

# Status bar
doc.status_bar(0, BG_LIGHT, TEXT_PRIMARY)

# Navigation bar
doc.nav_bar(40, "10月23日 周四", True, "⋯")

# Date selector pills
days = [("一", 20), ("二", 21), ("三", 22), ("四", 23), ("五", 24), ("六", 25), ("日", 26)]
for i, (dname, dnum) in enumerate(days):
    x = 20 + i * 52
    doc.week_pill(x, 108, 44, 52, dname, dnum, selected=(dnum == 23))

# Summary bar
doc.rect_shadow(20, 176, 360, 44, BG_WHITE, RADIUS_MD)
doc.text(36, 188, "📊 今日：8任务 · 6.5h专注 · 72%完成", 13, TEXT_SECONDARY)
doc.pill(320, 184, 44, 24, PRIMARY)
doc.text_c(342, 188, "编辑", 12, TEXT_WHITE, bold=True)

# Time labels and schedule blocks
doc.text(20, 238, "时间", 12, TEXT_MUTED)
doc.divider(60, 248, 320)

blocks = [
    (248, "09:00", "团队晨会", 48, CAT_WORK, "9AM"),
    (308, "10:45", "深度工作：项目报告", 56, CAT_WORK, "10AM"),
    (376, "12:00", "午餐休息", 40, CAT_BREAK, "12PM"),
    (428, "13:00", "客户邮件处理", 48, CAT_WORK, "1PM"),
    (488, "14:00", "代码审查", 48, CAT_WORK, "2PM"),
    (548, "15:00", "健身", 40, CAT_HEALTH, "3PM"),
    (600, "16:00", "学习：React 18", 48, CAT_LEARNING, "4PM"),
    (660, "17:30", "下班 · 自由时间", 48, CAT_BREAK, "5PM"),
]

for y, time_str, title, h, color, label in blocks:
    # Time label
    doc.text_r(56, y+8, time_str, 12, TEXT_MUTED)
    # Time block
    doc.time_block(64, y, 316, h-6, "", title, color)

# Bottom navigation
doc.bottom_tab_bar(720, active_idx=1)

# Gates
gates = K.dry_run(doc, "case-02", 12, [], max_parts=9000)
K.save_gates("case-02", gates, "初始版本")
K.assert_gates(gates, "case-02")

stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")

result = K.render_case("case-02", doc, "FlowDay日计划", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))
