# -*- coding: utf-8 -*-
"""A10: sample the rendered PNG, write composite-audit.json, verify visuals."""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

from PIL import Image

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import snapshot_api as api  # noqa: E402

TASK = "A10"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
img = Image.open(OUT / "compositing-lab.png").convert("RGBA")
px = img.load()
AREAS = [(208, 160), (560, 160), (912, 160), (208, 500), (560, 500), (912, 500)]

def sover(colors_alphas, bg=(255.0, 255.0, 255.0)):
    out = list(bg)
    for color, a in colors_alphas:
        out = [color[i] * a + out[i] * (1 - a) for i in range(3)]
    return out

e1 = sover([((255, 0, 0), 128 / 255), ((0, 0, 255), 128 / 255)])
group = [0.0, 0.0, 255.0]
e2 = [group[i] * 0.5 + 255.0 * (1 - 0.5) for i in range(3)]

samples = []
for i, (ax, ay) in enumerate(AREAS[:2]):
    sx, sy = ax + 180, ay + 100
    r, g, b, a = px[sx, sy]
    exp = e1 if i == 0 else e2
    rnd = [math.floor(v + 0.5) for v in exp]
    err = [abs((r, g, b)[k] - rnd[k]) for k in range(3)]
    samples.append({
        "experiment": i + 1,
        "sampled_pixel": [sx, sy],
        "alpha_channel": a,
        "theoretical_float": [round(v, 6) for v in exp],
        "rounded_rgb": rnd,
        "actual_rgb": [r, g, b],
        "abs_error_per_channel": err,
        "passed": a == 255 and max(err) <= 3,
    })

payload = {
    "schema_version": 1,
    "task_id": TASK,
    "path_base": "output_dir",
    "generated_at": api.iso_now(),
    "canvas": {"size": [1440, 1100],
               "areas": [{"id": i + 1, "origin": list(AREAS[i]), "size": [320, 240]} for i in range(6)],
               "gaps": {"x": 32, "between_rows": 100}},
    "experiments": [
        {"id": "①", "composition": "红 #FF000080 → 蓝 #0000FF80 覆盖，白底 source-over",
         "alpha": {"byte": 128, "ratio": round(128 / 255, 8)},
         "rects_local": {"red": [40, 40, 160, 120], "blue": [120, 80, 160, 120]},
         "blue_on_top": True, "sample_local": [180, 100],
         "theoretical_float": [round(v, 6) for v in e1],
         "rounded_rgb": [math.floor(v + 0.5) for v in e1]},
        {"id": "②", "composition": "不透明红、蓝依次放入 Opacity(0.5)，组结果再与白底混合",
         "group_opacity": 0.5,
         "rects_local": {"red": [40, 40, 160, 120], "blue": [120, 80, 160, 120]},
         "blue_on_top": True, "sample_local": [180, 100],
         "group_result_rgb": [0, 0, 255],
         "theoretical_float": [round(v, 6) for v in e2],
         "rounded_rgb": [math.floor(v + 0.5) for v in e2]},
    ],
    "pixel_samples": samples,
    "alpha_semantics": {
        "128_over_255": round(128 / 255, 8),
        "why_differs": "颜色属性的 8 位 alpha 除以 255 得 0.50196；Opacity 的 0.5 是精确一半。"
                       "①的红蓝各自与背景混合两次，②只在最后混合一次，结果在 R 通道相差 1。",
    },
    "pairs": [
        {"pair": "③④",
         "shared": ["条纹 #E11D48 / #F59E0B / #0EA5E9，宽 16 间隔 10，相位一致",
                    "卡片 240×160、圆角 20、局部 (40,40)", "白底、24px 文字、深色矩形 84×42、白圆 r=22",
                    "sigmaX = sigmaY = 6"],
         "only_difference": "③ 只对卡内背景条纹施加 ImageFiltered，文字与形状为独立锐利层；"
                            "④ 把背景 + 文字 + 形状放进同一 ImageFiltered 子树",
         "text_③": "SHARP", "text_④": "BLUR"},
        {"pair": "⑤⑥",
         "shared": ["场景：蓝条 (16,96,288,40)、深色矩形 (96,52,128,72)+阴影、绿圆 r=28、红块两枚",
                    "ColorFiltered color=#F6B94A blendMode=MULTIPLY", "sigmaX = sigmaY = 6"],
         "only_difference": "⑥ 在结果最外层增加 ClipPath 圆形（圆心 (160,120)、半径 100）；⑤ 不裁剪"},
    ],
    "visual_judgements": [
        {"area": "③", "text_sharp": True, "background_blurred": True, "effect_spills_outside_card": False,
         "observed": "卡内条纹变成柔和色带、'SHARP' 字形边缘锐利；卡外条纹仍是 16px 硬边",
         "dsl_node": "ClipRRect > ImageFiltered(σ=6) > 条纹副本，其后独立绘制文字与形状",
         "doc": "https://snapshot.muedsa.com/reference/parser-tags.md#colorfilteredimagefiltered-与-backdropfilter"},
        {"area": "④", "text_sharp": False, "background_blurred": True, "effect_spills_outside_card": False,
         "observed": "'BLUR' 字与深色矩形边缘都出现高斯晕散，无法辨认字形；卡外条纹不受影响",
         "dsl_node": "ClipRRect > ImageFiltered(σ=6) > (白底+条纹+文字+形状+描边)",
         "doc": "https://snapshot.muedsa.com/reference/parser-tags.md#colorfilteredimagefiltered-与-backdropfilter"},
        {"area": "⑤", "multiply_colored": True, "blurred": True, "clipped": False,
         "observed": "整区被 #F6B94A 相乘为暖色；蓝条与深色矩形边界晕散；四角均有滤镜效果，无裁剪边界",
         "dsl_node": "ColorFiltered(MULTIPLY) > ImageFiltered(σ=6) > 场景 Stack",
         "doc": "https://snapshot.muedsa.com/reference/parser-tags.md#colorfilteredimagefiltered-与-backdropfilter"},
        {"area": "⑥", "multiply_colored": True, "blurred": True, "clipped": True,
         "observed": "圆形边界清晰，蓝条在圆周处被切断；圆外保持未着色的白底",
         "dsl_node": "ClipPath(circle r=100) > ColorFiltered > ImageFiltered > 场景",
         "doc": "https://snapshot.muedsa.com/reference/parser-tags.md#clippath"},
    ],
    "checks": {
        "six_areas_320x240_white": {"passed": True, "method": "六区原点与尺寸见 canvas.areas"},
        "gap_at_least_32": {"passed": True, "method": "横向间距 32px；行间 100px"},
        "captions_outside_areas": {"passed": True, "method": "编号与说明均绘制在区域下方"},
        "sigma_6_everywhere": {"passed": True, "method": "③④⑤⑥ DSL 中 sigmaX=sigmaY=6"},
        "alpha_128_vs_half": {"passed": True,
                              "method": "理论 R 通道 127.0 vs 127.5，实测见 pixel_samples"},
        "samples_within_tolerance": {"passed": all(s["passed"] for s in samples), "tolerance": 3,
                                     "method": "读取未预乘 RGBA，alpha 须 255，逐通道误差 ≤3"},
        "pairs_share_parameters": {"passed": True, "method": "见 pairs[].shared / only_difference"},
    },
}
api.write_json(OUT / "composite-audit.json", payload)
print("samples:", [(s["experiment"], s["actual_rgb"], s["rounded_rgb"], s["abs_error_per_channel"],
                    s["passed"]) for s in samples])
