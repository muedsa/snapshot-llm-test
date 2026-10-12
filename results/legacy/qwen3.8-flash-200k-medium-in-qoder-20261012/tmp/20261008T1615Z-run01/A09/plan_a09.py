"""A09 data layer: compose every transform into one affine matrix and audit it.

Inputs are read verbatim from tasks/A09-transform-atlas/inputs/ (never rewritten).
Convention (documented in the delivered audit):

  * pixel coordinates: x to the right, y downwards -> the standard rotation matrix
    with +theta is *visually clockwise* on screen;
  * mirror_horizontal = left/right flip  -> [[-1,0],[0,1]]
    mirror_vertical   = top/bottom flip  -> [[1,0],[0,-1]];
  * every operation happens around the stamp-local pivot (60,60);
  * operations compose in list order, i.e. the first entry is applied first, so
    A_total = A_last @ ... @ A_first;
  * final placement maps local (60,60) onto the centre of its cell, hence the
    screen mapping q = cell_centre + A @ (p - pivot).

Only this module knows the matrix maths; the picture and the audit both read its
output, so a printed number can never disagree with a drawn pixel.
"""
import json
import math
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A09"
TEMP = ROOT / "tmp" / RID / TASK
OUT = ROOT / "outputs" / RID / TASK
INP = ROOT / "tasks" / "A09-transform-atlas" / "inputs"

stamp = json.loads((INP / "stamp.json").read_text(encoding="utf-8"))
transforms = json.loads((INP / "transforms.json").read_text(encoding="utf-8"))

SW, SH = stamp["size"]
PX, PY = stamp["pivot"]
assert (SW, SH) == (120, 120) and (PX, PY) == (60, 60)

COLS, ROWS = 4, 3
CW, CH, GAP = 300, 250, 32
GRID_W = COLS * CW + (COLS - 1) * GAP          # 1296
GRID_H = ROWS * CH + (ROWS - 1) * GAP          # 814
CANVAS_W, CANVAS_H = 1600, 1200
GX = (CANVAS_W - GRID_W) / 2.0                 # 152
GY = (CANVAS_H - GRID_H) / 2.0                 # 193

TOL = 1.5                                      # required cross-check tolerance


def mat_of(op, arg):
    if op == "rotate_clockwise_deg":
        r = math.radians(arg)
        return [[math.cos(r), -math.sin(r)], [math.sin(r), math.cos(r)]]
    if op == "mirror_horizontal":
        assert arg is True
        return [[-1.0, 0.0], [0.0, 1.0]]
    if op == "mirror_vertical":
        assert arg is True
        return [[1.0, 0.0], [0.0, -1.0]]
    if op == "scale_uniform":
        return [[arg, 0.0], [0.0, arg]]
    if op == "scale_xy":
        sx, sy = arg
        return [[sx, 0.0], [0.0, sy]]
    raise ValueError(f"unknown operation {op}")


def mul(A, B):
    return [[A[0][0] * B[0][0] + A[0][1] * B[1][0], A[0][0] * B[0][1] + A[0][1] * B[1][1]],
            [A[1][0] * B[0][0] + A[1][1] * B[1][0], A[1][0] * B[0][1] + A[1][1] * B[1][1]]]


def round6(v):
    return round(v + 0.0, 6)


def apply(A, p):
    return [A[0][0] * p[0] + A[0][1] * p[1], A[1][0] * p[0] + A[1][1] * p[1]]


def column_major44(A, t):
    """4x4, column-major, index = row + 4*col, affine 2-D part plus translation."""
    return [round6(A[0][0]), round6(A[1][0]), 0.0, 0.0,
            round6(A[0][1]), round6(A[1][1]), 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
            round6(t[0]), round6(t[1]), 0.0, 1.0]


def rect_corners(r):
    x, y, w, h = r["xywh"]
    return [[x, y], [x + w, y], [x + w, y + h], [x, y + h]]


def short_name(ops):
    parts = []
    for op, arg in ops:
        if op == "rotate_clockwise_deg":
            parts.append(f"rot {arg:g}°")
        elif op == "mirror_horizontal":
            parts.append("mirror H")
        elif op == "mirror_vertical":
            parts.append("mirror V")
        elif op == "scale_uniform":
            parts.append(f"scale {arg:g}")
        elif op == "scale_xy":
            parts.append(f"scale {arg[0]:g}×{arg[1]:g}")
    return " \u2192 ".join(parts) if parts else "identity"


def describe(ops):
    """Human-readable order statement; identity rotation still counts as a step."""
    if len(ops) == 1 and ops[0][0] == "rotate_clockwise_deg":
        return f"1 步 · 绕 (60,60) {short_name(ops)}"
    return f"{len(ops)} 步依序 · {short_name(ops)}"


cells = []
for idx, tf in enumerate(transforms):
    col, row = idx % COLS, idx // COLS
    cx = GX + col * (CW + GAP) + CW / 2.0
    cy = GY + row * (CH + GAP) + CH / 2.0
    ops = [(o, a) for o, a in tf["operations"]]
    A = [[1.0, 0.0], [0.0, 1.0]]
    steps = []
    for op, arg in ops:                      # list order: first entry applied first
        M = mat_of(op, arg)
        A = mul(M, A)
        steps.append({"operation": op, "argument": arg,
                      "matrix_column_major_around_pivot": column_major44(
                          M, [PX - (M[0][0] * PX + M[0][1] * PY),
                             PY - (M[1][0] * PX + M[1][1] * PY)])})
    det = A[0][0] * A[1][1] - A[0][1] * A[1][0]
    flipped = det < 0

    # local-space image of the shape (stamp-local frame: pivot stays at (60,60))
    loc = []
    for r in stamp["rectangles"]:
        pts = []
        for p in rect_corners(r):
            v = apply(A, [p[0] - PX, p[1] - PY])
            pts.append([round6(PX + v[0]), round6(PY + v[1])])
        loc.append(pts)
    d0 = stamp["dot"]["center"]
    dv = apply(A, [d0[0] - PX, d0[1] - PY])
    dotc = [round6(PX + dv[0]), round6(PY + dv[1])]
    rr = stamp["dot"]["radius"]
    ex = rr * math.hypot(A[0][0], A[0][1])          # ellipse half-extents
    ey = rr * math.hypot(A[1][0], A[1][1])
    xs = [p[0] for c in loc for p in c] + [dotc[0] - ex, dotc[0] + ex]
    ys = [p[1] for c in loc for p in c] + [dotc[1] - ey, dotc[1] + ey]
    bbox_loc = [round6(min(xs)), round6(min(ys)), round6(max(xs)), round6(max(ys))]

    t = [cx - (A[0][0] * PX + A[0][1] * PY), cy - (A[1][0] * PX + A[1][1] * PY)]
    scr = [[[round6(cx + (p[0] - PX)), round6(cy + (p[1] - PY))] for p in c]
           for c in loc]
    dot_s = [round6(cx + dotc[0] - PX), round6(cy + dotc[1] - PY)]
    bbox_scr = [round6(cx + bbox_loc[0] - PX), round6(cy + bbox_loc[1] - PY),
                round6(cx + bbox_loc[2] - PX), round6(cy + bbox_loc[3] - PY)]

    rect_bboxes = [[round6(min(p[0] for p in c)), round6(min(p[1] for p in c)),
                    round6(max(p[0] for p in c)), round6(max(p[1] for p in c))]
                   for c in scr]

    cells.append({
        "id": tf["id"], "index": idx, "row": row, "column": col,
        "cell_rect_canvas": [round6(GX + col * (CW + GAP)), round6(GY + row * (CH + GAP)),
                             CW, CH],
        "cell_centre_canvas": [round6(cx), round6(cy)],
        "operations": [[o, a] for o, a in ops],
        "operation_order_note": describe(ops),
        "short_name": short_name(ops),
        "matrix_2x2_about_pivot": [[round6(v) for v in r] for r in A],
        "matrix_column_major_local": column_major44(A, [0.0, 0.0]),
        "matrix_column_major_screen": column_major44(A, t),
        "transform_matrix_attribute": "(" + ",".join(
            f"{v:.6f}" for v in column_major44(A, [0.0, 0.0])) + ")",
        "determinant": round6(det),
        "orientation_reversing": flipped,
        "steps": steps,
        "rect_corners_local": loc,
        "rect_corners_canvas": scr,
        "rect_bboxes_canvas": rect_bboxes,
        "dot_centre_local": dotc,
        "dot_centre_canvas": dot_s,
        "dot_ellipse_half_extents": [round6(ex), round6(ey)],
        "bbox_local": bbox_loc,
        "bbox_canvas": bbox_scr,
    })

for c in cells:                              # nothing may be clipped by its cell
    x0, y0, x1, y1 = c["bbox_canvas"]
    cx0, cy0, cw, ch = c["cell_rect_canvas"]
    c["inside_cell"] = bool(x0 >= cx0 - 0.5 and y0 >= cy0 - 0.5
                            and x1 <= cx0 + cw + 0.5 and y1 <= cy0 + ch + 0.5)
    c["cell_margin_px"] = [round6(x0 - cx0), round6(y0 - cy0),
                           round6(cx0 + cw - x1), round6(cy0 + ch - y1)]
problems = [c["id"] for c in cells if not c["inside_cell"]]

t07, t08 = cells[6], cells[7]
order_proof = {
    "note": "T07 = rotate90 ∘ mirrorH 与 T08 = mirrorH ∘ rotate90 主对角/副对角不同，"
            "证明操作顺序影响结果；图中两者分开绘制并在说明行标注先后",
    "T07_matrix_2x2": t07["matrix_2x2_about_pivot"],
    "T08_matrix_2x2": t08["matrix_2x2_about_pivot"],
    "matrices_equal": t07["matrix_2x2_about_pivot"] == t08["matrix_2x2_about_pivot"],
    "corner_image_differs": t07["rect_corners_local"] != t08["rect_corners_local"],
    "T07_dot_local": t07["dot_centre_local"], "T08_dot_local": t08["dot_centre_local"],
}

audit = {
    "schema_version": 1, "path_base": "suite_root", "task_id": TASK, "run_id": RID,
    "source": {
        "stamp": "tasks/A09-transform-atlas/inputs/stamp.json",
        "transforms": "tasks/A09-transform-atlas/inputs/transforms.json",
        "image": "outputs/20261008T1615Z-run01/A09/transform-atlas.png",
        "generator": "tmp/20261008T1615Z-run01/A09/generate_a09.py",
    },
    "conventions": {
        "pixel_axes": "x 向右、y 向下；因此 [[cos,-sin],[sin,cos]] 在屏幕上呈视觉顺时针",
        "pivot": "每一步都围绕印章局部 (60,60) 进行；局部坐标从印章左上角量起",
        "composition": "operations 按列表顺序依次作用（第一项先作用），A_total = A_last ··· A_first",
        "placement": "最终局部中心 (60,60) 落在所属格中心",
        "mirror": "mirror_horizontal=左右镜像 [[-1,0],[0,1]]；mirror_vertical=上下镜像 [[1,0],[0,-1]]",
        "matrix_layout": "列主序 4×4，索引 = row + 4*col；与 DSL Transform.matrix 属性同序",
        "dsl_binding": "Transform matrix=<列主序矩阵> alignment=\"CENTER\"，子节点是未被改写坐标的"
                       "原始 120×120 印章（3 矩形 + 圆点），因此主体完全由矩阵表达",
        "units": "px（1 局部单位 = 1 像素，缩放直接乘在局部坐标上）",
    },
    "canvas": {"width": CANVAS_W, "height": CANVAS_H,
               "grid": {"columns": COLS, "rows": ROWS, "cell_w": CW, "cell_h": CH,
                        "gap": GAP, "grid_w": GRID_W, "grid_h": GRID_H,
                        "origin": [round6(GX), round6(GY)],
                        "centred": "grid 水平与垂直均居中：left=152、top=193"}},
    "stamp": stamp,
    "tolerance_px": TOL,
    "verification_method": {
        "visual": "把 transform-atlas.png 按格裁出 300×250 与整图，用 NEAREST 放大后与预测角点、外接框数值逐格对照；"
                  "NEAREST 避免 LANCZOS 把边缘插值成第二条线（A08 曾因此误判）",
        "pixel": f"对每格统计 4 种成分色（{[r['color'] for r in stamp['rectangles']]} 与 "
                 f"圆点 {stamp['dot']['color']}）的墨迹像素，取最小外接框与质心，"
                 f"与该格 rect_bboxes_canvas / dot_centre_canvas / bbox_canvas 比较，"
                 f"要求 |Δ| ≤ {TOL}px；像素按“舞台底色→成分色”的混合线段归属成分，"
                 f"因此反走样过渡像素计入而不误判",
        "edge_caveat": "边缘一圈像素是抗锯齿混合值：若只统计完全等于成分色的饱和像素，实测外接框会在"
                       "右/下两侧系统性地缩进约 2px（v02 实测），因此判据改为把 stage→成分色 线段上的"
                       "过渡像素也算作该成分；两种成分色的混合（矩形相接的接缝）不属于任何一条线段，"
                       "自动排除。超过 ±1.5px 记为不合格；圆点只比质心与外接范围，不比轮廓",
        "corner_probe": "角点位置用“亚像素支撑线残差”判定：把该成分的全部墨迹像素投影到“多边形中心→角点”"
                        "方向（矩形在该方向的唯一极值点正是这个角点），再用抗锯齿覆盖率将像素中心换算成真实"
                        "边缘位置 中心+(α−0.5)，取投影极值与预测角点投影之差，要求 |Δ| ≤ 1.5px。早期版本改用"
                        "固定内侧 2.5px 探针，在 T11/T12 上产生 2 次误判：细长条的角点对角线几乎平行于长边，"
                        "2.5px 只深入宽度 0.7px，正好落在相邻矩形覆盖的接缝上；此外角标刻线外偏 6px，避免角标"
                        "被当成主体墨迹（v02 的 28 个角点误判即由此而来）",
        "rim_attribution": "角点残差对边缘像素采用两条准入路径：干净的“舞台底色→成分色”混合，或距纯成分色 "
                           "≤40 色阶的像素；后者是必需的，因为印章下方有 20px 刻度网格，个别角点最外一圈像素是 "
                           "黄×网格×舞台的三重混合（实测 T11 rect3 角点 (1016,882) 黄色 α=0.92 但网格混合使"
                           "stage→黄 拟合误差 15，严格路径会漏掉该像素）",
        "identity_controls": "T01 为单位矩阵，其外接框必须等于原始印章 bbox（8,8)-(104,100) 加圆点半径，"
                             "用于证明对齐原点没有被 DSL 平移",
        "ab_anticlipping": "每格 bbox_canvas 与格边界之间保留正 margin（cell_margin_px），"
                           "证明变换后的主体没有被裁切",
        "tool": "tmp/20261008T1615Z-run01/A09/check_a09.py",
    },
    "cells": cells,
    "order_dependence": order_proof,
    "problems": problems,
}
(TEMP / "plan_a09.json").write_text(json.dumps(audit, ensure_ascii=False, indent=1),
                                    encoding="utf-8")
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "geometry-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=1),
                                         encoding="utf-8")

print(json.dumps({
    "cells": len(cells), "problems": problems,
    "matrices_distinct": len({c["transform_matrix_attribute"] for c in cells}),
    "T07": t07["matrix_2x2_about_pivot"], "T08": t08["matrix_2x2_about_pivot"],
    "order_matrices_equal": order_proof["matrices_equal"],
    "short_names": [c["short_name"] for c in cells],
    "min_cell_margin": min(min(c["cell_margin_px"]) for c in cells),
    "max_bbox_w": max(round6(c["bbox_canvas"][2] - c["bbox_canvas"][0]) for c in cells),
    "max_bbox_h": max(round6(c["bbox_canvas"][3] - c["bbox_canvas"][1]) for c in cells),
}, ensure_ascii=False))
