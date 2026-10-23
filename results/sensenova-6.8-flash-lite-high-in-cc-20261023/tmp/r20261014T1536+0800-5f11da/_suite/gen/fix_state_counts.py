"""修正 suite-state.json 两处记录问题。

1. counts_by_status 之前按 tasks_detail 长度算，但 tasks_detail 只记录了 A09–A15
   （A01–A08 没有逐题明细条目），算出 completed=7 与 completed 列表的 15 矛盾。
   改为按 completed 列表与 remaining 列表计数。
2. last_checkpoint 写成 Windows 反斜杠路径，违反 PATHS.md；统一为「/」相对路径。
3. 记录 tasks_detail 覆盖不全这一历史缺口，不补造 A01–A08 的明细。
"""
from __future__ import annotations

import json
import pathlib

HERE = pathlib.Path(__file__).resolve()
RUN_ID = HERE.parents[2].name
SUITE_ROOT = HERE.parents[4]
STATE = SUITE_ROOT / "outputs" / RUN_ID / "_suite" / "suite-state.json"
TS = "2026-10-19T04:50:00+08:00"


def posix(p: str) -> str:
    return p.replace("\\", "/")


def main() -> int:
    state = json.loads(STATE.read_text(encoding="utf-8"))

    # 计数以 completed / remaining 两份清单为准，二者互补且互斥
    n_done = len(state["completed"])
    n_left = len(state["remaining"])
    assert n_done + n_left == state["total_tasks"], (n_done, n_left,
                                                     state["total_tasks"])
    assert not (set(state["completed"]) & set(state["remaining"]))
    state["counts_by_status"] = {"completed": n_done, "in_progress": 0,
                                 "pending": n_left}

    state["last_checkpoint"] = posix(state["last_checkpoint"])
    state["updated_at"] = TS
    state["tasks_detail_note"] = (
        "tasks_detail 只逐题记录了 A09–A15 共 7 条；A01–A08 只出现在 completed 清单里，"
        "没有对应的逐题明细条目（缺起止时间、请求数、指标文件指针）。这是本轮之前遗留的"
        "记录缺口，本轮不补造——补造需要当时的真实产物与日志，凭空填会制造虚假留痕。"
        "counts_by_status 因此以 completed/remaining 清单为基准，而不是 tasks_detail 长度。"
    )

    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n",
                     encoding="utf-8")
    print("counts_by_status:", state["counts_by_status"])
    print("last_checkpoint:", state["last_checkpoint"])
    print("completed:", n_done, "remaining:", n_left, "total:",
          state["total_tasks"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
