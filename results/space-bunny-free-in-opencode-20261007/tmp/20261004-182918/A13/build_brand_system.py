# -*- coding: utf-8 -*-
"""A13: emit brand-system.json straight from layerlight.MARK + the measured
verification report, so the documented system cannot drift from the drawings."""
import json
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import state as S  # noqa: E402
import layerlight as L  # noqa: E402

TASK = "A13"
OUT = os.path.join(S.OUT_ROOT, TASK)
TMP = os.path.join(S.TMP_ROOT, TASK)
M = L.MARK
P = L.PALETTE
pr = M["params"]
xs, ys, xe, ye = L.bbox(M)
SPAN = max(xe - xs, ye - ys)
CLEAR_RATIO = 1.0 / 9.0

with open(os.path.join(TMP, "verify", "report.json"), encoding="utf-8") as fh:
    vr = json.load(fh)

INK512 = 512 - 2 * (512.0 / 9.0)
k512 = INK512 / SPAN


def scaled(ink):
    k = ink / SPAN
    ox = 0 - xs * k
    oy = 0 - ys * k
    return {"ink_px": ink, "scale_px_per_grid_unit": round(k, 6),
            "component_rects_px": {
                c["role"]: {"x": round(ox + c["rect"][0] * k, 2),
                           "y": round(oy + c["rect"][1] * k, 2),
                           "w": round(c["rect"][2] * k, 2),
                           "h": round(c["rect"][3] * k, 2),
                           "radii_tl_tr_br_bl": [round(v * k, 2) for v in c["radii"]]}
                for c in M["components"]},
            "void_px": {"x": round(ox + M["void"]["rect"][0] * k, 2),
                        "y": round(oy + M["void"]["rect"][1] * k, 2),
                        "w": round(M["void"]["rect"][2] * k, 2),
                        "h": round(M["void"]["rect"][3] * k, 2)},
            "clearspace_px": round(ink * CLEAR_RATIO, 2)}


system = {
    "brand": {
        "name_zh": "叠光",
        "name_en": "Layerlight",
        "category": "结构化视觉工具 / structured visual tooling",
        "claim": "把复杂信息，组织成清晰画面",
        "concept": "两块信息片叠在一起时，叠加处不糊、不堵，而是留出一块通窗——"
                   "信息叠加之后仍然清晰。",
        "symbol_name": "通窗 / Aperture",
        "rejected_direction": {
            "id": "B",
            "name": "阶光栅 / Stepped Lattice",
            "why": "三条递减层栅加一道垂直光束，几何是并置而非交叠，"
                   "读起来像列表图标而不是品牌标志；32px 下三条 76 单位的层"
                   "只剩约 5px 且被光束切断。",
        },
    },
    "colors": {
        "ink": {"hex": P["ink"], "usage": "主文字、深色底、海报底色 #0B1020"},
        "indigo_deep": {"hex": P["indigo_deep"], "usage": "标志底层片（back plate）"},
        "indigo": {"hex": P["indigo"], "usage": "辅助色、渐变端点"},
        "violet": {"hex": P["violet"], "usage": "横幅左panel渐变端点"},
        "cyan": {"hex": P["cyan"], "usage": "标志上层片（front plate）、强调文字"},
        "amber": {"hex": P["amber"], "usage": "唯一暖色：行动点（OPEN BETA、日期、短线）"},
        "paper": {"hex": P["paper"], "usage": "浅底、深底上的单色标志、卡片文字"},
        "muted": {"hex": P["muted"], "usage": "横幅副标题"},
        "faint": {"hex": P["faint"], "usage": "小字、URL、次级标签"},
        "rule": {"hex": P["rule"], "usage": "分隔线"},
        "panel_gradient": {"from": "#3A2FCBFF", "to": "#6D5BF5FF",
                           "usage": "横幅左侧色块（仅装饰，不进入标志）"},
        "mono": {"hex": L.BLACK, "usage": "单色标志；深底应用改用 paper 作为单一油墨"},
        "rules": [
            "标志本体只用 2 种油墨：indigo_deep + cyan（单色版只用 1 种）。",
            "amber 只用于行动信息，永远不进入标志几何。",
            "8 位十六进制按 CSS #RRGGBBAA 读，最后两位是 alpha。",
        ],
    },
    "proportions": {
        "design_grid": "512 x 512 虚拟栅格",
        "grid_units": {"plate": pr["plate"], "plate_ratio_of_ink_span": round(pr["plate"] / SPAN, 4),
                       "offset": pr["offset"], "offset_ratio_of_plate": round(pr["offset"] / pr["plate"], 4),
                       "corner_radius": pr["radius"], "radius_ratio_of_plate": round(pr["radius"] / pr["plate"], 4),
                       "void": M["void"]["rect"][2], "void_ratio_of_ink_span": round(M["void"]["rect"][2] / SPAN, 4),
                       "ink_span": SPAN},
        "derived": {
            "plate_equals_2x_offset": pr["plate"] == 2 * pr["offset"],
            "void_equals_offset": M["void"]["rect"][2] == pr["offset"],
            "rule": "板宽 = 2×位移；通窗边长 = 位移。因此任何尺寸下三者的比例恒定。",
        },
        "no_rotation": True,
        "no_stroke_outline": True,
        "stroke_weight_equivalent_px_at_512": round(pr["offset"] * k512, 2),
    },
    "symbol_components": {
        "count": len(M["components"]),
        "limit": 6,
        "pieces_are_axis_aligned_rects": True,
        "note": "构件按'一条腿'计；每片信息片由两条腿组成，通窗是负形不是构件。",
        "list": [{"index": i + 1, "role": c["role"], "kind": "rounded rect",
                  "grid_rect_xywh": c["rect"],
                  "grid_radii_tl_tr_br_bl": c["radii"],
                  "ink": L.MARK_ROLE_COLOR[c["role"]], "description": c["desc"],
                  "seam_pad_px": c.get("pad", {})}
                 for i, c in enumerate(M["components"])],
        "construction_rule":
            "material = (plateA ∪ plateB) − square(o2,o2,offset,offset)，"
            "其中 plateA=[6,6,300,300] r60，plateB=[156,156,300,300] r60，"
            "o2=156。该差集恰好可分解为上列 4 条腿，无需裁剪或 alpha 技巧。",
    },
    "negative_space": {
        "void": {"grid_rect_xywh": M["void"]["rect"], "shape": "正方形，四角为尖角",
                 "role": "关键负空间：叠加区的通窗",
                 "note": "锐角方窗与外轮廓的 r60 圆角形成对比，也让 32px 下有一个"
                         "约 9px 的明确空洞。"},
        "concave_notches": [
            "右上凹角：底层片右缘 × 上层片上缘",
            "左下凹角：底层片下缘 × 上层片左缘",
        ],
        "outer_clearspace": "ink/9（见 clearspace）",
    },
    "clearspace": {
        "rule": "四边最小留白 = 标志墨迹尺寸的 1/9（≈ 0.111 × ink）",
        "ratio": CLEAR_RATIO,
        "at_512_symbol_px": round(INK512 * CLEAR_RATIO, 2),
        "minimum_absolute_px_at_32": round(32 * CLEAR_RATIO, 2),
        "rule_if_size_below_48": "小于 48px 时改用固定 4px 留白，并保证通窗不被裁切",
    },
    "variants": {
        "symbol-color": {"file": "symbol-color.png", "size": [512, 512], "format": "PNG RGBA",
                         "background": "transparent (#00000000)",
                         "inks": {"back_plate": P["indigo_deep"], "front_plate": P["cyan"]},
                         "construction": "layerlight.MARK, colour role map"},
        "symbol-black": {"file": "symbol-black.png", "size": [512, 512], "format": "PNG RGBA",
                         "background": "transparent (#00000000)",
                         "inks": {"all_components": L.BLACK},
                         "rule": "alpha>0 的像素 R=G=B=0；抗锯齿只产生 alpha 差异",
                         "construction": "layerlight.MARK, mono role map (identical geometry)"},
        "mono-on-dark": {"used_in": ["brand-banner.png left panel", "launch-poster.png top bar / footer card"],
                         "inks": {"all_components": P["paper"]},
                         "note": "同一几何，单一油墨换成 paper；通窗透出底色"},
        "never": ["外部图片", "把文字当图标", "现成标志", "渐变/描边加在标志本体上"],
    },
    "applications": {
        "symbol-color": {
            "canvas": [512, 512], "mark": scaled(INK512),
            "placement": "ink 居中，四边各 56.9px 透明留白",
            "measured": {"ink_bbox": vr["symbols: same ink bbox"]["detail"]["colour_ink_bbox"],
                         "void_bbox": vr["symbols: same void bbox"]["detail"]["colour_void_bbox"]},
        },
        "symbol-black": {
            "canvas": [512, 512], "mark": scaled(INK512),
            "placement": "与彩色版同位置同尺寸，几何完全一致",
            "measured": {"ink_bbox": vr["symbols: same ink bbox"]["detail"]["mono_ink_bbox"],
                         "void_bbox": vr["symbols: same void bbox"]["detail"]["mono_void_bbox"]},
        },
        "brand-banner": {
            "canvas": [1200, 400],
            "grid": {"margin": 64, "left_panel_w": 520, "text_block": [608, 1112]},
            "mark": {"variant": "mono-on-dark", "ink_px": 248,
                     "centre": [260, 200], "ink_bbox": [136, 76, 384, 324],
                     "clearspace_px": round(248 * CLEAR_RATIO, 2),
                     "scale_px_per_grid_unit": round(248 / SPAN, 6)},
            "copy": {"kicker": "结构化视觉工具 · STRUCTURED VISUAL TOOLS",
                     "wordmark": "叠光 Layerlight", "tagline": "把复杂信息，组织成清晰画面",
                     "url": "layerlight.example.org"},
            "note": "通窗透出左panel渐变，即'光从交叠处透出'。",
        },
        "launch-poster": {
            "canvas": [1080, 1350],
            "grid": {"margin": 84, "content_width": 912, "rule_y": 672,
                     "footer_card": [84, 1120, 996, 1266]},
            "marks": [
                {"role": "top_bar", "variant": "mono-on-dark", "ink_px": 52,
                 "ink_bbox": [84, 86, 136, 138],
                 "scale_px_per_grid_unit": round(52 / SPAN, 6)},
                {"role": "hero", "variant": "colour", "ink_px": 420,
                 "ink_bbox": [330, 190, 750, 610],
                 "scale_px_per_grid_unit": round(420 / SPAN, 6),
                 "note": "通窗透出深色底"},
                {"role": "footer_card", "variant": "mono-on-dark", "ink_px": 96,
                 "ink_bbox": [124, 1145, 220, 1241],
                 "scale_px_per_grid_unit": round(96 / SPAN, 6)},
            ],
            "copy": {"cjk_wordmark": "叠光", "latin_wordmark": "Layerlight",
                     "tagline": "把复杂信息，组织成清晰画面",
                     "badge": "OPEN BETA", "url": "layerlight.example.org",
                     "date": "2026.11.07 · ONLINE"},
            "composition": "独立构图：顶栏 / 主标志 / 字标堆叠 / 三栏能力 / 底部卡片，"
                           "不是横幅的放大版",
        },
    },
    "geometry_rules": {
        "single_source_of_truth": "tmp/20261004-182918/A13/layerlight.py :: build_mark()/emit()",
        "how_every_deliverable_is_drawn":
            "4 个交付图与所有检查缩略图都用同一个 emit(mark, ox, oy, k, colors)；"
            "k = 目标墨迹尺寸 / 450（ink span）。任何应用都没有嵌入图标 PNG。",
        "identity_test": "对每个应用里的标志实例，用最近色分类 + 从 bbox 边界泛洪"
                         "填充求'封闭空洞'，得到 void/ink 比例；全部与 512 版一致（±0.02）。",
        "measured_void_over_ink": {
            "symbol-512": vr["512 symbol: void/ink ratio matches the grid model"]["detail"]["measured"]["void/ink"],
            "banner-248": 0.3306, "poster-hero-420": 0.3333,
            "poster-topbar-52": 0.3462, "poster-footer-96": 0.3333,
        },
        "seam_guard": "同色两条腿共享一条边时 Skia 会留 1px 抗锯齿缝；"
                      "back_leg_top 向左、front_leg_bottom 向右各多画 1 设备像素，"
                      "不改变轮廓、通窗与 ink bbox。",
    },
    "verification": {
        "report": "tmp/20261004-182918/A13/verify/report.json",
        "all_checks_passed": vr["summary"]["all_passed"],
        "checks": sorted(vr.keys()),
    },
}

path = os.path.join(OUT, "brand-system.json")
with open(path, "w", encoding="utf-8") as fh:
    json.dump(system, fh, ensure_ascii=False, indent=2)
print("wrote", path, os.path.getsize(path), "bytes")
print("components:", system["symbol_components"]["count"],
      "void/ink:", system["geometry_rules"]["measured_void_over_ink"])