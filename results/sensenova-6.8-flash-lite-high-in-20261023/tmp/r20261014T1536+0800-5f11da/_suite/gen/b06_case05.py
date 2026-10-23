"""B06 case-05: 营养标签快速对比
Problem: Nutrition labels are hard to compare between products
Solution: Side-by-side visual comparison with health scoring
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b06_kit as K
from b06_kit import *

W, H = 800, 600
doc = Doc(W, H, BG_WHITE)

# Header
doc.text(40, 30, "营养标签对比", 28, TEXT_PRIMARY, bold=True)
doc.text(40, 68, "两杯酸奶的营养差异", 16, TEXT_SECONDARY)

# Product A
doc.rect(40, 100, 340, 460, BG_LIGHT, 12)
doc.rect(40, 100, 340, 50, ACCENT_GREEN, 12)
doc.rect(40, 138, 340, 12, ACCENT_GREEN)
doc.text_c(210, 112, "A: 原味酸奶", 18, TEXT_LIGHT, bold=True)

# Health score
doc.circle(80, 190, 30, ACCENT_GREEN)
doc.text_c(80, 182, "A", 20, TEXT_LIGHT, bold=True)
doc.text_c(80, 230, "健康评分", 12, TEXT_SECONDARY)
doc.text_c(80, 248, "92分", 16, ACCENT_GREEN, bold=True)

# Nutrition bars
metrics = [
    ("热量", 120, "kcal", 100, ACCENT_BLUE),
    ("蛋白质", 8, "g", 20, ACCENT_PURPLE),
    ("脂肪", 3, "g", 20, ACCENT_ORANGE),
    ("糖", 5, "g", 25, ACCENT_RED),
]
for i, (name, val, unit, max_val, color) in enumerate(metrics):
    y = 270 + i*45
    doc.text(70, y, name, 13, TEXT_PRIMARY)
    doc.rect(130, y+2, 200, 14, BORDER, 7)
    fill_w = int(val/max_val*200)
    doc.rect(130, y+2, fill_w, 14, color, 7)
    doc.text(340, y, f"{val}{unit}", 12, TEXT_SECONDARY)

# Highlights
doc.rect(70, 460, 280, 70, ACCENT_GREEN + "15", 8)
doc.text(80, 470, "✓ 高蛋白 低糖", 14, ACCENT_GREEN, bold=True)
doc.text(80, 492, "✓ 无添加糖分", 13, TEXT_SECONDARY)
doc.text(80, 510, "✓ 低脂配方", 13, TEXT_SECONDARY)

# Product B
doc.rect(420, 100, 340, 460, BG_LIGHT, 12)
doc.rect(420, 100, 340, 50, ACCENT_RED, 12)
doc.rect(420, 138, 340, 12, ACCENT_RED)
doc.text_c(590, 112, "B: 果味酸奶", 18, TEXT_LIGHT, bold=True)

# Health score
doc.circle(460, 190, 30, ACCENT_ORANGE)
doc.text_c(460, 182, "B", 20, TEXT_LIGHT, bold=True)
doc.text_c(460, 230, "健康评分", 12, TEXT_SECONDARY)
doc.text_c(460, 248, "65分", 16, ACCENT_ORANGE, bold=True)

# Nutrition bars
metrics_b = [
    ("热量", 180, "kcal", 100, ACCENT_BLUE),
    ("蛋白质", 6, "g", 20, ACCENT_PURPLE),
    ("脂肪", 5, "g", 20, ACCENT_ORANGE),
    ("糖", 18, "g", 25, ACCENT_RED),
]
for i, (name, val, unit, max_val, color) in enumerate(metrics_b):
    y = 270 + i*45
    doc.text(450, y, name, 13, TEXT_PRIMARY)
    doc.rect(510, y+2, 200, 14, BORDER, 7)
    fill_w = int(val/max_val*200)
    doc.rect(510, y+2, fill_w, 14, color, 7)
    doc.text(720, y, f"{val}{unit}", 12, TEXT_SECONDARY)

# Highlights
doc.rect(450, 460, 280, 70, ACCENT_RED + "15", 8)
doc.text(460, 470, "⚠ 高糖分", 14, ACCENT_RED, bold=True)
doc.text(460, 492, "⚠ 添加蔗糖", 13, TEXT_SECONDARY)
doc.text(460, 510, "⚠ 热量较高", 13, TEXT_SECONDARY)

# Footer
doc.text(40, 580, "数据来源：营养标签（演示用途）", 12, TEXT_SECONDARY)

gates = K.dry_run(doc, "case-05", 12, [], max_parts=9000)
K.save_gates("case-05", gates, "初始版本")
K.assert_gates(gates, "case-05")

stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")

result = K.render("case-05", doc, "营养标签快速对比", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))
