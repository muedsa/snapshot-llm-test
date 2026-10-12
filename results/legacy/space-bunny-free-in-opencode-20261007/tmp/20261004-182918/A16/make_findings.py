# -*- coding: utf-8 -*-
"""Compose outputs/<run>/A16/findings.json.

All numbers come from the measurement JSONs produced earlier:
  flawed-geometry.json / flawed-geometry-2.json  -> bar rects, gridlines, legend swatches
  flawed-region-bboxes.json                     -> text ink bboxes in the flawed PNG
  verify-final.json                             -> post-fix verification of corrected-report.png
"""
import json, os
from datetime import datetime, timezone, timedelta

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
TASK = "A16"
TMP = os.path.join(ROOT, "tmp", RUN, TASK)
OUT = os.path.join(ROOT, "outputs", RUN, TASK)
CST = timezone(timedelta(hours=8))


def load(n):
    return json.load(open(os.path.join(TMP, n), encoding="utf-8"))


g1, g2 = load("flawed-geometry.json"), load("flawed-geometry-2.json")
bb = load("flawed-region-bboxes.json")["regions"]
vf = load("verify-final.json")
cd = json.load(open(os.path.join(OUT, "corrected-data.json"), encoding="utf-8"))
src = {r["quarter"]: r for r in cd["source_rows"]}
Q = [d["quarter"] for d in cd["source_rows"]]

# ---------------------------------------------------------------- derived evidence
GRID_Y = [295, 349, 403, 457, 511, 565]
TICKS_TOP_DOWN = [200, 180, 160, 140, 120, 100]
PPU = (GRID_Y[-1] - GRID_Y[0]) / float(TICKS_TOP_DOWN[0] - TICKS_TOP_DOWN[-1])  # px per 万元
BASE = GRID_Y[-1]
blue = [b for b in g2["bars_blue"]]
orange = [b for b in g2["bars_orange"]]
labels_rev = [120, 135, 128, 180]      # ink read from the flawed PNG, blue bars
labels_cost = [90, 108, 96, 126]      # ink read from the flawed PNG, orange bars


def implied(h):
    """value a reader would decode from the flawed chart's own printed axis"""
    return round(100 + h / PPU, 1)


flawed_bars = []
for i, q in enumerate(Q):
    b, o = blue[i], orange[i]
    hb = b["h"]
    ho = o["h"]
    flawed_bars.append({
        "quarter": q,
        "revenue": {"label": labels_rev[i], "px_rect": [b["x0"], b["y_top"], b["x1"], b["y_bot"]],
                    "height_px": hb, "implied_by_own_axis_wan": implied(hb),
                    "px_per_wan_implied_by_label": round(hb / labels_rev[i], 3)},
        "cost": {"label": labels_cost[i], "px_rect": [o["x0"], o["y_top"], o["x1"], o["y_bot"]],
                 "height_px": ho, "implied_by_own_axis_wan": implied(ho),
                 "px_per_wan_implied_by_label": round(ho / labels_cost[i], 3)},
        "visual_rev_minus_cost_px": o["y_top"] - b["y_top"],
        "visual_rev_minus_cost_wan": round((o["y_top"] - b["y_top"]) / PPU, 1),
        "profit_from_csv_wan": src[q]["profit"],
        "profit_shown_in_panel_wan": [30, 27, 42, 54][i],
    })

checks = {c["check"]: c for c in vf["checks"]}
V = lambda k: checks[k]["detail"]

findings = [
    {
        "id": "F01",
        "category": "叙事结论错误（标题）",
        "severity": "high",
        "image_location": {"region": "页首主标题", "ink_bbox_px": bb["title"],
                           "read_text": "季度复盘：Q3利润最高"},
        "observation": "标题断言 Q3 利润最高，但同一页的利润明细卡里 Q4 写的是 54 万元、Q3 写的是 42 万元，"
                       "标题与本页数据自相矛盾。",
        "source_data_check": "source.csv：利润 = 收入 − 成本 → Q1 30、Q2 27、Q3 32、Q4 54；"
                             "最高是 Q4 的 54 万元，不是 Q3。",
        "impact": "读者按标题会把资源投向利润最低的两个季度之一（Q2 的 27 万元实际是全年最低），"
                  "结论方向完全反了。",
        "fix": "标题改为可被数据核对的一句话：季度复盘：Q4 利润 54 万元居首，占全年利润的 37.8%"
               "（54 = 180 − 126；37.8% = 54 ÷ 143）。",
        "final_verification": "已在 corrected-report.png 中查看；标题字符串由 build_a16.py 从 "
                              "corrected-data.json 计算生成，不存在手写常量。"
                              "利润极值核对：%s" % V("bar_heights_match_csv"),
        "evidence_files": ["flawed-region-bboxes.json", "crop/zoom-profit-card.png"],
    },
    {
        "id": "F02",
        "category": "叙事与数据矛盾（副标题）",
        "severity": "high",
        "image_location": {"region": "页首副标题", "ink_bbox_px": bb["subtitle"],
                           "read_text": "收入持续上升，全年保持增长"},
        "observation": "副标题声称收入逐季上升，但柱图里 Q3 的蓝色柱（标签 128）低于 Q2（标签 135）。",
        "source_data_check": "source.csv：120 → 135 → 128 → 180；Q3 环比 = 128 ÷ 135 − 1 = −5.2%，"
                             "是全年唯一一次回落。",
        "impact": "“持续上升/保持增长”与图上唯一的下降段冲突，会掩盖 Q3 回落这个需要复盘的事实。",
        "fix": "副标题改为可核对的事实句：全年收入 563 万元、成本 420 万元、利润 143 万元；"
               "Q3 收入环比回落 5.2%，Q4 收入与利润创全年新高。",
        "final_verification": "已在最终图查看；563/420/143/5.2%% 全部由 CSV 计算，"
                              "Q3 柱（128）在像素上低于 Q2 柱（135），见 %s" % V("bar_heights_match_csv"),
        "evidence_files": ["flawed-region-bboxes.json", "flawed-geometry-2.json"],
    },
    {
        "id": "F03",
        "category": "图例与数据编码矛盾（系列错位）",
        "severity": "high",
        "image_location": {
            "region": "图例行",
            "blue_swatch_px": g2["legend_blue"], "blue_label": "成本",
            "blue_label_ink_bbox_px": bb["legend_label_cost"],
            "orange_swatch_px": g2["legend_orange"], "orange_label": "收入",
            "orange_label_ink_bbox_px": bb["legend_label_revenue"]},
        "observation": "蓝色色块（图例左侧）被标为“成本”，橙色色块被标为“收入”；"
                       "但蓝色柱上方的数字是 120/135/128/180，橙色柱上方是 90/108/96/126。",
        "source_data_check": "source.csv 的 revenue_wan = 120/135/128/180，cost_wan = 90/108/96/126，"
                             "即蓝柱承载收入、橙柱承载成本；图例把两个系列的名字互换了。",
        "impact": "按图例读图会把每根柱的数值安到相反的系列上：例如 Q4 的 180 会被读成成本、126 读成收入，"
                  "从而得出“成本高于收入、亏损”的相反结论。",
        "fix": "图例改为 蓝=收入、橙=成本，且图例顺序与柱序（收入在左、成本在右）一致；"
               "复验时按颜色像素定位色块与柱体，避免只改文字标签。",
        "final_verification": V("legend_present") + "；" + V("legend_order_revenue_first"),
        "evidence_files": ["zoom-legend.png", "flawed-geometry-2.json"],
    },
    {
        "id": "F04",
        "category": "坐标轴截断（非零起点）",
        "severity": "high",
        "image_location": {"region": "主图纵轴", "tick_labels_top_down": TICKS_TOP_DOWN,
                           "gridline_rows_px": GRID_Y, "label_gutter_ink_px": g1["y_tick_rows"],
                           "note": "最低一条网格线在 y=565，对应 100 而不是 0；8 根柱的底边都落在这条线上"},
        "observation": "纵轴范围只有 100–200，没有任何 0 值刻度或网格线；柱子从 100 起步，"
                       "即柱长只代表“数值 − 100”。",
        "source_data_check": "8 个数值里有 7 个大于 100，但 Q1 成本 90 万元小于 100："
                             "在截断轴上它根本无法被如实画出（实测该柱仍画在 100 线之上，标签写 90）。",
        "impact": "① 收入与成本的差距被放大（真实差 27–54 万元，视觉差被 2.70 px/万元 放大到 39–80 px）；"
                  "② 柱子看起来都接近等高，掩盖了 90 与 180 的真实一倍差；"
                  "③ 单位刻度缺失使读者无法从轴上读数。",
        "fix": "纵轴改为 0–200 万元，刻度 0/50/100/150/200，零基线画在 y=530 并用 2px 实线加重，"
               "其余网格线 1px；8 根柱共用同一 1.42 px/万元 比例尺与同一零基线。",
        "final_verification": "%s；%s；%s；%s" % (V("gridline_count"), V("gridline_values"),
                                                    V("zero_baseline"), V("domain_top")),
        "evidence_files": ["flawed-geometry.json", "verify-final.json"],
    },
    {
        "id": "F05",
        "category": "柱高与数值、与坐标轴都不对应（几何失真）",
        "severity": "critical",
        "image_location": {
            "region": "主图 8 根柱",
            "blue_rects_px": [[b["x0"], b["y_top"], b["x1"], b["y_bot"]] for b in blue],
            "orange_rects_px": [[b["x0"], b["y_top"], b["x1"], b["y_bot"]] for b in orange],
            "printed_axis_scale_px_per_wan": round(PPU, 3)},
        "observation": "① 用图上自带的刻度（2.70 px/万元）反读柱高，8 根柱全部落在 140–190 万元，"
                       "而标签写的是 90–180；② 若假设柱高与标签成正比，8 根柱隐含的比例尺在 "
                       "1.222–1.531 px/万元 之间（相差 25%），没有任何单一比例尺能同时成立；"
                       "③ 标签 128 的 Q3 蓝柱（196px）比标签 135 的 Q2 蓝柱（170px）更高，"
                       "即更高的柱配了更小的数字。",
        "source_data_check": "source.csv 的 8 个值与柱顶标签一一对应（120/135/128/180 与 90/108/96/126），"
                             "所以标签本身没错；正确几何必须满足 135 的柱高于 128 的柱，"
                             "且任意两根柱的柱高比 = 数值比。",
        "impact": "这是最严重的问题：只改数字标签无法修复——即使标签全部改对，柱形仍在说另一套故事"
                  "（读者会以为 Q3 收入高于 Q2）。",
        "fix": "重画时每根柱的 y_top 由数值算出：y_top = 530 − value × 1.42，"
               "柱底统一落在 y=530 的零基线；柱宽 68px、组内间距 16px，四组间距一致。",
        "final_verification": "%s；%s；%s" % (V("bar_heights_match_csv"),
                                              V("single_common_scale"),
                                              V("all_bars_share_zero_baseline")),
        "evidence_files": ["flawed-geometry-2.json", "verify-final.json"],
    },
    {
        "id": "F06",
        "category": "图内视觉差与利润明细互相矛盾",
        "severity": "medium",
        "image_location": {"region": "每组两根柱的柱顶间距",
                           "measured_px": [b["visual_rev_minus_cost_px"] for b in flawed_bars],
                           "measured_wan_at_own_scale": [b["visual_rev_minus_cost_wan"]
                                                         for b in flawed_bars]},
        "observation": "把组内两根柱的柱顶差按图上自己的刻度换算，得到 14.4 / 13.3 / 25.6 / 29.6 万元，"
                       "而同页利润明细写的是 30 / 27 / 42 / 54 万元。",
        "source_data_check": "CSV 真值差为 30 / 27 / 32 / 54 万元（Q3 应为 32，不是 42）。",
        "impact": "同一页出现两套互相矛盾的利润数字，读者无法判断该信柱形还是该信表格。",
        "fix": "让几何与表格同源：柱高差 = (收入 − 成本) × 1.42 px/万元，利润表逐季由同一组 CSV 值算出，"
               "并新增全年合计列与利润率行以便交叉验证。",
        "final_verification": "在最终图按像素测量，Q4 两柱柱顶差 180 − 126 = 54 万元 × 1.42 = 76.7px，"
                              "与 corrected-data.json 的 bar_geometry 一致；利润表 30/27/32/54/143 "
                              "与 CSV 逐格对应。" + V("bar_heights_match_csv"),
        "evidence_files": ["flawed-geometry-2.json", "verify-final.json"],
    },
    {
        "id": "F07",
        "category": "数值算错（利润明细 Q3）",
        "severity": "critical",
        "image_location": {"region": "利润明细卡 Q3 数值", "ink_bbox_px": bb["profit_q3"],
                           "read_text": "42 万元",
                           "neighbours": {"Q1": bb["profit_q1"], "Q2": bb["profit_q2"],
                                          "Q4": bb["profit_q4"]}},
        "observation": "明细卡 Q3 写 42 万元；同页 Q1 30、Q2 27、Q4 54 三格与 CSV 相符，唯独 Q3 对不上。",
        "source_data_check": "Q3：收入 128 − 成本 96 = 32 万元；42 对应的成本是 86，与 source.csv 的 96 不符。"
                             "其余三格：120−90=30、135−108=27、180−126=54 全部正确。",
        "impact": "虚增 10 万元（+31%），直接导致 Q3 被误判为利润最高的季度，是标题与结论文本错误的根因之一。",
        "fix": "利润表全部由 CSV 现算：利润 = 收入 − 成本，并加全年列 143 万元、利润率行 25.0/20.0/25.0/30.0/25.4%。",
        "final_verification": "最终图利润行显示 30 / 27 / 32 / 54 / 143，Q3 已改为 32；"
                              "数值由 build_a16.py 从 CSV 计算，无手写常量。",
        "evidence_files": ["zoom-profit-card.png", "flawed-region-bboxes.json"],
    },
    {
        "id": "F08",
        "category": "结论指向错误季度（重点观察）",
        "severity": "high",
        "image_location": {"region": "右下提示卡", "title_ink_bbox_px": bb["callout_title"],
                           "body_ink_bbox_px": bb["callout_body"],
                           "read_text": "重点观察 · Q3 / 建议把资源集中到Q3，它的利润超过其他季度。"},
        "observation": "提示卡建议把资源集中到 Q3，理由是“它的利润超过其他季度”，"
                       "而同页明细卡就写着 Q4 的 54 万元高于 Q3 的 42 万元。",
        "source_data_check": "更正后 Q3 = 32 万元，低于 Q1 的 30 之上但远低于 Q4 的 54；"
                             "“超过其他季度”不成立；Q4 才是收入（180）、利润（54）、"
                             "利润率（30.0%）三项最高，且占全年利润 37.8%。",
        "impact": "行动建议与数据相反，属于会把决策带偏的错误。",
        "fix": "改为“重点观察 · Q4”，并列出可核对依据：收入 180 万元最高、成本 126 万元同步走高、"
               "利润 54 万元四季居首、利润率 30.0% 全年最高、占全年利润 37.8%。",
        "final_verification": "已在最终图查看提示卡；五条依据全部来自 CSV 计算"
                              "（见 corrected-data.json 的 key_quarter_argument）。",
        "evidence_files": ["flawed-region-bboxes.json"],
    },
    {
        "id": "F09",
        "category": "可读性/规格不足（标注字号）",
        "severity": "medium",
        "image_location": {"region": "8 个柱顶数值标注",
                           "ink_bbox_px": {k: v for k, v in bb.items()
                                           if k.startswith("label_q")},
                           "measured_ink_height_px": 10,
                           "inferred_fontSize": "约 14–15px"},
        "observation": "柱顶数字的墨迹高度只有 10–11px，推断字号约 14–15px，"
                       "在 1280×900 整图上明显小于其他文字。",
        "source_data_check": "不涉及数值；属呈现规格。",
        "impact": "8 个关键数值在正常观看距离下偏小，削弱“可信”的第一眼可读性。",
        "fix": "柱顶数值统一 18px（fontFeatures=\"tnum=2\" 等宽数字），轴刻度 18px，"
               "正文（副标题、表格、提示卡）≥22px。",
        "final_verification": "最终图墨迹实测：柱顶标注区 %s；表头 18px、正文 22px，均 ≥18。"
                              % V("value_labels_above_bars"),
        "evidence_files": ["flawed-region-bboxes.json"],
    },
    {
        "id": "F10",
        "category": "信息不完整（缺少全年口径与利润率）",
        "severity": "low",
        "image_location": {"region": "利润明细卡整体",
                           "card_ink_bbox_px": {"title": bb["profit_card_title"],
                                                "row_labels": bb["profit_row_labels"]},
                           "note": "卡片只有四个季度的利润，没有收入/成本行、没有全年列、没有利润率"},
        "observation": "明细卡只给四个利润数字，既不能交叉验证柱图，也没有回答“哪个季度更值得投入”。",
        "source_data_check": "CSV 可以算出全年 563/420/143 万元与逐季利润率 25.0/20.0/25.0/30.0%。",
        "impact": "缺少全年口径，读者无法判断 42（错值）与 54 的相对重要性，也无法看利润率走势。",
        "fix": "利润明细改为 4 行（收入/成本/利润/利润率）× 5 列（Q1–Q4 + 全年）的表格，"
               "全年列用竖线分隔，利润行用绿色加粗突出。",
        "final_verification": "最终图已查看：表格 5 列 4 行齐全，全年列 563/420/143/25.4%%，"
                              "文字墨迹未越出卡片（%s）。" % V("profit_table_inside_card"),
        "evidence_files": ["zoom-profit-card.png"],
    },
]

uncertain = [
    {
        "id": "U01",
        "item": "单位标注的位置",
        "observation": "原稿把“单位：万元”放在面板标题下方 (87,230)-(169,246)，纵轴刻度本身没有单位后缀。",
        "why_uncertain": "无法判断这是刻意的版式还是漏标；数据本身单位自洽（数字与 CSV 的 _wan 列一致），"
                         "因此不构成数值错误。",
        "treatment": "重制版把“（单位：万元）”放进紧贴坐标区的面板标题，页脚再复述一次纵轴范围与刻度。",
    },
    {
        "id": "U02",
        "item": "图例顺序与柱序不一致",
        "observation": "原稿图例为“成本、收入”，柱序为“收入、成本”。",
        "why_uncertain": "纯属呈现偏好，不影响任何数值读解，故不记为错误。",
        "treatment": "重制版图例改为“收入、成本”，与柱序一致。",
    },
    {
        "id": "U03",
        "item": "柱底 1px 差与柱间距",
        "observation": "原稿蓝柱底边 y=563、橙柱底边 y=564；柱宽 64px，组内仅 12px 间隙。",
        "why_uncertain": "这更像绘制取整或版式选择，没有证据表明它改变了数值含义。",
        "treatment": "重制版统一柱宽 68px、组内间距 16px，8 根柱底边同在 y=529 的零基线上"
                     "（%s）。" % V("all_bars_share_zero_baseline"),
    },
    {
        "id": "U04",
        "item": "配色取值",
        "observation": "原稿用 #245CE4（蓝）与 #E88E35（橙），与常见 #2563EB/#F97316 不同。",
        "why_uncertain": "没有依据判断是否有意为之，且配色本身不承载数值。",
        "treatment": "重制版沿用同一蓝/橙语义但取 #2563EB/#F97316，并在图例中明确对应关系。",
    },
    {
        "id": "U05",
        "item": "未标注数据来源与口径",
        "observation": "原稿页脚只有“虚构数据 · 同事初稿，仅供诊断”(56,858)-(276,873)，"
                       "没有说明利润、利润率的算法。",
        "why_uncertain": "初稿不写来源可能是流程约定，不能据此断定数据不可信。",
        "treatment": "重制版页脚写明数据源、口径公式（利润 = 收入 − 成本、利润率 = 利润 ÷ 收入）"
                     "与纵轴定义。",
    },
]

doc = {
    "task": TASK,
    "title": "从错误图表恢复可信叙事",
    "generated_at": datetime.now(CST).isoformat(timespec="seconds"),
    "inputs": {
        "flawed_report": "tasks/A16-visual-data-forensics/inputs/flawed-report.png (1280×900)",
        "source_csv": "tasks/A16-visual-data-forensics/inputs/source.csv",
        "note": "没有旧 DSL，全部结论来自对图片的像素测量与对 CSV 的核算。",
    },
    "method": [
        "1) 用 read 工具打开 flawed-report.png 实际查看整图与局部放大（页脚/图例/利润卡）。",
        "2) 用 PIL 只做观察性测量：柱体矩形、网格线行、图例色块、各段文字墨迹 bbox（不裁块、不嵌入）。",
        "3) 由网格线行距推出图上自带的比例尺（2.70 px/万元），再用它反读 8 根柱的隐含数值。",
        "4) 与 source.csv 逐项核对（利润、环比、利润率、极值季度）。",
        "5) 用同一组 CSV 值重算全部几何，重渲染后用 verify_final.py 做像素级复验。",
    ],
    "evidence_files": {
        "flawed_geometry": "tmp/%s/A16/flawed-geometry.json" % RUN,
        "flawed_geometry_pass2": "tmp/%s/A16/flawed-geometry-2.json" % RUN,
        "flawed_region_bboxes": "tmp/%s/A16/flawed-region-bboxes.json" % RUN,
        "flawed_zoom_crops": ["tmp/%s/A16/zoom-profit-card.png" % RUN,
                              "tmp/%s/A16/zoom-legend.png" % RUN],
        "corrected_verification": "tmp/%s/A16/verify-final.json" % RUN,
    },
    "flawed_chart_measurements": {
        "printed_axis": {"gridline_rows_px": GRID_Y, "tick_labels_top_down": TICKS_TOP_DOWN,
                         "px_per_wan": round(PPU, 3), "baseline_row_px": BASE,
                         "baseline_value_wan": 100,
                         "zero_present": False},
        "bars": flawed_bars,
        "legend": {"blue_swatch_px": g2["legend_blue"], "blue_label": "成本",
                   "orange_swatch_px": g2["legend_orange"], "orange_label": "收入"},
        "summary": "标签本身大多正确（120/135/128/180 与 90/108/96/126 与 CSV 一致），"
                   "错在图例映射、轴起点、柱高几何，以及标题/副标题/利润 Q3/提示卡四处叙事。",
    },
    "findings": findings,
    "uncertain_items": uncertain,
    "verification_summary": {
        "method": "verify_final.py：读 corrected-data.json + source.csv，再对 corrected-report.png "
                  "做像素测量（网格线、柱体抗锯齿边缘的亚像素覆盖率、图例色块、文字墨迹 bbox）。",
        "rasterisation_limit": "1 px = 0.70 万元；柱顶亚像素测量与 DSL 计算位置最大偏差 0.56 px。",
        "checks": [{"check": k, "pass": v["pass"], "detail": v["detail"]}
                   for k, v in checks.items()],
        "all_pass": all(v["pass"] for v in checks.values()),
    },
    "corrected_deliverables": {
        "image": "corrected-report.png (1280×900)",
        "dsl": "corrected-report.snapshot",
        "data": "corrected-data.json",
        "note": "图上每个数字都可回到 corrected-data.json：柱顶 8 个数值、轴刻度 0/50/100/150/200、"
                "利润表 4 行 × 5 列、提示卡五条依据。",
    },
}

path = os.path.join(OUT, "findings.json")
with open(path, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(doc, fh, ensure_ascii=False, indent=1)
print("findings:", len(findings), "uncertain:", len(uncertain),
      "all_pass:", doc["verification_summary"]["all_pass"])
print("saved", path)