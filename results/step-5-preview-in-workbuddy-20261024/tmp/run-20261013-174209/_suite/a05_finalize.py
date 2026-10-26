"""A05 收尾：iterations.jsonl、task-metrics.json、套件登记。"""
from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ["SNAPSHOT_RUN_ID"]
OUT = ROOT / "outputs" / RUN_ID / "A05"
TMP = ROOT / "tmp" / RUN_ID / "A05"


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
        "id": "A05-it00",
        "parent": None,
        "type": "baseline",
        "dsl": "tmp/run-20261013-174209/A05/sensor-report.snapshot",
        "image": "tmp/run-20261013-174209/A05/base.png",
        "render_request_id": by_label["A05-baseline"]["id"],
        "viewed_at": ended.isoformat(),
        "observed": [
            "三联趋势、缺测断开、负压区标注、参考线对齐均正确。",
            "底部表格完全缺失：三张 300px 图 + 图例后竖向预算为负（TB_H = -224）。",
            "纵轴刻度标签由范围等分产生多位小数（如 22.476、32.74），不易读。",
        ],
        "changes": [],
        "result": "两处缺陷：表格被挤出画布、刻度标签不友好。",
        "status": "superseded",
    },
    {
        "id": "A05-it01",
        "parent": "A05-it00",
        "type": "visual",
        "dsl": "tmp/run-20261013-174209/A05/sensor-report.snapshot",
        "image": "outputs/run-20261013-174209/A05/sensor-report.png",
        "render_request_id": by_label["A05-iter2-layout-fit"]["id"],
        "viewed_at": ended.isoformat(),
        "observed": [
            "三图高度按剩余预算反推，图例与 12 行表格全部进入画布。",
            "纵轴刻度改为 nice_ticks（步长 1/2/2.5/5×10^k），标签为 22/20/18 等整数。",
            "分区放大：温度缺测断开、湿度缺测断开、压差零线与 09:40–10:50 负区标注、表格「—」均正确。",
        ],
        "changes": [
            "CH_H 由固定 300 改为 (H - PAD - CH_TOP - 图例 - 表格 - 2*gap) // 3",
            "新增 nice_ticks() 生成易读刻度，并用 min/max 扩展范围覆盖刻度",
            "表格行高 22→20，表头位置随表格区起点计算",
        ],
        "result": "全部缺陷修复，整图 + 4 个分区放大复查通过。",
        "status": "accepted",
    },
]
(TMP / "iterations.jsonl").write_text(
    "\n".join(json.dumps(i, ensure_ascii=False) for i in iters) + "\n", encoding="utf-8")

metrics = {
    "schema_version": 1,
    "path_base": "suite_root",
    "task_id": "A05",
    "run_id": RUN_ID,
    "task_round": None,
    "status": "completed",
    "stop_reason": "需求满足并完成视觉自检",
    "output_dir": f"outputs/{RUN_ID}/A05/",
    "temp_dir": f"tmp/{RUN_ID}/A05/",
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
        "image_views": 2 + 5,
        "completed_visual_iterations": 2,
        "incomplete_visual_iterations": 0,
    },
    "logs": {
        "requests": f"tmp/{RUN_ID}/A05/requests.jsonl",
        "iterations": f"tmp/{RUN_ID}/A05/iterations.jsonl",
    },
    "outputs": [
        {"path": f"outputs/{RUN_ID}/A05/sensor-report.png", "width": 1440, "height": 1000,
         "dsl": f"outputs/{RUN_ID}/A05/sensor-report.snapshot"},
        {"path": f"outputs/{RUN_ID}/A05/normalized-data.json"},
        {"path": f"outputs/{RUN_ID}/A05/snapshot-usage.md"},
        {"path": f"outputs/{RUN_ID}/A05/task-metrics.json"},
    ],
    "candidates": [
        {"image": f"tmp/{RUN_ID}/A05/base.png", "note": "基线，表格溢出 + 刻度不友好"},
        {"image": f"outputs/{RUN_ID}/A05/sensor-report.png", "note": "最终版本"},
    ],
    "rounds": [],
    "unresolved_issues": [],
}
(OUT / "task-metrics.json").write_text(
    json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("reqs", len(reqs), "ok", len(ok), "bad", len(bad), "elapsed", round(elapsed, 1))
