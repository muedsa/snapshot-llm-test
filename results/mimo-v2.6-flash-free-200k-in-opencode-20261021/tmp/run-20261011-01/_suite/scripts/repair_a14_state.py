# -*- coding: utf-8 -*-
"""Repair A14 suite-state entry after update_state.py crashed on the
string-vs-dict outputs format at A14 completion (event seq 22 was written,
but the state entry update aborted). Backfills the A14 entry from its
delivered task-metrics.json, preserving the original completion timestamp
recorded in events.jsonl. Writes a repair checkpoint + event.
"""
import datetime
import json
import pathlib

ROOT = pathlib.Path(".")
RUN = "run-20261011-01"
state_path = ROOT / "outputs" / RUN / "_suite" / "suite-state.json"
state = json.loads(state_path.read_text(encoding="utf-8"))

# original A14 completion ts from the event log
events_path = ROOT / "tmp" / RUN / "_suite" / "events.jsonl"
lines = [json.loads(l) for l in events_path.read_text(encoding="utf-8").splitlines()
         if l.strip()]
a14_ev = next(e for e in lines if e.get("task_id") == "A14"
              and e.get("status") == "completed")
ended_at = a14_ev["ts"]

metrics = json.loads(
    (ROOT / "outputs" / RUN / "A14" / "task-metrics.json").read_text(encoding="utf-8"))
entry = next(t for t in state["tasks"] if t["id"] == "A14")
entry["status"] = "completed"
entry["ended_at"] = ended_at
entry["artifacts"] = [f"outputs/{RUN}/A14/{o}" for o in metrics["outputs"]]
entry["visual_review_evidence"] = [
    metrics["logs"]["requests"], metrics["logs"]["iterations"],
] + metrics["candidates"]
entry["completed_rounds"] = []
entry["completed_cases"] = []
entry["unresolved_issues"] = metrics.get("unresolved_issues", [])

now = datetime.datetime.now().astimezone().isoformat(timespec="milliseconds")
state["updated_at"] = now
state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")

seq = max(e["seq"] for e in lines) + 1
with events_path.open("a", encoding="utf-8") as fh:
    fh.write(json.dumps({
        "seq": seq, "ts": now, "event": "state_repair", "task_id": "A14",
        "status": "completed",
        "note": "backfilled A14 entry: update_state.py had crashed at A14 "
                "completion on outputs string-vs-dict format (event seq 22 "
                "already recorded completion); script now tolerates both; "
                "ended_at preserved from event ts",
        "path_base": "suite_root"}, ensure_ascii=False) + "\n")

cp_dir = ROOT / "tmp" / RUN / "_suite" / "checkpoints"
n = len(sorted(cp_dir.glob("state-*.json"))) + 1
cp = cp_dir / f"state-{n:06d}.json"
cp.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n",
              encoding="utf-8")
state["last_checkpoint"] = f"tmp/{RUN}/_suite/checkpoints/{cp.name}"
state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")
print(f"A14 repaired -> completed, artifacts={len(entry['artifacts'])}, "
      f"checkpoint {cp.name}, event seq {seq}")
