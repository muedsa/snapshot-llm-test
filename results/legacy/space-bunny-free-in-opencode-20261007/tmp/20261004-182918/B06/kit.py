# -*- coding: utf-8 -*-
"""B06 kit - reuses the suite's proven component library and adds the
tokens for the "ten everyday information problems" portfolio.

Reuse is deliberate and recorded in problem-evidence.json / snapshot-usage.md:
every helper, every DSL pitfall handled here was already verified against the
live open-snapshot service earlier in this same run (A01-A24, B01-B04). B06 does
NOT re-probe them, it only re-uses them.
"""
from __future__ import annotations

import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
SUITE = os.path.join(ROOT, "tmp", "20261004-182918", "_suite")
B01 = os.path.join(ROOT, "tmp", "20261004-182918", "B01")
for p in (SUITE, B01):
    if p not in sys.path:
        sys.path.insert(0, p)

import dsllib as D          # noqa: E402
import atelier as _A        # noqa: E402  (proven component library, B01)
import snapkit              # noqa: E402

# Re-export the whole library so case scripts import exactly one module.
from atelier import (  # noqa: E402,F401
    A, mix, bd, grad, tw, wraps, label, para, one_line, mono, ctr, rule, vrule,
    plate, card, chip, dot, ring, bar, vbar, seg, polyline, spark, arrow,
    dashed_v, rot_box, font_style, rot_text, glow, vgrad_bar, area, band,
    flat, root, count_elements, check,
    UI, UI_SERIF, MONO, BLACK, SEMI, LIGHT,
)
box = D.box
hline = D.hline
vline = D.vline
dashed = D.dashed
polygon = D.polygon
text_el = D.text_el
snapshot = D.snapshot
stack = D.stack

# --------------------------------------------------------------- B06 palette
INK = "#0B1220FF"
INK2 = "#1E293BFF"
INK3 = "#475569FF"
MUTE = "#94A3B8FF"
HAIR = "#E2E8F0FF"
PAPER = "#F7F8FAFF"
WHITE = "#FFFFFFFF"

# one hue per case so the portfolio reads as ten different objects, not one
# template recoloured ten times
C01 = "#0F766EFF"   # unit price   - deep teal
C02 = "#B45309FF"   # mortgage    - amber
C03 = "#0D9488FF"   # energy      - teal green
C04 = "#BE123CFF"   # lab report  - crimson
C05 = "#7E22CEFF"   # AQI         - violet
C06 = "#1D4ED8FF"   # power bill   - blue
C07 = "#DB2777FF"   # coupon      - pink
C08 = "#15803DFF"   # payslip     - green
C09 = "#EA580CFF"   # telco       - orange
C10 = "#4F46E5FF"   # dosing      - indigo


def ramp(color, n):
    """n tints of one colour, lightest first. Deterministic, no randomness."""
    out = []
    for i in range(n):
        t = i / float(n - 1) if n > 1 else 0.0
        out.append(mix("#FFFFFF", color, 0.16 + 0.74 * t))
    return out