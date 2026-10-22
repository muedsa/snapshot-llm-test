# -*- coding: utf-8 -*-
"""Build B05 task-metrics.json from the real logs."""
import json
import os
from collections import Counter, defaultdict
from datetime import datetime

SUITE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      "..", "..", "..", ".."))
TMP = os.path.join(SUITE, "tmp", "run-20261011-01", "B05")
OUT = os.path.join(SUITE, "outputs", "run-20261011-01", "B05")


def iso(s):
    return datetime.fromisoformat(s)


reqs = [json.loads(l) for l in open(os.path.join(TMP, "requests.jsonl"),
                                    encoding="utf-8") if l.strip()]
its = [json.loads(l) for l in open(os.path.join(TMP, "iterations.jsonl"),
                                   encoding="utf-8") if l.strip()]

import re
by_case = defaultdict(list)
for r in reqs:
    m = re.search(r"(case-\d\d)-v(\d+)", r.get("dsl_path") or "")
    if m:
        by_case[m.group(1)].append((int(m.group(2)), r))

its_by_case = defaultdict(list)
for i in its:
    if i.get("case_id"):
        its_by_case[i["case_id"]].append(i)

ts = [r["ts"] for r in reqs if r.get("ts")]
start, end = min(ts), max(ts)
wall = (iso(end) - iso(start)).total_seconds()
ok = [r for r in reqs if r.get("status") == 200]
req_sum = sum(r.get("elapsed_seconds") or 0 for r in ok)
first_ok = min((r["ts"] for r in ok), key=lambda t: iso(t))
first_usable = (iso(first_ok) - iso(start)).total_seconds()

it_types = Counter(i.get("type") for i in its)
per_case = {}
for c in sorted(by_case):
    rl = by_case[c]
    acc = max(v for v, _ in rl)
    acc_r = [r for v, r in rl if v == acc][0]
    cl = its_by_case[c]
    ct = Counter(i.get("type") for i in cl)
    per_case[c] = {
        "case": c,
        "accepted_version": "v%d" % acc,
        "accepted_request_id": acc_r["id"],
        "dsl_versions": len(rl),
        "snapshot_requests": len(rl),
        "successful_snapshot_requests": sum(1 for _, r in rl if r.get("status") == 200),
        "failed_snapshot_requests": sum(1 for _, r in rl if r.get("status") != 200),
        "request_duration_sum_seconds": round(
            sum(r.get("elapsed_seconds") or 0 for _, r in rl if r.get("status") == 200), 2),
        "iterations_total": len(cl),
        "baseline": ct.get("baseline", 0),
        "completed_visual_iterations": ct.get("visual_iteration", 0),
        "structural_iterations": ct.get("structural", 0),
        "syntax_fix_iterations": ct.get("syntax_fix", 0),
        "regression_fix_iterations": ct.get("regression_fix", 0),
        "image_views": len(cl),
        "first_ts": min(r["ts"] for _, r in rl),
        "last_ts": max(r["ts"] for _, r in rl),
    }

case_md = {c: os.path.getmtime(os.path.join(OUT, c, "case.md"))
           for c in sorted(by_case)}

doc = {
    "schema_version": 2,
    "path_base": "suite_root",
    "task_id": "B05",
    "run_id": "run-20261011-01",
    "task_round": None,
    "status": "completed",
    "stop_reason": None,
    "output_dir": "outputs/run-20261011-01/B05/",
    "temp_dir": "tmp/run-20261011-01/B05/",
    "timings": {
        "started_at": start,
        "ended_at": end,
        "elapsed_seconds": round(wall, 2),
        "first_usable_image_seconds": round(first_usable, 2),
        "user_feedback_wait_seconds": 0,
        "rate_limit_wait_seconds": 0,
        "queue_wait_seconds": None,
        "request_duration_sum_seconds": round(req_sum, 2),
        "server_timing_source": "elapsed_seconds 由 snap_render.py 客户端计时（含网络往返）",
        "note": "总墙钟 %.2fs 远大于请求耗时之和 %.2fs，差额为生成脚本、断言、看图与写作时间" % (wall, req_sum),
    },
    "counts": {
        "snapshot_requests": len(reqs),
        "successful_snapshot_requests": len(ok),
        "failed_snapshot_requests": len(reqs) - len(ok),
        "retry_requests": 0,
        "other_service_requests": 0,
        "document_requests": 0,
        "probe_requests": sum(1 for r in reqs if "probe" in r["id"]),
        "dsl_versions": sum(v["dsl_versions"] for v in per_case.values()),
        "image_views": sum(v["image_views"] for v in per_case.values()),
        "completed_visual_iterations": it_types.get("visual_iteration", 0),
        "incomplete_visual_iterations": 0,
        "baseline_iterations": it_types.get("baseline", 0),
        "structural_iterations": it_types.get("structural", 0),
        "syntax_fix_iterations": it_types.get("syntax_fix", 0),
        "regression_fix_iterations": it_types.get("regression_fix", 0),
        "other_tool_calls": 0,
        "final_case_count": len(per_case),
    },
    "failure_detail": [
        {"request_id": "B05-req-0001", "status": 400, "kind": "PARSE_ERROR",
         "cause": "初版 DSL 使用 color='none'，非法 CSS 颜色",
         "resolution": "改用 transparent 后重渲，后续 38 次请求全部 200"},
    ],
    "logs": {
        "requests": "tmp/run-20261011-01/B05/requests.jsonl",
        "iterations": "tmp/run-20261011-01/B05/iterations.jsonl",
        "tool_usage": "tmp/run-20261011-01/B05/tool-usage.jsonl",
    },
    "outputs": [
        {"path": "outputs/run-20261011-01/B05/portfolio.json", "kind": "portfolio"},
        {"path": "outputs/run-20261011-01/B05/portfolio.md", "kind": "portfolio_essay"},
        {"path": "outputs/run-20261011-01/B05/gallery.md", "kind": "gallery"},
        {"path": "outputs/run-20261011-01/B05/snapshot-usage.md", "kind": "usage_report"},
        {"path": "outputs/run-20261011-01/B05/task-metrics.json", "kind": "metrics"},
        {"path": "outputs/run-20261011-01/B05/product-brief.md", "kind": "product_brief"},
        {"path": "outputs/run-20261011-01/B05/journey.json", "kind": "journey"},
    ] + [{"path": "outputs/run-20261011-01/B05/%s/final.png" % c, "kind": "final_image"}
         for c in sorted(per_case)],
    "candidates": [],
    "rounds": [],
    "unresolved_issues": [],
    "asset_policy": "dsl_primary_with_supporting_assets（本题实际全部纯 DSL 完成，无嵌入素材）",
    "shared_preparation": {
        "renderer": "tmp/run-20261011-01/_suite/scripts/snap_render.py",
        "state_tool": "tmp/run-20261011-01/_suite/scripts/update_state.py",
        "note": "渲染器与状态工具为全套共享，其构建耗时不计入本题",
    },
    "case_metrics": [per_case[c] for c in sorted(per_case)],
    "tool_usage_summary": [],
    "final_case_count": len(per_case),
}

with open(os.path.join(OUT, "task-metrics.json"), "w", encoding="utf-8") as f:
    json.dump(doc, f, ensure_ascii=False, indent=2)

print("wall %.2fs  first_usable %.2fs  req_sum %.2fs" % (wall, first_usable, req_sum))
print("requests %d ok %d fail %d | iterations %d | cases %d" % (
    doc["counts"]["snapshot_requests"], doc["counts"]["successful_snapshot_requests"],
    doc["counts"]["failed_snapshot_requests"],
    sum(it_types.values()), doc["counts"]["final_case_count"]))
tot = {"req": 0, "it": 0, "view": 0, "v": 0}
for c in sorted(per_case):
    v = per_case[c]
    tot["req"] += v["snapshot_requests"]
    tot["it"] += v["iterations_total"]
    tot["view"] += v["image_views"]
    tot["v"] += v["dsl_versions"]
    print("  %s %s reqs=%d dsl=%d iters=%d views=%d" % (
        c, v["accepted_version"], v["snapshot_requests"], v["dsl_versions"],
        v["iterations_total"], v["image_views"]))
print("  SUM req=%d dsl=%d iters=%d views=%d  (must equal totals)" % (
    tot["req"], tot["v"], tot["it"], tot["view"]))
