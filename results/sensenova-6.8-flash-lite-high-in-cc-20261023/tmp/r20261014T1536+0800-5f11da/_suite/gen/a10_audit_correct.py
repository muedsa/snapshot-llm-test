"""更正 A10 的 A03 跨题回归误报：同步 suite-state.json、追加事件、写新检查点。

背景：A10 审计最初把 A03 的 22 处 #33FFFFFF 当成跨题回归（status: open）。
核验后发现那 22 处全部在已被 v2 取代的探针草稿里，A03 交付件不含 α-首位色，
且 A03 自身迭代早已独立记录同一契约（I-07 / alpha-check.json）。
本脚本把 suite-state.json 中 A10 明细的 unresolved_issues 换成更正后的版本，
追加一条 audit_corrected 事件，并写新的不可覆盖检查点。
已写入 outputs/ 的三份报告已另行更正，本脚本只补齐状态层。

用法：
  SNAPSHOT_RUN_ID=<rid> python -I tmp/<rid>/_suite/gen/a10_audit_correct.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "tools"))
import suite as S  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

state = S.load_state()
dets = state.get("tasks_detail", [])
targets = [d for d in dets if d.get("id") == "A10"]
if not targets:
    raise SystemExit("suite-state.json 中没有 A10 明细，拒绝猜测")
detail = targets[0]

mp = S.rel(S.task_dirs("A10")[0] / "task-metrics.json")
metrics = json.loads((ROOT / mp).read_text(encoding="utf-8"))
fixed = metrics["unresolved_issues"]

detail["unresolved_issues"] = fixed
detail["audit_corrections"] = [
    {
        "corrected_at": S.now_iso(),
        "what": "a10-u2 由 status=open 改为 status=not_reproduced",
        "why": (
            "原判定只统计了 tmp/<run_id>/A03/ 下所有 .snapshot 的 8 位色，"
            "未区分交付件与已被取代的探针草稿。22 处 #33FFFFFF 全部位于 "
            "v0-original / p1..p5 / probe2-3-4-5 / req-* 等早期探针文件。"
        ),
        "verification": [
            "outputs/<run_id>/A03/system-pulse.snapshot 的 8 位色全部 α 在末位"
            "（#00000040×3、#FFFFFF66×1、#FFFFFF33×1、#FFFFFF1A×1），#33FFFFFF 出现 0 次",
            "outputs/<run_id>/A03/system-pulse.png（1280×800、1894 色）全图统计："
            "(51,255,255)/(179,255,255)/(179,51,65) 各 0 像素，且无任何 R<120 且 G≥200 且 B≥200 的青色值",
            "A03 自身 alpha-check.json 已记录同一契约（I-07 / I-08），A10 是独立复现而非首次发现",
        ],
        "impact": "A03 交付件无需重渲，无需修改 A03 的快照、指标或报告",
    }
]

S.save_state(state)

S.append_event({
    "ts": S.now_iso(),
    "event": "audit_corrected",
    "task_id": "A10",
    "issue_id": "a10-u2",
    "from_status": "open",
    "to_status": "not_reproduced",
    "summary": "撤回对 A03 的跨题回归判定：22 处 #33FFFFFF 全部在已被取代的探针草稿中，A03 交付件颜色正确",
    "verification": detail["audit_corrections"][0]["verification"],
    "prior_finding": "A03 在自身迭代中已独立发现同一契约（I-07 / I-08），A10 的独立复现不应记为首次发现",
    "corrected_records": [
        "outputs/r20261014T1536+0800-5f11da/A10/composite-audit.json",
        "outputs/r20261014T1536+0800-5f11da/A10/task-metrics.json",
        "outputs/r20261014T1536+0800-5f11da/A10/snapshot-usage.md",
    ],
})

ck = S.snapshot_checkpoint(state)
print("corrected A10 a10-u2 -> not_reproduced")
print("new checkpoint", ck)
