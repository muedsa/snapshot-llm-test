import json, os, datetime

P = "outputs/20261008T1615Z-run01/B01/task-metrics.json"
d = json.load(open(P, encoding="utf-8"))
assert d["task_id"] == "B01"
d["status_before_correction"] = d["status"]
d["status"] = "completed"
d["stop_reason"] = (
    "十件独立作品（case-01…case-10）全部定稿并逐件实际看图，收尾产物"
    "（gallery.md / portfolio.md / portfolio.json / asset-sources.json / "
    "snapshot-usage.md / task-metrics.json）齐备；无未解决事项。"
)
d.setdefault("counting_notes", {})["status_correction_at_suite_review"] = (
    "2026-10-11 套件级总审查时发现本文件 status 字段仍为 in_progress，"
    "而 counts.final_case_count=10、十个 case-NN/final.png + final.snapshot "
    "与全部收尾文件均已实际存在（见 tmp/<run>/_suite/suite-facts.json 的 "
    "B01.final_images=10）。据此把 status 更正为 completed 并补 stop_reason；"
    "原值保留在 status_before_correction 字段，请求/迭代/看图等计数一律未改动。"
)
d["status_corrected_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
json.dump(d, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("B01 status ->", d["status"])
