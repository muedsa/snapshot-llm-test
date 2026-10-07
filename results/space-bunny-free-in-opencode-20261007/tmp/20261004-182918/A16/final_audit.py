# -*- coding: utf-8 -*-
"""Final deliverable audit for A16 against task.json required/additional outputs."""
import json, os, re

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
OUT = os.path.join(ROOT, "outputs", "20261004-182918", "A16")
task = json.load(open(os.path.join(ROOT, "tasks", "A16-visual-data-forensics",
                                   "task.json"), encoding="utf-8"))

need = [(o["filename"], o.get("dsl"), o["width"], o["height"])
        for o in task["required_outputs"]]
extra = task["additional_outputs"] + task["common_outputs"]
ok = True
for fn, dsl, w, h in need:
    p = os.path.join(OUT, fn)
    dp = os.path.join(OUT, dsl) if dsl else None
    e1, e2 = os.path.exists(p), os.path.exists(dp) if dp else True
    ok = ok and e1 and e2
    print("%-24s exists=%s size=%s" % (fn, e1, os.path.getsize(p) if e1 else "-"))
    if dp:
        print("%-24s exists=%s size=%s" % (dsl, e2, os.path.getsize(dp) if e2 else "-"))
for fn in extra:
    p = os.path.join(OUT, fn)
    ok = ok and os.path.exists(p)
    print("%-24s exists=%s size=%s" % (fn, os.path.exists(p),
                                      os.path.getsize(p) if os.path.exists(p) else "-"))

f = json.load(open(os.path.join(OUT, "findings.json"), encoding="utf-8"))
req_keys = ["image_location", "observation", "source_data_check", "impact", "fix",
            "final_verification"]
for item in f["findings"]:
    missing = [k for k in req_keys if k not in item or not item[k]]
    if missing:
        ok = False
        print("finding %s MISSING %s" % (item.get("id"), missing))
print("findings:", len(f["findings"]), "uncertain:", len(f["uncertain_items"]),
      "all checks pass:", f["verification_summary"]["all_pass"],
      "checks:", len(f["verification_summary"]["checks"]))
print("uncertain ids:", [u["id"] for u in f["uncertain_items"]])

cd = json.load(open(os.path.join(OUT, "corrected-data.json"), encoding="utf-8"))
print("corrected-data keys:", list(cd.keys()))
print("axis:", {k: cd["axis"][k] for k in ("domain_wan", "ticks_wan", "pixels_per_wan",
                                           "baseline_y_px", "common_zero_baseline",
                                           "truncated_axis")})
print("bar_geometry entries:", len(cd["bar_geometry"]),
      "values:", [b["value"] for b in cd["bar_geometry"]])

m = json.load(open(os.path.join(OUT, "task-metrics.json"), encoding="utf-8"))
print("metrics usage:", m["usage"]["input_tokens"], m["usage"]["output_tokens"],
      m["usage"]["cost"], "| queue wait:", m["rate_limit_or_queue_wait_seconds"])
print("counts:", {k: m["counts"][k] for k in
                  ("render_requests", "successful_render_requests", "failed_render_requests",
                   "document_requests", "dsl_versions", "image_views",
                   "completed_visual_iterations", "final_pngs")})

s = open(os.path.join(OUT, "corrected-report.snapshot"), encoding="utf-8").read()
print("snapshot: Image=%s lines=%d fontSizes=%s" % ("<Image" in s, s.count("\n") + 1,
      sorted(set(re.findall(r'fontSize="([0-9.]+)"', s)), key=float)))
print("ALL REQUIRED PRESENT:", ok)