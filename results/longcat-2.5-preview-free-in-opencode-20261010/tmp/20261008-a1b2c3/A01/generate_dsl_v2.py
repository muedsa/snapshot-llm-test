#!/usr/bin/env python3
"""A01 - 六个月经营诊断驾驶舱 DSL 生成器 v2"""
import json
from pathlib import Path

# 数据
months = ["2026-04", "2026-05", "2026-06", "2026-07", "2026-08", "2026-09"]
orders = [420, 460, 445, 530, 570, 620]
gross = [126000, 142600, 137950, 169600, 188100, 210800]
refund = [6300, 7130, 11036, 8480, 15048, 8432]
cost = [82000, 93500, 99000, 112000, 132000, 138000]
sessions = [3500, 4100, 4200, 4700, 5200, 5600]

# 计算
net = [g - r for g, r in zip(gross, refund)]
profit = [n - c for n, c in zip(net, cost)]
refund_rate = [r / g * 100 for r, g in zip(refund, gross)]
conv_rate = [o / s * 100 for o, s in zip(orders, sessions)]

total_net = sum(net)
total_profit = sum(profit)
total_orders = sum(orders)
total_sessions = sum(sessions)
overall_conv = total_orders / total_sessions * 100

# 保存计算数据
computed = {
    "months": months,
    "net_revenue": net,
    "profit": profit,
    "refund_rate": [round(r, 2) for r in refund_rate],
    "conversion_rate": [round(r, 2) for r in conv_rate],
    "total_net_revenue": total_net,
    "total_profit": total_profit,
    "total_orders": total_orders,
    "total_sessions": total_sessions,
    "overall_conversion_rate": round(overall_conv, 2),
    "chart_axes": {
        "bar_max_value": max(net),
        "bar_max_height_px": 260,
        "sessions_max": max(sessions),
        "conv_max": max(conv_rate)
    },
    "conclusion_values": {
        "total_net": total_net,
        "total_profit": total_profit,
        "total_orders": total_orders,
        "overall_conv": round(overall_conv, 2),
        "best_month": months[net.index(max(net))],
        "worst_month": months[net.index(min(net))],
        "avg_refund_rate": round(sum(refund_rate) / len(refund_rate), 2)
    }
}

output_dir = Path("outputs/20261008-a1b2c3/A01")
output_dir.mkdir(parents=True, exist_ok=True)
with open(output_dir / "computed-data.json", "w", encoding="utf-8") as f:
    json.dump(computed, f, ensure_ascii=False, indent=2)

# 颜色定义
BG = "#0B1120"
CARD_BG = "#131C2E"
CARD_BORDER = "#1E2D45"
TEXT_PRIMARY = "#E8EEF7"
TEXT_SECONDARY = "#8896AB"
ACCENT_BLUE = "#4DA3FF"
ACCENT_CYAN = "#22D3EE"
ACCENT_GREEN = "#34D399"
ACCENT_AMBER = "#FBBF24"
ACCENT_RED = "#F87171"
NET_COLOR = "#4DA3FF"
PROFIT_COLOR = "#818CF8"
GRID_COLOR = "#1E2D45"

# 柱图计算
max_net = max(net)
bar_max_h = 240
bar_width = 22
bar_gap = 6

# 计算柱子高度
net_heights = [int(n / max_net * bar_max_h) for n in net]
profit_heights = [int(p / max_net * bar_max_h) for p in profit]

# 小图计算
sess_max = max(sessions)
sess_heights = [int(s / sess_max * 80) for s in sessions]
conv_max = max(conv_rate)
conv_heights = [int(c / conv_max * 80) for c in conv_rate]

# 格式化金额
def fmt_money(v):
    return f"{v:,.0f}"

def fmt_wan(v):
    return f"{v/10000:.1f}万"

# 构建DSL - 使用列表收集行
lines = []

# 根节点
lines.append(f'<Snapshot background="{BG}" type="png">')
lines.append(f'  <Container width="1600" height="1000" padding="(20,24)">')
lines.append(f'    <Column crossAxisAlignment="START">')
lines.append(f'')
lines.append(f'      <!-- 标题栏 -->')
lines.append(f'      <Container width="1552" height="40" color="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}" padding="(10,14)">')
lines.append(f'        <Row mainAxisAlignment="SPACE_BETWEEN" crossAxisAlignment="CENTER">')
lines.append(f'          <Text color="{TEXT_PRIMARY}" fontSize="18" fontStyle="BOLD">Northstar 经营诊断驾驶舱</Text>')
lines.append(f'          <Text color="{TEXT_SECONDARY}" fontSize="13">2026-04 至 2026-09 · 金额单位：元</Text>')
lines.append(f'        </Row>')
lines.append(f'      </Container>')
lines.append(f'')
lines.append(f'      <SizedBox height="10"/>')
lines.append(f'')
lines.append(f'      <!-- KPI 卡片行 -->')
lines.append(f'      <Row mainAxisAlignment="SPACE_BETWEEN">')

# KPI卡片
kpi_data = [
    ("总净收入", fmt_money(total_net), "元", ACCENT_BLUE),
    ("总经营利润", fmt_money(total_profit), "元", ACCENT_GREEN),
    ("总订单", fmt_money(total_orders), "笔", ACCENT_CYAN),
    ("期间总体转化率", f"{overall_conv:.2f}%", "总订单/总访问", ACCENT_AMBER),
]

for label, value, unit, color in kpi_data:
    lines.append(f'        <Container width="376" height="88" color="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}" padding="(12,14)">')
    lines.append(f'          <Column crossAxisAlignment="START" mainAxisAlignment="CENTER">')
    lines.append(f'            <Text color="{TEXT_SECONDARY}" fontSize="12">{label}</Text>')
    lines.append(f'            <SizedBox height="4"/>')
    lines.append(f'            <Text color="{color}" fontSize="24" fontStyle="BOLD">{value}</Text>')
    lines.append(f'            <Text color="{TEXT_SECONDARY}" fontSize="10">{unit}</Text>')
    lines.append(f'          </Column>')
    lines.append(f'        </Container>')

lines.append(f'      </Row>')
lines.append(f'')
lines.append(f'      <SizedBox height="10"/>')
lines.append(f'')
lines.append(f'      <!-- 主图表区 -->')
lines.append(f'      <Row mainAxisAlignment="SPACE_BETWEEN">')
lines.append(f'        <!-- 左侧：净收入与经营利润分组柱图 -->')
lines.append(f'        <Container width="760" height="380" color="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}" padding="(12,14)">')
lines.append(f'          <Column crossAxisAlignment="START">')
lines.append(f'            <Text color="{TEXT_PRIMARY}" fontSize="14" fontStyle="BOLD">月度净收入与经营利润</Text>')
lines.append(f'            <SizedBox height="6"/>')
lines.append(f'            <Row mainAxisAlignment="SPACE_BETWEEN" crossAxisAlignment="CENTER">')
lines.append(f'              <Row crossAxisAlignment="CENTER">')
lines.append(f'                <Container width="10" height="10" color="{NET_COLOR}" borderRadius="2"/>')
lines.append(f'                <SizedBox width="4"/>')
lines.append(f'                <Text color="{TEXT_SECONDARY}" fontSize="10">净收入</Text>')
lines.append(f'                <SizedBox width="8"/>')
lines.append(f'                <Container width="10" height="10" color="{PROFIT_COLOR}" borderRadius="2"/>')
lines.append(f'                <SizedBox width="4"/>')
lines.append(f'                <Text color="{TEXT_SECONDARY}" fontSize="10">经营利润</Text>')
lines.append(f'              </Row>')
lines.append(f'              <Text color="{TEXT_SECONDARY}" fontSize="9">单位：元</Text>')
lines.append(f'            </Row>')
lines.append(f'            <SizedBox height="8"/>')
lines.append(f'            <!-- 柱图区域（含Y轴刻度）-->')
lines.append(f'            <Row crossAxisAlignment="END">')
lines.append(f'              <!-- Y轴刻度 -->')
lines.append(f'              <Container width="45" height="240">')
lines.append(f'                <Column mainAxisAlignment="SPACE_BETWEEN" crossAxisAlignment="END">')
lines.append(f'                  <Text color="{TEXT_SECONDARY}" fontSize="8">20万</Text>')
lines.append(f'                  <Text color="{TEXT_SECONDARY}" fontSize="8">15万</Text>')
lines.append(f'                  <Text color="{TEXT_SECONDARY}" fontSize="8">10万</Text>')
lines.append(f'                  <Text color="{TEXT_SECONDARY}" fontSize="8">5万</Text>')
lines.append(f'                  <Text color="{TEXT_SECONDARY}" fontSize="8">0</Text>')
lines.append(f'                </Column>')
lines.append(f'              </Container>')
lines.append(f'              <SizedBox width="6"/>')
lines.append(f'              <!-- 柱图 -->')
lines.append(f'              <Container width="680" height="240">')
lines.append(f'                <Row crossAxisAlignment="END" mainAxisAlignment="SPACE_EVENLY">')

# 添加柱子
for i in range(6):
    lines.append(f'                  <Column crossAxisAlignment="CENTER" mainAxisAlignment="END">')
    lines.append(f'                    <Row crossAxisAlignment="END">')
    lines.append(f'                      <Container width="{bar_width}" height="{net_heights[i]}" color="{NET_COLOR}" borderRadius="2"/>')
    lines.append(f'                      <SizedBox width="{bar_gap}"/>')
    lines.append(f'                      <Container width="{bar_width}" height="{profit_heights[i]}" color="{PROFIT_COLOR}" borderRadius="2"/>')
    lines.append(f'                    </Row>')
    lines.append(f'                    <SizedBox height="4"/>')
    lines.append(f'                    <Text color="{TEXT_SECONDARY}" fontSize="9">{months[i][-2:]}</Text>')
    lines.append(f'                  </Column>')

lines.append(f'                </Row>')
lines.append(f'              </Container>')
lines.append(f'            </Row>')
lines.append(f'          </Column>')
lines.append(f'        </Container>')
lines.append(f'')
lines.append(f'        <!-- 右侧：两个共享月份对齐的小图 -->')
lines.append(f'        <Column mainAxisAlignment="SPACE_BETWEEN">')

# 访问量小图
lines.append(f'          <Container width="376" height="182" color="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}" padding="(10,12)">')
lines.append(f'            <Column crossAxisAlignment="START">')
lines.append(f'              <Text color="{TEXT_PRIMARY}" fontSize="12" fontStyle="BOLD">访问量（sessions）</Text>')
lines.append(f'              <SizedBox height="4"/>')
lines.append(f'              <Container width="352" height="110">')
lines.append(f'                <Row crossAxisAlignment="END" mainAxisAlignment="SPACE_EVENLY">')

for i in range(6):
    lines.append(f'                  <Column crossAxisAlignment="CENTER" mainAxisAlignment="END">')
    lines.append(f'                    <Container width="26" height="{sess_heights[i]}" color="{ACCENT_CYAN}" borderRadius="2"/>')
    lines.append(f'                    <SizedBox height="3"/>')
    lines.append(f'                    <Text color="{TEXT_SECONDARY}" fontSize="8">{months[i][-2:]}</Text>')
    lines.append(f'                  </Column>')

lines.append(f'                </Row>')
lines.append(f'              </Container>')
lines.append(f'            </Column>')
lines.append(f'          </Container>')

# 转化率小图
lines.append(f'          <Container width="376" height="182" color="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}" padding="(10,12)">')
lines.append(f'            <Column crossAxisAlignment="START">')
lines.append(f'              <Text color="{TEXT_PRIMARY}" fontSize="12" fontStyle="BOLD">月度转化率（%）</Text>')
lines.append(f'              <SizedBox height="4"/>')
lines.append(f'              <Container width="352" height="110">')
lines.append(f'                <Row crossAxisAlignment="END" mainAxisAlignment="SPACE_EVENLY">')

for i in range(6):
    lines.append(f'                  <Column crossAxisAlignment="CENTER" mainAxisAlignment="END">')
    lines.append(f'                    <Container width="26" height="{conv_heights[i]}" color="{ACCENT_AMBER}" borderRadius="2"/>')
    lines.append(f'                    <SizedBox height="3"/>')
    lines.append(f'                    <Text color="{TEXT_SECONDARY}" fontSize="8">{months[i][-2:]}</Text>')
    lines.append(f'                  </Column>')

lines.append(f'                </Row>')
lines.append(f'              </Container>')
lines.append(f'            </Column>')
lines.append(f'          </Container>')

lines.append(f'        </Column>')
lines.append(f'      </Row>')
lines.append(f'')
lines.append(f'      <SizedBox height="10"/>')
lines.append(f'')
lines.append(f'      <!-- 明细表 -->')
lines.append(f'      <Container width="1552" height="280" color="{CARD_BG}" borderRadius="8" border="1 SOLID {CARD_BORDER}" padding="(10,12)">')
lines.append(f'        <Column crossAxisAlignment="START">')
lines.append(f'          <Text color="{TEXT_PRIMARY}" fontSize="13" fontStyle="BOLD">月度明细</Text>')
lines.append(f'          <SizedBox height="6"/>')
lines.append(f'          <!-- 表头 -->')
lines.append(f'          <Container width="1528" height="28" color="{GRID_COLOR}" borderRadius="4" padding="(0,8)">')
lines.append(f'            <Row mainAxisAlignment="SPACE_BETWEEN" crossAxisAlignment="CENTER">')
lines.append(f'              <Text color="{TEXT_SECONDARY}" fontSize="10" fontStyle="BOLD">月份</Text>')
lines.append(f'              <Text color="{TEXT_SECONDARY}" fontSize="10" fontStyle="BOLD">净收入（元）</Text>')
lines.append(f'              <Text color="{TEXT_SECONDARY}" fontSize="10" fontStyle="BOLD">退款率</Text>')
lines.append(f'              <Text color="{TEXT_SECONDARY}" fontSize="10" fontStyle="BOLD">经营利润（元）</Text>')
lines.append(f'              <Text color="{TEXT_SECONDARY}" fontSize="10" fontStyle="BOLD">转化率</Text>')
lines.append(f'            </Row>')
lines.append(f'          </Container>')

# 添加数据行
for i in range(6):
    bg = "#162032" if i % 2 == 0 else CARD_BG
    lines.append(f'          <SizedBox height="2"/>')
    lines.append(f'          <Container width="1528" height="28" color="{bg}" borderRadius="4" padding="(0,8)">')
    lines.append(f'            <Row mainAxisAlignment="SPACE_BETWEEN" crossAxisAlignment="CENTER">')
    lines.append(f'              <Text color="{TEXT_PRIMARY}" fontSize="10">{months[i]}</Text>')
    lines.append(f'              <Text color="{NET_COLOR}" fontSize="10">{fmt_money(net[i])}</Text>')
    lines.append(f'              <Text color="{ACCENT_RED if refund_rate[i] > 6 else TEXT_SECONDARY}" fontSize="10">{refund_rate[i]:.2f}%</Text>')
    lines.append(f'              <Text color="{PROFIT_COLOR}" fontSize="10">{fmt_money(profit[i])}</Text>')
    lines.append(f'              <Text color="{ACCENT_AMBER}" fontSize="10">{conv_rate[i]:.2f}%</Text>')
    lines.append(f'            </Row>')
    lines.append(f'          </Container>')

lines.append(f'        </Column>')
lines.append(f'      </Container>')
lines.append(f'')
lines.append(f'      <SizedBox height="10"/>')
lines.append(f'')
lines.append(f'      <!-- 管理结论 -->')
lines.append(f'      <Container width="1552" height="56" color="#1A2740" borderRadius="8" border="1 SOLID #2A3F5F" padding="(10,14)">')
lines.append(f'        <Row crossAxisAlignment="CENTER">')
lines.append(f'          <Container width="3" height="36" color="{ACCENT_BLUE}" borderRadius="2"/>')
lines.append(f'          <SizedBox width="10"/>')
lines.append(f'          <Column crossAxisAlignment="START">')
lines.append(f'            <Text color="{TEXT_PRIMARY}" fontSize="12" fontStyle="BOLD">管理结论</Text>')
lines.append(f'            <SizedBox height="2"/>')
lines.append(f'            <Text color="{TEXT_SECONDARY}" fontSize="11">六个月总净收入 {fmt_wan(total_net)}，总经营利润 {fmt_wan(total_profit)}，利润率 {total_profit/total_net*100:.1f}%。9月净收入最高（{fmt_wan(net[5])}），6月退款率异常（{refund_rate[2]:.2f}%）需关注。总体转化率 {overall_conv:.2f}%，建议持续优化转化链路。</Text>')
lines.append(f'          </Column>')
lines.append(f'        </Row>')
lines.append(f'      </Container>')
lines.append(f'')
lines.append(f'    </Column>')
lines.append(f'  </Container>')
lines.append(f'</Snapshot>')

dsl = "\n".join(lines)

# 保存DSL
with open(output_dir / "operations.snapshot", "w", encoding="utf-8") as f:
    f.write(dsl)

print(f"DSL generated: {len(dsl)} chars, {len(lines)} lines")
print(f"Total net: {total_net}, Total profit: {total_profit}")
print(f"Overall conversion: {overall_conv:.2f}%")
