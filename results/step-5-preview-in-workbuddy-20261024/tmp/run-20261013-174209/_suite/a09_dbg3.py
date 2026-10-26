import json
from pathlib import Path

GEO = json.loads(Path("outputs/run-20261013-174209/A09/geometry-audit.json").read_text(encoding="utf-8"))
for c in GEO["cells"]:
    print(c["id"], "origin", c["cell_origin_px"], "center", c["cell_center_px"])
