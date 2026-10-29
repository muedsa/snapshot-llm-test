#!/usr/bin/env python3
"""Update suite-state.json, append events.jsonl and snapshot a checkpoint.
Usage: python state.py --task A01 --status completed --artifacts a,b [--note ...]
       python state.py --suite-start
       python state.py --suite-end
Paths are relative to the suite root; state lives in outputs/<run>/_suite/.
"""
import argparse, json, os, time
from datetime import datetime
from pathlib import Path

SCRIPT = Path(__file__).resolve()
SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", SCRIPT.parents[4]))
RUN_ID = SCRIPT.parents[2].name
OUT = SUITE_ROOT / "outputs" / RUN_ID / "_suite"
TMP = SUITE_ROOT / "tmp" / RUN_ID / "_suite"
OUT.mkdir(parents=True, exist_ok=True)
TMP.mkdir(parents=True, exist_ok=True)
STATE = OUT / "suite-state.json"
TASKS = ["A%02d" % i for i in range(1, 25)] + ["B%02d" % i for i in range(1, 7)]

def now():
    return datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")

def load():
    if STATE.exists():
        return json.loads(STATE.read_text(encoding="utf-8"))
    return {
        "schema_version": 1, "path_base": "suite_root", "suite_version": "1.0.0",
        "run_id": RUN_ID, "profile": "all", "status": "in_progress",
        "started_at": now(), "updated_at": now(), "current_task": None,
        "current_round": None, "current_case": None, "last_checkpoint": None,
        "tasks": [{"id": t, "status": "pending", "started_at": None, "ended_at": None,
                   "output_dir": f"outputs/{RUN_ID}/{t}", "temp_dir": f"tmp/{RUN_ID}/{t}",
                   "completed_rounds": [], "completed_cases": [], "artifacts": [],
                   "visual_review_evidence": [], "unresolved_issues": [],
                   "resume_notes": None} for t in TASKS],
        "suite_artifacts": [],
    }

def checkpoint(state):
    n = len(list((TMP / "checkpoints").glob("state-*.json"))) + 1
    p = TMP / "checkpoints" / f"state-{n:06d}.json"
    p.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    state["last_checkpoint"] = f"tmp/{RUN_ID}/_suite/checkpoints/{p.name}"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task")
    ap.add_argument("--status")
    ap.add_argument("--artifacts", default="")
    ap.add_argument("--note", default="")
    ap.add_argument("--suite-start", action="store_true")
    ap.add_argument("--suite-end", action="store_true")
    ap.add_argument("--current-round", default=None)
    ap.add_argument("--current-case", default=None)
    a = ap.parse_args()
    st = load()
    event = {"at": now(), "run_id": RUN_ID}
    if a.suite_start:
        st["status"] = "in_progress"
        st["started_at"] = st.get("started_at") or now()
        event.update(event="suite_start")
    elif a.suite_end:
        done = sum(1 for t in st["tasks"] if t["status"] == "completed")
        st["status"] = "completed" if done == len(TASKS) else "partial"
        event.update(event="suite_end", completed=done)
    elif a.task:
        for t in st["tasks"]:
            if t["id"] == a.task:
                if a.status == "in_progress" and not t["started_at"]:
                    t["started_at"] = now()
                if a.status in ("completed", "partial", "blocked"):
                    t["ended_at"] = now()
                t["status"] = a.status or t["status"]
                if a.artifacts:
                    t["artifacts"] = [x for x in a.artifacts.split(",") if x]
                if a.note:
                    t["resume_notes"] = a.note
                st["current_task"] = a.task
                if a.current_round: st["current_round"] = a.current_round
                if a.current_case: st["current_case"] = a.current_case
                event.update(event="task_" + (a.status or "update"), task=a.task,
                             artifacts=t["artifacts"])
                break
    st["updated_at"] = now()
    checkpoint(st)
    STATE.write_text(json.dumps(st, ensure_ascii=False, indent=2), encoding="utf-8")
    with (TMP / "events.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
    print(json.dumps(event, ensure_ascii=False))

if __name__ == "__main__":
    main()
