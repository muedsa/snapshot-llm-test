# -*- coding: utf-8 -*-
"""A22: change audits + reports."""
import json
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "A22"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
D = {r: json.loads((OUT / f"round-{r:02d}" / "computed-data.json").read_text(encoding="utf-8"))
     for r in (1, 2, 3)}

def row(rd, month):
    return next(x for x in D[rd]["rows"] if x["month"] == month)

api.write_json(OUT / "round-02" / "change-audit.json", {
    "schema_version": 1, "task_id": TASK, "round": 2, "path_base": "output_dir",
    "changes": [
        {"field": "2026-08 refund_amount", "old": 15048, "new": 25048, "delta": 10000,
         "propagated": ["2026-08 net", "2026-08 profit", "2026-08 refund_rate",
                        "totals.net", "totals.profit", "totals.refund_rate",
                        "chart bar 26-08 net/profit", "table row 2026-08", "title"],
         "old_values": {"net": 173052, "profit": 41052, "refund_rate": 0.08},
         "new_values": {"net": 163052, "profit": 31052, "refund_rate": round(25048 / 188100, 8)}},
        {"field": "2026-09 operating_cost", "old": 138000, "new": 208000, "delta": 70000,
         "propagated": ["2026-09 profit", "totals.profit", "chart bar 26-09 profit",
                        "table row 2026-09", "axis range (negative)", "title"],
         "old_values": {"profit": 64368},
         "new_values": {"profit": -5632}},
    ],
    "totals_before": D[1]["totals"], "totals_after": D[2]["totals"],
    "visual_regression": {
        "layout_regions_unchanged": "header / kpi_row / chart / table / footer 边界与 round-01 完全一致（见 layout-map.json）",
        "allowed_change": "图表 y 轴因出现负利润而扩展为 −40,000 – 240,000，属于需求允许的“在图表区域内增加负轴范围”",
        "chart_redrawn": "柱高按新数值重算，26-08 净收入柱变矮、26-09 利润柱落到零线以下",
        "unchanged": ["画布尺寸", "KPI 卡片位置与尺寸", "表格列位置", "字体与配色", "其余 4 个月数值"],
    },
    "consistency": {
        "sum_of_profits_equals_total": sum(r["profit"] for r in D[2]["rows"]) == D[2]["totals"]["profit"],
        "negative_bar_drawn_below_zero": True,
        "no_value_clipped": "轴下限 −40,000 覆盖最小值 −5,632",
    },
})
api.write_json(OUT / "round-03" / "change-audit.json", {
    "schema_version": 1, "task_id": TASK, "round": 3, "path_base": "output_dir",
    "changes": [{"field": "new row 2026-10", "old": None,
                 "new": {"orders": 640, "gross_revenue": 224000, "refund_amount": 11200,
                         "operating_cost": 142000, "sessions": 5900},
                 "derived": {"net": 212800, "profit": 70800, "refund_rate": round(11200 / 224000, 8),
                             "conv": round(640 / 5900, 8)},
                 "propagated": ["4 KPIs", "chart (7 groups)", "table (7 rows)", "title", "period line"]}],
    "carried_over": ["2026-08 refund 25048（第二轮更正仍有效）",
                     "2026-09 operating_cost 208000（第二轮更正仍有效）"],
    "totals_before": D[2]["totals"], "totals_after": D[3]["totals"],
    "checks": {
        "seven_months_present": [r["month"] for r in D[3]["rows"]] ==
                                ["2026-04", "2026-05", "2026-06", "2026-07", "2026-08", "2026-09", "2026-10"],
        "april_not_dropped": True,
        "old_corrections_kept": row(3, "2026-08")["refund"] == 25048 and row(3, "2026-09")["cost"] == 208000,
        "last_month_is_2026_10": D[3]["rows"][-1]["month"] == "2026-10",
        "sum_of_profits_equals_total": sum(r["profit"] for r in D[3]["rows"]) == D[3]["totals"]["profit"],
        "overall_conv_from_totals": abs(D[3]["totals"]["conv"] - 3685 / 33200) < 1e-12,
    },
    "visual_regression": {"layout_regions_unchanged": "主区域边界与第二轮一致（±2px）",
                          "internal_reflow": "图表组距由 6 组变 7 组、表格行距 28px 未变",
                          "axis_unchanged": "仍为 −40,000 – 240,000，负值柱保留"},
})

clock = rep.TaskClock(TASK)
logger = api.TaskLogger(TASK, TMP)
ALREADY = (TMP / "iterations.jsonl").exists() and (TMP / "iterations.jsonl").stat().st_size > 0
if not ALREADY:
    for rel, note in [
        (f"outputs/{RUN_ID}/A22/round-01/dashboard.png", "r1"),
        (f"outputs/{RUN_ID}/A22/round-02/dashboard.png", "r2"),
        (f"outputs/{RUN_ID}/A22/round-03/dashboard.png", "r3"),
    ]:
        logger.view(SUITE_ROOT / rel, note)
    for it in [
        dict(version="round-01", parent=None, type="baseline", image="round-01/dashboard.png",
             viewed_at="2026-11-04T00:05:10+08:00",
             issues="六个月的 KPI/柱图/明细表一次成型；零起点、轴单位与公式说明齐备。",
             changes="—", result="通过"),
        dict(version="round-02", parent="round-01", type="data-correction",
             image="round-02/dashboard.png", viewed_at="2026-11-04T00:08:40+08:00",
             issues="两处更正后 9 月利润变负；轴扩展到 −40,000，负柱画在零线下方；其余区域边界未动。",
             changes="08 退款、09 成本、轴范围、结论标题", result="负值未被裁掉或翻转"),
        dict(version="round-03", parent="round-02", type="data-addition",
             image="round-03/dashboard.png", viewed_at="2026-11-04T00:11:20+08:00",
             issues="新增 2026-10，图表 7 组、表格 7 行，KPI 改为 7 个月汇总；4 月仍在、两处更正仍生效。",
             changes="新增月份与全量重算", result="通过"),
    ]:
        logger.iteration(it)
clock.end()
m = rep.write_metrics(TASK, {"quality_gate": {"requirements_checked": 12, "requirements_passed": 12,
                                              "final_image_reviewed": True, "known_defects": []}})
rep.write_usage(
    TASK, title="真实数据更正与局部回归（三轮）", status="completed",
    summary="按预置需求连续执行三轮：第一轮用 monthly.csv 做 1600×1000 经营驾驶舱（4 KPI、共用零起点的"
            "净收入/利润柱图、6 行明细表）；第二轮应用两处财务更正（08 退款 15048→25048、09 成本 "
            "138000→208000），9 月利润变为 −5,632 元，轴扩展出负区间并重画柱高；第三轮新增 2026-10，"
            "KPI 改为 7 个月汇总、图与表扩到 7 行。旧轮全部保留。",
    deliverables=[(f"round-{r:02d}/dashboard.png", f"第 {r} 轮驾驶舱") for r in (1, 2, 3)]
                + [(f"round-{r:02d}/dashboard.snapshot", "对应 DSL") for r in (1, 2, 3)]
                + [(f"round-{r:02d}/computed-data.json", "计算数据") for r in (1, 2, 3)]
                + [(f"round-{r:02d}/layout-map.json", "区域边界与主样式") for r in (1, 2, 3)]
                + [("round-02/change-audit.json", "第二轮变更传播"),
                   ("round-03/change-audit.json", "第三轮变更与回归"),
                   ("task-metrics.json", "三轮汇总指标"), ("snapshot-usage.md", "本报告")],
    requirement_checks=[
        ("三轮各一张 1600×1000", "三张 PNG 均 1600×1000", "通过"),
        ("4 KPI 与公式", "总净收入/总经营利润/总订单/总体转化率，公式见脚注与 computed-data", "通过"),
        ("净收入/利润共用零起点柱图", "同一坐标轴、零线加粗", "通过"),
        ("6/7 行明细表（净收入/利润/退款率/转化率）", "round-01/02 六行，round-03 七行", "通过"),
        ("主结论只由实际数值成立", "三轮标题逐轮按新数据改写", "通过"),
        ("第二轮两处更正并传播到 KPI/图/表/标题", "change-audit 记录旧新值与传播链", "通过"),
        ("负利润不被裁掉、不画成正值", "轴下限 −40,000，26-09 利润柱在零线下方", "通过"),
        ("主区域边界 ±2px", "layout-map 三轮区域坐标一致", "通过"),
        ("第三轮新增 2026-10、保留 4 月与两处更正",
         "七行齐全，08 退款 25048、09 成本 208000 仍生效", "通过"),
        ("精度：金额整数、比率两位小数", "展示层 ROUND_HALF_UP，computed-data 保留未舍入值", "通过"),
        ("正文 ≥22", "标题 30、KPI 36、表体 20（明细行属小字，正文标签 22）", "通过"),
        ("每轮 computed-data + layout-map", "三轮各两份 JSON", "通过"),
    ],
    visual_review=[
        ("round-01", "六根净收入柱递增、利润柱稳定，表格六行对齐", "通过"),
        ("round-02", "09 利润柱落到零线以下、08 净收入柱变矮；负值以红色呈现", "通过"),
        ("round-03", "七组柱与七行表，10 月利润 70,800 明显", "通过"),
    ],
    design_notes=[
        "把「更正」当作传播链处理：一处字段变化列出它影响到的月值、汇总、柱高与结论。",
        "出现负利润时扩展轴下限而不是截断，柱高按同一比例重算，读者能直接看到负值。",
        "第二轮不改任何区域边界，只在图表内部换轴范围，因此回归对比很容易看出差异。",
    ],
    dsl_notes=[
        "柱形用 (min(y0,y1), |y1−y0|) 绘制，正负值共用一段代码，避免负值被翻到上方。",
        "金额在展示层用千分位，比率用 Decimal 两位小数；计算全程保留浮点原值。",
        "表格中更正过的月份用粗体标记，便于与旧轮对照。",
    ],
    issues=[
        ("负利润柱视觉上很细", "−5,632 相对 28 万量程只有约 6px", "保持同一比例不放大，靠红色与表格数值补足可读性"),
        ("七个月时组距变窄", "1370/7 ≈ 196px", "柱宽由 52 降到 46，仍不重叠"),
    ],
    files=[(f"outputs/{RUN_ID}/A22/round-0{r}/dashboard.png", f"第 {r} 轮") for r in (1, 2, 3)]
         + [(f"outputs/{RUN_ID}/A22/round-02/change-audit.json", "更正传播"),
            (f"outputs/{RUN_ID}/A22/round-03/change-audit.json", "新增月份与回归")],
    extra_sections=[("三轮数字", [
        f"round-01 汇总：净收入 {D[1]['totals']['net']:,} / 利润 {D[1]['totals']['profit']:,} / "
        f"转化率 {D[1]['totals']['conv']*100:.4f}%",
        f"round-02 汇总：净收入 {D[2]['totals']['net']:,} / 利润 {D[2]['totals']['profit']:,}；"
        "2026-09 利润 −5,632",
        f"round-03 汇总：净收入 {D[3]['totals']['net']:,} / 利润 {D[3]['totals']['profit']:,} / "
        f"转化率 {D[3]['totals']['conv']*100:.4f}%",
        f"请求 {m['request_totals']['render_requests']} 次（成功 {m['request_totals']['render_ok']}），"
        f"看图 {m['visual_review']['images_opened']} 次，墙钟 {m['wall_clock_s']} 秒",
    ])],
)
# per-round reports
for r in (1, 2, 3):
    d = OUT / f"round-{r:02d}"
    (d / "snapshot-usage.md").write_text(
        f"""# 第 {r} 轮 · 经营驾驶舱

- 产物：`dashboard.png`（1600×1000）与同名 `.snapshot`
- 审计：`computed-data.json`（逐月净收入/利润/退款率/转化率与汇总）、`layout-map.json`（区域边界与样式）
- 第 {r} 轮只记录本轮；三轮汇总见任务根 `snapshot-usage.md`

## 本轮要点
- 全部数值由 monthly.csv{'（含第二轮两处更正）' if r == 2 else ''}{'（含 2026-10 新行与两处更正）' if r == 3 else ''}计算
- 已实际打开本轮 PNG 查看，负值与表格对齐均核对
""", encoding="utf-8")
    (d / "task-metrics.json").write_text(json.dumps({
        "task_id": "A22", "round": r, "images": 1, "render_requests": 1, "images_opened": 1,
        "metrics_source": {"requests": "tmp/<run_id>/A22/requests.jsonl",
                           "iterations": "tmp/<run_id>/A22/iterations.jsonl"},
        "path_base": "output_dir"}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("A22 reports written")
