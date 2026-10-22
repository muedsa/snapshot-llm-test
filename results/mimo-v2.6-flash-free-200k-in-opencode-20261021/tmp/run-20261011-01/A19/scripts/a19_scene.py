# -*- coding: utf-8 -*-
"""A19 scene generator.

- Seeded 8x8 grid distribution for 64 objects G01-G64 with hard constraints
  (4 colours x16, 4 shapes x16, all 16 colour x shape combos, every colour and
  every shape in all three sizes, >=3 distinct colours and >=3 distinct shapes
  per row), verified by assertions on the ACTUAL generated result.
- DSL emission for grid-scene + occlusion/occlusion-alternative pair.

Canvas convention: origin top-left, x right, y down, pixel units.
Cell (row r, col c), 1-based: object centre = (200c+100, 200r+100);
G-id index = (r-1)*8 + c  (left->right, top->bottom).
"""
import itertools
import json
import math
import pathlib
import random

CANVAS = 1600
CELL = 200
ROWS = COLS = 8

COLORS = [("blue", "#2563EB"), ("orange", "#F59E0B"),
          ("green", "#16A34A"), ("purple", "#7C3AED")]
COLOR_HEX = dict(COLORS)
SHAPES = ["circle", "square", "ring", "rounded"]
SIZES = [48, 64, 80]
BASE_SEED = 20261019

TEXT_DARK = "#334155"
INK = "#0F172A"
LINE = "#E2E8F0"
PAPER = "#FFFFFF"
BG = "#F1F5F9"
FONT = "Noto Sans CJK SC"


# --------------------------------------------------------------- geometry
def rounded_radius(shape, size):
    """Radius for the 圆角方 rendering (circle uses full pill)."""
    if shape == "circle":
        return size / 2
    if shape == "rounded":
        return size / 4
    if shape == "ring":
        return size / 2
    return 0          # square


def row_ok(items):
    return (len({it[0] for it in items}) >= 3
            and len({it[1] for it in items}) >= 3)


def gen_pool(seed):
    """16 colour x shape combos x4, sizes rotating so every colour and every
    shape sees all three sizes."""
    rng = random.Random(seed)
    pool = []
    for ci, _ in enumerate(itertools.product(range(4), range(4))):
        for k in range(4):
            pool.append((ci // 4, ci % 4, SIZES[(k + ci) % 3]))
    rng.shuffle(pool)
    return pool


def rows_all_ok(pool):
    return all(row_ok(pool[r * COLS:(r + 1) * COLS]) for r in range(ROWS))


def find_seed():
    seed = BASE_SEED
    while True:
        pool = gen_pool(seed)
        if rows_all_ok(pool):
            return seed, pool
        seed += 1


def check_pool(pool):
    """Hard constraints; raises on violation, returns evidence dict."""
    color_freq = {n: 0 for n, _ in COLORS}
    shape_freq = {s: 0 for s in SHAPES}
    size_freq = {z: 0 for z in SIZES}
    combo = {}
    cs_size = {}
    row_counts = []
    for (ci, si, z) in pool:
        cn, sn = COLORS[ci][0], SHAPES[si]
        color_freq[cn] += 1
        shape_freq[sn] += 1
        size_freq[z] += 1
        combo[(cn, sn)] = combo.get((cn, sn), 0) + 1
        cs_size.setdefault((cn, sn), set()).add(z)
        cs_size.setdefault(("color", cn), set()).add(z)
        cs_size.setdefault(("shape", sn), set()).add(z)
    for r in range(ROWS):
        items = pool[r * COLS:(r + 1) * COLS]
        row_counts.append({
            "row": r + 1,
            "distinct_colors": len({COLORS[i][0] for i, _, _ in items}),
            "distinct_shapes": len({SHAPES[j] for _, j, _ in items}),
            "color_freq": {COLORS[i][0]:
                           sum(1 for x, _, _ in items if x == i)
                           for i in range(4)},
            "shape_freq": {SHAPES[j]:
                           sum(1 for _, y, _ in items if y == j)
                           for j in range(4)},
        })
    assert all(v == 16 for v in color_freq.values()), color_freq
    assert all(v == 16 for v in shape_freq.values()), shape_freq
    assert len(combo) == 16 and all(v == 4 for v in combo.values()), combo
    for cn, _ in COLORS:
        assert cs_size[("color", cn)] == {48, 64, 80}, (cn,
                                                       cs_size[("color", cn)])
    for sn in SHAPES:
        assert cs_size[("shape", sn)] == {48, 64, 80}, (sn,
                                                       cs_size[("shape", sn)])
    assert all(r["distinct_colors"] >= 3 for r in row_counts), row_counts
    assert all(r["distinct_shapes"] >= 3 for r in row_counts), row_counts
    return {"color_freq": color_freq, "shape_freq": shape_freq,
            "size_freq": size_freq,
            "combo_counts": {"%s x %s" % (COLORS[i][0], SHAPES[j]):
                             combo[(COLORS[i][0], SHAPES[j])]
                             for i, j in itertools.product(range(4), range(4))},
            "color_sizes": {cn: sorted(cs_size[("color", cn)])
                            for cn, _ in COLORS},
            "shape_sizes": {sn: sorted(cs_size[("shape", sn)])
                            for sn in SHAPES},
            "row_counts": row_counts}


def build_scene():
    seed, pool = find_seed()
    dist = check_pool(pool)
    objs = []
    for i, (ci, si, z) in enumerate(pool):
        r, c = divmod(i, COLS)          # 0-based
        cx, cy = c * CELL + CELL // 2, r * CELL + CELL // 2
        objs.append({
            "id": "G%02d" % (i + 1),
            "row": r + 1, "col": c + 1,
            "color": COLORS[ci][0], "shape": SHAPES[si], "size": z,
            "center": [cx, cy],
            "body_bbox": [cx - z // 2, cy - z // 2, cx + z // 2, cy + z // 2],
            "id_text_anchor": [c * CELL + 10, r * CELL + 6],
        })
    return seed, objs, dist


# ------------------------------------------------------------- DSL helpers
def fmt(v):
    s = ("%.4f" % float(v)).rstrip("0").rstrip(".")
    return s if s not in ("", "-0") else "0"


def pos(left, top, w, h, inner):
    return ('<Positioned left="%s" top="%s" width="%s" height="%s">%s'
            '</Positioned>' % (fmt(left), fmt(top), fmt(w), fmt(h), inner))


def text_el(box, s, size, color=TEXT_DARK, align="LEFT", bold=False):
    x, y, w, h = box
    a = ('<Positioned left="%s" top="%s" width="%s" height="%s">'
         '<Text fontSize="%s" color="%s" fontFamily="%s"' % (
             fmt(x), fmt(y), fmt(w), fmt(h), fmt(size), color, FONT))
    if bold:
        a += ' fontStyle="BOLD"'
    a += ' textAlign="%s" text="%s"/></Positioned>' % (align, s)
    return a


def object_el(o):
    """The 主体 for one grid object (centred in its cell).

    body_bbox is [left, top, right, bottom]; width/height = size (NOT bbox
    unpacked as w/h — caught by viewing the first render, bodies overflowed).
    """
    x, y = o["body_bbox"][0], o["body_bbox"][1]
    z = o["size"]
    w = h = z
    if o["shape"] == "ring":
        inner = ('<Container width="%d" height="%d" border="%d SOLID %s" '
                 'borderRadius="%s"/>'
                 % (z, z, z // 4, COLOR_HEX[o["color"]], fmt(z / 2)))
    elif o["shape"] == "square":
        inner = '<Container width="%d" height="%d" color="%s"/>' % (
            z, z, COLOR_HEX[o["color"]])
    else:
        inner = ('<Container width="%d" height="%d" color="%s" '
                 'borderRadius="%s"/>'
                 % (z, z, COLOR_HEX[o["color"]], fmt(rounded_radius(
                     o["shape"], z))))
    return pos(x, y, w, h, inner)


def emit_grid(objs):
    out = ['<Snapshot type="png" background="%s">' % BG,
           '<SizedBox width="%d" height="%d">' % (CANVAS, CANVAS),
           '<Stack alignment="TOP_LEFT" clipBehavior="NONE">']
    # 64 white cells with hairline grid
    for r in range(ROWS):
        for c in range(COLS):
            out.append(pos(c * CELL, r * CELL, CELL, CELL,
                           '<Container color="%s" border="1 SOLID %s"/>'
                           % (PAPER, LINE)))
    # bodies, then ID labels (labels never overlap bodies: anchor zone
    # (10,6)-(54,34) cell-local vs body zone >=60 for the largest size)
    for o in objs:
        out.append(object_el(o))
    for o in objs:
        x, y = o["id_text_anchor"]
        out.append(text_el([x, y, 48, 28], o["id"], 20))
    out += ['</Stack>', '</SizedBox>', '</Snapshot>']
    return "\n".join(out) + "\n"


# ------------------------------------------------- occlusion pair (800x800)
OCC = 800
HIDDEN = {
    "A": ("circle", "green", 160, "3"),
    "B": ("rounded", "orange", 160, "8"),
}


def emit_occlusion(version):
    """Visible layers are element-wise identical between A and B; only the
    hidden group (drawn UNDER the opaque occluder) differs."""
    shape, cname, z, glyph = HIDDEN[version]
    out = ['<Snapshot type="png" background="%s">' % BG,
           '<SizedBox width="%d" height="%d">' % (OCC, OCC),
           '<Stack alignment="TOP_LEFT" clipBehavior="NONE">']
    # ---- header (visible, identical)
    out.append(pos(0, 0, OCC, 96,
                   '<Container color="%s"/>' % INK))
    out.append(text_el([28, 30, 400, 40], "遮挡场景", 28, color="#F8FAFC"))
    # ---- visible corner objects (identical)
    out.append(pos(72, 144, 80, 80,
                   '<Container width="80" height="80" color="#F59E0B" '
                   'borderRadius="40"/>'))
    out.append(pos(648, 144, 80, 80,
                   '<Container width="80" height="80" color="#16A34A"/>'))
    out.append(pos(72, 600, 64, 64,
                   '<Container width="64" height="64" color="#7C3AED" '
                   'borderRadius="16"/>'))
    out.append(pos(648, 600, 80, 80,
                   '<Container width="80" height="80" '
                   'border="20 SOLID #2563EB" borderRadius="40"/>'))
    # ---- hidden content (differs; drawn before the occluder; includes a
    #      shadow whose whole effect stays under the occluder)
    hx, hy = 320, 300
    if shape == "circle":
        hbody = ('<Container width="160" height="160" color="%s" '
                 'borderRadius="80" boxShadow="0 8 24 0 #00000066 NORMAL"/>'
                 % COLOR_HEX[cname])
    else:
        hbody = ('<Container width="160" height="160" color="%s" '
                 'borderRadius="40" boxShadow="0 8 24 0 #00000066 NORMAL"/>'
                 % COLOR_HEX[cname])
    out.append(pos(hx, hy, 160, 160, hbody))
    out.append(text_el([hx + 40, hy + 24, 96, 120], glyph, 96,
                       color="#FFFFFF", align="CENTER", bold=True))
    # ---- opaque occluder + label (identical; covers hidden bbox + shadow)
    out.append(pos(240, 240, 320, 320,
                   '<Container color="#334155" borderRadius="16"/>'))
    out.append(text_el([240, 384, 320, 40], "遮挡区", 24,
                       color="#FFFFFF", align="CENTER"))
    out += ['</Stack>', '</SizedBox>', '</Snapshot>']
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    seed, objs, dist = build_scene()
    print("seed:", seed, "objects:", len(objs))
    print("color_freq:", dist["color_freq"])
    print("shape_freq:", dist["shape_freq"])
    print("size_freq:", dist["size_freq"])
    print("color_sizes:", dist["color_sizes"])
    print("shape_sizes:", dist["shape_sizes"])
    for r in dist["row_counts"]:
        print("  row%2d distinct colors=%d shapes=%d" % (
            r["row"], r["distinct_colors"], r["distinct_shapes"]))
