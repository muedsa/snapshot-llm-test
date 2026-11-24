from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import suitekit as sk

RUN, SUITE_OUT, SUITE_TEMP = sk.init_suite()
RUN_OUT = SUITE_OUT.parent
RUN_TEMP = SUITE_TEMP.parent
inventory = json.loads((BASE / "final-inventory-r001.json").read_text(encoding="utf-8"))
summary = []
for task_id in [f"A{i:02d}" for i in range(1, 25)] + [f"B{i:02d}" for i in range(1, 7)]:
    rows = sk.read_jsonl(RUN_TEMP / task_id / "iterations.jsonl")
    metrics = json.loads((RUN_OUT / task_id / "task-metrics.json").read_text(encoding="utf-8"))
    placeholder = [row for row in rows if "待视觉检查" in str(row.get("observable_issues", ""))]
    actual_rows = [row for row in rows if row not in placeholder]
    paths = [row.get("image_path", "") for row in actual_rows]
    existing = [path for path in paths if (ROOT / path).is_file()]
    missing = sorted(set(path for path in paths if not (ROOT / path).is_file()))
    finals = [item for item in inventory["items"] if item["task_id"] == task_id]
    final_hashes = {item["sha256"] for item in finals}
    viewed_final_hashes = set()
    import hashlib
    for path in existing:
        if path.lower().endswith(".png"):
            viewed_final_hashes.add(hashlib.sha256((ROOT / path).read_bytes()).hexdigest())
    summary.append({
        "task_id": task_id,
        "rows": len(rows),
        "types": dict(Counter(row.get("type") for row in rows)),
        "placeholder_rows": len(placeholder),
        "nonplaceholder_rows": len(actual_rows),
        "unique_nonplaceholder_paths": len(set(existing)),
        "duplicate_path_rows": len(existing) - len(set(existing)),
        "missing_path_rows": len(paths) - len(existing),
        "missing_paths": missing,
        "reported_image_views": metrics.get("image_views"),
        "reported_completed": metrics.get("completed_visual_iterations"),
        "reported_incomplete": metrics.get("incomplete_visual_iterations"),
        "reported_final_rechecks": metrics.get("final_visual_rechecks"),
        "final_count": len(finals),
        "finals_seen_by_hash": len(final_hashes & viewed_final_hashes),
    })
sk.write_json(BASE / "metrics-analysis-r001.json", {"run_id": RUN, "path_base": "suite_root", "tasks": summary})
for row in summary:
    print(json.dumps(row, ensure_ascii=False))
