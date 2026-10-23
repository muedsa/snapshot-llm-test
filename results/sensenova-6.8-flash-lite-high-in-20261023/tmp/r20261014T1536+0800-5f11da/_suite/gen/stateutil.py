"""全套进度状态更新工具（可复用）。

职责单一：把一题的状态变更同时落到三处，保证 suite-state.json、
events.jsonl 与 checkpoints/state-NNNNNN.json 三者一致。

约定：
* suite-state.json 是允许更新的「当前指针」；
* events.jsonl 只增不改；
* checkpoints/state-NNNNNN.json 只增不改、编号严格递增；
* 所有新写出的路径都是正斜杠相对路径（PATHS.md），path_base=suite_root；
* 历史条目里已有的反斜杠路径一律原样保留——那是不可改写的记录。
"""
from __future__ import annotations

import json
import pathlib
import time


def _ts() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S+08:00")


def _tid_key(tid: str):
    return (tid[0], int(tid[1:])) if tid[:2] in ("A0", "A1", "A2", "B0") else (tid, 0)


def next_checkpoint_number(cp_dir: pathlib.Path) -> int:
    if not cp_dir.exists():
        return 1
    nums = [int(p.stem.split("-")[1]) for p in cp_dir.glob("state-*.json")
            if p.stem.split("-")[1].isdigit()]
    return (max(nums) + 1) if nums else 1


def mark_task_completed(suite_root: pathlib.Path, run_id: str,
                        task_id: str, entry: dict,
                        *, event: dict, next_task: str,
                        progress_note: str | None = None) -> dict:
    """把 task_id 标为 completed 并同步三处记录。

    entry 是 tasks_detail 的新条目（须含 id / status / started_at / ended_at /
    elapsed_seconds / output_dir / temp_dir / artifacts / logs）；
    event 是追加到 events.jsonl 的事件体（须含 ts / timezone / event / task_id /
    run_id / status / detail / next_task），本函数补全 checkpoint 字段。

    幂等：若 task_id 已在 completed 中则不重复计数。
    """
    out_dir = suite_root / "outputs" / run_id / "_suite"
    tmp_dir = suite_root / "tmp" / run_id / "_suite"
    cp_dir = tmp_dir / "checkpoints"
    state_path = out_dir / "suite-state.json"

    state = json.loads(state_path.read_text(encoding="utf-8"))
    now = _ts()
    already = task_id in state.get("completed", [])

    if not already:
        state.setdefault("completed", []).append(task_id)
    state["remaining"] = [t for t in state.get("remaining", []) if t != task_id]
    state["completed"] = sorted(state["completed"], key=_tid_key)

    detail = [t for t in state.get("tasks_detail", []) if t.get("id") != task_id]
    detail.append(entry)
    state["tasks_detail"] = detail

    cbs = state.setdefault("counts_by_status", {})
    cbs["completed"] = len(state["completed"])
    cbs["in_progress"] = 0 if already else max(0, cbs.get("in_progress", 1) - 1)
    cbs["pending"] = len(state.get("remaining", []))

    state["completed_all"] = not state.get("remaining")
    state["current_task"] = next_task
    state["status"] = "completed" if state["completed_all"] else "in_progress"
    state["updated_at"] = now
    if progress_note:
        state["suite_progress_note"] = progress_note

    cp_num = next_checkpoint_number(cp_dir)
    cp_path = cp_dir / ("state-%06d.json" % cp_num)
    cp = dict(state)
    cp["last_checkpoint"] = cp_path.relative_to(suite_root).as_posix()

    out_dir.mkdir(parents=True, exist_ok=True)
    cp_dir.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(cp, ensure_ascii=False, indent=1),
                          encoding="utf-8")
    cp_path.write_text(json.dumps(cp, ensure_ascii=False, indent=1),
                       encoding="utf-8")

    ev = dict(event)
    ev["checkpoint"] = cp_path.relative_to(suite_root).as_posix()
    with (tmp_dir / "events.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(ev, ensure_ascii=False) + "\n")

    return {"state": state_path.relative_to(suite_root).as_posix(),
            "checkpoint": cp_path.relative_to(suite_root).as_posix(),
            "checkpoint_number": cp_num,
            "counts_by_status": cp["counts_by_status"],
            "completed_count": len(cp["completed"]),
            "remaining": cp["remaining"],
            "current_task": cp["current_task"]}
