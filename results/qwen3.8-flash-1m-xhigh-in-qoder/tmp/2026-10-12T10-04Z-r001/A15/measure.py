"""A15 anchor measurement.

Runs the same detector over the reference PNG and over a reconstruction PNG, so every
anchor is a measured number on both sides rather than an eyeballed estimate. The reference
is only read for measurement - it is never cropped into an asset or embedded.

Run: python tmp/<run_id>/A15/measure.py --image tasks/A15-reference-reconstruction/inputs/reference.png --tag reference
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
TMP_DIR = ROOT / "tmp" / RUN / "A15"


def rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.int16)


def near(arr, col, tol=28):
    return np.abs(arr - np.asarray(col, dtype=np.int16)).max(axis=2) <= tol


def bbox(mask):
    ys, xs = np.nonzero(mask)
    if not len(xs):
        return None
    return [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]


def components(mask, min_px=400):
    """Split axis-aligned UI blocks by column runs, then take each run's row extent."""
    colhits = mask.sum(axis=0)
    runs, st = [], None
    for x, v in enumerate(colhits):
        if v > 3 and st is None:
            st = x
        elif v <= 3 and st is not None:
            runs.append((st, x))
            st = None
    if st is not None:
        runs.append((st, len(colhits)))
    out = []
    for x0, x1 in runs:
        sub = mask[:, x0:x1]
        rows = np.nonzero(sub.sum(axis=1) > (x1 - x0) * 0.5)[0]
        if not len(rows):
            continue
        b = [int(x0), int(rows.min()), int(x1), int(rows.max()) + 1]
        if (b[2] - b[0]) * (b[3] - b[1]) >= min_px:
            out.append(b)
    return sorted(out, key=lambda b: (b[1], b[0]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    ap.add_argument("--tag", required=True)
    a = ap.parse_args()
    im = Image.open(ROOT / a.image).convert("RGB")
    im.load()
    arr = np.asarray(im, dtype=np.int16)
    H, W = arr.shape[:2]
    PAPER, CARD, SIDE = rgb("#EEF1F7"), rgb("#FFFFFF"), rgb("#16233C")
    BLUE, NAVY = rgb("#2F5BEA"), rgb("#12203A")

    paper = near(arr, PAPER, 14)
    card = near(arr, CARD, 8)
    side = near(arr, SIDE, 26)

    # 1 sidebar right edge: last column that is mostly sidebar-coloured
    colfrac = side.mean(axis=0)
    cand = np.nonzero(colfrac > 0.5)[0]
    sidebar_right = int(cand.max()) + 1 if len(cand) else None

    # 2 nav selected pill: a lighter navy block sitting on the darker sidebar
    pill = np.zeros((H, W), bool)
    pill[100:240, :(sidebar_right or 220) - 6] = True
    # the selected row is a navy that is both lighter and bluer than the sidebar body
    lighter = (arr[..., 2] - arr[..., 0] > 26) & (arr[..., 2] > 74)         & (arr[..., 2] < 126) & pill
    # keep only rows that are solidly filled: a pill body, not anti-aliased text pixels
    solid = lighter.sum(axis=1) > 120
    lighter &= solid[:, None]
    nav_pill = bbox(lighter)

    # 3 main title visible glyph box (dark ink in the header band)
    ink = (arr.max(axis=2) < 110)
    title_zone = np.zeros((H, W), bool)
    title_zone[20:80, (sidebar_right or 220) + 20:] = True
    title_box = bbox(ink & title_zone)

    # 4..6 KPI cards: white blocks in the KPI row band
    row = np.zeros((H, W), bool)
    row[130:290, :] = True
    kpis = components(card & row, 3000)

    # 7 chart card, 10 activity card: white blocks in the middle band
    row2 = np.zeros((H, W), bool)
    row2[305:600, :] = True
    mid = components(card & row2, 5000)
    chart_card = mid[0] if mid else None
    activity_card = mid[1] if len(mid) > 1 else None

    # 8 chart zero line left end: leftmost blue-ish gridline row near the baseline
    grid = near(arr, rgb("#DCE3EE"), 34) & row2
    grid[:, :280] = False
    grid[:, 990:] = False
    grid[:380, :] = False
    grid[560:, :] = False
    rows_with = np.nonzero(grid.sum(axis=1) > 300)[0]
    zero_y = int(rows_with.max()) if len(rows_with) else None
    # require a contiguous 60px run so anti-aliased tick-label edges are not the line
    row = grid[zero_y, :] if zero_y is not None else np.zeros(W, bool)
    zero_left = None
    run = 0
    for x in range(W):
        run = run + 1 if row[x] else 0
        if run >= 60:
            zero_left = x - 59
            break

    # 9 last bar top centre
    bmask = near(arr, BLUE, 46) & row2
    bmask[:, :280] = False
    bars = sorted(components(bmask, 1500), key=lambda b: b[0])
    last_bar = bars[-1] if bars else None
    bar_top_centre = [ (last_bar[0] + last_bar[2]) // 2, last_bar[1] ] if last_bar else None

    # 11 table card
    row3 = np.zeros((H, W), bool)
    row3[610:860, :] = True
    tbl = components(card & row3, 8000)
    table_card = tbl[0] if tbl else None

    # 12 last status label box: the green "Done" pill in the table
    zone3 = np.zeros((H, W), bool)
    if table_card:
        zone3[table_card[1]:table_card[3], table_card[0]:table_card[2]] = True
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    done = (g > r + 8) & (g > b + 4) & (g > 205) & zone3
    done_box = bbox(done)

    # extra anchors: button, footer ink, y-axis label
    btn = components(near(arr, NAVY, 40) & (np.ones((H, W), bool)), 2000)
    btn_box = None
    zone = np.zeros((H, W), bool)
    zone[30:100, 1100:] = True
    bb = bbox(near(arr, rgb("#2B54D8"), 60) & zone)

    out = {
        "tag": a.tag, "image": a.image, "canvas": [W, H],
        "anchors": {
            "sidebar_right_edge_x": sidebar_right,
            "nav_selected_pill_rect": nav_pill,
            # the spec anchors the title on its visible glyph box top-left corner;
            # the right/bottom edges are reported separately as font-metric differences
            "main_title_glyph_topleft": [title_box[0], title_box[1]] if title_box else None,
            "main_title_glyph_box_full": title_box,
            "kpi_card_1_rect": kpis[0] if len(kpis) > 0 else None,
            "kpi_card_2_rect": kpis[1] if len(kpis) > 1 else None,
            "kpi_card_3_rect": kpis[2] if len(kpis) > 2 else None,
            "chart_card_rect": chart_card,
            "chart_zero_line_left_point": [zero_left, zero_y] if zero_y is not None else None,
            "last_bar_top_centre": bar_top_centre,
            "activity_card_rect": activity_card,
            "table_card_rect": table_card,
            "last_status_label_rect": done_box,
            "export_button_rect": bb,
            "bar_count": len(bars),
            "kpi_card_count": len(kpis),
        },
    }
    (TMP_DIR / f"measure-{a.tag}.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
