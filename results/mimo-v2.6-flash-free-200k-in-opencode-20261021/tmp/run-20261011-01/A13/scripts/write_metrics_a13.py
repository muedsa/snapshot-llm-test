import json
import datetime

m = {
    "schema_version": 1,
    "path_base": "suite_root",
    "task_id": "A13",
    "run_id": "run-20261011-01",
    "task_round": None,
    "status": "completed",
    "stop_reason": "两方向预览实际对比选定后完善；四张交付图逐张与32px缩略视觉自检通过；纯黑0违规、几何一致性AA量化通过",
    "output_dir": "outputs/run-20261011-01/A13",
    "temp_dir": "tmp/run-20261011-01/A13",
    "timings": {
        "started_at": "2026-10-14T10:33:00+08:00",
        "started_at_note": "approximate: A12 state update at 10:31:08+08:00, first A13 render 10:38:08+08:00; task-file reading and generator writing in between",
        "ended_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "elapsed_seconds": 2340,
        "elapsed_note": "single active session wall clock (10:33-11:12)",
        "first_usable_image_seconds": 310,
        "first_usable_image_note": "start -> first successful render completed (A13-req-0001 direction-A preview, 10:38:09.7+08:00); both previews were usable on first render",
        "user_feedback_wait_seconds": 0,
        "user_feedback_wait_note": "single-shot automated suite run, no user feedback rounds",
        "rate_limit_wait_seconds": 0,
        "rate_limit_wait_note": "no 429 observed",
        "queue_wait_seconds": None,
        "queue_wait_note": "server queue time not exposed; client elapsed only",
        "request_duration_sum_seconds": 7.970,
        "request_duration_sum_note": "sum of the 6 render requests as logged in requests.jsonl; not the task wall clock",
        "server_timing_source": None,
        "server_timing_source_note": "no Server-Timing header; requestId not returned on 200 responses"
    },
    "counts": {
        "snapshot_requests": 6,
        "successful_snapshot_requests": 6,
        "failed_snapshot_requests": 0,
        "failed_snapshot_requests_note": "no 400/429; all six DSLs parsed and rendered on first attempt (circle border ring, transparent canvases, gradients all worked immediately)",
        "retry_requests": 0,
        "other_service_requests": 0,
        "other_service_requests_note": "ai-guide.md, parser-tags.html (Snapshot background default / Container border + shape=CIRCLE / color alpha) and the fonts list reused from the suite doc cache (logged as A13-doc-reuse-* in requests.jsonl, not new HTTP)",
        "probe_requests": 0,
        "probe_requests_note": "no probes needed: border ring and transparent background followed directly from the cached tag reference",
        "dsl_versions": 6,
        "dsl_versions_note": "6 DSL files: 2 direction previews (preview-a/b) + 4 finals (symbol-color/symbol-black/brand-banner/launch-poster); the final geometry is the refined version of preview-b",
        "image_views": 18,
        "image_views_note": "previews: 2 full + 2 at 32px light-bg + 2 x8 zoom; finals: 4 full canvases; final 32px check: 2 light-bg + 2 x8 zoom; delivered files re-opened: 4",
        "completed_visual_iterations": 1,
        "incomplete_visual_iterations": 0,
        "exploration_iterations": 1,
        "exploration_iterations_note": "iter-001: two genuinely different geometric directions compared at 512/32px/x8, direction B chosen",
        "measurement_iterations": 2,
        "measurement_iterations_note": "iter-003: pure-black/alpha-identity/bounds checks, plus a follow-up quantification of the 542 alpha-mismatch pixels (all delta=1 AA rounding on shape edges)"
    },
    "logs": {
        "requests": "tmp/run-20261011-01/A13/requests.jsonl",
        "iterations": "tmp/run-20261011-01/A13/iterations.jsonl"
    },
    "outputs": [
        "outputs/run-20261011-01/A13/symbol-color.png",
        "outputs/run-20261011-01/A13/symbol-color.snapshot",
        "outputs/run-20261011-01/A13/symbol-black.png",
        "outputs/run-20261011-01/A13/symbol-black.snapshot",
        "outputs/run-20261011-01/A13/brand-banner.png",
        "outputs/run-20261011-01/A13/brand-banner.snapshot",
        "outputs/run-20261011-01/A13/launch-poster.png",
        "outputs/run-20261011-01/A13/launch-poster.snapshot",
        "outputs/run-20261011-01/A13/brand-system.json",
        "outputs/run-20261011-01/A13/rationale.md",
        "outputs/run-20261011-01/A13/snapshot-usage.md",
        "outputs/run-20261011-01/A13/task-metrics.json"
    ],
    "candidates": [
        "tmp/run-20261011-01/A13/drafts/preview-a.png",
        "tmp/run-20261011-01/A13/drafts/preview-b.png",
        "tmp/run-20261011-01/A13/thumbs/symbol-color-32-light.png",
        "tmp/run-20261011-01/A13/thumbs/symbol-black-32-light.png",
        "tmp/run-20261011-01/A13/thumbs/preview-a-32-light.png",
        "tmp/run-20261011-01/A13/thumbs/preview-b-32-light.png"
    ],
    "rounds": [],
    "unresolved_issues": [],
    "audit_summary": {
        "two_directions": "direction A orthogonal staggered rounded plates vs direction B radial aperture (ring + eccentric lens disc + light dot); both 512x512 transparent previews kept in tmp; chosen by actual viewing at 512, 32px actual size and x8 zoom",
        "same_geometry": "one parameter table + one scale/offset generator feeds all four DSLs; colour vs black icons alpha channels compared pixel-by-pixel: 542 differing pixels, all delta=1 on antialiased edges, alpha coverage rel diff 2.3e-5",
        "pure_black": "Pillow 10.0.0 RGBA decode (PNG stores unpremultiplied): 92,549 pixels with alpha>0, all RGB=0, 0 violations, alpha range [1,255] (AA edges only)",
        "component_count": "3 primary motifs (ring/disc/dot) <= 6; hole and gaps are negative space with recorded generation rule",
        "small_size": "32x32 via premultiplied-alpha LANCZOS (Pillow 10.0.0), viewed at actual size on shared light background #F1F5F9 plus x8 NEAREST edge view; previews only in tmp, finals untouched",
        "applications": "banner 1200x400 icon at scale 0.375 offset (72,104); poster 1080x1350 independent vertical composition, icon at scale 0.62 offset (382,176); no Image widget anywhere",
        "gotcha": "85% translucent disc over the cyan ring muddied the silhouette at 32px - icon layers should be opaque with geometric overlap; transparent icons must omit the background attribute (default is transparent)"
    }
}

with open("outputs/run-20261011-01/A13/task-metrics.json", "w", encoding="utf-8") as f:
    json.dump(m, f, ensure_ascii=False, indent=2)
    f.write("\n")
print("written", m["timings"]["ended_at"])
