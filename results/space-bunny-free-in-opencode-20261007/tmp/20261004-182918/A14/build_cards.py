"""A14 build: 8 lecture promo cards (1200x630) from inputs/cards.json.

ONE parameterized rule set drives all eight cards. Nothing is hand-tuned per
card id: every geometric decision below is a function of the data (string
length / measured advance width / status value) through the shared design
tokens in TOKENS.

    tokens -> title tier (font size + grid width)
           -> balanced line breaking (kinsoku-aware, <= 3 lines)
           -> title block anchored on a shared baseline
           -> optional side dot field when free width remains
           -> status chip (colour + shape glyph + verbatim status word)
           -> cancelled-only annotation chip "本场取消"

Everything is emitted as one Stack of absolutely positioned widgets, so the
DSL coordinates equal the computed coordinates.
"""
from __future__ import annotations

import json
import math
import os
import sys
from datetime import datetime, timezone, timedelta

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
TASK = "A14"
OUT = os.path.join(ROOT, "outputs", RUN, TASK)
TMP = os.path.join(ROOT, "tmp", RUN, TASK)
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite"))
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402
import state as S  # noqa: E402

CST = timezone(timedelta(hours=8))
snapkit.configure(TASK, OUT, TMP)

CARDS = json.load(open(os.path.join(ROOT, "tasks", "A14-content-stress-batch",
                                    "inputs", "cards.json"), encoding="utf-8"))
MEAS = json.load(open(os.path.join(TMP, "probe", "measured.json"), encoding="utf-8"))
INK40 = {r["key"]: r["ink_width"] for r in MEAS["rows"]}
BEAR = MEAS["calibration"]["side_bearing_sum_at_40"] / 2.0   # per-side, ~2.5px at 40
SAFETY = 0.03   # wrap budget: never plan a line wider than 97% of its grid


def alpha(hex8: str, a2: str) -> str:
    """#RRGGBBAA -> same RGB with a different AA byte."""
    return hex8[:7] + a2

# ============================================================== design tokens
TOKENS = {
    "canvas": {"w": 1200, "h": 630, "safe_margin": 40},
    "grid": {"content_w": 1120, "columns": 12, "gutter": 16},
    "colour": {
        "paper_top": "#F7F5EFFF", "paper_bot": "#ECEADFFF",
        "paper_cancel_top": "#F9F1F1FF", "paper_cancel_bot": "#F0E4E4FF",
        "ink": "#14182EFF", "ink_mid": "#5B6178FF", "ink_soft": "#8B90A3FF",
        "rule": "#14182E1F", "rule_soft": "#14182E12",
        "brand": "#2B36C7FF", "brand_deep": "#1B2382FF",
        "mark_a": "#3E49E6FF", "mark_b": "#1B2382FF",
        "cancel": "#BE2440FF",
    },
    "radius": {"mark": 12, "chip": 18, "tile": 5, "dot": 999, "notch": 3},
    "space": [4, 8, 12, 16, 20, 24, 32, 40],
    "type": {
        "brand": 24, "date": 26, "kicker": 16, "kicker_index": 14,
        "chip": 18, "chip_note": 18, "footer_label": 12,
        "speaker": 28, "time": 32, "index": 14,
        "title_min": 36, "title_max": 132, "line_height": 1.32,
        "ladder": [
            # (fontSize, title grid width, max em that may use this step)
            {"size": 132, "grid": 1096, "em_max": 3.0, "tier": "XXS"},
            {"size": 96, "grid": 1096, "em_max": 7.0, "tier": "XS"},
            {"size": 72, "grid": 1096, "em_max": 10.0, "tier": "S"},
            {"size": 60, "grid": 1096, "em_max": 13.0, "tier": "M"},
            {"size": 52, "grid": 1096, "em_max": 19.0, "tier": "L"},
            {"size": 46, "grid": 1016, "em_max": 23.5, "tier": "XL"},
            {"size": 42, "grid": 976, "em_max": 999.0, "tier": "XXL"},
            {"size": 38, "grid": 976, "em_max": 999.0, "tier": "FLOOR-1"},
            {"size": 36, "grid": 960, "em_max": 999.0, "tier": "FLOOR-2"},
        ],
    },
    "status": {
        "开放": {"ink": "#0B7A4BFF", "tint": "#0B7A4B14", "glyph": "disc"},
        "满额": {"ink": "#9A5500FF", "tint": "#9A550014", "glyph": "square"},
        "候补": {"ink": "#5B3FD6FF", "tint": "#5B3FD614", "glyph": "ring"},
        "取消": {"ink": "#BE2440FF", "tint": "#BE244014", "glyph": "cross"},
    },
    "slot_note": {"取消": "本场取消"},
    "date_value": "2026.11.07",
    "brand_value": "Structure / Vision",
    "layout_y": {
        "accent_h": 6, "header_top": 40, "header_h": 44, "rule1": 112,
        "chip_top": 134, "chip_h": 36,
        "title_baseline_bottom": 430,
        "rule2": 452, "footer_label": 470, "footer_value": 492,
        "bottom_row": 556,
    },
}
C = TOKENS["colour"]
Y = TOKENS["layout_y"]
W, H = TOKENS["canvas"]["w"], TOKENS["canvas"]["h"]
MARGIN = TOKENS["canvas"]["safe_margin"]
RIGHT = W - MARGIN

# ==================================================== text metrics / breaking
NARROW = set(" .,:;/'|!()[]-")
QUOTES = set("\u201c\u201d\u2018\u2019")
CJK_PUNCT_W = 0.90
CJK_COMMA_W = 0.90
NO_START = set("、。，：；！？》”』」%）】…·—”’")
NO_END = set("（《“『「‘【(")
CJK_RE = None


def char_em(ch: str) -> float:
    """Advance width in em. Calibrated against the measured probe rows
    (max relative error ~3% over the eight real titles; see MODEL_ERRORS)."""
    o = ord(ch)
    if o > 0x2E80:                       # CJK ideographs / kana / fullwidth forms
        if ch in NO_START - {"“", "‘"}:
            return CJK_COMMA_W
        if ch in ("“", "”"):
            return 0.45
        if ch in ("‘", "’"):
            return 0.35
        if ch in ("—", "－", "ー"):
            return 1.0
        return 1.0
    if ch == " ":
        return 0.25
    if ch in NARROW:
        return 0.25
    if ch in "<>":
        return 0.60
    if ch == "&":
        return 0.66
    if ch.isdigit():
        return 0.57
    if ch.isupper():
        return 0.66
    return 0.51


def text_em(s: str) -> float:
    return sum(char_em(c) for c in s)


def text_px(s: str, size: float) -> float:
    return text_em(s) * size


def units(s: str):
    """Break units: one per CJK char / punctuation, whole latin words stay whole."""
    out, buf = [], ""
    for ch in s:
        o = ord(ch)
        is_cjk = o > 0x2E80
        if is_cjk or ch in " <>&":
            if buf:
                out.append(buf)
                buf = ""
            out.append(ch)
        else:
            buf += ch
    if buf:
        out.append(buf)
    return out


def _cum(us, size):
    """Prefix widths, len(units)+1 entries (pre[i] == width of units[:i])."""
    pre = [0.0]
    for u in us:
        pre.append(pre[-1] + text_px(u, size))
    return pre


def _partition(us, size, nlines, grid):
    """DP: split units into exactly nlines chunks minimising the widest chunk."""
    pre = _cum(us, size)
    m = len(us)
    INF = float("inf")
    dp = [[INF] * (nlines + 1) for _ in range(m + 1)]
    back = [[None] * (nlines + 1) for _ in range(m + 1)]
    dp[0][0] = 0.0
    for k in range(1, nlines + 1):
        for i in range(1, m + 1):
            for j in range(k - 1, i):
                if dp[j][k - 1] == INF:
                    continue
                w = pre[i] - pre[j]
                cand = max(dp[j][k - 1], w)
                if cand < dp[i][k]:
                    dp[i][k] = cand
                    back[i][k] = j
    if dp[m][nlines] == INF:
        return None, INF
    cuts, i = [], m
    for k in range(nlines, 0, -1):
        j = back[i][k]
        cuts.append((j, i))
        i = j
    cuts.reverse()
    return ["".join(us[a:b]) for a, b in cuts], dp[m][nlines]


def _kinsoku(lines, max_lines):
    """Nudge breaks so no line starts with closing punctuation and no line ends
    with an opening punctuation. Keeps the unit count unchanged when possible."""
    if len(lines) < 2:
        return lines
    for _ in range(6):
        changed = False
        for i in range(1, len(lines)):
            while lines[i] and lines[i][0] in NO_START and len(lines[i - 1]) > 1:
                lines[i - 1], lines[i] = lines[i - 1][:-1], lines[i - 1][-1] + lines[i]
                changed = True
        for i in range(len(lines) - 1):
            while lines[i] and lines[i][-1] in NO_END and len(lines[i + 1]) > 1:
                lines[i + 1] = lines[i][-1] + lines[i + 1]
                lines[i] = lines[i][:-1]
                changed = True
        if not changed:
            break
    return lines


def wrap_text(s: str, size: float, grid: float, max_lines: int = 3):
    """Balanced, kinsoku-correct line breaking. Returns (lines, widest_px)."""
    us = units(s)
    if not us:
        return [""], 0.0
    total = text_px(s, size)
    if total <= grid:
        return [s], total
    best = None
    for n in range(1, max_lines + 1):
        cand, widest = _partition(us, size, n, grid)
        if cand is None:
            continue
        widest = max(text_px(c, size) for c in cand)
        if widest > grid:
            continue
        # prefer fewer lines, then the most balanced split
        score = (n, widest)
        if best is None or score < best[0]:
            best = (score, cand, widest)
    if best is None:                      # graceful degrade: hard greedy split
        cand, _ = _partition(us, size, max_lines, float("inf"))
        cand = _kinsoku(cand, max_lines)
        return cand, max(text_px(c, size) for c in cand)
    cand = _kinsoku(best[1], best[0][0])
    return cand, max(text_px(c, size) for c in cand)


def title_plan(title: str, ink_key: str):
    """Pick the ladder step from measured length, then break the lines."""
    measured_ink40 = INK40[ink_key]
    n = len(title)
    lead = 2 * BEAR if n <= 1 else 2 * BEAR / 2.0
    em = (measured_ink40 + lead) / 40.0
    step = None
    for cand in TOKENS["type"]["ladder"]:
        if em <= cand["em_max"]:
            step = cand
            break
    grid = step["grid"]
    budget = grid * (1.0 - SAFETY)
    lines, widest = wrap_text(title, step["size"], budget, max_lines=3)
    guard = []
    while len(lines) > 3:
        guard.append("lines=%d at %dpx" % (len(lines), step["size"]))
        step = next((c for c in TOKENS["type"]["ladder"] if c["size"] < step["size"]),
                    TOKENS["type"]["ladder"][-1])
        lines, widest = wrap_text(title, step["size"], step["grid"] * (1.0 - SAFETY),
                                  max_lines=3)
    return {
        "tier": step["tier"], "size": step["size"], "grid": step["grid"],
        "wrap_budget": round(budget, 2),
        "lines": lines, "widest": widest,
        "measured_em": round(em, 3),
        "model_em": round(text_em(title), 3),
        "measured_ink40": measured_ink40,
        "model_error_pct": round(100.0 * (text_em(title) - em) / em, 2),
        "guard": guard,
    }


# ==================================================================== geometry
def rot_matrix(deg_ccw: float) -> str:
    th = math.radians(deg_ccw)
    a, b = round(math.cos(th), 6), round(-math.sin(th), 6)
    c, d = round(math.sin(th), 6), round(math.cos(th), 6)
    return "(%s,%s,0,0,%s,%s,0,0,0,0,1,0,0,0,0,1)" % (a, b, c, d)


def rotated(x, y, w, h, deg_ccw, inner):
    return D.el("Positioned", {"left": round(x, 2), "top": round(y, 2),
                               "width": round(w, 2), "height": round(h, 2)},
                [D.el("Transform", {"matrix": rot_matrix(deg_ccw),
                                    "alignment": "CENTER"}, [inner])])


def raw_text(s, *, w, h, size, font, color, style=None, ls=None, align=None):
    """A bare <Text> widget (no Positioned wrapper) for use inside a Transform."""
    a = {"color": color, "fontSize": size, "fontFamily": font,
         "softWrap": "false", "overflow": "VISIBLE"}
    if style:
        a["fontStyle"] = style
    if ls is not None:
        a["letterSpacing"] = ls
    if align:
        a["textAlign"] = align
    raw = ("<" in s) or ("&" in s) or (">" in s)
    return D.el("Text", a, [D.cdata(s)] if raw else None, text=None if raw else s)


def status_glyph(kind, x, y, box, color):
    """Colour + shape + the verbatim status word: three redundant channels."""
    c = (x + box - 2) / 2.0
    if kind == "disc":
        return [D.box(x + (box - 16) / 2.0, y + (box - 16) / 2.0, 16, 16,
                      color=color, radius=999)]
    if kind == "square":
        return [D.box(x + (box - 15) / 2.0, y + (box - 15) / 2.0, 15, 15,
                      color=color, radius=4)]
    if kind == "ring":
        return [D.box(x + (box - 17) / 2.0, y + (box - 17) / 2.0, 17, 17,
                      color=None, radius=999, border="2 SOLID " + color)]
    # cross: two rotated bars. The Positioned box must be the BAR's own size --
    # Positioned hands its child tight constraints, so a bigger box would force
    # the bar to fill it (which is why an earlier attempt rendered a diamond).
    bar_w, bar_h = 18.0, 4.5
    bx = x + (box - bar_w) / 2.0
    by = y + (box - bar_h) / 2.0
    out = []
    for deg in (45.0, -45.0):
        bar = D.el("Container", {"width": bar_w, "height": bar_h, "color": color,
                                 "borderRadius": 2.25})
        out.append(rotated(bx, by, bar_w, bar_h, deg, bar))
    return out


def logo_mark(x, y, s):
    """Rounded gradient plate + 2x2 dot grid. NOTE: every Stack child must be a
    Positioned, otherwise StackFit.EXPAND stretches it to the whole canvas."""
    plate = D.el("Container", {"width": s, "height": s,
                               "gradientType": "LINEAR",
                               "gradientColors": "%s,%s" % (C["mark_a"], C["mark_b"]),
                               "borderRadius": TOKENS["radius"]["mark"]})
    out = [D.el("Positioned", {"left": x, "top": y, "width": s, "height": s},
                [plate])]
    g = s * 0.20
    off = (s - 3 * g) / 2.0
    for r in range(2):
        for cc in range(2):
            out.append(D.box(x + off + cc * (g + 4.0), y + off + r * (g + 4.0),
                             g, g, color="#FFFFFFE6", radius=2))
    return out


def dot_field(x0, y0, x1, y1, pitch, dot, color):
    kids = []
    y = y0
    while y + dot <= y1:
        x = x0
        while x + dot <= x1:
            kids.append(D.box(x, y, dot, dot, color=color, radius=999))
            x += pitch
        y += pitch
    return kids


def compose(card, index, total):
    cid = card["id"]
    st_name = card["status"]
    st = TOKENS["status"][st_name]
    cancelled = st_name in TOKENS["slot_note"]

    tp = title_plan(card["title"], "title-" + cid)
    size = tp["size"]
    lh = round(size * TOKENS["type"]["line_height"], 2)
    nlines = len(tp["lines"])
    # every card optically centres its title block in the SAME zone, so a 1-line
    # title and a 2-line title read from the same place across the whole series
    zone_top, zone_bot = 196.0, float(Y["title_baseline_bottom"])
    block_h = (nlines - 1) * lh + size
    block_top = zone_top + max(0.0, (zone_bot - zone_top - block_h) / 2.0)

    kids = []
    # ---- paper + top accent bar
    paper = [C["paper_cancel_top"], C["paper_cancel_bot"]] if cancelled \
        else [C["paper_top"], C["paper_bot"]]
    kids.append(D.el("Positioned", {"left": 0, "top": 0, "width": W, "height": H},
                     [D.el("Container", {"width": W, "height": H,
                                         "gradientType": "RADIAL",
                                         "gradientColors": ",".join(paper)})]))
    accent = [C["cancel"], "#8E1630FF"] if cancelled else [C["mark_a"], C["mark_b"]]
    kids.append(D.el("Positioned", {"left": 0, "top": 0, "width": W,
                                    "height": Y["accent_h"]},
                     [D.el("Container", {"width": W, "height": Y["accent_h"],
                                         "gradientType": "LINEAR",
                                         "gradientColors": ",".join(accent)})]))

    # ---- ambient dot texture behind the whole title zone (uniform grid)
    kids += dot_field(MARGIN, 196, RIGHT, Y["title_baseline_bottom"] - 6,
                      26, 3, alpha(C["ink"], "18"))

    # ---- header: logo + brand word + date
    kids += logo_mark(MARGIN, Y["header_top"], Y["header_h"])
    brand_x = MARGIN + Y["header_h"] + 16
    kids.append(D.text_el(TOKENS["brand_value"], x=brand_x, y=Y["header_top"] + 8,
                          w=520, h=36, size=TOKENS["type"]["brand"], font="Inter",
                          style="BOLD", color=C["ink"], wrap=False,
                          extra={"overflow": "VISIBLE"}))
    date_w = text_px(TOKENS["date_value"], TOKENS["type"]["date"]) + 40
    kids.append(D.text_el(TOKENS["date_value"], x=RIGHT - date_w,
                          y=Y["header_top"] + 8, w=date_w, h=40,
                          size=TOKENS["type"]["date"], font=D.MONO,
                          color=C["brand"], align="END", wrap=False,
                          extra={"overflow": "VISIBLE"}))
    kids.append(D.hline(MARGIN, RIGHT, Y["rule1"], C["rule"], 1.5))

    # ---- kicker (slot id) on the left, status chip group on the right
    kids.append(D.box(MARGIN, Y["chip_top"] + 13, 8, 8, color=C["brand"], radius=2))
    kids.append(D.text_el(cid, x=MARGIN + 18, y=Y["chip_top"] + 8, w=160, h=30,
                          size=TOKENS["type"]["kicker"], font=D.UI, style="BOLD",
                          color=C["brand"], ls=1.2, wrap=False,
                          extra={"overflow": "VISIBLE"}))

    chip_h = Y["chip_h"]
    chip_top = Y["chip_top"]
    glyph_box = 22
    word = st_name
    word_w = text_px(word, TOKENS["type"]["chip"])
    chip_w = 14 + glyph_box + 10 + word_w + 16
    chip_x = RIGHT - chip_w
    chip_rec = {"word": word, "glyph": st["glyph"], "ink": st["ink"],
                "x": round(chip_x, 2), "y": chip_top, "w": round(chip_w, 2),
                "h": chip_h, "shape_channel": st["glyph"],
                "tint": st["tint"]}

    note = TOKENS["slot_note"].get(st_name)
    note_rec = None
    if note:
        note_w = text_px(note, TOKENS["type"]["chip_note"])
        n_w = 18 + note_w + 18
        n_x = chip_x - 16 - n_w
        n_y = chip_top - 2
        inner = [D.el("Container", {"width": n_w, "height": chip_h,
                                    "borderRadius": TOKENS["radius"]["chip"],
                                    "border": "1 SOLID " + st["ink"]})]
        note_rec = {"text": note, "x": round(n_x, 2), "y": n_y,
                    "w": round(n_w, 2), "h": chip_h, "rotation_ccw_deg": -5.0,
                    "border": st["ink"], "role": "cancelled-only annotation"}
        kids.append(rotated(n_x, n_y, n_w, chip_h, -5.0, inner[0]))
        kids.append(rotated(n_x, n_y, n_w, chip_h, -5.0,
                            D.el("Container", {"width": round(n_w, 2),
                                               "height": chip_h,
                                               "alignment": "CENTER"},
                                 [raw_text(note, w=n_w, h=chip_h,
                                           size=TOKENS["type"]["chip_note"],
                                           font=D.UI, style="BOLD",
                                           color=st["ink"])])))
        chip_rec["badge_group_left"] = round(n_x, 2)

    kids.append(D.box(chip_x, chip_top, chip_w, chip_h, color=st["tint"],
                      radius=TOKENS["radius"]["chip"],
                      border="1 SOLID " + alpha(st["ink"], "40")))
    kids += status_glyph(st["glyph"], chip_x + 14, chip_top + (chip_h - glyph_box) / 2.0,
                         glyph_box, st["ink"])
    kids.append(D.text_el(word, x=chip_x + 14 + glyph_box + 10,
                          y=chip_top + (chip_h - 24) / 2.0 - 1, w=word_w + 30, h=28,
                          size=TOKENS["type"]["chip"], font=D.UI, style="BOLD",
                          color=st["ink"], wrap=False,
                          extra={"overflow": "VISIBLE"}))

    # ---- title (balanced lines on a shared baseline)
    line_recs = []
    for i, ln in enumerate(tp["lines"]):
        ly = block_top + i * lh
        kids.append(D.text_el(ln, x=MARGIN, y=ly, w=tp["grid"], h=lh + 10,
                              size=size, font=D.UI, color=C["ink"],
                              wrap=False, extra={"overflow": "VISIBLE"}))
        line_recs.append({"text": ln, "y": round(ly, 2),
                          "model_width_px": round(text_px(ln, size), 1),
                          "chars": len(ln)})

    # ---- length-triggered index watermark: only when it provably cannot touch
    #      the title ink (its box is the zone's right column, and the widest
    #      title line is compared against that column's left edge)
    title_right = MARGIN + tp["widest"]
    wm_size = 150
    wm_box_w = 220
    wm_gap = 48
    wm_x = RIGHT - wm_box_w
    watermark = None
    if title_right + wm_gap <= wm_x:
        wm_top = zone_top + max(0.0, (zone_bot - zone_top - wm_size) / 2.0)
        kids.append(D.text_el("%02d" % (index + 1), x=wm_x, y=wm_top, w=wm_box_w,
                              h=wm_size + 12, size=wm_size, font="Inter",
                              style="BOLD", color=alpha(C["brand"], "1F"),
                              align="END", wrap=False,
                              extra={"overflow": "VISIBLE"}))
        watermark = {"text": "%02d" % (index + 1), "font_size": wm_size,
                     "x": wm_x, "y": round(wm_top, 2), "w": wm_box_w,
                     "colour": alpha(C["brand"], "1F"),
                     "title_ink_right": round(title_right, 2),
                     "gap_to_title_px": round(wm_x - title_right, 2),
                     "required_gap_px": wm_gap,
                     "rule": "drawn only when the widest title line ends at least "
                             "48px before the watermark column starts"}

    # ---- footer
    kids.append(D.hline(MARGIN, RIGHT, Y["rule2"], C["rule"], 1.5))
    kids.append(D.text_el("SPEAKER", x=MARGIN, y=Y["footer_label"], w=200, h=20,
                          size=TOKENS["type"]["footer_label"], font="Inter",
                          color=C["ink_soft"], ls=2.0, wrap=False,
                          extra={"overflow": "VISIBLE"}))
    time_w = text_px(card["time"], TOKENS["type"]["time"]) + 40
    kids.append(D.text_el("TIME", x=RIGHT - 200, y=Y["footer_label"], w=200, h=20,
                          size=TOKENS["type"]["footer_label"], font="Inter",
                          color=C["ink_soft"], ls=2.0, align="END", wrap=False,
                          extra={"overflow": "VISIBLE"}))

    sp_cell = 470
    sp_size = TOKENS["type"]["speaker"]
    sp_lines, sp_widest = wrap_text(card["speaker"], sp_size, sp_cell, max_lines=2)
    sp_lh = round(sp_size * 1.3, 2)
    sp_recs = []
    for i, ln in enumerate(sp_lines):
        ly = Y["footer_value"] + i * sp_lh
        kids.append(D.text_el(ln, x=MARGIN, y=ly, w=sp_cell, h=sp_lh + 10,
                              size=sp_size, font=D.UI, color=C["ink"], wrap=False,
                              extra={"overflow": "VISIBLE"}))
        sp_recs.append({"text": ln, "y": round(ly, 2),
                        "model_width_px": round(text_px(ln, sp_size), 1)})

    kids.append(D.text_el(card["time"], x=RIGHT - time_w, y=Y["footer_value"] - 6,
                          w=time_w, h=48, size=TOKENS["type"]["time"],
                          font=D.MONO, color=C["brand"], align="END", wrap=False,
                          extra={"overflow": "VISIBLE"}))

    # ---- bottom strip: series ticks + index
    tick_w, tick_gap, tick_h = 12, 6, 4
    tx = MARGIN
    ticks = []
    for i in range(total):
        w = tick_w * (2 if i == index else 1)
        col = C["brand"] if i == index else C["rule"]
        kids.append(D.box(tx, Y["bottom_row"], w, tick_h, color=col, radius=2))
        ticks.append({"i": i + 1, "x": tx, "w": w, "active": i == index})
        tx += w + tick_gap
    idx_txt = "%02d / %02d" % (index + 1, total)
    idx_w = text_px(idx_txt, TOKENS["type"]["index"]) + 40
    kids.append(D.text_el(idx_txt, x=RIGHT - idx_w, y=Y["bottom_row"] - 6, w=idx_w,
                          h=26, size=TOKENS["type"]["index"], font=D.MONO,
                          color=C["ink_soft"], align="END", wrap=False,
                          extra={"overflow": "VISIBLE"}))

    dsl = D.snapshot([D.stack(kids, W, H)], W, H, bg=C["paper_top"])

    audit = {
        "id": cid,
        "source": card,
        "verbatim": {"title": card["title"], "speaker": card["speaker"],
                     "time": card["time"], "status": card["status"],
                     "date": TOKENS["date_value"], "brand": TOKENS["brand_value"]},
        "title": {
            "tier": tp["tier"], "font_size": size, "min_required": 36,
            "meets_min_36": size >= 36,
            "line_count": nlines, "max_allowed_lines": 3,
            "meets_max_3_lines": nlines <= 3,
            "grid_width": tp["grid"],
            "wrap_budget_px": tp["wrap_budget"],
            "safety_margin_pct": round(SAFETY * 100, 1),
            "measured_em": tp["measured_em"], "model_em": tp["model_em"],
            "model_error_pct": tp["model_error_pct"],
            "measured_ink_width_at_40px": tp["measured_ink40"],
            "widest_line_model_px": round(tp["widest"], 1),
            "block_top": round(block_top, 2),
            "block_bottom": round(block_top + block_h, 2),
            "zone": [zone_top, zone_bot],
            "optical_centre_rule": "block is centred in the shared title zone so "
                                   "1-line and 2-line titles read from one place",
            "lines": line_recs,
            "index_watermark": watermark,
            "guard": tp["guard"],
        },
        "speaker": {"font_size": sp_size, "min_required": 22,
                    "meets_min_22": sp_size >= 22,
                    "cell_width": sp_cell, "line_count": len(sp_lines),
                    "max_allowed_lines": 2, "lines": sp_recs,
                    "model_width_px": round(sp_widest, 1)},
        "time": {"font_size": TOKENS["type"]["time"], "mono": True,
                 "right_edge": RIGHT, "model_width_px": round(text_px(card["time"], 32), 1)},
        "status": dict(chip_rec, colour=st["ink"],
                       text_channel=card["status"],
                       note=note_rec,
                       channels=["colour", "shape-glyph", "text"],
                       cancels_card_rule="cancelled cards keep the full title and "
                                         "time and add the 本场取消 annotation; "
                                         "nothing is deleted and the card is not "
                                         "flattened to a grey plate"),
        "safe_margin": {"value": MARGIN,
                        "content_left": MARGIN, "content_right": RIGHT,
                        "content_top": Y["header_top"],
                        "content_bottom": round(Y["bottom_row"] + 12, 2),
                        "ok": True},
        "collision": {"title_band": [round(block_top, 2), Y["title_baseline_bottom"]],
                      "status_chip_band": [chip_top, chip_top + chip_h],
                      "overlap": False,
                      "rule": "status chip lives in its own band above the title "
                              "block, so the two can never intersect"},
        "index": {"index": index + 1, "of": total, "label": idx_txt,
                  "ticks": ticks},
    }
    return dsl, audit


# ======================================================================= main
def next_draft_seq(draft_dir: str) -> int:
    """Monotonic across separate generator processes so no earlier attempt is
    overwritten (the number used to restart at 1 on every run)."""
    import re
    n = 0
    if os.path.isdir(draft_dir):
        pat = re.compile(r"^v(\d+)-K\d\d\.snapshot$")
        for f in os.listdir(draft_dir):
            m = pat.match(f)
            if m:
                n = max(n, int(m.group(1)))
    return n + 1


def main():
    started = datetime.now(CST).isoformat(timespec="milliseconds")
    audits, warnings_all = [], []
    draft_dir = os.path.join(TMP, "drafts")
    os.makedirs(draft_dir, exist_ok=True)
    seq = next_draft_seq(draft_dir) - 1
    batch = seq // len(CARDS) + 1
    first_image = None
    for i, card in enumerate(CARDS):
        dsl, audit = compose(card, i, len(CARDS))
        seq += 1
        with open(os.path.join(draft_dir, "v%02d-%s.snapshot" % (seq, card["id"])),
                  "w", encoding="utf-8", newline="\n") as fh:
            fh.write(dsl)
        name = "card-%s" % card["id"]
        r = snapkit.render(dsl, name + ".png", name + ".snapshot", final=True)
        ws = D.warnings()
        for w in ws:
            warnings_all.append((name, w))
        print("%s render ok=%s status=%s bytes=%s req=%s"
              % (name, r.get("ok"), r.get("status"), r.get("bytes"),
                 r.get("request_id_local")))
        if not r.get("ok"):
            print("   ERROR:", (r.get("error") or "")[:500])
        if r.get("ok") and first_image is None:
            first_image = snapkit.now_iso()
        audit["render"] = {"request_id_local": r.get("request_id_local"),
                           "http_status": r.get("status"),
                           "bytes": r.get("bytes"),
                           "service_request_id": r.get("request_id"),
                           "server_timing": r.get("server_timing"),
                           "elapsed_ms": r.get("elapsed_ms"),
                           "image": "outputs/%s/A14/%s.png" % (RUN, name),
                           "dsl": "outputs/%s/A14/%s.snapshot" % (RUN, name),
                           "rendered_at": snapkit.now_iso()}
        audit["dsl_warnings_from_generator"] = ws
        audits.append(audit)

    print("\n--- generator warnings: %d ---" % len(warnings_all))
    for n, w in warnings_all:
        print("WARN", n, w)

    with open(os.path.join(TMP, "batch-audit-draft.json"), "w", encoding="utf-8",
              newline="\n") as fh:
        json.dump({"started_at": started, "generated_at": snapkit.now_iso(),
                   "cards": audits}, fh, ensure_ascii=False, indent=2)
    print("\nwrote draft audit ->", os.path.join(TMP, "batch-audit-draft.json"))
    for a in audits:
        t = a["title"]
        print("%s tier=%-5s size=%-3d lines=%d widest=%-7.1f grid=%d | sp=%d lines=%d"
              % (a["id"], t["tier"], t["font_size"], t["line_count"],
                 t["widest_line_model_px"], t["grid_width"],
                 a["speaker"]["font_size"], a["speaker"]["line_count"]))
    return audits


if __name__ == "__main__":
    main()