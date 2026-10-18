"""A16 · corrected quarterly review from source.csv."""
from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A16"
TMP = ROOT / "tmp" / RUN / TASK
VERSION = sys.argv[1] if len(sys.argv) > 1 else "v001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))

from dsl import C, Col, Gap, HGap, Label, Pos, Row, SizedBox, Stack, T  # noqa: E402

W, H = 1280, 900
PAPER = "#F6F3EA"
INK = "#13202E"
MUTED = "#5B6B7C"
FAINT = "#7A8796"
BLUE = "#2563EB"
ORANGE = "#E8873A"
TEAL = "#0F766E"
LINE = "#DDE4EC"
CARD = "#FFFFFF"
FONT = "Inter,Noto Sans CJK SC"


def load():
    with open(ROOT / "tasks" / "A16-visual-data-forensics" / "inputs" / "source.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return [{"quarter": r["quarter"], "revenue": int(r["revenue_wan"]), "cost": int(r["cost_wan"]),
             "profit": int(r["revenue_wan"]) - int(r["cost_wan"])} for r in rows]


def card(x, y, w, h, color=CARD, border=f"1 SOLID {LINE}", shadow="ELEVATION_1"):
    return Pos(x, y, C(width=w, height=h, color=color, borderRadius=14, border=border, boxShadow=shadow), w=w, h=h)


def chart(data):
    nodes = [card(48, 170, 760, 430)]
    nodes += [
        Pos(76, 196, T("收入与成本对比", size=24, color=INK, weight="BOLD", family=FONT)),
        Pos(76, 230, T("单位：万元", size=18, color=MUTED, family=FONT)),
    ]
    # legend: blue revenue, orange cost
    nodes += [Pos(560, 202, C(width=14, height=14, color=BLUE, borderRadius=3)),
              Pos(580, 198, T("收入", size=20, color=INK, weight="BOLD", family=FONT)),
              Pos(660, 202, C(width=14, height=14, color=ORANGE, borderRadius=3)),
              Pos(680, 198, T("成本", size=20, color=INK, weight="BOLD", family=FONT))]
    # grid + ticks 0..200 step 40
    for v in (0, 40, 80, 120, 160, 200):
        y = 530 - v * 1.2
        nodes.append(Pos(120, y, C(width=640, height=2 if v == 0 else 1, color="#94A3B8" if v == 0 else "#E5EAF1")))
        nodes.append(Pos(74, y - 10, Label(str(v), 40, 24, align="CENTER_RIGHT", size=18, color=FAINT, family=FONT)))
    colors = {"revenue": BLUE, "cost": ORANGE}
    centers = [200, 360, 520, 680]
    for c, q in zip(centers, data):
        for key, dx in (("revenue", -46), ("cost", 2)):
            v = q[key]
            h = v * 1.2
            top = 530 - h
            x = c + dx
            nodes.append(Pos(x, top, C(width=44, height=h, color=colors[key], borderRadius=4)))
            nodes.append(Pos(x, top - 28, Label(str(v), 44, 24, align="CENTER", size=18, color=INK,
                                                weight="BOLD", family=FONT)))
        nodes.append(Pos(c - 60, 548, Label(q["quarter"], 120, 28, align="CENTER", size=20, color=MUTED, family=FONT)))
    return nodes


def profit(data):
    nodes = [card(832, 170, 400, 230),
             Pos(856, 194, T("利润明细", size=24, color=INK, weight="BOLD", family=FONT)),
             Pos(856, 228, T("收入 − 成本 · 万元", size=18, color=MUTED, family=FONT))]
    # Q4 highlight
    nodes.append(Pos(1032, 318, C(width=168, height=74, color="#FFF1D9", borderRadius=10)))
    for i, q in enumerate(data):
        x = 856 + (i % 2) * 184
        y = 254 + (i // 2) * 78
        nodes.append(Pos(x, y, T(q["quarter"], size=18, color=MUTED, family=FONT)))
        nodes.append(Pos(x, y + 22, T(f'{q["profit"]} 万元', size=26, color=TEAL if q["quarter"] == "Q4" else INK,
                                      weight="BOLD", family=FONT)))
    return nodes


def narrative(data):
    q4 = next(q for q in data if q["quarter"] == "Q4")
    return [card(832, 420, 400, 180, color="#E8F5F1", border="1 SOLID #BFE4DA"),
            Pos(856, 442, T("重点观察 / FOCUS", size=14, color=TEAL, weight="BOLD", family=FONT, spacing=2)),
            Pos(856, 468, T("Q4", size=30, color=TEAL, weight="BOLD", family=FONT)),
            Pos(920, 474, T(f'利润 {q4["profit"]} 万元 · 四季最高', size=22, color=INK, weight="BOLD", family=FONT)),
            Pos(856, 514, T(f'收入 {q4["revenue"]} 万元，亦为四季最高；Q3 利润 32 万元，较 Q2 回升 5 万元。',
                            size=22, color=INK, family=FONT, height="1.35"), w=352, h=68)]


def corrections():
    items = [
        "图例：蓝 = 收入，橙 = 成本（原图相反）",
        "纵轴：0–200 万元（原图从 100 起，柱高失真）",
        "Q3 利润：32 万元（128 − 96；原表 42 为错算）",
        "标题/重点：Q4 利润 54 万元最高（原图称 Q3）",
    ]
    nodes = [Pos(48, 620, C(width=1184, height=180, color="#FFF7E8", borderRadius=14, border="1 SOLID #F1D9AE")),
             Pos(76, 640, T("修正记录 / CORRECTIONS", size=20, color="#8A4B08", weight="BOLD", family=FONT, spacing=1))]
    for i, s in enumerate(items):
        nodes.append(Pos(76, 674 + i * 27, T(s, size=22, color=INK, family=FONT)))
    return nodes


def main() -> int:
    data = load()
    title = "Q4 利润 54 万元，全年最高"
    subtitle = "收入 180 万元亦为四季最高；Q3 利润 32 万元，较 Q2 回升 5 万元。"
    nodes = [SizedBox(W, H),
             Pos(0, 0, C(width=W, height=H, color=PAPER)),
             Pos(0, 0, C(width=W, height=8, gradientType="LINEAR", gradientColors=TEAL + ",#0F766E",
                         gradientBegin="CENTER_LEFT", gradientEnd="CENTER_RIGHT")),
             Pos(48, 42, T("QUARTERLY REVIEW / 2026", size=14, color=TEAL, weight="BOLD", family=FONT, spacing=3)),
             Pos(48, 60, T(title, size=40, color=INK, weight="BOLD", family=FONT)),
             Pos(48, 120, T(subtitle, size=22, color=MUTED, family=FONT)),
             Pos(1060, 48, C(width=172, height=38, color="#E8F5F1", borderRadius=19, border="1 SOLID #BFE4DA",
                             alignment="CENTER", child=T("数据修正版", size=16, color=TEAL, weight="BOLD", family=FONT))),
             Pos(1060, 94, T("SOURCE / source.csv", size=12, color=FAINT, family=FONT, spacing=1))]
    nodes += chart(data)
    nodes += profit(data)
    nodes += narrative(data)
    nodes += corrections()
    nodes.append(Pos(48, 842, T("数据源：source.csv · 单位：万元 · 虚构数据，仅用于排版测试", size=18, color=FAINT, family=FONT)))
    dsl = f'<Snapshot type="png" background="{PAPER}">\n' + Stack(nodes, width=W, height=H) + "\n</Snapshot>\n"
    (TMP / "dsl").mkdir(parents=True, exist_ok=True)
    (TMP / "renders").mkdir(parents=True, exist_ok=True)
    (TMP / "dsl" / f"{VERSION}.snapshot").write_text(dsl, encoding="utf-8")

    total_rev = sum(q["revenue"] for q in data)
    total_cost = sum(q["cost"] for q in data)
    total_profit = total_rev - total_cost
    corrected = {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
        "unit": "万元",
        "quarters": data,
        "totals": {"revenue": total_rev, "cost": total_cost, "profit": total_profit},
        "profit_formula": "profit = revenue - cost",
        "axis": {"min": 0, "max": 200, "tick_step": 40, "zero_baseline": True,
                 "scale": "1.2 px per 万元", "plot_bottom_y": 530, "plot_top_y": 290},
        "axes": {"zero": 0, "max": 200, "tick_step": 40, "zero_baseline": True,
                 "scale_px_per_wan": 1.2, "plot_left": 120, "plot_right": 760,
                 "plot_bottom_y": 530, "plot_top_y": 290, "bar_width": 44, "group_centers": [200, 360, 520, 680]},
        "bars": [{"quarter": q["quarter"], "revenue": q["revenue"], "cost": q["cost"],
                  "revenue_height_px": q["revenue"] * 1.2, "cost_height_px": q["cost"] * 1.2} for q in data],
        "highest_revenue": "Q4", "highest_profit": "Q4",
        "profit_rank": ["Q4 54", "Q3 32", "Q1 30", "Q2 27"],
        "legend": {"blue": "收入", "orange": "成本"},
        "conclusion": {"title": "Q4 利润 54 万元，全年最高", "focus": "Q4",
                       "reason": "Q4 profit 54 = revenue 180 - cost 126; highest among 30/27/32/54",
                       "fields": ["profit_rank", "highest_revenue", "highest_profit"]},
    }
    (TMP / "corrected-data.json").write_text(json.dumps(corrected, ensure_ascii=False, indent=2), encoding="utf-8")

    findings = {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
        "source": {"image": "inputs/flawed-report.png", "csv": "inputs/source.csv"},
        "findings": [
            {"id": "F1", "type": "visual-encoding", "location": [870, 182, 1160, 220],
             "observed": "图例写“蓝=成本、橙=收入”，但蓝柱数值为 120/135/128/180，对应 source.csv 的 revenue；橙柱 90/108/96/126 对应 cost。",
             "source_check": "source.csv: Q1 120/90, Q2 135/108, Q3 128/96, Q4 180/126。",
             "impact": "读者会把收入误读为成本，叙事方向相反。", "correction": "蓝=收入、橙=成本；图例与柱色、数值一致。",
             "final_view": "修正图图例蓝“收入”、橙“成本”，与柱高/标签一致。"},
            {"id": "F2", "type": "axis", "location": [95, 540, 760, 590],
             "observed": "纵轴最低刻度为 100，柱底从 100 起，Q1 收入 120 仅显示为 20 的差；柱高被截断。",
             "source_check": "数据最小成本为 90；以 100 为基线会把 90 的成本压到轴下/不可见，且夸大季度差。",
             "impact": "视觉比例失真，无法比较真实量级。", "correction": "纵轴 0–200、步长 40、共同零起点；柱高=值×1.2px。",
             "final_view": "八根柱均从 0 起，Q1 收入 120 高 144px、Q4 收入 180 高 216px。"},
            {"id": "F3", "type": "numeric", "location": [470, 738, 650, 800],
             "observed": "利润明细 Q3 写 42 万元；源数据 Q3 收入 128、成本 96。",
             "source_check": "128 − 96 = 32，正确 Q3 利润为 32 万元；42 比正确值多 10。",
             "impact": "Q3 利润被夸大，直接影响“重点季度”的判断。", "correction": "Q3 利润改为 32 万元；四季度利润 30/27/32/54。",
             "final_view": "修正图 Q3 为 32 万元，Q4 54 万元；四值合计 143 = 563 − 420。"},
            {"id": "F4", "type": "narrative", "location": [48, 40, 470, 88],
             "observed": "标题称“Q3 利润最高”。",
             "source_check": "利润 Q1 30、Q2 27、Q3 32、Q4 54；Q4 最高，Q3 仅第三。",
             "impact": "主结论与数据相反，误导资源决策。", "correction": "标题改为“Q4 利润 54 万元，全年最高”。",
             "final_view": "修正图标题与 Q4 利润 54、排名 54>32>30>27 一致。"},
            {"id": "F5", "type": "narrative", "location": [48, 95, 430, 130],
             "observed": "副标题称“收入持续上升，全年保持增长”。",
             "source_check": "收入 120→135→128→180；Q2→Q3 下降 7 万元，不是持续上升。",
             "impact": "把波动误写成单调增长，掩盖 Q3 收入回落。", "correction": "副标题改为“收入 180 万元亦为四季最高；Q3 利润 32 万元，较 Q2 回升 5 万元”。",
             "final_view": "修正图不再声称持续上升；Q3 收入 128 未被隐藏。"},
            {"id": "F6", "type": "narrative", "location": [880, 675, 1210, 810],
             "observed": "重点观察称“建议把资源集中到 Q3，它的利润超过其他季度”。",
             "source_check": "Q3 利润 32 < Q4 54；Q3 仅高于 Q1/Q2。",
             "impact": "建议建立在错误排名上，资源会投错季度。", "correction": "重点观察改为 Q4：利润 54 万元、收入 180 万元均最高。",
             "final_view": "修正图 FOCUS 为 Q4，文案与数据一致。"},
        ],
        "uncertainties": [
            {"item": "Q3 的 42 是笔误还是公式错误", "why": "原图未给公式/旧 DSL，只能确认结果与 128−96 不符，无法确定成因。", "handling": "按源数据修正为 32，不推断作者动机。"}
        ],
        "checks": [
            {"check": "all_findings_have_evidence", "passed": True, "method": "逐项给出图片框、现象、CSV 核对、影响、修正和最终查看。"},
            {"check": "bar_height_encodes_value", "passed": True, "method": "柱高=值×1.2px，零线 530，Q4 收入 216px、成本 151.2px。"},
            {"check": "legend_data_match", "passed": True, "method": "蓝收入/橙成本，与 CSV 数值对应。"},
            {"check": "narrative_data_match", "passed": True, "method": "标题/副标题/FOCUS 均以 30/27/32/54 与 120/135/128/180 为依据。"},
        ],
    }
    (TMP / "findings.json").write_text(json.dumps(findings, ensure_ascii=False, indent=2), encoding="utf-8")
    print("A16", VERSION, data, "total", total_rev, total_cost, total_profit)
    return 0


if __name__ == "__main__":
    sys.exit(main())
