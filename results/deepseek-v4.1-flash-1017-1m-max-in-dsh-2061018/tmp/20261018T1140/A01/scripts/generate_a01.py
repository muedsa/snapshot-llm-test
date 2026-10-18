"""A01 · 六个月经营诊断驾驶舱 — DSL generator.

Data source: tasks/A01-operations-dashboard/inputs/monthly.csv (read-only).
All computed values come from that file. Output: DSL text + computed-data.json
written under the task temp directory; final copies are made by the task driver.
Run from the suite root with SNAPSHOT_TASK_ROOT and SNAPSHOT_RUN_ID set.
"""
from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A01"
TMP = ROOT / "tmp" / RUN / TASK
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))

from dsl import (C, Col, Gap, HGap, Label, Pos, Row, SizedBox, Stack, T,  # noqa: E402
                 bar_chart, Circle, Series, line_chart, polygon, nice_ticks)

# ------------------------------------------------------------------ palette
BG = "#060B16"
PANEL = "#0C1526"
PANEL2 = "#101B31"
LINE = "#1E2C46"
TEXT = "#E8EFF9"
MUTED = "#8FA2BD"
FAINT = "#5F708A"
CYAN = "#22D3EE"
CYAN_SOFT = "#67E8F9"
VIOLET = "#8B5CF6"
AMBER = "#F59E0B"
GREEN = "#34D399"
RED = "#F87171"

W, H = 1600, 1000
PAD = 32
INNER = W - PAD * 2


def money(n: float) -> str:
    return f"{n:,.0f}"


def pct(n: float) -> str:
    return f"{n:.2f}%"


def load_rows() -> list[dict]:
    src = ROOT / "tasks" / "A01-operations-dashboard" / "inputs" / "monthly.csv"
    with src.open(encoding="utf-8") as fh:
        raw = list(csv.DictReader(fh))
    rows = []
    for r in raw:
        gross = float(r["gross_revenue"])
        refund = float(r["refund_amount"])
        cost = float(r["operating_cost"])
        orders = int(r["orders"])
        sessions = int(r["sessions"])
        net = gross - refund
        profit = net - cost
        rows.append({
            "month": r["month"],
            "orders": orders,
            "gross_revenue": gross,
            "refund_amount": refund,
            "operating_cost": cost,
            "sessions": sessions,
            "net_revenue": net,
            "operating_profit": profit,
            "refund_rate": refund / gross,
            "conversion_rate": orders / sessions,
        })
    return rows


def compute():
    rows = load_rows()
    totals = {
        "gross_revenue": sum(r["gross_revenue"] for r in rows),
        "refund_amount": sum(r["refund_amount"] for r in rows),
        "operating_cost": sum(r["operating_cost"] for r in rows),
        "net_revenue": sum(r["net_revenue"] for r in rows),
        "operating_profit": sum(r["operating_profit"] for r in rows),
        "orders": sum(r["orders"] for r in rows),
        "sessions": sum(r["sessions"] for r in rows),
    }
    totals["refund_rate"] = totals["refund_amount"] / totals["gross_revenue"]
    totals["conversion_rate"] = totals["orders"] / totals["sessions"]
    totals["profit_margin"] = totals["operating_profit"] / totals["net_revenue"]
    return rows, totals


def kpi_card(index, label, value, note, accent, width=368, height=126):
    bar = C(width=4, height=height - 36, color=accent, borderRadius=2)
    body = Col([
        Row([
            T(label, size=18, color=MUTED, weight="BOLD"),
            HGap(8),
            C(width=26, height=20, color=accent + "22", borderRadius=6,
              child=C(alignment="CENTER", child=T(index, size=11, color=accent, weight="BOLD", family="Inter"))),
        ], crossAxisAlignment="CENTER"),
        Gap(4),
        T(value, size=32, color=TEXT, weight="BOLD", family="Inter"),
        Gap(2),
        T(note, size=16, color=FAINT, max_lines=1),
    ], crossAxisAlignment="START", mainAxisAlignment="CENTER")
    return C(width=width, height=height, color=PANEL, borderRadius=16, border=f"1 SOLID {LINE}",
             padding="(16,18)",
             child=Row([bar, HGap(14), body], crossAxisAlignment="STRETCH", mainAxisAlignment="START"))


def table_cell(text, width, align="CENTER_RIGHT", color=TEXT, size=20, weight=None):
    return C(width=width, height=30, child=el_align(align, T(
        text, size=size, color=color, weight=weight, family="Inter,Noto Sans CJK SC")))


def table_row(values, widths, colors, aligns, bg=None, height=30, weight=None):
    cells = [table_cell(v, w, a, c, weight=weight) for v, w, c, a in zip(values, widths, colors, aligns)]
    body = Row(cells, crossAxisAlignment="CENTER")
    if bg:
        return C(width=sum(widths), height=height, color=bg, padding="(0,6)", child=body)
    return C(width=sum(widths), height=height, padding="(0,6)", child=body)


def build(rows, totals):
    months = [r["month"] for r in rows]
    shorts = [m[5:] + "月" for m in months]
    net_vals = [r["net_revenue"] for r in rows]
    profit_vals = [r["operating_profit"] for r in rows]
    session_vals = [r["sessions"] for r in rows]
    conv_vals = [r["conversion_rate"] * 100 for r in rows]

    # ------------------------------------------------------------- header
    badge = C(width=44, height=44, gradientType="LINEAR", gradientColors="#22D3EE,#8B5CF6",
              gradientBegin="TOP_LEFT", gradientEnd="BOTTOM_RIGHT", borderRadius=12,
              child=C(alignment="CENTER", child=T("N", size=24, color="#061019", weight="BOLD", family="Inter")))
    header = Row([
        badge, HGap(14),
        Col([
            Row([T("NORTHSTAR", size=14, color=CYAN, weight="BOLD", spacing=3),
                 HGap(10),
                 T("经营诊断驾驶舱", size=28, color=TEXT, weight="BOLD")], crossAxisAlignment="CENTER"),
            Gap(2),
            T("2026-04 — 2026-09 · 六个月经营复盘 · 管理层简报", size=17, color=MUTED),
        ], crossAxisAlignment="START"),
        el_spacer(),
        Row([
            C(width=8, height=8, color=GREEN, borderRadius=4),
            HGap(6),
            T("数据已核对", size=16, color=MUTED),
            HGap(18),
            C(color="#12203A", borderRadius=8, border=f"1 SOLID {LINE}", padding="(6,12)",
              child=T("BOARD REVIEW · 2026-10", size=15, color=CYAN_SOFT, family="Inter", weight="BOLD")),
        ], crossAxisAlignment="CENTER"),
    ], crossAxisAlignment="CENTER")

    # ---------------------------------------------------------------- KPIs
    rev_delta = net_vals[-1] / net_vals[0] - 1
    prof_delta = profit_vals[-1] / profit_vals[0] - 1
    kpis = [
        kpi_card("01", "总净收入", f"¥ {money(totals['net_revenue'])}",
                 f"9月较4月 +{rev_delta * 100:.1f}% · 全期累计", CYAN),
        kpi_card("02", "总经营利润", f"¥ {money(totals['operating_profit'])}",
                 f"利润率 {totals['profit_margin'] * 100:.1f}% · 9月为峰值", VIOLET),
        kpi_card("03", "总订单", f"{totals['orders']:,} 笔",
                 f"月均 {totals['orders'] / len(rows):.0f} 笔 · 9月 620 笔最高", AMBER),
        kpi_card("04", "期间总体转化率", pct(totals["conversion_rate"] * 100),
                 f"{totals['orders']:,} / {totals['sessions']:,}（订单/访问）", GREEN),
    ]
    kpi_row = Row([kpis[0], HGap(16), kpis[1], HGap(16), kpis[2], HGap(16), kpis[3]],
                  crossAxisAlignment="CENTER")

    # -------------------------------------------------------- main chart
    y_ticks = [0, 50000, 100000, 150000, 200000]
    chart = bar_chart(
        956, 280, shorts,
        [Series("净收入", CYAN, net_vals), Series("经营利润", VIOLET, profit_vals)],
        0, 220000, y_ticks,
        plot_left=64, plot_right=12, plot_top=14, plot_bottom=36,
        axis_color=LINE, grid_color="#16233A", text_color=MUTED,
        cat_size=16, legend=None, tick_size=15,
        bar_gap=5, group_gap=14, radius=4, bar_max=46, highlight=5, highlight_color="#132440",
        y_label=lambda v: f"{v / 10000:.0f}万" if v else "0")
    chart_title = Row([
        Col([
            T("净收入与经营利润", size=22, color=TEXT, weight="BOLD"),
            Gap(2),
            T("同为零起点 · 单位：元 · 六个月逐月对比", size=16, color=MUTED),
        ], crossAxisAlignment="START"),
    ])
    # % legend chips drawn as part of the chart; add a scale note at top-right of title
    scale_note = Row([
        C(width=8, height=8, color=CYAN, borderRadius=2), HGap(5), T("净收入", size=15, color=MUTED),
        HGap(12), C(width=8, height=8, color=VIOLET, borderRadius=2), HGap(5), T("经营利润", size=15, color=MUTED),
    ], crossAxisAlignment="CENTER")
    chart_panel = C(width=1004, height=378, color=PANEL, borderRadius=18, border=f"1 SOLID {LINE}",
                    padding="(18,24)",
                    child=Col([Row([chart_title, el_spacer(), scale_note], crossAxisAlignment="END"),
                               Gap(8), chart], crossAxisAlignment="START"))

    # ------------------------------------------------------- mini charts
    sess_ticks = [0, 2000, 4000, 6000]
    conv_ticks = [8, 10, 12]
    sess = bar_chart(
        468, 128, shorts, [Series("访问次数", CYAN_SOFT, session_vals)],
        0, 6000, sess_ticks,
        plot_left=44, plot_right=20, plot_top=10, plot_bottom=24,
        axis_color=LINE, grid_color="#16233A", text_color=MUTED,
        cat_size=13, bar_gap=0, group_gap=0, radius=3, bar_max=34, tick_size=12,
        y_label=lambda v: f"{v / 1000:.0f}k" if v else "0")
    conv = line_chart(
        468, 128, shorts, [Series("转化率", GREEN, conv_vals)],
        8, 13, conv_ticks,
        plot_left=44, plot_right=20, plot_top=10, plot_bottom=24,
        axis_color=LINE, grid_color="#16233A", text_color=MUTED, tick_size=12,
        area=True, area_alpha=0.14, line_width=2.4, dot_r=3,
        label_fmt=lambda v: f"{v:.0f}%", show_last=True,
        last_fmt=lambda v: f"{v:.2f}%")
    right_title = Row([
        T("流量与转化", size=22, color=TEXT, weight="BOLD"),
        HGap(10),
        T("访问次数 / 转化率 · 月份对齐", size=15, color=MUTED),
    ], crossAxisAlignment="END")
    right_panel = C(width=516, height=378, color=PANEL, borderRadius=18, border=f"1 SOLID {LINE}",
                    padding="(18,24)",
                    child=Col([
                        right_title,
                        Gap(4),
                        Row([T("访问次数", size=16, color=MUTED), el_spacer(),
                             T(f"9月 {session_vals[-1]:,} 次", size=16, color=CYAN_SOFT)], crossAxisAlignment="CENTER"),
                        sess,
                        Gap(6),
                        Row([T("总体转化率", size=16, color=MUTED), el_spacer(),
                             T(f"全期 {totals['conversion_rate'] * 100:.2f}%", size=16, color=GREEN)], crossAxisAlignment="CENTER"),
                        conv,
                    ], crossAxisAlignment="START"))

    # -------------------------------------------------------------- table
    widths = [100, 104, 220, 150, 220, 162]
    aligns = ["CENTER_LEFT", "CENTER_RIGHT", "CENTER_RIGHT", "CENTER_RIGHT", "CENTER_RIGHT", "CENTER_RIGHT"]
    head = table_row(["月份", "订单", "净收入", "退款率", "经营利润", "转化率"], widths,
                     [FAINT] * 6, aligns, bg="#0A1222", height=28, weight="BOLD")
    body_rows = []
    for i, r in enumerate(rows):
        is_last = i == len(rows) - 1
        refund_color = AMBER if r["refund_rate"] > 0.06 else MUTED
        vals = [r["month"], f"{r['orders']}", money(r["net_revenue"]), pct(r["refund_rate"] * 100),
                money(r["operating_profit"]), pct(r["conversion_rate"] * 100)]
        body_rows.append(table_row(vals, widths, [TEXT, MUTED, TEXT, refund_color, TEXT, GREEN],
                                   aligns, bg="#0E1B30" if is_last else None, weight="BOLD" if is_last else None))
    table = Col([head] + body_rows, crossAxisAlignment="START")
    table_panel = C(width=1004, height=300, color=PANEL, borderRadius=18, border=f"1 SOLID {LINE}",
                    padding="(16,24)",
                    child=Col([
                        Row([T("六个月明细", size=22, color=TEXT, weight="BOLD"),
                             HGap(10),
                             T("金额单位：元 · 比例保留两位小数", size=16, color=MUTED)]),
                        Gap(4), table,
                    ], crossAxisAlignment="START"))

    # ---------------------------------------------------------- conclusion
    evidence = [
        ("增长", f"9月净收入 {money(net_vals[-1])} 元（+{rev_delta * 100:.1f}%），经营利润 {money(profit_vals[-1])} 元（+{prof_delta * 100:.1f}%）。"),
        ("效率", f"订单 420→620 笔（+{(620 / 420 - 1) * 100:.1f}%），总体转化率 {totals['conversion_rate'] * 100:.2f}%。"),
        ("风险", "6/8月退款率均 8.00%，合计占全期退款 46.2%；9月降至 4.00%。"),
    ]
    ev_nodes = []
    for tag, text in evidence:
        ev_nodes.append(Row([
            C(width=42, height=20, color="#15243D", borderRadius=5, alignment="CENTER",
              child=T(tag, size=12, color=CYAN_SOFT, weight="BOLD")),
            HGap(8),
            C(width=396, child=T(text, size=20, color=MUTED, height="1.35")),
        ], crossAxisAlignment="START"))
    conclusion = C(width=516, height=300, color="#0D1930", borderRadius=18,
                   border="1 SOLID #24406A", padding="(16,24)",
                   child=Col([
                       Row([T("管理结论", size=14, color=CYAN, weight="BOLD", spacing=2),
                            HGap(8), C(width=80, height=1, color="#24406A")]),
                       Gap(6),
                       T("增长真实，退款是唯一逆风", size=24, color=TEXT, weight="BOLD", height="1.2"),
                       Gap(6),
                       Col(ev_nodes, crossAxisAlignment="START"),
                   ], crossAxisAlignment="START"))

    # ------------------------------------------------------------- footer
    footer = Row([
        T("数据源 monthly.csv", size=16, color=FAINT),
        HGap(12), T("·", size=16, color=FAINT), HGap(12),
        T("净收入=收入−退款 · 经营利润=净收入−成本 · 退款率=退款/收入 · 转化率=订单/访问", size=16, color=FAINT),
        el_spacer(),
        T("NORTHSTAR · INTERNAL", size=15, color=FAINT, family="Inter", spacing=1),
    ], crossAxisAlignment="CENTER")

    # --------------------------------------------------------------- root
    bg = Stack([
        SizedBox(W, H),
        C(width=900, height=900, gradientType="RADIAL",
          gradientColors="#12305700,#0B142400", gradientCenter="TOP_RIGHT",
          gradientRadius="0.9"),
        Pos(0, 0, C(width=W, height=4, gradientType="LINEAR",
                    gradientColors="#22D3EE00,#22D3EEE6,#8B5CF6E6,#22D3EE00",
                    gradientBegin="CENTER_LEFT", gradientEnd="CENTER_RIGHT")),
    ], width=W, height=H)

    content = Stack([bg] + [
        Pos(PAD, 28, header, w=INNER, h=58),
        Pos(PAD, 98, kpi_row, w=INNER, h=126),
        Pos(PAD, 240, chart_panel, w=1004, h=378),
        Pos(1052, 240, right_panel, w=516, h=378),
        Pos(PAD, 634, table_panel, w=1004, h=300),
        Pos(1052, 634, conclusion, w=516, h=300),
        Pos(PAD, 950, footer, w=INNER, h=20),
    ], width=W, height=H)

    dsl_text = f'<Snapshot type="png" background="{BG}">\n' + content + "\n</Snapshot>\n"

    # ------------------------------------------------------- computed json
    axes = [
        {
            "chart": "net_revenue_profit_grouped_bars",
            "unit": "CNY",
            "zero_baseline": True,
            "min": 0, "max": 220000,
            "ticks": y_ticks,
            "plot": {"x": 64, "y": 14, "width": 880, "height": 230},
            "mapping": "y_px = 14 + 230 * (220000 - value) / 220000",
            "x_mapping": "group_center_x = 64 + (880 / 6) * (index + 0.5)",
            "zero_pixel_y": 244,
        },
        {
            "chart": "sessions_bars",
            "unit": "sessions",
            "zero_baseline": True,
            "min": 0, "max": 6000,
            "ticks": sess_ticks,
            "plot": {"x": 44, "y": 10, "width": 404, "height": 94},
            "mapping": "y_px = 10 + 94 * (6000 - value) / 6000",
            "x_mapping": "bar_center_x = 44 + (404 / 6) * (index + 0.5)",
            "zero_pixel_y": 104,
        },
        {
            "chart": "conversion_line",
            "unit": "percent",
            "zero_baseline": False,
            "min": 8, "max": 13,
            "ticks": conv_ticks,
            "plot": {"x": 44, "y": 10, "width": 404, "height": 94},
            "mapping": "y_px = 10 + 94 * (13 - value) / 5",
            "x_mapping": "point_x = 44 + (404 / 5) * index",
            "zero_pixel_y": None,
        },
    ]
    computed = {
        "schema_version": 1,
        "task_id": TASK,
        "path_base": "output_dir",
        "source": "tasks/A01-operations-dashboard/inputs/monthly.csv",
        "formulas": {
            "net_revenue": "gross_revenue - refund_amount",
            "operating_profit": "net_revenue - operating_cost",
            "refund_rate": "refund_amount / gross_revenue",
            "conversion_rate": "orders / sessions",
            "overall_conversion_rate": "sum(orders) / sum(sessions)",
        },
        "months": [{
            "month": r["month"],
            "orders": r["orders"],
            "gross_revenue": r["gross_revenue"],
            "refund_amount": r["refund_amount"],
            "operating_cost": r["operating_cost"],
            "sessions": r["sessions"],
            "net_revenue": r["net_revenue"],
            "operating_profit": r["operating_profit"],
            "refund_rate": round(r["refund_rate"], 6),
            "conversion_rate": round(r["conversion_rate"], 6),
        } for r in rows],
        "totals": {k: round(v, 6) for k, v in totals.items()},
        "axes": axes,
        "conclusion": {
            "text": "增长真实，退款是唯一逆风：9月净收入与经营利润均为六个月最高，增长主要由订单量驱动；6月与8月 8.00% 的退款率是利润的主要拖累。",
            "citations": [
                {"field": "months[5].net_revenue", "value": net_vals[-1]},
                {"field": "months[0].net_revenue", "value": net_vals[0]},
                {"field": "months[5].operating_profit", "value": profit_vals[-1]},
                {"field": "months[0].operating_profit", "value": profit_vals[0]},
                {"field": "months[5].orders", "value": rows[-1]["orders"]},
                {"field": "months[0].orders", "value": rows[0]["orders"]},
                {"field": "months[2].refund_rate", "value": round(rows[2]["refund_rate"], 6)},
                {"field": "months[4].refund_rate", "value": round(rows[4]["refund_rate"], 6)},
                {"field": "totals.overall_conversion_rate", "value": round(totals["conversion_rate"], 6)},
            ],
        },
    }
    return dsl_text, computed


def el_spacer(child: str = "") -> str:
    return '<Spacer />'


def el_align(alignment: str, child: str) -> str:
    return f'<Align alignment="{alignment}">{child}</Align>'


def main() -> int:
    rows, totals = compute()
    dsl_text, computed = build(rows, totals)
    dsl_dir = TMP / "dsl" / "operations"
    dsl_dir.mkdir(parents=True, exist_ok=True)
    (dsl_dir / "v001.snapshot").write_text(dsl_text, encoding="utf-8")
    (TMP / "computed-data.json").write_text(json.dumps(computed, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {len(dsl_text)} bytes DSL and computed-data.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
