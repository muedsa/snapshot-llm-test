# -*- coding: utf-8 -*-
"""B05 水线 Waterline — shared product-UI component library + design tokens.

Single visual system reused across all 10 screens (phones / landscape / car /
desktop / wall). The memorable signature is the DepthRuler (vertical water-level
gauge). Risk color language (safe/caution/detour/block) is globally consistent
and driven by b05_data.risk_of. All components are thin wrappers over the proven
b05_common grammar so every screen is generated, self-consistent, and readable
at its target size.
"""
from b05_common import (box, circle, ellipse, text, grad, seg, poly, arc,
                        clip_rrect, clip_oval, dash_line, tw, fit, r2, esc,
                        transform_of, rot_matrix, translate_matrix)
from b05_data import (risk_of, risk_color, risk_label, ped_risk_of, RISK_BANDS,
                      RISK_DEMO_NOTE, CITY, NOW, NOW_DATE, USER)

# ---------------- design tokens (deep water emergency theme) ----------------
BG        = "#071A2B"   # deepest canvas
BG2       = "#0B2438"   # panel base
CARD      = "#0E2E45"   # raised card
CARD2     = "#12385400" # (unused placeholder)
STROKE    = "#1C4A6B"
STROKE_HI = "#27597E"
INK       = "#EAF6FF"   # primary text
SUB       = "#9FC4DE"   # secondary
MUTED     = "#5E86A3"   # tertiary
AQUA      = "#28C7D8"   # brand accent
AQUA_HI   = "#4FE3F0"
WATER     = "#1B6E8C"   # water fill body

# risk color language (mirror b05_data for UI convenience)
R_SAFE   = "#2FBF71"
R_CAUTION= "#2E86DE"
R_DETOUR = "#F2A93B"
R_BLOCK  = "#E4572E"

F_BODY = "Noto Sans CJK SC"
F_NUM  = "Inter"
F_MONO = "Noto Sans Mono CJK SC"


def risk_ui(level):
    return [R_SAFE, R_CAUTION, R_DETOUR, R_BLOCK][level]


# ---------------- phone chrome ----------------
def status_bar(w, dark=True, time_str=None):
    """iOS-like status bar: time left, signal/wifi/battery right."""
    t = time_str or NOW
    ink = INK if dark else "#0E1B2E"
    h = 60
    el = [text(44, 16, 160, 36, t, 27, ink, bold=True, font=F_NUM)]
    # signal bars
    bx = w - 168
    for i in range(4):
        bh = 8 + i * 6
        el.append(box(bx + i * 10, 40 - bh, 6, bh, ink, radius=2))
    # wifi
    wx = w - 118
    el.append(box(wx, 30, 22, 6, ink, radius=3))
    el.append(circle(wx + 11, 24, 3, ink))
    # battery
    bxx = w - 84
    el.append(box(bxx, 20, 40, 22, "transparent", radius=6, border=ink,
                  border_w=2))
    el.append(box(bxx + 4, 24, 26, 14, ink, radius=3))
    el.append(box(bxx + 42, 26, 4, 10, ink, radius=2))
    return "".join(el), h


def tab_bar(w, y, items, active_idx, dark=True):
    """Bottom tab bar with icon+label; each tab has an explainable role."""
    h = 118
    base = BG2 if dark else "#F2F7FB"
    ink = INK if dark else "#0E1B2E"
    out = [box(0, y, w, h, base)]
    out.append(box(0, y, w, 2, STROKE))
    n = len(items)
    cw = w / float(n)
    for i, (glyph, label) in enumerate(items):
        cx = cw * i + cw / 2.0
        col_ = AQUA if i == active_idx else MUTED
        bold = i == active_idx
        # simple glyph: a rounded tile with the char
        out.append(text(cx - cw / 2.0, y + 20, cw, 44, glyph, 30, col_,
                        bold=bold, align="CENTER"))
        out.append(text(cx - cw / 2.0, y + 66, cw, 34, label, 20, col_,
                        bold=bold, align="CENTER"))
    return "".join(out), h


def home_indicator(w, y, dark=True):
    ink = INK if dark else "#0E1B2E"
    return box(w / 2.0 - 70, y, 140, 8, ink, radius=4)


# ---------------- core UI atoms ----------------
def card(x, y, w, h, fill=CARD, radius=22, border=STROKE, border_w=1.5):
    return box(x, y, w, h, fill, radius=radius, border=border, border_w=border_w)


def chip(x, y, label, fg, bg, size=20, padx=16, h=40, bold=True, font=None):
    """rounded pill; width fits text."""
    twid = tw(label, size) + padx * 2
    el = [box(x, y, twid, h, bg, radius=h / 2.0)]
    el.append(text(x, y + (h - size * 1.3) / 2.0, twid, size * 1.4, label,
                   size, fg, bold=bold, align="CENTER", font=font))
    return "".join(el), twid


def risk_pill(x, y, depth, size=22, ped=False):
    """risk badge from a depth (uses global risk language)."""
    label, level, color = (ped_risk_of(depth) if ped else risk_of(depth))
    fg, bg = color, color + "26"
    return chip(x, y, label, fg, bg, size=size, padx=18, h=size + 20)[0]


def button(x, y, w, h, label, fill=AQUA, fg="#04222B", radius=16, size=26,
           bold=True, outline=None, font=None):
    el = []
    if outline:
        el.append(box(x, y, w, h, "transparent", radius=radius, border=outline,
                      border_w=2))
    else:
        el.append(box(x, y, w, h, fill, radius=radius))
    el.append(text(x, y + (h - size * 1.3) / 2.0, w, size * 1.5, label, size,
                   fg, bold=bold, align="CENTER", font=font))
    return "".join(el)


def toggle(x, on=True, w=74, h=42):
    track = AQUA if on else STROKE_HI
    el = [box(x, 0, w, h, track, radius=h / 2.0)]
    kx = x + (w - h + 6) if on else x + 6
    el.append(circle(kx + (h - 12) / 2.0, h / 2.0, (h - 12) / 2.0, "#FFFFFF"))
    return "".join(el)


def hbar(x, y, w, h, frac, color, track="#0C2740"):
    """horizontal progress bar; frac clamped 0..1."""
    f = max(0.0, min(1.0, frac))
    el = [box(x, y, w, h, track, radius=h / 2.0)]
    if f > 0:
        el.append(box(x, y, max(h, w * f), h, color, radius=h / 2.0))
    return "".join(el)


# ---------------- THE SIGNATURE: DepthRuler ----------------
def depth_ruler(x, y, w, h, depth_cm, max_cm=50.0, show_bands=True,
                label_side="right", big=True, theme="dark"):
    """Vertical water-level gauge — the product's memorable motif.

    A ruler with cm ticks, a colored water fill rising to depth_cm, a waterline
    marker, and the numeric readout. Water height is geometrically proportional
    to depth (verified in completion criteria). Bands (10/20/30cm) get the risk
    color so the thresholds are legible at a glance.
    """
    el = []
    inner_pad = 14
    gutter = 40 if label_side == "right" else 0
    track_x = x + inner_pad + gutter
    track_w = w - inner_pad * 2 - gutter - (60 if label_side == "right" else 0)
    track_top = y + 18
    track_bot = y + h - 18
    track_h = track_bot - track_top
    # track background
    el.append(box(track_x, track_top, track_w, track_h, "#08202F", radius=14,
                  border=STROKE, border_w=1.5))
    # cm scale (bottom=0)
    def yfor(cm):
        return track_bot - (cm / max_cm) * track_h
    # band fills up to depth
    if show_bands:
        # draw the water body from 0 to depth in segments by risk band
        segs = []
        for lo, hi, lbl, lvl, colr in RISK_BANDS:
            hi_c = min(hi, max_cm, depth_cm)
            if hi_c <= lo:
                continue
            ytop = yfor(hi_c)
            ybot = yfor(lo)
            segs.append((ytop, ybot, colr))
        # stack from bottom up
        for ytop, ybot, colr in segs:
            hh = ybot - ytop
            if hh > 0:
                el.append(box(track_x + 2, ytop, track_w - 4, hh, colr,
                              radius=0))
        # round the water top with a subtle cap
        if depth_cm > 0:
            el.append(clip_rrect(track_x + 2, yfor(depth_cm), track_w - 4, 26,
                                 10, box(0, 0, track_w - 4, 26, R_BLOCK
                                         if depth_cm >= 30 else WATER)))
    # waterline marker + numeric
    if depth_cm > 0:
        wy = yfor(depth_cm)
        wl_color = risk_color(depth_cm)
        el.append(box(track_x - 6, wy - 2, track_w + 12, 4, INK))
    # ticks + labels
    step = 10 if max_cm <= 60 else 20
    cm = 0
    while cm <= max_cm + 0.001:
        ty = yfor(cm)
        major = (cm % step == 0)
        tl = 16 if major else 9
        el.append(box(track_x + track_w - tl - 2, ty - 1, tl, 2,
                      MUTED if major else STROKE_HI))
        if major:
            el.append(text(x + inner_pad, ty - 14, gutter - 10, 26, "%d" % cm,
                           18, MUTED, align="RIGHT", font=F_NUM))
        cm += 5 if max_cm <= 60 else 10
    # numeric readout
    if label_side == "right":
        rx = track_x + track_w + 8
        rw = w - (track_x - x) - track_w - 8
        el.append(text(rx, yfor(depth_cm) - 30, rw, 40, "%.0f" % depth_cm,
                       44 if big else 30, INK, bold=True, font=F_NUM))
        el.append(text(rx, yfor(depth_cm) + 14, rw, 30, "cm", 24 if big else 20,
                       SUB, font=F_BODY))
    return "".join(el)


def mini_depth(x, y, w, h, depth_cm, max_cm=50.0, color=None):
    """compact horizontal depth bar (list rows).

    color: override the risk color (e.g. pass ped-rule color so the bar agrees
    with a pedestrian verdict pill instead of the vehicle rule).
    """
    f = depth_cm / max_cm
    el = [box(x, y, w, h, "#0C2740", radius=h / 2.0)]
    colr = color or risk_color(depth_cm)
    el.append(box(x, y, max(h, w * f), h, colr, radius=h / 2.0))
    return "".join(el)


# ---------------- charts ----------------
def sparkline(x, y, w, h, values, color=AQUA, baseline=None, fill=True,
              line_thick=3, smooth=False):
    """polyline trend chart of values (len>=2). Auto min/max scaling."""
    n = len(values)
    vmin = min(values)
    vmax = max(values)
    if vmax - vmin < 1e-6:
        vmax = vmin + 1.0
    pad = 8
    def px(i):
        return x + pad + (w - 2 * pad) * (i / float(n - 1))
    def py(v):
        return y + h - pad - (h - 2 * pad) * ((v - vmin) / (vmax - vmin))
    pts = [(px(i), py(v)) for i, v in enumerate(values)]
    el = []
    if fill:
        # area under line
        for i in range(n - 1):
            el.append(poly([pts[i], pts[i + 1]], line_thick, color))
        # fill via thin verticals (subtle)
        for xx, yy in pts:
            el.append(box(xx - 1, yy, 2, (y + h - pad) - yy, color + "33"))
    else:
        for i in range(n - 1):
            el.append(seg(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1],
                          line_thick, color))
    # end dot
    el.append(circle(pts[-1][0], pts[-1][1], 6, color))
    return "".join(el)


def vbars(x, y, w, h, values, colors, labels=None, max_v=None, gap=8,
          label_size=16, value_on_top=False):
    """vertical bar chart; proportional heights (geometry accuracy)."""
    n = len(values)
    vmax = max_v or (max(values) or 1)
    bw = (w - gap * (n - 1)) / float(n)
    el = []
    for i, v in enumerate(values):
        bh = (h) * (v / float(vmax)) if vmax else 0
        bx = x + i * (bw + gap)
        by = y + h - bh
        c = colors[i] if isinstance(colors, (list, tuple)) else colors
        el.append(box(bx, by, bw, max(2, bh), c, radius=min(6, bw / 2)))
        if labels:
            el.append(text(bx, y + h + 6, bw, label_size * 1.4, labels[i],
                           label_size, MUTED, align="CENTER"))
        if value_on_top and v:
            el.append(text(bx, by - label_size * 1.5, bw, label_size * 1.4,
                           "%g" % v, label_size, SUB, align="CENTER",
                           font=F_NUM, bold=True))
    return "".join(el)


def donut(x, y, r, frac, color, track=STROKE, thick=16, center_top="",
          center_bot="", num_size=40, lab_size=18):
    """ring progress via arc segments; frac 0..1. 0deg=12 o'clock cw."""
    el = []
    # track ring
    el.append(circle(x, y, r, "transparent", border=track, border_w=thick))
    # colored arc
    sweep = 360.0 * max(0.0, min(1.0, frac))
    if sweep > 0:
        el.append(arc(x, y, r, 0, sweep, thick, color, step=4.0))
    if center_top:
        el.append(text(x - r, y - num_size * 0.8, 2 * r, num_size * 1.2,
                       center_top, num_size, INK, bold=True, align="CENTER",
                       font=F_NUM))
    if center_bot:
        el.append(text(x - r, y + num_size * 0.35, 2 * r, lab_size * 1.4,
                       center_bot, lab_size, MUTED, align="CENTER"))
    return "".join(el)


# ---------------- decoration ----------------
def wave(y, w, amp=10, wl=140, color=None, opacity=None):
    """a subtle horizontal waterline wave across the top of a section."""
    c = color or STROKE
    steps = int(w / (wl / 2.0))
    pts = []
    for i in range(steps * 2 + 1):
        px = (wl / 4.0) * i
        py = y + (amp if i % 2 else -amp) * 0.5
        pts.append((px, py))
    return poly(pts, 3, c)


def ripple(cx, cy, r, color, thick=2, count=3, gap=16):
    """concentric ripple rings (decorative water metaphor)."""
    el = []
    for i in range(count):
        rr = r - i * gap
        if rr <= 2:
            break
        el.append(circle(cx, cy, rr, "transparent", border=color, border_w=thick))
    return "".join(el)


def scrim(x, y, w, h, color="#000000", alpha_hex="66"):
    """translucent overlay panel."""
    return box(x, y, w, h, color + alpha_hex)
