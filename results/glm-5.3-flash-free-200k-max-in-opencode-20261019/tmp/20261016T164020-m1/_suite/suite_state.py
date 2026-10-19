# -*- coding: utf-8 -*-
"""套件状态维护：更新 suite-state.json 单题记录、追加 events、保存检查点。
用法：python suite_state.py <action> <task_id> [json 载荷文件]
  action: start | complete | append-event | checkpoint
载荷（complete 用）：
  {"artifacts": [...], "evidence": [...], "summary": "..."}
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import snapshot_client as sc

_suite_out = sc.suite_out() / "_suite"
_suite_tmp = sc.suite_tmp() / "_suite"

action, task_id = sys.argv[1], sys.argv[2]
payload = {}
if len(sys.argv) > 3:
    payload = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))

state_path = _suite_out / "suite-state.json"
state = json.loads(state_path.read_text(encoding="utf-8"))
task = next(t for t in state["tasks"] if t["id"] == task_id)


def ev(kind, detail):
    p = _suite_tmp / "events.jsonl"
    rec = {"id": f"SUITE-ev-{sc.count_lines(p)+1:06d}", "at": sc.now_iso(),
           "kind": kind, "task_id": task_id, "detail": detail}
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


if action == "start":
    task["status"] = "in_progress"
    task["started_at"] = sc.now_iso()
    state["current_task"] = task_id
    ev("task-started", f"{task_id} in_progress")
elif action == "complete":
    task["status"] = payload.get("status", "completed")
    task["ended_at"] = sc.now_iso()
    task["artifacts"] = payload.get("artifacts", task.get("artifacts"))
    task["visual_review_evidence"] = payload.get("evidence", [])
    if payload.get("summary"):
        task["resume_notes"] = payload["summary"]
    ev("task-completed", payload.get("summary", f"{task_id} completed"))

state["updated_at"] = sc.now_iso()
state["last_checkpoint"] = f"tmp/{sc.RUN_ID}/_suite/checkpoints/"
state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

n = sc.count_lines(_suite_tmp / "checkpoints" / "state-000001.json") if False else 0
cp_dir = _suite_tmp / "checkpoints"
cp_dir.mkdir(exist_ok=True)
existing = len(list(cp_dir.glob("state-*.json")))
cp_file = cp_dir / f"state-{existing + 1:06d}.json"
cp_file.write_text(json.dumps({
    "at": sc.now_iso(), "run_id": sc.RUN_ID, "action": action, "task_id": task_id,
    "summary": {t["id"]: t["status"] for t in state["tasks"]},
}, ensure_ascii=False, indent=2), encoding="utf-8")
res = {"state": task["id"], "status": task["status"], "checkpoint": cp_file.name}
print(json.dumps(res, ensure_ascii=False))
