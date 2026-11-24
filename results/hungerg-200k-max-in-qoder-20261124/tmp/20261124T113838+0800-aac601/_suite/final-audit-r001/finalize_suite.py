from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
RUN_ID = "20261124T113838+0800-aac601"
SUITE_OUT = ROOT / "outputs" / RUN_ID / "_suite"
SUITE_TEMP = ROOT / "tmp" / RUN_ID / "_suite"
sys.path.insert(0, str(ROOT / "tools"))
import suite_audit
import suitekit as sk

state_path = SUITE_OUT / "suite-state.json"
state = json.loads(state_path.read_text(encoding="utf-8"))
assert len(state["tasks"]) == 30
assert all(entry["status"] == "completed" for entry in state["tasks"])
assert all(not entry.get("unresolved_issues") for entry in state["tasks"])

state["suite_artifacts"] = list(sk.CONFIG["suite_required_artifacts"])
state["final_review_evidence"] = [
    f"tmp/{RUN_ID}/_suite/final-audit-r001/all-final-view-audit-r002.json",
    f"tmp/{RUN_ID}/_suite/final-audit-r001/overview-review-manifest-v002.json",
    f"outputs/{RUN_ID}/A22/round-02/change-audit-r002-corrected.json",
    f"outputs/{RUN_ID}/A22/final-review-r002.json",
    f"tmp/{RUN_ID}/_suite/final-audit-r001/final-inventory-r001.json",
]
state["updated_at"] = sk.iso()
sk.write_json(state_path, state)
sk.append_jsonl(SUITE_TEMP / "events.jsonl", {
    "event_id": f"{RUN_ID}-suite-finalization-precheck-r001",
    "at": sk.iso(),
    "event": "suite-finalization-precheck-r001",
    "status": "completed",
    "artifacts": state["final_review_evidence"],
    "note": "30题状态与未解决事项已核对，注册全套必需产物并保留最终查看/复算证据。",
})
sk.checkpoint(RUN_ID, "suite-finalization-precheck-r001")

precheck = suite_audit.generate()
precheck_path = BASE / "pre-completion-audit-r001.json"
shutil.copyfile(SUITE_OUT / "audit-report.json", precheck_path)
allowed_status_issues = {
    "全部任务已完成但 suite-state.status 不是 completed",
    "全部任务已完成但缺少 ended_at",
}
remaining = [issue["issue"] for issue in precheck["issues"]]
if set(remaining) - allowed_status_issues:
    raise RuntimeError(json.dumps({"blocking_issues": precheck["issues"]}, ensure_ascii=False))
if not all(value for key, value in precheck["completion_gates"].items() if key != "no_unresolved_audit_issues"):
    raise RuntimeError("终审门禁存在未通过项")

state = json.loads(state_path.read_text(encoding="utf-8"))
state["status"] = "completed"
state["current_task"] = None
state["current_round"] = None
state["current_case"] = None
state["ended_at"] = sk.iso()
state["updated_at"] = state["ended_at"]
state["stop_reason"] = "all_selected_tasks_and_final_audit_completed"
sk.write_json(state_path, state)
sk.checkpoint(RUN_ID, "suite-completed-r001")

final = suite_audit.generate()
if not final["completion_ready"] or final["issue_count"]:
    raise RuntimeError(json.dumps({"final_gates": final["completion_gates"], "issues": final["issues"]}, ensure_ascii=False))

sk.append_jsonl(SUITE_TEMP / "events.jsonl", {
    "event_id": f"{RUN_ID}-suite-completed-r001",
    "at": sk.iso(),
    "event": "suite-completed-r001",
    "status": "completed",
    "artifacts": [f"outputs/{RUN_ID}/_suite/{name}" for name in sk.CONFIG["suite_required_artifacts"]],
    "note": "全部30题、124张最终PNG、60个B类独立用例、A21/A22各三轮及全套终审通过；原始日志与历史版本未改。",
})
sk.checkpoint(RUN_ID, "suite-completed-final-audit-r001")
summary = {
    "run_id": RUN_ID,
    "path_base": "suite_root",
    "started_at": state["started_at"],
    "ended_at": state["ended_at"],
    "tasks_completed": 30,
    "final_pngs": len(final["inventory"]),
    "creative_cases": 60,
    "completion_gates": final["completion_gates"],
    "precheck_artifact": sk.rel(precheck_path),
    "suite_artifacts": [f"outputs/{RUN_ID}/_suite/{name}" for name in sk.CONFIG["suite_required_artifacts"]],
}
sk.write_json(BASE / "suite-finalization-r001.json", summary)
print(json.dumps(summary, ensure_ascii=False))
