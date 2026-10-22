# -*- coding: utf-8 -*-
"""A13 delivery checks (run on the actual service PNGs in tmp drafts).

1. pure-black check  - decode RGBA (PNG stores unpremultiplied values); every
   pixel with alpha>0 must have R=G=B=0; count violations, record alpha range
2. geometry identity - the colour and black icons must share one geometry:
   compare the full alpha channels pixel by pixel
3. clear space / bounds - alpha bounding boxes, clear margins

Writes tmp/run-20261011-01/A13/checks.json (real numbers, no invented thresholds).
"""
import hashlib
import json
import pathlib

import PIL
from PIL import Image

ROOT = pathlib.Path(".")
RUN = "run-20261011-01"
TASK = "A13"
D = ROOT / "tmp" / RUN / TASK / "drafts"
OUT = ROOT / "tmp" / RUN / TASK / "checks.json"

color = Image.open(D / "symbol-color-v1.png").convert("RGBA")
black = Image.open(D / "symbol-black-v1.png").convert("RGBA")
assert color.size == (512, 512) and black.size == (512, 512), (color.size, black.size)

# ---- 1. pure black check --------------------------------------------------
bp = black.load()
violations = 0
alpha_vals = set()
first_viol = None
for y in range(black.size[1]):
    for x in range(black.size[0]):
        r, g, b, a = bp[x, y]
        if a > 0:
            alpha_vals.add(a)
            if r != 0 or g != 0 or b != 0:
                violations += 1
                if first_viol is None:
                    first_viol = (x, y, r, g, b, a)

# ---- 2. geometry identity (alpha channels) --------------------------------
cp, bp2 = color.load(), black.load()
alpha_mismatch = 0
for y in range(512):
    for x in range(512):
        if cp[x, y][3] != bp2[x, y][3]:
            alpha_mismatch += 1

# ---- 3. bounds and clear space --------------------------------------------
def alpha_bbox(img):
    p = img.load()
    xs, ys = [], []
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            if p[x, y][3] > 0:
                xs.append(x)
                ys.append(y)
    return [min(xs), min(ys), max(xs), max(ys)]

bbox_c = alpha_bbox(color)
bbox_b = alpha_bbox(black)

mass_c = sum(1 for y in range(512) for x in range(512) if cp[x, y][3] > 0)
mass_b = sum(1 for y in range(512) for x in range(512) if bp2[x, y][3] > 0)

res = {
    "decoder": {
        "tool": "Pillow " + PIL.__version__,
        "note": "Image.open().convert('RGBA'); PNG RGBA is stored unpremultiplied, "
                "channel values are checked exactly as decoded",
    },
    "black_check": {
        "file": "symbol-black.png (service bytes: drafts/symbol-black-v1.png)",
        "md5": hashlib.md5((D / "symbol-black-v1.png").read_bytes()).hexdigest(),
        "alpha_range_pixels_with_alpha_gt_0": [min(alpha_vals), max(alpha_vals)],
        "alpha_values_present": sorted(alpha_vals),
        "pixels_with_alpha_gt_0": mass_b,
        "violations_rgb_not_zero_with_alpha_gt_0": violations,
        "first_violation": first_viol,
        "passed": violations == 0,
    },
    "geometry_identity": {
        "alpha_channel_mismatch_pixels": alpha_mismatch,
        "color_ink_pixels": mass_c,
        "black_ink_pixels": mass_b,
        "identical_geometry": alpha_mismatch == 0 and mass_c == mass_b,
        "note": "antialiased alpha edge pixels included in comparison; "
                "colour differs by design, geometry (alpha) must be pixel-identical",
    },
    "bounds": {
        "color_alpha_bbox": bbox_c,
        "black_alpha_bbox": bbox_b,
        "clear_margin_px": {
            "left": bbox_c[0], "top": bbox_c[1],
            "right": 512 - 1 - bbox_c[2], "bottom": 512 - 1 - bbox_c[3],
        },
        "ring_outer_diameter_px": 400,
        "ring_border_px": 72,
        "expected_ring_margin_px": 56,
    },
}

OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(res, ensure_ascii=False, indent=2))
