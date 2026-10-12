# -*- coding: utf-8 -*-
"""A24 - shared visual system for the three release-plan figures.

One module holds the palette, the type scale, the team colours and the few
primitives (chips, stat tiles, legends) so that execution-board / decision-brief
/ action-card are unmistakably one family while keeping their own layouts.
Every number comes from plan.py, which reads inputs/release.json - nothing is
typed in by hand.
"""
from __future__ import annotations

import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
SUITE = os.path.join(ROOT, "tmp", "20261004-182918", "_suite")
sys.path.insert(0, SUITE)
import dsllib as D  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import plan as P  # noqa: E402

# ------------------------------------------------------------------ palette
INK = "#0F172AFF"
INK2 = "#1E293BFF"
MUTED = "#475569FF"
FAINT = "#94A3B8FF"
LINE = "#E2E8F0FF"
LINE2 = "#CBD5E1FF"
PAPER = "#F3F5FBFF"
CARD = "#FFFFFFFF"
DARK = "#101836FF"
DARK2 = "#1B2650FF"
BRAND = "#4F46E5FF"
BRAND_L = "#E8EAFDFF"

DESIGN = "#4338CAFF"
DESIGN_L = "#E9EAFBFF"
ENG = "#0E7490FF"
ENG_L = "#E2F2F6FF"

CP = "#BE185DFF"
CP_L = "#FCE7F3FF"
AMBER = "#B45309FF"
AMBER_L = "#FEF3C7FF"
GREEN = "#047857FF"
GREEN_L = "#D8F5E7FF"
RED = "#DC2626FF"
RED_L = "#FEE2E2FF"
WHITE = "#FFFFFFFF"

UI = "Inter,Noto Sans CJK SC"
MONO = "DejaVu Sans Mono,Noto Sans Mono CJK SC"

BRAND_NAME = "叠光 · 发布演练"
TEAM_ZH = {"design": "设计", "engineering": "工程"}
TEAM_COLOR = {"design": DESIGN, "engineering": ENG}
TEAM_LIGHT = {"design": DESIGN_L, "engineering": ENG_L}
TEAM_BAR = {"design": DESIGN, "engineering": ENG}

BY_ID = {t["id"]: t for t in P.SCHEDULE["tasks"]}
RISKS = {r["id"]: r for r in P.SRC["risks"]}
RISK_OF_TASK = {}
for _r in P.SRC["risks"]:
    RISK_OF_TASK.setdefault(_r["task"], []).append(_r)
CP_CHAIN = set(P.SCHEDULE["summary"]["schedule_critical_chain"])


def span(t):
    """'HH:MM-HH:MM' in a single fixed format used by all three figures."""
    return "%s–%s" % (BY_ID[t]["start_clock"], BY_ID[t]["end_clock"])


def rng(t):
    return "%s–%s" % (BY_ID[t]["start_clock"], BY_ID[t]["end_clock"])


def mw(s, size, pad=16, factor=1.12):
    """Width for a Text drawn in the monospace stack. DejaVu Sans Mono advances 0.602em
    where est_width assumes 0.55em, so mono boxes need a factor plus slack; a single-line
    Text that does not fit is silently dropped by the service."""
    return D.est_width(s, size) * factor + pad


def wraps(text, size, width):
    lines, cur, w = [], "", 0.0
    tokens, buf = [], ""
    for ch in text:
        if ord(ch) > 0x2E80 or ch in "，。、：；！？（）《》“”·—…→←·":
            if buf:
                tokens.append(buf)
                buf = ""
            tokens.append(ch)
        elif ch == " ":
            buf += ch
            tokens.append(buf)
            buf = ""
        else:
            buf += ch
    if buf:
        tokens.append(buf)
    for tok in tokens:
        tw = D.est_width(tok, size)
        if cur and w + tw > width:
            lines.append(cur.rstrip())
            # strip ASCII spaces only: U+3000 is Python whitespace but is used here as a
            # deliberate hanging indent and must survive
            cur, w = tok.lstrip(" "), D.est_width(tok.lstrip(" "), size)
        else:
            cur += tok
            w += tw
    if cur.strip():
        lines.append(cur.rstrip())
    return lines or [""]


def para(text, size, width, x, y, color=MUTED, lh=1.5, font=UI, align=None, bold=None):
    out, yy = [], y
    for ln in wraps(text, size, width):
        out.append(D.text_el(ln, x=x, y=yy, w=width, h=size * 1.4, size=size,
                             color=color, font=font, align=align, style=bold))
        yy += size * lh
    return out, yy


def bd(c):
    """The DSL border attr needs '<width> <STYLE> <color>'; accept a bare colour too."""
    if c is None:
        return None
    s = str(c)
    return s if s[:1].isdigit() else "1 SOLID %s" % s


def chip(x, y, w, h, label, size=20, fill=CARD, line=LINE, color=INK, radius=999,
         font=UI, bold=None, shadow=None):
    kids = []
    # The two pieces must be sibling Positioned nodes: a Positioned nested inside the
    # chip's Container makes the service fail with parentData must be StackParentData.
    return "\n".join([
        D.box(x, y, w, h, color=fill, radius=min(radius, h / 2.0), border=bd(line),
              shadow=shadow),
        D.text_el(label, x=x, y=y + (h - size * 1.25) / 2.0, w=w, h=size * 1.35,
                  size=size, color=color, align="CENTER", font=font, style=bold),
    ])


def swatch(x, y, w, h, fill, radius=6, line=None):
    return D.box(x, y, w, h, color=fill, radius=radius, border=bd(line))


def legend(x, y, items, size=20, gap=34, sw=26):
    """items: (color, text) or (color, text, line) - returns kids and end x."""
    out, cx = [], x
    for it in items:
        col, text = it[0], it[1]
        ln = it[2] if len(it) > 2 else None
        out.append(swatch(cx, y + (size - sw) / 2.0, sw, sw, col, radius=6, line=ln))
        out.append(D.text_el(text, x=cx + sw + 10, y=y + (size * 1.25 - sw) / 2.0,
                             w=D.est_width(text, size) + 8, h=size * 1.35, size=size,
                             color=MUTED))
        cx += sw + 10 + D.est_width(text, size) + gap
    return out, cx


def assign_rows(items, rows=2):
    """items: [(x, width)] -> row index per item, first-fit, stable in x order."""
    order = sorted(range(len(items)), key=lambda i: items[i][0])
    taken = [[] for _ in range(rows)]
    out = [0] * len(items)
    for i in order:
        x, w = items[i]
        for r in range(rows):
            if all(x + w <= ox or ox + ow <= x for ox, ow in taken[r]):
                taken[r].append((x, w))
                out[i] = r
                break
        else:
            out[i] = rows - 1
    return out
