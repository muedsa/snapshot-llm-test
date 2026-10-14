import json, random
from pathlib import Path

random.seed(42)

# Grid: 8x8 = 64 objects
# Colors: blue, orange, green, purple
# Shapes: circle, square, ring, rounded_square
# Sizes: 48, 64, 80

COLORS = [
    ("blue", "#3B82F6"),
    ("orange", "#F59E0B"),
    ("green", "#10B981"),
    ("purple", "#8B5CF6"),
]
SHAPES = ["circle", "square", "ring", "rounded_square"]
SIZES = [48, 64, 80]

# Generate all 16 color-shape combinations
combinations = [(c, s) for c in range(4) for s in range(4)]
random.shuffle(combinations)

# Assign sizes: each color and each shape must have all 3 sizes
# Use Latin square approach: 4 colors x 4 shapes, assign sizes such that
# each row (color) and column (shape) has all 3 sizes
# With 4 rows/columns and 3 sizes, one size appears twice per row/column

size_assignment = {}
for c in range(4):
    for s in range(4):
        # Latin square pattern: (c + s) % 3 gives sizes 48, 64, 80
        size_assignment[(c, s)] = SIZES[(c + s) % 3]

# Verify constraints
for c in range(4):
    sizes_for_c = [size_assignment[(c, s)] for s in range(4)]
    assert len(set(sizes_for_c)) == 3, f"Color {c} missing sizes: {sizes_for_c}"

for s in range(4):
    sizes_for_s = [size_assignment[(c, s)] for c in range(4)]
    assert len(set(sizes_for_s)) == 3, f"Shape {s} missing sizes: {sizes_for_s}"

# Create 64 objects: each combination appears 4 times
objects = []
for combo_idx, (c, s) in enumerate(combinations):
    for _ in range(4):
        objects.append({
            "color_idx": c,
            "color_name": COLORS[c][0],
            "color": COLORS[c][1],
            "shape": s,
            "size": size_assignment[(c, s)]
        })

# Shuffle and assign to grid
random.shuffle(objects)

# Verify row constraints: each row has at least 3 colors and 3 shapes
grid = []
for row in range(8):
    row_objects = objects[row*8:(row+1)*8]
    colors_in_row = set(o["color_idx"] for o in row_objects)
    shapes_in_row = set(o["shape"] for o in row_objects)
    if len(colors_in_row) < 3 or len(shapes_in_row) < 3:
        # Swap with another row to fix
        for other_row in range(row+1, 8):
            other_objects = objects[other_row*8:(other_row+1)*8]
            other_colors = set(o["color_idx"] for o in other_objects)
            other_shapes = set(o["shape"] for o in other_objects)
            if len(other_colors) >= 3 and len(other_shapes) >= 3:
                # Find a swap candidate
                for i, o1 in enumerate(row_objects):
                    for j, o2 in enumerate(other_objects):
                        new_row = row_objects[:i] + [o2] + row_objects[i+1:]
                        new_other = other_objects[:j] + [o1] + other_objects[j+1:]
                        if (len(set(o["color_idx"] for o in new_row)) >= 3 and
                            len(set(o["shape"] for o in new_row)) >= 3 and
                            len(set(o["color_idx"] for o in new_other)) >= 3 and
                            len(set(o["shape"] for o in new_other)) >= 3):
                            objects[row*8:(row+1)*8] = new_row
                            objects[other_row*8:(other_row+1)*8] = new_other
                            break
                    else:
                        continue
                    break
                break

grid = objects

# Generate grid DSL
W, H = 1600, 1600
CELL = 200
FONT = "Noto Sans CJK SC"
BG = "#F8FAFC"

dsl_parts = []
dsl_parts.append(f'<Snapshot type="png" background="{BG}">')
dsl_parts.append(f'  <Column mainAxisSize="MAX" height="{H}" width="{W}">')

for row in range(8):
    dsl_parts.append(f'    <Row>')
    for col in range(8):
        i = row * 8 + col
        obj = grid[i]
        obj_id = f"G{i+1:02d}"
        
        dsl_parts.append(f'      <Container width="{CELL}" height="{CELL}" padding="(4,4)">')
        dsl_parts.append(f'        <Column crossAxisAlignment="CENTER">')
        dsl_parts.append(f'          <Text text="{obj_id}" color="#1E293B" fontSize="16"/>')
        
        size = obj["size"]
        if obj["shape"] == 0:  # circle
            dsl_parts.append(f'          <Container width="{size}" height="{size}" color="{obj["color"]}" borderRadius="{size//2}"/>')
        elif obj["shape"] == 1:  # square
            dsl_parts.append(f'          <Container width="{size}" height="{size}" color="{obj["color"]}"/>')
        elif obj["shape"] == 2:  # ring
            dsl_parts.append(f'          <Container width="{size}" height="{size}" color="{obj["color"]}" borderRadius="{size//2}">')
            dsl_parts.append(f'            <Container width="{size//2}" height="{size//2}" color="{BG}" borderRadius="{size//4}"/>')
            dsl_parts.append(f'          </Container>')
        else:  # rounded_square
            dsl_parts.append(f'          <Container width="{size}" height="{size}" color="{obj["color"]}" borderRadius="{size//4}"/>')
        
        dsl_parts.append(f'        </Column>')
        dsl_parts.append(f'      </Container>')
    dsl_parts.append(f'    </Row>')

dsl_parts.append('  </Column>')
dsl_parts.append('</Snapshot>')

dsl = '\n'.join(dsl_parts)
with open('tmp/20261011-suite/A19/grid-scene.snapshot', 'w', encoding='utf-8') as f:
    f.write(dsl)
print(f'Grid DSL: {len(dsl)} chars')

# Generate occlusion DSLs
# Two versions: A has a blue circle behind a gray rectangle, B has an orange square
# Both have identical visible content

occl_dsl_a = '''<Snapshot type="png" width="800" height="800" background="#F1F5F9">
  <Column mainAxisSize="MAX" height="800" width="800">
    <Container width="800" height="800">
      <Stack>
        <!-- Hidden content A: blue circle -->
        <Positioned left="300" top="300" width="200" height="200">
          <Container color="#3B82F6" borderRadius="100"/>
        </Positioned>
        <!-- Occluder: gray rectangle -->
        <Positioned left="250" top="250" width="300" height="300">
          <Container color="#64748B" borderRadius="8"/>
        </Positioned>
        <!-- Visible foreground: red triangle shape -->
        <Positioned left="350" top="350" width="100" height="100">
          <Container color="#EF4444" borderRadius="4"/>
        </Positioned>
      </Stack>
    </Container>
  </Column>
</Snapshot>'''

occl_dsl_b = '''<Snapshot type="png" width="800" height="800" background="#F1F5F9">
  <Column mainAxisSize="MAX" height="800" width="800">
    <Container width="800" height="800">
      <Stack>
        <!-- Hidden content B: orange square -->
        <Positioned left="300" top="300" width="200" height="200">
          <Container color="#F59E0B" borderRadius="8"/>
        </Positioned>
        <!-- Occluder: gray rectangle (same as A) -->
        <Positioned left="250" top="250" width="300" height="300">
          <Container color="#64748B" borderRadius="8"/>
        </Positioned>
        <!-- Visible foreground: red triangle shape (same as A) -->
        <Positioned left="350" top="350" width="100" height="100">
          <Container color="#EF4444" borderRadius="4"/>
        </Positioned>
      </Stack>
    </Container>
  </Column>
</Snapshot>'''

with open('tmp/20261011-suite/A19/occlusion.snapshot', 'w', encoding='utf-8') as f:
    f.write(occl_dsl_a)
with open('tmp/20261011-suite/A19/occlusion-alternative.snapshot', 'w', encoding='utf-8') as f:
    f.write(occl_dsl_b)
print("Generated occlusion DSLs")

# Save scene-data.json
scene_data = {
    "schema_version": 1,
    "task_id": "A19",
    "path_base": "output_dir",
    "seed": 42,
    "grid_size": [8, 8],
    "objects": [{"id": f"G{i+1:02d}", "color": o["color_name"], "shape": SHAPES[o["shape"]], "size": o["size"]} for i, o in enumerate(grid)]
}

output_dir = Path('outputs/20261011-suite/A19')
output_dir.mkdir(parents=True, exist_ok=True)
with open(output_dir / 'scene-data.json', 'w', encoding='utf-8') as f:
    json.dump(scene_data, f, ensure_ascii=False, indent=2)
print('Saved scene-data.json')
