# -*- coding: utf-8 -*-
"""A16 收尾：findings.json、corrected-data.json、iterations.jsonl、complete-payload。"""
import io, sys, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
OUT = os.path.join(ROOT, "outputs", "20261016T164020-m1", "A16")
STEPS = os.path.join(ROOT, "tmp", "20261016T164020-m1", "A16", "steps")

def ev(n):
    return {"path_base": "suite_root", "path": "tmp/20261016T164020-m1/A16/steps/" + n}

def outp(n):
    return {"path_base": "output_dir", "path": n}

V = "最终查看：corrected-report.png 已整体查看（17:28）并放大核验图卡上左/双柱区/明细卡/关注卡："

findings = [
    {"id": "F1", "category": "叙事/数值", "severity": "high",
     "location": {"box_px": [57, 47, 428, 79], "note": "标题字形框（原图）"},
     "phenomenon": "标题“季度复盘：Q3利润最高”断言 Q3 为利润最高季度。",
     "source_check": "source.csv 利润 = 收入−成本：Q1 30 / Q2 27 / Q3 32 / Q4 54 万元，Q4 最高；按图自带的明细卡（Q4 54>Q3 42）亦自相矛盾。",
     "impact": "主结论指向错误季度，直接误导经营的“重点复盘”方向。",
     "fix": "标题改为数据可支撑结论：“季度复盘：Q4 利润 54 万元领先全年”（Q4 利润与收入同为全年最高）。",
     "final_view": V + "标题已替换为 Q4 结论，与明细/柱图一致。",
     "evidence": [ev("flaw-head.png"), ev("flaw-scan2.json")]},
    {"id": "F2", "category": "数值", "severity": "high",
     "location": {"box_px": [440, 755, 525, 790], "note": "明细卡 Q3 数值单元（原图 y771 行 runs 定位）"},
     "phenomenon": "利润明细 Q3 显示“42 万元”。",
     "source_check": "128−96 = 32；明细中 30/27/54 三项核算正确，仅 Q3 不符。",
     "impact": "Q3 利润虚增 10 万元；叠加 F1 使“Q3 最好”的假象更强。",
     "fix": "重制图明细按原始数据重算：Q3 = 32 万元。",
     "final_view": V + "利润明细卡四列 30/27/32/54，Q4 附环比章。",
     "evidence": [ev("flaw-detail.png"), ev("flaw-scan2.json")]},
    {"id": "F3", "category": "视觉映射", "severity": "high",
     "location": {"box_px": [877, 186, 1122, 207], "note": "图例区：蓝块 [877,186,896,206]+“成本”，橙块 [1056,186,1075,206]+“收入”"},
     "phenomenon": "图例标注蓝＝成本、橙＝收入。",
     "source_check": "图中蓝色柱承载收入值（120/135/128/180）、橙色柱承载成本值（90/108/96/126），图例与柱色互换。",
     "impact": "成本峰被读成收入峰（Q4 橙柱 126 易被误作收入），对比结论全部跟着错。",
     "fix": "重制图图例：收入＝蓝在前、成本＝橙在后，与柱色一致。",
     "final_view": V + "图例为收入(蓝)/成本(橙)，与柱色一致。",
     "evidence": [ev("flaw-legend.png"), ev("flaw-scan2.json")]},
    {"id": "F4", "category": "视觉/几何", "severity": "high",
     "location": {"box_px": [60, 236, 141, 567], "note": "y 轴刻度标签区；柱底=基线 y≈564，底刻度“100”带中心 y≈563.5"},
     "phenomenon": "y 轴刻度只有 100..200（6 档均匀，间隔 54px ≈ 2.71px/万元），无 0 刻度；柱底画在 100 刻度线上。",
     "source_check": "数据最低值——Q1 成本 90 —— 低于轴下限 100，在图上无法成立；共同零起点缺失。",
     "impact": "截断基线放大柱间差异（尤其收入对比与利润视觉），属标准“轴零点截断”误导。",
     "fix": "重制图共同零起点：0..200、50 步距均匀刻度（1.2px/万元），柱高含自零点的全部高度。",
     "final_view": V + "y 轴 0/50/100/150/200 均匀，柱底与 0 线对齐。",
     "evidence": [ev("flaw-scan.json"), ev("flaw-qtr.png")]},
    {"id": "F5", "category": "数值/几何", "severity": "high",
     "location": {"box_px": [224, 293, 1071, 565], "note": "8 根柱区域（蓝柱列心 255/491/727/963，橙柱 331/567/803/1039）"},
     "phenomenon": "柱高与轴/数据均不符：按 2.71px/万元折算，蓝柱顶隐含值 154.7/162.8/172.4/190.1（标签 120/135/128/180），橙柱 140.0/149.2/146.6/160.2（标签 90/108/96/126）；高宽比蓝 1.24~1.54、橙 1.21~1.32，不存在统一线性刻度；Q2→Q3 收入下降（135→128）被画成柱高上升（171→197px）。",
     "source_check": "source.csv 数值唯一可信。",
     "impact": "全年节奏失真（唯一回落季度呈上升），季度对比比例最大偏差约 24%。",
     "fix": "柱高 = 数值 × 1.2px/万元；顶圆角、底对 0 线。",
     "final_view": V + "重测 8 柱：隐含值与数据差 ≤0.5（子像素），实现 (512−top)/1.2 == 数值。",
     "evidence": [ev("flaw-scan.json"), outp("corrected-report.png")]},
    {"id": "F6", "category": "叙事/数值", "severity": "medium",
     "location": {"box_px": [57, 80, 425, 117], "note": "副标题字形框（原图）"},
     "phenomenon": "副标题“收入持续上升，全年保持增长”。",
     "source_check": "收入 120→135→128→180：Q3 环比 −5.18%（约 −5.2%），为全年唯一下降，与“持续上升”不符。",
     "impact": "掩盖 Q3 回落这一关键节奏信息。",
     "fix": "副标题改含数字：“全年利润 143 万元；Q3 收入环比 −5.2%，Q4 重回 180 万元新高”。",
     "final_view": V + "副标题与数据一致。",
     "evidence": [ev("flaw-head.png")]},
    {"id": "F7", "category": "叙事/数值", "severity": "high",
     "location": {"box_px": [843, 650, 1224, 821], "text_bbox": [867, 677, 1072, 765]},
     "phenomenon": "重点观察卡：“建议把资源集中到Q3，它的利润超过其他季度。”",
     "source_check": "Q3 利润 32 万元低于 Q4 的 54 万元；且该卡自身引用的 Q3 明细（42）也是错的（见 F2）——即使按 42，Q4 54 仍最高；资源配置建议无任何数据支撑。",
     "impact": "错误概括叠加错误数值，对季度资源决策形成双重误导。",
     "fix": "重点观察改为 Q4 并以数据论证：利润 54 万元、利润率 30% 均为全年最高；环比 +22 万元（+68.8%）由明细卡章节呈现；注明 Q3 收入为全年唯一下降（−5.2%）。",
     "final_view": V + "重点观察卡改为 Q4 数据论证版。",
     "evidence": [ev("flaw-focus.png")]},
]
uncertainties = [
    {"id": "U1", "subject": "原图零点截断是否“有意聚焦区间”",
     "note": "无法从图片确认截断动机；无论动机如何，共同零起点是本题重制要求，按标准修复。此为推断，不影响 F4 维持。"},
    {"id": "U2", "subject": "非数值风格项",
     "note": "柱圆角/间距、卡配色、字号节奏等属于审美偏好，任务允许风格改进，未列为数值错误；重制中同族配色微调（ax 标签灰阶统一）。"},
    {"id": "U3", "subject": "原页脚文案的主题延续",
     "note": "“虚构数据 · 同事初稿，仅供诊断”为合理免责文案，原样保留（[56,858,275,873]）。"},
]
findings_doc = {
    "schema_version": 1, "task_id": "A16", "path_base": "output_dir",
    "inputs_checked": [{"path_base": "task_input", "path": "flawed-report.png", "size": [1280, 900]},
                       {"path_base": "task_input", "path": "source.csv"}],
    "findings": findings, "uncertainties": uncertainties,
    "count": {"findings": len(findings), "uncertainties": len(uncertainties)},
}

Q = [
    {"quarter": "Q1", "revenue_wan": 120, "cost_wan": 90, "profit_wan": 30,
     "profit_margin_pct": 25.0, "rev_qoq_pct": None},
    {"quarter": "Q2", "revenue_wan": 135, "cost_wan": 108, "profit_wan": 27,
     "profit_margin_pct": 20.0, "rev_qoq_pct": 12.5},
    {"quarter": "Q3", "revenue_wan": 128, "cost_wan": 96, "profit_wan": 32,
     "profit_margin_pct": 25.0, "rev_qoq_pct": -5.185},
    {"quarter": "Q4", "revenue_wan": 180, "cost_wan": 126, "profit_wan": 54,
     "profit_margin_pct": 30.0, "rev_qoq_pct": 40.625},
]
centers = [276.25, 528.75, 781.25, 1033.75]
bars = []
for i, row in enumerate(Q):
    c = centers[i]
    bars.append({
        "quarter": row["quarter"],
        "revenue": {"x": c - 71, "top_y": 512 - row["revenue_wan"] * 1.2, "height_px": row["revenue_wan"] * 1.2},
        "cost": {"x": c + 7, "top_y": 512 - row["cost_wan"] * 1.2, "height_px": row["cost_wan"] * 1.2}})
data_doc = {
    "schema_version": 1, "task_id": "A16", "path_base": "output_dir",
    "source": {"path_base": "task_input", "path": "source.csv",
               "note": "收入/成本列原值；利润=收入−成本（万元）"},
    "artifacts": {"image": {"path_base": "output_dir", "path": "corrected-report.png"},
                  "dsl": {"path_base": "output_dir", "path": "corrected-report.snapshot"}},
    "quarters": Q,
    "totals": {"profit_sum_wan": 143, "revenue_sum_wan": 563, "cost_sum_wan": 420},
    "axes": {
        "common_zero": True, "unit": "万元",
        "canvas": [1280, 900],
        "plot_x": [150, 1160], "baseline_y": 512, "top_y": 272,
        "value_min_wan": 0, "value_max_wan": 200, "tick_step_wan": 50,
        "pixels_per_wan": 1.2, "tick_ys": {"0": 512, "50": 452, "100": 392, "150": 332, "200": 272},
        "axis_label_right_x": 138,
        "bar_w": 64, "bar_gap": 14, "group_centers": centers,
        "bars": bars,
        "note": "柱高=数值×1.2（端点含子像素圆整，实际渲染反算差 ≤0.5px）"},
    "conclusion": {
        "headline": "季度复盘：Q4 利润 54 万元领先全年",
        "subtitle": "全年利润 143 万元；Q3 收入环比 −5.2%，Q4 重回 180 万元新高",
        "focus_quarter": "Q4",
        "body": "利润 54 万元、利润率 30%，均为全年最高；Q3 收入为全年唯一下降（−5.2%），Q4 反弹至 180 万元。",
        "supporting_numbers": [
            {"claim": "Q4 利润全年最高", "value": "54 万元（Q4）; 30/27/32（其余三季）", "source": "quarters.profit_wan"},
            {"claim": "Q4 利润率全年最高", "value": "30%（Q4）; 25/20/25", "source": "quarters.profit_margin_pct"},
            {"claim": "Q3 唯一收入环比下降", "value": "−5.185%（Q3）; +12.5%/+40.625%", "source": "quarters.rev_qoq_pct"},
            {"claim": "Q4 环比利润增量", "value": "+22 万元（+68.8%）", "source": "profit_wan[Q4]−profit_wan[Q3]"}]}
}

json.dump(findings_doc, open(os.path.join(OUT, "findings.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(data_doc, open(os.path.join(OUT, "corrected-data.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

ITER = [
    {"id": "A16-v01", "type": "baseline",
     "image": "corrected-report.png", "request_id": "fd728960-02c6-4b45-8f51-20253eeea5f8",
     "viewed_at": "2026-10-17T17:28:30+08:00",
     "images": ["steps/v01.png", "steps/chk-top.png", "steps/chk-bars34.png", "steps/chk-detail.png", "steps/chk-focus.png"],
     "observable_issues": [
         "初版即满足：共同零起点、均匀轴、柱高=1.2px/万元、图例映射正确、Q3=32、Q4 数据论证卡、正文≥22/标注≥18"],
     "changes": [], "recheck": "8 柱反算 (512−top)/1.2 与数值差 ≤0.5；四区域放大通过", "final": True, "seq": 1},
    {"id": "A16-meas", "type": "alternative", "subject": "原图取证扫描×2 + 证据裁剪×7（无修改渲染）",
     "viewed_at": "2026-10-17T17:15:00+08:00",
     "images": ["steps/flaw-legend.png", "steps/flaw-head.png", "steps/flaw-detail.png", "steps/flaw-focus.png", "steps/flaw-foot.png", "steps/flaw-qtr.png"],
     "changes": ["刻度实测 2.71px/万元均匀（推翻早先目测的“非均匀刻度”假设）；图例/明细/标题/关注卡逐项定位"], "seq": 2},
]
with open(os.path.join(ROOT, "tmp", "20261016T164020-m1", "A16", "iterations.jsonl"), "w", encoding="utf-8") as f:
    for r in ITER:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

pay = {
    "artifacts": ["corrected-report.png", "corrected-report.snapshot", "findings.json", "corrected-data.json", "snapshot-usage.md", "task-metrics.json"],
    "evidence": [
        "7 项问题（标题断言/明细 Q3=42/图例互换/零点截断/柱高失真/副标题断言/重点卡建议）全部带原图坐标与 source.csv 核对；3 项不确定项如实分列",
        "重制：共同零点 0–200 轴、柱高=1.2px/万元（反算差≤0.5px）、图例 收入=蓝、明细 30/27/32/54、Q4 数据论证卡、正文≥22/标注≥18",
        "v01 全图 + 4 区域放大查看；8 柱数值反算通过"],
    "summary": "A16 完成：错误经营图诊断复原——7 问题修复、可信叙事重建（1280×900）。"}
open(os.path.join(ROOT, "tmp", "20261016T164020-m1", "A16", "complete-payload.json"), "w", encoding="utf-8").write(json.dumps(pay, ensure_ascii=False, indent=1))
print("findings/corrected-data/iterations/payload ok")
