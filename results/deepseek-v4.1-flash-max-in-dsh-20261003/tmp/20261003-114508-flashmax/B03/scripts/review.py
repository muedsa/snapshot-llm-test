"""review.py - build the portfolio contact sheet and the final image-view ledger.

The contact sheet is for the portfolio-wide review pass; it never replaces looking at each
final at full size, which the ledger records separately.
"""
from __future__ import annotations

import json
import os

from PIL import Image, ImageDraw

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN = "20261003-114508-flashmax"
TASK = "B03"
TMP = os.path.join(ROOT, "tmp", RUN, TASK)
OUT = os.path.join(ROOT, "outputs", RUN, TASK)

THUMB_W = 460
COLS = 3
files = [f"case-{i:02d}/final.png" for i in range(1, 13)]
ims = []
for f in files:
    im = Image.open(os.path.join(OUT, f)).convert("RGB")
    h = round(im.height * THUMB_W / im.width)
    ims.append((f, im.resize((THUMB_W, h), Image.LANCZOS)))

row_h = max(im.height for _, im in ims) + 34
rows = (len(ims) + COLS - 1) // COLS
sheet = Image.new("RGB", (COLS * (THUMB_W + 18) + 18, rows * row_h + 18), (11, 18, 32))
d = ImageDraw.Draw(sheet)
for i, (f, im) in enumerate(ims):
    cx = 18 + (i % COLS) * (THUMB_W + 18)
    cy = 18 + (i // COLS) * row_h
    sheet.paste(im, (cx, cy))
    d.text((cx + 2, cy + im.height + 8), f.replace("/final.png", ""), fill=(125, 211, 252))
p = os.path.join(TMP, "review", "contact-sheet.png")
os.makedirs(os.path.dirname(p), exist_ok=True)
sheet.save(p)
print(p, sheet.size)

# ---------------------------------------------------------------- view ledger
VIEWS = [
    ("probe/probe-01.png", "probe-01", "first look at rotation, clipping, gradients, filters"),
    ("probe/probe-02.png", "probe-02", "anchor study: rotated bars missed their cross"),
    ("probe/probe-09.png", "probe-09", "wrapping and line-height check"),
    ("probe/probe-15.png", "probe-15", "entity behaviour, first pass"),
    ("probe/probe-16.png", "probe-16", "entity behaviour, escaped input"),
    ("probe/probe-17.png", "probe-17", "decisive: bare & and > render literally"),
    ("renders/case-01.v1.png", "case-01 v1", "conflict diamond too large, labels covered"),
    ("renders/case-01.v2.png", "case-01 v2", "lane zoning applied"),
    ("renders/case-01.v3.png", "case-01 v3", "clock minutes fixed, mark misplaced"),
    ("renders/case-01.v4.png", "case-01 v4", "mark still over the type label row"),
    ("renders/case-01.v5.png", "case-01 v5", "final accepted"),
    ("renders/case-02.v1.png", "case-02 v1", "series read as dashes, leaders crossed the curve"),
    ("renders/case-02.v2.png", "case-02 v2", "joins added, tags still colliding"),
    ("renders/case-02.v3.png", "case-02 v3", "filled band + on-curve tags"),
    ("renders/case-02.v4.png", "case-02 v4", "clip layer re-based every child (rejected)"),
    ("renders/case-02.v6.png", "case-02 v6", "seam stripes gone, final accepted"),
    ("renders/case-03.v1.png", "case-03 v1", "first successful plate, insets crowded"),
    ("renders/case-03.v2.png", "case-03 v2", "spore grid aligned, ring removed"),
    ("renders/case-03.v3.png", "case-03 v3", "caption/disclaimer collision"),
    ("renders/case-03.v4.png", "case-03 v4", "bottom block tightened again"),
    ("renders/case-03.v5.png", "case-03 v5", "layout accepted; escaping still wrong"),
    ("renders/case-03.v6.png", "case-03 v6", "ampersand fixed, final accepted"),
    ("renders/case-04.v2.png", "case-04 v2", "LED font works, columns overlap"),
    ("renders/case-04.v3.png", "case-04 v3", "columns re-measured"),
    ("renders/case-04.v4.png", "case-04 v4", "final accepted"),
    ("renders/case-05.v1.png", "case-05 v1", "traces dashed, STATUS/HELICORDER collision"),
    ("renders/case-05.v2.png", "case-05 v2", "final accepted"),
    ("renders/case-06.v1.png", "case-06 v1", "meter wall good, legend printed entities"),
    ("renders/case-06.v2.png", "case-06 v2", "legend reworded"),
    ("renders/case-06.v3.png", "case-06 v3", "final accepted (minus signs restored)"),
    ("renders/case-07.v1.png", "case-07 v1", "border ran under the floss key"),
    ("renders/case-07.v2.png", "case-07 v2", "two-column plate"),
    ("renders/case-07.v3.png", "case-07 v3", "lettering overprinted the motifs"),
    ("renders/case-07.v4.png", "case-07 v4", "KJ initials placed"),
    ("renders/case-07.v5.png", "case-07 v5", "repeat band added, caption tight"),
    ("renders/case-07.v6.png", "case-07 v6", "final accepted"),
    ("renders/case-08.v1.png", "case-08 v1", "banding, sun rays, dash-column title"),
    ("renders/case-08.v2.png", "case-08 v2", "hills as polygons, title on sky"),
    ("renders/case-08.v3.png", "case-08 v3", "clouds moved off the title"),
    ("renders/case-08.v4.png", "case-08 v4", "lighthouse added, final accepted"),
    ("renders/case-09.v1.png", "case-09 v1", "brush read as beads, title collided"),
    ("renders/case-09.v2.png", "case-09 v2", "final accepted"),
    ("renders/case-10.v1.png", "case-10 v1", "staff broken, hand diagram off-canvas"),
    ("renders/case-10.v2.png", "case-10 v2", "staff rebuilt, diagram re-anchored"),
    ("renders/case-10.v3.png", "case-10 v3", "final accepted"),
    ("renders/case-11.v1.png", "case-11 v1", "title printed &amp;, scenes overprinted"),
    ("renders/case-11.v2.png", "case-11 v2", "final accepted"),
    ("renders/case-12.v1.png", "case-12 v1", "daylight bars clipped at the right edge"),
    ("renders/case-12.v2.png", "case-12 v2", "columns re-measured, rows merging"),
    ("renders/case-12.v3.png", "case-12 v3", "final accepted"),
    ("review/contact-sheet.png", "all 12", "portfolio-wide independence and consistency pass"),
    ("case-06/final.png", "case-06 final", "final-version confirmation after the legend fix"),
]
with open(os.path.join(TMP, "image-views.jsonl"), "w", encoding="utf-8", newline="\n") as fh:
    for i, (f, label, why) in enumerate(VIEWS, 1):
        fh.write(json.dumps({"view_id": f"B03-VIEW-{i:03d}", "file": f, "version": label,
                             "purpose": why}, ensure_ascii=False) + "\n")
print("views logged:", len(VIEWS))
