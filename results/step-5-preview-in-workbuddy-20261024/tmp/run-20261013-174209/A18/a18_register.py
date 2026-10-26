"""A18 完成登记：suite-state.json + events.jsonl + checkpoint。"""
from __future__ import annotations
import datetime as dt
import json
from pathlib import Path

ROOT = Path(".")
RUN_ID = "run-20261013-174209"
STATE = ROOT / "outputs" / RUN_ID / "_suite" / "suite-state.json"

state = json.loads(STATE.read_text(encoding="utf-8"))
for t in state["tasks"]:
    if t["id"] == "A18":
        t["status"] = "completed"
        t["started_at"] = "2026-10-19T21:07:00+08:00"
        t["ended_at"] = dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="seconds")
        t["artifacts"] = [
            f"outputs/{RUN_ID}/A18/three-act-story.png",
            f"outputs/{RUN_ID}/A18/three-act-story.snapshot",
            f"outputs/{RUN_ID}/A18/story-audit.json",
            f"outputs/{RUN_ID}/A18/rationale.md",
            f"outputs/{RUN_ID}/A18/snapshot-usage.md",
            f"outputs/{RUN_ID}/A18/task-metrics.json",
            f"outputs/{RUN_ID}/A18/verification.json",
        ]
        t["visual_review_evidence"] = [
            "outputs/run-20261013-174209/A18/three-act-story.png（1600×1000 终版整图实际查看）",
            "tmp/run-20261013-174209/A18/thumb-400.png（400px 宽缩略实际查看，三幕可辨）",
            "tmp/run-20261013-174209/A18/preview-A.png / preview-B.png（两种构图 1600×1000 实际预览）",
            "tmp/run-20261013-174209/A18/crops/A-act1.png / A-act2.png / A-act3.png（选定构图三栏 2x 放大）",
            "tmp/run-20261013-174209/A18/crops/A-act2-zoom.png / A-act3-zoom.png（形变节点与五边形簇 2x 放大）",
            "tmp/run-20261013-174209/A18/crops/B-act3.png（落选构图第三幕 2x 放大，用于选型对比）",
            "程序化复测（a18_final_verify.json）：几何 0 问题；45/45 圆 cov50 直径 35.70-36.19px；"
            "9/9 节点框与预期外包框一致；45 条连线沿线覆盖率全 1.00；圆外 0 个杂色像素；"
            "每幕蓝/橙/灰各 5；Text 恰 4 个（总标题+三幕名）；与 preview-A 逐像素 0 差异",
            "tmp/run-20261013-174209/A18/requests.jsonl（11 次请求，5 次成功，6 次网络失败全部重试后成功）",
            "tmp/run-20261013-174209/A18/iterations.jsonl（it00→it04）",
        ]
        t["unresolved_issues"] = []
        t["resume_notes"] = None
state["current_task"] = "A19"
state["updated_at"] = dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="milliseconds")
STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

ev = {
    "event": "task_completed", "task_id": "A18", "run_id": RUN_ID,
    "ts": dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="milliseconds"),
    "output_dir": f"outputs/{RUN_ID}/A18/",
    "artifacts": 7,
    "checks": "geometry 0 problems + PNG 0 problems; 45/45 circles (d 35.70-36.19px), "
              "9/9 node boxes, 9/9 glyph shapes, 45/45 connectors",
}
evpath = ROOT / "tmp" / RUN_ID / "_suite" / "events.jsonl"
old = [json.loads(l) for l in evpath.read_text(encoding="utf-8").splitlines() if l.strip()]
old = [e for e in old if not (e.get("task_id") == "A18" and e.get("event") == "task_completed")]
with evpath.open("w", encoding="utf-8") as fh:
    for e in old:
        fh.write(json.dumps(e, ensure_ascii=False) + "\n")
    fh.write(json.dumps(ev, ensure_ascii=False) + "\n")

ckdir = ROOT / "tmp" / RUN_ID / "_suite" / "checkpoints"
ckdir.mkdir(parents=True, exist_ok=True)
n = len(list(ckdir.glob("state-*.json"))) + 1
(ckdir / f"state-{n:06d}.json").write_text(
    json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
done = sum(1 for t in state["tasks"] if t["status"] == "completed")
print(f"A18 registered; current_task -> {state['current_task']}; completed {done}/{len(state['tasks'])}; checkpoint {n}")
