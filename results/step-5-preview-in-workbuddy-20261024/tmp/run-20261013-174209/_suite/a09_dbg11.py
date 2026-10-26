import json
import math
from pathlib import Path

GEO = json.loads(Path("outputs/run-20261013-174209/A09/geometry-audit.json").read_text(encoding="utf-8"))
for cid in ["T02", "T04", "T08"]:
    c = next(x for x in GEO["cells"] if x["id"] == cid)
    print(cid, "pivot matrix:")
    for row in c["matrix_3x3_pivot"]:
        print("   ", [round(v, 6) for v in row])
    print(cid, "full matrix:")
    for row in c["matrix_3x3_full"]:
        print("   ", [round(v, 6) for v in row])
