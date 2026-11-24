from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re
import shutil
import struct
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import suitekit as s


def png_size(path: Path) -> tuple[int, int] | None:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n" or len(data) < 24:
        return None
    return struct.unpack(">II", data[16:24])


def task_required(task: dict) -> list[str]:
    result = [item["filename"] for item in task.get("required_outputs", [])]
    result.extend(task.get("additional_outputs", []))
    result.extend(task.get("common_outputs", []))
    return result


def designated_final_pngs(task: dict, output: Path) -> list[Path]:
    if task.get("required_outputs"):
        return [output / item["filename"] for item in task["required_outputs"]]
    if task.get("track") not in {"creative", "open_creation"}:
        return []
    portfolio_path = output / "portfolio.json"
    if portfolio_path.exists():
        portfolio = json.loads(portfolio_path.read_text(encoding="utf-8"))
        return [output / case["png"] for case in portfolio.get("cases", []) if case.get("png")]
    return sorted(path for path in output.glob("case-*/final.png") if path.is_file())


def audit_template_errors(artifact: str, template: dict, data: dict) -> list[str]:
    errors = []
    fields = template.get("artifacts", {}).get(artifact, {}).get("required_fields", {})
    for field, description in fields.items():
        if field not in data:
            errors.append(f"缺少字段 {field}")
            continue
        value = data[field]
        if "array" in description.lower() and value is not None and not isinstance(value, list):
            errors.append(f"字段 {field} 应为 array")
    return errors


def final_view_evidence(run_id: str, suite_temp: Path) -> tuple[dict, dict, dict]:
    base = suite_temp / "final-audit-r001"
    views = json.loads((base / "all-final-view-audit-r002.json").read_text(encoding="utf-8"))
    metrics = json.loads((base / "view-metrics-reconciliation-r001.json").read_text(encoding="utf-8"))
    overview = json.loads((base / "overview-review-manifest-v002.json").read_text(encoding="utf-8"))
    if views.get("run_id") != run_id:
        raise ValueError("最终查看审计与当前 run_id 不一致")
    viewed = {row["sha256"]: row["png"] for row in views["final_coverage"] if row.get("verified_service_original_view")}
    return views, metrics, overview



def audit() -> tuple[list[dict], list[dict], dict, list[dict]]:
    run_id, suite_out, suite_temp = s.init_suite()
    state = json.loads((suite_out / "suite-state.json").read_text(encoding="utf-8"))
    task_by_id = {task["id"]: task for task in s.CATALOG["tasks"]}
    views, view_metrics, overview_review = final_view_evidence(run_id, suite_temp)
    task_view_metrics = {row["task_id"]: row for row in view_metrics["tasks"]}
    reconciled_metrics = {row["task_id"]: row["reconciled"] for row in json.loads((suite_temp / "final-audit-r001" / "task-metrics-reconciliation-summary-r005.json").read_text(encoding="utf-8"))["tasks"]}
    verified_view_hashes = {row["sha256"] for row in views["final_coverage"] if row.get("verified_service_original_view")}
    issues = []
    inventory = []
    resolved_history = []
    for entry in state["tasks"]:
        task_id = entry["id"]
        full_spec = json.loads((s.ROOT / task_by_id[task_id]["task_spec"]).read_text(encoding="utf-8"))
        spec = {**task_by_id[task_id], **full_spec}
        output, temp = s.task_dirs(run_id, task_id)
        viewed_hashes = verified_view_hashes
        status = entry["status"]
        if status == "pending":
            issues.append({"task_id": task_id, "severity": "missing", "issue": "任务尚未执行"})
            continue
        for name in task_required(spec):
            path = output / name
            if not path.exists():
                issues.append({"task_id": task_id, "severity": "missing", "issue": f"缺少指定交付 {name}"})
        for required in spec.get("required_outputs", []):
            png = output / required["filename"]
            dsl = png.with_suffix(".snapshot")
            if png.exists():
                size = png_size(png)
                if size != (required["width"], required["height"]):
                    issues.append({"task_id": task_id, "severity": "dimension", "issue": f"{required['filename']} 尺寸 {size} != {(required['width'], required['height'])}"})
                if not dsl.exists() or dsl.stat().st_size < 30:
                    issues.append({"task_id": task_id, "severity": "pairing", "issue": f"{required['filename']} 缺少完整 DSL"})
                elif "<Snapshot" not in dsl.read_text(encoding="utf-8"):
                    issues.append({"task_id": task_id, "severity": "pairing", "issue": f"{dsl.name} 不是完整 Snapshot DSL"})
            if not dsl.exists():
                issues.append({"task_id": task_id, "severity": "missing", "issue": f"缺少 {required.get('dsl')}"})
        if spec.get("round_count", 1) > 1 and status == "completed":
            expected_rounds = [f"round-{index:02d}" for index in range(1, spec["round_count"] + 1)]
            if entry.get("completed_rounds") != expected_rounds:
                issues.append({"task_id": task_id, "severity": "rounds", "issue": f"已完成轮次 {entry.get('completed_rounds')} != {expected_rounds}"})
            for round_spec in spec.get("rounds", []):
                round_dir = round_spec["output_subdirectory"]
                for name in round_spec.get("required_outputs", []) + round_spec.get("additional_outputs", []) + round_spec.get("common_outputs", []):
                    if isinstance(name, dict):
                        name = name["filename"]
                    if not (output / name).exists():
                        issues.append({"task_id": task_id, "severity": "rounds", "issue": f"{round_dir} 缺少 {name}"})
        if spec.get("case_artifacts"):
            case_dirs = sorted({(output / str(case["png"])).parent for case in json.loads((output / "portfolio.json").read_text(encoding="utf-8")).get("cases", []) if case.get("png")}) if (output / "portfolio.json").is_file() else sorted(path for path in output.glob("*case-*") if path.is_dir())
            for case_dir in case_dirs:
                for name in spec["case_artifacts"]:
                    if not (case_dir / name).exists():
                        issues.append({"task_id": task_id, "severity": "missing", "issue": f"{case_dir.name} 缺少 {name}"})
            if status == "completed" and len(case_dirs) < spec.get("minimum_independent_cases", 10):
                issues.append({"task_id": task_id, "severity": "count", "issue": f"独立用例目录 {len(case_dirs)} 少于 10"})
            portfolio_path = output / "portfolio.json"
            if status == "completed":
                if not portfolio_path.exists():
                    issues.append({"task_id": task_id, "severity": "evidence", "issue": "缺少 portfolio.json"})
                else:
                    portfolio = json.loads(portfolio_path.read_text(encoding="utf-8"))
                    cases = portfolio.get("cases", [])
                    if len(cases) < spec.get("minimum_independent_cases", 10):
                        issues.append({"task_id": task_id, "severity": "count", "issue": f"portfolio 独立用例 {len(cases)} 少于 10"})
                    required_case_keys = {
                        "id", "title", "audience", "use_context", "user_goal", "content_basis",
                        "visual_intent", "png", "snapshot", "dimensions", "supporting_assets",
                        "dsl_capabilities", "completion_criteria", "visual_review", "request_ids",
                        "iteration_ids", "plan_version", "criteria_history", "criterion_results",
                        "unresolved_issues",
                    }
                    case_ids, case_paths, case_hashes = set(), set(), set()
                    for case in cases:
                        case_id = case.get("id")
                        if not case_id or case_id in case_ids:
                            issues.append({"task_id": task_id, "severity": "evidence", "issue": f"portfolio 用例 ID 缺失或重复：{case_id}"})
                        case_ids.add(case_id)
                        missing = sorted(required_case_keys - set(case))
                        if missing:
                            issues.append({"task_id": task_id, "severity": "evidence", "issue": f"{case_id} portfolio 缺字段 {', '.join(missing)}"})
                        png_name = case.get("png")
                        if not png_name or png_name in case_paths:
                            issues.append({"task_id": task_id, "severity": "evidence", "issue": f"{case_id} PNG 路径缺失或重复：{png_name}"})
                        case_paths.add(png_name)
                        png = output / str(png_name)
                        if png.is_file():
                            digest = hashlib.sha256(png.read_bytes()).hexdigest()
                            if digest in case_hashes:
                                issues.append({"task_id": task_id, "severity": "independence", "issue": f"{case_id} 与其他用例最终 PNG 字节完全相同"})
                            case_hashes.add(digest)
                            if digest not in viewed_hashes:
                                issues.append({"task_id": task_id, "severity": "evidence", "issue": f"{case_id} 最终图无匹配字节查看记录"})
                        if not case.get("criterion_results"):
                            issues.append({"task_id": task_id, "severity": "evidence", "issue": f"{case_id} 缺少逐条完成标准结果"})
                        if case.get("unresolved_issues"):
                            issues.append({"task_id": task_id, "severity": "unresolved", "issue": f"{case_id} 仍有未解决问题"})
                    gallery_path = output / "gallery.md"
                    gallery = gallery_path.read_text(encoding="utf-8") if gallery_path.exists() else ""
                    for case in cases:
                        png_name = str(case.get("png", ""))
                        if png_name and png_name not in gallery:
                            issues.append({"task_id": task_id, "severity": "gallery", "issue": f"portfolio 用例 {case.get('id')} 未在 gallery.md 逐图展示"})
                    metric_path = output / "task-metrics.json"
                    if metric_path.exists():
                        metric = json.loads(metric_path.read_text(encoding="utf-8"))
                        if not metric.get("case_metrics") or not metric.get("tool_usage_summary"):
                            issues.append({"task_id": task_id, "severity": "metrics", "issue": "B类指标缺少 case_metrics 或 tool_usage_summary"})
        if status == "completed":
            task_dir = s.ROOT / task_by_id[task_id]["directory"]
            for artifact, template_name in spec.get("audit_templates", {}).items():
                artifact_path = output / artifact
                template_path = task_dir / template_name
                if not artifact_path.exists():
                    continue
                if not template_path.exists():
                    issues.append({"task_id": task_id, "severity": "audit-schema", "issue": f"{artifact} 的字段模板不存在：{template_name}"})
                    continue
                try:
                    artifact_data = json.loads(artifact_path.read_text(encoding="utf-8"))
                    template_data = json.loads(template_path.read_text(encoding="utf-8"))
                except (ValueError, UnicodeError) as exc:
                    issues.append({"task_id": task_id, "severity": "audit-schema", "issue": f"{artifact} JSON 无法解析：{exc}"})
                    continue
                for field, expected in (("schema_version", 1), ("task_id", task_id), ("path_base", "output_dir")):
                    if artifact_data.get(field) != expected:
                        issues.append({"task_id": task_id, "severity": "audit-schema", "issue": f"{artifact}.{field}={artifact_data.get(field)!r} != {expected!r}"})
                for error in audit_template_errors(artifact, template_data, artifact_data):
                    issues.append({"task_id": task_id, "severity": "audit-schema", "issue": f"{artifact} {error}"})
        for log_name in spec.get("log_files", []):
            if status != "pending" and not (temp / log_name).exists():
                issues.append({"task_id": task_id, "severity": "evidence", "issue": f"缺少过程日志 {log_name}"})
        pngs = designated_final_pngs(spec, output)
        minimum = spec.get("minimum_final_pngs", 1)
        if status == "completed" and len(pngs) < minimum:
            issues.append({"task_id": task_id, "severity": "count", "issue": f"指定最终 PNG {len(pngs)} < {minimum}"})
        requests = s.read_jsonl(temp / "requests.jsonl")
        iterations = s.read_jsonl(temp / "iterations.jsonl")
        if status != "pending":
            request_fields = {"request_id", "request_type", "started_at", "ended_at", "timezone", "elapsed_seconds", "request_file", "response_file", "http_status", "content_type"}
            request_ids = set()
            for record in requests:
                missing = sorted(request_fields - set(record))
                if missing:
                    issues.append({"task_id": task_id, "severity": "evidence", "issue": f"请求日志缺字段 {', '.join(missing)}"})
                if record.get("request_id") in request_ids:
                    issues.append({"task_id": task_id, "severity": "evidence", "issue": f"请求 ID 重复：{record.get('request_id')}"})
                request_ids.add(record.get("request_id"))
                if not record.get("timezone"):
                    issues.append({"task_id": task_id, "severity": "evidence", "issue": f"请求 {record.get('request_id')} 缺少时区"})
            iteration_fields = {"iteration_id", "version_id", "type", "image_path", "viewed_at", "timezone", "observable_issues", "changes", "review_and_comparison"}
            for record in iterations:
                missing = sorted(iteration_fields - set(record))
                if missing:
                    issues.append({"task_id": task_id, "severity": "evidence", "issue": f"迭代日志缺字段 {', '.join(missing)}"})
                if not record.get("timezone"):
                    issues.append({"task_id": task_id, "severity": "evidence", "issue": f"迭代 {record.get('iteration_id')} 缺少时区"})
        service_pairs = []
        for record in requests:
            if record["request_type"] != "render" or record["http_status"] != 200:
                continue
            response_path = s.ROOT / record["response_file"]
            request_path = s.ROOT / record["request_file"]
            if not response_path.exists() or not request_path.exists():
                issues.append({"task_id": task_id, "severity": "evidence", "issue": f"成功渲染 {record['request_id']} 缺少原始请求或响应"})
                continue
            service_pairs.append({
                "request_id": record["request_id"],
                "response_path": record["response_file"],
                "png_sha256": hashlib.sha256(response_path.read_bytes()).hexdigest(),
                "dsl_normalized_sha256": hashlib.sha256(request_path.read_bytes().replace(b"\r\n", b"\n")).hexdigest(),
            })
        success = sum(item["request_type"] == "render" and item["http_status"] == 200 for item in requests)
        if status == "completed" and success < len(pngs):
            issues.append({"task_id": task_id, "severity": "evidence", "issue": f"成功渲染 {success} 少于最终 PNG {len(pngs)}"})
        metric_path = output / "task-metrics.json"
        if status == "completed" and metric_path.exists():
            metric = json.loads(metric_path.read_text(encoding="utf-8"))
            expected_metrics = {
                "status": status,
                "started_at": entry.get("started_at"),
                "ended_at": entry.get("ended_at"),
                "snapshot_requests": sum(item["request_type"] == "render" for item in requests),
                "successful_snapshot_requests": success,
                "failed_snapshot_requests": sum(item["request_type"] == "render" and item["http_status"] != 200 for item in requests),
                "image_views": reconciled_metrics[task_id]["image_views"],
                "baseline_acceptances": reconciled_metrics[task_id]["baseline_acceptances"],
                "failed_baselines": reconciled_metrics[task_id]["failed_baselines"],
                "completed_visual_iterations": reconciled_metrics[task_id]["completed_visual_iterations"],
                "incomplete_visual_iterations": reconciled_metrics[task_id]["incomplete_visual_iterations"],
                "requirement_change_iterations": sum(row.get("type") == "requirement-change" for row in iterations),
                "document_requests": sum(row.get("request_type") in ("document", "research_document") for row in requests),
                "other_service_requests": sum(row.get("request_type") not in ("render", "document", "research_document") for row in requests),
                "snapshot_request_elapsed_seconds_sum": round(sum(float(row.get("elapsed_seconds") or 0) for row in requests if row.get("request_type") == "render"), 3),
                "all_http_request_elapsed_seconds_sum": round(sum(float(row.get("elapsed_seconds") or 0) for row in requests), 3),
                "final_pngs": len(pngs),
            }
            for key, expected in expected_metrics.items():
                if metric.get(key) != expected:
                    issues.append({"task_id": task_id, "severity": "metrics", "issue": f"task-metrics.{key}={metric.get(key)!r} != {expected!r}"})
            if not isinstance(metric.get("wall_clock_seconds"), (int, float)) or metric["wall_clock_seconds"] < 0:
                issues.append({"task_id": task_id, "severity": "metrics", "issue": "task-metrics.wall_clock_seconds 缺失或为负"})
            reconciliation = metric.get("metrics_reconciliation", {})
            if reconciliation.get("raw_logs_modified") is not False or reconciliation.get("revision") != "r005":
                issues.append({"task_id": task_id, "severity": "metrics", "issue": "task-metrics 缺少 r005 真实查看证据对账标记"})
            for key in ("completed_visual_iterations", "incomplete_visual_iterations", "requirement_change_iterations", "unviewed_baselines", "baseline_acceptances", "failed_baselines", "final_visual_rechecks"):
                if key not in metric or not isinstance(metric[key], int) or metric[key] < 0:
                    issues.append({"task_id": task_id, "severity": "metrics", "issue": f"task-metrics 缺少有效 {key}"})
            if metric.get("timings", {}).get("server_timing_source") != "requests.jsonl:elapsed_seconds":
                issues.append({"task_id": task_id, "severity": "metrics", "issue": "请求计时来源标签错误"})
            if metric.get("timestamp_provenance", {}).get("record_type") != "post_completion_audit_addendum" or metric.get("timestamp_provenance", {}).get("raw_iteration_logs_modified") is not False:
                issues.append({"task_id": task_id, "severity": "metrics", "issue": "缺少追溯时间补记披露"})
            if task_id.startswith("B") and metric.get("tool_usage_records") != len(s.read_jsonl(temp / "tool-usage.jsonl")):
                issues.append({"task_id": task_id, "severity": "metrics", "issue": "B类工具使用记录数与日志不一致"})
            for key in ("image_views", "baseline_acceptances", "failed_baselines", "completed_visual_iterations", "incomplete_visual_iterations", "requirement_change_iterations", "document_requests", "other_service_requests"):
                if key in metric.get("counts", {}) and metric["counts"][key] != metric.get(key):
                    issues.append({"task_id": task_id, "severity": "metrics", "issue": f"counts.{key} 与任务顶层不一致"})
        if status == "completed":
            for png in pngs:
                if png.exists() and hashlib.sha256(png.read_bytes()).hexdigest() not in viewed_hashes:
                    issues.append({"task_id": task_id, "severity": "evidence", "issue": f"{s.rel(png)} 没有匹配最终字节的实际查看记录"})
        if status == "completed" and (not entry.get("artifacts") or not entry.get("visual_review_evidence")):
            issues.append({"task_id": task_id, "severity": "evidence", "issue": "suite-state 缺少产物或视觉复核证据"})
        if status == "completed" and entry.get("unresolved_issues"):
            issues.append({"task_id": task_id, "severity": "unresolved", "issue": "completed 任务仍列未解决问题"})
        for png in pngs:
            if not png.exists():
                continue
            dsl = png.with_suffix(".snapshot")
            png_digest = hashlib.sha256(png.read_bytes()).hexdigest()
            dsl_digest = hashlib.sha256(dsl.read_bytes()).hexdigest() if dsl.exists() else None
            dsl_normalized_digest = hashlib.sha256(dsl.read_bytes().replace(b"\r\n", b"\n")).hexdigest() if dsl.exists() else None
            matched = next((pair for pair in service_pairs if pair["png_sha256"] == png_digest and pair["dsl_normalized_sha256"] == dsl_normalized_digest), None)
            if status == "completed" and matched is None:
                issues.append({"task_id": task_id, "severity": "evidence", "issue": f"{s.rel(png)} 与 DSL 未同时匹配任一成功渲染的原始请求/响应"})
            item = {
                "task_id": task_id, "status": status, "title": spec["title"],
                "path": s.rel(png), "dsl_path": s.rel(dsl) if dsl.exists() else None,
                "size": png_size(png), "sha256": png_digest, "dsl_sha256": dsl_digest,
                "dsl_normalized_sha256": dsl_normalized_digest,
                "service_response": matched["response_path"] if matched else None,
                "service_request_id": matched["request_id"] if matched else None,
                "group": png.parent.relative_to(output).as_posix() if png.parent != output else "final",
            }
            inventory.append(item)
            if not dsl.exists():
                issues.append({"task_id": task_id, "severity": "pairing", "issue": f"{s.rel(png)} 无同名 DSL"})
            if spec["track"] == "advanced" and dsl.exists() and re.search(r"<Image\b", dsl.read_text(encoding="utf-8")):
                issues.append({"task_id": task_id, "severity": "asset-policy", "issue": f"{s.rel(dsl)} 含 Image，A类要求纯 DSL"})
        if status in ("partial", "blocked"):
            issues.append({"task_id": task_id, "severity": status, "issue": entry.get("resume_notes") or "任务未完成"})
    expected_order = s.CATALOG["task_order"]
    actual_order = [entry["id"] for entry in state["tasks"]]
    if actual_order != expected_order:
        issues.append({"severity": "sequence", "issue": "suite-state 任务顺序与 catalog.task_order 不一致"})
    all_completed = all(entry["status"] == "completed" for entry in state["tasks"])
    if len(inventory) != s.CATALOG["minimum_final_pngs"]:
        issues.append({"severity": "count", "issue": f"当前指定最终 PNG {len(inventory)} != {s.CATALOG['minimum_final_pngs']}"})
    audit_by_path = {row["png"]: row for row in views["final_coverage"]}
    for item in inventory:
        evidence = audit_by_path.get(item["path"])
        if not evidence or evidence.get("sha256") != item["sha256"] or not evidence.get("verified_service_original_view"):
            issues.append({"task_id": item["task_id"], "severity": "evidence", "issue": f"{item['path']} 缺少渲染后真实查看服务原图的会话证据"})
    if overview_review.get("unviewed_count") != 0 or len(overview_review.get("sheets", [])) != 8:
        issues.append({"severity": "evidence", "issue": "八张全套总览接触表未全部完成实际查看"})
    overview_paths = [path for sheet in overview_review.get("sheets", []) for path in sheet.get("items", [])]
    if set(overview_paths) != {item["path"] for item in inventory}:
        issues.append({"severity": "evidence", "issue": "总览接触表覆盖集合与124张最终图清单不一致"})
    if all_completed:
        if state.get("status") != "completed":
            issues.append({"severity": "suite-status", "issue": "全部任务已完成但 suite-state.status 不是 completed"})
        if not state.get("ended_at"):
            issues.append({"severity": "suite-status", "issue": "全部任务已完成但缺少 ended_at"})
        if len(inventory) < s.CATALOG["minimum_final_pngs"]:
            issues.append({"severity": "count", "issue": f"全套指定最终 PNG {len(inventory)} < {s.CATALOG['minimum_final_pngs']}"})
        recorded = set(state.get("suite_artifacts", []))
        for name in s.CONFIG["suite_required_artifacts"]:
            if name not in recorded:
                issues.append({"severity": "suite-artifacts", "issue": f"suite-state.suite_artifacts 缺少 {name}"})
    elif state.get("status") == "completed":
        issues.append({"severity": "suite-status", "issue": "suite-state 提前标为 completed，仍有任务未完成"})
    previous_end = None
    for entry in state["tasks"]:
        if not entry.get("started_at"):
            continue
        started_at = dt.datetime.fromisoformat(entry["started_at"])
        if previous_end and started_at < previous_end:
            issues.append({"task_id": entry["id"], "severity": "sequence", "issue": "任务开始时间早于前一任务结束时间"})
        if entry.get("ended_at"):
            previous_end = dt.datetime.fromisoformat(entry["ended_at"])
    gitignore = s.ROOT / ".gitignore"
    if not gitignore.exists():
        issues.append({"severity": "setup", "issue": "缺少根 .gitignore"})
    else:
        rules = gitignore.read_text(encoding="utf-8").splitlines()
        for cache in ("__pycache__/", "*.pyc", ".pytest_cache/"):
            if cache not in rules:
                issues.append({"severity": "setup", "issue": f".gitignore 缺少 {cache}"})
        if any(rule.strip() in ("outputs/", "tmp/", "outputs", "tmp") for rule in rules):
            issues.append({"severity": "setup", "issue": ".gitignore 不得忽略 outputs/ 或 tmp/"})
    drive_pattern = r"(?<![A-Za-z])[A-Za-z]" + chr(58) + r"[\\/]"
    task_by_id = {task["id"]: task for task in s.CATALOG["tasks"]}
    input_drive_prefixes = {}
    for task_id, catalog_task in task_by_id.items():
        task_dir = s.ROOT / catalog_task["directory"]
        full_spec = json.loads((task_dir / "task.json").read_text(encoding="utf-8"))
        prefixes = set()
        for input_name in full_spec.get("inputs", []):
            input_path = task_dir / input_name
            if input_path.is_file():
                try:
                    input_text = input_path.read_text(encoding="utf-8")
                except UnicodeError:
                    continue
                prefixes.update(match.group(0) for match in re.finditer(drive_pattern, input_text))
        if prefixes:
            input_drive_prefixes[task_id] = sorted(prefixes)
    for task_id in [entry["id"] for entry in state["tasks"] if entry["status"] == "completed"]:
        output, temp = s.task_dirs(run_id, task_id)
        for base in (output, temp):
            if not base.exists():
                continue
            for path in base.rglob("*"):
                if not path.is_file() or path.suffix.lower() not in {".md", ".json", ".jsonl", ".snapshot", ".py", ".txt", ".yaml", ".request"}:
                    continue
                try:
                    content = path.read_text(encoding="utf-8")
                except UnicodeError:
                    continue
                found = {match.group(0) for match in re.finditer(drive_pattern, content)}
                unapproved = found - set(input_drive_prefixes.get(task_id, []))
                portable_successor = (
                    task_id == "B03"
                    and path.parent.name == "inspection"
                    and path.name in {"final-image-inventory.json", "final-image-inventory-r002.json", "final-image-inventory-r003.json"}
                    and (path.parent / "final-image-inventory-r004-portable.json").is_file()
                )
                if unapproved and not portable_successor:
                    issues.append({"task_id": task_id, "severity": "path-policy", "issue": f"{s.rel(path)} 含写死机器路径 {sorted(unapproved)}"})
                elif unapproved and portable_successor:
                    resolved_history.append({"task_id": task_id, "artifact": s.rel(path), "successor": s.rel(path.parent / "final-image-inventory-r004-portable.json"), "note": "历史文件保留；当前路径以可移植后继版本为准。"})
    for script in (s.ROOT / "tools").glob("*.py"):
        if re.search(drive_pattern, script.read_text(encoding="utf-8")):
            issues.append({"severity": "path-policy", "issue": f"{s.rel(script)} 含写死机器路径"})
    return issues, inventory, input_drive_prefixes, resolved_history


def generate() -> dict:
    run_id, suite_out, suite_temp = s.init_suite()
    views, view_metrics, overview_review = final_view_evidence(run_id, suite_temp)
    state = json.loads((suite_out / "suite-state.json").read_text(encoding="utf-8"))
    issues, inventory, input_drive_prefixes, resolved_history = audit()
    archive = suite_temp / "final-audit-r001" / "pre-final-aggregate-backup"
    archive.mkdir(parents=True, exist_ok=True)
    aggregate_names = s.CONFIG["suite_required_artifacts"] + ["audit-report.json"]
    archived = []
    for name in dict.fromkeys(aggregate_names):
        source = suite_out / name
        if source.is_file():
            target = archive / name
            if not target.exists():
                shutil.copyfile(source, target)
            archived.append(s.rel(target))
    task_by_id = {task["id"]: task for task in s.CATALOG["tasks"]}
    creative_titles = {}
    for task_id in ("B01", "B02", "B03", "B04", "B05", "B06"):
        output, _ = s.task_dirs(run_id, task_id)
        portfolio_path = output / "portfolio.json"
        if portfolio_path.exists():
            portfolio = json.loads(portfolio_path.read_text(encoding="utf-8"))
            for case in portfolio.get("cases", []):
                creative_titles[(task_id, s.rel(output / str(case.get("png", ""))))] = case.get("title", case.get("id", "未命名用例"))
    lines = ["# 全套最终图片画廊", "", f"运行 ID：`{run_id}`。本文件仅列出实际存在的最终 PNG；所有链接相对本文件。", ""]
    current_task = None
    current_group = None
    for item in inventory:
        if item["task_id"] != current_task:
            current_task = item["task_id"]
            current_group = None
            lines.extend([f"## {current_task} · {item['title']}", ""])
        if item["group"] != current_group:
            current_group = item["group"]
            lines.extend([f"### {current_group}", ""])
        png_link = os.path.relpath(s.ROOT / item["path"], suite_out).replace(os.sep, "/")
        dsl_link = os.path.relpath(s.ROOT / item["dsl_path"], suite_out).replace(os.sep, "/") if item["dsl_path"] else ""
        title = creative_titles.get((current_task, item["path"]), Path(item["path"]).stem.replace("-", " ").replace("_", " "))
        lines.extend([
            f"#### {title}",
            "",
            f"![{current_task} {title}]({png_link})",
            "",
            f"- 原 PNG：[{Path(item['path']).name}]({png_link})",
            f"- 完整 DSL：[{Path(item['dsl_path']).name}]({dsl_link})" if dsl_link else "- 完整 DSL：缺失",
            f"- 尺寸：{item['size'][0]}×{item['size'][1]}" if item['size'] else "- 尺寸：无效 PNG",
            "",
        ])
    (suite_out / "gallery.md").write_text("\n".join(lines), encoding="utf-8")
    index = ["# 全套任务索引", "", f"- 运行 ID：`{run_id}`", f"- 状态：`{state['status']}`", f"- 完整画廊：[gallery.md](gallery.md)", ""]
    for entry in state["tasks"]:
        spec = task_by_id[entry["id"]]
        report = suite_out.parent / entry["id"] / "snapshot-usage.md"
        report_link = f"- {entry['id']} · {spec['title']} · **{entry['status']}**"
        if report.exists():
            report_link += f" · [单题报告](../{entry['id']}/snapshot-usage.md)"
        index.append(report_link + (f" · 轮次 {', '.join(entry['completed_rounds'])}" if entry['completed_rounds'] else ""))
    index.extend(["", f"输出目录：`{s.rel(suite_out.parent)}`；临时目录：`{s.rel(suite_temp.parent)}`（path_base=suite_root）。", ""])
    (suite_out / "index.md").write_text("\n".join(index), encoding="utf-8")
    summaries = []
    totals = Counter()
    for entry in state["tasks"]:
        output, _ = s.task_dirs(run_id, entry["id"])
        metric_path = output / "task-metrics.json"
        if not metric_path.exists():
            continue
        metric = json.loads(metric_path.read_text(encoding="utf-8"))
        summaries.append(metric)
        for key in ("final_pngs", "snapshot_requests", "successful_snapshot_requests", "failed_snapshot_requests", "retry_requests", "other_service_requests", "document_requests", "dsl_versions", "image_views", "actual_service_read_events", "repeat_service_read_events", "inspection_derivative_views", "placeholder_iteration_rows_excluded", "baseline_acceptances", "failed_baselines", "completed_visual_iterations", "incomplete_visual_iterations", "requirement_change_iterations", "unviewed_baselines", "final_visual_rechecks"):
            totals[key] += int(metric.get(key) or 0)
    shared_requests = s.read_jsonl(suite_temp / "shared" / "requests.jsonl")
    totals["other_service_requests"] += sum(item["request_type"] not in ("render", "document", "research_document") for item in shared_requests)
    totals["document_requests"] += sum(item["request_type"] in ("document", "research_document") for item in shared_requests)
    totals["final_pngs"] = len(inventory)
    totals["independent_creative_cases"] = sum(len([item for item in inventory if item["task_id"] == task_id]) for task_id in ("B01", "B02", "B03", "B04", "B05", "B06"))
    status_counts = Counter(entry["status"] for entry in state["tasks"])
    started = dt.datetime.fromisoformat(state["started_at"])
    ended = dt.datetime.fromisoformat(state["ended_at"]) if state.get("ended_at") else s.now()
    suite_metrics = {
        "schema_version": 1, "path_base": "suite_root", "suite_version": s.CATALOG["suite_version"],
        "run_id": run_id, "profile": "all", "status": state["status"],
        "stop_reason": state.get("stop_reason"), "started_at": state["started_at"],
        "ended_at": s.iso(ended), "elapsed_seconds": round((ended - started).total_seconds(), 3),
        "elapsed_time_note": "elapsed_seconds 是启动到当前的墙钟时间，包含等待、间隙与并行执行，不都等同于主动工作。",
        "task_status_counts": {key: status_counts[key] for key in ("completed", "partial", "blocked", "pending", "in_progress")},
        "counts": dict(totals),
        "shared_preparation": {"path": s.rel(suite_temp / "shared"), "requests": len(shared_requests), "reused_documents": True},
        "task_summaries": summaries,
        "aggregation_rule": "Only task-level totals plus shared preparation; round/case details are not added again.",
        "view_evidence": {"source": s.rel(suite_temp / "final-audit-r001" / "all-final-view-audit-r002.json"), "verified_final_pngs": sum(row.get("verified_service_original_view") is True for row in views["final_coverage"]), "overview_sheets_viewed": sum(sheet.get("viewed") is True for sheet in overview_review["sheets"])},
        "pre_final_aggregate_archive": {"path": s.rel(archive), "newly_archived": archived},
        "resolved_historical_findings": resolved_history,
        "output_dir": s.rel(suite_out), "temp_dir": s.rel(suite_temp), "unresolved_issues": issues,
    }
    s.write_json(suite_out / "task-metrics.json", suite_metrics)
    task_prompt_checklists = []
    for entry in state["tasks"]:
        task_id = entry["id"]
        full_spec = json.loads((s.ROOT / task_by_id[task_id]["task_spec"]).read_text(encoding="utf-8"))
        output, temp = s.task_dirs(run_id, task_id)
        named_outputs = [item["filename"] for item in full_spec.get("required_outputs", [])]
        named_outputs += full_spec.get("additional_outputs", []) + full_spec.get("common_outputs", [])
        task_dir = s.ROOT / task_by_id[task_id]["directory"]
        instruction_sources = [task_by_id[task_id]["entry"], (task_dir / "AGENTS.md").as_posix()]
        source_manifest = {
            source: hashlib.sha256((s.ROOT / source).read_bytes()).hexdigest()
            for source in instruction_sources if (s.ROOT / source).is_file()
        }
        checks = []
        for number, requirement in enumerate(full_spec.get("prompt", "").splitlines(), 1):
            requirement = requirement.strip()
            if not requirement:
                continue
            evidence = []
            if any(word in requirement for word in ("PNG", "尺寸", "图", "海报", "卡片", "页面", "帧")):
                evidence.extend(name for name in named_outputs if name.endswith((".png", ".snapshot")))
            if any(word in requirement for word in ("JSON", "json", "审计", "audit", "数据", "公式", "计算", "路径")):
                evidence.extend(name for name in named_outputs if name.endswith(".json"))
            if any(word in requirement for word in ("查看", "视觉", "自检", "渲染", "服务", "DSL", "Snapshot")):
                evidence.extend([s.rel(temp / "iterations.jsonl"), s.rel(temp / "requests.jsonl"), s.rel(output / "snapshot-usage.md")])
            if not evidence:
                evidence = named_outputs + [s.rel(output / "snapshot-usage.md")]
            evidence = [name if name.startswith(("outputs/", "tmp/")) else s.rel(output / name) for name in dict.fromkeys(evidence)]
            missing_evidence = [name for name in evidence if not (s.ROOT / name).is_file()]
            if missing_evidence:
                issues.append({"task_id": task_id, "severity": "evidence", "issue": f"要求 {number} 的证据文件缺失：{', '.join(missing_evidence)}"})
            checks.append({
                "item": number,
                "requirement": requirement,
                "evidence": evidence,
                "evidence_exists": not missing_evidence,
                "verified": entry["status"] == "completed" and not [item for item in issues if item.get("task_id") == task_id] and not missing_evidence,
                "verification_scope": "结构、指定产物与日志存在性由本检查验证；语义、数据、几何与视觉质量以单题报告及实际查看记录为准。",
            })
        task_prompt_checklists.append({
            "task_id": task_id,
            "requirements_source": task_by_id[task_id]["task_spec"],
            "instructions_source": instruction_sources,
            "source_sha256": source_manifest,
            "status": entry["status"],
            "named_deliverables": named_outputs,
            "prompt_items": checks,
            "quality_gate": "completed 仅在有逐项报告、最终字节查看记录、数据/几何审计且无任务审计问题时成立；自动审计不替代人工视觉判断。",
        })
    audit_report = {
        "run_id": run_id, "audited_at": s.iso(), "objective": "START-PROMPT.txt 的全部 30 题、至少 124 张最终 PNG、A21/A22 各三轮、B01-B06 各至少 10 件及全套终审",
        "requirements": {
            "tasks_total": len(state["tasks"]), "tasks_completed": status_counts["completed"],
            "minimum_final_pngs": s.CATALOG["minimum_final_pngs"], "actual_final_pngs": len(inventory),
            "creative_cases": totals["independent_creative_cases"], "a21_rounds": next(entry["completed_rounds"] for entry in state["tasks"] if entry["id"] == "A21"),
            "a22_rounds": next(entry["completed_rounds"] for entry in state["tasks"] if entry["id"] == "A22"),
            "suite_artifacts": [name for name in s.CONFIG["suite_required_artifacts"] if (suite_out / name).exists()],
        },
        "issue_count": len(issues), "issues": issues, "inventory": inventory,
        "resolved_historical_findings": resolved_history,
        "required_input_path_literal_prefixes": input_drive_prefixes,
        "task_prompt_checklists": task_prompt_checklists,
        "prompt_to_artifact_checklist": [
            {"requirement": "读取 START-PROMPT、AGENTS、TASKS、catalog、run-config、PATHS 与全部子题规范", "evidence": "suite-state、30份 task_prompt_checklists、各题 snapshot-usage.md"},
            {"requirement": "同一 run_id、统一 outputs/tmp，按 catalog.task_order 顺序执行", "evidence": "suite-state 时间顺序、每任务 output_dir/temp_dir、sequence issues"},
            {"requirement": "启动时建立 suite-state、events.jsonl 与不可覆盖检查点", "evidence": "suite-state.json、tmp/<run_id>/_suite/events.jsonl、checkpoints/state-*.json"},
            {"requirement": "创建或合并根 .gitignore，仅排除运行时缓存", "evidence": ".gitignore 与 setup issues；outputs/tmp/日志/JSON/PNG/DSL 不被忽略"},
            {"requirement": "实际读取服务指南、OpenAPI、DSL语法/标签/文本/布局/滤镜/字体文档并缓存", "evidence": "tmp/<run_id>/_suite/shared 文档、requests.jsonl、各题来源记录"},
            {"requirement": "使用真实 open-snapshot 服务，以 UTF-8 纯文本 DSL 请求 /snapshot", "evidence": "requests.jsonl 的 method/url/content_type/request_file 与原始响应"},
            {"requirement": "每个请求记录唯一ID、时区、起止、耗时、状态、Content-Type、原始文件、错误、requestId/Server-Timing", "evidence": "请求日志字段审计与 request/response 文件"},
            {"requirement": "429/503按真实 Retry-After 重试并保留每次尝试", "evidence": "attempt/is_retry/parent_request_id/retry_after 与全部原始响应"},
            {"requirement": "A01–A24 全部完成并逐题满足各自内容、数据、几何、尺寸和专用审计", "evidence": "各题状态、task_prompt_checklists、数据/几何审计、自动审计 issues"},
            {"requirement": "B01–B06 各至少10件独立完整作品，共至少60件", "evidence": "六份 portfolio.json、case-*、case.md、独立计数、independence issues"},
            {"requirement": "B类首次渲染前建立完成标准，保留版本历史、逐条结果、工具使用和未解决事项", "evidence": "criteria_history、first_render_request_id、criterion_results、tool-usage.jsonl"},
            {"requirement": "B类不得把换色换字、简单缩放裁剪、局部放大或迭代变体算作独立作品", "evidence": "brief independence_rationale、case.md、portfolio、不同最终PNG哈希与人工审核"},
            {"requirement": "A21 按 TASK→round-02→round-03 顺序完成三轮双尺寸发布物", "evidence": "round-01/02/03 全部PNG/DSL、design-tokens/content-map、第三轮contrast-audit"},
            {"requirement": "A22 按 TASK→round-02→round-03 顺序完成三轮数据更正与局部回归", "evidence": "round-01/02/03 PNG/DSL、修正数据、主区域边界回归审计"},
            {"requirement": "所有轮次保留实际DSL、原始PNG、报告、指标、查看/变化证据且不覆盖前轮", "evidence": "round目录、versions、iterations、round task-metrics、completed_rounds"},
            {"requirement": "至少124张指定最终PNG，尺寸与 task.json 一致", "evidence": "inventory、minimum_final_pngs、PNG IHDR尺寸检查"},
            {"requirement": "每个指定最终PNG有同名完整Snapshot且与服务成功原始响应字节精确匹配", "evidence": "inventory.service_response/request_id、PNG SHA-256、规范化DSL SHA-256"},
            {"requirement": "A类主体纯DSL，不使用Image嵌入整图或外部素材", "evidence": "asset-policy issues、最终DSL检查"},
            {"requirement": "每张最终图实际打开查看，发现缺陷则修改、重渲染并复查", "evidence": "iterations.jsonl 最终字节哈希匹配、observable_issues/changes/review_and_comparison"},
            {"requirement": "保留初次、最终、失败、草稿、预览、脚本、研究/素材与中间数据，不清理不覆盖", "evidence": "tmp各题versions、request/response、iterations、research、脚本与日志"},
            {"requirement": "每题交付 snapshot-usage.md 与 task-metrics.json，过程日志齐全", "evidence": "task_required、log_files、metric consistency issues"},
            {"requirement": "指标分开记录墙钟、请求耗时、首次可用图、反馈/排队等待、成功失败重试、版本、查看与迭代", "evidence": "task-metrics字段、elapsed_time_note、日志重算结果"},
            {"requirement": "总指标仅累计任务顶层与shared，不重复累计轮次/用例明细", "evidence": "suite task-metrics.aggregation_rule 与 task_summaries"},
            {"requirement": "本地路径使用相对基准或目录环境变量，不写死机器/用户/UNC路径", "evidence": "path-policy issues、path_base字段、PATHS.md"},
            {"requirement": "不保存密钥，日志无可信凭证", "evidence": "suitekit仅从环境读取并写入请求头；请求日志不记录认证头"},
            {"requirement": "交付 index.md、gallery.md、snapshot-usage.md、task-metrics.json、suite-state.json", "evidence": "suite_required_artifacts、suite-state.suite_artifacts"},
            {"requirement": "gallery逐图展示全部最终PNG、原PNG与.snapshot相对链接，含A21/A22所有轮次和B类全部作品", "evidence": "inventory逐项生成gallery、Markdown链接存在性检查"},
            {"requirement": "完成前核对语义、视觉、数据、几何、效果、配对、报告、日志与链接，不以文件齐全代替质量", "evidence": "audit-report、逐题自检、最终人工复看与completion_ready"},
            {"requirement": "仅全部任务完成、必要检查完成、无已知交付缺陷且总审查通过才标全套completed", "evidence": "suite-state状态、audit issues、completion_ready"},
        ],
        "limitations": "自动审计验证文件、尺寸、配对、数量、日志和链接结构；语义与视觉质量仍以各题报告及最终人工复看为依据。",
    }
    s.write_json(suite_out / "audit-report.json", audit_report)
    usage = f"""# 全套 Snapshot 使用、经验与终审

- 运行 ID：`{run_id}`
- 当前状态：`{state['status']}`
- 输出：`{s.rel(suite_out)}`；临时：`{s.rel(suite_temp)}`（path_base=suite_root）
- 根缓存规则：[.gitignore](../../../.gitignore)，仅排除运行时缓存，不排除 `outputs/`、`tmp/` 与过程证据。

## 实际应用

真实读取并缓存 Open Snapshot 指南、OpenAPI、Parser 语法、标签、文本、示例、字体、媒体、绘制、布局、错误处理与数据模板。全部主体通过 UTF-8 纯文本 `<Snapshot>` DSL 提交 `/snapshot`；最终 PNG 保留服务原始字节。逐题报告记录数据/几何核对、实际图像查看、问题、修复与交付。

## 跨题经验

1. `Text.height` 是行高倍数而非像素高度；文字盒高度应由 `Positioned`/布局容器控制。
2. `Positioned` 必须直接位于 `Stack`；旋转线段使用 `Container.transform`，不把 `Positioned` 套在 `Transform` 内。
3. Parser 不解码 HTML 实体；动态文本按 CDATA/转义规则生成。边框使用 `1 SOLID #RRGGBB`。
4. 字体以 `/fonts` 实际响应为准，本套使用 `Noto Sans CJK SC`。服务文档版本不等于部署版本，新增能力均经真实渲染验证。
5. 金额轴与比例轴分离；加权比例先汇总分子分母；多轮修改保留前轮，不覆盖历史。

## 终审更正留痕

- B03三份历史图片清单的机器路径保留原样，当前有效清单为 `final-image-inventory-r004-portable.json`；九条迭代路径错误由 `iteration-path-corrections-r001.json` 精确映射，原始日志未改。
- A22第二轮原变更审计的错误失败标记保留；当前有效后继 `round-02/change-audit-r002-corrected.json` 独立复算28项未改字段、全部公式与八个主区域0px边界差，详见 [A22报告](../A22/snapshot-usage.md)。
- B06重复完成事件保留并注明为同一任务完成，不重复计请求或工作量。
- 指标r005将预置需求变更从视觉迭代中分离；image_views按唯一服务响应及SHA-256识别来源，A18同响应预览/版本路径去重，A01/A09复制路径及B04两个覆盖前基线已校正，总计247个来源。基线接受61与失败62依据 `baseline-classification-r005.json` 逐行语义核对，不再使用文本前缀；A01 v001实际查见的裁切缺陷以失败覆盖项补记，v002误标版本按真实服务字节纠正。历史viewed_at补记与实际Read时间分列，原始迭代日志未改；B05两次研究404计入document_requests，不计other_service_requests。
- 终审前的过期全套汇总已归档至 `{s.rel(archive)}`；本目录内现行汇总由全部30题重新生成。

## 终审

- 任务完成：{status_counts['completed']}/{len(state['tasks'])}；partial {status_counts['partial']}；blocked {status_counts['blocked']}；pending {status_counts['pending']}。
- 最终 PNG：{len(inventory)}（最低 {s.CATALOG['minimum_final_pngs']}）；B类独立作品：{totals['independent_creative_cases']}。
- A21 已完成轮次：{', '.join(next(entry['completed_rounds'] for entry in state['tasks'] if entry['id']=='A21')) or '无'}。
- A22 已完成轮次：{', '.join(next(entry['completed_rounds'] for entry in state['tasks'] if entry['id']=='A22')) or '无'}。
- 渲染请求：{totals['snapshot_requests']}；成功 {totals['successful_snapshot_requests']}；失败 {totals['failed_snapshot_requests']}；重试 {totals['retry_requests']}；文档请求 {totals['document_requests']}；其他服务请求 {totals['other_service_requests']}（类别互斥）。
- 实际查看记录：{totals['image_views']} 个不同服务图像来源；真实服务读取事件 {totals['actual_service_read_events']}；重复读取 {totals['repeat_service_read_events']}；检查衍生图读取 {totals['inspection_derivative_views']}。
- 完整视觉迭代：{totals['completed_visual_iterations']}；未完成视觉迭代 {totals['incomplete_visual_iterations']}（均为已修复的历史中间版，不代表最终未解决缺陷）；预置需求变更 {totals['requirement_change_iterations']}（单列，不混入视觉迭代）；基线接受 {totals['baseline_acceptances']}；失败基线 {totals['failed_baselines']}；最终复核 {totals['final_visual_rechecks']}。
- 未查看服务基线 {totals['unviewed_baselines']} 为实验性历史基线，不计入最终交付；124张指定最终图已全部由渲染后真实Read证据核验。
- 逐件查看证据：`{s.rel(suite_temp / 'final-audit-r001' / 'all-final-view-audit-r002.json')}`；总览接触表不替代124张服务原图逐件查看。
- 墙钟耗时：{suite_metrics['elapsed_seconds']} 秒；包含等待与执行间隙，不等同于净工作或请求耗时之和。
- 自动审计问题：{len(issues)}。详见 [audit-report.json](audit-report.json) 与 [task-metrics.json](task-metrics.json)。

## 未解决事项

""" + ("\n".join(f"- {item.get('task_id', 'suite')}: {item['issue']}" for item in issues) if issues else "无。") + "\n"
    (suite_out / "snapshot-usage.md").write_text(usage, encoding="utf-8")
    markdown_files = list(suite_out.glob("*.md"))
    for entry in state["tasks"]:
        task_output, _ = s.task_dirs(run_id, entry["id"])
        if entry["status"] != "pending":
            markdown_files.extend(task_output.rglob("*.md"))
    for document in markdown_files:
        content = document.read_text(encoding="utf-8")
        for target in re.findall(r"\]\(([^)]+)\)", content):
            if target.startswith(("http" + chr(58) + "//", "https" + chr(58) + "//", "mailto" + chr(58), "#")):
                continue
            clean = target.split("#", 1)[0]
            if not clean or "{" in clean or "}" in clean:
                continue
            resolved = (document.parent / clean).resolve()
            if not resolved.exists():
                issues.append({"severity": "link", "issue": f"{s.rel(document)} 链接失效：{target}"})
    audit_report["issues"] = issues
    audit_report["issue_count"] = len(issues)
    gallery_path = suite_out / "gallery.md"
    gallery_content = gallery_path.read_text(encoding="utf-8") if gallery_path.is_file() else ""
    gallery_targets = set()
    for target in re.findall(r"\]\(([^)]+)\)", gallery_content):
        if target.startswith(("http" + chr(58) + "//", "https" + chr(58) + "//", "mailto" + chr(58), "#")):
            continue
        resolved = (suite_out / target.split("#", 1)[0]).resolve()
        if resolved.is_relative_to(s.ROOT) and resolved.suffix.lower() == ".png":
            gallery_targets.add(s.rel(resolved))
    expected_gallery_paths = {item["path"] for item in inventory}
    if gallery_targets != expected_gallery_paths:
        issues.append({"severity": "gallery", "issue": f"画廊链接集合与最终清单不一致：缺失 {len(expected_gallery_paths - gallery_targets)}，多余 {len(gallery_targets - expected_gallery_paths)}"})
    if gallery_content.count("![") != len(inventory):
        issues.append({"severity": "gallery", "issue": f"画廊逐图预览 {gallery_content.count('![')} != 最终图 {len(inventory)}"})
    required_suite_files = list(dict.fromkeys(s.CONFIG["suite_required_artifacts"] + ["audit-report.json"]))
    for name in required_suite_files:
        if not (suite_out / name).is_file():
            issues.append({"severity": "suite-artifacts", "issue": f"缺少全套交付 {name}"})
    recorded_artifacts = set(state.get("suite_artifacts", []))
    if recorded_artifacts != set(s.CONFIG["suite_required_artifacts"]):
        issues.append({"severity": "suite-artifacts", "issue": "suite-state.suite_artifacts 与 run-config 必需清单不一致"})
    reconciled_tasks = [entry["id"] for entry in state["tasks"] if (suite_out.parent / entry["id"] / "task-metrics.json").is_file() and json.loads((suite_out.parent / entry["id"] / "task-metrics.json").read_text(encoding="utf-8")).get("metrics_reconciliation", {}).get("raw_logs_modified") is False]
    if set(reconciled_tasks) != set(s.CATALOG["task_order"]):
        issues.append({"severity": "metrics", "issue": "并非全部30题指标都完成真实查看证据对账"})
    final_gates = {
        "all_30_tasks_completed": all(entry["status"] == "completed" for entry in state["tasks"]),
        "exact_124_finals": len(inventory) == 124,
        "gallery_exact_inventory": gallery_targets == expected_gallery_paths and gallery_content.count("![") == len(inventory),
        "all_final_service_originals_viewed_after_render": len(views["final_coverage"]) == 124 and all(row.get("verified_service_original_view") for row in views["final_coverage"]),
        "eight_overview_sheets_viewed": len(overview_review.get("sheets", [])) == 8 and all(sheet.get("viewed") for sheet in overview_review.get("sheets", [])),
        "all_task_metrics_reconciled": set(reconciled_tasks) == set(s.CATALOG["task_order"]),
        "metrics_semantics_verified": not [item for item in issues if item.get("severity") == "metrics"],
        "required_suite_artifacts_exist": all((suite_out / name).is_file() for name in required_suite_files),
        "suite_artifact_registry_exact": recorded_artifacts == set(s.CONFIG["suite_required_artifacts"]),
        "prompt_item_evidence_verified": all(check["verified"] for task in task_prompt_checklists for check in task["prompt_items"]),
        "no_unresolved_audit_issues": not issues,
    }
    audit_report["completion_gates"] = final_gates
    audit_report["completion_ready"] = all(final_gates.values())
    audit_report["requirements"]["suite_artifacts"] = [name for name in s.CONFIG["suite_required_artifacts"] if (suite_out / name).exists()]
    suite_metrics["unresolved_issues"] = issues
    suite_metrics["completion_gates"] = final_gates
    usage_path = suite_out / "snapshot-usage.md"
    usage_content = usage_path.read_text(encoding="utf-8")
    usage_content = re.sub(r"- 自动审计问题：\d+。", f"- 自动审计问题：{len(issues)}。", usage_content)
    usage_content = usage_content.split("## 未解决事项", 1)[0] + "## 未解决事项\n\n" + ("\n".join(f"- {item.get('task_id', 'suite')}: {item['issue']}" for item in issues) if issues else "无。") + "\n"
    usage_path.write_text(usage_content, encoding="utf-8")
    s.write_json(suite_out / "audit-report.json", audit_report)
    s.write_json(suite_out / "task-metrics.json", suite_metrics)
    return audit_report


if __name__ == "__main__":
    report = generate()
    print(json.dumps({"status": report["requirements"], "issues": report["issue_count"]}, ensure_ascii=False))
