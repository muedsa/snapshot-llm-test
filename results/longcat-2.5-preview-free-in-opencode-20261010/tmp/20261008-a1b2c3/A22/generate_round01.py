#!/usr/bin/env python3
"""A22 - 真实数据更正与局部回归 第一轮 DSL 生成器"""
import json
from pathlib import Path

# 数据
months = ["2026-04", "2026-05", "2026-06", "2026-07", "2026-08", "2026-09"]
orders = [420, 460, 445, 530, 570, 620]
gross = [126000, 142600, 137950, 169600, 188100, 210800]
refund = [6300, 7130, 11036, 8480, 15048, 8432]
cost = [82000, 93500, 99000, 112000, 132000, 138000]
sessions = [3500, 4100, 4200, 4700, 5200, 5600]

net = [g - r for g, r in zip(gross, refund)]
profit = [n - c for n, c in zip(net, cost)]
refund_rate = [r / g * 100 for r, g in zip(refund, gross)]
conv_rate = [o / s * 100 for o, s in zip(orders, sessions)]

total_net = sum(net)
total_profit = sum(profit)
total_orders = sum(orders)
total_sessions = sum(sessions)
overall_conv = total_orders / total_sessions * 100

computed = {
    "months": months, "net_revenue": net, "profit": profit,
    "refund_rate": [round(r, 2) for r in refund_rate],
    "conversion_rate": [round(r, 2) for r in conv_rate],
    "total_net_revenue": total_net, "total_profit": total_profit,
    "total_orders": total_orders, "total_sessions": total_sessions,
    "overall_conversion_rate": round(overall_conv, 2)
}

output_dir = Path("outputs/20261008-a1b2c3/A22/round-01")
output_dir.mkdir(parents=True, exist_ok=True)
with open(output_dir / "computed-data.json", "w", encoding="utf-8") as f:
    json.dump(computed, f, ensure_ascii=False, indent=2)

BG = "#0F172A"
CARD_BG = "#1E293B"
CARD_BORDER = "#334155"
TEXT_PRIMARY = "#F1F5F9"
TEXT_SECONDARY = "#94A3B8"
COLOR_BLUE = "#3B82F6"
COLOR_GREEN = "#10B981"
COLOR_ORANGE = "#F59E0B"

lines = []
lines.append(f'<Snapshot background="{BG}" type="png">')
lines.append(f'  <Container width="1600" height="1000" padding="(24,28)">')
lines.append(f'    <Column crossAxisAlignment="START">')
lines.append(f'      <Text color="{TEXT_PRIMARY}" fontSize="24" fontStyle="BOLD">Northstar 经营驾驶舱</Text>')
lines.append(f'      <Text color="{TEXT_SECONDARY}" fontSize="14">2026-04 至 2026-09</Text>')
lines.append(f'      <SizedBox height="16"/>')
lines.append(f'      <Row mainAxisAlignment="SPACE_BETWEEN">')

kpis = [
    ("总净收入", f"{total_net:,}", COLOR_BLUE),
    ("总经营利润", f"{total_profit:,}", COLOR_GREEN),
    ("总订单", f"{total_orders:,}", COLOR_ORANGE),
    ("总体转化率", f"{overall_conv:.2f}%", COLOR_GREEN),
]
for label, value, color in kpis:
    lines.append(f'        <Container width="372" height="80" background="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}" padding="(12,14)">')
    lines.append(f'          <Column crossAxisAlignment="START">')
    lines.append(f'            <Text color="{TEXT_SECONDARY}" fontSize="14">{label}</Text>')
    lines.append(f'            <Text color="{color}" fontSize="28" fontStyle="BOLD">{value}</Text>')
    lines.append(f'          </Column>')
    lines.append(f'        </Container>')

lines.append(f'      </Row>')
lines.append(f'      <SizedBox height="16"/>')
lines.append(f'      <Container width="1544" height="300" background="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}" padding="(12,14)">')
lines.append(f'        <Column crossAxisAlignment="START">')
lines.append(f'          <Text color="{TEXT_PRIMARY}" fontSize="16" fontStyle="BOLD">净收入与经营利润</Text>')
lines.append(f'          <SizedBox height="8"/>')
lines.append(f'          <Row crossAxisAlignment="END" mainAxisAlignment="SPACE_EVENLY">')

max_val = max(max(net), max(profit))
bar_max_h = 200
for i in range(6):
    net_h = int(net[i] / max_val * bar_max_h)
    profit_h = int(profit[i] / max_val * bar_max_h)
    lines.append(f'            <Column crossAxisAlignment="CENTER" mainAxisAlignment="END">')
    lines.append(f'              <Row crossAxisAlignment="END">')
    lines.append(f'                <Container width="20" height="{net_h}" color="{COLOR_BLUE}" borderRadius="2"/>')
    lines.append(f'                <SizedBox width="4"/>')
    lines.append(f'                <Container width="20" height="{profit_h}" color="{COLOR_GREEN}" borderRadius="2"/>')
    lines.append(f'              </Row>')
    lines.append(f'              <Text color="{TEXT_SECONDARY}" fontSize="12">{months[i][-2:]}</Text>')
    lines.append(f'            </Column>')

lines.append(f'          </Row>')
lines.append(f'        </Column>')
lines.append(f'      </Container>')
lines.append(f'      <SizedBox height="16"/>')
lines.append(f'      <Container width="1544" height="280" background="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}" padding="(12,14)">')
lines.append(f'        <Column crossAxisAlignment="START">')
lines.append(f'          <Text color="{TEXT_PRIMARY}" fontSize="16" fontStyle="BOLD">月度明细</Text>')
lines.append(f'          <SizedBox height="8"/>')
lines.append(f'          <Row mainAxisAlignment="SPACE_BETWEEN">')
lines.append(f'            <Text color="{TEXT_SECONDARY}" fontSize="12">月份</Text>')
lines.append(f'            <Text color="{TEXT_SECONDARY}" fontSize="12">净收入</Text>')
lines.append(f'            <Text color="{TEXT_SECONDARY}" fontSize="12">利润</Text>')
lines.append(f'            <Text color="{TEXT_SECONDARY}" fontSize="12">退款率</Text>')
lines.append(f'            <Text color="{TEXT_SECONDARY}" fontSize="12">转化率</Text>')
lines.append(f'          </Row>')

for i in range(6):
    lines.append(f'          <Row mainAxisAlignment="SPACE_BETWEEN">')
    lines.append(f'            <Text color="{TEXT_PRIMARY}" fontSize="12">{months[i]}</Text>')
    lines.append(f'            <Text color="{COLOR_BLUE}" fontSize="12">{net[i]:,}</Text>')
    lines.append(f'            <Text color="{COLOR_GREEN}" fontSize="12">{profit[i]:,}</Text>')
    lines.append(f'            <Text color="{TEXT_SECONDARY}" fontSize="12">{refund_rate[i]:.2f}%</Text>')
    lines.append(f'            <Text color="{TEXT_SECONDARY}" fontSize="12">{conv_rate[i]:.2f}%</Text>')
    lines.append(f'          </Row>')

lines.append(f'        </Column>')
lines.append(f'      </Container>')
lines.append(f'      <SizedBox height="16"/>')
lines.append(f'      <Text color="{TEXT_SECONDARY}" fontSize="14">结论：六个月总净收入{total_net:,}元，总经营利润{total_profit:,}元，总体转化率{overall_conv:.2f}%。</Text>')
lines.append(f'    </Column>')
lines.append(f'  </Container>')
lines.append(f'</Snapshot>')

dsl = "\n".join(lines)
with open(output_dir / "dashboard.snapshot", "w", encoding="utf-8") as f:
    f.write(dsl)

layout_map = {
    "kpi": {"x": 28, "y": 70, "w": 1544, "h": 80},
    "chart": {"x": 28, "y": 170, "w": 1544, "h": 300},
    "table": {"x": 28, "y": 490, "w": 1544, "h": 280},
    "conclusion": {"x": 28, "y": 790, "w": 1544, "h": 40}
}
with open(output_dir / "layout-map.json", "w", encoding="utf-8") as f:
    json.dump(layout_map, f, ensure_ascii=False, indent=2)

print(f"DSL generated: {len(dsl)} chars")
