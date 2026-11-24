from __future__ import annotations

import json
import os
import re
import sys
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
    call["image_path"] = normalized
    call.update(results.get(call_id, {"result_at": None, "result_line": None, "is_error": None}))
    events.append(call)
events.sort(key=lambda item: (item["called_at"] or "", item["image_path"]))

request_rows = []
for task_id in ("B01", "B02"):
    request_rows.extend(sk.read_jsonl(RUN_OUT / task_id / "requests.jsonl"))
request_rows.sort(key=lambda item: item.get("requested_at") or item.get("at") or "")

report = {
    "schema_version": 1,
    "run_id": RUN,
    "generated_at": sk.iso(),
    "path_base": "suite_root",
    "purpose": "从真实会话工具记录恢复 B01/B02 PNG Read 调用时间；不修改原始迭代日志，不把补记时间伪装为历史时间。",
    "transcript_selection": "USERPROFILE 下当前项目 slug 中最大的 JSONL 会话文件",
    "read_call_count": len(events),
    "events": events,
    "snapshot_request_times": [
        {
            "task_id": row.get("task_id"),
            "request_id": row.get("request_id"),
            "at": row.get("requested_at") or row.get("at"),
            "status": row.get("status"),
            "image_path": row.get("image_path"),
        }
        for row in request_rows
    ],
    "limitations": "Read 工具调用与结果时间可证明查看动作顺序；不能单凭结果时间推断人工视觉判断质量。",
}
output = BASE / "view-chronology-r001.json"
sk.write_json(output, report)
print(json.dumps({"read_calls": len(events), "requests": len(request_rows), "output": sk.rel(output)}, ensure_ascii=False))
