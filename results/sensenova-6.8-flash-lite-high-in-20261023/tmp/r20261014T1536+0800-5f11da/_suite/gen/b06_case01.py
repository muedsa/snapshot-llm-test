"""B06 case-01: 药品服用时间可视化
Problem: Drug dosage schedules are confusing with text-only instructions
Solution: Visual timeline showing when to take each dose
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b06_kit as K
from b06_kit import *

W, H = 800, 600
doc = Doc(W, H, BG_WHITE)

# Header
doc.text(40, 30, "药品服用指南", 28, TEXT_PRIMARY, bold=True)
doc.text(40, 68, "阿莫西林胶囊 500mg", 18, TEXT_SECONDARY)
doc.text_r(760, 40, "每日3次", 14, ACCENT_RED, bold=True)

# Timeline background
doc.rect(40, 110, 720, 320, BG_LIGHT, 16)

# Time axis
doc.line_h(60, 740, 250, BORDER, 2)

# Dose times
doses = [
    (100, "08:00", "早餐前", "空腹服用", ACCENT_BLUE),
    (260, "14:00", "午餐后", "饭后服用", ACCENT_GREEN),
    (420, "20:00", "晚餐后", "饭后服用", ACCENT_GREEN),
]

for x, time, meal, instruction, color in doses:
    # Time circle
    doc.circle(x, 250, 20, color)
    doc.text_c(x, 242, time, 14, TEXT_LIGHT, bold=True)
    # Label above
    doc.text_c(x, 200, meal, 16, TEXT_PRIMARY, bold=True)
    doc.text_c(x, 222, instruction, 12, TEXT_SECONDARY)
    # Dose icon below
    doc.rect(x-16, 290, 32, 20, color + "40", 4)
    doc.text_c(x, 294, "1粒", 12, color, bold=True)

# Interval labels
doc.text_c(180, 265, "间隔6h", 12, TEXT_SECONDARY)
doc.text_c(340, 265, "间隔6h", 12, TEXT_SECONDARY)

# Important notes section
doc.rect(40, 460, 720, 100, BG_LIGHT, 12)
doc.text(60, 475, "注意事项", 16, TEXT_PRIMARY, bold=True)
notes = [
    "每日总量不超过3粒",
    "服药期间禁止饮酒",
    "如有过敏史请遵医嘱",
    "疗程一般7-10天",
]
for i, note in enumerate(notes):
    doc.text(60, 500 + i*18, "•", 12, ACCENT_RED)
    doc.text(76, 500 + i*18, note, 13, TEXT_SECONDARY)

# Footer
doc.text(40, 580, "数据来源：药品说明书（演示用途）", 12, TEXT_SECONDARY)

gates = K.dry_run(doc, "case-01", 12, [], max_parts=9000)
K.save_gates("case-01", gates, "初始版本")
K.assert_gates(gates, "case-01")

stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")

result = K.render("case-01", doc, "药品服用时间可视化", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))
