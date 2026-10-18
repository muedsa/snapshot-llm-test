"""A09 · 十二个非对称图形变换标本 (1600×1200) — Transform.matrix atlas."""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A09"
TMP = ROOT / "tmp" / RUN / TASK
VERSION = sys.argv[1] if len(sys.argv) > 1 else "v001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))

from dsl import C, Col, Gap, HGap, Label, Pos, Row, SizedBox, Stack, T  # noqa: E402

BG = "#F4F1E9"
CELL_BG = "#FFFFFF"
INK = "#111827"
MUTED = "#6B7280"
FAINT = "#9CA3AF"
BORDER = "#D8E0EA"
GUIDE = "#E5EAF1"
AMBER = "#B45309"
TEAL = "#0F766E"

W, H = 1600, 1200
CELL_W, CELL_H, GAP = 300, 250, 32
GRID_W = 4 * CELL_W + 3 * GAP
GRID_H = 3 * CELL_H + 2 * GAP
X0 = (W - GRID_W) // 2
Y0 = 180
PIVOT = (60.0, 60.0)

SHORT = {
    "T01": "0°", "T02": "CW 90°", "T03": "180°", "T04": "CW 270°",
    "T05": "镜像 H", "T06": "镜像 V", "T07": "镜像H → CW90°", "T08": "CW90° → 镜像H",
    "T09": "缩放 0.75×", "T10": "缩放 1.25 / 0.75", "T11": "CW 30°", "T12": "镜像V → CW30°",
}


def mat_mul(A, B):
    a, c, tx = A[0]
    b, d, ty = A[1]
    ea, ec, etx = B[0]
    eb, ed, ety = B[1]
    return [[a * ea + c * eb, a * ec + c * ed, a * etx + c * ety + tx],
            [b * ea + d * eb, b * ec + d * ed, b * etx + d * ety + ty],
            [0, 0, 1]]


def op_matrix(name, val):
    if name == "rotate_clockwise_deg":
        t = math.radians(val)
        co, si = math.cos(t), math.sin(t)
        A = [[co, -si, 0], [si, co, 0], [0, 0, 1]]
    elif name == "mirror_horizontal":
        A = [[-1, 0, 0], [0, 1, 0], [0, 0, 1]]
    elif name == "mirror_vertical":
        A = [[1, 0, 0], [0, -1, 0], [0, 0, 1]]
    elif name == "scale_uniform":
        A = [[val, 0, 0], [0, val, 0], [0, 0, 1]]
    elif name == "scale_xy":
        A = [[val[0], 0, 0], [0, val[1], 0], [0, 0, 1]]
    else:
        raise ValueError(name)
    return [[A[0][0], A[0][1], PIVOT[0] - A[0][0] * PIVOT[0] - A[0][1] * PIVOT[1]],
            [A[1][0], A[1][1], PIVOT[1] - A[1][0] * PIVOT[0] - A[1][1] * PIVOT[1]],
            [0, 0, 1]]


def final_matrix(ops, center):
    M = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    for name, val in ops:
        M = mat_mul(op_matrix(name, val), M)
    return mat_mul([[1, 0, center[0] - PIVOT[0]], [0, 1, center[1] - PIVOT[1]], [0, 0, 1]], M)


def apply(M, x, y):
    return (M[0][0] * x + M[0][1] * y + M[0][2], M[1][0] * x + M[1][1] * y + M[1][2])


def matrix16(M):
    return [M[0][0], M[1][0], 0, 0, M[0][1], M[1][1], 0, 0, 0, 0, 1, 0, M[0][2], M[1][2], 0, 1]


def transform_widget(M, stamp):
    m = matrix16(M)
    mstr = "(" + ",".join(f"{v:.6f}".rstrip("0").rstrip(".") if isinstance(v, float) else str(v) for v in m) + ")"
    shapes = []
    for i, r in enumerate(stamp["rectangles"]):
        x, y, w, h = r["xywh"]
        shapes.append(Pos(x, y, C(width=w, height=h, color=r["color"]), w=w, h=h))
    d = stamp["dot"]
    rad = d["radius"]
    shapes.append(Pos(d["center"][0] - rad, d["center"][1] - rad,
                      C(width=rad * 2, height=rad * 2, color=d["color"], borderRadius=rad)))
    child = Stack(shapes + [SizedBox(120, 120)], width=120, height=120)
    return f'<Transform matrix="{mstr}">{child}</Transform>'


def cell(t, stamp, col, row):
    cx0 = X0 + col * (CELL_W + GAP)
    cy0 = Y0 + row * (CELL_H + GAP)
    center = (CELL_W / 2, CELL_H / 2)
    M = final_matrix(t["operations"], center)
    cw, ch = CELL_W, CELL_H
    layers = [SizedBox(cw, ch)]
    # guides
    layers.append(Pos(16, ch / 2, C(width=cw - 32, height=1, color=GUIDE)))
    layers.append(Pos(cw / 2, 16, C(width=1, height=ch - 32, color=GUIDE)))
    for d in (-60, -30, 30, 60):
        layers.append(Pos(cw / 2 + d, ch / 2 - 3, C(width=1, height=6, color="#C7D0DD")))
        layers.append(Pos(cw / 2 - 3, ch / 2 + d, C(width=6, height=1, color="#C7D0DD")))
    # 120x120 reference frame (centered on pivot)
    rx, ry = cw / 2 - 60, ch / 2 - 60
    layers.append(Pos(rx, ry, C(width=120, height=120, color="transparent", border=f"1 SOLID {GUIDE}")))
    layers.append(Pos(cw / 2 - 2, ch / 2 - 2, C(width=4, height=4, color="#94A3B8", borderRadius=2)))
    layers.append(transform_widget(M, stamp))
    layers.append(Pos(12, 8, T(t["id"], size=20, color=INK, weight="BOLD", family="Inter")))
    layers.append(Pos(12, ch - 32, T(SHORT[t["id"]], size=20, color=TEAL, weight="BOLD")))
    return Pos(cx0, cy0, C(width=cw, height=ch, color=CELL_BG, borderRadius=12,
                           border=f"1 SOLID {BORDER}", child=Stack(layers, width=cw, height=ch)),
               w=cw, h=ch)


def build(stamp, transforms):
    header = Row([
        C(width=46, height=46, gradientType="LINEAR", gradientColors="#E54B4B,#2364DB,#EAB53B",
          gradientBegin="TOP_LEFT", gradientEnd="BOTTOM_RIGHT", borderRadius=12,
          child=C(alignment="CENTER", child=T("M", size=20, color="#FFFFFF", weight="BOLD", family="Inter"))),
        HGap(12),
        Col([
            T("十二个非对称图形变换标本", size=40, color=INK, weight="BOLD", family="Noto Serif CJK SC,Inter"),
            Gap(2),
            T("4×3 · 每格 300×250 · 格间 32 · 围绕局部 (60,60) 逐步变换", size=20, color=MUTED),
        ], crossAxisAlignment="START"),
        '<Spacer />',
        Col([
            T("TRANSFORM ATLAS", size=14, color=TEAL, weight="BOLD", family="Inter", spacing=2),
            Gap(3),
            T("12 SPECIMENS · ONE STAMP", size=15, color=MUTED, family="Inter"),
        ], crossAxisAlignment="END"),
    ], crossAxisAlignment="CENTER")

    grid = [cell(t, stamp, i % 4, i // 4) for i, t in enumerate(transforms)]

    legend = C(width=1520, height=184, color="#FFFFFF", borderRadius=14, border=f"1 SOLID {BORDER}",
               padding="(16,24)", child=Row([
                   C(width=920, child=Col([
                       Row([T("读图", size=22, color=INK, weight="BOLD"), HGap(10),
                            T("同一 120×120 印章（3 矩形 + 黑点）在 12 个矩阵下的结果", size=20, color=MUTED)]),
                       Gap(5),
                       T("所有格子的主体均由 Transform.matrix 应用；圆点随同变换，用来消除旋转/镜像的对称歧义。十字线、刻度与 120×120 参考框只帮助定位，不参与变换。", size=19, color=MUTED, height="1.35"),
                       Gap(4),
                       T("T07 / T08 同为“镜像 + 90°”，但顺序不同：T07 先镜像 H 再 CW90°；T08 先 CW90° 再镜像 H；矩阵与图形均不同。数据源 stamp.json / transforms.json。", size=19, color=AMBER, height="1.35"),
                   ], crossAxisAlignment="START")),
                   HGap(24),
                   C(width=1, height=102, color=BORDER),
                   HGap(24),
                   C(width=500, child=Col([
                       Row([C(width=22, height=14, color="#E54B4B"), HGap(6), T("矩形 A", size=20, color=MUTED),
                            HGap(14), C(width=22, height=14, color="#2364DB"), HGap(6), T("矩形 B", size=20, color=MUTED),
                            HGap(14), C(width=22, height=14, color="#EAB53B"), HGap(6), T("矩形 C", size=20, color=MUTED)]),
                       Gap(6),
                       Row([C(width=14, height=14, color="#111111", borderRadius=7), HGap(6), T("黑点（消除对称）", size=20, color=MUTED)]),
                       Gap(6),
                       T("矩阵：列主序 4×4，16 个有限浮点；旋转正向为屏幕顺时针。", size=18, color=FAINT),
                   ], crossAxisAlignment="START")),
               ], crossAxisAlignment="START"))

    content = Stack([
        SizedBox(W, H),
        Pos(0, 0, C(width=W, height=5, gradientType="LINEAR",
                    gradientColors="#E54B4B00,#E54B4BE6,#2364DBE6,#EAB53B00",
                    gradientBegin="CENTER_LEFT", gradientEnd="CENTER_RIGHT"), w=W, h=5),
        Pos(40, 30, header, w=W - 80, h=76),
        *grid,
        Pos(40, 1006, legend, w=1520, h=184),
    ], width=W, height=H)
    return f'<Snapshot type="png" background="{BG}">\n{content}\n</Snapshot>\n'


def geometry(stamp, transforms):
    out = []
    for t in transforms:
        col, row = (int(t["id"][1:]) - 1) % 4, (int(t["id"][1:]) - 1) // 4
        cx0 = X0 + col * (CELL_W + GAP)
        cy0 = Y0 + row * (CELL_H + GAP)
        local_center = (CELL_W / 2, CELL_H / 2)
        center = (cx0 + CELL_W / 2, cy0 + CELL_H / 2)
        M_local = final_matrix(t["operations"], local_center)
        M = final_matrix(t["operations"], center)
        rects = []
        for i, r in enumerate(stamp["rectangles"]):
            x, y, w, h = r["xywh"]
            corners_src = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
            corners = [apply(M, px, py) for px, py in corners_src]
            rects.append({"index": i, "color": r["color"], "source_xywh": [x, y, w, h],
                          "corners": [[round(px, 4), round(py, 4)] for px, py in corners]})
        dot = stamp["dot"]
        dot_center = apply(M, dot["center"][0], dot["center"][1])
        pts = [p for r in rects for p in r["corners"]]
        pts += [[dot_center[0] - dot["radius"], dot_center[1] - dot["radius"]],
                [dot_center[0] + dot["radius"], dot_center[1] + dot["radius"]]]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        out.append({
            "id": t["id"], "operations": t["operations"],
            "matrix_local_column_major": [round(v, 8) for v in matrix16(M_local)],
            "matrix_canvas_column_major": [round(v, 8) for v in matrix16(M)],
            "cell_origin": [cx0, cy0], "cell_center": [round(center[0], 2), round(center[1], 2)],
            "rectangles": rects,
            "dot_center": [round(dot_center[0], 4), round(dot_center[1], 4)],
            "bbox": [round(min(xs), 4), round(min(ys), 4), round(max(xs), 4), round(max(ys), 4)],
        })
    return out


def main() -> int:
    stamp = json.loads((ROOT / "tasks" / "A09-transform-atlas" / "inputs" / "stamp.json").read_text(encoding="utf-8"))
    transforms = json.loads((ROOT / "tasks" / "A09-transform-atlas" / "inputs" / "transforms.json").read_text(encoding="utf-8"))
    dsl = build(stamp, transforms)
    d = TMP / "dsl"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{VERSION}.snapshot").write_text(dsl, encoding="utf-8")
    geom = geometry(stamp, transforms)
    audit = {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
        "matrix_note": "matrix_column_major 是实际写入 Transform 的局部矩阵（格内坐标，格心为 150,125）；matrix_canvas_column_major 叠加了格原点，仅用于审计画布角点。",
        "coordinate_system": {
            "source_origin": "stamp local top-left", "source_size": [120, 120],
            "pivot": [60, 60], "x_direction": "right", "y_direction": "down",
            "rotation_positive": "clockwise on screen (y down)",
            "cell_mapping": "final local center (60,60) maps to each cell center; Transform.matrix is applied to the source shape coordinates",
            "cell_centers": [[X0 + (i % 4) * (CELL_W + GAP) + CELL_W / 2,
                              Y0 + (i // 4) * (CELL_H + GAP) + CELL_H / 2] for i in range(12)],
        },
        "transforms": [{"id": g["id"], "operations": g["operations"],
                        "matrix_column_major": g["matrix_local_column_major"],
                        "matrix_canvas_column_major": g["matrix_canvas_column_major"],
                        "cell_origin": g["cell_origin"], "cell_center": g["cell_center"]} for g in geom],
        "geometry": [{"id": g["id"], "rectangles": g["rectangles"], "dot_center": g["dot_center"], "bbox": g["bbox"]} for g in geom],
        "verification": [],
        "t07_t08": {
            "different_local_matrix": [round(a - b, 8) for a, b in zip(geom[6]["matrix_local_column_major"], geom[7]["matrix_local_column_major"])],
            "note": "T07 先镜像 H 再 CW90°；T08 先 CW90° 再镜像 H。",
        },
    }
    (TMP / "geometry-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"A09 {VERSION}: {len(dsl)} bytes, 12 cells")
    return 0


if __name__ == "__main__":
    sys.exit(main())
