"""Probe 07: coordinate space of Positioned inside a nested Stack.

The first case-01 render put every panel's inner content at canvas coordinates
instead of panel-local coordinates. Two candidate structures:

  A  Positioned > Container(decorated) > Stack(EXPAND) > Positioned
  B  Positioned > Stack(EXPAND) > Positioned        (Container placed as a
     sibling fill so the panel background still exists)

Each cell prints a crosshair whose local (30,30) must land at panel+(30,30).
A red rule marks the expected spot; a visible offset means the coordinate
space is wrong.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wlib as W  # noqa: E402

D = W.D
el, t2, box = W.el, W.t2, W.box

Wc, Hc = 1100, 420
PX, PY, PW, PH = 200, 140, 300, 200
k = []

# expected marker in canvas coords
k.append(box(PX + 30, PY + 30, 2, 40, color="#FF0000FF"))
k.append(box(PX + 30, PY + 30, 40, 2, color="#FF0000FF"))

# variant A
inner = [
    box(30, 30, 90, 50, color="#38BDF8FF", radius=6),
    t2("A", 30, 92, size=14, color=W.INK),
]
k.append(el("Positioned", {"left": PX, "top": PY, "width": PW, "height": PH},
            [el("Container", {"width": PW, "height": PH, "color": "#111A2EFF",
                              "borderRadius": "20", "border": "1 SOLID #1E293BFF"},
               [el("Stack", {"fit": "EXPAND"}, inner)])]))

# variant B: Stack directly under Positioned, background as a sibling
innerB = [
    box(0, 0, PW, PH, color="#111A2EFF", radius=20,
        border="1 SOLID #1E293BFF"),
    box(30, 30, 90, 50, color="#34D399FF", radius=6),
    t2("B", 30, 92, size=14, color=W.INK),
]
k.append(el("Positioned", {"left": 580, "top": PY, "width": PW, "height": PH},
            [el("Stack", {"fit": "EXPAND"}, innerB)]))
k.append(box(580 + 30, PY + 30, 2, 40, color="#FF0000FF"))
k.append(box(580 + 30, PY + 30, 40, 2, color="#FF0000FF"))

# variant C: Container > Stack fit=LOOSE
innerC = [
    box(30, 30, 90, 50, color="#FBBF24FF", radius=6),
    t2("C", 30, 92, size=14, color=W.INK),
]
k.append(el("Positioned", {"left": 580, "top": 20, "width": PW, "height": PH},
            [el("Container", {"width": PW, "height": PH, "color": "#111A2EFF"},
               [el("Stack", {"fit": "LOOSE"}, innerC)])]))

k.append(t2("PROBE 07 · 嵌套 Stack 的坐标系", 40, 20, size=19, color=W.INK,
            style="BOLD", w=700, h=26))
k.append(t2("红线 = 期望落点 (panel+30, panel+30)。A/B/C 三种结构各画一个"
            " 90x50 的方块，方块左上角应压住红线拐点。", 40, 48, size=12,
            color=W.INK3, w=1000, h=18))
k.append(t2("A  Positioned > Container > Stack(EXPAND)", 200, PY + PH + 8,
            size=11, color="#7DD3FCFF", w=400, h=16))
k.append(t2("B  Positioned > Stack(EXPAND) + 背景兄弟节点", 580, PY + PH + 8,
            size=11, color="#7DD3FCFF", w=400, h=16))
k.append(t2("C  Positioned > Container > Stack(LOOSE)", 580, 20 + PH + 8,
            size=11, color="#7DD3FCFF", w=400, h=16))

dsl = D.snapshot([D.stack(k, Wc, Hc)], Wc, Hc, bg=W.BG)
r = W.P.probe(dsl, "p07-nested-stack-coords")
print("probe07", r.get("ok"), r.get("status"), (r.get("error") or "")[:200])

if r.get("ok"):
    from PIL import Image
    im = Image.open(r["image"]).convert("RGB")

    def probe_px(x, y, w, h):
        """Top-leftmost pixel of the test colour inside the given rect."""
        best = None
        for yy in range(max(0, y - 200), min(im.size[1], y + h + 40)):
            for xx in range(max(0, x - 200), min(im.size[0], x + w + 40)):
                p = im.getpixel((xx, yy))
                if (abs(p[0] - 0x38) < 30 and abs(p[1] - 0xBD) < 30
                        and abs(p[2] - 0xF8) < 30):
                    if best is None or (xx + yy) < (best[0] + best[1]):
                        best = (xx, yy)
        return best

    a = probe_px(PX, PY, PW, PH)
    print("  A sky-blue block top-left =", a, "expected", (PX + 30, PY + 30))
    g = probe_px(580, PY, PW, PH)
    print("  B green block  top-left =", g, "expected", (580 + 30, PY + 30))
    y = probe_px(580, 20, PW, PH)
    print("  C amber block  top-left =", y, "expected", (580 + 30, 20 + 30))