"""Magnified QA crops for A09: one file per grid cell plus header, legend and the two
30-degree specimens, so every claim in the report can be checked by eye at 2x-3x.

NEAREST (not LANCZOS) keeps a 1px edge a single edge instead of inventing a second line.
"""
import json
import os
from pathlib import Path

from PIL import Image

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
TEMP = ROOT / "tmp" / RID / "A09"
SRC = Path(os.environ.get("A09_SRC") or (TEMP / "preview" / "v03.png"))
if not SRC.is_absolute():
    SRC = ROOT / SRC
OUT = TEMP / "preview" / "crops"
OUT.mkdir(parents=True, exist_ok=True)

im = Image.open(SRC).convert("RGB")
plan = json.loads((TEMP / "plan_a09.json").read_text(encoding="utf-8"))
gx, gy = plan["canvas"]["grid"]["origin"]

jobs = []
for i, c in enumerate(plan["cells"]):
    col, row = i % 4, i // 4
    jobs.append((f"cell_{c['id']}", (gx + col * 332, gy + row * 282, 300, 250), 2))
jobs.append(("header", (0, 0, 1600, 150), 2))
jobs.append(("legend", (0, gy + 874, 1600, 1200 - (gy + 874)), 2))
for cid in ("T11", "T12"):
    c = next(x for x in plan["cells"] if x["id"] == cid)
    x0, y0, w, h = c["cell_rect_canvas"]
    jobs.append((f"zoom_{cid}", (x0 + 16, y0 + 44, 268, 162), 3))

made = []
for name, (x, y, w, h), sc in jobs:
    crop = im.crop((int(x), int(y), int(x + w), int(y + h)))
    crop = crop.resize((int(w * sc), int(h * sc)), Image.NEAREST)
    crop.save(OUT / f"{name}.png")
    made.append(name)
print(json.dumps({"source": str(SRC.relative_to(ROOT)).replace("\\", "/"),
                  "crops": len(made), "names": made}))
