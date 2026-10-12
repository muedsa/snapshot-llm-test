"""A09 generator: twelve asymmetric transform specimens.

Computes the composite 4x4 column-major matrix for every entry of
tasks/A09-transform-atlas/inputs/transforms.json, then emits the full Snapshot DSL
(1600x1200, 4x3 cells of 300x250 with 32px gutters) plus the raw geometry data that
geometry-audit.json is built from.

Conventions established from the DSL docs (snapshot.muedsa.com/reference/parser-tags):
  * Transform.matrix is a column-major 4x4, flat order
        (a, b, 0, 0, c, d, 0, 0, 0, 0, 1, 0, tx, ty, 0, 1)
    where the local x axis maps to (a, b) and the local y axis maps to (c, d); this is
    the same flat layout A07/A08 verified with rotated line segments.
  * Transform only changes paint coordinates, so the matrix does the whole
    local->canvas mapping and the shapes keep their stamp.json coordinates untouched.
"""
from __future__ import annotations

import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
SHARED = os.path.join(ROOT, "tmp", "20261003-114508-flashmax", "_suite", "shared")
sys.path.insert(0, SHARED)
from dslkit import text_width, CJK, MONO  # noqa: E402

TASK_DIR = os.path.join(ROOT, "tasks", "A09-transform-atlas")
STAMP = json.load(open(os.path.join(TASK_DIR, "inputs", "stamp.json"), encoding="utf-8"))
TRANSFORMS = json.load(open(os.path.join(TASK_DIR, "inputs", "transforms.json"), encoding="utf-8"))

# ---------------------------------------------------------------- canvas geometry
W, H = 1600, 1200
COLS, ROWS = 4, 3
CW, CH = 300, 250
GAP = 32
GW = COLS * CW + (COLS - 1) * GAP          # 1296
GH = ROWS * CH + (ROWS - 1) * GAP          # 814
GX = (W - GW) // 2                         # 152
GY = (H - GH) // 2                         # 193
PIVOT = np.array(STAMP["pivot"], dtype=float)   # (60, 60)

# ------------------------------------------------------------------- palette
INK = "#0F172AFF"
INK_SOFT = "#475569FF"
MUTED = "#64748BFF"
HEAD_LINE = "#94A3B8FF"
PAGE_BG = "#EEF2F7FF"
CARD = "#FFFFFFFF"
EDGE = "#E2E8F0FF"
TICK = "#CBD5E1FF"
GRID = "#F1F5F9FF"
CROSS = "#E2E8F0FF"
FRAME = "#93C5FDFF"
FRAME_INNER = "#BFDBFEFF"
BBOX = "#0E9F8FFF"
ACCENT = "#1D4ED8FF"

SHORT = {
    "T01": "rot 0°", "T02": "rot 90°", "T03": "rot 180°", "T04": "rot 270°",
    "T05": "mirror H", "T06": "mirror V", "T07": "mirrorH→rot90", "T08": "rot90→mirrorH",
    "T09": "scale 0.75", "T10": "scale 1.25/0.75", "T11": "rot 30°", "T12": "mirrorV→rot30",
}
FULLOP = {
    "T01": "rotate 0°", "T02": "rotate 90°", "T03": "rotate 180°", "T04": "rotate 270°",
    "T05": "mirror_horizontal", "T06": "mirror_vertical", "T07": "mirror_h → rotate 90°",
    "T08": "rotate 90° → mirror_h", "T09": "scale_uniform 0.75", "T10": "scale_xy (1.25, 0.75)",
    "T11": "rotate 30°", "T12": "mirror_v → rotate 30°",
}


def op_matrix(name: str, arg) -> np.ndarray:
    """Linear part of one operation in image coordinates (x right, y down)."""
    if name == "rotate_clockwise_deg":
        t = math.radians(float(arg))
        c, s = math.cos(t), math.sin(t)
        return np.array([[c, -s], [s, c]], dtype=float)
    if name == "mirror_horizontal":       # left-right mirror
        return np.array([[-1.0, 0.0], [0.0, 1.0]])
    if name == "mirror_vertical":         # top-bottom mirror
        return np.array([[1.0, 0.0], [0.0, -1.0]])
    if name == "scale_uniform":
        s = float(arg)
        return np.array([[s, 0.0], [0.0, s]])
    if name == "scale_xy":
        sx, sy = (float(v) for v in arg)
        return np.array([[sx, 0.0], [0.0, sy]])
    raise ValueError(f"unknown operation {name!r}")


def compose(ops) -> np.ndarray:
    """Operations are applied in list order, each about the local pivot."""
    a = np.eye(2)
    for name, arg in ops:
        a = op_matrix(name, arg) @ a
    return a


def flat_matrix(a: np.ndarray, t: np.ndarray) -> str:
    vals = [a[0, 0], a[1, 0], 0, 0, a[0, 1], a[1, 1], 0, 0, 0, 0, 1, 0, t[0], t[1], 0, 1]
    def f(v):
        v = 0.0 if abs(v) < 1e-12 else v
        return f"{v:.6f}".rstrip("0").rstrip(".") if abs(v) < 1e9 else f"{v}"
    return "(" + ",".join(f(v) for v in vals) + ")"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class B:
    """Minimal DSL writer (flat Stack + absolute Positioned, per the suite rules)."""

    def __init__(self) -> None:
        self.p = [f'<Snapshot background="{PAGE_BG}" type="png">',
                  f'<Container width="{W}" height="{H}">',
                  '<Stack alignment="TOP_LEFT" fit="EXPAND">']

    def raw(self, s: str) -> None:
        self.p.append(s)

    def box(self, x, y, w, h, color, radius=None, border=None, extra="") -> None:
        a = f'<Container width="{w}" height="{h}"'
        if color:
            a += f' color="{color}"'
        if radius is not None:
            a += f' borderRadius="{radius}"'
        if border:
            a += f' border="{border}"'
        if extra:
            a += " " + extra
        self.p.append(f'<Positioned left="{x}" top="{y}">{a}/></Positioned>')

    def line(self, x, y, w, h, color) -> None:
        self.p.append(f'<Positioned left="{x}" top="{y}">'
                      f'<Container width="{w}" height="{h}" color="{color}"/></Positioned>')

    def text(self, x, y, s, size, color, weight="NORMAL", family=CJK, maxw=None) -> None:
        body = esc(s)
        a = f'fontSize="{size}" color="{color}" fontFamily="{family}" fontStyle="{weight}"'
        tw = text_width(s, size, mono=(family == MONO))
        if maxw is not None and tw > maxw:
            raise SystemExit(f"text too wide ({tw:.0f}>{maxw}): {s!r}")
        self.p.append(f'<Positioned left="{x}" top="{y}"><Text {a}>{body}</Text></Positioned>')

    def text_right(self, x_end, y, s, size, color, weight="NORMAL", family=CJK) -> None:
        tw = text_width(s, size, mono=(family == MONO))
        self.text(round(x_end - tw), y, s, size, color, weight, family)

    def seg(self, p0, p1, color, th):
        """Rotated bar drawn with its own translation matrix (verified in A07/A08)."""
        x0, y0 = float(p0[0]), float(p0[1])
        x1, y1 = float(p1[0]), float(p1[1])
        dx, dy = x1 - x0, y1 - y0
        length = math.hypot(dx, dy)
        ang = math.atan2(dy, dx)
        c, s = math.cos(ang), math.sin(ang)
        tx = (x0 + x1) / 2 - c * (length / 2) + s * (th / 2)
        ty = (y0 + y1) / 2 - s * (length / 2) - c * (th / 2)
        mat = flat_matrix(np.array([[c, -s], [s, c]]), np.array([tx, ty]))
        self.p.append(f'<Positioned left="0" top="0"><Transform matrix="{mat}">'
                      f'<Container width="{length:.4f}" height="{th}" color="{color}" '
                      f'borderRadius="{th/2}"/></Transform></Positioned>')

    def dashes(self, p0, p1, color, th, dash=9.0, gap=7.0):
        x0, y0 = float(p0[0]), float(p0[1])
        x1, y1 = float(p1[0]), float(p1[1])
        total = math.hypot(x1 - x0, y1 - y0)
        if total <= 0:
            return
        ux, uy = (x1 - x0) / total, (y1 - y0) / total
        d = 0.0
        while d < total:
            e = min(d + dash, total)
            self.seg((x0 + ux * d, y0 + uy * d), (x0 + ux * e, y0 + uy * e), color, th)
            d = e + gap

    def finish(self) -> str:
        self.p += ['</Stack>', '</Container>', '</Snapshot>']
        return "\n".join(self.p) + "\n"


# ------------------------------------------------------------------ computation
def rect_corners(xywh):
    x, y, w, h = xywh
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]


def build_cells():
    cells = []
    for i, t in enumerate(TRANSFORMS):
        col, row = i % COLS, i // COLS
        ox, oy = GX + col * (CW + GAP), GY + row * (CH + GAP)
        center = np.array([ox + CW / 2.0, oy + CH / 2.0])
        a = compose(t["operations"])
        trans = center - a @ PIVOT
        cells.append({
            "id": t["id"], "index": i, "col": col, "row": row,
            "origin": [ox, oy], "center": [float(center[0]), float(center[1])],
            "operations": t["operations"], "short_name": SHORT[t["id"]],
            "full_op": FULLOP[t["id"]], "A": a, "t": trans,
        })
    return cells


def fwd(a, trans, pt):
    v = a @ np.array(pt, dtype=float) + trans
    return [float(v[0]), float(v[1])]


def cell_geometry(cell):
    a, trans = cell["A"], cell["t"]
    rects = []
    pts = []
    for ri, r in enumerate(STAMP["rectangles"]):
        corners = [fwd(a, trans, c) for c in rect_corners(r["xywh"])]
        pts += corners
        rects.append({"index": ri, "color": r["color"], "xywh": r["xywh"], "corners": corners})
    dot = STAMP["dot"]
    dc = fwd(a, trans, dot["center"])
    dradius = float(dot["radius"])
    sv = np.linalg.svd(a, compute_uv=False)
    # ellipse semi axes of the transformed circle
    semi = [float(dradius * s) for s in sv]
    pts += [[dc[0] - dradius, dc[1] - dradius], [dc[0] + dradius, dc[1] + dradius]]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    cell["rects"] = rects
    cell["dot"] = {"center": dc, "radius_xy": semi, "source_center": dot["center"],
                   "source_radius": dradius}
    cell["bbox"] = [min(xs), min(ys), max(xs), max(ys)]
    cell["bbox_size"] = [max(xs) - min(xs), max(ys) - min(ys)]
    return cell


# ------------------------------------------------------------------------ image
def draw(b: B, cells):
    # header band
    b.box(0, 0, W, 168, INK)
    b.text(152, 30, "十二变换标本 · Transform Atlas", 38, "#F8FAFCFF", "BOLD")
    b.text(152, 88, "列主序 4×4 矩阵 · 每步围绕本地 (60,60) · 4 列 × 3 行，每格 300×250，格间 32，整体居中",
           22, "#94A3B8FF")
    b.text(152, 124, "像素坐标 x 向右、y 向下，“顺时针”按图像方向；mirror_horizontal = 左右镜像，mirror_vertical = 上下镜像",
           20, "#64748BFF")
    b.text_right(1448, 34, "stamp 120×120 · pivot (60,60)", 20, "#CBD5E1FF", family=MONO)
    b.text_right(1448, 68, "ticks 25px · bbox ±1.5px", 20, "#64748BFF", family=MONO)

    for cell in cells:
        ox, oy = cell["origin"]
        a, trans = cell["A"], cell["t"]
        b.box(ox, oy, CW, CH, CARD, radius=12, border=f"1 SOLID {EDGE}")
        # ruler ticks on the four inner edges, every 25px
        for k in range(0, CW + 1, 25):
            if k in (0, CW):
                continue
            b.line(ox + k, oy + 2, 1.5, 6, TICK)
            b.line(ox + k, oy + CH - 8, 1.5, 6, TICK)
        for k in range(0, CH + 1, 25):
            if k in (0, CH):
                continue
            b.line(ox + 2, oy + k, 6, 1.5, TICK)
            b.line(ox + CW - 8, oy + k, 6, 1.5, TICK)
        # pivot crosshair (the local (60,60) point lands on the cell centre)
        for k in range(25, CW, 25):
            b.line(ox + k, oy + 42, 1, CH - 62, GRID)
        for k in range(25, CH - 42, 25):
            b.line(ox + 10, oy + 42 + k, CW - 20, 1, GRID)
        b.line(ox + 10, oy + CH / 2 - 0.5, CW - 20, 1, CROSS)
        b.line(ox + CW / 2 - 0.5, oy + 42, 1, CH - 68, CROSS)
        # transformed local coordinate frame of the 120x120 stamp
        for p0, p1 in (((0, 0), (120, 0)), ((120, 0), (120, 120)),
                       ((120, 120), (0, 120)), ((0, 120), (0, 0))):
            b.seg(fwd(a, trans, p0), fwd(a, trans, p1), FRAME, 1.6)
        b.seg(fwd(a, trans, (60, 0)), fwd(a, trans, (60, 120)), FRAME_INNER, 1.2)
        b.seg(fwd(a, trans, (0, 60)), fwd(a, trans, (120, 60)), FRAME_INNER, 1.2)
        # transformed bounding box, dashed, drawn under the specimen; the outline is
        # inflated by 1.5px so it stays visible next to the antialiased ink edge
        x0, y0, x1, y1 = cell["bbox"]
        pad = 1.5
        x0, y0, x1, y1 = x0 - pad, y0 - pad, x1 + pad, y1 + pad
        for p0, p1 in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)),
                       ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
            b.dashes(p0, p1, BBOX, 1.2)
        # the specimen: one Transform carries the whole composite matrix, the four
        # shapes keep their stamp.json coordinates verbatim
        shapes = []
        for r in STAMP["rectangles"]:
            x, y, w, h = r["xywh"]
            shapes.append(f'<Positioned left="{x}" top="{y}">'
                          f'<Container width="{w}" height="{h}" color="{r["color"]}FF"/></Positioned>')
        dcx, dcy = STAMP["dot"]["center"]
        dr = STAMP["dot"]["radius"]
        shapes.append(f'<Positioned left="{dcx - dr}" top="{dcy - dr}">'
                      f'<Container width="{2*dr}" height="{2*dr}" color="{STAMP["dot"]["color"]}FF" '
                      f'shape="CIRCLE"/></Positioned>')
        b.raw(f'<Positioned left="0" top="0"><Transform matrix="{flat_matrix(a, trans)}">'
              f'<Stack alignment="TOP_LEFT" fit="EXPAND">' + "".join(shapes) +
              '</Stack></Transform></Positioned>')
        # labels
        b.text(ox + 14, oy + 8, cell["id"], 22, INK, "BOLD")
        b.text_right(ox + CW - 14, oy + 10, cell["short_name"], 20, INK_SOFT)
        b.text(ox + 14, oy + 212, cell["full_op"], 20, ACCENT, maxw=CW - 28)

    # legend
    ly = 1030
    b.box(152, ly, GW, 142, CARD, radius=12, border=f"1 SOLID {EDGE}")
    sw = [("E54B4B", "R1 (8,8) 28×92"), ("2364DB", "R2 (36,72) 68×28"),
          ("EAB53B", "R3 (64,8) 40×28"), ("111111", "dot (91,49) r8")]
    sx = 174
    for hexc, label in sw:
        b.box(sx, ly + 18, 16, 16, "#" + hexc + "FF", radius=4)
        b.text(sx + 24, ly + 14, label, 20, INK_SOFT)
        sx += 24 + text_width(label, 20) + 34
    b.text(174, ly + 50, "T07 与 T08 操作顺序相反：A(T08) = −A(T07)，两枚标本互为 180° 旋转；T05/T06 的镜面轴分别是竖轴与横轴。",
           20, INK_SOFT)
    b.text(174, ly + 80, "辅助线：四边内侧每 25px 一个刻度，格内 25px 淡格线 · 浅蓝实线=本地 120×120 坐标框（含 u=60/v=60 中线） · 绿色虚线=变换后外接框（外扩 1.5px 绘制）",
           20, MUTED)
    b.text(174, ly + 110, "标本几何直接取自 inputs/stamp.json，画布位置完全由 Transform.matrix 决定；逐点 ±1.5px 像素核对结果见 geometry-audit.json。",
           20, MUTED)


def main() -> None:
    cells = [cell_geometry(c) for c in build_cells()]
    version = sys.argv[1] if len(sys.argv) > 1 else "v1"
    b = B()
    draw(b, cells)
    dsl = b.finish()
    out = os.path.join(HERE, f"transform-atlas.{version}.snapshot")
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(dsl)
    data = {"canvas": [W, H], "grid": {"cols": COLS, "rows": ROWS, "cell": [CW, CH],
                                       "gap": GAP, "origin": [GX, GY]},
            "pivot": STAMP["pivot"], "stamp_size": STAMP["size"],
            "cells": [{k: v for k, v in c.items() if k not in ("A", "t")} |
                      {"matrix_16": [float(x) for x in np.array(
                          [c["A"][0, 0], c["A"][1, 0], 0, 0, c["A"][0, 1], c["A"][1, 1], 0, 0,
                           0, 0, 1, 0, c["t"][0], c["t"][1], 0, 1])]}
                      for c in cells]}
    with open(os.path.join(HERE, f"geometry-data.{version}.json"), "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    print("wrote", out, len(dsl), "bytes,", len(cells), "cells")
    for c in cells:
        print(f'  {c["id"]} A={np.round(c["A"],4).tolist()} bbox={[round(v,2) for v in c["bbox"]]} '
              f'size={[round(v,2) for v in c["bbox_size"]]}')


if __name__ == "__main__":
    main()
