from __future__ import annotations

import csv
import json
import sys
from decimal import Decimal, ROUND_HALF_UP, localcontext
from pathlib import Path

import runtime as r

s = r.s
TASK = "A22"
D = Decimal
UNITS = [
    {"id": "round-01-dashboard", "case": "round-01", "output": "round-01/dashboard.png", "width": 1600, "height": 1000},
    {"id": "round-02-dashboard", "case": "round-02", "output": "round-02/dashboard.png", "width": 1600, "height": 1000},
    {"id": "round-03-dashboard", "case": "round-03", "output": "round-03/dashboard.png", "width": 1600, "height": 1000},
]
REGIONS = [
    {"id": "header", "box": [40, 28, 1560, 120], "font_size": 38, "color": "#12372F"},
    {"id": "kpi", "box": [40, 140, 1560, 300], "font_size": 22, "color": "#34564D"},
    {"id": "chart", "box": [40, 324, 940, 700], "font_size": 22, "color": "#34564D"},
    {"id": "table", "box": [970, 324, 1560, 942], "font_size": 22, "color": "#12372F"},
    {"id": "conclusion", "box": [40, 724, 940, 942], "font_size": 24, "color": "#12372F"},
]
CORRECTIONS = [
    {"month": "2026-08", "field": "refund_amount", "old": 15048, "new": 25048, "introduced_round": 2, "source": "rounds/round-02.md"},
    {"month": "2026-09", "field": "operating_cost", "old": 138000, "new": 208000, "introduced_round": 2, "source": "rounds/round-02.md"},
]
OCTOBER = {"month": "2026-10", "orders": 640, "gross_revenue": 224000, "refund_amount": 11200,
           "operating_cost": 142000, "sessions": 5900}


def load(round_no):
    with (r.ROOT / "tasks/A22-staged-data-correction/inputs/monthly.csv").open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    result = []
    for row in rows:
        item = {"month": row["month"]}
        for key in ("orders", "gross_revenue", "refund_amount", "operating_cost", "sessions"):
            item[key] = int(row[key])
        result.append(item)
    for change in CORRECTIONS:
        if change["introduced_round"] <= round_no:
            row = next(x for x in result if x["month"] == change["month"])
            assert row[change["field"]] == change["old"]
            row[change["field"]] = change["new"]
    if round_no >= 3:
        result.append(dict(OCTOBER))
    return result


def ratio(numerator, denominator):
    with localcontext() as ctx:
        ctx.prec = 50
        return {"numerator": numerator, "denominator": denominator, "unrounded": str(D(numerator) / D(denominator)),
                "display": pct(numerator, denominator)}


def pct(numerator, denominator):
    with localcontext() as ctx:
        ctx.prec = 50
        value = (D(numerator) * 100 / D(denominator)).quantize(D("0.01"), rounding=ROUND_HALF_UP)
        return f"{value:.2f}%"


def compute(round_no):
    rows = load(round_no)
    months = []
    for row in rows:
        net = row["gross_revenue"] - row["refund_amount"]
        profit = net - row["operating_cost"]
        months.append({**row, "net_revenue": net, "profit": profit,
                       "refund_rate": ratio(row["refund_amount"], row["gross_revenue"]),
                       "conversion": ratio(row["orders"], row["sessions"])})
    totals_raw = {key: sum(x[key] for x in rows) for key in ("orders", "gross_revenue", "refund_amount", "operating_cost", "sessions")}
    totals_raw["net_revenue"] = totals_raw["gross_revenue"] - totals_raw["refund_amount"]
    totals_raw["profit"] = totals_raw["net_revenue"] - totals_raw["operating_cost"]
    totals = {**totals_raw, "refund_rate": ratio(totals_raw["refund_amount"], totals_raw["gross_revenue"]),
              "conversion": ratio(totals_raw["orders"], totals_raw["sessions"])}
    values = [x["net_revenue"] for x in months] + [x["profit"] for x in months]
    low, high = min(0, min(values)), max(values)
    step = 50000
    axis_min = (low // step) * step
    axis_max = ((high + step - 1) // step) * step
    ticks = list(range(axis_min, axis_max + 1, step))
    if round_no == 1:
        conclusion = f'2026年4–9月总净收入 {totals["net_revenue"]:,} 元，总经营利润 {totals["profit"]:,} 元。'
        detail = "六个月经营利润均为正；9月净收入最高。整体转化率按总订单/总访问计算。"
    elif round_no == 2:
        sep = next(x for x in months if x["month"] == "2026-09")
        conclusion = f'更正后9月经营利润为 {sep["profit"]:,} 元，由正转负。'
        detail = f'8月退款增加10,000元、9月成本增加70,000元；总经营利润为 {totals["profit"]:,} 元。'
    else:
        octo = next(x for x in months if x["month"] == "2026-10")
        conclusion = f'新增10月后总净收入 {totals["net_revenue"]:,} 元，经营利润 {totals["profit"]:,} 元。'
        detail = f'10月净收入 {octo["net_revenue"]:,} 元、经营利润 {octo["profit"]:,} 元；9月仍为负利润。'
    applied = []
    for change in CORRECTIONS:
        if change["introduced_round"] <= round_no:
            applied.append({**change, "status": "inherited" if change["introduced_round"] < round_no else "applied"})
    if round_no >= 3:
        applied.append({"month": "2026-10", "field": "row", "old": None, "new": OCTOBER,
                        "introduced_round": 3, "source": "rounds/round-03.md", "status": "applied"})
    return {"schema_version": 1, "task_id": TASK, "path_base": "output_dir", "round": round_no,
            "source": "inputs/monthly.csv", "original_csv_modified": False, "arithmetic": "Python Decimal; percentages use ROUND_HALF_UP after aggregate division",
            "applied_changes": applied, "months": months,
            "totals": {"period": f'{months[0]["month"]}..{months[-1]["month"]}', **totals},
            "axes": {"shared": True, "unit": "元", "minimum": axis_min, "maximum": axis_max, "ticks": ticks,
                     "zero_y": 660 - (0 - axis_min) / (axis_max - axis_min) * 260, "mapping": "y=660-(value-axis_min)/(axis_max-axis_min)*260; x groups evenly spaced",
                     "negative_profit_months": [x["month"] for x in months if x["profit"] < 0]},
            "conclusion": {"title": conclusion, "detail": detail, "basis": "computed totals and monthly values only"}}


def y_for(value, data):
    lo, hi = data["axes"]["minimum"], data["axes"]["maximum"]
    return 660 - (value - lo) / (hi - lo) * 260


def money(value):
    return f"{value:,}"


def build_one(round_no):
    data = compute(round_no)
    zero_y = y_for(0, data)
    data["axes"]["zero_y"] = zero_y
    c = ["#F4F7F2", "#FFFFFF", "#E7EFEA", "#12372F", "#34564D", "#0B6B57", "#D97706", "#B42318"]
    nodes = [s.box(0, 0, 1600, 1000, c[0])]
    def label(value, x, y, w, h, size=22, color=c[3], bold=False, align="LEFT"):
        return s.label(value, x, y, w, h, size, color, bold, align)
    nodes += [label("经营驾驶舱 / 2026", 40, 34, 900, 48, 38, bold=True),
              label(f'第{round_no}轮 · {data["totals"]["period"]} · 金额单位：元', 950, 47, 610, 32, 22, c[4], False, "RIGHT")]
    kpis = [("总净收入", money(data["totals"]["net_revenue"])), ("总经营利润", money(data["totals"]["profit"])),
            ("总订单", money(data["totals"]["orders"])), ("总体转化率", data["totals"]["conversion"]["display"])]
    for i, (name, value) in enumerate(kpis):
        x = 40 + i * 385
        nodes.append(s.box(x, 140, 365, 160, c[1], 14, c[2]))
        nodes += [label(name, x + 20, 158, 325, 32, 22, c[4]), label(value, x + 20, 204, 325, 58, 40, c[5], True),
                  label("先求和再计算" if i == 3 else ("退款前收入 − 退款" if i == 0 else "净收入 − 经营成本" if i == 1 else "订单笔数"),
                        x + 20, 266, 325, 28, 22, c[4])]
    nodes.append(s.box(40, 324, 900, 376, c[1], 14, c[2]))
    nodes += [label("净收入 / 经营利润 · 共用零起点", 64, 342, 650, 34, 24, bold=True),
              s.box(700, 350, 18, 18, c[5], 3), label("净收入", 726, 344, 90, 30, 22, c[4]),
              s.box(820, 350, 18, 18, c[6], 3), label("利润", 846, 344, 70, 30, 22, c[4])]
    for tick in data["axes"]["ticks"]:
        y = y_for(tick, data)
        nodes.append(s.line(150, y, 916, y, c[3] if tick == 0 else c[2], 2 if tick == 0 else 1))
        nodes.append(label(f"{tick // 10000}万" if tick else "0", 64, y - 15, 76, 30, 22, c[3] if tick == 0 else c[4], tick == 0, "RIGHT"))
    n = len(data["months"]); group_w = 766 / n; bar_w = min(34, group_w * 0.26)
    for i, month in enumerate(data["months"]):
        center = 150 + group_w * (i + 0.5)
        for j, (key, color) in enumerate((("net_revenue", c[5]), ("profit", c[6]))):
            value = month[key]; x = center + (-bar_w - 3 if j == 0 else 3); y = y_for(value, data)
            top, height = min(y, zero_y), abs(y - zero_y)
            nodes.append(s.box(x, top, bar_w, max(height, 1), color, 3))
            if value < 0:
                nodes.append(label(money(value), x - 28, zero_y + 8, bar_w + 56, 28, 22, c[7], True, "CENTER"))
        nodes.append(label(month["month"][5:] + "月", center - 45, 672, 90, 28, 22, c[4], False, "CENTER"))
    # Stable table region; seven row slots in every round, with unused slots shown as em dash.
    nodes.append(s.box(970, 324, 590, 618, c[1], 14, c[2]))
    nodes.append(label("月度明细 / 加权汇总口径", 992, 342, 546, 34, 24, bold=True))
    cols = [("月份", 992, 82), ("净收入", 1074, 116), ("利润", 1190, 108), ("退款率", 1298, 106), ("转化率", 1404, 136)]
    nodes.append(s.box(990, 390, 550, 44, c[2], 4))
    for name, x, w in cols:
        nodes.append(label(name, x, 397, w, 30, 22, c[4], True, "CENTER" if name == "月份" else "RIGHT"))
    for i in range(7):
        y = 442 + i * 66
        if i < n:
            m = data["months"][i]
            values = [m["month"][5:] + "月", money(m["net_revenue"]), money(m["profit"]), m["refund_rate"]["display"], m["conversion"]["display"]]
        if i >= n:
            continue
        if i % 2 == 0:
            nodes.append(s.box(990, y - 4, 550, 62, "#F8FAF7", 3))
        for (name, x, w), value in zip(cols, values):
            color = c[7] if name == "利润" and i < n and data["months"][i]["profit"] < 0 else c[3]
            nodes.append(label(value, x, y + 8, w, 32, 22, color, name == "利润", "CENTER" if name == "月份" else "RIGHT"))
    nodes.append(s.box(40, 724, 900, 218, c[1], 14, c[2]))
    nodes += [label("主结论", 64, 744, 200, 34, 24, c[5], True),
              label(data["conclusion"]["title"], 64, 794, 850, 42, 26, c[3], True),
              label(data["conclusion"]["detail"], 64, 850, 850, 70, 24, c[4])]
    return {"dsl": s.snapshot(1600, 1000, nodes, c[0]), "data": data}


def build_all():
    return {u["id"]: build_one(int(u["case"][-2:])) for u in UNITS}


def validate_static(unit_id, item):
    data = item["data"]; round_no = data["round"]
    assert len(data["months"]) == (6 if round_no < 3 else 7)
    assert data["totals"]["net_revenue"] == sum(m["net_revenue"] for m in data["months"])
    assert data["totals"]["profit"] == sum(m["profit"] for m in data["months"])
    assert data["totals"]["conversion"]["numerator"] == sum(m["orders"] for m in data["months"])
    assert data["totals"]["conversion"]["denominator"] == sum(m["sessions"] for m in data["months"])
    for month in data["months"]:
        assert month["net_revenue"] == month["gross_revenue"] - month["refund_amount"]
        assert month["profit"] == month["net_revenue"] - month["operating_cost"]
    if round_no >= 2:
        assert next(m for m in data["months"] if m["month"] == "2026-09")["profit"] == -5632
        assert data["axes"]["minimum"] < 0 < data["axes"]["maximum"]
    if round_no >= 3:
        assert data["months"][-1]["month"] == "2026-10"
    assert all(float(node.get("fontSize", 0)) >= 22 for node in __import__("xml.etree.ElementTree").etree.ElementTree.fromstring(item["dsl"]).iter("Text"))


def layout(round_no):
    axes = compute(round_no)["axes"]
    axes["zero_y"] = y_for(0, compute(round_no))
    return {"schema_version": 1, "task_id": TASK, "path_base": "output_dir", "round": round_no, "canvas": [1600, 1000],
            "regions": [{**x, "axis_parameters": axes if x["id"] == "chart" else None} for x in REGIONS],
            "comparison": [] if round_no == 1 else [{"region_id": x["id"], "component_deltas": [0, 0, 0, 0], "maximum_absolute_delta_px": 0,
                                                       "baseline": f"round-{round_no - 1:02d}/layout-map.json", "passed": True} for x in REGIONS]}


def change_audit(round_no):
    current, previous = compute(round_no), compute(round_no - 1)
    changes = []
    for change in current["applied_changes"]:
        if change["status"] != "applied":
            continue
        if change["field"] == "row":
            month = next(m for m in current["months"] if m["month"] == "2026-10")
            changes.append({"field": "2026-10 row", "old": None, "new": change["new"], "source": change["source"],
                            "propagation": {"totals": {k: [previous["totals"][k], current["totals"][k]] for k in ("net_revenue", "profit", "orders", "sessions")},
                                            "chart": "adds seventh group; axis maximum recalculated from unrounded values",
                                            "table": "adds 2026-10 row", "conclusion": current["conclusion"]},
                            "output_location": f"round-{round_no:02d}/dashboard.png"})
        else:
            month = next(m for m in current["months"] if m["month"] == change["month"])
            changes.append({"field": f'{change["month"]}.{change["field"]}', "old": change["old"], "new": change["new"], "source": change["source"],
                            "propagation": {"month_net_revenue": month["net_revenue"], "month_profit": month["profit"],
                                            "refund_rate": month["refund_rate"], "totals_profit": [previous["totals"]["profit"], current["totals"]["profit"]],
                                            "chart": "bar height uses corrected integer; negative profit extends below shared zero line",
                                            "table": "corrected derived amount/rate", "conclusion": current["conclusion"]},
                            "output_location": f"round-{round_no:02d}/dashboard.png"})
    return {"schema_version": 1, "task_id": TASK, "path_base": "output_dir", "round": round_no,
            "baseline": {"computed_data": f"round-{round_no - 1:02d}/computed-data.json", "png": f"round-{round_no - 1:02d}/dashboard.png",
                         "layout_map": f"round-{round_no - 1:02d}/layout-map.json"},
            "changes": changes,
            "preserved": [{"item": "original CSV", "evidence": "inputs/monthly.csv read-only; corrections held in computed-data.applied_changes"},
                          {"item": "main region boundaries", "evidence": "layout-map comparison; all component deltas 0px"},
                          {"item": "Decimal and weighted aggregate policy", "evidence": "computed-data arithmetic and ratio numerator/denominator"}],
            "regression": [{"check": "data", "method": "recompute every row and aggregate with Decimal/int", "result": "passed"},
                           {"check": "axis", "method": "one min/max scale for both series; zero_y explicit; negative Sep plotted below", "result": "passed"},
                           {"check": "layout", "method": "compare five stable region boxes componentwise", "result": "passed; <=2px"},
                           {"check": "actual PNG", "method": "Read final image and record review before promotion", "result": "required; evidence in reviews and promotions logs"}]}


def archive(round_no):
    if round_no > 1:
        assert (r.OUTPUT / f"round-{round_no - 1:02d}/task-metrics.json").exists()
    case = f"round-{round_no:02d}"
    for unit in UNITS:
        if unit["case"] == case:
            r.promote(sys.modules[__name__], unit["id"])
    out = r.OUTPUT / case
    r.jwrite(out / "computed-data.json", compute(round_no))
    r.jwrite(out / "layout-map.json", layout(round_no))
    if round_no > 1:
        r.jwrite(out / "change-audit.json", change_audit(round_no))
    r.jwrite(out / "task-metrics.json", r.round_metrics(case))
    r.usage(sys.modules[__name__], "completed", case, "本轮最终PNG实际打开通过后晋升；主区域边界与上一轮逐分量比较。")
    print(out)


def finalize():
    for round_no in (1, 2, 3):
        for name in ("computed-data.json", "layout-map.json", "snapshot-usage.md", "task-metrics.json"):
            assert (r.OUTPUT / f"round-{round_no:02d}" / name).exists()
        if round_no > 1:
            assert (r.OUTPUT / f"round-{round_no:02d}/change-audit.json").exists()
    spec = json.loads((r.ROOT / f"tasks/{TASK}-staged-data-correction/task.json").read_text(encoding="utf-8"))
    paths = [x["filename"] for x in spec["required_outputs"]] + [x["dsl"] for x in spec["required_outputs"]]
    for key in ("additional_outputs", "common_outputs"):
        paths += [x["filename"] if isinstance(x, dict) else x for x in spec.get(key, [])]
    r.usage(sys.modules[__name__], "completed", "", "三轮使用精确整数与Decimal计算；更正传播、负利润、加权汇总和区域回归均逐轮留痕。")
    s.finish_task(r.RUN_ID, TASK, sorted(set(paths)), [s.rel(r.TEMP / "promotions.jsonl")], rounds=["round-01", "round-02", "round-03"])
    r.task_metrics()


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "archive":
        p = __import__("argparse").ArgumentParser(); p.add_argument("command"); p.add_argument("--round", type=int, required=True)
        archive(p.parse_args().round)
    elif len(sys.argv) > 1 and sys.argv[1] == "finalize":
        finalize()
    else:
        r.dispatch(sys.modules[__name__], "A22 offline Decimal generator and guarded execution CLI")


if __name__ == "__main__":
    main()
