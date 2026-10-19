# -*- coding: utf-8 -*-
"""B06 数据计算：c02 IRR 二分解、c09 个税台阶与两方案、c03 跨档电费、c05 换算。
全部结果写入 research/calcs.json，图内数字以此为准。"""
import io
import json
import sys
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
TMP = Path(r"D:\mine\test\glm-5.3-flash\tmp\20261016T164020-m1\B06")
RES = TMP / "research"
RES.mkdir(parents=True, exist_ok=True)

out = {"created_at": datetime.now().astimezone().isoformat(timespec="milliseconds")}

# ---- c02: 12000 元 12 期，月手续费 0.6% = 72 元，月还本金 1000 + 72 = 1072 ----
principal, fee_m, n = 12000.0, 72.0, 12
pay = 1000.0 + fee_m  # 1072
A_target = principal / pay


def annuity(r):
    return (1 - (1 + r) ** -n) / r if r > 0 else float(n)


lo, hi = 1e-9, 0.2
for _ in range(200):
    mid = (lo + hi) / 2
    if annuity(mid) > A_target:
        lo = mid
    else:
        hi = mid
r_m = (lo + hi) / 2
out["c02"] = {
    "principal": principal, "term_months": n, "fee_per_month": fee_m,
    "monthly_payment": pay, "total_fee": fee_m * n,
    "nominal_rate_pct": 0.6 * 12, "target_annuity_factor": round(A_target, 6),
    "irr_monthly_pct": round(r_m * 100, 4),
    "irr_annual_compound_pct": round(((1 + r_m) ** 12 - 1) * 100, 4),
    "irr_annual_simple_pct": round(r_m * 12 * 100, 4),
    "note": "真实年化按复利折算口径为主；月利率×12 的单利口径同列",
}
print("c02 IRR:", out["c02"]["irr_monthly_pct"], "%/月;",
      out["c02"]["irr_annual_compound_pct"], "%年化(复利);",
      out["c02"]["irr_annual_simple_pct"], "%年化(单利x12)")

# ---- c03: 三档演示口径 2760/4800 度，0.52/0.57/0.82；7 月末累计 2700，8 月 480 度 ----
c1_end, c2_end = 2760, 4800
p1, p2, p3 = 0.52, 0.57, 0.82
base_cum, month_use = 2700, 480
seg1 = min(c1_end, base_cum + month_use) - base_cum          # 60
seg2 = min(c2_end, base_cum + month_use) - max(seg1 + base_cum, c1_end)  # 420
fee1, fee2 = seg1 * p1, seg2 * p2
flat = month_use * p1
out["c03"] = {
    "tiers": [[0, c1_end, p1], [c1_end, c2_end, p2], [c2_end, None, p3]],
    "base_cum": base_cum, "month_use": month_use,
    "seg1": seg1, "seg2": seg2, "seg3": month_use - seg1 - seg2,
    "fee1": round(fee1, 2), "fee2": round(fee2, 2), "total": round(fee1 + fee2, 2),
    "flat_assumption": round(flat, 2), "premium": round(fee1 + fee2 - flat, 2),
    "premium_pct": round((fee1 + fee2) / flat * 100 - 100, 2),
}
print("c03:", out["c03"]["seg1"], "x", p1, "+", out["c03"]["seg2"], "x", p2,
      "=", out["c03"]["total"], "vs flat", out["c03"]["flat_assumption"],
      "+", out["c03"]["premium"])

# ---- c09: 月度换算税率表（单独计税找档）与年度表（并入综合） ----
def sepa_tax(bonus):
    m = bonus / 12.0
    if m <= 3000:
        return bonus * 0.03 - 0
    if m <= 12000:
        return bonus * 0.10 - 210
    if m <= 25000:
        return bonus * 0.20 - 1410
    if m <= 35000:
        return bonus * 0.25 - 2660
    if m <= 55000:
        return bonus * 0.30 - 4410
    if m <= 80000:
        return bonus * 0.35 - 7160
    return bonus * 0.45 - 15160


def ann_tax(x):
    if x <= 36000:
        return x * 0.03
    if x <= 144000:
        return x * 0.10 - 2520
    if x <= 300000:
        return x * 0.20 - 16920
    if x <= 420000:
        return x * 0.25 - 31920
    # 高档位演示未用到，止于此
    return None


rows = []
for b in (34999, 36000, 36001, 38566.67):
    t = sepa_tax(b)
    rows.append({"bonus": b, "monthly": b / 12.0, "tax": t, "net": b - t})
w_case = 108000
w_tax = ann_tax(w_case - 60000)  # 无专项扣除演示
comb_tax = ann_tax(w_case - 60000 + 36000)
out["c09"] = {
    "policy_ref": "财政部 税务总局公告2023年第30号，执行至2027-12-31",
    "sepa_rows": rows, "sepa_rule": "奖金/12 定档 → 税=奖金*税率-速算扣除数",
    "jump_gap": rows[1]["net"] - rows[2]["net"],  # 36000 net - 36001 net
    "wage_only": w_case, "wage_tax": w_tax,
    "combined_tax_total": comb_tax, "sepa_tax_total": w_tax + rows[1]["tax"],
    "sepa_saving": comb_tax - (w_tax + rows[1]["tax"]),
}
print("c09 rows:")
for r in rows:
    print("  bonus", r["bonus"], "tax", r["tax"], "net", r["net"])
print("  jump gap:", out["c09"]["jump_gap"])
print("  combined vs separate:", comb_tax, out["c09"]["sepa_tax_total"],
      "saving", out["c09"]["sepa_saving"])

# ---- c05: 50g 糖 → 10 块 5g 方糖；4kcal/g = 200 kcal；慢跑 10 kcal/min → 20 分钟 ----
out["c05"] = {"sugar_g": 50, "cube_g": 5, "cubes": 10,
              "kcal": 200, "run_min": 20, "who25_ratio": 2.0,
              "note": "WHO 2015：<10%E 强建议、<5%E≈25g 条件建议"}
print("c05 ok")
(RES / "calcs.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("written research/calcs.json")
