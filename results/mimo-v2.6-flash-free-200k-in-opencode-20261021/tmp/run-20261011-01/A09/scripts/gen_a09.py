#!/usr/bin/env python3
"""A09 transform atlas generator + geometry-audit.json (predicted geometry).

Usage: python tmp/<run_id>/A09/scripts/gen_a09.py <suite_root> <run_id> [outdir]

Stamp ops compose in input order, each about local pivot (60,60).
Pixel coords: x right, y down; rotate_clockwise uses image orientation
L = [[cos, -sin], [sin, cos]] so (1,0) -> (0,1) at +90deg.
Each cell subject is drawn as ONE Transform.matrix (linear part, alignment
CENTER on a 240x240 box whose center == local (60,60)), never hand-placed
corners. geometry-audit.json verification[] is filled later by measure_a09.py
from the rendered PNG.
"""
import json
import math
import pathlib
import sys
from datetime import datetime

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
run_id = sys.argv[2] if len(sys.argv) > 2 else "run-20261011-01"
out_dir = pathlib.Path(sys.argv[3]) if len(sys.argv) > 3 else (root / "outputs" / run_id / "A09")
tmp_drafts = root / "tmp" / run_id / "A09" / "drafts"
tmp_drafts.mkdir(parents=True, exist_ok=True)
out_dir.mkdir(parents=True, exist_ok=True)

INP = root / "tasks" / "A09-transform-atlas" / "inputs"
stamp = json.loads((INP / "stamp.json").read_text(encoding="utf-8"))
tlist = json.loads((INP / "transforms.json").read_text(encoding="utf-8"))
assert stamp["size"] == [120, 120] and stamp["pivot"] == [60, 60]
assert len(tlist) == 12, "expected 12 transforms"

PIV = (60.0, 60.0)


def compose(A, B):
    """A after B (A o B), affine (m00,m01,m10,m11,tx,ty)."""
    a00, a01, a10, a11, atx, aty = A
    b00, b01, b10, b11, btx, bty = B
    return (a00 * b00 + a01 * b10, a00 * b01 + a01 * b11,
            a10 * b00 + a11 * b10, a10 * b01 + a11 * b11,
            a00 * btx + a01 * bty + atx,
            a10 * btx + a11 * bty + aty)


def linear_of(op):
    name, val = op[0], op[1]
    if name == "rotate_clockwise_deg":
        r = math.radians(val)
        c, s = math.cos(r), math.sin(r)
        return (c, -s, s, c), f"rotate {val}deg"
    if name == "mirror_horizontal":
        return (-1.0, 0.0, 0.0, 1.0), "mirror L/R"
    if name == "mirror_vertical":
        return (1.0, 0.0, 0.0, -1.0), "mirror T/B"
    if name == "scale_uniform":
        return (float(val), 0.0, 0.0, float(val)), f"scale {val}"
    if name == "scale_xy":
        sx, sy = float(val[0]), float(val[1])
        return (sx, 0.0, 0.0, sy), f"scale {sx}x{sy}"
    raise ValueError(f"unknown op {name}")


def about_pivot(L):
    m00, m01, m10, m11 = L
    tx = PIV[0] - (m00 * PIV[0] + m01 * PIV[1])
    ty = PIV[1] - (m10 * PIV[0] + m11 * PIV[1])
    return (m00, m01, m10, m11, tx, ty)


def compose_ops(ops):
    M = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
    labels = []
    for op in ops:
        L, lab = linear_of(op)
        M = compose(about_pivot(L), M)
        labels.append(lab)
    # all ops share the same pivot -> total must be linear about pivot
    exp_tx = PIV[0] - (M[0] * PIV[0] + M[1] * PIV[1])
    exp_ty = PIV[1] - (M[2] * PIV[0] + M[3] * PIV[1])
    assert abs(M[4] - exp_tx) < 1e-9 and abs(M[5] - exp_ty) < 1e-9, "pivot fixed point drift"
    return M, labels


def dsl_matrix(L):
    m00, m01, m10, m11 = L[0], L[1], L[2], L[3]
    return (f"({m00},{m10},0,0,{m01},{m11},0,0,0,0,1,0,0,0,0,1)")


def apply_canvas(L, pt, cx, cy):
    dx, dy = pt[0] - PIV[0], pt[1] - PIV[1]
    return [cx + L[0] * dx + L[1] * dy, cy + L[2] * dx + L[3] * dy]


# ---- sanity checks on the operation convention -------------------------------
M2, _ = compose_ops([["rotate_clockwise_deg", 90]])
assert abs(M2[0] - 0) < 1e-12 and abs(M2[3] - 0) < 1e-12
assert abs(M2[1] + 1) < 1e-12 and abs(M2[2] - 1) < 1e-12  # (1,0) -> (0,1) image-cw
M7, _ = compose_ops([["mirror_horizontal", True], ["rotate_clockwise_deg", 90]])
M8, _ = compose_ops([["rotate_clockwise_deg", 90], ["mirror_horizontal", True]])
assert M7 != M8, "T07/T08 must differ (order matters)"

# ---- layout ------------------------------------------------------------------
CW, CH = 1600, 1200
CELL_W, CELL_H, GAP = 300, 250, 32
COLS = 4
grid_w = COLS * CELL_W + (COLS - 1) * GAP
grid_h = 3 * CELL_H + 2 * GAP
X0 = (CW - grid_w) // 2          # 152
Y0 = (CH - grid_h) // 2          # 193
FONT = "Inter,Noto Sans CJK SC"
BG, CELL_BG, CELL_BD = "#0A1020", "#0F172E", "#1E293B"
CROSS, TICK, AXIS = "#2A3B5C", "#334155", "#64748B"
ACCENT = "#7DD3FC"

SHORT = {
    "rotate_clockwise_deg": lambda v: f"旋转{v:g}°",
    "mirror_horizontal": lambda v: "左右镜像",
    "mirror_vertical": lambda v: "上下镜像",
    "scale_uniform": lambda v: f"等比缩放{v:g}",
    "scale_xy": lambda v: f"缩放X{v[0]:g}×Y{v[1]:g}",
}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def f(v):
    if isinstance(v, float):
        s = f"{v:.2f}".rstrip("0").rstrip(".")
        return s if s not in ("-0", "") else "0"
    return str(v)


class DSL:
    def __init__(self):
        self.o = []

    def rect(self, x, y, w, h, color, extra=""):
        self.o.append(f'<Positioned left="{f(x)}" top="{f(y)}" width="{f(w)}" height="{f(h)}">'
                      f'<Container color="{color}"{extra} /></Positioned>')

    def box(self, x, y, w, h, inner):
        self.o.append(f'<Positioned left="{f(x)}" top="{f(y)}" width="{f(w)}" height="{f(h)}">{inner}</Positioned>')

    def text(self, x, y, s, size=22, color="#F8FAFC", weight="NORMAL", w=None, align="START"):
        wa = f' width="{f(w)}"' if w is not None else ""
        ta = f' textAlign="{align}"' if align != "START" else ""
        self.o.append(f'<Positioned left="{f(x)}" top="{f(y)}"{wa}>'
                      f'<Text fontFamily="{FONT}" fontSize="{f(size)}" color="{color}" '
                      f'fontStyle="{weight}"{ta}>{esc(s)}</Text></Positioned>')

    def seg(self, p0, p1, th, color):
        L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        if L < 0.01:
            return
        a = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
        c, s = math.cos(a), math.sin(a)
        cx, cy = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
        self.box(cx - L / 2, cy - th / 2, L, th,
                 f'<Transform matrix="({f(c)},{f(s)},0,0,{f(-s)},{f(c)},0,0,0,0,1,0,0,0,0,1)" '
                 f'alignment="CENTER"><Container height="{f(th)}" color="{color}" /></Transform>')

    def circle(self, cx, cy, d, fill):
        self.box(cx - d / 2, cy - d / 2, d, d,
                 f'<Container width="{f(d)}" height="{f(d)}" color="{fill}" shape="CIRCLE" />')

    def dashed(self, p0, p1, dash, gap, th, color):
        total = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        ux, uy = (p1[0] - p0[0]) / total, (p1[1] - p0[1]) / total
        t = 0.0
        while t < total:
            t2 = min(t + dash, total)
            self.seg((p0[0] + ux * t, p0[1] + uy * t), (p0[0] + ux * t2, p0[1] + uy * t2), th, color)
            t = t2 + gap

    def render(self, w, h, bg):
        return (f'<Snapshot type="png" background="{bg}">\n  <SizedBox width="{w}" height="{h}">\n  '
                '<Stack alignment="TOP_LEFT" clipBehavior="NONE">\n    '
                + "\n    ".join(self.o)
                + "\n  </Stack>\n  </SizedBox>\n</Snapshot>\n")


# ---- audit data ---------------------------------------------------------------
centers = {}
for i, t in enumerate(tlist):
    col, row = i % COLS, i // COLS
    centers[t["id"]] = [X0 + col * (CELL_W + GAP) + CELL_W // 2,
                        Y0 + row * (CELL_H + GAP) + CELL_H // 2]

transforms_audit, geometry_audit = [], []
for t in tlist:
    L, labels = compose_ops(t["operations"])
    cx, cy = centers[t["id"]]
    rect_corners, all_pts = [], []
    for r in stamp["rectangles"]:
        x, y, w, h = r["xywh"]
        src = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
        pts = [apply_canvas(L, p, cx, cy) for p in src]
        rect_corners.append(pts)
        all_pts.extend(pts)
    dot = stamp["dot"]
    d_center = apply_canvas(L, tuple(dot["center"]), cx, cy)
    hx = dot["radius"] * math.hypot(L[0], L[2])   # column 0 norm
    hy = dot["radius"] * math.hypot(L[1], L[3])   # column 1 norm
    all_pts.extend([[d_center[0] - hx, d_center[1] - hy], [d_center[0] + hx, d_center[1] + hy]])
    bbox = [min(p[0] for p in all_pts), min(p[1] for p in all_pts),
            max(p[0] for p in all_pts), max(p[1] for p in all_pts)]
    # subject must stay inside its cell (no clipping, no neighbour bleed)
    ex, ey = cx - CELL_W / 2, cy - CELL_H / 2
    assert bbox[0] >= ex + 4 and bbox[2] <= ex + 232, f"{t['id']} bbox bleeds x: {bbox}"
    assert bbox[1] >= ey + 36 and bbox[3] <= ey + 194, f"{t['id']} bbox bleeds y: {bbox}"
    transforms_audit.append({
        "id": t["id"],
        "operations": t["operations"],
        "operation_labels_input_order": labels,
        "matrix_col_major_16": [float(x) for x in
                                (L[0], L[2], 0, 0, L[1], L[3], 0, 0, 0, 0, 1, 0, 0, 0, 0, 1)],
        "matrix_note": ("linear part only; rendered as <Transform matrix alignment=CENTER> on a "
                        "240x240 box whose center equals local (60,60), so the pivot is the "
                        "fixed point (equivalently full affine about pivot: "
                        f"tx={PIV[0] - (L[0] * 60 + L[1] * 60)}, ty={PIV[1] - (L[2] * 60 + L[3] * 60)})"),
        "cell_center": centers[t["id"]],
        "operations_applied_in_list_order": True,
    })
    geometry_audit.append({
        "id": t["id"],
        "rectangles": [{"source_index": ri,
                        "corners_canvas_TL_TR_BR_BL": [pt for pt in pts]}
                       for ri, pts in enumerate(rect_corners)],
        "dot": {"center_canvas": d_center,
                "bbox_half_extents": [hx, hy],
                "shape_note": "circle under non-uniform scale (T10) becomes an ellipse; bbox from column norms"},
        "bbox_canvas": bbox,
    })

# ---- draw ---------------------------------------------------------------------
d = DSL()
# title block
d.text(X0, 38, "十二个非对称图形变换标本", 40, "#F8FAFC", "BOLD")
d.text(X0, 94, "1600×1200 · 4 列 × 3 行 · 单格 300×250 · 格距 32 · 操作按输入顺序围绕局部 (60,60) · "
               "像素坐标 x→右 y→下", 22, "#94A3B8")

for i, t in enumerate(tlist):
    col, row = i % COLS, i // COLS
    ox = X0 + col * (CELL_W + GAP)
    oy = Y0 + row * (CELL_H + GAP)
    cx, cy = ox + CELL_W // 2, oy + CELL_H // 2
    L, labels = compose_ops(t["operations"])

    d.rect(ox, oy, CELL_W, CELL_H, CELL_BG, f' borderRadius="10" border="1 SOLID {CELL_BD}"')
    # pivot crosshair (dashed, clipped clear of axis labels)
    d.dashed((ox + 40, cy), (ox + 236, cy), 8, 6, 1, CROSS)
    d.dashed((ox + 150, oy + 40), (ox + 150, oy + 190), 8, 6, 1, CROSS)
    # top ruler: ticks every 20px from centre + labels -60/0/+60
    for k in range(-7, 8):
        d.rect(ox + 150 + 20 * k, oy, 1, 6, TICK)
    for off in (-60, 0, 60):
        lab = "-60" if off < 0 else ("0" if off == 0 else "+60")
        d.text(ox + 150 + off - 30, oy + 8, lab, 20, AXIS, w=60, align="CENTER")
    # right ruler
    for k in range(-6, 7):
        d.rect(ox + CELL_W - 6, oy + 125 + 20 * k - 0, 6, 1, TICK)
    for off in (-60, 0, 60):
        d.text(ox + 236, oy + 125 + off - 13, "-60" if off < 0 else ("0" if off == 0 else "+60"),
               20, AXIS, w=56, align="CENTER")

    # subject: ONE Transform.matrix over the whole stamp group
    children = []
    for r in stamp["rectangles"]:
        x, y, w, h = r["xywh"]
        children.append(f'<Positioned left="{x + 60}" top="{y + 60}" width="{w}" height="{h}">'
                        f'<Container color="{r["color"]}" /></Positioned>')
    dc, dr = stamp["dot"]["center"], stamp["dot"]["radius"]
    children.append(f'<Positioned left="{dc[0] - dr + 60}" top="{dc[1] - dr + 60}" '
                    f'width="{2 * dr}" height="{2 * dr}">'
                    f'<Container width="{2 * dr}" height="{2 * dr}" color="{stamp["dot"]["color"]}" '
                    f'shape="CIRCLE" /></Positioned>')
    d.box(ox + 30, oy + 5, 240, 240,
          f'<Transform matrix="{dsl_matrix(L)}" alignment="CENTER">'
          f'<Stack alignment="TOP_LEFT" clipBehavior="NONE">'
          + "".join(children) + "</Stack></Transform>")

    # ID + operation short name (order-explicit for multi-step cells)
    d.text(ox + 10, oy + 6, t["id"], 22, ACCENT, "BOLD")
    if len(t["operations"]) > 1:
        seq = " → ".join(f"{'①②③'[j]}{SHORT[op[0]](op[1])}" for j, op in enumerate(t["operations"]))
    else:
        op = t["operations"][0]
        seq = SHORT[op[0]](op[1])
    d.text(ox + 10, oy + 198, seq, 20, "#CBD5E1")

# legend panel (outside grid)
d.rect(X0, 1040, grid_w, 110, CELL_BG, ' borderRadius="10" border="1 SOLID #1E293B"')
lx_items = [(X0 + 24, "#E54B4B", "① 红矩形 (8,8,28,92)"),
            (X0 + 295, "#2364DB", "② 蓝矩形 (36,72,68,28)"),
            (X0 + 588, "#EAB53B", "③ 黄矩形 (64,8,40,28)")]
for lx, color, label in lx_items:
    d.rect(lx, 1057, 22, 22, color, ' borderRadius="3"')
    d.text(lx + 30, 1056, label, 22, "#F8FAFC")
dot_x = X0 + 876
d.circle(dot_x + 11, 1068, 22, "#111111")
d.text(dot_x + 30, 1056, "黑圆点 (91,49) r=8（打破对称）", 22, "#F8FAFC")
d.text(X0 + 24, 1094, "十字虚线 = 局部枢轴 (60,60)；顶/右边缘刻度 20px/小格，标签 -60/0/+60 对齐枢轴", 20, "#CBD5E1")
d.text(X0 + 24, 1120, "各格主体 = 单个 Transform.matrix（列主序）表示的最终组合变换；圆点随同变换；"
                       "顺时针按图像方向 x→右 y→下", 20, "#CBD5E1")

dsl = d.render(CW, CH, BG)
(tmp_drafts / "transform-atlas.snapshot").write_text(dsl, encoding="utf-8")

audit = {
    "schema_version": 1,
    "task_id": "A09",
    "path_base": "output_dir",
    "coordinate_system": {
        "source_local_origin": "stamp top-left (0,0), units px",
        "source_pivot": [60, 60],
        "x_direction": "right",
        "y_direction": "down",
        "rotation_positive": "clockwise in image orientation",
        "op_semantics": {"mirror_horizontal": "left-right flip (x -> -x about pivot)",
                         "mirror_vertical": "top-bottom flip (y -> -y about pivot)"},
        "cell_mapping": ("canvas_center = [152 + col*332 + 150, 193 + row*282 + 125]; "
                         "p_canvas = cell_center + L * (p_local - [60,60])"),
        "grid_layout": {"cols": 4, "rows": 3, "cell_px": [CELL_W, CELL_H], "gap_px": GAP,
                        "origin_px": [X0, Y0], "canvas_px": [CW, CH]},
        "canvas": {"origin": "top-left", "x_axis": "right", "y_axis": "down", "units": "px"},
    },
    "transforms": transforms_audit,
    "geometry": geometry_audit,
    "verification": [],
    "verification_note": "filled by measure_a09.py from the rendered PNG; see verification[] entries",
    "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
}
(out_dir / "geometry-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2),
                                              encoding="utf-8")

print("dsl bytes:", len(dsl))
print("centers:", {k: centers[k] for k in list(centers)[:4]})
print("T07 matrix:", [round(x, 4) for x in transforms_audit[6]["matrix_col_major_16"][:4]],
      "T08:", [round(x, 4) for x in transforms_audit[7]["matrix_col_major_16"][:4]])
print("audit ->", out_dir / "geometry-audit.json")
