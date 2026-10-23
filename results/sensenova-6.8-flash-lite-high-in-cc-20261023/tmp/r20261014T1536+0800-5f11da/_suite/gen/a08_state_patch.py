"""A08 状态补丁（三件事，均不重写历史快照）：

1. 补 A08 的 started_at —— do_complete 只写 ended_at/recorded_at，
   而 A08 的开始时刻（11:43:02，A07 完成后的 current_task 切换）先前只落在
   suite-state 的 updated_at 上，没有被记进任务条目。
2. 补 paths.json 的 12/12 路径审计证据 —— suite_update.evidence_records 只能
   指向 tmp/<rid>/<tid>/ 下的文件，paths.json 在 outputs/ 下，故单独追加。
3. 追加一条事件补记 A08 的 task_started（当时漏记），并说明 started_at 的来源。

检查点 state-000039.json 已由 suite_update.py 生成，本脚本只改 suite-state.json
当前指针并追加事件，不覆盖历史快照。
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3] / "tools"))
os.environ.setdefault("SNAPSHOT_RUN_ID", "r20261014T1536+0800-5f11da")
import suite as S  # noqa: E402

RID = S.run_id()
STARTED = "2026-10-15T11:43:02+08:00"

state = S.load_state()
for t in state["tasks"]:
    if t["id"] == "A08":
        had = t.get("started_at")
        t["started_at"] = STARTED
        t["started_at_source"] = (
            "suite-state.json 的 updated_at：A07 task_completed（11:20:05）之后，"
            "11:43:02 将 current_task 切为 A08；当时未追加 events.jsonl 条目，"
            "本条为补记")
        ev = t.get("visual_review_evidence") or []
        if not any(e.get("check") == "path_audit" for e in ev):
            ev.append({
                "check": "path_audit",
                "verdict": "12/12",
                "path_base": "suite_root",
                "report": f"outputs/{RID}/A08/paths.json",
                "note": "由 a08_paths.py 从 inputs/floor.txt 原文独立复算，"
                        "不引用 model.json 的结论字段；生成器在 tmp/<rid>/A08/gen/",
            })
        t["visual_review_evidence"] = ev
        t["note_start_at_patch"] = (
            f"started_at 由 {had!r} 补为 {STARTED}，"
            "与 task-metrics.json 的 timings.started_at 一致")
        break

S.save_state(state)
S.append_event({
    "ts": S.now_iso(),
    "event": "task_started",
    "task_id": "A08",
    "status": "completed",
    "backfill": True,
    "backfills": "A08 开始时未追加事件，此处补记，保持 events.jsonl 与 suite-state 一致",
    "started_at": STARTED,
    "output_dir": f"outputs/{RID}/A08",
    "temp_dir": f"tmp/{RID}/A08",
})
S.append_event({
    "ts": S.now_iso(),
    "event": "metrics_completed",
    "task_id": "A08",
    "backfill": True,
    "started_at": STARTED,
    "started_at_source": "suite-state updated_at（原未记入任务条目，已补）",
    "paths_audit": "12/12",
    "paths_audit_report": f"outputs/{RID}/A08/paths.json",
    "deliverables": [
        f"outputs/{RID}/A08/wayfinding.png",
        f"outputs/{RID}/A08/wayfinding.snapshot",
        f"outputs/{RID}/A08/paths.json",
        f"outputs/{RID}/A08/snapshot-usage.md",
        f"outputs/{RID}/A08/task-metrics.json",
    ],
})
print("A08 状态补丁完成；started_at ->", STARTED)
print("visual_review_evidence:", len(state["tasks"][[t['id'] for t in state['tasks']].index('A08')]["visual_review_evidence"]), "条")
