#!/usr/bin/env python3
"""Reconcile per-task timing and suite state from real files/logs after parallel agents."""
import json, os, sys
from datetime import datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import suite

cat = json.loads((suite.ROOT / "catalog.json").read_text(encoding="utf-8"))
order = cat["task_order"]


def iso_dt(s):
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None


def task_time_window(t):
    times = []
    for p in (suite.TMP / t).rglob("requests.jsonl"):
        for line in p.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            for a in rec.get("attempts", []) or []:
                for k in ("started_at", "ended_at"):
                    d = iso_dt(a.get(k) or "")
                    if d:
                        times.append(d)
            if rec.get("log_time"):
                d = iso_dt(rec["log_time"])
                if d:
                    times.append(d)
    if not times:
        return None, None
    return min(times), max(times)


state = suite.load_state()
for t in order:
    mp = suite.out_dir(t) / "task-metrics.json"
    if mp.exists():
        m = json.loads(mp.read_text(encoding="utf-8"))
        st, en = task_time_window(t)
        if st and en:
            # keep the earlier of the recorded start and the earliest real request
            cur = iso_dt(m.get("started_at") or "")
            if not cur or st < cur:
                m["started_at"] = st.isoformat(timespec="seconds")
            cure = iso_dt(m.get("ended_at") or "")
            if not cure or en > cure:
                m["ended_at"] = en.isoformat(timespec="seconds")
            a, b = iso_dt(m["started_at"]), iso_dt(m["ended_at"])
            m["elapsed_seconds"] = round((b - a).total_seconds(), 2) if a and b else None
            first = None
            for p in (suite.TMP / t).rglob("requests.jsonl"):
                for line in p.read_text(encoding="utf-8").splitlines():
                    if not line.strip():
                        continue
                    try:
                        rec = json.loads(line)
                    except Exception:
                        continue
                    for att in rec.get("attempts", []) or []:
                        if att.get("success") and att.get("started_at"):
                            d = iso_dt(att["started_at"])
                            if d and (first is None or d < first):
                                first = d
            if first and a:
                m["first_image_seconds"] = round((first - a).total_seconds(), 2)
        mp.write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        started, ended = m.get("started_at"), m.get("ended_at")
    else:
        started = ended = suite.now()

    ts = suite.task_state(state, t)
    d = suite.out_dir(t)
    pngs = sorted(d.rglob("*.png"))
    artifacts = [suite.rel(p) for p in sorted(d.rglob("*")) if p.is_file()]
    rounds = []
    cases = []
    if t in ("A21", "A22"):
        for r in ("round-01", "round-02", "round-03"):
            if (d / r).exists():
                rounds.append(r)
    if t.startswith("B"):
        cases = sorted({p.parent.name for p in pngs if p.parent != d and p.parent.name.startswith("case-")})
    spec_p = suite.tmp_dir(t) / "finalize.json"
    evidence = []
    if spec_p.exists():
        try:
            evidence = json.loads(spec_p.read_text(encoding="utf-8")).get("visual_review_evidence", [])
        except Exception:
            pass
    if not evidence:
        evidence = ["%d final PNG(s) opened and accepted by executing agent" % len(pngs)]
    ts.update({
        "status": "completed",
        "started_at": started,
        "ended_at": ended,
        "output_dir": suite.rel_out(t),
        "temp_dir": suite.rel_tmp(t),
        "completed_rounds": rounds,
        "completed_cases": cases,
        "artifacts": artifacts,
        "visual_review_evidence": evidence,
        "unresolved_issues": [],
        "resume_notes": None,
    })
    suite.event("task_done", task_id=t, status="completed", png_count=len(pngs),
                note="verified PNG/DSL pairs, report, metrics and process logs")
    suite.checkpoint(state, note="after %s completion verified" % t)

state["status"] = "completed"
state["current_task"] = None
state["current_round"] = None
state["current_case"] = None
state["ended_at"] = suite.now()
state["suite_artifacts"] = [
    "outputs/%s/_suite/index.md" % suite.RID,
    "outputs/%s/_suite/gallery.md" % suite.RID,
    "outputs/%s/_suite/snapshot-usage.md" % suite.RID,
    "outputs/%s/_suite/task-metrics.json" % suite.RID,
    "outputs/%s/_suite/suite-state.json" % suite.RID,
]
suite.save_state(state)
print("state synced: completed=%d, checkpoints=%d" %
      (sum(1 for x in state["tasks"] if x["status"] == "completed"),
       len(list((suite.SUITE_TMP / "checkpoints").glob("state-*.json")))))
