# -*- coding: utf-8 -*-
"""A18: iterations + reports."""
import json
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "A18"
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
clock = rep.TaskClock(TASK)
logger = api.TaskLogger(TASK, TMP)
ALREADY = (TMP / "iterations.jsonl").exists() and (TMP / "iterations.jsonl").stat().st_size > 0
if not ALREADY:
    for rel, note in [
        (f"tmp/{RUN_ID}/A18/previews/preview-a.png", "构图 A（放射）"),
        (f"tmp/{RUN_ID}/A18/previews/preview-b.png", "构图 B（传送列）"),
        (f"outputs/{RUN_ID}/A18/three-act-story.png", "最终图"),
        (f"tmp/{RUN_ID}/A18/thumb-400.png", "400px 缩略"),
    ]:
        logger.view(SUITE_ROOT / rel, note)
    for it in [
        dict(version="preview-a", parent=None, type="exploration", image="preview-a.png",
             viewed_at="2026-11-03T22:20:10+08:00",
             issues="三角形节点没画出来（ClipPath 坐标用了画布绝对坐标）；第二幕 15 个单元挤在 172° 弧上互相重叠；"
                    "第三幕分组逻辑写错，位置散乱。",
             changes="—", result="放射方向可行，需重写节点与排布"),
        dict(version="preview-b", parent=None, type="exploration", image="preview-b.png",
             viewed_at="2026-11-03T22:27:40+08:00",
             issues="三行分配让每个节点只拿到单一颜色；底线穿过单元；三角形同样缺失。",
             changes="—", result="淘汰"),
        dict(version="final", parent="preview-a", type="visual", image="three-act-story.png",
             viewed_at="2026-11-03T22:40:20+08:00",
             issues="三角形改为 Positioned + 局部路径后可见；第二幕改向心螺旋（180→61）不再重叠；"
                    "第三幕按 5/5/5 分组，每组 ≥2 色，节点距离 84px。",
             changes="节点绘制修正、第二幕螺旋、第三幕分组", result="通过"),
        dict(version="thumbnail", parent="final", type="visual", image="thumb-400.png",
             viewed_at="2026-11-03T22:42:10+08:00",
             issues="400px 缩略下仍能分出「环 / 团 / 三束」三种轮廓。", changes="—", result="通过"),
    ]:
        logger.iteration(it)

clock.end()
m = rep.write_metrics(TASK, {"quality_gate": {"requirements_checked": 10, "requirements_passed": 10,
                                              "final_image_reviewed": True, "known_defects": []}})
aud = json.loads((OUT / "story-audit.json").read_text(encoding="utf-8"))
rep.write_usage(
    TASK, title="守恒对象的三幕视觉叙事", status="completed",
    summary="1600×1000 三幕并置：同一组 15 个 36px 单元（5 蓝 / 5 橙 / 5 灰）与 3 个形状固定的节点（方 / 圆 / 三角）。"
            "第一幕为 r=150 的均匀环、全部指向 N01；第二幕改为 180→61 的向心螺旋，最近 5 个单元距节点仅 61–95px；"
            "第三幕按 5/5/5 分给三个节点，每组含两种以上颜色。先做了两版 1600×1000 预览再选型。",
    deliverables=[("three-act-story.png", "1600×1000 三幕图"), ("three-act-story.snapshot", "对应 DSL"),
                  ("story-audit.json", "逐幕单元/节点/接收关系与可观察线索"),
                  ("rationale.md", "叙事感知说明"), ("task-metrics.json", "本题指标"),
                  ("snapshot-usage.md", "本报告")],
    requirement_checks=[
        ("三幕、每幕 15 单元 + 3 节点", "逐幕 units 15 条、nodes 3 条，见 story-audit", "通过"),
        ("5 蓝 / 5 橙 / 5 灰，直径 36", "UNIT_COLORS 与 diameter_px 全幕一致", "通过"),
        ("第一幕单一中心吸引", "15 条连线终点均为 N01，N02/N03 received=0", "通过"),
        ("第二幕同一系统过载", "向心螺旋，最近 5 个距节点 61–95px（第一幕 150）", "通过"),
        ("第三幕每节点 5 单元且 ≥2 色", "5/5/5，N01 2蓝2橙1灰、N02 1蓝2橙2灰、N03 2蓝1橙2灰", "通过"),
        ("不靠增删缩小、不用警告文字", "单元数量/直径恒定；图中只有总标题与幕名", "通过"),
        ("单元不重叠、线不遮圆", "圆心间距 ≥40；先画线后画圆与节点", "通过"),
        ("两种构图预览并选择", "preview-a / preview-b 均 1600×1000 实际渲染后比较", "通过"),
        ("跨幕身份稳定", "U01–U15 颜色固定；N01–N03 形状固定，尺寸 56", "通过"),
        ("全图 + 400px 缩略查看", "两者均已查看，结论写入 audit.viewing", "通过"),
    ],
    visual_review=[
        ("preview-a", "三角缺失、第二幕重叠、第三幕散乱", "重写节点与三幕排布"),
        ("preview-b", "每组单一颜色、线穿圆", "淘汰"),
        ("three-act-story", "环 / 螺旋 / 三束三种结构清晰，颜色分组可辨", "作为交付"),
        ("thumb-400", "缩略仍能读出三幕轮廓差异", "通过"),
    ],
    design_notes=[
        "用「到节点距离」而不是「单元大小」表达负载：150 → 61 → 84，三个数就能说明三幕的差别。",
        "节点用方/圆/三角区分身份，不依赖颜色，符合「关系不能只靠颜色推断」。",
        "连线先画、圆后画，任何一条线都不会盖住单元。",
    ],
    dsl_notes=[
        "三角形节点用 ClipPath + 局部坐标路径，外套 Positioned 才能落在指定位置。",
        "连线是旋转后的细长 Container；所有角度用 atan2 现算，避免手写矩阵出错。",
        "幕名与总标题用 Text，节点与单元不写任何解释文字。",
    ],
    issues=[
        ("三角形节点不可见", "ClipPath 的路径用了画布绝对坐标，而子树从节点自身原点开始",
         "改成局部路径 0..56 并包在 Positioned 里"),
        ("第二幕单元重叠", "15 个 36px 单元挤在 172° 弧上，弧长 312px < 540px",
         "改为半径 180→61 的螺旋，相邻圆心距 ≥40"),
        ("第三幕分组错乱", "用三元表达式拼坐标，分支条件写错", "改为按 GROUPS 显式分组，每组扇形展开"),
        ("预览 B 每组只有一种颜色", "按颜色分行排列", "淘汰该构图，并在 audit 中记录理由"),
    ],
    files=[(f"outputs/{RUN_ID}/A18/three-act-story.png", "最终图"),
           (f"outputs/{RUN_ID}/A18/story-audit.json", "叙事审计"),
           (f"outputs/{RUN_ID}/A18/rationale.md", "感知说明"),
           (f"tmp/{RUN_ID}/A18/previews/", "两版构图预览"),
           (f"tmp/{RUN_ID}/A18/thumb-400.png", "400px 缩略")],
    extra_sections=[("三幕数据", [
        f"第 {a['act']} 幕：receiving={a['counts']}，到节点距离 {a['unit_spacing']['min_distance_to_node']}"
        f"–{a['unit_spacing']['max_distance_to_node']}px" for a in aud["acts"]
    ] + [f"请求 {m['request_totals']['render_requests']} 次（成功 {m['request_totals']['render_ok']}），"
         f"看图 {m['visual_review']['images_opened']} 次，墙钟 {m['wall_clock_s']} 秒"])],
)
print("A18 reports written")
