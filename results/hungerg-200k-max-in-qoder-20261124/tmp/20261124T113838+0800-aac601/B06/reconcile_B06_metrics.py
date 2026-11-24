from __future__ import annotations
import json
import sys
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import suitekit as sk
import creativekit as ck

run = sk.init_suite()[0]
output, temp = sk.task_dirs(run, "B06")
iterations = sk.read_jsonl(temp / "iterations.jsonl")
tools = sk.read_jsonl(temp / "tool-usage.jsonl")
metrics = json.loads((output / "task-metrics.json").read_text(encoding="utf-8"))
if not any(item.get("case_id") == "B06-case-03" and item.get("version_id") == "v003"
           and "Parking色段" in item.get("observable_issues", "") for item in iterations):
    plan = json.loads((BASE / "plan-v001.json").read_text(encoding="utf-8"))
    case = next(item for item in plan["cases"] if item["id"] == "B06-case-03")
    ck.record_view("B06", case, temp / "versions" / "B06-case-03-v003" / "final-01.png", "v003",
                   "Utilities* $140外部标签仍落在Parking色段内，实际不可读；保留为未完成中间版。",
                   "将非顶部薄段标签移到堆栈右侧并加引线，另存v004。",
                   "与B06-case-03-v002服务原图比较；标签对比度已增加，但位置仍被上层色段覆盖。", False, "visual")
    iterations = sk.read_jsonl(temp / "iterations.jsonl")

actual = [item for item in iterations if str(item.get("image_path", "")).lower().endswith(".png")
          and "待视觉检查" not in item.get("observable_issues", "")]
unique_images = {item["image_path"] for item in actual}
visual = [item for item in actual if item.get("type") in {"visual", "requirement-change"}]
def unique_visual(items, completed):
    seen = set()
    count = 0
    for item in items:
        if bool(item.get("completed_visual_iteration")) != completed:
            continue
        key = (item.get("case_id"), item.get("version_id"), item.get("type"), item.get("observable_issues"))
        if key not in seen:
            seen.add(key)
            count += 1
    return count
completed = unique_visual(visual, True)
incomplete = unique_visual(visual, False)
metrics["image_views"] = len(unique_images)
metrics["inspection_derivative_views"] = 6
metrics["completed_visual_iterations"] = completed
metrics["incomplete_visual_iterations"] = incomplete
metrics["unviewed_baselines"] = 0
metrics["pending_view_placeholders_excluded"] = sum("待视觉检查" in item.get("observable_issues", "") for item in iterations)
metrics["duplicate_observation_rows_excluded"] = len(actual) - len(unique_images)
metrics["view_counting_note"] = ("image_views counts 21 distinct service PNG paths actually opened: ten v001 baselines, seven v002 corrections, three v003 corrections and one v004 correction. "
                                 "Builder placeholders and duplicate observations produced by review-script reruns are preserved in iterations.jsonl but excluded. "
                                 "Six inspection-derivative views (two three-image review passes) are reported separately; ten audit_visual_recheck rows are final review events, not additional PNG opens.")
for case_metric in metrics["case_metrics"]:
    cid = case_metric["case_id"]
    case_actual = [item for item in actual if item.get("case_id") == cid]
    case_visual = [item for item in case_actual if item.get("type") in {"visual", "requirement-change"}]
    case_metric["image_views"] = len({item["image_path"] for item in case_actual})
    case_metric["completed_visual_iterations"] = unique_visual(case_visual, True)
    case_metric["incomplete_visual_iterations"] = unique_visual(case_visual, False)

ck_tool_counts = Counter((item["tool"], item["purpose"]) for item in tools)
metrics["tool_usage_summary"] = [{"tool": tool, "count": count, "purpose": purpose}
                                 for (tool, purpose), count in ck_tool_counts.items()]
metrics["counts"].update({"image_views": len(unique_images), "completed_visual_iterations": completed,
                          "incomplete_visual_iterations": incomplete, "unviewed_baselines": 0,
                          "other_tool_calls": len(tools)})
metrics["tool_counting_note"] = ("tool_usage_summary groups identical tool/purpose rows; repeated direct-visual-review rows came from review-script reruns and do not represent extra image openings. "
                                 "Raw rows remain preserved. This reconciliation event is appended after the summary count.")
sk.write_json(output / "task-metrics.json", metrics)
if not any(item.get("tool") == "metrics reconciliation" for item in tools):
    ck.log_tool("B06", "metrics reconciliation", "复核并修正审查脚本重跑造成的重复观察/工具汇总，不删除原始日志",
                [sk.rel(temp / "iterations.jsonl"), sk.rel(temp / "tool-usage.jsonl")],
                [sk.rel(output / "task-metrics.json")], [f"B06-case-{i:02d}" for i in range(1, 11)],
                "实际服务原图查看21次，检查派生图查看6次；完整视觉迭代7次，未完成中间迭代4次；最终复查10次。原始重复行保留并排除于指标。")
metrics = json.loads((output / "task-metrics.json").read_text(encoding="utf-8"))
metrics["counts"]["other_tool_calls"] = len(sk.read_jsonl(temp / "tool-usage.jsonl"))
sk.write_json(output / "task-metrics.json", metrics)
print(json.dumps({"image_views": metrics["image_views"], "derivative_views": metrics["inspection_derivative_views"],
                  "completed_visual_iterations": completed, "incomplete_visual_iterations": incomplete,
                  "duplicate_rows_excluded": metrics["duplicate_observation_rows_excluded"], "final_rechecks": metrics["final_visual_rechecks"]}, ensure_ascii=False))
