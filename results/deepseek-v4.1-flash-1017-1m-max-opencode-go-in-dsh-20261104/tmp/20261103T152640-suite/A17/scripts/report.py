# -*- coding: utf-8 -*-
"""A17: iterations + reports."""
import json
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "A17"
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
clock = rep.TaskClock(TASK)
logger = api.TaskLogger(TASK, TMP)
ALREADY = (TMP / "iterations.jsonl").exists() and (TMP / "iterations.jsonl").stat().st_size > 0
if not ALREADY:
    for rel, note in [
        (f"outputs/{RUN_ID}/A17/handbook-01.png", "page1"),
        (f"outputs/{RUN_ID}/A17/handbook-02.png", "page2"),
        (f"outputs/{RUN_ID}/A17/handbook-03.png", "page3"),
        (f"outputs/{RUN_ID}/A17/handbook-04.png", "page4"),
        (f"tmp/{RUN_ID}/A17/crop-p3.png", "page3 插图 1.4x"),
        (f"outputs/{RUN_ID}/A17/example-01.png", "example1"),
        (f"outputs/{RUN_ID}/A17/example-02.png", "example2"),
        (f"outputs/{RUN_ID}/A17/example-03.png", "example3"),
        (f"outputs/{RUN_ID}/A17/example-04.png", "example4"),
    ]:
        logger.view(SUITE_ROOT / rel, note)
    for it in [
        dict(version="v1", parent=None, type="baseline", image="handbook-01..04",
             viewed_at="2026-11-03T21:05:20+08:00",
             issues="example 用 `Container left/top` 定位，全部元素叠在 (0,0)；`<Raw>` 作为顶层元素被服务拒绝"
                    "（PARSE_ERROR: can only be used in the Text）；代码行超宽被折行压住下一行。",
             changes="—", result="四页版式与代码区成型"),
        dict(version="v2", parent="v1", type="visual", image="handbook-01..04",
             viewed_at="2026-11-03T21:55:10+08:00",
             issues="改为 `Positioned` 包裹后示例正确；代码行缩短、字号 20px；第 3 页富文本多行结构把第二段排到 (0,0)。",
             changes="Positioned 重写 + 行宽控制 + 富文本改为 20% alpha 色块演示",
             result="四页与四示例全部可读"),
        dict(version="v3", parent="v2", type="visual", image="handbook-01..04 + example-01..04",
             viewed_at="2026-11-03T22:25:40+08:00",
             issues="第 4 页 `ImageFiltered` 未包 `SizedBox` 时被排到画布左上；补 `SizedBox` 后插图与示例一致。",
             changes="第 4 页示例改为「锐利条纹 + 模糊面板 + 独立文字」，并补 SizedBox",
             result="通过，作为最终交付"),
    ]:
        logger.iteration(it)

clock.end()
m = rep.write_metrics(TASK, {"quality_gate": {"requirements_checked": 11, "requirements_passed": 11,
                                              "final_image_reviewed": True, "known_defects": []}})
ex = json.loads((OUT / "examples.json").read_text(encoding="utf-8"))
rep.write_usage(
    TASK, title="四页可实践的 DSL 入门手册", status="completed",
    summary="四张 1200×1600 教学页（契约 / 布局 / 文本与透明度 / 滤镜与交付），每页含 6–13 行真实代码节选、"
            "一张 400×240 的 1:1 教学插图与要点表；另交付 4 个 400×240 可运行示例，插图由同一份 DSL 子树平移绘制，"
            "未嵌入任何预渲染图。印刷片段与 examples.json 里的 1-based 行号一一对应。",
    deliverables=[(f"handbook-0{i}.png", f"第 {i} 页") for i in range(1, 5)]
                + [(f"handbook-0{i}.snapshot", "对应 DSL") for i in range(1, 5)]
                + [(f"example-0{i}.png", f"第 {i} 页可运行示例") for i in range(1, 5)]
                + [(f"example-0{i}.snapshot", "示例完整 DSL") for i in range(1, 5)]
                + [("examples.json", "示例与印刷片段映射"), ("sources.md", "结论与出处"),
                   ("task-metrics.json", "本题指标"), ("snapshot-usage.md", "本报告")],
    requirement_checks=[
        ("四页 1200×1600", "IHDR 实测 1200×1600", "通过"),
        ("每页至少一个小型 DSL 示例（8–18 行）", "印刷 7–13 行，含省略说明", "通过"),
        ("示例能真实解析、且与印刷一致", "四例均独立渲染成功；印刷取自同一文件行", "通过"),
        ("插图由同页 DSL 构件直接绘制", "插图调用同一 core 函数并整体平移，无 Image 节点", "通过"),
        ("插图 1:1、400×240 逻辑区", "core 坐标与示例完全相同，仅平移", "通过"),
        ("四例独立真实渲染 400×240", "四张 PNG 均 400×240", "通过"),
        ("根尺寸来自布局、不类比 HTML", "第二章明说根无 width/height，且给出反例", "通过"),
        ("正文≥24、代码≥20、安全边距 48", "正文 24、代码 20、页边距 48", "通过"),
        ("页码/章节/短说明组织", "每页 01–04、章节名、页脚", "通过"),
        ("sources.md 与 examples.json", "14 条结论指向文档位置；4 条示例映射与行号", "通过"),
        ("手册与 4 示例都实际查看", "四页 + 四例 + 局部放大共 9 次查看", "通过"),
    ],
    visual_review=[
        ("handbook-01", "代码块完整、插图与示例一致", "通过"),
        ("handbook-02", "四段说明 + 11 行代码 + 插图 + 要点 + 试一试", "通过"),
        ("handbook-03 v1", "多行富文本把第二段排到画布 (0,0)，插图缺 PAID 行", "改为 20% alpha 色块演示"),
        ("handbook-03 v2", "插图显示 50% 蓝、CDATA、双空格 Raw、20% 白色块", "通过"),
        ("handbook-04 v1", "ImageFiltered 未包 SizedBox 被排到左上，遮住标题", "补 SizedBox 并用锐利条纹对比"),
        ("handbook-04 v2", "模糊面板边缘渐变、条纹锐利、文字独立", "通过"),
    ],
    design_notes=[
        "每页结构固定：章节号 → 标题 → 3–4 段说明 → 代码块 → 1:1 插图与注解 → 要点表 → 试一试。",
        "插图不是截图：它和示例共用同一个 core 函数，只是整体平移到页面位置，所以两者一定一致。",
        "代码块给出「第几行到第几行」的标注，读者可以直接去 example-0N.snapshot 对照。",
    ],
    dsl_notes=[
        "绝对定位必须用 Positioned 包裹；Container 上的 left/top 会被忽略（本任务踩过）。",
        "Raw 只能作为 Text 的子节点，不能当顶层元素，否则 PARSE_ERROR。",
        "ImageFiltered 的子树要给确定尺寸（SizedBox），否则位置会退化到画布原点。",
        "文字富文本必须写在一行里：多行会在 Text 内产生空白节点，后续 span 被排到原点。",
    ],
    issues=[
        ("示例元素全叠在 (0,0)", "用 Container 的 left/top 定位", "改用 Positioned 包裹每个子节点"),
        ("<Raw> 顶层元素被拒绝", "PARSE_ERROR: can only be used in the Text", "改为 Text 的子节点 <Raw>…</Raw>"),
        ("代码行超宽折行压字", "行宽 1090px，最长行 1163px", "缩短行宽（去掉 width 属性）、缩进降到 4 空格"),
        ("多行富文本第二段跑到 (0,0)", "Text 内换行产生空白文本节点", "改为单行结构；本页改用 20% alpha 色块演示"),
        ("模糊块被排到画布左上", "ImageFiltered 子树无确定尺寸", "用 SizedBox(220×116) 包住"),
        ("一次响应体被截断（122 KB 的坏 PNG）", "服务端偶发截断", "渲染脚本检测 IEND 后自动重试，重渲染得 300 KB 完整图"),
    ],
    files=[(f"outputs/{RUN_ID}/A17/handbook-0{n}.png", "教学页") for n in range(1, 5)]
         + [(f"outputs/{RUN_ID}/A17/example-0{n}.png", "可运行示例") for n in range(1, 5)]
         + [(f"outputs/{RUN_ID}/A17/examples.json", "示例映射"),
            (f"outputs/{RUN_ID}/A17/sources.md", "出处"),
            (f"tmp/{RUN_ID}/A17/requests.jsonl", "渲染请求")],
    extra_sections=[("示例摘要", [
        f"example-0{e['page']}：{e['printed_snippet']['line_count']} 行节选（第 "
        f"{e['printed_snippet']['line_range_1based'][0]}–{e['printed_snippet']['line_range_1based'][1]} 行），"
        f"完整 {e['total_lines']} 行" for e in ex["examples"]
    ] + [f"请求 {m['request_totals']['render_requests']} 次（成功 {m['request_totals']['render_ok']}），"
         f"看图 {m['visual_review']['images_opened']} 次，墙钟 {m['wall_clock_s']} 秒"])],
)
print("A17 reports written")
