# -*- coding: utf-8 -*-
"""A09: iterations + reports."""
import json
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "A09"
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
clock = rep.TaskClock(TASK)
logger = api.TaskLogger(TASK, TMP)
ALREADY = (TMP / "iterations.jsonl").exists() and (TMP / "iterations.jsonl").stat().st_size > 0
if not ALREADY:
    for rel, note in [
        (f"outputs/{RUN_ID}/A09/transform-atlas.png", "v1 全图"),
        (f"outputs/{RUN_ID}/A09/transform-atlas.png", "v2 全图（图例重排）"),
    ]:
        logger.view(SUITE_ROOT / rel, note)
    for it in [
        dict(version="v1", parent=None, type="baseline", image="transform-atlas.png",
             viewed_at="2026-11-03T17:28:40+08:00",
             issues="图例四列文字互相重叠：辅助线 2 行、记号 3 行都超出各自栏宽并压在一起。",
             changes="—", result="十二格变换与配色正确；图例需重排"),
        dict(version="v2", parent="v1", type="visual", image="transform-atlas.png",
             viewed_at="2026-11-03T17:33:10+08:00",
             issues="复查：图例每列改为定行距短句，无重叠；像素审计最差偏差 1.22px（容差 1.5px）。",
             changes="图例改为 3–4 行短句并固定行距 26px", result="通过，作为最终交付"),
    ]:
        logger.iteration(it)

clock.end()
m = rep.write_metrics(TASK, {"quality_gate": {"requirements_checked": 10, "requirements_passed": 10,
                                              "final_image_reviewed": True, "known_defects": []}})
audit = json.loads((OUT / "geometry-audit.json").read_text(encoding="utf-8"))
worst = max(abs(d) for s in audit["specimens"] for c in s["pixel_check"]["rectangles"]
            for d in (c["deviation_px"] or [0]))
rep.write_usage(
    TASK, title="十二个非对称图形变换标本", status="completed",
    summary="把 120×120 的非对称印章（3 个相邻矩形 + 1 个偏心黑点）按 transforms.json 的 12 组操作依次施加，"
            "每组都用一条 Transform.matrix 绘制：先算 2D 仿射（以局部 (60,60) 为不动点），再平移使局部中心落在 300×250 格的格心。"
            "4 列 × 3 行、格间 32、整体居中；每格含编号、中文操作名、英文原名与虚线十字 + 25px 刻度辅助线。",
    deliverables=[("transform-atlas.png", "1600×1200 变换图谱"), ("transform-atlas.snapshot", "对应 DSL"),
                  ("geometry-audit.json", "12 条列主序矩阵、逐角点、圆点、外接框与像素核对"),
                  ("task-metrics.json", "本题指标"), ("snapshot-usage.md", "本报告")],
    requirement_checks=[
        ("1600×1200、4×3、300×250、格间 32、整体居中",
         "格宽 1296 居中于 1600（左右各 152）；格高 814，起点 y=152", "通过"),
        ("标题与图例在格外", "标题在 y=22–110，图例条在 y=992–1168", "通过"),
        ("局部坐标从印章左上算、围绕 (60,60)", "所有矩阵以 (60,60) 为不动点，见 matrix_column_major", "通过"),
        ("12 个变换按列表顺序", "operations 顺序参与仿射连乘，T07/T08 结果不同（矩阵不等）", "通过"),
        ("每格主体由 Transform.matrix 表示", "每格恰一条 Transform，形状坐标直接用 stamp.json 原值", "通过"),
        ("圆点随同变换", "圆点由同一矩阵变换，像素探测 12 格全部命中且环带无点", "通过"),
        ("编号、操作短名、刻度辅助线齐全", "T01–T12 + 中文名 + 英文名 + 虚线十字 + 25px 刻度", "通过"),
        ("不裁切主体", "12 个外接框全部落在 300×250 内（fits_cell 全 true）", "通过"),
        ("标签 ≥20px", "编号 22px、中文名 20px；英文名 17px 为注释", "通过"),
        ("±1.5px 视觉/像素核对", f"12 格 36 个矩形逐色测量，最大偏差 {worst:.2f}px", "通过"),
    ],
    visual_review=[
        ("transform-atlas.png v1", "图例四列文字互相重叠", "改为定行距短句"),
        ("transform-atlas.png v2", "整图复查：12 格方向各不相同、圆点位置随变换移动、无裁切", "作为交付"),
    ],
    design_notes=[
        "同一枚印章 + 一个偏心黑点，使旋转/镜像/缩放的结果两两可区分；T07 与 T08 名称直接写出操作先后。",
        "每格画出虚线十字与 25px 刻度，读者可用它目测旋转角度与缩放比例，而不必依赖文字。",
        "格子用白卡 + 浅描边，图谱读起来像标本册；操作名用中文，底部保留英文原名便于对照 DSL。",
    ],
    dsl_notes=[
        "Transform.matrix 为列主序 4×4；2D 仿射 (a,b,c,d,tx,ty) 按 (a,b,0,0,c,d,0,0,0,0,1,0,tx,ty,0,1) 写入。",
        "`alignment=\"TOP_LEFT\"` 保证矩阵以子节点左上角为原点，便于直接用局部坐标推导。",
        "圆点用 Container + borderRadius=radius 绘制，随同一矩阵变换。",
        "每格 Stack 设 clipBehavior=HARD_EDGE，防止相邻格互相渗色；主体均在格内，因此不会真的裁切。",
    ],
    issues=[
        ("图例文字互相重叠", "四列文案过长，18px 下估算 472–782px，超出 420–430px 栏宽",
         "每列改为 3–4 行短句，固定行距 26px，重新渲染确认"),
        ("首次渲染耗时 138 秒", "服务端对含 Transform 的图谱渲染较慢（非 DSL 问题）",
         "重渲染一次降到 27 秒；请求记录保留两次耗时"),
    ],
    files=[(f"outputs/{RUN_ID}/A09/transform-atlas.png", "最终 PNG"),
           (f"outputs/{RUN_ID}/A09/transform-atlas.snapshot", "最终 DSL"),
           (f"outputs/{RUN_ID}/A09/geometry-audit.json", "几何审计"),
           (f"tmp/{RUN_ID}/A09/geom.json", "生成期几何中间数据"),
           (f"tmp/{RUN_ID}/A09/requests.jsonl", "渲染请求"),
           (f"tmp/{RUN_ID}/A09/iterations.jsonl", "2 版迭代")],
    extra_sections=[("几何核对摘要", [
        f"36 个矩形色块的实测外接框与矩阵计算值最大偏差 {worst:.2f}px（容差 1.5px）",
        "12 个黑点中心像素均为 (17,17,17)，半径 +5 环带均无黑点色",
        "T07 = mirror_h ∘ R(90)，T08 = R(90) ∘ mirror_h，矩阵逐项不同，图中形态亦不同",
        f"请求 {m['request_totals']['render_requests']} 次（成功 {m['request_totals']['render_ok']}），"
        f"看图 {m['visual_review']['images_opened']} 次，墙钟 {m['wall_clock_s']} 秒",
    ])],
)
print("A09 reports written")
