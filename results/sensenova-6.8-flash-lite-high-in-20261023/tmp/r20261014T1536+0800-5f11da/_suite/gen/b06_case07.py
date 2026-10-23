"""B06 case-07: 快递包装规范
Problem: People don't know how to properly package items
Solution: Visual guide showing packaging for different item types
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b06_kit as K
from b06_kit import *

W, H = 800, 600
doc = Doc(W, H, BG_WHITE)

# Header
doc.text(40, 30, "快递包装指南", 28, TEXT_PRIMARY, bold=True)
doc.text(40, 68, "不同物品的包装方式", 16, TEXT_SECONDARY)

# Item types
items = [
    (40, 100, "衣物", "轻便易压", "气泡膜+纸箱", 1, ACCENT_BLUE),
    (215, 100, "电子产品", "易碎精密", "泡沫+纸箱", 3, ACCENT_PURPLE),
    (390, 100, "易碎品", "玻璃陶瓷", "气泡膜+木架", 5, ACCENT_RED),
    (565, 100, "液体", "易泄漏", "密封袋+纸箱", 4, ACCENT_ORANGE),
]

for x, y, name, risk, method, risk_level, color in items:
    doc.rect(x, y, 175, 380, BG_LIGHT, 12)
    # Risk indicator
    risk_color = ACCENT_GREEN if risk_level <= 2 else ACCENT_ORANGE if risk_level == 3 else ACCENT_RED
    doc.circle(x+88, y+40, 24, risk_color + "30")
    doc.text_c(x+88, y+32, "⚠️" * risk_level, 16, risk_color)
    doc.text_c(x+88, y+70, name, 18, TEXT_PRIMARY, bold=True)
    doc.text_c(x+88, y+95, risk, 13, TEXT_SECONDARY)
    # Risk level bar
    doc.rect(x+38, y+115, 100, 8, BORDER, 4)
    doc.rect(x+38, y+115, int(100*risk_level/5), 8, risk_color, 4)
    doc.text_c(x+88, y+130, f"风险等级 {risk_level}/5", 12, TEXT_SECONDARY)
    # Packaging method
    doc.text_c(x+88, y+165, "推荐包装", 14, TEXT_PRIMARY, bold=True)
    doc.rect(x+28, y+185, 120, 40, color + "20", 8)
    doc.text_c(x+88, y+195, method, 13, color, bold=True)
    # Step numbers
    doc.rect(x+28, y+240, 120, 120, BG_WHITE, 8)
    doc.text_c(x+88, y+250, "包装步骤", 12, TEXT_SECONDARY)
    steps = ["1. 包裹物品", "2. 填充缓冲", "3. 密封纸箱", "4. 贴标签"]
    for i, step in enumerate(steps[:risk_level+1]):
        doc.circle(x+48, y+280+i*25, 12, color + "30")
        doc.text_c(x+48, y+276+i*25, str(i+1), 12, color, bold=True)
        doc.text(x+65, y+276+i*25, step, 12, TEXT_PRIMARY)

# Safety tips
doc.rect(40, 500, 720, 70, BG_LIGHT, 12)
doc.text(60, 512, "安全提示", 16, TEXT_PRIMARY, bold=True)
tips = ["易碎品务必标注", "液体需密封三层", "贵重品建议保价", "遵守航空禁运规定"]
for i, tip in enumerate(tips):
    doc.text(60+i*180, 538, f"✓ {tip}", 12, TEXT_SECONDARY)

# Footer
doc.text(40, 585, "数据来源：快递包装规范（演示用途）", 12, TEXT_SECONDARY)

gates = K.dry_run(doc, "case-07", 12, [], max_parts=9000)
K.save_gates("case-07", gates, "初始版本")
K.assert_gates(gates, "case-07")

stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")

result = K.render("case-07", doc, "快递包装规范", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))
