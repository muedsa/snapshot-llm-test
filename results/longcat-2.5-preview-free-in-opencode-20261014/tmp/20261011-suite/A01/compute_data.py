import csv, json
from pathlib import Path

rows = []
with open('tasks/A01-operations-dashboard/inputs/monthly.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

months = []
for row in rows:
    month = row['month']
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
        'month': month, 'orders': orders, 'gross_revenue': gross,
        'refund_amount': refund, 'operating_cost': cost, 'sessions': sessions,
        'net_revenue': net, 'profit': profit,
        'refund_rate': refund_rate, 'conversion_rate': conv_rate
    })

total_orders = sum(m['orders'] for m in months)
total_gross = sum(m['gross_revenue'] for m in months)
total_refund = sum(m['refund_amount'] for m in months)
total_cost = sum(m['operating_cost'] for m in months)
total_net = sum(m['net_revenue'] for m in months)
total_profit = sum(m['profit'] for m in months)
total_sessions = sum(m['sessions'] for m in months)
overall_conv = total_orders / total_sessions

print('=== Monthly Data ===')
for m in months:
    print(f"{m['month']}: net={m['net_revenue']}, profit={m['profit']}, refund_rate={m['refund_rate']:.4f}, conv={m['conversion_rate']:.4f}")
print(f'\n=== Totals ===')
print(f'Total orders: {total_orders}')
print(f'Total gross: {total_gross}')
print(f'Total refund: {total_refund}')
print(f'Total cost: {total_cost}')
print(f'Total net: {total_net}')
print(f'Total profit: {total_profit}')
print(f'Total sessions: {total_sessions}')
print(f'Overall conversion: {overall_conv:.4f}')

output_dir = Path('outputs/20261011-suite/A01')
output_dir.mkdir(parents=True, exist_ok=True)

computed = {
    'schema_version': 1,
    'task_id': 'A01',
    'path_base': 'output_dir',
    'months': months,
    'totals': {
        'total_orders': total_orders,
        'total_gross_revenue': total_gross,
        'total_refund': total_refund,
        'total_operating_cost': total_cost,
        'total_net_revenue': total_net,
        'total_profit': total_profit,
        'total_sessions': total_sessions,
        'overall_conversion_rate': overall_conv
    },
    'axes': [],
    'conclusion': {
        'text': '2026年4-9月经营持续改善，总净收入91.86万元，总利润26.21万元，9月利润创六个月新高。但6月和8月退款率升至8%，需关注退款原因。',
        'references': {
            'total_net_revenue': total_net,
            'total_profit': total_profit,
            'september_profit': months[5]['profit'],
            'august_refund_rate': months[4]['refund_rate']
        }
    }
}

with open(output_dir / 'computed-data.json', 'w', encoding='utf-8') as f:
    json.dump(computed, f, ensure_ascii=False, indent=2)
print('\nSaved computed-data.json')
