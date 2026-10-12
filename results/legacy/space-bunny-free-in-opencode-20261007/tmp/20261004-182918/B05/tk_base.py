"""B04 shared design kit: ocean-acidification visual special.

Editorial identity
-----------------
One palette (abyss navy -> surface cyan, one warm "risk" hue), one type scale
(Inter + Noto Sans CJK SC, DejaVu Sans Mono for every measured number), one rule
that measured numbers are always monospaced and never coloured, only the ink.
"""
from __future__ import annotations

import math
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import dsllib as D  # noqa: E402

UI = D.UI
MONO = D.MONO

# ---------------------------------------------------------------- palette ---
INK        = "#F1F7FBFF"   # primary text on dark
INK_2      = "#A8C2D4FF"   # secondary text
INK_3      = "#6E8AA0FF"   # tertiary / axis labels
ABYSS      = "#050D16FF"   # deepest background
DEEP       = "#0A1A28FF"   # panel fill
DEEP_2     = "#0E2537FF"   # raised panel
HAIR       = "#1D3A50FF"   # hairlines / gridlines
HAIR_2     = "#14304AFF"

CYAN       = "#5EE0D0FF"   # ocean chemistry / neutral fact
CYAN_DIM   = "#2E7F7AFF"
BLUE       = "#6BA8FFFF"   # model projection
BLUE_DIM   = "#2F5F9EFF"
AMBER      = "#FFC15EFF"   # measured data
AMBER_DIM  = "#8A6420FF"
CORAL      = "#FF7A6BFF"   # risk / adverse
CORAL_DIM  = "#8F3B33FF"
MINT       = "#9BE8A0FF"   # benefit / favourable
MINT_DIM   = "#3D7A45FF"
VIOLET     = "#C0A6FFFF"   # interpretation layer
PAPER      = "#F3EFE6FF"   # light-on-dark inverse panel
PAPER_INK  = "#0B1A26FF"

SHELL      = "#E9F3F8FF"   # CaCO3 shell white

# "Inter Black" is a real family in the service /fonts list, not a fontStyle.
DISPLAY = "Inter Black,Noto Sans CJK SC"
SEMI = "Inter Semi Bold,Noto Sans CJK SC"
SECTIONS = [
    ("01", "开篇", "COVER"),
    ("02", "证据", "EVIDENCE"),
    ("03", "机制", "MECHANISM"),
    ("04", "流向", "FLUX"),
    ("05", "尺度", "TIMESCALE"),
    ("06", "未来", "SCENARIO"),
    ("07", "阈值", "THRESHOLD"),
    ("08", "谁", "WHO"),
    ("09", "观测", "WATCH"),
    ("10", "核查", "CHECK"),
]

# ------------------------------------------------------------ type helpers ---
def h1(s, x, y, size=44, color=INK, ls=-0.6, font=None, w=None):
    return D.text_el(s, x=x, y=y, w=w, size=size, color=color, font=font or D.UI,
                     ls=ls, style="BOLD")


def h2(s, x, y, size=24, color=INK, ls=-0.2):
    return D.text_el(s, x=x, y=y, size=size, color=color, font=D.UI, ls=ls,
                     style="BOLD")


def body(s, x, y, w, size=16, color=INK_2, ls=0.1, lh=1.55, font=None, align=None):
    return D.text_el(s, x=x, y=y, w=w, size=size, color=color, font=font or D.UI,
                     ls=ls, align=align, h=size * lh * D.est_lines(s, size, w) + 4)


def kicker(s, x, y, size=12, color=CYAN, ls=2.6, w=None, align=None):
    return D.text_el(s, x=x, y=y, w=w, size=size, color=color, font=D.MONO,
                     ls=ls, style="BOLD", align=align)


def mono(s, x, y, size=18, color=INK, w=None, align=None, style=None):
    return D.text_el(s, x=x, y=y, w=w, size=size, color=color, font=D.MONO,
                     align=align, style=style)


def num(s, x, y, size=30, color=INK, align=None, w=None):
    """A measured value. Always monospaced so digits line up in a column."""
    return D.text_el(s, x=x, y=y, w=w, size=size, color=color, font=D.MONO,
                     style="BOLD", align=align)


def mono_w(s, size):
    """DejaVu Sans Mono advance width.

    dsllib.est_width uses 0.55em for latin, but DejaVu Sans Mono is monospaced
    at 0.602em (measured against case-03 v1, where `≈ 26%` collided with the
    preceding value). Use this for any offset placed after a mono string.
    """
    return len(s) * size * 0.602


def tag(s, x, y, color=CYAN, size=11, padx=9, padh=5, fill=None, border=True):
    """Small pill label; returns DSL plus the pill width."""
    tw = D.est_width(s, size)
    w = tw + padx * 2
    h = size * 1.6
    fillc = fill if fill else A(color, "22")
    b = "1 SOLID " + A(color, "66") if border else None
    out = [D.box(x, y, w, h, color=fillc, radius=h / 2, border=b),
           D.text_el(s, x=x, y=y + (h - size * 1.15) / 2, size=size, color=color,
                     font=D.UI, ls=0.8, style="BOLD")]
    return "\n".join(out), w


# ------------------------------------------------------------- background ---
def water_bg(w, h, *, warm=0.0, horizon=None):
    """Vertical abyss->surface gradient with an optional warm horizon band.

    `warm` 0..1 mixes a coral horizon glow used only where the piece is about
    risk. Nothing else in the suite uses it, so it reads as a deliberate
    section shift rather than decoration.
    """
    hz = horizon if horizon is not None else h * 0.42
    kids = []
    steps = 78
    for i in range(steps):
        t = i / (steps - 1.0)
        y = t * h
        # three-stop vertical ramp, sampled and emitted as scanline boxes
        if t < hz / h:
            u = t / (hz / h)
            c = _mix(ABYSS, "#08283CFF", u)
        else:
            u = (t - hz / h) / max(1e-6, 1 - hz / h)
            c = _mix("#08283CFF", "#0C3A4EFF", u ** 0.6)
        kids.append(D.box(0, y, w, h / steps + 1.0, color=c))
    if warm > 0:
        g = _mix(A(CORAL, "00"), A(CORAL, "55"), warm)
        kids.append(D.box(0, hz - 90, w, 190, color=None, extra={
            "gradientType": "LINEAR",
            "gradientColors": A(CORAL, "00") + "," + g + "," + A(CORAL, "00"),
            "gradientBegin": "(0.5,0)", "gradientEnd": "(0.5,1)"}))
    return kids


def A(c, alpha):
    """`A(CYAN, '4D')` -> '#5EE0D0FF' with the alpha replaced by 4D.

    Every palette constant in this kit is already 8-digit #RRGGBBAA, so plain
    string concatenation would produce invalid 10-digit colours (measured: the
    service answers 400 PARSE_ERROR).
    """
    s = c.lstrip("#")
    assert len(s) in (3, 6, 8), c
    if len(s) == 3:
        s = "".join(ch * 2 for ch in s)
    return "#" + s[:6].upper() + str(alpha).upper()


def _mix(a, b, t):
    """Blend two #RRGGBBAA strings."""
    t = max(0.0, min(1.0, t))
    def p(s):
        s = s.lstrip("#")
        return [int(s[i:i + 2], 16) for i in (0, 2, 4, 6)]
    ca, cb = p(a), p(b)
    out = []
    for i in range(4):
        if i == 3:
            out.append(max(ca[3], cb[3]))
        else:
            out.append(int(round(ca[i] + (cb[i] - ca[i]) * t)))
    return "#%02X%02X%02X%02X" % tuple(out)


def grain(w, h, step=17, color="#FFFFFF", alpha="08", count=None):
    """Deterministic sparse speckle so large dark fields do not read as flat."""
    out = []
    n = count if count else int(w * h / (step * step * 46))
    seed = 20261004
    for i in range(n):
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        x = seed % w
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        y = seed % h
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        s = 1 + (seed % 2)
        out.append(D.box(x, y, s, s, color=A(color, alpha)))
    return "\n".join(out)


# ------------------------------------------------------------ components ---
def panel(x, y, w, h, *, fill=DEEP, border=HAIR, radius=14, shadow=None):
    return D.box(x, y, w, h, color=fill, radius=radius, border="1 SOLID " + border,
                 shadow=shadow)


def circle(cx, cy, r, color, *, border=None, bw=2):
    """Filled circle centred on (cx,cy).

    Measured semantics: `shape="CIRCLE"` cannot be combined with `borderRadius`
    (service returns 400 PARSE_ERROR), so a filled disc carries no radius and a
    stroked circle is a CIRCLE with `border` only.
    """
    s = round(2 * r, 2)
    if border:
        w = int(bw) if float(bw) >= 1 else 1
        a = {"width": s, "height": s, "shape": "CIRCLE",
             "border": "%d SOLID %s" % (w, border)}
    else:
        a = {"width": s, "height": s, "shape": "CIRCLE"}
    if color:
        a["color"] = color
    return _abs_container(cx - r, cy - r, a)


def ring(cx, cy, r, color, width=2):
    return circle(cx, cy, r, None, border=color, bw=width)


def _abs_container(x, y, attrs):
    return D.el("Positioned", {"left": round(x, 2), "top": round(y, 2),
                               "width": attrs["width"], "height": attrs["height"]},
                [D.el("Container", attrs, None)])


def section_mark(n, x, y, *, color=CYAN, size=13):
    """`03 / FLUX` running head."""
    code = SECTIONS[n - 1]
    return "\n".join([
        D.vline(x, y + 1, y + size * 1.25, color, 2.5),
        D.text_el("%02d" % n, x=x + 12, y=y, size=size, color=color, font=D.MONO,
                  style="BOLD"),
        D.text_el("/ " + code[2], x=x + 12 + size * 2.9, y=y, size=size,
                  color=INK_3, font=D.MONO, ls=1.4),
    ])


def source_note(s, x, y, w, *, size=11, color=INK_3, label="来源"):
    """`来源 …` footnote block, wrapped and returned with the y it ended at."""
    lwid = D.est_width(label, size) + 8
    lines = wrap_cjk(s, w - lwid, size)
    out = [D.text_el(label, x=x, y=y, size=size, color=color, font=D.MONO, ls=0.8)]
    yy = y
    for i, ln in enumerate(lines):
        out.append(D.text_el(ln, x=x + lwid, y=yy, w=w - lwid, size=size,
                             color=color, font=UI))
        yy += size * 1.42
    return "\n".join(out), yy


def wrap_cjk(s, w, size=11):
    """Greedy wrap that treats CJK as breakable anywhere and latin as words."""
    out, cur, curw = [], "", 0.0
    i = 0
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


def rule(x0, x1, y, color=HAIR, w=1):
    return D.hline(x0, x1, y, color, w)


def hline(x0, x1, y, color=HAIR, w=1):
    return D.hline(x0, x1, y, color, w)


def vline(x, y0, y1, color=HAIR, w=1):
    return D.vline(x, y0, y1, color, w)


def hrule(x0, x1, y, color=HAIR, w=1):
    return D.hline(x0, x1, y, color, w)


def chip(s, x, y, color, *, size=12, fill=None, padx=11, h=26, mono_font=False):
    tw = D.est_width(s, size)
    w = tw + padx * 2
    out = [D.box(x, y, w, h, color=fill or A(color, "1F"), radius=h / 2,
                 border="1 SOLID " + A(color, "55")),
           D.text_el(s, x=x + padx, y=y + (h - size * 1.2) / 2, size=size,
                     color=color, font=D.MONO if mono_font else D.UI, style="BOLD")]
    return "\n".join(out), w


def legend(items, x, y, *, size=12, gap=22, dot=7, mono_font=False):
    """items = [(label, colour), ...] laid out on one baseline row."""
    out, xx = [], x
    for label, col in items:
        out.append(D.box(xx, y + size * 0.42, dot, dot, color=col, radius=dot / 2))
        out.append(D.text_el(label, x=xx + dot + 7, y=y, size=size, color=INK_2,
                             font=D.MONO if mono_font else D.UI))
        xx += dot + 7 + D.est_width(label, size) + gap
    return "\n".join(out)


# ------------------------------------------------------------ geometry -----
def polyline(pts, color, w=3, close=False, cap=None):
    """A stroked polyline built from rotated rectangles (DSL has no path node)."""
    out = []
    seq = list(pts) + ([pts[0]] if close and len(pts) > 2 else [])
    for i in range(len(seq) - 1):
        (x0, y0), (x1, y1) = seq[i], seq[i + 1]
        if i == 0 and cap:
            out.append(circle(x0, y0, cap, color))
        piece = seg(x0, y0, x1, y1, color, w)
        if piece:
            out.append(piece)
    return "\n".join([o for o in out if o])


def seg(x0, y0, x1, y1, color, w=3):
    """One rotated rectangle spanning (x0,y0)-(x1,y1), exact geometry.

    Measured semantics: `Transform` with `origin="(0,0)" alignment="CENTER"`
    rotates about the box centre, so the box itself must be positioned by
    left/top with a ZERO translation matrix. Putting the midpoint into the
    matrix translation slot as well shifts every segment by its own length.
    """
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    if L < 0.4:
        return ""
    ang = math.atan2(dy, dx)
    pad = w * 0.9
    bw, bh = L + pad * 2, w
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    a = math.cos(ang)
    s = math.sin(ang)
    m = "(%.5f,%.5f,0,0,%.5f,%.5f,0,0,0,0,1,0,0,0,0,1)" % (a, s, -s, a)
    inner = D.el("Container", {"width": round(bw, 2), "height": round(bh, 2),
                               "color": color}, None)
    tf = D.el("Transform", {"matrix": m, "origin": "(0,0)",
                            "alignment": "CENTER"}, [inner])
    return D.el("Positioned", {"left": round(cx - bw / 2.0, 2),
                               "top": round(cy - bh / 2.0, 2),
                               "width": round(bw, 2), "height": round(bh, 2)}, [tf])


def scatter(points, color, r=5, ring=None):
    out = []
    for x, y in points:
        if ring:
            out.append(D.box(x - r - 3, y - r - 3, (r + 3) * 2, (r + 3) * 2,
                             color=ring, radius=r + 3, shape="CIRCLE"))
        out.append(D.box(x - r, y - r, r * 2, r * 2, color=color, radius=r,
                         shape="CIRCLE"))
    return "\n".join(out)


def area(pts_top, y_base, color, rows=90):
    """Filled area under a polyline, emitted as scanline boxes."""
    rows_n = rows
    ymin = min(min(p[1] for p in pts_top), y_base)
    ymax = max(p[1] for p in pts_top)
    out = []
    for i in range(rows_n):
        y = ymin + (ymax - ymin) * (i + 0.5) / rows_n
        xs = _scan(pts_top, y)
        if xs is None:
            continue
        out.append(D.box(xs[0], y - (ymax - ymin) / rows_n / 2 - 0.5,
                         xs[1] - xs[0], (ymax - ymin) / rows_n + 1.0, color=color))
    return "\n".join(out)


def _scan(pts, y):
    xs = []
    n = len(pts)
    for i in range(n):
        (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % n]
        if (y1 <= y < y2) or (y2 <= y < y1):
            t = (y - y1) / (y2 - y1)
            xs.append(x1 + t * (x2 - x1))
    if len(xs) < 2:
        return None
    return min(xs), max(xs)


def fade_area(pts_top, y_base, color_top, color_bot, rows=130):
    """Area under a polyline down to `y_base`, alpha stepping top -> bottom.

    Three measured constraints, all from looking at real renders:
      1. the polyline must be closed against the baseline, otherwise a monotone
         rising curve gives <2 intersections per scanline and nothing renders;
      2. consecutive scanline boxes must NOT overlap — translucent boxes that
         overlap double-composite and the overlap lines read as hard banding;
         row edges are therefore snapped to integers so they tile exactly;
      3. 64 rows over a 350 px band made the alpha step itself visible, so the
         default is 130 rows and callers pass identical top/bottom alpha for a
         flat fill.
    """
    if not pts_top:
        return ""
    closed = list(pts_top) + [(pts_top[-1][0], y_base), (pts_top[0][0], y_base)]
    ytop = min(p[1] for p in pts_top)
    span = max(1.0, y_base - ytop)
    out = []
    for i in range(rows):
        ya = int(round(ytop + span * i / rows))
        yb = int(round(ytop + span * (i + 1) / rows))
        if yb <= ya:
            continue
        y = (ya + yb) / 2.0
        xs = _scan(closed, y)
        if xs is None:
            continue
        t = i / (rows - 1.0)
        c = _mix(color_top, color_bot, t)
        out.append(D.box(xs[0], ya, xs[1] - xs[0], yb - ya, color=c))
    return "\n".join(out)


def _scan_open(pts, y):
    xs = []
    n = len(pts)
    for i in range(n - 1):
        (x1, y1), (x2, y2) = pts[i], pts[i + 1]
        if (y1 <= y < y2) or (y2 <= y < y1):
            t = (y - y1) / (y2 - y1)
            xs.append(x1 + t * (x2 - x1))
    if len(xs) < 2:
        return None
    return min(xs), max(xs)


def arrow(x0, y0, x1, y1, color, w=2, head=9):
    ang = math.atan2(y1 - y0, x1 - x0)
    bx, by = x1 - head * 0.92 * math.cos(ang), y1 - head * 0.92 * math.sin(ang)
    return "\n".join([
        seg(x0, y0, bx, by, color, w),
        polyline([(x1, y1),
                  (x1 - head * math.cos(ang - 0.42), y1 - head * math.sin(ang - 0.42)),
                  (x1 - head * math.cos(ang + 0.42), y1 - head * math.sin(ang + 0.42))],
                 color, w, close=True),
    ])


def arrow_head(x, y, ang_deg, color, size=10):
    a = math.radians(ang_deg)
    p1 = (x, y)
    p2 = (x - size * math.cos(a - 0.42), y - size * math.sin(a - 0.42))
    p3 = (x - size * math.cos(a + 0.42), y - size * math.sin(a + 0.42))
    return polyline([p1, p2, p3], color, 2.4, close=True)


def triangle(pts, color, opacity=1.0):
    return D.polygon(pts, color)


def bars(values, x0, y_base, scale, *, color, gap=6, radius=3, colors=None,
         labels=None, vmax=None):
    """Vertical bars from a list of (w, value) tuples. Returns DSL + xs."""
    out, xs = [], []
    xx = x0
    vmax = vmax or max(v for _, v in values) * 1.0
    for i, (w, v) in enumerate(values):
        h = max(1.0, v * scale)
        c = colors[i] if colors else color
        out.append(D.box(xx, y_base - h, w, h, color=c, radius=radius,
                         radii={"BottomLeft": 0, "BottomRight": 0} if radius else None))
        xs.append((xx, w, y_base - h, v))
        xx += w + gap
    return "\n".join(out), xs


# ------------------------------------------------------------ data files ---
GML = os.path.join(ROOT, "tmp", "20261004-182918", "B04", "research",
                   "gml-co2-annmean-mlo.txt")


def keeling_series():
    """Real NOAA GML Mauna Loa annual means, parsed from the downloaded file."""
    rows = []
    with open(GML, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 2 or not parts[0].isdigit():
                continue
            rows.append((int(parts[0]), float(parts[1]), float(parts[2])))
    return rows


def count_elements(dsl_text):
    """Each Positioned box costs 2 elements; count tags as a proxy."""
    return dsl_text.count("<Positioned") + dsl_text.count("<Container") \
        + dsl_text.count("<Text")


def finish(dsl, w, h, bg=ABYSS):
    return D.snapshot([D.stack(dsl.split("\n") if isinstance(dsl, str) else dsl,
                                w, h)], w, h, bg=bg)
