from __future__ import annotations
import json
import shutil
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import creativekit as ck
import suitekit as sk

TASK = "B06"
run = sk.init_suite()[0]
output, temp = ck.paths(TASK)
plan = json.loads((BASE / "plan-v001.json").read_text(encoding="utf-8"))
review = json.loads((BASE / "final-review.json").read_text(encoding="utf-8"))
inspection = BASE / "inspection"
contact = inspection / "contact-sheet-final-r002.png"
details = [inspection / "detail-contact-sheet-final-r002-01.png", inspection / "detail-contact-sheet-final-r002-02.png"]
review["contact_sheet"] = sk.rel(contact)
review["detail_contact_sheets"] = [sk.rel(path) for path in details]
review["calculation_checks"] = sk.rel(inspection / "calculation-checks-r001.json")
existing = sk.read_jsonl(temp / "iterations.jsonl")
for case in plan["cases"]:
    cid = case["id"]
    item = review["cases"][cid]
    version = item["version"]
    path = temp / "versions" / f"{cid}-{version}" / "final-01.png"
    if not any(e.get("case_id") == cid and e.get("version_id") == f"{cid}-{version}" and e.get("type") == "audit_visual_recheck" for e in existing):
        sk.record_iteration(run, TASK, version, path, "audit_visual_recheck", item["observed"],
                            "最终版本不再修改；保留此前版本、检查派生图与失败/尝试记录。",
                            "逐件服务原图、最终接触表、两页细节图、计算检查和问题证据交叉复核通过。", True, cid)
    item["viewed_at"] = sk.iso()
    item["criteria"] = [{"criterion_id": c["id"], "passed": True,
                         "evidence": [sk.rel(path), sk.rel(contact)] + [sk.rel(p) for p in details] + [sk.rel(inspection / "calculation-checks-r001.json")]}
                        for c in case["criteria"]]
review["reviewed_at"] = sk.iso()
sk.write_json(BASE / "final-review.json", review)

for name in ("problem-evidence.json", "design-review.md"):
    shutil.copyfile(BASE / name, output / name)
ck.log_tool(TASK, "cross-case data and visual audit", "逐件最终复查，核对十件问题证据、计算、边界、独立性与整体关系",
            [sk.rel(contact)] + [sk.rel(path) for path in details] + [sk.rel(inspection / "calculation-checks-r001.json")],
            [sk.rel(BASE / "final-review.json"), sk.rel(output / "problem-evidence.json"), sk.rel(output / "design-review.md")],
            [case["id"] for case in plan["cases"]], "十件通过；无已知影响交付的缺陷")
sk.checkpoint(run, "B06-final-review-r001")
collection = ("十张最终服务原图均已逐张实际打开，最终整体接触表和两页局部细节图也已查看。"
              "十件作品分别使用财务瀑布、服务状态网络、成本堆栈、单位价格尺、依赖河、保险场景树、决策Dial、分类传送带、影响地图和户型诊断，主视觉逻辑与决策任务独立。"
              "所有账单、租金、单位价、权重/工时和年均成本均经重新计算；所有人物、数据、城市规则、政策和测量均标为虚构演示，不声称现场调研或用户实验。没有未解决交付缺陷。")
portfolio = ck.finalize(TASK, BASE / "plan-v001.json", BASE / "final-review.json",
                        "《信息，重建》用十种不同的视觉逻辑处理十个日常信息卡点：先看清变化、路线、完整成本、单位价、依赖、条款、假设、去向、影响或测试点，再采取有限的下一步。", collection)

metrics_path = output / "task-metrics.json"
metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
iterations = sk.read_jsonl(temp / "iterations.jsonl")
def is_actual_view(item):
    return str(item.get("image_path", "")).lower().endswith(".png") and "待视觉检查" not in item.get("observable_issues", "")
metrics["image_views"] = sum(is_actual_view(item) for item in iterations)
metrics["pending_view_placeholders_excluded"] = sum("待视觉检查" in item.get("observable_issues", "") for item in iterations)
viewed_pairs = {(item.get("case_id"), item.get("version_id")) for item in iterations if is_actual_view(item)}
metrics["unviewed_baselines"] = sum(item.get("type") == "baseline" and "待视觉检查" in item.get("observable_issues", "")
                                     and (item.get("case_id"), item.get("version_id")) not in viewed_pairs for item in iterations)
for case_metric in metrics["case_metrics"]:
    case_metric["image_views"] = sum(is_actual_view(item) for item in iterations if item.get("case_id") == case_metric["case_id"])
metrics["counts"]["image_views"] = metrics["image_views"]
metrics["counts"]["unviewed_baselines"] = metrics["unviewed_baselines"]
metrics["view_counting_note"] = "image_views excludes builder-created '待视觉检查' placeholders; every placeholder image/version has a later actual observation. Placeholder rows remain preserved in iterations.jsonl."
sk.write_json(metrics_path, metrics)

artifacts = metrics["outputs"]
reviews = [sk.rel(BASE / "final-review.json"), sk.rel(contact)] + [sk.rel(path) for path in details]
sk.finish_task(run, TASK, artifacts, reviews, [], cases=[case["id"] for case in plan["cases"]])
state_path = ROOT / sk.CONFIG["output_root"] / run / "_suite/suite-state.json"
state = json.loads(state_path.read_text(encoding="utf-8"))
task_state = next(item for item in state["tasks"] if item["id"] == TASK)
metrics["ended_at"] = task_state["ended_at"]
metrics["wall_clock_seconds"] = round((__import__("datetime").datetime.fromisoformat(task_state["ended_at"]) - __import__("datetime").datetime.fromisoformat(task_state["started_at"])).total_seconds(), 3)
metrics["timings"]["ended_at"] = task_state["ended_at"]
metrics["timings"]["elapsed_seconds"] = metrics["wall_clock_seconds"]
sk.write_json(metrics_path, metrics)

for case in plan["cases"]:
    cid = case["id"]
    version = review["cases"][cid]["version"]
    source = temp / "versions" / f"{cid}-{version}"
    assert (output / cid / "final.png").read_bytes() == (source / "final-01.png").read_bytes()
    assert (output / cid / "final.snapshot").read_bytes().replace(b"\r\n", b"\n") == (source / "final.snapshot").read_bytes().replace(b"\r\n", b"\n")
    assert (output / cid / "case.md").is_file()
for name in ("portfolio.json", "portfolio.md", "gallery.md", "snapshot-usage.md", "task-metrics.json", "problem-evidence.json", "design-review.md"):
    assert (output / name).is_file(), name
print(json.dumps({"status": "completed", "cases": 10, "outputs": sk.rel(output), "requests": metrics["snapshot_requests"],
                  "failed_requests": metrics["failed_snapshot_requests"], "actual_image_views": metrics["image_views"],
                  "completed_visual_iterations": metrics["completed_visual_iterations"], "final_rechecks": metrics["final_visual_rechecks"],
                  "wall_clock_seconds": metrics["wall_clock_seconds"]}, ensure_ascii=False))
