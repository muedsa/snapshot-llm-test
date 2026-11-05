#!/usr/bin/env python3
"""A16 - rebuild a trustworthy quarterly report from source.csv.

The flawed-report.png is used for observation/diagnosis only; it is never embedded.
Every value is computed from inputs/source.csv (the only trusted data source).
"""
import csv, json, os, sys
from pathlib import Path

TOOLS = os.environ["TOOLS"]
sys.path.insert(0, TOOLS)
from dsl import Canvas, CN, LATIN
import suite

TASK = "A16"
ROOT = suite.ROOT
SRC = ROOT / "tasks" / "A16-visual-data-forensics" / "inputs" / "source.csv"
rows = list(csv.DictReader(SRC.read_text(encoding="utf-8").splitlines()))
Q = []
for r in rows:
    rev = int(r["revenue_wan"]); cost = int(r["cost_wan"])
    Q.append({"quarter": r["quarter"], "revenue_wan": rev, "cost_wan": cost,
              "profit_wan": rev - cost})

TOTAL_REV = sum(q["revenue_wan"] for q in Q)
TOTAL_COST = sum(q["cost_wan"] for q in Q)
TOTAL_PROFIT = sum(q["profit_wan"] for q in Q)
BEST = max(Q, key=lambda q: q["profit_wan"])
WORST = min(Q, key=lambda q: q["profit_wan"])
Q3, Q2, Q4 = Q[2], Q[1], Q[3]

# ------------------------------------------------------------------ palette
BG = "#F5F7FA"; WHITE = "#FFFFFF"; CARD = "#FFFFFF"
INK = "#18283F"; MUTED = "#64748B"; SUBTLE = "#7B8BA3"
BLUE = "#245CE4"; ORANGE = "#F28C28"; GRID = "#E4E9F0"; LINE = "#E6EBF2"
GREEN = "#198369"; FOCUSBG = "#EAF2FF"; FOCUSLINE = "#C9DEFF"
ERRBG = "#FFF6E8"; ERRLINE = "#F6D9A8"; ERRINK = "#8A5A12"
HIGHLIGHT = "#FFF1D6"
BORDER = "1 SOLID " + LINE

# ------------------------------------------------------------------ chart geometry
PLOT_L, PLOT_R = 110, 1200
TOP_Y, ZERO_Y = 250, 500
VMAX = 200
SCALE = (ZERO_Y - TOP_Y) / VMAX          # 1.25 px per 万元
TICKS = [0, 40, 80, 120, 160, 200]
GROUP_W = (PLOT_R - PLOT_L) / 4
BAR_W = 52

c = Canvas(1280, 900, BG, font=CN)

# ================================================================== HEADER
c.text(48, 34, 1184, 58,
       "季度复盘 · Q4 收入与利润均创新高", 40, INK, bold=True)
c.text(48, 98, 1184, 36,
       "依据 source.csv 重制 · 单位：万元 · 四季收入/成本共用零起点 · 柱高对应真实数值",
       22, MUTED)
c.rect(48, 140, 1184, 3, BLUE)

# ================================================================== MAIN CHART CARD
c.rect(48, 158, 1184, 427, CARD, radius=16, border=BORDER)
c.text(72, 172, 520, 38, "收入与成本对比 · Q1–Q4", 26, INK, bold=True)
c.text(72, 212, 240, 26, "单位：万元", 18, MUTED)
# legend (colors correctly bound to the series this time)
c.rect(950, 180, 20, 20, BLUE, radius=4)
c.text(976, 176, 80, 28, "收入", 20, INK)
c.rect(1072, 180, 20, 20, ORANGE, radius=4)
c.text(1098, 176, 80, 28, "成本", 20, INK)
# grid lines + y ticks, common zero baseline
for v in TICKS:
    gy = ZERO_Y - v * SCALE
    c.hline(PLOT_L, gy, PLOT_R - PLOT_L, 1, GRID)
    c.text(58, gy - 15, 46, 30, str(v), 18, SUBTLE, align="RIGHT", font=LATIN)
c.hline(PLOT_L, ZERO_Y, PLOT_R - PLOT_L, 2, "#94A3B8")   # emphasised zero line
# grouped bars
for i, q in enumerate(Q):
    cx = PLOT_L + GROUP_W * i + GROUP_W / 2
    rx = cx - 58
    ox = cx + 6
    hr = q["revenue_wan"] * SCALE
    hc = q["cost_wan"] * SCALE
    c.add(rx, ZERO_Y - hr, BAR_W, hr,
          '<Container color="%s" borderRadiusTopLeft="4" borderRadiusTopRight="4" />' % BLUE)
    c.add(ox, ZERO_Y - hc, BAR_W, hc,
          '<Container color="%s" borderRadiusTopLeft="4" borderRadiusTopRight="4" />' % ORANGE)
    c.text(rx - 8, ZERO_Y - hr - 28, BAR_W + 16, 26, str(q["revenue_wan"]), 18,
           BLUE, bold=True, align="CENTER", font=LATIN)
    c.text(ox - 8, ZERO_Y - hc - 28, BAR_W + 16, 26, str(q["cost_wan"]), 18,
           "#B4650A", bold=True, align="CENTER", font=LATIN)
    c.text(cx - 60, 510, 120, 30, q["quarter"], 20, INK, bold=True,
           align="CENTER", font=LATIN)
c.text(72, 548, 1100, 28,
       "共同零起点 0 → 200 万元；每组左柱为收入、右柱为成本；Q4 收入 180 与成本 126 均为全年最高。",
       22, MUTED)

# ================================================================== PROFIT DETAIL CARD
c.rect(48, 600, 592, 160, CARD, radius=16, border=BORDER)
c.text(72, 614, 500, 36, "利润明细 · 收入 − 成本", 26, INK, bold=True)
for i, q in enumerate(Q):
    x = 72 + i * 130
    if q["quarter"] == "Q4":
        c.rect(x - 8, 656, 124, 92, HIGHLIGHT, radius=10)
    c.text(x, 662, 120, 28, q["quarter"], 20, MUTED, bold=True, font=LATIN)
    c.text(x, 690, 120, 40, "%d 万元" % q["profit_wan"], 26, INK, bold=True)
    c.bar(x, 738, q["profit_wan"] / 54 * 108, 8,
          BLUE if q["quarter"] == "Q4" else "#B9C6D8", radius=4)

# ================================================================== FOCUS CARD
c.rect(656, 600, 576, 160, FOCUSBG, radius=16, border="1 SOLID " + FOCUSLINE)
c.text(680, 610, 520, 36, "重点季度 · Q4", 26, BLUE, bold=True)
c.text(680, 650, 528, 32, "Q4 收入 180 万元、利润 54 万元，均为四季最高。", 22, INK)
c.text(680, 686, 528, 32, "利润较 Q3 的 32 万元增加 22 万元。", 22, INK)
c.text(680, 722, 528, 32, "Q3 收入 128 万较 Q2 的 135 万回落 7 万。", 22, MUTED)

# ================================================================== ERRATA STRIP
c.rect(48, 775, 1184, 108, ERRBG, radius=14, border="1 SOLID " + ERRLINE)
c.text(68, 783, 500, 30, "原图勘误（与 source.csv 逐项核对）", 22, ERRINK, bold=True)
c.text(68, 815, 1140, 26,
       "① 标题与重点结论误称「Q3 利润最高」：实际 Q4 利润 54 万最高、Q3 仅 32 万；② 图例颜色与系列对调；",
       20, ERRINK)
c.text(68, 841, 1140, 26,
       "③ Y 轴自 100 万截断而非零起点；④ 柱高与数值不符且 Q3 蓝柱逆势高于 Q2；",
       20, ERRINK)
c.text(68, 867, 1140, 26,
       "⑤ 利润明细 Q3 误写 42 万（应为 32 万）；⑥「收入持续上升」与 Q3 回落矛盾。",
       20, ERRINK)

# ================================================================== OUTPUTS
dsl = c.render()
out = suite.out_dir(TASK)
(out / "corrected-report.snapshot").write_text(dsl, encoding="utf-8")
ver = os.environ.get("BUILD_VERSION", "v1")
tmp = suite.tmp_dir(TASK, ver)
(tmp / "corrected-report.snapshot").write_text(dsl, encoding="utf-8")

# ------------------------------------------------------------------ corrected-data.json
profit_sum = sum(q["profit_wan"] for q in Q)
axes = {
    "unit": "万元 (10k CNY)", "zero_line_px": ZERO_Y, "vmin": 0, "vmax": VMAX,
    "pixel_mapping": "y = 500 - value * (500-250)/200 = 500 - value * 1.25",
    "scale_px_per_wan": SCALE, "ticks": TICKS,
    "grid_line_px": [ZERO_Y - v * SCALE for v in TICKS],
    "shared_zero_baseline": True,
    "group_centers_px": [PLOT_L + GROUP_W * i + GROUP_W / 2 for i in range(4)],
    "bar_width_px": BAR_W,
    "bars": [
        {"quarter": q["quarter"], "series": "revenue", "value_wan": q["revenue_wan"],
         "x_px": round(PLOT_L + GROUP_W * i + GROUP_W / 2 - 58, 2),
         "top_px": round(ZERO_Y - q["revenue_wan"] * SCALE, 2),
         "height_px": round(q["revenue_wan"] * SCALE, 2), "color": BLUE}
        for i, q in enumerate(Q)
    ] + [
        {"quarter": q["quarter"], "series": "cost", "value_wan": q["cost_wan"],
         "x_px": round(PLOT_L + GROUP_W * i + GROUP_W / 2 + 6, 2),
         "top_px": round(ZERO_Y - q["cost_wan"] * SCALE, 2),
         "height_px": round(q["cost_wan"] * SCALE, 2), "color": ORANGE}
        for i, q in enumerate(Q)
    ],
}
conclusion = {
    "headline": "季度复盘 · Q4 收入与利润均创新高",
    "focus_quarter": "Q4",
    "text": "Q4 收入 180 万元、利润 54 万元均为四季最高；利润较 Q3 的 32 万元增加 22 万元。Q3 收入 128 万元较 Q2 的 135 万元回落 7 万元，增长并非连续。",
    "referenced_fields": ["quarters[3].revenue_wan", "quarters[3].profit_wan",
                          "quarters[2].profit_wan", "quarters[2].revenue_wan",
                          "quarters[1].revenue_wan"],
    "values": {"total_revenue_wan": TOTAL_REV, "total_cost_wan": TOTAL_COST,
               "total_profit_wan": TOTAL_PROFIT,
               "best_profit_quarter": BEST["quarter"], "best_profit_wan": BEST["profit_wan"],
               "worst_profit_quarter": WORST["quarter"], "worst_profit_wan": WORST["profit_wan"],
               "q4_vs_q3_profit_delta_wan": Q4["profit_wan"] - Q3["profit_wan"],
               "q3_vs_q2_revenue_delta_wan": Q3["revenue_wan"] - Q2["revenue_wan"]},
}
corrected = {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "source": "inputs/source.csv (only trusted data)",
    "quarters": [{"quarter": q["quarter"], "revenue_wan": q["revenue_wan"],
                  "cost_wan": q["cost_wan"], "profit_wan": q["profit_wan"]} for q in Q],
    "axes": axes, "conclusion": conclusion,
    "evidence": {"png": "corrected-report.png", "dsl": "corrected-report.snapshot",
                 "checks": ["profit = revenue - cost", "all 8 bar heights = value * 1.25",
                            "shared zero baseline y=500", "legend color bound to correct series"]},
}
(out / "corrected-data.json").write_text(
    json.dumps(corrected, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# ------------------------------------------------------------------ findings.json
def finding(fid, loc, phenom, cat, check, impact, fix, view):
    return {"id": fid, "image_location": loc, "phenomenon": phenom,
            "category": cat, "source_data_check": check, "impact": impact,
            "correction": fix, "final_view_result": view}

findings = [
    finding("F01", "标题 x≈57,y≈40–80：「季度复盘：Q3利润最高」",
            "标题断言 Q3 利润为四季最高。", "叙事/数值",
            "source.csv 利润：Q1 30、Q2 27、Q3 32、Q4 54（万元）。最高是 Q4，Q3 仅第三。",
            "误导读者把资源投向 Q3；与重点观察卡、利润明细自相矛盾。",
            "标题改为「季度复盘 · Q4 收入与利润均创新高」，由 Q4 利润 54 与收入 180 论证。",
            "待看图确认"),
    finding("F02", "副标题 x≈57,y≈100–125：「收入持续上升，全年保持增长」",
            "声称收入全年连续增长。", "叙事/数值",
            "收入序列 120→135→128→180；Q3 较 Q2 回落 7 万元。",
            "掩盖 Q3 的回落，造成趋势误判。",
            "在重点卡明确写出「Q3 收入 128 万较 Q2 的 135 万回落 7 万，增长并非连续」。",
            "待看图确认"),
    finding("F03", "图例 x≈875–1150,y≈175–200：蓝=成本、橙=收入",
            "图例颜色与柱子所代表的系列对调。", "图例/数值",
            "蓝柱标注 120/135/128/180 恰为 source.csv 收入；橙柱 90/108/96/126 恰为成本。",
            "读者会把收入读成成本、成本读成收入，利润关系被颠倒。",
            "图例改为蓝=收入、橙=成本，并在柱顶分别标注真实收入/成本数值。",
            "待看图确认"),
    finding("F04", "Y 轴 x≈110–175,y≈230–565：刻度 100/120/140/160/180/200，柱底在 100 线",
            "纵轴从 100 万元截断，未从 0 起；柱底落在 y=565 的 100 线。", "坐标轴/视觉误导",
            "实测网格线 y=295/349/403/457/511/565 间隔 54px=20 万元（2.7px/万元），最下方为 100；柱底 y=564。",
            "夸大季度波动与收入/成本差距，是小基数差异的视觉放大。",
            "重制为 0–200 万元共同零起点，零线 y=500，柱高 = 数值 × 1.25px。",
            "待看图确认"),
    finding("F05", "蓝柱 x≈224/460/696/932,y≈319–564；橙柱 x≈300/536/772/1008",
            "柱高与数字标签及真实数据不符：蓝柱高度 150/172/198/246px 单调递增，Q3 反而高于 Q2。", "几何/数值",
            "真实收入 Q2=135 > Q3=128，Q3 柱应更矮；按 2.7px/万元 反推柱高也不对应其标签值。",
            "图形传达的趋势（Q3 继续上升）与数据（Q3 回落）相反。",
            "全部 8 根柱按真实数值 × 1.25px 重画，Q3 收入 160px < Q2 收入 168.75px。",
            "待看图确认"),
    finding("F06", "利润明细 x≈440–540,y≈740–790：Q3 显示「42 万元」",
            "Q3 利润数值错误。", "数值",
            "Q3 利润 = 128 − 96 = 32 万元；Q1 30、Q2 27、Q4 54 均正确。",
            "虚增 Q3 利润 10 万元，直接支撑了错误的「Q3 利润最高」叙事。",
            "利润明细改为 30 / 27 / 32 / 54 万元，Q4 高亮。",
            "待看图确认"),
    finding("F07", "重点观察卡 x≈845–1225,y≈645–820：「建议把资源集中到Q3，它的利润超过其他季度」",
            "重点季度与建议缺乏数据依据。", "叙事/数值",
            "即使按原图 42 万，Q4 的 54 万仍更高；真实 Q3 仅 32 万，Q4=54 为最高。",
            "把决策资源导向利润第三的季度。",
            "重点卡改为 Q4，附「收入 180、利润 54 均最高，较 Q3 增加 22 万」的数据论证。",
            "待看图确认"),
]
uncertainties = [
    {"item": "图例位置、卡片底色与字体选择属于审美偏好",
     "reason": "题面允许风格改进，无法仅凭图片判定为数值或叙事错误",
     "evidence_needed": "原设计稿意图说明；本次不列入 findings 正文"},
    {"item": "页脚「虚构数据 · 同事初稿，仅供诊断」",
     "reason": "属稿件状态标注，不是经营结论，不构成数据错误",
     "evidence_needed": "无；仅记录为不确定项"},
    {"item": "蓝/橙柱顶部数字标签本身 120/135/128/180 与 90/108/96/126",
     "reason": "数值与 source.csv 一致，只是所属系列（颜色）被对调；不单独判为数值错",
     "evidence_needed": "与 F03 合并处理"},
]
fdoc = {"schema_version": 1, "task_id": TASK, "path_base": "output_dir",
        "image_size": [1280, 900], "source": "inputs/source.csv",
        "findings": findings, "uncertainties": uncertainties}
(out / "findings.json").write_text(
    json.dumps(fdoc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("A16 DSL bytes", len(dsl.encode("utf-8")), "| version", ver,
      "| quarters", [(q["quarter"], q["profit_wan"]) for q in Q],
      "| findings", len(findings))
