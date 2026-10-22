# -*- coding: utf-8 -*-
"""A21 叠光 Layerlight — design identity + geometry source of truth.

One module drives all three rounds so the brand identity (primary colour,
type scale, 3-6 brand constructs) stays stable while content changes.

Brand concept "叠光 / Layerlight": light passing through stacked layers.
Core constructs (5, stable across rounds):
  1. prism_mark  — a 5-bar "stacked light" mark (bars of one primary hue at
                   descending opacity) + a beam wedge. Geometric, recognisable.
  2. beam_wedge  — a translucent triangle of light leaving the mark.
  3. baseline_rule — a thin full-width rule anchoring the wordmark.
  4. tagline_pill — the mandatory tagline set on a soft tinted pill.
  5. info_plate  — date/speaker/url/cta blocks share one tinted plate style.

Round-01 leaves a real top zone (wordmark band) and a real bottom zone
(info band) that are genuinely usable: the vertical rhythm already reserves
them, but round-01 writes NO placeholder text in them (per requirement).
"""
import math

TASK_ID = "A21"
BRAND_CN = "叠光"
BRAND_EN = "Layerlight"

# ---------------------------------------------------------------- geometry
# canvas top-left origin, x right, y down, px (audit default per template)
SIZES = {
    "portrait": (1080, 1350),
    "wide": (1440, 810),
}

# ------------------------------------------------------------------ colours
# Single primary hue across both images (identical hex = same 主色).
PRIMARY = "#4F46E5"          # indigo — the "light" hue
PRIMARY_DEEP = "#3730A3"
PRIMARY_TINT = "#EEF2FF"     # very light indigo (brand tint / pill fill)
INK = "#141B34"              # main text ink (dark navy)
INK_SOFT = "#39406B"         # secondary text
PAPER = "#FBFAFF"            # near-white page (round 1/2 base)
SURFACE = "#FFFFFF"
MUTED_LINE = "#D9DCF0"
ACCENT = "#F59E0B"           # amber, used only as a brand accent streak

# round-03 light theme tokens (contrast-critical). Backgrounds are LIGHT and
# every text colour below is pre-checked >= 4.5:1 against its real composited
# backdrop (see contrast-audit.py which re-verifies on real pixels).
R3 = {
    "PAPER": "#F4F3FB",
    "SURFACE": "#FFFFFF",
    "PRIMARY": "#372F9B",       # darker indigo so white-on-primary stays high
    "PRIMARY_DEEP": "#2A2378",
    "INK": "#12172E",
    "INK_SOFT": "#2E3557",
    "MUTED_LINE": "#C9CCE8",
    "ACCENT": "#B45309",
}

# ---------------------------------------------------------------- typography
# Noto Sans CJK SC handles both CJK + Latin so hierarchy is identical across
# the two images. Sizes are absolute px.
TYPE = {
    "title": {"size": 60, "line": 1.14, "weight": "BOLD", "color": "INK"},
    "title_r2": {"size": 48, "line": 1.16, "weight": "BOLD", "color": "INK"},
    "brand_cn": {"size": 40, "line": 1.2, "weight": "BOLD", "color": "INK"},
    "brand_en": {"size": 26, "line": 1.2, "weight": "BOLD", "color": "PRIMARY"},
    "eyebrow": {"size": 24, "line": 1.2, "weight": "BOLD", "color": "PRIMARY"},
    "tagline": {"size": 30, "line": 1.3, "weight": "BOLD", "color": "INK"},
    "body": {"size": 26, "line": 1.35, "weight": "NORMAL", "color": "INK_SOFT"},
    "label": {"size": 24, "line": 1.3, "weight": "BOLD", "color": "INK"},
    "date": {"size": 34, "line": 1.2, "weight": "BOLD", "color": "INK"},
    "url": {"size": 26, "line": 1.2, "weight": "BOLD", "color": "PRIMARY"},
    "en": {"size": 24, "line": 1.25, "weight": "BOLD", "color": "INK_SOFT"},
}
FONT = "Noto Sans CJK SC"

# ------------------------------------------------------------------ content
# Stable content IDs (used by content-map.json across rounds). Round-1 text.
REQUIRED = {
    "tagline": "让复杂信息变得清晰",
    "datetime": "2026.11.07 19:30",
    "kicker": "ONLINE LAUNCH",
    "speakers": "讲者：林川 / 苏言",
    "url": "layerlight.example.org",
}
TITLE_R2 = "当所有信息都想成为标题：让复杂信息变得清晰的结构化方法"
SPONSOR_R2 = "Northstar Research / 云构工具"
CTA_R2 = "免费参加 · 无需报名"
EN_R3 = "Clarity through structure"


def measure(text, size):
    """Estimate rendered text width in px (CJK 1em, latin/space narrower).

    Safety factor 1.06 guards against CLIP; callers should give boxes a
    little more room than this returns.
    """
    w = 0.0
    for ch in text:
        o = ord(ch)
        if 0x4E00 <= o <= 0x9FFF or 0xFF00 <= o <= 0xFFEF:
            w += 1.0
        elif ch == " ":
            w += 0.30
        elif ch.isdigit():
            w += 0.56
        elif ch.isupper():
            w += 0.74
        elif ch.islower():
            w += 0.56
        elif ch in "·/()（）：:.,-":
            w += 0.50
        else:
            w += 0.60
    return w * size * 1.06


def wrap(text, size, max_w):
    """Greedy CJK-aware wrap; breaks between CJK chars, keeps latin tokens."""
    lines = []
    cur = ""
    token = ""
    tokens = []
    # tokenise: CJK char = its own token, latin/word runs stay together
    buf = ""
    for ch in text:
        o = ord(ch)
        cjk = 0x4E00 <= o <= 0x9FFF or 0xFF00 <= o <= 0xFFEF or ch in "·：（）/"
        if cjk:
            if buf:
                tokens.append(buf)
                buf = ""
            tokens.append(ch)
        else:
            buf += ch
    if buf:
        tokens.append(buf)

    for tk in tokens:
        trial = cur + tk
        if cur and measure(trial, size) > max_w:
            lines.append(cur.rstrip())
            cur = tk.lstrip() if tk != " " else ""
        else:
            cur = trial
    if cur.strip():
        lines.append(cur.rstrip())
    return lines


def text_h(nlines, size, line_ratio):
    return nlines * size * line_ratio
