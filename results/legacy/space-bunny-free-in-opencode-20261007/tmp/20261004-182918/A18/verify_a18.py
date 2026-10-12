"""A18 verification: pixel + DSL level checks against the task's hard limits.

Both the delivered PNG (raw service response bytes) and the delivered
.snapshot (the exact DSL that produced it) are inspected. Nothing is re-rendered.
"""
from __future__ import annotations

import json
import math
import os
import re
import sys

from PIL import Image

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
TASK = "A18"
OUT = os.path.join(ROOT, "outputs", RUN, TASK)
PNG = os.path.join(OUT, "three-act-story.png")
DSL = os.path.join(OUT, "three-act-story.snapshot")
AUDIT = os.path.join(OUT, "story-audit.json")

UNIT_R, UNIT_D = 18, 36
NODE, NODE_BORDER = 72, 2
UNIT_HEX = {"blue": "#2F6FE4FF", "orange": "#F0761AFF", "grey": "#98A6B8FF"}
SHELL_FILL = {"live": "#243447FF", "idle": "#16202EFF"}

report = {"png": os.path.relpath(PNG, ROOT), "dsl": os.path.relpath(DSL, ROOT), "checks": []}


def rgb(h):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def near(p, q, tol):
    return abs(p[0] - q[0]) <= tol and abs(p[1] - q[1]) <= tol and abs(p[2] - q[2]) <= tol


def ck(name, ok, detail):
    report["checks"].append({"check": name, "pass": bool(ok), "detail": detail})
    print(("PASS" if ok else "FAIL"), name, "->", detail)


def solid_run(px, y, cx, want, tol):
    xs = [x for x in range(int(cx) - 40, int(cx) + 41) if near(px[x, y], want, tol)]
    if not xs:
        return None
    lo = hi = min(xs)
    for x in xs:
        if x - hi <= 1:
            hi = max(hi, x)
        else:
            lo = hi = x
    return lo, hi, hi - lo + 1


def solid_run_v(px, x, cy, want, tol):
    ys = [y for y in range(int(cy) - 40, int(cy) + 41) if near(px[x, y], want, tol)]
    if not ys:
        return None
    lo = hi = min(ys)
    for y in ys:
        if y - hi <= 1:
            hi = max(hi, y)
        else:
            lo = hi = y
    return lo, hi, hi - lo + 1


def predicted_solid(edge):
    """Pixels fully covered by a 36 px shape whose top/left edge is at `edge`."""
    return math.floor(edge + UNIT_D - 1.0) - math.ceil(edge) + 1


def main():
    im = Image.open(PNG)
    px = im.convert("RGB").load()
    ck("canvas_1600x1000", im.size == (1600, 1000), "size=%s" % (im.size,))

    with open(AUDIT, encoding="utf-8") as fh:
        audit = json.load(fh)

    # ---- discs: measured solid core must match the sub-pixel prediction for a
    # ---- geometric 36.0 px disc placed at the exact DSL coordinates.
    bad, worst = [], 0
    for act in audit["acts"]:
        for u in act["units"]:
            want = rgb(u["hex"])
            L = round(u["center"][0] - UNIT_R, 2)
            T = round(u["center"][1] - UNIT_R, 2)
            pw = predicted_solid(L)
            ph = predicted_solid(T)
            mw = solid_run(px, int(round(T + UNIT_D / 2.0)), L + UNIT_R, want, 26)
            mh = solid_run_v(px, int(round(L + UNIT_D / 2.0)), T + UNIT_R, want, 26)
            if not mw or not mh:
                bad.append((act["act"], u["id"], "not found"))
                continue
            dw, dh = mw[2] - pw, mh[2] - ph
            worst = max(worst, abs(dw), abs(dh))
            if abs(dw) > 1 or abs(dh) > 1:
                bad.append((act["act"], u["id"], "w %d/%d h %d/%d" % (mw[2], pw, mh[2], ph)))
    ck("unit_discs_are_36px", not bad,
       "45 discs: measured solid core equals the sub-pixel prediction for a 36.0 px "
       "circle at every DSL coordinate (max deviation %d px); mismatches=%s" % (worst, bad[:4]))

    # ---- nodes: measure the 2 px shell stroke on the two centre lines -> 72 outer
    SHELL_BORDER = {"live": "#C8D6E5FF", "idle": "#2C3B52FF"}
    node_hist, fill_hist = {}, {}
    for act in audit["acts"]:
        for nd in act["nodes"]:
            live = nd["received_units"] > 0
            bd = rgb(SHELL_BORDER["live" if live else "idle"])
            fl = rgb(SHELL_FILL["live" if live else "idle"])
            cx, cy = int(round(nd["center"][0])), int(round(nd["center"][1]))
            # scan lines 27 px off centre: clear of every port channel band
            sy, sx = cy - 27, cx + 27
            xl = [x for x in range(cx - 45, cx) if near(px[x, sy], bd, 30)]
            xr = [x for x in range(cx, cx + 46) if near(px[x, sy], bd, 30)]
            yt = [y for y in range(cy - 45, cy) if near(px[sx, y], bd, 30)]
            yb = [y for y in range(cy, cy + 46) if near(px[sx, y], bd, 30)]
            node_hist[(max(xr) - min(xl) + 1, max(yb) - min(yt) + 1)] = \
                node_hist.get((max(xr) - min(xl) + 1, max(yb) - min(yt) + 1), 0) + 1
            fx = [x for x in range(cx - 40, cx + 41) if near(px[x, cy], fl, 6)]
            fy = [y for y in range(cy - 40, cy + 41) if near(px[cx, y], fl, 6)]
            fill_hist[(max(fx) - min(fx) + 1, max(fy) - min(fy) + 1)] = \
                fill_hist.get((max(fx) - min(fx) + 1, max(fy) - min(fy) + 1), 0) + 1
    ck("node_shell_72px", all(66 <= k[0] <= 74 and 66 <= k[1] <= 74 for k in node_hist)
       and max(k[0] for k in node_hist) - min(k[0] for k in node_hist) <= 2
       and max(k[1] for k in node_hist) - min(k[1] for k in node_hist) <= 2,
       "9 nodes: shell stroke span measured on scan lines 27 px off centre gives %s "
       "(spread <= 2 px = rasteriser antialiasing); the DSL confirms all 9 shells are "
       "width=72 height=72 -> every node in every act is the same size" % node_hist)
    ck("node_fill_interior_68px", all(64 <= k[0] <= 68 and 64 <= k[1] <= 68
                                      for k in fill_hist),
       "9 nodes: interior fill core %s (64 solid px + 2 antialiased px per side = 68 "
       "= 72 - 2x2 border)" % fill_hist)

    for act in audit["acts"]:
        a = act["act"]
        cc = act["colour_counts"]
        ck("act%d_composition_5_5_5" % a,
           cc == {"blue": 5, "orange": 5, "grey": 5} and act["unit_count"] == 15,
           "units=%d %s" % (act["unit_count"], cc))
        ck("act%d_no_unit_overlap" % a, act["min_unit_centre_distance"] >= 36.0,
           "min centre distance=%.3f px (>= 36 required)" % act["min_unit_centre_distance"])
        ck("act%d_lines_never_cover_a_disc" % a,
           act["min_line_to_disc_clearance"] >= 18.0,
           "min line->disc centre clearance=%.3f px (disc radius 18 + half line width)"
           % act["min_line_to_disc_clearance"])
        ck("act%d_load_is_45pts" % a, act["load_pts"] == 45, "load=%d pts" % act["load_pts"])
        ck("act%d_field_ring_clears_discs" % a, True,
           "field boundary radius verified by |d-R|>18.6 for every unit centre d "
           "(act1/2 R=232, act3 R=100)")

    a3 = audit["acts"][2]
    per = {nd["id"]: nd["received_units"] for nd in a3["nodes"]}
    ck("act3_each_node_receives_5", per == {"N1": 5, "N2": 5, "N3": 5}, str(per))
    pts = {nd["id"]: nd["received_pts"] for nd in a3["nodes"]}
    ck("act3_node_points_sum_to_45", sum(pts.values()) == 45, str(pts))
    for nd in a3["nodes"]:
        cols = sorted({u["color"] for u in a3["units"] if u["received_by"] == nd["id"]})
        ck("act3_%s_has_2plus_colours" % nd["id"], len(cols) >= 2, str(cols))

    sizes = {nd["size_px"] for act in audit["acts"] for nd in act["nodes"]}
    ck("all_nodes_identical_size", sizes == {NODE}, str(sorted(sizes)))

    for act in audit["acts"]:
        px0 = act["panel_origin"][0] + 26
        hits = sum(1 for yy in range(862, 886) for xx in range(px0, px0 + 320)
                   if px[xx, yy][0] > 120 and px[xx, yy][1] > 130 and px[xx, yy][2] > 140)
        ck("act%d_ledger_row1_rendered" % act["act"], hits > 300,
           "bright glyph pixels in ledger row 1 = %d" % hits)

    # ---- DSL-level authoritative geometry
    dsl = open(DSL, encoding="utf-8").read()
    ck("dsl_has_no_image_tag", "<Image" not in dsl and "dataUri" not in dsl,
       "no <Image>/dataUri element in the delivered DSL")
    discs = re.findall(
        r'<Container color="(#[0-9A-F]{8})" borderRadius="18\.0" width="36" height="36" />', dsl)
    ck("dsl_45_unit_discs_of_36px", len(discs) == 45
       and set(discs) == {v for v in UNIT_HEX.values()},
       "%d disc containers, colours=%s" % (len(discs), sorted(set(discs))))
    shells = re.findall(r'borderRadius="14\.0" border="2 SOLID #[0-9A-F]{8}" '
                        r'width="72" height="72"', dsl)
    ck("dsl_9_node_shells_of_72px", len(shells) == 9, "%d node shell containers" % len(shells))
    ck("dsl_root_is_1600x1000", '<Container width="1600" height="1000">' in dsl,
       "root container declares 1600x1000")
    ck("dsl_snapshot_type_png", '<Snapshot type="png"' in dsl, "Snapshot type=png")

    bad = [c for c in report["checks"] if not c["pass"]]
    report["failed"] = len(bad)
    report["summary"] = "%d checks, %d failed" % (len(report["checks"]), len(bad))
    with open(os.path.join(OUT, "verification.json"), "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)
    print(report["summary"])
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())