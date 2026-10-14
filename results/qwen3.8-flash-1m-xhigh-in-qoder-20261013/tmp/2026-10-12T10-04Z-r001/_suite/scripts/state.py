"""Maintain suite-state.json, events.jsonl and numbered checkpoints.

Run from the suite task root (or set SNAPSHOT_TASK_ROOT).

  python tmp/<run_id>/_suite/scripts/state.py init --run-id <id>
  python tmp/<run_id>/_suite/scripts/state.py task --id A01 --status in_progress
  python tmp/<run_id>/_suite/scripts/state.py task --id A01 --status completed \
      --artifact outputs/<run_id>/A01/operations.png --evidence "checked final render"
  python tmp/<run_id>/_suite/scripts/state.py event --type render --data '{"k":"v"}'
  python tmp/<run_id>/_suite/scripts/state.py checkpoint --note "A01 done"

State lives at outputs/<run_id>/_suite/suite-state.json (path_base: suite_root).
Events and checkpoints live at tmp/<run_id>/_suite/.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
TEMPLATE = ROOT / "templates" / "suite-state-template.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def resolve(p: str) -> Path:
    q = Path(p)
    return q if q.is_absolute() else ROOT / q


def rel(p: Path) -> str:
    try:
        return p.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return p.as_posix()


class Store:
    def __init__(self, run_id: str):
        self.run_id = run_id
        self.state_file = resolve(f"outputs/{run_id}/_suite/suite-state.json")
        self.tmp_suite = resolve(f"tmp/{run_id}/_suite")
        self.events = self.tmp_suite / "events.jsonl"
        self.ckpt_dir = self.tmp_suite / "checkpoints"

    def load(self) -> dict:
        if self.state_file.exists():
            return json.loads(self.state_file.read_text(encoding="utf-8"))
        st = json.loads(TEMPLATE.read_text(encoding="utf-8"))
        st["run_id"] = self.run_id
        st["status"] = "in_progress"
        st["started_at"] = now_iso()
        return st

    def save(self, st: dict) -> None:
        st["updated_at"] = now_iso()
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state_file.write_text(
            json.dumps(st, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    def emit(self, etype: str, data: dict) -> None:
        self.events.parent.mkdir(parents=True, exist_ok=True)
        rec = {"ts": now_iso(), "type": etype, "run_id": self.run_id}
        rec.update(data)
        with self.events.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

    def checkpoint(self, note: str) -> str:
        self.ckpt_dir.mkdir(parents=True, exist_ok=True)
        nums = [
            int(p.stem.split("-")[1])
            for p in self.ckpt_dir.glob("state-*.json")
            if p.stem.split("-")[1].isdigit()
        ]
        nxt = (max(nums) + 1) if nums else 1
        path = self.ckpt_dir / f"state-{nxt:06d}.json"
        st = json.loads(self.state_file.read_text(encoding="utf-8"))
        st["last_checkpoint"] = rel(path)
        path.write_text(json.dumps(st, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        self.emit("checkpoint", {"note": note, "path": rel(path)})
        return rel(path)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["init", "task", "event", "checkpoint", "show"])
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--id", help="task id for `task`")
    ap.add_argument("--status")
    ap.add_argument("--round", dest="round_", default=None)
    ap.add_argument("--case", default=None)
    ap.add_argument("--artifact", action="append", default=[])
    ap.add_argument("--evidence", action="append", default=[])
    ap.add_argument("--issue", action="append", default=[])
    ap.add_argument("--resume-notes", default=None)
    ap.add_argument("--type", default=None)
    ap.add_argument("--data", default=None)
    ap.add_argument("--note", default="")
    ap.add_argument("--suite-artifact", action="append", default=[])
    a = ap.parse_args()

    s = Store(a.run_id)

    if a.action == "init":
        st = s.load()
        st["profile"] = st.get("profile") or "all"
        st["current_task"] = None
        s.save(st)
        s.emit("run_init", {"profile": st["profile"], "task_count": len(st["tasks"])})
        print(json.dumps({"ok": True, "state": rel(s.state_file)}, ensure_ascii=False))
        return 0

    if a.action == "show":
        st = s.load()
        counts: dict[str, int] = {}
        for t in st["tasks"]:
            counts[t["status"]] = counts.get(t["status"], 0) + 1
        print(json.dumps({"status": st["status"], "counts": counts}, ensure_ascii=False))
        return 0

    st = s.load()

    if a.action == "event":
        payload = json.loads(a.data) if a.data else {}
        s.emit(a.type or "event", payload)
        print(json.dumps({"ok": True}, ensure_ascii=False))
        return 0

    if a.action == "checkpoint":
        print(json.dumps({"ok": True, "path": s.checkpoint(a.note)}, ensure_ascii=False))
        return 0

    # task
    task = next((t for t in st["tasks"] if t["id"] == a.id), None)
    if task is None:
        print(f"unknown task {a.id}", file=sys.stderr)
        return 2
    if a.status:
        if a.status == "in_progress" and not task["started_at"]:
            task["started_at"] = now_iso()
            st["current_task"] = task["id"]
        if a.status in ("completed", "partial", "blocked"):
            task["ended_at"] = now_iso()
        task["status"] = a.status
    for art in a.artifact:
        if art not in task["artifacts"]:
            task["artifacts"].append(art)
    for ev in a.evidence:
        if ev not in task["visual_review_evidence"]:
            task["visual_review_evidence"].append(ev)
    for iss in a.issue:
        if iss not in task["unresolved_issues"]:
            task["unresolved_issues"].append(iss)
    if a.round_ and a.round_ not in task["completed_rounds"]:
        task["completed_rounds"].append(a.round_)
    if a.case and a.case not in task["completed_cases"]:
        task["completed_cases"].append(a.case)
    if a.resume_notes:
        task["resume_notes"] = a.resume_notes
    task.setdefault("output_dir", f"outputs/{s.run_id}/{a.id}/")
    task.setdefault("temp_dir", f"tmp/{s.run_id}/{a.id}/")
    for sa in a.suite_artifact:
        if sa not in st["suite_artifacts"]:
            st["suite_artifacts"].append(sa)
    if a.status == "in_progress":
        st["current_task"] = a.id
        st["current_round"] = a.round_
        st["current_case"] = a.case
    pending = [t["id"] for t in st["tasks"] if t["status"] in ("pending", "in_progress")]
    st["status"] = "in_progress" if pending else "completed"
    s.save(st)
    s.emit(
        "task_status",
        {"task": a.id, "status": a.status, "round": a.round_, "case": a.case},
    )
    print(json.dumps({"ok": True, "task": a.id, "status": a.status}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
