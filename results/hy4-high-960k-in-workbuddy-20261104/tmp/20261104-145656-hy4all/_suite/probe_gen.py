#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Capability probe: exercise RADIAL/SWEEP gradients, ClipPath arcs/rings,
Transform.rotate, ImageFiltered glow, Opacity, rich text, notched SVG card,
boxShadow. Rendered once to confirm the service instance supports them.
"""
import os, sys
sys.path.insert(0, os.environ["TOOLS"])
import suite
sys.path.insert(0, str(suite.SUITE_TMP))
import designkit as K

c = K.new_canvas(1200, 800, "#0E1726")

# header
K.linear(c, 0, 0, 1200, 74, ["#12305A", "#1D4E89"], begin="CENTER_LEFT", end="CENTER_RIGHT")
c.text(40, 14, 900, 48, "CAPABILITY PROBE / 高级 DSL 能力验证", 30, "#EAF3FF", bold=True)
c.text(880, 22, 280, 32, "B01·B02 shared", 18, "#8FB6EA", align="RIGHT", font=K.LATIN)

# 1 radial gradient disc
K.radial(c, 40, 110, 300, 250, ["#FFE9A8", "#F0873B", "#8A2F1C"],
         stops=[0, 0.55, 1], grad_radius=0.75, corner=18)
c.text(52, 322, 280, 30, "1 RADIAL gradient", 19, "#9FB4D0", font=K.LATIN, bold=True)

# 2 sweep gradient with hard stops
K.sweep(c, 360, 110, 250, 250, ["#34D399", "#34D399", "#1F3A4D", "#1F3A4D"],
        stops=[0, 0.62, 0.62, 1], corner=125)
c.circle(485, 235, 86, "#0E1726")
c.text(485, 218, 172, 40, "62%", 30, "#34D399", align="CENTER", bold=True, font=K.LATIN)
c.text(370, 322, 240, 30, "2 SWEEP hard stops", 19, "#9FB4D0", font=K.LATIN, bold=True)

# 3 arc gauge (annular sectors, -90 = 12 o'clock)
cx, cy = 760, 235
K.arc(c, cx, cy, 118, 86, -90, -90 + 360 * 0.78, "#FBBF24")
K.ring(c, cx, cy, 118, 86, "#22354C", opacity=0.0) if False else None
K.arc(c, cx, cy, 118, 86, -90 + 360 * 0.78, 270, "#22354C")
# center hole overlay to make it a clean track
c.circle(cx, cy, 78, "#0E1726")
c.text(cx - 80, cy - 26, 160, 52, "78%", 40, "#FFFFFF", align="CENTER", bold=True, font=K.LATIN)
c.text(650, 322, 240, 30, "3 ClipPath arc gauge", 19, "#9FB4D0", font=K.LATIN, bold=True)

# 4 ring (EVEN_ODD)
K.ring(c, 1070, 235, 96, 70, "#38BDF8")
K.ring(c, 1070, 235, 60, 56, "#A78BFA")
c.text(980, 322, 200, 30, "4 EVEN_ODD ring", 19, "#9FB4D0", font=K.LATIN, bold=True)

# 5 ImageFiltered glow behind a bright disc
K.glow(c, 180, 540, 110, 70, "#F472B6", sigma=34, opacity=0.85)
c.circle(180, 540, 46, "#FBCFE8")
c.text(70, 622, 230, 30, "5 ImageFiltered glow", 19, "#9FB4D0", font=K.LATIN, bold=True)

# 6 Transform rotation
K.rot(c, 360, 470, 240, 140, -18,
      f'<Container color="#1D4E89" borderRadius="14"><Container width="240" height="140" alignment="CENTER">'
      f'<Text fontFamily="{K.CN}" fontSize="26" color="#FFFFFF" fontStyle="BOLD" textAlign="CENTER">'
      f'{K.cdata("旋转卡片 ROTATED")}</Text></Container></Container>')
c.text(360, 622, 240, 30, "6 Transform.rotate", 19, "#9FB4D0", font=K.LATIN, bold=True)

# 7 rich text spans
c.rich(650, 470, 480, 60,
       [("状态 ", "#9FB4D0", False), ("NORMAL", "#34D399", True),
        (" · ", "#9FB4D0", False), ("12", "#FBBF24", True),
        (" 项已通过", "#EAF3FF", False)],
       size=26, align="LEFT")
c.text(650, 540, 480, 30, "7 Text 富文本 Span", 19, "#9FB4D0", font=K.LATIN, bold=True)

# 8 notched card + boxShadow
c.rect(650, 580, 480, 150, "#00000000")
K.notched_card(c, 650, 580, 480, 140, "#142A44", nr=24)
c.text(690, 600, 400, 30, "8 ClipPath SVG 票券缺口", 20, "#7DD3FC", bold=True)
c.text(690, 636, 400, 60, "ADMIT ONE · 2026", 22, "#C6DCF7", font=K.LATIN)

# 9 Opacity
c.rect(40, 690, 300, 70, "#38BDF8", radius=12, opacity=0.35)
c.text(56, 706, 280, 40, "9 Opacity 0.35", 22, "#FFFFFF", bold=True, font=K.LATIN)

# 10 boxShadow
c.rect(40, 110, 300, 250, "#00000000")
c.rect(380, 690, 220, 70, "#FFFFFF", radius=12,
       shadow="0 8 24 0 #00000099 NORMAL")
c.text(396, 706, 190, 40, "10 boxShadow", 22, "#0E1726", bold=True, font=K.LATIN)

dsl = c.render()
out = suite.SUITE_TMP / "probe"
out.mkdir(parents=True, exist_ok=True)
(out / "probe.snapshot").write_text(dsl, encoding="utf-8")
print("probe DSL bytes", len(dsl.encode("utf-8")))
