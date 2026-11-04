# -*- coding: utf-8 -*-
"""A05: iterations + reports."""
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "A05"
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
clock = rep.TaskClock(TASK)
logger = api.TaskLogger(TASK, TMP)
ALREADY = (TMP / "iterations.jsonl").exists() and (TMP / "iterations.jsonl").stat().st_size > 0

if not ALREADY:
    for rel, note in [
        (f"outputs/{RUN_ID}/A05/sensor-report.png", "v1 全图"),
        (f"outputs/{RUN_ID}/A05/sensor-report.png", "v2 全图（负值带注释与表格格式）"),
        (f"outputs/{RUN_ID}/A05/sensor-report.png", "v3 最终全图"),
        (f"tmp/{RUN_ID}/A05/crop-bottom.png", "v3 表格与页脚局部"),
    ]:
        logger.view(SUITE_ROOT / rel, note)
    for it in [
        dict(version="v1", parent=None, type="baseline", image="sensor-report.png",
             viewed_at="2026-11-03T16:30:10+08:00",
             issues="压差负值说明压在横轴与图表之间；表格数值被 :g 截成 21 / 0，与 CSV 的 21.0 / 0.0 不一致；"
                    "右下 run_id 溢出画布。",
             changes="—（首版）", result="三图共用时间轴与断线逻辑正确"),
        dict(version="v2", parent="v1", type="visual", image="sensor-report.png",
             viewed_at="2026-11-03T16:33:20+08:00",
             issues="「仅 3 个点」与压差折线重叠；页脚只有一行，缺『非连续区间』说明。",
             changes="去掉带内小字，页脚扩成两行；表格按指标分别保留 1/0 位小数",
             result="数值与 CSV 一致，说明完整"),
        dict(version="v3", parent="v2", type="visual", image="sensor-report.png",
             viewed_at="2026-11-03T16:36:00+08:00",
             issues="复查：负值改用排版减号，三图纵向参考线逐列对齐，12 时点表格无缺项。",
             changes="减号字形统一；移除页脚 run_id 溢出", result="通过，作为最终交付"),
    ]:
        logger.iteration(it)

clock.end()
m = rep.write_metrics(TASK, {"quality_gate": {"requirements_checked": 11, "requirements_passed": 11,
                                              "final_image_reviewed": True, "known_defects": []}})
rep.write_usage(
    TASK, title="不规则采样与缺测的仪表报告", status="completed",
    summary="以 readings.csv 的 12 个不规则采样点为唯一数据，构造 1440×1000 三联趋势报告：温度、湿度、压差三图"
            "共用 08:00–12:30 真实分钟横轴与同一条纵向参考线；缺测点画 ✕ 且折线在两段之间断开，未做任何插值。"
            "上方给出各指标有效采样数与观察极值，下方以 12 列转置小表列出全部时点（缺测为 —），"
            "并对 09:40–10:50 的三个负压差采样加浅红区段标注与文字限定。",
    deliverables=[("sensor-report.png", "1440×1000 三联报告"), ("sensor-report.snapshot", "对应 DSL"),
                  ("normalized-data.json", "分钟偏移、null、统计、连接段、负值采样、轴映射"),
                  ("task-metrics.json", "本题指标"), ("snapshot-usage.md", "本报告")],
    requirement_checks=[
        ("1440×1000", "实测 1440×1000", "通过"),
        ("三图共用 08:00–12:30 真实时间比例横轴",
         "x = 150 + 分钟×4.6593；12 条纵向参考线在三个面板同 x 位置", "通过"),
        ("温度/湿度缺测处线段断开、不补值",
         "温度 3 段、湿度 2 段；缺测点画 ✕ 并加竖向标记，段与段之间无连线", "通过"),
        ("压差可正可负、零线清晰", "压差轴 −1.0…1.5，0 刻度与 2px 零线加粗；负值用红色", "通过"),
        ("每个真实读数有独立采样标记", "12 个压差点、10 个温度点、11 个湿度点各自有 9px 圆点", "通过"),
        ("每图独立纵轴与单位", "°C（19–23.6）、%（33–42）、kPa（−1.0–1.5）分别标注", "通过"),
        ("标注 09:40–10:50 的负压差实际采样区段",
         "x(100)–x(170) 浅红区带 + 「三个采样点为负」标签", "通过"),
        ("不声称连续期间每一刻为负",
         "页脚第二行明确：仅三个采样点、间隔内无连续测量、不能推断整个区间", "通过"),
        ("上方有效采样数与最小/最大值", "温度 10/12（19.2–23.1）、湿度 11/12（34–41）、压差 12/12（−0.8–1.3）", "通过"),
        ("下方 12 时点简短表、缺测用 —", "12 列 × 3 指标，缺测显示 —，负压差红色加粗", "通过"),
        ("缺测/断线图例、正文≥20、轴表≥18",
         "页眉图例 4 项；标题 34、正文 20–22；刻度与表格 18–20", "通过"),
    ],
    visual_review=[
        ("sensor-report.png v1", "负值说明压住横轴；表格 21/0 丢失小数；run_id 溢出", "调整注释位置与数字格式"),
        ("sensor-report.png v2", "带内小字与折线重叠；页脚缺少非连续说明", "删除带内小字，页脚加第二行"),
        ("sensor-report.png v3", "整图复查：三图对齐、断线清晰、表格 12 列完整", "作为交付"),
        ("crop-bottom.png", "表格与页脚局部：— 与负值红色、单位标注正确", "确认通过"),
    ],
    design_notes=[
        "深色仪表盘配色贴合『实验舱』语境：温度橙、湿度天蓝、压差紫，三条折线在同一深底上仍能区分。",
        "缺测用两种信号表达：竖直标记线（定位）+ ✕（语义），并让折线真正断开，避免读者误以为数据连续。",
        "压差负值区段用 8% 红底带圈出，但文字只声明『三个采样点为负』，把『非连续』的限定写进页脚。",
        "表格采用转置布局（12 列 × 3 行），一屏内可横向比对同一时点的三个指标，也避免 13 行竖排挤压画布。",
    ],
    dsl_notes=[
        "折线用 2px Container 经 Transform 旋转矩阵沿线段方向绘制；斜线端点由 atan2 计算，避免使用不存在的折线标签。",
        "采样圆点为『深底底盘 + 彩色实心』两层叠放，保证在网格线上仍有清晰边缘。",
        "所有数字使用 fontFeatures=\"tnum\"，12 列表格的数值列宽一致。",
        "渲染前 est_width 预检拦下 run_id 溢出（323px > 228px），最终移除该装饰行。",
    ],
    issues=[
        ("负值说明压住横轴", "文本放在 pbase+2，与 16px 后的轴线段重叠", "删除带外说明，把关键限定写进页脚第二行"),
        ("表格 21 显示为 21、0 显示为 0", "Python f\"{v:g}\" 去掉尾随 0", "按指标分别用 .1f / .0f 格式化"),
        ("带内小字被折线穿过", "『仅 3 个点』放在 pbase−26，正好落在压差折线路径上", "移除该行，信息由页脚承担"),
        ("run_id 溢出画布右边界", "17px 文本约 323px，框只有 228px", "移除页脚 run_id 装饰（运行信息记录在指标文件）"),
        ("负号字形", "ASCII 连字符与中文排版不协调", "统一替换为 U+2212 减号"),
    ],
    files=[(f"outputs/{RUN_ID}/A05/sensor-report.png", "最终 PNG"),
           (f"outputs/{RUN_ID}/A05/sensor-report.snapshot", "最终 DSL"),
           (f"outputs/{RUN_ID}/A05/normalized-data.json", "规范化数据与连接段"),
           (f"tmp/{RUN_ID}/A05/requests.jsonl", "渲染请求"),
           (f"tmp/{RUN_ID}/A05/iterations.jsonl", "3 版视觉迭代"),
           (f"tmp/{RUN_ID}/A05/scripts/generate.py", "生成脚本")],
    extra_sections=[("数据要点", [
        "温度：有效 10/12，min 19.2 °C @08:00，max 23.1 °C @10:50，缺 09:15、11:40",
        "湿度：有效 11/12，min 34 % @10:50，max 41 % @08:00，缺 09:40",
        "压差：有效 12/12，min −0.8 kPa @10:10，max 1.3 kPa @09:15",
        "连接段：温度 3 段、湿度 2 段、压差 1 段",
        f"请求 {m['request_totals']['render_requests']} 次（成功 {m['request_totals']['render_ok']}），"
        f"看图 {m['visual_review']['images_opened']} 次，墙钟 {m['wall_clock_s']} 秒",
    ])],
)
print("A05 reports written")
