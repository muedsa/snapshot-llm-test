# -*- coding: utf-8 -*-
"""Record case-01's real visual iterations, in the order they happened."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run  # noqa: E402

D = os.path.join(run.TMP, "drafts")
P = os.path.join(run.TMP, "preview")
O = os.path.join(run.OUT, "case-01")
V = "2026-10-05T%s+08:00"

REC = [
    ("v01", "none", "baseline", "case-01-v001.snapshot", "preview/case-01.png",
     "01:58",
     "no image at all: 400 PARSE_ERROR at position 59282 - the error text showed a "
     "single tag name split one character per line, i.e. a string had been spliced "
     "into the child list. Cause: `kids += A.seg(...)` on a helper that returns ONE "
     "string instead of a list, so the string's characters became child nodes",
     "changed that one call to kids.append(); added A.flat() so cases can mix "
     "append and += freely", False),
    ("v02", "v01", "baseline", "case-01-v002.snapshot", "preview/case-01.png",
     "02:01",
     "first real image (1178 elements, 0 warnings). Defects: the header title was "
     "overlapped by the status pills; the load area fill was a terraced staircase "
     "because dsllib.polygon draws 72 overlapping scanlines with translucent "
     "colour; the chart footnote sat on the 00:30 axis label; and all five intertie "
     "rows fell outside the right panel below its bottom edge",
     "re-laid the header, the panel heights and the right column; wrote A.area() "
     "(abutting 3px columns) and A.band() to replace polygon fills", False),
    ("v03", "v02", "visual", "case-01-v003.snapshot", "preview/case-01.png",
     "02:05",
     "area fill is now smooth and the panels fit, but the forecast envelope still "
     "showed a ladder of darker ~45px blocks: those were the 24 hourly ribbon cells "
     "with a +1px overlap, each painted twice. A 1.4x crop of the plot confirmed the "
     "blocks sat between the upper and lower envelope edges",
     "removed the +1px overlap and added a dashed 'yesterday same-time' reference "
     "line so the left half of the plot carries information too", False),
    ("v04", "v03", "visual", "case-01-v001.snapshot", "preview/case-01.png",
     "02:08",
     "1.4x crop showed the envelope was STILL blocky - the abutting-hourly fix was "
     "not enough because each cell's top and bottom edge is a horizontal line, so the "
     "ribbon boundary is a 45px staircase no matter how the cells abut. Replaced with "
     "A.band(), which tracks both edges per column",
     "wrote A.band(upper, lower, ...) and rebuilt the envelope with it; reordered "
     "so the cyan measured fill is drawn first and the ribbon sits on top", False),
    ("v05", "v04", "visual", "case-01-final-v001.snapshot", "case-01/final.png",
     "02:11",
     "ribbon and area are both smooth now (verified on the full 1920x1080 image and "
     "on a 1.0x crop of the plot). One collision left: the peak callout "
     "'18:30 68.0 GW' ran straight through the three legend pills at the top of the "
     "panel",
     "moved the legend to the panel's bottom-right corner, right-aligned, leaving "
     "the plot's upper band free for the callout", False),
    ("v06", "v05", "visual", "case-01-final-v002.snapshot", "case-01/final.png",
     "02:14",
     "1.0x crop of the delivered chart: callout, leader line, legend, axis labels, "
     "event flags, peak marker and the footnote are all separated and fully legible; "
     "0 warnings, 2282 elements, PNG bytes are the raw service response and the "
     "delivered .snapshot is the DSL that produced them",
     "accepted", True),
]

run.note("case-01", "B01-v04b", "B01-v03", "trace-fix",
         os.path.join(D, "case-01-v001.snapshot"),
         os.path.join(run.TMP, "preview/case-01.png"), V % "02:09",
         "found a trace-keeping defect of my own: run.next_draft() sliced the draft "
         "name at len(prefix)+1 instead of len(prefix), so '.isdigit()' never matched "
         "and every preview render overwrote case-01-v001.snapshot. The archived v001 "
         "draft is therefore the LAST intermediate DSL, not the first one",
         "fixed the index; from here on every version keeps its own archive file",
         False)

for v, parent, kind, dsl, img, hh, obs, chg, ok in REC:
    run.note("case-01", "B01-" + v,
             parent if parent == "none" else "B01-" + parent,
             kind, os.path.join(D, dsl), os.path.join(run.TMP, img),
             V % hh, obs, chg, ok)
run.note("case-01", "B01-final-render", "B01-v05", "delivery",
         os.path.join(O, "final.snapshot"), os.path.join(O, "final.png"),
         V % "02:14",
         "final delivery render into outputs/20261004-182918/B01/case-01/ - "
         "1920x1080, 2282 elements, 0 warnings",
         "no further change after v05", True)
print("case-01 notes:", len(run.notes()))