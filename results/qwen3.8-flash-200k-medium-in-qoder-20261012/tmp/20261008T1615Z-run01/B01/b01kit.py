"""B01 作品集共用构件（建立在 _suite/scripts/dslkit.py 之上）。

用法（在各 case 生成脚本里）：

    import sys, os
    from pathlib import Path
    root = Path(os.environ["SNAPSHOT_TASK_ROOT"]); rid = os.environ["SNAPSHOT_RUN_ID"]
    sys.path.insert(0, str(root / "tmp" / rid / "_suite" / "scripts"))
    sys.path.insert(0, str(root / "tmp" / rid / "B01"))
    from dslkit import Doc, TextFit, GRAD_NIGHT, GRAD_LIGHT
    import b01kit as K

只放 B01 能力探针（probe/caps*.png）真实验证过的构造：SWEEP/RADIAL 环、
分段折线、毛玻璃、描边/霓虹文字、同心发光、waffle、表格。
dslkit 的 Doc.text 不接收任意属性，因此高级文本属性一律走本模块 T()/place()。
"""
import math

from dslkit import Doc, TextFit, n  # noqa: F401


def hexa(hex6, alpha):
    """#RRGGBB + 0..1 -> #RRGGBBAA（服务支持 8 位十六进制）"""
    a = max(0, min(255, int(round(alpha * 255))))
    return "%s%02X" % (hex6, a)


ALIGN = {"START": "CENTER_LEFT", "END": "CENTER_RIGHT", "CENTER": "CENTER",
         "TOP_LEFT": "TOP_LEFT", "TOP_CENTER": "TOP_CENTER",
         "BOTTOM_LEFT": "BOTTOM_LEFT", "BOTTOM_CENTER": "BOTTOM_CENTER"}


def T(s, font, **a):
    """任意属性的 <Text>。a 直接用 DSL 属性名（下划线转驼峰不便，故要求驼峰）。"""
    a.setdefault("color", "#F1F5F9")
    a["fontFamily"] = font
    at = "".join(' %s="%s"' % (k, v) for k, v in a.items())
    return "<Text%s>%s</Text>" % (at, s)


def place(d, x, y, w, h, inner, align="TOP_LEFT"):
    d.pos(x, y, w, h, d.box(w, h, align=ALIGN[align], inner=inner))


# ---------- 渐变 / 光 ----------
def radial_disc(d, x, y, size, colors, radius="0.5", ring=False, hole=0.0):
    """RADIAL 渐变圆盘。gradientRadius 是 0~1 比例而非像素（探针踩坑）。"""
    cols = colors if isinstance(colors, str) else ",".join(colors)
    d.pos(x, y, size, size,
          d.box(size, size, radius=size / 2,
                grad='gradientType="RADIAL" gradientColors="%s" gradientRadius="%s"'
                     % (cols, radius)))
    if ring:
        s = size * hole
        d.pos(x + (size - s) / 2, y + (size - s) / 2, s, s,
              d.box(s, s, color=d.P["card"], radius=s / 2))


def sweep_disc(d, cx, cy, r, colors, hole=0.0, stops=None):
    """SWEEP 扫描渐变圆盘（角度制色环）；hole>0 时挖成活动环。"""
    grad = 'gradientType="SWEEP" gradientColors="%s" gradientCenter="CENTER"' % (
        ",".join(colors),)
    if stops:
        grad += ' gradientStops="%s"' % stops
    d.pos(cx - r, cy - r, r * 2, r * 2, d.box(r * 2, r * 2, radius=r, grad=grad))
    if hole > 0:
        rr = r * hole
        d.pos(cx - rr, cy - rr, rr * 2, rr * 2,
              d.box(rr * 2, rr * 2, color=d.P["card"], radius=rr))


def lerp_colors(colors, t):
    ps = [c.lstrip("#") for c in colors]
    n_ = len(ps) - 1
    x = max(0.0, min(1.0, t)) * n_
    i = min(int(x), n_ - 1)
    f = x - i
    a = [int(ps[i][j:j + 2], 16) for j in (0, 2, 4)]
    b = [int(ps[i + 1][j:j + 2], 16) for j in (0, 2, 4)]
    return "#%02X%02X%02X" % tuple(round(a[k] + (b[k] - a[k]) * f) for k in range(3))


def glow(d, cx, cy, r, color, rings=10, a0=0.06):
    """同心圆柔光（不依赖滤镜）。"""
    for i in range(rings, 0, -1):
        rr = r * i / rings
        d.pos(cx - rr, cy - rr, rr * 2, rr * 2,
              d.box(rr * 2, rr * 2, color=hexa(color, a0 * (rings - i + 1)),
                    radius=rr))


# ---------- 几何 ----------
def polyline(d, pts, thickness, color):
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        d.line(x1, y1, x2, y2, thickness, color)


def arc(d, cx, cy, r, a0, a1, thickness, color, seg_deg=6.0):
    """旋转矩形段逼近圆弧（Snapshot 无 path 图元）。角度制，0=右，顺时针向下。"""
    step = (a1 - a0) / max(1, int(abs(a1 - a0) / seg_deg + 0.5))
    i = 0
    while (step > 0 and a0 + step * i < a1) or (step < 0 and a0 + step * i > a1):
        b0 = a0 + step * i
        b1 = b0 + step
        m = math.radians((b0 + b1) / 2)
        x, y = cx + r * math.cos(m), cy + r * math.sin(m)
        chord = 2 * r * math.sin(math.radians(abs(step) / 2)) + thickness * 0.75
        co, si = math.cos(m + math.pi / 2), math.sin(m + math.pi / 2)
        seg = (f'<Transform matrix="({co:.6f},{-si:.6f},0,0,{si:.6f},{co:.6f},0,0,'
               f'0,0,1,0,0,0,0,1)" alignment="TOP_LEFT">'
               + d.box(chord, thickness, color=color, radius=thickness / 2)
               + "</Transform>")
        d.pos(x - chord / 2, y - thickness / 2, chord, thickness, seg)
        i += 1


def donut(d, cx, cy, r, w, slices, start=-90.0, gap_deg=0.0):
    total = float(sum(v for v, _ in slices)) or 1.0
    a = start
    for v, col in slices:
        b = a + 360.0 * v / total
        arc(d, cx, cy, r, a + gap_deg / 2, b - gap_deg / 2, w, col)
        a = b


def waffle(d, x, y, cols, rows, cell, gap, filled, on, off, total=None):
    for i in range(cols * rows if total is None else total):
        c, r = i % cols, i // cols
        d.rect(x + c * (cell + gap), y + r * (cell + gap), cell, cell,
               on if i < filled else off, radius=cell * 0.28)


def bars_h(d, x, y, w_label, w_max, rows, h=34, gap=10, unit="",
           label_size=20, value_size=20, colors=None, track=None):
    """rows = [(标签, 值, 最大值)]，返回总高。"""
    track = track or d.P["row"]
    cy = y
    for i, (lab, val, mx) in enumerate(rows):
        col = (colors[i % len(colors)] if colors else d.P["cyan"])
        bw = w_max * max(0.0, min(1.0, float(val) / float(mx or 1)))
        d.label(x, cy, w_label, h, lab, d.P["t1"], label_size)
        d.rect(x + w_label + 10, cy + h * 0.2, w_max, h * 0.6, track, radius=4)
        if bw > 1:
            d.rect(x + w_label + 10, cy + h * 0.2, bw, h * 0.6, col, radius=4)
        d.label(x + w_label + 10 + w_max + 12, cy, 130, h, "%g%s" % (val, unit),
                d.P["t0"], value_size, align="END")
        cy += h + gap
    return cy - y


# ---------- 文本效果 ----------
def neon(d, x, y, w, h, s, size, color=None, shadow=None, align="START",
         style="BOLD", valign="CENTER"):
    color = color or d.P["t0"]
    shadow = shadow or ("5 6 0 %s,-5 -4 0 %s,0 0 18 #FFFFFF66"
                        % (hexa(d.P["cyan"], 0.75), hexa(d.P["pink"], 0.55)))
    place(d, x, y, w, h, T(s, d.font, color=color, fontSize=size,
                           fontStyle=style, textShadow=shadow),
          align={"START": "TOP_LEFT", "CENTER": "CENTER", "END": "CENTER_RIGHT"}[align]
          if valign == "CENTER" else "TOP_LEFT")


def stroke(d, x, y, w, h, s, size, color, fill=None, sw=3, align="CENTER",
           style="BOLD", spacing=None):
    a = dict(color=color, fontSize=size, fontStyle=style,
             foregroundColor=color)
    if fill:
        a.update(color=fill, foregroundMode="STROKE_AND_FILL",
                 foregroundStrokeWidth=sw)
    else:
        a.update(foregroundMode="STROKE", foregroundStrokeWidth=sw)
    if spacing:
        a["letterSpacing"] = spacing
    place(d, x, y, w, h, T(s, d.font, **a), align=align)


def frosted(d, x, y, w, h, radius=18, sigma=16, tint="#FFFFFF26",
            border="#FFFFFF55", content=None):
    d.pos(x, y, w, h,
          f'<ClipRRect borderRadius="{radius}" clipBehavior="ANTI_ALIAS">'
          f'<BackdropFilter sigmaX="{sigma}" sigmaY="{sigma}" tileMode="CLAMP">'
          + d.box(w, h, color=tint) + "</BackdropFilter></ClipRRect>")
    d.pos(x, y, w, h, d.box(w, h, radius=radius, border="1 SOLID %s" % border,
                            inner=content))


def rotated(d, x, y, w, h, deg, inner, align="TOP_LEFT"):
    co, si = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    seg = (f'<Transform matrix="({co:.4f},{si:.4f},0,0,{-si:.4f},{co:.4f},0,0,'
           f'0,0,1,0,0,0,0,1)" alignment="TOP_LEFT">' + inner + "</Transform>")
    d.pos(x, y, w, h, seg)


def rich(d, x, y, w, h, spans, base_size=22, base_color=None,
         align="TOP_LEFT", maxlines=None, spacing=None):
    """spans = [(文本, {DSL 属性})]；空 dict 表示继承。"""
    base_color = base_color or d.P["t0"]
    body = ""
    for s, a in spans:
        if not a:
            body += s
            continue
        at = "".join(' %s="%s"' % (k, v) for k, v in a.items())
        body += "<Text%s>%s</Text>" % (at, s)
    attrs = dict(color=base_color, fontSize=base_size)
    if maxlines:
        attrs["maxLines"] = maxlines
    if spacing:
        attrs["letterSpacing"] = spacing
    place(d, x, y, w, h, T(body, d.font, **attrs), align=align)


# ---------- 表格 ----------
def table(d, x, y, widths, row_h, rows, header=None, fs=None, aligns=None,
          cell_colors=None, zebra=True, pad=12, header_color=None):
    tw = float(sum(widths))
    cy = y
    header_color = header_color or d.P["t2"]
    fs = fs or [20] * len(widths)
    aligns = aligns or ["START"] * len(widths)
    if header:
        d.rect(x, cy, tw, row_h, d.P["card2"])
        cx = x
        for i, htxt in enumerate(header):
            d.label(cx + pad, cy, widths[i] - 2 * pad, row_h, htxt,
                    header_color, max(16, fs[i] - 2), "BOLD", align=aligns[i])
            cx += widths[i]
        cy += row_h
    for r, row in enumerate(rows):
        if zebra and r % 2 == 0:
            d.rect(x, cy, tw, row_h, d.P["row"])
        cx = x
        for i, cell in enumerate(row):
            col = d.P["t0"]
            if cell_colors and cell_colors[r] and cell_colors[r][i]:
                col = cell_colors[r][i]
            d.label(cx + pad, cy, widths[i] - 2 * pad, row_h, str(cell), col,
                    fs[i], align=aligns[i])
            cx += widths[i]
        d.line(x, cy + row_h, x + tw, cy + row_h, 1, d.P["border"])
        cy += row_h
    return cy - y


def section_title(d, x, y, w, s, sub=None, color=None):
    color = color or d.P["t0"]
    d.label(x, y, w, 30, s, color, 24, "BOLD")
    if sub:
        d.label(x, y + 30, w, 24, sub, d.P["t2"], 18)


def card(d, x, y, w, h, title=None, sub=None, pad=20, radius=14, color=None,
         border=None, shadow=None):
    d.pos(x, y, w, h, d.box(w, h, color=color or d.P["card"], radius=radius,
                            border=border if border is not None
                            else "1 SOLID %s" % d.P["border"], shadow=shadow))
    if title:
        d.label(x + pad, y + pad - 2, w - 2 * pad, 30, title, d.P["t0"], 22, "BOLD")
    if sub:
        d.label(x + pad, y + pad + 28, w - 2 * pad, 24, sub, d.P["t2"], 17)
    return (x + pad, y + pad + (60 if (title or sub) else 0), w - 2 * pad)
