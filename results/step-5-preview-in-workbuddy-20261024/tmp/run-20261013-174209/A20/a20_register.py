"""A20 完成登记：suite-state.json + events.jsonl + checkpoint（幂等）。"""
from __future__ import annotations
import datetime as dt
import json
from pathlib import Path

ROOT = Path(".")
RUN_ID = "run-20261013-174209"
STATE = ROOT / "outputs" / RUN_ID / "_suite" / "suite-state.json"

state = json.loads(STATE.read_text(encoding="utf-8"))
for t in state["tasks"]:
    if t["id"] == "A20":
        t["status"] = "completed"
        t["started_at"] = "2026-10-20T14:48:00+08:00"
        t["ended_at"] = dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="seconds")
        t["artifacts"] = [
            f"outputs/{RUN_ID}/A20/annotated-map.png",
            f"outputs/{RUN_ID}/A20/annotated-map.snapshot",
            f"outputs/{RUN_ID}/A20/label-layout.json",
            f"outputs/{RUN_ID}/A20/layout-audit.json",
            f"outputs/{RUN_ID}/A20/snapshot-usage.md",
            f"outputs/{RUN_ID}/A20/task-metrics.json",
        ]
        t["visual_review_evidence"] = [
            "outputs/run-20261013-174209/A20/annotated-map.png（1600x1100 整图实际查看："
            "24 标签、坐标轴/范围/单位/图例/TOP3 注记齐备）",
            "tmp/run-20261013-174209/A20/crops/center6-v2.png（指定中心 6 点 M06/M08/M09/M10/"
            "M11/M12 及全部引线 2x 放大：7 条簇引线各连回自有点，无交叉，净距 14.3px）",
            "tmp/run-20261013-174209/A20/crops/m12-m09.png（M12/M08/M09/M10 引线 3x 放大）",
            "tmp/run-20261013-174209/A20/crops/m04-m05.png（M04/M06 引线 3x 放大）",
            "tmp/run-20261013-174209/A20/crops/left-top.png（M01-M07 区 2x 放大）",
            "tmp/run-20261013-174209/A20/crops/right-bottom.png（M08-M11/M16-M19/M22/M23 区 "
            "2x 放大：TOP1/2/3 红标签引线连回各自红点）",
            "tmp/run-20261013-174209/A20/thumb-400.png（400x275 缩略实际查看）",
            "程序化复测（outputs/run-20261013-174209/A20/layout-audit.json）：19/19 通过——"
            "24/24 锚点映射一致、盒间距最小 5.044px(>=4)、盒-非本点盘最小净距 8.493px(>6)、"
            "自有标签不遮自有点最小 8.002px、引线 8/8 起点在所属圆周(6.000px)/终点在自有盒边、"
            "穿标签 0、自交 0、共线重合 0、交叉 0(<=3)、越界 0、TOP3=M10 93/M08 91/M23 90、"
            "点径 12 且最小圆心距 30.862px(盘净距 18.862px)故无需缩至 8px",
            "PNG 复测：24/24 点色精确比色、24/24 标签墨迹在盒内(309-1530px)、"
            "8/8 引线沿线覆盖率 >=0.991",
            "tmp/run-20261013-174209/A20/requests.jsonl（3 次渲染请求：1 次 matrix 未加括号"
            "报错、2 次成功；终版 request_id d452f296）",
            "tmp/run-20261013-174209/A20/iterations.jsonl（it00→it05）",
        ]
        t["unresolved_issues"] = []
        t["resume_notes"] = None
state["current_task"] = "A21"
state["updated_at"] = dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="milliseconds")
STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

ev = {
    "event": "task_completed", "task_id": "A20", "run_id": RUN_ID,
    "ts": dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="milliseconds"),
    "output_dir": f"outputs/{RUN_ID}/A20/",
    "artifacts": 6,
    "checks": ("geometry 19/19 + PNG 0 problems; 24/24 point colors, 24/24 label ink in box, "
               "8/8 leaders start on own circle (6.000px) and end on own box; crossings 0/3, "
               "min box gap 5.044px, min box-disk 8.493px, min leader gap 14.336px; "
               "min center dist 30.862px so no shrink to 8px needed"),
}
evpath = ROOT / "tmp" / RUN_ID / "_suite" / "events.jsonl"
old = [json.loads(l) for l in evpath.read_text(encoding="utf-8").splitlines() if l.strip()]
old = [e for e in old if not (e.get("task_id") == "A20" and e.get("event") == "task_completed")]
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
print(f"A20 registered; current_task -> {state['current_task']}; "
      f"completed {done}/{len(state['tasks'])}; checkpoint {n}")
