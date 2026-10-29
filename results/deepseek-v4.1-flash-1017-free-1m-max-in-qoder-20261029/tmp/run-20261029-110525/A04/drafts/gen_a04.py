#!/usr/bin/env python3
"""A04 conversion paradox: grouped rates, composition, overall, table, conclusion."""
import csv, json, os, html
from pathlib import Path

SCRIPT = Path(__file__).resolve()
SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", SCRIPT.parents[4]))
RUN_ID = SCRIPT.parents[2].name
OUT = SUITE_ROOT / "outputs" / RUN_ID / "A04"
OUT.mkdir(parents=True, exist_ok=True)

def esc(s): return html.escape(str(s), quote=False)
def T(txt, size, color="#0B1220", bold=False, extra=""):
    st = ' fontStyle="BOLD"' if bold else ""
    return f'<Text fontFamily="Noto Sans CJK SC" fontSize="{size}" color="{color}"{st}{extra}>{esc(txt)}</Text>'

rows = []
with (SUITE_ROOT / "tasks/A04-conversion-paradox/inputs/conversion.csv").open(encoding="utf-8") as f:
    for r in csv.DictReader(f):
        v = int(r["visits"]); c = int(r["conversions"])
        rows.append({"period": r["period"], "channel": r["channel"], "visits": v,
                     "conversions": c, "rate": c / v})
by = {(r["period"], r["channel"]): r for r in rows}
def total(p):
    rs = [r for r in rows if r["period"] == p]
    v = sum(r["visits"] for r in rs); c = sum(r["conversions"] for r in rs)
    return {"visits": v, "conversions": c, "rate": c / v}
t1, t2 = total("前期"), total("后期")
mix1 = {ch: by[("前期", ch)]["visits"] / t1["visits"] for ch in ["直接访问", "推广访问"]}
mix2 = {ch: by[("后期", ch)]["visits"] / t2["visits"] for ch in ["直接访问", "推广访问"]}
rate1 = {ch: by[("前期", ch)]["rate"] for ch in ["直接访问", "推广访问"]}
rate2 = {ch: by[("后期", ch)]["rate"] for ch in ["直接访问", "推广访问"]}
mix_effect = (mix2["直接访问"] - mix1["直接访问"]) * rate1["直接访问"] + (mix2["推广访问"] - mix1["推广访问"]) * rate1["推广访问"]
rate_effect = mix2["直接访问"] * (rate2["直接访问"] - rate1["直接访问"]) + mix2["推广访问"] * (rate2["推广访问"] - rate1["推广访问"])
delta = t2["rate"] - t1["rate"]

parts = ['<Snapshot background="#F7F8FC" type="png">', '<Container width="1600" height="1000"><Stack alignment="TOP_LEFT"><Container width="1600" height="1000" color="#F7F8FC"/>']
# header
parts.append('<Positioned left="40" top="32"><Column crossAxisAlignment="START" mainAxisSize="MIN">')
parts.append(T("CONVERSION DIAGNOSTICS / MIX EFFECT", 15, "#2563EB", True, ' letterSpacing="2"'))
parts.append('<SizedBox height="4"/>')
parts.append(T("转化变化，为什么不能只看平均？", 40, "#0B1220", True))
parts.append('<SizedBox height="4"/>')
parts.append(T("两期 × 两渠道 · 总体转化率 = 成交总数 ÷ 访问总数；不是渠道比例的平均", 22, "#56637A"))
parts.append('</Column></Positioned>')
parts.append('<Positioned right="40" top="46"><Column crossAxisAlignment="END" mainAxisSize="MIN">' + T("前期 → 后期", 24, "#0B1220", True) + T("每期访问量均为 10,000", 18, "#8896AB") + '</Column></Positioned>')

# ---- left rate chart ----
parts.append('<Positioned left="40" top="190"><Container width="780" height="440" color="#FFFFFF" borderRadius="20" border="1 SOLID #E3E9F2" padding="24"><Stack alignment="TOP_LEFT"><Container width="732" height="392" color="#FFFFFF"/>')
parts.append('<Positioned left="0" top="0">' + T("分渠道转化率", 24, "#0B1220", True) + '</Positioned>')
parts.append('<Positioned left="0" top="34">' + T("同一 0–100% 尺度 · 4 根柱对应 2 期 × 2 渠道", 18, "#8896AB") + '</Positioned>')
parts.append('<Positioned left="530" top="30"><Row crossAxisAlignment="CENTER"><Container width="12" height="12" color="#2563EB" borderRadius="3"/><SizedBox width="5"/>' + T("直接", 18, "#475569") + '<SizedBox width="14"/><Container width="12" height="12" color="#F59E0B" borderRadius="3"/><SizedBox width="5"/>' + T("推广", 18, "#475569") + '</Row></Positioned>')
# group bands
parts.append('<Positioned left="68" top="82" width="292" height="300"><Container width="292" height="300" color="#EFF4FF" borderRadius="12"/></Positioned>')
parts.append('<Positioned left="388" top="82" width="292" height="300"><Container width="292" height="300" color="#FFF6E8" borderRadius="12"/></Positioned>')
plot_top, plot_bottom = 106, 338
def yv(v): return plot_bottom - v * (plot_bottom - plot_top)
for tick in [0, 25, 50, 75, 100]:
    gy = yv(tick / 100)
    parts.append(f'<Positioned left="0" top="{gy-10}"><Container width="56" alignment="CENTER_RIGHT">' + T(f"{tick}%", 18, "#8896AB") + '</Container></Positioned>')
    parts.append(f'<Positioned left="64" top="{gy}" width="652" height="1"><Container width="652" height="1" color="{"#CBD5E1" if tick == 0 else "#E8EDF5"}"/></Positioned>')
bars = [
    ("前期", "直接访问", 96, 30.0, "#2563EB"), ("前期", "推广访问", 196, 10.0, "#F59E0B"),
    ("后期", "直接访问", 416, 35.0, "#2563EB"), ("后期", "推广访问", 516, 12.0, "#F59E0B"),
]
for period, channel, bx, val, color in bars:
    h = val / 100 * (plot_bottom - plot_top)
    parts.append(f'<Positioned left="{bx}" top="{plot_bottom-h:.1f}" width="72" height="{h:.1f}"><Container width="72" height="{h:.1f}" color="{color}" borderRadiusTopLeft="8" borderRadiusTopRight="8"/></Positioned>')
    parts.append(f'<Positioned left="{bx-14}" top="{plot_bottom-h-32:.1f}" width="100"><Container width="100" alignment="CENTER">' + T(f"{val:.2f}%", 24, "#0B1220", True) + '</Container></Positioned>')

parts.append(f'<Positioned left="68" top="{plot_bottom+14}" width="292"><Container width="292" alignment="CENTER">' + T("前期", 22, "#1D4ED8", True) + '</Container></Positioned>')
parts.append(f'<Positioned left="388" top="{plot_bottom+14}" width="292"><Container width="292" alignment="CENTER">' + T("后期", 22, "#B45309", True) + '</Container></Positioned>')
# delta chips
parts.append(f'<Positioned left="72" top="96"><Container padding="(2,8)" color="#DCFCE7" borderRadius="6">' + T("直接 +5.00pp", 16, "#166534") + '</Container></Positioned>')
parts.append(f'<Positioned left="388" top="96"><Container padding="(2,8)" color="#DCFCE7" borderRadius="6">' + T("推广 +2.00pp", 16, "#166534") + '</Container></Positioned>')
parts.append('</Stack></Container></Positioned>')

# ---- composition ----
parts.append('<Positioned left="840" top="190"><Container width="720" height="280" color="#FFFFFF" borderRadius="20" border="1 SOLID #E3E9F2" padding="24"><Stack alignment="TOP_LEFT"><Container width="672" height="232" color="#FFFFFF"/>')
parts.append('<Positioned left="0" top="0">' + T("两期访问构成", 24, "#0B1220", True) + '</Positioned>')
parts.append('<Positioned left="0" top="34">' + T("每期等长 100%，分段长度 = 真实访问占比", 18, "#8896AB") + '</Positioned>')
bars_x, bar_w = 100, 540
for idx, (p, tt, mix) in enumerate([("前期", t1, mix1), ("后期", t2, mix2)]):
    y = 72 + idx * 76
    w1 = bar_w * mix["直接访问"]
    parts.append(f'<Positioned left="0" top="{y+16}"><Container width="88" alignment="CENTER_RIGHT">' + T(p, 20, "#334155", True) + '</Container></Positioned>')
    w2 = bar_w - w1
    parts.append(f'<Positioned left="{bars_x}" top="{y}" width="{bar_w}" height="50"><Row><Container width="{w1:.1f}" height="50" color="#2563EB" borderRadiusTopLeft="8" borderRadiusBottomLeft="8" alignment="CENTER">' + T(f"{mix['直接访问']*100:.0f}%", 20, "#FFFFFF", True) + f'</Container><Container width="{w2:.1f}" height="50" color="#F59E0B" borderRadiusTopRight="8" borderRadiusBottomRight="8" alignment="CENTER">' + T(f"{mix['推广访问']*100:.0f}%", 20, "#FFFFFF", True) + '</Container></Row></Positioned>')
    parts.append(f'<Positioned left="{bars_x}" top="{y+54}" width="{bar_w}"><Row crossAxisAlignment="CENTER"><Container width="8" height="8" color="#2563EB" shape="CIRCLE"/><SizedBox width="4"/>' + T(f"直接 {by[(p,'直接访问')]['visits']:,}", 18, "#475569") + '<SizedBox width="12"/><Container width="8" height="8" color="#F59E0B" shape="CIRCLE"/><SizedBox width="4"/>' + T(f"推广 {by[(p,'推广访问')]['visits']:,}", 18, "#475569") + '</Row></Positioned>')
parts.append('</Stack></Container></Positioned>')

# ---- overall ----
parts.append('<Positioned left="840" top="474"><Container width="720" height="156" color="#0B1220" borderRadius="20" padding="20"><Column crossAxisAlignment="START" mainAxisSize="MIN">')
parts.append(T("总体转化率 / WEIGHTED TOTAL", 14, "#60A5FA", True, ' letterSpacing="1.5"'))
parts.append('<SizedBox height="2"/>')
parts.append('<Row crossAxisAlignment="END">' + T(f"{t1['rate']*100:.2f}%", 38, "#F8FAFC", True) + '<SizedBox width="12"/>' + T("→", 28, "#64748B") + '<SizedBox width="12"/>' + T(f"{t2['rate']*100:.2f}%", 38, "#FCA5A5", True) + '<SizedBox width="14"/>' + T(f"−{abs(delta)*100:.2f}pp", 22, "#F87171", True) + '</Row>')
parts.append('<SizedBox height="2"/>')
parts.append(T(f"2,600 ÷ 10,000 = 26.00%　→　1,660 ÷ 10,000 = 16.60%", 18, "#94A3B8"))
parts.append('</Column></Container></Positioned>')

# ---- table ----
parts.append('<Positioned left="40" top="660"><Container width="780" height="300" color="#FFFFFF" borderRadius="20" border="1 SOLID #E3E9F2" padding="(18,22)"><Column crossAxisAlignment="START" mainAxisSize="MIN">')
parts.append('<Row crossAxisAlignment="CENTER"><Container width="740" height="28"><Row crossAxisAlignment="CENTER">' + T("原始分子 / 分母", 22, "#0B1220", True) + '<Spacer/>' + T("所有数字均可直接复核", 16, "#8896AB") + '</Row></Container></Row>')
parts.append('<SizedBox height="6"/>')
cols = [("期", 76, "LEFT"), ("渠道", 140, "LEFT"), ("访问", 140, "RIGHT"), ("成交", 140, "RIGHT"), ("转化率", 150, "RIGHT")]
hdr = '<Row crossAxisAlignment="CENTER">'
for name, w, al in cols:
    hdr += f'<Container width="{w}" height="26" alignment="CENTER_{al}">' + T(name, 17, "#8896AB") + '</Container>'
hdr += '</Row>'
parts.append('<Container width="740" borderBottom="1 SOLID #DCE4EF">' + hdr + '</Container>')
def table_row(label1, label2, v, c, rate, bg, bold=False, color="#0B1220"):
    r = f'<Container width="740" height="31" color="{bg}"><Row crossAxisAlignment="CENTER">'
    r += f'<Container width="76" height="31" alignment="CENTER_LEFT">' + T(label1, 22, color, bold) + '</Container>'
    r += f'<Container width="140" height="31" alignment="CENTER_LEFT">' + T(label2, 22, color, bold) + '</Container>'
    r += f'<Container width="140" height="31" alignment="CENTER_RIGHT">' + T(f"{v:,}", 22, color, bold) + '</Container>'
    r += f'<Container width="140" height="31" alignment="CENTER_RIGHT">' + T(f"{c:,}", 22, color, bold) + '</Container>'
    r += f'<Container width="150" height="31" alignment="CENTER_RIGHT">' + T(f"{rate*100:.2f}%", 22, color, bold) + '</Container>'
    r += '</Row></Container>'
    return r
parts.append(table_row("前期", "直接访问", 8000, 2400, 0.30, "#FFFFFF"))
parts.append(table_row("前期", "推广访问", 2000, 200, 0.10, "#F8FAFD"))
parts.append(table_row("前期", "合计", 10000, 2600, 0.26, "#EFF4FF", True, "#1D4ED8"))
parts.append(table_row("后期", "直接访问", 2000, 700, 0.35, "#FFFFFF"))
parts.append(table_row("后期", "推广访问", 8000, 960, 0.12, "#F8FAFD"))
parts.append(table_row("后期", "合计", 10000, 1660, 0.166, "#FFF6E8", True, "#B45309"))
parts.append('</Column></Container></Positioned>')

# ---- conclusion ----
parts.append('<Positioned left="840" top="660"><Container width="720" height="300" color="#FFFFFF" borderRadius="20" border="1 SOLID #E3E9F2" padding="22"><Column crossAxisAlignment="START" mainAxisSize="MIN">')
parts.append(T("管理结论 / WHY THE AVERAGE FELL", 14, "#D97706", True, ' letterSpacing="1.5"'))
parts.append('<SizedBox height="4"/>')
parts.append(T("渠道都在变好，总体却被构成拖低。", 26, "#0B1220", True))
parts.append('<SizedBox height="8"/>')
parts.append(T("前期 80% 访问来自直接渠道（30%），后期 80% 来自推广渠道（12%）。高转化渠道的权重下降，把加权总体从 26.0% 拉到 16.6%。", 22, "#334155"))
parts.append('<SizedBox height="10"/>')
parts.append('<Row crossAxisAlignment="CENTER"><Container padding="(4,9)" color="#FEE2E2" borderRadius="6">' + T("构成效应 −12.0pp", 17, "#B91C1C") + '</Container><SizedBox width="8"/><Container padding="(4,9)" color="#DCFCE7" borderRadius="6">' + T("渠道内改善 +2.6pp", 17, "#166534") + '</Container><SizedBox width="8"/><Container padding="(4,9)" color="#E0E7FF" borderRadius="6">' + T("合计 −9.4pp", 17, "#3730A3") + '</Container></Row>')
parts.append('<Spacer/>')
parts.append(T("限制：该数据只能说明构成变化与总体下降同时发生，不能证明渠道调整导致下降；需控制投放、人群与时间等混杂因素。", 18, "#7C8BA1"))
parts.append('</Column></Container></Positioned>')
parts.append('</Stack></Container></Snapshot>')
dsl = "\n".join(parts)
(OUT / "conversion-story.snapshot").write_text(dsl, encoding="utf-8")

analysis = {
    "schema_version": 1, "task_id": "A04", "path_base": "output_dir",
    "source": "inputs/conversion.csv",
    "unit": "visits=次, conversions=笔, rate=成交/访问",
    "rows": [{"period": r["period"], "channel": r["channel"], "visits": r["visits"],
              "conversions": r["conversions"], "fraction": f"{r['conversions']}/{r['visits']}",
              "display_rate": f"{r['rate']*100:.2f}%"} for r in rows],
    "totals": [{"period": "前期", "visits": t1["visits"], "conversions": t1["conversions"], "rate": t1["rate"]},
               {"period": "后期", "visits": t2["visits"], "conversions": t2["conversions"], "rate": t2["rate"]}],
    "weights": [{"period": "前期", "direct": mix1["直接访问"], "promo": mix1["推广访问"]},
                {"period": "后期", "direct": mix2["直接访问"], "promo": mix2["推广访问"]}],
    "weighted_formula": "overall = w_direct * rate_direct + w_promo * rate_promo",
    "decomposition": {
        "delta_overall": delta,
        "mix_effect": mix_effect,
        "within_channel_effect": rate_effect,
        "check_sum": mix_effect + rate_effect,
        "formula": "Δ = Σ(Δw_i * r_i,early) + Σ(w_i,late * Δr_i)",
    },
    "conclusion": {
        "text": "两个渠道转化率均上升（直接 30%→35%，推广 10%→12%），但访问构成从 80% 直接转为 80% 推广，构成效应 −12.0pp 超过渠道内改善 +2.6pp，总体下降 9.4pp。",
        "referenced_fields": ["rows", "totals", "weights", "decomposition"],
        "causality_limit": "Observational period comparison; no causal claim."
    },
    "checks": {
        "overall_is_total_conversions_over_total_visits": [f"{t1['conversions']}/{t1['visits']}", f"{t2['conversions']}/{t2['visits']}"],
        "no_averaging_of_channel_rates": True,
        "equal_length_composition_bars": True,
        "rate_axis": [0, 100], "rate_axis_unit": "%",
    }
}
(OUT / "analysis.json").write_text(json.dumps(analysis, ensure_ascii=False, indent=2), encoding="utf-8")
print("wrote A04", len(dsl), "mix", mix_effect, "rate", rate_effect)
