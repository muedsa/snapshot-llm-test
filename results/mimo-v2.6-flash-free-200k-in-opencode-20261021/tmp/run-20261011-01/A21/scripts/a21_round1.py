# -*- coding: utf-8 -*-
"""A21 round-01 layout engine + DSL emitter.

Two distinct compositions sharing one identity (primary colour, type scale,
5 brand constructs):
  portrait 1080x1350 — stacked vertical rhythm
  wide      1440x810 — left column + right stage

Round-01 leaves a real usable top zone (wordmark band) and a real bottom zone
(info band) reserved by the vertical rhythm, but writes NO placeholder text in
them. Content rendered in round 1 is only the mandatory strings.

Usage (launch base = suite root):
  python tmp/run-20261011-01/A21/scripts/a21_round1.py
"""
import json
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import a21_identity as I  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[4]
GEN = ROOT / "tmp/run-20261011-01/A21/round-01"


def fmt(v):
    s = ("%.4f" % float(v)).rstrip("0").rstrip(".")
    return s if s not in ("", "-0") else "0"


def col(name):
    return getattr(I, name) if hasattr(I, name) else name


# ------------------------------------------------------------------ elements
def rect(l, t, w, h, color, radius=0, border=None):
    b = (' border="%s"' % border) if border else ""
    return ('<Positioned left="%s" top="%s" width="%s" height="%s">'
            '<Container width="%s" height="%s" color="%s" borderRadius="%s"%s/>'
            '</Positioned>'
            % (fmt(l), fmt(t), fmt(w), fmt(h), fmt(w), fmt(h), color,
               fmt(radius), b))


def line_el(p1, p2, width, color):
    x1, y1 = p1
    x2, y2 = p2
    length = math.hypot(x2 - x1, y2 - y1)
    th = math.atan2(y2 - y1, x2 - x1)
    c, s = math.cos(th), math.sin(th)
    m = "(%s,%s,0,0,%s,%s,0,0,0,0,1,0,0,0,0,1)" % (
        fmt(c), fmt(s), fmt(-s), fmt(c))
    return ('<Positioned left="%s" top="%s" width="%s" height="%s">'
            '<Transform matrix="%s" origin="(0,0)" alignment="TOP_LEFT">'
            '<Container width="%s" height="%s" color="%s" borderRadius="%s"/>'
            '</Transform></Positioned>'
            % (fmt(x1), fmt(y1), fmt(length), fmt(width), m,
               fmt(length), fmt(width), color, fmt(width / 2)))


def text_el(l, t, w, h, text, size, color, weight="NORMAL", align="LEFT",
            line=None):
    style = ' fontStyle="BOLD"' if weight == "BOLD" else ""
    lh = ' lineHeight="%s"' % fmt(line) if line else ""
    return ('<Positioned left="%s" top="%s" width="%s" height="%s">'
            '<Text fontSize="%s" fontFamily="%s" color="%s" textAlign="%s"%s%s'
            ' text="%s"/></Positioned>'
            % (fmt(l), fmt(t), fmt(w), fmt(h), fmt(size), I.FONT, color,
               align, style, lh, text))


def prism_mark(cx, top, scale, opacity_step=0.16, base=I.PRIMARY):
    """Brand construct 1+2: stacked-light bars + beam wedge.

    Returns (elements, total_height). Bars thin out/lighten downward; a beam
    wedge leaves the mark to the lower-right.
    """
    els = []
    bar_h = 13 * scale
    gap = 9 * scale
    widths = [150, 132, 114, 96, 78]
    n = len(widths)
    y = top
    for i, bw in enumerate(widths):
        w = bw * scale
        # opacity via a tint blend toward paper: darker bars on top
        shade = _blend(base, I.PAPER, opacity_step * i)
        els.append(rect(cx, y, w, bar_h, shade, radius=bar_h / 2))
        y += bar_h + gap
    total = y - gap - top
    # beam wedge (construct 2): a symmetric diamond of light leaving the mark
    # to the lower-right, kept fully inside the safe margin.
    bw2 = 70 * scale
    bx = cx + 150 * scale + 18 * scale
    by = top + total * 0.5 - bw2 * 0.75
    els.append(_wedge(bx, by, bw2, bw2 * 1.5,
                      _blend(base, I.PAPER, 0.55)))
    return els, total


def _wedge(x, y, w, h, color):
    """Symmetric diamond of light (pure geometry, no image).

    Built from stacked bars whose length peaks at the vertical centre then
    shrinks, so the silhouette is a diamond/rhombus — the "beam" construct.
    """
    els = []
    steps = 9
    for k in range(steps):
        frac = k / (steps - 1.0)
        seg_h = h / steps
        # diamond: length peaks at middle, tapers to both tips
        taper = 1.0 - abs(frac - 0.5) * 2.0
        seg_w = 8 + (w - 8) * taper
        els.append(rect(x + (w - seg_w) / 2, y + frac * h, seg_w,
                        seg_h * 1.15, color, radius=seg_h * 0.5))
    return "".join(els)


def _blend(hexc, tohex, t):
    t = max(0.0, min(1.0, t))
    a = _rgb(hexc)
    b = _rgb(tohex)
    m = [round(a[i] + (b[i] - a[i]) * t) for i in range(3)]
    return "#%02X%02X%02X" % tuple(m)


def _rgb(h):
    h = h.lstrip("#")
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def baseline_rule(l, t, w, color=I.MUTED_LINE, thick=2):
    """Brand construct 3."""
    return rect(l, t, w, thick, color, radius=thick / 2)


def tagline_pill(l, t, text, size, pad_x=26, pad_y=16):
    """Brand construct 4: tagline on a soft tinted pill."""
    tw = I.measure(text, size)
    w = tw + pad_x * 2
    h = size * 1.3 + pad_y * 2
    els = [rect(l, t, w, h, col("PRIMARY_TINT"), radius=h / 2,
                border="2 SOLID %s" % col("PRIMARY"))]
    els.append(text_el(l + pad_x, t + pad_y - 2, tw + 8, size * 1.3, text,
                       size, col("INK"), weight="BOLD"))
    return "".join(els), w, h


def info_plate(l, t, w, label, value, size, label_size=24):
    """Brand construct 5: label + value on one tinted plate style."""
    h = label_size * 1.3 + size * 1.25 + 34
    els = [rect(l, t, w, h, col("SURFACE"), radius=16,
                border="2 SOLID %s" % col("MUTED_LINE"))]
    els.append(rect(l, t + 16, 5, h - 32, col("PRIMARY"), radius=2.5))
    els.append(text_el(l + 22, t + 14, w - 40, label_size * 1.3, label,
                       label_size, col("PRIMARY"), weight="BOLD"))
    els.append(text_el(l + 22, t + 14 + label_size * 1.3 + 4, w - 40,
                       size * 1.25, value, size, col("INK"), weight="BOLD"))
    return "".join(els), h


# --------------------------------------------------------------- composition
def build_portrait():
    W, H = I.SIZES["portrait"]
    els = []
    els.append(rect(0, 0, W, H, col("PAPER")))
    # soft brand glow band top (real top zone, usable, no placeholder text)
    els.append(rect(0, 0, W, 300, _blend(col("PRIMARY"), I.PAPER, 0.90)))

    M = 96
    y = 120
    # wordmark (top zone, real content)
    els.append(text_el(M, y, 500, 54, I.BRAND_CN, 40, col("INK"), weight="BOLD"))
    els.append(text_el(M, y + 52, 500, 34, I.BRAND_EN, 26, col("PRIMARY"),
                       weight="BOLD"))
    # prism mark top-right
    pm, pmh = prism_mark(W - M - 150, 118, 1.0)
    els.extend(pm)

    y = 300
    # eyebrow
    els.append(text_el(M, y, 600, 32, I.REQUIRED["kicker"], 24,
                       col("PRIMARY"), weight="BOLD"))
    # rule under eyebrow (construct 3)
    els.append(baseline_rule(M, y + 44, W - 2 * M))
    y += 74

    # main title (tagline is the headline in round 1) — huge
    title = I.REQUIRED["tagline"]
    tl = I.wrap(title, 60, W - 2 * M)
    th = I.text_h(len(tl), 60, 1.14)
    for i, ln in enumerate(tl):
        els.append(text_el(M, y + i * 60 * 1.14, W - 2 * M, 70, ln, 60,
                           col("INK"), weight="BOLD"))
    y += th + 20

    # tagline pill (construct 4) — real brand line
    pill, pw, ph = tagline_pill(M, y, "叠光 Layerlight · 结构化呈现", 26)
    els.append(pill)
    y += ph + 30

    # divider
    els.append(baseline_rule(M, y, W - 2 * M))
    y += 34

    # info plates (construct 5) — the three mandatory info rows
    plate_w = W - 2 * M
    p1, h1 = info_plate(M, y, plate_w, "时间", I.REQUIRED["datetime"], 34)
    els.append(p1)
    y += h1 + 20
    p2, h2 = info_plate(M, y, plate_w, "讲者", I.REQUIRED["speakers"], 30)
    els.append(p2)
    y += h2 + 20
    p3, h3 = info_plate(M, y, plate_w, "参与网址", I.REQUIRED["url"], 26)
    els.append(p3)
    y += h3

    # BOTTOM ZONE: reserved real usable space (rhythm leaves it open on the
    # paper band) — deliberately no placeholder text here in round 1.
    bottom_zone_top = y + 40
    return els, W, H, bottom_zone_top


def build_wide():
    W, H = I.SIZES["wide"]
    els = []
    els.append(rect(0, 0, W, H, col("PAPER")))
    # left tinted column (brand stage)
    col_w = 560
    els.append(rect(0, 0, col_w, H, _blend(col("PRIMARY"), I.PAPER, 0.90)))

    M = 72
    # left column: wordmark + prism + tagline pill
    els.append(text_el(M, 96, 420, 52, I.BRAND_CN, 40, col("INK"), weight="BOLD"))
    els.append(text_el(M, 148, 420, 34, I.BRAND_EN, 26, col("PRIMARY"),
                       weight="BOLD"))
    pm, pmh = prism_mark(M, 236, 1.12)
    els.extend(pm)
    pill, pw, ph = tagline_pill(M, 236 + pmh + 40, I.REQUIRED["tagline"], 30)
    els.append(pill)

    # right side content
    RX = col_w + 80
    RW = W - RX - M
    y = 118
    els.append(text_el(RX, y, RW, 32, I.REQUIRED["kicker"], 24,
                       col("PRIMARY"), weight="BOLD"))
    els.append(baseline_rule(RX, y + 44, RW))
    y += 80

    # the mandatory tagline IS the headline here (dominant, not a small pill)
    title = I.REQUIRED["tagline"]
    tl = I.wrap(title, 64, RW)
    for i, ln in enumerate(tl):
        els.append(text_el(RX, y + i * 64 * 1.16, RW, 78, ln, 64,
                           col("INK"), weight="BOLD"))
    y += I.text_h(len(tl), 64, 1.16) + 18

    # brand-promise pill (construct 4) — real brand line, not placeholder
    pill, pw, ph = tagline_pill(RX, y, "叠光 Layerlight · 结构化呈现", 26)
    els.append(pill)
    y += ph + 22

    els.append(baseline_rule(RX, y, RW))
    y += 34

    plate_w = RW
    p1, h1 = info_plate(RX, y, plate_w, "时间", I.REQUIRED["datetime"], 34)
    els.append(p1)
    y += h1 + 20
    p2, h2 = info_plate(RX, y, plate_w, "讲者", I.REQUIRED["speakers"], 30)
    els.append(p2)
    y += h2 + 20
    p3, h3 = info_plate(RX, y, plate_w, "参与网址", I.REQUIRED["url"], 26)
    els.append(p3)
    y += h3

    bottom_zone_top = y + 30
    return els, W, H, bottom_zone_top


def emit(parts, W, H):
    return ('<Snapshot type="png" background="%s">'
            '<SizedBox width="%d" height="%d">'
            '<Stack alignment="TOP_LEFT" clipBehavior="NONE">%s'
            '</Stack></SizedBox></Snapshot>'
            % (col("PAPER"), W, H, "".join(parts)))


def main():
    GEN.mkdir(parents=True, exist_ok=True)
    out = {}
    for name, builder in (("launch-portrait", build_portrait),
                          ("launch-wide", build_wide)):
        parts, W, H, bz = builder()
        dsl = emit(parts, W, H)
        (GEN / (name + ".snapshot")).write_text(dsl, encoding="utf-8")
        out[name] = {"w": W, "h": H, "bottom_zone_top": round(bz, 1),
                     "bytes": len(dsl.encode("utf-8"))}
        print("%s: %dx%d, %d bytes, bottom-zone top y=%d"
              % (name, W, H, out[name]["bytes"], bz))
    (GEN / "round1-geom.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
