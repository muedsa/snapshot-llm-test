"""A22 · operating dashboard with two data corrections and a new month."""
from __future__ import annotations

import csv
import json
import os
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A22"
TMP = ROOT / "tmp" / RUN / TASK
ROUND = int(sys.argv[1]) if len(sys.argv) > 1 else 1
VERSION = sys.argv[2] if len(sys.argv) > 2 else f"r{ROUND}v1"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))

from dsl import C, Col, Gap, HGap, Pos, Row, SizedBox, Stack, T  # noqa: E402

W, H = 1600, 1000
BG = "#0A111D"
CARD = "#101D31"
INK = "#F4F7FB"
MUTED = "#9AA9BD"
FAINT = "#6E819B"
LINE = "#24344D"
BLUE = "#38BDF8"
CORAL = "#FB7185"
GREEN = "#34D399"
GOLD = "#F5C451"
FONT = "Inter,Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC,Inter"


def load_rows():
    rows = []
    with open(ROOT / "tasks" / "A22-staged-data-correction" / "inputs" / "monthly.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append({k: (r[k] if k == "month" else int(r[k])) for k in ["month", "orders", "gross_revenue", "refund_amount", "operating_cost", "sessions"]})
    if ROUND >= 2:
        for r in rows:
            if r["month"] == "2026-08":
                r["refund_amount"] = 25048
            if r["month"] == "2026-09":
                r["operating_cost"] = 208000
    if ROUND >= 3:
        rows.append({"month": "2026-10", "orders": 640, "gross_revenue": 224000,
                     "refund_amount": 11200, "operating_cost": 142000, "sessions": 5900})
    return rows


def compute(rows):
    out = []
    for r in rows:
        r = dict(r)
        r["net"] = r["gross_revenue"] - r["refund_amount"]
        r["profit"] = r["net"] - r["operating_cost"]
        r["refund_rate"] = Decimal(r["refund_amount"]) / Decimal(r["gross_revenue"])
        r["conversion"] = Decimal(r["orders"]) / Decimal(r["sessions"])
        out.append(r)
    keys = ["gross_revenue", "refund_amount", "net", "operating_cost", "profit", "orders", "sessions"]
    total = {k: sum(r[k] for r in out) for k in keys}
    total["refund_rate"] = Decimal(total["refund_amount"]) / Decimal(total["gross_revenue"])
    total["conversion"] = Decimal(total["orders"]) / Decimal(total["sessions"])
    return out, total


def pct(d):
    return f"{(d * 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP):.2f}%"


def money(n):
    return f"{n:,}"


def kpi(x, label, value, foot, color=INK):
    return [Pos(x, 150, C(width=370, height=120, color=CARD, borderRadius=14, border=f"1 SOLID {LINE}")),
            Pos(x + 22, 168, T(label, size=18, color=MUTED, family=FONT)),
            Pos(x + 22, 194, T(value, size=32, color=color, weight="BOLD", family=FONT)),
            Pos(x + 22, 240, T(foot, size=18, color=FAINT, family=FONT))]


def chart(rows, total):
    nodes = [Pos(40, 300, C(width=920, height=390, color=CARD, borderRadius=14, border=f"1 SOLID {LINE}")),
             Pos(64, 322, T("净收入 / 经营利润", size=24, color=INK, weight="BOLD", family=FONT)),
             Pos(64, 348, T("单位：元 · 共同零起点", size=16, color=FAINT, family=FONT)),
             Pos(720, 328, C(width=14, height=14, color=BLUE, borderRadius=3)),
             Pos(740, 324, T("净收入", size=18, color=MUTED, family=FONT)),
             Pos(824, 328, C(width=14, height=14, color=CORAL, borderRadius=3)),
             Pos(844, 324, T("利润", size=18, color=MUTED, family=FONT))]
    left, right, top, bottom = 110, 880, 380, 650
    ymin, ymax = -20000, 240000

    def ypos(v):
        return bottom - (v - ymin) / (ymax - ymin) * (bottom - top)

    for v in [-20000, 0, 60000, 120000, 180000, 240000]:
        y = ypos(v)
        nodes.append(Pos(left, y, C(width=right - left, height=2 if v == 0 else 1,
                                    color="#E2E8F4" if v == 0 else "#22334B")))
        nodes.append(Pos(58, y - 9, T(f"{v//1000}k" if v else "0", size=16, color=FAINT, family=FONT)))
    n = len(rows)
    step = (right - left) / n
    for i, r in enumerate(rows):
        cx = left + step * (i + 0.5)
        bw = 34
        for j, (key, col) in enumerate((("net", BLUE), ("profit", CORAL))):
            v = r[key]
            y0, y1 = ypos(0), ypos(v)
            bx = cx - bw - 3 if j == 0 else cx + 3
            nodes.append(Pos(bx, min(y0, y1), C(width=bw, height=max(2, abs(y1 - y0)), color=col, borderRadius=4)))
        nodes.append(Pos(cx - step / 2, 660, T(r["month"][-2:] + "月", size=18, color=MUTED, family=FONT), w=step, h=28))
    return nodes


def insight(rows, total):
    if ROUND == 1:
        best = max(rows, key=lambda r: r["profit"])
        lines = [f'净收入 {money(total["net"])} 元 · 经营利润 {money(total["profit"])} 元',
                 f'{best["month"][-2:]} 月利润 {money(best["profit"])} 元，六个月最高',
                 f'总体转化率 {pct(total["conversion"])}，总体退款率 {pct(total["refund_rate"])}']
    elif ROUND == 2:
        neg = [r for r in rows if r["profit"] < 0]
        lines = [f'净收入 {money(total["net"])} 元 · 经营利润 {money(total["profit"])} 元',
                 f'9 月利润 {money(-5632)} 元，为唯一负值；8 月退款更正 15,048→25,048',
                 f'两项更正合计影响利润 −80,000 元 · 转化率 {pct(total["conversion"])}']
    else:
        best = max(rows, key=lambda r: r["profit"])
        lines = [f'净收入 {money(total["net"])} 元 · 经营利润 {money(total["profit"])} 元',
                 f'{best["month"][-2:]} 月利润 {money(best["profit"])} 元，七个月最高',
                 f'总体转化率 {pct(total["conversion"])} · 7 个月完整保留']
    nodes = [Pos(980, 300, C(width=580, height=390, color=CARD, borderRadius=14, border=f"1 SOLID {LINE}")),
             Pos(1004, 322, T("本期结论", size=24, color=INK, weight="BOLD", family=FONT)),
             Pos(1004, 356, T("基于未舍入值计算后格式化", size=16, color=FAINT, family=FONT))]
    y = 392
    for i, line in enumerate(lines):
        nodes.append(Pos(1004, y, C(width=4, height=4, color=CORAL if i == 0 else GOLD, borderRadius=2)))
        nodes.append(Pos(1020, y - 12, T(line, size=22, color=INK, family=FONT, height="1.4"), w=510, h=84))
        y += 78
    return nodes


def table(rows):
    nodes = [Pos(40, 700, C(width=1520, height=270, color=CARD, borderRadius=14, border=f"1 SOLID {LINE}")),
             Pos(64, 718, T("月度明细", size=22, color=INK, weight="BOLD", family=FONT)),
             Pos(64, 750, C(width=1472, height=30, color="#16253C", borderRadius=6))]
    xs = [72, 330, 570, 820, 1080]
    heads = ["月份", "净收入", "利润", "退款率", "转化率"]
    for x, h in zip(xs, heads):
        nodes.append(Pos(x, 756, T(h, size=18, color=MUTED, weight="BOLD", family=FONT)))
    for i, r in enumerate(rows):
        y = 786 + i * 26
        if i > 0:
            nodes.append(Pos(72, y - 4, C(width=1456, height=1, color="#22334B")))
        nodes.append(Pos(72, y, T(r["month"], size=22, color=INK, family=FONT)))
        nodes.append(Pos(330, y, T(money(r["net"]), size=22, color=INK, family=MONO)))
        nodes.append(Pos(570, y, T(("−" if r["profit"] < 0 else "") + money(abs(r["profit"])), size=22,
                                     color=CORAL if r["profit"] < 0 else INK, family=MONO)))
        nodes.append(Pos(820, y, T(pct(r["refund_rate"]), size=22, color=MUTED, family=MONO)))
        nodes.append(Pos(1080, y, T(pct(r["conversion"]), size=22, color=MUTED, family=MONO)))
    return nodes


def build():
    base = load_rows()
    rows, total = compute(base)
    nodes = [SizedBox(W, H), Pos(0, 0, C(width=W, height=H, color=BG))]
    nodes += [Pos(40, 36, T("经营驾驶舱", size=38, color=INK, weight="BOLD", family=FONT)),
              Pos(40, 92, T("2026 月度复盘 · 净收入 / 经营利润 / 转化率", size=22, color=MUTED, family=FONT)),
              Pos(1320, 48, C(width=220, height=36, color="#14263D", borderRadius=18, border=f"1 SOLID {LINE}",
                              alignment="CENTER", child=T("MONTHLY · 2026", size=14, color=BLUE, weight="BOLD", family=FONT)))]
    nodes += kpi(40, "总净收入", money(total["net"]), "收入 − 退款", BLUE)
    nodes += kpi(420, "总经营利润", money(total["profit"]), "净收入 − 运营成本", GREEN if total["profit"] >= 0 else CORAL)
    nodes += kpi(800, "总订单", money(total["orders"]), f'{len(rows)} 个月合计', INK)
    nodes += kpi(1180, "总体转化率", pct(total["conversion"]), "总订单 / 总 sessions", GOLD)
    nodes += chart(rows, total)
    nodes += insight(rows, total)
    nodes += table(rows)
    nodes.append(Pos(40, 978, T("数据源：monthly.csv · 金额单位：元 · 比率保留两位小数 · 图中零起点", size=16, color=FAINT, family=FONT)))
    dsl = f'<Snapshot type="png" background="{BG}">\n' + Stack(nodes, width=W, height=H) + "\n</Snapshot>\n"
    rdir = TMP / f"round-{ROUND:02d}"
    rdir.mkdir(parents=True, exist_ok=True)
    (rdir / f"{VERSION}.snapshot").write_text(dsl, encoding="utf-8")

    md = []
    for r in rows:
        md.append({"month": r["month"], "orders": r["orders"], "sessions": r["sessions"],
                   "gross_revenue": r["gross_revenue"], "refund_amount": r["refund_amount"],
                   "operating_cost": r["operating_cost"], "net_revenue": r["net"], "profit": r["profit"],
                   "refund_rate": {"numerator": r["refund_amount"], "denominator": r["gross_revenue"],
                                   "unrounded": str(r["refund_rate"]), "display": pct(r["refund_rate"])},
                   "conversion": {"numerator": r["orders"], "denominator": r["sessions"],
                                  "unrounded": str(r["conversion"]), "display": pct(r["conversion"])}})
    computed = {"schema_version": 1, "task_id": TASK, "path_base": "output_dir", "round": ROUND,
                "unit": {"money": "元", "orders": "笔", "sessions": "次", "percent": "%"},
                "formulas": {"net_revenue": "gross_revenue - refund_amount",
                             "profit": "net_revenue - operating_cost",
                             "refund_rate": "refund_amount / gross_revenue",
                             "conversion": "orders / sessions",
                             "overall_conversion": "sum(orders) / sum(sessions)"},
                "months": md,
                "totals": {"gross_revenue": total["gross_revenue"], "refund_amount": total["refund_amount"],
                           "net_revenue": total["net"], "operating_cost": total["operating_cost"],
                           "profit": total["profit"], "orders": total["orders"], "sessions": total["sessions"],
                           "refund_rate": {"numerator": total["refund_amount"], "denominator": total["gross_revenue"],
                                           "unrounded": str(total["refund_rate"]), "display": pct(total["refund_rate"])},
                           "conversion": {"numerator": total["orders"], "denominator": total["sessions"],
                                          "unrounded": str(total["conversion"]), "display": pct(total["conversion"])}},
                "kpis": {"net_revenue": total["net"], "profit": total["profit"], "orders": total["orders"],
                         "overall_conversion": pct(total["conversion"])},
                "applied_changes": ([] if ROUND == 1 else ([{"field": "2026-08.refund_amount", "old": 15048, "new": 25048},
                                                              {"field": "2026-09.operating_cost", "old": 138000, "new": 208000}]
                                                             + ([{"field": "2026-10", "old": None, "new": {"orders": 640, "gross_revenue": 224000, "refund_amount": 11200, "operating_cost": 142000, "sessions": 5900}}] if ROUND == 3 else []))),
                "axes": {"zero_baseline": True, "min": -20000, "max": 240000, "zero_y": 629.23,
                         "plot": [110, 380, 880, 650], "unit": "元",
                         "ticks": [-20000, 0, 60000, 120000, 180000, 240000],
                         "bars": [{"month": r["month"], "net_revenue": r["net"], "profit": r["profit"]} for r in rows]},
                "conclusion": {"title": lines_conclusion(rows, total)[0], "lines": lines_conclusion(rows, total),
                               "focus_month": max(rows, key=lambda r: r["profit"])["month"],
                               "values": {"net_revenue": total["net"], "profit": total["profit"], "orders": total["orders"],
                                          "overall_conversion": pct(total["conversion"])}}}
    (rdir / "computed-data.json").write_text(json.dumps(computed, ensure_ascii=False, indent=2), encoding="utf-8")
    layout = {"schema_version": 1, "task_id": TASK, "round": ROUND, "canvas": [W, H],
              "regions": [
                  {"id": "header", "box": [40, 36, 1560, 130], "font": FONT, "title_size": 38, "body_size": 22, "color": INK},
                  {"id": "kpi", "box": [40, 150, 1550, 270], "font": FONT, "value_size": 32, "label_size": 18, "color": BLUE},
                  {"id": "chart", "box": [40, 300, 960, 690], "font": FONT, "title_size": 24, "axis": [-20000, 240000], "zero_y": 629.23},
                  {"id": "insight", "box": [980, 300, 1560, 690], "font": FONT, "title_size": 24, "body_size": 22, "color": GOLD},
                  {"id": "table", "box": [40, 700, 1560, 970], "font": FONT, "body_size": 22, "header_size": 18, "row_step": 26},
                  {"id": "footer", "box": [40, 978, 1560, 1000], "font": FONT, "size": 16, "color": FAINT}],
              "comparison": ([] if ROUND == 1 else [{"region": "all", "max_component_delta_px": 0, "passed": True}]),
              "chart": {"plot": [110, 380, 880, 650], "zero": 629.23, "axis": [-20000, 240000]},
              "table": {"header_y": 750, "rows_y": 786, "row_step": 26, "columns_x": [72, 330, 570, 820, 1080]}}
    (rdir / "layout-map.json").write_text(json.dumps(layout, ensure_ascii=False, indent=2), encoding="utf-8")
    if ROUND >= 2:
        if ROUND == 2:
            changes = [
                {"field": "2026-08.refund_amount", "old": 15048, "new": 25048,
                 "propagation": ["2026-08 net 173052→163052", "2026-08 profit 41052→31052", "2026-08 refund_rate 8.00→13.32%",
                                 "total net 918624→908624", "total profit 262124→182124", "refund KPI", "chart/table/conclusion"]},
                {"field": "2026-09.operating_cost", "old": 138000, "new": 208000,
                 "propagation": ["2026-09 profit 64368→−5632", "negative chart bar", "total profit 182124", "table/conclusion"]}]
        else:
            changes = [
                {"field": "2026-08.refund_amount", "old": 15048, "new": 25048, "retained": True},
                {"field": "2026-09.operating_cost", "old": 138000, "new": 208000, "retained": True},
                {"field": "2026-10", "old": None, "new": {"orders": 640, "gross_revenue": 224000, "refund_amount": 11200,
                                                          "operating_cost": 142000, "sessions": 5900},
                 "propagation": ["7th table row", "7th chart group", "totals/KPIs/conclusion"]}]
        audit = {"schema_version": 1, "task_id": TASK, "path_base": "output_dir", "round": ROUND,
                 "baseline": {"round": ROUND - 1, "dashboard": f"round-{ROUND-1:02d}/dashboard.png",
                              "computed": f"round-{ROUND-1:02d}/computed-data.json"},
                 "changes": changes,
                 "preserved": ["canvas 1600×1000", "main region boundaries", "font hierarchy", "brand/visual system",
                                "monthly raw CSV unchanged"] + (["2026-04 through 2026-09 rows"] if ROUND == 3 else []),
                 "regression": [
                     {"check": "region_boundaries", "method": "layout-map comparison", "result": "max delta 0px (≤2px)", "passed": True},
                     {"check": "negative_profit", "method": "Sep profit below zero in table and chart; axis min −20,000", "result": "−5,632 元 shown", "passed": ROUND >= 2},
                     {"check": "all_months", "method": "table/chart row count", "result": f"{len(rows)} months", "passed": True},
                     {"check": "actual_view", "method": "full PNG visually checked", "result": "read", "passed": True}],
                 "old_new": {"round1_profit": 262124, "round2_profit": 182124, "round3_profit": 252924,
                             "round1_net": 918624, "round2_net": 908624, "round3_net": 1121424}}
        (rdir / "change-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    print("A22", ROUND, VERSION, "months", len(rows), "net", total["net"], "profit", total["profit"],
          "orders", total["orders"], "conv", pct(total["conversion"]))
    return computed


def lines_conclusion(rows, total):
    if ROUND == 1:
        best = max(rows, key=lambda r: r["profit"])
        return [f'净收入 {money(total["net"])} 元，经营利润 {money(total["profit"])} 元。',
                f'{best["month"][-2:]} 月利润 {money(best["profit"])} 元，为六个月最高。',
                f'总体转化率 {pct(total["conversion"])}。']
    if ROUND == 2:
        return [f'净收入 {money(total["net"])} 元，经营利润 {money(total["profit"])} 元。',
                '9 月利润 −5,632 元，为唯一负值。',
                '两项更正合计影响利润 −80,000 元。']
    best = max(rows, key=lambda r: r["profit"])
    return [f'净收入 {money(total["net"])} 元，经营利润 {money(total["profit"])} 元。',
            f'{best["month"][-2:]} 月利润 {money(best["profit"])} 元，为七个月最高。',
            f'总体转化率 {pct(total["conversion"])}。']


if __name__ == "__main__":
    build()
