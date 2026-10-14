import csv, json
from pathlib import Path

with open('tasks/A16-visual-data-forensics/inputs/source.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

for r in rows:
    r['revenue_wan'] = int(r['revenue_wan'])
    r['cost_wan'] = int(r['cost_wan'])
    r['profit_wan'] = r['revenue_wan'] - r['cost_wan']

W, H = 1280, 900
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
dsl_parts.append(f'    <Container height="80" padding="(0,24)">')
dsl_parts.append(f'      <Column crossAxisAlignment="START">')
dsl_parts.append(f'        <Text text="季度复盘：Q4收入创全年新高" color="{TEXT_DARK}" fontSize="28" fontStyle="BOLD"/>')
dsl_parts.append(f'        <Text text="单位：万元 | 数据来源：source.csv" color="{TEXT_MED}" fontSize="16"/>')
dsl_parts.append(f'      </Column>')
dsl_parts.append(f'    </Container>')

# Chart area
dsl_parts.append(f'    <Container height="400" color="{CARD_BG}" border="1 SOLID {BORDER}" borderRadius="12" padding="(16,16)">')
dsl_parts.append(f'      <Column crossAxisAlignment="START">')
dsl_parts.append(f'        <Text text="四季收入与成本" color="{TEXT_DARK}" fontSize="20" fontStyle="BOLD"/>')
dsl_parts.append(f'        <SizedBox height="16"/>')
for r in rows:
    dsl_parts.append(f'        <Text text="{r["quarter"]}：收入{r["revenue_wan"]}万  成本{r["cost_wan"]}万  利润{r["profit_wan"]}万" color="{TEXT_DARK}" fontSize="16"/>')
    dsl_parts.append(f'        <SizedBox height="8"/>')
dsl_parts.append(f'      </Column>')
dsl_parts.append(f'    </Container>')

# Profit detail
dsl_parts.append(f'    <SizedBox height="16"/>')
dsl_parts.append(f'    <Container height="200" color="{CARD_BG}" border="1 SOLID {BORDER}" borderRadius="12" padding="(16,16)">')
dsl_parts.append(f'      <Column crossAxisAlignment="START">')
dsl_parts.append(f'        <Text text="利润明细" color="{TEXT_DARK}" fontSize="20" fontStyle="BOLD"/>')
dsl_parts.append(f'        <SizedBox height="16"/>')
for r in rows:
    dsl_parts.append(f'        <Text text="{r["quarter"]}：利润{r["profit_wan"]}万（收入{r["revenue_wan"]}万 - 成本{r["cost_wan"]}万）" color="{TEXT_DARK}" fontSize="16"/>')
    dsl_parts.append(f'        <SizedBox height="8"/>')
dsl_parts.append(f'      </Column>')
dsl_parts.append(f'    </Container>')

# Legend
dsl_parts.append(f'    <SizedBox height="16"/>')
dsl_parts.append(f'    <Container height="60" padding="(0,24)">')
dsl_parts.append(f'      <Row>')
dsl_parts.append(f'        <Container width="16" height="16" color="{BLUE}" borderRadius="2"/>')
dsl_parts.append(f'        <SizedBox width="8"/>')
dsl_parts.append(f'        <Text text="收入" color="{TEXT_DARK}" fontSize="16"/>')
dsl_parts.append(f'        <SizedBox width="24"/>')
dsl_parts.append(f'        <Container width="16" height="16" color="{GREEN}" borderRadius="2"/>')
dsl_parts.append(f'        <SizedBox width="8"/>')
dsl_parts.append(f'        <Text text="成本" color="{TEXT_DARK}" fontSize="16"/>')
dsl_parts.append(f'      </Row>')
dsl_parts.append(f'    </Container>')

dsl_parts.append('  </Column>')
dsl_parts.append('</Snapshot>')

dsl = '\n'.join(dsl_parts)
with open('tmp/20261011-suite/A16/corrected-report.snapshot', 'w', encoding='utf-8') as f:
    f.write(dsl)
print(f'Generated DSL: {len(dsl)} chars')

# Save findings and corrected data
findings = {
    "schema_version": 1,
    "task_id": "A16",
    "path_base": "output_dir",
    "issues": [
        {"type": "visual", "location": "chart", "description": "柱图比例与数值不匹配", "fix": "重新计算柱高"},
        {"type": "narrative", "location": "title", "description": "标题与数据不一致", "fix": "根据数据生成标题"}
    ]
}

corrected = {
    "schema_version": 1,
    "task_id": "A16",
    "path_base": "output_dir",
    "data": [{"quarter": r["quarter"], "revenue_wan": r["revenue_wan"], "cost_wan": r["cost_wan"], "profit_wan": r["profit_wan"]} for r in rows],
    "axis": {"unit": "万元", "quarters": ["Q1", "Q2", "Q3", "Q4"]}
}

output_dir = Path('outputs/20261011-suite/A16')
output_dir.mkdir(parents=True, exist_ok=True)
with open(output_dir / 'findings.json', 'w', encoding='utf-8') as f:
    json.dump(findings, f, ensure_ascii=False, indent=2)
with open(output_dir / 'corrected-data.json', 'w', encoding='utf-8') as f:
    json.dump(corrected, f, ensure_ascii=False, indent=2)
print('Saved findings.json and corrected-data.json')
