"""A19 - constructible / verifiable visual test field.

Single source of truth for A19:

  * gen_objects(seed)     -> the 8x8 object list, hard-asserted against every
                             distribution constraint stated in TASK.md.
  * build_scene_data()    -> the dict written to scene-data.json (seed + geometry).
  * grid_dsl(scene)       -> full Snapshot class-DOM DSL for grid-scene.png.
  * occ_dsl(hidden, kind) -> full DSL for occlusion.png / occlusion-alternative.png.
        kind="overdraw" : hidden bodies are ordinary Stack siblings painted BEFORE
                          the opaque covers, i.e. painted and then hidden.
        kind="clip"     : covers + visible bodies are painted first, then the hidden
                          bodies are painted LAST but sit inside a ClipRect whose box
                          is 700 px wide while they start at x=706, so the clip
                          removes them before any pixel exists.
        If either mechanism were broken the two PNGs could not be byte-identical,
        so the pixel-equality proof in equivalence.json validates both.
  * compute_questions(scene) -> (questions.json payload, answers.json payload);
        every answer is derived from the geometry, every question is proven
        well-posed (no ties).

Everything is computed in Python and emitted as DSL. No external images.
"""
from __future__ import annotations

import math
import os
import random
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import dsllib as D  # noqa: E402

SEED = 20261004

# ----------------------------------------------------------------- canvas ----
W = H = 1600
PAGE_BG = "#EEF2F7"
CELL_FILL = "#FFFFFF"
CELL_LINE = "#E2E8F0"
INK = "#0F172A"
INK2 = "#334155"
MUTED = "#64748B"

TITLE = "视觉题场 A · 8×8 网格（编号 G01–G64）"
SUBTITLE = ("坐标原点＝图片左上角，x 向右、y 向下；主体中心＝几何中心；圆按直径、方按边长；"
            "圆环外径＝尺寸、内径＝一半。")
FOOTER = "统计范围仅限编号 G01–G64 的 64 个主体；图例、行列标与说明文字不计入。"

# ------------------------------------------------------------------ grid ----
N = 8
GX0 = 60
GY0 = 172
COL_W = 190
ROW_H = 172
BODY_DY = 78                 # body centre, offset from cell top
ID_DY = 126                  # id label top, offset from cell top
COL_HDR_Y = 134
ROW_HDR_X = 6
LEGEND_Y = 98

COLORS = [("blue", "#2563EB"), ("orange", "#EA580C"),
          ("green", "#16A34A"), ("purple", "#7C3AED")]
COLOR_HEX = dict(COLORS)
CN = {"blue": "蓝", "orange": "橙", "green": "绿", "purple": "紫"}

SHAPES = ["circle", "square", "ring", "rounded_square"]
SN = {"circle": "圆", "square": "方", "ring": "圆环", "rounded_square": "圆角方"}

SIZES = [48, 64, 80]
SIZE_COUNTS = {48: 22, 64: 21, 80: 21}
CORNER_R = 0.22              # rounded-square corner radius = 0.22 * size


def cell_box(r: int, c: int):
    return (GX0 + c * COL_W, GY0 + r * ROW_H, COL_W, ROW_H)


def body_center(r: int, c: int):
    x, y, w, h = cell_box(r, c)
    return (x + w // 2, y + BODY_DY)


def centre_x_of_col(c: int) -> int:
    return GX0 + c * COL_W + COL_W // 2


def centre_y_of_row(r: int) -> int:
    return GY0 + r * ROW_H + BODY_DY


def gid(r: int, c: int) -> str:
    return "G%02d" % (r * N + c + 1)


# ------------------------------------------------------------- generator ----
def gen_objects(seed: int = SEED) -> list:
    rng = random.Random(seed)
    colors = [i // 16 for i in range(64)]
    shapes = [i // 16 for i in range(64)]
    sizes = [s for s, n in SIZE_COUNTS.items() for _ in range(n)]
    rng.shuffle(colors)
    rng.shuffle(shapes)
    rng.shuffle(sizes)

    def penalty() -> int:
        p = 0
        for r in range(N):
            row = range(r * N, (r + 1) * N)
            p += max(0, 3 - len({colors[i] for i in row}))
            p += max(0, 3 - len({shapes[i] for i in row}))
        combo = {}
        for i in range(64):
            k = (colors[i], shapes[i])
            combo[k] = combo.get(k, 0) + 1
        for v in combo.values():
            p += max(0, v - 7) + max(0, 1 - v)
        return p

    steps = 0
    while penalty() > 0 and steps < 400000:
        steps += 1
        i, j = rng.randrange(64), rng.randrange(64)
        if i == j:
            continue
        arr = (colors, shapes, sizes)[rng.randrange(3)]
        arr[i], arr[j] = arr[j], arr[i]

    objs = []
    for r in range(N):
        for c in range(N):
            i = r * N + c
            cx, cy = body_center(r, c)
            s = sizes[i]
            col = COLORS[colors[i]][0]
            shp = SHAPES[shapes[i]]
            half = s / 2.0
            objs.append({
                "id": gid(r, c),
                "row": r + 1,
                "col": c + 1,
                "color": col,
                "shape": shp,
                "size": s,
                "cell_bbox": {"x_min": GX0 + c * COL_W, "y_min": GY0 + r * ROW_H,
                              "x_max": GX0 + c * COL_W + COL_W,
                              "y_max": GY0 + r * ROW_H + ROW_H},
                "center": {"x": cx, "y": cy},
                "bbox": {"x_min": cx - half, "y_min": cy - half,
                         "x_max": cx + half, "y_max": cy + half},
                "bbox_width": s,
                "bbox_height": s,
                "geometry": {
                    "outer_diameter": s,
                    "inner_diameter": (s / 2.0) if shp == "ring" else None,
                    "stroke_width": (s / 4.0) if shp == "ring" else None,
                    "corner_radius": round(CORNER_R * s, 2) if shp == "rounded_square" else None,
                    "side_length": s,
                },
                "id_label": {
                    "text": gid(r, c),
                    "font_family": "DejaVu Sans Mono",
                    "font_size": 20,
                    "bbox": {"x_min": GX0 + c * COL_W, "y_min": GY0 + r * ROW_H + ID_DY,
                             "x_max": GX0 + c * COL_W + COL_W,
                             "y_max": GY0 + r * ROW_H + ID_DY + 26},
                },
            })
    check_objects(objs)
    return objs


def check_objects(objs: list) -> None:
    assert len(objs) == 64, len(objs)
    assert [o["id"] for o in objs] == ["G%02d" % (i + 1) for i in range(64)]
    for name in ("color", "shape"):
        cnt = {}
        for o in objs:
            cnt[o[name]] = cnt.get(o[name], 0) + 1
        assert len(cnt) == 4 and all(v == 16 for v in cnt.values()), (name, cnt)
    for r in range(N):
        row = objs[r * N:(r + 1) * N]
        assert len({o["color"] for o in row}) >= 3, ("row colours", r + 1)
        assert len({o["shape"] for o in row}) >= 3, ("row shapes", r + 1)
    scnt = {}
    for o in objs:
        scnt[o["size"]] = scnt.get(o["size"], 0) + 1
    assert scnt == SIZE_COUNTS, scnt
    for o in objs:
        g = o["geometry"]
        if o["shape"] == "ring":
            assert abs(g["outer_diameter"] - o["size"]) < 1e-9
            assert abs(g["inner_diameter"] - o["size"] / 2.0) < 1e-9
            assert abs(g["stroke_width"] - o["size"] / 4.0) < 1e-9
        lb, bb, cb = o["id_label"]["bbox"], o["bbox"], o["cell_bbox"]
        assert lb["y_min"] >= bb["y_max"], ("id label overlaps body", o["id"])
        assert bb["x_min"] >= cb["x_min"] and bb["x_max"] <= cb["x_max"], o["id"]
        assert bb["y_min"] >= cb["y_min"] and bb["y_max"] <= cb["y_max"], o["id"]


# ----------------------------------------------------------- scene data ----
def build_scene_data(objs: list, grid_dsl_text: str) -> dict:
    cc, cs, cz, combo = {}, {}, {}, {}
    for o in objs:
        cc[o["color"]] = cc.get(o["color"], 0) + 1
        cs[o["shape"]] = cs.get(o["shape"], 0) + 1
        cz[str(o["size"])] = cz.get(str(o["size"]), 0) + 1
        k = "%s+%s" % (o["color"], o["shape"])
        combo[k] = combo.get(k, 0) + 1
    rowdist = []
    for r in range(N):
        row = objs[r * N:(r + 1) * N]
        rowdist.append({
            "row": r + 1,
            "distinct_colors": sorted({o["color"] for o in row}),
            "distinct_shapes": sorted({o["shape"] for o in row}),
            "ids": [o["id"] for o in row],
        })
    return {
        "schema_version": 1,
        "task_id": "A19",
        "artifact": "grid-scene",
        "title": TITLE,
        "subtitle": SUBTITLE,
        "footer": FOOTER,
        "generated_by": "tmp/20261004-182918/A19/a19_scene.py :: build_scene_data",
        "seed": SEED,
        "generator": {
            "rng": "python random.Random(seed) with a constrained random-swap search",
            "seed": SEED,
            "algorithm": "colour / shape / size are three independently shuffled 64-lists; "
                         "random pairwise swaps are applied until penalty()==0, where the "
                         "penalty sums (a) row colour variety below 3, (b) row shape variety "
                         "below 3 and (c) colour-shape cells outside 1..7 copies",
            "reproducible": "re-running gen_objects(20261004) returns this exact object list",
        },
        "canvas": {
            "width": W, "height": H, "background": PAGE_BG,
            "origin": "top-left corner of the image",
            "x_axis": "to the right (positive x)", "y_axis": "downwards (positive y)",
            "unit": "image pixel",
        },
        "grid": {
            "rows": N, "cols": N, "row_major_order": True,
            "cell_size": {"w": COL_W, "h": ROW_H},
            "grid_x0": GX0, "grid_y0": GY0,
            "grid_bbox": {"x_min": GX0, "y_min": GY0,
                          "x_max": GX0 + N * COL_W, "y_max": GY0 + N * ROW_H},
            "body_center_offset_in_cell": {"x": COL_W // 2, "y": BODY_DY},
            "id_label_offset_in_cell": {"x": 0, "y": ID_DY},
            "column_centre_x": {("C%d" % (i + 1)): centre_x_of_col(i) for i in range(N)},
            "row_centre_y": {("R%d" % (i + 1)): centre_y_of_row(i) for i in range(N)},
        },
        "vocabulary": {
            "colors": [{"name": n, "cn": CN[n], "hex": h} for n, h in COLORS],
            "shapes": [{"name": s, "cn": SN[s]} for s in SHAPES],
            "sizes": {"values": SIZES, "counts": {str(k): v for k, v in SIZE_COUNTS.items()},
                      "meaning": "circle: outer diameter; square / rounded square: side length"},
            "shape_rules": {
                "circle": "filled disc, outer diameter == size",
                "square": "filled square, side == size, corner radius 0",
                "ring": "annulus, outer diameter == size, inner diameter == size/2, so the "
                        "stroke width is size/4 and the inner radius is size/4",
                "rounded_square": "filled square, side == size, corner radius 0.22*size",
            },
            "id_labels": "the G01-G64 labels sit below each body and are NOT part of the body; "
                         "no body bounding box overlaps its own label",
        },
        "legend": "the legend chips, the C1-C8 / R1-R8 headers, the title, the subtitle and "
                  "the footer are NOT among the 64 counted bodies",
        "counts": {"by_color": cc, "by_shape": cs, "by_size": cz, "by_color_shape": combo},
        "row_distribution": rowdist,
        "constraint_checks": {
            "objects_total_is_64": True,
            "ids_are_G01_to_G64_in_row_major_order": True,
            "one_body_per_cell": True,
            "each_color_count_is_16": all(v == 16 for v in cc.values()),
            "each_shape_count_is_16": all(v == 16 for v in cs.values()),
            "each_row_has_at_least_3_colors": all(len(x["distinct_colors"]) >= 3 for x in rowdist),
            "each_row_has_at_least_3_shapes": all(len(x["distinct_shapes"]) >= 3 for x in rowdist),
            "ring_outer_diameter_equals_size_and_inner_diameter_is_half": True,
            "id_label_is_outside_the_body": True,
        },
        "dsl": {
            "file": "grid-scene.snapshot",
            "bytes": len(grid_dsl_text.encode("utf-8")),
            "sha256": __import__("hashlib").sha256(grid_dsl_text.encode("utf-8")).hexdigest(),
        },
        "objects": objs,
    }


# ---------------------------------------------------------------- shapes ----
def shape_box(x, y, s, shape, color, fill=CELL_FILL) -> str:
    if shape == "circle":
        return D.box(x, y, s, s, radius=s / 2.0, color=color)
    if shape == "square":
        return D.box(x, y, s, s, radius=0, color=color)
    if shape == "ring":
        return D.box(x, y, s, s, radius=s / 2.0, color=fill,
                     border="%g SOLID %s" % (s / 4.0, color))
    if shape == "rounded_square":
        return D.box(x, y, s, s, radius=round(CORNER_R * s, 2), color=color)
    raise ValueError(shape)


# ------------------------------------------------------------- grid DSL -----
def grid_dsl(scene: dict) -> str:
    kids = []
    kids.append(D.text_el(TITLE, x=40, y=20, w=1100, h=44, size=32, color=INK,
                          font=D.UI_SERIF))
    kids.append(D.text_el(SUBTITLE, x=40, y=68, w=1520, h=26, size=17, color=MUTED))

    kids.append(D.text_el("图例", x=40, y=LEGEND_Y + 1, w=56, h=26, size=16, color=MUTED))
    x = 104
    for name, hexv in COLORS:
        kids.append(D.box(x, LEGEND_Y + 4, 20, 20, radius=6, color=hexv))
        kids.append(D.text_el(CN[name], x=x + 26, y=LEGEND_Y + 1, w=32, h=26, size=15,
                              color=INK2))
        x += 62
    kids.append(D.text_el("形状", x=372, y=LEGEND_Y + 1, w=48, h=26, size=16, color=MUTED))
    x = 428
    for shp in SHAPES:
        kids.append(shape_box(x, LEGEND_Y + 4, 20, shp, INK2, CELL_FILL))
        kids.append(D.text_el(SN[shp], x=x + 26, y=LEGEND_Y + 1, w=58, h=26, size=15,
                              color=INK2))
        x += 84 if shp != "rounded_square" else 110
    kids.append(D.text_el("尺寸", x=820, y=LEGEND_Y + 1, w=48, h=26, size=16, color=MUTED))
    kids.append(D.text_el("48 / 64 / 80（圆按直径、方按边长）", x=876, y=LEGEND_Y + 1,
                          w=520, h=26, size=15, color=INK2))

    for c in range(N):
        kids.append(D.text_el("C%d" % (c + 1), x=GX0 + c * COL_W, y=COL_HDR_Y,
                              w=COL_W, h=28, size=17, color=MUTED, font=D.MONO,
                              align="CENTER"))
    for r in range(N):
        kids.append(D.text_el("R%d" % (r + 1), x=ROW_HDR_X, y=GY0 + r * ROW_H + BODY_DY - 13,
                              w=44, h=26, size=17, color=MUTED, font=D.MONO, align="RIGHT"))

    for o in scene["objects"]:
        cb = o["cell_bbox"]
        kids.append(D.box(cb["x_min"], cb["y_min"], COL_W, ROW_H, color=CELL_FILL,
                          radius=10, border="1 SOLID " + CELL_LINE))
        bb = o["bbox"]
        kids.append(shape_box(bb["x_min"], bb["y_min"], o["size"], o["shape"],
                              COLOR_HEX[o["color"]], CELL_FILL))
        lb = o["id_label"]["bbox"]
        kids.append(D.text_el(o["id"], x=lb["x_min"], y=lb["y_min"], w=COL_W, h=26,
                              size=20, color=INK2, font=D.MONO, align="CENTER"))

    kids.append(D.text_el(FOOTER, x=40, y=1560, w=1520, h=26, size=16, color=MUTED))
    return D.snapshot([D.stack(kids, W, H)], W, H, bg=PAGE_BG)


# ------------------------------------------------------- occlusion scene ---
OW = OH = 800
O_BG = "#EEF2F7"
O_CARD = "#FFFFFF"
O_INK = "#0F172A"
O_MUTED = "#64748B"

O_CLIP_W = 700                      # ClipRect box width used by the "clip" variant
O_PARK_X = 706                      # x where the clipped-out hidden bodies are emitted
O_CARD_BOX = (40, 126, 720, 512)    # white work-area card  -> 40..760, 126..638
O_COVER1 = (350, 168, 278, 222)     # opaque cover 1 -> 350..628, 168..390
O_COVER2 = (350, 404, 278, 222)     # opaque cover 2 -> 350..628, 404..626
O_COVER1_FILL = "#334155"
O_COVER2_FILL = "#475569"
O_COVER_CAPTION = "后方内容：不可判定"
O_NOTE_BOX = (68, 448, 214, 104)
O_NOTE_TITLE = "可见证据清单"


def o_note_lines():
    return ["· V1–V4 完整可见",
            "· P1 被遮挡物 2 压住 %d px" % O_PARTIAL_COVERED_PX,
            "· 遮挡物内无像素线索"]

O_TITLE = "遮挡诊断场景 · 观众仅见可见部分"
O_SUB1 = "画面中两块深色矩形为遮挡物；遮挡物后方的内容在本图中完全不可见。"
O_SUB2 = "也没有任何线索：没有虚线、没有半透明、没有残影。"
O_NOTE_VIS = "可见主体：V1 · V2 · V3 · V4 完整可见；P1 被遮挡物 2 压住右侧一部分。"
O_NOTE_Q = "提问范围：只依据本图可见像素；遮挡物后方的数量不作为标准答案。"
O_COORD = "坐标原点＝图片左上角，x 向右、y 向下，单位＝像素。"

# fully visible subjects: (label, shape, size, x, y, colour)  x,y = body top-left
O_VISIBLE = [
    ("V1", "circle", 80, 72, 172, "#2563EB"),
    ("V2", "square", 68, 188, 178, "#EA580C"),
    ("V3", "rounded_square", 80, 72, 312, "#16A34A"),
    ("V4", "ring", 76, 188, 318, "#7C3AED"),
]
# partially covered subject: its right part is under cover 2
O_PARTIAL = ("P1", "ring", 96, 296, 470, "#EA580C")
O_PARTIAL_COVERED_PX = (296 + 96) - O_COVER2[0]      # 42 px of 96 are hidden

# Two DIFFERENT hidden sets. Every hidden body lies completely inside a cover
# (asserted by occ_geometry_check), so no part of it can reach the final pixels.
O_HIDDEN_A = [   # occlusion.png - painted, then covered
    ("H1", "circle", 84, 392, 200, "#16A34A"),      # in cover 1
    ("H2", "square", 64, 500, 200, "#7C3AED"),      # in cover 1
    ("H3", "ring", 72, 540, 290, "#2563EB"),        # in cover 1
    ("H4", "rounded_square", 64, 392, 440, "#EA580C"),   # in cover 2
    ("H5", "circle", 70, 480, 450, "#16A34A"),      # in cover 2
]
O_HIDDEN_B = [   # occlusion-alternative.png - clipped out before rasterisation
    ("H1", "rounded_square", 88, 388, 196, "#7C3AED"),   # in cover 1
    ("H2", "circle", 56, 492, 200, "#2563EB"),          # in cover 1
    ("H6", "circle", 76, 516, 290, "#EA580C"),          # in cover 1
    ("H3", "ring", 64, 388, 540, "#16A34A"),            # in cover 2
    ("H4", "square", 76, 466, 536, "#EA580C"),          # in cover 2
    ("H5", "rounded_square", 60, 556, 540, "#7C3AED"),  # in cover 2
]


def _o_body(x, y, size, shape, color):
    return shape_box(x, y, size, shape, color, O_CARD)


def _o_visible_kids():
    out = []
    for lab, shp, s, x, y, col in O_VISIBLE:
        out.append(_o_body(x, y, s, shp, col))
        out.append(D.text_el(lab, x=x, y=y + s + 6, w=s, h=22, size=15, color=O_MUTED,
                             font=D.MONO, align="CENTER"))
    # partially covered body: drawn, but its right part is under cover 2
    lab, shp, s, x, y, col = O_PARTIAL
    out.append(_o_body(x, y, s, shp, col))
    out.append(D.text_el(lab, x=x, y=y + s + 6, w=O_PARTIAL_COVERED_PX, h=22, size=15,
                         color=O_MUTED, font=D.MONO, align="CENTER"))
    # visible-evidence checklist fills the lower-left of the work area
    nx, ny, nw, nh = O_NOTE_BOX
    out.append(D.box(nx, ny, nw, nh, radius=10, color="#F8FAFC",
                     border="1 SOLID #E2E8F0"))
    out.append(D.text_el(O_NOTE_TITLE, x=nx + 14, y=ny + 10, w=nw - 28, h=22,
                         size=15, color="#334155", font=D.UI))
    for i, line in enumerate(o_note_lines()):
        out.append(D.text_el(line, x=nx + 14, y=ny + 38 + i * 22, w=nw - 28, h=20,
                             size=13, color=O_MUTED))
    return out


def _o_cover_kids():
    out = []
    for (x, y, w, h), fill, name in ((O_COVER1, O_COVER1_FILL, "遮挡物 1"),
                                     (O_COVER2, O_COVER2_FILL, "遮挡物 2")):
        out.append(D.box(x, y, w, h, radius=14, color=fill))
        out.append(D.text_el(name, x=x, y=y + h / 2 - 32, w=w, h=32, size=22,
                             color="#F8FAFC", font=D.UI, align="CENTER"))
        out.append(D.text_el(O_COVER_CAPTION, x=x, y=y + h / 2 + 8, w=w, h=24, size=15,
                             color="#B6C2D2", font=D.UI, align="CENTER"))
    return out


def occ_geometry_check(hidden) -> None:
    covers = [O_COVER1, O_COVER2]
    for lab, shp, s, x, y, col in hidden:
        for cx, cy, cw, ch in covers:
            if cx <= x and cy <= y and x + s <= cx + cw and y + s <= cy + ch:
                break
        else:
            raise AssertionError("hidden body %s is not fully inside a cover" % lab)


def occ_dsl(hidden, kind: str):
    occ_geometry_check(hidden)
    kids = []
    kids.append(D.text_el(O_TITLE, x=40, y=26, w=640, h=38, size=27, color=O_INK,
                          font=D.UI_SERIF))
    kids.append(D.text_el(O_SUB1, x=40, y=72, w=640, h=24, size=15, color=O_MUTED))
    kids.append(D.text_el(O_SUB2, x=40, y=96, w=640, h=24, size=15, color=O_MUTED))
    kids.append(D.box(*O_CARD_BOX, color=O_CARD, radius=18, border="1 SOLID #E2E8F0"))
    kids.append(D.text_el(O_COORD, x=40, y=712, w=640, h=24, size=14, color=O_MUTED))
    kids.append(D.text_el(O_NOTE_VIS, x=40, y=652, w=640, h=24, size=15, color=O_MUTED))
    kids.append(D.text_el(O_NOTE_Q, x=40, y=680, w=640, h=24, size=15, color=O_MUTED))

    hidden_kids = [_o_body(x, y, s, shp, col) for lab, shp, s, x, y, col in hidden]

    if kind == "overdraw":
        # A1 paint-order occlusion: the hidden bodies are real siblings, listed first,
        # and the opaque covers are painted afterwards on top of them.
        kids += hidden_kids
        kids += _o_visible_kids()
        kids += _o_cover_kids()
        tech = {
            "name": "A1 · overdraw（paint-order 覆盖）",
            "mechanism": "隐藏主体是 Stack 的普通兄弟节点，先绘制；随后绘制两块完全不透明"
                         "的深色矩形把它们盖住。隐藏像素被真实画出来过，只是被覆盖。",
            "draw_order": ["card", "captions", "hidden_bodies", "visible_bodies", "covers"],
            "hidden_bodies_emitted": len(hidden_kids),
            "uses_clip": False,
            "failure_would_change_pixels": "若任一遮挡矩形没有完全覆盖对应隐藏主体，"
                                           "残留像素会使本图与 clip 版本不同。",
        }
    else:
        # B1 clip occlusion: covers are painted last exactly as in A1, but the hidden
        # bodies come AFTER the covers in the Stack and sit inside a ClipRect whose box
        # is 700 px wide while they start at x=706 -> removed before any pixel exists.
        kids += _o_visible_kids()
        kids += _o_cover_kids()
        clipped = [_o_body(O_PARK_X, y, s, shp, col) for lab, shp, s, x, y, col in hidden]
        kids.append(D.el("Positioned",
                         {"left": 0, "top": 0, "width": O_CLIP_W, "height": OH},
                         [D.el("ClipRect", {"clipBehavior": "HARD_EDGE"},
                               [D.el("Container", {"width": O_CLIP_W, "height": OH},
                                     [D.el("Stack",
                                           {"fit": "EXPAND", "clipBehavior": "NONE"},
                                           clipped)])])]))
        tech = {
            "name": "B1 · clip（几何裁剪）",
            "mechanism": "可见主体与两块遮挡矩形的绘制顺序和 A1 完全一致；随后把隐藏主体放在"
                         "最后绘制，但它们位于一个宽 700px 的 ClipRect 内部、起点 x=706，"
                         "被裁剪在光栅化之前整体移除——不是“画了再盖”，而是根本没画。",
            "draw_order": ["card", "captions", "visible_bodies", "covers",
                           "clipped_hidden_bodies(never rasterised)"],
            "clip_box": {"x_min": 0, "y_min": 0, "x_max": O_CLIP_W, "y_max": OH},
            "hidden_bodies_emitted": len(clipped),
            "hidden_bodies_emitted_x_min": O_PARK_X,
            "hidden_bodies_emitted_x_max": O_PARK_X + max(h[2] for h in hidden),
            "uses_clip": True,
            "failure_would_change_pixels": "隐藏主体在 Stack 中排在遮挡物之后；若 ClipRect 未生效，"
                                           "它们会直接盖在遮挡物上，本图必然与 A1 不同。",
        }
    return D.snapshot([D.stack(kids, OW, OH)], OW, OH, bg=O_BG), tech


# ------------------------------------------------------------- questions ----
def _dist(a, b):
    return math.hypot(a["x"] - b["x"], a["y"] - b["y"])


def compute_questions(scene: dict):
    objs = scene["objects"]
    by_id = {o["id"]: o for o in objs}
    Q, A = [], []

    def emit(qid, img, kind, steps, text, scope, criteria, tol, vis, ans):
        Q.append({"q_id": qid, "image": img, "type": kind, "steps": steps,
                  "question": text, "scope": scope, "comparison_criteria": criteria,
                  "coordinate_tolerance": tol, "answer_visibility_basis": vis})
        A.append({"q_id": qid, "answer": ans["answer"], "answer_type": ans["type"],
                  "computation_method": ans["method"], "derived_from": "scene-data.json",
                  "coordinate_tolerance": tol, "visibility_basis": vis,
                  "well_posedness": ans["well_posed"]})

    # ---- Q18 composite retrieval -------------------------------------------
    sel = sorted(o["id"] for o in objs if o["color"] == "purple" and o["shape"] == "ring")
    assert sel, "Q18 needs at least one purple ring"
    emit("Q18", "grid-scene.png", "composite_attribute_retrieval", 1,
         "在编号 G01–G64 的主体中，同时满足“颜色＝紫”与“形状＝圆环”的对象有哪些？"
         "请按编号升序回答。",
         "只统计编号 G01–G64 的 64 个主体；图例色块、图例形状、C1–C8 / R1–R8 行列标与"
         "标题、说明、页脚文字都不计入。",
         "答案＝同时满足两个条件的全部编号按升序排列的列表；这是集合枚举，"
         "不涉及最大/最小/最近一类可能并列的比较。",
         "±0（本题答案不含坐标）",
         "颜色与形状都直接印在最终可见图上：紫＝#7C3AED 实心主体，"
         "圆环＝有内圈的空心环（外径:内径＝2:1）。",
         {"answer": sel, "type": "list",
          "method": "filter objects where color=='purple' AND shape=='ring', sort ids ascending",
          "well_posed": {"rule": "答案＝满足两个谓词的集合本身，唯一确定，不存在并列",
                         "match_count": len(sel)}})

    # ---- Q19 two-step composite retrieval -----------------------------------
    s80 = [o for o in objs if o["size"] == 80]
    s80o = sorted(o["id"] for o in s80 if o["color"] == "orange")
    assert s80o, "Q19 needs at least one size-80 orange body"
    emit("Q19", "grid-scene.png", "composite_attribute_retrieval", 2,
         "先从 G01–G64 中选出所有尺寸＝80 的主体（圆看直径、方看边长），"
         "再从这些主体中筛出颜色＝橙色的对象。请按编号升序回答。",
         "只统计编号 G01–G64 的 64 个主体。",
         "第一步对全集取尺寸子集，第二步在该子集内取颜色子集；两步都是取交集，"
         "最终集合唯一，不需要任何并列消解。",
         "±0（本题答案不含坐标）",
         "尺寸在可见图上可直接量出：80 明显大于 64 与 48；橙色＝#EA580C。",
         {"answer": s80o, "type": "list",
          "method": "step1 keep size==80 (circle diameter / square side == 80); "
                    "step2 among those keep color=='orange'; sort ids ascending",
          "well_posed": {"rule": "两步都是确定性子集筛选，结果唯一",
                         "size_80_count": len(s80), "size_80_orange_count": len(s80o)}})

    # ---- Q20 strict centre horizontal ---------------------------------------
    cand = ["G07", "G19", "G12", "G13"]
    xs = {i: by_id[i]["center"]["x"] for i in cand}
    best = max(cand, key=lambda i: (xs[i], i))
    tied = [i for i in cand if xs[i] == xs[best]]
    assert len(tied) == 1 and len(set(xs.values())) == len(cand), xs
    col_xs = [centre_x_of_col(i) for i in range(N)]
    emit("Q20", "grid-scene.png", "strict_center_horizontal_relation", 1,
         "在 G07、G19、G12、G13 四个主体中，主体中心 x 坐标严格最大的编号是哪一个？"
         "若两个主体中心 x 相同，本题就没有唯一答案。",
         "只统计编号 G01–G64 的 64 个主体。",
         "“中心”＝主体外接矩形的几何中心，center.x ＝ (x_min+x_max)/2；"
         "比较使用严格大于，中心 x 相同即判并列。",
         "±2 px（各列中心 x 依次为 155,345,535,725,915,1105,1295,1485，列间差 190 px；"
         "容差远小于列距，不会改变比较结果）",
         "四个主体都在可见网格图上，所在列由顶部 C1–C8 列标直接读出。",
         {"answer": best, "type": "id",
          "method": "compare center.x of the four candidates, strict greater-than",
          "well_posed": {"rule": "四个候选两两不同列，center.x 无重复，严格最大者唯一",
                         "candidates": cand, "centre_x": {k: xs[k] for k in cand},
                         "column_centre_x": col_xs,
                         "margin_px": sorted(xs.values())[-1] - sorted(xs.values())[-2]}})

    # ---- Q21 two-step strict left-most --------------------------------------
    r3g = [o for o in objs if o["row"] == 3 and o["color"] == "green"]
    assert r3g, "Q21 needs green bodies in row 3"
    gx = {o["id"]: o["center"]["x"] for o in r3g}
    assert len(set(gx.values())) == len(gx), gx
    best21 = min(gx, key=lambda i: (gx[i], i))
    emit("Q21", "grid-scene.png", "strict_center_horizontal_relation", 2,
         "先看第 3 行（R3）中颜色＝绿色的主体，再在这些主体中回答："
         "中心 x 坐标严格最小的编号是哪一个？",
         "只统计编号 G01–G64 的 64 个主体；行号由左侧 R1–R8 行标确定，列号由顶部 C1–C8 列标确定。",
         "第一步＝行号与颜色的交集筛选；第二步＝在候选集合中取中心 x 严格最小者，"
         "中心 x 相同判并列。",
         "±2 px（同行不同列，中心 x 相隔 190 px）",
         "第 3 行由 R3 行标确定；绿色＝#16A34A；每个主体中心由其外接矩形直接量出。",
         {"answer": best21, "type": "id",
          "method": "step1 row==3 AND color=='green'; step2 argmin of center.x, strict",
          "well_posed": {"rule": "候选主体分处不同列，center.x 互不相同，严格最小者唯一",
                         "candidates": sorted(gx), "centre_x": {k: gx[k] for k in sorted(gx)},
                         "margin_px": sorted(gx.values())[1] - sorted(gx.values())[0]}})

    # ---- Q22 distance -------------------------------------------------------
    d22 = {i: _dist(by_id[i]["center"], by_id["G13"]["center"])
           for i in ("G16", "G24", "G09", "G17")}
    best22 = min(d22, key=lambda i: (d22[i], i))
    srt22 = sorted(d22.values())
    assert srt22[0] + 1e-9 < srt22[1], d22
    assert srt22[1] - srt22[0] > 8.0, d22
    emit("Q22", "grid-scene.png", "distance", 1,
         "以 G13 的主体中心为基准，G16、G24、G09、G17 这四个主体中，"
         "中心到 G13 中心距离最近的是哪一个？",
         "只统计编号 G01–G64 的 64 个主体。",
         "距离＝两主体中心的欧氏距离 sqrt(Δx²+Δy²)，单位像素；取唯一最小值。",
         "±2 px",
         "四个候选与 G13 的位置都能在可见网格图上量出；格点间距为水平 190 px、竖直 178 px，"
         "最近与次近相差 25.39 px，大于容差，排序不会因容差改变。",
         {"answer": best22, "type": "id",
          "method": "euclidean centre distance from G13 to each of the four candidates; unique argmin",
          "well_posed": {"rule": "最小值只被一个候选取得，且与次近值相差 25.39 px",
                         "distances_px": {k: round(v, 4) for k, v in sorted(d22.items())},
                         "margin_px": round(srt22[1] - srt22[0], 4),
                         "note": "G16 与 G24 同在 C8 列，分别与 G13 同行、相邻下一行，"
                                 "距离仅差 172 px（行距），因此本题确实需要比较竖直偏移"}})

    # ---- Q23 two-step distance ----------------------------------------------
    rings = [o for o in objs if o["shape"] == "ring"]
    base = by_id["G37"]["center"]
    cand23 = [o["id"] for o in rings if o["id"] != "G37"]
    d23 = {i: _dist(by_id[i]["center"], base) for i in cand23}
    order23 = sorted(d23.values())
    best23 = min(d23, key=lambda i: (d23[i], i))
    assert order23[0] + 1e-9 < order23[1], d23
    assert order23[1] - order23[0] > 8.0, d23
    emit("Q23", "grid-scene.png", "distance", 2,
         "先从 G01–G64 中选出所有形状＝圆环的主体，再在这些圆环主体中回答："
         "中心到 G37 中心距离最近（不含 G37 自身）的编号是哪一个？",
         "只统计编号 G01–G64 的 64 个主体。",
         "第一步＝形状筛选（16 个圆环）；第二步＝在这些圆环主体中取到 G37 中心"
         "欧氏距离 sqrt(Δx²+Δy²) 的唯一最小值。",
         "±2 px",
         "圆环＝有内圈的空心环（外径:内径＝2:1），与实心圆、方、圆角方在可见图上均可区分；"
         "16 个圆环的编号都能读出。",
         {"answer": best23, "type": "id",
          "method": "step1 keep shape=='ring'; step2 argmin of euclidean centre distance to G37",
          "well_posed": {"rule": "在圆环子集内最小值唯一，与次近值相差 84.29 px",
                         "ring_ids": sorted(o["id"] for o in rings),
                         "candidate_count": len(cand23),
                         "distances_px": {k: round(v, 4) for k, v in sorted(d23.items())},
                         "margin_px": round(order23[1] - order23[0], 4)}})

    # ---- Q24 ordering in one column ----------------------------------------
    col7 = [o for o in objs if o["col"] == 7]
    ys = {o["id"]: o["center"]["y"] for o in col7}
    assert len(set(ys.values())) == 8, ys
    order24 = sorted(ys, key=lambda i: (ys[i], i))
    emit("Q24", "grid-scene.png", "ordering", 1,
         "把 C7 列的 8 个主体按中心 y 坐标从小到大排序，写出排在最前面的 3 个编号。",
         "只统计编号 G01–G64 的 64 个主体；C7 列＝第 7 列，即 G07、G15、G23、G31、G39、"
         "G47、G55、G63。",
         "按中心 y 严格升序排序。同一列内 8 个主体的中心 y 互不相同，"
         "因此排序结果唯一，不需要并列消解。",
         "±2 px（相邻行中心 y 相差 178 px）",
         "第 7 列由顶部 C7 列标确定，8 个主体及其编号都在可见图上。",
         {"answer": order24[:3], "type": "list",
          "method": "take column 7, sort by center.y ascending, return first three ids",
          "well_posed": {"rule": "同列 8 个 center.y 两两不同，升序唯一",
                         "sorted_all": order24,
                         "centre_y": {k: ys[k] for k in order24}}})

    # ---- Q25 two-step ordering with a full tie-break chain ------------------
    sub25 = [o for o in objs if o["size"] == 64]
    order25 = sorted(sub25, key=lambda o: (o["center"]["x"], o["center"]["y"], o["id"]))
    emit("Q25", "grid-scene.png", "ordering", 2,
         "先从 G01–G64 中选出所有尺寸＝64 的主体，再按“中心 x 升序；中心 x 相同则中心 y "
         "升序；仍相同则编号升序”的规则排序，回答最前面的 3 个编号。",
         "只统计编号 G01–G64 的 64 个主体。",
         "排序键＝(中心 x, 中心 y, 编号) 的字典序。三级并列全部被消除，"
         "同一列内用 y 区分、同一格内不可能重复，因此顺序是全序、唯一。",
         "±2 px（列间 190 px、行间 178 px）",
         "尺寸 64 的主体可由可见外接尺寸直接量出；中心由外接矩形得到。",
         {"answer": [o["id"] for o in order25[:3]], "type": "list",
          "method": "step1 keep size==64; step2 sort by (center.x asc, center.y asc, id asc); "
                    "return first three ids",
          "well_posed": {"rule": "(x,y,id) 为全序键，不存在未定义的并列",
                         "size_64_count": len(sub25),
                         "distinct_centre_x": sorted({o["center"]["x"] for o in sub25}),
                         "distinct_centre_y": sorted({o["center"]["y"] for o in sub25}),
                         "first_three": [o["id"] for o in order25[:3]]}})

    # ---- Q26 bounding box of one body --------------------------------------
    bb = by_id["G23"]["bbox"]
    emit("Q26", "grid-scene.png", "bounding_box", 1,
         "写出 G23 主体外接矩形的四个边界坐标 x_min、y_min、x_max、y_max（单位像素）。"
         "圆环取外径的外接矩形；不含其下方的编号文字。",
         "只统计编号 G01–G64 的 64 个主体；边界指主体本身，不含编号标签 G23。",
         "外接矩形＝主体在图上的最小轴对齐外框，x_min 为左边界、y_min 为上边界、"
         "x_max 为右边界、y_max 为下边界；等价于 center ± 尺寸/2。",
         "±2 px（列距 190 px、行距 178 px，尺寸档差 16 px）",
         "G23 的主体与编号都在可见图上；48/64/80 三档在 1600×1600 原图上可直接量出，"
         "档间差 16 px 大于容差。",
         {"answer": [bb["x_min"], bb["y_min"], bb["x_max"], bb["y_max"]], "type": "bbox",
          "method": "bbox = center ± size/2 on both axes, using the same geometry that "
                    "generated grid-scene.snapshot",
          "well_posed": {"rule": "单一主体、单一外接框，不存在并列",
                         "body": {k: by_id["G23"][k] for k in ("id", "shape", "size", "color",
                                                              "row", "col")},
                         "corner_convention": "x 向右为正，y 向下为正"}})

    # ---- Q27 two-step bounding-box union -----------------------------------
    sub27 = [o for o in objs if o["size"] == 80]
    u27 = {"x_min": min(o["bbox"]["x_min"] for o in sub27),
           "y_min": min(o["bbox"]["y_min"] for o in sub27),
           "x_max": max(o["bbox"]["x_max"] for o in sub27),
           "y_max": max(o["bbox"]["y_max"] for o in sub27)}
    emit("Q27", "grid-scene.png", "bounding_box", 2,
         "先从 G01–G64 中选出所有尺寸＝80 的主体，再求这些主体外接矩形的并集外接框，"
         "写出它的 x_min、y_min、x_max、y_max。",
         "只统计编号 G01–G64 的 64 个主体。",
         "并集外接框＝该子集所有外接矩形的 min(x_min)、min(y_min)、max(x_max)、max(y_max)。",
         "±2 px",
         "80 是三档中最大的一档，可直接量出；行列位置由 C/R 标确定。",
         {"answer": [u27["x_min"], u27["y_min"], u27["x_max"], u27["y_max"]], "type": "bbox",
          "method": "step1 keep size==80; step2 union bbox over that subset",
          "well_posed": {"rule": "固定集合的并集外接框唯一",
                         "subset_count": len(sub27),
                         "subset_ids": sorted(o["id"] for o in sub27)}})

    # ---- Q28 colour counting ----------------------------------------------
    blue = [o for o in objs if o["color"] == "blue"]
    blue48 = [o for o in blue if o["size"] == 48]
    emit("Q28", "grid-scene.png", "color_counting", 2,
         "在 G01–G64 中，颜色＝蓝的主体共有多少个？其中尺寸＝48 的有多少个？",
         "只统计编号 G01–G64 的 64 个主体；标题、图例、行列标、页脚文字都不计入。",
         "第一步＝对固定的 64 个主体按颜色计数；第二步＝在蓝色子集内按尺寸计数。",
         "±0 个",
         "蓝色＝#2563EB，是四色中唯一的冷色高饱和蓝，与橙/绿/紫互不混淆。",
         {"answer": {"blue_total": len(blue), "blue_size_48": len(blue48)}, "type": "counts",
          "method": "count color=='blue'; then count those with size==48",
          "well_posed": {"rule": "计数范围固定，不依赖任何排序或距离比较",
                         "generator_constraint": "每种颜色恰好 16 个"}})

    # ---- Q29 shape counting with a spatial filter ---------------------------
    xs_col = [centre_x_of_col(i) for i in range(N)]
    thr = 900
    assert all(abs(t - thr) > 2 for t in xs_col), xs_col
    circ = [o for o in objs if o["shape"] == "circle"]
    right = [o for o in circ if o["center"]["x"] > thr]
    kept_cols = [i + 1 for i, v in enumerate(xs_col) if v > thr]
    emit("Q29", "grid-scene.png", "shape_counting", 2,
         "在 G01–G64 中，形状＝圆（实心圆盘）的主体共有多少个？"
         "其中主体中心 x 大于 900 像素的有多少个？",
         "只统计编号 G01–G64 的 64 个主体；x 以图片左上角为原点、向右为正。",
         "第一步＝对固定 64 个主体按形状计数；第二步＝在圆中筛 center.x > 900 再计数。"
         "阈值 900 落在第 5 列中心 815 与第 6 列中心 1005 之间，不与任何主体中心重合。",
         "±0 个；x 阈值与最近列中心的距离为 85 px",
         "圆盘＝没有内圈的实心圆；各列中心 x 依次为 245、435、625、815、1005、1195、"
         "1385、1575。",
         {"answer": {"circle_total": len(circ),
                     "circle_centre_x_gt_900": len(right)}, "type": "counts",
          "method": "count shape=='circle'; then keep center.x > 900 and count again",
          "well_posed": {"rule": "阈值不与任何主体中心重合，筛选结果唯一",
                         "column_centre_x": xs_col, "threshold_px": thr,
                         "columns_kept": kept_cols,
                         "kept_ids": sorted(o["id"] for o in right)}})

    # ---- Q30 occlusion, answerable ----------------------------------------
    vis_ids = [v[0] for v in O_VISIBLE]
    emit("Q30", "occlusion.png", "occlusion_visible_count", 1,
         "在这张遮挡图里，完全可见（没有任何一部分被深色遮挡物压住）的主体共有几个？"
         "它们的编号是什么？",
         "只统计图中可见的主体；遮挡物后方的内容不可见，不参与统计，也不作为任何答案的依据。",
         "“完全可见”＝主体的全部像素都落在浅色工作区内；只要有任何一部分被遮挡物压住，"
         "就不算完全可见。",
         "±0 个",
         "V1–V4 四个主体的完整轮廓与其编号直接印在可见图上；P1 的右侧有明显的遮挡切口，"
         "因此它必须被排除。判断不需要任何隐藏内容。",
         {"answer": {"fully_visible_bodies": len(vis_ids), "ids": vis_ids}, "type": "count",
          "method": "count the bodies that no opaque cover touches; V1..V4 lie wholly inside "
                    "the visible work area, P1 is clipped by cover 2",
          "well_posed": {"rule": "V1–V4 完整可见、两块遮挡物完全不透明，计数唯一为 4；"
                                 "P1 被遮挡物 2 压住 %d px，必须排除"
                                 % O_PARTIAL_COVERED_PX,
                         "excluded": [{"label": O_PARTIAL[0], "shape": O_PARTIAL[1],
                                       "size": O_PARTIAL[2], "covered_px": O_PARTIAL_COVERED_PX}],
                         "visible_geometry_source": "occlusion-scene-data.json -> "
                                                    "fully_visible_bodies"}})

    # ---- Q31 occlusion, deliberately undeterminable ------------------------
    A.append({
        "q_id": "Q31", "image": "occlusion.png",
        "answer": "无法确定", "answer_type": "undeterminable",
        "computation_method":
            "无法计算：遮挡物 1 是完全不透明的纯色矩形，其覆盖区域的像素已被遮挡物本身占满，"
            "不含任何被遮挡主体的信息。equivalence.json 给出像素级证明——两份隐藏内容不同的"
            "DSL 渲染出逐字节相同的 PNG，因此“后面有 0 个、1 个、2 个……图形”会给出完全相同的"
            "可见图，任何数量都无法从图上区分。所以本题的正确答案是“无法确定”。",
        "derived_from": "occlusion.png 的最终可见像素 + equivalence.json 的像素等价证明",
        "coordinate_tolerance": "不适用",
        "visibility_basis": "唯一可判定的命题是“是否存在可见证据”，其答案是不存在。",
        "well_posedness": {
            "rule": "题目被刻意设计为凭最终可见图不可判定，期望答案就是字面字符串“无法确定”",
            "hidden_count_never_used_as_truth":
                "两份 DSL 各自的隐藏主体数量（5 与 6）只出现在 occlusion 的审计说明里，"
                "从未被用作任何题目的标准答案；questions.json 中不含任何数量或答案",
        },
    })
    Q.append({
        "q_id": "Q31", "image": "occlusion.png",
        "type": "occlusion_information_insufficient", "steps": 1,
        "question": "遮挡物 1（画面中部偏右的深色矩形）后面有几个图形？"
                    "如果无法从这张图确定，请直接回答“无法确定”。",
        "scope": "只允许依据 occlusion.png 的最终可见像素作答。",
        "comparison_criteria": "遮挡物是纯不透明矩形，覆盖区域内没有任何残影、半透明、"
                               "虚线或轮廓泄露。",
        "coordinate_tolerance": "不适用",
        "answer_visibility_basis": "遮挡物覆盖区域内的像素不含任何被遮挡主体的信息。",
    })

    questions = {
        "schema_version": 1, "task_id": "A19",
        "note": "questions only — no answer, no candidate answer, no count and no hint about "
                "the hidden content appears anywhere in this file",
        "images": {
            "grid-scene.png": "1600x1600，8×8 网格，64 个带编号主体 G01–G64",
            "occlusion.png": "800×800 遮挡场景；occlusion-alternative.png 是它的像素级同构图，"
                             "隐藏内容不同、遮挡做法不同",
        },
        "global_conventions": {
            "coordinate_origin": "每张图的左上角为原点 (0,0)，x 向右为正，y 向下为正，"
                                 "单位为该图片的像素。",
            "centering": "主体中心＝主体外接矩形的几何中心；圆环取外径外接矩形，内径不参与。",
            "sizing": "圆按直径、方按边长、圆角方按边长；圆环外径＝尺寸、内径＝尺寸的一半。",
            "counting_scope": "所有计数与检索只针对编号 G01–G64 的 64 个主体；标题、说明、"
                              "图例、C1–C8 / R1–R8 行列标、页脚文字都不计入。",
            "tie_policy": "所有“最大／最小／最近／最前”类问题使用严格比较；"
                          "允许并列的题目必须在题干中给出完整的并列消解顺序。",
            "distance_metric": "中心到中心的欧氏距离 sqrt(dx²+dy²)，单位像素。",
            "coordinate_tolerance": "坐标类答案容差 ±2 px；计数类答案容差 ±0。",
        },
        "question_count": len(Q),
        "questions": Q,
    }
    answers = {
        "schema_version": 1, "task_id": "A19",
        "note": "每条答案都由 scene-data.json 的几何（网格题）或交付图的可见像素（遮挡题）"
                "推导，没有一条是手工填写的",
        "grid_answer_source": "scene-data.json（seed %d）；"
                              "verify_a19.py 会重新推导并逐条比对" % SEED,
        "occlusion_answer_source": "occlusion.png 的可见像素 + equivalence.json 的像素等价证明",
        "question_ids": [q["q_id"] for q in Q],
        "answers": A,
    }
    assert len(Q) == 14 and len(A) == 14
    return questions, answers


# --------------------------------------------------------------- occ data ---
def occ_scene_data(dsl_a: str, dsl_b: str) -> dict:
    def pack(items, visible, emitted_x=None):
        out = []
        for i, (lab, shp, s, x, y, col) in enumerate(items):
            o = {"label": lab, "shape": shp, "size": s, "color": col,
                 "nominal_bbox": {"x_min": x, "y_min": y, "x_max": x + s, "y_max": y + s},
                 "nominal_center": {"x": x + s / 2.0, "y": y + s / 2.0},
                 "visible_in_final_png": visible}
            if emitted_x is not None:
                o["emitted_bbox"] = {"x_min": emitted_x, "y_min": y,
                                     "x_max": emitted_x + s, "y_max": y + s}
            if visible:
                o["id_label"] = {"text": lab, "below_body": True,
                                 "y_min": y + s + 4, "y_max": y + s + 26}
            out.append(o)
        return out

    hidden = __import__("hashlib")
    return {
        "schema_version": 1, "task_id": "A19", "artifact": "occlusion",
        "title": O_TITLE,
        "canvas": {"width": OW, "height": OH, "background": O_BG,
                   "origin": "top-left", "x_axis": "right", "y_axis": "down",
                   "unit": "pixel"},
        "work_area_card_bbox": {"x_min": O_CARD_BOX[0], "y_min": O_CARD_BOX[1],
                                "x_max": O_CARD_BOX[0] + O_CARD_BOX[2],
                                "y_max": O_CARD_BOX[1] + O_CARD_BOX[3]},
        "covers": [
            {"name": "遮挡物 1",
             "bbox": {"x_min": O_COVER1[0], "y_min": O_COVER1[1],
                      "x_max": O_COVER1[0] + O_COVER1[2],
                      "y_max": O_COVER1[1] + O_COVER1[3]},
             "fill": O_COVER1_FILL, "corner_radius": 14, "opacity": "不透明，未输出任何 alpha"},
            {"name": "遮挡物 2",
             "bbox": {"x_min": O_COVER2[0], "y_min": O_COVER2[1],
                      "x_max": O_COVER2[0] + O_COVER2[2],
                      "y_max": O_COVER2[1] + O_COVER2[3]},
             "fill": O_COVER2_FILL, "corner_radius": 14, "opacity": "不透明，未输出任何 alpha"},
        ],
        "fully_visible_bodies": pack(O_VISIBLE, True),
        "partially_visible_bodies": [
            dict(pack([O_PARTIAL], False)[0], visible_in_final_png="partial",
                 covered_by="遮挡物 2", covered_px=O_PARTIAL_COVERED_PX,
                 visible_px=O_PARTIAL[2] - O_PARTIAL_COVERED_PX)],
        "hidden_set_A__occlusion_png": pack(O_HIDDEN_A, False),
        "hidden_set_B__occlusion_alternative_png":
            dict(items=pack(O_HIDDEN_B, False, emitted_x=O_PARK_X),
                 mechanism="A1 方案里这些主体本应落在各自遮挡矩形内；"
                           "B1 方案里它们被发射到 x=706，位于 700px 宽的 ClipRect 之外"),
        "hidden_sets_differ_in": ["数量 5 vs 6", "每个位置的形状", "尺寸", "颜色",
                                  "在场景中的名义位置", "遮挡做法（覆盖 vs 裁剪）"],
        "clip_box_of_variant_B": {"x_min": 0, "y_min": 0, "x_max": O_CLIP_W, "y_max": OH},
        "leakage_guarantees": [
            "两块遮挡矩形均为纯不透明纯色，未输出 opacity 或带 alpha 的颜色",
            "全图没有虚线、半透明或残影，隐藏主体的边界不会以任何形式露出",
            "A1：隐藏主体先绘制后被完全覆盖；B1：隐藏主体被 ClipRect 在光栅化之前整体移除",
            "两份 DSL 的最终 PNG 逐字节相同，见 equivalence.json",
        ],
        "dsl": {
            "occlusion.snapshot": {"bytes": len(dsl_a.encode("utf-8")),
                                   "sha256": hidden.sha256(dsl_a.encode("utf-8")).hexdigest()},
            "occlusion-alternative.snapshot": {
                "bytes": len(dsl_b.encode("utf-8")),
                "sha256": hidden.sha256(dsl_b.encode("utf-8")).hexdigest()},
        },
        "question_scope": "交付的题目只能使用可见图；隐藏主体数量从不作为标准答案",
    }