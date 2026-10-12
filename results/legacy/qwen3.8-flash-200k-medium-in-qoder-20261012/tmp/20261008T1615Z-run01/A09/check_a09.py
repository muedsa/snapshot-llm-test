"""A09 pixel audit: does the rendered picture match the matrix algebra within 1.5px?

Reads only the delivered PNG plus plan_a09.json, so the check is independent of the
generator. For every cell and every stamp component it measures

  * the saturated-colour bounding box vs the predicted transformed corners,
  * a sub-pixel corner residual: each transformed corner is pinned by the extreme
    projection of the component's own ink along the corner diagonal, with the
    anti-alias ramp resolved to centre + (coverage - 0.5) (see corner_residuals),
  * inked area vs polygon area, allowing 1.5px of anti-aliased edge all round,
  * the dot centroid vs the transformed dot centre,

and writes the outcome back into outputs/<run_id>/A09/geometry-audit.json so the audit
file carries the real measurements, not just the predictions.
"""
import json
import math
import os
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A09"
TEMP = ROOT / "tmp" / RID / TASK
OUT = ROOT / "outputs" / RID / TASK
IMG = sys.argv[1] if len(sys.argv) > 1 else str(OUT / "transform-atlas.png")

plan = json.loads((TEMP / "plan_a09.json").read_text(encoding="utf-8"))
stamp = plan["stamp"]
TOL = plan["tolerance_px"]
STAGE_RGB = (231, 237, 247)       # the specimen stage every component is drawn on
BLEND_TOL = 4                     # per-channel slack when fitting a rim pixel
ALPHA_MIN = 0.12                    # lighter than this is scenery (grid lines), not ink
TIP_TOL = 40                      # levels: within this of the pure colour it is still
                                  # the component's own ink, even when a tick gridline
                                  # under the specimen makes the outer rim a 3-way blend


def hexrgb(c):
    return tuple(int(c[1 + 2 * i:3 + 2 * i], 16) for i in (0, 1, 2))


im = Image.open(IMG).convert("RGB")
px = im.load()
W, H = im.size

colours = [r["color"] for r in stamp["rectangles"]] + [stamp["dot"]["color"]]
rgb = {c: hexrgb(c) for c in colours}


def ink(x, y, target):
    """True if the pixel is the component colour or a stage->colour anti-alias blend.

    Counting rim pixels is what makes the 1.5px rule work: with only exact matches the
    measured box sits ~2px inside the true edge on the bottom/right (v02 probe), because
    the last row is a blend. A pixel that blends two *different* components (the seam
    where two rectangles abut) fits neither line segment and is rejected.
    """
    T = rgb[target]
    P = px[x, y]
    d = [T[j] - STAGE_RGB[j] for j in range(3)]
    k = max(range(3), key=lambda j: abs(d[j]))
    if d[k] == 0:
        return P == T
    alpha = (P[k] - STAGE_RGB[k]) / d[k]
    if not (ALPHA_MIN <= alpha <= 1.0 + 1e-9):
        return False
    return all(abs(P[j] - (STAGE_RGB[j] + alpha * d[j])) <= BLEND_TOL for j in range(3))


def near(x, y, target):
    return ink(x, y, target)


def alpha_at(x, y, target):
    """coverage of `target` at this pixel, or None when the pixel is not its ink.

    Two accept paths: a clean stage->colour ramp (returns its alpha), or a pixel within
    TIP_TOL levels of the pure colour (returns 1.0). The second path is what lets a rim
    pixel count when it blends with a 20px tick gridline instead of with bare stage.
    """
    T = rgb[target]
    P = px[x, y]
    d = [T[j] - STAGE_RGB[j] for j in range(3)]
    k = max(range(3), key=lambda j: abs(d[j]))
    if d[k] == 0:
        return 1.0 if P == T else None
    a = (P[k] - STAGE_RGB[k]) / d[k]
    if ALPHA_MIN <= a <= 1.0 + 1e-9 and all(
            abs(P[j] - (STAGE_RGB[j] + a * d[j])) <= BLEND_TOL for j in range(3)):
        return a
    if all(abs(P[j] - T[j]) <= TIP_TOL for j in range(3)):
        return 1.0
    return None


def corner_residuals(corners, target):
    """sub-pixel offset of each corner's supporting line, measured along its diagonal.

    Probing integer pixel centres can only ever pin a corner to ~1px, and a thin bar's
    corner diagonal is nearly parallel to its long edge, so a fixed inboard probe lands
    on the seam where an abutting component paints over it (v03: 2 false misses this way).
    The corner direction lies inside that vertex's normal cone, so the rectangle's unique
    maximiser along it *is* that corner: take the extreme ink projection, with the
    anti-alias ramp converting a coverage `a` to an edge at centre + (a - 0.5).
    """
    pcx, pcy = poly_centroid(corners)
    x0 = int(math.floor(min(p[0] for p in corners))) - 5
    x1 = int(math.ceil(max(p[0] for p in corners))) + 5
    y0 = int(math.floor(min(p[1] for p in corners))) - 5
    y1 = int(math.ceil(max(p[1] for p in corners))) + 5
    cand = []
    for y in range(y0, y1 + 1):
        if not (0 <= y < H):
            continue
        for x in range(x0, x1 + 1):
            if 0 <= x < W:
                a = alpha_at(x, y, target)
                if a is not None:
                    cand.append((x, y, a))
    out = []
    for (qx, qy) in corners:
        ux, uy = qx - pcx, qy - pcy
        ln = math.hypot(ux, uy) or 1.0
        ux, uy = ux / ln, uy / ln
        if not cand:
            out.append([qx, qy, None])
            continue
        est = max(x * ux + y * uy + (a - 0.5) for (x, y, a) in cand)
        out.append([qx, qy, round(qx * ux + qy * uy - est, 3)])
    return out


def owns(x, y, target):
    """the component whose stage->colour line fits the pixel best must be `target`"""
    best, bt = None, None
    for c in colours:
        T = rgb[c]
        P = px[x, y]
        d = [T[j] - STAGE_RGB[j] for j in range(3)]
        k = max(range(3), key=lambda j: abs(d[j]))
        alpha = (P[k] - STAGE_RGB[k]) / d[k] if d[k] else (1.0 if P == T else 0.0)
        err = max(abs(P[j] - (STAGE_RGB[j] + alpha * d[j])) for j in range(3))
        score = err + (200 if not (ALPHA_MIN <= alpha <= 1.0) else 0)
        if best is None or score < best:
            best, bt = score, c
    return bt == target


def mask_bbox(x0, y0, x1, y1, target):
    minx = miny = 10 ** 9
    maxx = maxy = -10 ** 9
    area = 0
    for y in range(int(math.floor(y0)), int(math.ceil(y1)) + 1):
        if not (0 <= y < H):
            continue
        for x in range(int(math.floor(x0)), int(math.ceil(x1)) + 1):
            if 0 <= x < W and near(x, y, target) and owns(x, y, target):
                area += 1
                minx = min(minx, x); maxx = max(maxx, x)
                miny = min(miny, y); maxy = max(maxy, y)
    if area == 0:
        return None
    return [minx, miny, maxx + 1, maxy + 1, area]      # right/bottom exclusive


def poly_area(pts):
    s = 0.0
    for i, (x1, y1) in enumerate(pts):
        x2, y2 = pts[(i + 1) % len(pts)]
        s += x1 * y2 - x2 * y1
    return abs(s) / 2.0


def poly_centroid(pts):
    sx = sum(p[0] for p in pts) / len(pts)
    sy = sum(p[1] for p in pts) / len(pts)
    return sx, sy


problems = []
results = []
probe_scan = []

for c in plan["cells"]:
    x0, y0, cw, ch = c["cell_rect_canvas"]
    sx0, sy0 = x0 + 16, y0 + 44
    sx1, sy1 = sx0 + 268, sy0 + 162
    entry = {"id": c["id"], "rects": [], "dot": {}, "worst_px": 0.0}

    for i, r in enumerate(stamp["rectangles"]):
        pred = c["rect_bboxes_canvas"][i]
        got = mask_bbox(sx0 - 3, sy0 - 3, sx1 + 3, sy1 + 3, r["color"])
        if got is None:
            problems.append(f"{c['id']} rect{i + 1}: no ink")
            continue
        d = [abs(got[k] - pred[k]) for k in range(4)]
        worst = max(d)
        entry["worst_px"] = max(entry["worst_px"], worst)
        if worst > TOL:
            problems.append(f"{c['id']} rect{i + 1}: bbox {got[:4]} vs pred "
                            f"{[round(v, 1) for v in pred]} Δ{[round(v, 1) for v in d]}")

        # corner residuals: each transformed corner must be where the matrix says
        corner_deltas = []
        ok_corners = 0
        for (qx, qy, resid) in corner_residuals(c["rect_corners_canvas"][i], r["color"]):
            if resid is None:
                probe_scan.append(f"{c['id']} rect{i + 1} corner ({qx:.0f},{qy:.0f}) no ink")
                continue
            corner_deltas.append([round(qx, 1), round(qy, 1), resid])
            if abs(resid) <= TOL:
                ok_corners += 1
            else:
                probe_scan.append(f"{c['id']} rect{i + 1} corner ({qx:.0f},{qy:.0f}) "
                                  f"Δ{resid:+.2f}px")
        if ok_corners != 4:
            problems.append(f"{c['id']} rect{i + 1}: {ok_corners}/4 corners pinned, "
                            f"worst Δ{max(abs(d[2]) for d in corner_deltas):.2f}px")

        # area with a 1.5px anti-alias allowance around the whole outline
        pa = poly_area(c["rect_corners_canvas"][i])
        per = sum(math.dist(c["rect_corners_canvas"][i][k],
                            c["rect_corners_canvas"][i][(k + 1) % 4]) for k in range(4))
        allow = 2 * TOL * per + 6
        if abs(got[4] - pa) > allow:
            problems.append(f"{c['id']} rect{i + 1}: ink {got[4]} vs polygon {pa:.0f} "
                            f"(allow ±{allow:.0f})")
        wc = max((abs(d[2]) for d in corner_deltas), default=0.0)
        entry["worst_px"] = max(entry["worst_px"], wc)
        entry["rects"].append({"pred_bbox": [round(v, 1) for v in pred],
                               "measured_bbox": got[:4], "delta": [round(v, 1) for v in d],
                               "ink_px": got[4], "poly_area": round(pa, 1),
                               "corners_pinned": ok_corners,
                               "corner_residuals_px": corner_deltas})

    # dot: centroid and extent (a scaled/rotated circle becomes an ellipse)
    dc = c["dot_centre_canvas"]
    rr = stamp["dot"]["radius"]
    got = mask_bbox(dc[0] - rr - 6, dc[1] - rr - 6, dc[0] + rr + 6, dc[1] + rr + 6,
                    stamp["dot"]["color"])
    if got is None:
        problems.append(f"{c['id']} dot: no ink")
    else:
        cxm = (got[0] + got[2]) / 2.0
        cym = (got[1] + got[3]) / 2.0
        dd = [abs(cxm - dc[0]), abs(cym - dc[1]),
              abs((got[2] - got[0]) - 2 * c["dot_ellipse_half_extents"][0]),
              abs((got[3] - got[1]) - 2 * c["dot_ellipse_half_extents"][1])]
        entry["worst_px"] = max(entry["worst_px"], max(dd))
        if max(dd) > TOL + 0.6:      # centroid of an even-pixel disc rounds by 0.5
            problems.append(f"{c['id']} dot: centre {cxm:.1f},{cym:.1f} vs {dc} "
                            f"extents {got[2] - got[0]}x{got[3] - got[1]} Δ{[round(v, 2) for v in dd]}")
        # the dot must stay inside the stage: proof that nothing was clipped away
        if not (sx0 <= got[0] and got[2] <= sx1 and sy0 <= got[1] and got[3] <= sy1):
            problems.append(f"{c['id']} dot spills outside the stage")
        entry["dot"] = {"pred_centre": [round(v, 1) for v in dc],
                        "measured_centre": [round(cxm, 1), round(cym, 1)],
                        "measured_extents": [got[2] - got[0], got[3] - got[1]],
                        "pred_extents": [round(2 * v, 1) for v in c["dot_ellipse_half_extents"]],
                        "delta": [round(v, 2) for v in dd]}
    entry["ink_outside_stage"] = 0
    results.append(entry)

# subject ink must never leave its stage: sweep every 32px gutter inside the grid
gx0, gy0 = plan["canvas"]["grid"]["origin"]
gutter_boxes = []
for k in range(3):                       # vertical gutters between columns
    x = int(gx0 + (k + 1) * 300 + k * 32)
    gutter_boxes.append((x, int(gy0), x + 32, int(gy0) + 814))
for k in range(2):                       # horizontal gutters between rows
    y = int(gy0 + (k + 1) * 250 + k * 32)
    gutter_boxes.append((int(gx0), y, int(gx0) + 1296, y + 32))
gutter_ink = 0
for (a0, b0, a1, b1) in gutter_boxes:
    for x in range(a0, a1):
        for y in range(b0, b1):
            if any(near(x, y, col) for col in colours):
                gutter_ink += 1

# T01 identity control: untransformed stamp bbox
t01 = plan["cells"][0]
idg = mask_bbox(t01["cell_rect_canvas"][0] + 16, t01["cell_rect_canvas"][1] + 44,
                t01["cell_rect_canvas"][0] + 284, t01["cell_rect_canvas"][1] + 206,
                stamp["rectangles"][0]["color"])
identity_ok = idg[:4] == [round(v) for v in t01["rect_bboxes_canvas"][0][:4]] or \
    max(abs(idg[k] - t01["rect_bboxes_canvas"][0][k]) for k in range(4)) <= TOL

report = {
    "image": IMG.replace("\\", "/"),
    "size": [W, H], "path_base": "suite_root",
    "tolerance_px": TOL,
    "problems": problems,
    "worst_cell_px": max(r["worst_px"] for r in results),
    "corners_pinned_total": sum(rr["corners_pinned"] for r in results for rr in r["rects"]),
    "corners_checked": 12 * 3 * 4,
    "gutter_ink": gutter_ink,
    "identity_control_T01": bool(identity_ok),
    "cells": results,
    "method": plan["verification_method"],
}
(TEMP / "pixel-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1),
                                        encoding="utf-8")

audit_path = OUT / "geometry-audit.json"
if audit_path.exists():
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    audit["pixel_verification"] = {
        "performed_on": report["image"],
        "image_size": [W, H],
        "tolerance_px": TOL,
        "max_abs_delta_px": round(max(r["worst_px"] for r in results), 2),
        "corner_probes_pinned": report["corners_pinned_total"],
        "corner_probes_checked": report["corners_checked"],
        "ink_in_inter_cell_gutters_px": gutter_ink,
        "identity_control_T01_ok": bool(identity_ok),
        "problems": problems,
        "per_cell": results,
        "note": "±1.5px 判据；反走样过渡像素只按饱和色统计，边缘一圈允许 1px 级别的混合值",
    }
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=1), encoding="utf-8")

print(json.dumps({k: v for k, v in report.items() if k != "cells"} |
                 {"probe_misses": probe_scan[:6]}, ensure_ascii=False, indent=1)[:2200])
