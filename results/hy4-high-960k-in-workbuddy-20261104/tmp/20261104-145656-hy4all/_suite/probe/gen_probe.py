#!/usr/bin/env python3
"""One-shot capability smoke probe for B05/B06. Not a delivered work."""
import os, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, os.environ["TOOLS"])
sys.path.insert(0, str(HERE))
from dsl import Canvas, LATIN, CN, MONO
import dslx as X

W, H = 1400, 900
c = Canvas(W, H, "#0A0E1A")
WHITE = "#F8FAFC"; MUTED = "#93A4BF"; LINE = "#23304A"

c.text(30, 16, 1340, 46, "DSL 能力冒烟探针  /  CAPABILITY SMOKE PROBE", 30, WHITE,
       bold=True, spacing=1.5)
c.text(30, 60, 1340, 26, "RADIAL · SWEEP · LINEAR+STOPS · Transform · ImageFiltered · ClipPath(C/A) · 富文本 · boxShadow · Opacity · letterSpacing · donut/arc",
       15, MUTED, font=MONO)

# ---- Row 1 : gradients -------------------------------------------------
# RADIAL
X.gradient(c, 30, 100, 430, 240, ["#FDE68A", "#F97316", "#7C2D12"],
           gtype="RADIAL", center="CENTER", grad_radius=0.62, radius=18)
c.circle(245, 220, 62, "#FFFFFF", opacity=0.16)
c.text(50, 112, 390, 30, "01  RADIAL 渐变", 20, "#3B1A05", bold=True)
c.text(50, 300, 390, 26, "gradientType=RADIAL · center/radius", 15, "#4A2307", font=MONO)

# SWEEP
X.gradient(c, 480, 100, 430, 240,
           ["#22D3EE", "#6366F1", "#EC4899", "#F59E0B", "#22D3EE"],
           gtype="SWEEP", center="CENTER", start_angle=0, end_angle=6.283185, radius=18)
c.circle(695, 220, 84, "#0A0E1A")
c.circle(695, 220, 84, "#FFFFFF", opacity=0.10)
c.text(500, 112, 390, 30, "02  SWEEP 扫描渐变", 20, WHITE, bold=True)
c.text(500, 300, 390, 26, "gradientStartAngle / EndAngle", 15, "#DCE7FA", font=MONO)

# LINEAR + stops
X.gradient(c, 930, 100, 430, 240, ["#0EA5E9", "#6366F1", "#EC4899"],
           gtype="LINEAR", stops=[0, 0.35, 1], begin="TOP_LEFT", end="BOTTOM_RIGHT", radius=18)
c.text(950, 112, 390, 30, "03  LINEAR 渐变 + stops", 20, WHITE, bold=True)
c.text(950, 300, 390, 26, "gradientStops=0,0.35,1", 15, "#EAF2FF", font=MONO)

# ---- Row 2 -------------------------------------------------------------
# Transform rotated card
X.transform(c, 30, 370, 430, 240, X.rot_matrix(-11, 0.92, 0.92),
            '<Container width="430" height="240" color="#1E293B" borderRadius="16" '
            'border="1 SOLID #38BDF8" alignment="CENTER">'
            '<Text color="#E0F2FE" fontSize="26" fontStyle="BOLD" fontFamily="Noto Sans CJK SC">'
            '<![CDATA[Transform.matrix 旋转 −11°]]></Text></Container>')
c.text(46, 382, 400, 30, "04  Transform.matrix", 20, MUTED, bold=True)
c.text(46, 586, 400, 24, "alignment=CENTER · 列主序 16 浮点", 15, MUTED, font=MONO)

# ImageFiltered blurred background + sharp text
bg = ('<Container width="430" height="240" color="#10233F" />'
      '<Positioned left="-40" top="40" width="520" height="26"><Container color="#22D3EE" /></Positioned>'
      '<Positioned left="-40" top="96" width="520" height="26"><Container color="#A78BFA" /></Positioned>'
      '<Positioned left="-40" top="152" width="520" height="26"><Container color="#F59E0B" /></Positioned>'
      '<Positioned left="-40" top="208" width="520" height="26"><Container color="#34D399" /></Positioned>')
X.blur_card(c, 480, 370, 430, 240, bg, sigma=7, radius=20,
            border="1 SOLID #FFFFFF44")
c.text(500, 386, 390, 30, "05  ImageFiltered 背景模糊", 20, WHITE, bold=True)
c.text(500, 430, 390, 26, "ClipRRect + 模糊副本，文字在外", 16, "#D7E9FF")
c.text(500, 566, 390, 24, "文字保持锐利可读", 16, "#7DD3FC", font=MONO)

# ClipPath cubic bezier wave
X.clip(c, 930, 370, 430, 240,
       "M0 90 C 60 20 120 20 215 90 C 300 160 360 160 430 90 L430 240 L0 240 Z",
       "#0EA5E9", opacity=0.85)
X.clip(c, 930, 370, 430, 240,
       "M0 140 C 70 80 140 80 215 140 C 300 200 370 200 430 140 L430 240 L0 240 Z",
       "#6366F1", opacity=0.8)
c.text(950, 382, 390, 30, "06  ClipPath 三次贝塞尔", 20, WHITE, bold=True)
c.text(950, 586, 390, 24, "C 曲线 · 多层波浪填充", 15, "#DCE7FA", font=MONO)

# ---- Row 3 -------------------------------------------------------------
# Rich text (nested Text spans)
c.rect(30, 650, 430, 220, "#111C30", radius=18, border="1 SOLID " + LINE)
c.rich(50, 668, 390, 60,
       [("今天 ", None, None), ("降水概率", "#38BDF8", True), (" 高达 ", None, None),
        ("92%", "#FB7185", True)], 26, WHITE)
c.rich(50, 740, 390, 50,
       [("建议 ", None, None), ("推迟出门", "#FBBF24", True), ("，改走 ", None, None),
        ("梧桐里", "#34D399", True)], 20, "#C9D8F0")
c.text(50, 820, 390, 30, "07  Text 嵌套富文本（多色/粗体）", 17, MUTED, font=MONO)

# boxShadow + Opacity
c.rect(480, 650, 430, 220, "#16243C", radius=18)
c.rect(505, 676, 180, 150, "#3B82F6", radius=14,
       shadow="0 10 24 0 #00000088 NORMAL")
c.circle(795, 750, 62, "#F472B6", opacity=0.45)
c.circle(840, 750, 62, "#22D3EE", opacity=0.45)
c.text(500, 662, 390, 30, "08  boxShadow + Opacity", 20, WHITE, bold=True)
c.text(500, 838, 390, 26, "自定义阴影 / 半透明叠圆", 15, MUTED, font=MONO)

# donut + arc ring
X.donut(c, 1145, 760, 92, 66, "#1E3A5F")
X.arc(c, 1145, 760, 92, 66, -90, -90 + 360 * 0.68, "#22D3EE")
X.arc(c, 1145, 760, 92, 66, -90 + 360 * 0.68, -90 + 360 * 0.86, "#F59E0B")
X.ring_ticks(c, 1145, 760, 100, 94, [i * 30 - 90 for i in range(12)], "#4B6085", 2)
c.text(1105, 736, 80, 44, "68%", 30, WHITE, bold=True, align="CENTER", font=LATIN)
c.text(950, 662, 390, 30, "09  donut / arc 环形", 20, WHITE, bold=True)
c.text(950, 838, 390, 26, "EVEN_ODD 镂空 + A 弧扇段", 15, MUTED, font=MONO)

c.text(30, 878, 1340, 20, "PROBE · 用于验证服务实际支持能力，不计入任何交付作品", 13, "#5C6E8C", font=MONO)

dsl = c.render()
(HERE / "capabilities.snapshot").write_text(dsl, encoding="utf-8")
print("probe bytes", len(dsl.encode("utf-8")))
