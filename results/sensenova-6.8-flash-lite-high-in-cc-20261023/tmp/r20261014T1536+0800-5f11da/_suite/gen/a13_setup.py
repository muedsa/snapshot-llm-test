"""A13 启动：创建 tmp/outputs 目录、追加 task_started 事件、登记 in_progress。

用法：SNAPSHOT_RUN_ID=<rid> python -I tmp/<rid>/_suite/gen/a13_setup.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(HERE.parent))
import suite as S  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

TASK = "A13"
RID = S.run_id()
OUT, TMP = S.task_dirs(TASK)
SDIR, TSDIR = S.suite_dirs()
STATE = SDIR / "suite-state.json"

for p in (OUT, TMP / "dsl", TMP / "responses", TMP / "preview", TMP / "gen"):
    p.mkdir(parents=True, exist_ok=True)

state = S.load_state()
state["tasks_detail"] = [t for t in state.get("tasks_detail", []) if t.get("id") != TASK]
entry = {
    "id": TASK, "status": "in_progress", "started_at": S.now_iso(),
    "ended_at": None, "elapsed_seconds": None,
    "title": "品牌标志到完整活动应用",
    "output_dir": S.rel(OUT), "temp_dir": S.rel(TMP),
    "artifacts": [], "metrics": None,
    "unresolved_issues": [], "recorded_at": S.now_iso()}
state["tasks_detail"].append(entry)
if TASK in state.get("completed", []):
    state["completed"] = [t for t in state["completed"] if t != TASK]
if TASK not in state.get("remaining", []):
    state["remaining"].append(TASK)
    state["remaining"].sort()
state["current_task"] = TASK
state["status"] = "in_progress"
state["counts_by_status"] = {
    "completed": len(set(state.get("completed", []))),
    "in_progress": 1,
    "pending": len(state.get("remaining", [])) - 1}
state["updated_at"] = S.now_iso()
S.save_state(state)

ev_before = sum(1 for l in (TSDIR / "events.jsonl").read_text(
    encoding="utf-8", errors="replace").splitlines() if l.strip())
S.append_event({"ts": S.now_iso(), "event": "task_started", "task_id": TASK,
                "title": entry["title"],
                "output_dir": S.rel(OUT), "temp_dir": S.rel(TMP)})
ck = S.snapshot_checkpoint(state)
state["last_checkpoint"] = ck
S.save_state(state)

print("OUT", S.rel(OUT))
print("TMP", S.rel(TMP))
print("counts", json.dumps(state["counts_by_status"], ensure_ascii=False))
print("events", ev_before, "->", ev_before + 1)
print("checkpoint", ck)
