"""A22 round-03 归档（末轮）：更新套级 suite-state.json、追加 events.jsonl、保存检查点。

与 a22_state_r01.py / a22_state_r02.py 同一模式：
只更新 suite-state.json 这个「允许更新的当前指针」；
checkpoints/state-*.json 是历史快照，只新增编号、绝不覆盖。
round-01 / round-02 的条目从 suite-state.json 里读出来原样保留，只追加 round-03。

本轮是三轮的末轮，所以同时把 A22 的 status 改为 completed、rounds_done 改为 3，
并更新套级计数（completed 21→22、pending 9→8、current_task 改为 A23）。
套级 index/gallery/snapshot-usage/task-metrics 仍在全部 30 题完成后由总审查生成，
本脚本不提前生成。

用法
    python -I -X utf8 a22_state_r03.py
"""
from __future__ import annotations

import datetime as dt
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
# HERE = <suite_root>/tmp/<run_id>/_suite/gen/a22_state_r03.py
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
R3_START = "2026-10-20T17:24:37+08:00"
# 三轮墙钟之和（round-01 8466 + round-02 6550 + round-03 见下方按 NOW 计算）
R1_ELAPSED = 8466.0
R2_ELAPSED = 6550.0


def _parse(ts: str) -> dt.datetime:
    return dt.datetime.fromisoformat(ts)


def r3_elapsed(now: str) -> float:
    """round-03 的墙钟 = NOW − 首条快照请求时刻。"""
    return round((_parse(now) - _parse(R3_START)).total_seconds(), 1)
OD = "outputs/%s/A22" % RUN_ID
TD = "tmp/%s/A22" % RUN_ID
R3 = "outputs/%s/A22/round-03" % RUN_ID

DISCLOSURES = [
    {
        "id": "a22-r3-u1",
        "issue": "footer 细条裁切（3008×64，宽高比 47:1）第三次被图像查看接口拒收",
        "why": "本轮实际重试一次确认仍被拒收（media removed — rejected by API），与 round-01、round-02 是同一个平台限制",
        "impact": "viewing-evidence.json 的 a22-r03-view-footer-010 事件没有对应的真实查看",
        "mitigation": "footer 可读性由 footer_left / footer_right（各 752×60，12.5:1）与 whole 1:1 确认；已在 rounds[\"3\"].notes 追加一条批注说明该事件未真正打开，原事件字段一字未改；counts.image_views=9 只算真正打开的，image_views_rejected_by_api=1 单列。处置办法已固化在 a22_view_footer.py，后续同类任务可直接复用",
        "status": "disclosed",
    },
    {
        "id": "a22-r3-u2",
        "issue": "本轮 completed_visual_iterations=0 且 audit_fixes=0，iterations.jsonl 无 round-03 条目",
        "why": "新增月份是一次性重算，首版渲染即满足 28/28 干跑门禁与 12/12 像素审计，9 次看图未发现影响交付的缺陷",
        "impact": "两个 0 都可能被误读为缺失留痕或没做检查",
        "mitigation": "这是首版即达标 + 前置防线已就位的结果，不是缺失：round-01 填了渲染层的坑、round-02 填了审计层的坑并加了自检脚本，round-03 只需喂一行新数据。独立证据为门禁 28/28、审计 12/12、9 次实际看图、14 根柱 delta 全 0",
        "status": "disclosed",
    },
    {
        "id": "a22-r3-u3",
        "issue": "服务端自报耗时与本地实测的差值在三轮里持续增大（round-02 2.981 s、round-03 10.549 s）",
        "why": "差值来自网络往返与本地处理，不可观测",
        "impact": "若误把服务端自报耗时当成请求耗时之和，会低估等待",
        "mitigation": "计时口径统一以本地 elapsed_ms 为准，服务端自报值仅作参照；两者与差值都写进 server_timing_source",
        "status": "disclosed",
    },
    {
        "id": "a22-r3-u4",
        "issue": "总体转化率与总体退款率被新增月拉低、利润率被拉高，三个比率方向不一致",
        "why": "2026-10 的转化率 10.85% 与退款率 5.00% 低于原期间值，但利润率 33.27% 高于原期间值 20.04%",
        "impact": "容易被合并成一句「整体变好了」的定性判断",
        "mitigation": "结论区分条陈述，每项比率单独给分子分母与百分点差；不写跨指标的综合定性结论",
        "status": "disclosed",
    },
]


def build_round03() -> dict:
    return {
        "round": 3,
        "status": "completed",
        "output_subdirectory": "round-03",
        "spec_source": "tasks/A22-staged-data-correction/rounds/round-03.md",
        "started_at": R3_START,
        "started_at_note": "取本轮首条（也是唯一一条）快照请求；此前给 a22_data.py 的 _apply(3) 加 2026-10 一行、给 a22_build.py 按月份数重算组槽宽与行高的代码改动没有独立时间戳，未计入 elapsed_seconds，所以墙钟是下界",
        "ended_at": NOW,
        "elapsed_seconds": r3_elapsed(NOW),
        "elapsed_note": "从 %s 到 %s 共 %.1f s；含看图、像素审计与写报告，不含上述前置代码改动时间。墙钟远大于 request_duration_sum_seconds（12.375 s），两者不可相加" % (R3_START, NOW, r3_elapsed(NOW)),
        "final_images": 1,
        "final_images_required": 1,
        "final_images_note": "dashboard.png 1600x1000，PNG 读 IHDR 实测一致；服务返回的原始字节，未后处理",
        "artifacts": [
            R3 + "/dashboard.png",
            R3 + "/dashboard.snapshot",
            R3 + "/computed-data.json",
            R3 + "/layout-map.json",
            R3 + "/change-audit.json",
            R3 + "/snapshot-usage.md",
            R3 + "/task-metrics.json",
        ],
        "artifacts_note": "round-03.md 列出的 7 个文件全部交付，没有多做也没有缺项",
        "metrics": R3 + "/task-metrics.json",
        "logs": {
            "requests": "tmp/%s/A22/requests.jsonl" % RUN_ID,
            "iterations": "tmp/%s/A22/iterations.jsonl" % RUN_ID,
            "viewing_evidence": "tmp/%s/A22/viewing-evidence.json" % RUN_ID,
            "preview_manifest": "tmp/%s/A22/preview/round-03/views-manifest.json" % RUN_ID,
            "gate_report": "tmp/%s/A22/gate-reports/round-03.json" % RUN_ID,
            "responses": "tmp/%s/A22/responses/" % RUN_ID,
            "audit_stdout_copy": "tmp/%s/_suite/gen/out_r3_audit.json" % RUN_ID,
            "dryrun_stdout_copy": "tmp/%s/_suite/gen/out_r3_dryrun.txt" % RUN_ID,
            "layout_stdout_copy": "tmp/%s/_suite/gen/out_r3_layout.txt" % RUN_ID,
            "render_stdout_copy": "tmp/%s/_suite/gen/out_r3_render.txt" % RUN_ID,
        },
        "quality_gates": {
            "dryrun": "28/28",
            "dryrun_report": "tmp/%s/A22/gate-reports/round-03.json" % RUN_ID,
            "pixel_audit": "12/12",
            "pixel_audit_report": R3 + "/change-audit.json",
            "pixel_audit_selftest": "7/7（沿用 round-02 新增的 a22_selftest_label_gate.py）",
            "visual_review": "9 次实际打开并读到内容（整图 1:1 + header/conclusion/kpi/chart/table 放大 + 零线负柱 2× 局部 + footer 两半 12.5:1）；另有 1 次 footer 整条裁切被接口拒收",
            "contrast_min": 4.552,
            "body_font_min_px": 22,
            "text_segments_checked": 90,
            "table_cells_checked": 35,
            "region_box_delta_max_px": 0,
            "region_box_tolerance_px": 2,
        },
        "delivery_verified_by": "响应字节 sha256 与交付 PNG sha256 比对一致（b041c03b…）；交付 DSL 与当前构造器重建结果逐字节一致（审计第 2 项）",
        "requests": 1,
        "http_requests": 1,
        "successful_requests": 1,
        "failed_requests": 0,
        "retry_requests": 0,
        "syntax_fix_resubmits": 0,
        "dsl_versions": 1,
        "image_views": 9,
        "image_view_events_logged": 10,
        "image_views_rejected_by_api": 1,
        "completed_visual_iterations": 0,
        "completed_visual_iterations_note": "首版即达标，不制造迭代",
        "audit_fixes": 0,
        "audit_fixes_note": "本轮未修改审计脚本；前三道「标签不压柱」防线与自检脚本沿用 round-02 的版本",
        "request_duration_sum_seconds": 12.375,
        "requirements_note": "round-03.md 逐项核对：新增 2026-10 整行五字段按给定值、派生值由公式算出；第二轮两项更正继续有效未回退；1600×1000；KPI 改为 7 个月期间汇总；图与表含全部 7 个月且 2026-04 未省略、末月 2026-10；六个主区域框分量差 0 px（容差 ±2）；正文最小 22；内部刻度/行距重排（组槽宽 118.00→101.14、行高 62.33→53.43）；轴未偷偷重排（round-02 的 12 根继承柱像素高逐根一致）；每项累计值/轴/结论已核对；真实看图",
        "data_note": "7 个月 2026-04→2026-10。applied_changes 3 项：沿用 2026-08 refund_amount 25,048、2026-09 operating_cost 208,000，新增 2026-10 整行（orders 640 / gross 224,000 / refund 11,200 / cost 142,000 / sessions 5,900 → 净收入 212,800、利润 70,800、退款率 5.00%、转化率 10.85%）。期间净收入 1,121,424 元（+212,800）、经营利润 252,924 元（+70,800）、总订单 3,685 笔（+640）、总访问 33,200 次（+5,900）、总体转化率 11.15%→11.10%（−0.05pp）、总体退款率 6.81%→6.47%（−0.34pp）、利润率 20.04%→22.55%（+2.51pp）；2026-10 的净收入与经营利润同时成为全期最高；2026-09 的 −5,632 仍为唯一亏损月；期间汇总为各月先分别求和，不平均各月百分比；交叉验算通过",
        "geometry_note": "轴沿用 round-02 的 −30,000→240,000、步长 60,000、6 条刻度线、零线 y=816.9（实测 817）、比例 0.001170 px/元、绘图区框 [152,536,860,852] 全部不变——新增月是正值，不需要再动轴。组槽宽 118.00→101.14 px（柱宽 30、组内间距 6、组宽 66 不变，组间净空 52→35.14），行高 62.33→53.43 px（表头 38 + 7×53.43 = 412.0 恰等于区域内容高）。14 根柱 delta_height_px 全部为 0（像素级精确一致），其中 round-02 的 12 根继承柱像素高逐根不变；标签 8 个（7 净收入 + 1 负值利润），8×14=112 对全部不相交、最近间距 4.0 px",
        "defects_found_and_fixed": 0,
        "defects_detail": "本轮没有发现需要改图的缺陷：28/28 干跑门禁与 12/12 像素审计在首版渲染上就全部通过，9 次实际看图也没有发现影响交付的问题。审计脚本本身也没有被修改",
        "unresolved_issues": DISCLOSURES,
    }


def build_task(current: dict) -> dict:
    rounds = list(current.get("rounds", []))
    rounds = [r for r in rounds if r.get("round") != 3]
    rounds.append(build_round03())
    rounds.sort(key=lambda r: r.get("round") or 0)
    return {
        "id": A,
        "status": "completed",
        "status_note": "预置连续三轮全部完成并归档：round-01 基线、round-02 财务更正、round-03 新增月份。三轮共用一套构造器/门禁/渲染代码（tmp/…/_suite/gen/a22_build.py、a22_data.py），轮次差异由 a22_data.py 的 _apply(round_no) 注入；题目层累计报告与指标在 outputs/%s/A22/snapshot-usage.md 与 task-metrics.json" % RUN_ID,
        "execution_mode": "预置连续执行（自动三轮）：round-01 归档后才读取 rounds/round-02.md，round-02 归档后才读取 rounds/round-03.md；不等待外部反馈",
        "started_at": current.get("started_at", "2026-10-20T12:24:03+08:00"),
        "ended_at": NOW,
        "elapsed_seconds": R1_ELAPSED + R2_ELAPSED + r3_elapsed(NOW),
        "elapsed_note": "三轮墙钟之和：%.0f + %.0f + %.1f = %.1f s（约 %.1f h）。每轮各自的 started_at 取该轮首条快照请求，前置代码改动时间不计入，所以合计仍是下界。请求耗时之和 35.314 s 与墙钟不可相加" % (R1_ELAPSED, R2_ELAPSED, r3_elapsed(NOW), R1_ELAPSED + R2_ELAPSED + r3_elapsed(NOW), (R1_ELAPSED + R2_ELAPSED + r3_elapsed(NOW)) / 3600.0),
        "output_dir": OD,
        "temp_dir": TD,
        "rounds_total": 3,
        "rounds_done": 3,
        "rounds": rounds,
        "final_images": 3,
        "final_images_required": 3,
        "artifacts": [
            "outputs/%s/A22/round-01/dashboard.png" % RUN_ID,
            "outputs/%s/A22/round-01/dashboard.snapshot" % RUN_ID,
            "outputs/%s/A22/round-02/dashboard.png" % RUN_ID,
            "outputs/%s/A22/round-02/dashboard.snapshot" % RUN_ID,
            "outputs/%s/A22/round-03/dashboard.png" % RUN_ID,
            "outputs/%s/A22/round-03/dashboard.snapshot" % RUN_ID,
            "outputs/%s/A22/snapshot-usage.md" % RUN_ID,
            "outputs/%s/A22/task-metrics.json" % RUN_ID,
        ],
        "metrics": "outputs/%s/A22/task-metrics.json" % RUN_ID,
        "requests": 5,
        "http_requests": 7,
        "successful_requests": 4,
        "failed_requests": 1,
        "retry_requests": 3,
        "syntax_fix_resubmits": 1,
        "dsl_versions": 5,
        "image_views": 28,
        "image_view_events_logged": 30,
        "image_views_rejected_by_api": 2,
        "completed_visual_iterations": 1,
        "audit_fixes": 3,
        "audit_selftests_added": 1,
        "request_duration_sum_seconds": 35.314,
        "counting_note": "requests=5 是 requests.jsonl 的记录条数（round-01 3 + round-02 1 + round-03 1），http_requests=7 是实际 POST 次数（5 + 1 + 1）；两个口径不同不能互替。image_views=28 只算真正打开的视图，image_view_events_logged=30 是事件条数，image_views_rejected_by_api=2 是 round-02/03 各被拒收的 footer 裁切",
    }


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    doc = json.loads(STATE.read_text(encoding="utf-8"))
    detail = [t for t in doc["tasks_detail"] if t["id"] == A]
    if detail:
        detail[0].update(build_task(detail[0]))
    else:
        doc["tasks_detail"].append(build_task({}))

    # 套级计数：A22 由 in_progress 转入 completed
    cbs = doc.setdefault("counts_by_status", {})
    cbs["completed"] = cbs.get("completed", 0) + 1
    cbs["pending"] = max(0, cbs.get("pending", 0) - 1)
    cbs["in_progress"] = 0
    if A not in doc.get("completed", []):
        doc.setdefault("completed", []).append(A)
    doc["remaining"] = [t for t in doc.get("remaining", []) if t != A]
    doc["current_task"] = NEXT
    doc["completed_all"] = len(doc.get("completed", [])) >= doc.get("total_tasks", 30)

    doc["current_round"] = {
        "task_id": A,
        "round": 3,
        "rounds_total": 3,
        "status": "completed",
        "next": "A22 三轮全部完成，进入下一题 A23",
        "note": "round-03 新增 2026-10 整行（净收入 212,800、利润 70,800），round-02 的两项更正继续有效；"
                "期间净收入 908,624→1,121,424 元（+212,800）、经营利润 182,124→252,924 元（+70,800）、"
                "总订单 3,045→3,685 笔；总体转化率 11.15%→11.10%、总体退款率 6.81%→6.47%、"
                "利润率 20.04%→22.55%；2026-09 的 −5,632 仍为唯一亏损月，负轴沿用未撤",
    }
    doc["updated_at"] = NOW
    doc["updated_at_note"] = (
        "%s 由 a22_state_r03.py 归档 A22 round-03（末轮）：tasks_detail 的 A22 条目追加 round-03、"
        "rounds_done 2→3、status 由 in_progress 改为 completed、套级 counts_by_status 的 completed 21→22 / "
        "pending 9→8、current_task 改为 A23、更新 current_round。追加 events.jsonl 两条事件，"
        "保存新编号检查点。round-01 / round-02 条目原样保留；历史快照不覆盖。"
        "同时修正 last_checkpoint 指向本检查点（前两轮归档脚本未更新该字段，值停留在 state-000057.json）" % NOW)
    doc["tasks_detail_note"] = (doc.get("tasks_detail_note", "") +
        " A22 于 %s 完成三轮归档，status=completed、rounds_done=3，"
        "逐轮状态与指标见该条目 rounds 数组与 outputs/%s/A22/task-metrics.json。" % (NOW, RUN_ID))

    doc["suite_progress_note"] = (
        "A01–A22 共 22 题完成；A22 三轮全部归档：每轮 dashboard.png + dashboard.snapshot + computed-data.json + "
        "layout-map.json + snapshot-usage.md + task-metrics.json，round-02/03 另附 change-audit.json。"
        "干跑门禁三轮各 28/28，像素审计三轮各 12/12；5 条请求记录 / 7 个 POST（4 成功 1 失败 3 内部重试 1 语法修复重交），"
        "28 次实际看图（另有 2 次 footer 裁切被接口拒收）、1 次完整视觉迭代、3 次审计脚本修复、3 张最终图片。"
        "A23、A24、B01–B06 共 8 题待执行")
    STATE.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n",
                     encoding="utf-8")

    ev = [
        {
            "ts": NOW, "timezone": "Asia/Shanghai (UTC+08:00)",
            "event": "round_started", "task_id": A, "run_id": RUN_ID,
            "round": 3, "rounds_total": 3,
            "started_at": R3_START,
            "note": "A22 新增月份轮（末轮）：在第二轮上新增 2026-10 整行（orders 640 / gross 224,000 / "
                    "refund 11,200 / cost 142,000 / sessions 5,900），第二轮两项更正继续有效；"
                    "CSV 只读，改动只在计算层 _apply(3) 生效",
        },
        {
            "ts": NOW, "timezone": "Asia/Shanghai (UTC+08:00)",
            "event": "round_completed", "task_id": A, "run_id": RUN_ID,
            "round": 3, "rounds_total": 3, "status": "completed",
            "output_dir": R3,
            "temp_dir": TD,
            "requests": 1, "http_requests": 1,
            "successful_requests": 1, "failed_requests": 0,
            "image_views": 9, "image_view_events_logged": 10,
            "image_views_rejected_by_api": 1,
            "visual_iterations": 0, "audit_fixes": 0,
            "dryrun_gates": "28/28", "pixel_audit": "12/12",
            "pixel_audit_selftest": "7/7",
            "request_duration_sum_seconds": 12.375,
            "wall_clock_seconds": r3_elapsed(NOW),
            "deliverables": [
                R3 + "/dashboard.png",
                R3 + "/dashboard.snapshot",
                R3 + "/computed-data.json",
                R3 + "/layout-map.json",
                R3 + "/change-audit.json",
                R3 + "/snapshot-usage.md",
                R3 + "/task-metrics.json",
            ],
            "detail": "A22 round-03（新增月份轮，末轮）完成：期间净收入 908,624→1,121,424 元"
                      "（+212,800）、经营利润 182,124→252,924 元（+70,800）、总订单 3,045→3,685 笔"
                      "、总访问 27,300→33,200 次；总体转化率 11.15%→11.10%、总体退款率 6.81%→6.47%、"
                      "利润率 20.04%→22.55%（三个比率方向不一致：转化率与退款率被拉低、利润率被拉高，"
                      "结论分条陈述不合并定性）。2026-10 的净收入 212,800 与经营利润 70,800 同时成为"
                      "全期最高；2026-09 的 −5,632 仍为唯一亏损月，负轴沿用未撤。"
                      "第七组柱挤进同一 708 px：组槽宽 118.00→101.14、组间净空 52→35.14，"
                      "柱宽 30 与组内间距 6 不变；行高 62.33→53.43（表头 38 + 7×53.43 = 412.0）。"
                      "14 根柱 delta_height_px 全部为 0，其中 round-02 的 12 根继承柱像素高逐根不变，"
                      "这是「轴未被偷偷重排」的直接证据；六个主区域框分量差 0 px。"
                      "1 次请求即成功（无 400、无重试）；0 次图面迭代、0 次审计脚本修复"
                      "（首版即达标，前置防线在 round-01/02 已建好）；9 次实际看图，"
                      "footer 47:1 裁切第三次被接口拒收已如实披露。4 项记录类事项已逐条披露，"
                      "未补造任何日志。三轮到此结束",
            "task_rounds_done": 3,
            "task_status": "completed",
            "next_task": NEXT,
        },
    ]
    with EVENTS.open("a", encoding="utf-8") as fh:
        for r in ev:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    CKPT.mkdir(parents=True, exist_ok=True)
    existing = sorted(p.name for p in CKPT.glob("state-*.json"))
    n = len(existing) + 1
    cp_path = CKPT / ("state-%06d.json" % n)
    cp = {
        "checkpoint": n,
        "created_at": NOW,
        "timezone": "Asia/Shanghai (UTC+08:00)",
        "reason": "A22 round-03（末轮）与题目层归档完成，A22 三轮全部完成，进入 A23",
        "suite_state_snapshot": dict(doc),
        "event_count": len(EVENTS.read_text(encoding="utf-8").splitlines()),
        "restore": {
            "how": "suite-state.json 允许更新，恢复时以最新 checkpoint 的 suite_state_snapshot 为准；A22 已 completed、rounds_done=3，其产物不覆盖，下一题 A23 按 catalog.json 的 task_order 继续",
            "resume_from": "tasks/A23-*（按 catalog.json 的 task_order）",
            "scripts": [
                "tmp/%s/_suite/gen/a22_data.py" % RUN_ID,
                "tmp/%s/_suite/gen/a22_build.py" % RUN_ID,
                "tmp/%s/_suite/gen/a22_log.py" % RUN_ID,
                "tmp/%s/_suite/gen/a22_view_footer.py" % RUN_ID,
                "tmp/%s/_suite/gen/a22_selftest_label_gate.py" % RUN_ID,
                "tmp/%s/_suite/gen/a22_state_r01.py" % RUN_ID,
                "tmp/%s/_suite/gen/a22_state_r02.py" % RUN_ID,
                "tmp/%s/_suite/gen/a22_state_r03.py" % RUN_ID,
            ],
            "pending": [
                "继续 A23、A24、B01–B06（共 8 题）",
                "B01–B06 各至少 10 件独立完整作品",
                "全部 30 题完成后生成套级 index.md / gallery.md / snapshot-usage.md / task-metrics.json 并做总审查",
                "套级 suite-state.json 的 required_artifacts_delivered 目前为 1/5，其余 4 件由总审查补齐",
            ],
        },
    }
    cp_path.write_text(json.dumps(cp, ensure_ascii=False, indent=1) + "\n",
                       encoding="utf-8")

    # 让 round-03/task-metrics.json 的 timings 与本归档时刻一致（只改 ended_at / elapsed_seconds）
    tm_path = OUT_ROOT / A / "round-03" / "task-metrics.json"
    if tm_path.exists():
        tm = json.loads(tm_path.read_text(encoding="utf-8"))
        tm.setdefault("timings", {})["ended_at"] = NOW
        tm["timings"]["elapsed_seconds"] = r3_elapsed(NOW)
        tm_path.write_text(json.dumps(tm, ensure_ascii=False, indent=1) + "\n",
                           encoding="utf-8")
        print("round-03/task-metrics.json 的 timings.ended_at 对齐为 %s" % NOW)
    doc["last_checkpoint"] = "tmp/%s/_suite/checkpoints/%s" % (RUN_ID, cp_path.name)
    STATE.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n",
                     encoding="utf-8")

    print("suite-state 已更新：A22 status=completed，rounds_done=3/3，rounds=%d 条"
          % len(detail[0]["rounds"]))
    print("套级计数：completed=%d，pending=%d，current_task=%s，remaining=%d 题"
          % (cbs["completed"], cbs["pending"], NEXT, len(doc["remaining"])))
    print("events.jsonl 追加 2 条，当前 %d 条"
          % len(EVENTS.read_text(encoding="utf-8").splitlines()))
    print("检查点 %s" % cp_path.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
