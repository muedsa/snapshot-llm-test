# -*- coding: utf-8 -*-
"""A23 final verification: tree, md5 cross-check, alpha, JSON identity."""
import hashlib
import json
import pathlib
import re
from PIL import Image

ROOT = pathlib.Path(".")
OUT = ROOT / "outputs/run-20261011-01/A23"
TMPR = ROOT / "tmp/run-20261011-01/A23"

need = ["cover.png", "cover.snapshot", "frame-data.json", "timing.json",
        "limitations.md", "snapshot-usage.md", "task-metrics.json"] + \
       ["frame-%02d.%s" % (k, e) for k in range(1, 7)
        for e in ("png", "snapshot")]
missing = [n for n in need if not (OUT / n).exists()]
print("required files: %d | missing: %s" % (len(need), missing or "NONE"))

actual = {}
for p in sorted(OUT.rglob("*")):
    if p.is_file() and p.suffix in (".png", ".snapshot"):
        actual[p.name] = hashlib.md5(p.read_bytes()).hexdigest()

problems = []
for p in sorted(OUT.rglob("*")):
    if p.suffix not in (".json", ".md"):
        continue
    txt = p.read_text(encoding="utf-8")
    for h in re.findall(r"\b[0-9a-f]{32}\b", txt):
        if h not in actual.values():
            problems.append("%s: stale full md5 %s" % (p.name, h))
    for pre in re.findall(r"`([0-9a-f]{8})\u2026`", txt):
        if not any(v.startswith(pre) for v in actual.values()):
            problems.append("%s: stale md5 prefix %s" % (p.name, pre))
print("md5 records vs bytes:", problems or "ALL MATCH")

# PNG dims + alpha + snapshot == tmp DSL bytes
for k in range(1, 7):
    im = Image.open(OUT / ("frame-%02d.png" % k)).convert("RGBA")
    assert im.size == (600, 600) and im.load()[0, 0][3] == 0, k
    a = hashlib.md5((OUT / ("frame-%02d.snapshot" % k)).read_bytes())
    b = hashlib.md5((TMPR / "frames" / ("frame-%02d.snapshot" % k))
                    .read_bytes())
    assert a.hexdigest() == b.hexdigest(), "dsl mismatch f%02d" % k
cov = Image.open(OUT / "cover.png").convert("RGBA")
assert cov.size == (1200, 800) and cov.load()[0, 0][3] == 255
a = hashlib.md5((OUT / "cover.snapshot").read_bytes())
b = hashlib.md5((TMPR / "cover.snapshot").read_bytes())
assert a.hexdigest() == b.hexdigest(), "dsl mismatch cover"
print("PNG dims/alpha OK (6 frames RGBA transparent, cover opaque); "
      ".snapshot == submitted DSL bytes")

# JSON identity + cross refs
for name in ("frame-data.json", "timing.json", "task-metrics.json"):
    d = json.load(open(OUT / name, encoding="utf-8"))
    assert d["schema_version"] == 1 and d["task_id"] == "A23" \
        and d["path_base"] == "output_dir", name
fd = json.load(open(OUT / "frame-data.json", encoding="utf-8"))
for fr in fd["frames"]:
    assert (OUT / fr["png"]).exists() and (OUT / fr["dsl"]).exists()
    assert len(fr["units"]) == 12 and all(u["visible"] for u in fr["units"])
    assert [u["id"] for u in fr["units"]] == \
        ["U%02d" % i for i in range(1, 13)]
assert fd["seam"]["seamless"] is False and len(fd["seam"]["per_id"]) == 12
assert len(fd["trajectories"]) == 12 and all(
    len(t["steps"]) == 5 for t in fd["trajectories"])
tj = json.load(open(OUT / "timing.json", encoding="utf-8"))
assert [f["t_ms"] for f in tj["frames"]] == [0, 250, 500, 750, 1000, 1250]
assert tj["loop"]["period_ms"] == 1500 and tj["loop"]["seamless"] is False
print("JSON identity fields OK; frame refs exist; 12 units x 6 frames; "
      "t series 0..1250ms; seam not seamless (honest)")

reqs = [json.loads(l) for l in open(TMPR / "requests.jsonl",
                                    encoding="utf-8")]
its = [json.loads(l) for l in open(TMPR / "iterations.jsonl",
                                   encoding="utf-8")]
mm = json.load(open(OUT / "task-metrics.json", encoding="utf-8"))
assert len(reqs) == mm["counts"]["snapshot_requests"] == 19
assert sum(1 for r in reqs if r["ok"]) == 18
assert len(its) == mm["counts"]["iteration_entries_total"] == 4
print("logs consistent: requests=%d (18 ok), iterations=%d"
      % (len(reqs), len(its)))
print("delivered files:", sum(1 for p in OUT.rglob("*") if p.is_file()))
print("VERIFICATION: PASS" if not problems and not missing else "FAIL")
