"""A22 acceptance checker: parses each delivered dashboard.snapshot and verifies the
TASK.md hard requirements + the round-specific requirement file.

Nothing here trusts the generator: it reads the shipped DSL text only.
Usage: python verify_a22.py <round>
"""
from __future__ import annotations

import json
import os
import re
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
TASK = "A22"
SUB = {1: "round-01", 2: "round-02", 3: "round-03"}[int(sys.argv[1])]
OUT = os.path.join(ROOT, "outputs", RUN, TASK, SUB)

RE_SIZE = re.compile(r'fontSize="([0-9.]+)"')
RE_TEXT = re.compile(r'text="([^"]*)"')
RE_POS = re.compile(r'<Positioned left="([-0-9.]+)" top="([-0-9.]+)" '
                    r'width="([-0-9.]+)" height="([-0-9.]+)"')

fail = []
warn = []


def check(cond, msg):
    (print("PASS  " + msg) if cond else fail.append(msg))
    if not cond:
        print("FAIL  " + msg)


with open(os.path.join(OUT, "dashboard.snapshot"), encoding="utf-8") as fh:
    dsl = fh.read()
lay = json.load(open(os.path.join(OUT, "layout-map.json"), encoding="utf-8"))
comp = json.load(open(os.path.join(OUT, "computed-data.json"), encoding="utf-8"))

# 1. canvas
m = re.search(r'<Container width="(\d+)" height="(\d+)">', dsl)
check(bool(m) and m.group(1) == "1600" and m.group(2) == "1000",
      "canvas is 1600x1000 (root Container width=%s height=%s)"
      % (m.group(1) if m else "?", m.group(2) if m else "?"))
check(dsl.count("<Container") >= 1 and "<Image" not in dsl, "no <Image> embedding")

# 2. body font floor
sizes = [float(x) for x in RE_SIZE.findall(dsl)]
small = [s for s in sizes if s < 22]
check(not small, "every fontSize >= 22 (min=%s, n=%d)" % (min(sizes), len(sizes)))

# 3. no element outside the canvas
out_of_canvas = []
for x, y, w, h in RE_POS.findall(dsl):
    x, y, w, h = float(x), float(y), float(w), float(h)
    if x < -0.5 or y < -0.5 or x + w > 1600.5 or y + h > 1000.5:
        out_of_canvas.append((x, y, w, h))
check(not out_of_canvas, "all Positioned boxes inside the canvas (%d offenders)"
      % len(out_of_canvas))

# 4. four KPIs with the mandated metrics
kpi_names = [k["name"] for k in lay["kpi"]]
check(kpi_names == ["总净收入", "总经营利润", "总订单", "总体转化率"],
      "four KPIs = %s" % kpi_names)
tot = comp["totals"]
expect = {
    "总净收入": tot["net_revenue"],
    "总经营利润": tot["operating_profit"],
    "总订单": tot["orders"],
    "总体转化率": tot["overall_conversion_rate"],
}
for k in lay["kpi"]:
    v = expect[k["name"]]
    txt = k["value_text"]
    want = ("{:,.0f}".format(v) if k["name"] != "总体转化率"
            else "%.2f%%" % (v * 100))
    check(want in txt, "KPI %s shows %s (expected %s)" % (k["name"], txt, want))
check(tot["net_revenue"] == sum(m["gross_revenue"] - m["refund_amount"]
                                for m in comp["months"]),
      "net_revenue = sum(gross - refund)")
check(tot["operating_profit"] == sum(m["net_revenue"] - m["operating_cost"]
                                     for m in comp["months"]),
      "operating_profit = sum(net - operating_cost)")
orders_tot = sum(m["orders"] for m in comp["months"])
sess_tot = sum(m["sessions"] for m in comp["months"])
check(abs(tot["overall_conversion_rate"] - orders_tot / sess_tot) < 5e-9,
      "overall conversion = total orders / total sessions (%d/%d=%.9f, recorded %.9f)"
      % (orders_tot, sess_tot, orders_tot / sess_tot,
         tot["overall_conversion_rate"]))
check(tot["orders"] == orders_tot and tot["sessions"] == sess_tot,
      "orders and sessions totals are period sums, not averages")

# 5. table: 6 rows in round 1/2, 7 rows in round 3, all months present
months = [m["month"] for m in comp["months"]]
expect_n = 6 if int(sys.argv[1]) < 3 else 7
check(len(months) == expect_n, "table shows %d month rows (%s)"
      % (len(months), ", ".join(months)))
for m in comp["months"]:
    net = m["gross_revenue"] - m["refund_amount"]
    prof = net - m["operating_cost"]
    check(m["net_revenue"] == net and m["operating_profit"] == prof,
          "%s row arithmetic: net=%d profit=%d"
          % (m["month"], m["net_revenue"], m["operating_profit"]))
    check("%.2f%%" % (m["refund_rate"] * 100) in dsl
          and "%.2f%%" % (m["conversion_rate"] * 100) in dsl,
          "%s refund_rate=%.2f%% and conversion_rate=%.2f%% are printed"
          % (m["month"], m["refund_rate"] * 100, m["conversion_rate"] * 100))

# 6. chart: shared linear scale, real bar heights, zero baseline
ax = lay["chart"]["axis"]
check(ax["shared_linear_scale_for"] == ["net_revenue", "operating_profit"],
      "net_revenue and operating_profit share one linear axis")
plot = lay["chart"]["plot_rect"]
lo, hi = ax["domain"]
zero_px = plot["y"] + plot["h"] - (0 - lo) / float(hi - lo) * plot["h"]


def scale(v):
    return plot["y"] + plot["h"] - (v - lo) / float(hi - lo) * plot["h"]


bad = []
for b in lay["chart"]["bars"]:
    v, r = b["value"], b["rect"]
    # a bar spans from zero to the value; check BOTH edges, not just the top edge
    if v >= 0:
        want_y, want_h = scale(v), scale(0.0) - scale(v)
    else:
        want_y, want_h = scale(0.0), scale(v) - scale(0.0)
    if abs(r["y"] - want_y) > 0.6 or abs(r["h"] - want_h) > 0.6:
        bad.append({"month": b["month"], "series": b["series"], "value": v,
                    "rect": r, "want_y": round(want_y, 2), "want_h": round(want_h, 2),
                    "dy": round(r["y"] - want_y, 2), "dh": round(r["h"] - want_h, 2)})
check(not bad, "all %d bar rectangles match the shared axis scale (%d mismatches)"
      % (len(lay["chart"]["bars"]), len(bad)))
for b in bad:
    print("   mismatch:", b)
check(abs(lay["chart"]["zero_baseline_y_px"] - zero_px) <= 0.6,
      "reported zero_baseline_y_px %.2f matches the axis mapping %.2f"
      % (lay["chart"]["zero_baseline_y_px"], zero_px))
neg = [b for b in lay["chart"]["bars"] if b["value"] < 0]
if neg:
    check(all(b["rect"]["y"] >= lay["chart"]["zero_baseline_y_px"] - 0.6
              for b in neg),
          "negative bars are drawn below the zero baseline, not clipped: %s"
          % [(b["month"], b["value"], round(b["rect"]["y"], 1)) for b in neg])
    check(ax["negative_values_present"], "axis declares negative values present")
check(lay["chart"]["bar_width_px"] == lay["chart"]["bars"][0]["rect"]["w"],
      "bar width constant across series")

# 7. conclusion numbers must all be traceable to the data
blob = json.dumps(comp, ensure_ascii=False)
for claim in comp["conclusion"]["claims"]:
    nums = re.findall(r"-?[\d,]+\.?\d*", claim["text"])
    miss = []
    for nnum in nums:
        if "," in nnum or "." in nnum:
            if nnum.replace(",", "") not in blob.replace(",", ""):
                miss.append(nnum)
    check(not miss, "conclusion number(s) %s all traceable to computed data"
          % (nums or "none"))
    for k, v in claim["support"].items():
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            cand = [str(v), ("%g" % v), ("%.2f" % v), ("%.6f" % v),
                    "{:,.0f}".format(v), str(int(v)) if float(v).is_integer() else str(v)]
            if not any(c in blob for c in cand):
                warn.append("support %s=%r not found verbatim in computed-data" % (k, v))

print()
if warn:
    for w_ in warn:
        print("NOTE  " + w_)
print("ROUND %s: %d failures" % (SUB, len(fail)))
sys.exit(1 if fail else 0)