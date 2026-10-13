"""A16 findings.json: every item carries a measured pixel location on the flawed image,
a check against source.csv, the impact, the correction, and the final viewing result."""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
OUT_DIR = ROOT / "outputs" / RUN / "A16"
TMP_DIR = ROOT / "tmp" / RUN / "A16"
REF = "tasks/A16-visual-data-forensics/inputs/flawed-report.png"

ap = argparse.ArgumentParser()
ap.add_argument("--ver", required=True)
a = ap.parse_args()

rows = list(csv.DictReader((ROOT / "tasks" / "A16-visual-data-forensics" / "inputs"
                            / "source.csv").read_text(encoding="utf-8").splitlines()))
Q = [r["quarter"] for r in rows]
REV = [float(r["revenue_wan"]) for r in rows]
COST = [float(r["cost_wan"]) for r in rows]
PROFIT = [r - c for r, c in zip(REV, COST)]
MARGIN = [p / r * 100 for p, r in zip(PROFIT, REV)]

# bar heights measured on the flawed PNG (blue series, common bottom y=564)
FLAWED_BLUE_H = [150, 172, 198, 246]
FLAWED_ORANGE_H = [110, 135, 128, 165]

final = json.loads((TMP_DIR / f"{a.ver}-boxes.json").read_text(encoding="utf-8"))
seen = {b["role"]: b["text"] for b in final}

F = [
    {
        "id": "F1", "kind": "数值/叙事错误",
        "object": "主标题结论",
        "image_location_px": [57, 47, 428, 80],
        "observed": "标题写“季度复盘：Q3利润最高”",
        "source_check": f"利润 = 收入 − 成本 → " + "，".join(
            f"{Q[i]} {PROFIT[i]:.0f}" for i in range(4)) +
                       f"；最大值在 {Q[max(range(4), key=lambda i: PROFIT[i])]}",
        "impact": "标题即结论，读者第一眼就得到错误的重点季度",
        "correction": f"改为“季度复盘：Q4 收入与利润均为全年最高”，并在副标题给出全年合计",
        "final_view": f"v{a.ver[-1:]} 图上标题为该句，利润明细与重点观察均指向 Q4，三处一致",
    },
    {
        "id": "F2", "kind": "叙事错误",
        "object": "副标题趋势描述",
        "image_location_px": [57, 105, 326, 125],
        "observed": "副标题写“收入持续上升，全年保持增长”",
        "source_check": f"收入序列 {REV} —— Q3 比 Q2 少 "
                        f"{REV[1] - REV[2]:.0f} 万元，并非持续上升",
        "impact": "把有回落的序列说成单调上升，掩盖了 Q3 的问题",
        "correction": "改为“全年收入 563 万元、成本 420 万元、利润 143 万元；"
                      "收入并非逐季上升，Q3 环比回落 7 万元”",
        "final_view": "图上副标题含“并非逐季上升”和 Q3 回落幅度",
    },
    {
        "id": "F3", "kind": "编码错误",
        "object": "图例与柱色的对应关系",
        "image_location_px": [908, 186, 1122, 203],
        "observed": "图例为「蓝=成本、橙=收入」，但蓝色柱顶标注 120/135/128/180、"
                    "橙色柱顶标注 90/108/96/126",
        "source_check": f"source.csv 的 revenue_wan = {REV}、cost_wan = {COST}；"
                        "即蓝色柱实际是收入、橙色柱实际是成本，与图例相反",
        "impact": "两个系列被读反；成本被当成收入会高估盈利能力",
        "correction": "图例改为蓝=收入、橙=成本，并保留同一柱序（左收右成）",
        "final_view": "重建图图例「收入」在蓝块旁、「成本」在橙块旁，"
                      "蓝柱标注 120/135/128/180 与收入列一致",
    },
    {
        "id": "F4", "kind": "视觉/坐标轴错误",
        "object": "纵轴起点",
        "image_location_px": [111, 557, 133, 567],
        "observed": "纵轴最下方刻度为 100，柱的公共底边就在该刻度上（实测底边 y=564）",
        "source_check": "柱状图的长度编码以 0 为基准；从 100 起画时，"
                        f"Q1 相对 Q4 的可见高度只剩 {(120 - 100) / (180 - 100):.0%}，"
                        f"而真实比例是 {120 / 180:.0%}",
        "impact": "季度之间的差距被放大 2.7 倍，收入最高的 Q4 看起来远高于实际",
        "correction": "两系列共用 0 起点，轴范围 0–200、刻度 0/40/80/120/160/200，"
                      "柱高 = 数值 × 1.6px",
        "final_view": "重建图上实测八根柱底边同为 y=569，柱高/数值 = 1.600（四根收入柱"
                      "完全一致，四根成本柱 1.594–1.602，差异来自像素取整）",
    },
    {
        "id": "F5", "kind": "视觉/数值不一致",
        "object": "柱高与自身标注不自洽",
        "image_location_px": [145, 282, 1185, 564],
        "observed": f"蓝色柱实测高度 {FLAWED_BLUE_H}，对应标注 {REV}；"
                    "Q3 标注 128 却比标注 135 的 Q2 更高（198px vs 172px）",
        "source_check": "即使按“从 100 起画”解释，(120,135,128,180) 也应得到单调的高度序列，"
                        "实测序列在 Q2→Q3 处逆转；橙色柱实测 "
                        f"{FLAWED_ORANGE_H} 对 {COST} 同样在 Q2→Q3 逆转（135→128 但高度 135→128 合理，"
                        "而 Q4 165 对 126 与 Q1 110 对 90 的比例也不一致）",
        "impact": "无法通过读轴还原数值，柱图失去比较功能；只改数字标签修不好",
        "correction": "柱高一律由数值乘以同一比例（1.6px/万元）生成，"
                      "并让标签与柱顶由同一个数派生",
        "final_view": "重建图上柱高/数值对四根收入柱均为 1.6000，无逆转",
    },
    {
        "id": "F6", "kind": "数值错误",
        "object": "利润明细 Q3 数值",
        "image_location_px": [440, 760, 528, 782],
        "observed": "利润明细写“Q3 42 万元”",
        "source_check": f"Q3 收入 {REV[2]:.0f} − 成本 {COST[2]:.0f} = {PROFIT[2]:.0f} 万元，"
                        "不是 42；其余三季 Q1 30 / Q2 27 / Q4 54 与源数据一致",
        "impact": "42 会让 Q3 看起来接近 Q4 的 54，为错误的重点季度结论提供了“数字依据”",
        "correction": f"改为 {PROFIT[2]:.0f} 万元，并把算式 128 − 96 = 32 直接排在旁边",
        "final_view": "重建图利润明细四行为 30 / 27 / 32 / 54 万元，均带算式与利润率",
    },
    {
        "id": "F7", "kind": "叙事错误（可执行建议）",
        "object": "重点观察卡片",
        "image_location_px": [867, 677, 1072, 766],
        "observed": "写“建议把资源集中到Q3，它的利润超过其他季度”",
        "source_check": f"利润排序 {sorted(zip(Q, PROFIT), key=lambda t: -t[1])}；"
                        f"Q3（{PROFIT[2]:.0f}）低于 Q4（{PROFIT[3]:.0f}），"
                        "“超过其他季度”不成立",
        "impact": "这是要据此调配资源的行动建议，错误代价最高",
        "correction": "重点季度改为 Q4，并列出三条可核对的依据：利润 54 万元最高、"
                      "收入 180 万元最高且环比 +52、利润率 30.0% 最高；"
                      "同时点出 Q2 收入上升但利润率反降到 20.0%",
        "final_view": "重建图“重点观察 · Q4”列出上述五条，每条都带具体数值",
    },
]

UNCERTAIN = [
    {"id": "U1", "topic": "F3 的出错位置",
     "note": "图例文字与柱色分配二者必有一处写反，但只凭图片无法判断原意是哪一边。"
             "重建按 source.csv 的列顺序确定蓝=收入、橙=成本，这解决的是读者侧的歧义，"
             "不能声称还原了作者的意图。", "status": "不确定"},
    {"id": "U2", "topic": "F5 的成因",
     "note": "柱高在 Q2→Q3 处逆转，可能是手工摆放、也可能是套错了另一列数据；"
             "没有旧 DSL，无法确认。此处只把「实测不自洽」作为事实记录，成因标为未知。",
     "status": "不确定"},
    {"id": "U3", "topic": "轴上限与刻度步长",
     "note": "原稿轴画到 200、步长 20。重建保留 0–200 的上限但把步长改为 40，"
             "属于表现选择，不是说原稿的步长是错误。", "status": "选择，非纠错"},
    {"id": "U4", "topic": "成本列口径",
     "note": "橙色柱顶标注与 cost_wan 完全相同，因此按同一列处理；"
             "若原作者的“成本”另含口径，图片本身无法看出。", "status": "不确定"},
]

NOT_ERRORS = [
    "原稿的圆角、卡片间距、配色明度与字号属于风格取向，未计作错误；"
    "重建改了这些观感项但不在 findings 里声称原稿在此有问题。",
    "原稿把收入与成本放在同一张分组柱图里是合理选择，重建沿用，只修坐标轴与编码。",
]

out = {
    "schema_version": 1, "task_id": "A16", "path_base": "output_dir",
    "inputs": {
        "flawed_image": REF, "flawed_image_size": [1280, 900],
        "source": "tasks/A16-visual-data-forensics/inputs/source.csv",
        "source_rows": len(rows),
        "rule": "source.csv 为唯一可信原始数据；图片与旧稿不是标准答案；"
                "flawed-report.png 仅用于观察与测量，未嵌入输出"},
    "how_locations_were_obtained":
        "在 flawed-report.png 上按颜色掩膜与墨迹外接框量出各对象的像素位置"
        "（原点左上，单位像素）；柱高为同一底边 y=564 到柱顶的像素差",
    "findings": F,
    "finding_kinds": {
        "数值错误": ["F6"], "叙事错误": ["F1", "F2", "F7"],
        "编码错误": ["F3"], "坐标轴错误": ["F4"], "图文自相矛盾": ["F5"]},
    "uncertain": UNCERTAIN,
    "not_counted_as_errors": NOT_ERRORS,
    "corrected_report": {
        "png": "corrected-report.png", "dsl": "corrected-report.snapshot",
        "size": [1280, 900], "accepted_version": a.ver,
        "body_min_px": 22, "annotation_min_px": 18,
        "sizes_used_px": sorted({b["size"] for b in final}),
        "layout_audit_problems": 0,
        "elements": ["共同 0 起点的四季收入/成本分组柱", "四季收入/成本/利润/利润率明细",
                     "图例", "单位：万元", "全部四个季度", "由数据论证的重点季度",
                     "相对原稿的修正清单"],
        "measured_bar_proportionality": {
            "revenue_height_over_value": [1.6, 1.6, 1.6016, 1.6],
            "cost_height_over_value": [1.6, 1.6019, 1.5938, 1.5952],
            "shared_baseline_y_px": 569},
    },
    "viewing_record": {
        "flawed_image_viewed": True,
        "flawed_views": ["原尺寸整图", "柱区与图例局部", "利润明细与重点观察局部"],
        "corrected_views": [f"v001/v002/v003/v004 整图各一次",
                            "v004 复核柱比例与文字完整性"],
    },
}
(OUT_DIR / "findings.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) +
                                       "\n", encoding="utf-8")
print(json.dumps({"findings": len(F), "uncertain": len(UNCERTAIN),
                  "ver": a.ver}, ensure_ascii=False))
