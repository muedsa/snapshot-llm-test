#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A22 · 真实数据更正与局部回归 · 预置三轮连续执行。

`--round N` 生成第 N 轮（严格按 1→2→3 顺序调用，不预先生成后续轮）：
  round-XX/dashboard.snapshot (1600×1000)
  round-XX/computed-data.json / layout-map.json
  round-XX/change-audit.json (round 2/3)
  round-XX/monthly.csv（本轮实际使用的数据快照，原始 inputs/monthly.csv 不修改）

公式/精度按 TASK.md 三轮共同口径；负利润轮次在原柱图区域内扩展负轴范围，
主区域边界跨轮固定(±2px)。DSL 全部由本脚本构造，无外部图片。
"""
import os, sys, json, csv, argparse
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

TOOLS = os.environ["TOOLS"]
sys.path.insert(0, TOOLS)
from dsl import Canvas, CN, LATIN
import suite

TASK = "A22"
OUT = suite.out_dir(TASK)
TMP = suite.tmp_dir(TASK)
VER = os.environ.get("BUILD_VERSION", "v1")
SRC = suite.ROOT / "tasks" / "A22-staged-data-correction" / "inputs" / "monthly.csv"

# ---------------------------------------------------------------- 调色板
BG = "#F4F7FC"; NAVY = "#0B1B35"; NAVY2 = "#16386F"; WHITE = "#FFFFFF"
INK = "#0F172A"; MUTED = "#5B6B85"; LINE = "#DDE5F0"; GRIDL = "#94A3B8"
BLUE = "#2563EB"; TEAL = "#0D9488"; AMBER = "#F59E0B"; RED = "#DC2626"; GREEN = "#16A34A"
NEGBG = "#FEE2E2"

# ---------------------------------------------------------------- 固定主区域（跨轮 ±2px）
REGIONS = {
    "header":        [0, 0, 1600, 112],
    "kpi_1":         [48, 136, 412, 264],
    "kpi_2":         [428, 136, 792, 264],
    "kpi_3":         [808, 136, 1172, 264],
    "kpi_4":         [1188, 136, 1552, 264],
    "bar_chart":     [48, 282, 988, 660],
    "mini_sessions": [1004, 282, 1552, 460],
    "mini_cvr":      [1004, 478, 1552, 660],
    "table":         [48, 676, 1000, 952],
    "conclusion":    [1064, 676, 1552, 952],
    "footer":        [0, 952, 1600, 1000],
}
REGION_STYLE = {
    "header": {"font": CN, "font_size": 34, "color": "#FFFFFF", "bg": NAVY, "note": "渐变头部"},
    "kpi_1": {"font": CN, "font_size": 22, "color": INK, "bg": WHITE, "accent": BLUE},
    "kpi_2": {"font": CN, "font_size": 22, "color": INK, "bg": WHITE, "accent": TEAL},
    "kpi_3": {"font": CN, "font_size": 22, "color": INK, "bg": WHITE, "accent": AMBER},
    "kpi_4": {"font": CN, "font_size": 22, "color": INK, "bg": WHITE, "accent": "#7C3AED"},
    "bar_chart": {"font": CN, "font_size": 22, "color": INK, "bg": WHITE, "note": "净收入/利润共用零起点分组柱图"},
    "mini_sessions": {"font": CN, "font_size": 22, "color": INK, "bg": WHITE, "note": "访问量 Sessions"},
    "mini_cvr": {"font": CN, "font_size": 22, "color": INK, "bg": WHITE, "note": "月转化率 CVR"},
    "table": {"font": CN, "font_size": 22, "color": INK, "bg": WHITE, "note": "月份/净收入/利润/退款率/转化率"},
    "conclusion": {"font": CN, "font_size": 22, "color": "#E8F0FC", "bg": NAVY, "note": "主结论"},
    "footer": {"font": CN, "font_size": 22, "color": MUTED, "bg": BG, "note": "口径脚注"},
}

# ---------------------------------------------------------------- 原始 CSV（6 个月，不改）
def load_base():
    rows = []
    with SRC.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append({
                "month": r["month"], "orders": int(r["orders"]),
                "gross_revenue": int(r["gross_revenue"]),
                "refund_amount": int(r["refund_amount"]),
                "operating_cost": int(r["operating_cost"]),
                "sessions": int(r["sessions"]),
            })
    return rows

BASE = load_base()
assert len(BASE) == 6 and BASE[0]["month"] == "2026-04" and BASE[-1]["month"] == "2026-09"

def data_for(n):
    rows = [dict(r) for r in BASE]
    changes = []
    if n >= 2:
        rows[4]["refund_amount"] = 25048   # 2026-08 旧 15048
        rows[5]["operating_cost"] = 208000  # 2026-09 旧 138000
        changes = [
            {"field": "2026-08.refund_amount", "old": 15048, "new": 25048, "source": "rounds/round-02.md"},
            {"field": "2026-09.operating_cost", "old": 138000, "new": 208000, "source": "rounds/round-02.md"},
        ]
    if n >= 3:
        rows.append(dict(month="2026-10", orders=640, gross_revenue=224000,
                         refund_amount=11200, operating_cost=142000, sessions=5900))
        changes = [
            {"field": "2026-08.refund_amount", "old": 15048, "new": 25048, "source": "round-02 更正（继续有效）"},
            {"field": "2026-09.operating_cost", "old": 138000, "new": 208000, "source": "round-02 更正（继续有效）"},
            {"field": "新增行 2026-10", "old": None,
             "new": {"orders": 640, "gross_revenue": 224000, "refund_amount": 11200,
                     "operating_cost": 142000, "sessions": 5900}, "source": "rounds/round-03.md"},
        ]
    return rows, changes

# ---------------------------------------------------------------- 计算（Decimal half-up）
def D(v): return Decimal(str(v))

def pct(num, den):
    raw = D(num) / D(den)
    disp = (raw * 100).quantize(D("0.01"), rounding=ROUND_HALF_UP)
    return float(raw), str(disp) + "%"

def compute(rows):
    months = []
    for r in rows:
        net = r["gross_revenue"] - r["refund_amount"]
        profit = net - r["operating_cost"]
        rr_raw, rr_disp = pct(r["refund_amount"], r["gross_revenue"])
        cv_raw, cv_disp = pct(r["orders"], r["sessions"])
        months.append({
            **r,
            "net_revenue": net, "operating_profit": profit,
            "refund_rate": {"numerator": r["refund_amount"], "denominator": r["gross_revenue"],
                            "raw": rr_raw, "display": rr_disp},
            "conversion_rate": {"numerator": r["orders"], "denominator": r["sessions"],
                                "raw": cv_raw, "display": cv_disp},
            "display": {"net_revenue": format(net, ","), "operating_profit": format(profit, ","),
                        "refund_rate": rr_disp, "conversion_rate": cv_disp},
        })
    keys = ("orders", "gross_revenue", "refund_amount", "operating_cost",
            "sessions", "net_revenue", "operating_profit")
    t = {k: sum(m[k] for m in months) for k in keys}
    oc_raw, oc_disp = pct(t["orders"], t["sessions"])
    orr_raw, orr_disp = pct(t["refund_amount"], t["gross_revenue"])
    t["overall_conversion_rate"] = {"numerator": t["orders"], "denominator": t["sessions"],
                                     "raw": oc_raw, "display": oc_disp}
    t["overall_refund_rate"] = {"numerator": t["refund_amount"], "denominator": t["gross_revenue"],
                                "raw": orr_raw, "display": orr_disp}
    t["period"] = months[0]["month"] + " — " + months[-1]["month"]
    t["months_count"] = len(months)
    t["display"] = {k: format(t[k], ",") for k in keys}
    return months, t

def axes_for(n):
    if n == 1:
        vmin, vmax = 0, 220000
        ticks = [0, 50000, 100000, 150000, 200000]
    else:
        vmin, vmax = -20000, 240000
        ticks = [-20000, 0, 50000, 100000, 150000, 200000]
    top_y, base_y = 356, 620
    scale = (base_y - top_y) / (vmax - vmin)
    zero_y = base_y - (0 - vmin) * scale
    return {
        "chart": "grouped_bars", "unit": "CNY 元", "shared_zero": True,
        "shared_by": ["net_revenue", "operating_profit"],
        "vmin": vmin, "vmax": vmax, "ticks": ticks,
        "negative_axis": vmin < 0,
        "zero_line_px": zero_y, "base_y_px": base_y, "top_y_px": top_y,
        "scale_px_per_yuan": scale,
        "pixel_mapping": "y = zero_y - value * (620-356)/(vmax-vmin)；zero_y = 620 - (0-vmin)*scale；"
                          "负值柱从 zero_y 向下绘制 |value|*scale 像素",
        "plot_l": 116, "plot_r": 958,
    }

def conclusion_for(n, months, t):
    first, last = months[0], months[-1]
    if n == 1:
        growth = (last["net_revenue"] / first["net_revenue"] - 1) * 100
        text = ("净收入由 %s 升至 %s 元（+%.1f%%），但总体转化率 %s 低于 4 月 %s；"
                "6、8 月退款率 8.00%%，增长靠规模而非效率，优先治理退款与转化。"
                % (first["display"]["net_revenue"], last["display"]["net_revenue"], growth,
                   t["overall_conversion_rate"]["display"], first["display"]["conversion_rate"]))
        refs = ["months[0].net_revenue", "months[5].net_revenue",
                "totals.overall_conversion_rate", "months[0].conversion_rate",
                "months[2].refund_rate", "months[4].refund_rate"]
        vals = {"net_growth_pct": round(growth, 2),
                "overall_cvr": t["overall_conversion_rate"]["display"],
                "apr_cvr": first["display"]["conversion_rate"]}
    elif n == 2:
        aug, sep = months[4], months[5]
        text = ("财务更正后：8 月退款率 %s，9 月利润转负（%s 元）；总净收入 %s、"
                "总利润 %s 元（−80,000），总体转化率仍 %s。优先治理退款与成本。"
                % (aug["display"]["refund_rate"], sep["display"]["operating_profit"],
                   t["display"]["net_revenue"], t["display"]["operating_profit"],
                   t["overall_conversion_rate"]["display"]))
        refs = ["months[4].refund_rate", "months[5].operating_profit",
                "totals.net_revenue", "totals.operating_profit", "totals.overall_conversion_rate"]
        vals = {"aug_refund_rate": aug["display"]["refund_rate"],
                "sep_profit": sep["operating_profit"],
                "total_net": t["net_revenue"], "total_profit": t["operating_profit"],
                "profit_delta_vs_round1": t["operating_profit"] - 262124}
    else:
        sep = months[5]  # 2026-09 仍为负
        text = ("新增 10 月（7 个月）：10 月净收入 %s、利润 %s 元，但 9 月仍负（%s）；"
                "累计净收入 %s、利润 %s 元、订单 %s 笔，总体转化率 %s。"
                % (last["display"]["net_revenue"], last["display"]["operating_profit"],
                   sep["display"]["operating_profit"], t["display"]["net_revenue"],
                   t["display"]["operating_profit"], t["display"]["orders"],
                   t["overall_conversion_rate"]["display"]))
        refs = ["months[6].net_revenue", "months[6].operating_profit",
                "months[5].operating_profit", "totals.net_revenue",
                "totals.operating_profit", "totals.orders", "totals.overall_conversion_rate"]
        vals = {"oct_net": last["net_revenue"], "oct_profit": last["operating_profit"],
                "sep_profit": sep["operating_profit"], "total_net": t["net_revenue"],
                "total_profit": t["operating_profit"], "total_orders": t["orders"],
                "overall_cvr": t["overall_conversion_rate"]["display"]}
    return {"text": text, "referenced_fields": refs, "values": vals,
            "evidence_basis": "仅根据该轮实际计算数值成立，引用字段见 computed-data.json"}

# ---------------------------------------------------------------- DSL
def fmt_tick(v):
    if v == 0: return "0"
    return ("−" if v < 0 else "") + "%dk" % (abs(v) // 1000)

def build_dashboard(n):
    rows, _ = data_for(n)
    months, t = compute(rows)
    ax = axes_for(n)
    conc = conclusion_for(n, months, t)
    c = Canvas(1600, 1000, BG)

    # ---- header ----
    c.gradient(0, 0, 1600, 112, [NAVY, NAVY2], begin="CENTER_LEFT", end="CENTER_RIGHT")
    c.rect(0, 108, 1600, 4, "#38BDF8")
    title = "NORTHSTAR  ·  六个月经营诊断驾驶舱" if n < 3 else "NORTHSTAR  ·  七个月经营诊断驾驶舱"
    c.text(48, 18, 900, 48, title, 34, WHITE, bold=True)
    c.text(48, 70, 900, 32, t["period"] + "   |   金额单位：元（CNY）", 22, "#BBD3F2")
    c.text(1130, 26, 420, 34, "MANAGEMENT VIEW / %sM" % t["months_count"], 22, "#8FB6EA", align="RIGHT", font=LATIN)
    c.text(1130, 66, 420, 30, "数据源：monthly.csv · %d 个月" % t["months_count"], 22, "#BBD3F2", align="RIGHT")

    # ---- KPI cards ----
    kpis = [
        ("总净收入", "¥ " + t["display"]["net_revenue"], "gross − refund", BLUE, "NET"),
        ("总经营利润", "¥ " + t["display"]["operating_profit"], "净收入 − 经营成本", TEAL, "PROFIT"),
        ("总订单", t["display"]["orders"] + " 笔", "%d 个月累计" % t["months_count"], AMBER, "ORDERS"),
        ("期间总体转化率", t["overall_conversion_rate"]["display"], "总订单 ÷ 总访问量", "#7C3AED", "CVR"),
    ]
    for i, (label, val, sub, col, en) in enumerate(kpis):
        x = 48 + i * 380
        c.rect(x, 136, 364, 128, WHITE, radius=16, border="1 SOLID " + LINE)
        c.rect(x, 136, 6, 128, col, radius=3)
        c.text(x + 24, 146, 320, 30, label, 22, MUTED)
        c.text(x + 24, 178, 330, 52, val, 34, INK, bold=True, font=LATIN if i in (0, 1, 2) else CN)
        c.text(x + 24, 230, 330, 28, sub, 22, MUTED)
        c.text(x + 250, 150, 90, 24, en, 14, "#9AAAC2", align="RIGHT", font=LATIN)

    # ---- left grouped bar chart (shared zero, same scale) ----
    LX, LY, LW, LH = 48, 282, 940, 378
    c.rect(LX, LY, LW, LH, WHITE, radius=16, border="1 SOLID " + LINE)
    c.text(70, 292, 620, 32, "净收入 与 经营利润 · 分月对比", 24, INK, bold=True)
    c.text(70, 326, 700, 28, "金额 / 元 · 同一零起点、同一刻度，两组柱共用比例", 22, MUTED)
    c.rect(634, 302, 16, 16, BLUE, radius=4); c.text(654, 296, 100, 30, "净收入", 22, INK)
    c.rect(766, 302, 16, 16, TEAL, radius=4); c.text(786, 296, 110, 30, "经营利润", 22, INK)
    if ax["negative_axis"]:
        c.rect(906, 303, 16, 16, RED, radius=4); c.text(926, 296, 56, 30, "负值", 22, RED)
    PLOT_L, PLOT_R = ax["plot_l"], ax["plot_r"]
    TOP_Y, BASE_Y = ax["top_y_px"], ax["base_y_px"]
    zero_y, SCALE = ax["zero_line_px"], ax["scale_px_per_yuan"]
    # 负轴区域浅红底（在网格线之前）
    if ax["negative_axis"]:
        c.rect(PLOT_L, zero_y, PLOT_R - PLOT_L, BASE_Y - zero_y, NEGBG, opacity=0.7)
    for v in ax["ticks"]:
        y = zero_y - v * SCALE
        c.hline(PLOT_L, y, PLOT_R - PLOT_L, 2 if v == 0 else 1, GRIDL if v == 0 else LINE)
        c.text(58, y - 13, 54, 26, fmt_tick(v), 22, MUTED, align="RIGHT", font=LATIN)
    G = len(months)
    GROUP = (PLOT_R - PLOT_L) / G
    for i, m in enumerate(months):
        gx = PLOT_L + GROUP * i + GROUP / 2
        hn = m["net_revenue"] * SCALE
        hp = m["operating_profit"] * SCALE
        # 净收入柱（正，向上）
        c.bar(gx - 41, zero_y - hn, 38, hn, BLUE, radius=5)
        # 利润柱（正向上 / 负向下，负用红色）
        pcol = RED if m["operating_profit"] < 0 else TEAL
        if hp >= 0:
            c.bar(gx + 3, zero_y - hp, 38, hp, pcol, radius=5)
        else:
            c.bar(gx + 3, zero_y, 38, -hp, pcol, radius=5)
        # 柱端数值：净收入柱顶精确金额；负利润柱底显式负号
        c.text(gx - 62, zero_y - hn - 28, 120, 26, m["display"]["net_revenue"], 22, BLUE,
               align="CENTER", font=LATIN)
        if m["operating_profit"] < 0:
            c.text(gx - 52, zero_y - hp + 4, 104, 26, m["display"]["operating_profit"], 22,
                   RED, bold=True, align="CENTER", font=LATIN)
        c.text(gx - 52, 626, 96, 28, m["month"][-2:] + "月", 22, INK, bold=True, align="CENTER")

    # ---- right mini: sessions ----
    RX, RW = 1004, 548
    c.rect(RX, 282, RW, 178, WHITE, radius=16, border="1 SOLID " + LINE)
    c.text(1026, 290, 360, 30, "访问量 Sessions", 24, INK, bold=True)
    c.text(1360, 292, 170, 28, "0 → 6,000", 22, MUTED, align="RIGHT", font=LATIN)
    SX0, SGAP, SBARW = 1062, 76 if G <= 6 else 66, 40 if G <= 6 else 34
    for i, m in enumerate(months):
        h = m["sessions"] / 6000 * 72
        x = SX0 + SGAP * i
        c.bar(x, 422 - h, SBARW, h, "#93C5FD", radius=5)
        c.text(x - 10, 398 - h, 60, 24, format(m["sessions"], ","), 22, BLUE, align="CENTER", font=LATIN)
        c.text(x - 8, 424, 56, 24, m["month"][-2:] + "月", 22, MUTED, align="CENTER")

    # ---- right mini: cvr ----
    c.rect(RX, 478, RW, 182, WHITE, radius=16, border="1 SOLID " + LINE)
    c.text(1026, 486, 360, 30, "转化率 CVR", 24, INK, bold=True)
    c.text(1360, 488, 170, 28, "8% → 13%", 22, MUTED, align="RIGHT", font=LATIN)
    CY0, CY1, CMIN, CMAX = 536, 610, 0.08, 0.13
    def cy(v): return CY1 - (v - CMIN) / (CMAX - CMIN) * (CY1 - CY0)
    for v in (0.09, 0.11, 0.13):
        y = cy(v)
        c.hline(1062, y, 452, 1, LINE)
        c.text(1024, y - 13, 36, 26, "%d%%" % (v * 100), 22, MUTED, align="RIGHT", font=LATIN)
    pts = [(SX0 + SGAP * i + SBARW / 2, cy(m["conversion_rate"]["raw"])) for i, m in enumerate(months)]
    for p1, p2 in zip(pts, pts[1:]):
        c.line(p1[0], p1[1], p2[0], p2[1], 4, "#7C3AED")
    for p in pts:
        c.circle(p[0], p[1], 6, "#7C3AED"); c.circle(p[0], p[1], 3, WHITE)
    ov = cy(t["overall_conversion_rate"]["raw"])
    c.dashed_hline(1062, ov, 452, 2, AMBER, dash=9, gap=6)
    c.rect(1382, ov - 36, 154, 26, "#FFF7ED", radius=6, border="1 SOLID #FDE68A")
    c.text(1388, ov - 35, 142, 24, "总体 " + t["overall_conversion_rate"]["display"], 22, "#B45309", bold=True, align="CENTER")
    for i, m in enumerate(months):
        x = SX0 + SGAP * i
        c.text(x - 8, 616, 56, 24, m["month"][-2:] + "月", 22, MUTED, align="CENTER")

    # ---- detail table ----
    TX, TY, TW, TH = 48, 676, 1000, 276
    c.rect(TX, TY, TW, TH, WHITE, radius=16, border="1 SOLID " + LINE)
    c.text(70, 684, 500, 30, "分月明细", 24, INK, bold=True)
    c.text(760, 686, 266, 26, "退款率 = 退款 ÷ 收入", 22, MUTED, align="RIGHT")
    cols = [(70, 150, "月份", "LEFT"), (220, 200, "净收入 / 元", "RIGHT"),
            (420, 170, "利润 / 元", "RIGHT"), (590, 190, "退款率", "RIGHT"),
            (800, 226, "转化率", "RIGHT")]
    c.rect(64, 720, 968, 38, "#EEF3FB", radius=6)
    for x, w, h, al in cols:
        c.text(x, 722, w, 32, h, 22, "#31456B", bold=True, align=al)
    rowh = 31 if G <= 6 else 26
    for i, m in enumerate(months):
        y = 760 + i * rowh
        if i % 2 == 1:
            c.rect(64, y - 2, 968, rowh, "#F8FAFE")
        vals = [m["month"], m["display"]["net_revenue"], m["display"]["operating_profit"],
                m["display"]["refund_rate"], m["display"]["conversion_rate"]]
        for j, ((x, w, h, al), v) in enumerate(zip(cols, vals)):
            col = RED if (j == 2 and m["operating_profit"] < 0) else (RED if (j == 3 and m["refund_rate"]["raw"] >= 0.08) else INK)
            c.text(x, y, w, 28, v, 22, col, align=al, font=LATIN if j in (1, 2, 3, 4) else CN)
    c.hline(64, 948, 968, 1, LINE)

    # ---- conclusion ----
    QX, QY, QW, QH = 1064, 676, 488, 276
    c.rect(QX, QY, QW, QH, NAVY, radius=16)
    c.text(1088, 686, 420, 30, "管理结论  /  EVIDENCE-BASED", 22, "#7DD3FC", bold=True)
    c.text(1088, 714, 436, 162, conc["text"], 22, "#E8F0FC", align="LEFT")
    c.rect(1088, 884, 200, 52, "#163A6B", radius=10)
    c.text(1100, 888, 180, 22, "总净收入", 22, "#7DD3FC", bold=True)
    c.text(1100, 910, 180, 22, t["display"]["net_revenue"], 22, "#C6DCF7", font=LATIN)
    c.rect(1300, 884, 228, 52, "#163A6B", radius=10)
    c.text(1312, 888, 206, 22, "总经营利润", 22, "#7DD3FC", bold=True)
    c.text(1312, 910, 206, 22, t["display"]["operating_profit"], 22,
           RED if t["operating_profit"] < 0 else "#C6DCF7", font=LATIN)

    # ---- footer ----
    c.text(48, 960, 1000, 28,
           "口径：净收入=收入−退款；利润=净收入−成本；总体转化率=总订单÷总访问量（不平均月比例）。",
           22, MUTED)
    c.text(1064, 960, 488, 28, "© NORTHSTAR · SNAPSHOT DSL · R%d" % n,
           22, MUTED, align="RIGHT", font=LATIN)
    return c.render(), months, t, ax, conc

# ---------------------------------------------------------------- 审计 JSON
def computed_data(n, months, t, ax, conc, changes):
    return {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir", "round": n,
        "units": {"amount": "CNY 元", "orders": "笔", "sessions": "次",
                  "rate": "小数比例(0-1)，显示百分比两位小数"},
        "rounding": "Decimal ROUND_HALF_UP（恰好半单位时绝对值增大）；先用未舍入值计算，最后格式化展示",
        "source_csv": "tasks/A22-staged-data-correction/inputs/monthly.csv（未修改）",
        "applied_changes": changes,
        "months": [
            {"month": m["month"], "orders": m["orders"], "gross_revenue": m["gross_revenue"],
             "refund_amount": m["refund_amount"], "operating_cost": m["operating_cost"],
             "sessions": m["sessions"], "net_revenue": m["net_revenue"],
             "operating_profit": m["operating_profit"],
             "refund_rate": m["refund_rate"], "conversion_rate": m["conversion_rate"],
             "display": m["display"]}
            for m in months
        ],
        "totals": t,
        "axes": ax,
        "conclusion": conc,
        "checks": ["net = gross - refund", "profit = net - cost",
                   "overall_cvr = total orders / total sessions（不平均月比例）",
                   "overall_refund_rate = total refund / total gross（不平均月比例）",
                   "bar heights recomputed from corrected values; negative profit drawn below zero line"],
    }

def layout_map(n, ax):
    regions = []
    for rid, box in REGIONS.items():
        st = dict(REGION_STYLE[rid])
        if rid == "bar_chart":
            st["axis"] = {"vmin": ax["vmin"], "vmax": ax["vmax"], "ticks": ax["ticks"],
                          "zero_line_px": round(ax["zero_line_px"], 3),
                          "scale_px_per_yuan": ax["scale_px_per_yuan"],
                          "negative_axis": ax["negative_axis"]}
        regions.append({"id": rid, "box": box, "main_style": st})
    comparison = []
    if n > 1:
        prev = OUT / ("round-%02d" % (n - 1)) / "layout-map.json"
        pm = {r["id"]: r["box"] for r in json.loads(prev.read_text(encoding="utf-8"))["regions"]}
        for rid, box in REGIONS.items():
            d = [abs(box[i] - pm[rid][i]) for i in range(4)]
            comparison.append({"id": rid, "previous_box": pm[rid], "current_box": box,
                               "component_deltas": d, "within_2px": all(x <= 2 for x in d)})
    return {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir", "round": n,
        "canvas": [1600, 1000], "regions": regions, "comparison": comparison,
        "note": "主区域边界跨轮固定；round-2/3 仅允许柱图内部增加负轴范围、表格内部行距/刻度重排",
    }

def change_audit(n, months, t, ax, conc, changes):
    prev = "round-%02d" % (n - 1)
    out_changes = []
    for ch in changes:
        fld = ch["field"]
        if fld.startswith("新增行"):
            m = months[-1]
            prop = ["months[6] 新增 2026-10 全部六项与推导值",
                    "totals 期间范围 → %s，months_count → 7" % t["period"],
                    "KPI 四张卡改为 7 个月期间汇总（净收入 %s / 利润 %s / 订单 %s / 转化率 %s）"
                    % (t["display"]["net_revenue"], t["display"]["operating_profit"],
                       t["display"]["orders"], t["overall_conversion_rate"]["display"]),
                    "柱图由 6 组变 7 组（含 10 月）、表格由 6 行变 7 行（内部行距重排为 26px）",
                    "主结论改为 7 个月口径并保留 9 月负利润事实"]
            out_changes.append({"field": fld, "old": ch["old"], "new": ch["new"],
                                "source": ch["source"], "propagation": prop,
                                "output_locations": ["round-03/computed-data.json:months[6]/totals/axes/conclusion",
                                                     "round-03/dashboard.png:kpi_* / bar_chart / table / conclusion"]})
        else:
            mi = 4 if "2026-08" in fld else 5
            m = months[mi]
            prop = ["months[%d].%s 重算" % (mi, fld.split(".")[1]),
                    "months[%d].net_revenue / operating_profit / refund_rate 重算" % mi,
                    "totals 总退款/总净收入/总利润/总体退款率重算",
                    "KPI 总净收入/总经营利润卡数值",
                    "柱图该月净收入/利润柱高按重算值绘制（9 月利润转负，柱向下画到负轴区）",
                    "表格该月净收入/利润/退款率单元格",
                    "主结论按更正后数值重写"]
            out_changes.append({"field": fld, "old": ch["old"], "new": ch["new"],
                                "source": ch["source"], "propagation": prop,
                                "output_locations": ["round-%02d/computed-data.json:months[%d]" % (n, mi),
                                                     "round-%02d/dashboard.png:bar_chart/table/conclusion" % n]})
    preserved = [
        {"item": "主区域边界", "evidence": "layout-map.json comparison 各区域分量差 = 0 ≤2px；画布 1600×1000 不变"},
        {"item": "主字体/字号/色彩/视觉系统", "evidence": "REGION_STYLE 跨轮相同，正文≥22，共用零起点与同一比例柱图"},
        {"item": "公式与显示精度", "evidence": "沿用 TASK.md 三轮共同口径：Decimal half-up、整数元、百分比两位"},
        {"item": "未指定月份数据", "evidence": "除轮次指定字段/新增行外，其余月份六项原值不变；computed-data.json months 可逐项比对"},
        {"item": "原始 CSV", "evidence": "inputs/monthly.csv 未修改；round-XX/monthly.csv 仅为该轮计算所用数据快照"},
    ]
    if n == 3:
        preserved.append({"item": "round-02 两项更正继续有效", "evidence": "2026-08 refund=25048、2026-09 cost=208000 仍生效；9 月利润仍为 -5632"})
        preserved.append({"item": "2026-04 未省略", "evidence": "months[0].month=2026-04 保留；未偷偷恢复旧数据"})
    regression = [
        {"kind": "data", "method": "按更正后数据全量重算 net/profit/退款率/转化率/汇总/KPI，Decimal 未舍入值参与",
         "result": "computed-data.json 已生成，见 checks；9 月利润 %s" % months[5]["display"]["operating_profit"],
         "evidence": "round-%02d/computed-data.json" % n},
        {"kind": "axis", "method": "柱图 y 轴 vmin=%d vmax=%d，zero_line_px=%.3f，负值柱从零线向下 |v|*scale 像素，不裁切不画正" % (ax["vmin"], ax["vmax"], ax["zero_line_px"]),
         "result": "负轴范围已加入（negative_axis=%s），柱高按重算值，9 月利润柱为红色向下" % ax["negative_axis"],
         "evidence": "round-%02d/computed-data.json:axes + dashboard.png:bar_chart" % n},
        {"kind": "layout", "method": "layout-map.json comparison 逐区域计算与上轮 box 的分量差",
         "result": "全部 0 ≤2px", "evidence": "round-%02d/layout-map.json" % n},
        {"kind": "visual_review", "method": "用 ViewImage 打开 round-%02d/dashboard.png 逐项检查文字/柱高/负轴/表格/结论/边界" % n,
         "result": "pending_visual_review", "evidence": "round-%02d/snapshot-usage.md（看图后回填）" % n},
    ]
    return {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir", "round": n,
        "baseline": {"round": n - 1,
                     "files": [prev + "/dashboard.png", prev + "/dashboard.snapshot",
                               prev + "/computed-data.json", prev + "/layout-map.json"]},
        "changes": out_changes, "preserved": preserved, "regression": regression,
        "status": "pending_visual_review",
    }

def write_monthly_csv(n, rows):
    p = OUT / ("round-%02d" % n) / "monthly.csv"
    with p.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["month", "orders", "gross_revenue", "refund_amount", "operating_cost", "sessions"])
        for r in rows:
            w.writerow([r["month"], r["orders"], r["gross_revenue"], r["refund_amount"],
                        r["operating_cost"], r["sessions"]])
    return p

# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", type=int, choices=[1, 2, 3], required=True)
    n = ap.parse_args().round
    rd = OUT / ("round-%02d" % n); rd.mkdir(parents=True, exist_ok=True)
    bdir = TMP / ("round-%02d" % n) / VER; bdir.mkdir(parents=True, exist_ok=True)
    rows, changes = data_for(n)
    dsl, months, t, ax, conc = build_dashboard(n)
    (rd / "dashboard.snapshot").write_text(dsl, encoding="utf-8")
    (bdir / "dashboard.snapshot").write_text(dsl, encoding="utf-8")
    (rd / "computed-data.json").write_text(json.dumps(computed_data(n, months, t, ax, conc, changes),
                                                       ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (rd / "layout-map.json").write_text(json.dumps(layout_map(n, ax), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if n >= 2:
        (rd / "change-audit.json").write_text(json.dumps(change_audit(n, months, t, ax, conc, changes),
                                                          ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_monthly_csv(n, rows)
    print("A22 ROUND %d BUILD %s | months=%d net=%s profit=%s orders=%s cvr=%s | vmin=%d zero_y=%.2f | DSL bytes=%d"
          % (n, VER, len(months), t["display"]["net_revenue"], t["display"]["operating_profit"],
             t["display"]["orders"], t["overall_conversion_rate"]["display"],
             ax["vmin"], ax["zero_line_px"], len(dsl.encode("utf-8"))))
    print("  conclusion:", conc["text"][:80], "...")

if __name__ == "__main__":
    main()
