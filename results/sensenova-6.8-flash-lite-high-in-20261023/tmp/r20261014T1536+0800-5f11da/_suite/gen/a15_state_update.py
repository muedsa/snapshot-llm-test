"""A15 完成后更新套件状态：suite-state.json + events.jsonl + 检查点。

只做追加与指针更新，不覆盖历史快照。运行方式：
    python -I tmp/<run_id>/_suite/gen/a15_state_update.py
"""
from __future__ import annotations

import json
import pathlib

# 路径由本文件位置派生：…/suite_root/tmp/<run_id>/_suite/gen/本文件
HERE = pathlib.Path(__file__).resolve()
RUN_ID = HERE.parents[2].name
SUITE_ROOT = HERE.parents[4]
OUT = SUITE_ROOT / "outputs" / RUN_ID
TMP = SUITE_ROOT / "tmp" / RUN_ID
STATE = OUT / "_suite" / "suite-state.json"
EVENTS = TMP / "_suite" / "events.jsonl"
CKPT_DIR = TMP / "_suite" / "checkpoints"
TS = "2026-10-19T04:35:13+08:00"

A15 = OUT / "A15"
A15_TMP = TMP / "A15"

A15_DETAIL = {
    "id": "A15",
    "status": "completed",
    "started_at": "2026-10-18T21:37:13+08:00",
    "ended_at": TS,
    "elapsed_seconds": 25080,
    "output_dir": str(A15.relative_to(SUITE_ROOT)),
    "temp_dir": str(A15_TMP.relative_to(SUITE_ROOT)),
    "artifacts": [
        "outputs/r20261014T1536+0800-5f11da/A15/reconstructed.png",
        "outputs/r20261014T1536+0800-5f11da/A15/reconstructed.snapshot",
        "outputs/r20261014T1536+0800-5f11da/A15/reconstruction-audit.json",
        "outputs/r20261014T1536+0800-5f11da/A15/comparison.md",
        "outputs/r20261014T1536+0800-5f11da/A15/snapshot-usage.md",
        "outputs/r20261014T1536+0800-5f11da/A15/task-metrics.json",
    ],
    "review_gallery": "outputs/r20261014T1536+0800-5f11da/A15/review/",
    "metrics": "outputs/r20261014T1536+0800-5f11da/A15/task-metrics.json",
    "requests": 17,
    "successful_requests": 9,
    "failed_requests": 8,
    "retry_requests": 7,
    "final_render_versions": 7,
    "image_views": 11,
    "visual_iterations": 6,
    "requirement_checks": {"total": 17, "passed": 17, "failed": 0},
    "verification": {
        "script": "tmp/r20261014T1536+0800-5f11da/_suite/gen/a15_audit.py",
        "report": "outputs/r20261014T1536+0800-5f11da/A15/reconstruction-audit.json",
        "checks": 19,
        "passed": 19,
        "failed": 0,
    },
    "anchors": {
        "checked": 19,
        "pass": 19,
        "tolerance_px_per_component": 8,
        "max_component_error_px": 4,
        "zero_error_anchors": 13,
    },
    "glyph_boxes": {
        "count": 36,
        "max_component_delta_px": 3,
        "ink_width_exact": 27,
        "ink_height_exact": 34,
    },
    "color_roles": {
        "sampled": 47,
        "exact_on_both_sides": 45,
        "tokens_grouped": 22,
        "with_residual_delta": 2,
    },
    "visual_reviews": 11,
    "final_images": 1,
    "final_render_request_id": "req-a15-reconstructed-032fdf",
    "byte_identical_to_service": True,
    "per_card_viewed": True,
    "defects_found_by_viewing": 3,
    "unresolved_issues": [
        "u1 字重与字体来源无法从参考位图唯一判定；探针 a15_diag11.py 已写好但本轮未运行，"
        "不宣称判定出参考字重",
        "u2 两处小字号文字色采样残余（y 轴刻度 (6,5,4)、月份标签 (1,1,1)），"
        "归因核心像素混入抗锯齿；并排看色相明暗一致，题面未设色差阈值",
        "u3 未做逐像素差异图；题面不要求，且预期以字体度量噪声为主",
    ],
    "recorded_at": TS,
}

A15_EVENT = {
    "ts": TS,
    "event": "task_completed",
    "task_id": "A15",
    "status": "completed",
    "requirement_checks": {"total": 17, "passed": 17, "failed": 0},
    "requests": 17,
    "successful_requests": 9,
    "failed_requests": 8,
    "retry_requests": 7,
    "final_render_versions": 7,
    "image_views": 11,
    "visual_iterations": 6,
    "anchors": "19/19",
    "anchor_tolerance_px_per_component": 8,
    "anchor_max_component_error_px": 4,
    "glyph_boxes": 36,
    "glyph_max_component_delta_px": 3,
    "color_roles": "45/47 exact",
    "verification_failed": 0,
    "defects_found_and_fixed": 3,
    "final_images": 1,
    "next_task": "A16",
    "output_dir": "outputs/r20261014T1536+0800-5f11da/A15",
}


def main() -> int:
    state = json.loads(STATE.read_text(encoding="utf-8"))

    ids = [t["id"] for t in state["tasks_detail"]]
    if "A15" in ids:
        print("A15 已在 tasks_detail 中，跳过追加（不覆盖既有记录）")
    else:
        state["tasks_detail"].append(A15_DETAIL)

    if "A15" not in state["completed"]:
        state["completed"].append("A15")
    if "A15" in state["remaining"]:
        state["remaining"] = [t for t in state["remaining"] if t != "A15"]

    counts: dict[str, int] = {"completed": 0, "in_progress": 0, "pending": 0,
                              "partial": 0, "blocked": 0}
    for tid in [t["id"] for t in state["tasks_detail"]]:
        entry = next(e for e in state["tasks_detail"] if e["id"] == tid)
        counts[entry["status"]] = counts.get(entry["status"], 0) + 1
    for tid in state["remaining"]:
        counts["pending"] = counts.get("pending", 0) + 1
    state["counts_by_status"] = {k: v for k, v in counts.items() if v}
    state["current_task"] = "A16"
    state["status"] = "in_progress"
    state["completed_all"] = len(state["remaining"]) == 0 and \
        len(state["completed"]) == state["total_tasks"]
    state["required_artifacts_delivered"] = 1
    state["updated_at"] = TS

    # 检查点：只新建编号文件，不覆盖任何已有快照
    existing = sorted(CKPT_DIR.glob("state-*.json"))
    next_no = (len(existing) + 1) if not existing else \
        int(existing[-1].stem.split("-")[-1]) + 1
    ckpt_path = CKPT_DIR / f"state-{next_no:06d}.json"
    if ckpt_path.exists():
        raise SystemExit(f"拒绝覆盖已有检查点：{ckpt_path}")
    state["last_checkpoint"] = str(ckpt_path.relative_to(SUITE_ROOT))
    ckpt_path.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    STATE.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    EVENTS.open("a", encoding="utf-8").write(
        json.dumps(A15_EVENT, ensure_ascii=False) + "\n"
    )

    print("suite-state.json 已更新：",
          state["counts_by_status"], "current_task =", state["current_task"])
    print("检查点：", state["last_checkpoint"])
    print("events.jsonl 已追加 A15 task_completed")


if __name__ == "__main__":
    raise SystemExit(main())
