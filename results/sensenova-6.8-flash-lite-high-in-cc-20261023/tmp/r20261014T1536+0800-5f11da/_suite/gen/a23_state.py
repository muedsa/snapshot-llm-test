"""A23 题目层归档：追加 events.jsonl 一条事件、保存新编号检查点、刷新 suite-state.json 指针。

前置：outputs/<run_id>/A23/ 下 8 张交付 PNG + 8 份 .snapshot + delivery-manifest.json +
frame-data.json + timing.json + limitations.md + pixel-audit.json + snapshot-usage.md +
task-metrics.json 都已就位。本脚本只做留痕，不改任何已交付的数值、几何或图像。

只更新 suite-state.json 这个「允许更新的当前指针」；checkpoints/state-*.json 是历史
快照，只新增编号、绝不覆盖。

用法
    python -I -X utf8 a23_state.py
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

A = "A23"
NEXT = "A24"
A_DIR = OUT_ROOT / A

DELIVERABLES = [
    "cover.png", "cover.snapshot",
    "frame-1.png", "frame-1.snapshot",
    "frame-2.png", "frame-2.snapshot",
    "frame-3.png", "frame-3.snapshot",
    "frame-4.png", "frame-4.snapshot",
    "frame-5.png", "frame-5.snapshot",
    "frame-6.png", "frame-6.snapshot",
    "contact-sheet.png", "contact-sheet.snapshot",
    "delivery-manifest.json",
    "frame-data.json", "timing.json",
    "limitations.md", "pixel-audit.json",
    "snapshot-usage.md", "task-metrics.json",
]
SCRIPTS = [
    "tmp/%s/_suite/gen/a23_units.py",
    "tmp/%s/_suite/gen/a23_probe.py",
    "tmp/%s/_suite/gen/a23_render.py",
    "tmp/%s/_suite/gen/a23_finalize.py",
    "tmp/%s/_suite/gen/a23_debug_unexplained.py",
    "tmp/%s/_suite/gen/a23_audit.py",
    "tmp/%s/_suite/gen/a23_deliver.py",
    "tmp/%s/_suite/gen/a23_metrics.py",
    "tmp/%s/_suite/gen/a23_state.py",
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
    audit = json.loads((A_DIR / "pixel-audit.json").read_text(encoding="utf-8"))
    tm = m["timings"]
    c = m["counts"]

    doc = json.loads(STATE.read_text(encoding="utf-8"))
    entry = {
        "id": A,
        "status": "completed",
        "status_note": (
            "TASK.md 逐项核对全部满足：1200×800 RGB PNG 封面（标题「从结构到画面」"
            "WCAG AA 4.5:1 实测通过）+ 6 张 600×600 透明 PNG 关键帧（无文字、12 个"
            "几何单元守恒、由分散逐步汇聚、末帧为可识别房景）+ frame-data.json + "
            "timing.json + limitations.md。8 件交付 PNG 的 sha256 全部等于服务原始响应"
            "字节，8 份 DSL 与当前构造器重建结果逐字节一致。能力边界 4 项判定"
            "（可编辑 SVG / CMYK / GIF / PNG 封面）全部带缓存文档行号依据；循环接缝"
            "如实记为硬跳变并声明 seamless=false"
        ),
        "execution_mode": "单轮：本题不是预置多轮题，预置连续执行模式不适用",
        "started_at": tm["started_at"],
        "started_at_note": tm["started_at_note"],
        "output_dir": "outputs/%s/%s" % (RUN_ID, A),
        "temp_dir": "tmp/%s/%s" % (RUN_ID, A),
        "ended_at": tm["ended_at"],
        "ended_at_note": tm["ended_at_note"],
        "elapsed_seconds": tm["elapsed_seconds"],
        "elapsed_note": tm["elapsed_note"],
        "final_images": c["final_images"],
        "final_images_required": c["final_images_required"],
        "final_images_note": (
            "1 张 1200×800 封面 + 6 张 600×600 透明关键帧 + 1 张 6 帧接触表。"
            "PNG 头实测尺寸与 color_type（封面 6=RGBA 全不透明，帧 6=RGBA 带真实"
            "alpha=0）；全部是服务返回的原始字节，未后处理"
        ),
        "artifacts": ["outputs/%s/%s/%s" % (RUN_ID, A, n) for n in DELIVERABLES],
        "metrics": "outputs/%s/%s/task-metrics.json" % (RUN_ID, A),
        "logs": {
            "requests": "tmp/%s/%s/requests.jsonl" % (RUN_ID, A),
            "iterations": "tmp/%s/%s/iterations.jsonl" % (RUN_ID, A),
            "viewing_evidence": "tmp/%s/%s/viewing-evidence.json" % (RUN_ID, A),
            "probe_report": "tmp/%s/%s/probe-layout.json" % (RUN_ID, A),
            "delivery_manifest": "tmp/%s/%s/delivery-manifest.json" % (RUN_ID, A),
            "dsl_versions": "tmp/%s/%s/dsl/" % (RUN_ID, A),
            "responses": "tmp/%s/%s/responses/" % (RUN_ID, A),
        },
        "quality_gates": {
            "dryrun": "%d/%d" % (c["dryrun_gates_passed"], c["dryrun_gates_total"]),
            "dryrun_note": "a23_units.dry_run，覆盖画布越界、单元重叠、遮挡上限、"
                           "HARD_EDGE 静默裁切、ID 唯一性、12 单元的几何/颜色/alpha "
                           "守恒；每次提交前重跑，失败即拒绝提交",
            "pixel_audit": "%d/%d" % (c["pixel_audit_checks_passed"],
                                      c["pixel_audit_checks_total"]),
            "pixel_audit_report": "outputs/%s/%s/pixel-audit.json" % (RUN_ID, A),
            "pixel_audit_note": (
                "6 帧 × 11 项 + 封面 4 项 + 交付字节恒等 1 项 + 审计活性证明 1 项。"
                "顶层 passed=true、failures=[]"
            ),
            "activation_tests": "6/6",
            "activation_tests_note": (
                "activation_tests：6 个已知坏样本反测门禁（少画一个单元、换成不透明白底、"
                "换一个单元颜色、把 U12 移出画布、硬裁左侧一条、负对照），all_triggered=true"
            ),
            "audit_runs": "%d（通过 %d / 失败 %d）" % (c["pixel_audit_runs"],
                                                      c["pixel_audit_runs_passed"],
                                                      c["pixel_audit_runs_failed"]),
            "visual_review": "5 次实际打开（cover、contact-sheet、frame-1/3/6 整图 1:1）"
                             "+ 3 张经接触表读到",
            "contrast_mean": 13.14,
            "contrast_worst_ink_px": 13.02,
            "contrast_note": "封面标题墨迹按 WCAG 相对亮度公式线性化后加权，"
                             "取最暗墨迹像素（保守口径），WCAG AA 4.5:1 通过",
            "alpha_note": "6 帧 fully_transparent_fraction 0.8083–0.8152，"
                          "distinct_alpha_levels 223–255，证明透明背景是真实 alpha=0 "
                          "而不是白底假透明",
            "conservation_note": "12 单元 × 6 帧 = 72 个实例的形状、未旋转宽高、RGB、"
                                 "alpha 全部一致（G04/G05 逐帧比对）；只允许位置与旋转变化",
        },
        "delivery_verified_by": (
            "pixel-audit.json 的 delivery_byte_identity：8/8 件交付 PNG 的 sha256 等于 "
            "tmp/%s/%s/responses/<request_id>.png 的服务原始响应字节；delivery-manifest.json "
            "的 all_bytes_unchanged=true、all_snapshots_match_source=true" % (RUN_ID, A)
        ),
        "requests": c["http_requests"],
        "http_requests": c["http_requests"],
        "successful_requests": c["successful_requests"],
        "failed_requests": c["failed_requests"],
        "retry_requests": c["retry_requests"],
        "syntax_fix_resubmits": c["syntax_fix_resubmits"],
        "dsl_versions": c["dsl_versions"],
        "submission_groups": c["submission_groups"],
        "submission_groups_ok": c["submission_groups_ok"],
        "submission_groups_never_ok": c["submission_groups_never_ok"],
        "image_views": c["image_views"],
        "image_views_via_contact_sheet": c["image_views_via_contact_sheet"],
        "events_logged": c["events_logged"],
        "completed_visual_iterations": c["completed_visual_iterations"],
        "audit_fixes": c["audit_fixes"],
        "audit_report_fixes": c["audit_report_fixes"],
        "audit_selftests_added": c["audit_selftests_added"],
        "request_duration_sum_seconds": tm["request_duration_sum_seconds"],
        "transport_read_timeout_seconds": tm["transport_read_timeout_seconds"],
        "counting_note": (
            "requests = http_requests = 43：本题每次 render() 都把每次尝试各记一条"
            "（带 -a2/-a3 后缀的 request_id），所以记录条数就是实际 POST /snapshot 次数，"
            "不像 A22 需要区分两个口径。43 = 38 次渲染 + 5 个最小探针。"
            "失败 32 = 29 次服务端 400（全部是 RENDER_ERROR Layout size is infinite）"
            "+ 3 次传输层读超时（read timeout after 180s，http_status=0、started_at=null）。"
            "提交组 24 按「label 段相同且 attempt 连续递增」归组：成功 11、始终失败 13"
            "（首轮 8 件各 3 次尝试 + 5 个探针），重试 19 次。"
            "image_views=5 只算实际打开的；image_views_via_contact_sheet=3 是透过接触表"
            "读到的，单列不并入。"
            "request_duration_sum_seconds（84.609 s）只统计 http_status 为 200 或 400 的"
            "本地 elapsed_ms，与 transport_read_timeout_seconds（550.358 s，本地 180 s"
            "读超时上限）不同口径、不可相加，两者也都不是 elapsed_seconds"
        ),
        "task_level_artifacts": {
            "snapshot_usage": "outputs/%s/%s/snapshot-usage.md" % (RUN_ID, A),
            "snapshot_usage_bytes": usage_path.stat().st_size,
            "task_metrics": "outputs/%s/%s/task-metrics.json" % (RUN_ID, A),
            "task_metrics_bytes": metrics_path.stat().st_size,
            "written_at": NOW,
            "note": (
                "题目层累计报告与指标已生成。task-metrics.json 的 path_base=suite_root，"
                "7 个阶段墙钟互不重叠、之和小于 elapsed_seconds；"
                "snapshot-usage.md 汇总 22 项要求逐项核对、8 件交付证据、能力边界 4 项"
                "判定、43 次请求时间线、11 处修改记录、关键设计选择（一次全局同伦、"
                "smoothstep 缓动、旋转以自身中心、ClipPath 做三角形）与 8 条可复用经验"
            ),
        },
        "unresolved_issues": [
            {
                "id": "%s-u1" % A.lower(),
                "issue": "客户原始请求中的「文字可编辑 SVG」与「CMYK 印刷稿」本服务原生不支持",
                "why": ("<Snapshot type=> 只接受 png/jpg/webp（tagref 第 219–224 行），"
                        "/snapshot 的 200 响应 content 只有 image/png|jpeg|webp；"
                        "缓存全部文档检索 CMYK/ICC/色彩空间零命中；颜色语法只有 "
                        "#RGB/#RGBA/#RRGGBB/#RRGGBBAA，没有色域或 ICC 描述符字段"),
                "impact": "不能直接交付这两种格式",
                "mitigation": (
                    "limitations.md 第 1、2 节给出替代与外部后续工作：交付的是等价的 "
                    "class-DOM DSL + 12 单元参数，足够作为 DSL→SVG 转换器的输入；"
                    "sRGB→CMYK 需外部印刷前处理并指定 ICC 与印刷条件。"
                    "特别注意 openapi.yaml 第 83–92 行的 enum: [png] 属于 errorImage "
                    "查询参数、不是输出格式枚举，已在 limitations.md 标注以防误读"
                ),
                "status": "disclosed",
            },
            {
                "id": "%s-u2" % A.lower(),
                "issue": "循环接缝是一次真实跳变，不是无缝循环",
                "why": (
                    "接缝位移 39.6344–136.0625 px、旋转 0°–120°，12 个单元全部背离"
                    "场景中心 C=(40,330) 跳回，与正向汇聚方向完全相反；接缝用 250 ms "
                    "走完 100% 位移而正向最快单帧只走完 Δe_max=0.296，速度比 3.3784 倍"
                    "（12 单元完全相同）。题目要求「t=0 分散、t=1250 汇聚」而无缝要求"
                    "「t=1500 ≡ t=0」，6 帧 + 250 ms/帧 下不能同时成立"
                ),
                "impact": "每次循环到帧 6→帧 1 时画面整体向外炸开，再重新汇聚",
                "mitigation": (
                    "timing.json.seamless=false、frame-data.json.seam.closure=false 已明确"
                    "声明，不因为 loop=true 就宣称无缝；跳变的位置、幅度、方向（点积逐 ID "
                    "验证）、速度与影响逐 ID 记录在 seam.units 与 timing.json.seam_evidence；"
                    "limitations.md 第 5 节给出 4 条可修复方案，其中「改 12 帧 / 3000 ms」"
                    "数据模型改动最小"
                ),
                "status": "disclosed",
            },
            {
                "id": "%s-u3" % A.lower(),
                "issue": "6 帧 PNG 的 223–255 个不同 alpha 级在合成 GIF 时会丢失部分梯度",
                "why": "GIF 调色板最多 256 色，而本服务不支持 GIF 输出（type 只接受 png/jpg/webp）",
                "impact": "外部合成后的透明度不如 PNG 细腻",
                "mitigation": (
                    "属外部合成步骤引入的损失，已在 limitations.md 第 3 节声明；"
                    "6 张 PNG 关键帧 + timing.json 是本交付的权威版本"
                ),
                "status": "disclosed",
            },
            {
                "id": "%s-u4" % A.lower(),
                "issue": "3 条请求的 http_status=0、started_at=null、elapsed_ms 为本地超时上限",
                "why": "read timeout after 180s，无服务端响应、无 Retry-After",
                "impact": "这 3 次请求的服务端耗时不可知",
                "mitigation": (
                    "无需恢复：原因写在日志的 error 字段；耗时单列 "
                    "transport_read_timeout_seconds（550.358 s），不并入 "
                    "request_duration_sum_seconds，也不等于 elapsed_seconds"
                ),
                "status": "disclosed",
            },
            {
                "id": "%s-u5" % A.lower(),
                "issue": "首条请求之前的阅读与设计工作没有独立时间戳；本轮未记 task_started 事件",
                "why": "读 TASK.md / task.json / audit-fields.json、检索文档判定能力边界、"
                       "编写 12 单元定义、构造器与 20 项干跑门禁的时间没有独立时间戳",
                "impact": "elapsed_seconds 是下界而非准确值",
                "mitigation": "无需恢复：已在 started_at_note 与 elapsed_note 中说明",
                "status": "disclosed",
            },
        ],
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
        "%s 归档 A23：题目层 24 个交付文件全部就位（8 张 PNG + 8 份同名 DSL + "
        "delivery-manifest.json + frame-data.json + timing.json + limitations.md + "
        "pixel-audit.json + snapshot-usage.md + task-metrics.json）。"
        "tasks_detail 的 A23 条目写入完整明细，completed 22→23、pending 8→7、"
        "current_task 指向 A24。追加 1 条 events.jsonl 事件，保存新编号检查点" % NOW
    )
    doc["tasks_detail_note"] = (
        "tasks_detail 目前逐题记录了 %s–%s 共 %d 条；A01–A08 只出现在 completed 清单里，"
        "没有对应的逐题明细条目（缺起止时间、请求数、指标路径）。该缺口是 A09 之前遗留的"
        "记录问题，不补造：补造需要当时的真实产物与日志，凭空填会制造虚假留痕，"
        "逐题明细以各题 task-metrics.json 与 outputs/<run_id>/<task_id>/ 目录为准"
        % (ids[0], ids[-1], n_detail)
    )
    doc["suite_progress_note"] = (
        "A01–A23 共 23 题完成；A23 全部交付就位：1200×800 RGB PNG 封面（标题「从结构到画面」"
        "WCAG AA 4.5:1 通过）+ 6 张 600×600 透明 PNG 关键帧（无文字、12 单元守恒、"
        "同伦因子 1.33→1.000 的分散到汇聚）+ contact-sheet + delivery-manifest + "
        "frame-data.json（12 单元 / 6 帧 / 12 条轨迹 / 接缝逐 ID）+ timing.json（250 ms/帧、"
        "1500 ms 循环、seamless=false 与接缝证据）+ limitations.md（能力边界 4 项判定）+ "
        "pixel-audit.json + snapshot-usage.md + task-metrics.json，共 24 个文件、8 张最终图。"
        "20/20 干跑门禁、72/72 像素审计判定、6/6 审计活性证明；43 次 POST /snapshot"
        "（11 成功 / 29 服务端 400 / 3 传输超时）、24 个提交组（成功 11 / 始终失败 13）、"
        "重试 19 次、请求往返合计 84.609 s、累计墙钟 %.0f s；5 次实际看图（另 3 张经接触表"
        "读到）、1 次视觉迭代、7 处审计器修复 + 2 处审计报告修复。"
        "A24、B01–B06 共 7 题待执行" % tm["elapsed_seconds"]
    )
    STATE.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n",
                     encoding="utf-8")

    # ---- 事件
    ev = {
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
        "syntax_fix_resubmits": c["syntax_fix_resubmits"],
        "dsl_versions": c["dsl_versions"],
        "submission_groups": c["submission_groups"],
        "image_views": c["image_views"],
        "image_views_via_contact_sheet": c["image_views_via_contact_sheet"],
        "visual_iterations": c["completed_visual_iterations"],
        "audit_fixes": c["audit_fixes"],
        "audit_report_fixes": c["audit_report_fixes"],
        "audit_selftests_added": c["audit_selftests_added"],
        "dryrun_gates": "%d/%d" % (c["dryrun_gates_passed"], c["dryrun_gates_total"]),
        "pixel_audit": "%d/%d" % (c["pixel_audit_checks_passed"],
                                  c["pixel_audit_checks_total"]),
        "activation_tests": "6/6",
        "units": c["units"],
        "frames": c["frames"],
        "unit_instances_checked": c["unit_instances_checked"],
        "seamless": c["seamless"],
        "seam_jump_range_px": c["seam_jump_range_px"],
        "request_duration_sum_seconds": tm["request_duration_sum_seconds"],
        "transport_read_timeout_seconds": tm["transport_read_timeout_seconds"],
        "wall_clock_seconds": tm["elapsed_seconds"],
        "started_at": tm["started_at"],
        "ended_at": tm["ended_at"],
        "detail": (
            "A23（格式边界下的动画分镜交付）完成：客户请求「文字可编辑 SVG / CMYK 印刷稿 / "
            "6 帧透明 GIF / PNG 封面」，其中 SVG、CMYK 原生不支持、GIF 格式不支持，"
            "PNG 封面支持。已按题目授权交付 1200×800 RGB PNG 封面 + 6 张 600×600 透明 PNG "
            "关键帧，各附完整 .snapshot；timing.json 表达 250 ms/帧与 1500 ms 循环；"
            "frame-data.json 用稳定 ID U01–U12 记录 12 单元的守恒属性、6 帧完整参数、"
            "逐单元相邻帧位移与角差、smoothstep 缓动与全局同伦公式，以及 1250→1500/0 接缝的"
            "逐 ID 位移（39.6344–136.0625 px）、旋转跳（0°–120°）、方向（12 单元全部背离"
            "场景中心 C=(40,330)）与速度比（3.3784 倍，12 单元完全相同）。"
            "seamless 明确为 false，不因为 loop=true 就宣称无缝。"
            "20/20 干跑门禁、72/72 像素审计判定、6/6 审计活性证明、8/8 交付字节恒等于服务"
            "响应；5 次实际看图 + 3 张经接触表读到。最大代价是首版把 width/height 写在 "
            "<Snapshot> 上导致 29 次请求 400（Layout size is infinite），靠 5 个最小探针"
            "定位到根因。未合成 GIF、未矢量化、未转 CMYK、未创建任何假的目标格式文件。"
            "进入 A24"
        ),
        "task_status": "completed",
        "next_task": NEXT,
        "suite_counts_by_status": dict(doc["counts_by_status"]),
    }
    with EVENTS.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(ev, ensure_ascii=False) + "\n")

    # ---- 新编号检查点
    CKPT.mkdir(parents=True, exist_ok=True)
    existing = sorted(p.name for p in CKPT.glob("state-*.json"))
    n = len(existing) + 1
    cp_path = CKPT / ("state-%06d.json" % n)
    cp = {
        "checkpoint": n,
        "created_at": NOW,
        "timezone": "Asia/Shanghai (UTC+08:00)",
        "reason": "A23 全部交付完成并归档（24 个文件、8 张最终图），进入 A24",
        "suite_state_snapshot": dict(doc),
        "event_count": len(EVENTS.read_text(encoding="utf-8").splitlines()),
        "restore": {
            "how": (
                "suite-state.json 允许更新，恢复时以最新 checkpoint 的 "
                "suite_state_snapshot 为准；A23 已 completed，24 个交付文件均已就位"
                "且不覆盖；下一题 A24 按 catalog.json 的 task_order 继续"
            ),
            "resume_from": "tasks/A24-*（按 catalog.json 的 task_order）",
            "done_in_this_checkpoint": [
                "A01–A23 共 23 题 completed",
                "A23 全部 24 个交付文件（8 PNG + 8 DSL + 8 份 JSON/MD 报告）",
                "A23 的 20/20 干跑门禁、72/72 像素审计、6/6 活性证明、8/8 字节恒等",
            ],
            "scripts": [s % RUN_ID for s in SCRIPTS],
            "pending": [
                "继续 A24、B01–B06（共 7 题）",
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

    print("suite-state 已写 A23 明细，updated_at=%s" % NOW)
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
