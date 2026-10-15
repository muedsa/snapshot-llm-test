#!/usr/bin/env python
"""B03 · 生成 task-metrics.json（从 requests.jsonl / iterations.jsonl 汇总）。"""
from __future__ import annotations

import datetime
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
sys.path.insert(0, str(ROOT / "tmp/run-20261011-01/_suite/scripts"))
import finalize_task as ft  # noqa: E402
import suite_log as sl      # noqa: E402

TASK = "B03"
OUTD, TEMPD = ft.task_dirs(TASK)
reqs = sl.read_jsonl(ROOT / f"{TEMPD}/requests.jsonl")
its = sl.read_jsonl(ROOT / f"{TEMPD}/iterations.jsonl")

PROBE_RE = __import__("re").compile(r"^[pqrs]\d{2}-")


def per_case():
    out = {}
    for r in reqs:
        ver = r.get("version") or ""
        cid = r.get("case_id") or ver
        if PROBE_RE.match(ver):
            cid = "shared-probes"
        e = out.setdefault(cid, {"render": 0, "render_ok": 0, "render_fail": 0,
                                 "retry": 0, "seconds": 0.0, "versions": []})
        if r.get("request_type") == "render":
            e["render"] += 1
            if r.get("status") == 200 and not r.get("error") and (r.get("response_bytes") or 0) > 0:
                e["render_ok"] += 1
            else:
                e["render_fail"] += 1
            if r.get("extra", {}).get("is_retry"):
                e["retry"] += 1
            if ver not in e["versions"]:
                e["versions"].append(ver)
        e["seconds"] += float(r.get("duration_seconds") or 0)
    for i in its:
        cid = i.get("case_id") or (i.get("extra") or {}).get("case_id") \
            or i.get("version") or "?"
        e = out.setdefault(cid, {"render": 0, "render_ok": 0, "render_fail": 0,
                                 "retry": 0, "seconds": 0.0, "versions": []})
        e.setdefault("views", 0)
        e.setdefault("visual_iters", 0)
        e["views"] += 1
        if i.get("kind") == "visual" and i.get("completed"):
            e["visual_iters"] += 1
    return out


def main() -> None:
    pc = per_case()
    started = min((r.get("started_at") for r in reqs if r.get("started_at")), default=None)
    ended = max((r.get("ended_at") for r in reqs if r.get("ended_at")), default=None)
    shared = pc.pop("shared-probes", {"render": 0, "render_ok": 0, "render_fail": 0,
                                       "retry": 0, "seconds": 0.0, "versions": []})
    cases = []
    drafts = ROOT / f"{TEMPD}/drafts"
    for cid in sorted(k for k in pc if k.startswith("case-")):
        e = pc[cid]
        n = len(list(drafts.glob(f"*{cid}-v*.snapshot"))) if drafts.exists() else 0
        cases.append({
            "case_id": cid,
            "dsl_drafts_retained": n,
            "delivered_dsl": f"{OUTD}/{cid}/final.snapshot",
            "render_requests": e["render"],
            "render_ok": e["render_ok"],
            "render_failed": e["render_fail"],
            "retry_requests": e["retry"],
            "image_views": e.get("views", 0),
            "completed_visual_iterations": e.get("visual_iters", 0),
            "request_duration_sum_seconds": round(e["seconds"], 3),
        })

    started_dt = sl.datetime.fromisoformat(started)
    ended_dt = sl.datetime.fromisoformat(ended)
    total = {
        "schema_version": 1,
        "path_base": "suite_root",
        "task_id": TASK,
        "run_id": os.environ.get("SNAPSHOT_RUN_ID", "run-20261011-01"),
        "status": "completed",
        "output_dir": OUTD,
        "temp_dir": TEMPD,
        "timings": {
            "started_at": started,
            "ended_at": ended,
            "elapsed_seconds": round((ended_dt - started_dt).total_seconds(), 3),
            "first_usable_image_seconds": round(
                (sl.datetime.fromisoformat(
                    min((r["ended_at"] for r in reqs
                         if r.get("request_type") == "render" and r.get("status") == 200),
                    default=ended)) - started_dt).total_seconds(), 3),
            "user_feedback_wait_seconds": 0,
            "rate_limit_wait_seconds": 0,
            "queue_wait_seconds": None,
            "request_duration_sum_seconds": round(
                sum(float(r.get("duration_seconds") or 0) for r in reqs), 3),
            "note": "墙钟时间为渲染请求时间跨度之和的量级参考，不等于人工工作时间；"
                    "本任务无外部反馈等待，无排队概念（queue 为 null），"
                    "未观察到 429/503，故 rate_limit_wait 为 0。",
        },
        "shared_preparation": {
            "scope": "能力边界探针（probe/probe2/probe3/probe4 四轮）+ 共用构件库",
            "render_requests": shared["render"],
            "render_ok": shared["render_ok"],
            "render_failed": shared["render_fail"],
            "retry_requests": shared["retry"],
            "dsl_versions": len(shared["versions"]),
            "request_duration_sum_seconds": round(shared["seconds"], 3),
        },
        "per_case": cases,
        "counts": {
            "final_cases": len(cases),
            "final_png": len(cases),
            "snapshot_render_requests": sum(r.get("request_type") == "render" for r in reqs),
            "successful_render_requests": sum(
                r.get("request_type") == "render" and r.get("status") == 200
                and not r.get("error") and (r.get("response_bytes") or 0) > 0 for r in reqs),
            "failed_render_requests": sum(
                1 for r in reqs if r.get("request_type") == "render"
                and not (r.get("status") == 200 and not r.get("error")
                         and (r.get("response_bytes") or 0) > 0)),
            "retry_requests": sum(1 for r in reqs
                                  if (r.get("extra") or {}).get("is_retry")),
            "other_service_requests": sum(
                1 for r in reqs if r.get("request_type") != "render"),
            "document_fetches_this_task": 0,
            "document_fetches_note": "官方文档页与 /fonts 列表在本 run 的共享准备里已取得"
                                      "（tmp/run-20261011-01/_suite/fonts-list.txt 等），"
                                      "本次直接复用，未重复发起请求。",
            "image_views": sum(c["image_views"] for c in cases),
            "completed_visual_iterations": sum(c["completed_visual_iterations"]
                                               for c in cases),
            "dsl_versions_delivered": sum(c["dsl_drafts_retained"] for c in cases),
        },
        "iteration_breakdown": {
            "baseline": sum(1 for i in its if i.get("kind") == "baseline"),
            "visual": sum(1 for i in its if i.get("kind") == "visual"),
            "syntax_fix": sum(1 for i in its if i.get("kind") == "syntax-fix"),
            "retry": sum(1 for i in its if i.get("kind") == "retry"),
            "alternative": sum(1 for i in its if i.get("kind") == "alternative"),
            "requirement_change": sum(1 for i in its if i.get("kind") == "requirement-change"),
        },
        "logs": {"requests": f"{TEMPD}/requests.jsonl",
                 "iterations": f"{TEMPD}/iterations.jsonl",
                 "tool_usage": f"{TEMPD}/tool-usage.jsonl",
                 "capability_findings": f"{TEMPD}/capability-findings.md",
                 "plan": f"{TEMPD}/plan-v1.md",
                 "generation_scripts": f"{TEMPD}/pieces/",
                 "probe_scripts": f"{TEMPD}/probe_b03_accept*.py",
                 "probe_images": f"{TEMPD}/probe*/"},
        "outputs": [f"{OUTD}/{c}" for c in (
            "case-01", "case-02", "case-03", "case-04", "case-05",
            "case-06", "case-07", "case-08", "case-09", "case-10")],
        "root_outputs": [f"{OUTD}/{f}" for f in (
            "portfolio.json", "portfolio.md", "gallery.md", "snapshot-usage.md",
            "technique-notes.md", "task-metrics.json")],
        "unresolved_issues": [
            "文字精确度量仍靠系数估算；ASCII 小写与斜体在不同字体下差异较大，"
            "已用 1.18 余量系数与生成期断言缓解，但不是根治。",
            "letterSpacing 逐行齐尾只对完全自己排版的单行/手动分行有效；"
            "若要让服务端断行的段落既齐尾又可控，仍缺实测断行位置。",
            "BackdropFilter 在子树带阴影溢出时的实际作用范围未验证（本次卡片均无溢出）。",
        ],
    }
    (ROOT / OUTD / "task-metrics.json").write_text(
        json.dumps(total, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(total["counts"], ensure_ascii=False, indent=2))
    print("timings:", json.dumps(total["timings"], ensure_ascii=False, indent=2))
    print("shared:", json.dumps(total["shared_preparation"], ensure_ascii=False))


if __name__ == "__main__":
    main()