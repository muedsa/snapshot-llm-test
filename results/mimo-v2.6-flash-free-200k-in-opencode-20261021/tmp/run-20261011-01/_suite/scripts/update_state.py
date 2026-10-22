#!/usr/bin/env python3
"""Suite progress updater: suite-state.json + events.jsonl + numbered checkpoints.

Launch base: suite root.
Usage:
  python tmp/<run_id>/_suite/scripts/update_state.py <suite_root> <run_id> <task_id> \
      <status> <phase> <note>
  status: pending|in_progress|completed|partial|blocked
  phase:  started|round|case|completed|blocked
"""
import datetime
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
run_id = sys.argv[2]
task_id = sys.argv[3]
status = sys.argv[4]
phase = sys.argv[5]
note = sys.argv[6] if len(sys.argv) > 6 else ""

state_path = root / "outputs" / run_id / "_suite" / "suite-state.json"
state = json.loads(state_path.read_text(encoding="utf-8"))
now = datetime.datetime.now().astimezone().isoformat(timespec="milliseconds")

entry = next(t for t in state["tasks"] if t["id"] == task_id)
if phase == "started":
    entry["started_at"] = now
    entry["status"] = "in_progress"
elif phase == "completed":
    entry["ended_at"] = now
    entry["status"] = status
    metrics_path = root / "outputs" / run_id / task_id / "task-metrics.json"
    if metrics_path.exists():
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        arts = []
        for o in metrics.get("outputs", []):
            # outputs entries may be plain path strings (A01-A14 style) or
            # dicts {"file": ...}; tolerate both so completion never crashes
            fname = o["file"] if isinstance(o, dict) else o
            arts.append(f"outputs/{run_id}/{task_id}/{fname}")
        entry["artifacts"] = arts
        logs = metrics.get("logs", {})
        entry["visual_review_evidence"] = [
            logs.get("requests"), logs.get("iterations"),
        ] + [c["file"] if isinstance(c, dict) else c
             for c in metrics.get("candidates", [])]
        rounds = metrics.get("rounds") or []
        if rounds:
            entry["completed_rounds"] = [r.get("round") for r in rounds]
        else:
            entry["completed_rounds"] = []
        cases = metrics.get("cases") or []
        entry["completed_cases"] = [c.get("case") for c in cases]
        entry["unresolved_issues"] = metrics.get("unresolved_issues", []) or []
elif phase == "blocked":
    entry["status"] = status
    if note:
        entry["unresolved_issues"].append(note)
else:
    entry["status"] = "in_progress"

state["updated_at"] = now
state["current_task"] = task_id
state["status"] = "in_progress"
state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

events = root / "tmp" / run_id / "_suite" / "events.jsonl"
seq = 0
if events.exists():
    for line in events.read_text(encoding="utf-8").splitlines():
        if line.strip():
            seq = json.loads(line)["seq"]
seq += 1
with events.open("a", encoding="utf-8") as fh:
    fh.write(json.dumps({"seq": seq, "ts": now, "event": f"task_{phase}", "task_id": task_id,
                         "status": status, "note": note, "path_base": "suite_root"},
                        ensure_ascii=False) + "\n")

cp_dir = root / "tmp" / run_id / "_suite" / "checkpoints"
existing = sorted(cp_dir.glob("state-*.json"))
n = len(existing) + 1
cp = cp_dir / f"state-{n:06d}.json"
cp.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
state["last_checkpoint"] = f"tmp/{run_id}/_suite/checkpoints/{cp.name}"
state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"{task_id} {phase} -> {status} | checkpoint {cp.name} | event seq {seq}")
