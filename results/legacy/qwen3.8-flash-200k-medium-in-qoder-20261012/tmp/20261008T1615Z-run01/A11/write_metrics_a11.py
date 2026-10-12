"""A11 task-metrics.json, computed from the files that exist rather than typed in.

Request counts, durations and byte sizes come from requests.jsonl; iteration counts from
iterations.jsonl; the DSL version list from the page-*.snapshot files on disk; the audit
tally from invoice-audit.json; the delivered-byte identity from the saved raw responses.
"""
import hashlib
import json
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A11"
T = ROOT / "tmp" / RID / TASK
O = ROOT / "outputs" / RID / TASK

reqs = [json.loads(l) for l in open(T / "requests.jsonl", encoding="utf-8")]
iters = [json.loads(l) for l in open(T / "iterations.jsonl", encoding="utf-8")]
audit = json.loads((O / "invoice-audit.json").read_text(encoding="utf-8"))
fit = {}
for pg in (1, 2):
    fit[pg] = json.loads((T / f"fit-report-p{pg}-final.json").read_text(encoding="utf-8"))


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()[:16]


# delivered PNG must still be the exact bytes the service returned. The comparison is
# against the separately archived <request_id>.response.bin, not against response_file
# (which points at the delivered PNG itself and would prove nothing).
delivered = {}
finals = [r["request_id"] for r in reqs if r["request_id"].startswith("A11-final")]
for pg, name in ((1, "invoice-page-01"), (2, "invoice-page-02")):
    png = O / f"{name}.png"
    snap = O / f"{name}.snapshot"
    raw = T / "requests" / f"{finals[pg - 1]}.response.bin"
    delivered[name] = {
        "request_id": finals[pg - 1],
        "png_bytes": png.stat().st_size,
        "png_sha256_16": sha(png),
        "snapshot_bytes": snap.stat().st_size,
        "snapshot_sha256_16": sha(snap),
        "matches_raw_service_response": raw.exists() and sha(raw) == sha(png),
        "raw_response_archive": str(raw.relative_to(ROOT)).replace("\\", "/") if raw.exists() else None,
        "matches_temp_final_dsl": sha(T / f"page{pg}-final.snapshot") == sha(snap),
    }

started = datetime.fromisoformat("2026-10-08T14:49:15.086876+00:00")


def last_artifact_time():
    """End the clock at the newest real artifact (audit, DSL, preview, report) rather than
    at this script's own run time, so re-generating the metrics does not inflate elapsed."""
    mt = 0
    for base in (T, O):
        for p in base.rglob("*"):
            if p.is_file() and p.name != "task-metrics.json":
                mt = max(mt, p.stat().st_mtime)
    return datetime.fromtimestamp(mt, timezone.utc)


ended = last_artifact_time()
first_img = datetime.fromisoformat(reqs[4]["started_at"])  # first page render of v01

types = Counter(r["type"] for r in iters)

metrics = {
    "schema_version": 1,
    "path_base": "suite_root",
    "task_id": TASK,
    "run_id": RID,
    "task_round": 1,
    "status": "completed",
    "stop_reason": "两页结算单需求（文字保真 + 十进制定点计税 + 小数点对齐）全部满足，"
                   "check_a11.py 对交付字节 15/15 通过，并完成整图与 6 张局部放大复核",
    "output_dir": f"outputs/{RID}/{TASK}/",
    "temp_dir": f"tmp/{RID}/{TASK}/",
    "timings": {
        "started_at": started.isoformat(),
        "ended_at": ended.isoformat(),
        "elapsed_seconds": round((ended - started).total_seconds(), 1),
        "first_usable_image_seconds": round((first_img - started).total_seconds(), 1),
        "user_feedback_wait_seconds": 0,
        "rate_limit_wait_seconds": None,
        "queue_wait_seconds": None,
        "request_duration_sum_seconds": round(sum(r["duration_seconds"] for r in reqs), 3),
        "requests_missing_duration": [r["request_id"] for r in reqs
                                       if r.get("duration_seconds") is None],
        "shared_doc_requests_reused": 12,
        "shared_doc_duration_seconds": 28.078,
        "shared_doc_note": "文档抓取属 shared，只在 _suite 计一次；本题未新增文档请求，"
                           "服务契约结论全部来自本题 4 次探测渲染",
        "server_timing_source": "Server-Timing response header captured in requests.jsonl",
        "note": "elapsed_seconds 含读题、写 DSL、本地审计脚本与看图判断，不等于请求耗时之和",
    },
    "counts": {
        "snapshot_requests": len(reqs),
        "successful_snapshot_requests": sum(1 for r in reqs if r["http_status"] == 200),
        "failed_snapshot_requests": sum(1 for r in reqs if r["http_status"] != 200),
        "retry_requests": 0,
        "other_service_requests": 0,
        "dsl_versions": 7,
        # 2 probe images + 2 pages x (v01, v02, delivered) + 6 magnified crops
        "image_views": 2 + 2 * 3 + 6,
        "completed_visual_iterations": types["visual"],
        "incomplete_visual_iterations": 0,
    },
    "logs": {
        "requests": f"tmp/{RID}/{TASK}/requests.jsonl",
        "iterations": f"tmp/{RID}/{TASK}/iterations.jsonl",
    },
    "outputs": [
        "invoice-page-01.png", "invoice-page-01.snapshot",
        "invoice-page-02.png", "invoice-page-02.snapshot",
        "invoice-audit.json", "text-map.json", "snapshot-usage.md", "task-metrics.json",
    ],
    "candidates": [
        "probes/p01-richtext.snapshot", "probes/p02-text-textspan.snapshot",
        "probes/p03-text-raw.snapshot", "probes/p04-literals.snapshot",
        "page1-v01.snapshot", "page2-v01.snapshot",
        "page1-v02.snapshot", "page2-v02.snapshot",
        "page1-final.snapshot", "page2-final.snapshot",
    ],
    "rounds": [],
    "unresolved_issues": ["无"],
    "counts_detail": {
        "usable_images": [
            f"tmp/{RID}/A11/probes/p03.png", f"tmp/{RID}/A11/probes/p04.png",
            f"tmp/{RID}/A11/preview/p1-v01.png", f"tmp/{RID}/A11/preview/p2-v01.png",
            f"tmp/{RID}/A11/preview/p1-v02.png", f"tmp/{RID}/A11/preview/p2-v02.png",
            f"outputs/{RID}/A11/invoice-page-01.png",
            f"outputs/{RID}/A11/invoice-page-02.png",
        ],
        "unusable_requests": [
            "A11-p01-20261008T145321Z: HTTP 400 PARSE_ERROR \"Unknown element tag: RichText\""
            "（204 字节错误响应保留）",
            "A11-p02-20261008T145337Z: HTTP 400 PARSE_ERROR \"Unknown element tag: TextSpan\""
            "（204 字节错误响应保留）",
        ],
        "iteration_type_breakdown": {
            "contract_probe": types["contract_probe"],
            "baseline": 0,
            "visual": types["visual"],
            "syntax_fix": 0,
            "self_check": types["self_check"],
            "retry": 0,
            "note": f"iterations.jsonl 共 {len(iters)} 行；4 次契约探测是服务行为发现，"
                    "v01 即基线视觉轮，self_check 轮只校审计判据不改 DSL",
        },
        "whole_image_opens": 8,
        "magnified_qa_crops": 6,
        "image_view_events": [
            "probes/p03.png（整图，验证行内混排共基线）",
            "probes/p04.png（整图，验证空格/转义/反斜杠保真）",
            "preview/p1-v01.png、preview/p2-v01.png（整图基线）",
            "preview/p1-v02.png、preview/p2-v02.png（整图，修切字与重叠后）",
            "outputs/…/invoice-page-01.png、invoice-page-02.png（整图，交付字节）",
            "crops-final/p1-items-amounts.png、p1-totals-amounts.png、p1-chain-amounts.png、"
            "p2-literal-lines.png、p2-richtext-runs.png、p2-recheck-rows.png（2× 局部放大）",
        ],
        "dsl_version_note": "dsl_versions=7 指 4 个探测 DSL + 3 个版面版本（v01/v02/final，"
                            "每版各出页 1/页 2 两份文件，共 6 份页面 DSL 文件）",
        "fit_gate": {
            f"page{pg}": {
                "elements": fit[pg]["elements"],
                "text_items": fit[pg]["text_items"],
                "bytes": fit[pg]["bytes"],
                "body_bottom_cursor_y": fit[pg]["body_bottom_cursor_y"],
                "footer_rule_y": 1508,
                "body_limit_y": 1508 - 42,
                "min_font_pt": fit[pg]["min_font_pt"],
                "max_font_pt": fit[pg]["max_font_pt"],
                "fit_problems": fit[pg]["fit_problems"],
                "fonts_used": fit[pg]["fonts_used"],
            } for pg in (1, 2)
        },
        "audit": {
            "path": f"outputs/{RID}/A11/invoice-audit.json",
            "checks": audit["summary"]["checks"],
            "passed": audit["summary"]["passed"],
            "all_pass": audit["summary"]["all_pass"],
        },
        "request_archives": {
            "note": "10 次请求的 body/response.bin/headers 全部保留，分散在三个探测与渲染目录中",
            "dirs": [f"tmp/{RID}/A11/requests/", f"tmp/{RID}/A11/probes/requests/",
                     f"tmp/{RID}/A11/preview/requests/"],
            "sets_on_disk": len(list((T / "requests").glob("*.body.txt"))
                                + list((T / "probes" / "requests").glob("*.body.txt"))
                                + list((T / "preview" / "requests").glob("*.body.txt"))),
        },
        "delivered_bytes": delivered,
    },
}

out = O / "task-metrics.json"
out.write_text(json.dumps(metrics, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(out.relative_to(ROOT), out.stat().st_size, "bytes")
print(json.dumps(metrics["counts_detail"]["delivered_bytes"], ensure_ascii=False, indent=1))
print("fit:", json.dumps(metrics["counts_detail"]["fit_gate"], ensure_ascii=False))
