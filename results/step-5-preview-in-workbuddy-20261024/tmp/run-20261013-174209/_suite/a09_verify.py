# -*- coding: utf-8 -*-
"""A09 pixel verification using matrix_3x3_full predictions."""
from __future__ import annotations

import json
import math
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ["SNAPSHOT_RUN_ID"]
OUT = ROOT / "outputs" / RUN_ID / "A09"
TMP = ROOT / "tmp" / RUN_ID / "A09"

from PIL import Image  # noqa: E402

GEO = json.loads((OUT / "geometry-audit.json").read_text(encoding="utf-8"))
IMG = Image.open(TMP / "iter4.png").convert("RGB")
W, H = IMG.size

COL = {(229, 75, 75): "R1", (35, 100, 219): "R2", (234, 181, 59): "R3", (17, 17, 17): "DOT"}
NAME2IDX = {"R1": 0, "R2": 1, "R3": 2, "DOT": None}

checks = []


def chk(name, ok, detail=""):
    checks.append({"check": name, "passed": bool(ok), "detail": detail})


def is_col(p, c, tol=14):
    return all(abs(a - b) <= tol for a, b in zip(p, c))


def angle_of(m):
    return math.degrees(math.atan2(m[1][0], m[0][0])) % 360


for cell in GEO["cells"]:
    cid = cell["id"]
    x0, y0 = cell["cell_origin_px"]
    mf = cell["matrix_3x3_full"]
    ang = angle_of(mf)
    axis_aligned = ang in (0.0, 90.0, 180.0, 270.0)

    found = {}
    for yy in range(int(y0) + 30, int(y0) + 248):
        for xx in range(int(x0) + 4, int(x0) + 296):
            p = IMG.getpixel((xx, yy))
            for c, n in COL.items():
                if is_col(p, c):
                    found.setdefault(n, []).append((xx, yy))

    pred = {}
    for rc in cell["rect_corners"]:
        cs = rc["corners_canvas_px"]
        pred["R%d" % (rc["rect_index"] + 1)] = (
            sum(p[0] for p in cs) / 4, sum(p[1] for p in cs) / 4)
    dc = cell["dot_center_canvas_px"]
    pred["DOT"] = (dc[0], dc[1])

    ctol = 1.5 if axis_aligned else 6.0
    for n, pts in found.items():
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        act = ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2)
        ex = pred[n]
        dx = abs(act[0] - ex[0])
        dy = abs(act[1] - ex[1])
        chk("%s_%s_center" % (cid, n), dx <= ctol and dy <= ctol,
            "actual=(%.1f,%.1f) expect=(%.1f,%.1f) d=(%.2f,%.2f)" % (
                act[0], act[1], ex[0], ex[1], dx, dy))

        aw, ah = max(xs) - min(xs) + 1, max(ys) - min(ys) + 1
        if n == "DOT":
            dcx = [p[0] for p in cell["dot_corners_canvas_px"]]
            dcy = [p[1] for p in cell["dot_corners_canvas_px"]]
            ew, eh = max(dcx) - min(dcx) + 1, max(dcy) - min(dcy) + 1
        else:
            ri = NAME2IDX[n]
            cs = cell["rect_corners"][ri]["corners_canvas_px"]
            cxs = [p[0] for p in cs]
            cys = [p[1] for p in cs]
            ew, eh = max(cxs) - min(cxs) + 1, max(cys) - min(cys) + 1
        stol = 3 if axis_aligned else 6
        chk("%s_%s_size" % (cid, n), abs(aw - ew) <= stol and abs(ah - eh) <= stol,
            "actual %dx%d expect %.1fx%.1f (angle %.0f%s)" % (
                aw, ah, ew, eh, ang, ", diagonal-AA tolerance" if not axis_aligned else ""))

    for n in ["R1", "R2", "R3", "DOT"]:
        chk("%s_%s_present" % (cid, n), n in found, "count=%d" % len(found.get(n, [])))

chk("canvas_1600x1200", (W, H) == (1600, 1200), "%dx%d" % (W, H))
chk("cells_12", len(GEO["cells"]) == 12)
chk("t07_ne_t08", not GEO["t07_t08_difference"]["matrices_equal"])

fails = [c for c in checks if not c["passed"]]
print(json.dumps({"total": len(checks), "failed": len(fails),
                  "failures": fails[:20]}, ensure_ascii=False, indent=2))
