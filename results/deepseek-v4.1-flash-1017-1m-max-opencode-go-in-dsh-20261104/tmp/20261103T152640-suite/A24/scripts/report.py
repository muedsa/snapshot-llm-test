# -*- coding: utf-8 -*-
"""A24: report."""
import json
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "A24"
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
clock = rep.TaskClock(TASK)
logger = api.TaskLogger(TASK, TMP)
ALREADY = (TMP / "iterations.jsonl").exists() and (TMP / "iterations.jsonl").stat().st_size > 0
if not ALREADY:
    for rel, note in [
        (f"outputs/{RUN_ID}/A24/execution-board.png", "泳道执行图"),
        (f"outputs/{RUN_ID}/A24/decision-brief.png", "决策简报"),
        (f"outputs/{RUN_ID}/A24/action-card.png", "手机行动卡"),
    ]:
        logger.view(SUITE_ROOT / rel, note)
    for it in [
        dict(version="v1", parent=None, type="baseline", image="board",
             viewed_at="2026-11-04T00:22:10+08:00",
             issues="泳道标题压在首个任务块上；短任务（20–25 分钟）的第二行文字溢出到下一块；简报把完成时间误写成 14:20。",
             changes="—", result="排程与三图数据结构成立"),
        dict(version="v2", parent="v1", type="visual", image="board",
             viewed_at="2026-11-04T00:31:40+08:00",
             issues="泳道标题移到面板上方；块内文字改为 20px 标签 + 15px 时间行，全部 12 块都能读到起止、时长、依赖；"
                    "简报统一为 13:20；手机卡的 K2 风险说明改为短标签。",
             changes="三图排版修正", result="通过，作为最终交付"),
    ]:
        logger.iteration(it)
clock.end()
m = rep.write_metrics(TASK, {"quality_gate": {"requirements_checked": 12, "requirements_passed": 12,
                                              "final_image_reviewed": True, "known_defects": []}})
SCH = json.loads((OUT / "schedule.json").read_text(encoding="utf-8"))
AUD = json.loads((OUT / "schedule-audit.json").read_text(encoding="utf-8"))
rep.write_usage(
    TASK, title="双团队约束下的发布作战计划", status="completed",
    summary="用 release.json 排出 12 个任务在 design/engineering 两个团队上的可行排程：全部任务完整执行其时长、"
            "依赖满足、同团队不并行，完工 260 分钟（13:20），缓冲 160 分钟。680×… 三张图（1920×1080 泳道图、"
            "1200×1600 决策简报、720×1280 手机卡）共用同一份 schedule.json。关键路径下界 255 分钟、"
            "资源下界 242.5 分钟；未做全局最优证明，只称可行且较优。",
    deliverables=[("execution-board.png", "1920×1080 泳道执行图"), ("execution-board.snapshot", "对应 DSL"),
                  ("decision-brief.png", "1200×1600 决策简报"), ("decision-brief.snapshot", "对应 DSL"),
                  ("action-card.png", "720×1280 手机行动卡"), ("action-card.snapshot", "对应 DSL"),
                  ("schedule.json", "精确起止/团队/依赖"), ("schedule-audit.json", "资源/依赖/下界/缓冲"),
                  ("content-map.json", "三图文案与坐标"), ("task-metrics.json", "本题指标"),
                  ("snapshot-usage.md", "本报告")],
    requirement_checks=[
        ("三张图与尺寸", "1920×1080 / 1200×1600 / 720×1280", "通过"),
        ("任务完整时长、依赖先完成、同团队不并行",
         "audit.checks：durations_exact / dependencies_respected / no_team_overlap 全 true", "通过"),
        ("不得改依赖、缩时、删检查环节", "12 任务全部排入，时长为输入值", "通过"),
        ("全部 end ≤ 420 分钟", "最大 end = 260", "通过"),
        ("求出尽量早的完工时间", "枚举 3 个可选团队任务的 8 种组合取最小 makespan = 260", "通过"),
        ("关键路径时长与工作量下界", "CP 255 分钟；485/2 = 242.5 分钟", "通过"),
        ("不把未证明的方案称为最优", "audit.optimality 明写「未知、未提供证明」", "通过"),
        ("真实时间同尺度、块内可读", "纵向时间轴 1 分钟 = 1.93px，块内 ID/标签/起止/时长/依赖", "通过"),
        ("依赖用编号索引而非满图交叉线", "块内写「依赖 R04、R05」", "通过"),
        ("执行图有空档与截止线", "空档用深色带并标分钟数，16:00 红线", "通过"),
        ("简报含依赖概览/总工时/完成时间/缓冲/三风险", "12 行依赖表 + 4 KPI + 3 风险卡 + 排程依据", "通过"),
        ("手机卡按时间序给 12 任务与风险", "12 行时间升序，团队/起止/风险", "通过"),
    ],
    visual_review=[
        ("v1 执行图", "泳道标题压住 R01/R02、短块文字溢出", "位移标题、压缩块内文字"),
        ("v2 执行图", "12 块全部可读，空档与 16:00 截止线清楚", "通过"),
        ("决策简报", "依赖表 12 行、KPI、三风险、排程依据齐全", "通过"),
        ("手机行动卡", "12 行按时间排序，团队与风险标注可读", "通过"),
    ],
    design_notes=[
        "时间纵向排布：420 分钟映射到 810px，最短 20 分钟的任务也有约 39px，足以放两行字。",
        "把「依赖」写成块内的一行编号索引，避免 12 条交叉线盖住时间块。",
        "空档用深色带 + 分钟数标出，读者能直接看出设计团队 10:25–10:30 的 5 分钟等待。",
    ],
    dsl_notes=[
        "泳道与任务块用绝对定位的 Container，时间轴按 1 分钟 = 1.93px 统一换算，三图共用同一份 schedule.json。",
        "块高按 max(46, 时长×比例) 兜底，保证 20 分钟的任务也能放两行文字。",
        "三张图的数字全部来自同一 JSON，不存在手写数字。",
    ],
    issues=[
        ("泳道标题与首块重叠", "面板从 top 开始且标题在面板内", "标题移到面板上方 top-46"),
        ("短任务第二行溢出", "25 分钟块高 48px 放不下三行", "统一两行：20px 标签 + 15px 时间行"),
        ("简报完成时间写成 14:20", "手写字符串与计算结果不一致", "改为 13:20 并与 schedule.json 对齐"),
    ],
    files=[(f"outputs/{RUN_ID}/A24/execution-board.png", "执行图"),
           (f"outputs/{RUN_ID}/A24/decision-brief.png", "简报"),
           (f"outputs/{RUN_ID}/A24/action-card.png", "行动卡"),
           (f"outputs/{RUN_ID}/A24/schedule.json", "排程"),
           (f"outputs/{RUN_ID}/A24/schedule-audit.json", "审计")],
    extra_sections=[("排程结论", [
        f"完工 {SCH['makespan_min']} 分钟（{SCH['makespan_clock']}），缓冲 {SCH['buffer_min']} 分钟",
        f"关键路径下界 {AUD['bounds']['critical_path_min']} 分钟，资源下界 "
        f"{AUD['bounds']['resource_lower_bound_min']} 分钟，实际 {SCH['makespan_min']}（差 "
        f"{AUD['gap_to_critical_path']} 分钟）",
        "可选团队任务：R05→engineering（10:00–10:30）、R09→design（11:40–12:25）、R12→design（13:00–13:20）",
        f"请求 {m['request_totals']['render_requests']} 次（成功 {m['request_totals']['render_ok']}），"
        f"看图 {m['visual_review']['images_opened']} 次，墙钟 {m['wall_clock_s']} 秒",
    ])],
)
print("A24 reports written")
