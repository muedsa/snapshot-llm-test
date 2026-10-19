# -*- coding: utf-8 -*-
"""A13 交付：brand-system.json（色彩/比例/构件/负空间/应用映射/计数依据）+ rationale.md（≤300字）。"""
import io, sys, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
OUT = os.path.join(ROOT, "outputs", "20261016T164020-m1", "A13")
STEPS = "tmp/20261016T164020-m1/A13/steps"
TMP = os.path.join(ROOT, "tmp", "20261016T164020-m1", "A13")
audit = json.load(open(os.path.join(TMP, "steps", "size-audit.json"), encoding="utf-8"))

def E(p, base="suite_root"):
    return {"path_base": base, "path": p}

COMP = [
    {"id": "mark.plate-01", "role": "底层片（前层读感：最高饱和）", "mother": "圆角方形 rounded-square",
     "params": {"box": [96, 196, 220, 220], "radius": 36, "alpha": "FF"},
     "dsl": {"symbol": "<Positioned left=96 top=196><Container 220x220 borderRadius=36 color=#3D6FF2FF /></Positioned>",
             "banner": "<Container 82.5x82.5 r=13.5> @ (84,177.5)（mark() f=0.375）",
             "poster": "<Container 111.7x111.7 r=18.3> @ (458.75,195.75)（f=260/512）"}},
    {"id": "mark.plate-02", "role": "中层片", "mother": "圆角方形",
     "params": {"box": [144, 148, 220, 220], "radius": 36, "alpha": "B8"},
     "dsl": {"symbol": "<Positioned left=144 top=148> … #7FB4FFB8", "banner": "同规则 ×0.375 @(108,159.25)", "poster": "同规则 ×0.5078 @(482.75,171.13)"}},
    {"id": "mark.plate-03", "role": "顶层片（含光孔）", "mother": "圆角方形（多轮廓裁剪）",
     "params": {"box": [192, 100, 220, 220], "radius": 36, "alpha": "CF"},
     "composite": "ClipPath path = 圆角方轮廓 + 圆孔轮廓，fillRule=EVEN_ODD，ANTI_ALIAS",
     "dsl": {"symbol": "<Positioned 192,100><SizedBox 220²><ClipPath …EVEN_ODD><Container #BCDCFFCF/></ClipPath></SizedBox>",
             "banner": "同规则 ×0.375 @(120,141)", "poster": "同规则 ×0.5078 @(506.7,146.6)"}},
]
NEG = {"plate_gaps": {"rule": "同一三片等大，步进 (+48, −48)（22% 片边），未覆盖区域露底形成 L 形阶梯负空间", "counted": False},
       "aperture_hole": {"rule": "顶层片母形内以 EVEN_ODD 第二轮廓挖除 r36 圆孔 @片心局部 (110,110)，透出中层 α72% 色调——光孔为扣除负空间", "counted": False}}
system = {
    "schema_version": 1, "task_id": "A13", "path_base": "output_dir",
    "brand": {"name_cjk": "叠光", "name_latin": "Layerlight",
              "concept": "信息叠加后仍然清晰", "domain": "结构化视觉工具",
              "positioning": "以错位叠层表达『叠』，以透出光孔表达『光/清晰』"},
    "palette": {
        "icon_layers": {"LL_BLUE": "#3D6FF2", "LL_SKY": "#7FB4FF", "LL_ICE": "#BCDCFF"},
        "layer_alphas": {"plate-01": "FF", "plate-02": "B8(72%)", "plate-03": "CF(81%)"},
        "app_colors": {"LL_GOLD": "#F2C94C", "LL_INK": "#0A162E", "LL_INK_SOFT": "#13224A",
                       "LL_PAPER": "#F5F9FF", "LL_SUB": "#46608F", "LL_PALE": "#9DBCE8",
                       "LL_LINE": "#D7E6FF", "LL_DARKLINE": "#30456F"},
        "black_icon_palette": "纯 #000000，仅以 alpha FF/B8/CF 区分层级（RGB 恒 0）"},
    "mark_geometry": {
        "mother_canvas": "512×512 透明；片母体 220²，圆角 36，步进 (+48,−48)，左下 (96,196) 起",
        "scale_rule": "f = 显示宽度 ÷ 512；坐标 = origin + 母坐标 × f（banner f=0.375 origin (48,104) size 192；poster f=0.5078 origin (410,96) size 260）",
        "aperture": {"local_center": [110, 110], "radius": 36, "fillRule": "EVEN_ODD",
                     "see_through": "中层片 α72%（黑版：α72% 黑），形成同构孔洞"},
        "negative_space": NEG,
        "same_rule_note": "四应用共用同一 mark() 几何生成器（另一画布坐标仅平移/缩放，不嵌任何渲染 PNG）"},
    "components": COMP,
    "component_count": {"total": 3, "limit": 6,
                        "basis": "可独立辨认母形实例：圆角方形 ×3（重复放置分别计数）；孔与片间缝隙为负空间不计数；旋转/裁剪/分组不另计——合计 3 ≤ 6",
                        "small_count_rule": "banner/大屏中的装饰回声为同母形重复实例，不属于图标本身计数（图标 = 图标应用内的 3 片）"},
    "typography": {"family": "Inter,Noto Sans CJK SC（本 run 前置真实字体查询缓存）",
                   "banner": {"lockup_cjk": 56, "lockup_latin": 44, "tagline": 28, "strip": 18},
                   "poster": {"title_cjk": 104, "title_latin": 56, "tagline": 32, "meta": 28, "site": 26}},
    "whitespace": {"min_margin": {"banner": 48, "poster": 64, "icon_iso_box": "片外接 (96..416,96..416)，四周各留 ≥96 母版空间（≥18.75% 隔离区）"},
                   "rule": "隔离区内不得放置其他元素；文字盒互不重叠"},
    "small_size": {"preview": {"tool": audit["tool"]["tool"], "resample": audit["tool"]["resample"], "pipeline": audit["tool"]["pipeline"],
                               "paths": [E(STEPS + "/symbol-color-32_on_paper.png"), E(STEPS + "/symbol-black-32_on_paper.png"),
                                         E(STEPS + "/symbol-color-32_zoom8.png"), E(STEPS + "/symbol-black-32_zoom8.png")]},
                   "target": "32px 下三层深浅步进、片间缝隙（≈3px）与孔洞点形均可识轮廓与关键负空间",
                   "improvements": ["顶层 α 45%→81%，拉开孔内外与层阶对比", "孔半径 30→36（32px 下 ≈2.25px 半径点形）", "黑版以 alpha 三级 FF/B8/CF 保重叠/孔洞可辨"]},
    "verification": {"black_purity": audit["black_purity"],
                     "geometry_match": audit["geometry_match"],
                     "alpha_plateaus_note": "彩版 alpha 直方图主峰 255/242/207/184 = 设计三层叠算（FF/72%、P2∩P3≈94.7%、CF 81、B8 72），结构精确成立"},
    "delivery": {"icons": {"symbol-color": "512×512 透明 PNG + snapshot", "symbol-black": "512×512 透明纯黑 PNG + snapshot"},
                 "banner": {"file": "brand-banner.png", "size": [1200, 400], "required_copy": ["叠光 Layerlight", "把复杂信息，组织成清晰画面"]},
                 "poster": {"file": "launch-poster.png", "size": [1080, 1350], "composition": "独立竖版：标志 260px 居中 + OPEN BETA 金 pill + 纵向双行名字 + 标语 + 分隔 + 日期/ONLINE + 官网",
                            "required_copy": ["叠光 Layerlight", "把复杂信息，组织成清晰画面", "2026.11.07 · ONLINE", "OPEN BETA", "layerlight.example.org"]},
                 "direction_previews": {"dir-a": E(TMP + "/dir-a.png"), "dir-b": E(TMP + "/dir-b.png")}}}
json.dump(system, open(os.path.join(OUT, "brand-system.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

rationale = ("两方向：A＝三片错位圆角方片（直角叠层、片间留缝、顶层圆孔）；"
             "B＝双三角山形＋金日轮（对角构图、坡线负空间）。看图对比：A 在 32px 下三层深浅、"
             "缝隙与孔点均可辨，B 双三角缩到 32px 融为实心楔形，且比喻偏景观、"
             "与『结构化视觉工具』贴合弱，故选 A。小尺寸改进：顶层 α 45%→81% 拉开孔内外对比，"
             "孔半径 30→36 保持 32px 点形可辨；22% 步进留缝维持负空间。")
assert len(rationale) <= 300, len(rationale)
open(os.path.join(OUT, "rationale.md"), "w", encoding="utf-8").write(
    "# 选型依据（≤300字）\n\n" + rationale + "\n")
print("len(rationale) =", len(rationale))
print("brand-system.json written")
