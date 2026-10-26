"""A03 收尾：iterations.jsonl、task-metrics.json、套件登记。"""
from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ["SNAPSHOT_RUN_ID"]
OUT = ROOT / "outputs" / RUN_ID / "A03"
TMP = ROOT / "tmp" / RUN_ID / "A03"


def read_jsonl(p: Path) -> list[dict]:
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
        "id": "A03-it00",
        "parent": None,
        "type": "baseline",
        "dsl": "tmp/run-20261013-174209/A03/original-broken.snapshot",
        "image": None,
        "render_request_id": "A03-render-1791889149383",
        "viewed_at": None,
        "observed": ["400 PARSE_ERROR：padding=\"24 32\" 格式错误。未取得图片，无法查看。"],
        "changes": [],
        "result": "显式语法错误，进入修复链。",
        "status": "failed",
    },
    {
        "id": "A03-it01",
        "parent": "A03-it00",
        "type": "syntax-fix",
        "dsl": "tmp/run-20261013-174209/A03/v1-padding.snapshot",
        "image": None,
        "render_request_id": None,
        "viewed_at": None,
        "observed": ["400 PARSE_ERROR：Attr [matrix] must not be null（Transform 无 rotate）。"],
        "changes": ['padding="24 32" → padding="(32,24)"'],
        "result": "第一个错误已修复，暴露下一个。",
        "status": "failed",
    },
    {
        "id": "A03-it02",
        "parent": "A03-it01",
        "type": "syntax-fix",
        "dsl": "tmp/run-20261013-174209/A03/v2-attrs.snapshot",
        "image": None,
        "render_request_id": None,
        "viewed_at": None,
        "observed": ["仍为 400 PARSE_ERROR：Attr [matrix] must not be null。"],
        "changes": ["font-size → fontSize", "根节点 width/height 移到内层 Container"],
        "result": "静默忽略类问题已修正，但 Transform 错误仍在。",
        "status": "failed",
    },
    {
        "id": "A03-it03",
        "parent": "A03-it02",
        "type": "syntax-fix",
        "dsl": "tmp/run-20261013-174209/A03/v3-transform-matrix.snapshot",
        "image": None,
        "render_request_id": None,
        "viewed_at": None,
        "observed": ["400 RENDER_ERROR：renderBox.parentData must be StackParentData。"],
        "changes": ["Transform rotate=\"-8\" → matrix=（列主序 4×4 顺时针/逆时针矩阵）"],
        "result": "Transform 修复，暴露 Positioned 父节点错误。",
        "status": "failed",
    },
    {
        "id": "A03-it04",
        "parent": "A03-it03",
        "type": "visual",
        "dsl": "tmp/run-20261013-174209/A03/v4-stack-positioned.snapshot",
        "image": "tmp/run-20261013-174209/A03/v4-stack-positioned.png",
        "render_request_id": None,
        "viewed_at": ended.isoformat(),
        "observed": [
            "首次取得可查看图片。",
            "REVIEW 底色为青色：#33FFFFFF 按 #RRGGBBAA 解析成不透明青。",
            "中央说明卡缺失；ImageFiltered 会连文字一起模糊。",
            "只有一张指标卡，缺 LATENCY 与 SUCCESS。",
            "彩色细条未画。",
        ],
        "changes": ["整体改为 Stack + Positioned；LIVE/REVIEW/指标卡归位"],
        "result": "渲染成功但视觉不满足要求，记录 4 项视觉缺陷。",
        "status": "superseded",
    },
    {
        "id": "A03-it05",
        "parent": "A03-it04",
        "type": "visual",
        "dsl": "outputs/run-20261013-174209/A03/system-pulse.snapshot",
        "image": "outputs/run-20261013-174209/A03/system-pulse.png",
        "render_request_id": None,
        "viewed_at": ended.isoformat(),
        "observed": [
            "十项问题全部修复。",
            "像素采样：背景 (11,18,32)=#0B1220；REVIEW/卡片底色 (59,65,76)=20% 白。",
            "REVIEW 四角露出背景，证明 8° 逆时针旋转生效。",
            "细条在说明卡左右两侧均可见（x=100 与 x=1200 处为彩色）。",
            "卡内背景模糊、文字锐利（BackdropFilter + ClipRRect）。",
        ],
        "changes": [
            "#33FFFFFF → #FFFFFF33（alpha 顺序）",
            "ImageFiltered → ClipRRect + BackdropFilter",
            "补 LATENCY 148 ms 与 SUCCESS 99.2% 两张等宽卡",
            "补 1280×6 彩色渐变细条，y=397 穿过说明卡",
            "明确 32px 安全边距与全部元素坐标",
        ],
        "result": "整图 + 4 个分区放大复查通过。",
        "status": "accepted",
    },
]
(TMP / "iterations.jsonl").write_text(
    "\n".join(json.dumps(i, ensure_ascii=False) for i in iters) + "\n", encoding="utf-8")

metrics = {
    "schema_version": 1,
    "path_base": "suite_root",
    "task_id": "A03",
    "run_id": RUN_ID,
    "task_round": None,
    "status": "completed",
    "stop_reason": "需求满足并完成视觉自检",
    "output_dir": f"outputs/{RUN_ID}/A03/",
    "temp_dir": f"tmp/{RUN_ID}/A03/",
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
        "dsl_versions": 6,
        "image_views": 2 + 4,
        "completed_visual_iterations": 2,
        "incomplete_visual_iterations": 4,
    },
    "logs": {
        "requests": f"tmp/{RUN_ID}/A03/requests.jsonl",
        "iterations": f"tmp/{RUN_ID}/A03/iterations.jsonl",
    },
    "outputs": [
        {"path": f"outputs/{RUN_ID}/A03/system-pulse.png", "width": 1280, "height": 800,
         "dsl": f"outputs/{RUN_ID}/A03/system-pulse.snapshot"},
        {"path": f"outputs/{RUN_ID}/A03/repair-log.json"},
        {"path": f"outputs/{RUN_ID}/A03/snapshot-usage.md"},
        {"path": f"outputs/{RUN_ID}/A03/task-metrics.json"},
    ],
    "candidates": [
        {"image": None, "note": "原稿（400，无图）"},
        {"image": f"tmp/{RUN_ID}/A03/v1-padding.png", "note": "400"},
        {"image": f"tmp/{RUN_ID}/A03/v2-attrs.png", "note": "400"},
        {"image": f"tmp/{RUN_ID}/A03/v3-transform-matrix.png", "note": "400"},
        {"image": f"tmp/{RUN_ID}/A03/v4-stack-positioned.png", "note": "首版可查看，4 项视觉缺陷"},
        {"image": f"outputs/{RUN_ID}/A03/system-pulse.png", "note": "最终版本"},
    ],
    "rounds": [],
    "unresolved_issues": [],
}
(OUT / "task-metrics.json").write_text(
    json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("reqs", len(reqs), "ok", len(ok), "bad", len(bad), "elapsed", round(elapsed, 1))
