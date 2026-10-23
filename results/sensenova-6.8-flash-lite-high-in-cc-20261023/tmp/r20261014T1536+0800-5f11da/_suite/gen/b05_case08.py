"""B05 case-08: FlowDay Quick Add
Fast task capture interface with smart suggestions
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b05_kit as K
from b05_kit import *

W, H = 400, 800
doc = Doc(W, H, BG_WHITE)

doc.status_bar()

# Header
doc.text(24, 56, "←", 18, TEXT_MUTED)
doc.text_c(200, 56, "快速添加", 16, TEXT_PRIMARY, bold=True)
doc.text_r(360, 56, "取消", 14, PRIMARY)

# Input area
doc.rect(20, 100, 360, 120, BG_MUTED, RADIUS_LG)
doc.text(36, 116, "📝", 20, TEXT_MUTED)
doc.text(36, 144, "今天需要完成项目报告第三章...", 18, TEXT_PRIMARY, bold=True)
doc.text(36, 176, "10月23日 · 2小时 · 工作", 13, TEXT_SECONDARY)
# Smart parse result
doc.text(36, 196, "AI已识别：任务名 · 日期 · 时长 · 分类", 12, PRIMARY)

# Smart suggestions
doc.text(20, 244, "智能建议", 14, TEXT_PRIMARY, bold=True)

suggestions = [
    ("📅 添加到今日日程", "自动安排在10:45-12:00空档"),
    ("⏱️ 创建专注会话", "45分钟深度工作模式"),
    ("👥 分配给张伟", "他正在处理相关项目"),
    ("🔁 设为每周重复", "每周一重复此任务"),
]

for i, (title, desc) in enumerate(suggestions):
    y = 272 + i * 52
    doc.rect(20, y, 360, 44, BG_LIGHT, RADIUS_MD)
    doc.circle(44, y+22, 14, BG_WHITE)
    doc.text(48, y+10, title, 13, TEXT_PRIMARY, bold=True)
    doc.text(48, y+30, desc, 12, TEXT_MUTED)
    doc.text_r(364, y+12, "›", 16, TEXT_MUTED)

# Recent tasks
doc.divider(20, 500, 360)
doc.text(20, 512, "最近任务", 14, TEXT_PRIMARY, bold=True)
doc.text_r(360, 512, "全部 ›", 12, PRIMARY)

recent = [
    ("客户邮件处理", "1小时前", ACCENT_GREEN, "✓"),
    ("代码审查", "3小时前", ACCENT_GREEN, "✓"),
    ("团队晨会", "5小时前", PRIMARY, "▶"),
]

for i, (title, time, color, icon) in enumerate(recent):
    y = 540 + i * 36
    doc.circle(36, y+12, 12, color)
    doc.text_c(36, y+8, icon, 12, TEXT_WHITE)
    doc.text(56, y, title, 13, TEXT_SECONDARY)
    doc.text_r(370, y+2, time, 12, TEXT_MUTED)

# Bottom bar
doc.divider(20, 660, 360)
doc.rect(20, 680, 170, 48, BG_MUTED, RADIUS_MD)
doc.text_c(105, 696, "🏷️ 更多选项", 13, TEXT_SECONDARY)
doc.rect(210, 680, 170, 48, PRIMARY, RADIUS_MD)
doc.text_c(295, 696, "添加任务", 15, TEXT_WHITE, bold=True)

# Gates
gates = K.dry_run(doc, "case-08", 12, [], max_parts=9000)
K.save_gates("case-08", gates, "初始版本")
K.assert_gates(gates, "case-08")

stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")

result = K.render_case("case-08", doc, "FlowDay快速添加", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))
