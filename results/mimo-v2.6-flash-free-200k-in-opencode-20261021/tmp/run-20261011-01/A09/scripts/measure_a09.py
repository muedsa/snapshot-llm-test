#!/usr/bin/env python3
"""Sub-pixel verification of the rendered A09 atlas -> geometry-audit.json.

Usage: python tmp/<run_id>/A09/scripts/measure_a09.py <suite_root> <run_id> <png> [audit_json]

Method (anti-aliased edges are measured, not excepted):
  Every cell pixel is tested for membership in a shape by projecting it onto
  the blend line  pixel = f*inside + (1-f)*neighbour  where neighbour is the
  cell background first (fast path) and otherwise another palette colour.
  Fits with residual <= 8 (8-bit round-off of a true AA blend) and
  0 < f <= 1 count as coverage.
  rects : per scanline/row the first and last member pixel give the sub-pixel
          interval [x + 1 - f_first, x_last + f_last]; bbox side = min/max of
          those over all scanlines, so corner rows with fractional coverage are
          included.
  dot   : centre = f-weighted centroid; bbox from the same row/column
          sub-pixel intervals (dot only abuts cell background).
  stamp : union of measured rect/dot boxes.
Criterion: every component error <= 1.5 px.
"""
import json
import math
import pathlib
import sys
from datetime import datetime

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
run_id = sys.argv[2] if len(sys.argv) > 2 else "run-20261011-01"
png = pathlib.Path(sys.argv[3]) if len(sys.argv) > 3 else (
    root / "outputs" / run_id / "A09" / "transform-atlas.png")
audit_path = pathlib.Path(sys.argv[4]) if len(sys.argv) > 4 else (
    root / "outputs" / run_id / "A09" / "geometry-audit.json")

INP = root / "tasks" / "A09-transform-atlas" / "inputs"
stamp = json.loads((INP / "stamp.json").read_text(encoding="utf-8"))
audit = json.loads(audit_path.read_text(encoding="utf-8"))

from PIL import Image

try:
    png_rel = str(png.resolve().relative_to(root)).replace("\\", "/")
except ValueError:
    png_rel = str(png).replace("\\", "/")
im = Image.open(png).convert("RGB")
px = im.load()
W, H = im.size
assert (W, H) == (1600, 1200), f"unexpected PNG size {W}x{H}"

CRIT = 1.5
RESID_MAX = 8.0        # 8-bit round-off of a genuine linear AA blend
MIN_F = 0.02           # ignore negligible fringe
BG = (15, 23, 46)      # CELL_BG #0F172E
DOT = tuple(int(stamp["dot"]["color"][i:i + 2], 16) for i in (1, 3, 5))
COLS = [tuple(int(r["color"][i:i + 2], 16) for i in (1, 3, 5))
        for r in stamp["rectangles"]]           # [red, blue, yellow]
# cell furniture drawn by gen_a09.py around/under the stamp: crosshair, ticks,
# axis labels, cell border, ID accent and text. Blends of these with the cell
# background are NOT stamp coverage even though some of them land on a
# shape->dot line with residual <= 8 (e.g. the 50% crosshair AA pixel
# (28,40,69) fits BG->blue via DOT at f=0.263, resid=6.5).
_HEX = lambda s: tuple(int(s[i:i + 2], 16) for i in (1, 3, 5))
FURN = [_HEX(c) for c in ("#1E293B", "#2A3B5C", "#334155", "#64748B",
                          "#7DD3FC", "#F8FAFC", "#CBD5E1")]


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def dot3(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def nrm(a):
    return math.sqrt(dot3(a, a))


def fit_f(p, c, n):
    """pixel p = f*c + (1-f)*n -> (f, residual)."""
    d = sub(c, n)
    dd = dot3(d, d)
    f = dot3(sub(p, n), d) / dd
    pred = (n[0] + f * d[0], n[1] + f * d[1], n[2] + f * d[2])
    return f, nrm(sub(p, pred))


_cache = {}


def cover(xx, yy, ci):
    """Sub-pixel coverage of pixel (xx,yy) w.r.t. rect colour ci (or None).

    The background->colour line is authoritative: if it explains the pixel
    (residual <= RESID_MAX), the pixel is either background (f<=MIN_F -> None)
    or coverage of this colour (f). Only pixels the background line cannot
    explain (blend lines between two palette colours, e.g. red+blue AA) are
    tried against other palette lines, taking the smallest residual. Without
    this, plain cell-background pixels fit the background->dot line
    (residual ~7 <= 8, f=0.13) and fake coverage everywhere.
    """
    key = (xx, yy, ci)
    hit = _cache.get(key)
    if hit is not None:
        return hit
    p = px[xx, yy]
    f0, r0 = fit_f(p, COLS[ci], BG)
    if r0 <= RESID_MAX:
        out = f0 if MIN_F < f0 <= 1.0 else None
        _cache[key] = out
        return out
    # not on this shape's background line: cell furniture (crosshair/tick/
    # axis/border/text) blended with the background also lands on some other
    # line with a small residual -> reject it before palette fallback
    for furn in FURN:
        ff, rf = fit_f(p, furn, BG)
        if 0.0 <= ff <= 1.0 and rf <= RESID_MAX:
            _cache[key] = None
            return None
    best = None
    for n in [c for k, c in enumerate(COLS) if k != ci] + [DOT]:
        f, r = fit_f(p, COLS[ci], n)
        if MIN_F < f <= 1.0 and r <= RESID_MAX and (best is None or r < best[1]):
            best = (f, r)
    out = best[0] if best else None
    _cache[key] = out
    return out


verification = []
EXCL_REL = [(4, 2, 72, 38), (4, 196, 292, 234)]   # ID top-left, op-name bottom-left
INSET = 12            # avoid rounded-corner page background + cell border
for i, tf in enumerate(audit["transforms"]):
    geom = audit["geometry"][i]
    assert geom["id"] == tf["id"]
    cx, cy = tf["cell_center"]
    x0, y0, x1, y1 = cx - 150, cy - 125, cx + 150, cy + 125
    excl = [(x0 + a, y0 + b, x0 + c, y0 + d) for a, b, c, d in EXCL_REL]
    bb = geom["bbox_canvas"]
    for e in excl:
        assert not (bb[0] < e[2] and bb[2] > e[0] and bb[1] < e[3] and bb[3] > e[1]), \
            f"{tf['id']} subject intersects label zone {e}"
    assert (bb[0] >= x0 + INSET and bb[2] <= x1 - INSET
            and bb[1] >= y0 + INSET and bb[3] <= y1 - INSET), \
        f"{tf['id']} subject outside dot measurement inset: {bb}"

    def blocked(xx, yy):
        return any(e[0] <= xx < e[2] and e[1] <= yy < e[3] for e in excl)

    comps = []
    measured_union = [1e18, 1e18, -1e18, -1e18]
    for ri in range(3):
        # pass 1: rows/columns containing solid (>=65%) interior -> anchor band
        solid_rows, solid_cols = {}, {}
        for yy in range(y0, y1):
            xs = [xx for xx in range(x0, x1)
                  if not blocked(xx, yy)
                  and (f := cover(xx, yy, ri)) is not None and f >= 0.65]
            if xs:
                solid_rows[yy] = xs
        for xx in range(x0, x1):
            ys = [yy for yy in range(y0, y1)
                  if not blocked(xx, yy)
                  and (f := cover(xx, yy, ri)) is not None and f >= 0.65]
            if ys:
                solid_cols[xx] = ys
        assert solid_rows and solid_cols, f"{tf['id']} rect{ri} has no solid interior"
        y_lo, y_hi = min(solid_rows), max(solid_rows)
        x_lo, x_hi = min(solid_cols), max(solid_cols)
        rows_band = range(max(y0, y_lo - 4), min(y1, y_hi + 5))
        cols_band = range(max(x0, x_lo - 4), min(x1, x_hi + 5))
        x_band = range(max(x0, x_lo - 12), min(x1, x_hi + 13))
        y_band = range(max(y0, y_lo - 12), min(y1, y_hi + 13))

        def run_of(members, start):
            a = b = start
            while (a - 1) in members:
                a -= 1
            while (b + 1) in members:
                b += 1
            return a, b

        lefts, rights = [], []
        for yy in rows_band:
            members = {}
            for xx in x_band:
                if blocked(xx, yy):
                    continue
                f = cover(xx, yy, ri)
                if f is not None:
                    members[xx] = f
            if not members:
                continue
            best = max(members, key=lambda k: members[k])
            a, b = run_of(members, best)
            lefts.append(a + 1 - members[a])
            rights.append(b + members[b])
        tops, bots = [], []
        for xx in cols_band:
            members = {}
            for yy in y_band:
                if blocked(xx, yy):
                    continue
                f = cover(xx, yy, ri)
                if f is not None:
                    members[yy] = f
            if not members:
                continue
            best = max(members, key=lambda k: members[k])
            a, b = run_of(members, best)
            tops.append(a + 1 - members[a])
            bots.append(b + members[b])
        assert len(lefts) > 10 and len(tops) > 10, f"{tf['id']} rect{ri} sparse rows"
        mb = [min(lefts), min(tops), max(rights), max(bots)]
        pred = [min(c[0] for c in geom["rectangles"][ri]["corners_canvas_TL_TR_BR_BL"]),
                min(c[1] for c in geom["rectangles"][ri]["corners_canvas_TL_TR_BR_BL"]),
                max(c[0] for c in geom["rectangles"][ri]["corners_canvas_TL_TR_BR_BL"]),
                max(c[1] for c in geom["rectangles"][ri]["corners_canvas_TL_TR_BR_BL"])]
        err = [round(m - p, 3) for m, p in zip(mb, pred)]
        comps.append({"component": f"rect{ri}_bbox", "predicted": pred,
                      "measured": [round(v, 3) for v in mb],
                      "error_left_top_right_bottom": err,
                      "max_abs_error": round(max(abs(e) for e in err), 3)})
        for k in range(4):
            measured_union[k] = (min(measured_union[k], mb[k]) if k < 2
                                 else max(measured_union[k], mb[k]))

    # ---- dot: coverage centroid + row/column sub-pixel intervals -----------
    # MIN_F_DOT=0.05: integer rounding of flat cell background projects onto
    # the background->dot line with f <= (2+6+29)/881 = 0.042, while every
    # shape/AA blend projects negatively -> 0.05 separates strays from the
    # dot fringe without losing real edge pixels (cost <= 0.05 px).
    MIN_F_DOT = 0.05
    fs = []
    dl, dr, dt, db_ = [], [], [], []
    for yy in range(y0 + INSET, y1 - INSET):         # rounded corners excluded
        first = last = None
        for xx in range(x0 + INSET, x1 - INSET):
            if blocked(xx, yy):
                continue
            f, resid = fit_f(px[xx, yy], DOT, BG)
            if MIN_F_DOT < f <= 1.0 and resid <= RESID_MAX:
                fs.append((xx + 0.5, yy + 0.5, f))
                if first is None:
                    first = (xx, f)
                last = (xx, f)
        if first is not None:
            dl.append(first[0] + 1 - first[1])
            dr.append(last[0] + last[1])
    for xx in range(x0 + INSET, x1 - INSET):
        first = last = None
        for yy in range(y0 + INSET, y1 - INSET):
            if blocked(xx, yy):
                continue
            f, resid = fit_f(px[xx, yy], DOT, BG)
            if MIN_F_DOT < f <= 1.0 and resid <= RESID_MAX:
                if first is None:
                    first = (yy, f)
                last = (yy, f)
        if first is not None:
            dt.append(first[0] + 1 - first[1])
            db_.append(last[0] + last[1])
    assert len(fs) >= 80, f"{tf['id']} dot coverage pixels {len(fs)}"
    mass = sum(f for _, _, f in fs)
    dcx = sum(x * f for x, _, f in fs) / mass
    dcy = sum(y * f for _, y, f in fs) / mass
    db = [min(dl), min(dt), max(dr), max(db_)]
    pdot = geom["dot"]["center_canvas"]
    pdot_bb = [pdot[0] - geom["dot"]["bbox_half_extents"][0],
               pdot[1] - geom["dot"]["bbox_half_extents"][1],
               pdot[0] + geom["dot"]["bbox_half_extents"][0],
               pdot[1] + geom["dot"]["bbox_half_extents"][1]]
    cerr = [round(dcx - pdot[0], 3), round(dcy - pdot[1], 3)]
    comps.append({"component": "dot_center", "predicted": pdot,
                  "measured": [round(dcx, 3), round(dcy, 3)],
                  "error_left_top_right_bottom": cerr,
                  "max_abs_error": round(max(abs(e) for e in cerr), 3)})
    derr = [round(m - p, 3) for m, p in zip(db, pdot_bb)]
    comps.append({"component": "dot_bbox", "predicted": pdot_bb,
                  "measured": [round(v, 3) for v in db],
                  "error_left_top_right_bottom": derr,
                  "max_abs_error": round(max(abs(e) for e in derr), 3)})
    for k in range(4):
        measured_union[k] = (min(measured_union[k], db[k]) if k < 2
                             else max(measured_union[k], db[k]))
    serr = [round(m - p, 3) for m, p in zip(measured_union, geom["bbox_canvas"])]
    comps.append({"component": "stamp_bbox", "predicted": geom["bbox_canvas"],
                  "measured": [round(v, 3) for v in measured_union],
                  "error_left_top_right_bottom": serr,
                  "max_abs_error": round(max(abs(e) for e in serr), 3)})

    worst = max(c["max_abs_error"] for c in comps)
    verification.append({
        "id": tf["id"],
        "method": ("sub-pixel coverage intervals: each cell pixel projected onto "
                   "blend line f*inside+(1-f)*neighbour (background first, then other "
                   "palette colours), residual<=8 and 0<f<=1 accepted; first/last "
                   "member per scanline -> [x+1-f, x+f], bbox side = min/max over "
                   "scanlines (fractional corner rows included); dot centre = "
                   "coverage centroid, dot bbox from row/column intervals; "
                   "predicted values are the four transformed source corners "
                   "(TL,TR,BR,BL) from geometry[]; ID/op-name label zones excluded "
                   "(asserted disjoint from subject)"),
        "criterion_px": CRIT,
        "anti_alias_exception": ("AA edges are fitted sub-pixel rather than skipped: "
                                 "the residual<=8 guard rejects pixels where two blend "
                                 "lines mix, and the inset 12px skips rounded-corner "
                                 "page-background pixels"),
        "components": comps,
        "max_abs_error_px": round(worst, 3),
        "passed": worst <= CRIT,
        "evidence": {"png": png_rel, "measure_log": "tmp/" + run_id + "/A09/measure.json"},
    })
    print(f"{tf['id']}: max_err={worst:.3f}px pass={worst <= CRIT}")

audit["verification"] = verification
audit["verification_summary"] = {
    "criterion_px": CRIT,
    "all_passed": all(v["passed"] for v in verification),
    "worst_error_px": max(v["max_abs_error_px"] for v in verification),
    "measured_png": png_rel,
    "measured_at": datetime.now().astimezone().isoformat(timespec="seconds"),
    "measured_components": sum(len(v["components"]) for v in verification),
}
audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
log = root / "tmp" / run_id / "A09" / "measure.json"
log.write_text(json.dumps(verification, ensure_ascii=False, indent=2), encoding="utf-8")
print("all_passed:", audit["verification_summary"]["all_passed"],
      "worst:", audit["verification_summary"]["worst_error_px"])
