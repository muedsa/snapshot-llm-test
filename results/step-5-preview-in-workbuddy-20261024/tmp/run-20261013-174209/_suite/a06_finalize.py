"""A06 收尾：iterations.jsonl、task-metrics.json、套件登记。"""
from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ["SNAPSHOT_RUN_ID"]
OUT = ROOT / "outputs" / RUN_ID / "A06"
TMP = ROOT / "tmp" / RUN_ID / "A06"


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
        "id": "A06-it00",
        "parent": None,
        "type": "baseline",
        "dsl": "tmp/run-20261013-174209/A06/dependency-map.snapshot",
        "image": "tmp/run-20261013-174209/A06/base.png",
        "render_request_id": next((r["id"] for r in reqs if r.get("label") == "A06-baseline"), None),
        "viewed_at": ended.isoformat(),
        "observed": [
            "14 个节点按 11 个拓扑层从左到右排列，层内并行关系清晰。",
            "16 条先决边用深灰实线 + 实心三角箭头，方向可辨。",
            "2 条反馈边用红色弯折线绕画布顶部通道进入目标上缘，未与先决边混淆。",
            "最长路径 11 个节点用蓝色边框高亮。",
            "分区放大（左部多层、第 5 层起单链、反馈通道）均无文字遮挡或断线。",
        ],
        "changes": [],
        "result": "首版即满足要求，未发现需修复缺陷。",
        "status": "accepted",
    },
]
(TMP / "iterations.jsonl").write_text(
    "\n".join(json.dumps(i, ensure_ascii=False) for i in iters) + "\n", encoding="utf-8")

metrics = {
    "schema_version": 1,
    "path_base": "suite_root",
    "task_id": "A06",
    "run_id": RUN_ID,
    "task_round": None,
    "status": "completed",
    "stop_reason": "需求满足并完成视觉自检",
    "output_dir": f"outputs/{RUN_ID}/A06/",
    "temp_dir": f"tmp/{RUN_ID}/A06/",
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
        "dsl_versions": 1,
        "image_views": 1 + 3,
        "completed_visual_iterations": 1,
        "incomplete_visual_iterations": 0,
    },
    "logs": {
        "requests": f"tmp/{RUN_ID}/A06/requests.jsonl",
        "iterations": f"tmp/{RUN_ID}/A06/iterations.jsonl",
    },
    "outputs": [
        {"path": f"outputs/{RUN_ID}/A06/dependency-map.png", "width": 1600, "height": 1000,
         "dsl": f"outputs/{RUN_ID}/A06/dependency-map.snapshot"},
        {"path": f"outputs/{RUN_ID}/A06/graph-audit.json"},
        {"path": f"outputs/{RUN_ID}/A06/snapshot-usage.md"},
        {"path": f"outputs/{RUN_ID}/A06/task-metrics.json"},
    ],
    "candidates": [
        {"image": f"outputs/{RUN_ID}/A06/dependency-map.png", "note": "首版即达标，直接采纳"},
    ],
    "rounds": [],
    "unresolved_issues": [],
}
(OUT / "task-metrics.json").write_text(
    json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("reqs", len(reqs), "ok", len(ok), "bad", len(bad), "elapsed", round(elapsed, 1))
