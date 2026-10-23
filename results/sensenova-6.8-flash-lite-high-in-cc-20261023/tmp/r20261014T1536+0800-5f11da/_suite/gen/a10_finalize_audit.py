"""A10 审计收口：把更正后的计数与真实结束时间落盘，追加事件并写新的不可覆盖检查点。

本脚本在 a10-it-15（撤回 A03 跨题回归误报）之后运行，做四件事：
1. task-metrics.json：ended_at / elapsed_seconds / core_elapsed_detail 按真实时间更新，
   counts 与 unresolved_issues 已是更正后的版本，这里只核对一致。
2. suite-state.json：A10 明细的 counts / ended_at / artifacts 与最终报告对齐。
3. events.jsonl：追加一条 task_audit_finalized。
4. checkpoints/：写新的 state-NNNNNN.json（不复用已存在编号）。

用法：
  SNAPSHOT_RUN_ID=<rid> python -I tmp/<rid>/_suite/gen/a10_finalize_audit.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "tools"))
import suite as S  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TZ = timezone(timedelta(hours=8))
STARTED = datetime(2026, 10, 15, 19, 23, 37, tzinfo=TZ)
ENDED = datetime(2026, 10, 15, 22, 31, 0, tzinfo=TZ)
elapsed = int((ENDED - STARTED).total_seconds())
core = 5189

mp = S.rel(S.task_dirs("A10")[0] / "task-metrics.json")
m = json.loads((ROOT / mp).read_text(encoding="utf-8"))

t = m["timings"]
t["ended_at"] = ENDED.isoformat()
t["ended_at_source"] = (
    "审计收口完成时刻：a10-it-15 撤回 A03 跨题回归误报、三份报告更正并同步状态层之后"
)
t["elapsed_seconds"] = elapsed
t["core_elapsed_detail"] = (
    "从 19:23:37 到最终 PNG 与 DSL 交付 20:50:06（%d 秒）；其余 %d 秒为像素审计、三份报告"
    "撰写，以及交付前的 a10-it-15 自我更正" % (core, elapsed - core)
)

# 计数一致性核对：found = fixed + not_reproduced + unresolved
c = m["counts"]
assert c["issues_found"] == c["issues_fixed"] + c["issues_not_reproduced"] + c["issues_unresolved"], (
    "issues_found 与分项之和不一致"
)
assert c["issues_unresolved"] == 1, "应仅剩 a10-u1"
assert [u["id"] for u in m["unresolved_issues"] if u["status"] != "not_reproduced"] == ["a10-u1"], (
    "unresolved_issues 与 counts 不一致"
)

(ROOT / mp).write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

state = S.load_state()
detail = next(d for d in state.get("tasks_detail", []) if d.get("id") == "A10")
detail["status"] = "completed"
detail["ended_at"] = ENDED.isoformat()
detail["counts"] = c
detail["requirement_checks"] = "51/51"

S.save_state(state)

S.append_event({
    "ts": S.now_iso(),
    "event": "task_audit_finalized",
    "task_id": "A10",
    "status": "completed",
    "requirement_checks": "51/51",
    "ended_at": ENDED.isoformat(),
    "elapsed_seconds": elapsed,
    "issues": {
        "found": c["issues_found"],
        "fixed": c["issues_fixed"],
        "not_reproduced": c["issues_not_reproduced"],
        "unresolved": c["issues_unresolved"],
    },
    "corrections_in_final_audit": [
        "④ 文字行扫描 R 通道最小值由 88 更正为 105",
        "④ 前景过渡带宽度由约 17 px 更正为 21 px",
        "圆外取样点 key 由 local_16_100 更正为 left_mid_16_120",
        "审计 JSON 的 bytes 22142 是字符数，更正为 22710 字节并另列 chars",
        "A03 跨题回归判定 a10-u2 由 open 更正为 not_reproduced（误报，已撤回）",
        "④ 文字行 R 最小值、⑤ 圆外 9 通道偏差作为已知偏差显式披露，未掩盖",
    ],
    "artifacts": [
        "outputs/r20261014T1536+0800-5f11da/A10/compositing-lab.png",
        "outputs/r20261014T1536+0800-5f11da/A10/compositing-lab.snapshot",
        "outputs/r20261014T1536+0800-5f11da/A10/composite-audit.json",
        "outputs/r20261014T1536+0800-5f11da/A10/snapshot-usage.md",
        "outputs/r20261014T1536+0800-5f11da/A10/task-metrics.json",
    ],
})

ck = S.snapshot_checkpoint(state)
print("A10 finalized: elapsed=%ds core=%ds remaining=%ds" % (elapsed, core, elapsed - core))
print("counts:", c["issues_found"], "found /", c["issues_fixed"], "fixed /",
      c["issues_not_reproduced"], "not_reproduced /", c["issues_unresolved"], "unresolved")
print("new checkpoint", ck)
