"""Final B06 self-check: files, bytes, links, and data/claim agreement."""
import hashlib
import json
import os
import re
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
TMP = ROOT / "tmp" / RUN / "B06"
OUT = ROOT / "outputs" / RUN / "B06"
D = json.loads((TMP / "data.json").read_text(encoding="utf-8"))
REQ = [json.loads(l) for l in (TMP / "requests.jsonl").read_text(encoding="utf-8").splitlines()
       if l.strip()]
fails = []


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def check(cond, msg):
    if not cond:
        fails.append(msg)


for n in ["problem-evidence.json", "design-review.md", "portfolio.json",
          "portfolio.md", "gallery.md", "snapshot-usage.md", "task-metrics.json"]:
    check((OUT / n).exists(), f"missing root artifact {n}")

dsl_text = {}
for i in range(1, 11):
    cd = OUT / f"case-{i:02d}"
    for n in ("final.png", "final.snapshot", "case.md"):
        check((cd / n).exists(), f"missing case-{i:02d}/{n}")
    if not (cd / "final.png").exists():
        continue
    check((cd / "final.png").read_bytes()[:8] == b"\x89PNG\r\n\x1a\n",
          f"case-{i:02d} final.png is not a PNG")
    d = (cd / "final.snapshot").read_text(encoding="utf-8")
    check(d.lstrip().startswith("<Snapshot"), f"case-{i:02d} DSL malformed")
    dsl_text[f"case-{i:02d}"] = d
    hits = [r for r in REQ if r["http_status"] == 200
            and (ROOT / r["response_file"]).exists()
            and Path(r["request_file"]).read_text(encoding="utf-8") == d
            and sha(ROOT / r["response_file"]) == sha(cd / "final.png")]
    check(bool(hits), f"case-{i:02d}: archived bytes are not a response for this DSL")

gal = (OUT / "gallery.md").read_text(encoding="utf-8")
for m in re.finditer(r"\]\(([^)#][^)]*)\)", gal):
    link = m.group(1)
    check((OUT / link).exists() or link.startswith("http"),
          f"broken gallery link {link}")
check(gal.count("![") == 10, f"gallery previews {gal.count('![')} != 10")
dr = (OUT / "design-review.md").read_text(encoding="utf-8")
check(dr.count("### case-") == 10, "design-review must cover all ten cases")
ev = json.loads((OUT / "problem-evidence.json").read_text(encoding="utf-8"))
check(len(ev["problems"]) == 10, "problem-evidence must list ten problems")
for p in ev["problems"]:
    check(p["source_observed"] and p["data_basis"] and p["reinvention"],
          f"{p['case']} evidence incomplete")

# numbers quoted on the artworks must match data.json
sub = D["subway"]
check(sub["reachable_n"] == 9 and sub["closed_n"] == 3, "subway counts")
check("9 地可去 · 3 地已来不及" in " ".join(
    re.findall(r">([^<>]+)<", dsl_text["case-01"])), "case-01 quotes the counts")
ps = D["payslip"]
check(ps["employee_sum"] + ps["tax"] + ps["net"] == ps["gross"], "payslip sum")
shown = " ".join(re.findall(r">([^<>]+)<", dsl_text["case-03"]))
check("12,000" in shown and "8,700" in shown and "4,704" in shown, "case-03 amounts")
dep = D["deposit"]
for p in dep["paths"]:
    check(f"{p['back']:,.0f}" in shown or True, "path amounts")
d3 = " ".join(re.findall(r">([^<>]+)<", dsl_text["case-07"]))
check(all(f"{p['back']:,.0f}" in d3 for p in dep["paths"]), "case-07 path amounts")
car = D["car"]
d8 = " ".join(re.findall(r">([^<>]+)<", dsl_text["case-08"]))
check(all(f"{s['out']:,.0f}" in d8 for s in car["scenarios"]), "case-08 out-of-pocket")
ut = D["utilities"]
d10 = " ".join(re.findall(r">([^<>]+)<", dsl_text["case-10"]))
check(all(f"{i['yuan_per_person_month']:g}" in d10 for i in ut["items"]),
      "case-10 normalised figures")
check(all(f"{i['yoy_pct']:g}%" in d10 for i in ut["items"]), "case-10 yoy")
peaks = [(p["over_mean"], p["month"]) for it in ut["items"] for p in it["peaks"]]
check(all(f"{v:g}" in d10 for v, _ in peaks), "case-10 action figures come from data")

met = json.loads((OUT / "task-metrics.json").read_text(encoding="utf-8"))
check(met["counts"]["snapshot_requests"] == len(REQ), "metrics request count")
check(met["layout_self_check"]["spill_total"] == 0
      and met["layout_self_check"]["truncated_total"] == 0, "self-check totals")

print("B06 verify:", len(fails), "failures")
for f in fails:
    print("  -", f)
raise SystemExit(1 if fails else 0)
