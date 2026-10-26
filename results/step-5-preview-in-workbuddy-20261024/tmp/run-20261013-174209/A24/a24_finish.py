#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A24 收尾：修正 task-metrics.json 计时、核对交付清单、登记 completed。

计时依据（全部来自文件证据，不凭记忆）：
- started_at  = tmp/run-20261013-174209/A24/a24_solve.py 写入时刻（本题首个产物）
- ended_at    = outputs/run-20261013-174209/A24/task-metrics.json 上次写入时刻
                （本题最后一份交付；本次登记只改状态文件，不回写该时刻）
- elapsed     = 两者之差；其中含一段约 2h22m 的非渲染间隔（精确求解 21:22 完成后
                至首次渲染 23:44 之前），成因为模型侧 429 限流与会话压缩，非本服务
                限流、非用户等待，已在 wall_clock_note 与 snapshot-usage.md 注明。
"""
from __future__ import annotations

import datetime
import json
import os
from pathlib import Path

ROOT = Path(".")
RUN = "run-20261013-174209"
TASK = "A24"
NEXT = "B01"
OUT = f"outputs/{RUN}/{TASK}"
TMP = f"tmp/{RUN}/{TASK}"
STATE = f"outputs/{RUN}/_suite/suite-state.json"
EVENTS = f"tmp/{RUN}/_suite/events.jsonl"
CKPT = f"outputs/{RUN}/_suite/checkpoints"

EXPECT = [
    "execution-board.png", "execution-board.snapshot",
    "decision-brief.png", "decision-brief.snapshot",
    "action-card.png", "action-card.snapshot",
    "schedule.json", "schedule-audit.json", "content-map.json",
    "snapshot-usage.md", "task-metrics.json",
]

START_AT = "2026-10-20T21:18:02+08:00"   # a24_solve.py 首次写入（本题首个产物）
END_AT = "2026-10-21T00:22:23+08:00"     # task-metrics.json 上次写入（本题最后交付）


def now_iso():
    return datetime.datetime.now(
        datetime.timezone(datetime.timedelta(hours=8))).isoformat(timespec="milliseconds")


def rj(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


reqs = [json.loads(l) for l in open(f"{TMP}/requests.jsonl", encoding="utf-8") if l.strip()]
total = len(reqs)
ok = sum(1 for r in reqs if r.get("status") == "ok")
fail = total - ok
dur = round(sum(r.get("elapsed_s") or 0 for r in reqs), 3)
renders = [r for r in reqs if r.get("type") == "render"]
r_ok = sum(1 for r in renders if r.get("status") == "ok")
iters = [json.loads(l) for l in open(f"{TMP}/iterations.jsonl", encoding="utf-8") if l.strip()]
ver = rj(f"{TMP}/verify-result.json")
assert ver["total"] == 0 and not any(ver["problems"].values()), ver

def parse_ts(s: str) -> datetime.datetime:
    for f in ("%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            return datetime.datetime.strptime(s, f)
        except ValueError:
            continue
    raise ValueError(s)


fmt = "%Y-%m-%dT%H:%M:%S%z"
t0 = parse_ts(START_AT)
t1 = parse_ts(END_AT)
wall = (t1 - t0).total_seconds()
first_ok = next(r for r in reqs if r.get("status") == "ok")
first_img = float(first_ok.get("elapsed_s") or 0)

# 墙钟构成（用于如实说明，不把限流/中断算进服务耗时）
solve_end = parse_ts("2026-10-20T21:22:15+08:00")   # optimal-schedules.json
first_render = parse_ts(reqs[0]["ts"])               # 23:44:48
gap = (first_render - solve_end).total_seconds()
render_phase = (parse_ts(reqs[-1]["ts"]) - first_render).total_seconds()

# ---------- 修正 task-metrics.json ----------
m = rj(f"{OUT}/task-metrics.json")
m["timings"].update({
    "started_at": START_AT,
    "ended_at": END_AT,
    "elapsed_seconds": round(wall, 3),
    "first_usable_image_seconds": first_img,
    "user_feedback_wait_seconds": 0,
    "rate_limit_wait_seconds": 0,          # 本服务（open-snapshot）无 429/503 记录
    "queue_wait_seconds": None,
    "request_duration_sum_seconds": dur,
    "server_timing_source": "requests.jsonl elapsed_s（客户端实测，8 次渲染无重试无重叠）",
})
m["timings"]["wall_clock_note"] = (
    f"墙钟 {round(wall)}s = 精确求解约 4min + 非渲染间隔 {round(gap)}s"
    f"（模型侧 429 限流与会话压缩，非本服务限流、非用户等待）"
    f"+ 渲染/复测/报告阶段约 {round(render_phase)}s + 文档收尾"
)
m["timings"]["registered_at"] = now_iso()
m["counts"]["snapshot_requests"] = total
m["counts"]["successful_snapshot_requests"] = ok
m["counts"]["failed_snapshot_requests"] = fail
m["counts"]["render_requests"] = len(renders)
m["counts"]["render_ok"] = r_ok
m["outputs"] = EXPECT
m["unresolved_issues"] = []
with open(f"{OUT}/task-metrics.json", "w", encoding="utf-8") as f:
    json.dump(m, f, ensure_ascii=False, indent=1)

# ---------- 同步 snapshot-usage.md 第 5 节计时 ----------
usage_p = Path(OUT) / "snapshot-usage.md"
u = usage_p.read_text(encoding="utf-8")
old_row = "| 任务总耗时（墙钟） | 约 6518 | 秒 | 含会话中断间隔；纯渲染阶段约 31 分钟 |"
new_row = (f"| 任务总耗时（墙钟） | {round(wall)} | 秒 | "
           f"21:18:02→00:22:23；构成：精确求解约 4min + 非渲染间隔 {round(gap)}s"
           f"（模型侧 429 限流与会话压缩，非本服务限流、非用户等待）"
           f"+ 渲染/复测/报告约 {round(render_phase)}s + 文档收尾 |")
assert old_row in u, "usage 计时行未找到"
u = u.replace(old_row, new_row)
u = u.replace("| 任务开始、结束时间 | 2026-10-20T21:18:02+08:00 → 2026-10-21T00:20+08:00 |",
              "| 任务开始、结束时间 | 2026-10-20T21:18:02+08:00 → 2026-10-21T00:22:23+08:00 |")
usage_p.write_text(u, encoding="utf-8")

missing = [p for p in EXPECT if not os.path.isfile(os.path.join(OUT, p))]
print(f"expected={len(EXPECT)} missing={missing}")
assert not missing, missing

# 每张 PNG 必须有同名 .snapshot，且 PNG 为服务真实响应（尺寸符合题面）
from PIL import Image
for n, (w, h) in (("execution-board", (1920, 1080)),
                  ("decision-brief", (1200, 1600)),
                  ("action-card", (720, 1280))):
    im = Image.open(f"{OUT}/{n}.png")
    assert im.size == (w, h), (n, im.size)
    dsl = (Path(OUT) / f"{n}.snapshot").read_text(encoding="utf-8")
    assert f'width="{w}"' in dsl and f'height="{h}"' in dsl, n
    print(f"{n}: {im.size} OK, dsl declares {w}x{h}")

# ---------- 登记 ----------
state = rj(STATE)
ent = None
for t in state["tasks"]:
    if t["id"] == TASK:
        ent = t
if ent is None:
    ent = {"id": TASK}
    state["tasks"].append(ent)
ent.update({
    "status": "completed",
    "started_at": START_AT,
    "ended_at": END_AT,
    "output_dir": f"{OUT}/", "temp_dir": f"{TMP}/",
    "completed_rounds": [],
    "completed_cases": ["execution-board", "decision-brief", "action-card"],
    "artifacts": [f"{OUT}/{p}" for p in EXPECT],
    "visual_review_evidence": [
        f"{OUT}/execution-board.png（v01/v03/最终整图查看）",
        f"{OUT}/decision-brief.png（v01/v02/最终整图查看）",
        f"{OUT}/action-card.png（v01/v02 整图查看）",
        f"{TMP}/zoom-board-top/design/eng/dep/foot/gap2/finish2.png（执行图分区放大）",
        f"{TMP}/zoom-brief-kpi/kpi2/gantt/gantt2/gantt3/dag2/risk2/head.png（简报分区放大）",
        f"{TMP}/zoom-dag-ch1/ch2/ch3.png（DAG 走线通道放大）",
        f"{TMP}/zoom-card-risk1/risk1b/k3/r10/r10b/bottom/bottom2.png（行动卡分区放大）",
        f"{TMP}/verify-result.json（程序化复测：总问题 0）",
        f"{TMP}/requests.jsonl", f"{TMP}/iterations.jsonl",
    ],
    "unresolved_issues": [],
    "resume_notes": None,
})
state["current_task"] = NEXT
state["current_round"] = None
state["current_case"] = None
state["updated_at"] = now_iso()
with open(STATE, "w", encoding="utf-8") as f:
    json.dump(state, f, ensure_ascii=False, indent=1)

os.makedirs(CKPT, exist_ok=True)
ck = f"state-{TASK}-completed.json"
with open(os.path.join(CKPT, ck), "w", encoding="utf-8") as f:
    json.dump({"checkpoint": ck, "task": TASK, "status": "completed", "ts": now_iso(),
               "current_task": state["current_task"],
               "makespan_minutes": 260, "buffer_minutes": 160}, f,
              ensure_ascii=False, indent=1)
state["last_checkpoint"] = ck
with open(STATE, "w", encoding="utf-8") as f:
    json.dump(state, f, ensure_ascii=False, indent=1)

ev = {"ts": now_iso(), "event": "task_completed", "task_id": TASK,
      "cases": ent["completed_cases"], "next_task": NEXT,
      "artifacts": len(ent["artifacts"]), "snapshot_requests": total,
      "successful": ok, "failed": fail, "iterations": len(iters),
      "verify_problems": ver["total"]}
with open(EVENTS, "a", encoding="utf-8") as f:
    f.write(json.dumps(ev, ensure_ascii=False) + "\n")

print("registered A24 completed; current_task =", state["current_task"])
print(f"requests={total} ok={ok} fail={fail} iterations={len(iters)}")
print(f"wall={round(wall)}s (solve ~4min + gap {round(gap)}s + render/verify/report"
      f" ~{round(render_phase)}s)")
print(f"first_image={first_img}s dur_sum={dur}s")
print("verify problems:", ver["total"])
