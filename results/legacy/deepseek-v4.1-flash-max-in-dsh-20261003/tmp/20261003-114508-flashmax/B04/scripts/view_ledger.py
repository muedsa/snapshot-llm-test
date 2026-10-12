"""view_ledger.py - write B03's image-view ledger from the exact list of images opened.

One record per `read_image` call actually made during the task, each stamped with the
ended_at of the request that produced that file (requests.jsonl). Images that were only
measured numerically with PIL are deliberately NOT listed as views.
"""
from __future__ import annotations

import json
import os
import re

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN = "20261003-114508-flashmax"
TMP3 = os.path.join(ROOT, "tmp", RUN, "B03")

VIEWED = [
    ("tmp/20261003-114508-flashmax/B03/probe/probe-01.png", "probe-01",
     "first look: rotation, clipping, gradients, filters"),
    ("tmp/20261003-114508-flashmax/B03/probe/probe-02.png", "probe-02",
     "anchor study: rotated bars missed their cross"),
    ("tmp/20261003-114508-flashmax/B03/probe/probe-09.png", "probe-09",
     "wrapping and line-height check"),
    ("tmp/20261003-114508-flashmax/B03/probe/probe-15.png", "probe-15",
     "entity behaviour, first pass"),
    ("tmp/20261003-114508-flashmax/B03/probe/probe-16.png", "probe-16",
     "entity behaviour with escaped input"),
    ("tmp/20261003-114508-flashmax/B03/probe/probe-17.png", "probe-17",
     "decisive: bare & and > render literally"),
    *[(f"tmp/20261003-114508-flashmax/B03/renders/case-01.{v}.png", f"case-01 {v}", d)
      for v, d in [("v1", "conflict diamond too large, band labels covered"),
                   ("v2", "lane zoning applied"),
                   ("v3", "clock minutes fixed; mark misplaced"),
                   ("v4", "mark still over the type label row"),
                   ("v5", "final accepted")]],
    *[(f"tmp/20261003-114508-flashmax/B03/renders/case-02.{v}.png", f"case-02 {v}", d)
      for v, d in [("v1", "series read as dashes; leaders crossed the curve"),
                   ("v2", "joins added; tags still colliding"),
                   ("v3", "filled band + on-curve tags"),
                   ("v4", "clip layer re-based every child (rejected)"),
                   ("v6", "seam stripes gone; final accepted")]],
    *[(f"tmp/20261003-114508-flashmax/B03/renders/case-03.{v}.png", f"case-03 {v}", d)
      for v, d in [("v1", "first successful plate; insets crowded"),
                   ("v2", "spore grid aligned; ring removed"),
                   ("v3", "caption/disclaimer collision"),
                   ("v4", "bottom block tightened again"),
                   ("v5", "layout accepted; escaping still wrong"),
                   ("v6", "ampersand fixed; final accepted")]],
    *[(f"tmp/20261003-114508-flashmax/B03/renders/case-04.{v}.png", f"case-04 {v}", d)
      for v, d in [("v2", "LED font works; columns overlap"),
                   ("v3", "columns re-measured"),
                   ("v4", "final accepted")]],
    *[(f"tmp/20261003-114508-flashmax/B03/renders/case-05.{v}.png", f"case-05 {v}", d)
      for v, d in [("v1", "traces dashed; STATUS/HELICORDER collision"),
                   ("v2", "final accepted")]],
    *[(f"tmp/20261003-114508-flashmax/B03/renders/case-06.{v}.png", f"case-06 {v}", d)
      for v, d in [("v1", "meter wall good; legend printed entities"),
                   ("v2", "legend reworded"),
                   ("v3", "final accepted (minus signs restored)")]],
    *[(f"tmp/20261003-114508-flashmax/B03/renders/case-07.{v}.png", f"case-07 {v}", d)
      for v, d in [("v1", "border ran under the floss key"),
                   ("v2", "two-column plate"),
                   ("v3", "lettering overprinted the motifs"),
                   ("v4", "KJ initials placed"),
                   ("v5", "repeat band added; caption tight"),
                   ("v6", "final accepted")]],
    *[(f"tmp/20261003-114508-flashmax/B03/renders/case-08.{v}.png", f"case-08 {v}", d)
      for v, d in [("v1", "banding, sun rays, dash-column title"),
                   ("v2", "hills as polygons; title on sky"),
                   ("v3", "clouds moved off the title"),
                   ("v4", "lighthouse added; final accepted")]],
    *[(f"tmp/20261003-114508-flashmax/B03/renders/case-09.{v}.png", f"case-09 {v}", d)
      for v, d in [("v1", "brush read as beads; title collided"),
                   ("v2", "final accepted")]],
    *[(f"tmp/20261003-114508-flashmax/B03/renders/case-10.{v}.png", f"case-10 {v}", d)
      for v, d in [("v1", "staff broken; hand diagram off-canvas"),
                   ("v2", "staff rebuilt; diagram re-anchored"),
                   ("v3", "final accepted")]],
    *[(f"tmp/20261003-114508-flashmax/B03/renders/case-11.{v}.png", f"case-11 {v}", d)
      for v, d in [("v1", "title printed &amp;; scenes overprinted"),
                   ("v2", "final accepted")]],
    *[(f"tmp/20261003-114508-flashmax/B03/renders/case-12.{v}.png", f"case-12 {v}", d)
      for v, d in [("v1", "daylight bars clipped at the right edge"),
                   ("v2", "columns re-measured; rows merging"),
                   ("v3", "final accepted")]],
    ("tmp/20261003-114508-flashmax/B03/review/contact-sheet.png", "all 12",
     "portfolio-wide independence and consistency pass"),
    ("outputs/20261003-114508-flashmax/B03/case-06/final.png", "case-06 final",
     "final-version confirmation after the legend fix"),
]

recs = [json.loads(l) for l in open(os.path.join(TMP3, "requests.jsonl"),
                                    encoding="utf-8-sig") if l.strip()]
by_file = {}
for r in recs:
    rf = (r.get("request_file") or "").replace("\\", "/")
    if r["success"]:
        by_file[rf] = r["ended_at"]
# a render wrote <out>.png from <dsl>.snapshot; map dsl -> the png it produced
dsl_to_png = {}
for r in recs:
    rf = (r.get("request_file") or "").replace("\\", "/")
    rp = (r.get("response_file") or "").replace("\\", "/")
    if r["success"] and rp:
        dsl_to_png[rf] = rp
png_time = {}
for rf, rp in dsl_to_png.items():
    t = next((r["ended_at"] for r in recs if r["success"]
              and (r.get("response_file") or "").replace("\\", "/") == rp), None)
    png_time[rp] = t

out = []
for i, (path, label, why) in enumerate(VIEWED, 1):
    key = path
    t = png_time.get(key)
    rec = {"view_id": f"B03-VIEW-{i:03d}", "file": path, "version": label, "purpose": why,
           "viewed_at": t,
           "basis": "render ended_at from requests.jsonl" if t else
                    "no logged render (local composite)"}
    out.append(rec)
open(os.path.join(TMP3, "image-views.jsonl"), "w", encoding="utf-8", newline="\n").write(
    "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in out))
print("views:", len(out), "with logged render time:",
      sum(1 for r in out if r["viewed_at"]))
mp = os.path.join(ROOT, "outputs", RUN, "B03", "task-metrics.json")
m = json.load(open(mp, encoding="utf-8"))
m["image_views"] = len(out)
m["image_views_ledger"] = "tmp/%s/B03/image-views.jsonl" % RUN
m["image_views_note"] = ("One record per read_image call actually made. Probe images that "
                         "were only measured with PIL are not counted as views.")
json.dump(m, open(mp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("metrics image_views =", m["image_views"])
