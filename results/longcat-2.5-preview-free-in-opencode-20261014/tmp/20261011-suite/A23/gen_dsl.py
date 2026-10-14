import math, json
from pathlib import Path

W, H = 600, 600
FONT = "Noto Sans CJK.sc"
BG = "transparent"

# 12 units converging from scattered positions to form a triangle
# Each unit: 40x40 square with different colors
UNIT_COLORS = [
    "#3B82F6", "#10B981", "#F59E0B", "#8B5CF6",
    "#EF4444", "#06B6D4", "#84CC16", "#F97316",
    "#6366F1", "#14B8A6", "#EAB308", "#A855F7"
]

# Final positions: triangle formation (3 rows: 1, 2, 3, 4, 2)
final_positions = [
    (280, 100),
    (240, 160), (320, 160),
    (200, 220), (280, 220), (360, 220),
    (160, 280), (240, 280), (320, 280), (400, 280),
    (240, 340), (320, 340)
]

# Initial positions: scattered around edges
initial_positions = [
    (50, 50), (550, 50), (50, 550), (550, 550),
    (300, 30), (300, 570), (30, 300), (570, 300),
    (100, 100), (500, 100), (100, 500), (500, 500)
]

def lerp(a, b, t):
    return a + (b - a) * t

output_dir = Path('outputs/20261011-suite/A23')
output_dir.mkdir(parents=True, exist_ok=True)

# Generate 6 frames
frames = []
for frame_idx in range(6):
    t = frame_idx / 5  # 0, 0.2, 0.4, 0.6, 0.8, 1.0

    dsl_parts = []
    dsl_parts.append(f'<Snapshot type="png" width="{W}" height="{H}" background="{BG}">')
    dsl_parts.append(f'  <Column mainAxisSize="MAX" height="{H}" width="{W}">')
    dsl_parts.append(f'    <Container width="{W}" height="{H}">')
    dsl_parts.append(f'      <Column crossAxisAlignment="CENTER">')

    for i in range(12):
        x = lerp(initial_positions[i][0], final_positions[i][0], t)
        y = lerp(initial_positions[i][1], final_positions[i][1], t)
        color = UNIT_COLORS[i]
        dsl_parts.append(f'        <Container width="40" height="40" color="{color}" borderRadius="4"/>')

    dsl_parts.append(f'      </Column>')
    dsl_parts.append(f'    </Container>')
    dsl_parts.append(f'  </Column>')
    dsl_parts.append(f'</Snapshot>')

    dsl = '\n'.join(dsl_parts)
    with open(f'tmp/20261011-suite/A23/frame-{frame_idx+1:02d}.snapshot', 'w', encoding='utf-8') as f:
        f.write(dsl)

    frames.append({
        "frame": frame_idx + 1,
        "time_ms": frame_idx * 250,
        "file": f"frame-{frame_idx+1:02d}.png"
    })

print("Generated 6 frame DSLs")

# Generate cover
cover_dsl = f'''<Snapshot type="png" width="1200" height="800" background="#0F172A">
  <Column mainAxisSize="MAX" height="800" width="1200">
    <Container height="200" padding="(40,40)">
      <Text text="结构汇聚成图像" color="#FFFFFF" fontSize="64" fontStyle="BOLD"/>
      <Text text="从结构到画面" color="#CBD5E1" fontSize="32"/>
    </Container>
    <Container height="400" padding="(40,40)">
      <Row mainAxisAlignment="CENTER">
        <Container width="200" height="200" color="#3B82F6" borderRadius="16"/>
        <SizedBox width="20"/>
        <Container width="200" height="200" color="#10B981" borderRadius="16"/>
        <SizedBox width="20"/>
        <Container width="200" height="200" color="#F59E0B" borderRadius="16"/>
      </Row>
    </Container>
    <Container height="200" padding="(40,40)">
      <Text text="Structure / Vision 2026" color="#FFFFFF" fontSize="28"/>
    </Container>
  </Column>
</Snapshot>'''

with open('tmp/20261011-suite/A23/cover.snapshot', 'w', encoding='utf-8') as f:
    f.write(cover_dsl)
print("Generated cover DSL")

# Save timing.json
timing = {
    "schema_version": 1,
    "task_id": "A23",
    "path_base": "output_dir",
    "frame_duration_ms": 250,
    "loop": True,
    "total_frames": 6,
    "cycle_ms": 1500,
    "frames": frames
}
with open(output_dir / 'timing.json', 'w', encoding='utf-8') as f:
    json.dump(timing, f, ensure_ascii=False, indent=2)

# Save frame-data.json
frame_data = {
    "schema_version": 1,
    "task_id": "A23",
    "path_base": "output_dir",
    "units": [{"id": f"U{i+1:02d}", "color": c, "size": 40} for i, c in enumerate(UNIT_COLORS)],
    "frames": frames
}
with open(output_dir / 'frame-data.json', 'w', encoding='utf-8') as f:
    json.dump(frame_data, f, ensure_ascii=False, indent=2)

# Save limitations.md
limitations = """# A23 Limitations

- SVG: Not natively supported by Snapshot DSL. Use PNG frames instead.
- CMYK: Not supported by Snapshot DSL. Requires external conversion.
- GIF: Not natively supported. Use 6 PNG frames with timing.json.
- Animation: No native animation support. Frames are separate PNGs.
"""
with open(output_dir / 'limitations.md', 'w', encoding='utf-8') as f:
    f.write(limitations)
print("Saved timing.json, frame-data.json, and limitations.md")
