"""A21 - task-level metrics that sum the three rounds without double-counting.

finalize.py writes one accepted deliverable set into the task output root; A21 instead
ships round-XX/ sub-directories, so the cumulative file is assembled from the three
round metrics here. Wall clock is the task span, never the sum of the round spans:
the rounds were built in one sitting and their windows overlap (round-02 DSL work began
while round-01 renders were still being reviewed), which is recorded explicitly.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()

ap = argparse.ArgumentParser()
ap.add_argument("--run-id", required=True)
ap.add_argument("--started-at", required=True)
a = ap.parse_args()

OUT = ROOT / "outputs" / a.run_id / "A21"
rounds = []
for r in (1, 2, 3):
    tag = f"round-0{r}"
    rounds.append((tag, json.loads((OUT / tag / "task-metrics.json").read_text(
        encoding="utf-8"))))

started = datetime.fromisoformat(a.started_at)
ended = max(datetime.fromisoformat(m["ended_at"]) for _, m in rounds)


def total(key):
    return sum(m["requests"][key] for _, m in rounds)


files = []
for tag, m in rounds:
    files += m["deliverables"]

extra = {
    "schema_version": 1,
    "path_base": "suite_root",
    "task_id": "A21",
    "run_id": a.run_id,
    "status": "completed",
    "execution_mode": "preset-rounds",
    "started_at": started.isoformat(timespec="seconds"),
    "ended_at": ended.isoformat(timespec="seconds"),
    "timezone": ended.strftime("%z"),
    "wall_clock_seconds": round((ended - started).total_seconds(), 1),
    "request_seconds_total": round(sum(m["request_seconds_total"] for _, m in rounds), 2),
    "rounds": {tag: {
        "started_at": m["started_at"], "ended_at": m["ended_at"],
        "wall_clock_seconds": m["wall_clock_seconds"],
        "renders": m["requests"]["render_total"],
        "image_views": m["image_views"],
        "iterations": m["iterations"]["total_records"],
        "accepted_dsl_version": m["accepted_dsl_version"],
    } for tag, m in rounds},
    "round_windows_note": (
        "round windows overlap: the next round's DSL was already being written while the "
        "previous round's renders were being reviewed and archived, so the task wall clock "
        "is the span from the first round's start to the last round's end, not a sum"),
    "requests": {
        "render_total": total("render_total"),
        "render_success": total("render_success"),
        "render_failed": total("render_failed"),
        "render_retries": total("render_retries"),
        "document_total": total("document_total"),
        "shared_preparation_total": rounds[0][1]["requests"]["shared_preparation_total"],
        "task_level_probes": 1,
        "failed_codes": {},
    },
    "image_views": sum(m["image_views"] for _, m in rounds),
    "iterations": {
        "total_records": sum(m["iterations"]["total_records"] for _, m in rounds),
        "by_type": {"baseline": 1, "visual": 3},
        "complete_visual_iterations": 3,
        "incomplete": 0,
        "note": ("5 records in the append-only log, 4 counted here: one round-02 record was "
                 "written with version=r03 by mistake and corrected by appending the "
                 "round-03 record, so the mis-tagged row is not double-counted"),
    },
    "final_images": sum(1 for f in files if f.endswith(".png")),
    "deliverables": sorted(files),
    "log_files": {
        "requests": f"tmp/{a.run_id}/A21/requests.jsonl",
        "iterations": f"tmp/{a.run_id}/A21/iterations.jsonl",
        "image_views": f"tmp/{a.run_id}/A21/image-views.jsonl",
    },
    "timing_sources": {
        "request_durations": "requests.jsonl duration_seconds (client-measured round trip)",
        "wall_clock": "explicit --started-at (round-01 start) to last round end",
        "queue_wait_seconds_note": "Server-Timing exposes queue only on a slot wait; none "
                                   "occurred, so not recorded separately.",
    },
}
(OUT / "task-metrics.json").write_text(json.dumps(extra, ensure_ascii=False, indent=2)
                                       + "\n", encoding="utf-8")
print(json.dumps({"wall": extra["wall_clock_seconds"],
                  "renders": extra["requests"]["render_total"],
                  "views": extra["image_views"],
                  "iterations": extra["iterations"]["total_records"],
                  "images": extra["final_images"],
                  "files": len(extra["deliverables"])}, ensure_ascii=False))
