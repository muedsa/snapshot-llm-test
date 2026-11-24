from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import suitekit as s


def build_dsl(rows: list[dict], totals: dict) -> str:
    c = []
    c.append(s.label("NORTHSTAR  /  经营诊断", 40, 28, 500, 26, 18, "#52627A", True))
    c.append(s.label("六个月增长复盘", 40, 57, 700, 52, 38, "#13233A", True))
    c.append(s.label("2026-04 — 2026-09  ·  金额单位：元", 790, 72, 770, 30, 20, "#52627A", False, "RIGHT"))
    kpis = [
        ("总净收入", f'{totals["net_revenue"]:,}', "退款后收入", "#176B87"),
        ("总经营利润", f'{totals["profit"]:,}', f'利润率 {totals["profit"] / totals["net_revenue"]:.2%}', "#13795B"),
        ("总订单", f'{totals["orders"]:,}', f'访问 {totals["sessions"]:,} 次', "#6C56B5"),
        ("期间总体转化率", f'{totals["conversion"]:.2%}', "总订单 ÷ 总访问", "#B86519"),
    ]
    for i, (name, value, note, color) in enumerate(kpis):
        x = 40 + i * 385
        c.append(s.box(x, 132, 365, 124, "#FFFFFF", 16, "#DDE5EF"))
        c.append(s.box(x, 132, 7, 124, color, 4))
        c.append(s.label(name, x + 24, 148, 315, 28, 20, "#52627A"))
        c.append(s.label(value, x + 24, 177, 315, 46, 34, color, True))
        c.append(s.label(note, x + 24, 224, 315, 24, 16, "#718096"))
    c.append(s.box(40, 278, 900, 338, "#FFFFFF", 16, "#DDE5EF"))
    c.append(s.label("收入与利润走势", 64, 296, 450, 30, 24, "#172033", True))
    c.append(s.box(664, 303, 18, 18, "#1D7FA3", 3))
    c.append(s.label("净收入", 690, 298, 92, 28, 18, "#52627A"))
    c.append(s.box(790, 303, 18, 18, "#9CCFB1", 3))
    c.append(s.label("经营利润", 816, 298, 105, 28, 18, "#52627A"))
    plot_x, plot_y, plot_w, plot_h = 128, 351, 766, 198
    zero_y = plot_y + plot_h
    maxv = 240000
    for tick in range(0, 240001, 60000):
        y = zero_y - tick / maxv * plot_h
        c.append(s.line(plot_x, y, plot_x + plot_w, y, "#E4EAF1", 1))
        c.append(s.label(f"{tick // 10000}万" if tick else "0", 55, y - 12, 62, 24, 16, "#718096", False, "RIGHT"))
    step = plot_w / 6
    for i, row in enumerate(rows):
        center = plot_x + step * (i + 0.5)
        net_h = row["net_revenue"] / maxv * plot_h
        profit_h = row["profit"] / maxv * plot_h
        c.append(s.box(center - 42, zero_y - net_h, 30, net_h, "#1D7FA3", 4))
        c.append(s.box(center - 8, zero_y - profit_h, 30, profit_h, "#9CCFB1", 4))
        c.append(s.label(row["month"][5:], center - 48, 561, 96, 25, 18, "#52627A", False, "CENTER"))
        c.append(s.label(f'{row["profit"] / 10000:.1f}万', center - 43, zero_y - profit_h - 25, 100, 23, 16, "#13795B", True, "CENTER"))
    c.append(s.label("零起点 · 两组柱共用 0—24 万元线性比例", 64, 587, 830, 22, 16, "#718096"))
    c.append(s.box(960, 278, 600, 338, "#FFFFFF", 16, "#DDE5EF"))
    c.append(s.label("访问量", 984, 294, 150, 28, 22, "#172033", True))
    c.append(s.label("次 / 月", 1434, 297, 102, 24, 16, "#718096", False, "RIGHT"))
    sx, sw, sy, sh = 1040, 490, 334, 92
    for tick in (0, 3000, 6000):
        y = sy + sh - tick / 6000 * sh
        c.append(s.line(sx, y, sx + sw, y, "#E8EDF3", 1))
        c.append(s.label(str(tick), 975, y - 11, 55, 22, 16, "#718096", False, "RIGHT"))
    sstep = sw / 6
    points = []
    for i, row in enumerate(rows):
        x = sx + sstep * (i + 0.5)
        y = sy + sh - row["sessions"] / 6000 * sh
        points.append((x, y))
        c.append(s.circle(x, y, 5, "#1D7FA3"))
        c.append(s.label(str(row["sessions"]), x - 43, y - 27, 86, 21, 16, "#176B87", True, "CENTER"))
    for a, b in zip(points, points[1:]):
        c.append(s.line(a[0], a[1], b[0], b[1], "#1D7FA3", 3))
    for i, row in enumerate(rows):
        x = sx + sstep * (i + 0.5)
        c.append(s.label(row["month"][5:], x - 30, 431, 60, 22, 16, "#52627A", False, "CENTER"))
    c.append(s.line(984, 462, 1536, 462, "#E4EAF1", 1))
    c.append(s.label("转化率", 984, 472, 150, 28, 22, "#172033", True))
    c.append(s.label("% / 月", 1434, 475, 102, 24, 16, "#718096", False, "RIGHT"))
    cy, ch = 510, 63
    for tick in (0, 5, 10, 15):
        y = cy + ch - tick / 15 * ch
        c.append(s.line(sx, y, sx + sw, y, "#E8EDF3", 1))
        c.append(s.label(f"{tick}%", 975, y - 11, 55, 22, 16, "#718096", False, "RIGHT"))
    points = []
    for i, row in enumerate(rows):
        x = sx + sstep * (i + 0.5)
        y = cy + ch - row["conversion"] * 100 / 15 * ch
        points.append((x, y))
        c.append(s.circle(x, y, 5, "#C77A2B"))
        c.append(s.label(f'{row["conversion"]:.2%}', x - 42, y - 25, 84, 21, 16, "#A85D18", True, "CENTER"))
    for a, b in zip(points, points[1:]):
        c.append(s.line(a[0], a[1], b[0], b[1], "#C77A2B", 3))
    for i, row in enumerate(rows):
        x = sx + sstep * (i + 0.5)
        c.append(s.label(row["month"][5:], x - 30, 579, 60, 22, 16, "#52627A", False, "CENTER"))
    c.append(s.box(40, 636, 940, 324, "#FFFFFF", 16, "#DDE5EF"))
    c.append(s.label("月度经营明细", 64, 652, 400, 30, 24, "#172033", True))
    cols = [(64, 130, "月份", "LEFT"), (214, 190, "净收入（元）", "RIGHT"), (424, 150, "退款率", "RIGHT"), (594, 170, "利润（元）", "RIGHT"), (784, 172, "转化率", "RIGHT")]
    c.append(s.box(64, 691, 892, 36, "#EFF4F8", 6))
    for x, w, name, align in cols:
        c.append(s.label(name, x, 696, w, 26, 18, "#52627A", True, align))
    for i, row in enumerate(rows):
        y = 731 + i * 35
        if i % 2:
            c.append(s.box(64, y - 2, 892, 34, "#F8FAFC", 4))
        values = [row["month"], f'{row["net_revenue"]:,}', f'{row["refund_rate"]:.2%}', f'{row["profit"]:,}', f'{row["conversion"]:.2%}']
        for (x, w, _, align), value in zip(cols, values):
            c.append(s.label(value, x, y, w, 27, 20, "#172033", i == 5, align))
    c.append(s.box(1000, 636, 560, 324, "#132B3A", 16))
    c.append(s.label("管理结论", 1028, 658, 250, 30, 22, "#7ED9C3", True))
    c.append(s.label("增长有效，退款治理要跟上", 1028, 700, 500, 38, 27, "#FFFFFF", True))
    c.append(s.label("9月经营利润 64,368 元，较4月增长 70.7%；净收入增长 69.1%。", 1028, 750, 500, 68, 21, "#D7E5EC"))
    c.append(s.label("但6月与8月退款率均达 8.00%，明显高于4月的 5.00%。优先排查这两个月的退款集中原因。", 1028, 824, 500, 86, 21, "#D7E5EC"))
    c.append(s.label("依据：月度明细；期间总体转化率为 3,045 ÷ 27,300。", 40, 976, 1520, 20, 16, "#718096"))
    return s.snapshot(1600, 1000, c)


def main() -> None:
    run_id, _, _ = s.init_suite()
    s.begin_task(run_id, "A01")
    task_dir = s.ROOT / "tasks" / "A01-operations-dashboard"
    with (task_dir / "inputs" / "monthly.csv").open(encoding="utf-8", newline="") as stream:
        raw = list(csv.DictReader(stream))
    rows = []
    for item in raw:
        gross, refund, cost = (int(item[key]) for key in ("gross_revenue", "refund_amount", "operating_cost"))
        net = gross - refund
        profit = net - cost
        rows.append({
            "month": item["month"], "orders": int(item["orders"]), "gross_revenue": gross,
            "refund_amount": refund, "operating_cost": cost, "sessions": int(item["sessions"]),
            "net_revenue": net, "profit": profit, "refund_rate": refund / gross,
            "conversion": int(item["orders"]) / int(item["sessions"]),
        })
    keys = ("orders", "gross_revenue", "refund_amount", "operating_cost", "sessions", "net_revenue", "profit")
    totals = {key: sum(row[key] for row in rows) for key in keys}
    totals["conversion"] = totals["orders"] / totals["sessions"]
    totals["refund_rate"] = totals["refund_amount"] / totals["gross_revenue"]
    growth_profit = rows[-1]["profit"] / rows[0]["profit"] - 1
    growth_net = rows[-1]["net_revenue"] / rows[0]["net_revenue"] - 1
    assert round(growth_profit, 4) == 0.7074
    assert round(growth_net, 4) == 0.6906
    conclusion = "9月经营利润 64,368 元，较4月增长 70.7%；净收入增长 69.1%。但6月与8月退款率均达 8.00%，明显高于4月的 5.00%。优先排查这两个月的退款集中原因。"
    audit = s.audit_identity("A01")
    audit.update({
        "months": rows, "totals": totals,
        "axes": [
            {"chart": "net_profit_grouped_bars", "unit": "元", "minimum": 0, "maximum": 240000, "zero_line_y": 549, "plot_box": [128, 351, 894, 549], "mapping": "y=549-value/240000*198", "series": ["net_revenue", "profit"], "shared_scale": True},
            {"chart": "sessions", "unit": "次", "minimum": 0, "maximum": 6000, "plot_box": [1040, 334, 1530, 426], "mapping": "y=426-value/6000*92"},
            {"chart": "conversion", "unit": "比例", "minimum": 0, "maximum": 0.15, "plot_box": [1040, 510, 1530, 573], "mapping": "y=573-value/0.15*63"},
        ],
        "conclusion": {"text": conclusion, "references": {"profit_september": rows[-1]["profit"], "profit_april": rows[0]["profit"], "profit_growth": growth_profit, "net_growth": growth_net, "refund_rate_june": rows[2]["refund_rate"], "refund_rate_august": rows[4]["refund_rate"], "refund_rate_april": rows[0]["refund_rate"]}},
    })
    output, temp = s.task_dirs(run_id, "A01")
    s.write_json(output / "computed-data.json", audit)
    dsl = build_dsl(rows, totals)
    image, record = s.render(run_id, "A01", dsl, "operations", "v002", final=False)
    s.record_iteration(run_id, "A01", "v002", image, "baseline", "首轮图形可见但文字因误用 Text.height 行高属性被裁切", "移除像素 height，改由 Positioned 提供布局高度", "修复后须查看文字、对齐与溢出")
    s.write_json(temp / "baseline-record.json", record)
    print(image)
    print(json.dumps(totals, ensure_ascii=False))


if __name__ == "__main__":
    main()
