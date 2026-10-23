"""B05 case-10: FlowDay Achievements
Gamification with streaks, badges, and leaderboard
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b05_kit as K
from b05_kit import *

W, H = 400, 800
doc = Doc(W, H, BG_WHITE)

doc.status_bar()

# Header with streak
doc.bg_section(0, 40, W, 120, PRIMARY)
doc.text(24, 56, "←", 18, "#C7D2FE")
doc.text_c(200, 56, "成就", 16, TEXT_WHITE, bold=True)
# Streak display
doc.text_c(200, 96, "🔥 12天连续", 20, TEXT_WHITE, bold=True)
doc.text_c(200, 124, "保持专注，超越自我！", 13, "#C7D2FE")

# Current level
doc.rect_shadow(20, 176, 360, 80, BG_WHITE, RADIUS_LG)
doc.avatar(56, 216, 24, ACCENT_ORANGE, "明")
doc.text(96, 188, "效率达人 · Lv.7", 16, TEXT_PRIMARY, bold=True)
doc.text(96, 212, "距下一等级还需 450分", 12, TEXT_SECONDARY)
doc.progress_bar(96, 232, 240, 8, 0.72, PRIMARY, BG_MUTED)

# Badges section
doc.text(20, 280, "徽章收集", 15, TEXT_PRIMARY, bold=True)
doc.text_r(360, 280, "全部 (24) ›", 12, PRIMARY)

# Badge grid
badges = [
    ("🎯", "专注大师", "100小时", True, PRIMARY),
    ("🔥", "坚持不懈", "30天连续", True, ACCENT_ORANGE),
    ("💎", "完美一周", "7天全勤", True, ACCENT_GREEN),
    ("🚀", "效率达人", "评分90+", True, ACCENT_PURPLE),
    ("📚", "学习之星", "50本书", False, BORDER_MED),
    ("💪", "健身达人", "100次运动", False, BORDER_MED),
    ("🌙", "早起鸟儿", "30天早起", False, BORDER_MED),
    ("🏆", "月度冠军", "月度第一", False, BORDER_MED),
]

for i, (icon, title, desc, unlocked, color) in enumerate(badges):
    row = i // 4
    col = i % 4
    x = 20 + col * 92
    y = 310 + row * 80
    bg = BG_LIGHT if unlocked else BG_MUTED
    doc.rect_shadow(x, y, 80, 72, bg, RADIUS_MD)
    doc.circle(x+40, y+24, 18, color if unlocked else BORDER_LIGHT)
    doc.text_c(x+40, y+16, icon, 14, TEXT_WHITE if unlocked else TEXT_MUTED)
    doc.text_c(x+40, y+48, title, 12, TEXT_PRIMARY if unlocked else TEXT_MUTED)

# Leaderboard
doc.divider(20, 490, 360)
doc.text(20, 502, "本周排行", 15, TEXT_PRIMARY, bold=True)
doc.text_r(360, 502, "全部 ›", 12, PRIMARY)

leaderboard = [
    ("🥇", "张伟", "98分", "12h", True),
    ("🥈", "你", "94分", "10h", True),
    ("🥉", "李明", "87分", "8h", False),
    ("4", "王芳", "82分", "7h", False),
    ("5", "赵强", "76分", "6h", False),
]

for i, (rank, name, score, hours, is_user) in enumerate(leaderboard):
    y = 530 + i * 36
    bg = PRIMARY + "15" if is_user else BG_LIGHT
    doc.rect(20, y, 360, 32, bg, RADIUS_SM)
    doc.text(32, y+4, rank, 14, TEXT_PRIMARY if is_user else TEXT_MUTED, bold=True)
    doc.text(64, y+4, name, 13, TEXT_PRIMARY, bold=is_user)
    doc.text_r(200, y+4, f"{score}分", 12, PRIMARY if is_user else TEXT_SECONDARY)
    doc.text_r(280, y+4, f"{hours}", 12, TEXT_MUTED)
    if is_user:
        doc.pill(320, y+4, 40, 22, PRIMARY)
        doc.text_c(340, y+7, "当前", 12, TEXT_WHITE, bold=True)

# Weekly goal
doc.rect_shadow(20, 720, 360, 60, BG_WHITE, RADIUS_MD)
doc.text(36, 732, "🎯 本周目标", 13, TEXT_PRIMARY, bold=True)
doc.progress_bar(36, 756, 240, 8, 0.85, ACCENT_GREEN, BG_MUTED)
doc.text_r(360, 748, "85%", 16, ACCENT_GREEN, bold=True)

# Gates
gates = K.dry_run(doc, "case-10", 12, [], max_parts=9000)
K.save_gates("case-10", gates, "初始版本")
K.assert_gates(gates, "case-10")

stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")

result = K.render_case("case-10", doc, "FlowDay成就", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))
