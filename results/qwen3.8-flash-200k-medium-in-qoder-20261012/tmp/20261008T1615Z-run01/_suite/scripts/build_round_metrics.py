"""Build round-N/task-metrics.json for a multi-round task (A21/A22).

Filters requests.jsonl / iterations.jsonl by DSL version prefix for that round,
so round metrics are a real subset and not a restatement.

Usage:
  python tmp/<run_id>/_suite/scripts/build_round_metrics.py --task A21 --round 1 \
      --prefix r01- --status completed --started 2026-10-09T05:30:00+00:00 \
      --note "..."
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
ap.add_argument("--round", type=int, required=True)
ap.add_argument("--prefix", required=True, help="dsl_version prefix owned by this round")
ap.add_argument("--status", default="completed")
ap.add_argument("--started", default=None)
ap.add_argument("--stop-reason", default="本轮需求满足并完成视觉自检")
ap.add_argument("--outputs", default="")
ap.add_argument("--unresolved", default="")
ap.add_argument("--include-prefix", default="", help="extra prefixes counted in this round")
ap.add_argument("--note", default="")
a = ap.parse_args()

temp = root / "tmp" / rid / a.task
outdir = root / "outputs" / rid / a.task / f"round-{a.round:02d}"


def read_jsonl(p):
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


prefixes = (a.prefix + "," + a.include_prefix).split(",")
owned = lambda v: any((v or "").startswith(p) for p in prefixes if p)

reqs = [r for r in read_jsonl(temp / "requests.jsonl") if owned(r.get("dsl_version"))]
iters = [i for i in read_jsonl(temp / "iterations.jsonl") if owned(i.get("version"))]
renders = [r for r in reqs if r.get("kind") == "render"]
ok = [r for r in renders if r.get("http_status") == 200]
bad = [r for r in renders if r.get("http_status") != 200]
views = [i for i in iters if i.get("image_viewed")]
vis = [i for i in iters if i.get("type") == "visual"]
noops = [i for i in iters if i.get("noop_render")]

ended = datetime.now(timezone.utc).isoformat()
elapsed = round((datetime.fromisoformat(ended)
                 - datetime.fromisoformat(a.started)).total_seconds(), 1) if a.started else None
first_img = None
if a.started and ok:
    first_img = round((datetime.fromisoformat(ok[0]["ended_at"])
                       - datetime.fromisoformat(a.started)).total_seconds(), 1)

metrics = {
    "schema_version": 1, "path_base": "suite_root",
    "task_id": a.task, "run_id": rid,
    "task_round": a.round, "scope": f"round-{a.round:02d} only",
    "version_prefix": a.prefix,
    "status": a.status, "stop_reason": a.stop_reason,
    "output_dir": f"outputs/{rid}/{a.task}/round-{a.round:02d}/",
    "temp_dir": f"tmp/{rid}/{a.task}/",
    "timings": {
        "started_at": a.started, "ended_at": ended, "elapsed_seconds": elapsed,
        "first_usable_image_seconds": first_img,
        "request_duration_sum_seconds": round(sum(r["duration_seconds"] or 0 for r in reqs), 3),
        "note": "elapsed_seconds 为本轮起止墙钟时间，含看图与本地计算；请求耗时之和非活跃时间",
    },
    "counts": {
        "snapshot_requests": len(renders),
        "successful_snapshot_requests": len(ok),
        "failed_snapshot_requests": len(bad),
        "other_service_requests": len([r for r in reqs if r.get("kind") != "render"]),
        "dsl_versions": len({r.get("dsl_version") for r in reqs}),
        "image_views": len(views),
        "completed_visual_iterations": len([i for i in iters
                                            if i.get("completed") and i.get("image_viewed")]),
        "requirement_change_versions": len([i for i in iters
                                            if i.get("type") == "requirement-change"]),
        "noop_renders": len(noops),
        "final_images": len([o for o in a.outputs.split(",") if o.endswith(".png")]),
    },
    "logs": {"requests": f"tmp/{rid}/{a.task}/requests.jsonl",
             "iterations": f"tmp/{rid}/{a.task}/iterations.jsonl",
             "filter": f"dsl_version startswith one of {prefixes}"},
    "outputs": [x for x in a.outputs.split(",") if x],
    "note": a.note,
    "unresolved_issues": [x for x in a.unresolved.split(";") if x],
    "cumulative_metrics": f"outputs/{rid}/{a.task}/task-metrics.json",
}
outdir.mkdir(parents=True, exist_ok=True)
(outdir / "task-metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2),
                                          encoding="utf-8")
print(json.dumps({"round": a.round, **metrics["counts"]}, ensure_ascii=False))
