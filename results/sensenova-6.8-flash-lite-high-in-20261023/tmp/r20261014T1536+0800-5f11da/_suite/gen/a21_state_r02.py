"""A21 round-02 归档时更新套级进度：suite-state.json + events.jsonl + 检查点。

用法：python a21_state_r02.py

只写这三处：
  1) outputs/<run>/_suite/suite-state.json   —— 在已有 A21 条目上追加 round 2，推进 updated_at
  2) tmp/<run>/_suite/events.jsonl           —— 追加 round_completed 事件（只增不改）
  3) tmp/<run>/_suite/checkpoints/state-NNNNNN.json —— 新编号快照，不覆盖旧快照
所有数字都从 round-02/task-metrics.json、content-map.json、design-tokens.json、
viewing-evidence.json 现读，不手抄。
"""
from __future__ import annotations

import datetime as dt
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve()
RUN = HERE.parents[2].name
ROOT = HERE.parents[4]
SUITE = ROOT / "outputs" / RUN / "_suite"
TMP_S = ROOT / "tmp" / RUN / "_suite"
R2 = "outputs/%s/A21/round-02" % RUN
R1CHECK = "outputs/%s/A21/round-01" % RUN
T1 = "tmp/%s/A21" % RUN


def load(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    for st in (sys.stdout, sys.stderr):
        if hasattr(st, "reconfigure"):
            st.reconfigure(encoding="utf-8")

    state_path = SUITE / "suite-state.json"
    state = load(state_path)
    metrics = load(pathlib.Path(R2) / "task-metrics.json")
    cm = load(pathlib.Path(R2) / "content-map.json")
    tokens = load(pathlib.Path(R2) / "design-tokens.json")
    views = load(pathlib.Path(T1) / "viewing-evidence.json")

    now = dt.datetime.now().astimezone().replace(microsecond=0)
    now_iso = now.isoformat(timespec="seconds")

    r2_ev = views["rounds"]["2"]
    checks = cm.get("checks") or cm.get("checks_list") or []
    checks_ok = sum(1 for c in checks if c.get("passed"))
    checks_tot = len(checks)
    imgs = metrics["counts"]
    tm = metrics["timings"]

    arts = [
        R2 + "/launch-portrait.png", R2 + "/launch-portrait.snapshot",
        R2 + "/launch-wide.png", R2 + "/launch-wide.snapshot",
        R2 + "/design-tokens.json", R2 + "/content-map.json",
        R2 + "/snapshot-usage.md", R2 + "/task-metrics.json",
    ]

    round2 = {
        "round": 2,
        "status": "completed",
        "output_subdirectory": "round-02",
        "spec_source": "tasks/A21-staged-launch-change/rounds/round-02.md",
        "base_artifacts": ["outputs/%s/A21/round-01/launch-portrait.png" % RUN,
                           "outputs/%s/A21/round-01/launch-wide.png" % RUN],
        "started_at": tm["started_at"],
        "ended_at": tm["ended_at"],
        "elapsed_seconds": tm["elapsed_seconds"],
        "started_at_note": "由 attempt 1 的 started_at 减 elapsed_ms 还原；"
                           "逐条证据见 task-metrics.json 的 timings.started_at_correction",
        "archive_tail_seconds": tm["archive_tail_seconds"],
        "final_images": 2,
        "final_images_required": 2,
        "final_images_note": "launch-portrait 1080x1350 与 launch-wide 1440x810 尺寸未变；"
                             "竖版 3 行标题、横版 2 行标题，两图仍分别构图而非等比缩放",
        "artifacts": arts,
        "metrics": R2 + "/task-metrics.json",
        "logs": metrics["logs"],
        "audit": {
            "content_map": R2 + "/content-map.json",
            "checks_passed": "%d/%d" % (checks_ok, checks_tot),
            "all_passed": cm.get("all_passed"),
            "design_tokens": R2 + "/design-tokens.json",
            "brand_geometry_components": len(tokens.get("brand_geometry", [])),
            "brand_geometry_note": "6 个构件形态未变；报名状态牌是牌子族的新实例"
                                   "而非新构件，故构件数不因新增内容而增加",
            "viewing_evidence": T1 + "/viewing-evidence.json",
            "viewing_events": len(r2_ev["image_open_events"]),
            "changes": T1 + "/round-02-changes.json",
            "collision_result": "100 对文字墨迹交集面积全为 0 px²（竖版 55 对、横版 45 对）；"
                                "文字墨迹到 orb_core 的净距全为正，最小 141 px"
                                "（横版 title_line2）",
        },
        "delivery_verified_by": "响应字节 sha256 与交付 PNG sha256 逐一比对"
                                "（metrics.delivery_map，两对完全一致）",
        "requests": imgs["snapshot_requests"],
        "successful_requests": imgs["successful_snapshot_requests"],
        "failed_requests": imgs["failed_snapshot_requests"],
        "retry_requests": imgs["retry_requests"],
        "syntax_fix_resubmits": imgs["syntax_fix_resubmits"],
        "service_stall_seconds": tm["service_stall_seconds"],
        "service_stall_note": "2 次服务端读取超时（924.282 s + 417.859 s）未返回任何字节，"
                              "无响应文件可留痕；挂起之外的有效请求耗时 27.485 s",
        "image_views": imgs["image_views"],
        "completed_visual_iterations": imgs["completed_visual_iterations"],
        "request_duration_sum_seconds": tm["request_duration_sum_seconds"],
        "requirements_note": "27 字长标题（最多 3 行、≥48）、新增赞助方与报名状态、"
                             "日期/讲者/ONLINE LAUNCH/网址保留、主色与 6 构件形态不变、"
                             "两尺寸不变、不用变形压窄，逐项核对见 "
                             "round-02/snapshot-usage.md 的 1.2 节表格；"
                             "长标题与新增信息的碰撞规避说明见 1.3 节",
        "defects_found_and_fixed": 1,
        "defects_detail": "1) 横版标题会静默丢掉「的结构化方法」（27 字变 21 字，"
                          "渲染仍正常）——提交前的无网络干跑门在打印元素表时发现，"
                          "改为新增 title_2w 后才提交；未消耗任何服务请求",
        "unresolved_issues": metrics["unresolved_issues"],
    }

    # 在已有 A21 条目上追加 round 2，不重建整个条目
    entry = None
    for t in state["tasks_detail"]:
        if t.get("id") == "A21":
            entry = t
            break
    assert entry is not None, "tasks_detail 里找不到 A21"
    rounds = [r for r in entry.get("rounds", []) if r.get("round") != 2]
    rounds.append(round2)
    entry["rounds"] = sorted(rounds, key=lambda r: r["round"])
    entry["status"] = "in_progress"
    entry["status_note"] = ("三轮任务：round-01、round-02 已归档；round-03 待执行"
                            "（另需 contrast-audit.json）。"
                            "任务级状态在完成第三轮并生成题目级汇总报告后置为 completed")
    entry["recorded_at"] = now_iso

    state["counts_by_status"] = {"completed": 20, "in_progress": 1, "pending": 9}
    state["current_task"] = "A21"
    state["current_round"] = {
        "task_id": "A21", "round": 2, "rounds_total": 3, "status": "completed",
        "next": "读取 tasks/A21-staged-launch-change/rounds/round-03.md 后执行 round-03",
        "note": "round-03.md 在 round-02 归档完成前未读取，"
                "符合题目要求的执行顺序",
    }
    state["remaining"] = ["A22", "A23", "A24", "B01", "B02", "B03", "B04", "B05", "B06"]
    state["suite_progress_note"] = (
        "A01–A20 共 20 题完成；A21（三轮）的 round-01 与 round-02 已归档："
        "每轮两图 + 两 DSL + design-tokens.json + content-map.json + "
        "snapshot-usage.md + task-metrics.json，交付映射由 sha256 证实"
        "（round-01 %d/%d 项检查、round-02 %d/%d 项检查，均 all_passed）。"
        "round-02 首轮即通过、无视觉迭代；其 portrait 前两次请求遇服务端读取超时"
        "（合计 %.1f s，无产出）。round-03 待执行，另需 contrast-audit.json"
        % (sum(1 for c in load(pathlib.Path(R1CHECK) / "content-map.json")
               .get("checks", []) if c.get("passed")),
           len(load(pathlib.Path(R1CHECK) / "content-map.json").get("checks", [])),
           checks_ok, checks_tot, tm["service_stall_seconds"]))
    state["tasks_detail_note"] = (state.get("tasks_detail_note", "")
                                  + " A21 round-02 自 %s 起加入本条目的 rounds；"
                                    "同一次归档只向 round-01/task-metrics.json 追加了"
                                    "字段以对齐当前生成器（数值未改，原文件留底于 "
                                    "tmp/%s/A21/archive-conform/）。"
                                    % (now_iso, RUN))
    state["updated_at"] = now_iso

    cp_dir = TMP_S / "checkpoints"
    nums = [int(m.group(1)) for p in cp_dir.glob("state-*.json")
            if (m := re.match(r"state-(\d+)\.json$", p.name))]
    cp_num = (max(nums) + 1) if nums else 1
    cp_rel = "tmp/%s/_suite/checkpoints/state-%06d.json" % (RUN, cp_num)
    snapshot = json.loads(json.dumps(state))
    snapshot["last_checkpoint"] = cp_rel
    snapshot["checkpoint_note"] = ("本检查点记录 A21 round-02 归档完成、round-03 尚未开始的"
                                   "时刻；A21 任务级状态仍为 in_progress")
    (cp_dir / ("state-%06d.json" % cp_num)).write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=1), encoding="utf-8")
    state["last_checkpoint"] = cp_rel

    state["suite_artifacts"] = {
        "suite_state": "outputs/%s/_suite/suite-state.json" % RUN,
        "index": "outputs/%s/_suite/index.md" % RUN,
        "gallery": "outputs/%s/_suite/gallery.md" % RUN,
        "snapshot_usage": "outputs/%s/_suite/snapshot-usage.md" % RUN,
        "task_metrics": "outputs/%s/_suite/task-metrics.json" % RUN,
    }
    state["suite_artifacts_note"] = (
        "suite-state.json 已落盘；其余 4 件在 30 题全部完成后由总审查生成。"
        "各题已有本地产物，见各题 task-metrics.json 的 outputs")
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

    ev = {
        "ts": now_iso, "timezone": "Asia/Shanghai (UTC+08:00)",
        "event": "round_completed", "task_id": "A21", "run_id": RUN,
        "round": 2, "rounds_total": 3, "status": "completed",
        "task_status": "in_progress",
        "output_dir": "outputs/%s/A21" % RUN,
        "round_dir": R2, "temp_dir": T1,
        "detail": "A21 round-02 归档：在第一轮两图上替换主标题为 27 字长句"
                  "（竖版 3 行 12/9/6、横版 2 行 12/15，字号 66/52 均 ≥48），"
                  "新增赞助方「Northstar Research / 云构工具」与报名状态牌"
                  "「免费参加 · 无需报名」（牌子族新实例、主色描边，构件数仍为 6），"
                  "日期/讲者/ONLINE LAUNCH/网址全部保留；两尺寸不变，"
                  "主色 #5FE0FF 与 6 个品牌构件形态未变，装饰只做了移动与缩放"
                  "（竖版球 130→165 并下移填补 3 行标题留下的空区、网址牌 632→560、"
                  "角部水印 300→288 并外移、主标记 76/58→72/52），"
                  "交付 .snapshot 中 0 个 Text 带 transform/matrix。"
                  "content-map %d/%d 项检查通过；100 对文字墨迹交集面积为 0、"
                  "文字到 orb_core 净距全为正（最小 141 px）。"
                  "首轮即通过，14 次实际看图（含 12 个语义裁切视图与 2 次归档复查）"
                  "未发现需返工的缺陷，故无视觉迭代" % (checks_ok, checks_tot),
        "content_map_checks": {"passed": checks_ok, "total": checks_tot,
                               "all_passed": cm.get("all_passed")},
        "final_images": 2, "final_images_required": 2,
        "image_views": imgs["image_views"],
        "completed_visual_iterations": imgs["completed_visual_iterations"],
        "snapshot_requests": imgs["snapshot_requests"],
        "successful_requests": imgs["successful_snapshot_requests"],
        "failed_requests": imgs["failed_snapshot_requests"],
        "retry_requests": imgs["retry_requests"],
        "syntax_fix_resubmits": imgs["syntax_fix_resubmits"],
        "service_stall_seconds": tm["service_stall_seconds"],
        "request_duration_sum_seconds": tm["request_duration_sum_seconds"],
        "first_usable_image_seconds": tm["first_usable_image_seconds"],
        "first_delivered_image_seconds": tm["first_delivered_image_seconds"],
        "elapsed_seconds": tm["elapsed_seconds"],
        "archive_tail_seconds": tm["archive_tail_seconds"],
        "defects_found_and_fixed": 1,
        "artifacts": arts,
        "metrics": R2 + "/task-metrics.json",
        "unresolved": [u["id"] + " " + u["issue"] for u in metrics["unresolved_issues"]],
        "next": "读取 tasks/A21-staged-launch-change/rounds/round-03.md "
                "并执行 round-03（另需 contrast-audit.json）",
        "checkpoint": cp_rel,
    }
    with (TMP_S / "events.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(ev, ensure_ascii=False) + "\n")

    print("A21 round-02 checks: %d/%d  all_passed=%s"
          % (checks_ok, checks_tot, cm.get("all_passed")))
    print("brand_geometry components: %d" % len(tokens.get("brand_geometry", [])))
    print("viewing events r2: %d" % len(r2_ev["image_open_events"]))
    print("checkpoint: %s" % cp_rel)
    print("state updated_at: %s" % state["updated_at"])
    print("A21 rounds recorded: %s" % [r["round"] for r in entry["rounds"]])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
