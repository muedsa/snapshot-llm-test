"""A16 完成登记：suite-state.json + events.jsonl + checkpoint。"""
from __future__ import annotations
import datetime as dt
import json
from pathlib import Path

ROOT = Path(".")
RUN_ID = "run-20261013-174209"
STATE = ROOT / "outputs" / RUN_ID / "_suite" / "suite-state.json"

state = json.loads(STATE.read_text(encoding="utf-8"))
for t in state["tasks"]:
    if t["id"] == "A16":
        t["status"] = "completed"
        t["started_at"] = "2026-10-19T18:45:00+08:00"
        t["ended_at"] = "2026-10-19T19:05:00+08:00"
        t["artifacts"] = [
            f"outputs/{RUN_ID}/A16/corrected-report.png",
            f"outputs/{RUN_ID}/A16/corrected-report.snapshot",
            f"outputs/{RUN_ID}/A16/findings.json",
            f"outputs/{RUN_ID}/A16/corrected-data.json",
            f"outputs/{RUN_ID}/A16/snapshot-usage.md",
            f"outputs/{RUN_ID}/A16/task-metrics.json",
        ]
        t["visual_review_evidence"] = [
            "tasks/A16-visual-data-forensics/inputs/flawed-report.png（原尺寸 + 图表区/底部卡 2× 放大实际查看）",
            "tmp/run-20261013-174209/A16/flawed-chart-2x.png（错误图表 2× 放大：柱高与标签矛盾）",
            "tmp/run-20261013-174209/A16/flawed-cards-2x.png（底部卡 2× 放大：Q3=42 与观察卡结论）",
            "tmp/run-20261013-174209/A16/corrected-v1.png（修正版整图查看）",
            "tmp/run-20261013-174209/A16/qc-q1_header.png ~ qc-q4_kpi.png（四分区 1.6× 放大复查）",
            "tmp/run-20261013-174209/A16/side-by-side.png（错误版/修正版并排证据）",
            "程序化复测：八柱顶/高/零起点与 值×1.8 精确一致（0 误差）",
            "tmp/run-20261013-174209/A16/requests.jsonl",
            "tmp/run-20261013-174209/A16/iterations.jsonl",
        ]
        t["unresolved_issues"] = []
        t["resume_notes"] = None
state["current_task"] = "A17"
state["updated_at"] = dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="milliseconds")
STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

ev = {
    "event": "task_completed", "task_id": "A16", "run_id": RUN_ID,
    "ts": dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="milliseconds"),
    "output_dir": f"outputs/{RUN_ID}/A16/",
    "artifacts": 6,
}
with (ROOT / "tmp" / RUN_ID / "_suite" / "events.jsonl").open("a", encoding="utf-8") as fh:
    fh.write(json.dumps(ev, ensure_ascii=False) + "\n")

ckdir = ROOT / "tmp" / RUN_ID / "_suite" / "checkpoints"
ckdir.mkdir(parents=True, exist_ok=True)
n = len(list(ckdir.glob("state-*.json"))) + 1
(ckdir / f"state-{n:06d}.json").write_text(
    json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("A16 registered; current_task ->", state["current_task"], "; checkpoint", n)
