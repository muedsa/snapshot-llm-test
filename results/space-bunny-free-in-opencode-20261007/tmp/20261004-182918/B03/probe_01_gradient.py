"""Probe 01: gradient semantics.

Verifies: LINEAR/RADIAL/SWEEP, gradientStops, gradientTileMode
(REPEAT/MIRROR/DECAL), gradientBegin/End, gradientRotation, gradientCenter/
Radius, gradientFocal/FocalRadius, gradientStartAngle/EndAngle,
backgroundBlendMode, shape="CIRCLE", and the 8-digit #RRGGBBAA alpha order.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import probe_lib as P  # noqa: E402
import dsllib as D  # noqa: E402

W, H = 1400, 1330
BG = "#0B1020FF"
k = []
LBL = 15


def lab(x, y, s, color="#93A4C7FF", size=LBL, w=None, h=None):
    k.append(D.text_el(s, x=x, y=y, size=size, color=color,
                       w=w or D.est_width(s, size) + 6,
                       h=h or size * 1.4))


COL = 280
ROW = 210
GAP = 30
X0 = 40
Y0 = 56


def size1(s, sz):
    return D.est_lines(s, sz, COL - 34) * sz * 1.4


def cell(i, j, label, attrs, notes=None):
    x = X0 + j * (COL + GAP)
    y = Y0 + i * (ROW + GAP)
    k.append(D.box(x, y, COL, ROW, color="#FFFFFF08", radius=12,
                   border="1 SOLID #FFFFFF18"))
    a = dict(attrs)
    a["width"] = COL - 40
    a["height"] = ROW - 46
    inner = D.el("Container", a)
    k.append(D.el("Positioned", {"left": x + 20, "top": y + 14}, [inner]))
    lab(x + 20, y + ROW - 36, label, "#E2E8F0FF", 13,
        w=COL - 34, h=size1(label, 13))
    if notes:
        lab(x + 20, y + ROW - 14, notes, "#7C8BA8FF", 11, w=COL - 34)


# ---- row 0: LINEAR
cell(0, 0, 'LINEAR default (CENTER_LEFT->RIGHT)',
     {"gradientType": "LINEAR", "gradientColors": "#38BDF8FF,#F472B6FF"})
cell(0, 1, "LINEAR TOP_LEFT->BOTTOM_RIGHT + stops",
     {"gradientType": "LINEAR", "gradientColors": "#6750A4FF,#03DAC6FF,#FFC107FF",
      "gradientStops": "0,0.55,1", "gradientBegin": "TOP_LEFT",
      "gradientEnd": "BOTTOM_RIGHT"})
cell(0, 2, "LINEAR gradientRotation=1.5708",
     {"gradientType": "LINEAR", "gradientColors": "#22D3EEFF,#6366F1FF",
      "gradientRotation": "1.5707963268"})

# ---- row 1: tileMode
cell(1, 0, "LINEAR tileMode=REPEAT (stops 0,0.25)",
     {"gradientType": "LINEAR", "gradientColors": "#FDE68AFF,#FCA5A5FF",
      "gradientStops": "0,0.25", "gradientTileMode": "REPEAT"})
cell(1, 1, "LINEAR tileMode=MIRROR (stops 0,0.3)",
     {"gradientType": "LINEAR", "gradientColors": "#BBF7D0FF,#0EA5E9FF",
      "gradientStops": "0,0.3", "gradientTileMode": "MIRROR"})
cell(1, 2, "LINEAR tileMode=DECAL (stops 0,0.5)",
     {"gradientType": "LINEAR", "gradientColors": "#111827FF,#FDE047FF",
      "gradientStops": "0,0.5", "gradientTileMode": "DECAL"})

# ---- row 2: RADIAL
cell(2, 0, "RADIAL default center/radius .5",
     {"gradientType": "RADIAL", "gradientColors": "#FFFFFFFF,#60A5FAFF,#1E3A8AFF",
      "gradientStops": "0,0.35,1"})
cell(2, 1, "RADIAL focal (.5,.35) r .1 focalRadius .25",
     {"gradientType": "RADIAL", "gradientColors": "#FEF9C3FF,#F59E0BFF,#7C2D12FF",
      "gradientCenter": "(0.5,0.5)", "gradientRadius": "0.6",
      "gradientFocal": "(0.5,0.32)", "gradientFocalRadius": "0.22"})
cell(2, 2, 'RADIAL center=BOTTOM_LEFT radius=.85',
     {"gradientType": "RADIAL", "gradientColors": "#A78BFAFF,#312E81FF",
      "gradientCenter": "BOTTOM_LEFT", "gradientRadius": "0.85"})

# ---- row 3: SWEEP
cell(3, 0, "SWEEP default 0..2pi",
     {"gradientType": "SWEEP", "gradientColors": "#F87171FF,#FBBF24FF,#34D399FF,#60A5FAFF,#C084FCFF,#F87171FF"})
cell(3, 1, "SWEEP startAngle=1.0 endAngle=5.0",
     {"gradientType": "SWEEP", "gradientColors": "#0F172AFF,#38BDF8FF,#F8FAFCFF,#0F172AFF",
      "gradientStartAngle": "1.0", "gradientEndAngle": "5.0"})
cell(3, 2, "SWEEP + borderRadius 120 (arc inside pill)",
     {"gradientType": "SWEEP", "gradientColors": "#22D3EEFF,#A855F7FF,#F43F5EFF,#22D3EEFF",
      "borderRadius": "120"})

# ---- row 4: blend mode, shape, alpha order
cell(4, 0, "backgroundBlendMode=MULTIPLY over pink",
     {"color": "#EC4899FF", "gradientType": "LINEAR",
      "gradientColors": "#FDE047FF,#22D3EEFF",
      "backgroundBlendMode": "MULTIPLY", "borderRadius": "14"})
cell(4, 1, 'shape="CIRCLE" + radial',
     {"shape": "CIRCLE", "gradientType": "RADIAL",
      "gradientColors": "#FFFFFFFF,#FBBF24FF,#B45309FF"})
cell(4, 2, "8-hex alpha: #1E90FF00/.55/.FF",
     {"gradientType": "LINEAR", "gradientColors": "#1E90FF00,#1E90FF8C,#1E90FFFF",
      "gradientStops": "0,0.5,1"})

k.append(D.text_el("PROBE 01 · gradient family", x=40, y=18, size=20,
                   color="#F8FAFCFF", w=600, h=28, style="BOLD"))
k.append(D.text_el("BG behind cells = #0B1020FF (dark) to make blends visible",
                   x=X0 + 3 * (COL + GAP), y=18, size=12, color="#64748BFF",
                   w=500, h=18))

dsl = D.snapshot([D.stack(k, W, H)], W, H, bg=BG)
r = P.probe(dsl, "p01-gradient")
print("probe01", r.get("ok"), r.get("status"), r.get("error"))
for wn in D.warnings():
    print("WARN", wn)