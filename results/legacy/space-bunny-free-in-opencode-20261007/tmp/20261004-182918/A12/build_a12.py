"""A12 - four-breakpoint responsive visual system for one event.

One content set (tasks/A12-responsive-system/inputs/content.json) plus one shared
design-token set drive four independently laid-out canvases:

    mobile  360x800    1 column x 6 rows, everything stacked
    tablet  768x1024   hero band on top, 2 columns x 3 rows of step cards
    desktop 1440x900   split: hero column left, 3 columns x 2 rows of cards right
    stage   1920x1080  wide poster: split hero band, 6 cards in one pipeline row

Every canvas is emitted as its own complete absolute-positioned DSL and rendered
separately against the live service. No <Image>, no cropping, no stretching.

Widths are NOT guessed: probe_fonts.py / probe_fonts2.py / probe_glyphband.py
measured real advance widths and glyph bands from service responses, and those
measurements are encoded in WID / MONO_ADV / BAND_* below.
"""
from __future__ import annotations

import json
import os
import sys
import time

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402
import state as S  # noqa: E402

TASK = "A12"
CONTENT_PATH = os.path.join(ROOT, "tasks", "A12-responsive-system", "inputs", "content.json")
OUT = os.path.join(S.OUT_ROOT, TASK)
TMP = os.path.join(S.TMP_ROOT, TASK)
DRAFTS = os.path.join(TMP, "drafts")
os.makedirs(DRAFTS, exist_ok=True)
snapkit.configure(TASK, OUT, TMP)

with open(CONTENT_PATH, encoding="utf-8") as fh:
    C = json.load(fh)

# ==========================================================================
# calibrated text metrics (measured, see tmp/.../A12/font-metrics-2.json)
# ==========================================================================
FULLWIDTH = "\u3001\u3002\uff0c\uff1a\uff1b\uff01\uff1f\uff08\uff09\u300a\u300b" \
            "\u201c\u201d\u2014\u2026"
# measured: CJK 0.9938 em/char, Inter upper 0.65, lower 0.55, space 0.20,
#           'DSL' -> 0.65 em each, '/' 0.40, '·' U+00B7 -> 0.39-0.40 em (NOT full
#           width: measured 12.70 em for 12 CJK + '·' + 2 spaces at 100 px)
_ADV = {"space": 0.20, "digit": 0.58, "upper": 0.65, "lower": 0.55, "other": 0.40}
MONO_ADV = 0.61      # DejaVu Sans Mono measured 0.5935 em ink / 0.602 em advance
CELL_R = 1.55        # flow cell height = fontSize * CELL_R
BAND_TOP = 0.15      # ink band top inside the box, in em  (measured 0.17-0.31)
BAND_H = 1.15        # ink band height in em              (measured 0.86-0.98)


def adv_em(ch):
    if ord(ch) > 0x2E80 or ch in FULLWIDTH:
        return 1.0
    if ch == "\u00b7":           # MIDDLE DOT - measured narrow, not full width
        return _ADV["other"]
    if ch == " ":
        return _ADV["space"]
    if ch.isdigit():
        return _ADV["digit"]
    if ch.isupper():
        return _ADV["upper"]
    if ch.islower():
        return _ADV["lower"]
    return _ADV["other"]


def wid(s, size, mono=False):
    """Measured ink advance width in px (never below the real rendered width)."""
    if mono:
        return len(s) * MONO_ADV * size
    return sum(adv_em(c) for c in s) * size


SAFE = 1.05   # a box must be wider than the measured ink: side bearings are not
              # part of the ink measurement, and an over-wide box is the only way
              # to be sure the service will not wrap the line and clip it.
ADV_KEY = "\u0001"
MEAS_PATH = os.path.join(TMP, "measured-metrics.json")
MEAS = {}
if os.path.exists(MEAS_PATH):
    with open(MEAS_PATH, encoding="utf-8") as fh:
        MEAS = json.load(fh)


def meas_ink(shown, font, size):
    """Exact rendered ink width in px, measured from the service (probe_metrics.py).

    Returns None when the string/size has not been measured yet, in which case
    the conservative model is used instead.
    """
    return MEAS.get("%s%s%s%d" % (shown, ADV_KEY, font, size))


def ink_w(shown, size, mono, font=None):
    m = meas_ink(shown, font or (D.MONO if mono else D.UI), size)
    if m is not None:
        return float(m)
    return wid(shown, size, mono)


def need(s, size, mono=False, font=None):
    """Box width required to hold the text on one line."""
    return max(wid(s, size, mono), ink_w(s, size, mono, font)) * SAFE


def cell(s):
    return s * CELL_R


CLR = {
    "bg": "#0B0E13FF", "surface": "#151B24FF", "surface_alt": "#1E2632FF",
    "stroke": "#2E3846FF", "grid_line": "#FFFFFF0A",
    "text_primary": "#F4F7FBFF", "text_secondary": "#B4C0CEFF",
    "text_muted": "#8B96A5FF", "accent": "#FF7A3DFF",
    "accent_2": "#5CC6FFFF", "gold": "#FFC24AFF",
}
ACC6 = "#FF7A3D"          # 6-digit base; alpha is appended to THIS, not to ACC_A
ACC_A = CLR["accent"]
RAD = {"tick": 3, "chip": 8, "card": 16, "panel": 16, "cta": 14}

BP = {
    "mobile": {"w": 360, "h": 800, "m": 20, "cols": 1, "rows": 6, "pitch": 40,
               "body_min": 16, "min_margin": 16, "main_title": 32, "subtitle": 17,
               "card_title": 18, "card_detail": 16, "meta": 16, "label": 16,
               "cta": 17, "website": 16, "ghost": 30},
    "tablet": {"w": 768, "h": 1024, "m": 40, "cols": 2, "rows": 3, "pitch": 64,
               "body_min": 20, "min_margin": 32, "main_title": 48, "subtitle": 24,
               "card_title": 24, "card_detail": 20, "meta": 22, "label": 20,
               "cta": 22, "website": 22, "ghost": 46},
    "desktop": {"w": 1440, "h": 900, "m": 48, "cols": 3, "rows": 2, "pitch": 80,
                "body_min": 20, "min_margin": 32, "main_title": 72, "subtitle": 28,
                "card_title": 26, "card_detail": 20, "meta": 20, "label": 20,
                "cta": 26, "website": 26, "ghost": 72},
    "stage": {"w": 1920, "h": 1080, "m": 72, "cols": 6, "rows": 1, "pitch": 120,
              "body_min": 20, "min_margin": 32, "main_title": 96, "subtitle": 34,
              "card_title": 26, "card_detail": 20, "meta": 26, "label": 20,
              "cta": 28, "website": 28, "ghost": 76},
}
LBL = {"date": "\u65e5\u671f", "time": "\u65f6\u95f4", "location": "\u5730\u70b9",
       "site": "\u5b98\u7f51", "steps": "\u516d\u4e2a\u73af\u8282"}


class Rec:
    """Records every text box so width / margin / overlap rules can be proved."""

    def __init__(self, bp):
        self.bp = bp
        self.texts = []
        self.panels = []
        self.issues = []

    def t(self, field, shown, x, y, w, size, align=None, semantic=None,
          mono=False, origin=(0, 0), optical=0.0, color=None, **kw):
        """Emit one Text box.

        `origin` is the canvas position of the parent Container: the emitted
        Positioned must use coordinates RELATIVE to that parent, while the
        recorded box stays in canvas coordinates for the overlap map.
        """
        lh = cell(size)
        fam = kw.get("font", D.UI)
        iw = ink_w(shown, size, mono, fam)
        req = max(wid(shown, size, mono), iw) * SAFE
        if req > w + 0.5:
            self.issues.append("TEXT_TOO_NARROW %s %r needs %.1f box %.1f"
                               % (field, shown, req, w))
        # the width model must match the family actually requested, otherwise the
        # box is sized for one font and painted with another (v03 location bug)
        if mono and fam != D.MONO:
            self.issues.append("FONT_MODEL_MISMATCH %s: mono width model, font=%r"
                               % (field, fam))
        if not mono and fam == D.MONO:
            self.issues.append("FONT_MODEL_MISMATCH %s: ui width model, font=MONO"
                               % field)
        ox, oy = origin
        gx1 = x + iw
        if align in ("CENTER", "center"):
            gx0 = x + (w - iw) / 2.0
        elif align in ("RIGHT", "END", "end"):
            gx0 = x + w - iw
        else:
            gx0 = x
        rec = {"field": field, "shown": shown, "value": semantic or shown,
               "x": round(x + ox, 2), "y": round(y + oy, 2),
               "w": round(w, 2), "h": round(lh, 2), "need_w": round(req, 2),
               "ink_w": round(iw, 2), "color": color or kw.get("color"),
               "font": fam,
               "gx0": round(gx0 + ox, 2), "gx1": round(gx1 + ox, 2),
               "gy0": round(y + size * BAND_TOP + oy, 2),
               "gy1": round(y + size * (BAND_TOP + BAND_H) + oy, 2),
               "size": round(size, 2), "align": align or "START", "mono": mono}
        self.texts.append(rec)
        # align MUST be forwarded: it is a real textAlign enum (verified in
        # tmp/.../A12/textalign-probe2.json) and dropping it silently left-aligned
        # every single text box in v03.
        return D.text_el(shown, x=x, y=y + optical, w=w, h=lh, size=size,
                         align=align, color=color, **kw)

    def panel(self, kind, x, y, w, h):
        self.panels.append({"kind": kind, "x": round(x, 2), "y": round(y, 2),
                            "w": round(w, 2), "h": round(h, 2)})


# ==========================================================================
# shared decorative components - identical construction, re-arranged only
# ==========================================================================
def comp_grid(x0, y0, x1, y1, pitch):
    out, x = [], x0 + pitch
    while x < x1:
        out.append(D.box(x, y0, 1, y1 - y0, color=CLR["grid_line"]))
        x += pitch
    y = y0 + pitch
    while y < y1:
        out.append(D.box(x0, y, x1 - x0, 1, color=CLR["grid_line"]))
        y += pitch
    return out


def comp_tick(x, y, w, h=5):
    return [D.box(x, y, w, h, color=ACC_A, radius=RAD["tick"])]


def comp_corner_ticks(x, y, w, h, arm, t=2, color=None):
    c = color or CLR["stroke"]
    return [D.box(x, y, arm, t, color=c), D.box(x, y, t, arm, color=c),
            D.box(x + w - arm, y, arm, t, color=c), D.box(x + w - t, y, t, arm, color=c),
            D.box(x, y + h - t, arm, t, color=c), D.box(x, y + h - arm, t, arm, color=c),
            D.box(x + w - arm, y + h - t, arm, t, color=c),
            D.box(x + w - t, y + h - arm, t, arm, color=c)]


def comp_ring(x, y, d, t=2, color=None):
    # NOTE: must return a LIST - `kids += <str>` would splice characters in.
    return [D.box(x, y, d, d, radius=d / 2.0,
                  border="%d SOLID %s" % (t, color or CLR["stroke"]))]


def comp_index_chip(rec, field, x, y, s, label, size):
    # A Positioned may only sit directly under a Stack, so nested text always
    # goes through Stack(fit=EXPAND) with parent-relative coordinates.
    inner = rec.t(field, label, 0, (s - cell(size)) / 2.0, s, size, align="CENTER",
                  mono=True, origin=(x, y), font=D.MONO, style="BOLD",
                  color=CLR["bg"], ls=0.4)
    return D.box(x, y, s, s, color=ACC_A, radius=RAD["chip"],
                 children=[D.el("Stack", {"fit": "EXPAND"}, [inner])])


def comp_step_rail(x0, x1, y, n, dot, color=None):
    c = color or ACC_A
    out = [D.dashed(x0 + dot / 2.0, x1 - dot / 2.0, y, c, 2, 9, 7)]
    for i in range(n):
        cx = x0 + (x1 - x0 - dot) * i / float(n - 1)
        out.append(D.box(cx, y - dot / 2.0, dot, dot, color=c, radius=dot / 2.0))
        out.append(D.box(cx + 3, y - dot / 2.0 + 3, dot - 6, dot - 6,
                         color=CLR["bg"], radius=(dot - 6) / 2.0))
    return out


# ==========================================================================
# shared content components
# ==========================================================================
def hero(kids, rec, x, y, w, tsize, tlines, ssize):
    kids += comp_tick(x, y, max(44, tsize * 0.9))
    yy = y + 5 + 7
    for ln in tlines:
        kids.append(rec.t("title", ln, x, yy, w, tsize, semantic=C["title"],
                          font=D.LATIN, style="BOLD", color=CLR["text_primary"],
                          ls=-tsize * 0.022))
        yy += cell(tsize)
    kids.append(rec.t("subtitle", C["subtitle"], x, yy + 4, w, ssize,
                      color=CLR["text_secondary"]))
    return yy + 4 + cell(ssize)


def meta_cols(w, vsize, mono_flags, pad=20, gap=20):
    req = [need(v, vsize, mf, D.MONO if mf else D.UI) for v, mf in zip(
        [C["date"], C["time"], C["location"]], mono_flags)]
    avail = w - 2 * pad - 2 * gap
    if sum(req) > avail:
        raise ValueError("meta columns do not fit: need %.1f avail %.1f size %.1f"
                         % (sum(req), avail, vsize))
    add = (avail - sum(req)) / 3.0
    return [r + add for r in req]


def meta(kids, rec, x, y, w, h, mode, lsize, vsize, pad=20, gap=20):
    kids.append(D.box(x, y, w, h, color=CLR["surface"], radius=RAD["panel"],
                      border="1 SOLID " + CLR["stroke"]))
    rec.panel("meta", x, y, w, h)
    items = [("date", C["date"], True), ("time", C["time"], True),
             ("location", C["location"], False)]
    if mode == "rows":
        lw, vx = 56, x + 16 + 56
        vw = w - 32 - 56
        ry = y + (h - 3 * cell(vsize)) / 2.0
        for i, (k, v, mf) in enumerate(items):
            yy = ry + i * cell(vsize)
            kids.append(rec.t("label:" + k, LBL[k], x + 16, yy, lw, lsize,
                              color=CLR["text_muted"]))
            kids.append(rec.t(k, v, vx, yy, vw, vsize, mono=mf,
                              color=CLR["text_primary"],
                              font=D.MONO if mf else D.UI,
                              style="BOLD", optical=0.05 * vsize))
            if i < 2:
                kids.append(D.hline(x + 16, x + w - 16, yy + cell(vsize) - 2,
                                    CLR["grid_line"], 1))
    else:
        widths = meta_cols(w, vsize, [m for _, _, m in items], pad, gap)
        cx = x + pad
        lh = cell(lsize) + 4 + cell(vsize)
        oy = y + (h - lh) / 2.0
        for i, (k, v, mf) in enumerate(items):
            kids.append(rec.t("label:" + k, LBL[k], cx, oy, widths[i], lsize,
                              color=CLR["text_muted"]))
            kids.append(rec.t(k, v, cx, oy + cell(lsize) + 4, widths[i], vsize,
                              mono=mf, color=CLR["text_primary"],
                              font=D.MONO if mf else D.UI,
                              style="BOLD", optical=0.05 * vsize))
            if i < 2:
                kids.append(D.vline(cx + widths[i] + gap / 2.0, oy, oy + lh,
                                    CLR["stroke"], 1))
            cx += widths[i] + gap
    return kids


def cta(kids, rec, x, y, w, h, size):
    rec.panel("cta", x, y, w, h)
    inner = rec.t("cta", C["cta"], 16, (h - cell(size)) / 2.0, w - 32, size,
                  align="CENTER", style="BOLD", color=CLR["bg"], origin=(x, y))
    kids.append(D.box(x, y, w, h, color=ACC_A, radius=RAD["cta"],
                      children=[D.el("Stack", {"fit": "EXPAND"}, [inner])]))


def site(kids, rec, x, y, w, size, labelled):
    if labelled:
        kids.append(rec.t("label:website", LBL["site"], x, y, 52, size,
                          color=CLR["text_muted"]))
        kids.append(rec.t("website", C["website"], x + 52, y, w - 52, size, mono=True,
                          color=CLR["accent_2"], font=D.MONO, style="BOLD",
                          optical=0.05 * size))
    else:
        kids.append(rec.t("website", C["website"], x, y, w, size, mono=True,
                          color=CLR["accent_2"], font=D.MONO, style="BOLD",
                          optical=0.05 * size))


def comp_dashed_v(x, y0, y1, color, w=2, dash=8, gap=10):
    """Vertical dashed rule - dsllib.dashed() only emits horizontal segments."""
    out, y = [], min(y0, y1)
    while y < max(y0, y1):
        seg = min(dash, max(y0, y1) - y)
        out.append(D.box(x - w / 2.0, y, w, seg, color=color))
        y += dash + gap
    return out


def step_card(kids, rec, x, y, w, h, card, idx, chip, chip_fs, tsize, dsize,
              mark, mark_pos, pad, div=None):
    """One of the six step cards - same construction at every breakpoint."""
    i = idx + 1
    kids.append(D.box(x, y, w, h, color=CLR["surface"], radius=RAD["card"],
                      border="1 SOLID " + CLR["stroke"]))
    kids += comp_corner_ticks(x + 10, y + 10, w - 20, h - 20, 12, 2, ACC6 + "33")
    kids.append(comp_index_chip(rec, "cards[%d].chip" % idx, x + pad, y + pad,
                                chip, "%02d" % i, chip_fs))
    tx = pad + chip + 10
    head = pad + max(chip, cell(tsize))
    kids.append(rec.t("cards[%d].title" % idx, card["title"], x + tx,
                      y + pad + (chip - cell(tsize)) / 2.0, w - pad - 10 - tx,
                      tsize, style="BOLD", color=CLR["text_primary"]))
    dy = y + head + 10
    if div:
        # the rule belongs between the head and the detail, never on the title baseline
        kids.append(D.dashed(x + pad, x + w - pad, y + head + 26, ACC6 + "4D", 2, 7, 6))
        dy += div
    kids.append(rec.t("cards[%d].detail" % idx, card["detail"], x + pad, dy,
                      w - 2 * pad, dsize, color=CLR["text_secondary"]))
    if mark:
        mw = need("%02d" % i, mark, True, D.MONO) + 4
        inset = 10 if mark_pos == "mid" else 0
        my = {"top": y + pad, "bottom": y + h - pad - cell(mark)}.get(
            mark_pos, y + (h - cell(mark)) / 2.0)
        kids.append(rec.t("cards[%d].index" % idx, "%02d" % i,
                          x + w - pad - inset - mw, my,
                          mw, mark, align="RIGHT", mono=True, font=D.MONO,
                          style="BOLD", color=ACC6 + "33"))
    rec.panel("card:%d" % i, x, y, w, h)
    return kids


# ==========================================================================
# breakpoint composers
# ==========================================================================
def compose_mobile():
    b = BP["mobile"]
    W, H, M = b["w"], b["h"], b["m"]
    X0, X1, CW = M, W - M, W - 2 * M
    rec = Rec("mobile")
    kids = comp_grid(0, 0, W, H, b["pitch"])
    kids += comp_corner_ticks(M - 6, 12, CW + 12, H - 24, 16, 2, CLR["stroke"])

    y = hero(kids, rec, X0, 20, CW, b["main_title"], [C["title"]], b["subtitle"])
    my = y + 10
    meta(kids, rec, X0, my, CW, 92, "rows", b["label"], b["meta"])
    cta(kids, rec, X0, my + 102, CW, 44, b["cta"])
    site(kids, rec, X0, my + 152, CW, b["website"], True)
    kids.append(D.hline(X0, X1, my + 190, CLR["stroke"], 1))

    top = my + 190 + 12
    gap = 8
    ch = (H - M - top - gap * 5) / 6.0
    pad = (ch - (max(24, cell(b["card_title"])) + 4 + cell(b["card_detail"]))) / 2.0
    for i, c in enumerate(C["cards"]):
        step_card(kids, rec, X0, top + i * (ch + gap), CW, ch, c, i,
                  24, b["meta"], b["card_title"], b["card_detail"],
                  b["ghost"], "mid", pad)
    return rec, kids, W, H


def compose_tablet():
    b = BP["tablet"]
    W, H, M = b["w"], b["h"], b["m"]
    X0, X1, CW = M, W - M, W - 2 * M
    rec = Rec("tablet")
    kids = comp_grid(0, 0, W, H, b["pitch"])
    kids += comp_corner_ticks(M - 14, 24, CW + 28, H - 48, 24, 2, CLR["stroke"])

    y = hero(kids, rec, X0, 40, CW, b["main_title"], [C["title"]], b["subtitle"])
    my = y + 12
    meta(kids, rec, X0, my, CW, 96, "cols", b["label"], b["meta"])
    cta(kids, rec, X0, my + 110, 340, 58, b["cta"])
    site(kids, rec, X0 + 360, my + 128, CW - 360, b["website"], False)
    kids.append(D.hline(X0, X1, my + 196, CLR["stroke"], 1))
    kids.append(rec.t("label:steps", LBL["steps"], X0, my + 208, 200, b["label"],
                      color=ACC_A, style="BOLD"))

    top = my + 208 + cell(b["label"]) + 14
    gap = 22
    cw = (CW - gap) / 2.0
    ch = (H - M - top - gap * 2) / 3.0
    kids += comp_dashed_v(X0 + cw + gap / 2.0, top + 33,
                          top + 2 * (ch + gap) + 33, ACC6 + "4D", 2, 8, 10)
    for i, c in enumerate(C["cards"]):
        step_card(kids, rec, X0 + (i % 2) * (cw + gap), top + (i // 2) * (ch + gap),
                  cw, ch, c, i, 26, b["label"], b["card_title"], b["card_detail"],
                  b["ghost"], "bottom", 20)
    return rec, kids, W, H


def compose_desktop():
    b = BP["desktop"]
    W, H, M = b["w"], b["h"], b["m"]
    X0, X1 = M, W - M
    rec = Rec("desktop")
    kids = comp_grid(0, 0, W, H, b["pitch"])

    HW = 510
    y = hero(kids, rec, X0, 60, HW, 72, ["Structure /", "Vision"], 28)
    my = y + 20
    meta(kids, rec, X0, my, HW, 124, "cols", b["label"], b["meta"], pad=14, gap=14)
    cta(kids, rec, X0, my + 144, 400, 72, b["cta"])
    kids += comp_ring(X0 + (HW - 110) / 2.0, 606, 110, 2, CLR["stroke"])
    kids += comp_ring(X0 + (HW - 62) / 2.0, 630, 62, 2, ACC6 + "33")
    kids += comp_step_rail(X0 + 40, X0 + HW - 40, 760, 6, 14)
    kids.append(D.hline(X0, X0 + HW, 796, CLR["stroke"], 1))
    kids.append(rec.t("website", C["website"], X0, 810, HW, b["website"], mono=True,
                      align="RIGHT", color=CLR["accent_2"], font=D.MONO,
                      style="BOLD", optical=0.05 * b["website"]))

    CX0 = X0 + HW + 48
    CW = X1 - CX0
    kids.append(rec.t("label:steps.cards", LBL["steps"], CX0, 48, 200, b["label"],
                      color=ACC_A, style="BOLD"))
    kids.append(D.hline(CX0, X1, 79, CLR["stroke"], 1))
    gap, ch, top = 20, 340, 96
    cw = (CW - gap * 2) / 3.0
    for i, c in enumerate(C["cards"]):
        step_card(kids, rec, CX0 + (i % 3) * (cw + gap), top + (i // 3) * (ch + 28),
                  cw, ch, c, i, 30, b["label"], b["card_title"], b["card_detail"],
                  b["ghost"], "bottom", 18, div=46)
    return rec, kids, W, H


def compose_stage():
    b = BP["stage"]
    W, H, M = b["w"], b["h"], b["m"]
    X0, X1, CW = M, W - M, W - 2 * M
    rec = Rec("stage")
    kids = comp_grid(0, 0, W, H, b["pitch"])
    kids += comp_ring(W - 430, -110, 420, 2, CLR["stroke"])
    kids += comp_ring(W - 372, -38, 304, 2, ACC6 + "33")

    hero(kids, rec, X0, 72, 1000, b["main_title"], ["Structure /", "Vision"],
         b["subtitle"])
    RX, RW = 1180, X1 - 1180
    meta(kids, rec, RX, 72, RW, 104, "cols", b["label"], b["meta"], pad=16, gap=16)
    cta(kids, rec, RX, 190, 520, 76, b["cta"])
    site(kids, rec, RX, 276, RW, b["website"], False)
    kids.append(D.hline(X0, X1, 470, CLR["stroke"], 1))
    kids.append(rec.t("label:steps", LBL["steps"], X0, 496, 150, b["label"],
                      color=ACC_A, style="BOLD"))
    kids += comp_step_rail(X0 + 190, X1, 508, 6, 12, CLR["gold"])

    gap = 20
    cw = (CW - gap * 5) / 6.0
    ch, top = 380, 570
    for i, c in enumerate(C["cards"]):
        step_card(kids, rec, X0 + i * (cw + gap), top, cw, ch, c, i,
                  30, b["label"], b["card_title"], b["card_detail"],
                  b["ghost"], "bottom", 22, div=46)
    kids += comp_step_rail(X0 + cw / 2.0, X0 + CW - cw / 2.0, top + ch + 46, 6, 14)
    return rec, kids, W, H


COMPOSERS = [("mobile", compose_mobile), ("tablet", compose_tablet),
             ("desktop", compose_desktop), ("stage", compose_stage)]

LAYOUT_NOTES = {
    "mobile": "single column, top to bottom: accent tick, one-line main title, "
              "subtitle, date/time/location definition list, full-width CTA button, "
              "labelled website line, hairline, then six step cards stacked 1x6 with "
              "the ghost index centred on the right of each card",
    "tablet": "full-width hero band (one-line title, subtitle, 3-column labelled meta "
              "strip), CTA button with the website on the same row, then six step cards "
              "as 2 columns x 3 rows linked by a vertical dashed rail in the gutter",
    "desktop": "split composition: hero column on the left (two-line 72 px title, "
               "subtitle, 3-column meta strip, 72 px CTA, ring ornament, six-node rail "
               "and a hairline footer carrying the right-aligned website) and the six "
               "step cards as 3 columns x 2 rows on the right",
    "stage": "wide poster: two-line 96 px title and subtitle left of the hero band, meta "
             "strip + CTA + website on the right, then all six step cards in one "
             "horizontal pipeline row between a gold rail above and an accent rail below",
}

INPUT_FIELDS = ["title", "subtitle", "date", "time", "location", "cta", "website"] + \
               ["cards[%d].title" % i for i in range(6)] + \
               ["cards[%d].detail" % i for i in range(6)]


def band_overlap(a, c):
    return (a["gx0"] < c["gx1"] - 0.5 and c["gx0"] < a["gx1"] - 0.5 and
            a["gy0"] < c["gy1"] - 0.5 and c["gy0"] < a["gy1"] - 0.5)


def check(name, rec, W, H):
    b = BP[name]
    M = b["m"]
    p = list(rec.issues)
    for t in rec.texts:
        if t["size"] < b["body_min"] - 1e-6:
            p.append("FONT_BELOW_MIN %s %s %.1f<%d" % (name, t["field"], t["size"],
                                                       b["body_min"]))
        if t["field"] == "title" and t["size"] < 40 and name != "mobile":
            p.append("MAIN_TITLE_BELOW_40 %s" % name)
        if t["field"] == "cards[%d].title" % 0 and t["size"] < 18:
            p.append("CARD_TITLE_BELOW_18 %s" % name)
        if (t["x"] < M - 1e-6 or t["x"] + t["w"] > W - M + 1e-6 or
                t["y"] < 0 or t["y"] + t["h"] > H):
            p.append("SAFE_MARGIN %s %s (%.1f,%.1f,%.1f,%.1f) margin=%d"
                     % (name, t["field"], t["x"], t["y"], t["w"], t["h"], M))
        if t["gy1"] > H + 0.5 or t["gx1"] > W + 0.5 or t["gx0"] < -0.5 or t["gy0"] < -0.5:
            p.append("OUT_OF_CANVAS %s %s ink=(%.1f,%.1f)-(%.1f,%.1f)"
                     % (name, t["field"], t["gx0"], t["gy0"], t["gx1"], t["gy1"]))
    for i in range(len(rec.texts)):
        for j in range(i + 1, len(rec.texts)):
            if band_overlap(rec.texts[i], rec.texts[j]):
                p.append("TEXT_BAND_OVERLAP %s %s <-> %s"
                         % (name, rec.texts[i]["field"], rec.texts[j]["field"]))
    exp = {"subtitle": C["subtitle"], "date": C["date"], "time": C["time"],
           "location": C["location"], "cta": C["cta"], "website": C["website"]}
    for i, c in enumerate(C["cards"]):
        exp["cards[%d].title" % i] = c["title"]
        exp["cards[%d].detail" % i] = c["detail"]
    joined = ""
    for t in rec.texts:
        if t["field"] == "title":
            joined += t["shown"]
        elif t["field"] in exp and t["shown"] != exp[t["field"]]:
            p.append("VALUE_MISMATCH %s %s %r != %r"
                     % (name, t["field"], t["shown"], exp[t["field"]]))
    if "".join(joined.split()) != "".join(C["title"].split()):
        p.append("VALUE_MISMATCH %s title %r != %r" % (name, joined, C["title"]))
    for f in INPUT_FIELDS:
        if not any(t["field"] == f for t in rec.texts):
            p.append("FIELD_MISSING %s %s" % (name, f))
    return p


def tokens():
    return {
        "task": TASK, "run_id": S.RUN,
        "source": "tasks/A12-responsive-system/inputs/content.json",
        "color": {k: {"hex": v} for k, v in CLR.items()},
        "color_roles": {
            "bg": "page background", "surface": "card and panel fill",
            "surface_alt": "reserved inset fill",
            "stroke": "1 px card/panel border and corner ticks",
            "grid_line": "decorative grid hairline (4% white)",
            "text_primary": "main title, card title, meta value, CTA text",
            "text_secondary": "subtitle, card detail",
            "text_muted": "field labels",
            "accent": "accent tick, index chip fill, CTA fill, dashed rails, ghost index",
            "accent_2": "website line", "gold": "stage hero rail only"},
        "type": {
            "families": {"ui": D.UI, "display": D.LATIN, "mono": D.MONO},
            "line_cell_ratio": CELL_R,
            "measured_metrics": {
                "source": "tmp/20261004-182918/A12/font-metrics-2.json and glyph-band.json",
                "cjk_em_per_char": 0.9938, "inter_upper_em": 0.65,
                "inter_lower_em": 0.55, "space_em": 0.20, "slash_em": 0.40,
                "middot_em": 0.40, "digit_em": 0.58,
                "mono_em_per_char": MONO_ADV, "mono_measured_ink_em_per_char": 0.5935,
                "ink_band_top_em": BAND_TOP, "ink_band_height_em": BAND_H},
            "scale": {k: {"main_title": v["main_title"], "subtitle": v["subtitle"],
                          "card_title": v["card_title"],
                          "card_detail": v["card_detail"], "meta_value": v["meta"],
                          "label": v["label"], "cta": v["cta"],
                          "website": v["website"], "ghost_index": v["ghost"]}
                      for k, v in BP.items()},
            "minimums": {"mobile": {"body": 16, "card_title": 18},
                         "tablet": {"body": 20, "main_title": 40},
                         "desktop": {"body": 20, "main_title": 40},
                         "stage": {"body": 20, "main_title": 40}},
            "hierarchy": ["main title", "subtitle", "card title",
                          "card detail / meta value", "field label", "ghost index"],
        },
        "space": {
            "page_margin": {k: v["m"] for k, v in BP.items()},
            "min_safe_margin_required": {k: v["min_margin"] for k, v in BP.items()},
            "card_gap": {"mobile": 8, "tablet": 22, "desktop": 20, "stage": 20},
            "grid_pitch": {k: v["pitch"] for k, v in BP.items()},
        },
        "radius": dict(RAD),
        "stroke": {"hairline": 1, "border": 1, "corner_tick": 2, "rail": 2, "ring": 2},
        "grid": {k: {"columns": v["cols"], "card_rows": v["rows"]}
                 for k, v in BP.items()},
        "components": {
            "accent_tick": "rounded accent bar, width max(44, 0.9*mainTitle), height 5",
            "grid_field": "1 px page-coloured hairlines at the breakpoint grid pitch",
            "index_chip": "rounded square, accent fill, bg-coloured mono 01-06",
            "ghost_index": "accent 20% alpha mono numeral; vertically centred on mobile, "
                           "bottom-right elsewhere",
            "corner_ticks": "four L brackets; canvas edge (stroke) on mobile, "
                            "card edge (accent 20%) elsewhere",
            "step_rail": "dashed rail with exactly 6 hollow nodes on every "
                         "breakpoint; horizontal above/below the stage row, in the "
                         "tablet gutter (vertical), and above the desktop footer",
            "ring": "outline-only circle, large-scale texture",
            "meta_strip": "surfaced panel with date/time/location verbatim; labelled rows "
                          "on mobile, 3 labelled columns elsewhere",
            "cta_button": "accent rounded button, CTA text verbatim in bg bold",
            "site_line": "mono accent-2 website line; labelled on mobile only",
            "step_card": "surface card = index chip + card title + card detail + "
                         "(optional dashed rule) + ghost index + corner ticks",
        },
        "rules_enforced": {
            "image_tags_emitted": 0, "no_external_assets": True,
            "no_crop_or_scale": "each canvas is an independently generated layout",
            "text_fit": "every text box width >= the measured advance width and height "
                        "= 1.55 * fontSize, so no line wraps or is clipped",
        },
    }


def main():
    t0 = time.time()
    first_image = None
    results, problems = [], []
    cmap = {"task": TASK, "run_id": S.RUN,
            "source": "tasks/A12-responsive-system/inputs/content.json",
            "adaptation_method": "one generator, one content set and one token set emit "
                                 "four independent absolute-positioned DSL documents; "
                                 "nothing is cropped, scaled, or re-used as an image",
            "measured_width_model": "tmp/20261004-182918/A12/font-metrics-2.json",
            "input_fields": {}, "canvases": []}
    for f in ["title", "subtitle", "date", "time", "location", "cta", "website"]:
        cmap["input_fields"][f] = {"value": C[f], "chars": len(C[f])}
    for i, c in enumerate(C["cards"]):
        for k in ["id", "title", "detail"]:
            cmap["input_fields"]["cards[%d].%s" % (i, k)] = {
                "value": c[k], "chars": len(c[k])}

    for name, fn in COMPOSERS:
        rec, kids, W, H = fn()
        dsl = D.snapshot([D.stack(kids, W, H)], W, H, bg=CLR["bg"])
        v = 1
        while os.path.exists(os.path.join(DRAFTS, "%s-v%02d.snapshot" % (name, v))):
            v += 1
        with open(os.path.join(DRAFTS, "%s-v%02d.snapshot" % (name, v)), "w",
                  encoding="utf-8", newline="\n") as fh:
            fh.write(dsl)
        before = len(D.WARNINGS)
        r = snapkit.render(dsl, "%s.png" % name, "%s.snapshot" % name, final=True)
        if r.get("ok") and first_image is None:
            first_image = snapkit.now_iso()
        probs = check(name, rec, W, H)
        problems += probs
        print("== %-7s %dx%d  widgets=%d  dsl=%dB  ok=%s status=%s bytes=%s"
              % (name, W, H, len(kids), len(dsl), r.get("ok"), r.get("status"),
                 r.get("bytes")))
        if not r.get("ok"):
            print("   ERROR:", (r.get("error") or "")[:600])
        for wn in D.WARNINGS[before:]:
            print("   WARN", wn)
        for p in probs:
            print("   CHECK", p)
        b = BP[name]
        cmap["canvases"].append({
            "canvas": name, "width": W, "height": H,
            "png": "%s.png" % name, "snapshot": "%s.snapshot" % name,
            "safe_margin_px": b["m"], "required_safe_margin_px": b["min_margin"],
            "grid": {"columns": b["cols"], "card_rows": b["rows"], "card_count": 6},
            "layout": LAYOUT_NOTES[name],
            "render_ok": bool(r.get("ok")), "request_id": r.get("request_id_local"),
            "service_request_id": r.get("request_id"),
            "layout_problems": probs,
            "text_boxes": len(rec.texts), "widgets": len(kids),
            "content_fields": [
                {"field": t["field"], "input_value": t["value"],
                 "drawn_text": t["shown"], "font_size": t["size"],
                 "font": "mono" if t["mono"] else "ui", "font_family": t["font"],
                 "text_color": t["color"],
                 "box": {"x": t["x"], "y": t["y"], "w": t["w"], "h": t["h"]},
                 "ink_extent": {"x0": t["gx0"], "x1": t["gx1"],
                                "y0": t["gy0"], "y1": t["gy1"]},
                 "expected_ink_px": t["ink_w"],
                 "required_box_px": t["need_w"], "lines": 1,
                 "status": "verbatim" if t["shown"] == t["value"]
                           else "verbatim_split_across_lines",
                 "abbreviated": False, "truncated": False, "wrapped": False}
                for t in rec.texts if t["field"] in INPUT_FIELDS],
            "design_chrome_text": [
                {"text": t["shown"], "font_size": t["size"],
                 "box": {"x": t["x"], "y": t["y"], "w": t["w"], "h": t["h"]}}
                for t in rec.texts if t["field"].startswith("label:")],
            "panels": rec.panels,
        })
        results.append({"name": name, "w": W, "h": H, "ok": bool(r.get("ok")),
                        "png": r.get("image"), "dsl": r.get("dsl"),
                        "requests": r.get("request_id_local"),
                        "widgets": len(kids)})
    cmap["summary"] = {
        "input_field_count": len(cmap["input_fields"]),
        "canvas_count": len(results),
        "all_fields_on_all_canvases": not any(
            x.startswith("FIELD_MISSING") or x.startswith("VALUE_MISMATCH")
            for x in problems),
        "content_omitted_or_abbreviated": "none",
        "design_chrome_note": "\u65e5\u671f/\u65f6\u95f4/\u5730\u70b9/\u5b98\u7f51/"
                               "\u516d\u4e2a\u73af\u8282 are added field labels only; every "
                               "input value is drawn verbatim on all four canvases",
        "qr_code": "not required; the CTA is delivered as text",
        "images_embedded": 0,
        "problems_total": len(problems),
    }
    with open(os.path.join(OUT, "content-map.json"), "w", encoding="utf-8") as fh:
        json.dump(cmap, fh, ensure_ascii=False, indent=2)
    with open(os.path.join(OUT, "design-tokens.json"), "w", encoding="utf-8") as fh:
        json.dump(tokens(), fh, ensure_ascii=False, indent=2)
    with open(os.path.join(TMP, "build-state.json"), "w", encoding="utf-8") as fh:
        json.dump({"results": results, "problems": problems,
                   "first_image_at": first_image,
                   "elapsed": round(time.time() - t0, 1)},
                  fh, ensure_ascii=False, indent=2)
    print("TOTAL PROBLEMS:", len(problems), "| first image:", first_image)
    return results, problems, first_image, t0


if __name__ == "__main__":
    main()
