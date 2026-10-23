"""A04 数据模型：读 inputs/conversion.csv，算出所有要上图的数值，并写 analysis.json。

所有百分比都由 成交数/访问数 现场计算，不从字符串解析。总体率必须是
成交总数 ÷ 访问总数，绝不对渠道比例取平均（TASK.md 明令禁止）。

启动基准：总任务根（cwd）。用法：python a04_model.py
"""

from __future__ import annotations

import csv
import json
import os
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a04_io as IO  # noqa: E402

RUN = "r20261014T1536+0800-5f11da"
PERIODS = ["前期", "后期"]
CHANNELS = ["直接访问", "推广访问"]


def pct(fr: Fraction, digits: int = 4) -> float:
    """精确分数 → 显示百分比（未舍入的原值另行记录）。"""
    return float(fr * 100)


def frac_str(f: Fraction) -> str:
    return f"{f.numerator}/{f.denominator}"


def make_naive_derivation(i: int, total: float, cells: dict) -> str:
    """未加权平均的逐步算式，例如 (30.0000 + 10.0000) / 2 = 20.0000。"""
    parts = []
    for ch in CHANNELS:
        c, v = cells[(PERIODS[i], ch)]["conversions"], cells[(PERIODS[i], ch)]["visits"]
        parts.append(f"{float(Fraction(c, v) * 100):g}")
    return "(" + " + ".join(parts) + f") / {len(CHANNELS)} = {total}"


def fmt_delta(d: dict, cells: dict) -> str:
    """把一个分组的变化写成可核对的一句话。"""
    ch = d["scope"]
    a, b = cells[(PERIODS[0], ch)], cells[(PERIODS[1], ch)]
    return (f"{a['conversions']}/{a['visits']} = {d['from_percent']}% → "
            f"{b['conversions']}/{b['visits']} = {d['to_percent']}% "
            f"（{d['delta_percentage_points']:+.2f} pp）")


def build_model() -> dict:
    src = IO.ROOT / "tasks" / "A04-conversion-paradox" / "inputs" / "conversion.csv"
    rows = []
    with src.open(encoding="utf-8-sig", newline="") as fh:
        for r in csv.DictReader(fh):
            rows.append({
                "period": r["period"].strip(),
                "channel": r["channel"].strip(),
                "visits": int(r["visits"]),
                "conversions": int(r["conversions"]),
            })
    assert len(rows) == 4, f"期望 4 行，实际 {len(rows)}"

    # --- 分组：期 × 渠道 ---
    cells: dict[tuple[str, str], dict] = {}
    for r in rows:
        v, c = r["visits"], r["conversions"]
        f = Fraction(c, v)
        cells[(r["period"], r["channel"])] = {
            "period": r["period"],
            "channel": r["channel"],
            "conversions": c,
            "visits": v,
            "exact_fraction": frac_str(f),
            "exact_fraction_value": float(f),
            "rate_percent_exact": float(f * 100),
            "rate_percent_display": pct(f),
        }

    # --- 期合计：总体率 = 成交总数 / 访问总数 ---
    periods = []
    for p in PERIODS:
        tot_v = sum(cells[(p, ch)]["visits"] for ch in CHANNELS)
        tot_c = sum(cells[(p, ch)]["conversions"] for ch in CHANNELS)
        f = Fraction(tot_c, tot_v)
        periods.append({
            "period": p,
            "total_conversions": tot_c,
            "total_visits": tot_v,
            "overall_exact_fraction": frac_str(f),
            "overall_rate_percent_exact": float(f * 100),
            "overall_rate_percent_display": pct(f),
            "formula": "overall = total_conversions / total_visits",
            "composition": [
                {
                    "channel": ch,
                    "visits": cells[(p, ch)]["visits"],
                    "share_exact_fraction": frac_str(
                        Fraction(cells[(p, ch)]["visits"], tot_v)),
                    "share_percent_display": pct(
                        Fraction(cells[(p, ch)]["visits"], tot_v)),
                }
                for ch in CHANNELS
            ],
        })

    # --- 变化量（百分点，非百分比）---
    p0, p1 = periods[0], periods[1]
    deltas = []
    for ch in CHANNELS:
        ca = cells[(PERIODS[0], ch)]
        cb = cells[(PERIODS[1], ch)]
        # 变化量必须由精确分数相减再换算，不能拿已舍入的显示百分比相减
        fa = Fraction(ca["conversions"], ca["visits"])
        fb = Fraction(cb["conversions"], cb["visits"])
        dpp = float((fb - fa) * 100)
        deltas.append({
            "scope": ch,
            "from_percent": float(fa * 100),
            "to_percent": float(fb * 100),
            "from_fraction": ca["exact_fraction"],
            "to_fraction": cb["exact_fraction"],
            "delta_fraction": frac_str(fb - fa),
            "delta_percentage_points": dpp,
            "direction": "上升" if fb > fa else ("下降" if fb < fa else "持平"),
        })
    f0 = Fraction(p0["total_conversions"], p0["total_visits"])
    f1 = Fraction(p1["total_conversions"], p1["total_visits"])
    dov = float((f1 - f0) * 100)
    deltas.append({
        "scope": "总体（成交总数/访问总数）",
        "from_percent": float(f0 * 100),
        "to_percent": float(f1 * 100),
        "from_fraction": p0["overall_exact_fraction"],
        "to_fraction": p1["overall_exact_fraction"],
        "from_numerator_denominator":
            f"{p0['total_conversions']}/{p0['total_visits']}",
        "to_numerator_denominator":
            f"{p1['total_conversions']}/{p1['total_visits']}",
        "delta_fraction": frac_str(f1 - f0),
        "delta_percentage_points": dov,
        "formula": "overall = total_conversions / total_visits",
        "direction": "下降" if f1 < f0 else "上升",
    })

    # --- 恒等分解：总体率 O = Σ w_i r_i，两种顺序分解 ---
    tot = {q["period"]: q["total_visits"] for q in periods}
    w = {p: {ch: Fraction(cells[(p, ch)]["visits"], tot[p]) for ch in CHANNELS}
         for p in PERIODS}
    r = {p: {ch: Fraction(cells[(p, ch)]["conversions"],
                          cells[(p, ch)]["visits"]) for ch in CHANNELS}
         for p in PERIODS}

    def overall(wp: dict, rp: dict) -> Fraction:
        return sum(wp[ch] * rp[ch] for ch in CHANNELS)

    O00 = overall(w[PERIODS[0]], r[PERIODS[0]])
    O11 = overall(w[PERIODS[1]], r[PERIODS[1]])
    O10 = overall(w[PERIODS[0]], r[PERIODS[1]])   # 后期率 × 前期构成
    O01 = overall(w[PERIODS[1]], r[PERIODS[0]])   # 前期率 × 后期构成

    def pp(x: Fraction) -> float:
        return float(x * 100)

    decomposition = {
        "identity": "overall = Σ_i (visits_i / total_visits) × (conversions_i / visits_i)",
        "order_rates_then_mix": {
            "steps": [f"{PERIODS[0]}: {frac_str(O00)} = {pct(O00)}%",
                      f"只换率: {frac_str(O10)} = {pct(O10)}%",
                      f"再换构成: {frac_str(O11)} = {pct(O11)}%"],
            "rate_effect_pp": pp(O10 - O00),
            "mix_effect_pp": pp(O11 - O10),
            "sum_pp": pp(O11 - O00),
        },
        "order_mix_then_rates": {
            "steps": [f"{PERIODS[0]}: {frac_str(O00)} = {pct(O00)}%",
                      f"只换构成: {frac_str(O01)} = {pct(O01)}%",
                      f"再换率: {frac_str(O11)} = {pct(O11)}%"],
            "mix_effect_pp": pp(O01 - O00),
            "rate_effect_pp": pp(O11 - O01),
            "sum_pp": pp(O11 - O00),
        },
        "counterfactual_late_period_at_early_mix": pct(O10),
        "counterfactual_early_rates_at_late_mix": pct(O01),
        "note": "两种顺序的分组率效应（+2.60 ～ +4.40 pp）与构成效应"
                "（-12.00 ～ -13.80 pp）区间不同，但合计恒等于总体变化 -9.40 pp。"
                "构成变化的量级远大于分组率的改善量级。",
    }

    # --- 被禁止的两种算法：它们会给出什么（用于说明为什么不准） ---
    naive = []
    for p in PERIODS:
        chs = [Fraction(cells[(p, ch)]["conversions"], cells[(p, ch)]["visits"])
               for ch in CHANNELS]
        q = next(x for x in periods if x["period"] == p)
        naive.append({
            "period": p,
            "unweighted_mean_of_channel_rates_percent": pct(sum(chs) / len(chs)),
            "true_overall_percent": pct(Fraction(q["total_conversions"],
                                                 q["total_visits"])),
        })
    naive_mean = [n["unweighted_mean_of_channel_rates_percent"] for n in naive]
    naive_delta = naive_mean[1] - naive_mean[0]

    prohibited = {
        "averaging_channel_rates": {
            "rule": "不准对渠道转化率取（未加权的）平均",
            "computed": [
                {"period": PERIODS[i], "value_percent": naive_mean[i],
                 "derivation": make_naive_derivation(i, naive_mean[i], cells)}
                for i in range(len(PERIODS))
            ],
            "apparent_delta_pp": naive_delta,
            "why_wrong": "两渠道的访问数不等（8000/2000 与 2000/8000），"
                         "未加权平均忽略了这个差异。该算法会得到 +3.50 pp 的"
                         "「总体上升」，与真实的 -9.40 pp 方向相反。",
        },
        "treating_absolute_conversions_as_rate": {
            "rule": "不准把同期不同渠道的绝对成交量当成转化率",
            "computed": {
                PERIODS[0]: {"total_conversions": p0["total_conversions"],
                             "unit": "次（绝对成交量，不是百分比）"},
                PERIODS[1]: {"total_conversions": p1["total_conversions"],
                             "unit": "次（绝对成交量，不是百分比）"},
            },
            "why_wrong": "2,600 与 1,660 是绝对成交量，跨期比较必须除以各自"
                         "的访问总数。两期访问总数恰好都是 10,000 次，因此本例的"
                         "绝对量变化幅度与总体率变化幅度同比例，但这两者并非"
                         "同一口径——访问总数不同时两者会给出不同结论，"
                         "本任务要求按 成交总数 ÷ 访问总数 计算。",
        },
    }

    model = {
        "schema_version": 1,
        "task_id": "A04",
        "path_base": "output_dir",
        "timezone": "Asia/Shanghai (UTC+08:00)",
        "run_id": RUN,
        "source_input": {
            "path_base": "suite_root",
            "path": "tasks/A04-conversion-paradox/inputs/conversion.csv",
            "rows": 4,
            "units": {"visits": "次", "conversions": "次",
                      "rate": "%（成交数 ÷ 访问数）"},
        },
        "groups": [cells[(p, ch)] for p in PERIODS for ch in CHANNELS],
        "periods": periods,
        "deltas": deltas,
        "decomposition": decomposition,
        "prohibited_methods": prohibited,
        "axes": [
            {
                "id": "rate_scale",
                "name": "转化率",
                "min": 0.0, "max": 100.0,
                "unit": "%",
                "shared_by": ["chart1_channel_rates", "chart3_overall"],
                "note": "渠道分组率图与总体对照图使用同一 0–100% 尺度，"
                        "且两者使用相同的「每 1% = N 像素」比例，可直接目视比较。",
            },
            {
                "id": "composition_scale",
                "name": "访问构成",
                "total_per_period_visits": 10000,
                "unit": "次",
                "equal_length": True,
                "note": "两期访问总数都是 10,000 次，所以两条堆叠条等长，"
                        "分段长度按真实占比 80/20 与 20/80。",
            },
        ],
        # 渲染契约：把题面「率图同尺度」「构成图等长」转成可测量的像素常量，
        # 由 tmp/.../A04/inspect-*.json 对最终 PNG 反向验证。
        "rendering_contract": {
            "canvas_size": [1600, 1000],
            "coordinate_system": "画布左上原点，x 向右，y 向下，单位像素，"
                                 "框为 [left, top, right, bottom]",
            "rate_px_per_percent": 2.6,
            "rate_full_scale_px": 260.0,
            "rate_origin_x": {"chart1_channel_rates": 256,
                              "chart3_overall": 1230},
            "composition_origin_x": 584,
            "composition_total_length_px": 420,
            "composition_visits_per_px": 10000 / 420,
            "composition_segment_width_px": [
                {"period": p["period"], "channel": c["channel"],
                 "visits": c["visits"],
                 "width_px": c["visits"] / (10000 / 420),
                 "expected_right_x": 584 + c["visits"] / (10000 / 420)}
                for p in periods for c in p["composition"]
            ],
            "chart1_bar_box": [
                {"period": p, "channel": ch,
                 "left": 256, "top": None,
                 "right": 256 + float(Fraction(cells[(p, ch)]["conversions"],
                                               cells[(p, ch)]["visits"]) * 100) * 2.6,
                 "bottom": None,
                 "length_px": float(Fraction(cells[(p, ch)]["conversions"],
                                             cells[(p, ch)]["visits"]) * 100) * 2.6}
                for p in PERIODS for ch in CHANNELS
            ],
            "check": "条长 / 标称百分比 必须等于 rate_px_per_percent，"
                     "且图1与图3测得的值一致（容差 0.06 px/1%）；"
                     "构成两条总长差 ≤ 2px，分段占比与访问占比差 ≤ 1.2pp。",
        },
        "conclusions": [
            {
                "id": "C1",
                "claim": "两个渠道的转化率都在上升，但总体转化率下降了 9.40 个百分点。",
                "evidence": {
                    "direct": fmt_delta(deltas[0], cells),
                    "promo": fmt_delta(deltas[1], cells),
                    "overall": (
                        f"{deltas[2]['from_numerator_denominator']} = "
                        f"{deltas[2]['from_percent']}% → "
                        f"{deltas[2]['to_numerator_denominator']} = "
                        f"{deltas[2]['to_percent']}% "
                        f"（{deltas[2]['delta_percentage_points']:+.2f} pp）"),
                },
                "concordant": False,
                "explanation": "分组与总体不同向。恒等分解显示构成变化的量级"
                               "（-12.00 ～ -13.80 pp）远大于分组率改善的量级"
                               "（+2.60 ～ +4.40 pp）。访问从 80% 高转化渠道"
                               "转向 80% 低转化渠道，加权结果因此下降。",
                "decomposition_ref": "decomposition",
            },
            {
                "id": "C2",
                "claim": "总体转化率必须用成交总数 ÷ 访问总数计算，"
                         "不能对渠道比例取平均。",
                "evidence": {
                    "true_overall": (
                        f"{deltas[2]['from_numerator_denominator']} = "
                        f"{deltas[2]['from_percent']}% → "
                        f"{deltas[2]['to_numerator_denominator']} = "
                        f"{deltas[2]['to_percent']}%"),
                    "naive_mean": {
                        "values_percent": naive_mean,
                        "apparent_delta_pp": naive_delta,
                        "note": "未加权平均渠道比例会得到表观上升，"
                                "方向与真实总体变化相反。",
                    },
                },
                "prohibited_method_ref":
                    "prohibited_methods.averaging_channel_rates",
            },
            {
                "id": "C3",
                "claim": "不能由该数据证明因果。",
                "limitation": "数据只有 2 期 × 2 渠道的聚合计数（共 4 行），"
                              "没有对照组、没有随机分配、没有流量来源或"
                              "投放预算等混杂变量，也没有期内的时间序列。"
                              "恒等分解只说明算术关系，构成变化的原因"
                              "（投放策略、季节、归因口径等）无法从本数据判断。"
                              "因此「构成变化导致总体下降」是算术上的解释，"
                              "不是已证实的因果链。",
                "design_facts": {
                    "rows": 4,
                    "periods": 2,
                    "channels": 2,
                    "has_control_group": False,
                    "has_random_assignment": False,
                    "has_within_period_time_series": False,
                    "logged_confounders": 0,
                },
            },
        ],
    }
    return model


def main() -> None:
    out, tmp = IO.dirs()
    m = build_model()
    (out / "analysis.json").write_text(
        json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (tmp / "model.json").write_text(
        json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("分组率：")
    for g in m["groups"]:
        print(f"  {g['period']} {g['channel']}: {g['conversions']}/{g['visits']} "
              f"= {g['exact_fraction']} = {g['rate_percent_exact']}%")
    print("总体：")
    for p in m["periods"]:
        print(f"  {p['period']}: {p['total_conversions']}/{p['total_visits']} "
              f"= {p['overall_exact_fraction']} = {p['overall_rate_percent_exact']}%")
        print(f"     构成: " + "  ".join(
            f"{c['channel']} {c['visits']}({c['share_percent_display']}%)"
            for c in p["composition"]))
    print("变化（pp）：")
    for d in m["deltas"]:
        print(f"  {d['scope']}: {d['from_percent']}% → {d['to_percent']}% "
              f"Δ={d['delta_percentage_points']:+.4f} pp ({d['direction']})")
    d = m["decomposition"]
    print(f"分解 A 率→构成: 率 {d['order_rates_then_mix']['rate_effect_pp']:+.4f} pp "
          f"构成 {d['order_rates_then_mix']['mix_effect_pp']:+.4f} pp "
          f"合计 {d['order_rates_then_mix']['sum_pp']:+.4f} pp")
    print(f"分解 B 构成→率: 构成 {d['order_mix_then_rates']['mix_effect_pp']:+.4f} pp "
          f"率 {d['order_mix_then_rates']['rate_effect_pp']:+.4f} pp "
          f"合计 {d['order_mix_then_rates']['sum_pp']:+.4f} pp")
    print(f"未加权平均（错误口径）: {m['prohibited_methods']['averaging_channel_rates']['computed'][0]['value_percent']}% "
          f"→ {m['prohibited_methods']['averaging_channel_rates']['computed'][1]['value_percent']}% "
          f"Δ={m['prohibited_methods']['averaging_channel_rates']['apparent_delta_pp']:+.4f} pp")
    print(f"analysis.json → {out / 'analysis.json'}")


if __name__ == "__main__":
    main()
