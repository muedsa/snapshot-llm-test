from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import suitekit as sk

RUN, SUITE_OUT, SUITE_TEMP = sk.init_suite()
RUN_OUT = SUITE_OUT.parent
RUN_TEMP = SUITE_TEMP.parent
project = Path.cwd().resolve()
slug = project.drive.replace(":", "") + "--" + "-".join(project.parts[1:])
transcripts = list((Path(os.environ["USERPROFILE"]) / ".qoder-cn" / "projects" / slug).glob("*.jsonl"))
transcript = max(transcripts, key=lambda path: path.stat().st_size)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone()


calls = {}
results = {}
run_marker = f"/{RUN}/"
root_prefix = ROOT.as_posix() + "/"
with transcript.open(encoding="utf-8") as handle:
    for line_number, line in enumerate(handle, 1):
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        content = obj.get("message", {}).get("content", [])
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "tool_use" and block.get("name") == "Read":
                raw = str(block.get("input", {}).get("file_path", "")).replace("\\", "/")
                if not raw.lower().endswith(".png") or run_marker not in raw:
                    continue
                relative = "tmp/" + RUN + "/" + raw.split(run_marker, 1)[1] if "/tmp/" in raw else "outputs/" + RUN + "/" + raw.split(run_marker, 1)[1]
                call_id = block.get("id")
                calls[call_id] = {
                    "tool_use_id": call_id,
                    "called_at": obj.get("timestamp"),
                    "transcript_line": line_number,
                    "image_path": relative,
                }
            elif block.get("type") == "tool_result" and block.get("tool_use_id") in calls:
                call_id = block.get("tool_use_id")
                results[call_id] = {
                    "result_at": obj.get("timestamp"),
                    "result_line": line_number,
                    "is_error": bool(block.get("is_error")),
                }

events = []
for call_id, call in calls.items():
    call.update(results.get(call_id, {"result_at": None, "result_line": None, "is_error": None}))
    path = ROOT / call["image_path"]
    call["exists"] = path.is_file()
    call["sha256"] = digest(path) if path.is_file() else None
    call["task_id"] = call["image_path"].split(f"/{RUN}/", 1)[1].split("/", 1)[0]
    events.append(call)
events.sort(key=lambda item: (item["called_at"] or "", item["image_path"]))

requests = []
for task_id in [f"A{i:02d}" for i in range(1, 25)] + [f"B{i:02d}" for i in range(1, 7)]:
    requests.extend(sk.read_jsonl(RUN_TEMP / task_id / "requests.jsonl"))
render_by_hash = {}
for row in requests:
    if row.get("request_type") != "render" or row.get("http_status") != 200:
        continue
    response = ROOT / row["response_file"]
    if response.is_file():
        render_by_hash.setdefault(digest(response), []).append(row)

inventory = json.loads((BASE / "final-inventory-r001.json").read_text(encoding="utf-8"))
coverage = []
for item in inventory["items"]:
    exact = [event for event in events if event["image_path"] == item["png"] and not event["is_error"]]
    same_bytes = [event for event in events if event["sha256"] == item["sha256"] and not event["is_error"]]
    render = render_by_hash.get(item["sha256"], [None])[-1]
    ordered_exact = [
        event for event in exact
        if render and event["result_at"] and utc(event["result_at"]) >= utc(render["ended_at"])
    ]
    ordered_same_bytes = [
        event for event in same_bytes
        if render and event["result_at"] and utc(event["result_at"]) >= utc(render["ended_at"])
    ]
    coverage.append({
        "task_id": item["task_id"],
        "case_id": item["case_id"],
        "group": item["group"],
        "png": item["png"],
        "sha256": item["sha256"],
        "exact_final_path_read_count": len(exact),
        "same_bytes_read_count": len(same_bytes),
        "exact_reads_after_render": len(ordered_exact),
        "same_bytes_reads_after_render": len(ordered_same_bytes),
        "same_bytes_tool_use_ids": [event["tool_use_id"] for event in ordered_same_bytes],
        "verified_exact_final_view": bool(ordered_exact),
        "verified_service_original_view": bool(ordered_same_bytes),
    })

by_task = Counter(event["task_id"] for event in events)
report = {
    "schema_version": 1,
    "run_id": RUN,
    "path_base": "suite_root",
    "generated_at": sk.iso(),
    "purpose": "从真实会话 Read 工具调用/结果核验每张指定最终输出路径是否在对应服务渲染完成后被实际打开。",
    "transcript_selection": "USERPROFILE 下当前项目 slug 中最大的 JSONL 会话文件",
    "read_event_count": len(events),
    "unique_png_paths_read": len(set(event["image_path"] for event in events)),
    "read_events_by_task": dict(sorted(by_task.items())),
    "missing_read_files": [event["image_path"] for event in events if not event["exists"]],
    "final_coverage": coverage,
    "verified_final_count": sum(item["verified_service_original_view"] for item in coverage),
    "verified_exact_final_path_count": sum(item["verified_exact_final_view"] for item in coverage),
    "unverified_finals": [item["png"] for item in coverage if not item["verified_service_original_view"]],
    "events": events,
    "limitations": "Read 工具结果证明图片被打开并进入会话；视觉质量结论仍以各题观察、计算和最终复查记录为准。",
}
output = BASE / "all-final-view-audit-r002.json"
sk.write_json(output, report)
print(json.dumps({"read_events": len(events), "unique_paths": report["unique_png_paths_read"], "verified_finals": report["verified_final_count"], "unverified": len(report["unverified_finals"]), "output": sk.rel(output)}, ensure_ascii=False))
