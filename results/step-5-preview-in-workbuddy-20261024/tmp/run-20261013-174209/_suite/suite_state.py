"""套件进度管理：suite-state.json、events.jsonl、checkpoints。

启动基准：总任务根（或 SNAPSHOT_TASK_ROOT 指向总任务根）。
suite-state.json 是允许更新的当前指针；历史快照不可覆盖。
"""

from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
from typing import Any

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ["SNAPSHOT_RUN_ID"]
SUITE_OUT = ROOT / "outputs" / RUN_ID / "_suite"
SUITE_TMP = ROOT / "tmp" / RUN_ID / "_suite"
TEMPLATE = ROOT / "templates" / "suite-state-template.json"
STATE = SUITE_OUT / "suite-state.json"
EVENTS = SUITE_TMP / "events.jsonl"
CKPT_DIR = SUITE_TMP / "checkpoints"

for d in (SUITE_OUT, SUITE_TMP, CKPT_DIR):
    d.mkdir(parents=True, exist_ok=True)


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="milliseconds")


def load() -> dict[str, Any]:
    if STATE.exists():
        return json.loads(STATE.read_text(encoding="utf-8"))
    base = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    base["run_id"] = RUN_ID
    base["profile"] = "all"
    base["status"] = "in_progress"
    base["started_at"] = now_iso()
    for t in base["tasks"]:
        t["output_dir"] = f"outputs/{RUN_ID}/{t['id']}/"
        t["temp_dir"] = f"tmp/{RUN_ID}/{t['id']}/"
    return base


def save(state: dict[str, Any], *, checkpoint: bool = True) -> None:
    state["updated_at"] = now_iso()
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if checkpoint:
        n = len(list(CKPT_DIR.glob("state-*.json"))) + 1
        (CKPT_DIR / f"state-{n:06d}.json").write_text(
            json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def event(kind: str, **kw: Any) -> None:
    rec = {"ts": now_iso(), "run_id": RUN_ID, "kind": kind, **kw}
    with EVENTS.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def find(state: dict[str, Any], task_id: str) -> dict[str, Any]:
    for t in state["tasks"]:
        if t["id"] == task_id:
            return t
    raise KeyError(task_id)


def start_task(task_id: str) -> dict[str, Any]:
    st = load()
    t = find(st, task_id)
    t["status"] = "in_progress"
    t["started_at"] = now_iso()
    st["current_task"] = task_id
    save(st)
    event("task_started", task_id=task_id)
    return st


def complete_task(task_id: str, *, artifacts: list[str], evidence: list[str],
                  cases: list[str] | None = None) -> dict[str, Any]:
    st = load()
    t = find(st, task_id)
    t["status"] = "completed"
    t["ended_at"] = now_iso()
    t["artifacts"] = artifacts
    t["visual_review_evidence"] = evidence
    t["completed_cases"] = cases or []
    t["unresolved_issues"] = []
    t["resume_notes"] = None
    save(st)
    event("task_completed", task_id=task_id, artifacts=artifacts)
    return st


if __name__ == "__main__":
    print(STATE.relative_to(ROOT).as_posix())
