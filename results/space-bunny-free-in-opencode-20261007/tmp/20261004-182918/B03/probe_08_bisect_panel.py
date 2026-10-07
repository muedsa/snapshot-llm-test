"""Probe 08: bisect why nested panel content shifted by the panel origin.

Case-01 v1 rendered every panel's inner content at canvas coordinates
(+panel.x, +panel.y) although probe-07 variant A (Positioned > Container >
Stack(EXPAND) > Positioned) was exact. This script renders the compass panel
alone, then progressively smaller slices of it, measuring the amber arrow
head (#FCD34D) top-left each time.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wlib as W  # noqa: E402
from PIL import Image  # noqa: E402

D = W.D
el, box = W.el, W.box

PX, PY, PW, PH = 40, 116, 420, 560
FW, FH = 136, 210
ccx, ccy = PX + PW / 2.0, PY + 322
ARROW = [
    el("Positioned",
       {"left": round(ccx - FW / 2, 2), "top": round(ccy - FH / 2, 2),
        "width": FW, "height": FH},
       [el("Transform",
          {"matrix": W.P.col_major(W.P.mat_rot(212.0)), "alignment": "CENTER"},
          [el("Container", {"width": FW, "height": FH},
             [el("Stack", {"fit": "LOOSE"}, [
                 D.polygon([(FW / 2, 10), (FW / 2 + 22, 54),
                            (FW / 2 - 22, 54)], "#FCD34DFF")])])])]),
]
MARK = [
    el("Positioned",
       {"left": round(ccx - 9, 2), "top": round(ccy - 9, 2),
        "width": 18, "height": 18},
       [el("Container", {"width": 18, "height": 18, "shape": "CIRCLE",
                         "color": "#22D3EEFF"})]),
]
TICK1 = [box(ccx - 152, ccy - 1, 2, 30, color="#64748BFF")]
TEXT1 = [W.t2("W", PX + 28, PY + 24, size=17, color=W.INK, w=44, h=26)]

SETS = [
    ("arrow only", ARROW),
    ("mark only", MARK),
    ("tick only", TICK1),
    ("text only", TEXT1),
    ("arrow+mark+tick+text", ARROW + MARK + TICK1 + TEXT1),
]

EXPECT = {
    "arrow only": None,
    "mark only": (ccx - 9, ccy - 9),
    "tick only": (ccx - 152, ccy - 14),
    "text only": (PX + 28, PY + 24),
}

for name, kids in SETS:
    dsl = D.snapshot([D.stack([W.panel(PX, PY, PW, PH, kids)], 1600, 1000)],
                     1600, 1000, bg=W.BG)
    r = W.P.probe(dsl, "p08-" + name.replace(" ", "-").replace("+", "and"))
    print("%-22s ok=%s %s" % (name, r.get("ok"), (r.get("error") or "")[:120]))
    if not r.get("ok"):
        continue
    im = Image.open(r["image"]).convert("RGB")
    px = im.load()
    target = (252, 211, 77) if "arrow" in name else (
        (34, 211, 238) if "mark" in name else (
            (100, 116, 139) if "tick" in name else (241, 245, 249)))
    best = None
    for y in range(0, 1000):
        for x in range(0, 1600):
            p = px[x, y]
            if (abs(p[0] - target[0]) < 24 and abs(p[1] - target[1]) < 24
                    and abs(p[2] - target[2]) < 24):
                if best is None or (x + y) < (best[0] + best[1]):
                    best = (x, y)
    print("   first px %s  expected %s" % (best, EXPECT.get(name)))
    for w in D.warnings():
        print("   WARN", w)
    D.WARNINGS.clear()