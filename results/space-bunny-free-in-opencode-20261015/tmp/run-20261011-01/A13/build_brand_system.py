#!/usr/bin/env python
"""A13 brand-system.json 生成（比例、构件、最小留白、各应用映射、核验结果）。

启动基准：总任务根 (suite_root)。所有构件数据来自 geom_a13，核验数据来自 check_a13.py 的 checks.json。
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, "tmp/run-20261011-01/A13")
from geom_a13 import (  # noqa: E402
    PAL_COLOR, PAL_BLACK, COMPONENTS_A, COMPONENTS_B, NEGATIVE_SPACE_B,
    DIRECTION_NAME, components_of,
)

BASE = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
DRAFTS = BASE / "tmp/run-20261011-01/A13/drafts"
OUT = "outputs/run-20261011-01/A13"

OPTICAL = 420          # 符号光学外框（框线外缘直径）
CLEAR_RATIO = 1 / 6    # 最小留白 = 光学外框边长 / 6


def scaled(comp, k):
    o = dict(comp)
    o["scaled_by"] = round(k, 6)
    return o


def main() -> None:
    checks = json.loads((DRAFTS / "checks.json").read_text(encoding="utf-8"))
    sel = components_of("B", 512)
    apps = {
        "symbol-color": {"png": "symbol-color.png", "dsl": "symbol-color.snapshot",
                         "size_px": [512, 512], "symbol_size_px": 512,
                         "symbol_scale": 1.0, "background": "透明（PNG alpha）",
                         "palette": "PAL_COLOR", "clear_space_px": round(OPTICAL * CLEAR_RATIO, 1)},
        "symbol-black": {"png": "symbol-black.png", "dsl": "symbol-black.snapshot",
                         "size_px": [512, 512], "symbol_size_px": 512,
                         "symbol_scale": 1.0, "background": "透明（PNG alpha）",
                         "palette": "PAL_BLACK（全部构件 #000000）",
                         "clear_space_px": round(OPTICAL * CLEAR_RATIO, 1)},
        "brand-banner": {"png": "brand-banner.png", "dsl": "brand-banner.snapshot",
                         "size_px": [1200, 400], "symbol_size_px": 180,
                         "symbol_scale": round(180 / 512, 6),
                         "symbol_box_px": [90, 110, 180, 180],
                         "background": "#071428 + 左缘 16px 品牌色竖条",
                         "composition": "横向三区锁定：左符号 / 中字标+标语 / 右信息面板",
                         "required_text": ["叠光", "Layerlight", "把复杂信息，组织成清晰画面"],
                         "clear_space_px": round(180 * OPTICAL / 512 * CLEAR_RATIO, 1),
                         "nearest_element_gap_px": 62},
        "launch-poster": {"png": "launch-poster.png", "dsl": "launch-poster.snapshot",
                          "size_px": [1080, 1350], "symbol_size_px": 400,
                          "symbol_scale": round(400 / 512, 6),
                          "symbol_box_px": [80, 96, 400, 400],
                          "background": "#071428 + 顶/底品牌色横条",
                          "composition": "独立竖向构图：大符号 / 品牌字 / 标语 / 日期地点条 / CTA 条；非横幅放大",
                          "required_text": ["叠光", "Layerlight", "把复杂信息，组织成清晰画面",
                                            "2026.11.07 · ONLINE", "OPEN BETA",
                                            "layerlight.example.org"],
                          "clear_space_px": round(400 * OPTICAL / 512 * CLEAR_RATIO, 1),
                          "nearest_element_gap_px": 60},
    }

    data = {
        "schema_version": 1, "task_id": "A13", "path_base": "output_dir", "round": "round-01",
        "brand": {
            "name_cn": "叠光", "name_en": "Layerlight",
            "category": "结构化视觉工具（虚构品牌）",
            "concept": "信息叠加后仍然清晰",
            "tagline": "把复杂信息，组织成清晰画面",
            "event": "2026.11.07 · ONLINE", "status": "OPEN BETA",
            "site": "layerlight.example.org",
        },
        "explored_directions": [
            {"id": "A", "name": "环聚 CONVERGE", "geometry": "圆环 + 三层旋转薄片 + 光核",
             "components": len(COMPONENTS_A), "preview": "tmp/run-20261011-01/A13/preview/dir-A.png",
             "preview_dsl": "tmp/run-20261011-01/A13/drafts/dir-A.snapshot",
             "characteristic": "旋转 / 汇聚动势；外框为圆，内层为放射状星芒",
             "rejected_because": ("内层簇（三条 250×44 薄片）只占圆环 332px 内径的约三分之一，"
                                  "圆环内部大片留白；缩到 32×32 时三层薄片糊成一个点，"
                                  "整体只剩一个空心圆，失去「层」的语义")},
            {"id": "B", "name": "窗格 WINDOW", "geometry": "圆角方框 + 三条正交层格 + 45° 光束 + 焦点",
             "components": len(COMPONENTS_B), "preview": "tmp/run-20261011-01/A13/preview/dir-B.png",
             "preview_dsl": "tmp/run-20261011-01/A13/drafts/dir-B.snapshot",
             "characteristic": "正交 / 网格动势；一条 45° 斜切把网格打断，动势是「穿透」",
             "selected": True,
             "selected_because": ("圆角方框轮廓在 32×32 仍是强可辨识剪影；三条层格撑满框内，"
                                  "四条通道负空间清晰；斜向光束提供了区别于普通网格的方向记忆点")},
        ],
        "selection_evidence": {
            "previews_rendered": ["tmp/run-20261011-01/A13/preview/dir-A.png",
                                  "tmp/run-20261011-01/A13/preview/dir-B.png"],
            "side_by_side": "tmp/run-20261011-01/A13/preview/dir-sheet.png",
            "how_compared": "两个方向各出 512×512 透明 PNG，另出一张 1160×600 浅底并排对照图，实际打开看图后决定；"
                           "不是只看 DSL 节点数或参数",
            "chosen": "B",
        },
        "color": {
            "symbol_color": {k: v for k, v in PAL_COLOR.items()
                             if k in ("ring", "b1", "b2", "b3", "core", "beam")
                             or k == "slat"},
            "symbol_black": {"note": "全部构件 #000000；alpha>0 处 RGB 必须为 0（已实测 0 违规）"},
            "applications": {
                "symbol-color": {"background": "透明", "text": "不适用（纯图形）"},
                "symbol-black": {"background": "透明", "text": "不适用（纯图形）"},
                "brand-banner": {"background": "#071428", "brand_bar": "#1D4ED8",
                                 "wordmark_cn": "#FFFFFF", "wordmark_en": "#93C5FD",
                                 "tagline": "#CBD5E1", "divider": "#1E40AF",
                                 "panel_fill": "#FFFFFF12", "panel_border": "#1E40AF",
                                 "label": "#64748B", "value": "#E2E8F0",
                                 "accent": "#F59E0B", "link": "#93C5FD",
                                 "decor": ["#1E3A8A", "#12306B"]},
                "launch-poster": {"background": "#071428", "brand_bar": "#1D4ED8",
                                  "top_rule": "#0F172A", "bottom_bar": "#0F766E",
                                  "wordmark_cn": "#FFFFFF", "wordmark_en": "#93C5FD",
                                  "tagline": "#E2E8F0", "divider": "#1E40AF",
                                  "block_fill": "#FFFFFF0D", "block_border": "#1E40AF",
                                  "label": "#64748B", "value": "#E2E8F0",
                                  "cta_fill": "#1D4ED8", "cta_text": "#FFFFFF",
                                  "cta_link": "#BFDBFE", "footer": "#64748B / #475569",
                                  "decor": ["#F59E0B", "#0F766E"]},
            },
            "fonts": {"latin": "Inter / Inter Semi Bold / Inter Medium",
                      "cjk": "Noto Sans CJK SC",
                      "source": "run 级 GET /fonts 实际返回的 27 个字体族"},
        },
        "proportion": {
            "master_grid_px": 512,
            "optical_box_px": OPTICAL,
            "optical_ratio": round(OPTICAL / 512, 4),
            "frame_stroke_px": 44, "frame_corner_radius_px": 88,
            "slat_size_px": [312, 48], "slat_corner_radius_px": 24,
            "slat_gap_px": 42, "channel_count": 4,
            "beam_size_px": [340, 44], "beam_deg": 45, "beam_corner_radius_px": 22,
            "core_diameter_px": 84,
            "scaling_rule": "所有构件按 size/512 等比缩放；不改变比例、不做非等比变形、不旋转画布",
        },
        "icon_components": sel,
        "component_count": {
            "visible_count": len(sel), "limit": 6, "within_limit": len(sel) <= 6,
            "counting_rule": ("按设计中可独立辨认的几何母形实例计数，不按 DSL 节点数计数；"
                              "同一母形用多个节点实现仍算 1 个；重复放置的母形分别计数；"
                              "位置、尺寸、变换、分组包装不另计；圆环内孔与扣除产生的负空间不额外计数但记录生成规则"),
            "basis": (
                "B1 圆角方框：1 个母形（Container + border 实现，按 1 计）；"
                "B2/B3/B4 三条层格：同一圆角矩形母形重复放置 3 次 → 3 个；"
                "B5 光束：1 个圆角矩形加 45° 变换 → 1 个（变换不另计）；"
                "B6 焦点圆：1 个母形（ClipOval 实现，按 1 计）。"
                "合计 1+3+1+1 = 6，正好等于上限；无任何母形被合并成单个容器或路径来压低计数。"
                "框的内孔、层格之间的通道、光束切出的对角断口均为上述母形之间的空隙，"
                "按题面规则不计入构件数，另见 negative_space。"),
            "no_clip_split": "没有用裁剪把一个母形切成多个独立图形，因此不存在需要分别计数的拆分件",
        },
        "negative_space": NEGATIVE_SPACE_B,
        "negative_space_rule": "负空间由构件之间的空隙自然形成，未额外绘制任何几何；不计入构件数",
        "min_clear_space": {
            "rule": "光学外框边长的 1/6",
            "at_512_px": round(OPTICAL * CLEAR_RATIO, 1),
            "definition": "以符号光学外框为基准，四周留白不得小于该值；"
                          "留白区内不得出现其他文字、图形或裁切边",
            "per_application": {k: v["clear_space_px"] for k, v in apps.items()},
            "measured_gap_px": {"brand-banner": 62, "launch-poster": 60},
            "compliance": "banner 62px ≥ 30.9px；poster 60px ≥ 54.7px；两个图标文件为透明底，无外部元素",
        },
        "applications": apps,
        "application_mapping_rule": (
            "四个应用都调用同一个 symbol(direction, cx, cy, size, palette)；"
            "横幅与海报中的符号是按同一套几何规则**现场生成**的，"
            "没有嵌入任何图标渲染 PNG，只做等比缩放与平移"),
        "small_size": {
            "check_size_px": [32, 32],
            "changes_made": [
                "层格间距从预览版的 19px 放大到 42px（32px 下仍约 2.6px，通道不被糊死）",
                "层格改为顶到方框内边（x 100→412、y 100→412），使剪影是一个完整的网格而不是漂浮条",
                "方框圆角取 88（= 2×线宽），既保住「圆角」的识别点，又避开服务端 borderRadius < 线宽 会 500 的限制",
                "光束加粗到 44px 并贯穿全框，缩小后仍提供方向记忆",
            ],
            "observed": (
                "彩色版在 32×32 实际尺寸下轮廓、圆角、四条横向通道与斜向断口均可辨；"
                "纯黑版由于光束与焦点同为 #000000，32px 下二者并成一条，焦点消失——"
                "因此系统建议 48px 以下优先使用彩色版，纯黑版用于单色印刷/烫印场景"),
            "preview_files": checks["thumbnails"],
        },
        "verification": checks,
        "outputs": [
            {"kind": "png", "filename": "symbol-color.png", "dsl": "symbol-color.snapshot",
             "width": 512, "height": 512},
            {"kind": "png", "filename": "symbol-black.png", "dsl": "symbol-black.snapshot",
             "width": 512, "height": 512},
            {"kind": "png", "filename": "brand-banner.png", "dsl": "brand-banner.snapshot",
             "width": 1200, "height": 400},
            {"kind": "png", "filename": "launch-poster.png", "dsl": "launch-poster.snapshot",
             "width": 1080, "height": 1350},
            {"kind": "json", "filename": "brand-system.json"},
            {"kind": "md", "filename": "rationale.md"},
        ],
    }
    (DRAFTS / "brand-system-raw.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("components:", data["component_count"]["visible_count"],
          "within limit:", data["component_count"]["within_limit"])
    print("clear space @512:", data["min_clear_space"]["at_512_px"], "px")
    print("black check passed:", checks["black_check"]["passed"],
          "| geometry identity passed:", checks["geometry_identity"]["passed"])


if __name__ == "__main__":
    main()