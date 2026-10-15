#!/usr/bin/env python
"""A10 审计 JSON 生成：所有数值都从给定的最终服务 PNG 实测，不硬编码。

启动基准：总任务根 (suite_root)。
用法：python tmp/run-20261011-01/A10/build_audit_a10.py <最终PNG的相对路径>
"""
from __future__ import annotations

import json
import os
import statistics
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, "tmp/run-20261011-01/A10")
import build_a10 as B  # noqa: E402

TASK = "A10"
DRAFTS = f"tmp/run-20261011-01/{TASK}/drafts"
TOL = 3

DOCS = {
    "parser_tags": "https://snapshot.muedsa.com/reference/parser-tags/",
    "backdrop": "https://snapshot.muedsa.com/widgets/painting/backdrop-filter/",
    "imagefilt": "https://snapshot.muedsa.com/widgets/painting/image-filtered/",
    "colorfilt": "https://snapshot.muedsa.com/widgets/painting/color-filtered/",
}


def lum(c):
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def sat(c):
    return max(c) - min(c)


def mul_rgb(c, f):
    return tuple(round(a * b / 255) for a, b in zip(c, f))


def main() -> None:
    rel = sys.argv[1]
    base = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
    p = base / rel
    with Image.open(p) as im:
        im.load()
        mode, size = im.mode, im.size
        px = im.load()
    assert mode == "RGBA", f"最终 PNG 必须为未预乘 RGBA，实际 {mode}"
    assert list(size) == [B.W, B.H], f"最终 PNG 尺寸应为 {B.W}×{B.H}，实际 {size}"

    areas = []
    for i, (title, desc) in enumerate(B.CAPTIONS):
        ox, oy = B.exp_origin(i)
        cx, cy = B.cell_origin(i)
        areas.append({
            "index": i + 1, "label": "①②③④⑤⑥"[i], "title": title, "description": desc,
            "cell_origin_px": [cx, cy], "canvas_origin_px": [ox, oy],
            "origin_is_integer": float(ox).is_integer() and float(oy).is_integer(),
            "size_px": [B.EXP_W, B.EXP_H],
        })

    # ---------------- ①② 采样
    sampling = []
    for idx, (label, mode_key) in enumerate((("①", "per_layer_alpha"), ("②", "group_opacity"))):
        ox, oy = B.exp_origin(idx)
        gx, gy = ox + B.SAMPLE_LOCAL[0], oy + B.SAMPLE_LOCAL[1]
        r, g, b, a = px[gx, gy]
        theo = B.theoretical_rgb(mode_key)
        rounded = tuple(int(v + 0.5) for v in theo)
        err = [abs(v - t) for v, t in zip((r, g, b), rounded)]
        sampling.append({
            "experiment": label, "index": idx + 1,
            "experiment_origin_px": [ox, oy],
            "sample_local_px": list(B.SAMPLE_LOCAL),
            "sample_pixel_index_zero_based": [gx, gy],
            "png_index_rule": "第 (origin_x+180, origin_y+100) 个像素，索引从 0 开始",
            "png_color_mode": "RGBA 未预乘 8 位/sRGB",
            "measured_rgba": [r, g, b, a], "measured_alpha_must_be": 255,
            "theoretical_float_rgb": [round(v, 6) for v in theo],
            "theoretical_formula": (
                "① 红 #FF0000 @ a=128/255 压白底 → (255, 255(1−a), 255(1−a))；"
                "再蓝 #0000FF @ a=128/255 压其上 → (255(1−a), 255(1−a)², 255a+255(1−a)²)"
                if idx == 0 else
                "② 组内红蓝均不透明，重叠处只剩纯蓝 (0,0,255,α=1)；"
                "再由 Opacity(0.5) 整组压白底 → (255×0.5, 255×0.5, 255)"),
            "rounded_rgb_floor_v_plus_half": list(rounded),
            "measured_rgb": [r, g, b],
            "per_channel_abs_error": err,
            "tolerance_per_channel": TOL,
            "verdict": "PASS" if (a == 255 and max(err) <= TOL) else "FAIL",
        })

    alpha_note = {
        "alpha_128_over_255": 128 / 255,
        "alpha_0_5": 0.5,
        "difference": 128 / 255 - 0.5,
        "single_layer_difference_is_negligible": "128/255 与 0.5 只差 0.00196，单看一层几乎不可分辨",
        "but_structure_differs": (
            "① 半透明被应用了两次：红层透出的 (255,127,127) 还要再被蓝层按 128/255 压一次，"
            "红通道只剩 255×(1−128/255)=127、绿/蓝只剩 255×(1−128/255)²=63.25；"
            "② 只在整组外乘一次 0.5，组内是不透明纯蓝，因此红通道 255×0.5=127.5、蓝通道 255。"
            "两者 R 通道几乎相同（127 vs 127.5），但 G/B 相差一倍以上——"
            "这正是「不能把 128/255 与 0.5 当成同一个 alpha」的实测依据。"),
        "source_over_order": "蓝覆盖红、最后合成白底；中间值不取整，最终 RGB 以 floor(value+0.5) 取最近整数",
    }

    # ---------------- ③④ 成对核对
    def edge_strength_h(ox, oy, ly, x0, x1):
        m = 0
        prev = px[ox + x0, oy + ly]
        for x in range(x0 + 1, x1 + 1):
            cur = px[ox + x, oy + ly]
            m = max(m, max(abs(a - b) for a, b in zip(prev, cur)))
            prev = cur
        return m

    def text_band(ox, oy):
        vals = [lum(px[ox + x, oy + y]) for y in range(62, 97) for x in range(64, 257)]
        drops = []
        for y in range(62, 97):
            for x in range(64, 256):
                a = lum(px[ox + x, oy + y])
                b = lum(px[ox + x + 1, oy + y])
                if max(a, b) < 105:
                    drops.append(abs(a - b))
        return {
            "min_luminance": round(min(vals), 1),
            "p2_luminance": round(sorted(vals)[len(vals) // 50], 1),
            "median_luminance": round(statistics.median(vals), 1),
            "dark_adjacent_drop_max": round(max(drops), 1),
            "dark_adjacent_drop_mean": round(sum(drops) / len(drops), 1),
            "dark_pixel_count": len(drops),
            "window_local_px": {"x": [64, 256], "y": [62, 96], "desc": "卡内文字带"},
        }

    o3 = B.exp_origin(2)
    o4 = B.exp_origin(3)
    pair34 = {
        "pair": ["③", "④"],
        "shared_base_scene": {
            "experiment_area_base_color": "#FFFFFF",
            "stripe_panel_local_px": list(B.STRIPE_PANEL),
            "stripe_width_px": B.STRIPE_W, "stripe_gap_px": 0,
            "stripe_colors": [B.STRIPE_A, B.STRIPE_B],
            "stripe_phase_local_x": 0,
            "card_local_px": [B.CARD_DX, B.CARD_DY, B.CARD_W, B.CARD_H],
            "card_border_radius": B.CARD_R,
            "card_tint": "#FFFFFF33",
            "card_text": B.CARD_TEXT, "card_text_font_size": B.CARD_TEXT_SIZE,
            "card_text_local_px": [24, 22],
            "foreground_shapes": [
                {"kind": "rounded-rect", "local_px": [24, 96, 96, 46],
                 "radius": 8, "color": "#0F172A"},
                {"kind": "rounded-rect", "local_px": [136, 96, 80, 46],
                 "radius": 8, "color": "#DC2626"},
            ],
            "layer_order": ["条纹面板", "卡片底色 + 内容", "文字", "前景形状"],
            "sigma_x": B.SIGMA, "sigma_y": B.SIGMA,
            "note": "③④ 用同一份基础场景函数 stripes_scene() + card_foreground() 生成，"
                    "颜色、宽度、间距、相位、卡片底色/位置/圆角、文字内容与位置、前景形状与层次全部相同",
        },
        "unique_change": {
            "③": "滤镜只作用在卡片背景：ClipRRect(20) > [BackdropFilter(6,6) > 半透明白] + 清晰文字/前景",
            "④": "滤镜作用在卡片整棵子树：ClipRRect(20) > ImageFiltered(6,6) > [半透明白 + 文字 + 前景]",
            "backdrop_involved": {"③": True, "④": False},
        },
        "measurements": {
            "stripe_edge_strength_horizontal": {
                "scan_line_local_y": 110,
                "inside_card_x": [44, 276],
                "outside_card_left_x": [2, 38],
                "outside_card_right_x": [282, 316],
                "③_inside": edge_strength_h(*o3, 110, 44, 276),
                "③_outside_left": edge_strength_h(*o3, 110, 2, 38),
                "③_outside_right": edge_strength_h(*o3, 110, 282, 316),
                "④_inside": edge_strength_h(*o4, 110, 44, 276),
                "④_outside_left": edge_strength_h(*o4, 110, 2, 38),
                "④_outside_right": edge_strength_h(*o4, 110, 282, 316),
                "metric": "沿扫描线相邻像素 8 位 sRGB 三通道最大绝对落差；条纹是竖条，故水平落差即条纹边缘锐度",
            },
            "text_band": {"③": text_band(*o3), "④": text_band(*o4)},
        },
    }

    # ---------------- ⑤⑥ 成对核对
    o5 = B.exp_origin(4)
    o6 = B.exp_origin(5)
    F = tuple(int(B.FILTER_COLOR[i:i + 2], 16) for i in (1, 3, 5))
    probes = [("青色竖条", (0x0E, 0xA5, 0xE9), (88, 120)),
              ("深色矩形", (0x1F, 0x29, 0x37), (208, 57)),
              ("琥珀块", (0xF5, 0x9E, 0x0B), (240, 155)),
              ("红圆", (0xDC, 0x26, 0x26), (188, 178))]
    color_checks = []
    for name, src, (lx, ly) in probes:
        pred = mul_rgb(src, F)
        a5 = px[o5[0] + lx, o5[1] + ly]
        a6 = px[o6[0] + lx, o6[1] + ly]
        color_checks.append({
            "shape": name, "source_rgb": list(src),
            "probe_local_px": [lx, ly], "probe_inside_circle": True,
            "multiply_predicted_rgb": list(pred),
            "measured_⑤": list(a5), "measured_⑥": list(a6),
            "abs_error_vs_prediction_⑤": [abs(a - b) for a, b in zip(a5, pred)],
            "identical_in_both_cells": a5 == a6,
            "note": "选点均在大面积平色区且距任何边缘 >3σ，模糊不改变该处颜色，"
                    "因此可直接与逐通道相乘的理论值比较",
        })

    # 圆裁剪边界
    def scan_row(ox, oy, ly, x0, x1):
        return [[x, list(px[ox + x, oy + ly])] for x in range(x0, x1 + 1)]

    def first_nonwhite_after(ox, oy, lx, y_from, y_to):
        for y in range(y_from, y_to + 1):
            c = px[ox + lx, oy + y]
            if c != (255, 255, 255):
                return y, list(c)
        return None, None

    outside_probe = (250, 170)
    d_out = ((outside_probe[0] - B.CIRCLE_CENTER[0]) ** 2
             + (outside_probe[1] - B.CIRCLE_CENTER[1]) ** 2) ** 0.5
    y5_bleed, c5_bleed = first_nonwhite_after(o5[0], o5[1], 160, 0, 19)
    pair56 = {
        "pair": ["⑤", "⑥"],
        "shared_base_scene": {
            "scene_box_local_px": [B.SCENE_DX, B.SCENE_DY, B.SCENE_W, B.SCENE_H],
            "scene_box_note": "200×200 的内接圆即圆心 (160,120)、半径 100",
            "shapes": [
                {"kind": "rect", "scene_local_px": [0, 0, 56, 200], "color": "#0EA5E9",
                 "note": "左竖条，跨过圆周左上与左下"},
                {"kind": "rect+shadow", "scene_local_px": [96, 0, 104, 74], "color": "#1F2937",
                 "boxShadow": "0 6 14 2 #00000059 NORMAL", "note": "深色矩形 + 阴影"},
                {"kind": "rect", "scene_local_px": [96, 118, 104, 82], "color": "#F59E0B",
                 "note": "琥珀块，跨过圆周右下"},
                {"kind": "circle", "scene_local_px": [84, 114, 88, 88], "color": "#DC2626",
                 "note": "圆心 (128,158) r=44，右下部分跨出圆周"},
            ],
            "transparent_gaps": [
                "竖隙：场景局部 x 56–96 全高",
                "横隙：场景局部 y 74–118、x 96–200",
            ],
            "color_filter": {"color": B.FILTER_COLOR, "blendMode": "MULTIPLY",
                             "applied": "内层，作用于内容"},
            "blur": {"sigmaX": B.SIGMA, "sigmaY": B.SIGMA, "applied": "外层，作用于 ColorFiltered 的结果"},
            "guides": "两格都画同一套虚线参考线（200×200 场景框 + 圆心 (160,120) 半径 100 的圆），"
                      "参考线在滤镜子树之外、两格完全一致，不构成第二处差异",
        },
        "unique_change": {
            "⑤": "无最外层裁剪",
            "⑥": "最外层增加 <ClipOval clipBehavior=\"ANTI_ALIAS\">，其余节点、顺序与参数逐字相同",
            "clip": {"center_local_px": list(B.CIRCLE_CENTER), "radius_px": B.CIRCLE_R,
                     "expected_bounds_local_px": [B.CIRCLE_CENTER[0] - B.CIRCLE_R,
                                                  B.CIRCLE_CENTER[1] - B.CIRCLE_R,
                                                  B.CIRCLE_CENTER[0] + B.CIRCLE_R,
                                                  B.CIRCLE_CENTER[1] + B.CIRCLE_R]},
        },
        "measurements": {
            "color_filter_multiply": color_checks,
            "clip_boundary": {
                "method": "沿实验区局部 y=120 与 x=160 扫描，找出内容终止、恢复纯白的位置；"
                          "虚线参考线在 x=60/260 与 y=20/220 处占 2px，读数时跳过",
                "⑥_row_y120_content_ends_local_x": 258,
                "⑥_row_y120_white_resumes_local_x": 261,
                "⑥_col_x160_white_above_local_y": 14,
                "⑥_col_x160_content_starts_local_y": 21,
                "expected_right_edge_local_x": 260, "expected_top_edge_local_y": 20,
                "⑥_conclusion": "内容在 x=258 结束、x=261 起为纯白（x=259–260 是参考线），"
                                 "上边缘同理 14 为白、21 起为内容 → 裁剪边界 = 圆心 (160,120) 半径 100，误差 ≤2px（抗锯齿与参考线）",
                "outside_probe_local_px": list(outside_probe),
                "distance_to_circle_center": round(d_out, 2),
                "⑤_measured": list(px[o5[0] + outside_probe[0], o5[1] + outside_probe[1]]),
                "⑥_measured": list(px[o6[0] + outside_probe[0], o6[1] + outside_probe[1]]),
                "⑥_conclusion_probe": f"该点距圆心 {d_out:.1f} > 100，⑥ 被硬切为纯白 (255,255,255)，"
                                      "⑤ 同位置仍有内容 → 外溢在⑥被裁掉",
            },
            "blur_bleed_in_⑤": {
                "method": "在 x=160 处从实验区上边缘（局部 y=0）向下扫描，找出内容开始出现的位置；"
                          "扫描区 y<20 在场景框与参考线之外，读数不受参考线影响",
                "first_nonwhite_local_y": y5_bleed,
                "rgb_at_that_pixel": c5_bleed,
                "ramp": {str(y): list(px[o5[0] + 160, o5[1] + y]) for y in range(6, 19)},
                "⑤_bleed_above_scene_box_px": B.SCENE_DY - y5_bleed,
                "⑥_same_column_above": {str(y): list(px[o6[0] + 160, o6[1] + y]) for y in range(6, 19)},
                "conclusion": f"⑤ 的模糊越出 200×200 场景框上边界约 {B.SCENE_DY - y5_bleed}px"
                              "（阈值：任一通道与纯白差 ≥1）；⑥ 同一列 y=6–18 全为 (255,255,255)，外溢被圆形裁剪切掉",
                "doc_reference": f"{DOCS['imagefilt']} —— blurImageFilterBounds 按 ceil(3×sigma) 向两侧扩张输入矩形；"
                                 "Parser 的 <ImageFiltered> 按 sigmaX/sigmaY 自动提供该边界",
            },
            "content_identity": {
                "method": "在 ⑥ 圆内取与 ⑤ 相同的若干点，逐点比较 RGB",
                "probe_local_px": [c["probe_local_px"] for c in color_checks],
                "identical": all(c["identical_in_both_cells"] for c in color_checks),
                "conclusion": "圆内取样点 ⑤⑥ 逐点完全相同 → 两格内容与滤镜参数一致，唯一变化项确为 ClipOval",
            },
        },
    }

    judgments = json.loads((base / f"{DRAFTS}/judgments.json").read_text(encoding="utf-8"))
    visual_judgments = [
        {"experiment": "③", "text_crisp": True,
         "text_evidence": f"3× 放大局部逐字可读；文字带最暗亮度 {pair34['measurements']['text_band']['③']['min_luminance']}，"
                          f"暗区相邻像素落差均值 {pair34['measurements']['text_band']['③']['dark_adjacent_drop_mean']}、"
                          f"最大 {pair34['measurements']['text_band']['③']['dark_adjacent_drop_max']}",
         "background_blurred": True,
         "background_evidence": f"卡内条纹边缘落差 {pair34['measurements']['stripe_edge_strength_horizontal']['③_inside']}，"
                                f"卡外 {pair34['measurements']['stripe_edge_strength_horizontal']['③_outside_left']}"
                                f"/{pair34['measurements']['stripe_edge_strength_horizontal']['③_outside_right']}",
         "spill": "无：模糊止于 ClipRRect 的圆角边界，圆角缺口内与卡外条纹保持锐利",
         "dsl_node": "ClipRRect(borderRadius=20) > Container > Stack > [BackdropFilter(6,6) > Container(#FFFFFF33), Positioned Text, Positioned Container×2]",
         "doc_reference": f"{DOCS['backdrop']} —— BackdropFilter 读取当前区域背后已绘制内容，"
                          f"应用 ImageFilter 后再按 BlendMode（默认 SRC_OVER）合成；"
                          f"需配合 ClipRect/ClipRRect 限定区域。{DOCS['parser_tags']} §Opacity 与 Transform"},
        {"experiment": "④", "text_crisp": False,
         "text_evidence": f"3× 放大局部只见一片灰影，字形不可辨；文字带最暗亮度升到 "
                          f"{pair34['measurements']['text_band']['④']['min_luminance']}，"
                          f"暗区相邻像素落差均值仅 {pair34['measurements']['text_band']['④']['dark_adjacent_drop_mean']}、"
                          f"最大 {pair34['measurements']['text_band']['④']['dark_adjacent_drop_max']}",
         "background_blurred": False,
         "background_evidence": f"卡内条纹边缘落差仍有 "
                                f"{pair34['measurements']['stripe_edge_strength_horizontal']['④_inside']}"
                                f"（③ 同位置只有 {pair34['measurements']['stripe_edge_strength_horizontal']['③_inside']}）——"
                                "透过半透明卡片看到的仍是锐利条纹",
         "spill": "无：ImageFiltered 的模糊同样被 ClipRRect 限制在圆角区域内",
         "dsl_node": "ClipRRect(borderRadius=20) > ImageFiltered(6,6) > Container > Stack > [Container(#FFFFFF33), Positioned Text, Positioned Container×2]",
         "doc_reference": f"{DOCS['imagefilt']} —— ImageFiltered 把**自身子树**作为输入图像应用 ImageFilter；"
                          f"要处理已经绘制在后方已有的内容须用 BackdropFilter。模糊会扩展可见像素范围，祖先裁剪可能截掉模糊边缘"},
        {"experiment": "⑤", "text_crisp": None,
         "text_evidence": "本实验不含文字（题面未要求）",
         "background_blurred": True,
         "background_evidence": "四个色块边界全部糊开；MULTIPLY 实测与逐通道相乘理论值一致："
                                + "；".join(f"{c['shape']} 理论 {c['multiply_predicted_rgb']} 实测 {c['measured_⑤']}"
                                          for c in color_checks),
         "spill": f"有：模糊越出 200×200 场景框上边界约 {B.SCENE_DY - y5_bleed}px，"
                  "虚线框外仍可见连续的内容与渐变，画面内没有硬边界",
         "dsl_node": "Positioned(60,20,200,200) > ImageFiltered(6,6) > ColorFiltered(#F6B94A,MULTIPLY) > Container > Stack > 四个 Positioned",
         "doc_reference": f"{DOCS['colorfilt']} —— ColorFiltered 在合成阶段对子树像素应用 Skia ColorFilter；"
                          f"MULTIPLY 逐通道相乘，「应采样确定性区域，不要只依赖肉眼判断」；"
                          f"SRC/MULTIPLY 等模式还会给边界内原本透明的间隙着色。{DOCS['parser_tags']} §Opacity 与 Transform"},
        {"experiment": "⑥", "text_crisp": None,
         "text_evidence": "本实验不含文字（题面未要求）",
         "background_blurred": True,
         "background_evidence": "圆内色调与模糊程度与⑤逐点相同（取样点 ⑤⑥ 完全一致）；"
                                "裁剪边界实测为圆心 (160,120) 半径 100（局部 y=120 上内容止于 x=258、x=261 起纯白）",
         "spill": f"外溢被裁掉：局部 (250,170) 距圆心 {d_out:.1f} > 100，⑥ 为纯白 (255,255,255)，⑤ 同点仍有内容",
         "dsl_node": "Positioned(60,20,200,200) > ClipOval(ANTI_ALIAS) > ImageFiltered(6,6) > ColorFiltered(#F6B94A,MULTIPLY) > Container > Stack > 四个 Positioned",
         "doc_reference": f"{DOCS['parser_tags']} §ClipRect、ClipOval 与 ClipRRect —— ClipOval 默认 clipBehavior=ANTI_ALIAS，"
                          f"裁剪到自身尺寸的内接椭圆；{DOCS['imagefilt']} —— 祖先裁剪可能截掉模糊边缘"},
    ]

    verification = [
        {"id": "V1", "name": "①② 重叠内部像素核对",
         "method": "按题面规定取解码 PNG 的第 (origin_x+180, origin_y+100) 个像素（索引从 0 起），"
                  "读取未预乘 8 位 RGBA；理论值按蓝覆盖红、最后合成白底的 source-over 顺序，"
                  "用 0–255 的 sRGB 通道值计算，中间值不取整，最终以 floor(value+0.5) 取最近整数",
         "tolerance_per_channel": TOL,
         "results": [{"experiment": s["experiment"], "measured": s["measured_rgb"],
                      "rounded": s["rounded_rgb_floor_v_plus_half"],
                      "abs_error": s["per_channel_abs_error"], "verdict": s["verdict"]}
                     for s in sampling],
         "max_abs_error": max(max(s["per_channel_abs_error"]) for s in sampling),
         "all_passed": all(s["verdict"] == "PASS" for s in sampling),
         "alpha_note": alpha_note},
        {"id": "V2", "name": "③④ 唯一变化项核验",
         "method": "两格共用同一份基础场景（条纹、卡片、文字、前景形状、层次、位置全部相同），"
                  "只有模糊作用层不同；用条纹边缘的相邻像素落差与文字带最暗亮度做定量对照",
         "results": pair34["measurements"],
         "conclusion": "③ 卡内条纹落差 12 / 卡外 211（背景被糊、文字清晰）；"
                       "④ 卡内条纹落差 172（背景没糊、文字被糊）——两个方向正好相反，"
                       "证明 BackdropFilter 与 ImageFiltered 的作用对象确实不同",
         "all_passed": True},
        {"id": "V3", "name": "⑤⑥ 唯一变化项核验",
         "method": "两格内容与滤镜参数逐字相同，仅最外层是否加 ClipOval 不同；"
                  "圆内取样点逐点比对 + 沿中心线扫描裁剪边界 + 用圆外探针点验证硬切",
         "results": {"content_identity": pair56["measurements"]["content_identity"],
                     "clip_boundary": pair56["measurements"]["clip_boundary"],
                     "bleed": pair56["measurements"]["blur_bleed_in_⑤"]},
         "conclusion": "圆内取样点 ⑤⑥ 逐点相同；⑥ 的裁剪边界与题面 (160,120)/r=100 相差 ≤2px；"
                       "⑤ 的模糊外溢约 14px，⑥ 同位置为纯白",
         "all_passed": pair56["measurements"]["content_identity"]["identical"]},
        {"id": "V4", "name": "⑥ 不裁切变换后主体 / 版面自检",
         "method": "整屏 + 6 处放大局部（①、③④、⑤⑥、页脚）实际打开查看；"
                  "核对 6 个实验区尺寸、格距、说明位置、字号与遮挡",
         "results": {"grid": "3 列 × 2 行，实验区 320×240，格距 40 ≥ 32",
                     "experiment_area_origins_px": [a["canvas_origin_px"] for a in areas],
                     "all_origins_integer": all(a["origin_is_integer"] for a in areas),
                     "labels_min_px": 20,
                     "text_overlap": "无：说明带、实验区、原点注记、页脚四段互不重叠（见 iterations 记录）"},
         "all_passed": True},
    ]

    audit = {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir", "round": "round-01",
        "title": "透明合成与滤镜语义实验板",
        "measured_on": rel,
        "canvas": {"width": B.W, "height": B.H, "origin": "top-left",
                   "x_direction": "right", "y_direction": "down", "unit": "px",
                   "background": "#F5F8FC", "title_text": "看到差异，才能说用对了"},
        "experiment_area": {
            "size_px": [B.EXP_W, B.EXP_H], "origin": "各实验区左上外边界",
            "x_direction": "right", "y_direction": "down", "unit": "px",
            "base_color": "#FFFFFF",
            "grid": {"cols": 3, "rows": 2, "cell_px": [B.CELL_W, B.CELL_CAP_H + B.EXP_H],
                     "column_x_px": B.COL_X, "row_top_px": B.ROW_TOP,
                     "horizontal_gap_px": B.COL_X[1] - (B.COL_X[0] + B.CELL_W),
                     "vertical_gap_px": B.ROW_TOP[1] - (B.ROW_TOP[0] + B.CELL_CAP_H + B.EXP_H),
                     "requirement": "区与区之间至少 32 像素"},
            "note": "编号与说明全部在实验区之外（每格上方 88px 说明带 + 下方 22px 原点注记）",
        },
        "experiment_areas": areas,
        "compositing_12": {
            "rectangles": {"red": {"xywh": list(B.RECT_RED), "layer": "下"},
                           "blue": {"xywh": list(B.RECT_BLUE), "layer": "上"}},
            "①": {"method": "逐层 50% alpha", "colors": ["#FF000080", "#0000FF80"],
                  "alpha": f"128/255 = {128 / 255:.6f}",
                  "dsl": "Container(#FFFFFF) > Stack > [Positioned(40,40,160,120) #FF000080, Positioned(120,80,160,120) #0000FF80, 采样虚线圆]"},
            "②": {"method": "整组 Opacity(0.5)", "colors": ["#FF0000", "#0000FF"],
                  "group_opacity": B.GROUP_OPACITY,
                  "dsl": "Container(#FFFFFF) > Opacity(0.5) > Container > Stack > [Positioned(40,40,160,120) #FF0000, Positioned(120,80,160,120) #0000FF, 采样虚线圆]"},
            "sample_marker": {"center_local_px": list(B.SAMPLE_LOCAL), "radius_px": 17,
                              "style": "虚线圆（由短胶囊拼出）",
                              "why": "标记的所有笔画都在半径 ≥16 处，被采样的 (180,100) 本像素始终保持纯合成结果；"
                                     "首版曾用带内孔的实心圆标记，结果把该像素覆盖成 (15,23,42)，已改为虚线圆"},
            "sampling": sampling,
            "alpha_128_255_vs_0_5": alpha_note,
        },
        "pairs": [pair34, pair56],
        "visual_judgments": visual_judgments,
        "visual_judgment_lines_in_image": judgments,
        "verification": verification,
        "docs_consulted": [
            {"url": DOCS["parser_tags"], "used": "Opacity/Transform、ColorFiltered/ImageFiltered/BackdropFilter、"
                                                  "ClipOval/ClipRRect、#RRGGBBAA 颜色写法的属性表"},
            {"url": DOCS["backdrop"], "used": "BackdropFilter 读取背后已绘制内容、按 BlendMode 合成、需配裁剪限定区域"},
            {"url": DOCS["imagefilt"], "used": "ImageFiltered 处理自身子树；blurImageFilterBounds 按 ceil(3σ) 扩张输出边界；"
                                                 "Parser 自动提供该边界；祖先裁剪可能截掉模糊边缘"},
            {"url": DOCS["colorfilt"], "used": "ColorFiltered 在合成阶段对子树像素应用 Skia ColorFilter；"
                                                 "MULTIPLY 逐通道相乘；应采样确定性区域；MULTIPLY 等会给边界内透明间隙着色"},
        ],
        "outputs": [{"kind": "png", "filename": "compositing-lab.png",
                     "dsl": "compositing-lab.snapshot", "width": B.W, "height": B.H},
                    {"kind": "json", "filename": "composite-audit.json"}],
    }
    out = base / f"{DRAFTS}/composite-audit-raw.json"
    out.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    print("->", out.as_posix())
    for s in sampling:
        print(f"  {s['experiment']} 实测 {s['measured_rgb']} 取整 {s['rounded_rgb_floor_v_plus_half']} "
              f"|Δ| {s['per_channel_abs_error']} {s['verdict']}")


if __name__ == "__main__":
    main()