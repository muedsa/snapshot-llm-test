"""推进全套进度：更新 suite-state.json、写检查点快照、追加 events.jsonl。

复用 tools/suite.py 的留痕 API（load_state / save_state / snapshot_checkpoint /
append_event），检查点由 suite.py 递增编号且不可覆盖。
运行前需设置环境变量 SNAPSHOT_RUN_ID（见 PATHS.md）。

用法：
  SNAPSHOT_RUN_ID=<rid> python -I tmp/<rid>/_suite/gen/suite_update.py \
      complete <task_id> [--ended ISO8601] requests=N successful=N failed=N \
      retry=N image_views=N visual_iterations=N issues_found=N \
      requirement_checks="34/34" elapsed=秒 \
      [--evidence "检查ID:报告文件:通过/总数"] ...
  SNAPSHOT_RUN_ID=<rid> python -I tmp/<rid>/_suite/gen/suite_update.py \
      start <task_id>

要点：
- `--ended` 指定任务**实际工作结束**时间（通常等于最后一个交付物的写入时刻）。
  缺省时用当前时间。状态写入时刻另存为 `recorded_at`，两者分离，
  避免"状态是晚写的"被误读成"任务晚结束"。
- 同名参数可重复；重复出现的键累积成列表（evidence 需要多条）。
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))
import suite as S  # noqa: E402


def parse_kv(argv: list[str]) -> dict:
    """解析 --flag 之后的 key=value；同名键累积为 list。"""
    out: dict = {}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a.startswith("--"):
            if a == "--ended":
                out["ended"] = argv[i + 1]
                i += 2
            elif a == "--evidence":
                out.setdefault("evidence", []).append(argv[i + 1])
                i += 2
            else:
                raise SystemExit(f"未知参数 {a!r}")
            continue
        k, v = a.split("=", 1)
        try:
            v = int(v)
        except ValueError:
            pass
        if k in out:
            out[k] = [out[k]] if not isinstance(out[k], list) else out[k]
            out[k].append(v)
        else:
            out[k] = v
        i += 1
    out.setdefault("evidence", [])
    return out


def find_task(state: dict, tid: str) -> dict:
    for t in state["tasks"]:
        if t["id"] == tid:
            return t
    raise KeyError(tid)


def art_list(tid: str) -> list[str]:
    out = Path(f"outputs/{S.run_id()}/{tid}")
    if not out.is_dir():
        return []
    return sorted(S.rel(p) for p in out.iterdir() if p.is_file())


def evidence_records(tid: str, items: list) -> list[dict]:
    """'C1..C10:inspect-map.json:10/10' -> 结构化证据条目（路径相对 suite_root）。"""
    out: list[dict] = []
    for it in items:
        parts = str(it).split(":")
        cid, fname = parts[0], parts[1] if len(parts) > 1 else ""
        verdict = parts[2] if len(parts) > 2 else ""
        out.append({"check": cid, "verdict": verdict,
                    "path_base": "suite_root",
                    "report": f"tmp/{S.run_id()}/{tid}/{fname}" if fname else None})
    return out


def refresh_progress(state: dict) -> dict:
    """重算全套进度摘要与总交付物清单（只反映磁盘事实，不宣称完成）。"""
    from collections import Counter
    by = Counter(t.get("status") or "pending" for t in state["tasks"])
    order = state.get("task_order") or [t["id"] for t in state["tasks"]]
    done_ids = [t["id"] for t in state["tasks"]
                if t.get("status") == "completed"]
    pending = [tid for tid in order if tid not in done_ids]

    rc = Path("run-config.json")
    required: list[str] = []
    if rc.is_file():
        required = json.loads(rc.read_text(encoding="utf-8")) \
                              .get("suite_required_artifacts") or []
    suite_out = Path(f"outputs/{S.run_id()}/_suite")
    arts = []
    for name in required:
        p = suite_out / name
        arts.append({
            "path": S.rel(p) if p.exists() else f"outputs/{S.run_id()}/_suite/{name}",
            "required": True,
            "exists": p.exists(),
            # pending = 还没写（题没做完，正常）；missing = 应该已经写了却没有
            "status": "delivered" if p.exists() else (
                "pending" if pending else "missing"),
        })
        if name == "suite-state.json" and p.exists():
            arts[-1]["note"] = "当前进度指针；历史版本在检查点快照里"

    state["suite_artifacts"] = arts
    state["suite_progress"] = {
        "total_tasks": len(order),
        "counts_by_status": dict(by),
        "completed": done_ids,
        "current_task": state.get("current_task"),
        "remaining": pending,
        "required_suite_artifacts": required,
        "required_artifacts_delivered": sum(1 for a in arts if a["exists"]),
        "completed_all": not pending and all(a["exists"] for a in arts),
    }
    return state["suite_progress"]


def do_start(tid: str, kv: dict) -> None:
    now = S.now_iso()
    state = S.load_state()
    t = find_task(state, tid)
    t["status"] = "in_progress"
    t["started_at"] = kv.get("ended") or now
    t["output_dir"] = t.get("output_dir") or f"outputs/{S.run_id()}/{tid}"
    t["temp_dir"] = t.get("temp_dir") or f"tmp/{S.run_id()}/{tid}"
    state["current_task"] = tid
    state["status"] = "in_progress"
    S.save_state(refresh_progress(state))
    S.append_event({"ts": S.now_iso(), "event": "task_started", "task_id": tid,
                    "status": "in_progress",
                    "output_dir": t["output_dir"], "temp_dir": t["temp_dir"]})
    print(f"started {tid}")


def do_complete(tid: str, kv: dict) -> None:
    """标完成。ended = 实际工作结束（默认 now）；recorded_at = 状态写入时刻。"""
    recorded = S.now_iso()
    ended = kv.get("ended") or recorded
    state = S.load_state()
    t = find_task(state, tid)
    t["status"] = "completed"
    t["ended_at"] = ended
    t["recorded_at"] = recorded
    t["output_dir"] = t.get("output_dir") or f"outputs/{S.run_id()}/{tid}"
    t["temp_dir"] = t.get("temp_dir") or f"tmp/{S.run_id()}/{tid}"
    t["artifacts"] = art_list(tid)
    t["visual_review_evidence"] = evidence_records(tid, kv.get("evidence", []))
    t["unresolved_issues"] = []
    t["metrics"] = {
        "snapshot_requests": kv.get("requests"),
        "successful": kv.get("successful"),
        "failed": kv.get("failed"),
        "retry_requests": kv.get("retry"),
        "image_views": kv.get("image_views"),
        "visual_iterations": kv.get("visual_iterations"),
        "issues_found": kv.get("issues_found"),
        "requirement_checks": kv.get("requirement_checks"),
        "elapsed_seconds": kv.get("elapsed"),
        "source": {"path_base": "suite_root",
                   "task_metrics": f"outputs/{S.run_id()}/{tid}/task-metrics.json",
                   "requests_log": f"tmp/{S.run_id()}/{tid}/requests.jsonl",
                   "iterations_log": f"tmp/{S.run_id()}/{tid}/iterations.jsonl"},
    }

    order = state.get("task_order") or [x["id"] for x in state["tasks"]]
    idx = order.index(tid)
    state["current_task"] = order[idx + 1] if idx + 1 < len(order) else None
    S.save_state(refresh_progress(state))
    ck = S.snapshot_checkpoint(state)
    state["last_checkpoint"] = ck
    S.save_state(state)
    S.append_event({"ts": recorded, "event": "task_completed", "task_id": tid,
                    "status": "completed", "ended_at": ended,
                    "recorded_at": recorded, "checkpoint": ck,
                    "artifacts": t["artifacts"],
                    "snapshot_requests": kv.get("requests"),
                    "successful": kv.get("successful"),
                    "failed": kv.get("failed"),
                    "retry_requests": kv.get("retry"),
                    "image_views": kv.get("image_views"),
                    "visual_iterations": kv.get("visual_iterations"),
                    "issues_found": kv.get("issues_found"),
                    "requirement_checks": kv.get("requirement_checks"),
                    "elapsed_seconds": kv.get("elapsed"),
                    "visual_review_evidence": t["visual_review_evidence"]})
    print(f"completed {tid} ended_at={ended} recorded_at={recorded}")
    print(f"  checkpoint {Path(ck).name}; current_task={state['current_task']}")
    print(f"  artifacts {len(t['artifacts'])}, evidence {len(t['visual_review_evidence'])}")


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if not os.environ.get("SNAPSHOT_RUN_ID"):
        print(__doc__)
        print("（需要设置 SNAPSHOT_RUN_ID）")
        return 1
    action = sys.argv[1]
    ck_flag = "--checkpoint" in sys.argv[2:]
    if action == "refresh":
        # 重算进度摘要与总交付物清单，不动任务字段、不加事件；
        # 加 --checkpoint 时另写一个检查点，使恢复点与当前状态一致
        state = S.load_state()
        p = refresh_progress(state)
        S.save_state(state)
        print(f"进度已刷新: {p['counts_by_status']}")
        print(f"  已完成 {len(p['completed'])}/{p['total_tasks']}"
              f"，当前 {p['current_task']}，剩余 {len(p['remaining'])} 题")
        print(f"  总交付物 {p['required_artifacts_delivered']}/"
              f"{len(p['required_suite_artifacts'])} 已落地，"
              f"completed_all={p['completed_all']}")
        if ck_flag:
            ck = S.snapshot_checkpoint(state)
            state["last_checkpoint"] = ck
            S.save_state(state)
            print(f"  检查点 {Path(ck).name}（内容 = 当前状态）")
        return 0
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    tid = sys.argv[2]
    kv = parse_kv(sys.argv[3:])
    if action == "start":
        do_start(tid, kv)
    elif action == "complete":
        do_complete(tid, kv)
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
