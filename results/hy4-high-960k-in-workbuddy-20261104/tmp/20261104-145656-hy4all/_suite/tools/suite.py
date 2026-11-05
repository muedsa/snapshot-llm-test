#!/usr/bin/env python3
"""Suite-level helpers: paths, state, events, checkpoints, logs, metrics.

All local paths in records are relative to the suite root (path_base=suite_root).
The suite root is read from SNAPSHOT_TASK_ROOT (defaults to cwd); run id from
SNAPSHOT_RUN_ID.  No machine-specific path is persisted.
"""
from __future__ import annotations
import datetime
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RID = os.environ.get("SNAPSHOT_RUN_ID", "")
if not RID:
    raise SystemExit("SNAPSHOT_RUN_ID is required")
OUT = ROOT / "outputs" / RID
TMP = ROOT / "tmp" / RID
SUITE_OUT = OUT / "_suite"
SUITE_TMP = TMP / "_suite"
BASE_URL = os.environ.get("SNAPSHOT_BASE_URL", "https://open-snapshot.muedsa.com")

TASK_IDS = ["A%02d" % i for i in range(1, 25)] + ["B%02d" % i for i in range(1, 7)]


def now():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def rel(p) -> str:
    try:
        return Path(p).resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return Path(p).name


def out_dir(task, sub=""):
    d = OUT / task / sub if sub else OUT / task
    d.mkdir(parents=True, exist_ok=True)
    return d


def tmp_dir(task, sub=""):
    d = TMP / task / sub if sub else TMP / task
    d.mkdir(parents=True, exist_ok=True)
    return d


def rel_out(task, name=""):
    return "outputs/%s/%s/%s" % (RID, task, name) if name else "outputs/%s/%s/" % (RID, task)


def rel_tmp(task, name=""):
    return "tmp/%s/%s/%s" % (RID, task, name) if name else "tmp/%s/%s/" % (RID, task)


# ------------------------------------------------------------------ state
def load_state():
    p = SUITE_OUT / "suite-state.json"
    if not p.exists():
        state = {
            "schema_version": 1, "path_base": "suite_root", "suite_version": "1.0.0",
            "run_id": RID, "profile": "all", "status": "in_progress",
            "started_at": now(), "updated_at": now(), "current_task": None,
            "current_round": None, "current_case": None, "last_checkpoint": None,
            "tasks": [
                {"id": t, "status": "pending", "started_at": None, "ended_at": None,
                 "output_dir": rel_out(t), "temp_dir": rel_tmp(t),
                 "completed_rounds": [], "completed_cases": [], "artifacts": [],
                 "visual_review_evidence": [], "unresolved_issues": [], "resume_notes": None}
                for t in TASK_IDS
            ],
            "suite_artifacts": [],
        }
        save_state(state)
        return state
    return json.loads(p.read_text(encoding="utf-8"))


def save_state(state):
    SUITE_OUT.mkdir(parents=True, exist_ok=True)
    state["updated_at"] = now()
    (SUITE_OUT / "suite-state.json").write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def task_state(state, tid):
    return next(t for t in state["tasks"] if t["id"] == tid)


def event(kind, **fields):
    SUITE_TMP.mkdir(parents=True, exist_ok=True)
    e = {"seq_time": now(), "run_id": RID, "kind": kind, **fields}
    with (SUITE_TMP / "events.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(e, ensure_ascii=False) + "\n")
    return e


def checkpoint(state, note=""):
    d = SUITE_TMP / "checkpoints"
    d.mkdir(parents=True, exist_ok=True)
    n = len(list(d.glob("state-*.json"))) + 1
    name = "state-%06d.json" % n
    (d / name).write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    state["last_checkpoint"] = "tmp/%s/_suite/checkpoints/%s" % (RID, name)
    event("checkpoint", path=state["last_checkpoint"], note=note)
    return state["last_checkpoint"]


def task_start(tid, note=""):
    state = load_state()
    t = task_state(state, tid)
    t["status"] = "in_progress"
    t["started_at"] = now()
    state["current_task"] = tid
    save_state(state)
    event("task_start", task_id=tid, note=note)
    return state


def task_done(tid, artifacts=None, rounds=None, cases=None, evidence=None, issues=None, status="completed"):
    state = load_state()
    t = task_state(state, tid)
    t["status"] = status
    t["ended_at"] = now()
    if artifacts:
        t["artifacts"] = list(dict.fromkeys(t["artifacts"] + list(artifacts)))
    if rounds:
        t["completed_rounds"] = list(dict.fromkeys(t["completed_rounds"] + list(rounds)))
    if cases:
        t["completed_cases"] = list(dict.fromkeys(t["completed_cases"] + list(cases)))
    if evidence:
        t["visual_review_evidence"] = list(t["visual_review_evidence"]) + list(evidence)
    if issues:
        t["unresolved_issues"] = list(issues)
    state["current_task"] = tid
    save_state(state)
    event("task_done", task_id=tid, status=status, artifacts=t["artifacts"], note="")
    checkpoint(state, note="after %s %s" % (tid, status))
    return state


# ------------------------------------------------------------------ logs
def append_jsonl(task, filename, record):
    d = tmp_dir(task)
    with (d / filename).open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def iteration(task, version_id, parent, itype, image, viewed_at, observed, change,
              result, complete=True, extra=None):
    rec = {
        "task_id": task, "version_id": version_id, "parent_version": parent,
        "type": itype, "image": image, "viewed_at": viewed_at,
        "observed_issues": observed, "change": change, "recheck_result": result,
        "complete": complete, "time": now(),
    }
    if extra:
        rec.update(extra)
    append_jsonl(task, "iterations.jsonl", rec)


def tool_usage(task, tool, purpose, result, source=None):
    append_jsonl(task, "tool-usage.jsonl", {
        "task_id": task, "time": now(), "tool": tool, "purpose": purpose,
        "result": result, "source": source,
    })


def read_request_log(task):
    base = TMP / task
    files = sorted(base.rglob("requests.jsonl")) if base.exists() else []
    recs = []
    for p in files:
        for x in p.read_text(encoding="utf-8").splitlines():
            if x.strip():
                try:
                    recs.append(json.loads(x))
                except Exception:
                    pass
    return recs


def summarize_requests(task):
    recs = read_request_log(task)
    attempts = [a for r in recs for a in r.get("attempts", [])]
    return {
        "render_requests": len(attempts),
        "successful": sum(1 for a in attempts if a.get("success")),
        "failed": sum(1 for a in attempts if not a.get("success")),
        "retries": sum(1 for a in attempts if a.get("attempt", 0) > 0),
        "request_ms_sum": round(sum(a.get("duration_ms", 0) for a in attempts), 1),
    }


def write_metrics(task, started_at, extra=None):
    r = summarize_requests(task)
    it = tmp_dir(task) / "iterations.jsonl"
    its = [json.loads(x) for x in it.read_text(encoding="utf-8").splitlines() if x.strip()] if it.exists() else []
    views = sum(1 for x in its if x.get("viewed_at"))
    st = task_state(load_state(), task)
    ended_at = (st.get("ended_at") if st.get("status") in ("completed", "partial", "blocked") else None) or now()
    try:
        elapsed = round((datetime.datetime.fromisoformat(ended_at) -
                         datetime.datetime.fromisoformat(started_at)).total_seconds(), 2)
    except Exception:
        elapsed = None
    first_ok = None
    for rec in read_request_log(task):
        for a in rec.get("attempts", []):
            if a.get("success"):
                try:
                    first_ok = round((datetime.datetime.fromisoformat(a["started_at"]) -
                                       datetime.datetime.fromisoformat(started_at)).total_seconds(), 2)
                except Exception:
                    pass
                break
        if first_ok is not None:
            break
    m = {
        "schema_version": 1, "path_base": "suite_root", "task_id": task, "run_id": RID,
        "started_at": started_at, "ended_at": ended_at,
        "elapsed_seconds": elapsed,
        "first_image_seconds": first_ok,
        "user_feedback_wait_seconds": 0,
        "rate_limit_wait_seconds": None,
        "queue_wait_seconds": None,
        "request_duration_sum_seconds": round(r["request_ms_sum"] / 1000, 3),
        "render_requests": r["render_requests"],
        "successful_requests": r["successful"],
        "failed_requests": r["failed"],
        "retry_requests": r["retries"],
        "other_service_requests": 0,
        "document_requests": 0,
        "dsl_versions": len({x.get("version_id") for x in its}),
        "image_views": views,
        "completed_visual_iterations": sum(1 for x in its if x.get("type") == "visual" and x.get("complete")),
        "incomplete_visual_iterations": sum(1 for x in its if not x.get("complete")),
        "counts_source": "requests.jsonl + iterations.jsonl (task temp dir)",
        "timing_source": "local wall-clock timestamps with timezone",
    }
    if extra:
        m.update(extra)
    (out_dir(task) / "task-metrics.json").write_text(
        json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return m


def write_report(task, text):
    (out_dir(task) / "snapshot-usage.md").write_text(text, encoding="utf-8")
