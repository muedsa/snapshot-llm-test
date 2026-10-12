"""A15 · measure a 1440x900 dashboard render the same way for reference and rebuild.

Observation only: colours are sampled and boundaries found by scanning for colour
changes. Nothing from the reference is copied into the output.
"""
from __future__ import annotations

import json
import sys

from PIL import Image


def near(c, ref, tol=12):
    return all(abs(a - b) <= tol for a, b in zip(c[:3], ref))


def hexs(c):
    return "#%02X%02X%02X" % c[:3]


def col_runs(px, y0, y1, x0, x1, pred, frac=0.6, minw=30):
    """Columns where `pred` holds for at least `frac` of the rows in [y0,y1)."""
    need = int((y1 - y0) * frac)
    hits = []
    for x in range(x0, x1):
        n = sum(1 for y in range(y0, y1) if pred(px[x, y]))
        hits.append(n >= need)
    runs, start = [], None
    for i, h in enumerate(hits):
        if h and start is None:
            start = i
        elif not h and start is not None:
            if i - start >= minw:
                runs.append([x0 + start, x0 + i - 1])
            start = None
    if start is not None and len(hits) - start >= minw:
        runs.append([x0 + start, x0 + len(hits) - 1])
    return runs


def row_runs(px, x0, x1, y0, y1, pred, frac=0.6, minh=16):
    need = int((x1 - x0) * frac)
    hits = []
    for y in range(y0, y1):
        n = sum(1 for x in range(x0, x1) if pred(px[x, y]))
        hits.append(n >= need)
    runs, start = [], None
    for i, h in enumerate(hits):
        if h and start is None:
            start = i
        elif not h and start is not None:
            if i - start >= minh:
                runs.append([y0 + start, y0 + i - 1])
            start = None
    if start is not None and len(hits) - start >= minh:
        runs.append([y0 + start, y0 + len(hits) - 1])
    return runs


_SIZE = (10 ** 6, 10 ** 6)


def bbox(px, x0, y0, x1, y1, pred, size=None):
    left = top = right = bottom = None
    W, H = size or _SIZE
    x0, y0 = max(0, int(x0)), max(0, int(y0))
    x1, y1 = min(int(x1), W), min(int(y1), H)
    for y in range(y0, y1):
        for x in range(x0, x1):
            if pred(px[x, y]):
                if left is None or x < left:
                    left = x
                if right is None or x > right:
                    right = x
                if top is None:
                    top = y
                if bottom is None or y > bottom:
                    bottom = y
    return None if left is None else [left, top, right, bottom]


def measure(path: str) -> dict:
    global _SIZE
    im = Image.open(path).convert("RGB")
    W, H = im.size
    _SIZE = (W, H)
    px = im.load()
    is_white = lambda c: near(c, (255, 255, 255), 8)
    is_light = lambda c: near(c, (243, 246, 251), 10)
    # secondary UI text tops out around #63748F (max 143); 205 keeps muted greys in
    # while still excluding the #E2E8F1 card border
    is_ink = lambda c: max(c[:3]) < 205
    out = {"file": path, "size": [W, H], "samples": {}}

    for name, (x, y) in {
        "sidebar_mid": (10, 450), "sidebar_top": (200, 8), "sidebar_bottom": (10, 890),
        "page_bg": (1420, 300), "page_bg2": (700, 120), "kpi_card": (300, 260),
        "chart_card": (300, 580), "activity_card": (1050, 560), "table_card": (300, 830),
        "bar": (380, 520), "export_btn": (1300, 66), "logo": (43, 46),
        "nav_selected": (100, 140), "nav_idle": (100, 200),
        "workspace_panel": (100, 810),
    }.items():
        out["samples"][name] = hexs(px[x, y])

    # ---- sidebar -------------------------------------------------------------
    x = 0
    while x < W and not is_light(px[x, 400]):
        x += 1
    out["sidebar_right_edge_x"] = x - 1
    out["sidebar_width"] = x

    # ---- content column ------------------------------------------------------
    cx0 = out["sidebar_width"]
    # KPI row: white columns across y 150..265 (clear of text baselines is impossible,
    # so require 60% white which text never breaks)
    out["kpi_cards_x"] = col_runs(px, 150, 265, cx0, W, is_white, 0.55, 150)
    out["kpi_card1_y"] = row_runs(px, out["kpi_cards_x"][0][0] + 10,
                                  out["kpi_cards_x"][0][1] - 10, 100, 330, is_white, 0.8, 20) \
        if out["kpi_cards_x"] else None
    # second row: scan the thin white strip between the card top edge and the titles
    out["row2_cards_x"] = col_runs(px, 312, 334, cx0, W, is_white, 0.8, 150)
    if len(out["row2_cards_x"]) >= 2:
        c0, c1 = out["row2_cards_x"][0]
        out["chart_card_y"] = row_runs(px, c0 + 10, c1 - 10, 295, 620, is_white, 0.75, 30)
        a0, a1 = out["row2_cards_x"][-1]
        out["activity_card_y"] = row_runs(px, a0 + 10, a1 - 10, 295, 620, is_white, 0.75, 30)
    out["table_card_x"] = col_runs(px, 630, 690, cx0, W, is_white, 0.5, 200)
    if out["table_card_x"]:
        t0, t1 = out["table_card_x"][0]
        out["table_card_y"] = row_runs(px, t0 + 10, t1 - 10, 600, 890, is_white, 0.7, 30)

    # ---- chart internals -----------------------------------------------------
    is_bar = lambda c: c[2] > 150 and c[2] - c[0] > 60 and c[1] < 150
    if out["row2_cards_x"]:
        c0, c1 = out["row2_cards_x"][0]
        cy = out.get("chart_card_y") or [[311, 594]]
        y0, y1 = min(r[0] for r in cy), max(r[1] for r in cy)
        out["chart_bars"] = []
        band_y = bbox(px, c0, y0, c1, y1, is_bar)
        out["chart_bar_band"] = band_y
        if band_y:
            ymid = band_y[3] - 8   # just above the zero line: every bar exists here
            inbar, start = False, None
            for x in range(c0, c1):
                b = is_bar(px[x, ymid])
                if b and not inbar:
                    inbar, start = True, x
                elif not b and inbar:
                    inbar = False
                    out["chart_bars"].append([start, x - 1])
            if inbar:
                out["chart_bars"].append([start, c1 - 1])
            out["chart_bars"] = [b for b in out["chart_bars"] if b[1] - b[0] > 12]
            for b in out["chart_bars"]:
                top = bbox(px, b[0], y0, b[1] + 1, y1, is_bar)
                b.append(top[1] if top else None)
        # gridlines: sampled left of the first bar and below the card title/unit label
        gx = c0 + 74
        gl = []
        for y in range(y0 + 85, y1 - 8):
            c = px[gx, y]
            if 195 < c[0] < 245 and abs(c[0] - c[1]) < 10 and abs(c[1] - c[2]) < 12:
                if not gl or y - gl[-1] > 2:
                    gl.append(y)
        out["chart_gridlines_y"] = gl
        out["chart_card_box"] = [c0, y0, c1, y1]
        out["chart_title_ink"] = bbox(px, c0 + 20, y0 + 10, c0 + 500, y0 + 70, is_ink)
        out["chart_period_ink"] = bbox(px, c1 - 320, y0 + 10, c1 - 20, y0 + 70, is_ink)
        out["chart_axis_labels"] = bbox(px, c0 + 20, y0 + 60, c0 + 110, y1 - 20, is_ink)
        out["chart_month_labels"] = bbox(px, c0 + 20, (band_y[3] + 4) if band_y else y1 - 60,
                                         c1 - 10, y1 - 4, is_ink)

    # ---- activity card -------------------------------------------------------
    if len(out["row2_cards_x"]) >= 2:
        a0, a1 = out["row2_cards_x"][-1]
        ay = out.get("activity_card_y") or [[311, 594]]
        ay0, ay1 = min(r[0] for r in ay), max(r[1] for r in ay)
        out["activity_title_ink"] = bbox(px, a0 + 20, ay0 + 10, a1 - 20, ay0 + 70, is_ink)
        # the three status dots sit in a narrow column left of the item titles
        dots = bbox(px, a0 + 16, ay0 + 60, a0 + 40, ay1 - 10,
                    lambda c: max(c[:3]) - min(c[:3]) > 40)
        out["activity_dots"] = dots
        if dots:
            runs = []
            for y in range(dots[1], dots[3] + 1):
                on = max(px[dots[0] + 5, y][:3]) - min(px[dots[0] + 5, y][:3]) > 40
                if on:
                    if not runs or y - runs[-1][1] > 1:
                        runs.append([y, y])
                    else:
                        runs[-1][1] = y
            out["activity_dot_rows_y"] = runs

    # ---- table ---------------------------------------------------------------
    if out.get("table_card_x") and out.get("table_card_y"):
        t0 = out["table_card_x"][0][0]
        t1 = out["table_card_x"][0][1]
        ty0 = min(r[0] for r in out["table_card_y"])
        ty1 = max(r[1] for r in out["table_card_y"])
        out["table_card_box"] = [t0, ty0, t1, ty1]
        out["table_title_ink"] = bbox(px, t0 + 20, ty0 + 8, t0 + 500, ty0 + 70, is_ink)
        hdr = bbox(px, t0 + 10, ty0 + 60, t1 - 10, ty0 + 110,
                   lambda c: not near(c, (255, 255, 255), 6))
        out["table_header_band"] = hdr
        pills = bbox(px, t0 + 600, ty0 + 60, t1 - 200, ty1,
                     lambda c: max(c[:3]) - min(c[:3]) > 25 and min(c[:3]) > 180)
        out["table_status_pills"] = pills
        if pills:
            col = (pills[0] + pills[2]) // 2
            pruns = []
            for y in range(pills[1], pills[3] + 1):
                c = px[col, y]
                on = max(c[:3]) - min(c[:3]) > 25 and min(c[:3]) > 180
                if on:
                    if not pruns or y - pruns[-1][1] > 1:
                        pruns.append([y, y])
                    else:
                        pruns[-1][1] = y
            out["table_pill_rows_y"] = pruns

    # ---- header --------------------------------------------------------------
    out["title_ink"] = bbox(px, cx0 + 20, 25, cx0 + 760, 82, is_ink)
    out["subtitle_ink"] = bbox(px, cx0 + 20, 84, cx0 + 760, 115, is_ink)
    out["export_button"] = bbox(px, cx0 + 700, 20, W - 8, 110,
                                lambda c: c[2] > 180 and c[0] < 90 and c[1] < 150)

    # ---- sidebar internals ---------------------------------------------------
    out["logo_mark"] = bbox(px, 8, 8, 90, 80,
                            lambda c: c[1] > 120 and c[1] - c[0] > 35)
    out["brand_text_ink"] = bbox(px, 62, 15, 205, 80, lambda c: min(c[:3]) > 190)
    out["nav_selected"] = bbox(px, 12, 100, out["sidebar_width"] - 12, 180,
                               lambda c: 35 < c[0] < 85 and 50 < c[1] < 105
                               and 65 < c[2] < 135)
    out["nav_idle_dot"] = bbox(px, 12, 180, out["sidebar_width"] - 12, 360,
                               lambda c: 60 < c[0] < 130 and 80 < c[1] < 150
                               and 110 < c[2] < 190)
    out["workspace_panel"] = bbox(px, 5, 700, out["sidebar_width"] - 5, 895,
                                  lambda c: 30 < c[0] < 75 and 42 < c[1] < 90
                                  and 58 < c[2] < 120)
    out["footer_ink"] = bbox(px, cx0 + 20, 850, cx0 + 760, 898,
                             lambda c: max(c[:3]) < 200)
    return out


if __name__ == "__main__":
    res = measure(sys.argv[1])
    print(json.dumps(res, ensure_ascii=False, indent=2))
    if len(sys.argv) > 2:
        with open(sys.argv[2], "w", encoding="utf-8") as fh:
            json.dump(res, fh, ensure_ascii=False, indent=2)
