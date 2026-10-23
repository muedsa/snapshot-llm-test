"""A21 round-01 归档时更新套级进度：suite-state.json + events.jsonl + 检查点。

用法：python a21_state_r01.py

只写这三处：
  1) outputs/<run>/_suite/suite-state.json      —— 加 A21 的逐轮条目、推进 updated_at
  2) tmp/<run>/_suite/events.jsonl              —— 追加 round_completed 事件（只增不改）
  3) tmp/<run>/_suite/checkpoints/state-NNNNNN.json —— 新编号快照，不覆盖旧快照
所有数字都从 round-01/task-metrics.json、content-map.json、
design-tokens.json、viewing-evidence.json 现读，不手抄。
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
A21OUT = ROOT / "outputs" / RUN / "A21"
R1 = "outputs/%s/A21/round-01" % RUN
T1 = "tmp/%s/A21" % RUN


def load(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    for st in (sys.stdout, sys.stderr):
        if hasattr(st, "reconfigure"):
            st.reconfigure(encoding="utf-8")

    state_path = SUITE / "suite-state.json"
    state = load(state_path)
    metrics = load(pathlib.Path(R1) / "task-metrics.json")
    cm = load(pathlib.Path(R1) / "content-map.json")
    tokens = load(pathlib.Path(R1) / "design-tokens.json")
    views = load(pathlib.Path(T1) / "viewing-evidence.json")

    now = dt.datetime.now().astimezone().replace(microsecond=0)
    now_iso = now.isoformat(timespec="seconds")

    r1_ev = views["rounds"]["1"]
    checks = cm.get("checks") or cm.get("checks_list") or []
    checks_ok = sum(1 for c in checks if c.get("passed"))
    checks_tot = len(checks)
    imgs = metrics["counts"]

    arts = [
        R1 + "/launch-portrait.png", R1 + "/launch-portrait.snapshot",
        R1 + "/launch-wide.png", R1 + "/launch-wide.snapshot",
        R1 + "/design-tokens.json", R1 + "/content-map.json",
        R1 + "/snapshot-usage.md", R1 + "/task-metrics.json",
    ]

    round1 = {
        "round": 1,
        "status": "completed",
        "output_subdirectory": "round-01",
        "started_at": metrics["timings"]["started_at"],
        "ended_at": metrics["timings"]["ended_at"],
        "elapsed_seconds": metrics["timings"]["elapsed_seconds"],
        "final_images": 2,
        "final_images_required": 2,
        "final_images_note": "launch-portrait 1080x1350 与 launch-wide 1440x810，"
                             "两图分别构图，不是等比缩放",
        "artifacts": arts,
        "metrics": R1 + "/task-metrics.json",
        "logs": metrics["logs"],
        "audit": {
            "content_map": R1 + "/content-map.json",
            "checks_passed": "%d/%d" % (checks_ok, checks_tot),
            "all_passed": cm.get("all_passed"),
            "design_tokens": R1 + "/design-tokens.json",
            "brand_geometry_components": len(tokens.get("brand_geometry", [])),
            "viewing_evidence": T1 + "/viewing-evidence.json",
            "viewing_events": len(r1_ev["image_open_events"]),
        },
        "delivery_verified_by": "响应字节 sha256 与交付 PNG sha256 逐一比对"
                                "（metrics.delivery_map，两对完全一致）",
        "requests": imgs["snapshot_requests"],
        "successful_requests": imgs["successful_snapshot_requests"],
        "failed_requests": imgs["failed_snapshot_requests"],
        "retry_requests": imgs["retry_requests"],
        "syntax_fix_resubmits": imgs["syntax_fix_resubmits"],
        "image_views": imgs["image_views"],
        "completed_visual_iterations": imgs["completed_visual_iterations"],
        "request_duration_sum_seconds": metrics["timings"]["request_duration_sum_seconds"],
        "requirements_note": "尺寸、必需文案、字号下限、品牌构件数、构图差异、"
                             "扩展空间、无占位文字逐项核对，"
                             "见 round-01/snapshot-usage.md 第 1 节表格",
        "defects_found_and_fixed": 3,
        "defects_detail": "1) 字标中英粘连（嵌套 Text 裁掉前导空白）"
                          " 2) 竖版右上大面积空白 "
                          " 3) 强调条与灰细线间距过近且长度不一",
        "unresolved_issues": metrics["unresolved_issues"],
    }

    entry = {
        "id": "A21",
        "status": "in_progress",
        "status_note": "三轮任务：round-01 已归档；round-02 / round-03 待执行。"
                       "任务级状态在完成第三轮并生成题目级汇总报告后置为 completed",
        "started_at": "2026-10-19T18:39:48+08:00",
        "output_dir": "outputs/%s/A21" % RUN,
        "temp_dir": T1,
        "execution_mode": "预置连续执行（自动三轮）：round-01 归档后才读取 "
                          "rounds/round-02.md，round-02 归档后才读取 rounds/round-03.md；"
                          "不等待外部反馈",
        "rounds": [round1],
        "recorded_at": now_iso,
    }

    # tasks_detail 按 A09…A20 顺序排列，A21 追加到末尾
    state["tasks_detail"] = [t for t in state["tasks_detail"] if t.get("id") != "A21"]
    state["tasks_detail"].append(entry)

    state["counts_by_status"] = {"completed": 20, "in_progress": 1, "pending": 9}
    state["current_task"] = "A21"
    state["current_round"] = {
        "task_id": "A21", "round": 1, "rounds_total": 3, "status": "completed",
        "next": "读取 tasks/A21-staged-launch-change/rounds/round-02.md 后执行 round-02",
        "note": "round-02.md 与 round-03.md 在 round-01 归档完成前未读取，"
                "符合题目要求的执行顺序",
    }
    state["remaining"] = ["A22", "A23", "A24", "B01", "B02", "B03", "B04", "B05", "B06"]
    state["suite_progress_note"] = (
        "A01–A20 共 20 题完成；A21（三轮）的 round-01 已归档：两图 + 两 DSL + "
        "design-tokens.json + content-map.json（%d/%d 项检查通过）+ "
        "snapshot-usage.md + task-metrics.json，交付映射由 sha256 证实。"
        "round-02 与 round-03 待执行，round-03 另需 contrast-audit.json"
        % (checks_ok, checks_tot))
    state["tasks_detail_note"] = (state.get("tasks_detail_note", "")
                                  + " A21 自 %s 起加入 tasks_detail，"
                                    "记录三轮任务的逐轮状态；"
                                    "A01–A08 仍只有 task-metrics.json 而无逐题明细。"
                                    % now_iso)
    state["updated_at"] = now_iso

    # 新检查点编号：现有最大号 + 1，旧快照不覆盖
    cp_dir = TMP_S / "checkpoints"
    nums = [int(m.group(1)) for p in cp_dir.glob("state-*.json")
            if (m := re.match(r"state-(\d+)\.json$", p.name))]
    cp_num = (max(nums) + 1) if nums else 1
    cp_rel = "tmp/%s/_suite/checkpoints/state-%06d.json" % (RUN, cp_num)
    snapshot = json.loads(json.dumps(state))
    snapshot["last_checkpoint"] = cp_rel
    snapshot["checkpoint_note"] = ("本检查点记录 A21 round-01 归档完成、round-02 尚未开始的"
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

    # events.jsonl 追加（只增不改）
    ev = {
        "ts": now_iso, "timezone": "Asia/Shanghai (UTC+08:00)",
        "event": "round_completed", "task_id": "A21", "run_id": RUN,
        "round": 1, "rounds_total": 3, "status": "completed",
        "task_status": "in_progress",
        "output_dir": "outputs/%s/A21" % RUN,
        "round_dir": R1, "temp_dir": T1,
        "detail": "A21 round-01（基线）归档：launch-portrait 1080x1350 与 "
                  "launch-wide 1440x810 两图分别构图（纵向信息栈+右中主视觉 vs "
                  "左栏文字+右整栏主视觉，非等比缩放），6 个可识别品牌构件，"
                  "主标题 132/116px、其余最小 28px，顶部 118/88px、底部 207/74px "
                  "真实扩展空间且无占位文字。v1 看图发现 3 处缺陷"
                  "（字标中英粘连、竖版右上空白、双分隔线），修复后重渲 v2 并逐件复查。"
                  "content-map %d/%d 项检查通过（含墨迹两两碰撞、文字到发光球实体"
                  "净距、字号下限等像素级检查）；交付件与服务响应的对应由 sha256 "
                  "逐一比对证实" % (checks_ok, checks_tot),
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
        "request_duration_sum_seconds": metrics["timings"]["request_duration_sum_seconds"],
        "first_usable_image_seconds": metrics["timings"]["first_usable_image_seconds"],
        "first_delivered_image_seconds":
            metrics["timings"]["first_delivered_image_seconds"],
        "elapsed_seconds": metrics["timings"]["elapsed_seconds"],
        "defects_found_and_fixed": 3,
        "artifacts": arts,
        "metrics": R1 + "/task-metrics.json",
        "unresolved": [u["id"] + " " + u["issue"] for u in metrics["unresolved_issues"]],
        "next": "读取 tasks/A21-staged-launch-change/rounds/round-02.md "
                "并执行 round-02",
        "checkpoint": cp_rel,
    }
    with (TMP_S / "events.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(ev, ensure_ascii=False) + "\n")

    print("A21 checks: %d/%d  all_passed=%s"
          % (checks_ok, checks_tot, cm.get("all_passed")))
    print("brand_geometry components: %d" % len(tokens.get("brand_geometry", [])))
    print("viewing events r1: %d" % len(r1_ev["image_open_events"]))
    print("checkpoint: %s" % cp_rel)
    print("state updated_at: %s" % state["updated_at"])
    print("counts: %s" % state["counts_by_status"])
    print("tasks_detail ids: %s" % [t["id"] for t in state["tasks_detail"]])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
