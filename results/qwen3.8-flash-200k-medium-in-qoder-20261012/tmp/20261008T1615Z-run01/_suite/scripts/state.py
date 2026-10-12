"""Update suite-state.json + append suite events/checkpoints.

Run from suite root. Usage:
  python tmp/<run_id>/_suite/scripts/state.py --task A01 --status completed \
      --artifacts "operations.png,operations.snapshot,computed-data.json,snapshot-usage.md,task-metrics.json" \
      --event task_completed --note "5 DSL versions, 4 visual iterations"
"""
import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

root = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
rid = os.environ["SNAPSHOT_RUN_ID"]
out = root / "outputs" / rid / "_suite"
temp = root / "tmp" / rid / "_suite"
state_path = out / "suite-state.json"

ap = argparse.ArgumentParser()
ap.add_argument("--task", default=None)
ap.add_argument("--status", default=None)
ap.add_argument("--artifacts", default="")
ap.add_argument("--rounds", default="")
ap.add_argument("--cases", default="")
ap.add_argument("--evidence", default="")
ap.add_argument("--unresolved", default="")
ap.add_argument("--resume-notes", default=None)
ap.add_argument("--event", required=True)
ap.add_argument("--note", default="")
ap.add_argument("--suite-artifact", default=None)
a = ap.parse_args()

now = datetime.now(timezone.utc).isoformat()
st = json.loads(state_path.read_text(encoding="utf-8"))
st["updated_at"] = now
if a.task:
    st["current_task"] = a.task
    for t in st["tasks"]:
        if t["id"] == a.task:
            if a.status:
                t["status"] = a.status
                if a.status == "in_progress" and not t["started_at"]:
                    t["started_at"] = now
                if a.status in ("completed", "partial", "blocked"):
                    t["ended_at"] = now
            for key, val in (("artifacts", a.artifacts), ("completed_rounds", a.rounds),
                             ("completed_cases", a.cases),
                             ("visual_review_evidence", a.evidence),
                             ("unresolved_issues", a.unresolved)):
                for x in [v for v in val.split(",") if v]:
                    if x not in t[key]:
                        t[key].append(x)
            if a.resume_notes is not None:
                t["resume_notes"] = a.resume_notes
if a.suite_artifact:
    for x in [v for v in a.suite_artifact.split(",") if v]:
        if x not in st["suite_artifacts"]:
            st["suite_artifacts"].append(x)
st["last_checkpoint"] = f"tmp/{rid}/_suite/checkpoints/state-{len(list((temp/'checkpoints').glob('*.json')))+1:06d}.json"
state_path.write_text(json.dumps(st, ensure_ascii=False, indent=2), encoding="utf-8")

with (temp / "events.jsonl").open("a", encoding="utf-8") as f:
    f.write(json.dumps({"ts": now, "run_id": rid, "task_id": a.task, "event": a.event,
                        "status": a.status, "note": a.note, "path_base": "suite_root"},
                       ensure_ascii=False) + "\n")

(temp / "checkpoints").mkdir(parents=True, exist_ok=True)
n = len(list((temp / "checkpoints").glob("*.json"))) + 1
cp = temp / "checkpoints" / f"state-{n:06d}.json"
cp.write_text(json.dumps(st, ensure_ascii=False, indent=2), encoding="utf-8")
print(cp.relative_to(root).as_posix())
