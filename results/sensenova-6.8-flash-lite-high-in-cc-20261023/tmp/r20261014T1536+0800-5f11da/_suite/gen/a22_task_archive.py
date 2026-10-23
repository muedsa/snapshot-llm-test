"""A22 题目层归档：追加 events.jsonl 一条事件、保存新编号检查点、刷新 suite-state.json 指针。

前置：a22_task_metrics.py 已生成 outputs/<run_id>/A22/task-metrics.json，
A22/snapshot-usage.md 已写好。本脚本只做留痕，不改任何已交付的数值或几何结论。

只更新 suite-state.json 这个「允许更新的当前指针」；checkpoints/state-*.json 是历史
快照，只新增编号、绝不覆盖。

用法
    python -I -X utf8 a22_task_archive.py
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

A = "A22"
NEXT = "A23"
A22_DIR = OUT_ROOT / A

R1_END = "2026-10-20T14:45:09+08:00"
R2 = "2026-10-20T15:06:53+08:00"
R2_END = "2026-10-20T16:57:03+08:00"
R3 = "2026-10-20T17:24:37+08:00"


def _parse(ts: str) -> dt.datetime:
    return dt.datetime.fromisoformat(ts)


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    metrics = json.loads((A22_DIR / "task-metrics.json").read_text(encoding="utf-8"))
    usage = A22_DIR / "snapshot-usage.md"
    for p in (A22_DIR / "task-metrics.json", usage):
        if not p.exists() or p.stat().st_size == 0:
            raise SystemExit("缺少题目层交付件：%s" % p)

    doc = json.loads(STATE.read_text(encoding="utf-8"))
    detail = [t for t in doc["tasks_detail"] if t["id"] == A]
    if not detail:
        raise SystemExit("suite-state.json 里没有 A22 条目")
    t = detail[0]
    # 题目层交付件：补上（若前一轮归档脚本已写入则去重）
    arts = list(t.get("artifacts", []))
    for rel in ("outputs/%s/A22/snapshot-usage.md" % RUN_ID, "outputs/%s/A22/task-metrics.json" % RUN_ID):
        if rel not in arts:
            arts.append(rel)
    t["artifacts"] = arts
    t["task_level_artifacts"] = {
        "snapshot_usage": "outputs/%s/A22/snapshot-usage.md" % RUN_ID,
        "snapshot_usage_bytes": usage.stat().st_size,
        "task_metrics": "outputs/%s/A22/task-metrics.json" % RUN_ID,
        "task_metrics_bytes": (A22_DIR / "task-metrics.json").stat().st_size,
        "written_at": NOW,
        "note": (
            "题目层累计报告与指标已生成。task-metrics.json 只累计各轮顶层汇总"
            "（requests 5 条 / http 7 个 / 看图 28 次 / 迭代 1 次 / 审计修复 4 次 / "
            "请求耗时 35.314 s / 累计墙钟 %.0f s），逐轮明细仍在 rounds 数组指向的各轮文件里；"
            "snapshot-usage.md 汇总三轮的数据演进、传播链、几何一致性、质量门与踩坑（D1–D18）"
            % metrics["timings"]["elapsed_seconds"]
        ),
    }
    t["ended_at"] = metrics["timings"]["ended_at"]
    t["elapsed_seconds"] = metrics["timings"]["elapsed_seconds"]

    doc["updated_at"] = NOW
    doc["updated_at_note"] = (
        "%s 归档 A22 题目层交付件（snapshot-usage.md + task-metrics.json）："
        "tasks_detail 的 A22 条目补上 task_level_artifacts 与两个文件路径，"
        "elapsed_seconds 对齐为 %.0f s（三轮墙钟之和）。"
        "同时在本轮追加两条记录类披露：D17（round-02 的 elapsed 60 s 内部不一致）、"
        "D18（round-03 的 elapsed_compared_to_previous_rounds 初版两处值错，已修正并留修正记录）。"
        "A22 三轮与各轮归档不改动。追加 1 条 events.jsonl 事件，保存新编号检查点" % (
            NOW, metrics["timings"]["elapsed_seconds"])
    )
    doc["suite_progress_note"] = (
        "A01–A22 共 22 题完成；A22 三轮与题目层累计交付全部就位："
        "每轮 dashboard.png + dashboard.snapshot + computed-data.json + layout-map.json + "
        "snapshot-usage.md + task-metrics.json，round-02/03 另附 change-audit.json，"
        "题目层另有三轮累计的 snapshot-usage.md 与 task-metrics.json。"
        "干跑门禁三轮各 28/28，像素审计三轮各 12/12；5 条请求记录 / 7 个 POST"
        "（4 成功 1 失败 3 内部重试 1 语法修复重交），28 次实际看图（另有 2 次 footer 裁切被接口拒收）、"
        "1 次完整视觉迭代、4 次审计脚本修复、3 张最终图片。"
        "A23、A24、B01–B06 共 8 题待执行")
    STATE.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    ev = {
        "ts": NOW, "timezone": "Asia/Shanghai (UTC+08:00)",
        "event": "task_level_archived", "task_id": A, "run_id": RUN_ID,
        "output_dir": "outputs/%s/A22" % RUN_ID,
        "artifacts": [
            "outputs/%s/A22/snapshot-usage.md" % RUN_ID,
            "outputs/%s/A22/task-metrics.json" % RUN_ID,
        ],
        "rounds_total": 3, "rounds_completed": 3,
        "requests": metrics["counts"]["snapshot_requests"],
        "http_requests": metrics["counts"]["http_requests"],
        "successful_requests": metrics["counts"]["successful_snapshot_requests"],
        "failed_requests": metrics["counts"]["failed_snapshot_requests"],
        "retry_requests": metrics["counts"]["retry_requests"],
        "syntax_fix_resubmits": metrics["counts"]["syntax_fix_resubmits"],
        "dsl_versions": metrics["counts"]["dsl_versions"],
        "image_views": metrics["counts"]["image_views"],
        "image_view_events_logged": metrics["counts"]["image_view_events_logged"],
        "image_views_rejected_by_api": metrics["counts"]["image_views_rejected_by_api"],
        "visual_iterations": metrics["counts"]["completed_visual_iterations"],
        "audit_fixes": metrics["counts"]["audit_fixes"],
        "audit_selftests_added": metrics["counts"]["audit_selftests_added"],
        "dryrun_gates": "%s/%s" % (metrics["counts"]["dryrun_gates_passed"],
                                    metrics["counts"]["dryrun_gates_total"]),
        "pixel_audit": "%s/%s" % (metrics["counts"]["pixel_audit_checks_passed"],
                                   metrics["counts"]["pixel_audit_checks_total"]),
        "final_images": metrics["counts"]["final_images"],
        "request_duration_sum_seconds": metrics["timings"]["request_duration_sum_seconds"],
        "wall_clock_seconds": metrics["timings"]["elapsed_seconds"],
        "span_start_to_end_seconds": metrics["timings"]["wall_clock_gaps"]["span_start_to_end_seconds"],
        "between_rounds_seconds": metrics["timings"]["wall_clock_gaps"]["total_between_rounds_seconds"],
        "detail": (
            "A22 题目层归档：snapshot-usage.md（三轮累计，13+11+13=37 项要求逐项对照、三轮数值演进表、"
            "两轮变更传播链、跨轮几何一致性、质量门、17 条方法类踩坑 + 18 条记录类披露 D1–D18）与 "
            "task-metrics.json（只累计各轮顶层汇总：5 条请求记录 / 7 个 POST / 28 次看图 / 1 次视觉迭代 / "
            "4 次审计修复 / 请求耗时 35.314 s / 累计墙钟 %.0f s）都已生成。"
            "归档时发现并披露两处时间记录问题：round-02 的 elapsed_seconds 6550 与它自己时间戳跨度 6610 "
            "差 60 s（原值保留，只做披露）；round-03 的 elapsed_compared_to_previous_rounds 初版把 round_01 "
            "写成 5023.0、round_03 写成 1883.0，已按各轮实际 ended_at 修正为 8466.0 / 2367.0 并在同字段 "
            "note 里保留修正前的值与依据。A22 到此全部完成，进入 A23"
            % metrics["timings"]["elapsed_seconds"]
        ),
        "task_status": t.get("status"),
        "next_task": NEXT,
    }
    with EVENTS.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(ev, ensure_ascii=False) + "\n")

    CKPT.mkdir(parents=True, exist_ok=True)
    existing = sorted(p.name for p in CKPT.glob("state-*.json"))
    n = len(existing) + 1
    cp_path = CKPT / ("state-%06d.json" % n)
    cp = {
        "checkpoint": n,
        "created_at": NOW,
        "timezone": "Asia/Shanghai (UTC+08:00)",
        "reason": "A22 题目层累计报告与指标归档完成，A22 全部交付，进入 A23",
        "suite_state_snapshot": dict(doc),
        "event_count": len(EVENTS.read_text(encoding="utf-8").splitlines()),
        "restore": {
            "how": (
                "suite-state.json 允许更新，恢复时以最新 checkpoint 的 suite_state_snapshot 为准；"
                "A22 已 completed、rounds_done=3，三轮产物与题目层累计文件均已就位且不覆盖，"
                "下一题 A23 按 catalog.json 的 task_order 继续"
            ),
            "resume_from": "tasks/A23-*（按 catalog.json 的 task_order）",
            "done_in_this_checkpoint": [
                "A22 round-01 / round-02 / round-03 各 7 个文件（共 21 个）",
                "A22 题目层 snapshot-usage.md 与 task-metrics.json",
                "A22 共 23 个交付文件",
            ],
            "scripts": [
                "tmp/%s/_suite/gen/a22_data.py" % RUN_ID,
                "tmp/%s/_suite/gen/a22_build.py" % RUN_ID,
                "tmp/%s/_suite/gen/a22_log.py" % RUN_ID,
                "tmp/%s/_suite/gen/a22_view_footer.py" % RUN_ID,
                "tmp/%s/_suite/gen/a22_selftest_label_gate.py" % RUN_ID,
                "tmp/%s/_suite/gen/a22_state_r01.py" % RUN_ID,
                "tmp/%s/_suite/gen/a22_state_r02.py" % RUN_ID,
                "tmp/%s/_suite/gen/a22_state_r03.py" % RUN_ID,
                "tmp/%s/_suite/gen/a22_task_metrics.py" % RUN_ID,
                "tmp/%s/_suite/gen/a22_task_archive.py" % RUN_ID,
            ],
            "pending": [
                "继续 A23、A24、B01–B06（共 8 题）",
                "B01–B06 各至少 10 件独立完整作品",
                "全部 30 题完成后生成套级 index.md / gallery.md / snapshot-usage.md / task-metrics.json 并做总审查",
                "套级 suite-state.json 的 required_artifacts_delivered 目前为 1/5，其余 4 件由总审查补齐",
            ],
        },
    }
    cp_path.write_text(json.dumps(cp, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    doc["last_checkpoint"] = "tmp/%s/_suite/checkpoints/%s" % (RUN_ID, cp_path.name)
    STATE.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    print("suite-state 已补 A22 题目层交付件，updated_at=%s" % NOW)
    print("events.jsonl 追加 1 条，当前 %d 条"
          % len(EVENTS.read_text(encoding="utf-8").splitlines()))
    print("检查点 %s" % cp_path.name)
    print("last_checkpoint -> %s" % doc["last_checkpoint"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
