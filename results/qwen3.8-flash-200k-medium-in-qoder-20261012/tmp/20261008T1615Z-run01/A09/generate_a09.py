"""A09: 1600x1200 transform atlas, 4 columns x 3 rows of 300x250 specimen cells.

Single source of truth: tmp/<run_id>/A09/plan_a09.json (built by plan_a09.py from
inputs/stamp.json + inputs/transforms.json). The picture and geometry-audit.json both
come from that table, so a printed matrix can never disagree with a drawn pixel.

Rules this file enforces before any DSL is emitted:
  * every subject is the *original* 120x120 stamp (3 rectangles + dot, coordinates
    untouched) drawn through one Transform.matrix -> no hand-edited shape geometry;
  * Transform alignment="CENTER" puts the matrix origin on the child centre, which is
    the stamp-local pivot (60,60), and the child box is positioned so that point lands
    on the cell centre;
  * the transformed bbox keeps a positive margin inside its stage (nothing is clipped);
  * T07/T08 carry their operation order in the caption because their matrices differ;
  * every text box passes the pre-render fit gate (labels >= 20pt).
"""
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(ROOT / "tmp" / RID / "_suite" / "scripts"))
from dslkit import Doc, TextFit, n  # noqa: E402

TASK = "A09"
TEMP = ROOT / "tmp" / RID / TASK
OUT = ROOT / "outputs" / RID / TASK
VERSION = os.environ.get("DSL_VERSION", "v01")

plan = json.loads((TEMP / "plan_a09.json").read_text(encoding="utf-8"))
stamp, cells = plan["stamp"], plan["cells"]

W, H = 1600, 1200
GX, GY = plan["canvas"]["grid"]["origin"]
CW, CH, GAP = 300, 250, 32
PITCH = 20                                  # tick grid pitch, px

BG = "#0A1120"
PANEL = "#0F1A2E"
PANEL_LINE = "#26374F"
STAGE = "#E7EDF7"
STAGE_LINE = "#C2CCDE"
GRID_MINOR = "#D5DEEB"            # v04: the 20px grid sat almost as dark as the
GRID_MAJOR = "#BCC8DA"            # specimen and read as clutter (crop QA)
STAGE_TICK = "#7B8FAC"
AXIS = "#44597A"
INK = "#F1F5F9"
DIM = "#9FB0C9"
FAINT = "#7086A6"
ACCENT = "#38BDF8"
BBOX = "#34D399"
VIOLET = "#A78BFA"
GREEN = "#34D399"

p = Doc(W, H, bg=BG)
fit = TextFit()

HDR_BOT = 150
LEG_TOP = GY + 3 * CH + 2 * GAP + 20        # 1027

# ---------------------------------------------------------------- header
p.label(GX, 28, 860, 46, "十二个非对称图形变换标本 · 一格一个组合矩阵", INK, 34, "BOLD")
sub = "4 列 × 3 行 · 每格 300×250 · 间隔 32 · 整体居中（left 152 / top 193）"
p.label(GX, 78, 1000, 32, sub, DIM, 22)
fit.check("sub", sub, 22, 1000, 32)
sub2 = "x 向右、y 向下 · 每步绕局部 (60,60) · operations 按列表顺序作用"
p.label(GX, 110, 1000, 28, sub2, FAINT, 20)
fit.check("sub2", sub2, 20, 1000, 28)
src = "stamp.json + transforms.json"
p.label(1050, 78, 398, 26, src, DIM, 20, align="END")
fit.check("src", src, 20, 398, 26)
src2 = "审计 geometry-audit.json"
p.label(1050, 108, 398, 26, src2, FAINT, 20, align="END")
fit.check("src2", src2, 20, 398, 26)
p.line(GX, HDR_BOT, W - GX, HDR_BOT, 1, PANEL_LINE)

# ---------------------------------------------------------------- cells
def positioned(x, y, w, h, inner):
    return (f'<Positioned left="{n(x)}" top="{n(y)}" width="{n(w)}" '
            f'height="{n(h)}">{inner}</Positioned>')


def stamp_body():
    """The untouched stamp: 120x120 transparent box, shapes at their input coordinates."""
    kids = []
    for r in stamp["rectangles"]:
        x, y, w, h = r["xywh"]
        kids.append(positioned(x, y, w, h, p.box(w, h, color=r["color"])))
    d = stamp["dot"]
    dx, dy, rr = d["center"][0], d["center"][1], d["radius"]
    kids.append(positioned(dx - rr, dy - rr, 2 * rr, 2 * rr,
                           p.box(2 * rr, 2 * rr, color=d["color"], radius=rr)))
    return p.box(stamp["size"][0], stamp["size"][1],
                 inner='<Stack alignment="TOP_LEFT" clipBehavior="NONE">'
                       + "".join(kids) + "</Stack>")


BODY = stamp_body()


def dash_line(x1, y1, x2, y2, color, dash=7, gap=5, t=1.0):
    """Snapshot has no dashed stroke: emit repeated short segments."""
    if y1 == y2:
        s, e = sorted((x1, x2))
        x = s
        while x < e - 0.25:
            p.line(x, y1, min(x + dash, e), y1, t, color)
            x += dash + gap
    elif x1 == x2:
        s, e = sorted((y1, y2))
        y = s
        while y < e - 0.25:
            p.line(x1, y, x1, min(y + dash, e), t, color)
            y += dash + gap
    else:
        raise ValueError("dash_line only handles axis-aligned segments")


STAGE_INSET_Y = 44
STAGE_H = CH - 2 * STAGE_INSET_Y           # 162
STAGE_X, STAGE_W = 16, CW - 32             # 268
drawn = []

for c in cells:
    x0, y0, _, _ = c["cell_rect_canvas"]
    cx, cy = c["cell_centre_canvas"]
    sx0, sy0 = x0 + STAGE_X, y0 + STAGE_INSET_Y
    sx1, sy1 = sx0 + STAGE_W, sy0 + STAGE_H

    # panel + stage
    p.pos(x0, y0, CW, CH, p.box(CW, CH, color=PANEL, radius=12,
                                border=f"1 SOLID {PANEL_LINE}"))
    p.pos(sx0, sy0, STAGE_W, STAGE_H, p.box(STAGE_W, STAGE_H, color=STAGE, radius=6,
                                           border=f"1 SOLID {STAGE_LINE}"))

    # tick grid: every 20px measured from the pivot, so the crosshair sits on a line
    for k in range(-12, 13):
        gx = cx + k * PITCH
        if sx0 + 2 < gx < sx1 - 2:
            strong = (k % 5 == 0)
            p.line(gx, sy0 + 3, gx, sy1 - 3, 1,
                   GRID_MAJOR if strong else GRID_MINOR)
    for k in range(-8, 9):
        gy = cy + k * PITCH
        if sy0 + 2 < gy < sy1 - 2:
            strong = (k % 5 == 0)
            p.line(sx0 + 3, gy, sx1 - 3, gy, 1,
                   GRID_MAJOR if strong else GRID_MINOR)
    # edge rulers along the stage top and left
    for k in range(-12, 13):
        gx = cx + k * PITCH
        if sx0 <= gx <= sx1:
            p.rect(gx, sy0, 1, 6 if k % 5 else 11, STAGE_TICK)
    for k in range(-8, 9):
        gy = cy + k * PITCH
        if sy0 <= gy <= sy1:
            p.rect(sx0, gy, 6 if k % 5 else 11, 1, STAGE_TICK)

    # dashed crosshair through the pivot
    dash_line(sx0 + 3, cy, sx1 - 3, cy, AXIS, dash=11, gap=7)
    dash_line(cx, sy0 + 3, cx, sy1 - 3, AXIS, dash=11, gap=7)

    # the subject: original stamp geometry, one Transform.matrix, alignment on the pivot
    p.pos(cx - 60, cy - 60, 120, 120,
          f'<Transform matrix="{c["transform_matrix_attribute"]}" alignment="CENTER">'
          + BODY + "</Transform>")

    # pivot ring on top of the subject
    p.pos(cx - 7, cy - 7, 14, 14, p.box(14, 14, radius=7, border=f"1.5 SOLID {VIOLET}"))

    # corner brackets of the transformed bbox (element budget: dashed outline of the
    # whole box blew past the service's 4096-element cap on the first probe). The elbow
    # sits `off` OUTSIDE the box and the arms run back toward it, so no bracket pixel
    # lands on the specimen (v03 had them 6px inside, covering the real corners).
    bx0, by0, bx1, by1 = c["bbox_canvas"]
    arm = min(14.0, (bx1 - bx0) / 3, (by1 - by0) / 3)
    off = 6.0
    for ax, sx in ((bx0, -1), (bx1, 1)):
        for ay, sy in ((by0, -1), (by1, 1)):
            ex, ey = ax + sx * off, ay + sy * off
            p.line(ex, ey, ex - sx * arm, ey, 1.5, BBOX)
            p.line(ex, ey, ex, ey - sy * arm, 1.5, BBOX)

    # labels
    p.label(x0 + 14, y0 + 8, 66, 30, c["id"], ACCENT, 24, "BOLD")
    name = c["short_name"]
    nw = fit.w(name, 20) + 16
    p.label(x0 + CW - 14 - nw, y0 + 10, nw, 28, name, INK, 20, align="END")
    fit.check(f"{c['id']}-name", name, 20, nw, 28)
    det = c["determinant"]
    p.label(x0 + 14, y0 + CH - 34, 120, 26, f"det {det:+.2f}", DIM, 20)
    fit.check(f"{c['id']}-det", f"det {det:+.2f}", 20, 120, 26)
    tagl = f"{bx1 - bx0:.0f}×{by1 - by0:.0f} px"
    p.label(x0 + CW - 14 - 140, y0 + CH - 34, 140, 26, tagl, FAINT, 20, align="END")
    fit.check(f"{c['id']}-tag", tagl, 20, 140, 26)

    # nothing may be clipped: subject bbox must live inside the stage
    assert bx0 >= sx0 and by0 >= sy0 and bx1 <= sx1 and by1 <= sy1, c["id"]
    drawn.append({"id": c["id"], "stage_margin": [round(bx0 - sx0, 1), round(by0 - sy0, 1),
                                                  round(sx1 - bx1, 1), round(sy1 - by1, 1)]})

# ---------------------------------------------------------------- legend
p.line(GX, LEG_TOP - 14, W - GX, LEG_TOP - 14, 1, PANEL_LINE)
lg = "图例 · 印章构件与辅助线"
p.label(GX, LEG_TOP, 300, 28, lg, INK, 22, "BOLD")
fit.check("legend-title", lg, 22, 300, 28)

part_keys = [(r["color"], f"矩形 {i + 1} · xywh {','.join(str(v) for v in r['xywh'])}")
             for i, r in enumerate(stamp["rectangles"])]
part_keys.append((stamp["dot"]["color"], "消对称圆点 r=8"))
guide_keys = [(VIOLET, "pivot 环 (60,60)"), (GRID_MAJOR, "刻度网格 20px"),
              (AXIS, "过 pivot 虚线轴"), (BBOX, "外接框角标 · 外偏 6px")]


def legend_row(items, y):
    x = GX
    for col, text in items:
        w = fit.w(text, 20) + 30
        # a near-black chip on the navy panel is invisible without a light rim
        lum = sum(int(col[i:i + 2], 16) for i in (1, 3, 5)) / 3
        rim = STAGE_LINE if lum < 90 else PANEL_LINE
        p.pos(x, y + 2, 18, 18,
              p.box(18, 18, color=col, radius=4, border=f"1 SOLID {rim}"))
        p.label(x + 24, y, w - 24, 22, text, DIM, 20)
        x += w + 14
    return x


ry1 = LEG_TOP + 32
ry2 = ry1 + 26
right1 = legend_row(part_keys, ry1)
right2 = legend_row(guide_keys, ry2)
assert right1 <= W - GX and right2 <= W - GX, f"legend overflow {right1} / {right2}"

NY = ry2 + 30
NH = 52
note1 = ("T07 与 T08 顺序相反：[[0,−1],[−1,0]] ≠ [[0,1],[1,0]]，"
         "主体形状随之不同（矩阵不可交换）。格内 det 为负即手性翻转。")
p.label(GX, NY, 630, NH, note1, DIM, 20)
fit.check("note1", note1, 20, 630, NH, lines=2)
note2 = ("主体坐标一律未改动，只经 Transform.matrix（列主序 4×4，alignment=CENTER）"
         "变换，圆点同步变换。")
p.label(GX + 656, NY, 630, NH, note2, FAINT, 20, align="END")
fit.check("note2", note2, 20, 630, NH, lines=2)
LEG_BOT = NY + NH

# ---------------------------------------------------------------- gate
dsl = p.dsl()
elements = len(re.findall(r"<[A-Za-z]", dsl))
assert elements <= 4000, f"service caps a document at 4096 elements, got {elements}"
report = {
    "version": VERSION,
    "bytes": len(dsl.encode("utf-8")),
    "elements": elements,
    "text_items": fit.n,
    "fit_problems": fit.problems,
    "cells": len(cells),
    "distinct_matrices": len({c["transform_matrix_attribute"] for c in cells}),
    "min_stage_margin": min(min(d["stage_margin"]) for d in drawn),
    "min_font_pt": min(int(s) for s in re.findall(r'fontSize="(\d+)"', dsl)),
    "legend_right_edges": [round(right1, 1), round(right2, 1)],
    "legend_bottom": LEG_BOT,
}
assert LEG_BOT <= H - 20, f"legend below canvas margin {LEG_BOT}"
(TEMP / "fit-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1),
                                      encoding="utf-8")
(TEMP / f"{VERSION}.snapshot").write_text(dsl, encoding="utf-8")
if VERSION == "final":
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "transform-atlas.snapshot").write_text(dsl, encoding="utf-8")
print(json.dumps(report, ensure_ascii=False))
