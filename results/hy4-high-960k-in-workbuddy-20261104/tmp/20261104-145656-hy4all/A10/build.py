#!/usr/bin/env python3
"""A10 compositing lab: six 320x240 white panels on 1440x1100, 3x2 with >=32px
gaps. Demonstrates per-shape alpha vs group Opacity, background-only blur vs
subtree blur, and ColorFiltered(MULTIPLY)+ImageFiltered with/without ClipOval.
Emits compositing-lab.snapshot + composite-audit.json (theoretical values).
sample.py / visual.py fill in real PNG measurements and observations after render.
"""
import json, os, sys
from pathlib import Path

TOOLS = os.environ["TOOLS"]
sys.path.insert(0, TOOLS)
from dsl import Canvas, CN, LATIN, MONO, cdata
import suite

TASK = "A10"
ROOT = suite.ROOT
BG = "#EEF3FA"; WHITE = "#FFFFFF"; INK = "#0F172A"; MUTED = "#5B6B85"
LINE = "#DDE5F0"; NAVY = "#0B1B35"; NAVY2 = "#16386F"
STRIPE_DARK = "#1B3A5F"; FILTER_COLOR = "#F6B94A"
AMBER = "#B45309"; TEAL = "#0D9488"

# ---- layout ----
AW, AH = 320, 240
COL_X = [192, 560, 928]
ROW_Y = [180, 590]
ORIGINS = [(COL_X[i], ROW_Y[j]) for j in range(2) for i in range(3)]
CAP_Y = [112, 522]
DESC_Y = [428, 838]
assert ORIGINS[0] == (192, 180) and ORIGINS[5] == (928, 590)

NAMES = [
    "逐层 50% alpha", "整组 Opacity(0.5)", "背景模糊 / 字清晰",
    "子树模糊 / 字模糊", "滤色+模糊", "滤色+模糊+圆裁剪",
]
DESCS = [
    "两个矩形各设 50% alpha；蓝在上层，与白底逐层 source-over。",
    "不透明红蓝放进 Opacity(0.5) 组；整组只与白底混合一次。",
    "仅卡片覆盖处的条纹被模糊，文字与前景保持清晰。",
    "相同场景，文字与前景一起进入子树高斯模糊。",
    "先 MULTIPLY 滤色，再 sigma=6 子树模糊；效果铺满整个实验区。",
    "与第 5 格同效果，最外层加圆形裁剪（圆心 (160,120)、r=100）。",
]

c = Canvas(1440, 1100, BG)

# ---- title ----
c.rect(0, 0, 1440, 100, WHITE)
c.rect(0, 96, 1440, 4, "#38BDF8")
c.text(48, 16, 1000, 50, "看到差异，才能说用对了", 40, NAVY, bold=True)
c.text(48, 66, 1100, 28, "透明合成与滤镜语义实验板 ｜ 6 格 × 320×240 白底实验区 ｜ sigmaX = sigmaY = 6", 20, MUTED)
c.text(1120, 26, 280, 34, "A10 / COMPOSITING LAB", 18, "#8FB6EA", align="RIGHT", font=LATIN)
c.text(1120, 64, 280, 28, "题面数值 + 真实 PNG 采样", 17, MUTED, align="RIGHT")

# ---- caption / description bands (outside the areas) ----
for k, (ox, oy) in enumerate(ORIGINS):
    row = k // 3
    capy, descy = CAP_Y[row], DESC_Y[row]
    c.circle(ox + 28, capy + 28, 20, NAVY)
    c.text(ox + 8, capy + 8, 40, 40, str(k + 1), 22, WHITE, bold=True, align="CENTER", font=LATIN)
    c.text(ox + 60, capy + 6, 260, 44, NAMES[k], 24, INK, bold=True)
    c.text(ox, descy + 6, AW, 72, DESCS[k], 20, MUTED)

# ---- white experiment areas ----
for ox, oy in ORIGINS:
    c.rect(ox, oy, AW, AH, WHITE, border="1 SOLID " + LINE)

# ================================================================ panel 1
ox, oy = ORIGINS[0]
c.rect(ox + 40, oy + 40, 160, 120, "#FF000080")     # red, alpha 128/255
c.rect(ox + 120, oy + 80, 160, 120, "#0000FF80")    # blue on top, alpha 128/255
# NOTE: no marker is drawn at local (180,100) -- that pixel must stay a pure
# source-over result for the composite-audit.json sample.

# ================================================================ panel 2
ox, oy = ORIGINS[1]
group = ('<Opacity opacity="0.5">'
         '<Container width="320" height="240">'
         '<Stack alignment="TOP_LEFT" clipBehavior="HARD_EDGE">'
         '<Container width="320" height="240" />'
         '<Positioned left="40" top="40" width="160" height="120"><Container color="#FF0000" /></Positioned>'
         '<Positioned left="120" top="80" width="160" height="120"><Container color="#0000FF" /></Positioned>'
         '</Stack></Container></Opacity>')
c.add(ox, oy, AW, AH, group)

# ---- shared stripe / card scene for panels 3 and 4 ----
def stripes_bars(xoff, w, h):
    """Vertical 8px dark bars every 16px; xoff maps global stripes into a local box."""
    s = ""
    for j in range(-3, 26):
        lx = 16 * j - xoff
        x0, x1 = max(0, lx), min(w, lx + 8)
        if x1 > x0:
            s += ('<Positioned left="%g" top="0" width="%g" height="%g">'
                  '<Container color="%s" /></Positioned>' % (x0, x1 - x0, h, STRIPE_DARK))
    return s


def full_stripes():
    return ('<Container width="320" height="240" color="#FFFFFF">'
            '<Stack alignment="TOP_LEFT" clipBehavior="HARD_EDGE">'
            '<Container width="320" height="240" />' + stripes_bars(0, 320, 240) +
            '</Stack></Container>')


def card_foreground():
    return (
        '<Positioned left="0" top="0" width="240" height="160">'
        '<Container color="#FFFFFF33" borderRadius="20" /></Positioned>'
        '<Positioned left="20" top="52" width="200" height="40">'
        '<Container width="200" height="40" alignment="CENTER">'
        '<Text fontFamily="Noto Sans CJK SC" fontSize="24" fontStyle="BOLD" color="#0F172A" textAlign="CENTER">'
        + cdata("SHARP / BLUR") + '</Text></Container></Positioned>'
        '<Positioned left="20" top="116" width="72" height="20">'
        '<Container color="#0D9488" borderRadius="6" /></Positioned>'
    )


def card_blur(blur_foreground):
    inner = ('<Container width="240" height="160" color="#FFFFFF">'
             '<Stack alignment="TOP_LEFT" clipBehavior="HARD_EDGE">'
             '<Container width="240" height="160" />' + stripes_bars(40, 240, 160))
    if blur_foreground:
        inner += card_foreground()
    inner += '</Stack></Container>'
    return ('<ClipRRect borderRadius="20" clipBehavior="ANTI_ALIAS">'
            '<ImageFiltered sigmaX="6" sigmaY="6" tileMode="CLAMP">' + inner +
            '</ImageFiltered></ClipRRect>')


# panel 3: sharp stripes + blurred background copy + SHARP foreground
ox, oy = ORIGINS[2]
c.add(ox, oy, AW, AH, full_stripes())
c.add(ox + 40, oy + 40, 240, 160, card_blur(False))
c.add(ox + 40, oy + 40, 240, 160,
      '<Container width="240" height="160"><Stack alignment="TOP_LEFT" clipBehavior="HARD_EDGE">'
      '<Container width="240" height="160" />' + card_foreground() + '</Stack></Container>')

# panel 4: identical scene, but text + foreground INSIDE the blurred subtree
ox, oy = ORIGINS[3]
c.add(ox, oy, AW, AH, full_stripes())
c.add(ox + 40, oy + 40, 240, 160, card_blur(True))

# ---- shared filter scene for panels 5 and 6 ----
def filter_shapes():
    return (
        '<Positioned left="20" top="100" width="280" height="40"><Container color="#3B6FE0" /></Positioned>'
        '<Positioned left="40" top="24" width="44" height="64"><Container color="#E0533D" /></Positioned>'
        '<Positioned left="110" top="24" width="44" height="64"><Container color="#2FA36B" /></Positioned>'
        '<Positioned left="180" top="24" width="44" height="64"><Container color="#8B4FD1" /></Positioned>'
        '<Positioned left="224" top="150" width="60" height="60"><Container color="#EAB53B" /></Positioned>'
        '<Positioned left="110" top="150" width="100" height="60">'
        '<Container color="#1F2937" boxShadow="0 6 10 0 #00000066 NORMAL" /></Positioned>'
    )


def filtered_scene():
    return ('<ImageFiltered sigmaX="6" sigmaY="6" tileMode="CLAMP">'
            '<ColorFiltered color="#F6B94A" blendMode="MULTIPLY">'
            '<Container width="320" height="240">'
            '<Stack alignment="TOP_LEFT" clipBehavior="HARD_EDGE">'
            '<Container width="320" height="240" />' + filter_shapes() +
            '</Stack></Container></ColorFiltered></ImageFiltered>')


# panel 5: no clip -> effect spills outside the whole area
ox, oy = ORIGINS[4]
c.add(ox, oy, AW, AH, filtered_scene())

# panel 6: same scene, outer ClipOval = circle centre (160,120) r=100
ox, oy = ORIGINS[5]
c.add(ox + 60, oy + 20, 200, 200,
      '<ClipOval clipBehavior="ANTI_ALIAS">'
      '<Container width="200" height="200">'
      '<Stack alignment="TOP_LEFT" clipBehavior="NONE">'
      '<Container width="200" height="200" />'
      '<Positioned left="-60" top="-20" width="320" height="240">' + filtered_scene() +
      '</Positioned></Stack></Container></ClipOval>')

# ---- footer: shared parameters + doc references ----
c.rect(0, 928, 1440, 172, "#F8FAFF")
c.rect(0, 928, 1440, 2, LINE)
c.text(48, 938, 500, 32, "共用参数 / 采样 / 文档", 24, INK, bold=True)
FOOT = [
    "③④ 共用：16px 周期 / 8px 暗条、卡 240×160 圆角 20、文字 SHARP / BLUR 24px、sigma=6；唯一差异＝模糊层。",
    "⑤⑥ 共用：滤色 #F6B94A MULTIPLY、sigma=6、透明间隙 / 深色矩形 / 阴影；唯一差异＝圆形裁剪 r=100。",
    "①② 采样：各区局部 (180,100)；① 用 #80=128/255，② 用 Opacity(0.5)；取整 ① (127,63,191)、② (128,128,255)。",
    "依据：parser-tags.md（Opacity / ColorFiltered / ImageFiltered / ClipRRect / ClipOval）与 AGENT-BRIEF。",
]
for i, t in enumerate(FOOT):
    c.text(48, 976 + i * 30, 1344, 28, t, 20, MUTED)

dsl = c.render()
out = suite.out_dir(TASK)
(out / "compositing-lab.snapshot").write_text(dsl, encoding="utf-8")
ver = os.environ.get("BUILD_VERSION", "v1")
tmp = suite.tmp_dir(TASK, ver)
(tmp / "compositing-lab.snapshot").write_text(dsl, encoding="utf-8")

# ================================================================ composite-audit.json
a = 128.0 / 255.0
b = 1.0 - a
# panel 1: white -> red(a) -> blue(a)
r1 = (255.0, 255.0 * b, 255.0 * b)
p1 = (255.0 * b, r1[1] * b, 255.0 * a + r1[2] * b)
# panel 2: opaque blue inside group, then alpha 0.5 over white
p2 = (0.0 * 0.5 + 255.0 * 0.5, 0.0 * 0.5 + 255.0 * 0.5, 255.0 * 0.5 + 255.0 * 0.5)


def rnd(v):
    return round(v, 6)


def round_rgb(t):
    return [int(v + 0.5) for v in t]


panels = []
for k, (ox, oy) in enumerate(ORIGINS):
    n = k + 1
    panels.append({
        "id": n, "name": NAMES[k], "origin_px": [ox, oy], "size_px": [AW, AH],
        "local_coordinates": "origin at panel top-left, x right / y down, px",
        "scene": {
            1: {"rectangles": [{"x": 40, "y": 40, "w": 160, "h": 120, "color": "#FF000080"},
                               {"x": 120, "y": 80, "w": 160, "h": 120, "color": "#0000FF80"}],
                "paint_order": "red first, blue on top", "background": "opaque white"},
            2: {"rectangles": [{"x": 40, "y": 40, "w": 160, "h": 120, "color": "#FF0000"},
                               {"x": 120, "y": 80, "w": 160, "h": 120, "color": "#0000FF"}],
                "paint_order": "red first, blue on top (both opaque)", "group": "Opacity(0.5)",
                "background": "opaque white"},
            3: {"stripes": {"period_px": 16, "dark_width_px": 8, "color": STRIPE_DARK, "phase": 0,
                            "background": "#FFFFFF"},
                "card": {"local_xy": [40, 40], "size_px": [240, 160], "radius": 20,
                         "base_color": "#FFFFFF33"},
                "text": {"content": "SHARP / BLUR", "size": 24, "color": "#0F172A"},
                "foreground_shape": {"local_xy": [20, 116], "size_px": [72, 20], "color": TEAL},
                "blur": {"node": "ImageFiltered", "sigmaX": 6, "sigmaY": 6, "applies_to": "background stripes copy only"}},
            4: {"stripes": "same as panel 3", "card": "same as panel 3",
                "text": "same as panel 3", "foreground_shape": "same as panel 3",
                "blur": {"node": "ImageFiltered", "sigmaX": 6, "sigmaY": 6,
                         "applies_to": "background + text + foreground as one subtree"}},
            5: {"shapes": "blue bar (20,100,280,40); red/green/purple bars at y=24 with transparent gaps; "
                          "yellow square (224,150,60,60); dark rect (110,150,100,60) with boxShadow 0 6 10 0 #00000066",
                "color_filter": {"node": "ColorFiltered", "color": FILTER_COLOR, "blendMode": "MULTIPLY", "position": "inner"},
                "blur": {"node": "ImageFiltered", "sigmaX": 6, "sigmaY": 6, "position": "outer"},
                "clip": None},
            6: {"shapes": "identical to panel 5 (same filtered_scene XML)",
                "color_filter": "same as panel 5", "blur": "same as panel 5",
                "clip": {"node": "ClipOval", "center_local": [160, 120], "radius_px": 100,
                         "bbox_local": [60, 20, 260, 220], "position": "outermost"}},
        }[n],
        "effect_nodes": {
            1: ["Container color=#FF000080", "Container color=#0000FF80"],
            2: ["Opacity opacity=0.5", "Container color=#FF0000", "Container color=#0000FF"],
            3: ["ImageFiltered sigmaX=6 sigmaY=6 (background copy)", "ClipRRect borderRadius=20", "sharp Text + sharp foreground"],
            4: ["ImageFiltered sigmaX=6 sigmaY=6 (whole card subtree)", "ClipRRect borderRadius=20"],
            5: ["ColorFiltered color=#F6B94A blendMode=MULTIPLY", "ImageFiltered sigmaX=6 sigmaY=6"],
            6: ["ColorFiltered color=#F6B94A blendMode=MULTIPLY", "ImageFiltered sigmaX=6 sigmaY=6", "ClipOval r=100"],
        }[n],
        "caption_region_px": [ox, CAP_Y[k // 3], AW, 56],
        "description_region_px": [ox, DESC_Y[k // 3], AW, 80],
    })

paired = [
    {"pair": "3-4", "shared_params": {
        "stripes": {"period_px": 16, "dark_width_px": 8, "color": STRIPE_DARK, "phase": 0, "background": "#FFFFFF"},
        "card_local_xy": [40, 40], "card_size_px": [240, 160], "card_radius": 20, "card_base_color": "#FFFFFF33",
        "text": "SHARP / BLUR @ 24px #0F172A", "foreground_shape": "teal 72x20 at local (20,116)",
        "sigmaX": 6, "sigmaY": 6, "clip": "ClipRRect borderRadius=20"},
     "only_difference": "③ 只对背景条纹副本做 ImageFiltered，文字/前景在滤镜外保持清晰；④ 把背景+文字+前景整棵子树放进同一个 ImageFiltered。场景、位置、颜色、层次完全相同。",
     "circle_clip": None},
    {"pair": "5-6", "shared_params": {
        "shapes": "identical (blue bar crossing circle, 3 spaced bars with transparent gaps, yellow square, dark rect with boxShadow)",
        "color_filter": "ColorFiltered #F6B94A MULTIPLY (inner)",
        "blur": "ImageFiltered sigmaX=6 sigmaY=6 (outer)", "order": "color filter first, then blur"},
     "only_difference": "⑥ 在最外层增加 ClipOval 圆形裁剪；⑤ 不加裁剪，效果外溢到整个 320×240 实验区。其余节点与参数逐字相同。",
     "circle_clip": {"center_local": [160, 120], "radius_px": 100, "bbox_local": [60, 20, 260, 220],
                     "crossing_shape": "blue bar (20,100)-(300,140) crosses the circle at x≈60 and x≈260; yellow square crosses near x=240"}},
]

samples = [
    {"panel": 1, "local": [180, 100], "canvas_pixel": [372, 280],
     "compositing_steps": [
         "white (255,255,255)",
         "red (255,0,0) with a=128/255 over white -> (255, 255*127/255, 255*127/255)",
         "blue (0,0,255) with a=128/255 over previous -> (255*127/255, (255*127/255)*(127/255), 255*128/255 + (255*127/255)*(127/255))"],
     "alpha_used": "128/255 = 0.501960784 (#80)", "theoretical_float_rgb": [rnd(v) for v in p1],
     "rounding": "floor(v+0.5)", "rounded_rgb": round_rgb(p1),
     "actual_rgb": None, "actual_alpha": None, "channel_errors": None,
     "tolerance_per_channel": 3, "passed": None,
     "pending_reason": "PNG 尚未渲染/采样；sample.py 填真实值。"},
    {"panel": 2, "local": [180, 100], "canvas_pixel": [740, 280],
     "compositing_steps": [
         "inside the Opacity group: opaque blue covers opaque red -> (0,0,255,255)",
         "composite the flattened group with alpha=0.5 over white -> (0*0.5+255*0.5, 0*0.5+255*0.5, 255*0.5+255*0.5)"],
     "alpha_used": "0.5 (Opacity widget); Skia may quantise to 128/255, hence tolerance 3",
     "theoretical_float_rgb": [rnd(v) for v in p2],
     "rounding": "floor(v+0.5)", "rounded_rgb": round_rgb(p2),
     "actual_rgb": None, "actual_alpha": None, "channel_errors": None,
     "tolerance_per_channel": 3, "passed": None,
     "pending_reason": "PNG 尚未渲染/采样；sample.py 填真实值。"},
]

visual_checks = []
for n in (3, 4, 5, 6):
    visual_checks.append({
        "panel": n,
        "observation": None,
        "text_sharp": None, "background_blurred": None, "effect_spills": None,
        "dsl_nodes": ["see panels[%d].effect_nodes" % (n - 1)],
        "local_evidence": "tmp/<run_id>/A10/inspect/panel_%d.png (2x crop of the 320x240 area)" % n,
        "doc_sources": ["tmp/20261104-145656-hy4all/_suite/docs/parser-tags.md (ColorFiltered / ImageFiltered / BackdropFilter / ClipRRect / ClipOval / Opacity / 8-digit colours)",
                        "tmp/20261104-145656-hy4all/_suite/AGENT-BRIEF.md (BackdropFilter produces no visible blur on this service; use ClipRRect + ImageFiltered on a background copy)"],
        "pending_reason": "需渲染后打开整图与局部放大，按实际观察填写，不把预期描述当成观察结果。",
    })

audit = {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "units": {"rgb": "0-255 sRGB 8-bit channels", "alpha": "#RRGGBBAA last byte / 255, or Opacity double",
              "coordinates": "px, panel-local origin = panel top-left, canvas origin = image top-left"},
    "alpha_explanation": "① 两个矩形各自带 #80 = 128/255 ≈ 0.50196 的 alpha，与白底逐层 source-over；② 两个不透明矩形先在一层内合成（蓝盖红），整层再以 Opacity(0.5) 与白底混合一次。128/255 不是精确 0.5：若把 ① 误用 0.5 会得到 (128,64,191) 而不是 (127,63,191)，相差 1；更重要的是逐层混合 vs 整组单层混合使 G/B 通道差异巨大（63/191 对 128/255）。",
    "panels": panels,
    "paired_scenes": paired,
    "samples": samples,
    "visual_checks": visual_checks,
    "evidence": {"png": "compositing-lab.png", "dsl": "compositing-lab.snapshot",
                 "checks": ["①② 采样点 alpha 须 255", "每通道误差 ≤3", "③④ 唯一差异为模糊层",
                            "⑤⑥ 唯一差异为圆形裁剪", "③–⑥ 视觉判断引用实际整图/局部"]},
}
(out / "composite-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("A10 DSL bytes", len(dsl.encode("utf-8")))
print("panel1 theoretical", [rnd(v) for v in p1], "rounded", round_rgb(p1))
print("panel2 theoretical", [rnd(v) for v in p2], "rounded", round_rgb(p2))
