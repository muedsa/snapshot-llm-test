"""Shared visual system for the ten Kelpline (B05) screens.

One product = one design language: hull navy surfaces, chart-paper light surfaces,
teal for "go", amber for "watch", red for "stop", and the tide curve used at four
different scales as the product's signature mark.
"""
from __future__ import annotations

import math

from bkit import Doc, CJK, MONO, INTER, tw

# ------------------------------------------------------------------ palette
NAVY = "#0B1B2BFF"
NAVY2 = "#10243AFF"
NAVY3 = "#17304AFF"
DARKLINE = "#27435FFF"
INK = "#0F172AFF"
INK2 = "#1E293BFF"
MUTED = "#64748BFF"
SLATE = "#94A3B8FF"
PAPER = "#F4F1EAFF"
LIGHT = "#F1F5F9FF"
WHITE = "#FFFFFFFF"
LINE = "#E2E8F0FF"
LINE2 = "#CBD5E1FF"
TEAL = "#0E9F8FFF"
TEAL_D = "#0B7A6EFF"
TEAL_L = "#5EEAD4FF"
AMBER = "#D97706FF"
AMBER_L = "#FCD34DFF"
RED = "#D92D20FF"
RED_L = "#FCA5A5FF"
BLUE = "#1D4ED8FF"
SKY = "#38BDF8FF"
GREEN = "#16A34AFF"


def clock(t: float) -> str:
    t = t % 24
    h = int(t)
    m = int(round((t - h) * 60))
    if m == 60:
        h, m = h + 1, 0
    return f"{h:02d}:{m:02d}"


# ------------------------------------------------------------------ surfaces
def status_bar(d: Doc, w: int, title: str, right: str, color=SLATE, bg=None, y=0, h=54):
    if bg:
        d.box(0, y, w, h, bg)
    d.text(28, y + 14, title, 20, color, "BOLD", MONO)
    d.rtext(w - 28, y + 14, 26, right, 18, color, weight="NORMAL")


def header(d: Doc, w: int, title: str, sub: str, right_lines, h=112, bg=NAVY,
           accent=TEAL, title_color=WHITE):
    d.box(0, 0, w, h, bg)
    d.box(0, h - 4, w, 4, accent)
    d.text(40, 26, title, 34, title_color, "BOLD", CJK)
    if sub:
        d.text(40, h - 40, sub, 20, SLATE, "NORMAL", CJK)
    yy = 26
    for i, (txt, col, size, weight) in enumerate(right_lines):
        d.rtext(w - 40, yy, 30, txt, size, col, weight=weight)
        yy += 30


def footer(d: Doc, w: int, h: int, left: str, right: str, bg=NAVY, color=SLATE, y=None):
    y = h - 56 if y is None else y
    d.box(0, y, w, h - y, bg)
    d.text(40, y + 18, left, 18, color, "NORMAL", CJK)
    d.rtext(w - 40, y + 18, 24, right, 18, color)


def panel(d: Doc, x, y, w, h, fill=WHITE, border=None, radius=14, shadow=None):
    d.box(x, y, w, h, fill, radius=radius,
          border=border or f"1 SOLID {LINE}", shadow=shadow)
    return d


def section_label(d: Doc, x, y, s, color=MUTED, size=18, w=None):
    d.text(x, y, s.upper(), size, color, "BOLD", INTER, spacing=2)


def key_value(d: Doc, x, y, w, label, value, size=20, label_color=MUTED,
              value_color=INK, gap=0, family_val=CJK, weight_val="BOLD"):
    d.text(x, y, label, size, label_color, "NORMAL", CJK)
    d.rtext(x + w, y, 26, value, size, value_color, weight=weight_val, family=family_val)


def chip(d: Doc, x, y, w, h, label, value, color, fill=None, value_size=22, label_size=15):
    fill = fill or WHITE
    d.box(x, y, w, h, fill, radius=10, border=f"1 SOLID {LINE}")
    d.box(x, y, 5, h, color, tl=10, bl=10)
    d.text(x + 16, y + 10, label.upper(), label_size, MUTED, "BOLD", INTER, spacing=1)
    d.text(x + 16, y + h - 34, value, value_size, color, "BOLD", CJK)


def pill(d: Doc, x, y, text, color, size=17, pad=14, h=30, fill=None):
    w = tw(text, size, INTER) + pad * 2
    d.box(x, y, w, h, fill or WHITE, radius=h / 2, border=f"1 SOLID {color}")
    d.tbox(x, y, w, h, text, size, color, "CENTER", "BOLD", INTER)
    return w


def dot(d: Doc, cx, cy, r, color):
    d.circle(cx, cy, r, color)


# ------------------------------------------------------------------ tide chart
def tide_chart(d: Doc, x, y, w, h, curve, t0=0.0, t1=24.0, hmin=0.0, hmax=4.5,
               line=SKY, fill="#38BDF826", gates=None, gate_fill="#0E9F8F22",
               gate_label=TEAL_L, marks=None, vlines=None, grid_color="#1E3A57FF",
               label_color=SLATE, axis_label_size=16, grid=True, thickness=4.5,
               h_lines=1.0, t_step=2, fill_cols=True, watermark=None):
    """Tide height against time. curve: [{'t':hours,'h':metres}, ...]."""
    def X(t):
        return x + (t - t0) / (t1 - t0) * w

    def Y(hh):
        return y + h - (hh - hmin) / (hmax - hmin) * h

    if gates:
        for g in gates:
            gx0, gx1 = max(x, X(g["from_t"])), min(x + w, X(g["to_t"]))
            if gx1 > gx0:
                d.box(gx0, y, gx1 - gx0, h, gate_fill)
    if grid:
        hh = hmin
        while hh <= hmax + 1e-6:
            d.box(x, Y(hh) - 0.5, w, 1, grid_color)
            d.rtext(x - 12, Y(hh) - 11, 22, f"{hh:.0f}", axis_label_size, label_color, pad=4)
            hh += h_lines
    if fill_cols:
        step = 6
        cols = int(w / step) + 1
        for i in range(cols):
            t = t0 + (t1 - t0) * i / (cols - 1)
            hh = sample(curve, t)
            top = Y(hh)
            if Y(hmin) - top > 1:
                d.box(x + i * step, top, step, Y(hmin) - top, fill)
    pts = [(X(s["t"]), Y(s["h"])) for s in curve if t0 - 0.01 <= s["t"] <= t1 + 0.01]
    if pts:
        d.poly(pts, line, thickness)
    if grid:
        t = math.ceil(t0 / t_step) * t_step
        while t <= t1 + 1e-6:
            d.box(X(t) - 0.5, y, 1, h + 8, grid_color)
            d.ctext(X(t), y + h + 10, 22, f"{int(t):02d}", axis_label_size, label_color, pad=6)
            t += t_step
    if vlines:
        for v in vlines:
            vx = X(v["t"])
            if v.get("dash"):
                d.dash(vx, y, vx, y + h, v["color"], 2, 9, 7)
            else:
                d.box(vx - 1.5, y, 3, h, v["color"])
            if v.get("label"):
                lw = tw(v["label"], 16, INTER) + 16
                lx = min(max(x, vx - lw / 2), x + w - lw)
                d.box(lx, y - 26, lw, 24, v.get("lfill", v["color"]), radius=6)
                d.tbox(lx, y - 26, lw, 24, v["label"], 15, v.get("lcolor", WHITE),
                       "CENTER", "BOLD", INTER)
    if marks:
        for m in marks:
            mx, my = X(m["t"]), Y(m["h"])
            d.circle(mx, my, m.get("r", 8), m.get("fill", WHITE), border=f"3 SOLID {m['color']}")
            if m.get("label"):
                lw = tw(m["label"], 17, INTER) + 18
                lx = min(max(x - 6, mx - lw / 2), x + w - lw + 6)
                ly = my + m.get("dy", -34)
                d.box(lx, ly, lw, 26, NAVY, radius=6, border=f"1 SOLID {m['color']}")
                d.tbox(lx, ly, lw, 26, m["label"], 16, m["color"], "CENTER", "BOLD", INTER)
    if watermark:
        d.text(x + 8, y + 8, watermark, 15, label_color, "BOLD", INTER, spacing=2)
    return d


def sample(curve, t):
    """Linear interpolation of the tide curve at hour t."""
    if t <= curve[0]["t"]:
        return curve[0]["h"]
    if t >= curve[-1]["t"]:
        return curve[-1]["h"]
    lo, hi = 0, len(curve) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if curve[mid]["t"] <= t:
            lo = mid
        else:
            hi = mid
    a, b = curve[lo], curve[hi]
    f = (t - a["t"]) / (b["t"] - a["t"])
    return a["h"] + f * (b["h"] - a["h"])


def sparkline(d: Doc, x, y, w, h, curve, t0, t1, hmin, hmax, color, thickness=3):
    pts = []
    n = 60
    for i in range(n + 1):
        t = t0 + (t1 - t0) * i / n
        hh = sample(curve, t)
        pts.append((x + w * i / n, y + h - (hh - hmin) / (hmax - hmin) * h))
    d.poly(pts, color, thickness)
    return d


# ------------------------------------------------------------------ instrument bits
def compass_tape(d: Doc, x, y, w, h, heading, colors=None):
    """Horizontal compass ribbon: 1 deg = 3 px, ticks every 5 deg, labels every 30."""
    ppd = 3.0
    cx = x + w / 2
    d.box(x, y, w, h, colors or NAVY2)
    start = int(heading - (w / 2) / ppd) - 2
    end = int(heading + (w / 2) / ppd) + 2
    for deg in range(start, end + 1):
        px = cx + (deg - heading) * ppd
        if px < x - 2 or px > x + w + 2:
            continue
        dd = deg % 360
        if dd % 30 == 0:
            d.box(px - 1, y + h - 34, 2, 22, SLATE)
            lbl = {0: "N", 90: "E", 180: "S", 270: "W"}.get(dd, f"{dd:03d}")
            d.ctext(px, y + 8, 24, lbl, 17, WHITE if dd % 90 == 0 else SLATE, "BOLD", MONO, pad=8)
        elif dd % 10 == 0:
            d.box(px - 1, y + h - 24, 2, 14, "#3E5A78FF")
        elif dd % 5 == 0:
            d.box(px - 1, y + h - 18, 2, 9, "#2C4560FF")
    d.box(cx - 3, y, 6, h, AMBER_L)
    return d


def bar(d: Doc, x, y, w, h, frac, color, track="#E2E8F0FF", radius=None):
    radius = h / 2 if radius is None else radius
    d.box(x, y, w, h, track, radius=radius)
    if frac > 0.001:
        d.box(x, y, max(h, w * min(1.0, frac)), h, color, radius=radius)
    return d


def range_arc(d: Doc, cx, cy, rmax, rings, color=TEAL, label_color=MUTED):
    """Semicircle range rings above the centre point."""
    for frac, lbl in rings:
        d.arc(cx, cy, rmax * frac, 180, 360, color, 1.5)
    return d


def fill_poly(d: Doc, pts, color, step=6):
    """Even-odd scanline fill, so map landmasses are real filled areas built from
    DSL rectangles rather than an embedded image."""
    ys = [p[1] for p in pts]
    y0, y1 = min(ys), max(ys)
    y = y0
    while y <= y1:
        xs = []
        n = len(pts)
        for i in range(n):
            x1, y1_ = pts[i]
            x2, y2_ = pts[(i + 1) % n]
            if (y1_ <= y < y2_) or (y2_ <= y < y1_):
                t = (y - y1_) / (y2_ - y1_)
                xs.append(x1 + t * (x2 - x1))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            if xs[i + 1] - xs[i] > 0.5:
                d.box(xs[i], y, xs[i + 1] - xs[i], step, color)
        y += step
    return d


def projector(bounds, x, y, w, h):
    """Equirectangular lat/lon -> canvas pixels for a small chart sketch."""
    lat0, lat1, lon0, lon1 = bounds
    kx = math.cos(math.radians((lat0 + lat1) / 2))

    def P(lat, lon):
        px = x + (lon - lon0) / (lon1 - lon0) * w
        py = y + (lat1 - lat) / (lat1 - lat0) * h
        return px, py
    P.kx = kx
    return P


def sea_grid(d: Doc, x, y, w, h, bounds, color="#1E3A57FF", step_min=5, label=None,
             label_color=None):
    """Lat/lon graticule for a chart sketch."""
    lat0, lat1, lon0, lon1 = bounds
    P = projector(bounds, x, y, w, h)
    la = math.ceil(lat0 * 60 / step_min) * step_min / 60
    while la < lat1:
        _, py = P(la, lon0)
        d.box(x, py, w, 1, color)
        if label:
            d.text(x + 6, py + 3, f"{int(la)}°{int(round((la-int(la))*60)):02d}'", 12,
                   label_color or color, "NORMAL", MONO)
        la += step_min / 60
    lo = math.ceil(lon0 * 60 / step_min) * step_min / 60
    while lo < lon1:
        px, _ = P(lat0, lo)
        d.box(px, y, 1, h, color)
        lo += step_min / 60
    return P


def north_arrow(d: Doc, cx, cy, size, color=WHITE, label=True):
    d.seg(cx, cy + size / 2, cx, cy - size / 2, color, 2)
    d.seg(cx, cy - size / 2, cx - size * 0.22, cy - size * 0.2, color, 2)
    d.seg(cx, cy - size / 2, cx + size * 0.22, cy - size * 0.2, color, 2)
    d.ctext(cx, cy - size / 2 - 26, 22, "N", 18, color, "BOLD", INTER, pad=8)
    return d


def scale_bar(d: Doc, x, y, px_per_nm, color="#0F172AFF", label_color=None, nm=1.0):
    n = 4
    seg_w = px_per_nm * nm / n
    for i in range(n):
        d.box(x + i * seg_w, y, seg_w, 8, color if i % 2 == 0 else "#FFFFFF00",
              border=f"1 SOLID {color}")
    d.text(x, y + 14, "0", 14, label_color or color, "NORMAL", MONO)
    d.rtext(x + px_per_nm * nm, y + 14, 20, f"{nm:g} nm", 14, label_color or color)
    return d
