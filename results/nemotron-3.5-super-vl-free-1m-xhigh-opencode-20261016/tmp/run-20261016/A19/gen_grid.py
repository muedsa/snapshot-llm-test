import math, json

W, H = 1600, 1600
GW, GH = 8, 8
CELL_W, CELL_H = W // GW, H // GH  # 200 × 160

COLORS = ["#2563EB", "#F59E0B", "#22C55E", "#A855F7"]  # blue, orange, green, purple
SHAPES = ["circle", "square", "ring", "roundrect"]
SIZES = [48, 64, 80]

cells = []
for r in range(GH):
    for c in range(GW):
        ci = (r + c) % 4
        si = (r * 2 + c) % 4
        si_size = (r + 3*c) % 3
        cells.append({
            "id": f"G{r*GW+c+1:02d}",
            "row": r, "col": c,
            "color_idx": ci, "shape_idx": si, "size_idx": si_size
        })

objects = []
for cell in cells:
    color = COLORS[cell["color_idx"]]
    shape = SHAPES[cell["shape_idx"]]
    size = SIZES[cell["size_idx"]]
    cx = cell["col"] * CELL_W + CELL_W / 2
    cy = cell["row"] * CELL_H + CELL_H / 2
    objects.append({
        "id": cell["id"],
        "shape": shape,
        "color": color,
        "size": size,
        "cx": round(cx, 1),
        "cy": round(cy, 1),
        "row": cell["row"],
        "col": cell["col"]
    })

def shape_dsl(obj):
    x, y = obj["cx"], obj["cy"]
    color = obj["color"]
    shape = obj["shape"]
    size = obj["size"]
    r = size / 2
    if shape == "circle":
        return f'      <Positioned left="{x-r:.1f}" top="{y-r:.1f}" width="{size:.1f}" height="{size:.1f}"><Container color="{color}" borderRadius="{r:.1f}"/></Positioned>'
    elif shape == "square":
        return f'      <Positioned left="{x-size/2:.1f}" top="{y-size/2:.1f}" width="{size:.1f}" height="{size:.1f}"><Container color="{color}"/></Positioned>'
    elif shape == "ring":
        outer_r = size / 2
        inner_r = size / 4
        inner_d = inner_r * 2
        return f'''      <Positioned left="{x-outer_r:.1f}" top="{y-outer_r:.1f}" width="{size:.1f}" height="{size:.1f}"><Container color="{color}" borderRadius="{outer_r:.1f}"/></Positioned>
      <Positioned left="{x-inner_r:.1f}" top="{y-inner_r:.1f}" width="{inner_d:.1f}" height="{inner_d:.1f}"><Container color="#FFFFFF" borderRadius="{inner_r:.1f}"/></Positioned>'''
    elif shape == "roundrect":
        return f'''      <Positioned left="{x-size/2:.1f}" top="{y-size/2:.1f}" width="{size:.1f}" height="{size:.1f}">
        <Container color="{color}" borderRadius="{size/4:.1f}"/>
      </Positioned>'''
    else:
        return f'''      <Positioned left="{x-size/2:.1f}" top="{y-size/2:.1f}" width="{size:.1f}" height="{size:.1f}">
        <Container color="{color}"/></Positioned>'''

el = []
el.append('<Snapshot background="#FFFFFF" type="png">')
el.append(f'  <SizedBox width="{W}" height="{H}">')
el.append('    <Stack alignment="TOP_LEFT" clipBehavior="NONE">')
for obj in objects:
    el.append(shape_dsl(obj))
el.append('    </Stack>')
el.append('  </SizedBox>')
el.append('</Snapshot>')

dsl = "\n".join(el)
with open("tmp/run-20261016/A19/grid-scene.v1.snapshot", "w", encoding="utf-8") as f:
    f.write(dsl)
print("Grid DSL written, chars:", len(dsl))
print("Objects:", len(objects))
