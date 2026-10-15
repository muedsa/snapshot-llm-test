#!/usr/bin/env python
"""A01 六个月经营诊断驾驶舱 —— 数据计算 + DSL 生成。

启动基准：总任务根（环境变量 SNAPSHOT_TASK_ROOT 指向的目录）。
输入：tasks/A01-operations-dashboard/inputs/monthly.csv （只读，不修改）
输出：tmp/<run_id>/A01/drafts/a01-<version>.snapshot
"""
from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path

SCRIPTS = Path("tmp/run-20261011-01/_suite/scripts")
sys.path.insert(0, str(SCRIPTS))
import snapkit as sk  # noqa: E402
from snapkit import C, Col, F_BODY, F_HEAD, F_NUM  # noqa: E402

RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "run-20261011-01")
TASK = "A01"
INPUT_CSV = "tasks/A01-operations-dashboard/inputs/monthly.csv"
DRAFT_DIR = f"tmp/{RUN_ID}/{TASK}/drafts"

W, H = 1600, 1000


# ----------------------------------------------------------------- 数据层
def load_rows():
    root = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
    with (root / INPUT_CSV).open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def compute():
    rows = load_rows()
    months = []
    for r in rows:
        m = r["month"]
        orders = int(r["orders"])
        gross = int(r["gross_revenue"])
        refund = int(r["refund_amount"])
        cost = int(r["operating_cost"])
        sessions = int(r["sessions"])
        net = gross - refund
        profit = net - cost
        months.append({
            "month": m,
            "orders": orders,
            "gross_revenue": gross,
            "refund_amount": refund,
            "operating_cost": cost,
            "sessions": sessions,
            "net_revenue": net,
            "operating_profit": profit,
            "refund_rate": refund / gross,
            "conversion_rate": orders / sessions,
            "profit_margin": profit / net if net else None,
            "aov": net / orders,
        })
    T = {k: sum(m[k] for m in months) for k in
         ("orders", "gross_revenue", "refund_amount", "operating_cost",
          "sessions", "net_revenue", "operating_profit")}
    T["overall_conversion_rate"] = T["orders"] / T["sessions"]
    T["overall_refund_rate"] = T["refund_amount"] / T["gross_revenue"]
    T["profit_margin"] = T["operating_profit"] / T["net_revenue"]
    T["avg_monthly_conversion_rate"] = sum(
        m["conversion_rate"] for m in months) / len(months)
    T["refund_rate_spread"] = max(m["refund_rate"] for m in months) - min(
        m["refund_rate"] for m in months)
    return months, T


# ----------------------------------------------------------------- 版面常量
MARGIN = 28
CONTENT_W = W - 2 * MARGIN              # 1544
LEFT_W = 912
RIGHT_X = MARGIN + LEFT_W + 20          # 960
RIGHT_W = CONTENT_W - LEFT_W - 20       # 612

KPI_Y, KPI_H = 74, 128
MID_Y, MID_H = 212, 352
BOT_Y, BOT_H = 574, 352
FOOT_Y = 936


def build(months, T) -> str:
    months_full = [m["month"] for m in months]
    net_w = [sk.wan(m["net_revenue"]) for m in months]
    pro_w = [sk.wan(m["operating_profit"]) for m in months]
    sessions = [m["sessions"] for m in months]
    conv = [m["conversion_rate"] for m in months]

    parts = []

    # ---------------- 页眉
    parts.append(sk.header(
        CONTENT_W,
        "Northstar 经营诊断驾驶舱",
        "统计期间 2026-04 至 2026-09 · 金额单位：元（图表纵轴按万元标注）· 数据源 inputs/monthly.csv",
        h=64, bg=C.CANVAS, accent=C.BLUE, title_size=28, sub_size=17))

    # ---------------- 四张 KPI
    kpi_gap = 18
    kpi_w = (CONTENT_W - 3 * kpi_gap) / 4
    kpis = [
        ("总净收入（收入−退款）", sk.fmt_int(T["net_revenue"]), "元",
         f'合计 {sk.fmt_int(T["net_revenue"])} 元 ＝ {sk.fmt_num(sk.wan(T["net_revenue"]), 2)} 万元', C.BLUE),
        ("总经营利润（净收入−成本）", sk.fmt_int(T["operating_profit"]), "元",
         f'利润率 {sk.fmt_pct(T["profit_margin"], 2)} ＝ {sk.fmt_num(sk.wan(T["operating_profit"]), 2)} 万元', C.GREEN),
        ("总订单", sk.fmt_int(T["orders"]), "笔",
         f'6 个月累计 · 月均 {sk.fmt_num(T["orders"] / 6, 0)} 笔', C.INDIGO),
        ("期间总体转化率", sk.fmt_pct(T["overall_conversion_rate"], 2), "",
         f'{sk.fmt_int(T["orders"])} 笔 ÷ {sk.fmt_int(T["sessions"])} 次（加权口径）', C.AMBER),
    ]
    for i, (lb, val, unit, sub, acc) in enumerate(kpis):
        x = MARGIN + i * (kpi_w + kpi_gap)
        node = sk.kpi_card(lb, val, unit=unit or None, sub=sub, accent=acc,
                           w=kpi_w, h=KPI_H, value_size=40, label_size=19, sub_size=16)
        parts.append(f'<Positioned left="{x}" top="{KPI_Y}">{node}</Positioned>')

    # ---------------- 主图：净收入 / 经营利润 分组柱图
    card_w, card_h = LEFT_W, MID_H
    pad = 18
    parts.append(f'<Positioned left="{MARGIN}" top="{MID_Y}">{sk.card(card_w, card_h)}</Positioned>')
    parts.append(f'<Positioned left="{MARGIN + pad}" top="{MID_Y + 12}" width="{card_w - 2 * pad}" height="28">'
                 f'{sk.text("净收入与经营利润 · 分组柱图", size=21, color=C.INK, family=F_HEAD)}</Positioned>')
    # 横向图例置于卡片右上（hlegend 在 total_w 模式下返回 Row，可安全嵌套）
    parts.append(f'<Positioned left="{MARGIN}" top="{MID_Y + 17}" width="{card_w - 2 * pad}" height="26">'
                 f'{sk.hlegend([(C.BLUE, "净收入"), (C.GREEN, "经营利润")], size=17, gap=26, swatch=14, total_w=card_w - 2 * pad)}'
                 f'</Positioned>')
    parts.append(f'<Positioned left="{MARGIN + pad}" top="{MID_Y + 42}" width="{card_w - 2 * pad}" height="24">'
                 f'{sk.text("两序列共用零起点与同一比例尺 · 纵轴单位：万元", size=16, color=C.MUTED, family=F_BODY)}</Positioned>')
    chart = sk.vbar_chart(
        months_full, [("净收入", C.BLUE, net_w), ("经营利润", C.GREEN, pro_w)],
        width=card_w - 2 * pad, height=card_h - 92,
        plot_left=70, plot_right=16, plot_top=16, plot_bottom=44,
        value_fmt=lambda v: sk.fmt_num(v, 2),
        axis_fmt=lambda v: sk.fmt_num(v, 0),
        tick_target=5, value_size=15, label_size=17, tick_size=16)
    parts.append(f'<Positioned left="{MARGIN + pad}" top="{MID_Y + 68}">{chart}</Positioned>')

    # ---------------- 右上：访问量小图
    sc_h = (MID_H - 14) / 2
    parts.append(f'<Positioned left="{RIGHT_X}" top="{MID_Y}">{sk.card(RIGHT_W, sc_h)}</Positioned>')
    parts.append(f'<Positioned left="{RIGHT_X + pad}" top="{MID_Y + 11}" width="380" height="26">'
                 f'{sk.text("访问量 sessions", size=19, color=C.INK, family=F_HEAD)}</Positioned>')
    parts.append(f'<Positioned left="{RIGHT_X}" top="{MID_Y + 13}" width="{RIGHT_W - pad}" height="22">'
                 f'{sk.text("单位：次 · 零起点", size=15, color=C.FAINT, family=F_BODY, align="RIGHT")}</Positioned>')
    ch1 = sk.vbar_chart(
        months_full, [("访问量", C.CYAN, sessions)],
        width=RIGHT_W - 2 * pad, height=sc_h - 46,
        plot_left=58, plot_right=12, plot_top=16, plot_bottom=30,
        value_fmt=lambda v: sk.fmt_int(v),
        axis_fmt=lambda v: sk.fmt_int(v),
        tick_target=3, value_size=14, label_size=15, tick_size=14)
    parts.append(f'<Positioned left="{RIGHT_X + pad}" top="{MID_Y + 36}">{ch1}</Positioned>')

    # ---------------- 右下：转化率小图（非零起点，图上标注）
    cv_y = MID_Y + sc_h + 14
    cv_h = MID_H - sc_h - 14
    parts.append(f'<Positioned left="{RIGHT_X}" top="{cv_y}">{sk.card(RIGHT_W, cv_h)}</Positioned>')
    parts.append(f'<Positioned left="{RIGHT_X + pad}" top="{cv_y + 11}" width="380" height="26">'
                 f'{sk.text("下单转化率", size=19, color=C.INK, family=F_HEAD)}</Positioned>')
    parts.append(f'<Positioned left="{RIGHT_X}" top="{cv_y + 13}" width="{RIGHT_W - pad}" height="22">'
                 f'{sk.text("纵轴 10.50%–12.00% 非零起点 · 虚线＝总体均值", size=15, color=C.FAINT, family=F_BODY, align="RIGHT")}</Positioned>')
    ch2 = sk.vline_chart(
        months_full, [("转化率", C.VIOLET, conv)],
        width=RIGHT_W - 2 * pad, height=cv_h - 46,
        plot_left=68, plot_right=16, plot_top=20, plot_bottom=30,
        value_fmt=lambda v: sk.fmt_pct(v, 2),
        axis_fmt=lambda v: sk.fmt_pct(v, 2),
        tick_target=4, value_size=14, label_size=15, tick_size=14,
        zero_base=False, area=False,
        ref_lines=[(T["overall_conversion_rate"], "#64748B", "")])
    parts.append(f'<Positioned left="{RIGHT_X + pad}" top="{cv_y + 36}">{ch2}</Positioned>')

    # ---------------- 明细表
    parts.append(f'<Positioned left="{MARGIN}" top="{BOT_Y}">{sk.card(LEFT_W, BOT_H)}</Positioned>')
    parts.append(f'<Positioned left="{MARGIN + pad}" top="{BOT_Y + 12}" width="500" height="26">'
                 f'{sk.text("六个月经营明细", size=20, color=C.INK, family=F_HEAD)}</Positioned>')
    parts.append(f'<Positioned left="{MARGIN}" top="{BOT_Y + 15}" width="{LEFT_W - pad}" height="22">'
                 f'{sk.text("金额单位：元（整数） · 比例为两位小数", size=15, color=C.FAINT, family=F_BODY, align="RIGHT")}</Positioned>')
    cols = [
        Col("month", "月份", 132, "LEFT", color=C.INK),
        Col("net", "净收入（元）", 196),
        Col("rr", "退款率", 146, color=C.AMBER),
        Col("profit", "经营利润（元）", 196),
        Col("cv", "转化率", 182, color=C.VIOLET),
    ]
    trows = [{
        "month": m["month"],
        "net": sk.fmt_int(m["net_revenue"]),
        "rr": sk.fmt_pct(m["refund_rate"], 2),
        "profit": sk.fmt_int(m["operating_profit"]),
        "cv": sk.fmt_pct(m["conversion_rate"], 2),
    } for m in months]
    tbl = sk.table(cols, trows, x=MARGIN + pad, y=BOT_Y + 46, row_h=38, head_h=42,
                   size=20, head_size=18, pad=12, emphasis=5,
                   emphasis_bg="#E0E7FF", emphasis_color=C.INK, cell_color=C.INK2)
    parts.append(tbl)

    # ---------------- 结论卡
    parts.append(f'<Positioned left="{RIGHT_X}" top="{BOT_Y}">{sk.card(RIGHT_W, BOT_H, bg="#F8FAFC")}</Positioned>')
    parts.append(f'<Positioned left="{RIGHT_X + pad}" top="{BOT_Y + 12}" width="420" height="26">'
                 f'{sk.text("管理结论与行动建议", size=20, color=C.INK, family=F_HEAD)}</Positioned>')

    last, first = months[-1], months[0]
    jun, may, aug = months[2], months[1], months[4]
    refund_68 = jun["refund_amount"] + aug["refund_amount"]
    items = [
        (C.BLUE, "规模", f'净收入自 06 月 {sk.fmt_int(jun["net_revenue"])} 元升至 09 月 '
                        f'{sk.fmt_int(last["net_revenue"])} 元（+{sk.fmt_pct(last["net_revenue"] / jun["net_revenue"] - 1, 2)}）；'
                        f'期间总经营利润 {sk.fmt_int(T["operating_profit"])} 元，利润率 {sk.fmt_pct(T["profit_margin"], 2)}。'),
        (C.RED, "症结", f'06 与 08 月退款率同为 {sk.fmt_pct(jun["refund_rate"], 2)}，是 04/05/07 月 '
                       f'{sk.fmt_pct(first["refund_rate"], 2)} 的 1.60 倍；两月退款 {sk.fmt_int(refund_68)} 元，'
                       f'占期间退款 {sk.fmt_pct(refund_68 / T["refund_amount"], 2)}。'),
        (C.RED, "代价", f'06 月净收入较 05 月少 {sk.fmt_int(may["net_revenue"] - jun["net_revenue"])} 元'
                       f'（{sk.fmt_pct(jun["net_revenue"] / may["net_revenue"] - 1, 2)}），'
                       f'经营利润同步从 {sk.fmt_int(may["operating_profit"])} 元降至 {sk.fmt_int(jun["operating_profit"])} 元。'),
        (C.AMBER, "结构", f'总体转化率 {sk.fmt_pct(T["overall_conversion_rate"], 2)} 低于 04 月 '
                         f'{sk.fmt_pct(first["conversion_rate"], 2)}；增长主要来自访问量 '
                         f'{sk.fmt_int(first["sessions"])}→{sk.fmt_int(last["sessions"])} 次（+60.00%）。'),
        (C.GREEN, "行动", f'优先治理 06/08 月退款，守住 {sk.fmt_pct(first["refund_rate"], 2)} 基线；'
                         f'09 月已回落至 {sk.fmt_pct(last["refund_rate"], 2)}，利润 {sk.fmt_int(last["operating_profit"])} 元创新高。'),
    ]
    ly = BOT_Y + 48
    for col, head_txt, body_txt in items:
        parts.append(sk.box(4, 56, color=col, radius=2, left=RIGHT_X + pad, top=ly + 2))
        parts.append(f'<Positioned left="{RIGHT_X + pad + 14}" top="{ly}" width="{RIGHT_W - 2 * pad - 14}" height="58">'
                     f'<Row crossAxisAlignment="START">'
                     f'<SizedBox width="56" height="58">'
                     f'{sk.text(head_txt, size=20, color=col, family=F_HEAD)}</SizedBox>'
                     f'<SizedBox width="8" />'
                     f'<SizedBox width="{RIGHT_W - 2 * pad - 78}" height="58">'
                     f'{sk.wrapped(RIGHT_W - 2 * pad - 78, body_txt, size=20, color=C.INK2, line_height=1.42)}'
                     f'</SizedBox></Row></Positioned>')
        ly += 60

    # ---------------- 页脚脚注
    footnote = (
        "口径：净收入＝退款前收入−当月退款；经营利润＝净收入−不含退款的经营成本；退款率＝当月退款÷当月退款前收入；"
        "转化率＝当月订单÷当月访问次数。期间总体转化率＝总订单 3,045÷总访问 27,300＝11.15%（按月比例简单平均为 11.19%，本屏采用加权口径）。"
        "分组柱图两序列共用零起点与同一比例尺；转化率折线纵轴为 10.50%–12.00% 非零起点，虚线为总体均值 11.15%。"
    )
    parts.append(f'<Positioned left="{MARGIN}" top="{FOOT_Y}" width="{CONTENT_W}" height="1">'
                 f'{sk.divider(CONTENT_W)}</Positioned>')
    parts.append(f'<Positioned left="{MARGIN}" top="{FOOT_Y + 9}" width="{CONTENT_W}" height="52">'
                 f'{sk.wrapped(CONTENT_W, footnote, size=17, color=C.MUTED, line_height=1.5)}</Positioned>')

    body = "".join(parts)
    return f'<Snapshot type="png" background="#F1F5F9">\n<Container width="{W}" height="{H}">\n' \
           f'<Stack fit="EXPAND">\n{body}\n</Stack>\n</Container>\n</Snapshot>\n'


def _axis(chart_id, title, unit, values_display, scale, origin_x, plot_x0, plot_x1,
          plot_y0, plot_y1, zero_base, note=""):
    """构造审计用的轴定义（含像素映射，原点为画布左上、x 向右 / y 向下）。"""
    lo, hi = scale
    return {
        "chart_id": chart_id,
        "title": title,
        "unit": unit,
        "zero_base": zero_base,
        "axis_min": round(lo, 6),
        "axis_max": round(hi, 6),
        "zero_line_value": 0.0 if (lo <= 0.0 <= hi) else None,
        "zero_line_y_px": (round(plot_y1 - (0.0 - lo) / (hi - lo) * (plot_y1 - plot_y0), 3)
                           if (lo <= 0.0 <= hi) else None),
        "plot_area_px": {"left": plot_x0, "right": plot_x1, "top": plot_y0, "bottom": plot_y1},
        "value_to_pixel": {
            "formula": "y_px = bottom_px - (value - axis_min) / (axis_max - axis_min) * (bottom_px - top_px)",
            "canvas_origin": "top-left",
            "x_axis_direction": "right",
            "y_axis_direction": "down",
            "unit": "pixel",
            "chart_origin_px": [origin_x, 0],
        },
        "ticks": values_display,
        "note": note,
    }


def main():
    months, T = compute()
    version = sys.argv[1] if len(sys.argv) > 1 else "v1"
    root = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
    out = root / DRAFT_DIR / f"a01-{version}.snapshot"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build(months, T), encoding="utf-8")

    pad = 18
    net_w = [sk.wan(m["net_revenue"]) for m in months]
    pro_w = [sk.wan(m["operating_profit"]) for m in months]
    sessions = [m["sessions"] for m in months]
    conv = [m["conversion_rate"] for m in months]

    # --- 主柱图（万元，零起点）
    b_h = MID_H - 92
    b_ticks, b_lo, b_hi = sk.nice_ticks(0.0, max(net_w + pro_w), 5)
    b_x0, b_y0 = MARGIN + pad, MID_Y + 68
    b_px0, b_px1 = b_x0 + 70, b_x0 + (card_w_of(MID_H)) - pad - 16
    b_py0, b_py1 = b_y0 + 16, b_y0 + b_h - 44
    axes = [{
        "chart_id": "chart_net_profit_grouped_bar",
        "title": "净收入与经营利润 · 分组柱图",
        "unit": "万元 (CNY 10k)",
        "series": ["净收入", "经营利润"],
        "zero_base": True,
        "axis_min": b_lo, "axis_max": b_hi,
        "zero_line_value": 0.0,
        "zero_line_y_px": round(b_py1 - (0 - b_lo) / (b_hi - b_lo) * (b_py1 - b_py0), 3),
        "plot_area_px": {"left": b_px0, "right": b_px1, "top": b_py0, "bottom": b_py1},
        "ticks": [round(t, 4) for t in b_ticks],
        "tick_display": [sk.fmt_num(t, 0) for t in b_ticks],
        "shared_scale_note": "两个序列共用同一零线与同一比例尺（同一 Scale 实例）",
        "value_to_pixel": {
            "formula": "y_px = bottom_px - (value_wan - axis_min) / (axis_max - axis_min) * (bottom_px - top_px)",
            "canvas_origin": "top-left", "x_axis_direction": "right",
            "y_axis_direction": "down", "unit": "pixel",
        },
        "bar_top_y_px": {m["month"]: round(b_py1 - (sk.wan(m["net_revenue"]) - b_lo) / (b_hi - b_lo) * (b_py1 - b_py0), 3)
                         for m in months},
        "profit_bar_top_y_px": {m["month"]: round(b_py1 - (sk.wan(m["operating_profit"]) - b_lo) / (b_hi - b_lo) * (b_py1 - b_py0), 3)
                                for m in months},
    }]

    # --- 访问量柱图（次，零起点）
    sc_h = (MID_H - 14) / 2
    s_ticks, s_lo, s_hi = sk.nice_ticks(0.0, max(sessions), 3)
    s_x0, s_y0 = RIGHT_X + pad, MID_Y + 36
    s_h2 = sc_h - 46
    s_py0, s_py1 = s_y0 + 16, s_y0 + s_h2 - 30
    axes.append({
        "chart_id": "chart_sessions_bar", "title": "访问量 sessions", "unit": "次",
        "zero_base": True, "axis_min": s_lo, "axis_max": s_hi,
        "zero_line_value": 0.0,
        "zero_line_y_px": round(s_py1, 3),
        "plot_area_px": {"left": s_x0 + 58, "right": s_x0 + (RIGHT_W - 2 * pad) - 12,
                         "top": s_py0, "bottom": s_py1},
        "ticks": [round(t, 4) for t in s_ticks],
        "tick_display": [sk.fmt_int(t) for t in s_ticks],
        "value_to_pixel": {
            "formula": "y_px = bottom_px - value / axis_max * (bottom_px - top_px)",
            "canvas_origin": "top-left", "x_axis_direction": "right",
            "y_axis_direction": "down", "unit": "pixel"},
    })

    # --- 转化率折线（非零起点）
    cv_y = MID_Y + sc_h + 14
    cv_h = MID_H - sc_h - 14
    c_ticks, c_lo, c_hi = sk.nice_ticks(min(conv), max(conv), 4, zero_base=False)
    c_x0, c_y0 = RIGHT_X + pad, cv_y + 36
    c_h2 = cv_h - 46
    c_py0, c_py1 = c_y0 + 20, c_y0 + c_h2 - 30
    axes.append({
        "chart_id": "chart_conversion_line", "title": "下单转化率", "unit": "ratio (0–1)，显示为百分比",
        "zero_base": False, "axis_min": round(c_lo, 6), "axis_max": round(c_hi, 6),
        "zero_line_value": None, "zero_line_y_px": None,
        "non_zero_baseline_note": "纵轴为 10.50%–12.00% 非零起点，已在图上与脚注显式标注；虚线为总体均值 11.15%",
        "reference_line_value": round(T["overall_conversion_rate"], 6),
        "reference_line_y_px": round(c_py1 - (T["overall_conversion_rate"] - c_lo) / (c_hi - c_lo) * (c_py1 - c_py0), 3),
        "plot_area_px": {"left": c_x0 + 68, "right": c_x0 + (RIGHT_W - 2 * pad) - 16,
                         "top": c_py0, "bottom": c_py1},
        "ticks": [round(t, 6) for t in c_ticks],
        "tick_display": [sk.fmt_pct(t, 2) for t in c_ticks],
        "value_to_pixel": {
            "formula": "y_px = bottom_px - (value - axis_min) / (axis_max - axis_min) * (bottom_px - top_px)",
            "canvas_origin": "top-left", "x_axis_direction": "right",
            "y_axis_direction": "down", "unit": "pixel"},
    })

    last, first = months[-1], months[0]
    jun, may, aug = months[2], months[1], months[4]
    refund_68 = jun["refund_amount"] + aug["refund_amount"]

    computed = {
        "schema_version": 1,
        "task_id": "A01",
        "path_base": "output_dir",
        "run_id": RUN_ID,
        "round": "round-01",
        "title": "六个月经营诊断驾驶舱 · 审计数据",
        "canvas": {"width": W, "height": H, "format": "png", "service": "open-snapshot /snapshot"},
        "coordinate_system": {"origin": "canvas top-left", "x": "right", "y": "down", "unit": "pixel"},
        "inputs": {
            "source": "inputs/monthly.csv",
            "note": "唯一业务数据源；金额单位元，订单笔，sessions 次；输入未被修改",
            "period": f'{months[0]["month"]} .. {months[-1]["month"]}',
            "row_count": len(months),
        },
        "definitions": {
            "net_revenue": "gross_revenue - refund_amount",
            "operating_profit": "net_revenue - operating_cost",
            "refund_rate": "refund_amount / gross_revenue",
            "conversion_rate": "orders / sessions",
            "overall_conversion_rate": "sum(orders) / sum(sessions)  （加权口径，非月比例平均）",
        },
        "months": [{
            "month": m["month"],
            "orders": m["orders"], "sessions": m["sessions"],
            "gross_revenue": m["gross_revenue"], "refund_amount": m["refund_amount"],
            "operating_cost": m["operating_cost"],
            "net_revenue": m["net_revenue"], "operating_profit": m["operating_profit"],
            "net_revenue_wan": round(sk.wan(m["net_revenue"]), 4),
            "operating_profit_wan": round(sk.wan(m["operating_profit"]), 4),
            "refund_rate": round(m["refund_rate"], 6),
            "refund_rate_display": sk.fmt_pct(m["refund_rate"], 2),
            "conversion_rate": round(m["conversion_rate"], 6),
            "conversion_rate_display": sk.fmt_pct(m["conversion_rate"], 2),
            "profit_margin": round(m["profit_margin"], 6),
            "profit_margin_display": sk.fmt_pct(m["profit_margin"], 2),
            "aov": round(m["aov"], 2),
        } for m in months],
        "totals": {
            "gross_revenue": T["gross_revenue"],
            "refund_amount": T["refund_amount"],
            "operating_cost": T["operating_cost"],
            "net_revenue": T["net_revenue"],
            "operating_profit": T["operating_profit"],
            "orders": T["orders"],
            "sessions": T["sessions"],
            "overall_conversion_rate": round(T["overall_conversion_rate"], 6),
            "overall_conversion_rate_display": sk.fmt_pct(T["overall_conversion_rate"], 2),
            "overall_refund_rate": round(T["overall_refund_rate"], 6),
            "overall_refund_rate_display": sk.fmt_pct(T["overall_refund_rate"], 2),
            "profit_margin": round(T["profit_margin"], 6),
            "profit_margin_display": sk.fmt_pct(T["profit_margin"], 2),
            "avg_monthly_conversion_rate": round(T["avg_monthly_conversion_rate"], 6),
            "avg_monthly_conversion_rate_display": sk.fmt_pct(T["avg_monthly_conversion_rate"], 2),
            "net_revenue_wan": round(sk.wan(T["net_revenue"]), 4),
            "operating_profit_wan": round(sk.wan(T["operating_profit"]), 4),
        },
        "kpi_display": {
            "总净收入": {"value": sk.fmt_int(T["net_revenue"]), "unit": "元",
                     "wan": sk.fmt_num(sk.wan(T["net_revenue"]), 2)},
            "总经营利润": {"value": sk.fmt_int(T["operating_profit"]), "unit": "元",
                       "wan": sk.fmt_num(sk.wan(T["operating_profit"]), 2)},
            "总订单": {"value": sk.fmt_int(T["orders"]), "unit": "笔"},
            "期间总体转化率": {"value": sk.fmt_pct(T["overall_conversion_rate"], 2), "unit": "",
                         "formula": "3045 / 27300"},
        },
        "table": {
            "columns": ["月份", "净收入（元）", "退款率", "经营利润（元）", "转化率"],
            "row_count": len(months),
            "amount_precision": "integer 元", "ratio_precision": "2 decimal places",
            "rows": [{
                "month": m["month"],
                "net_revenue_display": sk.fmt_int(m["net_revenue"]),
                "refund_rate_display": sk.fmt_pct(m["refund_rate"], 2),
                "operating_profit_display": sk.fmt_int(m["operating_profit"]),
                "conversion_rate_display": sk.fmt_pct(m["conversion_rate"], 2),
            } for m in months],
        },
        "axes": axes,
        "conclusion": {
            "headline": "增长来自流量而非转化效率；06/08 月退款率异常是利润受损的直接原因，应优先治理。",
            "items": [
                {"key": "规模", "text": f'净收入自 06 月 {jun["net_revenue"]:,} 元升至 09 月 {last["net_revenue"]:,} 元'
                                        f'（+{sk.fmt_pct(last["net_revenue"] / jun["net_revenue"] - 1, 2)}）',
                 "cited_fields": ["months[2].net_revenue", "months[5].net_revenue"],
                 "cited_values": [jun["net_revenue"], last["net_revenue"]]},
                {"key": "症结", "text": f'06 与 08 月退款率同为 {sk.fmt_pct(jun["refund_rate"], 2)}，'
                                       f'是 04/05/07 月 {sk.fmt_pct(first["refund_rate"], 2)} 的 1.60 倍；'
                                       f'两月退款 {refund_68:,} 元，占期间退款 {sk.fmt_pct(refund_68 / T["refund_amount"], 2)}',
                 "cited_fields": ["months[2].refund_rate", "months[4].refund_rate",
                                  "months[2].refund_amount", "months[4].refund_amount",
                                  "totals.refund_amount"],
                 "cited_values": [round(jun["refund_rate"], 6), round(aug["refund_rate"], 6),
                                  jun["refund_amount"], aug["refund_amount"], T["refund_amount"]]},
                {"key": "代价", "text": f'06 月净收入较 05 月少 {may["net_revenue"] - jun["net_revenue"]:,} 元'
                                       f'（{sk.fmt_pct(jun["net_revenue"] / may["net_revenue"] - 1, 2)}），'
                                       f'经营利润从 {may["operating_profit"]:,} 元降至 {jun["operating_profit"]:,} 元',
                 "cited_fields": ["months[1].net_revenue", "months[2].net_revenue",
                                  "months[1].operating_profit", "months[2].operating_profit"],
                 "cited_values": [may["net_revenue"], jun["net_revenue"],
                                  may["operating_profit"], jun["operating_profit"]]},
                {"key": "结构", "text": f'总体转化率 {sk.fmt_pct(T["overall_conversion_rate"], 2)} 低于 04 月 '
                                       f'{sk.fmt_pct(first["conversion_rate"], 2)}；访问量 {first["sessions"]:,}→'
                                       f'{last["sessions"]:,} 次（+60.00%）',
                 "cited_fields": ["totals.overall_conversion_rate", "months[0].conversion_rate",
                                  "months[0].sessions", "months[5].sessions"],
                 "cited_values": [round(T["overall_conversion_rate"], 6),
                                  round(first["conversion_rate"], 6),
                                  first["sessions"], last["sessions"]]},
                {"key": "行动", "text": f'优先治理 06/08 月退款，守住 {sk.fmt_pct(first["refund_rate"], 2)} 基线；'
                                       f'09 月已回落至 {sk.fmt_pct(last["refund_rate"], 2)}，'
                                       f'利润 {last["operating_profit"]:,} 元创新高',
                 "cited_fields": ["months[0].refund_rate", "months[5].refund_rate",
                                  "months[5].operating_profit"],
                 "cited_values": [round(first["refund_rate"], 6), round(last["refund_rate"], 6),
                                  last["operating_profit"]]},
            ],
            "evidence_summary": {
                "total_net_revenue": T["net_revenue"],
                "total_operating_profit": T["operating_profit"],
                "overall_conversion_rate": round(T["overall_conversion_rate"], 6),
                "worst_refund_months": ["2026-06", "2026-08"],
                "worst_refund_rate": 0.08,
                "baseline_refund_rate": 0.05,
                "refund_share_of_0608": round(refund_68 / T["refund_amount"], 6),
                "sessions_growth": round(last["sessions"] / first["sessions"] - 1, 6),
                "best_profit_month": max(months, key=lambda m: m["operating_profit"])["month"],
            },
        },
        "typography_inventory_px": {
            "page_title": 28, "kpi_label": 19, "kpi_value": 40, "kpi_sub": 16,
            "card_title": 20, "table_header": 18, "table_body": 20,
            "conclusion_body": 20, "chart_category_label": 15,
            "main_chart_category_label": 17, "main_chart_tick": 16,
            "chart_value_label": 14, "main_chart_value_label": 15, "footnote": 17,
            "note": "正文类（表体、结论、卡片标题、KPI 标签）≥19px，明细表与结论正文 20px；脚注 17px ≥16；"
                    "图表刻度/类别标签为图表附属元素，14–17px。",
        },
        "outputs": [
            {"kind": "png", "filename": "operations.png", "dsl": "operations.snapshot",
             "width": W, "height": H},
            {"kind": "json", "filename": "computed-data.json"},
        ],
    }
    (root / DRAFT_DIR).mkdir(parents=True, exist_ok=True)
    (root / DRAFT_DIR / "computed-raw.json").write_text(
        json.dumps(computed, ensure_ascii=False, indent=2), encoding="utf-8")
    print(str(out))


def card_w_of(_mid_h):
    return LEFT_W


if __name__ == "__main__":
    main()