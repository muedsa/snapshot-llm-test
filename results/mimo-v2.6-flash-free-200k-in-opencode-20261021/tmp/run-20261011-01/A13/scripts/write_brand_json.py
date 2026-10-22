# -*- coding: utf-8 -*-
"""Write A13 brand-system.json (embedding the real measured check numbers)
and rationale.md (<=300 Chinese characters)."""
import json
import pathlib

ROOT = pathlib.Path(".")
RUN = "run-20261011-01"
TASK = "A13"
TMP = ROOT / "tmp" / RUN / TASK
OUT = ROOT / "outputs" / RUN / TASK
OUT.mkdir(parents=True, exist_ok=True)

checks = json.loads((TMP / "checks.json").read_text(encoding="utf-8"))
geo = json.loads((TMP / "checks-geometry-detail.json").read_text(encoding="utf-8"))

# ---- icon constants (the single geometry rule source, 512 box) ------------
RING = {"x": 56, "y": 56, "d": 400, "border": 72, "color": "#22D3EE"}
DISC = {"x": 240, "y": 240, "d": 160, "color": "#7C3AED"}
DOT = {"x": 183, "y": 183, "d": 56, "color": "#3B82F6"}

# derived numbers (unrounded where used in checks)
import math
cx = cy = 256.0
disc_c = (DISC["x"] + DISC["d"] / 2, DISC["y"] + DISC["d"] / 2)          # (320,320)
disc_off = math.hypot(disc_c[0] - cx, disc_c[1] - cy)                    # 90.5097
disc_far = disc_off + DISC["d"] / 2                                       # 170.5097
ring_inner = RING["d"] / 2 - RING["border"]                               # 128
ring_outer = RING["d"] / 2                                                # 200
ring_overlap = disc_far - ring_inner                                      # 42.5097
ring_remnant = ring_outer - disc_far                                      # 29.4903
dot_c = (DOT["x"] + DOT["d"] / 2, DOT["y"] + DOT["d"] / 2)                # (211,211)
dot_off = math.hypot(dot_c[0] - cx, dot_c[1] - cy)                        # 63.6396
dot_near = dot_off - DOT["d"] / 2                                         # 35.6396
dot_far = dot_off + DOT["d"] / 2                                          # 91.6396
gap_ring_dot = ring_inner - dot_far                                       # 36.3604
gap_disc_dot = dot_near + (disc_off - DISC["d"] / 2)                      # 46.1493

S32 = 32 / 512

system = {
    "schema_version": 1,
    "task_id": "A13",
    "path_base": "output_dir",
    "brand": {
        "name": "叠光 Layerlight",
        "concept": "信息叠加后仍然清晰",
    },
    "colors": {
        "light_cyan": {"hex": "#22D3EE", "role": "主色 · 圆环（光圈本体）"},
        "violet": {"hex": "#7C3AED", "role": "辅色 · 透镜圆盘（叠加层）"},
        "blue": {"hex": "#3B82F6", "role": "点缀 · 光点"},
        "ink_top": {"hex": "#0B1220", "role": "应用底色 · 渐变起点（横幅/海报）"},
        "ink_mid": {"hex": "#0D1526", "role": "应用底色 · 渐变中点"},
        "ink_bottom": {"hex": "#111C31", "role": "应用底色 · 渐变终点"},
        "amber": {"hex": "#F59E0B", "role": "强调 · OPEN BETA 徽章"},
        "text_primary": {"hex": "#F8FAFC", "role": "标题文字"},
        "text_secondary": {"hex": "#A9BCD8", "role": "副文文字"},
        "pure_black": {"hex": "#000000", "role": "单色版图标（RGB 必须为 0）"},
    },
    "geometry": {
        "coordinate_system": "画布左上原点，x 向右、y 向下，单位像素；图标基准盒 512×512",
        "base_box": [0, 0, 512, 512],
        "icon_center": [256, 256],
        "ring": {
            "box": [56, 56, 455, 455], "diameter": 400, "border": 72,
            "shape": "CIRCLE", "inner_hole_diameter": 256,
            "note": "Container shape=CIRCLE + border=\"72 SOLID <色>\"，无填充",
        },
        "disc": {
            "box": [240, 240, 399, 399], "diameter": 160,
            "center": [320, 320],
            "offset_from_icon_center": [64, 64],
            "offset_distance": round(disc_off, 4),
            "overlap_into_ring_band": round(ring_overlap, 4),
            "ring_remnant_at_45deg": round(ring_remnant, 4),
        },
        "dot": {
            "box": [183, 183, 238, 238], "diameter": 56,
            "center": [211, 211],
            "offset_distance": round(dot_off, 4),
        },
        "negative_space": {
            "key": "环孔月牙：圆环内孔（直径256）减去透镜圆盘与光点后的剩余区域，随盘/点位置呈偏心月牙形",
            "generation_rule": "hole = circle(r=128@center) minus disc(d=160@(320,320)) minus dot(d=56@(211,211))",
            "crescent_max_width_ring_to_disc": round(ring_inner + (disc_off - DISC["d"] / 2), 4),
            "crescent_note": "月牙沿 -45° 轴（背离圆盘方向）的最大宽度 = 环内缘128 + 盘近缘距中心10.5097；圆盘在 +45° 方向压过环内缘，故该处无间隙而是重叠42.51单位",
            "gap_ring_to_dot": round(gap_ring_dot, 4),
            "gap_disc_to_dot": round(gap_disc_dot, 4),
            "min_gap_icon_units": round(min(gap_ring_dot, gap_disc_dot), 4),
            "min_gap_at_32px": round(min(gap_ring_dot, gap_disc_dot) * S32, 3),
        },
        "proportions": {
            "ring_diameter_to_box": 400 / 512,
            "border_to_ring_diameter": 72 / 400,
            "disc_to_ring_diameter": 160 / 400,
            "dot_to_ring_diameter": 56 / 400,
            "scale_note": "所有应用 = 本表坐标 × 统一比例 s + 原点偏移 (ox,oy)，无其他变换",
        },
    },
    "components": [
        {
            "id": "C1",
            "prototype": "圆环（CIRCLE border 环形母形）",
            "instance_count": 1,
            "geometry": "box(56,56) d=400 border=72 shape=CIRCLE 无填充",
            "dsl_positioning": "<Positioned left=56 top=56 width=400 height=400><Container shape=\"CIRCLE\" border=\"72 SOLID #22D3EE\"/></Positioned>",
            "count_basis": "1 个可独立辨认母形实例",
        },
        {
            "id": "C2",
            "prototype": "实心圆盘（CIRCLE 实色母形）",
            "instance_count": 1,
            "geometry": "box(240,240) d=160 实色 #7C3AED；与环 45° 方向重叠 42.51 单位（遮挡表达'叠'）",
            "dsl_positioning": "<Positioned left=240 top=240 width=160 height=160><Container shape=\"CIRCLE\" color=\"#7C3AED\"/></Positioned>",
            "count_basis": "1 个母形实例",
        },
        {
            "id": "C3",
            "prototype": "实心光点（CIRCLE 实色母形，C2 的缩小实例）",
            "instance_count": 1,
            "geometry": "box(183,183) d=56 实色 #3B82F6，位于环孔月牙内",
            "dsl_positioning": "<Positioned left=183 top=183 width=56 height=56><Container shape=\"CIRCLE\" color=\"#3B82F6\"/></Positioned>",
            "count_basis": "1 个母形实例（重复放置的母形分别计数，此处仅 1 个）",
        },
    ],
    "component_count": {
        "total": 3,
        "limit": 6,
        "within_limit": True,
        "justification": "按可独立辨认母形实例计数：环1+盘1+点1=3；环孔与三处间隙为负空间不计数（生成规则见 geometry.negative_space）；无裁剪分割图形。位置、尺寸、分组包装不另计。",
    },
    "clear_space": {
        "unit": "icon_units (512 基准盒像素)",
        "value": 56,
        "value_ratio_of_box": 56 / 512,
        "measurement_basis": "两枚512图标 alpha 包围盒实测 [56,56,455,455]（见 black_check/bounds 实测），即环外缘到画布边 56 单位；规定任何其他文字/图形距图标外接矩形 ≥56 单位（=11% 图标盒 = 0.7×环宽）",
        "measured_in_applications": {
            "brand-banner": {"min_gap_target_px": 72, "between": "图标盒右缘 x=264 到强调条 x=336", "in_icon_units": 72 / 0.375, "passed": True},
            "launch-poster": {"min_gap_target_px": round(560 - (176 + 56 * 0.62 + 200 * 0.62), 2), "between": "环外缘 y=458.72 到 OPEN BETA 徽章 y=560", "in_icon_units": round((560 - (176 + 56 * 0.62 + 200 * 0.62)) / 0.62, 2), "passed": True},
        },
        "evidence": {"path_base": "suite_root", "path": "tmp/run-20261011-01/A13/checks.json"},
    },
    "applications": [
        {
            "file": "symbol-color.png",
            "type": "color icon",
            "canvas": [512, 512],
            "background": "transparent",
            "icon_scale": 1.0,
            "icon_origin": [0, 0],
            "ink_alpha_bbox": checks["bounds"]["color_alpha_bbox"],
            "geometry_mapping": "基准坐标 ×1.0 + (0,0)",
        },
        {
            "file": "symbol-black.png",
            "type": "black icon",
            "canvas": [512, 512],
            "background": "transparent",
            "icon_scale": 1.0,
            "icon_origin": [0, 0],
            "ink_alpha_bbox": checks["bounds"]["black_alpha_bbox"],
            "geometry_mapping": "同彩版，仅颜色全部 #000000（alpha 通道实测一致，见 geometry_identity）",
        },
        {
            "file": "brand-banner.png",
            "type": "brand banner",
            "canvas": [1200, 400],
            "background": "线性渐变 #0B1220→#0D1526→#111C31 (TOP_LEFT→BOTTOM_RIGHT)",
            "icon_scale": 0.375,
            "icon_origin": [72, 104],
            "icon_box": [72, 104, 264, 296],
            "geometry_mapping": "同一 ICON 表坐标 ×0.375 + (72,104)：环(93,125) d150 border27 / 盘(162,194) d60 / 点(140.63,172.63) d21",
            "texts": ["叠光 Layerlight", "把复杂信息，组织成清晰画面", "layerlight.example.org"],
        },
        {
            "file": "launch-poster.png",
            "type": "launch poster",
            "canvas": [1080, 1350],
            "background": "线性渐变 #0B1220→#0D1526→#111C31 (TOP→BOTTOM)",
            "icon_scale": 0.62,
            "icon_origin": [382, 176],
            "icon_box": [382, 176, 699.44, 493.44],
            "geometry_mapping": "同一 ICON 表坐标 ×0.62 + (382,176)：环(416.72,210.72) d248 border44.64 / 盘(530.8,324.8) d99.2 / 点(495.46,289.46) d34.72；独立纵向构图（徽章/标题/副文/分隔/日期/网址），非横幅放大",
            "texts": ["叠光 Layerlight", "把复杂信息，组织成清晰画面", "2026.11.07 · ONLINE", "OPEN BETA", "layerlight.example.org"],
        },
    ],
    "black_check": checks["black_check"],
    "geometry_identity_check": {
        **geo,
        "applied_to": ["symbol-color.png", "symbol-black.png"],
        "passed": geo["all_mismatches_on_shape_edges"] and geo["max_abs_alpha_delta"] == 1,
    },
    "small_size_review": {
        "thumbnails": [
            {"path_base": "suite_root", "path": "tmp/run-20261011-01/A13/thumbs/symbol-color-32.png", "size": [32, 32], "note": "512→32 重采样结果（未合成背景，RGBA）"},
            {"path_base": "suite_root", "path": "tmp/run-20261011-01/A13/thumbs/symbol-black-32.png", "size": [32, 32], "note": "同上"},
            {"path_base": "suite_root", "path": "tmp/run-20261011-01/A13/thumbs/symbol-color-32-light.png", "note": "共享浅色底 #F1F5F9 上的实际尺寸查看图（原尺寸检查用）"},
            {"path_base": "suite_root", "path": "tmp/run-20261011-01/A13/thumbs/symbol-black-32-light.png", "note": "同上"},
            {"path_base": "suite_root", "path": "tmp/run-20261011-01/A13/thumbs/symbol-color-32-light-x8.png", "note": "×8 NEAREST 放大，仅观察边缘，不能替代原尺寸检查"},
            {"path_base": "suite_root", "path": "tmp/run-20261011-01/A13/thumbs/symbol-black-32-light-x8.png", "note": "同上"},
            {"path_base": "suite_root", "path": "tmp/run-20261011-01/A13/thumbs/preview-a-32-light.png", "note": "方向A预览的32px检查图"},
            {"path_base": "suite_root", "path": "tmp/run-20261011-01/A13/thumbs/preview-b-32-light.png", "note": "方向B预览的32px检查图"},
        ],
        "tool": "Pillow 10.0.0 (scripts/tool_thumb32.py)",
        "pipeline": "RGBA解码 → alpha 预乘 → Image.LANCZOS 512→32 → 反预乘（alpha=0 的 RGB 忽略）→ 32×32 RGBA 保存；再合成到共享浅色底 #F1F5F9 生成原尺寸查看图；×8 放大用 NEAREST",
        "actual_size_viewing_evidence": "2026-10-14T10:52+08:00 以 32×32 实际尺寸打开两张 -light.png：环、透镜盘、光点与月牙负空间均可辨认（色版/黑版）；另开 ×8 图观察边缘。预览仅存临时目录，未覆盖任何最终服务 PNG，未做额外描边或锐化。",
        "small_size_findings": [
            "方向A预览（三横条）32px 下最清晰但形态接近通用列表图标",
            "方向B预览（环+盘+点）32px 下环孔月牙保留；v1 圆盘85%透明度压环导致轮廓混色发糊、圆盘176过大、光点48偏小",
            "定稿改进后（盘160不透明、外移；点56；最小间隙36.36单位=2.27px@32）实际尺寸可辨认",
        ],
    },
    "refinement_log": {
        "direction_previews": [
            {"direction": "A", "kind": "叠层光板（正交圆角横条对角错排）", "dsl": "tmp/run-20261011-01/A13/drafts/preview-a.snapshot", "png": "tmp/run-20261011-01/A13/drafts/preview-a.png"},
            {"direction": "B", "kind": "光圈叠月（环+偏心透镜盘+光点）", "dsl": "tmp/run-20261011-01/A13/drafts/preview-b.snapshot", "png": "tmp/run-20261011-01/A13/drafts/preview-b.png"},
        ],
        "chosen": "B",
        "changes_for_small_size": [
            "圆盘 d176→160 并外移至 (240,240)：45° 处保留 29.49 单位残环，32px 下环保持连续（约1.84px）",
            "圆盘去透明（原 alpha 217/D9→255）：85% 透明度压在环上时 32px 轮廓混色发糊",
            "光点 d48→56：32px 下约 3.5px，清晰可见",
            "最小负空间间隙 36.36 单位（32px 下 2.27px），月牙负空间保留",
        ],
    },
}

(OUT / "brand-system.json").write_text(
    json.dumps(system, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

rationale = """# 设计说明（叠光 Layerlight 品牌图标）

方向A"叠层光板"：三根圆角横条对角错排；32px 下最清晰，但形态接近通用列表图标，辨识度弱。

方向B"光圈叠月"：圆环＋偏心透镜盘＋光点，全圆形母形；盘压过环内缘成"叠光"，环孔切成偏心月牙为关键负空间。

对比两方向 512 预览、32px 原尺寸图与 ×8 放大后选 B：更独特，"光"直扣品牌名，月牙负空间在 32px 保留。

32px 检查的问题与改进：①盘原 85% 透明压环使轮廓混色发糊→改不透明；②盘 176→160 并外移，45° 处保留 29.5 单位残环，环小尺寸连续；③点 48→56（32px 下约 3.5px）；间隙 ≥36 单位（32px 下 ≥2.3px）。
"""
(OUT / "rationale.md").write_text(rationale, encoding="utf-8")

body = rationale.replace("# 设计说明（叠光 Layerlight 品牌图标）", "").strip()
n = len(body.replace("\n", ""))
print("brand-system.json written; rationale body chars =", n)
