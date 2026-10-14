import json, math
from pathlib import Path

with open('tasks/A09-transform-atlas/inputs/stamp.json', 'r', encoding='utf-8') as f:
    stamp = json.load(f)
with open('tasks/A09-transform-atlas/inputs/transforms.json', 'r', encoding='utf-8') as f:
    transforms = json.load(f)

def mat_mul(A, B):
    result = [0] * 16
    for col in range(4):
        for row in range(4):
            result[col*4 + row] = sum(A[k*4 + row] * B[col*4 + k] for k in range(4))
    return result

def translate(tx, ty):
    return [1,0,0,0, 0,1,0,0, 0,0,1,0, tx,ty,0,1]

def rotate(deg):
    rad = math.radians(deg)
    c, s = round(math.cos(rad), 3), round(math.sin(rad), 3)
    return [c,-s,0,0, s,c,0,0, 0,0,1,0, 0,0,0,1]

def mirror_h():
    return [-1,0,0,0, 0,1,0,0, 0,0,1,0, 120,0,0,1]

def mirror_v():
    return [1,0,0,0, 0,-1,0,0, 0,0,1,0, 0,120,0,1]

def scale(sx, sy):
    return [sx,0,0,0, 0,sy,0,0, 0,0,1,0, 60-60*sx, 60-60*sy, 0,1]

def pivot_transform(op, val):
    if op == 'rotate_clockwise_deg':
        R = rotate(val)
        T1 = translate(-60, -60)
        T2 = translate(60, 60)
        return mat_mul(T2, mat_mul(R, T1))
    elif op == 'mirror_horizontal':
        return mirror_h()
    elif op == 'mirror_vertical':
        return mirror_v()
    elif op == 'scale_uniform':
        return scale(val, val)
    elif op == 'scale_xy':
        return scale(val[0], val[1])
    return [1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1]

def compose_matrix(operations):
    M = [1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1]
    for op, val in operations:
        M_op = pivot_transform(op, val)
        M = mat_mul(M_op, M)
    return M

def transform_point(M, x, y):
    tx = M[0]*x + M[4]*y + M[12]
    ty = M[1]*x + M[5]*y + M[13]
    return (round(tx, 1), round(ty, 1))

def transform_rect(M, xywh):
    x, y, w, h = xywh
    corners = [(x, y), (x+w, y), (x, y+h), (x+w, y+h)]
    transformed = [transform_point(M, cx, cy) for cx, cy in corners]
    xs = [p[0] for p in transformed]
    ys = [p[1] for p in transformed]
    return (min(xs), min(ys), max(xs)-min(xs), max(ys)-min(ys))

# Generate DSL
dsl_parts = []
dsl_parts.append('<Snapshot type="png" background="#F8FAFC">')
dsl_parts.append('  <Column mainAxisSize="MAX" height="1200" width="1600">')

# Title
dsl_parts.append('    <Container height="50" padding="(0,24)">')
dsl_parts.append('      <Text text="十二个非对称图形变换标本" color="#1E293B" fontSize="24" fontStyle="BOLD"/>')
dsl_parts.append('    </Container>')

# Grid: 4 columns x 3 rows, each cell 300x250, gap 32
cell_w, cell_h, gap = 300, 250, 32
start_x = (1600 - (4*cell_w + 3*gap)) // 2
start_y = 70

for idx, t in enumerate(transforms):
    row = idx // 4
    col = idx % 4
    x = start_x + col * (cell_w + gap)
    y = start_y + row * (cell_h + gap)
    
    M = compose_matrix(t['operations'])
    matrix_str = ','.join(str(round(v, 3)) for v in M)
    
    # Transform stamp elements
    rects = []
    for r in stamp['rectangles']:
        new_xywh = transform_rect(M, r['xywh'])
        rects.append((new_xywh, r['color']))
    dot_center = transform_point(M, stamp['dot']['center'][0], stamp['dot']['center'][1])
    
    dsl_parts.append(f'    <Positioned left="{x}" top="{y}" width="{cell_w}" height="{cell_h}">')
    dsl_parts.append(f'      <Container width="{cell_w}" height="{cell_h}" color="#FFFFFF" border="1 SOLID #E2E8F0" borderRadius="8">')
    dsl_parts.append(f'        <Stack>')
    dsl_parts.append(f'          <Positioned left="0" top="0" width="{cell_w}" height="40">')
    dsl_parts.append(f'            <Column crossAxisAlignment="START">')
    dsl_parts.append(f'              <Text text="{t["id"]}" color="#1E293B" fontSize="20" fontStyle="BOLD"/>')
    dsl_parts.append(f'              <Text text="({t["operations"][0][0][:12]})" color="#64748B" fontSize="14"/>')
    dsl_parts.append(f'            </Column>')
    dsl_parts.append(f'          </Positioned>')
    for (nx, ny, nw, nh), color in rects:
        dsl_parts.append(f'          <Positioned left="{90+nx}" top="{60+ny}" width="{nw}" height="{nh}">')
        dsl_parts.append(f'            <Container color="{color}"/>')
        dsl_parts.append(f'          </Positioned>')
    dsl_parts.append(f'          <Positioned left="{90+dot_center[0]-8}" top="{60+dot_center[1]-8}" width="16" height="16">')
    dsl_parts.append(f'            <Container color="{stamp["dot"]["color"]}" borderRadius="8"/>')
    dsl_parts.append(f'          </Positioned>')
    dsl_parts.append(f'        </Stack>')
    dsl_parts.append(f'      </Container>')
    dsl_parts.append(f'    </Positioned>')

dsl_parts.append('  </Column>')
dsl_parts.append('</Snapshot>')

dsl = '\n'.join(dsl_parts)
with open('tmp/20261011-suite/A09/transform-atlas.snapshot', 'w', encoding='utf-8') as f:
    f.write(dsl)
print(f'Generated DSL: {len(dsl)} chars')

# Generate geometry audit
audit = {
    "schema_version": 1,
    "task_id": "A09",
    "path_base": "output_dir",
    "stamp": stamp,
    "transforms": []
}

for t in transforms:
    M = compose_matrix(t['operations'])
    matrix_str = ','.join(str(round(v, 3)) for v in M)
    rects = []
    for r in stamp['rectangles']:
        new_xywh = transform_rect(M, r['xywh'])
        rects.append({"xywh": list(new_xywh), "color": r['color']})
    dot_center = transform_point(M, stamp['dot']['center'][0], stamp['dot']['center'][1])
    all_corners = []
    for r in rects:
        x, y, w, h = r['xywh']
        all_corners.extend([(x, y), (x+w, y), (x, y+h), (x+w, y+h)])
    bbox = (min(c[0] for c in all_corners), min(c[1] for c in all_corners),
            max(c[0] for c in all_corners), max(c[1] for c in all_corners))
    audit["transforms"].append({
        "id": t["id"],
        "matrix": matrix_str,
        "rectangles": rects,
        "dot_center": list(dot_center),
        "bounding_box": list(bbox)
    })

output_dir = Path('outputs/20261011-suite/A09')
output_dir.mkdir(parents=True, exist_ok=True)
with open(output_dir / 'geometry-audit.json', 'w', encoding='utf-8') as f:
    json.dump(audit, f, ensure_ascii=False, indent=2)
print('Saved geometry-audit.json')
