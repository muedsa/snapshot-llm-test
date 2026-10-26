"""A15 完成登记：suite-state.json + events.jsonl + checkpoint。"""
from __future__ import annotations
import datetime as dt
import json
from pathlib import Path

ROOT = Path(".")
RUN_ID = "run-20261013-174209"
STATE = ROOT / "outputs" / RUN_ID / "_suite" / "suite-state.json"

state = json.loads(STATE.read_text(encoding="utf-8"))
for t in state["tasks"]:
    if t["id"] == "A15":
        t["status"] = "completed"
        t["started_at"] = "2026-10-19T17:56:42.392+08:00"
        t["ended_at"] = "2026-10-19T18:40:00+08:00"
        t["artifacts"] = [
            f"outputs/{RUN_ID}/A15/reconstructed.png",
            f"outputs/{RUN_ID}/A15/reconstructed.snapshot",
            f"outputs/{RUN_ID}/A15/reconstruction-audit.json",
            f"outputs/{RUN_ID}/A15/comparison.md",
            f"outputs/{RUN_ID}/A15/snapshot-usage.md",
            f"outputs/{RUN_ID}/A15/task-metrics.json",
        ]
        t["visual_review_evidence"] = [
            "tmp/run-20261013-174209/A15/reconstructed-draft.png（v1 整图查看，发现系统性 1px 偏差）",
            "tmp/run-20261013-174209/A15/reconstructed-v2.png（v2 整图查看 + 锚点对比 60+ 项）",
            "tmp/run-20261013-174209/A15/reconstructed-v3.png（v3 整图查看，确认删 hack 无回归）",
            "tmp/run-20261013-174209/A15/reconstructed-v4.png（终版整图查看）",
            "tmp/run-20261013-174209/A15/qc-q1_header.png ~ qc-q7_pro.png（七分区 2× 放大与参考并排复查）",
            "tmp/run-20261013-174209/A15/anchor-compare-v4.json（41 锚点同方法程序化对比，0 超差）",
            "tmp/run-20261013-174209/A15/requests.jsonl",
            "tmp/run-20261013-174209/A15/iterations.jsonl",
        ]
        t["unresolved_issues"] = []
        t["resume_notes"] = None
state["current_task"] = "A16"
state["updated_at"] = dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="milliseconds")
STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

ev = {
    "event": "task_completed", "task_id": "A15", "run_id": RUN_ID,
    "ts": dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="milliseconds"),
    "output_dir": f"outputs/{RUN_ID}/A15/",
    "artifacts": 6,
}
with (ROOT / "tmp" / RUN_ID / "_suite" / "events.jsonl").open("a", encoding="utf-8") as fh:
    fh.write(json.dumps(ev, ensure_ascii=False) + "\n")

ckdir = ROOT / "tmp" / RUN_ID / "_suite" / "checkpoints"
ckdir.mkdir(parents=True, exist_ok=True)
n = len(list(ckdir.glob("state-*.json"))) + 1
(ckdir / f"state-{n:06d}.json").write_text(
    json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("A15 registered; current_task ->", state["current_task"], "; checkpoint", n)
