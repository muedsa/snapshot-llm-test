# -*- coding: utf-8 -*-
"""B03 公共构件：程序化采样/像素字形/圆环/旋转封装。"""
import os
import math
from pathlib import Path

TASK_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ["SNAPSHOT_RUN_ID"]
BASE = TASK_ROOT / "outputs" / RUN / "B03"
CJK = "Noto Sans CJK SC"
NUM = "Inter"

CASES = []


def case(mark, w, h):
    def deco(fn):
        CASES.append((mark, w, h, fn))
        return fn
    return deco


def fnum(v):
    s = f"{float(v):.4f}".rstrip("0").rstrip(".")
    return s if s else "0"


def rect(s, x, y, w, h, color, radius=0, border=None):
    a = (f'<Positioned left="{fnum(x)}" top="{fnum(y)}" width="{fnum(w)}" '
         f'height="{fnum(h)}"><Container width="{fnum(w)}" height="{fnum(h)}"')
    if color:
        a += f' color="{color}"'
    if radius:
        a += f' borderRadius="{fnum(radius)}"'
    if border:
        a += f' border="{border}"'
    s.append(a + " /></Positioned>")


def txt(s, x, y, content, size, color, bold=False, family=CJK, align=None,
        box_w=None):
    sty = f'<Text fontSize="{fnum(size)}" color="{color}" fontFamily="{family}"'
    if bold:
        sty += ' fontStyle="BOLD"'
    if align:
        sty += f' textAlign="{align}"'
    sty += ">"
    if box_w is not None:
        s.append(f'<Positioned left="{fnum(x)}" top="{fnum(y)}" '
                 f'width="{fnum(box_w)}">{sty}{content}</Text></Positioned>')
    else:
        s.append(f'<Positioned left="{fnum(x)}" top="{fnum(y)}">{sty}'
                 f'{content}</Text></Positioned>')


def wrap_dsl(w, h, body, bg):
    return (f'<Snapshot background="{bg}" type="png">\n<Stack>\n'
            f'<SizedBox width="{w}" height="{h}" />\n' + "\n".join(body) +
            "\n</Stack>\n</Snapshot>\n")


def ellipse(s, cx, cy, rx, ry, color, border=None, bw=None):
    """中心椭圆（filled=描边兼 role）。border=(宽度枚数, 'SOLID', 色)。"""
    a = (f'<Positioned left="{fnum(cx - rx)}" top="{fnum(cy - ry)}" '
         f'width="{fnum(rx * 2)}" height="{fnum(ry * 2)}"><Container '
         f'width="{fnum(rx * 2)}" height="{fnum(ry * 2)}" '
         f'borderRadius="999"')
    if color:
        a += f' color="{color}"'
    if border and bw:
        a += f' border="{fnum(bw)} {border}"'
    s.append(a + " /></Positioned>")


def ring(s, cx, cy, r, thickness, color, bg):
    """双色圆环：外盘 color + 内盘 bg。"""
    ellipse(s, cx, cy, r, r, color)
    ellipse(s, cx, cy, r - thickness, r - thickness, bg)


def hill_rows(s, cx, cy, rx, ry, color, step=1):
    """实心「丘」形（椭圆剪影逐行填充）；由外向内叠画可得等高线。"""
    rows = int(2 * ry / step)
    for i in range(rows):
        yc = -ry + (i + 0.5) * step
        t = yc / ry
        hw = rx * math.sqrt(max(0.0, 1.0 - t * t))
        if hw > 0.4:
            rect(s, cx - hw, cy + yc, 2 * hw, step, color)


def ellipse_rows(s, cx, cy, rx, ry, color, step=1):
    hill_rows(s, cx, cy, rx, ry, color, step)


def sample_curve(s, x0, y0, w, h, fn, color, step=1):
    """fn(t)∈[0,1]（0=底 1=顶），逐列采样画竖矩形。"""
    for px in range(0, int(w), step):
        t = px / max(w - 1, 1)
        f = max(0.0, min(1.0, fn(t)))
        ph = f * h
        rect(s, x0 + px, y0 + h - ph, step, max(ph, 1), color)


def transform_str(m00, m01, m10, m11):
    return (f'({fnum(m00)},{fnum(m01)},0,0,{fnum(m10)},{fnum(m11)},0,0,'
            f'0,0,1,0,0,0,0,1)')


def rot_text(s, cx, cy, content, size, color, deg, bold=False, family=CJK):
    """把文本绕其中心旋转 deg 度（度→弧度矩阵）。实验件，不成立时改布局。"""
    a = math.radians(deg)
    m = (f'({fnum(math.cos(a))},{fnum(math.sin(a))},0,0,'
         f'{fnum(-math.sin(a))},{fnum(math.cos(a))},0,0,0,0,1,0,0,0,0,1)')
    bold_attr = ' fontStyle="BOLD"' if bold else ""
    box = max(size * len(content) * 1.15, size * 1.5)
    h = size * 1.6
    s.append(f'<Positioned left="{fnum(cx - box / 2)}" top="{fnum(cy - h / 2)}" '
             f'width="{fnum(box)}" height="{fnum(h)}">'
             f'<Transform matrix="{m}" origin="({fnum(box / 2)},{fnum(h / 2)})">'
             f'<Container width="{fnum(box)}" height="{fnum(h)}" '
             f'color="#00000000">'
             f'<Text fontSize="{fnum(size)}" color="{color}" '
             f'fontFamily="{family}"{bold_attr} '
             f'textAlign="CENTER">{content}</Text></Container>'
             f'</Transform></Positioned>')


PIX5 = {
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "3": ["11110", "00001", "00001", "11110", "00001", "00001", "11110"],
    "2": ["11110", "00001", "00001", "11110", "10000", "10000", "11110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
}
PIX7 = {
    "A": ["0011100", "0100010", "1000001", "1111111", "1000001", "1000001",
          "1000001"],
}


def pixel_text(s, x, y, cell, text, on, off=None):
    for ci, ch in enumerate(text):
        g = PIX5.get(ch)
        if g is None:
            continue
        for r, row in enumerate(g):
            for c, b in enumerate(row):
                if b == "1":
                    rect(s, x + (ci * 6 + c) * cell, y + r * cell, cell - 1,
                         cell - 1, on, 1)


def poly_rows(s, pts, color, step=1):
    """扫描线填充任意凸多边形（逐行小矩形）；round to step 网格。"""
    ysmin = min(p[1] for p in pts)
    ysmax = max(p[1] for p in pts)
    edges = [(pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts))]
    y = ysmin
    while y < ysmax:
        yc = y + 0.5
        xs = []
        for (x1, y1), (x2, y2) in edges:
            if (y1 <= yc) != (y2 <= yc):
                t = (yc - y1) / (y2 - y1)
                xs.append(x1 + t * (x2 - x1))
        if len(xs) >= 2:
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                w_seg = xs[k + 1] - xs[k]
                if w_seg > 0.2:
                    rect(s, xs[k], y, w_seg, step, color)
        y += step


def line_thick(s, x0, y0, x1, y1, w, color, step=1):
    dx = x1 - x0
    dy = y1 - y0
    ln = math.hypot(dx, dy) or 1.0
    nx = -dy / ln * w / 2
    ny = dx / ln * w / 2
    pts = [(x0 + nx, y0 + ny), (x1 + nx, y1 + ny),
           (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)]
    poly_rows(s, pts, color, step)


def stadium(s, cx, cy, length, thick, deg, color):
    """绕中心旋转的胶囊（等宽条），用于花瓣/刻度。"""
    a = math.radians(deg)
    m = (f'({fnum(math.cos(a))},{fnum(math.sin(a))},0,0,'
         f'{fnum(-math.sin(a))},{fnum(math.cos(a))},0,0,0,0,1,0,0,0,0,1)')
    lw = length
    lh = thick
    s.append(f'<Positioned left="{fnum(cx - lw / 2)}" top="{fnum(cy - lh / 2)}" '
             f'width="{fnum(lw)}" height="{fnum(lh)}">'
             f'<Transform matrix="{m}" origin="({fnum(lw / 2)},'
             f'{fnum(lh / 2)})"><Container width="{fnum(lw)}" '
             f'height="{fnum(lh)}" color="{color}" '
             f'borderRadius="{fnum(lh / 2)}" /></Transform></Positioned>')
