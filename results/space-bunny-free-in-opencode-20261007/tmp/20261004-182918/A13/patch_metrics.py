# -*- coding: utf-8 -*-
"""A13: append an A13-specific detail block to task-metrics.json.

`finalize.build()` cannot know about this task's inspection extras, and re-running
wrapup would duplicate iterations.jsonl, so the extra fields are appended here and
labelled as such.
"""
import json
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import state as S  # noqa: E402

OUT = os.path.join(S.OUT_ROOT, "A13")
TMP = os.path.join(S.TMP_ROOT, "A13")
path = os.path.join(OUT, "task-metrics.json")
with open(path, encoding="utf-8") as fh:
    m = json.load(fh)

vr = json.load(open(os.path.join(TMP, "verify", "report.json"), encoding="utf-8"))
m["a13_detail"] = {
    "appended_after_wrapup": True,
    "note": "counts.image_views counts iteration-log entries that carry a viewed_at "
            "timestamp; actual_image_opens counts the PNG files opened with the "
            "image viewer during the task. They differ because two iterations "
            "(v01/v02) reuse one request and the crops were viewed without a "
            "separate DSL version.",
    "actual_image_opens": 21,
    "actual_image_open_list": [
        "probes/probe-alpha.png", "preview/direction-A.png", "preview/direction-B.png",
        "preview/v03-amber/symbol-color.png", "preview/v04b-inset/symbol-color.png",
        "preview/v04c-r64exact/symbol-color.png",
        "preview/v04c-r64exact/magnified/svc-check-black-32x32.png",
        "preview/v05-void/symbol-color.png",
        "preview/v05-void/magnified/svc-check-black-32x32.png",
        "preview/v06-sharpvoid/symbol-color.png", "preview/candidates.png",
        "preview/v09-fixed/symbol-color.png", "preview/v10-noseam/zoom-center.png",
        "outputs/A13/symbol-black.png", "outputs/A13/brand-banner.png",
        "crops/brand-banner-banner-mark.png", "outputs/A13/launch-poster.png (1st)",
        "outputs/A13/launch-poster.png (2nd, after rhythm fix)",
        "crops/launch-poster-poster-topbar.png",
        "crops/launch-poster-poster-hero.png", "preview/final/thumb32-check.png",
    ],
    "renders_by_purpose": {
        "capability_probes": 2,
        "direction_previews_512_transparent": 2,
        "geometry_schemes_explored": 5,
        "candidate_comparison_sheet": 1,
        "small_size_checks_32_48_64_96": 30,
        "delivered_final_images": 5,
        "final_32px_thumbnails": 2,
        "total": 47,
        "note": "the remainder of the 78 render requests are the companion mono/colour "
                "pair of each scheme iteration; see requests.jsonl for the exact list",
    },
    "self_check": {
        "report": "tmp/20261004-182918/A13/verify/report.json",
        "checks": len(vr) - 1,
        "all_passed": vr["summary"]["all_passed"],
        "failed": vr["summary"]["failed_checks"],
    },
    "delivered": {
        "symbol-color.png": "512x512 RGBA, alpha 0 in the clearspace ring",
        "symbol-black.png": "512x512 RGBA, RGB=0 wherever alpha>0",
        "brand-banner.png": "1200x400 RGBA",
        "launch-poster.png": "1080x1350 RGBA",
    },
}
with open(path, "w", encoding="utf-8") as fh:
    json.dump(m, fh, ensure_ascii=False, indent=2)
print("patched", path, os.path.getsize(path), "bytes")