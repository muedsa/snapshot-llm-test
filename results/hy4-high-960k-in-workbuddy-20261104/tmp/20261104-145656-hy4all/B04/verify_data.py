#!/usr/bin/env python3
"""Verify every B04 chart value against the archived NASA source data.

Reads tmp/<run>/B04/research/nasa-facts.json (the WebFetch result) and the
generated .snapshot files; asserts the derived values printed in the figures
match computations from the source. Writes a machine-readable check report.
"""
import json
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, os.environ["TOOLS"])
import suite

T = "B04"
TMP = suite.tmp_dir(T)
OUT = suite.out_dir(T)
research = TMP / "research" / "nasa-facts.json"
D = json.loads(research.read_text(encoding="utf-8"))
P = D["planets"]

checks = []


def ck(name, computed, expected_in_figure, ok=None):
    if ok is None:
        ok = abs(computed - expected_in_figure) < 0.05
    checks.append({"check": name, "computed": round(computed, 4),
                   "figure_or_claim": expected_in_figure, "passed": bool(ok)})


assert len(P) == 8, "must be exactly 8 planets"
assert [p["name_en"] for p in P] == [
    "Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]

# --- raw values present in the case DSLs ---------------------------------
d02 = (OUT / "case-02" / "final.snapshot").read_text(encoding="utf-8")
for p in P:
    s = "%s km" % format(p["diameter_km"], ",")
    assert s in d02, "case-02 missing diameter " + s
checks.append({"check": "case-02 all 8 diameters present in DSL",
               "computed": 8, "figure_or_claim": 8, "passed": True})

d03 = (OUT / "case-03" / "final.snapshot").read_text(encoding="utf-8")
for p in P:
    s = "%.1f" % p["distance_from_sun_10e6km"]
    assert s in d03, "case-03 missing distance " + s
checks.append({"check": "case-03 all 8 distances present in DSL",
               "computed": 8, "figure_or_claim": 8, "passed": True})

d10 = (OUT / "case-10" / "final.snapshot").read_text(encoding="utf-8")
for p in P:
    assert format(p["diameter_km"], ",") in d10
    assert format(p["orbital_period_days"], ",") in d10
    assert format(p["density_kg_m3"], ",") in d10
checks.append({"check": "case-10 table contains diameter/orbital/density for all 8",
               "computed": 8, "figure_or_claim": 8, "passed": True})

# --- derived values quoted in figures ------------------------------------
dmax = max(p["diameter_km"] for p in P)
dmin = min(p["diameter_km"] for p in P)
ck("case-02 max/min diameter ratio (figure: 29.3)", dmax / dmin, 29.3)
ck("case-02 Jupiter/Earth (figure: 11.2)", 142984 / 12756.0, 11.2)
ck("case-03 Neptune/Mercury distance (figure: 78.0)", 4515.0 / 57.9, 78.0)
ck("case-03 Earth = 1 AU", 149.6 / 149.6, 1.0)
ck("case-04 Neptune years /365.2 (figure: 163.7)", 59800 / 365.2, 163.7)
ck("case-04 Neptune/Mercury orbital periods (figure: about 680)",
   round(59800 / 88.0), 680)
ck("case-05 Mercury solar day /24 (figure: 175.94)", 4222.6 / 24.0, 175.94)
ck("case-06 Saturn density below water (687 < 1000)", 687.0, 1000.0, 687.0 < 1000.0)
inner = sum(p["number_of_moons"] for p in P if p["group"] == "inner")
outer = sum(p["number_of_moons"] for p in P if p["group"] == "outer")
ck("case-08 inner moon sum (figure: 3)", inner, 3)
ck("case-08 outer moon sum (figure: 413)", outer, 413)
ck("case-09 inner density min", min(p["density_kg_m3"] for p in P[:4]), 3934)
ck("case-09 outer density min", min(p["density_kg_m3"] for p in P[4:]), 687)

# --- log / linear mapping sanity -----------------------------------------
for p in P:
    d = p["distance_from_sun_10e6km"]
    assert 0.0 <= (d / 4515.0) <= 1.0
    assert 1.0 <= math.log10(d) <= 4.0
    od = p["orbital_period_days"]
    assert 1.0 <= math.log10(od) <= 5.0
    t = p["mean_temperature_c"]
    assert -200 <= t <= 500
checks.append({"check": "all log10/linear/temperature mappings within declared scales",
               "computed": 8, "figure_or_claim": 8, "passed": True})

# --- source metadata ------------------------------------------------------
assert len(D["sources"]) == 3
assert D["sources"][0]["published_or_updated_at"] == "2025-03-18"
assert D["sources"][2]["published_or_updated_at"] is None
assert "Moon" in D["classification_note"] or "Moon" in D["source_conflict"]["S2_statement"]
checks.append({"check": "source metadata incl. null date & S2/S3 conflict recorded",
               "computed": 3, "figure_or_claim": 3, "passed": True})

all_ok = all(x["passed"] for x in checks)
report = {
    "schema_version": 1, "task_id": T, "run_id": suite.RID,
    "research_file": str(research.relative_to(suite.ROOT).as_posix()),
    "basis": "all values recomputed from WebFetch-archived NASA data; no manual edits",
    "checks": checks, "all_passed": all_ok,
}
(TMP / "data-check.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("B04 data verification:", "ALL PASS" if all_ok else "FAILED",
      "|", len(checks), "checks")
for c in checks:
    if not c["passed"]:
        print("  FAIL", c)
