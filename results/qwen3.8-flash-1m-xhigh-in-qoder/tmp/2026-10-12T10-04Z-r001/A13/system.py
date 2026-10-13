"""A13 deliverables: brand-system.json and rationale.md.

Reads the geometry record gen.py wrote for the accepted version, so the component table in
the JSON is the same data the DSL was built from rather than a hand-written copy.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
OUT_DIR = ROOT / "outputs" / RUN / "A13"
TMP_DIR = ROOT / "tmp" / RUN / "A13"

ap = argparse.ArgumentParser()
ap.add_argument("--ver", required=True)
a = ap.parse_args()

geo = json.loads((TMP_DIR / f"{a.ver}-geometry.json").read_text(encoding="utf-8"))
ver = json.loads((TMP_DIR / f"{a.ver}-verify.json").read_text(encoding="utf-8"))

# mark ink bbox on the 512 grid, measured from the returned PNG
bb = ver["symbol-color"]["ink_bbox"]
mark_w, mark_h = bb[2] - bb[0] + 1, bb[3] - bb[1] + 1
clear = 132   # the front block's side, in 512-grid units

system = {
    "schema_version": 1, "task_id": "A13", "path_base": "output_dir",
    "brand": {"zh": "叠光", "en": "Layerlight",
              "concept": "信息叠加后仍然清晰",
              "fictional": True},
    "accepted_version": a.ver,
    "direction_chosen": "A 正交层叠",
    "direction_rejected": "B 放射光圈（见 rationale 与实际预览）",
    "colours": {
        "primary": {"blue": {"hex": "#1F5FA8", "role": "后层 / 拉丁字标"},
                    "teal": {"hex": "#2E9E8F", "role": "中层框"},
                    "amber": {"hex": "#E8A33D", "role": "前层小块 / 强调"},
                    "ink": {"hex": "#0E1A2B", "role": "光源点 / 中文字标、深底"}},
        "surfaces": {"paper": "#F5F2EA", "white": "#FFFFFF", "black_cut": "#000000"},
        "on_dark": {"blue": "#8FC7F2", "teal": "#7FD6C4", "amber": "#F2C063",
                    "ink": "#FFFFFF", "note": "海报深色带上的反相构件，几何与彩色版完全相同"},
        "usage_ratio": "约 蓝35% 青30% 橙20% 墨10% 留白随版式；不引入第五种色相",
    },
    "proportions": {
        "design_grid_units": 512,
        "mark_ink_bbox_units": bb,
        "mark_size_units": [mark_w, mark_h],
        "offset_between_layers_units": [72, 104],
        "front_block_side_units": 132,
        "frame_stroke_units": 34,
        "dot_diameter_units": 56,
        "corner_radius_ratio": "外圆角 40/216 ≈ 0.185；前层 26/132 ≈ 0.197；"
                               "同一套圆角语言，不按绝对值缩放",
    },
    "icon_components": {
        "counting_rule": "按可独立辨认的几何母形实例计数；位置/尺寸/变换/分组包装不另计；"
                         "圆环内孔等由扣除产生的负空间不计数，但记录生成规则",
        "components": geo["components"],
        "total": geo["component_count"],
        "limit": geo["limit"],
        "within_limit": geo["within_limit"],
        "negative_space_generation":
            "A2 的孔由 Container 的 border 生成：外圆角 40、描边 34 ⇒ 内孔 148 见方、"
            "内圆角 6；未使用遮罩或路径扣除，因此孔不计为额外构件",
    },
    "minimum_clear_space": {
        "rule": "图标四周留空 ≥ 前层小块边长（132/512 ≈ 25.8% 图标绘制边长）",
        "value_units": clear,
        "value_ratio_of_icon_side": round(clear / 512, 3),
        "measured_in_banner": "图标绘制区 280 单位，四周到文字块与画布边缘均 ≥ 44px 安全边距；"
                              "verify.py 实测 1200×400 外框 44px 内 0 个非背景像素",
        "measured_in_poster": "1080×1350 外框 56px 内 0 个非背景像素",
    },
    "applications": [
        {"file": "symbol-color.png", "dsl": "symbol-color.snapshot", "canvas": [512, 512],
         "purpose": "透明彩色图标", "palette": "colours.primary",
         "transparent": True,
         "measured": {k: ver["symbol-color"][k] for k in
                      ("alpha_zero_px", "alpha_opaque_px", "alpha_partial_px", "ink_bbox")}},
        {"file": "symbol-black.png", "dsl": "symbol-black.snapshot", "canvas": [512, 512],
         "purpose": "透明纯黑图标", "palette": "colours.surfaces.black_cut",
         "transparent": True,
         "depth_encoding": "层序改由 alpha 递增表达：后层 A0、中层 D0、前层与圆点 FF",
         "measured": {k: ver["symbol_black_purity"][k] for k in
                      ("alpha_positive_px", "violating_px", "pass", "distinct_rgb_count",
                       "alpha_range_on_alpha_positive")},
         "geometry_identity": ver["geometry_identity"]},
        {"file": "brand-banner.png", "dsl": "brand-banner.snapshot", "canvas": [1200, 400],
         "purpose": "品牌横幅", "safe_margin_px": 44,
         "symbol_placement": "图标按 s=280/512 重绘于 (184,200) 中心，非嵌入图标 PNG",
         "texts": ["叠光", "Layerlight", "把复杂信息，组织成清晰画面",
                   "信息叠加后仍然清晰 · IDENTITY SYSTEM"],
         "measured": {k: ver["brand-banner"][k] for k in
                      ("ink_px_inside_safe_margin", "within_margin")}},
        {"file": "launch-poster.png", "dsl": "launch-poster.snapshot", "canvas": [1080, 1350],
         "purpose": "发布海报（独立构图，非放大横幅）", "safe_margin_px": 56,
         "composition": "上 430px 深色带内放反相图标 + OPEN BETA + 品牌行；"
                        "下部纸面为大字标、主张、信息三行与 CTA 条",
         "symbol_placement": "图标按 s=300/512 以 on_dark 调色板重绘",
         "texts": ["叠光", "Layerlight", "把复杂信息，组织成清晰画面", "信息叠加后仍然清晰",
                   "2026.11.07 · ONLINE", "OPEN BETA", "layerlight.example.org"],
         "measured": {k: ver["launch-poster"][k] for k in
                      ("ink_px_inside_safe_margin", "within_margin")}},
    ],
    "no_embedded_raster": "横幅与海报里的图标由同一 symbol_A(cx, cy, s, palette) 生成器"
                          "按各自中心与比例重新构造 DSL 节点，未把 symbol-*.png 作为 Image 嵌入",
    "small_size_check": {
        "thumbnails": {k: ver["thumbnails_32"][k] for k in ver["thumbnails_32"]},
        "viewed_at_actual_size": True,
        "also_enlarged_for_edge_inspection": True,
        "note": "32×32 为预乘 alpha 的 Lanczos 结果，只存临时目录，不覆盖最终 PNG",
    },
}
(OUT_DIR / "brand-system.json").write_text(
    json.dumps(system, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

RATIONALE = """# 叠光 / Layerlight 选型说明

**两方向差异。** A 是正交层叠：三个圆角方块沿对角线错位，中层做成厚框，
透过方孔仍见后层的边，"叠加后仍然清晰"直接构进图形。B 是放射构图：
圆环加三条过心旋转弦与圆心，语义偏"分光"而非"叠层"。

**预览依据。** 两张 512 透明预览并排看图，再各做 32px 缩略比较：
B 的六向对称一缩就并成轮辐，且像通用齿轮；A 仍保住两块一方框的前后关系
与框内负空间，故选 A。

**小尺寸改进。** v001 的 A 用两条 16 单位描边，缩略后仅 57/1024 像素不透明，轮廓断裂；
改为后层实心、中层 34 单位厚框、前层 132 单位实心块后升到 158 像素。
纯黑版不靠色相分层，改用 alpha 160/208/255 递增使上层更实。
"""
(OUT_DIR / "rationale.md").write_text(RATIONALE, encoding="utf-8")
body = "".join(RATIONALE.split("\n", 2)[2:])
cjk = sum(1 for ch in body if ord(ch) > 0x2E80)
print(json.dumps({"brand-system.json": (OUT_DIR / "brand-system.json").stat().st_size,
                  "rationale_cjk_chars": cjk,
                  "rationale_total_chars": len(body.replace("\n", "").replace(" ", "")),
                  "limit": 300, "within_limit": cjk <= 300}, ensure_ascii=False))
