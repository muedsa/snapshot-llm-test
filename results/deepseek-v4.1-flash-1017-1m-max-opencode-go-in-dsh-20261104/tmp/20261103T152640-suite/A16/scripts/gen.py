# -*- coding: utf-8 -*-
"""A16: corrected quarterly report (1280x900) + findings."""
from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import dslkit as K  # noqa: E402
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "A16"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
OUT.mkdir(parents=True, exist_ok=True)
clock = rep.TaskClock(TASK)

rows = list(csv.DictReader((SUITE_ROOT / "tasks" / "A16-visual-data-forensics" / "inputs"
                            / "source.csv").read_text(encoding="utf-8").splitlines()))
data = []
for r in rows:
    rev, cost = int(r["revenue_wan"]), int(r["cost_wan"])
    data.append({"quarter": r["quarter"], "revenue": rev, "cost": cost,
                 "profit": rev - cost, "margin": round((rev - cost) / rev * 100, 1)})
tot_rev = sum(d["revenue"] for d in data)
tot_cost = sum(d["cost"] for d in data)
tot_profit = tot_rev - tot_cost
best = max(data, key=lambda d: d["profit"])
print(data, tot_rev, tot_cost, tot_profit, best)

BG = "#F7F7F4"
CARD = "#FFFFFF"
INK = "#12161C"
INK2 = "#3A4453"
MUTED = "#6B7686"
REV = "#2563EB"
COST = "#E8890C"
PROFIT = "#0F7A5A"
LINE = "#E3E5E1"
FONT = "Inter,Noto Sans CJK SC"
W, H = 1280, 900

p: list[str] = []
p.append(K.rect(0, 0, W, H, color=BG))
p.append(K.rect(0, 0, W, 6, color=REV))
p.append(K.text(48, 30, f"季度复盘：Q4 利润 {best['profit']} 万元、利润率 {best['margin']:.1f}%，均为全年最高",
                size=32, color=INK, bold=True, width=1184))
p.append(K.text(48, 80, f"全年收入 {tot_rev} 万元、成本 {tot_cost} 万元、利润 {tot_profit} 万元；"
                        f"Q3 收入环比 −5.2%，但利润率回升至 25.0%。", size=22, color=INK2, width=1184))

# ---------------- chart
CX0, CY0, CX1, CY1 = 48, 126, 1232, 600
p.append(K.rect(CX0, CY0, CX1 - CX0, CY1 - CY0, color=CARD, radius=12, border=f"1 SOLID {LINE}"))
p.append(K.text(CX0 + 24, 146, "收入与成本（万元）", size=22, color=INK, bold=True, width=320))
p.append(K.text(CX0 + 24, 176, "共同零起点 · 每格 40 万元", size=18, color=MUTED, width=360))
# legend
p.append(K.rect(966, 156, 18, 18, color=REV, radius=4))
p.append(K.text(992, 152, "收入", size=20, color=INK2, bold=True, width=80))
p.append(K.rect(1092, 156, 18, 18, color=COST, radius=4))
p.append(K.text(1118, 152, "成本", size=20, color=INK2, bold=True, width=80))

X0, X1 = 214, 1180
BASE, TOP = 520, 250
MAXV = 200
k = (BASE - TOP) / MAXV
for v in range(0, 201, 40):
    y = round(BASE - v * k)
    p.append(K.rect(X0, y, X1 - X0, 1, color=("#C9CED6" if v == 0 else "#E9EBE7")))
    p.append(K.text(120, y - 11, str(v), width=74, size=18, color=MUTED, align="RIGHT"))
p.append(K.text(56, TOP - 40, "万元", size=18, color=MUTED, width=80))

GW = (X1 - X0) / 4
BW = 58
for i, d in enumerate(data):
    cx = X0 + GW * (i + 0.5)
    for j, (v, color) in enumerate(((d["revenue"], REV), (d["cost"], COST))):
        bx = cx - BW - 5 + j * (BW + 10)
        bh = v * k
        p.append(K.rect(round(bx), round(BASE - bh), BW, round(bh), color=color, radius=4))
        p.append(K.text(round(bx) - 12, round(BASE - bh) - 26, str(v), width=BW + 24, size=18,
                        color=INK2, bold=True, align="CENTER"))
    p.append(K.text(round(cx) - 80, BASE + 14, d["quarter"], width=160, size=20, color=INK2,
                    bold=True, align="CENTER"))

# ---------------- profit table
TX0, TY0, TX1, TY1 = 48, 620, 792, 856
p.append(K.rect(TX0, TY0, TX1 - TX0, TY1 - TY0, color=CARD, radius=12, border=f"1 SOLID {LINE}"))
p.append(K.text(TX0 + 24, TY0 + 14, "利润明细（万元）", size=22, color=INK, bold=True, width=300))
colx = [TX0 + 24, 268, 440, 612]
p.append(K.text(TX0 + 24, TY0 + 54, "季度", size=18, color=MUTED, width=200))
for i, d in enumerate(data):
    p.append(K.text(colx[i], TY0 + 54, d["quarter"], size=18, color=MUTED, width=140, align="RIGHT"))
labels = [("收入", "revenue", REV), ("成本", "cost", COST), ("利润", "profit", PROFIT)]
for r, (name, key, color) in enumerate(labels):
    y = TY0 + 88 + r * 38
    p.append(K.text(TX0 + 24, y, name, size=22, color=INK2, bold=True, width=160))
    for i, d in enumerate(data):
        p.append(K.text(colx[i], y, str(d[key]), size=22, color=color, bold=True, width=140,
                        align="RIGHT"))
y = TY0 + 88 + 3 * 38
p.append(K.text(TX0 + 24, y, "利润率", size=22, color=INK2, bold=True, width=160))
for i, d in enumerate(data):
    p.append(K.text(colx[i], y, f"{d['margin']:.1f}%", size=22, color=INK, bold=True, width=140,
                    align="RIGHT"))
p.append(K.rect(TX0 + 24, TY0 + 88 + 3 * 38 - 8, TX1 - TX0 - 48, 1, color=LINE))

# ---------------- insight
IX0, IY0, IX1, IY1 = 812, 620, 1232, 856
p.append(K.rect(IX0, IY0, IX1 - IX0, IY1 - IY0, color="#EEF4FF", radius=12, border=f"1 SOLID #C7D8F5"))
p.append(K.text(IX0 + 24, IY0 + 16, "重点季度 · Q4", size=22, color="#1D4ED8", bold=True, width=300))
p.append(K.text(IX0 + 24, IY0 + 54, f"利润 {best['profit']} 万元，利润率 {best['margin']:.1f}%",
                size=22, color=INK2, width=372))
p.append(K.text(IX0 + 24, IY0 + 88, "比第二名 Q3（32 万元）高 22 万元", size=20, color=INK2, width=372))
p.append(K.text(IX0 + 24, IY0 + 122, "Q3 收入环比 −7 万元（−5.2%）", size=20, color=INK2, width=372))
p.append(K.text(IX0 + 24, IY0 + 152, "成本降到 96 万元，利润率回到 25.0%", size=20, color=INK2, width=372))
p.append(K.text(IX0 + 24, IY0 + 186, "柱高 1.35 像素/万元，零起点一致", size=18, color=MUTED, width=372))
p.append(K.text(48, 868, "数据源 inputs/source.csv · 虚构数据，仅用于排版测试", size=18, color=MUTED,
                width=700))

dsl = K.document(W, H, p, background=BG)
snap = OUT / "corrected-report.snapshot"
snap.write_text(dsl, encoding="utf-8")
warn = K.drain_warnings()
logger = api.TaskLogger(TASK, TMP)
rec = logger.render(snap, OUT / "corrected-report.png", "corrected v1")
print("render:", rec["http_status"], rec["response_bytes"], rec["elapsed_s"])
for w in warn:
    print("  ", w)
if rec["http_status"] != 200:
    print((TMP / "responses" / f"{rec['id']}.bin").read_text(encoding="utf-8", errors="replace")[:1200])
    raise SystemExit(1)

# ---------------- findings
FINDINGS = [
    {"id": "F1", "type": "visual-scale", "location": "图表 y 轴（1280×900 中 x≈120–180，y 292–565）",
     "phenomenon": "y 轴最低刻度是 100，柱形自 100 起画；读者会把 100 当作零起点。",
     "source_check": "source.csv 的数值范围 90–180，四季度都落在 100 附近，截断后差异被放大。",
     "impact": "Q1 收入 120 与成本 90 的真实差 30，在图上看起来接近两倍高差。",
     "fix": "改为 0–200 共同零起点，每 40 万元一条网格线。", "verified": True},
    {"id": "F2", "type": "visual-scale", "location": "图表柱高与网格线（x 200–1120, y 295–565）",
     "phenomenon": "柱高与 y 轴刻度不是同一比例：轴为 2.7 px/万元，柱高约 1.25 px/万元。",
     "source_check": "按轴读数 Q1 收入为 155.6、Q4 为 191.1，而标签分别是 120、180。",
     "impact": "任何按轴估读的数值都比真实值高 11–45 万元。",
     "fix": "柱高改为 1.35 px/万元并与轴共用同一比例。", "verified": True},
    {"id": "F3", "type": "visual-encoding", "location": "Q3 蓝色柱（x 696–759）",
     "phenomenon": "Q3 柱高 198px 高于 Q2 的 172px，但标签 128 < 135。",
     "source_check": "Q2 收入 135、Q3 收入 128，Q2 应更高。",
     "impact": "柱高排序与数值排序相反，读者会误判 Q3 收入高于 Q2。",
     "fix": "按统一比例重绘，Q2 柱高于 Q3 柱。", "verified": True},
    {"id": "F4", "type": "legend", "location": "图例（x 880–1200, y 180–205）",
     "phenomenon": "图例写「■ 成本」用蓝色、「■ 收入」用橙色。",
     "source_check": "柱上标签 120/135/128/180 与 revenue_wan 一致，蓝色柱是收入。",
     "impact": "颜色与系列含义相反，读者会把收入读成成本。",
     "fix": "图例改为蓝色=收入、橙色=成本，与柱色一致。", "verified": True},
    {"id": "F5", "type": "narrative", "location": "主标题（x 56–430, y 40–70）",
     "phenomenon": "标题称「Q3 利润最高」。",
     "source_check": "利润 Q1 30、Q2 27、Q3 32、Q4 54，最高是 Q4。",
     "impact": "结论与数据相反，整张图的立论失效。",
     "fix": "标题改为「Q4 利润 54 万元、利润率 30.0%，均为全年最高」。", "verified": True},
    {"id": "F6", "type": "numeric", "location": "利润明细卡 Q3 数值（x 380–520, y 750–790）",
     "phenomenon": "Q3 利润写作 42 万元。",
     "source_check": "128 − 96 = 32。", "impact": "Q3 利润被高估 10 万元，直接影响排名判断。",
     "fix": "改为 32 万元，并用表格同时给出收入/成本/利润/利润率。", "verified": True},
    {"id": "F7", "type": "narrative", "location": "副标题（x 56–360, y 100–122）",
     "phenomenon": "副标题称「收入持续上升，全年保持增长」。",
     "source_check": "收入 120→135→128→180，Q3 环比下降 7 万元（−5.2%）。",
     "impact": "「持续上升」不成立，掩盖了 Q3 的回落。",
     "fix": "副标题改为给出全年合计与 Q3 环比 −5.2% 的事实陈述。", "verified": True},
    {"id": "F8", "type": "narrative", "location": "重点观察卡（x 840–1220, y 655–820）",
     "phenomenon": "建议把资源集中到 Q3，理由是「它的利润超过其他季度」。",
     "source_check": "Q3 利润 32 万元低于 Q4 的 54 万元，利润率 25.0% 也低于 Q4 的 30.0%。",
     "impact": "基于错误前提的建议会误导资源分配。",
     "fix": "重点改为 Q4，并给出利润率与对比差额。", "verified": True},
    {"id": "F9", "type": "uncertain", "location": "整图",
     "phenomenon": "缺少利润的图形表达，只有四个数字；没有利润率。",
     "source_check": "source.csv 可直接算出利润与利润率。",
     "impact": "不影响正确性，但读者需要自己做减法才能比较季度表现。",
     "fix": "本次补上利润表格与利润率行（属于改进，不计为原图「错误」）。",
     "verified": False, "note": "这是设计取舍，不是数值错误，单列为待确认/改进项。"},
    {"id": "F10", "type": "uncertain", "location": "图例顺序与配色（x 880–1200）",
     "phenomenon": "图例先列成本、后列收入；蓝色比橙色视觉更重。",
     "source_check": "无数据含义。", "impact": "仅影响阅读顺序与视觉权重偏好。",
     "fix": "本次把收入放在前、并使用主色，属于风格改进。", "verified": False,
     "note": "审美偏好，不当作数值错误。"},
]
api.write_json(OUT / "findings.json", {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "source": "tasks/A16-visual-data-forensics/inputs/{flawed-report.png, source.csv}",
    "method": "先目视查看原图，再用像素扫描量出网格线（y=295→565 对应 200→100）与柱矩形，"
              "与 source.csv 逐项核对；不确定项单列。",
    "evidence_measurements": {
        "axis": {"y_for_200": 295, "y_for_100": 565, "px_per_unit": 2.7, "starts_at": 100},
        "bars_blue": [{"q": "Q1", "top": 415, "bottom": 564, "h": 150, "label": 120},
                      {"q": "Q2", "top": 393, "h": 172, "label": 135},
                      {"q": "Q3", "top": 367, "h": 198, "label": 128},
                      {"q": "Q4", "top": 319, "h": 246, "label": 180}],
        "bars_orange": [{"q": "Q1", "top": 455, "h": 109, "label": 90},
                        {"q": "Q2", "top": 430, "h": 134, "label": 108},
                        {"q": "Q3", "top": 437, "h": 127, "label": 96},
                        {"q": "Q4", "top": 400, "h": 164, "label": 126}],
        "axis_reading_vs_label": {"Q1": [155.6, 120], "Q2": [163.7, 135], "Q3": [173.3, 128],
                                  "Q4": [191.1, 180]},
    },
    "findings": FINDINGS,
    "counts": {"confirmed": sum(1 for f in FINDINGS if f["verified"]),
               "uncertain": sum(1 for f in FINDINGS if not f["verified"])},
})
api.write_json(OUT / "corrected-data.json", {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "unit": "万元", "axis": {"min": 0, "max": 200, "tick": 40, "zero_baseline": True,
                             "px_per_unit": 1.35, "plot_top_y": 250, "plot_base_y": 520},
    "quarters": data,
    "totals": {"revenue": tot_rev, "cost": tot_cost, "profit": tot_profit,
               "margin_pct": round(tot_profit / tot_rev * 100, 1)},
    "derivations": {
        "profit": "revenue_wan − cost_wan",
        "margin_pct": "(revenue_wan − cost_wan) / revenue_wan × 100",
        "qoq_revenue_q3": "-7 万元 (-5.2%)",
        "highlight": f"{best['quarter']} 利润 {best['profit']} 万元、利润率 {best['margin']}% 为全年最高",
    },
    "title_basis": "标题中的数值全部来自上表：最高利润季度与最高利润率季度都是 Q4。",
})
print("done")
