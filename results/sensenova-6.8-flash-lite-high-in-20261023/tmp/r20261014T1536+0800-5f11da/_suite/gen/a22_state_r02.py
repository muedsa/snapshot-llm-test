"""A22 round-02 归档：更新套级 suite-state.json、追加 events.jsonl、保存检查点。

只更新 suite-state.json 这个「允许更新的当前指针」；
checkpoints/state-*.json 是历史快照，只新增编号、绝不覆盖。
round-01 的条目从 suite-state.json 里读出来原样保留，只追加 round-02。

用法
    python -I -X utf8 a22_state_r02.py
"""
from __future__ import annotations

import datetime as dt
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
# HERE = <suite_root>/tmp/<run_id>/_suite/gen/a22_state_r02.py
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
OD = "outputs/%s/A22" % RUN_ID
TD = "tmp/%s/A22" % RUN_ID
R2 = "outputs/%s/A22/round-02" % RUN_ID

DISCLOSURES = [
    {
        "id": "a22-r2-u1",
        "issue": "footer 细条裁切（3008×64，宽高比 47:1）再次被图像查看接口拒收",
        "why": "本轮实际重试一次确认仍被拒收（media removed — rejected by API），与 round-01 是同一平台限制",
        "impact": "viewing-evidence.json 的 a22-r02-view-footer-010 事件没有对应的真实查看",
        "mitigation": "footer 可读性由 footer_left / footer_right（各 752×60，12.5:1）与 whole 1:1 确认；已在 rounds[\"2\"].notes 追加一条批注说明该事件未真正打开，原事件字段一字未改；counts.image_views=9 只算真正打开的，image_views_rejected_by_api=1 单列",
        "status": "disclosed",
    },
    {
        "id": "a22-r2-u2",
        "issue": "像素审计第 6 项的算法在本轮被改写了三次，round-01 的报告正文是旧表述",
        "why": "三次都是改检查器而不是改图：(1) 索引漏减 PLOT[\"left\"]；(2) 挖墨迹外接框的修复是空操作（切片下标基准错一层，cnt 366→366 没变）；(3) ink-bbox 方案有漏报盲区（柱体比框大且落在框内时柱体被当成墨迹挖掉），整个方案换成「柱体列窗口内实心行段 ≥4 行」判定",
        "impact": "同一套检查在两个轮次里一度是两套标准；round-01 的 snapshot-usage.md 第 4.2 节仍是旧判定表述",
        "mitigation": "round-01 与 round-02 的 change-audit.json、a22_audit_r1/r2.out.json 都用新算法重跑刷新，两者仍 12/12；新增 a22_selftest_label_gate.py 用 7 张合成图反测活性（含同色压柱必报、压 3 行不报）；round-01 历史正文不回写，改在其报告尾部追加第 9 节「轮后补充」说明差异",
        "status": "disclosed",
    },
    {
        "id": "a22-r2-u3",
        "issue": "change-audit.json 的 regression.viewing.viewing_events 在审计时刻是 1，归档后实际是 10",
        "why": "审计在只看图 1 张时运行，当时写入 1",
        "impact": "报告里的看图次数小于实际记录的事件数",
        "mitigation": "归档时回写为 10，并保留 audited_at_event_count=1 与 viewing_events_updated_at 时间戳；round-01 同样处理（1→10）",
        "status": "disclosed",
    },
    {
        "id": "a22-r2-u4",
        "issue": "本轮 completed_visual_iterations=0，iterations.jsonl 无 round-02 条目",
        "why": "数据更正是一次性重算，首版渲染即满足 28/28 干跑门禁与 12/12 像素审计，9 次看图未发现影响交付的缺陷",
        "impact": "迭代数为 0 可能被误读为缺失留痕",
        "mitigation": "这是首版即达标的证据而不是缺失；3 次审计脚本修复单独记在 counts.audit_fixes，不与视觉迭代混算（改检查器不等于改作品）",
        "status": "disclosed",
    },
    {
        "id": "a22-r2-u5",
        "issue": "负轴使全部 12 根柱等比例变矮 11.2%（0.001317 → 0.001170 px/元）",
        "why": "轴底由 0 扩到 −30,000 元，量程 240,000 → 270,000，绘图区框与 chart 区域边界不变，零线由 y=852 移到 y=817",
        "impact": "与 round-01 相比所有柱都变矮了，可能被误判为渲染异常",
        "mitigation": "这是负轴的必然后果：若保持原像素高就等于谎称比例没变。审计第 4 项用**新的**比例逐根量高度，12 根全部 ±1 px 一致；change-audit.json 的 changes[1].geometry 记录了前后两套 scale/zero_y/axis_min",
        "status": "disclosed",
    },
]


def build_round02() -> dict:
    return {
        "round": 2,
        "status": "completed",
        "output_subdirectory": "round-02",
        "spec_source": "tasks/A22-staged-data-correction/rounds/round-02.md",
        "started_at": "2026-10-20T15:06:53+08:00",
        "started_at_note": "取本轮首条快照请求；此前给 a22_data.py 的 _apply(2) 加两项更正、给 a22_build.py 加负轴与负柱代码的时间没有独立时间戳，未计入 elapsed_seconds，所以墙钟是下界",
        "ended_at": "2026-10-20T16:57:03+08:00",
        "elapsed_seconds": 6550.0,
        "final_images": 1,
        "final_images_required": 1,
        "final_images_note": "dashboard.png 1600x1000，PNG 读 IHDR 实测一致；服务返回的原始字节，未后处理",
        "artifacts": [
            R2 + "/dashboard.png",
            R2 + "/dashboard.snapshot",
            R2 + "/computed-data.json",
            R2 + "/layout-map.json",
            R2 + "/change-audit.json",
            R2 + "/snapshot-usage.md",
            R2 + "/task-metrics.json",
        ],
        "artifacts_note": "round-02.md 列出的 7 个文件全部交付，没有多做也没有缺项",
        "metrics": R2 + "/task-metrics.json",
        "logs": {
            "requests": "tmp/%s/A22/requests.jsonl" % RUN_ID,
            "iterations": "tmp/%s/A22/iterations.jsonl" % RUN_ID,
            "viewing_evidence": "tmp/%s/A22/viewing-evidence.json" % RUN_ID,
            "preview_manifest": "tmp/%s/A22/preview/round-02/views-manifest.json" % RUN_ID,
            "gate_report": "tmp/%s/A22/gate-reports/round-02.json" % RUN_ID,
            "responses": "tmp/%s/A22/responses/" % RUN_ID,
            "audit_stdout_copy": "tmp/%s/_suite/gen/a22_audit_r2.out.json" % RUN_ID,
            "audit_selftest": "tmp/%s/_suite/gen/a22_selftest_label_gate.py" % RUN_ID,
        },
        "quality_gates": {
            "dryrun": "28/28",
            "dryrun_report": "tmp/%s/A22/gate-reports/round-02.json" % RUN_ID,
            "pixel_audit": "12/12",
            "pixel_audit_report": R2 + "/change-audit.json",
            "pixel_audit_selftest": "7/7（a22_selftest_label_gate.py，合成图反测标签压柱判定的活性）",
            "visual_review": "9 次实际打开并读到内容（整图 1:1 + header/conclusion/kpi/chart/table 放大 + 零线负柱 2× 局部 + footer 两半 12.5:1）；另有 1 次 footer 整条裁切被接口拒收",
            "contrast_min": 4.552,
            "body_font_min_px": 22,
            "table_cells_checked": 30,
            "region_box_delta_max_px": 0,
            "region_box_tolerance_px": 2,
        },
        "delivery_verified_by": "响应字节 sha256 与交付 PNG sha256 比对一致（359d5e6a…）；交付 DSL 与当前构造器重建结果逐字节一致（审计第 2 项）",
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
        "audit_fixes": 3,
        "audit_fixes_note": "改的是审计脚本而不是图，未重渲，不计入视觉迭代",
        "audit_selftests_added": 1,
        "request_duration_sum_seconds": 5.016,
        "requirements_note": "round-02.md 逐项核对：两项更正已应用且 CSV 原值不改（每月 csv_original 保留原值）、其余原始数据不变（2026-04–07 与全部 orders/sessions）、重算每月/汇总/KPI/图表/表格/标题结论、允许在原 chart 区域内增加负轴范围、六个主区域框分量差 0 px（容差 ±2）、主字体与视觉系统未动、负值未裁掉未画成正值未只改数字不改柱高、真实看图",
        "data_note": "6 个月 2026-04→2026-09，applied_changes 2 项：2026-08 refund_amount 15,048→25,048（+10,000）、2026-09 operating_cost 138,000→208,000（+70,000）。净收入合计 908,624 元（−10,000）、经营利润 182,124 元（−80,000）、总订单 3,045 笔（不变）、总访问 27,300 次（不变）、总体转化率 11.15%（不变）、总体退款率 6.81%（+1.02pp）、利润率 20.04%（−8.49pp）；2026-09 利润 −5,632 元成为全期唯一亏损月（成本 208,000 − 净收入 202,368 = 5,632）；期间汇总为各月先分别求和，不平均各月百分比；交叉验算通过",
        "geometry_note": "轴 −30,000→240,000 步长 60,000 共 6 条刻度线，零线 y=816.9（实测 817），比例 0.001170 px/元（上一轮 0.001317），绘图区框 [152,536,860,852] 未变；12 根柱高度与计算值全部 ±1 px 一致，负柱 7 px 画在零线下方、未放大未隐藏；表格行高 62.33 px 与上一轮相同；标签 7 个（6 净收入 + 1 负值利润），标签与柱体不相交对数 84、最近间距 4.0 px",
        "defects_found_and_fixed": 0,
        "defects_detail": "本轮没有发现需要改图的缺陷：28/28 干跑门禁与 12/12 像素审计在首版渲染上就全部通过，9 次实际看图也没有发现影响交付的问题。审计脚本自身的 3 个缺陷已修（改检查器、不是改图），并用 7 例合成图反测活性",
        "unresolved_issues": DISCLOSURES,
    }


def build_task(current: dict) -> dict:
    rounds = list(current.get("rounds", []))
    rounds = [r for r in rounds if r.get("round") != 2]
    rounds.append(build_round02())
    rounds.sort(key=lambda r: r.get("round") or 0)
    return {
        "id": A,
        "status": "in_progress",
        "status_note": "预置连续三轮任务的第 2 轮已完成归档；round-03 待执行。三轮共用一套构造器/门禁/渲染代码（tmp/…/_suite/gen/a22_build.py、a22_data.py），轮次差异由 a22_data.py 的 _apply(round_no) 注入",
        "execution_mode": "预置连续执行（自动三轮）：round-01 归档后才读取 rounds/round-02.md，round-02 归档后才读取 rounds/round-03.md；不等待外部反馈",
        "started_at": current.get("started_at", "2026-10-20T12:24:03+08:00"),
        "output_dir": OD,
        "temp_dir": TD,
        "rounds_total": 3,
        "rounds_done": 2,
        "rounds": rounds,
    }


def main() -> int:
    doc = json.loads(STATE.read_text(encoding="utf-8"))
    detail = [t for t in doc["tasks_detail"] if t["id"] == A]
    if detail:
        detail[0].update(build_task(detail[0]))
    else:
        doc["tasks_detail"].append(build_task({}))
    doc["current_round"] = {
        "task_id": A,
        "round": 2,
        "rounds_total": 3,
        "status": "completed",
        "next": "读取 tasks/A22-staged-data-correction/rounds/round-03.md，新增 2026-10 月份并重算（round-02 的两项更正继续有效）",
        "note": "round-02 应用两项财务更正：2026-08 退款 15,048→25,048、2026-09 经营成本 138,000→208,000；期间利润 262,124→182,124 元（−80,000），2026-09 成为唯一亏损月，轴在原 chart 区域内扩到 −30,000 元",
    }
    doc["updated_at"] = NOW
    doc["updated_at_note"] = (
        "%s 由 a22_state_r02.py 归档 A22 round-02：tasks_detail 的 A22 条目追加 round-02、"
        "rounds_done 1→2、status 仍为 in_progress（round-03 待执行）、更新 current_round、"
        "追加 events.jsonl 两条事件、保存新编号检查点。round-01 条目原样保留；"
        "A22 的 completed/pending 计数在三轮全部完成前保持不动；历史快照不覆盖" % NOW)
    STATE.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n",
                     encoding="utf-8")

    ev = [
        {
            "ts": NOW, "timezone": "Asia/Shanghai (UTC+08:00)",
            "event": "round_started", "task_id": A, "run_id": RUN_ID,
            "round": 2, "rounds_total": 3,
            "started_at": "2026-10-20T15:06:53+08:00",
            "note": "A22 财务更正轮：2026-08 refund_amount 15,048→25,048、"
                    "2026-09 operating_cost 138,000→208,000，其余原始数据不变；"
                    "CSV 只读，更正只在计算层 _apply(2) 生效",
        },
        {
            "ts": NOW, "timezone": "Asia/Shanghai (UTC+08:00)",
            "event": "round_completed", "task_id": A, "run_id": RUN_ID,
            "round": 2, "rounds_total": 3, "status": "completed",
            "output_dir": R2,
            "temp_dir": TD,
            "requests": 1, "http_requests": 1,
            "successful_requests": 1, "failed_requests": 0,
            "image_views": 9, "image_view_events_logged": 10,
            "image_views_rejected_by_api": 1,
            "visual_iterations": 0, "audit_fixes": 3,
            "dryrun_gates": "28/28", "pixel_audit": "12/12",
            "pixel_audit_selftest": "7/7",
            "request_duration_sum_seconds": 5.016,
            "wall_clock_seconds": 6550.0,
            "deliverables": [
                R2 + "/dashboard.png",
                R2 + "/dashboard.snapshot",
                R2 + "/computed-data.json",
                R2 + "/layout-map.json",
                R2 + "/change-audit.json",
                R2 + "/snapshot-usage.md",
                R2 + "/task-metrics.json",
            ],
            "detail": "A22 round-02（财务更正轮）完成：期间净收入 918,624→908,624 元"
                      "（−10,000）、经营利润 262,124→182,124 元（−80,000）、"
                      "总体退款率 5.79%→6.81%、利润率 28.53%→20.04%；总订单与总体转化率不变。"
                      "2026-09 经营利润 −5,632 元成为全期唯一亏损月（成本 208,000 − 净收入 "
                      "202,368 = 5,632），轴在原 chart 区域内由 0 扩到 −30,000 元，零线 "
                      "y=852→817，比例 0.001317→0.001170 px/元，六个主区域框分量差 0 px。"
                      "12 根柱高度与计算值全部 ±1 px 一致，负柱 7 px 画在零线下方未放大未隐藏。"
                      "1 次请求即成功（无 400、无重试）：round-01 加的渐变端点离线门禁生效。"
                      "0 次图面迭代（首版即达标）；审计脚本自修 3 次并新增 7 例合成图自检，"
                      "round-01/02 的 change-audit 都用新算法重跑刷新（仍各 12/12）。"
                      "9 次实际看图；footer 47:1 裁切再次被接口拒收已如实披露。"
                      "5 项记录类事项已逐条披露，未补造任何日志",
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
        "reason": "A22 round-02 归档完成，进入 round-03",
        "suite_state_snapshot": dict(doc),
        "event_count": len(EVENTS.read_text(encoding="utf-8").splitlines()),
        "restore": {
            "how": "suite-state.json 允许更新，恢复时以最新 checkpoint 的 suite_state_snapshot 为准；round-03 的轮次文件与产物按 tasks_detail.A22.rounds 继续追加，不覆盖 round-01/02",
            "resume_from": "tasks/A22-staged-data-correction/rounds/round-03.md",
            "scripts": [
                "tmp/%s/_suite/gen/a22_data.py" % RUN_ID,
                "tmp/%s/_suite/gen/a22_build.py" % RUN_ID,
                "tmp/%s/_suite/gen/a22_log.py" % RUN_ID,
                "tmp/%s/_suite/gen/a22_view_footer.py" % RUN_ID,
                "tmp/%s/_suite/gen/a22_selftest_label_gate.py" % RUN_ID,
                "tmp/%s/_suite/gen/a22_state_r01.py" % RUN_ID,
                "tmp/%s/_suite/gen/a22_state_r02.py" % RUN_ID,
            ],
            "pending": [
                "读取 rounds/round-03.md 并执行 round-03（新增 2026-10，round-02 两项更正继续有效）",
                "round-03 归档后写 A22 题目层的 snapshot-usage.md 与 task-metrics.json",
                "round-03 完成后把 suite-state.json 的 A22 状态改为 completed、rounds_done=3",
                "之后继续 A23、A24、B01–B06 与套级总审查",
            ],
        },
    }
    cp_path.write_text(json.dumps(cp, ensure_ascii=False, indent=1) + "\n",
                       encoding="utf-8")

    print("suite-state 已更新：A22 status=in_progress，rounds_done=2/3，rounds=%d 条"
          % len(detail[0]["rounds"]))
    print("events.jsonl 追加 2 条，当前 %d 条"
          % len(EVENTS.read_text(encoding="utf-8").splitlines()))
    print("检查点 %s" % cp_path.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
