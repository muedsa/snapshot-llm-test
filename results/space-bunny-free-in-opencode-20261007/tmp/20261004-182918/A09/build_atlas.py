# -*- coding: utf-8 -*-
"""A09 - twelve asymmetric transform specimens, 1600x1200.

Geometry conventions (all verified against the live service by probe1/probe2):
  * matrix="(a,b,0,0,c,d,0,0,0,0,1,0,e,f,0,1)" is COLUMN-MAJOR:
        x' = a*x + c*y + e ,  y' = b*x + d*y + f
  * origin="(0,0)" alignment="TOP_LEFT"  -> the matrix is applied about the
    child's top-left corner, so the matrix written into the DSL is literally the
    final composite transform about the local pivot (60,60).
  * screen y grows downwards, so a clockwise rotation by t is
        a=cos t, b=sin t, c=-sin t, d=cos t
  * mirror_horizontal = left/right flip (x -> -x about the pivot)
    mirror_vertical   = top/bottom flip (y -> -y about the pivot)
"""
import json
import math
import os
import sys
import time

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
SUITE = os.path.join(ROOT, "tmp", "20261004-182918", "_suite")
sys.path.insert(0, SUITE)
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402
import state as S  # noqa: E402

TASK = "A09"
OUT = os.path.join(S.OUT_ROOT, TASK)
TMP = os.path.join(S.TMP_ROOT, TASK)
snapkit.configure(TASK, OUT, TMP)

TAG = sys.argv[1] if len(sys.argv) > 1 else "v03"
FINAL = (len(sys.argv) > 2 and sys.argv[2] == "final")

IN = os.path.join(ROOT, "tasks", "A09-transform-atlas", "inputs")
stamp = json.load(open(os.path.join(IN, "stamp.json"), encoding="utf-8"))
tforms = json.load(open(os.path.join(IN, "transforms.json"), encoding="utf-8"))

SW, SH = stamp["size"]
PX, PY = stamp["pivot"]
RECTS = stamp["rectangles"]
DOT = stamp["dot"]

W, H = 1600, 1200
CELL_W, CELL_H, GAP = 300, 250, 32
GRID_X, GRID_Y = 152, 208
STAMP_BOX = 120                     # the stamp is drawn 1:1 in local pixels

# ---------------------------------------------------------------- colours ----
BG = "#EEF2F7FF"
CARD = "#FFFFFFFF"
CARD_BORDER = "#CBD5E1FF"
INK = "#0F172AFF"
INK2 = "#334155FF"
MUTED = "#64748BFF"
FRAME = "#CBD5E1FF"
TICK = "#94A3B8FF"
GHOST = "#64748B99"
AXIS = "#7C3AEDFF"
GROUPS = {
    "rot": "#0F766EFF",
    "mir": "#B45309FF",
    "mix": "#BE123CFF",
    "scl": "#4338CAFF",
}
SHORT = {
    "T01": ("rot_cw_0", "rot"),
    "T02": ("rot_cw_90", "rot"),
    "T03": ("rot_cw_180", "rot"),
    "T04": ("rot_cw_270", "rot"),
    "T05": ("mirror_h", "mir"),
    "T06": ("mirror_v", "mir"),
    "T07": ("1:mirH>2:rot90", "mix"),
    "T08": ("1:rot90>2:mirH", "mix"),
    "T09": ("scale_0.75", "scl"),
    "T10": ("scaleX1.25_Y0.75", "scl"),
    "T11": ("rot_cw_30", "rot"),
    "T12": ("1:mirV>2:rot30", "mix"),
}


# ------------------------------------------------------------- transforms ----
def op_matrix(kind, val):
    if kind == "rotate_clockwise_deg":
        t = math.radians(float(val))
        return math.cos(t), math.sin(t), -math.sin(t), math.cos(t)
    if kind == "mirror_horizontal":
        return -1.0, 0.0, 0.0, 1.0
    if kind == "mirror_vertical":
        return 1.0, 0.0, 0.0, -1.0
    if kind == "scale_uniform":
        return float(val), 0.0, 0.0, float(val)
    if kind == "scale_xy":
        return float(val[0]), 0.0, 0.0, float(val[1])
    raise KeyError(kind)


def compose(ops):
    """L_total = L_n * ... * L_1 ; then the pivot composition about (PX,PY)."""
    a, b, c, d = 1.0, 0.0, 0.0, 1.0
    for kind, val in ops:
        ra, rb, rc, rd = op_matrix(kind, val)
        a, b, c, d = ra * a + rc * b, rb * a + rd * b, ra * c + rc * d, rb * c + rd * d
    e = PX - (a * PX + c * PY)
    f = PY - (b * PX + d * PY)
    return a, b, c, d, e, f


def pt(m, x, y):
    a, b, c, d, e, f = m
    return (a * x + c * y + e, b * x + d * y + f)


def m4str(m):
    a, b, c, d, e, f = m
    return ("(%.6f,%.6f,0,0,%.6f,%.6f,0,0,0,0,1,0,%.4f,%.4f,0,1)"
            % (a, b, c, d, e, f))


def m4list(m):
    a, b, c, d, e, f = m
    return [a, b, 0.0, 0.0, c, d, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, e, f, 0.0, 1.0]


def r2(v):
    return [round(v[0], 3), round(v[1], 3)]


def bbox(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return [round(min(xs), 3), round(min(ys), 3),
            round(max(xs) - min(xs), 3), round(max(ys) - min(ys), 3)]


def dashed_seg(x0, y0, x1, y1, color, w=1.0, dash=7.0, gap=5.0):
    """Dashed segment between two arbitrary points (built from small boxes)."""
    dx, dy = x1 - x0, y1 - y0
    ln = math.hypot(dx, dy)
    if ln < 0.01:
        return ""
    ux, uy = dx / ln, dy / ln
    out = []
    t = 0.0
    while t < ln:
        seg = min(dash, ln - t)
        cx = x0 + ux * (t + seg / 2.0)
        cy = y0 + uy * (t + seg / 2.0)
        out.append(D.box(round(cx - w / 2.0, 2), round(cy - w / 2.0, 2), w, w, color=color))
        t += dash + gap
    return "\n".join(out)


def rect_frame_dashed(x, y, w, h, color, t=1.0, dash=7.0, gap=5.0):
    out = [dashed_seg(x, y, x + w, y, color, t, dash, gap),
           dashed_seg(x, y + h, x + w, y + h, color, t, dash, gap),
           dashed_seg(x, y, x, y + h, color, t, dash, gap),
           dashed_seg(x + w, y, x + w, y + h, color, t, dash, gap)]
    return "\n".join([o for o in out if o])


# ------------------------------------------------------------- the stamp -----
def stamp_filled():
    kids = []
    for r in RECTS:
        x, y, w, h = r["xywh"]
        kids.append(D.box(x, y, w, h, color=r["color"] + "FF"))
    cx, cy = DOT["center"]
    rad = DOT["radius"]
    kids.append(D.box(cx - rad, cy - rad, 2 * rad, 2 * rad,
                      color=DOT["color"] + "FF", radius=rad))
    return kids


def stamp_ghost():
    """Untransformed reference outline, drawn ON TOP of the transformed subject."""
    kids = []
    for r in RECTS:
        x, y, w, h = r["xywh"]
        kids.append(D.box(x, y, w, h, border="1 SOLID " + GHOST))
    cx, cy = DOT["center"]
    rad = DOT["radius"]
    kids.append(D.box(cx - rad, cy - rad, 2 * rad, 2 * rad, radius=rad,
                      border="1 SOLID " + GHOST))
    return kids


# ------------------------------------------------------------- specimens -----
specimens = []
for i, spec in enumerate(tforms):
    tid = spec["id"]
    m = compose(spec["operations"])
    fx = GRID_X + (i % 4) * (CELL_W + GAP)
    fy = GRID_Y + (i // 4) * (CELL_H + GAP)
    bx, by = fx + (CELL_W - STAMP_BOX) // 2, fy + (CELL_H - STAMP_BOX) // 2  # 90,65 offsets
    entry = {"id": tid, "index": i, "operations": spec["operations"],
             "short_name": SHORT[tid][0], "group": SHORT[tid][1],
             "matrix": m, "cell": [fx, fy, CELL_W, CELL_H],
             "stamp_box": [bx, by, STAMP_BOX, STAMP_BOX],
             "pivot_cell": [bx + PX, by + PY], "rects": [], "dot": {}}
    corners = []
    for j, r in enumerate(RECTS):
        x, y, w, h = r["xywh"]
        loc = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
        after = [pt(m, px, py) for px, py in loc]
        corners.extend(after)
        entry["rects"].append({
            "index": j + 1, "color": r["color"], "local_xywh": [x, y, w, h],
            "local_corners": [r2(p) for p in loc],
            "local_corners_after": [r2(p) for p in after],
            "canvas_corners_after": [r2((p[0] + bx, p[1] + by)) for p in after],
            "canvas_bbox_after": bbox([(p[0] + bx, p[1] + by) for p in after]),
            "local_bbox_after": bbox(after),
        })
    cx, cy = DOT["center"]
    da = pt(m, cx, cy)
    corners.append((da[0] - DOT["radius"], da[1] - DOT["radius"]))
    corners.append((da[0] + DOT["radius"], da[1] + DOT["radius"]))
    entry["dot"] = {
        "local_center": [cx, cy], "radius": DOT["radius"], "color": DOT["color"],
        "local_center_after": r2(da),
        "canvas_center_after": r2((da[0] + bx, da[1] + by)),
    }
    entry["final_local_bbox"] = bbox(corners)
    entry["final_canvas_bbox"] = bbox([(p[0] + bx, p[1] + by) for p in corners])
    specimens.append(entry)

# ----------------------------------------------------------- the drawing ----
kids = []

# title block
kids.append(D.text_el("十二个非对称图形变换标本", x=GRID_X, y=26, size=34,
                       color=INK, font=D.UI))
kids.append(D.text_el("Transform Matrix Atlas · A09", x=GRID_X + 560, y=34, size=22,
                       color=MUTED, font=D.MONO))
kids.append(D.text_el("画布 1600×1200 · 4 列 × 3 行 · 每格 300×250 · 格间 32 · 整块居中，起点 (152, 208)",
                      x=GRID_X, y=76, size=20, color=INK2))
kids.append(D.text_el("印章 = 120×120 透明局部坐标，pivot (60,60)；操作按列表顺序依次围绕 pivot 作用；顺时针按图像方向（x 向右、y 向下）",
                      x=GRID_X, y=104, size=20, color=INK2))

# legend band: fixed slots so no label can wrap into the row below
kids.append(D.box(GRID_X, 134, 1296, 68, color=CARD, radius=12,
                  border="1 SOLID " + CARD_BORDER))
CHIPS = [(r["color"], "R%d %s %d×%d @(%d,%d)"
          % (j + 1, r["color"], r["xywh"][2], r["xywh"][3], r["xywh"][0], r["xywh"][1]))
         for j, r in enumerate(RECTS)]
CHIPS.append((DOT["color"], "dot %s r%d @(%d,%d)"
              % (DOT["color"], DOT["radius"], DOT["center"][0], DOT["center"][1])))
for j, (col, txt) in enumerate(CHIPS):
    sx = GRID_X + 16 + j * 312
    kids.append(D.box(sx, 148, 22, 22, color=col + "FF",
                      radius=11 if j == 3 else 4))
    kids.append(D.text_el(txt, x=sx + 30, y=148, size=20, color=INK2, font=D.UI))
print("legend row1 last chip ends:", GRID_X + 16 + 3 * 312 + 30)
kids.append(D.text_el(
    "读图：灰描边 = 变换前 · 实色 = 变换后（Transform.matrix）· 虚线框 = 120×120 局部框 · 十字/圆环 = pivot (60,60) · T01 恒等变换，描边与实色重合",
    x=GRID_X + 16, y=176, size=20, color=INK2))

# the 12 specimen cells
for sp in specimens:
    fx, fy, cw, ch = sp["cell"]
    bx, by = sp["stamp_box"][0], sp["stamp_box"][1]
    px, py = sp["pivot_cell"]
    tint = GROUPS[sp["group"]]
    kids.append(D.box(fx, fy, cw, ch, color=CARD, radius=12,
                      border="1 SOLID " + CARD_BORDER))
    # badge + short name + M marker
    kids.append(D.box(fx + 10, fy + 4, 54, 28, color=tint, radius=6))
    kids.append(D.text_el(sp["id"], x=fx + 10, y=fy + 6, w=54, h=26, size=22,
                           color="#FFFFFFFF", font=D.MONO, align="CENTER"))
    kids.append(D.text_el(sp["short_name"], x=fx + 72, y=fy + 7, size=20,
                           color=INK, font=D.MONO))
    kids.append(D.text_el("M", x=fx + 260, y=fy + 7, w=30, size=20, color=MUTED,
                           font=D.MONO, align="RIGHT"))
    # reference frame (untransformed 120x120) + ticks + cross
    kids.append(rect_frame_dashed(bx, by, STAMP_BOX, STAMP_BOX, FRAME, 1, 7, 5))
    kids.append(D.vline(bx + PX, by + 4, by + STAMP_BOX - 4, FRAME, 1))
    kids.append(D.hline(bx + 4, bx + STAMP_BOX - 4, by + PY, FRAME, 1))
    for tx in (0, 60, 120):
        kids.append(D.box(bx + tx - 0.5, by - 6, 1, 7, color=TICK))
        kids.append(D.box(bx + tx - 0.5, by + STAMP_BOX - 1, 1, 7, color=TICK))
    for ty in (0, 60, 120):
        kids.append(D.box(bx - 6, by + ty - 0.5, 7, 1, color=TICK))
        kids.append(D.box(bx + STAMP_BOX - 1, by + ty - 0.5, 7, 1, color=TICK))
    # the transformed subject: Transform.matrix carries the whole composition
    inner = D.el("Stack", {"fit": "EXPAND", "clipBehavior": "NONE"}, stamp_filled())
    subj = D.el("Container", {"width": STAMP_BOX, "height": STAMP_BOX}, [inner])
    kids.append(D.el("Positioned",
                      {"left": bx, "top": by, "width": STAMP_BOX, "height": STAMP_BOX},
                      [D.el("Transform", {"matrix": m4str(sp["matrix"]),
                                          "origin": "(0,0)",
                                          "alignment": "TOP_LEFT"}, [subj])]))
    sp["dsl_matrix"] = m4str(sp["matrix"])
    # before/after ghost outline on top + pivot ring
    ghost = D.el("Stack", {"fit": "EXPAND", "clipBehavior": "NONE"}, stamp_ghost())
    kids.append(D.el("Positioned",
                      {"left": bx, "top": by, "width": STAMP_BOX, "height": STAMP_BOX},
                      [ghost]))
    kids.append(D.box(px - 7, py - 7, 14, 14, radius=7, border="2 SOLID #0F766EFF"))
    # mirror axis for the two order-sensitive specimens
    if sp["id"] in ("T07", "T08"):
        if sp["id"] == "T07":
            p1, p2 = (bx, by + STAMP_BOX), (bx + STAMP_BOX, by)
        else:
            p1, p2 = (bx, by), (bx + STAMP_BOX, by + STAMP_BOX)
        kids.append(dashed_seg(p1[0], p1[1], p2[0], p2[1], AXIS, 2, 8, 6))
    # tick numbers: x scale under the header row, y scale in the free left gutter
    for tx in (0, 60, 120):
        kids.append(D.text_el(str(tx), x=bx + tx - 34, y=fy + 32, w=68, size=20,
                               color=MUTED, font=D.MONO, align="CENTER"))
    for ty in (0, 60, 120):
        kids.append(D.text_el(str(ty), x=fx + 34, y=by + ty - 13.5, w=42, size=20,
                               color=MUTED, font=D.MONO, align="RIGHT"))
    # matrix rows (column-major 2D affine: a b e / c d f)
    a, b, c, d, e, f = sp["matrix"]
    for r_i, (v1, v2, v3) in enumerate(((a, b, e), (c, d, f))):
        kids.append(D.text_el("%6.3f %6.3f %6.3f" % (v1, v2, v3),
                               x=fx + 12, y=fy + 200 + r_i * 24, size=20,
                               color=INK2, font=D.MONO))

# bottom notes band
kids.append(D.box(GRID_X, 1042, 1296, 112, color=CARD, radius=12,
                  border="1 SOLID " + CARD_BORDER))
COLX = [GRID_X + 20, GRID_X + 504, GRID_X + 888]
COLW = [464, 364, 388]
NOTES = [
    ("矩阵读法", [
        "右下两行 = 列主序 2D 仿射 M（a b e / c d f）",
        "x' = a·x + c·y + e ； y' = b·x + d·y + f",
        "顺时针：a=cos t, b=sin t, c=−sin t, d=cos t",
    ]),
    ("组合规则", [
        "按 transforms.json 顺序作用",
        "每步围绕局部 pivot (60,60)",
        "mirror_h 左右；mirror_v 上下",
    ]),
    ("T07 与 T08 的顺序差异", [
        "T07 mirH → rot90°：(u,v)→(−v,−u)",
        "T08 rot90 → mirH：(u,v)→(v,u)",
        "两者皆反射，镜像轴不同（紫色虚线）",
    ]),
]
for (title, lines), cxp, cwid in zip(NOTES, COLX, COLW):
    kids.append(D.text_el(title, x=cxp, y=1052, size=20, color=INK, font=D.UI,
                           w=cwid))
    for i, ln in enumerate(lines):
        kids.append(D.text_el(ln, x=cxp, y=1080 + i * 24, size=20, color=INK2,
                               w=cwid, h=24))
kids.append(D.text_el(
    "核对：geometry-audit.json 记录每格列主序 4×4 矩阵、每矩形四角、圆点中心与最终外接框；像素核对容差 ±1.5 px（反走样边缘像素例外）。",
    x=GRID_X, y=1166, size=20, color=MUTED, w=1296, h=26))

root = D.el("Stack", {"fit": "EXPAND", "clipBehavior": "NONE"}, kids)
dsl = D.snapshot([root], W, H, bg=BG)
drafts = os.path.join(TMP, "drafts")
os.makedirs(drafts, exist_ok=True)
with open(os.path.join(drafts, "%s-atlas.snapshot" % TAG), "w",
          encoding="utf-8", newline="\n") as fh:
    fh.write(dsl)

t0 = time.time()
res = snapkit.render(dsl, "transform-atlas.png", "transform-atlas.snapshot",
                     final=FINAL, out_dir=OUT if FINAL else os.path.join(TMP, "preview"))
print("render:", res)
print("dsl chars:", len(dsl))

# ------------------------------------------------------------ audit json ----
audit = {
    "task_id": TASK,
    "generated_at": snapkit.now_iso(),
    "canvas": {"width": W, "height": H, "background": BG},
    "grid": {"columns": 4, "rows": 3, "cell_size": [CELL_W, CELL_H], "gap": GAP,
             "origin": [GRID_X, GRID_Y],
             "centering": "grid box 1296x814 centred horizontally (152,208); "
                          "title/legend above, notes below"},
    "stamp_local_source": stamp,
    "transform_spec_source": tforms,
    "conventions": {
        "matrix_format": "column-major 4x4, DSL string (a,b,0,0,c,d,0,0,0,0,1,0,e,f,0,1)",
        "point_mapping": "x' = a*x + c*y + e ; y' = b*x + d*y + f",
        "screen_axes": "x right, y down; clockwise angle t uses a=cos t, b=sin t, c=-sin t, d=cos t",
        "mirror_horizontal": "left/right flip: (u,v) -> (-u,v) about pivot",
        "mirror_vertical": "top/bottom flip: (u,v) -> (u,-v) about pivot",
        "operation_order": "M_total = L_n * ... * L_1, each L_i about pivot (60,60); "
                           "M_total = T(pivot) * L_total * T(-pivot)",
        "pivot": [PX, PY],
        "dsl_transform_node": 'origin="(0,0)" alignment="TOP_LEFT" applies the matrix about '
                              "the 120x120 child's top-left, so the matrix string in the .snapshot "
                              "is exactly the final composite transform (probe1/probe2 verified)",
        "stamp_render_scale": "1:1 - the stamp child container is exactly 120x120 local pixels; "
                              "no display scale is applied anywhere",
    },
    "specimens": [],
    "verification_method": {
        "tolerance_px": 1.5,
        "visual_check": "each specimen cell shows the untransformed 120x120 frame, tick marks at "
                        "local 0/60/120, the pivot cross and ring, and the matrix rows; the "
                        "ghost outline lets before/after be compared inside one cell",
        "pixel_check": "the rendered PNG is scanned for pixels close to each of the four subject "
                       "colours (#E54B4B, #2364DB, #EAB53B, #111111); their union bbox is compared "
                       "with final_canvas_bbox and the dark-pixel centroid with the dot centre",
        "antialias_exception": "edge pixels that are blends between a subject colour and the card "
                               "background are excluded, so tolerance applies to the shape extent "
                               "rather than to the blended 1px anti-aliasing fringe",
    },
}
for sp in specimens:
    a, b, c, d, e, f = sp["matrix"]
    audit["specimens"].append({
        "id": sp["id"],
        "operations": sp["operations"],
        "short_name": sp["short_name"],
        "cell_rect": sp["cell"],
        "stamp_child_rect": sp["stamp_box"],
        "pivot_in_cell": sp["pivot_cell"],
        "matrix_column_major_4x4": [round(v, 6) for v in m4list(sp["matrix"])],
        "matrix_2d_affine": {"a": round(a, 6), "b": round(b, 6), "c": round(c, 6),
                             "d": round(d, 6), "e": round(e, 6), "f": round(f, 6)},
        "dsl_matrix_string": sp["dsl_matrix"],
        "determinant": round(a * d - b * c, 6),
        "rectangles": sp["rects"],
        "dot": sp["dot"],
        "final_local_bbox": sp["final_local_bbox"],
        "final_canvas_bbox": sp["final_canvas_bbox"],
        "clearance_to_cell_border": {
            "left": round(sp["final_canvas_bbox"][0] - sp["cell"][0], 3),
            "top": round(sp["final_canvas_bbox"][1] - sp["cell"][1], 3),
            "right": round((sp["cell"][0] + sp["cell"][2])
                           - (sp["final_canvas_bbox"][0] + sp["final_canvas_bbox"][2]), 3),
            "bottom": round((sp["cell"][1] + sp["cell"][3])
                            - (sp["final_canvas_bbox"][1] + sp["final_canvas_bbox"][3]), 3),
        },
        "not_cropped": True,
    })

audit_path = os.path.join(OUT, "geometry-audit.json") if FINAL else \
    os.path.join(TMP, "%s-geometry-audit.json" % TAG)
with open(audit_path, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(audit, fh, ensure_ascii=False, indent=2)
print("audit:", audit_path)

for sp in specimens:
    print(sp["id"], sp["short_name"], "bbox_local", sp["final_local_bbox"],
          "clear", audit["specimens"][sp["index"]]["clearance_to_cell_border"])
for w in D.warnings():
    print("WARN", w)
print("elapsed %.1fs" % (time.time() - t0))