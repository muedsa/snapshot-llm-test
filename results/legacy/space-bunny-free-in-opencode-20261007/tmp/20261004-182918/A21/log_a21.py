# -*- coding: utf-8 -*-
"""A21 wrap-up: record the three-round summary in the suite state and build the
cumulative task-metrics.json.

Iterations were already appended to iterations.jsonl as they happened (one call
per real render/view event), so nothing is re-logged here - that keeps the
iteration count honest and avoids double counting.
"""
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite"))
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "A21"))
import wrapup  # noqa: E402
import state as S  # noqa: E402

STARTED = "2026-10-05T03:40:28.609+08:00"
FIRST_IMAGE = "2026-10-05T03:49:12.000+08:00"
ENDED = "2026-10-05T05:02:00.000+08:00"

ARTIFACTS = []
for rnd in ("round-01", "round-02", "round-03"):
    for f in ("launch-portrait.png", "launch-portrait.snapshot",
              "launch-wide.png", "launch-wide.snapshot",
              "design-tokens.json", "content-map.json",
              "snapshot-usage.md", "task-metrics.json"):
        ARTIFACTS.append(os.path.join("outputs", RUN, "A21", rnd, f))
ARTIFACTS += [os.path.join("outputs", RUN, "A21", "round-03", n) for n in
              ("contrast-audit.json", "contrast-audit-launch-portrait.json",
               "contrast-audit-launch-wide.json")]
ARTIFACTS += [os.path.join("outputs", RUN, "A21", n) for n in
              ("design-tokens.json", "content-map.json",
               "snapshot-usage.md", "task-metrics.json")]

VISUAL = []
for rnd in ("round-01", "round-02", "round-03"):
    for img in ("launch-portrait", "launch-wide"):
        VISUAL.append("opened %s/%s.png with the read tool and reviewed it at full size"
                      % (rnd, img))
        VISUAL.append("opened %s/%s-notxt-%s.png (text-free reference) via the audit "
                      "pipeline and pixel-diffed it against the final image"
                      % (rnd, img, rnd.split("-")[1]))
VISUAL += [
    "opened tmp/20261004-182918/A21/preview/probe-metrics.png and cropped the shape probe row (Transform / gradients / ring / dashed / BOLD_ITALIC)",
    "opened tmp/20261004-182918/A21/preview/probe-display.png to check Inter Black metrics",
    "cropped crops/launch-portrait-r01-header.png (44px header mark, 1.6x)",
    "cropped crops/launch-portrait-r01-mark.png (380px hero mark, 1.6x)",
    "cropped crops/launch-portrait-r02-card.png (three-row info card, 1.5x)",
    "cropped crops/launch-portrait-r02-title.png (long title + kicker, 1.5x)",
    "cropped crops/launch-portrait-r03-mark.png (light-theme mark, 1.7x)",
    "cropped crops/launch-wide-r03-en.png (English line above the URL, 1.7x)",
    "ran tmp/20261004-182918/A21/verify_all.py on the delivered files: 0 failures",
]

UNRESOLVED = [
    "round-02/03 requirements were pre-loaded in the task folder, so this run is "
    "preloaded_sequential execution and NOT hidden-feedback blind testing; no "
    "round claims to have received surprise feedback",
    "the standalone round-01 tagline line was dropped from round-02 on because its "
    "text became part of the new main title; the string is still present inside "
    "the title. This is a design decision, documented in round-02/snapshot-usage.md",
    "the wide asset's third title line starts with the particle '的'; that is the "
    "only way to satisfy 'at most 3 lines' + 'at least 48px' + 'no transform "
    "narrowing' inside a 628px column (the single line needs 1288px at 48px)",
    "token / cost / image_input_usage are null: the service exposes no such metric "
    "and the chat platform reported none; nothing was estimated",
    "rate_limit_or_queue_wait_seconds is null because no response reported a queue "
    "segment and no 429/503 occurred",
]

NOTES = ("A21 executed all three preloaded rounds back to back without waiting for "
         "a user message: round-01 from TASK.md, round-02 after archiving round-01, "
         "round-03 after archiving round-02. Shared kit: brandkit.py (tokens, the "
         "six component mark, measured type metrics, layout recorder), audit.py "
         "(ink containment, pairwise text collision, reserved band and WCAG "
         "contrast audits driven by a text-free reference render), verify_all.py "
         "(delivery gate).")

m = wrapup.wrapup("A21", STARTED, FIRST_IMAGE, ENDED, iterations=[],
                  artifacts=ARTIFACTS, visual_evidence=VISUAL,
                  unresolved=UNRESOLVED, rounds=["round-01", "round-02", "round-03"],
                  cases=[], notes=NOTES, status="completed")

# --- enrich the task level metrics with the per-round split ---------------
import json  # noqa: E402

OUT = os.path.join(S.OUT_ROOT, "A21")
pngs, dsls = [], []
for dirpath, _dirs, files in os.walk(OUT):
    for f in sorted(files):
        rel = os.path.relpath(os.path.join(dirpath, f), ROOT).replace(os.sep, "/")
        if f.endswith(".png"):
            pngs.append(rel)
        elif f.endswith(".snapshot"):
            dsls.append(rel)
pngs.sort()
dsls.sort()
rounds = {}
for rnd in ("round-01", "round-02", "round-03"):
    with open(os.path.join(OUT, rnd, "task-metrics.json"), encoding="utf-8") as fh:
        r = json.load(fh)
    rounds[rnd] = {
        "requirements_source": r["notes"],
        "wall_clock_seconds_total": r["wall_clock_seconds_total"],
        "sum_of_request_durations_seconds": r["sum_of_request_durations_seconds"],
        "render_requests": r["counts"]["render_requests"],
        "successful_render_requests": r["counts"]["successful_render_requests"],
        "failed_render_requests": r["counts"]["failed_render_requests"],
        "image_views": r["counts"]["image_views"],
        "completed_visual_iterations": r["counts"]["completed_visual_iterations"],
        "dsl_version_ids": r["counts"]["dsl_version_ids"],
        "final_png_files": r["counts"]["final_png_files"],
    }
m["counts"]["final_pngs"] = len(pngs)
m["counts"]["final_png_files"] = pngs
m["counts"]["delivered_snapshot_files"] = len(dsls)
m["counts"]["delivered_snapshot_paths"] = dsls
m["counts"]["dsl_versions"] = 12
m["counts"]["dsl_version_ids"] = ["A21-r01-v01 .. A21-r01-v06",
                                  "A21-r02-v01 .. A21-r02-v03",
                                  "A21-r03-v01 .. A21-r03-v03"]
m["counts"]["note_on_dsl_versions"] = (
    "12 logged design iterations across the three rounds; the distinct DSL file "
    "basenames are only 4 because each round reuses launch-portrait.snapshot / "
    "launch-wide.snapshot plus the two metric probes. Every version is preserved "
    "in tmp/20261004-182918/A21/drafts/ and logged in iterations.jsonl.")
m["per_round"] = rounds
m["visual_review_evidence_count"] = len(VISUAL)
m["verification"] = {
    "delivery_gate": "tmp/20261004-182918/A21/verify_all.py",
    "result": "0 failures",
    "checks_cover": ["PNG exists and is a real PNG", "exact pixel size",
                     "PNG/DSL pairing", "DSL is well-formed with root <Snapshot>",
                     "no <Image> tag", "no remote or data URI",
                     "ink containment vs a text-free reference render",
                     "pairwise text-on-text collision count",
                     "reserved extension bands empty",
                     "every text >= 4.5:1 against the composited background",
                     "required copy present in both sizes",
                     "minimum font size >= 24", "main title size and line count",
                     "brand mark has 6 components"],
}
m["rounds_delivered"] = ["round-01", "round-02", "round-03"]
m["round_execution"] = "preloaded_sequential"
m["blind_feedback"] = False
m["round_execution_note"] = (
    "round-02 and round-03 requirement files were readable in the task folder "
    "from the start; each was opened only after the previous round was rendered, "
    "viewed and archived, but this is NOT hidden-feedback blind testing.")
with open(os.path.join(OUT, "task-metrics.json"), "w", encoding="utf-8") as fh:
    json.dump(m, fh, ensure_ascii=False, indent=2)
print(json.dumps({k: m[k] for k in ("wall_clock_seconds_total",
                                    "wall_clock_seconds_to_first_usable_image",
                                    "sum_of_request_durations_seconds", "counts")},
                 ensure_ascii=False, indent=2))