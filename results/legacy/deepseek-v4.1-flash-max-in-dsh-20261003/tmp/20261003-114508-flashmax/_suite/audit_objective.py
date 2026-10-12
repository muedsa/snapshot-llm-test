"""Whole-objective audit: prove every clause of the goal against files on disk.

Nothing here trusts a status field on its own. Each clause of the objective is turned into a
check that reads the filesystem (and, where relevant, the per-task logs), so the run can only
report "achieved" for clauses that are actually supported by artefacts.
"""
from __future__ import annotations

import json
import os
import re
import sys

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN = "20261003-114508-flashmax"
OUT = os.path.join(ROOT, "outputs", RUN)
TMP = os.path.join(ROOT, "tmp", RUN)
SUITE = os.path.join(OUT, "_suite")

CAT = json.load(open(os.path.join(ROOT, "catalog.json"), encoding="utf-8"))
ORDER = CAT["task_order"]
TASKS = {t["id"]: t for t in CAT["tasks"]}
MIN = json.load(open(os.path.join(TMP, "_suite", "min-pngs.json"), encoding="utf-8"))
STATE = json.load(open(os.path.join(SUITE, "suite-state.json"), encoding="utf-8"))
SMAP = {t["id"]: t for t in STATE["tasks"]}
FAILS: list[str] = []
NOTES: list[str] = []


def check(cond, label, detail=""):
    print(("  PASS  " if cond else "  FAIL  ") + label + ((" | " + detail) if detail else ""))
    if not cond:
        FAILS.append(label + ((" | " + detail) if detail else ""))
    return cond


print("=" * 78)
print("CLAUSE 1  every task in catalog.json task_order has its real artefacts")
print("=" * 78)
total_png = 0
for tid in ORDER:
    d = os.path.join(OUT, tid)
    tmp = os.path.join(TMP, tid)
    inputs = os.path.join(ROOT, TASKS[tid]["directory"].replace("/", os.sep))
    pngs = []
    for base, _dd, ff in os.walk(d):
        for f in ff:
            if f.lower().endswith(".png"):
                pngs.append(os.path.join(base, f))
    unpaired = [p for p in pngs if not os.path.exists(os.path.splitext(p)[0] + ".snapshot")]
    total_png += len(pngs)
    ok = (os.path.isdir(d) and os.path.isdir(tmp)
          and len(pngs) >= MIN[tid] and not unpaired
          and os.path.exists(os.path.join(d, "snapshot-usage.md"))
          and os.path.exists(os.path.join(d, "task-metrics.json"))
          and os.path.exists(os.path.join(tmp, "requests.jsonl"))
          and os.path.exists(os.path.join(tmp, "iterations.jsonl"))
          and os.path.exists(os.path.join(inputs, "TASK.md"))
          and os.path.exists(os.path.join(inputs, "task.json")))
    check(ok, f"{tid}: {len(pngs)} png >= {MIN[tid]}, all paired, report+metrics+logs present",
          f"unpaired={len(unpaired)}" if unpaired else "")
check(total_png >= (CAT.get("minimum_final_pngs") or 0),
      f"suite total final PNGs {total_png} >= minimum {CAT.get('minimum_final_pngs')}")

print()
print("=" * 78)
print("CLAUSE 2  one single run_id used everywhere (no stray run directories)")
print("=" * 78)
runs = sorted(x for x in os.listdir(os.path.join(ROOT, "outputs")) if os.path.isdir(os.path.join(ROOT, "outputs", x)))
check(runs == [RUN], "outputs/ holds exactly the one run_id", str(runs))
# tmp/ legitimately also holds the shared _suite preparation area and the harness's own
# _acl-reports diagnostics; the check is that no SECOND run_id directory exists.
truns = sorted(x for x in os.listdir(os.path.join(ROOT, "tmp"))
               if os.path.isdir(os.path.join(ROOT, "tmp", x)) and x[:8].isdigit())
check(truns == [RUN], "tmp/ holds exactly one run_id directory", str(truns))
check(os.path.isdir(os.path.join(ROOT, "tmp", "_suite")),
      "tmp/_suite shared preparation area exists", "")

print()
print("=" * 78)
print("CLAUSE 3  renders really came from the live service (logged 200 + image/png)")
print("=" * 78)
svc = 0
bad = []
for tid in ORDER + ["_suite"]:
    p = os.path.join(TMP, tid, "requests.jsonl")
    if not os.path.exists(p):
        continue
    with open(p, encoding="utf-8-sig") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                bad.append(f"{tid}: unparsable log line")
                continue
            if r.get("success") and r.get("http_status") == 200 and "image" in str(r.get("content_type", "")):
                svc += 1
check(svc > 700, f"{svc} logged responses were HTTP 200 with an image content-type", "")
check(not bad, "every requests.jsonl line is valid JSON", str(bad[:3]))

print()
print("=" * 78)
print("CLAUSE 4  A21 / A22 completed three preloaded rounds each")
print("=" * 78)
for tid in ("A21", "A22"):
    rounds_req = sorted(x for x in os.listdir(os.path.join(ROOT, TASKS[tid]["directory"].replace("/", os.sep), "rounds"))
                        if x.endswith(".md"))
    d = os.path.join(OUT, tid)
    got = []
    for rn in ("round-01", "round-02", "round-03"):
        rd = os.path.join(d, rn)
        if not os.path.isdir(rd):
            continue
        rpng = [f for f in os.listdir(rd) if f.endswith(".png")]
        rdsl = [f for f in os.listdir(rd) if f.endswith(".snapshot")]
        got.append((rn, len(rpng), len(rdsl), os.path.exists(os.path.join(rd, "task-metrics.json"))))
    # round-01's requirements live in TASK.md; the task ships the two FOLLOW-UP rounds as files
    check(rounds_req == ["round-02.md", "round-03.md"],
          f"{tid}: ships the two follow-up round files (round-01 spec is TASK.md)", str(rounds_req))
    check([g[0] for g in got] == ["round-01", "round-02", "round-03"],
          f"{tid}: three separate round directories exist", str([g[0] for g in got]))
    check(all(g[1] >= 1 and g[1] == g[2] and g[3] for g in got),
          f"{tid}: each round has its own paired PNG+DSL and its own metrics", str(got))
    check(os.path.exists(os.path.join(d, "snapshot-usage.md"))
          and os.path.exists(os.path.join(d, "task-metrics.json")),
          f"{tid}: task-level cumulative report and metrics exist", "")

print()
print("=" * 78)
print("CLAUSE 5  B01-B06 each has >=10 independent complete works")
print("=" * 78)
for tid in ("B01", "B02", "B03", "B04", "B05", "B06"):
    d = os.path.join(OUT, tid)
    cases = sorted(x for x in os.listdir(d) if re.fullmatch(r"case-\d+", x))
    complete = []
    for c in cases:
        cd = os.path.join(d, c)
        if (os.path.exists(os.path.join(cd, "final.png"))
                and os.path.exists(os.path.join(cd, "final.snapshot"))
                and os.path.exists(os.path.join(cd, "case.md"))):
            complete.append(c)
    root_files = set(os.listdir(d))
    need_root = {"portfolio.json", "portfolio.md", "gallery.html", "snapshot-usage.md", "task-metrics.json"}
    check(len(complete) >= 10, f"{tid}: {len(complete)} independent works with final.png+final.snapshot+case.md",
          f"cases={len(cases)}")
    check(need_root <= root_files, f"{tid}: portfolio + gallery + report + metrics at task root",
          str(sorted(need_root - root_files)))

print()
print("=" * 78)
print("CLAUSE 6  the five required _suite deliverables exist and are self-consistent")
print("=" * 78)
need = ["index.md", "gallery.html", "snapshot-usage.md", "task-metrics.json", "suite-state.json"]
for n in need:
    p = os.path.join(SUITE, n)
    check(os.path.exists(p) and os.path.getsize(p) > 1000, f"_suite/{n} exists and is non-trivial",
          f"{os.path.getsize(p) if os.path.exists(p) else 0} B")

tm = json.load(open(os.path.join(SUITE, "task-metrics.json"), encoding="utf-8"))
check(tm["status_counts"]["completed"] == len(ORDER), "task-metrics status_counts.completed == 30",
      str(tm["status_counts"]))
check(tm["final_pngs_total"] == total_png, "task-metrics final_pngs_total matches a fresh disk count",
      f"{tm['final_pngs_total']} vs {total_png}")
check(tm["final_pngs_meets_minimum"] is True, "task-metrics states the PNG minimum is met", "")
check(tm["resources"]["tokens"] is None and tm["resources"]["image_inputs"] is None
      and tm["resources"]["money"] is None, "unavailable platform resources are recorded as null, not invented", "")
check("source" in tm["requests"], "request totals state their source", tm["requests"].get("source", "")[:60])

g = open(os.path.join(SUITE, "gallery.html"), encoding="utf-8").read()
imgs = re.findall(r"<img[^>]*src='\.\./([^']+)'", g)
link = re.findall(r"<a[^>]*href='\.\./([^']+)'", g)
on_disk = set()
for base, _dd, ff in os.walk(OUT):
    if os.sep + "_suite" in base:
        continue
    for f in ff:
        if f.lower().endswith(".png"):
            on_disk.add(os.path.relpath(os.path.join(base, f), OUT).replace(os.sep, "/"))
broken = [s for s in imgs if not os.path.exists(os.path.join(OUT, s.replace("/", os.sep)))]
check(len(imgs) == total_png, f"gallery indexes every final PNG ({len(imgs)} of {total_png})", "")
check(not broken, "no broken gallery image paths", str(broken[:3]))
check(set(imgs) == on_disk, "gallery set equals the set of PNGs on disk", "")
check(len(re.findall(r"(?:src|href)=[\"'](?:https?:)?//", g)) == 0, "gallery has zero remote references", "")
check(len(re.findall(r"<script", g)) == 0, "gallery has zero script tags", "")
check(len(link) == len(imgs), "every image is clickable to full size", f"{len(link)} links")

st = json.load(open(os.path.join(SUITE, "suite-state.json"), encoding="utf-8"))
check(st["status"] == "completed", "suite-state status == completed", st["status"])
check(all(t["status"] == "completed" for t in st["tasks"]), "every task status == completed", "")
check(all(t.get("visual_review_evidence") for t in st["tasks"]), "every task records visual-review evidence", "")
check(all(t.get("artifacts") for t in st["tasks"]), "every task lists its artefacts", "")
check(os.path.isdir(os.path.join(TMP, "_suite", "checkpoints"))
      and len(os.listdir(os.path.join(TMP, "_suite", "checkpoints"))) >= 30,
      "progress checkpoints were written throughout",
      str(len(os.listdir(os.path.join(TMP, "_suite", "checkpoints")))))

print()
print("=" * 78)
print("CLAUSE 7  no fabricated completion: everything claimed is backed by a file")
print("=" * 78)
idx = open(os.path.join(SUITE, "index.md"), encoding="utf-8").read()
listed = re.findall(r"`([A-Z]\d\d/[^`]+\.png)`", idx)
check(len(listed) == total_png, f"index.md lists every final PNG path ({len(listed)})", "")
check(all(os.path.exists(os.path.join(OUT, p.replace("/", os.sep))) for p in listed),
      "every path printed in index.md exists on disk", "")
unres = tm.get("unresolved") or []
check(len(unres) > 0, f"limitations are disclosed rather than hidden ({len(unres)} tasks)", "")

print()
print("=" * 78)
if FAILS:
    print(f"AUDIT RESULT: {len(FAILS)} clause(s) NOT satisfied")
    for f in FAILS:
        print("   -", f)
    sys.exit(1)
print("AUDIT RESULT: every clause of the objective is satisfied by artefacts on disk")
print(f"  tasks={len(ORDER)}  final PNGs={total_png}  service 200 image responses={svc}")
print(f"  dsl_versions={tm['dsl_versions_total']}  image_reviews={tm['image_reviews_total']}  "
      f"iterations={tm['iterations_total']}")
print(f"  render requests={tm['requests']['requests_total']} "
      f"(ok {tm['requests']['render_success']} / fail {tm['requests']['render_failed']})  "
      f"all HTTP={tm['requests']['grand_total_all_http']}")
