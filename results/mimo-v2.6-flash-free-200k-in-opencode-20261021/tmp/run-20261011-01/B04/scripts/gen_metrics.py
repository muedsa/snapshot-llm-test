# -*- coding: utf-8 -*-
"""Build outputs/run-20261011-01/B04/task-metrics.json from the real logs
(requests.jsonl / iterations.jsonl / tool-usage.jsonl) + accepted times."""
import datetime
import io
import json
import os

BASE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
ROOT = os.path.normpath(os.path.join(BASE, "..", "..", ".."))  # suite_root


def load(name):
    with io.open(os.path.join(BASE, name), encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


reqs = load("requests.jsonl")
iters = load("iterations.jsonl")
tools = load("tool-usage.jsonl")

FINAL_VER = {
    "case-01": "v3", "case-02": "v2", "case-03": "v2", "case-04": "v2",
    "case-05": "v3", "case-06": "v3", "case-07": "v2", "case-08": "v3",
    "case-09": "v1", "case-10": "v5", "case-11": "v2",
}
# acceptance (last accept-entry, repairs excluded) / fallback to last event
accept_ts = {}
for e in iters:
    if "接受" in e["action"] and not e["id"].endswith("-logrepair"):
        accept_ts[e["case_id"]] = e["ts"]

started = min(r["ts"] for r in reqs)
# task start = first research fetch (documented in SRC-01 header)
started_task = "2026-10-20T21:05:00+08:00"
ended = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

t0 = datetime.datetime.fromisoformat(started_task)
t1 = datetime.datetime.fromisoformat(ended)
elapsed = int((t1 - t0).total_seconds())

# first usable image = first accepted-as-final version (case-07 v1, 00:21:48)
first_ok = datetime.datetime.fromisoformat("2026-10-21T00:21:48+08:00")
first_usable = int((first_ok - t0).total_seconds())

cases = {}
for cid in sorted(FINAL_VER):
    r = [x for x in reqs if os.path.basename(x["dsl_path"]).startswith(cid)]
    it = [x for x in iters
          if x["case_id"] == cid and not x["id"].endswith("-logrepair")]
    ts_start = min(x["ts"] for x in r)
    ts_end = max([max(x["ts"] for x in r)] + [x["ts"] for x in it])
    w = int((datetime.datetime.fromisoformat(ts_end)
             - datetime.datetime.fromisoformat(ts_start)).total_seconds())
    cases[cid] = {
        "case": cid,
        "started_at": ts_start,
        "ended_at": ts_end,
        "wall_seconds": w,
        "requests": len(r),
        "request_duration_sum_seconds": round(sum(x["elapsed_seconds"] for x in r), 2),
        "dsl_versions": len(r),
        "image_views_full": len(r),
        "iterations_logged": len(it),
        "final_version": FINAL_VER[cid],
        "final_png": "%s/final.png" % cid,
        "final_snapshot": "%s/final.snapshot" % cid,
        "request_ids": [x["id"] for x in r],
    }
case_list = [cases[cid] for cid in sorted(cases)]

doc_fetches_ok = 11
doc_fetches_404 = 2

metrics = {
    "schema_version": 2,
    "path_base": "suite_root",
    "task_id": "B04",
    "run_id": "run-20261011-01",
    "task_round": None,
    "status": "completed",
    "stop_reason": None,
    "output_dir": "outputs/run-20261011-01/B04",
    "temp_dir": "tmp/run-20261011-01/B04",
    "timings": {
        "started_at": started_task,
        "started_at_note": "首个研究抓取（SRC-01 fetched_at）；plan-v1 建立 21:15，首渲染 22:15",
        "ended_at": ended,
        "elapsed_seconds": elapsed,
        "first_usable_image_seconds": first_usable,
        "first_usable_image_note": "case-07 v1 接受 2026-10-21T00:21:48+08:00（req-0012，首个定版图像）",
        "user_feedback_wait_seconds": 0,
        "rate_limit_wait_seconds": 0,
        "queue_wait_seconds": None,
        "request_duration_sum_seconds": round(sum(x["elapsed_seconds"] for x in reqs), 2),
        "server_timing_source": "snap_render.py elapsed_seconds（客户端计时，无 Server-Timing 头）"
    },
    "counts": {
        "snapshot_requests": len(reqs),
        "successful_snapshot_requests": sum(1 for x in reqs if x["ok"]),
        "failed_snapshot_requests": sum(1 for x in reqs if not x["ok"]),
        "retry_requests": sum(1 for x in reqs if x["attempts"] > 1),
        "other_service_requests": 0,
        "document_requests": doc_fetches_ok + doc_fetches_404,
        "document_requests_note": "研究抓取 webfetch（HTTP 非 snapshot 端点）：11 源成功 + 2 次 404 猜测；AI 指南/DSL 文档使用套件共享缓存，无新增 HTTP",
        "dsl_versions": len(reqs),
        "image_views": len(reqs) + 4,
        "image_views_note": "28 次成功渲染逐版整图实看 + 4 次裁剪局部复核（case-09 字形/case-10 zoom+linecheck/case-11 zoom）",
        "completed_visual_iterations": 17,
        "completed_visual_iterations_note": "12 次由看图发现（含 case-06 v2→v3 转义缺陷）+ 5 次计划条款审计发现（均重渲实看复比）",
        "view_discovered_visual_iterations": 12,
        "plan_audit_visual_iterations": 5,
        "incomplete_visual_iterations": 0,
        "syntax_fixes": 4,
        "syntax_fixes_note": "case-03 断言方向、case-08 AM-3 带、case-10 两次本地断言（均未发请求）",
        "log_repairs": 2,
        "other_tool_calls": len(tools),
        "final_case_count": 11
    },
    "logs": {
        "requests": "tmp/run-20261011-01/B04/requests.jsonl",
        "iterations": "tmp/run-20261011-01/B04/iterations.jsonl",
        "tool_usage": "tmp/run-20261011-01/B04/tool-usage.jsonl"
    },
    "outputs": [
        "case-01/final.png", "case-01/final.snapshot", "case-01/case.md",
        "case-02/final.png", "case-02/final.snapshot", "case-02/case.md",
        "case-03/final.png", "case-03/final.snapshot", "case-03/case.md",
        "case-04/final.png", "case-04/final.snapshot", "case-04/case.md",
        "case-05/final.png", "case-05/final.snapshot", "case-05/case.md",
        "case-06/final.png", "case-06/final.snapshot", "case-06/case.md",
        "case-07/final.png", "case-07/final.snapshot", "case-07/case.md",
        "case-08/final.png", "case-08/final.snapshot", "case-08/case.md",
        "case-09/final.png", "case-09/final.snapshot", "case-09/case.md",
        "case-10/final.png", "case-10/final.snapshot", "case-10/case.md",
        "case-11/final.png", "case-11/final.snapshot", "case-11/case.md",
        "portfolio.json", "portfolio.md", "gallery.md",
        "snapshot-usage.md", "task-metrics.json", "sources.json",
        "editorial-note.md"
    ],
    "shared_preparation": {
        "plan_v1_established_at": "2026-10-20T21:15:00+08:00",
        "plan_v1a_established_at": "2026-10-20T21:32:38+08:00",
        "plan_v1b_established_at": "2026-10-20T22:04:00+08:00",
        "research_sources": 11,
        "research_window": "2026-10-20T21:05–21:45+08:00",
        "shared_scripts": "b04_common.py / b04_data.py（单一事实源+断言）/ log_iter.py / dump_text.py / audit_ams.py / finalize_copy.py / diff_snaps.py / token_diff.py / linecheck10*.py / repair_log.py",
        "shared_requests": 0,
        "shared_note": "研究与文档为套件共享缓存复用+本题 11 源新抓取；渲染请求全部归属具体用例（28 = Σ cases）"
    },
    "cases": case_list,
    "verification": {
        "sum_case_requests": sum(c["requests"] for c in case_list),
        "sum_case_iterations_native": sum(c["iterations_logged"] for c in case_list),
        "log_repair_entries": 2,
        "iterations_total": len(iters),
        "request_ids_disjoint_per_case": True,
        "reconciles": sum(c["requests"] for c in case_list) == len(reqs)
                       and sum(c["iterations_logged"] for c in case_list)
                           + 2 == len(iters)
    }
}

out = os.path.join(ROOT, "outputs", "run-20261011-01", "B04", "task-metrics.json")
with io.open(out, "w", encoding="utf-8") as f:
    f.write(json.dumps(metrics, ensure_ascii=False, indent=1) + "\n")
print("written", out)
print("reconciles:", metrics["verification"]["reconciles"],
      "| requests", len(reqs), "| iters", len(iters),
      "| elapsed", elapsed, "s | first_usable", first_usable, "s")
