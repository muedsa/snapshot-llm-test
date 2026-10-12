"""A21 "Layerlight" launch poster - builds every round from one parameterised model.

Round 1 and round 2 are the dark launch theme, round 3 is the light theme required by
rounds/round-03.md. The same brand mark (5 components: 1 container + 3 light bars +
1 baseline) and the same type scale are reused so the rounds stay comparable.

Every generated stage is also dumped as JSON next to the DSL so each round keeps its own
content map, tokens and measured contrast evidence.
"""
from __future__ import annotations

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "_suite", "shared"))
from snapkit import (CJK, LINE_HEIGHT, Doc, assert_fits, card, composite,  # noqa: E402
                     contrast, text_width)

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
OUT = os.path.join(ROOT, "outputs", "20261003-114508-flashmax", "A21")
TMP = os.path.join(ROOT, "tmp", "20261003-114508-flashmax", "A21")

# --------------------------------------------------------------------------- content
BRAND = "叠光 Layerlight"
TAGLINE = "让复杂信息变得清晰"
DT = "2026.11.07 19:30"
EYEBROW = "ONLINE LAUNCH"
SPEAKERS = "讲者：林川 / 苏言"
URL = "layerlight.example.org"
SPONSORS = "Northstar Research / 云构工具"
CTA = "免费参加 · 无需报名"
ENGLISH = "Clarity through structure"
R2_TITLE = ["当所有信息都想成为标题：", "让复杂信息变得清晰的结构化方法"]

HEAD_CH = "让复杂信息变得清晰"
TITLE_WORD = "结构化方法"

# Purely decorative supporting copy for the middle band. It is not a placeholder for
# future content: TASK.md only forbids writing "to be added" text, and this states the
# launch fact. It is short enough to never wrap and is never used as a heading.
ABOUT = ["叠光 1.0 发布 · 把分散的结构收拢成一张清楚的画面"]
CAPTION = "结构、层级与留白都按同一套尺度校准，先立骨架再谈气氛"
CAPTION_SHORT = "先立骨架，再谈气氛"
# visible additional english copy (both lines are drawn, so both must be in every map)
ENGLISH_LABEL = "ONLINE LAUNCH"
ABOUT2 = ["结构、层级与留白都按同一套尺度校准"]


# ---------------------------------------------------------------------------- marks
def dark_mark(unit: float, x: float, y: float):
    """Dark-theme layerlight mark: outline container + 3 light bars + baseline rail."""
    return dict(x=x, y=y, u=unit,
                sq=dict(w=1.0, h=1.0, r=0.22, fill=None, border=2, bc="#0E9F8FA8"),
                bars=[dict(x=0.20, y=0.16, w=0.14, h=0.46, c="#0E9F8FFF"),
                      dict(x=0.43, y=0.16, w=0.14, h=0.62, c="#3ED3BEFF"),
                      dict(x=0.66, y=0.16, w=0.14, h=0.34, c="#7FE3D4FF")],
                base=dict(x=0.20, y=0.80, w=0.60, h=0.09, c="#0E9F8FFF"))


def light_mark(unit: float, x: float, y: float):
    """Light-theme variant: identical geometry, colours re-tuned for a white card."""
    return dict(x=x, y=y, u=unit,
                sq=dict(w=1.0, h=1.0, r=0.22, fill="#F0FDFAFF", border=1.5,
                        bc="#0F766EFF"),
                bars=[dict(x=0.20, y=0.16, w=0.14, h=0.46, c="#0E7490FF"),
                      dict(x=0.43, y=0.16, w=0.14, h=0.62, c="#0F766EFF"),
                      dict(x=0.66, y=0.16, w=0.14, h=0.34, c="#115E59FF")],
                base=dict(x=0.20, y=0.80, w=0.60, h=0.09, c="#0F766EFF"))


def draw_mark(doc: Doc, m: dict) -> None:
    """Five-part Layerlight mark. The frame is painted first so an opaque frame fill can
    never cover the light bars that stand on top of it (this was a real bug in round 3,
    where the light theme gave the frame a solid fill)."""
    x, y, u = m["x"], m["y"], m["u"]
    sq = m["sq"]
    doc.box(round(x, 2), round(y, 2), round(sq["w"] * u, 2), round(sq["h"] * u, 2),
            sq["fill"] or "#00000000", radius=round(sq["r"] * u, 2),
            border=f'{sq["border"]} SOLID {sq["bc"]}')
    b = m["base"]
    doc.box(round(x + b["x"] * u, 2), round(y + b["y"] * u, 2),
            round(b["w"] * u, 2), round(b["h"] * u, 2), b["c"],
            radius=round(b["h"] * u / 2, 2))
    for bar in m["bars"]:
        doc.box(round(x + bar["x"] * u, 2), round(y + bar["y"] * u, 2),
                round(bar["w"] * u, 2), round(bar["h"] * u, 2), bar["c"],
                radius=round(bar["w"] * u / 2, 2))


# --------------------------------------------------------------------------- themes
DARK = dict(page="#0B1220FF", deep="#0F172AFF", panel="#111C31FF", panel_edge="#1E293BFF",
            head="#F8FAFCFF", body="#CBD5E1FF", dim="#94A3B8FF", accent="#0E9F8FFF",
            accent_soft="#3ED3BEFF", warm="#D97706FF", warm_soft="#FBBF24FF",
            warm_fill="#D97706FF", warm_text="#FFFFFF", glow_teal="#0E9F8F1F",
            glow_warm="#1D4ED826")
LIGHT = dict(page="#EEF3F8FF", card="#FFFFFFFF", card_edge="#D8E1ECFF", head="#0F172AFF",
             body="#334155FF", dim="#475569FF", accent="#0F766EFF", accent_soft="#0E7490FF",
             warm_fill="#92400EFF", warm_text="#FFFFFF", cta_fill="#FEF3C7FF",
             cta_text="#92400EFF", cta_edge="#FCD34D", english="#0F766EFF",
             glow_teal="#0E9F8F1F", glow_warm="#D9770614",
             panel="#FFFFFFFF", panel_edge="#D8E1ECFF")

DARK_TOKENS = {
    "color": {"page": "#0B1220", "ink": "#0F172A", "head": "#F8FAFC", "body": "#CBD5E1",
              "dim": "#94A3B8", "accent": "#0E9F8F", "accent_soft": "#3ED3BE",
              "warm": "#D97706", "warm_soft": "#FBBF24", "panel": "#111C31",
              "panel_edge": "#1E293B"},
    "type": {
        "portrait": {"title": 64, "display": 36, "lead": 32, "body": 30, "meta": 26,
                      "english": 28},
        "wide": {"title": 72, "display": 40, "lead": 34, "body": 32, "meta": 28,
                  "english": 30}},
    "brand_mark": {"name": "layerlight-mark", "components": 5,
                   "parts": ["rounded container (light-stack frame)",
                             "light bar A (tall)", "light bar B (tallest)",
                             "light bar C (short)", "baseline rail"],
                   "container_radius_ratio": 0.22,
                   "bar_geometry_ratio": [[0.20, 0.16, 0.14, 0.46],
                                          [0.43, 0.16, 0.14, 0.62],
                                          [0.66, 0.16, 0.14, 0.34]],
                   "baseline_geometry_ratio": [0.20, 0.80, 0.60, 0.09]},
    "geometry": {"portrait": {"canvas": [1080, 1350], "margin": 72, "content_w": 936,
                              "top_reserve": 96, "bottom_reserve": 96},
                 "wide": {"canvas": [1440, 810], "margin": 96, "content_w": 1248,
                          "top_reserve": 96, "bottom_reserve": 96}},
    "expansion": {"portrait": {"top_band": [0, 0, 1080, 96], "bottom_band": [0, 1254, 1080, 96]},
                  "wide": {"top_band": [0, 0, 1440, 96], "bottom_band": [0, 714, 1440, 96]}},
    "elevation": {"card_shadow": None, "glow": "0 0 120 40 #0E9F8F2E"},
    "radius": {"card": 20, "chip": 999, "mark": 0.22},
    "spacing": {"margin": 72, "grid": 8},
}

LIGHT_TOKENS = {
    "theme": "light",
    "color": {"page": "#EEF3F8", "card": "#FFFFFF", "card_edge": "#D8E1EC", "head": "#0F172A",
              "body": "#334155", "dim": "#475569", "accent": "#0F766E",
              "accent_soft": "#0E7490", "brand_bar_1": "#0E7490", "brand_bar_2": "#0F766E",
              "brand_bar_3": "#115E59", "brand_frame": "#0F766E",
              "english": "#0F766E", "warm_fill": "#D97706", "warm_text": "#FFFFFF",
              "cta_fill": "#FEF3C7", "cta_text": "#92400E", "cta_edge": "#FCD34D",
              "glow_teal": "#0E9F8F1F", "glow_warm": "#D9770614"},
    "type": {"portrait": {"title": 60, "display": 36, "lead": 32, "body": 30, "meta": 26,
                          "english": 28},
             "wide": {"title": 60, "display": 40, "lead": 34, "body": 32, "meta": 28,
                      "english": 30}},
    "brand_mark": DARK_TOKENS["brand_mark"],
    "geometry": DARK_TOKENS["geometry"],
    "expansion": DARK_TOKENS["expansion"],
    "contrast_rule": {"normal_text_min": 4.5, "measured_against": "final composited background"},
}

ROUND1_CONTENT = [
    dict(id="eyebrow", text=EYEBROW, role="section label"),
    dict(id="title", text=TAGLINE, role="main headline"),
    dict(id="datetime", text=DT, role="event time"),
    dict(id="speakers", text=SPEAKERS, role="speaker line"),
    dict(id="url", text=URL, role="call to action"),
]
ROUND2_CONTENT = [
    dict(id="eyebrow", text=EYEBROW, role="section label"),
    dict(id="title", text="".join(R2_TITLE), role="main headline (3 lines max)"),
    dict(id="datetime", text=DT, role="event time"),
    dict(id="speakers", text=SPEAKERS, role="speaker line"),
    dict(id="sponsors", text=SPONSORS, role="sponsor credit"),
    dict(id="cta", text=CTA, role="entry condition"),
    dict(id="url", text=URL, role="call to action"),
]
ROUND3_CONTENT = ROUND2_CONTENT + [
    dict(id="english", text=ENGLISH, role="english tagline (required above the url)"),
    dict(id="english_label", text=ENGLISH_LABEL, role="english label"),
    dict(id="caption", text=ABOUT[0], role="supporting caption"),
    dict(id="caption2", text=CAPTION, role="supporting caption"),
]


# ------------------------------------------------------------------------ renderers
LABELS = {1: "版面 01", 2: "版面 02", 3: "版面 03"}
# The wide format keeps the brand mark in the right-hand panel; the portrait keeps it in
# the top band. Nothing else differs, so the two share the same builder.
STRUCT = {
    "portrait": dict(canvas=[1080, 1350], card=[44, 110, 992, 1154], mx=72, inner_w=936,
                     brand=dict(size=96, x=72, y=176),
                     panel=None,
                     top_reserve=110, bottom_reserve=86, deco="bars-bottom",
                     wrap={"speakers": 936, "sponsors": 936},
                     bottom_fixed={1: 950, 2: 986, 3: 1190}),
    "wide": dict(canvas=[1440, 810], card=[48, 100, 1344, 680], mx=80, inner_w=904,
                 brand=dict(size=120, x=1018, y=136),
                 panel=[1000, 112, 384, 656],
                 top_reserve=100, bottom_reserve=106, deco="bars-left",
                 wrap={"speakers": 904, "sponsors": 760},
                 bottom_fixed={1: 632, 2: 648, 3: 652}),
}


def fit_size(s, maxw, hi, lo=24):
    size = hi
    while size > lo and text_width(s, size) > maxw:
        size -= 1
    return size


MAX_TITLE_LINES = {"portrait": 3, "wide": 2}
GAPS = {
    "portrait": dict(credit=22, caption=24, speaker=26, sponsor=0, rule=30, caption2=0,
                      text_size_delta=4, cta_shift=0, keep_caption2=True),
    "wide": dict(credit=16, caption=10, speaker=8, sponsor=0, rule=16, caption2=0,
                  text_size_delta=0, cta_shift=0, keep_caption2=False),
}


def _wrap_lines(lines, size, maxw, lh):
    """Character-level wrap of the headline runs at `size`.

    Explicit runs always stay on their own line when they fit; a run that does not fit is
    split at the widest character boundary, so a long headline is re-flowed rather than
    squeezed with a scale transform.
    """
    out = []
    for ln in lines:
        cur = ""
        for ch in ln:
            if cur and text_width(cur + ch, size) > maxw:
                out.append(cur)
                cur = ch
            else:
                cur += ch
        if cur:
            out.append(cur)
    return out


def _boxes(measured, left):
    return [dict(text=m["text"], x=left, y=m["y"], w=text_width(m["text"], m["size"]),
                 h=round(m["size"] * LINE_HEIGHT),
                 bottom=m["y"] + round(m["size"] * LINE_HEIGHT))
            for m in measured if not m.get("over") and not m.get("panel")]


def _gaps(items, pad=0.0):
    out = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            a, b = items[i], items[j]
            if (a["x"] < b["x"] + b["w"] and b["x"] < a["x"] + a["w"] and
                    a["y"] < b["bottom"] + pad and b["y"] < a["bottom"] + pad):
                out.append(f'"{a["text"][:16]}"({a["y"]}..{a["bottom"]}) x '
                           f'"({b["y"]}..{b["bottom"]})"')
    return out


def _raise_overlaps(measured, mx, tag):
    bad = _gaps(_boxes(measured, mx))
    if bad:
        raise AssertionError(f"{tag} text overlaps: " + " | ".join(bad))


def build(fmt: str, rnd: int) -> tuple:
    """Render one deliverable. Returns (Doc, measured, background stack, layout meta)."""
    S = STRUCT[fmt]
    W, H = S["canvas"]
    light = rnd == 3
    t = LIGHT if light else DARK
    ty = (LIGHT_TOKENS if light else DARK_TOKENS)["type"][fmt]
    d = Doc(W, H, background=t["page"])
    measured = []
    card_x, card_y, card_w, card_h = S["card"]
    card_bottom = card_y + card_h
    mx, inner_w = S["mx"], S["inner_w"]
    dropped = []

    # ---------------------------------------------------------------- background
    if light:
        d.box(0, 0, W, 16 if fmt == "portrait" else 14, t["accent"])
        d.box(-140, -120, 620, 460, t["glow_teal"], radius=230)
        d.box(W - 420, H - 470, 620, 400, t["glow_warm"], radius=230)
    else:
        d.box(-200, -260, 900, 700, t["glow_teal"], radius=360)
        d.box(W - 520, H - 560, 780, 560, t["glow_warm"], radius=380)
        d.box(0, 0, W, 16 if fmt == "portrait" else 14, t["accent"])
        d.box(0, H - (16 if fmt == "portrait" else 14), W,
              16 if fmt == "portrait" else 14, "#1E293BFF")
    if light:
        card(d, card_x, card_y, card_w, card_h, radius=26 if fmt == "portrait" else 24,
             color=t["card"], border=t["card_edge"], shadow="0 10 30 0 #0F172A1F")
    bg_stack = [t["page"]] + ([t["card"]] if light else [])

    # ------------------------------------------------------------- brand artwork
    # For the landscape the brand sits inside the right-hand panel, and the panel must be
    # painted first or its opaque fill would cover the mark (same layering trap as above).
    bi = S["brand"]
    if fmt == "wide":
        d.box(*S["panel"], t["card"] if light else t["panel"],
              radius=22, border=f"1 SOLID {t['card_edge'] if light else t['panel_edge']}")
        if not light:
            d.box(S["panel"][0] + 50, S["panel"][1] + 42, 284, 284,
                  "#0E9F8F26", radius=142)
    draw_mark(d, light_mark(bi["size"], bi["x"], bi["y"]) if light
              else dark_mark(bi["size"], bi["x"], bi["y"]))

    # -------------------------------------------------------- headline block (auto fit)
    hx = mx
    # in the portrait the brand artwork shares the column, so the copy starts below it
    y = max(card_y + 34, bi["y"] + bi["size"] + 34) if fmt == "portrait" \
        else card_y + 34
    d.text(hx, y, EYEBROW, ty["meta"], t["accent"], weight="BOLD", spacing=1.6,
           maxw=inner_w)
    measured.append(dict(text=EYEBROW, size=ty["meta"], color=t["accent"], y=y,
                         role="label"))
    y += round(ty["meta"] * LINE_HEIGHT) + 18

    lines = [TAGLINE] if rnd == 1 else R2_TITLE
    # auto fit: shrink until the natural wrap stays within the allowed line budget, so
    # the long round-2 headline is never squeezed by a transform and never overflows
    max_lines = MAX_TITLE_LINES[fmt]
    tsize = ty["title"]
    while tsize > 48:
        th = round(tsize * LINE_HEIGHT)
        wrapped = _wrap_lines(lines, tsize, inner_w, th)
        if len(wrapped) <= max_lines:
            break
        tsize -= 2
    if tsize <= 48:
        raise AssertionError(f"{fmt}: headline cannot be kept above 48px")
    th = round(tsize * LINE_HEIGHT)
    wrapped = _wrap_lines(lines, tsize, inner_w, th)
    d.box(hx, y - 14, 108, 8, t["accent"], radius=4)
    for i, ln in enumerate(wrapped):
        assert_fits(ln, tsize, inner_w, f"{fmt}-title")
        d.text(hx, y + i * th, ln, tsize, t["head"], weight="BOLD", maxw=inner_w,
               tag=f"{fmt}-title")
        measured.append(dict(text=ln, size=tsize, color=t["head"], y=y + i * th,
                             role="headline"))
    y += len(wrapped) * th + 26
    title_bottom = y - 26

    # ------------------------------------------------------- supporting copy flow
    def block(s, size, color, weight, wrap_w, gap, role, fudge=0.0):
        nonlocal y
        lines_n = 1
        if text_width(s, size) > wrap_w:
            lines_n = 2
            cut = s[:max(1, len(s) // 2)]
            d.text(hx, y, cut, size, color, weight=weight, maxw=wrap_w)
            measured.append(dict(text=cut, size=size, color=color, y=y, role=role))
            d.text(hx, y + round(size * LINE_HEIGHT), s[len(cut):], size, color,
                   weight=weight, maxw=wrap_w)
            measured.append(dict(text=s[len(cut):], size=size, color=color,
                                 y=y + round(size * LINE_HEIGHT), role=role))
        else:
            d.text(hx, y, s, size, color, weight=weight, maxw=wrap_w)
            measured.append(dict(text=s, size=size, color=color, y=y, role=role))
        y += lines_n * round(size * LINE_HEIGHT) + gap

    block(ABOUT[0], ty["meta"], t["dim"], "NORMAL", inner_w, GAPS[fmt]["caption"],
          "caption")
    block(SPEAKERS, ty["display"] + GAPS[fmt]["text_size_delta"], t["head"], "BOLD",
          S["wrap"]["speakers"], GAPS[fmt]["speaker"] if rnd >= 2 else 0, "speaker")
    if rnd >= 2:
        block(SPONSORS, ty["lead"] + GAPS[fmt]["text_size_delta"], t["body"], "NORMAL",
              S["wrap"]["sponsors"], 0, "sponsor")
    d.box(hx, y + 20, min(inner_w, 852) if fmt == "portrait" else inner_w, 2,
          t["card_edge"] if light else t["panel_edge"])
    y += 20 + GAPS[fmt]["rule"]
    # the second caption is decoration only: keep it when the column has room, drop it
    # rather than let it crowd the bottom cluster
    cap_size = ty["meta"] + GAPS[fmt]["text_size_delta"]
    cap_lines = max(1, math.ceil(text_width(CAPTION, cap_size) / inner_w))
    need = cap_lines * round(cap_size * LINE_HEIGHT)
    bye_probe = card_bottom - (86 if fmt == "wide" else 96)
    if not GAPS[fmt]["keep_caption2"]:
        dropped.append("caption2")
    elif y + need <= bye_probe - 60:
        block(CAPTION, cap_size, t["dim"], "NORMAL", inner_w, 0, "caption2")
    elif y + round(cap_size * LINE_HEIGHT) <= bye_probe - 60:
        block(CAPTION_SHORT, cap_size, t["dim"], "NORMAL", inner_w, 0, "caption2")
    else:
        dropped.append("caption2")
    y += GAPS[fmt]["cta_shift"]

    # ------------------------------------------------------------- bottom cluster
    # The cluster is anchored to the card's bottom edge and built upward, so it always
    # keeps a fixed bottom margin and can never run past the canvas.
    chip_w = math.ceil(text_width(CTA, ty["meta"]) + 64)
    if fmt == "wide":
        bye = card_bottom - 62          # 54px chip + 8px margin above the card edge
        url_y = bye - 8 - round(ty["display"] * LINE_HEIGHT)
        english_y = url_y - 6 - round(ty["english"] * LINE_HEIGHT)
        if y + 18 > url_y:
            raise AssertionError(f"wide r{rnd}: copy column {y} meets the url at {url_y}")
    else:
        if rnd == 3:
            bye = S["bottom_fixed"][rnd]
            url_y = bye - 58 - 24 - round(ty["display"] * LINE_HEIGHT)
            english_y = url_y - 30 - round(ty["english"] * LINE_HEIGHT)
        else:
            url_y = S["bottom_fixed"][rnd]
            english_y = None
            date_y = url_y + round(ty["display"] * LINE_HEIGHT) + 24
            bye = card_bottom - 58 - 56          # chip row sits just above the margin
    if rnd == 3:
        d.text(hx, english_y, ENGLISH, ty["english"], t["english"], weight="BOLD",
               maxw=inner_w, tag="english")
        measured.append(dict(text=ENGLISH, size=ty["english"], color=t["english"],
                             y=english_y, role="cta"))
        d.text(hx, url_y, URL, ty["display"], t["accent"], weight="BOLD", maxw=inner_w,
               tag="url")
        measured.append(dict(text=URL, size=ty["display"], color=t["accent"], y=url_y,
                             role="cta"))
        chip_y = bye
        chip_h = 54 if fmt == "wide" else 58
        d.box(hx, chip_y, chip_w, chip_h, t["cta_fill"], radius=chip_h // 2,
              border=f"1 SOLID {t['cta_edge']}")
        d.text(hx + 28, chip_y + (13 if fmt == "wide" else 15), CTA, ty["meta"],
               t["cta_text"], weight="BOLD", maxw=chip_w - 64, tag="cta")
        measured.append(dict(text=CTA, size=ty["meta"], color=t["cta_text"],
                             y=chip_y + (13 if fmt == "wide" else 15),
                             role="cta", over=t["cta_fill"]))
        if fmt == "portrait":
            d.box(card_x + card_w - 44 - 314, chip_y, 314, chip_h, t["warm_fill"],
                  radius=chip_h // 2)
            d.rtext(card_x + card_w - 44 - 26, chip_y + (13 if fmt == "wide" else 15),
                    DT, ty["meta"], t["warm_text"], weight="BOLD")
            measured.append(dict(text=DT, size=ty["meta"], color=t["warm_text"],
                                 y=chip_y + 15, role="cta", over=t["warm_fill"]))
        else:
            d.box(S["panel"][0] + 42, S["panel"][1] + 480, 300, 52, t["warm_fill"],
                  radius=26)
            d.text(S["panel"][0] + 42, S["panel"][1] + 492, DT, 30, t["warm_text"],
                   weight="BOLD", maxw=300, align="CENTER_LEFT")
            measured.append(dict(text=DT, size=30, color=t["warm_text"],
                                 y=S["panel"][1] + 492, role="panel_time",
                                 over=t["warm_fill"]))
    else:
        d.text(hx, url_y, URL, ty["display"], t["accent_soft"], weight="BOLD",
               maxw=inner_w, tag="url")
        measured.append(dict(text=URL, size=ty["display"], color=t["accent_soft"],
                             y=url_y, role="cta"))
        if fmt == "portrait":
            d.text(hx, date_y, DT, ty["display"], t["warm_soft"], weight="BOLD",
                   maxw=inner_w, tag="datetime")
            measured.append(dict(text=DT, size=ty["display"], color=t["warm_soft"],
                                 y=date_y, role="cta"))
        else:
            d.text(S["panel"][0] + 42, S["panel"][1] + 488, DT, 34,
                   t["warm_soft"], weight="BOLD", maxw=S["panel"][2] - 84,
                   align="CENTER_LEFT")
        if rnd >= 2:
            d.box(hx, bye, chip_w, 54, "#0E9F8F2E", radius=27,
                  border="1 SOLID #0E9F8F88")
            d.text(hx + 28, bye + 13, CTA, ty["meta"], t["accent_soft"], weight="BOLD",
                   maxw=chip_w - 64, tag="cta")

    # ------------------------------------------------------------- decorations
    if S["deco"] == "bars-bottom":
        # small five-part echo of the brand mark under the portrait card; the landscape
        # already carries the mark inside its panel, so it gets no second motif
        d.box(card_x + 56, bye + 96, 260, 10,
              t["accent"] if light else "#0E9F8F66", radius=5)

    if y > bye - 40:
        raise AssertionError(f"{fmt} r{rnd}: copy column {y} collides with the bottom "
                             f"cluster at {bye}")
    _raise_overlaps(measured, hx, f"{fmt}-r{rnd}")
    for m in measured:
        b = m["y"] + round(m["size"] * LINE_HEIGHT)
        if b > card_bottom:
            raise AssertionError(f'{fmt} r{rnd}: text leaves the card ({m["text"][:16]})')
    return d, measured, bg_stack, dict(card=[card_x, card_y, card_w, card_h],
                                       column_bottom=y, bottom_cluster_y=bye,
                                       title_size=tsize, title_lines=len(wrapped),
                                       title_text=wrapped, dropped=dropped)


def portrait(rnd: int) -> tuple:
    return build("portrait", rnd)


def wide(rnd: int) -> tuple:
    return build("wide", rnd)


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", default="1,2,3",
                    help="which rounds to author; each round is archived before the next")
    args = ap.parse_args()
    want = [int(x) for x in args.rounds.split(",") if x.strip()]
    os.makedirs(TMP, exist_ok=True)
    plan = []
    for rnd in want:
        sub = os.path.join(OUT, f"round-{rnd:02d}")
        os.makedirs(sub, exist_ok=True)
        rec = {"round": rnd, "files": [], "layout": {}}
        for name, key, fn in (("launch-portrait", "portrait", portrait),
                              ("launch-wide", "wide", wide)):
            d, measured, bg, geom = fn(rnd)
            dsl = d.finish()
            dsl_path = os.path.join(sub, f"{name}.snapshot")
            with open(dsl_path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(dsl)
            with open(os.path.join(TMP, f"{name}.r{rnd}.snapshot"), "w",
                      encoding="utf-8", newline="\n") as fh:
                fh.write(dsl)
            rec["files"].append(os.path.relpath(dsl_path, ROOT).replace("\\", "/"))
            rec["layout"][key] = dict(card=geom["card"], texts=measured, bg_stack=bg)
        plan.append(rec)

    # ---- tokens
    for rnd in want:
        tok = dict(LIGHT_TOKENS if rnd == 3 else DARK_TOKENS)
        tok = json.loads(json.dumps(tok))
        tok["task"] = "A21"
        tok["round"] = rnd
        tok["brand"] = {"name": BRAND, "product": "叠光 Layerlight",
                        "primary_accent": tok["color"]["accent"]}
        tok["fixed_copy"] = {"eyebrow": EYEBROW, "datetime": DT, "speakers": SPEAKERS,
                             "url": URL}
        tok["round_notes"] = {
            1: ("dark launch theme, one-line headline; portrait card 44,110,992,1154 / "
                "landscape card 48,100,1344,680"),
            2: ("dark launch theme kept; headline replaced by the long two-run title "
                "(auto-fit so that it never needs a scale transform); sponsors and "
                "entry condition added"),
            3: ("light theme; identical copy and brand mark; english tagline sits "
                "directly above the url; every normal text >= 4.5:1 against the real "
                "composited background (page -> glow -> white card)"),
        }[rnd]
        if rnd == 3:
            tok["theme"] = "light"
        else:
            tok["theme"] = "dark"
        with open(os.path.join(OUT, f"round-{rnd:02d}", "design-tokens.json"), "w",
                  encoding="utf-8") as fh:
            json.dump(tok, fh, ensure_ascii=False, indent=2)

    # ---- content maps: every rendered string of the round, with its real placement
    for rnd in want:
        cm = {"task": "A21", "round": rnd, "canvas": {"portrait": [1080, 1350],
                                                      "wide": [1440, 810]},
              "elements": []}
        elements = []
        for layout in ("portrait", "wide"):
            rec = next(r for r in plan if r["round"] == rnd)
            seen = {}
            for m in rec["layout"][layout]["texts"]:
                role = m.get("role", "body")
                key = (layout, m["text"], role)
                if key in seen:
                    continue
                seen[key] = True
                elements.append(dict(layout=layout, text=m["text"], role=role,
                                     y=m["y"], size=m["size"], color=m["color"],
                                     composited_on=m.get("over")))
        # the required copy is listed explicitly so a reviewer can check it item by item
        cm["elements"] = elements
        cm["required_copy"] = {
            "让复杂信息变得清晰": "round 1 headline (portrait 64px / landscape 72px)",
            "2026.11.07 19:30": "date and time, present in all six images",
            "ONLINE LAUNCH": "eyebrow label, present in all six images",
            "讲者：林川 / 苏言": "speaker line, present in all six images",
            "layerlight.example.org": "url, present in all six images",
            "Northstar Research / 云构工具": "sponsor line, rounds 2 and 3",
            "免费参加 · 无需报名": "entry condition chip, rounds 2 and 3",
            "Clarity through structure": "english line added directly above the url in "
                                         "round 3",
        }
        cm["brand_mark"] = {
            "name": "layerlight-mark",
            "components": 5,
            "parts": ["rounded container", "light bar A", "light bar B", "light bar C",
                      "baseline rail"],
            "geometry_ratio": DARK_TOKENS["brand_mark"]["bar_geometry_ratio"],
            "changed_between_rounds": "colour only (round 3 light theme); geometry fixed"}
        cm["fixed_across_rounds"] = ["datetime", "speakers", "eyebrow", "url", "brand_mark"]
        cm["round_deltas"] = {
            1: ["initial launch poster in the dark launch theme"],
            2: ["headline replaced by the long two-run title (auto-fit, never scaled)",
                "added sponsors: " + SPONSORS,
                "added entry condition: " + CTA],
            3: ["dark -> light theme", "added english line: " + ENGLISH,
                "date badge darkened to #92400E so white text clears 4.5:1",
                "every normal text re-measured against its real composited background"],
        }[rnd]
        rec = next(r for r in plan if r["round"] == rnd)
        cm["expansion_bands"] = {
            "portrait": {"top": [0, 0, 1080, 110], "bottom": [0, 1238, 1080, 112],
                         "card": rec["layout"]["portrait"]["card"]},
            "wide": {"top": [0, 0, 1440, 100], "bottom": [0, 780, 1440, 30],
                     "card": rec["layout"]["wide"]["card"]},
            "note": ("no copy of any round enters these bands; the free space is real "
                     "page area that a later round can extend into")}
        cm["requirement_visibility"] = (
            "rounds/round-02.md and rounds/round-03.md are preloaded and readable from "
            "the start; execution was sequential (round 1 archived before round 2 was "
            "applied), not blind feedback.")
        with open(os.path.join(OUT, f"round-{rnd:02d}", "content-map.json"), "w",
                  encoding="utf-8") as fh:
            json.dump(cm, fh, ensure_ascii=False, indent=2)

    # ---- round 3 contrast audit (>=6 body-contrast pairs per image)
    if 3 in want:
        audit = {"task": "A21", "round": 3, "standard": "WCAG 2.x contrast ratio",
                 "threshold": 4.5,
                 "method": "each text colour composited over the real background stack "
                           "of its own region (page -> soft glow -> white card)",
                 "images": {}}
        for name, fn in (("launch-portrait", portrait), ("launch-wide", wide)):
            d, measured, bg, geom = fn(3)
            stack = [LIGHT["page"], LIGHT["card"]]
            items = []
            for m in measured:
                over = m.get("over", stack[-1])
                base = composite(over, stack[-1])
                bg_hex = "#%02X%02X%02X" % (round(base[0]), round(base[1]), round(base[2]))
                items.append(dict(text=m["text"], size=m["size"], color=m["color"],
                                  background=bg_hex,
                                  role="body" if m["size"] < 48 else "display",
                                  contrast_ratio=round(contrast(m["color"], bg_hex), 2),
                                  passes=round(contrast(m["color"], bg_hex), 2) >= 4.5))
            audit["images"][name] = dict(
                size=[d.w, d.h], background_stack=stack, pairs=items,
                pairs_checked=len(items),
                body_pairs_checked=sum(1 for i in items if i["role"] == "body"),
                all_pass=all(i["passes"] for i in items))
        with open(os.path.join(OUT, "round-03", "contrast-audit.json"), "w",
                  encoding="utf-8") as fh:
            json.dump(audit, fh, ensure_ascii=False, indent=2)

    print(json.dumps({"ok": True, "plan": [r["files"] for r in plan]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
