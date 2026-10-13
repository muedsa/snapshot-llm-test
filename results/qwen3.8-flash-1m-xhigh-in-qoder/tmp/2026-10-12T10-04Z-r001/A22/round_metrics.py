"""A22 - per-round task-metrics.json, counting only records tagged with that round."""
from __future__ import annotations

import argparse
import json
import os
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()

ap = argparse.ArgumentParser()
ap.add_argument("--run-id", required=True)
ap.add_argument("--round", type=int, required=True)
ap.add_argument("--started-at", required=True)
a = ap.parse_args()

TMP = ROOT / "tmp" / a.run_id / "A22"
OUT = ROOT / "outputs" / a.run_id / "A22"
tag = f"round-0{a.round}"


def read(p):
    return [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines()
            if l.strip()] if Path(p).exists() else []


reqs = [r for r in read(TMP / "requests.jsonl") if r.get("round") == tag]
iters = [r for r in read(TMP / "iterations.jsonl") if r.get("round") == tag]
views = [r for r in read(TMP / "image-views.jsonl") if r.get("round") == tag]
renders = [r for r in reqs if r.get("request_type") == "render"]
ok = [r for r in renders if r.get("image_format") in ("png", "jpeg", "webp")]
started = datetime.fromisoformat(a.started_at)
stamps = [datetime.fromisoformat(r[k]) for r in reqs for k in ("started_at", "ended_at")
          if r.get(k)]
ended = max(stamps) if stamps else datetime.now().astimezone()
itypes = Counter(i.get("type") for i in iters)
files = ["dashboard.png", "dashboard.snapshot", "computed-data.json", "layout-map.json",
         "change-audit.json", "snapshot-usage.md", "task-metrics.json"]

m = {
    "schema_version": 1, "path_base": "suite_root", "task_id": "A22",
    "run_id": a.run_id, "round": tag, "accepted_dsl_version": f"r{a.round:02d}",
    "started_at": started.isoformat(timespec="seconds"),
    "ended_at": ended.isoformat(timespec="seconds"), "timezone": ended.strftime("%z"),
    "wall_clock_seconds": round((ended - started).total_seconds(), 1),
    "request_seconds_total": round(sum(r.get("duration_seconds") or 0 for r in reqs), 2),
    "requests": {
        "render_total": len(renders), "render_success": len(ok),
        "render_failed": len(renders) - len(ok),
        "render_retries": sum(1 for r in renders if r.get("kind") == "retry"),
        "document_total": 0,
        "shared_preparation_total": len(read(ROOT / "tmp" / a.run_id / "_suite"
                                            / "requests.jsonl")),
        "auxiliary_no_ink_renders": sum(1 for r in renders if "-noink" in str(
            r.get("request_id"))),
    },
    "image_views": len(views),
    "iterations": {"total_records": len(iters), "by_type": dict(itypes),
                   "complete_visual_iterations": itypes.get("visual", 0)},
    "deliverables": sorted((OUT / tag / n).relative_to(ROOT).as_posix()
                           for n in files if (OUT / tag / n).exists()),
    "pixel_audit": json.loads((TMP / f"r{a.round:02d}-verify.json").read_text(
        encoding="utf-8"))["checks"],
    "log_files": {"requests": f"tmp/{a.run_id}/A22/requests.jsonl",
                  "iterations": f"tmp/{a.run_id}/A22/iterations.jsonl",
                  "image_views": f"tmp/{a.run_id}/A22/image-views.jsonl",
                  "filter": "records whose round field equals this round"},
}
(OUT / tag).mkdir(parents=True, exist_ok=True)
(OUT / tag / "task-metrics.json").write_text(json.dumps(m, ensure_ascii=False, indent=2)
                                             + "\n", encoding="utf-8")
print(json.dumps({"round": tag, "renders": len(renders), "views": len(views),
                  "iterations": len(iters), "wall": m["wall_clock_seconds"]},
                 ensure_ascii=False))
