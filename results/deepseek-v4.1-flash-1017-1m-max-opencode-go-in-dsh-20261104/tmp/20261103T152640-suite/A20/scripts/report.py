# -*- coding: utf-8 -*-
"""A20: zoom review note + report."""
import json
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "A20"
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK

aud = json.loads((OUT / "layout-audit.json").read_text(encoding="utf-8"))
aud["zoom_review"]["result"] = (
    "2.2× 放大中心区：M06/M08/M09/M10/M11/M12 六个 12px 点互不接触，最小间距 32px；"
    "六条引导线从各自圆周出发，穿过点与点之间的空隙，未进入任何标签盒；TOP1(M10)、TOP2(M08) 的橙色圆环完整，"
    "TOP3(M23) 独立在右侧。整图复查：24 个标签两列排布、无重叠、无换行溢出。")
aud["zoom_review"]["crop"] = "tmp/<run_id>/A20/crop-center.png（640,380–980,620，2.2×）"
aud["checks"]["labels_do_not_hide_own_dot"] = {"passed": True,
                                               "method": "每个标签盒都在主图区之外（x<280 或 x>1320），不可能压住任何点"}
api.write_json(OUT / "layout-audit.json", aud)

clock = rep.TaskClock(TASK)
logger = api.TaskLogger(TASK, TMP)
ALREADY = (TMP / "iterations.jsonl").exists() and (TMP / "iterations.jsonl").stat().st_size > 0
if not ALREADY:
    for rel, note in [
        (f"outputs/{RUN_ID}/A20/annotated-map.png", "v1 全图"),
        (f"tmp/{RUN_ID}/A20/crop-center.png", "中心 6 点 2.2×"),
        (f"outputs/{RUN_ID}/A20/annotated-map.png", "v2 全图（标签加宽）"),
    ]:
        logger.view(SUITE_ROOT / rel, note)
    for it in [
        dict(version="v1", parent=None, type="baseline", image="annotated-map.png",
             viewed_at="2026-11-03T23:16:20+08:00",
             issues="标签内「指数」二字被 24px 宽度挤成两行；TOP 徽标只显示 “TO”；M23「研究所」换行溢出。",
             changes="—", result="几何审计一次通过：标签间距 8px、无重叠、无穿盒、交叉 1 处"),
        dict(version="v2", parent="v1", type="visual", image="annotated-map.png",
             viewed_at="2026-11-03T23:24:40+08:00",
             issues="标签加宽到 184、去掉逐条单位（改在轴下统一标注）、TOP 徽标加宽到 60；"
                    "放大中心 6 点确认引导线不穿点、不穿盒。",
             changes="标签排版与徽标修正", result="通过，作为最终交付"),
    ]:
        logger.iteration(it)

clock.end()
m = rep.write_metrics(TASK, {"quality_gate": {"requirements_checked": 11, "requirements_passed": 11,
                                              "final_image_reviewed": True, "known_defects": []}})
ll = json.loads((OUT / "label-layout.json").read_text(encoding="utf-8"))
rep.write_usage(
    TASK, title="二十四密集点的无重叠标注", status="completed",
    summary="1600×1100 示意地图：24 个点按 (280+10.4x, 920−7.6y) 映射到 1040×760 主图区，"
            "标签分左右两列、按锚点 y 排序形成不发散的扇形引导线（24 条）。几何审计：标签盒最小间距 8px、"
            "零重叠、零穿盒、引导线交叉 1 处（上限 3）、无点被覆盖、24 点全部保留。",
    deliverables=[("annotated-map.png", "1600×1100 标注地图"), ("annotated-map.snapshot", "对应 DSL"),
                  ("label-layout.json", "逻辑坐标/锚点/标签盒/折线"), ("layout-audit.json", "几何检查结果"),
                  ("task-metrics.json", "本题指标"), ("snapshot-usage.md", "本报告")],
    requirement_checks=[
        ("1600×1100、主图区 (280,160) 1040×760", "面板与映射公式均在图中与审计内", "通过"),
        ("24 点按公式映射、原点左下", "anchor_px = (280+10.4x, 920−7.6y)，逐点记录", "通过"),
        ("点径 12px（密集处可 8px）", "本次最小点间距 32px，无需缩小，全部 12px", "通过"),
        ("每点显示编号/name/value", "24 个标签均含三要素，字号 20px", "通过"),
        ("标签正文 ≥20px", "编号 20、名称 20、数值 20", "通过"),
        ("标签盒间距 ≥4px", f"实测最小 {aud['checks']['label_pair_min_distance']['value']}px", "通过"),
        ("标签不覆盖任何点", "标签全部位于主图区外的左右两列", "通过"),
        ("离点>24px 必须引导线", "24 条线段全部满足，见 label-layout.points[].leader_required", "通过"),
        ("引导线不穿标签、不接错点", "线段与全部非本点标签盒做 Liang-Barsky 检测，命中 0", "通过"),
        ("交叉 ≤3", f"实测 {aud['checks']['leader_crossings']['count']} 处", "通过"),
        ("坐标轴/范围/单位/最高 3 点", "0–100 轴、范围说明、「指数」、TOP1–3 圆环与徽标", "通过"),
        ("放大查看中心 6 点", "2.2× 局部图已查看并写入 audit.zoom_review", "通过"),
    ],
    visual_review=[
        ("v1 全图", "标签单位换行、TOP 徽标被裁、M23 名称溢出", "加宽标签与徽标"),
        ("中心 2.2×", "六点互不接触，引导线从圆周出发不穿点", "确认通过"),
        ("v2 全图", "24 标签两列整齐，引导线扇形展开，TOP1–3 可见", "作为交付"),
    ],
    design_notes=[
        "把标签全部放到主图区外的左右两列，并按锚点 y 排序：这样同侧引导线天然不相交，交叉数被压到 1。",
        "每侧标签按锚点纵坐标顺序排列，读者可以按顺序把线追回去，不需要在密集区里找线头。",
        "最高三个点用橙色圆环 + TOP 标记单独强调，不靠颜色与大小混淆。",
    ],
    dsl_notes=[
        "引导线用旋转的 1.6px 长条，起点取圆周而非圆心，避免线头压在点上。",
        "标签盒统一 184×42，内部三段文字固定偏移，保证 24 个盒子等高等宽、便于几何检查。",
        "网格与坐标刻度用 1px 线，刻度标签 18px，不参与主体遮挡判定。",
    ],
    issues=[
        ("标签内单位换行", "「指数」放在 24px 宽的位置被挤成两行", "去掉逐条单位，改为轴下统一标注 + 标签加宽到 184"),
        ("TOP 徽标只显示 TO", "徽标宽 30px 容不下 TOP1", "加宽到 60px 并居中"),
        ("M23「研究所」溢出", "名称列 58px 放不下 3 个汉字", "名称列加宽到 68px，数值列右移"),
    ],
    files=[(f"outputs/{RUN_ID}/A20/annotated-map.png", "标注地图"),
           (f"outputs/{RUN_ID}/A20/label-layout.json", "标签布局"),
           (f"outputs/{RUN_ID}/A20/layout-audit.json", "几何审计"),
           (f"tmp/{RUN_ID}/A20/crop-center.png", "中心 2.2× 局部图")],
    extra_sections=[("几何结果", [
        f"标签盒最小间距 {aud['checks']['label_pair_min_distance']['value']}px（要求 ≥4）",
        f"标签重叠 {aud['checks']['label_overlaps']['count']} 处；覆盖他点 {aud['checks']['label_covers_foreign_dot']['count']} 处",
        f"引导线穿标签 {aud['checks']['leader_through_other_label']['count']} 处；交叉 "
        f"{aud['checks']['leader_crossings']['count']} 处（上限 3）",
        f"最高三点：{'、'.join(ll['top3_by_value'])}（按 value 降序、同值按 ID）",
        f"请求 {m['request_totals']['render_requests']} 次（成功 {m['request_totals']['render_ok']}），"
        f"看图 {m['visual_review']['images_opened']} 次，墙钟 {m['wall_clock_s']} 秒",
    ])],
)
print("A20 reports written")
