"""A10 generator: six-panel compositing / filter semantics board (1440x1100).

Panels (areas are 320x240 on white, 3 cols x 2 rows, 48px gutters, captions outside):
  P1  two rectangles with their own 50% alpha      (#FF000080 over, #0000FF80 on top)
  P2  the same rectangles opaque inside Opacity(0.5)
  P3  sharp stripes, rounded card, only the BACKDROP blurred (ClipRRect+BackdropFilter)
  P4  the same stripes, the card's own text+shape blurred (ImageFiltered subtree)
  P5  ColorFiltered(MULTIPLY #F6B94A) then subtree blur, with a transparent gap,
      a dark rectangle and a shadow so the paint bounds stay observable
  P6  the same P5 stack restricted to a circular ClipOval

Semantics measured with probe-a10.png first (see iterations.jsonl): ClipRRect limits
BackdropFilter to the rounded card (outside stays sharp), ImageFiltered only touches its
own subtree, and MULTIPLY stays inside the subtree paint bounds while tinting the
transparent gaps - which is what makes P5/P6 legible.
"""
from __future__ import annotations

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261003-114508-flashmax", "_suite", "shared"))
from dslkit import text_width, CJK, MONO  # noqa: E402

W, H = 1440, 1100
AW, AH = 320, 240
AX = [192, 560, 928]
AY = [226, 586]
SIGMA = 6
INK = "#0F172AFF"
SOFT = "#475569FF"
MUTED = "#64748BFF"
PAGE = "#EEF2F7FF"
CARD = "#FFFFFFFF"
EDGE = "#E2E8F0FF"
AREA_EDGE = "#CBD5E1FF"
ACCENT = "#0E9F8FFF"
RED = "#FF000080"
BLUE = "#0000FF80"
TINT = "#F6B94AFF"

CARD_W, CARD_H, CARD_R = 240, 160, 20
CONTENT_W, CONTENT_H = 200, 130          # P5/P6 filtered content box
CIRCLE_D = 200                            # P6 ClipOval box (radius 100)


class B:
    def __init__(self) -> None:
        self.p = [f'<Snapshot background="{PAGE}" type="png">',
                  f'<Container width="{W}" height="{H}">',
                  '<Stack alignment="TOP_LEFT" fit="EXPAND">']

    def raw(self, s: str) -> None:
        self.p.append(s)

    def box(self, x, y, w, h, color=None, radius=None, border=None, shadow=None,
            shape=None, extra="") -> None:
        a = f'<Container width="{w}" height="{h}"'
        if color:
            a += f' color="{color}"'
        if radius is not None:
            a += f' borderRadius="{radius}"'
        if border:
            a += f' border="{border}"'
        if shadow:
            a += f' boxShadow="{shadow}"'
        if shape:
            a += f' shape="{shape}"'
        if extra:
            a += " " + extra
        self.p.append(f'<Positioned left="{x}" top="{y}">{a}/></Positioned>')

    def text(self, x, y, s, size, color, weight="NORMAL", family=CJK, w=None, align="CENTER_LEFT"):
        if w is not None and text_width(s, size, family == MONO) > w + 0.5:
            raise SystemExit(f"text too wide ({text_width(s,size,family==MONO):.0f}>{w}): {s!r}")
        body = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        a = f'fontSize="{size}" color="{color}" fontFamily="{family}" fontStyle="{weight}"'
        if w:
            self.p.append(f'<Positioned left="{x}" top="{y}" width="{w}">'
                          f'<Container alignment="{align}"><Text {a}>{body}</Text>'
                          f'</Container></Positioned>')
        else:
            self.p.append(f'<Positioned left="{x}" top="{y}"><Text {a}>{body}</Text></Positioned>')

    def dashes(self, x0, y0, x1, y1, color, th=1.0, dash=8.0, gap=6.0):
        total = math.hypot(x1 - x0, y1 - y0)
        ux, uy = (x1 - x0) / total, (y1 - y0) / total
        d = 0.0
        while d < total:
            e = min(d + dash, total)
            mx, my = x0 + ux * (d + e) / 2, y0 + uy * (d + e) / 2
            ln = e - d
            ang = math.atan2(uy, ux)
            c, s = math.cos(ang), math.sin(ang)
            tx = mx - c * (ln / 2) + s * (th / 2)
            ty = my - s * (ln / 2) - c * (th / 2)
            mat = f"({c:.6f},{s:.6f},0,0,{-s:.6f},{c:.6f},0,0,0,0,1,0,{tx:.4f},{ty:.4f},0,1)"
            self.raw(f'<Positioned left="0" top="0"><Transform matrix="{mat}">'
                     f'<Container width="{ln:.3f}" height="{th}" color="{color}"/></Transform></Positioned>')
            d = e + gap

    def finish(self) -> str:
        self.p += ['</Stack>', '</Container>', '</Snapshot>']
        return "\n".join(self.p) + "\n"


def area_open(b: B, x, y):
    b.box(x, y, AW, AH, CARD, border=f"1 SOLID {AREA_EDGE}")


def stripes(x, y, w, h, sw=14, color=INK):
    out = []
    i = 0
    while i * sw < w:
        out.append(f'<Positioned left="{x + i * sw}" top="{y}">'
                   f'<Container width="{min(sw, w - i * sw)}" height="{h}" color="{color}"/></Positioned>')
        i += 2
    return "".join(out)


def sample_marker(b: B, x, y):
    """1px ring around the sampling point; the centre pixel stays untouched."""
    b.raw(f'<Positioned left="{x - 7}" top="{y - 7}"><Container width="15" height="15" '
          f'shape="CIRCLE" border="1 SOLID #0F172AFF"/></Positioned>')


def card_content(b: B, ox, oy, blurred: bool):
    """White pill + text + accent bar inside the rounded card.

    The accent bar is 276px wide on a 240px card, i.e. it deliberately bleeds 18px past
    both card edges: in P3 it stays razor sharp while the backdrop is blurred, in P4 the
    same bar sits inside the ImageFiltered subtree so its blur visibly spills onto the
    still-sharp stripes outside the card (documented ImageFiltered behaviour).

    Coordinates below are relative to the filter box, which starts 18px left of the card
    so that the bleeding bar is inside the filtered subtree's own box.
    """
    bar_w, bar_h = CARD_W + 36, 16
    pill_w, pill_h = 200, 44
    pad = (bar_w - CARD_W) / 2                    # 18
    pill_x = pad + (CARD_W - pill_w) / 2
    tx = pill_x + (pill_w - text_width("SHARP / BLUR", 24, True)) / 2

    def placed(left, top, body):
        return f'<Positioned left="{left:.1f}" top="{top}"' + (f'>{body}</Positioned>')

    parts = [
        (pill_x, 22, f'<Container width="{pill_w}" height="{pill_h}" color="#FFFFFFFF" borderRadius="22"/>'),
        (tx, 29, f'<Text fontSize="24" color="#0F172AFF" fontFamily="{MONO}" fontStyle="BOLD">'
                 f'SHARP / BLUR</Text>'),
        (0, 108, f'<Container width="{bar_w}" height="{bar_h}" color="{ACCENT}" borderRadius="8"/>'),
    ]
    if blurred:
        inner = "".join(placed(x, y, body) for x, y, body in parts)
        b.raw(f'<Positioned left="{ox - pad}" top="{oy}" width="{bar_w}" height="200">'
              f'<ImageFiltered sigmaX="{SIGMA}" sigmaY="{SIGMA}">'
              f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
              + inner + '</Stack></ImageFiltered></Positioned>')
    else:
        for x, y, body in parts:
            b.raw(placed(x + ox - pad, y + oy, body))


def p5_content(x, y, clip: bool):
    """Dark rectangle + two bars with a transparent gap + a soft shadow."""
    body = [
        f'<Positioned left="0" top="20"><Container width="70" height="90" color="#1F2937FF" '
        f'borderRadius="8" boxShadow="0 8 16 0 #0F172A40 NORMAL"/></Positioned>',
        f'<Positioned left="86" top="20"><Container width="44" height="44" color="#2563EBFF" borderRadius="6"/></Positioned>',
        f'<Positioned left="142" top="20"><Container width="44" height="44" color="#2563EBFF" borderRadius="6"/></Positioned>',
        f'<Positioned left="86" top="74"><Container width="100" height="56" color="#CBD5E1FF" borderRadius="8"/></Positioned>',
    ]
    stack = ('<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">' + "".join(body) + '</Stack>')
    filtered = (f'<ImageFiltered sigmaX="{SIGMA}" sigmaY="{SIGMA}">'
                f'<ColorFiltered color="{TINT}" blendMode="MULTIPLY">{stack}</ColorFiltered>'
                f'</ImageFiltered>')
    if clip:
        return (f'<Positioned left="{x}" top="{y}" width="{CIRCLE_D}" height="{CIRCLE_D}">'
                f'<ClipOval>{filtered}</ClipOval></Positioned>')
    return filtered


def main() -> None:
    version = sys.argv[1] if len(sys.argv) > 1 else "v1"
    b = B()
    # header
    b.box(0, 0, W, 118, INK)
    b.text(192, 26, "看到差异，才能说用对了", 40, "#F8FAFCFF", "BOLD")
    b.text(192, 80, "六格对照：alpha / 组透明度 / 仅背景模糊 / 子树模糊 / 滤色×模糊 / 圆形裁剪"
                    "　·　σx=σy=6　·　实验区 320×240 白底",
           20, "#94A3B8FF")

    p1 = (AX[0], AY[0])
    p2 = (AX[1], AY[0])
    p3 = (AX[2], AY[0])
    p4 = (AX[0], AY[1])
    p5 = (AX[1], AY[1])
    p6 = (AX[2], AY[1])

    caps = [
        (p1[0], "① 两个矩形各自 50% alpha", "红下蓝上，各带 50% alpha", "重叠处两层互相混合 → 偏紫"),
        (p2[0], "② 不透明矩形 + Opacity(0.5)", "组内先压平，再整体 50%", "重叠处 = 蓝白各半 → 淡蓝"),
        (p3[0], "③ 仅背景模糊", "ClipRRect + BackdropFilter", "字清晰 · 背景糊 · 不外溢"),
        (p4[0], "④ 卡内子树模糊", "ImageFiltered σ=6 只糊内容", "字糊 · 条纹清晰 · 模糊外溢卡外"),
        (p5[0], "⑤ 滤色 → 子树模糊", "MULTIPLY #F6B94A 之后 σ=6", "滤色限框内 · 模糊外溢约 18px"),
        (p6[0], "⑥ ⑤ 再限定圆形裁剪", "ClipOval 直径 200 限定区域", "圆外无滤色 · 边界清晰"),
    ]
    for i, (x, t1, t2, t3) in enumerate(caps):
        base = AY[0] if i < 3 else AY[1]
        b.text(x, base - 94, t1, 22, INK, "BOLD", w=AW)
        b.text(x, base - 64, t2, 20, SOFT, w=AW)
        b.text(x, base - 36, t3, 20, ACCENT, "BOLD", w=AW)

    # ---------------------------------------------------------------- P1 / P2
    area_open(b, *p1)
    b.box(p1[0] + 40, p1[1] + 40, 160, 120, "#FF000080")
    b.box(p1[0] + 120, p1[1] + 80, 160, 120, "#0000FF80")
    sample_marker(b, p1[0] + 180, p1[1] + 100)
    area_open(b, *p2)
    b.raw(f'<Positioned left="0" top="0"><Opacity opacity="0.5">'
          f'<Stack alignment="TOP_LEFT" fit="EXPAND">'
          f'<Positioned left="{p2[0] + 40}" top="{p2[1] + 40}">'
          f'<Container width="160" height="120" color="#FF0000FF"/></Positioned>'
          f'<Positioned left="{p2[0] + 120}" top="{p2[1] + 80}">'
          f'<Container width="160" height="120" color="#0000FFFF"/></Positioned>'
          f'</Stack></Opacity></Positioned>')
    sample_marker(b, p2[0] + 180, p2[1] + 100)

    # ---------------------------------------------------------------- P3 / P4
    for area, blurred in ((p3, False), (p4, True)):
        area_open(b, *area)
        b.raw(stripes(area[0] + 1, area[1] + 1, AW - 2, AH - 2))
        cx, cy = area[0] + 40, area[1] + 40
        if blurred:
            # sharp card fill, then the blurred content, then the card outline
            b.raw(f'<Positioned left="{cx}" top="{cy}"><ClipRRect borderRadius="{CARD_R}">'
                  f'<Container width="{CARD_W}" height="{CARD_H}" color="#FFFFFF99"/></ClipRRect></Positioned>')
            card_content(b, cx, cy, True)
        else:
            b.raw(f'<Positioned left="{cx}" top="{cy}"><ClipRRect borderRadius="{CARD_R}">'
                  f'<BackdropFilter sigmaX="{SIGMA}" sigmaY="{SIGMA}">'
                  f'<Container width="{CARD_W}" height="{CARD_H}" color="#FFFFFF99"/>'
                  f'</BackdropFilter></ClipRRect></Positioned>')
            card_content(b, cx, cy, False)
        b.box(cx, cy, CARD_W, CARD_H, None, radius=CARD_R, border="1 SOLID #0F172A33")

    # ---------------------------------------------------------------- P5
    area_open(b, *p5)
    cx5, cy5 = p5[0] + (AW - CONTENT_W) // 2, p5[1] + (AH - CONTENT_H) // 2
    for x0, y0, x1, y1 in ((cx5, cy5, cx5 + CONTENT_W, cy5), (cx5 + CONTENT_W, cy5, cx5 + CONTENT_W, cy5 + CONTENT_H),
                           (cx5 + CONTENT_W, cy5 + CONTENT_H, cx5, cy5 + CONTENT_H), (cx5, cy5 + CONTENT_H, cx5, cy5)):
        b.dashes(x0, y0, x1, y1, "#94A3B8FF", 1.0, 7.0, 5.0)
    b.raw(f'<Positioned left="{cx5}" top="{cy5}" width="{CONTENT_W}" height="{CONTENT_H}">'
          + p5_content(0, 0, False) + '</Positioned>')

    # ---------------------------------------------------------------- P6
    area_open(b, *p6)
    ox6, oy6 = p6[0] + (AW - CIRCLE_D) // 2, p6[1] + (AH - CIRCLE_D) // 2
    # identical content position inside the area, so P5 and P6 differ only by the clip
    inner_dx = (AW - CONTENT_W) // 2 - (AW - CIRCLE_D) // 2
    inner_dy = (AH - CONTENT_H) // 2 - (AH - CIRCLE_D) // 2
    for x0, y0, x1, y1 in ((ox6 + inner_dx, oy6 + inner_dy, ox6 + inner_dx + CONTENT_W, oy6 + inner_dy),
                           (ox6 + inner_dx + CONTENT_W, oy6 + inner_dy, ox6 + inner_dx + CONTENT_W, oy6 + inner_dy + CONTENT_H),
                           (ox6 + inner_dx + CONTENT_W, oy6 + inner_dy + CONTENT_H, ox6 + inner_dx, oy6 + inner_dy + CONTENT_H),
                           (ox6 + inner_dx, oy6 + inner_dy + CONTENT_H, ox6 + inner_dx, oy6 + inner_dy)):
        b.dashes(x0, y0, x1, y1, "#94A3B8FF", 1.0, 7.0, 5.0)
    b.raw(f'<Positioned left="{ox6}" top="{oy6}" width="{CIRCLE_D}" height="{CIRCLE_D}">'
          f'<ClipOval><Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
          f'<Positioned left="{inner_dx}" top="{inner_dy}" width="{CONTENT_W}" height="{CONTENT_H}">'
          + p5_content(0, 0, False) +
          f'</Positioned></Stack></ClipOval></Positioned>')
    b.box(ox6, oy6, CIRCLE_D, CIRCLE_D, None, radius=CIRCLE_D // 2, border="1 SOLID #94A3B8FF")
    b.text(p6[0] + 10, p6[1] + 214, "灰圆 = ClipOval 边界", 20, MUTED)

    # ---------------------------------------------------------------- footer
    fy = 840
    b.box(AX[0], fy, 1056, 244, CARD, radius=16, border=f"1 SOLID {EDGE}")
    b.text(AX[0] + 24, fy + 16, "①② 采样点 (180,100)：预期值 vs 最终图实测值", 22, INK, "BOLD")
    b.text(AX[0] + 24, fy + 48,
           "① α = 128/255 = 0.50196：红先、蓝后各自合成 → 理想 (127, 63, 191)，实测一致", 20, SOFT)
    b.text(AX[0] + 24, fy + 76,
           "② 组 opacity = 0.5 先压平：蓝盖住红 → 理想 127.5，实测 (126, 126, 255)", 20, SOFT)
    b.text(AX[0] + 24, fy + 104,
           "差别：① 两层各自混合、② 组内先压平再整体半透明；② 走离屏图层，8bit 量化比理想低 1–2 阶。", 20, MUTED)
    b.text(AX[0] + 24, fy + 140, "③–⑥ 视觉判断（依据像素测量，详见 composite-audit.json）", 22, INK, "BOLD")
    b.text(AX[0] + 24, fy + 174, "③ 卡内背景已糊、卡外条纹与文字清晰 → 不外溢", 20, SOFT)
    b.text(AX[0] + 24, fy + 202, "④ 文字糊、条纹清晰、跨边色条模糊外溢到卡外约 18px", 20, SOFT)
    b.text(AX[0] + 600, fy + 174, "⑤ 滤色限在内容框内，模糊外扩约 18px", 20, SOFT)
    b.text(AX[0] + 600, fy + 202, "⑥ 圆外 0 个滤色像素，圆形边界清晰", 20, SOFT)

    dsl = b.finish()
    out = os.path.join(HERE, f"compositing-lab.{version}.snapshot")
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(dsl)
    layout = {
        "canvas": [W, H], "area": [AW, AH], "sigma": SIGMA,
        "areas": {"P1": list(p1), "P2": list(p2), "P3": list(p3),
                  "P4": list(p4), "P5": list(p5), "P6": list(p6)},
        "sample_point": [180, 100],
        "rects": {"red": [40, 40, 160, 120], "blue": [120, 80, 160, 120]},
        "card": {"size": [CARD_W, CARD_H], "radius": CARD_R, "offset": [40, 40],
                 "stripes": {"width": 14}},
        "content_p5": {"size": [CONTENT_W, CONTENT_H],
                       "origin": [p5[0] + (AW - CONTENT_W) // 2, p5[1] + (AH - CONTENT_H) // 2]},
        "content_p6": {"origin": [p6[0] + (AW - CONTENT_W) // 2, p6[1] + (AH - CONTENT_H) // 2]},
        "circle_p6": {"origin": [(p6[0] + (AW - CIRCLE_D) // 2), (p6[1] + (AH - CIRCLE_D) // 2)],
                      "diameter": CIRCLE_D},
        "colors": {"tint": TINT, "red": "#FF0000", "blue": "#0000FF", "stripe": INK,
                   "area": "#FFFFFF"},
    }
    with open(os.path.join(HERE, f"layout.{version}.json"), "w", encoding="utf-8") as fh:
        json.dump(layout, fh, ensure_ascii=False, indent=2)
    print("wrote", out, len(dsl), "chars")


if __name__ == "__main__":
    main()
