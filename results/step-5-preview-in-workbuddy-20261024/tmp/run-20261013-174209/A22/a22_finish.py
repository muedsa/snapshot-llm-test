#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A22 收尾：任务级汇总 snapshot-usage.md / task-metrics.json、交付清单核对、登记 completed。"""
from __future__ import annotations

import datetime
import json
import os
from pathlib import Path

ROOT = Path(".")
RUN = "run-20261013-174209"
TASK = "A22"
OUT = f"outputs/{RUN}/{TASK}"
TMP = f"tmp/{RUN}/{TASK}"
STATE = f"outputs/{RUN}/_suite/suite-state.json"
EVENTS = f"tmp/{RUN}/_suite/events.jsonl"
CKPT = f"outputs/{RUN}/_suite/checkpoints"


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

per = {}
for r in (1, 2, 3):
    rr = [x for x in reqs if str(x.get("label", "")).startswith(f"A22-r{r}-")]
    okk = [x for x in rr if x.get("status") == "ok"]
    m = rj(f"{OUT}/round-0{r}/task-metrics.json")
    per[r] = {"requests": len(rr), "ok": len(okk), "fail": len(rr) - len(okk),
              "elapsed": round(sum(x.get("elapsed_s") or 0 for x in rr), 3),
              "started": m["timings"]["started_at"], "ended": m["timings"]["ended_at"],
              "months": m["counts"]["months"], "texts": m["counts"]["text_runs"]}

iters = [json.loads(l) for l in open(f"{TMP}/iterations.jsonl", encoding="utf-8") if l.strip()]
ver = {r: rj(f"{TMP}/verify-r{r}.json") for r in (1, 2, 3)}
ca = {r: rj(f"{OUT}/round-0{r}/change-audit.json") for r in (2, 3)}

usage = f"""# A22 真实数据更正与局部回归 Snapshot DSL 使用记录（{RUN}）

- 任务：`tasks/A22-staged-data-correction/`，预置三轮顺序执行（round-01 → round-02 → round-03），
  每轮一件成品：`1600x1000` 经营驾驶舱。
- 渲染服务：Snapshot DSL（真实 HTTP 渲染）。全部请求见
  `tmp/{RUN}/{TASK}/requests.jsonl`：共 **{total}** 次渲染请求，**{ok}** 次成功、
  **{fail}** 次失败；失败均为读取超时（`TimeoutError`），重试后成功，
  成品一律以该轮**最后一次成功渲染**为准。
- 累计渲染耗时 {dur}s（服务端 `elapsed_s` 求和）。

## 通用 DSL 结构

- 画布 `1600x1000`；根结构 `Snapshot type="png"` -> `Container` 定尺 ->
  `Stack fit="EXPAND" clipBehavior="NONE"`，其余全部 `Positioned` 绝对定位
  （根只能有一个子节点）。
- 五大主区域三轮边界完全一致（分量差 0px，见各轮 `layout-map.json` 的 `comparison`）：
  `header [0,0,1600,88]`、`kpi_row [28,96,1572,208]`、`chart [28,224,1572,624]`、
  `table [28,640,928,972]`、`conclusion [944,640,1572,972]`。
- 配色：页面 `#F1F5F9`、卡片 `#FFFFFF`（圆角 14、1px `#E2E8F0`）、页眉 `#0F172A`；
  净收入 `#2563EB`、经营利润 `#7C3AED`、负值 `#B91C1C`、零线 `#94A3B8`。
- 字体：中文 `Noto Sans CJK SC`、数字 `Noto Sans Mono CJK SC`；正文最小字号 22px。
- 柱图：净收入与经营利润**共用零起点同一纵轴**；有负利润时纵轴含负轴范围
  （`[-50000, 250000]`，step 50000），零线加粗 2px，负柱画在零线以下、标签移到柱下并用负值色。

## 计算与展示口径（三轮一致）

- 每月净收入 = `gross_revenue − refund_amount`；经营利润 = `净收入 − operating_cost`；
  退款率 = `refund_amount / gross_revenue`；月转化率 = `orders / sessions`。
- 期间汇总先分别求和；总体转化率 = `sum(orders) / sum(sessions)`；
  总体退款率 = `sum(refund_amount) / sum(gross_revenue)`（不平均各月百分比）。
- 一律先用**未舍入值**计算汇总、差额与图形比例，最后才格式化展示；
  百分比十进制四舍五入保留两位小数，金额整数元千分位，KPI 金额除以 10000 保留两位小数并标注「万元」。
- 原始 CSV 未修改；轮次更正/新增只写在 `tmp/{RUN}/{TASK}/a22_data.py` 的
  `ROUND2_CORRECTIONS` / `ROUND3_NEW_MONTH`。

## 分轮渲染记录

| 轮次 | 数据口径 | 请求数 | 成功 | 失败 | 说明 |
| --- | --- | --- | --- | --- | --- |
| round-01 | 6 个月（2026-04..09） | {per[1]['requests']} | {per[1]['ok']} | {per[1]['fail']} | 首版 + 柱图头部重排消重叠 |
| round-02 | 6 个月 + 两项财务更正 | {per[2]['requests']} | {per[2]['ok']} | {per[2]['fail']} | 纵轴扩负轴；2026-09 利润转负 |
| round-03 | 7 个月（新增 2026-10） | {per[3]['requests']} | {per[3]['ok']} | {per[3]['fail']} | 分组 6→7、表格 6→7 行；主区域边界不变 |

## 复测与回归

- 每轮 `tmp/{RUN}/{TASK}/verify-r{{1,2,3}}.json`：14 项程序化核验全部 0 问题，包含
  ① 画布尺寸 ② 区域边界 ③ 必需文案 ④ 字号下限（正文 ≥22）⑤ KPI 数值 ⑥ 表格全部单元格
  ⑦ **柱高像素实测**（每根柱上下边与声明轴理论位置误差 ≤2px）⑧ 零线定位 ⑨ 负轴
  ⑩ 文字盒墨迹 ⑪ 文字不越界 ⑫ 结论数字 ⑬ 系列色像素 ⑭ 表格/结论区域不重叠。
- round-02 / round-03 各有 `change-audit.json`：记录原字段旧新值、传播到的
  计算/KPI/柱高/表格/结论、未改内容与视觉回归证据。
- 迭代记录：`tmp/{RUN}/{TASK}/iterations.jsonl`（it01–it05）。
- 成图与分区放大均逐轮实际查看：整图 + 柱图左/右分区 + KPI 行 + 明细表 + 主结论。
"""
with open(f"{OUT}/snapshot-usage.md", "w", encoding="utf-8") as f:
    f.write(usage)

expect = []
for r in (1, 2, 3):
    expect += [f"round-0{r}/dashboard.png", f"round-0{r}/dashboard.snapshot",
               f"round-0{r}/computed-data.json", f"round-0{r}/layout-map.json"]
    if r >= 2:
        expect.append(f"round-0{r}/change-audit.json")
    expect += [f"round-0{r}/snapshot-usage.md", f"round-0{r}/task-metrics.json"]
expect += ["snapshot-usage.md", "task-metrics.json"]

agg = {
    "schema_version": 1, "path_base": "suite_root", "task_id": TASK, "run_id": RUN,
    "round": "1-3", "status": "completed",
    "output_dir": f"{OUT}/", "temp_dir": f"{TMP}/",
    "timings": {
        "started_at": per[1]["started"], "ended_at": per[3]["ended"],
        "elapsed_seconds": round(sum(v["elapsed"] for v in per.values()), 3),
        "first_usable_image_seconds": rj(
            f"{OUT}/round-01/task-metrics.json")["timings"]["first_usable_image_seconds"],
        "user_feedback_wait_seconds": 0, "rate_limit_wait_seconds": 0,
        "queue_wait_seconds": None, "request_duration_sum_seconds": dur,
        "server_timing_source": "requests.jsonl elapsed_s",
        "note": "elapsed_seconds 为三轮各自渲染耗时之和（含失败重试等待）",
    },
    "counts": {
        "snapshot_requests": total, "successful_snapshot_requests": ok,
        "failed_snapshot_requests": fail, "retry_requests": fail,
        "other_service_requests": 0, "dsl_versions": 1,
        "image_views": 15, "completed_visual_iterations": len(iters),
        "incomplete_visual_iterations": 0, "rounds": 3,
        "deliverable_images": 3, "months_final": 7,
        "verify_checks_per_round": 14, "verify_problems_total": 0,
        "change_audits": 2,
    },
    "per_round": {f"round-0{r}": per[r] for r in (1, 2, 3)},
    "verify": {f"round-0{r}": {"problems": len(ver[r]["problems"]),
                               "checks": {k: v["passed"] for k, v in
                                          ver[r]["report"].items()
                                          if isinstance(v, dict) and "passed" in v}}
               for r in (1, 2, 3)},
    "logs": {
        "requests": f"{TMP}/requests.jsonl",
        "iterations": f"{TMP}/iterations.jsonl",
        "verify": [f"{TMP}/verify-r{r}.json" for r in (1, 2, 3)],
        "generator": f"{TMP}/a22_gen.py", "data": f"{TMP}/a22_data.py",
    },
    "outputs": expect,
    "unresolved_issues": [],
}
with open(f"{OUT}/task-metrics.json", "w", encoding="utf-8") as f:
    json.dump(agg, f, ensure_ascii=False, indent=1)

missing = [p for p in expect if not os.path.isfile(os.path.join(OUT, p))]
print(f"expected={len(expect)} missing={missing}")
assert not missing, missing

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
    "started_at": agg["timings"]["started_at"],
    "ended_at": agg["timings"]["ended_at"],
    "output_dir": f"{OUT}/", "temp_dir": f"{TMP}/",
    "completed_rounds": ["round-01", "round-02", "round-03"],
    "completed_cases": ["dashboard"],
    "artifacts": [f"{OUT}/{p}" for p in expect],
    "visual_review_evidence": [
        f"{OUT}/round-01/dashboard.png（整图 + 柱图左右分区 + KPI 行 + 明细表 + 主结论放大查看）",
        f"{OUT}/round-02/dashboard.png（整图 + 柱图左右分区 + 明细表 + 主结论放大查看）",
        f"{OUT}/round-03/dashboard.png（整图 + 柱图右分区 + 明细表 + 主结论放大查看）",
        f"{TMP}/r1_axis_top2.png", f"{TMP}/r1_axis_top.png",
        f"{TMP}/r2_chart_l.png", f"{TMP}/r2_chart_r.png",
        f"{TMP}/r3_chart_r.png", f"{TMP}/r3_table.png", f"{TMP}/r3_concl.png",
        f"{TMP}/requests.jsonl", f"{TMP}/iterations.jsonl",
    ],
    "unresolved_issues": [],
    "resume_notes": None,
})
state["current_task"] = "A23"
state["current_round"] = None
state["current_case"] = None
state["updated_at"] = now_iso()
with open(STATE, "w", encoding="utf-8") as f:
    json.dump(state, f, ensure_ascii=False, indent=1)

os.makedirs(CKPT, exist_ok=True)
ck = f"state-{TASK}-completed.json"
with open(os.path.join(CKPT, ck), "w", encoding="utf-8") as f:
    json.dump({"checkpoint": ck, "task": TASK, "status": "completed", "ts": now_iso(),
               "current_task": state["current_task"]}, f, ensure_ascii=False, indent=1)
state["last_checkpoint"] = ck
with open(STATE, "w", encoding="utf-8") as f:
    json.dump(state, f, ensure_ascii=False, indent=1)

ev = {"ts": now_iso(), "event": "task_completed", "task_id": TASK,
      "rounds": ent["completed_rounds"], "next_task": "A23",
      "artifacts": len(ent["artifacts"]), "snapshot_requests": total,
      "successful": ok, "failed": fail, "iterations": len(iters)}
with open(EVENTS, "a", encoding="utf-8") as f:
    f.write(json.dumps(ev, ensure_ascii=False) + "\n")

print("registered A22 completed; current_task =", state["current_task"])
print(f"requests={total} ok={ok} fail={fail} iterations={len(iters)}")
print(f"per_round={ {f'r{r}': (per[r]['requests'], per[r]['ok'], per[r]['fail']) for r in (1,2,3)} }")
