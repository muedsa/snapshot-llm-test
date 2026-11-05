#!/usr/bin/env python3
"""A13 · 品牌标志到完整活动应用 (Layerlight / 叠光).

Selected direction A (after viewing both 512 transparent previews and their
32x32 thumbnails): two offset rounded-square RINGS sharing one aligned
transparent core hole, plus a light dot.  The exact same geometric rule
(draw_symbol) is reused to redraw the mark inside the banner and the poster;
no rendered icon PNG is ever embedded.
"""
import json
import os
import sys

TOOLS = os.environ["TOOLS"]
sys.path.insert(0, TOOLS)
from dsl import Canvas, CN, LATIN, MONO  # noqa: E402
import suite  # noqa: E402

TASK = "A13"
ROOT = suite.ROOT
TMP = suite.tmp_dir(TASK)
sys.path.insert(0, str(TMP))
from thumbnail import TOOL_INFO  # noqa: E402

# ------------------------------------------------------------------ tokens
BLUE = "#1D4ED8"
CYAN = "#22D3EE"
AMBER = "#FBBF24"
INK = "#0B1B35"
NAVY = "#0B2545"
NAVY2 = "#16386F"
PAPER = "#F4F7FC"
WHITE = "#FFFFFF"
MUTED = "#5B6B85"
LINE = "#DDE5F0"
BLACK = "#000000"

COLOR_PAL = (BLUE, CYAN, AMBER)
BLACK_PAL = (BLACK, BLACK, BLACK)

# 512-basis geometry (final, small-size refined)
P1_OUT = (56, 56, 336, 336)
P2_OUT = (112, 112, 336, 336)
HOLE = (192, 192, 128, 128)
R_OUT, R_HOLE = 56, 22
DOT = (400, 112, 30)


def rr_path(x, y, w, h, r):
    return (f"M{x+r} {y} H{x+w-r} A{r} {r} 0 0 1 {x+w} {y+r} "
            f"V{y+h-r} A{r} {r} 0 0 1 {x+w-r} {y+h} "
            f"H{x+r} A{r} {r} 0 0 1 {x} {y+h-r} "
            f"V{y+r} A{r} {r} 0 0 1 {x+r} {y} Z")


def draw_symbol(c, ox, oy, s, palette):
    """Same DSL geometry rule at any origin/scale. 3 main components only."""
    def X(v):
        return ox + v * s / 512.0

    def Y(v):
        return oy + v * s / 512.0

    def R(v):
        return v * s / 512.0

    def rr(t):
        return rr_path(X(t[0]), Y(t[1]), R(t[2]), R(t[3]), R(t[4] if len(t) > 4 else R_OUT))

    hole = rr_path(X(HOLE[0]), Y(HOLE[1]), R(HOLE[2]), R(HOLE[3]), R(R_HOLE))
    x1, y1, w1, h1 = P1_OUT
    x2, y2, w2, h2 = P2_OUT
    d1 = rr_path(X(x1), Y(y1), R(w1), R(h1), R(R_OUT)) + " " + hole
    d2 = rr_path(X(x2), Y(y2), R(w2), R(h2), R(R_OUT)) + " " + hole
    c.path(d1, palette[0], fill_rule="EVEN_ODD")
    c.path(d2, palette[1], fill_rule="EVEN_ODD")
    c.circle(X(DOT[0]), Y(DOT[1]), R(DOT[2]), palette[2])


# ================================================================== icons
def icon(palette):
    c = Canvas(512, 512, "transparent")
    draw_symbol(c, 0, 0, 512, palette)
    return c.render()


# ================================================================== banner
def banner():
    c = Canvas(1200, 400, PAPER)
    c.rect(0, 0, 1200, 6, CYAN)
    c.rect(0, 394, 1200, 6, BLUE)
    # left: the mark redrawn with the same DSL geometry (no embedded PNG)
    c.rect(40, 40, 320, 320, WHITE, radius=24, border="1 SOLID " + LINE)
    draw_symbol(c, 60, 60, 280, COLOR_PAL)
    # right: wordmark + tagline
    c.text(400, 96, 760, 92, "叠光 Layerlight", 64, INK, bold=True)
    c.rect(400, 200, 88, 6, CYAN, radius=3)
    c.text(400, 224, 760, 56, "把复杂信息，组织成清晰画面", 34, MUTED)
    c.text(400, 306, 760, 34, "LAYERLIGHT  ·  STRUCTURED VISUAL TOOLS", 22, BLUE,
           font=LATIN, bold=True)
    c.text(940, 30, 220, 30, "BRAND / 2026", 20, MUTED, font=LATIN, align="RIGHT")
    return c.render()


# ================================================================== poster
def poster():
    c = Canvas(1080, 1350, PAPER)
    # upper dark stage
    c.gradient(0, 0, 1080, 720, [NAVY, NAVY2], begin="TOP_LEFT", end="BOTTOM_RIGHT")
    c.rect(0, 0, 1080, 6, CYAN)
    c.text(64, 44, 600, 34, "LAYERLIGHT  /  VISUAL SYSTEM", 22, "#8FB6EA",
           font=LATIN, bold=True)
    c.text(800, 44, 216, 34, "2026", 22, "#8FB6EA", font=LATIN, align="RIGHT")
    # large mark, same geometry rule
    draw_symbol(c, 300, 108, 480, COLOR_PAL)
    c.text(64, 596, 700, 96, "OPEN BETA", 82, WHITE, font=LATIN, bold=True)
    c.rect(64, 686, 180, 8, CYAN, radius=4)
    # lower light stage: independent vertical composition
    c.text(64, 760, 952, 96, "叠光 Layerlight", 72, INK, bold=True)
    c.text(64, 872, 952, 58, "把复杂信息，组织成清晰画面", 36, MUTED)
    c.hline(64, 962, 952, 2, LINE)
    c.text(64, 990, 560, 52, "2026.11.07 · ONLINE", 32, INK, bold=True)
    c.text(64, 1054, 560, 44, "结构化视觉工具 / Open Beta", 24, MUTED)
    c.rect(64, 1130, 620, 72, NAVY, radius=36)
    c.text(88, 1130, 572, 72, "layerlight.example.org", 30, WHITE,
           font=LATIN, bold=True, align="CENTER")
    # small repeated instance of the same geometry as a signature
    draw_symbol(c, 876, 1124, 140, COLOR_PAL)
    c.text(64, 1260, 952, 34, "信息叠加后仍然清晰  ·  STRUCTURE AFTER OVERLAY", 20, MUTED)
    return c.render()


# ------------------------------------------------------------------ emit
dsls = {
    "symbol-color": icon(COLOR_PAL),
    "symbol-black": icon(BLACK_PAL),
    "brand-banner": banner(),
    "launch-poster": poster(),
}
out = suite.out_dir(TASK)
ver = os.environ.get("BUILD_VERSION", "v1")
tmp = suite.tmp_dir(TASK, ver)
for name, dsl in dsls.items():
    (out / (name + ".snapshot")).write_text(dsl, encoding="utf-8")
    (tmp / (name + ".snapshot")).write_text(dsl, encoding="utf-8")

# ------------------------------------------------------------------ rationale.md
rationale = """# 方向选择与小尺寸改进（叠光 / Layerlight）

两方向均为 512×512 透明 DSL 预览。A 为两个错位圆角方环叠加、共用中央透明方孔，右上加光点；B 为同心圆环加对角光带与中心圆。实际打开两张预览及 32×32 缩略后选 A：A 的阶梯轮廓与方孔在 32 像素仍一眼可辨，呼应「信息叠加后仍然清晰」；B 的斜带与中心圆在小尺寸粘连，环内负空间被挤占、层次变糊。小尺寸改进：层间错位 48→56、中央方孔 120→128、光点半径 26→30，并统一两层圆角，使缩略后边带、方孔、光点均保持约 3 像素且互不粘连。
"""
(out / "rationale.md").write_text(rationale, encoding="utf-8")

# ------------------------------------------------------------------ brand-system.json
def box(t):
    return [t[0], t[1], t[0] + t[2], t[1] + t[3]]


components = [
    {"id": "P1", "shape": "圆角方环（圆角矩形外轮廓 − 圆角矩形内孔）", "instance": "后层",
     "outer": list(P1_OUT), "outer_radius": R_OUT, "hole": list(HOLE), "hole_radius": R_HOLE,
     "fill_rule": "EVEN_ODD",
     "negative_space": "与 P2 内孔完全对齐，形成贯穿所有层的透明方孔（关键负空间）",
     "dsl": "c.path(rr_path(56,56,336,336,56) + ' ' + rr_path(192,192,128,128,22), BLUE, fill_rule='EVEN_ODD')",
     "counts_as": 1},
    {"id": "P2", "shape": "圆角方环（圆角矩形外轮廓 − 圆角矩形内孔）", "instance": "前层",
     "outer": list(P2_OUT), "outer_radius": R_OUT, "hole": list(HOLE), "hole_radius": R_HOLE,
     "fill_rule": "EVEN_ODD",
     "negative_space": "内孔与 P1 对齐；相对 P1 向右下错位 56px 形成阶梯轮廓",
     "dsl": "c.path(rr_path(112,112,336,336,56) + ' ' + rr_path(192,192,128,128,22), CYAN, fill_rule='EVEN_ODD')",
     "counts_as": 1},
    {"id": "P3", "shape": "实心圆", "instance": "光点",
     "center": [DOT[0], DOT[1]], "radius": DOT[2],
     "dsl": "c.circle(400,112,30,AMBER)", "counts_as": 1},
]

brand = {
    "schema_version": 1,
    "task_id": TASK,
    "path_base": "output_dir",
    "brand": {"name_zh": "叠光", "name_en": "Layerlight",
              "concept": "信息叠加后仍然清晰", "category": "结构化视觉工具"},
    "colors": {
        "primary": {"hex": BLUE, "role": "后层 / 主品牌蓝"},
        "secondary": {"hex": CYAN, "role": "前层 / 亮青"},
        "accent": {"hex": AMBER, "role": "光点 / 琥珀"},
        "ink": {"hex": INK, "role": "深色背景上的正文与标题"},
        "navy": {"hex": NAVY, "role": "海报深色舞台渐变起色"},
        "navy2": {"hex": NAVY2, "role": "海报深色舞台渐变止色"},
        "paper": {"hex": PAPER, "role": "浅色底 / 透明图标检查底"},
        "white": {"hex": WHITE, "role": "反白文字"},
        "muted": {"hex": MUTED, "role": "辅助说明文字"},
        "black": {"hex": BLACK, "role": "纯黑图标唯一色（所有非透明像素 R=G=B=0）"},
    },
    "geometry": {
        "basis": "512×512 画布，左上原点，x 向右 / y 向下，像素；应用按 scale = size/512 线性映射",
        "bounding_box": [56, 56, 448, 448],
        "core_negative_space": box(HOLE),
        "layer_offset": [56, 56],
        "alignment_rule": "P1 与 P2 的内孔坐标完全相同 → 透明方孔贯穿两环；层错位只改变外轮廓",
        "negative_space_rules": [
            "每个方环用 EVEN_ODD 双轮廓裁剪：外圆角矩形 + 内圆角矩形，内孔为负空间不另计构件",
            "两环内孔对齐，叠加后中央 [192,192,320,320] 保持 alpha=0",
            "环与环之间的透明缝隙与阶梯轮廓共同构成可识别的小尺寸外形",
        ],
        "components_total": 3,
        "counts_basis": "按可独立辨认的几何母形实例计数（不按 DSL 节点数）；每个带孔方环含外轮廓+内孔仍算 1 个母形，内孔为负空间不另计；分组/变换/定位不另计；3 ≤ 6",
        "max_allowed": 6,
    },
    "components": components,
    "clear_space": {
        "basis": "512 基准下图形包围盒 [56,56,448,448]，四边最小留白均为 56px",
        "value_px": 56,
        "ratio_of_canvas": 56 / 512,
        "ratio_of_symbol_extent": 56 / 392,
        "rule": "任何应用四周留白 ≥ 0.14 × 图标边长（约 1/7 图标尺寸）",
    },
    "applications": [
        {"file": "symbol-color.png", "dsl": "symbol-color.snapshot", "canvas": [512, 512],
         "transparent": True, "symbol_origin": [0, 0], "symbol_size": 512, "scale": 1.0,
         "palette": "color", "role": "透明彩色图标（主交付）"},
        {"file": "symbol-black.png", "dsl": "symbol-black.snapshot", "canvas": [512, 512],
         "transparent": True, "symbol_origin": [0, 0], "symbol_size": 512, "scale": 1.0,
         "palette": "black", "role": "透明纯黑图标（与彩色版几何相同，仅颜色不同）"},
        {"file": "brand-banner.png", "dsl": "brand-banner.snapshot", "canvas": [1200, 400],
         "transparent": False, "symbol_origin": [60, 60], "symbol_size": 280,
         "scale": 280 / 512, "palette": "color", "role": "横幅左侧主视觉（同一 draw_symbol 几何重绘）"},
        {"file": "launch-poster.png", "dsl": "launch-poster.snapshot", "canvas": [1080, 1350],
         "transparent": False, "symbol_origin": [300, 108], "symbol_size": 480,
         "scale": 480 / 512, "palette": "color",
         "extra_instance": {"origin": [876, 1124], "size": 140, "scale": 140 / 512},
         "role": "海报上半部主视觉 + 右下角签名实例；独立竖向构图，非横幅放大"},
    ],
    "shared_geometry_rule": "build.py draw_symbol(c, ox, oy, s, palette)：所有几何坐标以 512 为基准线性缩放，四个应用调用同一函数；未使用任何 <Image> 或渲染 PNG 嵌入",
    "black_check": {
        "decoder": "Pillow 13.0.0 Image.open(...).convert('RGBA')，对服务原始 PNG 解码后的未预乘 8 位 RGBA",
        "method": "遍历全部像素，对 alpha>0 的像素检查 R=G=B=0；统计违规像素数与实际 alpha 范围；alpha=0 的 RGB 不参与判断",
        "alpha_range": None,
        "alpha_gt0_pixels": None,
        "violating_pixels": None,
        "result": None,
        "evidence": {"path_base": "suite_root",
                     "path": "tmp/20261104-145656-hy4all/A13/black-check.json"},
    },
    "small_size_review": {
        "tool": TOOL_INFO,
        "light_background": PAPER,
        "previews": [
            {"source": "symbol-color.png",
             "thumb_rgba": "tmp/20261104-145656-hy4all/A13/preview/symbol-color-32.png",
             "on_light_32": "tmp/20261104-145656-hy4all/A13/preview/symbol-color-32-on-light.png",
             "zoom8": "tmp/20261104-145656-hy4all/A13/preview/symbol-color-32-zoom8.png"},
            {"source": "symbol-black.png",
             "thumb_rgba": "tmp/20261104-145656-hy4all/A13/preview/symbol-black-32.png",
             "on_light_32": "tmp/20261104-145656-hy4all/A13/preview/symbol-black-32-on-light.png",
             "zoom8": "tmp/20261104-145656-hy4all/A13/preview/symbol-black-32-zoom8.png"},
        ],
        "viewed_at_actual_32px": None,
        "observation": None,
    },
    "direction_previews": {
        "path_base": "suite_root",
        "direction_A": "tmp/20261104-145656-hy4all/A13/v0-previews/direction-A.png",
        "direction_B": "tmp/20261104-145656-hy4all/A13/v0-previews/direction-B.png",
        "chosen": "A",
        "choice_evidence": "两张 512 透明预览及 32×32 缩略均用 ViewImage 打开比较；见 rationale.md 与 finalize.json",
    },
}
(out / "brand-system.json").write_text(
    json.dumps(brand, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("A13 built | ver=%s | dsls=%d | components=%d | rationale_chars=%d" % (
    ver, len(dsls), len(components), len(rationale)))
for name, dsl in dsls.items():
    print("  %-15s %5d bytes" % (name, len(dsl.encode("utf-8"))))
