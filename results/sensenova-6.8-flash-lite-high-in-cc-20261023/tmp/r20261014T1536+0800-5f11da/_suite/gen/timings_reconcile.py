"""调和各题"工作结束"与"状态交接结束"两个时刻，避免两者被混成一个数。

背景（A03 暴露出来的）：
- A03 的 task-metrics.json：started 23:42:18 / ended 01:21:00 / elapsed 5922 s
  —— 5922 正好等于 23:42:18 → 01:21:00，这份记录自身自洽，ended_at 是
  "三份交付物写完"的时刻。
- A03 的 suite-state：ended_at 01:28:21 —— 这是 events.jsonl 第 34 行
  task_completed 的触发时刻，也是 A04 的 started_at（交接边界）。
- 两者差 441 s。

不能简单二选一：
- 改 suite-state 的 ended_at 会断开"上一题 ended_at == 下一题 started_at"的
  链条，并与 events.jsonl 的 task_completed 记录矛盾；
- 改 task-metrics 的 elapsed 会改掉该题已交付、已交叉验证过的指标。

做法：两者都保留，各自标注语义，并把差额写清楚。
- metrics.elapsed_seconds        = task-metrics 的墙钟（工作跨度，权威值）
- metrics.timings.work_ended_at  = task-metrics 的 ended_at
- metrics.timings.handoff_ended_at = suite-state 的 ended_at（= 下一题 started_at）
- metrics.timings.handoff_elapsed_seconds = started_at → handoff_ended_at
- metrics.timings.work_vs_handoff_delta_seconds = 差额（0 表示两者一致）
- 差额不为 0 时写 note 说明原因。

A07 的情况同理：task-metrics 的 ended 11:07:00 即工作结束；suite-state 另有
recorded_at（11:20:05）记录状态写入时刻。这里统一成一套字段。

运行前设置 SNAPSHOT_RUN_ID。不覆盖历史检查点，另写新检查点并追加事件。
"""

from __future__ import annotations

import datetime as dt
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))
import suite as S  # noqa: E402


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if not os.environ.get("SNAPSHOT_RUN_ID"):
        print("需要设置 SNAPSHOT_RUN_ID")
        return 1

    state = S.load_state()
    order = state.get("task_order") or [t["id"] for t in state["tasks"]]
    rows: list[dict] = []

    for t in state["tasks"]:
        tid = t["id"]
        if t.get("status") != "completed":
            continue
        tm = json.loads(Path(f"outputs/{S.run_id()}/{tid}/task-metrics.json")
                        .read_text(encoding="utf-8"))
        # A01–A06 的起止在顶层；A07 放在 timings 里
        tmt = tm.get("timings") or tm.get("timing") or {}
        we_raw = tm.get("ended_at") or tmt.get("ended_at")
        work_end = dt.datetime.fromisoformat(we_raw)
        start = dt.datetime.fromisoformat(t["started_at"])
        handoff = dt.datetime.fromisoformat(t["ended_at"])
        work_elapsed = int((work_end - start).total_seconds())
        handoff_elapsed = int((handoff - start).total_seconds())
        delta = handoff_elapsed - work_elapsed

        m = t["metrics"]
        # 不改 task-metrics 的权威值，只把它与"按两端时刻重算"的结果并列
        if m.get("elapsed_seconds") != work_elapsed:
            m["elapsed_seconds_note"] = (
                f"task-metrics.json 记 {m.get('elapsed_seconds')}，"
                f"但其自身 ended_at − started_at = {work_elapsed}；"
                f"以该题自己的起止时刻为准，见 timings.work_ended_at")
            m["elapsed_seconds_recomputed_from_ended"] = work_elapsed

        m["timings"] = {
            "path_base": "suite_root",
            "start": t["started_at"],
            "work_ended_at": we_raw,
            "handoff_ended_at": t["ended_at"],
            "elapsed_seconds": work_elapsed,
            "handoff_elapsed_seconds": handoff_elapsed,
            "work_vs_handoff_delta_seconds": delta,
            "note": ("工作结束（交付物写完）与状态交接结束（task_completed 事件、"
                     "即下一题 started_at）为两个不同时刻"
                     if delta else "两者一致"),
        }
        rows.append({"task_id": tid, "start": t["started_at"],
                     "work_ended": we_raw,
                     "handoff_ended": t["ended_at"],
                     "work_elapsed": work_elapsed,
                     "handoff_elapsed": handoff_elapsed, "delta": delta})

    # 交接关系：重叠是错误（两题同时开工），间隔是正常的交接耗时
    overlap: list[str] = []
    gaps: list[str] = []
    done = [(t["id"], t["started_at"], t["ended_at"])
            for t in state["tasks"] if t.get("status") == "completed"]
    for (a, _, ae), (b, bs, _) in zip(done, done[1:]):
        d = (dt.datetime.fromisoformat(bs)
             - dt.datetime.fromisoformat(ae)).total_seconds()
        if d < 0:
            overlap.append(f"{a}→{b} 重叠 {-int(d)}s")
        elif d > 0:
            gaps.append(f"{a}→{b} 间隔 {int(d)}s")
    chain = overlap          # 只有重叠算硬错误

    S.save_state(state)
    ck = S.snapshot_checkpoint(state)
    state["last_checkpoint"] = ck
    S.save_state(state)

    S.append_event({
        "ts": S.now_iso(), "event": "timings_reconciled", "checkpoint": ck,
        "why": ("各题 elapsed_seconds 来自其 task-metrics.json（工作跨度），"
                "suite-state 的 ended_at 是 task_completed 事件时刻（交接边界）。"
                "A03 两者相差 441 s，原先会被读成自相矛盾；现分别标注语义，"
                "两者都保留、都指向各自的来源文件。"),
        "unchanged": "suite-state 的 ended_at 与 task-metrics 的 elapsed_seconds "
                     "数值均未改动；只补充了 timings 的语义标注。",
        "no_overlaps": not chain,
        "overlaps": chain,
        "inter_task_gaps": gaps,
        "gap_note": ("间隔是正常的交接耗时（读下一题 TASK.md、准备脚本），"
                     "不计入任何一题的 elapsed_seconds，"
                     "因此 suite 总墙钟 > 各题 elapsed 之和。"),
        "tasks": rows,
    })

    print(f"调和完成 → {Path(ck).name}")
    print(f"无重叠: {not chain}" + ("" if not chain else f" 重叠 {chain}"))
    if gaps:
        print(f"交接间隔 {len(gaps)} 处: {gaps}")
    print(f"\n{'题':4s} {'起':19s} {'工作结束':19s} {'交接结束':19s} "
          f"{'工作s':>7s} {'交接s':>7s} {'差':>5s}")
    for r in rows:
        print(f"{r['task_id']:4s} {r['start'][11:19]:19s} "
              f"{r['work_ended'][11:19]:19s} {r['handoff_ended'][11:19]:19s} "
              f"{r['work_elapsed']:7d} {r['handoff_elapsed']:7d} {r['delta']:5d}")
    return 0 if not chain else 1


if __name__ == "__main__":
    sys.exit(main())
