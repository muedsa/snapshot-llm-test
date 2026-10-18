"""Suite state / checkpoint helper.

    python tmp/<run_id>/_suite/scripts/suite_state.py \
        --task A01 --status completed --artifacts operations.png ...

Creates outputs/<run_id>/_suite/suite-state.json from the suite template on first
use, appends tmp/<run_id>/_suite/events.jsonl and writes numbered checkpoints.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

TZ = timezone(timedelta(hours=8))


def root() -> Path:
    return Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()


def rid() -> str:
    value = os.environ.get("SNAPSHOT_RUN_ID")
    if not value:
        raise SystemExit("SNAPSHOT_RUN_ID is required")
    return value


def now() -> str:
    return datetime.now(TZ).replace(microsecond=0).isoformat()


def state_path() -> Path:
    return root() / "outputs" / rid() / "_suite" / "suite-state.json"


def load_state() -> dict:
    p = state_path()
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    tpl = json.loads((root() / "templates" / "suite-state-template.json").read_text(encoding="utf-8"))
    tpl["run_id"] = rid()
    tpl["status"] = "in_progress"
    tpl["started_at"] = now()
    tpl["updated_at"] = now()
    for t in tpl["tasks"]:
        t["output_dir"] = f"outputs/{rid()}/{t['id']}"
        t["temp_dir"] = f"tmp/{rid()}/{t['id']}"
    return tpl


def save_state(state: dict) -> None:
    state["updated_at"] = now()
    p = state_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    events = root() / "tmp" / rid() / "_suite" / "events.jsonl"
    events.parent.mkdir(parents=True, exist_ok=True)
    with events.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({
            "ts": now(), "event": "state_update", "current_task": state.get("current_task"),
            "status": state.get("status"), "task_statuses": {
                t["id"]: t["status"] for t in state["tasks"]},
        }, ensure_ascii=False) + "\n")


def checkpoint(state: dict, note: str) -> str:
    cdir = root() / "tmp" / rid() / "_suite" / "checkpoints"
    cdir.mkdir(parents=True, exist_ok=True)
    existing = sorted(cdir.glob("state-*.json"))
    num = len(existing) + 1
    name = f"state-{num:06d}.json"
    (cdir / name).write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    state["last_checkpoint"] = f"tmp/{rid()}/_suite/checkpoints/{name}"
    events = root() / "tmp" / rid() / "_suite" / "events.jsonl"
    with events.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"ts": now(), "event": "checkpoint", "file": state["last_checkpoint"],
                             "note": note}, ensure_ascii=False) + "\n")
    return state["last_checkpoint"]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task")
    ap.add_argument("--status")
    ap.add_argument("--current-round")
    ap.add_argument("--current-case")
    ap.add_argument("--note", default="")
    ap.add_argument("--artifacts", nargs="*")
    ap.add_argument("--review", nargs="*")
    ap.add_argument("--issues", nargs="*")
    ap.add_argument("--resume-notes")
    ap.add_argument("--suite-status")
    ap.add_argument("--checkpoint", action="store_true")
    args = ap.parse_args(argv)

    state = load_state()
    if args.suite_status:
        state["status"] = args.suite_status
    if args.task:
        state["current_task"] = args.task
        for t in state["tasks"]:
            if t["id"] != args.task:
                continue
            if args.status:
                t["status"] = args.status
                if args.status == "in_progress" and not t["started_at"]:
                    t["started_at"] = now()
                if args.status in ("completed", "partial", "blocked"):
                    t["ended_at"] = now()
            if args.artifacts:
                t["artifacts"] = args.artifacts
            if args.review:
                t["visual_review_evidence"] = args.review
            if args.issues is not None:
                t["unresolved_issues"] = args.issues
            if args.resume_notes:
                t["resume_notes"] = args.resume_notes
    if args.current_round:
        state["current_round"] = args.current_round
    if args.current_case:
        state["current_case"] = args.current_case
    if args.status == "completed" and args.task:
        # keep current_task as the next task when the caller says so; otherwise this one
        pass
    if args.checkpoint:
        checkpoint(state, args.note or f"{args.task or 'suite'} {args.status or ''}")
    save_state(state)
    print(json.dumps({"current_task": state.get("current_task"), "status": state.get("status"),
                      "checkpoint": state.get("last_checkpoint")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
