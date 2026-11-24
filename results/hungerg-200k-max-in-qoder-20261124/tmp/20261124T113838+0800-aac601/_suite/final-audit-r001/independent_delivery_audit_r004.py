from __future__ import annotations
import datetime as dt
import hashlib
import json
import re
import struct
import sys
from collections import Counter
from pathlib import Path
BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import suitekit as sk
RUN, SUITE, TEMP = sk.init_suite()
OUT = SUITE.parent
RTEMP = TEMP.parent
TASKS = [f"A{i:02d}" for i in range(1, 25)] + [f"B{i:02d}" for i in range(1, 7)]
issues = []
checks = []
def check(name, passed, detail):
    checks.append({"check": name, "passed": bool(passed), "detail": detail})
    if not passed:
        issues.append({"check": name, "detail": detail})
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def png_size(path):
    data = path.read_bytes()
    return struct.unpack(">II", data[16:24]) if data[:8] == b"\x89PNG\r\n\x1a\n" and len(data) >= 24 else None
def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
state = json.loads((SUITE / "suite-state.json").read_text(encoding="utf-8"))
catalog = sk.CATALOG
check("30题顺序与状态", [x["id"] for x in state["tasks"]] == catalog["task_order"] and all(x["status"] == "completed" for x in state["tasks"]), [x["id"] for x in state["tasks"]])
checkpoints = sorted((TEMP / "checkpoints").glob("state-*.json"))
check("启动事件与连续检查点", (TEMP / "events.jsonl").is_file() and len(checkpoints) >= 61 and [int(x.stem.split("-")[-1]) for x in checkpoints] == list(range(1, len(checkpoints) + 1)), {"events": len(read_jsonl(TEMP / "events.jsonl")), "checkpoints": len(checkpoints)})
view_audit = json.loads((BASE / "all-final-view-audit-r002.json").read_text(encoding="utf-8"))
viewed = {x["sha256"]: x for x in view_audit["final_coverage"] if x.get("verified_service_original_view")}
render_ends = {}
for task_id in TASKS:
    for row in read_jsonl(RTEMP / task_id / "requests.jsonl"):
        if row.get("request_type") == "render" and row.get("http_status") == 200:
            response = ROOT / row["response_file"]
            if response.is_file():
                render_ends.setdefault(sha(response), []).append(dt.datetime.fromisoformat(row["ended_at"]))
b04_rows = read_jsonl(RTEMP / "B04" / "requests.jsonl")
b04_by_id = {row["request_id"]: row for row in b04_rows}
recovered_chronology = {}
for recovery in json.loads((RTEMP / "B04" / "inspection" / "baseline-recovery.json").read_text(encoding="utf-8")):
    original = b04_by_id[recovery["request_id"]]
    later = sorted([row for row in b04_rows if row.get("case_id") == original["case_id"] and row.get("http_status") == 200 and dt.datetime.fromisoformat(row["started_at"]) > dt.datetime.fromisoformat(original["ended_at"])], key=lambda row: row["started_at"])
    if later:
        for event in view_audit["events"]:
            if event["task_id"] == "B04" and event["image_path"] == f'tmp/{RUN}/B04/versions/{original["version_id"]}/final-01.png':
                read_time = dt.datetime.fromisoformat(event["result_at"].replace("Z", "+00:00"))
                if dt.datetime.fromisoformat(original["ended_at"]) <= read_time < dt.datetime.fromisoformat(later[0]["started_at"]):
                    recovered_chronology[event["tool_use_id"]] = dt.datetime.fromisoformat(original["ended_at"])
chronology_failures = []
for event in view_audit["events"]:
    digest = event.get("sha256")
    if digest in render_ends and event.get("result_at") and not event.get("is_error"):
        read_time = dt.datetime.fromisoformat(event["result_at"].replace("Z", "+00:00"))
        ends = [recovered_chronology[event["tool_use_id"]]] if event["tool_use_id"] in recovered_chronology else render_ends[digest]
        if not any(read_time >= end for end in ends):
            chronology_failures.append(event["tool_use_id"])
check("服务图读取不早于渲染", not chronology_failures, chronology_failures)
overview = json.loads((BASE / "overview-review-manifest-v002.json").read_text(encoding="utf-8"))
check("124张最终图实际查看证据", len(viewed) == 123 and len(view_audit["final_coverage"]) == 124 and all(x.get("verified_service_original_view") for x in view_audit["final_coverage"]), {"coverage": len(view_audit["final_coverage"]), "unique_hashes": len(viewed)})
check("八张总览实际查看", len(overview.get("sheets", [])) == 8 and all(x.get("viewed") for x in overview["sheets"]), len(overview.get("sheets", [])))
inventory = []
for entry in state["tasks"]:
    task_id = entry["id"]
    output, temp = sk.task_dirs(RUN, task_id)
    spec = json.loads((ROOT / next(x for x in catalog["tasks"] if x["id"] == task_id)["task_spec"]).read_text(encoding="utf-8"))
    requests = read_jsonl(temp / "requests.jsonl")
    iterations = read_jsonl(temp / "iterations.jsonl")
    check(f"{task_id} 过程日志", all((temp / name).is_file() for name in spec.get("log_files", [])), spec.get("log_files", []))
    if task_id.startswith("B"):
        check(f"{task_id} 工具日志", (temp / "tool-usage.jsonl").is_file(), "tool-usage.jsonl")
    pairs = []
    for row in requests:
        if row.get("request_type") == "render" and row.get("http_status") == 200:
            request_path, response_path = ROOT / row["request_file"], ROOT / row["response_file"]
            if request_path.is_file() and response_path.is_file():
                pairs.append((sha(response_path), hashlib.sha256(request_path.read_bytes().replace(b"\r\n", b"\n")).hexdigest(), row["request_id"], row["response_file"]))
    if task_id.startswith("B"):
        portfolio = json.loads((output / "portfolio.json").read_text(encoding="utf-8"))
        cases = portfolio.get("cases", [])
        check(f"{task_id} 十件独立作品", len(cases) == 10 and len({x["id"] for x in cases}) == 10 and len({sha(output / x["png"]) for x in cases}) == 10, len(cases))
        finals = [(output / x["png"], x.get("title", x["id"]), None) for x in cases]
    else:
        finals = [(output / x["filename"], Path(x["filename"]).stem, (x["width"], x["height"])) for x in spec.get("required_outputs", []) if x["filename"].lower().endswith(".png")]
        if spec.get("round_count", 1) > 1:
            check(f"{task_id} 三轮顺序归档", entry.get("completed_rounds") == ["round-01", "round-02", "round-03"], entry.get("completed_rounds"))
    for png, title, expected_size in finals:
        dsl = png.with_suffix(".snapshot")
        if not png.is_file() or not dsl.is_file():
            issues.append({"check": f"{task_id} 配对", "detail": sk.rel(png)})
            continue
        digest = sha(png)
        normalized = hashlib.sha256(dsl.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        match = next((pair for pair in pairs if pair[0] == digest and pair[1] == normalized), None)
        size = png_size(png)
        check(f"{task_id}:{sk.rel(png)} 服务来源", match is not None, match[2] if match else None)
        check(f"{task_id}:{sk.rel(png)} 查看", digest in viewed, digest)
        if expected_size:
            check(f"{task_id}:{sk.rel(png)} 尺寸", size == expected_size, {"actual": size, "expected": expected_size})
        if task_id.startswith("A"):
            check(f"{task_id}:{sk.rel(png)} 纯DSL", re.search(rb"<Image(?:\s|>)", dsl.read_bytes()) is None, "Image absent")
        inventory.append({"task_id": task_id, "png": sk.rel(png), "snapshot": sk.rel(dsl), "sha256": digest, "size": size, "service_response": match[3] if match else None})
check("最终数量与轨迹", len(inventory) == 124 and sum(x["task_id"].startswith("A") for x in inventory) == 64 and sum(x["task_id"].startswith("B") for x in inventory) == 60, {"total": len(inventory), "A": sum(x["task_id"].startswith("A") for x in inventory), "B": sum(x["task_id"].startswith("B") for x in inventory)})
gallery = (SUITE / "gallery.md").read_text(encoding="utf-8")
png_targets = re.findall(r"!\[[^\]]*\]\(([^)]+\.png)\)", gallery)
check("画廊逐图覆盖", Counter(png_targets) == Counter("../" + x["task_id"] + "/" + (ROOT / x["png"]).relative_to(OUT / x["task_id"]).as_posix() for x in inventory), {"previews": len(png_targets), "inventory": len(inventory)})
link_count = 0
for document in list(SUITE.glob("*.md")) + [p for task_id in TASKS for p in (OUT / task_id).rglob("*.md")]:
    for target in re.findall(r"\]\(([^)]+)\)", document.read_text(encoding="utf-8")):
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        clean = target.split("#", 1)[0]
        if not clean or "{" in clean or "}" in clean:
            continue
        link_count += 1
        if not (document.parent / clean).resolve().exists():
            issues.append({"check": "Markdown相对链接", "detail": f"{sk.rel(document)} -> {target}"})
check("Markdown相对链接可访问", not [x for x in issues if x["check"] == "Markdown相对链接"], link_count)
required = sk.CONFIG["suite_required_artifacts"]
check("五份全套产物", all((SUITE / name).is_file() for name in required) and set(state.get("suite_artifacts", [])) == set(required), required)
ignore = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
check("缓存忽略规则", all(rule in ignore for rule in ("__pycache__/", "*.pyc", "*.pyo", ".pytest_cache/", ".mypy_cache/", ".ruff_cache/")) and not any(rule in ignore for rule in ("tmp/", "outputs/", "cache/", ".cache/", "*.log", "*.png", "*.snapshot", "*.json")), ignore)
started = dt.datetime.fromisoformat(state["started_at"])
late_inputs = []
for base in (ROOT / "tasks", ROOT / "templates"):
    for path in base.rglob("*"):
        if path.is_file() and dt.datetime.fromtimestamp(path.stat().st_mtime, started.tzinfo) > started:
            late_inputs.append(sk.rel(path))
check("题库与模板未在运行后改写", not late_inputs, late_inputs)
current_docs = [SUITE / name for name in ("index.md", "gallery.md", "snapshot-usage.md")] + [OUT / task_id / "snapshot-usage.md" for task_id in TASKS] + [OUT / task_id / "task-metrics.json" for task_id in TASKS]
hardcoded = []
for path in current_docs:
    if path.is_file() and re.search(r"(?:[A-Za-z]:\\|C:\\Users\\|/Users/|\\\\[^\\]+\\\\)", path.read_text(encoding="utf-8")):
        hardcoded.append(sk.rel(path))
check("现行报告无硬编码机器路径", not hardcoded, hardcoded)
metrics = json.loads((SUITE / "task-metrics.json").read_text(encoding="utf-8"))
counts = metrics["counts"]
check("指标汇总互斥且预期", counts["document_requests"] == 15 and counts["other_service_requests"] == 1 and counts["snapshot_requests"] == 304 and counts["image_views"] == 248 and counts["completed_visual_iterations"] == 86 and counts["incomplete_visual_iterations"] == 11 and counts["requirement_change_iterations"] == 9, counts)
check("指标时间口径", metrics.get("elapsed_time_note") and "等待" in metrics["elapsed_time_note"], metrics.get("elapsed_time_note"))
summary = {"run_id": RUN, "audited_at": sk.iso(), "path_base": "suite_root", "independent_of_suite_audit": True, "passed": not issues, "checks": checks, "issues": issues, "inventory": inventory, "local_links_checked": link_count, "scope_note": "本脚本独立核验交付结构、配对、查看证据、链接与路径；指标语义由另一独立复核从原始日志重算。"}
sk.write_json(BASE / "independent-delivery-audit-r004.json", summary)
print(json.dumps({"passed": summary["passed"], "checks": len(checks), "issues": issues, "finals": len(inventory), "links": link_count}, ensure_ascii=False))
if issues:
    raise SystemExit(1)
