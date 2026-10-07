"""Probe 03: filters, blend modes, opacity.

Verifies:
  * ImageFiltered gaussian blur (sigmaX/sigmaY, tileMode) + auto output bounds
  * BackdropFilter: does it read what is BEHIND it? does it need a clip?
  * ColorFiltered blend modes over a known backdrop
  * Opacity semantics (subtree compositing) and Interaction with blend modes
  * The FAQ claim that MULTIPLY / SRC tint transparent gaps inside the bounds
  * foregroundColor/foreground* text painting
  * backToFront ordering: is a later sibling drawn on top (normal Z order)?
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import probe_lib as P  # noqa: E402
import dsllib as D  # noqa: E402

W, H = 2000, 1700
k = []
CW, CH = 200, 150
COLS = 5


def slot(x, y, w, h):
    k.append(D.box(x, y, w, h, color="#FFFFFF0A", radius=8,
                   border="1 SOLID #FFFFFF1C"))


def cap(x, y, s, w=190, color="#94A3B8FF", size=11):
    k.append(D.text_el(s, x=x, y=y, size=size, color=color, w=w,
                       h=D.est_lines(s, size, w) * (size * 1.35)))


def X0(c):
    return 40 + c * 230


def Y0(r):
    return 70 + r * 230


# ---------- Row 1: ImageFiltered blur strength + tileMode
def swatches(n, w=200, h=120):
    """Colour bars as the blur source so blur is measurable."""
    pal = ["#F87171FF", "#FBBF24FF", "#34D399FF", "#60A5FAFF", "#C084FCFF",
           "#F472B6FF", "#22D3EEFF", "#FDE047FF"]
    out = []
    for i in range(n):
        out.append(D.box(i * (w / n), 0, w / n + 1, h,
                         color=pal[i % len(pal)]))
    return out


for j, (lab, sx, sy, tm) in enumerate([
        ("ImageFiltered sigma 0,0 (control)", 0, 0, "CLAMP"),
        ("ImageFiltered sigma 2,2", 2, 2, "CLAMP"),
        ("ImageFiltered sigma 8,8", 8, 8, "CLAMP"),
        ("ImageFiltered sigma 24,24", 24, 24, "CLAMP"),
        ("ImageFiltered sigma 40x4 (aniso)", 40, 4, "CLAMP")]):
    src = D.el("Container", {"width": CW - 20, "height": CH - 20,
                              "borderRadius": "8"},
               [D.el("Stack", {"fit": "LOOSE"}, swatches(5, CW - 20, CH - 20))])
    widget = D.el("ImageFiltered", {"sigmaX": sx, "sigmaY": sy,
                                    "tileMode": tm}, [src])
    slot(X0(j), Y0(0), CW, CH)
    k.append(D.el("Positioned", {"left": X0(j) + 10, "top": Y0(0) + 10,
                                 "width": CW - 20, "height": CH - 20},
                  [widget]))
    cap(X0(j), Y0(0) + CH + 8, lab)

# ---------- Row 2: BackdropFilter reads the backdrop?
# each cell: gradient background, then a BackdropFilter plate with a tint
for j, (lab, use_bf, has_clip, tint) in enumerate([
        ("BackdropFilter no clip", True, False, "#FFFFFF55"),
        ("BackdropFilter + ClipRRect", True, True, "#FFFFFF55"),
        ("BackdropFilter + Container plate", True, "plate", "#FFFFFF33"),
        ("plain semi plate (no filter)", False, True, "#FFFFFF55"),
        ("BackdropFilter sigma 18", True, True, "#FFFFFF44")]):
    sigma = 18 if "18" in lab else 8
    x, y = X0(j), Y0(1)
    slot(x, y, CW, CH)
    # background gradient (the thing a BackdropFilter should read)
    bg = D.el("Container", {
        "width": CW - 20, "height": CH - 20, "borderRadius": "8",
        "gradientType": "SWEEP",
        "gradientColors": "#F87171FF,#FBBF24FF,#34D399FF,#60A5FAFF,"
                          "#C084FCFF,#F87171FF"})
    stack_kids = [bg]
    if use_bf:
        plate = D.el("BackdropFilter", {"sigmaX": sigma, "sigmaY": sigma},
                     [D.el("Container", {"width": CW - 60, "height": CH - 60,
                                         "color": tint})])
        if has_clip is True:
            inner = D.el("ClipRRect", {"borderRadius": "10",
                                       "clipBehavior": "ANTI_ALIAS"}, [plate])
            stack_kids.append(D.el("Positioned",
                                   {"left": 10, "top": 10, "width": CW - 40,
                                    "height": CH - 40}, [inner]))
        elif has_clip == "plate":
            stack_kids.append(D.el("Positioned",
                                   {"left": 10, "top": 10, "width": CW - 40,
                                    "height": CH - 40},
                                   [D.el("ClipRRect",
                                         {"borderRadius": "10"}, [plate])]))
        else:
            stack_kids.append(D.el("Positioned",
                                   {"left": 20, "top": 20, "width": CW - 60,
                                    "height": CH - 60}, [plate]))
    else:
        stack_kids.append(D.el("Positioned",
                               {"left": 10, "top": 10, "width": CW - 40,
                                "height": CH - 40},
                               [D.el("Container",
                                     {"width": CW - 40, "height": CH - 40,
                                      "borderRadius": "10",
                                      "color": tint})]))
    st = D.el("Stack", {"fit": "LOOSE"}, stack_kids)
    k.append(D.el("Positioned", {"left": x + 10, "top": y + 10,
                                 "width": CW - 20, "height": CH - 20}, [st]))
    cap(x, y + CH + 8, lab)

# ---------- Row 3: ColorFiltered blend modes over a fixed mid-grey backdrop
MODES = ["MULTIPLY", "SCREEN", "OVERLAY", "DARKEN", "LIGHTEN", "PLUS",
         "DIFFERENCE", "EXCLUSION", "HUE", "SATURATION", "COLOR", "LUMINOSITY"]
BACK = "#808080FF"
SRC = "#FF6B35FF"   # orange
for i, mode in enumerate(MODES):
    r, c = 2 + i // COLS, i % COLS
    x, y = X0(c), Y0(r)
    slot(x, y, CW, CH)
    filt = D.el("ColorFiltered", {"color": SRC, "blendMode": mode},
                [D.el("Container", {"width": CW - 20, "height": CH - 20,
                                    "color": BACK, "borderRadius": "8"})])
    k.append(D.el("Positioned", {"left": x + 10, "top": y + 10,
                                 "width": CW - 20, "height": CH - 20}, [filt]))
    cap(x, y + CH + 8, "ColorFiltered " + mode)

# ---------- Row 4: Opacity + MULTIPLY over transparent gaps
y = Y0(4)
for j, (lab, kids_fn) in enumerate([
        ("Opacity .5 over gradient",
         lambda: [D.el("Opacity", {"opacity": "0.5"}, [
             D.el("Container", {"width": CW - 20, "height": CH - 20,
                                 "color": "#F87171FF"})])]),
        ("MULTIPLY over transparent gap",
         lambda: [D.el("ColorFiltered", {"color": "#F87171FF",
                                         "blendMode": "MULTIPLY"},
                       [D.el("Container", {"width": CW - 20,
                                           "height": CH - 20,
                                           "color": None})])]),
        ("MULTIPLY on transparent bg (no color)",
         lambda: [D.el("ColorFiltered", {"color": "#38BDF8FF",
                                         "blendMode": "MULTIPLY"},
                       [D.el("Container", {"width": CW - 20,
                                           "height": CH - 20,
                                           "color": "#10B981FF"})])]),
        ("Opacity .35 nested x2 (.12)",
         lambda: [D.el("Opacity", {"opacity": "0.35"}, [
             D.el("Opacity", {"opacity": "0.35"}, [
                 D.el("Container", {"width": CW - 20, "height": CH - 20,
                                     "color": "#FDE047FF"})])])]),
        ("Opacity 1.5 (out of range)",
         lambda: [D.el("Opacity", {"opacity": "1.0"}, [
             D.el("Container", {"width": CW - 20, "height": CH - 20,
                                 "color": "#F43F5EFF"})])]),
        ("Opacity 0 (invisible)",
         lambda: [D.el("Opacity", {"opacity": "0"}, [
             D.el("Container", {"width": CW - 20, "height": CH - 20,
                                 "color": "#F43F5EFF"})])]),
        ("Container opacity=.5 attr",
         lambda: [D.el("Container", {"width": CW - 20, "height": CH - 20,
                                     "opacity": "0.5",
                                     "color": "#F43F5EFF"})]),
]):
    x = X0(j)
    slot(x, y, CW, CH)
    inner = D.el("Stack", {"fit": "LOOSE"}, [
        D.el("Container", {
            "width": CW - 20, "height": CH - 20,
            "gradientType": "LINEAR",
            "gradientColors": "#0EA5E9FF,#F472B6FF"}),
    ] + kids_fn())
    k.append(D.el("Positioned", {"left": x + 10, "top": y + 10,
                                 "width": CW - 20, "height": CH - 20},
                  [inner]))
    cap(x, y + CH + 8, lab)

k.append(D.text_el("PROBE 03 · filters, blend modes, opacity", x=40, y=20,
                   size=20, color="#F8FAFCFF", w=700, h=28, style="BOLD"))
k.append(D.text_el("row3 backdrop = #808080 grey, filter colour = #FF6B35 "
                   "orange; row2 background is a SWEEP gradient",
                   x=40, y=44, size=12, color="#64748BFF", w=1200, h=18))

dsl = D.snapshot([D.stack(k, W, H)], W, H, bg="#0B1020FF")
r = P.probe(dsl, "p03-filter")
print("probe03", r.get("ok"), r.get("status"), r.get("error"))
for wn in D.warnings():
    print("WARN", wn)