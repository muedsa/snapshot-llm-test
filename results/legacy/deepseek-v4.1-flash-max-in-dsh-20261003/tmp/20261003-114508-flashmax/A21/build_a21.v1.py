"""A21 "Layerlight" launch poster - builds every round from one parameterised model.

Round 1 and round 2 are the dark launch theme, round 3 is the light theme required by
rounds/round-03.md. The same brand mark (5 components: 1 container + 3 light bars +
1 baseline) and the same type scale are reused so the rounds stay comparable.

Every generated stage is also dumped as JSON next to the DSL so each round keeps its own
content map, tokens and measured contrast evidence.
"""
from __future__ import annotations

import json
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
    x, y, u = m["x"], m["y"], m["u"]
    sq = m["sq"]
    # baseline rail first so the bars read as standing on it
    b = m["base"]
    doc.box(round(x + b["x"] * u, 2), round(y + b["y"] * u, 2),
            round(b["w"] * u, 2), round(b["h"] * u, 2), b["c"],
            radius=round(b["h"] * u / 2, 2))
    for bar in m["bars"]:
        doc.box(round(x + bar["x"] * u, 2), round(y + bar["y"] * u, 2),
                round(bar["w"] * u, 2), round(bar["h"] * u, 2), bar["c"],
                radius=round(bar["w"] * u / 2, 2))
    doc.box(round(x, 2), round(y, 2), round(sq["w"] * u, 2), round(sq["h"] * u, 2),
            sq["fill"] or "#00000000", radius=round(sq["r"] * u, 2),
            border=f'{sq["border"]} SOLID {sq["bc"]}')


# --------------------------------------------------------------------------- themes
DARK = dict(page="#0B1220FF", deep="#0F172AFF", panel="#111C31FF", panel_edge="#1E293BFF",
            head="#F8FAFCFF", body="#CBD5E1FF", dim="#94A3B8FF", accent="#0E9F8FFF",
            accent_soft="#3ED3BEFF", warm="#D97706FF", warm_soft="#FBBF24FF")
LIGHT = dict(page="#EEF3F8FF", card="#FFFFFFFF", card_edge="#D8E1ECFF", head="#0F172AFF",
             body="#334155FF", dim="#475569FF", accent="#0F766EFF", accent_soft="#0E7490FF",
             warm_fill="#D97706FF", warm_text="#FFFFFF", cta_fill="#FEF3C7FF",
             cta_text="#92400EFF", cta_edge="#FCD34D", english="#0F766EFF")

DARK_TOKENS = {
    "color": {"page": "#0B1220", "ink": "#0F172A", "head": "#F8FAFC", "body": "#CBD5E1",
              "dim": "#94A3B8", "accent": "#0E9F8F", "accent_soft": "#3ED3BE",
              "warm": "#D97706", "warm_soft": "#FBBF24", "panel": "#111C31",
              "panel_edge": "#1E293B"},
    "type": {
        "portrait": {"title": 64, "display": 36, "lead": 32, "body": 30, "meta": 26},
        "wide": {"title": 72, "display": 40, "lead": 34, "body": 32, "meta": 28}},
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
ROUND3_CONTENT = ROUND2_CONTENT + [dict(id="english", text=ENGLISH, role="english tagline")]


# ------------------------------------------------------------------------ renderers
def portrait(rnd: int) -> tuple:
    """1080x1350 poster. rnd 1/2 = dark launch theme, 3 = light theme."""
    W, H = 1080, 1350
    light = rnd == 3
    t = LIGHT if light else DARK
    d = Doc(W, H, background=t["page"])
    tok = LIGHT_TOKENS if light else DARK_TOKENS
    ty = tok["type"]["portrait"]
    measured = []

    # ---- decorative background (bottom layer, never overlaps copy boxes)
    if light:
        d.box(0, 0, W, 16, t["accent"])
        d.box(-140, -120, 620, 460, t["glow_teal"], radius=230)
        d.box(W - 420, H - 470, 620, 400, t["glow_warm"], radius=230)
    else:
        d.box(-200, -260, 900, 700, "#0E9F8F1F", radius=360)
        d.box(W - 520, H - 560, 780, 560, "#1D4ED826", radius=380)
        d.box(0, 0, W, 16, t["accent"])
        d.box(0, H - 16, W, 16, "#1E293BFF")

    # ---- copy container: light theme wraps the copy in a real white card
    card_x, card_y, card_w, card_h = 44, 132, 992, 1154 if rnd >= 2 else 1140
    if light:
        card(d, card_x, card_y, card_w, card_h, radius=26, color=t["card"],
             border=t["card_edge"], shadow="0 10 30 0 #0F172A1F")
    mx = 72
    inner_w = card_w - 2 * (mx - card_x)
    bg_stack = [t["page"]] + ([t["card"]] if light else [])

    def put(y, s, size, color, weight="NORMAL", maxw=None, tag=None, spacing=None):
        d.text(mx, y, s, size, color, weight=weight, maxw=maxw or inner_w, tag=tag,
               spacing=spacing)
        measured.append(dict(text=s, size=size, color=color, y=y))
        return y + round(size * LINE_HEIGHT)

    # ---- brand mark (5 components) inside the top spacing band
    draw_mark(d, light_mark(96, mx, 176) if light else dark_mark(96, mx, 176))

    y = 306
    y = put(y, EYEBROW, ty["meta"] + 2, t["accent"], "BOLD", spacing=1.6)
    y += 20

    # ---- main headline: max 3 lines, never squeezed
    if rnd == 1:
        lines, tsize = [TAGLINE], ty["title"]
    else:
        tsize = 60
        lines = [R2_TITLE[0], R2_TITLE[1][:8], R2_TITLE[1][8:]]
    for ln in lines:
        assert_fits(ln, tsize, inner_w, "portrait-title")
    th = round(tsize * LINE_HEIGHT)
    d.box(mx, y + 4, 108, 8, t["accent"], radius=4)
    ty0 = y + 26
    for i, ln in enumerate(lines):
        d.text(mx, ty0 + i * th, ln, tsize, t["head"], weight="BOLD", maxw=inner_w,
               tag="portrait-title")
        measured.append(dict(text=ln, size=tsize, color=t["head"], y=ty0 + i * th))
    y = ty0 + len(lines) * th + 34

    y = put(y, SPEAKERS, ty["display"], t["head"], "BOLD")
    y += 74
    if rnd >= 2:
        y = put(y, SPONSORS, ty["lead"], t["body"])
        y += 54
        d.box(mx, y, inner_w, 2, t["panel_edge"] if not light else t["card_edge"])
        y += 56

    # ---- explanatory paragraph keeps the middle band from going empty
    for ln in ABOUT:
        assert_fits(ln, ty["meta"], inner_w, "about")
        d.text(mx, y, ln, ty["meta"], t["dim"], maxw=inner_w, tag="about")
        measured.append(dict(text=ln, size=ty["meta"], color=t["dim"], y=y))
        y += round(ty["meta"] * 1.5)

    # ---- bottom cluster, all of it above the empty bottom band
    if rnd == 3:
        assert_fits(ENGLISH, ty["english"], inner_w, "english")
        d.text(mx, 1038, ENGLISH, ty["english"], t["english"], weight="BOLD",
               maxw=inner_w, tag="english")
        measured.append(dict(text=ENGLISH, size=ty["english"], color=t["english"], y=1038))
        d.text(mx, 1092, URL, ty["lead"], t["accent"], weight="BOLD", maxw=inner_w,
               tag="url")
        measured.append(dict(text=URL, size=ty["lead"], color=t["accent"], y=1092))
        d.box(mx, 1182, 386, 62, t["cta_fill"], radius=31,
              border=f"1 SOLID {t['cta_edge']}")
        d.text(mx + 26, 1197, CTA, ty["meta"], t["cta_text"], weight="BOLD",
               maxw=340, tag="cta")
        measured.append(dict(text=CTA, size=ty["meta"], color=t["cta_text"], y=1197,
                             over=t["cta_fill"]))
        d.box(984 - 314, 1182, 314, 62, t["warm_fill"], radius=31)
        d.rtext(984 - 26, 1197, DT, ty["meta"], t["warm_text"], weight="BOLD")
        measured.append(dict(text=DT, size=ty["meta"], color=t["warm_text"], y=1197,
                             over=t["warm_fill"]))
    else:
        uy, dy = (1012, 1070) if rnd == 1 else (1038, 1096)
        d.text(mx, uy, URL, ty["display"], t["accent_soft"], weight="BOLD", maxw=inner_w,
               tag="url")
        measured.append(dict(text=URL, size=ty["display"], color=t["accent_soft"], y=uy))
        d.text(mx, dy, DT, ty["display"], t["warm_soft"], weight="BOLD",
               maxw=inner_w, tag="datetime")
        measured.append(dict(text=DT, size=ty["display"], color=t["warm_soft"], y=dy))
        if rnd >= 2:
            chip_w = round(text_width(CTA, ty["meta"]) + 56)
            d.box(mx, 1190, chip_w, 58, "#0E9F8F2E", radius=29,
                  border="1 SOLID #0E9F8F88")
            d.text(mx + 28, 1204, CTA, ty["meta"], t["accent_soft"], weight="BOLD",
                   maxw=chip_w - 56, tag="cta")
            measured.append(dict(text=CTA, size=ty["meta"], color=t["accent_soft"],
                                 y=1204, over="#0E9F8F2E"))
    assert y <= card_y + card_h - 120, f"portrait copy overruns the card: y={y}"
    return d, measured, bg_stack, dict(card=[card_x, card_y, card_w, card_h])


def wide(rnd: int) -> tuple:
    W, H = 1440, 810
    light = rnd == 3
    t = LIGHT if light else DARK
    d = Doc(W, H, background=t["page"])
    tok = LIGHT_TOKENS if light else DARK_TOKENS
    ty = tok["type"]["wide"]
    measured = []

    if light:
        d.box(0, 0, W, 14, t["accent"])
        d.box(-180, -200, 900, 620, t["glow_teal"], radius=310)
        d.box(W - 520, H - 420, 760, 520, t["glow_warm"], radius=260)
    else:
        d.box(-260, -300, 1100, 780, "#0E9F8F1F", radius=390)
        d.box(W - 640, H - 520, 940, 620, "#1D4ED826", radius=320)
        d.box(0, 0, W, 14, t["accent"])
        d.box(0, H - 14, W, 14, "#1E293BFF")

    card_x, card_y, card_w, card_h = 48, 112, 1344, 596
    if light:
        card(d, card_x, card_y, card_w, card_h, radius=24, color=t["card"],
             border=t["card_edge"], shadow="0 10 30 0 #0F172A1F")
    mx = 96
    inner_w = 760
    bg_stack = [t["page"]] + ([t["card"]] if light else [])

    def put(y, s, size, color, weight="NORMAL", maxw=None, tag=None, spacing=None):
        d.text(mx, y, s, size, color, weight=weight, maxw=maxw or inner_w, tag=tag,
               spacing=spacing)
        measured.append(dict(text=s, size=size, color=color, y=y))
        return y + round(size * LINE_HEIGHT)

    draw_mark(d, light_mark(135, mx, 144) if light else dark_mark(135, mx, 144))
    y = 306
    y = put(y, EYEBROW, ty["meta"], t["accent"], "BOLD", spacing=1.6)
    y += 16
    if rnd == 1:
        assert_fits(TAGLINE, ty["title"], inner_w, "wide-title")
        d.text(mx, y, TAGLINE, ty["title"], t["head"], weight="BOLD", maxw=inner_w,
               tag="wide-title")
        measured.append(dict(text=TAGLINE, size=ty["title"], color=t["head"], y=y))
        y += round(ty["title"] * LINE_HEIGHT) + 24
    else:
        for ln in R2_TITLE:
            assert_fits(ln, 60, inner_w, "wide-title")
            d.text(mx, y, ln, 60, t["head"], weight="BOLD", maxw=inner_w,
                   tag="wide-title")
            measured.append(dict(text=ln, size=60, color=t["head"], y=y))
            y += round(60 * LINE_HEIGHT)
        y += 18
    y = put(y, SPEAKERS, ty["display"], t["head"], "BOLD")
    y += 30
    if rnd >= 2:
        y = put(y, SPONSORS, ty["lead"], t["body"])
        y += 34
    d.box(mx, y, inner_w, 2, t["card_edge"] if light else t["panel_edge"])
    y += 30
    for ln in ABOUT:
        assert_fits(ln, ty["meta"], inner_w, "wide-about")
        d.text(mx, y, ln, ty["meta"], t["dim"], maxw=inner_w, tag="wide-about")
        measured.append(dict(text=ln, size=ty["meta"], color=t["dim"], y=y))
        y += round(ty["meta"] * 1.5)

    # ---- right-hand brand panel
    px, py, pw, ph = 920, 160, 424, 560
    if light:
        d.box(px, py, pw, ph, t["card"], radius=22, border=f"1 SOLID {t['card_edge']}")
    else:
        d.box(px, py, pw, ph, t["panel"], radius=22, border=f"1 SOLID {t['panel_edge']}")
        d.box(px + 40, py + 52, 344, 344, "#0E9F8F26", radius=172)
    draw_mark(d, light_mark(150, px + 137, py + 116) if light
              else dark_mark(150, px + 137, py + 116))
    d.text(px, py + 402, EYEBROW, ty["meta"], t["accent"], weight="BOLD", spacing=1.6,
           maxw=pw, align="CENTER_LEFT")
    d.text(px, py + 444, DT, ty["display"], t["warm_fill"] if light else t["warm_soft"],
           weight="BOLD", maxw=pw, align="CENTER_LEFT")
    measured.append(dict(text=DT, size=ty["display"],
                         color=t["warm_fill"] if light else t["warm_soft"], y=py + 444,
                         over=t["card"] if light else t["panel"]))

    # ---- decorative bar stack in the empty bottom-right corner (never carries copy)
    for bx, by, bw, bh, bc in [(92, 0, 64, 22, "#0E9F8FFF"),
                               (174, 0, 128, 22, "#1D4ED8FF"),
                               (320, 0, 88, 22, "#D97706FF")]:
        d.box(bx, 742, bw, bh, bc, radius=11)

    # ---- bottom cluster
    if rnd == 3:
        assert_fits(ENGLISH, ty["english"], inner_w, "english")
        d.text(mx, 622, ENGLISH, ty["english"], t["english"], weight="BOLD", maxw=inner_w,
               tag="english")
        measured.append(dict(text=ENGLISH, size=ty["english"], color=t["english"], y=622))
        assert_fits(ENGLISH + "     " + URL, ty["body"], inner_w, "english+url")
        d.text(mx, 668, URL, ty["display"], t["accent"], weight="BOLD", maxw=inner_w,
               tag="url")
        measured.append(dict(text=URL, size=ty["display"], color=t["accent"], y=668))
        cw = round(text_width(CTA, ty["meta"]) + 52)
        d.box(mx + 372, 470, cw, 52, t["cta_fill"], radius=26,
              border=f"1 SOLID {t['cta_edge']}")
        d.text(mx + 372 + 26, 481, CTA, ty["meta"], t["cta_text"], weight="BOLD",
               maxw=cw - 52, tag="cta")
        measured.append(dict(text=CTA, size=ty["meta"], color=t["cta_text"], y=481,
                             over=t["cta_fill"]))
    else:
        uy = 622 if rnd == 1 else 656
        d.text(mx, uy, URL, ty["display"], t["accent_soft"], weight="BOLD", maxw=inner_w,
               tag="url")
        measured.append(dict(text=URL, size=ty["display"], color=t["accent_soft"], y=uy))
        if rnd >= 2:
            cw = round(text_width(CTA, ty["meta"]) + 52)
            d.box(mx + 372, uy - 6, cw, 52, "#0E9F8F2E", radius=26,
                  border="1 SOLID #0E9F8F88")
            d.text(mx + 372 + 26, uy + 5, CTA, ty["meta"], t["accent_soft"], weight="BOLD",
                   maxw=cw - 52, tag="cta")
            measured.append(dict(text=CTA, size=ty["meta"], color=t["accent_soft"],
                                 y=uy + 5, over="#0E9F8F2E"))
    assert y <= 706, f"wide copy overruns the card: y={y}"
    return d, measured, bg_stack, dict(card=[card_x, card_y, card_w, card_h])


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
            1: "dark launch theme, one-line headline",
            2: "dark launch theme kept; headline replaced by the 3-line long title; "
               "sponsors and entry condition added",
            3: "light theme; identical copy and brand mark; english tagline added above "
               "the url; all normal text >= 4.5:1 against the composited background",
        }[rnd]
        if rnd == 3:
            tok["theme"] = "light"
        else:
            tok["theme"] = "dark"
        with open(os.path.join(OUT, f"round-{rnd:02d}", "design-tokens.json"), "w",
                  encoding="utf-8") as fh:
            json.dump(tok, fh, ensure_ascii=False, indent=2)

    # ---- content maps
    for rnd in want:
        base_content = {1: ROUND1_CONTENT, 2: ROUND2_CONTENT, 3: ROUND3_CONTENT}[rnd]
        cm = {"task": "A21", "round": rnd, "canvas": {"portrait": [1080, 1350],
                                                      "wide": [1440, 810]},
              "elements": []}
        entries = []
        for item in base_content:
            rows = []
            for layout in ("portrait", "wide"):
                rec = next(r for r in plan if r["round"] == rnd)
                found = [m for m in rec["layout"][layout]["texts"] if m["text"] == item["text"]]
                for f in found:
                    rows.append(dict(layout=layout, x=None, y=f["y"], size=f["size"],
                                     color=f["color"]))
            entries.append(dict(id=item["id"], text=item["text"], role=item["role"],
                                placements=rows))
        cm["elements"] = entries
        cm["brand_mark"] = {
            "name": "layerlight-mark",
            "components": 5,
            "parts": ["rounded container", "light bar A", "light bar B", "light bar C",
                      "baseline rail"],
            "geometry_ratio": DARK_TOKENS["brand_mark"]["bar_geometry_ratio"],
            "changed_between_rounds": "colour only (round 3 light theme); geometry fixed"}
        cm["fixed_across_rounds"] = ["datetime", "speakers", "eyebrow", "url", "brand_mark"]
        cm["round_deltas"] = {
            1: ["initial launch poster"],
            2: ["title -> 3-line long title (>=48px, <=3 lines)",
                "added sponsors: " + SPONSORS, "added entry condition: " + CTA],
            3: ["dark -> light theme", "added english tagline: " + ENGLISH,
                "all normal text re-checked against the composited background"],
        }[rnd]
        cm["expansion_bands"] = {"portrait": {"top": [0, 0, 1080, 96],
                                              "bottom": [0, 1254, 1080, 96]},
                                 "wide": {"top": [0, 0, 1440, 96],
                                          "bottom": [0, 714, 1440, 96]},
                                 "note": "kept free of copy in every round"}
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
