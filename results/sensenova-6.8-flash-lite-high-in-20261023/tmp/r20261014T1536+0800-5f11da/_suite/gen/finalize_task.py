"""记录一题完成：更新 suite-state.json 进度摘要与逐题明细、追加 events.jsonl、写检查点。

本 run 的 suite-state.json 是摘要型 schema（counts_by_status / completed / current_task /
remaining），A01–A08 完成时未写逐题明细。这里**不重写既有字段含义**，只追加一个
tasks_detail 列表记录当前题的完整证据；A01–A08 的逐题指标以各题 task-metrics.json 为准。
检查点由 tools/suite.py 递增编号且不可覆盖。

用法：
  SNAPSHOT_RUN_ID=<rid> python -I tmp/<rid>/_suite/gen/finalize_task.py complete <task_id> \
      --ended <ISO8601> requests=N successful=N failed=N retry=N image_views=N \
      visual_iterations=N issues_found=N requirement_checks="34/34" elapsed=秒 \
      --evidence "检查ID:报告路径:通过/总数" ...
"""

from __future__ import annotations

import json
import os
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))
import suite as S  # noqa: E402


def parse(argv: list[str]) -> tuple[dict, str | None]:
    out: dict = {}
    ended = None
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--ended":
            ended = argv[i + 1]
            i += 2
            continue
        if a == "--evidence":
            out.setdefault("evidence", []).append(argv[i + 1])
            i += 2
            continue
        k, v = a.split("=", 1)
        try:
            v = int(v)
        except ValueError:
            pass
        out[k] = v
        i += 1
    return out, ended


def artifact_list(out_dir: Path) -> list[str]:
    """本任务输出目录里的交付文件（不含子目录），按文件名排序。"""
    if not out_dir.exists():
        return []
    return [S.rel(p) for p in sorted(out_dir.iterdir()) if p.is_file()]


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    tid = sys.argv[2]
    kv, ended = parse(sys.argv[3:])
    now = S.now_iso()

    state = S.load_state()
    order = [t["id"] for t in state.get("task_order", [])] or None
    metrics_path = S.rel(S.task_dirs(tid)[0] / "task-metrics.json")
    m = {}
    mp = Path(metrics_path)
    if mp.exists():
        m = json.loads(mp.read_text(encoding="utf-8"))

    detail = {
        "id": tid,
        "status": "completed",
        "started_at": m.get("timings", {}).get("started_at"),
        "ended_at": ended,
        "elapsed_seconds": kv.get("elapsed"),
        "output_dir": S.rel(S.task_dirs(tid)[0]),
        "temp_dir": S.rel(S.task_dirs(tid)[1]),
        "artifacts": artifact_list(S.task_dirs(tid)[0]),
        "metrics": metrics_path,
        "requests": kv.get("requests"),
        "successful_requests": kv.get("successful"),
        "failed_requests": kv.get("failed"),
        "retry_requests": kv.get("retry"),
        "image_views": kv.get("image_views"),
        "visual_iterations": kv.get("visual_iterations"),
        "issues_found": kv.get("issues_found"),
        "requirement_checks": kv.get("requirement_checks"),
        "visual_review_evidence": [
            {"check": e.split(":")[0], "report": e.split(":")[1],
             "verdict": e.split(":")[2]} for e in kv.get("evidence", []) if ":" in e
        ],
        "unresolved_issues": m.get("unresolved_issues") or [],
        "recorded_at": now,
    }

    details = state.setdefault("tasks_detail", [])
    details = [d for d in details if d.get("id") != tid] + [detail]
    state["tasks_detail"] = sorted(details, key=lambda d: d["id"])

    completed_ids = [d["id"] for d in state["tasks_detail"] if d.get("status") == "completed"]
    prev = state.get("completed") or []
    state["completed"] = prev + [i for i in completed_ids if i not in prev]

    total = state.get("total_tasks")
    order = state.get("task_order")
    if not order:
        cat = Path(S.suite_root()) / "catalog.json"
        if cat.exists():
            order = json.loads(cat.read_text(encoding="utf-8")).get("task_order", [])
    order = order or (list(state.get("remaining") or []) + prev)
    remaining = [t for t in order if t not in state["completed"]]
    in_progress = [d["id"] for d in state["tasks_detail"]
                   if d["status"] == "in_progress" and d["id"] not in state["completed"]]

    state["remaining"] = remaining
    state["current_task"] = remaining[0] if remaining else None
    state["counts_by_status"] = {
        "completed": len(state["completed"]),
        "in_progress": len(in_progress),
        "pending": total - len(state["completed"]) - len(in_progress) if total else 0,
    }
    state["updated_at"] = now
    state["status"] = ("completed" if total and len(state["completed"]) >= total
                       else "in_progress")

    S.save_state(state)

    S.append_event({
        "ts": now, "event": "task_completed", "task_id": tid, "status": "completed",
        "ended_at": ended, "recorded_at": now,
        "output_dir": S.rel(S.task_dirs(tid)[0]),
        "temp_dir": S.rel(S.task_dirs(tid)[1]),
        "artifacts": detail["artifacts"],
        "snapshot_requests": kv.get("requests"),
        "successful": kv.get("successful"),
        "failed": kv.get("failed"),
        "retry_requests": kv.get("retry"),
        "image_views": kv.get("image_views"),
        "visual_iterations": kv.get("visual_iterations"),
        "issues_found": kv.get("issues_found"),
        "requirement_checks": kv.get("requirement_checks"),
        "elapsed_seconds": kv.get("elapsed"),
        "metrics": metrics_path,
        "visual_review_evidence": detail["visual_review_evidence"],
        "note": "tasks_detail 于本题起追加；A01–A08 逐题明细见各自 task-metrics.json",
    })
    ck = S.snapshot_checkpoint(state)
    state["last_checkpoint"] = ck
    state["updated_at"] = S.now_iso()
    S.save_state(state)

    print("task_completed", tid, "->", ck)
    print(json.dumps({k: state[k] for k in
                      ("counts_by_status", "completed", "updated_at", "status")},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
