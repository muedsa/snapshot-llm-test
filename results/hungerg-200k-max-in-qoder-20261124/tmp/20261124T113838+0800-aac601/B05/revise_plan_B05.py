from __future__ import annotations
import copy
import json
import sys
from pathlib import Path
BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import creativekit as ck
import suitekit as sk

old = json.loads((BASE / "plan-v001.json").read_text(encoding="utf-8"))
cases = copy.deepcopy(old["cases"])
for case in cases:
    for med in case["content_basis"]["medications"]:
        if med["id"] == "M04":
            med["schedule"] = "每日 08:00 · 1片"
    if case["id"] == "B05-case-04":
        case["criteria_history"] = [{
            "changed_at": sk.iso(), "from_plan_version": "v001", "effective_plan_version": "v002",
            "change": "No acceptance condition changed. The demo Omeprazole time was aligned from 07:30 to 08:00 before the first render so the morning three-item screen matches its established criterion and all shared medication data.",
            "reason": "Pre-render cross-screen data consistency correction; no image had yet been rendered.",
            "evidence": [sk.rel(BASE / "plan-v001.json"), sk.rel(BASE / "product-data.json")]
        }]
new = ck.prepare("B05", cases, "v002", old["asset_policy"])
product = json.loads((BASE / "product-data.json").read_text(encoding="utf-8"))
next(med for med in product["medications"] if med["id"] == "M04")["schedule"] = "每日 08:00 · 1片"
sk.write_json(BASE / "product-data.json", product)
print(sk.rel(new))
