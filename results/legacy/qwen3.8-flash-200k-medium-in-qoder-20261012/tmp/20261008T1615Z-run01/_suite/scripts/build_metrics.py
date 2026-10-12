"""Build task-metrics.json for one task from its requests/iterations logs.

Run from suite root. Usage:
  python tmp/<run_id>/_suite/scripts/build_metrics.py --task A01 --status completed \
      --started 2026-10-08T08:15:00+00:00 --rounds 1
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
ap.add_argument("--status", default="completed")
ap.add_argument("--stop-reason", default="需求满足并完成视觉自检")
ap.add_argument("--started", default=None)
ap.add_argument("--first-image", default=None)
ap.add_argument("--outputs", default="")
ap.add_argument("--unresolved", default="")
ap.add_argument("--extra", default=None, help="path to json with extra keys")
a = ap.parse_args()

task = a.task
temp = root / "tmp" / rid / task
out = root / "outputs" / rid / task


def read_jsonl(p):
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


reqs = read_jsonl(temp / "requests.jsonl")
shared = read_jsonl(root / "tmp" / rid / "_suite" / "requests.jsonl")
allreqs = reqs + shared
renders = [r for r in reqs if r.get("kind") == "render"]
others = [r for r in reqs if r.get("kind") != "render"]
ok = [r for r in renders if r.get("http_status") == 200]
bad = [r for r in renders if r.get("http_status") != 200]
iters = read_jsonl(temp / "iterations.jsonl")
versions = sorted({(r.get("dsl_version") or "").replace("-final", "")
                   for r in reqs if r.get("dsl_version")
                   and not r["dsl_version"].startswith("zoom")})
completed_vis = [i for i in iters if i["type"] == "visual" and i["completed"]]
incomplete_vis = [i for i in iters if i["type"] == "visual" and not i["completed"]]
views = [i for i in iters if i.get("image_viewed")]

started = a.started
ended = datetime.now(timezone.utc).isoformat()
elapsed = None
if started:
    elapsed = round((datetime.fromisoformat(ended)
                     - datetime.fromisoformat(started)).total_seconds(), 1)
first_img = None
if a.first_image and started:
    first_img = round((datetime.fromisoformat(a.first_image)
                       - datetime.fromisoformat(started)).total_seconds(), 1)
elif ok and started:
    first_img = round((datetime.fromisoformat(ok[0]["ended_at"])
                       - datetime.fromisoformat(started)).total_seconds(), 1)

q = [r for r in renders if r.get("http_status") in (429, 503)]
rate_wait = sum(float(r["retry_after"]) for r in q if r.get("retry_after")) if q else None
st = [r.get("server_timing") for r in ok if r.get("server_timing")]
queue_vals = []
for s in st:
    for part in s.split(","):
        if part.strip().startswith("queue;dur="):
            queue_vals.append(float(part.strip().split("=")[1]))

metrics = {
    "schema_version": 1, "path_base": "suite_root",
    "task_id": task, "run_id": rid, "task_round": 1,
    "status": a.status, "stop_reason": a.stop_reason,
    "output_dir": f"outputs/{rid}/{task}/", "temp_dir": f"tmp/{rid}/{task}/",
    "timings": {
        "started_at": started, "ended_at": ended, "elapsed_seconds": elapsed,
        "first_usable_image_seconds": first_img,
        "user_feedback_wait_seconds": 0 if len(iters) else None,
        "rate_limit_wait_seconds": rate_wait,
        "queue_wait_seconds": round(sum(queue_vals), 3) if queue_vals else None,
        "request_duration_sum_seconds": round(sum(r["duration_seconds"] or 0
                                                  for r in reqs), 3),
        "requests_missing_duration": [r["request_id"] for r in reqs
                                      if r.get("duration_seconds") is None],
        "shared_doc_requests_reused": len(shared),
        "shared_doc_duration_seconds": round(sum(r["duration_seconds"] for r in shared), 3),
        "shared_doc_note": "文档抓取属 shared，只在 _suite 计一次，不计入本题耗时之和",
        "server_timing_source": "Server-Timing response header captured in requests.jsonl",
        **({"duration_note": "duration_seconds=null 的请求（被终止或无响应）按 0 参与求和，"
                             "其 ID 列在 requests_missing_duration，不猜测耗时"}
           if any(r.get("duration_seconds") is None for r in reqs) else {}),
    },
    "counts": {
        "snapshot_requests": len(renders),
        "successful_snapshot_requests": len(ok),
        "failed_snapshot_requests": len(bad),
        "retry_requests": len([r for r in renders
                               if (r.get("attempt_note") or "").startswith("retry")]),
        "other_service_requests": len(others),
        "dsl_versions": len(versions),
        "image_views": len(views),
        "completed_visual_iterations": len(completed_vis),
        "incomplete_visual_iterations": len(incomplete_vis),
    },
    "logs": {"requests": f"tmp/{rid}/{task}/requests.jsonl",
             "iterations": f"tmp/{rid}/{task}/iterations.jsonl"},
    "outputs": [x for x in a.outputs.split(",") if x],
    "candidates": sorted(p.name for p in temp.glob("*.snapshot")),
    "rounds": [], "unresolved_issues": [x for x in a.unresolved.split(";") if x],
}
if a.extra:
    metrics.update(json.loads(Path(a.extra).read_text(encoding="utf-8")))
out.mkdir(parents=True, exist_ok=True)
(out / "task-metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2),
                                       encoding="utf-8")
print(json.dumps(metrics["counts"], ensure_ascii=False))
