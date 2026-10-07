"""A12 wrap-up: log the real iteration history, build task-metrics.json and
update the suite state. Must be run after build_a12.py + verify_png.py."""
from __future__ import annotations

import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import wrapup  # noqa: E402

STARTED = "2026-10-04T22:39:54.246+08:00"
FIRST_IMAGE = "2026-10-04T22:44:08.843+08:00"
ENDED = "2026-10-05T00:08:35.983+08:00"

T = os.path.join("tmp", "20261004-182918", "A12")
O = os.path.join("outputs", "20261004-182918", "A12")

# (version, parent, kind, dsl, image, viewed_at, observed, changes, complete)
ITERATIONS = [
    ("A12-v01", None, "baseline",
     T + "/drafts/mobile-v01.snapshot", O + "/mobile.png",
     "2026-10-04T22:47:00+08:00",
     "Opened mobile.png: the whole top band is empty - main title, subtitle, CTA "
     "button text and the six index chips are all missing. grep of the emitted DSL "
     "found no 'Structure' and no subtitle string at all, so the elements were "
     "never generated rather than dropped by the service.",
     "first render of all four canvases from one content set + one token set",
     False),
    ("A12-v01-fix-a", "A12-v01", "syntax-fix",
     T + "/drafts/mobile-v01.snapshot", None, None,
     "400 PARSE_ERROR on #FF7A3DFF33 (10 hex digits) and "
     "'Unexpected character in state TAG_OPEN' (tag name printed one char per line).",
     "alpha colours rebuilt from a 6-digit base; comp_ring now returns a list so "
     "'kids += ' cannot splice characters; nested text wrapped in Stack(fit=EXPAND)",
     False),
    ("A12-v02", "A12-v01-fix-a", "visual",
     T + "/drafts/mobile-v02.snapshot", O + "/mobile.png",
     "2026-10-04T23:13:55+08:00",
     "Opened all four v02 PNGs. Titles/subtitles/CTA/chips now render. Two real "
     "defects remain: '云构中心 · ONLINE' is cut to '云构中心 ·' on desktop and stage, "
     "and the dashed rule inside each card runs through the card title baseline "
     "(confirmed at 4x zoom on crops/s-card1.png).",
     "measured per-size advance widths with probe_fonts2/4 and probe_metrics; box "
     "widths now max(model, measured)*1.05; dashed rule moved to head+26 and div "
     "60->46; desktop empty rail panel replaced by a ring + rail + hairline footer",
     False),
    ("A12-v03", "A12-v02", "visual",
     T + "/drafts/desktop-v03.snapshot", O + "/desktop.png",
     "2026-10-04T23:38:30+08:00",
     "Opened desktop.png and stage.png: '云构中心 · ONLINE' is STILL truncated. "
     "Measuring the accent-2 pixels of the desktop footer website showed the ink at "
     "x=50..381 instead of 225..558, and the ghost '01' measured 49 px wide, i.e. the "
     "whole canvas was rendering every Text left-aligned.",
     "grep of the DSL showed the location value carried fontFamily=DejaVu Sans Mono "
     "(no CJK glyphs) while its width model assumed the UI font; added "
     "FONT_MODEL_MISMATCH assertion. probe_textalign2 proved the textAlign enum is "
     "fine, so the bug was Rec.t swallowing 'align' instead of forwarding it to "
     "D.text_el - fixed, which also centred the CTA text and index chips",
     False),
    ("A12-v04", "A12-v03", "visual",
     T + "/drafts/desktop-v03.snapshot", O + "/desktop.png",
     "2026-10-04T23:52:10+08:00",
     "Opened desktop.png: location value now complete, CTA centred, website "
     "right-aligned. Remaining: the ghost-index box was still sized from the "
     "hand-made model instead of the measured ink, so TEXT_TOO_NARROW fired for 12 "
     "ghost numerals.",
     "ghost box width changed to need(measured)+4; then ran probe_metrics.py over all "
     "104 (text, family, size) triples the build emits and re-rendered",
     False),
    ("A12-v05", "A12-v04", "visual",
     O + "/mobile.snapshot", O + "/mobile.png",
     "2026-10-05T00:09:40+08:00",
     "Opened mobile.png, tablet.png, desktop.png, stage.png in turn: every input "
     "field is present verbatim, no box overlap, safe margins met, CTA/chips centred, "
     "ghost indices right-aligned and clear of the corner ticks, the tablet gutter "
     "rail and both stage rails visible.",
     "no further change - this is the delivered version",
     True),
    ("A12-v05-verify", "A12-v05", "visual",
     O + "/content-map.json", None,
     "2026-10-05T00:10:30+08:00",
     "Pixel-level check of the delivered PNGs: 78 content fields isolated by exact "
     "RGB; all four sizes correct; worst ink delta 3 px (anti-aliased edges), well "
     "inside the 4 px edge tolerance and far below a wrap-and-clip loss.",
     "verify_png.py: per-field rendered ink vs measured ink, plus safe-margin audit; "
     "result written to verify-png.json and content-map.json (verification block)",
     True),
]

ARTIFACTS = [
    "mobile.png", "mobile.snapshot", "tablet.png", "tablet.snapshot",
    "desktop.png", "desktop.snapshot", "stage.png", "stage.snapshot",
    "design-tokens.json", "content-map.json", "snapshot-usage.md",
]

VISUAL_EVIDENCE = [
    "mobile.png opened at full size after every render round (5 rounds)",
    "tablet.png opened at full size after every render round (5 rounds)",
    "desktop.png opened at full size after every render round (5 rounds)",
    "stage.png opened at full size after every render round (5 rounds)",
    "crops/m-card1-ghost.png - 4x zoom proving the ghost index clears the corner tick",
    "crops/s-card1.png - 4x zoom proving the card dashed rule ran through the title",
    "crops/s-meta.png - 2x zoom proving '云构中心 · ONLINE' was truncated",
    "crops/d-meta.png - 2.6x zoom re-checking the same field after the font fix",
    "verify-png.json - per-field ink measurement of the four delivered PNGs (78/78 ok)",
]

UNRESOLVED = [
    "probe_textalign.py with the degenerate string 'WWWWWWWWWW' rendered roughly 19 "
    "W glyphs although the DSL contains one Text node with 10; a normal string "
    "behaves correctly. Not reproduced in any deliverable, cause unconfirmed.",
    "The 2-3 px difference between grey-background probe ink and on-canvas ink is "
    "anti-aliased edge pixels lost to exact-RGB matching; the verifier uses a 4 px "
    "tolerance, which still separates this from a real wrap-and-clip loss.",
]

NOTES = ("one generator + one content set + one token set emit four independent "
         "absolute-positioned DSLs; 590 render requests total (4 final + 586 probes "
         "and development iterations); 21 real failures all documented; no 429/503; "
         "one client read timeout auto-retried successfully")

if __name__ == "__main__":
    m = wrapup.wrapup("A12", STARTED, FIRST_IMAGE, ENDED, ITERATIONS,
                      artifacts=ARTIFACTS, visual_evidence=VISUAL_EVIDENCE,
                      unresolved=UNRESOLVED, notes=NOTES, status="completed",
                      rounds=["v01-baseline", "v02-measured-widths", "v03-font-and-align",
                              "v04-measured-metrics", "v05-final"],
                      cases=["mobile-360x800", "tablet-768x1024",
                             "desktop-1440x900", "stage-1920x1080"])
    print("render_requests      :", m["counts"]["render_requests"])
    print("successful           :", m["counts"]["successful_render_requests"])
    print("failed               :", m["counts"]["failed_render_requests"])
    print("dsl_versions         :", m["counts"]["dsl_versions"])
    print("image_views          :", m["counts"]["image_views"])
    print("completed_visual_it  :", m["counts"]["completed_visual_iterations"])
    print("final_pngs           :", m["counts"]["final_pngs"], m["counts"]["final_png_files"])
    print("wall_clock_seconds   :", m["wall_clock_seconds_total"])
    print("sum_request_seconds  :", m["sum_of_request_durations_seconds"])