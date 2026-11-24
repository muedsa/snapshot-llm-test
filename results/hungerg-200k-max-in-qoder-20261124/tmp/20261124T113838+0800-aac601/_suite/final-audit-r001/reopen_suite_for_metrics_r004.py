from __future__ import annotations
import json
import sys
from pathlib import Path
BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import suitekit as sk
RUN, OUT, TEMP = sk.init_suite()
path = OUT / "suite-state.json"
state = json.loads(path.read_text(encoding="utf-8"))
prior = {
    "status": state.get("status"),
    "ended_at": state.get("ended_at"),
    "stop_reason": state.get("stop_reason"),
    "artifact": sk.rel(BASE / "suite-finalization-r001.json"),
}
assert prior["status"] == "completed"
state["status"] = "in_progress"
state["ended_at"] = None
state["stop_reason"] = None
state["current_task"] = None
state["current_round"] = None
state["current_case"] = None
state["superseded_completion_records"] = [*state.get("superseded_completion_records", []), {
    "reopened_at": sk.iso(), "reason": "独立指标复核发现预置需求变更混入视觉迭代、B04覆盖来源未按内容还原、请求类别与计时标签不准确；保留旧终审不覆盖。",
    "prior": prior,
}]
state["updated_at"] = sk.iso()
sk.write_json(path, state)
sk.append_jsonl(TEMP / "events.jsonl", {
    "event_id": f"{RUN}-suite-reopened-for-metrics-r004", "at": sk.iso(),
    "event": "suite-reopened-for-metrics-r004", "status": "in_progress",
    "reason": state["superseded_completion_records"][-1]["reason"],
})
sk.checkpoint(RUN, "suite-reopened-for-metrics-r004")
print(json.dumps({"status": state["status"], "prior_completion_preserved": prior}, ensure_ascii=False))
