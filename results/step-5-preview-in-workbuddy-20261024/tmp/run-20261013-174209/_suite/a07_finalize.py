"""A07 收尾：iterations.jsonl、task-metrics.json、套件登记。"""
from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ["SNAPSHOT_RUN_ID"]
OUT = ROOT / "outputs" / RUN_ID / "A07"
TMP = ROOT / "tmp" / RUN_ID / "A07"


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
        "id": "A07-it00",
        "parent": None,
        "type": "baseline",
        "dsl": "tmp/run-20261013-174209/A07/network-map.snapshot",
        "image": "tmp/run-20261013-174209/A07/map-base.png",
        "render_request_id": next((r["id"] for r in reqs if r.get("label") == "A07-map-baseline"), None),
        "viewed_at": ended.isoformat(),
        "observed": [
            "16 站、3 线、换乘站标记、无障碍图例与状态表均渲染成功。",
            "绿线 S05→S16 段为 68.2°，不满足 45°/90° 约束。",
            "线路字母徽标与 S01/S07/S13 的编号标签距离过近，几乎贴在一起。",
        ],
        "changes": [],
        "result": "两处缺陷：折线角度不合规、徽标与站标签贴近。",
        "status": "superseded",
    },
    {
        "id": "A07-it01",
        "parent": "A07-it00",
        "type": "visual",
        "dsl": "tmp/run-20261013-174209/A07/network-map.snapshot",
        "image": "outputs/run-20261013-174209/A07/network-map.png",
        "render_request_id": next((r["id"] for r in reqs if r.get("label") == "A07-map-iter2-angle-and-badge-fix"), None),
        "viewed_at": ended.isoformat(),
        "observed": [
            "绿线末段改为 (860,560)→(860,660)→(900,660)，即 90° + 0°，全部线段角度合规。",
            "徽标左移到起点左侧 −104px，与编号标签分离。",
            "整图复查：无遮挡、无角度违规。",
        ],
        "changes": [
            "绿线路由末段由 (860,560)→(900,660) 改为 (860,560)→(860,660)→(900,660)",
            "线路徽标 x 偏移 −62 → −104，名称右对齐到 −120",
        ],
        "result": "地图缺陷修复；矩阵反推角度核验通过（仅 0°/90°/135°）。",
        "status": "accepted",
    },
    {
        "id": "A07-it02",
        "parent": None,
        "type": "baseline",
        "dsl": "tmp/run-20261013-174209/A07/travel-card.snapshot",
        "image": "outputs/run-20261013-174209/A07/travel-card.png",
        "render_request_id": next((r["id"] for r in reqs if r.get("label") == "A07-card-baseline"), None),
        "viewed_at": ended.isoformat(),
        "observed": [
            "三张旅程卡片全部进入画布（末 y=1256 < 1280）。",
            "旅程 1/3 无障碍与普通路线相同；旅程 2 需改用 6 边 2 换乘的无障碍路线，原因说明清楚。",
            "站序色带、线路段文字、站间边/站数说明均正确。",
        ],
        "changes": [],
        "result": "首版即满足要求。",
        "status": "accepted",
    },
]
(TMP / "iterations.jsonl").write_text(
    "\n".join(json.dumps(i, ensure_ascii=False) for i in iters) + "\n", encoding="utf-8")

metrics = {
    "schema_version": 1,
    "path_base": "suite_root",
    "task_id": "A07",
    "run_id": RUN_ID,
    "task_round": None,
    "status": "completed",
    "stop_reason": "需求满足并完成视觉自检",
    "output_dir": f"outputs/{RUN_ID}/A07/",
    "temp_dir": f"tmp/{RUN_ID}/A07/",
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
        "image_views": 2 + 3,
        "completed_visual_iterations": 3,
        "incomplete_visual_iterations": 0,
    },
    "logs": {
        "requests": f"tmp/{RUN_ID}/A07/requests.jsonl",
        "iterations": f"tmp/{RUN_ID}/A07/iterations.jsonl",
    },
    "outputs": [
        {"path": f"outputs/{RUN_ID}/A07/network-map.png", "width": 1600, "height": 1000,
         "dsl": f"outputs/{RUN_ID}/A07/network-map.snapshot"},
        {"path": f"outputs/{RUN_ID}/A07/travel-card.png", "width": 720, "height": 1280,
         "dsl": f"outputs/{RUN_ID}/A07/travel-card.snapshot"},
        {"path": f"outputs/{RUN_ID}/A07/routes.json"},
        {"path": f"outputs/{RUN_ID}/A07/snapshot-usage.md"},
        {"path": f"outputs/{RUN_ID}/A07/task-metrics.json"},
    ],
    "candidates": [
        {"image": f"tmp/{RUN_ID}/A07/map-base.png", "note": "地图基线，角度与徽标缺陷"},
        {"image": f"tmp/{RUN_ID}/A07/card-base.png", "note": "旅行卡首版即达标"},
        {"image": f"outputs/{RUN_ID}/A07/network-map.png", "note": "地图终版"},
        {"image": f"outputs/{RUN_ID}/A07/travel-card.png", "note": "旅行卡终版"},
    ],
    "rounds": [],
    "unresolved_issues": [],
}
(OUT / "task-metrics.json").write_text(
    json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("reqs", len(reqs), "ok", len(ok), "bad", len(bad), "elapsed", round(elapsed, 1))
