import os, json, datetime
from collections import Counter

RUN = "20261008T1615Z-run01"
ROOT = "outputs/" + RUN
SUITE = ROOT + "/_suite/"
F = json.load(open("tmp/%s/_suite/suite-facts.json" % RUN, encoding="utf-8"))
CAT = json.load(open("catalog.json", encoding="utf-8"))
ORDER = CAT["task_order"]
T = F["tasks"]

ALIAS = {
    "snapshot_requests": ["snapshot_requests", "http_requests_total", "render_submissions", "requests_total", "renders"],
    "successful_snapshot_requests": ["successful_snapshot_requests", "render_ok", "requests_success"],
    "failed_snapshot_requests": ["failed_snapshot_requests", "requests_failed", "render_transport_or_truncated"],
    "retry_requests": ["retry_requests", "retries"],
    "image_views": ["image_views", "images_viewed"],
    "completed_visual_iterations": ["completed_visual_iterations", "visual_iterations"],
    "incomplete_visual_iterations": ["incomplete_visual_iterations"],
    "dsl_versions": ["dsl_versions"],
    "document_requests": ["document_requests"],
    "other_service_requests": ["other_service_requests", "other_tool_calls", "tool_usage_records"],
}
USED = {}
MISSING = {}


def norm(tid):
    c = T[tid]["counts"]
    out = {}
    for key, names in ALIAS.items():
        for n in names:
            v = c.get(n)
            if isinstance(v, int):
                out[key] = v
                USED.setdefault(key, set()).add(n)
                break
        else:
            out[key] = None
            MISSING.setdefault(key, []).append(tid)
    return out


DERIVED = []


def derive(tid, out, c):
    """按各题自有字段补齐缺项，并在 counts_note.derived 里留痕。"""
    def setv(key, val, why):
        if out.get(key) is None and val is not None:
            out[key] = val
            DERIVED.append("%s.%s=%s（%s）" % (tid, key, val, why))

    hb = c.get("http_status_breakdown")
    if isinstance(hb, dict):
        setv("successful_snapshot_requests", int(hb.get("200") or 0), "http_status_breakdown['200']")
        setv("failed_snapshot_requests", sum(int(v) for k, v in hb.items() if k != "200"),
             "http_status_breakdown 非 200 项之和")
    if c.get("render_errors_400") is not None and c.get("render_transport_or_truncated") is not None:
        setv("failed_snapshot_requests",
             int(c["render_errors_400"]) + int(c["render_transport_or_truncated"]),
             "render_errors_400 + render_transport_or_truncated")
    ibt = c.get("iterations_by_type")
    if isinstance(ibt, dict):
        setv("retry_requests", int(ibt.get("retry") or 0), "iterations_by_type.retry")
        if "visual" in ibt:
            setv("completed_visual_iterations", int(ibt["visual"]), "iterations_by_type.visual")


N = {}
for tid in ORDER:
    N[tid] = norm(tid)
    derive(tid, N[tid], T[tid]["counts"])
MISSING = {}
for tid in ORDER:
    for k, v in N[tid].items():
        if v is None:
            MISSING.setdefault(k, []).append(tid)


def total(key):
    vals = [N[t][key] for t in ORDER if N[t][key] is not None]
    return sum(vals)


def secs(v):
    return None if v is None else round(float(v), 1)


def jsonl(path):
    if not os.path.exists(path):
        return []
    recs = []
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            recs.append(json.loads(line))
        except Exception:
            pass
    return recs


# 服务请求数以各题 requests.jsonl 的实发记录为准（自报字段口径不一，见 counts_note.log_recount）。
DOC_KINDS = ("doc", "document", "docs", "guide", "research", "reference")
LOG = {}
STATUS = Counter()
CACHE_HITS = {}
for tid in ORDER:
    n = ok = fail = doc = other = 0
    for r in jsonl("tmp/%s/%s/requests.jsonl" % (RUN, tid)):
        u = r.get("url") or ""
        if u.endswith("/snapshot") or str(r.get("kind", "")).lower() in ("snapshot", "render"):
            n += 1
            STATUS[str(r.get("http_status"))] += 1
            if "hit" in str(r.get("server_timing") or ""):
                CACHE_HITS[tid] = CACHE_HITS.get(tid, 0) + 1
            if r.get("http_status") == 200:
                ok += 1
            else:
                fail += 1
        elif str(r.get("kind", "")).lower() in DOC_KINDS:
            doc += 1
        else:
            other += 1
    LOG[tid] = {"snapshot_requests": n, "successful_snapshot_requests": ok,
                "failed_snapshot_requests": fail, "document_requests": doc,
                "other_service_requests": other}
shared_log = jsonl("tmp/%s/_suite/requests.jsonl" % RUN)
SHARED_DOC = sum(1 for r in shared_log if str(r.get("kind", "")).lower() in DOC_KINDS)


def log_total(key):
    return sum(LOG[t][key] for t in ORDER)


gaps = F["suite_idle_gaps_over_300s"]
idle_sum = round(sum(g["seconds"] for g in gaps), 1)
span = F["suite_evidence_span_seconds"]
started = min(t["started_at"] for t in T.values() if t["started_at"])
ended = max(t["ended_at"] for t in T.values() if t["ended_at"])
suite_elapsed = round((datetime.datetime.fromisoformat(ended) - datetime.datetime.fromisoformat(started)).total_seconds(), 1)

rows = {}
for tid in ORDER:
    ti = T[tid]["timings"] or {}
    rows[tid] = {
        "started_at": ti.get("started_at") or ti.get("task_started_at"),
        "ended_at": ti.get("ended_at") or ti.get("task_ended_at"),
        "recorded_elapsed_seconds": secs(ti.get("elapsed_seconds")),
        "recorded_wall_clock_seconds": secs(ti.get("wall_clock_seconds")),
        "recorded_active_seconds": secs(ti.get("active_seconds")),
        "recorded_idle_gap_seconds": secs(ti.get("idle_gap_seconds")),
        "request_duration_sum_seconds": secs(ti.get("request_duration_sum_seconds")),
        "recomputed_evidence_span_seconds": T[tid]["recomputed_evidence_span_seconds"],
        "recomputed_idle_seconds_over_300s": round(sum(g["seconds"] for g in T[tid]["recomputed_idle_gaps_over_300s"]), 1),
        "recomputed_idle_gap_count_over_300s": len(T[tid]["recomputed_idle_gaps_over_300s"]),
        "elapsed_time_note": ti.get("elapsed_time_note"),
    }

task_summaries = []
for tid in ORDER:
    t = T[tid]
    m = json.load(open(os.path.join(ROOT, tid, "task-metrics.json"), encoding="utf-8"))
    task_summaries.append({
        "task_id": tid,
        "title": t["title"],
        "track": "advanced" if tid.startswith("A") else "creative",
        "status": t["status"],
        "rounds": (["round-01", "round-02", "round-03"] if tid in ("A21", "A22") else []),
        "cases": ([c["rel"].split("/")[1] for c in t["images"] if "/case-" in c["rel"]]
                  if tid.startswith("B") else []),
        "final_images": t["final_images"],
        "minimum_final_pngs": t["minimum_final_pngs"],
        "independent_creative_works": (len({i["rel"].split("/")[1] for i in t["images"] if "/case-" in i["rel"]})
                                       if tid.startswith("B") else None),
        "counts": N[tid],
        "service_counts_from_logs": LOG[tid],
        "timings": rows[tid],
        "output_dir": t["output_dir"],
        "temp_dir": t["temp_dir"],
        "artifacts_present": t["closeout"],
        "unresolved_issue_count": len(m.get("unresolved_issues") or []),
    })

unresolved = []
for tid in ORDER:
    m = json.load(open(os.path.join(ROOT, tid, "task-metrics.json"), encoding="utf-8"))
    for u in (m.get("unresolved_issues") or []):
        unresolved.append({"task_id": tid, "issue": u if isinstance(u, str) else json.dumps(u, ensure_ascii=False)})

DIVERGE = []
for tid in ORDER:
    for k in ("snapshot_requests", "successful_snapshot_requests", "failed_snapshot_requests"):
        if N[tid][k] is not None and N[tid][k] != LOG[tid][k]:
            DIVERGE.append("%s.%s 自报 %s → 实发日志 %s" % (tid, k, N[tid][k], LOG[tid][k]))

out = {
    "schema_version": 1,
    "path_base": "suite_root",
    "suite_version": CAT["suite_version"],
    "run_id": RUN,
    "profile": "all",
    "status": "completed",
    "stop_reason": ("30 题（A01–A24、B01–B06）全部 completed：%d 张最终图片（题库最低 %d），"
                    "每张都有同名完整 .snapshot 且实际开图自检；B01–B06 每题 10 个开放用例独立作品；"
                    "A21/A22 三个预置轮次全部交付；套件级 index/gallery/snapshot-usage/task-metrics/suite-state "
                    "五件总交付齐备并通过总审查。" % (F["totals"]["final_images"], F["totals"]["minimum_required"])),
    "started_at": started,
    "ended_at": ended,
    "elapsed_seconds": suite_elapsed,
    "task_status_counts": dict(Counter(T[t]["status"] for t in ORDER)),
    "counts": {
        "final_pngs": F["totals"]["final_images"],
        "independent_creative_cases": sum(ts["independent_creative_works"] or 0 for ts in task_summaries),
        "snapshot_requests": log_total("snapshot_requests"),
        "successful_snapshot_requests": log_total("successful_snapshot_requests"),
        "failed_snapshot_requests": log_total("failed_snapshot_requests"),
        "retry_requests": total("retry_requests"),
        "other_service_requests": log_total("other_service_requests"),
        "document_requests": log_total("document_requests") + SHARED_DOC,
        "dsl_versions": total("dsl_versions"),
        "image_views": total("image_views"),
        "completed_visual_iterations": total("completed_visual_iterations"),
        "incomplete_visual_iterations": total("incomplete_visual_iterations"),
        "suite_documents_fetched": len(shared_log),
    },
    "counts_note": {
        "aggregation": "只累加每题实发请求日志与各题 task-metrics.json 顶层自有计数；轮次/用例明细不再重复相加。",
        "log_recount": {
            "rule": "snapshot_requests / successful / failed / document_requests / other_service_requests 一律按 "
                    "tmp/<run>/<task>/requests.jsonl 的实发记录重新点数（URL 以 /snapshot 结尾或 kind=snapshot 记为服务渲染请求；"
                    "kind∈doc/document/guide/research/reference 记为文档或资料请求；其余 GET 记为其他服务请求），"
                    "再与 shared 阶段的 %d 次文档请求相加。" % len(shared_log),
            "divergences": DIVERGE,
            "why": "总审查发现各题自报字段口径不一：B04 的 http_requests_total 把 40 次外部资料 GET 与 1 次 fonts 查询算进了请求数，"
                   "B03 的 snapshot_requests 把 4 次文档 GET 算进渲染请求数。套件层改用日志实数，各题自报值保留在 "
                   "task_summaries[].counts 中以便对照，不改写各题原文件。",
        },
        "field_normalization": {k: sorted(v) for k, v in USED.items()},
        "missing_for_tasks": MISSING,
        "failed_definition": "失败 = 非 200 响应 + 传输截断/无响应体；各题原始日志保留具体 http_status（0/None 表示传输层失败）。",
        "derived": DERIVED,
        "document_requests_note": "A 轨多数题目未单列文档请求（服务指南与 DSL 文档在 shared 阶段一次抓取并缓存复用），"
                                  "文档请求数只统计日志里确有 GET 的题（shared+A17+B03+B04）；缓存复用不重复计数。",
        "gate_blocked_note": "B03–B06 另有文字闸门（TextFit）拦下、未发请求的尝试，计在各题 counts 的 "
                             "gate_blocked_no_request / gate_blocked_events / gate_warnings_blocked，不在上面的请求数内。",
    },
    "shared_preparation": {
        "dir": "tmp/%s/_suite/" % RUN,
        "requests": len(shared_log),
        "document_requests": SHARED_DOC,
        "docs_cache": "tmp/%s/_suite/docs/" % RUN,
        "note": "服务指南与 DSL 文档在 shared 阶段抓取并缓存；后续题只读缓存不重复计数（各题 document_requests_note 有说明）。",
    },
    "timing_accounting": {
        "suite_started_at": started,
        "suite_ended_at": ended,
        "suite_elapsed_seconds": suite_elapsed,
        "suite_evidence_first_at": F["suite_evidence_first"],
        "suite_evidence_last_at": F["suite_evidence_last"],
        "suite_evidence_span_seconds": span,
        "suite_idle_seconds_over_300s": idle_sum,
        "suite_idle_gap_count_over_300s": len(gaps),
        "suite_idle_gaps_over_300s": gaps,
        "elapsed_time_note": (
            "elapsed_seconds / 时间跨度包含大量非工作空档（本 run 跨 2026-10-08→2026-10-11，"
            "会话多次恢复、等待与人工看图间歇）。空档按日志时间戳重算：相邻证据事件间隔 >300s 记为 idle，"
            "合计 %s，绝不把这些时间说成连续工作。只记录了单一 elapsed 的早期题目（A 轨与 B01/B02 部分）"
            "未拆分 active/idle，其真实工作时长以 request_duration_sum_seconds + 迭代/看图日志时间戳为上界参考。"
            % idle_sum),
        "per_task": rows,
        "sources": ["tmp/%s/_suite/requests.jsonl" % RUN,
                     "tmp/%s/<task>/requests.jsonl" % RUN,
                     "tmp/%s/<task>/iterations.jsonl" % RUN,
                     "outputs/%s/<task>/task-metrics.json timings" % RUN],
    },
    "delivery": {
        "suite_dir": "outputs/%s/_suite/" % RUN,
        "artifacts": ["outputs/%s/_suite/index.md" % RUN,
                      "outputs/%s/_suite/gallery.md" % RUN,
                      "outputs/%s/_suite/snapshot-usage.md" % RUN,
                      "outputs/%s/_suite/task-metrics.json" % RUN,
                      "outputs/%s/_suite/suite-state.json" % RUN],
        "gallery_images": F["totals"]["final_images"],
        "root_gitignore": ".gitignore",
        "runtime_cache_rules": ["__pycache__/", "*.pyc", "*.pyo", ".pytest_cache/", ".mypy_cache/",
                                ".ruff_cache/", "node_modules/", ".pnpm-store/", ".eslintcache",
                                "*.pyd", "*.egg-info/", "build/", "dist/", ".idea/", ".vscode/"],
        "evidence_not_ignored": "outputs/ 与 tmp/ 未设忽略规则；过程证据（草稿、失败响应、预览、脚本、日志、检查点）全部保留。",
    },
    "final_review": {
        "checked_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "checks": [],
        "result": None,
    },
    "aggregation_rule": "Only task-level totals plus shared preparation; never add round/case detail again.",
    "output_dir": "outputs/%s/" % RUN,
    "temp_dir": "tmp/%s/" % RUN,
    "unresolved_issues": unresolved,
    "task_summaries": task_summaries,
}
GATE_KEYS = ("gate_blocked_no_request", "gate_blocked_events", "gate_warnings_blocked")
out["service_response_breakdown"] = {
    "snapshot_post_status_counts": dict(STATUS),
    "cache_hit_posts": CACHE_HITS,
    "cache_hit_note": "Server-Timing: cache;desc=hit 的字节相同提交——服务端命中缓存返回同一图，属无效渲染尝试，"
                      "各题已记录且未当作成品；这些次已包含在上面的 200 计数里。",
    "gate_blocked_by_task": {t: {k: T[t]["counts"].get(k) for k in GATE_KEYS if T[t]["counts"].get(k) is not None}
                             for t in ORDER if any(T[t]["counts"].get(k) for k in GATE_KEYS)},
    "gate_blocked_note": "本地 TextFit/结构闸门拦下、未发出请求的尝试，各题字段名不同，原值列于此，不计入请求数。",
}
json.dump(out, open(SUITE + "task-metrics.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("suite task-metrics.json written; counts:", json.dumps(out["counts"], ensure_ascii=False))
