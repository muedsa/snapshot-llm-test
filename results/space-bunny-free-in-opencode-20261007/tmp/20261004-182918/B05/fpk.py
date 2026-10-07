#!/usr/bin/env python
"""B05 · shared design kit — 房谱 HOMESPEC

Design language
---------------
One palette, one type scale, one rule.

The palette is derived from the product's own object: a survey anchor plate
(yellow/black hazard id tag on an off-white survey sheet) sitting on top of a
blueprint. So every screen has, somewhere, the same yellow-black anchor tag as
a literal object, and the same measured-blue rules as background structure.

The type scale is fixed: Inter for interface text, DejaVu Sans Mono for every
number that the product decides, Noto Sans CJK SC for Chinese, Noto Serif CJK
for the two narrative screens (05 report pull-quote, 08 share card).

Rule: a number the product *decided* (Δ mm, ¥, kWh, counts, dates) is mono and
ink-coloured. A number that is a *state* (pass/fail/暂挂) may carry a semantic
colour, and only those may.
"""
from __future__ import annotations

import math
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import dsllib as D  # noqa: E402

# ---------------------------------------------------------------- palette ---
INK       = "#141B26FF"   # primary ink, near-black blue
INK_2     = "#43536BFF"   # secondary text
INK_3     = "#8494A8FF"   # tertiary / axis / meta
INK_4     = "#B4C0CEFF"   # faintest rule-on-paper

PAPER     = "#F7F4EEFF"   # survey sheet / app paper background
PAPER_2   = "#FFFFFF"     # raised white card
PAPER_3   = "#EFEAE1FF"   # recessed slot
LINE      = "#DED7CBFF"   # hairline on paper
LINE_2    = "#CBC2B2FF"

BLUE      = "#1E4FD8FF"   # primary action / "unchanged" / structural
BLUE_DK   = "#14379BFF"
BLUE_LT   = "#D9E2FBFF"
BLUE_XLT  = "#EEF2FEFF"

YELLOW    = "#F5C518FF"   # THE anchor tag yellow
YELLOW_DK = "#C79A05FF"
YELLOW_LT = "#FDF3D0FF"

AMBER     = "#E08A0BFF"   # 暂挂 / cannot-compare
AMBER_LT  = "#FDF0D9FF"

RED       = "#D93B2BFF"   # 新增损伤 / failure
RED_DK    = "#A32B1EFF"
RED_LT    = "#FBE5E2FF"

GREEN     = "#1F8A5CFF"   # 已修复 / pass
GREEN_LT  = "#DDF0E6FF"

SLATE     = "#5A6B80FF"
NIGHT     = "#0E1622FF"   # phone/desktop chrome, watch body
NIGHT_2   = "#1A2635FF"
NIGHT_3   = "#2A3A4EFF"

# fonts (all confirmed against a live GET /fonts, saved at tmp/.../B05/fonts-list.txt)
DISPLAY = "Inter Black,Noto Sans CJK SC"
SEMI    = "Inter Semi Bold,Noto Sans CJK SC"
MED     = "Inter Medium,Noto Sans CJK SC"
UI      = D.UI
MONO    = D.MONO
SERIF   = "Noto Serif CJK SC"

APP      = "房谱"
APP_EN   = "HOMESPEC"
VERSION  = "2.4.1"

# ------------------------------------------------------------------ facts ---
# All fictional, all consistent across the 10 screens. See product-brief.md §6.
ADDR      = "云栖里 3 号楼 1602 室"
ADDR_S    = "云栖里 · 1602"
TENANT    = "林知远"
OWNER     = "陆文君"
FIXER     = "老周"

D_IN      = "2023-07-01"
D_OUT     = "2026-09-30"

ANCHORS = [
    ("A-01", "入户门内侧 · 合页侧",        "door",  "2023-07-01", "2026-09-30"),
    ("A-02", "入户门锁舌盒",                "door",  "2023-07-01", "2026-09-30"),
    ("A-03", "玄关地板 · 门口 400mm",       "floor", "2023-07-01", "—"),
    ("K-01", "厨房 · 水槽下左角",            "kitchen", "2023-07-01", "2026-09-30"),
    ("K-02", "厨房 · 龙头阀根",              "kitchen", "2023-07-01", "2026-09-30"),
    ("K-03", "厨房 · 橱柜挡板右段",          "kitchen", "2023-07-01", "2026-09-30"),
    ("B-01", "卫生间 · 马桶后墙角",          "bath",  "2023-07-01", "2026-09-30"),
    ("B-02", "卫生间 · 台盆下 U 型弯",       "bath",  "2023-07-01", "2026-09-30"),
    ("W-01", "主卧 · 飘窗窗台左端",          "bed",   "2023-07-01", "2026-09-30"),
    ("W-02", "主卧 · 空调出风口下墙",        "bed",   "2023-07-01", "2026-09-30"),
    ("E-01", "阳台 · 洗衣机进水口",          "balc",  "2023-07-01", "2026-09-30"),
    ("E-02", "阳台 · 排水地漏盖",            "balc",  "2023-07-01", "—"),
]

# 退租差分 — 10 comparable anchors, the 2 remaining were out of scope this round.
DIFF_ROWS = [
    # id, label, category, detail, delta_text, money, note
    ("K-01", "厨房 · 水槽下左角", "new",  "不锈钢水槽支架右后角 3 道划痕，深度判定 0.12mm",
     "新增", 120, "0.8mm 划痕 ×3 处"),
    ("W-02", "主卧 · 空调出风口下墙", "new", "出风口右下 2 个膨胀螺栓钉孔，直径 8mm，无渗水痕迹",
     "新增", 80, "钉孔 ×2，直径 8mm"),
    ("B-02", "卫生间 · 台盆下 U 型弯", "fixed", "2025-06 更换的 U 型弯与接头本次无渗水、无挂垢",
     "已修复", 0, "R-2506-042 已闭环"),
    ("K-02", "厨房 · 龙头阀根", "fixed", "2024-03 更换的陶瓷阀芯与垫片无渗水",
     "已修复", 0, "R-2403-118 已闭环"),
    ("A-01", "入户门内侧 · 合页侧", "same", "合页螺丝、门框漆面与 2023-07 一致",
     "未变化", 0, ""),
    ("A-02", "入户门锁舌盒", "same", "锁舌行程正常，无撬压痕",
     "未变化", 0, ""),
    ("B-01", "卫生间 · 马桶后墙角", "same", "墙砖釉面、硅胶收口无开裂、无霉斑",
     "未变化", 0, ""),
    ("W-01", "主卧 · 飘窗窗台左端", "same", "窗台漆面、密封胶条无变化",
     "未变化", 0, ""),
    ("E-01", "阳台 · 洗衣机进水口", "same", "角阀、手轮、进水软管接口无渗水",
     "未变化", 0, ""),
    ("E-02", "阳台 · 排水地漏盖", "hold", "返工拍摄时逆光过曝，未识别到 E-02 标记牌",
     "暂挂", 0, "重拍期限 10-07"),
]
CATS = {
    "new":   ("新增损伤", RED,   RED_LT,   "NEW"),
    "fixed": ("已修复",   GREEN, GREEN_LT, "FIXED"),
    "same":  ("未变化",   BLUE,  BLUE_LT,  "SAME"),
    "hold":  ("暂挂",     AMBER, AMBER_LT, "HOLD"),
}

REP_AIR = [("R-2403-118", "2024-03-09", "厨房 · 龙头阀根渗水", "更换陶瓷阀芯 + 垫片", "老周", 180, "闭环"),
           ("R-2506-042", "2025-06-21", "卫生间 · 台盆下返味", "更换 U 型弯 + 密封圈", "老周", 260, "闭环")]

KWH_IN, KWH_OUT = 1284, 3611

MOISTURE = [  # (month, 逐月渗水读数 %RH，含 2024-08 与 2025-08 两次维修后的下降)
    ("23-07", None), ("23-08", 71), ("23-09", 74), ("23-10", 69), ("23-11", 58), ("23-12", 55),
    ("24-01", 57), ("24-02", 61), ("24-03", 74), ("24-04", 66), ("24-05", 63), ("24-06", 60),
    ("24-07", 58), ("24-08", 55), ("24-09", 57), ("24-10", 53), ("24-11", 49), ("24-12", 47),
    ("25-01", 50), ("25-02", 55), ("25-03", 61), ("25-04", 57), ("25-05", 54), ("25-06", 68),
    ("25-07", 62), ("25-08", 59), ("25-09", 55), ("25-10", 50), ("25-11", 47), ("25-12", 45),
    ("26-01", 48), ("26-02", 53), ("26-03", 57), ("26-04", 54), ("26-05", 51), ("26-06", 49),
    ("26-07", 47), ("26-08", 45), ("26-09", 48),
]


# --------------------------------------------------------------- colour ------
def A(c: str, alpha: str) -> str:
    s = c.lstrip("#")
    assert len(s) in (3, 6, 8), c
    if len(s) == 3:
        s = "".join(ch * 2 for ch in s)
    return "#" + s[:6].upper() + str(alpha).upper()


def mix(a: str, b: str, t: float) -> str:
    t = max(0.0, min(1.0, t))
    def p(s):
        s = s.lstrip("#")
        if len(s) == 3:
            s = "".join(ch * 2 for ch in s)
        if len(s) == 6:
            s = s + "FF"
        return [int(s[i:i + 2], 16) for i in (0, 2, 4, 6)]
    ca, cb = p(a), p(b)
    return "#%02X%02X%02X%02X" % tuple(
        (max(ca[3], cb[3]) if i == 3 else int(round(ca[i] + (cb[i] - ca[i]) * t)))
        for i in range(4))


def alpha_mix(c: str, t: float) -> str:
    """Same hue, lighter surface — for fills behind ink."""
    return mix(c, "#FFFFFFFF", t)


def tmix(c: str, t: float) -> str:
    """Same hue, toward paper — for tracks behind a fill."""
    return mix(c, PAPER, t)


# ------------------------------------------------------------------ type ----
def h1(s, x, y, size=40, color=INK, ls=-0.5, font=None, w=None, align=None):
    return D.text_el(s, x=x, y=y, w=w, size=size, color=color,
                     font=font or DISPLAY, ls=ls, align=align)


def h2(s, x, y, size=24, color=INK, ls=-0.2, font=None, w=None, align=None):
    return D.text_el(s, x=x, y=y, w=w, size=size, color=color,
                     font=font or SEMI, ls=ls, align=align)


def body(s, x, y, w, size=16, color=INK_2, ls=0.1, lh=1.55, font=None,
         align=None, style=None):
    return D.text_el(s, x=x, y=y, w=w, size=size, color=color,
                     font=font or UI, ls=ls, align=align, style=style,
                     h=size * lh * D.est_lines(s, size, w) + 6)


def mono(s, x, y, size=16, color=INK, w=None, align=None, style=None, wrap=None,
         ls=None):
    return D.text_el(s, x=x, y=y, w=w, size=size, color=color, font=MONO,
                     align=align, style=style, wrap=wrap, ls=ls)


def mono_w(s, size):
    """DejaVu Sans Mono advance = 0.602em (measured in B04 case-03)."""
    return len(s) * size * 0.602


def kicker(s, x, y, size=11, color=BLUE, ls=2.2, w=None, align=None):
    return D.text_el(s, x=x, y=y, w=w, size=size, color=color, font=MONO,
                     ls=ls, style="BOLD", align=align)


def tag(s, x, y, color=BLUE, size=11, padx=9, padh=5, fill=None, border=True,
        font=None, h=None):
    tw = D.est_width(s, size, )
    tw = D.est_width(s, size)
    w = tw + padx * 2
    hh = h or size * 1.7
    b = ("1 SOLID " + A(color, "55")) if border else None
    return "\n".join([
        D.box(x, y, w, hh, color=fill if fill else A(color, "18"), radius=hh / 2,
              border=b),
        D.text_el(s, x=x + padx, y=y + (hh - size * 1.2) / 2, size=size,
                  color=color, font=font or UI, ls=0.6, style="BOLD"),
    ]), w


def tag_w(s, size=11, padx=9):
    return D.est_width(s, size) + padx * 2


# ----------------------------------------------------------------- shapes ---
def circle(cx, cy, r, color=None, *, border=None, bw=2):
    s = round(2 * r, 2)
    a = {"width": s, "height": s, "shape": "CIRCLE"}
    if color:
        a["color"] = color
    if border:
        a["border"] = "%d SOLID %s" % (int(bw) if float(bw) >= 1 else 1, border)
    return D.el("Positioned", {"left": round(cx - r, 2), "top": round(cy - r, 2),
                               "width": s, "height": s},
                [D.el("Container", a, None)])


def ring(cx, cy, r, color, width=2):
    return circle(cx, cy, r, None, border=color, bw=width)


def dot(cx, cy, r, color, ring_c=None, ring_w=2):
    out = []
    if ring_c:
        out.append(circle(cx, cy, r + ring_w + 1.5, A(ring_c, "2E"), border=ring_c,
                          bw=ring_w))
    out.append(circle(cx, cy, r, color))
    return "\n".join(out)


def seg(x0, y0, x1, y1, color, w=3):
    """One rotated rectangle spanning (x0,y0)-(x1,y1). Rotates about box centre."""
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    if L < 0.4:
        return ""
    ang = math.atan2(dy, dx)
    pad = w * 0.9
    bw, bh = L + pad * 2, w
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    m = "(%.5f,%.5f,0,0,%.5f,%.5f,0,0,0,0,1,0,0,0,0,1)" % (
        math.cos(ang), math.sin(ang), -math.sin(ang), math.cos(ang))
    inner = D.el("Container", {"width": round(bw, 2), "height": round(bh, 2),
                               "color": color}, None)
    tf = D.el("Transform", {"matrix": m, "origin": "(0,0)",
                            "alignment": "CENTER"}, [inner])
    return D.el("Positioned", {"left": round(cx - bw / 2.0, 2),
                               "top": round(cy - bh / 2.0, 2),
                               "width": round(bw, 2), "height": round(bh, 2)}, [tf])


def polyline(pts, color, w=3, close=False, cap=None):
    out = []
    seq = list(pts) + ([pts[0]] if close and len(pts) > 2 else [])
    for i in range(len(seq) - 1):
        (x0, y0), (x1, y1) = seq[i], seq[i + 1]
        if i == 0 and cap:
            out.append(circle(x0, y0, cap, color))
        p = seg(x0, y0, x1, y1, color, w)
        if p:
            out.append(p)
    return "\n".join([o for o in out if o])


def arrow(x0, y0, x1, y1, color, w=2, head=9):
    ang = math.atan2(y1 - y0, x1 - x0)
    bx, by = x1 - head * .92 * math.cos(ang), y1 - head * .92 * math.sin(ang)
    return "\n".join([
        seg(x0, y0, bx, by, color, w),
        polyline([(x1, y1),
                  (x1 - head * math.cos(ang - .42), y1 - head * math.sin(ang - .42)),
                  (x1 - head * math.cos(ang + .42), y1 - head * math.sin(ang + .42))],
                 color, w, close=True)])


def triangle(pts, color):
    return D.polygon(pts, color)


def _scan(pts, y):
    xs = []
    n = len(pts)
    for i in range(n):
        (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % n]
        if (y1 <= y < y2) or (y2 <= y < y1):
            xs.append(x1 + (y - y1) / (y2 - y1) * (x2 - x1))
    if len(xs) < 2:
        return None
    return min(xs), max(xs)


def area(pts, y_base, color, rows=60):
    """Closed scanline fill. Snap rows to ints so translucent bands don't double."""
    if not pts:
        return ""
    closed = list(pts) + [(pts[-1][0], y_base), (pts[0][0], y_base)]
    ytop = min(min(p[1] for p in pts), y_base)
    span = max(1.0, y_base - ytop)
    out = []
    for i in range(rows):
        ya = int(round(ytop + span * i / rows))
        yb = int(round(ytop + span * (i + 1) / rows))
        if yb <= ya:
            continue
        xs = _scan(closed, (ya + yb) / 2.0)
        if xs is None:
            continue
        out.append(D.box(xs[0], ya, xs[1] - xs[0], yb - ya, color=color))
    return "\n".join(out)


def gradient_v(x, y, w, h, top, bottom, steps=48):
    out = []
    for i in range(steps):
        yy = y + h * i / steps
        out.append(D.box(x, yy, w, h / steps + 1.0, color=mix(top, bottom, i / (steps - 1.0))))
    return "\n".join(out)


def grain(w, h, step=17, alpha="07", count=None, seed=20261005, color="#FFFFFF"):
    out = []
    n = count if count else int(w * h / (step * step * 60))
    for _ in range(n):
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        x = seed % w
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        y = seed % h
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        s = 1 + (seed % 2)
        out.append(D.box(x, y, s, s, color=A(color, alpha)))
    return "\n".join(out)


def blueprint(w, h, step=40, color=None, alpha="0C"):
    """Faint measured grid; `color=None` -> INK_4 derived faint rule."""
    c = color or LINE
    out = []
    x = step
    while x < w:
        out.append(D.box(x, 0, 1, h, color=A(c, alpha)))
        x += step
    y = step
    while y < h:
        out.append(D.box(0, y, w, 1, color=A(c, alpha)))
        y += step
    return out


# -------------------------------------------------------------- surfaces ----
def panel(x, y, w, h, *, fill=PAPER_2, border=LINE, radius=12, shadow=None,
          bw=1):
    return D.box(x, y, w, h, color=fill, radius=radius,
                 border="%d SOLID %s" % (bw, border) if border else None,
                 shadow=shadow)


def slot(x, y, w, h, *, fill=PAPER_3, radius=10, border=None):
    return D.box(x, y, w, h, color=fill, radius=radius,
                 border="1 SOLID %s" % border if border else None)


def clipped(x, y, w, h, children, *, radius=0, fill=None, border=None, shadow=None):
    """ClipRRect > Container > Stack > children.

    Measured: `Container` accepts exactly ONE child, so a multi-child region has
    to be wrapped in a Stack. Without this the service answers
    400 PARSE_ERROR "Tag Container only can have one child".
    """
    clip_a = {"width": round(w, 2), "height": round(h, 2)}
    if radius:
        clip_a["borderRadius"] = round(radius, 2)
    if border:
        clip_a["border"] = border
    core = dict(clip_a)
    if fill:
        core["color"] = fill
    if shadow:
        core["boxShadow"] = shadow
    inner = el_stack(children, w, h)
    return D.el("Positioned", {"left": round(x, 2), "top": round(y, 2),
                               "width": round(w, 2), "height": round(h, 2)},
                [D.el("ClipRRect", clip_a, [D.el("Container", core, [inner])])])


def faded(x, y, w, h, children, opacity, *, radius=0, clip=False):
    """Positioned > Opacity > (ClipRRect >) Container > Stack > children.

    Measured: `opacity` is NOT a Container attribute — the parser ignores unknown
    attributes, so `opacity="0.1"` on a box paints it fully opaque (seen in
    case-01 v1: the detection tint covered the anchor plate). Opacity is a tag
    and it takes a single child, hence the inner Stack.
    """
    stack_ = el_stack(children, w, h)
    if clip:
        inner = D.el("ClipRRect", {"width": round(w, 2), "height": round(h, 2),
                                   "borderRadius": round(radius, 2)}, [stack_])
    else:
        inner = stack_
    return D.el("Positioned", {"left": round(x, 2), "top": round(y, 2),
                               "width": round(w, 2), "height": round(h, 2)},
                [D.el("Opacity", {"opacity": round(opacity, 4)}, [inner])])


def el_stack(children, w, h):
    lst = []
    for c in children:
        if isinstance(c, list):
            lst.extend(c)
        else:
            lst.append(c)
    return D.el("Stack", {"fit": "EXPAND"}, lst)


def button(x, y, w, h, label, *, fill=BLUE, fg="#FFFFFF", size=16, radius=10,
           sub=None, font=None):
    out = [D.box(x, y, w, h, color=fill, radius=radius)]
    cy = y + (h - (size * 1.2 + (sub and 20 or 0))) / 2
    out.append(D.text_el(label, x=x + 16, y=cy, w=w - 32, size=size, color=fg,
                         font=font or SEMI, align="CENTER", ls=0.2))
    if sub:
        out.append(D.text_el(sub, x=x + 16, y=cy + size * 1.35, w=w - 32,
                             size=size * 0.72, color=A("#FFFFFF", "B8"),
                             font=UI, align="CENTER"))
    return "\n".join(out)


def btn_w(label, size=16):
    return D.est_width(label, size) + 32


def row_item(x, y, w, h, *, fill=PAPER_2, radius=12, border=LINE, accent=None,
             accent_w=4):
    out = []
    if accent:
        out.append(D.box(x, y, accent_w, h, color=accent,
                         radii={"TopLeft": radius, "BottomLeft": radius}))
    out.append(D.box(x, y, w, h, color=fill, radius=radius,
                     border="1 SOLID %s" % border))
    return "\n".join(out)


def icon_tile(x, y, s, glyph, color, *, fill=None, radius=10, gs=15):
    return "\n".join([
        D.box(x, y, s, s, color=fill or A(color, "16"), radius=radius),
        D.text_el(glyph, x=x, y=y + (s - gs * 1.2) / 2, w=s, size=gs, color=color,
                  font=SEMI, align="CENTER"),
    ])


def toggle(x, y, w=52, h=30, on=True, on_c=GREEN, off_c=INK_4):
    c = on_c if on else off_c
    return "\n".join([
        D.box(x, y, w, h, color=c, radius=h / 2),
        D.box(x + (w - h + 4 if on else 4), y + 4, h - 8, h - 8,
              color="#FFFFFFFF", radius=(h - 8) / 2),
    ])


def check(x, y, s=18, color=BLUE, *, w=2):
    """Tick mark as two rotated segments."""
    return polyline([(x + s * .16, y + s * .52), (x + s * .40, y + s * .76),
                     (x + s * .84, y + s * .24)], color, w)


def cross(x, y, s=18, color=RED, *, w=2.4):
    return "\n".join([seg(x + s * .18, y + s * .18, x + s * .82, y + s * .82, color, w),
                      seg(x + s * .82, y + s * .18, x + s * .18, y + s * .82, color, w)])


def anchor_tag(x, y, w, h, code, *, label=None, scale=1.0):
    """The literal product object: a hazard id plate.

    Real geometry: rounded yellow plate, black border, two black corner blocks,
    the anchor code in heavy mono, and a small hazard stripe strip. This object
    appears at a different physical scale in almost every screen, so it is the
    one component the whole identity hangs on.
    """
    out = [D.box(x, y, w, h, color=YELLOW, radius=4 * scale,
                 border="%d SOLID #14181FFF" % max(1, int(2.4 * scale)))]
    has_label = bool(label) and h >= 26 * scale
    cs = (min(h * (.52 if has_label else .66), w * .34)) * scale
    cy = y + (h * .40 if has_label else h / 2) - cs * .62
    out.append(D.text_el(code, x=x + w * .07, y=cy, w=w * .86,
                         size=cs, color="#14181FFF", font=DISPLAY,
                         ls=-cs * .04, wrap=False))
    if has_label:
        # Measured: a label narrower than its mono advance silently wraps and the
        # overflow lands OUTSIDE the plate (case-01 v5). So size it from the real
        # 0.602em advance and turn wrapping off.
        ls_ = min(h * .21, (w * .86) / (len(label) * 0.602), 11 * scale)
        out.append(D.text_el(label, x=x + w * .07, y=y + h - ls_ * 1.45,
                             w=w * .86, size=ls_, color=A("#14181F", "B8"),
                             font=MONO, ls=0.2, wrap=False))
    # corner blocks
    b = max(2.0, 5 * scale)
    out.append(D.box(x + 2.5 * scale, y + 2.5 * scale, b, b, color="#14181FFF"))
    out.append(D.box(x + w - 2.5 * scale - b, y + h - 2.5 * scale - b, b, b,
                     color="#14181FFF"))
    return "\n".join(out)


def hazard_stripe(x, y, w, h, *, c1=YELLOW, c2="#14181FFF", pitch=None,
                  thickness=0.5):
    """Diagonal hazard stripes inside a band of exactly (w,h).

    Measured: a rotated bar's vertical extent is about
    (length + thickness) / sqrt(2), so bars sized for a 16px band actually paint
    ~58px and swamp the copy above them (case-03 v2). Building them oversized
    and letting a ClipRRect cut them back is the reliable way.
    """
    p = pitch or max(10.0, h * 1.4)
    bars = []
    n = int(w / p) + int(h / p) + 3
    for i in range(-n, n + 1):
        bx = i * p
        bars.append(seg(bx, h, bx + h, 0, c2, w=p * thickness))
    return clipped(x, y, w, h, [D.box(0, 0, w, h, color=c1)] + bars, radius=0)


# ------------------------------------------------------------- text wrap ----
def wrap_cjk(s, w, size=11):
    out, cur, curw, i = [], "", 0.0, 0
    while i < len(s):
        ch = s[i]
        if ord(ch) > 0x2E80:
            tok, tokw = ch, size
            i += 1
        else:
            j = i
            while j < len(s) and ord(s[j]) <= 0x2E80 and s[j] != " ":
                j += 1
            tok = s[i:j] + " "
            tokw = D.est_width(tok, size)
            i = j + 1
        if curw + tokw > w and cur:
            out.append(cur.rstrip())
            cur, curw = "", 0.0
        cur += tok
        curw += tokw
    if cur.strip():
        out.append(cur.rstrip())
    return out or [""]


def para(s, x, y, w, *, size=13, color=INK_2, lh=1.55, align=None, font=None):
    lines = wrap_cjk(s, w, size)
    out = []
    yy = y
    for ln in lines:
        out.append(D.text_el(ln, x=x, y=yy, w=w, size=size, color=color,
                             font=font or UI, align=align))
        yy += size * lh
    return "\n".join(out), yy


def lines_h(n, size=13, lh=1.55):
    return n * size * lh


# --------------------------------------------------------------- charts -----
def hline(x0, x1, y, color=LINE, w=1):
    return D.hline(x0, x1, y, color, w)


def vline(x, y0, y1, color=LINE, w=1):
    return D.vline(x, y0, y1, color, w)


def rule(x0, x1, y, color=LINE, w=1):
    return D.hline(x0, x1, y, color, w)


def bars(values, x0, y_base, scale, *, color=BLUE, gap=8, radius=3, width=None,
         colors=None):
    out, xs = [], []
    n = len(values)
    w = width or ((max(x for x, *_ in values) - x0) / n if values and isinstance(values[0], (list, tuple)) else 20)
    xx = x0
    for i, v in enumerate(values):
        h = max(1.0, v * scale)
        c = colors[i] if colors else color
        out.append(D.box(xx, y_base - h, w, h, color=c, radius=radius,
                         radii={"BottomLeft": 0, "BottomRight": 0} if radius else None))
        xs.append((xx, w, y_base - h))
        xx += w + gap
    return "\n".join(out), xs


def sparkline(values, x0, w, y_base, y_top, vmin, vmax, color, *, lw=2.6,
              dots=None, label_every=6, label_fmt="%s", label_size=10,
              label_color=None, band=None, label_dy=-16):
    out = []
    pts = []
    n = len(values)
    for i, v in enumerate(values):
        if v is None:
            continue
        x = x0 + w * i / (n - 1.0)
        y = y_base - (v - vmin) / (vmax - vmin) * (y_base - y_top)
        pts.append((x, y, i, v))
    if len(pts) < 2:
        return "", []
    if band:
        out.append(D.box(x0, y_top, w, y_base - y_top, color=band))
    out.append(polyline([(p[0], p[1]) for p in pts], color, lw))
    if dots:
        out.append(circle(pts[-1][0], pts[-1][1], dots, color))
    if label_every:
        for j, (x, y, i, v) in enumerate(pts):
            if i % label_every and j != len(pts) - 1:
                continue
            out.append(D.text_el(label_fmt % v, x=x - 26, y=y + label_dy, w=52,
                                 size=label_size, color=label_color or INK_3,
                                 font=MONO, align="CENTER"))
    return "\n".join(out), pts


# ---------------------------------------------------------------- chrome ----
def status_bar(x, y, w, *, time="9:41", dark=True, color=None, size=12):
    fg = color or ("#FFFFFFFF" if dark else INK)
    out = [D.text_el(time, x=x + 18, y=y, w=60, size=size, color=fg, font=SEMI),
           D.text_el("房谱", x=x + w / 2 - 30, y=y + 1, w=60, size=size * .92,
                     color=fg, font=UI, align="CENTER")]
    # battery + signal, right aligned
    bx = x + w - 46
    out.append(D.box(bx, y + 4, 22, 10, color=None, radius=2,
                     border="1 SOLID " + A(fg, "99")))
    out.append(D.box(bx + 2, y + 6, 14, 6, color=fg, radius=1))
    out.append(D.box(bx + 23, y + 7, 2, 4, color=A(fg, "99")))
    for i, bh in enumerate((4, 6, 8, 10)):
        out.append(D.box(bx - 14 + i * 3.4, y + 14 - bh, 2.4, bh, color=fg))
    return "\n".join(out)


def phone_frame(w, h, *, radius=44, bg="#0B111CFF"):
    """Outer handset body so a phone screen never floats without a device."""
    return "\n".join([
        D.box(0, 0, w, h, color=bg, radius=radius,
              border="1 SOLID #2A3546FF"),
        D.box(4, 4, w - 8, h - 8, color="#FFFFFFFF", radius=radius - 4),
        D.box(4, 4, w - 8, h - 8, color=None, radius=radius - 4,
              border="1 SOLID #0E1622FF", children=[]),
    ])


def notch(x, y, w, h=26):
    return D.box(x + w / 2 - 46, y + 8, 92, h, color="#0B111CFF", radius=13)


def watch_case(w, h, *, radius=56):
    """Square-ish smartwatch: band stubs + body + screen."""
    out = []
    bx, by = (w - w * .58) / 2, 0
    out.append(D.box(bx, by - 30, w * .58, h + 60, color="#232C39FF", radius=34))
    out.append(D.box(w * .21, 0, w * .58, h, color="#121924FF", radius=radius))
    out.append(D.box(w * .21 + 3, 3, w * .58 - 6, h - 6, color="#070C13FF",
                     radius=radius - 3))
    return "\n".join(out)


def desktop_chrome(x, y, w, h, *, title="房谱 HOMESPEC", tab="退租差分 · 1602 室",
                   accent=BLUE):
    """Window frame + tab strip + sidebar rail, drawn as real chrome."""
    out = [D.box(x, y, w, h, color=PAPER, radius=12,
                 border="1 SOLID " + LINE, shadow="0 8 34 0 #0E16221F")]
    T = 38
    out.append(D.box(x, y, w, h, color=None, radius=12, children=[],
                     extra={"borderTopWidth": T, "borderTopColor": PAPER_3,
                            "borderLeftWidth": T, "borderLeftColor": PAPER_3,
                            "borderRightWidth": T, "borderRightColor": PAPER_3,
                            "color": PAPER_3, "borderRadius": 12}))
    # traffic lights
    for i, c in enumerate(("#FF5F57FF", "#FEBC2EFF", "#28C840FF")):
        out.append(D.box(x + 18 + i * 18, y + T / 2 - 5, 10, 10, color=c, radius=5))
    out.append(D.text_el(title, x=x + 82, y=y + T / 2 - 8, w=420, size=12,
                         color=INK_2, font=SEMI))
    out.append(D.box(x + w / 2 - 118, y + 8, 236, 24, color=PAPER_2, radius=7,
                     border="1 SOLID " + LINE))
    out.append(D.text_el(tab, x=x + w / 2 - 118, y=y + 8 + 6, w=236, size=11.5,
                         color=INK_2, font=UI, align="CENTER"))
    out.append(D.box(x + w - 200, y + T / 2 - 9, 70, 18, color=A(accent, "14"),
                     radius=9))
    out.append(D.text_el("SYNCED", x=x + w - 196, y=y + T / 2 - 7, w=62, size=9.5,
                         color=accent, font=MONO, ls=1.0, align="CENTER"))
    out.append(circle(x + w - 46, y + T / 2, 12, BLUE_XLT))
    out.append(D.text_el("陆", x=x + w - 58, y=y + T / 2 - 8, w=24, size=12,
                         color=BLUE_DK, font=SEMI, align="CENTER"))
    return "\n".join(out), T


def sidebar(x, y, w, h, items, *, active=0, radius=0):
    out = [D.box(x, y, w, h, color=PAPER_2, border="1 SOLID " + LINE)]
    yy = y + 22
    for i, (code, label, state) in enumerate(items):
        on = (i == active)
        if on:
            out.append(D.box(x + 10, yy - 6, w - 20, 34, color=BLUE_XLT, radius=8))
            out.append(D.box(x + 10, yy - 6, 3, 34, color=BLUE, radius=2))
        col = INK if on else INK_3
        out.append(D.text_el(code, x=x + 22, y=yy + 2, w=34, size=11, color=col,
                             font=MONO, style="BOLD"))
        out.append(D.text_el(label, x=x + 56, y=yy, w=w - 70, size=12.5,
                             color=col, font=SEMI if on else UI))
        if state:
            c = {"ok": GREEN, "warn": AMBER, "bad": RED, "none": INK_4}[state]
            out.append(circle(x + w - 22, yy + 9, 4, c))
        yy += 40
    return "\n".join(out)


# --------------------------------------------------------------- chrome 2 ---
def paper_sheet(w, h, *, tone=PAPER, shadow="0 10 40 0 #0E16221F"):
    """A physical printed sheet on a neutral desk surface."""
    return "\n".join([
        D.box(0, 0, w, h, color="#E3DED4FF"),
        D.box(26, 26, w - 52, h - 52, color=tone, shadow=shadow),
    ])


def crop_marks(w, h, m=26, length=16, color=INK_4):
    out = []
    for (cx, cy, dx, dy) in ((m, m, 1, 1), (w - m, m, -1, 1),
                             (m, h - m, 1, -1), (w - m, h - m, -1, -1)):
        x0 = cx - length / 2 if dx > 0 else cx - length / 2
        out.append(D.box(x0 if dx > 0 else cx - m * 0 + (m - length), cy - 0.5, length, 1,
                         color=color))
        out.append(D.box(cx - 0.5, cy - length / 2, 1, length, color=color))
    return "\n".join(out)


def qr_dummy(x, y, s, *, seed=7, dark=INK, quiet=6, modules=21):
    """A deterministic pseudo-QR block pattern. NOT a real QR code."""
    out = [D.box(x - quiet, y - quiet, s + 2 * quiet, s + 2 * quiet, color="#FFFFFFFF")]
    cell = s / modules
    seed = seed
    def nxt():
        nonlocal seed
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        return seed

    def finder(i, j):
        if i < 7 and j < 7:
            on = (i in (0, 6) or j in (0, 6) or (2 <= i <= 4 and 2 <= j <= 4))
            return on
        if i >= modules - 7 and j < 7:
            ii, jj = i - (modules - 7), j
            return (ii in (0, 6) or jj in (0, 6) or (2 <= ii <= 4 and 2 <= jj <= 4))
        if i < 7 and j >= modules - 7:
            ii, jj = i, j - (modules - 7)
            return (ii in (0, 6) or jj in (0, 6) or (2 <= ii <= 4 and 2 <= jj <= 4))
        return False

    def finder_on(i, j):
        return finder(i, j)

    # data modules, deterministic
    grid = {}
    for i in range(modules):
        for j in range(modules):
            if finder_on(i, j):
                continue
            v = nxt() % 100
            grid[(i, j)] = v < 46
    # timing rows
    for k in range(8, modules - 8):
        grid[(6, k)] = (k % 2 == 0)
        grid[(k, 6)] = (k % 2 == 0)
    for i in range(modules):
        for j in range(modules):
            if finder_on(i, j):
                grid[(i, j)] = finder(i, j)
    for (i, j), on in grid.items():
        if on:
            out.append(D.box(x + j * cell, y + i * cell, cell + .3, cell + .3,
                             color=dark))
    return "\n".join(out)


def disclaimer(s, x, y, w, *, size=9.5, color=INK_4, align="LEFT"):
    return D.text_el(s, x=x, y=y, w=w, size=size, color=color, font=UI,
                     ls=.2, align=align)


# ------------------------------------------------------------------ util ----
def count_elements(dsl_text):
    return dsl_text.count("<Positioned") + dsl_text.count("<Container") \
        + dsl_text.count("<Text") + dsl_text.count("<Transform") \
        + dsl_text.count("<ClipRRect")


def finish(kids, w, h, bg=PAPER, type_="png"):
    lst = []
    for k in kids:
        if isinstance(k, list):
            lst.extend(k)
        else:
            lst.append(k)
    return D.snapshot([D.stack(lst, w, h)], w, h, bg=bg, type_=type_)