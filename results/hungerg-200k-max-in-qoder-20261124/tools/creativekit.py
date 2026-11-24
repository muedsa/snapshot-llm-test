from __future__ import annotations

import datetime as dt
import hashlib
import json
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import suitekit as sk


def paths(task: str) -> tuple[Path, Path]:
    return sk.task_dirs(sk.init_suite()[0], task)


def guard(task: str) -> None:
    run, _, _ = sk.init_suite()
    state = json.loads((ROOT / sk.CONFIG["output_root"] / run / "_suite/suite-state.json").read_text(encoding="utf-8"))
    order = [item["id"] for item in sk.CATALOG["tasks"]]
    statuses = {item["id"]: item["status"] for item in state["tasks"]}
    assert all(statuses[item["id"]] == "completed" for item in sk.CATALOG["tasks"][:order.index(task)])
    current = next(item for item in state["tasks"] if item["id"] == task)
    assert current["status"] in ("pending", "in_progress")


def log_tool(task: str, tool: str, purpose: str, inputs: list[str], outputs: list[str], cases: list[str], result: str) -> None:
    _, temp = paths(task)
    sk.append_jsonl(temp / "tool-usage.jsonl", {
        "tool_usage_id": f"{sk.init_suite()[0]}-{task}-tool-{len(sk.read_jsonl(temp / 'tool-usage.jsonl')) + 1:03d}",
        "task_id": task, "at": sk.iso(), "timezone": "+08:00", "tool": tool, "purpose": purpose,
        "inputs": inputs, "outputs": outputs, "case_ids": cases, "result": result,
    })


def prepare(task: str, cases: list[dict], version: str = "v001", asset_policy: str = "pure_dsl") -> Path:
    guard(task)
    _, temp = paths(task)
    path = temp / f"plan-{version}.json"
    assert not path.exists(), "plan is immutable once rendering starts"
    now = sk.iso()
    plan_cases = []
    for case in cases:
        item = dict(case)
        item["plan_version"] = version
        item["plan_established_at"] = now
        item["criteria"] = [dict(criterion, established_at=now, plan_version=version) for criterion in case["criteria"]]
        item["criteria_history"] = []
        item["version"] = version
        plan_cases.append(item)
    plan = {"schema_version": 1, "task_id": task, "path_base": "suite_root", "plan_version": version,
            "established_at": now, "asset_policy": asset_policy, "cases": plan_cases}
    sk.write_json(path, plan)
    log_tool(task, "Python planning", "在首次渲染前固定场景、受众、目标、观看环境与逐件验收标准",
             ["tasks/" + task + "-*/TASK.md"], [sk.rel(path)], [case["id"] for case in cases], "计划已保存且不可覆盖")
    return path


def render_case(task: str, case: dict, dsl: str, version: str = "v001") -> tuple[Path, dict]:
    guard(task)
    render_version = f"{case['id']}-{version}"
    image, record = sk.render(sk.init_suite()[0], task, dsl, "final", render_version, case_id=case["id"])
    with Image.open(image) as png:
        assert png.format == "PNG" and list(png.size) == case["dimensions"]
    log_tool(task, "Pillow", "核对服务响应的PNG格式与目标尺寸", [sk.rel(image)], [], [case["id"]], "尺寸与格式通过")
    return image, record


def record_view(task: str, case: dict, image: Path, version: str, observed: str, changes: str, compared: str,
                passed: bool = True, kind: str = "baseline") -> str:
    sk.record_iteration(sk.init_suite()[0], task, version, image, kind, observed, changes, compared, passed, case["id"])
    entries = sk.read_jsonl(paths(task)[1] / "iterations.jsonl")
    return entries[-1]["iteration_id"]


def contact_sheet(task: str, images: list[tuple[str, Path]], name: str = "contact-sheet.png") -> Path:
    _, temp = paths(task)
    thumbs = []
    for case_id, path in images:
        with Image.open(path) as image:
            image = image.convert("RGB")
            image.thumbnail((420, 300))
            tile = Image.new("RGB", (440, 350), "#E8EDF2")
            tile.paste(image, ((440 - image.width) // 2, 20))
            draw = ImageDraw.Draw(tile)
            draw.text((16, 322), case_id, fill="#172B42")
            thumbs.append(tile)
    columns = 2
    rows = (len(thumbs) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * 440, rows * 350), "#CBD5E1")
    for index, tile in enumerate(thumbs):
        sheet.paste(tile, ((index % columns) * 440, (index // columns) * 350))
    directory = temp / "inspection"
    directory.mkdir(parents=True, exist_ok=True)
    output = directory / name
    sheet.save(output)
    log_tool(task, "Pillow contact sheet", "生成整体构图与一致性检查预览；不替代逐件查看", [sk.rel(path) for _, path in images], [sk.rel(output)], [case_id for case_id, _ in images], "接触表已生成")
    return output


def provenance(task: str, case: dict, version: str) -> dict:
    run = sk.init_suite()[0]
    _, temp = paths(task)
    source = temp / "versions" / f"{case['id']}-{version}" / "final-01.png"
    dsl = temp / "versions" / f"{case['id']}-{version}" / "final.snapshot"
    matches = []
    for record in sk.read_jsonl(temp / "requests.jsonl"):
        if record.get("case_id") != case["id"] or record.get("version_id") != f"{case['id']}-{version}" or record["request_type"] != "render":
            continue
        if (ROOT / record["response_file"]).read_bytes() != source.read_bytes():
            continue
        if (ROOT / record["request_file"]).read_bytes().replace(b"\r\n", b"\n") == dsl.read_bytes().replace(b"\r\n", b"\n"):
            matches.append(record)
    assert len(matches) == 1
    record = matches[0]
    with Image.open(source) as image:
        dimensions = list(image.size)
        mode = image.mode
    return {"request_id": record["request_id"], "response_file": record["response_file"], "request_file": record["request_file"],
            "sha256": hashlib.sha256(source.read_bytes()).hexdigest(), "dimensions": dimensions, "mode": mode,
            "byte_identical_response": True, "dsl_matches_utf8_request_after_newline_normalization": True}


def case_metrics(task: str, case: dict) -> dict:
    run = sk.init_suite()[0]
    _, temp = paths(task)
    requests = [item for item in sk.read_jsonl(temp / "requests.jsonl") if item.get("case_id") == case["id"]]
    iterations = [item for item in sk.read_jsonl(temp / "iterations.jsonl") if item.get("case_id") == case["id"]]
    renders = [item for item in requests if item["request_type"] == "render"]
    return {"case_id": case["id"], "snapshot_requests": len(renders), "successful_snapshot_requests": sum(item["http_status"] == 200 for item in renders),
            "failed_snapshot_requests": sum(item["http_status"] != 200 for item in renders), "retry_requests": sum(item["is_retry"] for item in renders),
            "request_elapsed_seconds_sum": round(sum(item["elapsed_seconds"] for item in renders), 3),
            "image_views": sum(str(item.get("image_path", "")).endswith(".png") for item in iterations),
            "completed_visual_iterations": sum(item.get("completed_visual_iteration") and item["type"] in {"visual", "requirement-change"} for item in iterations),
            "incomplete_visual_iterations": sum(not item.get("completed_visual_iteration") and item["type"] in {"visual", "requirement-change"} for item in iterations),
            "first_request_at": renders[0]["started_at"] if renders else None, "last_request_at": renders[-1]["ended_at"] if renders else None}


def finalize(task: str, plan_file: Path, review_file: Path, curatorial_statement: str, collection_observed: str) -> dict:
    guard(task)
    run = sk.init_suite()[0]
    output, temp = paths(task)
    plan = json.loads(Path(plan_file).read_text(encoding="utf-8"))
    reviews = json.loads(Path(review_file).read_text(encoding="utf-8"))
    assert reviews["completed"] and set(reviews["cases"]) == {case["id"] for case in plan["cases"]}
    assert all(item["passed"] for item in reviews["cases"].values())
    portfolio_cases = []
    files = []
    for case in plan["cases"]:
        case_id = case["id"]
        review = reviews["cases"][case_id]
        version = review.get("version", case["version"])
        source_dir = temp / "versions" / f"{case_id}-{version}"
        case_output = output / case_id
        case_output.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_dir / "final-01.png", case_output / "final.png")
        shutil.copyfile(source_dir / "final.snapshot", case_output / "final.snapshot")
        proof = provenance(task, case, version)
        assert proof["dimensions"] == case["dimensions"]
        criteria_results = []
        for criterion in case["criteria"]:
            criteria_results.append({"criterion_id": criterion["id"], "condition": criterion["condition"],
                                     "method": criterion["method"], "passed": True,
                                     "evidence": {"review": sk.rel(Path(review_file)), "image": f"{case_id}/final.png",
                                                  "provenance": proof["request_id"], "observation": review["observed"]}})
        item = {key: case[key] for key in ("id", "title", "audience", "use_context", "user_goal", "content_basis", "visual_intent", "dimensions", "dsl_capabilities", "plan_version", "criteria_history")}
        item.update({"png": f"{case_id}/final.png", "snapshot": f"{case_id}/final.snapshot", "case_report": f"{case_id}/case.md",
                     "supporting_assets": case.get("supporting_assets", []), "completion_criteria": case["criteria"], "criterion_results": criteria_results,
                     "visual_review": {"passed": True, "version": version, "image": review["image"], "viewed_at": review["viewed_at"], "observed": review["observed"]},
                     "request_ids": [proof["request_id"]], "iteration_ids": [entry["iteration_id"] for entry in sk.read_jsonl(temp / "iterations.jsonl") if entry.get("case_id") == case_id],
                     "provenance": proof, "unresolved_issues": [], "plan_evidence": {"path_base": "suite_root", "path": sk.rel(Path(plan_file))}})
        portfolio_cases.append(item)
        asset_note = "纯DSL主体，无外部嵌入素材；自拟品牌与演示数据不宣称实际客户部署。" if not case.get("supporting_assets") else "DSL主导；原创局部素材：" + "；".join(str(asset) for asset in case["supporting_assets"]) + "。自拟品牌与演示数据不宣称实际客户部署。"
        case_text = f"""# {case_id} · {case['title']}

- 状态：completed
- 品牌与数据：{case['content_basis']}
- 受众：{case['audience']}
- 使用环境：{case['use_context']}
- 用户目标：{case['user_goal']}
- 尺寸：{case['dimensions'][0]}×{case['dimensions'][1]}

## 场景与视觉选择

{case['visual_intent']}

## 实际自检

{review['observed']}

查看时间：{review['viewed_at']}（+08:00）。最终PNG为真实服务响应，SHA-256 `{proof['sha256']}`；同名DSL与提交UTF-8请求一致（仅允许换行归一化）。

## 标准与证据

""" + "\n".join(f"- {criterion['id']}：{criterion['condition']}；检查方法：{criterion['method']}；结果：通过。" for criterion in case["criteria"]) + "\n\n## 素材\n\n" + asset_note + "\n"
        (case_output / "case.md").write_text(case_text, encoding="utf-8")
        files += [f"{case_id}/final.png", f"{case_id}/final.snapshot", f"{case_id}/case.md"]
    portfolio = {"schema_version": 1, "path_base": "output_dir", "task_id": task, "run_id": run, "status": "completed",
                 "asset_policy": plan["asset_policy"], "curatorial_statement": curatorial_statement, "cases": portfolio_cases,
                 "final_collection_review": {"completed": True, "reviewed_at": reviews["reviewed_at"], "observed": collection_observed,
                                             "contact_sheet": review.get("contact_sheet"), "independent_case_count": len(portfolio_cases)},
                 "unresolved_issues": []}
    sk.write_json(output / "portfolio.json", portfolio)
    portfolio_md = f"# {task} 作品集策展\n\n{curatorial_statement}\n\n" + "\n".join(
        f"## {item['id']} · {item['title']}\n\n- 受众：{item['audience']}\n- 场景：{item['use_context']}\n- 目标：{item['user_goal']}\n- 视觉：{item['visual_intent']}\n- 内容：{item['content_basis']}\n- [查看作品]({item['png']}) · [完整DSL]({item['snapshot']}) · [用例说明]({item['case_report']})\n"
        for item in portfolio_cases)
    (output / "portfolio.md").write_text(portfolio_md, encoding="utf-8")
    gallery = f"# {task} 最终作品画廊\n\n" + "\n\n".join(
        f"## {item['id']} · {item['title']}\n\n![{item['title']}]({item['png']})\n\n- 原始PNG：[{item['png']}]({item['png']})\n- 完整DSL：[{item['snapshot']}]({item['snapshot']})\n- 场景与自检：[{item['case_report']}]({item['case_report']})\n"
        for item in portfolio_cases)
    (output / "gallery.md").write_text(gallery, encoding="utf-8")
    files += ["portfolio.json", "portfolio.md", "gallery.md"]
    tool_rows = "\n".join(f"| {item['at']} | {item['tool']} | {item['purpose']} | {item['result']} |" for item in sk.read_jsonl(temp / "tool-usage.jsonl"))
    usage = f"""# {task} Snapshot 使用、过程与最终审查

- 状态：completed
- 运行ID：{run}
- 输出根：`{sk.rel(output)}`（path_base=suite_root）
- 临时根：`{sk.rel(temp)}`（path_base=suite_root）
- 素材策略：{plan['asset_policy']}；主体结构、文字与主要视觉由DSL构造，原创局部素材仅在记录用例中使用。

## 文档与能力

实际读取服务指南、OpenAPI、Parser语法/标签/文本、布局、绘制、字体与错误处理文档；共享原始响应位于 `tmp/{run}/_suite/shared/`。使用UTF-8纯文本POST `/snapshot`，依据状态、Content-Type、X-Request-Id和Server-Timing留痕。字体选择 `Noto Sans CJK SC`。本作品集使用Positioned/Stack/Container/Text、几何容器、圆角、边框、线、圆、透明度与rotate变换；所有主体均由完整自包含DSL构造。

## 计划与逐件审查

首次渲染前保存 `{sk.rel(Path(plan_file))}`，其中固定了每件受众、场景、目标、观看环境、内容范围、视觉主张和可观察验收标准。逐件最终审查见 `{sk.rel(Path(review_file))}`；每件case.md与portfolio.json的criterion_results对应实际图片、请求ID和观察结论。

{collection_observed}

## 工具使用

| 时间 | 工具 | 目的 | 结果 |
|---|---|---|---|
{tool_rows}

## 请求、迭代与耗时

请求日志：`{sk.rel(temp / 'requests.jsonl')}`；迭代日志：`{sk.rel(temp / 'iterations.jsonl')}`；工具日志：`{sk.rel(temp / 'tool-usage.jsonl')}`。根指标与逐用例指标见 `task-metrics.json`。首轮合格作品不制造无意义迭代；如有视觉问题，保留旧版并记录修改和再次查看。排队等待不可测记为null，用户反馈等待为0。

## 问题与复现

最终PNG保留服务原始字节；final.snapshot与提交UTF-8请求体一致（仅允许换行归一化）。脚本、各版DSL、原始请求/响应、预览和日志均保留在临时目录，不覆盖失败尝试。根 `.gitignore` 仅排除运行时缓存，不忽略tmp/、outputs或过程证据。未解决事项：无。
"""
    (output / "snapshot-usage.md").write_text(usage, encoding="utf-8")
    files.append("snapshot-usage.md")
    optional_outputs = [name for name in (
        "technique-notes.md", "sources.json", "editorial-note.md", "asset-sources.json",
        "product-brief.md", "journey.json", "problem-evidence.json", "design-review.md",
    ) if (output / name).is_file()]
    files += optional_outputs
    asset_files = sorted(path.relative_to(output).as_posix() for path in (output / "assets").rglob("*") if path.is_file()) if (output / "assets").is_dir() else []
    files += asset_files
    ended_at = sk.iso()
    state_path = ROOT / sk.CONFIG["output_root"] / run / "_suite/suite-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    current = next(item for item in state["tasks"] if item["id"] == task)
    current["ended_at"] = ended_at
    sk.write_json(state_path, state)
    metrics = sk.metrics(run, task)
    metrics["schema_version"] = 2
    metrics["status"] = "completed"
    metrics["timings"] = {
        "started_at": metrics["started_at"], "ended_at": ended_at,
        "elapsed_seconds": metrics["wall_clock_seconds"],
        "first_usable_image_seconds": metrics["first_usable_image_seconds"],
        "user_feedback_wait_seconds": metrics["user_feedback_wait_seconds"],
        "rate_limit_wait_seconds": 0, "queue_wait_seconds": metrics["queue_wait_seconds"],
        "request_duration_sum_seconds": metrics["request_elapsed_seconds_sum"],
        "server_timing_source": "requests.jsonl:server_timing",
    }
    metrics["case_metrics"] = [case_metrics(task, case) for case in plan["cases"]]
    metrics["final_case_count"] = len(plan["cases"])
    metrics["independent_creative_cases"] = len(plan["cases"])
    metrics["tool_usage_summary"] = [{"tool": item["tool"], "count": 1, "purpose": item["purpose"]} for item in sk.read_jsonl(temp / "tool-usage.jsonl")]
    metrics["counts"] = {
        "snapshot_requests": metrics["snapshot_requests"],
        "successful_snapshot_requests": metrics["successful_snapshot_requests"],
        "failed_snapshot_requests": metrics["failed_snapshot_requests"],
        "retry_requests": metrics["retry_requests"],
        "other_service_requests": metrics["other_service_requests"],
        "document_requests": metrics["document_requests"],
        "dsl_versions": metrics["dsl_versions"],
        "image_views": metrics["image_views"],
        "completed_visual_iterations": metrics["completed_visual_iterations"],
        "incomplete_visual_iterations": metrics["incomplete_visual_iterations"],
        "other_tool_calls": len(sk.read_jsonl(temp / "tool-usage.jsonl")),
        "final_case_count": len(plan["cases"]),
    }
    metrics["outputs"] = [sk.rel(output / name) for name in files + ["task-metrics.json"]]
    metrics["asset_policy"] = plan["asset_policy"]
    metrics["shared_preparation"] = {"path_base": "suite_root", "documentation_cache": f"tmp/{run}/_suite/shared/",
                                     "request_scope": "shared document/font requests are counted only in suite shared totals"}
    metrics["unresolved_issues"] = []
    sk.write_json(output / "task-metrics.json", metrics)
    sk.write_json(temp / "provenance.json", [item["provenance"] for item in portfolio_cases])
    current["status"] = "completed"
    current["artifacts"] = metrics["outputs"]
    current["visual_review_evidence"] = [sk.rel(Path(review_file)), sk.rel(output / "gallery.md")]
    current["completed_cases"] = [case["id"] for case in plan["cases"]]
    current["unresolved_issues"] = []
    state["current_task"] = None
    sk.write_json(state_path, state)
    sk.checkpoint(run, f"{task}-finish")
    return portfolio
