import json
from pathlib import Path

with open('tasks/A20-dense-annotation/inputs/markers.json', 'r', encoding='utf-8') as f:
    markers = json.load(f)

W, H = 1600, 1100
FONT = "Noto Sans CJK SC"
BG = "#F8FAFC"
CARD_BG = "#FFFFFF"
BORDER = "#E2E8F0"
TEXT_DARK = "#1E293B"
TEXT_MED = "#64748B"
BLUE = "#3B82F6"

# Map area
MAP_X, MAP_Y = 280, 160
MAP_W, MAP_H = 1040, 760

def to_pixel(x, y):
    px = MAP_X + 10.4 * x
    py = 920 - 7.6 * y
    return px, py

dsl_parts = []
dsl_parts.append(f'<Snapshot type="png" background="{BG}">')
dsl_parts.append(f'  <Column mainAxisSize="MAX" height="{H}" width="{W}">')

# Title
dsl_parts.append(f'    <Container height="60" padding="(0,24)">')
dsl_parts.append(f'      <Text text="二十四密集点标注地图" color="{TEXT_DARK}" fontSize="24" fontStyle="BOLD"/>')
dsl_parts.append(f'    </Container>')

# Map area with markers
dsl_parts.append(f'    <Container width="{MAP_W}" height="{MAP_H}" color="{CARD_BG}" border="1 SOLID {BORDER}" borderRadius="8" padding="(8,8)">')
dsl_parts.append(f'      <Column crossAxisAlignment="START">')

for m in markers:
    px, py = to_pixel(m['x'], m['y'])
    mid = m['id']
    name = m['name']
    value = m['value']
    
    dsl_parts.append(f'        <Container width="120" height="60" color="{CARD_BG}" border="1 SOLID {BORDER}" borderRadius="4" padding="(4,4)">')
    dsl_parts.append(f'          <Column crossAxisAlignment="START">')
    dsl_parts.append(f'            <Text text="{mid} {name}" color="{TEXT_DARK}" fontSize="20"/>')
    dsl_parts.append(f'            <Text text="指数：{value}" color="{TEXT_MED}" fontSize="18"/>')
    dsl_parts.append(f'          </Column>')
    dsl_parts.append(f'        </Container>')
    dsl_parts.append(f'        <SizedBox height="4"/>')

dsl_parts.append(f'      </Column>')
dsl_parts.append(f'    </Container>')

# Axis labels
dsl_parts.append(f'    <Container height="40" padding="(0,24)">')
dsl_parts.append(f'      <Text text="X轴：0-100  Y轴：0-100  单位：指数" color="{TEXT_MED}" fontSize="16"/>')
dsl_parts.append(f'    </Container>')

dsl_parts.append('  </Column>')
dsl_parts.append('</Snapshot>')

dsl = '\n'.join(dsl_parts)
with open('tmp/20261011-suite/A20/annotated-map.snapshot', 'w', encoding='utf-8') as f:
    f.write(dsl)
print(f'Generated DSL: {len(dsl)} chars')

# Save label-layout.json
label_layout = {
    "schema_version": 1,
    "task_id": "A20",
    "path_base": "output_dir",
    "markers": [{"id": m["id"], "name": m["name"], "x": m["x"], "y": m["y"], "value": m["value"], "pixel": list(to_pixel(m["x"], m["y"]))} for m in markers]
}

output_dir = Path('outputs/20261011-suite/A20')
output_dir.mkdir(parents=True, exist_ok=True)
with open(output_dir / 'label-layout.json', 'w', encoding='utf-8') as f:
    json.dump(label_layout, f, ensure_ascii=False, indent=2)
print('Saved label-layout.json')
