"""Finalise one task: copy the accepted render + its DSL into the output dir and
build task-metrics.json from the task's own logs.

The image bytes are copied verbatim from the saved service response; nothing is
re-encoded.

Run from the suite task root:
  python tmp/<run_id>/_suite/scripts/finalize.py --run-id <id> --task A01 \
      --ver v008 --deliverable operations \
      --views tmp/<run_id>/A01/image-views.jsonl
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()


def read_jsonl(p: Path) -> list[dict]:
    if not p.exists():
        return []
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def iso(p: str | None) -> datetime | None:
    return datetime.fromisoformat(p) if p else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--task", required=True)
    ap.add_argument("--ver", required=True, help="accepted DSL version stem in the temp dir")
    ap.add_argument("--deliverable", action="append", default=[],
                    help="basename without extension, e.g. operations")
    ap.add_argument("--pair", action="append", default=[],
                    help="suffix=basename for multi-image tasks, e.g. wide=agenda-wide")
    ap.add_argument("--started-at", default=None)
    ap.add_argument("--ended-at", default=None)
    ap.add_argument("--views", default=None, help="image-views.jsonl path")
    ap.add_argument("--extra", default=None, help="JSON object merged into the metrics")
    a = ap.parse_args()

    tmp_task = ROOT / "tmp" / a.run_id / a.task
    out_task = ROOT / "outputs" / a.run_id / a.task
    out_task.mkdir(parents=True, exist_ok=True)

    reqs = read_jsonl(tmp_task / "requests.jsonl")
    shared = read_jsonl(ROOT / "tmp" / a.run_id / "_suite" / "requests.jsonl")
    iters = read_jsonl(tmp_task / "iterations.jsonl")
    views = read_jsonl(ROOT / a.views) if a.views else []

    jobs = [(None, n) for n in a.deliverable]
    for spec in a.pair:
        suffix, _, name = spec.partition("=")
        jobs.append((suffix, name))

    copies = []
    for suffix, name in jobs:
        tag = f"{a.ver}-{suffix}" if suffix else a.ver
        src_png = tmp_task / f"{tag}.png"
        src_dsl = tmp_task / f"{tag}.snapshot"
        if not src_png.exists():
            print(f"missing {src_png}", file=sys.stderr)
            return 2
        dst_png = out_task / f"{name}.png"
        dst_dsl = out_task / f"{name}.snapshot"
        shutil.copyfile(src_png, dst_png)
        shutil.copyfile(src_dsl, dst_dsl)
        copies.append({
            "png": dst_png.relative_to(ROOT).as_posix(),
            "dsl": dst_dsl.relative_to(ROOT).as_posix(),
            "png_bytes": dst_png.stat().st_size,
            "source_response": src_png.relative_to(ROOT).as_posix(),
        })

    renders = [r for r in reqs if r.get("request_type") == "render"]
    # A 200 status alone is not success: the edge can return headers and never stream a
    # body, so count only responses that were actually saved as an image.
    ok = [r for r in renders if r.get("image_format") in ("png", "jpeg", "webp")]
    bad = [r for r in renders if r not in ok]
    docs = [r for r in reqs if r.get("request_type") in ("document", "service_get")]
    retry_like = [r for r in renders if r.get("kind") == "retry"]
    rate_waits = [float(r["retry_after"]) for r in renders
                  if r.get("retry_after") and str(r["retry_after"]).replace(".", "").isdigit()]

    ts = [iso(r.get("started_at")) for r in reqs if r.get("started_at")]
    ts += [iso(r.get("ended_at")) for r in reqs if r.get("ended_at")]
    started = iso(a.started_at) or (min(ts) if ts else None)
    ended = iso(a.ended_at) or datetime.now(timezone.utc).astimezone()

    first_ok = min((r for r in ok), key=lambda r: r.get("ended_at") or "") if ok else None
    first_image_secs = None
    if first_ok and started and first_ok.get("ended_at"):
        first_image_secs = round(
            (iso(first_ok["ended_at"]) - started).total_seconds(), 1)

    itypes = Counter(i.get("type", "unspecified") for i in iters)
    incomplete = sum(1 for i in iters if i.get("outcome") in ("failed", "incomplete"))

    metrics = {
        "schema_version": 1,
        "path_base": "suite_root",
        "task_id": a.task,
        "run_id": a.run_id,
        "accepted_dsl_version": a.ver,
        "status": None,
        "started_at": started.isoformat(timespec="seconds") if started else None,
        "ended_at": ended.isoformat(timespec="seconds"),
        "timezone": ended.tzname(),
        "wall_clock_seconds": round((ended - started).total_seconds(), 1) if started else None,
        "first_successful_image_seconds_after_start": first_image_secs,
        "user_feedback_wait_seconds": None,
        "rate_limit_wait_seconds": sum(rate_waits) if rate_waits else None,
        "queue_wait_seconds": None,
        "request_seconds_total": round(sum(r.get("duration_seconds") or 0 for r in reqs), 2),
        "requests": {
            "render_total": len(renders),
            "render_success": len(ok),
            "render_failed": len(bad),
            "render_retries": len(retry_like),
            "document_total": len(docs),
            "shared_preparation_total": len(shared),
            "failed_codes": dict(Counter(str(r.get("error_code")) for r in bad)),
        },
        "dsl_versions": len({i.get("version") for i in iters if i.get("version")}),
        "image_views": len(views),
        "iterations": {
            "total_records": len(iters),
            "by_type": dict(itypes),
            "complete_visual_iterations": itypes.get("visual", 0),
            "incomplete": incomplete,
        },
        "deliverables": copies,
        "log_files": {
            "requests": (tmp_task / "requests.jsonl").relative_to(ROOT).as_posix(),
            "iterations": (tmp_task / "iterations.jsonl").relative_to(ROOT).as_posix(),
            "image_views": ((ROOT / a.views).relative_to(ROOT).as_posix() if a.views else None),
        },
        "timing_sources": {
            "request_durations": "requests.jsonl duration_seconds (client-measured round trip)",
            "wall_clock": "explicit --started-at when given, else earliest log timestamp",
            "queue_wait_seconds_note": "Server-Timing exposes queue only when a slot wait occurred; not separately retrievable here, so recorded as null.",
        },
    }
    if a.extra:
        metrics.update(json.loads(a.extra))

    (out_task / "task-metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"metrics": (out_task / "task-metrics.json").relative_to(ROOT).as_posix(),
                      "copies": copies, "image_views": len(views),
                      "renders": metrics["requests"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
