from __future__ import annotations
import json
import sys
from pathlib import Path
BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import creativekit as ck
import suitekit as sk
TASK = "B06"
run = sk.init_suite()[0]
sk.begin_task(run, TASK)
source = BASE / "preparation.json"
target = BASE / "plan-v001.json"
assert source.is_file() and not target.exists()
prep = json.loads(source.read_text(encoding="utf-8"))
cases = []
for item in prep["cases"]:
    case = {k: item[k] for k in ("id", "title", "audience", "content_basis", "visual_intent", "dimensions", "dsl_capabilities")}
    case["use_context"] = item["context"]
    case["user_goal"] = item["goal"]
    case["criteria"] = [{"id": c["id"], "condition": c["observable_condition"], "method": c["inspection_method"],
                         "established_at": c["established_at"], "plan_version": "v001"} for c in item["pre_render_completion_criteria"]]
    case["criteria_history"] = []
    case["target_viewing"] = item["target_viewing"]
    case["independence_rationale"] = item["independence_rationale"]
    case["validation_question"] = item["validation_question"]
    case["plan_version"] = "v001"
    case["plan_established_at"] = prep["created_at"]
    case["version"] = "v001"
    cases.append(case)
plan = {"schema_version": 1, "task_id": TASK, "run_id": run, "path_base": "suite_root", "plan_version": "v001",
        "established_at": prep["created_at"], "execution_started_at": sk.iso(), "asset_policy": "pure_dsl_fictional_demonstrations",
        "evidence_policy": prep["evidence_policy"], "curatorial_statement": prep["curatorial_statement"],
        "collection_independence_review": prep["collection_independence_review"], "preparation_source": sk.rel(source), "cases": cases}
sk.write_json(target, plan)
ck.log_tool(TASK, "Python planning", "采用首次渲染前已保存的十题研究计划，补齐标准字段并开始执行；所有内容明确为虚构演示",
            [sk.rel(source)], [sk.rel(target)], [c["id"] for c in cases], "计划建立于2026-11-24T04:38:29Z，早于所有渲染；十题信息结构互不重复")
print(json.dumps({"plan": sk.rel(target), "cases": len(cases), "run": run}, ensure_ascii=False))
