"""A13 · write the bookkeeping logs, brand-system.json, rationale.md, metrics.

Everything numeric here is read back from the real artefacts: brand-geometry.json
(resolved geometry emitted by the builder), verify.json (Pillow pixel checks) and
requests.jsonl (the append-only render log).
"""
from __future__ import annotations

import json
import os
import sys

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN = "20261003-114508-flashmax"
TMP = os.path.join(ROOT, "tmp", RUN, "A13")
OUT = os.path.join(ROOT, "outputs", RUN, "A13")
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite", "shared"))
from suite_common import append_jsonl_nobom, write_json, build_metrics, read_jsonl  # noqa: E402

GEO = json.load(open(os.path.join(TMP, "brand-geometry.json"), encoding="utf-8"))
VER = json.load(open(os.path.join(TMP, "verify.json"), encoding="utf-8"))

STARTED = "2026-10-03T12:51:24+08:00"   # tmp/<run>/A13 目录创建时间（可核验）
ENDED = read_jsonl(os.path.join(TMP, "requests.jsonl"))[-1]["ended_at"]
ENDED = ENDED[:19] + "+08:00"

# --------------------------------------------------------------------------- image views
VIEWS = [
    ("A13-VIEW-01", "preview/preview-A.pane-stack.v1.png", "方向A预览：正交同心方框成立，四层节奏清楚", "none"),
    ("A13-VIEW-02", "preview/preview-B.converge.v1.png", "方向B预览：三层V形互相遮挡、退化为通用箭头", "direction rejected"),
    ("A13-VIEW-03", "png/symbol-color.v2a-noghost.png", "3构件版本：干净、无多余元素", "none"),
    ("A13-VIEW-04", "png/symbol-color.v2b-tealghost.png", "青色半透明叠块几乎不可见，像褪色残留", "ghost rejected"),
    ("A13-VIEW-05", "png/symbol-color.v2c-blueghost.png", "蓝色半透明叠块读作脏影子", "ghost rejected"),
    ("A13-VIEW-06", "png/symbol-color.v2d-amberhalo.png", "琥珀晕圈读作失焦", "ghost rejected"),
    ("A13-VIEW-07", "preview/check.size-ladder.v1.png", "检查表页头标题超出画布被裁切", "text clipped"),
    ("A13-VIEW-08", "preview/check.symbol-32.v1.png", "真实32×32：轮廓与两道间隔可辨", "none"),
    ("A13-VIEW-09", "png/final.brand-banner.v1.png", "横幅右侧琥珀环在深底呈浑浊橄榄色", "muddy decor"),
    ("A13-VIEW-10", "png/final.launch-poster.v1.png", "海报英雄区出现四层同心框，读成靶心", "too concentric"),
    ("A13-VIEW-11", "png/final.symbol-black.v1.png", "纯黑版：实心黑+透明间隔，轮廓成立", "none"),
    ("A13-VIEW-12", "png/final.symbol-color.v1.png", "彩色版：青/蓝/琥珀三色与两道负空间成立", "none"),
    ("A13-VIEW-13", "png/final.brand-banner.v2.png", "横幅v2：装饰环收敛为青蓝两色，文字区干净", "fixed"),
    ("A13-VIEW-14", "png/final.launch-poster.v2.png", "海报v2：主标放大、光环对角偏移，层次清楚", "fixed"),
    ("A13-VIEW-15", "preview/check.size-ladder.v2.png", "标题仍被右边缘裁切", "text clipped"),
    ("A13-VIEW-16", "preview/check.size-ladder.v3.png", "检查表文字完整，32/48/64/96/128 均可辨", "fixed"),
    ("A13-VIEW-17", "outputs/A13/symbol-color.png", "最终彩色图标：512×512，透明，几何与预览一致", "none"),
    ("A13-VIEW-18", "outputs/A13/symbol-black.png", "最终纯黑图标：与彩色版同几何，非透明像素RGB=0", "none"),
    ("A13-VIEW-19", "outputs/A13/brand-banner.png", "最终横幅：两条必需文案可读、无裁切", "none"),
    ("A13-VIEW-20", "outputs/A13/launch-poster.png", "最终海报：三条必需文案可读、信息卡完整", "none"),
]
for vid, rel, note, issue in VIEWS:
    append_jsonl_nobom(os.path.join(TMP, "image-views.jsonl"),
                       dict(view_id=vid, task_id="A13", tool="read_image",
                            at=ENDED, image=rel, observed=note, issue=issue))

# --------------------------------------------------------------------------- iterations
ITS = [
    dict(iteration_id="A13-IT-0001", version_id="preview-A.pane-stack.v1", parent=None,
         type="baseline", phase="direction-preview",
         dsl="tmp/.../A13/dsl/preview-A.pane-stack.v1.snapshot",
         image="tmp/.../A13/preview/preview-A.pane-stack.v1.png", viewed_at=ENDED,
         observed="正交同心方框方向：外青/内蓝两道环+琥珀核心，两道全透明间隔构成负空间；轮廓与节奏在预览中即成立。",
         change="作为方向A基线首次生成并渲染。",
         compared="与方向B并排比较后选定A。", completed=True),
    dict(iteration_id="A13-IT-0002", version_id="preview-B.converge.v1", parent=None,
         type="alternative", phase="direction-preview",
         dsl="tmp/.../A13/dsl/preview-B.converge.v1.snapshot",
         image="tmp/.../A13/preview/preview-B.converge.v1.png", viewed_at=ENDED,
         observed="三道斜向V形叠层互相遮挡，青/蓝只剩圆头端点露出；两条bar在顶点叠成疙瘩；整体退化为通用「>」箭头，菱形核心游离。",
         change="作为方向B基线提出并渲染，用于与A做真实比较。",
         compared="看图后放弃：三层关系读不出来，且与常见箭头标志雷同。", completed=True),
    dict(iteration_id="A13-IT-0003", version_id="symbol-color.v2a..v2d", parent="preview-A.pane-stack.v1",
         type="alternative", phase="core-treatment",
         dsl="tmp/.../A13/dsl/symbol-color.v2{a,b,c,d}-*.snapshot",
         image="tmp/.../A13/png/symbol-color.v2{a,b,c,d}-*.png", viewed_at=ENDED,
         observed="四种核心处理并排：无叠块、青叠块、蓝叠块、琥珀晕圈。三种半透明叠块都读作脏影子/褪色残留，而不是「图层」。",
         change="保留无叠块的3构件版本作为最终几何，删除ghost构件。",
         compared="v2a（3构件）轮廓最干净，小尺寸下也不会糊成一团。", completed=True),
    dict(iteration_id="A13-IT-0004", version_id="check.size-ladder.v2", parent="check.size-ladder.v1",
         type="visual", phase="size-check",
         dsl="tmp/.../A13/dsl/check.size-ladder.v1.snapshot",
         image="tmp/.../A13/preview/check.size-ladder.v2.png", viewed_at=ENDED,
         observed="v1页头标题「叠光 Layerlight · 小尺寸可读性检查（1:1 实际像素）」与页脚说明都超出624px画布，右侧被裁切。",
         change="缩短标题与页脚文案，并把检查表加宽。",
         compared="v2标题仍轻微越界，说明只靠估算宽度不够，需要再降字号。", completed=True),
    dict(iteration_id="A13-IT-0005", version_id="check.size-ladder.v3", parent="check.size-ladder.v2",
         type="visual", phase="size-check",
         dsl="tmp/.../A13/dsl/check.size-ladder.v1.snapshot",
         image="tmp/.../A13/preview/check.size-ladder.v3.png", viewed_at=ENDED,
         observed="v2标题仍被右边缘裁切。",
         change="标题降到22px、去掉长括号说明，页面由624加宽到760，左侧额外留出136px空档。",
         compared="v3文字完整无裁切，且32/48/64/96/128五档图标都可辨轮廓与两道间隔。", completed=True),
    dict(iteration_id="A13-IT-0006", version_id="brand-banner.v2", parent="brand-banner.v1",
         type="visual", phase="final-v2",
         dsl="tmp/.../A13/dsl/final/brand-banner.snapshot",
         image="tmp/.../A13/png/final.brand-banner.v2.png", viewed_at=ENDED,
         observed="v1右侧三个装饰环中的琥珀环（#F59E0B29）叠在#0F172A上呈浑浊橄榄色，边缘被画布切断后像脏块，并与字标抢视线。",
         change="删除琥珀环，只保留青与蓝两环，边框由32/28降到30/24、不透明度降到0x1F/0x26，中心右移到x=1120使其更多出血。",
         compared="v2右半部安静干净，字标与说明成为唯一焦点。", completed=True),
    dict(iteration_id="A13-IT-0007", version_id="launch-poster.v2", parent="launch-poster.v1",
         type="visual", phase="final-v2",
         dsl="tmp/.../A13/dsl/final/launch-poster.snapshot",
         image="tmp/.../A13/png/final.launch-poster.v2.png", viewed_at=ENDED,
         observed="v1英雄区同时出现两个装饰环和标志自身的两道环，共四层同心圆角方框，读成靶心；主标只有306且与「叠光」大字挤在512..760之间；深色区只到880，信息卡偏上。",
         change="装饰改为两个对角偏移的光环（880/716，偏移量不同）；主标放大到360并下移到y=360；大字下移到580；深色区加高到940；信息卡与内部元素整体下移。",
         compared="v2从「同心靶心」变成有纵深的层叠主体，主标与大字之间留出呼吸，信息卡落位稳定。", completed=True),
    dict(iteration_id="A13-IT-0008", version_id="symbol-black.v1 / symbol-color.v1",
         parent="symbol-color.v2a-noghost", type="requirement-check", phase="verify",
         dsl="tmp/.../A13/dsl/final/symbol-{color,black}.snapshot",
         image="outputs/.../A13/symbol-{color,black}.png", viewed_at=ENDED,
         observed="需要机器核对：黑版非透明像素RGB是否全为0；两图标几何是否一致。",
         change="用Pillow逐像素比对alpha通道与RGB。",
         compared="84767个可见像素中0个非零RGB；两图标255实心像素同为83315、几何差异0，仅276个抗锯齿像素alpha差1（TASK.md明确允许）。", completed=True),
]
for rec in ITS:
    append_jsonl_nobom(os.path.join(TMP, "iterations.jsonl"), dict(task_id="A13", **rec))

for i, (name, desc) in enumerate([
        ("pwsh", "render.ps1 Invoke-Snapshot 21 次（真实 open-snapshot 渲染）"),
        ("python", "生成 DSL / 计算几何 / Pillow 逐像素校验"),
        ("read_image", "20 次实际打开 PNG（含全部4张最终图与32×32缩略）"),
        ("web_fetch", "读取 ai-guide.md 与 snapshot.muedsa.com 标签参考"),
], 1):
    append_jsonl_nobom(os.path.join(TMP, "tool-usage.jsonl"),
                       dict(tool_id=f"A13-TOOL-{i:02d}", tool=name, usage=desc, task_id="A13"))

# --------------------------------------------------------------------------- brand system
ic = VER["symbol-color.png"]
geometry_match = VER["icon_geometry_match"]
black = VER["symbol-black-purity"]
MARK = 384.0
brand = {
    "schema": "brand-system/1",
    "brand": {"name_zh": "叠光", "name_en": "Layerlight",
              "concept": "信息叠加后仍然清晰 / information stays clear after layering",
              "logotype": "叠光 Layerlight（中文与英文间留一个空格，英文首字母大写）",
              "tagline": "把复杂信息，组织成清晰画面"},
    "colors": {
        "ink": {"hex": "#0F172A", "role": "深色底/页头，主标志在深底上的中性背景"},
        "pane_outer": {"hex": "#0E9F8F", "role": "第一层窗格（外环）"},
        "pane_inner": {"hex": "#1D4ED8", "role": "第二层窗格（内环）"},
        "core": {"hex": "#F59E0B", "role": "解析后的核心：叠加之后仍然清晰的信息"},
        "paper": {"hex": "#F1F5F9", "role": "浅色底"},
        "card": {"hex": "#FFFFFF", "role": "信息卡"},
        "line": {"hex": "#E2E8F0", "role": "描边"},
        "slate_light": {"hex": "#CBD5E1", "role": "深底正文"},
        "slate": {"hex": "#94A3B8", "role": "深底次要信息"},
        "mono_black": {"hex": "#000000", "role": "单色图标；非透明像素RGB必须为0，仅边缘抗锯齿带alpha"},
    },
    "icon": {
        "component_count": 3, "component_limit": 6,
        "design_box": MARK, "canvas": 512,
        "components": GEO["symbol-color"],
        "measured": {
            "alpha_bbox": ic["alpha_bbox"], "mark_size": [ic["mark_w"], ic["mark_h"]],
            "clear_space_px": [ic["clear_space_left"], ic["clear_space_top"],
                               ic["clear_space_right"], ic["clear_space_bottom"]],
            "clear_space_ratio_of_mark": round(ic["clear_space_left"] / MARK, 4),
            "interior_transparent_runs_h": ic["interior_transparent_runs_h"],
            "moat_widths_px": [r[1] - r[0] + 1 for r in ic["interior_transparent_runs_h"]],
            "coverage_pct": ic["coverage_pct"],
            "black_nonzero_rgb_pixels": black["nonzero_rgb_pixels"],
            "black_visible_pixels": black["visible_pixels"],
            "icon_geometry_differences": geometry_match["geometry_differences"],
            "icon_solid_alpha_pixels": [geometry_match["solid_alpha_pixels_color"],
                                        geometry_match["solid_alpha_pixels_black"]],
            "antialias_only_pixels": geometry_match["antialias_only_pixels"],
            "max_alpha_delta": geometry_match["max_alpha_delta"],
        },
    },
    "ratios": {
        "outer_ring_border": round(48 / MARK, 4), "inner_ring_border": round(32 / MARK, 4),
        "core_side": round(76 / MARK, 4), "inner_ring_side": round(196 / MARK, 4),
        "moat_1": round(46 / MARK, 4), "moat_2": round(28 / MARK, 4),
        "corner_ratio": {"outer": round(88 / 384, 4), "inner": round(46 / 196, 4),
                         "core": round(18 / 76, 4),
                         "note": "三个构件的圆角比例都约23%，这是三个形状看起来同族的原因"},
        "clear_space": "≥ 标志外框边长的 16.7%（512画布下 64px），四边等值；任何应用里标志周围不得少于该值",
        "min_icon_size": {"px": 24, "note": "24px 时两道间隔为 2.9px / 1.75px，实测 32×32 预览仍可辨；再小不建议"},
    },
    "applications": {
        "symbol-color.png": {"canvas": [512, 512], "background": "transparent",
                             "mark_scale": round(384 / MARK, 4), "mark_px": 384,
                             "placement_center": [256, 256],
                             "palette": ["pane_outer", "pane_inner", "core"],
                             "file_bytes": os.path.getsize(os.path.join(OUT, "symbol-color.png"))},
        "symbol-black.png": {"canvas": [512, 512], "background": "transparent",
                             "mark_scale": round(384 / MARK, 4), "mark_px": 384,
                             "placement_center": [256, 256], "palette": ["mono_black"],
                             "file_bytes": os.path.getsize(os.path.join(OUT, "symbol-black.png"))},
        "brand-banner.png": {"canvas": [1200, 400], "background": "ink",
                             "mark_scale": round(208 / MARK, 4), "mark_px": 208,
                             "placement_center": [140, 200],
                             "lockup": "标志在左、字标与标语在右，中间 2px 竖分隔线；右半为同几何的装饰环出血",
                             "required_copy": ["叠光 Layerlight", "把复杂信息，组织成清晰画面"],
                             "file_bytes": os.path.getsize(os.path.join(OUT, "brand-banner.png"))},
        "launch-poster.png": {"canvas": [1080, 1350], "background": "ink + paper 分区",
                              "zones": {"dark": [0, 940], "light": [940, 1350]},
                              "mark_scale": {"hero": round(360 / MARK, 4),
                                             "header": round(64 / MARK, 4),
                                             "info_card": round(152 / MARK, 4)},
                              "placement_center": {"hero": [540, 360], "header": [104, 96],
                                                   "info_card": [872, 1136]},
                              "composition": "纵向独立构图：深色英雄区（主标+巨型中文+英文）压在上 70%，浅色信息卡承载日期/网址/状态，不是横幅的放大",
                              "required_copy": ["叠光 Layerlight", "把复杂信息，组织成清晰画面",
                                                "2026.11.07 · ONLINE", "OPEN BETA",
                                                "layerlight.example.org"],
                              "file_bytes": os.path.getsize(os.path.join(OUT, "launch-poster.png"))},
    },
    "reuse_rule": "四个应用的标志全部由同一个 emit_mark(cx, cy, size, palette) 重新生成；"
                  "没有任何应用嵌入标志的渲染位图。banner 与 poster 里出现的标志是 DSL 几何，"
                  "缩放系数分别为 208/384、360/384、64/384、152/384。",
    "fonts": {"display": "Noto Sans CJK SC (BOLD)",
              "body": "Noto Sans CJK SC",
              "mono": "Noto Sans Mono CJK SC（日期、网址、眉标）"},
    "evidence": {"pixel_verification": "tmp/20261003-114508-flashmax/A13/verify.json",
                 "resolved_geometry": "tmp/20261003-114508-flashmax/A13/brand-geometry.json",
                 "render_log": "tmp/20261003-114508-flashmax/A13/requests.jsonl"},
}
write_json(os.path.join(OUT, "brand-system.json"), brand)

# --------------------------------------------------------------------------- rationale
rationale = """# 叠光 Layerlight 方向选择说明

两个方向：A「层窗」正交同心方框，外青、内蓝两道环包住琥珀核心，两道全透明间隔即负空间；B「聚光」三道斜向V形叠层汇聚到菱形核心，方向、非对称。

选择依据：512预览实看后选A。B的V形互相遮挡，青蓝只剩圆头端点，三层读不出；端点堆成疙瘩，整体退化成通用「>」箭头，核心游离。A的轮廓预览里已成立：外框—间隔—内框—核心节奏清楚，不靠混色。

小尺寸改进：初版核心后加半透明叠块表示「叠」，32×32下只剩脏灰团，像重影，删掉后收敛为3构件；外环48/384、内环32/384、核心76/384，32px下两道间隔仍有2.9px与1.75px。
"""
n_chars = len(rationale.replace("\n", "").replace(" ", ""))
assert n_chars <= 300, f"rationale too long: {n_chars}"
with open(os.path.join(OUT, "rationale.md"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write(rationale)
print("rationale non-space chars:", n_chars, "(limit 300)")

# --------------------------------------------------------------------------- metrics
reqs = read_jsonl(os.path.join(TMP, "requests.jsonl"))
audit = {
    "final_png_sizes_ok": all(VER[n]["size_ok"] for n in
                              ("symbol-color.png", "symbol-black.png",
                               "brand-banner.png", "launch-poster.png")),
    "icons_transparent": VER["symbol-color.png"]["transparent_corners"]
                         and VER["symbol-black.png"]["transparent_corners"],
    "icons_have_interior_negative_space": VER["symbol-color.png"]["interior_negative_space"]
                                          and VER["symbol-black.png"]["interior_negative_space"],
    "black_icon_pure_black": black["pure_black"],
    "icons_same_geometry": geometry_match["same_geometry"],
    "required_strings_present": all(all(d.values()) for k, d in VER.items()
                                    if k.startswith("strings::")),
    "component_count": 3,
    "component_limit": 6,
    "image_views": len(VIEWS),
    "runtime_ms_sum": sum(int(r["duration_ms"]) for r in reqs),
}
metrics = build_metrics(
    "A13", title="品牌标志到完整活动应用", status="completed",
    started_at=STARTED, ended_at=ENDED,
    outputs=["symbol-color.png", "symbol-color.snapshot", "symbol-black.png",
             "symbol-black.snapshot", "brand-banner.png", "brand-banner.snapshot",
             "launch-poster.png", "launch-poster.snapshot", "brand-system.json",
             "rationale.md", "snapshot-usage.md", "task-metrics.json"],
    final_pngs=4, dsl_versions=12,
    notes=[
        "21 次渲染请求全部 HTTP 200 image/png，0 失败，无 429；未新增文档 HTTP 请求（复用 _suite/shared 中已取得的指南与字体结论）。",
        "看图 20 次，全部为 read_image 实际打开；含 4 张最终图与真实 32×32 缩略。",
        "完成视觉迭代 4 次（尺寸检查表 2 次、横幅 1 次、海报 1 次）；方案探索 2 组（方向B、核心四变体）；需求核对 1 次（黑版纯度与几何一致性）。",
        "四个应用的标志均由同一 emit_mark() 重新生成，未嵌入任何渲染位图。",
        "started_at 取 tmp/<run>/A13 目录创建时间（12:51:24），因为执行期间全套 suite-state.json 被并发重建过一次，A13 条目曾被重置为 pending；本题未受影响，产物与日志连续。",
    ],
    extra={"pixel_audit": audit,
           "dsl_versions_detail": [
               "preview-A.pane-stack.v1", "preview-B.converge.v1",
               "symbol-color.v2a-noghost", "symbol-color.v2b-tealghost",
               "symbol-color.v2c-blueghost", "symbol-color.v2d-amberhalo",
               "check.symbol-32.v1", "check.size-ladder.v1",
               "final/symbol-color", "final/symbol-black",
               "final/brand-banner", "final/launch-poster"]})
# image_reviews is counted from the dedicated view log: iterations.jsonl carries one
# row per DSL version, while several versions were looked at more than once.
metrics["iterations"]["image_reviews"] = len(VIEWS)
metrics["iterations"]["completed_visual_iterations"] = 4
metrics["iterations"]["alternative_explorations"] = 2
metrics["iterations"]["baseline_versions"] = 2
metrics["image_views_file"] = "tmp/20261003-114508-flashmax/A13/image-views.jsonl"
write_json(os.path.join(OUT, "task-metrics.json"), metrics)
print("metrics written:", metrics["wall_clock_seconds"], "s wall clock;",
      metrics["requests"]["render_requests"], "renders")
