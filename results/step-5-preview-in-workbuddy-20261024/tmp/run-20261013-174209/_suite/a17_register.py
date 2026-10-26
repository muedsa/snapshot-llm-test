"""A17 完成登记：suite-state.json + events.jsonl + checkpoint。"""
from __future__ import annotations
import datetime as dt
import json
from pathlib import Path

ROOT = Path(".")
RUN_ID = "run-20261013-174209"
STATE = ROOT / "outputs" / RUN_ID / "_suite" / "suite-state.json"

state = json.loads(STATE.read_text(encoding="utf-8"))
for t in state["tasks"]:
    if t["id"] == "A17":
        t["status"] = "completed"
        t["started_at"] = "2026-10-19T19:21:30+08:00"
        t["ended_at"] = dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="seconds")
        t["artifacts"] = [
            f"outputs/{RUN_ID}/A17/handbook-0{n}.{e}" for n in range(1, 5) for e in ("png", "snapshot")
        ] + [
            f"outputs/{RUN_ID}/A17/example-0{i}.{e}" for i in range(1, 5) for e in ("png", "snapshot")
        ] + [
            f"outputs/{RUN_ID}/A17/examples.json",
            f"outputs/{RUN_ID}/A17/sources.md",
            f"outputs/{RUN_ID}/A17/verification.json",
            f"outputs/{RUN_ID}/A17/snapshot-usage.md",
            f"outputs/{RUN_ID}/A17/task-metrics.json",
        ]
        t["visual_review_evidence"] = [
            "outputs/run-20261013-174209/A17/handbook-01..04.png（四页整图实际查看）",
            "tmp/run-20261013-174209/A17/zoom-p1-illus.png / zoom-p2-illus.png（插图区 3x 放大）",
            "tmp/run-20261013-174209/A17/example-01..04.png（独立示例实际查看）",
            "tmp/run-20261013-174209/A17/probe-glyph.snapshot（字形前进实测：等宽 ASCII 10.0px / CJK 20.0px @20px）",
            "tmp/run-20261013-174209/A17/bdtest.png、ex4-panel-4x.png（ColorFiltered 圆角透明角被滤色的反例）",
            "程序化墨迹边界检查：四页非背景墨迹包围盒 x∈[48,1151]、y≤1531，0 项越界",
            "程序化像素比对：手册插图区与独立示例 PNG maxdiff=0，0/96000 像素差异（4 页全部）",
            "tmp/run-20261013-174209/A17/a17_verify.py → 33 项检查全部通过",
            "tmp/run-20261013-174209/A17/requests.jsonl（141 次请求，94 成功，47 次失败全部为重试后成功）",
            "tmp/run-20261013-174209/A17/iterations.jsonl（it00→it06）",
        ]
        t["unresolved_issues"] = []
        t["resume_notes"] = None
state["current_task"] = "A18"
state["updated_at"] = dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="milliseconds")
STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

ev = {
    "event": "task_completed", "task_id": "A17", "run_id": RUN_ID,
    "ts": dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="milliseconds"),
    "output_dir": f"outputs/{RUN_ID}/A17/",
    "artifacts": 21,
    "checks": "33/33 pass",
}
with (ROOT / "tmp" / RUN_ID / "_suite" / "events.jsonl").open("a", encoding="utf-8") as fh:
    fh.write(json.dumps(ev, ensure_ascii=False) + "\n")

ckdir = ROOT / "tmp" / RUN_ID / "_suite" / "checkpoints"
ckdir.mkdir(parents=True, exist_ok=True)
n = len(list(ckdir.glob("state-*.json"))) + 1
(ckdir / f"state-{n:06d}.json").write_text(
    json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
done = sum(1 for t in state["tasks"] if t["status"] == "completed")
print(f"A17 registered; current_task -> {state['current_task']}; completed {done}/{len(state['tasks'])}; checkpoint {n}")
