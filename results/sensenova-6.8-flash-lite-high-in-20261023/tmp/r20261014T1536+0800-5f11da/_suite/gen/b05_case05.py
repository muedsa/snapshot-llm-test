"""B05 case-05: FlowDay Task Detail
Single task view with subtasks, due date, priority, and notes
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b05_kit as K
from b05_kit import *

W, H = 400, 800
doc = Doc(W, H, BG_LIGHT)

doc.status_bar(0, BG_WHITE, TEXT_PRIMARY)

# Nav bar
doc.bg_section(0, 40, W, 56, BG_WHITE)
doc.line_h(0, W, 96, BORDER_LIGHT)
doc.text(20, 58, "←", 18, TEXT_PRIMARY)
doc.text_c(200, 58, "任务详情", 16, TEXT_PRIMARY, bold=True)
doc.text_r(360, 58, "🗑️", 16, TEXT_MUTED)

# Task header card
doc.rect_shadow(20, 108, 360, 120, BG_WHITE, RADIUS_LG)
doc.rect(20, 108, 4, 120, CAT_WORK, 2)
# Priority badge
doc.pill(36, 120, 56, 24, ACCENT_ORANGE)
doc.text_c(64, 124, "高优先级", 12, TEXT_WHITE, bold=True)
# Category
doc.pill(100, 120, 44, 24, CAT_WORK + "30")
doc.text_c(122, 124, "工作", 12, CAT_WORK, bold=True)
# Title
doc.text(36, 156, "完成项目报告第三章", 20, TEXT_PRIMARY, bold=True)
# Meta
doc.text(36, 188, "📅 10月23日 · ⏱️ 预计2小时 · 📌 进行中", 12, TEXT_SECONDARY)

# Subtasks section
doc.text(20, 248, "子任务 (3/5)", 14, TEXT_PRIMARY, bold=True)
doc.text_r(360, 248, "查看全部 ›", 12, PRIMARY)

subtasks = [
    ("完成数据分析部分", True),
    ("撰写结论与建议", True),
    ("添加图表和视觉化", True),
    ("内部评审和修改", False),
    ("最终提交给客户", False),
]

for i, (title, done) in enumerate(subtasks):
    y = 276 + i * 36
    doc.rect(20, y, 360, 32, BG_WHITE, RADIUS_SM)
    doc.checkbox(32, y+4, 20, done, PRIMARY)
    color = TEXT_MUTED if done else TEXT_PRIMARY
    doc.text(60, y+6, title, 13, color, bold=not done)
    if done:
        # strikethrough effect
        doc.line_h(60, 60+len(title)*13, y+16, TEXT_MUTED, 1)

# Progress
doc.divider(20, 460, 360)
doc.text(20, 472, "完成进度", 13, TEXT_PRIMARY, bold=True)
doc.progress_bar(20, 496, 280, 8, 0.6, PRIMARY, BG_MUTED)
doc.text_r(360, 490, "60%", 14, PRIMARY, bold=True)

# Notes section
doc.text(20, 524, "📝 备注", 14, TEXT_PRIMARY, bold=True)
doc.rect(20, 548, 360, 80, BG_WHITE, RADIUS_MD)
doc.text(32, 560, "第三章主要包含：", 13, TEXT_PRIMARY)
doc.text(32, 580, "• 数据分析结果汇总", 13, TEXT_SECONDARY)
doc.text(32, 600, "• 可视化图表（需确认数据源）", 13, TEXT_SECONDARY)

# Collaborators
doc.text(20, 644, "👥 协作者", 14, TEXT_PRIMARY, bold=True)
collabs = [("张", "#3B82F6", "张伟"), ("李", "#10B981", "李明"), ("王", "#F59E0B", "王芳")]
for i, (letter, color, name) in enumerate(collabs):
    x = 32 + i * 36
    doc.avatar(x+14, 676, 14, color, letter)
    doc.text_c(x+14, 696, name, 12, TEXT_MUTED)

# Action buttons
doc.rect(20, 716, 170, 44, BG_MUTED, RADIUS_MD)
doc.text_c(105, 730, "🏷️ 添加标签", 13, TEXT_SECONDARY)
doc.rect(210, 716, 170, 44, PRIMARY, RADIUS_MD)
doc.text_c(295, 730, "标记完成", 14, TEXT_WHITE, bold=True)

# Gates
gates = K.dry_run(doc, "case-05", 12, [], max_parts=9000)
K.save_gates("case-05", gates, "初始版本")
K.assert_gates(gates, "case-05")

stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")

result = K.render_case("case-05", doc, "FlowDay任务详情", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))
