from __future__ import annotations
import json
import shutil
import subprocess
import sys
from pathlib import Path
BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import suite_audit
import suitekit as sk
RUN, SUITE_OUT, SUITE_TEMP = sk.init_suite()
state_path = SUITE_OUT / "suite-state.json"
state = json.loads(state_path.read_text(encoding="utf-8"))
assert state["status"] == "in_progress" and state.get("superseded_completion_records")
assert len(state["tasks"]) == 30 and all(x["status"] == "completed" and not x.get("unresolved_issues") for x in state["tasks"])
independent_script = BASE / "independent_delivery_audit_r005.py"
suite_audit.generate()
subprocess.run([sys.executable, str(independent_script)], cwd=ROOT, check=True)
independent = json.loads((BASE / "independent-delivery-audit-r005.json").read_text(encoding="utf-8"))
assert independent["passed"] and independent["independent_of_suite_audit"]
state["suite_artifacts"] = list(sk.CONFIG["suite_required_artifacts"])
state["final_review_evidence"] = list(dict.fromkeys([
    *state.get("final_review_evidence", []),
    sk.rel(BASE / "task-metrics-reconciliation-summary-r005.json"),
    sk.rel(BASE / "independent-delivery-audit-r005.json"),
    sk.rel(BASE / "baseline-classification-r005.json"),
    f"outputs/{RUN}/B05/research-ledger-r002-corrected.json",
]))
state["updated_at"] = sk.iso()
sk.write_json(state_path, state)
sk.append_jsonl(SUITE_TEMP / "events.jsonl", {
    "event_id": f"{RUN}-suite-finalization-precheck-r003", "at": sk.iso(),
    "event": "suite-finalization-precheck-r003", "status": "completed",
    "artifacts": state["final_review_evidence"],
    "note": "r005指标语义、逐行基线分类与独立交付审计通过后重新终审；r001完成记录与未执行的r002脚本作为历史保留。",
})
sk.checkpoint(RUN, "suite-finalization-precheck-r003")
precheck = suite_audit.generate()
shutil.copyfile(SUITE_OUT / "audit-report.json", BASE / "pre-completion-audit-r003.json")
allowed = {"全部任务已完成但 suite-state.status 不是 completed", "全部任务已完成但缺少 ended_at"}
remaining = [x["issue"] for x in precheck["issues"]]
if set(remaining) - allowed:
    raise RuntimeError(json.dumps(precheck["issues"], ensure_ascii=False))
if not all(value for key, value in precheck["completion_gates"].items() if key != "no_unresolved_audit_issues"):
    raise RuntimeError("终审门禁存在未通过项")
state = json.loads(state_path.read_text(encoding="utf-8"))
state["status"] = "completed"
state["current_task"] = state["current_round"] = state["current_case"] = None
state["ended_at"] = sk.iso()
state["updated_at"] = state["ended_at"]
state["stop_reason"] = "all_selected_tasks_and_final_audit_completed"
sk.write_json(state_path, state)
sk.checkpoint(RUN, "suite-completed-r003")
final = suite_audit.generate()
if not final["completion_ready"] or final["issue_count"]:
    raise RuntimeError(json.dumps({"gates": final["completion_gates"], "issues": final["issues"]}, ensure_ascii=False))
subprocess.run([sys.executable, str(independent_script)], cwd=ROOT, check=True)
independent = json.loads((BASE / "independent-delivery-audit-r005.json").read_text(encoding="utf-8"))
assert independent["passed"]
sk.append_jsonl(SUITE_TEMP / "events.jsonl", {
    "event_id": f"{RUN}-suite-completed-r003", "at": sk.iso(),
    "event": "suite-completed-r003", "status": "completed",
    "artifacts": [f"outputs/{RUN}/_suite/{name}" for name in sk.CONFIG["suite_required_artifacts"]],
    "note": "30题、124张最终PNG、60个B类独立用例、A21/A22各三轮、r005指标、逐行基线分类与独立交付审计全部通过。",
})
sk.checkpoint(RUN, "suite-completed-final-audit-r003")
summary = {
    "run_id": RUN, "path_base": "suite_root", "revision": "r003",
    "supersedes": sk.rel(BASE / "suite-finalization-r001.json"),
    "started_at": state["started_at"], "ended_at": state["ended_at"],
    "tasks_completed": 30, "final_pngs": 124, "creative_cases": 60,
    "completion_gates": final["completion_gates"],
    "independent_audit": sk.rel(BASE / "independent-delivery-audit-r005.json"),
    "baseline_classification": sk.rel(BASE / "baseline-classification-r005.json"),
    "precheck_artifact": sk.rel(BASE / "pre-completion-audit-r003.json"),
    "suite_artifacts": [f"outputs/{RUN}/_suite/{name}" for name in sk.CONFIG["suite_required_artifacts"]],
}
sk.write_json(BASE / "suite-finalization-r003.json", summary)
print(json.dumps(summary, ensure_ascii=False))
