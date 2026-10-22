#!/usr/bin/env python3
"""A10 compositing lab generator + composite-audit.json (predicted parts).

Usage: python tmp/<run_id>/A10/scripts/gen_a10.py <suite_root> <run_id> [outdir]

1440x1100 board, six 320x240 white experiment areas (3 cols x 2 rows, gaps >=32),
numbers/descriptions outside the areas.  All local coordinates are panel-local
(origin = panel top-left OUTER edge, x right, y down, px).

Samples in panels 1/2 at local (180,100) are computed from first principles
(straight-alpha source-over in 0-255 sRGB, no intermediate rounding, final
RGB = floor(v + 0.5)); actual RGB is filled later by sample_a10.py from the
rendered PNG.
"""
import json
import math
import pathlib
import sys
from datetime import datetime, timezone, timedelta

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
run_id = sys.argv[2] if len(sys.argv) > 2 else "run-20261011-01"
out_dir = pathlib.Path(sys.argv[3]) if len(sys.argv) > 3 else (root / "outputs" / run_id / "A10")
tmp_dir = root / "tmp" / run_id / "A10"
tmp_drafts = tmp_dir / "drafts"
tmp_drafts.mkdir(parents=True, exist_ok=True)
out_dir.mkdir(parents=True, exist_ok=True)

W, H = 1440, 1100
PW, PH = 320, 240                     # experiment area size
COL_X = [144, 560, 976]               # integer canvas origins, gap 96 (>=32)
ROW_Y = [188, 584]                    # integer canvas origins, gap 156 (>=32)
FONT = "Inter,Noto Sans CJK SC"
PAGE = "#0B1120"
WHITE = "#FFFFFF"
STRIPE = "#334155"                    # 3/4 shared stripe colour
STRIPE_PITCH, STRIPE_W = 24, 12        # 3/4 shared stripe geometry (sigma=6 leaves visible soft bands)
CARD = [40, 40, 240, 160, 20]         # 3/4 shared card x,y,w,h,radius (panel-local)
CARD_FILL = "#FFFFFF99"               # 3/4 shared card fill (60% white)
CARD_TEXT = "SHARP / BLUR"
CARD_TEXT_SIZE = 24
BAR_COLOR, BAR_RECT = "#E11D48", [24, 84, 100, 16]
CIRCLE_SHAPE = [148, 72, 64, 64]      # card-local foreground shape
FILTER_COLOR = "#F6B94A"              # 5/6 multiply filter colour
SIGMA = 6                             # 3/4/5/6 sigmaX = sigmaY
OVAL = [160, 120, 100]                # 6 circle centre + radius (panel-local)
RED_HALF, BLUE_HALF = "#FF000080", "#0000FF80"
RED_OPAQUE, BLUE_OPAQUE = "#FF0000", "#0000FF"
R1 = [40, 40, 160, 120]               # 1/2 red rect (panel-local)
R2 = [120, 80, 160, 120]              # 1/2 blue rect (panel-local, on top)
SAMPLE = [180, 100]                   # 1/2 overlap interior sample point
S5_BAR = [(30, 70, 80, 40), (130, 70, 80, 40), (230, 70, 60, 40)]  # gaps 110-130,210-230
S5_DARK = (90, 140, 80, 60)
S5_SHADOW = (186, 136, 84, 56)
S5_SHADOW_CSS = "0 6 16 0 #00000059"

# ---- page text ----------------------------------------------------------------
TITLE = "看到差异，才能说用对了"
SUBTITLE = "六格对照：透明度作用层级 · 模糊作用层级 · 裁剪边界"
HEADINGS = [
    "① 逐层 alpha：两个半透明矩形",
    "② 组级 Opacity(0.5)",
    "③ 背景模糊（BackdropFilter）",
    "④ 子树模糊（ImageFiltered）",
    "⑤ MULTIPLY 滤色后再模糊",
    "⑥ ⑤ 基础上加圆形裁剪",
]
DESCS = [
    ["两个半透明矩形：#FF000080 / #0000FF80",
     "逐层两次 source-over（蓝压红合白底）"],
    ["同样不透明红蓝放进 Opacity(0.5) 组",
     "组内先合成为一层，最后只混合一次"],
    ["BackdropFilter σ=6：只模糊卡下条纹",
     "文字与前景在滤镜之后绘制，保持锐利"],
    ["ImageFiltered σ=6：同一场景整体模糊",
     "条纹、文字、前景一起被模糊；区外不变"],
    ["先 ColorFiltered(MULTIPLY #F6B94A)",
     "再 ImageFiltered σ=6 高斯模糊，无裁剪"],
    ["同⑤，最外层加 ClipOval 圆形裁剪",
     "圆心(160,120) r=100，圆外内容被裁掉"],
]
FOOTER = [
    "合成：服务指南颜色语法 #RRGGBBAA（alpha 在最后两位）；0–255 sRGB 直通 alpha 逐层 source-over 混合。",
    "滤镜：标签参考 Opacity / ColorFiltered / ImageFiltered / BackdropFilter / ClipRRect / ClipOval 与各自页面说明。",
    "证据：composite-audit.json 记录①②采样点理论/实际值，以及③–⑥整图与局部裁剪的实际观察（visual_checks）。",
]

origins = [[COL_X[c], ROW_Y[r]] for r in range(2) for c in range(3)]
assert PW * 3 + (COL_X[1] - COL_X[0] - PW) * 2 + COL_X[0] * 2 == W
for i in range(6):
    ox, oy = origins[i]
    assert ox in COL_X and oy in ROW_Y
assert COL_X[1] - (COL_X[0] + PW) >= 32 and ROW_Y[1] - (ROW_Y[0] + PH) >= 32

# ---- theory for the 1/2 samples ------------------------------------------------
A80 = 128.0 / 255.0                   # 0x80 -> 128/255 = 0.5019607843137255
A_HALF = 0.5


def floor_half(v):
    return int(math.floor(v + 0.5))


def over(top, top_a, dst):
    """straight-alpha source-over, channels 0-255, no intermediate rounding."""
    return [top[i] * top_a + dst[i] * (1.0 - top_a) for i in range(3)]


WHITE_RGB = [255.0, 255.0, 255.0]
RED_RGB = [255.0, 0.0, 0.0]
BLUE_RGB = [0.0, 0.0, 255.0]

# 1: red @128/255 over white, then blue @128/255 over that
s1_mid = over(RED_RGB, A80, WHITE_RGB)
s1_theory = over(BLUE_RGB, A80, s1_mid)
# same with alpha exactly 0.5 (for the 128/255 vs 0.5 explanation)
s1_mid_half = over(RED_RGB, A_HALF, WHITE_RGB)
s1_theory_half = over(BLUE_RGB, A_HALF, s1_mid_half)
# 2: opaque blue wins inside the group layer; the layer is composited once @0.5
s2_group = list(BLUE_RGB)
s2_theory = over(s2_group, A_HALF, WHITE_RGB)
# what a (wrong) per-child opacity would give, for the audit explanation
s2_per_child = over(BLUE_RGB, A_HALF, over(RED_RGB, A_HALF, WHITE_RGB))

# ---- DSL builder ---------------------------------------------------------------
def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def f(v):
    if isinstance(v, float):
        s = f"{v:.2f}".rstrip("0").rstrip(".")
        return s if s not in ("-0", "") else "0"
    return str(v)


class DSL:
    def __init__(self):
        self.o = []

    def rect(self, x, y, w, h, color, extra=""):
        self.o.append(f'<Positioned left="{f(x)}" top="{f(y)}" width="{f(w)}" height="{f(h)}">'
                      f'<Container color="{color}"{extra} /></Positioned>')

    def box(self, x, y, w, h, inner):
        self.o.append(f'<Positioned left="{f(x)}" top="{f(y)}" width="{f(w)}" height="{f(h)}">{inner}</Positioned>')

    def text(self, x, y, s, size=22, color="#F8FAFC", weight="NORMAL", w=None, align="START"):
        wa = f' width="{f(w)}"' if w is not None else ""
        ta = f' textAlign="{align}"' if align != "START" else ""
        self.o.append(f'<Positioned left="{f(x)}" top="{f(y)}"{wa}>'
                      f'<Text fontFamily="{FONT}" fontSize="{f(size)}" color="{color}" '
                      f'fontStyle="{weight}"{ta}>{esc(s)}</Text></Positioned>')

    def render(self, w, h, bg):
        return ('<Snapshot type="png" background="%s">\n  <SizedBox width="%d" height="%d">\n  '
                '<Stack alignment="TOP_LEFT" clipBehavior="NONE">\n    '
                % (bg, w, h)
                + "\n    ".join(self.o)
                + "\n  </Stack>\n  </SizedBox>\n</Snapshot>\n")


d = DSL()

# ---- page chrome ---------------------------------------------------------------
d.text(COL_X[0], 40, TITLE, 44, "#F8FAFC", "BOLD")
d.text(COL_X[0], 104, SUBTITLE, 22, "#94A3B8")
d.text(COL_X[0], 926, "依据与证据", 24, "#F8FAFC", "BOLD")
for i, line in enumerate(FOOTER):
    d.text(COL_X[0], 966 + i * 30, line, 20, "#CBD5E1")

for i in range(6):
    ox, oy = origins[i]
    row = i // 3
    hy = oy - 38 if row == 0 else oy - 38
    d.text(ox, hy, HEADINGS[i], 24, "#F8FAFC", "BOLD")
    for j, line in enumerate(DESCS[i]):
        d.text(ox, oy + PH + 14 + j * 28, line, 20, "#CBD5E1")


def panel_frame(ox, oy):
    d.rect(ox - 1, oy - 1, PW + 2, PH + 2, "#334155")     # 1px frame OUTSIDE the area
    d.rect(ox, oy, PW, PH, WHITE)


def panel_outline(ox, oy):
    """1px outline strictly outside the experiment area (never over it)."""
    d.rect(ox - 1, oy - 1, PW + 2, 1, "#64748B")
    d.rect(ox - 1, oy + PH, PW + 2, 1, "#64748B")
    d.rect(ox - 1, oy, 1, PH, "#64748B")
    d.rect(ox + PW, oy, 1, PH, "#64748B")


def stripes(dsl, dx, dy, n=PW, h=PH):
    """Shared 3/4 stripe field: dark 8px bar every 16px, phase x = 0 (mod 16)."""
    x = 0
    while x < n:
        dsl.rect(dx + x, dy, min(STRIPE_W, n - x), h, STRIPE)
        x += STRIPE_PITCH


# ---- panel 1: per-shape alpha ---------------------------------------------------
ox, oy = origins[0]
panel_frame(ox, oy)
d.rect(ox + R1[0], oy + R1[1], R1[2], R1[3], RED_HALF)
d.rect(ox + R2[0], oy + R2[1], R2[2], R2[3], BLUE_HALF)
panel_outline(ox, oy)

# ---- panel 2: group Opacity(0.5) -------------------------------------------------
ox, oy = origins[1]
panel_frame(ox, oy)
d.box(ox, oy, PW, PH,
      '<Opacity opacity="0.5"><Stack alignment="TOP_LEFT" clipBehavior="NONE">'
      f'<Positioned left="{R1[0]}" top="{R1[1]}" width="{R1[2]}" height="{R1[3]}">'
      f'<Container color="{RED_OPAQUE}" /></Positioned>'
      f'<Positioned left="{R2[0]}" top="{R2[1]}" width="{R2[2]}" height="{R2[3]}">'
      f'<Container color="{BLUE_OPAQUE}" /></Positioned>'
      '</Stack></Opacity>')
panel_outline(ox, oy)

# ---- shared card scene (card-local coords), used by 3 and 4 ----------------------
def card_scene_stack():
    return ('<Stack alignment="TOP_LEFT" clipBehavior="NONE">'
            f'<Positioned left="0" top="0" width="{CARD[2]}" height="{CARD[3]}">'
            f'<Container color="{CARD_FILL}" borderRadius="{CARD[4]}" /></Positioned>'
            f'<Positioned left="24" top="26"><Text fontFamily="{FONT}" fontSize="{CARD_TEXT_SIZE}" '
            f'color="#0F172A" fontStyle="BOLD">{CARD_TEXT}</Text></Positioned>'
            f'<Positioned left="{BAR_RECT[0]}" top="{BAR_RECT[1]}" width="{BAR_RECT[2]}" '
            f'height="{BAR_RECT[3]}"><Container color="{BAR_COLOR}" borderRadius="8" /></Positioned>'
            f'<Positioned left="{CIRCLE_SHAPE[0]}" top="{CIRCLE_SHAPE[1]}" width="{CIRCLE_SHAPE[2]}" '
            f'height="{CIRCLE_SHAPE[3]}"><Container color="#16A34A" shape="CIRCLE" /></Positioned>'
            '</Stack>')


# ---- panel 3: backdrop blur only -------------------------------------------------
ox, oy = origins[2]
panel_frame(ox, oy)
stripes(d, ox, oy)
d.box(ox + CARD[0], oy + CARD[1], CARD[2], CARD[3],
      f'<ClipRRect clipBehavior="ANTI_ALIAS" borderRadius="{CARD[4]}">'
      f'<Stack alignment="TOP_LEFT" clipBehavior="NONE">'
      f'<BackdropFilter sigmaX="{SIGMA}" sigmaY="{SIGMA}">'
      f'<Container width="{CARD[2]}" height="{CARD[3]}" color="{CARD_FILL}" borderRadius="{CARD[4]}" />'
      '</BackdropFilter>'
      f'<Positioned left="24" top="26"><Text fontFamily="{FONT}" fontSize="{CARD_TEXT_SIZE}" '
      f'color="#0F172A" fontStyle="BOLD">{CARD_TEXT}</Text></Positioned>'
      f'<Positioned left="{BAR_RECT[0]}" top="{BAR_RECT[1]}" width="{BAR_RECT[2]}" '
      f'height="{BAR_RECT[3]}"><Container color="{BAR_COLOR}" borderRadius="8" /></Positioned>'
      f'<Positioned left="{CIRCLE_SHAPE[0]}" top="{CIRCLE_SHAPE[1]}" width="{CIRCLE_SHAPE[2]}" '
      f'height="{CIRCLE_SHAPE[3]}"><Container color="#16A34A" shape="CIRCLE" /></Positioned>'
      '</Stack></ClipRRect>')
panel_outline(ox, oy)

# ---- panel 4: whole-subtree blur (same scene, blur layer changes) ----------------
ox, oy = origins[3]
panel_frame(ox, oy)
stripes(d, ox, oy)                                  # crisp base everywhere
sub = ('<Stack alignment="TOP_LEFT" clipBehavior="NONE">'
       f'<Positioned left="-40" top="-40" width="{PW}" height="{PH}">'
       f'<Container color="{WHITE}" /></Positioned>')
# panel-aligned stripe copy inside the card box (card origin = panel (40,40))
sx = 0
while sx < PW:
    sub += (f'<Positioned left="{sx - CARD[0]}" top="{-CARD[1]}" width="{STRIPE_W}" '
            f'height="{PH}"><Container color="{STRIPE}" /></Positioned>')
    sx += STRIPE_PITCH
sub += card_scene_stack()
sub += '</Stack>'
d.box(ox + CARD[0], oy + CARD[1], CARD[2], CARD[3],
      f'<ClipRRect clipBehavior="ANTI_ALIAS" borderRadius="{CARD[4]}">'
      f'<ImageFiltered sigmaX="{SIGMA}" sigmaY="{SIGMA}">{sub}</ImageFiltered></ClipRRect>')
panel_outline(ox, oy)


# ---- shared 5/6 scene (panel-local, offset applied for the clip box) --------------
def scene56(dx, dy):
    out = ""
    for (x, y, w, h) in S5_BAR:
        out += (f'<Positioned left="{f(x + dx)}" top="{f(y + dy)}" width="{w}" height="{h}">'
                f'<Container color="#2563EB" /></Positioned>')
    x, y, w, h = S5_DARK
    out += (f'<Positioned left="{f(x + dx)}" top="{f(y + dy)}" width="{w}" height="{h}">'
            f'<Container color="#1F2937" /></Positioned>')
    x, y, w, h = S5_SHADOW
    out += (f'<Positioned left="{f(x + dx)}" top="{f(y + dy)}" width="{w}" height="{h}">'
            f'<Container color="#EAB308" borderRadius="12" boxShadow="{S5_SHADOW_CSS}" /></Positioned>')
    return out


# ---- panel 5: MULTIPLY then subtree blur, no clip ---------------------------------
ox, oy = origins[4]
panel_frame(ox, oy)
inner = ('<Stack alignment="TOP_LEFT" clipBehavior="NONE">' + scene56(0, 0) + '</Stack>')
d.box(ox, oy, PW, PH,
      f'<ImageFiltered sigmaX="{SIGMA}" sigmaY="{SIGMA}">'
      f'<ColorFiltered color="{FILTER_COLOR}" blendMode="MULTIPLY">{inner}</ColorFiltered>'
      '</ImageFiltered>')
panel_outline(ox, oy)

# ---- panel 6: same as 5 + outermost circular clip --------------------------------
ox, oy = origins[5]
panel_frame(ox, oy)
box = [OVAL[0] - OVAL[2], OVAL[1] - OVAL[2], 2 * OVAL[2], 2 * OVAL[2]]
inner = ('<Stack alignment="TOP_LEFT" clipBehavior="NONE">'
         + scene56(-box[0], -box[1]) + '</Stack>')
d.box(ox + box[0], oy + box[1], box[2], box[3],
      f'<ClipOval clipBehavior="ANTI_ALIAS">'
      f'<ImageFiltered sigmaX="{SIGMA}" sigmaY="{SIGMA}">'
      f'<ColorFiltered color="{FILTER_COLOR}" blendMode="MULTIPLY">{inner}</ColorFiltered>'
      '</ImageFiltered></ClipOval>')
panel_outline(ox, oy)

# ---- write DSL -------------------------------------------------------------------
dsl = d.render(W, H, PAGE)
draft = tmp_drafts / "compositing-lab.snapshot"
draft.write_text(dsl, encoding="utf-8")

# ---- audit (predicted / theory parts; actual filled after render) ----------------
TZ = timezone(timedelta(hours=8))
panels = []
scene34 = {
    "stripes": {"colour": STRIPE, "pitch_px": STRIPE_PITCH, "width_px": STRIPE_W,
                "phase": "dark stripe starts at local x = 0 (mod 16)", "orientation": "vertical",
                "base": WHITE},
    "card": {"local_xywh_radius": CARD, "fill": CARD_FILL,
             "text": {"content": CARD_TEXT, "fontSize": CARD_TEXT_SIZE, "local_xy": [24, 26]},
             "foreground": {"bar": {"local_xywh": BAR_RECT, "color": BAR_COLOR, "radius": 8},
                            "circle": {"local_xywh": CIRCLE_SHAPE, "color": "#16A34A"}},
             "draw_order": ["panel white", "stripes", "card fill", "text", "bar", "circle"]},
}
scene56_params = {
    "filter_color": FILTER_COLOR, "blend_mode": "MULTIPLY", "sigmaX": SIGMA, "sigmaY": SIGMA,
    "transparent_gaps_panel_local": [[110, 70, 20, 40], [210, 70, 20, 40]],
    "bar_segments_panel_local": [list(s) for s in S5_BAR], "bar_color": "#2563EB",
    "dark_rect_panel_local": list(S5_DARK), "dark_rect_color": "#1F2937",
    "shadow_rect_panel_local": list(S5_SHADOW), "shadow_rect_color": "#EAB308",
    "box_shadow": S5_SHADOW_CSS,
    "draw_order": ["panel white (outside the filter)", "ColorFiltered(MULTIPLY) content "
                    "bar segments, dark rect, shadow rect", "ImageFiltered(sigma=6)"],
}
panel_meta = [
    ("per-shape alpha", ["Container color=#FF000080 (red, alpha 128/255)",
                         "Container color=#0000FF80 (blue, alpha 128/255, painted after red)"],
     "no filter; straight-alpha source-over onto the white panel"),
    ("group opacity", ["Opacity opacity=0.5 wrapping one Stack of two opaque Containers "
                       "(#FF0000 then #0000FF)"],
     "single layer: children composite at alpha 1, the layer is blended once at 0.5"),
    ("backdrop blur", ["white panel", "stripe field (crisp, full panel)",
                       "ClipRRect(40,40,240,160,r20) > BackdropFilter sigmaX=sigmaY=6 > "
                       "Container(#FFFFFFB3, r20)", "Text(SHARP / BLUR, 24)",
                       "bar + circle (crisp, painted after the filter)"],
     "BackdropFilter blurs only what is already painted behind the card"),
    ("subtree blur", ["white panel", "stripe field (crisp, full panel)",
                      "ClipRRect(40,40,240,160,r20) > ImageFiltered sigmaX=sigmaY=6 > "
                      "Stack(white base + panel-aligned stripes + card fill + text + bar + circle)"],
     "ImageFiltered blurs the whole subtree output, then ClipRRect clips it"),
    ("multiply + blur", ["white panel",
                         "ImageFiltered sigmaX=sigmaY=6 > ColorFiltered(color=#F6B94A, "
                         "blendMode=MULTIPLY) > Stack(bar segments, dark rect, shadow rect)"],
     "no clip: blur output may extend over the whole subtree bounds"),
    ("multiply + blur + oval clip", ["white panel",
                                     "ClipOval(box=(60,20,200,200)) > ImageFiltered sigmaX=sigmaY=6 > "
                                     "ColorFiltered(color=#F6B94A, blendMode=MULTIPLY) > Stack(same "
                                     "content offset by (-60,-20))"],
     "identical to panel 5 except the outermost circular clip"),
]
for i in range(6):
    ox, oy = origins[i]
    name, nodes, effect = panel_meta[i]
    panels.append({
        "panel": i + 1,
        "origin_px": [ox, oy],
        "size_px": [PW, PH],
        "local_coordinate_note": "origin = panel top-left OUTER edge, x right, y down, px; "
                                 "canvas_xy = origin_px + local_xy",
        "scene": scene34 if i in (2, 3) else (scene56_params if i in (4, 5) else
                 {"red_rect_local_xywh": R1, "red_color": RED_HALF if i == 0 else RED_OPAQUE,
                  "blue_rect_local_xywh": R2, "blue_color": BLUE_HALF if i == 0 else BLUE_OPAQUE,
                  "z_order": "red first, blue on top", "backdrop": WHITE,
                  "alpha": ("per-shape 0x80 = 128/255" if i == 0 else
                            "group Opacity 0.5 over opaque children")}),
        "effect_nodes": nodes,
        "effect_summary": effect,
    })

paired = [
    {"pair": "3-4", "shared_scene": scene34,
     "shared_parameters": ["stripe colour/width/pitch/phase", "card xywh+radius+fill",
                           "text content/size/position", "foreground shapes and draw order",
                           "sigmaX=sigmaY=6", "clip radius 20 on the same rounded card box"],
     "single_difference": "which layer the blur is applied to: panel 3 blurs only the backdrop "
                          "behind the card (BackdropFilter) then paints text/foreground crisp; "
                          "panel 4 blurs the identical background+text+foreground subtree "
                          "(ImageFiltered). No scene parameter differs.",
     "circular_clip": None},
    {"pair": "5-6", "shared_scene": scene56_params,
     "shared_parameters": ["filter colour #F6B94A", "blendMode MULTIPLY", "sigmaX=sigmaY=6",
                           "content geometry/colours/shadow (drawn through one shared builder "
                           "with a constant origin offset)", "white panel backdrop"],
     "single_difference": "panel 6 adds the outermost ClipOval circular clip; panel 5 has no clip",
     "circular_clip": {"center_local": [OVAL[0], OVAL[1]], "radius_px": OVAL[2],
                       "clip_box_local": box, "widget": "ClipOval clipBehavior=ANTI_ALIAS",
                       "clip_position": "outermost, wraps the blurred multiply result",
                       "crossing_shape": "bar segment (30,70,80,40) crosses the circle at "
                                         "x = 160 - sqrt(100^2 - (y-120)^2); segment (230,70,60,40) "
                                         "and the shadow rect cross on the right"}},
]


def sample_record(panel, theory, extra):
    ox, oy = origins[panel - 1]
    cx, cy = ox + SAMPLE[0], oy + SAMPLE[1]
    rec = {
        "panel": panel,
        "local_xy": list(SAMPLE),
        "index_note": "the (origin_x+180, origin_y+100)-th pixel of the decoded PNG, 0-based",
        "canvas_index_xy": [cx, cy],
        "origin_px": [ox, oy],
        "alpha_at_sample_expected": 255,
        "theory_float_rgb": theory,
        "theory_rounded_rgb": [floor_half(v) for v in theory],
        "rounding_rule": "floor(value + 0.5)",
        "actual_rgb": None,
        "actual_alpha": None,
        "abs_error_per_channel": None,
        "tolerance_per_channel": 3,
        "within_tolerance": None,
        "actual_note": "filled by tmp/run-20261011-01/A10/scripts/sample_a10.py from the final "
                       "service PNG (RGBA, unpremultiplied 8-bit)",
    }
    rec.update(extra)
    return rec


samples = [
    sample_record(1, s1_theory, {
        "composition_steps": [
            f"start from the white panel: dst = (255,255,255), alpha = 1",
            f"step 1 red #FF000080: src = (255,0,0), a = 128/255 = {A80!r}",
            f"  mid = src*a + dst*(1-a) = {s1_mid}",
            f"step 2 blue #0000FF80 on top: src = (0,0,255), a = 128/255",
            f"  out = src*a + mid*(1-a) = {s1_theory}",
            "final RGB = floor(value + 0.5)",
        ],
        "alpha_note": "0x80 = 128, and 128/255 = 0.5019607843137255 != 0.5; using exactly 0.5 "
                      f"would give {s1_theory_half} -> {[floor_half(v) for v in s1_theory_half]}, "
                      f"i.e. one unit higher in R and G than the {A80:.6f} result "
                      f"{[floor_half(v) for v in s1_theory]}. 128/255 and 0.5 are different "
                      "alphas and must not be conflated.",
    }),
    sample_record(2, s2_theory, {
        "composition_steps": [
            "inside Opacity(0.5) the two opaque children composite first (alpha 1 each):",
            "  group layer at the sample = blue (0,0,255) because blue is painted last on top",
            f"the layer is blended once onto the white panel: a = 0.5",
            f"  out = (0,0,255)*0.5 + (255,255,255)*0.5 = {s2_theory}",
            "final RGB = floor(value + 0.5)",
        ],
        "alpha_note": "group opacity applies a single 0.5 blend of the finished layer; it is not "
                      "the same as giving each child alpha 128/255. A per-child (incorrect) "
                      f"opacity-0.5 composite would yield {s2_per_child} -> "
                      f"{[floor_half(v) for v in s2_per_child]}, which fails the <=3 channel "
                      f"tolerance against {[floor_half(v) for v in s2_theory]}.",
        "contrast_with_panel1": "panel 1 blends twice (red over white, then blue over the result) "
                                "with a = 128/255; panel 2 blends once with a = 0.5",
    }),
]

audit = {
    "schema_version": 1,
    "task_id": "A10",
    "path_base": "output_dir",
    "run_id": run_id,
    "generated_at": datetime.now(TZ).isoformat(),
    "coordinate_system": {
        "canvas": {"width": W, "height": H, "origin": "top-left", "x_axis": "right",
                   "y_axis": "down", "units": "px"},
        "panel_local": "each 320x240 experiment area has its own origin at its top-left OUTER "
                       "edge; x right, y down, px; canvas_xy = origin_px + local_xy",
        "panel_origins_integer": True,
        "sample_mapping": "local (180,100) -> decoded PNG pixel (origin_x+180, origin_y+100), "
                          "0-based, taken from the final service PNG (not a screenshot)",
    },
    "artifacts": {"png": "compositing-lab.png", "dsl": "compositing-lab.snapshot",
                  "png_size_px": [W, H]},
    "alpha_notes": {
        "hex_alpha": "8-digit CSS colour is #RRGGBBAA (alpha in the last two digits), so "
                     "#FF000080 is red with alpha 0x80 = 128/255 = 0.5019607843137255",
        "why_not_half": "128/255 and 0.5 differ by 0.0019607843137254902; over two source-over "
                        "steps with a 255 white backdrop this moves the rounded R/G channels by "
                        "one unit, so the two alphas cannot be used interchangeably",
        "group_vs_per_shape": "Opacity(0.5) on a group blends the composited layer once; "
                              "per-shape alpha blends every shape against whatever is below it",
        "doc_source": "ai-guide.md: colours use CSS syntax #RRGGBBAA with alpha in the last two "
                      "digits; parser-tags.html: Opacity 'opacity defaults to 1, range 0..1, "
                      "applies to the whole subtree'",
    },
    "panels": panels,
    "paired_scenes": paired,
    "samples": samples,
    "visual_checks": [],   # filled after viewing the rendered crops
    "evidence": {"service_png": "compositing-lab.png",
                 "crops": {"path_base": "suite_root",
                           "paths": [f"tmp/{run_id}/A10/crops/panel{i}.png" for i in range(1, 7)]}},
}
(out_dir / "composite-audit.json").write_text(
    json.dumps(audit, ensure_ascii=False, indent=1), encoding="utf-8")

print("dsl:", draft, len(dsl))
print("panel origins:", origins)
print("samples:", origins[0][0] + 180, origins[0][1] + 100, "|",
      origins[1][0] + 180, origins[1][1] + 100)
print("theory 1:", s1_theory, "->", [floor_half(v) for v in s1_theory])
print("theory 2:", s2_theory, "->", [floor_half(v) for v in s2_theory])
print("theory1 @0.5:", s1_theory_half, "->", [floor_half(v) for v in s1_theory_half])
print("audit:", out_dir / "composite-audit.json")
