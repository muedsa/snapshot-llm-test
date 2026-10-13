"""Numeric readout for B03 probe rounds 2 and 3.

Answers "did the attribute change pixels?" per probe, so technique-notes.md can cite
confirmed behaviour, silent no-ops and hard errors instead of guesses.

Run: python tmp/<run_id>/B03/probe_check2.py   (from the suite task root)
"""
from __future__ import annotations

import json
import math
import os
from pathlib import Path

from PIL import Image

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
TMP = ROOT / "tmp" / "2026-10-12T10-04Z-r001" / "B03"
EV: dict = {}


def load(name):
    p = TMP / f"{name}.png"
    return Image.open(p).convert("RGB") if p.exists() else None


def px(im, x, y):
    return im.getpixel((int(x), int(y)))


def line(im, y, x0, x1, step=1):
    return [px(im, x, y) for x in range(int(x0), int(x1), step)]


def transitions(runs, tol=40):
    n = 0
    for a, b in zip(runs, runs[1:]):
        if sum(abs(i - j) for i, j in zip(a, b)) > tol:
            n += 1
    return n


def lum(c):
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def ink_cols(im, y0, y1, x0, x1, thresh=170):
    return [x for x in range(x0, x1)
            if any(lum(px(im, x, y)) < thresh for y in range(y0, y1))]


def extent(im, y0, y1, x0=0, x1=None, thresh=170):
    cols = ink_cols(im, y0, y1, x0, x1 or im.width, thresh)
    return None if not cols else (cols[0], cols[-1], cols[-1] - cols[0] + 1)


def dark_centroid(im, box, thresh=90):
    x0, y0, x1, y1 = box
    xs = ys = n = 0
    for y in range(y0, y1):
        for x in range(x0, x1):
            if lum(px(im, x, y)) < thresh:
                xs += x
                ys += y
                n += 1
    return None if not n else (round(xs / n, 1), round(ys / n, 1), n)


# ---------------------------------------------------------------- round 2
if (im := load("probe2-blur2")):
    m = json.loads((TMP / "probe2-measure.json").read_text(encoding="utf-8"))["blur2"]
    sx, sy, ex = m["sharp_row"]
    gx, gy, gex = m["glass_row"]
    EV["blur2"] = {
        "sharp_transitions": transitions(line(im, sy, sx, ex)),
        "glass_transitions": transitions(line(im, gy, gx, gex)),
        "note": "BackdropFilter over an already-painted checkerboard, sigma 6",
    }
if (im := load("probe2-tile2")):
    m = json.loads((TMP / "probe2-measure.json").read_text(encoding="utf-8"))["tile2"]
    EV["tile2"] = {mode: transitions(line(im, r[1], r[0], r[2]))
                   for mode, r in zip(m["modes"], m["rows"])}
if (im := load("probe2-gradrot")):
    m = json.loads((TMP / "probe2-measure.json").read_text(encoding="utf-8"))["gradrot"]
    EV["gradrot"] = {
        "plain_tl": list(px(im, *m["plain_tl"])), "plain_br": list(px(im, *m["plain_br"])),
        "rot_tl": list(px(im, *m["rot_tl"])), "rot_br": list(px(im, *m["rot_br"])),
        "radial_centre": list(px(im, *m["radial_centre"])),
        "focal_dark": dark_centroid(im, m["focal_dark_centroid_box"]),
        "plain_dark": dark_centroid(im, (20, 200, 180, 360)),
    }
if (im := load("probe2-shadow2")):
    EV["shadow2"] = {}
    for i, e in enumerate(("ELEVATION_0", "ELEVATION_1", "ELEVATION_3", "ELEVATION_6",
                           "ELEVATION_9", "ELEVATION_12")):
        y = 20 + i * 76 + 62
        EV["shadow2"][e] = {"sheet": list(px(im, 12, y)), "under_card": list(px(im, 126, y))}
if (im := load("probe2-shadowcustom")):
    EV["shadowcustom"] = {"sheet": list(px(im, 20, 160)),
                          "under_card": list(px(im, 140, 112))}
if (im := load("probe2-filter2")):
    EV["filter2"] = {
        "tint_row_transitions": transitions(line(im, 55, 30, 300)),
        "tint_samples": [list(px(im, x, 55)) for x in (40, 90, 140, 200, 260)],
        "blur_row_transitions": transitions(line(im, 230, 30, 350)),
        "plain_row_transitions": transitions(line(im, 55, 30, 300)),
        "opacity_035": list(px(im, 95, 310)),
        "backdrop_on_flat": list(px(im, 375, 310)),
        "sheet": list(px(im, 470, 370)),
    }
if (im := load("probe2-clip2")):
    EV["clip2"] = {
        "oval_corner": list(px(im, 22, 22)), "oval_centre": list(px(im, 140, 116)),
        "rrect_corner": list(px(im, 22, 242)), "rrect_centre": list(px(im, 120, 300)),
        "path_outside": list(px(im, 302, 310)), "path_inside": list(px(im, 400, 200)),
    }
if (im := load("probe2-transform2")):
    def bbox(colour, box, tol=26):
        x0, y0, x1, y1 = box
        pts = [(x, y) for y in range(y0, y1) for x in range(x0, x1)
               if sum(abs(a - b) for a, b in zip(px(im, x, y), colour)) < tol]
        return None if not pts else (min(p[0] for p in pts), min(p[1] for p in pts),
                                     max(p[0] for p in pts), max(p[1] for p in pts), len(pts))
    EV["transform2"] = {
        "x_shear": bbox((231, 111, 81), (20, 20, 200, 110)),
        "y_shear": bbox((42, 157, 143), (20, 110, 200, 200)),
        "scale_140_060": bbox((69, 123, 157), (200, 10, 400, 100)),
        "mirror_text_ink": extent(im, 110, 170, 200, 380),
        "origin_top_left_square": bbox((17, 17, 17), (20, 200, 200, 320)),
        "align_top_left_square": bbox((230, 57, 70), (200, 200, 340, 320)),
    }
if (im := load("probe2-textab")):
    m = json.loads((TMP / "probe2-measure.json").read_text(encoding="utf-8"))["textab"]
    lh, rows, x0 = m["lh"], m["rows"], m["x0"]
    ext = {}
    for i, name in enumerate(rows):
        y0 = i * lh + 12
        ext[name] = extent(im, y0, y0 + lh - 6, x0, x0 + 520)
    EV["textab"] = ext
    red = sum(1 for y in range(9 * lh + 12, 9 * lh + 60) for x in range(16, 300)
              if px(im, x, y)[0] - px(im, x, y)[1] > 40)
    blue = sum(1 for y in range(10 * lh + 12, 10 * lh + 60) for x in range(16, 300)
               if px(im, x, y)[2] - px(im, x, y)[0] > 40)
    EV["textab"]["shadow_red_pixels"] = red
    EV["textab"]["shadow2_blue_pixels"] = blue
    bgteal = sum(1 for y in range(17 * lh + 8, 17 * lh + 46) for x in range(16, 300)
                 if abs(px(im, x, y)[0] - 42) < 45 and abs(px(im, x, y)[1] - 157) < 45)
    EV["textab"]["background_box_pixels"] = bgteal
    # line pitch of the height=1.0 vs height=2.6 rows
    def rows_with_ink(im, y0, y1, x0=16, x1=260, thresh=170):
        band = []
        for y in range(y0, y1):
            if any(lum(px(im, x, y)) < thresh for x in range(x0, x1, 2)):
                band.append(y)
        groups = []
        for y in band:
            if groups and y == groups[-1][-1] + 1:
                groups[-1].append(y)
            else:
                groups.append([y])
        return [(g[0], g[-1]) for g in groups if len(g) > 2]
    EV["textab"]["hi_1_0_bands"] = rows_with_ink(im, 11 * lh + 8, 11 * lh + 46)
    EV["textab"]["hi_2_6_bands"] = rows_with_ink(im, 12 * lh + 8, 12 * lh + 46)

# ---------------------------------------------------------------- round 3
for style in ("SOLID", "DOTTED", "DASHED", "DOUBLE", "WAVY"):
    im = load(f"probe3-deco-{style}") or load(f"deco-{style}")
    if im is None:
        im = load(f"probe3-deco-{style}".replace("probe3-", ""))
    if im is None:
        continue
    # the decoration line sits under the glyph baseline: count ink rows below 40
    rows = [y for y in range(40, 68)
            if any(px(im, x, y)[0] - px(im, x, y)[1] > 60 for x in range(16, 340))]
    runs = 0
    prev = False
    for y in range(40, 68):
        on = any(px(im, x, y)[0] - px(im, x, y)[1] > 60 for x in range(16, 340))
        if on and not prev:
            runs += 1
        prev = on
    EV.setdefault("deco", {})[style] = {"red_rows": len(rows), "red_run_groups": runs}
for i, spec in enumerate(("30 30", "(30,30)", "30,30")):
    p = TMP / f"origin{i}.png"
    EV.setdefault("origin", {})[spec] = "200 " + str(Image.open(p).size) if p.exists(
    ) else "400 PARSE_ERROR"
if (im := load("misc")) or load("probe3-misc"):
    im = im or load("probe3-misc")
    EV["misc"] = {
        "ellipsis_ink": extent(im, 12, 44, 0, 320),
        "ellipsis_has_dots": any(px(im, x, 26)[0] < 90 for x in range(150, 220)),
        "align_end_ink": extent(im, 56, 88, 0, 340),
        "clip_arc_inside": list(px(im, 100, 220)),
        "clip_arc_outside": list(px(im, 30, 165)),
        "hole_inside_reversed_subpath": list(px(im, 340, 220)),
        "hole_frame": list(px(im, 260, 165)),
        "custom_shadow_under": list(px(im, 560, 215)),
        "custom_shadow_sheet": list(px(im, 30, 460)),
        "gradrot_linear_diag": [list(px(im, 30, 330)), list(px(im, 190, 370))],
        "gradrot_radial": [list(px(im, 310, 350)), list(px(im, 230, 322))],
        "foreground_gradient": [list(px(im, 440, 330)), list(px(im, 590, 370))],
        "widgetspan_baseline_red": sum(1 for y in range(415, 455) for x in range(150, 220)
                                        if px(im, x, y)[0] > 180 and px(im, x, y)[1] < 110),
    }

(TMP / "probe-evidence2.json").write_text(json.dumps(EV, indent=2), encoding="utf-8")
print(json.dumps(EV, indent=2, ensure_ascii=False))
