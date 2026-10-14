"""Generic multi-round rollup: outputs/<run_id>/<task>/task-metrics.json.

finalize.py writes one accepted deliverable set into the task root; a staged task instead
ships round-XX/ sub-directories, so the cumulative file is assembled from the round
metrics. Wall clock is the task span, never the sum of the round spans, because the
rounds of one sitting overlap (the next round's DSL is often already being written while
the previous round's renders are being reviewed) — that is recorded explicitly.

  python tmp/<run_id>/_suite/scripts/rollup.py --run-id <id> --task A22 \
      --started-at 2026-10-12T23:15:00+08:00
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()

ap = argparse.ArgumentParser()
ap.add_argument("--run-id", required=True)
ap.add_argument("--task", required=True)
ap.add_argument("--started-at", required=True)
ap.add_argument("--status", default="completed")
ap.add_argument("--mode", default="preset-rounds",
                help="execution mode recorded in the summary")
ap.add_argument("--note", action="append", default=[],
                help="extra provenance notes, key=value pairs go to notes{}")
a = ap.parse_args()

OUT = ROOT / "outputs" / a.run_id / a.task
round_dirs = sorted(p for p in OUT.glob("round-*") if p.is_dir())
if not round_dirs:
    print("no round-* directories found", file=sys.stderr)
    raise SystemExit(2)

rounds = {}
for p in round_dirs:
    f = p / "task-metrics.json"
    if not f.exists():
        print(f"missing {f.relative_to(ROOT).as_posix()}", file=sys.stderr)
        raise SystemExit(2)
    rounds[p.name] = json.loads(f.read_text(encoding="utf-8"))

started = datetime.fromisoformat(a.started_at)
ended = max(datetime.fromisoformat(m["ended_at"]) for m in rounds.values())
files = sorted({f for m in rounds.values() for f in m["deliverables"]})
itypes: Counter = Counter()
for m in rounds.values():
    itypes.update(m["iterations"]["by_type"])

summary = {
    "schema_version": 1, "path_base": "suite_root", "task_id": a.task,
    "run_id": a.run_id, "status": a.status, "execution_mode": a.mode,
    "rounds_present": list(rounds),
    "started_at": started.isoformat(timespec="seconds"),
    "ended_at": ended.isoformat(timespec="seconds"),
    "timezone": ended.strftime("%z"),
    "wall_clock_seconds": round((ended - started).total_seconds(), 1),
    "request_seconds_total": round(sum(m["request_seconds_total"]
                                       for m in rounds.values()), 2),
    "rounds": {tag: {"started_at": m["started_at"], "ended_at": m["ended_at"],
                     "wall_clock_seconds": m["wall_clock_seconds"],
                     "renders": m["requests"]["render_total"],
                     "image_views": m["image_views"],
                     "iterations": m["iterations"]["total_records"],
                     "accepted_dsl_version": m["accepted_dsl_version"]}
               for tag, m in rounds.items()},
    "round_windows_note": (
        "round windows overlap: work for the next round started while the previous "
        "round's renders were still being reviewed, so the task wall clock is the span "
        "from the first round's start to the last round's end, not a sum of round spans"),
    "requests": {
        "render_total": sum(m["requests"]["render_total"] for m in rounds.values()),
        "render_success": sum(m["requests"]["render_success"] for m in rounds.values()),
        "render_failed": sum(m["requests"]["render_failed"] for m in rounds.values()),
        "render_retries": sum(m["requests"]["render_retries"] for m in rounds.values()),
        "document_total": sum(m["requests"].get("document_total", 0)
                              for m in rounds.values()),
        "shared_preparation_total": next(iter(rounds.values()))["requests"][
            "shared_preparation_total"],
        "auxiliary_no_ink_renders": sum(m["requests"].get(
            "auxiliary_no_ink_renders", 0) for m in rounds.values()),
        "failed_codes": {},
    },
    "image_views": sum(m["image_views"] for m in rounds.values()),
    "iterations": {"total_records": sum(m["iterations"]["total_records"]
                                        for m in rounds.values()),
                   "by_type": dict(itypes),
                   "complete_visual_iterations": itypes.get("visual", 0)},
    "final_images": sum(1 for f in files if f.endswith(".png")),
    "deliverables": files,
    "log_files": {k: f"tmp/{a.run_id}/{a.task}/{k}.jsonl"
                  for k in ("requests", "iterations", "image-views")},
    "timing_sources": {
        "request_durations": "requests.jsonl duration_seconds (client-measured round trip)",
        "wall_clock": "explicit --started-at (first round start) to last round end",
        "queue_wait_seconds_note": "Server-Timing exposes queue only on a slot wait; "
                                   "none occurred, so not recorded separately.",
    },
}
for n in a.note:
    k, _, v = n.partition("=")
    summary.setdefault("notes", {})[k] = v
(OUT / "task-metrics.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2)
                                       + "\n", encoding="utf-8")
print(json.dumps({"task": a.task, "wall": summary["wall_clock_seconds"],
                  "renders": summary["requests"]["render_total"],
                  "views": summary["image_views"],
                  "iterations": summary["iterations"]["total_records"],
                  "images": summary["final_images"],
                  "files": len(files)}, ensure_ascii=False))
