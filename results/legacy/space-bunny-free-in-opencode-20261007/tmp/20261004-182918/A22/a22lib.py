"""A22 shared library: data, corrections, layout constants, DSL emitters.

Every geometry constant below is the single source of truth for both the emitted
DSL and layout-map.json, so the regression comparison between rounds can be done
on the very same numbers the service was asked to draw.

Element registry: every DSL element is emitted through Emitter.tb()/bb() so its
logical name, kind and rectangle are recorded. compare_rounds.py diffs those
registries across rounds to prove which parts changed and which did not.
"""
from __future__ import annotations

import csv
import os

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
CSV_PATH = os.path.join(ROOT, "tasks", "A22-staged-data-correction", "inputs", "monthly.csv")

W, H = 1600, 1000
BG = "#F1F5F9FF"
INK = "#0F172AFF"
MUTED = "#64748BFF"
LINE = "#E2E8F0FF"
NET_C = "#2563EBFF"
PROF_C = "#0D9488FF"
LOSS_C = "#DC2626FF"
CARD = "#FFFFFFFF"

# ---- main region rectangles (kept within +-2px across all three rounds) -------
REGIONS = {
    "header":       {"x": 40, "y": 28, "w": 1520, "h": 92},
    "kpi_row":      {"x": 40, "y": 130, "w": 1520, "h": 152},
    "chart":        {"x": 40, "y": 292, "w": 1520, "h": 320},
    "table":        {"x": 40, "y": 622, "w": 800, "h": 330},
    "conclusion":   {"x": 856, "y": 622, "w": 704, "h": 330},
    "_spacer":      {"x": 840, "y": 622, "w": 16, "h": 330},
    "footnote":     {"x": 40, "y": 964, "w": 1520, "h": 28},
}
KPI_GAP = 16
KPI_N = 4
KPI_W = (REGIONS["kpi_row"]["w"] - KPI_GAP * (KPI_N - 1)) / KPI_N

TITLE_SIZE = 34
BODY_SIZE = 22           # TASK.md hard floor: body text >= 22
SECT_SIZE = 24
KPI_LABEL_SIZE = 22
KPI_VALUE_SIZE = 42

TBL_HDR_SIZE = 22
BARS_LABEL_SIZE = 22

TABLE_TITLE_TOP = 12
TABLE_HDR_TOP = 54
TABLE_HDR_RULE = 86
TABLE_ROWS_TOP = 94
TABLE_BOTTOM_PAD = 14
TABLE_CELL_H = 26
# (key, align, x-anchor inside panel, box width, chinese header label)
TABLE_COLS = [
    ("month",            "LEFT",  24, 140, "月份"),
    ("net_revenue",      "RIGHT", 316, 172, "净收入"),
    ("operating_profit", "RIGHT", 498, 176, "经营利润"),
    ("refund_rate",      "RIGHT", 656, 152, "退款率"),
    ("conversion_rate",  "RIGHT", 786, 152, "转化率"),
]

CONC_TITLE_TOP = 14
CONC_HEAD_TOP = 52
CONC_HEAD_STEP = 31
CONC_BODY_TOP = 124
CONC_BODY_STEP = 27
CONC_RULE_Y_OFF = 292
CONC_FOOT_Y_OFF = 304
CONC_BULLET_GAP_LINES = 0.3
CONC_MAX_LINES = 5

CH_PLOT_X0_OFF = 130
CH_PLOT_X1_OFF = 1220
CH_PLOT_Y0_OFF = 64
CH_PLOT_Y1_OFF = 240
CH_SIDE_X_OFF = 1232
CH_SIDE_W = 288
CH_MONTH_LABEL_GAP = 34      # below max(plot bottom, lowest negative bar)
BAR_W = 56
BAR_GAP = 16

SUBTITLE_W = 900
VERDICT_W = 600

ROUND_META = {
    1: {"subdir": "round-01", "req": "tasks/A22-staged-data-correction/TASK.md"},
    2: {"subdir": "round-02", "req": "tasks/A22-staged-data-correction/rounds/round-02.md"},
    3: {"subdir": "round-03", "req": "tasks/A22-staged-data-correction/rounds/round-03.md"},
}


# --------------------------------------------------------------------- data
def load_rows() -> list:
    with open(CSV_PATH, newline="", encoding="utf-8") as fh:
        return [{k: (r[k] if k == "month" else int(r[k])) for k in
                 ("month", "orders", "gross_revenue", "refund_amount",
                  "operating_cost", "sessions")}
                for r in csv.DictReader(fh)]


def rows_for_round(round_no: int):
    """Return (rows, applied_corrections, added_rows)."""
    rows = load_rows()
    applied = []
    if round_no >= 2:
        for r in rows:
            if r["month"] == "2026-08":
                applied.append({
                    "round": 2, "month": "2026-08", "field": "refund_amount",
                    "old": 15048, "new": 25048,
                    "requirement": "rounds/round-02.md：2026-08 refund_amount 应为 25048（旧值 15048）",
                })
                r["refund_amount"] = 25048
            if r["month"] == "2026-09":
                applied.append({
                    "round": 2, "month": "2026-09", "field": "operating_cost",
                    "old": 138000, "new": 208000,
                    "requirement": "rounds/round-02.md：2026-09 operating_cost 应为 208000（旧值 138000）",
                })
                r["operating_cost"] = 208000
    added = []
    if round_no >= 3:
        added = [{"month": "2026-10", "orders": 640, "gross_revenue": 224000,
                  "refund_amount": 11200, "operating_cost": 142000, "sessions": 5900}]
        applied.append({
            "round": 3, "month": "2026-10", "field": "<new month row>",
            "old": None,
            "new": "orders=640,gross_revenue=224000,refund_amount=11200,"
                   "operating_cost=142000,sessions=5900",
            "requirement": "rounds/round-03.md：在第二轮上新增 2026-10 一行",
        })
        rows = rows + added
    return rows, applied, added


def derive(rows: list) -> dict:
    months = []
    for r in rows:
        net = r["gross_revenue"] - r["refund_amount"]
        profit = net - r["operating_cost"]
        months.append({
            "month": r["month"], "orders": r["orders"], "sessions": r["sessions"],
            "gross_revenue": r["gross_revenue"], "refund_amount": r["refund_amount"],
            "operating_cost": r["operating_cost"], "net_revenue": net,
            "operating_profit": profit,
            "refund_rate": r["refund_amount"] / r["gross_revenue"],
            "conversion_rate": r["orders"] / r["sessions"],
            "margin": profit / net,
        })
    tot = {k: sum(m[k] for m in months) for k in
           ("orders", "sessions", "gross_revenue", "refund_amount",
            "operating_cost", "net_revenue", "operating_profit")}
    tot["overall_conversion_rate"] = tot["orders"] / tot["sessions"]
    tot["overall_refund_rate"] = tot["refund_amount"] / tot["gross_revenue"]
    tot["margin"] = tot["operating_profit"] / tot["net_revenue"]
    hi = max(max(m["net_revenue"], m["operating_profit"]) for m in months)
    lo = min(min(m["net_revenue"], m["operating_profit"]) for m in months)
    top = (int(hi) // 60000 + 1) * 60000
    if top <= hi:
        top += 60000
    bottom = (int(lo) // 20000) * 20000 if lo < 0 else 0
    ticks = ([bottom] if bottom < 0 else []) + list(range(0, top + 1, 60000))
    return {"months": months, "total": tot, "axis": {
        "measure": "CNY 元", "domain": [bottom, top], "zero_baseline": True,
        "ticks": ticks, "tick_labels": [wan_label(v) for v in ticks],
        "negative_values_present": lo < 0,
        "shared_linear_scale_for": ["net_revenue", "operating_profit"],
    }}


def wan_label(v: int) -> str:
    if v == 0:
        return "0"
    s = ("%.1f" % (v / 10000.0)).rstrip("0").rstrip(".")
    return s + "万"


def conclusion_for(round_no: int, d: dict) -> dict:
    ms = d["months"]
    t = d["total"]
    first, last = ms[0], ms[-1]
    g = (last["net_revenue"] / first["net_revenue"] - 1) * 100
    gp = (last["operating_profit"] / first["operating_profit"] - 1) * 100
    peak_rr = max(ms, key=lambda m: m["refund_rate"])
    min_rr = min(ms, key=lambda m: m["refund_rate"])
    peak_cv = max(ms, key=lambda m: m["conversion_rate"])
    low_cv = min(ms, key=lambda m: m["conversion_rate"])
    base = derive(load_rows())
    bt = base["total"]
    bi = {m["month"]: m for m in base["months"]}
    bi8, bi9 = bi["2026-08"], bi["2026-09"]

    def f(v):
        return "{:,.0f}".format(v)

    if round_no == 1:
        peak = max(ms, key=lambda m: m["net_revenue"])
        head = "净收入峰值 %s 元（%s）" % (f(peak["net_revenue"]), peak["month"])
        head_lines = ["累计利润 %s 元，利润率 %.2f%%" % (f(t["operating_profit"]),
                                                       t["margin"] * 100)]
        bullets = [
            "净收入 %s→%s 元（+%.1f%%），利润 %s→%s 元（+%.1f%%）" % (
                f(first["net_revenue"]), f(last["net_revenue"]), g,
                f(first["operating_profit"]), f(last["operating_profit"]), gp),
            "退款率最高 %.2f%%（%s），最低 %.2f%%（%s）" % (
                peak_rr["refund_rate"] * 100, peak_rr["month"],
                min_rr["refund_rate"] * 100, min_rr["month"]),
            "总体转化率 %.2f%%，单月最高 %.2f%%（%s）" % (
                t["overall_conversion_rate"] * 100,
                peak_cv["conversion_rate"] * 100, peak_cv["month"]),
        ]
        claims = [
            {"text": " ".join([head] + head_lines), "support": {
                "peak_net_revenue": max(m["net_revenue"] for m in ms),
                "peak_net_revenue_month": max(ms, key=lambda m: m["net_revenue"])["month"],
                "total_operating_profit": t["operating_profit"]}},
            {"text": bullets[0], "support": {
                "first_net": first["net_revenue"], "last_net": last["net_revenue"],
                "net_growth_pct": round(g, 2),
                "first_profit": first["operating_profit"],
                "last_profit": last["operating_profit"],
                "profit_growth_pct": round(gp, 2)}},
            {"text": bullets[1], "support": {
                "peak_refund_rate": round(peak_rr["refund_rate"], 6),
                "peak_refund_month": peak_rr["month"],
                "min_refund_rate": round(min_rr["refund_rate"], 6),
                "min_refund_month": min_rr["month"]}},
            {"text": bullets[2], "support": {
                "overall_conversion_rate": round(t["overall_conversion_rate"], 6),
                "peak_conversion_rate": round(peak_cv["conversion_rate"], 6),
                "peak_conversion_month": peak_cv["month"]}},
        ]
    elif round_no == 2:
        neg = [m for m in ms if m["operating_profit"] < 0]
        head = "%s 更正后转亏 %s 元" % (neg[0]["month"],
                                      f(abs(neg[0]["operating_profit"]))) \
            if neg else "期间无负利润月份"
        head_lines = ["期间利润合计 %s 元" % f(t["operating_profit"])]
        bullets = [
            "08 退款 %s→%s 元，退款率 %.2f%%→%.2f%%" % (
                f(bi8["refund_amount"]), f(ms[4]["refund_amount"]),
                bi8["refund_rate"] * 100, ms[4]["refund_rate"] * 100),
            "09 成本 %s→%s 元，利润 %s→%s 元" % (
                f(bi9["operating_cost"]), f(ms[5]["operating_cost"]),
                f(bi9["operating_profit"]), f(ms[5]["operating_profit"])),
            "总净收入 %s→%s 元，累计利润 %s→%s 元" % (
                f(bt["net_revenue"]), f(t["net_revenue"]),
                f(bt["operating_profit"]), f(t["operating_profit"])),
        ]
        claims = [
            {"text": " ".join([head] + head_lines), "support": {
                "negative_months": [m["month"] for m in neg],
                "worst_profit": min(m["operating_profit"] for m in ms),
                "total_operating_profit": t["operating_profit"]}},
            {"text": bullets[0], "support": {
                "aug_refund_old": bi8["refund_amount"], "aug_refund_new": ms[4]["refund_amount"],
                "aug_refund_rate_old": round(bi8["refund_rate"], 6),
                "aug_refund_rate_new": round(ms[4]["refund_rate"], 6),
                "aug_profit_old": bi8["operating_profit"],
                "aug_profit_new": ms[4]["operating_profit"]}},
            {"text": bullets[1], "support": {
                "sep_cost_old": bi9["operating_cost"], "sep_cost_new": ms[5]["operating_cost"],
                "sep_profit_old": bi9["operating_profit"],
                "sep_profit_new": ms[5]["operating_profit"]}},
            {"text": bullets[2], "support": {
                "net_before": bt["net_revenue"], "net_after": t["net_revenue"],
                "profit_before": bt["operating_profit"],
                "profit_after": t["operating_profit"]}},
        ]
    else:
        head = "%s 净收入 %s 元创新高" % (last["month"], f(last["net_revenue"]))
        head_lines = ["%d 个月累计利润 %s 元" % (len(ms), f(t["operating_profit"]))]
        bullets = [
            "新增 %s：净收入 %s 元、利润 %s 元" % (
                last["month"], f(last["net_revenue"]), f(last["operating_profit"])),
            "期间总净收入 %s 元、总利润 %s 元，利润率 %.2f%%" % (
                f(t["net_revenue"]), f(t["operating_profit"]), t["margin"] * 100),
            "总体转化率 %.2f%%，最低 %.2f%%（%s）" % (
                t["overall_conversion_rate"] * 100,
                low_cv["conversion_rate"] * 100, low_cv["month"]),
        ]
        claims = [
            {"text": " ".join([head] + head_lines), "support": {
                "last_month": last["month"], "last_net": last["net_revenue"],
                "month_count": len(ms), "total_profit": t["operating_profit"]}},
            {"text": bullets[0], "support": {k: last[k] for k in
                                             ("net_revenue", "operating_profit", "refund_rate")}},
            {"text": bullets[1], "support": {
                "net": t["net_revenue"], "profit": t["operating_profit"],
                "margin": round(t["margin"], 6)}},
            {"text": bullets[2], "support": {
                "overall_conversion_rate": round(t["overall_conversion_rate"], 6),
                "low_conversion_rate": round(low_cv["conversion_rate"], 6),
                "low_conversion_month": low_cv["month"]}},
        ]
    return {"headline": head, "headline_lines": [head] + head_lines,
            "bullets": bullets, "claims": claims}


# ------------------------------------------------------------- text helpers
def char_w(ch: str, size: float) -> float:
    o = ord(ch)
    if o > 0x2E80 or ch in "，。、：；！？（）《》“”·—…":
        return size
    if ch == " ":
        return size * 0.28
    return size * 0.55


def str_w(s: str, size: float) -> float:
    return sum(char_w(ch, size) for ch in s)


WRAP_SAFETY = 0.93     # the estimator is optimistic; keep a real margin


_NUMCH = set("0123456789,.%+-−→~")


def tokenize(s: str) -> list:
    """Split into break tokens: a run of digits/punctuation stays one token so a
    number is never split across two lines."""
    out, cur = [], ""
    for ch in s:
        if ch in _NUMCH:
            cur += ch
        else:
            if cur:
                out.append(cur)
                cur = ""
            out.append(ch)
    if cur:
        out.append(cur)
    return out


def wrap_cjk(s: str, size: float, width: float) -> list:
    width = width * WRAP_SAFETY
    lines, cur, w = [], "", 0.0
    for tok in tokenize(s):
        tw = str_w(tok, size)
        if w + tw > width + 0.01 and cur:
            lines.append(cur)
            cur, w = tok, tw
        else:
            cur += tok
            w += tw
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------- DSL emitters
class Emitter:
    def __init__(self):
        self.kids: list = []
        self.reg: list = []

    def _rec(self, name, kind, x, y, w, h, extra):
        self.reg.append(dict(name=name, kind=kind, x=round(x, 2), y=round(y, 2),
                             w=None if w is None else round(w, 2),
                             h=None if h is None else round(h, 2), **extra))

    def tb(self, name, s, x, y, w=None, h=None, **kw):
        self._rec(name, "text", x, y, w, h,
                  {"text": s, "fontSize": kw.get("size", BODY_SIZE),
                   "color": kw.get("color", INK), "align": kw.get("align")})
        import dsllib as D
        out = D.text_el(s, x=x, y=y, w=w, h=h, **kw)
        self.kids.append(out)
        return out

    def bb(self, name, x, y, w, h, **kw):
        self._rec(name, "box", x, y, w, h,
                  {"color": kw.get("color"), "radius": kw.get("radius")})
        import dsllib as D
        out = D.box(x, y, w, h, **kw)
        self.kids.append(out)
        return out

    def ln(self, name, x, y, w, color, thickness=1):
        return self.bb(name, x, y - thickness / 2.0, w, thickness, color=color)