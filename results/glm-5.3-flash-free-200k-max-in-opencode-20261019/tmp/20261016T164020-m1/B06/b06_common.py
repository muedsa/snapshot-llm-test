# -*- coding: utf-8 -*-
"""B06 共享组件：发射格式完全沿用 B05 已通过真实渲染验证的写法
（Positioned 包 Container/Text、fontStyle=BOLD、Transform 矩阵）。
字体纪律：CJK 字符串走 txt（Noto Sans CJK SC）；纯 ASCII 数字走 num（Inter）。
禁裸 '<'：用量词或全角符号。颜色均带 #。"""
import math

CJK = "Noto Sans CJK SC"
INTER = "Inter"

CASES = []


def case(mark, w, h):
    def deco(fn):
        CASES.append((mark, w, h, fn))
        return fn
    return deco


def fnum(v):
    s = ("%.4f" % float(v)).rstrip("0").rstrip(".")
    return s if s else "0"


def rect(s, x, y, w, h, color, radius=0, border=None):
    a = ('<Positioned left="%s" top="%s" width="%s" height="%s">'
         '<Container width="%s" height="%s"' %
         (fnum(x), fnum(y), fnum(w), fnum(h), fnum(w), fnum(h)))
    if color:
        a += ' color="%s"' % color
    if radius:
        a += ' borderRadius="%s"' % fnum(radius)
    if border:
        a += ' border="%s"' % border
    s.append(a + " /></Positioned>")


def txt(s, x, y, content, size, color, bold=False, family=CJK, align=None,
        box_w=None):
    sty = ('<Text fontSize="%s" color="%s" fontFamily="%s"' %
           (fnum(size), color, family))
    if bold:
        sty += ' fontStyle="BOLD"'
    if align:
        sty += ' textAlign="%s"' % align
    sty += ">"
    if box_w is not None:
        s.append('<Positioned left="%s" top="%s" width="%s">%s%s</Text>'
                 '</Positioned>' % (fnum(x), fnum(y), fnum(box_w), sty, content))
    else:
        s.append('<Positioned left="%s" top="%s">%s%s</Text></Positioned>' %
                 (fnum(x), fnum(y), sty, content))


def num(s, x, y, content, size, color, bold=False, align=None, box_w=None):
    txt(s, x, y, content, size, color, bold=bold, family=INTER, align=align,
        box_w=box_w)


def wrap_dsl(w, h, body, bg):
    return ('<Snapshot background="%s" type="png">\n<Stack>\n'
            '<SizedBox width="%s" height="%s" />\n' % (bg, w, h)
            + "\n".join(body) + "\n</Stack>\n</Snapshot>\n")


def hill_rows(s, cx, cy, rx, ry, color, step=1):
    rows = int(2 * ry / step)
    for i in range(rows):
        yc = -ry + (i + 0.5) * step
        t = yc / ry
        hw = rx * math.sqrt(max(0.0, 1.0 - t * t))
        if hw > 0.4:
            rect(s, cx - hw, cy + yc, 2 * hw, step, color)


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


def transform_str(m00, m01, m10, m11):
    return ("%s,%s,0,0,%s,%s,0,0,0,0,1,0,0,0,0,1" %
            (fnum(m00), fnum(m01), fnum(m10), fnum(m11)))


def rot_text(s, cx, cy, content, size, color, deg, bold=False, family=CJK):
    a = math.radians(deg)
    m = transform_str(math.cos(a), math.sin(a), -math.sin(a), math.cos(a))
    bold_attr = ' fontStyle="BOLD"' if bold else ""
    box = max(size * len(content) * 1.15, size * 1.5)
    hh = size * 1.6
    s.append('<Positioned left="%s" top="%s" width="%s" height="%s">'
             '<Transform matrix="(%s)" origin="(%s,%s)">'
             '<Container width="%s" height="%s" color="#00000000">'
             '<Text fontSize="%s" color="%s" fontFamily="%s"%s '
             'textAlign="CENTER">%s</Text></Container></Transform>'
             '</Positioned>' % (fnum(cx - box / 2), fnum(cy - hh / 2),
                                fnum(box), fnum(hh), m, fnum(box / 2),
                                fnum(hh / 2), fnum(box), fnum(hh),
                                fnum(size), color, family, bold_attr, content))


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
    s.append('<Positioned left="%s" top="%s" width="%s" height="%s">'
             '<Transform matrix="(%s)" origin="(%s,%s)">'
             '<Container width="%s" height="%s" color="%s" '
             'borderRadius="%s" /></Transform></Positioned>' %
             (fnum(cx - lw / 2), fnum(cy - lh / 2), fnum(lw), fnum(lh), m,
              fnum(lw / 2), fnum(lh / 2), fnum(lw), fnum(lh), color,
              fnum(lh / 2)))


def dash_line(s, x0, y0, x1, y1, w, color, dash=8, gap=6):
    dx, dy = x1 - x0, y1 - y0
    ln = math.hypot(dx, dy)
    if ln <= 0:
        return
    ux, uy = dx / ln, dy / ln
    t = 0.0
    while t < ln:
        t2 = min(t + dash, ln)
        line_thick(s, x0 + ux * t, y0 + uy * t, x0 + ux * t2, y0 + uy * t2,
                   w, color)
        t = t2 + gap


def arrow(s, x0, y0, x1, y1, w, color, head=12):
    ang = math.atan2(y1 - y0, x1 - x0)
    bx = x1 - head * math.cos(ang)
    by = y1 - head * math.sin(ang)
    line_thick(s, x0, y0, bx, by, w, color)
    left = (bx + (head * 0.7) * math.cos(ang + math.radians(140)),
            by + (head * 0.7) * math.sin(ang + math.radians(140)))
    right = (bx + (head * 0.7) * math.cos(ang - math.radians(140)),
             by + (head * 0.7) * math.sin(ang - math.radians(140)))
    poly_rows(s, [(x1, y1), left, right], color)


def pill(s, x, y, label, accent, dark=False, size=18):
    """小圆角标签（B05 式：胶囊左上角为 (x,y)，文字在 y+7）。"""
    wlab = size * len(label) + 26
    fill = "#1B3A5E" if dark else "#EFE8D8"
    rect(s, x, y, wlab, size + 14, fill, size + 14,
         border='1.4 SOLID %s' % accent)
    is_cjk = any(ord(c) > 0x2E00 for c in label)
    fam = CJK if is_cjk else INTER
    txt(s, x, y + 7, label, size, accent, bold=True, align="CENTER",
        box_w=wlab, family=fam)


def lamp(s, x, y, color, r=7):
    hill_rows(s, x, y, r, r, color, 1)


def card(s, x, y, w, h, color="#FFFFFF", accent=None, r=14, border=None):
    if border is None:
        border = '1 SOLID #DDD5C4' if accent is None else ('1.5 SOLID %s' % accent)
    rect(s, x, y, w, h, color, r, border)


def dot_text(s, x, y, dot_color, text, size, color, bold=False, dot_r=6,
             family=None):
    lamp(s, x + dot_r, y + size * 0.75, dot_color, dot_r)
    txt(s, x + dot_r * 2 + 12, y, text, size, color, bold=bold,
        family=family if family else CJK)
