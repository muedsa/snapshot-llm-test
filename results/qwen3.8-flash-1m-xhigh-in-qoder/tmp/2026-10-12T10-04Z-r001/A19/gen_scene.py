"""A19 - build the 8x8 question field (64 objects) and the two occlusion versions.

The scene is generated from a seed and then checked against every constraint the task
sets, on the values actually produced - the seed alone is never treated as evidence:

  * 64 objects G01-G64, reading order left-to-right / top-to-bottom, one per cell;
  * 4 colours x 4 shapes, each colour and each shape exactly 16 times;
  * all 16 colour-shape combinations present;
  * every colour and every shape appears in all three sizes 48 / 64 / 80;
  * every row has at least 3 distinct colours and 3 distinct shapes;
  * ring outer diameter = size, inner diameter = size / 2;
  * the ID label sits outside the subject's box.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))

from snap import (  # noqa: E402
    C, Node, Positioned, Snapshot, Stack, num,
)

W = H = 1600
CELL = 200
N = 8
COLours = {"blue": "#2B5BD7", "orange": "#E0913B", "green": "#1F8A5F",
           "violet": "#7A4FD3"}
SHAPES = ["circle", "square", "ring", "rounded-square"]
SIZES = [48, 64, 80]
BG = "#FFFFFF"
GRID_LINE = "#E3E8F0"
LABEL = "#33404F"
MONO = "Noto Sans Mono CJK SC"
JITTER = 14
SEED = 20261012


def centre(idx, rng):
    r, c = divmod(idx, N)
    return (c * CELL + CELL / 2 + round(rng.uniform(-JITTER, JITTER), 1),
            r * CELL + CELL / 2 + round(rng.uniform(-JITTER, JITTER), 1))


def balanced(rng, items, k):
    """A list of len N*N where each of `items` appears exactly `k` times."""
    pool = [x for x in items for _ in range(k)]
    rng.shuffle(pool)
    return pool


def row_groups(vals):
    return [vals[i * N:(i + 1) * N] for i in range(N)]


def fix_rows(rng, vals, items, k, min_distinct, extra=None):
    """Swap until every row has >= min_distinct distinct values (and any extra test)."""
    for _ in range(40000):
        groups = row_groups(vals)
        bad = [i for i, g in enumerate(groups)
               if len(set(g)) < min_distinct or (extra and not extra(i, g))]
        if not bad:
            return vals
        i = bad[0]
        j = rng.randrange(N)
        if j == i:
            continue
        a = rng.randrange(N)
        b = rng.randrange(N)
        if vals[i * N + a] == vals[j * N + b]:
            continue
        vals[i * N + a], vals[j * N + b] = vals[j * N + b], vals[i * N + a]
    raise AssertionError("could not satisfy row constraints")


def pair_coverage_ok(colour, shape):
    return len({(colour[i], shape[i]) for i in range(N * N)}) == 16


def build_scene(seed=SEED):
    rng = random.Random(seed)
    colours = fix_rows(rng, balanced(rng, list(COLours), 16), list(COLours), 16, 3)
    shapes = fix_rows(rng, balanced(rng, SHAPES, 16), SHAPES, 16, 3)
    for _ in range(20000):      # reshuffle until all 16 colour-shape pairs occur
        if pair_coverage_ok(colours, shapes):
            break
        shapes = fix_rows(rng, balanced(rng, SHAPES, 16), SHAPES, 16, 3)
    else:
        raise AssertionError("no pair coverage found")

    sizes = [rng.choice(SIZES) for _ in range(N * N)]

    def repair_sizes():
        for _ in range(60000):
            need = [(c, s) for c in COLours for s in SIZES
                    if not any(colours[i] == c and sizes[i] == s for i in range(64))]
            need += [(f"shape:{sh}", s) for sh in SHAPES for s in SIZES
                     if not any(shapes[i] == sh and sizes[i] == s for i in range(64))]
            if not need:
                return sizes
            key, want = need[0]
            idx = [i for i in range(64)
                   if (colours[i] == key if not str(key).startswith("shape:")
                       else shapes[i] == key.split(":")[1])
                   and sizes[i] != want]
            donor = [i for i in range(64) if sizes[i] == want]
            if idx and donor:
                sizes[rng.choice(idx)] = want
    sizes = repair_sizes()

    rng2 = random.Random(seed + 7)
    objects = []
    for i in range(N * N):
        cx, cy = centre(i, rng2)
        size = sizes[i]
        shape = shapes[i]
        box = subject_box(shape, size, cx, cy)
        label_box = id_label_box(shape, size, cx, cy)
        objects.append({
            "id": f"G{i + 1:02d}", "row": i // N + 1, "col": i % N + 1,
            "colour": colours[i],
            "colour_hex": COLours[colours[i]], "shape": shape, "size_px": size,
            "centre": [round(cx, 1), round(cy, 1)],
            "subject_box": [round(v, 1) for v in box],
            "id_label_box": [round(v, 1) for v in label_box],
        })
    return objects


def subject_box(shape, size, cx, cy):
    return [cx - size / 2, cy - size / 2, cx + size / 2, cy + size / 2]


def id_label_box(shape, size, cx, cy):
    """Label sits below the subject, left-aligned with its left edge: outside the body."""
    w = 3 * 22 * 0.5          # three monospace characters at fontSize 22
    return [cx - size / 2, cy + size / 2 + 6, cx - size / 2 + w, cy + size / 2 + 6 + 24]


def check_constraints(objects):
    rep = {}
    by_colour = {}
    by_shape = {}
    by_size = {}
    for o in objects:
        by_colour[o["colour"]] = by_colour.get(o["colour"], 0) + 1
        by_shape[o["shape"]] = by_shape.get(o["shape"], 0) + 1
        by_size[o["size_px"]] = by_size.get(o["size_px"], 0) + 1
    rows = [{"row": r + 1,
             "colours": sorted({o["colour"] for o in objects if o["row"] == r + 1}),
             "shapes": sorted({o["shape"] for o in objects if o["row"] == r + 1})}
            for r in range(N)]
    combos = sorted({(o["colour"], o["shape"]) for o in objects})
    colour_sizes = {c: sorted({o["size_px"] for o in objects if o["colour"] == c})
                    for c in COLours}
    shape_sizes = {s: sorted({o["size_px"] for o in objects if o["shape"] == s})
                   for s in SHAPES}
    ids = [o["id"] for o in objects]
    rep = {
        "object_count": len(objects),
        "ids_in_reading_order": ids == [f"G{i + 1:02d}" for i in range(64)],
        "one_subject_per_cell": len({(o["row"], o["col"]) for o in objects}) == 64,
        "colour_counts": by_colour, "shape_counts": by_shape, "size_counts": by_size,
        "combination_coverage": {"present": len(combos), "required": 16,
                                 "missing": sorted({(c, s) for c in COLours
                                                    for s in SHAPES} - set(combos))},
        "sizes_per_colour": colour_sizes, "sizes_per_shape": shape_sizes,
        "rows": rows,
        "rows_all_ge3_colours": all(len(r["colours"]) >= 3 for r in rows),
        "rows_all_ge3_shapes": all(len(r["shapes"]) >= 3 for r in rows),
    }
    rep["all_constraints_met"] = bool(
        rep["object_count"] == 64 and rep["ids_in_reading_order"]
        and rep["one_subject_per_cell"]
        and all(v == 16 for v in by_colour.values()) and len(by_colour) == 4
        and all(v == 16 for v in by_shape.values()) and len(by_shape) == 4
        and rep["combination_coverage"]["present"] == 16
        and all(v == SIZES for v in colour_sizes.values())
        and all(v == SIZES for v in shape_sizes.values())
        and rep["rows_all_ge3_colours"] and rep["rows_all_ge3_shapes"])
    return rep


def subject_node(o):
    size, colour = o["size_px"], o["colour_hex"]
    if o["shape"] == "circle":
        return C(width=num(size), height=num(size), color=colour, shape="CIRCLE")
    if o["shape"] == "square":
        return C(width=num(size), height=num(size), color=colour)
    if o["shape"] == "rounded-square":
        return C(width=num(size), height=num(size), color=colour,
                 borderRadius=num(size * 0.25))
    return Stack(C(width=num(size), height=num(size), color=colour, shape="CIRCLE"),
                 C(width=num(size / 2), height=num(size / 2), color=BG, shape="CIRCLE"),
                 alignment="CENTER", clipBehavior="NONE")


def grid_doc(objects):
    """Grid lines first, then subjects, then ID labels: labels never sit under a body."""
    body = Node("Stack", {"alignment": "TOP_LEFT", "clipBehavior": "HARD_EDGE"},
                [C(width=num(W), height=num(H), color=BG)]
                + [Positioned(C(width="1", height=num(H), color=GRID_LINE),
                              left=num(c * CELL), top="0") for c in range(N + 1)]
                + [Positioned(C(width=num(W), height="1", color=GRID_LINE),
                              left="0", top=num(r * CELL)) for r in range(N + 1)]
                + [Positioned(subject_node(o), left=num(o["subject_box"][0]),
                              top=num(o["subject_box"][1])) for o in objects]
                + [Positioned(Node("Text", {"fontSize": "22", "color": LABEL,
                                            "fontFamily": MONO}, [], o["id"]),
                              left=num(o["id_label_box"][0]),
                              top=num(o["id_label_box"][1])) for o in objects])
    return Snapshot(body, background=BG, type="png")


ap = argparse.ArgumentParser()
ap.add_argument("--ver", default="v001")
ap.add_argument("--seed", type=int, default=SEED)
a = ap.parse_args()
TMP = ROOT / "tmp" / RUN / "A19"
TMP.mkdir(parents=True, exist_ok=True)

objects = build_scene(a.seed)
report = check_constraints(objects)
(TMP / f"{a.ver}-scene.json").write_text(
    json.dumps({"seed": a.seed, "objects": objects, "distribution": report},
               ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
(TMP / f"{a.ver}-grid-scene.snapshot").write_text(
    grid_doc(objects).render() + "\n", encoding="utf-8")
print(json.dumps({"all_constraints_met": report["all_constraints_met"],
                  "colour_counts": report["colour_counts"],
                  "shape_counts": report["shape_counts"],
                  "size_counts": report["size_counts"],
                  "combos": report["combination_coverage"]["present"],
                  "sizes_per_colour": report["sizes_per_colour"],
                  "sizes_per_shape": report["sizes_per_shape"]},
                 ensure_ascii=False, indent=1))
assert report["all_constraints_met"], report
