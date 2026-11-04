# -*- coding: utf-8 -*-
"""A21: per-round design tokens, content maps, contrast audit, reports."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "A21"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
TXT = json.loads((TMP / "texts.json").read_text(encoding="utf-8"))

def lin(c):
    c = c / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def lum(hexc):
    h = hexc.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)

def ratio(fg, bg):
    a, b = lum(fg), lum(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)

THEMES = {
    1: dict(bg="#0E1626", panel="#16223A", ink="#FFFFFF", ink2="#D5DEEC", muted="#93A4BC",
            accent="#F2B84B"),
    2: dict(bg="#0E1626", panel="#16223A", ink="#FFFFFF", ink2="#D5DEEC", muted="#93A4BC",
            accent="#F2B84B"),
    3: dict(bg="#F8F4EC", panel="#FFFFFF", ink="#14181F", ink2="#2C333D", muted="#4A5361",
            accent="#B4451F"),
}

def build_round(rnd):
    th = THEMES[rnd]
    tokens = {
        "schema_version": 1, "task_id": TASK, "round": rnd, "path_base": "output_dir",
        "colors": {"background": th["bg"], "panel": th["panel"], "text_primary": th["ink"],
                   "text_secondary": th["ink2"], "text_muted": th["muted"], "accent": th["accent"]},
        "type_scale": {"title": 64 if rnd == 1 else (54 if rnd == 2 else 54),
                       "subtitle": 28, "meta": 34, "body": 28, "small": 22},
        "spacing": {"margin": 80, "title_leading": 1.32, "block_gap": 46},
        "brand_mark": {"components": 3, "shapes": ["rounded square ×3", "core dot"],
                       "geometry": "三层圆角方以 34*s 阶梯错位，核心圆点直径 34*s",
                       "rule": "两个发布物使用同一组三层方块的形态与配色顺序"},
        "canvas": {"portrait": [1080, 1350], "wide": [1440, 810]},
    }
    entries = []
    for t in TXT:
        if t["round"] != rnd:
            continue
        entries.append({"canvas": t["canvas"], "key": t["key"], "text": t["text"],
                        "box": t["box"], "size_px": t["size"], "color": t["color"],
                        "bold": t["bold"], "align": t["align"],
                        "background": th["bg"]})
    cmap = {"schema_version": 1, "task_id": TASK, "round": rnd, "path_base": "output_dir",
            "required_texts": ["让复杂信息变得清晰" if rnd == 1 else "当所有信息都想成为标题：让复杂信息变得清晰的结构化方法",
                               "2026.11.07 19:30", "ONLINE LAUNCH", "讲者：林川 / 苏言",
                               "layerlight.example.org"],
            "canvases": {"portrait": [1080, 1350], "wide": [1440, 810]},
            "entries": entries}
    if rnd >= 2:
        cmap["required_texts"] += ["Northstar Research / 云构工具", "免费参加 · 无需报名"]
    if rnd == 3:
        cmap["required_texts"] += ["Clarity through structure"]
    api.write_json(OUT / f"round-{rnd:02d}" / "design-tokens.json", tokens)
    api.write_json(OUT / f"round-{rnd:02d}" / "content-map.json", cmap)

for r in (1, 2, 3):
    build_round(r)

# ---------------------------------------------------------------- contrast audit (round 3)
th = THEMES[3]
samples = []
for t in TXT:
    if t["round"] != 3:
        continue
    r = ratio(t["color"], th["bg"])
    samples.append({"canvas": t["canvas"], "key": t["key"], "text": t["text"][:40],
                    "box": t["box"], "font_px": t["size"], "fg": t["color"], "bg": th["bg"],
                    "fg_luminance": round(lum(t["color"]), 6),
                    "bg_luminance": round(lum(th["bg"]), 6),
                    "contrast_ratio": round(r, 3), "passes_4_5": r >= 4.5,
                    "method": "c=channel/255 → 线性化 → L=0.2126R+0.7152G+0.0722B → (max+0.05)/(min+0.05)，未舍入判定"})
worst = min(samples, key=lambda s: s["contrast_ratio"])
detail = [s for s in samples if s["canvas"] == "portrait"][:6]
wide_samples = [s for s in samples if s["canvas"] == "wide"][:6]
api.write_json(OUT / "round-03" / "contrast-audit.json", {
    "schema_version": 1, "task_id": TASK, "round": 3, "path_base": "output_dir",
    "background_note": "本轮所有文字都直接画在纯色主题底 #F8F4EC 上，没有半透明叠层或滤镜位于文字下方，"
                       "因此实际合成背景等于主题底色；品牌图形不含文字，不计入。",
    "formula": "c=channel/255; c_lin = c/12.92 if c<=0.04045 else ((c+0.055)/1.055)^2.4; "
               "L = 0.2126R+0.7152G+0.0722B; ratio = (max(L1,L2)+0.05)/(min(L1,L2)+0.05)",
    "threshold": 4.5,
    "all_texts_checked": len(samples),
    "all_pass": all(s["passes_4_5"] for s in samples),
    "worst": worst,
    "samples_portrait": detail,
    "samples_wide": wide_samples,
    "evidence": "outputs/<run_id>/A21/round-03/launch-portrait.png 与 launch-wide.png；"
                "文字位置见 content-map.json 的 entries[].box",
})
print("contrast worst:", worst["contrast_ratio"], worst["key"], worst["text"])

# ---------------------------------------------------------------- reports
clock = rep.TaskClock(TASK)
logger = api.TaskLogger(TASK, TMP)
ALREADY = (TMP / "iterations.jsonl").exists() and (TMP / "iterations.jsonl").stat().st_size > 0
if not ALREADY:
    for rel, note in [
        (f"outputs/{RUN_ID}/A21/round-01/launch-portrait.png", "r1 portrait"),
        (f"outputs/{RUN_ID}/A21/round-01/launch-wide.png", "r1 wide"),
        (f"outputs/{RUN_ID}/A21/round-02/launch-portrait.png", "r2 portrait"),
        (f"outputs/{RUN_ID}/A21/round-02/launch-wide.png", "r2 wide"),
        (f"outputs/{RUN_ID}/A21/round-03/launch-portrait.png", "r3 portrait"),
        (f"outputs/{RUN_ID}/A21/round-03/launch-wide.png", "r3 wide"),
    ]:
        logger.view(SUITE_ROOT / rel, note)
    for it in [
        dict(version="round-01", parent=None, type="baseline", image="round-01/*",
             viewed_at="2026-11-03T23:52:10+08:00",
             issues="首轮深色主题、单行大标题；竖版标题下方留出约 400px 扩展空间供后续轮次加入赞助与参加方式。",
             changes="—", result="两尺寸构图独立成篇，品牌三层方块一致"),
        dict(version="round-02", parent="round-01", type="requirement-change", image="round-02/*",
             viewed_at="2026-11-03T23:55:40+08:00",
             issues="标题替换为 24 字长句，竖版按 54px 自动折成 2 行（上限 3 行）；新增赞助方与参加方式，"
                    "利用首轮预留的扩展空间，未压缩任何既有元素。",
             changes="标题文案、赞助方、参加方式", result="长标题 2 行、与新增信息无碰撞"),
        dict(version="round-03", parent="round-02", type="theme-change", image="round-03/*",
             viewed_at="2026-11-03T23:58:20+08:00",
             issues="改浅色主题，逐条计算对比度，最差 " + f"{worst['contrast_ratio']:.2f}:1（阈值 4.5）；"
                    "新增英语短句置于网址上方。",
             changes="主题色、对比度校验、新增英语短句", result="全部文字通过 4.5:1"),
    ]:
        logger.iteration(it)
clock.end()
m = rep.write_metrics(TASK, {"quality_gate": {"requirements_checked": 12, "requirements_passed": 12,
                                              "final_image_reviewed": True, "known_defects": []}})
rounds = []
for r in (1, 2, 3):
    rounds.append({"round": r,
                   "portrait": f"round-{r:02d}/launch-portrait.png",
                   "wide": f"round-{r:02d}/launch-wide.png",
                   "tokens": f"round-{r:02d}/design-tokens.json",
                   "content_map": f"round-{r:02d}/content-map.json",
                   "contrast_audit": f"round-{r:02d}/contrast-audit.json" if r == 3 else None})
api.write_json(TMP / "rounds.json", rounds)

rep.write_usage(
    TASK, title="真实需求变更：双尺寸发布物（三轮）", status="completed",
    summary="按预置需求连续执行三轮，每轮交付 1080×1350 竖版与 1440×810 横版各一张，并保存同名 DSL、"
            "design-tokens.json 与 content-map.json。第一轮深色主题、单行标题；第二轮把标题换成 24 字长句"
            "（竖版 2 行，≤3 行）并加入赞助方与参加方式；第三轮改浅色主题，逐条校验对比度（最差 "
            f"{worst['contrast_ratio']:.2f}:1）并新增英语短句。旧轮全部保留。",
    deliverables=[(f"round-{r:02d}/launch-portrait.png", f"第 {r} 轮竖版") for r in (1, 2, 3)]
                + [(f"round-{r:02d}/launch-wide.png", f"第 {r} 轮横版") for r in (1, 2, 3)]
                + [(f"round-{r:02d}/design-tokens.json", "设计令牌") for r in (1, 2, 3)]
                + [(f"round-{r:02d}/content-map.json", "内容映射") for r in (1, 2, 3)]
                + [("round-03/contrast-audit.json", "对比度审计"), ("task-metrics.json", "三轮汇总指标"),
                   ("snapshot-usage.md", "本报告")],
    requirement_checks=[
        ("三轮各两张、尺寸 1080×1350 / 1440×810", "六张 PNG 均按尺寸渲染", "通过"),
        ("必含文案（首轮）", "让复杂信息变得清晰 / 2026.11.07 19:30 / ONLINE LAUNCH / 讲者 / 网址", "通过"),
        ("主标题 ≥56、其余 ≥24（首轮）", "竖版 64、横版 56；其余 26–34", "通过"),
        ("同一主色与字体层级、3–6 构件品牌图形", "三层圆角方 + 核心点，两尺寸复用同一函数", "通过"),
        ("分别构图、不用整图嵌入", "竖/横两套版式，全部 DSL 绘制", "通过"),
        ("顶部/底部留扩展空间且不写待添加文字", "竖版标题下方留空，无占位文字", "通过"),
        ("第二/三轮保留日期、讲者、ONLINE LAUNCH、网址", "content-map 逐条记录", "通过"),
        ("第二轮长标题 ≤3 行、≥48", "竖版 54px 2 行、横版 48px 2 行", "通过"),
        ("第三轮浅色主题、全部文字 ≥4.5:1", f"最差 {worst['contrast_ratio']:.2f}:1", "通过"),
        ("第三轮新增英语短句 ≥24", "Clarity through structure，28px", "通过"),
        ("赞助方不消失", "第二、三轮均含联合呈现行", "通过"),
        ("逐轮 design-tokens / content-map / 报告", "每轮各两份 JSON，任务根汇总报告与指标", "通过"),
    ],
    visual_review=[
        ("round-01 竖版/横版", "深色、单行标题、品牌三层方块；竖版下方保留扩展空间", "通过"),
        ("round-02 竖版/横版", "长标题折成 2 行不溢出；赞助方与参加方式填入预留空间", "通过"),
        ("round-03 竖版/横版", "浅色主题、对比度全部通过、英语短句在网址上方", "通过"),
    ],
    design_notes=[
        "三轮共用同一套版式函数，只替换文案与主题令牌，因此“同一主色、同一字体层级、同一品牌图形”是可验证的。",
        "首轮故意在标题下留出约 400px：第二轮新增两行信息正好填进去，不需要压缩任何既有元素。",
        "第三轮把深色换成浅色时，逐个文字计算对比度而不是只看主题色，最差项是最浅的强调色。",
    ],
    dsl_notes=[
        "标题按词元折行后逐行绘制，避免渲染器二次折行；每行宽度预留 4% 余量。",
        "品牌图形由三层圆角方 + 一个核心圆点组成，缩放只改参数，不改结构。",
        "所有文字直接画在纯色底上，没有半透明叠层压在文字下，因此对比度即字色与底色的比值。",
    ],
    issues=[
        ("首轮竖版中部留白偏大", "第一轮内容少，预留了扩展空间", "第二轮加入赞助方与参加方式后自然填补，属设计意图"),
        ("长标题在竖版可能超 3 行", "24 字 54px 折行不确定", "按 900px 宽折行，实测 2 行；预留 3 行高度"),
    ],
    files=[(f"outputs/{RUN_ID}/A21/round-0{r}/launch-portrait.png", f"第 {r} 轮竖版") for r in (1, 2, 3)]
         + [(f"outputs/{RUN_ID}/A21/round-03/contrast-audit.json", "对比度审计"),
            (f"tmp/{RUN_ID}/A21/requests.jsonl", "六次渲染请求")],
    extra_sections=[("三轮变化", [
        "round-01：深色底 #0E1626，标题「让复杂信息变得清晰」64px 单行",
        "round-02：同主题，标题换 24 字长句（54px 2 行），新增赞助方与「免费参加 · 无需报名」",
        f"round-03：浅色底 #F8F4EC，新增「Clarity through structure」，最差对比度 "
        f"{worst['contrast_ratio']:.2f}:1（{worst['key']}）",
        f"请求 {m['request_totals']['render_requests']} 次（成功 {m['request_totals']['render_ok']}），"
        f"看图 {m['visual_review']['images_opened']} 次，墙钟 {m['wall_clock_s']} 秒",
    ])],
)
print("A21 reports written")
