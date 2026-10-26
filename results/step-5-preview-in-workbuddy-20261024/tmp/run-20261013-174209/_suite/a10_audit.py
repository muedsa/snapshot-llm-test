# -*- coding: utf-8 -*-
"""A10 composite-audit.json generator with pixel sampling."""
from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A10"
OUT_DIR = ROOT / "outputs" / RUN_ID / TASK
TMP_DIR = ROOT / "tmp" / RUN_ID / TASK

from PIL import Image  # noqa: E402

IMG = Image.open(TMP_DIR / "iter2.png").convert("RGBA")
W, H = IMG.size

ORIGINS = {1: [208, 120], 2: [560, 120], 3: [912, 120],
           4: [208, 392], 5: [560, 392], 6: [912, 392]}
CELL_W, CELL_H = 320, 240
SAMPLE = (180, 100)


def rnd(v):
    return int(v + 0.5)


def over(fg, fa, bg):
    return [f * fa + b * (1 - fa) for f, b in zip(fg, bg)]


RED, BLUE, WHITE = [255, 0, 0], [0, 0, 255], [255, 255, 255]
A128 = 128 / 255

# ---------- ①② 理论值 ----------
# ① 红 #FF000080 over 白，再蓝 #0000FF80 over 结果
r1 = over(RED, A128, WHITE)
b1 = over(BLUE, A128, r1)
e1_theory = [rnd(v) for v in b1]
e1_float = [round(v, 6) for v in b1]

# ② 不透明红 over 白 = 红；不透明蓝 over 红 = 蓝；整组 opacity 0.5 over 白
g_red = over(RED, 1.0, WHITE)
g_blue = over(BLUE, 1.0, g_red)
g2 = over(g_blue, 0.5, WHITE)
e2_theory = [rnd(v) for v in g2]
e2_float = [round(v, 6) for v in g2]

# ---------- 采样 ----------
samples = {}
for cell in (1, 2):
    ox, oy = ORIGINS[cell]
    px = IMG.getpixel((ox + SAMPLE[0], oy + SAMPLE[1]))
    samples[cell] = {"rgba": list(px), "rgb": list(px[:3]), "alpha": px[3]}

err1 = [abs(samples[1]["rgb"][i] - e1_theory[i]) for i in range(3)]
err2 = [abs(samples[2]["rgb"][i] - e2_theory[i]) for i in range(3)]

audit = {
    "schema_version": 1,
    "task_id": TASK,
    "path_base": "output_dir",
    "run_id": RUN_ID,
    "canvas": {"width": W, "height": H, "origin": "canvas_top_left_y_down"},
    "local_coordinate_rule": "局部坐标原点为对应 320x240 实验区左上外边界，x 向右、y 向下，单位像素",
    "cell_origins_px": {str(k): v for k, v in ORIGINS.items()},
    "sample_point_local": list(SAMPLE),
    "sample_pixel_index": "解码 PNG 的第 (origin_x+180, origin_y+100) 个像素，索引从 0 开始",
    "compositing_rules": {
        "order": "蓝覆盖红，最后合成白底，source-over",
        "color_space": "0-255 sRGB 通道值",
        "intermediate": "中间值不取整",
        "final_rounding": "floor(value + 0.5) 取最近整数",
        "alpha_128_vs_05": "128/255 = 0.5019607843 与 0.5 是两个不同值，不可混为同一个 alpha",
    },
    "experiments": {},
}

# 实验 1
audit["experiments"]["1"] = {
    "title": "红蓝重叠矩形分别设置 50% alpha",
    "dsl_nodes": [
        'Positioned(40,40,160,120) > Container color="#FF000080"',
        'Positioned(120,80,160,120) > Container color="#0000FF80"  (蓝在上层)',
    ],
    "alpha_source": "矩形自身 color 的第 7-8 位（CSS #RRGGBBAA），128/255 = 0.5019607843",
    "rects": {
        "red": {"xywh": [40, 40, 160, 120], "color": "#FF000080", "alpha": A128},
        "blue": {"xywh": [120, 80, 160, 120], "color": "#0000FF80", "alpha": A128},
    },
    "theory": {
        "float": e1_float,
        "rounded_rgb": e1_theory,
        "steps": [
            "red_over_white = 255*0.50196 + 255*0.49804 = " + str([round(v, 4) for v in r1]),
            "blue_over_that = 0*0.50196 + red_over_white*0.49804 (R), "
            "255*0.50196 + red_over_white*0.49804 (B) = " + str(e1_float),
        ],
    },
    "actual": samples[1],
    "abs_error_per_channel": err1,
    "tolerance_per_channel": 3,
    "within_tolerance": all(e <= 3 for e in err1),
}

# 实验 2
audit["experiments"]["2"] = {
    "title": "同样的两个不透明矩形放在 Opacity(0.5) 组内",
    "dsl_nodes": [
        'Positioned(0,0,320,240) > Opacity opacity="0.5" > Stack > '
        'Positioned(40,40,160,120) Container #FF0000 + Positioned(120,80,160,120) Container #0000FF',
    ],
    "alpha_source": "Opacity widget 的 opacity 属性，恰好 0.5（不是 128/255）",
    "rects": {
        "red": {"xywh": [40, 40, 160, 120], "color": "#FF0000", "alpha": 1.0},
        "blue": {"xywh": [120, 80, 160, 120], "color": "#0000FF", "alpha": 1.0},
    },
    "group_opacity": 0.5,
    "theory": {
        "float": e2_float,
        "rounded_rgb": e2_theory,
        "steps": [
            "组内：不透明红 over 白 = 红 (255,0,0)；不透明蓝 over 红 = 蓝 (0,0,255)",
            "整组 opacity 0.5 over 白 = 0.5*蓝 + 0.5*白 = " + str(e2_float),
        ],
    },
    "actual": samples[2],
    "abs_error_per_channel": err2,
    "tolerance_per_channel": 3,
    "within_tolerance": all(e <= 3 for e in err2),
}

audit["alpha_difference_explanation"] = {
    "value_128_over_255": A128,
    "value_05": 0.5,
    "difference": A128 - 0.5,
    "why_results_differ": (
        "①中两个矩形各自带 alpha=128/255，红色先以该 alpha 合成到白底得到 (127.5,127.5,255) 附近的"
        "半透明红，蓝色再以同样 alpha 合成上去，红色通道被蓝色 alpha 二次衰减 → (127,63,191)。"
        "②中组内两矩形均不透明，蓝色完全覆盖红色得到纯蓝 (0,0,255)，再由 Opacity 0.5 一次性合成到白底 → (127.5,127.5,255)≈(128,128,255)。"
        "因此①②在重叠处不同：①的 G 通道约 63，②约 128。"
    ),
    "observed": {
        "exp1_rgb": samples[1]["rgb"],
        "exp2_rgb": samples[2]["rgb"],
        "green_channel_gap": samples[2]["rgb"][1] - samples[1]["rgb"][1],
    },
}

# ---------- ③④ ----------
audit["experiments"]["3"] = {
    "title": "带锐利条纹背景的圆角卡，仅背景模糊",
    "shared_base_scene": {
        "stripes": {"width": 24, "colors": ["#0F172A", "#F8FAFC"], "phase": "x=0 起深色",
                    "span": "跨满 320x240 实验区"},
        "card": {"local_xy": [40, 40], "size": [240, 160], "radius": 20,
                 "text": "SHARP / BLUR", "text_size": 24},
        "foreground_shape": {"local_xy": [150, 110], "size": [40, 40], "radius": 20,
                             "color": "#0D9488"},
        "draw_order": "条纹 → 模糊背景 → 卡片边框/阴影/文字/前景",
    },
    "unique_change": "模糊作用层：仅卡片覆盖处的背景（BackdropFilter + ClipRRect 限定）",
    "dsl_nodes": [
        " stripes: Positioned(0..320 step 24, 0, 24, 240) Container #0F172A / #F8FAFC",
        " Positioned(40,40,240,160) > ClipRRect(20) > BackdropFilter(sigmaX=6, sigmaY=6) "
        "> Container(240,160) transparent",
        " Positioned(40,40,240,160) > Container(transparent, radius 20, border, boxShadow) "
        "> Stack > Text + 前景圆",
    ],
    "documentation": "https://snapshot.muedsa.com/widgets/painting/backdrop-filter/ "
                     "「BackdropFilter 读取当前区域背后的已绘制内容…典型用途是毛玻璃」；"
                     "https://snapshot.muedsa.com/widgets/painting/image-filtered/ "
                     "「它处理的是自身子树；要处理已经绘制在后方的内容，使用 BackdropFilter」",
    "visual_judgement": {
        "method": "整图与局部放大（i2-c3.png）+ 行扫描像素梯度",
        "card_interior_blurred": True,
        "card_interior_evidence": "卡内 y=240 行从 x=953 到 x=1191 只有 3 次跳变且为柔和过渡，"
                                  "未见 24px 周期的硬边；卡外同 y 行保持 24px 深浅交替",
        "outside_card_sharp": True,
        "outside_card_evidence": "实验区卡外条纹保持 24px 等宽深淡交替（#0F172A / #F8FAFC）",
        "text_sharp": True,
        "text_evidence": "「SHARP / BLUR」文字边缘清晰，位于卡内 y≈192-222",
        "foreground_sharp": True,
        "foreground_evidence": "前景圆 (150,110,40,40) 边缘清晰、颜色 #0D9488",
        "effect_overflow": False,
        "overflow_evidence": "ClipRRect(20) 将滤镜限定在圆角卡区域内，卡外条纹未被模糊",
    },
}

audit["experiments"]["4"] = {
    "title": "相同条纹，把卡内文字与形状一起子树模糊",
    "shared_base_scene": "与实验 3 完全相同（条纹颜色/宽度/间距/相位、卡片底色/位置/文字/前景形状/绘制层次）",
    "unique_change": "模糊作用层：卡片整棵子树（ImageFiltered 包住含文字与前景的整张卡）",
    "dsl_nodes": [
        " stripes: 同实验 3",
        " Positioned(40,40,240,160) > ImageFiltered(sigmaX=6, sigmaY=6) > "
        "Container(240,160,#FFFFFF,radius 20,border,boxShadow) > Stack > Text + 前景圆",
    ],
    "documentation": "https://snapshot.muedsa.com/widgets/painting/image-filtered/ "
                     "「ImageFiltered 把子树作为输入图像应用 ImageFilter」；"
                     "「模糊会扩展可见像素范围，祖先裁剪可能截掉模糊边缘」",
    "visual_judgement": {
        "method": "整图与局部放大（i2-c4.png）+ 行扫描像素梯度",
        "card_interior_blurred": True,
        "card_interior_evidence": "卡内 y=512 行从 x=249 到 x=488 有 40+ 次逐像素渐变，"
                                  "文字与圆形均已模糊成色块",
        "text_blurred": True,
        "text_evidence": "「SHARP / BLUR」文字模糊，无法清晰辨认字形",
        "foreground_blurred": True,
        "foreground_evidence": "前景圆模糊成 #0D9488 色团，边缘失去锐利度",
        "outside_card_sharp": True,
        "outside_card_evidence": "实验区卡外条纹保持 24px 等宽深淡交替",
        "effect_overflow": False,
        "overflow_evidence": "ImageFiltered 的子树边界即卡片 240x160，卡外条纹不受影响",
    },
}

audit["pair_3_4"] = {
    "shared": "同一份未加效果的基础场景：条纹颜色/宽度/间距/相位、卡片底色/位置/文字/前景形状/绘制层次",
    "only_difference": "模糊所作用的层（③背景 vs ④整棵子树）",
    "observed_contrast": "③卡内文字与前景清晰、仅背景条纹模糊；④卡内文字与前景一并模糊。"
                         "两格卡外条纹同样清晰。",
}

# ---------- ⑤⑥ ----------
audit["experiments"]["5"] = {
    "title": "先 ColorFiltered(MULTIPLY) 后子树高斯模糊",
    "shared_base_scene": {
        "filter_color": "#F6B94A",
        "blend_mode": "MULTIPLY",
        "sigma": [6, 6],
        "elements": [
            "深色矩形 (30,40,120,90) #1E293B radius 8（跨出圆周左上方）",
            "透明间隙矩形 (170,30,110,70) 透明填充 + 2 SOLID #94A3B8 边框 radius 8",
            "中等色块 (180,150,130,80) #0D9488 radius 8（跨出圆周右下方）",
            "小圆点 (120,170,50,50) #DC2626 radius 25",
            "文字 MULTIPLY (60,110,200) 22px #F8FAFC",
        ],
        "no_full_white_background": "基础场景不铺满白底，实验区白底作为背景，"
                                    "使 MULTIPLY 只作用于有色形状与文字",
    },
    "unique_change": "无圆形裁剪",
    "dsl_nodes": [
        " Positioned(0,0,320,240) > Stack > [深色矩形, 透明间隙, 色块, 圆点, 文字]",
        " 外层：ColorFiltered color=#F6B94A blendMode=MULTIPLY > ImageFiltered(6,6) > 上述 Stack",
    ],
    "documentation": "https://snapshot.muedsa.com/widgets/painting/color-filtered/ "
                     "「ColorFiltered 在合成阶段对子树像素应用 ColorFilter…MODULATE 会逐通道相乘」；"
                     "「SRC、MULTIPLY 等可能改变透明像素的混合模式，也可能给边界内原本透明的间隙着色」",
    "visual_judgement": {
        "method": "整图与局部放大（i2-c56.png）",
        "tint_applied": True,
        "tint_evidence": "实验区整体呈 #F6B94A 的橙黄色调；深色矩形变为暗橙、"
                         "#0D9488 色块变为橄榄绿、#DC2626 圆点变为砖红",
        "blur_applied": True,
        "blur_evidence": "所有形状边缘均呈 6px 高斯的柔和过渡，无硬边",
        "transparent_gap_tinted": True,
        "transparent_gap_evidence": "透明间隙矩形内部被 MULTIPLY 着色（非纯白），"
                                    "与文档「可能给边界内原本透明的间隙着色」一致",
        "effect_overflow": True,
        "overflow_evidence": "无圆形裁剪，滤色与模糊效果覆盖整个 320x240 实验区",
    },
}

audit["experiments"]["6"] = {
    "title": "同样的 ⑤ 效果再限定于圆形裁剪区域",
    "shared_base_scene": "与实验 5 完全相同（同一基础场景、位置、颜色、阴影和滤镜参数）",
    "unique_change": "最外层增加 ClipOval 圆形裁剪",
    "clip": {"center_local": [160, 120], "radius": 100,
             "canvas_center_px": [ORIGINS[6][0] + 160, ORIGINS[6][1] + 120]},
    "dsl_nodes": [
        " Positioned(60,20,200,200) > ClipOval(clipBehavior=ANTI_ALIAS) > "
        "[ColorFiltered(#F6B94A,MULTIPLY) > ImageFiltered(6,6) > Stack]",
    ],
    "documentation": "https://snapshot.muedsa.com/reference/parser-tags/ ClipOval 椭圆裁剪；"
                     "https://snapshot.muedsa.com/guides/layout/ "
                     "「布局溢出和绘制裁剪是两个不同问题」",
    "visual_judgement": {
        "method": "整图与局部放大（i2-c56.png）",
        "clip_boundary_visible": True,
        "clip_boundary_evidence": "可见清晰圆形边界；深色矩形与 #0D9488 色块均跨过圆周，"
                                  "圆周外部分被裁掉、圆周内保留，边界可检查",
        "shapes_crossing_circle": ["深色矩形 (30,40,120,90)", "#0D9488 色块 (180,150,130,80)"],
        "inside_circle_same_as_5": True,
        "inside_circle_evidence": "圆内滤色与模糊效果与实验 5 一致（同一滤镜链）",
        "outside_circle_clean": True,
        "outside_circle_evidence": "圆外为实验区白底，无滤色、无模糊",
        "effect_overflow": False,
        "overflow_evidence": "ClipOval 将效果限定在半径 100 的圆内",
    },
}

audit["pair_5_6"] = {
    "shared": "同一份基础场景、位置、颜色、阴影和滤镜参数"
              "（ColorFiltered #F6B94A MULTIPLY + ImageFiltered sigma 6）",
    "only_difference": "⑥ 在最外层增加 ClipOval 圆形裁剪，⑤ 不加",
    "observed_contrast": "⑤ 效果覆盖整个实验区；⑥ 效果被限制在圆心 (160,120) 半径 100 的圆内，"
                         "圆外保持白底，且可看到有色形状被圆周裁断的边界。",
}

audit["visual_checks"] = {
    "caption_min_px": 20,
    "cells_visible": True,
    "evidence_visible": True,
    "all_cell_origins_integer": all(isinstance(v[0], int) and isinstance(v[1], int)
                                    for v in ORIGINS.values()),
}

(OUT_DIR / "composite-audit.json").write_text(
    json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("wrote composite-audit.json")
print("E1 theory", e1_theory, "actual", samples[1]["rgb"], "err", err1)
print("E2 theory", e2_theory, "actual", samples[2]["rgb"], "err", err2)
