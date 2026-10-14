"""Pixel evidence for the B03 capability probes.

Each probe answers one question: did the service actually apply the documented capability,
or silently ignore it? Sampling beats eyeballing a 420px thumbnail, so every probe gets a
numeric test here; the PNGs are still opened by eye afterwards.

Run: python tmp/<run_id>/B03/probe_check.py   (from the suite task root)
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from PIL import Image

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
TMP = ROOT / "tmp" / "2026-10-12T10-04Z-r001" / "B03"


def img(tag):
    return Image.open(TMP / f"probe-{tag}.png").convert("RGB")


def px(im, x, y):
    return im.getpixel((x, y))


def row_slice(im, y, x0, x1):
    return [px(im, x, y) for x in range(x0, x1)]


def distinct(runs, tol=24):
    """Number of colour transitions along a sampled line."""
    n = 0
    for a, b in zip(runs, runs[1:]):
        if sum(abs(i - j) for i, j in zip(a, b)) > tol:
            n += 1
    return n + 1


def variance(rgb_rows):
    vals = [v for c in rgb_rows for v in c]
    m = sum(vals) / len(vals)
    return sum((v - m) ** 2 for v in vals) / len(vals)


def main() -> int:
    out = {}

    # --- BackdropFilter: blurred glass must crush the stripe edges under it
    im = img("blur")
    crisp = row_slice(im, 95, 0, 88)          # left of the glass: raw stripes
    glass = row_slice(im, 95, 150, 330)       # inside the glass
    out["blur"] = {
        "crisp_transitions": distinct(crisp),
        "glass_transitions": distinct(glass),
        "glass_variance": round(variance(glass), 1),
        "crisp_variance": round(variance(crisp), 1),
        "verdict": "blurred" if variance(glass) < variance(crisp) * 0.6 else "not blurred",
    }

    # --- SWEEP gradient: colour must rotate with angle
    im = img("sweep")
    cx, cy, r = 110, 110, 70
    ang = {}
    import math
    for label, a in (("0deg", 0), ("90deg", 90), ("180deg", 180), ("270deg", 270)):
        x = int(cx + r * math.sin(math.radians(a)))
        y = int(cy - r * math.cos(math.radians(a)))
        ang[label] = px(im, x, y)
    out["sweep"] = {
        "samples": {k: list(v) for k, v in ang.items()},
        "distinct": len({tuple(v) for v in ang.values()}),
        "verdict": "rotates" if len({tuple(v) for v in ang.values()}) >= 3 else "flat",
    }

    # --- ColorFiltered / foregroundGradient / backgroundBlendMode
    im = img("blend")
    out["blend"] = {
        "base_top": list(px(im, 110, 30)),
        "base_bottom": list(px(im, 110, 190)),
        "colorfiltered": list(px(im, 310, 110)),
        "foreground_top": list(px(im, 110, 230)),
        "foreground_bottom": list(px(im, 110, 390)),
    }

    # --- text effects: letterSpacing widens the run; shadow adds coloured pixels
    im = img("textfx")
    def text_extent(y0, y1, x0=10, x1=440, dark=(40, 40, 40)):
        cols = [x for x in range(x0, x1)
                if any(sum(px(im, x, y)[k] for k in range(3)) < sum(dark) * 3 * 0.75
                       for y in range(y0, y1))]
        return (min(cols), max(cols)) if cols else None
    t1 = text_extent(20, 52)
    t2 = text_extent(60, 92)
    shadow_px = [px(im, x, y) for y in range(100, 150) for x in range(20, 240)]
    reddish = sum(1 for c in shadow_px if c[0] > 170 and c[1] < 120)
    teal = sum(1 for c in [px(im, x, y) for y in range(200, 236) for x in range(150, 300)]
               if abs(c[0] - 42) < 40 and abs(c[1] - 157) < 40 and abs(c[2] - 143) < 40)
    out["textfx"] = {
        "tnum_row_extent": t1,
        "smcp_row_extent": t2,
        "shadow_reddish_pixels": reddish,
        "widgetspan_teal_pixels": teal,
    }

    # --- Transform: rotation of a solid card must move its corners
    im = img("transform")
    def bbox(colour, tol=30):
        pts = [(x, y) for y in range(im.height) for x in range(im.width)
               if sum(abs(a - b) for a, b in zip(px(im, x, y), colour)) < tol]
        return (min(p[0] for p in pts), min(p[1] for p in pts),
                max(p[0] for p in pts), max(p[1] for p in pts), len(pts)) if pts else None
    out["transform"] = {
        "skew_card_bbox": bbox((231, 111, 81)),
        "rotated_text_ink": bbox((17, 17, 17), tol=90),
    }

    # --- gradientTileMode: repetition multiplies the number of bands
    im = img("tile")
    out["tile"] = {
        "repeat_bands": distinct(row_slice(im, 110, 22, 198)),
        "mirror_bands": distinct(row_slice(im, 110, 222, 398)),
        "radial_repeat_centre": list(px(im, 110, 310)),
        "radial_repeat_offset": list(px(im, 60, 260)),
    }

    # --- ClipPath wrapping a Stack: children outside the path must be gone.
    # The probe canvas has a white background, so "clipped away" reads as white.
    im = img("clipstack")
    out["clipstack"] = {
        "inside_path_top_left": list(px(im, 22, 22)),
        "inside_path_second_band": list(px(im, 160, 60)),
        "outside_path_below_curve": list(px(im, 250, 210)),
        "nested_rrect_corner": list(px(im, 30, 250)),
        "nested_inside": list(px(im, 160, 300)),
        "plain_stack_overlap_winner": list(px(im, 400, 40)),
    }

    # --- boxShadow: shadow pixels darker than the sheet under the cards
    im = img("shadow")
    base = px(im, 150, 8)
    below = px(im, 150, 118)
    below24 = px(im, 150, 306)
    out["shadow"] = {
        "sheet": list(base),
        "under_elevation_2": list(below),
        "under_elevation_24": list(below24),
        "darker": (sum(below) < sum(base)) and (sum(below24) < sum(below)),
    }

    (TMP / "probe-evidence.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
