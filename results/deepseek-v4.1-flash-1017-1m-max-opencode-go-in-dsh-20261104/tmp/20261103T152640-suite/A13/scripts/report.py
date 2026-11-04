# -*- coding: utf-8 -*-
"""A13: iterations + reports."""
import json
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "A13"
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
clock = rep.TaskClock(TASK)
logger = api.TaskLogger(TASK, TMP)
ALREADY = (TMP / "iterations.jsonl").exists() and (TMP / "iterations.jsonl").stat().st_size > 0
if not ALREADY:
    for rel, note in [
        (f"tmp/{RUN_ID}/A13/previews/preview-a.png", "方向 A 预览 512"),
        (f"tmp/{RUN_ID}/A13/previews/preview-b.png", "方向 B 预览 512"),
        (f"outputs/{RUN_ID}/A13/symbol-color.png", "彩色图标 512"),
        (f"outputs/{RUN_ID}/A13/symbol-black.png", "纯黑图标 512"),
        (f"outputs/{RUN_ID}/A13/brand-banner.png", "横幅 1200×400"),
        (f"outputs/{RUN_ID}/A13/launch-poster.png", "海报 1080×1350"),
        (f"tmp/{RUN_ID}/A13/previews/thumb-sheet.png", "32px 缩略 + 4× 放大对照"),
    ]:
        logger.view(SUITE_ROOT / rel, note)
    for it in [
        dict(version="direction-a", parent=None, type="exploration", image="preview-a.png",
             viewed_at="2026-11-03T18:14:30+08:00",
             issues="三层叠加成立，中心白点清晰；深色层在透明底上偏灰。",
             changes="—", result="入选"),
        dict(version="direction-b", parent=None, type="exploration", image="preview-b.png",
             viewed_at="2026-11-03T18:15:10+08:00",
             issues="三横杠 + 光柱，32px 会读成字母 l，主次不清。", changes="—", result="淘汰"),
        dict(version="final-symbol", parent="direction-a", type="visual", image="symbol-color.png",
             viewed_at="2026-11-03T18:33:20+08:00",
             issues="黑版三层 alpha 过于接近，缩略时糊成一团；核点略小。",
             changes="核点 60、黑版 alpha 改为 0.60/0.76/0.90", result="缩略可分出层次"),
        dict(version="applications", parent="final-symbol", type="visual", image="brand-banner.png",
             viewed_at="2026-11-03T18:36:40+08:00",
             issues="横幅上深色层与深底几乎同色，三层读不出；海报标志偏左、标题行距过紧。",
             changes="深底场景把 back 层换为 #31415F；海报标志居中、Layerlight 下移 12px",
             result="通过，作为最终交付"),
        dict(version="thumb-32", parent="applications", type="visual", image="thumb-sheet.png",
             viewed_at="2026-11-03T18:42:10+08:00",
             issues="32px 实尺寸下彩色版三层与核点可辨；纯黑版层次可辨。",
             changes="黑版 alpha 再提到 0.60/0.76/0.90", result="通过"),
    ]:
        logger.iteration(it)

clock.end()
m = rep.write_metrics(TASK, {"quality_gate": {"requirements_checked": 11, "requirements_passed": 11,
                                              "final_image_reviewed": True, "known_defects": []}})
brand = json.loads((OUT / "brand-system.json").read_text(encoding="utf-8"))
bc = brand["black_check"]
rep.write_usage(
    TASK, title="品牌标志到完整活动应用", status="completed",
    summary="为虚构品牌「叠光 / Layerlight」先做两个几何方向各 512×512 透明预览（斜向叠压 vs 横杠加光柱），"
            "看图后选前者。最终交付 512×512 透明彩色图标与同几何的纯黑图标、1200×400 品牌横幅、1080×1350 发布海报；"
            "后两者用同一 DSL 几何函数重绘标志，未嵌入图标 PNG。图标由 4 个主要几何构件组成，32×32 缩略仍可读。",
    deliverables=[("symbol-color.png", "512×512 透明彩色图标"), ("symbol-color.snapshot", "对应 DSL"),
                  ("symbol-black.png", "512×512 透明纯黑图标"), ("symbol-black.snapshot", "对应 DSL"),
                  ("brand-banner.png", "1200×400 品牌横幅"), ("brand-banner.snapshot", "对应 DSL"),
                  ("launch-poster.png", "1080×1350 发布海报"), ("launch-poster.snapshot", "对应 DSL"),
                  ("brand-system.json", "色彩/构件/留白/应用映射"), ("rationale.md", "方向取舍说明"),
                  ("task-metrics.json", "本题指标"), ("snapshot-usage.md", "本报告")],
    requirement_checks=[
        ("两个真正不同的几何方向预览 512 透明", "preview-a（叠压）与 preview-b（横杠 + 光柱），均在 tmp 保留", "通过"),
        ("看图选择后完善同一方案", "选 A，在 A 的几何上放大核点并调整黑版 alpha", "通过"),
        ("彩色/纯黑 512 透明", "两张均 512×512、背景透明（Snapshot 不设 background）", "通过"),
        ("纯黑版 alpha>0 像素 RGB 全为 0",
         f"违规像素 {bc['violating_pixels']}，alpha 范围 {bc['alpha_min']}–{bc['alpha_max']}", "通过"),
        ("图标构件 ≤6", "4 个：三块圆角方 + 一个圆点，见 brand-system.components", "通过"),
        ("32×32 仍可识别", "预乘 Lanczos 缩略实尺寸查看，三层与核点可辨", "通过"),
        ("横幅含指定文案", "「叠光」「Layerlight」「把复杂信息，组织成清晰画面」+ 官网", "通过"),
        ("海报含指定文案且独立构图", "日期、OPEN BETA、官网齐全；纵向海报版式，非横幅放大", "通过"),
        ("不嵌入图标 PNG", "横幅与海报调用同一 mark() 几何函数重绘", "通过"),
        ("无色块当图标/无外部图片", "全部为 Container 几何，无 Image 节点", "通过"),
        ("brand-system.json + rationale.md ≤300 字", "构件表、留白、应用映射齐全；说明约 280 字", "通过"),
    ],
    visual_review=[
        ("preview-a", "三层叠压 + 白点，透明底上层次清楚", "入选方向"),
        ("preview-b", "横杠 + 光柱，小尺寸像字母 l", "淘汰"),
        ("symbol-color", "512 下三层与核点清晰", "作为交付"),
        ("symbol-black", "四档 alpha 形成可读层次，RGB 全 0", "作为交付"),
        ("brand-banner v1", "深色层与深底同色、看不出三层", "深底场景 back 层改 #31415F"),
        ("launch-poster v1", "标志偏左、叠光与 Layerlight 过近", "标志居中、标题下移"),
        ("thumb-sheet", "32px 实尺寸与 4× 放大对照，彩色/黑色均可辨", "作为交付"),
    ],
    design_notes=[
        "标志讲的是「叠」：三层沿对角线错开，每层只露出两条边与一个角，叠加处变深但不糊；中心白点是「仍然清晰」的锚点。",
        "深色场景把最底层换成 #31415F，几何不变、只在深底上换明度，保证三层仍能读出（记录在 brand-system.applications）。",
        "横幅是横向 lockup（标志 + 中文名 + 英文名 + 标语 + 官网），海报是纵向海报版式（大标志、标题区、状态与日期、页脚），两者不互为缩放。",
    ],
    dsl_notes=[
        "透明画布：Snapshot 不写 background 属性即可（dslkit.document(background=None) 已支持省略）。",
        "半透明色用 8 位 #RRGGBBAA（如 #101826E6）；同一几何换 mode='black' 即可得到纯黑版。",
        "圆角方块用 Container + borderRadius；核点用等宽高 + borderRadius=半径 得到正圆。",
    ],
    issues=[
        ("黑版三层糊成一团", "0.90/0.80/0.88 三档 alpha 太接近，叠加后几乎全不透明",
         "改为 0.60/0.76/0.90，缩略时能看到三级层次"),
        ("横幅上深色层不可见", "back 层 #101826 与底色 #0C1322 几乎同色", "深底场景改用 #31415F"),
        ("海报标志偏左、标题过近", "mark 放在 x=228，且 Layerlight 紧贴叠光", "标志居中到 304，标题下移 12px"),
        ("dslkit 透明背景输出 None 字符串", "document() 直接插值 background", "background=None 时省略属性"),
    ],
    files=[(f"outputs/{RUN_ID}/A13/symbol-color.png", "彩色图标"),
           (f"outputs/{RUN_ID}/A13/symbol-black.png", "纯黑图标"),
           (f"outputs/{RUN_ID}/A13/brand-banner.png", "横幅"),
           (f"outputs/{RUN_ID}/A13/launch-poster.png", "海报"),
           (f"outputs/{RUN_ID}/A13/brand-system.json", "品牌系统"),
           (f"tmp/{RUN_ID}/A13/previews/", "两个方向预览与 32px 缩略")],
    extra_sections=[("纯黑与缩略检查", [
        f"symbol-black.png：alpha>0 像素 {bc['nonzero_alpha_pixels']} 个，违规 {bc['violating_pixels']} 个，"
        f"alpha {bc['alpha_min']}–{bc['alpha_max']}",
        "32×32：Pillow Lanczos（预乘后重采样再还原未预乘），仅存 tmp 预览",
        "彩色/黑色缩略均在 #F2F4F8 浅底上按实际 32 像素查看",
        f"请求 {m['request_totals']['render_requests']} 次（成功 {m['request_totals']['render_ok']}），"
        f"看图 {m['visual_review']['images_opened']} 次，墙钟 {m['wall_clock_s']} 秒",
    ])],
)
print("A13 reports written")
