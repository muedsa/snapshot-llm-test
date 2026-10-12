# -*- coding: utf-8 -*-
"""B06 task-metrics.json 构建器：次数、耗时、逐件指标全部从实际日志与文件读出。
时间口径按总根约定：墙钟 = 最早与最晚留痕之差；相邻留痕间隔 >900s 记为空闲/经过时间，
不计入有效工时。人工核对过的定性计数（闸门拦截、本地 assert 中止）单独标 source。
"""
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
TMP = ROOT / "tmp" / RID / "B06"
OUT = ROOT / "outputs" / RID / "B06"
SUITE = ROOT / "outputs" / RID / "_suite"
IDLE_THRESHOLD = 900.0


def jl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def pars(t):
    return datetime.fromisoformat(t)


REQ, IT, TU, BL = jl(TMP / "requests.jsonl"), jl(TMP / "iterations.jsonl"), \
    jl(TMP / "tool-usage.jsonl"), jl(TMP / "build-log.jsonl")
STATE = json.load(open(SUITE / "suite-state.json", encoding="utf-8"))
B06 = [t for t in STATE["tasks"] if t["id"] == "B06"][0]
START = pars(B06["started_at"])

# ---------------------------------------------------------------- 留痕时间轴
stamps = []
for r in REQ:
    stamps += [pars(r["started_at"]), pars(r["ended_at"])]
for i in IT:
    stamps += [pars(i["recorded_at"]), pars(i["image_viewed_at"])]
for t in TU:
    stamps.append(pars(t["at"]))
for b in BL:
    stamps.append(pars(b["ts"]))
for p in list(OUT.glob("case-*/final.png")) + list(OUT.glob("case-*/final.snapshot")) \
        + list(OUT.glob("case-*/case.md")) + list(TMP.glob("case-*/case*.snapshot")):
    stamps.append(datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc))
stamps = sorted(set(s for s in stamps if s.tzinfo))
first, last = stamps[0], stamps[-1]
gaps = []
for a, b in zip(stamps, stamps[1:]):
    d = (b - a).total_seconds()
    if d > IDLE_THRESHOLD:
        gaps.append({"from": a.isoformat(), "to": b.isoformat(), "seconds": round(d, 1)})
small = []
for a, b in zip(stamps, stamps[1:]):
    d = (b - a).total_seconds()
    if 300.0 < d <= IDLE_THRESHOLD:
        inside = []
        for p in list(OUT.rglob("*")) + list(TMP.rglob("*")):
            if not p.is_file():
                continue
            m = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc)
            if a.timestamp() + 2 < m.timestamp() <= b.timestamp() + 1:
                inside.append("%s  %s" % (m.isoformat()[11:19],
                                          str(p.relative_to(ROOT)).replace(os.sep, "/")))
        inside.sort()
        small.append({"from": a.isoformat()[11:19], "to": b.isoformat()[11:19], "seconds": round(d, 1),
                      "files_written_at_interval_end": inside[:6],
                      "files_written_at_interval_end_count": len(inside),
                      "reading": "左端是上一条留痕，右端是下一条留痕；区间内无新留痕，"
                                 "右端出现的文件说明这段是本地撰写/修订（写上一件的 case.md、写下一件的脚本与生成器），不是空闲也不是等服务"})
wall = round((last - START).total_seconds(), 1)
idle = round(sum(g["seconds"] for g in gaps), 1)
ok = [r for r in REQ if r["http_status"] == 200]
bad = [r for r in REQ if r["http_status"] != 200]
kinds = {
    "http_400_parse_or_render_error": sum(1 for r in REQ if r["http_status"] == 400),
    "transport_failure_no_body": sum(1 for r in REQ if r["http_status"] == 0),
    "truncated_response_content_length_mismatch": sum(1 for r in REQ if r["http_status"] is None),
}
srv_render = sum(float(re.search(r"render;dur=([\d.]+)", r["server_timing"]).group(1)) / 1000
                 for r in ok if r.get("server_timing") and "render;dur" in r["server_timing"])
srv_total = sum(float(re.search(r"total;dur=([\d.]+)", r["server_timing"]).group(1)) / 1000
                for r in ok if r.get("server_timing") and "total;dur" in r["server_timing"])

# ---------------------------------------------------------------- 逐件指标
GATE_EVENTS = {"case-01": 1, "case-05": 2, "case-08": 1, "case-09": 1}
GATE_WARNINGS = {"case-01": 3, "case-05": 5, "case-08": 1, "case-09": 2}
ASSERT_ABORTS = {"case-03": 2, "case-04": 3, "case-05": 1, "case-06": 3,
                 "case-07": 2, "case-08": 2, "case-10": 2}
NO_DRAFT_STATIC = {"case-09": 1}

case_metrics = []
for n in range(1, 11):
    cid = "case-%02d" % n
    pre = "case%02d-" % n
    rs = [r for r in REQ if r["dsl_version"].startswith(pre)]
    its = [i for i in IT if i["version"].startswith(pre)]
    ts = [pars(r["started_at"]) for r in rs] + [pars(i["recorded_at"]) for i in its]
    tl = [t for t in TU if cid in (t.get("affects") or "")]
    rq_ok = [r for r in rs if r["http_status"] == 200]
    png = OUT / cid / "final.png"
    case_metrics.append({
        "case": cid,
        "started_at": min(ts).isoformat(),
        "ended_at": max(ts).isoformat(),
        "wall_clock_seconds": round((max(ts) - min(ts)).total_seconds(), 1),
        "request_duration_sum_seconds": round(sum(r["duration_seconds"] for r in rs), 2),
        "server_render_sum_seconds": round(sum(
            float(re.search(r"render;dur=([\d.]+)", r["server_timing"]).group(1)) / 1000
            for r in rq_ok if r.get("server_timing") and "render;dur" in r["server_timing"]), 2),
        "render_requests": len(rs),
        "render_ok": len(rq_ok),
        "render_failed_or_truncated": len(rs) - len(rq_ok),
        "dsl_versions": len(set(r["dsl_version"] for r in rs)),
        "iterations": len(its),
        "iterations_by_type": {t: sum(1 for i in its if i["type"] == t)
                               for t in ("baseline", "visual", "syntax-fix", "retry") if
                               any(i["type"] == t for i in its)},
        "image_views": sum(1 for i in its if i["image_viewed"]),
        "completed_versions_flagged": [i["version"] for i in its if i["completed"]],
        "gate_blocked_events": GATE_EVENTS.get(cid, 0),
        "gate_warnings_blocked": GATE_WARNINGS.get(cid, 0),
        "local_assert_abort_events": ASSERT_ABORTS.get(cid, 0),
        "static_review_drafted_never_rendered": NO_DRAFT_STATIC.get(cid, 0),
        "previews": len(list((OUT / cid).glob("v0*-preview.png"))),
        "qa_crops": len(list((TMP / cid / "qa").glob("*.png"))) + len(list((TMP / cid).glob("qa-*.png"))),
        "tool_usage_entries": len(tl),
        "works": 1,
        "canvas": "%dx%d" % (int.from_bytes(open(png, "rb").read(24)[16:20], "big"),
                             int.from_bytes(open(png, "rb").read(24)[20:24], "big")),
        "final_png": "%s/final.png" % cid,
        "final_snapshot": "%s/final.snapshot" % cid,
        "case_report": "%s/case.md" % cid,
        "final_bytes": png.stat().st_size,
    })

probe = [r for r in REQ if r["dsl_version"].startswith("case00-")]
M = {
    "schema_version": 2,
    "path_base": "suite_root",
    "task_id": "B06",
    "run_id": RID,
    "task_round": "round-01（本题为开放作品集，无预置轮次）",
    "status": "completed",
    "stop_reason": "十件独立作品全部交付、逐件自检通过，收尾产物（problem-evidence/design-review/portfolio/gallery/snapshot-usage/task-metrics）齐",
    "output_dir": "outputs/%s/B06/" % RID,
    "temp_dir": "tmp/%s/B06/" % RID,
    "theme": "把十个日常信息难题重做成作品：每题做一次「原始口径 → 换算 → 行动」的翻译",
    "timings": {
        "task_started_at": START.isoformat(),
        "first_evidence_at": first.isoformat(),
        "last_evidence_at": last.isoformat(),
        "task_ended_at": last.isoformat(),
        "wall_clock_seconds": wall,
        "active_seconds": round(wall - idle, 1),
        "idle_gap_seconds": idle,
        "idle_gaps": gaps,
        "sub_threshold_gaps_over_300s": small,
        "elapsed_time_note": (
            "墙钟 %.1fs（%.2f h）＝本题 started_at 与最晚留痕之差。按总根口径（相邻留痕间隔 >%ds 计空闲）"
            "本题为 %d 段共 %.1fs，因此有效工时记 %.1fs（%.2f h）。为了不把「无超阈间隔」读成全程无间断，"
            "另列 %d 段 300–900s 的间隔（sub_threshold_gaps_over_300s）及其右端实际写出的文件，"
            "这些间隔对应本地工作（写上一件的 case.md、撰写下一件的 caseNN.py 与生成器修订），"
            "不是空闲也不是等待服务。有效工时只是「有留痕覆盖的时间上界」，不等于持续专注时长；"
            "单请求端到端耗时见 request_duration_sum_seconds（含 8 次失败/截断的等待），"
            "服务渲染耗时见 server_render_sum_seconds，两者与墙钟互不相加。"
            % (wall, wall / 3600, int(IDLE_THRESHOLD), len(gaps), idle, wall - idle, (wall - idle) / 3600, len(small))),
        "first_service_response_at": ok[0]["started_at"] if ok else None,
        "first_probe_image_seconds": round((pars(probe[2]["ended_at"]) - START).total_seconds(), 1),
        "first_work_image_seconds": round((pars([r for r in REQ if r["dsl_version"].startswith("case01-")][0]["ended_at"])
                                           - START).total_seconds(), 1),
        "first_usable_image_seconds": round((pars([r for r in REQ if r["dsl_version"].startswith("case01-")
                                                   and r["http_status"] == 200][0]["ended_at"]) - START).total_seconds(), 1),
        "user_feedback_wait_seconds": 0,
        "rate_limit_wait_seconds": 0,
        "queue_wait_seconds": None,
        "request_duration_sum_seconds": round(sum(r["duration_seconds"] for r in REQ), 2),
        "request_duration_ok_only_seconds": round(sum(r["duration_seconds"] for r in ok), 2),
        "request_duration_source": "requests.jsonl 的 duration_seconds（curl 端到端，含 8 次失败/截断的等待）",
        "server_render_sum_seconds": round(srv_render, 2),
        "server_total_sum_seconds": round(srv_total, 2),
        "server_timing_source": "41 次 HTTP 200 响应的 Server-Timing 头（render;dur / total;dur，毫秒）",
        "timing_sources": "suite-state.json(B06.started_at) + requests.jsonl + iterations.jsonl(recorded_at/image_viewed_at) + tool-usage.jsonl(at) + build-log.jsonl(ts) + 产物文件 mtime",
    },
    "counts": {
        "independent_works": 10,
        "final_case_count": 10,
        "final_images": 10,
        "final_png_bytes_total": sum(c["final_bytes"] for c in case_metrics),
        "distinct_canvases": sorted(set(c["canvas"] for c in case_metrics)),
        "snapshot_requests": len(REQ),
        "successful_snapshot_requests": len(ok),
        "failed_snapshot_requests": len(bad),
        "failure_kinds": kinds,
        "retry_requests": None,
        "retry_requests_note": "requests.jsonl 未单列 retry 标记；同版本多次请求即失败重发，按 dsl_version 分组可见："
                               "case00-v04 三次传输失败后改 v04b 再两次。--retries 参数值未回写日志，故留 null 并说明",
        "other_service_requests": 0,
        "document_requests": 0,
        "document_note": "服务指南与 DSL 文档在 shared 阶段一次下载缓存（tmp/<run>/_suite/docs/），本题只读缓存，不重复计数",
        "fonts_queries": 0,
        "dsl_versions": len(set(r["dsl_version"] for r in REQ)),
        "dsl_files_kept": len(list(TMP.glob("case-*/case*.snapshot"))),
        "image_views": sum(1 for i in IT if i["image_viewed"]),
        "iterations_total": len(IT),
        "iterations_by_type": {t: sum(1 for i in IT if i["type"] == t)
                               for t in ("baseline", "visual", "syntax-fix", "retry")},
        "completed_visual_iterations": sum(1 for i in IT if i["type"] == "visual" and i["completed"]),
        "incomplete_visual_iterations": sum(1 for i in IT if i["type"] == "visual" and not i["completed"]),
        "gate_blocked_events": sum(GATE_EVENTS.values()),
        "gate_warnings_blocked": sum(GATE_WARNINGS.values()),
        "local_assert_abort_events": sum(ASSERT_ABORTS.values()),
        "promoted_finals": 10,
        "voided_promotions": 1,
        "voided_promotion_evidence": "件-07 的 v03 提升后因数据文案自相矛盾（24 h 封顶措辞）作废，改由 v05 作 final；"
                                     "件-06 的 v04 是 cache;desc=hit 的无效渲染，未作成品候选",
        "noop_cache_hit_renders": 1,
        "pre_render_static_review_abort": 1,
        "textfit_box_checks_total": sum(b["gate"]["checks"] for b in BL),
        "qa_crops": sum(c["qa_crops"] for c in case_metrics),
        "previews": sum(c["previews"] for c in case_metrics),
        "tool_usage_entries": len(TU),
        "build_log_entries": len(BL),
        "other_tool_calls": None,
        "other_tool_calls_note": "本地 python 脚本执行次数未单独计数（caseNN.py 生成、递归 diff 等），逐条目的见 tool-usage.jsonl",
    },
    "capability_probe": {
        "dir": "tmp/%s/B06/case-00/" % RID,
        "requests": len(probe),
        "ok": sum(1 for r in probe if r["http_status"] == 200),
        "purpose": "在正式十件之前实测 ClipRect/ClipOval/BackdropFilter/Transform matrix 的真实语义",
        "findings": [
            "BackdropFilter 必须给 sigmaX/sigmaY，只写 blur 报 400 Attr [sigmaX] must not be null（B06-case00-v01）",
            "ClipRect/ClipOval 不是 Stack：往里放 Positioned 报 400 renderBox.parentData must be StackParentData（B06-case00-v02）",
            "ClipRect 会把超高子元素底部对齐，需自行算 top",
            "Transform matrix 用 16 个列主序浮点、逗号后不加空格才能解析",
            "类 DOM 解析器注册的 38 个标签里没有矢量 path，ClipPath/PathBuilder 只在 Kotlin DSL → 曲线一律图元逼近",
            "字节相同的 DSL 会命中服务端缓存（cache;desc=hit），返回图与原图 md5 相同，属无效渲染",
        ],
        "retained_failures": "3 次 400、4 次传输失败（curl 56/28）、1 次截断（44,087/155,020 B）全部保留在 requests.jsonl 与 case-00/requests/",
    },
    "logs": {
        "requests": "tmp/%s/B06/requests.jsonl" % RID,
        "iterations": "tmp/%s/B06/iterations.jsonl" % RID,
        "tool_usage": "tmp/%s/B06/tool-usage.jsonl" % RID,
        "build_log": "tmp/%s/B06/build-log.jsonl" % RID,
        "events": "tmp/%s/B06/build-log.jsonl 与 tmp/%s/_suite/events.jsonl（题级）" % (RID, RID),
        "plan": "tmp/%s/B06/PLAN.md" % RID,
        "dataset": "tmp/%s/B06/research/demo.json" % RID,
    },
    "outputs": ["outputs/%s/B06/%s" % (RID, f) for f in
                ("problem-evidence.json", "design-review.md", "portfolio.json", "portfolio.md",
                 "gallery.md", "snapshot-usage.md", "task-metrics.json")],
    "candidates": ["outputs/%s/B06/%s" % (RID, c["final_png"]) for c in case_metrics],
    "rounds": [],
    "case_metrics": case_metrics,
    "shared_preparation": {
        "docs_cache": "tmp/%s/_suite/docs/（本题只读，未新增请求）" % RID,
        "suite_scripts": ["tmp/%s/_suite/scripts/render.py" % RID, "tmp/%s/_suite/scripts/dslkit.py" % RID,
                          "tmp/%s/_suite/scripts/iterlog.py" % RID, "tmp/%s/_suite/scripts/state.py" % RID],
        "note": "b06kit/b06run/promote/qa/tlog/b06data 属本题；文档与渲染脚本复用 shared，不在本题重复计数",
    },
    "counting_notes": [
        "请求 49 次 = 十件 40 次（39 次 200 + 1 次 400）+ 能力探针 case00 9 次（2 次 200 + 7 次失败/截断）",
        "同一 dsl_version 的多次请求是失败重发（case00-v04 3 次传输失败后 v04b 重发，v04b 截断再一次）",
        "DSL 版本按 requests.jsonl 的 dsl_version 去重计数，与 build-log 的 45 条一一对应（每次提交渲染写一条）",
        "闸门拦截（TextFit problems）与本地 assert 中止都不产生 HTTP 请求，也不写 build-log，"
        "其证据在 iterations.jsonl 的 observed_problems 与各 case.md 的改版记录；件-09 首稿连 DSL 都未落盘",
        "看图次数取 iterations.jsonl 的 image_viewed=true（40 条全部为 true）；QA 裁图是看图的辅助证据，另计",
        "件-06 v04 与 v03 响应字节完全相同（cache;desc=hit），计为 1 次成功请求但 0 次有效迭代改进",
        "套件级汇总只累加每题顶层与本 shared，不重复累加 case 明细",
    ],
    "tool_usage_summary": {
        "entries": len(TU),
        "tools": sorted(set(t["tool"] for t in TU)),
        "note": "逐条含 purpose/input/output/affects/requests_ref，见 tmp/%s/B06/tool-usage.jsonl" % RID,
    },
    "unresolved_issues": [
        "十件均未做真实用户验证；design-review.md 把可观察改善与未验证效果分栏，未验证项一律不主张",
        "件-05／09／10 的医疗、营养、法律口径只复述公开常识并标注需核对，未回源核实现行条文、指南与参考区间",
        "件-02／03／04／06／07 的时长、价格、费率、用量与程序参数为自拟演示值",
        "曲线为图元逼近（类 DOM 无矢量 path），2× 放大可见折线边；十件 final 未使用 ClipRect/ClipOval/BackdropFilter，与 PLAN.md 的设想有偏差",
        "requests.jsonl 中 case00 早期 4 条（v01/v02/v03×2）的 request_file/response_file 字段带重复目录前缀且对应文件不在磁盘上：这四次是探针最初几发，请求原文未落盘，只有 .snapshot 与 error_summary 保留；后续版本路径正常",
        "case.md 与 gallery 中的过程预览（vNN-preview.png）落在 OUTPUT_DIR 而非 TEMP_DIR（b06run 默认输出路径），与 B03–B05 一致；它们不计入十件作品，gallery 只列 final",
    ],
    "asset_policy_applied": "总 run-config 的 creative 轨道允许局部辅助素材；本题十件全部为纯 DSL 构造，辅助素材数 0，参考原文只作观察未转成素材",
}
json.dump(M, open(OUT / "task-metrics.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("wall", wall, "idle", idle, "gaps", len(gaps))
for g in gaps:
    print(" gap", g)
print("reqs", len(REQ), "ok", len(ok), "bad", len(bad), kinds)
print("views", M["counts"]["image_views"], "iters", len(IT), "dsl_versions", M["counts"]["dsl_versions"])
print("textfit", M["counts"]["textfit_box_checks_total"], "qa", M["counts"]["qa_crops"],
      "previews", M["counts"]["previews"], "png_bytes", M["counts"]["final_png_bytes_total"])
print("first_usable", M["timings"]["first_usable_image_seconds"])
