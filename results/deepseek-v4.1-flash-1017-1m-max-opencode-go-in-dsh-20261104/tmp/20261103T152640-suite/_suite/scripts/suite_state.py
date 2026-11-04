# -*- coding: utf-8 -*-
"""Suite state manager: suite-state.json + events.jsonl + numbered checkpoints.

Script base: suite_root. All persisted paths are relative to the suite root.
Usage (from suite root):
    python tmp/<run_id>/_suite/scripts/suite_state.py set A01 in_progress
    python tmp/<run_id>/_suite/scripts/suite_state.py event started A01 "..."
    python tmp/<run_id>/_suite/scripts/suite_state.py checkpoint
"""
from __future__ import annotations

import json
import os
import sys
import datetime
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "20261103T152640-suite")
OUT_SUITE = SUITE_ROOT / "outputs" / RUN_ID / "_suite"
TMP_SUITE = SUITE_ROOT / "tmp" / RUN_ID / "_suite"
STATE_PATH = OUT_SUITE / "suite-state.json"
EVENTS = TMP_SUITE / "events.jsonl"
CHECKPOINTS = TMP_SUITE / "checkpoints"

TASK_IDS = [f"A{i:02d}" for i in range(1, 25)] + [f"B{i:02d}" for i in range(1, 7)]


def iso() -> str:
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def load() -> dict:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return new_state()


def new_state() -> dict:
    return {
        "schema_version": 1,
        "path_base": "suite_root",
        "suite_version": "1.0.0",
        "run_id": RUN_ID,
        "profile": "all",
        "status": "in_progress",
        "started_at": iso(),
        "updated_at": iso(),
        "current_task": None,
        "current_round": None,
        "current_case": None,
        "last_checkpoint": None,
        "output_root": f"outputs/{RUN_ID}",
        "temp_root": f"tmp/{RUN_ID}",
        "service_base_url": "https://open-snapshot.muedsa.com",
        "tasks": [
            {
                "id": tid,
                "status": "pending",
                "started_at": None,
                "ended_at": None,
                "output_dir": f"outputs/{RUN_ID}/{tid}/",
                "temp_dir": f"tmp/{RUN_ID}/{tid}/",
                "completed_rounds": [],
                "completed_cases": [],
                "artifacts": [],
                "visual_review_evidence": [],
                "unresolved_issues": [],
                "resume_notes": None,
            }
            for tid in TASK_IDS
        ],
        "suite_artifacts": [],
    }


def save(state: dict) -> None:
    state["updated_at"] = iso()
    OUT_SUITE.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def event(kind: str, task: str | None, message: str, **extra) -> None:
    CHECKPOINTS.parent.mkdir(parents=True, exist_ok=True)
    rec = {
        "at": iso(),
        "tz": "Asia/Shanghai",
        "kind": kind,
        "task": task,
        "message": message,
        "run_id": RUN_ID,
        "path_base": "suite_root",
    }
    rec.update(extra)
    with EVENTS.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def checkpoint(state: dict) -> str:
    CHECKPOINTS.mkdir(parents=True, exist_ok=True)
    n = 1
    while True:
        p = CHECKPOINTS / f"state-{n:06d}.json"
        if not p.exists():
            break
        n += 1
    p.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    state["last_checkpoint"] = p.relative_to(SUITE_ROOT).as_posix()
    return state["last_checkpoint"]


def task(state: dict, tid: str) -> dict:
    for t in state["tasks"]:
        if t["id"] == tid:
            return t
    raise KeyError(tid)


def cmd_set(tid: str, status: str, **fields) -> None:
    st = load()
    t = task(st, tid)
    t["status"] = status
    if status in ("in_progress", "completed", "partial", "blocked") and not t["started_at"]:
        t["started_at"] = iso()
    if status in ("completed", "partial", "blocked"):
        t["ended_at"] = iso()
    for k, v in fields.items():
        t[k] = v
    st["current_task"] = tid if status == "in_progress" else st.get("current_task")
    ck = checkpoint(st)
    save(st)
    event("task_status", tid, status, checkpoint=ck)
    print(json.dumps({"task": tid, "status": status, "checkpoint": ck}, ensure_ascii=False))


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 1
    cmd = argv[0]
    if cmd == "init":
        st = new_state()
        ck = checkpoint(st)
        save(st)
        event("suite_started", None, "suite state initialised", checkpoint=ck)
        print(f"initialised {STATE_PATH.relative_to(SUITE_ROOT).as_posix()} checkpoint={ck}")
        return 0
    if cmd == "set":
        tid, status = argv[1], argv[2]
        fields = {}
        for item in argv[3:]:
            if "=" in item:
                k, v = item.split("=", 1)
                try:
                    fields[k] = json.loads(v)
                except json.JSONDecodeError:
                    fields[k] = v
        cmd_set(tid, status, **fields)
        return 0
    if cmd == "event":
        event(argv[1], argv[2] if len(argv) > 2 else None, argv[3] if len(argv) > 3 else "")
        print("event logged")
        return 0
    if cmd == "checkpoint":
        st = load()
        ck = checkpoint(st)
        save(st)
        print(f"checkpoint {ck}")
        return 0
    if cmd == "show":
        st = load()
        counts: dict[str, int] = {}
        for t in st["tasks"]:
            counts[t["status"]] = counts.get(t["status"], 0) + 1
        print(json.dumps({"status": st["status"], "counts": counts,
                          "current": st["current_task"]}, ensure_ascii=False))
        return 0
    print(__doc__)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
