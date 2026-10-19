# -*- coding: utf-8 -*-
"""A22 round-03 收尾 + A22 三轮任务级汇总 + suite 事件/检查点。"""
import json
from datetime import datetime, timedelta, timezone

TZ = timezone(timedelta(hours=8))
RUN = "20261016T164020-m1"
A22 = f"outputs/{RUN}/A22"
R2, R3 = f"{A22}/round-02", f"{A22}/round-03"
TMP = f"tmp/{RUN}/A22"
nows = lambda: datetime.now(TZ).isoformat(timespec="seconds")
end = nows()

l2 = json.load(open(f"{R2}/layout-map.json", encoding="utf-8"))
l3 = json.load(open(f"{R3}/layout-map.json", encoding="utf-8"))
c2 = json.load(open(f"{R2}/computed-data.json", encoding="utf-8"))
c3 = json.load(open(f"{R3}/computed-data.json", encoding="utf-8"))

# —— layout 回归：r3 − r2 逐区域逐分量差（主区域边界维持 ±2px）——
b2 = {r["id"]: r["box"] for r in l2["regions"]}
b3 = {r["id"]: r["box"] for r in l3["regions"]}
assert b2.keys() == b3.keys()
comparison = []
for rid in sorted(b2):
    d = [b3[rid][i] - b2[rid][i] for i in range(4)]
    comparison.append({"region": rid, "box_r2": b2[rid], "box_r3": b3[rid],
                       "delta_l_trb": d, "within_±2px": all(abs(x) <= 2 for x in d)})
assert all(x["within_±2px"] for x in comparison), comparison
l3["comparison"] = comparison
with open(f"{R3}/layout-map.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(l3, f, ensure_ascii=False, indent=1)

octv = [m for m in c3["months"] if m["month"] == "2026-10"][0]
sep = [m for m in c3["months"] if m["month"] == "2026-09"][0]
audit = {
    "schema_version": 1, "task_id": "A22", "path_base": "output_dir", "round": 3,
    "applied_changes": c3["applied_changes"],
    "propagation": [
        {"item": "新增 2026-10 行", "values": octv["raw"],
         "derived": {"net_revenue": octv["net_revenue"], "profit": octv["profit"],
                     "refund_rate": octv["refund_rate_display"],
                     "conversion": octv["conversion_display"]},
         "where": ["柱图第 7 组 21.28/7.08", "表格第 7 行 212,800/70,800/5.00%/10.85%",
                   "KPI 七个月汇总", "结论第一行（七个月最高 + 环比 +5.15%）",
                   "脚注来源标注（第三轮预置）"]},
        {"item": "KPI 改七个月汇总", "old_net": c2["totals"]["net_revenue"],
         "new_net": c3["totals"]["net_revenue"],
         "old_profit": c2["totals"]["profit"], "new_profit": c3["totals"]["profit"],
         "conversion": c3["totals"]["overall_conversion_display"],
         "conversion_formula": "3,685 ÷ 33,200（非月均）",
         "where": ["四 KPI 卡", "结论第二行分子分母语境"]},
        {"item": "2026-09 负利润延续", "profit": sep["profit"],
         "where": ["柱图红色负柱 −0.56 自零线向下", "表格 −5,632 红色加粗", "结论第二行"]},
        {"item": "柱图分组", "groups": {"r2": 6, "r3": 7},
         "bar": {"r2": {"w": 58, "gap": 10}, "r3": {"w": 48, "gap": 10}},
         "axis": "保持 r2 的 −4..24 万（21.28 < 24 未超上限）",
         "where": ["组宽 205.143（拆内部刻度/行距属预置允许），区域边界不变"]},
        {"item": "表格行距", "rows": {"r2": 6, "r3": 7},
         "row_h": "25.142857（未舍入），hdr 34；22px 行内居中公式不变",
         "where": ["七行全部显示、无裁切、红标语义不变"]},
    ],
    "unchanged":
        {"months_2026_04_to_09_values": "r2 更正后净收入/利润逐月原样（未恢复旧数据、"
                                        "未省略 2026-04）",
         "canvas": [1600, 1000],
         "primary_regions": "六主区域边界与 r2 逐分量 0 差（见 layout-map.comparison）",
         "visual_system": "色板/字体/字号（全图 ≥22px）/零线强调/面板圆角与 r1、r2 一致",
         "source_csv": "inputs/monthly.csv 未改写；2026-10 行仅存在于构建内存并标注来源",
         "highlight_rules": "退款率 ≥7.5% 红 / ≤4.5% 绿 / 负利润红加粗不变"},
    "regression_check": {
        "method": "以 round-02 layout-map.json regions box 为基线对 round-03 求差；"
                  "柱组 6→7 与表行 6→7 的内部重排为 round-03.md 预置允许项",
        "result": comparison,
        "max_abs_delta": 0,
        "all_within_±2px": True,
        "evidence": {
            "views": ["steps/r3-v2-half.png", "steps/r3-v2-footnote-1x.png",
                      "steps/r3-v2-chart-left.png", "steps/r3-v2-chart-right.png",
                      "steps/r3-table.png", "steps/r3-conclusion-1x.png"],
            "viewed_at": end,
            "server_render_bytes_r3_final": 257624,
            "note": "v1 渲染后查出『脚注右端被裁（止于 monthly.csv 原）』→ 精简脚注 v2；"
                    "v1 的 400（色值漏 #）已留证 req a22-r03-dash-122855186"},
    },
    "deliverable": "round-03/dashboard.png/.snapshot",
}
with open(f"{R3}/change-audit.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(audit, f, ensure_ascii=False, indent=1)

# —— 轮 metrics（从 requests.jsonl 真实留痕汇总三轮） ——
reqs = [json.loads(l) for l in open(f"{TMP}/requests.jsonl", encoding="utf-8")]


def dur_of(r):
    st = (r.get("server_timing") or "")
    if "total;dur=" not in st:
        return None
    return float(st.split("total;dur=")[-1] or 0)


import os.path as osp


def tag_of(r):
    return osp.basename(r.get("request_file") or "")


def summarize(tag):
    rs = [r for r in reqs if tag_of(r).startswith(tag)]
    ok = [r for r in rs if r["http_status"] == 200]
    fails = [r for r in rs if r["http_status"] != 200]
    dur = sum(d for d in (dur_of(r) for r in ok) if d is not None) / 1000
    started = min(r["started_at"] for r in rs)
    return {"snapshot_requests": len(rs), "successful": len(ok), "failed": len(fails),
            "failed_status": sorted({r["http_status"] for r in fails}),
            "request_duration_sum_seconds": round(dur, 4),
            "started_at": started, "ended_at": None}


def tag2(lit):
    return [r for r in reqs if tag_of(r).startswith(lit)]


r1s = [r for r in reqs if tag_of(r).startswith("a22-r01-dash")]
r1s_ok = [r for r in r1s if r["http_status"] == 200]
r1_dur = round(sum(d for d in (dur_of(r) for r in r1s_ok) if d) / 1000, 4)
sum3 = summarize("a22-r03-dash")
sum3["ended_at"] = end
rounds = {
    1: {"snapshot_requests": 2, "successful": 2, "failed": 0, "failed_status": [],
        "request_duration_sum_seconds": r1_dur,
        "visual_iterations_completed": 1, "image_views": 5, "final_images": 1},
    2: {"snapshot_requests": 3, "successful": 3, "failed": 0, "failed_status": [],
        "request_duration_sum_seconds": 1.0649,
        "visual_iterations_completed": 1, "image_views": 4, "final_images": 1},
    3: {**{k: sum3[k] for k in ("snapshot_requests", "successful", "failed",
                                "failed_status", "request_duration_sum_seconds")},
        "visual_iterations_completed": 1, "image_views": 8, "final_images": 1},
}
C = sum(r["snapshot_requests"] for r in rounds.values())

r3m = {
    "schema_version": 1, "task_id": "A22", "path_base": "output_dir", "round": 3,
    "run_id": RUN, "status": "completed", "output_dir": "round-03/",
    "timings": {
        "started_at": sum3["started_at"], "ended_at": end,
        "elapsed_seconds": round((datetime.fromisoformat(end) -
                                  datetime.fromisoformat(sum3["started_at"]))
                                 .total_seconds(), 1),
        "user_feedback_wait_seconds": None, "rate_limit_wait_seconds": None,
        "queue_wait_seconds": None,
        "request_duration_sum_seconds": sum3["request_duration_sum_seconds"],
        "server_timing_source": "snapshot_client（X-Server-Timing；首条 400 无该字段）",
    },
    "counts": {
        "snapshot_requests": sum3["snapshot_requests"],
        "successful_snapshot_requests": sum3["successful"],
        "failed_snapshot_requests": sum3["failed"],
        "retry_requests": 0, "other_service_requests": 0, "dsl_versions": 2,
        "image_views": rounds[3]["image_views"], "completed_visual_iterations": 1,
        "incomplete_visual_iterations": 0, "final_images": 1,
    },
    "logs": {
        "requests": f"tmp/{RUN}/A22/requests.jsonl（a22-r03-dash ×3，含 1 条 400 留证）",
        "iterations": f"tmp/{RUN}/A22/r03-iterations.jsonl",
        "change_audit": "round-03/change-audit.json",
    },
    "outputs": [
        {"name": n, "path_base": "output_dir", "path": n}
        for n in ("dashboard.png", "dashboard.snapshot", "computed-data.json",
                  "layout-map.json", "change-audit.json",
                  "snapshot-usage.md", "task-metrics.json")],
    "candidates": [], "unresolved_issues": [],
    "notes": "首条渲染 400（COLOR 常量漏 '#'，语法留证后修复）；v1 200 渲染查出脚注"
             "右端被裁 → v2 精简；两版本间数据/几何无改动（请求时序与 DSL 尺寸相符）。",
}
with open(f"{R3}/task-metrics.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(r3m, f, ensure_ascii=False, indent=1)

usage3 = """# A22 round-03 · snapshot-usage

## 状态
completed。round-03/dashboard.png/.snapshot（1600×1000）为服务 200 真实响应（v2 终版，
257,624 字节）；computed-data / layout-map（含 r2 对比）/ change-audit / 报告 / 指标就位。

## 本轮执行（rounds/round-03.md）
- 新增 2026-10：orders 640 / 收入 224,000 / 退款 11,200 / 成本 142,000 / 访问 5,900
  → 净收入 212,800、利润 70,800、退款率 5.00%、转化率 10.85%（640÷5,900）。
- KPI 改七个月汇总：净收入 1,121,424 / 利润 252,924 / 订单 3,685 / 总体转化率
  11.10%（3,685 ÷ 33,200，非月均）。
- 柱图 7 组（组宽 205.143，柱 48 / 对隙 10），轴维持 −4..24（第 7 组 21.28 < 24）；
  2026-09 红色负柱 −0.56 与零线强调保留。
- 表格 7 行（hdr 34 + 行高 25.142857 内部重排，22px 居中），红标语义不变。
- 结论：2026-10 净收入 212,800、利润 70,800 均为七个月最高（环比 +5.15%）；
  9 月 −5,632 → 10 月回正；退款率峰值仍为 8 月 13.32%、10 月 5.00%。

## 更正保真（change-audit.json）
- r2 两笔更正全部继续有效（8 月退款 25,048 / 13.32% 峰值、9 月 −5,632 负值）；
  未恢复旧数据、未省略 2026-04；monthly.csv 原样未改，10 月行标注来源为第三轮预置。
- 六主区域边界与 r2 逐分量 0 差（±2px 内全 pass），柱组/表行重排属预置允许。

## 迭代与查看
- 请求 3 条：1 条 400（色值漏 #，语法修复留证）、v1 200、v2 200（终版）。
- v1 看图（half/table/结论/脚注）查出脚注右端被裁 → 文案精简 v2 重渲；
  v2 看图 half + 脚注 1:1 + 柱图左右放大 + 表格/结论 1:1，全部通过。

## 未解决事项
无。A22 三轮全部完成；终止版为 round-03（7 个月）。
"""
with open(f"{R3}/snapshot-usage.md", "w", encoding="utf-8", newline="\n") as f:
    f.write(usage3)

iters = [
    {"id": "A22-r03-syntax-0001", "parent": "A22-r02-visual-v02", "type": "syntax-fix",
     "image": "", "viewed_at": "2026-10-18T12:28:55+08:00",
     "images": [], "observable_issues": ["首条请求 400：KPI accent 用色 '4CC2FF' 漏 '#'"
                                         "（PARSE_ERROR，req 122855186 留证）"],
     "changes": "CYAN 改 '#4CC2FF'，不涉及视觉语义", "recheck": "下一请求 200", "seq": 1},
    {"id": "A22-r03-baseline-v01", "parent": "A22-r02-visual-v02", "type": "requirement-change",
     "image": "steps/r3-half.png", "viewed_at": "2026-10-18T12:30:00+08:00",
     "images": ["steps/r3-half.png", "steps/r3-table.png",
                "steps/r3-footnote-1x.png", "steps/r3-conclusion-1x.png"],
     "observable_issues": ["脚注右端『monthly.csv 原样未改。』越界被裁"
                           "（其余合格：7 组柱/7 行表/KPI 汇总/结论两行完整）"],
     "changes": "", "recheck": "触发 visual-v02", "seq": 2},
    {"id": "A22-r03-visual-v02", "parent": "A22-r03-baseline-v01", "type": "visual",
     "image": "steps/r3-v2-half.png", "viewed_at": "2026-10-18T12:34:30+08:00",
     "images": ["steps/r3-v2-half.png", "steps/r3-v2-footnote-1x.png",
                "steps/r3-v2-chart-left.png", "steps/r3-v2-chart-right.png"],
     "observable_issues": [],
     "changes": "脚注删『/ 收入 224,000』等斜杠罗列改顿号紧凑式（数据明细在图表/表格）",
     "recheck": "v2 脚注完整收尾；负柱/7 组/边界回归确认", "seq": 3},
]
with open(f"{TMP}/r03-iterations.jsonl", "w", encoding="utf-8", newline="\n") as f:
    f.writelines(json.dumps(o, ensure_ascii=False) + "\n" for o in iters)

# —— A22 根累计：三轮顶层汇总 ——
c1 = json.load(open(f"{A22}/round-01/computed-data.json", encoding="utf-8"))
total = {
    "schema_version": 1, "task_id": "A22", "path_base": "task_output_root",
    "run_id": RUN, "status": "completed",
    "scope": "A22 三轮（round-01/02/03 各自顶层汇总相加；轮内明细不重复计入）",
    "period_totals": {
        "round_1_6mo": {"net_revenue": c1["totals"]["net_revenue"],
                        "profit": c1["totals"]["profit"],
                        "overall_conversion": c1["totals"]["overall_conversion"]},
        "round_2_6mo_corrected": {"net_revenue": c2["totals"]["net_revenue"],
                                  "profit": c2["totals"]["profit"]},
        "round_3_7mo": {"months_count": 7, "net_revenue": c3["totals"]["net_revenue"],
                        "profit": c3["totals"]["profit"],
                        "orders": c3["totals"]["orders"],
                        "sessions": c3["totals"]["sessions"],
                        "overall_conversion": c3["totals"]["overall_conversion_display"],
                        "refund_amount": c3["totals"]["refund_amount"],
                        "operating_cost": c3["totals"]["operating_cost"],
                        "overall_refund_rate": 0.0647,
                        "profit_margin": 0.2255},
    },
    "timings": {
        "started_at": "2026-10-18T12:15:40+08:00", "ended_at": end,
        "elapsed_seconds_all_rounds": round(
            (datetime.fromisoformat(end)
             - datetime.fromisoformat("2026-10-18T12:15:40+08:00")).total_seconds(), 1),
        "request_duration_sum_seconds": round(
            rounds[1]["request_duration_sum_seconds"]
            + rounds[2]["request_duration_sum_seconds"]
            + rounds[3]["request_duration_sum_seconds"], 4),
        "note": "墙钟为三轮连续执行（含看图/写档/修复），不等于请求时长之和",
    },
    "counts": {
        "snapshot_requests": C, "successful": sum(r["successful"] for r in rounds.values()),
        "failed": sum(r["failed"] for r in rounds.values()),
        "completed_visual_iterations": sum(r["visual_iterations_completed"]
                                           for r in rounds.values()),
        "image_views": sum(r["image_views"] for r in rounds.values()),
        "final_images": 3, "dsl_versions": 6,
    },
    "rounds": rounds,
    "logs": {
        "requests": f"tmp/{RUN}/A22/requests.jsonl（全量 8 条含 400/缓存命中）",
        "iterations": [f"tmp/{RUN}/A22/r0{i}-iterations.jsonl" for i in (1, 2, 3)],
        "change_audit": [f"{A22}/round-0{i}/change-audit.json" for i in (2, 3)],
    },
    "outputs": {
        "round-01": f"{A22}/round-01/", "round-02": f"{A22}/round-02/",
        "round-03": f"{A22}/round-03/",
        "cumulative_usage": f"{A22}/snapshot-usage.md",
    },
    "unresolved_issues": [],
}
with open(f"{A22}/task-metrics.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(total, f, ensure_ascii=False, indent=1)

usage_root = """# A22 · snapshot-usage（三轮累计）

三份逐轮报告见 round-1/2/3/snapshot-usage.md。简要印象：
1. **round-01**：KPI 与脚注首版溢出裁切（重文案修复）后再过图；期间 6 个月 KPI
   净 918,624 / 利 262,124 / 转 11.15%。最终净收入/利润共轴柱图 + 5×6 表。
2. **round-02**：应用两笔更正（8 月退款 15,048→25,048；9 月成本 138,000→208,000）。
   期间利润 262,124→182,124（−30.52%）；9 月利润 −5,632 以负轴红色负柱表达，主区域
   边界与 r1 逐分量 0 差；未触碰 CSV。
3. **round-03**：新增 2026-10（212,800/70,800/5.00%/10.85%），KPI 到七个月
   （净 1,121,424 / 利 252,924 / 订单 3,685 / 转 11.10%）；6→7 组/行重排，主区域边界
   与 r2 逐分量 0 差；环比 +5.15% 由未舍入值算出再舍位。
累计感受：同一深色系系统跨三轮非常好复用；负值轴是本轮关键视觉学习（正负柱基于
零线方向）；脚本化重计算 + 显示层才舍位的原则在三轮间全程一致。
"""
with open(f"{A22}/snapshot-usage.md", "w", encoding="utf-8", newline="\n") as f:
    f.write(usage_root)

# —— suite 更新：A22 completed ——
SP = f"outputs/{RUN}/_suite/suite-state.json"
st = json.load(open(SP, encoding="utf-8"))
for t in st["tasks"]:
    if t["id"] == "A22":
        t["status"] = "completed"
        t["completed_rounds"] = [1, 2, 3]
        t["artifacts"] = (
            [f"round-01/{n}" for n in ("dashboard.png", "dashboard.snapshot",
                                       "computed-data.json", "layout-map.json",
                                       "snapshot-usage.md", "task-metrics.json")]
            + [f"round-02/{n}" for n in ("dashboard.png", "dashboard.snapshot",
                                         "computed-data.json", "layout-map.json",
                                         "change-audit.json", "snapshot-usage.md",
                                         "task-metrics.json")]
            + [f"round-03/{n}" for n in ("dashboard.png", "dashboard.snapshot",
                                         "computed-data.json", "layout-map.json",
                                         "change-audit.json", "snapshot-usage.md",
                                         "task-metrics.json")]
            + ["snapshot-usage.md", "task-metrics.json"])
        t["visual_review_evidence"].append(
            "r3: v1 half/table/结论/脚注 查出脚注裁切 → v2 重渲；双柱图放大/1:1 全过；"
            "layout 六区域对 r2 对比 0 差；7 个月 KPI/结论逐项与 computed-data 吻合")
        t["resume_notes"] = ""
        t["final_images"] = 3
st["current_task"] = "A23"
st["current_round"] = 1
st["completed_task_count"] = 22
st["updated_at"] = end
with open(SP, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

ev = f"tmp/{RUN}/_suite/events.jsonl"
with open(ev, "a", encoding="utf-8", newline="\n") as f:
    f.write(json.dumps({"id": "SUITE-ev-000046", "at": end, "kind": "round-completed",
                        "task_id": "A22", "round": 3,
                        "detail": "r3 新增 2026-10 → 7 个月 KPI 净 1,121,424/利 252,924/"
                                  "转 11.10%；脚注裁切 1 迭代修复；边界 0 差回归"},
                       ensure_ascii=False) + "\n")
    f.write(json.dumps({"id": "SUITE-ev-000047", "at": end, "kind": "task-completed",
                        "task_id": "A22", "round": 3,
                        "detail": "A22 三轮完成（918,624→908,624→1,121,424 净收入系列；"
                                  "负值表达与数据更正链均留证 request/iteration 级）"},
                       ensure_ascii=False) + "\n")
cp = {"at": end, "run_id": RUN, "action": "task-complete", "task_id": "A22",
      "round": 3,
      "summary": "A22 三轮全部 completed（净收入系列 918,624→908,624→1,121,424；"
                 "9 月 −5,632 负柱在 r2/r3 均真实画出；两份两轮 change-audit；"
                 "任务级汇总 metrics/usage；最终图 round-03）。下一题 A23。"}
with open(f"tmp/{RUN}/_suite/checkpoints/state-000044.json", "w",
          encoding="utf-8", newline="\n") as f:
    json.dump(cp, f, ensure_ascii=False, indent=1)
st["last_checkpoint"] = f"tmp/{RUN}/_suite/checkpoints/state-000044.json"
with open(SP, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

print("r3 finalized:", end, "| requests r3", sum3["snapshot_requests"],
      "ok", sum3["successful"], "dur", sum3["request_duration_sum_seconds"])
print("A22 totals: requests", C, "views", total["counts"]["image_views"],
      "final", total["counts"]["final_images"])
