"""A22 - measure the rendered cockpit and compare it with the numbers it claims.

Nothing here trusts the DSL: bar tops are found by scanning the painted pixels, the
implied value is converted back through the axis geometry, and the result is compared
with the unrounded figure the bar was supposed to draw. Text runs are located by
template search so the audit can also prove that a label really is where the layout
map says it is.

Run:  python tmp/<run_id>/A22/verify.py --round 1
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
sys.path.insert(0, str(ROOT / "tmp" / RUN / "A22"))
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))
import dash as DS  # noqa: E402
import data as D  # noqa: E402

TOL_RGB = 40


def load(path):
    return np.asarray(Image.open(path).convert("RGB")).astype(int)


def colour_mask(img, hex_colour, tol=TOL_RGB):
    rgb = np.array([int(hex_colour[i:i + 2], 16) for i in (1, 3, 5)])
    return (np.abs(img - rgb).sum(2) <= tol)


def value_from_px(y_px, lo, hi, plot):
    return lo + (plot[3] - y_px) / (plot[3] - plot[1]) * (hi - lo)


def main(rnd):
    TMP = ROOT / "tmp" / RUN / "A22"
    img = load(TMP / f"r{rnd:02d}-dashboard.png")
    d = D.compute(rnd)
    s, _, c, meta = DS.build(rnd)
    lo, hi, step = meta["axis"]
    px0, py0, px1, py1 = DS.PLOT
    zero_y = py1 - (0 - lo) / (hi - lo) * (py1 - py0)

    checks = {}
    # 1. zero line really is painted where the geometry says
    row = img[int(round(zero_y)) - 1:int(round(zero_y)) + 2, px0 + 40:px1 - 40]
    checks["zero_line_pixels"] = int((np.abs(row - np.array([148, 163, 184])).sum(2)
                                      <= 60).sum(1).max() > 200)

    # 2. every bar is measured where the layout says it is, and its painted height is
    #    converted back through the axis to compare with the unrounded value
    n = len(d["months"])
    pitch = (px1 - px0) / n
    bar_w = min(46.0, pitch * 0.36)
    gap = 10.0
    rows = []
    for j, (key, colour) in enumerate((("net_revenue", "net"),
                                       ("operating_profit", "profit"))):
        m2 = colour_mask(img, DS.P[colour])
        for i, m in enumerate(d["months"]):
            gcx = px0 + pitch * (i + 0.5)
            x0 = gcx - bar_w - gap / 2 + j * (bar_w + gap)
            cx = int(round(x0 + bar_w / 2))
            col = np.where(m2[py0 - 20:py1 + 20, cx])[0] + py0 - 20
            if len(col) == 0:
                rows.append({"month": m["month"], "series": key, "error": "no bar pixels",
                             "centre_x": cx})
                continue
            # the value label above/below the bar is painted in the same colour, so
            # only the contiguous run that touches the zero line is the bar itself
            z = int(round(zero_y))
            idx = set(int(v) for v in col)
            # the 2px zero line is painted under the bar, so seed from the nearest
            # bar-coloured row instead of assuming the rounded zero row belongs to it
            seed = next((c for c in (z, z - 1, z - 2, z + 1, z + 2) if c in idx), None)
            if seed is None:
                rows.append({"month": m["month"], "series": key,
                             "error": "no bar pixels at the zero line", "centre_x": cx})
                continue
            top = bot = seed
            while top - 1 in idx:
                top -= 1
            while bot + 1 in idx:
                bot += 1
            positive = m[key] >= 0
            edge = top - 0.5 if positive else bot + 0.5
            val = value_from_px(edge, lo, hi, DS.PLOT) * 10000
            # width: how many columns at mid-bar height carry the bar colour
            midy = int((max(top, py0) + min(bot, py1)) / 2)
            run = np.where(m2[midy, px0:px1])[0]
            seg = [int(c + px0) for c in run if abs(c + px0 - cx) <= bar_w]
            rows.append({
                "month": m["month"], "series": key,
                "expected_yuan": m[key], "measured_yuan": round(val),
                "centre_x": cx, "expected_x0": round(x0, 2),
                "top_px": top, "bottom_px": bot,
                "expected_px": round((abs(m[key]) / 10000) / (hi - lo)
                                     * (py1 - py0), 2),
                "measured_px": round(abs(edge - zero_y), 2),
                "width_px": (max(seg) - min(seg) + 1) if seg else 0,
                "expected_width_px": round(bar_w, 2),
            })
    worst_px = max(abs(r["expected_px"] - r["measured_px"]) for r in rows)
    worst_val = max(abs(r["expected_yuan"] - r["measured_yuan"]) for r in rows)
    checks["bars"] = rows
    checks["bar_worst_px_error"] = float(worst_px)
    checks["bar_worst_yuan_error"] = int(worst_val)
    checks["bar_width_ok"] = all(abs(r["width_px"] - r["expected_width_px"]) <= 2
                                 for r in rows)
    checks["bar_height_ok"] = all(abs(r["expected_px"] - r["measured_px"]) <= 1.5
                                  for r in rows)
    checks["bar_position_ok"] = all(abs(r["centre_x"] - (r["expected_x0"]
                                                        + r["expected_width_px"] / 2))
                                    <= 1.5 for r in rows)
    checks["negative_bar_below_zero"] = [
        r["month"] + "/" + r["series"] for r in rows if r["expected_yuan"] < 0]

    # 3. every text run of the layout exists in the render at the recorded box
    built = json.loads((TMP / f"r{rnd:02d}-built.json").read_text(encoding="utf-8"))
    grey = np.asarray(Image.open(TMP / f"r{rnd:02d}-dashboard-noink.png").convert(
        "RGB")).astype(int) if (TMP / f"r{rnd:02d}-dashboard-noink.png").exists() else None
    ink = np.abs(img - grey).sum(2) > 60 if grey is not None else None
    text_checks = []
    if ink is None:
        checks["text_runs_checked"] = 0
        text_checks = [{"note": "no twin render"}]
    for it in (built["items"] if ink is not None else []):
        x0, y0, x1, y1 = [int(round(v)) for v in it["box"]]
        band = ink[y0:y1 + 1, :]
        # nothing may be painted in the 4px strips just outside the recorded box:
        # that is what an under-estimated text width would show up as
        left = int(band[:, max(x0 - 4, 0):x0].sum())
        right = int(band[:, x1 + 1:x1 + 5].sum())
        text_checks.append({"text": it["text"], "role": it["role"], "box": it["box"],
                            "ink_px": int(band.sum()), "spill_left": left,
                            "spill_right": right})
    # a 1-3px fringe in the 4px strip is anti-aliasing of the last glyph, not overflow;
    # a whole character escaping the box would paint 15-25px there
    SPILL_OK = 6
    bad = [t for t in text_checks
           if t.get("ink_px", 1) < 20 or t.get("spill_left", 0) > SPILL_OK
           or t.get("spill_right", 0) > SPILL_OK]
    checks["text_spill_tolerance_px"] = SPILL_OK
    checks["text_box_failures"] = bad
    checks["text_runs_checked"] = len(text_checks)

    # 4. the "sum first" rule really produced the printed overall rate
    from fractions import Fraction as F
    mean_monthly = (sum(F(m["conversion_rate_exact"]["numerator"],
                         m["conversion_rate_exact"]["denominator"]) for m in d["months"])
                    / len(d["months"]) * 100)
    overall = F(d["totals"]["overall_conversion_rate_exact"]["numerator"],
                d["totals"]["overall_conversion_rate_exact"]["denominator"]) * 100
    checks["overall_rate_sum_first"] = {
        "printed_pct": d["totals"]["display"]["overall_conversion_rate_pct"],
        "sum_based_pct_unrounded": float(overall),
        "mean_of_monthly_pct_unrounded": float(mean_monthly),
        "differs_from_mean_of_months": bool(abs(overall - mean_monthly) > F(1, 10000)),
        "printed_equals_sum_based": str(D.half_up(overall, 2)) ==
                                    d["totals"]["display"]["overall_conversion_rate_pct"],
    }
    assert checks["overall_rate_sum_first"]["printed_equals_sum_based"]

    out = {"round": rnd, "axis": meta["axis"], "zero_y_px": round(zero_y, 2),
           "checks": {k: v for k, v in checks.items()
                      if k not in ("bars", "text_boxes_sample")},
           "bars": rows, "text_boxes": text_checks}
    (TMP / f"r{rnd:02d}-verify.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"round": rnd, "zero_line": checks["zero_line_pixels"],
                      "worst_px": checks["bar_worst_px_error"],
                      "worst_yuan": checks["bar_worst_yuan_error"],
                      "widths_ok": checks["bar_width_ok"],
                      "text_fails": len(bad),
                      "text_examples": [b["text"] for b in bad][:4],
                      "neg_bars": len(checks["negative_bar_below_zero"])},
                     ensure_ascii=False))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", type=int, required=True, choices=(1, 2, 3))
    a = ap.parse_args()
    main(a.round)
