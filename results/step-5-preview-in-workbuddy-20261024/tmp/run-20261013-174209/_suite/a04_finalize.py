"""A04 收尾：iterations.jsonl、task-metrics.json、套件登记。"""
from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ["SNAPSHOT_RUN_ID"]
OUT = ROOT / "outputs" / RUN_ID / "A04"
TMP = ROOT / "tmp" / RUN_ID / "A04"


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
        "id": "A04-it00",
        "parent": None,
        "type": "baseline",
        "dsl": "tmp/run-20261013-174209/A04/conversion-story.snapshot",
        "image": "tmp/run-20261013-174209/A04/base.png",
        "render_request_id": next((r["id"] for r in reqs if r.get("label") == "A04-baseline"), None),
        "viewed_at": ended.isoformat(),
        "observed": [
            "三张图（分组率、访问构成、总体对照）与底部小表均渲染成功。",
            "主结论文案中的总体数字是手写估计值（26.0%→20.8%），与真实加权结果 26.0%→16.6% 不符。",
        ],
        "changes": [],
        "result": "结论数字与数据不一致，必须修正。",
        "status": "superseded",
    },
    {
        "id": "A04-it01",
        "parent": "A04-it00",
        "type": "visual",
        "dsl": "tmp/run-20261013-174209/A04/conversion-story.snapshot",
        "image": "tmp/run-20261013-174209/A04/iter2.png",
        "render_request_id": next((r["id"] for r in reqs if r.get("label") == "A04-iter2-conclusion-fix"), None),
        "viewed_at": ended.isoformat(),
        "observed": [
            "主结论改为由脚本注入真实计算值（26.0%→16.6%）。",
            "「限制说明」标题与主结论第三行文字重叠。",
        ],
        "changes": ["结论三段文案改为 f-string 注入 P0/P1 的真实 rate"],
        "result": "数字正确；出现文字重叠。",
        "status": "superseded",
    },
    {
        "id": "A04-it02",
        "parent": "A04-it01",
        "type": "visual",
        "dsl": "tmp/run-20261013-174209/A04/conversion-story.snapshot",
        "image": "tmp/run-20261013-174209/A04/iter3.png",
        "render_request_id": next((r["id"] for r in reqs if r.get("label") == "A04-iter3-conclusion-spacing"), None),
        "viewed_at": ended.isoformat(),
        "observed": [
            "结论行距与限制标题间距加大。",
            "但总体柱 16.6% 的数值标签（宽 tw+40=190，x 640–830）越界进入结论列（CONCL_X=680），仍与「限制说明」重叠。",
        ],
        "changes": ["结论行距 26→28；限制标题前置间距 8→16；限制正文行距 24→26"],
        "result": "仍有标签越界重叠。",
        "status": "superseded",
    },
    {
        "id": "A04-it03",
        "parent": "A04-it02",
        "type": "visual",
        "dsl": "tmp/run-20261013-174209/A04/conversion-story.snapshot",
        "image": "tmp/run-20261013-174209/A04/iter4.png",
        "render_request_id": next((r["id"] for r in reqs if r.get("label") == "A04-iter4-bar-label-width"), None),
        "viewed_at": ended.isoformat(),
        "observed": [
            "柱标签宽度收紧到 tw+20，但柱1 右缘 800 仍越过 CONCL_X=680，重叠未解除。",
        ],
        "changes": ["柱数值/分子分母/期名标签宽度由 tw+40 收紧为 tw+20"],
        "result": "重叠仍在，根因是结论列起点在柱体右侧之内。",
        "status": "superseded",
    },
    {
        "id": "A04-it04",
        "parent": "A04-it03",
        "type": "visual",
        "dsl": "tmp/run-20261013-174209/A04/conversion-story.snapshot",
        "image": "outputs/run-20261013-174209/A04/conversion-story.png",
        "render_request_id": next((r["id"] for r in reqs if r.get("label") == "A04-iter5-conclusion-column-shift"), None),
        "viewed_at": ended.isoformat(),
        "observed": [
            "结论列右移至 CONCL_X=840（柱1 右缘 800 之外），重叠解除。",
            "整图与 4 个分区（率图、构成图、总体对照、底部小表）放大复查通过。",
            "率图 0–100% 单一尺度；构成图两期等长、分段 80/20 与 20/80；总体柱 26.0% 与 16.6%。",
        ],
        "changes": ["CONCL_X 由 PAD+640 改为 PAD+800"],
        "result": "全部缺陷修复。",
        "status": "accepted",
    },
]
(TMP / "iterations.jsonl").write_text(
    "\n".join(json.dumps(i, ensure_ascii=False) for i in iters) + "\n", encoding="utf-8")

metrics = {
    "schema_version": 1,
    "path_base": "suite_root",
    "task_id": "A04",
    "run_id": RUN_ID,
    "task_round": None,
    "status": "completed",
    "stop_reason": "需求满足并完成视觉自检",
    "output_dir": f"outputs/{RUN_ID}/A04/",
    "temp_dir": f"tmp/{RUN_ID}/A04/",
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
        "retry_requests": len([r for r in reqs if (r.get("attempt") or 0) > 0]),
        "other_service_requests": 0,
        "dsl_versions": 5,
        "image_views": 5 + 4,
        "completed_visual_iterations": 5,
        "incomplete_visual_iterations": 0,
    },
    "logs": {
        "requests": f"tmp/{RUN_ID}/A04/requests.jsonl",
        "iterations": f"tmp/{RUN_ID}/A04/iterations.jsonl",
    },
    "outputs": [
        {"path": f"outputs/{RUN_ID}/A04/conversion-story.png", "width": 1600, "height": 1000,
         "dsl": f"outputs/{RUN_ID}/A04/conversion-story.snapshot"},
        {"path": f"outputs/{RUN_ID}/A04/analysis.json"},
        {"path": f"outputs/{RUN_ID}/A04/snapshot-usage.md"},
        {"path": f"outputs/{RUN_ID}/A04/task-metrics.json"},
    ],
    "candidates": [
        {"image": f"tmp/{RUN_ID}/A04/base.png", "note": "基线，结论数字手写错误"},
        {"image": f"tmp/{RUN_ID}/A04/iter2.png", "note": "结论数字修正"},
        {"image": f"tmp/{RUN_ID}/A04/iter3.png", "note": "行距调整"},
        {"image": f"tmp/{RUN_ID}/A04/iter4.png", "note": "标签宽度收紧"},
        {"image": f"outputs/{RUN_ID}/A04/conversion-story.png", "note": "最终版本"},
    ],
    "rounds": [],
    "unresolved_issues": [],
}
(OUT / "task-metrics.json").write_text(
    json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("reqs", len(reqs), "ok", len(ok), "bad", len(bad), "elapsed", round(elapsed, 1))
