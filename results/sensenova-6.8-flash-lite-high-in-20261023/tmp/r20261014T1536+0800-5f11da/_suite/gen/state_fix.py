"""A07 进度记录的一次性修正（2026-10-15）。

背景：首次执行 suite_update.py complete A07 时写入的记录有两处不自洽：

1. `visual_review_evidence` 塌缩成单个字符串 "audit-routes.json:14/14"。
   原因：旧版 parse_kv 用 dict 收集 key=value，重复的 evidence= 相互覆盖，只留最后一条。
2. `ended_at` 记成 2026-10-15T11:20:05+08:00（状态写入时刻），而同一记录的
   `elapsed_seconds` = 12366 对应的是 07:40:54 → 11:07:00。两者互相矛盾：
   按 ended_at 反算应为 13151 s。原因是旧脚本没有区分
   "任务实际结束" 与 "状态被写入"。

修正（不覆盖历史，按追加语义）：
- ended_at 改回 2026-10-15T11:07:00+08:00，与 A07 的 task-metrics.json
  及 snapshot-usage.md 记录一致（那份报告写于 11:07:34）。
- 新增 recorded_at = 2026-10-15T11:20:05+08:00，如实保留"状态写入比工作结束晚约 13 分钟"。
- 新增 last_artifact_at = 2026-10-15T11:09:45+08:00（最后交付物 task-metrics.json 的
  写入时刻；它是对运行结果的汇总，晚于内容交付物 snapshot-usage.md）。
- visual_review_evidence 重建为 3 条结构化记录，各带 suite_root 相对路径。
- 先前写入的 state-000034.json 与 events.jsonl 第 N 条事件保持原样不动
  （不可覆盖的历史快照 / 只追加日志），本修正另写 state-000035.json 并追加一条
  metrics_corrected 事件说明改了哪些字段、为什么。

运行前设置 SNAPSHOT_RUN_ID。
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))
import suite as S  # noqa: E402

TID = "A07"
ENDED = "2026-10-15T11:07:00+08:00"
RECORDED = "2026-10-15T11:20:05+08:00"
LAST_ARTIFACT = "2026-10-15T11:09:45+08:00"

EVIDENCE = [
    ("C1..C10 网络示意图像素校验", "inspect-map.json", "10/10"),
    ("D1..D10 旅行卡像素校验", "inspect-card.json", "10/10"),
    ("A0..A10 routes.json 审计（含对 inputs/network.json 的独立重算）",
     "audit-routes.json", "14/14"),
]


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if not os.environ.get("SNAPSHOT_RUN_ID"):
        print("需要设置 SNAPSHOT_RUN_ID")
        return 1
    rid = S.run_id()

    state = S.load_state()
    t = next(x for x in state["tasks"] if x["id"] == TID)
    before = {k: t.get(k) for k in ("ended_at", "recorded_at",
                                    "visual_review_evidence", "metrics")}
    before_m = json.loads(json.dumps(before, ensure_ascii=False))

    t["ended_at"] = ENDED
    t["recorded_at"] = RECORDED
    t["last_artifact_at"] = LAST_ARTIFACT
    t["visual_review_evidence"] = [
        {"check": c, "verdict": v, "path_base": "suite_root",
         "report": f"tmp/{rid}/{TID}/{f}"}
        for c, f, v in EVIDENCE]
    t["metrics"]["elapsed_seconds"] = 12366
    t["metrics"]["timings"] = {
        "path_base": "suite_root",
        "start": state["started_at"],
        "end": ENDED,
        "note": ("elapsed_seconds=12366 = 07:40:54 → 11:07:00，与 "
                 "task-metrics.json 一致；状态写入晚于工作结束，"
                 "见 recorded_at 与 last_artifact_at"),
    }

    S.save_state(state)
    ck = S.snapshot_checkpoint(state)
    state["last_checkpoint"] = ck
    S.save_state(state)

    S.append_event({
        "ts": S.now_iso(), "event": "metrics_corrected", "task_id": TID,
        "corrects": "state-000034.json", "checkpoint": ck,
        "reason": [
            "visual_review_evidence 被重复 evidence= 参数覆盖成单字符串，"
            "旧 parse_kv 用 dict 收集键值导致同名键只留最后一条",
            "ended_at 原先记录状态写入时刻 11:20:05，与同记录的 elapsed_seconds=12366"
            "（对应 11:07:00）矛盾；按 ended_at 反算应为 13151 s",
        ],
        "before": before_m,
        "after": {"ended_at": t["ended_at"], "recorded_at": t["recorded_at"],
                  "last_artifact_at": t["last_artifact_at"],
                  "visual_review_evidence": t["visual_review_evidence"],
                  "elapsed_seconds": t["metrics"]["elapsed_seconds"]},
        "history_preserved": ("state-000034.json 与原始 task_completed 事件保留未改；"
                             "本修正写入新检查点并追加本事件"),
    })

    print(f"修正 {TID} 完成 → {Path(ck).name}")
    print("before:", json.dumps(before_m, ensure_ascii=False))
    print("after :", json.dumps({"ended_at": t["ended_at"],
                                 "recorded_at": t["recorded_at"],
                                 "last_artifact_at": t["last_artifact_at"],
                                 "evidence": t["visual_review_evidence"]},
                                ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
