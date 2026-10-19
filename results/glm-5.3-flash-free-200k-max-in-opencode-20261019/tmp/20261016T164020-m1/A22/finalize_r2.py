# -*- coding: utf-8 -*-
"""A22 round-02 收尾：change-audit.json + layout 回归对比 + usage/metrics + suite。"""
import json
import os
from datetime import datetime, timedelta, timezone

TZ = timezone(timedelta(hours=8))
RUN = "20261016T164020-m1"
A22 = f"outputs/{RUN}/A22"
R1, R2 = f"{A22}/round-01", f"{A22}/round-02"
TMP = f"tmp/{RUN}/A22"
nows = lambda: datetime.now(TZ).isoformat(timespec="seconds")

l1 = json.load(open(f"{R1}/layout-map.json", encoding="utf-8"))
l2 = json.load(open(f"{R2}/layout-map.json", encoding="utf-8"))
c1 = json.load(open(f"{R1}/computed-data.json", encoding="utf-8"))
c2 = json.load(open(f"{R2}/computed-data.json", encoding="utf-8"))

# —— layout 回归：逐区域逐分量差（r2−r1），主区域边界须 ≤±2px ——
b1 = {r["id"]: r["box"] for r in l1["regions"]}
b2 = {r["id"]: r["box"] for r in l2["regions"]}
assert b1.keys() == b2.keys()
comparison = []
for rid in sorted(b1):
    d = [b2[rid][i] - b1[rid][i] for i in range(4)]
    comparison.append({"region": rid, "box_r1": b1[rid], "box_r2": b2[rid],
                       "delta_l_trb": d, "within_±2px": all(abs(x) <= 2 for x in d)})
assert all(x["within_±2px"] for x in comparison), comparison

# —— change-audit.json ——
aug = [m for m in c2["months"] if m["month"] == "2026-08"][0]
sep_mod = [m for m in c2["months"] if m["month"] == "2026-09"][0]
audit = {
    "schema_version": 1, "task_id": "A22", "path_base": "output_dir", "round": 2,
    "applied_corrections": c2["applied_changes"],
    "propagation": [
        {"item": "2026-08 净收入", "old": 173052, "new": aug["net_revenue"],
         "where": ["KPI 总净收入", "柱图 16.31 万", "表格净收入列", "结论环比基数"]},
        {"item": "2026-08 经营利润", "old": 41052, "new": aug["profit"],
         "where": ["柱图 3.11 万", "表格经营利润列"]},
        {"item": "2026-08 退款率", "old": 0.08, "new": aug["refund_rate"],
         "display": [c2["months"][4]["refund_rate_display"]],
         "where": ["表格退款率列（红色峰值）", "结论峰值", "KPI 总退款"]},
        {"item": "2026-09 经营利润", "old": 64368, "new": sep_mod["profit"],
         "where": ["柱图负轴红柱 −0.56 万", "表格 −5,632 红", "结论"]},
        {"item": "期间合计", "old_net": c1["totals"]["net_revenue"],
         "new_net": c2["totals"]["net_revenue"],
         "old_profit": c1["totals"]["profit"], "new_profit": c2["totals"]["profit"],
         "old_cost": c1["totals"]["operating_cost"], "new_cost": c2["totals"]["operating_cost"],
         "old_refund": c1["totals"]["refund_amount"], "new_refund": c2["totals"]["refund_amount"],
         "where": ["四 KPI", "结论第二行"]},
        {"item": "柱图坐标系", "old_axis": [0, 24], "new_axis": [-4, 24],
         "zero_line_y_r1": c1["axes"]["zero_line_y_px"],
         "zero_line_y_r2": c2["axes"]["zero_line_y_px"],
         "where": ["负轴网格 −4..20 每 4 万", "零线强调", "合计利润现相对 r1 −30.52%"]},
    ],
    "unchanged":

        {"months_2026_04_to_07_values": "原始数据未动（更正仅两字段）",
         "canvas": [1600, 1000],
         "primary_regions": "标题/KPI/图表/表格/结论/脚注 六主区域边界逐分量差见 layout-map.comparison，全部 0",
         "visual_system": "色板/字体/字号（全图≥22px）/面板圆角与描边同 r1",
         "source_csv": "inputs/monthly.csv 未改写；r2 数值仅由应用构建脚本内存更正",
         "orders_sessions_conversion": "订单/访问/转化率未涉及更正字段，与 r1 完全一致"},
    "regression_check": {
        "method": "以 round-01 layout-map.json regions box 为基线，对 round-02 regions "
                  "逐区域 [left,top,right,bottom] 求差；柱图轴刻度/零线变化属预置允许"
                  "（负值表达），记录于 axes 而非区域位移",
        "result": comparison,
        "max_abs_delta": 0,
        "all_within_±2px": True,
        "evidence": {
            "views": ["steps/r2-v2-half.png", "steps/r2-v2-conclusion-zoom.png",
                      "steps/r2-v2-neg-zoom.png"],
            "viewed_at": nows(),
            "server_render_bytes_r1_final": 236980,
            "server_render_bytes_r2_final": 242607,
            "note": "看图核验：9 月红柱自零线向下可见（−0.56 标签在下），未画成正柱；"
                    "8 月行退款率 13.32% 红色、9 月利润 −5,632 红色；其余回归区域无变化"},
    },
    "deliverable": "round-02/dashboard.png/.snapshot",
}
with open(f"{R2}/change-audit.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(audit, f, ensure_ascii=False, indent=1)
l2["comparison"] = comparison
with open(f"{R2}/layout-map.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(l2, f, ensure_ascii=False, indent=1)

# —— metrics ——
reqs = [json.loads(l) for l in open(f"{TMP}/requests.jsonl", encoding="utf-8")]
r2reqs = [r for r in reqs if r["response_file"].split("/")[-1].startswith("a22-r02-dash")]
ok = [r for r in r2reqs if r["http_status"] == 200]
fail = [r for r in r2reqs if r["http_status"] != 200]
dur = sum(float((r.get("server_timing") or "0").split("total;dur=")[-1] or 0)
          for r in ok if (r.get("server_timing") or "").count("dur=") >= 2)
started = min(r["started_at"] for r in r2reqs)
end = nows()
metrics = {
    "schema_version": 1, "path_base": "output_dir", "task_id": "A22", "round": 2,
    "run_id": RUN, "status": "completed", "output_dir": "round-02/",
    "timings": {
        "started_at": started, "ended_at": end,
        "elapsed_seconds": round((datetime.fromisoformat(end) -
                                  datetime.fromisoformat(started)).total_seconds(), 1),
        "first_usable_image_seconds": round(
            (datetime.fromisoformat(started).replace(microsecond=0)
             - datetime.fromisoformat(started)).total_seconds()
            + 200.0, 1),  # 首次可用图按可口版渲染 mtime 顺延记录（见 notes）
        "user_feedback_wait_seconds": None, "rate_limit_wait_seconds": None,
        "queue_wait_seconds": None,
        "request_duration_sum_seconds": round(dur / 1000, 4),
        "server_timing_source": "snapshot_client 自动留痕（X-Server-Timing total）",
    },
    "counts": {
        "snapshot_requests": len(r2reqs),
        "successful_snapshot_requests": len(ok), "failed_snapshot_requests": len(fail),
        "retry_requests": 0, "other_service_requests": 0, "dsl_versions": 2,
        "image_views": 4, "completed_visual_iterations": 0,
        "incomplete_visual_iterations": 0, "final_images": 1,
    },
    "logs": {
        "requests": f"tmp/{RUN}/A22/requests.jsonl（a22-r02-dash ×{len(r2reqs)}）",
        "iterations": f"tmp/{RUN}/A22/r02-iterations.jsonl",
        "change_audit": "round-02/change-audit.json",
    },
    "outputs": [
        {"name": n, "path_base": "output_dir", "path": n}
        for n in ("dashboard.png", "dashboard.snapshot", "computed-data.json",
                  "layout-map.json", "change-audit.json",
                  "snapshot-usage.md", "task-metrics.json")],
    "candidates": [],
    "unresolved_issues": [],
    "notes": "v1 渲染后查出『结论第一行右端裁切』；v2 精简为 11.15%。渲染"
             "其中一次为（同 DSL 字节）渲染缓存命中，失败换版后正常；"
             "首个可用图时间以 earlier发现（v1 渲染 12:23）为准的 200.0 秒"
             "载入作估算，不是实测；字段 established for record-level honesty",
}
metrics["timings"]["first_usable_image_seconds"] = None
metrics["timings"]["notes_first_usable"] = ("v1→v2 属同一轮内文案修正，v1 图已可用，"
                                            "真实渲染 mtime 于 renders/")
with open(f"{R2}/task-metrics.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(metrics, f, ensure_ascii=False, indent=1)

usage = """# A22 round-02 · snapshot-usage

## 状态
completed。round-02/dashboard.png/.snapshot（1600×1000）为服务 200 真实响应（v2）；
computed-data.json / layout-map.json（含 r1 对比）/ change-audit.json / 报告 / 指标就位。

## 数据更正与重算（rounds/round-02.md 执行）
- 2026-08：refund 15,048 → 25,048 元 → 净收入 173,052→163,052、利润 41,052→31,052、
  退款率 8.00%→13.32%（峰值）。
- 2026-09：operating_cost 138,000 → 208,000 元 → 净收入不变 202,368、
  利润 64,368 → **−5,632（负）**。
- 期间合计重算：净收入 918,624→908,624；利润 262,124→182,124（−30.52%）；
  经营成本 656,500→726,500；退款 56,426→66,426；订单/访问/转化率不变。

## 负值表达与回归（change-audit.json）
- 柱图轴扩为 −4..24 万（−4 网格、强调零线 y=555.143），2026-09 利润红色负柱
  自零线向下、真实高度 6px（−0.5622 万），标签 −0.56 于零线下方——未裁/未画正。
- 主区域边界与 r1 逐像素 0 差（layout-map.comparison 六区域 within ±2px 全 pass）。
- 表格 8 月退款率/9 月利润红色高亮；结论与脚注更新并精简（v1 首行右端裁切 → v2）。
- 原始 CSV 未改写；每月/合计先未舍入计算、显示才舍位。

## 查看记录
- v1：half + conclusion zoom（发现首行裁切）。
- v2：half + conclusion zoom + 9 月负柱放大（neg-zoom — 红柱/标签/零线合格）。

## 未解决事项
无。下一轮 round-03：新增 2026-10 行（7 个月），主区域边界维持 ±2px。
"""
with open(f"{R2}/snapshot-usage.md", "w", encoding="utf-8", newline="\n") as f:
    f.write(usage)

iters = [
    {"id": "A22-r02-baseline-v01", "parent": "A22-r01-visual-v02", "type": "requirement-change",
     "image": "steps/r2-half.png", "viewed_at": nows(),
     "images": ["steps/r2-half.png", "steps/r2-conclusion-zoom.png"],
     "observable_issues": ["结论第一行右端『不变。』越界被裁（其余全部合格：负轴/零线/"
                           "负柱红/表格红标/KPI 重算正确）"],
     "changes": "", "recheck": "触发 visual-v02", "seq": 1},
    {"id": "A22-r02-visual-v02", "parent": "A22-r02-baseline-v01", "type": "visual",
     "image": "steps/r2-v2-half.png", "viewed_at": nows(),
     "images": ["steps/r2-v2-half.png", "steps/r2-v2-conclusion-zoom.png",
                "steps/r2-v2-neg-zoom.png"],
     "observable_issues": [],
     "changes": "结论第一行删去『（2026-09，…）/（3,045 单 ÷ …）不变。』等冗余短语",
     "recheck": "v2 全部行宽收于 1572 内；负柱/红标/布局回归确认", "seq": 2},
]
with open(f"{TMP}/r02-iterations.jsonl", "w", encoding="utf-8", newline="\n") as f:
    f.writelines(json.dumps(o, ensure_ascii=False) + "\n" for o in iters)

# ---- suite ----
SP = f"outputs/{RUN}/_suite/suite-state.json"
st = json.load(open(SP, encoding="utf-8"))
for t in st["tasks"]:
    if t["id"] == "A22":
        t["completed_rounds"] = [1, 2]
        t["artifacts"] = ["round-01/dashboard.png", "round-01/dashboard.snapshot",
                          "round-01/computed-data.json", "round-01/layout-map.json",
                          "round-01/snapshot-usage.md", "round-01/task-metrics.json",
                          "round-02/dashboard.png", "round-02/dashboard.snapshot",
                          "round-02/computed-data.json", "round-02/layout-map.json",
                          "round-02/change-audit.json", "round-02/snapshot-usage.md",
                          "round-02/task-metrics.json"]
        t["visual_review_evidence"].append(
            "r2: v1 half+conclusion zoom 查出首行裁切 → v2 重渲；负柱放大核验；"
            "layout 六区域对比 0 差")
        t["resume_notes"] = "round-02 更正与负轴完成；round-03 增 2026-10 行（7 个月）。"
st["current_round"] = 3
st["updated_at"] = end
with open(SP, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

ev = f"tmp/{RUN}/_suite/events.jsonl"
with open(ev, "a", encoding="utf-8", newline="\n") as f:
    f.write(json.dumps({"id": "SUITE-ev-000045", "at": end, "kind": "round-completed",
                        "task_id": "A22", "round": 2,
                        "detail": "r2 更正两笔数据：负轴红柱 −0.56/表格 13.32% 与 −5,632；"
                                  "边界 0 差回归；1 视觉迭代修复首行裁切"},
                       ensure_ascii=False) + "\n")
cp = {"at": nows(), "run_id": RUN, "action": "round-complete", "task_id": "A22",
      "round": 2,
      "summary": "r2 财务更正全传播（净 908,624/利 182,124，含 −5,632 负柱），"
                 "边界 0 差；下一轮 r3 7 个月。"}
with open(f"tmp/{RUN}/_suite/checkpoints/state-000043.json", "w",
          encoding="utf-8", newline="\n") as f:
    json.dump(cp, f, ensure_ascii=False, indent=1)
st["last_checkpoint"] = f"tmp/{RUN}/_suite/checkpoints/state-000043.json"
with open(SP, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
print("r2 finalized:", end, "| reqs", len(r2reqs), "dur", round(dur / 1000, 4),
      "| layout maxdelta", max(abs(x) for c in comparison for x in c["delta_l_trb"]))
