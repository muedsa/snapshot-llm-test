"""Probe 05: shadows, corner radii, alpha hex, and Stack/Flex composition.

Sections:
  A ELEVATION_ names and custom shadow syntax (incl. spreadRadius, blurStyle)
  B four independent corner radii + asymmetric border sides
  C 8-digit #RRGGBBAA alpha ladder composited over a colour field
  D Flex: Row/Column mainAxisAlignment/crossAxisAlignment, Expanded, Flexible,
    Spacer, mainAxisSize, textBaseline
  E Stack: fit variants, alignment, IndexedStack index
  F overflow: OverflowBox / SizedOverflowBox / SizedBox / AspectRatio /
    FractionallySizedBox
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import probe_lib as P  # noqa: E402
import dsllib as D  # noqa: E402

W, H = 1560, 3060
k = []
SEC = [40]


def sec(t, note=""):
    k.append(D.text_el(t, x=40, y=SEC[0], size=15, color="#7DD3FCFF",
                       w=1200, h=22, style="BOLD"))
    if note:
        k.append(D.text_el(note, x=40, y=SEC[0] + 22, size=11,
                           color="#64748BFF", w=1400, h=16))
        SEC[0] += 24
    SEC[0] += 30


def cap(x, y, s, w=200, size=11, color="#7DD3FCFF"):
    k.append(D.text_el(s, x=x, y=y, size=size, color=color, w=w,
                       h=D.est_lines(s, size, w) * size * 1.35))


# ---------------- A: shadows ----------------
sec("A · boxShadow: ELEVATION names, custom syntax, spreadRadius, blurStyle")
ELEV = ["ELEVATION_0", "ELEVATION_1", "ELEVATION_2", "ELEVATION_4",
        "ELEVATION_8", "ELEVATION_16", "ELEVATION_24"]
for i, e in enumerate(ELEV):
    x = 60 + i * 210
    y = SEC[0]
    k.append(D.box(x, y, 170, 92, color="#F1F5F9FF", radius=16, shadow=e))
    cap(x, y + 100, e)
CUSTOM = [
    ("0 2 6 0 #00000033", "small, no spread"),
    ("0 4 12 4 #00000044", "spread +4 grows the shadow"),
    ("0 4 12 -4 #00000044", "spread -4 shrinks it"),
    ("8 8 20 0 #F43F5E66", "offset xy, coloured"),
    ("0 0 0 6 #38BDF866", "zero blur, spread ring"),
    ("0 4 10 0 #00000055 NORMAL,0 1 2 0 #00000088", "two shadows"),
    ("0 4 10 0 #00000044 INNER", "blurStyle=INNER"),
    ("0 4 10 0 #00000044 OUTER", "blurStyle=OUTER"),
    ("0 4 10 0 #00000044 SOLID", "blurStyle=SOLID"),
]
for i, (sh, note) in enumerate(CUSTOM):
    col, row = i // 5, i % 5
    x = 60 + col * 480
    y = SEC[0] + row + 130
    k.append(D.box(x, y, 170, 80, color="#F1F5F9FF", radius=14, shadow=sh))
    cap(x + 180, y + 4, sh, w=290)
    cap(x + 180, y + 22, note, w=290, size=10, color="#94A3B8FF")
SEC[0] += 130 + 5 * 96 + 20

# ---------------- B: radii + asymmetric borders ----------------
sec("B · independent corner radii and per-side borders")
RADII = [
    {"borderRadius": "40"},
    {"borderRadiusTopLeft": "48", "borderRadiusBottomRight": "48"},
    {"borderRadiusTopLeft": "60", "borderRadiusTopRight": "8",
     "borderRadiusBottomLeft": "8", "borderRadiusBottomRight": "60"},
    {"borderRadiusTopLeft": "0", "borderRadiusBottomLeft": "56"},
]
for i, r in enumerate(RADII):
    x = 60 + i * 230
    y = SEC[0]
    k.append(D.box(x, y, 190, 120, color="#0EA5E9FF", extra=r))
    cap(x, y + 126, str(r)[:56], w=220)
BORD = [
    {"border": "5 SOLID #F59E0BFF"},
    {"borderTop": "5 SOLID #F59E0BFF"},
    {"borderLeft": "5 SOLID #F59E0BFF", "borderRight": "5 SOLID #F59E0BFF"},
    {"borderTop": "8 SOLID #EF4444FF", "borderBottom": "8 SOLID #EF4444FF"},
]
for i, b in enumerate(BORD):
    x = 1000 + i * 230
    y = SEC[0]
    k.append(D.box(x, y, 190, 120, color="#111827FF", extra=b))
    cap(x, y + 126, str(b)[:56], w=220)
SEC[0] += 170

# ---------------- C: alpha ladder ----------------
sec("C · 8-digit #RRGGBBAA alpha composited over a colour field",
    "top swatch row is the reference colour; below it the same hue at "
    "alpha 00 22 44 66 88 AA CC FF")
FIELD = "#F59E0BFF"
k.append(D.box(60, SEC[0], 190, 60, color=FIELD, radius=8))
cap(60, SEC[0] + 64, "reference #F59E0BFF", w=190)
ALPHAS = ["00", "22", "44", "66", "88", "AA", "CC", "FF"]
for i, a in enumerate(ALPHAS):
    x = 270 + i * 150
    k.append(D.box(x, SEC[0], 130, 60,
                   color="#0F172AFF", radius=8))
    k.append(D.box(x, SEC[0], 130, 60,
                   color="#F59E0B" + a, radius=8))
    cap(x, SEC[0] + 64, "#F59E0B" + a, w=140)
# second field to show blending with a busy background
k.append(D.box(60, SEC[0] + 110, 1170, 46, radius=8,
               gradient={"gradientType": "LINEAR",
                         "gradientColors": "#38BDF8FF,#F472B6FF,#34D399FF"}))
cap(60, SEC[0] + 160, "over a gradient field", w=300)
for i, a in enumerate(ALPHAS):
    x = 270 + i * 150
    k.append(D.box(x, SEC[0] + 110, 130, 46, color="#F59E0B" + a, radius=0))
    cap(x, SEC[0] + 160, "#F59E0B" + a, w=140)
SEC[0] += 210

# ---------------- D: Flex ----------------
sec("D · Flex: alignment, Expanded / Flexible / Spacer, mainAxisSize")


def flex_demo(title, widget, w=560, h=90):
    global SEC
    x = 60 + ((SEC[0] // 200) % 2) * 620
    y = SEC[0] + ((SEC[0] // 200) // 2) * 130
    k.append(D.el("Positioned", {"left": x, "top": y, "width": w, "height": h},
                  [D.el("Container", {"width": w, "height": h,
                                      "color": "#FFFFFF08",
                                      "border": "1 SOLID #FFFFFF1C"},
                        [widget])]))
    cap(x, y + h + 4, title, w=w - 4, size=11)


def bar(color, w=60, h=40, tag="Container"):
    return D.el(tag, {"width": w, "height": h, "color": color})


FLEX = [
    ("Row SPACE_BETWEEN",
     D.el("Row", {"mainAxisAlignment": "SPACE_BETWEEN"},
          [bar("#F87171FF"), bar("#FBBF24FF"), bar("#34D399FF")])),
    ("Row SPACE_AROUND",
     D.el("Row", {"mainAxisAlignment": "SPACE_AROUND"},
          [bar("#F87171FF"), bar("#FBBF24FF"), bar("#34D399FF")])),
    ("Row SPACE_EVENLY",
     D.el("Row", {"mainAxisAlignment": "SPACE_EVENLY"},
          [bar("#F87171FF"), bar("#FBBF24FF"), bar("#34D399FF")])),
    ("Row crossAxisAlignment=START",
     D.el("Row", {"crossAxisAlignment": "START"},
          [bar("#F87171FF", 60, 20), bar("#FBBF24FF", 60, 60),
           bar("#34D399FF", 60, 40)])),
    ("Column mainAxisAlignment=CENTER",
     D.el("Column", {"mainAxisAlignment": "CENTER"},
          [bar("#F87171FF", 40, 18), bar("#FBBF24FF", 40, 18)])),
    ("Column verticalDirection=UP",
     D.el("Column", {"verticalDirection": "UP"},
          [bar("#F87171FF", 40, 20), bar("#FBBF24FF", 40, 20)])),
    ("Row Expanded flex=2 + Flexible flex=1",
     D.el("Row", {}, [
         D.el("Expanded", {"flex": 2}, [bar("#60A5FAFF", 0, 40)]),
         D.el("Flexible", {"flex": 1, "fit": "TIGHT"},
              [bar("#A78BFAFF", 0, 40)])])),
    ("Row Spacer flex=1",
     D.el("Row", {}, [bar("#F87171FF"), D.el("Spacer", {"flex": 1}),
                     bar("#34D399FF")])),
    ("Row mainAxisSize=MIN (left aligned)",
     D.el("Row", {"mainAxisSize": "MIN"},
          [bar("#F87171FF"), bar("#FBBF24FF")])),
    ("Column mainAxisSize=MIN",
     D.el("Column", {"mainAxisSize": "MIN"},
          [bar("#F87171FF", 40, 20), bar("#FBBF24FF", 40, 20)])),
    ("Row crossAxisAlignment=BASELINE",
     D.el("Row", {"crossAxisAlignment": "BASELINE",
                  "textBaseline": "ALPHABETIC"},
          [D.el("Text", {"text": "big", "fontSize": 40,
                         "fontFamily": D.LATIN, "color": "#F8FAFCFF"}),
           D.el("Text", {"text": "small", "fontSize": 16,
                         "fontFamily": D.LATIN, "color": "#94A3B8FF"})])),
    ("Row textDirection=RTL",
     D.el("Row", {"textDirection": "RTL"},
          [bar("#F87171FF", 80, 40), bar("#FBBF24FF", 80, 40)])),
]
grid_top = SEC[0]
for i, (title, widget) in enumerate(FLEX):
    col, row = i % 2, i // 2
    x = 60 + col * 740
    y = grid_top + row * 130
    k.append(D.el("Positioned", {"left": x, "top": y, "width": 700,
                                 "height": 96},
                  [D.el("Container", {"width": 700, "height": 96,
                                      "color": "#FFFFFF08",
                                      "border": "1 SOLID #FFFFFF1C"},
                        [widget])]))
    cap(x, y + 100, title, w=700, size=11)
SEC[0] += ((len(FLEX) + 1) // 2) * 130 + 20

# ---------------- E: Stack / IndexedStack ----------------
sec("E · Stack fit / alignment and IndexedStack index")
STACKS = [
    ("Stack fit=LOOSE alignment=TOP_RIGHT",
     D.el("Stack", {"fit": "LOOSE", "alignment": "TOP_RIGHT"},
          [bar("#F87171FF", 80, 30), bar("#34D399FF", 120, 30)])),
    ("Stack fit=EXPAND alignment=BOTTOM_LEFT",
     D.el("Stack", {"fit": "EXPAND", "alignment": "BOTTOM_LEFT"},
          [bar("#F87171FF", 80, 30), bar("#34D399FF", 120, 30)])),
    ("Stack alignment=(0.8,-0.6) custom",
     D.el("Stack", {"fit": "LOOSE", "alignment": "(0.8,-0.6)"},
          [bar("#F87171FF", 80, 30), bar("#34D399FF", 120, 30)])),
    ("IndexedStack index=1",
     D.el("IndexedStack", {"index": 1, "fit": "LOOSE",
                           "alignment": "CENTER"},
          [bar("#F87171FF", 160, 60), bar("#34D399FF", 160, 60)])),
    ("IndexedStack index=0",
     D.el("IndexedStack", {"index": 0, "fit": "LOOSE",
                           "alignment": "CENTER"},
          [bar("#F87171FF", 160, 60), bar("#34D399FF", 160, 60)])),
    ("Stack non-Positioned siblings all align",
     D.el("Stack", {"fit": "LOOSE", "alignment": "CENTER"},
          [bar("#F87171FF", 90, 24), bar("#FBBF24FF", 90, 24)])),
]
grid_top = SEC[0]
for i, (title, widget) in enumerate(STACKS):
    col, row = i % 2, i // 2
    x = 60 + col * 740
    y = grid_top + row * 130
    k.append(D.el("Positioned", {"left": x, "top": y, "width": 700,
                                 "height": 96},
                  [D.el("Container", {"width": 700, "height": 96,
                                      "color": "#FFFFFF08",
                                      "border": "1 SOLID #FFFFFF1C"},
                        [widget])]))
    cap(x, y + 100, title, w=700, size=11)
SEC[0] += ((len(STACKS) + 1) // 2) * 130 + 20

# ---------------- F: overflow / ratio ----------------
sec("F · OverflowBox, SizedOverflowBox, AspectRatio, FractionallySizedBox")
OVER = [
    ("OverflowBox alignment=TOP_RIGHT child bigger",
     D.el("OverflowBox", {"alignment": "TOP_RIGHT"},
          [D.el("Container", {"width": 260, "height": 120,
                              "color": "#F59E0BFF"})]), 300, 100),
    ("SizedOverflowBox 160x100, child 260x120",
     D.el("SizedOverflowBox", {"width": 160, "height": 100,
                               "alignment": "BOTTOM_RIGHT"},
          [D.el("Container", {"width": 260, "height": 120,
                              "color": "#60A5FAFF"})]), 300, 100),
    ("AspectRatio 2.0 inside 200x200",
     D.el("AspectRatio", {"aspectRatio": 2.0},
          [D.el("Container", {"color": "#34D399FF"})]), 200, 200),
    ("AspectRatio 0.5 inside 200x200",
     D.el("AspectRatio", {"aspectRatio": 0.5},
          [D.el("Container", {"color": "#C084FCFF"})]), 200, 200),
    ("FractionallySizedBox wFactor .5 hFactor .25",
     D.el("FractionallySizedBox", {"widthFactor": 0.5,
                                   "heightFactor": 0.25,
                                   "alignment": "CENTER"},
          [D.el("Container", {"width": 120, "height": 40,
                              "color": "#38BDF8FF"})]), 200, 200),
    ("ConstrainedBox maxWidth 80 shrinks child",
     D.el("ConstrainedBox", {"maxWidth": 80},
          [D.el("Container", {"width": 200, "height": 60,
                              "color": "#FB7185FF"})]), 300, 100),
]
grid_top = SEC[0]
for i, (title, widget, ww, hh) in enumerate(OVER):
    col, row = i % 3, i // 3
    x = 60 + col * 500
    y = grid_top + row * 250
    k.append(D.el("Positioned", {"left": x, "top": y, "width": ww,
                                 "height": hh},
                  [D.el("Container", {"width": ww, "height": hh,
                                      "color": "#FFFFFF08",
                                      "border": "1 SOLID #FFFFFF1C"},
                        [widget])]))
    cap(x, y + hh + 6, title, w=ww + 60, size=11)
SEC[0] += ((len(OVER) + 2) // 3) * 250 + 20

k.append(D.text_el("PROBE 05 · shadows, radii, alpha, Flex, Stack, overflow",
                   x=40, y=8, size=18, color="#F8FAFCFF", w=1100, h=26,
                   style="BOLD"))

dsl = D.snapshot([D.stack(k, W, H)], W, H, bg="#0B1020FF")
r = P.probe(dsl, "p05-compose")
print("probe05", r.get("ok"), r.get("status"), r.get("error"), "usedH=", SEC[0])
for wn in D.warnings():
    print("WARN", wn)