# -*- coding: utf-8 -*-
"""A04: conversion-paradox explainer (1600x1000)."""
from __future__ import annotations

import csv
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import dslkit as K  # noqa: E402
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "A04"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
OUT.mkdir(parents=True, exist_ok=True)
clock = rep.TaskClock(TASK)

BG = "#F7F9FC"
CARD = "#FFFFFF"
INK = "#14213D"
INK2 = "#4A5875"
MUTED = "#8494AE"
LINE = "#E3E9F2"
TEAL_D = "#0F766E"
TEAL = "#14B8A6"
TEAL_L = "#99F6E4"
AMBER_D = "#B45309"
AMBER = "#F59E0B"
AMBER_L = "#FDE68A"
INDIGO = "#4338CA"
RED = "#DC2626"
GREEN = "#15803D"

# ---------------------------------------------------------------- data
src = SUITE_ROOT / "tasks" / "A04-conversion-paradox" / "inputs" / "conversion.csv"
rows = []
with src.open(encoding="utf-8", newline="") as fh:
    for r in csv.DictReader(fh):
        rows.append({"period": r["period"], "channel": r["channel"],
                     "visits": int(r["visits"]), "conversions": int(r["conversions"])})

def get(period, channel):
    for r in rows:
        if r["period"] == period and r["channel"] == channel:
            return r
    raise KeyError((period, channel))

D0, P0 = get("前期", "直接访问"), get("前期", "推广访问")
D1, P1 = get("后期", "直接访问"), get("后期", "推广访问")

def rate(r):
    return r["conversions"] / r["visits"] * 100

def total(r1, r2):
    v = r1["visits"] + r2["visits"]
    c = r1["conversions"] + r2["conversions"]
    return {"visits": v, "conversions": c, "rate": c / v * 100}

T0, T1 = total(D0, P0), total(D1, P1)
SHARE0 = [D0["visits"] / T0["visits"], P0["visits"] / T0["visits"]]
SHARE1 = [D1["visits"] / T1["visits"], P1["visits"] / T1["visits"]]
R0 = [rate(D0), rate(P0)]
R1 = [rate(D1), rate(P1)]
naive0 = (R0[0] + R0[1]) / 2
naive1 = (R1[0] + R1[1]) / 2
within_mix0 = R0[0] * SHARE1[0] + R0[1] * SHARE1[1]      # 后期访问结构 + 前期率
mix_effect = within_mix0 - T0["rate"]
rate_effect = T1["rate"] - within_mix0
total_effect = T1["rate"] - T0["rate"]

# ---------------------------------------------------------------- palette by channel
CH_COLOR = {"直接访问": (TEAL, TEAL_L), "推广访问": (AMBER, AMBER_L)}

p: list[str] = []
W, H = 1600, 1000

# header
p.append(K.rect(0, 0, W, 6, color=INDIGO))
p.append(K.text(32, 26, "转化变化，为什么不能只看平均？", size=44, color=INK, bold=True, spacing=-0.3))
p.append(K.text(32, 82, "直接访问 vs 推广访问 · 前期 / 后期 · 两期访问量各 10,000 次 · 单位：转化率 %（成交 ÷ 访问）",
                size=22, color=INK2))
p.append(K.text(1120, 34, "数据分析信息图 · A04", width=448, size=18, color=MUTED, align="RIGHT"))
p.append(K.text(1120, 62, "所有原始分母 / 分子见右下小表", width=448, size=18, color=MUTED, align="RIGHT"))

# ---------------------------------------------------------------- panel A: channel rates
AX, AY, AW, AH = 32, 132, 728, 338
p.append(K.rect(AX, AY, AW, AH, color=CARD, radius=16, border=f"1 SOLID {LINE}"))
p.append(K.text(AX + 24, AY + 18, "渠道转化率：同一 0–100% 尺度", size=22, color=INK, bold=True))
p.append(K.text(AX + 24, AY + 48, "四个柱共用同一零起点，柱高可直接比较", size=18, color=MUTED))

PLOT_X0, PLOT_X1 = 120.0, 712.0
PLOT_TOP, PLOT_BASE = 214.0, 392.0
def yA(v):
    return PLOT_BASE - v / 100 * (PLOT_BASE - PLOT_TOP)

for t in (0, 25, 50, 75, 100):
    y = yA(t)
    p.append(K.rect(PLOT_X0 - 6, y, PLOT_X1 - PLOT_X0 + 12, 1, color=LINE))
    p.append(K.text(60, y - 11, f"{t}%", width=52, size=18, color=MUTED, align="RIGHT"))
p.append(K.rect(PLOT_X0, PLOT_BASE, PLOT_X1 - PLOT_X0, 2, color="#B9C4D6"))

groups = [("直接访问", D0, D1, 268.0), ("推广访问", P0, P1, 564.0)]
for name, r0, r1, cx in groups:
    dark, light = CH_COLOR[name]
    for k, (rec, color, tag) in enumerate(((r0, light, "前期"), (r1, dark, "后期"))):
        left = cx - 98 + k * 106
        v = rate(rec)
        y = yA(v)
        p.append(K.rect(left, y, 90, PLOT_BASE - y, color=color, radius=4,
                        extra=f'borderRadiusTopLeft="4" borderRadiusTopRight="4"'))
        p.append(K.text(left - 10, y - 26, f"{v:.2f}%", width=110, size=20, color=INK, bold=True,
                        align="CENTER"))
        p.append(K.text(left - 10, PLOT_BASE + 7, tag, width=110, size=18, color=INK2, align="CENTER"))
    p.append(K.text(cx - 110, PLOT_BASE + 28, name, width=220, size=22, color=INK, bold=True,
                    align="CENTER"))
    delta = rate(r1) - rate(r0)
    p.append(K.text(cx - 110, PLOT_BASE + 50, f"渠道内 {delta:+.2f}pp", width=220, size=18,
                    color=GREEN, bold=True, align="CENTER"))

# ---------------------------------------------------------------- panel B: overall vs naive
BX, BY, BW, BH = 780, 132, 788, 338
p.append(K.rect(BX, BY, BW, BH, color=CARD, radius=16, border=f"1 SOLID {LINE}"))
p.append(K.text(BX + 24, BY + 18, "总体转化率：成交总数 ÷ 访问总数", size=22, color=INK, bold=True))
p.append(K.text(BX + 24, BY + 48, "分母是两渠道访问量之和，不是两个比例的平均", size=18, color=MUTED))

def big(x, label, value, note):
    p.append(K.text(x, BY + 88, label, size=18, color=MUTED))
    p.append(K.text(x, BY + 110, value, size=52, color=INK, bold=True, spacing=-1.0))
    p.append(K.text(x, BY + 172, note, size=18, color=INK2))

big(BX + 28, "前期 · 总体", f"{T0['rate']:.2f}%", f"2,600 ÷ 10,000")
big(BX + 380, "后期 · 总体", f"{T1['rate']:.2f}%", f"1,660 ÷ 10,000")
p.append(K.text(BX + 268, BY + 118, "→", width=80, size=40, color=MUTED, align="CENTER"))
p.append(K.rect(BX + 640, BY + 108, 120, 40, color="#FEE2E2", radius=8))
p.append(K.text(BX + 640, BY + 115, f"{total_effect:+.2f}pp", width=120, size=22, color=RED,
                bold=True, align="CENTER"))

p.append(K.rect(BX + 24, BY + 208, BW - 48, 1, color=LINE))
p.append(K.text(BX + 28, BY + 220, "常见误算：把两个渠道比例平均", size=18, color=RED, bold=True))
p.append(K.text(BX + 28, BY + 246, f"（30.00% + 10.00%）÷ 2 = {naive0:.2f}%", size=20, color=INK2))
p.append(K.text(BX + 28, BY + 272, f"（35.00% + 12.00%）÷ 2 = {naive1:.2f}%", size=20, color=INK2))
p.append(K.text(BX + 470, BY + 246, f"{naive1 - naive0:+.2f}pp", width=200, size=28, color=RED,
                bold=True))
p.append(K.text(BX + 470, BY + 276, "方向与实际相反", width=260, size=18, color=RED))
p.append(K.rect(BX + 24, BY + 302, 4, 22, color=RED, radius=2))
p.append(K.text(BX + 38, BY + 300, "平均法把两个不同分母的比例等权，忽略了访问结构；它给出上升，总体却在下降。",
                width=BW - 70, size=18, color=INK2))

# ---------------------------------------------------------------- panel C: visit mix
CX, CY, CW, CH = 32, 486, 728, 238
p.append(K.rect(CX, CY, CW, CH, color=CARD, radius=16, border=f"1 SOLID {LINE}"))
p.append(K.text(CX + 24, CY + 16, "访问构成：每期等长，分段按真实占比", size=22, color=INK, bold=True))
BAR_X0, BAR_W, BAR_H = 128.0, 566.0, 54.0
for i, (period, tot, shares) in enumerate((("前期", T0, SHARE0), ("后期", T1, SHARE1))):
    y = CY + 62 + i * 82
    p.append(K.text(CX + 24, y + 14, period, size=22, color=INK, bold=True))
    x = BAR_X0
    for j, (ch, share) in enumerate(zip(("直接访问", "推广访问"), shares)):
        seg_w = share * BAR_W
        dark, light = CH_COLOR[ch]
        p.append(K.rect(x, y, seg_w, BAR_H, color=dark if j == 0 else AMBER, radius=0,
                        extra=(f'borderRadiusTopLeft="6" borderRadiusBottomLeft="6"' if j == 0 else
                               'borderRadiusTopRight="6" borderRadiusBottomRight="6"')))
        rec = (D0 if period == "前期" else D1) if ch == "直接访问" else (P0 if period == "前期" else P1)
        p.append(K.text(x, y + 8, f"{rec['visits']:,}", width=seg_w, size=20, color="#FFFFFF",
                        bold=True, align="CENTER"))
        p.append(K.text(x, y + 32, f"{share*100:.0f}%", width=seg_w, size=18, color="#FFFFFF",
                        align="CENTER"))
        x += seg_w
    p.append(K.text(BAR_X0, y + BAR_H + 6, f"合计 {tot['visits']:,} 次", width=BAR_W, size=18,
                    color=MUTED, align="RIGHT"))

# ---------------------------------------------------------------- panel D: raw table
DX, DY, DW, DH = 780, 486, 788, 238
p.append(K.rect(DX, DY, DW, DH, color=CARD, radius=16, border=f"1 SOLID {LINE}"))
p.append(K.text(DX + 24, DY + 16, "原始分母 / 分子：可逐项核对", size=22, color=INK, bold=True))
COLS = [("期", DX + 24, "START"), ("渠道", DX + 96, "START"), ("访问", DX + 386, "RIGHT"),
        ("成交", DX + 526, "RIGHT"), ("转化率", DX + 686, "RIGHT")]
p.append(K.text(COLS[0][1], DY + 52, "期", size=18, color=MUTED))
p.append(K.text(COLS[1][1], DY + 52, "渠道", size=18, color=MUTED))
for label, edge, _ in COLS[2:]:
    p.append(K.text(edge - 110, DY + 52, label, width=110, size=18, color=MUTED, align="RIGHT"))
rows_view = [
    ("前期", D0, TEAL_L), ("前期", P0, AMBER_L),
    ("前期合计", T0, LINE), ("后期", D1, TEAL_L), ("后期", P1, AMBER_L), ("后期合计", T1, LINE),
]
for i, (name, rec, tint) in enumerate(rows_view):
    y = DY + 76 + i * 26
    is_total = "合计" in name
    if is_total:
        p.append(K.rect(DX + 16, y - 2, DW - 32, 26, color="#F1F5FB"))
    label = name.replace("合计", "")
    p.append(K.text(DX + 24, y, label, size=20 if not is_total else 20, color=INK if is_total else INK2,
                    bold=is_total))
    if not is_total:
        p.append(K.text(DX + 96, y, rec["channel"], size=20, color=INK2))
    else:
        p.append(K.text(DX + 96, y, "两渠道合计", size=20, color=INK2))
    p.append(K.text(DX + 276, y, f"{rec['visits']:,}", width=110, size=20, color=INK, align="RIGHT",
                    extra='fontFeatures="tnum"'))
    p.append(K.text(DX + 416, y, f"{rec['conversions']:,}", width=110, size=20, color=INK, align="RIGHT",
                    extra='fontFeatures="tnum"'))
    p.append(K.text(DX + 576, y, f"{rate(rec):.2f}%", width=110, size=20, color=INDIGO if is_total else INK,
                    bold=is_total, align="RIGHT", extra='fontFeatures="tnum"'))

# ---------------------------------------------------------------- equation strip
EX, EY, EW, EH = 32, 740, 1536, 88
p.append(K.rect(EX, EY, EW, EH, color=CARD, radius=16, border=f"1 SOLID {LINE}"))
p.append(K.text(EX + 24, EY + 14, "逐步拆解", size=18, color=MUTED, bold=True))
nodes = [
    (EX + 108, "前期总体", f"{T0['rate']:.2f}%"),
    (EX + 590, "后期结构 × 前期率", f"{within_mix0:.2f}%"),
    (EX + 1080, "后期总体", f"{T1['rate']:.2f}%"),
]
for x, label, value in nodes:
    p.append(K.text(x, EY + 14, label, width=240, size=18, color=MUTED))
    p.append(K.text(x, EY + 36, value, width=240, size=34, color=INK, bold=True))

def arrow(x1, x2, y, label, color):
    p.append(K.rect(x1, y, x2 - x1, 2, color=color))
    p.append(K.rect(x2 - 12, y - 6, 12, 14, color=color, radius=2))
    p.append(K.text(x1, y - 30, label, width=x2 - x1 + 10, size=20, color=color, bold=True,
                    align="CENTER"))

arrow(EX + 330, EX + 562, EY + 48, f"结构效应 {mix_effect:+.2f}pp", RED)
arrow(EX + 820, EX + 1052, EY + 48, f"渠道内改善 {rate_effect:+.2f}pp", GREEN)
p.append(K.text(EX + 1330, EY + 18, f"合计 {total_effect:+.2f}pp", width=190, size=24, color=INDIGO,
                bold=True, align="RIGHT"))
p.append(K.text(EX + 1330, EY + 52, "结构效应主导", width=190, size=18, color=MUTED, align="RIGHT"))

# ---------------------------------------------------------------- conclusion
YX, YY, YW, YH = 32, 840, 1536, 128
p.append(K.rect(YX, YY, YW, YH, color="#EEF2FF", radius=16, border="1 SOLID #C7D2FE"))
p.append(K.rect(YX, YY, 5, YH, color=INDIGO, radius=2))
p.append(K.text(YX + 24, YY + 14, "主结论", size=18, color=INDIGO, bold=True, spacing=1.2))
p.append(K.text(YX + 100, YY + 8,
                "两渠道转化率都在上升（30.00%→35.00%、10.00%→12.00%），总体却从 26.00% 降到 16.60%。",
                width=YW - 124, size=22, color=INK, bold=True))
p.append(K.text(YX + 100, YY + 38,
                f"访问结构由 80/20 翻转为 20/80：结构效应 {mix_effect:+.2f}pp 压过渠道内改善 "
                f"{rate_effect:+.2f}pp，只看平均会误得 {naive1-naive0:+.2f}pp。",
                width=YW - 124, size=22, color=INK))
p.append(K.rect(YX + 24, YY + 76, YW - 48, 1, color="#C7D2FE"))
p.append(K.text(YX + 24, YY + 84,
                "限制：仅两期两渠道，无成本、时段、落地页与来源质量数据；只能说明构成变化足以解释总体下降，"
                "不能证明因果，也不能推断维持原结构时总体率不变。",
                width=YW - 48, size=18, color=INK2))

dsl = K.document(W, H, p, background=BG)
path = OUT / "conversion-story.snapshot"
path.write_text(dsl, encoding="utf-8")
warn = K.drain_warnings()
logger = api.TaskLogger(TASK, TMP)
rec = logger.render(path, OUT / "conversion-story.png", "baseline: three views + decomposition")
print("render:", rec["http_status"], rec["response_bytes"], rec["elapsed_s"], "s")
for x in warn:
    print(x)
if rec["http_status"] != 200:
    print((TMP / "responses" / f"{rec['id']}.bin").read_text(encoding="utf-8", errors="replace")[:2000])
    raise SystemExit(1)
print("size:", api.measure_png(OUT / "conversion-story.png"))

analysis = {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "generated_at": api.iso_now(),
    "units": {"visits": "次", "conversions": "笔", "rate": "%"},
    "groups": [
        {"period": r["period"], "channel": r["channel"], "numerator": r["conversions"],
         "denominator": r["visits"], "exact_fraction": f"{r['conversions']}/{r['visits']}",
         "exact_decimal": round(r["conversions"] / r["visits"], 8),
         "display_pct": round(rate(r), 2)}
        for r in (D0, P0, D1, P1)
    ],
    "periods": [
        {"period": "前期", "numerator": T0["conversions"], "denominator": T0["visits"],
         "weighted_formula": "(2400 + 200) / (8000 + 2000)",
         "exact_decimal": round(T0["conversions"] / T0["visits"], 8),
         "display_pct": round(T0["rate"], 2),
         "visit_share": {"直接访问": round(SHARE0[0], 6), "推广访问": round(SHARE0[1], 6)}},
        {"period": "后期", "numerator": T1["conversions"], "denominator": T1["visits"],
         "weighted_formula": "(700 + 960) / (2000 + 8000)",
         "exact_decimal": round(T1["conversions"] / T1["visits"], 8),
         "display_pct": round(T1["rate"], 2),
         "visit_share": {"直接访问": round(SHARE1[0], 6), "推广访问": round(SHARE1[1], 6)}},
    ],
    "axes": [
        {"chart": "channel_rates", "unit": "%", "domain": [0, 100], "zero_line": True,
         "pixel_mapping": {"plot_box": [PLOT_X0, PLOT_TOP, PLOT_X1, PLOT_BASE],
                           "formula": "y = 392 - value / 100 * 178"}},
        {"chart": "visit_mix", "unit": "次", "bar_width_px": 566, "equal_length": True,
         "segment_widths_px": {"前期": [round(566 * SHARE0[0], 2), round(566 * SHARE0[1], 2)],
                               "后期": [round(566 * SHARE1[0], 2), round(566 * SHARE1[1], 2)]}},
    ],
    "decomposition": {
        "total_change_pp": round(total_effect, 4),
        "counterfactual_late_mix_early_rates_pct": round(within_mix0, 4),
        "mix_effect_pp": round(mix_effect, 4),
        "rate_effect_pp": round(rate_effect, 4),
        "check_sum_pp": round(mix_effect + rate_effect, 4),
        "method": "sequential: 前期总体 → 用后期访问结构重算（保留前期渠道率）→ 后期实际总体",
    },
    "naive_average": {"early_pct": round(naive0, 4), "late_pct": round(naive1, 4),
                      "delta_pp": round(naive1 - naive0, 4),
                      "why_wrong": "两个渠道分母不同（8000/2000 → 2000/8000），等权平均忽略了访问结构"},
    "conclusions": [
        {"claim": "两渠道转化率均上升", "values": ["30.00→35.00 (+5.00pp)", "10.00→12.00 (+2.00pp)"],
         "support": "groups[*].display_pct"},
        {"claim": "总体转化率下降 9.40pp", "values": ["26.00% → 16.60%"],
         "support": "periods[*].display_pct（成交总数/访问总数）"},
        {"claim": "结构效应主导", "values": [f"mix {mix_effect:+.2f}pp", f"rate {rate_effect:+.2f}pp"],
         "support": "decomposition"},
        {"claim": "平均渠道比例会得出相反方向",
         "values": [f"{naive0:.2f}% → {naive1:.2f}% ({naive1-naive0:+.2f}pp)"], "support": "naive_average"},
    ],
    "limitations": [
        "仅两期、两渠道，样本时点未说明抽样方式",
        "未记录投放成本、时段、落地页版本、用户来源质量等混杂因素",
        "因此不能证明访问结构变化是总体下降的原因，也不能推断维持原结构时总体转化率必然不变",
        "本图只做构成分解，不做统计显著性检验",
    ],
    "deliverables": {"png": {"path": "conversion-story.png", "size": [1600, 1000]},
                     "dsl": "conversion-story.snapshot"},
}
api.write_json(OUT / "analysis.json", analysis)
print("mix", round(mix_effect, 2), "rate", round(rate_effect, 2), "total", round(total_effect, 2))
