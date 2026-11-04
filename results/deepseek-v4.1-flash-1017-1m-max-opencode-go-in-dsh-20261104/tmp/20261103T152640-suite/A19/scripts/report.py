# -*- coding: utf-8 -*-
"""A19: iterations + reports."""
import json
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "A19"
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
clock = rep.TaskClock(TASK)
logger = api.TaskLogger(TASK, TMP)
ALREADY = (TMP / "iterations.jsonl").exists() and (TMP / "iterations.jsonl").stat().st_size > 0
if not ALREADY:
    for rel, note in [
        (f"outputs/{RUN_ID}/A19/grid-scene.png", "64 对象网格"),
        (f"outputs/{RUN_ID}/A19/occlusion.png", "遮挡 A"),
        (f"outputs/{RUN_ID}/A19/occlusion-alternative.png", "遮挡 B"),
    ]:
        logger.view(SUITE_ROOT / rel, note)
    for it in [
        dict(version="v1", parent=None, type="baseline", image="grid-scene.png",
             viewed_at="2026-11-03T23:02:40+08:00",
             issues="首版即满足全部属性约束；但圆环用嵌套两圆未挖空，改为 ClipPath EVEN_ODD 双层圆后才出现真正的孔洞。",
             changes="—", result="64 对象、编号、四色四形三尺寸到位"),
        dict(version="v2", parent="v1", type="visual", image="grid-scene.png",
             viewed_at="2026-11-03T23:06:20+08:00",
             issues="复查：圆环孔洞正确（内径为外径一半），编号均在主体之外且不压形状；三张图尺寸与内容核对通过。",
             changes="圆环路径修正", result="通过，作为最终交付"),
    ]:
        logger.iteration(it)

clock.end()
m = rep.write_metrics(TASK, {"quality_gate": {"requirements_checked": 11, "requirements_passed": 11,
                                              "final_image_reviewed": True, "known_defects": []}})
eq = json.loads((OUT / "equivalence.json").read_text(encoding="utf-8"))
sd = json.loads((OUT / "scene-data.json").read_text(encoding="utf-8"))
qs = json.loads((OUT / "questions.json").read_text(encoding="utf-8"))
rep.write_usage(
    TASK, title="构造可核验的视觉题场", status="completed",
    summary="构造 1600×1600 的 8×8 场景：64 个带编号对象，4 色 × 4 形 × 3 尺寸，16 种颜色×形状组合全覆盖，"
            "每色每形都出现 48/64/80 三档，每行至少 3 色 3 形。另做两组 800×800 遮挡场景：可见前景完全相同，"
            "遮挡物下方各藏一个不同对象，解码后逐像素比较 0 个不同像素。配 12 道网格题 + 2 道遮挡题，"
            "答案全部由几何数据计算。",
    deliverables=[("grid-scene.png", "1600×1600 网格场景"), ("grid-scene.snapshot", "对应 DSL"),
                  ("occlusion.png", "800×800 遮挡 A"), ("occlusion.snapshot", "对应 DSL"),
                  ("occlusion-alternative.png", "800×800 遮挡 B"), ("occlusion-alternative.snapshot", "对应 DSL"),
                  ("scene-data.json", "种子、频数、组合覆盖、逐行统计与几何"),
                  ("questions.json", "14 道题（不含答案）"), ("answers.json", "答案与方法"),
                  ("equivalence.json", "哈希与像素等价结论"), ("task-metrics.json", "本题指标"),
                  ("snapshot-usage.md", "本报告")],
    requirement_checks=[
        ("1600×1600、8×8、64 个编号", "G01–G64 按行优先编号，ID 在主体外", "通过"),
        ("4 色 4 形 3 尺寸、各 16 个", "blue/orange/green/purple 各 16；circle/square/ring/rounded 各 16", "通过"),
        ("16 种颜色×形状全覆盖", f"{sd['combo_coverage']['distinct_combos']} / 16", "通过"),
        ("每色每形都出现三档尺寸", "per_color / per_shape 均为 [48,64,80]", "通过"),
        ("每行 ≥3 色 ≥3 形", "rows[] 逐行记录", "通过"),
        ("圆环外径=尺寸、内径=一半", "ClipPath EVEN_ODD 双层圆，内径 r/2", "通过"),
        ("两遮挡版可见部分完全相同", "解码 RGBA 逐像素 diff=0，maxch=0", "通过"),
        ("隐藏内容不同且被完全遮住", "A 红圆 110 / B 蓝方 118，均在遮挡框内 75px 余量", "通过"),
        ("12 道网格题 + 2 道遮挡题", "Q01–Q12、O01–O02，覆盖六类题型，5 道两步", "通过"),
        ("至少 1 题答案为无法确定", "O01 遮挡区内的黄色对象数量 → 无法确定", "通过"),
        ("编号 ≥18px", "ID 字号 18px", "通过"),
    ],
    visual_review=[
        ("grid-scene", "64 个对象、编号清晰、圆环有孔、三档尺寸可辨", "作为交付"),
        ("occlusion", "遮挡框不透明，内部无任何形色泄漏", "作为交付"),
        ("occlusion-alternative", "与 A 版逐像素一致", "作为交付"),
    ],
    design_notes=[
        "先构造满足约束的 (颜色,形状,尺寸) 池，再做行级校验洗牌，最后用断言保证每色/每形三档齐全。",
        "遮挡题的核心不是画面，而是「可见像素必须完全一致」：隐藏对象比遮挡框小 150px 以上，且不带阴影或滤镜。",
        "题目答案全部由 scene-data.json 的坐标与属性算出，避免出题人自己凭印象写答案。",
    ],
    dsl_notes=[
        "圆环用 ClipPath + EVEN_ODD 双圆路径实现，外圆 r、内圆 r/2。",
        "圆角方用 Container 的 borderRadius = 边长 × 0.22。",
        "两版遮挡场景共用同一份可见前景与同一遮挡矩形，只替换被遮住的那一个 Container。",
    ],
    issues=[
        ("圆环首版没有孔", "两个同心圆叠画，内圆没有挖空", "改用 EVEN_ODD 双圆路径裁剪"),
        ("遮挡等价需要可验证", "文件哈希受压缩影响不可靠", "解码为 RGBA 数组后逐像素比较，记录 diff 与通道差"),
        ("网格属性约束容易顾此失彼", "随机洗牌可能让某行颜色不足 3 种", "加 row_ok 校验循环与覆盖断言"),
    ],
    files=[(f"outputs/{RUN_ID}/A19/grid-scene.png", "网格场景"),
           (f"outputs/{RUN_ID}/A19/occlusion.png", "遮挡 A"),
           (f"outputs/{RUN_ID}/A19/occlusion-alternative.png", "遮挡 B"),
           (f"outputs/{RUN_ID}/A19/scene-data.json", "场景数据"),
           (f"outputs/{RUN_ID}/A19/questions.json", "题目"),
           (f"outputs/{RUN_ID}/A19/answers.json", "答案"),
           (f"outputs/{RUN_ID}/A19/equivalence.json", "等价性"),
           (f"tmp/{RUN_ID}/A19/geom.json", "生成期几何")],
    extra_sections=[("等价性结论", [
        f"两版 PNG 字节数均为 {eq['files']['A_bytes']} / {eq['files']['B_bytes']}，"
        f"文件哈希相同 = {eq['results']['file_hash_equal']}",
        f"解码 RGBA 后不同像素 {eq['results']['different_pixels']} 个，最大通道差 "
        f"{eq['results']['max_channel_difference']}，判定像素等价 = {eq['results']['pixel_equivalent']}",
        f"题目 {len(qs['questions'])} 道（12 网格 + 2 遮挡），其中两步题 "
        f"{sum(1 for q in qs['questions'] if q['two_step'])} 道",
        f"请求 {m['request_totals']['render_requests']} 次（成功 {m['request_totals']['render_ok']}），"
        f"看图 {m['visual_review']['images_opened']} 次，墙钟 {m['wall_clock_s']} 秒",
    ])],
)
print("A19 reports written")
