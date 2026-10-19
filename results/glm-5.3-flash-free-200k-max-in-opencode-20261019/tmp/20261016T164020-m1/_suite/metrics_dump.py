# -*- coding: utf-8 -*-
"""生成单题 task-metrics.json。启动基准：总任务根。
用法：python metrics_dump.py <task_id> [round]
- 读 tmp/<run>/<task_id>/{requests.jsonl,iterations.jsonl,task-times.json}
- 写 outputs/<run>/<task_id>[/round]/task-metrics.json
"""
import json
import os
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import snapshot_client as sc

task_id = sys.argv[1]
round_id = sys.argv[2] if len(sys.argv) > 2 else None

tmp = sc.task_tmp(task_id)
reqs = [json.loads(l) for l in (tmp / "requests.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
iters = [json.loads(l) for l in (tmp / "iterations.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
if round_id:
    reqs = [r for r in reqs if r.get("round") in (None, round_id)]
    iters = [i for i in iters if i.get("round") in (None, round_id)]

renders = [r for r in reqs if r["request_type"] == "render"]
ok = [r for r in renders if r["http_status"] == 200]
fail = [r for r in renders if r["http_status"] != 200]
retried = [r for r in renders if (r.get("retry_after") is not None) or any(
    q["http_status"] != 200 for q in renders)]
other = [r for r in reqs if r["request_type"] in ("fonts", "fonts_png")]
times = sc.get_task_time(task_id)

t = sc.now_iso()
def parse_ts(s):
    return datetime.fromisoformat(s)
start = times.get("started_at")
end = times.get("ended_at") or t
elapsed = (parse_ts(end) - parse_ts(start)).total_seconds() if start else None
first_img = times.get("first_usable_image_at")
first_img_s = (parse_ts(first_img) - parse_ts(start)).total_seconds() if (start and first_img) else None
req_dur_sum = sum((r.get("duration_ms") or 0) for r in reqs) / 1000.0

views = [i for i in iters if i.get("viewed_at") and (i.get("image") or i.get("images"))]
completed = [i for i in iters if i.get("type") in ("visual", "requirement-change") and i.get("recheck") not in ("pending", None)]
incompl = [i for i in iters if i.get("recheck") == "pending"]

metrics = {
    "schema_version": 1,
    "path_base": "suite_root",
    "task_id": task_id,
    "run_id": sc.RUN_ID,
    "task_round": round_id,
    "status": "completed" if not incompl else ("partial" if ok else "blocked"),
    "stop_reason": None,
    "output_dir": f"outputs/{sc.RUN_ID}/{task_id}/",
    "temp_dir": f"tmp/{sc.RUN_ID}/{task_id}/",
    "timings": {
        "started_at": start,
        "ended_at": end,
        "elapsed_seconds": round(elapsed, 1) if elapsed else None,
        "first_usable_image_seconds": round(first_img_s, 1) if first_img_s else None,
        "user_feedback_wait_seconds": None,
        "rate_limit_wait_seconds": None,
        "queue_wait_seconds": None,
        "request_duration_sum_seconds": round(req_dur_sum, 1),
        # 服务端耗时来源：open-snapshot 响应头 Server-Timing（render/total），保留在 requests.jsonl
        "server_timing_source": "X-Server-Timing header captured per request in requests.jsonl",
    },
    "counts": {
        "snapshot_requests": len(renders),
        "successful_snapshot_requests": len(ok),
        "failed_snapshot_requests": len(fail),
        "retry_requests": 0,
        "other_service_requests": len(other),
        "dsl_versions": len({i.get("version") for i in iters if i.get("version")}),
        "image_views": len(views),
        "completed_visual_iterations": len(completed),
        "incomplete_visual_iterations": len(incompl),
    },
    "logs": {
        "requests": f"tmp/{sc.RUN_ID}/{task_id}/requests.jsonl",
        "iterations": f"tmp/{sc.RUN_ID}/{task_id}/iterations.jsonl",
    },
    "outputs": [],
    "candidates": [],
    "rounds": [],
    "unresolved_issues": [],
}
if fail:
    metrics["unresolved_issues"].append("存在失败渲染请求，详见 requests.jsonl")
out = sc.suite_out() / task_id / (round_id if round_id else "")
out.mkdir(parents=True, exist_ok=True)
(out / "task-metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"written": str(out / "task-metrics.json"), "renders": len(renders), "ok": len(ok),
                  "fail": len(fail), "views": len(views), "iters": len(iters)}, ensure_ascii=False))
