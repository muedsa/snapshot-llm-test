"""B06 case-03: 电费阶梯计算可视化
Problem: Tiered electricity pricing is hard to understand
Solution: Visual breakdown showing how usage affects your bill
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b06_kit as K
from b06_kit import *

W, H = 800, 600
doc = Doc(W, H, BG_WHITE)

# Header
doc.text(40, 30, "居民用电阶梯电价", 28, TEXT_PRIMARY, bold=True)
doc.text(40, 68, "看懂你的电费账单", 16, TEXT_SECONDARY)

# Tier cards
tiers = [
    (40, 100, 220, 140, "第一档", "0-200度", "0.52元/度", ACCENT_GREEN, "约40%用户"),
    (280, 100, 220, 140, "第二档", "201-400度", "0.57元/度", ACCENT_ORANGE, "约45%用户"),
    (520, 100, 220, 140, "第三档", "400度以上", "0.82元/度", ACCENT_RED, "约15%用户"),
]

for x, y, w, h, tier, range_str, price, color, user_pct in tiers:
    doc.rect(x, y, w, h, color + "10", 12)
    doc.rect(x, y, 6, h, color)
    doc.text(x+24, y+16, tier, 18, TEXT_PRIMARY, bold=True)
    doc.text(x+24, y+44, range_str, 24, color, bold=True)
    doc.text(x+24, y+80, price, 20, TEXT_PRIMARY, bold=True)
    doc.text(x+24, y+108, user_pct, 12, TEXT_SECONDARY)

# Example calculation
doc.rect(40, 270, 720, 280, BG_LIGHT, 12)
doc.text(60, 290, "计算示例：月用电350度", 18, TEXT_PRIMARY, bold=True)

# Tier 1: 200 kWh
doc.rect(60, 320, 240, 60, ACCENT_GREEN + "20", 8)
doc.text(80, 330, "第一档：200度 × 0.52元", 14, ACCENT_GREEN, bold=True)
doc.text(80, 352, "= 104.00 元", 16, TEXT_PRIMARY, bold=True)

# Tier 2: 150 kWh
doc.rect(60, 390, 240, 60, ACCENT_ORANGE + "20", 8)
doc.text(80, 400, "第二档：150度 × 0.57元", 14, ACCENT_ORANGE, bold=True)
doc.text(80, 422, "= 85.50 元", 16, TEXT_PRIMARY, bold=True)

# Total
doc.rect(60, 460, 240, 50, TEXT_PRIMARY + "10", 8)
doc.text(80, 472, "总电费", 14, TEXT_SECONDARY)
doc.text(80, 490, "= 189.50 元", 18, TEXT_PRIMARY, bold=True)

# Bar chart comparison
doc.text(340, 290, "对比：无阶梯定价", 16, TEXT_PRIMARY, bold=True)
bar_w = 380
max_val = 250
# Actual with tiers
doc.rect(360, 330, int(189.50/max_val*bar_w), 30, ACCENT_ORANGE, 4)
doc.text(360+int(189.50/max_val*bar_w)+10, 334, "189.50元", 14, ACCENT_ORANGE, bold=True)
# Without tiers
doc.rect(360, 375, int(182.00/max_val*bar_w), 30, ACCENT_BLUE, 4)
doc.text(360+int(182.00/max_val*bar_w)+10, 379, "182.00元", 14, ACCENT_BLUE, bold=True)
doc.text(340, 425, "阶梯定价多付 7.50 元", 13, TEXT_SECONDARY)

# Savings tip
doc.rect(340, 460, 380, 50, ACCENT_GREEN + "15", 8)
doc.text(360, 472, "💡 节约用电到200度以内，每度省0.05-0.30元", 13, ACCENT_GREEN, bold=True)
doc.text(360, 492, "每月可省 10-30 元", 12, TEXT_SECONDARY)

# Footer
doc.text(40, 575, "数据来源：国家电网居民阶梯电价（演示用途）", 12, TEXT_SECONDARY)

gates = K.dry_run(doc, "case-03", 12, [], max_parts=9000)
K.save_gates("case-03", gates, "初始版本")
K.assert_gates(gates, "case-03")

stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")

result = K.render("case-03", doc, "电费阶梯计算可视化", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))
