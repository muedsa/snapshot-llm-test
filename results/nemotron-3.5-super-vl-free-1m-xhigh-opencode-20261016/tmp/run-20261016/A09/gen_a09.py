import math, json

# ---------------- Stamp definition (from inputs/stamp.json) ----------------
STAMP_W, STAMP_H = 120, 120
PIVOT = (60.0, 60.0)
RECTS = [
    {"xywh": (8, 8, 28, 92),   "color": "#E54B4B"},
    {"xywh": (36, 72, 68, 28),  "color": "#2364DB"},
    {"xywh": (64, 8, 40, 28),   "color": "#EAB53B"},
]
DOT = {"center": (91.0, 49.0), "radius": 8, "color": "#111111"}

OP_NAMES = {
    "T01": "旋转0°",
    "T02": "顺时针旋转90°",
    "T03": "顺时针旋转180°",
    "T04": "顺时针旋转270°",
    "T05": "左右镜像",
    "T06": "上下镜像",
    "T07": "镜像水平→旋转90°",
    "T08": "旋转90°→镜像水平",
    "T09": "等比缩放0.75",
    "T10": "非等比缩放(1.25,0.75)",
    "T11": "顺时针旋转30°",
    "T12": "镜像竖直→旋转30°",
}

TRANSFORMS = [
    {"id": "T01", "ops": [("r", 0.0)]},
    {"id": "T02", "ops": [("r", 90.0)]},
    {"id": "T03", "ops": [("r", 180.0)]},
    {"id": "T04", "ops": [("r", 270.0)]},
    {"id": "T05", "ops": [("mx", None)]},
    {"id": "T06", "ops": [("my", None)]},
    {"id": "T07", "ops": [("mx", None), ("r", 90.0)]},
    {"id": "T08", "ops": [("r", 90.0), ("mx", None)]},
    {"id": "T09", "ops": [("s", 0.75)]},
    {"id": "T10", "ops": [("sxy", (1.25, 0.75))]},
    {"id": "T11", "ops": [("r", 30.0)]},
    {"id": "T12", "ops": [("my", None), ("r", 30.0)]},
]

# 2x2 matrices operating on column vectors [x, y] in screen coords (x right, y down)
def rot_cw(deg):
    th = math.radians(deg)
    c, s = math.cos(th), math.sin(th)
    return ((c, s), (-s, c))          # clockwise visual rotation in screen coords

def mx():
    return ((-1.0, 0.0), (0.0, 1.0))

def my():
    return ((1.0, 0.0), (0.0, -1.0))

def scale(s):
    return ((s, 0.0), (0.0, s))

def scale_xy(sx, sy):
    return ((sx, 0.0), (0.0, sy))

def mat_mul(A, B):
    return ((A[0][0]*B[0][0] + A[0][1]*B[1][0], A[0][0]*B[0][1] + A[0][1]*B[1][1]),
            (A[1][0]*B[0][0] + A[1][1]*B[1][0], A[1][0]*B[0][1] + A[1][1]*B[1][1]))

def compose(ops):
    M = ((1.0, 0.0), (0.0, 1.0))   # identity
    for kind, val in ops:
        if kind == "r":
            op = rot_cw(val)
        elif kind == "mx":
            op = mx()
        elif kind == "my":
            op = my()
        elif kind == "s":
            op = scale(val)
        elif kind == "sxy":
            op = scale_xy(*val)
        M = mat_mul(op, M)
    return M

def mat_flat(M):
    # column-major flat 16 values: (c00,c10,c20,c30, c01,c11,c21,c31, c02,c12,c22,c32, c03,c13,c23,c33)
    a, b = M[0][0], M[1][0]
    c, d = M[0][1], M[1][1]
    return (a, b, 0.0, 0.0, c, d, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0)

def apply_pt(M, p):
    x, y = p
    return (M[0][0]*x + M[0][1]*y, M[1][0]*x + M[1][1]*y)

# ---------------- Canvas geometry ----------------
W, H = 1600, 1200
CELL_W, CELL_H = 300, 250
GAP = 32
COLS, ROWS = 4, 3
grid_w = COLS * CELL_W + (COLS - 1) * GAP
grid_h = ROWS * CELL_H + (ROWS - 1) * GAP
ox = (W - grid_w) / 2.0
oy = (H - grid_h) / 2.0

def cell_origin(c, r):
    return (ox + c * (CELL_W + GAP), oy + r * (CELL_H + GAP))

def cell_center(c, r):
    x0, y0 = cell_origin(c, r)
    return (x0 + CELL_W / 2.0, y0 + CELL_H / 2.0)

# ---------------- Build DSL ----------------
el = []
el.append('<Snapshot background="#FFFFFF" type="png">')
el.append(f'  <SizedBox width="{W}" height="{H}">')
el.append('    <Stack alignment="TOP_LEFT" clipBehavior="NONE">')

# Title
el.append('      <Positioned left="40" top="24">')
el.append('        <Text color="#0F172A" fontSize="28" fontStyle="BOLD" fontFamily="Noto Sans CJK SC,Inter">变换图谱 · 十二个非对称图形变换标本</Text>')
el.append('      </Positioned>')
el.append('      <Positioned left="40" top="58" width="1000">')
el.append('        <Text color="#475569" fontSize="20" fontFamily="Noto Sans CJK SC,Inter" softWrap="true">每格300×250，格间32，整体居中；所有主体由Transform.matrix按列表顺序围绕局部(60,60)变换，圆点随同变换，不裁切。</Text>')
el.append('      </Positioned>')

cell_fills = ["#FFFFFF", "#F8FAFC"]
for idx, spec in enumerate(TRANSFORMS):
    tid = spec["id"]
    c = idx % COLS
    r = idx // COLS
    x0, y0 = cell_origin(c, r)
    cx, cy = cell_center(c, r)
    M = compose(spec["ops"])
    flat = mat_flat(M)
    flat_s = ",".join(f"{v:.6f}" for v in flat)

    # cell
    el.append(f'      <Positioned left="{x0:.1f}" top="{y0:.1f}" width="{CELL_W:.1f}" height="{CELL_H:.1f}">')
    el.append('        <Container color="#FFFFFF" border="1 SOLID #E5E7EB">')
    el.append('          <Stack>')
    # cell frame fills
    el.append(f'            <Positioned left="0" top="0" width="{CELL_W:.1f}" height="{CELL_H:.1f}"><Container color="#FFFFFF" border="1 SOLID #CBD5E1" borderRadius="8"/></Positioned>')
    # cell number + op name
    el.append(f'            <Positioned left="12" top="10" width="260">')
    el.append(f'              <Text color="#0F172A" fontSize="22" fontStyle="BOLD" fontFamily="Noto Sans CJK SC,Inter">{tid}</Text>')
    el.append(f'            </Positioned>')
    el.append(f'            <Positioned left="12" top="38" width="260">')
    el.append(f'              <Text color="#475569" fontSize="20" fontFamily="Noto Sans CJK SC,Inter">{OP_NAMES[tid]}</Text>')
    el.append(f'            </Positioned>')
    # stamp box centered in cell
    sbx, sby = cx - 60.0, cy - 60.0
    el.append(f'            <Positioned left="{sbx:.1f}" top="{sby:.1f}" width="120" height="120">')
    el.append(f'              <Transform matrix="({flat_s})" origin="(60,60)">')
    el.append('                <Stack alignment="TOP_LEFT">')
    # rectangles
    for i, rc in enumerate(RECTS):
        x, y, wd, ht = rc["xywh"]
        el.append(f'                  <Positioned left="{float(x):.1f}" top="{float(y):.1f}" width="{float(wd):.1f}" height="{float(ht):.1f}">')
        el.append(f'                    <Container color="{rc["color"]}"/>')
        el.append(f'                  </Positioned>')
    # dot
    dx, dy = DOT["center"]
    dr = DOT["radius"] * 2
    el.append(f'                  <Positioned left="{dx - DOT["radius"]:.1f}" top="{dy - DOT["radius"]:.1f}" width="{dr:.1f}" height="{dr:.1f}">')
    el.append(f'                    <Container color="{DOT["color"]}" borderRadius="{DOT["radius"]:.1f}"/>')
    el.append(f'                  </Positioned>')
    el.append('                </Stack>')
    el.append(f'              </Transform>')
    el.append(f'            </Positioned>')
    # guide lines: vertical at local stamp x = 0,30,60,90,120 mapped into cell coords
    for gx in (0, 30, 60, 90, 120):
        gx_abs = sbx + gx
        el.append(f'            <Positioned left="{gx_abs:.1f}" top="{y0+4:.1f}" width="1" height="{CELL_H-8:.1f}"><Container color="#E2E8F0"/></Positioned>')
        el.append(f'            <Positioned left="{gx_abs-14:.1f}" top="{y0-22:.1f}" width="28">')
        el.append(f'              <Text textAlign="CENTER" color="#64748B" fontSize="20" fontFamily="Noto Sans CJK SC,Inter">{gx}</Text>')
        el.append(f'            </Positioned>')
    # horizontal guide lines at local y = 0,30,60,90,120
    for gy in (0, 30, 60, 90, 120):
        gy_abs = sby + gy
        el.append(f'            <Positioned left="{x0+4:.1f}" top="{gy_abs:.1f}" width="{CELL_W-8:.1f}" height="1"><Container color="#E2E8F0"/></Positioned>')
        el.append(f'            <Positioned left="{x0-28:.1f}" top="{gy_abs-10:.1f}" width="24">')
        el.append(f'              <Text textAlign="RIGHT" color="#64748B" fontSize="20" fontFamily="Noto Sans CJK SC,Inter">{gy}</Text>')
        el.append(f'            </Positioned>')
    el.append('          </Stack>')
    el.append('        </Container>')
    el.append(f'      </Positioned>')

el.append('    </Stack>')
el.append('  </SizedBox>')
el.append('</Snapshot>')

dsl = "\n".join(el)
open("tmp/run-20261016/A09/transform-atlas.v1.snapshot", "w", encoding="utf-8").write(dsl)
print("DSL written, chars:", len(dsl))

# ---------------- geometry-audit.json ----------------
audit_specimens = []
for spec in TRANSFORMS:
    tid = spec["id"]
    M = compose(spec["ops"])
    # corners of each rectangle (local stamp coords), transformed
    rect_audit = []
    for rc in RECTS:
        x, y, wd, ht = rc["xywh"]
        corners = [(x, y), (x + wd, y), (x + wd, y + ht), (x, y + ht)]
        tc = [apply_pt(M, (px - PIVOT[0], py - PIVOT[1])) for px, py in corners]
        # add cell center translation
        tc = [(px + PIVOT[0], py + PIVOT[1]) for px, py in tc]  # local stamp coords after transform, relative to stamp origin
        rect_audit.append({
            "color": rc["color"],
            "xywh": list(rc["xywh"]),
            "corners_local": [[round(px, 3), round(py, 3)] for px, py in tc],
        })
    # dot center
    dtx, dty = apply_pt(M, (DOT["center"][0] - PIVOT[0], DOT["center"][1] - PIVOT[1]))
    dtx += PIVOT[0]; dty += PIVOT[1]
    dot_audit = {"center_local": [round(dtx, 3), round(dty, 3)], "radius": DOT["radius"], "color": DOT["color"]}
    # bounding box of all transformed geometry (local stamp coords)
    all_pts = []
    for rc in RECTS:
        x, y, wd, ht = rc["xywh"]
        for px, py in [(x, y), (x + wd, y), (x + wd, y + ht), (x, y + ht)]:
            all_pts.append((px - PIVOT[0], py - PIVOT[1]))
    dcx, dcy = DOT["center"][0] - PIVOT[0], DOT["center"][1] - PIVOT[1]
    r = DOT["radius"]
    all_pts.append((dcx - r, dcy - r))
    all_pts.append((dcx + r, dcy + r))
    tpts = [apply_pt(M, p) for p in all_pts]
    xs = [p[0] for p in tpts]; ys = [p[1] for p in tpts]
    bbox_local = [round(min(xs), 3), round(min(ys), 3), round(max(xs), 3), round(max(ys), 3)]
    audit_specimens.append({
        "id": tid,
        "name": OP_NAMES[tid],
        "matrix_flat": [round(v, 6) for v in flat],
        "pivot_local": [60.0, 60.0],
        "rectangles": rect_audit,
        "dot": dot_audit,
        "bounding_box_local": bbox_local,
    })

geometry = {
    "schema_version": 1,
    "task_id": "A09",
    "path_base": "output_dir",
    "source": {"stamp": "inputs/stamp.json", "transforms": "inputs/transforms.json"},
    "canvas": {"width": W, "height": H},
    "cell": {"width": CELL_W, "height": CELL_H, "gap": GAP, "origin_px": [ox, oy]},
    "pivot_local": [60.0, 60.0],
    "units": "pixels, image coordinate system (x right, y down); clockwise rotation per image direction",
    "specimens": audit_specimens,
    "check_method": "每矩形四角、圆点中心按 M_full = T(cell_center)·M_composite·T(-pivot) 映射到画布，与最终图对应位置核对，误差允许±1.5像素（反走样边缘例外）。外接框取所有变换后几何的最小/最大 x、y。matrix 为列主序 4×4（16 值），以 pivot (60,60) 为局部原点，操作按 transforms.json 列表顺序左乘合成。",
}
open("tmp/run-20261016/A09/geometry-audit.v1.json", "w", encoding="utf-8").write(json.dumps(geometry, ensure_ascii=False, indent=2))
print("geometry-audit draft written")
for s in audit_specimens:
    print(s["id"], s["matrix_flat"])
