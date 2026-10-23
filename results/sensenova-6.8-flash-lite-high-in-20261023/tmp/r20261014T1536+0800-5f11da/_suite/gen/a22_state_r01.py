"""A22 round-01 归档：更新套级 suite-state.json、追加 events.jsonl、保存检查点。

只更新 suite-state.json 这个「允许更新的当前指针」；
checkpoints/state-*.json 是历史快照，只新增编号、绝不覆盖。

用法
    python -I -X utf8 a22_state_r01.py
"""
from __future__ import annotations

import datetime as dt
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
# HERE = <suite_root>/tmp/<run_id>/_suite/gen/a22_state_r01.py
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

DISCLOSURES = [
    {
        "id": "a22-r1-u1",
        "issue": "requests.jsonl 只有 3 条记录，但实际发出 5 个 POST /snapshot",
        "why": "log_request 每次 render() 只写一条，attempts 字段给出该条内部的尝试次数；400 那一条是同一份 DSL 的内部重试 3 次",
        "impact": "按记录条数统计会低估请求次数",
        "mitigation": "task-metrics.json 同时给出 counts.snapshot_requests=3 与 counts.http_requests=5，两个口径不互相替代",
        "status": "disclosed",
    },
    {
        "id": "a22-r1-u2",
        "issue": "400 请求的前两次尝试没有独立时间戳与响应留痕",
        "why": "记录里的 started_at/ended_at/elapsed_ms（12:24:03→12:24:04，1172 ms）是第 3 次尝试的 meta",
        "impact": "前两次尝试只存在于「attempts=3」这个声明里，无法逐次追溯",
        "mitigation": "已在干跑门禁加入渐变端点取值校验，同类确定性语法错误不再消耗请求",
        "status": "disclosed",
    },
    {
        "id": "a22-r1-u3",
        "issue": "v0 与 v1 的 DSL 正文不可复原",
        "why": "tmp/…/A22/dsl/r01-dashboard.attempt-01.snapshot 每次 render 都被覆盖，现在只剩 v2 正文",
        "impact": "只能靠 requests.jsonl 的 request_bytes/request_sha256 核验这两版存在过",
        "mitigation": "v1 的服务响应原始字节完整保留在 tmp/…/A22/responses/req-a22-r01-dashboard-8102fe.png（237428 字节，sha256 ab3aa582…），视觉效果可回溯；round-02/03 起在每轮归档后立刻把 DSL 正文另存一份到 round 目录以外的临时位置",
        "status": "disclosed",
    },
    {
        "id": "a22-r1-u4",
        "issue": "迭代与看图记录的 recorded_at / opened_at 是日志写入时刻，不是发生时刻",
        "why": "iterations.jsonl 与 viewing-evidence.json 在交付渲染完成之后才建立",
        "impact": "时间戳与实际发生时刻相差数分钟到一小时",
        "mitigation": "改动的证据链改用 requests.jsonl 的时间序列（v1 12:38、v2 13:53）与 responses/ 的字节",
        "status": "disclosed",
    },
    {
        "id": "a22-r1-u5",
        "issue": "footer 细条裁切（3008×64，宽高比 47:1）被图像查看接口拒收，对应视图未能真正打开",
        "impact": "viewing-evidence.json 的 a22-r01-view-footer-008 事件没有对应的真实查看",
        "mitigation": "改裁带上下留白的两半各 752×60（12.5:1）并实际打开，作为 a22-r01-view-footer_left-009 与 footer_right-010 追加；原事件保留不改。footer 完整可读性也在 whole 视图 1:1 下确认",
        "status": "disclosed",
    },
    {
        "id": "a22-r1-u6",
        "issue": "requests.jsonl 字段命名与本套件前几题不同（request_bytes/response_bytes/request_sha256/response_sha256 vs A19/A20 的 dsl_bytes/response_path、A21 的 request_path）",
        "impact": "跨题统计必须按各题记录的实际键读取",
        "mitigation": "本条写入 disclosers；所有记录均不含密钥",
        "status": "disclosed",
    },
    {
        "id": "a22-r1-u7",
        "issue": "正值经营利润柱不带数值标签",
        "why": "708 px 绘图区放 6 组×2 柱，22 px 标签宽 74–86 px 而组宽仅 66 px；短柱的标签必然压进同组更高的净收入柱体（已作为真实视觉缺陷修掉过一次）",
        "impact": "柱图上读不到经营利润的逐月数值",
        "mitigation": "刻意的设计选择：净收入柱标注、正值利润柱由紧邻的右侧明细表承载，图表说明写明口径；另有两条检查兜底（标签与柱体不相交、未标注值必须能在表格「利润」列逐月找到）",
        "status": "disclosed",
    },
]


def build_round01() -> dict:
    return {
        "round": 1,
        "status": "completed",
        "output_subdirectory": "round-01",
        "spec_source": "tasks/A22-staged-data-correction/TASK.md 第一轮",
        "started_at": "2026-10-20T12:24:03+08:00",
        "started_at_note": "取首条快照请求（该次即 400 PARSE_ERROR）；此前编写数据层、构造器与干跑门禁、以及首轮 DSL 草稿的时间没有独立时间戳，未计入 elapsed_seconds，所以墙钟是下界",
        "ended_at": "2026-10-20T14:45:09+08:00",
        "elapsed_seconds": 8466.0,
        "final_images": 1,
        "final_images_required": 1,
        "final_images_note": "dashboard.png 1600x1000，PNG 读 IHDR 实测一致；服务返回的原始字节，未后处理",
        "artifacts": [
            "outputs/%s/A22/round-01/dashboard.png" % RUN_ID,
            "outputs/%s/A22/round-01/dashboard.snapshot" % RUN_ID,
            "outputs/%s/A22/round-01/computed-data.json" % RUN_ID,
            "outputs/%s/A22/round-01/layout-map.json" % RUN_ID,
            "outputs/%s/A22/round-01/change-audit.json" % RUN_ID,
            "outputs/%s/A22/round-01/snapshot-usage.md" % RUN_ID,
            "outputs/%s/A22/round-01/task-metrics.json" % RUN_ID,
        ],
        "artifacts_note": "TASK.md 的审计文件表只要求 round-02/03 交付 change-audit.json，round-01 这份是多做的（第一轮无上一轮可比，其 comparison 为空数组），不作为交付缺口",
        "metrics": "outputs/%s/A22/round-01/task-metrics.json" % RUN_ID,
        "logs": {
            "requests": "tmp/%s/A22/requests.jsonl" % RUN_ID,
            "iterations": "tmp/%s/A22/iterations.jsonl" % RUN_ID,
            "viewing_evidence": "tmp/%s/A22/viewing-evidence.json" % RUN_ID,
            "preview_manifest": "tmp/%s/A22/preview/round-01/views-manifest.json" % RUN_ID,
            "gate_report": "tmp/%s/A22/gate-reports/round-01.json" % RUN_ID,
            "responses": "tmp/%s/A22/responses/" % RUN_ID,
        },
        "quality_gates": {
            "dryrun": "28/28",
            "dryrun_report": "tmp/%s/A22/gate-reports/round-01.json" % RUN_ID,
            "pixel_audit": "12/12",
            "pixel_audit_report": "outputs/%s/A22/round-01/change-audit.json" % RUN_ID,
            "visual_review": "10 次实际打开（整图 1:1 + 7 个区域放大裁切 + 2 个 footer 补充裁切）",
            "contrast_min": 4.552,
            "body_font_min_px": 22,
            "table_cells_checked": 30,
        },
        "delivery_verified_by": "响应字节 sha256 与交付 PNG sha256 比对一致（654ab60e…）；交付 DSL 与当前构造器重建结果逐字节一致（审计第 2 项）",
        "requests": 3,
        "http_requests": 5,
        "successful_requests": 2,
        "failed_requests": 1,
        "retry_requests": 3,
        "syntax_fix_resubmits": 1,
        "dsl_versions": 3,
        "image_views": 10,
        "completed_visual_iterations": 1,
        "request_duration_sum_seconds": 17.923,
        "requirements_note": "TASK.md 第一轮逐项核对：1600x1000、四 KPI、两条公式、总体转化率口径、共享零起点柱图、六行五列表、仅依据实际数值的主结论、所有月份原样、正文 ≥22，见 round-01/snapshot-usage.md 第 1 节表格",
        "data_note": "6 个月 2026-04→2026-09，未应用更正（applied_changes 为空）；净收入合计 918,624 元、经营利润 262,124 元、总订单 3,045 笔、总访问 27,300 次、总体转化率 11.15%、总体退款率 5.79%；期间汇总为各月先分别求和，不平均各月百分比；交叉验算通过",
        "defects_found_and_fixed": 1,
        "defects_detail": "1) 正的经营利润柱数值标签墨迹压在净收入柱体内，导致 2026-06 净收入柱像素高被量成 113 px（应为 167 px）——按选择性直标修掉，并补上「标签与柱体不相交」的干跑门禁与像素审计项",
        "unresolved_issues": DISCLOSURES,
    }


def build_task() -> dict:
    return {
        "id": A,
        "status": "in_progress",
        "status_note": "预置连续三轮任务的第 1 轮已完成归档；round-02 与 round-03 待执行。三轮共用一套构造器/门禁/渲染代码（tmp/…/_suite/gen/a22_build.py、a22_data.py），轮次差异由 a22_data.py 的 _apply(round_no) 注入",
        "execution_mode": "预置连续执行（自动三轮）：round-01 归档后才读取 rounds/round-02.md，round-02 归档后才读取 rounds/round-03.md；不等待外部反馈",
        "started_at": "2026-10-20T12:24:03+08:00",
        "output_dir": OD,
        "temp_dir": TD,
        "rounds_total": 3,
        "rounds_done": 1,
        "rounds": [build_round01()],
    }


def main() -> int:
    doc = json.loads(STATE.read_text(encoding="utf-8"))
    detail = [t for t in doc["tasks_detail"] if t["id"] == A]
    if detail:
        detail[0].update(build_task())
    else:
        doc["tasks_detail"].append(build_task())
    doc["current_round"] = {
        "task_id": A,
        "round": 1,
        "rounds_total": 3,
        "status": "completed",
        "next": "读取 tasks/A22-staged-data-correction/rounds/round-02.md，应用两项财务更正并重算",
        "note": "round-01 是 A22 的基线轮：未应用任何更正，6 个月原值直接计算；round-02 起 CSV 原值不改，更正只在计算层 _apply() 生效",
    }
    doc["updated_at"] = NOW
    doc["updated_at_note"] = (
        "%s 由 a22_state_r01.py 归档 A22 round-01：新增 tasks_detail 的 A22 条目"
        "（status=in_progress，rounds_done=1/3）、更新 current_round、追加 events.jsonl "
        "两条事件、保存 checkpoints/state-000058.json。A22 的 completed/pending 计数在本题"
        "三轮全部完成前保持不动；历史快照不覆盖" % NOW)
    STATE.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n",
                     encoding="utf-8")

    ev = [
        {
            "ts": NOW, "timezone": "Asia/Shanghai (UTC+08:00)",
            "event": "round_started", "task_id": A, "run_id": RUN_ID,
            "round": 1, "rounds_total": 3,
            "started_at": "2026-10-20T12:24:03+08:00",
            "note": "A22 基线轮：1600x1000 经营驾驶舱，四 KPI + 共享零起点柱图 + "
                    "六行五列表 + 仅依据实际数值的主结论",
        },
        {
            "ts": NOW, "timezone": "Asia/Shanghai (UTC+08:00)",
            "event": "round_completed", "task_id": A, "run_id": RUN_ID,
            "round": 1, "rounds_total": 3, "status": "completed",
            "output_dir": "outputs/%s/A22/round-01" % RUN_ID,
            "temp_dir": TD,
            "requests": 3, "http_requests": 5,
            "successful_requests": 2, "failed_requests": 1,
            "image_views": 10, "visual_iterations": 1,
            "dryrun_gates": "28/28", "pixel_audit": "12/12",
            "request_duration_sum_seconds": 17.923,
            "wall_clock_seconds": 8466.0,
            "deliverables": [
                "outputs/%s/A22/round-01/dashboard.png" % RUN_ID,
                "outputs/%s/A22/round-01/dashboard.snapshot" % RUN_ID,
                "outputs/%s/A22/round-01/computed-data.json" % RUN_ID,
                "outputs/%s/A22/round-01/layout-map.json" % RUN_ID,
                "outputs/%s/A22/round-01/change-audit.json" % RUN_ID,
                "outputs/%s/A22/round-01/snapshot-usage.md" % RUN_ID,
                "outputs/%s/A22/round-01/task-metrics.json" % RUN_ID,
            ],
            "detail": "A22 round-01（基线轮）完成：6 个月 2026-04→2026-09 原值计算，"
                      "净收入合计 918,624 元 / 经营利润 262,124 元 / 总订单 3,045 笔 / "
                      "总访问 27,300 次 / 总体转化率 11.15% / 总体退款率 5.79%，"
                      "期间汇总为各月先分别求和、不平均各月百分比；净收入与经营利润共用"
                      "同一比例 0.00131667 px/元与同一零线 y=852；表格 5 列×6 行 30 格"
                      "逐格与 computed-data 一致；正文最小 22 px、对比度最小 4.552。"
                      "1 次视觉迭代修掉「经营利润标签压在净收入柱上」这个真实缺陷"
                      "（2026-06 柱高被量成 113 px 应为 167 px），改为选择性直标并补两条"
                      "检查。3 条请求记录实际对应 5 个 POST（含 1 条 400 PARSE_ERROR 的 3 次"
                      "内部重试，根因 gradientBegin=\"50% 0%\"，已加离线门禁）。"
                      "8 项记录类事项已逐条披露，未补造任何日志",
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
        "reason": "A22 round-01 归档完成，进入 round-02",
        "suite_state_snapshot": dict(doc),
        "event_count": len(EVENTS.read_text(encoding="utf-8").splitlines()),
        "restore": {
            "how": "suite-state.json 允许更新，恢复时以最新 checkpoint 的 suite_state_snapshot 为准；round-02/03 的轮次文件与产物按 tasks_detail.A22.rounds 继续追加，不覆盖 round-01",
            "resume_from": "tasks/A22-staged-data-correction/rounds/round-02.md",
            "scripts": [
                "tmp/%s/_suite/gen/a22_data.py" % RUN_ID,
                "tmp/%s/_suite/gen/a22_build.py" % RUN_ID,
                "tmp/%s/_suite/gen/a22_log.py" % RUN_ID,
                "tmp/%s/_suite/gen/a22_view_footer.py" % RUN_ID,
                "tmp/%s/_suite/gen/a22_state_r01.py" % RUN_ID,
            ],
        },
    }
    cp_path.write_text(json.dumps(cp, ensure_ascii=False, indent=1) + "\n",
                       encoding="utf-8")

    print("suite-state 已更新：A22 status=in_progress，rounds_done=1/3")
    print("events.jsonl 追加 2 条，当前 %d 条" % len(EVENTS.read_text(encoding="utf-8").splitlines()))
    print("检查点 %s" % cp_path.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
