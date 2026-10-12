"""Append an iteration record to a task's iterations.jsonl.

Run from suite root. Usage:
  python tmp/<run_id>/_suite/scripts/iterlog.py --task A01 --version v02 --parent v01 \
    --type visual --image outputs/<run_id>/A01/operations.png \
    --problems "..." --changes "..." --result "..."
"""
import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

root = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
rid = os.environ["SNAPSHOT_RUN_ID"]

ap = argparse.ArgumentParser()
ap.add_argument("--task", required=True)
ap.add_argument("--version", required=True)
ap.add_argument("--parent", default=None)
ap.add_argument("--type", required=True,
                choices=["baseline", "visual", "syntax-fix", "retry", "alternative",
                         "requirement-change"])
ap.add_argument("--image", default=None)
ap.add_argument("--viewed", default="true",
                help="'true', 'false', or the ISO timestamp the image was actually opened")
ap.add_argument("--problems", default="")
ap.add_argument("--changes", default="")
ap.add_argument("--result", default="")
ap.add_argument("--complete", default="true")
a = ap.parse_args()

now = datetime.now(timezone.utc)
v = (a.viewed or "").strip()
if v.lower() in ("true", "false"):
    viewed = v.lower() == "true"
    viewed_at = now.isoformat() if viewed else None
else:
    viewed = True
    viewed_at = datetime.fromisoformat(v).isoformat()
rec = {
    "iteration_id": f'{a.task}-{a.version}-{now.strftime("%H%M%S")}',
    "task_id": a.task, "run_id": rid,
    "version": a.version, "parent_version": a.parent, "type": a.type,
    "recorded_at": now.isoformat(),
    "image_path": a.image,
    "image_viewed": viewed,
    "image_viewed_at": viewed_at,
    "observed_problems": a.problems,
    "changes_made": a.changes,
    "recompare_result": a.result,
    "completed": a.complete.lower() == "true",
    "path_base": "suite_root",
}
p = root / "tmp" / rid / a.task / "iterations.jsonl"
p.parent.mkdir(parents=True, exist_ok=True)
with p.open("a", encoding="utf-8") as fh:
    fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
print(rec["iteration_id"])
