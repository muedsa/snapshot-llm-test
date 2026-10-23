"""B05 case-06: FlowDay Onboarding
First-run setup wizard for goals and preferences
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b05_kit as K
from b05_kit import *

W, H = 400, 800
doc = Doc(W, H, BG_WHITE)

doc.status_bar()

# Step indicator
doc.text_c(200, 60, "第 2/5 步", 13, TEXT_MUTED)
doc.progress_bar(60, 80, 280, 4, 0.4, PRIMARY, BG_MUTED)

# Main content
doc.text_c(200, 140, "你的主要目标是什么？", 22, TEXT_PRIMARY, bold=True)
doc.text_c(200, 176, "选择最符合你当前需求的目标", 14, TEXT_SECONDARY)

# Goal cards (selectable)
goals = [
    ("🎯", "提高效率", "管理时间和任务，减少拖延", CAT_WORK, True),
    ("💪", "健康生活", "追踪运动、饮食和睡眠", CAT_HEALTH, False),
    ("📚", "持续学习", "学习计划和新技能", CAT_LEARNING, False),
    ("👥", "社交平衡", "维护人际关系", CAT_SOCIAL, False),
]

for i, (icon, title, desc, color, selected) in enumerate(goals):
    y = 210 + i * 72
    bg = color + "15" if selected else BG_LIGHT
    border = color if selected else BORDER_LIGHT
    doc.rect(20, y, 360, 60, bg, RADIUS_MD, stroke=border, stroke_width=2 if selected else 1)
    doc.circle(48, y+30, 20, color if selected else BG_MUTED)
    doc.text_c(48, y+22, icon, 16, TEXT_WHITE if selected else TEXT_SECONDARY)
    doc.text(78, y+12, title, 16, TEXT_PRIMARY, bold=True)
    doc.text(78, y+34, desc, 12, TEXT_SECONDARY)
    if selected:
        doc.checkbox(350, y+20, 20, True, PRIMARY)

# Bottom actions
doc.divider(20, 540, 360)
doc.text_c(200, 560, "或自定义你的目标组合", 13, TEXT_MUTED)

# Navigation buttons
doc.rect(20, 620, 170, 48, BG_MUTED, RADIUS_MD)
doc.text_c(105, 636, "上一步", 15, TEXT_SECONDARY, bold=True)
doc.rect(210, 620, 170, 48, PRIMARY, RADIUS_MD)
doc.text_c(295, 636, "继续", 15, TEXT_WHITE, bold=True)

# Bottom text
doc.text_c(200, 700, "你也可以稍后在设置中调整", 12, TEXT_MUTED)
doc.text_c(200, 724, "跳过", 13, PRIMARY)

# Gates
gates = K.dry_run(doc, "case-06", 12, [], max_parts=9000)
K.save_gates("case-06", gates, "初始版本")
K.assert_gates(gates, "case-06")

stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")

result = K.render_case("case-06", doc, "FlowDay引导设置", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))
