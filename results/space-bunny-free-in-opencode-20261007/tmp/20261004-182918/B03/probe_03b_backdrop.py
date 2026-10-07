"""Probe 03b: BackdropFilter semantics, measured.

Probe 03 row 2 used a smooth SWEEP gradient as the backdrop, so blur could not
be observed by eye. Here the backdrop is a high-frequency 8-bar pattern, and
blur is measured as edge energy (sum |p(x+1)-p(x)|) across a fixed scanline.

Cases:
  A no filter, plain 55%-white plate       (control)
  B BackdropFilter sigma 6, no clip
  C BackdropFilter sigma 6 + ClipRRect
  D BackdropFilter sigma 18 + ClipRRect
  E ImageFiltered sigma 6 (for comparison - blurs the subtree)
  F BackdropFilter with NO backdrop behind it
  G BackdropFilter blendMode
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import probe_lib as P  # noqa: E402
import dsllib as D  # noqa: E402

W, H = 1900, 900
k = []
CW, CH = 230, 160
STEP = 250


def bars(x, y, w, h):
    pal = ["#111827FF", "#F8FAFCFF"]
    out = []
    n = 10
    for i in range(n):
        out.append(D.box(x + i * (w / n), y, w / n + 1, h,
                         color=pal[i % 2]))
    return out


def cell(j, label, plate_fn, with_bars=True):
    x = 40 + j * STEP
    y = 90
    k.append(D.box(x, y, CW, CH, color="#FFFFFF08", radius=8,
                   border="1 SOLID #FFFFFF1C"))
    kids = []
    if with_bars:
        kids.append(D.el("Container", {"width": CW - 20, "height": CH - 20,
                                       "borderRadius": "8"},
                          [D.el("Stack", {"fit": "LOOSE"},
                                bars(0, 0, CW - 20, CH - 20))]))
    kids.extend(plate_fn())
    k.append(D.el("Positioned", {"left": x + 10, "top": y + 10,
                                 "width": CW - 20, "height": CH - 20},
                  [D.el("Stack", {"fit": "LOOSE"}, kids)]))
    k.append(D.text_el(label, x=x, y=y + CH + 10, size=12,
                       color="#CBD5E1FF", w=STEP - 12,
                       h=D.est_lines(label, 12, STEP - 12) * 17))
    return x, y


def plate_plate():
    return [D.el("Positioned", {"left": 14, "top": 14, "width": CW - 48,
                                "height": CH - 48},
                  [D.el("Container", {"width": CW - 48, "height": CH - 48,
                                      "borderRadius": "10",
                                      "color": "#FFFFFF55"})])]


def bf_plate(sigma, clip=True, blend=None, tint="#FFFFFF55"):
    bf = {"sigmaX": sigma, "sigmaY": sigma}
    if blend:
        bf["blendMode"] = blend
    inner = D.el("BackdropFilter", bf,
                 [D.el("Container", {"width": CW - 48, "height": CH - 48,
                                     "color": tint})])
    node = D.el("ClipRRect", {"borderRadius": "10",
                              "clipBehavior": "ANTI_ALIAS"}, [inner]) \
        if clip else inner
    return [D.el("Positioned", {"left": 14, "top": 14, "width": CW - 48,
                                "height": CH - 48}, [node])]


def if_plate(sigma):
    return [D.el("Positioned", {"left": 14, "top": 14, "width": CW - 48,
                                "height": CH - 48},
                  [D.el("ClipRRect", {"borderRadius": "10"}, [
                      D.el("ImageFiltered", {"sigmaX": sigma,
                                             "sigmaY": sigma}, [
                          D.el("Container", {
                              "width": CW - 48, "height": CH - 48,
                              "color": "#FFFFFF55"})])])])]


cell(0, "A no filter (control)", plate_plate)
cell(1, "B BackdropFilter 6, no clip", lambda: bf_plate(6, clip=False))
cell(2, "C BackdropFilter 6 + ClipRRect", lambda: bf_plate(6, clip=True))
cell(3, "D BackdropFilter 18 + ClipRRect", lambda: bf_plate(18, clip=True))
cell(4, "E ImageFiltered 6 (blurs subtree)", lambda: if_plate(6))
cell(5, "F BackdropFilter 12, NO backdrop", lambda: bf_plate(12, clip=True),
     with_bars=False)
cell(6, "G BackdropFilter 10 blend SCREEN",
     lambda: bf_plate(10, clip=True, blend="SCREEN", tint="#FFFFFF33"))

k.append(D.text_el("PROBE 03b · BackdropFilter, measured", x=40, y=20,
                   size=20, color="#F8FAFCFF", w=800, h=28, style="BOLD"))
k.append(D.text_el("backdrop = 10 black/white bars; plate covers the middle "
                   "90% of the cell", x=40, y=46, size=12, color="#64748BFF",
                   w=1100, h=18))

# row 2: does BackdropFilter need a *sibling* painted before it in the same
# Stack, or does it read the whole canvas including the page background?
y2 = 340
k.append(D.text_el("row2: BackdropFilter sibling order — plate BEFORE the "
                   "bars vs AFTER", x=40, y=y2 - 34, size=14,
                   color="#94A3B8FF", w=1100, h=20))
for j, (label, bars_first) in enumerate([
        ("H bars painted first, plate after (normal)", True),
        ("I plate painted first, bars after", False)]):
    x = 40 + j * 400
    plate = D.el("BackdropFilter", {"sigmaX": 10, "sigmaY": 10},
                 [D.el("Container", {"width": CW - 48, "height": CH - 48,
                                     "color": "#FFFFFF55"})])
    bar_stack = D.el("Stack", {"fit": "LOOSE"},
                     bars(0, 0, CW - 20, CH - 20))
    ordered = ([D.el("Container", {"width": CW - 20, "height": CH - 20,
                                   "borderRadius": "8"}, [bar_stack]),
                D.el("Positioned", {"left": 14, "top": 14, "width": CW - 48,
                                    "height": CH - 48}, [plate])]
              if bars_first else
              [D.el("Positioned", {"left": 14, "top": 14, "width": CW - 48,
                                   "height": CH - 48}, [plate]),
               D.el("Container", {"width": CW - 20, "height": CH - 20,
                                  "borderRadius": "8"}, [bar_stack])])
    k.append(D.el("Positioned", {"left": x, "top": y2, "width": CW,
                                 "height": CH},
                  [D.el("Stack", {"fit": "LOOSE"}, ordered)]))
    k.append(D.text_el(label, x=x, y=y2 + CH + 10, size=12,
                       color="#CBD5E1FF", w=380,
                       h=D.est_lines(label, 12, 380) * 17))
    k.append(D.box(x, y2, CW, CH, color=None, border="1 SOLID #FFFFFF1C"))

dsl = D.snapshot([D.stack(k, W, H)], W, H, bg="#0B1020FF")
r = P.probe(dsl, "p03b-backdrop")
print("probe03b", r.get("ok"), r.get("status"), r.get("error"))

from PIL import Image  # noqa: E402
if r.get("ok"):
    im = Image.open(r["image"]).convert("RGB")

    def energy(x, y, cw, ch):
        """Sum of |dR|+|dG|+|dB| along a scanline: high = sharp edges."""
        tot = 0
        yy = y + ch // 2
        prev = im.getpixel((x, yy))
        for xx in range(x + 1, x + cw):
            cur = im.getpixel((xx, yy))
            tot += abs(cur[0] - prev[0]) + abs(cur[1] - prev[1]) \
                + abs(cur[2] - prev[2])
            prev = cur
        return tot

    for j, label in enumerate(["A no filter (control)",
                               "B BF6 no clip", "C BF6 + ClipRRect",
                               "D BF18 + ClipRRect", "E ImageFiltered 6",
                               "F BF12 no backdrop", "G BF10 SCREEN"]):
        x = 40 + j * STEP
        print("  %-26s edge_energy=%6d" % (label, energy(x + 10, 90,
                                                         CW - 20, CH - 20)))
    for j, label in enumerate(["H bars first", "I plate first"]):
        x = 40 + j * 400
        print("  %-26s edge_energy=%6d" % (label, energy(x + 10, y2,
                                                         CW - 20, CH - 20)))