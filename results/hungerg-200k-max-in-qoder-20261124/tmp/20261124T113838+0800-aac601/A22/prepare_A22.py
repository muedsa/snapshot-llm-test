from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
import shutil
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import suitekit as sk

RUN = (ROOT / "tmp" / "_suite" / "run-id.txt").read_text(encoding="utf-8").strip()
TASK = "A22"
INPUT = ROOT / "tasks/A22-staged-data-correction/inputs/monthly.csv"
HERE = ROOT / sk.CONFIG["temp_root"] / RUN / TASK
OUTPUT = ROOT / sk.CONFIG["output_root"] / RUN / TASK
STATE_PATH = ROOT / sk.CONFIG["output_root"] / RUN / "_suite/suite-state.json"


def rp(path: Path) -> str:
    return sk.rel(path, ROOT)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def guard(round_no: int) -> None:
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    order = [item["id"] for item in sk.CATALOG["tasks"]]
    statuses = {item["id"]: item["status"] for item in state["tasks"]}
    assert all(statuses[item["id"]] == "completed" for item in sk.CATALOG["tasks"][:order.index(TASK)]), "strict task order"
    task = next(item for item in state["tasks"] if item["id"] == TASK)
    assert task["status"] in ("pending", "in_progress")
    if round_no > 1:
        assert f"round-{round_no-1:02d}" in task.get("completed_rounds", []), "round order"


def q2(numerator: int, denominator: int) -> str:
    value = Decimal(numerator) / Decimal(denominator)
    return str(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def money(n: int) -> str:
    return f"{n:,}"


def wan(n: int) -> str:
    value = (Decimal(n) / Decimal(10000)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"{value:,.2f}"


def ratio_fields(numerator: int, denominator: int) -> dict:
    return {"numerator": numerator, "denominator": denominator, "unrounded": numerator / denominator, "display": q2(numerator, denominator), "unit": "ratio"}


def load_months(round_no: int) -> list[dict]:
    with INPUT.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    months = []
    for row in rows:
        item = {"month": row["month"]}
        for key in ("orders", "gross_revenue", "refund_amount", "operating_cost", "sessions"):
            item[key] = int(row[key])
        months.append(item)
    if round_no >= 2:
        august = next(item for item in months if item["month"] == "2026-08")
        assert august["refund_amount"] == 15048
        august["refund_amount"] = 25048
        september = next(item for item in months if item["month"] == "2026-09")
        assert september["operating_cost"] == 138000
        september["operating_cost"] = 208000
    if round_no >= 3:
        months.append({"month": "2026-10", "orders": 640, "gross_revenue": 224000,
                       "refund_amount": 11200, "operating_cost": 142000, "sessions": 5900})
    for item in months:
        item["net_revenue"] = item["gross_revenue"] - item["refund_amount"]
        item["operating_profit"] = item["net_revenue"] - item["operating_cost"]
        item["refund_rate"] = ratio_fields(item["refund_amount"], item["gross_revenue"])
        item["conversion_rate"] = ratio_fields(item["orders"], item["sessions"])
    return months


def totals_for(months: list[dict]) -> dict:
    keys = ("gross_revenue", "refund_amount", "operating_cost", "net_revenue", "operating_profit", "orders", "sessions")
    sums = {key: sum(item[key] for item in months) for key in keys}
    return {
        "period": f"{months[0]['month']}—{months[-1]['month']}",
        "month_count": len(months),
        **sums,
        "refund_rate": ratio_fields(sums["refund_amount"], sums["gross_revenue"]),
        "conversion_rate": ratio_fields(sums["orders"], sums["sessions"]),
        "aggregation_method": "金额与计数先分别求和；总体率由期间总量相除，不平均各月百分比。",
    }


def axis_for(months: list[dict]) -> dict:
    values = [value for item in months for value in (item["net_revenue"], item["operating_profit"])]
    ymin, ymax = (-20000, 220000) if min(values) < 0 else (0, 220000)
    ticks = [-20000, 0, 50000, 100000, 150000, 200000] if ymin < 0 else [0, 50000, 100000, 150000, 200000]
    return {"unit": "元", "display_unit": "万元", "shared_zero_baseline": True, "value_min": min(values),
            "value_max": max(values), "y_min": ymin, "y_max": ymax, "ticks": ticks,
            "plot_box": [160, 548, 920, 872], "scale_method": "线性共同比例；净收入与经营利润共用零线和纵轴，未截断负值。",
            "bar_values": [{"month": item["month"], "net_revenue": item["net_revenue"],
                            "operating_profit": item["operating_profit"]} for item in months]}


def applied_changes(round_no: int) -> list[dict]:
    if round_no == 1:
        return [{"source": "inputs/monthly.csv", "fields": "全部六个月原始字段", "old": None,
                 "new": "按CSV原值载入", "status": "baseline"}]
    if round_no == 2:
        return [
            {"source": "rounds/round-02.md", "month": "2026-08", "field": "refund_amount", "old": 15048, "new": 25048},
            {"source": "rounds/round-02.md", "month": "2026-09", "field": "operating_cost", "old": 138000, "new": 208000},
        ]
    return [{"source": "rounds/round-03.md", "month": "2026-10", "field": "entire_row", "old": None,
             "new": {"orders": 640, "gross_revenue": 224000, "refund_amount": 11200,
                     "operating_cost": 142000, "sessions": 5900}, "status": "appended"},
            {"source": "rounds/round-02.md", "month": "2026-08", "field": "refund_amount", "old": 15048, "new": 25048, "status": "retained"},
            {"source": "rounds/round-02.md", "month": "2026-09", "field": "operating_cost", "old": 138000, "new": 208000, "status": "retained"}]


def conclusion_for(round_no: int, months: list[dict], totals: dict) -> dict:
    if round_no == 1:
        june = next(item for item in months if item["month"] == "2026-06")
        may = next(item for item in months if item["month"] == "2026-05")
        delta = june["net_revenue"] - may["net_revenue"]
        text = f"4—9月累计净收入 {money(totals['net_revenue'])} 元；6月净收入环比减少 {money(abs(delta))} 元。"
        refs = [{"metric": "period_net_revenue", "value": totals["net_revenue"]},
                {"metric": "june_net_revenue_change", "value": delta, "from_month": "2026-05", "to_month": "2026-06"}]
    elif round_no == 2:
        september = next(item for item in months if item["month"] == "2026-09")
        text = f"财务更正后，9月经营利润为 {money(september['operating_profit'])} 元，首次转负；期间累计利润 {money(totals['operating_profit'])} 元。"
        refs = [{"metric": "september_operating_profit", "value": september["operating_profit"]},
                {"metric": "period_operating_profit", "value": totals["operating_profit"]}]
    else:
        october = months[-1]
        negative = [item["month"] for item in months if item["operating_profit"] < 0]
        text = f"10月净收入 {money(october['net_revenue'])} 元、利润 {money(october['operating_profit'])} 元；9月仍为唯一亏损月。"
        refs = [{"metric": "october_net_revenue", "value": october["net_revenue"]},
                {"metric": "october_operating_profit", "value": october["operating_profit"]},
                {"metric": "negative_profit_months", "value": negative}]
    return {"text": text, "references": refs, "basis": "仅引用当前轮未舍入计算值；展示金额按十进制四舍五入。"}


def computed_data(round_no: int, months: list[dict], totals: dict, axis: dict, conclusion: dict) -> dict:
    return {"schema_version": 1, "task_id": TASK, "path_base": "output_dir", "round": round_no,
            "source": {"path_base": "suite_root", "path": rp(INPUT), "sha256": sha(INPUT), "modified": False},
            "applied_changes": applied_changes(round_no),
            "formulas": {"net_revenue": "gross_revenue - refund_amount", "operating_profit": "net_revenue - operating_cost",
                         "refund_rate": "refund_amount / gross_revenue", "conversion_rate": "orders / sessions",
                         "period_rates": "期间分子总计 / 期间分母总计", "rounding": "Decimal ROUND_HALF_UP；计算与图形比例使用未舍入值"},
            "units": {"money": "元", "orders": "笔", "sessions": "次", "rates": "ratio"},
            "months": months, "totals": totals, "axes": axis, "conclusion": conclusion,
            "display_rules": {"monthly_money": "整数元，千分位", "kpi_money": "万元，两位小数，标签明确万元",
                              "percentages": "两位小数", "body_minimum_font_px": 22}}


def regions() -> list[dict]:
    return [
        {"id": "header", "box": [48, 36, 1552, 144], "font_size": 42, "color": "#0F172A", "style": "品牌行、标题与期间"},
        {"id": "kpi_net", "box": [48, 176, 412, 314], "font_size": 22, "color": "#0F172A", "style": "总净收入·万元"},
        {"id": "kpi_profit", "box": [428, 176, 792, 314], "font_size": 22, "color": "#0F172A", "style": "总经营利润·万元"},
        {"id": "kpi_orders", "box": [808, 176, 1172, 314], "font_size": 22, "color": "#0F172A", "style": "总订单"},
        {"id": "kpi_conversion", "box": [1188, 176, 1552, 314], "font_size": 22, "color": "#0F172A", "style": "总体转化率"},
        {"id": "conclusion", "box": [48, 336, 1552, 404], "font_size": 26, "color": "#0F172A", "style": "仅基于当前数值的主结论"},
        {"id": "chart", "box": [48, 432, 944, 948], "font_size": 22, "color": "#334155", "style": "净收入/利润共用零起点柱图",
         "axis": {"plot": [160, 548, 920, 872], "round_dependent": True}},
        {"id": "table", "box": [968, 432, 1552, 948], "font_size": 22, "color": "#334155", "style": "月份/净收入/利润/退款率/转化率"},
    ]


def layout_map(round_no: int) -> dict:
    comparison = []
    if round_no > 1:
        previous = json.loads((HERE / f"round-{round_no-1:02d}" / "v001" / "layout-map.json").read_text(encoding="utf-8"))
        old = {item["id"]: item["box"] for item in previous["regions"]}
        for item in regions():
            before = old[item["id"]]
            delta = [item["box"][i] - before[i] for i in range(4)]
            comparison.append({"region_id": item["id"], "previous_box": before, "current_box": item["box"],
                               "component_delta": delta, "max_abs_delta": max(abs(v) for v in delta),
                               "passed": max(abs(v) for v in delta) <= 2})
    return {"schema_version": 1, "task_id": TASK, "path_base": "output_dir", "round": round_no,
            "canvas": [1600, 1000], "coordinate_system": "左上原点，x向右，y向下，像素；框为[left,top,right,bottom]",
            "regions": regions(), "comparison": comparison,
            "body_minimum_font_px": 22,
            "internal_layout": {"table_header": [992, 504, 1528, 552], "table_row_height": 52,
                                "chart_plot": [160, 548, 920, 872], "chart_group_labels_y": 884,
                                "note": "三、七个月仅改变内部柱组与表格行距；所有主区域边界不变。"}}


def build_dsl(round_no: int, months: list[dict], totals: dict, axis: dict, conclusion: dict) -> str:
    children = [sk.box(0, 0, 1600, 1000, "#F3F6FA")]
    children += [sk.label("NORTHSTAR  /  经营驾驶舱", 48, 42, 600, 34, 22, "#2563EB", True),
                 sk.label("月度经营表现", 48, 78, 760, 58, 42, "#0F172A", True),
                 sk.label(f"{totals['period']}  ·  {totals['month_count']}个月", 1050, 78, 502, 44, 24, "#475569", False, "RIGHT"),
                 sk.box(48, 144, 1504, 2, "#D9E2EC")]
    cards = [
        ("总净收入 · 万元", wan(totals["net_revenue"]), "退款前收入 − 退款", "#2563EB"),
        ("总经营利润 · 万元", wan(totals["operating_profit"]), "净收入 − 经营成本", "#D97706"),
        ("总订单", money(totals["orders"]) + " 笔", f"{totals['month_count']}个月订单合计", "#0F766E"),
        ("总体转化率", q2(totals["orders"], totals["sessions"]) + "%", "总订单 ÷ 总访问", "#7C3AED"),
    ]
    for x, (title, value, note, accent) in zip((48, 428, 808, 1188), cards):
        children += [sk.box(x, 176, 364, 138, "#FFFFFF", 14, "#DCE3EC"),
                     sk.box(x, 176, 7, 138, accent, 4),
                     sk.label(title, x + 24, 192, 316, 34, 22, "#475569"),
                     sk.label(value, x + 24, 226, 316, 50, 36, "#0F172A", True),
                     sk.label(note, x + 24, 278, 316, 30, 22, "#64748B")]
    children += [sk.box(48, 336, 1504, 68, "#E8F0FE", 12),
                 sk.label("本期结论", 68, 354, 132, 34, 22, "#1D4ED8", True),
                 sk.label(conclusion["text"], 220, 350, 1308, 42, 26, "#0F172A", True)]
    children += [sk.box(48, 432, 896, 516, "#FFFFFF", 14, "#DCE3EC"),
                 sk.box(968, 432, 584, 516, "#FFFFFF", 14, "#DCE3EC"),
                 sk.label("净收入与经营利润", 72, 450, 420, 38, 28, "#0F172A", True),
                 sk.label("共用零起点 · 单位：万元", 492, 456, 424, 32, 22, "#64748B", False, "RIGHT"),
                 sk.box(74, 504, 18, 18, "#2563EB", 3), sk.label("净收入", 100, 498, 100, 34, 22, "#334155"),
                 sk.box(216, 504, 18, 18, "#D97706", 3), sk.label("经营利润", 242, 498, 140, 34, 22, "#334155"),
                 sk.label("万元", 72, 520, 84, 30, 22, "#64748B")]
    plot_left, plot_top, plot_right, plot_bottom = axis["plot_box"]
    scale = (plot_bottom - plot_top) / (axis["y_max"] - axis["y_min"])
    zero_y = plot_bottom - (0 - axis["y_min"]) * scale
    for tick in axis["ticks"]:
        y = plot_bottom - (tick - axis["y_min"]) * scale
        color = "#64748B" if tick == 0 else "#E2E8F0"
        children.append(sk.line(plot_left, y, plot_right, y, color, 2 if tick == 0 else 1))
        tick_text = "0" if tick == 0 else f"{tick // 10000:+d}" if tick < 0 else str(tick // 10000)
        children.append(sk.label(tick_text, 76, y - 16, 72, 34, 22, "#475569", False, "RIGHT"))
    group_width = (plot_right - plot_left) / len(months)
    bar_width = min(34, group_width * 0.30)
    for index, item in enumerate(months):
        center = plot_left + group_width * (index + 0.5)
        for offset, key, color in ((-bar_width - 3, "net_revenue", "#2563EB"), (3, "operating_profit", "#D97706")):
            value = item[key]
            height = abs(value) * scale
            x = center + offset - bar_width / 2
            y = zero_y - height if value >= 0 else zero_y
            children.append(sk.box(x, y, bar_width, max(height, 1), color, 4))
        children.append(sk.label(item["month"], center - group_width / 2, 884, group_width, 34, 22, "#334155", False, "CENTER"))
    children += [sk.label("月度明细", 992, 450, 300, 38, 28, "#0F172A", True),
                 sk.label("金额：元  ·  比率：%", 1230, 456, 298, 32, 22, "#64748B", False, "RIGHT")]
    columns = [("月份", 132), ("净收入", 130), ("利润", 120), ("退款率", 100), ("转化率", 102)]
    x = 992
    for title, width in columns:
        children.append(sk.label(title, x, 504, width, 48, 22, "#475569", True, "LEFT" if title == "月份" else "RIGHT"))
        x += width
    children.append(sk.box(992, 552, 536, 2, "#CBD5E1"))
    for row_index, item in enumerate(months):
        y = 554 + row_index * 52
        if row_index % 2 == 0:
            children.append(sk.box(984, y - 2, 552, 50, "#F8FAFC", 4))
        values = [item["month"], money(item["net_revenue"]), money(item["operating_profit"]),
                  item["refund_rate"]["display"] + "%", item["conversion_rate"]["display"] + "%"]
        x = 992
        for column_index, ((_, width), value) in enumerate(zip(columns, values)):
            color = "#B91C1C" if column_index == 2 and item["operating_profit"] < 0 else "#334155"
            children.append(sk.label(value, x, y, width, 48, 22, color, column_index == 0,
                                     "LEFT" if column_index == 0 else "RIGHT"))
            x += width
    return sk.snapshot(1600, 1000, children, "#F3F6FA")


def prepare(round_no: int) -> None:
    guard(round_no)
    if round_no == 1:
        sk.begin_task(RUN, TASK)
    months = load_months(round_no)
    totals = totals_for(months)
    axis = axis_for(months)
    conclusion = conclusion_for(round_no, months, totals)
    directory = HERE / f"round-{round_no:02d}" / "v001"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "dashboard.snapshot").write_text(build_dsl(round_no, months, totals, axis, conclusion), encoding="utf-8")
    sk.write_json(directory / "computed-data.json", computed_data(round_no, months, totals, axis, conclusion))
    sk.write_json(directory / "layout-map.json", layout_map(round_no))
    sk.write_json(directory / "timing.json", {"started_at": sk.iso()})
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    state["current_round"] = f"round-{round_no:02d}"
    sk.write_json(STATE_PATH, state)
    sk.checkpoint(RUN, f"{TASK}-round-{round_no:02d}-start")
    print(json.dumps({"prepared": TASK, "round": round_no, "months": len(months), "totals": totals}, ensure_ascii=False))


def execute(round_no: int, version: str) -> None:
    directory = HERE / f"round-{round_no:02d}" / version
    source = directory / "dashboard.snapshot"
    response, record = sk.request(RUN, TASK, "render", sk.BASE + "/snapshot", source.read_bytes(),
                                  "text/plain; charset=utf-8", version_id=f"round-{round_no:02d}-{version}", case_id="dashboard")
    if record["http_status"] != 200 or not response.startswith(b"\x89PNG\r\n\x1a\n"):
        raise RuntimeError(record)
    png = directory / "dashboard.png"
    png.write_bytes(response)
    with Image.open(png) as image:
        assert image.size == (1600, 1000)
    print(json.dumps({"request_id": record["request_id"], "image": rp(png), "sha256": sha(png)}, ensure_ascii=False))


def provenance(png: Path, dsl: Path) -> dict:
    png_hash = sha(png)
    dsl_normalized = hashlib.sha256(dsl.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    for request in sk.read_jsonl(HERE / "requests.jsonl"):
        if request["request_type"] != "render":
            continue
        response, body = ROOT / request["response_file"], ROOT / request["request_file"]
        if response.exists() and body.exists() and sha(response) == png_hash and hashlib.sha256(body.read_bytes().replace(b"\r\n", b"\n")).hexdigest() == dsl_normalized:
            return {"request_id": request["request_id"], "request_file": request["request_file"],
                    "response_file": request["response_file"], "http_status": request["http_status"],
                    "content_type": request["content_type"], "png_sha256": png_hash,
                    "dsl_sha256": hashlib.sha256(dsl.read_bytes()).hexdigest(),
                    "png_byte_identical_to_response": True, "dsl_matches_submitted_utf8": True}
    raise AssertionError("final provenance not found")


def data_checks(round_no: int, data: dict, previous: dict | None) -> list[dict]:
    months, totals, axis = data["months"], data["totals"], data["axes"]
    checks = []
    for item in months:
        checks.append({"check": f"month_formula:{item['month']}", "passed": item["net_revenue"] == item["gross_revenue"] - item["refund_amount"] and item["operating_profit"] == item["net_revenue"] - item["operating_cost"], "method": "整数金额公式逐月复算"})
    checks.append({"check": "period_totals", "passed": all(totals[key] == sum(item[key] for item in months) for key in ("gross_revenue", "refund_amount", "operating_cost", "net_revenue", "operating_profit", "orders", "sessions")), "method": "七项期间总量逐项求和复算"})
    checks.append({"check": "weighted_rates", "passed": totals["conversion_rate"]["numerator"] == totals["orders"] and totals["conversion_rate"]["denominator"] == totals["sessions"] and totals["refund_rate"]["denominator"] == totals["gross_revenue"], "method": "总体率使用期间总量相除"})
    checks.append({"check": "axis_contains_values", "passed": axis["y_min"] <= min(axis["value_min"], 0) and axis["y_max"] >= max(axis["value_max"], 0), "method": "未舍入柱值全部位于共同纵轴范围内"})
    if previous:
        retained = [item for item in previous["months"] if item["month"] != "2026-10"]
        current = {item["month"]: item for item in months}
        unchanged = all(current[item["month"]][key] == item[key] for item in retained for key in ("orders", "gross_revenue", "refund_amount", "operating_cost", "sessions"))
        checks.append({"check": "prior_corrections_and_rows_retained", "passed": unchanged and len(months) >= len(previous["months"]), "method": "与上一轮逐月原始字段比较"})
    return checks


def change_audit(round_no: int, data: dict, review: dict) -> dict:
    previous = json.loads((OUTPUT / f"round-{round_no-1:02d}" / "computed-data.json").read_text(encoding="utf-8"))
    current_months = {item["month"]: item for item in data["months"]}
    old_months = {item["month"]: item for item in previous["months"]}
    changes = []
    if round_no == 2:
        specs = [("2026-08", "refund_amount", 15048, 25048), ("2026-09", "operating_cost", 138000, 208000)]
    else:
        specs = [("2026-10", "entire_row", None, {key: current_months["2026-10"][key] for key in ("orders", "gross_revenue", "refund_amount", "operating_cost", "sessions")})]
    for month, field, old, new in specs:
        if field == "entire_row":
            propagation = ["新增月份净收入212800、利润70800及两项月度率", "KPI期间汇总与总体转化率", "柱图新增一组、表格新增一行", "结论最后月份改为2026-10"]
            old_values = None
            new_values = new
        else:
            before, after = old_months[month], current_months[month]
            affected = "net_revenue" if field == "refund_amount" else "operating_profit"
            old_values = {field: old, affected: before[affected]}
            new_values = {field: new, affected: after[affected]}
            if month == "2026-08":
                propagation = ["8月净收入与利润各减少10000元", "KPI汇总、8月双柱、表格与结论", "经营利润仍为正"]
            else:
                propagation = ["9月利润由64368元变为-5632元", "共同纵轴新增-20000元负刻度", "KPI汇总、9月利润柱、表格与结论"]
            if field == "refund_amount":
                propagation.append("8月退款率由8.00%精确值更新为13.31%展示值")
        changes.append({"month": month, "field": field, "old": old_values, "new": new_values,
                        "propagation": propagation,
                        "output_locations": [f"round-{round_no:02d}/dashboard.png", f"round-{round_no:02d}/computed-data.json", f"round-{round_no:02d}/layout-map.json"]})
    layout = json.loads((OUTPUT / f"round-{round_no:02d}" / "layout-map.json").read_text(encoding="utf-8"))
    regression = data_checks(round_no, data, previous)
    regression += [
        {"check": "main_region_bounds", "passed": all(item["max_abs_delta"] <= 2 for item in layout["comparison"]), "method": "逐区域四边界与上一轮比较，容差±2px", "evidence": f"round-{round_no:02d}/layout-map.json"},
        {"check": "actual_image_review", "passed": review["completed"], "method": "实际打开最终服务PNG并核对内容、表格、柱图、负值、坐标与结论", "evidence": review["views"]},
        {"check": "provenance", "passed": True, "method": "最终PNG与原始响应字节一致，DSL与UTF-8请求一致", "evidence": rp(HERE / f"round-{round_no:02d}" / "v001" / "provenance.json")},
    ]
    return {"schema_version": 1, "task_id": TASK, "path_base": "output_dir", "round": round_no,
            "baseline": {"round": round_no - 1, "png": f"round-{round_no-1:02d}/dashboard.png", "dsl": f"round-{round_no-1:02d}/dashboard.snapshot", "computed_data": f"round-{round_no-1:02d}/computed-data.json"},
            "changes": changes,
            "preserved": [{"item": "画布与八个主区域", "evidence": "layout-map.json comparison所有分量差为0"},
                          {"item": "字体与视觉系统", "evidence": "Noto Sans CJK SC；主标题42px、正文不低于22px；配色与卡片/图表样式不变"},
                          {"item": "历史月份和上一轮更正", "evidence": "逐月原始字段回归检查"},
                          {"item": "原始CSV", "evidence": rp(INPUT) + " 未被修改"}],
            "regression": regression}


def round_metrics(round_no: int, version: str, ended_at: str) -> dict:
    prefix = f"round-{round_no:02d}-"
    requests = [item for item in sk.read_jsonl(HERE / "requests.jsonl") if str(item.get("version_id", "")).startswith(prefix)]
    iterations = [item for item in sk.read_jsonl(HERE / "iterations.jsonl") if str(item.get("version_id", "")).startswith(prefix)]
    timing = json.loads((HERE / f"round-{round_no:02d}" / "v001" / "timing.json").read_text(encoding="utf-8"))
    return {"schema_version": 1, "path_base": "suite_root", "task_id": TASK, "run_id": RUN,
            "task_round": f"round-{round_no:02d}", "status": "completed", "started_at": timing["started_at"], "ended_at": ended_at,
            "wall_clock_seconds": round((sk.dt.datetime.fromisoformat(ended_at) - sk.dt.datetime.fromisoformat(timing["started_at"])).total_seconds(), 3),
            "snapshot_requests": len(requests), "successful_snapshot_requests": sum(item["http_status"] == 200 for item in requests),
            "failed_snapshot_requests": sum(item["http_status"] != 200 for item in requests), "retry_requests": sum(item["is_retry"] for item in requests),
            "request_elapsed_seconds_sum": round(sum(item["elapsed_seconds"] for item in requests), 3),
            "image_views": sum(str(item.get("image_path", "")).endswith(".png") for item in iterations),
            "completed_visual_iterations": sum(item["type"] in {"baseline", "visual", "requirement-change"} and item["completed_visual_iteration"] for item in iterations),
            "incomplete_visual_iterations": sum(item["type"] in {"baseline", "visual", "requirement-change"} and not item["completed_visual_iteration"] for item in iterations),
            "final_pngs": 1, "logs": {"requests": rp(HERE / "requests.jsonl"), "iterations": rp(HERE / "iterations.jsonl")},
            "scope": "仅本轮请求、查看与迭代；root task-metrics.json汇总三轮，不重复累计。"}


def record_review(round_no: int, version: str, review: dict) -> None:
    existing = {item["iteration_id"] for item in sk.read_jsonl(HERE / "iterations.jsonl")}
    iteration_id = f"{RUN}-{TASK}-round-{round_no:02d}-dashboard"
    if iteration_id in existing:
        return
    viewed = review["reviewed"]["dashboard"]
    sk.append_jsonl(HERE / "iterations.jsonl", {
        "iteration_id": iteration_id, "task_id": TASK, "case_id": "dashboard", "version_id": f"round-{round_no:02d}-{version}",
        "parent_version": f"round-{round_no-1:02d}-v001" if round_no > 1 else None,
        "type": "baseline" if round_no == 1 else "requirement-change", "image_path": viewed["image"], "image_paths": [viewed["image"]],
        "viewed_at": viewed["viewed_at"], "timezone": "+08:00", "observable_issues": viewed["observed"],
        "changes": review["change_summary"], "review_and_comparison": review["conclusion"], "completed_visual_iteration": True,
    })


def finalize_round(review_file: str, round_no: int, version: str) -> None:
    guard(round_no)
    review = json.loads(Path(review_file).read_text(encoding="utf-8"))
    if not review.get("completed") or set(review.get("reviewed", {})) != {"dashboard"}:
        raise SystemExit("completed dashboard review required")
    source = HERE / f"round-{round_no:02d}" / version
    target = OUTPUT / f"round-{round_no:02d}"
    target.mkdir(parents=True, exist_ok=True)
    for suffix in ("png", "snapshot"):
        shutil.copyfile(source / f"dashboard.{suffix}", target / f"dashboard.{suffix}")
    proof = provenance(target / "dashboard.png", target / "dashboard.snapshot")
    sk.write_json(source / "provenance.json", proof)
    data = json.loads((source / "computed-data.json").read_text(encoding="utf-8"))
    layout = json.loads((source / "layout-map.json").read_text(encoding="utf-8"))
    assert all(item["passed"] for item in data_checks(round_no, data, None))
    assert not layout["comparison"] or all(item["passed"] for item in layout["comparison"])
    sk.write_json(target / "computed-data.json", data)
    sk.write_json(target / "layout-map.json", layout)
    files = ["dashboard.png", "dashboard.snapshot", "computed-data.json", "layout-map.json"]
    if round_no > 1:
        audit = change_audit(round_no, data, review)
        sk.write_json(target / "change-audit.json", audit)
        files.append("change-audit.json")
    record_review(round_no, version, review)
    ended = sk.iso()
    sk.write_json(target / "task-metrics.json", round_metrics(round_no, version, ended))
    checks = [
        ("data", "逐月公式、期间汇总、加权率、未舍入图形值及ROUND_HALF_UP展示均由computed-data.json复算。"),
        ("layout", "1600×1000；八个主区域边界稳定；正文不低于22px；六/七个月完整显示。"),
        ("chart", "净收入与经营利润共用零起点纵轴；负利润保留并增加负刻度，未裁切或改成正值。"),
        ("table", "月份、净收入、利润、退款率、转化率逐行对应当前轮数据，金额整数元、百分比两位小数。"),
        ("visual", "最终服务PNG已实际查看，标题、KPI、柱图、表格和结论无碰撞或信息遗漏。"),
    ]
    if round_no > 1:
        checks.append(("regression", "change-audit.json记录旧新值、传播位置、保留项、区域±2px、数值与真实图像回归。"))
    sk.write_usage(RUN, TASK, "completed", checks,
                   "浅色经营仪表盘：四张KPI卡、单一结论带、左侧共享零轴双柱图、右侧高密度明细表；金额与计数分层显示。",
                   review["change_summary"], [f"round-{round_no:02d}/{name}" for name in files])
    report = target / "snapshot-usage.md"
    shutil.copyfile(OUTPUT / "snapshot-usage.md", report)
    report.write_text(report.read_text(encoding="utf-8").replace(f"# {TASK} Snapshot", f"# {TASK} round-{round_no:02d} Snapshot", 1), encoding="utf-8")
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    task = next(item for item in state["tasks"] if item["id"] == TASK)
    task.setdefault("completed_rounds", [])
    label = f"round-{round_no:02d}"
    if label not in task["completed_rounds"]:
        task["completed_rounds"].append(label)
    task["artifacts"] = sorted(set(task.get("artifacts", []) + [rp(target / name) for name in files] + [rp(target / "snapshot-usage.md"), rp(target / "task-metrics.json")]))
    state["current_round"] = None if round_no == 3 else f"round-{round_no+1:02d}"
    sk.write_json(STATE_PATH, state)
    sk.checkpoint(RUN, f"{TASK}-round-{round_no:02d}-finish")
    print(json.dumps({"round_completed": round_no, "files": files}, ensure_ascii=False))


def finalize_task(review_file: str) -> None:
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    task = next(item for item in state["tasks"] if item["id"] == TASK)
    assert task.get("completed_rounds") == ["round-01", "round-02", "round-03"]
    review = json.loads(Path(review_file).read_text(encoding="utf-8"))
    assert review.get("completed")
    files = [rp(path) for path in sorted(OUTPUT.rglob("*")) if path.is_file()]
    sk.write_usage(RUN, TASK, "completed", [
        ("rounds", "round-01、round-02、round-03按预置需求连续执行，三轮完整保留。"),
        ("corrections", "第二轮两项财务更正持续有效；第三轮新增2026-10且未恢复旧值。"),
        ("propagation", "每月、汇总、四KPI、双柱、表格与主结论均由当前轮未舍入值重新计算。"),
        ("regression", "主区域边界逐轮比较均为0px差；数值公式、轴范围、历史行和实际图像检查通过。"),
        ("mode", "预置连续执行模式；未来需求可提前访问，不声称隐藏反馈盲测。"),
    ], "同一驾驶舱视觉系统贯穿三轮；通过稳定主区域和可重排内部柱组/行距容纳六个月到七个月。",
       "首轮建立数据与布局；第二轮将8月退款改为25048元、9月成本改为208000元并显示负利润；第三轮新增10月并保留前轮更正。",
       files)
    sk.metrics(RUN, TASK)
    sk.finish_task(RUN, TASK, files, [rp(HERE / "final-review.json")], rounds=task["completed_rounds"])
    sk.metrics(RUN, TASK)
    sk.checkpoint(RUN, f"{TASK}-finish")
    print(json.dumps({"completed": TASK, "artifacts": len(files)}, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["prepare", "execute", "finalize-round", "finalize-task"])
    parser.add_argument("--round", type=int, default=1)
    parser.add_argument("--version", default="v001")
    parser.add_argument("--review-file")
    args = parser.parse_args()
    if args.mode == "prepare":
        prepare(args.round)
    elif args.mode == "execute":
        execute(args.round, args.version)
    elif args.mode == "finalize-round":
        finalize_round(args.review_file, args.round, args.version)
    else:
        finalize_task(args.review_file)


if __name__ == "__main__":
    main()
