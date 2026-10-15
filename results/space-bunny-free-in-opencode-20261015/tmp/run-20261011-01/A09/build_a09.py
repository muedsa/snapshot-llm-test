#!/usr/bin/env python
"""A09 十二个非对称图形变换标本 —— 1600×1200 变换图谱。

启动基准：总任务根(suite_root)。输入 tasks/A09-transform-atlas/inputs/ 只读。
每格主体用一个 Transform.matrix 承载最终组合矩阵；矩形与圆点的局部坐标原样取自 stamp.json。
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, "tmp/run-20261011-01/_suite/scripts")
import snapkit as sk  # noqa: E402
from snapkit import C  # noqa: E402

TASK = "A09"
BASE = "tasks/A09-transform-atlas"
STAMP_IN = f"{BASE}/inputs/stamp.json"
XF_IN = f"{BASE}/inputs/transforms.json"
DRAFTS = f"tmp/run-20261011-01/{TASK}/drafts"

W, H = 1600, 1200
CW, CH, GAPX, GAPY = 300, 250, 32, 32
GX = (W - (4 * CW + 3 * GAPX)) // 2          # 152
GY = 140
CELL_CX, CELL_CY = 150, 112                  # 格内主体中心相对格左上
OPS_TOP, OPS_STEP = 196, 25                 # 操作序列文字带（每步操作一行）
PIVOT = (60, 60)

SHORT = {
    "T01": "恒等（原样）", "T02": "顺时针 90°", "T03": "顺时针 180°", "T04": "顺时针 270°",
    "T05": "左右镜像", "T06": "上下镜像", "T07": "镜像 → 旋转 90°", "T08": "旋转 90° → 镜像",
    "T09": "等比缩放 0.75", "T10": "非等比 1.25 × 0.75", "T11": "顺时针 30°",
    "T12": "上下镜像 → 旋转 30°",
}


def load():
    r = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
    return (json.loads((r / STAMP_IN).read_text(encoding="utf-8")),
            json.loads((r / XF_IN).read_text(encoding="utf-8")))


# ---------------------------------------------------------------- 矩阵
def I():
    return [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]


def mul(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def apply(M, p):
    return (M[0][0] * p[0] + M[0][1] * p[1] + M[0][2],
            M[1][0] * p[0] + M[1][1] * p[1] + M[1][2])


def lin(M, v):
    """只取线性部分（忽略平移）。"""
    return (M[0][0] * v[0] + M[0][1] * v[1], M[1][0] * v[0] + M[1][1] * v[1])


def about_pivot(L, p=PIVOT):
    """先平移到枢轴 → 线性变换 → 平移回枢轴；枢轴在局部坐标中保持不动。"""
    t = I()
    t[0][2], t[1][2] = -p[0], -p[1]
    back = I()
    back[0][2], back[1][2] = p[0], p[1]
    return mul(back, mul(L, t))


def op_matrix(op):
    kind, val = op[0], op[1]
    if kind == "rotate_clockwise_deg":
        # 屏幕坐标 y 向下：正角 = 图像顺时针
        a = math.radians(float(val))
        c, s = math.cos(a), math.sin(a)
        return about_pivot([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])
    if kind == "mirror_horizontal":          # 左右镜像：x → −x
        return about_pivot([[-1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
    if kind == "mirror_vertical":            # 上下镜像：y → −y
        return about_pivot([[1.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, 1.0]])
    if kind == "scale_uniform":
        s = float(val)
        return about_pivot([[s, 0.0, 0.0], [0.0, s, 0.0], [0.0, 0.0, 1.0]])
    if kind == "scale_xy":
        sx, sy = float(val[0]), float(val[1])
        return about_pivot([[sx, 0.0, 0.0], [0.0, sy, 0.0], [0.0, 0.0, 1.0]])
    raise SystemExit(f"未知操作 {kind}")


def compose(ops):
    M = I()
    for op in ops:                 # 按输入顺序：先做的在右侧
        M = mul(op_matrix(op), M)
    return M


def col_major(M, nd=6):
    """列主序 4×4（16 个数）。

    实测语义（见 tmp/run-20261011-01/A09/probe_matrix.py 与 preview/probe-p1.png）：
    服务端把 `Transform(matrix, alignment="CENTER")` 实现为
        p' = C + L·(p − C) + t
    其中 C 是子节点中心、L 是矩阵线性部分、t 是矩阵最后一列的平移量；
    m[8], m[9] 被忽略。由于印章容器的中心恰好就是枢轴 (60,60)，
    要得到「绕 (60,60) 的组合变换」，只需把**线性部分**写入矩阵、t 取 0。
    因此这里输出 L + 单位第三行第四行。
    """
    v = col_major_list(M)
    return "(" + ",".join(f"{round(x, nd) + 0.0:g}" for x in v) + ")"


def col_major_list(M):
    v = [0.0] * 16
    v[0], v[1] = M[0][0], M[1][0]
    v[4], v[5] = M[0][1], M[1][1]
    v[10] = 1.0
    v[15] = 1.0
    return v


def cell_xy(idx):
    c, r = idx % 4, idx // 4
    return GX + c * (CW + GAPX), GY + r * (CH + GAPY)


# ---------------------------------------------------------------- 图元
def dashed(x1, y1, x2, y2, wdt, color, dash=8.0, gap=6.0):
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    if L < 0.01:
        return ""
    ux, uy = dx / L, dy / L
    parts, t = [], 0.0
    while t < L:
        e = min(t + dash, L)
        parts.append(seg(x1 + ux * t, y1 + uy * t, x1 + ux * e, y1 + uy * e, wdt, color))
        t = e + gap
    return "".join(parts)


def seg(x1, y1, x2, y2, wdt, color):
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    if L < 0.01:
        return ""
    ang = math.degrees(math.atan2(dy, dx))
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    bw = L + wdt + 2
    return (f'<Positioned left="{round(cx - bw / 2, 2)}" top="{round(cy - wdt / 2, 2)}" '
            f'width="{round(bw, 2)}" height="{wdt}">'
            f'<Transform matrix="{sk.rot_matrix(ang)}" alignment="CENTER">'
            f'<Container width="{round(bw, 2)}" height="{wdt}" color="{color}" '
            f'borderRadius="{round(wdt / 2, 2)}"/></Transform></Positioned>')


def arrow(x, y, ux, uy, color, size=9.0, thick=2.6, ang=34.0):
    a = math.radians(ang)
    d1 = (ux * math.cos(a) - uy * math.sin(a), ux * math.sin(a) + uy * math.cos(a))
    d2 = (ux * math.cos(-a) - uy * math.sin(-a), ux * math.sin(-a) + uy * math.cos(-a))
    return (seg(x - d1[0] * size, y - d1[1] * size, x, y, thick, color) +
            seg(x - d2[0] * size, y - d2[1] * size, x, y, thick, color))


# ---------------------------------------------------------------- 建图
def build(stamp, xforms):
    P = []
    A = P.append
    A(f'<Positioned left="0" top="0" width="{W}" height="{H}">'
      f'<Container width="{W}" height="{H}" color="#F5F8FC"/></Positioned>')

    # 页眉
    A(sk.text("十二个非对称图形变换标本", size=36, color=C.INK, family=sk.F_HEAD,
              left=GX, top=24, width=760, height=48))
    A(sk.text("印章 120×120 · 枢轴 O(60,60) · 4 列 × 3 行 · 每格 300×250 · 格距 32",
              size=22, color=C.MUTED, family=sk.F_BODY, left=GX, top=80, width=760, height=30))

    recs = []
    for i, xf in enumerate(xforms):
        tid = xf["id"]
        cx0, cy0 = cell_xy(i)
        ccx, ccy = cx0 + CELL_CX, cy0 + CELL_CY
        M = compose(xf["operations"])

        # 格底
        A(f'<Positioned left="{cx0}" top="{cy0}" width="{CW}" height="{CH}">'
          f'<Container width="{CW}" height="{CH}" color="#FFFFFF" borderRadius="14" '
          f'border="1.5 SOLID #CBD5E1"/></Positioned>')
        # 编号 + 短名
        A(f'<Positioned left="{cx0 + 14}" top="{cy0 + 10}" width="56" height="30">'
          f'<Container width="56" height="30" color="#1E293B" borderRadius="8" alignment="CENTER">'
          f'<Text fontSize="22" color="#FFFFFF" fontFamily="{sk.F_HEAD}" fontStyle="BOLD">'
          f'{tid}</Text></Container></Positioned>')
        A(sk.text(SHORT[tid], size=22, color=C.INK, family=sk.F_HEAD,
                  left=cx0 + 78, top=cy0 + 12, width=210, height=28))
        # 操作序列：一步一行，避免两条操作在换行处连成一片
        for k, o in enumerate(xf["operations"]):
            A(f'<Positioned left="{cx0 + 14}" top="{cy0 + OPS_TOP + k * OPS_STEP}" '
              f'width="{CW - 28}" height="{OPS_STEP}">'
              f'<Text fontSize="20" color="{C.MUTED}" fontFamily="{sk.F_BODY}">'
              f'{sk.esc(f"({k + 1}) " + op_label(o))}</Text></Positioned>')

        # 中心坐标轴（辅助线）
        A(seg(ccx - 100, ccy, ccx + 100, ccy, 1.6, "#64748B"))
        A(seg(ccx, ccy - 72, ccx, ccy + 72, 1.6, "#64748B"))
        for d in (1, -1):
            A(arrow(ccx + d * 100, ccy, d, 0, "#64748B"))
            A(arrow(ccx, ccy + d * 72, 0, d, "#64748B"))
        # 轴端字母：放在局部 120×120 框之外（所有变换后印章都不越出该框），
        # 且不落在操作序列文字带（cy0+196 起）内。
        A(sk.text("x", size=20, color=C.MUTED, family=sk.F_NUM, align="CENTER",
                  left=ccx + 60, top=ccy - 31, width=28, height=22))
        A(sk.text("y", size=20, color=C.MUTED, family=sk.F_NUM, align="CENTER",
                  left=ccx - 40, top=ccy + 60, width=28, height=22))

        # 局部坐标框（120×120 原位参考）+ 每 20 单位一格刻度
        bx0, by0 = cx0 + CELL_CX - 60, cy0 + CELL_CY - 60
        for a, b in (((bx0, by0), (bx0 + 120, by0)), ((bx0 + 120, by0), (bx0 + 120, by0 + 120)),
                     ((bx0 + 120, by0 + 120), (bx0, by0 + 120)), ((bx0, by0 + 120), (bx0, by0))):
            A(dashed(a[0], a[1], b[0], b[1], 1.4, "#CBD5E1", dash=9, gap=7))
        for k in range(1, 6):
            t = bx0 + k * 20
            A(seg(t, by0 + 120, t, by0 + 127, 1.6, "#94A3B8"))
            t = by0 + k * 20
            A(seg(bx0, t, bx0 - 7, t, 1.6, "#94A3B8"))

        # 主体：一个 Transform.matrix 承载最终组合变换
        m = col_major(M)
        stamp_nodes = []
        for rc in stamp["rectangles"]:
            x, y, w_, h_ = rc["xywh"]
            stamp_nodes.append(
                f'<Positioned left="{x}" top="{y}" width="{w_}" height="{h_}">'
                f'<Container width="{w_}" height="{h_}" color="{rc["color"]}"/></Positioned>')
        dc = stamp["dot"]["center"]
        dr = stamp["dot"]["radius"]
        stamp_nodes.append(
            f'<Positioned left="{dc[0] - dr}" top="{dc[1] - dr}" width="{2 * dr}" height="{2 * dr}">'
            f'<ClipOval><Container width="{2 * dr}" height="{2 * dr}" color="{stamp["dot"]["color"]}"/>'
            f'</ClipOval></Positioned>')
        A(f'<Positioned left="{bx0}" top="{by0}" width="120" height="120">'
          f'<Transform matrix="{m}" alignment="CENTER">'
          f'<Container width="120" height="120"><Stack fit="EXPAND">'
          f'{"".join(stamp_nodes)}</Stack></Container></Transform></Positioned>')
        # 枢轴标记（不随变换移动，标出局部中心落点）
        A(f'<Positioned left="{ccx - 5}" top="{ccy - 5}" width="10" height="10">'
          f'<ClipOval><Container width="10" height="10" color="#FFFFFF"/></ClipOval></Positioned>')
        A(f'<Positioned left="{ccx - 7}" top="{ccy - 7}" width="14" height="14">'
          f'<ClipOval><Container width="14" height="14" color="#FFFFFF00" border="2 SOLID #94A3B8"/>'
          f'</ClipOval></Positioned>')

        # 几何记录
        rects = []
        allpts = []
        for rc in stamp["rectangles"]:
            x, y, w_, h_ = rc["xywh"]
            corners = [(x, y), (x + w_, y), (x + w_, y + h_), (x, y + h_)]
            cs = [apply(M, p) for p in corners]
            canv = [[round(bx0 + p[0], 4), round(by0 + p[1], 4)] for p in cs]
            rects.append({"color": rc["color"], "source_xywh": [x, y, w_, h_],
                          "local_corners_tl_tr_br_bl": [[round(p[0], 4), round(p[1], 4)] for p in corners],
                          "transformed_local": [[round(p[0], 4), round(p[1], 4)] for p in cs],
                          "canvas_corners_tl_tr_br_bl": canv})
            allpts += canv
        dot_local = apply(M, tuple(dc))
        dot_canvas = [round(bx0 + dot_local[0], 4), round(by0 + dot_local[1], 4)]
        ux = lin(M, (1, 0))
        vy = lin(M, (0, 1))
        nu = math.hypot(*ux) or 1.0
        nv = math.hypot(*vy) or 1.0
        radii = {"radius_if_uniform": round(dr * max(nu, nv), 4),
                 "semi_axis_u": round(dr * nu, 4), "semi_axis_v": round(dr * nv, 4),
                 "note": "等比变换时为圆；非等比（T10）时沿 u/v 为长短半轴的椭圆"}
        for k in range(24):
            th = 2 * math.pi * k / 24
            allpts.append([dot_canvas[0] + (nu if abs(nu - nv) < 1e-9 else nu) * math.cos(th) * 1.0,
                           dot_canvas[1] + nv * math.sin(th) * 1.0])
        bb = [round(min(p[0] for p in allpts), 4), round(min(p[1] for p in allpts), 4),
              round(max(p[0] for p in allpts), 4), round(max(p[1] for p in allpts), 4)]
        cell_box = [cx0, cy0, cx0 + CW, cy0 + CH]
        recs.append({
            "id": tid, "short_name": SHORT[tid],
            "operations": [[o[0], o[1]] for o in xf["operations"]],
            "operations_readable": [op_label(o) for o in xf["operations"]],
            "matrix_about_pivot_3x3": [[round(v, 6) for v in row] for row in M],
            "matrix_linear_2x2": [[round(M[0][0], 6), round(M[0][1], 6)],
                                  [round(M[1][0], 6), round(M[1][1], 6)]],
            "matrix_column_major_4x4_dsl": [round(x, 6) for x in col_major_list(M)],
            "matrix_dsl_string": m,
            "cell_index": i, "cell_box_px": cell_box,
            "cell_center_px": [round(ccx, 4), round(ccy, 4)],
            "local_origin_px": [round(bx0, 4), round(by0, 4)],
            "stamp_geometry": {"rectangles": rects,
                               "dot": {"source_center": dc, "source_radius": dr,
                                       "transformed_local_center": [round(dot_local[0], 4),
                                                                    round(dot_local[1], 4)],
                                       "canvas_center": dot_canvas, "radii": radii}},
            "final_bounding_box_px": bb,
            "fits_in_cell": bb[0] >= cell_box[0] and bb[1] >= cell_box[1]
                             and bb[2] <= cell_box[2] and bb[3] <= cell_box[3],
            "clipped_by_cell": not (bb[0] >= cell_box[0] and bb[1] >= cell_box[1]
                                    and bb[2] <= cell_box[2] and bb[3] <= cell_box[3]),
        })

    # ---------------- 图例
    LX, LY, LW, LH = GX, 966, 4 * CW + 3 * GAPX, 224
    A(f'<Positioned left="{LX}" top="{LY}" width="{LW}" height="{LH}">'
      f'<Container width="{LW}" height="{LH}" color="#FFFFFF" borderRadius="14" '
      f'border="1.5 SOLID #CBD5E1"/></Positioned>')
    # 参考印章
    rx, ry = LX + 24, LY + 30
    A(dashed(rx, ry, rx + 120, ry, 1.4, "#CBD5E1", dash=9, gap=7))
    A(dashed(rx, ry, rx, ry + 120, 1.4, "#CBD5E1", dash=9, gap=7))
    A(dashed(rx, ry + 120, rx + 120, ry + 120, 1.4, "#CBD5E1", dash=9, gap=7))
    A(dashed(rx + 120, ry, rx + 120, ry + 120, 1.4, "#CBD5E1", dash=9, gap=7))
    for rc in stamp["rectangles"]:
        x, y, w_, h_ = rc["xywh"]
        A(f'<Positioned left="{rx + x}" top="{ry + y}" width="{w_}" height="{h_}">'
          f'<Container width="{w_}" height="{h_}" color="{rc["color"]}"/></Positioned>')
    dc, dr = stamp["dot"]["center"], stamp["dot"]["radius"]
    A(f'<Positioned left="{rx + dc[0] - dr}" top="{ry + dc[1] - dr}" width="{2 * dr}" height="{2 * dr}">'
      f'<ClipOval><Container width="{2 * dr}" height="{2 * dr}" color="{stamp["dot"]["color"]}"/>'
      f'</ClipOval></Positioned>')
    A(f'<Positioned left="{rx + PIVOT[0] - 6}" top="{ry + PIVOT[1] - 6}" width="12" height="12">'
      f'<ClipOval><Container width="12" height="12" color="#FFFFFF00" border="2 SOLID #94A3B8"/>'
      f'</ClipOval></Positioned>')
    A(sk.text("原始印章（未变换）", size=20, color=C.SLATE, family=sk.F_BODY,
              left=rx - 6, top=ry + 132, width=180, height=24))

    tx = rx + 200
    lines = [
        "印章：3 个彩色矩形 + 1 个黑圆点，局部画布 120×120",
        "局部坐标自左上角起算；每步围绕枢轴 (60,60) 进行",
        "x 向右、y 向下；顺时针为图像顺时针（正角）",
        "操作按输入顺序相乘（先做的在矩阵右侧）",
        "mirror_horizontal = 左右镜像 x→−x；mirror_vertical = 上下镜像 y→−y",
        "虚线框为局部 0–120 原位参考，边缘刻度每 20 单位一格",
    ]
    ty = LY + 14
    for t in lines:
        n = sk.est_lines(t, 690, 20)
        A(f'<Positioned left="{tx}" top="{ty}" width="700" height="{n * 27}">'
          f'{sk.wrapped(700, t, size=20, color=C.INK2, line_height=1.35)}</Positioned>')
        ty += n * 27 + 3

    cx2 = tx + 720
    t07t08 = ("T07 = 镜像H → 旋转90°，结果为关于 x+y=120 的反对角线反射；"
              "T08 = 旋转90° → 镜像H，结果为关于 x=y 的主对角线反射。两格互为镜像。")
    nw = LW - (cx2 - LX) - 22
    A(f'<Positioned left="{cx2}" top="{LY + 16}" width="{nw}" height="192">'
      f'<Container width="{nw}" height="192" color="#FFF7ED" borderRadius="10" '
      f'border="1.4 SOLID #FDBA74"><Stack fit="EXPAND">'
      f'<Positioned left="14" top="12" width="{nw - 28}" height="30">'
      f'<Text fontSize="22" color="#9A3412" fontFamily="{sk.F_HEAD}" softWrap="true">'
      f'T07 与 T08：顺序不同</Text>'
      f'</Positioned>'
      f'<Positioned left="14" top="50" width="{nw - 28}" height="140">'
      f'{sk.wrapped(nw - 28, t07t08, size=20, color="#7C2D12", line_height=1.38)}'
      f'</Positioned></Stack></Container></Positioned>')

    dsl = (f'<Snapshot type="png">\n<Container width="{W}" height="{H}">\n<Stack fit="EXPAND">\n'
           f'{"".join(P)}\n</Stack>\n</Container>\n</Snapshot>\n')
    return dsl, recs


def op_label(op):
    k, v = op[0], op[1]
    if k == "rotate_clockwise_deg":
        return f"顺时针 {int(v)}°"
    if k == "mirror_horizontal":
        return "左右镜像"
    if k == "mirror_vertical":
        return "上下镜像"
    if k == "scale_uniform":
        return f"等比缩放 {v}"
    if k == "scale_xy":
        return f"非等比 {v[0]} × {v[1]}"
    return str(k)


def main():
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    r = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
    stamp, xforms = load()
    dsl, recs = build(stamp, xforms)
    d = r / DRAFTS
    d.mkdir(parents=True, exist_ok=True)
    (d / f"a09-{ver}.snapshot").write_text(dsl, encoding="utf-8")

    audit = {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir", "round": "round-01",
        "coordinate_system": {
            "source_local": {"canvas": stamp["size"], "origin": "top-left",
                             "pivot": stamp["pivot"], "x_direction": "right", "y_direction": "down"},
            "canvas": {"width": W, "height": H, "origin": "top-left",
                       "x_direction": "right", "y_direction": "down"},
            "grid": {"cols": 4, "rows": 3, "cell_px": [CW, CH], "gap_px": [GAPX, GAPY],
                     "grid_origin_px": [GX, GY], "grid_size_px": [4 * CW + 3 * GAPX, 3 * CH + 2 * GAPY],
                     "centering": f"水平居中：(1600 − 1296) / 2 = {GX}"},
            "mapping": "格 (c,r) 左上 = (GX + c×332, GY + r×282)；"
                       "格内主体中心 = 格左上 + (150,112)；"
                       "局部坐标 (x,y) 的画布位置 = 局部原点 + M·(x,y)，"
                       "局部原点 = 格左上 + (90,52)；"
                       "操作序列文字自格左上 + (14,196) 起，每步操作一行、行距 25",
            "rotation_positive": "屏幕坐标 y 向下，矩阵 [[c,−s],[s,c]] 使正角对应图像顺时针",
            "matrix_convention": "行主序 3×3 记绕枢轴的完整仿射；写入 Transform.matrix 时取其线性部分，"
                                 "转成列主序 4×4（16 个数），平移列置 0",
            "engine_transform_semantics": {
                "formula": "p' = C + L·(p − C) + t，C = 子节点中心，L = 线性部分，t = 最后一列平移",
                "evidence": "探针 tmp/run-20261011-01/A09/probe_matrix.py 与 preview/probe-p1.png："
                            "P2（仅线性部分 + alignment=CENTER）落点与理论值一致；"
                            "P1（再写一次平移 t=120）整体右移 120px；"
                            "P3（把平移放进 m[8],m[9]）与 P2 完全相同，说明该两槽被忽略；"
                            "P4（alignment=TOP_LEFT）绕子节点左上角旋转，确认 alignment 生效",
                "consequence": "印章容器中心即枢轴 (60,60)，故矩阵只写线性部分即可得到绕枢轴的组合变换",
            },
        },
        "inputs": {"stamp": "inputs/stamp.json", "transforms": "inputs/transforms.json",
                   "modified": False,
                   "rectangles": len(stamp["rectangles"]), "dot_radius": stamp["dot"]["radius"]},
        "transforms": [{
            "id": rec["id"], "short_name": rec["short_name"],
            "operations": rec["operations"],
            "operations_readable": rec["operations_readable"],
            "matrix_about_pivot_3x3": rec["matrix_about_pivot_3x3"],
            "matrix_linear_2x2": rec["matrix_linear_2x2"],
            "matrix_column_major_4x4_dsl": rec["matrix_column_major_4x4_dsl"],
            "matrix_dsl_string": rec["matrix_dsl_string"],
            "matrix_note": "Transform.matrix 写入的是组合变换的**线性部分**；"
                           "枢轴 (60,60) 由 alignment=\"CENTER\" 承担，"
                           "矩阵平移列取 0（实测：再写一次平移会被叠加）。",
            "cell_index": rec["cell_index"], "cell_box_px": rec["cell_box_px"],
            "cell_center_px": rec["cell_center_px"],
            "local_origin_px": rec["local_origin_px"],
            "final_bounding_box_px": rec["final_bounding_box_px"],
            "clipped_by_cell": rec["clipped_by_cell"],
        } for rec in recs],
        "geometry": [{
            "id": rec["id"],
            "rectangles": [{
                "color": rc["color"], "source_xywh": rc["source_xywh"],
                "local_corners_source_order": rc["local_corners_tl_tr_br_bl"],
                "local_corners_after_transform": rc["transformed_local"],
                "canvas_corners_tl_tr_br_bl": rc["canvas_corners_tl_tr_br_bl"],
            } for rc in rec["stamp_geometry"]["rectangles"]],
            "dot": rec["stamp_geometry"]["dot"],
            "final_bounding_box_px": rec["final_bounding_box_px"],
        } for rec in recs],
        "order_sensitivity": {
            "pair": ["T07", "T08"],
            "T07_operations": ["mirror_horizontal", "rotate_clockwise_deg 90"],
            "T08_operations": ["rotate_clockwise_deg 90", "mirror_horizontal"],
            "T07_result": "x' = −y + 120, y' = −x + 120（关于 x+y=120 的反对角线反射）",
            "T08_result": "x' = y, y' = x（关于 x=y 的主对角线反射）",
            "differ": True,
            "evidence": "两格的组合矩阵不同，图中并排显示，图例说明文字另写明各自结果",
        },
        "verification": [],
        "outputs": [{"kind": "png", "filename": "transform-atlas.png",
                     "dsl": "transform-atlas.snapshot", "width": W, "height": H},
                    {"kind": "json", "filename": "geometry-audit.json"}],
    }
    (d / "geometry-audit-raw.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2),
                                               encoding="utf-8")
    for rec in recs:
        bb = rec["final_bounding_box_px"]
        print(rec["id"], rec["matrix_dsl_string"][:44] + "...",
              "bbox", [round(v, 1) for v in bb], "clip" if rec["clipped_by_cell"] else "ok")
    print("cells:", len(recs), "| dsl bytes:", len(dsl.encode()))


if __name__ == "__main__":
    main()
