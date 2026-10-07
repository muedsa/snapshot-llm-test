"""A19 pixel audit: measure the rendered PNGs against scene-data.json.

Verifies (independently of the DSL text) that
  * each body's coloured pixels actually occupy its declared bbox,
  * each ring's hole really is half the outer diameter,
  * every id label is present and sits below its body,
  * nothing leaks into the occlusion covers.
"""
from __future__ import annotations

import json
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
OUT = os.path.join(ROOT, "outputs", RUN, "A19")
TMP = os.path.join(ROOT, "tmp", RUN, "A19")
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite"))

HEX = {"blue": (37, 99, 235), "orange": (234, 88, 12),
       "green": (22, 163, 74), "purple": (124, 58, 237)}
NEAR = 24


def near(px, ref, tol=NEAR):
    return all(abs(px[i] - ref[i]) <= tol for i in range(3))


def rgb_hex(rgb):
    return "#%02X%02X%02X" % rgb


def in_segment(p, a, b, tol=6):
    """True when p is within tol of the straight line segment a-b in RGB."""
    ab = [b[i] - a[i] for i in range(3)]
    ap = [p[i] - a[i] for i in range(3)]
    lab2 = sum(x * x for x in ab)
    if lab2 == 0:
        return max(abs(ap[i]) for i in range(3)) <= tol
    t = sum(ap[i] * ab[i] for i in range(3)) / float(lab2)
    t = max(0.0, min(1.0, t))
    proj = [a[i] + t * ab[i] for i in range(3)]
    return max(abs(p[i] - proj[i]) for i in range(3)) <= tol


def main():
    from PIL import Image

    scene = json.load(open(os.path.join(OUT, "scene-data.json"), encoding="utf-8"))
    occ = json.load(open(os.path.join(OUT, "occlusion-scene-data.json"), encoding="utf-8"))
    im = Image.open(os.path.join(OUT, "grid-scene.png")).convert("RGB")
    px = im.load()
    res = []

    def ck(name, ok, detail=""):
        res.append({"check": name, "pass": bool(ok), "detail": str(detail)})
        print("%-4s %-52s %s" % ("PASS" if ok else "FAIL", name, detail))

    print("=== grid bodies measured from the rendered pixels ===")
    bad_bbox, bad_ring, bad_label, bad_fill = [], [], [], []
    for o in scene["objects"]:
        bb = o["bbox"]
        x0, y0 = int(bb["x_min"]), int(bb["y_min"])
        x1, y1 = int(bb["x_max"]), int(bb["y_max"])
        ref = HEX[o["color"]]
        cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
        s = o["size"]
        # centre of a filled body must be the body colour; of a ring it must be the hole
        if o["shape"] == "ring":
            if not near(px[cx, cy], (255, 255, 255), 10):
                bad_ring.append((o["id"], "hole not white at centre", px[cx, cy]))
        elif not near(px[cx, cy], ref):
            bad_fill.append((o["id"], px[cx, cy]))
        # sample well INSIDE the painted band on each of the four sides.
        # For a ring the painted band is stroke=size/4 thick, so step in by size/8.
        inset = s // 8 if o["shape"] == "ring" else (s // 4)
        probes = ((x0 + inset, cy), (x1 - 1 - inset, cy),
                  (cx, y0 + inset), (cx, y1 - 1 - inset))
        for ex, ey in probes:
            if not near(px[ex, ey], ref):
                bad_bbox.append((o["id"], (ex, ey), px[ex, ey]))
        # the bbox must be tight: no body colour 3px outside on any side
        for ox, oy in ((x0 - 3, cy), (x1 + 2, cy), (cx, y0 - 3), (cx, y1 + 2)):
            if near(px[ox, oy], ref, 14):
                bad_bbox.append((o["id"], "bbox not tight", (ox, oy), px[ox, oy]))
        # the label band below the body must contain dark glyph pixels and no body colour
        lb = o["id_label"]["bbox"]
        band = [px[x, y] for y in range(int(lb["y_min"]) + 2, int(lb["y_min"]) + 24, 2)
                for x in range(int(lb["x_min"]) + 55, int(lb["x_max"]) - 55, 2)]
        dark = sum(1 for p in band if sum(p) < 340)
        if dark < 20:
            bad_label.append((o["id"], "dark px %d of %d" % (dark, len(band))))
        if any(near(p, ref, 40) for p in band):
            bad_fill.append((o["id"], "body colour inside the label band"))
    ck("all 64 bodies are body-coloured just inside their bbox on all 4 sides", not bad_bbox,
       bad_bbox[:4])
    ck("all 16 ring holes are white at the centre", not bad_ring, bad_ring[:3])
    ck("filled bodies (48 of them) are body-coloured at the centre", not bad_fill,
       bad_fill[:4])
    ck("no body colour appears inside its own label band", not bad_fill)
    ck("every id label renders dark glyph pixels below its body", not bad_label,
       bad_label[:4])

    print("\n=== ring outer/inner diameter measured in pixels ===")
    for o in scene["objects"]:
        if o["shape"] != "ring":
            continue
        bb = o["bbox"]
        cy = int((bb["y_min"] + bb["y_max"]) / 2)
        ref = HEX[o["color"]]
        row = [px[x, cy] for x in range(int(bb["x_min"]) - 4, int(bb["x_max"]) + 4)]
        on = [i for i, p in enumerate(row) if near(p, ref)]
        outer = (on[-1] - on[0] + 1) if on else 0
        gap = [i for i in range(on[0], on[-1]) if not near(row[i], ref)] if on else []
        inner = (gap[-1] - gap[0] + 1) if gap else 0
        exp_o, exp_i = o["size"], o["size"] // 2
        ck("%s ring outer=%d inner=%d" % (o["id"], outer, inner),
           abs(outer - exp_o) <= 2 and abs(inner - exp_i) <= 2,
           "expected outer=%d inner=%d" % (exp_o, exp_i))

    print("\n=== occlusion covers leak check ===")
    io = Image.open(os.path.join(OUT, "occlusion.png")).convert("RGB")
    op = io.load()
    HEXO = {"blue": (37, 99, 235), "orange": (234, 88, 12),
            "green": (22, 163, 74), "purple": (124, 58, 237)}
    # every colour that any hidden body could contribute
    hidden_cols = set()
    for b in occ["hidden_set_A__occlusion_png"]:
        for name, rgb in HEXO.items():
            if b["color"].lower().endswith(rgb_hex(rgb).lower()):
                hidden_cols.add(rgb)
    ck("collected the 4 possible hidden-body colours", len(hidden_cols) == 4,
       str(sorted(hidden_cols)))
    cov1, cov2 = occ["covers"]
    for c in (cov1, cov2):
        fill = tuple(int(c["fill"][i:i + 2], 16) for i in (1, 3, 5))
        bb = c["bbox"]
        leaks = []
        flat = set()
        for x in range(int(bb["x_min"]) + 4, int(bb["x_max"]) - 4):
            for y in range(int(bb["y_min"]) + 4, int(bb["y_max"]) - 4):
                p = op[x, y]
                if any(near(p, hc, 30) for hc in hidden_cols):
                    leaks.append((x, y, p))
                flat.add(p)
        ck("%s interior contains no pixel of any hidden-body colour" % c["name"],
           not leaks, "%d leaks %s" % (len(leaks), leaks[:3]))
        # Every interior pixel must be either the flat fill, or an anti-aliased blend
        # lying on a straight line between the fill and one of the two label text
        # colours (the label is drawn straight on top of the fill). Text rasterisation
        # uses gamma-corrected blending, hence the generous 26/255 tolerance.
        tri = [fill, (248, 250, 252), (182, 194, 210)]
        stray = [p for p in flat
                 if not any(in_segment(p, a, b, tol=26) for a in tri for b in tri)]
        ck("%s interior is flat fill + label anti-aliasing only" % c["name"],
           not stray, "%d stray colours %s" % (len(stray), stray[:4]))
        ck("%s interior colour count is consistent with flat fill + 2 texts" % c["name"],
           len(flat) <= 400, "%d distinct colours" % len(flat))

    npass = sum(1 for r in res if r["pass"])
    print("\n==== %d / %d pixel checks passed ====" % (npass, len(res)))
    with open(os.path.join(TMP, "pixel-audit.json"), "w", encoding="utf-8",
              newline="\n") as fh:
        json.dump({"task_id": "A19", "checks_total": len(res),
                   "checks_passed": npass, "all_passed": npass == len(res),
                   "checks": res}, fh, ensure_ascii=False, indent=2)
    return 0 if npass == len(res) else 1


if __name__ == "__main__":
    sys.exit(main())
