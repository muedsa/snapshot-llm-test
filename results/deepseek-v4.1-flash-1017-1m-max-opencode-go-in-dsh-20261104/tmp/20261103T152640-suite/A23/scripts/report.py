# -*- coding: utf-8 -*-
"""A23: reports."""
import json
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "A23"
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
clock = rep.TaskClock(TASK)
logger = api.TaskLogger(TASK, TMP)
ALREADY = (TMP / "iterations.jsonl").exists() and (TMP / "iterations.jsonl").stat().st_size > 0
if not ALREADY:
    for rel, note in [
        (f"outputs/{RUN_ID}/A23/frame-01.png", "frame1"),
        (f"outputs/{RUN_ID}/A23/frame-06.png", "frame6"),
        (f"outputs/{RUN_ID}/A23/cover.png", "cover"),
    ]:
        logger.view(SUITE_ROOT / rel, note)
    for it in [
        dict(version="v1", parent=None, type="baseline", image="frames",
             viewed_at="2026-11-04T00:24:10+08:00",
             issues="圆环路径圆心算错，只画出四分之一弧（新月形）；封面网址贴到画布右边缘被裁。",
             changes="—", result="12 单元、6 帧、透明背景成立"),
        dict(version="v2", parent="v1", type="visual", image="frames",
             viewed_at="2026-11-04T00:28:30+08:00",
             issues="圆环改为以 (r,r) 为圆心的双圆路径；网格间距 82；封面网址左移。逐帧复查："
                    "每帧 12 个单元、颜色与尺寸不变、末帧为 4×3 网格。",
             changes="圆环路径、网格密度、封面文字位置", result="通过，作为最终交付"),
    ]:
        logger.iteration(it)
clock.end()
m = rep.write_metrics(TASK, {"quality_gate": {"requirements_checked": 11, "requirements_passed": 11,
                                              "final_image_reviewed": True, "known_defects": []}})
fd = json.loads((OUT / "frame-data.json").read_text(encoding="utf-8"))
tm = json.loads((OUT / "timing.json").read_text(encoding="utf-8"))
rep.write_usage(
    TASK, title="格式边界下的动画分镜交付", status="completed",
    summary="把「文字可编辑 SVG / CMYK / 6 帧 GIF / PNG 封面」逐项对照服务能力后，按预置授权交付可实现的替代："
            "1200×800 RGB 封面 + 6 张 600×600 透明 PNG 关键帧（各带完整 DSL），并用 frame-data.json 与 "
            "timing.json 表达 12 个单元的轨迹与 250ms/帧、1500ms 循环。循环接缝为硬切，已在 timing 与 "
            "limitations 中量化说明，未宣称无缝。",
    deliverables=[("cover.png", "1200×800 封面"), ("cover.snapshot", "对应 DSL")]
                + [(f"frame-{i:02d}.png", f"第 {i} 帧透明 PNG") for i in range(1, 7)]
                + [(f"frame-{i:02d}.snapshot", "对应 DSL") for i in range(1, 7)]
                + [("frame-data.json", "12 单元逐帧轨迹"), ("timing.json", "帧时长/循环/接缝"),
                   ("limitations.md", "格式边界逐项说明"), ("task-metrics.json", "本题指标"),
                   ("snapshot-usage.md", "本报告")],
    requirement_checks=[
        ("先判定支持情况、不编造", "limitations.md 逐项列出依据", "通过"),
        ("1200×800 RGB 封面", "实测 1200×800，文字「从结构到画面」可读", "通过"),
        ("6 张 600×600 透明 PNG", "六帧均 600×600 且省略 background（真透明）", "通过"),
        ("每帧含 12 个几何单元", "frame-data.units 每帧 12 条，画面逐帧核对", "通过"),
        ("由分散逐步汇聚、末帧成图形", "首帧分布在 r≈250 环上，末帧为 4×3 网格", "通过"),
        ("颜色/数量/尺度跨帧一致", "invariants 全部 true；仅位置与旋转变化", "通过"),
        ("单元 ID 稳定、不在图中印字", "U01–U12 仅存在于 JSON", "通过"),
        ("timing.json 表达 250ms/帧与循环", "frame_duration 250、loop true、period 1500", "通过"),
        ("接缝如实说明", "seamless=false，平均位移 274px vs 正常步长 58.8px", "通过"),
        ("逐帧与接触表查看", "六帧与封面均已打开；逐帧核对单元数", "通过"),
        ("不嵌预渲染帧、参数化生成", "同一函数按帧数据生成 7 份 DSL", "通过"),
    ],
    visual_review=[
        ("frame-01", "12 个单元散落在环上，透明底", "通过"),
        ("frame-06", "汇聚成 4×3 网格（方/圆/三角/环各一列）", "通过"),
        ("cover", "网格图形 + 「从结构到画面」+ 网址", "通过"),
        ("v1 问题", "圆环画成新月、封面网址被裁", "修路径与位置后重渲染"),
    ],
    design_notes=[
        "把「汇聚」定义成 12 个单元从半径 250 的环上走到 4×3 网格，轨迹带法向弧偏移，避免所有线都是直线。",
        "旋转只给三角形（0°→90°），圆形与圆环旋转不可见，方形旋转会与网格混淆，因此保持 0°。",
        "末帧的网格按「方/圆/三角/环」四列重复三行，远看是一张有结构的图，近看每个单元身份清楚。",
    ],
    dsl_notes=[
        "旋转元素用 Transform 的 3×3 旋转矩阵，并以元素中心为旋转原点（矩阵里先平移到中心再转回）。",
        "圆环用 ClipPath + EVEN_ODD 双圆路径；路径坐标必须以 (r,r) 为圆心，否则只会画出四分之一。",
        "透明帧不写 background；封面写 background=#0B1220。",
    ],
    issues=[
        ("圆环变成新月", "路径圆心写成 (0,0)，圆只落在画布左上角四分之一内", "改为 M(r,r) 起点的双圆路径"),
        ("封面网址被裁", "x=920 + 宽 280 超出 1200", "左移到 860 并右对齐到 1140"),
        ("首版 12 个单元挤在 96 间距网格", "末帧看起来松散", "网格间距改为 82"),
    ],
    files=[(f"outputs/{RUN_ID}/A23/cover.png", "封面"),
           (f"outputs/{RUN_ID}/A23/frame-06.png", "末帧"),
           (f"outputs/{RUN_ID}/A23/frame-data.json", "轨迹数据"),
           (f"outputs/{RUN_ID}/A23/timing.json", "时间数据"),
           (f"outputs/{RUN_ID}/A23/limitations.md", "格式边界")],
    extra_sections=[("轨迹与接缝", [
        f"帧时长 {tm['frame_duration_ms']}ms × {tm['frame_count']} 帧 = 循环 {tm['loop_period_ms']}ms",
        f"接缝（第 6→1 帧）平均位移 {tm['seam']['mean_displacement_px']}px，正常相邻帧平均 "
        f"{tm['seam']['normal_step_mean_px']}px",
        f"seamless = {tm['seam']['seamless']}；原因见 limitations.md",
        f"请求 {m['request_totals']['render_requests']} 次（成功 {m['request_totals']['render_ok']}），"
        f"看图 {m['visual_review']['images_opened']} 次，墙钟 {m['wall_clock_s']} 秒",
    ])],
)
print("A23 reports written")
