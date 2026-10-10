#!/usr/bin/env python3
"""A01 - 六个月经营诊断驾驶舱 DSL 生成器"""
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
        "bar_max_height_px": 280,
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

# 生成DSL
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
bar_max_h = 260
bar_width = 22
bar_gap = 6
group_gap = 18

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

# 构建DSL
dsl_parts = []
dsl_parts.append(f'''<Snapshot background="{BG}" type="png">
  <Container width="1600" height="1000" padding="(24,28)">
    <Column crossAxisAlignment="START">

      <!-- 标题栏 -->
      <Container width="1544" height="44" color="{CARD_BG}" borderRadius="10" border="1 SOLID {CARD_BORDER}" padding="(12,16)">
        <Row mainAxisAlignment="SPACE_BETWEEN" crossAxisAlignment="CENTER">
          <Text color="{TEXT_PRIMARY}" fontSize="20" fontStyle="BOLD">Northstar 经营诊断驾驶舱</Text>
          <Text color="{TEXT_SECONDARY}" fontSize="14">2026-04 至 2026-09 · 金额单位：元</Text>
        </Row>
      </Container>

      <SizedBox height="12"/>

      <!-- KPI 卡片行 -->
      <Row mainAxisAlignment="SPACE_BETWEEN">
        <Container width="372" height="96" color="{CARD_BG}" borderRadius="10" border="1 SOLID {CARD_BORDER}" padding="(14,16)">
          <Column crossAxisAlignment="START" mainAxisAlignment="CENTER">
            <Text color="{TEXT_SECONDARY}" fontSize="13">总净收入</Text>
            <SizedBox height="4"/>
            <Text color="{ACCENT_BLUE}" fontSize="26" fontStyle="BOLD">{fmt_money(total_net)}</Text>
            <Text color="{TEXT_SECONDARY}" fontSize="11">元</Text>
          </Column>
        </Container>
        <Container width="372" height="96" color="{CARD_BG}" borderRadius="10" border="1 SOLID {CARD_BORDER}" padding="(14,16)">
          <Column crossAxisAlignment="START" mainAxisAlignment="CENTER">
            <Text color="{TEXT_SECONDARY}" fontSize="13">总经营利润</Text>
            <SizedBox height="4"/>
            <Text color="{ACCENT_GREEN}" fontSize="26" fontStyle="BOLD">{fmt_money(total_profit)}</Text>
            <Text color="{TEXT_SECONDARY}" fontSize="11">元</Text>
          </Column>
        </Container>
        <Container width="372" height="96" color="{CARD_BG}" borderRadius="10" border="1 SOLID {CARD_BORDER}" padding="(14,16)">
          <Column crossAxisAlignment="START" mainAxisAlignment="CENTER">
            <Text color="{TEXT_SECONDARY}" fontSize="13">总订单</Text>
            <SizedBox height="4"/>
            <Text color="{ACCENT_CYAN}" fontSize="26" fontStyle="BOLD">{fmt_money(total_orders)}</Text>
            <Text color="{TEXT_SECONDARY}" fontSize="11">笔</Text>
          </Column>
        </Container>
        <Container width="372" height="96" color="{CARD_BG}" borderRadius="10" border="1 SOLID {CARD_BORDER}" padding="(14,16)">
          <Column crossAxisAlignment="START" mainAxisAlignment="CENTER">
            <Text color="{TEXT_SECONDARY}" fontSize="13">期间总体转化率</Text>
            <SizedBox height="4"/>
            <Text color="{ACCENT_AMBER}" fontSize="26" fontStyle="BOLD">{overall_conv:.2f}%</Text>
            <Text color="{TEXT_SECONDARY}" fontSize="11">总订单/总访问</Text>
          </Column>
        </Container>
      </Row>

      <SizedBox height="12"/>

      <!-- 主图表区 -->
      <Row mainAxisAlignment="SPACE_BETWEEN">
        <!-- 左侧：净收入与经营利润分组柱图 -->
        <Container width="760" height="400" color="{CARD_BG}" borderRadius="10" border="1 SOLID {CARD_BORDER}" padding="(14,16)">
          <Column crossAxisAlignment="START">
            <Text color="{TEXT_PRIMARY}" fontSize="15" fontStyle="BOLD">月度净收入与经营利润</Text>
            <SizedBox height="8"/>
            <Row mainAxisAlignment="SPACE_BETWEEN" crossAxisAlignment="CENTER">
              <Row crossAxisAlignment="CENTER">
                <Container width="12" height="12" color="{NET_COLOR}" borderRadius="2"/>
                <SizedBox width="4"/>
                <Text color="{TEXT_SECONDARY}" fontSize="11">净收入</Text>
                <SizedBox width="10"/>
                <Container width="12" height="12" color="{PROFIT_COLOR}" borderRadius="2"/>
                <SizedBox width="4"/>
                <Text color="{TEXT_SECONDARY}" fontSize="11">经营利润</Text>
              </Row>
              <Text color="{TEXT_SECONDARY}" fontSize="10">单位：元</Text>
            </Row>
            <SizedBox height="10"/>
            <!-- 柱图区域（含Y轴刻度）-->
            <Row crossAxisAlignment="END">
              <!-- Y轴刻度 -->
              <Container width="50" height="260">
                <Column mainAxisAlignment="SPACE_BETWEEN" crossAxisAlignment="END">
                  <Text color="{TEXT_SECONDARY}" fontSize="9">20万</Text>
                  <Text color="{TEXT_SECONDARY}" fontSize="9">15万</Text>
                  <Text color="{TEXT_SECONDARY}" fontSize="9">10万</Text>
                  <Text color="{TEXT_SECONDARY}" fontSize="9">5万</Text>
                  <Text color="{TEXT_SECONDARY}" fontSize="9">0</Text>
                </Column>
              </Container>
              <SizedBox width="8"/>
              <!-- 柱图 -->
              <Container width="670" height="260">
                <Row crossAxisAlignment="END" mainAxisAlignment="SPACE_EVENLY">''')

# 添加柱子
for i in range(6):
    dsl_parts.append(f'''                <Column crossAxisAlignment="CENTER" mainAxisAlignment="END">
                  <Row crossAxisAlignment="END">
                    <Container width="{bar_width}" height="{net_heights[i]}" color="{NET_COLOR}" borderRadius="3"/>
                    <SizedBox width="{bar_gap}"/>
                    <Container width="{bar_width}" height="{profit_heights[i]}" color="{PROFIT_COLOR}" borderRadius="3"/>
                  </Row>
                  <SizedBox height="6"/>
                  <Text color="{TEXT_SECONDARY}" fontSize="10">{months[i][-2:]}</Text>
                </Column>''')

dsl_parts.append(f'''              </Row>
            </Container>
          </Column>
        </Container>

        <!-- 右侧：两个共享月份对齐的小图 -->
        <Column mainAxisAlignment="SPACE_BETWEEN">
          <!-- 访问量小图 -->
          <Container width="372" height="192" color="{CARD_BG}" borderRadius="10" border="1 SOLID {CARD_BORDER}" padding="(12,14)">
            <Column crossAxisAlignment="START">
              <Text color="{TEXT_PRIMARY}" fontSize="13" fontStyle="BOLD">访问量（sessions）</Text>
              <SizedBox height="6"/>
              <Container width="344" height="120">
                <Row crossAxisAlignment="END" mainAxisAlignment="SPACE_EVENLY">''')

for i in range(6):
    dsl_parts.append(f'''                  <Column crossAxisAlignment="CENTER" mainAxisAlignment="END">
                    <Container width="28" height="{sess_heights[i]}" color="{ACCENT_CYAN}" borderRadius="2"/>
                    <SizedBox height="4"/>
                    <Text color="{TEXT_SECONDARY}" fontSize="9">{months[i][-2:]}</Text>
                  </Column>''')

dsl_parts.append(f'''                </Row>
              </Container>
            </Column>
          </Container>

          <!-- 转化率小图 -->
          <Container width="372" height="192" color="{CARD_BG}" borderRadius="10" border="1 SOLID {CARD_BORDER}" padding="(12,14)">
            <Column crossAxisAlignment="START">
              <Text color="{TEXT_PRIMARY}" fontSize="13" fontStyle="BOLD">月度转化率（%）</Text>
              <SizedBox height="6"/>
              <Container width="344" height="120">
                <Row crossAxisAlignment="END" mainAxisAlignment="SPACE_EVENLY">''')

for i in range(6):
    dsl_parts.append(f'''                  <Column crossAxisAlignment="CENTER" mainAxisAlignment="END">
                    <Container width="28" height="{conv_heights[i]}" color="{ACCENT_AMBER}" borderRadius="2"/>
                    <SizedBox height="4"/>
                    <Text color="{TEXT_SECONDARY}" fontSize="9">{months[i][-2:]}</Text>
                  </Column>''')

dsl_parts.append(f'''                </Row>
              </Container>
            </Column>
          </Container>
        </Column>
      </Row>

      <SizedBox height="12"/>

      <!-- 明细表 -->
      <Container width="1544" height="290" color="{CARD_BG}" borderRadius="10" border="1 SOLID {CARD_BORDER}" padding="(12,14)">
        <Column crossAxisAlignment="START">
          <Text color="{TEXT_PRIMARY}" fontSize="14" fontStyle="BOLD">月度明细</Text>
          <SizedBox height="8"/>
          <!-- 表头 -->
          <Container width="1512" height="30" color="{GRID_COLOR}" borderRadius="6" padding="(0,10)">
            <Row mainAxisAlignment="SPACE_BETWEEN" crossAxisAlignment="CENTER">
              <Text color="{TEXT_SECONDARY}" fontSize="11" fontStyle="BOLD">月份</Text>
              <Text color="{TEXT_SECONDARY}" fontSize="11" fontStyle="BOLD">净收入（元）</Text>
              <Text color="{TEXT_SECONDARY}" fontSize="11" fontStyle="BOLD">退款率</Text>
              <Text color="{TEXT_SECONDARY}" fontSize="11" fontStyle="BOLD">经营利润（元）</Text>
              <Text color="{TEXT_SECONDARY}" fontSize="11" fontStyle="BOLD">转化率</Text>
            </Row>
          </Container>''')

# 添加数据行
for i in range(6):
    bg = "#162032" if i % 2 == 0 else CARD_BG
    dsl_parts.append(f'''          <SizedBox height="3"/>
          <Container width="1512" height="30" color="{bg}" borderRadius="6" padding="(0,10)">
            <Row mainAxisAlignment="SPACE_BETWEEN" crossAxisAlignment="CENTER">
              <Text color="{TEXT_PRIMARY}" fontSize="11">{months[i]}</Text>
              <Text color="{NET_COLOR}" fontSize="11">{fmt_money(net[i])}</Text>
              <Text color="{ACCENT_RED if refund_rate[i] > 6 else TEXT_SECONDARY}" fontSize="11">{refund_rate[i]:.2f}%</Text>
              <Text color="{PROFIT_COLOR}" fontSize="11">{fmt_money(profit[i])}</Text>
              <Text color="{ACCENT_AMBER}" fontSize="11">{conv_rate[i]:.2f}%</Text>
            </Row>
          </Container>''')

dsl_parts.append(f'''        </Column>
      </Container>

      <SizedBox height="12"/>

      <!-- 管理结论 -->
      <Container width="1544" height="64" color="#1A2740" borderRadius="10" border="1 SOLID #2A3F5F" padding="(12,16)">
        <Row crossAxisAlignment="CENTER">
          <Container width="4" height="40" color="{ACCENT_BLUE}" borderRadius="2"/>
          <SizedBox width="12"/>
          <Column crossAxisAlignment="START">
            <Text color="{TEXT_PRIMARY}" fontSize="14" fontStyle="BOLD">管理结论</Text>
            <SizedBox height="4"/>
            <Text color="{TEXT_SECONDARY}" fontSize="12">六个月总净收入 {fmt_wan(total_net)}，总经营利润 {fmt_wan(total_profit)}，利润率 {total_profit/total_net*100:.1f}%。9月净收入最高（{fmt_wan(net[5])}），6月退款率异常（{refund_rate[2]:.2f}%）需关注。总体转化率 {overall_conv:.2f}%，建议持续优化转化链路。</Text>
          </Column>
        </Row>
      </Container>

    </Column>
  </Container>
</Snapshot>''')

dsl = "\n".join(dsl_parts)

# 保存DSL
with open(output_dir / "operations.snapshot", "w", encoding="utf-8") as f:
    f.write(dsl)

print(f"DSL generated: {len(dsl)} chars")
print(f"Total net: {total_net}, Total profit: {total_profit}")
print(f"Overall conversion: {overall_conv:.2f}%")
