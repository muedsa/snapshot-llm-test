"""A05 pixel self-check: canvas, 32px safe ring, inter-panel gutters, row bands.

Usage: python tmp/<run_id>/A05/check_geom_a05.py <png>
Observation only - it never edits the image or the DSL.
"""
import json
import sys
from collections import Counter
from pathlib import Path

from PIL import Image

BG = (0x0B, 0x12, 0x20)
INK_MIN = 90                      # channel-sum threshold above BG noise
W, H, M = 1440, 1000, 32
CARD_W = (W - 2 * M - 2 * 14) / 3.0
PANELS = {f"card{i}": (M + i * (CARD_W + 14), 100, M + (i + 1) * CARD_W + i * 14, 196)
          for i in range(3)}
PANELS.update({"chart1": (32, 204, 1408, 374), "chart2": (32, 380, 1408, 550),
               "chart3": (32, 556, 1408, 726), "table": (32, 790, 1408, 968)})
# the header text line and the legend/caveat rows live in the same columns as the
# panels below them, so a halo crossing those rows would report their ink as outside
FREE_BANDS = [(0, 96), (727, 790)]
GUTTERS = {"header/cards": (0, 95, W, 100), "cards/chart1": (0, 197, W, 204),
           "chart1/chart2": (0, 375, W, 380), "chart2/chart3": (0, 551, W, 556),
           "chart3/legend": (0, 727, W, 734), "legend/caveat": (0, 759, W, 762),
           "caveat/table": (0, 787, W, 790), "below": (0, 969, W, H)}


def load(path):
    im = Image.open(path).convert("RGBA")
    return im, im.load(), im.size


def bright(px, x, y):
    r, g, b, a = px[x, y]
    return a > 0 and (abs(r - BG[0]) + abs(g - BG[1]) + abs(b - BG[2])) > INK_MIN


def ring(px):
    bad = []
    for x in range(W):
        for y in list(range(0, M)) + list(range(H - M, H)):
            if bright(px, x, y):
                bad.append((x, y))
    for y in range(H):
        for x in list(range(0, M)) + list(range(W - M, W)):
            if bright(px, x, y):
                bad.append((x, y))
    return Counter(b[1] // 50 for b in bad), len(bad)


def rows_with_ink(px, y0, y1, x0=0, x1=W):
    out = []
    for y in range(y0, y1):
        if any(bright(px, x, y) for x in range(x0, x1, 2)):
            out.append(y)
    return out


def bands(rows):
    if not rows:
        return []
    out, s, p = [], rows[0], rows[0]
    for y in rows[1:]:
        if y != p + 1:
            out.append((s, p))
            s = y
        p = y
    out.append((s, p))
    return out


def main():
    path = Path(sys.argv[1])
    im, px, size = load(path)
    rep = {"image": path.as_posix(), "size": list(size), "mode": im.mode}
    hist, nring = ring(px)
    rep["safe_ring_violations"] = nring
    rep["safe_ring_rows"] = dict(sorted(hist.items()))
    rep["gutter_ink"] = {}
    for name, (x0, y0, x1, y1) in GUTTERS.items():
        rep["gutter_ink"][name] = sum(1 for y in range(y0, y1)
                                      for x in range(x0, x1, 2) if bright(px, x, y))
    # outside-ink per panel: any bright pixel in the panel's own gutter columns
    rep["panel_outside"] = {}
    for name, (x0, y0, x1, y1) in PANELS.items():
        out = 0
        for y in range(y0 - 6, y1 + 6):
            if y < 0 or y >= H or any(a <= y < b for a, b in FREE_BANDS):
                continue
            for x in range(max(0, int(x0) - 6), min(W, int(x1) + 7)):
                if x < x0 - 1 or x > x1 + 1 or y < y0 - 1 or y > y1 + 1:
                    if bright(px, x, y):
                        out += 1
        rep["panel_outside"][name] = out
    rep["legend_bands"] = bands(rows_with_ink(px, 728, 760))
    rep["caveat_bands"] = bands(rows_with_ink(px, 758, 790))
    rep["table_row_bands"] = bands(rows_with_ink(px, 790, 968, 40, 1400))
    # colour census inside the three plot boxes: expected series colours present?
    plots = {"chart1": (110, 250, 1386, 334), "chart2": (110, 426, 1386, 510),
             "chart3": (110, 602, 1386, 686)}
    want = {"chart1": "#FBBF24", "chart2": "#38BDF8", "chart3": "#A78BFA"}
    rep["series_pixels"] = {}
    for name, (x0, y0, x1, y1) in plots.items():
        c = want[name][1:]
        tgt = (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16))
        n = sum(1 for y in range(y0, y1) for x in range(x0, x1, 2)
                if all(abs(px[x, y][i] - tgt[i]) <= 12 for i in range(3))
                and px[x, y][3] > 0)
        rep["series_pixels"][name] = n
    print(json.dumps(rep, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
