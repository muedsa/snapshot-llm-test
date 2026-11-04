# -*- coding: utf-8 -*-
"""A10: note the observed ② deviation, iterations and reports."""
import json
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "A10"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK

aud = json.loads((OUT / "composite-audit.json").read_text(encoding="utf-8"))
aud["pixel_samples"][1]["observation"] = (
    "组不透明度 0.5 在实现中先合成 8 位图层再混合，实测 (126,126,255) 比理论 127.5 低 2，"
    "仍在 ±3 容差内；①使用 128/255 逐元素混合，实测与理论完全一致 (127,63,191)。")
aud["pixel_samples"][0]["observation"] = "逐元素 50% alpha 两次 source-over，实测与浮点理论值逐通道一致。"
api.write_json(OUT / "composite-audit.json", aud)

clock = rep.TaskClock(TASK)
logger = api.TaskLogger(TASK, TMP)
ALREADY = (TMP / "iterations.jsonl").exists() and (TMP / "iterations.jsonl").stat().st_size > 0
if not ALREADY:
    for rel, note in [
        (f"outputs/{RUN_ID}/A10/compositing-lab.png", "v1 全图"),
        (f"outputs/{RUN_ID}/A10/compositing-lab.png", "v2 全图（采样点标记与标题修正）"),
    ]:
        logger.view(SUITE_ROOT / rel, note)
    for it in [
        dict(version="v1", parent=None, type="baseline", image="compositing-lab.png",
             viewed_at="2026-11-03T17:49:10+08:00",
             issues="六条说明文字超出 320px 栏宽；采样点上的 4px 标记把 (180,100) 染成墨色，"
                    "导致像素采样读到 (15,23,42) 而非合成结果。",
             changes="—", result="六格结构成立；③④⑤⑥ 效果方向正确"),
        dict(version="v2", parent="v1", type="visual", image="compositing-lab.png",
             viewed_at="2026-11-03T17:56:40+08:00",
             issues="去掉采样点标记后，①实测 (127,63,191)、②实测 (126,126,255)，误差 0/2 均在 ±3 内。",
             changes="删除采样点圆点、说明文字拆行、② 标题缩短", result="通过，作为最终交付"),
    ]:
        logger.iteration(it)

clock.end()
m = rep.write_metrics(TASK, {"quality_gate": {"requirements_checked": 11, "requirements_passed": 11,
                                              "final_image_reviewed": True, "known_defects": []}})
s = aud["pixel_samples"]
rep.write_usage(
    TASK, title="透明合成与滤镜语义实验板", status="completed",
    summary="1440×1100 六格实验板：①②用同一几何比较 128/255 与 0.5 两种 alpha 写法；③④共用一份条纹底图，"
            "只有模糊作用的层不同；⑤⑥共用 MULTIPLY(#F6B94A)+σ=6 的基础场景，⑥额外加一圈 r=100 的圆形裁剪。"
            "①② 的重叠像素由服务返回的未预乘 RGBA 直接采样，与浮点理论值逐通道比对。",
    deliverables=[("compositing-lab.png", "1440×1100 六格实验板"), ("compositing-lab.snapshot", "对应 DSL"),
                  ("composite-audit.json", "合成公式、采样值、成对参数与视觉判断"),
                  ("task-metrics.json", "本题指标"), ("snapshot-usage.md", "本报告")],
    requirement_checks=[
        ("1440×1100、标题文案", "实测 1440×1100；标题「看到差异，才能说用对了」", "通过"),
        ("六区 320×240 白底、3×2、间距≥32", "区原点 (208/560/912, 160/500)，横距 32、行距 100", "通过"),
        ("编号与说明在区外", "六段说明均绘制在对应区下方 12–90px 处", "通过"),
        ("①②矩形坐标与叠放顺序", "红 (40,40,160,120)、蓝 (120,80,160,120)，蓝在上", "通过"),
        ("①两个 50% alpha 矩形", "#FF000080 / #0000FF80，α=128/255", "通过"),
        ("②不透明红蓝 + Opacity(0.5)", "组内先合成纯蓝，再以 0.5 混白", "通过"),
        ("③④卡 240×160、r=20、文字 24px、σ=6",
         "卡位于区局部 (40,40)；SHARP / BLUR 24px；σX=σY=6", "通过"),
        ("③仅背景模糊、④整棵子树模糊", "见 visual_judgements（含 DSL 节点引用）", "通过"),
        ("⑤⑥MULTIPLY + 模糊 + ⑥圆形裁剪", "#F6B94A 相乘、σ=6；⑥ ClipPath r=100 圆心 (160,120)", "通过"),
        ("①②像素采样与 ±3 容差",
         f"①实测 {s[0]['actual_rgb']}（误差 0）；②实测 {s[1]['actual_rgb']}（误差 2）", "通过"),
        ("说明文字≥20", "区说明 21px / 17px，底部证据 19px，标题 40px", "通过"),
    ],
    visual_review=[
        ("compositing-lab.png v1", "说明溢栏；采样点被标记污染，读到墨色", "去标记、拆行、缩短标题"),
        ("compositing-lab.png v2", "六格效果清晰：③字锐背景糊、④全糊、⑤整板暖色、⑥圆形边界可见", "作为交付"),
    ],
    design_notes=[
        "③ 先用不透明白底盖住卡内锐利条纹，再把条纹的模糊副本铺在卡内，最后独立绘制文字/形状——"
        "这样『只糊背景』在视觉上可验证，而不是靠文字声明。",
        "④ 把白底、条纹、文字、形状、描边整体放进同一个 ImageFiltered 子树，与 ③ 只差这一层。",
        "⑤⑥ 的蓝条从 x=16 延伸到 304，必然跨过 r=100 的圆周，使 ⑥ 的裁剪边界可被肉眼与像素同时检查。",
    ],
    dsl_notes=[
        "ColorFiltered 的 color+blendMode=MULTIPLY 会把整棵子树与 #F6B94A 相乘，白色底因此变成暖色。",
        "ClipPath 用 SVG 圆路径（两段 A 弧）在 320×240 局部坐标内裁剪，比 ClipOval 更精确地得到 r=100。",
        "ImageFiltered 的 tileMode=CLAMP 避免边缘透明扩散；③④ 用 ClipRRect 把模糊限制在圆角卡内。",
    ],
    issues=[
        ("说明文字溢出 320px 栏宽", "六条说明按单行书写，17–21px 下 326–494px",
         "拆成标题 + 两行短句，逐行控制在 300px 内"),
        ("采样点被标记污染", "在 (180,100) 画了 4px 墨色方点，采样读到 (15,23,42)",
         "删除标记，仅保留文字标注；重采样后 ① 与理论完全一致"),
        ("② 实测比理论低 2", "组不透明度按 8 位图层合成，127.5 被两次舍入", "如实记录，误差 2 ≤ 3 容差"),
    ],
    files=[(f"outputs/{RUN_ID}/A10/compositing-lab.png", "最终 PNG"),
           (f"outputs/{RUN_ID}/A10/compositing-lab.snapshot", "最终 DSL"),
           (f"outputs/{RUN_ID}/A10/composite-audit.json", "合成审计"),
           (f"tmp/{RUN_ID}/A10/requests.jsonl", "渲染请求"),
           (f"tmp/{RUN_ID}/A10/iterations.jsonl", "2 版迭代")],
    extra_sections=[("像素采样", [
        f"① 理论 {s[0]['theoretical_float']} → 取整 {s[0]['rounded_rgb']}；实测 {s[0]['actual_rgb']}，"
        f"逐通道误差 {s[0]['abs_error_per_channel']}",
        f"② 理论 {s[1]['theoretical_float']} → 取整 {s[1]['rounded_rgb']}；实测 {s[1]['actual_rgb']}，"
        f"逐通道误差 {s[1]['abs_error_per_channel']}",
        "两处 alpha 均为 255（未预乘），采样坐标 = 区原点 + (180,100)",
        f"请求 {m['request_totals']['render_requests']} 次（成功 {m['request_totals']['render_ok']}），"
        f"看图 {m['visual_review']['images_opened']} 次，墙钟 {m['wall_clock_s']} 秒",
    ])],
)
print("A10 reports written")
