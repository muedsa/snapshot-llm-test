"""Probe 02b (v2): what actually crops a rotated child?

v1 was invalid: the rotated plate FIT inside its slot, and the 'dark pixel'
threshold also matched the page background. Now the plate is deliberately larger
than the slot, and overflow is measured as plate-coloured pixels in a band
strictly outside the slot's right/bottom edges.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import probe_lib as P  # noqa: E402
import dsllib as D  # noqa: E402

W, H = 2200, 700
k = []
BW, BH = 200, 220
GAPX = 330
BG = (11, 16, 32)
PLATE = (52, 211, 153)   # #34D399
M = P.col_major(P.mat_rot(38))

# 300x300 plate rotated 38deg inside a 200x220 slot -> guaranteed overflow
inner = D.el("Positioned", {"left": -50, "top": -40, "width": 300,
                            "height": 300},
             [D.el("Transform", {"matrix": M, "alignment": "CENTER"},
                   [D.el("Container", {"width": 300, "height": 300,
                                       "color": "#34D399FF",
                                       "borderRadius": "10"})])])

VARIANTS = [
    ("A Stack HARD_EDGE", D.el("Stack", {"fit": "EXPAND",
                                    "clipBehavior": "HARD_EDGE"}, [inner])),
    ("B Stack NONE", D.el("Stack", {"fit": "EXPAND",
                                "clipBehavior": "NONE"}, [inner])),
    ("C ClipRect ANTI_ALIAS", D.el("ClipRect", {"clipBehavior": "ANTI_ALIAS"},
                                [D.el("Stack", {"fit": "EXPAND"}, [inner])])),
    ("D ClipRect HARD_EDGE", D.el("ClipRect", {"clipBehavior": "HARD_EDGE"},
                               [D.el("Stack", {"fit": "EXPAND"}, [inner])])),
    ("E ClipRRect r=24", D.el("ClipRRect", {"borderRadius": "24",
                                        "clipBehavior": "ANTI_ALIAS"},
                              [D.el("Stack", {"fit": "EXPAND"}, [inner])])),
    ("F Container clip+dec", D.el(
        "Container", {"width": BW, "height": BH, "clipBehavior": "HARD_EDGE",
                      "color": "#FFFFFF0A", "borderRadius": "12"},
        [D.el("Stack", {"fit": "EXPAND"}, [inner])])),
]

for j, (lab, widget) in enumerate(VARIANTS):
    x = 40 + j * (BW + GAPX)
    k.append(D.el("Positioned", {"left": x, "top": 60, "width": BW,
                                 "height": BH}, [widget]))
    k.append(D.text_el(lab, x=x, y=288, size=12, color="#CBD5E1FF", w=BW,
                       h=18))
    k.append(D.box(x, 60, BW, BH, color=None, border="2 SOLID #FF4D6DFF"))

k.append(D.text_el("PROBE 02b v2 · does the rotated child escape its slot?",
                   x=40, y=16, size=20, color="#F8FAFCFF", w=900, h=28,
                   style="BOLD"))
k.append(D.text_el("300x300 plate rotated 38deg in a 200x220 slot; "
                   "red line = slot border", x=40, y=42, size=12,
                   color="#64748BFF", w=900, h=18))

# ---- row 2: shadow inside a clip that is clearly tight
y2 = 340
for j, (lab, wrap) in enumerate([
        ("G shadow, no clip",
         D.el("Stack", {"fit": "EXPAND"}, [
             D.el("Positioned", {"left": 30, "top": 30, "width": 200,
                                 "height": 80},
                  [D.el("Container", {"width": 200, "height": 80,
                                      "color": "#F59E0BFF", "borderRadius": "12",
                                      "boxShadow": "0 8 22 0 #FF0000AA"})])])),
        ("H shadow inside tight ClipRect",
         D.el("ClipRect", {}, [
             D.el("Stack", {"fit": "EXPAND"}, [
                 D.el("Positioned", {"left": 30, "top": 30, "width": 200,
                                     "height": 80},
                      [D.el("Container", {"width": 200, "height": 80,
                                          "color": "#F59E0BFF",
                                          "borderRadius": "12",
                                          "boxShadow":
                                              "0 8 22 0 #FF0000AA"})])])])),
]):
    x = 40 + j * 400
    k.append(D.el("Positioned", {"left": x, "top": y2, "width": 340,
                                 "height": 170}, [wrap]))
    k.append(D.text_el(lab, x=x, y=y2 + 176, size=12, color="#CBD5E1FF",
                       w=340, h=18))
    k.append(D.box(x, y2, 340, 170, color=None, border="2 SOLID #FF4D6DFF"))

dsl = D.snapshot([D.stack(k, W, H)], W, H, bg="#0B1020FF")
r = P.probe(dsl, "p02b2-clip")
print("probe02b2", r.get("ok"), r.get("status"), r.get("error"))

from PIL import Image  # noqa: E402
if r.get("ok"):
    im = Image.open(r["image"]).convert("RGB")
    for j, (lab, _) in enumerate(VARIANTS):
        x = 40 + j * (BW + GAPX)
        # band strictly to the RIGHT of the slot (x0 .. x+BW .. x+BW+23)
        right = im.crop((x + BW + 1, 61, x + BW + 22, 60 + BH - 1))
        below = im.crop((x + 1, 60 + BH + 1, x + BW - 1, 60 + BH + 22))
        out = sum(1 for p in list(right.getdata()) + list(below.getdata())
                  if abs(p[0] - PLATE[0]) < 26 and abs(p[1] - PLATE[1]) < 26
                  and abs(p[2] - PLATE[2]) < 26)
        print("  %-24s escaped_px=%d -> %s" % (lab, out,
                                                "CLIPPED" if out == 0 else "ESCAPES"))
    for j, lab in enumerate(["G shadow, no clip", "H shadow tight ClipRect"]):
        x = 40 + j * 400
        band = im.crop((x + 1, y2 + 1, x + 339, y2 + 169))
        red = sum(1 for p in band.getdata()
                  if p[0] > 120 and p[1] < 90 and p[2] < 90)
        print("  %-24s shadow_px_inside_slot=%d" % (lab, red))