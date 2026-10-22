import json, datetime

m = {
    "schema_version": 1,
    "path_base": "suite_root",
    "task_id": "A11",
    "run_id": "run-20261011-01",
    "task_round": None,
    "status": "completed",
    "stop_reason": "需求满足并完成两页与局部裁剪的视觉自检",
    "output_dir": "outputs/run-20261011-01/A11",
    "temp_dir": "tmp/run-20261011-01/A11",
    "timings": {
        "started_at": "2026-10-13T12:33:00+08:00",
        "started_at_note": "approximate: A10 ended 12:31:30+08:00, first A11 file created ~12:44, task-file reading happened in between",
        "ended_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "elapsed_seconds": 4500,
        "elapsed_note": "two active sessions separated by an overnight pause: 2026-10-13 12:33-13:05 (1920s) + 2026-10-14 09:12-09:55 (2580s); overnight wait not counted",
        "first_usable_image_seconds": 957,
        "first_usable_image_note": "start -> first successful render (A11-req-0003 finished 12:49:57+08:00); the v1 baseline had failed with 400",
        "user_feedback_wait_seconds": 0,
        "user_feedback_wait_note": "single-shot automated suite run, no user feedback rounds",
        "rate_limit_wait_seconds": 0,
        "rate_limit_wait_note": "no 429 observed",
        "queue_wait_seconds": None,
        "queue_wait_note": "server queue time not exposed; client elapsed only",
        "request_duration_sum_seconds": 26.814,
        "request_duration_sum_note": "sum of the 13 render requests as logged in requests.jsonl; not the task wall clock",
        "server_timing_source": None,
        "server_timing_source_note": "no Server-Timing/requestId surfaced to the client in the response headers (requestId only appears inside 400 error bodies)"
    },
    "counts": {
        "snapshot_requests": 13,
        "successful_snapshot_requests": 8,
        "failed_snapshot_requests": 5,
        "failed_snapshot_requests_note": "all 5 are diagnosed 400 PARSE_ERROR responses (v1 generator bug x2, probe failures x4 - one probe succeeded); bodies kept as drafts/*.error.json, no 429, no retries",
        "retry_requests": 0,
        "other_service_requests": 0,
        "other_service_requests_note": "ai-guide.md, parser-tags.html and the fonts list were reused from the suite doc cache (logged as A11-doc-reuse-* in requests.jsonl, not new HTTP)",
        "probe_requests": 7,
        "probe_requests_note": "A11-req-0005..0011: entity/raw-tag/Raw-placement/text-attribute/PAID-spacing emission probes (3x200, 4x400)",
        "dsl_versions": 3,
        "probe_dsl_variants": 6,
        "image_views": 20,
        "image_views_note": "v2: 2 full pages + 2 crops; probes: 3 images; v3: 2 full pages + 5 crops; final delivered PNGs: 2 full pages + 4 fresh crops cut from outputs/",
        "completed_visual_iterations": 2,
        "incomplete_visual_iterations": 0,
        "measurement_iterations": 2,
        "measurement_iterations_note": "v1 check run reported 2 false failures from flawed metrics (median-gap spacing, raw-baseline equality); v2 after the cell-model/CJK-hang rewrite passed all 7 checks without touching the images"
    },
    "logs": {
        "requests": "tmp/run-20261011-01/A11/requests.jsonl",
        "iterations": "tmp/run-20261011-01/A11/iterations.jsonl"
    },
    "outputs": [
        "outputs/run-20261011-01/A11/invoice-page-01.png",
        "outputs/run-20261011-01/A11/invoice-page-01.snapshot",
        "outputs/run-20261011-01/A11/invoice-page-02.png",
        "outputs/run-20261011-01/A11/invoice-page-02.snapshot",
        "outputs/run-20261011-01/A11/invoice-audit.json",
        "outputs/run-20261011-01/A11/text-map.json",
        "outputs/run-20261011-01/A11/snapshot-usage.md",
        "outputs/run-20261011-01/A11/task-metrics.json"
    ],
    "candidates": [
        "tmp/run-20261011-01/A11/drafts/invoice-page-01-v1.png.error.json",
        "tmp/run-20261011-01/A11/drafts/invoice-page-01-v2.png",
        "tmp/run-20261011-01/A11/drafts/invoice-page-02-v2.png",
        "tmp/run-20261011-01/A11/drafts/probe-entities.png",
        "tmp/run-20261011-01/A11/drafts/probe-entities5.png",
        "tmp/run-20261011-01/A11/drafts/probe-paid.png"
    ],
    "rounds": [],
    "unresolved_issues": [],
    "audit_summary": {
        "money": "Decimal ROUND_HALF_UP: lines 805.50/478.80/1160.00/1680.00 -> subtotal 4124.30; pre-tax 3944.30; tax exact 236.6580 -> 236.66; shipping 35.00; payable 4215.96 (generator asserts, restated in the page-2 caption)",
        "literal_lines": "monospace cell model (half 14px from L4, full 28px): all space cells empty, all glyph cells inked, right edges match; bearing-decomposed gaps = exactly 2 space cells for both L1 gaps, exactly 1 for every L2-L4 gap",
        "alignment": "unit/amount/totals right edges 968/1150/1150, payable 1151 (boxes 970/1152) - decimal points column-aligned",
        "page_identity": "header region max diff 0 and footer-left max diff 0 between the two final pages",
        "safe_margin": "ink bbox [48,76,1151,1525] on both pages, inside the 48px safe margin",
        "paid_baseline": "PAID latin groups share one bottom row; CJK hangs 6px (0.10em at size 60) below, matching three control lines at 0.077/0.094/0.115em - one shared natural baseline, payable unchanged",
        "emission": "renderer never decodes entities; '<' in content or Raw child -> PARSE_ERROR; Raw only inside Text; text attribute passes raw '<>&'; nested Text spans trim spaces (use Raw for ' / ')"
    }
}

with open("outputs/run-20261011-01/A11/task-metrics.json", "w", encoding="utf-8") as f:
    json.dump(m, f, ensure_ascii=False, indent=2)
    f.write("\n")
print("written", m["timings"]["ended_at"])
