"""A13 收口状态：suite-state.json 追加 A13、events.jsonl 追加 task_completed、打检查点。

用法：SNAPSHOT_RUN_ID=<rid> python -I tmp/<rid>/_suite/gen/a13_state.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(HERE.parent))
import suite as S  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

TASK = "A13"
RID = S.run_id()
OUT, TMP = S.task_dirs(TASK)
SDIR, TSDIR = S.suite_dirs()

state = S.load_state()
metrics = json.loads((OUT / "task-metrics.json").read_text(encoding="utf-8"))
brand = json.loads((OUT / "brand-system.json").read_text(encoding="utf-8"))
audit = json.loads((TMP / "gen" / "a13_audit.json").read_text(encoding="utf-8"))

artifacts = sorted(p.name for p in OUT.iterdir() if p.is_file())
summary = metrics["requirement_checks"]["summary"]
black = brand["black_check"]

entry = {
    "id": TASK, "status": "completed",
    "started_at": metrics["timings"]["started_at"],
    "ended_at": S.now_iso(),
    "elapsed_seconds": metrics["timings"]["elapsed_seconds"],
    "output_dir": S.rel(OUT), "temp_dir": S.rel(TMP),
    "artifacts": [S.rel(OUT / n) for n in artifacts],
    "metrics": S.rel(OUT / "task-metrics.json"),
    "requests": metrics["counts"]["snapshot_requests"],
    "successful_requests": metrics["counts"]["successful_snapshot_requests"],
    "failed_requests": metrics["counts"]["failed_snapshot_requests"],
    "retry_requests": metrics["counts"]["retry_requests"],
    "image_views": metrics["counts"]["image_views"],
    "visual_iterations": metrics["counts"]["iterations_total"],
    "issues_found": len(metrics.get("issues", [])),
    "requirement_checks": summary,
    "artefact_geometry": {
        "chosen_direction": brand.get("chosen_direction"),
        "components": brand["component_count"]["total"],
        "component_limit": brand["component_count"]["limit"],
        "grid_unit_px": brand["geometry"]["grid_unit_px"],
        "live_area_px": brand["geometry"]["live_area_px"],
        "clear_space_px": brand["clear_space"]["value_px_at_512"],
    },
    "black_check": {
        "compliant": black["compliant"],
        "n_alpha_gt0": black["n_alpha_gt0"],
        "n_alpha_gt0_rgb_nonzero": black["n_alpha_gt0_rgb_nonzero"],
        "semi_transparent_edge_pixels": black.get("semi_transparent_edge_pixels"),
    },
    "small_size_review": {
        "targets": [t["icon"] for t in brand["small_size_review"]["targets"]],
        "resample_filter": brand["small_size_review"]["resample"]
                           ["resample_filter"],
        "pillow_version": brand["small_size_review"]["resample"]
                          ["pillow_version"],
        "preview_paths": [t["preview_32"]["path"]
                          for t in brand["small_size_review"]["targets"]],
    },
    "verification": {
        "script": "tmp/" + RID + "/_suite/gen/a13_audit.py",
        "report": S.rel(TMP / "gen" / "a13_audit.json"),
        "checks": len(audit["checks"]),
        "passed": sum(1 for c in audit["checks"] if c["passed"]),
        "failed": sum(1 for c in audit["checks"] if not c["passed"]),
    },
    # 逐图实际查看的记录（Read 工具打开最终/中间 PNG 并据视觉反馈修改）
    "visual_review_evidence": [
        {"image": "tmp/%s/A13/preview/probe-geo-onlight.png" % RID,
         "purpose": "量测确认 border 向内绘制、孔径=宽−2×描边、胶囊两端半圆",
         "outcome": "确立几何契约，用于全部四张图的尺寸规划"},
        {"image": "tmp/%s/A13/preview/preview-a.png" % RID,
         "purpose": "方向 A 512 预览与方向 B 对比选择",
         "outcome": "选定 A"},
        {"image": "tmp/%s/A13/preview/preview-b.png" % RID,
         "purpose": "方向 B 512 预览与方向 A 对比选择",
         "outcome": "排除 B（32 px 下坍缩为靶心、净空 −1.02 px）"},
        {"image": "tmp/%s/A13/preview/a13-direction-32-sheet.png" % RID,
         "purpose": "两方向 32×32 同尺量测对比",
         "outcome": "确认 A 空隙 2 px / 59.86%，B 空隙 1 px / 64.84%"},
        {"image": "outputs/%s/A13/brand-banner.png" % RID,
         "purpose": "逐图自检品牌横幅",
         "outcome": "分割线实测延伸到 x=1099、右缘零墨迹，判定右侧留白正常，不改"},
        {"image": "outputs/%s/A13/launch-poster.png（首版）" % RID,
         "purpose": "逐图自检发布海报",
         "outcome": "发现底部三条阶调色带贴住画布左边缘、底部留白 38 px，"
                    "像被裁断的残片"},
        {"image": "outputs/%s/A13/launch-poster.png" % RID,
         "purpose": "修复后复看发布海报",
         "outcome": "三条色带已移除，底部留白恢复为 96 px，与顶部 84 px 对称"},
        {"image": "tmp/%s/A13/preview/symbol-color-onlight.png" % RID,
         "purpose": "浅底合成查看彩色图标",
         "outcome": "环孔真透明，三层等差递减清晰可辨"},
        {"image": "tmp/%s/A13/preview/symbol-black-onlight.png" % RID,
         "purpose": "浅底合成查看纯黑图标",
         "outcome": "三层仅靠有无覆盖即可分开，环孔为真透明"},
        {"image": "outputs/%s/A13/symbol-color.png（原始 RGBA）" % RID,
         "purpose": "验证 alpha 通道真实存在、验证深底存活",
         "outcome": "确认透明；浅阶深底上对比不足，已记为已知限制"},
        {"image": "outputs/%s/A13/symbol-black.png（原始 RGBA）" % RID,
         "purpose": "验证纯黑版 alpha 通道与边缘",
         "outcome": "透明与半透明边缘均为纯黑"},
        {"image": "tmp/%s/A13/preview/a13-32-review-sheet.png" % RID,
         "purpose": "两张交付图按实际 32 像素原尺寸复核",
         "outcome": "轮廓与关键负空间可辨，最窄空隙 2 px"},
    ],
    "visual_check_list": [
        {"check": c["id"], "desc": c["desc"],
         "report": S.rel(TMP / "gen" / "a13_audit.json"),
         "verdict": "PASS" if c["passed"] else "FAIL"}
        for c in audit["checks"]],
    "unresolved_issues": metrics.get("unresolved_issues", []),
    "recorded_at": S.now_iso()}

A_CHOSEN = "A"
state["tasks_detail"] = [t for t in state.get("tasks_detail", [])
                         if t.get("id") != TASK] + [entry]
state["completed"] = state.get("completed") or []
if TASK not in state["completed"]:
    state["completed"].append(TASK)
comp = set(state["completed"])
state["remaining"] = [t for t in state.get("remaining", []) if t not in comp]
state["current_task"] = sorted(state["remaining"])[0] if state["remaining"] \
    else None
state["counts_by_status"] = {"completed": len(comp), "in_progress": 0,
                             "pending": len(state["remaining"])}
assert len(comp) + len(state["remaining"]) == int(state["total_tasks"]), (
    len(comp), len(state["remaining"]))
state["updated_at"] = S.now_iso()
state["status"] = "completed" if not state["remaining"] else "in_progress"
S.save_state(state)

ev_before = sum(1 for l in (TSDIR / "events.jsonl").read_text(
    encoding="utf-8", errors="replace").splitlines() if l.strip())
S.append_event({
    "ts": S.now_iso(), "event": "task_completed", "task_id": TASK,
    "status": "completed", "requirement_checks": summary,
    "requests": metrics["counts"]["snapshot_requests"],
    "image_views": metrics["counts"]["image_views"],
    "visual_iterations": metrics["counts"]["iterations_total"],
    "components": brand["component_count"]["total"],
    "black_check_violations": black["n_alpha_gt0_rgb_nonzero"],
    "verification_failed": sum(1 for c in audit["checks"]
                               if not c["passed"]),
    "next_task": state["current_task"],
    "output_dir": S.rel(OUT)})
ck = S.snapshot_checkpoint(state)
state["last_checkpoint"] = ck
S.save_state(state)

print("artifacts:", artifacts)
print("checks evidence: %d 条" % len(entry["visual_review_evidence"]))
print("counts_by_status:",
      json.dumps(state["counts_by_status"], ensure_ascii=False))
print("current_task:", state["current_task"], " status:", state["status"])
print("events:", ev_before, "->", ev_before + 1)
print("checkpoint:", ck)
