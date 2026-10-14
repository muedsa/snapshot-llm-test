"""A21 - per-round metrics.

finalize.py writes the task-level cumulative task-metrics.json; this writes the
round-XX/task-metrics.json each round also has to ship, counting only the requests,
iterations and image views tagged with that round.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
sys.path.insert(0, str(ROOT / "tmp" / os.environ.get("SNAPSHOT_RUN", "2026-10-12T10-04Z-r001")
                           / "_suite" / "scripts"))


def read(p):
    if not Path(p).exists():
        return []
    return [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l]


ap = argparse.ArgumentParser()
ap.add_argument("--run-id", required=True)
ap.add_argument("--round", type=int, required=True)
ap.add_argument("--started-at", required=True)
ap.add_argument("--views", required=True)
a = ap.parse_args()

TMP = ROOT / "tmp" / a.run_id / "A21"
OUT = ROOT / "outputs" / a.run_id / "A21"
tag = f"round-0{a.round}"
reqs = [r for r in read(TMP / "requests.jsonl") if r.get("round") == tag]
iters = [r for r in read(TMP / "iterations.jsonl")
           if r.get("round") == tag and r.get("version") == f"r{a.round:02d}"]
views = [r for r in read(ROOT / a.views) if r.get("round") == tag]
renders = [r for r in reqs if r.get("request_type") == "render"]
ok = [r for r in renders if r.get("image_format") in ("png", "jpeg", "webp")]
ts = [r[k] for r in reqs for k in ("started_at", "ended_at") if r.get(k)]
started = datetime.fromisoformat(a.started_at)
stamps = [datetime.fromisoformat(t) for t in ts]
ended = max(stamps) if stamps else datetime.now(timezone.utc).astimezone()
itypes = Counter(i.get("type") for i in iters)

m = {
    "schema_version": 1, "path_base": "suite_root", "task_id": "A21",
    "run_id": a.run_id, "round": tag,
    "accepted_dsl_version": f"r{a.round:02d}",
    "started_at": started.isoformat(timespec="seconds"),
    "ended_at": ended.isoformat(timespec="seconds"),
    "timezone": ended.tzname(),
    "wall_clock_seconds": round((ended - started).total_seconds(), 1),
    "request_seconds_total": round(sum(r.get("duration_seconds") or 0 for r in reqs), 2),
    "requests": {
        "render_total": len(renders), "render_success": len(ok),
        "render_failed": len(renders) - len(ok),
        "render_retries": sum(1 for r in renders if r.get("kind") == "retry"),
        "document_total": 0,
        "shared_preparation_total": len(read(ROOT / "tmp" / a.run_id / "_suite"
                                            / "requests.jsonl")),
    },
    "image_views": len(views),
    "iterations": {"total_records": len(iters), "by_type": dict(itypes),
                   "complete_visual_iterations": itypes.get("visual", 0)},
    "deliverables": sorted(str((OUT / tag / n).relative_to(ROOT).as_posix())
                           for n in (f"launch-portrait.png", f"launch-portrait.snapshot",
                                     f"launch-wide.png", f"launch-wide.snapshot",
                                     "design-tokens.json", "content-map.json",
                                     "contrast-audit.json",
                                     "snapshot-usage.md", "task-metrics.json")
                           if (OUT / tag / n).exists()),
    "log_files": {"requests": (TMP / "requests.jsonl").relative_to(ROOT).as_posix(),
                  "iterations": (TMP / "iterations.jsonl").relative_to(ROOT).as_posix(),
                  "image_views": (ROOT / a.views).relative_to(ROOT).as_posix(),
                  "filter": "records whose round field equals this round"},
}
(OUT / tag).mkdir(parents=True, exist_ok=True)
(OUT / tag / "task-metrics.json").write_text(json.dumps(m, ensure_ascii=False, indent=2)
                                             + "\n", encoding="utf-8")
print(json.dumps({"round": tag, "renders": m["requests"]["render_total"],
                  "views": len(views), "iterations": len(iters),
                  "wall": m["wall_clock_seconds"]}, ensure_ascii=False))
