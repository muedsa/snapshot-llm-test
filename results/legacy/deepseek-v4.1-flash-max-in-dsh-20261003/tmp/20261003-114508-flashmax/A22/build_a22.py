"""A22 business cockpit builder.

Data is recomputed from inputs/monthly.csv for every round; the round-2 corrections and
the round-3 extra month are applied as *data* overrides, never as hand-written numbers.
All money is in whole CNY, all rates in percent.
"""
from __future__ import annotations

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "_suite", "shared"))
from snapkit import (CJK, LINE_HEIGHT, MONO, Doc, assert_fits, card,  # noqa: E402
                     contrast, text_width)

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
OUT = os.path.join(ROOT, "outputs", "20261003-114508-flashmax", "A22")
TMP = os.path.join(ROOT, "tmp", "20261003-114508-flashmax", "A22")
CSV = os.path.join(ROOT, "tasks", "A22-staged-data-correction", "inputs", "monthly.csv")

W, H = 1600, 1000
# Region boundaries. Round 2 requires them to stay within +-2px of the previous round, so
# they are identical in all three rounds; only the row count inside the table panel and
# the numbers inside every region change.
REG = dict(header=[28, 20, 1572, 112], kpis=[28, 142, 1544, 128],
           conclusion=[28, 282, 1544, 96],
           chart=[28, 390, 1108, 436], table=[1148, 390, 424, 436],
           footer=[28, 822, 1572, 120])
CARD_W, CARD_GAP = 380, 8
CARD_X = [28 + i * (CARD_W + CARD_GAP) for i in range(4)]

INK = "#0F172AFF"
SUB = "#475569FF"
LINE = "#E2E8F0FF"
NET = "#1D4ED8FF"
PROFIT = "#0E9F8FFF"
NEG = "#D92D20FF"
WARN = "#D97706FF"
HEAD_BG = "#0F172AFF"
PAGE = "#F1F5F9FF"


# ----------------------------------------------------------------------------- data
def read_csv() -> list:
    rows = []
    with open(CSV, encoding="utf-8") as fh:
        head = fh.readline().strip().split(",")
        for line in fh:
            line = line.strip()
            if not line:
                continue
            vals = line.split(",")
            rec = {k: (v if k == "month" else float(v)) for k, v in zip(head, vals)}
            rows.append(rec)
    return rows


CORRECTIONS = {  # round 2: the two finance corrections from rounds/round-02.md
    "2026-08": {"refund_amount": 25048},
    "2026-09": {"operating_cost": 208000},
}
NEW_MONTH = {"month": "2026-10", "orders": 640, "gross_revenue": 224000,
             "refund_amount": 11200, "operating_cost": 142000, "sessions": 5900}


def compute(rnd: int) -> dict:
    base = read_csv()
    applied = []
    if rnd >= 2:
        for m, patch in CORRECTIONS.items():
            for r in base:
                if r["month"] == m:
                    for k, v in patch.items():
                        applied.append(dict(month=m, field=k, old=r[k], new=v,
                                            source="rounds/round-02.md"))
                        r[k] = v
    if rnd >= 3:
        base.append(dict(NEW_MONTH))
        applied.append(dict(month="2026-10", field="row", old=None, new=NEW_MONTH,
                            source="rounds/round-03.md"))
    months = []
    for r in base:
        net = r["gross_revenue"] - r["refund_amount"]
        profit = net - r["operating_cost"]
        months.append({
            "month": r["month"],
            "orders": int(r["orders"]),
            "sessions": int(r["sessions"]),
            "gross_revenue": int(r["gross_revenue"]),
            "refund_amount": int(r["refund_amount"]),
            "operating_cost": int(r["operating_cost"]),
            "net_revenue": int(net),
            "operating_profit": int(profit),
            "refund_rate": round(r["refund_amount"] / r["gross_revenue"] * 100, 2),
            "conversion_rate": round(r["orders"] / r["sessions"] * 100, 2),
        })
    tot = {
        "months": len(months),
        "period": f'{months[0]["month"]} .. {months[-1]["month"]}',
        "orders": sum(m["orders"] for m in months),
        "sessions": sum(m["sessions"] for m in months),
        "gross_revenue": sum(m["gross_revenue"] for m in months),
        "refund_amount": sum(m["refund_amount"] for m in months),
        "operating_cost": sum(m["operating_cost"] for m in months),
        "net_revenue": sum(m["net_revenue"] for m in months),
        "operating_profit": sum(m["operating_profit"] for m in months),
    }
    tot["refund_rate"] = round(tot["refund_amount"] / tot["gross_revenue"] * 100, 2)
    tot["conversion_rate"] = round(tot["orders"] / tot["sessions"] * 100, 2)
    best = max(months, key=lambda m: m["operating_profit"])
    worst = min(months, key=lambda m: m["operating_profit"])
    first, last = months[0], months[-1]
    return dict(months=months, totals=tot, corrections_applied=applied,
                derived=dict(best_profit_month=best["month"],
                             best_profit=best["operating_profit"],
                             worst_profit_month=worst["month"],
                             worst_profit=worst["operating_profit"],
                             last_month=last["month"],
                             net_growth_first_to_last=last["net_revenue"] - first["net_revenue"],
                             negative_profit_months=[m["month"] for m in months
                                                     if m["operating_profit"] < 0],
                             max_net_revenue=max(m["net_revenue"] for m in months),
                             min_operating_profit=worst["operating_profit"]))


def fmt(n: int) -> str:
    return f"{n:,}"


def conclusion_text(d: dict, rnd: int) -> tuple:
    """Returns two lines; both are asserted to fit the conclusion band at 22px."""
    t = d["totals"]
    dd = d["derived"]
    if rnd == 1:
        return (f'{t["months"]} 个月合计：净收入 {fmt(t["net_revenue"])} 元，'
                f'经营利润 {fmt(t["operating_profit"])} 元，'
                f'总订单 {fmt(t["orders"])} 单，总体转化率 {t["conversion_rate"]:.2f}%。',
                f'利润最高月 {dd["best_profit_month"]}（{fmt(dd["best_profit"])} 元）；'
                f'净收入由 {d["months"][0]["month"]} 的 {fmt(d["months"][0]["net_revenue"])} '
                f'元升至 {dd["last_month"]} 的 {fmt(d["months"][-1]["net_revenue"])} 元，'
                f'全部月份经营利润为正。')
    if rnd == 2:
        return (f'更正后 {t["months"]} 个月合计：净收入 {fmt(t["net_revenue"])} 元，'
                f'经营利润 {fmt(t["operating_profit"])} 元，'
                f'总体转化率 {t["conversion_rate"]:.2f}%。',
                f'{dd["worst_profit_month"]} 是唯一经营利润为负的月份'
                f'（{fmt(dd["worst_profit"])} 元），其余月份为正；'
                f'利润最高月仍为 {dd["best_profit_month"]}'
                f'（{fmt(dd["best_profit"])} 元）。')
    return (f'{t["months"]} 个月（{t["period"]}）合计：净收入 {fmt(t["net_revenue"])} 元，'
            f'经营利润 {fmt(t["operating_profit"])} 元，'
            f'总体转化率 {t["conversion_rate"]:.2f}%。',
            f'末月 {dd["last_month"]} 净收入 {fmt(d["months"][-1]["net_revenue"])} 元、'
            f'经营利润 {fmt(d["months"][-1]["operating_profit"])} 元；'
            f'{dd["worst_profit_month"]} 仍为唯一经营利润为负的月份。')


# ------------------------------------------------------------------------- drawing
def draw(d: dict, rnd: int) -> tuple:
    doc = Doc(W, H, background=PAGE)
    measured = []
    months = d["months"]
    t = d["totals"]
    title = "叠光 2026 经营驾驶舱"
    sub = ("数据来源 inputs/monthly.csv"
           + ("；已应用 2026-08 退款更正与 2026-09 成本更正" if rnd >= 2 else "")
           + ("；含 2026-10 新增月份" if rnd >= 3 else ""))

    # ------------------------------------------------------------------ header
    hx, hy, hw, hh = REG["header"]
    doc.box(hx, hy, hw, hh, HEAD_BG, radius=18)
    doc.text(hx + 28, hy + 14, title, 34, "#F8FAFCFF", weight="BOLD", maxw=hw - 420)
    doc.rtext(hx + hw - 28, hy + 30, f'{t["months"]} 个月 · {t["period"]}', 22,
              "#94A3B8FF")
    doc.text(hx + 28, hy + 78, sub, 20, "#CBD5E1FF", maxw=hw - 56)

    # -------------------------------------------------------------------- KPIs
    kx, ky, kw, kh = REG["kpis"]
    kpis = [
        ("总净收入", fmt(t["net_revenue"]), "元", "收入 − 退款", NET),
        ("总经营利润", fmt(t["operating_profit"]), "元", "净收入 − operating_cost", PROFIT),
        ("总订单", fmt(t["orders"]), "单", f'{fmt(t["sessions"])} 次 sessions', WARN),
        ("总体转化率", f'{t["conversion_rate"]:.2f}', "%", "总订单 ÷ 总 sessions", NEG),
    ]
    for i, (label, value, unit, note, col) in enumerate(kpis):
        x = CARD_X[i]
        card(doc, x, ky, CARD_W, kh, radius=16)
        doc.box(x, ky, 6, kh, col, tl=16, bl=16, tr=0, br=0)
        doc.text(x + 26, ky + 14, label, 22, SUB, maxw=CARD_W - 44)
        vw = text_width(value, 48, mono=True)
        doc.text(x + 26, ky + 44, value, 48, INK, weight="BOLD", family=MONO,
                 maxw=CARD_W - 44)
        doc.text(x + 30 + vw, ky + 66, unit, 22, SUB, maxw=CARD_W - 54 - vw)
        doc.text(x + 26, ky + 98, note, 20, "#64748BFF", maxw=CARD_W - 44)
        measured.append(dict(text=label, size=22, color=SUB, y=ky + 14, role="kpi_label"))
        measured.append(dict(text=value, size=48, color=INK, y=ky + 44, role="kpi_value"))
        measured.append(dict(text=note, size=20, color="#64748BFF", y=ky + 98,
                             role="kpi_note"))

    # -------------------------------------------------------------- conclusion
    cx, cy, cw, ch = REG["conclusion"]
    doc.box(cx, cy, cw, ch, "#FFFFFFFF", radius=16, border=f"1 SOLID {LINE}")
    doc.box(cx, cy, 6, ch, NET, tl=16, bl=16, tr=0, br=0)
    doc.text(cx + 26, cy + 12, "主结论（仅依据本图实际数值）", 22, NET, weight="BOLD",
             maxw=cw - 52)
    cl1, cl2 = conclusion_text(d, rnd)
    assert_fits(cl1, 22, cw - 60, "conclusion-1")
    assert_fits(cl2, 22, cw - 60, "conclusion-2")
    doc.text(cx + 26, cy + 42, cl1, 22, INK, maxw=cw - 52)
    doc.text(cx + 26, cy + 72, cl2, 22, INK, maxw=cw - 52)
    measured.append(dict(text=cl1, size=22, color=INK, y=cy + 42, role="conclusion"))
    measured.append(dict(text=cl2, size=22, color=INK, y=cy + 72, role="conclusion"))

    # ----------------------------------------------------------------- chart
    px, py, pw, ph = REG["chart"]
    card(doc, px, py, pw, ph, radius=16)
    doc.text(px + 24, py + 14, "净收入 / 经营利润（共用零起点）", 24, INK, weight="BOLD",
             maxw=390)
    lx = px + 430
    ly = py + 34
    for lbl, col in (("净收入", NET), ("经营利润", PROFIT), ("零起点", NEG)):
        doc.box(lx, ly - 6, 22, 12, col, radius=6)
        doc.text(lx + 30, ly - 12, lbl, 20, SUB, maxw=int(text_width(lbl, 20)) + 8)
        lx += 30 + int(text_width(lbl, 20)) + 34
    doc.rtext(px + pw - 24, py + 18, "单位：元", 20, "#64748BFF")

    plot_x0, plot_x1 = px + 118, px + pw - 24
    plot_top, plot_bot = py + 82, py + ph - 46
    VMIN, VMAX = -40000, 220000
    zero_y = plot_bot - (0 - VMIN) / (VMAX - VMIN) * (plot_bot - plot_top)

    def yval(v):
        return plot_bot - (v - VMIN) / (VMAX - VMIN) * (plot_bot - plot_top)

    # gridlines + value axis
    for gv in (-40000, 0, 50000, 100000, 150000, 200000):
        gy = round(yval(gv))
        if gv == 0:
            continue
        doc.box(plot_x0, gy, plot_x1 - plot_x0, 1, "#EEF2F6FF")
        doc.rtext(plot_x0 - 12, gy - 13, fmt(gv), 20, "#64748BFF", family=MONO)
    doc.box(plot_x0, round(zero_y), plot_x1 - plot_x0, 2, "#94A3B8FF")

    n = len(months)
    step = (plot_x1 - plot_x0) / n
    bw, bgap = 32.0, 8.0
    for i, m in enumerate(months):
        gx = plot_x0 + step * (i + 0.5)
        net_x = gx - (bw + bgap / 2)
        prof_x = gx + bgap / 2
        net_top = min(yval(m["net_revenue"]), zero_y)
        net_h = abs(yval(m["net_revenue"]) - zero_y)
        doc.box(round(net_x), round(net_top), round(bw), max(2, round(net_h)), NET,
                radius=6)
        prof_top = min(yval(m["operating_profit"]), zero_y)
        prof_h = abs(yval(m["operating_profit"]) - zero_y)
        col = NEG if m["operating_profit"] < 0 else PROFIT
        doc.box(round(prof_x), round(prof_top), round(bw), max(2, round(prof_h)), col,
                radius=6)
        label = m["month"][5:]
        doc.text(round(gx - text_width(label, 20, mono=True) / 2), plot_bot + 10, label,
                 20, SUB, family=MONO)
        measured.append(dict(text=label, size=20, color=SUB, y=plot_bot + 10,
                             role="axis_x"))
        # value callouts for the last month only (avoid clutter on short bars)
        if i == n - 1:
            doc.text(round(gx - 40), round(yval(m["net_revenue"]) - 30), fmt(m["net_revenue"]),
                     20, NET, family=MONO, maxw=110)
            doc.text(round(gx - 40), round(zero_y + 10), fmt(m["operating_profit"]), 20,
                     col, family=MONO, maxw=110)

    # ----------------------------------------------------------------- table
    tx, ty, tw, th = REG["table"]
    card(doc, tx, ty, tw, th, radius=16)
    doc.text(tx + 18, ty + 12, "月度明细", 24, INK, weight="BOLD", maxw=170)
    doc.rtext(tx + tw - 18, ty + 18, f"{n} 行", 20, "#64748BFF")
    ttop = ty + 48
    # every row (text and its tint) must stay inside the panel: solve the row height from
    # the bottom edge instead of guessing it
    rh = (ty + th - 14 - ttop) / (n + 1)
    assert rh >= 40, f"table rows would be crushed to {rh:.1f}px"
    # explicit pixel columns: month | net revenue | operating profit | refund | conversion
    _hdr = [("月份", "left", 20, CJK), ("净收入", "right", 20, MONO),
            ("经营利润", "right", 20, MONO), ("退款率", "right", 20, MONO),
            ("转化率", "right", 20, MONO)]
    _vals = [["月份"] + [m["month"] for m in months],
             ["净收入"] + [fmt(m["net_revenue"]) for m in months],
             ["经营利润"] + [fmt(m["operating_profit"]) for m in months],
             ["退款率"] + [f'{m["refund_rate"]:.2f}%' for m in months],
             ["转化率"] + [f'{m["conversion_rate"]:.2f}%' for m in months]]
    _w = [max(text_width(v, 20, mono=(fam is MONO)) for v in col) + 6
          for col, _a, _sz, fam in zip(_vals, [c[1] for c in _hdr],
                                       [c[2] for c in _hdr], [c[3] for c in _hdr])]
    _avail = tw - 32
    if sum(_w) > _avail:
        k = _avail / sum(_w)
        _w = [x * k for x in _w]
    _gap = (_avail - sum(_w)) / 4
    cols = []
    _x = 16.0
    for i, (name, align, sz, fam) in enumerate(_hdr):
        cols.append((name, round(_x), round(_w[i]), align, fam))
        _x += _w[i] + _gap
    for name, off, wdt, align, _fam in cols:
        yy = round(ttop + rh * 0.30)
        if align == "right":
            doc.rtext(tx + off + wdt, yy, name, 20, "#64748BFF", weight="BOLD")
        else:
            doc.text(tx + off, yy, name, 20, "#64748BFF", weight="BOLD", maxw=wdt)
        measured.append(dict(text=name, size=20, color="#64748BFF", y=yy,
                             role="table_head"))
    doc.box(tx + 16, round(ttop + rh - 1), tw - 32, 2, "#CBD5E1FF")
    for i, m in enumerate(months):
        ry = ttop + rh * (i + 1)
        if m["month"] == "2026-10":
            # the new month is marked by its own accent tint and rail, painted BEFORE the
            # values of the row so the mark can never cover the numbers
            doc.box(tx + 12, round(ry), tw - 24, round(rh), "#ECFDF5FF", radius=8)
            doc.box(tx + 12, round(ry), 4, round(rh), PROFIT, radius=2)
        elif i % 2 == 1:
            doc.box(tx + 12, round(ry), tw - 24, round(rh), "#F8FAFCFF", radius=8)
        vals = [(m["month"], INK, "left", CJK),
                (fmt(m["net_revenue"]), INK, "right", MONO),
                (fmt(m["operating_profit"]),
                 NEG if m["operating_profit"] < 0 else INK, "right", MONO),
                (f'{m["refund_rate"]:.2f}%', SUB, "right", MONO),
                (f'{m["conversion_rate"]:.2f}%', SUB, "right", MONO)]
        for j, (val, col, align, fam) in enumerate(vals):
            _name, off, wdt, _al, _fam = cols[j]
            yy = round(ry + max(6, (rh - 26) / 2))
            if align == "right":
                doc.rtext(tx + off + wdt, yy, val, 20, col, family=fam)
            else:
                doc.text(tx + off, yy, val, 20, col, weight="BOLD", family=fam,
                         maxw=wdt)
            measured.append(dict(text=val, size=20, color=col, y=yy, role="table_row"))
    assert ttop + rh * (n + 1) <= ty + th - 10, "table rows overflow the panel"

    # ------------------------------------------------------------------ footer
    fx, fy, fw, fh = REG["footer"]
    doc.box(fx, fy, fw, fh, "#FFFFFFFF", radius=16, border=f"1 SOLID {LINE}")
    notes = [
        "净收入 = gross_revenue − refund_amount；经营利润 = 净收入 − operating_cost。",
        "退款率 = refund_amount ÷ gross_revenue；转化率 = orders ÷ sessions。",
        ("更正已生效：2026-08 refund_amount 15048 → 25048，2026-09 operating_cost "
         "138000 → 208000（旧值即 CSV 原始数据）。" if rnd >= 2 else
         "本轮使用 CSV 原始数据，未做任何人工调整。"),
        (f'总体转化率按全部 {t["months"]} 个月的 orders 合计 ÷ sessions 合计计算，'
         f'不是各月转化率的平均；表格绿色标记行为新增月份 2026-10。' if rnd >= 3 else
         "总体转化率按全部 6 个月的 orders 合计 ÷ sessions 合计计算，"
         "不是各月转化率的平均；表格与柱高来自同一份计算结果。"),
    ]
    for i, nt in enumerate(notes):
        assert_fits(nt, 20, fw - 56, "footer")
        doc.text(fx + 26, fy + 12 + i * 26, nt, 20, SUB, maxw=fw - 56)
        measured.append(dict(text=nt, size=20, color=SUB, y=fy + 12 + i * 26,
                             role="footer"))

    return doc, measured, dict(months=[m["month"] for m in months],
                               zero_y=round(zero_y), plot=[plot_x0, plot_top, plot_x1,
                                                           plot_bot],
                               vmin=VMIN, vmax=VMAX,
                               table_row_height=round(rh, 2))


# ------------------------------------------------------------------------- layout map
def layout_map(geom: dict, rnd: int) -> dict:
    return {
        "task": "A22", "round": rnd, "canvas": [W, H],
        "tolerance_vs_previous_round_px": 2,
        "regions": {
            "header": {"bounds": REG["header"], "style":
                       {"fill": "#0F172A", "radius": 18, "title_size": 34,
                        "meta_size": 22, "note_size": 20}},
            "kpi": {"bounds": REG["kpis"], "cards": [
                {"bounds": [CARD_X[i], REG["kpis"][1], CARD_W, REG["kpis"][3]],
                 "accent": c} for i, c in
                enumerate([NET, PROFIT, WARN, NEG])],
                "style": {"fill": "#FFFFFF", "border": "#E2E8F0", "radius": 16,
                          "label_size": 22, "value_size": 52, "note_size": 20}},
            "conclusion": {"bounds": REG["conclusion"],
                           "style": {"fill": "#FFFFFF", "border": "#E2E8F0",
                                     "radius": 16, "label_size": 22, "text_size": 22}},
            "chart": {"bounds": REG["chart"],
                      "plot": geom["plot"], "value_axis": [geom["vmin"], geom["vmax"]],
                      "zero_line_y": geom["zero_y"],
                      "series": [{"key": "net_revenue", "fill": "#1D4ED8"},
                                 {"key": "operating_profit", "fill": "#0E9F8F",
                                  "negative_fill": "#D92D20"}],
                      "style": {"fill": "#FFFFFF", "radius": 16, "title_size": 24,
                                "tick_size": 20}},
            "table": {"bounds": REG["table"], "row_height": geom["table_row_height"],
                      "columns": ["月份", "净收入", "经营利润", "退款率", "转化率"],
                      "style": {"fill": "#FFFFFF", "radius": 16, "header_size": 20,
                                "cell_size": 22}},
            "footer": {"bounds": REG["footer"],
                       "style": {"fill": "#FFFFFF", "border": "#E2E8F0", "radius": 16,
                                 "text_size": 20}},
        },
        "style_scale": {"body_min_size": 20, "body_sizes_used": [20, 22, 24, 34, 52],
                        "fonts": [CJK, MONO]},
    }


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", default="1,2,3")
    args = ap.parse_args()
    want = [int(x) for x in args.rounds.split(",") if x.strip()]
    os.makedirs(TMP, exist_ok=True)
    for rnd in want:
        sub = os.path.join(OUT, f"round-{rnd:02d}")
        os.makedirs(sub, exist_ok=True)
        data = compute(rnd)
        doc, measured, geom = draw(data, rnd)
        dsl = doc.finish()
        for path in (os.path.join(sub, "dashboard.snapshot"),
                     os.path.join(TMP, f"dashboard.r{rnd}.snapshot")):
            with open(path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(dsl)
        payload = dict(data)
        payload.update({"task": "A22", "round": rnd,
                        "formulas": {
                            "net_revenue": "gross_revenue - refund_amount",
                            "operating_profit": "net_revenue - operating_cost",
                            "refund_rate_pct": "refund_amount / gross_revenue * 100",
                            "conversion_rate_pct": "orders / sessions * 100",
                            "overall_conversion_pct": "sum(orders) / sum(sessions) * 100"},
                        "input": "tasks/A22-staged-data-correction/inputs/monthly.csv",
                        "generator": "tmp/20261003-114508-flashmax/A22/build_a22.py",
                        "verified": {"zero_based_bar_chart": True,
                                     "negative_values_kept_signed": True,
                                     "all_months_present": [m["month"] for m in data["months"]]}})
        with open(os.path.join(sub, "computed-data.json"), "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
        with open(os.path.join(sub, "layout-map.json"), "w", encoding="utf-8") as fh:
            json.dump(layout_map(geom, rnd), fh, ensure_ascii=False, indent=2)
        with open(os.path.join(TMP, f"computed.r{rnd}.json"), "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
        print(json.dumps({"round": rnd, "months": len(data["months"]),
                          "net_revenue": data["totals"]["net_revenue"],
                          "operating_profit": data["totals"]["operating_profit"],
                          "overall_conversion": data["totals"]["conversion_rate"],
                          "negative_months": data["derived"]["negative_profit_months"]},
                         ensure_ascii=False))


if __name__ == "__main__":
    main()
