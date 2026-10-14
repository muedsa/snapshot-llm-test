import json
from pathlib import Path

with open('tasks/A14-content-stress-batch/inputs/cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

W, H = 1200, 630
MARGIN = 40
FONT = "Noto Sans CJK SC"

STATUS_COLORS = {
    "开放": "#10B981",
    "满额": "#EF4444",
    "候补": "#F59E0B",
    "取消": "#64748B",
}

BG = "#0F172A"
CARD_BG = "#1E293B"
BORDER = "#334155"
TEXT_DARK = "#F8FAFC"
TEXT_MED = "#CBD5E1"

output_dir = Path('outputs/20261011-suite/A14')
output_dir.mkdir(parents=True, exist_ok=True)

for card in cards:
    cid = card['id']
    title = card['title']
    speaker = card['speaker']
    status = card['status']
    time = card['time']
    color = STATUS_COLORS[status]

    dsl_parts = []
    dsl_parts.append(f'<Snapshot type="png" background="{BG}">')
    dsl_parts.append(f'  <Column mainAxisSize="MAX" height="{H}" width="{W}">')

    # Header
    dsl_parts.append(f'    <Container height="60" padding="({MARGIN},{MARGIN})">')
    dsl_parts.append(f'      <Row mainAxisAlignment="SPACE_BETWEEN">')
    dsl_parts.append(f'        <Text text="Structure / Vision" color="{TEXT_DARK}" fontSize="28" fontStyle="BOLD"/>')
    dsl_parts.append(f'        <Text text="2026.11.07" color="{TEXT_MED}" fontSize="24"/>')
    dsl_parts.append(f'      </Row>')
    dsl_parts.append(f'    </Container>')

    # Card
    dsl_parts.append(f'    <Container height="400" color="{CARD_BG}" border="1 SOLID {BORDER}" borderRadius="16" padding="(32,32)">')
    dsl_parts.append(f'      <Column crossAxisAlignment="START">')
    dsl_parts.append(f'        <Text text="{cid}" color="{TEXT_MED}" fontSize="20"/>')
    dsl_parts.append(f'        <Text text="{title}" color="{TEXT_DARK}" fontSize="40" fontStyle="BOLD"/>')
    dsl_parts.append(f'        <Text text="讲者：{speaker}" color="{TEXT_MED}" fontSize="24"/>')
    dsl_parts.append(f'        <Text text="时间：{time}" color="{TEXT_MED}" fontSize="24"/>')
    if status == "取消":
        dsl_parts.append(f'        <Text text="本场取消" color="{color}" fontSize="24" fontStyle="BOLD"/>')
    dsl_parts.append(f'      </Column>')
    dsl_parts.append(f'    </Container>')

    # Status badge
    dsl_parts.append(f'    <Container height="80" padding="({MARGIN},{MARGIN})">')
    dsl_parts.append(f'      <Row>')
    dsl_parts.append(f'        <Container width="120" height="40" color="{color}" borderRadius="20" padding="(8,16)">')
    dsl_parts.append(f'          <Text text="{status}" color="#FFFFFF" fontSize="20" fontStyle="BOLD"/>')
    dsl_parts.append(f'        </Container>')
    dsl_parts.append(f'      </Row>')
    dsl_parts.append(f'    </Container>')

    dsl_parts.append('  </Column>')
    dsl_parts.append('</Snapshot>')

    dsl = '\n'.join(dsl_parts)
    with open(f'tmp/20261011-suite/A14/card-{cid}.snapshot', 'w', encoding='utf-8') as f:
        f.write(dsl)

print(f'Generated {len(cards)} card DSLs')

# Save batch audit
audit = {
    "schema_version": 1,
    "task_id": "A14",
    "path_base": "output_dir",
    "cards": [{"id": c["id"], "title": c["title"], "speaker": c["speaker"], "status": c["status"], "time": c["time"]} for c in cards]
}
with open(output_dir / 'batch-audit.json', 'w', encoding='utf-8') as f:
    json.dump(audit, f, ensure_ascii=False, indent=2)
print('Saved batch-audit.json')
