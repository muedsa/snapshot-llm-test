# -*- coding: utf-8 -*-
"""A22 dashboard generator: compute + audit JSON + DSL, one run per round.

Usage (launch base = suite root):
  python tmp/run-20261011-01/A22/scripts/a22_gen.py <1|2|3>

- Reads inputs/monthly.csv fresh each time; NEVER modifies the input.
- Round 2 applies the two financial corrections from rounds/round-02.md.
- Round 3 inherits those corrections and appends 2026-10 (rounds/round-03.md).
- Writes to tmp/<run>/A22/round-0X/: dashboard.snapshot, computed-data.json,
  layout-map.json (compared against previous round's tmp layout-map).
- Display rounding is decimal half-up at the very end; all geometry/summaries
  use unrounded values.
"""
import csv
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import a22_common as C  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[4]
CSV_PATH = ROOT / "tasks/A22-staged-data-correction/inputs/monthly.csv"
BASE = ROOT / "tmp/run-20261011-01/A22"

W, H = 1600, 1000
FONT = C.FONT
INK = C.col("ink")
SOFT = C.col("ink_soft")
MUTED = C.col("muted")

# ---- fixed region boxes (identical in all rounds; regression = 0px) --------
REGIONS = {
    "header":    [40, 24, 1560, 96],
    "kpi_row":   [40, 116, 1560, 268],
    "kpi_card_1": [40, 116, 405, 268],
    "kpi_card_2": [425, 116, 790, 268],
    "kpi_card_3": [810, 116, 1175, 268],
    "kpi_card_4": [1195, 116, 1560, 268],
    "chart":     [40, 292, 940, 784],
    "table":     [960, 292, 1560, 784],
    "conclusion": [40, 800, 1560, 968],
}
REGION_STYLE = {
    "header": {"font": FONT, "title_size": 34, "period_size": 26,
               "color": INK, "fill": "#FFFFFF", "border": C.col("line"),
               "radius": 16},
    "kpi_row": {"font": FONT, "label_size": 22, "value_size": 40,
                "unit_size": 24, "note_size": 22, "color": INK,
                "fill": "#FFFFFF", "border": C.col("line"), "radius": 16,
                "cards": 4, "card_w": 365, "card_gap": 20},
    "chart": {"font": FONT, "title_size": 26, "tick_size": 22,
              "label_size": 22, "color": INK, "fill": "#FFFFFF",
              "border": C.col("line"), "radius": 16,
              "plot_box": [150, 350, 920, 730],
              "series": {"net_revenue": C.col("primary"),
                         "operating_profit": C.col("profit"),
                         "profit_negative": C.col("negative")},
              "grid": C.col("grid"), "axis": C.col("axis")},
    "table": {"font": FONT, "title_size": 26, "head_size": 22,
              "cell_size": 22, "color": INK, "fill": "#FFFFFF",
              "border": C.col("line"), "radius": 16,
              "columns": ["月份", "净收入", "经营利润", "退款率", "转化率"]},
    "conclusion": {"font": FONT, "label_size": 22, "text_size": 24,
                   "line": 34, "color": INK, "fill": "#FFFFFF",
                   "border": C.col("line"), "radius": 16},
}
for _k in ("kpi_card_1", "kpi_card_2", "kpi_card_3", "kpi_card_4"):
    REGION_STYLE[_k] = dict(REGION_STYLE["kpi_row"])

AXIS_MAX = 240000
AXIS_MIN_R1 = 0
AXIS_MIN_R23 = -30000

# chart geometry
CX0, CY0, CX1, CY1 = 150, 350, 920, 730      # plot box
CHART_CARD = [40, 292, 940, 784]
TABLE_CARD = [960, 292, 1560, 784]
TBL_IN_X = 972
TBL_RIGHTS = {"net": 1216, "profit": 1346, "refund": 1456, "conv": 1548}
TBL_MONTH_X = 980
CONCL = [40, 800, 1560, 968]


def read_months():
    rows = []
    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as fh:
        for r in csv.DictReader(fh):
            rows.append({
                "month": r["month"],
                "orders": int(r["orders"]),
                "gross_revenue": int(r["gross_revenue"]),
                "refund_amount": int(r["refund_amount"]),
                "operating_cost": int(r["operating_cost"]),
                "sessions": int(r["sessions"]),
            })
    return rows


def apply_round(round_no, months):
    """Return (months, applied_changes). Input data never modified on disk."""
    changes = []
    months = [dict(m) for m in months]
    if round_no >= 2:
        m8 = next(m for m in months if m["month"] == "2026-08")
        old = m8["refund_amount"]
        m8["refund_amount"] = 25048
        changes.append({
            "action": "correction", "field": "refund_amount",
            "month": "2026-08", "old": old, "new": 25048,
            "source": "tasks/A22-staged-data-correction/rounds/round-02.md",
            "input_csv_modified": False,
        })
        m9 = next(m for m in months if m["month"] == "2026-09")
        old = m9["operating_cost"]
        m9["operating_cost"] = 208000
        changes.append({
            "action": "correction", "field": "operating_cost",
            "month": "2026-09", "old": old, "new": 208000,
            "source": "tasks/A22-staged-data-correction/rounds/round-02.md",
            "input_csv_modified": False,
        })
    else:
        changes.append({
            "action": "none", "field": "*", "month": None, "old": None,
            "new": None,
            "source": "inputs/monthly.csv 原始六行数据原样使用",
            "input_csv_modified": False,
        })
    if round_no >= 3:
        months.append({
            "month": "2026-10", "orders": 640, "gross_revenue": 224000,
            "refund_amount": 11200, "operating_cost": 142000,
            "sessions": 5900,
        })
        changes.append({
            "action": "append_month", "field": "row", "month": "2026-10",
            "old": None,
            "new": {"orders": 640, "gross_revenue": 224000,
                    "refund_amount": 11200, "operating_cost": 142000,
                    "sessions": 5900},
            "source": "tasks/A22-staged-data-correction/rounds/round-03.md",
            "input_csv_modified": False,
        })
    return months, changes


def compute(round_no):
    raw = read_months()
    months, changes = apply_round(round_no, raw)
    for m in months:
        m["net_revenue"] = m["gross_revenue"] - m["refund_amount"]
        m["operating_profit"] = m["net_revenue"] - m["operating_cost"]
        m["refund_rate"] = {
            "numerator": m["refund_amount"],
            "denominator": m["gross_revenue"],
            "value": m["refund_amount"] / m["gross_revenue"],
            "display": C.fmt_pct(m["refund_amount"] / m["gross_revenue"]),
        }
        m["conversion"] = {
            "numerator": m["orders"],
            "denominator": m["sessions"],
            "value": m["orders"] / m["sessions"],
            "display": C.fmt_pct(m["orders"] / m["sessions"]),
        }
        m["net_revenue_display"] = C.fmt_int(m["net_revenue"])
        m["operating_profit_display"] = C.fmt_int(m["operating_profit"])
    t = {
        "gross_revenue": sum(m["gross_revenue"] for m in months),
        "refund_amount": sum(m["refund_amount"] for m in months),
        "operating_cost": sum(m["operating_cost"] for m in months),
        "orders": sum(m["orders"] for m in months),
        "sessions": sum(m["sessions"] for m in months),
    }
    t["net_revenue"] = t["gross_revenue"] - t["refund_amount"]
    t["operating_profit"] = t["net_revenue"] - t["operating_cost"]
    t["overall_conversion"] = {
        "numerator": t["orders"], "denominator": t["sessions"],
        "value": t["orders"] / t["sessions"],
        "display": C.fmt_pct(t["orders"] / t["sessions"]),
    }
    t["overall_refund_rate"] = {
        "numerator": t["refund_amount"], "denominator": t["gross_revenue"],
        "value": t["refund_amount"] / t["gross_revenue"],
        "display": C.fmt_pct(t["refund_amount"] / t["gross_revenue"]),
    }
    t["period_start"] = months[0]["month"]
    t["period_end"] = months[-1]["month"]
    t["months"] = len(months)
    return months, changes, t


def conclusions(round_no, months, t):
    by = {m["month"]: m for m in months}
    if round_no == 1:
        text = (
            "2026-04至2026-09累计净收入918,624元、经营利润262,124元，"
            "总体转化率11.15%（3,045单÷27,300次访问）。净收入在2026-06回落至"
            "126,914元后连续三个月走高，2026-09达202,368元为期间峰值；"
            "经营利润同期峰值64,368元，2026-06退款率升至8.00%、净收入回落，"
            "经营利润27,914元为期间低点。"
        )
        claims = [
            {"claim": "期间累计净收入918,624元、经营利润262,124元",
             "cited": {"net_revenue_sum": t["net_revenue"],
                       "operating_profit_sum": t["operating_profit"]}},
            {"claim": "总体转化率11.15%=总订单3,045÷总访问27,300（加权，非各月平均）",
             "cited": {"orders": t["orders"], "sessions": t["sessions"],
                       "value": t["overall_conversion"]["value"]}},
            {"claim": "净收入2026-06回落至126,914元后连续三个月走高，"
                      "2026-09为期间峰值202,368元",
             "cited": {"2026-06": by["2026-06"]["net_revenue"],
                       "2026-09": by["2026-09"]["net_revenue"]}},
            {"claim": "经营利润期间峰值64,368元（2026-09），"
                      "低点27,914元（2026-06，当月退款率8.00%）",
             "cited": {"peak": by["2026-09"]["operating_profit"],
                       "low": by["2026-06"]["operating_profit"],
                       "refund_2026-06": by["2026-06"]["refund_rate"]["value"]}},
        ]
    elif round_no == 2:
        text = (
            "财务更正后（2026-08退款25,048元、2026-09经营成本208,000元）："
            "累计净收入908,624元、经营利润182,124元，较更正前分别减少10,000元、"
            "80,000元。2026-09经营利润-5,632元为唯一负值月份，2026-08退款率升至"
            "13.32%；更正不涉及订单与访问，总体转化率保持11.15%。"
        )
        claims = [
            {"claim": "更正后累计净收入908,624元、经营利润182,124元",
             "cited": {"net_revenue_sum": t["net_revenue"],
                       "operating_profit_sum": t["operating_profit"]}},
            {"claim": "较更正前差额：净收入-10,000元（=退款+10,000元）、"
                      "经营利润-80,000元（退款+10,000+成本+70,000）",
             "cited": {"net_delta": -10000, "profit_delta": -80000}},
            {"claim": "2026-09经营利润-5,632元为唯一负值月份",
             "cited": {"2026-09": by["2026-09"]["operating_profit"]}},
            {"claim": "2026-08退款率13.32%；总体转化率仍11.15%",
             "cited": {"refund_2026-08": by["2026-08"]["refund_rate"]["value"],
                       "overall": t["overall_conversion"]["value"]}},
        ]
    else:
        text = (
            "2026-04至2026-10累计净收入1,121,424元、经营利润252,924元，"
            "总订单3,685笔、总体转化率11.10%（3,685÷33,200）。2026-10单月"
            "净收入212,800元、经营利润70,800元均为期间最高；2026-08退款率13.32%、"
            "2026-09经营成本208,000元使该月利润-5,632元，两项更正继续生效。"
        )
        claims = [
            {"claim": "7个月累计净收入1,121,424元、经营利润252,924元",
             "cited": {"net_revenue_sum": t["net_revenue"],
                       "operating_profit_sum": t["operating_profit"]}},
            {"claim": "总体转化率11.10%=3,685÷33,200（加权）",
             "cited": {"orders": t["orders"], "sessions": t["sessions"],
                       "value": t["overall_conversion"]["value"]}},
            {"claim": "2026-10净收入212,800元、利润70,800元均为期间最高",
             "cited": {"net": by["2026-10"]["net_revenue"],
                       "profit": by["2026-10"]["operating_profit"]}},
            {"claim": "2026-09利润-5,632元（成本208,000元更正），"
                      "2026-08退款率13.32%为期间峰值",
             "cited": {"2026-09": by["2026-09"]["operating_profit"],
                       "refund_2026-08": by["2026-08"]["refund_rate"]["value"]}},
        ]
    # sanity: the headline numbers must match the actual computation
    assert text.find(C.fmt_int(t["net_revenue"])) >= 0, "net sum mismatch"
    assert text.find(C.fmt_int(t["operating_profit"])) >= 0, "profit sum mismatch"
    assert t["overall_conversion"]["display"] in text, "conv mismatch"
    return {"title": "主结论", "display_text": text, "claims": claims}


def axis_spec(round_no, months):
    amin = AXIS_MIN_R1 if round_no == 1 else AXIS_MIN_R23
    span = AXIS_MAX - amin
    # Keep round-01's 60k gridline series and add -30k/0 in rounds 2-3 so
    # gridlines stay comparable across rounds (positions remain true values).
    if round_no == 1:
        ticks = [0, 60000, 120000, 180000, 240000]
    else:
        ticks = [-30000, 0, 60000, 120000, 180000, 240000]
    h = CY1 - CY0
    return {
        "type": "净收入/经营利润共用比例零起点分组柱图",
        "unit": "元",
        "min": amin, "max": AXIS_MAX, "span": span,
        "ticks": ticks,
        "tick_step": 60000,
        "zero_based": True,
        "negative_axis_added": round_no >= 2,
        "plot_box": [CX0, CY0, CX1, CY1],
        "zero_line_y": round(CY1 - (0 - amin) / span * h, 4),
        "px_per_unit": h / span,
        "label_format": "千分位整数元（十进制四舍五入）",
        "scale_from_unrounded": True,
    }


def build_computed(round_no, months, changes, t, axis, concl):
    return {
        "schema_version": 1, "task_id": "A22", "path_base": "output_dir",
        "round": round_no,
        "source": {"path_base": "suite_root",
                   "path": "tasks/A22-staged-data-correction/inputs/monthly.csv",
                   "note": "输入CSV未修改；更正/新增仅作用于本轮计算与显示"},
        "formulas": {
            "net_revenue": "gross_revenue - refund_amount",
            "operating_profit": "net_revenue - operating_cost",
            "refund_rate": "refund_amount / gross_revenue",
            "monthly_conversion": "orders / sessions",
            "overall_conversion": "sum(orders) / sum(sessions)",
            "overall_refund_rate": "sum(refund_amount) / sum(gross_revenue)",
        },
        "precision": {
            "amount": "整数元（原金额整数保留）",
            "percent": "两位小数，十进制四舍五入（半单位绝对值增大）",
            "kpi_amount": "整数元，千分位分隔",
            "note": "汇总/差额/柱高比例均用未舍入值计算，最后一步才格式化",
        },
        "applied_changes": changes,
        "months": [
            {
                "month": m["month"],
                "orders": m["orders"], "gross_revenue": m["gross_revenue"],
                "refund_amount": m["refund_amount"],
                "operating_cost": m["operating_cost"],
                "sessions": m["sessions"],
                "net_revenue": m["net_revenue"],
                "operating_profit": m["operating_profit"],
                "net_revenue_display": m["net_revenue_display"],
                "operating_profit_display": m["operating_profit_display"],
                "refund_rate": dict(m["refund_rate"]),
                "conversion": dict(m["conversion"]),
            } for m in months
        ],
        "totals": {
            "period_start": t["period_start"], "period_end": t["period_end"],
            "months": t["months"],
            "gross_revenue_sum": t["gross_revenue"],
            "refund_amount_sum": t["refund_amount"],
            "operating_cost_sum": t["operating_cost"],
            "net_revenue_sum": t["net_revenue"],
            "operating_profit_sum": t["operating_profit"],
            "orders_sum": t["orders"], "sessions_sum": t["sessions"],
            "net_revenue_sum_display": C.fmt_int(t["net_revenue"]),
            "operating_profit_sum_display": C.fmt_int(t["operating_profit"]),
            "overall_conversion": dict(t["overall_conversion"]),
            "overall_refund_rate": dict(t["overall_refund_rate"]),
        },
        "axes": axis,
        "conclusion": concl,
    }


def build_layout(round_no, prev_round=None):
    regions = []
    for rid, box in REGIONS.items():
        regions.append({
            "id": rid, "box": box, "style": REGION_STYLE[rid],
        })
    comparison = []
    if prev_round:
        prev = json.loads(
            (BASE / ("round-%02d" % prev_round) / "layout-map.json")
            .read_text(encoding="utf-8"))
        prev_boxes = {r["id"]: r["box"] for r in prev["regions"]}
        for rid, box in REGIONS.items():
            pb = prev_boxes.get(rid)
            if pb is None:
                comparison.append({"id": rid, "prev_box": None, "box": box,
                                   "delta": None,
                                   "within_2px": False,
                                   "note": "上轮无此区域"})
                continue
            delta = [box[i] - pb[i] for i in range(4)]
            comparison.append({
                "id": rid, "prev_box": pb, "box": box, "delta": delta,
                "within_2px": all(abs(d) <= 2 for d in delta),
            })
    return {
        "schema_version": 1, "task_id": "A22", "path_base": "output_dir",
        "round": round_no,
        "canvas": [W, H],
        "coordinate_note": "画布左上原点，x向右/y向下，像素单位，box=[left,top,right,bottom]",
        "regions": regions,
        "comparison": comparison,
        "comparison_note": ("首轮为空" if round_no == 1 else
                            "对上轮各区域边界的分量差（要求≤2px）"),
    }


# ---------------------------------------------------------------- DSL build
def draw_header(els, t):
    x, y, x2, y2 = REGIONS["header"]
    els.append(C.rect_at(x, y, x2 - x, y2 - y, C.col("surface"), 16,
                         "1 SOLID %s" % C.col("line")))
    els.append(C.text_el(64, 30, 640, 46, "经营驾驶舱 · 月度经营看板", 34,
                         INK, weight="BOLD"))
    period = "统计期 %s – %s（%d个月）" % (
        t["period_start"].replace("-", "."), t["period_end"].replace("-", "."),
        t["months"])
    els.append(C.text_el(996, 30, 540, 36, period, 26, C.col("primary"),
                         weight="BOLD", align="RIGHT"))
    formula_note = "净收入=收入−退款 · 利润=净收入−经营成本 · 数据源 inputs/monthly.csv"
    els.append(C.text_el(756, 62, 780, 30, formula_note, 22, SOFT,
                         align="RIGHT"))


def draw_kpis(els, t, round_no):
    n = t["months"]
    cards = [
        ("总净收入", C.fmt_int(t["net_revenue"]), "元",
         "收入−退款（%d个月累计）" % n),
        ("总经营利润", C.fmt_int(t["operating_profit"]), "元",
         "净收入−经营成本"),
        ("总订单", C.fmt_int(t["orders"]), "笔", "%d个月合计" % n),
        ("总体转化率", t["overall_conversion"]["display"], None,
         "%s单 ÷ %s次" % (C.fmt_int(t["orders"]), C.fmt_int(t["sessions"]))),
    ]
    xs = [40, 425, 810, 1195]
    for i, (label, value, unit, note) in enumerate(cards):
        x = xs[i]
        els.append(C.rect_at(x, 116, 365, 152, C.col("surface"), 16,
                             "1 SOLID %s" % C.col("line")))
        els.append(C.rect_at(x, 116, 365, 4, C.col("primary") if i != 1
                             else C.col("profit"), 2))
        els.append(C.text_el(x + 22, 132, 321, 30, label, 22, SOFT))
        els.append(C.text_el(x + 22, 166, 330, 54, value, 40, INK,
                             weight="BOLD"))
        if unit:
            ux = x + 22 + C.measure(value, 40) + 10
            els.append(C.text_el(ux, 180, 60, 34, unit, 24, C.col("primary"),
                                 weight="BOLD"))
        els.append(C.text_el(x + 22, 222, 330, 30, note, 22, MUTED))


def draw_chart(els, months, axis, round_no):
    x, y, x2, y2 = CHART_CARD
    els.append(C.rect_at(x, y, x2 - x, y2 - y, C.col("surface"), 16,
                         "1 SOLID %s" % C.col("line")))
    els.append(C.text_el(56, 300, 480, 36, "净收入与经营利润（单位：元）", 26,
                         INK, weight="BOLD"))
    # legend (right aligned on the title row)
    items = [("净收入", C.col("primary")), ("经营利润", C.col("profit"))]
    if round_no >= 2:
        items.append(("利润为负", C.col("negative")))
    widths = [20 + 8 + C.measure(t_, 22) for t_, _ in items]
    total = sum(widths) + 28 * (len(items) - 1)
    lx = 916 - total
    for (t_, colr), wv in zip(items, widths):
        els.append(C.rect_at(lx, 306, 20, 20, colr, 4))
        els.append(C.text_el(lx + 28, 302, wv - 28 + 8, 30, t_, 22, SOFT))
        lx += wv + 28
    # y grid + labels
    span = axis["span"]
    amin = axis["min"]
    h = CY1 - CY0
    for tick in axis["ticks"]:
        ty = CY1 - (tick - amin) / span * h
        if tick == 0:
            continue
        els.append(C.hline(CX0, round(ty, 2), CX1 - CX0, C.col("grid"), 1))
        els.append(C.text_el(46, round(ty - 14, 2), 96, 28, C.fmt_int(tick),
                             22, MUTED, align="RIGHT"))
    # zero label (ticks include 0) already drawn? draw 0 label explicitly
    zy = axis["zero_line_y"]
    els.append(C.text_el(46, zy - 14, 96, 28, "0", 22, MUTED, align="RIGHT"))
    # bars
    count = len(months)
    slot = (CX1 - CX0) / count
    bar_w = 44 if count <= 6 else 38
    gap = 12 if count <= 6 else 10
    group_w = 2 * bar_w + gap
    px = axis["px_per_unit"]
    for i, m in enumerate(months):
        sx = CX0 + i * slot
        start = sx + (slot - group_w) / 2
        ncx = start + bar_w / 2
        pcx = ncx + bar_w + gap
        # net bar
        nv = m["net_revenue"]
        nh = nv * px
        els.append(C.rect_at(round(start, 2), round(zy - nh, 2), bar_w,
                             round(nh, 2), C.col("primary"), 4))
        els.append(C.text_el(round(ncx - 56, 2), round(zy - nh - 28, 2), 112,
                             28, C.fmt_int(nv), 22, INK, weight="BOLD",
                             align="CENTER"))
        # profit bar
        pv = m["operating_profit"]
        px_left = start + bar_w + gap
        if pv >= 0:
            ph = pv * px
            els.append(C.rect_at(round(px_left, 2), round(zy - ph, 2), bar_w,
                                 round(ph, 2), C.col("profit"), 4))
            els.append(C.text_el(round(pcx - 46, 2), round(zy - ph - 28, 2),
                                 112, 28, C.fmt_int(pv), 22, C.col("profit"),
                                 weight="BOLD", align="CENTER"))
        else:
            ph = abs(pv) * px
            els.append(C.rect_at(round(px_left, 2), round(zy, 2), bar_w,
                                 round(ph, 2), C.col("negative"), 4))
            els.append(C.text_el(round(pcx - 46, 2), round(zy + ph + 4, 2),
                                 112, 28, C.fmt_int(pv), 22,
                                 C.col("negative"), weight="BOLD",
                                 align="CENTER"))
        # month label
        els.append(C.text_el(round(sx + 2, 2), 740, round(slot - 4, 2), 30,
                             m["month"], 22, MUTED, align="CENTER"))
    # axes last (over grid, under nothing important)
    for tick in axis["ticks"]:
        ty = CY1 - (tick - amin) / span * h
        if tick == 0:
            continue
    # zero baseline
    els.append(C.hline(CX0, round(zy, 2), CX1 - CX0, C.col("axis"), 2))
    # left axis vertical
    els.append(C.vline(CX0 - 2, CY0, CY1 - CY0 + 2, C.col("grid"), 1))


def draw_table(els, months, round_no):
    x, y, x2, y2 = TABLE_CARD
    els.append(C.rect_at(x, y, x2 - x, y2 - y, C.col("surface"), 16,
                         "1 SOLID %s" % C.col("line")))
    els.append(C.text_el(976, 300, 400, 36,
                         "月度明细（%d个月）" % len(months), 26, INK,
                         weight="BOLD"))
    hy = 344
    hh = 48 if len(months) <= 6 else 44
    els.append(C.rect_at(TBL_IN_X, hy, 1548 - TBL_IN_X, hh,
                         C.col("tint_soft"), 8))
    heads = [("月份", TBL_MONTH_X, "LEFT"),
             ("净收入", TBL_RIGHTS["net"], "RIGHT"),
             ("经营利润", TBL_RIGHTS["profit"], "RIGHT"),
             ("退款率", TBL_RIGHTS["refund"], "RIGHT"),
             ("转化率", TBL_RIGHTS["conv"], "RIGHT")]
    for label, edge, align in heads:
        if align == "LEFT":
            els.append(C.text_el(edge, hy + 12, 120, 30, label, 22, SOFT,
                                 weight="BOLD"))
        else:
            els.append(C.text_el(edge - 130, hy + 12, 130, 30, label, 22,
                                 SOFT, weight="BOLD", align="RIGHT"))
    y0 = hy + hh
    total_h = 764 - y0
    rh = total_h / len(months)
    for i, m in enumerate(months):
        ry = y0 + i * rh
        if i % 2 == 1:
            els.append(C.rect_at(TBL_IN_X, round(ry, 2),
                                 1548 - TBL_IN_X, round(rh, 2),
                                 C.col("tint_soft"), 0))
        cy = round(ry + (rh - 28) / 2, 2)
        els.append(C.text_el(TBL_MONTH_X, cy, 120, 28, m["month"], 22, SOFT))
        els.append(C.text_el(TBL_RIGHTS["net"] - 130, cy, 130, 28,
                             m["net_revenue_display"], 22, INK, align="RIGHT"))
        pv = m["operating_profit"]
        els.append(C.text_el(TBL_RIGHTS["profit"] - 130, cy, 130, 28,
                             C.fmt_int(pv), 22,
                             C.col("negative") if pv < 0 else INK,
                             weight="BOLD" if pv < 0 else None, align="RIGHT"))
        els.append(C.text_el(TBL_RIGHTS["refund"] - 130, cy, 130, 28,
                             m["refund_rate"]["display"], 22, SOFT,
                             align="RIGHT"))
        els.append(C.text_el(TBL_RIGHTS["conv"] - 130, cy, 130, 28,
                             m["conversion"]["display"], 22, SOFT,
                             align="RIGHT"))
    els.append(C.hline(TBL_IN_X, 764, 1548 - TBL_IN_X, C.col("line"), 1))


def draw_conclusion(els, concl, round_no):
    x, y, x2, y2 = CONCL
    els.append(C.rect_at(x, y, x2 - x, y2 - y, C.col("surface"), 16,
                         "1 SOLID %s" % C.col("line")))
    els.append(C.rect_at(64, 818, 5, 24, C.col("primary"), 2.5))
    els.append(C.text_el(78, 814, 300, 30, "主结论", 22, C.col("primary"),
                         weight="BOLD"))
    lines = C.wrap(concl["display_text"], 24, 1472)
    assert len(lines) <= 3, "conclusion wraps to %d lines" % len(lines)
    for i, ln in enumerate(lines):
        els.append(C.text_el(64, 852 + i * 34, 1472, 32, ln, 24, INK))
    return len(lines)


def main():
    round_no = int(sys.argv[1])
    assert round_no in (1, 2, 3)
    gendir = BASE / ("round-%02d" % round_no)
    gendir.mkdir(parents=True, exist_ok=True)

    months, changes, t = compute(round_no)
    axis = axis_spec(round_no, months)
    concl = conclusions(round_no, months, t)

    computed = build_computed(round_no, months, changes, t, axis, concl)
    (gendir / "computed-data.json").write_text(
        json.dumps(computed, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8")

    layout = build_layout(round_no, prev_round=round_no - 1 if round_no > 1 else None)
    (gendir / "layout-map.json").write_text(
        json.dumps(layout, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8")

    els = []
    els.append(C.rect(0, 0, W, H, C.col("bg")))
    draw_header(els, t)
    draw_kpis(els, t, round_no)
    draw_chart(els, months, axis, round_no)
    draw_table(els, months, round_no)
    nlines = draw_conclusion(els, concl, round_no)
    dsl = C.emit(els, W, H, C.col("bg"))
    (gendir / "dashboard.snapshot").write_text(dsl, encoding="utf-8")

    print("round-%d: %d months, %d bytes dsl, conclusion %d lines, "
          "net_sum=%s profit_sum=%s conv=%s, axis=[%d..%d]"
          % (round_no, len(months), len(dsl.encode("utf-8")), nlines,
             C.fmt_int(t["net_revenue"]), C.fmt_int(t["operating_profit"]),
             t["overall_conversion"]["display"], axis["min"], axis["max"]))
    if round_no > 1:
        bad = [c for c in layout["comparison"] if not c["within_2px"]]
        print("region comparison vs round-%d: %s"
              % (round_no - 1, "ALL <=2px" if not bad else bad))


if __name__ == "__main__":
    main()
