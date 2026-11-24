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
for task_id in ("A01", "A07", "A08", "B03", "B04", "B05", "B06"):
    rows = sk.read_jsonl(SUITE_TEMP.parent / task_id / "iterations.jsonl")
    patterns = Counter(
        (row.get("observable_issues", ""), row.get("review_and_comparison", ""))
        for row in rows if "待视觉检查" in row.get("observable_issues", "")
    )
    print(task_id, len(patterns))
    for (issues, review), count in patterns.most_common():
        print(count, json.dumps({"issues": issues, "review": review}, ensure_ascii=False))
