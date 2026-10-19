# -*- coding: utf-8 -*-
"""B05 套件收尾：suite-state 更新 + events 追加 + checkpoint 落盘。
遵循 PATHS.md：输出均为相对 suite_root 的路径。不覆盖旧 checkpoint。"""
import io
import json
import sys
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(r"D:\mine\test\glm-5.3-flash")
RUN = "20261016T164020-m1"
SUITE_OUT = ROOT / "outputs" / RUN / "_suite"
SUITE_TMP = ROOT / "tmp" / RUN / "_suite"
NOW = datetime.now().astimezone().isoformat(timespec="milliseconds")

SS = SUITE_OUT / "suite-state.json"
st = json.loads(SS.read_text(encoding="utf-8"))

b05 = [t for t in st["tasks"] if t["id"] == "B05"][0]
b05.update({
    "status": "completed",
    "started_at": "2026-10-18T19:33:58+08:00",
    "ended_at": NOW,
    "output_dir": "outputs/%s/B05/" % RUN,
    "temp_dir": "tmp/%s/B05/" % RUN,
    "completed_rounds": [],
    "completed_cases": ["case-%02d" % i for i in range(1, 11)],
    "artifacts": ["portfolio.json", "portfolio.md", "gallery.md", "snapshot-usage.md",
                  "task-metrics.json", "product-brief.md", "journey.json",
                  "case-01..10/（final.png + final.snapshot + case.md ×10）"],
    "visual_review_evidence": [
        "tmp/%s/B05/steps/sheet-1.png" % RUN, "tmp/%s/B05/steps/sheet-2.png" % RUN,
        "tmp/%s/B05/steps/sheet-3.png" % RUN, "tmp/%s/B05/steps/sheet-4.png" % RUN,
        "tmp/%s/B05/steps/sheet-5.png" % RUN,
        "tmp/%s/B05/steps/zoom-c02-member-v4.png" % RUN,
        "tmp/%s/B05/steps/zoom-c03-left-v3.png" % RUN,
        "tmp/%s/B05/steps/zoom-c04-today.png" % RUN,
        "tmp/%s/B05/steps/zoom-c08-posts-v3.png" % RUN,
        "tmp/%s/B05/steps/zoom-c10-bars-v2.png" % RUN,
    ],
    "unresolved_issues": [],
    "resume_notes": "",
    "final_images": 10,
})
st["completed_task_count"] = 29
st["current_task"] = "B06"
st["current_round"] = None
st["current_case"] = None
st["updated_at"] = NOW
st["last_checkpoint"] = "state-000051.json"
SS.write_text(json.dumps(st, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("suite-state B05 -> completed; completed=29 current=B06")

# events 追加
EV = SUITE_TMP / "events.jsonl"
ev_next = len(EV.read_text(encoding="utf-8").strip().splitlines()) + 1
event = {
    "id": "SUITE-ev-%06d" % ev_next,
    "at": NOW,
    "kind": "task-completed",
    "task_id": "B05",
    "detail": ("十屏《轮值 LUNZHI》家庭照护协调工具全部虚构演示：c01..c10 终版 v3/v4/v3/v2/v2/v2/v3/v4/v5/v3，"
               "32 渲染请求（30x200+2x400 同因 DASHED border 已修）+ 33 次真实看图（终态五张接触表整卷复审）+ "
               "32 行迭代台账（baseline 9 / visual 13 / syntax 2 / requirement 7 / final 1）；"
               "product-brief.md journey.json portfolio.json/md gallery.md 等 16 类交付已验证；"
               "统一锚点见 plan-v1.md（v1.1/v1.2 追记）。"),
}
with EV.open("a", encoding="utf-8") as f:
    f.write(json.dumps(event, ensure_ascii=False) + "\n")
print("event appended:", event["id"], "total rows:", ev_next)

# checkpoint
ck = dict(st)
ck["checkpoint_id"] = "state-000051.json"
ck["checkpoint_at"] = NOW
ck["checkpoint_prev"] = "tmp/%s/_suite/checkpoints/state-000050.json" % RUN
CK = SUITE_TMP / "checkpoints" / "state-000051.json"
if CK.exists():
    CK = SUITE_TMP / "checkpoints" / "state-000051_dup.json"
CK.write_text(json.dumps(ck, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("checkpoint saved:", CK.name)

# finals 汇总核对
total = sum([t.get("final_images", 0) or 0 for t in st["tasks"]])
print("suite finals total:", total)
