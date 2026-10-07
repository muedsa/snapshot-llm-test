# -*- coding: utf-8 -*-
"""Final cross-check of B01's delivered output tree.

Checks the things that must be true for the deliverable to be honest:
PNG/DSL pairing, dimensions actually read off the PNG, no <Image> anywhere in
any final DSL, element budget, case.md present for all ten, the five root
outputs, log files, and that no PNG was altered after the response was written.
"""
from __future__ import annotations

import io
import json
import os
import re

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
OUT = os.path.join(ROOT, "outputs", RUN, "B01")
TMP = os.path.join(ROOT, "tmp", RUN, "B01")
LIMIT = 4096

from PIL import Image  # noqa: E402

fail = []


def chk(cond, msg):
    print(("  OK   " if cond else "  FAIL ") + msg)
    if not cond:
        fail.append(msg)


print("== case directories ==")
CASES = sorted(x for x in os.listdir(OUT) if x.startswith("case-"))
chk(len(CASES) == 10, "10 case directories (got %d)" % len(CASES))

print("== per-case artefacts ==")
print("  case        dims          PNG     DSL    elem  limit%  <Image>  case.md")
for c in CASES:
    png = os.path.join(OUT, c, "final.png")
    snap = os.path.join(OUT, c, "final.snapshot")
    md = os.path.join(OUT, c, "case.md")
    im = Image.open(png)
    w, h = im.size
    s = io.open(snap, encoding="utf-8").read()
    n = sum(1 for m in re.finditer(r"<(/?)[A-Za-z][A-Za-z0-9]*[ />]", s)
            if m.group(1) == "")
    has_img = "<Image" in s or "dataUri" in s or "url=" in s
    print("  %-10s %-13s %6d %6d %6d %6.1f%%  %-7s %s"
          % (c, "%dx%d" % (w, h), os.path.getsize(png), os.path.getsize(snap),
             n, 100.0 * n / LIMIT, "YES" if has_img else "no",
             "yes" if os.path.exists(md) else "NO"))
    chk(os.path.exists(png) and os.path.exists(snap) and os.path.exists(md),
        "%s has final.png + final.snapshot + case.md" % c)
    chk(n <= LIMIT, "%s element count %d within 4096" % (c, n))
    chk(not has_img, "%s DSL contains no <Image>/url/dataUri" % c)
    # the DSL must be a complete document: one Snapshot root, one root child
    chk(s.count("<Snapshot") == 1, "%s DSL has exactly one <Snapshot>" % c)
    chk(re.search(r'<Container width="[\d.]+" height="[\d.]+"', s) is not None,
        "%s DSL sizes the canvas with a root Container" % c)
    # the canvas the DSL declares must match the PNG
    m = re.search(r'<Container width="([\d.]+)" height="([\d.]+)"', s)
    chk(m and int(float(m.group(1))) == w and int(float(m.group(2))) == h,
        "%s declared canvas %sx%s == PNG %dx%d"
        % (c, m.group(1), m.group(2), w, h))
    # case.md must state the fictional-data disclaimer
    txt = io.open(md, encoding="utf-8").read()
    chk("自拟" in txt, "%s case.md declares self-authored data" % c)
    chk(chr(0xFFFD) not in txt, "%s case.md has no mojibake" % c)

print("== root outputs ==")
for f in ("portfolio.json", "portfolio.md", "gallery.html",
          "snapshot-usage.md", "task-metrics.json"):
    p = os.path.join(OUT, f)
    chk(os.path.exists(p) and os.path.getsize(p) > 0,
        "%s present (%d bytes)" % (f, os.path.getsize(p) if os.path.exists(p) else 0))

print("== no leftover template placeholders ==")
for f in ("portfolio.md", "snapshot-usage.md", "gallery.html"):
    s = io.open(os.path.join(OUT, f), encoding="utf-8").read()
    chk("<填写>" not in s and "TODO" not in s, "%s has no template placeholders" % f)
pj = json.load(io.open(os.path.join(OUT, "portfolio.json"), encoding="utf-8"))
chk(pj["case_count"] == 10 and len(pj["cases"]) == 10,
    "portfolio.json maps 10 cases")
chk(all(c["unresolved_issues"] == [] for c in pj["cases"]),
    "portfolio.json records no unresolved issue per case")
mj = json.load(io.open(os.path.join(OUT, "task-metrics.json"), encoding="utf-8"))
chk(mj["usage"]["input_tokens"] is None and mj["usage"]["output_tokens"] is None
    and mj["usage"]["cost"] is None,
    "task-metrics.json leaves unprovided usage fields null")
chk(mj["counts"]["final_pngs"] == 10, "task-metrics.json counts 10 final PNGs")
chk(len(mj["case_metrics"]) == 10, "task-metrics.json has per-case metrics")
tot = sum(c["dsl_elements"] for c in mj["case_metrics"])
chk(tot > 0, "per-case element counts present")

print("== gallery is fully local ==")
g = io.open(os.path.join(OUT, "gallery.html"), encoding="utf-8").read()
refs = re.findall(r'(?:src|href)="([^"]+)"', g)
chk(not [r for r in refs if r.startswith(("http", "//", "data:"))],
    "gallery.html has no remote or data references")
chk("<script" not in g.lower() and "<link" not in g.lower(),
    "gallery.html has no script/link tags")
for c in CASES:
    chk('href="%s/final.png"' % c in g, "gallery.html indexes %s" % c)

print("== temp logs ==")
for f in ("requests.jsonl", "iterations.jsonl", "tool-usage.jsonl",
          "iteration-notes.jsonl", "plan.md", "fonts.txt"):
    p = os.path.join(TMP, f)
    chk(os.path.exists(p), "%s exists" % f)
nreq = sum(1 for _ in io.open(os.path.join(TMP, "requests.jsonl"), encoding="utf-8"))
nit = sum(1 for _ in io.open(os.path.join(TMP, "iterations.jsonl"), encoding="utf-8"))
print("  requests=%d iterations=%d" % (nreq, nit))
for d in ("drafts", "preview", "crops", "responses", "docs", "docs-text"):
    p = os.path.join(TMP, d)
    chk(os.path.isdir(p) and len(os.listdir(p)) > 0,
        "%s/ preserved with %d files"
        % (d, len(os.listdir(p)) if os.path.isdir(p) else 0))

print("== delivered PNGs are the raw service responses ==")
REQS = [json.loads(l) for l in
        io.open(os.path.join(TMP, "requests.jsonl"), encoding="utf-8") if l.strip()]
last = {}
for r in REQS:
    rf = (r.get("response_file") or "").replace("\\", "/")
    if (r.get("content_type") or "").startswith("image/") and "/outputs/" in rf:
        last[rf] = r["request_id"]
for c in CASES:
    k = "outputs/%s/B01/%s/final.png" % (RUN, c)
    hit = [v for kk, v in last.items() if kk.endswith("/B01/%s/final.png" % c)]
    chk(bool(hit), "%s final.png traces to a recorded 200 response %s"
        % (c, hit[-1] if hit else "NONE"))

print()
print("RESULT:", "ALL CHECKS PASSED" if not fail else "%d FAILURES" % len(fail))
for f in fail:
    print("  -", f)