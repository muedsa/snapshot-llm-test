"""A17 完成后：更新 suite-state.json、追加 events.jsonl、写 state-000051.json 检查点。"""
from __future__ import annotations

import datetime
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
RUN_ID = HERE.parents[2].name
SUITE_ROOT = HERE.parents[4]
SUITE_OUT = SUITE_ROOT / "outputs" / RUN_ID / "_suite"
SUITE_TMP = SUITE_ROOT / "tmp" / RUN_ID / "_suite"
TZ = "Asia/Shanghai (UTC+08:00)"

A17 = SUITE_ROOT / "outputs" / RUN_ID / "A17"
A17_TMP = SUITE_ROOT / "tmp" / RUN_ID / "A17"

NAMES = ["handbook-01", "handbook-02", "handbook-03", "handbook-04",
         "example-01", "example-02", "example-03", "example-04"]


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
    m = json.loads((A17 / "task-metrics.json").read_text(encoding="utf-8"))
    t = m["timings"]

    state = json.loads((SUITE_OUT / "suite-state.json").read_text(encoding="utf-8"))
    detail = {
        "id": "A17",
        "status": "completed",
        "started_at": t["started_at"],
        "ended_at": now,
        "elapsed_seconds": int((datetime.datetime.now()
                                - datetime.datetime.fromisoformat(
                                    t["started_at"].replace("+08:00", ""))).total_seconds()),
        "output_dir": "outputs/%s/A17" % RUN_ID,
        "temp_dir": "tmp/%s/A17" % RUN_ID,
        "artifacts": ["outputs/%s/A17/%s.%s" % (RUN_ID, n, ext)
                      for n in NAMES
                      for ext in ("png", "snapshot")]
                     + ["outputs/%s/A17/%s" % (RUN_ID, f)
                        for f in ("sources.md", "examples.json", "snapshot-usage.md",
                                  "task-metrics.json", "promotion-manifest.json")],
        "final_pngs": 8,
        "final_pngs_required": 8,
        "final_png_sizes": {"handbook-01..04": [1200, 1600], "example-01..04": [400, 240]},
        "snapshot_requests": m["counts"]["snapshot_requests"],
        "snapshot_requests_successful": m["counts"]["successful_snapshot_requests"],
        "snapshot_requests_failed": m["counts"]["failed_snapshot_requests"],
        "probe_requests": m["counts"]["probe_requests"],
        "retry_requests": m["counts"]["retry_requests"],
        "dsl_versions": m["counts"]["dsl_versions"],
        "image_views": m["counts"]["image_views"],
        "completed_visual_iterations": m["counts"]["completed_visual_iterations"],
        "syntax_fix_iterations": m["counts"]["syntax_fix_iterations"],
        "baseline_iterations": m["counts"]["baseline_iterations"],
        "requirements_checked": m["counts"]["requirements_checked"],
        "logs": {
            "requests": "tmp/%s/A17/requests.jsonl" % RUN_ID,
            "iterations": "tmp/%s/A17/iterations.jsonl" % RUN_ID,
            "audit_trace": "tmp/%s/A17/audit-trace.json" % RUN_ID,
            "build_manifest": "tmp/%s/A17/build-manifest.json" % RUN_ID,
        },
        "evidence": [
            "tmp/%s/A17/audit-trace.json" % RUN_ID,
            "tmp/%s/A17/iterations.jsonl" % RUN_ID,
            "tmp/%s/_suite/gen/a17_check.py" % RUN_ID,
            "tmp/%s/_suite/gen/a17_core.py" % RUN_ID,
            "tmp/%s/_suite/gen/a17_page.py" % RUN_ID,
            "tmp/%s/_suite/gen/a17_build.py" % RUN_ID,
            "tmp/%s/_suite/gen/a17_promote.py" % RUN_ID,
            "tmp/%s/_suite/gen/a17_report.py" % RUN_ID,
            "tmp/%s/_suite/gen/a17_docs.py" % RUN_ID,
            "tmp/%s/_suite/gen/a17_iterations.py" % RUN_ID,
            "tmp/%s/_suite/gen/a17_zoom.py" % RUN_ID,
            "tmp/%s/A17/preview/hb4-illus.png" % RUN_ID,
            "tmp/%s/A17/preview/hb4-glass.png" % RUN_ID,
            "tmp/%s/A17/preview/ex4-glass.png" % RUN_ID,
            "tmp/%s/A17/preview/hb3-illus.png" % RUN_ID,
        ],
        "evidence_note": "audit-trace.json 为 8 件交付与真实 200 响应的字节级配对审计；"
                         "a17_check.py 是发请求前的静态断言（印刷行数、行宽、单孩子契约、"
                         "属性值禁 <、印刷片段逐字同源）；preview/ 为 2×/3× 放大自检图",
        "visual_defect_found_and_fixed": {
            "page": 4,
            "defect": "毛玻璃面板 136×92@(118,10) 未覆盖两个源色块与整行标签，"
                      "像素采样显示左缘外 x=128 为未模糊原色 (56,189,248)、"
                      "标签行 x=120 为未模糊文字 (60,73,93)",
            "fix": "面板改为 left=104 top=6 width=196 height=96（仅 2 行属性值），"
                   "内部 Container 同步 196×96",
            "verification": "重渲后 x=120 为模糊值 (227,246,254)、标签行 y=110 最暗 "
                            "(244,246,246)；3× 放大确认无未模糊的源色块边缘；"
                            "印刷行数仍为 17（8–18 内）",
            "requests": ["req-a17-handbook-04-5f859e", "req-a17-example-04-0f4e38"],
        },
        "constraints_discovered": [
            "Container 与 Positioned 只允许一个子元素，否则 400 PARSE_ERROR",
            "解析器不做 HTML 实体解码，属性值与元素内容禁写字面 < 与 &（正文走 Raw+CDATA）",
            "根 Stack 不能直接做 Snapshot 的子节点：无限约束 + fit=EXPAND 触发 "
            "RENDER_ERROR Layout size is infinite，必须外包显式尺寸 Container",
            "Column 的直接 Row 子节点不渲染且会中断其后的兄弟，需先包显式尺寸 Container",
            "滤镜内的 Container 只有 height 没有 width 时子树滤镜撑满整块画布",
            "BackdropFilter 只模糊已绘制在其背后的内容，纯色背景看不出效果",
        ],
        "constraints_note": "以上为本题请求逼出的服务实测契约，非文档结论；"
                            "手册第 4 页把它们写成「先用一次渲染确认」",
        "unresolved": [u["id"] + " " + u["item"] for u in m["unresolved_issues"]],
    }
    state["tasks_detail"] = [d for d in state["tasks_detail"] if d["id"] != "A17"]
    state["tasks_detail"].append(detail)

    state["completed"] = sorted(set(state["completed"]) | {"A17"})
    state["remaining"] = [x for x in state["remaining"] if x != "A17"]
    state["counts_by_status"] = {
        "completed": len(state["completed"]),
        "in_progress": 0,
        "pending": len(state["remaining"]),
    }
    state["current_task"] = "A18"
    state["updated_at"] = now
    state["status"] = "in_progress"
    state["completed_all"] = len(state["completed"]) == state["total_tasks"]
    # required_suite_artifacts 是否齐备：5 件总交付里目前只有本文件，其余在总审查时生成
    present = [a for a in state["required_suite_artifacts"]
               if (SUITE_OUT / a).exists()]
    state["required_artifacts_delivered"] = len(present)
    state["required_artifacts_delivered_note"] = "齐备 %d/%d（%s）；" \
        "index.md、gallery.md、snapshot-usage.md、task-metrics.json 在全部 30 题完成后" \
        "由总审查生成" % (len(present), len(state["required_suite_artifacts"]),
                          "、".join(present))
    state["suite_progress_note"] = (
        "A01–A17 共 17 题完成（A17 为 4 页手册 + 4 个 400×240 独立示例，"
        "8 件全部为真实服务 200 响应）；按 task_order 下一题为 A18")
    ckpt = SUITE_TMP / "checkpoints"
    ckpt.mkdir(parents=True, exist_ok=True)
    existing = [int(p.name.split("-")[-1].split(".")[0])
                for p in ckpt.glob("state-*.json")]
    ckpt_path = ckpt / ("state-%06d.json" % (max(existing or [0]) + 1))
    state["last_checkpoint"] = str(ckpt_path.relative_to(SUITE_ROOT))
    ckpt_path.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")
    (SUITE_OUT / "suite-state.json").write_text(
        json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")

    ev = {
        "ts": now, "timezone": TZ, "event": "task_completed", "task_id": "A17",
        "run_id": RUN_ID, "status": "completed",
        "detail": "A17 四页可实践的 DSL 入门手册：4 页 1200×1600 + 4 个 400×240 独立示例，"
                  "教学插图与独立示例逐字复用同一核心子树；15 条技术结论各指向实际文档页与示例；"
                  "三轮语法修复（Container/Positioned 单孩子、字面 < 与 CDATA、根 Stack 无限约束）"
                  "各由 4 组探针定位；一轮视觉修复（第 4 页毛玻璃面板未覆盖源色块，"
                  "像素采样取证后加宽面板）；20/20 条要求通过",
        "requirement_checks": {"total": 20, "passed": 20, "failed": 0},
        "requests": m["counts"]["snapshot_requests"] + m["counts"]["probe_requests"],
        "successful_requests": 29,
        "failed_requests": 17,
        "failed_breakdown": {"http_400": 13, "timeout_or_disconnect": 4},
        "retry_requests": m["counts"]["retry_requests"],
        "document_requests": m["counts"]["document_requests"],
        "final_images": 8,
        "image_views": m["counts"]["image_views"],
        "visual_iterations": m["counts"]["completed_visual_iterations"],
        "syntax_fix_iterations": m["counts"]["syntax_fix_iterations"],
        "baseline_iterations": m["counts"]["baseline_iterations"],
        "defects_found_and_fixed": 1,
        "request_duration_sum_seconds": t["request_duration_sum_seconds"],
        "elapsed_seconds": t["elapsed_seconds"],
        "first_usable_image_seconds": t["first_usable_image_seconds"],
        "first_deliverable_image_seconds": t["first_deliverable_image_seconds"],
        "next_task": "A18",
        "output_dir": "outputs/%s/A17" % RUN_ID,
        "temp_dir": "tmp/%s/A17" % RUN_ID,
        "unresolved": [u["id"] for u in m["unresolved_issues"]],
        "checkpoint": state["last_checkpoint"],
    }
    with (SUITE_TMP / "events.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(ev, ensure_ascii=False) + "\n")

    print(json.dumps({
        "state_updated": str((SUITE_OUT / "suite-state.json").relative_to(SUITE_ROOT)),
        "checkpoint": state["last_checkpoint"],
        "counts_by_status": state["counts_by_status"],
        "current_task": state["current_task"],
        "remaining": len(state["remaining"]),
        "tasks_detail_len": len(state["tasks_detail"]),
    }, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
