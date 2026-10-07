"""Probe 02c (v2): does a clip widget crop a child's boxShadow?

v1 was inconclusive: the slot was larger than card+shadow, so nothing escaped.
Here the clip slot is EXACTLY the card bounds (200x70), so any unclipped shadow
must appear outside it.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import probe_lib as P  # noqa: E402
import dsllib as D  # noqa: E402

W, H = 2050, 620
k = []
CW, CH = 200, 70          # clip slot == card size, shadow must escape
SH = "0 12 30 0 #FF0000CC"


def card(color="#F59E0BFF", sh=SH):
    return D.el("Container", {"width": CW, "height": CH, "color": color,
                              "borderRadius": "10", "boxShadow": sh})


def wrap_clip(kind, extra=None, color="#F59E0BFF", sh=SH):
    inner = D.el("Stack", {"fit": "LOOSE"}, [card(color, sh)])
    if kind == "none":
        return inner
    a = {"width": CW, "height": CH}
    a.update(extra or {})
    return D.el(kind, a, [inner])


CASES = [
    ("A no clip at all (baseline)", wrap_clip("none"),
     "#FF0000CC"),
    ("B Stack fit=EXPAND HARD_EDGE",
     D.el("Stack", {"fit": "LOOSE", "clipBehavior": "HARD_EDGE"},
          [card("#38BDF8FF")]), "#FF0000CC"),
    ("C ClipRect default",
     wrap_clip("ClipRect"), "#FF0000CC"),
    ("D ClipRect HARD_EDGE",
     wrap_clip("ClipRect", {"clipBehavior": "HARD_EDGE"}), "#FF0000CC"),
    ("E ClipRRect r=10",
     wrap_clip("ClipRRect", {"borderRadius": "10"}), "#FF0000CC"),
    ("F ClipOval (no radius attrs)",
     wrap_clip("ClipOval"), "#FF0000CC"),
]

STEP = 330
for j, (lab, widget, hue) in enumerate(CASES):
    x = 40 + j * STEP
    y = 80
    # place the widget in its own 200x70 Positioned so it gets tight bounds
    k.append(D.el("Positioned", {"left": x, "top": y, "width": CW,
                                 "height": CH}, [widget]))
    k.append(D.text_el(lab, x=x, y=y + CH + 12, size=11, color="#CBD5E1FF",
                       w=STEP - 10, h=30))
    k.append(D.box(x, y, CW, CH, color=None, border="2 SOLID #FFFFFF66"))

k.append(D.text_el("PROBE 02c v2 · clip slot == card bounds (200x70)",
                   x=40, y=18, size=20, color="#F8FAFCFF", w=800, h=28,
                   style="BOLD"))
k.append(D.text_el("shadow = 0 12 30 0 red80 ; any red halo outside the white "
                   "outline means NOT cropped", x=40, y=46, size=12,
                   color="#64748BFF", w=1100, h=18))

dsl = D.snapshot([D.stack(k, W, H)], W, H, bg="#0B1020FF")
r = P.probe(dsl, "p02c2-shadowclip")
print("probe02c2", r.get("ok"), r.get("status"), r.get("error"))

from PIL import Image  # noqa: E402
if r.get("ok"):
    im = Image.open(r["image"]).convert("RGB")
    for j, (lab, _, _) in enumerate(CASES):
        x = 40 + j * STEP
        y = 80
        bands = [(x + 2, y - 40, x + CW - 2, y - 1),
                 (x + 2, y + CH + 1, x + CW - 2, y + CH + 40),
                 (x - 40, y + 2, x - 1, y + CH - 2),
                 (x + CW + 1, y + 2, x + CW + 40, y + CH - 2)]
        tot = 0
        for b in bands:
            for p in im.crop(b).getdata():
                if p[0] > 70 and p[0] - p[1] > 40 and p[0] - p[2] > 40:
                    tot += 1
        print("  %-30s shadow_px_outside=%5d -> %s"
              % (lab, tot, "CROPPED" if tot == 0 else "ESCAPES"))