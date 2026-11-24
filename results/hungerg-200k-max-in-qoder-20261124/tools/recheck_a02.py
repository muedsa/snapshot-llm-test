import csv
import json
import shutil
from pathlib import Path

from suitekit import ROOT, append_jsonl, iso, now, write_json

RUN_ID = "20261124T113838+0800-aac601"
OUT = ROOT / "outputs" / RUN_ID / "A02"
TMP = ROOT / "tmp" / RUN_ID / "A02"
AUDIT = OUT / "schedule-audit.json"
SOURCE = ROOT / "tasks" / "A02-conference-schedule" / "inputs" / "agenda.csv"
START, END, LUNCH_START, LUNCH_END = 540, 960, 720, 780


def minute(value):
    hour, minute_value = map(int, value.split(":"))
    return hour * 60 + minute_value


def clock(value):
    return f"{value // 60:02d}:{value % 60:02d}"


rows = list(csv.DictReader(SOURCE.read_text(encoding="utf-8-sig").splitlines()))
data = json.loads(AUDIT.read_text(encoding="utf-8"))
backup_dir = TMP / "audit-corrections"
backup_dir.mkdir(parents=True, exist_ok=True)
backup = backup_dir / "schedule-audit-before-gap-fix.json"
if not backup.exists():
    shutil.copy2(AUDIT, backup)

gaps = []
for venue in ("A", "B", "C"):
    blocked = [(minute(row["start"]), minute(row["end"])) for row in rows if row["venue"] == venue]
    blocked.append((LUNCH_START, LUNCH_END))
    cursor = START
    for begin, finish in sorted(blocked):
        if begin > cursor:
            gaps.append({
                "venue": venue,
                "start_minute": cursor,
                "end_minute": begin,
                "start": clock(cursor),
                "end": clock(begin),
                "duration_minutes": begin - cursor,
                "type": "free_gap",
                "excludes_public_lunch": True,
            })
        cursor = max(cursor, finish)
    if cursor < END:
        gaps.append({
            "venue": venue,
            "start_minute": cursor,
            "end_minute": END,
            "start": clock(cursor),
            "end": clock(END),
            "duration_minutes": END - cursor,
            "type": "free_gap",
            "excludes_public_lunch": True,
        })

expected = {
    "A": [(580, 600), (645, 660), (710, 720), (830, 850), (900, 930)],
    "B": [(595, 610), (670, 720), (855, 875), (930, 960)],
    "C": [(540, 555), (600, 615), (650, 665), (705, 720), (780, 800), (840, 860), (910, 960)],
}
for venue, intervals in expected.items():
    actual = [(gap["start_minute"], gap["end_minute"]) for gap in gaps if gap["venue"] == venue]
    assert actual == intervals, (venue, actual, intervals)

data["venue_gaps"] = gaps
data["gap_audit_method"] = {
    "day_start_minute": START,
    "day_end_minute": END,
    "blocked_intervals": "same-venue event intervals plus public lunch 12:00-13:00",
    "non_overlapping": True,
    "public_lunch_counted_as_event": False,
    "public_lunch_duplicated_in_venue_gaps": False,
    "free_gap_totals_minutes": {venue: sum(g["duration_minutes"] for g in gaps if g["venue"] == venue) for venue in expected},
}
data["audit_review"] = {
    "reviewed_at": iso(now()),
    "final_images_reopened": ["agenda-wide.png", "agenda-mobile.png"],
    "images_changed": False,
    "correction": "Excluded the separately recorded public lunch from each venue's free gaps to prevent overlap and double counting.",
    "previous_audit_snapshot": "tmp/20261124T113838+0800-aac601/A02/audit-corrections/schedule-audit-before-gap-fix.json",
}
write_json(AUDIT, data)

for name in ("agenda-wide.png", "agenda-mobile.png"):
    append_jsonl(TMP / "iterations.jsonl", {
        "iteration_id": f"{RUN_ID}-A02-final-recheck-{name}",
        "task_id": "A02",
        "case_id": None,
        "version_id": "final-independent-recheck",
        "parent_version": "v003-wide" if name.endswith("wide.png") else "v001-mobile",
        "type": "audit_visual_recheck",
        "image_path": f"outputs/{RUN_ID}/A02/{name}",
        "viewed_at": iso(now()),
        "timezone": "+08:00",
        "observable_issues": "No visual defect. All 15 events, required fields, capacities, lunch and dense 10:00 area are readable and consistent.",
        "changes": "Corrected schedule-audit free gaps to exclude public lunch; PNG and DSL unchanged.",
        "review_and_comparison": "Compared final image and complete audit against agenda.csv and venues.json.",
        "completed_visual_iteration": False,
    })

metrics_path = OUT / "task-metrics.json"
metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
metrics["status"] = "completed"
metrics["image_views"] += 2
metrics["audit_corrections"] = 1
write_json(metrics_path, metrics)

usage_path = OUT / "snapshot-usage.md"
usage = usage_path.read_text(encoding="utf-8")
usage += "\n## 独立终检补记\n\n最终两张 PNG 已重新打开核对。修正 `schedule-audit.json`：各会场 free_gap 不再与独立记录的 12:00–13:00 公共午休重叠或重复计时；修正前文件保存在临时目录 `audit-corrections/`。图片与 DSL 未改动。\n"
usage_path.write_text(usage, encoding="utf-8")
