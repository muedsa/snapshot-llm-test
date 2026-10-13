"""A22 - the numbers behind the cockpit, computed once per round.

The CSV is read as-is and never rewritten; a round only layers the corrections and the
new month on top of it. Every value keeps three forms so nothing is quietly rounded:
the raw integers from the source, the unrounded computed value (used for every sum,
difference and bar height), and the display string produced last with decimal
ROUND_HALF_UP.

Run:  python tmp/<run_id>/A22/data.py --round 1
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from decimal import Decimal, ROUND_HALF_UP
from fractions import Fraction
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
CSV = ROOT / "tasks/A22-staged-data-correction/inputs/monthly.csv"
TMP = ROOT / "tmp" / RUN / "A22"

INT_FIELDS = ("orders", "gross_revenue", "refund_amount", "operating_cost", "sessions")

# round 2: two finance corrections; round 3: same two + one new month (cumulative)
CORRECTIONS = {
    1: {},
    2: {"2026-08": {"refund_amount": 25048}, "2026-09": {"operating_cost": 208000}},
    3: {"2026-08": {"refund_amount": 25048}, "2026-09": {"operating_cost": 208000}},
}
EXTRA_MONTHS = {
    1: [], 2: [],
    3: [{"month": "2026-10", "orders": 640, "gross_revenue": 224000,
         "refund_amount": 11200, "operating_cost": 142000, "sessions": 5900}],
}


def read_rows():
    with CSV.open(encoding="utf-8") as fh:
        return [{**r, **{f: int(r[f]) for f in INT_FIELDS}} for r in csv.DictReader(fh)]


def half_up(value: Fraction, places: int) -> Decimal:
    """Decimal round-half-up on magnitude: a tie moves away from zero."""
    q = Decimal(1).scaleb(-places)
    return (Decimal(value.numerator) / Decimal(value.denominator)).quantize(
        q, rounding=ROUND_HALF_UP)


def money_yuan(v: int) -> str:
    return f"{v:,}"


def wan(v: int) -> str:
    return str(half_up(Fraction(v, 10000), 2))


def pct(num: int, den: int) -> str:
    return str(half_up(Fraction(num, den) * 100, 2))


def month_rows(rnd: int):
    rows = {r["month"]: dict(r) for r in read_rows()}
    for m, patch in CORRECTIONS[rnd].items():
        rows[m].update(patch)
    for r in EXTRA_MONTHS[rnd]:
        rows[r["month"]] = dict(r)
    return [rows[k] for k in sorted(rows)]


def compute(rnd: int) -> dict:
    rows = month_rows(rnd)
    months = []
    for r in rows:
        net = r["gross_revenue"] - r["refund_amount"]
        profit = net - r["operating_cost"]
        months.append({
            "month": r["month"],
            "source": {k: r[k] for k in INT_FIELDS},
            "net_revenue": net,
            "operating_profit": profit,
            "refund_rate_exact": {"numerator": r["refund_amount"],
                                  "denominator": r["gross_revenue"],
                                  "unrounded": float(Fraction(r["refund_amount"],
                                                              r["gross_revenue"]))},
            "conversion_rate_exact": {"numerator": r["orders"],
                                      "denominator": r["sessions"],
                                      "unrounded": float(Fraction(r["orders"],
                                                                  r["sessions"]))},
            "display": {"net_revenue_yuan": money_yuan(net),
                        "operating_profit_yuan": money_yuan(profit),
                        "net_revenue_wan": wan(net),
                        "operating_profit_wan": wan(profit),
                        "refund_rate_pct": pct(r["refund_amount"], r["gross_revenue"]),
                        "conversion_rate_pct": pct(r["orders"], r["sessions"])},
        })
    t = {f: sum(m["source"][f] for m in months) for f in INT_FIELDS}
    total_net = t["gross_revenue"] - t["refund_amount"]
    total_profit = total_net - t["operating_cost"]
    totals = {
        "months": len(months),
        "summed_from": [m["month"] for m in months],
        "gross_revenue": t["gross_revenue"], "refund_amount": t["refund_amount"],
        "operating_cost": t["operating_cost"], "orders": t["orders"],
        "sessions": t["sessions"],
        "net_revenue": total_net, "operating_profit": total_profit,
        "overall_refund_rate_exact": {"numerator": t["refund_amount"],
                                      "denominator": t["gross_revenue"],
                                      "unrounded": float(Fraction(t["refund_amount"],
                                                                  t["gross_revenue"]))},
        "overall_conversion_rate_exact": {"numerator": t["orders"],
                                          "denominator": t["sessions"],
                                          "unrounded": float(Fraction(t["orders"],
                                                                      t["sessions"]))},
        "profit_share_of_net_exact": {"numerator": total_profit, "denominator": total_net,
                                      "unrounded": float(Fraction(total_profit,
                                                                  total_net))},
        "display": {"net_revenue_yuan": money_yuan(total_net),
                    "net_revenue_wan": wan(total_net),
                    "operating_profit_yuan": money_yuan(total_profit),
                    "operating_profit_wan": wan(total_profit),
                    "orders": money_yuan(t["orders"]), "sessions": money_yuan(t["sessions"]),
                    "overall_refund_rate_pct": pct(t["refund_amount"], t["gross_revenue"]),
                    "overall_conversion_rate_pct": pct(t["orders"], t["sessions"]),
                    "profit_share_pct": pct(total_profit, total_net)},
        "rule": ("期间汇总先分别求和；总体率=总orders/总sessions、总refund/总gross，"
                 "不平均各月百分比"),
    }
    return {"months": months, "totals": totals}


def conclusions(rnd: int, d: dict) -> dict:
    """Every clause below is asserted against the computed values before it is used."""
    ms, t = d["months"], d["totals"]
    best_net = max(ms, key=lambda m: m["net_revenue"])
    best_profit = max(ms, key=lambda m: m["operating_profit"])
    worst_profit = min(ms, key=lambda m: m["operating_profit"])
    lowest_rr = min(ms, key=lambda m: m["refund_rate_exact"]["unrounded"])
    highest_conv = max(ms, key=lambda m: m["conversion_rate_exact"]["unrounded"])
    negative = [m for m in ms if m["operating_profit"] < 0]
    profitable = len(ms) - len(negative)
    facts = {
        "months": len(ms), "profitable_months": profitable,
        "negative_profit_months": [m["month"] for m in negative],
        "best_net": (best_net["month"], best_net["net_revenue"]),
        "best_profit": (best_profit["month"], best_profit["operating_profit"]),
        "worst_profit": (worst_profit["month"], worst_profit["operating_profit"]),
        "lowest_refund_rate": (lowest_rr["month"],
                               lowest_rr["refund_rate_exact"]["unrounded"]),
        "highest_conversion": (highest_conv["month"],
                               highest_conv["conversion_rate_exact"]["unrounded"]),
        "total_net": t["net_revenue"], "total_profit": t["operating_profit"],
        "profit_share": t["profit_share_of_net_exact"]["unrounded"],
        "net_best_and_rr_lowest_same_month": best_net["month"] == lowest_rr["month"],
    }
    # assertions: the headline may only say what these prove
    assert all(m["net_revenue"] > m["operating_profit"] for m in ms)
    assert facts["best_net"][0] == max(ms, key=lambda m: m["net_revenue"])["month"]
    assert facts["total_profit"] == t["operating_profit"]

    head = (f"{len(ms)} 个月净收入 {t['display']['net_revenue_wan']} 万元、"
            f"利润 {t['display']['operating_profit_wan']} 万元"
            f"（占净收入 {t['display']['profit_share_pct']}%），"
            f"{profitable}/{len(ms)} 个月盈利")
    if negative:
        head += f"；{worst_profit['month']} 利润转负 {money_yuan(worst_profit['operating_profit'])} 元"
    else:
        head += "，无亏损月"
    # "净收入最高的那个月退款率也最低" only holds while it is really the same month
    if best_net["month"] == lowest_rr["month"]:
        head += (f"；净收入最高且退款率最低的月份是 {best_net['month']}"
                 f"（{money_yuan(best_net['net_revenue'])} 元 / "
                 f"{lowest_rr['display']['refund_rate_pct']}%）")
        pairing = "same-month"
    else:
        head += (f"；净收入最高 {best_net['month']}（{money_yuan(best_net['net_revenue'])} 元），"
                 f"退款率最低 {lowest_rr['month']}"
                 f"（{lowest_rr['display']['refund_rate_pct']}%）")
        pairing = "different-months"
    sub = (f"单月利润最高 {best_profit['month']} {money_yuan(best_profit['operating_profit'])} 元"
           f" · 月转化率最高 {highest_conv['month']} "
           f"{highest_conv['display']['conversion_rate_pct']}%"
           f" · 期间总体转化率 {t['display']['overall_conversion_rate_pct']}%"
           f"（先求和，不平均各月）")
    for clause, ok in {
        "净收入>利润(每月)": all(m["net_revenue"] > m["operating_profit"] for m in ms),
        "利润为正月数": profitable == len([m for m in ms if m["operating_profit"] > 0]),
        "唯一亏损月": len(negative) in (0, 1),
        "同月并列说法只在同月时使用": (
            ("净收入最高且退款率最低" in head) == (best_net["month"] == lowest_rr["month"])),
    }.items():
        assert ok, clause
    return {"headline": head, "sub": sub, "pairing": pairing, "facts": facts}


FORMULAS = {
    "net_revenue": "每月净收入 = gross_revenue - refund_amount",
    "operating_profit": "经营利润 = 净收入 - operating_cost",
    "refund_rate": "退款率 = refund_amount / gross_revenue",
    "conversion_rate": "月转化率 = orders / sessions",
    "overall_conversion": "总体转化率 = 总 orders / 总 sessions",
    "overall_refund": "总体退款率 = 总 refund_amount / 总 gross_revenue",
    "totals": "期间汇总先分别求和，不平均各月百分比",
    "rounding": "计算全程用未舍入值；展示用 Decimal ROUND_HALF_UP（恰好半单位时绝对值增大）",
    "precision": "明细金额整数元、订单/访问整数、百分比两位小数、KPI 金额万元两位小数",
}


def payload(rnd: int) -> dict:
    """The whole computed-data.json body for one round (meta.py writes the same thing)."""
    d = compute(rnd)
    d.update({
        "schema_version": 1, "task_id": "A22", "path_base": "output_dir",
        "round": f"round-0{rnd}",
        "unit": "元 / 笔 / 次；KPI 金额另给万元（÷10000，两位小数）",
        "source_file": CSV.relative_to(ROOT).as_posix(),
        "source_sha256": hashlib.sha256(CSV.read_bytes()).hexdigest(),
        "source_rows_unchanged": True,
        "corrections_applied": CORRECTIONS[rnd],
        "months_added": [r["month"] for r in EXTRA_MONTHS[rnd]],
        "formulas": FORMULAS,
    })
    d["conclusion"] = conclusions(rnd, d)
    return d


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", type=int, required=True, choices=(1, 2, 3))
    a = ap.parse_args()
    d = payload(a.round)
    d["axis"] = {"unit": "万元", "step_wan": 4, "series": ["net_revenue", "operating_profit"],
                 "note": "三轮共用 4 万元刻度步长，第二轮只因负值多出一条 -4 万元刻度"}
    TMP.mkdir(parents=True, exist_ok=True)
    (TMP / f"r{a.round:02d}-computed.json").write_text(
        json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"round": a.round, "months": d["totals"]["months"],
                      "net_wan": d["totals"]["display"]["net_revenue_wan"],
                      "profit_wan": d["totals"]["display"]["operating_profit_wan"],
                      "conv": d["totals"]["display"]["overall_conversion_rate_pct"],
                      "neg": d["conclusion"]["facts"]["negative_profit_months"],
                      "headline": d["conclusion"]["headline"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
