"""brand.py - the shared editorial identity of the B04 special issue.

One visual system for all ten works (the task allows a unified style when a special issue
needs one), while each work keeps its own structure. Every number printed on a B04 sheet
comes from scripts/ozone.py (NASA Ozone Watch) or from the published figures recorded in
research/sources-draft.json; the helper `source_line()` makes the provenance visible on the
artwork itself.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sk import Sk, tw, alpha, MONO, CJK, INTER, SERIF  # noqa: E402
import std  # noqa: E402

# ---- palette
NIGHT = "#0B1226FF"
DEEP = "#122040FF"
CARD = "#16264AFF"
LINE = "#25375FFF"
PAPER = "#F5F8FCFF"
INK = "#0E1729FF"
SOFT = "#5C6B85FF"
RULE = "#D7DEE9FF"
VIOLET = "#7C6BF0FF"
CYAN = "#38BDF8FF"
TEAL = "#2DD4BFFF"
AMBER = "#F5A524FF"
RED = "#EF4444FF"
GREEN = "#34D399FF"

ISSUE = "STRATOSPHERE REVIEW"
ISSUE_NO = "ISSUE 07 · 2026"
EDITOR = "edited by R. Okonjo-Vale"


def masthead(s: Sk, title, standfirst, accent=CYAN, w=0, x=48, y=34, dark=True,
             size=34, sub_size=15, kicker=None, kicker2=None):
    """Standard masthead: kicker rail, title, standfirst, optional kicker line.

    The standfirst is wrapped first so the kicker cannot be overprinted by a second line -
    case-02 v1 lost the end of its standfirst under the kicker that way.
    """
    fg = PAPER if dark else INK
    dim = "#9FB0CCFF" if dark else SOFT
    s.box(x, y, 4, size * 1.9, accent)
    s.text(x + 18, y - 2, f"{ISSUE} · {ISSUE_NO}", 12, accent, "BOLD", MONO, spacing=1)
    s.text(x + 18, y + 18, title, size, fg, "BOLD", INTER)
    ty = y + 18 + size * 1.16
    if standfirst:
        maxw = (w - 120) if w else 1200
        s.para(x + 18, ty, standfirst, sub_size, dim, maxw)
        ty += s.para_height(standfirst, sub_size, maxw) + 6
    if kicker:
        s.text(x + 18, ty, kicker, 12, dim, family=MONO)
        ty += 20
    return ty + 8


def source_line(s: Sk, x, y, text, w=0, color=None, dark=True, size=11, align="CENTER_LEFT"):
    c = color or ("#6C7C99FF" if dark else "#7A8699FF")
    s.text(x, y, text, size, c, w=w if w else None, align=align, family=MONO)


def footer(s: Sk, x, y, w, left, right, dark=True, size=11):
    c = "#6C7C99FF" if dark else "#7A8699FF"
    s.text(x, y, left, size, c, family=MONO)
    s.text(x, y, right, size, c, w=w, align="CENTER_RIGHT", family=MONO)


def source_footer(s: Sk, x, y, w, refs, note="", dark=True):
    """The provenance strip: which sources this sheet used."""
    c = "#6C7C99FF" if dark else "#7A8699FF"
    s.box(x, y - 12, w, 1, alpha("#7C8CB0", "40") if dark else alpha("#8894A8", "55"))
    s.text(x, y, "SOURCES  " + refs, 11, c, family=MONO, w=w)
    if note:
        s.text(x, y + 18, note, 11, c, family=MONO, w=w)


def figure_no(s: Sk, x, y, n, kind, dark=True):
    c = CYAN if dark else "#1D4ED8FF"
    s.text(x, y, f"FIG. {n}", 13, c, "BOLD", MONO)
    s.text(x + 62, y, kind, 12, "#8FA0BCFF" if dark else SOFT, family=MONO)


def fact_panel(s: Sk, x, y, w, h, label, value, unit="", note="", accent=CYAN,
               dark=True, value_size=40):
    s.box(x, y, w, h, CARD if dark else "#FFFFFFFF",
          radius=8, border=f"1 SOLID {LINE if dark else RULE}")
    s.box(x, y, 4, h, accent)
    s.text(x + 18, y + 14, label.upper(), 11, "#9FB0CCFF" if dark else SOFT, "BOLD", MONO)
    s.text(x + 18, y + 36, value, value_size, PAPER if dark else INK, "BOLD", INTER)
    vw = tw(value, value_size)
    if unit:
        s.text(round(x + 30 + vw, 2), y + 36 + value_size * 0.42, unit, 14,
               "#9FB0CCFF" if dark else SOFT, family=MONO)
    if note:
        std.text_fit(s, x + 18, y + 36 + value_size * 1.28, note, 12,
                     "#8FA0BCFF" if dark else SOFT, w - 34, fam=MONO)


def confidence(s: Sk, x, y, level, dark=True):
    col = {"high": GREEN, "medium": AMBER, "low": RED}.get(level.lower(), SOFT)
    txt = level.upper()
    w = tw(txt, 11, mono=True) + 20
    s.box(x, y, round(w, 2), 22, alpha(col, "26"), radius=11,
          border=f"1 SOLID {alpha(col, 'AA')}")
    s.text(x, y + 4, txt, 11, col, "BOLD", MONO, w=round(w, 2), align="CENTER")
    return w


def chip(s: Sk, x, y, txt, col, dark=True, size=11):
    w = tw(txt, size, mono=True) + 18
    s.box(x, y, round(w, 2), 20, alpha(col, "22"), radius=10,
          border=f"1 SOLID {alpha(col, '99')}")
    s.text(x, y + 3, txt, size, col, "BOLD", MONO, w=round(w, 2), align="CENTER")
    return w


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    return path
