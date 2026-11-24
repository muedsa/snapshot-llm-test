from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
RUN, SUITE_OUT, SUITE_TEMP = sk = None, None, None
sys.path.insert(0, str(ROOT / "tools"))
import suitekit as sk

RUN, SUITE_OUT, SUITE_TEMP = sk.init_suite()
RUN_OUT = SUITE_OUT.parent
project = Path.cwd().resolve()
slug = project.drive.replace(":", "") + "--" + "-".join(project.parts[1:])
transcripts = list((Path(os.environ["USERPROFILE"]) / ".qoder-cn" / "projects" / slug).glob("*.jsonl"))
if not transcripts:
    raise RuntimeError("No session transcript found")
transcript = max(transcripts, key=lambda path: path.stat().st_size)

calls = {}
results = {}
targeted = re.compile(r"[\\/](B01|B02)[\\/].*\.png(?:$|[\\/])", re.IGNORECASE)
with transcript.open(encoding="utf-8") as handle:
    for line_number, line in enumerate(handle, 1):
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        message = obj.get("message", {})
        content = message.get("content", [])
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "tool_use" and block.get("name") == "Read":
                file_path = str(block.get("input", {}).get("file_path", ""))
                if targeted.search(file_path):
                    call_id = block.get("id")
                    calls[call_id] = {
                        "tool_use_id": call_id,
                        "transcript_line": line_number,
                        "called_at": obj.get("timestamp"),
                        "task_id": targeted.search(file_path).group(1).upper(),
                        "recorded_path": file_path,
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
    raw = call.pop("recorded_path")
    normalized = raw.replace("\\", "/")
    marker = f"/{RUN}/"
    if marker in normalized:
        normalized = normalized.split(marker, 1)[1]
    elif normalized.startswith(str(ROOT).replace("\\", "/") + "/"):
        normalized = normalized[len(str(ROOT).replace("\\", "/")) + 1 :]
    if normalized.startswith(("B01/", "B02/")):
        normalized = f"tmp/{RUN}/" + normalized
    call["image_path"] = normalized
    call.update(results.get(call_id, {"result_at": None, "result_line": None, "is_error": None}))
    events.append(call)
events.sort(key=lambda item: (item["called_at"] or "", item["image_path"]))

request_rows = []
for task_id in ("B01", "B02"):
    request_rows.extend(sk.read_jsonl(SUITE_TEMP.parent / task_id / "requests.jsonl"))
request_rows.sort(key=lambda item: item.get("started_at") or "")

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def utc(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(datetime.now().astimezone().tzinfo) if value else None


for event in events:
    image_path = ROOT / event["image_path"]
    event["sha256"] = sha256(image_path)
    event["kind"] = "inspection_derivative" if "inspection" in event["image_path"] else "service_image"

render_by_hash = {}
for row in request_rows:
    response = ROOT / row["response_file"]
    digest = sha256(response) if response.is_file() else None
    row["response_sha256"] = digest
    row["ended_at_utc"] = datetime.fromisoformat(row["ended_at"].replace("Z", "+00:00")).astimezone().isoformat().replace("+00:00", "Z") if row.get("ended_at") else None
    row["started_at_utc"] = datetime.fromisoformat(row["started_at"].replace("Z", "+00:00")).astimezone().isoformat().replace("+00:00", "Z") if row.get("started_at") else None
    if row.get("http_status") == 200 and digest:
        render_by_hash.setdefault(digest, []).append(row)

inventory = json.loads((BASE / "final-inventory-r001.json").read_text(encoding="utf-8"))
final_coverage = []
for item in inventory["items"]:
    if item["task_id"] not in ("B01", "B02"):
        continue
    digest = item["sha256"]
    final_render = render_by_hash.get(digest, [])
    render = final_render[-1] if final_render else None
    observed = [
        event for event in events
        if event["kind"] == "service_image"
        and event["sha256"] == digest
        and render
        and datetime.fromisoformat(event["result_at"].replace("Z", "+00:00")) >= datetime.fromisoformat(render["ended_at_utc"].replace("Z", "+00:00"))
    ]
    final_coverage.append({
        "task_id": item["task_id"],
        "case_id": item["case_id"],
        "png": item["png"],
        "sha256": digest,
        "render_request_id": render.get("request_id") if render else None,
        "render_ended_at": render.get("ended_at") if render else None,
        "view_tool_use_ids": [event["tool_use_id"] for event in observed],
        "view_result_times": [event["result_at"] for event in observed],
        "verified": bool(render and observed),
    })

remediation_pairs = [
    ("B01", "case-03", "v001", "v002"),
    ("B01", "case-05", "v001", "v002"),
    ("B01", "case-08", "v001", "v002"),
    ("B02", "case-04", "v001", "v002"),
    ("B02", "case-08", "v001", "v002"),
    ("B02", "case-09", "v001", "v002"),
]
sequence_checks = []
for task_id, case_id, old_version, new_version in remediation_pairs:
    old_path = f"tmp/{RUN}/{task_id}/versions/{case_id}-{old_version}/final-01.png"
    new_path = f"tmp/{RUN}/{task_id}/versions/{case_id}-{new_version}/final-01.png"
    old_view = next(event for event in events if event["image_path"] == old_path)
    new_view = next(event for event in events if event["image_path"] == new_path)
    old_render = render_by_hash.get(old_view["sha256"], [None])[-1]
    new_render = render_by_hash.get(new_view["sha256"], [None])[-1]
    if old_render is None or new_render is None:
        raise RuntimeError(f"Render response hash not found for {task_id}/{case_id}: old={old_view['sha256']}, new={new_view['sha256']}")
    times = {
        "old_render_ended": datetime.fromisoformat(old_render["ended_at_utc"].replace("Z", "+00:00")),
        "old_view_result": datetime.fromisoformat(old_view["result_at"].replace("Z", "+00:00")),
        "new_render_started": datetime.fromisoformat(new_render["started_at_utc"].replace("Z", "+00:00")),
        "new_render_ended": datetime.fromisoformat(new_render["ended_at_utc"].replace("Z", "+00:00")),
        "new_view_result": datetime.fromisoformat(new_view["result_at"].replace("Z", "+00:00")),
    }
    ordered = times["old_render_ended"] < times["old_view_result"] < times["new_render_started"] <= times["new_render_ended"] < times["new_view_result"]
    sequence_checks.append({
        "task_id": task_id,
        "case_id": case_id,
        "old_view_tool_use_id": old_view["tool_use_id"],
        "new_view_tool_use_id": new_view["tool_use_id"],
        "new_render_request_id": new_render["request_id"],
        "times_utc": {key: value.isoformat().replace("+00:00", "Z") for key, value in times.items()},
        "ordered": ordered,
    })

report = {
    "schema_version": 1,
    "run_id": RUN,
    "generated_at": sk.iso(),
    "path_base": "suite_root",
    "purpose": "从真实会话工具记录恢复 B01/B02 PNG Read 调用时间；不修改原始迭代日志，不把补记时间伪装为历史时间。",
    "transcript_selection": "USERPROFILE 下当前项目 slug 中最大的 JSONL 会话文件",
    "read_call_count": len(events),
    "events": events,
    "final_coverage": final_coverage,
    "verified_final_count": sum(item["verified"] for item in final_coverage),
    "remediation_sequence_checks": sequence_checks,
    "verified_remediation_sequence_count": sum(item["ordered"] for item in sequence_checks),
    "snapshot_request_times": [
        {
            "task_id": row.get("task_id"),
            "request_id": row.get("request_id"),
            "at": row.get("started_at"),
            "status": row.get("http_status"),
            "version_id": row.get("version_id"),
            "response_file": row.get("response_file"),
        }
        for row in request_rows
    ],
    "limitations": "Read 工具调用与结果时间可证明查看动作顺序；不能单凭结果时间推断人工视觉判断质量。",
}
output = BASE / "view-chronology-r002.json"
sk.write_json(output, report)
print(json.dumps({"read_calls": len(events), "requests": len(request_rows), "verified_finals": report["verified_final_count"], "verified_remediations": report["verified_remediation_sequence_count"], "output": sk.rel(output)}, ensure_ascii=False))
