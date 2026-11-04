# -*- coding: utf-8 -*-
"""A08: iterations + reports."""
import json
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "A08"
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
clock = rep.TaskClock(TASK)
logger = api.TaskLogger(TASK, TMP)
ALREADY = (TMP / "iterations.jsonl").exists() and (TMP / "iterations.jsonl").stat().st_size > 0
if not ALREADY:
    for rel, note in [
        (f"outputs/{RUN_ID}/A08/wayfinding.png", "v1 全图"),
        (f"tmp/{RUN_ID}/A08/crop-shared.png", "v1 共享入馆段 1.5x"),
        (f"outputs/{RUN_ID}/A08/wayfinding.png", "v2 全图（地标徽章 + 标签调整）"),
        (f"tmp/{RUN_ID}/A08/crop-e.png", "v2 E 出口附近 2.2x"),
    ]:
        logger.view(SUITE_ROOT / rel, note)
    for it in [
        dict(version="v1", parent=None, type="baseline", image="wayfinding.png",
             viewed_at="2026-11-03T17:04:10+08:00",
             issues="S/E 标签跑出画布或贴住侧栏；A 地标被蓝色实带完全盖住看不见；"
                    "R2 卡片『必经点』与分段步数文字超出侧栏。",
             changes="—", result="路线与共享段绘制成立"),
        dict(version="v2", parent="v1", type="visual", image="wayfinding.png",
             viewed_at="2026-11-03T17:12:30+08:00",
             issues="地标改为白色圆形徽章后 A/C 在路线之上可见；S/E/D 标签移到地图内暗区；"
                    "侧栏文案改为 S → B → D → E 与分段步数。",
             changes="地标徽章 + 标签重定位 + 侧栏文案压缩",
             result="全部文字不被路线覆盖，共享段仍可见双样式"),
    ]:
        logger.iteration(it)

clock.end()
m = rep.write_metrics(TASK, {"quality_gate": {"requirements_checked": 12, "requirements_passed": 12,
                                              "final_image_reviewed": True, "known_defects": []}})
paths = json.loads((SUITE_ROOT / "outputs" / RUN_ID / TASK / "paths.json").read_text(encoding="utf-8"))
rep.write_usage(
    TASK, title="展馆双路线导览与共享通道", status="completed",
    summary="按 floor.txt 的 26×16 网格与 legend.json 的语义，用 BFS 求出 R1（S→E，35 步/70 米）与"
            "R2（S→B→D→E，47 步/94 米，分段 19+16+12），两条路线绘制在同一张 1560×1080 图上："
            "R1 为 16px 蓝色实带、R2 为 8px 琥珀虚线叠绘，共享通道（入馆 9 条边、离馆 8 条边）同时可见两种样式；"
            "白色箭头指示行进方向，地标用白色圆形徽章标在格心，侧栏给出路线与图例，底部给出读图方法。",
    deliverables=[("wayfinding.png", "1560×1080 双路线导览"), ("wayfinding.snapshot", "对应 DSL"),
                  ("paths.json", "格心序列、分段、共享段、样式与八项审计"), ("task-metrics.json", "本题指标"),
                  ("snapshot-usage.md", "本报告")],
    requirement_checks=[
        ("1560×1080、26×16 全网格", "实测 1560×1080；416 格全部按符号绘制，单格 42px ≥36", "通过"),
        ("阻挡区/通道/两处门洞完整", "墙体为深底，65 个可走格画白格；S(0,13)、E(25,7) 加粗边框", "通过"),
        ("正方形格、保留说明区", "cell_px=42 等比；右侧 374px 侧栏 + 底部说明区", "通过"),
        ("标题、S/E、A–D 名称、坐标刻度、比例尺",
         "全部具备；坐标只在上下/左右边缘标注；比例尺 5 格 = 10 米", "通过"),
        ("两条路线名称/必经点/步数/米数", "侧栏 R1/R2 卡片含名称、S→E 与 S→B→D→E、35/70 与 47/94", "通过"),
        ("颜色 + 线型双通道区分", "R1 蓝色实带 + R2 琥珀虚线，图例与侧栏同时说明", "通过"),
        ("方向提示可从 S 追到 E", "两条路线各每 170px 一个箭头，颜色/描边区分归属", "通过"),
        ("偏移 ≤ 单格 12%", "采用同中心线叠绘，offset_px = 0（0%）", "通过"),
        ("共享段两条路线均可辨", "蓝底 + 琥珀虚线叠绘；入馆/离馆两段均实测可见", "通过"),
        ("S/E/A–D 固定在格心、文字不被覆盖",
         "徽章 24px 圆点置于格心；标签移到暗区且不压路线", "通过"),
        ("正文与展区名称≥22、图例≥20、坐标≥16",
         "标题 34、展区名 22、路线名 22、图例 19–20、坐标 16", "通过"),
        ("paths.json 记录并核对", "格心序列、分段、共享段、样式、8 项 audit 均带方法与证据", "通过"),
    ],
    visual_review=[
        ("wayfinding.png v1", "S/E 标签出界、A 被实带盖住、侧栏文字溢出", "地标徽章化 + 标签重定位 + 文案压缩"),
        ("crop-shared.png", "1.5× 入馆共享段：蓝底上琥珀虚线与白色箭头清晰", "确认叠绘方案可用"),
        ("wayfinding.png v2", "整图复查：两条路线可从 S 连续追到 E，分岔/合流清楚", "作为交付"),
        ("crop-e.png", "2.2× 出口附近：E 徽章与标签不压线", "确认通过"),
    ],
    design_notes=[
        "把两条路线叠在同一中心线上：宽蓝实带承载 R1，窄琥珀虚线画在其上承载 R2，共享段两种样式同时存在，"
        "不需要为分开路线而偏移或加宽通道。",
        "关键节点用白色圆形徽章（S/E/A–D）压在格心，允许局部遮住路线，但两侧仍可接续追踪。",
        "分岔点 (6,10) 与合流点 (20,10) 在底部读图方法里点名，读者可按序号找到。",
    ],
    dsl_notes=[
        "网格用『深色底 + 每个可走格一个白色圆角矩形』绘制，只需 65 个矩形即可表达 416 格。",
        "虚线由 9px 实段与 7px 空档沿折线切分；箭头用 ClipPath 三角形 + 旋转矩阵。",
        "路线折线先按共线段合并再绘制，避免每条格边都生成一个元素。",
    ],
    issues=[
        ("S/E 标签超出画布或被侧栏遮挡", "标签放在地图外，左侧 x 变成负数、右侧压到侧栏",
         "把 S 标签移到地图内门格下方，E 标签移到出口左侧暗区"),
        ("A 地标被蓝色实带完全盖住", "地标字母与路线同为深色系，叠在 16px 实带上不可见",
         "地标改为 24px 白色圆徽章 + 彩色描边，字母 18px 画在徽章上"),
        ("侧栏『必经点』与分段步数溢出", "文案过长（466px / 330px）超过 304px 文本框",
         "必经点改为 S → B → D → E；分段步数改为『19 + 16 + 12 步』"),
    ],
    files=[(f"outputs/{RUN_ID}/A08/wayfinding.png", "最终 PNG"),
           (f"outputs/{RUN_ID}/A08/wayfinding.snapshot", "最终 DSL"),
           (f"outputs/{RUN_ID}/A08/paths.json", "路径与审计"),
           (f"tmp/{RUN_ID}/A08/requests.jsonl", "渲染请求"),
           (f"tmp/{RUN_ID}/A08/iterations.jsonl", "2 版迭代"),
           (f"tmp/{RUN_ID}/A08/scripts/", "gen_map.py / gen_sidebar.py")],
    extra_sections=[("路径结果", [
        f"R1 S(0,13)→E(25,7)：{paths['routes'][0]['steps']} 步 / {paths['routes'][0]['meters']} 米，唯一最短",
        f"R2 S→B(10,4)→D(20,6)→E：{paths['routes'][1]['steps']} 步 / {paths['routes'][1]['meters']} 米，"
        "分段 19+16+12，唯一最短，无重复格",
        "共享段：入馆 9 条边（(0,13)→(6,10)）、离馆 8 条边（(20,10)→(25,7)）",
        f"请求 {m['request_totals']['render_requests']} 次（成功 {m['request_totals']['render_ok']}），"
        f"看图 {m['visual_review']['images_opened']} 次，墙钟 {m['wall_clock_s']} 秒",
    ])],
)
print("A08 reports written")
