"""B06 case-06: 出租车费用计算器
Problem: Taxi fare rules are complex and hard to calculate
Solution: Visual breakdown of fare components
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b06_kit as K
from b06_kit import *

W, H = 800, 600
doc = Doc(W, H, BG_WHITE)

# Header
doc.text(40, 30, "出租车费用计算", 28, TEXT_PRIMARY, bold=True)
doc.text(40, 68, "起步价 + 里程费 + 等候费", 16, TEXT_SECONDARY)

# Trip info
doc.rect(40, 100, 720, 60, BG_LIGHT, 10)
doc.text(60, 112, "行程", 14, TEXT_SECONDARY)
doc.text(60, 132, "人民广场 → 浦东机场", 18, TEXT_PRIMARY, bold=True)
doc.text(400, 112, "距离", 14, TEXT_SECONDARY)
doc.text(400, 132, "32.5公里", 18, TEXT_PRIMARY, bold=True)
doc.text(560, 112, "用时", 14, TEXT_SECONDARY)
doc.text(560, 132, "45分钟", 18, TEXT_PRIMARY, bold=True)

# Fare breakdown
doc.rect(40, 180, 340, 300, BG_LIGHT, 12)
doc.text(60, 195, "费用明细", 18, TEXT_PRIMARY, bold=True)

components = [
    ("起步价", "3公里内", "14.00元", ACCENT_BLUE, 60),
    ("里程费", "29.5公里 × 2.4元", "70.80元", ACCENT_GREEN, 180),
    ("等候费", "5分钟 × 2元", "10.00元", ACCENT_ORANGE, 40),
    ("燃油附加", "每公里", "3.50元", ACCENT_PURPLE, 20),
]
for i, (name, detail, price, color, bar_h) in enumerate(components):
    y = 230 + i*60
    doc.rect(60, y, 20, 40, color)
    doc.text(90, y+2, name, 14, TEXT_PRIMARY, bold=True)
    doc.text(90, y+20, detail, 12, TEXT_SECONDARY)
    doc.text(260, y+8, price, 18, color, bold=True)
    # Proportional bar
    doc.rect(60, y+50, int(300*bar_h/200), 6, color + "30", 3)

# Total
doc.rect(40, 500, 340, 50, TEXT_PRIMARY + "08", 10)
doc.line_h(40, 380, 500, BORDER, 2)
doc.text(60, 510, "合计", 16, TEXT_PRIMARY, bold=True)
doc.text(260, 505, "98.30元", 24, TEXT_PRIMARY, bold=True)

# Comparison
doc.rect(400, 180, 340, 370, BG_LIGHT, 12)
doc.text(420, 195, "对比参考", 18, TEXT_PRIMARY, bold=True)

comparisons = [
    ("出租车", "98.30元", "45分钟", ACCENT_BLUE),
    ("网约车", "85.00元", "45分钟", ACCENT_GREEN),
    ("地铁", "10.00元", "90分钟", ACCENT_PURPLE),
    ("公交", "5.00元", "120分钟", ACCENT_ORANGE),
]
for i, (mode, price, time, color) in enumerate(comparisons):
    y = 230 + i*70
    doc.rect(420, y, 300, 50, color + "10", 8)
    doc.rect(420, y, 6, 50, color)
    doc.text(445, y+8, mode, 16, TEXT_PRIMARY, bold=True)
    doc.text(445, y+30, time, 12, TEXT_SECONDARY)
    doc.text(600, y+12, price, 20, color, bold=True)

# Best value indicator
doc.rect(420, 490, 300, 50, ACCENT_GREEN + "15", 8)
doc.text(440, 500, "💡 最佳性价比", 14, ACCENT_GREEN, bold=True)
doc.text(440, 520, "地铁：10元/90分钟", 13, TEXT_SECONDARY)

# Footer
doc.text(40, 585, "数据来源：上海出租车计价规则（演示用途）", 12, TEXT_SECONDARY)

gates = K.dry_run(doc, "case-06", 12, [], max_parts=9000)
K.save_gates("case-06", gates, "初始版本")
K.assert_gates(gates, "case-06")

stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")

result = K.render("case-06", doc, "出租车费用计算器", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))
