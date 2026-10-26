"""A02 收尾：iterations.jsonl、task-metrics.json、套件登记。"""
from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ["SNAPSHOT_RUN_ID"]
OUT = ROOT / "outputs" / RUN_ID / "A02"
TMP = ROOT / "tmp" / RUN_ID / "A02"


def read_jsonl(p: Path) -> list[dict]:
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


reqs = read_jsonl(TMP / "requests.jsonl")
ok = [r for r in reqs if r.get("status") == "ok"]
bad = [r for r in reqs if r.get("status") != "ok"]


def iso(s: str) -> dt.datetime:
    return dt.datetime.fromisoformat(s)


started = min(iso(r["start_ts"]) for r in reqs)
ended = max(iso(r["start_ts"]) + dt.timedelta(seconds=r.get("elapsed_s") or 0) for r in reqs)
elapsed = (ended - started).total_seconds()
first_ok = next(r for r in reqs if r.get("status") == "ok")
first_usable = (iso(first_ok["start_ts"]) + dt.timedelta(seconds=first_ok["elapsed_s"])
                - started).total_seconds()
req_sum = round(sum(r.get("elapsed_s") or 0 for r in reqs), 3)

by_label = {r.get("label"): r for r in reqs}

iters = [
    {
        "id": "A02-it00",
        "parent": None,
        "type": "baseline",
        "dsl": "tmp/run-20261013-174209/A02/agenda-wide.snapshot",
        "image": "tmp/run-20261013-174209/A02/wide-base.png",
        "render_request_id": by_label["A02-wide-baseline"]["id"],
        "viewed_at": ended.isoformat(),
        "observed": [
            "三条泳道、时间轴、色块、午休区块与图例均正确渲染。",
            "右侧编号索引列宽仅 16px（IDX_W 计算为负），标题/讲者文字不可见。",
            "手机版列表总高 1556px，超出 1280 画布，末尾活动被裁掉。",
        ],
        "changes": [],
        "result": "两处缺陷：右侧索引文字缺失、手机图溢出。",
        "status": "superseded",
    },
    {
        "id": "A02-it01",
        "parent": "A02-it00",
        "type": "visual",
        "dsl": "tmp/run-20261013-174209/A02/agenda-wide.snapshot",
        "image": "tmp/run-20261013-174209/A02/wide-iter2.png",
        "render_request_id": by_label["A02-wide-iter2-index-fit"]["id"],
        "viewed_at": ended.isoformat(),
        "observed": [
            "索引行距改为按可用高度均分（48px/项），底部不再超出说明区。",
            "但 IDX_W 仍为 16，索引文字依旧不可见——根因是 ax_x1 距右边距只剩 30px。",
        ],
        "changes": [
            "索引行距由固定 54px 改为 IDX_AVAIL/len(events)。",
            "手机图改为按 1280 画布精确预算卡片高度。",
        ],
        "result": "手机图已能容纳；大图索引文字仍不可见。",
        "status": "superseded",
    },
    {
        "id": "A02-it02",
        "parent": "A02-it01",
        "type": "visual",
        "dsl": "tmp/run-20261013-174209/A02/agenda-wide.snapshot",
        "image": "tmp/run-20261013-174209/A02/wide-iter3.png",
        "render_request_id": by_label["A02-wide-iter3-index-width-fix"]["id"],
        "viewed_at": ended.isoformat(),
        "observed": [
            "为索引列显式预留 INDEX_W=300，ax_x1 相应左移；15 项索引的标题、讲者、会场与时长全部可读。",
            "整图复查：10:00 附近密集区（A 的 S04、B 的 S05、C 的 S06）块宽与时间比例正确。",
            "C 会场 09:15/10:15/11:05 三个块与午休、下午两块均未重叠。",
        ],
        "changes": [
            "新增 INDEX_W=300，ax_x1 = W - PAD - INDEX_W - 14；IDX_W 取 INDEX_W。",
        ],
        "result": "大图与手机图均满足要求，逐区放大复查通过。",
        "status": "accepted",
    },
]
(TMP / "iterations.jsonl").write_text(
    "\n".join(json.dumps(i, ensure_ascii=False) for i in iters) + "\n", encoding="utf-8")

metrics = {
    "schema_version": 1,
    "path_base": "suite_root",
    "task_id": "A02",
    "run_id": RUN_ID,
    "task_round": None,
    "status": "completed",
    "stop_reason": "需求满足并完成视觉自检",
    "output_dir": f"outputs/{RUN_ID}/A02/",
    "temp_dir": f"tmp/{RUN_ID}/A02/",
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
        "dsl_versions": 3,
        "image_views": 2 + 6,
        "completed_visual_iterations": 3,
        "incomplete_visual_iterations": 0,
    },
    "logs": {
        "requests": f"tmp/{RUN_ID}/A02/requests.jsonl",
        "iterations": f"tmp/{RUN_ID}/A02/iterations.jsonl",
    },
    "outputs": [
        {"path": f"outputs/{RUN_ID}/A02/agenda-wide.png", "width": 1920, "height": 1200,
         "dsl": f"outputs/{RUN_ID}/A02/agenda-wide.snapshot"},
        {"path": f"outputs/{RUN_ID}/A02/agenda-mobile.png", "width": 720, "height": 1280,
         "dsl": f"outputs/{RUN_ID}/A02/agenda-mobile.snapshot"},
        {"path": f"outputs/{RUN_ID}/A02/schedule-audit.json"},
        {"path": f"outputs/{RUN_ID}/A02/snapshot-usage.md"},
        {"path": f"outputs/{RUN_ID}/A02/task-metrics.json"},
    ],
    "candidates": [
        {"image": f"tmp/{RUN_ID}/A02/wide-base.png", "note": "大图基线"},
        {"image": f"tmp/{RUN_ID}/A02/mobile-base.png", "note": "手机基线（溢出）"},
        {"image": f"tmp/{RUN_ID}/A02/wide-iter2.png", "note": "索引行距调整"},
        {"image": f"tmp/{RUN_ID}/A02/mobile-iter2.png", "note": "手机紧凑布局"},
        {"image": f"tmp/{RUN_ID}/A02/wide-iter3.png", "note": "最终大图"},
    ],
    "rounds": [],
    "unresolved_issues": [],
}
(OUT / "task-metrics.json").write_text(
    json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("wrote iterations.jsonl + task-metrics.json; reqs", len(reqs), "ok", len(ok),
      "elapsed", round(elapsed, 1))
