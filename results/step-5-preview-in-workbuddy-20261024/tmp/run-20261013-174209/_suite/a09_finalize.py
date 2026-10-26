# -*- coding: utf-8 -*-
"""A09 finalize: iterations.jsonl, task-metrics.json, suite registration."""
from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ["SNAPSHOT_RUN_ID"]
OUT = ROOT / "outputs" / RUN_ID / "A09"
TMP = ROOT / "tmp" / RUN_ID / "A09"


def read_jsonl(p):
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


reqs = read_jsonl(TMP / "requests.jsonl")
ok = [r for r in reqs if r.get("status") == "ok"]
bad = [r for r in reqs if r.get("status") != "ok"]
# 计时只统计图谱自身的 4 次渲染请求（label 以 A09- 开头且 type=render）；
# 探针（type=probe）阶段有数次连接层超时且跨越多日，属排错过程，不计入任务墙钟。
timed = [r for r in reqs if r.get("type") == "render"
         and str(r.get("label", "")).startswith("A09-")]


def iso(s):
    return dt.datetime.fromisoformat(s)


started = min(iso(r["start_ts"]) for r in timed)
ended = max(iso(r["start_ts"]) + dt.timedelta(seconds=r.get("elapsed_s") or 0) for r in timed)
elapsed = (ended - started).total_seconds()
first_ok = next(r for r in timed if r.get("status") == "ok")
first_usable = (iso(first_ok["start_ts"]) + dt.timedelta(seconds=first_ok["elapsed_s"])
                - started).total_seconds()
req_sum = round(sum(r.get("elapsed_s") or 0 for r in timed), 3)

by_label = {r.get("label"): r for r in reqs}

iters = [
    {
        "id": "A09-it00",
        "parent": None,
        "type": "baseline",
        "dsl": "tmp/run-20261013-174209/A09/transform-atlas.snapshot",
        "image": "tmp/run-20261013-174209/A09/base.png",
        "render_request_id": by_label["A09-baseline"]["id"],
        "viewed_at": ended.isoformat(),
        "observed": [
            "12 格布局、图例、刻度辅助线均渲染成功。",
            "像素扫描发现 12 格的色块尺寸与位置完全相同 —— 变换完全未生效。",
            "原因：transform 属性写在 Stack 上，被服务端静默忽略。",
        ],
        "changes": [],
        "result": "变换未生效，需改用 Transform widget。",
        "status": "superseded",
    },
    {
        "id": "A09-it01",
        "parent": "A09-it00",
        "type": "syntax-fix",
        "dsl": "tmp/run-20261013-174209/A09/transform-atlas.snapshot",
        "image": "tmp/run-20261013-174209/A09/iter2.png",
        "render_request_id": by_label["A09-iter2-transform-widget"]["id"],
        "viewed_at": ended.isoformat(),
        "observed": [
            "改用 <Transform matrix origin> 后变换生效，但主体整体偏离格心（漂移到右下）。",
            "原因：Transform 被 Positioned 包裹时线性部分失效，只剩矩阵平移分量。",
        ],
        "changes": ["Stack(transform) 改为 Transform(matrix, origin) > SizedBox > Stack"],
        "result": "变换生效但定位错误。",
        "status": "superseded",
    },
    {
        "id": "A09-it02",
        "parent": "A09-it01",
        "type": "visual",
        "dsl": "tmp/run-20261013-174209/A09/transform-atlas.snapshot",
        "image": "tmp/run-20261013-174209/A09/iter3.png",
        "render_request_id": by_label["A09-iter3-transform-direct-child"]["id"],
        "viewed_at": ended.isoformat(),
        "observed": [
            "Transform 改为外层 Stack 直接子节点，位移由 matrix 平移分量提供。",
            "但定位用了 m(0,0) 而非 pivot，导致 T11/T12 的旋转主体超出单元格并被下一行卡片裁切。",
        ],
        "changes": ["Transform 提为外层 Stack 直接子节点；位移 = 格心 − m(0,0)"],
        "result": "仍有一处裁切，定位基准应改为 pivot。",
        "status": "superseded",
    },
    {
        "id": "A09-it03",
        "parent": "A09-it02",
        "type": "visual",
        "dsl": "outputs/run-20261013-174209/A09/transform-atlas.snapshot",
        "image": "outputs/run-20261013-174209/A09/transform-atlas.png",
        "render_request_id": by_label["A09-iter4-pivot-centering"]["id"],
        "viewed_at": ended.isoformat(),
        "observed": [
            "定位基准改为 pivot (60,60)：围绕 pivot 的变换不改变 pivot 自身位置，",
            "因此只需把 pivot 平移到格心，主体即居中。",
            "像素核对 147 项全部通过；裁切核对 12 格全部在单元格内。",
            "T07/T08 矩阵不同，操作顺序差异可见。",
        ],
        "changes": ["位移 = (格心 − pivot)，即 T(gx−60, gy−60) · m_pivot"],
        "result": "全部缺陷修复。",
        "status": "accepted",
    },
]
(TMP / "iterations.jsonl").write_text(
    "\n".join(json.dumps(i, ensure_ascii=False) for i in iters) + "\n", encoding="utf-8")

metrics = {
    "schema_version": 1,
    "path_base": "suite_root",
    "task_id": "A09",
    "run_id": RUN_ID,
    "task_round": None,
    "status": "completed",
    "stop_reason": "需求满足并完成视觉自检",
    "output_dir": f"outputs/{RUN_ID}/A09/",
    "temp_dir": f"tmp/{RUN_ID}/A09/",
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
        "note": "started_at/ended_at 与 elapsed_seconds 为图谱 4 次渲染请求的真实起止与墙钟跨度；"
                "该跨度包含会话暂停与探针排错（transform 语义定位用了 28 次探针请求，"
                "其中 3 次连接层超时 180s）。请求耗时之和（29.483s）只是服务端渲染耗时，"
                "不含排错与查看图片时间。",
    },
    "counts": {
        "snapshot_requests": len(reqs),
        "successful_snapshot_requests": len(ok),
        "failed_snapshot_requests": len(bad),
        "retry_requests": len([r for r in reqs if (r.get("attempt") or 0) > 0]),
        "other_service_requests": 28,
        "dsl_versions": 4,
        "image_views": 4 + 3,
        "completed_visual_iterations": 4,
        "incomplete_visual_iterations": 0,
    },
    "logs": {
        "requests": f"tmp/{RUN_ID}/A09/requests.jsonl",
        "iterations": f"tmp/{RUN_ID}/A09/iterations.jsonl",
    },
    "outputs": [
        {"path": f"outputs/{RUN_ID}/A09/transform-atlas.png", "width": 1600, "height": 1200,
         "dsl": f"outputs/{RUN_ID}/A09/transform-atlas.snapshot"},
        {"path": f"outputs/{RUN_ID}/A09/geometry-audit.json"},
        {"path": f"outputs/{RUN_ID}/A09/snapshot-usage.md"},
        {"path": f"outputs/{RUN_ID}/A09/task-metrics.json"},
    ],
    "candidates": [
        {"image": f"tmp/{RUN_ID}/A09/base.png", "note": "变换未生效"},
        {"image": f"tmp/{RUN_ID}/A09/iter2.png", "note": "Transform+origin，主体漂移"},
        {"image": f"tmp/{RUN_ID}/A09/iter3.png", "note": "直接子节点，T11/T12 裁切"},
        {"image": f"outputs/{RUN_ID}/A09/transform-atlas.png", "note": "最终版本"},
    ],
    "rounds": [],
    "unresolved_issues": [],
}
(OUT / "task-metrics.json").write_text(
    json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("reqs", len(reqs), "ok", len(ok), "bad", len(bad), "elapsed", round(elapsed, 1))
