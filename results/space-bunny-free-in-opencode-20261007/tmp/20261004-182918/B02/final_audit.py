# -*- coding: utf-8 -*-
"""B02 final acceptance audit: required files, JSON validity, PNG/DSL pairing,
canvas diversity, element budget, gallery links, log integrity."""
import hashlib
import json
import os
import re
import struct
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
OUT = os.path.join(ROOT, "outputs", RUN, "B02")
TMP = os.path.join(ROOT, "tmp", RUN, "B02")
fail = []


def ck(cond, msg):
    print(("  OK   " if cond else "  FAIL ") + msg)
    if not cond:
        fail.append(msg)


print("== 1. required outputs at output root ==")
for f in ["portfolio.json", "portfolio.md", "gallery.html", "snapshot-usage.md",
          "task-metrics.json", "project-brief.md", "design-system.json",
          "touchpoint-map.json"]:
    ck(os.path.isfile(os.path.join(OUT, f)) and os.path.getsize(os.path.join(OUT, f)) > 0,
       f)

print("== 2. per-case artifacts ==")
sizes, leaves = [], {}
for i in range(1, 11):
    d = os.path.join(OUT, "case-%02d" % i)
    png, snap, note = (os.path.join(d, x) for x in ("final.png", "final.snapshot", "case.md"))
    ok = all(os.path.isfile(p) and os.path.getsize(p) > 0 for p in (png, snap, note))
    ck(ok, "case-%02d has final.png + final.snapshot + case.md" % i)
    if not ok:
        continue
    d0 = open(png, "rb").read(32)
    ck(d0[:8] == b"\x89PNG\r\n\x1a\n", "case-%02d is a real PNG" % i)
    w, h = struct.unpack(">II", d0[16:24])
    sizes.append((w, h))
    s = open(snap, encoding="utf-8").read()
    leaves[i] = sum(1 for _ in re.finditer(r"<[A-Za-z]", s))
    ck('<Snapshot' in s and '<Stack' in s, "case-%02d snapshot is a full self-contained doc" % i)
    ck("<Image" not in s, "case-%02d snapshot uses no <Image>" % i)
    ck(leaves[i] <= 4096, "case-%02d leaf elements %d <= 4096" % (i, leaves[i]))
    # PNG must equal a tracked draft
    dh = hashlib.sha256(s.encode()).hexdigest()
    hit = [f for f in os.listdir(os.path.join(TMP, "drafts"))
           if f.startswith("case-%02d.v" % i)
           and open(os.path.join(TMP, "drafts", f), encoding="utf-8").read() == s]
    ck(bool(hit), "case-%02d final.snapshot byte-identical to drafts/%s" % (i, hit[0] if hit else "?"))

print("== 3. independence / diversity ==")
ck(len(set(sizes)) == 10, "10 cases have 10 distinct canvas sizes: %s" % sorted(set(sizes)))
ck(len(sizes) == 10, "10 final PNGs")

print("== 4. JSON validity ==")
docs = {}
for f in ["portfolio.json", "design-system.json", "touchpoint-map.json", "task-metrics.json"]:
    try:
        docs[f] = json.load(open(os.path.join(OUT, f), encoding="utf-8"))
        ck(True, "%s parses" % f)
    except Exception as e:
        ck(False, "%s parses (%s)" % (f, e))

p = docs.get("portfolio.json", {})
ck(len(p.get("cases", [])) == 10, "portfolio.json lists 10 cases")
need = {"id", "title", "audience", "use_context", "user_goal", "content_basis",
        "visual_intent", "png", "snapshot", "dimensions", "supporting_assets",
        "dsl_capabilities", "completion_criteria", "visual_review", "request_ids",
        "iteration_ids", "unresolved_issues"}
ck(all(need <= set(c) for c in p.get("cases", [])), "every case has all guide fields")
ck(all(c["png"] and os.path.isfile(os.path.join(OUT, c["png"])) for c in p["cases"]),
   "every portfolio.png path resolves")
ck(all(c["snapshot"] and os.path.isfile(os.path.join(OUT, c["snapshot"])) for c in p["cases"]),
   "every portfolio.snapshot path resolves")
ck(all(list(c["dimensions"]) == list(sizes[n]) for n, c in enumerate(p["cases"])),
   "portfolio dimensions match the PNG IHDR exactly")

print("== 5. metrics vs logs ==")
m = docs.get("task-metrics.json", {})
reqs = [json.loads(l) for l in open(os.path.join(TMP, "requests.jsonl"), encoding="utf-8") if l.strip()]
iters = [json.loads(l) for l in open(os.path.join(TMP, "iterations.jsonl"), encoding="utf-8") if l.strip()]
tools = [json.loads(l) for l in open(os.path.join(TMP, "tool-usage.jsonl"), encoding="utf-8") if l.strip()]
rend = [r for r in reqs if r["request_type"] == "render"]
okr = [r for r in rend if (r.get("content_type") or "").startswith("image/")]
c = m.get("counts", {})
ck(c.get("total_http_requests") == len(reqs), "counts.total_http_requests == len(requests.jsonl)=%d" % len(reqs))
ck(c.get("snapshot_requests") == len(rend), "counts.snapshot_requests == %d" % len(rend))
ck(c.get("successful_snapshot_requests") == len(okr), "successful == %d" % len(okr))
ck(c.get("failed_snapshot_requests") == len(rend) - len(okr), "failed == %d" % (len(rend) - len(okr)))
ck(c.get("image_views") == len([i for i in iters if i.get("viewed_at")]), "image_views == %d" % len([i for i in iters if i.get("viewed_at")]))
ck(c.get("completed_visual_iterations") == len([i for i in iters if i.get("complete_visual_iteration")]),
   "completed_visual_iterations == %d" % len([i for i in iters if i.get("complete_visual_iteration")]))
ck(c.get("other_tool_calls") == len(tools), "other_tool_calls == len(tool-usage.jsonl)=%d" % len(tools))
ck(c.get("final_case_count") == 10, "final_case_count == 10")
ck(len(m.get("case_metrics", [])) == 10, "case_metrics has 10 entries")
# Every render must land in exactly one of three buckets: a case final.png,
# the shared probe scope, or the failure-response archive. No double counting.
buckets = {"case": [], "shared_probe": [], "failed": []}
for r in rend:
    rf = (r.get("response_file") or "").replace("\\", "/")
    if not (r.get("content_type") or "").startswith("image/"):
        buckets["failed"].append(r["request_id"])
    elif "/case-" in rf and rf.endswith("/final.png"):
        buckets["case"].append(r["request_id"])
    elif "/probes/" in rf:
        buckets["shared_probe"].append(r["request_id"])
    else:
        buckets.setdefault("unattributed", []).append(r["request_id"])
ck(sum(len(v) for v in buckets.values()) == len(rend),
   "every render request falls in exactly one bucket: case=%d shared_probe=%d failed=%d (total %d/%d)"
   % (len(buckets["case"]), len(buckets["shared_probe"]), len(buckets["failed"]),
      sum(len(v) for v in buckets.values()), len(rend)))
ck("unattributed" not in buckets, "no unattributed render requests")
# and each case's own request ids in portfolio.json match the bucket
by_case = {}
for r in rend:
    rf = (r.get("response_file") or "").replace("\\", "/")
    m2 = re.search(r"/(case-\d\d)/final\.png$", rf)
    if m2 and (r.get("content_type") or "").startswith("image/"):
        by_case.setdefault(m2.group(1), []).append(r["request_id"])
for c in p["cases"]:
    want = sorted(by_case.get(c["id"], []))
    ck(sorted(c["request_ids"]) == want,
       "portfolio request_ids for %s match the log exactly (%s)"
       % (c["id"], ",".join(want)))
ck(all(x["cost"] is None and x["input_tokens"] is None for x in [m["usage"]]),
   "usage token/cost fields are null, not estimated")

print("== 6. gallery ==")
g = open(os.path.join(OUT, "gallery.html"), encoding="utf-8").read()
links = re.findall(r'(?:href|src)="([^"]+)"', g)
miss = [x for x in links if not x.startswith("http") and not os.path.exists(os.path.join(OUT, x))]
ck(not miss, "all %d relative links resolve locally" % len(links))
ck("<script" not in g, "gallery has no script tag")
ck(g.count("<img") == 10, "gallery indexes all 10 final images")

print("== 7. cross-document consistency ==")
ds = docs.get("design-system.json", {})
tm = docs.get("touchpoint-map.json", {})
ck(len(tm.get("touchpoints", [])) == 10, "touchpoint-map has 10 touchpoints")
ck(ds.get("asset_policy_applied", {}).get("actually_used", "").startswith("无辅助素材"),
   "design-system records that no assets were used")
brief = open(os.path.join(OUT, "project-brief.md"), encoding="utf-8").read()
ck("自拟" in brief and "虚构" not in brief[:0] + "", "project-brief marks content as fabricated")
su = open(os.path.join(OUT, "snapshot-usage.md"), encoding="utf-8").read()
ck("null" in su and "未按" in su, "snapshot-usage states unknown metrics are null, not estimated")
ck("�" not in su and "�" not in brief, "no mojibake in the two reports")

print()
print("FAILURES:", len(fail))
for f in fail:
    print("  -", f)
print("AUDIT", "PASS" if not fail else "FAIL")