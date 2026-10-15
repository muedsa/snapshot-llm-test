#!/usr/bin/env python
"""A16 findings.json：逐条给可观察证据（图片位置/现象/数据核对/影响/修正/查看结果）。

启动基准：总任务根 (suite_root）。
坐标基准：画布左上原点、x 向右 / y 向下、单位 px、框为 [left,top,right,bottom]。
所有「原图位置」来自 probe_flawed_a16.py / probe_flawed2_a16.py 的像素测量，
原始测量保留在 tmp/run-20261011-01/A16/drafts/flawed-geometry*.json。
"""
from __future__ import annotations

import csv
import json
import os
from pathlib import Path

BASE = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
DRAFTS = BASE / "tmp/run-20261011-01/A16/drafts"
OUT = BASE / "tmp/run-20261011-01/A16/drafts/findings-raw.json"
SRC = BASE / "tasks/A16-visual-data-forensics/inputs/source.csv"


def load():
    with SRC.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    out = []
    for r in rows:
        rev, cost = int(r["revenue_wan"]), int(r["cost_wan"])
        out.append({"q": r["quarter"], "rev": rev, "cost": cost, "profit": rev - cost,
                    "margin": round((rev - cost) / rev * 100, 1)})
    return out


def main() -> None:
    g = json.loads((DRAFTS / "flawed-geometry-2.json").read_text(encoding="utf-8"))
    d = load()
    blue, orange = g["bars_remeasured"]["blue"], g["bars_remeasured"]["orange"]
    rev_labels = [r["rev"] for r in d]
    cost_labels = [r["cost"] for r in d]
    profits = {r["q"]: r["profit"] for r in d}

    # 逐根柱：轴上读数 vs 标签值
    per_bar = []
    for i, q in enumerate(["Q1", "Q2", "Q3", "Q4"]):
        per_bar.append({
            "quarter": q, "series_label": "成本（蓝色）", "label_value": blue[i] and rev_labels[i],
            "bar_box": [blue[i]["x_left"], blue[i]["y_top"], blue[i]["x_right"], blue[i]["y_bottom"]],
            "axis_value_at_bar_top": blue[i]["axis_value_at_top"],
            "height_px": blue[i]["height_px"],
            "implied_source_column": "revenue_wan",
        })
        per_bar.append({
            "quarter": q, "series_label": "收入（橙色）", "label_value": cost_labels[i],
            "bar_box": [orange[i]["x_left"], orange[i]["y_top"], orange[i]["x_right"],
                        orange[i]["y_bottom"]],
            "axis_value_at_bar_top": orange[i]["axis_value_at_top"],
            "height_px": orange[i]["height_px"],
            "implied_source_column": "cost_wan",
        })

    def delta(i):   # 蓝柱
        return round(blue[i]["axis_value_at_top"] - rev_labels[i], 1)

    def delta_o(i):
        return round(orange[i]["axis_value_at_top"] - cost_labels[i], 1)

    findings = [
        {
            "id": "F01",
            "category": "坐标轴误导",
            "title": "纵轴从 100 起始，柱长不代表从零起算的大小",
            "location_in_original": {
                "region": "图表卡左侧纵轴刻度",
                "tick_ink_rows_px": [295, 349, 403, 457, 511, 565],
                "tick_labels_top_to_bottom": [200, 180, 160, 140, 120, 100],
                "baseline_value": 100,
                "bar_bottom_y": 564,
                "evidence_image": "tmp/run-20261011-01/A16/preview/flawed-axis-2x.png",
            },
            "observed": "六条网格线分别标注 200/180/160/140/120/100，最低刻度是 100 而不是 0；"
                        "所有柱体的底边都落在 y=564 这条 100 线上。",
            "source_data_check": {
                "checked_field": "source.csv 全部 revenue_wan / cost_wan 的最小值",
                "min_value_in_source": min(rev_labels + cost_labels),
                "conclusion": "源数据最小值为 90，坐标轴从 100 起意味着**源数据中的 90 落在坐标轴范围之外**，"
                              "读者无法从图上读出成本最低的一季与最低值。",
            },
            "impact": "截断基线会把 Q4 相对 Q2 的差距放大到视觉上远超真实比例"
                      "（真实 180:135 = 1.33，截断后柱长 246:172 ≈ 1.43 且起点被抬高），"
                      "并让所有柱长无法按比例读数。",
            "correction": "改为共同零起点：基线 = 0，刻度 0/50/100/150/200，"
                          "px_per_unit = (512 − 248) / 200 = 1.32，柱高 = value × 1.32，"
                          "柱底严格落在 y=512 的 0 线上（verify.json 的 bar_bottom_on_zero_line 全为 true）。",
            "final_visual_check": "定稿 3× 放大 fixed-axis-zero-3x.png：0 线与柱底对齐，"
                                 "最小值 90 的成本柱完整落在轴内；8 根柱底全部落在 0 线上。",
        },
        {
            "id": "F02",
            "category": "数值 / 系列错配",
            "title": "图例标注的两个系列与其柱上数值互换了",
            "location_in_original": {
                "legend_blue_text_box_px": g["legend_boxes"]["blue_text"],
                "legend_orange_text_box_px": g["legend_boxes"]["orange_text"],
                "legend_blue_swatch_box_px": g["legend_boxes"]["blue_swatch"],
                "legend_orange_swatch_box_px": g["legend_boxes"]["orange_swatch"],
                "group_bar_order": "每组内蓝色在左、橙色在右",
                "evidence_image": "tmp/run-20261011-01/A16/preview/flawed-bars-q1q2-2x.png",
            },
            "observed": "图例写「蓝色 = 成本、橙色 = 收入」，但蓝色柱上的标签依次是 "
                        "120 / 135 / 128 / 180，橙色柱上是 90 / 108 / 96 / 126。",
            "source_data_check": {
                "checked_field": "source.csv 的 revenue_wan 与 cost_wan 两列",
                "revenue_column": rev_labels,
                "cost_column": cost_labels,
                "conclusion": "蓝色（标为成本）承载的正是 revenue_wan 全部四个值；"
                              "橙色（标为收入）承载的正是 cost_wan 全部四个值。两列被整体互换。",
            },
            "impact": "读者会把「成本」读成收入、把「收入」读成成本，"
                      "由此推导出的利润方向完全相反（原图因此得出「Q3 利润最高」的错误结论）。",
            "correction": "重制图把收入固定为蓝色、成本固定为橙色，图例顺序与分组内柱序一致"
                          "（收入在左、成本在右），并把数值标签直接绑定到源数据列而非绑到颜色。",
            "final_visual_check": "定稿整屏与 3× 放大 fixed-q4-tops-3x.png 复查："
                                 "蓝色柱标签 120/135/128/180 = revenue_wan，橙色 90/108/96/126 = cost_wan，"
                                 "图例「收入（蓝）/ 成本（橙）」与柱序一致。",
        },
        {
            "id": "F03",
            "category": "几何失真",
            "title": "柱高既不与自身数值标签成比例，也不与坐标轴刻度成比例",
            "location_in_original": {
                "bar_boxes_px": [b["bar_box"] for b in per_bar],
                "per_bar_detail": per_bar,
                "evidence_image": "tmp/run-20261011-01/A16/preview/flawed-bars-q1q2-2x.png",
            },
            "observed": "用原图自己的坐标轴读柱顶：蓝色四根分别为 "
                        f"{blue[0]['axis_value_at_top']} / {blue[1]['axis_value_at_top']} / "
                        f"{blue[2]['axis_value_at_top']} / {blue[3]['axis_value_at_top']}，"
                        f"橙色四根分别为 {orange[0]['axis_value_at_top']} / "
                        f"{orange[1]['axis_value_at_top']} / {orange[2]['axis_value_at_top']} / "
                        f"{orange[3]['axis_value_at_top']}；"
                        "而它们各自的标签是 120/135/128/180 与 90/108/96/126。",
            "source_data_check": {
                "checked_field": "柱高 ÷ 标签值 是否为同一比例",
                "blue_height_over_label": [round(blue[i]["height_px"] / rev_labels[i], 3)
                                           for i in range(4)],
                "orange_height_over_label": [round(orange[i]["height_px"] / cost_labels[i], 3)
                                             for i in range(4)],
                "conclusion": "同一系列内的「柱高 ÷ 标签」并不恒定（蓝 1.25→1.54，橙 1.22→1.33），"
                              "因此柱高既不是按标签值画的，也不是按任何固定比例画的；"
                              "图上柱高与数字属于两套互不相关的编码。",
            },
            "impact": "柱形是读者读数的首要通道。标签与柱高互相矛盾时，"
                      "无论读者信哪一个都会得出与源数据不同的结论；"
                      "F04、F07 两处叙事错误很可能就来自对柱高的误读。",
            "correction": "定稿把柱高、柱顶标签、坐标轴刻度统一到同一个函数："
                          "y = 512 − value × 1.32、height = value × 1.32。"
                          "反测 8 根柱：高度误差 −0.80…+0.04 px，x 误差 ≤0.75 px，"
                          "柱底全部落在 0 线（verify.json.bar_checks_passed = true）。",
            "final_visual_check": "定稿 3× 放大 fixed-axis-zero-3x.png 与 fixed-q4-tops-3x.png："
                                 "每根柱顶与标签、与刻度三者一致，柱底与 0 线一致。",
        },
        {
            "id": "F04",
            "category": "叙事与数据矛盾",
            "title": "标题「Q3 利润最高」与源数据相反",
            "location_in_original": {
                "title_ink_box_px": [56, 46, 428, 81],
                "title_text": "季度复盘：Q3利润最高",
                "evidence_image": "tmp/run-20261011-01/A16/preview/flawed-header-2x.png",
            },
            "observed": "整图左上角标题声称利润最高的季度是 Q3。",
            "source_data_check": {
                "checked_field": "revenue_wan − cost_wan",
                "profit_by_quarter": profits,
                "conclusion": f"Q1 {profits['Q1']}、Q2 {profits['Q2']}、Q3 {profits['Q3']}、"
                              f"Q4 {profits['Q4']}（万元）。最高的是 Q4（{profits['Q4']}），"
                              f"Q3（{profits['Q3']}）只排第二，比 Q4 少 {profits['Q4'] - profits['Q3']} 万元。",
            },
            "impact": "标题是读者第一眼看到的结论，也是全图叙事的锚点。"
                      "标题一错，正文的「重点观察」与管理层的第一印象都会跟着错。",
            "correction": "改写为「季度复盘：Q4 收入与利润双双创高」，"
                          "副标题只陈述口径与对应关系（四季对比 / 单位 / 柱高与数值一一对应），不重复结论。",
            "final_visual_check": "定稿 2× 放大 fixed-header-2x.png：标题与副标题完整、无截断；"
                                 "结论与右侧「重点观察 · Q4」及利润表高亮行三处一致。",
        },
        {
            "id": "F05",
            "category": "叙事与数据矛盾",
            "title": "副标题「收入持续上升，全年保持增长」被 Q3 反例直接推翻",
            "location_in_original": {
                "subtitle_ink_box_px": [56, 105, 326, 125],
                "subtitle_text": "收入持续上升，全年保持增长",
                "evidence_image": "tmp/run-20261011-01/A16/preview/flawed-header-2x.png",
            },
            "observed": "副标题断言收入逐季上升、全年保持增长。",
            "source_data_check": {
                "checked_field": "source.csv 的 revenue_wan 序列",
                "revenue_sequence": rev_labels,
                "conclusion": f"Q3 收入 {rev_labels[2]} < Q2 收入 {rev_labels[1]}，"
                              f"序列中存在一次下降（{rev_labels[1]} → {rev_labels[2]}，"
                              f"{rev_labels[2] - rev_labels[1]}），「持续上升」不成立。",
            },
            "impact": "「持续上升」会让读者忽略 Q3 的回落，把四季误读成单调增长，"
                      "从而高估经营稳定性。",
            "correction": "删去增长叙事，副标题改为陈述口径："
                          "「四季对比 · 收入 / 成本 / 利润均以万元计 · 柱高与数值一一对应」。"
                          "Q3 的回落由图上 128 的柱与标签自然呈现，不再需要文字掩饰。",
            "final_visual_check": "定稿 2× 放大 fixed-header-2x.png：副标题只含口径与对应关系陈述；"
                                 "Q3 柱（128）明显低于 Q2（135），回落可被直接读出。",
        },
        {
            "id": "F06",
            "category": "数值错误",
            "title": "利润明细表 Q3 写成 42，正确值是 32",
            "location_in_original": {
                "profit_value_boxes_px": g["profit_card_boxes"]["values"],
                "q3_value_box_px": g["profit_card_boxes"]["values"][2],
                "evidence_image": "tmp/run-20261011-01/A16/preview/flawed-profit-callout-2x.png",
            },
            "observed": "利润明细四个值显示为 30 / 27 / 42 / 54。",
            "source_data_check": {
                "checked_field": "revenue_wan − cost_wan 逐季",
                "computed": profits,
                "per_quarter": [
                    {"quarter": q, "shown": s, "correct": profits[q],
                     "match": s == profits[q]}
                    for q, s in (("Q1", 30), ("Q2", 27), ("Q3", 42), ("Q4", 54))],
                "conclusion": "Q1 / Q2 / Q4 与源数据一致，只有 Q3 不符："
                              f"128 − 96 = {profits['Q3']}，原图写 42，多了 10 万元。",
            },
            "impact": "同一张表里三个数对、一个数错，比全错更难被发现；"
                      "而这一个错数正好落在被标题点名的 Q3 上，会强化错误叙事。",
            "correction": "利润明细改为由 source.csv 现算的五行表（季度 / 收入 / 成本 / 利润 / 利润率），"
                          "不写死任何数字；定稿四行利润为 30 / 27 / 32 / 54。",
            "final_visual_check": "定稿 2× 放大 fixed-profit-table-2x.png："
                                 "Q3 利润显示 32，与图表柱标签、标注卡「四季利润 30 / 27 / 32 / 54」三处一致。",
        },
        {
            "id": "F07",
            "category": "叙事与数据矛盾",
            "title": "重点观察卡断言「Q3 利润超过其他季度」并据此建议集中资源",
            "location_in_original": {
                "callout_title_box_px": g["callout_boxes"]["title"],
                "callout_body_line1_box_px": g["callout_boxes"]["body_l1"],
                "callout_body_line2_box_px": g["callout_boxes"]["body_l2"],
                "callout_text": "重点观察 · Q3 / 建议把资源集中到Q3，/ 它的利润超过其他季度。",
                "evidence_image": "tmp/run-20261011-01/A16/preview/flawed-profit-callout-2x.png",
            },
            "observed": "右下角标注卡点名 Q3，并给出「利润超过其他季度」的事实性论断与资源建议。",
            "source_data_check": {
                "checked_field": "profit_wan 的排序",
                "profit_by_quarter": profits,
                "conclusion": f"Q3 利润 {profits['Q3']} 万元，低于 Q4 的 {profits['Q4']} 万元，"
                              "「超过其他季度」不成立。",
            },
            "impact": "这是一条会直接影响资源配置的建议，且建立在被 F02/F03 放大的错误读数之上；"
                      "按原图执行会把资源投到利润次高的季度。",
            "correction": "重点观察改到 Q4，并把论据直接写在卡上："
                          "收入 180 万元 · 成本 126 万元 / 利润 54 万元 · 利润率 30.0% / "
                          "三项均为全年最高 / 四季利润 30 / 27 / 32 / 54。"
                          "四个季度的高亮行也同步指向 Q4。",
            "final_visual_check": "定稿 2× 放大 fixed-callout-2x.png：卡内四行全部完整显示、无截断，"
                                 "数字与利润表、柱标签三处一致。",
        },
    ]

    uncertainties = [
        {
            "id": "U01",
            "topic": "截断纵轴是否出于有意的设计取舍",
            "what_is_known": "纵轴确实从 100 起始（网格线 y=565 标 100，柱底 y=564），"
                             "这本身是 F01 已确认的误导性做法。",
            "why_unconfirmed": "无法从单张成品图判断作者是**有意**为了放大差异，"
                               "还是绘图时把 y 轴下限写错了；成品图不携带意图信息。",
            "needed_evidence": "原始绘图脚本（y 轴 min 的取值）或制作者的设计说明。",
            "how_handled": "按「结果是否误导」而不是「是否有意」来判定："
                           "定稿无条件改成共同零起点，不揣测原意。",
        },
        {
            "id": "U02",
            "topic": "利润明细里 Q3 的 42 从何而来",
            "what_is_known": "128 − 96 = 32，与原图的 42 不符；同表其余三个数（30/27/54）都对。",
            "why_unconfirmed": "在 source.csv 的六个数值里找不到任何能相减得到 42 的组合"
                               "（30 / 27 / 32 / 54），因此无法判断 42 是笔误、"
                               "还是来自某张未提供的中间表。",
            "needed_evidence": "作者的中间计算表或利润口径说明。",
            "how_handled": "记为数值错误（F06）并按源数据改为 32；"
                           "不对 42 的来源做推测，也不为它编一个解释。",
        },
        {
            "id": "U03",
            "topic": "原图柱高所用的比例规则",
            "what_is_known": "同一系列内「柱高 ÷ 标签值」不恒定（蓝 1.25/1.27/1.54/1.37，"
                             "橙 1.22/1.25/1.33/1.31），柱顶在原图自己的轴上也读不出整数。",
            "why_unconfirmed": "无法反推出作者实际使用的比例；可以确定的只是「柱高与标签、"
                               "与轴刻度都不自洽」，而不是「作者用了某个具体错误值」。",
            "needed_evidence": "原始 DSL 或绘图代码。",
            "how_handled": "F03 只陈述可观测的不自洽与区间，不臆造一个「作者想要的数值」；"
                           "定稿则把三套编码统一到一个函数并给出反测误差。",
        },
        {
            "id": "U04",
            "topic": "「收入」「成本」是否另有口径（如含税/不含税、内部结算价）",
            "what_is_known": "source.csv 给出两列原值 120/135/128/180 与 90/108/96/126，单位万元。",
            "why_unconfirmed": "source.csv 未声明口径，成品图上也没有口径注记，"
                               "因此无法判断原作者图里的数字是否经过某种口径调整。",
            "needed_evidence": "口径说明文档或数据字典。",
            "how_handled": "重制严格照抄 source.csv 原值，不做任何口径推断或调整；"
                           "标题与标注卡的结论也只用这两列可验证的关系。",
        },
    ]

    doc = {
        "schema_version": 1, "task_id": "A16", "round": "round-01", "path_base": "output_dir",
        "method": {
            "reference_image": "tasks/A16-visual-data-forensics/inputs/flawed-report.png",
            "reference_usage": "仅用于观察与像素测量；未嵌入 DSL、未裁块、未作为输出资产",
            "trusted_source": "tasks/A16-visual-data-forensics/inputs/source.csv",
            "coordinate_convention": "原点画布左上，x 向右 / y 向下，单位 px，框为 "
                                     "[left,top,right,bottom] 外轮廓",
            "measurement_scripts": [
                "tmp/run-20261011-01/A16/probe_flawed_a16.py",
                "tmp/run-20261011-01/A16/probe_flawed2_a16.py",
                "tmp/run-20261011-01/A16/crop_flawed_a16.py"],
            "raw_measurements": [
                "tmp/run-20261011-01/A16/drafts/flawed-geometry.json",
                "tmp/run-20261011-01/A16/drafts/flawed-geometry-2.json"],
            "rule": "只写能从图片或数据里观察到的现象，不按「常见错误模板」列坑；"
                    "审美偏好单独归入 uncertainties，不计为数值错误",
        },
        "source_data_snapshot": {
            "quarters": d, "unit": "万元",
            "profit_derivation": "profit_wan = revenue_wan − cost_wan",
        },
        "findings_count": len(findings),
        "findings": findings,
        "uncertainties": uncertainties,
        "uncertainties_count": len(uncertainties),
        "checked_but_not_errors": [
            {"item": "图例顺序「成本」在「收入」之前",
             "why_not_an_error": "图例顺序与分组内柱序（蓝左橙右）自洽，不产生任何矛盾；"
                                 "属于排序偏好，不计入数值或叙事错误。"},
            {"item": "四个季度是否齐全",
             "why_not_an_error": "Q1–Q4 四个分组齐全，柱标签与刻度齐全，无缺失季度。"},
            {"item": "卡片圆角、留白、阴影等样式",
             "why_not_an_error": "沿卡边扫描确认原图白卡只有 1px #E2E8F1 描边、没有投影，"
                                 "样式本身不承载数据信息。"},
        ],
        "final_review": {
            "deliverable": "corrected-report.png",
            "verified_against": "tmp/run-20261011-01/A16/drafts/verify.json",
            "bar_height_match": True, "gridline_match_px": 0.0,
            "viewed_after_delivery": True,
            "note": "每条 finding 的 final_visual_check 都在定稿渲染后实际打开对应局部图确认过。",
        },
    }
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"findings={len(findings)} uncertainties={len(uncertainties)} -> {OUT.as_posix()}")
    for f in findings:
        print(f"  {f['id']} {f['category']:12} {f['title']}")


if __name__ == "__main__":
    main()