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
backup_dir = BASE / "task-metrics-backups-r004"
backup_dir.mkdir(parents=True, exist_ok=True)
attempt = len(list(BASE.glob("task-metrics-reconciliation-summary-r004-attempt-*.json"))) + 3
view_audit = json.loads((BASE / "all-final-view-audit-r002.json").read_text(encoding="utf-8"))
view_metrics = json.loads((BASE / "view-metrics-reconciliation-r001.json").read_text(encoding="utf-8"))
view_by_task = {row["task_id"]: row for row in view_metrics["tasks"]}
r003_summary = {row["task_id"]: row for row in json.loads((BASE / "task-metrics-reconciliation-summary-r003.json").read_text(encoding="utf-8"))["tasks"]}
chronology = json.loads((BASE / "view-chronology-r002.json").read_text(encoding="utf-8"))
inventory = json.loads((BASE / "final-inventory-r001.json").read_text(encoding="utf-8"))
final_paths = {item["png"] for item in inventory["items"]}
def utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone()


service_hashes = set()
render_rows = []
for task_id in TASK_IDS:
    for row in sk.read_jsonl(RUN_TEMP / task_id / "requests.jsonl"):
        if row.get("request_type") == "render" and row.get("http_status") == 200:
            response = ROOT / row["response_file"]
            response_hash = hashlib.sha256(response.read_bytes()).hexdigest() if response.is_file() else None
            if response_hash:
                service_hashes.add(response_hash)
                render_rows.append({**row, "png_sha256": response_hash})
b04_recovery = {
    row["request_id"]: row
    for row in json.loads((RUN_TEMP / "B04" / "inspection" / "baseline-recovery.json").read_text(encoding="utf-8"))
}
b04_requests = [row for row in sk.read_jsonl(RUN_TEMP / "B04" / "requests.jsonl") if row.get("http_status") == 200]
source_events = defaultdict(list)
read_events_by_task = defaultdict(list)
for event in view_audit["events"]:
    if event["is_error"] or not event["result_at"] or not event["sha256"]:
        continue
    source_hash = event["sha256"]
    evidence_path = event["image_path"]
    source_id = evidence_path + ":" + source_hash
    final_match = next((item for item in inventory["items"] if item["png"] == event["image_path"] and item["sha256"] == source_hash), None)
    if final_match:
        dsl_path = ROOT / final_match["snapshot"]
        dsl_hash = hashlib.sha256(dsl_path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        final_candidates = [row for row in render_rows if row["task_id"] == final_match["task_id"] and row["png_sha256"] == source_hash and hashlib.sha256((ROOT / row["request_file"]).read_bytes().replace(b"\r\n", b"\n")).hexdigest() == dsl_hash]
        if len(final_candidates) == 1:
            source_id = "response:" + final_candidates[0]["request_id"]
    version_match = re.search(r"/versions/([^/]+)/[^/]+\.png$", event["image_path"])
    if version_match:
        candidates = [row for row in render_rows if row["task_id"] == event["task_id"] and row.get("version_id") == version_match.group(1) and row["png_sha256"] == source_hash]
        if len(candidates) == 1:
            source_id = "response:" + candidates[0]["request_id"]
    if event["task_id"] == "B04":
        for recovery in b04_recovery.values():
            original = next(row for row in b04_requests if row["request_id"] == recovery["request_id"])
            later = sorted([
                row for row in b04_requests
                if row["case_id"] == original["case_id"] and utc(row["started_at"]) > utc(original["ended_at"])
            ], key=lambda row: utc(row["started_at"]))
            if not later:
                continue
            expected_path = f'tmp/{RUN}/B04/versions/{original["version_id"]}/final-01.png'
            if event["image_path"] == expected_path and utc(original["ended_at"]) <= utc(event["result_at"]) < utc(later[0]["started_at"]):
                source_hash = recovery["png_sha256"]
                evidence_path = recovery["recovered_dir"] + "/final-01.png"
                source_id = "response:" + recovery["request_id"]
                break
    if source_hash in service_hashes:
        source_events[event["task_id"]].append({**event, "source_sha256": source_hash, "source_evidence_path": evidence_path, "source_id": source_id})
        read_events_by_task[event["task_id"]].append(event)
source_views = {
    task_id: {
        "image_views": len({event["source_id"] for event in events}),
        "actual_service_read_events": len(events),
        "repeat_service_read_events": len(events) - len({event["source_id"] for event in events}),
    }
    for task_id, events in source_events.items()
}
b03_corrections = {
    row["original_image_path"]: row["corrected_image_path"]
    for row in json.loads((RUN_TEMP / "B03" / "inspection" / "iteration-path-corrections-r001.json").read_text(encoding="utf-8"))["corrections"]
}


def digest(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


render_by_hash = defaultdict(list)
for task_id in TASK_IDS:
    for row in sk.read_jsonl(RUN_TEMP / task_id / "requests.jsonl"):
        if row.get("request_type") == "render" and row.get("http_status") == 200 and row.get("ended_at"):
            response_hash = digest(ROOT / row["response_file"])
            if response_hash:
                render_by_hash[response_hash].append(utc(row["ended_at"]))

valid_read_hashes = set()
for events in source_events.values():
    for event in events:
        source_hash = event["source_sha256"]
        if any(utc(event["result_at"]) >= ended for ended in render_by_hash.get(source_hash, [])):
            valid_read_hashes.add(source_hash)

summaries = []
for task_id in TASK_IDS:
    metric_path = RUN_OUT / task_id / "task-metrics.json"
    backup_path = backup_dir / f"{task_id}-task-metrics-before-reconciliation.json"
    if not backup_path.exists():
        shutil.copyfile(metric_path, backup_path)
    metrics = json.loads(metric_path.read_text(encoding="utf-8"))
    previous_source = json.loads(backup_path.read_text(encoding="utf-8")) if backup_path.exists() else metrics
    previous = {key: r003_summary[task_id]["reconciled"].get(key, previous_source.get(key)) for key in ("image_views", "completed_visual_iterations", "incomplete_visual_iterations", "unviewed_baselines", "final_visual_rechecks")}
    iterations = sk.read_jsonl(RUN_TEMP / task_id / "iterations.jsonl")
    placeholder_ids = {
        row["iteration_id"] for row in iterations
        if "待视觉检查" in row.get("observable_issues", "")
        and row.get("review_and_comparison") in ("尚未完成视觉复核", "无前版；等待完整查看", "基线", "待实际打开试验图后记录", "待查看后与全尺寸比较")
    }
    records = []
    for row in iterations:
        image_path = b03_corrections.get(row.get("image_path", ""), row.get("image_path", ""))
        if not str(image_path).lower().endswith(".png"):
            continue
        image_hash = digest(ROOT / image_path)
        if task_id == "B04" and row.get("type") == "baseline":
            recovery = next((item for item in b04_recovery.values() if item["case_id"] == row.get("case_id")), None)
            if recovery:
                image_hash = recovery["png_sha256"]
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
            "placeholder": row["iteration_id"] in placeholder_ids,
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

    completed = distinct([record for record in records if record["viewed"] and record["row"].get("type") == "visual" and record["row"].get("completed_visual_iteration")])

    def baseline_accepted(record):
        text = str(record["row"].get("observable_issues", "")).strip()
        return record["row"].get("completed_visual_iteration") and (text.startswith(("无", "未发现", "通过", "正常", "完整", "清晰")) or "均通过" in text or "通过初查" in text)

    baselines = distinct([record for record in records if record["viewed"] and record["row"].get("type") == "baseline" and baseline_accepted(record)])
    alternatives = distinct([record for record in records if record["viewed"] and record["row"].get("type") == "alternative" and record["row"].get("completed_visual_iteration")])
    completed_keys = {
        (record["case_id"], record["row"].get("version_id"), record["image_hash"])
        for record in [*baselines, *completed]
    }
    incomplete = distinct([
        record for record in records
        if record["viewed"] and not record["placeholder"]
        and record["row"].get("type") == "visual"
        and not record["row"].get("completed_visual_iteration")
        and (
            record["row"].get("type") == "requirement-change"
            or (record["case_id"], record["row"].get("version_id"), record["image_hash"]) not in completed_keys
        )
    ])
    failed_baselines = distinct([
        record for record in records
        if record["viewed"] and not record["placeholder"]
        and record["row"].get("type") == "baseline"
        and not record["row"].get("completed_visual_iteration")
        and (record["case_id"], record["row"].get("version_id"), record["image_hash"]) not in completed_keys
    ])
    baseline_hashes = {record["image_hash"] for record in records if record["row"].get("type") == "baseline" and record["image_hash"] in render_by_hash}
    unviewed_baselines = sum(image_hash not in valid_read_hashes for image_hash in baseline_hashes)
    final_hashes = {item["sha256"] for item in inventory["items"] if item["task_id"] == task_id}
    final_recheck_keys = {
        (record["case_id"], record["image_hash"]) for record in records
        if record["viewed"] and record["row"].get("type") == "audit_visual_recheck" and record["image_hash"] in final_hashes
    }
    requirement_changes = distinct([record for record in records if record["viewed"] and record["row"].get("type") == "requirement-change"])
    vm = view_by_task[task_id]
    sv = source_views.get(task_id, {"image_views": 0, "actual_service_read_events": 0, "repeat_service_read_events": 0})
    metrics["image_views"] = sv["image_views"]
    metrics["completed_visual_iterations"] = len(completed)
    metrics["requirement_change_iterations"] = len(requirement_changes)
    metrics["requirement_change_iteration_ids"] = [record["row"]["iteration_id"] for record in requirement_changes]
    metrics["incomplete_visual_iterations"] = len(incomplete)
    metrics["unviewed_baselines"] = unviewed_baselines
    metrics["alternative_visual_iterations"] = len(alternatives)
    metrics["final_visual_rechecks"] = len(final_recheck_keys)
    metrics["baseline_acceptances"] = len(baselines)
    metrics["failed_baselines"] = len(failed_baselines)
    metrics["remediation_candidates"] = len(incomplete) + len(failed_baselines)
    metrics["actual_service_read_events"] = sv["actual_service_read_events"]
    metrics["repeat_service_read_events"] = sv["repeat_service_read_events"]
    metrics["inspection_derivative_views"] = vm["derivative_read_events"]
    metrics["placeholder_iteration_rows_excluded"] = vm["placeholder_iteration_rows_excluded"]
    metrics["view_counting_note"] = "image_views 为真实 Read 打开的不同服务 PNG 来源数；以原始响应/版本与SHA-256共同识别，同响应复制路径不重复计，独立渲染的同字节作品不合并，覆盖前来源按请求时序还原。completed_visual_iterations 仅计 type=visual 的完成记录；requirement_change_iterations 单列预置需求变更，不等于视觉迭代。"
    metrics["metrics_reconciliation"] = {
        "reconciled_at": sk.iso(),
        "revision": "r004",
        "source": [sk.rel(BASE / "all-final-view-audit-r002.json"), sk.rel(BASE / "view-metrics-reconciliation-r001.json"), sk.rel(RUN_TEMP / "B04" / "inspection" / "baseline-recovery.json")],
        "previous_values": previous,
        "raw_logs_modified": False,
        "ordering_verification": "complete_for_B01_B02_remediations" if task_id in ("B01", "B02") else "new_view_verified; historical_order_not_fully_verified",
        "note": "最终124张服务原图查看已由会话工具记录逐件核验；历史补记行不单独当作新打开事件。",
    }
    if task_id in ("B01", "B02"):
        metrics["ordered_remediation_checks"] = [item for item in chronology["remediation_sequence_checks"] if item["task_id"] == task_id]
    if "counts" in metrics:
        for key in ("image_views", "completed_visual_iterations", "incomplete_visual_iterations", "requirement_change_iterations", "unviewed_baselines", "final_visual_rechecks"):
            if key in metrics["counts"]:
                metrics["counts"][key] = metrics[key]
        metrics["counts"]["baseline_acceptances"] = len(baselines)
        metrics["counts"]["failed_baselines"] = len(failed_baselines)
        metrics["counts"]["remediation_candidates"] = len(incomplete) + len(failed_baselines)
        metrics["counts"]["actual_service_read_events"] = vm["actual_service_read_events"]
        metrics["counts"]["inspection_derivative_views"] = vm["derivative_read_events"]
    if "case_metrics" in metrics:
        for case in metrics["case_metrics"]:
            case_id = case["case_id"]
            case_records = [record for record in records if record["case_id"] == case_id or record["case_id"].endswith(case_id)]
            case["image_views"] = len({record["image_hash"] for record in case_records if record["viewed"]})
            case["requirement_change_iterations"] = len(distinct([record for record in case_records if record["viewed"] and record["row"].get("type") == "requirement-change"]))
            case["completed_visual_iterations"] = len(distinct([record for record in case_records if record["viewed"] and record["row"].get("type") == "visual" and record["row"].get("completed_visual_iteration")]))
            case["incomplete_visual_iterations"] = len(distinct([
                record for record in case_records
                if record["viewed"] and not record["placeholder"]
                and record["row"].get("type") == "visual"
                and not record["row"].get("completed_visual_iteration")
                and (
                    record["row"].get("type") == "requirement-change"
                    or (record["case_id"], record["row"].get("version_id"), record["image_hash"]) not in completed_keys
                )
            ]))
            case["failed_baselines"] = len(distinct([
                record for record in case_records
                if record["viewed"] and not record["placeholder"]
                and record["row"].get("type") == "baseline"
                and not record["row"].get("completed_visual_iteration")
                and (record["case_id"], record["row"].get("version_id"), record["image_hash"]) not in completed_keys
            ]))
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
    request_rows = sk.read_jsonl(RUN_TEMP / task_id / "requests.jsonl")
    metrics["document_requests"] = sum(row.get("request_type") in ("document", "research_document") for row in request_rows)
    metrics["other_service_requests"] = sum(row.get("request_type") not in ("render", "document", "research_document") for row in request_rows)
    metrics["snapshot_request_elapsed_seconds_sum"] = round(sum(float(row.get("elapsed_seconds") or 0) for row in request_rows if row.get("request_type") == "render"), 3)
    metrics["all_http_request_elapsed_seconds_sum"] = round(sum(float(row.get("elapsed_seconds") or 0) for row in request_rows), 3)
    metrics["request_elapsed_seconds_sum"] = metrics["all_http_request_elapsed_seconds_sum"]
    metrics.setdefault("timings", {})["server_timing_source"] = "requests.jsonl:elapsed_seconds"
    metrics["timings"]["request_duration_sum_seconds"] = metrics["all_http_request_elapsed_seconds_sum"]
    actual_times_by_hash = defaultdict(set)
    for event in source_events.get(task_id, []):
        actual_times_by_hash[event["source_sha256"]].add(event["result_at"])
    retrospective_rows = []
    for record in records:
        row = record["row"]
        actual_times = sorted(actual_times_by_hash.get(record["image_hash"], []))
        if actual_times and row.get("viewed_at") not in actual_times:
            retrospective_rows.append({"iteration_id": row["iteration_id"], "logged_viewed_at": row.get("viewed_at"), "actual_read_result_times": actual_times})
    metrics["timestamp_provenance"] = {
        "record_type": "post_completion_audit_addendum",
        "raw_iteration_logs_modified": False,
        "retrospective_viewed_at_row_count": len(retrospective_rows),
        "rows": retrospective_rows,
        "note": "viewed_at 是历史补记时间，不单独证明当时查看；实际服务Read结果时间来自会话工具记录。B06任务墙钟保留原完成时间，指标写入与复核晚于该时间，不伪装成原任务内查看。",
    }
    if task_id.startswith("B"):
        tool_rows = sk.read_jsonl(RUN_TEMP / task_id / "tool-usage.jsonl")
        metrics["tool_usage_records"] = len(tool_rows)
        metrics.setdefault("counts", {})["other_tool_calls"] = len(tool_rows)
    metrics.setdefault("counts", {}).update({
        "document_requests": metrics["document_requests"],
        "other_service_requests": metrics["other_service_requests"],
        "requirement_change_iterations": metrics["requirement_change_iterations"],
        "repeat_service_read_events": metrics["repeat_service_read_events"],
    })
    if task_id == "B04":
        metrics["source_hash_recovery"] = {
            "evidence": sk.rel(RUN_TEMP / "B04" / "inspection" / "baseline-recovery.json"),
            "recovered_baseline_hashes": [row["png_sha256"] for row in b04_recovery.values()],
            "note": "两个v002路径先保存原始基线、后被修正版覆盖；按原始响应结束至下一次同用例渲染开始之间的Read时序还原来源，故case-01与case-05分别计2与3个内容来源。",
        }
    if task_id == "B05":
        ledger_path = RUN_TEMP / "B05" / "research-ledger.json"
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
        research = [row for row in request_rows if row.get("request_type") == "research_document"]
        ledger["audit_correction_r002"] = {
            "corrected_at": sk.iso(), "raw_logs_modified": False,
            "attempted_at_now_means": "raw request.started_at",
            "corrections": [{"request_id": row["request_id"], "attempted_at": row["started_at"], "ended_at": row["ended_at"], "http_status": row["http_status"]} for row in research],
        }
        sk.write_json(RUN_OUT / "B05" / "research-ledger-r002-corrected.json", ledger)
        metrics["external_research_metrics"].update({
            "elapsed_seconds": round(sum(float(row["elapsed_seconds"]) for row in research), 3),
            "request_elapsed_seconds_sum": round(sum(float(row["elapsed_seconds"]) for row in research), 3),
            "corrected_ledger": sk.rel(RUN_OUT / "B05" / "research-ledger-r002-corrected.json"),
            "note": "task request_elapsed_seconds_sum 含两次外部研究404；document_requests计入这两次，other_service_requests不计；case_metrics仅含Snapshot渲染。",
        })
        metrics["request_timing_breakdown"] = {
            "snapshot_request_elapsed_seconds_sum": metrics["snapshot_request_elapsed_seconds_sum"],
            "research_document_elapsed_seconds_sum": metrics["external_research_metrics"]["elapsed_seconds"],
            "all_http_request_elapsed_seconds_sum": metrics["all_http_request_elapsed_seconds_sum"],
            "source": "requests.jsonl:elapsed_seconds",
        }
    sk.write_json(metric_path, metrics)
    summaries.append({
        "task_id": task_id,
        "previous": previous,
        "reconciled": {key: metrics.get(key) for key in ("image_views", "completed_visual_iterations", "incomplete_visual_iterations", "unviewed_baselines", "final_visual_rechecks", "baseline_acceptances", "failed_baselines", "remediation_candidates", "actual_service_read_events", "inspection_derivative_views", "requirement_change_iterations", "document_requests", "other_service_requests", "snapshot_request_elapsed_seconds_sum", "all_http_request_elapsed_seconds_sum", "tool_usage_records")},
    })

sk.append_jsonl(SUITE_TEMP / "events.jsonl", {
    "event_id": f"{RUN}-suite-metrics-reconciliation-r004-attempt-{attempt:03d}",
    "at": sk.iso(),
    "event": "suite-metrics-reconciliation-r004",
    "status": "completed",
    "artifacts": [sk.rel(BASE / "view-metrics-reconciliation-r001.json"), sk.rel(backup_dir)],
    "note": "30题指标按真实Read证据统一口径：基线通过、未完成视觉迭代、失败基线和最终复核分列；原始请求/迭代日志未改，旧指标逐题备份。",
})
sk.checkpoint(RUN, "suite-metrics-reconciliation-r004")
summary_payload = {"run_id": RUN, "path_base": "suite_root", "attempt": attempt, "tasks": summaries}
sk.write_json(BASE / f"task-metrics-reconciliation-summary-r004-attempt-{attempt:03d}.json", summary_payload)
sk.write_json(BASE / "task-metrics-reconciliation-summary-r004.json", summary_payload)
print(json.dumps({"tasks": len(summaries), "image_views": sum(row["reconciled"]["image_views"] for row in summaries), "completed_visual_iterations": sum(row["reconciled"]["completed_visual_iterations"] for row in summaries), "incomplete_visual_iterations": sum(row["reconciled"]["incomplete_visual_iterations"] for row in summaries)}, ensure_ascii=False))
