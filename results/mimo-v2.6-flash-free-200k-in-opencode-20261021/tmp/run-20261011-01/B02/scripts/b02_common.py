# -*- coding: utf-8 -*-
"""B02 禾风里社区共耕花园 shared design-system helpers + width budgeting.

Design tokens (see plan-v1.json): 宣纸底 paper, 土陶橙 clay, 叶绿 leaf,
深叶绿 leafD, 墨 ink. Reusable components: brand leaf mark, seal, ruler
ticks, section header, price cell, stat bar. All emits are pure DSL strings.

Width budgeting: tw()/fit() estimate rendered text width (CJK≈1em,
ASCII/Latin≈0.56em, digits≈0.56em) and warn at generation time so overflow
is caught before rendering. fit() raises nothing, just warns.
"""
import os

FONT = "Noto Sans CJK SC"

# ---------------- design tokens ----------------
PAPER = "#F7F1E4"     # 宣纸底
PAPER2 = "#FDFAF2"    # 浅纸白卡
CLAY = "#C1502E"      # 土陶橙（主强调）
CLAYD = "#98381D"     # 深土陶
LEAF = "#4A7C4E"      # 叶绿（主色）
LEAFD = "#2F5A38"     # 深叶绿
LEAFL = "#D9E4CE"     # 浅叶绿底
SUN = "#E8A93D"       # 阳光黄（次强调）
INK = "#2E2A25"       # 墨
MUTED = "#7A7264"     # 灰墨
LINE = "#D8CFBC"      # 纸纹线
SOIL = "#6B4A2F"      # 土棕

NAME = "禾风里社区共耕花园"
NAME_S = "禾风里"
LATIN = "HEFENGLI COMMUNITY GARDEN"

# ---------------- shared facts (single source, asserted per case) --------
FACTS = {
    "plots": 12, "plot_size": "3m×4m", "households": 24,
    "market_day": "每周六 09:00–13:00",
    "member_discount": 0.8,
    "basket": [("小份", 29, "1–2 人"), ("中份", 49, "3–4 人"), ("家庭份", 79, "5 人+")],
    "crops8": ["番茄", "黄瓜", "生菜", "空心菜", "辣椒", "茄子", "南瓜", "罗勒"],
    "q3_total": 1286,
    "q3_break": [("番茄", 380), ("黄瓜", 265), ("生菜", 210), ("空心菜", 180),
                 ("辣椒", 126), ("茄子", 95), ("南瓜", 30)],
    "volunteers": 38,
    "compost_in": 2.4, "compost_out": 0.8,
    "class": {"time": "每周六 15:00", "dur": "90 分钟", "age": "6–10 岁",
              "seats": 12, "enrolled": 9},
    "address": "临风路 88 号",
}

MARKET_PRICES = [  # (菜, 单价元/斤, 会员价=round(单价*0.8))
    ("番茄", 6), ("黄瓜", 5), ("生菜", 4), ("空心菜", 4),
    ("辣椒", 8), ("茄子", 5), ("南瓜", 3), ("罗勒", 10),
]


def assert_facts():
    """Cross-case data integrity (G3)."""
    s = sum(v for _n, v in FACTS["q3_break"])
    assert s == FACTS["q3_total"], (s, FACTS["q3_total"])
    for p in MARKET_PRICES:
        assert round(p[1] * FACTS["member_discount"]) == round(p[1] * 0.8)
    assert FACTS["basket"][1][1] == 49
    assert FACTS["class"]["enrolled"] < FACTS["class"]["seats"]


# ---------------- width budgeting ----------------
def tw(s, size):
    """estimated text width in px."""
    w = 0.0
    for ch in s:
        o = ord(ch)
        if o >= 0x2E80:
            w += 1.0
        elif ch in "　":
            w += 1.0
        else:
            w += 0.56
    return w * size


def fit(s, size, budget, tag):
    """warn when estimated width exceeds budget (generation-time guard)."""
    w = tw(s, size)
    if w > budget:
        print("FIT-WARN %s: %.1f > %d | %s" % (tag, w, budget, s[:40]))
    return w


def r2(x):
    return round(float(x), 2)


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


def col(*hexes):
    return ",".join("#%s" % h.lstrip("#") for h in hexes)


# ---------------- core elements (B01-proven forms) ----------------
# Grammar facts (learned from real service responses):
# - Snapshot takes exactly ONE child -> SizedBox > Stack(TOP_LEFT, NONE)
# - absolute placement ONLY via <Positioned left top width height>
# - Text carries text="..." attribute (no inner content), lineHeight="1.28"
# - boxes = Positioned > SizedBox > DecoratedBox (radius/border/boxShadow)

def box(x, y, w, h, color, radius=0, border=None, border_w=1, shadow=None):
    b = (' border="%g SOLID %s"' % (border_w, border)) if border else ""
    s = (' boxShadow="%s"' % shadow) if shadow else ""
    return ('<Positioned left="%g" top="%g" width="%g" height="%g">'
            '<SizedBox width="%g" height="%g"><DecoratedBox color="%s"'
            ' borderRadius="%g"%s%s/></SizedBox></Positioned>'
            % (r2(x), r2(y), r2(w), r2(h), r2(w), r2(h), color, r2(radius),
               s, b))


def grad_box(x, y, w, h, colors, direction="TOP_CENTER", radius=0,
             border=None, border_w=1):
    b = (' border="%g SOLID %s"' % (border_w, border)) if border else ""
    # service gradientBegin/End vocabulary: TOP_LEFT/TOP_CENTER/...,
    # CENTER_LEFT/CENTER/CENTER_RIGHT/BOTTOM_* (no LEFT_CENTER!)
    begin_end = {"TOP_CENTER": ("TOP_CENTER", "BOTTOM_CENTER"),
                 "TOP_LEFT": ("TOP_LEFT", "TOP_RIGHT"),
                 "LEFT_CENTER": ("CENTER_LEFT", "CENTER_RIGHT"),
                 "CENTER_LEFT": ("CENTER_LEFT", "CENTER_RIGHT")}
    bg, ed = begin_end.get(direction, ("TOP_CENTER", "BOTTOM_CENTER"))
    return ('<Positioned left="%g" top="%g" width="%g" height="%g">'
            '<SizedBox width="%g" height="%g">'
            '<Container width="%g" height="%g" gradientType="LINEAR"'
            ' gradientColors="%s" gradientBegin="%s" gradientEnd="%s"'
            ' borderRadius="%g"%s/></SizedBox></Positioned>'
            % (r2(x), r2(y), r2(w), r2(h), r2(w), r2(h), r2(w), r2(h),
               colors, bg, ed, r2(radius), b))


def text(x, y, w, h, s, size, color=INK, bold=False, align="LEFT",
         line_h=None, italic=False):
    fit(s, size, w, "text:%s" % s[:16])
    wt = ""
    if bold:
        wt += ' fontStyle="BOLD"'
    if italic:
        wt += ' fontStyle="ITALIC"'
    return ('<Positioned left="%g" top="%g" width="%g" height="%g">'
            '<Text fontSize="%g" fontFamily="%s" color="%s" textAlign="%s"%s'
            ' lineHeight="%s" text="%s"/></Positioned>'
            % (r2(x), r2(y), r2(w), r2(h), size, FONT, color, align, wt,
               line_h or 1.28, esc(s)))


def circle(cx, cy, r, fill, border=None, border_w=1, shadow=None):
    b = (' border="%g SOLID %s"' % (border_w, border)) if border else ""
    s = (' boxShadow="%s"' % shadow) if shadow else ""
    return ('<Positioned left="%g" top="%g" width="%g" height="%g">'
            '<SizedBox width="%g" height="%g"><DecoratedBox color="%s"'
            ' borderRadius="%g"%s%s/></SizedBox></Positioned>'
            % (r2(cx - r), r2(cy - r), r2(2 * r), r2(2 * r), r2(2 * r),
               r2(2 * r), fill, r2(r), s, b))


def ring(cx, cy, r, pct, color, track="#00000018", width=10):
    """progress ring approximated by arc of small dots (pure DSL)."""
    import math
    out = []
    n = max(6, int(pct / 100.0 * 44))
    for i in range(44):
        ang = -90 + i * (360.0 / 44)
        rad = math.radians(ang)
        c = color if i < n else track
        out.append(circle(cx + (r - width / 2) * math.cos(rad),
                          cy + (r - width / 2) * math.sin(rad),
                          width / 2, c))
    return "".join(out)


def chip(x, y, w, h, bg, label, size, fg, radius=12, border=None,
         border_w=1, bold=True):
    fit(label, size, w - 16, "chip:%s" % label)
    return (box(x, y, w, h, bg, radius=radius, border=border, border_w=border_w)
            + text(x + 8, y + (h - size * 1.25) / 2, w - 16, size * 1.3, label,
                   size, fg, bold=bold, align="CENTER"))


def line_h(x1, y, x2, color=LINE, w=1):
    return box(x1, y, x2 - x1, w, color)


def line_v(x, y1, y2, color=LINE, w=1):
    return box(x, y1, w, y2 - y1, color)


def dashed_h(x1, y, x2, color=LINE, dash=8, gap=6, w=2):
    out = []
    x = x1
    while x < x2:
        out.append(box(x, y, min(dash, x2 - x), w, color))
        x += dash + gap
    return "".join(out)


# ---------------- brand components ----------------
def rot_matrix(rot):
    import math
    a = math.radians(rot)
    c, s = math.cos(a), math.sin(a)
    f = lambda v: ("%.8f" % v).rstrip("0").rstrip(".") or "0"
    return "(%s,%s,0,0,%s,%s,0,0,0,0,1,0,0,0,0,1)" % (f(c), f(s), f(-s), f(c))


def leaf_mark(cx, cy, r, color=LEAF, stem=True, rot=45):
    """stylized leaf: rotated rounded square (proven B01 Transform pattern)
    + optional stem line."""
    size = 2 * r
    out = ['<Positioned left="%s" top="%s" width="%s" height="%s">'
           '<Transform matrix="%s" alignment="CENTER">'
           '<SizedBox width="%s" height="%s">'
           '<DecoratedBox color="%s" borderRadius="%s"/>'
           '</SizedBox></Transform></Positioned>' % (
               r2(cx - r), r2(cy - r), r2(size), r2(size), rot_matrix(rot),
               r2(size), r2(size), color, r2(r * 0.45))]
    if stem:
        out.append(box(cx - r * 0.06, cy, r * 0.12, r * 1.5, color))
    return "".join(out)


def seal(x, y, d, top, mid, color=CLAY):
    """round official seal with inner ring."""
    return (circle(x + d / 2, y + d / 2, d / 2, "#00000000", border=color,
                   border_w=3)
            + circle(x + d / 2, y + d / 2, d / 2 - 7, "#00000000",
                     border=color, border_w=1)
            + leaf_mark(x + d / 2, y + d / 2 - d * 0.13, d * 0.10, color,
                        stem=False)
            + text(x + 6, y + d * 0.40, d - 12, d * 0.22, mid, d * 0.155,
                   color, bold=True, align="CENTER")
            + text(x + 6, y + d * 0.62, d - 12, d * 0.14, top, d * 0.085,
                   color, align="CENTER"))


def ruler_ticks(x, y, w, n=24, color=SOIL, h=7):
    step = w / float(n)
    out = []
    for i in range(n + 1):
        hh = h if i % 4 == 0 else h * 0.55
        out.append(box(x + i * step, y, max(1.5, step * 0.14), hh, color))
    return "".join(out)


def brand_header(x, y, w, color=INK, mark=LEAF, size=22, latin_size=11):
    """leaf mark + 禾风里社区共耕花园 + latin — small brand lockup."""
    return (leaf_mark(x + 12, y + size * 0.55, size * 0.42, mark)
            + text(x + size * 1.5, y, w - size * 1.6, size * 1.3, NAME_S,
                   size, color, bold=True)
            + text(x + size * 1.5, y + size * 1.18, w - size * 1.6,
                   latin_size * 1.4, LATIN, latin_size, MUTED))


def footnote(x, y, w, s, size=12, color=MUTED, align="LEFT"):
    fit(s, size, w, "foot")
    return text(x, y, w, size * 1.5, s, size, color, align=align)


def section(x, y, w, title, size=24, color=INK, mark=CLAY, rule=True):
    """section header: clay bar + title (+ optional rule under)."""
    out = [box(x, y + size * 0.12, 5, size * 0.95, mark),
           text(x + 14, y, w - 14, size * 1.3, title, size, color, bold=True)]
    if rule:
        out.append(line_h(x, y + size * 1.45, x + w, LINE, 1))
    return "".join(out)


# ---------------- emitter ----------------
def emit(path, body, w, h, bg=PAPER):
    # service grammar: Snapshot takes exactly ONE child; B01-proven nesting
    # is Snapshot > SizedBox > Stack(alignment=TOP_LEFT, clipBehavior=NONE)
    doc = ('<Snapshot type="png" background="%s">\n'
           '<SizedBox width="%d" height="%d">\n'
           '<Stack alignment="TOP_LEFT" clipBehavior="NONE">\n'
           '%s\n'
           '</Stack>\n</SizedBox>\n</Snapshot>\n'
           % (bg, w, h, body))
    with open(path, "w", encoding="utf-8") as f:
        f.write(doc)
    print("written", os.path.basename(path), len(doc), "chars")
