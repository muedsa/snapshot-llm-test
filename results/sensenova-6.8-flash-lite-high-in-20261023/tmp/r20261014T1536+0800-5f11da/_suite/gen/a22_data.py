"""A22 三轮共用的数据计算层。

输入 tasks/A22-staged-data-correction/inputs/monthly.csv —— 只读，不修改。
口径来自 TASK.md「三轮共同计算与显示口径」：
  期间汇总先分别求和；总体转化率 = 总 orders / 总 sessions；总体退款率 =
  总 refund_amount / 总 gross_revenue，不平均各月百分比。
  未舍入值参与全部计算（汇总、差额、图形比例），最后才按展示精度格式化。
  明细金额与订单/访问量为整数元；百分比统一两位小数；十进制四舍五入。

第二轮、第三轮的更正与新增月份只在 _apply() 内生效，CSV 原值始终保留在
返回结果的 months[].raw 中，便于 change-audit 追溯。
"""
from __future__ import annotations

import csv
import decimal
import math
import pathlib
import re

HERE = pathlib.Path(__file__).resolve()
SUITE_ROOT = HERE.parents[4]
RUN_ID = HERE.parents[2].name
TASK_DIR = SUITE_ROOT / "tasks" / "A22-staged-data-correction"
CSV_PATH = TASK_DIR / "inputs" / "monthly.csv"

RUNTIME = decimal.ROUND_HALF_UP  # 十进制四舍五入，恰好半单位时绝对值增大


def _q(x: decimal.Decimal, places: int = 2) -> decimal.Decimal:
    return x.quantize(decimal.Decimal(1).scaleb(-places), rounding=RUNTIME)


def load_csv() -> list[dict]:
    """读原始 CSV，不改写。金额/订单/访问量为整数。"""
    rows = []
    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            rows.append({
                "month": r["month"].strip(),
                "orders": int(r["orders"]),
                "gross_revenue": int(r["gross_revenue"]),
                "refund_amount": int(r["refund_amount"]),
                "operating_cost": int(r["operating_cost"]),
                "sessions": int(r["sessions"]),
            })
    return rows


# ------------------------------------------------------------------ 轮次口径

# 第二轮：2026-08 refund_amount 15048→25048；2026-09 operating_cost 138000→208000
R2_CORRECTIONS = [
    {"month": "2026-08", "field": "refund_amount", "old": 15048, "new": 25048,
     "source": "rounds/round-02.md 第 1 行"},
    {"month": "2026-09", "field": "operating_cost", "old": 138000, "new": 208000,
     "source": "rounds/round-02.md 第 1–2 行"},
]
# 第三轮：新增 2026-10 一行，第二轮换正继续有效
R3_ADDED_MONTH = {
    "month": "2026-10", "orders": 640, "gross_revenue": 224000,
    "refund_amount": 11200, "operating_cost": 142000, "sessions": 5900,
    "source": "rounds/round-03.md 第 1–2 行",
}

# 柱图刻度：步长 60,000 元，顶部 240,000 元在三轮中一致；
# 第二轮出现实际负利润后，允许在原图表区域内向下增加负轴范围到 -30,000 元。
AXIS_STEP = 60000
AXIS_TOP = 240000
AXIS_BOTTOM_NEG = -30000


def _apply(round_no: int):
    rows = load_csv()
    applied = []
    if round_no >= 2:
        for c in R2_CORRECTIONS:
            hit = False
            for r in rows:
                if r["month"] == c["month"]:
                    assert r[c["field"]] == c["old"], (
                        "CSV 原值 %s 与更正声明的旧值 %s 不一致"
                        % (r[c["field"]], c["old"]))
                    r[c["field"]] = c["new"]
                    applied.append(dict(c))
                    hit = True
            assert hit, "CSV 中找不到 %s" % c["month"]
    if round_no >= 3:
        assert not any(r["month"] == R3_ADDED_MONTH["month"] for r in rows), (
            "2026-10 不应已存在于原始 CSV")
        rows.append({k: v for k, v in R3_ADDED_MONTH.items()
                     if k != "source"})
        applied.append(dict(R3_ADDED_MONTH))
    return rows, applied


def _month(m: dict, round_no: int) -> dict:
    gross = decimal.Decimal(m["gross_revenue"])
    refund = decimal.Decimal(m["refund_amount"])
    cost = decimal.Decimal(m["operating_cost"])
    orders = decimal.Decimal(m["orders"])
    sessions = decimal.Decimal(m["sessions"])

    net = gross - refund
    profit = net - cost
    rr = refund / gross if gross else decimal.Decimal("NaN")
    cr = orders / sessions if sessions else decimal.Decimal("NaN")

    return {
        "month": m["month"],
        "orders": m["orders"],
        "sessions": m["sessions"],
        "gross_revenue": m["gross_revenue"],
        "refund_amount": m["refund_amount"],
        "operating_cost": m["operating_cost"],
        "net_revenue": int(net),
        "net_revenue_calc": "%d - %d" % (m["gross_revenue"], m["refund_amount"]),
        "profit": int(profit),
        "profit_calc": "%d - %d" % (int(net), m["operating_cost"]),
        "refund_rate": {
            "numerator": m["refund_amount"], "denominator": m["gross_revenue"],
            "value_unrounded": float(rr),
            "display": "%.2f%%" % (_q(rr * 100)),
        },
        "conversion_rate": {
            "numerator": m["orders"], "denominator": m["sessions"],
            "value_unrounded": float(cr),
            "display": "%.2f%%" % (_q(cr * 100)),
        },
        "display": {
            "gross_revenue": "{:,}".format(m["gross_revenue"]),
            "refund_amount": "{:,}".format(m["refund_amount"]),
            "operating_cost": "{:,}".format(m["operating_cost"]),
            "net_revenue": "{:,}".format(int(net)),
            "profit": "{:,}".format(int(profit)),
            "orders": "{:,}".format(m["orders"]),
            "sessions": "{:,}".format(m["sessions"]),
        },
    }


def compute(round_no: int) -> dict:
    """产出某一轮的完整计算结果：months / totals / axes / conclusion。"""
    rows, applied = _apply(round_no)
    original = {m["month"]: dict(m) for m in load_csv()}  # CSV 原值，始终保留
    months = []
    for m in rows:
        d = _month(m, round_no)
        orig = original.get(m["month"])
        if orig is not None:
            changed = [k for k in ("orders", "gross_revenue", "refund_amount",
                                   "operating_cost", "sessions")
                       if orig[k] != m[k]]
            d["csv_original"] = orig
            d["corrected_fields"] = changed
        else:
            d["csv_original"] = None
            d["corrected_fields"] = []
            d["added_in_round"] = round_no
        months.append(d)

    tg = sum(m["gross_revenue"] for m in months)
    tr = sum(m["refund_amount"] for m in months)
    tc = sum(m["operating_cost"] for m in months)
    to_ = sum(m["orders"] for m in months)
    ts = sum(m["sessions"] for m in months)
    tn = tg - tr
    tp = tn - tc

    g = decimal.Decimal(tg)
    totals = {
        "period": {"from": months[0]["month"], "to": months[-1]["month"],
                   "months_count": len(months),
                   "basis": "按原始月份顺序连续汇总，所有月份原样出现，不跳过、不合并"},
        "gross_revenue": tg,
        "refund_amount": tr,
        "operating_cost": tc,
        "net_revenue": tn,
        "net_revenue_calc": "%d - %d" % (tg, tr),
        "profit": tp,
        "profit_calc": "%d - %d" % (tn, tc),
        "orders": to_,
        "sessions": ts,
        "refund_rate": {
            "numerator": tr, "denominator": tg,
            "value_unrounded": float(decimal.Decimal(tr) / g),
            "display": "%.2f%%"
                       % _q(decimal.Decimal(tr) / g * 100),
            "note": "总退款 / 总收入，未平均各月百分比",
        },
        "conversion_rate": {
            "numerator": to_, "denominator": ts,
            "value_unrounded": float(decimal.Decimal(to_) / decimal.Decimal(ts)),
            "display": "%.2f%%"
                       % _q(decimal.Decimal(to_) / decimal.Decimal(ts) * 100),
            "note": "总订单 / 总访问次数，未平均各月百分比",
        },
        "display": {
            "gross_revenue": "{:,}".format(tg),
            "refund_amount": "{:,}".format(tr),
            "operating_cost": "{:,}".format(tc),
            "net_revenue": "{:,}".format(tn),
            "profit": "{:,}".format(tp),
            "net_revenue_wan": "%.2f 万元"
                               % _q(decimal.Decimal(tn) / 10000),
            "profit_wan": "%.2f 万元" % _q(decimal.Decimal(tp) / 10000),
            "orders": "{:,}".format(to_),
            "sessions": "{:,}".format(ts),
        },
    }

    values = [m["net_revenue"] for m in months] + [m["profit"] for m in months]
    vmax, vmin = max(values), min(values)
    bottom = AXIS_BOTTOM_NEG if (round_no >= 2 and vmin < 0) else 0
    top = max(AXIS_TOP, math.ceil(vmax / AXIS_STEP) * AXIS_STEP)
    # 网格线从 0 开始按步长递增（零点必须落在网格上）；负轴底端另加一条轴底线
    grid = list(range(0, top + 1, AXIS_STEP))
    if bottom and bottom not in grid:
        grid = [bottom] + grid
    axes = {
        "unit": "元",
        "unit_note": "轴刻度为整数元，千位分隔；柱顶数值标签同单位",
        "scale": "净收入与经营利润共用同一线性比例与同一零点",
        "min": bottom, "max": top, "range": top - bottom,
        "step": AXIS_STEP,
        "gridlines": grid,
        "zero_value": 0,
        "negative_axis": bottom < 0,
        "negative_axis_note": (
            "第二轮起 2026-09 经营利润为负，在原图表区域内把零线下方扩展为"
            "%s 元；正值侧步长与顶部不变，故每元对应的像素数与前一轮不同，"
            "该差异记入 change-audit.json 的 regression" % "{:,}".format(bottom)
            if bottom < 0 else
            "第一轮全部为正值，零点即绘图区底边，无需负轴"),
    }

    return {
        "round": round_no,
        "applied_changes": applied,
        "source_csv": {
            "path_base": "suite_root",
            "path": "tasks/A22-staged-data-correction/inputs/monthly.csv",
            "modified": False,
            "note": "原始 CSV 只读；第二轮更正与第三轮新增月份只在本计算层生效，"
                    "每月 csv_original 保留 CSV 原值",
        },
        "units": {
            "money": "元（整数，未取整到千元或万元）",
            "orders": "笔",
            "sessions": "次",
            "rate": "百分比，两位小数",
        },
        "precision": {
            "money_display": "整数元 + 千位分隔",
            "orders_sessions_display": "整数 + 千位分隔",
            "rate_display": "两位小数（十进制四舍五入，恰好半单位时绝对值增大）",
            "rule": "汇总、差额与图形比例全部用未舍入值计算，最后才格式化展示",
        },
        "months": months,
        "totals": totals,
        "axes": axes,
        "_vmax": vmax,
        "_vmin": vmin,
    }


# ------------------------------------------------------------------ 主结论

def _pct(new: int, old: int) -> str:
    if old == 0:
        return "不可比"
    v = (decimal.Decimal(new) - decimal.Decimal(old)) / decimal.Decimal(old) * 100
    return "%+.2f%%" % _q(v)


def _pp(a: dict, b: dict) -> str:
    """两个比率的百分点差，直接用分子/分母算，不用已经舍入的 float。"""
    an = decimal.Decimal(a["numerator"]) / decimal.Decimal(a["denominator"])
    bn = decimal.Decimal(b["numerator"]) / decimal.Decimal(b["denominator"])
    return "%+.2fpp" % _q((an - bn) * 100)


def _maxmonths(mo, key, field):
    """返回 (达到最大值的月份列表, 最大值)。并列时全部列出，不挑第一个冒充分。"""
    v = max(m[key] for m in mo)
    return [m[field] for m in mo if m[key] == v], v


def conclusion(res: dict, prev: dict = None) -> dict:
    """只写实际数值能成立的结论；每条都带可复核的引用数值。

    prev 是上一轮的计算结果（若有），用于给出真实的轮间差额，不写推算值。
    """
    mo = res["months"]
    tt = res["totals"]
    first, last = mo[0], mo[-1]
    neg = [m for m in mo if m["profit"] < 0]
    net_months, net_max = _maxmonths(mo, "net_revenue", "month")
    prof_months, prof_max = _maxmonths(mo, "profit", "month")
    rr_max = max(m["refund_rate"]["value_unrounded"] for m in mo)
    rr_months = [m["month"] for m in mo
                 if m["refund_rate"]["value_unrounded"] == rr_max]
    cr_max = max(m["conversion_rate"]["value_unrounded"] for m in mo)
    conv_higher = [m["month"] for m in mo
                   if m["conversion_rate"]["value_unrounded"] > cr_max]
    minconv = min(mo, key=lambda m: m["conversion_rate"]["value_unrounded"])

    claims = [
        "%s 至 %s 期间净收入合计 %s 元、经营利润合计 %s 元，总订单 %s 笔、"
        "总体转化率 %s"
        % (first["month"], last["month"], tt["display"]["net_revenue"],
           tt["display"]["profit"], tt["display"]["orders"],
           tt["conversion_rate"]["display"]),
        "%s 单月净收入 %s 元为全期最高；经营利润最高是 %s 的 %s 元%s"
        % ("、".join(net_months), "{:,}".format(net_max),
           "、".join(prof_months), "{:,}".format(prof_max),
           "" if net_months == prof_months else "（与净收入最高不同月）"),
        "转化率由 %s 的 %s 变为 %s 的 %s（%s），全期最高仍是 %s 的 %s，"
        "没有任何月份超过首月"
        % (first["month"], first["conversion_rate"]["display"], last["month"],
           last["conversion_rate"]["display"],
           _pp(last["conversion_rate"], first["conversion_rate"]),
           first["month"], first["conversion_rate"]["display"]),
    ]

    if neg:
        n0 = neg[0]
        claims.append(
            "%s 经营利润 %s 元是全期%s亏损月：该月净收入 %s 元，经营成本 "
            "%s 元，成本比净收入高出 %s 元，正好等于亏损额"
            % (n0["month"], n0["display"]["profit"],
               "唯一" if len(neg) == 1 else "%d 个" % len(neg),
               n0["display"]["net_revenue"], n0["display"]["operating_cost"],
               "{:,}".format(n0["operating_cost"] - n0["net_revenue"])))
    else:
        lo = min(mo, key=lambda m: m["profit"])
        claims.append(
            "全期 %d 个月经营利润均为正，最低是 %s 的 %s 元"
            % (len(mo), lo["month"], lo["display"]["profit"]))

    claims.append(
        "退款率最高 %s，出现在 %s；最低转化率 %s 出现在 %s；期间总体退款率 %s，"
        "由总退款 %s 元 ÷ 总收入 %s 元算出，不是各月百分比的平均"
        % ("%.2f%%" % _q(decimal.Decimal(str(rr_max)) * 100),
           "、".join(rr_months), minconv["conversion_rate"]["display"],
           minconv["month"], tt["refund_rate"]["display"],
           tt["display"]["refund_amount"], tt["display"]["gross_revenue"]))

    dn = _pct(last["net_revenue"], first["net_revenue"])
    dp = _pct(last["profit"], first["profit"])
    if last["profit"] >= first["profit"]:
        tail = "净收入与经营利润都随规模上升，而转化率同期回落，增量主要来自" \
               "收入规模而非转化效率"
    elif last["profit"] < 0:
        tail = "净收入继续上升，但 %s 的经营利润已转负，期间利润由 %s 元缩到" \
               " %s 元，规模增长没能覆盖成本" % (
                   last["month"], "{:,}".format(first["profit"]),
                   "{:,}".format(last["profit"]))
    else:
        tail = "净收入上升而经营利润同期下滑，规模增长未能覆盖成本"
    claims.append(
        "以 %s 为基准：%s 净收入变化 %s、%s 经营利润变化 %s。%s"
        % (first["month"], last["month"], dn, last["month"], dp, tail))

    if prev is not None:
        claims.append(
            "相对上一轮（round-%02d）：期间净收入由 %s 元变为 %s 元（%+d），"
            "经营利润由 %s 元变为 %s 元（%+d），总订单由 %s 笔变为 %s 笔，"
            "总体转化率由 %s 变为 %s，总体退款率由 %s 变为 %s"
            % (prev["round"], "{:,}".format(prev["totals"]["net_revenue"]),
               "{:,}".format(tt["net_revenue"]),
               tt["net_revenue"] - prev["totals"]["net_revenue"],
               "{:,}".format(prev["totals"]["profit"]),
               "{:,}".format(tt["profit"]), tt["profit"] - prev["totals"]["profit"],
               "{:,}".format(prev["totals"]["orders"]),
               "{:,}".format(tt["orders"]),
               prev["totals"]["conversion_rate"]["display"],
               tt["conversion_rate"]["display"],
               prev["totals"]["refund_rate"]["display"],
               tt["refund_rate"]["display"]))

    if res["round"] == 1:
        title = "收入规模持续走高，转化率逐月回落"
        basis = "TASK.md 第一轮：四 KPI、共享零起点柱图、六行表与仅依据实际数值的主结论"
    elif res["round"] == 2:
        title = "更正后 2026-09 转为亏损月，期间利润减少 80,000 元"
        basis = "rounds/round-02.md：两项财务更正的重算、负轴与视觉回归"
    else:
        title = "新增 2026-10 后利润创全期新高，转化率仍在全期低位"
        basis = "rounds/round-03.md：新增月份后的七个月期间汇总与轴/结论核对"

    return {
        "title": title,
        "claim": "；".join(claims[:2]) + "。",
        "claims": claims,
        "basis": basis,
        "verified_against": "computed-data.json 的 months/totals 逐项数值，"
                            "每条结论都可由该文件复算",
        "cited_values": {
            "total_net_revenue": tt["net_revenue"],
            "total_profit": tt["profit"],
            "total_orders": tt["orders"],
            "total_sessions": tt["sessions"],
            "total_conversion_rate_display": tt["conversion_rate"]["display"],
            "total_refund_rate_display": tt["refund_rate"]["display"],
            "first_month": first["month"], "last_month": last["month"],
            "max_net_revenue_months": net_months,
            "max_net_revenue": net_max,
            "max_profit_months": prof_months,
            "max_profit": prof_max,
            "min_conversion_rate_month": minconv["month"],
            "min_conversion_rate_display": minconv["conversion_rate"]["display"],
            "negative_profit_months": [m["month"] for m in neg],
            "months_exceeding_first_conversion": conv_higher,
        },
    }


def _check(res: dict) -> list[str]:
    """内部一致性校验：交叉验算，防止汇总与明细脱节。"""
    msgs = []
    mo, tt = res["months"], res["totals"]
    assert sum(m["gross_revenue"] for m in mo) == tt["gross_revenue"]
    assert sum(m["refund_amount"] for m in mo) == tt["refund_amount"]
    assert sum(m["operating_cost"] for m in mo) == tt["operating_cost"]
    assert sum(m["net_revenue"] for m in mo) == tt["net_revenue"], "净收入汇总"
    assert sum(m["profit"] for m in mo) == tt["profit"], "利润汇总"
    for m in mo:
        assert m["net_revenue"] == m["gross_revenue"] - m["refund_amount"]
        assert m["profit"] == m["net_revenue"] - m["operating_cost"]
        assert m["refund_rate"]["display"] == "%.2f%%" % _q(
            decimal.Decimal(m["refund_amount"]) /
            decimal.Decimal(m["gross_revenue"]) * 100)
        assert m["conversion_rate"]["display"] == "%.2f%%" % _q(
            decimal.Decimal(m["orders"]) / decimal.Decimal(m["sessions"]) * 100)
    assert _q(decimal.Decimal(tt["orders"]) /
              decimal.Decimal(tt["sessions"]) * 100) == (
        decimal.Decimal(tt["conversion_rate"]["display"].rstrip("%"))), "总转化率"
    assert re.match(r"^\d{4}-\d{2}$", mo[0]["month"]) and len(mo) in (6, 7)
    msgs.append("明细与汇总交叉验算通过：%d 个月、净收入 %d、利润 %d、"
                "订单 %d、访问 %d" % (len(mo), tt["net_revenue"], tt["profit"],
                                      tt["orders"], tt["sessions"]))

    # 结论里写成文字的判断必须由数据支持，防止文案与数值脱节
    c = conclusion(res, prev=None)
    crs = [m["conversion_rate"]["value_unrounded"] for m in mo]
    assert crs.index(max(crs)) == 0, "转化率最高月不是首月，结论需改写"
    neg = [m for m in mo if m["profit"] < 0]
    for n in neg:
        assert n["operating_cost"] - n["net_revenue"] == -n["profit"], (
            "亏损月的成本-净收入不等于亏损额")
    assert not any("占位" in s or "TODO" in s for s in c["claims"])
    msgs.append("结论 %d 条，措辞与 computed-data 数值一致（转化率最高月=首月、"
                "亏损月差额=成本-净收入）" % len(c["claims"]))
    return msgs


if __name__ == "__main__":
    prev = None
    for rnd in (1, 2, 3):
        r = compute(rnd)
        c = conclusion(r, prev=prev)
        ok = _check(r)
        print("=== round-%02d ===" % rnd)
        print("  期间 %s → %s（%d 个月）" % (r["totals"]["period"]["from"],
                                             r["totals"]["period"]["to"],
                                             r["totals"]["period"]["months_count"]))
        print("  轴 [%s, %s] 步长 %s，网格 %s"
              % (r["axes"]["min"], r["axes"]["max"], r["axes"]["step"],
                 r["axes"]["gridlines"]))
        print("  总净收入 %s / 总利润 %s / 总订单 %s / 总转化 %s / 总退款率 %s"
              % (r["totals"]["display"]["net_revenue"],
                 r["totals"]["display"]["profit"],
                 r["totals"]["display"]["orders"],
                 r["totals"]["conversion_rate"]["display"],
                 r["totals"]["refund_rate"]["display"]))
        for m in r["months"]:
            print("   %s  净 %9s  利 %9s  退 %6s  转 %6s"
                  % (m["month"], m["display"]["net_revenue"],
                     m["display"]["profit"], m["refund_rate"]["display"],
                     m["conversion_rate"]["display"]))
        print("  结论：%s" % c["claim"])
        for line in c["claims"]:
            print("    · %s" % line)
        print("  校验：%s" % "; ".join(ok))
        prev = r
