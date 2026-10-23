"""B05 case-04: FlowDay Week Calendar
Weekly overview with color-coded task categories
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b05_kit as K
from b05_kit import *

W, H = 400, 800
doc = Doc(W, H, BG_WHITE)

doc.status_bar()
doc.nav_bar(40, "十月 2026", True, "🔍")

# Month navigation
doc.text_c(60, 108, "‹", 18, TEXT_MUTED)
doc.text_c(200, 108, "10月23日", 16, TEXT_PRIMARY, bold=True)
doc.text_c(340, 108, "›", 18, TEXT_MUTED)

# Week day headers
days_w = ["一", "二", "三", "四", "五", "六", "日"]
for i, d in enumerate(days_w):
    x = 20 + i * 52
    color = PRIMARY if i == 3 else TEXT_MUTED
    doc.text_c(x+22, 148, d, 12, color, bold=(i == 3))

# Calendar grid (October 2026)
# Oct 1 is Thursday, so week starts Oct 1 (col 3)
oct_days = list(range(1, 32))
weeks = [
    [None, None, None, 1, 2, 3, 4],
    [5, 6, 7, 8, 9, 10, 11],
    [12, 13, 14, 15, 16, 17, 18],
    [19, 20, 21, 22, 23, 24, 25],
    [26, 27, 28, 29, 30, 31, None],
]

# Event colors for specific days
events = {1: CAT_WORK, 5: CAT_HEALTH, 8: CAT_LEARNING, 12: CAT_WORK,
          15: CAT_PERSONAL, 18: CAT_SOCIAL, 20: CAT_WORK, 22: CAT_LEARNING,
          23: CAT_WORK, 25: CAT_HEALTH, 28: CAT_PERSONAL, 30: CAT_SOCIAL}

# Draw full calendar
row_y = 172
for row in weeks:
    for i, day in enumerate(row):
        x = 20 + i * 52
        if day is None:
            continue
        is_today = day == 23
        has_event = day in events
        event_color = events.get(day, ACCENT_BLUE)
        doc.date_pill(x, row_y, 44, 44, "", day, selected=is_today,
                      has_event=has_event, event_color=event_color)
    row_y += 48

# Legend
doc.divider(20, row_y + 20, 360)
doc.text(20, row_y + 30, "分类", 13, TEXT_PRIMARY, bold=True)
categories = [("工作", CAT_WORK), ("学习", CAT_LEARNING), ("健康", CAT_HEALTH),
              ("社交", CAT_SOCIAL), ("个人", CAT_PERSONAL)]
for i, (name, color) in enumerate(categories):
    x = 20 + i * 72
    doc.rect(x, row_y + 52, 12, 12, color, radius=3)
    doc.text(x + 18, row_y + 52, name, 12, TEXT_SECONDARY)

# Today's schedule preview
doc.text(20, row_y + 80, "今日安排", 14, TEXT_PRIMARY, bold=True)
today_items = [
    ("09:00", "团队晨会", CAT_WORK),
    ("10:45", "深度工作", CAT_WORK),
    ("15:00", "健身", CAT_HEALTH),
]
for i, (time, title, color) in enumerate(today_items):
    y = row_y + 104 + i * 28
    doc.rect(20, y, 4, 24, color, radius=2)
    doc.text(32, y, time, 12, TEXT_MUTED)
    doc.text(68, y, title, 12, TEXT_PRIMARY)

# Bottom nav
doc.bottom_tab_bar(720, active_idx=1)

# Gates
gates = K.dry_run(doc, "case-04", 12, [], max_parts=9000)
K.save_gates("case-04", gates, "初始版本")
K.assert_gates(gates, "case-04")

stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")

result = K.render_case("case-04", doc, "FlowDay周历", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))
