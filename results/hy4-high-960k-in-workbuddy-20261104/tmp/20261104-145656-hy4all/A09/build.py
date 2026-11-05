#!/usr/bin/env python3
"""A09 transform atlas: 12 combined Transform.matrix compositions on a 120x120
asymmetric stamp, 4x3 cells of 300x250 with 32px gaps, centred on 1600x1200.
Emits transform-atlas.snapshot + geometry-audit.json. A separate verify.py fills
in the real PNG pixel measurements after rendering.
"""
import json, os, sys, math
from pathlib import Path

TOOLS = os.environ["TOOLS"]
sys.path.insert(0, TOOLS)
from dsl import Canvas, CN, LATIN, MONO
import suite

TASK = "A09"
ROOT = suite.ROOT
TASK_DIR = ROOT / "tasks" / "A09-transform-atlas"
STAMP = json.loads((TASK_DIR / "inputs" / "stamp.json").read_text(encoding="utf-8"))
TRANSFORMS = json.loads((TASK_DIR / "inputs" / "transforms.json").read_text(encoding="utf-8"))
PIVOT = tuple(STAMP["pivot"])               # (60, 60)
RECTS = [(tuple(r["xywh"]), r["color"]) for r in STAMP["rectangles"]]
DOT = (tuple(STAMP["dot"]["center"]), STAMP["dot"]["radius"], STAMP["dot"]["color"])

# ---------------------------------------------------------------- matrix math
def L_rot(deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return ((c, -s), (s, c))                # clockwise in image coords (y down)


def L_of(op, arg):
    if op == "rotate_clockwise_deg":
        return L_rot(arg)
    if op == "mirror_horizontal":
        return ((-1.0, 0.0), (0.0, 1.0))
    if op == "mirror_vertical":
        return ((1.0, 0.0), (0.0, -1.0))
    if op == "scale_uniform":
        return ((float(arg), 0.0), (0.0, float(arg)))
    if op == "scale_xy":
        return ((float(arg[0]), 0.0), (0.0, float(arg[1])))
    raise ValueError("unknown operation " + op)


def mm(A, B):
    return ((A[0][0] * B[0][0] + A[0][1] * B[1][0], A[0][0] * B[0][1] + A[0][1] * B[1][1]),
            (A[1][0] * B[0][0] + A[1][1] * B[1][0], A[1][0] * B[0][1] + A[1][1] * B[1][1]))


def compose(ops):
    M = ((1.0, 0.0), (0.0, 1.0))
    for op, arg in ops:
        M = mm(L_of(op, arg), M)            # later operation left-multiplies
    return M


def fmt(v):
    if abs(v) < 5e-9:
        v = 0.0
    s = "%.8f" % v
    s = s.rstrip("0").rstrip(".")
    return s if s not in ("", "-0") else "0"


def matrix16(M, C):
    """column-major 4x4 mapping local stamp coords to canvas coords, with
    pivot (60,60) landing on the cell centre C."""
    m00, m01 = M[0]
    m10, m11 = M[1]
    px, py = PIVOT
    tx = C[0] - (m00 * px + m01 * py)
    ty = C[1] - (m10 * px + m11 * py)
    vals = [m00, m10, 0, 0, m01, m11, 0, 0, 0, 0, 1, 0, tx, ty, 0, 1]
    return [round(v, 8) for v in vals], "(" + ",".join(fmt(v) for v in vals) + ")"


def apply(M, C, p):
    m00, m01 = M[0]; m10, m11 = M[1]
    px, py = PIVOT
    x, y = p
    return (C[0] + m00 * (x - px) + m01 * (y - py),
            C[1] + m10 * (x - px) + m11 * (y - py))


def corners_of(xywh):
    x, y, w, h = xywh
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]   # TL, TR, BR, BL


def bbox(points):
    xs = [p[0] for p in points]; ys = [p[1] for p in points]
    return [min(xs), min(ys), max(xs), max(ys)]


# ---------------------------------------------------------------- layout
CW, CH, GAP = 300, 250, 32
GW, GH = 4 * CW + 3 * GAP, 3 * CH + 2 * GAP
GL, GT = (1600 - GW) / 2, (1200 - GH) / 2
assert (GL, GT) == (152.0, 193.0)


def cell(i):
    col, row = i % 4, i // 4
    left = GL + col * (CW + GAP)
    top = GT + row * (CH + GAP)
    return left, top, (left + CW / 2, top + CH / 2)


SHORT = {
    "T01": "R 0°", "T02": "R 90°", "T03": "R 180°", "T04": "R 270°",
    "T05": "MH 左右镜像", "T06": "MV 上下镜像",
    "T07": "MH → R90°", "T08": "R90° → MH",
    "T09": "S 0.75", "T10": "SX1.25 / SY0.75", "T11": "R 30°", "T12": "MV → R30°",
}
ORDER_TAG = {"T07": "先 MH", "T08": "先 R90°"}

# ---------------------------------------------------------------- palette
BG = "#EEF3FA"; WHITE = "#FFFFFF"; INK = "#0F172A"; MUTED = "#5B6B85"
LINE = "#DDE5F0"; GUIDE = "#CDD9EC"; TICK = "#9AAAC2"
NAVY = "#0B1B35"; NAVY2 = "#16386F"; PURPLE = "#6D28D9"; LPURPLE = "#EDE9FE"

c = Canvas(1600, 1200, BG)

# ---- header ----
c.rect(0, 0, 1600, 150, WHITE)
c.rect(0, 146, 1600, 4, "#38BDF8")
c.text(48, 20, 1000, 52, "十二个非对称图形变换标本", 38, NAVY, bold=True)
c.text(48, 80, 1100, 32, "1600×1200 ｜ 4 列 × 3 行 ｜ 每格 300×250 ｜ 格间 32 ｜ 组合矩阵 Transform.matrix", 20, MUTED)
c.text(1140, 28, 420, 34, "A09 / TRANSFORM ATLAS", 19, "#8FB6EA", align="RIGHT", font=LATIN)
c.text(1140, 68, 420, 30, "数据源 stamp.json · transforms.json", 17, MUTED, align="RIGHT")

# ---- cells: background + guide lines (drawn before the subjects) ----
for i in range(12):
    l, t, C = cell(i)
    c.rect(l, t, CW, CH, WHITE, radius=10, border="1 SOLID " + LINE)
    # dashed 120x120 original-stamp reference box
    l0, t0 = C[0] - 60, C[1] - 60
    for k in range(0, 120, 10):
        c.rect(l0 + k, t0, 6, 1.2, GUIDE)
        c.rect(l0 + k + 6, t0 + 119, 4, 1.2, GUIDE)
        c.rect(l0, t0 + k, 1.2, 6, GUIDE)
        c.rect(l0 + 119, t0 + k + 6, 1.2, 4, GUIDE)
    # centre crosshair (dashed)
    for k in range(int(l + 8), int(l + CW - 8), 12):
        c.rect(k, C[1] - 0.6, 7, 1.2, GUIDE)
    for k in range(int(t + 8), int(t + CH - 8), 12):
        c.rect(C[0] - 0.6, k, 1.2, 7, GUIDE)
    # tick marks every 30 px on both axes, longer at +-60
    for d in (-60, -30, 30, 60):
        ln = 12 if abs(d) == 60 else 7
        c.vline(C[0] + d - 0.75, C[1] - ln / 2, ln, 1.5, TICK)
        c.hline(C[0] - ln / 2, C[1] + d - 0.75, ln, 1.5, TICK)

# ---- stamp XML (identical local geometry for all 12 cells) ----
def stamp_inner():
    s = '<Container width="120" height="120"><Stack alignment="TOP_LEFT" clipBehavior="HARD_EDGE">'
    s += '<Container width="120" height="120" />'
    for (x, y, w, h), col in RECTS:
        s += ('<Positioned left="%g" top="%g" width="%g" height="%g">'
              '<Container color="%s" /></Positioned>' % (x, y, w, h, col))
    (dx, dy), r, col = DOT
    s += ('<Positioned left="%g" top="%g" width="%g" height="%g">'
          '<Container color="%s" borderRadius="%g" /></Positioned>' %
          (dx - r, dy - r, 2 * r, 2 * r, col, r))
    s += '</Stack></Container>'
    return s


def subject_xml(mstr):
    return '<Transform matrix="%s">%s</Transform>' % (mstr, stamp_inner())


# ---- compute matrices + geometry, add subjects as direct Stack children ----
records = []
for i, spec in enumerate(TRANSFORMS):
    tid = spec["id"]
    ops = spec["operations"]
    M = compose(ops)
    l, t, C = cell(i)
    vals, mstr = matrix16(M, C)
    c.raw(subject_xml(mstr))
    # geometry
    rects_geo = []
    for xywh, col in RECTS:
        cnv = [list(apply(M, C, p)) for p in corners_of(xywh)]
        rects_geo.append({"color": col, "source_xywh": list(xywh),
                          "corners_canvas_px": cnv, "bbox_px": bbox(cnv)})
    dc = list(apply(M, C, DOT[0]))
    r = DOT[1]
    hx = r * math.hypot(M[0][0], M[0][1])
    hy = r * math.hypot(M[1][0], M[1][1])
    dot_bbox = [dc[0] - hx, dc[1] - hy, dc[0] + hx, dc[1] + hy]
    all_boxes = [rg["bbox_px"] for rg in rects_geo] + [dot_bbox]
    final_bbox = [min(b[0] for b in all_boxes), min(b[1] for b in all_boxes),
                  max(b[2] for b in all_boxes), max(b[3] for b in all_boxes)]
    records.append({
        "id": tid, "operations": ops, "matrix_column_major_16": vals,
        "matrix_dsl": mstr, "cell_left_top_px": [l, t], "cell_center_px": [C[0], C[1]],
        "geometry": {"rectangles": rects_geo, "dot_center_px": dc,
                     "dot_bbox_px": dot_bbox, "final_bbox_px": final_bbox},
    })

# ---- labels (on top of subjects) ----
for i, rec in enumerate(records):
    l, t, C = cell(i)
    tid = rec["id"]
    c.text(l + 14, t + 10, 140, 30, tid, 22, INK, bold=True, font=LATIN)
    if tid in ORDER_TAG:
        c.rect(l + CW - 122, t + 10, 108, 30, LPURPLE, radius=8, border="1 SOLID " + PURPLE)
        c.text(l + CW - 122, t + 11, 108, 28, ORDER_TAG[tid], 20, PURPLE, bold=True, align="CENTER")
    c.text(l + 12, t + CH - 42, CW - 24, 32, SHORT[tid], 20, INK, align="CENTER")

# ---- footer legend ----
c.rect(0, 1015, 1600, 185, "#F8FAFF")
c.rect(0, 1015, 1600, 2, LINE)
c.text(48, 1024, 400, 32, "图例 / 说明", 24, INK, bold=True)
FOOT = [
    "R：顺时针旋转（图像方向，x 右 / y 下）｜ MH：左右镜像 ｜ MV：上下镜像 ｜ S / SX,SY：缩放 ｜ 箭头表示操作先后顺序。",
    "每步均绕局部 (60,60)；最终局部中心置于各格中心；主体只用一个 Transform.matrix 表达组合变换，圆点随同变换。",
    "虚线框 = 原始 120×120 印章范围；十字与刻度 = 局部坐标轴（间隔 30）；彩色矩形与黑圆点均不直接改坐标。",
    "T07（先 MH 后 R90°）与 T08（先 R90° 后 MH）操作相同、顺序不同，组合矩阵与图形结果均不同（对照第 2 行第 3、4 格）。",
]
for i, t in enumerate(FOOT):
    c.text(48, 1062 + i * 32, 1500, 30, t, 20, MUTED)
# colour swatches
sx = 1180
for (xywh, col) in RECTS:
    c.rect(sx, 1028, 26, 20, col, radius=4)
    sx += 34
c.circle(sx + 8, 1038, 9, DOT[2])
c.text(sx + 24, 1024, 260, 28, "印章 3 矩形 + 黑圆点", 20, INK)

dsl = c.render()
out = suite.out_dir(TASK)
(out / "transform-atlas.snapshot").write_text(dsl, encoding="utf-8")
ver = os.environ.get("BUILD_VERSION", "v1")
tmp = suite.tmp_dir(TASK, ver)
(tmp / "transform-atlas.snapshot").write_text(dsl, encoding="utf-8")

# ---------------------------------------------------------------- geometry-audit.json
def rnd(v):
    return round(v, 4)


def rnd_list(ls):
    return [rnd(v) for v in ls]


geometry = []
for rec in records:
    g = rec["geometry"]
    geometry.append({
        "id": rec["id"],
        "rectangles": [
            {"color": r["color"], "source_xywh": r["source_xywh"],
             "corners_canvas_px": [rnd_list(p) for p in r["corners_canvas_px"]],
             "corner_order": "TL,TR,BR,BL",
             "bbox_px": rnd_list(r["bbox_px"])}
            for r in g["rectangles"]
        ],
        "dot_center_px": rnd_list(g["dot_center_px"]),
        "dot_radius_local_px": DOT[1],
        "dot_bbox_px": rnd_list(g["dot_bbox_px"]),
        "final_bbox_px": rnd_list(g["final_bbox_px"]),
    })

verification = []
for rec in records:
    g = rec["geometry"]
    verification.append({
        "id": rec["id"],
        "method": "Pillow 解码最终 PNG；按格矩形裁切；三矩形按原色核心像素阈值求外接框（红 r>190,g<140,b<140；蓝 b>160,r<110,60<g<170，g>60 用于排除紫色角标文字；黄 r>190,g>130,b<140），与组合矩阵预测的角点外接框逐边比较；黑圆点在预测圆心 ±36px 窗口内取暗像素(r,g,b<70)质心。误差取四边绝对差最大值，判据 ±1.5px；旋转 30° 斜边反走样核心像素内缩按例外（≤2.5px）记录，圆心误差仍须 ≤1.5px。",
        "predicted": {"rect_bboxes_px": [rnd_list(r["bbox_px"]) for r in g["rectangles"]],
                      "dot_center_px": rnd_list(g["dot_center_px"]),
                      "final_bbox_px": rnd_list(g["final_bbox_px"])},
        "measured_from_png": None,
        "component_errors_px": None,
        "max_error_px": None,
        "tolerance_px": 1.5,
        "anti_alias_exception": "旋转 30°/非等比缩放的斜边由反走样混合，核心像素外接框会内缩约 1px；此类边缘按例外记录，整数轴对齐边仍按 ±1.5px 判定。",
        "local_evidence": "见 tmp/<run_id>/A09/verify.py 与 tmp/<run_id>/A09/inspect/ 局部放大图；最终 PNG outputs/<run_id>/A09/transform-atlas.png",
        "passed": None,
        "pending_reason": "PNG 尚未渲染/测量；渲染后由 verify.py 填真实测量值与结论。",
    })

audit = {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "coordinate_system": {
        "source_local_origin": "印章左上角 (0,0)",
        "source_local_center_pivot": list(PIVOT),
        "x_direction": "right", "y_direction": "down",
        "rotation_positive": "顺时针（图像方向）：x' = cosθ·x − sinθ·y, y' = sinθ·x + cosθ·y",
        "matrix_storage": "Transform.matrix 为列主序 16 个浮点数 [m00,m10,0,0,m01,m11,0,0,0,0,1,0,tx,ty,0,1]",
        "cell_to_canvas": "格(i) 左上 = (152 + (i%4)*332, 193 + (i//4)*282)；格心 = 左上 + (150,125)；局部 pivot 经组合矩阵映射到格心。",
        "units": "像素",
        "stamp_size": STAMP["size"],
    },
    "transforms": [
        {"id": rec["id"], "operations_in_input_order": rec["operations"],
         "matrix_column_major_16": [rnd(v) for v in rec["matrix_column_major_16"]],
         "matrix_dsl": rec["matrix_dsl"],
         "cell_center_px": rnd_list(rec["cell_center_px"]),
         "cell_left_top_px": rnd_list(rec["cell_left_top_px"])}
        for rec in records
    ],
    "geometry": geometry,
    "verification": verification,
    "paired_order_check": {
        "T07": "MH 后 R90°", "T08": "R90° 后 MH",
        "same_operations": True, "different_order": True,
        "matrix_differ": [round(a - b, 6) for a, b in zip(records[6]["matrix_column_major_16"],
                                                          records[7]["matrix_column_major_16"])],
        "note": "两格短名与『先 MH / 先 R90°』角标直接显示顺序差异；组合矩阵不同，图形结果不同。",
    },
    "evidence": {"png": "transform-atlas.png", "dsl": "transform-atlas.snapshot",
                 "checks": ["12 个主体均为单个 Transform.matrix，形状局部坐标未改",
                            "圆点随同变换", "T07/T08 顺序差异", "不裁切主体", "±1.5px 像素核对"]},
}
(out / "geometry-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("A09 DSL bytes", len(dsl.encode("utf-8")))
for rec in records:
    print(rec["id"], rec["matrix_dsl"], "final bbox", [round(v, 1) for v in rec["geometry"]["final_bbox_px"]])
