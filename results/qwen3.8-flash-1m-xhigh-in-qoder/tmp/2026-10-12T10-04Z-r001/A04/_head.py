"""A04 - Simpson's paradox conversion story, 1600x1000.

Reads tasks/A04-conversion-paradox/inputs/conversion.csv, keeps exact fractions,
writes analysis.json and emits the Snapshot DSL.

Run from the suite task root:
  python tmp/<run_id>/A04/gen.py --ver v001 [--final outputs/<run_id>/A04/conversion-story.snapshot]
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
sys.path.insert(0, str(ROOT / "tmp" / "2026-10-12T10-04Z-r001" / "_suite" / "scripts"))

from snap import (  # noqa: E402
    C, Border, Col, Container, Positioned, Row, Snapshot, Stack, Text, hline, label,
    num, vline,
)

RUN = "2026-10-12T10-04Z-r001"
TASK = "A04"
IN_CSV = ROOT / "tasks" / "A04-conversion-paradox" / "inputs" / "conversion.csv"
OUT_DIR = ROOT / "outputs" / RUN / TASK
TMP_DIR = ROOT / "tmp" / RUN / TASK

FONT = "Noto Sans CJK SC,Inter"
FONT_MONO = "Noto Sans Mono CJK SC,DejaVu Sans Mono"

BG, BG2 = "#070C1A", "#0E1830"
CARD, EDGE = "#101B36", "#243657"
TXT, TXT_2, TXT_3 = "#F2F6FC", "#9FB2D0", "#6A7E9E"
P1C, P2C = "#7C93B5", "#38BDF8"     # 前期 / 后期
DIRECT, PROMO = "#34D399", "#FBBF24"
ROSE, VIOLET = "#FB7185", "#A78BFA"
EMERALD, AMBER = "#34D399", "#FBBF24"

PERIODS = ["前期", "后期"]
CHANNELS = ["直接访问", "推广访问"]

# ---------------------------------------------------------------- data
raw = []
with IN_CSV.open(encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        raw.append({"period": r["period"], "channel": r["channel"],
                    "visits": int(r["visits"]), "conversions": int(r["conversions"])})
assert len(raw) == 4

D = {}
for r in raw:
    D[(r["period"], r["channel"])] = r
tot = {p: {"visits": sum(x["visits"] for x in raw if x["period"] == p),
           "conversions": sum(x["conversions"] for x in raw if x["period"] == p)}
       for p in PERIODS}


def rate(p, ch):
    return F(D[(p, ch)]["conversions"], D[(p, ch)]["visits"])


def overall(p):
    return F(tot[p]["conversions"], tot[p]["visits"])


def mix(p, ch):
    return F(D[(p, ch)]["visits"], tot[p]["visits"])


def pc(x: F, nd: int = 2) -> str:
    return f"{float(x) * 100:.{nd}f}%"


def pp(x: F) -> str:
    v = float(x) * 100
    return f"{'+' if v >= 0 else '−'}{abs(v):.2f} pp"


mix_only = sum(rate("前期", c) * mix("后期", c) for c in CHANNELS)      # 构成变、率不变
rate_only = sum(rate("后期", c) * mix("前期", c) for c in CHANNELS)     # 率变、构成不变
delta_mix = mix_only - overall("前期")
delta_rate = overall("后期") - mix_only
naive = {p: sum(rate(p, c) for c in CHANNELS) / 2 for p in PERIODS}

CONCLUSION = (
    f"两个渠道各自的转化率都上升了（直接访问 {pc(rate('前期','直接访问'))}→{pc(rate('后期','直接访问'))}，"
    f"推广访问 {pc(rate('前期','推广访问'))}→{pc(rate('后期','推广访问'))}），"
    f"但总体转化率从 {pc(overall('前期'))} 降到 {pc(overall('后期'))}（{pp(overall('后期')-overall('前期'))}）。"
    f"分组与总体方向相反。"
)
MECHANISM = (
    f"因为高转化的直接访问占比从 {pc(mix('前期','直接访问'),0)} 降到 {pc(mix('后期','直接访问'),0)}。"
    f"只换构成、率保持前期不变，总体即值 {pc(mix_only)}（{pp(delta_mix)}）；"
    f"再叠加两渠道的率提升，才回到 {pc(overall('后期'))}（{pp(delta_rate)}）。"
)
TRAP = (
    f"若把两个渠道的转化率直接平均，前期得 {pc(naive['前期'])}、后期得 {pc(naive['后期'])}，"
    f"会得出“上升 {pp(naive['后期']-naive['前期'])}”的相反结论——两个渠道分母不同，不能等权。"
)
LIMIT = (
    "以上只是同一总体内“构成”与“率”的算术分解，不能证明因果。"
    "数据仅两期、每渠道一个汇总值，没有用户级配对、曝光量、预算或渠道质量记录，"
    "无法判断直接访问占比下降是推广投放增加、还是自然流量流失所致，"
    "也不能据此推断“加大推广会降低转化”。"
)

analysis = {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "source_input": "tasks/A04-conversion-paradox/inputs/conversion.csv",
    "units_note": "输入给出的是访问数与成交数的原始计数，未标注计量单位；图中按“次/笔”作计数单位呈现，比率一律为百分比。",
    "periods": PERIODS, "channels": CHANNELS,
    "raw": raw,
    "exact": {
        f"{p}|{c}": {
            "visits": D[(p, c)]["visits"], "conversions": D[(p, c)]["conversions"],
            "rate_fraction": f"{D[(p, c)]['conversions']}/{D[(p, c)]['visits']}",
            "rate_fraction_reduced": str(rate(p, c)),
            "rate_exact_percent": str(rate(p, c) * 100),
            "rate_display_percent": pc(rate(p, c)),
            "visit_share_fraction": str(mix(p, c)),
            "visit_share_display_percent": pc(mix(p, c), 0),
        } for p in PERIODS for c in CHANNELS
    },
    "totals": {
        p: {"visits": tot[p]["visits"], "conversions": tot[p]["conversions"],
            "overall_fraction": f"{tot[p]['conversions']}/{tot[p]['visits']}",
            "overall_fraction_reduced": str(overall(p)),
            "overall_exact_percent": str(overall(p) * 100),
            "overall_display_percent": pc(overall(p))} for p in PERIODS
    },
    "weighted_formula": {
        "rule": "总体转化率 = 成交总数 ÷ 访问总数；等价于按访问数加权的渠道率之和",
        "expression": "overall = Σ_c conversions_c / Σ_c visits_c = Σ_c (visits_c / Σ visits) × (conversions_c / visits_c)",
        "前期": {
            "as_weighted_sum": f"(8000/10000)×(2400/8000) + (2000/10000)×(200/2000) "
                               f"= {str(mix('前期','直接访问')*rate('前期','直接访问'))} + "
                               f"{str(mix('前期','推广访问')*rate('前期','推广访问'))} = {str(overall('前期'))}",
            "value_percent": pc(overall("前期")),
        },
        "后期": {
            "as_weighted_sum": f"(2000/10000)×(700/2000) + (8000/10000)×(960/8000) "
                               f"= {str(mix('后期','直接访问')*rate('后期','直接访问'))} + "
                               f"{str(mix('后期','推广访问')*rate('后期','推广访问'))} = {str(overall('后期'))}",
            "value_percent": pc(overall("后期")),
        },
    },
    "forbidden_calculations": {
        "mean_of_channel_rates": {
            "前期": {"value": str(naive["前期"] * 100), "display": pc(naive["前期"]),
                     "why_wrong": "两渠道访问数分别为 8000 与 2000，分母相差 4 倍，不能等权平均"},
            "后期": {"value": str(naive["后期"] * 100), "display": pc(naive["后期"]),
                     "why_wrong": "同上；且后期高转化渠道权重反而更小"},
            "would_imply": f"上升 {pp(naive['后期'] - naive['前期'])}，与总体实际下降 {pp(overall('后期') - overall('前期'))} 相反",
        },
        "absolute_conversions_as_rate": {
            "example": "推广访问成交数 200→960 增长 380%，但其转化率只从 10.00% 升到 12.00%",
            "why_wrong": "同期访问数从 2000 增至 8000，绝对成交量反映的是流量规模而非转化效率",
        },
    },
    "decomposition": {
        "base_前期": pc(overall("前期")),
        "mix_only_前期率后期构成": {"value": str(mix_only * 100), "display": pc(mix_only)},
        "rate_only_后期率前期构成": {"value": str(rate_only * 100), "display": pc(rate_only)},
        "final_后期": pc(overall("后期")),
        "mix_effect_pp": str(delta_mix * 100),
        "rate_effect_pp": str(delta_rate * 100),
        "identity_check": f"base + mix_effect + rate_effect = {pc(overall('后期'))}",
        "note": "顺序分解：先只换构成、再只换率；两种顺序的效应量不同，此处记录的是该顺序下的分解。",
    },
    "direction_check": {
        "直接访问": {"direction": "up", "delta_pp": str((rate("后期", "直接访问") - rate("前期", "直接访问")) * 100)},
        "推广访问": {"direction": "up", "delta_pp": str((rate("后期", "推广访问") - rate("前期", "推广访问")) * 100)},
        "总体": {"direction": "down", "delta_pp": str((overall("后期") - overall("前期")) * 100)},
        "same_direction": False,
        "verdict": "分组与总体反向（Simpson 悖论）",
    },
    "conclusion_basis": {
        "main": CONCLUSION, "mechanism": MECHANISM, "trap": TRAP,
        "values_cited": {
            "rate_前期_直接访问": pc(rate("前期", "直接访问")),
            "rate_后期_直接访问": pc(rate("后期", "直接访问")),
            "rate_前期_推广访问": pc(rate("前期", "推广访问")),
            "rate_后期_推广访问": pc(rate("后期", "推广访问")),
            "overall_前期": pc(overall("前期")), "overall_后期": pc(overall("后期")),
            "overall_delta_pp": str((overall("后期") - overall("前期")) * 100),
            "share_前期_直接访问": pc(mix("前期", "直接访问"), 0),
            "share_后期_直接访问": pc(mix("后期", "直接访问"), 0),
            "mix_only": pc(mix_only), "mix_effect_pp": str(delta_mix * 100),
            "rate_effect_pp": str(delta_rate * 100),
        },
    },
    "causality_limitation": LIMIT,
    "chart_scales": {
        "rate_axis": {"min": 0, "max": 100, "unit": "%", "shared_by": ["channel_grouped", "overall_compare"],
                      "note": "两张率图共用同一 0–100% 尺度与同一刻度位置"},
        "composition_axis": {"kind": "100% stacked", "bar_length_px_equal": True,
                             "segments": "按真实访问占比", "unit": "%"},
    },
}

