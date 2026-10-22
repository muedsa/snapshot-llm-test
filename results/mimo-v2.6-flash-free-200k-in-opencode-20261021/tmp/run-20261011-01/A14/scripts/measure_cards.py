# -*- coding: utf-8 -*-
"""Pixel measurement for A14 batch cards (1200x630).

Usage: measure_cards.py <version>      e.g. measure_cards.py v4
Writes: tmp/run-20261011-01/A14/measured-cards-<ver>.json

Checks per card (all from real render pixels, threshold lum>70):
  * size == 1200x630
  * all bright ink inside safe margin [40,1160]x[40,590]
  * title region: ink band count == title_line_count, each band within the
    declared line box +-4 (detects service soft-wrap / dropped glyph like the
    v3 date bug), band width <= 1120
  * speaker region: band count == speaker_line_count, inside box +-4
  * header brand / index / date: single band each, date band == 10-char width
    (>=110px => no dropped glyph), index/date/text pills vertically single-line
  * time / badge / annotation pills: text ink inside pill inner window, no
    second line (band below pill top+34)
  * title block bottom < divider - 8  (no collision with status badge which
    lives below the divider)
  * declared fonts: title>=36, speaker>=22 (from layout JSON)
"""
import json
import pathlib
import sys
from PIL import Image

RUN = "run-20261011-01"
BASE = pathlib.Path("tmp") / RUN / "A14"
VER = sys.argv[1] if len(sys.argv) > 1 else "v4"
CARDS = BASE / "cards" / VER
THRESH = 70
M = 40


def lum(p):
    r, g, b = p[0], p[1], p[2]
    return (r * 299 + g * 587 + b * 114) // 1000


def bands(px, x1, y1, x2, y2, gap=3, thr=THRESH):
    out, cur, last = [], None, None
    for y in range(y1, y2 + 1):
        xs = [x for x in range(x1, x2 + 1) if lum(px[x, y]) > thr]
        if xs:
            if cur is None:
                cur = [y, y, min(xs), max(xs), len(xs)]
            elif y - last >= gap:
                out.append(cur)
                cur = [y, y, min(xs), max(xs), len(xs)]
            else:
                cur[1] = y
                cur[2] = min(cur[2], min(xs))
                cur[3] = max(cur[3], max(xs))
                cur[4] += len(xs)
            last = y
    if cur:
        out.append(cur)
    return out


def dark_bands(px, x1, y1, x2, y2, gap=3, thr=90):
    """Bands of DARK pixels (text on a bright fill)."""
    out, cur, last = [], None, None
    for y in range(y1, y2 + 1):
        xs = [x for x in range(x1, x2 + 1) if lum(px[x, y]) < thr]
        if xs:
            if cur is None:
                cur = [y, y, min(xs), max(xs), len(xs)]
            elif y - last >= gap:
                out.append(cur)
                cur = [y, y, min(xs), max(xs), len(xs)]
            else:
                cur[1] = y
                cur[2] = min(cur[2], min(xs))
                cur[3] = max(cur[3], max(xs))
                cur[4] += len(xs)
            last = y
    if cur:
        out.append(cur)
    return out


def main():
    layout = json.loads((CARDS / f"layout-{VER}.json").read_text(encoding="utf-8"))
    report = {"version": VER, "cards": [], "failures": []}
    F = report["failures"]

    for rec in layout["cards"]:
        cid = rec["id"]
        png = CARDS / f"card-{cid}.png"
        img = Image.open(png).convert("RGB")
        W, H = img.size
        px = img.load()
        c = {"id": cid, "png": str(png), "size": [W, H], "checks": {}}

        if (W, H) != (1200, 630):
            F.append(f"{cid}: size {(W,H)} != (1200,630)")

        # global ink inside safe margin
        ink_xy = [(x, y) for y in range(0, H, 2) for x in range(0, W, 2)
                  if lum(px[x, y]) > THRESH]
        # background gradient is dark (lum<70); pills/borders bright
        ib = [min(p[0] for p in ink_xy), min(p[1] for p in ink_xy),
              max(p[0] for p in ink_xy), max(p[1] for p in ink_xy)]
        c["checks"]["ink_bbox"] = ib
        if ib[0] < M - 2 or ib[1] < M - 2 or ib[2] > W - M + 2 or ib[3] > H - M + 2:
            F.append(f"{cid}: ink bbox {ib} violates safe margin {M}")

        # title bands
        tb = rec["title_line_boxes"]
        ty1 = tb[0][1] - 6
        ty2 = tb[-1][3] + 6
        tband = bands(px, tb[0][0], ty1, tb[0][2], ty2)
        c["checks"]["title_bands"] = len(tband)
        c["checks"]["title_expected"] = rec["title_line_count"]
        if len(tband) != rec["title_line_count"]:
            F.append(f"{cid}: title bands {len(tband)} != {rec['title_line_count']} "
                     f"(soft-wrap or dropped glyph)")
        for i, (y1, y2, x1, x2, n) in enumerate(tband):
            d = tb[min(i, len(tb) - 1)]
            # ink must be CONTAINED in the declared line box (+-4 AA tolerance):
            # line boxes include leading, so ink top sits ~17px below box top
            if y1 < d[1] - 4 or y2 > d[3] + 4:
                F.append(f"{cid}: title band[{i}] y {y1}-{y2} outside box "
                         f"{d[1]}-{d[3]} (+-4)")
            if x1 < d[0] - 4 or x2 > d[2] + 4:
                F.append(f"{cid}: title band[{i}] x {x1}-{x2} outside box "
                         f"{d[0]}-{d[2]} (+-4)")

        # declared fonts
        if rec["title_font_size"] < 36:
            F.append(f"{cid}: title font {rec['title_font_size']} < 36")
        if rec["speaker_font_size"] < 22:
            F.append(f"{cid}: speaker font {rec['speaker_font_size']} < 22")
        if rec["title_line_count"] > 3:
            F.append(f"{cid}: title lines {rec['title_line_count']} > 3")

        # title must stay above divider (badge sits below divider -> no collision)
        if tb[-1][3] > rec["divider_y"] - 8:
            F.append(f"{cid}: title bottom {tb[-1][3]} too close to divider "
                     f"{rec['divider_y']}")

        # speaker bands
        sb = rec["speaker_boxes"]
        sy1 = sb[0][1] - 4
        sy2 = sb[-1][3] + 4
        sband = bands(px, sb[0][0], sy1, sb[0][2], sy2)
        c["checks"]["speaker_bands"] = len(sband)
        if len(sband) != rec["speaker_line_count"]:
            F.append(f"{cid}: speaker bands {len(sband)} != {rec['speaker_line_count']}")

        # header: brand, index, date single band
        bb = rec["brand_box"]
        brand = bands(px, bb[0], bb[1] - 4, bb[0] + 560, bb[3] + 4)
        if len(brand) != 1:
            F.append(f"{cid}: brand bands {len(brand)} != 1")
        ibb = rec["index_box"]
        idx = bands(px, ibb[0] + 2, ibb[1] + 2, ibb[2] - 2, ibb[3] - 2, thr=90)
        if len(idx) != 1:
            F.append(f"{cid}: index text bands {len(idx)} != 1 (wrapped?)")
        db = rec["date_box"]
        date = bands(px, db[0], db[1] - 4, W - M, db[3] + 6)
        c["checks"]["date_bands"] = [[b[0], b[1], b[2], b[3]] for b in date]
        if len(date) != 1:
            F.append(f"{cid}: date bands {len(date)} != 1 (wrapped -> glyph lost?)")
        elif date[0][3] - date[0][2] + 1 < 110:
            F.append(f"{cid}: date ink width {date[0][3]-date[0][2]+1} < 110 "
                     f"(truncated?)")

        # pills: time / badge / annotation text inside inner window, single line
        pill_items = [("time_box", rec["time_box"]),
                      ("badge_box", rec["badge_box"])]
        if rec.get("annotation_box"):
            pill_items.append(("annotation_box", rec["annotation_box"]))
        for key, box in pill_items:
            x1, y1, x2, y2 = box
            # inner window must clear the r=22 border arc (reaches x1+7 at
            # dy<=15) and the rounded-corner background sliver: x+-12, y+-6
            wx1, wy1, wx2, wy2 = x1 + 12, y1 + 6, x2 - 12, y2 - 6
            if key == "annotation_box":
                # solid bright fill: text is DARK on light -> invert detection
                inner = dark_bands(px, wx1, wy1, wx2, wy2)
            else:
                inner = bands(px, wx1, wy1, wx2, wy2, thr=85)
            if len(inner) != 1:
                F.append(f"{cid}: {key} text bands {len(inner)} != 1 "
                         f"(wrapped/second line or arc leak)")
            else:
                tx1, tx2 = inner[0][2], inner[0][3]
                lp, rp = tx1 - x1, x2 - tx2
                if lp < 6 or rp < 6:
                    F.append(f"{cid}: {key} text {tx1}-{tx2} vs pill {x1}-{x2} "
                             f"(padding l={lp} r={rp} < 6)")
                elif abs(lp - rp) > 10:
                    F.append(f"{cid}: {key} text not centered: l={lp} r={rp}")

        c["checks"]["title_font_size"] = rec["title_font_size"]
        c["checks"]["speaker_font_size"] = rec["speaker_font_size"]
        c["checks"]["status_encoding"] = rec["status_encoding"]
        c["checks"]["annotation"] = rec["annotation_text"]
        c["warnings"] = rec["warnings"]
        report["cards"].append(c)

    out = BASE / f"measured-cards-{VER}.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2),
                   encoding="utf-8")
    print(f"cards={len(report['cards'])} failures={len(F)}")
    for f in F:
        print("  FAIL:", f)
    print("->", out)


if __name__ == "__main__":
    main()
