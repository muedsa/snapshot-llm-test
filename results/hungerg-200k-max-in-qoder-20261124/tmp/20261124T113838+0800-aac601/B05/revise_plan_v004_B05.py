from __future__ import annotations
import copy
import json
import sys
from pathlib import Path
BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import suitekit as sk
source = BASE / "plan-v003.json"
target = BASE / "plan-v004.json"
assert source.is_file() and not target.exists()
plan = json.loads(source.read_text(encoding="utf-8"))
previous = plan["plan_version"]
case = next(c for c in plan["cases"] if c["id"] == "B05-case-04")
old = copy.deepcopy(case["criteria"][0])
case["criteria"][0]["condition"] = "08:00四项与案例01清单一致，Metformin保留未确认状态"
case["criteria_history"].append({
    "changed_at": sk.iso(), "previous_plan_version": previous, "new_plan_version": "v004",
    "reason": "最终整体接触表与跨屏数据核验发现：共享清单中Metformin也为08:00用药，晨间页遗漏该项并与案例05的早晨未确认记录不一致。",
    "evidence": [sk.rel(BASE / "inspection" / "contact-sheet-final-r001.png")],
    "criterion_before": old, "criterion_after": copy.deepcopy(case["criteria"][0]),
})
plan["plan_version"] = "v004"
plan["established_at"] = sk.iso()
for item in plan["cases"]:
    item["plan_version"] = "v004"
    item["plan_established_at"] = plan["established_at"]
    item["version"] = "v004"
    for criterion in item["criteria"]:
        criterion["plan_version"] = "v004"
sk.write_json(target, plan)
print(sk.rel(target))
