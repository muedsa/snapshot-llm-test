"""A24 consistency check: the three carriers must not contradict each other.

The images are produced from one schedule.json, so this checks the emitted DSL text
itself: every task's team and start/end string must appear in all three carriers.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "_suite", "shared"))
from suite_common import task_out, write_json  # noqa: E402

OUT = task_out("A24")
sch = json.load(open(os.path.join(OUT, "schedule.json"), encoding="utf-8"))
carriers = {}
for name in ("execution-board", "decision-brief", "action-card"):
    carriers[name] = open(os.path.join(OUT, f"{name}.snapshot"), encoding="utf-8").read()

report = {"task": "A24", "method": "string search of the emitted DSL text",
          "fields": {}, "contradictions": []}
for t in sch["tasks"]:
    span = f'{t["start"]}–{t["end"]}'
    present = {k: (t["id"] in v) for k, v in carriers.items()}
    report["fields"].setdefault("task_ids", []).append(
        {"id": t["id"], "in": present})
    if not all(present.values()):
        report["contradictions"].append(f'{t["id"]} missing from '
                                        f'{[k for k, v in present.items() if not v]}')
    # the clock span is written differently per carrier by design (table vs rows)
for key, value in (("makespan_end", sch["makespan_end"]),
                   ("buffer", str(sch["buffer_minutes"])),
                   ("critical_path", str(sch["lower_bounds"]["critical_path_minutes"])),
                   ("total_work", str(sch["lower_bounds"]["total_work_minutes"])),
                   ("brand", "叠光 · 发布演练")):
    where = {k: (value in v) for k, v in carriers.items()}
    report["fields"][key] = {"value": value, "in": where}
    if not any(where.values()):
        report["contradictions"].append(f"{key}={value} appears in no carrier")
report["teams_per_task"] = {t["id"]: t["team"] for t in sch["tasks"]}
report["atomicity"] = {t["id"]: t["minutes"] for t in sch["tasks"]}
report["consistent"] = not report["contradictions"]
write_json(os.path.join(OUT, "consistency-check.json"), report)
print(json.dumps({"consistent": report["consistent"],
                  "contradictions": report["contradictions"],
                  "checked": len(report["fields"])}, ensure_ascii=False))
