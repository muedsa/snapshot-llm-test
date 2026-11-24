from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import suitekit as sk

RUN, SUITE_OUT, SUITE_TEMP = sk.init_suite()
RUN_TEMP = SUITE_TEMP.parent
audit = json.loads((BASE / "all-final-view-audit-r002.json").read_text(encoding="utf-8"))
service_hashes = set()
for task_id in [f"A{i:02d}" for i in range(1, 25)] + [f"B{i:02d}" for i in range(1, 7)]:
    for row in sk.read_jsonl(RUN_TEMP / task_id / "requests.jsonl"):
        if row.get("request_type") == "render" and row.get("http_status") == 200:
            response = ROOT / row["response_file"]
            if response.is_file():
                service_hashes.add(hashlib.sha256(response.read_bytes()).hexdigest())

by_task = defaultdict(list)
for event in audit["events"]:
    event["kind"] = "service_image" if event["sha256"] in service_hashes else "inspection_derivative"
    by_task[event["task_id"]].append(event)

rows = []
for task_id in [f"A{i:02d}" for i in range(1, 25)] + [f"B{i:02d}" for i in range(1, 7)]:
    events = by_task[task_id]
    service = [event for event in events if event["kind"] == "service_image"]
    derivatives = [event for event in events if event["kind"] == "inspection_derivative"]
    iterations = sk.read_jsonl(RUN_TEMP / task_id / "iterations.jsonl")
    placeholder_ids = {
        row["iteration_id"] for row in iterations
        if "待视觉检查" in row.get("observable_issues", "")
        and row.get("review_and_comparison") in ("尚未完成视觉复核", "无前版；等待完整查看", "基线", "待实际打开试验图后记录", "待查看后与全尺寸比较")
    }
    rows.append({
        "task_id": task_id,
        "actual_service_read_events": len(service),
        "unique_service_image_opens": len(set(event["image_path"] for event in service)),
        "repeat_service_read_events": len(service) - len(set(event["image_path"] for event in service)),
        "derivative_read_events": len(derivatives),
        "unique_derivative_opens": len(set(event["image_path"] for event in derivatives)),
        "total_png_read_events": len(events),
        "placeholder_iteration_rows_excluded": len(placeholder_ids),
        "raw_iteration_rows": len(iterations),
        "raw_png_iteration_rows": sum(str(row.get("image_path", "")).lower().endswith(".png") for row in iterations),
        "nonplaceholder_png_iteration_rows": sum(str(row.get("image_path", "")).lower().endswith(".png") and row["iteration_id"] not in placeholder_ids for row in iterations),
    })
output = BASE / "view-metrics-reconciliation-r001.json"
sk.write_json(output, {
    "schema_version": 1,
    "run_id": RUN,
    "path_base": "suite_root",
    "created_at": sk.iso(),
    "definition": "image_views 统一为真实 Read 打开的不同服务 PNG 路径数；重复打开、检查衍生图和迭代占位行分列，不混算。",
    "source": sk.rel(BASE / "all-final-view-audit-r002.json"),
    "tasks": rows,
    "totals": {
        key: sum(row[key] for row in rows)
        for key in ("actual_service_read_events", "unique_service_image_opens", "repeat_service_read_events", "derivative_read_events", "unique_derivative_opens", "total_png_read_events", "placeholder_iteration_rows_excluded", "raw_iteration_rows", "raw_png_iteration_rows", "nonplaceholder_png_iteration_rows")
    },
})
for row in rows:
    print(json.dumps(row, ensure_ascii=False))
print(json.dumps({"totals": json.loads(output.read_text(encoding="utf-8"))["totals"]}, ensure_ascii=False))
