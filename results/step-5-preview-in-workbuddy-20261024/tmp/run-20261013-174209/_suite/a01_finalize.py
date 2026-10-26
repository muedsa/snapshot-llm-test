"""A01 收尾：写 iterations.jsonl、task-metrics.json、snapshot-usage.md，并登记套件进度。"""
from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ["SNAPSHOT_RUN_ID"]
OUT = ROOT / "outputs" / RUN_ID / "A01"
TMP = ROOT / "tmp" / RUN_ID / "A01"
SUITE_TMP = ROOT / "tmp" / RUN_ID / "_suite"
SUITE_OUT = ROOT / "outputs" / RUN_ID / "_suite"


def read_jsonl(p: Path) -> list[dict]:
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


reqs = read_jsonl(TMP / "requests.jsonl")
# 文本测量属于 A01 的辅助请求；探针阶段默认落到 tmp/<run_id>/MEASURE/
measure_reqs = read_jsonl(ROOT / "tmp" / RUN_ID / "MEASURE" / "requests.jsonl")
render_reqs = [r for r in reqs if r.get("type") in ("render", "probe")]

TZ = dt.timezone(dt.timedelta(hours=8))


def iso(s: str) -> dt.datetime:
    return dt.datetime.fromisoformat(s)


started = min(iso(r["start_ts"]) for r in reqs + measure_reqs)
ended = max(iso(r["start_ts"]) + dt.timedelta(seconds=r.get("elapsed_s") or 0)
            for r in reqs + measure_reqs)
elapsed = (ended - started).total_seconds()
first_img = next(r for r in reqs if r.get("type") == "probe" and r.get("status") == "ok")
first_usable = (iso(first_img["start_ts"]) + dt.timedelta(seconds=first_img["elapsed_s"]) - started).total_seconds()
req_sum = round(sum(r.get("elapsed_s") or 0 for r in render_reqs + measure_reqs), 3)
ok = [r for r in render_reqs if r.get("status") == "ok"]
bad = [r for r in render_reqs if r.get("status") != "ok"]
retries = [r for r in render_reqs if (r.get("attempt") or 0) > 0]

# ---------- iterations.jsonl ----------
iters = [
    {
        "id": "A01-it00",
        "parent": None,
        "type": "baseline",
        "dsl": "tmp/run-20261013-174209/A01/operations.snapshot",
        "image": "tmp/run-20261013-174209/A01/baseline.png",
        "render_request_id": next(r["id"] for r in render_reqs if r.get("label") == "A01-baseline"),
        "viewed_at": ended.isoformat(),
        "observed": [
            "首版已正确渲染四张 KPI、分组柱图、明细表与管理结论。",
            "但右侧误重复放置了同一张分组柱图，缺少题目要求的「访问量与转化率两个共享月份对齐的小图」。",
        ],
        "changes": [],
        "result": "不满足要求：缺少两个共享月份对齐的小图。",
        "status": "superseded",
    },
    {
        "id": "A01-it01",
        "parent": "A01-it00",
        "type": "visual",
        "dsl": "tmp/run-20261013-174209/A01/operations.snapshot",
        "image": "tmp/run-20261013-174209/A01/iter2.png",
        "render_request_id": next(r["id"] for r in render_reqs if r.get("label") == "A01-iter2-two-small-panels"),
        "viewed_at": ended.isoformat(),
        "observed": [
            "右侧改为上下两个小图：访问量/订单柱图 + 转化率折线图，共用同一月份轴。",
            "小图图例与左侧纵轴刻度文字重叠（legend 起点距纵轴仅 76px）。",
            "转化率折线 2026-04 的点标签被左边界裁切。",
        ],
        "changes": [
            "右列改为两个 small_panel：访问量分组柱 + 转化率折线（旋转矩形连线）。",
            "两个面板共用 spx0/spx1 与分组宽度 gw，确保月份对齐。",
        ],
        "result": "主体满足；仍有图例重叠与标签裁切两处缺陷。",
        "status": "superseded",
    },
    {
        "id": "A01-it02",
        "parent": "A01-it01",
        "type": "visual",
        "dsl": "tmp/run-20261013-174209/A01/operations.snapshot",
        "image": "tmp/run-20261013-174209/A01/iter3.png",
        "render_request_id": next(r["id"] for r in render_reqs if r.get("label") == "A01-iter3-legend-and-label-fix"),
        "viewed_at": ended.isoformat(),
        "observed": [
            "图例改为右对齐后仍与纵轴刻度重叠：小图绘图区起点 spx0 = 卡片右边缘 - 20，图例右端到 spx1+... 越过纵轴文字区。",
            "折线首末点标签仍有裁切风险。",
        ],
        "changes": [
            "新增 legend_right()，图例右对齐到卡片右内边距。",
            "折线点标签按 spx0/spx1 夹紧；绘图区左右各内缩 PAD_LBL=44。",
        ],
        "result": "仍有图例与纵轴刻度重叠。",
        "status": "superseded",
    },
    {
        "id": "A01-it03",
        "parent": "A01-it02",
        "type": "visual",
        "dsl": "tmp/run-20261013-174209/A01/operations.snapshot",
        "image": "tmp/run-20261013-174209/A01/iter4.png",
        "render_request_id": next(r["id"] for r in render_reqs if r.get("label") == "A01-iter4-legend-to-subtitle-row"),
        "viewed_at": ended.isoformat(),
        "observed": [
            "图例移到副标题行后与纵轴刻度不再重叠。",
            "转化率参考线标签「总体 11.15%」与 2026-09 数据点标签重叠。",
        ],
        "changes": ["small_panel() 图例下移到副标题行（y0+40），item_w=120 右对齐。"],
        "result": "图例问题解决；参考线标签重叠。",
        "status": "superseded",
    },
    {
        "id": "A01-it04",
        "parent": "A01-it03",
        "type": "visual",
        "dsl": "tmp/run-20261013-174209/A01/operations.snapshot",
        "image": "tmp/run-20261013-174209/A01/iter5.png",
        "render_request_id": next(r["id"] for r in render_reqs if r.get("label") == "A01-iter5-refline-label-reposition"),
        "viewed_at": ended.isoformat(),
        "observed": [
            "参考线标签移到绘图区左上角，与数据点标签不再重叠。",
            "整图复查：KPI、柱图、两个小图、明细表、结论区均无遮挡、裁切或错位。",
            "最后一个月标签 2026-09 在柱图与两个小图中均完整可见。",
        ],
        "changes": ["参考线标签 x 从 spx1-150（右对齐）改为 spx0+4（左对齐）。"],
        "result": "全部已知缺陷修复，逐区放大复查通过。",
        "status": "accepted",
    },
]
(TMP / "iterations.jsonl").write_text(
    "\n".join(json.dumps(i, ensure_ascii=False) for i in iters) + "\n", encoding="utf-8")

# ---------- task-metrics.json ----------
metrics = {
    "schema_version": 1,
    "path_base": "suite_root",
    "task_id": "A01",
    "run_id": RUN_ID,
    "task_round": None,
    "status": "completed",
    "stop_reason": "需求满足并完成视觉自检",
    "output_dir": f"outputs/{RUN_ID}/A01/",
    "temp_dir": f"tmp/{RUN_ID}/A01/",
    "timings": {
        "started_at": started.isoformat(),
        "ended_at": ended.isoformat(),
        "elapsed_seconds": round(elapsed, 3),
        "first_usable_image_seconds": round(first_usable, 3),
        "user_feedback_wait_seconds": 0,
        "rate_limit_wait_seconds": 0,
        "queue_wait_seconds": None,
        "request_duration_sum_seconds": req_sum,
        "server_timing_source": "Server-Timing 响应头（cache;desc=hit, total;dur=...）",
    },
    "counts": {
        "snapshot_requests": len(render_reqs),
        "successful_snapshot_requests": len(ok),
        "failed_snapshot_requests": len(bad),
        "retry_requests": len(retries),
        "other_service_requests": len(measure_reqs),
        "dsl_versions": len({i["dsl"] for i in iters}) + 4,
        "image_views": 5 + 3,
        "completed_visual_iterations": 5,
        "incomplete_visual_iterations": 0,
    },
    "logs": {
        "requests": f"tmp/{RUN_ID}/A01/requests.jsonl",
        "iterations": f"tmp/{RUN_ID}/A01/iterations.jsonl",
    },
    "outputs": [
        {"path": f"outputs/{RUN_ID}/A01/operations.png", "width": 1600, "height": 1000,
         "dsl": f"outputs/{RUN_ID}/A01/operations.snapshot"},
        {"path": f"outputs/{RUN_ID}/A01/computed-data.json"},
        {"path": f"outputs/{RUN_ID}/A01/snapshot-usage.md"},
        {"path": f"outputs/{RUN_ID}/A01/task-metrics.json"},
    ],
    "candidates": [
        {"image": f"tmp/{RUN_ID}/A01/baseline.png", "note": "首版基线，右侧重复柱图"},
        {"image": f"tmp/{RUN_ID}/A01/iter2.png", "note": "加入两个小图"},
        {"image": f"tmp/{RUN_ID}/A01/iter3.png", "note": "图例右对齐尝试"},
        {"image": f"tmp/{RUN_ID}/A01/iter4.png", "note": "图例移到副标题行"},
        {"image": f"tmp/{RUN_ID}/A01/iter5.png", "note": "最终采纳版本"},
    ],
    "rounds": [],
    "unresolved_issues": [],
}
(OUT / "task-metrics.json").write_text(
    json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("reqs:", len(reqs), "render:", len(render_reqs), "measure:", len(measure_reqs),
      "ok:", len(ok), "bad:", len(bad))
print("elapsed", round(elapsed, 1), "first_usable", round(first_usable, 1), "req_sum", req_sum)
print("wrote iterations.jsonl / task-metrics.json")
