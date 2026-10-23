"""B06 case-04: 地铁换乘指南
Problem: Subway transfer instructions are confusing
Solution: Visual step-by-step transfer guide with station indicators
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b06_kit as K
from b06_kit import *

W, H = 800, 600
doc = Doc(W, H, BG_WHITE)

# Header
doc.text(40, 30, "地铁换乘指南", 28, TEXT_PRIMARY, bold=True)
doc.text(40, 68, "从A站到B站的最优路线", 16, TEXT_SECONDARY)

# Route indicator
doc.rect(40, 100, 720, 50, BG_LIGHT, 10)
doc.text(60, 112, "起点", 14, TEXT_SECONDARY)
doc.text(60, 130, "人民广场站", 18, TEXT_PRIMARY, bold=True)
doc.text(350, 112, "途经", 14, TEXT_SECONDARY)
doc.text(350, 130, "1号线 → 2号线", 16, ACCENT_BLUE, bold=True)
doc.text(550, 112, "终点", 14, TEXT_SECONDARY)
doc.text(550, 130, "世纪大道站", 18, TEXT_PRIMARY, bold=True)

# Step 1: Line 1
doc.rect(40, 170, 340, 180, ACCENT_BLUE + "10", 12)
doc.rect(40, 170, 6, 180, ACCENT_BLUE)
doc.text(64, 185, "第1步", 14, ACCENT_BLUE, bold=True)
doc.text(64, 208, "乘坐1号线", 20, TEXT_PRIMARY, bold=True)
doc.text(64, 238, "人民广场 → 南京东路", 14, TEXT_SECONDARY)
doc.text(64, 260, "方向：往富锦路", 13, TEXT_SECONDARY)
doc.text(64, 282, "用时：约5分钟", 13, TEXT_SECONDARY)
doc.rect(64, 305, 280, 30, ACCENT_BLUE, 6)
doc.text_c(204, 311, "约2站", 14, TEXT_LIGHT, bold=True)

# Step 2: Transfer
doc.rect(400, 170, 340, 180, ACCENT_PURPLE + "10", 12)
doc.rect(400, 170, 6, 180, ACCENT_PURPLE)
doc.text(424, 185, "第2步", 14, ACCENT_PURPLE, bold=True)
doc.text(424, 208, "换乘2号线", 20, TEXT_PRIMARY, bold=True)
doc.text(424, 238, "南京东路 → 人民广场", 14, TEXT_SECONDARY)
doc.text(424, 260, "方向：往浦东国际机场", 13, TEXT_SECONDARY)
doc.text(424, 282, "用时：约3分钟", 13, TEXT_SECONDARY)
doc.rect(424, 305, 280, 30, ACCENT_PURPLE, 6)
doc.text_c(564, 311, "站内换乘", 14, TEXT_LIGHT, bold=True)

# Step 3: Line 2
doc.rect(40, 370, 700, 100, ACCENT_GREEN + "10", 12)
doc.rect(40, 370, 6, 100, ACCENT_GREEN)
doc.text(64, 385, "第3步", 14, ACCENT_GREEN, bold=True)
doc.text(64, 408, "乘坐2号线", 20, TEXT_PRIMARY, bold=True)
doc.text(300, 385, "人民广场 → 世纪大道", 14, TEXT_SECONDARY)
doc.text(300, 408, "方向：往浦东国际机场", 13, TEXT_SECONDARY)
doc.text(500, 385, "用时：约8分钟", 13, TEXT_SECONDARY)
doc.rect(64, 440, 640, 20, ACCENT_GREEN, 4)

# Summary
doc.rect(40, 490, 720, 80, BG_LIGHT, 12)
doc.text(60, 505, "总用时", 14, TEXT_SECONDARY)
doc.text(60, 528, "约16分钟", 24, TEXT_PRIMARY, bold=True)
doc.text(260, 505, "换乘次数", 14, TEXT_SECONDARY)
doc.text(260, 528, "1次", 24, ACCENT_PURPLE, bold=True)
doc.text(440, 505, "总费用", 14, TEXT_SECONDARY)
doc.text(440, 528, "4元", 24, ACCENT_GREEN, bold=True)
doc.text(620, 505, "总距离", 14, TEXT_SECONDARY)
doc.text(620, 528, "7.5km", 24, TEXT_PRIMARY, bold=True)

# Footer
doc.text(40, 585, "数据来源：上海地铁线路图（演示用途）", 12, TEXT_SECONDARY)

gates = K.dry_run(doc, "case-04", 12, [], max_parts=9000)
K.save_gates("case-04", gates, "初始版本")
K.assert_gates(gates, "case-04")

stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")

result = K.render("case-04", doc, "地铁换乘指南", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))
