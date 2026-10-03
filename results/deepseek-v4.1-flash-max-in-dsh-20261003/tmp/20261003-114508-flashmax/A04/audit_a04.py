"""A04: exact fractions, displayed percentages, weighting formula and evidence for analysis.json."""
from __future__ import annotations

import csv
import json
import os
from datetime import datetime, timedelta, timezone

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN_ID = "20261003-114508-flashmax"
TASK = "A04"
SRC = os.path.join(ROOT, "tasks", "A04-conversion-paradox", "inputs", "conversion.csv")
OUT = os.path.join(ROOT, "outputs", RUN_ID, TASK)
TMP = os.path.join(ROOT, "tmp", RUN_ID, TASK)
TZ = timezone(timedelta(hours=8))
os.makedirs(OUT, exist_ok=True)
os.makedirs(TMP, exist_ok=True)

rows = []
with open(SRC, newline="", encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        rows.append({"period": r["period"], "channel": r["channel"],
                     "visits": int(r["visits"]), "conversions": int(r["conversions"])})

PERIODS = ["前期", "后期"]
CHANNELS = ["直接访问", "推广访问"]


def cell(p, c):
    for r in rows:
        if r["period"] == p and r["channel"] == c:
            return r
    raise KeyError((p, c))


cells = {}
for p in PERIODS:
    for c in CHANNELS:
        r = cell(p, c)
        cells[f"{p}|{c}"] = {
            **r,
            "rate": r["conversions"] / r["visits"],
            "rate_pct": round(r["conversions"] / r["visits"] * 100, 2),
            "fraction": f"{r['conversions']}/{r['visits']}",
        }

period_totals = {}
for p in PERIODS:
    V = sum(cell(p, c)["visits"] for c in CHANNELS)
    C = sum(cell(p, c)["conversions"] for c in CHANNELS)
    period_totals[p] = {
        "visits": V, "conversions": C,
        "rate": C / V, "rate_pct": round(C / V * 100, 2),
        "fraction": f"{C}/{V}",
        "mix": {c: cell(p, c)["visits"] / V for c in CHANNELS},
        "mix_pct": {c: round(cell(p, c)["visits"] / V * 100, 2) for c in CHANNELS},
    }

# naive average of channel rates — computed only to show it is NOT used
naive = {p: round(sum(cells[f"{p}|{c}"]["rate"] for c in CHANNELS) / len(CHANNELS) * 100, 2)
         for p in PERIODS}

# ---- exact decomposition of the overall change (mix vs within-channel rate) ----
def decompose(p_from: str, p_to: str) -> dict:
    mix_effect, rate_effect, detail = 0.0, 0.0, []
    for c in CHANNELS:
        a, b = cells[f"{p_from}|{c}"], cells[f"{p_to}|{c}"]
        mix = (b["visits"] / period_totals[p_to]["visits"]
               - a["visits"] / period_totals[p_from]["visits"]) * a["rate"]
        rate = (b["rate"] - a["rate"]) * (a["visits"] / period_totals[p_from]["visits"])
        inter = ((b["visits"] / period_totals[p_to]["visits"]
                  - a["visits"] / period_totals[p_from]["visits"]) * (b["rate"] - a["rate"]))
        mix_effect += mix
        rate_effect += rate
        detail.append({"channel": c, "mix_component": round(mix * 100, 4),
                       "rate_component": round(rate * 100, 4),
                       "interaction_component": round(inter * 100, 4)})
    total = period_totals[p_to]["rate"] - period_totals[p_from]["rate"]
    inter_total = total - mix_effect - rate_effect
    return {
        "formula": "Δ总体率 = Σ(份额变化 × 前期渠道率) + Σ(前期份额 × 渠道率变化) + 交互项",
        "mix_effect_pp": round(mix_effect * 100, 4),
        "rate_effect_pp": round(rate_effect * 100, 4),
        "interaction_pp": round(inter_total * 100, 4),
        "total_change_pp": round(total * 100, 4),
        "check_sum_pp": round((mix_effect + rate_effect + inter_total) * 100, 4),
        "per_channel": detail,
        "reading": "份额结构变化贡献 %+.2fpp，渠道自身转化率变化贡献 %+.2fpp，交互项 %+.2fpp；合计 %+.2fpp。"
                   % (mix_effect * 100, rate_effect * 100, inter_total * 100, total * 100),
    }


mixed = {
    p: round(sum(period_totals[p]["mix"][c] * cells[f"{p}|{c}"]["rate"] for c in CHANNELS) * 100, 2)
    for p in PERIODS
}

doc = {
    "schema": "a04-analysis/1",
    "generated_at": datetime.now(TZ).isoformat(),
    "timezone": "+08:00",
    "source_file": "tasks/A04-conversion-paradox/inputs/conversion.csv",
    "row_definition": "每行 = 某期某渠道的访问数（visits）与成交数（conversions）",
    "units": {"visits": "次", "conversions": "次", "rate": "%"},
    "exact_fractions": {k: v["fraction"] for k, v in cells.items()},
    "channel_cells": cells,
    "period_totals": period_totals,
    "naive_channel_average_pct": naive,
    "naive_average_note": "两期都列出渠道比例的算术平均值，仅用于对照；本图所有总体值都用总成交数 ÷ 总访问数，不使用该平均值。",
    "weighted_formula": {
        "period_overall": "总体转化率 = 该期成交数之和 ÷ 该期访问数之和",
        "as_weighted_mix": "总体转化率 = Σ(渠道访问份额 × 渠道转化率)",
        "workings": {p: " + ".join(f"{period_totals[p]['mix_pct'][c]}% × {cells[f'{p}|{c}']['rate_pct']}%"
                                  for c in CHANNELS) + f" = {mixed[p]}%" for p in PERIODS},
        "weighted_recomputed_pct": mixed,
        "must_not": [
            "不得平均两个渠道的转化率（会得到 20.00% / 23.50%，与真实总体 26.00% / 16.60% 都不符）",
            "不得把同期不同渠道的绝对成交数（2400 与 200）当成转化率",
        ],
    },
    "displayed_percentages": {
        "channel_rates_pct": {k: v["rate_pct"] for k, v in cells.items()},
        "overall_rates_pct": {p: period_totals[p]["rate_pct"] for p in PERIODS},
        "visits_mix_pct": {p: period_totals[p]["mix_pct"] for p in PERIODS},
        "decimals": 2,
    },
    "decomposition": decompose("前期", "后期"),
    "conclusion": {
        "statement": "两个渠道的转化率都上升（直接 30.00%→35.00%、推广 10.00%→12.00%），总体转化率却从 26.00% 降到 16.60%（-9.40pp）：因为访问构成从「直接 80% / 推广 20%」翻转为「直接 20% / 推广 80%」，高转化渠道的占比大幅下降。",
        "evidence": {
            "direct_rate_change_pp": round(cells["后期|直接访问"]["rate_pct"] - cells["前期|直接访问"]["rate_pct"], 2),
            "promo_rate_change_pp": round(cells["后期|推广访问"]["rate_pct"] - cells["前期|推广访问"]["rate_pct"], 2),
            "overall_change_pp": round(period_totals["后期"]["rate_pct"] - period_totals["前期"]["rate_pct"], 2),
            "direct_share_change_pp": round(period_totals["后期"]["mix_pct"]["直接访问"] - period_totals["前期"]["mix_pct"]["直接访问"], 2),
            "mix_effect_pp": decompose("前期", "后期")["mix_effect_pp"],
            "rate_effect_pp": decompose("前期", "后期")["rate_effect_pp"],
            "total_visits_each_period": {p: period_totals[p]["visits"] for p in PERIODS},
            "total_conversions_each_period": {p: period_totals[p]["conversions"] for p in PERIODS},
        },
    },
    "causal_limits": {
        "statement": "该数据不能证明因果关系。",
        "points": [
            "这是两个期的汇总计数，没有随机分组、没有对照，也没有时间趋势控制；渠道份额变化可能同时受投放预算、季节、活动排期等多个未观测因素影响。",
            "「直接访问」与「推广访问」的人群本身不同（主动回访 vs 被投放触达），期与期之间的人群构成也可能变化，转化率差异不能只归因于渠道质量。",
            "样本只有两期各 10,000 次访问、四个格子，无法估计置信区间或做显著性检验；-9.40pp 的总体变化里，结构效应占 %+.2fpp，渠道效应占 %+.2fpp，剩余为交互项。" % (
                decompose("前期", "后期")["mix_effect_pp"], decompose("前期", "后期")["rate_effect_pp"]),
            "图上所有数值都是描述性统计，不能读成「推广渠道变差了」或「直接访问变好了」的原因。",
        ],
    },
    "chart_specs": {
        "channel_rate_chart": {"axis_pct": [0, 40], "tick_step_pct": 5,
                               "note": "两期同尺度 0—40%，四条柱共用同一零起点"},
        "mix_stacked_chart": {"band_width": 240, "note": "每期等长（=100% 访问），分段宽度按真实份额"},
        "overall_chart": {"axis_pct": [0, 40], "note": "与渠道率图同一 0—40% 尺度，可直接比较高度"},
        "audit_table": {"note": "列出四个格子的分子分母与百分比，可逐个核对"},
    },
}

with open(os.path.join(OUT, "analysis.json"), "w", encoding="utf-8") as fh:
    json.dump(doc, fh, ensure_ascii=False, indent=2)
with open(os.path.join(TMP, "analysis.check.json"), "w", encoding="utf-8") as fh:
    json.dump({"overall": {p: period_totals[p]["rate_pct"] for p in PERIODS},
               "channel": doc["displayed_percentages"]["channel_rates_pct"],
               "mix": doc["displayed_percentages"]["visits_mix_pct"],
               "decomposition": doc["decomposition"], "naive": naive},
              fh, ensure_ascii=False, indent=2)

print("前期总体", period_totals["前期"]["rate_pct"], "% | 后期总体", period_totals["后期"]["rate_pct"], "%")
print("渠道率", doc["displayed_percentages"]["channel_rates_pct"])
print("份额", doc["displayed_percentages"]["visits_mix_pct"])
print("分解", doc["decomposition"]["reading"])
print("加权复核", doc["weighted_formula"]["workings"])
print("朴素平均(不采用)", naive)
