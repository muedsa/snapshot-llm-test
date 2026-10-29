#!/usr/bin/env python3
"""A16 corrected quarterly report + findings + corrected data."""
import csv, json, os, html
from pathlib import Path

SCRIPT = Path(__file__).resolve()
SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", SCRIPT.parents[4]))
RUN_ID = SCRIPT.parents[2].name
OUT = SUITE_ROOT / "outputs" / RUN_ID / "A16"
OUT.mkdir(parents=True, exist_ok=True)

def esc(s): return html.escape(str(s), quote=False)
def T(txt, size, color="#0B1220", bold=False, extra=""):
    st = ' fontStyle="BOLD"' if bold else ""
    return f'<Text fontFamily="Noto Sans CJK SC" fontSize="{size}" color="{color}"{st}{extra}>{esc(txt)}</Text>'

rows = []
with (SUITE_ROOT / "tasks/A16-visual-data-forensics/inputs/source.csv").open(encoding="utf-8") as f:
    for r in csv.DictReader(f):
        rev = float(r["revenue_wan"]); cost = float(r["cost_wan"]); profit = rev - cost
        rows.append({"quarter": r["quarter"], "revenue": rev, "cost": cost, "profit": profit,
                     "margin": profit / rev})
maxp = max(r["profit"] for r in rows)
maxq = next(r["quarter"] for r in rows if r["profit"] == maxp)
q3 = next(r for r in rows if r["quarter"] == "Q3"); q2 = next(r for r in rows if r["quarter"] == "Q2")

parts = ['<Snapshot background="#F6F7FB" type="png"><Container width="1280" height="900"><Stack alignment="TOP_LEFT"><Container width="1280" height="900" color="#F6F7FB"/>']
parts.append('<Positioned left="40" top="30"><Column crossAxisAlignment="START" mainAxisSize="MIN">' + T("QUARTERLY REVIEW / CORRECTED", 13, "#0D9488", True, ' letterSpacing="2"') + T("季度复盘：Q4 利润最高，Q3 收入回落", 34, "#0B1220", True) + T("收入 / 成本单位：万元 · 共同零起点 · 数据源 source.csv", 20, "#56637A") + '</Column></Positioned>')
parts.append('<Positioned right="40" top="36"><Container padding="(8,14)" color="#E6F7F2" borderRadius="8">' + T("修正版 / 可信叙事", 18, "#0D9488", True) + '</Container></Positioned>')
# chart card
parts.append('<Positioned left="40" top="150"><Container width="760" height="460" color="#FFFFFF" borderRadius="18" border="1 SOLID #E1E7F0"><Stack alignment="TOP_LEFT"><Container width="760" height="460" color="#FFFFFF"/>')
parts.append('<Positioned left="24" top="20">' + T("收入与成本对比", 24, "#0B1220", True) + '</Positioned>')
parts.append('<Positioned left="540" top="24"><Row crossAxisAlignment="CENTER"><Container width="14" height="14" color="#2563EB" borderRadius="3"/><SizedBox width="6"/>' + T("收入", 18, "#475569") + '<SizedBox width="16"/><Container width="14" height="14" color="#F6B94A" borderRadius="3"/><SizedBox width="6"/>' + T("成本", 18, "#475569") + '</Row></Positioned>')
parts.append('<Positioned left="24" top="56">' + T("单位：万元", 18, "#8896AB") + '</Positioned>')
PL, PR, PT, PB = 80, 736, 110, 390
def yv(v): return PB - v / 200 * (PB - PT)
for tick in [0, 50, 100, 150, 200]:
    gy = yv(tick)
    parts.append(f'<Positioned left="16" top="{gy-9:.1f}" width="56"><Container width="56" alignment="CENTER_RIGHT">' + T(str(tick), 18, "#8896AB") + '</Container></Positioned>')
    parts.append(f'<Positioned left="{PL}" top="{gy:.1f}" width="{PR-PL}" height="1"><Container width="{PR-PL}" height="1" color="{"#CBD5E1" if tick == 0 else "#EDF1F7"}"/></Positioned>')
centers = [PL + 82 + i * 164 for i in range(4)]
for i, r in enumerate(rows):
    cx = centers[i]; bw = 42
    for j, (val, col) in enumerate([(r["revenue"], "#2563EB"), (r["cost"], "#F6B94A")]):
        bh = val / 200 * (PB - PT)
        x = cx - 47 + j * 52
        parts.append(f'<Positioned left="{x}" top="{PB-bh:.1f}" width="42" height="{bh:.1f}"><Container width="42" height="{bh:.1f}" color="{col}" borderRadiusTopLeft="5" borderRadiusTopRight="5"/></Positioned>')
        parts.append(f'<Positioned left="{x-14}" top="{PB-bh-24:.1f}" width="70"><Container width="70" alignment="CENTER">' + T(f"{val:.0f}", 18, "#334155", True) + '</Container></Positioned>')
    parts.append(f'<Positioned left="{cx-40}" top="{PB+10}" width="80"><Container width="80" alignment="CENTER">' + T(r["quarter"], 18, "#475569", True) + '</Container></Positioned>')
parts.append('</Stack></Container></Positioned>')
# profit card
parts.append('<Positioned left="820" top="150"><Container width="420" height="460" color="#FFFFFF" borderRadius="18" border="1 SOLID #E1E7F0"><Stack alignment="TOP_LEFT"><Container width="420" height="460" color="#FFFFFF"/>')
parts.append('<Positioned left="24" top="20">' + T("利润明细", 24, "#0B1220", True) + '</Positioned>')
parts.append('<Positioned left="24" top="54">' + T("利润 = 收入 − 成本 · 利润率 = 利润 ÷ 收入", 18, "#8896AB") + '</Positioned>')
for i, r in enumerate(rows):
    y = 92 + i * 82
    hi = r["quarter"] == maxq
    parts.append(f'<Positioned left="16" top="{y}" width="388" height="72"><Container width="388" height="72" color="{"#E6F7F2" if hi else "#F8FAFD"}" borderRadius="10" border="{"1 SOLID #0D9488" if hi else "1 SOLID #EDF1F7"}"/></Positioned>')
    parts.append(f'<Positioned left="32" top="{y+10}">' + T(r["quarter"], 22, "#0D9488" if hi else "#475569", True) + '</Positioned>')
    parts.append(f'<Positioned left="32" top="{y+38}">' + T(f"{r['profit']:.0f} 万元", 26, "#0B1220", True) + '</Positioned>')
    parts.append(f'<Positioned left="190" top="{y+18}">' + T(f"利润率 {r['margin']*100:.1f}%", 18, "#56637A") + '</Positioned>')
    if hi:
        parts.append(f'<Positioned right="32" top="{y+14}"><Container padding="(2,8)" color="#0D9488" borderRadius="6">' + T("最高", 18, "#FFFFFF", True) + '</Container></Positioned>')
    barw = r["profit"] / 60 * 160
    parts.append(f'<Positioned left="190" top="{y+46}" width="160" height="8"><Container width="160" height="8" color="#E8EDF4" borderRadius="4"><Container width="{barw:.1f}" height="8" color="{"#0D9488" if hi else "#94A3B8"}" borderRadius="4"/></Container></Positioned>')
parts.append('</Stack></Container></Positioned>')
# conclusion
parts.append('<Positioned left="40" top="630"><Container width="1200" height="230" color="#0B1220" borderRadius="18" padding="24"><Column crossAxisAlignment="START" mainAxisSize="MIN">' + T("可信叙事 / WHAT THE DATA SUPPORTS", 14, "#5EEAD4", True, ' letterSpacing="1.5"') + '<SizedBox height="8"/>')
for txt in ["Q4 利润 54 万为四季最高；Q3 实际利润 32 万，不是原图的 42 万。",
            "收入并非持续上升：Q3 收入 128 万，较 Q2 的 135 万下降 5.2%。",
            "Q3 利润仍环比增加 5 万：成本从 108 万降到 96 万（−11.1%）。"]:
    parts.append('<Row crossAxisAlignment="START"><Container width="6" height="6" color="#5EEAD4" borderRadius="3" margin="(0,9,10,0)"/><Expanded>' + T(txt, 22, "#E2E8F0") + '</Expanded></Row>')
    parts.append('<SizedBox height="8"/>')
parts.append('<Spacer/>')
parts.append(T("原图另有三处问题：收入/成本图例与颜色对调；Y 轴从 100 起而非 0；Q3“重点观察”结论不成立。", 18, "#94A3B8"))
parts.append('</Column></Container></Positioned>')
parts.append('<Positioned left="40" top="872">' + T("虚构数据 · 依据 source.csv 重算 · 所有柱高与零起点一致", 18, "#94A3B8") + '</Positioned>')
parts.append('</Stack></Container></Snapshot>')
dsl = "\n".join(parts)
(OUT / "corrected-report.snapshot").write_text(dsl, encoding="utf-8")

findings = {
    "schema_version": 1, "task_id": "A16", "path_base": "output_dir",
    "source": "inputs/source.csv", "flawed_report": "inputs/flawed-report.png",
    "findings": [
        {"id": "F1", "kind": "数值错误", "location": "左上标题「季度复盘：Q3利润最高」",
         "phenomenon": "标题声称 Q3 利润最高", "source_check": "Q3 profit 128−96=32；Q4 180−126=54",
         "impact": "把最高利润季度说错，资源建议方向相反", "fix": "标题改为 Q4 利润最高、Q3 收入回落",
         "final_check": "corrected-report 标题与利润明细一致"},
        {"id": "F2", "kind": "数值错误", "location": "利润明细 Q3「42 万元」",
         "phenomenon": "Q3 利润写 42 万", "source_check": "128−96=32 万；42 万无法由本表推出",
         "impact": "高估 Q3 利润 10 万，支撑了错误标题", "fix": "改为 32 万", "final_check": "Q3 行显示 32 万元"},
        {"id": "F3", "kind": "图例/编码错误", "location": "图表图例（右上）与柱色",
         "phenomenon": "蓝色图例写「成本」、橙色写「收入」，但蓝柱 120/135/128/180 与 revenue 一致，橙柱 90/108/96/126 与 cost 一致",
         "source_check": "两组柱高逐季对应 revenue/cost 列", "impact": "读者把收入与成本完全读反",
         "fix": "蓝=收入、橙=成本，图例与柱色一致", "final_check": "图例与柱高对应正确"},
        {"id": "F4", "kind": "叙事错误", "location": "副标题「收入持续上升，全年保持增长」",
         "phenomenon": "声称收入持续上升", "source_check": "Q3 128 < Q2 135，环比 −5.2%",
         "impact": "掩盖 Q3 收入回落", "fix": "改为 Q3 收入回落、Q4 反弹", "final_check": "副标题与数据一致"},
        {"id": "F5", "kind": "坐标轴错误", "location": "纵轴刻度 100–200",
         "phenomenon": "柱图从 100 起，视觉夸大差异", "source_check": "数据最小值 90，轴应含 0",
         "impact": "放大季度差异，误导比较", "fix": "0–200 共同零起点", "final_check": "修正图 0 起点、柱高=值/200"},
        {"id": "F6", "kind": "结论错误", "location": "右下「重点观察 · Q3」",
         "phenomenon": "称 Q3 利润超过其他季度并建议集中资源", "source_check": "Q4 利润 54 > Q3 32；Q3 利润率 25% = Q1，低于 Q4 30%",
         "impact": "建议缺乏数据依据", "fix": "改为 Q4 最高；Q3 的改善来自成本下降", "final_check": "结论卡三条均有数值"},
        {"id": "F7", "kind": "叙事遗漏", "location": "全图",
         "phenomenon": "未解释 Q3 收入下降但利润上升", "source_check": "成本 108→96，降 12 万；收入降 7 万",
         "impact": "错过真正的经营解释", "fix": "结论中加入成本下降 11.1%", "final_check": "结论卡第三条"}
    ],
    "uncertain": [
        {"item": "Q3 的 42 万是否为排版笔误或由其他口径计算", "why_uncertain": "图片无计算过程，source.csv 只能得到 32 万；无法确认作者意图", "treatment": "按源数据修正为 32 万，不推测其他口径"},
        {"item": "图例颜色对调是否有意为之", "why_uncertain": "无旧 DSL；但柱高与列名可核对，编码与数据不一致是客观事实", "treatment": "记为编码错误，不评价审美"},
        {"item": "字体、留白、圆角等视觉偏好", "why_uncertain": "不属于数值或叙事错误", "treatment": "不作为 finding，仅在新版风格中改进"}
    ],
    "not_errors": ["图表使用分组柱而非折线，是合理的表达选择", "配色审美与圆角大小不属于数据错误"]
}
(OUT / "findings.json").write_text(json.dumps(findings, ensure_ascii=False, indent=2), encoding="utf-8")
cd = {
    "schema_version": 1, "task_id": "A16", "path_base": "output_dir",
    "quarterly": [{"quarter": r["quarter"], "revenue_wan": r["revenue"], "cost_wan": r["cost"],
                    "profit_wan": r["profit"], "margin": round(r["margin"], 6)} for r in rows],
    "axis": {"unit": "万元", "min": 0, "max": 200, "ticks": [0, 50, 100, 150, 200], "zero_baseline": True,
             "mapping": "y = 540 - value/200*280 (canvas absolute)"},
    "q3_vs_q2": {"revenue_change_pct": round((q3["revenue"] - q2["revenue"]) / q2["revenue"] * 100, 2),
                 "cost_change_pct": round((q3["cost"] - q2["cost"]) / q2["cost"] * 100, 2),
                 "profit_change_wan": q3["profit"] - q2["profit"]},
    "highest_profit": {"quarter": maxq, "profit_wan": maxp, "margin": round(next(r for r in rows if r["quarter"] == maxq)["margin"], 4)},
    "title_claim": "Q4 利润最高，Q3 收入回落",
    "bar_geometry": {"group_centers_px": centers, "bar_width_px": 42, "plot_bottom_px": 540, "plot_top_px": 260}
}
(OUT / "corrected-data.json").write_text(json.dumps(cd, ensure_ascii=False, indent=2), encoding="utf-8")
print("wrote A16", len(dsl), "max", maxq, maxp, "q3", q3)
