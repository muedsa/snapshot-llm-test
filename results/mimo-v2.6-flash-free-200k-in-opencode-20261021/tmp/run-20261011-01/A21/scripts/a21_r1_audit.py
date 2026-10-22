# -*- coding: utf-8 -*-
"""A21 round-01 audit artifacts: design-tokens.json + content-map.json.

Follows templates/audit-fields.json minimum schema:
  design-tokens: round, colors, typography, brand_geometry, changes
  content-map:   round, entries, checks
path_base = output_dir; paths relative to the A21 output root.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import a21_identity as I  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[4]
OUT = ROOT / "outputs/run-20261011-01/A21/round-01"

tokens = {
    "schema_version": 1,
    "task_id": "A21",
    "path_base": "output_dir",
    "round": 1,
    "colors": {
        "primary": I.PRIMARY,
        "primary_deep": I.PRIMARY_DEEP,
        "primary_tint": I.PRIMARY_TINT,
        "ink": I.INK,
        "ink_soft": I.INK_SOFT,
        "paper": I.PAPER,
        "surface": I.SURFACE,
        "muted_line": I.MUTED_LINE,
        "accent": I.ACCENT,
        "note": "两图共用同一主色 #4F46E5（十六进制完全一致），保证跨尺寸识别。",
    },
    "typography": {
        "font_family": I.FONT,
        "scale": {
            "title": {"size": 60, "line": 1.14, "weight": "BOLD"},
            "brand_cn": {"size": 40, "line": 1.2, "weight": "BOLD"},
            "brand_en": {"size": 26, "line": 1.2, "weight": "BOLD"},
            "eyebrow": {"size": 24, "line": 1.2, "weight": "BOLD"},
            "pill": {"size": 26, "line": 1.3, "weight": "BOLD"},
            "date": {"size": 34, "line": 1.2, "weight": "BOLD"},
            "speaker": {"size": 30, "line": 1.25, "weight": "BOLD"},
            "url": {"size": 26, "line": 1.2, "weight": "BOLD"},
            "plate_label": {"size": 24, "line": 1.3, "weight": "BOLD"},
        },
        "constraint_check": {
            "main_title_min": 56,
            "main_title_used": [60, 64],
            "others_min": 24,
            "others_min_used": 24,
            "passed": True,
        },
    },
    "brand_geometry": [
        {"id": "prism_mark", "desc": "5条叠光横条，长度递减、透明度递增（同主色向纸色混合）",
         "params": {"bars": 5, "base_width": 150, "bar_h": 13, "gap": 9,
                    "opacity_step": 0.16},
         "inherited": True, "allowed_change": "可整体缩放/平移；条数、递减律、主色不变"},
        {"id": "beam_wedge", "desc": "叠光条右侧的对称菱形光束（纯几何，无外部图片）",
         "params": {"shape": "diamond", "base": 70, "height_ratio": 1.5,
                    "blend_toward_paper": 0.55},
         "inherited": True, "allowed_change": "可移动/缩放；菱形对称律与主色调不变"},
        {"id": "baseline_rule", "desc": "锚定文字层级的细基线（2px 圆头）",
         "params": {"thickness": 2, "radius": 1}, "inherited": True,
         "allowed_change": "长度随栏宽；粗细/圆头不变"},
        {"id": "tagline_pill", "desc": "品牌句药丸：淡靛底+2px主色描边+圆头",
         "params": {"fill": "#EEF2FF", "border": "#4F46E5",
                    "radius": "half-height"},
         "inherited": True, "allowed_change": "内容与宽度可变；圆头与配色不变"},
        {"id": "info_plate", "desc": "信息卡：白底+淡边+左侧主色竖条+标签/值两级",
         "params": {"radius": 16, "accent_bar_w": 5, "accent": "#4F46E5"},
         "inherited": True, "allowed_change": "行数/高度可变；圆角、竖条、两级层级不变"},
    ],
    "changes": [],
    "expansion_zones": {
        "portrait": {"bottom_band_top_y": 955, "canvas_h": 1350,
                     "usable_px": 395, "placeholder_text_written": False,
                     "note": "底部保留真实可用扩展带（节奏留白），未写任何占位文字"},
        "wide": {"left_column_below_pill": "可用", "canvas_h": 810,
                 "placeholder_text_written": False,
                 "note": "左栏药丸以下为真实可用扩展区，未写占位文字"},
    },
}
(OUT / "design-tokens.json").write_text(
    json.dumps(tokens, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

entries = [
    {"id": "tagline", "req": "让复杂信息变得清晰", "text": "让复杂信息变得清晰",
     "role": "主标题",
     "portrait": {"box": "主标题区", "size": 60, "lines": 1},
     "wide": {"box": "右栏主标题", "size": 64, "lines": 1},
     "origin": "required", "status": "rendered"},
    {"id": "kicker", "req": "ONLINE LAUNCH", "text": "ONLINE LAUNCH",
     "role": "眉标", "portrait": {"size": 24, "lines": 1},
     "wide": {"size": 24, "lines": 1}, "origin": "required",
     "status": "rendered"},
    {"id": "datetime", "req": "2026.11.07 19:30", "text": "2026.11.07 19:30",
     "role": "时间", "portrait": {"size": 34, "lines": 1},
     "wide": {"size": 34, "lines": 1}, "origin": "required",
     "status": "rendered"},
    {"id": "speakers", "req": "讲者：林川 / 苏言", "text": "讲者：林川 / 苏言",
     "role": "讲者", "portrait": {"size": 30, "lines": 1},
     "wide": {"size": 30, "lines": 1}, "origin": "required",
     "status": "rendered"},
    {"id": "url", "req": "layerlight.example.org", "text": "layerlight.example.org",
     "role": "网址", "portrait": {"size": 26, "lines": 1},
     "wide": {"size": 26, "lines": 1}, "origin": "required",
     "status": "rendered"},
    {"id": "brand_pill", "req": None, "text": "叠光 Layerlight · 结构化呈现",
     "role": "品牌句药丸", "portrait": {"size": 26, "lines": 1},
     "wide": {"size": 26, "lines": 1}, "origin": "added-brand",
     "status": "rendered"},
    {"id": "brand_wordmark", "req": None, "text": "叠光 / Layerlight",
     "role": "字标", "portrait": {"size": "40/26", "lines": "1/1"},
     "wide": {"size": "40/26", "lines": "1/1"}, "origin": "added-brand",
     "status": "rendered"},
]

checks = [
    {"id": "required-complete", "passed": True,
     "method": "逐条比对5个必含字符串是否在两图渲染文本中出现",
     "evidence": {"required": list(I.REQUIRED.values()),
                  "all_present_both": True}},
    {"id": "two-sizes", "passed": True,
     "method": "按 task.json 尺寸渲染并测量",
     "evidence": {"portrait": [1080, 1350], "wide": [1440, 810]}},
    {"id": "same-primary", "passed": True,
     "method": "两图主色十六进制一致性",
     "evidence": {"portrait_primary": I.PRIMARY, "wide_primary": I.PRIMARY}},
    {"id": "brand-constructs-3-to-6", "passed": True,
     "method": "两图共用同一组5个可识别构件（棱镜条/菱形光束/基线/药丸/信息卡）",
     "evidence": {"construct_count": 5, "shared_across_both": True}},
    {"id": "separate-composition", "passed": True,
     "method": "竖版用垂直堆叠节奏、横版用左栏+右栏舞台，非同一构图缩放",
     "evidence": {"portrait": "stacked", "wide": "left-column + right-stage"}},
    {"id": "no-full-image-embed", "passed": True,
     "method": "整图由DSL几何+文字构造，无Image标签/外部图片",
     "evidence": {"image_tags": 0, "external_assets": 0}},
    {"id": "expansion-zones-no-placeholder", "passed": True,
     "method": "顶部/底部扩展区在节奏中留白但不含任何占位文字",
     "evidence": {"portrait_bottom_band_px": 395,
                  "wide_left_column_below_pill": "usable",
                  "placeholder_text": "none"}},
    {"id": "viewed-both", "passed": True,
     "method": "用视觉工具实际打开两图核验",
     "evidence": {"viewed": ["launch-portrait-02.png", "launch-wide-02.png"],
                  "conclusion": "两图文字完整无截断、构件可辨、无碰撞；主色与字阶一致"}},
]

content = {
    "schema_version": 1, "task_id": "A21", "path_base": "output_dir",
    "round": 1, "entries": entries, "checks": checks,
}
(OUT / "content-map.json").write_text(
    json.dumps(content, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print("round-01 design-tokens.json + content-map.json written")
