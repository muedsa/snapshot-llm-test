"""B06 case-10: 地震预警信息
Problem: Earthquake warning messages are vague and scary
Solution: Clear, actionable earthquake information with safety steps
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b06_kit as K
from b06_kit import *

W, H = 800, 600
doc = Doc(W, H, BG_WHITE)

# Alert banner
doc.rect(0, 0, 800, 80, ACCENT_RED, 0)
doc.text(40, 12, "⚠️ 地震预警", 24, TEXT_LIGHT, bold=True)
doc.text(280, 15, "2026-10-23 14:32:15", 16, "#FFD6D6")
doc.text(280, 42, "震中：成都简阳 | 震级：5.2", 14, "#FFD6D6")
doc.text(560, 20, "预警延迟：3秒", 14, TEXT_LIGHT)
doc.text(560, 42, "您的位置：成都市区", 14, "#FFD6D6")

# Shake intensity
doc.rect(40, 100, 340, 140, ACCENT_ORANGE + "15", 12)
doc.text(60, 112, "预计烈度", 14, TEXT_SECONDARY)
doc.text(60, 135, "III级 - 轻微", 24, ACCENT_ORANGE, bold=True)
doc.rect(60, 165, 280, 30, ACCENT_ORANGE + "20", 8)
# Intensity scale
levels = ["I", "II", "III", "IV", "V", "VI"]
colors = [ACCENT_GREEN, ACCENT_YELLOW, ACCENT_ORANGE, ACCENT_RED, "#FF4444", "#880000"]
for i, (level, color) in enumerate(zip(levels, colors)):
    doc.rect(65+i*45, 170, 40, 20, color, 4)
    doc.text_c(85+i*45, 174, level, 12, TEXT_LIGHT if color != ACCENT_YELLOW else TEXT_PRIMARY)
doc.text(60, 205, "大部分人无感觉，少数人略有感觉", 12, TEXT_SECONDARY)

# Action steps
doc.rect(400, 100, 360, 140, ACCENT_BLUE + "10", 12)
doc.text(420, 112, "立即行动", 16, TEXT_PRIMARY, bold=True)
actions = [
    ("1. 就近躲避", "远离窗户和重物"),
    ("2. 保护头部", "用手或物品护住头部"),
    ("3. 不要慌张", "等待震动停止"),
]
for i, (action, detail) in enumerate(actions):
    y = 140 + i*36
    doc.circle(435, y+10, 12, ACCENT_BLUE)
    doc.text_c(435, y+6, str(i+1), 12, TEXT_LIGHT, bold=True)
    doc.text(455, y, action, 14, TEXT_PRIMARY, bold=True)
    doc.text(455, y+18, detail, 12, TEXT_SECONDARY)

# Location map (simplified)
doc.rect(40, 260, 340, 220, BG_LIGHT, 12)
doc.text(60, 272, "震中位置", 16, TEXT_PRIMARY, bold=True)
# Map background
doc.rect(60, 295, 280, 160, "#E8F4F8", 8)
# City markers
doc.circle(150, 380, 15, ACCENT_RED)
doc.text_c(150, 374, "震中", 12, TEXT_LIGHT, bold=True)
doc.text_c(150, 395, "简阳", 12, TEXT_PRIMARY, bold=True)
# Distance circles
doc.circle(150, 380, 50, ACCENT_ORANGE + "30")
doc.circle(150, 380, 90, ACCENT_YELLOW + "20")
doc.text_c(200, 330, "50km", 12, ACCENT_ORANGE)
doc.text_c(240, 310, "100km", 12, ACCENT_YELLOW)
# Your location
doc.circle(220, 370, 12, ACCENT_BLUE)
doc.text_c(220, 358, "您", 12, TEXT_LIGHT, bold=True)
doc.text(60, 465, "距震中：45公里", 13, TEXT_SECONDARY)

# Safety resources
doc.rect(400, 260, 360, 220, BG_LIGHT, 12)
doc.text(420, 272, "紧急资源", 16, TEXT_PRIMARY, bold=True)

resources = [
    ("110", "报警求助", ACCENT_RED),
    ("119", "消防救援", ACCENT_ORANGE),
    ("120", "医疗急救", ACCENT_GREEN),
    ("12350", "安全生产", ACCENT_PURPLE),
]
for i, (phone, desc, color) in enumerate(resources):
    y = 300 + i*40
    doc.rect(420, y, 80, 28, color, 8)
    doc.text_c(460, y+5, phone, 14, TEXT_LIGHT, bold=True)
    doc.text(510, y+7, desc, 14, TEXT_PRIMARY)

# Post-quake actions
doc.rect(420, 470, 320, 12, BORDER, 4)
doc.text(420, 470, "震动停止后", 12, TEXT_SECONDARY)
doc.text(420, 485, "• 检查周围安全", 12, TEXT_PRIMARY)
doc.text(420, 500, "• 帮助他人撤离", 12, TEXT_PRIMARY)
doc.text(420, 515, "• 查看官方通报", 12, TEXT_PRIMARY)

# Footer
doc.text(40, 585, "数据来源：国家地震局预警系统（演示用途）", 12, TEXT_SECONDARY)

gates = K.dry_run(doc, "case-10", 12, [], max_parts=9000)
K.save_gates("case-10", gates, "初始版本")
K.assert_gates(gates, "case-10")

stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")

result = K.render("case-10", doc, "地震预警信息", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))
