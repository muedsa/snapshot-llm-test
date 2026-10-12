"""Merge three-way timing (wall / active / idle) into a task's task-metrics.json.

Run from suite root. Usage:
  python tmp/<run_id>/_suite/scripts/timefit.py --task A15 \
      --gap 2026-10-09T02:00:28+00:00 2026-10-09T02:06:54+00:00 active "evidence text"

wall = metrics started_at -> ended_at (or artifact span when wider)
idle = sum of gaps explicitly classified as idle (including gaps outside the window,
       which are reported but not subtracted from the window)
active = wall - idle_inside_window
"""
import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

root = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
rid = os.environ["SNAPSHOT_RUN_ID"]

ap = argparse.ArgumentParser()
ap.add_argument("--task", required=True)
ap.add_argument("--gap", nargs="+", action="append", default=[],
                help="start_iso end_iso classification evidence")
a = ap.parse_args()

mp = root / "outputs" / rid / a.task / "task-metrics.json"
m = json.loads(mp.read_text(encoding="utf-8"))
iso = lambda s: datetime.fromisoformat(s)  # noqa: E731
t0, t1 = iso(m["timings"]["started_at"]), iso(m["timings"]["ended_at"])
wall = (t1 - t0).total_seconds()

gaps, idle_in = [], 0.0
for g in a.gap:
    s, e, cls, *ev = g
    d = (iso(e) - iso(s)).total_seconds()
    if iso(s) >= t0 and iso(e) <= t1:
        if cls == "idle":
            idle_in += d
    gaps.append({"start": iso(s).astimezone(timezone.utc).isoformat(),
                 "end": iso(e).astimezone(timezone.utc).isoformat(),
                 "seconds": round(d, 1), "classification": cls,
                 "evidence": ev[0] if ev else ""})

m["timings"].update({
    "wall_clock_seconds": round(wall, 1),
    "active_seconds": round(wall - idle_in, 1),
    "idle_gap_seconds": round(idle_in, 1),
    "idle_gaps": gaps,
    "elapsed_time_note": (
        "elapsed/wall is the task window, not a claim of continuous work; gaps classified "
        "idle (session resume, waiting on the user, retries) are subtracted from active and "
        "listed with evidence; request_duration_sum only counts real service calls"),
})
mp.write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")
print(a.task, "wall", m["timings"]["wall_clock_seconds"],
      "active", m["timings"]["active_seconds"], "idle", m["timings"]["idle_gap_seconds"])
