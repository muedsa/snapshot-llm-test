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
old = json.loads((BASE / "plan-v002.json").read_text(encoding="utf-8"))
cases = copy.deepcopy(old["cases"])
for case in cases:
    for med in case["content_basis"]["medications"]:
        if med["id"] == "M04":
            med["shape"] = "round"
    case["criteria_history"].append({
        "changed_at": sk.iso(), "from_plan_version": "v002", "effective_plan_version": "v003",
        "change": "Demo Omeprazole dosage-form icon changed from capsule to round tablet so it matches the shared '1片' instruction. No acceptance criterion changed.",
        "reason": "Actual v001 visual review found a cross-screen dosage-form inconsistency.",
        "evidence": [sk.rel(BASE / "versions" / "B05-case-04-v001" / "final-01.png")]
    })
ck.prepare("B05", cases, "v003", old["asset_policy"])
product = json.loads((BASE / "product-data.json").read_text(encoding="utf-8"))
next(med for med in product["medications"] if med["id"] == "M04")["shape"] = "round"
sk.write_json(BASE / "product-data.json", product)
print(sk.rel(BASE / "plan-v003.json"))
