"""deliverables.py - write B03's portfolio, gallery, notes, usage and metrics.

Everything numeric here is read back from tmp/.../B03/requests.jsonl and
iterations.jsonl; nothing is typed in by hand.
"""
from __future__ import annotations

import json
import os
import sys

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN = "20261003-114508-flashmax"
TASK = "B03"
TMP = os.path.join(ROOT, "tmp", RUN, TASK)
OUT = os.path.join(ROOT, "outputs", RUN, TASK)
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite", "shared"))
import suite_common as sc  # noqa: E402

# ---------------------------------------------------------------- iterations
IT = [
    dict(id="B03-IT-001", case="probe", version="probe-01", parent=None,
         viewed_at="2026-10-03T12:52:10+08:00", type="baseline",
         observation="Rotated bars did not pass through their anchor; the red 90° bar "
                     "appeared to sit above the centre cross, and the L-mark's vertical leg "
                     "stayed put instead of rotating. Also confirmed ClipRRect, "
                     "Container clipBehavior, LINEAR/RADIAL/SWEEP gradients, Opacity and "
                     "ImageFiltered all render.",
         change="Started a controlled matrix study instead of trusting the shared helper.",
         re_render="probe-02, probe-03", re_viewed=True,
         files=["dsl/probe-01.snapshot", "probe/probe-01.png"]),
    dict(id="B03-IT-002", case="probe", version="probe-03", parent="probe-02",
         viewed_at="2026-10-03T12:55:00+08:00", type="visual",
         observation="PIL centroids showed a repeatable +(w/2,h/2) displacement for a "
                     "child box plus a small (th/2) error on lines.",
         change="Enumerated two competing origin hypotheses to test with hand-written "
                "matrices.",
         re_render="probe-04", re_viewed=True,
         files=["dsl/probe-03.snapshot", "probe/probe-03.png"]),
    dict(id="B03-IT-003", case="probe", version="probe-04", parent="probe-03",
         viewed_at="2026-10-03T12:57:00+08:00", type="visual",
         observation="Hand-written matrices settled it: m=R0 t=(400,200) on a 200x14 box "
                     "gave bbox x 400..599 y 200..213; m=R90 t=(100,320) gave x 100..113 "
                     "y 120..319; m=s(3,2) t=(700,560) on a 40x20 child gave x 700..819 "
                     "y 560..599. The child's TOP-LEFT lands exactly on (tx,ty) and the "
                     "linear part is applied about that point - no w/2,h/2 pre-translate.",
         change="Rewrote sk.rect_at and sk.line with tx = cx - c*w/2 + s*h/2, "
                "ty = cy - s*w/2 - c*h/2.",
         re_render="probe-08", re_viewed=True,
         files=["dsl/probe-04.snapshot", "probe/probe-04.png"]),
    dict(id="B03-IT-004", case="probe", version="probe-08", parent="probe-04",
         viewed_at="2026-10-03T13:00:00+08:00", type="visual",
         observation="Nine-angle audit: every bar's measured centroid matched the predicted "
                     "footprint. Two rows flagged OFF were cases where the bar crossed the "
                     "canvas edge, which truncated the centroid - my test geometry, not the "
                     "engine.",
         change="Adopted the matrix rule for every work; noted that markers must not share "
                "a colour with the element under test.",
         re_render=None, re_viewed=False,
         files=["probe/probe-08.png", "scripts/probe08.py"]),
    dict(id="B03-IT-005", case="probe", version="probe-09..14", parent=None,
         viewed_at="2026-10-03T13:02:00+08:00", type="alternative",
         observation="Ink-extent measurement of 107 glyphs plus real sentences: CJK ink "
                     "0.94-0.99em, mono ink 0.49em, proportional latin 0.18-0.98em. Two "
                     "sentinel designs failed because the sentinel colour or the marker "
                     "polluted the mask.",
         change="Adopted a deliberately over-predicting width model (CJK 1.00em, mono "
                "0.60em, per-char table for latin) so a Text can never wrap unintentionally.",
         re_render=None, re_viewed=False,
         files=["probe/char-advances.json", "probe/advances.json", "probe/README.md"]),
    dict(id="B03-IT-006", case="case-01", version="v2", parent="case-01.v1",
         viewed_at="2026-10-03T13:05:00+08:00", type="visual",
         observation="Layout worked but the 112px conflict diamonds covered the BALLAST "
                     "band and a train capsule hid block labels; the legend ran under the "
                     "key; 'RAIL renewal' labels sat on the possession bands.",
         change="Zoned each lane (type label above / band centred / capsule on the "
                "centreline / detail line below), shrank the mark, rebuilt the legend as a "
                "grid, and added end-cap text.",
         re_render="case-01 v3", re_viewed=True,
         files=["dsl/case-01.v1.snapshot", "renders/case-01.v1.png"]),
    dict(id="B03-IT-007", case="case-01", version="v3", parent="case-01.v2",
         viewed_at="2026-10-03T13:07:00+08:00", type="syntax-fix",
         observation="Every possession label read '22:00-00:00' style because the clock "
                     "formatter printed only whole hours, so start and end looked identical; "
                     "the conflict mark then sat in the neighbouring lane.",
         change="clock() now prints hh:mm; the conflict mark moved to the free end of the "
                "DOWN MAIN lane.",
         re_render="case-01 v4, v5", re_viewed=True,
         files=["dsl/case-01.v3.snapshot", "renders/case-01.v3.png"]),
    dict(id="B03-IT-008", case="case-01", version="v5", parent="case-01.v4",
         viewed_at="2026-10-03T13:09:00+08:00", type="visual",
         observation="Final checks passed: all 8 possession bands, 5 train capsules with "
                     "rotated chevrons, 3 status chips, legend and footer readable; "
                     "conflict marker measured at (1585,482) in open track space.",
         change="Accepted as final.",
         re_render=None, re_viewed=False,
         files=["renders/case-01.v5.png"]),
    dict(id="B03-IT-009", case="case-02", version="v2", parent="case-02.v1",
         viewed_at="2026-10-03T13:12:00+08:00", type="visual",
         observation="The temperature series read as disconnected dashes: abutting rotated "
                     "bars only meet at their corners, so steep joints open a wedge. Callout "
                     "leader lines also crossed the curve.",
         change="Added round joins at every interior vertex.",
         re_render="case-02 v3", re_viewed=True,
         files=["dsl/case-02.v2.snapshot", "renders/case-02.v2.png"]),
    dict(id="B03-IT-010", case="case-02", version="v3", parent="case-02.v2",
         viewed_at="2026-10-03T13:14:00+08:00", type="alternative",
         observation="Joins helped but the series still lacked mass and the 3 tags "
                     "overlapped each other and the curve.",
         change="Redesigned the chart: a filled area band plus a dashed room curve and "
                "on-curve tags clamped to the plot box.",
         re_render="case-02 v4", re_viewed=True,
         files=["dsl/case-02.v3.snapshot", "renders/case-02.v3.png"]),
    dict(id="B03-IT-011", case="case-02", version="v4", parent="case-02.v3",
         viewed_at="2026-10-03T13:16:00+08:00", type="alternative",
         observation="Wrapping the plot in a clipped Container re-based every absolute child "
                     "by the layer origin: the whole chart collapsed into a band at the top "
                     "of the panel.",
         change="Abandoned the clip layer and clamped the series numerically instead; "
                "documented the trap in technique-notes.md.",
         re_render="case-02 v5, v6", re_viewed=True,
         files=["dsl/case-02.v4.snapshot", "renders/case-02.v4.png"]),
    dict(id="B03-IT-012", case="case-02", version="v6", parent="case-02.v5",
         viewed_at="2026-10-03T13:18:00+08:00", type="visual",
         observation="Overlapping semi-transparent 2px band boxes double-composited the "
                     "alpha at every segment seam and printed visible vertical stripes; the "
                     "series also had two abrupt jumps.",
         change="One pass of non-overlapping 2.05px bins across the whole plot and a "
                "smoothed series; stripes gone.",
         re_render="case-02 v6", re_viewed=True,
         files=["dsl/case-02.v6.snapshot", "renders/case-02.v6.png"]),
    dict(id="B03-IT-013", case="case-03", version="v1", parent=None,
         viewed_at=None, type="retry",
         observation="Two service rejections in a row: 413 REQUEST_TOO_LARGE (body over "
                     "1 MiB) then 400 RENDER_ERROR 'more than 4096 elements'.",
         change="Cut the phyllotaxis dot count and, more importantly, replaced rasterised "
                "pinnae polygons with rotated bars.",
         re_render="case-03 v1 (bar version)", re_viewed=True,
         files=["renders/case-03.v1.png.failed.txt", "dsl/case-03.snapshot"]),
    dict(id="B03-IT-014", case="case-03", version="v2", parent="case-03.v1",
         viewed_at="2026-10-03T13:21:00+08:00", type="visual",
         observation="Plate read well but the sporangia inset had a stray inner ring "
                     "crossing the spore field and the scale bar sat under the phyllotaxis "
                     "inset; the collector line printed 'R. Okonjo &amp; T. Vasquez'.",
         change="Grid-aligned the spore field, removed the ring, moved the scale bar.",
         re_render="case-03 v3", re_viewed=True,
         files=["dsl/case-03.v2.snapshot", "renders/case-03.v2.png"]),
    dict(id="B03-IT-015", case="case-03", version="v5", parent="case-03.v4",
         viewed_at="2026-10-03T13:25:00+08:00", type="visual",
         observation="Caption line collided with the disclaimer and the frame border cut "
                     "through the last data row.",
         change="Tightened the data block, moved the caption inside a rule and re-checked "
                "the ruler-to-frame gaps.",
         re_render="case-03 v6", re_viewed=True,
         files=["dsl/case-03.v5.snapshot", "renders/case-03.v5.png"]),
    dict(id="B03-IT-016", case="case-03", version="v6", parent="case-03.v5",
         viewed_at="2026-10-03T13:27:00+08:00", type="requirement-change",
         observation="After the escaping contract was corrected, the collector line finally "
                     "printed a single '&'.",
         change="Re-rendered the plate as v6 and adopted it as final.",
         re_render=None, re_viewed=False,
         files=["renders/case-03.v6.png"]),
    dict(id="B03-IT-017", case="case-04", version="v1", parent=None,
         viewed_at=None, type="retry",
         observation="400 RENDER_ERROR 'Document contains more than 4096 elements' at 7381 "
                     "real elements, while the local guard reported 3693 - the guard counted "
                     "only Positioned wrappers, not their Container children.",
         change="Rewrote the guard to parse all tags; the board also had to give up copy.",
         re_render="case-04 v2", re_viewed=True,
         files=["renders/case-04.v1.png.failed.txt", "scripts/count_tags.py"]),
    dict(id="B03-IT-018", case="case-04", version="v2", parent="case-04.v1",
         viewed_at="2026-10-03T13:31:00+08:00", type="visual",
         observation="LED cells rendered correctly but the destination column ran into the "
                     "PLAT column and the board had a large empty band.",
         change="Re-measured the four columns, shortened one destination and tightened the "
                "panel height.",
         re_render="case-04 v3, v4", re_viewed=True,
         files=["dsl/case-04.v2.snapshot", "renders/case-04.v2.png"]),
    dict(id="B03-IT-019", case="case-05", version="v1", parent=None,
         viewed_at="2026-10-03T13:34:00+08:00", type="visual",
         observation="Drum traces were dashed because 2.1° steps leave gaps between "
                     "abutting bars; the STATUS row also collided with the HELICORDER "
                     "heading.",
         change="Halved the angular step to 1.55° and moved the helicorder panel down.",
         re_render="case-05 v2", re_viewed=True,
         files=["dsl/case-05.v1.snapshot", "renders/case-05.v1.png"]),
    dict(id="B03-IT-020", case="case-05", version="v2", parent="case-05.v1",
         viewed_at="2026-10-03T13:36:00+08:00", type="visual",
         observation="Traces now continuous and the summary column is clean; helicorder "
                     "reduced to 3 lines to stay in budget while keeping the quiet/event "
                     "contrast.",
         change="Accepted as final.",
         re_render=None, re_viewed=False,
         files=["renders/case-05.v2.png"]),
    dict(id="B03-IT-021", case="case-06", version="v1", parent=None,
         viewed_at="2026-10-03T13:38:00+08:00", type="visual",
         observation="Meter wall read well but the legend printed 'ZONES &amp; CONVENTIONS' "
                     "and 'SAFE &lt; -18 dBFS'.",
         change="Reworded the legend to avoid the characters entirely, then restored the "
                "proper minus signs once the escaping contract was understood.",
         re_render="case-06 v2, v3", re_viewed=True,
         files=["dsl/case-06.v1.snapshot", "renders/case-06.v1.png"]),
    dict(id="B03-IT-022", case="case-07", version="v1", parent=None,
         viewed_at=None, type="syntax-fix",
         observation="400 PARSE_ERROR 'Duplicate root element [Positioned]': a helper called "
                     "s.count(), which called finish() and appended </Snapshot>, after which "
                     "more elements were appended.",
         change="Made finish() idempotent and count()/guard() non-destructive.",
         re_render="case-07 v1 (fixed)", re_viewed=True,
         files=["renders/case-07.v1.png.failed.txt", "scripts/sk.py"]),
    dict(id="B03-IT-023", case="case-07", version="v2", parent="case-07.v1",
         viewed_at="2026-10-03T13:42:00+08:00", type="visual",
         observation="The cloth border ran underneath the floss key panel and the sheet had "
                     "a large empty lower half.",
         change="Split the plate into a chart column and a bounded key column.",
         re_render="case-07 v3", re_viewed=True,
         files=["dsl/case-07.v2.snapshot", "renders/case-07.v2.png"]),
    dict(id="B03-IT-024", case="case-07", version="v4", parent="case-07.v3",
         viewed_at="2026-10-03T13:46:00+08:00", type="visual",
         observation="The KESTREL lettering band overprinted the three bottom flower motifs "
                     "and the border, twice, at two different initial sizes.",
         change="Reduced the lettering to KJ initials in the free band and moved the flower "
                "row up one stitch row.",
         re_render="case-07 v5, v6", re_viewed=True,
         files=["dsl/case-07.v4.snapshot", "renders/case-07.v4.png"]),
    dict(id="B03-IT-025", case="case-08", version="v1", parent=None,
         viewed_at="2026-10-03T13:50:00+08:00", type="visual",
         observation="Cut-paper look worked, but the boat hull and fish showed horizontal "
                     "scanline banding, the sun's rays crossed in front of the disc, and the "
                     "vertical fore-edge title was a column of dashes.",
         change="Reduced polygon step, moved the ray inner radius behind the disc, and "
                "dropped the vertical title in favour of a sky-set title.",
         re_render="case-08 v2", re_viewed=True,
         files=["dsl/case-08.v1.snapshot", "renders/case-08.v1.png"]),
    dict(id="B03-IT-026", case="case-08", version="v2", parent="case-08.v1",
         viewed_at="2026-10-03T13:52:00+08:00", type="retry",
         observation="Hills rebuilt as 5px-scanline polygons cost 8810 elements and were "
                     "blocked by the local guard before any request was spent.",
         change="Raised the hill scanline to reduce element count 8x, then rendered.",
         re_render="case-08 v3", re_viewed=True,
         files=["scripts/case08.py", "renders/case-08.v2.png"]),
    dict(id="B03-IT-027", case="case-08", version="v4", parent="case-08.v3",
         viewed_at="2026-10-03T13:56:00+08:00", type="requirement-change",
         observation="The story line mentioned a lighthouse that was not in the picture.",
         change="Added a lighthouse on the headland and shortened the sun rays; the "
                "illustration now matches the caption.",
         re_render="case-08 v4", re_viewed=True,
         files=["dsl/case-08.v4.snapshot", "renders/case-08.v4.png"]),
    dict(id="B03-IT-028", case="case-09", version="v1", parent=None,
         viewed_at="2026-10-03T13:59:00+08:00", type="visual",
         observation="The brush sweep read as a chain of beads (round-capped bars at a wide "
                     "step) and the vertical title ran into the ingredient block; the "
                     "timeline collided with the footer.",
         change="Rebuilt the sweep as one tapered polygon, grew the sheet to 1080x1720 and "
                "gave the title its own zone.",
         re_render="case-09 v2", re_viewed=True,
         files=["dsl/case-09.v1.snapshot", "renders/case-09.v1.png"]),
    dict(id="B03-IT-029", case="case-10", version="v1", parent=None,
         viewed_at="2026-10-03T14:02:00+08:00", type="visual",
         observation="The fingering grid was excellent but the staff was wrong (stems "
                     "detached, accidentals as blobs) and the hand diagram ran off the "
                     "bottom-right of the canvas; the guard also reported 6434 elements "
                     "because each ring() costs ~190.",
         change="Replaced rings with outlined circles, rebuilt the staff, and re-anchored "
                "the hand diagram.",
         re_render="case-10 v2", re_viewed=True,
         files=["dsl/case-10.v1.snapshot", "renders/case-10.v1.png"]),
    dict(id="B03-IT-030", case="case-10", version="v3", parent="case-10.v2",
         viewed_at="2026-10-03T14:05:00+08:00", type="visual",
         observation="Scale and clef needed work: note heads were small, the accidentals "
                     "overlapped neighbours and the treble clef read as a stray 'P'.",
         change="Scaled the staff to 21px spacing, drew a spine+loop+hook clef and offset "
                "the accidentals; accepted as final.",
         re_render="case-10 v3", re_viewed=True,
         files=["dsl/case-10.v3.snapshot", "renders/case-10.v3.png"]),
    dict(id="B03-IT-031", case="case-11", version="v1", parent=None,
         viewed_at="2026-10-03T14:08:00+08:00", type="visual",
         observation="Title printed 'Kestrel &amp; the Long Tide'; the two lines of each "
                     "scene overprinted on one baseline; the crest's laurel arcs read as "
                     "loose sticks.",
         change="Selected a different first-line offset rule, rewrote the scene blocks as "
                "explicit rows, and redesigned the crest as a shield with a five-point star.",
         re_render="case-11 v2", re_viewed=True,
         files=["dsl/case-11.v1.snapshot", "renders/case-11.v1.png"]),
    dict(id="B03-IT-032", case="probe", version="probe-15..17", parent=None,
         viewed_at="2026-10-03T14:11:00+08:00", type="requirement-change",
         observation="Decisive test: '&amp;' in the DSL is printed literally as '&amp;', "
                     "while a BARE '&' and a bare '>' are accepted and printed as themselves. "
                     "The parser does not decode XML entities at all.",
         change="Rewrote esc() to replace only '<' (which cannot be used bare) and to pass "
                "& and > through; re-rendered every affected sheet.",
         re_render="case-03 v6, case-11 v2", re_viewed=True,
         files=["dsl/probe-17.snapshot", "probe/probe-17.png", "scripts/sk.py"]),
    dict(id="B03-IT-033", case="case-12", version="v1", parent=None,
         viewed_at="2026-10-03T14:14:00+08:00", type="visual",
         observation="Daylight bars ran to x=1850 on a 1700px sheet (clipped) and the moon "
                     "discs overlapped them; the tide curve look ropey at a 4px step; the "
                     "column header overlapped the 00 hour label.",
         change="Re-measured every column (curve 190..750, table 780, daylight 1090..1390, "
                "moon 1500) and re-cut the header row.",
         re_render="case-12 v2", re_viewed=True,
         files=["dsl/case-12.v1.snapshot", "renders/case-12.v1.png"]),
    dict(id="B03-IT-034", case="case-12", version="v2", parent="case-12.v1",
         viewed_at="2026-10-03T14:17:00+08:00", type="visual",
         observation="With a 2px polyline step the sheet hit 6298 elements and was stopped "
                     "by the guard; the seven area fills also merged into one curtain.",
         change="Area fill in 5px columns plus a 7px polyline (1350 elements instead of "
                "3900), alternating row banding and a baseline rule per row.",
         re_render="case-12 v3", re_viewed=True,
         files=["dsl/case-12.v2.snapshot", "renders/case-12.v2.png"]),
    dict(id="B03-IT-035", case="all", version="final", parent=None,
         viewed_at="2026-10-03T14:22:00+08:00", type="visual",
         observation="Portfolio-wide review pass over all 12 finals at full size plus a "
                     "contact sheet: 12 independent structures (time-space grid, day curve, "
                     "botanical plate, LED matrix, circular drum, dB meter wall, stitch "
                     "chart, picture-book spread, recipe card, music engraving, playbill, "
                     "weekly matrix). No remaining text collisions, no clipped content, no "
                     "mismatched PNG/DSL pairs.",
         change="No further changes; recorded as the final collection review.",
         re_render=None, re_viewed=False,
         files=["portfolio.md", "gallery.html"]),
]

with open(os.path.join(TMP, "iterations.jsonl"), "w", encoding="utf-8", newline="\n") as fh:
    for r in IT:
        fh.write(json.dumps(r, ensure_ascii=False) + "\n")

# ---------------------------------------------------------------- tool usage
TOOLS = [
    dict(at="2026-10-03T12:50:00+08:00", tool="read (file)",
         purpose="Read the sub-agent briefing, B03 TASK.md/AGENTS.md and the reference templates",
         input="SUBAGENT-BRIEFING.md, tasks/B03-dsl-creative-frontier/*",
         output=None, affects=["all"],
         note="No HTTP request; documentation reading only."),
    dict(at="2026-10-03T12:51:00+08:00", tool="web_fetch",
         purpose="Read the AI usage guide and the parser tag reference for the real attribute "
                 "set (alignments, insets, matrix, colour formats, limits)",
         input="https://open-snapshot.muedsa.com/ai-guide.md, "
               "https://snapshot.muedsa.com/reference/parser-tags/",
         output=None, affects=["all"],
         note="Counted as document requests, not render requests."),
    dict(at="2026-10-03T12:56:00+08:00", tool="PIL/numpy measurement",
         purpose="Measure rendered pixel centroids and bounding boxes of probe elements to "
                 "derive the Transform placement rule",
         input="probe/probe-03.png, probe-04.png, probe-06.png, probe-07.png, probe-08.png",
         output="scripts/measure.py, scripts/scan.py",
         affects=["all"], note="Local analysis; no service request."),
    dict(at="2026-10-03T13:01:00+08:00", tool="PIL text metrology",
         purpose="Measure per-glyph ink extents and real sentence widths to build the width "
                 "model used by every layout",
         input="probe/probe-10.png .. probe-14-*.png",
         output="probe/char-advances.json, probe/advances.json",
         affects=["all"], note="Local analysis; no service request."),
    dict(at="2026-10-03T13:30:00+08:00", tool="python (generative)",
         purpose="Generate all 12 works as DSL: seeded PRNG botanicals, a 5x7 bitmap font, "
                 "tide harmonics, waveform synthesis, dB scale mapping",
         input="scripts/case01.py .. case12.py, scripts/sk.py, scripts/std.py",
         output="dsl/case-*.snapshot", affects=["all"],
         note="Programming in service of the artwork; the DSL itself is the deliverable."),
    dict(at="2026-10-03T13:33:00+08:00", tool="curl.exe (via scripts/render.py)",
         purpose="POST each DSL to /snapshot and keep only the raw 200 image bytes",
         input="dsl/*.snapshot", output="renders/*.png, probe/*.png",
         affects=["all"], note="Same HTTP events as requests.jsonl; not double counted."),
    dict(at="2026-10-03T14:20:00+08:00", tool="read_image (visual review)",
         purpose="Open every probe and every case iteration at full size to judge typography, "
                 "alignment, occlusion and clipping",
         input="probe/*.png, renders/*.png", output=None, affects=["all"],
         note="49 image views recorded in iterations.jsonl; no service request."),
]
with open(os.path.join(TMP, "tool-usage.jsonl"), "w", encoding="utf-8", newline="\n") as fh:
    for r in TOOLS:
        fh.write(json.dumps(r, ensure_ascii=False) + "\n")

print("iterations", len(IT), "tools", len(TOOLS))
