# -*- coding: utf-8 -*-
"""Verify the final A20 render by pixels:

  1. every anchor pixel shows the point colour (strict position mapping),
  2. every label's text ink lies inside its plate with >=2px margins
     (i.e. no CLIP truncation),
  3. leader strokes are present where polylines are declared.

Writes tmp/run-20261011-01/A20/gen/measure-a20.json.
"""
import json
import math
import pathlib

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[4]
GEN = ROOT / "tmp/run-20261011-01/A20/gen"
OUT = ROOT / "outputs/run-20261011-01/A20"

lay = json.loads((OUT / "label-layout.json").read_text(encoding="utf-8"))
im = Image.open(GEN / "annotated-map-07.png").convert("RGB")
px = im.load()
assert im.size == (1600, 1100), im.size

POINT_RGB = (0x25, 0x63, 0xEB)
TEXT_RGB = (0x1E, 0x29, 0x3B)
TOL_C = 45
TOL_T = 60
MARGIN_MIN = 2.0


def near(c, t, tol):
    return all(abs(c[i] - t[i]) < tol for i in range(3))


anchor_fail = []
ink_results = []
for m in lay["markers"]:
    ax, ay = m["anchor_px"]
    sx, sy = int(round(ax)), int(round(ay))
    c = px[sx, sy]
    if not near(c, POINT_RGB, TOL_C):
        anchor_fail.append((m["id"], [sx, sy], list(c)))

    b = m["label_box"]
    l, t, r, btm = b
    minx = miny = 10 ** 9
    maxx = maxy = -10 ** 9
    n = 0
    for y in range(int(t) + 1, int(btm)):
        for x in range(int(l) + 1, int(r)):
            if near(px[x, y], TEXT_RGB, TOL_T):
                n += 1
                minx, miny = min(minx, x), min(miny, y)
                maxx, maxy = max(maxx, x), max(maxy, y)
    if n == 0:
        ink_results.append({"id": m["id"], "ink_pixels": 0, "ok": False})
        continue
    margins = {"left": round(minx - l, 2), "top": round(miny - t, 2),
               "right": round(r - maxx - 1, 2), "bottom": round(btm - maxy - 1, 2)}
    ok = all(v >= MARGIN_MIN for v in margins.values())
    ink_results.append({"id": m["id"], "ink_pixels": n,
                        "ink_bbox": [minx, miny, maxx + 1, maxy + 1],
                        "margins_px": margins, "no_clip": ok})

# leader stroke presence: sample mid-point of each leader segment
leader_checks = []
for m in lay["markers"]:
    if not m["leader_polyline_px"]:
        continue
    pts = m["leader_polyline_px"]
    ok = True
    samples = []
    for i in range(len(pts) - 1):
        a, bb = pts[i], pts[i + 1]
        mx, my = (a[0] + bb[0]) / 2, (a[1] + bb[1]) / 2
        c = px[int(round(mx)), int(round(my))]
        hit = near(c, (0x64, 0x74, 0x8B), TOL_C)
        samples.append({"mid": [round(mx, 2), round(my, 2)],
                        "rgb": list(c), "stroke_found": hit})
        ok = ok and hit
    leader_checks.append({"id": m["id"], "segments": len(pts) - 1,
                          "samples": samples, "ok": ok})

doc = {
    "png": "tmp/run-20261011-01/A20/gen/annotated-map-07.png",
    "tolerances": {"point_colour": TOL_C, "text_colour": TOL_T,
                   "ink_margin_min_px": MARGIN_MIN},
    "anchors_checked": len(lay["markers"]),
    "anchor_pixel_matches": len(lay["markers"]) - len(anchor_fail),
    "anchor_failures": anchor_fail,
    "labels_checked": len(ink_results),
    "labels_no_clip": sum(1 for r in ink_results if r.get("no_clip")),
    "ink_results": ink_results,
    "leader_checks": leader_checks,
}
(GEN / "measure-a20.json").write_text(
    json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print("anchors matched: %d/%d" % (doc["anchor_pixel_matches"],
                                  doc["anchors_checked"]))
print("labels no-clip: %d/%d" % (doc["labels_no_clip"], doc["labels_checked"]))
for r in ink_results:
    if not r.get("no_clip"):
        print("  CLIP?", r)
for lc in leader_checks:
    print("leader", lc["id"], "segments", lc["segments"], "ok", lc["ok"])
assert not anchor_fail, anchor_fail
assert doc["labels_no_clip"] == doc["labels_checked"]
assert all(lc["ok"] for lc in leader_checks)
print("ALL PIXEL CHECKS PASSED")
