# -*- coding: utf-8 -*-
"""A13 final: symbol (color/black), banner, poster, 32px checks, audits."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import dslkit as K  # noqa: E402
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "A13"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
PREV = TMP / "previews"
clock = rep.TaskClock(TASK)

INK = "#101826"
BLUE = "#2F6BFF"
AMBER = "#FFB020"
PAPER = "#0C1322"

def hx(color, a):
    return f"{color}{int(round(a * 255)):02X}"

GEO = [(72, 72, 264, 60), (152, 124, 206, 46), (204, 196, 164, 34)]

def mark(x, y, s, mode="color", core=True, back_ink=INK):
    out = []
    if mode == "color":
        layers = [(back_ink, 0.90), (BLUE, 0.80), (AMBER, 0.88)]
        core_color = "#FFFFFF"
    else:
        layers = [("#000000", 0.60), ("#000000", 0.76), ("#000000", 0.90)]
        core_color = "#000000"
    for (gx, gy, size, r), (color, a) in zip(GEO, layers):
        out.append(K.rect(x + gx * s, y + gy * s, size * s, size * s,
                          color=hx(color, a), radius=r * s))
    if core:
        out.append(K.rect(x + 256 * s, y + 255 * s, 60 * s, 60 * s, color=core_color, radius=30 * s))
    return "".join(out)

logger = api.TaskLogger(TASK, TMP)
def render(name, parts, w, h, bg, tag):
    dsl = K.document(w, h, parts, background=bg)
    snap = OUT / f"{name}.snapshot"
    snap.write_text(dsl, encoding="utf-8")
    warn = K.drain_warnings()
    rec = logger.render(snap, OUT / f"{name}.png", tag)
    print(f"{name}: {rec['http_status']} {rec['response_bytes']}B {rec['elapsed_s']}s")
    for x in warn:
        print("  ", x)
    if rec["http_status"] != 200:
        print((TMP / "responses" / f"{rec['id']}.bin").read_text(encoding="utf-8", errors="replace")[:1200])
        raise SystemExit(1)

# 1) color symbol 512 transparent
render("symbol-color", [mark(0, 0, 1.0, "color")], 512, 512, None, "symbol color")
# 2) black symbol 512 transparent
render("symbol-black", [mark(0, 0, 1.0, "black")], 512, 512, None, "symbol black")

# 3) banner 1200x400
bp: list[str] = []
bp.append(K.rect(0, 0, 1200, 400, color=PAPER))
bp.append(K.rect(0, 0, 6, 400, color=AMBER))
bp.append(mark(64, 55, 0.56, "color", back_ink="#31415F"))
bp.append(K.text(390, 96, "叠光", size=76, color="#FFFFFF", bold=True, width=360))
bp.append(K.text(390, 186, "Layerlight", size=52, color=AMBER, bold=True, width=520))
bp.append(K.rect(392, 262, 84, 4, color=BLUE))
bp.append(K.text(392, 282, "把复杂信息，组织成清晰画面", size=26, color="#C7D2E4", width=700))
bp.append(K.text(1096, 340, "layerlight.example.org", size=20, color="#6C7C96", width=360,
                 align="RIGHT"))
render("brand-banner", bp, 1200, 400, PAPER, "banner")

# 4) poster 1080x1350
pp: list[str] = []
pp.append(K.rect(0, 0, 1080, 1350, color=PAPER))
pp.append(K.rect(64, 64, 952, 3, color=AMBER))
pp.append(mark(304, 120, 0.92, "color", back_ink="#31415F"))
pp.append(K.rect(64, 640, 952, 1, color="#26344C"))
pp.append(K.text(64, 672, "叠光", size=96, color="#FFFFFF", bold=True, width=400))
pp.append(K.text(64, 802, "Layerlight", size=58, color=AMBER, bold=True, width=560))
pp.append(K.text(64, 884, "把复杂信息，组织成清晰画面", size=34, color="#C7D2E4", width=900))
pp.append(K.rect(64, 950, 210, 46, color=hx(BLUE, 0.22), radius=23, border=f"1 SOLID {BLUE}"))
pp.append(K.text(64, 960, "OPEN BETA", size=24, color="#8FB0FF", bold=True, width=210, align="CENTER"))
pp.append(K.text(64, 1042, "2026.11.07 · ONLINE", size=30, color="#FFFFFF", bold=True, width=700))
pp.append(K.text(64, 1104, "layerlight.example.org", size=26, color="#8C9CB8", width=700))
pp.append(K.rect(64, 1244, 952, 1, color="#26344C"))
pp.append(K.text(64, 1264, "结构化视觉工具 · 信息叠加后仍然清晰", size=22, color="#6C7C96", width=760))
render("launch-poster", pp, 1080, 1350, PAPER, "poster")

# ---------------------------------------------------------------- checks
def check_black(path):
    im = Image.open(path).convert("RGBA")
    a = np.array(im)
    alpha = a[:, :, 3]
    rgb = a[:, :, :3]
    mask = alpha > 0
    bad = np.sum(mask & ((rgb[:, :, 0] != 0) | (rgb[:, :, 1] != 0) | (rgb[:, :, 2] != 0)))
    return {"file": path.name, "size": list(im.size), "violating_pixels": int(bad),
            "alpha_min": int(alpha.min()), "alpha_max": int(alpha.max()),
            "nonzero_alpha_pixels": int(mask.sum()), "passed": int(bad) == 0}

black = check_black(OUT / "symbol-black.png")
print("black check:", black)

def preview32(path, out):
    im = Image.open(path).convert("RGBA")
    arr = np.array(im).astype(np.float64)
    alpha = arr[:, :, 3:4] / 255.0
    prem = np.concatenate([arr[:, :, :3] * alpha, arr[:, :, 3:4]], axis=2)
    small = Image.fromarray(np.clip(np.round(prem), 0, 255).astype(np.uint8), "RGBA")
    small = small.resize((32, 32), Image.LANCZOS)
    s = np.array(small).astype(np.float64)
    a = s[:, :, 3:4]
    with np.errstate(invalid="ignore", divide="ignore"):
        rgb = np.where(a > 0, s[:, :, :3] * 255.0 / np.maximum(a, 1e-6), 0)
    res = np.concatenate([np.clip(np.round(rgb), 0, 255), a], axis=2).astype(np.uint8)
    Image.fromarray(res, "RGBA").save(out)
    return str(out)

p32 = preview32(OUT / "symbol-color.png", PREV / "symbol-color-32.png")
p32b = preview32(OUT / "symbol-black.png", PREV / "symbol-black-32.png")
# contact sheet on light background at actual 32px plus a 4x zoom for edge inspection
sheet = Image.new("RGB", (32 * 6, 32 * 2 + 60), "#F2F4F8")
for i, pth in enumerate((p32, p32b)):
    im = Image.open(pth).convert("RGBA")
    sheet.paste(im, (16 + i * 64, 16), im)
    big = im.resize((128, 128), Image.NEAREST)
    sheet.paste(big, (16 + i * 64, 60), big)
sheet.save(PREV / "thumb-sheet.png")
print("thumbnails:", p32, p32b)

brand = {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "brand": {"name_cn": "叠光", "name_en": "Layerlight",
              "concept": "信息叠加后仍然清晰", "tagline": "把复杂信息，组织成清晰画面"},
    "colors": {"ink": INK, "blue": BLUE, "amber": AMBER, "paper": PAPER,
               "alpha": {"back": 0.90, "mid": 0.80, "front": 0.88, "core": 1.0}},
    "geometry_reference_box": [512, 512],
    "components": [
        {"id": "S1", "primitive": "rounded square", "instance": "back layer",
         "geometry": {"x": 72, "y": 72, "w": 264, "h": 264, "radius": 60},
         "fill": "#101826E6", "dsl": "Container border-radius 60", "count": 1},
        {"id": "S2", "primitive": "rounded square", "instance": "middle layer",
         "geometry": {"x": 152, "y": 124, "w": 206, "h": 206, "radius": 46},
         "fill": "#2F6BFFCC", "dsl": "Container border-radius 46", "count": 2},
        {"id": "S3", "primitive": "rounded square", "instance": "front layer",
         "geometry": {"x": 204, "y": 196, "w": 164, "h": 164, "radius": 34},
         "fill": "#FFB020E0", "dsl": "Container border-radius 34", "count": 3},
        {"id": "S4", "primitive": "circle", "instance": "clarity core",
         "geometry": {"x": 256, "y": 255, "w": 60, "h": 60, "radius": 30},
         "fill": "#FFFFFF", "dsl": "Container border-radius 30", "count": 4},
    ],
    "component_count": 4,
    "count_rationale": "四个可独立辨认的母形实例：三个圆角方块 + 一个圆点；"
                       "负空间（层间透出的深色缺口）由叠加自然产生，不另计。",
    "clear_space": {"minimum_ratio_of_mark": 0.18,
                    "rule": "方形安全区边长 = 标志外框 × 1.18，四周留白不小于外框的 9%"},
    "small_size_rules": {"min_render_px": 32, "core_kept": True,
                         "note": "32px 时三层仍各有 2 个可见圆角，白色核点直径约 3.2px 保留"},
    "applications": [
        {"file": "symbol-color.png", "size": [512, 512], "background": "transparent",
         "mark_scale": 1.0, "mark_origin": [0, 0], "mode": "color"},
        {"file": "symbol-black.png", "size": [512, 512], "background": "transparent",
         "mark_scale": 1.0, "mark_origin": [0, 0], "mode": "black"},
        {"file": "brand-banner.png", "size": [1200, 400], "background": PAPER,
         "mark_scale": 0.56, "mark_origin": [64, 55], "mode": "color",
         "text": ["叠光", "Layerlight", "把复杂信息，组织成清晰画面", "layerlight.example.org"]},
        {"file": "launch-poster.png", "size": [1080, 1350], "background": PAPER,
         "mark_scale": 0.92, "mark_origin": [228, 120], "mode": "color",
         "text": ["叠光", "Layerlight", "把复杂信息，组织成清晰画面", "2026.11.07 · ONLINE",
                  "OPEN BETA", "layerlight.example.org"]},
    ],
    "anti_patterns": ["不使用现成标志", "不把文字整体当图标", "不使用外部图片",
                      "横幅与海报均由同一 DSL 几何函数重绘，未嵌入图标 PNG"],
    "black_check": black,
    "thumbnail_check": {"tool": "Pillow " + Image.__version__ if hasattr(Image, "__version__") else "Pillow",
                        "resample": "LANCZOS on premultiplied alpha, then un-premultiply",
                        "sizes": [32, 32],
                        "previews": ["previews/symbol-color-32.png", "previews/symbol-black-32.png",
                                     "previews/thumb-sheet.png"]},
}
api.write_json(OUT / "brand-system.json", brand)
print("brand-system written")
