"""Final B05 self-check: files present, bytes consistent, links resolvable, data single-sourced."""
import hashlib
import json
import os
import re
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
TMP = ROOT / "tmp" / RUN / "B05"
OUT = ROOT / "outputs" / RUN / "B05"
D = json.loads((TMP / "data.json").read_text(encoding="utf-8"))
REQ = [json.loads(l) for l in (TMP / "requests.jsonl").read_text(encoding="utf-8").splitlines()
       if l.strip()]
fails = []


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def check(cond, msg):
    if not cond:
        fails.append(msg)


# 1. required files
for n in ["product-brief.md", "journey.json", "portfolio.json", "portfolio.md",
          "gallery.md", "snapshot-usage.md", "task-metrics.json"]:
    check((OUT / n).exists(), f"missing root artifact {n}")
for i in range(1, 11):
    cd = OUT / f"case-{i:02d}"
    for n in ("final.png", "final.snapshot", "case.md"):
        check((cd / n).exists(), f"missing case-{i:02d}/{n}")
    check((cd / "final.png").read_bytes()[:8] == b"\x89PNG\r\n\x1a\n",
          f"case-{i:02d} final.png is not a PNG")
    check(cd.joinpath("final.snapshot").read_text(encoding="utf-8").lstrip()
          .startswith("<Snapshot"), f"case-{i:02d} DSL malformed")

# 2. archived DSL is exactly what the builder produces today
for i in range(1, 11):
    stem = json.loads((TMP / "case-manifest.json").read_text(encoding="utf-8"))[i - 1]["dsl_stem"]
    src = TMP / f"{stem}.snapshot"
    dst = OUT / f"case-{i:02d}" / "final.snapshot"
    check(sha(src) == sha(dst), f"{stem}: archived DSL differs from the builder output")

# 3. archived PNG is a real service response for that exact DSL text
dsl_text = {(OUT / f"case-{i:02d}" / "final.snapshot").read_text(encoding="utf-8")
            for i in range(1, 11)}
for i in range(1, 11):
    cd = OUT / f"case-{i:02d}"
    png_sha = sha(cd / "final.png")
    dsl = (cd / "final.snapshot").read_text(encoding="utf-8")
    ok = [r for r in REQ
          if r["http_status"] == 200 and (ROOT / r["response_file"]).exists()
          and Path(r["request_file"]).read_text(encoding="utf-8") == dsl
          and sha(ROOT / r["response_file"]) == png_sha]
    check(bool(ok), f"case-{i:02d}: no logged 200 response matches the archived pair")

# 4. gallery links resolve relative to the gallery file
gal = (OUT / "gallery.md").read_text(encoding="utf-8")
for m in re.finditer(r"\]\(([^)#][^)]*)\)", gal):
    link = m.group(1)
    check((OUT / link).exists() or link.startswith("http"),
          f"broken gallery link {link}")
check(gal.count("![") == 10, f"gallery previews {gal.count('![')} != 10")

# 5. cross-screen data consistency
meds = {m["id"]: m for m in D["meds"]}
check(meds["M3"]["remaining"] == 3 and meds["M3"]["expiry_days"] == 7, "M3 facts")
check(meds["M5"]["expiry_days"] == 85, "M5 must use the opened-date expiry everywhere")
check(D["per_person"]["gm"]["adherence_14"] == 92.9, "gm aggregate rate")
gm_miss = sum(r.count("漏") for mid in ("M1", "M2", "M3") for r in D["grid14"][mid])
check(gm_miss == D["per_person"]["gm"]["missed_14"],
      f"grid shows {gm_miss} misses, per_person says {D['per_person']['gm']['missed_14']}")
import re as _re
for mid, m in meds.items():
    if m["printed_expiry_days"] == m["expiry_days"]:
        continue
    for p in sorted(OUT.glob("case-*/final.snapshot")):
        # only what the screen actually shows, not coordinates or measured widths
        shown = " ".join(_re.findall(r">([^<>]+)<", p.read_text(encoding="utf-8")))
        check(str(m["printed_expiry_days"]) not in shown,
              f"{p.parent.name} still quotes the printed {m['printed_expiry_days']}d for {mid}")

# 6. metrics freshness
met = json.loads((OUT / "task-metrics.json").read_text(encoding="utf-8"))
check(met["counts"]["snapshot_requests"] == len(REQ),
      f"metrics {met['counts']['snapshot_requests']} vs log {len(REQ)}")
check(met["counts"]["final_case_count"] == 10, "metrics case count")

print("B05 verify:", len(fails), "failures")
for f in fails:
    print("  -", f)
raise SystemExit(1 if fails else 0)
