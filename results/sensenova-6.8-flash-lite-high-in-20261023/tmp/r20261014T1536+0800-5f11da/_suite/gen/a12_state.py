"""A12 收口状态：suite-state.json 追加 A12、events.jsonl 追加 task_completed、打检查点。

用法：SNAPSHOT_RUN_ID=<rid> python -I tmp/<rid>/_suite/gen/a12_state.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(HERE.parent))
import suite as S  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

TASK = "A12"
RID = S.run_id()
OUT = S.task_dirs(TASK)[0]
TMP = S.task_dirs(TASK)[1]
SDIR, TSDIR = S.suite_dirs()
STATE = SDIR / "suite-state.json"

state = S.load_state()
metrics = json.loads((OUT / "task-metrics.json").read_text(encoding="utf-8"))
cm = json.loads((OUT / "content-map.json").read_text(encoding="utf-8"))

artifacts = sorted(p.name for p in OUT.iterdir() if p.is_file())
evidence = [
    {"check": c["id"], "report": "outputs/" + RID + "/A12/content-map.json",
     "verdict": "1/1"} for c in cm["checks"] if c["passed"]]

entry = {
    "id": TASK, "status": "completed",
    "started_at": metrics["timings"]["started_at"],
    "ended_at": S.now_iso(),
    "elapsed_seconds": metrics["timings"]["elapsed_seconds"],
    "output_dir": S.rel(OUT), "temp_dir": S.rel(TMP),
    "artifacts": [S.rel(OUT / n) for n in artifacts],
    "metrics": S.rel(OUT / "task-metrics.json"),
    "requests": metrics["counts"]["snapshot_requests"],
    "successful_requests": metrics["counts"]["successful_snapshot_requests"],
    "failed_requests": metrics["counts"]["failed_snapshot_requests"],
    "retry_requests": metrics["counts"]["retry_requests"],
    "image_views": metrics["counts"]["image_views"],
    "visual_iterations": metrics["counts"]["iterations_total"],
    "issues_found": len(metrics.get("issues", [])),
    "requirement_checks": metrics["requirement_checks"]["summary"],
    "canvases": [
        {"id": c["id"], "size_px": [c["width"], c["height"]],
         "margin": c["margin"],
         "entries": len([e for e in cm["entries"] if e["canvas"] == c["id"]])}
        for c in cm["canvases"]],
    "verification": {
        "script": "tmp/" + RID + "/_suite/gen/a12_verify.py",
        "report": "tmp/" + RID + "/A12/gen/a12_verify.json",
        "entries_measured": metrics["counts"]["verification_measured_entries"],
        "failures": metrics["counts"]["verification_failures"],
        "warnings": metrics["counts"]["verification_warnings"],
        "ratio_groups_checked": metrics["counts"]["ratio_groups_checked"],
        "ratio_groups_failed": metrics["counts"]["ratio_groups_failed"]},
    "defects_found_and_fixed": metrics["counts"]["real_defects_found_and_fixed"],
    "visual_review_evidence": evidence,
    "unresolved_issues": metrics.get("unresolved_issues", []),
    "recorded_at": S.now_iso()}

det = [t for t in state["tasks_detail"] if t.get("id") != TASK] + [entry]
state["tasks_detail"] = det
state["completed"] = state.get("completed") or []
if TASK not in state["completed"]:
    state["completed"].append(TASK)
comp = set(state["completed"])
state["remaining"] = [t for t in state.get("remaining", []) if t not in comp]
state["current_task"] = sorted(state["remaining"])[0] if state["remaining"] else None
state["counts_by_status"] = {"completed": len(comp), "in_progress": 0,
                             "pending": len(state["remaining"])}
assert len(comp) + len(state["remaining"]) == int(state["total_tasks"]), (
    len(comp), len(state["remaining"]))
state["updated_at"] = S.now_iso()
state["status"] = "completed" if not state["remaining"] else "in_progress"
S.save_state(state)

ev_before = sum(1 for l in (TSDIR / "events.jsonl").read_text(
    encoding="utf-8", errors="replace").splitlines() if l.strip())
S.append_event({
    "ts": S.now_iso(), "event": "task_completed", "task_id": TASK,
    "status": "completed",
    "requirement_checks": metrics["requirement_checks"]["summary"],
    "requests": metrics["counts"]["snapshot_requests"],
    "image_views": metrics["counts"]["image_views"],
    "visual_iterations": metrics["counts"]["iterations_total"],
    "verification_failures": metrics["counts"]["verification_failures"],
    "defects_found_and_fixed": metrics["counts"]["real_defects_found_and_fixed"],
    "next_task": state["current_task"],
    "output_dir": S.rel(OUT)})
ck = S.snapshot_checkpoint(state)
state["last_checkpoint"] = ck
S.save_state(state)

print(f"artifacts: {artifacts}")
print(f"checks evidence: {len(evidence)} 条")
print(f"counts_by_status: {json.dumps(state['counts_by_status'], ensure_ascii=False)}")
print(f"current_task: {state['current_task']}  status: {state['status']}")
print(f"events: {ev_before} -> {ev_before + 1}")
print(f"checkpoint: {ck}")
