"""A10: 1440x1100 compositing / filter semantics lab, six 320x240 white experiment areas.

Everything is drawn from tmp/<run_id>/A10/plan_a10.json, so a number printed on the board is
the same number check_a10.py measures against.

Six experiments, each isolating one compositing question:
  1  two rectangles that each carry 50% hex alpha   -> per-layer source-over
  2  the same two *opaque* rectangles in one Opacity(0.5) group -> flatten, then fade
  3  rounded card over sharp stripes, only the backdrop inside the card is blurred
  4  the same card, but its text + shapes are blurred as one subtree
  5  ColorFiltered(MULTIPLY #F6B94A) and then a subtree gaussian blur
  6  the 5 chain again, confined to a circular clip drawn over an unfiltered base

Coordinates inside a filtered/clipped subtree are box-local (the subtree is one Positioned
box on the canvas), which keeps the "what exactly is the subtree" question answerable.

Gates before any DSL is emitted: every text box passes the pre-render fit gate (>= 20pt),
the document stays under the service's 4096-element cap.
"""
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(ROOT / "tmp" / RID / "_suite" / "scripts"))
from dslkit import Doc, TextFit, n  # noqa: E402

TASK = "A10"
TEMP = ROOT / "tmp" / RID / TASK
OUT = ROOT / "outputs" / RID / TASK
VERSION = os.environ.get("DSL_VERSION", "v01")
plan = json.loads((TEMP / "plan_a10.json").read_text(encoding="utf-8"))

W, H = plan["canvas"]
LAY = plan["layout"]
F = plan["filters"]
SH = plan["shapes"]
PRED = plan["predicted"]

BG, PANEL, PANEL_LINE = "#0A1120", "#0F1A2E", "#26374F"
WHITE, STAGE_LINE = LAY["area_background"], "#C2CCDE"
INK, DIM, FAINT = "#E9EFF9", "#9FB0C9", "#7086A6"
ACCENT, VIOLET, BBOX = "#38BDF8", "#A78BFA", "#34D399"
AMBER = PRED["multiply"]["filter_color"]
SIG, STRIPE = F["sigmaX"], F["stripe"]["color"]
PITCH, SWID = F["stripe"]["pitch"], F["stripe"]["width"]
CARD, CR = F["card"]["rect_in_area"], F["card"]["radius"]
CARDTXT, FS = F["card"]["text"], F["card"]["text_font_size"]
CONTENT_ORIGIN, CONTENT_SIZE = [60, 45], [200, 150]
CIRCLE_R = 100
SHADOW = "0 6 14 0 #00000066 NORMAL"

p = Doc(W, H, bg=BG)
fit = TextFit()


def box(w, h, nodes=None, color=None, radius=None, border=None):
    """a sized Container; `nodes` are Positioned children in box-local coordinates"""
    inner = ('<Stack alignment="TOP_LEFT" clipBehavior="NONE">' + "".join(nodes) + "</Stack>") \
        if nodes else None
    return p.box(w, h, color=color, radius=radius, border=border, inner=inner)


def place(x, y, w, h, node):
    p.pos(x, y, w, h, node)


def rect(x, y, w, h, color, radius=None, border=None, shadow=None):
    return (f'<Positioned left="{x:g}" top="{y:g}" width="{w:g}" height="{h:g}">'
            + box(w, h, color=color, radius=radius, border=border) + "</Positioned>") \
        if not shadow else (
            f'<Positioned left="{x:g}" top="{y:g}" width="{w:g}" height="{h:g}">'
            f'<Container width="{w:g}" height="{h:g}" color="{color}" '
            f'boxShadow="{shadow}"/></Positioned>')


def txt(x, y, w, h, s, size, color, weight="BOLD"):
    return (f'<Positioned left="{x:g}" top="{y:g}" width="{w:g}" height="{h:g}">'
            + p.text(s, color=color, size=size, style=weight, align="CENTER")
            + "</Positioned>")


def lbl(x, y, w, h, s, size=20, color=DIM, style=None, align="START", tag=None, lines=1):
    p.label(x, y, w, h, s, color, size, style, align=align)
    fit.check(tag or f"t{int(x)}-{int(y)}", s, size, w, h, lines=lines)


def filtered(content, color_filter=True, blur=True):
    node = content
    if color_filter:
        node = f'<ColorFiltered color="{AMBER}" blendMode="MULTIPLY">{node}</ColorFiltered>'
    if blur:
        node = (f'<ImageFiltered sigmaX="{SIG:g}" sigmaY="{SIG:g}" tileMode="CLAMP">'
                + node + "</ImageFiltered>")
    return node


def content_box():
    return box(CONTENT_SIZE[0], CONTENT_SIZE[1], [
        rect(0, 5, 120, 80, "#1E293B", shadow=SHADOW),
        rect(95, 85, 105, 60, "#0F172A"),
        rect(150, 0, 44, 44, None, radius=22, border="7 SOLID #22D3EE"),
    ])


def stripes_box(w, h):
    """sharp vertical stripes that run the full area, so they cross the card edge"""
    nodes = [rect(i * PITCH, 0, SWID, h, STRIPE)
             for i in range((w + PITCH - 1) // PITCH)]
    return box(w, h, nodes, color=WHITE)


# ---------------------------------------------------------------- title band
lbl(40, 30, 560, 44, "看到差异，才能说用对了", 34, INK, "BOLD", tag="title")
lbl(40, 82, 980, 26, "六格透明合成与滤镜语义实验板 · 实验区 320×240 白底 · 3 列 × 2 行 · "
                     "滤镜 sigmaX=sigmaY=6", 20, DIM, tag="sub1")
lbl(40, 110, 980, 26, "格内数字为按 source-over / MULTIPLY 公式算出的期望值，"
                      "交付前在同一点实测", 20, FAINT, tag="sub2")
lbl(1040, 30, 360, 26, "绿圈 ①② = 采样点 (180,100)", 20, DIM, align="END", tag="t1")
lbl(1040, 58, 360, 26, "③④ 卡片 240×160 圆角 20", 20, FAINT, align="END", tag="t2")
lbl(1040, 86, 360, 26, "⑤ 紫框 = 滤镜作用盒 200×150", 20, VIOLET, align="END", tag="t3")
lbl(1040, 114, 360, 26, "⑤⑥ 滤色 #F6B94A σ=6", 20, FAINT, align="END", tag="t4")
p.line(40, 142, W - 40, 142, 1, PANEL_LINE)

# ---------------------------------------------------------------- slot frames
AREAS = {}
for c in plan["cells"]:
    sx, sy, sw, sh = c["slot_rect"]
    ax, ay = c["area_origin"]
    AREAS[c["number"]] = (ax, ay)
    place(sx, sy, sw, sh, box(sw, sh, color=PANEL, radius=14, border=f"1 SOLID {PANEL_LINE}"))
    lbl(sx + 16, sy + 10, 40, 30, c["number"], 26, ACCENT, "BOLD", tag=c["number"])
    lbl(sx + 52, sy + 14, sw - 68, 26, c["name"], 20, INK, tag=c["number"] + "-name")
    place(ax, ay, 320, 240, box(320, 240, color=WHITE, radius=4,
                                border=f"1 SOLID {STAGE_LINE}"))

# ---------------------------------------------------------------- ① per-layer alpha
a1 = AREAS["①"]
place(a1[0], a1[1], 320, 240, box(320, 240, [
    rect(*SH["red"]["xywh_in_area"][0:2], SH["red"]["xywh_in_area"][2],
         SH["red"]["xywh_in_area"][3], "#FF000080"),
    rect(*SH["blue"]["xywh_in_area"][0:2], SH["blue"]["xywh_in_area"][2],
         SH["blue"]["xywh_in_area"][3], "#0000FF80"),
]))

# ---------------------------------------------------------------- ② group opacity
a2 = AREAS["②"]
place(a2[0], a2[1], 320, 240,
      '<Opacity opacity="0.5">' + box(320, 240, [
          rect(*SH["red"]["xywh_in_area"][0:2], SH["red"]["xywh_in_area"][2],
               SH["red"]["xywh_in_area"][3], "#FF0000"),
          rect(*SH["blue"]["xywh_in_area"][0:2], SH["blue"]["xywh_in_area"][2],
               SH["blue"]["xywh_in_area"][3], "#0000FF"),
      ]) + "</Opacity>")

# ---------------------------------------------------------------- sample markers for ①②
# ring at radius 9 keeps the sampled pixel itself free of annotation ink; the point is
# identified in the title band instead of by a label inside the experiment area
for c in plan["cells"][:2]:
    mx, my = c["sample_canvas"]
    place(mx - 9, my - 9, 18, 18, box(18, 18, radius=9, border=f"2 SOLID {BBOX}"))

# ---------------------------------------------------------------- ③ backdrop only
a3 = AREAS["③"]
place(a3[0], a3[1], 320, 240, box(320, 240, [
    f'<Positioned left="0" top="0" width="320" height="240">'
    + stripes_box(320, 240) + "</Positioned>",
    f'<Positioned left="{CARD[0]:g}" top="{CARD[1]:g}" width="{CARD[2]:g}" '
    f'height="{CARD[3]:g}"><ClipRRect borderRadius="{CR}" clipBehavior="ANTI_ALIAS">'
    f'<BackdropFilter sigmaX="{SIG:g}" sigmaY="{SIG:g}" tileMode="CLAMP">'
    + box(CARD[2], CARD[3], color="#FFFFFF1A")
    + "</BackdropFilter></ClipRRect></Positioned>",
    rect(CARD[0], CARD[1], CARD[2], CARD[3], None, radius=CR, border="2 SOLID #0B1B3A"),
]))
lbl(a3[0] + CARD[0], a3[1] + CARD[1] + CARD[3] / 2 - FS, CARD[2], FS + 12, CARDTXT,
    FS, "#0B1B3A", "BOLD", align="CENTER", tag="c3-text")

# ---------------------------------------------------------------- ④ subtree blur
a4 = AREAS["④"]
# no border on this card: a blurred 2px rim would sit exactly where the 10-90% rise of the
# card edge is measured, so ④ shows the feathered fill alone and ③ keeps the sharp rim
card_sub = box(CARD[2], CARD[3], [
    rect(0, 0, CARD[2], CARD[3], "#FFFFFFB3", radius=CR),
    txt(0, CARD[3] / 2 - FS, CARD[2], FS + 12, CARDTXT, FS, "#0B1B3A"),
])
place(a4[0], a4[1], 320, 240, box(320, 240, [
    f'<Positioned left="0" top="0" width="320" height="240">'
    + stripes_box(320, 240) + "</Positioned>",
    f'<Positioned left="{CARD[0]:g}" top="{CARD[1]:g}" width="{CARD[2]:g}" '
    f'height="{CARD[3]:g}"><ImageFiltered sigmaX="{SIG:g}" sigmaY="{SIG:g}" '
    f'tileMode="CLAMP">' + card_sub + "</ImageFiltered></Positioned>",
]))

# ---------------------------------------------------------------- ⑤ multiply then blur
a5 = AREAS["⑤"]
place(a5[0] + CONTENT_ORIGIN[0], a5[1] + CONTENT_ORIGIN[1], *CONTENT_SIZE,
      filtered(content_box()))

# ---------------------------------------------------------------- ⑥ clipped to a circle
a6 = AREAS["⑥"]
place(a6[0] + CONTENT_ORIGIN[0], a6[1] + CONTENT_ORIGIN[1], *CONTENT_SIZE, content_box())
cx6 = CONTENT_ORIGIN[0] + CONTENT_SIZE[0] / 2 - CIRCLE_R
cy6 = 120 - CIRCLE_R
place(a6[0] + cx6, a6[1] + cy6, 2 * CIRCLE_R, 2 * CIRCLE_R,
      f'<ClipOval clipBehavior="ANTI_ALIAS">'
      + '<Stack alignment="TOP_LEFT" clipBehavior="NONE">'
      + f'<Positioned left="{CONTENT_ORIGIN[0] - cx6:g}" '
        f'top="{CONTENT_ORIGIN[1] - cy6:g}" width="{CONTENT_SIZE[0]:g}" '
        f'height="{CONTENT_SIZE[1]:g}">' + filtered(content_box()) + "</Positioned>"
      + "</Stack></ClipOval>")

# violet rectangle = the drawing bounds the ⑤ filter chain is applied to
for c in (plan["cells"][4],):
    ax, ay = c["area_origin"]
    ox, oy = ax + CONTENT_ORIGIN[0], ay + CONTENT_ORIGIN[1]
    w6, h6 = CONTENT_SIZE
    p.line(ox, oy, ox + w6, oy, 1, VIOLET)
    p.line(ox, oy + h6, ox + w6, oy + h6, 1, VIOLET)
    p.line(ox, oy, ox, oy + h6, 1, VIOLET)
    p.line(ox + w6, oy, ox + w6, oy + h6, 1, VIOLET)

# ---------------------------------------------------------------- captions
CAP = {
    "①": ["红 #FF000080 蓝 #0000FF80",
          "各带 alpha＝128/255＝0.502",
          "重叠 (180,100) 期望 (127,63,191)",
          "红侧 (255,127,127) 蓝侧 (127,127,255)"],
    "②": ["不透明红蓝放进 Opacity(0.5) 组",
          "组内先拍平：重叠只剩纯蓝",
          "整层按 0.5 合成 → (128,128,255)±2",
          "与①同点相差 (1,65,64)：差在顺序"],
    "③": ["条纹清晰，卡内只糊背景",
          "BackdropFilter 读取已绘内容",
          "文字 SHARP / BLUR 保持锐利",
          "卡内波纹实测 14 级，卡外 226 级"],
    "④": ["ImageFiltered 包住卡内子树",
          "文字与形状一起被模糊",
          "卡边无描边：羽化台阶 ≈15px",
          "条纹本体清晰，未被滤镜触及"],
    "⑤": ["MULTIPLY #F6B94A 后再模糊",
          "透明间隙被染成实心琥珀",
          "深矩形 (30,41,59)→(29,30,17)±1",
          "晕染越盒沿，50% 点在框外 15px"],
    "⑥": ["⑤ 的链套进 ClipOval",
          "圆外是未滤镜的原图",
          "青环界外仍是 (34,211,238)",
          "裁剪边界硬：台阶 1–3px"],
}
for c in plan["cells"]:
    sx, sy, sw, sh = c["slot_rect"]
    for i, line in enumerate(CAP[c["number"]]):
        lbl(sx + 16, sy + 292 + i * 30, sw - 32, 26, line, 20,
            DIM if i else INK, tag=f"{c['number']}-cap{i}")

# ---------------------------------------------------------------- footer
p.line(40, 1016, W - 40, 1016, 1, PANEL_LINE)
lbl(40, 1028, 900, 26, "文档依据：「透明度与颜色滤镜」「Opacity 与 Transform」",
    20, FAINT, tag="f1")
lbl(980, 1028, 420, 26, "①② source-over · ⑤⑥ dst×filter", 20, FAINT, align="END",
    tag="f2")
lbl(40, 1056, 1360, 26, "裁剪区与滤镜边界另见「ClipRect、ClipOval 与 ClipRRect」；"
                        f"台阶 10–90% 上升宽度 sigma=6 预测 ≈ "
                        f"{F['predicted_step_edge_rise_10_90_px']}px", 20, FAINT, tag="f3")

# ---------------------------------------------------------------- gate
dsl = p.dsl()
elements = len(re.findall(r"<[A-Za-z]", dsl))
assert elements <= 4000, f"service caps a document at 4096 elements, got {elements}"
report = {
    "version": VERSION,
    "bytes": len(dsl.encode("utf-8")),
    "elements": elements,
    "text_items": fit.n,
    "fit_problems": fit.problems,
    "cells": len(plan["cells"]),
    "min_font_pt": min(int(s) for s in re.findall(r'fontSize="(\d+)"', dsl)),
    "filters_used": sorted(set(re.findall(r"<(Opacity|ColorFiltered|ImageFiltered|"
                                          r"BackdropFilter|ClipRRect|ClipOval)", dsl))),
    "footer_bottom": 1082,
}
assert report["footer_bottom"] <= H - 10, report["footer_bottom"]
(TEMP / "fit-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1),
                                      encoding="utf-8")
(TEMP / f"{VERSION}.snapshot").write_text(dsl, encoding="utf-8")
if VERSION == "final":
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "compositing-lab.snapshot").write_text(dsl, encoding="utf-8")
print(json.dumps(report, ensure_ascii=False))
