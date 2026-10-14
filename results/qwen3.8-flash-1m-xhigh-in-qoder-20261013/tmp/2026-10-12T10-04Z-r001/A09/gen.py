"""A09 - twelve asymmetric transform specimens, 1600x1200.

Composes each transform list into one column-major 4x4 matrix about the stamp's
local pivot (60,60) and applies it through <Transform matrix=...>, so no shape
coordinate is ever rewritten by hand.

Run from the suite task root:
  python tmp/<run_id>/A09/gen.py --ver v001
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
sys.path.insert(0, str(ROOT / "tmp" / "2026-10-12T10-04Z-r001" / "_suite" / "scripts"))

from snap import (  # noqa: E402
    C, Col, Container, Positioned, Row, Snapshot, Stack, Text, Transform, label, num,
)

RUN = "2026-10-12T10-04Z-r001"
TASK = "A09"
IN_DIR = ROOT / "tasks" / "A09-transform-atlas" / "inputs"
OUT_DIR = ROOT / "outputs" / RUN / TASK
TMP_DIR = ROOT / "tmp" / RUN / TASK

FONT = "Noto Sans CJK SC,Inter"
MONO = "Noto Sans Mono CJK SC,DejaVu Sans Mono"
stamp = json.loads((IN_DIR / "stamp.json").read_text(encoding="utf-8"))
TRANSFORMS = json.loads((IN_DIR / "transforms.json").read_text(encoding="utf-8"))

SW, SH = stamp["size"]
PX, PY = stamp["pivot"]
RECTS = stamp["rectangles"]
DOT = stamp["dot"]

CELL_W, CELL_H, GAP = 300, 250, 32
COLS, ROWS = 4, 3
GRID_W = COLS * CELL_W + (COLS - 1) * GAP          # 1296
GRID_H = ROWS * CELL_H + (ROWS - 1) * GAP          # 814
W, H = 1600, 1200
OX = (W - GRID_W) / 2                              # 152
OY = 138

BG = "#0A101E"
CELL_BG, CELL_EDGE = "#101B33", "#26385C"
TXT, TXT_2, TXT_3 = "#F2F6FC", "#A6B8D4", "#6E82A2"
GUIDE, AXIS = "#1D2B47", "#3A5480"

SHORT = {
    "T01": "rotate 0°", "T02": "rotate 90°", "T03": "rotate 180°",
    "T04": "rotate 270°", "T05": "mirror H", "T06": "mirror V",
    "T07": "mirror H → rotate 90°", "T08": "rotate 90° → mirror H",
    "T09": "scale 0.75", "T10": "scale 1.25 × 0.75", "T11": "rotate 30°",
    "T12": "mirror V → rotate 30°",
}


def op_matrix(op):
    kind, val = op[0], op[1]
    if kind == "rotate_clockwise_deg":
        t = math.radians(val)          # y-down canvas: +theta is visually clockwise
        c, s = math.cos(t), math.sin(t)
        return [[c, -s], [s, c]]
    if kind == "mirror_horizontal":
        return [[-1.0, 0.0], [0.0, 1.0]]
    if kind == "mirror_vertical":
        return [[1.0, 0.0], [0.0, -1.0]]
    if kind == "scale_uniform":
        return [[float(val), 0.0], [0.0, float(val)]]
    if kind == "scale_xy":
        return [[float(val[0]), 0.0], [0.0, float(val[1])]]
    raise ValueError(f"unknown operation {kind}")


def compose(ops):
    """Operations act in list order: M = M_n ··· M_2 · M_1."""
    m = [[1.0, 0.0], [0.0, 1.0]]
    for op in ops:
        a = op_matrix(op)
        m = [[a[0][0] * m[0][0] + a[0][1] * m[1][0], a[0][0] * m[0][1] + a[0][1] * m[1][1]],
             [a[1][0] * m[0][0] + a[1][1] * m[1][0], a[1][0] * m[0][1] + a[1][1] * m[1][1]]]
    return m


def cell_origin(i):
    r, c = divmod(i, COLS)
    return OX + c * (CELL_W + GAP), OY + r * (CELL_H + GAP)


def build_entry(idx, spec):
    m = compose(spec["operations"])
    gx, gy = cell_origin(idx)
    ccx, ccy = gx + CELL_W / 2, gy + CELL_H / 2
    # final(p) = M·(p - pivot) + cell centre
    mpx = m[0][0] * PX + m[0][1] * PY
    mpy = m[1][0] * PX + m[1][1] * PY
    return {"id": spec["id"], "m": m, "cc": (ccx, ccy), "origin": (gx, gy),
            "tx_abs": ccx - mpx, "ty_abs": ccy - mpy,
            # <Transform> paints relative to the child's layout box, so the
            # translation in the DSL matrix is measured from the cell origin
            "tx_rel": CELL_W / 2 - mpx, "ty_rel": CELL_H / 2 - mpy}


ENTRIES = [build_entry(i, t) for i, t in enumerate(TRANSFORMS)]


def col_major(e):
    m = e["m"]
    return [m[0][0], m[1][0], 0.0, 0.0,
            m[0][1], m[1][1], 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
            e["tx_rel"], e["ty_rel"], 0.0, 1.0]


def fmt_matrix(cm):
    return "(" + ",".join(f"{v:.6f}" if v else "0" for v in cm) + ")"


def transformed_point(e, x, y):
    dx, dy = x - PX, y - PY
    m = e["m"]
    return e["cc"][0] + m[0][0] * dx + m[0][1] * dy, e["cc"][1] + m[1][0] * dx + m[1][1] * dy


def bbox_of(e):
    pts = []
    for r in RECTS:
        x, y, w, h = r["xywh"]
        pts += [(x, y), (x + w, y), (x, y + h), (x + w, y + h)]
    cx, cy = DOT["center"]
    rad = DOT["radius"]
    for ang in range(0, 360, 10):
        pts.append((cx + rad * math.cos(math.radians(ang)),
                    cy + rad * math.sin(math.radians(ang))))
    tp = [transformed_point(e, px, py) for px, py in pts]
    xs, ys = [p[0] for p in tp], [p[1] for p in tp]
    return [min(xs), min(ys), max(xs), max(ys)]


def stamp_node():
    kids = []
    for r in RECTS:
        x, y, w, h = r["xywh"]
        kids.append(Positioned(C(width=num(w), height=num(h), color=r["color"]),
                               left=num(x), top=num(y)))
    d = DOT["radius"] * 2
    kids.append(Positioned(
        C(width=num(d), height=num(d), color=DOT["color"], shape="CIRCLE"),
        left=num(DOT["center"][0] - DOT["radius"]), top=num(DOT["center"][1] - DOT["radius"])))
    return Stack(C(width=num(SW), height=num(SH)), *kids,
                 alignment="TOP_LEFT", clipBehavior="NONE")


# ---------------------------------------------------------------- draw
els = []


def layer(*children, w=W, h=H):
    return Stack(C(width=num(w), height=num(h)), *children,
                 alignment="TOP_LEFT", clipBehavior="HARD_EDGE")


els.append(Positioned(
    Row(C(width="6", height="56", color="#EAB53B", borderRadius="3"), Container(width="16"),
        Col(Text("变换图谱 · 12 个非对称标本", color=TXT, fontSize="34", fontStyle="BOLD",
                 fontFamily=FONT),
            Container(height="6"),
            Text("同一枚 120×120 印章，每步围绕局部 (60,60)；像素坐标 x 向右、y 向下，"
                 "因此“顺时针”按图像方向", color=TXT_2, fontSize="20", fontFamily=FONT),
            crossAxisAlignment="START"),
        crossAxisAlignment="CENTER"),
    left=num(OX), top=num(40)))

for i, e in enumerate(ENTRIES):
    gx, gy = e["origin"]
    ccx, ccy = e["cc"]
    els.append(Positioned(C(width=num(CELL_W), height=num(CELL_H), color=CELL_BG,
                            borderRadius="12", border=f"1 SOLID {CELL_EDGE}"),
                          left=num(gx), top=num(gy)))
    for k in range(1, CELL_W // 30):
        els.append(Positioned(C(width="1", height=num(CELL_H - 2), color=GUIDE),
                              left=num(gx + k * 30), top=num(gy + 1)))
    for k in range(1, CELL_H // 30):
        els.append(Positioned(C(width=num(CELL_W - 2), height="1", color=GUIDE),
                              left=num(gx + 1), top=num(gy + k * 30)))
    els.append(Positioned(C(width=num(CELL_W - 2), height="2", color=AXIS),
                          left=num(gx + 1), top=num(ccy - 1)))
    els.append(Positioned(C(width="2", height=num(CELL_H - 2), color=AXIS),
                          left=num(ccx - 1), top=num(gy + 1)))
    # the specimen itself: one combined matrix, shapes untouched
    els.append(Positioned(
        Transform(stamp_node(), matrix=fmt_matrix(col_major(e))),
        left=num(gx), top=num(gy)))
    els.append(label(gx + 14, gy + 10, e["id"], 22, TXT, anchor="left_top", align="LEFT",
                     width=70, font=MONO, bold=True))
    # NOTE: must not reuse a stamp fill colour here, or the pixel mask in
    # verify.py would pick up the label text instead of only the specimen.
    els.append(label(gx + CELL_W - 14, gy + 12, SHORT[e["id"]], 20, "#FBBF24",
                     anchor="right_top", align="RIGHT", width=CELL_W - 92, font=FONT))
    bb = bbox_of(e)
    els.append(label(gx + 14, gy + CELL_H - 12,
                     f"外接框 {bb[2]-bb[0]:.0f}×{bb[3]-bb[1]:.0f}px", 18, TXT_3,
                     anchor="left_bottom", align="LEFT", width=CELL_W - 28, font=MONO))

LY = OY + GRID_H + 22
LEG_H = 1200 - LY - 26
els.append(Positioned(C(width=num(GRID_W), height=num(LEG_H), color="#0E1830",
                        borderRadius="12", border=f"1 SOLID {CELL_EDGE}"),
                      left=num(OX), top=num(LY)))
els.append(Positioned(
    Col(
        Text("图例与约定", color=TXT, fontSize="22", fontStyle="BOLD", fontFamily=FONT),
        Container(height="10"),
        Row(
            C(width="16", height="16", color=RECTS[0]["color"]), Container(width="6"),
            Text("红竖条 8,8,28,92", color=TXT_2, fontSize="18", fontFamily=FONT),
            Container(width="20"),
            C(width="16", height="16", color=RECTS[1]["color"]), Container(width="6"),
            Text("蓝横条 36,72,68,28", color=TXT_2, fontSize="18", fontFamily=FONT),
            Container(width="20"),
            C(width="16", height="16", color=RECTS[2]["color"]), Container(width="6"),
            Text("金横条 64,8,40,28", color=TXT_2, fontSize="18", fontFamily=FONT),
            Container(width="20"),
            C(width="16", height="16", color=DOT["color"], shape="CIRCLE"),
            Container(width="6"),
            Text(f"黑圆点 圆心 {DOT['center'][0]},{DOT['center'][1]} 半径 {DOT['radius']}",
                 color=TXT_2, fontSize="18", fontFamily=FONT),
            crossAxisAlignment="CENTER"),
        Container(height="10"),
        Text(f"印章左右不对称（红竖条在左、金横条在右上），圆点只落在右上区域，"
             f"镜像与旋转后的朝向都能分辨。每格 {CELL_W}×{CELL_H}、格间 {GAP}，"
             f"网格水平居中（左右各 {OX:.0f}px）；浅线 30px 刻度，十字为格心。",
             color=TXT_2, fontSize="18", fontFamily=FONT, textAlign="LEFT",
             softWrap="true", height="1.3"),
        Container(height="8"),
        Text("12 个标本各自只使用一个列主序 4×4 矩阵作用在原始印章上，未手改任何形状坐标；"
             "T07 与 T08 用同样的两个操作但顺序相反，矩阵与图像均不同。",
             cdata=True, color="#BFD6EE", fontSize="18", fontFamily=FONT, textAlign="LEFT",
             softWrap="true", height="1.3"),
        crossAxisAlignment="START"),
    left=num(OX + 20), top=num(LY + 16), width=num(GRID_W - 40)))

doc = Snapshot(Container(layer(*els), width=num(W), height=num(H), color=BG),
               background=BG, type="png")

# ---------------------------------------------------------------- audit
audit = {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "inputs": {"stamp": "tasks/A09-transform-atlas/inputs/stamp.json",
               "transforms": "tasks/A09-transform-atlas/inputs/transforms.json"},
    "canvas": [W, H],
    "grid": {"cols": COLS, "rows": ROWS, "cell_px": [CELL_W, CELL_H], "gap_px": GAP,
             "grid_px": [GRID_W, GRID_H], "origin": [OX, OY],
             "centred": f"水平居中，左右各留 {OX:.0f}px"},
    "stamp": {"size": [SW, SH], "pivot_local": [PX, PY],
              "rectangles": RECTS, "dot": DOT,
              "asymmetry": "红竖条 x=8 与金横条 x=64 形状位置都不同；圆点 (91,49) 只在右上，"
                           "消除 90°/180° 旋转与镜像之间的朝向歧义"},
    "convention": {
        "coordinate_space": "画布左上原点，x 向右 y 向下，单位像素",
        "clockwise": "y 向下时标准旋转矩阵取正角度即为图像上的顺时针",
        "rotation_matrix": "[[cosθ,-sinθ],[sinθ,cosθ]]，θ 为 clockwise 角度",
        "mirror_horizontal": "[[-1,0],[0,1]] 左右镜像",
        "mirror_vertical": "[[1,0],[0,-1]] 上下镜像",
        "composition": "操作按列表顺序作用：M = M_n·…·M_2·M_1，全部围绕局部 (60,60)",
        "placement": "final(p) = M·(p − pivot) + cell_centre",
        "dsl_translation_note": "Transform 标签的平移相对子节点布局盒，因此矩阵里写的是 "
                                "cell_centre − origin − M·pivot = (cell_w/2, cell_h/2) − M·pivot",
        "matrix_format": "列主序 4×4，16 值，写在 Transform 的 matrix 属性上",
    },
    "specimens": [],
}
for i, e in enumerate(ENTRIES):
    r, c = divmod(i, COLS)
    corners = {}
    for j, rect in enumerate(RECTS):
        x, y, w, h = rect["xywh"]
        loc = [[x, y], [x + w, y], [x + w, y + h], [x, y + h]]
        corners[f"rect_{chr(ord('A') + j)}"] = {
            "local": loc,
            "canvas": [[round(v, 4) for v in transformed_point(e, px, py)]
                       for px, py in loc],
        }
    dc = transformed_point(e, DOT["center"][0], DOT["center"][1])
    bb = bbox_of(e)
    det = e["m"][0][0] * e["m"][1][1] - e["m"][0][1] * e["m"][1][0]
    gx, gy = e["origin"]
    audit["specimens"].append({
        "id": e["id"], "cell": {"row": r, "col": c}, "cell_box_px": [gx, gy, gx + CELL_W,
                                                                     gy + CELL_H],
        "operations": TRANSFORMS[i]["operations"],
        "short_label": SHORT[e["id"]],
        "linear_2x2": [[round(v, 10) for v in row] for row in e["m"]],
        "determinant": round(det, 10),
        "orientation_reversing": det < 0,
        "column_major_4x4": [round(v, 10) for v in col_major(e)],
        "dsl_matrix_attr": fmt_matrix(col_major(e)),
        "absolute_translation": [round(e["tx_abs"], 6), round(e["ty_abs"], 6)],
        "cell_centre_px": [round(e["cc"][0], 2), round(e["cc"][1], 2)],
        "rect_corners": corners,
        "dot_centre_local": DOT["center"],
        "dot_centre_canvas": [round(dc[0], 4), round(dc[1], 4)],
        "transformed_bbox_px": [round(v, 4) for v in bb],
        "bbox_size_px": [round(bb[2] - bb[0], 4), round(bb[3] - bb[1], 4)],
        "fits_inside_cell": (bb[0] >= gx - 1.5 and bb[2] <= gx + CELL_W + 1.5
                             and bb[1] >= gy - 1.5 and bb[3] <= gy + CELL_H + 1.5),
    })

audit["order_sensitivity"] = {
    "pair": ["T07", "T08"],
    "same_operation_set": sorted(map(str, TRANSFORMS[6]["operations"]))
    == sorted(map(str, TRANSFORMS[7]["operations"])),
    "T07_linear": [[round(v, 6) for v in row] for row in ENTRIES[6]["m"]],
    "T08_linear": [[round(v, 6) for v in row] for row in ENTRIES[7]["m"]],
    "matrices_equal": fmt_matrix(col_major(ENTRIES[6])) == fmt_matrix(col_major(ENTRIES[7])),
    "explanation": "T07 先左右镜像再顺时针 90°；T08 先顺时针 90° 再左右镜像。"
                   "同一组操作、相反顺序，得到不同的复合矩阵。",
}
audit["verification"] = {
    "tolerance_px": 1.5,
    "method": "① 解析：对三个矩形的 12 个角点与圆点圆心套用同一个 4×4 矩阵，得期望画布坐标与外接框；"
              "② 像素：读取服务返回的 PNG，在每格内按 #E54B4B / #2364DB / #EAB53B 三种填充色"
              "与 #111111 圆点做精确颜色掩膜，取掩膜外接框并与解析值比较；"
              "反走样产生的半透明边缘像素不进入掩膜，按 ±1.5px 例外处理。",
    "pixel_check_results": None,
    "note": "像素核对由同目录 verify.py 在实际渲染图上执行后回填。",
}

OUT_DIR.mkdir(parents=True, exist_ok=True)
(OUT_DIR / "geometry-audit.json").write_text(
    json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

ap = argparse.ArgumentParser()
ap.add_argument("--ver", default="v001")
ap.add_argument("--final", default=None)
a = ap.parse_args()
TMP_DIR.mkdir(parents=True, exist_ok=True)
(TMP_DIR / f"{a.ver}.snapshot").write_text(doc.render() + "\n", encoding="utf-8")
if a.final:
    (ROOT / a.final).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / a.final).write_text(doc.render() + "\n", encoding="utf-8")
print(json.dumps({"ver": a.ver, "T07": fmt_matrix(col_major(ENTRIES[6])),
                  "T08": fmt_matrix(col_major(ENTRIES[7])),
                  "all_fit": all(bbox_of(e)[0] >= e["origin"][0] - 1.5
                                 and bbox_of(e)[2] <= e["origin"][0] + CELL_W + 1.5
                                 for e in ENTRIES)}, ensure_ascii=False))
