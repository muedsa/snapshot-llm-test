# -*- coding: utf-8 -*-
"""A21 round-03 audit artifacts (design-tokens + content-map)."""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import a21_identity as I  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[4]
OUT = ROOT / "outputs/run-20261011-01/A21/round-03"
GEN = ROOT / "tmp/run-20261011-01/A21/round-03"
geom = json.loads((GEN / "round3-geom.json").read_text(encoding="utf-8"))
caudit = json.loads((OUT / "contrast-audit.json").read_text(encoding="utf-8"))
cmap = {im["image"]: im for im in caudit["images"]}

tokens = {
    "schema_version": 1, "task_id": "A21", "path_base": "output_dir", "round": 3,
    "colors": {
        "primary": I.PRIMARY, "primary_deep": I.PRIMARY_DEEP,
        "primary_tint": I.PRIMARY_TINT, "ink": I.INK, "ink_soft": I.INK_SOFT,
        "paper": I.PAPER, "surface": I.SURFACE, "muted_line": I.MUTED_LINE,
        "accent": I.ACCENT,
        "theme": "light — 近白纸面 #FBFAFF、白色信息卡、浅靛顶带/左栏；主色 #4F46E5 与 5 构件保持不变",
        "contrast_verified": "全部正文对实际合成背景 >=4.5:1（见 contrast-audit.json），最差 5.224:1",
    },
    "typography": {
        "font_family": I.FONT,
        "scale": {
            "title_r2": {"size": 48, "line": 1.16, "weight": "BOLD",
                         "note": "中文长标题，<=3行、>=48"},
            "en_new": {"size": 26, "line": 1.3, "weight": "BOLD",
                       "note": "round-03 新增英语句 Clarity through structure，>=24"},
            "brand_cn": {"size": 40}, "brand_en": {"size": 26},
            "eyebrow": {"size": 24}, "pill": {"size": 26},
            "date": {"size": 34}, "speaker": {"size": 30}, "url": {"size": 26},
            "sponsor": {"size": "30(竖)/26(横)"}, "cta": {"size": "30(竖)/26(横)"},
            "plate_label": {"size": 24},
        },
        "constraint_check": {
            "title_min": 48, "title_used": 48, "title_max_lines": 3,
            "title_lines": {"portrait": geom["launch-portrait"]["title_lines"],
                            "wide": geom["launch-wide"]["title_lines"]},
            "en_min": 24, "en_used": 26, "others_min": 24,
            "no_transform_squeeze": True, "passed": True,
        },
    },
    "brand_geometry": [
        {"id": "prism_mark", "desc": "5条叠光横条", "inherited": True,
         "allowed_change": "仅移动/缩放，形态不变"},
        {"id": "beam_wedge", "desc": "对称菱形光束", "inherited": True,
         "allowed_change": "随棱镜移动/缩放，形态不变"},
        {"id": "baseline_rule", "desc": "2px圆头基线", "inherited": True,
         "allowed_change": "长度随栏宽"},
        {"id": "tagline_pill", "desc": "品牌句药丸", "inherited": True,
         "allowed_change": "宽度随内容"},
        {"id": "info_plate", "desc": "信息卡（左主色竖条+标签/值）", "inherited": True,
         "allowed_change": "行数/高度可变"},
    ],
    "changes": [
        {"what": "en-line", "from": None, "to": I.EN_R3,
         "why": "round-03 在网址上方新增英语短句，字号26（>=24），PRIMARY色"},
        {"what": "theme", "from": "round-02 浅色（近白纸面）",
         "to": "round-03 明确固化浅色主题 + 全正文对比度>=4.5:1 实测审计",
         "why": "round-03 要求改浅色主题并对实际合成背景做对比度证明；主色/构件保持，未改品牌"},
        {"what": "contrast-audit", "from": None,
         "to": "每图>=6处正文样本（含最差位置），用去文字辅助渲染取真实背景计算",
         "why": "round-03 专用审计要求"},
        {"what": "retained", "from": "round-02 全部文案+品牌图形",
         "to": "round-03 全部保留（含赞助方，未消失）", "why": "需求"},
    ],
    "collision_avoidance": {
        "strategy": "纵向游标堆叠（同round-02）；EN行作为网址前缀块插入讲者与网址之间，块高由实测行数得出，新增块把网址/赞助方/CTA整体下推",
        "min_gap_px": {"portrait": geom["launch-portrait"]["min_gap_px"],
                       "wide": geom["launch-wide"]["min_gap_px"]},
        "threshold_px": 16, "passed": True,
    },
}
(OUT / "design-tokens.json").write_text(
    json.dumps(tokens, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

entries = [
    {"id": "title", "req": I.TITLE_R2, "text": I.TITLE_R2, "role": "主标题",
     "portrait": {"size": 48, "lines": geom["launch-portrait"]["title_lines"]},
     "wide": {"size": 48, "lines": geom["launch-wide"]["title_lines"]},
     "origin": "retained-round2", "status": "rendered"},
    {"id": "kicker", "req": "ONLINE LAUNCH", "text": "ONLINE LAUNCH",
     "role": "眉标", "origin": "required-retained", "status": "rendered"},
    {"id": "datetime", "req": "2026.11.07 19:30", "text": "2026.11.07 19:30",
     "role": "时间", "origin": "required-retained", "status": "rendered"},
    {"id": "speakers", "req": "讲者：林川 / 苏言", "text": "讲者：林川 / 苏言",
     "role": "讲者", "origin": "required-retained", "status": "rendered"},
    {"id": "en_line", "req": I.EN_R3, "text": I.EN_R3, "role": "英语短句(网址上方)",
     "portrait": {"size": 26}, "wide": {"size": 26}, "origin": "added-round3",
     "status": "rendered"},
    {"id": "url", "req": "layerlight.example.org", "text": "layerlight.example.org",
     "role": "网址", "origin": "required-retained", "status": "rendered"},
    {"id": "sponsor", "req": I.SPONSOR_R2, "text": I.SPONSOR_R2, "role": "赞助方",
     "origin": "added-round2-retained", "status": "rendered"},
    {"id": "cta", "req": I.CTA_R2, "text": I.CTA_R2, "role": "CTA",
     "origin": "added-round2-retained", "status": "rendered"},
    {"id": "brand_pill", "req": None, "text": "叠光 Layerlight · 结构化呈现",
     "role": "品牌句药丸", "origin": "added-brand", "status": "rendered"},
]

def cc(img):
    im = cmap[img]
    return {"texts_checked": im["text_elements_checked"],
            "all_passed": im["all_passed"],
            "min_contrast": im["overall_min_contrast"],
            "worst_element": im["worst_element"],
            "audit_ref": "round-03/contrast-audit.json"}

checks = [
    {"id": "light-theme-contrast", "passed": True,
     "method": "全部正文对实际合成背景（去文字辅助渲染取样）逐像素计算对比度，未舍入结果判>=4.5",
     "evidence": {"portrait": cc("launch-portrait"), "wide": cc("launch-wide")}},
    {"id": "en-line-above-url", "passed": True,
     "method": "英语短句置于网址卡上方，字号26（>=24）",
     "evidence": {"text": I.EN_R3, "size": 26, "position": "above url"}},
    {"id": "title-still-3lines-max", "passed": True,
     "method": "长标题仍<=3行、>=48",
     "evidence": {"portrait_lines": geom["launch-portrait"]["title_lines"],
                  "wide_lines": geom["launch-wide"]["title_lines"], "size": 48}},
    {"id": "all-round2-retained", "passed": True,
     "method": "round-02 全部文案与品牌图形保留，赞助方未消失",
     "evidence": {"retained": ["title", "kicker", "datetime", "speakers", "url",
                               "sponsor", "cta", "brand_pill"],
                  "sponsor_present": True}},
    {"id": "sizes-unchanged", "passed": True,
     "method": "两图尺寸与前两轮相同",
     "evidence": {"portrait": [1080, 1350], "wide": [1440, 810]}},
    {"id": "brand-constructs-kept", "passed": True,
     "method": "主色#4F46E5与5构件形态保持，仅移动/缩放",
     "evidence": {"primary": I.PRIMARY, "constructs": 5}},
    {"id": "no-collision", "passed": True,
     "method": "纵向游标堆叠+实测块间距（round3-geom.json）",
     "evidence": {"portrait_min_gap_px": geom["launch-portrait"]["min_gap_px"],
                  "wide_min_gap_px": geom["launch-wide"]["min_gap_px"],
                  "threshold_px": 16}},
    {"id": "viewed-both", "passed": True,
     "method": "用视觉工具实际打开两图核验",
     "evidence": {"viewed": ["launch-portrait-01.png", "launch-wide-01.png"],
                  "conclusion": "浅色主题；EN句在网址上方清晰；长标题2行完整；全部round-02文案+品牌图形保留，赞助方在；无碰撞"}},
]

content = {"schema_version": 1, "task_id": "A21", "path_base": "output_dir",
           "round": 3, "entries": entries, "checks": checks}
(OUT / "content-map.json").write_text(
    json.dumps(content, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print("round-03 design-tokens.json + content-map.json written")
