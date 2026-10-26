"""A19 完成登记：suite-state.json + events.jsonl + checkpoint（幂等）。"""
from __future__ import annotations
import datetime as dt
import json
from pathlib import Path

ROOT = Path(".")
RUN_ID = "run-20261013-174209"
STATE = ROOT / "outputs" / RUN_ID / "_suite" / "suite-state.json"

state = json.loads(STATE.read_text(encoding="utf-8"))
for t in state["tasks"]:
    if t["id"] == "A19":
        t["status"] = "completed"
        t["started_at"] = "2026-10-20T09:05:56+08:00"
        t["ended_at"] = dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="seconds")
        t["artifacts"] = [
            f"outputs/{RUN_ID}/A19/grid-scene.png",
            f"outputs/{RUN_ID}/A19/grid-scene.snapshot",
            f"outputs/{RUN_ID}/A19/occlusion.png",
            f"outputs/{RUN_ID}/A19/occlusion.snapshot",
            f"outputs/{RUN_ID}/A19/occlusion-alternative.png",
            f"outputs/{RUN_ID}/A19/occlusion-alternative.snapshot",
            f"outputs/{RUN_ID}/A19/scene-data.json",
            f"outputs/{RUN_ID}/A19/questions.json",
            f"outputs/{RUN_ID}/A19/answers.json",
            f"outputs/{RUN_ID}/A19/equivalence.json",
            f"outputs/{RUN_ID}/A19/snapshot-usage.md",
            f"outputs/{RUN_ID}/A19/task-metrics.json",
        ]
        t["visual_review_evidence"] = [
            "outputs/run-20261013-174209/A19/grid-scene.png（1600×1600 整图实际查看）",
            "tmp/run-20261013-174209/A19/crops/q-row1-2.png（第 1-2 行 2x 放大）",
            "tmp/run-20261013-174209/A19/crops/q-row3-4.png（第 3-4 行 1.5x 放大）",
            "tmp/run-20261013-174209/A19/crops/q-row5-6.png（第 5-6 行 1.5x 放大）",
            "tmp/run-20261013-174209/A19/crops/q-row7-8-left.png / q-row7-8-right.png（第 7-8 行 2x 放大）",
            "tmp/run-20261013-174209/A19/crops/q-mid.png（中部 4 格 2x 放大）",
            "tmp/run-20261013-174209/A19/grid-thumb.png（400px 缩略实际查看，结构仍可辨）",
            "outputs/run-20261013-174209/A19/occlusion.png（800×800 遮挡图整图实际查看）",
            "程序化复测（tmp/run-20261013-174209/A19/grid-verify.json）：64/64 对象通过——"
            "颜色精确（16×4）、cov50 尺寸与形状判别唯一（16×4、尺寸 22/21/21）、"
            "标签墨迹 125-161px、框外 6px 环带 0 非白像素、强彩色 0 越界",
            "遮挡等价（tmp/run-20261013-174209/A19/occ-compare.json）：Pillow 10.0.0 解码 "
            "8 位未预乘 RGBA 逐像素比对，不同像素 0、最大通道差 0、数组哈希相同；"
            "遮挡矩形内非遮挡色像素 0（隐藏内容零泄漏）",
            "题库唯一性（tmp/run-20261013-174209/A19/qa-uniqueness.json）：14/14 通过，"
            "含 Q06 最大值唯一、Q12 最近邻唯一（200.00 vs 次近 282.84）、Q07 排序键全序",
            "tmp/run-20261013-174209/A19/requests.jsonl（7 次渲染请求，3 成功 4 网络失败重试后成功）",
            "tmp/run-20261013-174209/A19/iterations.jsonl（it00→it06）",
        ]
        t["unresolved_issues"] = []
        t["resume_notes"] = None
state["current_task"] = "A20"
state["updated_at"] = dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="milliseconds")
STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

ev = {
    "event": "task_completed", "task_id": "A19", "run_id": RUN_ID,
    "ts": dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="milliseconds"),
    "output_dir": f"outputs/{RUN_ID}/A19/",
    "artifacts": 12,
    "checks": ("64 objects constraint 0 problems; PNG recheck 64/64 (colors 16x4, "
               "shapes 16x4, sizes 22/21/21); occlusion A/B pixel-equivalent "
               "(different_pixels=0, max_channel_diff=0, equal array hash, equal file sha256); "
               "occluder interior 0 non-occluder px; 14 questions all computed with "
               "unique-answer verification 14/14"),
}
evpath = ROOT / "tmp" / RUN_ID / "_suite" / "events.jsonl"
old = [json.loads(l) for l in evpath.read_text(encoding="utf-8").splitlines() if l.strip()]
old = [e for e in old if not (e.get("task_id") == "A19" and e.get("event") == "task_completed")]
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
print(f"A19 registered; current_task -> {state['current_task']}; completed {done}/{len(state['tasks'])}; checkpoint {n}")
