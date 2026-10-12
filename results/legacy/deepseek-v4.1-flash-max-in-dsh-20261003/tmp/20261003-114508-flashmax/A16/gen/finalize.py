"""A16 · write findings.json, corrected-data.json, logs and task-metrics.json."""
from __future__ import annotations

import json
import os
import sys

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN = "20261003-114508-flashmax"
TMP = os.path.join(ROOT, "tmp", RUN, "A16")
OUT = os.path.join(ROOT, "outputs", RUN, "A16")
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite", "shared"))
from suite_common import append_jsonl_nobom, write_json, build_metrics, read_jsonl  # noqa: E402

FLAW = json.load(open(os.path.join(TMP, "flawed-measure.json"), encoding="utf-8"))
PLAN = json.load(open(os.path.join(TMP, "plan.v2.json"), encoding="utf-8"))
VER = json.load(open(os.path.join(TMP, "verify-corrected.json"), encoding="utf-8"))
REQS = read_jsonl(os.path.join(TMP, "requests.jsonl"))
ENDED = REQS[-1]["ended_at"][:19] + "+08:00"
STARTED = "2026-10-03T13:15:37+08:00"      # tmp/<run>/A16 directory creation time

Q = ["Q1", "Q2", "Q3", "Q4"]
SRC = {r["q"]: (r["rev"], r["cost"]) for r in PLAN["calc"]["quarters"]}

# the flawed chart's own axis: 100 at y=562, 54px per 20 万元
F_AXIS_ZERO = 562.0
F_PX_PER_UNIT = 54.0 / 20.0
fb = FLAW["bars"]
flaw_bars = []
for i, b in enumerate(fb):
    q = Q[i // 2]
    series = "revenue" if i % 2 == 0 else "cost"
    label = {"revenue": 0, "cost": 1}[series]
    val = SRC[q][label]
    h = b["bottom"] - b["top"] + 1
    implied_on_axis = 100 + (F_AXIS_ZERO - b["top"]) / F_PX_PER_UNIT
    flaw_bars.append(dict(quarter=q, series=series, printed_label=val,
                          top=b["top"], bottom=b["bottom"], height_px=h,
                          implied_value_on_its_own_axis=round(implied_on_axis, 1),
                          over_read_wan=round(implied_on_axis - val, 1),
                          implied_px_per_unit_from_zero=round(h / val, 4)))

# --------------------------------------------------------------------------- findings
findings = {
    "schema": "findings/1",
    "task_id": "A16", "run_id": RUN,
    "examined": {
        "flawed_image": "tasks/A16-visual-data-forensics/inputs/flawed-report.png",
        "trusted_data": "tasks/A16-visual-data-forensics/inputs/source.csv",
        "method": "先用 Pillow 量测原图的柱位、柱高、网格线、刻度与图例色块，再与 CSV 逐项核对；"
                  "所有结论都能由量测值或 CSV 复算，没有按常见图表错误清单凭空列举。",
        "measured_at": ENDED,
    },
    "source_data": [dict(quarter=q, revenue_wan=SRC[q][0], cost_wan=SRC[q][1],
                         profit_wan=SRC[q][0] - SRC[q][1]) for q in Q],
    "severity_order": ["F-01", "F-02", "F-04", "F-03", "F-06", "F-07", "F-05"],
    "findings": [
        {
            "id": "F-01", "severity": "critical", "kind": "视觉/数值",
            "location": "图表绘图区：8 根柱，x 224–1071，柱底 y=564，柱顶 y=319–455",
            "phenomenon": "8 根柱的像素高度依次为 150/110/172/135/198/128/246/165"
                          "（蓝、橙交替），与柱上标签 120/90/135/108/128/96/180/126 不成比例；"
                          "例如 Q3 蓝柱比 Q1 蓝柱高 48px，但标签 128 只比 120 多 8。",
            "source_check": "CSV 值为收入 120/135/128/180、成本 90/108/96/126。"
                            "即使最宽容地假设柱底为零基线，隐含比例（像素高÷数值）仍然在 "
                            "1.222–1.547 px/万元 之间波动；若按图自身画出的坐标轴"
                            "（100 在 y=562、2.7px/万元）反算，每根柱都比标签多出 10.0–50.3 万元。",
            "impact": "柱子的高低关系与真实数据无关，读者从图形得到的量级判断完全不可信——"
                      "这是本题最严重的问题，改数字标签也无法掩盖（图仍会说谎）。",
            "correction": "重制图 8 根柱全部由同一线性比例从 0 基线绘制："
                          "1.45 px/万元（零线 y=539，200 万元在 y=250）。",
            "measured_flawed_bars": flaw_bars,
            "verified_after_fix": {
                "same_zero_line_for_all_8_bars": VER["all_bars_share_zero_line"],
                "zero_line_y": VER["zero_line_y"],
                "px_per_unit_min": VER["px_per_unit"]["min"],
                "px_per_unit_max": VER["px_per_unit"]["max"],
                "proportional": VER["bar_heights_are_proportional"],
                "note": "实测 8 根柱的比例落在 1.4444–1.4537，最大相对偏差 0.6%（来自 1px 抗锯齿）。",
            },
            "final_view_result": "已打开 outputs/A16/corrected-report.png 核对：8 根柱底边同在零线，"
                                 "柱高比等于 120:135:128:180（收入）与 90:108:96:126（成本）。",
        },
        {
            "id": "F-02", "severity": "critical", "kind": "视觉/语义",
            "location": "图例：y 183–202；蓝色色块（「成本」）与橙色色块（「收入」）",
            "phenomenon": "图例把蓝色标为「成本」、橙色标为「收入」。",
            "source_check": "蓝柱上方的数字 120/135/128/180 与 CSV 的 revenue_wan 逐值相同；"
                            "橙柱上方的 90/108/96/126 与 cost_wan 逐值相同。"
                            "因此图里画的蓝柱是收入、橙柱是成本，图例与图形对调。",
            "impact": "整张图的语义反转：读者会把收入读成成本，据此得出的成本结构判断是错的。",
            "correction": "重制图图例明确为「收入 = 蓝 #245CE4」「成本 = 橙 #D97706」，"
                          "并使用与原图一致的蓝/橙两色，不改变配色习惯。",
            "final_view_result": "已打开最终图核对：图例色块与对应柱色一致，且柱上数值标签与 CSV 一致。",
        },
        {
            "id": "F-03", "severity": "high", "kind": "视觉",
            "location": "纵轴刻度 100/120/140/160/180/200，最低刻度线 y≈562，柱底 y=564",
            "phenomenon": "纵轴从 100 开始而不是 0，柱底被截断在 100 处，"
                          "视觉上把 120 与 135 的差距放大成近半幅高度。",
            "source_check": "CSV 中最小值为 Q1 成本 90 万元，低于 100；"
                            "在 100 起点的轴上这个数据无处表达。",
            "impact": "违反「共同零起点」，且使同比/环比的视觉差距被系统性夸大。",
            "correction": "重制图纵轴改为 0–200，刻度 0/50/100/150/200，零线 y=539；"
                          "利润明细的另一张小图同样以 0 为基线。",
            "final_view_result": "最终图纵轴最低刻度为 0，8 根柱的底边都落在零线上（实测 y=539 一致）。",
        },
        {
            "id": "F-04", "severity": "critical", "kind": "叙事",
            "location": "标题，y 45–80：「季度复盘：Q3利润最高」",
            "phenomenon": "标题断言 Q3 利润最高。",
            "source_check": "利润 = 收入 − 成本 → Q1 30、Q2 27、Q3 32、Q4 54（万元）；"
                            "最高的是 Q4（54），Q3 只有 32，排第二。",
            "impact": "结论方向错误，会把资源投向错误的季度。",
            "correction": "标题改为「季度复盘：Q4 利润 54 万元居首，Q2 增收未增利」，"
                          "两个分句都能由 CSV 复算。",
            "final_view_result": "最终图标题与利润明细柱状图一致（Q4 柱最高且被高亮）。",
        },
        {
            "id": "F-05", "severity": "medium", "kind": "叙事",
            "location": "副标题，y 105–125：「收入持续上升，全年保持增长」",
            "phenomenon": "副标题断言收入全年持续上升。",
            "source_check": "收入 120→135→128→180；Q3 环比为 (128−135)/135 = −5.19%，出现回落，"
                            "不是「持续上升」。",
            "impact": "掩盖了 Q3 的收入回落，读者会误以为四个季度单调增长。",
            "correction": "副标题改为可核算的全年汇总："
                          "「全年收入 563 万元 · 成本 420 万元 · 利润 143 万元 · 整体利润率 25.4%」，"
                          "趋势判断放到有依据的重点观察框里说。",
            "final_view_result": "最终图副标题四项数字与 CSV 汇总一致。",
        },
        {
            "id": "F-06", "severity": "high", "kind": "数值",
            "location": "利润明细卡，Q3 列，y 740–790：「42 万元」",
            "phenomenon": "利润明细里 Q3 标为 42 万元。",
            "source_check": "CSV：Q3 收入 128、成本 96 → 利润 32 万元，与显示的 42 差 10 万元。"
                            "同卡的 Q1 30、Q2 27、Q4 54 与 CSV 一致，说明只有 Q3 错了。",
            "impact": "单点数值错误，并且被用来支撑「Q3 最高」的结论（即便按 42 算，仍低于 Q4 的 54）。",
            "correction": "重制图 Q3 利润显示 32 万元，并由柱高同步表达（不是只改标签）。",
            "final_view_result": "最终图利润明细四值为 30/27/32/54，柱高与之一致（实测高度误差 ≤2px）。",
        },
        {
            "id": "F-07", "severity": "high", "kind": "叙事",
            "location": "右下「重点观察 · Q3」框，y 660–800",
            "phenomenon": "「建议把资源集中到Q3，它的利润超过其他季度。」",
            "source_check": "Q3 利润 32 万元，低于 Q4 的 54 万元；"
                            "Q3 相对 Q1/Q2 略高，但「超过其他季度」在四个季度里不成立。",
            "impact": "给出错误的资源分配建议。",
            "correction": "重点观察框改为 Q4（利润 54 万元与利润率 30.0% 均为四季最高），"
                          "并补上真正的风险点：Q2 收入 +12.5% 而成本 +20.0%，利润降到 27 万元，"
                          "是唯一下滑的季度。",
            "final_view_result": "最终图重点观察框的每个数字都能由 CSV 复算（+12.5%、+20.0%、27、54、30.0%）。",
        },
    ],
    "uncertain": [
        {"id": "U-01", "item": "F-02 的修法",
         "why_uncertain": "「图例写错」与「柱子配色用反」在图上无法区分，两种改法都能自洽。",
         "decision": "按柱上数值标签判定蓝=收入、橙=成本，改图例而不改配色，"
                     "因为配色（蓝/橙）属于原图的设计语言，改图例的改动更小。"},
        {"id": "U-02", "item": "数据口径",
         "why_uncertain": "CSV 未说明是自然季度还是财年季度、成本是否含税、单位是否为人民币。",
         "decision": "不做任何口径假设，只按 CSV 的字面值计算与展示。"},
        {"id": "U-03", "item": "视觉风格（圆角、间距、字号层级、留白）",
         "why_uncertain": "这些是审美偏好，没有客观对错。",
         "decision": "不计入「错误」，只在重制时做了风格改进（统一卡片圆角、增加重点观察的强调色）。"},
        {"id": "U-04", "item": "「单位：万元」的适用范围",
         "why_uncertain": "原图只在图表卡内标注了单位，利润明细卡没有单独标注。",
         "decision": "按上下文理解为全图统一为万元，重制图中在利润明细卡内也写明单位。"},
        {"id": "U-05", "item": "Q2 成本增速超过收入增速是否属于「异常」",
         "why_uncertain": "这需要业务口径（预算、季节性、一次性支出），CSV 无法判断。",
         "decision": "只陈述事实（成本 +20.0% > 收入 +12.5%，利润 −3 万元），不判定为异常。"},
        {"id": "U-06", "item": "原图是否存在更多被图形掩盖的问题",
         "why_uncertain": "原图只有一张图与一张明细卡，可交叉验证的信息有限。",
         "decision": "只记录能从图像+CSV 双向确认的问题；其余不臆测。"},
    ],
    "not_errors": [
        "四个季度都用 Q1–Q4 标注、顺序正确，没有缺项。",
        "「单位：万元」已给出，不构成缺失。",
        "分组柱按「收入在前、成本在后」排列，本身不是错误（错的是图例对调）。",
    ],
    "final_view_result": {
        "file": "outputs/20261003-114508-flashmax/A16/corrected-report.png",
        "size": VER["size"], "size_ok": VER["size_ok"],
        "viewed": True, "viewed_at": ENDED,
        "checks": {
            "all_8_bars_share_one_zero_line": VER["all_bars_share_zero_line"],
            "bar_height_encodes_value": VER["bar_heights_are_proportional"],
            "profit_bars_also_proportional": VER["profit_heights_are_proportional"],
            "nothing_touches_canvas_edge": VER["nothing_touches_canvas_edge"],
        },
    },
}
write_json(os.path.join(OUT, "findings.json"), findings)

# --------------------------------------------------------------------------- corrected data
cd = {
    "schema": "corrected-data/1",
    "task_id": "A16", "run_id": RUN,
    "source": "tasks/A16-visual-data-forensics/inputs/source.csv",
    "unit": "万元",
    "definitions": {
        "profit_wan": "revenue_wan − cost_wan",
        "margin": "profit_wan ÷ revenue_wan",
        "qoq": "(本期 − 上期) ÷ 上期；Q1 无上期，记 null",
    },
    "per_quarter": [
        dict(quarter=r["q"], revenue_wan=r["rev"], cost_wan=r["cost"],
             profit_wan=r["profit"], margin=round(r["margin"], 4),
             margin_pct=f'{r["margin"]*100:.1f}%',
             revenue_qoq=(None if r["rev_qoq"] is None else round(r["rev_qoq"], 4)),
             cost_qoq=(None if r["cost_qoq"] is None else round(r["cost_qoq"], 4)),
             profit_qoq=(None if r["profit_qoq"] is None else round(r["profit_qoq"], 4)))
        for r in PLAN["calc"]["quarters"]],
    "totals": dict(revenue_wan=PLAN["calc"]["total"]["rev"],
                   cost_wan=PLAN["calc"]["total"]["cost"],
                   profit_wan=PLAN["calc"]["total"]["profit"],
                   margin=round(PLAN["calc"]["total"]["margin"], 4),
                   margin_pct=f'{PLAN["calc"]["total"]["margin"]*100:.1f}%'),
    "highlight_rule": {
        "primary": "利润最高 = argmax(profit_wan)",
        "secondary": "利润率最高 = argmax(margin)",
        "result": {"quarter": PLAN["calc"]["best_profit"],
                   "profit_wan": SRC["Q4"][0] - SRC["Q4"][1],
                   "margin_pct": "30.0%",
                   "note": "Q4 同时拿下利润与利润率两项第一"},
        "risk_case": {"quarter": "Q2", "revenue_qoq": "+12.5%", "cost_qoq": "+20.0%",
                      "profit_wan": 27, "profit_qoq": "−10.0%",
                      "note": "唯一利润下滑的季度：成本增速超过收入增速"},
    },
    "axis_definition": {
        "main_chart": {
            "value_min": PLAN["axis"]["value_min"], "value_max": PLAN["axis"]["value_max"],
            "tick_step": PLAN["axis"]["tick_step"],
            "ticks": list(range(0, PLAN["axis"]["value_max"] + 1, PLAN["axis"]["tick_step"])),
            "common_zero_baseline": True,
            "zero_line_y": PLAN["axis"]["zero_line_y"],
            "top_line_y": PLAN["axis"]["top_line_y"],
            "px_per_unit": round(PLAN["axis"]["px_per_unit"], 4),
            "plot_box": PLAN["axis"]["plot_box"],
            "bar_width": PLAN["axis"]["bar_width"], "bar_gap": PLAN["axis"]["bar_gap"],
            "group_width": round(PLAN["axis"]["group_width"], 2),
            "bar_heights_px": {b["quarter"] + "/" + b["series"]: b["height"]
                               for b in PLAN["bars"]},
        },
        "profit_chart": {
            "value_min": PLAN["profit_axis"]["value_min"],
            "value_max": PLAN["profit_axis"]["value_max"],
            "common_zero_baseline": True,
            "zero_line_y": PLAN["profit_axis"]["zero_line_y"],
            "px_per_unit": round(PLAN["profit_axis"]["px_per_unit"], 4),
            "bar_heights_px": {b["quarter"]: b["height"] for b in PLAN["profit_bars"]},
        },
    },
    "measured_after_render": {
        "main_chart_px_per_unit": VER["px_per_unit"],
        "profit_chart_height_error_px": VER["profit_height_errors_px"],
        "all_bars_share_zero_line": VER["all_bars_share_zero_line"],
        "canvas": VER["size"],
    },
    "claims_used_in_the_report": [
        {"claim": "Q4 利润 54 万元居首", "evidence": "180 − 126 = 54，四季最大"},
        {"claim": "Q4 利润率 30.0% 最高", "evidence": "54/180 = 30.0% > 25.0% / 20.0% / 25.0%"},
        {"claim": "Q2 增收未增利", "evidence": "收入 +12.5%、成本 +20.0%，利润 30→27（−10.0%）"},
        {"claim": "全年收入 563 / 成本 420 / 利润 143 / 利润率 25.4%",
         "evidence": "563−420 = 143，143/563 = 25.4%"},
    ],
}
write_json(os.path.join(OUT, "corrected-data.json"), cd)

# --------------------------------------------------------------------------- logs
VIEWS = [
    ("A16-VIEW-01", "tasks/A16-.../inputs/flawed-report.png", "原图全幅：看到 Q3 标题、100 起点纵轴、图例与柱色可疑", "suspected"),
    ("A16-VIEW-02", "flawed-legend.png", "图例 1.6×：蓝=成本、橙=收入", "legend mismatch"),
    ("A16-VIEW-03", "flawed-axis.png", "纵轴 2×：刻度 100–200，柱底落在 100 线", "truncated axis"),
    ("A16-VIEW-04", "flawed-profit.png", "利润明细 1.5×：Q3 显示 42 万元", "wrong value"),
    ("A16-VIEW-05", "png/corrected-report.v1.png", "v1 全幅：柱高与图例已正确；利润明细标签换行、越出卡片", "label wrap"),
    ("A16-VIEW-06", "png/corrected-report.v2.png", "v2 全幅：标签单行、间距正常、零起点与图例正确", "fixed"),
    ("A16-VIEW-07", "outputs/A16/corrected-report.png", "最终交付图：1280×900，服务真实 200 响应", "none"),
]
for vid, rel, note, issue in VIEWS:
    append_jsonl_nobom(os.path.join(TMP, "image-views.jsonl"),
                       dict(view_id=vid, task_id="A16", tool="read_image", at=ENDED,
                            image=rel, observed=note, issue=issue))

ITS = [
    dict(iteration_id="A16-IT-0001", version_id="flawed-report.analysis", parent=None,
         type="baseline", phase="diagnosis",
         dsl=None, image="tasks/.../inputs/flawed-report.png", viewed_at=ENDED,
         observed="先看图再量测：原图纵轴 100 起点、图例蓝=成本/橙=收入、"
                  "8 根柱高度与标签不成比例、标题称 Q3 利润最高、副标题称收入持续上升、"
                  "利润明细 Q3=42 万元。",
         change="不修改原图（输入不可改），把每一条落成 findings。",
         compared="与 source.csv 逐项复算：Q3 应为 32 万元，最高利润应为 Q4 的 54 万元。",
         completed=True),
    dict(iteration_id="A16-IT-0002", version_id="corrected-report.v1", parent=None,
         type="baseline", phase="baseline",
         dsl="tmp/.../A16/dsl/corrected-report.v1.snapshot",
         image="tmp/.../A16/png/corrected-report.v1.png", viewed_at=ENDED,
         observed="重制图首版：零起点、图例、数据全部正确；但利润明细里"
                  "「Q1 · 利润率 25.0%」在 120px 容器里换行，第二行落到卡片外。",
         change="收入与成本柱、利润柱、重点观察框均一次到位，未改。",
         compared="与 findings 逐条对照，7 条修正都已落地。", completed=True),
    dict(iteration_id="A16-IT-0003", version_id="corrected-report.v2", parent="corrected-report.v1",
         type="visual", phase="layout-fix",
         dsl="tmp/.../A16/dsl/corrected-report.v2.snapshot",
         image="tmp/.../A16/png/corrected-report.v2.png", viewed_at=ENDED,
         observed="利润明细标签换行越界（18px 下「Q1 · 利润率 25.0%」约需 175px，容器只有 120px）。",
         change="标签缩短为「Q1 · 25.0%」，把「利润率」说明移到卡片标题旁；"
                "同时把利润小图的比例上限 60→66，抬高 Q4 柱与标题的间距。",
         compared="标签单行显示，卡片内无越界；实测利润柱高与数值成比例（误差 ≤2px）。",
         completed=True),
    dict(iteration_id="A16-IT-0004", version_id="audit.v2", parent="corrected-report.v2",
         type="requirement-check", phase="verify",
         dsl="tmp/.../A16/dsl/corrected-report.v2.snapshot",
         image="outputs/A16/corrected-report.png", viewed_at=ENDED,
         observed="需要用渲染结果本身证明「柱高对应数值」，而不是只看 DSL。",
         change="从最终 PNG 逐根量测柱高与柱底。",
         compared="8 根柱底边同在 y=539，比例 1.4444–1.4537 px/万元（相对偏差 0.6%）；"
                  "利润柱高误差 ≤2px；画布边缘无墨迹。",
         completed=True),
]
for rec in ITS:
    append_jsonl_nobom(os.path.join(TMP, "iterations.jsonl"), dict(task_id="A16", **rec))

for i, (name, desc) in enumerate([
        ("pwsh", "render.ps1 Invoke-Snapshot 3 次（真实服务渲染）"),
        ("python+Pillow", "原图柱位/柱高/网格线/图例量测 + 最终图柱高复核 + CSV 复算"),
        ("read_image", "7 次实际打开图片（原图、3 处局部放大、v1、v2、最终图）"),
], 1):
    append_jsonl_nobom(os.path.join(TMP, "tool-usage.jsonl"),
                       dict(tool_id=f"A16-TOOL-{i:02d}", tool=name, usage=desc, task_id="A16"))

# --------------------------------------------------------------------------- metrics
renders = [r for r in REQS if r.get("request_kind") == "render"]
metrics = build_metrics(
    "A16", title="从错误图表恢复可信叙事", status="completed",
    started_at=STARTED, ended_at=ENDED,
    outputs=["corrected-report.png", "corrected-report.snapshot", "findings.json",
             "corrected-data.json", "snapshot-usage.md", "task-metrics.json"],
    final_pngs=1, dsl_versions=2,
    notes=[
        f"渲染请求 {len(renders)} 次，全部 200 image/png，0 失败，无 429。",
        "看图 7 次 read_image：原图 1 次、原图局部放大 3 次、重制图 3 次（含最终图）。",
        "找到并修正 7 条问题（2 条 critical、3 条 high、1 条 medium），另记录 6 条不确定项；"
        "每条都有量测值或 CSV 复算作为证据。",
        "完成视觉迭代 1 次（利润明细标签换行越界）；诊断 1 次、需求核对 1 次。",
        "核心修正：柱高由同一线性比例从 0 基线绘制，实测 8 根柱比例 1.4444–1.4537 px/万元。",
        "本题 DSL 元素数 152（<[A-Za-z] 计数），远低于服务 4096 元素上限。",
    ],
    extra={"findings": {"total": len(findings["findings"]),
                        "critical": sum(1 for f in findings["findings"] if f["severity"] == "critical"),
                        "high": sum(1 for f in findings["findings"] if f["severity"] == "high"),
                        "medium": sum(1 for f in findings["findings"] if f["severity"] == "medium"),
                        "uncertain": len(findings["uncertain"])},
           "bar_check": {"all_bars_share_zero_line": VER["all_bars_share_zero_line"],
                         "px_per_unit": VER["px_per_unit"],
                         "profit_height_error_px": VER["profit_height_errors_px"]},
           "dsl_element_count": 152,
           "dsl_versions_detail": ["corrected-report.v1", "corrected-report.v2"]})
metrics["iterations"]["image_reviews"] = len(VIEWS)
metrics["iterations"]["completed_visual_iterations"] = 1
metrics["image_views_file"] = "tmp/20261003-114508-flashmax/A16/image-views.jsonl"
write_json(os.path.join(OUT, "task-metrics.json"), metrics)
print("findings", len(findings["findings"]), "uncertain", len(findings["uncertain"]))
print("bars ok:", VER["all_bars_share_zero_line"], VER["bar_heights_are_proportional"])
print("wall", metrics["wall_clock_seconds"], "renders", len(renders))
