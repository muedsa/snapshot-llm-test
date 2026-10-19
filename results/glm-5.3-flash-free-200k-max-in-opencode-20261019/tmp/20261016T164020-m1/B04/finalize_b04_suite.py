# -*- coding: utf-8 -*-
"""B04 收尾 3/3：suite-state 更新 + events 追加 + checkpoint 快照。"""
import json
import io
import os
from pathlib import Path
from datetime import datetime, timezone, timedelta

TZ8 = timezone(timedelta(hours=8))
ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", r"D:\mine\test\glm-5.3-flash")).resolve()
RUN = os.environ.get("SNAPSHOT_RUN_ID", "20261016T164020-m1")
SU = ROOT / "outputs" / RUN / "_suite"
TSU = ROOT / "tmp" / RUN / "_suite"
NOW = datetime.now(TZ8).isoformat(timespec="seconds")

state_path = SU / "suite-state.json"
state = json.load(io.open(state_path, encoding="utf-8"))

b04 = next(t for t in state["tasks"] if t["id"] == "B04")
b04.update({
    "status": "completed",
    "started_at": "2026-10-18T18:03:55+08:00",
    "ended_at": NOW,
    "output_dir": "outputs/%s/B04/" % RUN,
    "temp_dir": "tmp/%s/B04/" % RUN,
    "completed_rounds": [],
    "completed_cases": ["case-%02d" % i for i in range(1, 11)],
    "artifacts": ["portfolio.json", "portfolio.md", "gallery.md", "snapshot-usage.md",
                  "task-metrics.json", "sources.json", "editorial-note.md"],
    "visual_review_evidence": [
        "tmp/%s/B04/steps/sheet-1.png" % RUN, "tmp/%s/B04/steps/sheet-2.png" % RUN,
        "tmp/%s/B04/steps/sheet-3.png" % RUN, "tmp/%s/B04/steps/sheet-4.png" % RUN,
        "tmp/%s/B04/steps/sheet-5.png" % RUN,
        "tmp/%s/B04/steps/zoom-c08-bars-v4.png" % RUN],
    "unresolved_issues": [],
    "resume_notes": "",
    "final_images": 10,
})
state["current_task"] = "B05"
state["current_case"] = None
state["current_round"] = None
state["completed_task_count"] = 28
state["updated_at"] = NOW
prev_cp = state.get("last_checkpoint")
state["last_checkpoint"] = "state-000050.json"

state_path.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")

ev_path = TSU / "events.jsonl"
with ev_path.open("a", encoding="utf-8") as f:
    f.write(json.dumps({
        "id": "SUITE-ev-000053", "at": NOW, "kind": "task-completed", "task_id": "B04",
        "detail": "十件深海研究特辑《下潜 DEEP DIVE》：S01-S22 实抓留痕+claims 59 条台账；"
                  "21 渲染请求（20x200+1x400 已修复：case-08 裸<）；3 轮视觉迭代+1 语法修复，17 次看图；"
                  "sources.json/case.md/portfolio/gallery/metrics/editorial 齐套",
    }, ensure_ascii=False) + "\n")

cp_name = "state-000050.json"
snapshot = dict(state)
snapshot["checkpoint_id"] = cp_name
snapshot["checkpoint_at"] = NOW
snapshot["checkpoint_prev"] = prev_cp
(TSU / "checkpoints" / cp_name).write_text(
    json.dumps(snapshot, ensure_ascii=False, indent=1), encoding="utf-8")

print("suite-state: B04 completed, completed_task_count=28, current=B05")
print("event: SUITE-ev-000053 | checkpoint:", cp_name)
