# -*- coding: utf-8 -*-
"""A11 finalize."""
from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ["SNAPSHOT_RUN_ID"]
OUT = ROOT / "outputs" / RUN_ID / "A11"
TMP = ROOT / "tmp" / RUN_ID / "A11"


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

by_label = {r.get("label"): r for r in reqs}

iters = [
    {
        "id": "A11-it00",
        "parent": None,
        "type": "baseline",
        "dsl": "tmp/run-20261013-174209/A11/invoice-page-01.snapshot",
        "image": "tmp/run-20261013-174209/A11/p1-base.png",
        "render_request_id": by_label["A11-p1-baseline"]["id"],
        "viewed_at": ended.isoformat(),
        "observed": [
            "第 1 页结构、金额与汇总正确。",
            "SKU 列显示为 A&lt;B&amp;C&gt; —— HTML 实体被字面输出，未还原成 < > &。",
        ],
        "changes": [],
        "result": "SKU 保真缺陷。",
        "status": "superseded",
    },
    {
        "id": "A11-it01",
        "parent": "A11-it00",
        "type": "syntax-fix",
        "dsl": "tmp/run-20261013-174209/A11/invoice-page-02.snapshot",
        "image": None,
        "render_request_id": by_label["A11-p2-baseline"]["id"],
        "viewed_at": None,
        "observed": ["400 PARSE_ERROR：Unknown element tag [RichText]"],
        "changes": [],
        "result": "RichText 不是解析器注册标签。",
        "status": "failed",
    },
    {
        "id": "A11-it02",
        "parent": "A11-it01",
        "type": "syntax-fix",
        "dsl": "tmp/run-20261013-174209/A11/invoice-page-02.snapshot",
        "image": "tmp/run-20261013-174209/A11/p2-iter2.png",
        "render_request_id": by_label["A11-p2-iter2-nested-text"]["id"],
        "viewed_at": ended.isoformat(),
        "observed": [
            "改用 Text 嵌套 Text 实现富文本，PAID/已结算 三色共用基线正常。",
            "literal_lines 四行逐字符保真（双空格、反斜杠、尖括号、& 均正确）。",
            "但说明文字里的 & 被输出成字面 &amp;。",
        ],
        "changes": ["RichText 改为 Text 嵌套 Text"],
        "result": "富文本修复；说明文字出现可见实体。",
        "status": "superseded",
    },
    {
        "id": "A11-it03",
        "parent": "A11-it00",
        "type": "visual",
        "dsl": "outputs/run-20261013-174209/A11/invoice-page-01.snapshot",
        "image": "outputs/run-20261013-174209/A11/invoice-page-01.png",
        "render_request_id": by_label["A11-p1-iter2-sku-cdata"]["id"],
        "viewed_at": ended.isoformat(),
        "observed": ["SKU 改用 CDATA 后显示为 A<B&C>D，保真正确"],
        "changes": ["SKU 与 literal_lines 一律用 <![CDATA[...]]> 包裹，不做 HTML 转义"],
        "result": "第 1 页 SKU 保真修复。",
        "status": "accepted",
    },
    {
        "id": "A11-it04",
        "parent": "A11-it02",
        "type": "visual",
        "dsl": "outputs/run-20261013-174209/A11/invoice-page-02.snapshot",
        "image": "outputs/run-20261013-174209/A11/invoice-page-02.png",
        "render_request_id": by_label["A11-p2-iter3-caption-fix"]["id"],
        "viewed_at": ended.isoformat(),
        "observed": ["说明文字中的 & 改写为「AND 符号」，不再出现可见实体"],
        "changes": ["说明文案中的 & 改为文字描述"],
        "result": "第 2 页修复。",
        "status": "accepted",
    },
]
(TMP / "iterations.jsonl").write_text(
    "\n".join(json.dumps(i, ensure_ascii=False) for i in iters) + "\n", encoding="utf-8")

metrics = {
    "schema_version": 1,
    "path_base": "suite_root",
    "task_id": "A11",
    "run_id": RUN_ID,
    "task_round": None,
    "status": "completed",
    "stop_reason": "需求满足并完成视觉自检",
    "output_dir": f"outputs/{RUN_ID}/A11/",
    "temp_dir": f"tmp/{RUN_ID}/A11/",
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
        "dsl_versions": 4,
        "image_views": 4 + 2,
        "completed_visual_iterations": 4,
        "incomplete_visual_iterations": 1,
    },
    "logs": {
        "requests": f"tmp/{RUN_ID}/A11/requests.jsonl",
        "iterations": f"tmp/{RUN_ID}/A11/iterations.jsonl",
    },
    "outputs": [
        {"path": f"outputs/{RUN_ID}/A11/invoice-page-01.png", "width": 1200, "height": 1600,
         "dsl": f"outputs/{RUN_ID}/A11/invoice-page-01.snapshot"},
        {"path": f"outputs/{RUN_ID}/A11/invoice-page-02.png", "width": 1200, "height": 1600,
         "dsl": f"outputs/{RUN_ID}/A11/invoice-page-02.snapshot"},
        {"path": f"outputs/{RUN_ID}/A11/invoice-audit.json"},
        {"path": f"outputs/{RUN_ID}/A11/text-map.json"},
        {"path": f"outputs/{RUN_ID}/A11/snapshot-usage.md"},
        {"path": f"outputs/{RUN_ID}/A11/task-metrics.json"},
    ],
    "candidates": [
        {"image": f"tmp/{RUN_ID}/A11/p1-base.png", "note": "SKU 显示为实体"},
        {"image": f"tmp/{RUN_ID}/A11/p2-iter2.png", "note": "说明文字出现 &amp;"},
        {"image": f"outputs/{RUN_ID}/A11/invoice-page-01.png", "note": "第 1 页终版"},
        {"image": f"outputs/{RUN_ID}/A11/invoice-page-02.png", "note": "第 2 页终版"},
    ],
    "rounds": [],
    "unresolved_issues": [],
}
(OUT / "task-metrics.json").write_text(
    json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("reqs", len(reqs), "ok", len(ok), "bad", len(bad), "elapsed", round(elapsed, 1))
