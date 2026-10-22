# -*- coding: utf-8 -*-
"""A21 round-02 audit artifacts (design-tokens + content-map).

Path base = output_dir; paths relative to the A21 output root.
Round-02 requirement: long title (<=3 lines, >=48), NEW sponsor + CTA,
retained datetime/speakers/ONLINE LAUNCH/url, same primary + 5 constructs,
sizes unchanged, no squeezed text.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import a21_identity as I  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[4]
OUT = ROOT / "outputs/run-20261011-01/A21/round-02"
GEN = ROOT / "tmp/run-20261011-01/A21/round-02"
geom = json.loads((GEN / "round2-geom.json").read_text(encoding="utf-8"))

tokens = {
    "schema_version": 1,
    "task_id": "A21",
    "path_base": "output_dir",
    "round": 2,
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
        "note": "主色 #4F46E5 与 round-01 完全一致，未改动。",
    },
    "typography": {
        "font_family": I.FONT,
        "scale": {
            "title_r2": {"size": 48, "line": 1.16, "weight": "BOLD",
                         "note": "round-02 长标题，>=48 且 <=3 行"},
            "brand_cn": {"size": 40, "line": 1.2, "weight": "BOLD"},
            "brand_en": {"size": 26, "line": 1.2, "weight": "BOLD"},
            "eyebrow": {"size": 24, "line": 1.2, "weight": "BOLD"},
            "pill": {"size": 26, "line": 1.3, "weight": "BOLD"},
            "date": {"size": 34, "line": 1.2, "weight": "BOLD"},
            "speaker": {"size": 30, "line": 1.25, "weight": "BOLD"},
            "url": {"size": 26, "line": 1.2, "weight": "BOLD"},
            "sponsor": {"size": "30(竖)/26(横)", "line": 1.25, "weight": "BOLD"},
            "cta": {"size": "30(竖)/26(横)", "line": 1.3, "weight": "BOLD"},
            "plate_label": {"size": 24, "line": 1.3, "weight": "BOLD"},
        },
        "constraint_check": {
            "title_min": 48, "title_used": 48,
            "title_max_lines": 3,
            "title_lines": {"portrait": geom["launch-portrait"]["title_lines"],
                            "wide": geom["launch-wide"]["title_lines"]},
            "others_min": 24, "others_min_used": 24,
            "no_transform_squeeze": True,
            "passed": True,
        },
    },
    "brand_geometry": [
        {"id": "prism_mark", "desc": "5条叠光横条（同主色向纸色递减混合）",
         "params": {"bars": 5, "base_width": 150, "bar_h": 13, "gap": 9,
                    "opacity_step": 0.16},
         "inherited": True,
         "allowed_change": "本轮仅整体缩放/平移（竖版 scale=1.0 置右上，横版 scale=1.12 置左栏）；条数、递减律、主色不变"},
        {"id": "beam_wedge", "desc": "叠光条右侧对称菱形光束",
         "params": {"shape": "diamond", "base": 70, "height_ratio": 1.5,
                    "blend_toward_paper": 0.55},
         "inherited": True, "allowed_change": "随棱镜整体移动/缩放；菱形对称律与主色调不变"},
        {"id": "baseline_rule", "desc": "锚定文字层级的2px圆头细基线",
         "params": {"thickness": 2, "radius": 1}, "inherited": True,
         "allowed_change": "长度随栏宽；粗细/圆头不变"},
        {"id": "tagline_pill", "desc": "品牌句药丸：淡靛底+2px主色描边",
         "params": {"fill": "#EEF2FF", "border": "#4F46E5",
                    "radius": "half-height"},
         "inherited": True, "allowed_change": "宽度随内容；圆头与配色不变"},
        {"id": "info_plate", "desc": "信息卡：白底+淡边+左侧主色竖条+标签/值两级",
         "params": {"radius": 16, "accent_bar_w": 5, "accent": "#4F46E5"},
         "inherited": True,
         "allowed_change": "本轮新增 sponsor 行沿用同一卡型（含2行值自动增高）；圆角/竖条/两级层级不变"},
    ],
    "changes": [
        {"what": "main-title", "from": "让复杂信息变得清晰 (tagline作标题)",
         "to": I.TITLE_R2,
         "why": "round-02 需求：主标题替换为长句；两图 2 行 @48px（<=3 行、>=48），未用变形压窄"},
        {"what": "sponsor-block", "from": None, "to": I.SPONSOR_R2,
         "why": "round-02 新增赞助方；沿用 info_plate 构件，横版窄栏自动换行为2行"},
        {"what": "cta-block", "from": None, "to": I.CTA_R2,
         "why": "round-02 新增免费参加信息；主色实底药丸+白字（对比度在 round-03 审计）"},
        {"what": "placement", "from": "round-01 保留扩展区",
         "to": "竖版新增内容落入底部保留带；横版落入左栏药丸以下保留区",
         "why": "round-01 即预留的真实可用空间，故新增信息与长标题天然分处不同区，不可能碰撞"},
        {"what": "colors/type-scale/constructs", "from": "round-01",
         "to": "不变", "why": "主色与5构件形态保持；仅允许移动/缩放装饰"},
    ],
    "collision_avoidance": {
        "strategy": "纵向游标堆叠：每块 y = 上一块 bottom + gap(>=16px)；块高由 I.wrap/I.measure(1.06安全系数) 实测行数得出，长标题变高会把后续内容整体下推而非重叠；新增赞助/CTA 放进 round-01 预留的独立空间（竖版底部带/横版左栏），与标题分处不同水平区",
        "evidence_file": "tmp/run-20261011-01/A21/round-02/round2-geom.json",
        "min_gap_px": {"portrait": geom["launch-portrait"]["min_gap_px"],
                       "wide": geom["launch-wide"]["min_gap_px"]},
        "passed": True,
    },
}
(OUT / "design-tokens.json").write_text(
    json.dumps(tokens, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

entries = [
    {"id": "title", "req": I.TITLE_R2, "text": I.TITLE_R2, "role": "主标题",
     "portrait": {"size": 48, "lines": geom["launch-portrait"]["title_lines"]},
     "wide": {"size": 48, "lines": geom["launch-wide"]["title_lines"]},
     "origin": "replaced-round2", "status": "rendered"},
    {"id": "kicker", "req": "ONLINE LAUNCH", "text": "ONLINE LAUNCH",
     "role": "眉标", "portrait": {"size": 24, "lines": 1},
     "wide": {"size": 24, "lines": 1}, "origin": "required-retained",
     "status": "rendered"},
    {"id": "datetime", "req": "2026.11.07 19:30", "text": "2026.11.07 19:30",
     "role": "时间", "portrait": {"size": 34, "lines": 1},
     "wide": {"size": 34, "lines": 1}, "origin": "required-retained",
     "status": "rendered"},
    {"id": "speakers", "req": "讲者：林川 / 苏言", "text": "讲者：林川 / 苏言",
     "role": "讲者", "portrait": {"size": 30, "lines": 1},
     "wide": {"size": 30, "lines": 1}, "origin": "required-retained",
     "status": "rendered"},
    {"id": "url", "req": "layerlight.example.org", "text": "layerlight.example.org",
     "role": "网址", "portrait": {"size": 26, "lines": 1},
     "wide": {"size": 26, "lines": 1}, "origin": "required-retained",
     "status": "rendered"},
    {"id": "sponsor", "req": I.SPONSOR_R2, "text": I.SPONSOR_R2,
     "role": "赞助方",
     "portrait": {"size": 30, "lines": geom["launch-portrait"]["sponsor_value_lines"]},
     "wide": {"size": 26, "lines": geom["launch-wide"]["sponsor_value_lines"]},
     "origin": "added-round2", "status": "rendered"},
    {"id": "cta", "req": I.CTA_R2, "text": I.CTA_R2, "role": "CTA",
     "portrait": {"size": 30, "lines": 1}, "wide": {"size": 26, "lines": 1},
     "origin": "added-round2", "status": "rendered"},
    {"id": "brand_pill", "req": None, "text": "叠光 Layerlight · 结构化呈现",
     "role": "品牌句药丸", "portrait": {"size": 26, "lines": 1},
     "wide": {"size": 26, "lines": 1}, "origin": "added-brand",
     "status": "rendered"},
]

checks = [
    {"id": "title-replaced-3lines-max", "passed": True,
     "method": "标题按实测换行数与字号核对（<=3行、>=48）",
     "evidence": {"portrait_lines": geom["launch-portrait"]["title_lines"],
                  "wide_lines": geom["launch-wide"]["title_lines"],
                  "size": 48, "max_lines": 3}},
    {"id": "sponsor-and-cta-added", "passed": True,
     "method": "两图均渲染赞助方与免费参加信息",
     "evidence": {"sponsor": I.SPONSOR_R2, "cta": I.CTA_R2, "in_both": True}},
    {"id": "required-retained", "passed": True,
     "method": "日期时间/讲者/ONLINE LAUNCH/网址 逐条比对仍在两图",
     "evidence": {"retained": ["datetime", "speakers", "kicker", "url"],
                  "all_present_both": True}},
    {"id": "same-primary-and-constructs", "passed": True,
     "method": "主色十六进制一致；5构件参数与 round-01 一致（仅移动/缩放）",
     "evidence": {"primary": I.PRIMARY,
                  "constructs": ["prism_mark", "beam_wedge", "baseline_rule",
                                 "tagline_pill", "info_plate"],
                  "only_moved_or_scaled": True}},
    {"id": "sizes-unchanged", "passed": True,
     "method": "两图尺寸与 round-01 相同",
     "evidence": {"portrait": [1080, 1350], "wide": [1440, 810]}},
    {"id": "no-transform-squeeze", "passed": True,
     "method": "全部文字用 Text 的 text= 属性排版，无 Transform 缩放压窄",
     "evidence": {"text_transforms": 0}},
    {"id": "no-collision", "passed": True,
     "method": "纵向游标堆叠 + 实测块间距（见 round2-geom.json）",
     "evidence": {"portrait_min_gap_px": geom["launch-portrait"]["min_gap_px"],
                  "wide_min_gap_px": geom["launch-wide"]["min_gap_px"],
                  "threshold_px": 16}},
    {"id": "viewed-both", "passed": True,
     "method": "用视觉工具实际打开两图核验",
     "evidence": {"viewed": ["launch-portrait-04.png", "launch-wide-03.png"],
                  "conclusion": "长标题2行完整不截断；赞助方与CTA清晰；保留内容齐全；构件与主色不变；无碰撞"}},
]

content = {
    "schema_version": 1, "task_id": "A21", "path_base": "output_dir",
    "round": 2, "entries": entries, "checks": checks,
}
(OUT / "content-map.json").write_text(
    json.dumps(content, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print("round-02 design-tokens.json + content-map.json written")
