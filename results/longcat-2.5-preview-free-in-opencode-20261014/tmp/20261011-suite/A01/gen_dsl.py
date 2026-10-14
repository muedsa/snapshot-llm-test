import csv, json
from pathlib import Path

# Read data
rows = []
with open('tasks/A01-operations-dashboard/inputs/monthly.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

months = []
for row in rows:
    orders = int(row['orders'])
    gross = int(row['gross_revenue'])
    refund = int(row['refund_amount'])
    cost = int(row['operating_cost'])
    sessions = int(row['sessions'])
    net = gross - refund
    profit = net - cost
    refund_rate = refund / gross
    conv_rate = orders / sessions
    months.append({
        'month': row['month'], 'orders': orders, 'gross_revenue': gross,
        'refund_amount': refund, 'operating_cost': cost, 'sessions': sessions,
        'net_revenue': net, 'profit': profit,
        'refund_rate': refund_rate, 'conversion_rate': conv_rate
    })

total_orders = sum(m['orders'] for m in months)
total_net = sum(m['net_revenue'] for m in months)
total_profit = sum(m['profit'] for m in months)
total_sessions = sum(m['sessions'] for m in months)
overall_conv = total_orders / total_sessions

# Layout constants
W, H = 1600, 1000
MARGIN = 24
TITLE_H = 64
KPI_H = 110
KPI_GAP = 16
CHART_H = 380
TABLE_H = 340

# Colors
BG = "#F8FAFC"
CARD_BG = "#FFFFFF"
CARD_BORDER = "#E2E8F0"
TEXT_DARK = "#1E293B"
TEXT_MED = "#64748B"
TEXT_LIGHT = "#94A3B8"
BLUE = "#3B82F6"
GREEN = "#10B981"
ORANGE = "#F59E0B"
RED = "#EF4444"
GRID = "#E2E8F0"
AXIS = "#CBD5E1"

# KPI cards
kpi_w = (W - 2 * MARGIN - 3 * KPI_GAP) // 4
kpis = [
    ("总净收入", f"{total_net:,}元", f"≈{total_net/10000:.1f}万", BLUE),
    ("总经营利润", f"{total_profit:,}元", f"≈{total_profit/10000:.1f}万", GREEN),
    ("总订单", f"{total_orders:,}笔", "六个月累计", ORANGE),
    ("总体转化率", f"{overall_conv*100:.2f}%", f"{total_orders}/{total_sessions}", RED),
]

# Chart area
chart_x = MARGIN
chart_y = TITLE_H + KPI_H + 20
chart_w = 920
chart_h = CHART_H

# Bar chart calculations
bar_area_x = chart_x + 60
bar_area_y = chart_y + 40
bar_area_w = chart_w - 80
bar_area_h = chart_h - 80
max_val = 220000
n_months = 6
bar_group_w = bar_area_w / n_months
bar_w = bar_group_w / 2 - 6

# Small charts
small_x = chart_x + chart_w + 20
small_w = W - MARGIN - small_x
small_h = (CHART_H - 16) // 2

# Table
table_x = MARGIN
table_y = chart_y + chart_h + 20
table_w = 920
table_h = H - table_y - MARGIN

# Conclusion
concl_x = table_x + table_w + 20
concl_w = W - MARGIN - concl_x

# Build DSL
dsl_parts = []
dsl_parts.append(f'<Snapshot type="png" background="{BG}">')
dsl_parts.append(f'  <Column mainAxisSize="MAX" height="{H}">')

# Title
dsl_parts.append(f'    <Container height="{TITLE_H}" padding="(0,{MARGIN})">')
dsl_parts.append(f'      <Row mainAxisAlignment="SPACE_BETWEEN" crossAxisAlignment="CENTER">')
dsl_parts.append(f'        <Text text="Northstar 经营诊断驾驶舱" color="{TEXT_DARK}" fontSize="26" fontStyle="BOLD"/>')
dsl_parts.append(f'        <Text text="2026年4月 – 2026年9月" color="{TEXT_MED}" fontSize="16"/>')
dsl_parts.append(f'      </Row>')
dsl_parts.append(f'    </Container>')

# KPI cards
dsl_parts.append(f'    <Row>')
for i, (label, value, sub, color) in enumerate(kpis):
    dsl_parts.append(f'      <Expanded>')
    dsl_parts.append(f'        <Container height="{KPI_H}" color="{CARD_BG}" border="1 SOLID {CARD_BORDER}" borderRadius="12" padding="(16,20)">')
    dsl_parts.append(f'          <Column crossAxisAlignment="START">')
    dsl_parts.append(f'            <Text text="{label}" color="{TEXT_MED}" fontSize="14"/>')
    dsl_parts.append(f'            <SizedBox height="8"/>')
    dsl_parts.append(f'            <Text text="{value}" color="{color}" fontSize="24" fontStyle="BOLD"/>')
    dsl_parts.append(f'            <SizedBox height="4"/>')
    dsl_parts.append(f'            <Text text="{sub}" color="{TEXT_LIGHT}" fontSize="12"/>')
    dsl_parts.append(f'          </Column>')
    dsl_parts.append(f'        </Container>')
    dsl_parts.append(f'      </Expanded>')
    if i < 3:
        dsl_parts.append(f'      <SizedBox width="{KPI_GAP}"/>')
dsl_parts.append(f'    </Row>')

# Main chart area
dsl_parts.append(f'    <SizedBox height="20"/>')
dsl_parts.append(f'    <Row>')

# Left: Grouped bar chart
dsl_parts.append(f'      <Expanded>')
dsl_parts.append(f'        <Container height="{CHART_H}" color="{CARD_BG}" border="1 SOLID {CARD_BORDER}" borderRadius="12" padding="(16,20)">')
dsl_parts.append(f'          <Column crossAxisAlignment="START">')
dsl_parts.append(f'            <Text text="月度净收入与经营利润" color="{TEXT_DARK}" fontSize="16" fontStyle="BOLD"/>')
dsl_parts.append(f'            <SizedBox height="12"/>')

# Chart area with Stack
dsl_parts.append(f'            <Container width="{chart_w-40}" height="{chart_h-60}">')
dsl_parts.append(f'              <Stack fit="EXPAND">')

# Grid lines and bars
for i, m in enumerate(months):
    x = bar_area_x - chart_x - 20 + i * bar_group_w
    # Net revenue bar
    net_h = int(m['net_revenue'] / max_val * bar_area_h)
    profit_h = int(m['profit'] / max_val * bar_area_h)
    dsl_parts.append(f'                <Positioned left="{x:.0f}" bottom="0" width="{bar_w:.0f}" height="{net_h}">')
    dsl_parts.append(f'                  <Container color="{BLUE}" borderRadius="4"/>')
    dsl_parts.append(f'                </Positioned>')
    dsl_parts.append(f'                <Positioned left="{x + bar_w + 4:.0f}" bottom="0" width="{bar_w:.0f}" height="{profit_h}">')
    dsl_parts.append(f'                  <Container color="{GREEN}" borderRadius="4"/>')
    dsl_parts.append(f'                </Positioned>')

dsl_parts.append(f'              </Stack>')
dsl_parts.append(f'            </Container>')

# X axis labels
dsl_parts.append(f'            <Row>')
for i, m in enumerate(months):
    dsl_parts.append(f'              <Expanded>')
    dsl_parts.append(f'                <Text text="{m["month"][5:]}" color="{TEXT_MED}" fontSize="12" textAlign="CENTER"/>')
    dsl_parts.append(f'              </Expanded>')
dsl_parts.append(f'            </Row>')

# Legend
dsl_parts.append(f'            <Row mainAxisAlignment="CENTER">')
dsl_parts.append(f'              <Container width="12" height="12" color="{BLUE}" borderRadius="2"/>')
dsl_parts.append(f'              <SizedBox width="6"/>')
dsl_parts.append(f'              <Text text="净收入" color="{TEXT_MED}" fontSize="12"/>')
dsl_parts.append(f'              <SizedBox width="20"/>')
dsl_parts.append(f'              <Container width="12" height="12" color="{GREEN}" borderRadius="2"/>')
dsl_parts.append(f'              <SizedBox width="6"/>')
dsl_parts.append(f'              <Text text="经营利润" color="{TEXT_MED}" fontSize="12"/>')
dsl_parts.append(f'            </Row>')

dsl_parts.append(f'          </Column>')
dsl_parts.append(f'        </Container>')
dsl_parts.append(f'      </Expanded>')

dsl_parts.append(f'      <SizedBox width="20"/>')

# Right: Two small charts
dsl_parts.append(f'      <Expanded>')
dsl_parts.append(f'        <Column>')

# Sessions chart
dsl_parts.append(f'          <Container height="{small_h}" color="{CARD_BG}" border="1 SOLID {CARD_BORDER}" borderRadius="12">')
dsl_parts.append(f'            <Padding padding="(16,16)">')
dsl_parts.append(f'              <Column crossAxisAlignment="START">')
dsl_parts.append(f'                <Text text="月度访问量" color="{TEXT_DARK}" fontSize="14" fontStyle="BOLD"/>')
dsl_parts.append(f'                <SizedBox height="8"/>')
dsl_parts.append(f'                <Container width="{small_w-32}" height="{small_h-50}">')
dsl_parts.append(f'                  <Stack fit="EXPAND">')
for i, m in enumerate(months):
    x = i * (small_w - 32) / 6
    h = int(m['sessions'] / 6000 * (small_h - 50))
    dsl_parts.append(f'                    <Positioned left="{x:.0f}" bottom="0" width="{(small_w-32)/6-4:.0f}" height="{h}">')
    dsl_parts.append(f'                      <Container color="{ORANGE}" borderRadius="3"/>')
    dsl_parts.append(f'                    </Positioned>')
dsl_parts.append(f'                  </Stack>')
dsl_parts.append(f'                </Container>')
dsl_parts.append(f'                <Row>')
for i, m in enumerate(months):
    dsl_parts.append(f'                  <Expanded>')
    dsl_parts.append(f'                    <Text text="{m["month"][5:]}" color="{TEXT_LIGHT}" fontSize="10" textAlign="CENTER"/>')
    dsl_parts.append(f'                  </Expanded>')
dsl_parts.append(f'                </Row>')
dsl_parts.append(f'              </Column>')
dsl_parts.append(f'            </Padding>')
dsl_parts.append(f'          </Container>')

dsl_parts.append(f'          <SizedBox height="16"/>')

# Conversion rate chart
dsl_parts.append(f'          <Container height="{small_h}" color="{CARD_BG}" border="1 SOLID {CARD_BORDER}" borderRadius="12">')
dsl_parts.append(f'            <Padding padding="(16,16)">')
dsl_parts.append(f'              <Column crossAxisAlignment="START">')
dsl_parts.append(f'                <Text text="月度转化率" color="{TEXT_DARK}" fontSize="14" fontStyle="BOLD"/>')
dsl_parts.append(f'                <SizedBox height="8"/>')
dsl_parts.append(f'                <Container width="{small_w-32}" height="{small_h-50}">')
dsl_parts.append(f'                  <Stack fit="EXPAND">')
for i, m in enumerate(months):
    x = i * (small_w - 32) / 6
    h = int(m['conversion_rate'] / 0.15 * (small_h - 50))
    dsl_parts.append(f'                    <Positioned left="{x:.0f}" bottom="0" width="{(small_w-32)/6-4:.0f}" height="{h}">')
    dsl_parts.append(f'                      <Container color="{RED}" borderRadius="3"/>')
    dsl_parts.append(f'                    </Positioned>')
dsl_parts.append(f'                  </Stack>')
dsl_parts.append(f'                </Container>')
dsl_parts.append(f'                <Row>')
for i, m in enumerate(months):
    dsl_parts.append(f'                  <Expanded>')
    dsl_parts.append(f'                    <Text text="{m["month"][5:]}" color="{TEXT_LIGHT}" fontSize="10" textAlign="CENTER"/>')
    dsl_parts.append(f'                  </Expanded>')
dsl_parts.append(f'                </Row>')
dsl_parts.append(f'              </Column>')
dsl_parts.append(f'            </Padding>')
dsl_parts.append(f'          </Container>')

dsl_parts.append(f'        </Column>')
dsl_parts.append(f'      </Expanded>')

dsl_parts.append(f'    </Row>')

# Bottom area
dsl_parts.append(f'    <SizedBox height="20"/>')
dsl_parts.append(f'    <Row>')

# Left: Detail table
dsl_parts.append(f'      <Expanded>')
dsl_parts.append(f'        <Container height="{TABLE_H}" color="{CARD_BG}" border="1 SOLID {CARD_BORDER}" borderRadius="12" padding="(16,20)">')
dsl_parts.append(f'          <Column crossAxisAlignment="START">')
dsl_parts.append(f'            <Text text="月度明细" color="{TEXT_DARK}" fontSize="16" fontStyle="BOLD"/>')
dsl_parts.append(f'            <SizedBox height="12"/>')

# Table header
dsl_parts.append(f'            <Row>')
dsl_parts.append(f'              <Expanded><Text text="月份" color="{TEXT_MED}" fontSize="12" fontStyle="BOLD"/></Expanded>')
dsl_parts.append(f'              <Expanded><Text text="净收入(元)" color="{TEXT_MED}" fontSize="12" fontStyle="BOLD" textAlign="END"/></Expanded>')
dsl_parts.append(f'              <Expanded><Text text="退款率" color="{TEXT_MED}" fontSize="12" fontStyle="BOLD" textAlign="END"/></Expanded>')
dsl_parts.append(f'              <Expanded><Text text="利润(元)" color="{TEXT_MED}" fontSize="12" fontStyle="BOLD" textAlign="END"/></Expanded>')
dsl_parts.append(f'              <Expanded><Text text="转化率" color="{TEXT_MED}" fontSize="12" fontStyle="BOLD" textAlign="END"/></Expanded>')
dsl_parts.append(f'            </Row>')
dsl_parts.append(f'            <Container height="1" color="{GRID}"/>')
dsl_parts.append(f'            <SizedBox height="8"/>')

# Table rows
for m in months:
    dsl_parts.append(f'            <Row>')
    dsl_parts.append(f'              <Expanded><Text text="{m["month"]}" color="{TEXT_DARK}" fontSize="13"/></Expanded>')
    dsl_parts.append(f'              <Expanded><Text text="{m["net_revenue"]:,}" color="{TEXT_DARK}" fontSize="13" textAlign="END"/></Expanded>')
    dsl_parts.append(f'              <Expanded><Text text="{m["refund_rate"]*100:.2f}%" color="{TEXT_DARK}" fontSize="13" textAlign="END"/></Expanded>')
    dsl_parts.append(f'              <Expanded><Text text="{m["profit"]:,}" color="{TEXT_DARK}" fontSize="13" textAlign="END"/></Expanded>')
    dsl_parts.append(f'              <Expanded><Text text="{m["conversion_rate"]*100:.2f}%" color="{TEXT_DARK}" fontSize="13" textAlign="END"/></Expanded>')
    dsl_parts.append(f'            </Row>')
    dsl_parts.append(f'            <SizedBox height="6"/>')

dsl_parts.append(f'          </Column>')
dsl_parts.append(f'        </Container>')
dsl_parts.append(f'      </Expanded>')

dsl_parts.append(f'      <SizedBox width="20"/>')

# Right: Conclusion
dsl_parts.append(f'      <Expanded>')
dsl_parts.append(f'        <Container height="{TABLE_H}" color="{CARD_BG}" border="1 SOLID {CARD_BORDER}" borderRadius="12" padding="(16,20)">')
dsl_parts.append(f'          <Column crossAxisAlignment="START">')
dsl_parts.append(f'            <Text text="管理结论" color="{TEXT_DARK}" fontSize="16" fontStyle="BOLD"/>')
dsl_parts.append(f'            <SizedBox height="12"/>')
dsl_parts.append(f'            <Text text="2026年4-9月经营持续改善，总净收入91.86万元，总利润26.21万元，9月利润创六个月新高。但6月和8月退款率升至8%，需关注退款原因。" color="{TEXT_DARK}" fontSize="14"/>')
dsl_parts.append(f'            <SizedBox height="16"/>')
dsl_parts.append(f'            <Text text="关键指标" color="{TEXT_MED}" fontSize="12" fontStyle="BOLD"/>')
dsl_parts.append(f'            <SizedBox height="8"/>')
dsl_parts.append(f'            <Text text="• 9月净收入202,368元，为六个月最高" color="{TEXT_DARK}" fontSize="13"/>')
dsl_parts.append(f'            <SizedBox height="4"/>')
dsl_parts.append(f'            <Text text="• 6月退款率8.00%，为期间最高" color="{TEXT_DARK}" fontSize="13"/>')
dsl_parts.append(f'            <SizedBox height="4"/>')
dsl_parts.append(f'            <Text text="• 总体转化率11.15%，保持稳定" color="{TEXT_DARK}" fontSize="13"/>')
dsl_parts.append(f'          </Column>')
dsl_parts.append(f'        </Container>')
dsl_parts.append(f'      </Expanded>')

dsl_parts.append(f'    </Row>')

dsl_parts.append(f'  </Column>')
dsl_parts.append(f'</Snapshot>')

dsl = '\n'.join(dsl_parts)
with open('tmp/20261011-suite/A01/operations.snapshot', 'w', encoding='utf-8') as f:
    f.write(dsl)
print(f'Generated DSL: {len(dsl)} chars')
