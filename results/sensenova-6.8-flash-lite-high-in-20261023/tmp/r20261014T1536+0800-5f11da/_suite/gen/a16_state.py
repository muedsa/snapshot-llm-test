"""A16 完成后更新套件状态：状态清单、逐题明细、事件流、检查点快照。

只追加与更新指针，不覆盖历史：
  * suite-state.json 的 completed/remaining/counts_by_status 与 updated_at 更新；
  * tasks_detail 追加 A16 条目（已有条目不动）；
  * tmp/<run_id>/_suite/events.jsonl 追加事件；
  * checkpoints/state-000050.json 保存新的编号快照。

运行方式：
    python -I tmp/<run_id>/_suite/gen/a16_state.py
"""
from __future__ import annotations

import datetime
import json
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve()
RUN_ID = HERE.parents[2].name
ROOT = HERE.parents[4]
SUITE_OUT = ROOT / "outputs" / RUN_ID / "_suite"
SUITE_TMP = ROOT / "tmp" / RUN_ID / "_suite"
TASK = "A16"
NOW = datetime.datetime.now(
    datetime.timezone(datetime.timedelta(hours=8))).replace(
    microsecond=0).isoformat()

A16_DETAIL = {
    "id": TASK,
    "status": "completed",
    "started_at": "2026-10-19T04:51:24+08:00",
    "ended_at": NOW,
    "elapsed_seconds": int((
        datetime.datetime.fromisoformat(NOW)
        - datetime.datetime.fromisoformat(
            "2026-10-19T04:51:24+08:00")).total_seconds()),
    "output_dir": f"outputs/{RUN_ID}/{TASK}",
    "temp_dir": f"tmp/{RUN_ID}/{TASK}",
    "artifacts": [
        f"outputs/{RUN_ID}/{TASK}/corrected-report.png",
        f"outputs/{RUN_ID}/{TASK}/corrected-report.snapshot",
        f"outputs/{RUN_ID}/{TASK}/findings.json",
        f"outputs/{RUN_ID}/{TASK}/corrected-data.json",
        f"outputs/{RUN_ID}/{TASK}/snapshot-usage.md",
        f"outputs/{RUN_ID}/{TASK}/task-metrics.json",
    ],
    "final_pngs": 1,
    "final_pngs_required": 1,
    "snapshot_requests": 3,
    "snapshot_requests_successful": 3,
    "snapshot_requests_failed": 0,
    "dsl_versions": 3,
    "image_views": 9,
    "completed_visual_iterations": 2,
    "logs": {
        "requests": f"tmp/{RUN_ID}/{TASK}/requests.jsonl",
        "iterations": f"tmp/{RUN_ID}/{TASK}/iterations.jsonl",
    },
    "evidence": [
        f"tmp/{RUN_ID}/{TASK}/gen/a16/diag1.json",
        f"tmp/{RUN_ID}/{TASK}/gen/a16/diag2.json",
        f"tmp/{RUN_ID}/{TASK}/gen/a16/diag3.json",
        f"tmp/{RUN_ID}/{TASK}/gen/a16/diag4.json",
        f"tmp/{RUN_ID}/{TASK}/gen/a16/diag5.json",
        f"tmp/{RUN_ID}/{TASK}/gen/a16/diag6.json",
        f"tmp/{RUN_ID}/{TASK}/gen/a16/diag7.json",
        f"tmp/{RUN_ID}/{TASK}/gen/a16/diag8.json",
    ],
    "evidence_note": "diag1–diag7 为参考图 flawed-report.png 的图像取证，"
                     "diag8 为最终交付图的柱高/零点/标签/对比度核验",
    "findings": {"confirmed": 10, "uncertain": 7},
    "unresolved": [
        "v01 渲染请求的起始时间与耗时未捕获（当时未设 SNAPSHOT_RUN_ID，"
        "log_request 写盘后抛错）；已以 elapsed_ms=null 补记并写明原因，"
        "生成脚本已修复",
        "started_at 为区间下界：文档阅读早于 diag1.json 但未单独留痕",
        "7 项 uncertainties 依赖原始 DSL，题面不提供，按约定保留为不确定",
    ],
}


def main() -> int:
    sp = SUITE_OUT / "suite-state.json"
    state = json.loads(sp.read_text(encoding="utf-8"))

    completed = state.setdefault("completed", [])
    if TASK not in completed:
        completed.append(TASK)
    remaining = state.get("remaining")
    if isinstance(remaining, list) and TASK in remaining:
        remaining.remove(TASK)
    order = ["A01", "A02", "A03", "A04", "A05", "A06", "A07", "A08",
             "A09", "A10", "A11", "A12", "A13", "A14", "A15", "A16",
             "A17", "A18", "A19", "A20", "A21", "A22", "A23", "A24",
             "B01", "B02", "B03", "B04", "B05", "B06"]
    state["current_task"] = order[len(completed)] if len(completed) < 30 else None
    counts = state.setdefault("counts_by_status", {})
    counts["completed"] = len(completed)
    counts["in_progress"] = 0
    counts["pending"] = len(order) - len(completed)

    detail = state.setdefault("tasks_detail", [])
    ids = [d.get("id") for d in detail if isinstance(d, dict)]
    if TASK not in ids:
        detail.append(A16_DETAIL)
    state["tasks_detail_note"] = (
        "tasks_detail 仅逐题记录了 A09–A16 共 8 条；A01–A08 只出现在 completed "
        "清单里，没有对应的逐题明细条目（缺起止时间、请求数、指标路径）。该缺口是"
        "本轮之前遗留的记录问题，本轮不补造：补造需要当时的真实产物与日志，"
        "凭空填会制造虚假留痕。逐题明细以各题 task-metrics.json 为准。")
    state["suite_progress_note"] = (
        "A01–A16 共 16 题完成；按 task_order 下一题为 A17"
        "（四页可实践的DSL入门手册，minimum_final_pngs=8）。")
    state["status"] = "in_progress"
    state["completed_all"] = len(completed) >= 30
    state["updated_at"] = NOW
    sp.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n",
                  encoding="utf-8")

    # 事件流
    ev = {"ts": NOW, "timezone": "Asia/Shanghai (UTC+08:00)", "type": "task_completed",
          "task_id": TASK, "run_id": RUN_ID,
          "detail": "A16 从错误图表恢复可信叙事：10 项确认发现 + 7 项不确定；"
                    "3 次渲染、2 次完整视觉迭代、9 次看图；最终图实测柱高偏差 ≤0.4px、"
                    "柱底零点统一、标签零裁切、对比度全部达标",
          "output_dir": A16_DETAIL["output_dir"]}
    with (SUITE_TMP / "events.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(ev, ensure_ascii=False) + "\n")

    # 检查点
    cps = sorted((SUITE_TMP / "checkpoints").glob("state-*.json"))
    nxt = len(cps) + 1
    snap = {"checkpoint_id": f"state-{nxt:06d}", "taken_at": NOW,
            "timezone": "Asia/Shanghai (UTC+08:00)", "run_id": RUN_ID,
            "task_id": TASK, "task_status": "completed",
            "note": "A16 交付完成后的快照；历史快照不覆盖",
            "suite_state": state}
    (SUITE_TMP / "checkpoints" / f"state-{nxt:06d}.json").write_text(
        json.dumps(snap, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    state["last_checkpoint"] = f"tmp/{RUN_ID}/_suite/checkpoints/state-{nxt:06d}.json"
    sp.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n",
                  encoding="utf-8")

    print(json.dumps({
        "completed_count": len(completed),
        "current_task": state["current_task"],
        "counts_by_status": counts,
        "last_checkpoint": state["last_checkpoint"],
        "tasks_detail_ids": ids + [TASK],
    }, ensure_ascii=True, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
