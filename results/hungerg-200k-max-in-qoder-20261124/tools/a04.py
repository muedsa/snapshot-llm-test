from __future__ import annotations
import csv
import json
import sys
from fractions import Fraction
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import suitekit as s

RUN_ID = "20261124T113838+0800-aac601"
TASK = "A04"
COLORS = {"直接访问": "#2563EB", "推广访问": "#EA580C"}


def load_data():
    path = s.ROOT / "tasks/A04-conversion-paradox/inputs/conversion.csv"
    with path.open(encoding="utf-8", newline="") as f:
        raw = list(csv.DictReader(f))
    rows = []
    for r in raw:
        visits, conversions = int(r["visits"]), int(r["conversions"])
        rate = Fraction(conversions, visits)
        rows.append({**r, "visits": visits, "conversions": conversions, "fraction": rate, "rate": float(rate)})
    periods = {}
    for period in ("前期", "后期"):
        subset = [r for r in rows if r["period"] == period]
        visits = sum(r["visits"] for r in subset)
        conversions = sum(r["conversions"] for r in subset)
        periods[period] = {
            "visits": visits, "conversions": conversions, "fraction": Fraction(conversions, visits), "rate": conversions / visits,
            "mix": {r["channel"]: Fraction(r["visits"], visits) for r in subset},
        }
    assert [r["rate"] for r in rows] == [0.3, 0.1, 0.35, 0.12]
    assert periods["前期"]["rate"] == 0.26 and periods["后期"]["rate"] == 0.166
    return rows, periods


def pct(value, digits=1):
    return f"{value * 100:.{digits}f}%"


def build_dsl(rows, periods):
    c = []
    c.append(s.label("CONVERSION / MIX EFFECT", 40, 24, 700, 26, 18, "#52627A", True))
    c.append(s.label("转化变化，为什么不能只看平均？", 40, 56, 1250, 56, 42, "#13233A", True))
    c.append(s.label("两期 · 两渠道  |  转化率 = 成交数 ÷ 访问数  |  总体率 = 总成交数 ÷ 总访问数", 40, 122, 1520, 32, 22, "#52627A"))
    # Shared channel colors connect all three panels.
    c.append(s.box(1120, 36, 18, 18, COLORS["直接访问"], 4))
    c.append(s.label("直接访问", 1146, 30, 130, 28, 20, "#344257"))
    c.append(s.box(1310, 36, 18, 18, COLORS["推广访问"], 4))
    c.append(s.label("推广访问", 1336, 30, 150, 28, 20, "#344257"))

    # Panel 1: channel rates, common zero-to-100 scale.
    c.append(s.box(40, 178, 550, 342, "#FFFFFF", 16, "#DCE4ED"))
    c.append(s.label("01  渠道分组转化率", 64, 198, 480, 32, 24, "#13233A", True))
    c.append(s.label("同一 0–100% 尺度 · 单位：%", 64, 234, 480, 26, 18, "#52627A"))
    px, py, pw, ph = 100, 282, 450, 170
    for tick in (0, 25, 50, 75, 100):
        y = py + ph - tick / 100 * ph
        c.append(s.line(px, y, px + pw, y, "#E3EAF2", 1))
        c.append(s.label(f"{tick}%", 48, y - 12, 46, 24, 18, "#718096", False, "RIGHT"))
    groups = [("前期", "直接访问"), ("前期", "推广访问"), ("后期", "直接访问"), ("后期", "推广访问")]
    for i, (period, channel) in enumerate(groups):
        r = next(r for r in rows if r["period"] == period and r["channel"] == channel)
        x = px + 28 + i * 108
        h = r["rate"] * ph
        color = COLORS[channel]
        c.append(s.box(x, py + ph - h, 72, h, color, 5))
        c.append(s.label(pct(r["rate"], 0), x - 8, py + ph - h - 30, 88, 26, 20, color, True, "CENTER"))
        c.append(s.label(period, x - 10, 464, 92, 24, 18, "#52627A", True, "CENTER"))
        c.append(s.label("直接" if channel == "直接访问" else "推广", x - 10, 488, 92, 22, 18, "#52627A", False, "CENTER"))

    # Panel 2: visit mix, equal-length stacked bars.
    c.append(s.box(620, 178, 470, 342, "#FFFFFF", 16, "#DCE4ED"))
    c.append(s.label("02  两期访问构成", 644, 198, 420, 32, 24, "#13233A", True))
    c.append(s.label("每期等长 · 分段按真实访问占比", 644, 234, 420, 26, 18, "#52627A"))
    bx, bw = 680, 350
    for period, y in (("前期", 298), ("后期", 402)):
        c.append(s.label(period, 644, y + 12, 60, 28, 22, "#13233A", True))
        offset = 0
        for channel in ("直接访问", "推广访问"):
            share = float(periods[period]["mix"][channel])
            w = bw * share
            c.append(s.box(bx + offset, y, w, 54, COLORS[channel], 0))
            c.append(s.label(pct(share, 0), bx + offset, y + 13, w, 28, 20, "#FFFFFF", True, "CENTER"))
            offset += w
        c.append(s.label(f'访问总数 {periods[period]["visits"]:,}', bx, y + 60, bw, 24, 18, "#52627A"))
    c.append(s.label("直接访问占比 80% → 20%；推广访问占比 20% → 80%。", 644, 492, 420, 24, 18, "#52627A"))

    # Panel 3: weighted overall comparison.
    c.append(s.box(1120, 178, 440, 342, "#FFFFFF", 16, "#DCE4ED"))
    c.append(s.label("03  总体转化率", 1144, 198, 390, 32, 24, "#13233A", True))
    c.append(s.label("总成交 ÷ 总访问 · 非渠道率平均", 1144, 234, 390, 26, 18, "#52627A"))
    for period, x in (("前期", 1160), ("后期", 1370)):
        p = periods[period]
        c.append(s.label(period, x - 20, 282, 150, 28, 22, "#13233A", True, "CENTER"))
        c.append(s.label(pct(p["rate"]), x - 20, 318, 150, 48, 36, "#0F766E" if period == "前期" else "#BE123C", True, "CENTER"))
        c.append(s.label(f'{p["conversions"]:,} / {p["visits"]:,}', x - 20, 374, 150, 28, 20, "#52627A", False, "CENTER"))
    c.append(s.line(1340, 292, 1340, 414, "#DCE4ED", 1))
    c.append(s.box(1144, 434, 392, 62, "#FFF1F2", 10))
    c.append(s.label("总体下降 9.4 个百分点", 1160, 449, 360, 30, 24, "#BE123C", True, "CENTER"))

    # Raw audit table: all original numerators and denominators.
    c.append(s.box(40, 540, 1520, 270, "#FFFFFF", 16, "#DCE4ED"))
    c.append(s.label("原始数据核对  /  率均由本行分子与分母计算", 64, 558, 1000, 30, 24, "#13233A", True))
    cols = [(64, 170, "期名", "LEFT"), (250, 250, "渠道", "LEFT"), (540, 220, "访问数（分母）", "RIGHT"), (800, 220, "成交数（分子）", "RIGHT"), (1060, 220, "分组转化率", "RIGHT"), (1320, 210, "访问占比", "RIGHT")]
    c.append(s.box(64, 596, 1472, 34, "#EFF4F8", 5))
    for x, w, name, align in cols:
        c.append(s.label(name, x, 600, w, 26, 18, "#52627A", True, align))
    table_rows = rows + [
        {"period": "前期", "channel": "总体", "visits": periods["前期"]["visits"], "conversions": periods["前期"]["conversions"], "rate": periods["前期"]["rate"], "fraction": periods["前期"]["fraction"]},
        {"period": "后期", "channel": "总体", "visits": periods["后期"]["visits"], "conversions": periods["后期"]["conversions"], "rate": periods["后期"]["rate"], "fraction": periods["后期"]["fraction"]},
    ]
    for i, r in enumerate(table_rows):
        y = 638 + i * 27
        if i >= 4:
            c.append(s.box(64, y - 1, 1472, 27, "#F1F5F9", 0))
        mix = "—" if r["channel"] == "总体" else pct(float(periods[r["period"]]["mix"][r["channel"]]), 0)
        vals = [r["period"], r["channel"], f'{r["visits"]:,}', f'{r["conversions"]:,}', pct(r["rate"]), mix]
        for (x, w, _, align), value in zip(cols, vals):
            c.append(s.label(value, x, y, w, 26, 22, "#172033", i >= 4, align))

    # Conclusion after evidence, plus explicit causal limit.
    c.append(s.box(40, 824, 1030, 136, "#132B3A", 16))
    c.append(s.label("数据支持的主结论", 64, 842, 500, 30, 24, "#7ED9C3", True))
    c.append(s.label("两渠道转化率都上升，但访问构成转向较低的推广渠道，导致总体转化率由 26.0% 降至 16.6%。", 64, 882, 980, 62, 22, "#FFFFFF", True))
    c.append(s.box(1090, 824, 470, 136, "#FFF7E6", 16, "#E8C577"))
    c.append(s.label("限制说明", 1114, 842, 420, 30, 24, "#8A5410", True))
    c.append(s.label("该数据描述分组率与构成变化，不能由该数据证明因果。", 1114, 882, 420, 62, 22, "#6B4B16"))
    return s.snapshot(1600, 1000, c)


def analysis(rows, periods):
    groups = []
    for r in rows:
        groups.append({"period": r["period"], "channel": r["channel"], "conversions": r["conversions"], "visits": r["visits"], "exact_fraction": f'{r["conversions"]}/{r["visits"]}', "fraction_reduced": f'{r["fraction"].numerator}/{r["fraction"].denominator}', "display_percentage": pct(r["rate"]), "rate_decimal": r["rate"]})
    period_records = []
    for period in ("前期", "后期"):
        p = periods[period]
        formula = f'({p["conversions"]})/({p["visits"]})={p["conversions"]}/{p["visits"]}={p["conversions"]/p["visits"]:.6f}'
        period_records.append({"period": period, "conversions": p["conversions"], "visits": p["visits"], "exact_fraction": f'{p["conversions"]}/{p["visits"]}', "display_percentage": pct(p["rate"]), "weighted_formula": formula, "visit_mix": {ch: {"visits": next(r["visits"] for r in rows if r["period"] == period and r["channel"] == ch), "share_exact": f'{p["mix"][ch].numerator}/{p["mix"][ch].denominator}', "share_display": pct(float(p["mix"][ch]), 0)} for ch in ("直接访问", "推广访问")}})
    result = s.audit_identity(TASK)
    result.update({
        "source": "inputs/conversion.csv",
        "groups": groups,
        "periods": period_records,
        "axes": [
            {"chart": "channel_rate", "unit": "%", "minimum": 0, "maximum": 100, "plot_box": [100, 282, 550, 452], "mapping": "bar_height=rate*170", "shared_scale": True},
            {"chart": "visit_mix", "unit": "%", "minimum": 0, "maximum": 100, "plot_box": [680, 298, 1030, 456], "bar_lengths": [350, 350], "mapping": "segment_width=350*channel_visits/period_visits"},
            {"chart": "overall_comparison", "unit": "%", "minimum": 0, "maximum": 100, "values_from": "total conversions / total visits"},
        ],
        "comparisons": {"direct_pp_change": (rows[2]["rate"] - rows[0]["rate"]) * 100, "promotion_pp_change": (rows[3]["rate"] - rows[1]["rate"]) * 100, "overall_pp_change": (periods["后期"]["rate"] - periods["前期"]["rate"]) * 100, "group_and_overall_same_direction": False},
        "conclusions": [
            {"claim": "两渠道分组转化率均改善：直接访问 30%→35%，推广访问 10%→12%。", "references": ["S01/S03", "S02/S04"], "evidence": "各组 conversions/visits"},
            {"claim": "总体转化率下降 26.0%→16.6%，与分组变化不同向；同期访问构成从直接 80%/推广 20% 变为直接 20%/推广 80%。", "references": ["前期总计", "后期总计"], "evidence": "总成交/总访问与访问占比堆叠图"},
            {"claim": "不能由该数据证明因果。", "limitation": "这是两期汇总观测数据，未控制其他因素，分组率与构成的相关变化不等于渠道迁移的因果效应。"},
        ],
        "method_notes": ["未平均渠道比例", "未将绝对成交量当作转化率", "所有显示百分比四舍五入至 1 位；精确分数保留在 JSON"],
    })
    return result


def main():
    s.begin_task(RUN_ID, TASK)
    rows, periods = load_data()
    out, tmp = s.task_dirs(RUN_ID, TASK)
    s.write_json(out / "analysis.json", analysis(rows, periods))
    s.write_json(tmp / "computed-values.json", {"groups": groups_json(rows), "periods": {k: {"visits": v["visits"], "conversions": v["conversions"], "rate": v["rate"]} for k, v in periods.items()}})
    image, record = s.render(RUN_ID, TASK, build_dsl(rows, periods), "conversion-story", "v001", kind="baseline")
    s.write_json(tmp / "v001-response.json", record)
    print(image)


def groups_json(rows):
    return [{"period": r["period"], "channel": r["channel"], "visits": r["visits"], "conversions": r["conversions"], "rate": r["rate"]} for r in rows]


if __name__ == "__main__":
    main()
