"""Probe 02: Transform 4x4 matrix semantics.

Verifies: rotate / scale / skew / perspective(m[2][3]) / translate-in-matrix,
origin, alignment, and whether a transformed child can exceed its layout box
(the "does not participate in parent layout" rule from the docs).
Also verifies Stack clipBehavior="NONE" is required for non-clipped overflow.

Layout rule learned the hard way: Positioned must be a DIRECT child of
Stack/IndexedStack, so the Positioned wrapper goes OUTSIDE Transform.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import probe_lib as P  # noqa: E402
import dsllib as D  # noqa: E402

W, H = 1440, 1200
k = []
CW, CH = 200, 130


def plate(w, h, color="#38BDF8FF", text=""):
    """A plain Container (no Positioned) used as the Transform child."""
    kids = []
    if text:
        kids.append(D.el("Text", {"color": "#0B1020FF", "fontSize": 13,
                                  "fontFamily": D.UI, "textAlign": "CENTER",
                                  "text": text}))
    return D.el("Container", {"width": w, "height": h, "color": color,
                              "borderRadius": "6"}, kids)


def cell(x, y, label, matrix, notes=None, cellw=CW, cellh=CH,
         origin="(0,0)", alignment=None, pw=None, ph=None):
    """Positioned (outer) > Transform > Container (inner)."""
    k.append(D.box(x, y, cellw, cellh, color="#FFFFFF0A", radius=10,
                   border="1 SOLID #FFFFFF1C"))
    w = pw if pw is not None else cellw - 44
    h = ph if ph is not None else cellh - 40
    pa = {"left": x + (cellw - w) / 2.0, "top": y + (cellh - h) / 2.0,
          "width": w, "height": h}
    ta = {"matrix": matrix, "origin": origin}
    if alignment:
        ta["alignment"] = alignment
    k.append(D.el("Positioned", pa,
                  [D.el("Transform", ta, [plate(w, h)])]))
    k.append(D.text_el(label, x=x + 12, y=y + cellh + 4, size=12,
                       color="#CBD5E1FF", w=cellw - 8,
                       h=D.est_lines(label, 12, cellw - 8) * 17))
    if notes:
        k.append(D.text_el(notes, x=x + 12, y=y + cellh + 22, size=11,
                           color="#64748BFF", w=cellw - 8,
                           h=D.est_lines(notes, 11, cellw - 8) * 15))


k.append(D.text_el("PROBE 02 · Transform 4x4 matrix", x=40, y=20, size=20,
                   color="#F8FAFCFF", w=700, h=28, style="BOLD"))

# -- row 1: rotations
R = [(0, "identity"), (15, "rot 15 CCW"), (45, "rot 45 CCW"), (90, "rot 90 CCW"),
     (-30, "rot -30 (CW)"), (180, "rot 180")]
for i, (deg, lab) in enumerate(R):
    cell(40 + i * 232, 70, lab, P.col_major(P.mat_rot(deg)),
         alignment="CENTER", pw=150, ph=90)

# -- row 2: origin + alignment variants, all 45 deg
y2 = 290
cell(40, y2, "rot45 alignment=CENTER origin=(0,0)",
     P.col_major(P.mat_rot(45)), alignment="CENTER")
cell(272, y2, "rot45 alignment=TOP_LEFT origin=(0,0)",
     P.col_major(P.mat_rot(45)), origin="(0,0)", alignment="TOP_LEFT")
cell(504, y2, "rot45 alignment=CENTER origin=(40,0)",
     P.col_major(P.mat_rot(45)), origin="(40,0)", alignment="CENTER")
cell(736, y2, "rot45 alignment unset (child top-left origin)",
     P.col_major(P.mat_rot(45)))
cell(968, y2, "rot45 alignment=BOTTOM_RIGHT origin=(0,-30)",
     P.col_major(P.mat_rot(45)), origin="(0,-30)", alignment="BOTTOM_RIGHT")

# -- row 3: scale / skew / perspective
y3 = 510
cell(40, y3, "scale 1.4x / 0.7y", P.col_major(P.mat_scale(1.4, 0.7)),
     alignment="CENTER")
cell(272, y3, "skewX 25deg", P.col_major(P.mat_skew(25)), alignment="CENTER")
cell(504, y3, "skewX 25 + skewY 15", P.col_major(P.mat_skew(25, 15)),
     alignment="CENTER")
cell(736, y3, "persp m[2][3]=0.0035 x rot20",
     P.col_major(P.mat_mul(P.mat_persp(0.0035), P.mat_rot(20))),
     "m[2][3]!=0 => foreshortening", alignment="CENTER", pw=150, ph=110)
cell(968, y3, "translate(30,20) in matrix only",
     P.col_major(P.mat_translate(30, 20)))

# -- row 4: Stack clipBehavior vs rotated child
y4 = 760
for j, (fit, cb) in enumerate([("EXPAND", "HARD_EDGE"), ("EXPAND", "NONE"),
                               ("LOOSE", "HARD_EDGE")]):
    x = 40 + j * 440
    k.append(D.box(x, y4, 420, 200, color="#FFFFFF08", radius=12,
                   border="1 SOLID #FFFFFF1C"))
    m = P.col_major(P.mat_rot(35))
    rot = D.el("Positioned",
               {"left": 40, "top": 30, "width": 340, "height": 140},
               [D.el("Transform", {"matrix": m, "alignment": "CENTER"},
                     [plate(340, 140, "#34D399FF")])])
    st = D.el("Stack", {"fit": fit, "clipBehavior": cb}, [rot])
    k.append(D.el("Positioned", {"left": x, "top": y4, "width": 420,
                                 "height": 200}, [st]))
    k.append(D.text_el("Stack fit=%s clipBehavior=%s" % (fit, cb), x=x + 12,
                       y=y4 + 208, size=13, color="#CBD5E1FF", w=410, h=20))

k.append(D.text_el("read: HARD_EDGE cuts rotated corners; NONE lets them bleed",
                   x=40, y=1005, size=13, color="#64748BFF", w=1200, h=20))
k.append(D.text_el("read: Transform is paint-only - parent layout still uses "
                   "the untransformed box", x=40, y=1030, size=13,
                   color="#64748BFF", w=1200, h=20))

dsl = D.snapshot([D.stack(k, W, H)], W, H, bg="#0B1020FF")
r = P.probe(dsl, "p02-transform")
print("probe02", r.get("ok"), r.get("status"), r.get("error"))
for wn in D.warnings():
    print("WARN", wn)