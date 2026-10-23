"""B06 case-02: 垃圾分类速查表
Problem: People don't know which bin to use
Solution: Visual guide with clear icons and color coding
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b06_kit as K
from b06_kit import *

W, H = 800, 600
doc = Doc(W, H, BG_WHITE)

# Header
doc.text(40, 30, "垃圾分类速查表", 28, TEXT_PRIMARY, bold=True)
doc.text(40, 68, "快速判断，正确投放", 16, TEXT_SECONDARY)

# Four category cards
categories = [
    (40, 100, "可回收物", ACCENT_BLUE, ["纸类", "塑料", "金属", "玻璃", "织物"]),
    (215, 100, "有害垃圾", ACCENT_RED, ["电池", "灯管", "药品", "油漆", "杀虫剂"]),
    (390, 100, "厨余垃圾", ACCENT_GREEN, ["剩饭", "菜叶", "果皮", "蛋壳", "茶叶"]),
    (565, 100, "其他垃圾", TEXT_SECONDARY, ["烟蒂", "尘土", "陶瓷", "卫生纸", "一次性餐具"]),
]

for x, y, name, color, items in categories:
    # Card
    doc.rect(x, y, 175, 440, BG_LIGHT, 12)
    # Color header
    doc.rect(x, y, 175, 60, color, 12)
    doc.rect(x, y+50, 175, 10, color)
    # Icon circle
    doc.circle(x+88, y+150, 40, color + "30")
    doc.text_c(x+88, y+138, {"可回收物":"♻️", "有害垃圾":"⚠️", "厨余垃圾":"🍃", "其他垃圾":"🗑️"}[name], 28, color)
    # Name
    doc.text_c(x+88, y+200, name, 20, TEXT_PRIMARY, bold=True)
    doc.text_c(x+88, y+228, "投入此类", 12, TEXT_SECONDARY)
    # Items
    doc.text_c(x+88, y+270, "常见物品", 14, TEXT_PRIMARY, bold=True)
    for i, item in enumerate(items):
        doc.rect(x+40, y+295+i*32, 95, 26, color + "15", 4)
        doc.text_c(x+88, y+300+i*32, item, 13, TEXT_PRIMARY)

# Bottom tip
doc.rect(40, 560, 720, 30, BG_LIGHT, 8)
doc.text_c(400, 565, "💡 不确定时，请投放至其他垃圾并咨询物业", 14, TEXT_SECONDARY)

gates = K.dry_run(doc, "case-02", 12, [], max_parts=9000)
K.save_gates("case-02", gates, "初始版本")
K.assert_gates(gates, "case-02")

stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")

result = K.render("case-02", doc, "垃圾分类速查表", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))
