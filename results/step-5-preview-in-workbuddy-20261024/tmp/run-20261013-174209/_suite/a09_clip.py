# -*- coding: utf-8 -*-
"""A09 clipping check: verify no transformed body extends outside its cell."""
from __future__ import annotations

import json
import os
from pathlib import Path

from PIL import Image

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ["SNAPSHOT_RUN_ID"]
OUT = ROOT / "outputs" / RUN_ID / "A09"
TMP = ROOT / "tmp" / RUN_ID / "A09"

GEO = json.loads((OUT / "geometry-audit.json").read_text(encoding="utf-8"))
IMG = Image.open(TMP / "iter4.png").convert("RGB")

checks = []
for cell in GEO["cells"]:
    cid = cell["id"]
    bx = cell["final_bbox_canvas_px"]
    x0, y0 = cell["cell_origin_px"]
    cw, chh = 300, 250
    inside = (bx[0] >= x0 and bx[1] >= y0 and bx[2] <= x0 + cw and bx[3] <= y0 + chh)
    checks.append({"cell": cid, "passed": bool(inside),
                   "bbox": [round(v, 1) for v in bx],
                   "cell": [x0, y0, x0 + cw, y0 + chh]})

fails = [c for c in checks if not c["passed"]]
print(json.dumps({"total": len(checks), "failed": len(fails), "failures": fails},
                 ensure_ascii=False, indent=2))
