# -*- coding: utf-8 -*-
"""Cross-check A22 delivered files vs md5s recorded in reports (honesty gate)."""
import hashlib
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[4]
OUT = ROOT / "outputs/run-20261011-01/A22"

need = []
for r in ("round-01", "round-02", "round-03"):
    f = ["dashboard.png", "dashboard.snapshot", "computed-data.json",
         "layout-map.json", "snapshot-usage.md", "task-metrics.json"]
    if r != "round-01":
        f.append("change-audit.json")
    need += [r + "/" + x for x in f]
need += ["snapshot-usage.md", "task-metrics.json"]
missing = [n for n in need if not (OUT / n).exists()]
print("required files:", len(need), "| missing:", missing or "NONE")

# md5 of delivered binary/key files
actual = {}
for p in sorted(OUT.rglob("*")):
    if p.is_file() and p.suffix in (".png", ".snapshot", ".json"):
        actual[str(p.relative_to(OUT)).replace("\\", "/")] = hashlib.md5(
            p.read_bytes()).hexdigest()

# recorded full md5s + 8-char prefixes in reports
problems = []
for p in sorted(OUT.rglob("*")):
    if p.suffix not in (".json", ".md"):
        continue
    rel = str(p.relative_to(OUT)).replace("\\", "/")
    txt = p.read_text(encoding="utf-8")
    for h in re.findall(r"\b[0-9a-f]{32}\b", txt):
        if h not in actual.values():
            problems.append("%s: stale full md5 %s" % (rel, h))
    for pre in re.findall(r"`([0-9a-f]{8})\u2026`", txt):
        if not any(v.startswith(pre) for v in actual.values()):
            problems.append("%s: stale md5 prefix %s" % (rel, pre))
print("md5 records vs bytes:", problems or "ALL MATCH")

# PNG header + dims + snapshot == tmp DSL bytes
from PIL import Image
for r in ("round-01", "round-02", "round-03"):
    png = OUT / (r + "/dashboard.png")
    assert png.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n", r
    assert list(Image.open(png).size) == [1600, 1000], r
    a = hashlib.md5((OUT / (r + "/dashboard.snapshot")).read_bytes()).hexdigest()
    b = hashlib.md5((ROOT / ("tmp/run-20261011-01/A22/%s/dashboard.snapshot"
                             % r)).read_bytes()).hexdigest()
    assert a == b, "dsl mismatch " + r
print("PNG headers/dims OK; .snapshot == tmp DSL bytes for all 3 rounds")

# logs
req = [json.loads(l) for l in
       open(ROOT / "tmp/run-20261011-01/A22/requests.jsonl", encoding="utf-8")]
it = [json.loads(l) for l in
      open(ROOT / "tmp/run-20261011-01/A22/iterations.jsonl", encoding="utf-8")]
print("requests.jsonl: %d | ok=%d fail=%d"
      % (len(req), sum(1 for r in req if r["ok"]),
         sum(1 for r in req if not r["ok"])))
print("iterations.jsonl: %d (seq %s, kinds %s)"
      % (len(it), [e["seq"] for e in it], [e["kind"] for e in it]))
print("delivered files:", sum(1 for p in OUT.rglob("*") if p.is_file()))
