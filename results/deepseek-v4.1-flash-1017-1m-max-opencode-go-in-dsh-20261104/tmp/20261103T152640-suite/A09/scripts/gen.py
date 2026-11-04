# -*- coding: utf-8 -*-
"""A09: twelve asymmetric transform specimens (1600x1200)."""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import dslkit as K  # noqa: E402
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "A09"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
OUT.mkdir(parents=True, exist_ok=True)
clock = rep.TaskClock(TASK)

base = SUITE_ROOT / "tasks" / "A09-transform-atlas" / "inputs"
stamp = json.loads((base / "stamp.json").read_text(encoding="utf-8"))
transforms = json.loads((base / "transforms.json").read_text(encoding="utf-8"))
PX, PY = stamp["pivot"]

# ---------------------------------------------------------------- affine helpers
def mat_mul(m2, m1):
    """m2 ∘ m1 for 2D affine (a,b,c,d,tx,ty): x' = a x + c y + tx ; y' = b x + d y + ty"""
    a2, b2, c2, d2, tx2, ty2 = m2
    a1, b1, c1, d1, tx1, ty1 = m1
    return (a2 * a1 + c2 * b1,
            b2 * a1 + d2 * b1,
            a2 * c1 + c2 * d1,
            b2 * c1 + d2 * d1,
            a2 * tx1 + c2 * ty1 + tx2,
            b2 * tx1 + d2 * ty1 + ty2)

def apply(m, x, y):
    a, b, c, d, tx, ty = m
    return (a * x + c * y + tx, b * x + d * y + ty)

def op_matrix(op):
    kind, val = op
    if kind == "rotate_clockwise_deg":
        t = math.radians(val)
        a, b, c, d = math.cos(t), math.sin(t), -math.sin(t), math.cos(t)
    elif kind == "mirror_horizontal":
        a, b, c, d = -1, 0, 0, 1
    elif kind == "mirror_vertical":
        a, b, c, d = 1, 0, 0, -1
    elif kind == "scale_uniform":
        a, b, c, d = val, 0, 0, val
    elif kind == "scale_xy":
        a, b, c, d = val[0], 0, 0, val[1]
    else:
        raise ValueError(kind)
    tx = PX - (a * PX + c * PY)
    ty = PY - (b * PX + d * PY)
    return (a, b, c, d, tx, ty)

def compose(ops):
    m = (1, 0, 0, 1, 0, 0)
    for op in ops:
        m = mat_mul(op_matrix(op), m)
    return m

SHORT = {
    "T01": "旋转 0°", "T02": "旋转 90°（顺时针）", "T03": "旋转 180°", "T04": "旋转 270°",
    "T05": "水平镜像（左右）", "T06": "垂直镜像（上下）", "T07": "先水平镜像 → 再旋转 90°",
    "T08": "先旋转 90° → 再水平镜像", "T09": "等比缩放 ×0.75", "T10": "非等比缩放 ×1.25 / ×0.75",
    "T11": "旋转 30°", "T12": "先垂直镜像 → 再旋转 30°",
}
TINY = {
    "T01": "rotate 0°", "T02": "rotate 90°", "T03": "rotate 180°", "T04": "rotate 270°",
    "T05": "mirror H", "T06": "mirror V", "T07": "mirror H → rotate 90°",
    "T08": "rotate 90° → mirror H", "T09": "scale 0.75", "T10": "scale (1.25, 0.75)",
    "T11": "rotate 30°", "T12": "mirror V → rotate 30°",
}

# ---------------------------------------------------------------- layout
BG = "#F4F6FA"
CARD = "#FFFFFF"
INK = "#111A28"
INK2 = "#46566E"
MUTED = "#7C8DA6"
GRID_LINE = "#C9D6E6"
W, H = 1600, 1200
COLS, ROWS = 4, 3
CW, CH, GAP = 300, 250, 32
GX = (W - (COLS * CW + (COLS - 1) * GAP)) / 2
GY = 152

p: list[str] = []
p.append(K.rect(0, 0, W, 6, color="#E54B4B"))
p.append(K.text(GX, 22, "非对称印章 · 十二变换图谱", size=38, color=INK, bold=True))
p.append(K.text(GX, 74, "每格把 120×120 的印章绕局部 (60,60) 依次施加变换，再把局部中心对齐到格心；"
                         "x 向右、y 向下，因此“顺时针”按图像方向。", size=19, color=INK2))
p.append(K.text(GX, 104, "所有主体均由一条 Transform.matrix（列主序 4×4）绘制，形状坐标未手工改写。",
                size=19, color=MUTED))

def stamp_dsl():
    parts = []
    for r in stamp["rectangles"]:
        x, y, w, h = r["xywh"]
        parts.append(K.rect(x, y, w, h, color=r["color"]))
    d = stamp["dot"]
    parts.append(K.rect(d["center"][0] - d["radius"], d["center"][1] - d["radius"],
                        2 * d["radius"], 2 * d["radius"], color=d["color"], radius=d["radius"]))
    return "".join(parts)

def dashed(x1, y1, x2, y2, color, width=1.5, dash=6, gap=6):
    length = math.hypot(x2 - x1, y2 - y1)
    if length < 0.1:
        return
    ux, uy = (x2 - x1) / length, (y2 - y1) / length
    def seg(a, b):
        if abs(y1 - y2) < 0.01:
            p.append(K.rect(min(a[0], b[0]), y1 - width / 2, abs(b[0] - a[0]), width, color=color))
        else:
            p.append(K.rect(x1 - width / 2, min(a[1], b[1]), width, abs(b[1] - a[1]), color=color))
    t = 0.0
    while t < length:
        t2 = min(t + dash, length)
        seg((x1 + ux * t, y1 + uy * t), (x1 + ux * t2, y1 + uy * t2))
        t = t2 + gap

records = []
for idx, item in enumerate(transforms):
    tid = item["id"]
    col, row = idx % COLS, idx // COLS
    x0 = GX + col * (CW + GAP)
    y0 = GY + row * (CH + GAP)
    m = compose(item["operations"])
    a, b, c, d, tx, ty = m
    # local placement: pivot -> cell centre
    ltx = tx + (CW / 2 - PX)
    lty = ty + (CH / 2 - PY)
    matrix = f"({a:.6f},{b:.6f},0,0,{c:.6f},{d:.6f},0,0,0,0,1,0,{ltx:.4f},{lty:.4f},0,1)"

    p.append(K.rect(x0, y0, CW, CH, color=CARD, radius=14, border="1 SOLID #DCE5F0"))
    # guide cross through the cell centre
    ccx, ccy = x0 + CW / 2, y0 + CH / 2
    dashed(x0 + 12, ccy, x0 + CW - 12, ccy, GRID_LINE)
    dashed(ccx, y0 + 40, ccx, y0 + CH - 12, GRID_LINE)
    for k in range(-3, 4):
        if k == 0:
            continue
        p.append(K.rect(ccx + k * 25 - 0.75, ccy - 6, 1.5, 6, color=GRID_LINE))
        p.append(K.rect(ccx - 6, ccy + k * 25 - 0.75, 6, 1.5, color=GRID_LINE))

    # the specimen
    p.append(f'<Positioned left="{x0:g}" top="{y0:g}">'
             f'<SizedBox width="{CW}" height="{CH}">'
             f'<Transform matrix="{matrix}" alignment="TOP_LEFT">'
             f'<SizedBox width="120" height="120">'
             f'<Stack alignment="TOP_LEFT" clipBehavior="NONE">{stamp_dsl()}</Stack>'
             f'</SizedBox></Transform></SizedBox></Positioned>')

    p.append(K.text(x0 + 14, y0 + 10, tid, size=22, color=INK, bold=True))
    p.append(K.text(x0 + 14, y0 + 38, SHORT[tid], width=CW - 28, size=20, color=INK2, bold=True,
                    allow_wrap=True))
    p.append(K.text(x0 + 14, y0 + CH - 26, TINY[tid], width=CW - 28, size=17, color=MUTED))

    # geometry in canvas coordinates
    rects = []
    for r in stamp["rectangles"]:
        rx, ry, rw, rh = r["xywh"]
        corners = [apply((a, b, c, d, ltx, lty), rx, ry),
                   apply((a, b, c, d, ltx, lty), rx + rw, ry),
                   apply((a, b, c, d, ltx, lty), rx + rw, ry + rh),
                   apply((a, b, c, d, ltx, lty), rx, ry + rh)]
        rects.append({"xywh": [rx, ry, rw, rh], "color": r["color"],
                      "corners_cell": [[round(px, 2), round(py, 2)] for px, py in corners],
                      "corners_canvas": [[round(x0 + px, 2), round(y0 + py, 2)] for px, py in corners]})
    dcx, dcy = apply((a, b, c, d, ltx, lty), *stamp["dot"]["center"])
    xs = [v for r in rects for v in (r["corners_cell"][0][0], r["corners_cell"][1][0],
                                     r["corners_cell"][2][0], r["corners_cell"][3][0])]
    ys = [v for r in rects for v in (r["corners_cell"][0][1], r["corners_cell"][1][1],
                                     r["corners_cell"][2][1], r["corners_cell"][3][1])]
    bbox = [min(xs), min(ys), max(xs), max(ys)]
    records.append({
        "id": tid, "operations": item["operations"], "short_name": SHORT[tid],
        "matrix_column_major": [round(v, 6) for v in (a, b, 0, 0, c, d, 0, 0, 0, 0, 1, 0,
                                                      ltx, lty, 0, 1)],
        "rectangles": rects,
        "dot_center_cell": [round(dcx, 2), round(dcy, 2)],
        "dot_center_canvas": [round(x0 + dcx, 2), round(y0 + dcy, 2)],
        "subject_bbox_cell": [round(v, 2) for v in bbox],
        "subject_bbox_canvas": [round(x0 + bbox[0], 2), round(y0 + bbox[1], 2),
                                round(x0 + bbox[2], 2), round(y0 + bbox[3], 2)],
        "cell_box": [x0, y0, x0 + CW, y0 + CH],
        "fits_cell": bbox[0] >= 0 and bbox[1] >= 0 and bbox[2] <= CW and bbox[3] <= CH,
    })

# ---------------------------------------------------------------- legend strip
LY = GY + ROWS * CH + (ROWS - 1) * GAP + 26
p.append(K.rect(GX, LY, W - 2 * GX, 176, color=CARD, radius=14, border="1 SOLID #DCE5F0"))
p.append(K.text(GX + 22, LY + 14, "图例", size=20, color=INK, bold=True))
# stamp composition
sx = GX + 22
for i, r in enumerate(stamp["rectangles"]):
    p.append(K.rect(sx, LY + 48 + i * 30, 22, 16, color=r["color"], radius=3))
    p.append(K.text(sx + 30, LY + 45 + i * 30, f"{r['color']} · {r['xywh'][2]}×{r['xywh'][3]}",
                    width=200, size=18, color=INK2))
p.append(K.rect(sx + 8, LY + 142, 16, 16, color=stamp["dot"]["color"], radius=8))
p.append(K.text(sx + 30, LY + 139, f"黑点 r={stamp['dot']['radius']} @({stamp['dot']['center'][0]},"
                                   f"{stamp['dot']['center'][1]})", width=220, size=18, color=INK2))

p.append(K.text(GX + 340, LY + 42, "辅助线", size=19, color=INK, bold=True))
for i, line in enumerate([
    "虚线十字 = 格心，即印章局部中心 (60,60) 的落点",
    "短刻度每 25 像素一格，用于目测量级",
    "格子 300×250、间距 32；主体均在格内，未裁切",
]):
    p.append(K.text(GX + 340, LY + 70 + i * 26, line, width=430, size=18, color=INK2))

p.append(K.text(GX + 800, LY + 42, "记号", size=19, color=INK, bold=True))
for i, line in enumerate([
    "rotate：按图像方向顺时针旋转指定角度",
    "mirror H / V：左右 / 上下镜像",
    "scale：等比或 (sx, sy) 非等比缩放",
    "操作按列表顺序施加，均以 (60,60) 为不动点",
]):
    p.append(K.text(GX + 800, LY + 70 + i * 26, line, width=420, size=18, color=INK2))

p.append(K.text(GX + 1240, LY + 42, "矩阵", size=19, color=INK, bold=True))
for i, line in enumerate([
    "列主序 4×4，16 个值",
    "逐角点与外接框",
    "见 geometry-audit.json",
]):
    p.append(K.text(GX + 1240, LY + 70 + i * 26, line, width=210, size=17, color=INK2))
dsl = K.document(W, H, p, background=BG)
path = OUT / "transform-atlas.snapshot"
path.write_text(dsl, encoding="utf-8")
warn = K.drain_warnings()
logger = api.TaskLogger(TASK, TMP)
rec = logger.render(path, OUT / "transform-atlas.png", "atlas v1")
print("render:", rec["http_status"], rec["response_bytes"], rec["elapsed_s"], "s")
for w in warn:
    print(w)
if rec["http_status"] != 200:
    print((TMP / "responses" / f"{rec['id']}.bin").read_text(encoding="utf-8", errors="replace")[:1500])
    raise SystemExit(1)
print("size:", api.measure_png(OUT / "transform-atlas.png"))
api.write_json(TMP / "geom.json", {"records": records, "grid": {"origin": [GX, GY], "cell": [CW, CH],
                                                                "gap": GAP, "rows": ROWS, "cols": COLS}})
print("T07 vs T08 matrices differ:", records[6]["matrix_column_major"] != records[7]["matrix_column_major"])
print("all fit:", all(r["fits_cell"] for r in records))
