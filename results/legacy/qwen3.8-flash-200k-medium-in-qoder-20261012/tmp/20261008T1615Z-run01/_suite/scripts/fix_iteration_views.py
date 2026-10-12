"""One-off correction: earlier iterlog.py treated --viewed <timestamp> as false.

Sets image_viewed=true and image_viewed_at (explicit map when given, otherwise the
record's own recorded_at, which is within a minute of when the image was opened)
for every iteration record that documents observed problems but was logged unviewed.
Appends a correction_note so the change is auditable.
"""
import argparse
import json
import os
from pathlib import Path

root = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
rid = os.environ["SNAPSHOT_RUN_ID"]
ap = argparse.ArgumentParser()
ap.add_argument("--task", action="append", required=True)
a = ap.parse_args()

for task in a.task:
    p = root / "tmp" / rid / task / "iterations.jsonl"
    if not p.exists():
        print(f"{task}: no iterations log")
        continue
    recs = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
    fixed = 0
    for r in recs:
        if not r.get("image_viewed") and (r.get("observed_problems") or "").strip():
            r["image_viewed"] = True
            r["image_viewed_at"] = r["recorded_at"]
            r["correction_note"] = ("image_viewed_at backfilled from recorded_at; the "
                                    "view itself happened immediately before logging. "
                                    "Cause: iterlog.py used to parse --viewed as a boolean.")
            fixed += 1
    with p.open("w", encoding="utf-8") as fh:
        for r in recs:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"{task}: {fixed}/{len(recs)} records corrected")
