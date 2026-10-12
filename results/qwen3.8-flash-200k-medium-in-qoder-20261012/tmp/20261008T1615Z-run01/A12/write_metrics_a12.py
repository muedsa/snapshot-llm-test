"""Assemble A12 task-metrics.json.

build_metrics.py derives counts from the logs but counts one dsl_version string per
(canvas, version) pair and stamps ended_at with the clock, so this script feeds it the
task window and then corrects the two fields that must come from the evidence instead:
`counts` (7 DSL versions per canvas, 28 requests = 4 x 7) and `timings.ended_at`
(newest delivered artifact, not "whenever this script happened to run").
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"]).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
TEMP = ROOT / "tmp" / RID / "A12"
OUT = ROOT / "outputs" / RID / "A12"
SCRIPTS = ROOT / "tmp" / RID / "_suite" / "scripts"

reqs = [json.loads(l) for l in (TEMP / "requests.jsonl").read_text(encoding="utf-8").splitlines()]
iters = [json.loads(l) for l in (TEMP / "iterations.jsonl").read_text(encoding="utf-8").splitlines()]
rep = json.loads((OUT / "check-report.json").read_text(encoding="utf-8"))
cmap = json.loads((OUT / "content-map.json").read_text(encoding="utf-8"))
shared = [json.loads(l) for l in (ROOT / "tmp" / RID / "_suite" / "requests.jsonl")
          .read_text(encoding="utf-8").splitlines()]

started = "2026-10-08T15:45:23.451380+00:00"          # _suite/events.jsonl task_started A12
first_img = min(r["ended_at"] for r in reqs if r["http_status"] == 200)
ended = max(datetime.fromtimestamp(p.stat().st_mtime, timezone.utc)
            for p in OUT.rglob("*") if p.is_file()).isoformat()

versions = sorted({r["dsl_version"].rsplit("-", 1)[0] for r in reqs})
crops = sorted(p.name for p in (TEMP / "preview" / "crops-final").glob("*.png"))

counts = {
    "snapshot_requests": len(reqs),
    "successful_snapshot_requests": len([r for r in reqs if r["http_status"] == 200]),
    "failed_snapshot_requests": len([r for r in reqs if r["http_status"] != 200]),
    "retry_requests": 0,
    "other_service_requests": 0,
    "dsl_versions": len(versions),
    "image_views": len([i for i in iters if i["image_viewed"]]),
    "completed_visual_iterations": len([i for i in iters
                                        if i["type"] == "visual" and i["completed"]]),
    "incomplete_visual_iterations": len([i for i in iters
                                         if i["type"] == "visual" and not i["completed"]]),
}
extra = {
    "timings": {
        "started_at": started,
        "ended_at": ended,
        "elapsed_seconds": round((datetime.fromisoformat(ended)
                                  - datetime.fromisoformat(started)).total_seconds(), 1),
        "first_usable_image_seconds": round((datetime.fromisoformat(first_img)
                                             - datetime.fromisoformat(started)).total_seconds(), 1),
        "user_feedback_wait_seconds": 0,
        "rate_limit_wait_seconds": None,
        "queue_wait_seconds": None,
        "request_duration_sum_seconds": round(sum(r["duration_seconds"] for r in reqs), 3),
        "requests_missing_duration": [r["request_id"] for r in reqs
                                      if r.get("duration_seconds") is None],
        "shared_doc_requests_reused": len(shared),
        "shared_doc_duration_seconds": round(sum(r["duration_seconds"] or 0
                                                 for r in shared), 3),
        "shared_doc_note": "文档抓取属 shared，只在 _suite 计一次；本题未新增文档请求，"
                           "版面结论全部来自本题 28 次渲染与本地度量",
        "server_timing_source": "Server-Timing response header captured in requests.jsonl "
                                "(28 次中 4 次 cache;desc=hit，其余 render;dur=…)",
        "note": "elapsed_seconds 含读题、写令牌表、求解器修正与看图判断，不等于请求耗时之和",
    },
    "counts": counts,
    "counts_detail": {
        "delivered_images": [f"outputs/{RID}/A12/{bp}.png"
                             for bp in ("mobile", "tablet", "desktop", "stage")],
        "usable_images": sorted(str(p.relative_to(ROOT)).replace("\\", "/")
                                for p in TEMP.glob("preview/v0*/*.png"))
                          + [f"outputs/{RID}/A12/{bp}.png"
                             for bp in ("mobile", "tablet", "desktop", "stage")],
        "unusable_requests": [],
        "iteration_type_breakdown": {
            "baseline": 3, "visual": 25, "self_check": 2, "retry": 0,
            "note": "iterations.jsonl 共 30 行；baseline 两条是渲染前的求解器修正（SLACK 盒宽、"
                    "余量杠杆），一条是 v01 手机基线；self_check 一条是 1.45em 下伸部发现，"
                    "一条是复核脚本自身的 glob 假失败",
        },
        "whole_image_opens": 16,
        "magnified_qa_crops": len(crops),
        "crop_evidence": [f"tmp/{RID}/A12/preview/crops-final/{c}" for c in crops],
        "image_view_events": [
            "preview/v01/{mobile,tablet,desktop,stage}.png（整图基线，四张）",
            "preview/v02/desktop.png（整图，side→band 重构后）",
            "preview/v03/{desktop,stage,mobile}.png（整图，CTA 并入 meta 行）",
            "preview/v04/{mobile,tablet,desktop,stage}.png（整图，meta 度量折行流）",
            "preview/v05/{mobile,tablet,desktop,stage}.png（整图，下伸部余量后；"
            "sha256 与交付 PNG 逐字节相同）",
            "preview/crops-final/ 10 张 2× 放大（mobile hero/cards/footer、"
            "tablet meta/C6、desktop line/C3、stage line/C4/footer）",
        ],
        "dsl_version_note": "dsl_versions=7 指每个断点的 7 个版本（v01/v02/v03/v04/v05/"
                            "final/final2）；请求数 28 = 4 断点 × 7 版本，"
                            "requests.jsonl 的 dsl_version 形如 v03-desktop",
        "fit_gate": {bp: {
            "gap_multiplier": c["layout"]["gap_multiplier"],
            "hero_h": c["layout"]["hero_h"],
            "meta_lines": c["layout"]["meta_block"],
            "cta_block": c["layout"]["cta_block"],
            "bottom_used": c["layout"]["bottom_used"],
            "bottom_limit": c["layout"]["limit"],
            "positioned_elements": cmap["layout_report"][bp]["positioned_elements"],
            "text_boxes": c["text_boxes"],
            "min_font_pt": min(r["font_pt"] for r in cmap["fields"][bp].values()),
            "ink_pixels_min": c["ink_pixels_min"],
            "png_bytes": c["png_bytes"],
            "dsl_bytes": c["dsl_bytes"],
            "served_by": c["served_by"],
        } for bp, c in rep["canvases"].items()},
        "audit": {"checker": f"tmp/{RID}/A12/check_a12.py",
                  "report": f"outputs/{RID}/A12/check-report.json",
                  "total_checks": rep["summary"]["total_checks"],
                  "passed": rep["summary"]["passed"],
                  "failures": rep["failures"],
                  "required_input_strings": rep["summary"]["required_strings"]},
    },
    "rounds": [],
    "unresolved_issues": ["无。已知约束：mobile 的 gap_multiplier 落在节奏带下限 0.5，"
                          "800px 高要装下 6 张完整卡片 + 3 行 meta + 页脚；再加内容只能放宽"
                          "卡片行数或允许卡内换行，不能继续压缩节奏带"],
    "outputs": ["mobile.png", "mobile.snapshot", "tablet.png", "tablet.snapshot",
                "desktop.png", "desktop.snapshot", "stage.png", "stage.snapshot",
                "design-tokens.json", "content-map.json", "check-report.json",
                "snapshot-usage.md", "task-metrics.json", "requests/"],
    "stop_reason": "四张断点画布（360×800/768×1024/1440×900/1920×1080）由同一份 content.json 与"
                   "同一张令牌表生成，19 条输入字符串逐字保留、无缩写；check_a12.py 对交付字节"
                   " 60/60 通过，并完成 16 次整图与 10 次 2× 放大复核",
}
(TEMP / "metrics-extra.json").write_text(json.dumps(extra, ensure_ascii=False, indent=1),
                                         encoding="utf-8")

cmd = [sys.executable, str(SCRIPTS / "build_metrics.py"), "--task", "A12",
       "--status", "completed", "--started", started, "--first-image", first_img,
       "--extra", str(TEMP / "metrics-extra.json"),
       "--stop-reason", extra["stop_reason"]]
print(subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                     env={**os.environ, "SNAPSHOT_TASK_ROOT": str(ROOT),
                          "SNAPSHOT_RUN_ID": RID}).stdout)
m = json.loads((OUT / "task-metrics.json").read_text(encoding="utf-8"))
print(json.dumps({"timings": m["timings"]["elapsed_seconds"],
                  "ended": m["timings"]["ended_at"], "counts": m["counts"],
                  "keys": list(m)}, ensure_ascii=False))
