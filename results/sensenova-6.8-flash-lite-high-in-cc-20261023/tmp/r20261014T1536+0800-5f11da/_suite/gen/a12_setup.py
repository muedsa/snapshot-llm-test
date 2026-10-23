"""A12 目录初始化与 task_started 留痕。幂等：已存在事件则不重复追加。

用法：SNAPSHOT_RUN_ID=<rid> python -I tmp/<rid>/_suite/gen/a12_setup.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "tools"))
import suite as S  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

TASK = "A12"
RID = S.run_id()
OUT, TMP = S.task_dirs(TASK)
SRC = ROOT / "tasks" / "A12-responsive-system" / "inputs" / "content.json"
CONTENT_REL = "tasks/A12-responsive-system/inputs/content.json"

for sub in ("", "dsl", "responses", "preview", "gen"):
    (TMP / sub).mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

content = json.loads(SRC.read_text(encoding="utf-8"))
print("content keys:", list(content.keys()))
print("title   :", content["title"])
print("subtitle:", content["subtitle"])
print("date    :", content["date"])
print("time    :", content["time"])
print("location:", content["location"])
print("cta     :", content["cta"])
print("website :", content["website"])
print("cards   :", len(content["cards"]))
for c in content["cards"]:
    print("  ", c["id"], c["title"], "|", c["detail"],
          "| title=%d detail=%d" % (len(c["title"]), len(c["detail"])))

EVENTS = TMP.parent / "_suite" / "events.jsonl"
already = False
if EVENTS.exists():
    for line in EVENTS.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("event") == "task_started" and ev.get("task_id") == TASK:
            already = True
            break
if not already:
    S.append_event({
        "ts": S.now_iso(),
        "event": "task_started",
        "task_id": TASK,
        "title": "四断点完整内容视觉系统",
        "status": "in_progress",
        "started_at": S.now_iso(),
        "output_dir": S.rel(OUT),
        "temp_dir": S.rel(TMP),
    })
    print("appended task_started", TASK)
else:
    print("task_started already recorded for", TASK)

print("OUT:", S.rel(OUT))
print("TMP:", S.rel(TMP))
