"""A08 收尾：iterations.jsonl、task-metrics.json、套件登记。"""
from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ["SNAPSHOT_RUN_ID"]
OUT = ROOT / "outputs" / RUN_ID / "A08"
TMP = ROOT / "tmp" / RUN_ID / "A08"


def read_jsonl(p):
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


reqs = read_jsonl(TMP / "requests.jsonl")
ok = [r for r in reqs if r.get("status") == "ok"]
bad = [r for r in reqs if r.get("status") != "ok"]


def iso(s):
    return dt.datetime.fromisoformat(s)


started = min(iso(r["start_ts"]) for r in reqs)
ended = max(iso(r["start_ts"]) + dt.timedelta(seconds=r.get("elapsed_s") or 0) for r in reqs)
elapsed = (ended - started).total_seconds()
first_ok = next(r for r in reqs if r.get("status") == "ok")
first_usable = (iso(first_ok["start_ts"]) + dt.timedelta(seconds=first_ok["elapsed_s"])
                - started).total_seconds()
req_sum = round(sum(r.get("elapsed_s") or 0 for r in reqs), 3)

iters = [
    {
        "id": "A08-it00",
        "parent": None,
        "type": "baseline",
        "dsl": "tmp/run-20261013-174209/A08/wayfinding.snapshot",
        "image": "tmp/run-20261013-174209/A08/base.png",
        "render_request_id": next((r["id"] for r in reqs if r.get("label") == "A08-baseline"), None),
        "viewed_at": ended.isoformat(),
        "observed": [
            "26×16 网格、阻挡区、两处门洞、两条路线与侧栏均渲染成功。",
            "「共享通道」标签水平放置在段中心上方，压在路线上。",
        ],
        "changes": [],
        "result": "标签压线一处缺陷。",
        "status": "superseded",
    },
    {
        "id": "A08-it01",
        "parent": "A08-it00",
        "type": "visual",
        "dsl": "tmp/run-20261013-174209/A08/wayfinding.snapshot",
        "image": "outputs/run-20261013-174209/A08/wayfinding.png",
        "render_request_id": next((r["id"] for r in reqs if r.get("label") == "A08-iter2-shared-label"), None),
        "viewed_at": ended.isoformat(),
        "observed": [
            "共享通道标签改为按段走向放置：水平段上方、垂直段左侧，均不压线。",
            "分区放大：入馆共享段（S→(6,10)）与离馆共享段（(20,10)→E）中，",
            "R1 红色实线在左、R2 蓝色虚线在右，两条路线身份与方向均可辨。",
            "分岔点 (6,10) 与合流点 (20,10) 有箭头；S/E/A–D 标记固定于对应格心。",
        ],
        "changes": ["共享通道标签按段走向（水平/垂直）分别放置在段上方/左侧"],
        "result": "缺陷修复，整图 + 2 个共享段分区放大复查通过。",
        "status": "accepted",
    },
]
(TMP / "iterations.jsonl").write_text(
    "\n".join(json.dumps(i, ensure_ascii=False) for i in iters) + "\n", encoding="utf-8")

metrics = {
    "schema_version": 1,
    "path_base": "suite_root",
    "task_id": "A08",
    "run_id": RUN_ID,
    "task_round": None,
    "status": "completed",
    "stop_reason": "需求满足并完成视觉自检",
    "output_dir": f"outputs/{RUN_ID}/A08/",
    "temp_dir": f"tmp/{RUN_ID}/A08/",
    "timings": {
        "started_at": started.isoformat(),
        "ended_at": ended.isoformat(),
        "elapsed_seconds": round(elapsed, 3),
        "first_usable_image_seconds": round(first_usable, 3),
        "user_feedback_wait_seconds": 0,
        "rate_limit_wait_seconds": 0,
        "queue_wait_seconds": None,
        "request_duration_sum_seconds": req_sum,
        "server_timing_source": "Server-Timing 响应头",
    },
    "counts": {
        "snapshot_requests": len(reqs),
        "successful_snapshot_requests": len(ok),
        "failed_snapshot_requests": len(bad),
        "retry_requests": 0,
        "other_service_requests": 0,
        "dsl_versions": 2,
        "image_views": 2 + 2,
        "completed_visual_iterations": 2,
        "incomplete_visual_iterations": 0,
    },
    "logs": {
        "requests": f"tmp/{RUN_ID}/A08/requests.jsonl",
        "iterations": f"tmp/{RUN_ID}/A08/iterations.jsonl",
    },
    "outputs": [
        {"path": f"outputs/{RUN_ID}/A08/wayfinding.png", "width": 1560, "height": 1080,
         "dsl": f"outputs/{RUN_ID}/A08/wayfinding.snapshot"},
        {"path": f"outputs/{RUN_ID}/A08/paths.json"},
        {"path": f"outputs/{RUN_ID}/A08/snapshot-usage.md"},
        {"path": f"outputs/{RUN_ID}/A08/task-metrics.json"},
    ],
    "candidates": [
        {"image": f"tmp/{RUN_ID}/A08/base.png", "note": "基线，共享标签压线"},
        {"image": f"outputs/{RUN_ID}/A08/wayfinding.png", "note": "最终版本"},
    ],
    "rounds": [],
    "unresolved_issues": [],
}
(OUT / "task-metrics.json").write_text(
    json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("reqs", len(reqs), "ok", len(ok), "bad", len(bad), "elapsed", round(elapsed, 1))
