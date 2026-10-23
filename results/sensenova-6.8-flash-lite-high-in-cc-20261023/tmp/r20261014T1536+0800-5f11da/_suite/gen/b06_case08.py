"""B06 case-08: 医保报销流程可视化
Problem: Medical insurance reimbursement process is confusing
Solution: Clear step-by-step flow with document requirements
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b06_kit as K
from b06_kit import *

W, H = 800, 600
doc = Doc(W, H, BG_WHITE)

# Header
doc.text(40, 30, "医保报销流程", 28, TEXT_PRIMARY, bold=True)
doc.text(40, 68, "从就诊到报销的完整步骤", 16, TEXT_SECONDARY)

# Step flow
steps = [
    (40, 100, "1", "门诊/住院", "挂号就诊", "携带医保卡", ACCENT_BLUE),
    (200, 100, "2", "缴费", "自付部分", "保留发票", ACCENT_GREEN),
    (360, 100, "3", "收集材料", "发票/清单/病历", "拍照备份", ACCENT_ORANGE),
    (520, 100, "4", "提交申请", "线上/线下", "15个工作日起", ACCENT_PURPLE),
]

for x, y, num, title, detail, note, color in steps:
    doc.rect(x, y, 140, 140, BG_LIGHT, 12)
    doc.rect(x, y, 140, 50, color)
    doc.text_c(x+70, y+15, num, 24, TEXT_LIGHT, bold=True)
    doc.text_c(x+70, y+65, title, 16, TEXT_PRIMARY, bold=True)
    doc.text_c(x+70, y+90, detail, 12, TEXT_SECONDARY)
    doc.rect(x+20, y+110, 100, 20, color + "15", 4)
    doc.text_c(x+70, y+115, note, 12, color)
    # Arrow
    if x < 520:
        doc.text_c(x+150, y+65, "→", 20, TEXT_SECONDARY)

# Required documents
doc.rect(40, 270, 340, 220, BG_LIGHT, 12)
doc.text(60, 285, "所需材料清单", 18, TEXT_PRIMARY, bold=True)

docs = [
    ("医保卡", "原件", "必须"),
    ("收费发票", "原件", "必须"),
    ("费用清单", "原件", "必须"),
    ("诊断证明", "复印件", "住院需要"),
    ("费用明细", "复印件", "超过5000元"),
    ("银行卡", "复印件", "用于打款"),
]
for i, (name, type_str, note) in enumerate(docs):
    y = 320 + i*28
    doc.circle(70, y+8, 12, ACCENT_BLUE + "30")
    doc.text_c(70, y+4, "✓", 12, ACCENT_BLUE)
    doc.text(90, y, name, 14, TEXT_PRIMARY)
    doc.text(220, y, type_str, 12, TEXT_SECONDARY)
    doc.text(300, y, note, 12, ACCENT_RED)

# Reimbursement rates
doc.rect(400, 270, 340, 220, BG_LIGHT, 12)
doc.text(420, 285, "报销比例", 18, TEXT_PRIMARY, bold=True)

rates = [
    ("门诊", "60-80%", "年度限额15000元", ACCENT_BLUE),
    ("住院", "80-95%", "年度限额300000元", ACCENT_GREEN),
    ("大病", "70-90%", "年度限额500000元", ACCENT_PURPLE),
    ("特殊病种", "90%以上", "长期慢性病", ACCENT_ORANGE),
]
for i, (type_str, rate, limit, color) in enumerate(rates):
    y = 320 + i*40
    doc.rect(420, y, 100, 28, color + "15", 6)
    doc.text_c(470, y+6, type_str, 13, color, bold=True)
    doc.text(540, y+4, rate, 16, TEXT_PRIMARY, bold=True)
    doc.text(540, y+24, limit, 12, TEXT_SECONDARY)

# Timeline
doc.rect(40, 510, 720, 50, BG_LIGHT, 10)
doc.text(60, 522, "报销周期", 14, TEXT_SECONDARY)
doc.text(60, 542, "15-30个工作日", 18, TEXT_PRIMARY, bold=True)
doc.text(350, 522, "线上查询", 14, TEXT_SECONDARY)
doc.text(350, 542, "医保App实时跟踪", 16, ACCENT_BLUE, bold=True)
doc.text(600, 522, "咨询电话", 14, TEXT_SECONDARY)
doc.text(600, 542, "12393", 18, ACCENT_GREEN, bold=True)

# Footer
doc.text(40, 580, "数据来源：国家医保局政策（演示用途）", 12, TEXT_SECONDARY)

gates = K.dry_run(doc, "case-08", 12, [], max_parts=9000)
K.save_gates("case-08", gates, "初始版本")
K.assert_gates(gates, "case-08")

stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")

result = K.render("case-08", doc, "医保报销流程可视化", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))
