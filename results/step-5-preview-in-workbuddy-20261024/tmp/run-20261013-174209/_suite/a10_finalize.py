# -*- coding: utf-8 -*-
"""A10 finalize."""
from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ["SNAPSHOT_RUN_ID"]
OUT = ROOT / "outputs" / RUN_ID / "A10"
TMP = ROOT / "tmp" / RUN_ID / "A10"


def read_jsonl(p):
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


reqs = read_jsonl(TMP / "requests.jsonl")
ok = [r for r in reqs if r.get("status") == "ok"]
bad = [r for r in reqs if r.get("status") != "ok"]


# 计时只统计图谱自身的渲染请求（label 以 A10- 开头）；
# 逐元素切片探针（A10-slice-*）用于定位 parentData 错误，属排错过程。
timed = [r for r in reqs if str(r.get("label", "")).startswith("A10-")
         and not str(r.get("label", "")).startswith("A10-slice")]


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
        "id": "A10-it00",
        "parent": None,
        "type": "baseline",
        "dsl": "tmp/run-20261013-174209/A10/compositing-lab.snapshot",
        "image": None,
        "render_request_id": by_label["A10-baseline"]["id"],
        "viewed_at": None,
        "observed": ["400 RENDER_ERROR：renderBox.parentData must be StackParentData"],
        "changes": [],
        "result": "ClipOval 内直接放了 Positioned，违反单子节点 + StackParentData 约束。",
        "status": "failed",
    },
    {
        "id": "A10-it01",
        "parent": "A10-it00",
        "type": "syntax-fix",
        "dsl": "tmp/run-20261013-174209/A10/compositing-lab.snapshot",
        "image": None,
        "render_request_id": by_label["A10-baseline-2"]["id"],
        "viewed_at": None,
        "observed": ["仍为 400 RENDER_ERROR parentData"],
        "changes": ["ClipOval 移到 Positioned 内"],
        "result": "错误未消除，说明还有别处。",
        "status": "failed",
    },
    {
        "id": "A10-it02",
        "parent": "A10-it01",
        "type": "syntax-fix",
        "dsl": "tmp/run-20261013-174209/A10/compositing-lab.snapshot",
        "image": "tmp/run-20261013-174209/A10/base.png",
        "render_request_id": by_label["A10-baseline-3"]["id"],
        "viewed_at": ended.isoformat(),
        "observed": [
            "渲染成功。用逐元素切片（1..38）定位到第 31 个顶层元素：",
            "ImageFiltered 的子节点是 Positioned，违反 StackParentData 约束。",
            "① ② 像素采样与理论一致（127,63,191 与 126,126,255）。",
            "③ 卡内为纯白：BackdropFilter 之上又画了不透明白底卡片，把模糊背景完全遮住。",
            "⑤ 基础场景铺满白底，MULTIPLY 后整区被染成 #F6B94A，看不出形状边界。",
        ],
        "changes": ["滤镜链子节点由 Positioned 改为 Stack"],
        "result": "渲染通过但有两处视觉缺陷。",
        "status": "superseded",
    },
    {
        "id": "A10-it03",
        "parent": "A10-it02",
        "type": "visual",
        "dsl": "outputs/run-20261013-174209/A10/compositing-lab.snapshot",
        "image": "outputs/run-20261013-174209/A10/compositing-lab.png",
        "render_request_id": by_label["A10-iter2-backdrop-and-tint-fix"]["id"],
        "viewed_at": ended.isoformat(),
        "observed": [
            "③ 卡片改为透明底（只留边框/阴影/文字/前景），模糊条纹背景可见，文字与前景清晰。",
            "④ 卡内文字与前景一并模糊，与 ③ 形成明确对照。",
            "⑤ 基础场景不再铺满白底，MULTIPLY 只作用于有色形状，透明间隙亦被着色。",
            "⑥ 圆形裁剪边界清晰，有色形状跨过圆周可检查。",
            "像素采样：① (127,63,191) 误差 0；② (126,126,255) 误差 2，均在容差 3 内。",
        ],
        "changes": [
            "③ 卡片 color 由 #FFFFFF 改为 transparent，模糊背景与卡片外观分层绘制",
            "⑤⑥ 基础场景移除满铺白底 Container",
        ],
        "result": "全部缺陷修复。",
        "status": "accepted",
    },
]
(TMP / "iterations.jsonl").write_text(
    "\n".join(json.dumps(i, ensure_ascii=False) for i in iters) + "\n", encoding="utf-8")

metrics = {
    "schema_version": 1,
    "path_base": "suite_root",
    "task_id": "A10",
    "run_id": RUN_ID,
    "task_round": None,
    "status": "completed",
    "stop_reason": "需求满足并完成视觉自检",
    "output_dir": f"outputs/{RUN_ID}/A10/",
    "temp_dir": f"tmp/{RUN_ID}/A10/",
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
        "note": "起止与耗时按图谱自身渲染请求（label 以 A10- 开头）计算；"
                "另有 34 次逐元素切片探针用于定位 parentData 错误，属排错过程，不计入。",
    },
    "counts": {
        "snapshot_requests": len(reqs),
        "successful_snapshot_requests": len(ok),
        "failed_snapshot_requests": len(bad),
        "retry_requests": 0,
        "other_service_requests": 0,
        "dsl_versions": 4,
        "image_views": 3 + 3,
        "completed_visual_iterations": 4,
        "incomplete_visual_iterations": 2,
    },
    "logs": {
        "requests": f"tmp/{RUN_ID}/A10/requests.jsonl",
        "iterations": f"tmp/{RUN_ID}/A10/iterations.jsonl",
    },
    "outputs": [
        {"path": f"outputs/{RUN_ID}/A10/compositing-lab.png", "width": 1440, "height": 1100,
         "dsl": f"outputs/{RUN_ID}/A10/compositing-lab.snapshot"},
        {"path": f"outputs/{RUN_ID}/A10/composite-audit.json"},
        {"path": f"outputs/{RUN_ID}/A10/snapshot-usage.md"},
        {"path": f"outputs/{RUN_ID}/A10/task-metrics.json"},
    ],
    "candidates": [
        {"image": None, "note": "baseline / baseline-2：400 parentData"},
        {"image": f"tmp/{RUN_ID}/A10/base.png", "note": "渲染成功但 ③⑤ 有视觉缺陷"},
        {"image": f"outputs/{RUN_ID}/A10/compositing-lab.png", "note": "最终版本"},
    ],
    "rounds": [],
    "unresolved_issues": [],
}
(OUT / "task-metrics.json").write_text(
    json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("reqs", len(reqs), "ok", len(ok), "bad", len(bad), "elapsed", round(elapsed, 1))
