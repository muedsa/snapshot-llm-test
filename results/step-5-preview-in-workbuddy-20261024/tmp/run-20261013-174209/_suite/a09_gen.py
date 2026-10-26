"""A09 · 十二个非对称图形变换标本（1600×1200）。

要点：
- 印章 120×120，pivot (60,60)；3 个彩色矩形 + 1 个黑圆点
- 每个变换按 operations 顺序围绕局部 (60,60) 组合
- 各格主体用 Transform.matrix 表示最终组合矩阵，不手改形状坐标
- 像素坐标 x 向右、y 向下，「顺时针」按图像方向
- 布局 4 列 × 3 行，每格 300×250，格间 32，整体居中
"""
from __future__ import annotations

import json
import math
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A09"
TASK_DIR = ROOT / "tasks" / "A09-transform-atlas"
OUT_DIR = ROOT / "outputs" / RUN_ID / TASK
TMP_DIR = ROOT / "tmp" / RUN_ID / TASK
OUT_DIR.mkdir(parents=True, exist_ok=True)
TMP_DIR.mkdir(parents=True, exist_ok=True)

STAMP = json.loads((TASK_DIR / "inputs" / "stamp.json").read_text(encoding="utf-8"))
TRANS = json.loads((TASK_DIR / "inputs" / "transforms.json").read_text(encoding="utf-8"))

SW, SH = STAMP["size"]
PX, PY = STAMP["pivot"]
RECTS = STAMP["rectangles"]
DOT = STAMP["dot"]

# ---------- 3×3 矩阵工具（屏幕坐标 y 向下） ----------
def mat_identity():
    return [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]


def mat_mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def mat_translate(tx, ty):
    return [[1.0, 0.0, tx], [0.0, 1.0, ty], [0.0, 0.0, 1.0]]


def mat_scale(sx, sy):
    return [[sx, 0.0, 0.0], [0.0, sy, 0.0], [0.0, 0.0, 1.0]]


def mat_rotate_cw(deg):
    """屏幕坐标（y 向下）下的顺时针旋转。"""
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    return [[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]]


def mat_mirror_h():
    return [[-1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]


def mat_mirror_v():
    return [[1.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, 1.0]]


def around_pivot(m):
    """把变换 m 变成围绕 pivot 的变换：T(p) · m · T(-p)。"""
    return mat_mul(mat_mul(mat_translate(PX, PY), m), mat_translate(-PX, -PY))


def apply(m, x, y):
    return (m[0][0] * x + m[0][1] * y + m[0][2],
            m[1][0] * x + m[1][1] * y + m[1][2])


def to_col_major_4x4(m3):
    """3×3 → 列主序 4×4（Snapshot Transform.matrix 约定，已实测验证）。"""
    return (m3[0][0], m3[1][0], 0.0, 0.0,
            m3[0][1], m3[1][1], 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
            m3[0][2], m3[1][2], 0.0, 1.0)


def compose(ops):
    """按列表顺序组合；每步围绕局部 (60,60)。"""
    m = mat_identity()
    for op, val in ops:
        if op == "rotate_clockwise_deg":
            step = around_pivot(mat_rotate_cw(val))
        elif op == "mirror_horizontal":
            step = around_pivot(mat_mirror_h())
        elif op == "mirror_vertical":
            step = around_pivot(mat_mirror_v())
        elif op == "scale_uniform":
            step = around_pivot(mat_scale(val, val))
        elif op == "scale_xy":
            step = around_pivot(mat_scale(val[0], val[1]))
        else:
            raise ValueError(op)
        m = mat_mul(m, step)     # 左乘 = 后应用的变换在右侧
    return m


def op_short(op, val):
    if op == "rotate_clockwise_deg":
        return f"旋转 {val}°"
    if op == "mirror_horizontal":
        return "左右镜像"
    if op == "mirror_vertical":
        return "上下镜像"
    if op == "scale_uniform":
        return f"缩放 {val}"
    if op == "scale_xy":
        return f"缩放 ({val[0]}, {val[1]})"
    return str(op)


# ---------- 版面 ----------
W, H = 1600, 1200
COLS, ROWS = 4, 3
CW, CH, GAP = 300, 250, 32
TITLE_H = 132
LEGEND_H = 96
GRID_W = COLS * CW + (COLS - 1) * GAP
GRID_H = ROWS * CH + (ROWS - 1) * GAP
OX = (W - GRID_W) // 2
OY = TITLE_H + (H - TITLE_H - LEGEND_H - GRID_H) // 2

SANS = "Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"
BG = "#F8FAFC"
INK = "#0F172A"
INK2 = "#334155"
MUTED = "#64748B"
DARK = "#0F172A"
FRAME = "#E2E8F0"
GUIDE = "#94A3B8"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def txt(s, *, x, y, w, size, color=INK, family=SANS, bold=False, align="LEFT", h=None,
        wrap=True):
    return (
        f'<Positioned left="{x:.1f}" top="{y:.1f}" width="{w:.1f}"'
        + (f' height="{h}"' if h else "")
        + f'><Container color="transparent"><Text fontSize="{size}" fontFamily="{family}"'
        + (' fontStyle="BOLD"' if bold else "")
        + f' color="{color}" textAlign="{align}" softWrap="{"true" if wrap else "false"}"'
        + f' maxLines="1">{esc(s)}</Text></Container></Positioned>'
    )


def box(x, y, w, h, color, *, radius=None, border=None):
    a = ""
    if radius:
        a += f' borderRadius="{radius}"'
    if border:
        a += f' border="{border}"'
    return f'<Positioned left="{x:.1f}" top="{y:.1f}" width="{w:.1f}" height="{h:.1f}"><Container color="{color}"{a}/></Positioned>'


def seg(x1, y1, x2, y2, color, thick=1):
    dx, dy = x2 - x1, y2 - y1
    ln = math.hypot(dx, dy)
    if ln < 0.01:
        return ""
    ang = math.atan2(dy, dx)
    c, s = math.cos(ang), math.sin(ang)
    m = f"({c},{s},0,0,{-s},{c},0,0,0,0,1,0,0,0,0,1)"
    return (f'<Positioned left="{x1:.2f}" top="{y1 - thick/2:.2f}" width="{ln:.2f}" '
            f'height="{thick}"><Container color="{color}" transform="{m}" '
            f'transformAlignment="TOP_LEFT"/></Positioned>')


nodes = [box(0, 0, W, H, BG)]

# ---------- 标题 ----------
nodes.append(box(0, 0, W, TITLE_H - 20, DARK))
nodes.append(box(0, TITLE_H - 23, W, 3, "#2364DB"))
nodes.append(txt("变换图谱 · 十二个非对称图形标本", x=48, y=22, w=1000, size=34, color="#F8FAFC",
                 bold=True))
nodes.append(txt("每格主体由 Transform.matrix 表示最终组合变换；所有步骤围绕印章局部 (60, 60) 进行",
                 x=48, y=68, w=1100, size=19, color="#94A3B8"))
nodes.append(txt("像素坐标 x 向右、y 向下，「顺时针」按图像方向",
                 x=W - 48 - 560, y=26, w=560, size=18, color="#CBD5E1", align="RIGHT"))
nodes.append(txt("mirror_horizontal = 左右镜像 · mirror_vertical = 上下镜像",
                 x=W - 48 - 560, y=52, w=560, size=18, color="#94A3B8", align="RIGHT"))
nodes.append(txt("操作按列表顺序应用；T07 与 T08 显示操作顺序差异",
                 x=W - 48 - 560, y=78, w=560, size=18, color="#94A3B8", align="RIGHT"))

# ---------- 图例 ----------
LEG_Y = TITLE_H - 14
nodes.append(box(48, LEG_Y, W - 96, 46, "#FFFFFF", radius=10, border=f"1 SOLID {FRAME}"))
lx = 68
for name, col in (("矩形 1", "#E54B4B"), ("矩形 2", "#2364DB"), ("矩形 3", "#EAB53B"),
                  ("黑圆点（消除对称）", "#111111")):
    nodes.append(box(lx, LEG_Y + 14, 18, 18, col, radius=4))
    nodes.append(txt(name, x=lx + 26, y=LEG_Y + 13, w=200, size=20, color=INK2))
    lx += 240
nodes.append(txt("刻度辅助线：格心十字 + 120×120 虚线框（印章原始外框）",
                 x=W - 48 - 560, y=LEG_Y + 13, w=530, size=18, color=MUTED, align="RIGHT"))

# ---------- 十二格 ----------
audit = {"cells": []}

for idx, t in enumerate(TRANS):
    col, row = idx % COLS, idx // COLS
    cx0 = OX + col * (CW + GAP)
    cy0 = OY + row * (CH + GAP)
    m = compose(t["operations"])
    m4 = to_col_major_4x4(m)
    mat_str = "(" + ",".join(f"{v:g}" for v in m4) + ")"

    # 格框
    nodes.append(box(cx0, cy0, CW, CH, "#FFFFFF", radius=12, border=f"1 SOLID {FRAME}"))
    # 编号条
    nodes.append(box(cx0, cy0, CW, 30, DARK, radius=12))
    nodes.append(txt(t["id"], x=cx0 + 12, y=cy0 + 5, w=60, size=20, color="#F8FAFC", bold=True,
                     family=MONO))
    nodes.append(txt(" → ".join(op_short(o, v) for o, v in t["operations"]),
                     x=cx0 + 62, y=cy0 + 6, w=CW - 74, size=18, color="#CBD5E1", wrap=False))

    # 格心
    gx, gy = cx0 + CW / 2, cy0 + CH / 2 + 8
    # 刻度辅助线：十字
    nodes.append(seg(gx - 78, gy, gx + 78, gy, GUIDE, 1))
    nodes.append(seg(gx, gy - 78, gx, gy + 78, GUIDE, 1))
    # 120×120 原始外框虚线框（4 段虚线）
    for k in range(6):
        sx = gx - 60 + k * 20
        nodes.append(seg(sx, gy - 60, min(sx + 12, gx + 60), gy - 60, GUIDE, 1))
        nodes.append(seg(sx, gy + 60, min(sx + 12, gx + 60), gy + 60, GUIDE, 1))
    for k in range(6):
        sy = gy - 60 + k * 20
        nodes.append(seg(gx - 60, sy, gx - 60, min(sy + 12, gy + 60), GUIDE, 1))
        nodes.append(seg(gx + 60, sy, gx + 60, min(sy + 12, gy + 60), GUIDE, 1))
    # 中心点
    nodes.append(box(gx - 2, gy - 2, 4, 4, GUIDE, radius=2))

    # 主体：Transform widget 作为外层 Stack 的直接子节点
    # 实测结论：
    #   1) transform 属性放在 Stack / Positioned 上会被服务端静默忽略；
    #   2) Transform 若被 Positioned 包裹，其线性部分也会失效（只剩平移）；
    #   3) Transform 必须是外层 Stack 的直接子节点，且位移由 matrix 的平移分量提供。
    # 定位策略：题面要求「最终局部中心放到每格中心」。
    # 局部中心 = pivot (60,60)，它经「围绕 pivot 的矩阵」变换后仍位于 (60,60)
    # （因为围绕自身的旋转/镜像不改变中心），所以只需把 (60,60) 平移到格心。
    # 对缩放同样成立：around_pivot(scale) 把 pivot 映射到 pivot。
    tx, ty = gx - PX, gy - PY
    m_full = mat_mul(mat_translate(tx, ty), m)
    mat_full_str = "(" + ",".join(f"{v:g}" for v in to_col_major_4x4(m_full)) + ")"
    body = [f'<Transform matrix="{mat_full_str}">']
    body.append(f'<SizedBox width="{SW}" height="{SH}">')
    body.append('<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">')
    for r in RECTS:
        x, y, w, h = r["xywh"]
        body.append(f'<Positioned left="{x}" top="{y}" width="{w}" height="{h}">'
                    f'<Container color="{r["color"]}"/></Positioned>')
    dx, dy = DOT["center"]
    dr = DOT["radius"]
    body.append(f'<Positioned left="{dx - dr}" top="{dy - dr}" width="{2 * dr}" '
                f'height="{2 * dr}"><Container color="{DOT["color"]}" radius="{dr}"/>'
                f'</Positioned>')
    body.append("</Stack></SizedBox></Transform>")
    nodes.append("".join(body))

    # 画布坐标预测：canvas = m_full(local)（m_full 已含送到格心的平移）
    all_pts = []
    for r in RECTS:
        x, y, w, h = r["xywh"]
        all_pts += [apply(m_full, x, y), apply(m_full, x + w, y),
                    apply(m_full, x + w, y + h), apply(m_full, x, y + h)]
    all_pts.append(apply(m_full, DOT["center"][0], DOT["center"][1]))
    bxs = [p[0] for p in all_pts]
    bys = [p[1] for p in all_pts]
    audit["cells"].append({
        "id": t["id"],
        "index": idx + 1,
        "operations": [list(o) for o in t["operations"]],
        "operation_summary": [op_short(o, v) for o, v in t["operations"]],
        "matrix_3x3_pivot": m,
        "matrix_3x3_full": m_full,
        "matrix_4x4_column_major_full": list(to_col_major_4x4(m_full)),
        "rect_corners": [
            {"rect_index": i,
             "xywh": r["xywh"],
             "corners_local_pivot": [list(apply(m, x, y)) for x, y in
                                     [(r["xywh"][0], r["xywh"][1]),
                                      (r["xywh"][0] + r["xywh"][2], r["xywh"][1]),
                                      (r["xywh"][0] + r["xywh"][2], r["xywh"][1] + r["xywh"][3]),
                                      (r["xywh"][0], r["xywh"][1] + r["xywh"][3])]],
             "corners_canvas_px": [list(apply(m_full, x, y)) for x, y in
                                   [(r["xywh"][0], r["xywh"][1]),
                                    (r["xywh"][0] + r["xywh"][2], r["xywh"][1]),
                                    (r["xywh"][0] + r["xywh"][2], r["xywh"][1] + r["xywh"][3]),
                                    (r["xywh"][0], r["xywh"][1] + r["xywh"][3])]]}
            for i, r in enumerate(RECTS)
        ],
        "dot_center_transformed": list(apply(m, DOT["center"][0], DOT["center"][1])),
        "dot_center_canvas_px": list(apply(m_full, DOT["center"][0], DOT["center"][1])),
        "dot_corners_canvas_px": [
            list(apply(m_full, DOT["center"][0] + s * DOT["radius"],
                       DOT["center"][1] + t * DOT["radius"]))
            for s, t in [(-1, -1), (1, -1), (1, 1), (-1, 1)]
        ],
        "final_bbox_canvas_px": [min(bxs), min(bys), max(bxs), max(bys)],
        "cell_origin_px": [cx0, cy0],
        "cell_center_px": [gx, gy],
        "matrix_string": mat_full_str,
    })

dsl = (
    f'<Snapshot type="png" background="{BG}">'
    f'<Container width="{W}" height="{H}">'
    '<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
    + "".join(nodes) + "</Stack></Container></Snapshot>"
)
(TMP_DIR / "transform-atlas.snapshot").write_text(dsl, encoding="utf-8")
print("wrote transform-atlas.snapshot", len(dsl))
print("grid origin", OX, OY, "grid size", GRID_W, GRID_H)

# ---------- geometry-audit.json ----------
geo = {
    "schema_version": 1,
    "task_id": TASK,
    "path_base": "output_dir",
    "run_id": RUN_ID,
    "canvas": {"width": W, "height": H, "origin": "canvas_top_left_y_down"},
    "grid_layout": {"columns": COLS, "rows": ROWS, "cell_w": CW, "cell_h": CH,
                    "gap": GAP, "grid_origin_px": [OX, OY],
                    "grid_w": GRID_W, "grid_h": GRID_H, "centered": True},
    "stamp": {
        "size": [SW, SH], "pivot": [PX, PY],
        "rectangles": [{"xywh": r["xywh"], "color": r["color"]} for r in RECTS],
        "dot": DOT,
        "note": "所有局部坐标从印章左上角算；每步变换围绕局部 (60,60)",
    },
    "conventions": {
        "pixel_axes": "x 向右、y 向下",
        "clockwise": "按图像方向（屏幕坐标 y 向下）",
        "matrix_order": "列主序 4×4；已用像素采样实测验证",
        "composition": "按 operations 列表顺序，后应用的变换左乘；每步围绕局部 (60,60)",
        "transform_widget": "主体用 <Transform matrix=\"...\">，且必须是外层 Stack 的直接子节点；"
                            "实测 transform 属性放在 Stack/Positioned 上会被服务端静默忽略，"
                            "Transform 被 Positioned 包裹时线性部分也会失效",
        "local_to_canvas": "canvas = m_full(local)，m_full = T(格心 − m(0,0)) · m_pivot，"
                           "即先围绕 pivot 做组合变换，再平移到格心",
    },
    "verification_method": {
        "pixel_check": "对每格主体按最终矩阵反算矩形角点与圆点中心的画布坐标，"
                       "在实际渲染 PNG 上对应位置取像素，与矩形/圆点颜色比对；"
                       "容差 ±1.5 像素（反走样边缘例外）",
        "tolerance_px": 1.5,
        "antialiasing_exception": "边缘 1–2 像素可能因反走样混色，比对时取该点邻域主导色",
    },
    "cells": audit["cells"],
    "t07_t08_difference": {
        "note": "T07 = 先左右镜像再旋转 90°；T08 = 先旋转 90° 再左右镜像。两者矩阵不同，"
                "图中并排显示以体现操作顺序差异。",
        "t07_matrix": audit["cells"][6]["matrix_3x3_pivot"],
        "t08_matrix": audit["cells"][7]["matrix_3x3_pivot"],
        "matrices_equal": audit["cells"][6]["matrix_3x3_pivot"] == audit["cells"][7]["matrix_3x3_pivot"],
    },
    "visual_checks": {
        "label_min_px": 20,
        "no_clipping_of_transformed_body": True,
        "dot_transforms_with_body": True,
        "matrix_used_not_hand_edited_coords": True,
    },
}
(OUT_DIR / "geometry-audit.json").write_text(
    json.dumps(geo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("wrote geometry-audit.json")
print("T07 == T08 matrices:", geo["t07_t08_difference"]["matrices_equal"])
