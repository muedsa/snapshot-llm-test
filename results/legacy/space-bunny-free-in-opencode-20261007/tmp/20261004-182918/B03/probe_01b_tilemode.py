"""Probe 01b: does gradientTileMode repeat?

Probe 01 showed REPEAT/MIRROR/DECAL with default begin/end produced a single
non-repeating ramp. Hypothesis: Skia's repeat/mirror only becomes visible when
the gradient vector is shorter than the painted box (t spans > 1).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import probe_lib as P  # noqa: E402
import dsllib as D  # noqa: E402

W, H = 1300, 820
k = []
COL, ROW, GAP, X0, Y0 = 380, 150, 30, 40, 76


def lab(x, y, s, color="#93A4C7FF", size=14):
    k.append(D.text_el(s, x=x, y=y, size=size, color=color,
                       w=D.est_width(s, size) + 8, h=size * 1.4))


def cell(i, j, label, attrs):
    x = X0 + j * (COL + GAP)
    y = Y0 + i * (ROW + GAP + 18)
    k.append(D.box(x, y, COL, ROW, color="#FFFFFF08", radius=10,
                   border="1 SOLID #FFFFFF18"))
    a = dict(attrs)
    a["width"] = COL - 24
    a["height"] = ROW - 20
    k.append(D.el("Positioned", {"left": x + 12, "top": y + 10},
                  [D.el("Container", a)]))
    lab(x + 12, y + ROW + 2, label)


G2 = ["#FDE68AFF", "#F43F5EFF"]

# Row 0: vector exactly spans the box (default)
cell(0, 0, "CLAMP default begin/end (vector spans box)",
     {"gradientType": "LINEAR", "gradientColors": ",".join(G2)})
cell(0, 1, "REPEAT default begin/end (vector spans box)",
     {"gradientType": "LINEAR", "gradientColors": ",".join(G2),
      "gradientTileMode": "REPEAT"})
cell(0, 2, "MIRROR default begin/end (vector spans box)",
     {"gradientType": "LINEAR", "gradientColors": ",".join(G2),
      "gradientTileMode": "MIRROR"})

# Row 1: short vector = (0.1,0.5)->(0.22,0.5) on a wide box => t spans ~8x
SHORT = {"gradientBegin": "(0.1,0.5)", "gradientEnd": "(0.22,0.5)"}
cell(1, 0, "CLAMP short vector t>1 (clamps to last)",
     dict({"gradientType": "LINEAR", "gradientColors": ",".join(G2)}, **SHORT))
cell(1, 1, "REPEAT short vector (hypothesis: repeats)",
     dict({"gradientType": "LINEAR", "gradientColors": ",".join(G2),
           "gradientTileMode": "REPEAT"}, **SHORT))
cell(1, 2, "MIRROR short vector (hypothesis: reflects)",
     dict({"gradientType": "LINEAR", "gradientColors": ",".join(G2),
           "gradientTileMode": "MIRROR"}, **SHORT))

# Row 2: very short vector + stops, DECAL
cell(2, 0, "DECAL short vector stops 0,0.25",
     dict({"gradientType": "LINEAR", "gradientColors": ",".join(G2),
           "gradientStops": "0,0.25", "gradientTileMode": "DECAL"}, **SHORT))
cell(2, 1, "REPEAT short vector + stops 0,0.25",
     dict({"gradientType": "LINEAR", "gradientColors": ",".join(G2),
           "gradientStops": "0,0.25", "gradientTileMode": "REPEAT"}, **SHORT))
cell(2, 2, "SWEEP 2 cycles via stops 0,0.5 MIRROR",
     {"gradientType": "SWEEP",
      "gradientColors": "#22D3EEFF,#F472B6FF,#22D3EEFF",
      "gradientStops": "0,0.5,1", "gradientTileMode": "MIRROR"})

k.append(D.text_el("PROBE 01b · gradientTileMode repeat semantics", x=40, y=20,
                   size=20, color="#F8FAFCFF", w=700, h=28, style="BOLD"))
k.append(D.text_el("gradient vector (0.1,0.5)->(0.22,0.5) is 12% of box width",
                   x=40, y=44, size=13, color="#64748BFF", w=800, h=18))

dsl = D.snapshot([D.stack(k, W, H)], W, H, bg="#0B1020FF")
r = P.probe(dsl, "p01b-tilemode")
print("probe01b", r.get("ok"), r.get("status"), r.get("error"))