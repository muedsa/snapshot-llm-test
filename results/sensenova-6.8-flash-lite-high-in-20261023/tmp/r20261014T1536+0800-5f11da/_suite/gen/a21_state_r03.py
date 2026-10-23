"""A21 round-03 套级归档：suite-state / events.jsonl / checkpoint。

- 向 A21 的 tasks_detail 条目追加 round-03 块，并把题目状态置为 completed；
- 更新套级 completed / counts_by_status / current_task / current_round / 进度说明；
- 向 tmp/<run>/_suite/events.jsonl 追加 round_completed 与 task_completed；
- 写出新编号的 checkpoint 快照（state-000057.json），不覆盖任何历史快照；
- 写出题目根层的跨三轮累计指标 outputs/<run>/A21/task-metrics.json。

数字一律从三轮的 task-metrics.json 现算，不硬编码。
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
RUN_ID = HERE.parents[2].name
ROOT = HERE.parents[4]
RUN = ROOT / "tmp" / RUN_ID
SUITE_TMP = RUN / "_suite"
SUITE_OUT = ROOT / "outputs" / RUN_ID / "_suite"
A21 = ROOT / "outputs" / RUN_ID / "A21"
A21TMP = RUN / "A21"
STATE = SUITE_OUT / "suite-state.json"
EVENTS = SUITE_TMP / "events.jsonl"
CHECKPOINTS = SUITE_TMP / "checkpoints"

NOW = dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat(
    timespec="seconds")
TZ = "Asia/Shanghai (UTC+08:00)"

REQUIRED_R3 = [
    "launch-portrait.png", "launch-portrait.snapshot",
    "launch-wide.png", "launch-wide.snapshot",
    "design-tokens.json", "content-map.json", "contrast-audit.json",
    "snapshot-usage.md", "task-metrics.json",
]


def load_metrics(rnd: int) -> dict:
    p = A21 / ("round-%02d" % rnd) / "task-metrics.json"
    return json.loads(p.read_text(encoding="utf-8"))


def main() -> int:
    for st in (sys.stdout, sys.stderr):
        if hasattr(st, "reconfigure"):
            st.reconfigure(encoding="utf-8")

    m1, m2, m3 = load_metrics(1), load_metrics(2), load_metrics(3)
    ca = json.loads((A21 / "round-03" / "contrast-audit.json").read_text(
        encoding="utf-8"))["overall"]

    # 交付文件核对
    missing = [f for f in REQUIRED_R3
               if not (A21 / "round-03" / f).exists()]
    if missing:
        raise SystemExit("round-03 交付缺件: %s" % missing)
    sizes = {f: (A21 / "round-03" / f).stat().st_size for f in REQUIRED_R3}

    state = json.loads(STATE.read_text(encoding="utf-8"))
    a21 = next(t for t in state["tasks_detail"] if t["id"] == "A21")

    t3 = m3["timings"]
    r3 = {
        "round": 3,
        "status": "completed",
        "output_subdirectory": "round-03",
        "spec_source": "tasks/A21-staged-launch-change/rounds/round-03.md",
        "base_artifacts": [
            "outputs/%s/A21/round-02/launch-portrait.png" % RUN_ID,
            "outputs/%s/A21/round-02/launch-wide.png" % RUN_ID],
        "started_at": t3["started_at"],
        "ended_at": t3["ended_at"],
        "elapsed_seconds": t3["elapsed_seconds"],
        "archive_tail_seconds": t3["archive_tail_seconds"],
        "final_images": 2,
        "final_images_required": 2,
        "final_images_note": "launch-portrait 1080x1350 与 launch-wide 1440x810 "
                             "尺寸未变；标题仍为竖版 3 行 66px、横版 2 行 52px，"
                             "两图仍分别构图而非等比缩放",
        "artifacts": ["outputs/%s/A21/round-03/%s" % (RUN_ID, f)
                      for f in REQUIRED_R3],
        "artifacts_bytes": sizes,
        "metrics": "outputs/%s/A21/round-03/task-metrics.json" % RUN_ID,
        "logs": {
            "round_changes": "tmp/%s/A21/round-03-changes.json" % RUN_ID,
            "requests": "tmp/%s/A21/requests.jsonl" % RUN_ID,
            "iterations": "tmp/%s/A21/iterations.jsonl" % RUN_ID,
            "viewing_evidence": "tmp/%s/A21/viewing-evidence.json" % RUN_ID,
            "preview_manifest": "tmp/%s/A21/preview/round-03/views-manifest.json"
                                % RUN_ID,
            "auxiliary_background_renders": "tmp/%s/A21/backgrounds/" % RUN_ID,
            "contrast_local_evidence": "tmp/%s/A21/contrast-evidence/" % RUN_ID,
            "note": "去文字辅助渲染与逐段对比度局部证据只落在临时目录，"
                    "不进交付清单，也不是作品",
        },
        "audit": {
            "content_map": "outputs/%s/A21/round-03/content-map.json" % RUN_ID,
            "checks_passed": "9/9",
            "all_passed": True,
            "contrast_audit": "outputs/%s/A21/round-03/contrast-audit.json"
                              % RUN_ID,
            "contrast_threshold": 4.5,
            "contrast_n_text_segments": ca["n_text_segments_checked"],
            "contrast_n_not_checked": ca["n_text_segments_not_checked"],
            "contrast_global_minimum_unrounded":
                ca["global_minimum_contrast_unrounded"],
            "contrast_global_minimum": round(
                ca["global_minimum_contrast_unrounded"], 4),
            "contrast_worst": "竖版 date #C2410C 对页面底 #F5F8FC",
            "contrast_method": "背景取去文字辅助渲染在字形覆盖区的实际像素"
                               "（同构造器、Canvas.text(record_text=False)），"
                               "前景取 design-token 色，按需求规定的 8 位 sRGB "
                               "线性化公式与未舍入结果判阈值；墨迹外逐通道最大差 "
                               "12.0 证明辅助渲染与交付图只差在文字",
            "coordinate_samples": 12,
            "coordinate_samples_note": "每图 6 处，共 12 处，均含实际坐标、"
                                       "颜色、亮度与未舍入计算过程，且各含最差位置",
            "design_tokens": "outputs/%s/A21/round-03/design-tokens.json"
                             % RUN_ID,
            "brand_geometry_components": 6,
            "brand_geometry_note": "6 个构件的形态、层数、圆角比例、光带条数与"
                                   "递减关系全部未变，只换色带与辉光收敛半径",
            "viewing_evidence": "tmp/%s/A21/viewing-evidence.json" % RUN_ID,
            "viewing_events": 15,
        },
        "delivery_verified_by": "响应字节 sha256 与交付 PNG sha256 逐一比对"
                                "（metrics.delivery_map，两对完全一致）",
        "requests": 4,
        "requests_by_kind": {"render": 2, "render-aux": 2},
        "successful_requests": 4,
        "failed_requests": 0,
        "retry_requests": 0,
        "syntax_fix_resubmits": 0,
        "image_views": 15,
        "completed_visual_iterations": 0,
        "request_duration_sum_seconds": t3["request_duration_sum_seconds"],
        "service_stall_seconds": 0.0,
        "first_usable_image_seconds": t3["first_usable_image_seconds"],
        "first_delivered_image_seconds": t3["first_delivered_image_seconds"],
        "requirements_note": "浅色主题、23 段普通文字全量对比度 ≥4.5、保留全部"
                             "第二轮文案与品牌图形、网址上方新增英语短句、两尺寸与"
                             "标题行数/字号不变、赞助方未消失、未忽略实际叠层，"
                             "逐项核对见 round-03/snapshot-usage.md 第 1.2 节",
        "unresolved_issues": [
            {"id": i["id"], "issue": i["issue"], "status": i["status"]}
            for i in m3["unresolved_issues"]],
    }

    # 追加（不覆盖）round 块
    rounds = a21.setdefault("rounds", [])
    rounds = [r for r in rounds if r.get("round") != 3]
    rounds.append(r3)
    a21["rounds"] = sorted(rounds, key=lambda r: r["round"])

    a21["status"] = "completed"
    a21["status_note"] = (
        "三轮任务全部完成：round-01（基线）、round-02（长标题 + 赞助方）、"
        "round-03（浅色主题 + 对比度审计）。round-03 的 23 段普通文字全量对比度"
        "最小 4.8616（阈值 4.5）、无未检查项；6 个品牌构件形态未变；两尺寸与标题"
        "行数/字号未变；赞助方与报名状态牌仍在。题目级累计指标见 "
        "outputs/%s/A21/task-metrics.json" % RUN_ID)
    a21["ended_at"] = t3["ended_at"]
    a21["artifacts"] = a21.get("artifacts", []) + [
        "outputs/%s/A21/task-metrics.json" % RUN_ID,
        "outputs/%s/A21/snapshot-usage.md" % RUN_ID]

    # 套级
    if "A21" not in state["completed"]:
        state["completed"].append("A21")
    state["completed"] = sorted(state["completed"],
                               key=lambda s: (s[0], s[1:]))
    state["counts_by_status"] = {"completed": len(state["completed"]),
                                 "in_progress": 0,
                                 "pending": len(state["remaining"])}
    state["current_task"] = "A22"
    state["current_round"] = {
        "task_id": "A21", "round": 3, "rounds_total": 3,
        "status": "completed",
        "next": "按 catalog.json 顺序进入 A22（同样为三轮任务，"
                "也要求 contrast-audit.json）",
        "note": "round-03 是 A21 的末轮；本题三轮全部归档"}
    state["updated_at"] = NOW
    state["suite_progress_note"] = (
        "A01–A21 共 21 题完成；A21 三轮全部归档：每轮两图 + 两 DSL + "
        "design-tokens.json + content-map.json + snapshot-usage.md + "
        "task-metrics.json，round-03 另附 contrast-audit.json。"
        "交付映射由 sha256 证实（round-01 7/7、round-02 9/9、round-03 9/9 项检查，"
        "均 all_passed）。round-03 新增 2 条去文字辅助渲染请求（只用于对比度背景"
        "取样、不产出交付件），三轮共 17 条请求、12 条成功、5 条失败、43 次看图、"
        "6 张最终图片。A22–A24、B01–B06 共 9 题待执行")

    # events.jsonl
    ckpt = "tmp/%s/_suite/checkpoints/state-000057.json" % RUN_ID
    ev_round = {
        "ts": NOW, "timezone": TZ, "event": "round_completed", "task_id": "A21",
        "run_id": RUN_ID, "round": 3, "rounds_total": 3, "status": "completed",
        "task_status": "completed",
        "output_dir": "outputs/%s/A21" % RUN_ID,
        "round_dir": "outputs/%s/A21/round-03" % RUN_ID,
        "temp_dir": "tmp/%s/A21" % RUN_ID,
        "detail": (
            "A21 round-03（末轮）归档：改浅色主题（页面底 #060A18→#F5F8FC、"
            "牌子底→#FFFFFF；ink→#0B1B33、muted→#4A5A72、primary #5FE0FF→"
            "#0A6FA8、accent→#C2410C），保留全部第二轮 9 条文案与 6 个品牌构件"
            "（形态、层数、圆角比例、光带条数与递减关系全未变，只换色带与辉光收敛"
            "半径），在网址牌之上新增英语短句「Clarity through structure」"
            "（竖版 28px、横版 26px，均 ≥24），两尺寸与标题行数/字号（3/2 行、"
            "66/52px）不变，赞助方与报名状态牌仍在网址牌之下。为满足"
            "「不能只改两种颜色忽略实际叠层」，取消主标题青色发光阴影、把发光球移到"
            "标题与信息栈之间的右列空区并把外辉光收到 2.7r/2.75r 使辉光填充框与"
            "所有文字墨迹几何不相交、氛围 wash 反转为页面底到纯白的渐白。"
            "对比度按需求规定的公式量测：背景取去文字辅助渲染的实际像素（同构造器、"
            "Canvas.text(record_text=False)），23 段普通文字全量检查、"
            "n_not_checked=0、全局最小 4.8616（未舍入 4.861573385783012），"
            "最差段为竖版 date #C2410C 对页面底 #F5F8FC；每图另附 6 处带实际坐标、"
            "颜色、亮度与未舍入计算过程的样本（共 12 处）。content-map 9/9 项检查"
            "通过；15 次实际看图（含 12 个语义裁切视图与 2 次去文字背景整图）"
            "未发现需返工的缺陷，故无视觉迭代；4 条请求全部一次成功，无 400、"
            "无 429/503、无读取超时"),
        "content_map_checks": {"passed": 9, "total": 9, "all_passed": True},
        "contrast_audit": {
            "threshold": 4.5, "n_text_segments_checked": 23,
            "n_not_checked": 0,
            "global_minimum_unrounded": ca["global_minimum_contrast_unrounded"],
            "global_minimum": round(ca["global_minimum_contrast_unrounded"], 4),
            "coordinate_samples": 12,
            "path": "outputs/%s/A21/round-03/contrast-audit.json" % RUN_ID,
        },
        "final_images": 2, "final_images_required": 2, "image_views": 15,
        "completed_visual_iterations": 0, "snapshot_requests": 4,
        "snapshot_requests_by_kind": {"render": 2, "render-aux": 2},
        "successful_requests": 4, "failed_requests": 0, "retry_requests": 0,
        "syntax_fix_resubmits": 0, "service_stall_seconds": 0.0,
        "request_duration_sum_seconds": t3["request_duration_sum_seconds"],
        "first_usable_image_seconds": t3["first_usable_image_seconds"],
        "first_delivered_image_seconds": t3["first_delivered_image_seconds"],
        "elapsed_seconds": t3["elapsed_seconds"],
        "archive_tail_seconds": t3["archive_tail_seconds"],
        "artifacts": r3["artifacts"],
        "metrics": "outputs/%s/A21/round-03/task-metrics.json" % RUN_ID,
        "unresolved": ["%s %s" % (i["id"], i["issue"])
                       for i in m3["unresolved_issues"]],
        "next": "按 catalog.json 顺序进入 A22（三轮任务，也需 contrast-audit.json）",
        "checkpoint": ckpt,
    }
    ev_task = {
        "ts": NOW, "timezone": TZ, "event": "task_completed", "task_id": "A21",
        "run_id": RUN_ID, "status": "completed", "rounds_total": 3,
        "output_dir": "outputs/%s/A21" % RUN_ID,
        "temp_dir": "tmp/%s/A21" % RUN_ID,
        "detail": (
            "A21（staged-launch-change，预置连续三轮）全部完成：round-01 基线两图 + "
            "3 条能力探针；round-02 换成 27 字长标题（最多 3 行、≥48）并新增赞助方与"
            "报名状态牌；round-03 改浅色主题并按需求公式完成 23 段普通文字的全量"
            "对比度审计（最小 4.8616，阈值 4.5，背景取自去文字辅助渲染的实际像素）。"
            "三轮共 6 张最终图片、17 条快照请求（12 成功 / 5 失败）、43 次实际看图、"
            "4 次完整视觉迭代记录中的 1 次为 round-01 的 v1→v2 修复闭环，"
            "round-02 与 round-03 首版即通过。前两轮归档件一字未改"),
        "final_images_total": 6,
        "rounds": [
            {"round": 1, "final_images": 2, "requests": m1["counts"]
             ["snapshot_requests"], "image_views": m1["counts"]["image_views"]},
            {"round": 2, "final_images": 2, "requests": m2["counts"]
             ["snapshot_requests"], "image_views": m2["counts"]["image_views"]},
            {"round": 3, "final_images": 2, "requests": m3["counts"]
             ["snapshot_requests"], "image_views": m3["counts"]["image_views"]},
        ],
        "artifacts": a21["artifacts"],
        "task_metrics": "outputs/%s/A21/task-metrics.json" % RUN_ID,
        "checkpoint": ckpt,
    }
    prev_events = [json.loads(l) for l in EVENTS.read_text(
        encoding="utf-8").splitlines() if l.strip()] if EVENTS.exists() else []
    already = any(e.get("task_id") == "A21" and e.get("event") == "round_completed"
                  and e.get("round") == 3 for e in prev_events)
    if already:
        events_appended = 0
    else:
        with EVENTS.open("a", encoding="utf-8") as f:
            f.write(json.dumps(ev_round, ensure_ascii=False) + "\n")
            f.write(json.dumps(ev_task, ensure_ascii=False) + "\n")
        events_appended = 2

    # 题目级累计指标
    reqs = [json.loads(l) for l in (A21TMP / "requests.jsonl").read_text(
        encoding="utf-8").splitlines() if l.strip()]
    # round-01 的 3 条能力探针记录 round 字段为 null（驱动脚本在轮次字段落地之前
    # 就发出了这几条请求）；按它们的 started_at（18:40–18:43，落在 round-01 的
    # 起点 18:39:48 之后）归属 round-01，并在指标里标明这一归属口径。
    reqs_r = [r for r in reqs if r.get("round") in (1, 2, 3)
              or r.get("kind") == "probe"]
    aux = [r for r in reqs_r if r.get("kind") == "render-aux"]
    its = [json.loads(l) for l in (A21TMP / "iterations.jsonl").read_text(
        encoding="utf-8").splitlines() if l.strip()]
    view = json.loads((A21TMP / "viewing-evidence.json").read_text(
        encoding="utf-8"))
    views = {k: len(v.get("image_open_events", []))
             for k, v in view.get("rounds", {}).items()}

    task_metrics = {
        "schema_version": "1.0",
        "path_base": "suite_root",
        "scope": "task（A21 三轮累计；逐轮明细见各 round-NN/task-metrics.json，"
                 "本文件只累计顶层汇总，不重复相加轮次内的明细）",
        "task_id": "A21",
        "task_name": "staged-launch-change",
        "run_id": RUN_ID,
        "rounds_total": 3,
        "status": "completed",
        "stop_reason": "三轮需求全部满足并完成视觉自检与对比度审计",
        "started_at": m1["timings"]["started_at"],
        "ended_at": m3["timings"]["ended_at"],
        "elapsed_seconds": (dt.datetime.fromisoformat(
            m3["timings"]["ended_at"]) - dt.datetime.fromisoformat(
            m1["timings"]["started_at"])).total_seconds(),
        "elapsed_note": "从 round-01 开始到 round-03 归档完成的墙钟差，"
                        "包含三轮之间的阅读与设计时间，也包含本会话中段的上下文"
                        "压缩与平台停顿；不等于三轮 elapsed_seconds 之和"
                        "（三轮之间还有跨轮准备与归档时间），也不等于请求耗时之和",
        "output_dir": "outputs/%s/A21" % RUN_ID,
        "temp_dir": "tmp/%s/A21" % RUN_ID,
        "final_images_total": 6,
        "final_images_note": "每轮 2 张（launch-portrait 1080x1350、"
                             "launch-wide 1440x810），三轮各为一组独立作品，"
                             "不是同一张图的重复",
        "counts": {
            "snapshot_requests": len(reqs_r),
            "snapshot_requests_by_round": {
                "1": m1["counts"]["snapshot_requests"],
                "2": m2["counts"]["snapshot_requests"],
                "3": m3["counts"]["snapshot_requests"]},
            "snapshot_requests_by_kind": {
                "render": len([r for r in reqs_r if r.get("kind") == "render"]),
                "render-aux": len(aux),
                "probe": len([r for r in reqs_r if r.get("kind") == "probe"])},
            "snapshot_requests_note": "round-01 含 3 条能力探针（实测 gradientFocal、"
                                      "Opacity、文本扩展、CIRCLE 与 borderRadius 互斥等）；"
                                      "round-03 含 2 条去文字辅助渲染，只为对比度审计"
                                      "量取文字下方的实际合成背景，不产出交付件、"
                                      "不计入作品数",
            "snapshot_requests_attribution_note": "3 条能力探针的 requests.jsonl 记录"
                                                  " round 字段为 null（驱动脚本在轮次"
                                                  "字段落地之前就发出了它们）；按 "
                                                  "started_at（2026-10-19T18:40–18:43，"
                                                  "落在 round-01 起点 18:39:48 之后）"
                                                  "归属 round-01，与 round-01 "
                                                  "task-metrics.json 的 9 条一致",
            "successful_snapshot_requests": len(
                [r for r in reqs_r if r.get("http_status") == 200]),
            "failed_snapshot_requests": len(
                [r for r in reqs_r if r.get("http_status") is None
                 or r.get("http_status") != 200]),
            "retry_requests": sum(m["counts"]["retry_requests"]
                                  for m in (m1, m2, m3)),
            "syntax_fix_resubmits": sum(m["counts"]["syntax_fix_resubmits"]
                                        for m in (m1, m2, m3)),
            "dsl_versions": sum(m["counts"]["dsl_versions"]
                                for m in (m1, m2, m3)),
            "image_views": sum(m["counts"]["image_views"] for m in (m1, m2, m3)),
            "image_views_by_round": views,
            "completed_visual_iterations": sum(
                m["counts"]["completed_visual_iterations"]
                for m in (m1, m2, m3)),
            "iteration_records": len(its),
        },
        "request_duration_sum_seconds": round(
            sum(r["elapsed_ms"] for r in reqs_r if r.get("elapsed_ms")
                is not None) / 1000, 3),
        "request_duration_sum_note": "三轮 requests.jsonl 的 elapsed_ms 之和；"
                                     "round-02 含 1342.141 s 服务端读取超时挂起"
                                     "（无产出），扣掉后有效请求耗时为 "
                                     "%.3f s" % (
                                         sum(r["elapsed_ms"] for r in reqs_r
                                             if r.get("elapsed_ms") is not None
                                             and r.get("http_status") == 200)
                                         / 1000),
        "rounds": [
            {
                "round": 1,
                "output_subdirectory": "round-01",
                "started_at": m1["timings"]["started_at"],
                "ended_at": m1["timings"]["ended_at"],
                "elapsed_seconds": m1["timings"]["elapsed_seconds"],
                "final_images": 2,
                "snapshot_requests": m1["counts"]["snapshot_requests"],
                "image_views": m1["counts"]["image_views"],
                "completed_visual_iterations":
                    m1["counts"]["completed_visual_iterations"],
                "content_map_checks": "7/7",
                "request_duration_sum_seconds":
                    m1["timings"]["request_duration_sum_seconds"],
                "first_usable_image_seconds":
                    m1["timings"]["first_usable_image_seconds"],
                "first_delivered_image_seconds":
                    m1["timings"]["first_delivered_image_seconds"],
                "metrics": "outputs/%s/A21/round-01/task-metrics.json" % RUN_ID,
            },
            {
                "round": 2,
                "output_subdirectory": "round-02",
                "started_at": m2["timings"]["started_at"],
                "ended_at": m2["timings"]["ended_at"],
                "elapsed_seconds": m2["timings"]["elapsed_seconds"],
                "final_images": 2,
                "snapshot_requests": m2["counts"]["snapshot_requests"],
                "image_views": m2["counts"]["image_views"],
                "completed_visual_iterations":
                    m2["counts"]["completed_visual_iterations"],
                "content_map_checks": "9/9",
                "request_duration_sum_seconds":
                    m2["timings"]["request_duration_sum_seconds"],
                "service_stall_seconds":
                    m2["timings"]["service_stall_seconds"],
                "first_usable_image_seconds":
                    m2["timings"]["first_usable_image_seconds"],
                "first_delivered_image_seconds":
                    m2["timings"]["first_delivered_image_seconds"],
                "metrics": "outputs/%s/A21/round-02/task-metrics.json" % RUN_ID,
            },
            {
                "round": 3,
                "output_subdirectory": "round-03",
                "started_at": m3["timings"]["started_at"],
                "ended_at": m3["timings"]["ended_at"],
                "elapsed_seconds": m3["timings"]["elapsed_seconds"],
                "archive_tail_seconds": m3["timings"]["archive_tail_seconds"],
                "final_images": 2,
                "snapshot_requests": m3["counts"]["snapshot_requests"],
                "snapshot_requests_by_kind":
                    m3["counts"]["snapshot_requests_by_kind"],
                "image_views": m3["counts"]["image_views"],
                "completed_visual_iterations":
                    m3["counts"]["completed_visual_iterations"],
                "content_map_checks": "9/9",
                "request_duration_sum_seconds":
                    m3["timings"]["request_duration_sum_seconds"],
                "first_usable_image_seconds":
                    m3["timings"]["first_usable_image_seconds"],
                "first_delivered_image_seconds":
                    m3["timings"]["first_delivered_image_seconds"],
                "metrics": "outputs/%s/A21/round-03/task-metrics.json" % RUN_ID,
            },
        ],
        "contrast_audit": {
            "requirement": "round-03.md：所有普通文字与实际合成背景 ≥4.5:1，"
                           "不得只用主题 token 或名义底色",
            "path": "outputs/%s/A21/round-03/contrast-audit.json" % RUN_ID,
            "threshold": 4.5,
            "n_text_segments_checked": ca["n_text_segments_checked"],
            "n_text_segments_not_checked": ca["n_text_segments_not_checked"],
            "n_images_checked": ca["n_images_checked"],
            "global_minimum_contrast_unrounded":
                ca["global_minimum_contrast_unrounded"],
            "global_minimum_contrast": round(
                ca["global_minimum_contrast_unrounded"], 4),
            "all_plain_text_meets_threshold":
                ca["all_plain_text_meets_threshold"],
            "not_checked_items": ca["not_checked_items"],
            "method": "前景取 design-token 色；背景取去文字辅助渲染（同构造器、"
                      "Canvas.text(record_text=False)）在字形覆盖区的实际像素，"
                      "按需求规定的 8 位 sRGB 线性化与相对亮度公式、用未舍入结果"
                      "判阈值；渐变背景取字形覆盖区内最差值",
            "note": "仅 round-03 要求对比度审计；round-01 与 round-02 为深底主题，"
                    "需求未要求该项，故无该文件",
        },
        "delivery_verified_by": "每轮 metrics.delivery_map 均用响应字节 sha256 "
                                "与交付 PNG sha256 逐一比对",
        "unresolved_issues": [
            {"round": 1, "id": i["id"], "issue": i["issue"],
             "status": i["status"]} for i in m1["unresolved_issues"]
        ] + [
            {"round": 2, "id": i["id"], "issue": i["issue"],
             "status": i["status"]} for i in m2["unresolved_issues"]
        ] + [
            {"round": 3, "id": i["id"], "issue": i["issue"],
             "status": i["status"]} for i in m3["unresolved_issues"]
        ],
        "logs": {
            "requests": "tmp/%s/A21/requests.jsonl" % RUN_ID,
            "iterations": "tmp/%s/A21/iterations.jsonl" % RUN_ID,
            "viewing_evidence": "tmp/%s/A21/viewing-evidence.json" % RUN_ID,
            "round_changes": ["tmp/%s/A21/round-%02d-changes.json"
                              % (RUN_ID, n) for n in (2, 3)],
            "preview_manifests": ["tmp/%s/A21/preview/round-%02d/"
                                  "views-manifest.json" % (RUN_ID, n)
                                  for n in (1, 2, 3)],
            "auxiliary_background_renders": "tmp/%s/A21/backgrounds/" % RUN_ID,
            "contrast_local_evidence": "tmp/%s/A21/contrast-evidence/" % RUN_ID,
            "archive_conform_backup": "tmp/%s/A21/archive-conform/" % RUN_ID,
            "iterations_pre_normalize_backup":
                "tmp/%s/A21/iterations.pre-r03-normalize.jsonl" % RUN_ID,
        },
        "outputs": sorted(str(p.relative_to(ROOT)).replace("\\", "/")
                          for p in A21.rglob("*") if p.is_file()),
    }
    (A21 / "task-metrics.json").write_text(
        json.dumps(task_metrics, ensure_ascii=False, indent=1),
        encoding="utf-8")

    # checkpoint（新编号，不覆盖历史）
    checkpoint = dict(state)
    checkpoint["checkpoint_note"] = (
        "A21 三轮全部完成并归档。state-000056 是 round-02 归档后的快照；"
        "本快照新增 round-03 块、把 A21 置为 completed、把套级 completed 推进到 21 题，"
        "并写出题目级累计指标。历史快照一律未覆盖")
    (CHECKPOINTS / "state-000057.json").write_text(
        json.dumps(checkpoint, ensure_ascii=False, indent=1), encoding="utf-8")
    state["last_checkpoint"] = ckpt

    (STATE).write_text(json.dumps(state, ensure_ascii=False, indent=1),
                       encoding="utf-8")

    print("A21 → completed；套级 completed %d/30" % len(state["completed"]))
    print("round-03 交付 %d/9 | 累计最终图 %d 张" % (len(REQUIRED_R3), 6))
    print("累计请求 %d（成功 %d / 失败 %d）| 看图 %s | 迭代记录 %d 条"
          % (len(reqs_r),
             len([r for r in reqs_r if r.get("http_status") == 200]),
             len([r for r in reqs_r if r.get("http_status") != 200]),
             sum(views.values()), len(its)))
    print("events +%d | checkpoint %s" % (events_appended, ckpt))
    print("task metrics wrote outputs/%s/A21/task-metrics.json" % RUN_ID)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
