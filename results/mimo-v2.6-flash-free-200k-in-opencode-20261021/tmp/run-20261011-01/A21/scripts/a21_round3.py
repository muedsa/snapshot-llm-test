# -*- coding: utf-8 -*-
"""A21 round-03: light theme + English line + real-pixel contrast audit.

Round-03 requirements (rounds/round-03.md):
  * light theme, every ordinary text vs its ACTUAL composited background >= 4.5:1
  * keep ALL round-02 copy + brand graphics; sponsor must not disappear
  * add EN line "Clarity through structure" ABOVE the url, size >= 24
  * sizes unchanged; CN long title still <=3 lines, >=48
  * per image: contrast-audit.json with >=6 body-text samples incl. the worst
    position, computed on the real final background (not nominal tokens)

Theme note: rounds 01/02 already used a light theme (near-white paper #FBFAFF,
white plates). Round-03 keeps the exact primary #4F46E5 and the 5 brand
constructs (brand preserved per requirement) and *proves* the light theme is
compliant by sampling the real composited background from a text-removed
auxiliary render of each image.

For every image this script emits:
  * the final DSL
  * a text-removed DSL (identical layers, text="" ) used only as background
    evidence (kept in tmp per requirement)

Usage (launch base = suite root):
  python tmp/run-20261011-01/A21/scripts/a21_round3.py
"""
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import a21_identity as I  # noqa: E402
import a21_round1 as R1   # noqa: E402
import a21_round2 as R2   # noqa: E402  (info_plate2, cta_pill, Stack)

ROOT = pathlib.Path(__file__).resolve().parents[4]
GEN = ROOT / "tmp/run-20261011-01/A21/round-03"

TITLE_SIZE = 48
TITLE_LINE = 1.16
EN_SIZE = 26          # >= 24 requirement
MIN_GAP = 16.0


def en_line_el(l, t, w, text, size=EN_SIZE):
    """Standalone English sentence above the url (PRIMARY, bold)."""
    return R1.text_el(l, t, w, size * 1.3, text, size, R1.col("PRIMARY"),
                      weight="BOLD")


def build_portrait():
    W, H = I.SIZES["portrait"]
    S = R2.Stack()
    S.els.append(R1.rect(0, 0, W, H, R1.col("PAPER")))
    S.els.append(R1.rect(0, 0, W, 300,
                         R1._blend(R1.col("PRIMARY"), I.PAPER, 0.90)))
    M = 96

    S.els.append(R1.text_el(M, 120, 500, 54, I.BRAND_CN, 40, R1.col("INK"),
                            weight="BOLD"))
    S.els.append(R1.text_el(M, 172, 500, 34, I.BRAND_EN, 26,
                            R1.col("PRIMARY"), weight="BOLD"))
    S.add("wordmark", 120, 206)
    pm, pmh = R1.prism_mark(W - M - 150, 118, 1.0)
    S.els.extend(pm)
    S.add("prism", 118, 118 + pmh, side=True)

    y = 300
    S.els.append(R1.text_el(M, y, 600, 32, I.REQUIRED["kicker"], 24,
                            R1.col("PRIMARY"), weight="BOLD"))
    S.add("kicker", y, y + 31.2)
    y = 344
    S.els.append(R1.baseline_rule(M, y, W - 2 * M))

    y = 374
    tl = I.wrap(I.TITLE_R2, TITLE_SIZE, W - 2 * M)
    assert len(tl) <= 3, tl
    th = I.text_h(len(tl), TITLE_SIZE, TITLE_LINE)
    for i, ln in enumerate(tl):
        S.els.append(R1.text_el(M, y + i * TITLE_SIZE * TITLE_LINE,
                                W - 2 * M, 58, ln, TITLE_SIZE,
                                R1.col("INK"), weight="BOLD"))
    S.add("title", y, y + th)
    y = y + th + 18

    pill, pw, ph = R1.tagline_pill(M, y, "叠光 Layerlight · 结构化呈现", 26)
    S.els.append(pill)
    S.add("brand_pill", y, y + ph)
    y = y + ph + 26
    S.els.append(R1.baseline_rule(M, y, W - 2 * M))
    y = y + 34

    for label, key, size in (("时间", "datetime", 34),
                             ("讲者", "speakers", 30)):
        p, h, _ = R2.info_plate2(M, y, W - 2 * M, label, I.REQUIRED[key], size)
        S.add(label, y, y + h, p)
        y = y + h + 20

    # NEW in round-03: English sentence above the url
    S.els.append(en_line_el(M, y, W - 2 * M, I.EN_R3, EN_SIZE))
    S.add("en_line", y, y + EN_SIZE * 1.3)
    y = y + EN_SIZE * 1.3 + 16

    p, h, _ = R2.info_plate2(M, y, W - 2 * M, "参与网址", I.REQUIRED["url"], 26)
    S.add("参与网址", y, y + h, p)
    y = y + h + 20
    sp, sph, spv = R2.info_plate2(M, y, W - 2 * M, "赞助方", I.SPONSOR_R2, 30)
    S.add("sponsor", y, y + sph, sp)
    y = y + sph + 20
    cta, cw, ch = R2.cta_pill(M, y, I.CTA_R2, 30)
    S.add("cta", y, y + ch, cta)

    return S, W, H, {"title_lines": len(tl), "en_size": EN_SIZE,
                     "content_bottom": round(y + ch, 2)}


def build_wide():
    W, H = I.SIZES["wide"]
    S = R2.Stack()
    S.els.append(R1.rect(0, 0, W, H, R1.col("PAPER")))
    col_w = 560
    S.els.append(R1.rect(0, 0, col_w, H,
                         R1._blend(R1.col("PRIMARY"), I.PAPER, 0.90)))
    M = 72

    S.els.append(R1.text_el(M, 96, 420, 52, I.BRAND_CN, 40, R1.col("INK"),
                            weight="BOLD"))
    S.els.append(R1.text_el(M, 148, 420, 34, I.BRAND_EN, 26,
                            R1.col("PRIMARY"), weight="BOLD"))
    S.add("wordmark", 96, 182)
    pm, pmh = R1.prism_mark(M, 236, 1.12)
    S.els.extend(pm)
    S.add("prism", 236, 236 + pmh)

    y = 236 + pmh + 40
    pill, pw, ph = R1.tagline_pill(M, y, "叠光 Layerlight · 结构化呈现", 26)
    S.els.append(pill)
    S.add("brand_pill", y, y + ph)
    y = y + ph + 24

    lw = col_w - 2 * M
    sp, sph, spv = R2.info_plate2(M, y, lw, "赞助方", I.SPONSOR_R2, 26)
    S.add("sponsor", y, y + sph, sp)
    y = y + sph + 18
    cta, cw, ch = R2.cta_pill(M, y, I.CTA_R2, 26)
    S.add("cta", y, y + ch, cta)

    RX = col_w + 80
    RW = W - RX - M
    R = R2.Stack()
    R.els = S.els
    y = 118
    R.add("kicker", y, y + 31.2,
          R1.text_el(RX, y, RW, 32, I.REQUIRED["kicker"], 24,
                     R1.col("PRIMARY"), weight="BOLD"))
    y = 162
    R.els.append(R1.baseline_rule(RX, y, RW))

    y = 198
    tl = I.wrap(I.TITLE_R2, TITLE_SIZE, RW)
    assert len(tl) <= 3, tl
    th = I.text_h(len(tl), TITLE_SIZE, TITLE_LINE)
    for i, ln in enumerate(tl):
        R.els.append(R1.text_el(RX, y + i * TITLE_SIZE * TITLE_LINE, RW, 58,
                                ln, TITLE_SIZE, R1.col("INK"), weight="BOLD"))
    R.add("title", y, y + th)
    y = y + th + 20
    R.els.append(R1.baseline_rule(RX, y, RW))
    y = y + 34

    for label, key, size in (("时间", "datetime", 34),
                             ("讲者", "speakers", 30)):
        p, h, _ = R2.info_plate2(RX, y, RW, label, I.REQUIRED[key], size)
        R.add(label, y, y + h, p)
        y = y + h + 20

    # NEW in round-03: English sentence above the url
    R.els.append(en_line_el(RX, y, RW, I.EN_R3, EN_SIZE))
    R.add("en_line", y, y + EN_SIZE * 1.3)
    y = y + EN_SIZE * 1.3 + 16

    p, h, _ = R2.info_plate2(RX, y, RW, "参与网址", I.REQUIRED["url"], 26)
    R.add("参与网址", y, y + h, p)
    y = y + h + 20

    return S, R, W, H, {"title_lines": len(tl), "en_size": EN_SIZE,
                        "content_bottom": round(y, 2)}


def strip_text(dsl):
    """Return the DSL with all Text content emptied (layers preserved)."""
    return re.sub(r'text="[^"]*"', 'text=""', dsl)


def main():
    GEN.mkdir(parents=True, exist_ok=True)
    geom = {}

    sp, W, H, m1 = build_portrait()
    dsl = R1.emit(sp.els, W, H)
    (GEN / "launch-portrait.snapshot").write_text(dsl, encoding="utf-8")
    (GEN / "launch-portrait.snapshot").with_name(
        "launch-portrait.notext.snapshot").write_text(
        strip_text(dsl), encoding="utf-8")
    g1 = sp.min_gaps()
    assert min(g1) >= MIN_GAP, g1
    geom["launch-portrait"] = {"size": [W, H], "blocks": sp.blocks,
                               "gaps_px": g1, "min_gap_px": min(g1), **m1}
    print("portrait: %dx%d, %d bytes, title %d lines@%d, min gap %.1f, bottom y=%d"
          % (W, H, len(dsl.encode("utf-8")), m1["title_lines"], TITLE_SIZE,
             min(g1), m1["content_bottom"]))

    sl, sr, W, H, m2 = build_wide()
    dsl = R1.emit(sl.els, W, H)
    (GEN / "launch-wide.snapshot").write_text(dsl, encoding="utf-8")
    (GEN / "launch-wide.snapshot").with_name(
        "launch-wide.notext.snapshot").write_text(
        strip_text(dsl), encoding="utf-8")
    g2 = sl.min_gaps() + sr.min_gaps()
    assert min(g2) >= MIN_GAP, g2
    geom["launch-wide"] = {"size": [W, H], "left_column_blocks": sl.blocks,
                           "left_gaps_px": sl.min_gaps(),
                           "right_column_blocks": sr.blocks,
                           "right_gaps_px": sr.min_gaps(),
                           "min_gap_px": min(g2), **m2}
    print("wide: %dx%d, %d bytes, title %d lines@%d, min gap %.1f, bottom y=%d"
          % (W, H, len(dsl.encode("utf-8")), m2["title_lines"], TITLE_SIZE,
             min(g2), m2["content_bottom"]))

    (GEN / "round3-geom.json").write_text(
        json.dumps(geom, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
