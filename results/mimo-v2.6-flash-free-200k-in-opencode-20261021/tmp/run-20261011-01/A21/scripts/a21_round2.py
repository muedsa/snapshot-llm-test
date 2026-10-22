# -*- coding: utf-8 -*-
"""A21 round-02: long title + sponsor + CTA on both round-01 compositions.

Changes vs round-01 (per rounds/round-02.md):
  * main title replaced by the long sentence, max 3 lines, size >= 48
  * NEW sponsor block "Northstar Research / 云构工具" and CTA "免费参加 · 无需报名"
  * datetime / speakers / ONLINE LAUNCH / url all retained
  * primary colour + 5 brand constructs unchanged (may move/scale)
  * sizes unchanged; no Transform-squeezed text anywhere

Collision strategy (recorded in round2-geom.json as evidence):
  every block is stacked by a cursor y = previous block bottom + gap;
  block heights come from measured wrapped line counts (I.wrap/I.measure
  with 1.06 safety), so the taller long title pushes everything down
  deterministically instead of overlapping.  The new sponsor/CTA go into the
  space that round-01 deliberately reserved (portrait bottom band / wide
  left column), so they cannot collide with the title block at all.

Usage (launch base = suite root):
  python tmp/run-20261011-01/A21/scripts/a21_round2.py
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import a21_identity as I  # noqa: E402
import a21_round1 as R1   # noqa: E402  (reuses emit helpers + constructs)

ROOT = pathlib.Path(__file__).resolve().parents[4]
GEN = ROOT / "tmp/run-20261011-01/A21/round-02"

TITLE_SIZE = 48          # >= 48 requirement
TITLE_LINE = 1.16
MIN_GAP = 16.0           # enforced vertical gap between stacked blocks


def info_plate2(l, t, w, label, value, size, label_size=24):
    """Round-1 info plate, but wrap-aware for multi-line values."""
    vlines = I.wrap(value, size, w - 44)
    vh = I.text_h(len(vlines), size, 1.25)
    h = label_size * 1.3 + vh + 34
    els = [R1.rect(l, t, w, h, R1.col("SURFACE"), radius=16,
                   border="2 SOLID %s" % R1.col("MUTED_LINE"))]
    els.append(R1.rect(l, t + 16, 5, h - 32, R1.col("PRIMARY"), radius=2.5))
    els.append(R1.text_el(l + 22, t + 14, w - 40, label_size * 1.3, label,
                          label_size, R1.col("PRIMARY"), weight="BOLD"))
    vy = t + 14 + label_size * 1.3 + 4
    for i, ln in enumerate(vlines):
        els.append(R1.text_el(l + 22, vy + i * size * 1.25, w - 40,
                              size * 1.3, ln, size, R1.col("INK"),
                              weight="BOLD"))
    return "".join(els), h, len(vlines)


def cta_pill(l, t, text, size=30, pad_x=28, pad_y=16):
    """CTA construct: primary-filled pill, white bold text (contrast checked
    in round-03 against the real composited colour)."""
    tw = I.measure(text, size)
    w = tw + pad_x * 2
    h = size * 1.3 + pad_y * 2
    els = [R1.rect(l, t, w, h, R1.col("PRIMARY"), radius=h / 2)]
    els.append(R1.text_el(l + pad_x, t + pad_y - 2, tw + 10, size * 1.3,
                          text, size, "#FFFFFF", weight="BOLD"))
    return "".join(els), w, h


class Stack(object):
    """Cursor + block ledger so vertical rhythm is auditable."""

    def __init__(self):
        self.els = []
        self.blocks = []

    def add(self, bid, top, bottom, el=None, side=False):
        """side=True marks decor that sits in a different horizontal zone
        (e.g. the portrait prism beside the wordmark); it is recorded but
        excluded from the vertical gap check."""
        if el:
            self.els.append(el)
        self.blocks.append({"id": bid, "top": round(top, 2),
                            "bottom": round(bottom, 2), "side": side})

    def min_gaps(self):
        seq = [b for b in self.blocks if not b.get("side")]
        return [round(seq[i + 1]["top"] - seq[i]["bottom"], 2)
                for i in range(len(seq) - 1)]


def build_portrait():
    W, H = I.SIZES["portrait"]
    S = Stack()
    S.els.append(R1.rect(0, 0, W, H, R1.col("PAPER")))
    S.els.append(R1.rect(0, 0, W, 300,
                         R1._blend(R1.col("PRIMARY"), I.PAPER, 0.90)))
    M = 96

    # wordmark (top band)
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

    # --- long title (round-02 requirement): 48px, <=3 lines ---------------
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
                             ("讲者", "speakers", 30),
                             ("参与网址", "url", 26)):
        p, h, _ = info_plate2(M, y, W - 2 * M, label, I.REQUIRED[key], size)
        S.add(label, y, y + h, p)
        y = y + h + 20
    y -= 20

    # --- round-02 additions: into the reserved bottom band ---------------
    y += 30
    sp, sph, spv = info_plate2(M, y, W - 2 * M, "赞助方", I.SPONSOR_R2, 30)
    S.add("sponsor", y, y + sph, sp)
    y = y + sph + 20
    cta, cw, ch = cta_pill(M, y, I.CTA_R2, 30)
    S.add("cta", y, y + ch, cta)

    return S, W, H, {"title_lines": len(tl), "title_size": TITLE_SIZE,
                     "sponsor_value_lines": spv,
                     "content_bottom": round(y + ch, 2)}


def build_wide():
    W, H = I.SIZES["wide"]
    S = Stack()
    S.els.append(R1.rect(0, 0, W, H, R1.col("PAPER")))
    col_w = 560
    S.els.append(R1.rect(0, 0, col_w, H,
                         R1._blend(R1.col("PRIMARY"), I.PAPER, 0.90)))
    M = 72

    # left column: wordmark -> prism -> brand pill -> sponsor -> CTA
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
    sp, sph, spv = info_plate2(M, y, lw, "赞助方", I.SPONSOR_R2, 26)
    S.add("sponsor", y, y + sph, sp)
    y = y + sph + 18
    cta, cw, ch = cta_pill(M, y, I.CTA_R2, 26)
    S.add("cta", y, y + ch, cta)

    # right column: eyebrow -> rule -> long title -> rule -> 3 plates
    RX = col_w + 80
    RW = W - RX - M
    R = Stack()
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
                             ("讲者", "speakers", 30),
                             ("参与网址", "url", 26)):
        p, h, _ = info_plate2(RX, y, RW, label, I.REQUIRED[key], size)
        R.add(label, y, y + h, p)
        y = y + h + 20

    return S, R, W, H, {"title_lines": len(tl), "title_size": TITLE_SIZE,
                        "sponsor_value_lines": spv,
                        "content_bottom": round(y, 2)}


def main():
    GEN.mkdir(parents=True, exist_ok=True)
    geom = {}

    sp, W, H, m1 = build_portrait()
    dsl = R1.emit(sp.els, W, H)
    (GEN / "launch-portrait.snapshot").write_text(dsl, encoding="utf-8")
    gaps1 = sp.min_gaps()
    assert min(gaps1) >= MIN_GAP, gaps1
    geom["launch-portrait"] = {
        "size": [W, H], "blocks": sp.blocks, "gaps_px": gaps1,
        "min_gap_px": min(gaps1), **m1}
    print("portrait: %dx%d, %d bytes, title %d lines@%d, min gap %.1f, bottom y=%d"
          % (W, H, len(dsl.encode("utf-8")), m1["title_lines"],
             TITLE_SIZE, min(gaps1), m1["content_bottom"]))

    sl, sr, W, H, m2 = build_wide()
    dsl = R1.emit(sl.els, W, H)
    (GEN / "launch-wide.snapshot").write_text(dsl, encoding="utf-8")
    gaps_l = sl.min_gaps()
    gaps_r = sr.min_gaps()
    assert min(gaps_l + gaps_r) >= MIN_GAP, (gaps_l, gaps_r)
    geom["launch-wide"] = {
        "size": [W, H], "left_column_blocks": sl.blocks,
        "left_gaps_px": gaps_l, "right_column_blocks": sr.blocks,
        "right_gaps_px": gaps_r,
        "min_gap_px": min(gaps_l + gaps_r), **m2}
    print("wide: %dx%d, %d bytes, title %d lines@%d, min gap %.1f, bottom y=%d"
          % (W, H, len(dsl.encode("utf-8")), m2["title_lines"],
             TITLE_SIZE, min(gaps_l + gaps_r), m2["content_bottom"]))

    (GEN / "round2-geom.json").write_text(
        json.dumps(geom, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
