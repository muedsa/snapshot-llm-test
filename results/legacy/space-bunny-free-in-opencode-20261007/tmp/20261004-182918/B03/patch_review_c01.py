"""B03 review fix 1 - case-01 moon phase.

Problem found by opening case-01/final.png during the wrap-up review:
the label under the moon said "亏凸月 · 照亮 72%" while the drawn disc was a
thin crescent on the RIGHT limb (~20% lit).  Both the percentage and the name
came from a hard-coded constant (MOON_ILLUM = 0.72) and matched neither the
picture nor the board's own timestamp.

Fix, no guessing:
  * derive illuminated fraction and waxing/waning from the printed board
    timestamp (2026-10-05 09:45 +08:00 == 01:45 UTC) from the mean elongation D
    (Meeus ch.47 low-precision series), k = (1 - cos D) / 2;
  * print the phase name and k that computation produced;
  * draw a terminator that really encloses k of the disc: inside a ClipOval,
    one 1-px bar per row, running from the limb to
    x(y) = 88 -/+ (1-2k)*88*sqrt(1-(y/88)^2).  Lit limb on the left because the
    moon is waning;
  * say in the footer note that the moon is computed, not invented.
"""
import io

p = "build_c01.py"
s = io.open(p, encoding="utf-8").read()
n = 0


def rep(old, new):
    global s, n
    assert old in s, old[:80]
    s = s.replace(old, new, 1)
    n += 1


rep("MOON_ILLUM = 0.72\n",
    '''# Moon phase for the board's own timestamp, not a made-up number.
# D = mean elongation of the Moon from the Sun (Meeus, Astronomical Algorithms
# ch. 47 low-precision series); D = 0 at new moon, 180 at full moon.
# Illuminated fraction k = (1 - cos D) / 2.
BOARD_JD = 2461318.57292          # 2026-10-05 09:45 +08:00 == 01:45 UTC
_T = (BOARD_JD - 2451545.0) / 36525.0
_MOON_DEG = (297.8501921 + 445267.1114034 * _T - 0.0018819 * _T ** 2) % 360.0
MOON_ILLUM = (1.0 - math.cos(math.radians(_MOON_DEG))) / 2.0
MOON_WANING = _MOON_DEG > 180.0
MOON_AGE = _MOON_DEG / 360.0 * 29.530588
MOON_PSI = abs(180.0 - _MOON_DEG)          # 105.0 deg
_MOON_SGN = -1.0 if MOON_WANING else 1.0  # which limb carries the sun
MOON_NAME = ("残月" if MOON_ILLUM <= 0.48 else "下弦月") if MOON_WANING else \\
            ("蛾眉月" if MOON_ILLUM <= 0.48 else "上弦月")
MR = 88.0


def _moon_lum(nx, ny):
    """Shading of the lit surface at disc coords nx, ny, both in [-1, 1]."""
    nz2 = 1.0 - nx * nx - ny * ny
    nz = math.sqrt(nz2) if nz2 > 0.0 else 0.0
    psi = math.radians(MOON_PSI)
    b = _MOON_SGN * nx * math.sin(psi) + nz * math.cos(psi)
    return max(0.0, min(1.0, b))


def _rgb(c):
    v = 0.10 + 0.90 * (c ** 0.55)
    return "#%02X%02X%02XFF" % (int(58 + 183 * v), int(66 + 179 * v),
                                int(84 + 165 * v))


def _moon_bar(row, mr=MR):
    """One 1-px row of the lit region; None where the terminator has closed.

    The terminator of a sphere projects to a half-ellipse whose semi-axis along
    the sun direction is R(1-2k), so filling one bar per row inside a ClipOval
    encloses exactly k of the disc.
    """
    yy = row - mr + 0.5
    u = 1.0 - (yy / mr) ** 2
    if u <= 0.0:
        return None
    xt = mr - _MOON_SGN * (1.0 - 2.0 * MOON_ILLUM) * mr * math.sqrt(u)
    if MOON_WANING:
        x0, x1 = 0.0, xt
    else:
        x0, x1 = xt, 2.0 * mr
    if x1 - x0 < 0.6:
        return None
    wbar = round(x1 - x0, 2)
    ca = _rgb(_moon_lum((x0 - mr) / mr, yy / mr))
    cb = _rgb(_moon_lum((x1 - mr) / mr, yy / mr))
    kid = el("Container", {"width": wbar, "height": 1,
                           "gradientType": "LINEAR",
                           "gradientColors": ca + "," + cb,
                           "gradientBegin": "(0,0.5)",
                           "gradientEnd": "(1,0.5)"})
    return el("Positioned", {"left": round(x0, 2), "top": row,
                             "width": wbar, "height": 1}, [kid])


def _mare(cx, cy, r):
    kid = el("Container", {"width": 2 * r, "height": 2 * r,
                           "shape": "CIRCLE", "color": "#5B647A66"})
    return el("Positioned", {"left": cx - r, "top": cy - r,
                             "width": 2 * r, "height": 2 * r}, [kid])
''')

OLD_MOON = '''    moon = [el("Container", {"width": 176, "height": 176, "shape": "CIRCLE",
                             "gradientType": "RADIAL",
                             "gradientColors": "#FEF9C3FF,#E2E8F0FF,#94A3B8FF",
                             "gradientCenter": "(0.5,0.5)",
                             "gradientRadius": "0.75",
                             "gradientFocal": "(0.38,0.33)",
                             "gradientFocalRadius": "0.52"}),
            el("Positioned", {"left": 26, "top": 40, "width": 34, "height": 30},
               [el("Container", {"width": 34, "height": 30, "shape": "CIRCLE",
                                 "color": "#94A3B866"})]),
            el("Positioned", {"left": 104, "top": 96, "width": 44,
                              "height": 38},
               [el("Container", {"width": 44, "height": 38, "shape": "CIRCLE",
                                 "color": "#94A3B866"})]),
            el("Positioned", {"left": 96, "top": 42, "width": 26, "height": 26},
               [el("Container", {"width": 26, "height": 26, "shape": "CIRCLE",
                                 "color": "#94A3B866"})]),
            el("Positioned", {"left": -54, "top": -14, "width": 208,
                              "height": 208},
               [el("Container", {"width": 208, "height": 208,
                                 "shape": "CIRCLE", "color": "#070B16FF"})])]'''

NEW_MOON = '''    moon = [el("Container", {"width": 176, "height": 176, "shape": "CIRCLE",
                             "color": "#0A0F1CFF"})]
    for row in range(176):
        bar = _moon_bar(row)
        if bar is not None:
            moon.append(bar)
    for mx_, my_, md_ in ((34, 54, 22), (60, 104, 27), (28, 118, 15)):
        moon.append(_mare(mx_, my_, md_))'''

rep(OLD_MOON, NEW_MOON)

rep('''    s.add(s.ctr("亏凸月 · 照亮 %.0f%%" % (MOON_ILLUM * 100), mcx - 100,
                mcy + 100, 200, size=13, color=W.INK2, font=D.MONO))''',
    '''    s.add(s.ctr("%s · 照亮 %.0f%%" % (MOON_NAME, MOON_ILLUM * 100), mcx - 100,
                mcy + 98, 200, size=13, color=W.INK2, font=D.MONO))
    s.add(s.ctr("月龄 %.1f d · 由 D=%.1f° 算得" % (MOON_AGE, _MOON_DEG),
                mcx - 110, mcy + 114, 220, size=9, color=W.INK4,
                font=D.MONO))''')

rep('''    b.add(b.tx("站位、风、海况、月相为演示用虚构值；潮位由六个分潮调和数按 "''',
    '''    b.add(b.tx("站位、风、海况为演示用虚构值；月相按本页时间戳真实算出；"
               "潮位由六个分潮调和数按 "''')

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("patched", n, "blocks")