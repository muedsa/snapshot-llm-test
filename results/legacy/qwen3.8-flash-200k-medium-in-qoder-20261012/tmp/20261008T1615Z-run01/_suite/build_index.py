import os, json, datetime

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
FIELD_SRC = {}


def norm(tid):
    c = T[tid]["counts"]
    out = {}
    for key, names in ALIAS.items():
        for n in names:
            v = c.get(n)
            if isinstance(v, int):
                out[key] = v
                FIELD_SRC.setdefault(key, set()).add(n)
                break
        else:
            out[key] = None
    return out


N = {tid: norm(tid) for tid in ORDER}


def total(key):
    vals = [N[t][key] for t in ORDER if N[t][key] is not None]
    missing = [t for t in ORDER if N[t][key] is None]
    return sum(vals), len(vals), missing


def secs(v):
    return None if v is None else round(float(v), 1)


def hhmmss(sec):
    if sec is None:
        return "未记录"
    sec = float(sec)
    d = int(sec // 86400)
    h = int(sec % 86400 // 3600)
    m = int(sec % 3600 // 60)
    s = sec % 60
    return ("%dd " % d if d else "") + "%d:%02d:%02d（%.1fs）" % (h, m, s, sec)


# timing roll-up
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
        "rate_limit_wait_seconds": secs(ti.get("rate_limit_wait_seconds")),
        "recomputed_evidence_span_seconds": T[tid]["recomputed_evidence_span_seconds"],
        "recomputed_idle_gap_seconds_over_300s": round(sum(g["seconds"] for g in T[tid]["recomputed_idle_gaps_over_300s"]), 1),
        "recomputed_idle_gaps_over_300s_count": len(T[tid]["recomputed_idle_gaps_over_300s"]),
        "idle_gap_note": ti.get("elapsed_time_note"),
    }

gaps = F["suite_idle_gaps_over_300s"]
idle_sum = round(sum(g["seconds"] for g in gaps), 1)
span = F["suite_evidence_span_seconds"]

REQ_TOTAL, REQ_OK, REQ_FAIL, VIEWS, VITER, DSLV = (total(k) for k in (
    "snapshot_requests", "successful_snapshot_requests", "failed_snapshot_requests",
    "image_views", "completed_visual_iterations", "dsl_versions"))
RETRY, OTHERSVC, DOCS, INCVITER = (total(k) for k in ("retry_requests", "other_service_requests", "document_requests", "incomplete_visual_iterations"))

# 请求/看图/迭代口径以套件 task-metrics.json 为准（该文件已按实发日志重数并留痕）。
SM = json.load(open(SUITE + "task-metrics.json", encoding="utf-8"))
C = SM["counts"]
SB = SM["service_response_breakdown"]["snapshot_post_status_counts"]

# ---------------- index.md ----------------
I = []
I.append("# 全套索引 · run `%s`" % RUN)
I.append("")
I.append("总任务根：本仓库根目录（`path_base=suite_root`，全部路径为相对路径，见 [PATHS.md](../../../PATHS.md)）。")
I.append("总输出根：`outputs/%s/`；总临时根：`tmp/%s/`。" % (RUN, RUN))
I.append("")
I.append("## 全套状态")
I.append("")
I.append("| 项 | 值 |")
I.append("| --- | --- |")
I.append("| 题目数 | %d（A01–A24 高级轨道 + B01–B06 创作轨道） |" % len(ORDER))
from collections import Counter
SC = Counter(T[t]["status"] for t in ORDER)
I.append("| 状态 | %s |" % " / ".join("%s %d" % (k, v) for k, v in sorted(SC.items())))
I.append("| 最终图片 | %d 张（题库要求 ≥%d 张），每张都有同名完整 `.snapshot` |" % (F["totals"]["final_images"], F["totals"]["minimum_required"]))
I.append("| 逐图画廊 | [gallery.md](gallery.md) |")
I.append("| 实际耗时口径 | 全套有证据的时间跨度 %s，其中 >300s 的空档合计 %s（%d 段，会话恢复/等待，不计为工作时长）；详见 [task-metrics.json](task-metrics.json) 的 `timing_accounting` |" % (
    hhmmss(span), hhmmss(idle_sum), len(gaps)))
I.append("| 请求 | POST /snapshot 共 %d 次（200 %d、400 %d、500 %d、传输失败 %d），"
         "另计文档/资料 GET %d 次、其他服务 GET %d 次、重试 %d 次；口径见 task-metrics.json 的 "
         "`counts_note.log_recount` |" % (
             C["snapshot_requests"], SB.get("200", 0), SB.get("400", 0), SB.get("500", 0),
             int(SB.get("0", 0)) + int(SB.get("None", 0)),
             C["document_requests"], C["other_service_requests"], C["retry_requests"]))
I.append("| 看图与迭代 | 实际看图 %d 次，完整视觉迭代 %d 次（未完整 %d 次），DSL 版本 %d 个 |" % (
    C["image_views"], C["completed_visual_iterations"], C["incomplete_visual_iterations"], C["dsl_versions"]))
I.append("")
I.append("## 逐题清单")
I.append("")
I.append("| 题目 | 内容 | 状态 | 最终图 | 输出目录 | 临时目录 | 单题入口 |")
I.append("| --- | --- | --- | --- | --- | --- | --- |")
for tid in ORDER:
    t = T[tid]
    ent = "[使用说明](../%s/snapshot-usage.md) · [指标](../%s/task-metrics.json)" % (tid, tid)
    extra = " · [画廊](../%s/gallery.md)" % tid if "gallery.md" in t["closeout"] else ""
    I.append("| %s | %s | %s | %d/%d | `%s` | `%s` | %s%s |" % (
        tid, t["title"], t["status"], t["final_images"], t["minimum_final_pngs"],
        t["output_dir"], t["temp_dir"], ent, extra))
I.append("")
I.append("「最终图」列格式为 实际交付 / 题库最低要求。A21、A22 各自包含 3 个预置轮次的全部图片（每轮 2 张 / 1 张），"
         "B01–B06 每题包含 10 个开放用例的独立作品（B02 的 case-02 正反面共 2 张，故为 11 张）。")
I.append("")
I.append("## 交付物与实际路径")
I.append("")
I.append("| 套件级文件 | 路径 |")
I.append("| --- | --- |")
for f, d in [("index.md", "本文件"), ("gallery.md", "全套 %d 张最终图片逐图展示" % F["totals"]["final_images"]),
             ("snapshot-usage.md", "全套文档/DSL/工具应用、跨题经验与踩坑、总审查与剩余事项"),
             ("task-metrics.json", "全套起止/总耗时、shared+各题请求/迭代/看图/作品数"),
             ("suite-state.json", "逐题进度与证据指针（最终态）")]:
    I.append("| `%s` | `outputs/%s/_suite/%s` |" % (f, RUN, f))
I.append("")
I.append("共享准备（服务指南/DSL 文档抓取、字体探测）在 `tmp/%s/_suite/`，"
         "请求与迭代日志在各题 `tmp/%s/<task>/`，运行事件与检查点在 `tmp/%s/_suite/events.jsonl` 与 `tmp/%s/_suite/checkpoints/`。" % (RUN, RUN, RUN, RUN))
I.append("")
I.append("## 运行时缓存与 .gitignore")
I.append("")
I.append("总任务根 `.gitignore`（`​.gitignore`，仅一份，不在每题重复创建）排除了 `__pycache__/`、`*.pyc`、`*.pyo`、"
         "`.pytest_cache/`、`.mypy_cache/`、`.ruff_cache/`、`node_modules/`、`.pnpm-store/`、`.eslintcache`、`*.pyd`、"
         "`*.egg-info/`、`build/`、`dist/`、`.idea/`、`.vscode/`；没有 `tmp/`、`outputs/`、`cache/`、`.cache/`、`*.log` "
         "或图片/DSL/JSON 的通配忽略，因此最终产物与过程证据都不会被忽略。运行中确实产生了 Python 字节码缓存目录 "
         "（如 `tmp/%s/B06/__pycache__/`），按约定只作为运行时缓存排除，不列为证据，也未删除真实尝试记录。" % RUN)
I.append("")
I.append("## 各题耗时（按记录值，含空档）")
I.append("")
I.append("| 题目 | 记录起点 | 记录终点 | 记录跨度 | 其中 >300s 空档（重算） | 请求耗时之和 |")
I.append("| --- | --- | --- | --- | --- | --- |")
for tid in ORDER:
    r = rows[tid]
    I.append("| %s | %s | %s | %s | %s（%d 段） | %s |" % (
        tid, r["started_at"] or "—", r["ended_at"] or "—",
        hhmmss(r["recorded_wall_clock_seconds"] or r["recorded_elapsed_seconds"]),
        hhmmss(r["recomputed_idle_gap_seconds_over_300s"]), r["recomputed_idle_gaps_over_300s_count"],
        hhmmss(r["request_duration_sum_seconds"])))
I.append("")
I.append("A 轨与 B01/B02 早期记录只给出单一 `elapsed_seconds`，未拆分活动/空档；"
         "本表最后一列的空档由 `requests.jsonl` + `iterations.jsonl` 的时间戳重算（>300s 的相邻事件间隔），"
         "用于说明「跨度时间」不等于「连续工作时间」。B03–B06 与 B01 后期在各自 task-metrics 中另有 "
         "`active_seconds` / `idle_gap_seconds` / `idle_gaps[]` 明细。")
I.append("")
I.append("## 局部阻塞与未完成事项")
I.append("")
any_un = False
for tid in ORDER:
    m = json.load(open(os.path.join(ROOT, tid, "task-metrics.json"), encoding="utf-8"))
    u = [x for x in (m.get("unresolved_issues") or [])
         if str(x if isinstance(x, str) else json.dumps(x, ensure_ascii=False)).strip().rstrip("。") not in ("无", "none", "None")]
    if u:
        any_un = True
        I.append("**%s**（%d 项）：" % (tid, len(u)))
        for x in u:
            I.append("- %s" % (x if isinstance(x, str) else json.dumps(x, ensure_ascii=False)))
        I.append("")
if not any_un:
    I.append("无。")
I.append("")
I.append("上述事项是能力/环境边界（如服务无矢量路径、无法做真实用户验证），不影响对应题目的交付要求；"
         "详见各题 `snapshot-usage.md` 与 [snapshot-usage.md](snapshot-usage.md) 的「剩余事项」。")
I.append("")
I.append("套件级总审查的逐项结论写在 [snapshot-usage.md](snapshot-usage.md) 的「最终审查」一节，"
         "机器可读的检查记录在 `tmp/%s/_suite/final-review-checks.json`，"
         "字节级溯源在 `tmp/%s/_suite/png-provenance.json` 与 `tmp/%s/_suite/dsl-provenance.json`。" % (RUN, RUN, RUN))
open(SUITE + "index.md", "w", encoding="utf-8").write("\n".join(I) + "\n")
print("index.md", len(I), "lines")
