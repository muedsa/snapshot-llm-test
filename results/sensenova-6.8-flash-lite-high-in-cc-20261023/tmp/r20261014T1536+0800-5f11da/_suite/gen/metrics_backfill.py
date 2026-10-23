"""把已完成各题的 task-metrics.json 汇总进 suite-state.json 的 tasks[].metrics。

动机：全套总指标只累计"每题顶层汇总 + shared"，需要每题在 suite-state 里有一份
可追溯的指标摘要。A07 由 suite_update.py 写入，A01–A06 早于该脚本完成，
其 tasks[].metrics 为空，这里从各题自己的 task-metrics.json 回填。

各题 task-metrics.json 的字段名不完全一致，这里做归一化（只重命名，不改数值）：
- visual_iterations / completed_visual_iterations  -> visual_iterations
- pixel_checks / requirement_checks（总数）        -> requirement_checks_total
- pixel_failures / requirement_failures（失败数）  -> requirement_failures
- 通过数 = 总数 - 失败数（两者均已记录，非推算）
- elapsed_seconds：顶层字段；A07 放在 timings.elapsed_seconds，两种位置都读
- A07 的 verification 三组 passed/total 合并成 34/34

同时修正 state_fix.py 引入的一处错误：A07 的 metrics.timings.start
误取了 suite 级 started_at（2026-10-14T15:43:30），应为 A07 自己的 started_at。

不覆盖历史：state-000034/35.json 与既有事件保持原样，本脚本另写新检查点
并追加一条 metrics_backfilled 事件，事件里带每题的 before/after 与来源字段名。
运行前设置 SNAPSHOT_RUN_ID。
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))
import suite as S  # noqa: E402


def load_task_metrics(tid: str) -> dict | None:
    p = Path(f"outputs/{S.run_id()}/{tid}/task-metrics.json")
    if not p.is_file():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def norm(tid: str, m: dict) -> dict:
    """从一题的 task-metrics.json 抽出归一化摘要。找不到就返回带说明的 None。"""
    c = m.get("counts") or {}
    timing = m.get("timings") or m.get("timing") or {}
    elapsed = m.get("elapsed_seconds", timing.get("elapsed_seconds"))

    total = c.get("requirement_checks", c.get("pixel_checks"))
    fails = c.get("requirement_failures", c.get("pixel_failures"))
    if total is not None:
        assert fails is not None, f"{tid}: 有总数但无失败数字段"
        src = ("counts." + ("requirement_checks" if c.get("requirement_checks")
                            else "pixel_checks")
               + " − counts." + ("requirement_failures"
                                 if c.get("requirement_failures") is not None
                                 else "pixel_failures"))
        passed = total - fails
    else:
        # A07：counts 里没有汇总字段，检查项按组记在 verification 里
        g = m.get("verification")
        groups = [v for v in (g or {}).values()
                  if isinstance(v, dict) and "total" in v and "passed" in v] \
            if isinstance(g, dict) else []
        assert groups, f"{tid}: 找不到 requirement_checks 或 verification 检查组"
        total = sum(v["total"] for v in groups)
        passed = sum(v["passed"] for v in groups)
        fails = total - passed
        src = "verification 各组 passed/total 求和（" \
              + ", ".join(f"{k}:{v['passed']}/{v['total']}"
                          for k, v in g.items()
                          if isinstance(v, dict) and "total" in v) + "）"

    issues = c.get("issues_found")
    if issues is None and isinstance(m.get("known_defects_fixed"), list):
        issues = len(m["known_defects_fixed"])   # A07 记在顶层

    # 未解决事项：各题的 unresolved_issues 是 task-metrics 的顶层结构，
    # 状态取值 open / accepted。这里只取计数与状态分布做汇总索引，
    # 条目全文仍留在 suite-state 的 tasks[].unresolved_issues 与各题报告里。
    ui = m.get("unresolved_issues") or []
    ui_status: dict[str, int] = {}
    for x in ui:
        s = (x.get("status") if isinstance(x, dict) else None) or "unlabeled"
        ui_status[s] = ui_status.get(s, 0) + 1
    blocking = [x.get("id") for x in ui
                if isinstance(x, dict)
                and (x.get("severity") in ("high", "critical", "blocker")
                     or x.get("status") == "open")]

    return {
        "snapshot_requests": c.get("snapshot_requests"),
        "successful": c.get("successful_snapshot_requests"),
        "failed": c.get("failed_snapshot_requests"),
        "retry_requests": c.get("retry_requests"),
        "image_views": c.get("image_views"),
        "visual_iterations": c.get("visual_iterations",
                                    c.get("completed_visual_iterations")),
        "incomplete_visual_iterations": c.get("incomplete_visual_iterations"),
        "requirement_checks": f"{passed}/{total}",
        "requirement_checks_total": total,
        "requirement_checks_passed": passed,
        "requirement_failures": fails,
        "requirement_checks_source": src,
        "issues_found": issues,
        "unresolved_issues_count": len(ui),
        "unresolved_issues_status": ui_status,
        "unresolved_needing_attention": blocking,
        "elapsed_seconds": elapsed,
        "source": {
            "path_base": "suite_root",
            "task_metrics": f"outputs/{S.run_id()}/{tid}/task-metrics.json",
            "requests_log": f"tmp/{S.run_id()}/{tid}/requests.jsonl",
            "iterations_log": f"tmp/{S.run_id()}/{tid}/iterations.jsonl",
        },
    }


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if not os.environ.get("SNAPSHOT_RUN_ID"):
        print("需要设置 SNAPSHOT_RUN_ID")
        return 1

    state = S.load_state()
    changed: list[dict] = []
    for t in state["tasks"]:
        tid = t["id"]
        if t.get("status") != "completed":
            continue
        tm = load_task_metrics(tid)
        if tm is None:
            changed.append({"task_id": tid, "before": t.get("metrics"),
                            "after": None, "note": "task-metrics.json 不存在"})
            continue
        t["metrics"] = norm(tid, tm)
        # 附带本任务的真实起止时刻，便于总墙钟与本项互校
        t["metrics"]["timings"] = {
            "path_base": "suite_root",
            "start": t.get("started_at"),
            "end": t.get("ended_at"),
            "elapsed_seconds": t["metrics"]["elapsed_seconds"],
        }
        changed.append({"task_id": tid, "before": None, "after": t["metrics"]})

    S.save_state(state)
    ck = S.snapshot_checkpoint(state)
    state["last_checkpoint"] = ck
    S.save_state(state)

    S.append_event({
        "ts": S.now_iso(), "event": "metrics_backfilled", "checkpoint": ck,
        "scope": "A01..A07",
        "why": "全套总指标只累计每题顶层汇总，需要每题在 suite-state 有可追溯指标摘要；"
               "A01–A06 早于 suite_update.py 完成，metrics 为空",
        "normalization": {
            "visual_iterations": "visual_iterations | completed_visual_iterations",
            "requirement_checks": "pixel_checks | requirement_checks（总数），"
                                   "通过数 = 总数 - pixel_failures/requirement_failures，"
                                   "两者均已记录",
            "elapsed_seconds": "顶层字段；A07 在 timings.elapsed_seconds",
        },
        "correction": {
            "field": "A07.metrics.timings.start",
            "was": "2026-10-14T15:43:30+08:00",
            "now": "2026-10-15T07:40:54+08:00",
            "why": "state_fix.py 误取 suite 级 started_at；已改为 A07 自己的 started_at",
        },
        "tasks": changed,
        "history_preserved": "state-000034.json 与 state-000035.json 及既有事件未改动",
    })

    print(f"回填完成 → {Path(ck).name}")
    for c in changed:
        a = c["after"]
        if a:
            print(f"  {c['task_id']}: req {a['snapshot_requests']} "
                  f"({a['successful']}ok/{a['failed']}fail/{a['retry_requests']}retry) "
                  f"views {a['image_views']} visIter {a['visual_iterations']} "
                  f"checks {a['requirement_checks']} elapsed {a['elapsed_seconds']}s")
        else:
            print(f"  {c['task_id']}: 跳过 — {c.get('note')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
