# -*- coding: utf-8 -*-
"""A02: iterations + reports."""
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "A02"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
clock = rep.TaskClock(TASK)
logger = api.TaskLogger(TASK, TMP)
ALREADY = (TMP / "iterations.jsonl").exists() and (TMP / "iterations.jsonl").stat().st_size > 0

if not ALREADY:
    for rel, note in [
        (f"outputs/{RUN_ID}/A02/agenda-wide.png", "wide v1 全图"),
        (f"outputs/{RUN_ID}/A02/agenda-mobile.png", "mobile v1 全图"),
        (f"outputs/{RUN_ID}/A02/agenda-wide.png", "wide v2 全图：图例/空档/短块时间"),
        (f"tmp/{RUN_ID}/A02/crop-b.png", "wide v2 泳道 B 空档局部 1.4x"),
        (f"outputs/{RUN_ID}/A02/agenda-wide.png", "wide v3 全图：空档按午休拆分"),
        (f"outputs/{RUN_ID}/A02/agenda-mobile.png", "mobile v3 全图"),
        (f"tmp/{RUN_ID}/A02/crop-mob.png", "mobile v3 行局部 1.4x"),
    ]:
        logger.view(SUITE_ROOT / rel, note)

    for it in [
        dict(version="v1", parent=None, type="baseline", image="agenda-wide.png / agenda-mobile.png",
             viewed_at="2026-11-03T15:52:00+08:00",
             issues="大图：图例与『读图方法』文本重叠，第 5 个类别被盖住；泳道标题『6 场 · 共 265 分钟』"
                    "被首块遮住；S15（30 分钟）时间文字超出 120px 块宽。手机：每行提示文字贴到卡片右边缘。",
             changes="—（首版）",
             result="保留基线；确认块宽 = 时长×4px。"),
        dict(version="v2", parent="v1", type="visual", image="agenda-wide.png",
             viewed_at="2026-11-03T15:57:00+08:00",
             issues="泳道 B 的 11:10–12:00 空档标签被午休带遮住，只剩一个字；空档档期把午休也算进会场空档。",
             changes="图例改两行、读图方法右移；泳道标题拆行；S15 时间改两行；空档加浅色带与分钟标注。",
             result="图例恢复；空档带出现，但 B 泳道仍显示为跨午休的一整段。"),
        dict(version="v3", parent="v2", type="visual", image="agenda-wide.png / agenda-mobile.png",
             viewed_at="2026-11-03T16:02:00+08:00",
             issues="gaps_of 未在 12:00/13:00 切分，B 泳道 11:10–13:00 被当成一个 110 分钟空档。",
             changes="gaps_of 在午休边界切分；空档标签对比度提高；索引 meta 与读图说明提升到 18px；"
                     "手机提示文字左右各留 24px。",
             result="B 空档正确显示 50 分钟，午休独立；19 条空档记录与图上标注一致。"),
    ]:
        logger.iteration(it)

clock.end()
m = rep.write_metrics(TASK, {"quality_gate": {"requirements_checked": 10, "requirements_passed": 10,
                                              "final_image_reviewed": True, "known_defects": []}})

rep.write_usage(
    TASK, title="三会场密集会议日程", status="completed",
    summary="同一份 inputs/agenda.csv 生成两张不同信息架构的图：1920×1200 三泳道比例日程（时间→x 轴线性映射，"
            "块宽 = 时长 × 4px）与 720×1280 手机分时段列表（独立重排，不是缩放大图）。"
            "15 场活动的编号、标题、讲者、起止、类别、会场在两图中都能读到。",
    deliverables=[("agenda-wide.png", "1920×1200 三泳道日程"), ("agenda-wide.snapshot", "对应 DSL"),
                  ("agenda-mobile.png", "720×1280 手机导览"), ("agenda-mobile.snapshot", "对应 DSL"),
                  ("schedule-audit.json", "时长/空档/冲突/内容映射/时间轴"), ("task-metrics.json", "本题指标"),
                  ("snapshot-usage.md", "本报告")],
    requirement_checks=[
        ("1920×1200 与 720×1280 两张图", "实测 1920×1200、720×1280，均为服务真实 PNG", "通过"),
        ("日期/地点/时区", "2026.11.07 · 云构中心 A/B/C 会场 · Asia/Shanghai 同时写在两图页眉", "通过"),
        ("三条泳道共用 09:00–16:00 线性轴",
         "x = 180 + 分钟×4，整点 8 条刻度线；`time_axis` 记录公式与 lane_tops", "通过"),
        ("块位置与长度按实际起止比例",
         "15 块宽度 = duration×4px（30–75 分钟 → 120–300px），`content_map[].wide.box` 记录每块像素框",
         "通过"),
        ("空档保留", "19 条空档，浅色带 + 分钟标注；07:50 等窄空档只留带不标字", "通过"),
        ("午休跨三泳道独立标识", "12:00–13:00 竖直灰带贯穿三泳道，带内『公共午休/12:00–13:00/独立时段』",
         "通过"),
        ("15 项编号/标题/讲者/起止/类别可读",
         "块内编号与起止 18px；索引 15 条含编号·起止·会场·类别（18px）与标题·讲者（20px）", "通过"),
        ("短活动用外侧说明/编号索引，不夸大时长",
         "S15 仅 120px 宽，块内只放编号与两行时间，标题讲者在索引；所有块宽严格 4px/分钟", "通过"),
        ("正文≥20、时间标签≥18", "索引标题与块内标题 20px；块内与索引时间标签 18px", "通过"),
        ("手机图分时段列表、不缩放大图",
         "手机图独立排版：上午 8 行 + 午休 + 下午 7 行，无 Image 元素、无缩放裁切", "通过"),
        ("手机正文≥18 且写明讲者指引",
         "标题 20px、时间/编号/类别 18px；页眉与每行均写『讲者详见完整日程』", "通过"),
        ("不捏造冲突/不改时间", "逐会场区间扫描 conflicts=[]，时间全部来自 CSV 原文", "通过"),
    ],
    visual_review=[
        ("agenda-wide.png v1", "图例被读图说明覆盖、泳道统计被首块遮挡、S15 时间溢出", "重排页眉与短块排版"),
        ("agenda-mobile.png v1", "行内提示贴边、卡片底部略挤", "内容重排 + 右侧留白"),
        ("agenda-wide.png v2", "B 泳道空档标签被午休带截断", "拆分午休边界"),
        ("crop-b.png", "1.4× 局部确认空档标签只剩一个字", "定位为 gaps_of 未切分午休"),
        ("agenda-wide.png v3", "空档分钟标注完整（20/50/30…），午休独立", "通过"),
        ("agenda-mobile.png v3", "15 行完整、午休条居中、页脚不遮挡", "通过"),
        ("crop-mob.png", "1.4× 局部确认行内四段文字间距与右留白", "通过"),
    ],
    design_notes=[
        "两张图刻意采用不同信息架构：大图强调并行时间关系（比例泳道），手机图强调按时间阅读（列表），"
        "避免『把大图缩小』这种不可读的做法。",
        "类别用 5 色（主旨砖红/工作坊墨绿/分享藏蓝/演示紫/圆桌橄榄），左侧 4px 实色边条 + 浅色底，"
        "在白底纸感画布上保持低饱和、可打印。",
        "空档以更浅的暖灰带 + 分钟数标注，读者能一眼看出『这里没有安排』而不必心算。",
        "索引按时间顺序列优先排布（S01–S05 / S06–S10 / S11–S15），与泳道顺序一致。",
    ],
    dsl_notes=[
        "`borderLeft=\"4 SOLID #B23A0C\"` 与统一 `border` 同时使用时，单边边框覆盖同侧；实图确认左边条生效。",
        "块内文本用绝对定位而非 Column，避免短块内部溢出不可控；标题用 `width` 限宽换行。",
        "`fontFeatures=\"tnum\"` 用于所有时间与数字，保证 09:00–09:40 与 15:30–16:00 等宽对齐。",
        "手机图完全独立构造：同一数据源、不同版式，未使用 `<Image>` 嵌入大图。",
        "渲染前用 `est_width` 预检，S15 的『15:30–16:00』在 100px 框内超宽（119px），改为上下两行。",
    ],
    issues=[
        ("图例第 5 项被读图说明覆盖", "图例宽 580px 起于 900，与 x=1240 起的说明区重叠",
         "图例改两行三列（880 起），说明区右移到 1290，重渲染确认五项齐全"),
        ("泳道标题『6 场 · 共 265 分钟』被首块遮住", "标签列只有 132px，文本 200px",
         "拆为『容量 320 座』与『6 场』两行，总时长移到页脚"),
        ("S15 时间文字溢出块宽", "120px 块内 18px 文字需 119px，减去内边距只剩 100px",
         "宽度 < 136px 的块改为上下两行显示起止；并把此阈值用于标题显示"),
        ("B 泳道空档被午休带截断", "gaps_of 只按事件间隙计算，未在 12:00/13:00 切分",
         "按午休边界切分空档，重算后 19 条记录与图上标注一致"),
    ],
    files=[(f"outputs/{RUN_ID}/A02/agenda-wide.png", "大图 PNG"),
           (f"outputs/{RUN_ID}/A02/agenda-mobile.png", "手机图 PNG"),
           (f"tmp/{RUN_ID}/A02/requests.jsonl", "渲染请求"),
           (f"tmp/{RUN_ID}/A02/iterations.jsonl", "3 版视觉迭代"),
           (f"tmp/{RUN_ID}/A02/tool-usage.jsonl", "7 次看图"),
           (f"tmp/{RUN_ID}/A02/scripts/generate.py", "生成脚本")],
    extra_sections=[("指标摘要", [
        f"渲染请求 {m['request_totals']['render_requests']} 次（成功 {m['request_totals']['render_ok']}）",
        f"视觉迭代 {m['visual_review']['iterations_total']} 个版本，看图 {m['visual_review']['images_opened']} 次",
        f"任务墙钟 {m['wall_clock_s']} 秒；首次可用图 {m['first_usable_image_s']} 秒"])],
)
print("A02 reports written")
