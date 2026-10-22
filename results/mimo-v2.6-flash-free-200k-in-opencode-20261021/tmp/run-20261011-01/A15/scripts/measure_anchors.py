# -*- coding: utf-8 -*-
"""A15 shared geometry-anchor measurer.

Identical detectors applied to reference.png and reconstructed.png so the
audit compares like with like. Covers the 12 task-required objects plus
extra anchors for canvas quadrants, chart and table detail.

Usage: python measure_anchors.py <image> <out.json>
"""
import json
import pathlib
import sys

from PIL import Image

BG = (243, 246, 251)


def lum(p):
    return (p[0] * 299 + p[1] * 587 + p[2] * 114) // 1000


def near(p, c, tol):
    return abs(p[0] - c[0]) <= tol and abs(p[1] - c[1]) <= tol \
        and abs(p[2] - c[2]) <= tol


def is_bg(p, tol=4):
    return near(p, BG, tol)


def bbox_color(px, win, c, tol):
    x1, y1, x2, y2 = win
    xs, ys = [], []
    for y in range(y1, y2 + 1):
        for x in range(x1, x2 + 1):
            if near(px[x, y], c, tol):
                xs.append(x)
                ys.append(y)
    if not xs:
        return None
    return [min(xs), min(ys), max(xs), max(ys)]


def _merge_gaps(runs, max_gap=2):
    """Merge runs separated by <=max_gap px: near-BG anti-aliased glyph
    edges can split a card row scan by 1-2 px in BOTH images alike."""
    if not runs:
        return runs
    out = [list(runs[0])]
    for r in runs[1:]:
        if r[0] - out[-1][1] - 1 <= max_gap:
            out[-1][1] = r[1]
        else:
            out.append(list(r))
    return out


def notbg_runs_row(px, y, xa, xb):
    runs, s = [], None
    for x in range(xa, xb + 1):
        if not is_bg(px[x, y]):
            if s is None:
                s = x
        elif s is not None:
            runs.append([s, x - 1])
            s = None
    if s is not None:
        runs.append([s, xb])
    return _merge_gaps(runs)


def notbg_run_col(px, x, ya, yb):
    runs, s = [], None
    for y in range(ya, yb + 1):
        if not is_bg(px[x, y]):
            if s is None:
                s = y
        elif s is not None:
            runs.append([s, y - 1])
            s = None
    if s is not None:
        runs.append([s, yb])
    return runs


def dark_bbox(px, win, thr=160):
    x1, y1, x2, y2 = win
    xs, ys = [], []
    for y in range(y1, y2 + 1):
        for x in range(x1, x2 + 1):
            if lum(px[x, y]) < thr:
                xs.append(x)
                ys.append(y)
    if not xs:
        return None
    return [min(xs), min(ys), max(xs), max(ys)]


def gridline_left(px, y):
    runs, s = [], None
    for x in range(270, 1000):
        ok = 200 <= lum(px[x, y]) <= 244
        if ok and s is None:
            s = x
        elif not ok and s is not None:
            runs.append((s, x - 1))
            s = None
    if s is not None:
        runs.append((s, 999))
    best = max(runs, key=lambda r: r[1] - r[0]) if runs else None
    return best[0] if best else None


def blue_bbox(px, win):
    x1, y1, x2, y2 = win
    xs, ys = [], []
    for y in range(y1, y2 + 1):
        for x in range(x1, x2 + 1):
            p = px[x, y]
            if p[2] - p[0] > 100 and p[2] > 180:
                xs.append(x)
                ys.append(y)
    if not xs:
        return None
    return [min(xs), min(ys), max(xs), max(ys)]


def main():
    img = Image.open(pathlib.Path(sys.argv[1])).convert("RGB")
    px = img.load()
    R = {}

    # 1) sidebar right boundary (x) on row 450
    for x in range(200, 260):
        if is_bg(px[x, 450]):
            R["sidebar_right_x"] = x
            break

    # 2) nav selected pill outer frame
    R["nav_selected_frame"] = bbox_color(
        px, (10, 105, 215, 175), (41, 68, 103), 8)

    # 3) main title visible glyph box top-left -> point
    tb = dark_bbox(px, (255, 32, 620, 76))
    R["title_glyph_box"] = tb
    R["title_glyph_tl"] = [tb[0], tb[1]] if tb else None

    # 4-6) KPI card outer frames via row 210 not-bg runs, vertical via col
    runs = notbg_runs_row(px, 210, 240, 1420)
    runs = [r for r in runs if r[1] - r[0] > 100]
    names = ["kpi1_box", "kpi2_box", "kpi3_box"]
    for name, r in zip(names, runs):
        cx = (r[0] + r[1]) // 2
        vruns = [vr for vr in notbg_run_col(px, cx, 125, 300)
                 if vr[1] - vr[0] > 100]
        if vruns:
            R[name] = [r[0], vruns[0][0], r[1], vruns[0][1]]

    # 7) chart card: col 600 vertical, row 320 horizontal
    vr = [r for r in notbg_run_col(px, 600, 300, 610) if r[1] - r[0] > 100]
    hr = [r for r in notbg_runs_row(px, 320, 250, 1010) if r[1] - r[0] > 100]
    if vr and hr:
        R["chart_card_box"] = [hr[0][0], vr[0][0], hr[0][1], vr[0][1]]

    # 8) chart zero line left endpoint (gridline color, row 549)
    gz = gridline_left(px, 549)
    R["zero_line_left"] = [gz, 549] if gz else None

    # 9) last bar (Sep) top center
    bb = blue_bbox(px, (850, 400, 930, 560))
    R["last_bar_box"] = bb
    R["last_bar_top_center"] = [round((bb[0] + bb[1] * 0 + bb[2]) / 2, 1),
                                bb[1]] if bb else None

    # 9b) first bar (Apr) top center
    fb = blue_bbox(px, (340, 400, 420, 560))
    R["first_bar_box"] = fb
    R["first_bar_top_center"] = [round((fb[0] + fb[2]) / 2, 1), fb[1]] \
        if fb else None

    # 10) activity card: col 1200 vertical, row 320 second run
    vr = [r for r in notbg_run_col(px, 1200, 300, 610) if r[1] - r[0] > 100]
    hr = [r for r in notbg_runs_row(px, 320, 1020, 1439) if r[1] - r[0] > 100]
    if vr and hr:
        R["activity_card_box"] = [hr[0][0], vr[0][0], hr[0][1], vr[0][1]]

    # 11) table card: col 1350 (merge runs across bg band), row 650
    trs = [r for r in notbg_run_col(px, 1350, 610, 850) if r[1] - r[0] > 30]
    hr = [r for r in notbg_runs_row(px, 650, 250, 1439) if r[1] - r[0] > 100]
    if trs and hr:
        R["table_card_box"] = [hr[0][0], trs[0][0], hr[0][1], trs[-1][1]]

    # 12) last row status pill (Done tint)
    R["pill_done_box"] = bbox_color(
        px, (1015, 790, 1190, 835), (220, 245, 236), 6)
    # extra pills
    R["pill_progress_box"] = bbox_color(
        px, (1015, 720, 1190, 762), (231, 239, 255), 6)
    R["pill_review_box"] = bbox_color(
        px, (1015, 755, 1190, 797), (255, 243, 215), 6)

    # 13) export button (TR)
    R["export_button_box"] = bbox_color(
        px, (1150, 25, 1430, 100), (36, 92, 228), 10)

    # 14) workspace card (BL)
    R["workspace_card_box"] = bbox_color(
        px, (10, 740, 215, 885), (35, 57, 84), 6)

    # 15) footer glyph top-left (BL)
    fb2 = dark_bbox(px, (255, 860, 545, 888))
    R["footer_glyph_box"] = fb2
    R["footer_glyph_tl"] = [fb2[0], fb2[1]] if fb2 else None

    # 16) subtitle glyph top-left (TL)
    sb = dark_bbox(px, (255, 80, 545, 112))
    R["subtitle_glyph_box"] = sb
    R["subtitle_glyph_tl"] = [sb[0], sb[1]] if sb else None

    # 17) table header band (bg-colored, inside white card)
    R["table_band_box"] = bbox_color(px, (270, 680, 1390, 730), BG, 3)

    # 18) separators: rows with separator color at col 1000
    sep = [y for y in range(750, 805)
           if near(px[1000, y], (235, 239, 245), 4)]
    R["separator_rows"] = sep

    # 19) logo mark box (green)
    R["logo_box"] = bbox_color(px, (20, 20, 70, 75), (100, 219, 182), 14)

    out = pathlib.Path(sys.argv[2])
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(R, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    print(f"anchors measured -> {out.as_posix()}")


if __name__ == "__main__":
    main()
