"""A24 题目层归档：追加 events.jsonl 一条事件、保存新编号检查点、刷新 suite-state.json 指针。

前置：outputs/<run_id>/A24/ 下 3 张交付 PNG + 3 份同名 .snapshot + schedule.json +
schedule-audit.json + content-map.json + delivery-manifest.json + viewing-evidence.json +
task-metrics.json + snapshot-usage.md 都已就位。本脚本只做留痕，不改任何已交付的数值、
几何或图像。

只更新 suite-state.json 这个「允许更新的当前指针」；checkpoints/state-*.json 是历史
快照，只新增编号、绝不覆盖。

用法
    python -I -X utf8 a24_state.py
"""
from __future__ import annotations

import datetime as dt
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
ROOT = HERE.parents[4]
RUN_ID = HERE.parents[2].name
OUT_ROOT = ROOT / "outputs" / RUN_ID
TMP_ROOT = ROOT / "tmp" / RUN_ID
STATE = OUT_ROOT / "_suite" / "suite-state.json"
EVENTS = TMP_ROOT / "_suite" / "events.jsonl"
CKPT = TMP_ROOT / "_suite" / "checkpoints"
TZ = dt.timezone(dt.timedelta(hours=8))
NOW = dt.datetime.now(TZ).isoformat(timespec="seconds")

A = "A24"
NEXT = "B01"
A_DIR = OUT_ROOT / A

DELIVERABLES = [
    "execution-board.png", "execution-board.snapshot",
    "decision-brief.png", "decision-brief.snapshot",
    "action-card.png", "action-card.snapshot",
    "schedule.json", "schedule-audit.json",
    "content-map.json", "delivery-manifest.json",
    "viewing-evidence.json",
    "snapshot-usage.md", "task-metrics.json",
]
SCRIPTS = [
    "tmp/%s/_suite/gen/a24_sched.py",
    "tmp/%s/_suite/gen/a24_deliver.py",
    "tmp/%s/_suite/gen/a24_pages.py",
    "tmp/%s/_suite/gen/a24_map.py",
    "tmp/%s/_suite/gen/a24_difftext.py",
    "tmp/%s/_suite/gen/a24_evidence.py",
    "tmp/%s/_suite/gen/a24_metrics.py",
    "tmp/%s/_suite/gen/a24_state.py",
]


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")

    metrics_path = A_DIR / "task-metrics.json"
    usage_path = A_DIR / "snapshot-usage.md"
    missing = [p.name for p in (metrics_path, usage_path)
               if not p.exists() or p.stat().st_size == 0]
    for name in DELIVERABLES:
        if not (A_DIR / name).exists() or (A_DIR / name).stat().st_size == 0:
            missing.append(name)
    if missing:
        raise SystemExit("缺少题目层交付件：%s" % "、".join(missing))

    m = json.loads(metrics_path.read_text(encoding="utf-8"))
    aud = json.loads((A_DIR / "schedule-audit.json").read_text(encoding="utf-8"))
    cmap = json.loads((A_DIR / "content-map.json").read_text(encoding="utf-8"))
    ev = json.loads((A_DIR / "viewing-evidence.json").read_text(encoding="utf-8"))
    gates = json.loads((TMP_ROOT / A / "page-gates.json").read_text(encoding="utf-8"))
    tm = m["timings"]
    c = m["counts"]
    sr = m["schedule_result"]

    doc = json.loads(STATE.read_text(encoding="utf-8"))
    entry = {
        "id": A,
        "status": "completed",
        "status_note": (
            "TASK.md 逐项核对全部满足：1920×1080 执行泳道 + 1200×1600 决策简报 + "
            "720×1280 手机行动卡，三张图全部由 schedule.json 渲染、字节等于服务原始"
            "响应，且与当前构建器重建的 DSL 在换行归一化后逐字节一致。420 分钟窗口内"
            "12 任务全部执行，完工第 260 分钟（2026-11-07T13:20+08:00）、缓冲 160 分钟，"
            "总工作量 485 分钟。排程经 2^3=8 种指派全枚举 + 分支定界（1032 个节点、"
            "search_exhausted=true、aborted_by_node_cap=false）核验为全局最优；"
            "关键路径下界 255 分钟不紧，多出的 5 分钟全部来自 R04→R07，已如实披露而非"
            "掩盖成「达到下界」；工作量下界 242.5 分钟保留小数、不提前取整。"
            "8/8 排程审计、22/22 干跑门禁、16/16 跨图一致性检查通过；两轮共 9 次实际"
            "看图，第一轮在决策简报文字层发现的 5 处缺陷已在第二轮消除，"
            "执行泳道与手机卡两轮字节恒等（零回归）"
        ),
        "execution_mode": "单轮：本题不是预置多轮题；两轮渲染是视觉迭代，不是预置轮次",
        "started_at": tm["started_at"],
        "started_at_note": tm["started_at_note"],
        "output_dir": "outputs/%s/%s" % (RUN_ID, A),
        "temp_dir": "tmp/%s/%s" % (RUN_ID, A),
        "ended_at": tm["ended_at"],
        "ended_at_note": tm["ended_at_note"],
        "elapsed_seconds": tm["elapsed_seconds"],
        "elapsed_note": tm["elapsed_note"],
        "work_started_at": tm["work_started_at"],
        "work_started_at_note": tm["work_started_at_note"],
        "total_wall_seconds": tm["total_wall_seconds"],
        "total_wall_note": tm["total_wall_note"],
        "phase_wall_seconds": tm["phase_wall_seconds"],
        "phase_wall_note": tm["phase_wall_note"],
        "final_images": c["final_images"],
        "final_images_required": c["final_images_required"],
        "final_images_note": c["final_images_note"],
        "artifacts": ["outputs/%s/%s/%s" % (RUN_ID, A, n) for n in DELIVERABLES],
        "metrics": "outputs/%s/%s/task-metrics.json" % (RUN_ID, A),
        "logs": {
            "requests": "tmp/%s/%s/requests.jsonl" % (RUN_ID, A),
            "iterations": "tmp/%s/%s/iterations.jsonl" % (RUN_ID, A),
            "page_gates": "tmp/%s/%s/page-gates.json" % (RUN_ID, A),
            "viewing_evidence": "outputs/%s/%s/viewing-evidence.json" % (RUN_ID, A),
            "solve_result": "tmp/%s/%s/solve-result.json" % (RUN_ID, A),
            "delivery_manifest": "tmp/%s/%s/delivery-manifest.json" % (RUN_ID, A),
            "task_metrics_copy": "tmp/%s/%s/task-metrics.json" % (RUN_ID, A),
            "dsl_versions": "tmp/%s/%s/dsl/" % (RUN_ID, A),
            "responses": "tmp/%s/%s/responses/" % (RUN_ID, A),
        },
        "quality_gates": {
            "schedule_audit": "%d/%d" % (c["schedule_audit_checks_passed"],
                                         c["schedule_audit_checks_total"]),
            "schedule_audit_report": "outputs/%s/%s/schedule-audit.json" % (RUN_ID, A),
            "schedule_audit_note": (
                "A01 时长严格等于输入、A02 start≥0 且 end≤420、A03 同团队 [start,end) "
                "不重叠、A04 依赖 end ≤ 后继 start、A05 执行团队在候选内、"
                "A06 12 任务集合与输入相等、A07 每任务在其团队里恰好一段（不被抢占或拆分）、"
                "A08 风险未计入固定时长；feasible=true、failed=[]"
            ),
            "dryrun": "%d/%d" % (gates["passed"], gates["total"]),
            "dryrun_report": "tmp/%s/%s/page-gates.json" % (RUN_ID, A),
            "dryrun_note": (
                "3 图 × 3 项通用门禁（画布内 / 同层不重叠 / 字号下限）+ 泳道 6 项 + "
                "简报 5 项 + 手机卡 2 项专项门禁；每次渲染前重跑，失败即拒绝渲染，"
                "不靠渲染后发现"
            ),
            "cross_image_consistency": "%d/%d"
                                       % (c["cross_image_checks_passed"],
                                          c["cross_image_checks_total"]),
            "cross_image_report": "outputs/%s/%s/content-map.json" % (RUN_ID, A),
            "cross_image_note": c["cross_image_checks_note"],
            "visual_review": "%d 次实际看图（两轮各 3 件 + 交付版 3 件）" % c["image_views"],
            "visual_review_report": "outputs/%s/%s/viewing-evidence.json" % (RUN_ID, A),
            "defects_found": c["defects_found"],
            "defects_all_fixed": True,
            "gates_added_this_round": c["gates_added"],
            "byte_identity": "3/3（交付 PNG 的 sha256 等于服务原始响应字节）",
            "dsl_identity": "3/3 换行归一化后与当前构建器重建逐字节一致"
                            "（落盘为 CRLF，原始字节口径记为 false 并附原因）",
            "font_floor": "泳道 20 px / 简报 24 px / 手机卡 20 px，全部满足题设下限",
            "color_check": "两个团队色过色盲校验：deutan ΔE 27.6、tritan ΔE 13.3、"
                           "normal ΔE 30.8；warning 与 danger 一律带文字标签",
        },
        "schedule_result": {
            "window_minutes": sr["window_minutes"],
            "origin": sr["origin"],
            "deadline": sr["deadline"],
            "task_count": sr["task_count"],
            "flexible_tasks": sr["flexible_tasks"],
            "workload_minutes": sr["workload_minutes"],
            "finish_minute": sr["finish_minute"],
            "finish_time": sr["finish_time"],
            "buffer_minutes": sr["buffer_minutes"],
            "critical_path_lower_bound_minutes": sr["critical_path_lower_bound_minutes"],
            "critical_path": sr["critical_path"],
            "workload_lower_bound_minutes": sr["workload_lower_bound_minutes"],
            "workload_lower_bound_note": sr["workload_lower_bound_note"],
            "binding_lower_bound": sr["binding_lower_bound"],
            "gap_to_lower_bound_minutes": sr["gap_to_lower_bound_minutes"],
            "gap_note": sr["gap_note"],
            "idle_minutes": sr["idle_minutes"],
            "idle_ranges": sr["idle_ranges"],
            "provably_globally_optimal": sr["provably_globally_optimal"],
            "assignments_enumerated": sr["assignments_enumerated"],
            "search_nodes": sr["search_nodes"],
            "search_exhausted": sr["search_exhausted"],
            "aborted_by_node_cap": sr["aborted_by_node_cap"],
            "claim_wording": sr["claim_wording"],
        },
        "delivery_verified_by": (
            "delivery-manifest.json 的 all_bytes_unchanged=true、"
            "all_images_have_snapshot=true，逐件记录 png_sha256 与 response_sha256 相等；"
            "content-map.json 的 CM-16 复算 PNG IHDR 尺寸与字节恒等；"
            "CM-01～CM-16 全部从交付的 .snapshot 反查真实文本与矩形几何后与 "
            "schedule.json / schedule-audit.json / inputs 复算比对"
        ),
        "requests": c["http_requests"],
        "http_requests": c["http_requests"],
        "http_requests_note": c["http_requests_note"],
        "successful_requests": c["successful_requests"],
        "failed_requests": c["failed_requests"],
        "by_http_status": c["by_http_status"],
        "by_error": c["by_error"],
        "server_rejected": c["server_rejected"],
        "retry_requests": c["retry_requests"],
        "retry_after_used": c["retry_after_used"],
        "rate_limit_wait_seconds": c["rate_limit_wait_seconds"],
        "transport_read_timeout_seconds": c["transport_read_timeout_seconds"],
        "queue_wait_seconds": c["queue_wait_seconds"],
        "queue_wait_null_reason": c["queue_wait_null_reason"],
        "user_feedback_wait_seconds": c["user_feedback_wait_seconds"],
        "submission_groups": c["submission_groups"],
        "submission_groups_ok": c["submission_groups_ok"],
        "image_views": c["image_views"],
        "image_views_note": c["image_views_note"],
        "events_logged": c["events_logged"],
        "completed_visual_iterations": c["completed_visual_iterations"],
        "completed_visual_iterations_note": c["completed_visual_iterations_note"],
        "defects_found": c["defects_found"],
        "defects_found_note": c["defects_found_note"],
        "gates_added": c["gates_added"],
        "gates_added_note": c["gates_added_note"],
        "report_generator_fixes": c["report_generator_fixes"],
        "report_generator_fixes_note": c["report_generator_fixes_note"],
        "iterations_total": c["iterations_total"],
        "iterations_note": c["iterations_note"],
        "json_artifacts": c["json_artifacts"],
        "report_artifacts": c["report_artifacts"],
        "dryrun_gates_total": gates["total"],
        "dryrun_gates_passed": gates["passed"],
        "schedule_audit_checks_total": c["schedule_audit_checks_total"],
        "schedule_audit_checks_passed": c["schedule_audit_checks_passed"],
        "cross_image_checks_total": c["cross_image_checks_total"],
        "cross_image_checks_passed": c["cross_image_checks_passed"],
        "request_duration_sum_seconds": tm["request_duration_sum_seconds"],
        "transport_read_timeout_seconds": tm["transport_read_timeout_seconds"],
        "rate_limit_wait_seconds": tm["rate_limit_wait_seconds"],
        "counting_note": (
            "requests = http_requests = successful_requests = 6：按 requests.jsonl 记录"
            "条数，两轮各 3 件，全部 HTTP 200、无重试、无 429/503、无读超时。"
            "request_duration_sum_seconds（%s s）只统计本地实测往返，与 elapsed_seconds"
            "（%s s）、total_wall_seconds（%s s）、phase_wall_seconds 之和（%s s）都"
            "不同口径、不可相加。total_wall_seconds 才是覆盖全部工作（含首条请求之前的"
            "求解与审计阶段）的墙钟；阶段之和对应 total_wall_seconds 而不是 "
            "elapsed_seconds，两者都保留、不互相凑平。queue_wait_seconds 为 null"
            "（服务端不可观测），不记 0。completed_visual_iterations=1 与 "
            "report_generator_fixes=%d 分开统计：前者改图并重渲，后者只改报告生成器、"
            "不影响任何已交付字节。events_logged 只记本题 1 条 task_completed，"
            "两轮渲染与 9 次看图不重复计入套级指标"
            % (tm["request_duration_sum_seconds"], tm["elapsed_seconds"],
               tm["total_wall_seconds"], sum(tm["phase_wall_seconds"].values()),
               c["report_generator_fixes"])
        ),
        "task_level_artifacts": {
            "snapshot_usage": "outputs/%s/%s/snapshot-usage.md" % (RUN_ID, A),
            "snapshot_usage_bytes": usage_path.stat().st_size,
            "task_metrics": "outputs/%s/%s/task-metrics.json" % (RUN_ID, A),
            "task_metrics_bytes": metrics_path.stat().st_size,
            "written_at": NOW,
            "note": (
                "题目层累计报告与指标已生成。task-metrics.json 的 path_base=suite_root、"
                "deliverables.path_base=output_dir，7 个阶段墙钟互不重叠。"
                "snapshot-usage.md 汇总 13 个交付件、12 任务排程表、两个下界与最优性证据"
                "（含 8 种指派的每指派最优）、三图分工与四层核验口径、9 次看图与 5 处"
                "缺陷的原文/改后/依据、DSL 用法、能力边界 5 项判定与 12 条踩坑"
            ),
        },
        "unresolved_issues": m["unresolved_issues"],
    }

    # ---- 写入 suite-state.json
    detail = doc.setdefault("tasks_detail", [])
    if any(t.get("id") == A for t in detail):
        detail[:] = [entry] + [t for t in detail if t.get("id") != A]
    else:
        detail.append(entry)
        detail.sort(key=lambda t: t.get("id", ""))

    doc["counts_by_status"]["completed"] = doc["counts_by_status"].get("completed", 0) + 1
    doc["counts_by_status"]["pending"] = max(0, doc["counts_by_status"].get("pending", 0) - 1)
    completed = list(doc.get("completed", []))
    if A not in completed:
        completed.append(A)
    doc["completed"] = completed
    remaining = [t for t in doc.get("remaining", []) if t != A]
    doc["remaining"] = remaining
    doc["current_task"] = NEXT
    n_detail = len(detail)
    ids = [t.get("id") for t in detail]
    doc["updated_at"] = NOW
    doc["updated_at_note"] = (
        "%s 归档 A24：题目层 13 个交付文件全部就位（3 张 PNG + 3 份同名 DSL + schedule.json "
        "+ schedule-audit.json + content-map.json + delivery-manifest.json + "
        "viewing-evidence.json + snapshot-usage.md + task-metrics.json）。tasks_detail 的 "
        "A24 条目写入完整明细，completed 23→24、pending 7→6、current_task 指向 B01。"
        "追加 1 条 events.jsonl 事件，保存新编号检查点" % NOW
    )
    doc["tasks_detail_note"] = (
        "tasks_detail 目前逐题记录了 %s–%s 共 %d 条；A01–A08 只出现在 completed 清单里，"
        "没有对应的逐题明细条目（缺起止时间、请求数、指标路径）。该缺口是 A09 之前遗留的"
        "记录问题，不补造：补造需要当时的真实产物与日志，凭空填会制造虚假留痕，"
        "逐题明细以各题 task-metrics.json 与 outputs/<run_id>/<task_id>/ 目录为准"
        % (ids[0], ids[-1], n_detail)
    )
    doc["suite_progress_note"] = (
        "A01–A24 共 24 题完成；A24（发布演练排程）全部交付就位：1920×1080 执行泳道 + "
        "1200×1600 决策简报 + 720×1280 手机行动卡（3 件最终图），加 schedule.json"
        "（12 任务精确起止/团队/依赖）、schedule-audit.json（8 项约束检查、两个下界、"
        "最优性搜索）、content-map.json（逐元素定位 + 11 条声明 + 16 项跨图一致性）、"
        "delivery-manifest.json、viewing-evidence.json（9 次看图）、snapshot-usage.md、"
        "task-metrics.json，共 13 个文件。420 分钟窗口内 12 任务全部执行，总工作量 485 分钟，"
        "完工第 260 分钟（2026-11-07T13:20+08:00）、缓冲 160 分钟；关键路径下界 255 分钟"
        "不紧、多出的 5 分钟全在 R04→R07 并已如实披露；工作量下界 242.5 分钟保留小数不取整。"
        "8 种指派全枚举 + 分支定界（1032 节点、search_exhausted=true、"
        "aborted_by_node_cap=false）核验为全局最优。8/8 排程审计、22/22 干跑门禁、"
        "16/16 跨图一致性、3/3 交付字节恒等；6 次 POST /snapshot 全部 200（无重试、"
        "无 429/503、无读超时），9 次实际看图、1 次视觉迭代、第一轮发现的 5 处文字缺陷"
        "全部修复、新增 4 条门禁、报告生成器 11 处修复。请求往返合计 %s s、累计墙钟 "
        "%.0f s。B01–B06 共 6 题待执行"
        % (tm["request_duration_sum_seconds"], tm["total_wall_seconds"])
    )
    STATE.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n",
                     encoding="utf-8")

    # ---- 事件
    ev_row = {
        "ts": NOW,
        "timezone": "Asia/Shanghai (UTC+08:00)",
        "event": "task_completed",
        "task_id": A,
        "run_id": RUN_ID,
        "output_dir": "outputs/%s/%s" % (RUN_ID, A),
        "temp_dir": "tmp/%s/%s" % (RUN_ID, A),
        "artifacts": ["outputs/%s/%s/%s" % (RUN_ID, A, n) for n in DELIVERABLES],
        "final_images": c["final_images"],
        "final_images_required": c["final_images_required"],
        "requests": c["http_requests"],
        "http_requests": c["http_requests"],
        "successful_requests": c["successful_requests"],
        "failed_requests": c["failed_requests"],
        "retry_requests": c["retry_requests"],
        "retry_after_used": c["retry_after_used"],
        "rate_limit_wait_seconds": c["rate_limit_wait_seconds"],
        "transport_read_timeout_seconds": c["transport_read_timeout_seconds"],
        "queue_wait_seconds": c["queue_wait_seconds"],
        "user_feedback_wait_seconds": c["user_feedback_wait_seconds"],
        "submission_groups": c["submission_groups"],
        "submission_groups_ok": c["submission_groups_ok"],
        "image_views": c["image_views"],
        "visual_iterations": c["completed_visual_iterations"],
        "defects_found": c["defects_found"],
        "gates_added": c["gates_added"],
        "report_generator_fixes": c["report_generator_fixes"],
        "iterations_total": c["iterations_total"],
        "dryrun_gates": "%d/%d" % (gates["passed"], gates["total"]),
        "schedule_audit": "%d/%d" % (c["schedule_audit_checks_passed"],
                                     c["schedule_audit_checks_total"]),
        "cross_image_consistency": "%d/%d" % (c["cross_image_checks_passed"],
                                              c["cross_image_checks_total"]),
        "window_minutes": sr["window_minutes"],
        "task_count": sr["task_count"],
        "workload_minutes": sr["workload_minutes"]["total"],
        "finish_minute": sr["finish_minute"],
        "finish_time": sr["finish_time"],
        "buffer_minutes": sr["buffer_minutes"],
        "critical_path_lower_bound_minutes": sr["critical_path_lower_bound_minutes"],
        "critical_path": sr["critical_path"],
        "workload_lower_bound_minutes": sr["workload_lower_bound_minutes"],
        "binding_lower_bound_minutes": sr["binding_lower_bound"]["minutes"],
        "binding_lower_bound_which": sr["binding_lower_bound"]["which"],
        "gap_to_lower_bound_minutes": sr["gap_to_lower_bound_minutes"],
        "idle_minutes": sr["idle_minutes"],
        "provably_globally_optimal": sr["provably_globally_optimal"],
        "assignments_enumerated": sr["assignments_enumerated"],
        "search_nodes": sr["search_nodes"],
        "search_exhausted": sr["search_exhausted"],
        "aborted_by_node_cap": sr["aborted_by_node_cap"],
        "claim_wording": sr["claim_wording"],
        "request_duration_sum_seconds": tm["request_duration_sum_seconds"],
        "wall_clock_seconds": tm["elapsed_seconds"],
        "total_wall_seconds": tm["total_wall_seconds"],
        "started_at": tm["started_at"],
        "ended_at": tm["ended_at"],
        "detail": (
            "A24（发布演练排程）完成：420 分钟窗口（09:00 开工、16:00 截止，09:00 = 第 0 分钟）"
            "内 12 个任务全部执行，design 与 engineering 各一个团队、同团队不并行不抢占无"
            "切换耗时；tasks.teams 双团队任务 R05/R09/R12 只占一个团队。总工作量 485 分钟"
            "（design 255 · engineering 230），完工第 260 分钟 = 2026-11-07T13:20+08:00，"
            "缓冲 160 分钟；关键路径 R01→R04→R07→R09→R10→R12 = 255 分钟，工作量下界 "
            "485/2 = 242.5 分钟（保留小数、不提前取整），绑定下界是关键路径 255 分钟。"
            "排程比关键路径下界多 5 分钟、全部在 R04→R07 之间（R07 等前驱 R05，"
            "R05 只能排到 engineering），已如实披露而非写成「达到下界」。"
            "2^3 = 8 种指派全枚举 + 每种分支定界，1032 个节点、search_exhausted=true、"
            "aborted_by_node_cap=false，声明的是已核验的全局最优。三张图全部由 "
            "schedule.json 渲染，依赖用编号索引表达而非交叉连线；真实时间等比（1 分钟 = 4 像素）、"
            "空档斜纹、16:00 截止线与缓冲带齐全。8/8 排程审计、22/22 干跑门禁、"
            "16/16 跨图一致性检查、3/3 交付字节恒等于服务原始响应；9 次实际看图，"
            "第一轮在决策简报文字层发现 5 处缺陷（2 事实错误 / 1 归因错误 / 1 缺证据 / "
            "1 量纲混淆），第二轮全部消除，泳道与手机卡两轮字节恒等（零回归）。"
            "6 次 POST /snapshot 全部 200、无重试、无 429/503、无读超时。"
            "已知限制 3 项全部 disclosed：关键路径下界不紧、第一轮看图时刻无独立时间戳"
            "（只给区间 + retroactive=true）、K1 风险文案有排版归一化（TN-01，语义未变）"
        ),
        "task_status": "completed",
        "next_task": NEXT,
        "suite_counts_by_status": dict(doc["counts_by_status"]),
    }
    with EVENTS.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(ev_row, ensure_ascii=False) + "\n")

    # ---- 新编号检查点
    CKPT.mkdir(parents=True, exist_ok=True)
    existing = sorted(p.name for p in CKPT.glob("state-*.json"))
    n = len(existing) + 1
    cp_path = CKPT / ("state-%06d.json" % n)
    cp = {
        "checkpoint": n,
        "created_at": NOW,
        "timezone": "Asia/Shanghai (UTC+08:00)",
        "reason": "A24 全部交付完成并归档（13 个文件、3 张最终图），进入 B01",
        "suite_state_snapshot": dict(doc),
        "event_count": len(EVENTS.read_text(encoding="utf-8").splitlines()),
        "restore": {
            "how": (
                "suite-state.json 允许更新，恢复时以最新 checkpoint 的 "
                "suite_state_snapshot 为准；A24 已 completed，13 个交付文件均已就位"
                "且不覆盖；下一题 B01 按 catalog.json 的 task_order 继续，"
                "B01–B06 各至少 10 件独立完整作品并需 tool-usage.jsonl"
            ),
            "resume_from": "tasks/B01-*（按 catalog.json 的 task_order）",
            "done_in_this_checkpoint": [
                "A01–A24 共 24 题 completed",
                "A24 全部 13 个交付文件（3 PNG + 3 DSL + 6 份 JSON + 1 份 MD 报告）",
                "A24 的 8/8 排程审计、22/22 干跑门禁、16/16 跨图一致性、3/3 字节恒等",
            ],
            "scripts": [s % RUN_ID for s in SCRIPTS],
            "pending": [
                "继续 B01–B06（共 6 题）",
                "B01–B06 各至少 10 件独立完整作品（≥60 件），另需 tool-usage.jsonl",
                "全部 30 题完成后生成套级 index.md / gallery.md / snapshot-usage.md / "
                "task-metrics.json 并做总审查",
                "套级 suite-state.json 的 required_artifacts_delivered 目前为 1/5，"
                "其余 4 件由总审查补齐",
            ],
        },
    }
    cp_path.write_text(json.dumps(cp, ensure_ascii=False, indent=1) + "\n",
                       encoding="utf-8")

    doc["last_checkpoint"] = "tmp/%s/_suite/checkpoints/%s" % (RUN_ID, cp_path.name)
    STATE.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n",
                     encoding="utf-8")

    print("suite-state 已写 A24 明细，updated_at=%s" % NOW)
    print("counts_by_status=%s" % doc["counts_by_status"])
    print("current_task=%s remaining=%s" % (doc["current_task"], doc["remaining"]))
    print("tasks_detail %d 条：%s" % (n_detail, "、".join(ids)))
    print("events.jsonl 追加 1 条，当前 %d 条"
          % len(EVENTS.read_text(encoding="utf-8").splitlines()))
    print("检查点 %s" % cp_path.name)
    print("last_checkpoint -> %s" % doc["last_checkpoint"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
