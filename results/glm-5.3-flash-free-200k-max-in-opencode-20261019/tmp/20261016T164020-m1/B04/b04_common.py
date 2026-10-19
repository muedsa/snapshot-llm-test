# -*- coding: utf-8 -*-
"""B04 共用构件（低层 API 与 B03 完全一致的已验证字符串 DSL 写法）。"""
import os
import math
from pathlib import Path

TASK_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ.get("SNAPSHOT_RUN_ID", "20261016T164020-m1")
BASE = TASK_ROOT / "outputs" / RUN / "B04"
CJK = "Noto Sans CJK SC"
NUM = "Inter"

CASES = []

# —— 特辑色板（编辑系统五带语言）——
CREAM = "#F4EFE4"   # 纸底
INK = "#16293B"
MUTED = "#6E7F8C"
CYAN = "#2FA79E"
AMBER = "#E89B3C"
CORAL = "#D9543F"
FIG = "#2E7FB0"
ZT = ["#9CD1E6", "#BFDCE7", "#8FBFD9", "#4E8FB4", "#20567B"]  # 五带由浅入深
NAVY = "#08182A"
PANEL = "#0E2438"
DLINE = "#1E3A52"
LTX = "#E8F0F5"
LSUB = "#7FB3C9"


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


def num(s, x, y, content, size, color, bold=False, align=None, box_w=None):
    txt(s, x, y, content, size, color, bold=bold, family=NUM, align=align,
        box_w=box_w)


def wrap_dsl(w, h, body, bg):
    return (f'<Snapshot background="{bg}" type="png">\n<Stack>\n'
            f'<SizedBox width="{w}" height="{h}" />\n' + "\n".join(body) +
            "\n</Stack>\n</Snapshot>\n")


def ellipse_rows(s, cx, cy, rx, ry, color, step=1):
    hill_rows(s, cx, cy, rx, ry, color, step)


def hill_rows(s, cx, cy, rx, ry, color, step=1):
    rows = int(2 * ry / step)
    for i in range(rows):
        yc = -ry + (i + 0.5) * step
        t = yc / ry
        hw = rx * math.sqrt(max(0.0, 1.0 - t * t))
        if hw > 0.4:
            rect(s, cx - hw, cy + yc, 2 * hw, step, color)


def sample_curve(s, x0, y0, w, h, fn, color, step=1):
    for px in range(0, int(w), step):
        t = px / max(w - 1, 1)
        f = max(0.0, min(1.0, fn(t)))
        ph = f * h
        rect(s, x0 + px, y0 + h - ph, step, max(ph, 1), color)


def transform_str(m00, m01, m10, m11):
    return (f'({fnum(m00)},{fnum(m01)},0,0,{fnum(m10)},{fnum(m11)},0,0,'
            f'0,0,1,0,0,0,0,1)')


def rot_text(s, cx, cy, content, size, color, deg, bold=False, family=CJK):
    a = math.radians(deg)
    m = transform_str(math.cos(a), math.sin(a), -math.sin(a), math.cos(a))
    bold_attr = ' fontStyle="BOLD"' if bold else ""
    box = max(size * len(content) * 1.15, size * 1.5)
    h = size * 1.6
    s.append(f'<Positioned left="{fnum(cx - box / 2)}" top="{fnum(cy - h / 2)}" '
             f'width="{fnum(box)}" height="{fnum(h)}">'
             f'<Transform matrix="{m}" origin="({fnum(box / 2)},'
             f'{fnum(h / 2)})">'
             f'<Container width="{fnum(box)}" height="{fnum(h)}" '
             f'color="#00000000">'
             f'<Text fontSize="{fnum(size)}" color="{color}" '
             f'fontFamily="{family}"{bold_attr} '
             f'textAlign="CENTER">{content}</Text></Container>'
             f'</Transform></Positioned>')


def poly_rows(s, pts, color, step=1):
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
    a = math.radians(deg)
    m = transform_str(math.cos(a), math.sin(a), -math.sin(a), math.cos(a))
    lw, lh = length, thick
    s.append(f'<Positioned left="{fnum(cx - lw / 2)}" top="{fnum(cy - lh / 2)}" '
             f'width="{fnum(lw)}" height="{fnum(lh)}">'
             f'<Transform matrix="{m}" origin="({fnum(lw / 2)},'
             f'{fnum(lh / 2)})"><Container width="{fnum(lw)}" '
             f'height="{fnum(lh)}" color="{color}" '
             f'borderRadius="{fnum(lh / 2)}" /></Transform></Positioned>')


# —— 特辑版式 —— MAST/FOOT等
def mast(s, w, idx, title, tagline, dark=False):
    bg = "#02203A" if dark else "#12293B"
    rect(s, 0, 0, w, 116, bg)
    rect(s, 0, 0, 10, 116, CYAN)
    txt(s, 34, 20, "下潜 DEEP DIVE · 特辑", 14, "#8FD6CB", bold=True)
    num(s, 34, 42, f"{idx:02d} / 10 pieces", 16, "#5E93B0", bold=True)
    txt(s, 34, 70, title, 32, "#F2EFE6", bold=True)
    txt(s, w - 74, 34, tagline, 16, LSUB, align="RIGHT", box_w=min(w - 110, 640))


def footer(s, w, h, left, codes, dark=False):
    bg = "#0A1F33" if dark else "#EBE1CC"
    fg = "#93A9BD" if dark else "#7C8B98"
    ac = "#C9A15A" if dark else "#B08430"
    rect(s, 0, h - 58, w, 58, bg)
    txt(s, 24, h - 40, left, 15, fg, box_w=max(w - 360, 200))
    srcs(s, w - 320, h - 40, codes, ac)


def chip(s, x, y, w, h, label, fill, fg, size=14, r=None, bold=True):
    rect(s, x, y, w, h, fill, r if r is not None else h / 2)
    txt(s, x, y + h / 2 - size * 0.72, label, size, fg, bold=bold,
        align="CENTER", box_w=w)


def srcs(s, x, y, codes, color):
    if isinstance(codes, str):
        codes = [codes]
    num(s, x, y, "[" + " / ".join(c for c in codes) + "]", 15, color, bold=True)


def sept(s, x1, y1, x2, y2, color, step=1):
    line_thick(s, x1, y1, x2, y2, 1, color, step)


def exhibit(s, x, y, w, h, title, body, codes, dark=False,
            title_col=None, bg=None, border=None, size=15):
    bg = bg or (PANEL if dark else "#FFFFFF")
    tc = title_col or ("#9FD8CC" if dark else CYAN)
    bc = LTX if dark else INK
    rect(s, x, y, w, h, bg, 10, border or f'1 SOLID {DLINE if dark else "#D8CDB5"}')
    txt(s, x + 22, y + 20, title, 18, tc, bold=True)
    lines = body.split("\n")
    yy = y + 54
    for ln in lines:
        txt(s, x + 22, yy, ln, size, bc, box_w=w - 44)
        yy += size * 1.62
    num(s, x + 22, y + h - 32, "[" + " / ".join(codes) + "]", 14,
        "#C9A15A" if dark else "#B08430", bold=True)
