"""A10: measure the delivered PNG against plan_a10.json.

Nothing in here carries a coordinate of its own: every sample point, scan window and
expected value is read from the plan that generate_a10.py drew from, so a caption on the
board and a number in composite-audit.json cannot disagree.

Checks
  geometry      each 320x240 white area is where the plan says it is (+-2px), found as the
                rows/columns whose brightness fraction crosses the plan's threshold, so the
                slot captions above/below an area cannot be mistaken for its edge
  samples       ①⑤⑥ point colours vs source-over / MULTIPLY arithmetic
  ripple        ③ vs ④: peak-to-peak of one stripe period, outside and inside the card
  card edge     ③ near-black rim position; ④ 10-90% rise of the blurred card edge
  text          B-channel gradient content of the card caption band, ③ (sharp) vs ④ (blurred)
  halo          ⑤: how far the blur reaches past the filter box's top edge
  clip arc      ⑥ radial profile across the ClipOval boundary: hard or feathered?

A "measured" value is always the raw pixel from the service response; expected values are
kept next to it with the tolerance, so a reviewer sees the size of the agreement and the
windows that had to be re-fitted after the first probe (probe_a10.py).
"""
import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A10"
TEMP = ROOT / "tmp" / RID / TASK
OUT = ROOT / "outputs" / RID / TASK
SRC = Path(os.environ.get("A10_SRC", TEMP / "preview" / "v06.png"))
if not SRC.is_absolute():
    SRC = (ROOT / SRC).resolve()

plan = json.loads((TEMP / "plan_a10.json").read_text(encoding="utf-8"))
MEAS = plan["measurements"]
im = Image.open(SRC).convert("RGB")
px = im.load()
W, H = im.size
assert [W, H] == plan["canvas"], (W, H)
CELL = {c["number"]: c for c in plan["cells"]}
CH = {"R": 0, "G": 1, "B": 2}


def at(x, y):
    return px[int(round(x)), int(round(y))]


def lum(p):
    return 0.2126 * p[0] + 0.7152 * p[1] + 0.0722 * p[2]


def area_xy(cell, lx, ly):
    ax, ay = CELL[cell]["area_origin"]
    return ax + lx, ay + ly


def rise_10_90(xs, ys):
    """10%-90% transition width of a profile, linear interpolation between samples"""
    lo, hi = min(ys), max(ys)
    if hi - lo < 6:
        return None, None, None
    a, b = lo + 0.1 * (hi - lo), lo + 0.9 * (hi - lo)

    def cross(level):
        for i in range(len(ys) - 1):
            y0, y1 = ys[i], ys[i + 1]
            if (y0 - level) * (y1 - level) <= 0 and y0 != y1:
                return xs[i] + (level - y0) * (xs[i + 1] - xs[i]) / (y1 - y0)
        return None

    x10, x90 = cross(a), cross(b)
    return (abs(x90 - x10) if None not in (x10, x90) else None), x10, x90


# ------------------------------------------------------------------ area geometry
M = MEAS["area_geometry_method"]
geo = []
for g in MEAS["area_geometry"]:
    cell = g["cell"]
    ax, ay, aw, ah = g["expected_bbox"]
    m = M["search_margin_px"]

    def row_frac(y):
        v = [lum(at(x, y)) > M["lum_bright"] for x in range(ax, ax + aw)]
        return sum(v) / len(v)

    def col_frac(x):
        v = [lum(at(x, y)) > M["lum_bright"] for y in range(ay, ay + ah)]
        return sum(v) / len(v)

    xs = [x for x in range(ax - m, ax + aw + m) if col_frac(x) >= M["col_fraction_min"]]
    ys = [y for y in range(ay - m, ay + ah + m) if row_frac(y) >= M["row_fraction_min"]]
    bbox = [min(xs), min(ys), max(xs) - min(xs) + 1, max(ys) - min(ys) + 1]
    dev = [bbox[i] - (ax, ay, aw, ah)[i] for i in range(4)]
    geo.append({"cell": cell, "expected": g["expected_bbox"], "measured": bbox,
                "deviation": dev, "tolerance_px": M["tolerance_px"],
                "pass": all(abs(d) <= M["tolerance_px"] for d in dev)})

# ------------------------------------------------------------------ point samples
smp = []
for s in MEAS["samples"]:
    x, y = s["canvas"]
    got = list(at(x, y))
    d = [got[i] - s["expected"][i] for i in range(3)]
    smp.append({"cell": s["cell"], "label": s["label"], "canvas": [x, y],
                "expected": s["expected"], "measured": got, "delta_levels": d,
                "tolerance": s["tolerance"], "claim": s["claim"],
                "pass": max(abs(v) for v in d) <= s["tolerance"]})

# ------------------------------------------------------------------ ripple amplitude
rip = []
ci = CH[MEAS["ripple"]["channel"]]
for side, spec in (("outside", MEAS["ripple"]["outside"]),
                   ("inside", MEAS["ripple"]["inside"])):
    for cell in spec["cells"]:
        x0, x1 = spec["x_range"]
        vals = [at(*area_xy(cell, x, spec["row_area_y"]))[ci] for x in range(x0, x1 + 1)]
        p2p = max(vals) - min(vals)
        exp = spec["expected_p2p"][cell]
        tol = max(12, 0.18 * p2p) if side == "outside" else max(8, 0.35 * exp)
        rip.append({"cell": cell, "side": side, "channel": MEAS["ripple"]["channel"],
                    "row_area_y": spec["row_area_y"], "x_range": [x0, x1],
                    "measured_p2p": p2p, "expected_p2p": exp,
                    "tolerance": round(tol, 1), "pass": abs(p2p - exp) <= tol})

# ------------------------------------------------------------------ ③ sharp rim position
spec = MEAS["card_edge"]["cell_3_rim"]
a3 = CELL["③"]["area_origin"]
dark = [x for x in range(spec["x_range"][0], spec["x_range"][1] + 1)
        if lum(at(a3[0] + x, a3[1] + spec["row_area_y"])) < spec["lum_max_dark"]]
rim = {"cell": "③", "spec": spec, "dark_columns_area_x": dark,
       "expected_columns": spec["expected_columns"],
       "centroid": round(sum(dark) / len(dark), 2) if dark else None,
       "tolerance_px": spec["tolerance_px"]}
rim["pass"] = bool(dark) and dark == spec["expected_columns"]

# ------------------------------------------------------------------ ④ blurred card edge
spec = MEAS["card_edge"]["cell_4_profile"]
c4 = CELL["④"]["area_origin"]
ci4 = CH[spec["channel"]]
ys = list(range(spec["y_range"][0], spec["y_range"][1] + 1))
prof = [sum(at(c4[0] + x, c4[1] + y)[ci4]
            for x in range(spec["col_range_area_x"][0], spec["col_range_area_x"][1] + 1))
        / (spec["col_range_area_x"][1] - spec["col_range_area_x"][0] + 1) for y in ys]
lo_plateau = sum(prof[:10]) / 10
hi_plateau = sum(prof[-10:]) / 10
w, x10, x90 = rise_10_90(ys, prof)
mid = rise_10_90(ys, prof)
edge4 = {"cell": "④", "profiled_along": "y across the card top edge",
         "mean_over_area_x": spec["col_range_area_x"],
         "plateau_outside_mean_R": round(lo_plateau, 1),
         "expected_outside": spec["plateau_outside_mean_R"],
         "plateau_inside_mean_R": round(hi_plateau, 1),
         "expected_inside": spec["plateau_inside_mean_R"],
         "rise_10_90_px": round(w, 2) if w else None,
         "predicted_rise_10_90_px": spec["expected_rise_10_90_px"],
         "implied_sigma_px": round(w / 2.5631, 2) if w else None,
         "crossing_10_area_y": round(x10, 2) if x10 else None,
         "crossing_90_area_y": round(x90, 2) if x90 else None,
         "crossing_50_area_y": round(mid[1] + 0.5 * (mid[2] - mid[1]), 2) if mid[0] else None,
         "expected_edge_area_y": spec["edge_area_y"], "rise_tol_px": spec["rise_tol_px"]}
edge4["pass"] = (w is not None
                 and abs(w - spec["expected_rise_10_90_px"]) <= spec["rise_tol_px"]
                 and abs(lo_plateau - spec["plateau_outside_mean_R"]) <= 6
                 and abs(hi_plateau - spec["plateau_inside_mean_R"]) <= 6
                 and abs(edge4["crossing_50_area_y"] - spec["edge_area_y"]) <= 2.0)

# ------------------------------------------------------------------ text sharpness ③ vs ④
spec = MEAS["text_band_gradient"]
bx0, by0, bx1, by1 = spec["area_rect"]
ciT = CH[spec["channel"]]
grad, sharp = {}, {}
for cell in ("③", "④"):
    ax0, ay0 = CELL[cell]["area_origin"]
    d = [abs(at(ax0 + x + 1, ay0 + y)[ciT] - at(ax0 + x, ay0 + y)[ciT])
         for y in range(int(by0), int(by1)) for x in range(int(bx0), int(bx1))]
    grad[cell] = round(sum(d) / len(d), 3)
    sharp[cell] = sum(1 for v in d if v >= 60)
ratio = grad["③"] / grad["④"] if grad["④"] else None
grad_res = {"band_area_rect": spec["area_rect"], "channel": spec["channel"],
            "mean_abs_dB_per_px": grad, "pixels_with_abs_dB_ge_60": sharp,
            "ratio_3_over_4": round(ratio, 2) if ratio else None,
            "rule": spec["rule"], "pass": bool(ratio and ratio >= 2.5
                                               and sharp["④"] == 0 and sharp["③"] > 0)}

# ------------------------------------------------------------------ ⑤ blur halo past the box
spec = MEAS["filter_halo_profile"]
cih = CH[spec["channel"]]
top = spec["box_top_canvas_y"]
halo_pts = {y: at(spec["canvas_x"], y)[cih] for y in range(*[spec["y_range"][0],
                                                             spec["y_range"][1] + 1])}
prof_y = sorted(halo_pts)
prof_v = [halo_pts[y] for y in prof_y]
w5, h10, h90 = rise_10_90(prof_y, prof_v)
mid5 = None
lo, hi = min(prof_v), max(prof_v)
lvl = (lo + hi) / 2
for i in range(len(prof_v) - 1):
    if (prof_v[i] - lvl) * (prof_v[i + 1] - lvl) <= 0 and prof_v[i] != prof_v[i + 1]:
        mid5 = prof_y[i] + (lvl - prof_v[i]) * (prof_y[i + 1] - prof_y[i]) / (
            prof_v[i + 1] - prof_v[i])
        break
A = spec["assertions"]
b_at = lambda d: halo_pts[top - d]
halo = {"cell": spec["cell"], "canvas_x": spec["canvas_x"], "channel": spec["channel"],
        "box_top_canvas_y": top, "profile_B_above_box": {str(k): v for k, v in halo_pts.items()},
        "B_at_6px_outside": b_at(6), "B_at_30px_outside": b_at(30),
        "expected_amber_B": spec["amber_B"], "expected_white_B": spec["white_B"],
        "rise_10_90_px": round(w5, 2) if w5 else None,
        "midpoint_canvas_y": round(mid5, 2) if mid5 else None,
        "midpoint_offset_outside_box_px": round(top - mid5, 2) if mid5 else None,
        "assertions": A, "claim": spec["claim"],
        "naive_step_model_rejected": spec["naive_step_model_rejected"]}
off = halo["midpoint_offset_outside_box_px"]
halo["pass"] = bool(b_at(6) <= A["B_at_minus_6_max"] and b_at(30) >= A["B_at_minus_30_min"]
                    and off is not None
                    and A["midpoint_offset_px_range"][0] <= off
                    <= A["midpoint_offset_px_range"][1])

# ------------------------------------------------------------------ ⑥ clip arc profile
arc = MEAS["arc_profile"]
a6 = CELL[arc["cell"]]["area_origin"]
ctr = plan["filters"]["circle"]["center_area"]
ccx, ccy = a6[0] + ctr[0], a6[1] + ctr[1]
th = math.radians(arc["angle_deg"])
cia = CH[arc["channel"]]
rs = list(range(arc["r_range"][0], arc["r_range"][1] + 1))
rv = [at(ccx + r * math.cos(th), ccy + r * math.sin(th))[cia] for r in rs]
ns = arc["plateau_samples"]
lo_r, hi_r = arc["step_window_r"]
win = [(r, v) for r, v in zip(rs, rv) if lo_r <= r <= hi_r]
w2, y10, y90 = rise_10_90([r for r, _ in win], [v for _, v in win])
arc_res = {"cell": arc["cell"], "angle_deg": arc["angle_deg"], "channel": arc["channel"],
           "center_canvas": [ccx, ccy], "r_range": arc["r_range"],
           f"profile_{arc['channel']}_vs_radius": dict(zip(rs, rv)),
           "inside_plateau": round(sum(rv[:ns]) / ns, 1),
           "expected_inside": arc["inside"],
           "outside_plateau": round(sum(rv[-ns:]) / ns, 1),
           "expected_outside": arc["outside"],
           "step_window_r": [lo_r, hi_r],
           "rise_10_90_px": round(w2, 2) if w2 else None,
           "crossing_10_r": round(y10, 2) if y10 else None,
           "crossing_90_r": round(y90, 2) if y90 else None,
           "predicted_max_rise_px": arc["expected_rise_10_90_px_max"],
           "note": arc["note"], "claim": arc["claim"]}
arc_res["pass"] = bool(
    w2 is not None and w2 <= arc["expected_rise_10_90_px_max"]
    and abs(arc_res["inside_plateau"] - arc["inside"][cia]) <= 4
    and abs(arc_res["outside_plateau"] - arc["outside"][cia]) <= 4)

# ------------------------------------------------------------------ verdict
groups = {"area_geometry": geo, "samples": smp, "stripe_ripple": rip,
          "cell3_rim_position": [rim], "cell4_card_edge": [edge4],
          "text_band_gradient": [grad_res], "cell5_blur_halo": [halo],
          "cell6_clip_arc_edge": [arc_res]}
flat = [c for v in groups.values() for c in v]
results = {k: v for k, v in groups.items()}
results["source_png"] = str(SRC.relative_to(ROOT)).replace("\\", "/")
results["size"] = [W, H]
results["summary"] = {
    "checks": len(flat), "passed": sum(1 for c in flat if c.get("pass")),
    "failed": [f"{g}:{c.get('label') or c.get('side') or c.get('cell')}"
               for g, v in groups.items() for c in v if not c.get("pass")],
    "max_sample_delta_levels": max((max(abs(x) for x in s["delta_levels"]) for s in smp),
                                   default=None)}
results["verified_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")

audit = dict(plan)
audit["measured"] = results
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "composite-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=1),
                                          encoding="utf-8")
print(json.dumps(results["summary"], ensure_ascii=False))
for g, v in groups.items():
    for c in v:
        if not c.get("pass"):
            print("FAIL", g, json.dumps(c, ensure_ascii=False)[:600])
print(json.dumps({"ripple": [(r["cell"], r["side"], r["measured_p2p"], r["expected_p2p"])
                             for r in rip],
                  "edge4": [edge4["rise_10_90_px"], edge4["crossing_50_area_y"],
                            edge4["plateau_outside_mean_R"],
                            edge4["plateau_inside_mean_R"]],
                  "rim": rim["dark_columns_area_x"],
                  "gradient": [grad, sharp],
                  "halo": [halo["B_at_6px_outside"], halo["B_at_30px_outside"],
                           halo["rise_10_90_px"], halo["midpoint_offset_outside_box_px"]],
                  "arc": [arc_res["rise_10_90_px"], arc_res["inside_plateau"],
                          arc_res["outside_plateau"]],
                  "worst_samples": sorted(
                      [(max(abs(x) for x in s["delta_levels"]), s["cell"], s["label"],
                        s["measured"], s["expected"]) for s in smp], reverse=True)[:4]},
             ensure_ascii=False))
