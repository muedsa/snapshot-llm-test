"""probe-01: Transform rotation direction, clipping, gradients, opacity, filters.

Renders one 1200x760 sheet whose geometry is fully predetermined, so reading the PNG
answers every open DSL question at once (see probe/README.md for the answers).
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sk import Sk, CJK, MONO, SERIF  # noqa: E402

TMP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(TMP, "dsl", "probe-01.snapshot")

W, H = 1200, 780
s = Sk(W, H, "#0B1220FF")
s.box(0, 0, W, 56, "#111C2EFF")
s.text(24, 16, "PROBE-01  rotation / clip / gradient / text metrics", 22, "#7DD3FCFF", "BOLD")

# --- A. rotation direction: 0/90/180/270 about a fixed anchor -----------------
ax, ay = 210, 250
s.circle(ax, ay, 8, "#F8FAFCFF")
s.text(24, 92, "A  rect_at(deg) about centre (210,250)", 18, "#94A3B8FF")
# each bar is 150x18, centre offset so the four rotations are distinguishable
s.rect_at(ax, ay, 150, 18, 0, "#64748BFF", radius=9)
s.rect_at(ax, ay, 150, 18, 90, "#EF4444FF", radius=9)
s.rect_at(ax, ay, 150, 18, 180, "#22C55EFF", radius=9)
s.rect_at(ax, ay, 150, 18, 270, "#3B82F6FF", radius=9)
s.text(24, 380, "grey=0 red=90 green=180 blue=270", 16, "#64748BFF", family=MONO)

# --- B. asymmetric mark rotated, to separate "cw" from "ccw" ------------------
bx, by = 200, 560
s.text(24, 430, "B  L-mark: vertical leg DOWN at 0deg", 18, "#94A3B8FF")
s.rect_at(bx, by, 24, 120, 0, "#F59E0BFF", radius=4)
s.rect_at(bx, by - 48, 96, 24, 0, "#F59E0BFF", radius=4)
s.rect_at(bx + 200, by, 24, 120, 90, "#F59E0BFF", radius=4)
s.rect_at(bx + 200 - 48, by, 96, 24, 90, "#F59E0BFF", radius=4)

# --- C. ClipRRect vs Container clipBehavior ----------------------------------
s.text(470, 92, "C  clipping", 18, "#94A3B8FF")
s.box(470, 120, 200, 120, "#1E293BFF", radius=16)
inner = ('<Positioned left="-40" top="-30"><Container width="280" height="200" '
         'gradientType="LINEAR" gradientColors="#38BDF8,#A78BFA,#F472B6" '
         'gradientBegin="TOP_LEFT" gradientEnd="BOTTOM_RIGHT"/></Positioned>')
s.raw(f'<Positioned left="470" top="120"><ClipRRect borderRadius="16">'
      f'<Stack alignment="TOP_LEFT">{inner}</Stack></ClipRRect></Positioned>')
s.text(470, 248, "ClipRRect 16", 15, "#64748BFF", family=MONO)
img2 = ('<Positioned left="-40" top="-30"><Container width="280" height="200" '
        'color="#F97316FF"/></Positioned>')
s.raw(f'<Positioned left="700" top="120"><Container width="200" height="120" '
      f'borderRadius="16" clipBehavior="ANTI_ALIAS">'
      f'<Stack alignment="TOP_LEFT">{img2}</Stack></Container></Positioned>')
s.text(700, 248, "Container clip ANTI_ALIAS", 15, "#64748BFF", family=MONO)

# --- D. gradients + opacity ---------------------------------------------------
s.text(470, 300, "D  gradients / opacity / blend", 18, "#94A3B8FF")
s.grad(470, 330, 130, 90, "#0EA5E9,#22D3EE", "LINEAR", "TOP_LEFT", "BOTTOM_RIGHT")
s.grad(612, 330, 130, 90, "#F59E0B,#7C2D12", "RADIAL", radius=0.9, center="CENTER_LEFT")
s.grad(754, 330, 130, 90, "#8B5CF6,#22C55E", "SWEEP", start_angle=0, end_angle=6.2832)
s.box(900, 330, 130, 90, "#1D4ED8FF", radius=8, opacity=None)
s.opacity(900, 330, 130, 90, '<Positioned left="0" top="0"><Container width="130" '
          'height="45" color="#F8FAFCFF"/></Positioned><Positioned left="0" top="45">'
          '<Container width="130" height="45" color="#0F172AFF"/></Positioned>', 0.35)
s.text(470, 428, "LINEAR / RADIAL / SWEEP / Opacity 0.35 over split", 15, "#64748BFF",
       family=MONO)

# --- E. filters ---------------------------------------------------------------
s.text(900, 92, "E  filters", 18, "#94A3B8FF")
s.box(900, 120, 130, 120, "#334155FF", radius=8)
s.blur(900, 120, 130, 120, '<Positioned left="20" top="30"><Container width="90" '
       'height="60" color="#F43F5EFF" borderRadius="8"/></Positioned>', 6)
s.text(900, 248, "ImageFiltered s=6", 15, "#64748BFF", family=MONO)

# --- F. text metrics ----------------------------------------------------------
s.text(24, 640, "F  text metrics @24px: ", 18, "#94A3B8FF")
probe = "ABCDEFGHIJ 0123456789"
s.text(230, 640, probe, 24, "#F8FAFCFF", family=MONO)
s.box(230, 668, 1, 12, "#FF0000FF")
s.text(24, 690, "CJK @24px: 字形宽度测量样例", 24, "#F8FAFCFF")
s.box(24 + 24 * 4, 718, 1, 12, "#FF0000FF")

open(OUT, "w", encoding="utf-8", newline="\n").write(s.finish())
print(OUT)
