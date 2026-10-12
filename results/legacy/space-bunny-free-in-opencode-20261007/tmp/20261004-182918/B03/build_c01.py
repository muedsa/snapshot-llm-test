"""B03 case-01 · 潮汐与风 · 海岸观测站值班板.

Primary capability under test: the gradient family.
  LINEAR / RADIAL / SWEEP, gradientStops, gradientTileMode (which only
  repeats when the gradient vector is shorter than the painted box),
  gradientFocal + gradientFocalRadius, gradientStartAngle/EndAngle,
  gradientRotation, backgroundBlendMode, shape="CIRCLE", and 8-digit
  #RRGGBBAA alpha.

The tide curve is computed from six real harmonic constituents
(M2 S2 N2 K1 O1 MS4) so numbers, geometry and labels agree.

Stage 1 renders a dedicated capability probe; stage 2 renders the work.
"""
from __future__ import annotations

import math
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

import wlib as W  # noqa: E402

D = W.D
el, box = W.el, W.box

# ---------------------------------------------------------------- demo content
CONST = [("M2", 1.15, 12.4206, 32.0), ("S2", 0.42, 12.0000, 58.0),
         ("N2", 0.24, 19.3413, 12.0), ("K1", 0.28, 23.9345, 210.0),
         ("O1", 0.19, 18.7693, 195.0), ("MS4", 0.10, 6.1033, 88.0)]
MSL = 2.05
VMAX = 4.4
HOURS = 24
NOW_H = 9.75
WIND_FROM, WIND_MS, GUST = 212.0, 6.8, 11.4
SEA = {"hs": 1.6, "tp": 7.2, "dir": 218.0}
VIS_KM, TEMP_C, PRES_HPA = 14.2, 26.4, 1013.6
SUNRISE, SUNSET = "05:52", "17:38"
# Moon phase for the board's own timestamp, not a made-up number.
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
MOON_NAME = ("残月" if MOON_ILLUM <= 0.48 else "下弦月") if MOON_WANING else \
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


def tide(hours):
    v = MSL
    for _n, a, per, ph in CONST:
        v += a * math.cos(2 * math.pi * (hours - ph / 15.0) / per)
    return v


SAMPLES = [tide(i) for i in range(25)]


def extremes():
    hi = max(SAMPLES)
    lo = min(SAMPLES)
    return (hi, SAMPLES.index(hi)), (lo, SAMPLES.index(lo))


# ------------------------------------------------------------------- stage 1
def probe():
    Wc, Hc = 1240, 1060
    k = [W.t2("PROBE c01 · 本件专用渐变能力探针", 40, 20, size=19,
              color=W.INK, style="BOLD", w=700, h=26),
         W.t2("每格只测一种写法；正式作品只使用验证通过的那一种", 40, 48,
              size=12, color=W.INK3, w=800, h=18)]

    def cell(col, row, label, widget, note=""):
        cw, ch = 350, 200
        x = 40 + col * 400
        y = 92 + row * 240
        k.append(box(x, y, cw, ch, color="#FFFFFF08", radius=12,
                     border="1 SOLID #FFFFFF1C"))
        k.append(el("Positioned", {"left": x + 20, "top": y + 18,
                                   "width": cw - 40, "height": ch - 66},
                    [widget]))
        k.append(W.t2(label, x + 16, y + ch - 48, size=12, color="#E2E8F0FF",
                      w=cw - 30, h=D.est_lines(label, 12, cw - 30) * 17))
        if note:
            k.append(W.t2(note, x + 16, y + ch - 26, size=10, color=W.INK3,
                          w=cw - 30, h=14))

    cell(0, 0, "A 垂直渐变 顶实→底虚 (0.5,0)→(0.5,1)",
         el("Container", {"width": 150, "height": 120, "borderRadius": "6",
                          "gradientType": "LINEAR",
                          "gradientColors": "#F59E0BFF,#F59E0B00",
                          "gradientBegin": "(0.5,0)",
                          "gradientEnd": "(0.5,1)"}),
         "柱状填充的标准做法")
    cell(1, 0, "B 垂直渐变 + stops 0,0.65,1",
         el("Container", {"width": 150, "height": 120, "borderRadius": "6",
                          "gradientType": "LINEAR",
                          "gradientColors": "#22D3EEFF,#0EA5E9FF,#0B1020FF",
                          "gradientStops": "0,0.65,1",
                          "gradientBegin": "(0.5,0)", "gradientEnd": "(0.5,1)"}),
         "stop 位置是否真的生效")
    cell(2, 0, "C REPEAT 竖条 (向量 x 0.10→0.16)",
         el("Container", {"width": 150, "height": 120, "borderRadius": "6",
                          "gradientType": "LINEAR",
                          "gradientColors": "#0EA5E9FF,#0EA5E900",
                          "gradientBegin": "(0.10,0.5)",
                          "gradientEnd": "(0.16,0.5)",
                          "gradientTileMode": "REPEAT"}),
         "短向量才看得到重复")
    cell(0, 1, "D REPEAT 横条 (向量 y 0.20→0.26)",
         el("Container", {"width": 150, "height": 120, "borderRadius": "6",
                          "gradientType": "LINEAR",
                          "gradientColors": "#38BDF8FF,#38BDF800",
                          "gradientBegin": "(0.5,0.20)",
                          "gradientEnd": "(0.5,0.26)",
                          "gradientTileMode": "REPEAT"}),
         "横向条带 = 水面纹理")
    cell(1, 1, "E MIRROR 短向量 (与 C 对照)",
         el("Container", {"width": 150, "height": 120, "borderRadius": "6",
                          "gradientType": "LINEAR",
                          "gradientColors": "#FBBF24FF,#FBBF2400",
                          "gradientBegin": "(0.10,0.5)",
                          "gradientEnd": "(0.16,0.5)",
                          "gradientTileMode": "MIRROR"}),
         "与 C 的相位差证明 tileMode 生效")
    cell(2, 1, "F SWEEP 扇形 start=0.55 end=2.05",
         el("Container", {"width": 150, "height": 120, "shape": "CIRCLE",
                          "gradientType": "SWEEP",
                          "gradientColors": "#F59E0B00,#F59E0BFF,#F59E0B00",
                          "gradientStartAngle": "0.55",
                          "gradientEndAngle": "2.05"}),
         "扫描渐变当扇形用")
    cell(0, 2, "G RADIAL 焦点 (.38,.33) focalRadius .52",
         el("Container", {"width": 150, "height": 120, "shape": "CIRCLE",
                          "gradientType": "RADIAL",
                          "gradientColors": "#FEF9C3FF,#CBD5E1FF,#64748BFF",
                          "gradientCenter": "(0.5,0.5)",
                          "gradientRadius": "0.72",
                          "gradientFocal": "(0.38,0.33)",
                          "gradientFocalRadius": "0.52"}),
         "球面高光")
    cell(1, 2, "H 8位 hex alpha 阶梯压在 REPEAT 条纹上",
         el("Container", {"width": 268, "height": 120, "borderRadius": "6",
                          "gradientType": "LINEAR",
                          "gradientColors": "#1E293BFF,#33415500",
                          "gradientBegin": "(0.5,0.10)",
                          "gradientEnd": "(0.5,0.16)",
                          "gradientTileMode": "REPEAT"},
             [el("Stack", {"fit": "LOOSE"},
                 [box(16 + i * 32, 20, 30, 80, color="#0EA5E9" + a)
                  for i, a in enumerate(["1A", "33", "4D", "66", "80", "99",
                                         "B3", "FF"])])]),
         "半透明必须能合成在纹理上")
    cell(2, 2, "I gradientRotation=0.7853981634 (45°)",
         el("Container", {"width": 150, "height": 120, "borderRadius": "6",
                          "gradientType": "LINEAR",
                          "gradientColors": "#F472B6FF,#FDE047FF",
                          "gradientRotation": "0.7853981634"}),
         "角度制 → 弧度")
    cell(0, 3, "J CLAMP 短向量 (与 C/D 对照)",
         el("Container", {"width": 150, "height": 120, "borderRadius": "6",
                          "gradientType": "LINEAR",
                          "gradientColors": "#0EA5E9FF,#0EA5E900",
                          "gradientBegin": "(0.10,0.5)",
                          "gradientEnd": "(0.16,0.5)"}),
         "无 tileMode 时只画一段")
    cell(1, 3, "K SWEEP + borderRadius 140 (环形)",
         el("Container", {"width": 150, "height": 120, "borderRadius": "140",
                          "gradientType": "SWEEP",
                          "gradientColors": "#22D3EEFF,#A855F7FF,#F43F5EFF,"
                                            "#22D3EEFF"}),
         "扫描渐变绕圆角胶囊走一圈")
    cell(2, 3, "L backgroundBlendMode=MULTIPLY",
         el("Container", {"width": 150, "height": 120, "borderRadius": "6",
                          "color": "#EC4899FF", "gradientType": "LINEAR",
                          "gradientColors": "#FDE047FF,#22D3EEFF",
                          "gradientBegin": "(0,0)", "gradientEnd": "(1,1)",
                          "backgroundBlendMode": "MULTIPLY"}),
         "渐变与底色相乘")

    dsl = D.snapshot([D.stack(k, Wc, Hc)], Wc, Hc, bg=W.BG)
    r = W.P.probe(dsl, "c01-gradient-idioms")
    print("  probe c01-1", r.get("ok"), r.get("status"),
          (r.get("error") or "")[:160])
    for wn in D.warnings():
        print("  WARN", wn)
    D.WARNINGS.clear()
    return r


# ------------------------------------------------------------------- stage 2
CW, CH = 1600, 1000


def build():
    k = []

    # ---- header ----
    k.append(box(0, 0, CW, 92, color="#0A0F1EFF"))
    k.append(W.rule(0, 91, CW, "#1E293BFF", 1))
    k.append(W.t2("澄澳灯桩 · 海岸自动观测站", 40, 8, size=24, color=W.INK,
                  style="BOLD", w=520, h=34))
    k.append(W.t2("CANG'AO LIGHT No.07 / COASTAL WATCH BOARD", 42, 42,
                  size=11, color=W.INK3, ls=2.6, w=520, h=16, font=D.MONO))
    k.append(el("Positioned", {"left": 980, "top": 16, "width": 580,
                               "height": 34},
                [el("Text", {"color": W.INK, "fontSize": "24",
                             "fontFamily": D.MONO, "textAlign": "RIGHT",
                             "text": "2026-10-05  09:45  UTC+8"})]))
    k.append(el("Positioned", {"left": 900, "top": 54, "width": 660,
                               "height": 22},
                [el("Text", {"color": W.INK3, "fontSize": "12",
                             "fontFamily": D.MONO, "textAlign": "RIGHT",
                             "text": "第 281 天 · 自动站每 10 分钟上报 · "
                                     "数值口径见页脚"})]))
    cx = 40
    for lab, fill, fg in (("ONLINE", "#34D399FF", "#052E16FF"),
                          ("SENSOR 6/6", "#38BDF8FF", "#082F49FF"),
                          ("LAST PROBE 09:40", "#F59E0BFF", "#451A03FF")):
        w_, els = W.chip(cx, 60, lab, fill, fg=fg, size=11, h=22, ls=1.2, mono=True)
        k.extend(els)
        cx += w_ + 10

    # ---- compass panel ----
    PW, PH = 420, 560
    f = W.frame(40, 116, PW, PH)
    f.head("风向与海面", "WIND / SEA STATE", lx=28, ly=24, w=300)
    f.add(f.rt("212° 6.8 m/s", PW - 28, 22, size=19, color="#FBBF24FF",
               w=150, h=26))
    ccx, ccy = PW / 2.0, 292.0
    f.add(W.ring(ccx, ccy, 132, 1.2, "#243350FF"))
    f.add(W.ring(ccx, ccy, 84, 1, "#1B2740FF"))
    f.add(f.at(ccx - 30, ccy - 30, 60, 60,
               el("Container", {"width": 60, "height": 60, "shape": "CIRCLE",
                                "gradientType": "RADIAL",
                                "gradientColors": "#1E293BFF,#0B1220FF",
                                "gradientCenter": "(0.5,0.5)",
                                "gradientRadius": "0.7"})))
    for i in range(36):
        ang = i * 10.0
        major = (i % 9) == 0
        r1 = 132 - (22 if major else 10)
        x1, y1 = W.polar(ccx, ccy, r1, ang)
        x2, y2 = W.polar(ccx, ccy, 132, ang)
        mx, my = (x1 + x2) / 2.0, (y1 + y2) / 2.0
        seg = math.hypot(x2 - x1, y2 - y1)
        f.add(f.ab(mx - 1, my - seg / 2.0, 2, seg,
                   color=("#64748BFF" if major else "#334155FF")))
    for ang, lab, sz, col in ((0, "N", 17, W.INK), (90, "E", 14, W.INK2),
                              (180, "S", 14, W.INK2), (270, "W", 14, W.INK2),
                              (45, "NE", 10, W.INK3), (135, "SE", 10, W.INK3),
                              (225, "SW", 10, W.INK3), (315, "NW", 10, W.INK3)):
        tx_, ty_ = W.polar(ccx, ccy, 94 if sz > 12 else 100, ang)
        f.add(f.ctr(lab, tx_ - 22, ty_ - sz * 0.78, 44, size=sz, color=col,
                    h=sz * 1.6, font=D.MONO))
    FW, FH = 136, 210
    arrow = [box(FW / 2 - 6, 52, 12, 158,
                 gradient=W.vgrad("#F59E0BFF", "#F59E0B00")),
             D.polygon([(FW / 2, 10), (FW / 2 + 22, 54), (FW / 2 - 22, 54)],
                       "#FCD34DFF"),
             box(FW / 2 - 34, 52, 20, 3, color="#FCD34D66"),
             box(FW / 2 + 14, 52, 20, 3, color="#FCD34D66")]
    f.add(f.at(ccx - FW / 2, ccy - FH / 2, FW, FH,
               el("Transform",
                  {"matrix": W.P.col_major(W.P.mat_rot(WIND_FROM)),
                   "alignment": "CENTER"},
                  [el("Container", {"width": FW, "height": FH},
                     [el("Stack", {"fit": "LOOSE"}, arrow)])])))
    f.add(f.at(ccx - 14, ccy - 14, 28, 28,
               el("Container", {"width": 28, "height": 28, "shape": "CIRCLE",
                                "color": "#0B1220FF",
                                "border": "2 SOLID #F59E0BAA"})))
    f.add(f.ctr("箭头指向来向 212°", ccx - 170, ccy + 140, 340,
                size=11, color=W.INK3, font=D.MONO))
    READ = [("风速", "%.1f m/s" % WIND_MS, W.INK),
            ("阵风", "%.1f m/s" % GUST, W.INK),
            ("有义波高 Hs", "%.1f m" % SEA["hs"], W.INK),
            ("谱峰周期 Tp", "%.1f s" % SEA["tp"], W.INK),
            ("蒲福风级", "4 级", W.INK2),
            ("浪向", "%.0f°" % SEA["dir"], W.INK2)]
    for i, (lab, val, col) in enumerate(READ):
        colx = 28 + (i % 2) * 194
        ry = 462 + (i // 2) * 32
        f.add(f.tx(lab, colx, ry, size=11, color=W.INK3, w=94, h=17))
        f.add(f.rt(val, colx + 166, ry - 1, size=14, color=col, w=72, h=20,
                   font=D.MONO))
    k.append(f.render())

    # ---- tide panel ----
    TX, TY, TW, TH = 500, 116, 660, 560
    g = W.frame(TX, TY, TW, TH)
    g.head("潮位曲线 · 24 小时", "TIDE / 24H", lx=28, ly=22, w=340)
    g.add(g.rt("%.2f m" % tide(NOW_H), TW - 28, 18, size=36,
               color="#5EEAD4FF", w=220, h=46))
    g.add(g.rt("当前实测 · 站点理论最低面", TW - 28, 60, size=12,
               color=W.INK3, w=220, h=18))
    PXp, PYp, PWp, PHp = 76, 176, 552, 232
    for v in range(5):
        gy = PYp + PHp - (v / VMAX) * PHp
        g.add(g.ab(PXp, gy, PWp, 1, color="#16203A55"))
        g.add(g.rt("%.1f" % v, PXp - 10, gy - 9, size=11, color=W.INK3,
                   w=40, h=18))
    step = PWp / HOURS
    for i in range(13):
        gx = PXp + i * 2 * step
        g.add(g.ab(gx, PYp, 1, PHp, color="#16203A40"))
        g.add(g.ctr("24" if i == 12 else "%02d" % (i * 2), gx - 22,
                    PYp + PHp + 8, 44, size=11, color=W.INK3, font=D.MONO))
    g.add(g.tx("时", PXp - 48, PYp + PHp + 8, size=11, color=W.INK3, w=20,
               h=16))
    for i, v in enumerate(SAMPLES):
        hgt = (v / VMAX) * PHp
        g.add(g.ab(PXp + i * step - 6.5, PYp + PHp - hgt, 13, hgt,
                   gradient=W.vgrad("#2DD4BF00", "#2DD4BFFF")))
    for i in range(HOURS):
        for j in range(6):
            th = i + j / 6.0
            g.add(g.ab(PXp + th * step - 1.5,
                       PYp + PHp - (tide(th) / VMAX) * PHp - 1.5, 3, 3,
                       color="#99F6E4FF"))
    (hi, hi_h), (lo, lo_h) = extremes()
    for val, hh, nm, col in ((hi, hi_h, "高潮", "#FCD34DFF"),
                             (lo, lo_h, "低潮", "#7DD3FCFF")):
        mx = PXp + hh * step
        my = PYp + PHp - (val / VMAX) * PHp
        g.add(g.at(mx - 5, my - 5, 10, 10,
                   el("Container", {"width": 10, "height": 10,
                                    "shape": "CIRCLE", "color": col})))
        lab = "%s %.2fm %02d:00" % (nm, val, hh)
        if nm == "低潮":
            # the low tide sits on the axis with no free space beside it, so
            # the label floats above-right of the dot with a dotted leader
            g.add(g.tx(lab, mx + 38, my - 66, size=12, color=col, w=140,
                       h=18, font=D.MONO))
        elif mx > PXp + PWp - 150:
            g.add(g.rt(lab, mx - 12, my - 10, size=12, color=col, w=134, h=18,
                       font=D.MONO))
        else:
            g.add(g.tx(lab, mx + 12, my - 10, size=12, color=col, w=134, h=18,
                       font=D.MONO))
    nx = PXp + NOW_H * step
    g.add(g.ab(nx, PYp - 14, 1.5, PHp + 14, color="#F472B6FF"))
    g.add(g.ctr("NOW 09:45", nx - 46, PYp - 34, 92, size=11, color="#F472B6FF",
                font=D.MONO))
    ny = PYp + PHp + 38
    g.add(g.r(28, ny, TW - 56, "#1E293BFF", 1))
    rows = (("理论高低潮", "高潮 %.2f m @%02d:00 · 低潮 %.2f m @%02d:00"
              % (hi, hi_h, lo, lo_h)),
            ("大潮差", "%.2f m" % (hi - lo)),
            ("调和数", " · ".join("%s %.2f" % (n, a) for n, a, _p, _q in CONST)),
            ("平均海平面", "%.2f m（理论最低面以上）" % MSL))
    for lab, val in rows:
        g.add(g.tx(lab, 28, ny + 12, size=11, color=W.INK3, w=110, h=16))
        g.add(g.rt(val, TW - 28, ny + 11, size=11, color=W.INK2,
                   w=TW - 150, h=18, font=D.MONO))
        ny += 22
    k.append(g.render())

    # ---- sky panel ----
    SX, SY, SW, SH = 1180, 116, 380, 560
    s = W.frame(SX, SY, SW, SH)
    s.head("月相与光照", "MOON / SUN", lx=28, ly=24, w=260)
    mcx, mcy = SW / 2.0, 168.0
    moon = [el("Container", {"width": 176, "height": 176, "shape": "CIRCLE",
                             "color": "#0A0F1CFF"})]
    for row in range(176):
        bar = _moon_bar(row)
        if bar is not None:
            moon.append(bar)
    for mx_, my_, md_ in ((34, 54, 22), (60, 104, 27), (28, 118, 15)):
        moon.append(_mare(mx_, my_, md_))
    s.add(s.at(mcx - 88, mcy - 88, 176, 176,
               el("ClipOval", {"clipBehavior": "ANTI_ALIAS"},
                  [el("Stack", {"fit": "LOOSE"}, moon)])))
    s.add(s.ctr("%s · 照亮 %.0f%%" % (MOON_NAME, MOON_ILLUM * 100), mcx - 100,
                mcy + 98, 200, size=13, color=W.INK2, font=D.MONO))
    s.add(s.ctr("月龄 %.1f d · 由 D=%.1f° 算得" % (MOON_AGE, _MOON_DEG),
                mcx - 110, mcy + 114, 220, size=9, color=W.INK4,
                font=D.MONO))
    s.add(s.r(28, mcy + 134, SW - 56, "#1E293BFF", 1))
    sy2 = mcy + 148
    for lab, val, col in (("日出", SUNRISE, W.INK), ("日落", SUNSET, W.INK),
                          ("白昼时长", "11h46m", W.INK2),
                          ("能见度", "%.1f km" % VIS_KM, W.INK),
                          ("气温", "%.1f ℃" % TEMP_C, W.INK),
                          ("气压", "%.1f hPa" % PRES_HPA, W.INK2)):
        s.kv(lab, val, sy2, vcolor=col, lw=120, vright=SW - 28, vsize=15)
        s.add(s.r(28, sy2 + 22, SW - 56, "#16203AFF", 1))
        sy2 += 36
    k.append(s.render())

    # ---- sea profile + alpha ladder ----
    BX, BY, BW, BH = 40, 700, 1520, 280
    b = W.frame(BX, BY, BW, BH)
    b.head("海面剖面与水深分级", "SEA PROFILE / DEPTH CLASSES", lx=28, ly=22,
           w=460)
    base_y, x0, span, n = 158.0, 32.0, 840.0, 72
    stepw = span / n
    for i in range(n):
        tt = i / float(n)
        amp = SEA["hs"] * (0.62 * math.sin(2 * math.pi * tt * 3.1)
                           + 0.26 * math.sin(2 * math.pi * tt * 7.3 + 1.1)
                           + 0.14 * math.sin(2 * math.pi * tt * 13.7 + 2.4))
        bh = max(8.0, abs(amp) * 62.0)
        b.add(b.ab(x0 + i * stepw, base_y - bh, stepw - 3, bh,
                   gradient=W.vgrad("#38BDF800", "#38BDF8FF")))
    b.add(b.r(x0, base_y, span, "#334155FF", 1))
    b.add(W.hatch(x0, base_y + 1, span, 52, "#0EA5E9FF", period_px=8.0,
                  axis="y"))
    b.add(b.tx("STILL WATER LEVEL · 静水面", x0, base_y + 60, size=10,
               color=W.INK3, w=240, h=14, ls=1.4, font=D.MONO))
    b.add(b.tx("η(x) = Hs·Σ aᵢ sin(2πkᵢx/λ), n = 72", x0 + 470,
               base_y + 60, size=10, color=W.INK3, w=330, h=14, font=D.MONO))
    lx0 = 992
    b.add(W.hatch(lx0 - 16, 66, 512, 126, "#1E293BFF", period_px=9.0,
                  axis="y", alpha_end="00"))
    for i, a in enumerate(["1A", "33", "4D", "66", "80", "99", "B3", "FF"]):
        b.add(b.ab(lx0 + i * 62, 86, 54, 54, color="#0EA5E9" + a, radius=4,
                   border="1 SOLID #0F172AFF"))
        b.add(b.ctr("#0EA5E9" + a, lx0 + i * 62 - 4, 144, 62, size=9,
                    color=W.INK3, font=D.MONO))
    DEPTH = ["0.0–0.3", "0.3–0.6", "0.6–0.9", "0.9–1.2", "1.2–1.8",
             "1.8–2.4", "2.4–3.0", "> 3.0 m"]
    for i, dl in enumerate(DEPTH):
        b.add(b.ctr(dl, lx0 + i * 62 - 8, 162, 70, size=9, color=W.INK2,
                    font=D.MONO))
    b.add(b.tx("水深分级（m）· 8 位 #RRGGBBAA 八级 alpha 压在同一层 REPEAT "
               "纹理上，验证半透明确实参与合成", lx0 - 16, 196, size=11,
               color=W.INK3, w=512, h=16))
    b.add(b.tx("站位、风、海况为演示用虚构值；月相按本页时间戳真实算出；"
               "潮位由六个分潮调和数按 "
               "h(t)=MSL+ΣA·cos(2π(t−g)/T) 合成，几何与标注同源。",
               32, 250, size=10, color=W.INK4, w=1200, h=14))
    k.append(b.render())

    dsl = D.snapshot([D.stack(k, CW, CH)], CW, CH, bg=W.BG)
    r = W.P.render_final(dsl, "case-01", "final")
    print("  case-01", r.get("ok"), r.get("status"), (r.get("error") or "")[:200])
    for wn in D.warnings():
        print("  WARN", wn)
    D.WARNINGS.clear()
    return r


if __name__ == "__main__":
    print("== case-01 stage 1: capability probe")
    probe()
    print("== case-01 stage 2: work")
    build()