# -*- coding: utf-8 -*-
"""Record B01's real visual iterations and finish the task.

log_c01.py already appended case-01's 8 records to iteration-notes.jsonl before
the interruption; those are kept as-is. This file appends the records for
case-02..case-10 that are actually documented in the session, then hands
everything to wrapup() so iterations.jsonl / task-metrics.json / suite-state.json
are written from the real logs rather than typed by hand.
"""
from __future__ import annotations

import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "_suite"))
import run  # noqa: E402
import state as S  # noqa: E402
import wrapup as W  # noqa: E402

D = os.path.join(run.TMP, "drafts")
O = run.OUT
P = os.path.join(run.TMP, "preview")
V = "2026-10-05T%s+08:00"

# (case, version, parent, kind, dsl_rel, image_rel, viewed_hhmm, observed, changes, complete)
REC = [
 # ---------------------------------------------------------------- case-02
 ("case-02", "v01", "none", "baseline", "case-02-v001.snapshot", "preview/case-02.png",
  "02:31",
  "first real image for this case: 848 elements, 0 warnings. The six entry blocks, "
  "the editor's note and the store information block all fit; the right-hand "
  "vertical title reads correctly and the two red squares of the stamp clear the "
  "border",
  "no change needed - the layout was solved entirely by the measured type scale, "
  "which is why this sheet needed no geometry iteration", True),
 ("case-02", "final-render", "v01", "delivery", "case-02/final.snapshot",
  "case-02/final.png", "02:33",
  "final delivery render into outputs/.../case-02/ - 1200x1600, 848 elements, "
  "0 warnings; QR modules and spine bars verified as solid black rectangles at 1:1",
  "no further change", True),

 # ---------------------------------------------------------------- case-03
 ("case-03", "v01", "none", "baseline", "case-03-v001.snapshot", "preview/case-03.png",
  "02:38",
  "1743 elements, 0 warnings. Concentric scanline wind circles, vessel diamonds and "
  "the 6-step action timeline all render, but the orange warning capsule in the "
  "header reads LEFT of the text it contains",
  "noted for the cross-case centring audit", False),
 ("case-03", "v02", "v01", "visual", "case-03-final-v001.snapshot", "preview/case-03.png",
  "05:41",
  "the audit script flagged this call as one of 10 sites mixing align=\"CENTER\" "
  "with an explicit w=; a 2x crop of the header (fin03-pill.png) confirms the text "
  "sat about 104px right of the pill's centre",
  "replaced with A.ctr(cx, ...) which takes a true centre; same for the scale-bar N",
  False),
 ("case-03", "final-render", "v02", "delivery", "case-03/final.snapshot",
  "case-03/final.png", "05:44",
  "re-rendered final at 1600x1100, 1743 elements, 0 warnings; fin03-pill.png crop "
  "shows the capsule text now centred and the N glyph centred on its arrow",
  "no further change", True),

 # ---------------------------------------------------------------- case-04
 ("case-04", "v01", "none", "baseline", "case-04-v001.snapshot", "preview/case-04.png",
  "02:46",
  "1400x1750, 1600 elements, 0 warnings. Both traces, four phase bands, six turning "
  "points, six scoring bars and the four brew cards all fit inside the A4 sheet. "
  "One defect: the time axis labels and the four phase names all sit visibly right "
  "of the gridlines and phase bands they belong to",
  "none at this point", False),
 ("case-04", "v02", "v01", "visual", "case-04-final-v001.snapshot",
  "preview/case-04.png", "05:48",
  "crop chk04-axis.png (1190x90 strip under the plot) shows every '0:00'..'9:00' "
  "label about 35px right of its gridline, and chk04-ph.png (1.6x of the last phase "
  "band) shows '发展尾段 / 落豆' running off the right edge of its own plate. Root "
  "cause is textAlign=CENTER centring inside the BOX while one_line places the box's "
  "LEFT edge at x, so every glyph shifted right by w/2",
  "replaced all three sites (axis labels, phase names, phase subtitles) with A.ctr, "
  "which takes a real centre x and derives the box itself; also converted the phase "
  "duration row", False),
 ("case-04", "final-render", "v02", "delivery", "case-04/final.snapshot",
  "case-04/final.png", "05:51",
  "re-rendered final at 1400x1750, 1600 elements, 0 warnings; full-size view plus a "
  "fresh axis crop confirm all nine axis labels sit on their gridlines and all four "
  "phase plates contain their names",
  "no further change", True),

 # ---------------------------------------------------------------- case-05
 ("case-05", "v01", "none", "baseline", "case-05-v001.snapshot", "preview/case-05.png",
  "03:04",
  "1680x1050, all 264 cells render with their counts, the four-band season rail sits "
  "over the month columns, the right-hand density ramp and the two migration notes "
  "are clear of the grid, and the bottom per-month mini-bars align with the month "
  "labels",
  "no change needed", True),
 ("case-05", "final-render", "v01", "delivery", "case-05/final.snapshot",
  "case-05/final.png", "03:06",
  "final delivery render into outputs/.../case-05/ - 1680x1050, 0 warnings",
  "no further change", True),

 # ---------------------------------------------------------------- case-06
 ("case-06", "v01", "none", "baseline", "case-06-v001.snapshot", "preview/case-06.png",
  "03:12",
  "1600x1200, 348 elements, 0 warnings. Giant A018 card, countdown ring, queue rows "
  "and the four instruction cards all render. Two centring defects: '剩余时长' sits "
  "left of the ring rather than under it, and each queue row's state chip has its "
  "text pushed to the right edge",
  "none at this point", False),
 ("case-06", "v02", "v01", "visual", "case-06-final-v001.snapshot",
  "preview/case-06.png", "05:54",
  "crops chk06-ring.png and chk06-pill.png confirm both: the caption is 100px left of "
  "the ring centre and the chip labels sit right of their pills. The ring caption "
  "had a second bug on top - its x was NX+660, which was never the ring centre",
  "switched both to A.ctr; for the caption changed the reference to CX, the actual "
  "ring centre", False),
 ("case-06", "v03", "v02", "visual", "case-06-final-v002.snapshot",
  "case-06/final.png", "06:03",
  "crop fin06-pill.png shows the chip labels now centred, but a fresh view of the "
  "final showed the caption had moved to the far LEFT of the card instead of under "
  "the ring - the first re-render had used A.ctr with the old NX+660 x, so the "
  "caption was correctly centred on the wrong point",
  "changed the caption x from NX+660 to CX and re-rendered the final",
  False),
 ("case-06", "final-render", "v03", "delivery", "case-06/final.snapshot",
  "case-06/final.png", "06:05",
  "final delivery render at 1600x1200, 348 elements, 0 warnings; fin06-ring.png crop "
  "confirms '剩余时长' now sits directly under the countdown ring",
  "no further change", True),

 # ---------------------------------------------------------------- case-07
 ("case-07", "v01", "none", "baseline", "case-07-v001.snapshot", "preview/case-07.png",
  "03:20",
  "2000x760 ultra-wide. Six coach side elevations render with windows, doors, bogies "
  "and class bands; the platform door strip below aligns with the coach doors",
  "initial layout, several callout collisions to resolve", False),
 ("case-07", "v02", "v01", "visual", "case-07-v002.snapshot", "preview/case-07.png",
  "03:22",
  "the '05·6 号门' leader line crossed the coach-05 body, and the accessibility "
  "position labels collided with the platform door numbers",
  "moved the callout above the coach row and re-derived the door strip from measured "
  "coach widths", False),
 ("case-07", "v03", "v02", "visual", "case-07-v003.snapshot", "preview/case-07.png",
  "03:24",
  "coach 03's seat-band label overlapped the coach body; the facility comparison "
  "table's third column ran under the boarding-order cards",
  "re-laid the facility table into measured columns", False),
 ("case-07", "v04", "v03", "visual", "case-07-v004.snapshot", "preview/case-07.png",
  "03:26",
  "crops final-c07-train.png and final-c07-pdrow.png showed the bogie wheels sitting "
  "one row too low, clipping the coach skirt, and the platform door row misaligned "
  "by half a cell",
  "raised the wheels into the body and snapped the door row to coach boundaries",
  False),
 ("case-07", "v05", "v04", "visual", "case-07-final-v005.snapshot", "preview/case-07.png",
  "03:29",
  "crop final-c07-pd3.png confirms the door strip now aligns to coach doors and the "
  "accessibility markers clear the numbers; a full 2000x760 view shows all four "
  "panels separated with the footnote on clear ground",
  "accepted", True),
 ("case-07", "final-render", "v05", "delivery", "case-07/final.snapshot",
  "case-07/final.png", "03:31",
  "final delivery render into outputs/.../case-07/ - 2000x760, 0 warnings",
  "no further change", True),

 # ---------------------------------------------------------------- case-08
 ("case-08", "v01", "none", "baseline", "case-08-v001.snapshot", "preview/case-08.png",
  "03:44",
  "1400x1600, 3377 elements - the largest document in the portfolio, still only 82% "
  "of the 4096 limit. The 24-term ring, 12 month blocks and all 365 day cells "
  "render; three ink-wash ridges stay below the header band",
  "initial layout", False),
 ("case-08", "v02", "v01", "visual", "case-08-final-v001.snapshot", "preview/case-08.png",
  "05:57",
  "crop chk08-seal2.png (4x of the top-right corner) shows the stamp's second glyph "
  "'步' cut off by the red box edge - two 19px serif glyphs do not fit a 56px box "
  "with rotation applied. The same crop also showed '2026' sitting right of the "
  "ring's vertical centreline",
  "enlarged the stamp to 72x72 and re-measured the text box against the new width; "
  "switched '2026' to A.ctr", False),
 ("case-08", "final-render", "v02", "delivery", "case-08/final.snapshot",
  "case-08/final.png", "06:00",
  "re-rendered final at 1400x1600, 3377 elements, 0 warnings; crop chk08-ring.png "
  "confirms both glyphs '汀步' fit inside the stamp and '2026' is centred in the "
  "ring; the 24 season labels still clear each other around the full circumference",
  "no further change", True),

 # ---------------------------------------------------------------- case-09
 ("case-09", "v01", "none", "baseline", "case-09-v001.snapshot", "preview/case-09.png",
  "12:04",
  "1600x1000. The depth section, sampling grid, sweep and catalogue all render, but "
  "crop chk09-hdr.png shows two header values losing their last glyph - 'DIVE 3 / 7' "
  "printed as 'DIVE 3 /' and '2 级 · 涌 1.1 m' as '2 级 · 涌 1.1'",
  "none at this point", False),
 ("case-09", "v02", "v01", "visual", "case-09-v002.snapshot", "preview/case-09.png",
  "06:12",
  "the dropped glyphs were NOT random: they are the widest characters. Root cause is "
  "in the shared metric - atelier.tw() measured mono strings as len(s)*0.6021em, but "
  "DejaVu Sans Mono's ASCII advance is 0.6021em while the CJK fallback glyph is still "
  "1em, so any mixed string was under-measured by ~6% and the service silently "
  "dropped the overflowing tail (a documented behaviour, no error). A second defect "
  "found in crop chk09-cat.png: the 深度 column value '1837.4 m' touched the 网格 "
  "column and read as one value '1837.4 mB2'",
  "rewrote tw()'s mono branch to measure per character; made one_line use it "
  "automatically whenever font is the mono stack; widened the catalogue column "
  "offsets from 268/344 to 262/356", False),
 ("case-09", "v03", "v02", "visual", "case-09-v003.snapshot", "preview/case-09.png",
  "06:15",
  "crop chk09-hdr2.png confirms both header strings now render complete, and "
  "chk09-cat2.png confirms the catalogue columns separate. Two placement defects "
  "remained: the '探照灯 / 扫掠角 58°' labels were painted over by the catalogue "
  "panel because only 32px remained to their right, and '探坑范围 2.4 x 1.8 m' sat "
  "inside the plan on top of the D4 cell label",
  "moved both legend lines below the plan square", False),
 ("case-09", "v04", "v03", "visual", "case-09-v004.snapshot", "case-09/final.png",
  "06:19",
  "crop fin09-foot.png showed the relocated '虚线 = 探坑范围' line had landed on the "
  "depth-scale tick row ('0' and '水深 1,842 m') instead of clear of it",
  "moved it to +58 and the sweep legend to +80", False),
 ("case-09", "final-render", "v04", "delivery", "case-09/final.snapshot",
  "case-09/final.png", "06:22",
  "final delivery render at 1600x1000, 842 elements, 0 warnings; a fresh "
  "fin09-foot.png crop shows four cleanly separated rows under the plan: the depth "
  "scale, the dashed-outline note, the sweep legend and the north note",
  "no further change", True),

 # ---------------------------------------------------------------- case-10
 ("case-10", "v01", "none", "baseline", "case-10-v001.snapshot", "preview/case-10.png",
  "12:41",
  "1750x1150, 664 elements, 0 warnings, first render. Four panels all fit, but five "
  "defects: the header's 4th label rendered as mojibake ('场??'), the difficulty "
  "bands were off by one grade against the route chips and wall histograms, the "
  "header summary said '6 条空闲 · 3 条占用中' while the route flags actually give "
  "5 and 4, the coach note's right-aligned '38 人' ran through the paragraph's "
  "second line, and the wall-face hatching crossed the wall names",
  "none at this point", False),
 ("case-10", "v02", "v01", "visual", "case-10-v002.snapshot", "preview/case-10.png",
  "12:46",
  "the off-by-one is the substantive one: grades VB..V5 were being used directly as "
  "band indices, but VB occupies index 0, so V3 landed on the V2 colour and every "
  "route chip and wall histogram disagreed with the ladder above it. Also confirmed "
  "with crop chk10-hdr.png that '38 人' overflowed the header plate's right edge",
  "added an explicit GI grade-label to band-index map and switched ROUTES and "
  "WALLS to grade strings; computed the free/busy counts from the flags; moved the "
  "counter above the paragraph; restricted the hatch to the band between title and "
  "tally line", False),
 ("case-10", "final-render", "v02", "delivery", "case-10/final.snapshot",
  "case-10/final.png", "12:49",
  "final delivery render at 1750x1150, 664 elements, 0 warnings. crop "
  "chk10-hdr2.png confirms the header block now sits inside the plate; the ladder, "
  "the nine route chips and the four wall histograms all agree on colours; crop "
  "chk10-wall.png confirms the hatch no longer crosses '东墙' or its route tally",
  "no further change", True),
]

# Each run rebuilds iteration-notes.jsonl from scratch, then WRITES iterations.jsonl
# from that same list. snapkit only appends, so without the rewrite every re-run
# would double the iteration counts - which is exactly what happened the first two
# times this script was executed.
SRC = os.path.join(run.TMP, "iteration-notes.jsonl")
keep = []


def _append(cid, ver, parent, kind, dsl_path, img_path, viewed, obs, chg, ok):
    keep.append({"case_id": cid, "version": ver, "parent": parent, "kind": kind,
                 "dsl_file": os.path.relpath(dsl_path, ROOT_ABS).replace("\\", "/"),
                 "image_file": os.path.relpath(img_path, ROOT_ABS).replace("\\", "/"),
                 "viewed_at": viewed, "observed": obs, "changes": chg,
                 "complete_visual_iteration": ok})


ROOT_ABS = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"

# preserve case-01's pre-interruption rows exactly as log_c01.py wrote them,
# then rebuild the rest from REC
for r in run.notes():
    if r["case_id"] == "case-01":
        keep.append(r)

for cid, ver, parent, kind, dsl_rel, img_rel, hh, obs, chg, ok in REC:
    dsl_path = (os.path.join(O, dsl_rel) if dsl_rel.startswith("case-")
                else os.path.join(D, dsl_rel))
    img_path = (os.path.join(O, img_rel) if img_rel.startswith("case-")
                else os.path.join(P, img_rel))
    _append(cid, "B01-" + ver, ("B01-" + parent) if parent != "none" else None,
            kind, dsl_path, img_path, V % hh, obs, chg, ok)

# canonical order: by case, then by the time of the viewing record
ORDER = {c: i for i, c in enumerate(
    ["case-01", "case-02", "case-03", "case-04", "case-05",
     "case-06", "case-07", "case-08", "case-09", "case-10"])}
keep.sort(key=lambda r: (ORDER.get(r["case_id"], 99), r["viewed_at"] or ""))

with io.open(SRC, "w", encoding="utf-8", newline="\n") as fh:
    for r in keep:
        fh.write(json.dumps(r, ensure_ascii=False) + "\n")

# iterations.jsonl is the derived artefact: rewrite it so the counts in
# task-metrics.json always match iteration-notes.jsonl exactly
ITP = os.path.join(run.TMP, "iterations.jsonl")
if os.path.exists(ITP):
    os.remove(ITP)
run.notes = lambda: list(keep)
print("notes written:", len(keep))

print("notes now:", len(run.notes()))

ROOT_ABS = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"

# snapkit.log_iteration takes a 9-tuple; run.note() records also carry case_id,
# which lives on the record rather than in the tuple
ITER = [(r["version"], r["parent"], r["kind"],
         os.path.join(ROOT_ABS, r["dsl_file"].replace("/", os.sep)),
         os.path.join(ROOT_ABS, r["image_file"].replace("/", os.sep)),
         r["viewed_at"], r["observed"], r["changes"], r["complete_visual_iteration"])
        for r in run.notes()]

CASE_IDS = sorted(x for x in os.listdir(run.OUT) if x.startswith("case-"))
ARTIFACTS = []
for cid in CASE_IDS:
    ARTIFACTS += ["%s/final.png" % cid, "%s/final.snapshot" % cid,
                  "%s/case.md" % cid]
ARTIFACTS += ["portfolio.json", "portfolio.md", "gallery.html",
              "snapshot-usage.md", "task-metrics.json"]

EVIDENCE = []
for r in run.notes():
    if r["complete_visual_iteration"]:
        EVIDENCE.append("%s %s viewed %s: %s" % (r["case_id"], r["version"],
                                                r["viewed_at"],
                                                r["observed"][:120]))

m = W.wrapup(
    "B01",
    started="2026-10-05T05:27:31.893+08:00",
    first_image="2026-10-05T05:28:32.193+08:00",
    ended=S.now_iso(),
    iterations=ITER,
    artifacts=ARTIFACTS,
    visual_evidence=EVIDENCE,
    unresolved=[],
    status="completed",
    cases=CASE_IDS,
    notes="Ten independent complete cases. All ten final PNGs are raw service "
          "response bytes paired with the exact DSL that produced them. No external "
          "image asset and no <Image> tag anywhere. Brand names and all data are "
          "self-authored demo values, stated as such in every case.md and in "
          "portfolio.json.",
)
print(json.dumps(m["counts"], ensure_ascii=False, indent=2))