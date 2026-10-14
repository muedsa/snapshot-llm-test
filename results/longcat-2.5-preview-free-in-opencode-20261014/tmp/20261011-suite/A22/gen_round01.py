import csv, json
from pathlib import Path

with open('tasks/A22-staged-data-correction/inputs/monthly.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

months = []
for r in rows:
    orders = int(r['orders'])
    gross = int(r['gross_revenue'])
    refund = int(r['refund_amount'])
    cost = int(r['operating_cost'])
    sessions = int(r['sessions'])
    net = gross - refund
    profit = net - cost
    refund_rate = refund / gross
    conv_rate = orders / sessions
    months.append({
        'month': r['month'], 'orders': orders, 'gross': gross, 'refund': refund,
        'cost': cost, 'sessions': sessions, 'net': net, 'profit': profit,
        'refund_rate': refund_rate, 'conv_rate': conv_rate
    })

total_orders = sum(m['orders'] for m in months)
total_net = sum(m['net'] for m in months)
total_profit = sum(m['profit'] for m in months)
total_sessions = sum(m['sessions'] for m in months)
overall_conv = total_orders / total_sessions

W, H = 1600, 1000
FONT = "Noto Sans CJK SC"
BG = "#F8FAFC"
CARD_BG = "#FFFFFF"
BORDER = "#E2E8F0"
TEXT_DARK = "#1E293B"
TEXT_MED = "#64748B"
BLUE = "#3B82F6"
GREEN = "#10B981"

dsl_parts = []
dsl_parts.append(f'<Snapshot type="png" background="{BG}">')
dsl_parts.append(f'  <Column mainAxisSize="MAX" height="{H}" width="{W}">')

# Title
dsl_parts.append(f'    <Container height="60" padding="(0,24)">')
dsl_parts.append(f'      <Column crossAxisAlignment="START">')
dsl_parts.append(f'        <Text text="经营驾驶舱" color="{TEXT_DARK}" fontSize="28" fontStyle="BOLD"/>')
dsl_parts.append(f'      </Column>')
dsl_parts.append(f'    </Container>')

# KPI cards
dsl_parts.append(f'    <Container height="100">')
dsl_parts.append(f'      <Row>')
dsl_parts.append(f'        <Container width="370" height="80" color="{CARD_BG}" border="1 SOLID {BORDER}" borderRadius="8" padding="(12,12)">')
dsl_parts.append(f'          <Column crossAxisAlignment="START">')
dsl_parts.append(f'            <Text text="总净收入" color="{TEXT_MED}" fontSize="14"/>')
dsl_parts.append(f'            <Text text="{total_net}元" color="{BLUE}" fontSize="22" fontStyle="BOLD"/>')
dsl_parts.append(f'          </Column>')
dsl_parts.append(f'        </Container>')
dsl_parts.append(f'        <SizedBox width="16"/>')
dsl_parts.append(f'        <Container width="370" height="80" color="{CARD_BG}" border="1 SOLID {BORDER}" borderRadius="8" padding="(12,12)">')
dsl_parts.append(f'          <Column crossAxisAlignment="START">')
dsl_parts.append(f'            <Text text="总经营利润" color="{TEXT_MED}" fontSize="14"/>')
dsl_parts.append(f'            <Text text="{total_profit}元" color="{GREEN}" fontSize="22" fontStyle="BOLD"/>')
dsl_parts.append(f'          </Column>')
dsl_parts.append(f'        </Container>')
dsl_parts.append(f'        <SizedBox width="16"/>')
dsl_parts.append(f'        <Container width="370" height="80" color="{CARD_BG}" border="1 SOLID {BORDER}" borderRadius="8" padding="(12,12)">')
dsl_parts.append(f'          <Column crossAxisAlignment="START">')
dsl_parts.append(f'            <Text text="总订单" color="{TEXT_MED}" fontSize="14"/>')
dsl_parts.append(f'            <Text text="{total_orders}笔" color="{TEXT_DARK}" fontSize="22" fontStyle="BOLD"/>')
dsl_parts.append(f'          </Column>')
dsl_parts.append(f'        </Container>')
dsl_parts.append(f'        <SizedBox width="16"/>')
dsl_parts.append(f'        <Container width="370" height="80" color="{CARD_BG}" border="1 SOLID {BORDER}" borderRadius="8" padding="(12,12)">')
dsl_parts.append(f'          <Column crossAxisAlignment="START">')
dsl_parts.append(f'            <Text text="总体转化率" color="{TEXT_MED}" fontSize="14"/>')
dsl_parts.append(f'            <Text text="{overall_conv*100:.2f}%" color="{TEXT_DARK}" fontSize="22" fontStyle="BOLD"/>')
dsl_parts.append(f'          </Column>')
dsl_parts.append(f'        </Container>')
dsl_parts.append(f'      </Row>')
dsl_parts.append(f'    </Container>')

# Chart area
dsl_parts.append(f'    <SizedBox height="16"/>')
dsl_parts.append(f'    <Container height="300" color="{CARD_BG}" border="1 SOLID {BORDER}" borderRadius="8" padding="(16,16)">')
dsl_parts.append(f'      <Column crossAxisAlignment="START">')
dsl_parts.append(f'        <Text text="月度净收入与经营利润" color="{TEXT_DARK}" fontSize="18" fontStyle="BOLD"/>')
dsl_parts.append(f'        <SizedBox height="16"/>')
for m in months:
    dsl_parts.append(f'        <Text text="{m["month"]}：净收入{m["net"]}元  利润{m["profit"]}元" color="{TEXT_DARK}" fontSize="14"/>')
    dsl_parts.append(f'        <SizedBox height="8"/>')
dsl_parts.append(f'      </Column>')
dsl_parts.append(f'    </Container>')

# Table
dsl_parts.append(f'    <SizedBox height="16"/>')
dsl_parts.append(f'    <Container height="250" color="{CARD_BG}" border="1 SOLID {BORDER}" borderRadius="8" padding="(16,16)">')
dsl_parts.append(f'      <Column crossAxisAlignment="START">')
dsl_parts.append(f'        <Text text="月度明细" color="{TEXT_DARK}" fontSize="18" fontStyle="BOLD"/>')
dsl_parts.append(f'        <SizedBox height="16"/>')
for m in months:
    dsl_parts.append(f'        <Text text="{m["month"]}  净收入{m["net"]}元  退款率{m["refund_rate"]*100:.2f}%  利润{m["profit"]}元  转化率{m["conv_rate"]*100:.2f}%" color="{TEXT_DARK}" fontSize="14"/>')
    dsl_parts.append(f'        <SizedBox height="8"/>')
dsl_parts.append(f'      </Column>')
dsl_parts.append(f'    </Container>')

# Conclusion
dsl_parts.append(f'    <SizedBox height="16"/>')
dsl_parts.append(f'    <Container height="60" padding="(0,24)">')
dsl_parts.append(f'      <Text text="主结论：2026年4-9月经营持续改善，总净收入{total_net}元，总利润{total_profit}元。" color="{TEXT_DARK}" fontSize="16"/>')
dsl_parts.append(f'    </Container>')

dsl_parts.append('  </Column>')
dsl_parts.append('</Snapshot>')

dsl = '\n'.join(dsl_parts)
with open('tmp/20261011-suite/A22/round-01/dashboard.snapshot', 'w', encoding='utf-8') as f:
    f.write(dsl)
print(f'Generated A22 round-01 DSL: {len(dsl)} chars')

# Save computed-data.json
computed = {
    "schema_version": 1,
    "task_id": "A22",
    "path_base": "output_dir",
    "months": [{"month": m["month"], "net": m["net"], "profit": m["profit"], "refund_rate": m["refund_rate"], "conv_rate": m["conv_rate"]} for m in months],
    "totals": {"total_net": total_net, "total_profit": total_profit, "total_orders": total_orders, "total_sessions": total_sessions, "overall_conv": overall_conv}
}

output_dir = Path('outputs/20261011-suite/A22/round-01')
output_dir.mkdir(parents=True, exist_ok=True)
with open(output_dir / 'computed-data.json', 'w', encoding='utf-8') as f:
    json.dump(computed, f, ensure_ascii=False, indent=2)

layout_map = {
    "schema_version": 1,
    "task_id": "A22",
    "path_base": "output_dir",
    "kpi_area": [24, 60, 1576, 160],
    "chart_area": [24, 176, 1576, 476],
    "table_area": [24, 492, 1576, 742]
}
with open(output_dir / 'layout-map.json', 'w', encoding='utf-8') as f:
    json.dump(layout_map, f, ensure_ascii=False, indent=2)
print("Saved computed-data.json and layout-map.json")
