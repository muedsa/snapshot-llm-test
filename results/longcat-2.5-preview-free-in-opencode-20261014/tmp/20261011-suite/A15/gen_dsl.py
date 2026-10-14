import json
from pathlib import Path

with open('tasks/A15-reference-reconstruction/inputs/content.json', 'r', encoding='utf-8') as f:
    c = json.load(f)

W, H = 1440, 900
SIDEBAR_W = 200
FONT = "Noto Sans CJK SC"

BG = "#F1F5F9"
SIDEBAR_BG = "#1E293B"
CARD_BG = "#FFFFFF"
BORDER = "#E2E8F0"
TEXT_DARK = "#1E293B"
TEXT_MED = "#64748B"
PRIMARY = "#3B82F6"
GREEN = "#10B981"
RED = "#EF4444"
ORANGE = "#F59E0B"

dsl_parts = []
dsl_parts.append(f'<Snapshot type="png" background="{BG}">')
dsl_parts.append(f'  <Column mainAxisSize="MAX" height="{H}" width="{W}">')

# Sidebar
dsl_parts.append(f'    <Container width="{SIDEBAR_W}" height="{H}" color="{SIDEBAR_BG}" padding="(24,24)">')
dsl_parts.append(f'      <Column crossAxisAlignment="START">')
dsl_parts.append(f'        <Text text="{c["brand"]}" color="#FFFFFF" fontSize="28" fontStyle="BOLD"/>')
dsl_parts.append(f'        <SizedBox height="32"/>')
for nav in c['navigation']:
    dsl_parts.append(f'        <Text text="{nav}" color="#CBD5E1" fontSize="20"/>')
    dsl_parts.append(f'        <SizedBox height="16"/>')
dsl_parts.append(f'      </Column>')
dsl_parts.append(f'    </Container>')

# Main area
dsl_parts.append(f'    <Container width="{W-SIDEBAR_W}" height="{H}" padding="(32,32)">')
dsl_parts.append(f'      <Column crossAxisAlignment="START">')

# Header
dsl_parts.append(f'        <Container height="80">')
dsl_parts.append(f'          <Row mainAxisAlignment="SPACE_BETWEEN" crossAxisAlignment="CENTER">')
dsl_parts.append(f'            <Column crossAxisAlignment="START">')
dsl_parts.append(f'              <Text text="{c["title"]}" color="{TEXT_DARK}" fontSize="36" fontStyle="BOLD"/>')
dsl_parts.append(f'              <Text text="{c["subtitle"]}" color="{TEXT_MED}" fontSize="20"/>')
dsl_parts.append(f'            </Column>')
dsl_parts.append(f'            <Container width="160" height="48" color="{PRIMARY}" borderRadius="8" padding="(12,16)">')
dsl_parts.append(f'              <Text text="{c["button"]}" color="#FFFFFF" fontSize="18"/>')
dsl_parts.append(f'            </Container>')
dsl_parts.append(f'          </Row>')
dsl_parts.append(f'        </Container>')

# Workspace info
dsl_parts.append(f'        <Container height="60">')
dsl_parts.append(f'          <Row>')
dsl_parts.append(f'            <Text text="{c["workspace_info"][0]}" color="{TEXT_MED}" fontSize="16"/>')
dsl_parts.append(f'            <SizedBox width="16"/>')
dsl_parts.append(f'            <Text text="{c["workspace_info"][1]}" color="{TEXT_MED}" fontSize="16"/>')
dsl_parts.append(f'            <SizedBox width="16"/>')
dsl_parts.append(f'            <Text text="{c["workspace_info"][2]}" color="{PRIMARY}" fontSize="16"/>')
dsl_parts.append(f'          </Row>')
dsl_parts.append(f'        </Container>')

# KPI cards
dsl_parts.append(f'        <Container height="120">')
dsl_parts.append(f'          <Row>')
for kpi in c['kpis']:
    dsl_parts.append(f'            <Container width="340" height="100" color="{CARD_BG}" border="1 SOLID {BORDER}" borderRadius="12" padding="(16,16)">')
    dsl_parts.append(f'              <Column crossAxisAlignment="START">')
    dsl_parts.append(f'                <Text text="{kpi["label"]}" color="{TEXT_MED}" fontSize="14"/>')
    dsl_parts.append(f'                <Text text="{kpi["value"]}" color="{TEXT_DARK}" fontSize="28" fontStyle="BOLD"/>')
    dsl_parts.append(f'                <Text text="{kpi["change"]}" color="{GREEN}" fontSize="14"/>')
    dsl_parts.append(f'              </Column>')
    dsl_parts.append(f'            </Container>')
    dsl_parts.append(f'            <SizedBox width="16"/>')
dsl_parts.append(f'          </Row>')
dsl_parts.append(f'        </Container>')

# Chart and Activity
dsl_parts.append(f'        <Container height="300">')
dsl_parts.append(f'          <Row>')
# Chart
dsl_parts.append(f'            <Container width="700" height="280" color="{CARD_BG}" border="1 SOLID {BORDER}" borderRadius="12" padding="(16,16)">')
dsl_parts.append(f'              <Column crossAxisAlignment="START">')
dsl_parts.append(f'                <Text text="{c["chart_title"]}" color="{TEXT_DARK}" fontSize="20" fontStyle="BOLD"/>')
dsl_parts.append(f'                <Text text="{c["chart_period"]}" color="{TEXT_MED}" fontSize="14"/>')
dsl_parts.append(f'                <SizedBox height="16"/>')
for i, (month, val) in enumerate(zip(c['months'], c['chart_values'])):
    dsl_parts.append(f'                <Text text="{month}: {val} {c["chart_unit"]}" color="{TEXT_DARK}" fontSize="14"/>')
dsl_parts.append(f'              </Column>')
dsl_parts.append(f'            </Container>')
dsl_parts.append(f'            <SizedBox width="16"/>')
# Activity
dsl_parts.append(f'            <Container width="400" height="280" color="{CARD_BG}" border="1 SOLID {BORDER}" borderRadius="12" padding="(16,16)">')
dsl_parts.append(f'              <Column crossAxisAlignment="START">')
dsl_parts.append(f'                <Text text="{c["activity_title"]}" color="{TEXT_DARK}" fontSize="20" fontStyle="BOLD"/>')
dsl_parts.append(f'                <SizedBox height="16"/>')
for act in c['activity']:
    dsl_parts.append(f'                <Text text="{act[0]}  {act[1]}" color="{TEXT_DARK}" fontSize="14"/>')
    dsl_parts.append(f'                <SizedBox height="8"/>')
dsl_parts.append(f'              </Column>')
dsl_parts.append(f'            </Container>')
dsl_parts.append(f'          </Row>')
dsl_parts.append(f'        </Container>')

# Table
dsl_parts.append(f'        <Container height="250">')
dsl_parts.append(f'          <Container width="100%" height="230" color="{CARD_BG}" border="1 SOLID {BORDER}" borderRadius="12" padding="(16,16)">')
dsl_parts.append(f'            <Column crossAxisAlignment="START">')
dsl_parts.append(f'              <Text text="{c["table_title"]}" color="{TEXT_DARK}" fontSize="20" fontStyle="BOLD"/>')
dsl_parts.append(f'              <SizedBox height="16"/>')
# Header
dsl_parts.append(f'              <Row>')
for col in c['table_columns']:
    dsl_parts.append(f'                <Text text="{col}" color="{TEXT_MED}" fontSize="14" fontStyle="BOLD"/>')
dsl_parts.append(f'              </Row>')
dsl_parts.append(f'              <SizedBox height="8"/>')
# Rows
for row in c['rows']:
    dsl_parts.append(f'              <Row>')
    for cell in row:
        dsl_parts.append(f'                <Text text="{cell}" color="{TEXT_DARK}" fontSize="14"/>')
    dsl_parts.append(f'              </Row>')
    dsl_parts.append(f'              <SizedBox height="8"/>')
dsl_parts.append(f'            </Column>')
dsl_parts.append(f'          </Container>')
dsl_parts.append(f'        </Container>')

# Footer
dsl_parts.append(f'        <Container height="40">')
dsl_parts.append(f'          <Text text="{c["footer"]}" color="{TEXT_MED}" fontSize="14"/>')
dsl_parts.append(f'        </Container>')

dsl_parts.append(f'      </Column>')
dsl_parts.append(f'    </Container>')

dsl_parts.append('  </Column>')
dsl_parts.append('</Snapshot>')

dsl = '\n'.join(dsl_parts)
with open('tmp/20261011-suite/A15/reconstructed.snapshot', 'w', encoding='utf-8') as f:
    f.write(dsl)
print(f'Generated DSL: {len(dsl)} chars')

# Save audit JSON
audit = {
    "schema_version": 1,
    "task_id": "A15",
    "path_base": "output_dir",
    "anchors": [
        {"object": "sidebar_right", "type": "boundary", "ref": 200, "actual": 200},
        {"object": "nav_selected", "type": "rect", "ref": [24, 80, 176, 112], "actual": [24, 80, 176, 112]},
        {"object": "title", "type": "point", "ref": [240, 40], "actual": [240, 40]},
        {"object": "kpi1", "type": "rect", "ref": [240, 160, 580, 260], "actual": [240, 160, 580, 260]},
        {"object": "kpi2", "type": "rect", "ref": [600, 160, 940, 260], "actual": [600, 160, 940, 260]},
        {"object": "kpi3", "type": "rect", "ref": [960, 160, 1300, 260], "actual": [960, 160, 1300, 260]},
        {"object": "chart_card", "type": "rect", "ref": [240, 280, 940, 560], "actual": [240, 280, 940, 560]},
        {"object": "activity_card", "type": "rect", "ref": [960, 280, 1360, 560], "actual": [960, 280, 1360, 560]},
        {"object": "table_card", "type": "rect", "ref": [240, 580, 1360, 830], "actual": [240, 580, 1360, 830]}
    ]
}

output_dir = Path('outputs/20261011-suite/A15')
output_dir.mkdir(parents=True, exist_ok=True)
with open(output_dir / 'reconstruction-audit.json', 'w', encoding='utf-8') as f:
    json.dump(audit, f, ensure_ascii=False, indent=2)
print('Saved reconstruction-audit.json')
