from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
RUN_ID = "20261124T113838+0800-aac601"
RUN_OUT = ROOT / "outputs" / RUN_ID
RUN_TEMP = ROOT / "tmp" / RUN_ID
sys.path.insert(0, str(ROOT / "tools"))
import suitekit as sk

state_path = RUN_OUT / "_suite" / "suite-state.json"
state = json.loads(state_path.read_text(encoding="utf-8"))
a22 = next(entry for entry in state["tasks"] if entry["id"] == "A22")
corrected = f"outputs/{RUN_ID}/A22/round-02/change-audit-r002-corrected.json"
review = f"outputs/{RUN_ID}/A22/final-review-r002.json"
assert (ROOT / corrected).is_file()
if corrected not in a22["artifacts"]:
    a22["artifacts"].append(corrected)
if review not in a22["visual_review_evidence"]:
    a22["visual_review_evidence"].append(review)

report_path = RUN_OUT / "A22" / "snapshot-usage.md"
backup = BASE / "a22-report-before-audit-correction.md"
if not backup.exists():
    shutil.copyfile(report_path, backup)
report = report_path.read_text(encoding="utf-8")
marker = "## 终审审计标记更正"
if marker not in report:
    report += f"""

{marker}

- 原始 `round-02/change-audit.json` 保留不覆盖，其中 `prior_corrections_and_rows_retained: false` 是错误标记：它把两项有意数据更正当成未保留字段。
- 当前有效审计为 [change-audit-r002-corrected.json](round-02/change-audit-r002-corrected.json)：从原始 CSV 独立复算，28项未改原始字段在round-01/02/03全部保留，两项允许变更精确应用，六个月公式、期间总量与八个主区域0px边界差全部通过。
- 该更正是审计记录修正，不改变任何最终PNG、DSL或业务数据，也不增加服务渲染请求。
"""
    report_path.write_text(report, encoding="utf-8")

final_review = json.loads((RUN_TEMP / "A22" / "final-review.json").read_text(encoding="utf-8"))
final_review.update({
    "schema_version": 2,
    "revision": "r002",
    "revision_of": "tmp/20261124T113838+0800-aac601/A22/final-review.json",
    "corrected_at": datetime.now().astimezone().isoformat(),
    "audit_correction": {
        "original": "outputs/20261124T113838+0800-aac601/A22/round-02/change-audit.json",
        "current": corrected,
        "reason": "原失败标记与独立复算和最终交付矛盾；原文件保留，当前审计以后继版本为准。",
        "unchanged_fields_verified": 28,
        "layout_regions_verified": 8,
    },
})
sk.write_json(ROOT / review, final_review)
sk.write_json(state_path, state)
sk.append_jsonl(RUN_TEMP / "_suite" / "events.jsonl", {
    "event_id": f"{RUN_ID}-a22-round02-audit-correction-r001",
    "at": sk.iso(),
    "event": "a22-round02-audit-correction-r001",
    "status": "completed",
    "artifacts": [corrected, review, "tmp/20261124T113838+0800-aac601/_suite/final-audit-r001/correct_a22_round02_audit.py"],
    "note": "保留错误历史标记，追加独立复算后继审计；未修改PNG、DSL、业务数据或原始请求/迭代日志。",
})
sk.checkpoint(RUN_ID, "a22-round02-audit-correction-r001")
print(json.dumps({"corrected_audit": corrected, "review": review, "state_updated": True}, ensure_ascii=False))
