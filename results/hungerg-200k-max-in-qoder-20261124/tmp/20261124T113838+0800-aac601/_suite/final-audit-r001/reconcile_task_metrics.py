from __future__ import annotations

import hashlib
import json
import re
import shutil
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import suitekit as sk

RUN, SUITE_OUT, SUITE_TEMP = sk.init_suite()
RUN_OUT = SUITE_OUT.parent
RUN_TEMP = SUITE_TEMP.parent
TASK_IDS = [f"A{i:02d}" for i in range(1, 25)] + [f"B{i:02d}" for i in range(1, 7)]
backup_dir = BASE / "task-metrics-backups-r001"
backup_dir.mkdir(parents=True, exist_ok=True)
view_audit = json.loads((BASE / "all-final-view-audit-r002.json").read_text(encoding="utf-8"))
view_metrics = json.loads((BASE / "view-metrics-reconciliation-r001.json").read_text(encoding="utf-8"))
view_by_task = {row["task_id"]: row for row in view_metrics["tasks"]}
chronology = json.loads((BASE / "view-chronology-r002.json").read_text(encoding="utf-8"))
inventory = json.loads((BASE / "final-inventory-r001.json").read_text(encoding="utf-8"))
final_paths = {item["png"] for item in inventory["items"]}
b03_corrections = {
    row["original_image_path"]: row["corrected_image_path"]
    for row in json.loads((RUN_TEMP / "B03" / "inspection" / "iteration-path-corrections-r001.json").read_text(encoding="utf-8"))["corrections"]
}


def digest(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone()


render_by_hash = defaultdict(list)
for task_id in TASK_IDS:
    for row in sk.read_jsonl(RUN_TEMP / task_id / "requests.jsonl"):
        if row.get("request_type") == "render" and row.get("http_status") == 200 and row.get("ended_at"):
            response_hash = digest(ROOT / row["response_file"])
            if response_hash:
                render_by_hash[response_hash].append(utc(row["ended_at"]))

valid_read_hashes = set()
for event in view_audit["events"]:
    if event["is_error"] or not event["result_at"] or not event["sha256"]:
        continue
    if any(utc(event["result_at"]) >= ended for ended in render_by_hash.get(event["sha256"], [])):
        valid_read_hashes.add(event["sha256"])

summaries = []
for task_id in TASK_IDS:
    metric_path = RUN_OUT / task_id / "task-metrics.json"
    backup_path = backup_dir / f"{task_id}-task-metrics-before-reconciliation.json"
    if not backup_path.exists():
        shutil.copyfile(metric_path, backup_path)
    metrics = json.loads(metric_path.read_text(encoding="utf-8"))
    previous = {key: metrics.get(key) for key in ("image_views", "completed_visual_iterations", "incomplete_visual_iterations", "unviewed_baselines", "final_visual_rechecks")}
    iterations = sk.read_jsonl(RUN_TEMP / task_id / "iterations.jsonl")
    records = []
    for row in iterations:
        image_path = b03_corrections.get(row.get("image_path", ""), row.get("image_path", ""))
        if not str(image_path).lower().endswith(".png"):
            continue
        image_hash = digest(ROOT / image_path)
        case_id = row.get("case_id")
        if not case_id:
            match = re.search(r"(B0[1-6]-case-\d+|case-\d+)", image_path)
            case_id = match.group(1) if match else "task-level"
        records.append({
            "row": row,
            "image_path": image_path,
            "image_hash": image_hash,
            "case_id": case_id,
            "viewed": image_hash in valid_read_hashes,
        })

    def distinct(selected):
        seen = set()
        result = []
        for record in selected:
            row = record["row"]
            key = (record["case_id"], row.get("version_id"), record["image_hash"], row.get("type"))
            if key not in seen:
                seen.add(key)
                result.append(record)
        return result

    completed = distinct([record for record in records if record["viewed"] and record["row"].get("type") in ("visual", "requirement-change") and record["row"].get("completed_visual_iteration")])
    incomplete = distinct([record for record in records if record["viewed"] and record["row"].get("type") in ("baseline", "visual", "requirement-change") and not record["row"].get("completed_visual_iteration")])
    def baseline_accepted(record):
        text = str(record["row"].get("observable_issues", ""))
        return record["row"].get("completed_visual_iteration") and any(marker in text for marker in ("无影响", "无视觉", "通过", "正常", "完整", "清晰"))

    baselines = distinct([record for record in records if record["viewed"] and record["row"].get("type") == "baseline" and baseline_accepted(record)])
    alternatives = distinct([record for record in records if record["viewed"] and record["row"].get("type") == "alternative" and record["row"].get("completed_visual_iteration")])
    baseline_hashes = {record["image_hash"] for record in records if record["row"].get("type") == "baseline"}
    unviewed_baselines = sum(image_hash not in valid_read_hashes for image_hash in baseline_hashes)
    final_recheck_paths = {
        record["image_path"] for record in records
        if record["viewed"] and record["row"].get("type") == "audit_visual_recheck" and record["image_path"] in final_paths
    }
    vm = view_by_task[task_id]
    metrics["image_views"] = vm["unique_service_image_opens"]
    metrics["completed_visual_iterations"] = len(completed)
    metrics["incomplete_visual_iterations"] = len(incomplete)
    metrics["unviewed_baselines"] = unviewed_baselines
    metrics["alternative_visual_iterations"] = len(alternatives)
    metrics["final_visual_rechecks"] = len(final_recheck_paths)
    metrics["baseline_acceptances"] = len(baselines)
    metrics["actual_service_read_events"] = vm["actual_service_read_events"]
    metrics["repeat_service_read_events"] = vm["repeat_service_read_events"]
    metrics["inspection_derivative_views"] = vm["derivative_read_events"]
    metrics["placeholder_iteration_rows_excluded"] = vm["placeholder_iteration_rows_excluded"]
    metrics["view_counting_note"] = "image_views 为真实 Read 打开的不同服务 PNG 路径数；重复打开、检查衍生图和占位行分列。completed_visual_iterations 仅计有新图真实查看的 visual/requirement-change 完成记录，不等于基线通过。"
    metrics["metrics_reconciliation"] = {
        "reconciled_at": sk.iso(),
        "source": [sk.rel(BASE / "all-final-view-audit-r002.json"), sk.rel(BASE / "view-metrics-reconciliation-r001.json")],
        "previous_values": previous,
        "raw_logs_modified": False,
        "ordering_verification": "complete_for_B01_B02_remediations" if task_id in ("B01", "B02") else "new_view_verified; historical_order_not_fully_verified",
        "note": "最终124张服务原图查看已由会话工具记录逐件核验；历史补记行不单独当作新打开事件。",
    }
    if task_id in ("B01", "B02"):
        metrics["ordered_remediation_checks"] = [item for item in chronology["remediation_sequence_checks"] if item["task_id"] == task_id]
    if "counts" in metrics:
        for key in ("image_views", "completed_visual_iterations", "incomplete_visual_iterations", "unviewed_baselines", "final_visual_rechecks"):
            if key in metrics["counts"]:
                metrics["counts"][key] = metrics[key]
        metrics["counts"]["baseline_acceptances"] = len(baselines)
        metrics["counts"]["actual_service_read_events"] = vm["actual_service_read_events"]
        metrics["counts"]["inspection_derivative_views"] = vm["derivative_read_events"]
    if "case_metrics" in metrics:
        for case in metrics["case_metrics"]:
            case_id = case["case_id"]
            case_records = [record for record in records if record["case_id"] == case_id or record["case_id"].endswith(case_id)]
            case["image_views"] = len(set(record["image_path"] for record in case_records if record["viewed"]))
            case["completed_visual_iterations"] = len(distinct([record for record in case_records if record["viewed"] and record["row"].get("type") in ("visual", "requirement-change") and record["row"].get("completed_visual_iteration")]))
            case["incomplete_visual_iterations"] = len(distinct([record for record in case_records if record["viewed"] and record["row"].get("type") in ("baseline", "visual", "requirement-change") and not record["row"].get("completed_visual_iteration")]))
    if task_id == "B03":
        metrics["probe_metrics"] = {
            "snapshot_requests": 5,
            "request_elapsed_seconds_sum": 13.673,
            "note": "任务顶层含5次能力/约束探针请求；case_metrics仅统计十个正式用例，差值不是漏记。",
        }
        metrics["iteration_path_correction"] = sk.rel(RUN_TEMP / "B03" / "inspection" / "iteration-path-corrections-r001.json")
    if task_id == "B05":
        metrics["external_research_metrics"] = {
            "requests": 2,
            "elapsed_seconds": 11.141,
            "note": "task request_elapsed_seconds_sum 含两次外部研究请求；case_metrics仅含Snapshot渲染。",
        }
    if task_id == "B04":
        metrics["research_timing_note"] = "来源访问准备早于本题执行开始；不把准备时间计入任务墙钟，不把直接失败研究请求计入Snapshot/shared服务请求。S15硬编码时间已标为不可验证。"
    sk.write_json(metric_path, metrics)
    summaries.append({
        "task_id": task_id,
        "previous": previous,
        "reconciled": {key: metrics[key] for key in ("image_views", "completed_visual_iterations", "incomplete_visual_iterations", "unviewed_baselines", "final_visual_rechecks", "baseline_acceptances", "actual_service_read_events", "inspection_derivative_views")},
    })

sk.append_jsonl(SUITE_TEMP / "events.jsonl", {
    "event_id": f"{RUN}-suite-metrics-reconciliation-r001",
    "at": sk.iso(),
    "event": "suite-metrics-reconciliation-r001",
    "status": "completed",
    "artifacts": [sk.rel(BASE / "view-metrics-reconciliation-r001.json"), sk.rel(backup_dir)],
    "note": "30题指标已按真实Read证据统一口径；原始请求/迭代日志未改，旧指标逐题备份。",
})
sk.checkpoint(RUN, "suite-metrics-reconciliation-r001")
sk.write_json(BASE / "task-metrics-reconciliation-summary-r001.json", {"run_id": RUN, "path_base": "suite_root", "tasks": summaries})
print(json.dumps({"tasks": len(summaries), "image_views": sum(row["reconciled"]["image_views"] for row in summaries), "completed_visual_iterations": sum(row["reconciled"]["completed_visual_iterations"] for row in summaries), "incomplete_visual_iterations": sum(row["reconciled"]["incomplete_visual_iterations"] for row in summaries)}, ensure_ascii=False))
