# -*- coding: utf-8 -*-
"""A19: 8x8 attribute grid scene + two pixel-identical occlusion variants."""
from __future__ import annotations

import hashlib
import json
import math
import os
import random
import sys
from pathlib import Path

import numpy as np
from PIL import Image

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import dslkit as K  # noqa: E402
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "A19"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
OUT.mkdir(parents=True, exist_ok=True)
clock = rep.TaskClock(TASK)

COLORS = {"blue": "#2563EB", "orange": "#EA8A2F", "green": "#16A34A", "purple": "#7C3AED"}
SHAPES = ["circle", "square", "ring", "rounded"]
SIZES = [48, 64, 80]
BG = "#F4F6FA"
INK = "#111A28"
GRID_LINE = "#E3E8F0"

# ---------------------------------------------------------------- grid data
rng = random.Random(20261107)
combos = [(c, s) for c in COLORS for s in SHAPES]
pool = []
for ci, (c, s) in enumerate(combos):
    for k in range(4):
        pool.append((c, s, SIZES[(ci + k) % 3]))
# ensure each colour and each shape has all three sizes
def ensure(axis):
    for key_i in range(4):
        for size in SIZES:
            pass
rng.shuffle(pool)

def row_ok(objs):
    for r in range(8):
        row = objs[r * 8:(r + 1) * 8]
        if len({o[0] for o in row}) < 3 or len({o[1] for o in row}) < 3:
            return False
    return True

for attempt in range(4000):
    rng.shuffle(pool)
    if row_ok(pool):
        break
objs = pool

# per-colour / per-shape size coverage check + repair by swapping same-combo entries
def coverage(objs):
    bad = []
    for c in COLORS:
        sizes = {o[2] for o in objs if o[0] == c}
        if len(sizes) < 3:
            bad.append(("color", c, sizes))
    for s in SHAPES:
        sizes = {o[2] for o in objs if o[1] == s}
        if len(sizes) < 3:
            bad.append(("shape", s, sizes))
    return bad

for _ in range(4000):
    bad = coverage(objs)
    if not bad:
        break
    rng.shuffle(objs)

assert not coverage(objs), coverage(objs)

M, CELL = 64, 184
records = []
for i, (c, s, size) in enumerate(objs):
    r, col = divmod(i, 8)
    cx, cy = M + (col + 0.5) * CELL, M + (r + 0.5) * CELL
    records.append({"id": f"G{i+1:02d}", "row": r + 1, "col": col + 1, "color": c, "shape": s,
                    "size": size, "center": [round(cx, 1), round(cy, 1)],
                    "bbox": [round(cx - size / 2, 1), round(cy - size / 2, 1),
                             round(cx + size / 2, 1), round(cy + size / 2, 1)]})

def shape_dsl(rec, dx=0, dy=0):
    cx, cy = rec["center"][0] + dx, rec["center"][1] + dy
    s = rec["size"]
    color = COLORS[rec["color"]]
    if rec["shape"] == "circle":
        return K.rect(cx - s / 2, cy - s / 2, s, s, color=color, radius=s / 2)
    if rec["shape"] == "square":
        return K.rect(cx - s / 2, cy - s / 2, s, s, color=color, radius=0)
    if rec["shape"] == "rounded":
        return K.rect(cx - s / 2, cy - s / 2, s, s, color=color, radius=s * 0.22)
    r, ir = s / 2, s / 4
    path = (f"M{r:g} {r:g} m{-r:g} 0 a{r:g} {r:g} 0 1 0 {2*r:g} 0 a{r:g} {r:g} 0 1 0 {-2*r:g} 0 "
            f"M{r:g} {r:g} m{-ir:g} 0 a{ir:g} {ir:g} 0 1 1 {2*ir:g} 0 a{ir:g} {ir:g} 0 1 1 {-2*ir:g} 0 Z")
    return (f'<Positioned left="{cx - s/2:g}" top="{cy - s/2:g}">'
            f'<ClipPath path="{path}" fillRule="EVEN_ODD" clipBehavior="ANTI_ALIAS">'
            f'<Container width="{s:g}" height="{s:g}" color="{color}"/></ClipPath></Positioned>')

W = H = 1600
p: list[str] = [K.rect(0, 0, W, H, color=BG)]
for i in range(9):
    p.append(K.rect(M + i * CELL, M, 1, CELL * 8, color=GRID_LINE))
    p.append(K.rect(M, M + i * CELL, CELL * 8, 1, color=GRID_LINE))
for rec in records:
    p.append(shape_dsl(rec))
    p.append(K.text(rec["center"][0] - 46, rec["center"][1] + rec["size"] / 2 + 8, rec["id"],
                    width=92, size=18, color=INK, align="CENTER"))
dsl = K.document(W, H, p, background=BG)
(OUT / "grid-scene.snapshot").write_text(dsl, encoding="utf-8")

# ---------------------------------------------------------------- occlusion
OW = OH = 800
COVER = (270, 300, 260, 200)          # opaque occluder
HIDDEN_A = {"shape": "circle", "color": "#E23A2E", "center": [400, 400], "size": 110}
HIDDEN_B = {"shape": "square", "color": "#2E7BE2", "center": [400, 400], "size": 118}
VISIBLE = [
    {"shape": "square", "color": "#F0B429", "center": [140, 140], "size": 96},
    {"shape": "circle", "color": "#22B573", "center": [660, 150], "size": 88},
    {"shape": "circle", "color": "#8B5CF6", "center": [150, 660], "size": 104},
    {"shape": "square", "color": "#E07B39", "center": [655, 655], "size": 92},
    {"shape": "circle", "color": "#38BDF8", "center": [400, 690], "size": 84},
]

def occl_dsl(hidden):
    q: list[str] = [K.rect(0, 0, OW, OH, color="#101826")]
    q.append(K.rect(120, 120, 560, 560, color="#16202E", radius=24))
    # hidden object first (fully covered later)
    s = hidden["size"]
    q.append(K.rect(hidden["center"][0] - s / 2, hidden["center"][1] - s / 2, s, s,
                    color=hidden["color"],
                    radius=(s / 2 if hidden["shape"] == "circle" else 0)))
    for v in VISIBLE:
        s2 = v["size"]
        q.append(K.rect(v["center"][0] - s2 / 2, v["center"][1] - s2 / 2, s2, s2, color=v["color"],
                        radius=(s2 / 2 if v["shape"] == "circle" else 0)))
    q.append(K.text(120, 724, "OCCLUSION SAMPLE", size=18, color="#5B6B84", width=560))
    x, y, w2, h2 = COVER
    q.append(K.rect(x, y, w2, h2, color="#1D2738", radius=12, border="2 SOLID #2E3D57"))
    return K.document(OW, OH, q, background="#101826")

for name, hidden in (("occlusion", HIDDEN_A), ("occlusion-alternative", HIDDEN_B)):
    (OUT / f"{name}.snapshot").write_text(occl_dsl(hidden), encoding="utf-8")

# ---------------------------------------------------------------- render
logger = api.TaskLogger(TASK, TMP)
for name in ("grid-scene", "occlusion", "occlusion-alternative"):
    rec = logger.render(OUT / f"{name}.snapshot", OUT / f"{name}.png", name)
    print(name, rec["http_status"], rec["response_bytes"], rec["elapsed_s"])
    if rec["http_status"] != 200:
        print((TMP / "responses" / f"{rec['id']}.bin").read_text(encoding="utf-8", errors="replace")[:900])
        raise SystemExit(1)
print("grid size", api.measure_png(OUT / "grid-scene.png"))
api.write_json(TMP / "geom.json", {"records": records, "hidden": [HIDDEN_A, HIDDEN_B],
                                   "visible": VISIBLE, "cover": COVER})
