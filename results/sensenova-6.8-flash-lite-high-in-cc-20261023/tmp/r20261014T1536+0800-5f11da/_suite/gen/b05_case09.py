"""B05 case-09: FlowDay Settings
Preferences, integrations, and account management
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b05_kit as K
from b05_kit import *

W, H = 400, 800
doc = Doc(W, H, BG_LIGHT)

doc.status_bar(0, BG_WHITE, TEXT_PRIMARY)
doc.nav_bar(40, "设置", True, "📝")

# Profile section
doc.bg_section(0, 96, W, 100, BG_WHITE)
doc.line_h(0, W, 196, BORDER_LIGHT)
doc.avatar(56, 140, 28, PRIMARY, "明")
doc.text(96, 120, "小明", 18, TEXT_PRIMARY, bold=True)
doc.text(96, 148, "xiaoming@example.com", 13, TEXT_SECONDARY)
doc.text_r(370, 136, "›", 18, TEXT_MUTED)

# Preferences section
doc.text(20, 212, "偏好设置", 13, TEXT_MUTED, bold=True)
doc.bg_section(0, 228, W, 160, BG_WHITE)
doc.line_h(0, W, 388, BORDER_LIGHT)

pref_items = [
    ("🎨 主题外观", "浅色模式"),
    ("🔔 通知提醒", "智能通知"),
    ("⏰ 专注模式", "自动开启"),
    ("🌐 语言", "简体中文"),
]

for i, (title, subtitle) in enumerate(pref_items):
    y = 236 + i * 38
    doc.circle(40, y+12, 14, BG_MUTED)
    doc.text(60, y, title, 14, TEXT_PRIMARY)
    doc.text_r(340, y+2, subtitle, 12, TEXT_MUTED)
    doc.text_r(370, y, "›", 14, TEXT_MUTED)
    if i < 3:
        doc.divider(60, y+30, 310)

# Integrations section
doc.text(20, 400, "集成应用", 13, TEXT_MUTED, bold=True)
doc.bg_section(0, 416, W, 140, BG_WHITE)
doc.line_h(0, W, 556, BORDER_LIGHT)

integrations = [
    ("📅 Google日历", True),
    ("📊 Notion", True),
    ("💬 微信", False),
    ("🎵 Spotify", False),
]

for i, (title, connected) in enumerate(integrations):
    y = 424 + i * 34
    doc.circle(40, y+12, 14, BG_MUTED)
    doc.text(60, y, title, 14, TEXT_PRIMARY)
    if connected:
        doc.toggle(330, y+4, 36, 20, True, PRIMARY)
    else:
        doc.toggle(330, y+4, 36, 20, False)

# Account section
doc.text(20, 568, "账户", 13, TEXT_MUTED, bold=True)
doc.bg_section(0, 584, W, 100, BG_WHITE)
doc.line_h(0, W, 684, BORDER_LIGHT)

account_items = [
    ("👤 个人信息", "编辑资料"),
    ("🔐 密码与安全", "修改密码"),
    ("📦 数据导出", "下载备份"),
]

for i, (title, subtitle) in enumerate(account_items):
    y = 592 + i * 32
    doc.circle(40, y+12, 14, BG_MUTED)
    doc.text(60, y, title, 14, TEXT_PRIMARY)
    doc.text_r(340, y+2, subtitle, 12, TEXT_MUTED)
    doc.text_r(370, y, "›", 14, TEXT_MUTED)

# Bottom nav
doc.bottom_tab_bar(720, active_idx=4)

# Gates
gates = K.dry_run(doc, "case-09", 12, [], max_parts=9000)
K.save_gates("case-09", gates, "初始版本")
K.assert_gates(gates, "case-09")

stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")

result = K.render_case("case-09", doc, "FlowDay设置", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))
