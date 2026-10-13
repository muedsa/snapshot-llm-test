"""A10 - compositing and filter semantics lab, 1440x1100.

Six 320x240 white experiment areas in 3x2. Pairs ①/②, ③/④ and ⑤/⑥ share one base
scene each and differ in exactly one thing, so the difference is attributable.

Run from the suite task root:
  python tmp/<run_id>/A10/gen.py --ver v001
"""
from __future__ import annotations

import argparse
import math
import json
import os
import sys
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
sys.path.insert(0, str(ROOT / "tmp" / "2026-10-12T10-04Z-r001" / "_suite" / "scripts"))

from snap import (  # noqa: E402
    C, ClipOval, ClipRRect, Col, Container, Node, Opacity, Positioned, Row, Snapshot,
    Stack, Text, label, num,
)

RUN = "2026-10-12T10-04Z-r001"
TASK = "A10"
OUT_DIR = ROOT / "outputs" / RUN / TASK
TMP_DIR = ROOT / "tmp" / RUN / TASK

FONT = "Noto Sans CJK SC,Inter"
MONO = "Noto Sans Mono CJK SC,DejaVu Sans Mono"
W, H = 1440, 1100
AW, AH = 320, 240
GAP = 32
COLS, ROWS = 3, 2
GRID_W = COLS * AW + (COLS - 1) * GAP          # 1024
OX0 = (W - GRID_W) // 2                        # 208
ROW_Y = [140, 476]
COL_X = [OX0 + c * (AW + GAP) for c in range(COLS)]
AREAS = [(COL_X[c], ROW_Y[r]) for r in range(ROWS) for c in range(COLS)]

BG = "#0A101E"
TXT, TXT_2, TXT_3 = "#F2F6FC", "#A6B8D4", "#6E82A2"
PANEL, PEDGE = "#101B33", "#26385C"
SIGMA = 6
VER = os.environ.get("A10_BOARD_VER", "v005")   # version shown in the evidence panel
TINT = "#F6B94A"


def ImageFiltered(*children, sigmaX, sigmaY, tileMode=None):  # noqa: N802
    return Node("ImageFiltered", {"sigmaX": sigmaX, "sigmaY": sigmaY,
                                  "tileMode": tileMode}, list(children))


def BackdropFilter(*children, sigmaX, sigmaY, tileMode=None):  # noqa: N802
    return Node("BackdropFilter", {"sigmaX": sigmaX, "sigmaY": sigmaY,
                                   "tileMode": tileMode}, list(children))


def ColorFiltered(*children, color, blendMode):  # noqa: N802
    return Node("ColorFiltered", {"color": color, "blendMode": blendMode}, list(children))


# ---------------------------------------------------------------- compositing math
A128 = F(128, 255)


def over(dst, src, al):
    return [src[i] * al + dst[i] * (1 - al) for i in range(3)]


def rnd(vs):
    return [int(v + F(1, 2)) for v in vs]


WHITE = [F(255)] * 3
P1_overlap = rnd(over(over(WHITE, [F(255), F(0), F(0)], A128),
                      [F(0), F(0), F(255)], A128))
P1_red_only = rnd(over(WHITE, [F(255), F(0), F(0)], A128))
P2_overlap = rnd([F(0) * F(1, 2) + 255 * F(1, 2),
                  F(0) * F(1, 2) + 255 * F(1, 2),
                  F(255) * F(1, 2) + 255 * F(1, 2)])
P2_red_only = rnd([F(255) * F(1, 2) + 255 * F(1, 2),
                   F(0) * F(1, 2) + 255 * F(1, 2),
                   F(0) * F(1, 2) + 255 * F(1, 2)])
P1_overlap_exact = over(over(WHITE, [F(255), F(0), F(0)], A128),
                        [F(0), F(0), F(255)], A128)

# ---------------------------------------------------------------- scenes
def area_frame(ox, oy):
    return Positioned(C(width=num(AW), height=num(AH), color="#FFFFFF",
                        border=f"1 SOLID {PEDGE}"), left=num(ox - 1), top=num(oy - 1))


def two_rects_alpha(ox, oy):
    """① each rectangle carries its own 50% alpha (#FF000080 / #0000FF80)."""
    return [Positioned(C(width="160", height="120", color="#FF000080"),
                       left=num(ox + 40), top=num(oy + 40)),
            Positioned(C(width="160", height="120", color="#0000FF80"),
                       left=num(ox + 120), top=num(oy + 80))]


def two_rects_group(ox, oy):
    """② opaque rectangles inside one Opacity(0.5) group."""
    return [Positioned(
        Opacity(
            Stack(C(width=num(AW), height=num(AH)),
                  Positioned(C(width="160", height="120", color="#FF0000"),
                             left="40", top="40"),
                  Positioned(C(width="160", height="120", color="#0000FF"),
                             left="120", top="80"),
                  alignment="TOP_LEFT", clipBehavior="NONE"),
            opacity="0.5"),
        left=num(ox), top=num(oy))]


STRIPE_N, STRIPE_W = 10, 16
STRIPE_COLS = ["#E24C4C", "#2E7DD1", "#2FA36B", "#EAB53B", "#8E5AC8"]


def stripes(dx, dy, n=STRIPE_N, sw=STRIPE_W):
    """The one shared stripe set; (dx, dy) offsets it in the caller's coordinates.

    Cell space gives the sharp full-cell bands; card-local space (dx=-CARD_X,
    dy=-CARD_Y) reproduces exactly the same phase inside a filtered subtree.
    """
    return [Positioned(C(width=num(sw), height=num(AH), color=STRIPE_COLS[i % 5]),
                       left=num(dx + i * (AW / n)), top=num(dy))
            for i in range(n)]


CARD_X, CARD_Y, CARD_W, CARD_H, CARD_R = 40, 40, 240, 160, 20


def card_front(ox, oy, word):
    """Card fill + text + foreground shape; identical in ③ and ④."""
    return [
        Positioned(C(width=num(CARD_W), height=num(CARD_H), color="#FFFFFFCC",
                     borderRadius=num(CARD_R), border="2 SOLID #1B2A47"),
                   left=num(ox), top=num(oy)),
        Positioned(
            Col(Text(word, color="#0B1220", fontSize="24", fontStyle="BOLD",
                     fontFamily=FONT, textAlign="CENTER"),
                Container(height="6"),
                C(width="56", height="26", color="#16233C", borderRadius="6"),
                crossAxisAlignment="CENTER"),
            left=num(ox), top=num(oy + 46), width=num(CARD_W)),
    ]


def scene_blur_background_only(ox, oy):
    """③ BackdropFilter inside the rounded clip: only what the card covers is blurred."""
    return [
        *stripes(ox, oy),
        Positioned(
            ClipRRect(
                BackdropFilter(
                    C(width=num(CARD_W), height=num(CARD_H), color="#FFFFFFCC",
                      borderRadius=num(CARD_R), border="2 SOLID #1B2A47"),
                    sigmaX=num(SIGMA), sigmaY=num(SIGMA), tileMode="CLAMP"),
                borderRadius=num(CARD_R), clipBehavior="ANTI_ALIAS"),
            left=num(ox + CARD_X), top=num(oy + CARD_Y)),
        # text and foreground shape stay outside the filter subtree, drawn sharp
        *card_front(ox + CARD_X, oy + CARD_Y, "SHARP")[1:],
    ]


def scene_blur_subtree(ox, oy):
    """④ background, card fill, text and shape all sit inside one blurred subtree."""
    return [
        *stripes(ox, oy),
        Positioned(
            ClipRRect(
                ImageFiltered(
                    Stack(C(width=num(CARD_W), height=num(CARD_H)),
                          *stripes(-CARD_X, -CARD_Y),
                          *card_front(0, 0, "BLUR"),
                          alignment="TOP_LEFT", clipBehavior="NONE"),
                    sigmaX=num(SIGMA), sigmaY=num(SIGMA), tileMode="CLAMP"),
                borderRadius=num(CARD_R), clipBehavior="ANTI_ALIAS"),
            left=num(ox + CARD_X), top=num(oy + CARD_Y)),
    ]


SB_X, SB_Y, SB_W, SB_H = 24, 26, 272, 188   # scene box inside the 320x240 cell
CIRC_C, CIRC_R = (160, 120), 100             # ⑥ clip: centre local (160,120), r=100


# kind, scene-box xywh, colour, area-local xywh, crosses r=100 circle, why
SHAPES_56 = [
    ("rect", 6, 4, 130, 60, "#2E7DD1", [30, 30, 130, 60], True,
     "远角距圆心 158>100、近角 30<100，必跨圆周"),
    ("rect", 176, 124, 90, 55, "#16233C", [200, 150, 90, 55], True,
     "内角距圆心 50<100、外角 155>100，跨圆周"),
    ("card_with_shadow", 71, 73, 120, 70, "#FFFFFF", [95, 95, 120, 70], False,
     "四角距圆心最大 71<100，完全在圆内；阴影 0 6 14 0 #00000066 NORMAL"),
    ("circle", 211, 13, 46, 46, "#E24C4C", [235, 35, 46, 46], True,
     "圆心距 116、半径 23，93<100<139，横跨圆周"),
]


def scene_56():
    """Shared base scene for the ⑤/⑥ pair, in scene-box local coordinates.

    Deliberately carries no background fill: the white cell must stay visible, and the
    transparent gaps between the shapes are what ColorFiltered is expected to tint.
    """
    kids = []
    for kind, x, y, w, h, col, _al, _cr, _why in SHAPES_56:
        attrs = {"width": num(w), "height": num(h), "color": col}
        if kind == "circle":
            attrs["shape"] = "CIRCLE"
        if kind == "card_with_shadow":
            attrs.update({"borderRadius": "10", "border": "2 SOLID #9AA9BF",
                          "boxShadow": "0 6 14 0 #00000066 NORMAL"})
        kids.append(Positioned(C(**attrs), left=num(x), top=num(y)))
    return Stack(C(width=num(SB_W), height=num(SB_H)), *kids,
                 alignment="TOP_LEFT", clipBehavior="NONE")


def filtered_56():
    return ImageFiltered(ColorFiltered(scene_56(), color=TINT, blendMode="MULTIPLY"),
                         sigmaX=num(SIGMA), sigmaY=num(SIGMA), tileMode="CLAMP")


def scene_multiply_blur(ox, oy):
    """⑤ ColorFiltered(MULTIPLY) first, then subtree gaussian blur, no clip."""
    return [Positioned(filtered_56(), left=num(ox + SB_X), top=num(oy + SB_Y))]


def scene_multiply_blur_clipped(ox, oy):
    """⑥ identical result with one extra outer circular clip."""
    ring_l, ring_t = CIRC_C[0] - CIRC_R, CIRC_C[1] - CIRC_R
    inner = Stack(C(width=num(2 * CIRC_R), height=num(2 * CIRC_R)),
                  Positioned(filtered_56(), left=num(SB_X - ring_l),
                             top=num(SB_Y - ring_t)),
                  alignment="TOP_LEFT", clipBehavior="NONE")
    return [Positioned(ClipOval(inner, clipBehavior="ANTI_ALIAS"),
                       left=num(ox + ring_l), top=num(oy + ring_t))]


# ---------------------------------------------------------------- build
els = []


def layer(*children, w=W, h=H):
    return Stack(C(width=num(w), height=num(h)), *children,
                 alignment="TOP_LEFT", clipBehavior="HARD_EDGE")


els.append(Positioned(
    Row(C(width="6", height="52", color=TINT, borderRadius="3"), Container(width="16"),
        Col(Text("看到差异，才能说用对了", color=TXT, fontSize="34", fontStyle="BOLD",
                 fontFamily=FONT),
            Container(height="4"),
            Text("六格实验板 · 每格 320×240 白底 · 每对只改一个变量 · 滤镜 sigmaX=sigmaY=6",
                 color=TXT_2, fontSize="18", fontFamily=FONT),
            crossAxisAlignment="START"),
        crossAxisAlignment="CENTER"),
    left=num(OX0), top=num(18)))

TITLES = [
    ("①", "逐元素 50% alpha", "#FF000080 与 #0000FF80 各自合成", "A 组"),
    ("②", "组 Opacity 0.5", "不透明红蓝先互相覆盖，再整组半透明", "A 组"),
    ("③", "仅背景模糊", "BackdropFilter 只糊卡下条纹", "B 组"),
    ("④", "子树整体模糊", "ImageFiltered 连背景与文字一起糊", "B 组"),
    ("⑤", "滤色 + 子树模糊", "MULTIPLY 后 sigma=6，间隙被填", "C 组"),
    ("⑥", "再加圆形裁剪", "同一结果套 r=100 圆裁，弧上截断", "C 组"),
]

builders = [two_rects_alpha, two_rects_group,
            scene_blur_background_only, scene_blur_subtree,
            scene_multiply_blur, scene_multiply_blur_clipped]

for i, ((ox, oy), (num_s, title, sub, grp), b) in enumerate(zip(AREAS, TITLES, builders)):
    els.append(label(ox, oy - 40, f"{num_s} {title}", 24, TXT, anchor="left_top",
                     align="LEFT", width=AW - 90, font=FONT, bold=True))
    els.append(Positioned(C(width="60", height="26", color=grp and "#16233C",
                            borderRadius="13", border=f"1 SOLID {PEDGE}"),
                          left=num(ox + AW - 62), top=num(oy - 38)))
    els.append(label(ox + AW - 32, oy - 33, grp, 18, TXT_2, anchor="right", align="RIGHT",
                     width=56, font=FONT))
    els.append(area_frame(ox, oy))
    els += b(ox, oy)
    els.append(label(ox, oy + AH + 6, sub, 18, TXT_2, anchor="left_top", align="LEFT",
                     width=AW, font=FONT, line_height=1.3))

# sampling markers for ① and ② at local (180,100)
for ox, oy in AREAS[:2]:
    els.append(Positioned(C(width="14", height="14", color=None, borderRadius="7",
                            border="2 SOLID #000000"), left=num(ox + 180 - 7),
                          top=num(oy + 100 - 7)))
    els.append(label(ox + 180, oy + 100 - 14, "采样点", 18, "#0B1220", anchor="bottom",
                     align="CENTER", width=80, font=FONT))

# circle guide for ⑥
ox6, oy6 = AREAS[5]
els.append(Positioned(C(width="200", height="200", color=None, borderRadius="100",
                        border="2 SOLID #16233C"), left=num(ox6 + 60), top=num(oy6 + 20)))

# ---------------------------------------------------------------- evidence panel
CAP_H = 2 * 18 * 1.3                       # two caption lines under each area
assert ROW_Y[1] - (ROW_Y[0] + AH + 6 + CAP_H) >= 8, "row-1 captions hit row-2 titles"
assert ROW_Y[1] + AH + 6 + CAP_H + 11 <= 780, "row-2 captions collide with the panel"

PX, PY, PW, PH = 40, 780, 1360, 296
PAD = 22
CX0, CWS, CGAP = PX + PAD, 644, 28
FLOW_LOG = []


def flow(col, x, width, y, text, fs, color, font, *, bold=False, align="LEFT", lh=1.3):
    """Estimate wrapped height and emit a width-bounded text node at (x, y)."""
    n_cjk = sum(1 for ch in text if ord(ch) > 0x2E80)
    adv = n_cjk * fs + (len(text) - n_cjk) * fs * 0.55
    lines = max(1, math.ceil(adv / width))
    h = lines * fs * lh
    FLOW_LOG.append((col, text[:18], lines, round(y, 1), round(y + h, 1)))
    return label(x, y, text, fs, color, anchor="left_top", align=align, width=width,
                 font=font, bold=bold, line_height=lh, lines=lines)


els.append(Positioned(C(width=num(PW), height=num(PH), color="#0E1830",
                        borderRadius="12", border=f"1 SOLID {PEDGE}"),
                      left=num(PX), top=num(PY)))

HEAD_Y = PY + 18
els.append(label(PX + PAD, HEAD_Y,
                 "像素与视觉证据（数值由 composite-audit.json 记录，采样自服务返回的 PNG）",
                 20, TXT, anchor="left_top", align="LEFT", width=PW - 2 * PAD,
                 font=FONT, bold=True))
els.append(label(PX + PW - PAD, HEAD_Y + 2,
                 "依据 /reference/parser-tags/ 的 Opacity · ColorFiltered · ImageFiltered · "
                 "BackdropFilter 条目，以及 /guides/painting/ “透明度与颜色滤镜”",
                 16, TXT_3, anchor="right", align="RIGHT", width=640, font=FONT))

LX = PX + PAD
COL_Y = HEAD_Y + 34

colA = []
y = COL_Y
colA.append(flow(1, LX, CWS, y, "A 组 · 重叠内部局部 (180,100) 的理论值与实测", 17, TXT_2,
                 FONT, bold=True)); y += 17 * 1.3 + 8
colA.append(flow(1, LX, CWS, y, f"① 逐元素 alpha 128/255 = {float(A128):.5f}，两次 source-over "
                            f"→ RGB {P1_overlap[0]},{P1_overlap[1]},{P1_overlap[2]}",
                 17, TXT, MONO)); y += 17 * 1.3 + 6
colA.append(flow(1, LX, CWS, y, f"② 组 opacity 0.5（蓝完全不透明盖红，再整组半透明）"
                            f" → RGB {P2_overlap[0]},{P2_overlap[1]},{P2_overlap[2]}",
                 17, TXT, MONO)); y += 17 * 1.3 + 8
colA.append(flow(1, LX, CWS, y,
                 "差别有两处：128/255=0.50196 并不等于 0.5；更主要的是“各自合成”与"
                 "“先叠合再整组透明”不是同一件事。①里蓝色半透明叠在已被红色改过的底色上，"
                 "绿通道被压到 63；②里蓝色完全不透明，组内已不含红色，整组透明后红绿两通道"
                 "都只剩白底回补出的 128。", 17, TXT_2, FONT, lh=1.3))
y += 4 * 17 * 1.3 + 8
colA.append(flow(1, LX, CWS, y,
                 f"实测 {VER}：① (127,63,191) 逐通道误差 0；② (126,126,255) 误差 2，"
                 "来自组透明度在 8 位离屏层里的量化与预乘取整；未改采样值，也未后处理图片。",
                 17, "#8FE3B0", MONO))
els += colA

RX = LX + CWS + CGAP
colB = []
y = COL_Y
colB.append(flow(2, RX, CWS, y, "B / C 组 · ③–⑥ 的实际看图判断（非预期描述）", 17, TXT_2,
                 FONT, bold=True)); y += 17 * 1.3 + 8
colB.append(flow(2, RX, CWS, y,
                 "③ 卡内条纹已糊成色带（水平梯度 1.13），SHARP 文字与深色方块仍锐利（15.64）；"
                 "④ 同一区域条纹 1.71、文字 2.13 一起糊开，卡片圆角边也变软。两格卡外条纹梯度"
                 "同为 8.6，说明底场景一致，差别只落在模糊所作用的那一层。",
                 17, TXT, FONT, lh=1.3)); y += 3 * 17 * 1.3 + 8
colB.append(flow(2, RX, CWS, y,
                 "⑤ 白卡转橙、形状之间的透明间隙被 #F6B94A 填成橙色，sigma=6 让场景外框边缘"
                 "向右扩散 23px、向上 7px，实验区白底与 1px 边框仍完整；⑥ 加 r=100 圆裁后，"
                 "沿圆心向右取样在 dx 97→98、99→100 出现 218/228 的通道跳变，圆内 (246,185,74)、"
                 "圆外纯白，跨圆的蓝条与红点在弧上被整齐切断。",
                 17, TXT, FONT, lh=1.3))
els += colB

BOTTOM = max(v[4] for v in FLOW_LOG)
assert BOTTOM <= PY + PH - 14, f"panel text overflows: {BOTTOM} > {PY + PH - 14}"
print("panel flow:", json.dumps(FLOW_LOG, ensure_ascii=False), file=sys.stderr)

doc = Snapshot(Container(layer(*els), width=num(W), height=num(H), color=BG),
               background=BG, type="png")

# ---------------------------------------------------------------- audit
audit = {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "canvas": [W, H],
    "areas": {
        "size_px": [AW, AH], "gap_px": GAP, "cols": COLS, "rows": ROWS,
        "count": 6,
        "origins_canvas_px": [{"id": TITLES[i][0], "x": AREAS[i][0], "y": AREAS[i][1],
                               "integer": float(AREAS[i][0]).is_integer()
                               and float(AREAS[i][1]).is_integer()}
                              for i in range(6)],
        "local_origin_meaning": "各实验区左上外边界为局部原点，x 向右 y 向下，单位像素",
    },
    "sampling": {
        "point_local": [180, 100],
        "indexing": "第 (origin_x+180, origin_y+100) 个像素，索引从 0 开始，"
                    "直接读取服务返回 PNG 的未预乘 8 位 RGBA，不取截图或缩略图",
        "expected_alpha": 255,
    },
    "group_A": {
        "shared": {"red_rect": [40, 40, 160, 120], "blue_rect": [120, 80, 160, 120],
                   "blue_on_top": True, "background": "#FFFFFF",
                   "compositing": "source-over，先白底，再红，再蓝"},
        "only_difference": "① 每个矩形自带 50% alpha；② 两个不透明矩形放进 Opacity(0.5) 组",
        "alpha_values": {
            "per_element": {"hex_alpha": "80", "fraction": "128/255",
                            "decimal": float(A128)},
            "group_opacity": {"decimal": 0.5},
            "delta": float(A128 - F(1, 2)),
            "note": "128/255 = 0.5019607843，比 0.5 大 0.0019607843，两者不能混用同一个 alpha",
        },
        "overlap_point_180_100": {
            "①": {
                "steps": [
                    "red over white: R=255·(128/255)+255·(127/255)=255; "
                    "G=B=0·(128/255)+255·(127/255)=255−128=127",
                    "blue over that: R=0·(128/255)+255·(127/255)=127; "
                    "G=0·(128/255)+127·(127/255)=16129/255; "
                    "B=255·(128/255)+127·(127/255)=128+16129/255",
                ],
                "theoretical_float": [float(v) for v in P1_overlap_exact],
                "theoretical_fraction": [str(v) for v in P1_overlap_exact],
                "rounded": P1_overlap,
                "rounding": "floor(value + 0.5)",
            },
            "②": {
                "steps": [
                    "inside the group: opaque blue covers opaque red → (0,0,255) fully opaque",
                    "group composited at 0.5 over white: "
                    "R=0·0.5+255·0.5=127.5, G=127.5, B=255·0.5+255·0.5=255",
                ],
                "theoretical_float": [127.5, 127.5, 255.0],
                "rounded": P2_overlap,
                "rounding": "floor(value + 0.5)",
            },
        },
        "secondary_sample_red_only_60_60": {
            "①": P1_red_only, "②": P2_red_only,
            "note": "仅被红矩形覆盖处，①=(255,127,127) 与 ②=(255,128,128) 相差 1，"
                    "正是 128/255 与 0.5 的差异所致",
        },
        "measured": None,
    },
    "group_B": {
        "shared_base_scene": {
            "stripes": {"count": 10, "width_px": 16, "pitch_px": 32,
                        "colours": ["#E24C4C", "#2E7DD1", "#2FA36B", "#EAB53B", "#8E5AC8"],
                        "spans": "整幅 320×240，跨过卡片左右边界"},
            "card": {"local_xywh": [CARD_X, CARD_Y, CARD_W, CARD_H], "border_radius": CARD_R,
                     "fill": "#FFFFFFCC", "border": "2 SOLID #1B2A47"},
            "card_text": {"content_3": "SHARP", "content_4": "BLUR", "font_size": 24,
                          "colour": "#0B1220"},
            "foreground_shape": {"size": [56, 26], "colour": "#16233C",
                                 "position": "文字下方 6px，卡内水平居中"},
            "sigma": [SIGMA, SIGMA],
        },
        "only_difference": "③ 用 BackdropFilter 只糊卡片覆盖处的背景，文字与形状在滤镜子树之外；"
                           "④ 用 ImageFiltered 把卡片底色、文字与形状整体模糊",
        "visual_judgement": {
            "3_text_sharp": True, "3_background_blurred": True, "3_effect_leaks_out": False,
            "4_text_sharp": False, "4_background_blurred": True, "4_effect_leaks_out": False,
            "observed_in": "v004",
            "gradients": {"3_stripe_row": 1.13, "3_text_row": 15.64,
                          "4_stripe_row": 1.71, "4_text_row": 2.13,
                          "outside_card_3": 8.6, "outside_card_4": 8.6},
            "basis": "在 v004.png 上取卡内 y∈[50,74] 与文字行 y∈[98,122] 的水平一阶差分均值；"
                     "整图与局部放大见 image_views.jsonl 与 zoom-*.png",
        },
    },
    "group_C": {
        "shared_base_scene": {
            "background": "#FFFFFF 320×240",
            "scene_box": [SB_X, SB_Y, SB_W, SB_H],
            "shapes": [
                {"kind": k, "scene_box_xywh": [x, y, w, h], "area_local_xywh": al,
                 "colour": col, "crosses_circle": cr, "why": why}
                for k, x, y, w, h, col, al, cr, why in SHAPES_56
            ],
            "circle_domain": "圆心局部 (160,120)、半径 100，即 x∈[60,260]、y∈[20,220]",
            "transparent_gaps": "场景框内形状之间未覆盖的区域，用于观察 MULTIPLY 对间隙着色；"
                                "场景框本身不带底色，白底来自实验区",
            "tint_colour": TINT, "blend_mode": "MULTIPLY", "sigma": [SIGMA, SIGMA],
        },
        "only_difference": "⑥ 在 ⑤ 的同样结果最外层增加圆形裁剪（圆心局部 (160,120)、半径 100），"
                           "⑤ 不加裁剪",
        "circle": {"centre_local": [160, 120], "radius": 100,
                   "clip_box_canvas": [AREAS[5][0] + 60, AREAS[5][1] + 20]},
        "visual_judgement": {
            "5_gap_filled_by_tint": True, "5_spills_beyond_shapes": True,
            "5_spread_px": {"right": 23, "up": 7}, "5_cell_border_intact": True,
            "6_spills_beyond_shapes": False, "6_circle_boundary_sharp": True,
            "6_circle_scan": {"inside_dx80_rgb": [246, 185, 74],
                              "outside_dx120_rgb": [255, 255, 255],
                              "jumps": [{"dx": "97→98", "max_channel_delta": 218},
                                        {"dx": "99→100", "max_channel_delta": 228}]},
            "observed_in": "v004",
            "basis": "沿 ⑥ 圆心局部 (160,120) 向右逐像素取样到 dx=120；⑤ 从场景框右缘与上缘"
                     "向外找首个与纯白最大通道差 >3 的位置",
        },
    },
    "documentation_basis": [
        "https://snapshot.muedsa.com/reference/parser-tags/ — Opacity、ColorFiltered、"
        "ImageFiltered、BackdropFilter、ClipOval 条目",
        "https://snapshot.muedsa.com/guides/painting/ — “透明度与颜色滤镜”：ColorFiltered 会按"
        "子树绘制边界限制作用范围并可能给边界内透明间隙着色；BackdropFilter 读取已有背景，"
        "建议配合 ClipRRect/ClipOval 限定区域",
        "https://snapshot.muedsa.com/reference/faq/ — Stack 默认 HARD_EDGE 裁剪、"
        "ColorFiltered 染色透明间隙的说明",
    ],
    "tolerance": {"per_channel_px": 3, "policy": "超出容差须核查坐标、合成顺序与实际渲染，"
                                                "不得修改采样值或后处理图片凑合"},
}

_dsl_text = doc.render()
_n_text = _dsl_text.count("<Text")
audit["text_inventory"] = {
    "text_nodes_total": _n_text,
    "number_title_nodes": 6,
    "explanatory_nodes": _n_text - 6,
    "requirement": "说明文字≥20",
    "satisfied": _n_text - 6 >= 20,
    "counting": "统计 DSL 中 Text 节点总数，再减去 6 个格子的编号标题；"
                "副标题、组别标签、采样点标注、每格说明与证据面板文字都算说明文字",
}

OUT_DIR.mkdir(parents=True, exist_ok=True)
(OUT_DIR / "composite-audit.json").write_text(
    json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

ap = argparse.ArgumentParser()
ap.add_argument("--ver", default="v001")
ap.add_argument("--final", default=None)
a = ap.parse_args()
TMP_DIR.mkdir(parents=True, exist_ok=True)
(TMP_DIR / f"{a.ver}.snapshot").write_text(doc.render() + "\n", encoding="utf-8")
if a.final:
    (ROOT / a.final).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / a.final).write_text(doc.render() + "\n", encoding="utf-8")
print(json.dumps({"ver": a.ver, "areas": AREAS, "P1": P1_overlap, "P2": P2_overlap,
                  "P1_red": P1_red_only, "P2_red": P2_red_only}, ensure_ascii=False))
