"""B02 brand kit for 水位线 (TIDELINE) - tokens plus the components every touchpoint reuses.

Everything the ten artefacts share lives here: the mark, the four-level colour ramp, the
type scale, the 8 pt grid, and the components (status pill, water gauge, station card,
sparkline, legend, section rule, footer, wayfinding chevrons, decorative code block).
Keeping them in one module is what makes ten different media read as one project; each
touchpoint still sets its own density, size and hierarchy.

Run:  python tmp/<run_id>/B02/tide.py --selftest
"""
from __future__ import annotations

import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ.get("SNAPSHOT_RUN", "2026-10-12T10-04Z-r001")
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))
sys.path.insert(0, str(ROOT / "tmp" / RUN / "B02"))
from bkit import MONO, SANS, SERIF, Sheet, f, tw, wrap  # noqa: E402
import data  # noqa: E402

# ---- tokens ----------------------------------------------------------------------------
INK = "#12212E"
INK_2 = "#3D4C59"
INK_3 = "#5E6B77"
PAPER = "#F5F2EA"
PANEL = "#E7E1D3"
LINE = "#C9C1AE"
CYAN = "#1E88A8"
SAND = "#E08A1E"
ALARM = "#C6412F"
SAFE = "#2E7D5B"
WATER = "#2F6F8F"
LEVEL_COLOUR = {lv["code"]: lv["colour"] for lv in data.LEVELS}
LEVEL_INK = {lv["code"]: lv["ink"] for lv in data.LEVELS}
LEVEL_NAME = {lv["code"]: lv["name"] for lv in data.LEVELS}
LEVEL_ACTION = {lv["code"]: lv["action"] for lv in data.LEVELS}
TYPE_SCALE = {"display": 44, "h1": 34, "h2": 26, "body": 20, "meta": 18, "micro": 14}
GRID = 8                                # base spacing unit, px
SERIES = {"sans": SANS, "mono": MONO, "serif": SERIF}


def _lin(c):
    def ch(i):
        v = int(c[i:i + 2], 16) / 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * ch(1) + 0.7152 * ch(3) + 0.0722 * ch(5)


def contrast(a, b):
    la, lb = _lin(a), _lin(b)
    hi, lo = max(la, lb), min(la, lb)
    return round((hi + 0.05) / (lo + 0.05), 2)


def assert_contrast(pairs, floor=4.5):
    """pairs: [(fg, bg, where)] - raises with the real ratio so failures cannot be ignored."""
    bad = [(fg, bg, where, contrast(fg, bg)) for fg, bg, where in pairs if contrast(fg, bg) < floor]
    if bad:
        raise ValueError(f"contrast below {floor}: {bad}")


# ---- mark ------------------------------------------------------------------------------
def mark(s: Sheet, x, y, size, colour=INK, bg=None, *, tag="mark"):
    """The 水位线 mark: a gauge frame, a wave-topped water block filling its lower half and
    two rising level lines above it. Monochrome, legible from 24 px to 5 m."""
    if bg:
        s.rect(x - size * 0.08, y - size * 0.08, size * 1.16, size * 1.16, bg,
               radius=size * 0.2)
    w = h = size
    s.rect(x, y, w, h, "#00000000", border=f"{size * 0.09:.1f} SOLID {colour}",
           radius=size * 0.16)
    # water: filled from the bottom to 0.62h with a single gentle crest
    d = (f"M 0 {h * 0.62:.1f} Q {w * 0.25:.1f} {h * 0.50:.1f} {w * 0.5:.1f} {h * 0.62:.1f} "
         f"T {w:.1f} {h * 0.62:.1f} L {w:.1f} {h:.1f} L 0 {h:.1f} Z")
    s.path(x, y, w, h, d, colour)
    for i, ww in enumerate((0.52, 0.34)):
        s.rect(x + w * 0.24, y + h * (0.20 + i * 0.14), w * ww, h * 0.075, colour,
               radius=h * 0.037)


def wordmark(s: Sheet, x, y, size, colour=INK, *, latin=False, bold=True):
    if latin:
        return s.text("brand", "TIDELINE", x, y, size, colour, bold=bold, font=MONO)
    return s.text("brand", data.ORG, x, y, size, colour, bold=bold)


def lockup(s: Sheet, x, y, size, colour=INK, bg=None, *, latin=True, tag="lockup"):
    """Mark + Chinese name + latin line, on a fixed 8 pt grid."""
    mark(s, x, y, size, colour, bg, tag=tag)
    s.text("wm", data.ORG, x + size + size * 0.28, y + size * 0.16, size * 0.52, colour,
           bold=True)
    if latin:
        s.text("wm2", "TIDELINE · 社区内涝预警与互助网络", x + size + size * 0.28,
               y + size * 0.78, size * 0.22, INK_3, font=MONO)
    return y + size + GRID


# ---- components ------------------------------------------------------------------------
def status_pill(s: Sheet, x, y, code, *, h=44, size=22, extra=None, solid=True):
    col = LEVEL_COLOUR[code]
    txt = f"{code} 级 · {LEVEL_NAME[code]}" + (f" · {extra}" if extra else "")
    w = tw(txt, size, True) + h
    if solid:
        s.rect(x, y, w, h, col, radius=h / 2)
    else:
        s.rect(x, y, w, h, "#00000000", border=f"{h * 0.06:.1f} SOLID {col}", radius=h / 2)
    s.text("pill", txt, x + h / 2, y + (h - size * 1.06) / 2, size,
           LEVEL_INK[code] if solid else col, bold=True, font=MONO)
    return x + w


def gauge(s: Sheet, x, y, h, value_cm, *, w=46, top_cm=90, label=True):
    """Vertical water gauge with the three threshold ticks."""
    s.rect(x, y, w, h, "#DCE3E6", radius=6, border=f"1.5 SOLID {INK_3}")
    fill = h * min(value_cm, top_cm) / top_cm
    s.rect(x, y + h - fill, w, fill, WATER, radius=6)
    for cm, name, col in ((data.WARN_CM, "警戒", CYAN), (data.CRIT_CM, "紧急", SAND),
                          (data.DISASTER_CM, "灾难", ALARM)):
        ty = y + h - h * cm / top_cm
        s.line(x - 10, ty, x + w + 4, ty, col, 2)
        if label:
            s.text("gt", f"{name} {cm}", x + w + 10, ty - 10, 20, col, font=MONO)
    s.text("gv", f"{value_cm:.0f} cm", x + w / 2, y + h - fill - 26, 20,
           "#FFFFFF" if fill > 40 else INK, align="center", bold=True, font=MONO)


def sparkline(s: Sheet, x, y, w, h, series, *, colour=WATER, band=None, dots=False):
    lo, hi = min(series), max(series)
    rng = (hi - lo) or 1.0
    pts = [(x + w * i / (len(series) - 1), y + h - h * (v - lo) / rng)
           for i, v in enumerate(series)]
    body = [(x, y + h)] + pts + [(x + w, y + h)]
    d = "M " + " L ".join(f"{p[0] - x:.1f} {p[1] - y:.1f}" for p in body) + " Z"
    s.path(x, y, w, h, d, colour, opacity=0.22)
    for a, b in zip(pts, pts[1:]):
        s.line(a[0], a[1], b[0], b[1], colour, 2.6)
    if band:
        for cm, col in band:
            yy = y + h - h * (cm - lo) / rng
            if y <= yy <= y + h:
                s.line(x, yy, x + w, yy, col, 1.6)
    if dots:
        s.dot(pts[-1][0], pts[-1][1], 5, colour)
    return pts


def station_card(s: Sheet, x, y, w, station, *, h=104):
    sid, name, now, ser, drain = station
    code = data.classify(now)
    s.rect(x, y, w, h, PAPER, radius=10, border=f"1.5 SOLID {LINE}")
    s.rect(x, y, 6, h, LEVEL_COLOUR[code], radius=3)
    s.text("sc", sid, x + 20, y + 14, 20, INK_3, font=MONO)
    s.text("sn", name, x + 20, y + 40, 24, INK, bold=True)
    s.text("sv", f"{now:.0f} cm", x + 20, y + 70, 22, LEVEL_COLOUR[code], bold=True,
           font=MONO)
    sparkline(s, x + w - 150, y + 26, 130, 52, ser, colour=LEVEL_COLOUR[code], dots=True)
    return y + h


def legend_row(s: Sheet, x, y, items, *, size=20, gap=22, swatch=20):
    """items: [(colour, label)] laid out left to right with measured gaps."""
    cx = x
    for col, lab in items:
        s.rect(cx, y + (size * 1.06 - swatch) / 2, swatch, swatch, col, radius=4)
        s.text("lg", lab, cx + swatch + 8, y, size, INK_2)
        cx += swatch + 8 + tw(lab, size) + gap
    return cx - gap


def section_rule(s: Sheet, x, y, w, label, *, size=22, colour=INK):
    s.text("sr", label, x, y, size, colour, bold=True)
    lx = x + tw(label, size, True) + 12
    s.line(lx, y + size * 0.52, x + w, y + size * 0.52, LINE, 1.5)
    return y + size * 1.46


def chevrons(s: Sheet, x, y, size, colour=INK, n=3, *, step=0.55, weight=None):
    """Wayfinding chevrons pointing right."""
    weight = weight or size * 0.16
    for i in range(n):
        cx = x + i * size * step
        s.line(cx, y, cx + size * 0.42, y + size / 2, colour, weight, cap_round=True)
        s.line(cx + size * 0.42, y + size / 2, cx, y + size, colour, weight, cap_round=True)
    return x + (n - 1) * size * step + size * 0.42


def code_block(s: Sheet, x, y, size, seed=7, *, quiet=4):
    """Decorative code square - NOT scannable; touchpoints must label it as such."""
    n = 9
    cell = (size - 2 * quiet) / n
    s.rect(x, y, size, size, PAPER, radius=6, border=f"1.5 SOLID {INK}")
    for i in range(n):
        for j in range(n):
            corner = (i < 2 and j < 2) or (i > n - 4 and j < 2) or (i < 2 and j > n - 4)
            on = corner or ((i * 7 + j * 13 + seed * 5 + i * j) % 3 == 0)
            if on:
                s.rect(x + quiet + i * cell, y + quiet + j * cell, cell * 0.92,
                       cell * 0.92, INK)


def footer(s: Sheet, x, y, w, lines, *, size=18, colour=INK_3):
    s.line(x, y - 10, x + w, y - 10, LINE, 1.2)
    for i, ln in enumerate(lines):
        s.text("ft", ln, x, y + i * (size * 1.46 + 4), size, colour)
    return y + len(lines) * (size * 1.46 + 4)


def sheet(w, h, *, bg=PAPER, min_font=20):
    return Sheet(w, h, min_font=min_font, bg=bg)


def selftest():
    s = sheet(1200, 300)
    lockup(s, 40, 40, 120, INK)
    for i, code in enumerate((1, 2, 3, 4)):
        status_pill(s, 40 + i * 250, 190, code)
    gauge(s, 1080, 40, 200, data.TOP_STATION[2])
    sparkline(s, 520, 60, 300, 90, data.STATIONS[1][3], dots=True)
    legend_row(s, 40, 250, [(LEVEL_COLOUR[c], LEVEL_NAME[c]) for c in (1, 2, 3, 4)])
    chevrons(s, 520, 200, 30, INK)
    code_block(s, 900, 180, 100)
    pairs = [(PAPER, INK, "paper on ink"), (LEVEL_INK[3], LEVEL_COLOUR[3], "level3 text"),
             (INK_3, PAPER, "meta on paper"), (INK_2, PAPER, "body on paper")]
    assert_contrast(pairs, 4.5)
    return {"ok": True, "contrast": {f"{a}/{b}": contrast(a, b) for a, b, _ in pairs},
            "texts": len(s.items), "shapes": s.shapes}


if __name__ == "__main__":
    import json
    print(json.dumps(selftest(), ensure_ascii=False))
