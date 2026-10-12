"""A10: cut the QA crops that the whole-image view cannot settle.

NEAREST soffit crops at 1:1 plus two 3x zooms (③'s rim corner, ⑤'s halo above the filter
box). Every crop is taken from the delivered PNG, and the crop list is recorded in
task-metrics.json as the magnified visual-QA evidence.
"""
import json
import os
from pathlib import Path

from PIL import Image

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
TEMP = ROOT / "tmp" / RID / "A10"
SRC = Path(os.environ.get("A10_SRC", TEMP / "preview" / "v06.png"))
if not SRC.is_absolute():
    SRC = (ROOT / SRC).resolve()
DST = SRC.parent / "crops"
DST.mkdir(parents=True, exist_ok=True)
plan = json.loads((TEMP / "plan_a10.json").read_text(encoding="utf-8"))
im = Image.open(SRC).convert("RGB")

BOXES = {"header": (30, 20, 1410, 150), "footer": (30, 1010, 1410, 1092)}
for c in plan["cells"]:
    sx, sy, sw, sh = c["slot_rect"]
    BOXES["cell_" + c["number"]] = (sx, sy, sx + sw, sy + sh)
a3 = next(c["area_origin"] for c in plan["cells"] if c["number"] == "③")
a5 = next(c["area_origin"] for c in plan["cells"] if c["number"] == "⑤")
BOXES["zoom_c3_rim"] = (a3[0] + 20, a3[1] + 20, a3[0] + 100, a3[1] + 90)
BOXES["zoom_c5_halo"] = (a5[0] + 40, a5[1] + 0, a5[0] + 220, a5[1] + 100)

manifest = []
for name, (x0, y0, x1, y1) in BOXES.items():
    crop = im.crop((x0, y0, x1, y1))
    scale = 3 if name.startswith("zoom_") else 1
    if scale > 1:
        crop = crop.resize((crop.width * scale, crop.height * scale), Image.NEAREST)
    out = DST / f"{name}.png"
    crop.save(out)
    manifest.append({"name": name, "source_box": [x0, y0, x1, y1], "scale": scale,
                     "px": [crop.width, crop.height],
                     "path": str(out.relative_to(ROOT)).replace("\\", "/")})
(DST / "manifest.json").write_text(json.dumps(
    {"source": str(SRC.relative_to(ROOT)).replace("\\", "/"), "crops": manifest},
    ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps({"count": len(manifest), "dir": str(DST.relative_to(ROOT))},
                 ensure_ascii=False))
