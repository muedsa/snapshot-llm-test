#!/usr/bin/env python3
"""A10 final-PNG sampler + paired-control/geometry measurements.

Usage: python tmp/<run_id>/A10/scripts/sample_a10.py <suite_root> <run_id>

Reads outputs/<run_id>/A10/compositing-lab.png (the raw service response),
samples the panel-1/2 overlap points at local (180,100), measures panel-1/2
rectangle edges, verifies the 3-4 shared stripe field is byte-identical
outside the card, measures in-card blur vs outside sharpness, and checks the
5/6 circular clip. Fills composite-audit.json (samples.actual_*, measurements)
and writes crops/panel1..6.png (2x) from the FINAL png.
"""
import json
import math
import pathlib
import sys

from PIL import Image

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
run_id = sys.argv[2] if len(sys.argv) > 2 else "run-20261011-01"
out_dir = root / "outputs" / run_id / "A10"
tmp_dir = root / "tmp" / run_id / "A10"
crops = tmp_dir / "crops"
crops.mkdir(parents=True, exist_ok=True)

png = out_dir / "compositing-lab.png"
im = Image.open(png).convert("RGBA")
px = im.load()
W, H = im.size
assert (W, H) == (1440, 1100), im.size

ORIGINS = [[144, 188], [560, 188], [976, 188], [144, 584], [560, 584], [976, 584]]
CARD = [40, 40, 240, 160]              # card local xywh inside panels 3/4
OVAL = (160, 120, 100)                 # panel-6 circle centre + radius
STRIPE_PITCH, STRIPE_W = 24, 12


def is_white(c):
    return c[0] > 250 and c[1] > 250 and c[2] > 250


def blue_dom(c):
    return c[2] > c[0] + 10


def red_dom(c):
    return c[0] > c[2] + 10 and c[0] > c[1] + 10


results = {}

# ---- samples: panel 1 and 2 at local (180, 100) ---------------------------------
samples_out = []
for panel, theory_round in ((1, [127, 63, 191]), (2, [128, 128, 255])):
    ox, oy = ORIGINS[panel - 1]
    cx, cy = ox + 180, oy + 100
    c = px[cx, cy]
    samples_out.append({"panel": panel, "canvas_index_xy": [cx, cy],
                        "actual_rgb": [c[0], c[1], c[2]], "actual_alpha": c[3],
                        "theory_rounded_rgb": theory_round,
                        "abs_error": [abs(c[i] - theory_round[i]) for i in range(3)]})
    print(f"sample p{panel} @({cx},{cy}) = {c} theory {theory_round} "
          f"err {[abs(c[i]-theory_round[i]) for i in range(3)]}")

# ---- panel 1/2 rectangle edge measurement ---------------------------------------
ox, oy = ORIGINS[0]
edge = {}

# red top row: local y=60 (inside red y40..160, above blue top y80)
y = oy + 60
xs = [x for x in range(ox, ox + 320) if not is_white(px[x, y])]
edge["p1_row_localY60_first_last_nonwhite"] = [xs[0] - ox, xs[-1] + 1 - ox]
edge["p1_row_localY60_expected"] = [40, 200]

# blue lower row: local y=180 (inside blue y80..200, red ended at 160)
y = oy + 180
xs = [x for x in range(ox, ox + 320) if not is_white(px[x, y])]
edge["p1_row_localY180_first_last_nonwhite"] = [xs[0] - ox, xs[-1] + 1 - ox]
edge["p1_row_localY180_expected"] = [120, 280]

# column local x=160: white -> red (40) -> blend (80) -> blue continues (160..200)
x = ox + 160
col = [px[x, yy] for yy in range(oy, oy + 240)]
first_nw = next(i for i, c in enumerate(col) if not is_white(c))
first_blue = next(i for i, c in enumerate(col) if blue_dom(c))
last_nw = 239 - next(i for i, c in enumerate(reversed(col)) if not is_white(c))
edge["p1_col_localX160_first_nonwhite_redtop"] = [first_nw, 40]
edge["p1_col_localX160_first_bluedom_bluetop"] = [first_blue, 80]
edge["p1_col_localX160_last_nonwhite_bluebottom"] = [last_nw + 1, 200]

# panel 2 same geometry (opaque children inside the group)
ox2, oy2 = ORIGINS[1]
x = ox2 + 160
col = [px[x, yy] for yy in range(oy2, oy2 + 240)]
first_nw2 = next(i for i, c in enumerate(col) if not is_white(c))
first_blue2 = next(i for i, c in enumerate(col) if blue_dom(c))
last_nw2 = 239 - next(i for i, c in enumerate(reversed(col)) if not is_white(c))
edge["p2_col_localX160_edges"] = [first_nw2, first_blue2, last_nw2 + 1]
edge["p2_col_localX160_expected"] = [40, 80, 200]
print("edges:", json.dumps(edge))

# ---- panels 3/4: shared stripe field identical OUTSIDE the card -----------------
o3, o4 = ORIGINS[2], ORIGINS[3]
diff_max = 0
diff_count = 0
diff_where = None
for ly in range(240):                 # scan the full 320x240 area
    for lx in range(320):
        # skip the card box (with 2px margin for the rounded-corner AA) and
        # the 1px outline which sits OUTSIDE the area already
        if CARD[0] - 2 <= lx < CARD[0] + CARD[2] + 2 and CARD[1] - 2 <= ly < CARD[1] + CARD[3] + 2:
            continue
        c3 = px[o3[0] + lx, o3[1] + ly]
        c4 = px[o4[0] + lx, o4[1] + ly]
        d = max(abs(c3[i] - c4[i]) for i in range(3))
        if d > diff_max:
            diff_max, diff_where = d, (lx, ly, c3, c4)
        if d > 0:
            diff_count += 1
results["paired_3_4_outside_card"] = {
    "compared_area": "full 320x240 panel area minus the card box (local 38..282 x 38..202, "
                     "2px margin around the rounded card) and the 1px outline outside the area",
    "pixels_compared": 320 * 240 - (244 * 164),
    "max_abs_channel_diff": diff_max,
    "differing_pixels": diff_count,
    "first_difference": diff_where,
    "meaning": "stripes/card surroundings outside the card are pixel-identical between 3 and 4; "
               "the only difference between the pair is which layer the blur touches",
    "passed": diff_max == 0,
}
print("paired 3/4 outside-card max diff:", diff_max, "diff px:", diff_count)

# ---- stripe geometry + blur-vs-sharp contrast (panel 3) --------------------------
ox3, oy3 = ORIGINS[2]
runs = []
row = [px[ox3 + lx, oy3 + 10][0] for lx in range(320)]     # local y=10, above the card
state = row[0] < 128
start = 0
for i in range(1, 320):
    s = row[i] < 128
    if s != state:
        runs.append((start, i - start, state))
        start, state = i, s
runs.append((start, 320 - start, state))
dark_runs = [(s, w) for (s, w, st) in runs if st]
widths = [w for _, w in dark_runs]
starts = [s for s, _ in dark_runs]
pitches = [starts[i + 1] - starts[i] for i in range(len(starts) - 1)]
results["stripe_field"] = {
    "panel": 3, "scan_row_local_y": 10,
    "dark_run_starts": starts[:6], "dark_run_widths": widths[:6],
    "pitches": pitches[:5],
    "expected": "dark 12px every 24px, phase local x=0 (mod 24)",
    "passed": all(w == STRIPE_W for w in widths) and all(p == STRIPE_PITCH for p in pitches),
}

# contrast and edge sharpness inside the card (blurred) vs outside (sharp)
def contrast(lx0, lx1, ly):
    vals = [sum(px[ox3 + lx, oy3 + ly][:3]) / 3 for lx in range(lx0, lx1)]
    return round(max(vals) - min(vals), 1)


def max_hgrad(lx0, lx1, ly):
    g, prev = 0.0, None
    for lx in range(lx0, lx1):
        v = sum(px[ox3 + lx, oy3 + ly][:3]) / 3
        if prev is not None:
            g = max(g, abs(v - prev))
        prev = v
    return round(g, 1)


grads_out = [max_hgrad(60, 260, ly) for ly in (210, 220, 230)]
grads_in = [max_hgrad(60, 260, ly) for ly in (100, 104, 108)]
results["blur_vs_sharp"] = {
    "panel": 3,
    "outside_card_rows_local_y": [210, 220, 230],
    "outside_card_max_hgrad_gray_per_px": grads_out,
    "inside_card_rows_local_y": [100, 104, 108],
    "inside_card_rows_note": "chosen to contain only the blurred stripe field (between the "
                             "text band ending at y=90 and the foreground shapes starting at y=112)",
    "inside_card_max_hgrad_gray_per_px": grads_in,
    "outside_minmax_gray_row_y220": contrast(60, 260, 220),
    "inside_minmax_gray_row_y120": contrast(60, 260, 120),
    "expected": "stripe edges inside the card are soft (small per-pixel gradient) while the "
                "same field outside the card keeps single-pixel black/white steps",
    "passed": min(grads_out) > 10 * max(grads_in),
}
print("sharpness:", results["blur_vs_sharp"])

# text crispness proxy: sharpest vertical gradient of the text glyph edges, panel 3 vs 4
def max_grad(lx0, lx1, ly0, ly1, ox_, oy_):
    g = 0
    for ly in range(ly0, ly1):
        prev = None
        for lx in range(lx0, lx1):
            v = sum(px[ox_ + lx, oy_ + ly][:3]) / 3
            if prev is not None:
                g = max(g, abs(v - prev))
            prev = v
    return round(g, 1)


g3 = max_grad(64, 230, 66, 92, ox3, oy3)      # "SHARP / BLUR" glyph band (inside card), panel 3
g4 = max_grad(64, 230, 66, 92, o4[0], o4[1])  # same band, panel 4
results["text_sharpness"] = {
    "band_local_xywh": [64, 66, 166, 26],
    "panel3_max_horizontal_gray_gradient": g3,
    "panel4_max_horizontal_gray_gradient": g4,
    "expected": "panel 3 (backdrop-only blur) keeps crisp glyph edges (large gradient); "
                "panel 4 (subtree blur) has soft edges (small gradient)",
    "passed": g3 > 2 * g4,
}
print("text grad p3/p4:", g3, g4)

# ---- panels 5/6: circular clip verification --------------------------------------
ox5, oy5 = ORIGINS[4]
ox6, oy6 = ORIGINS[5]
c5 = px[ox5 + 40, oy5 + 100]        # local (40,100): inside scene, 121.7px from circle centre
c6 = px[ox6 + 40, oy6 + 100]        # same point in panel 6 -> outside r=100 -> clipped to white
cc6 = px[ox6 + 160, oy6 + 120]      # circle centre in panel 6 -> content visible
results["clip_5_6"] = {
    "probe_local_xy_outside_circle": [40, 100],
    "distance_from_centre_px": round(math.hypot(40 - 160, 100 - 120), 2),
    "panel5_rgb": list(c5[:3]), "panel5_meaning": "unclipped multiply+blur content (tinted)",
    "panel6_rgb": list(c6[:3]), "panel6_meaning": "outside the r=100 circle -> white panel",
    "panel6_centre_rgb": list(cc6[:3]), "panel6_centre_meaning": "inside the circle -> tinted content",
    "expected": "panel5 non-white, panel6 white at the same local point, panel6 centre non-white",
    "passed": (not is_white(c5)) and is_white(c6) and (not is_white(cc6)),
}
print("clip:", results["clip_5_6"])

# circle boundary along the centre row of panel 6
y = oy6 + 120
xs = [lx for lx in range(320) if not is_white(px[ox6 + lx, y])]
results["clip_5_6"]["panel6_centre_row_span_local"] = [xs[0], xs[-1] + 1]
results["clip_5_6"]["panel6_centre_row_span_expected"] = [60, 260]

# ---- fill composite-audit.json ----------------------------------------------------
audit_p = out_dir / "composite-audit.json"
audit = json.loads(audit_p.read_text(encoding="utf-8"))
theory = [s["theory_rounded_rgb"] for s in audit["samples"]]
for i, so in enumerate(samples_out):
    s = audit["samples"][i]
    s["actual_rgb"] = so["actual_rgb"]
    s["actual_alpha"] = so["actual_alpha"]
    err = so["abs_error"]
    s["abs_error_per_channel"] = err
    s["within_tolerance"] = max(err) <= s["tolerance_per_channel"]
audit["measurements"] = results
audit["measurement_method"] = {
    "tool": "PIL pixel access on the decoded final service PNG (compositing-lab.png, "
            "the untouched bytes returned by open-snapshot)",
    "script": {"path_base": "suite_root", "path": f"tmp/{run_id}/A10/scripts/sample_a10.py"},
    "crops": {"path_base": "suite_root",
              "paths": [f"tmp/{run_id}/A10/crops/panel{i}.png" for i in range(1, 7)],
              "note": "2x nearest-neighbour crops of the FINAL png around each panel"},
}
audit_p.write_text(json.dumps(audit, ensure_ascii=False, indent=1), encoding="utf-8")

# ---- final panel crops (from the FINAL png) ---------------------------------------
for i, (ox, oy) in enumerate(ORIGINS, start=1):
    box = (ox - 6, oy - 6, ox + 326, oy + 250)
    im.crop(box).resize(((box[2] - box[0]) * 2, (box[3] - box[1]) * 2), Image.NEAREST).save(
        crops / f"panel{i}.png")
    print("crop", crops / f"panel{i}.png")

ok = all(s["within_tolerance"] for s in audit["samples"])
print("samples within tolerance:", ok)
