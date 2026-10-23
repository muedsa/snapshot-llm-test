"""B05 case-03: FlowDay Focus Mode
Minimal distraction-free view with pomodoro timer
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b05_kit as K
from b05_kit import *

W, H = 400, 800
doc = Doc(W, H, BG_DARK)

# Status bar (dark mode)
doc.status_bar(0, BG_DARK, "#6B7280")

# Top controls
doc.text(24, 52, "← 退出专注", 14, "#6B7280")
doc.text_c(200, 52, "专注模式", 14, "#9CA3AF")

# Focus timer (large circular)
cx, cy = 200, 280
# Outer glow
doc.circle(cx, cy, 140, PRIMARY, 0.1)
doc.circle(cx, cy, 120, PRIMARY, 0.15)
# Timer ring background
doc.circle(cx, cy, 100, "#2D3748", 1.0)
doc.circle(cx, cy, 88, BG_DARK, 1.0)
# Timer display
doc.text_c(cx, cy-30, "24:17", 52, TEXT_WHITE, bold=True)
doc.text_c(cx, cy+35, "剩余时间", 14, "#9CA3AF")

# Task being focused on
doc.rect(40, 440, 320, 80, "#1A1D23", RADIUS_LG)
doc.rect(40, 440, 4, 80, PRIMARY, 2)
doc.text(60, 456, "🎯 当前任务", 12, "#6B7280")
doc.text(60, 476, "完成项目报告第三章", 18, TEXT_WHITE, bold=True)
doc.text(60, 500, "预计 45分钟 · 已完成 52%", 12, "#9CA3AF")

# Timer controls
doc.circle(140, 580, 28, "#2D3748")
doc.text_c(140, 570, "⏸", 20, "#9CA3AF")
doc.circle(200, 580, 36, PRIMARY)
doc.text_c(200, 568, "▶", 24, TEXT_WHITE)
doc.circle(260, 580, 28, "#2D3748")
doc.text_c(260, 570, "↻", 20, "#9CA3AF")

# Session stats
doc.divider(40, 660, 320)
doc.text_c(200, 672, "今日专注统计", 13, "#6B7280")
doc.text_c(100, 708, "3", 32, PRIMARY_LIGHT, bold=True)
doc.text_c(100, 748, "已完成", 12, "#9CA3AF")
doc.text_c(200, 708, "24m", 32, ACCENT_GREEN, bold=True)
doc.text_c(200, 748, "专注中", 12, "#9CA3AF")
doc.text_c(300, 708, "1h 52m", 28, ACCENT_ORANGE, bold=True)
doc.text_c(300, 748, "今日总计", 12, "#9CA3AF")

# Gates
gates = K.dry_run(doc, "case-03", 12, [], max_parts=9000)
K.save_gates("case-03", gates, "初始版本")
K.assert_gates(gates, "case-03")

stats = doc.stats()
print(f"Parts: {stats['parts']}, Texts: {stats['texts']}, Shapes: {stats['shapes']}")

result = K.render_case("case-03", doc, "FlowDay专注模式", "final", "")
print(json.dumps(result, ensure_ascii=False, indent=2))
